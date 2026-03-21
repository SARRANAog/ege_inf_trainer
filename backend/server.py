import ast
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

try:
    from .storage import LocalSQLiteStorage
except ImportError:
    from storage import LocalSQLiteStorage

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_BUILD_DIR = PROJECT_ROOT / "frontend" / "build"

load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="EGE Informatics Trainer API")

cors_origins_raw = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = LocalSQLiteStorage(BASE_DIR)
SERVE_FRONTEND_BUILD = os.environ.get("SERVE_FRONTEND_BUILD", "1").strip().lower() not in {"0", "false", "no"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============== MODELS ==============

class ProfileCreate(BaseModel):
    name: str = "Ученик"
    target_score: int = 80
    exam_date: str = "2026-06-01"
    confidence_level: str = "medium"
    daily_hours: float = 2.0
    weekly_hours: float = 10.0
    font_size: int = 14


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    target_score: Optional[int] = None
    exam_date: Optional[str] = None
    confidence_level: Optional[str] = None
    daily_hours: Optional[float] = None
    weekly_hours: Optional[float] = None
    font_size: Optional[int] = None


class AnswerCheck(BaseModel):
    exercise_id: str
    answer: Any


class CodeRun(BaseModel):
    code: str
    stdin: str = ""


class CodeCheck(BaseModel):
    exercise_id: str
    code: str


class MockExamAnswer(BaseModel):
    task_number: int
    answer: Any
    code: Optional[str] = None


class DraftUpsert(BaseModel):
    draft_type: str = "generic"
    task_number: Optional[int] = None
    exercise_id: Optional[str] = None
    payload: Any = None


# ============== HELPERS ==============

def load_static_content() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        from .content_data import THEORY_DATA, EXERCISES_DATA, ROADMAP_DATA
    except ImportError:
        from content_data import THEORY_DATA, EXERCISES_DATA, ROADMAP_DATA
    return THEORY_DATA, EXERCISES_DATA, ROADMAP_DATA


async def ensure_storage_seeded(force: bool = False) -> dict[str, Any]:
    theory_data, exercises_data, roadmap_data = load_static_content()
    return storage.seed_static_content(theory_data, exercises_data, roadmap_data, force=force)


async def get_profile_doc() -> Optional[dict[str, Any]]:
    return storage.get_profile()


async def save_profile_doc(profile: dict[str, Any]) -> None:
    storage.save_profile(profile)


async def bump_profile_counters() -> None:
    profile = await get_profile_doc()
    if not profile:
        return
    profile["total_exercises_done"] = storage.count_attempts()
    profile["total_correct"] = storage.count_attempts(correct=True)
    profile["updated_at"] = now_iso()
    await save_profile_doc(profile)


async def update_progress_after_attempt(task_number: int, correct: bool) -> None:
    prog = storage.get_progress(task_number)
    current_time = now_iso()

    if prog:
        prog["total_attempts"] = prog.get("total_attempts", 0) + 1
        prog["correct_attempts"] = prog.get("correct_attempts", 0) + (1 if correct else 0)
    else:
        prog = {
            "task_number": task_number,
            "total_attempts": 1,
            "correct_attempts": 1 if correct else 0,
            "status": "started",
        }

    total_attempts = prog.get("total_attempts", 0)
    correct_attempts = prog.get("correct_attempts", 0)
    accuracy = round((correct_attempts / total_attempts) * 100, 2) if total_attempts else 0.0

    prog["accuracy"] = accuracy
    prog["last_activity"] = current_time

    if total_attempts >= 10 and accuracy >= 80:
        prog["status"] = "mastered"
    elif total_attempts >= 3:
        prog["status"] = "in_progress"
    else:
        prog["status"] = "started"

    storage.save_progress(prog)
    await bump_profile_counters()


def safe_literal_eval(raw: str) -> Any:
    try:
        return ast.literal_eval(raw)
    except Exception:
        return raw


def build_code_task_result(exercise: dict[str, Any], passed: bool, details: str = "") -> dict[str, Any]:
    return {
        "correct": passed,
        "type": "code",
        "message": "Код прошёл проверку" if passed else "Код не прошёл проверку",
        "details": details,
        "expected": exercise.get("solution"),
        "explanation": exercise.get("explanation", ""),
    }


def run_python_code(source_code: str, stdin_text: str = "") -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "solution.py"
        script_path.write_text(source_code, encoding="utf-8")

        try:
            completed = subprocess.run(
                [sys.executable, str(script_path)],
                input=stdin_text,
                text=True,
                capture_output=True,
                timeout=5,
                encoding="utf-8",
                errors="replace",
            )
            return {
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "returncode": completed.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Превышено время выполнения (timeout 5 сек).",
                "returncode": -1,
            }


def get_theory_or_404(task_number: int) -> dict[str, Any]:
    item = storage.get_theory(task_number)
    if not item:
        raise HTTPException(404, "Теория не найдена")
    return item


def get_exercise_or_404(exercise_id: str) -> dict[str, Any]:
    exercise = storage.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(404, "Упражнение не найдено")
    return exercise


# ============== THEORY ==============

@app.get("/api/theory")
async def list_theory():
    return storage.list_theory()


@app.get("/api/theory/{task_number}")
async def get_theory(task_number: int):
    return get_theory_or_404(task_number)


# ============== EXERCISES / PRACTICE ==============

@app.get("/api/exercises")
async def list_exercises(task: Optional[int] = None):
    return storage.list_exercises(task)


@app.get("/api/exercises/{exercise_id}")
async def get_exercise(exercise_id: str):
    return get_exercise_or_404(exercise_id)


@app.post("/api/check-answer")
async def check_answer(payload: AnswerCheck):
    exercise = get_exercise_or_404(payload.exercise_id)
    expected_answer = exercise.get("correct_answer")
    task_number = exercise.get("task_number", 0)

    submitted = payload.answer
    correct = False

    if isinstance(expected_answer, list):
        correct = submitted in expected_answer
    else:
        correct = submitted == expected_answer

    attempt = {
        "exercise_id": payload.exercise_id,
        "task_number": task_number,
        "submitted_answer": submitted,
        "correct_answer": expected_answer,
        "correct": correct,
        "attempt_type": "answer",
        "created_at": now_iso(),
    }
    storage.add_history(attempt)
    await update_progress_after_attempt(task_number, correct)

    return {
        "correct": correct,
        "expected": expected_answer,
        "explanation": exercise.get("explanation", ""),
    }


@app.post("/api/run-code")
async def run_code(payload: CodeRun):
    return run_python_code(payload.code, payload.stdin)


@app.post("/api/check-code")
async def check_code(payload: CodeCheck):
    exercise = get_exercise_or_404(payload.exercise_id)
    task_number = exercise.get("task_number", 0)
    tests = exercise.get("tests", [])

    if not tests:
        result = build_code_task_result(exercise, False, "Для задачи не заданы тесты.")
        storage.add_history(
            {
                "exercise_id": payload.exercise_id,
                "task_number": task_number,
                "submitted_code": payload.code,
                "correct": False,
                "attempt_type": "code",
                "created_at": now_iso(),
            }
        )
        await update_progress_after_attempt(task_number, False)
        return result

    failure_details = []
    all_passed = True

    for index, test in enumerate(tests, start=1):
        run_result = run_python_code(payload.code, test.get("input", ""))
        actual_output = (run_result.get("stdout") or "").strip()
        expected_output = (test.get("output") or "").strip()

        if run_result.get("returncode") != 0:
            all_passed = False
            failure_details.append(
                f"Тест {index}: ошибка выполнения.\n{run_result.get('stderr', '').strip()}"
            )
            continue

        if actual_output != expected_output:
            all_passed = False
            failure_details.append(
                f"Тест {index}: ожидалось `{expected_output}`, получено `{actual_output}`"
            )

    storage.add_history(
        {
            "exercise_id": payload.exercise_id,
            "task_number": task_number,
            "submitted_code": payload.code,
            "correct": all_passed,
            "attempt_type": "code",
            "created_at": now_iso(),
        }
    )
    await update_progress_after_attempt(task_number, all_passed)

    return build_code_task_result(exercise, all_passed, "\n".join(failure_details))


# ============== PROFILE ==============

@app.get("/api/profile")
async def get_profile():
    profile = await get_profile_doc()
    if profile:
        return profile

    default_profile = {
        "name": "Ученик",
        "target_score": 80,
        "exam_date": "2026-06-01",
        "confidence_level": "medium",
        "daily_hours": 2.0,
        "weekly_hours": 10.0,
        "font_size": 14,
        "total_exercises_done": 0,
        "total_correct": 0,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    await save_profile_doc(default_profile)
    return default_profile


@app.post("/api/profile")
async def create_profile(payload: ProfileCreate):
    profile = {
        "name": payload.name,
        "target_score": payload.target_score,
        "exam_date": payload.exam_date,
        "confidence_level": payload.confidence_level,
        "daily_hours": payload.daily_hours,
        "weekly_hours": payload.weekly_hours,
        "font_size": payload.font_size,
        "total_exercises_done": 0,
        "total_correct": 0,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    await save_profile_doc(profile)
    return profile


@app.put("/api/profile")
async def update_profile(payload: ProfileUpdate):
    existing = await get_profile_doc()
    if not existing:
        raise HTTPException(404, "Профиль не найден")

    update_data = payload.model_dump(exclude_unset=True)
    existing.update(update_data)
    existing["updated_at"] = now_iso()

    await save_profile_doc(existing)
    return existing


# ============== PROGRESS ==============

@app.get("/api/progress")
async def get_progress():
    return storage.list_progress()


@app.get("/api/history")
async def get_history(limit: int = 50):
    return storage.list_history(limit=limit)


# ============== ROADMAP ==============

@app.get("/api/roadmap")
async def get_roadmap():
    return storage.list_roadmap()


# ============== WEEKLY REVIEW ==============

@app.get("/api/weekly-review")
async def get_weekly_review():
    review = storage.get_weekly_review()
    if review:
        return review

    progress_items = storage.list_progress()
    weak_tasks = [
        item for item in progress_items
        if item.get("accuracy", 0) < 70 or item.get("status") != "mastered"
    ]

    suggested_focus = [item["task_number"] for item in weak_tasks[:5]]

    review = {
        "generated_at": now_iso(),
        "summary": "Еженедельный обзор по локальным данным прогресса.",
        "weak_tasks": suggested_focus,
        "stats": {
            "tasks_started": len([p for p in progress_items if p.get("total_attempts", 0) > 0]),
            "tasks_mastered": len([p for p in progress_items if p.get("status") == "mastered"]),
            "total_attempts": sum(p.get("total_attempts", 0) for p in progress_items),
            "total_correct": sum(p.get("correct_attempts", 0) for p in progress_items),
        },
    }
    storage.save_weekly_review(review)
    return review


# ============== MOCK EXAM ==============

@app.get("/api/mock-exam")
async def get_mock_exam():
    mock_exam = storage.get_mock_exam()
    if mock_exam:
        return mock_exam

    theory_items = storage.list_theory()
    tasks = []
    for item in theory_items:
        tasks.append(
            {
                "task_number": item["task_number"],
                "title": item["title"],
                "status": "pending",
                "flagged": False,
                "answer": None,
                "code": None,
            }
        )

    mock_exam = {
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "mode": "full",
        "tasks": tasks,
    }
    storage.save_mock_exam(mock_exam)
    return mock_exam


@app.post("/api/mock-exam/answer")
async def submit_mock_exam_answer(payload: MockExamAnswer):
    exam = storage.get_mock_exam()
    if not exam:
        raise HTTPException(404, "Пробный экзамен не найден")

    updated = False
    for task in exam.get("tasks", []):
        if task["task_number"] == payload.task_number:
            task["answer"] = payload.answer
            task["code"] = payload.code
            task["status"] = "answered"
            updated = True
            break

    if not updated:
        raise HTTPException(404, "Задание не найдено в пробном экзамене")

    exam["updated_at"] = now_iso()
    storage.save_mock_exam(exam)
    return {"status": "ok"}


@app.post("/api/mock-exam/flag/{task_number}")
async def toggle_mock_exam_flag(task_number: int):
    exam = storage.get_mock_exam()
    if not exam:
        raise HTTPException(404, "Пробный экзамен не найден")

    for task in exam.get("tasks", []):
        if task["task_number"] == task_number:
            task["flagged"] = not task.get("flagged", False)
            break

    exam["updated_at"] = now_iso()
    storage.save_mock_exam(exam)
    return {"status": "ok"}


# ============== DRAFTS / AUTOSAVE FOUNDATION ==============

@app.get("/api/drafts/{scope}")
async def get_draft(scope: str):
    draft = storage.get_draft(scope)
    if not draft:
        raise HTTPException(404, "Draft not found")
    return draft


@app.put("/api/drafts/{scope}")
async def upsert_draft(scope: str, data: DraftUpsert):
    draft = {
        "scope": scope,
        "draft_type": data.draft_type,
        "task_number": data.task_number,
        "exercise_id": data.exercise_id,
        "payload": data.payload,
        "updated_at": now_iso(),
    }
    storage.save_draft(scope, draft)
    return {"status": "ok"}


@app.delete("/api/drafts/{scope}")
async def delete_draft(scope: str):
    storage.delete_draft(scope)
    return {"status": "ok"}


# ============== CONTENT / STORAGE INIT ==============

@app.on_event("startup")
async def startup_event():
    storage.initialize()
    await ensure_storage_seeded(force=False)


@app.post("/api/reseed")
async def reseed():
    result = await ensure_storage_seeded(force=True)
    return {
        "status": "ok",
        "theory": result["theory"],
        "exercises": result["exercises"],
        "roadmap": result["roadmap"],
    }


@app.get("/api/health")
async def health():
    build_index_exists = (FRONTEND_BUILD_DIR / "index.html").exists()
    return {
        "status": "ok",
        "timestamp": now_iso(),
        "storage": "sqlite",
        "db_path": str(storage.db_path),
        "serving_frontend_build": SERVE_FRONTEND_BUILD,
        "frontend_build_exists": build_index_exists,
    }


# ============== OPTIONAL FRONTEND BUILD HOSTING ==============

@app.get("/", include_in_schema=False)
async def serve_frontend_index():
    if not SERVE_FRONTEND_BUILD:
        raise HTTPException(404, "Frontend build hosting disabled")

    index_path = FRONTEND_BUILD_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(404, "Frontend build not found")

    return FileResponse(index_path)


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend_app(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(404, "Not found")

    if not SERVE_FRONTEND_BUILD:
        raise HTTPException(404, "Frontend build hosting disabled")

    index_path = FRONTEND_BUILD_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(404, "Frontend build not found")

    target = FRONTEND_BUILD_DIR / full_path
    if target.exists() and target.is_file():
        return FileResponse(target)

    if Path(full_path).suffix:
        raise HTTPException(404, "Static asset not found")

    return FileResponse(index_path)