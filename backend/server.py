import ast
import os
import subprocess
import sys
import tempfile
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
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

CODE_TASKS = {2, 5, 6, 8, 12, 13, 14, 15, 16, 17, 19, 20, 21, 23, 24, 25, 26, 27}

GUIDED_STAGES = [
    {
        "stage_number": 1,
        "kind": "learn",
        "title": "Старт: задания 1–5",
        "description": "Проход первого блока: базовая теория, короткая практика, без перескоков.",
        "tasks": [1, 2, 3, 4, 5],
        "min_attempts": 2,
        "min_accuracy": 60,
        "estimated_minutes": 90,
    },
    {
        "stage_number": 2,
        "kind": "revisit",
        "title": "Возврат 1–5: усложнённое закрепление",
        "description": "Возврат к первым заданиям с большей сложностью и контролем ошибок.",
        "tasks": [1, 2, 3, 4, 5],
        "min_attempts": 4,
        "min_accuracy": 72,
        "estimated_minutes": 80,
    },
    {
        "stage_number": 3,
        "kind": "learn",
        "title": "Дальше: задания 6–10",
        "description": "Второй блок нового материала.",
        "tasks": [6, 7, 8, 9, 10],
        "min_attempts": 2,
        "min_accuracy": 60,
        "estimated_minutes": 95,
    },
    {
        "stage_number": 4,
        "kind": "review",
        "title": "Weekly Review A",
        "description": "Обязательный контрольный блок по заданиям 1–10.",
        "review_index": 1,
        "review_tasks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "estimated_minutes": 35,
    },
    {
        "stage_number": 5,
        "kind": "revisit",
        "title": "Возврат 1–10: закрепление блока",
        "description": "Повторение пройденного до перехода в среднюю часть дорожки.",
        "tasks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "min_attempts": 4,
        "min_accuracy": 70,
        "estimated_minutes": 90,
    },
    {
        "stage_number": 6,
        "kind": "learn",
        "title": "Средний блок: задания 11–15",
        "description": "Основная середина дорожки, включая кодовые задания.",
        "tasks": [11, 12, 13, 14, 15],
        "min_attempts": 2,
        "min_accuracy": 60,
        "estimated_minutes": 110,
    },
    {
        "stage_number": 7,
        "kind": "review",
        "title": "Weekly Review B",
        "description": "Контроль и возврат по заданиям 6–15.",
        "review_index": 2,
        "review_tasks": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "estimated_minutes": 40,
    },
    {
        "stage_number": 8,
        "kind": "revisit",
        "title": "Возврат 6–15: сложнее и точнее",
        "description": "Повторение с упором на слабые темы и трудные упражнения.",
        "tasks": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "min_attempts": 4,
        "min_accuracy": 72,
        "estimated_minutes": 95,
    },
    {
        "stage_number": 9,
        "kind": "learn",
        "title": "Старший блок: задания 16–20",
        "description": "Продвинутая часть с высокой ценой ошибок.",
        "tasks": [16, 17, 18, 19, 20],
        "min_attempts": 2,
        "min_accuracy": 60,
        "estimated_minutes": 110,
    },
    {
        "stage_number": 10,
        "kind": "review",
        "title": "Weekly Review C",
        "description": "Контроль по заданиям 11–20.",
        "review_index": 3,
        "review_tasks": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        "estimated_minutes": 40,
    },
    {
        "stage_number": 11,
        "kind": "revisit",
        "title": "Возврат 11–20: работа над ошибками",
        "description": "Усложнённое повторение перед финальным блоком.",
        "tasks": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        "min_attempts": 4,
        "min_accuracy": 74,
        "estimated_minutes": 100,
    },
    {
        "stage_number": 12,
        "kind": "learn",
        "title": "Финиш: задания 21–27",
        "description": "Последний новый материал перед стабилизацией и пробниками.",
        "tasks": [21, 22, 23, 24, 25, 26, 27],
        "min_attempts": 2,
        "min_accuracy": 60,
        "estimated_minutes": 140,
    },
    {
        "stage_number": 13,
        "kind": "review",
        "title": "Weekly Review D",
        "description": "Обязательный контроль по завершающему блоку.",
        "review_index": 4,
        "review_tasks": [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
        "estimated_minutes": 45,
    },
    {
        "stage_number": 14,
        "kind": "revisit",
        "title": "Финальное закрепление 16–27",
        "description": "Последний возврат назад перед полноценными пробниками.",
        "tasks": [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
        "min_attempts": 4,
        "min_accuracy": 76,
        "estimated_minutes": 120,
    },
    {
        "stage_number": 15,
        "kind": "mock",
        "title": "Пробники и стабилизация",
        "description": "Формат, тайминг и доводка слабых мест.",
        "min_mock_exams": 1,
        "estimated_minutes": 235,
    },
]

TRAINING_MOCK_TASKS = [2, 5, 6, 8, 12, 14, 16, 17, 19, 23, 25, 27]


class ProfileCreate(BaseModel):
    name: str = "Ученик"
    target_score: int = 80
    exam_date: str = "2026-06-01"
    confidence_level: str = "medium"
    daily_hours: float = 2.0
    weekly_hours: float = 10.0
    font_size: int = 14
    learning_mode: str = "guided"


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    target_score: Optional[int] = None
    exam_date: Optional[str] = None
    confidence_level: Optional[str] = None
    daily_hours: Optional[float] = None
    weekly_hours: Optional[float] = None
    font_size: Optional[int] = None
    learning_mode: Optional[str] = None


class AnswerCheck(BaseModel):
    exercise_id: str
    answer: Any


class CodeRun(BaseModel):
    code: str
    stdin: str = ""


class CodeCheck(BaseModel):
    exercise_id: str
    code: str


class WeeklyReviewAnswer(BaseModel):
    exercise_id: str
    answer: Any


class MockExamStart(BaseModel):
    mode: str = "exam"


class MockExamAnswer(BaseModel):
    task_number: int
    answer: Any = None
    code: Optional[str] = None


class DraftUpsert(BaseModel):
    draft_type: str = "generic"
    task_number: Optional[int] = None
    exercise_id: Optional[str] = None
    payload: Any = None


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_iso() -> str:
    return now_utc().isoformat()


def parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def normalize_learning_mode(value: Optional[str]) -> str:
    return "free" if value == "free" else "guided"


def load_static_content() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        from .content_data import THEORY_DATA, EXERCISES_DATA, ROADMAP_DATA
    except ImportError:
        from content_data import THEORY_DATA, EXERCISES_DATA, ROADMAP_DATA
    return THEORY_DATA, EXERCISES_DATA, ROADMAP_DATA


async def ensure_storage_seeded(force: bool = False) -> dict[str, Any]:
    theory_data, exercises_data, roadmap_data = load_static_content()
    return storage.seed_static_content(theory_data, exercises_data, roadmap_data, force=force)


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


def get_profile_core() -> dict[str, Any]:
    profile = storage.get_profile()
    if profile:
        return profile
    profile = {
        "name": "Ученик",
        "target_score": 80,
        "exam_date": "2026-06-01",
        "confidence_level": "medium",
        "daily_hours": 2.0,
        "weekly_hours": 10.0,
        "font_size": 14,
        "learning_mode": "guided",
        "total_exercises_done": 0,
        "total_correct": 0,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    storage.save_profile(profile)
    return profile


def get_profile_payload() -> dict[str, Any]:
    profile = get_profile_core().copy()
    profile["exists"] = True
    return profile


def save_profile(profile: dict[str, Any]) -> dict[str, Any]:
    profile["learning_mode"] = normalize_learning_mode(profile.get("learning_mode"))
    profile["updated_at"] = now_iso()
    storage.save_profile(profile)
    return profile


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


def is_objective_exercise(exercise: dict[str, Any]) -> bool:
    answer_type = exercise.get("answer_type")
    exercise_type = exercise.get("exercise_type")
    return exercise_type == "code" or answer_type in {"single_choice", "multiple_choice", "number"}


def choose_exercises_for_task(
    task_number: int,
    *,
    mode: str = "free",
    prefer_harder: bool = False,
    limit: int = 8,
) -> list[dict[str, Any]]:
    theory_item = storage.get_theory(task_number) or {}
    should_be_code = task_number in CODE_TASKS or theory_item.get("is_code_task")

    exercises = storage.list_exercises(task_number=task_number, only_objective=True)
    if should_be_code:
        code_exercises = [item for item in exercises if item.get("exercise_type") == "code"]
        if code_exercises:
            exercises = code_exercises

    def difficulty_rank(value: str) -> int:
        order = {"easy": 0, "medium": 1, "hard": 2}
        return order.get(value or "medium", 1)

    exercises = sorted(
        exercises,
        key=lambda item: (
            0 if (should_be_code and item.get("exercise_type") == "code") else 1,
            -difficulty_rank(item.get("difficulty")) if prefer_harder else difficulty_rank(item.get("difficulty")),
            item.get("exercise_id", ""),
        ),
    )

    if mode == "guided":
        return exercises[: min(limit, 6)]
    if mode == "weak":
        return exercises[: min(limit, 6)]
    if mode == "mistakes":
        return exercises[: min(limit, 5)]
    return exercises[:limit]


def record_attempt(task_number: int, exercise_id: str, correct: bool, attempt_type: str, payload: dict[str, Any]) -> None:
    storage.add_attempt(
        {
            "task_number": task_number,
            "exercise_id": exercise_id,
            "correct": correct,
            "attempt_type": attempt_type,
            "timestamp": now_iso(),
            **payload,
        }
    )
    update_progress_after_attempt(task_number, correct)


def update_progress_after_attempt(task_number: int, correct: bool) -> dict[str, Any]:
    progress = storage.get_progress(task_number) or {
        "task_number": task_number,
        "total_attempts": 0,
        "correct_attempts": 0,
        "accuracy": 0,
        "status": "not_started",
    }
    progress["total_attempts"] = safe_int(progress.get("total_attempts")) + 1
    progress["correct_attempts"] = safe_int(progress.get("correct_attempts")) + (1 if correct else 0)
    progress["accuracy"] = round(
        (progress["correct_attempts"] / progress["total_attempts"]) * 100, 2
    ) if progress["total_attempts"] else 0.0
    progress["last_practiced"] = now_iso()
    progress["updated_at"] = progress["last_practiced"]

    attempts = progress["total_attempts"]
    accuracy = progress["accuracy"]
    if attempts >= 6 and accuracy >= 85:
        progress["status"] = "mastered"
    elif attempts >= 3 and accuracy >= 70:
        progress["status"] = "stable"
    elif attempts > 0:
        progress["status"] = "learning"
    else:
        progress["status"] = "not_started"

    storage.save_progress(progress)

    profile = get_profile_core()
    profile["total_exercises_done"] = storage.count_attempts()
    profile["total_correct"] = storage.count_attempts(correct=True)
    save_profile(profile)
    return progress


def evaluate_answer_against_exercise(exercise: dict[str, Any], submitted_answer: Any) -> tuple[bool, Any]:
    expected_answer = exercise.get("correct_answer")
    correct = False

    if exercise.get("exercise_type") == "code":
        return False, expected_answer

    if isinstance(expected_answer, list):
        if isinstance(submitted_answer, list):
            correct = sorted(str(item) for item in submitted_answer) == sorted(str(item) for item in expected_answer)
        else:
            correct = str(submitted_answer) in {str(item) for item in expected_answer}
    else:
        correct = str(submitted_answer).strip() == str(expected_answer).strip()
    return correct, expected_answer


def evaluate_code_against_exercise(exercise: dict[str, Any], source_code: str) -> dict[str, Any]:
    tests = exercise.get("tests") or []
    if not tests:
        return {
            "correct": False,
            "message": "Для этой задачи пока не настроены тесты.",
            "details": "Тестов нет, поэтому автоматическая проверка недоступна.",
            "test_results": [],
            "explanation": exercise.get("explanation", ""),
        }

    failures: list[str] = []
    test_results: list[dict[str, Any]] = []
    all_passed = True

    for index, test in enumerate(tests, start=1):
        run_result = run_python_code(source_code, test.get("input", ""))
        actual_output = (run_result.get("stdout") or "").strip()
        expected_output = (test.get("output") or "").strip()

        if run_result.get("returncode") != 0:
            all_passed = False
            failures.append(f"Тест {index}: ошибка выполнения.")
            test_results.append(
                {
                    "test_number": index,
                    "passed": False,
                    "expected": expected_output,
                    "actual": run_result.get("stderr", "").strip(),
                    "is_public": True,
                }
            )
            continue

        passed = actual_output == expected_output
        if not passed:
            all_passed = False
            failures.append(f"Тест {index}: ожидалось {expected_output}, получено {actual_output}")
        test_results.append(
            {
                "test_number": index,
                "passed": passed,
                "expected": expected_output,
                "actual": actual_output,
                "is_public": True,
            }
        )

    return {
        "correct": all_passed,
        "message": "Код прошёл проверку" if all_passed else "Код не прошёл проверку",
        "details": "\n".join(failures),
        "test_results": test_results,
        "explanation": exercise.get("explanation", ""),
    }


def build_progress_metrics() -> dict[str, Any]:
    theory_items = storage.list_theory()
    progress_rows = {row["task_number"]: row for row in storage.list_progress()}
    attempts = storage.list_recent_attempts(limit=180)
    completed_mock_exams = storage.list_completed_mock_exams(limit=12)
    completed_reviews = storage.list_completed_weekly_reviews(limit=12)

    task_metrics: list[dict[str, Any]] = []
    weak_tasks: list[int] = []
    mistake_burden: dict[int, int] = defaultdict(int)

    for attempt in attempts[:60]:
        if not attempt.get("correct"):
            mistake_burden[safe_int(attempt.get("task_number"))] += 1

    for theory in theory_items:
        task_number = theory["task_number"]
        row = progress_rows.get(task_number, {})
        total_attempts = safe_int(row.get("total_attempts"))
        correct_attempts = safe_int(row.get("correct_attempts"))
        accuracy = round(float(row.get("accuracy", 0) or 0), 2)
        last_practiced = row.get("last_practiced")
        incorrect_count = total_attempts - correct_attempts
        mastery_score = round(
            clamp((accuracy * 0.72) + min(total_attempts, 8) * 3.5 + (8 if total_attempts >= 3 else 0), 0, 100),
            1,
        )

        if total_attempts == 0:
            status = "not_started"
        elif accuracy >= 85 and total_attempts >= 6:
            status = "mastered"
        elif accuracy >= 70 and total_attempts >= 3:
            status = "stable"
        elif accuracy >= 50:
            status = "developing"
        else:
            status = "weak"

        if total_attempts > 0 and (accuracy < 65 or incorrect_count >= correct_attempts + 1 or mistake_burden.get(task_number, 0) >= 2):
            weak_tasks.append(task_number)

        task_metrics.append(
            {
                "task_number": task_number,
                "title": theory.get("title", f"Задание {task_number}"),
                "is_code_task": bool(theory.get("is_code_task") or task_number in CODE_TASKS),
                "total_attempts": total_attempts,
                "correct_attempts": correct_attempts,
                "accuracy": accuracy,
                "incorrect_attempts": incorrect_count,
                "status": status,
                "last_practiced": last_practiced,
                "mastery_score": mastery_score,
                "mistake_burden": mistake_burden.get(task_number, 0),
            }
        )

    task_map = {item["task_number"]: item for item in task_metrics}
    started_tasks = [item for item in task_metrics if item["total_attempts"] > 0]
    coverage = round((len(started_tasks) / max(len(task_metrics), 1)) * 100, 1)
    avg_accuracy = round(mean([item["accuracy"] for item in started_tasks]), 1) if started_tasks else 0.0

    recent_mock_scores = [float(item.get("score", 0) or 0) for item in completed_mock_exams[:5] if item.get("score") is not None]
    recent_mock_avg = round(mean(recent_mock_scores), 1) if recent_mock_scores else None

    signal = (
        avg_accuracy * 0.45
        + coverage * 0.35
        + ((recent_mock_avg if recent_mock_avg is not None else avg_accuracy) * 0.20)
    )
    weak_penalty = min(18, len(weak_tasks) * 1.1)
    predicted = round(clamp(signal - weak_penalty, 0, 100), 1)
    spread = 10 if len(started_tasks) < 7 else 7 if len(started_tasks) < 14 else 5
    estimated_score = {
        "min": int(clamp(predicted - spread, 0, 100)),
        "max": int(clamp(predicted + spread, 0, 100)),
        "center": predicted,
        "level": "strong" if predicted >= 82 else "good" if predicted >= 68 else "medium" if predicted >= 45 else "early",
        "description": (
            "Прогноз основан на покрытии тем, точности и завершённых пробниках."
            if started_tasks
            else "Нужны первые решённые задания, чтобы строить прогноз."
        ),
    }

    history_by_day: dict[str, dict[str, int]] = defaultdict(lambda: {"attempts": 0, "correct": 0})
    for attempt in attempts:
        stamp = parse_iso(attempt.get("timestamp"))
        day_key = stamp.date().isoformat() if stamp else "unknown"
        history_by_day[day_key]["attempts"] += 1
        history_by_day[day_key]["correct"] += 1 if attempt.get("correct") else 0

    history_points = []
    for day_key in sorted(history_by_day.keys())[-14:]:
        point = history_by_day[day_key]
        attempts_count = point["attempts"]
        history_points.append(
            {
                "date": day_key,
                "attempts": attempts_count,
                "accuracy": round((point["correct"] / attempts_count) * 100, 1) if attempts_count else 0,
            }
        )

    mistake_tasks = []
    seen_tasks: set[int] = set()
    for attempt in attempts:
        if attempt.get("correct"):
            continue
        task_number = safe_int(attempt.get("task_number"))
        if task_number in seen_tasks:
            continue
        seen_tasks.add(task_number)
        mistake_tasks.append(task_number)
        if len(mistake_tasks) >= 6:
            break

    return {
        "coverage": coverage,
        "avg_accuracy": avg_accuracy,
        "total_attempts": storage.count_attempts(),
        "total_correct": storage.count_attempts(correct=True),
        "tasks": task_metrics,
        "task_map": task_map,
        "estimated_score": estimated_score,
        "weak_tasks": weak_tasks[:8],
        "mistake_tasks": mistake_tasks,
        "history": history_points,
        "mock_exams_completed": len(completed_mock_exams),
        "weekly_reviews_completed": len(completed_reviews),
        "recent_mock_avg": recent_mock_avg,
    }


def is_stage_complete(stage: dict[str, Any], progress_map: dict[int, dict[str, Any]], reviews_completed: int, mocks_completed: int) -> bool:
    kind = stage["kind"]
    if kind in {"learn", "revisit"}:
        for task_number in stage.get("tasks", []):
            item = progress_map.get(task_number, {})
            if item.get("total_attempts", 0) < stage.get("min_attempts", 0):
                return False
            if item.get("accuracy", 0) < stage.get("min_accuracy", 0):
                return False
        return True
    if kind == "review":
        return reviews_completed >= stage.get("review_index", 0)
    if kind == "mock":
        return mocks_completed >= stage.get("min_mock_exams", 1)
    return False


def build_today_plan(
    current_stage: dict[str, Any],
    progress_metrics: dict[str, Any],
    profile: dict[str, Any],
    review_due: bool,
    weak_details: list[dict[str, Any]],
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []

    if review_due:
        items.append(
            {
                "type": "weekly_review",
                "title": "Сначала обязательный Weekly Review",
                "description": "Дорожка остановлена до прохождения контрольного блока.",
                "minutes": current_stage.get("estimated_minutes", 35),
                "href": "/weekly-review",
                "action_label": "Открыть Weekly Review",
            }
        )
    elif current_stage.get("kind") in {"learn", "revisit"}:
        for task_number in current_stage.get("tasks", [])[:3]:
            task_data = progress_metrics["task_map"].get(task_number, {})
            if task_data.get("total_attempts", 0) == 0:
                items.append(
                    {
                        "type": "theory",
                        "title": f"Кратко пройти теорию по заданию {task_number}",
                        "description": "Открыть краткую и полную теорию, затем перейти к практике.",
                        "minutes": 15,
                        "href": f"/theory?task={task_number}",
                        "action_label": "К теории",
                    }
                )
                items.append(
                    {
                        "type": "practice",
                        "title": f"Решать задание {task_number} в guided mode",
                        "description": "Наберите первые попытки по текущему этапу.",
                        "minutes": 20,
                        "href": f"/practice?task={task_number}&mode=guided",
                        "action_label": "К практике",
                    }
                )
                break

        if not items and current_stage.get("tasks"):
            weakest_inside_stage = sorted(
                [progress_metrics["task_map"].get(task_number, {}) for task_number in current_stage["tasks"]],
                key=lambda item: (item.get("accuracy", 0), item.get("total_attempts", 0)),
            )[0]
            items.append(
                {
                    "type": "practice",
                    "title": f"Добрать точность по заданию {weakest_inside_stage.get('task_number')}",
                    "description": "Это задание сильнее всего тормозит переход к следующему этапу.",
                    "minutes": 25,
                    "href": f"/practice?task={weakest_inside_stage.get('task_number')}&mode=guided",
                    "action_label": "Открыть guided practice",
                }
            )
    else:
        items.append(
            {
                "type": "mock",
                "title": "Перейти к пробнику",
                "description": "Guided path доведён до режима стабилизации.",
                "minutes": 120,
                "href": "/mock-exam",
                "action_label": "Открыть пробник",
            }
        )

    if weak_details:
        task_number = weak_details[0]["task_number"]
        items.append(
            {
                "type": "weak",
                "title": f"Вернуться к слабой теме №{task_number}",
                "description": weak_details[0]["reason"],
                "minutes": 20,
                "href": f"/practice?task={task_number}&mode=weak",
                "action_label": "Слабые темы",
            }
        )

    if progress_metrics["mistake_tasks"]:
        task_number = progress_metrics["mistake_tasks"][0]
        items.append(
            {
                "type": "mistakes",
                "title": f"Разобрать недавние ошибки по №{task_number}",
                "description": "Режим ошибок показывает темы, где были последние промахи.",
                "minutes": 15,
                "href": f"/practice?task={task_number}&mode=mistakes",
                "action_label": "К ошибкам",
            }
        )

    daily_hours = float(profile.get("daily_hours", 2) or 2)
    total_minutes = int(sum(item["minutes"] for item in items[:3]))
    return {
        "summary": "Понятный план на сегодня без лишней геймификации.",
        "daily_budget_minutes": int(daily_hours * 60),
        "planned_minutes": total_minutes,
        "items": items[:3],
    }


def build_roadmap_payload() -> dict[str, Any]:
    profile = get_profile_core()
    progress_metrics = build_progress_metrics()
    progress_map = progress_metrics["task_map"]
    reviews_completed = progress_metrics["weekly_reviews_completed"]
    mocks_completed = progress_metrics["mock_exams_completed"]

    current_stage = GUIDED_STAGES[-1]
    for stage in GUIDED_STAGES:
        if not is_stage_complete(stage, progress_map, reviews_completed, mocks_completed):
            current_stage = stage
            break

    stages_payload = []
    review_due = current_stage.get("kind") == "review"
    weak_details = []
    for task_number in progress_metrics["weak_tasks"][:6]:
        item = progress_map.get(task_number, {})
        weak_details.append(
            {
                "task_number": task_number,
                "accuracy": item.get("accuracy", 0),
                "attempts": item.get("total_attempts", 0),
                "reason": (
                    "Низкая точность после серии попыток."
                    if item.get("accuracy", 0) < 60
                    else "Задание решается нестабильно и требует закрепления."
                ),
            }
        )

    for stage in GUIDED_STAGES:
        stage_complete = is_stage_complete(stage, progress_map, reviews_completed, mocks_completed)
        stage_tasks = stage.get("tasks", [])
        stage_attempts = [progress_map.get(task_number, {}) for task_number in stage_tasks]
        covered = len([item for item in stage_attempts if item.get("total_attempts", 0) > 0])
        stage_accuracy = round(mean([item.get("accuracy", 0) for item in stage_attempts if item.get("total_attempts", 0) > 0]), 1) if covered else 0
        if stage_tasks:
            progress_pct = round((covered / len(stage_tasks)) * 100, 1)
        elif stage["kind"] == "review":
            progress_pct = 100.0 if reviews_completed >= stage.get("review_index", 0) else 0.0
        else:
            progress_pct = 100.0 if mocks_completed >= stage.get("min_mock_exams", 1) else 0.0

        stages_payload.append(
            {
                **stage,
                "is_current": stage["stage_number"] == current_stage["stage_number"],
                "is_completed": stage_complete,
                "progress_pct": progress_pct,
                "avg_accuracy": stage_accuracy,
                "blocked_by_review": review_due and stage["stage_number"] > current_stage["stage_number"],
            }
        )

    if current_stage["kind"] in {"learn", "revisit"}:
        current_focus_tasks = current_stage.get("tasks", [])
    elif current_stage["kind"] == "review":
        current_focus_tasks = current_stage.get("review_tasks", [])
    else:
        current_focus_tasks = list(range(1, 28))

    today_plan = build_today_plan(current_stage, progress_metrics, profile, review_due, weak_details)

    return {
        "profile_learning_mode": normalize_learning_mode(profile.get("learning_mode")),
        "dashboard_title": "Дашборд подготовки",
        "current_stage": current_stage["stage_number"],
        "current_stage_title": current_stage["title"],
        "current_stage_kind": current_stage["kind"],
        "current_focus_tasks": current_focus_tasks,
        "review_due": review_due,
        "review_gate_label": current_stage["title"] if review_due else None,
        "stages": stages_payload,
        "weak_tasks": progress_metrics["weak_tasks"][:6],
        "weak_task_details": weak_details,
        "mistake_tasks": progress_metrics["mistake_tasks"],
        "progress_data": progress_map,
        "today_plan": today_plan,
        "quick_actions": [
            {"label": "Свободная практика", "href": "/practice?mode=free"},
            {"label": "Guided path", "href": "/practice?mode=guided"},
            {"label": "Weekly Review", "href": "/weekly-review"},
            {"label": "Пробник", "href": "/mock-exam"},
        ],
        "summary": {
            "coverage": progress_metrics["coverage"],
            "accuracy": progress_metrics["avg_accuracy"],
            "estimated_score": progress_metrics["estimated_score"],
            "mock_exams_completed": progress_metrics["mock_exams_completed"],
            "weekly_reviews_completed": progress_metrics["weekly_reviews_completed"],
        },
    }


def build_weekly_review_blueprint(active_only: bool = False) -> dict[str, Any]:
    active_review = storage.get_active_weekly_review()
    if active_review:
        return active_review

    roadmap = build_roadmap_payload()
    current_stage = next(stage for stage in roadmap["stages"] if stage["stage_number"] == roadmap["current_stage"])
    progress = build_progress_metrics()
    weak_tasks = roadmap["weak_tasks"]
    base_tasks = list(dict.fromkeys((current_stage.get("review_tasks") or current_stage.get("tasks") or []) + weak_tasks))
    if not base_tasks:
        base_tasks = [item["task_number"] for item in progress["tasks"][:6]]

    selected_exercises: list[dict[str, Any]] = []
    for task_number in base_tasks:
        exercises = choose_exercises_for_task(task_number, mode="weak", prefer_harder=False, limit=3)
        objective_exercises = [item for item in exercises if item.get("exercise_type") != "code"]
        if not objective_exercises:
            objective_exercises = [item for item in exercises if is_objective_exercise(item)]
        if objective_exercises:
            selected_exercises.append(objective_exercises[0])
        if len(selected_exercises) >= 8:
            break

    return {
        "status": "ready",
        "summary": "Weekly Review собирается из текущего этапа, слабых тем и недавних ошибок.",
        "review_tasks": list(dict.fromkeys(item["task_number"] for item in selected_exercises)),
        "weak_tasks": weak_tasks,
        "estimated_time": max(20, len(selected_exercises) * 4),
        "exercises": selected_exercises,
        "required_checkpoint": roadmap["review_due"],
        "checkpoint_label": roadmap["review_gate_label"],
        "completed_reviews": progress["weekly_reviews_completed"],
        "has_active": False,
        "answers_count": 0,
        "correct_count": 0,
    }


def build_mock_exam_task(task_number: int, mode: str) -> dict[str, Any]:
    prefer_harder = mode == "exam"
    exercises = choose_exercises_for_task(task_number, mode="guided", prefer_harder=prefer_harder, limit=6)
    exercise = exercises[0] if exercises else None
    theory = storage.get_theory(task_number) or {}
    return {
        "task_number": task_number,
        "title": theory.get("title", f"Задание {task_number}"),
        "status": "pending",
        "flagged": False,
        "answer": None,
        "code": exercise.get("code_template", "") if exercise and exercise.get("exercise_type") == "code" else None,
        "exercise": exercise,
        "is_code_task": bool(theory.get("is_code_task") or task_number in CODE_TASKS),
    }


def mock_elapsed_seconds(exam: dict[str, Any]) -> int:
    started_at = parse_iso(exam.get("started_at"))
    if not started_at:
        return safe_int(exam.get("elapsed_seconds"), 0)

    total_paused_seconds = safe_int(exam.get("total_paused_seconds"), 0)
    if exam.get("status") == "paused":
        paused_at = parse_iso(exam.get("paused_at"))
        if paused_at:
            return max(0, int((paused_at - started_at).total_seconds()) - total_paused_seconds)
    return max(0, int((now_utc() - started_at).total_seconds()) - total_paused_seconds)


def mock_exam_status_payload() -> dict[str, Any]:
    active_exam = storage.get_active_mock_exam()
    recent_exams = storage.list_completed_mock_exams(limit=8)

    payload = {
        "has_active": bool(active_exam),
        "exam": None,
        "recent_exams": [
            {
                "exam_id": item.get("exam_id"),
                "mode": item.get("mode"),
                "score": item.get("score"),
                "correct_count": item.get("correct_count"),
                "total_count": item.get("total_count"),
                "completed_at": item.get("completed_at"),
            }
            for item in recent_exams
        ],
        "modes": [
            {
                "mode": "exam",
                "label": "Экзаменационный",
                "duration_minutes": 235,
                "tasks_count": 27,
                "description": "Максимально похоже на реальный экзамен.",
            },
            {
                "mode": "training",
                "label": "Тренировочный",
                "duration_minutes": 120,
                "tasks_count": len(TRAINING_MOCK_TASKS),
                "description": "Укороченный пробник с акцентом на тренируемые типы задач.",
            },
        ],
    }
    if active_exam:
        exam = active_exam.copy()
        exam["elapsed_seconds"] = mock_elapsed_seconds(exam)
        payload["exam"] = exam
    return payload


@app.get("/api/theory")
async def list_theory():
    return storage.list_theory()


@app.get("/api/theory/{task_number}")
async def get_theory(task_number: int):
    return get_theory_or_404(task_number)


@app.get("/api/exercises")
async def list_exercises(
    task: Optional[int] = None,
    mode: str = "free",
):
    if task is None:
        return []
    prefer_harder = mode in {"guided", "weak", "mistakes"}
    return choose_exercises_for_task(task, mode=mode, prefer_harder=prefer_harder)


@app.get("/api/exercises/{task_number}")
async def list_exercises_for_task(
    task_number: int,
    mode: str = Query(default="free"),
):
    prefer_harder = mode in {"guided", "weak", "mistakes"}
    return choose_exercises_for_task(task_number, mode=mode, prefer_harder=prefer_harder)


@app.get("/api/exercise/{exercise_id}")
async def get_exercise_alias(exercise_id: str):
    return get_exercise_or_404(exercise_id)

@app.post("/api/check-answer")
async def check_answer(payload: AnswerCheck):
    exercise = get_exercise_or_404(payload.exercise_id)
    if exercise.get("exercise_type") == "code":
        raise HTTPException(400, "Для кодовых задач используйте /api/check-code")

    correct, expected_answer = evaluate_answer_against_exercise(exercise, payload.answer)
    record_attempt(
        exercise["task_number"],
        exercise["exercise_id"],
        correct,
        "practice_answer",
        {
            "submitted_answer": payload.answer,
            "correct_answer": expected_answer,
        },
    )
    return {
        "correct": correct,
        "expected": expected_answer,
        "explanation": exercise.get("explanation", ""),
    }


@app.post("/api/exercises/check")
async def check_answer_alias(payload: AnswerCheck):
    return await check_answer(payload)


@app.post("/api/run-code")
async def run_code(payload: CodeRun):
    return run_python_code(payload.code, payload.stdin)


@app.post("/api/code/run")
async def run_code_alias(payload: CodeRun):
    return await run_code(payload)


@app.post("/api/check-code")
async def check_code(payload: CodeCheck):
    exercise = get_exercise_or_404(payload.exercise_id)
    result = evaluate_code_against_exercise(exercise, payload.code)
    record_attempt(
        exercise["task_number"],
        exercise["exercise_id"],
        bool(result["correct"]),
        "practice_code",
        {
            "submitted_code": payload.code,
        },
    )
    return result


@app.post("/api/code/check")
async def check_code_alias(payload: CodeCheck):
    return await check_code(payload)


@app.get("/api/profile")
async def get_profile():
    return get_profile_payload()


@app.post("/api/profile")
async def create_profile(payload: ProfileCreate):
    profile = get_profile_core()
    profile.update(
        {
            "name": payload.name,
            "target_score": payload.target_score,
            "exam_date": payload.exam_date,
            "confidence_level": payload.confidence_level,
            "daily_hours": payload.daily_hours,
            "weekly_hours": payload.weekly_hours,
            "font_size": payload.font_size,
            "learning_mode": normalize_learning_mode(payload.learning_mode),
        }
    )
    save_profile(profile)
    return get_profile_payload()


@app.put("/api/profile")
async def update_profile(payload: ProfileUpdate):
    profile = get_profile_core()
    update_data = payload.model_dump(exclude_unset=True)
    if "learning_mode" in update_data:
        update_data["learning_mode"] = normalize_learning_mode(update_data.get("learning_mode"))
    profile.update(update_data)
    save_profile(profile)
    return get_profile_payload()


@app.post("/api/profile/reset")
async def reset_profile():
    profile = get_profile_core()
    storage.clear_progress_state()
    profile["total_exercises_done"] = 0
    profile["total_correct"] = 0
    save_profile(profile)
    return {"status": "ok"}


@app.get("/api/progress")
async def get_progress():
    metrics = build_progress_metrics()
    return metrics


@app.get("/api/progress/{task_number}")
async def get_progress_for_task(task_number: int):
    metrics = build_progress_metrics()
    task = metrics["task_map"].get(task_number)
    if not task:
        raise HTTPException(404, "Прогресс по заданию не найден")
    return task


@app.get("/api/attempts/{task_number}")
async def get_attempts(task_number: int, limit: int = 20):
    return storage.list_attempts(task_number, limit=limit)


@app.get("/api/history")
async def get_history(limit: int = 60):
    return storage.list_recent_attempts(limit=limit)


@app.get("/api/roadmap")
async def get_roadmap():
    return build_roadmap_payload()


@app.get("/api/weekly-review")
async def get_weekly_review():
    active_review = storage.get_active_weekly_review()
    if active_review:
        return active_review
    return build_weekly_review_blueprint()


@app.post("/api/weekly-review/start")
async def start_weekly_review():
    active_review = storage.get_active_weekly_review()
    if active_review:
        return active_review

    blueprint = build_weekly_review_blueprint()
    if not blueprint.get("exercises"):
        raise HTTPException(400, "Не удалось собрать Weekly Review: недостаточно объективных заданий.")

    review = {
        **blueprint,
        "review_id": f"review-{uuid.uuid4().hex[:10]}",
        "status": "active",
        "started_at": now_iso(),
        "completed_at": None,
        "has_active": True,
        "answers": {},
        "results": {},
        "answers_count": 0,
        "correct_count": 0,
    }
    storage.insert_weekly_review(review)
    return review


@app.post("/api/weekly-review/answer")
async def answer_weekly_review(payload: WeeklyReviewAnswer):
    review = storage.get_active_weekly_review()
    if not review:
        raise HTTPException(404, "Активный Weekly Review не найден")

    exercise = next((item for item in review.get("exercises", []) if item.get("exercise_id") == payload.exercise_id), None)
    if not exercise:
        raise HTTPException(404, "Задание не найдено в активном Weekly Review")

    if exercise.get("exercise_type") == "code":
        raise HTTPException(400, "Weekly Review принимает только объективные ответы.")

    correct, expected_answer = evaluate_answer_against_exercise(exercise, payload.answer)
    review.setdefault("answers", {})[payload.exercise_id] = payload.answer
    review.setdefault("results", {})[payload.exercise_id] = {
        "correct": correct,
        "expected": expected_answer,
        "explanation": exercise.get("explanation", ""),
    }
    review["answers_count"] = len(review["results"])
    review["correct_count"] = sum(1 for item in review["results"].values() if item.get("correct"))

    storage.save_active_weekly_review(review)

    record_attempt(
        exercise["task_number"],
        exercise["exercise_id"],
        correct,
        "weekly_review",
        {
            "submitted_answer": payload.answer,
            "correct_answer": expected_answer,
            "review_id": review["review_id"],
        },
    )

    return review["results"][payload.exercise_id]


@app.post("/api/weekly-review/complete")
async def complete_weekly_review():
    review = storage.get_active_weekly_review()
    if not review:
        raise HTTPException(404, "Активный Weekly Review не найден")

    total = len(review.get("exercises", []))
    answers_count = safe_int(review.get("answers_count"), 0)
    if total == 0:
        raise HTTPException(400, "Weekly Review пуст.")
    if answers_count < max(3, total - 1):
        raise HTTPException(400, "Нужно ответить почти на все задания review, прежде чем завершать.")

    review["status"] = "completed"
    review["has_active"] = False
    review["completed_at"] = now_iso()
    review["score"] = round((safe_int(review.get("correct_count"), 0) / total) * 100, 1)
    storage.save_active_weekly_review(review)
    return review


@app.get("/api/mock-exam")
async def get_mock_exam():
    return mock_exam_status_payload()


@app.post("/api/mock-exam/start")
async def start_mock_exam(payload: MockExamStart):
    active_exam = storage.get_active_mock_exam()
    if active_exam:
        return mock_exam_status_payload()

    mode = "training" if payload.mode == "training" else "exam"
    task_numbers = TRAINING_MOCK_TASKS if mode == "training" else list(range(1, 28))
    exam_id = f"mock-{uuid.uuid4().hex[:10]}"

    exam = {
        "exam_id": exam_id,
        "mode": mode,
        "status": "active",
        "started_at": now_iso(),
        "completed_at": None,
        "paused_at": None,
        "total_paused_seconds": 0,
        "duration_minutes": 120 if mode == "training" else 235,
        "tasks": [build_mock_exam_task(task_number, mode) for task_number in task_numbers],
        "results": [],
        "score": None,
        "correct_count": None,
        "total_count": len(task_numbers),
    }
    storage.save_mock_exam(exam)
    return mock_exam_status_payload()


@app.put("/api/mock-exam/{exam_id}/answer")
async def save_mock_exam_answer(exam_id: str, payload: MockExamAnswer):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "Пробник не найден")
    if exam.get("status") == "completed":
        raise HTTPException(400, "Пробник уже завершён")

    updated = False
    for task in exam.get("tasks", []):
        if task["task_number"] == payload.task_number:
            task["answer"] = payload.answer
            task["code"] = payload.code
            task["status"] = "answered" if (payload.answer not in {None, ""} or payload.code) else "pending"
            updated = True
            break
    if not updated:
        raise HTTPException(404, "Задание не найдено в пробнике")

    storage.save_mock_exam(exam)
    return {"status": "ok"}


@app.put("/api/mock-exam/{exam_id}/flag")
async def flag_mock_exam_task(exam_id: str, payload: MockExamAnswer):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "Пробник не найден")

    for task in exam.get("tasks", []):
        if task["task_number"] == payload.task_number:
            task["flagged"] = not task.get("flagged", False)
            storage.save_mock_exam(exam)
            return {"status": "ok", "flagged": task["flagged"]}
    raise HTTPException(404, "Задание не найдено")


@app.put("/api/mock-exam/{exam_id}/flag/{task_number}")
async def flag_mock_exam_task_compat(exam_id: str, task_number: int):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "Пробник не найден")

    for task in exam.get("tasks", []):
        if task["task_number"] == task_number:
            task["flagged"] = not task.get("flagged", False)
            storage.save_mock_exam(exam)
            return {"status": "ok", "flagged": task["flagged"]}
    raise HTTPException(404, "Задание не найдено")


@app.post("/api/mock-exam/{exam_id}/pause")
async def pause_mock_exam(exam_id: str):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "Пробник не найден")
    if exam.get("status") == "paused":
        return {"status": "ok"}
    if exam.get("status") == "completed":
        raise HTTPException(400, "Пробник уже завершён")

    exam["elapsed_seconds"] = mock_elapsed_seconds(exam)
    exam["paused_at"] = now_iso()
    exam["status"] = "paused"
    storage.save_mock_exam(exam)
    return {"status": "ok", "elapsed_seconds": exam["elapsed_seconds"]}


@app.post("/api/mock-exam/{exam_id}/resume")
async def resume_mock_exam(exam_id: str):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "Пробник не найден")
    if exam.get("status") != "paused":
        return {"status": "ok"}

    paused_at = parse_iso(exam.get("paused_at"))
    if paused_at:
        exam["total_paused_seconds"] = safe_int(exam.get("total_paused_seconds"), 0) + int((now_utc() - paused_at).total_seconds())
    exam["paused_at"] = None
    exam["status"] = "active"
    storage.save_mock_exam(exam)
    return {"status": "ok"}


@app.post("/api/mock-exam/{exam_id}/submit")
async def submit_mock_exam(exam_id: str):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "Пробник не найден")
    if exam.get("status") == "completed":
        return exam

    results = []
    correct_count = 0

    for task in exam.get("tasks", []):
        exercise = task.get("exercise")
        task_number = task.get("task_number")
        if not exercise:
            results.append(
                {
                    "task_number": task_number,
                    "correct": False,
                    "explanation": "Для этого задания не найдено упражнение в локальной базе.",
                }
            )
            continue

        if exercise.get("exercise_type") == "code":
            evaluation = evaluate_code_against_exercise(exercise, task.get("code") or "")
            correct = bool(evaluation.get("correct"))
            if task.get("code"):
                record_attempt(
                    task_number,
                    exercise["exercise_id"],
                    correct,
                    "mock_code",
                    {
                        "submitted_code": task.get("code"),
                        "exam_id": exam_id,
                    },
                )
        else:
            correct, expected_answer = evaluate_answer_against_exercise(exercise, task.get("answer"))
            record_attempt(
                task_number,
                exercise["exercise_id"],
                correct,
                "mock_answer",
                {
                    "submitted_answer": task.get("answer"),
                    "correct_answer": expected_answer,
                    "exam_id": exam_id,
                },
            )
            evaluation = {
                "correct": correct,
                "expected": expected_answer,
                "explanation": exercise.get("explanation", ""),
            }

        correct_count += 1 if correct else 0
        results.append(
            {
                "task_number": task_number,
                "correct": correct,
                "explanation": evaluation.get("explanation", ""),
                "details": evaluation.get("details", ""),
            }
        )

    total_count = len(exam.get("tasks", []))
    score = round((correct_count / total_count) * 100, 1) if total_count else 0.0
    exam["results"] = results
    exam["correct_count"] = correct_count
    exam["total_count"] = total_count
    exam["score"] = score
    exam["completed_at"] = now_iso()
    exam["status"] = "completed"
    exam["elapsed_seconds"] = mock_elapsed_seconds(exam)
    exam["paused_at"] = None
    storage.save_mock_exam(exam)

    return {
        "exam_id": exam_id,
        "mode": exam.get("mode"),
        "score": score,
        "correct": correct_count,
        "total": total_count,
        "elapsed_seconds": exam["elapsed_seconds"],
        "results": results,
    }


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
