import ast
import mimetypes
import os
import random
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
        "title": "РЎС‚Р°СЂС‚: Р·Р°РґР°РЅРёСЏ 1вЂ“5",
        "description": "РџСЂРѕС…РѕРґ РїРµСЂРІРѕРіРѕ Р±Р»РѕРєР°: Р±Р°Р·РѕРІР°СЏ С‚РµРѕСЂРёСЏ, РєРѕСЂРѕС‚РєР°СЏ РїСЂР°РєС‚РёРєР°, Р±РµР· РїРµСЂРµСЃРєРѕРєРѕРІ.",
        "tasks": [1, 2, 3, 4, 5],
        "min_attempts": 2,
        "min_accuracy": 60,
        "estimated_minutes": 90,
    },
    {
        "stage_number": 2,
        "kind": "revisit",
        "title": "Р’РѕР·РІСЂР°С‚ 1вЂ“5: СѓСЃР»РѕР¶РЅС‘РЅРЅРѕРµ Р·Р°РєСЂРµРїР»РµРЅРёРµ",
        "description": "Р’РѕР·РІСЂР°С‚ Рє РїРµСЂРІС‹Рј Р·Р°РґР°РЅРёСЏРј СЃ Р±РѕР»СЊС€РµР№ СЃР»РѕР¶РЅРѕСЃС‚СЊСЋ Рё РєРѕРЅС‚СЂРѕР»РµРј РѕС€РёР±РѕРє.",
        "tasks": [1, 2, 3, 4, 5],
        "min_attempts": 4,
        "min_accuracy": 72,
        "estimated_minutes": 80,
    },
    {
        "stage_number": 3,
        "kind": "learn",
        "title": "Р”Р°Р»СЊС€Рµ: Р·Р°РґР°РЅРёСЏ 6вЂ“10",
        "description": "Р’С‚РѕСЂРѕР№ Р±Р»РѕРє РЅРѕРІРѕРіРѕ РјР°С‚РµСЂРёР°Р»Р°.",
        "tasks": [6, 7, 8, 9, 10],
        "min_attempts": 2,
        "min_accuracy": 60,
        "estimated_minutes": 95,
    },
    {
        "stage_number": 4,
        "kind": "review",
        "title": "Weekly Review A",
        "description": "РћР±СЏР·Р°С‚РµР»СЊРЅС‹Р№ РєРѕРЅС‚СЂРѕР»СЊРЅС‹Р№ Р±Р»РѕРє РїРѕ Р·Р°РґР°РЅРёСЏРј 1вЂ“10.",
        "review_index": 1,
        "review_tasks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "estimated_minutes": 35,
    },
    {
        "stage_number": 5,
        "kind": "revisit",
        "title": "Р’РѕР·РІСЂР°С‚ 1вЂ“10: Р·Р°РєСЂРµРїР»РµРЅРёРµ Р±Р»РѕРєР°",
        "description": "РџРѕРІС‚РѕСЂРµРЅРёРµ РїСЂРѕР№РґРµРЅРЅРѕРіРѕ РґРѕ РїРµСЂРµС…РѕРґР° РІ СЃСЂРµРґРЅСЋСЋ С‡Р°СЃС‚СЊ РґРѕСЂРѕР¶РєРё.",
        "tasks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "min_attempts": 4,
        "min_accuracy": 70,
        "estimated_minutes": 90,
    },
    {
        "stage_number": 6,
        "kind": "learn",
        "title": "РЎСЂРµРґРЅРёР№ Р±Р»РѕРє: Р·Р°РґР°РЅРёСЏ 11вЂ“15",
        "description": "РћСЃРЅРѕРІРЅР°СЏ СЃРµСЂРµРґРёРЅР° РґРѕСЂРѕР¶РєРё, РІРєР»СЋС‡Р°СЏ РєРѕРґРѕРІС‹Рµ Р·Р°РґР°РЅРёСЏ.",
        "tasks": [11, 12, 13, 14, 15],
        "min_attempts": 2,
        "min_accuracy": 60,
        "estimated_minutes": 110,
    },
    {
        "stage_number": 7,
        "kind": "review",
        "title": "Weekly Review B",
        "description": "РљРѕРЅС‚СЂРѕР»СЊ Рё РІРѕР·РІСЂР°С‚ РїРѕ Р·Р°РґР°РЅРёСЏРј 6вЂ“15.",
        "review_index": 2,
        "review_tasks": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "estimated_minutes": 40,
    },
    {
        "stage_number": 8,
        "kind": "revisit",
        "title": "Р’РѕР·РІСЂР°С‚ 6вЂ“15: СЃР»РѕР¶РЅРµРµ Рё С‚РѕС‡РЅРµРµ",
        "description": "РџРѕРІС‚РѕСЂРµРЅРёРµ СЃ СѓРїРѕСЂРѕРј РЅР° СЃР»Р°Р±С‹Рµ С‚РµРјС‹ Рё С‚СЂСѓРґРЅС‹Рµ СѓРїСЂР°Р¶РЅРµРЅРёСЏ.",
        "tasks": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "min_attempts": 4,
        "min_accuracy": 72,
        "estimated_minutes": 95,
    },
    {
        "stage_number": 9,
        "kind": "learn",
        "title": "РЎС‚Р°СЂС€РёР№ Р±Р»РѕРє: Р·Р°РґР°РЅРёСЏ 16вЂ“20",
        "description": "РџСЂРѕРґРІРёРЅСѓС‚Р°СЏ С‡Р°СЃС‚СЊ СЃ РІС‹СЃРѕРєРѕР№ С†РµРЅРѕР№ РѕС€РёР±РѕРє.",
        "tasks": [16, 17, 18, 19, 20],
        "min_attempts": 2,
        "min_accuracy": 60,
        "estimated_minutes": 110,
    },
    {
        "stage_number": 10,
        "kind": "review",
        "title": "Weekly Review C",
        "description": "РљРѕРЅС‚СЂРѕР»СЊ РїРѕ Р·Р°РґР°РЅРёСЏРј 11вЂ“20.",
        "review_index": 3,
        "review_tasks": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        "estimated_minutes": 40,
    },
    {
        "stage_number": 11,
        "kind": "revisit",
        "title": "Р’РѕР·РІСЂР°С‚ 11вЂ“20: СЂР°Р±РѕС‚Р° РЅР°Рґ РѕС€РёР±РєР°РјРё",
        "description": "РЈСЃР»РѕР¶РЅС‘РЅРЅРѕРµ РїРѕРІС‚РѕСЂРµРЅРёРµ РїРµСЂРµРґ С„РёРЅР°Р»СЊРЅС‹Рј Р±Р»РѕРєРѕРј.",
        "tasks": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        "min_attempts": 4,
        "min_accuracy": 74,
        "estimated_minutes": 100,
    },
    {
        "stage_number": 12,
        "kind": "learn",
        "title": "Р¤РёРЅРёС€: Р·Р°РґР°РЅРёСЏ 21вЂ“27",
        "description": "РџРѕСЃР»РµРґРЅРёР№ РЅРѕРІС‹Р№ РјР°С‚РµСЂРёР°Р» РїРµСЂРµРґ СЃС‚Р°Р±РёР»РёР·Р°С†РёРµР№ Рё РїСЂРѕР±РЅРёРєР°РјРё.",
        "tasks": [21, 22, 23, 24, 25, 26, 27],
        "min_attempts": 2,
        "min_accuracy": 60,
        "estimated_minutes": 140,
    },
    {
        "stage_number": 13,
        "kind": "review",
        "title": "Weekly Review D",
        "description": "РћР±СЏР·Р°С‚РµР»СЊРЅС‹Р№ РєРѕРЅС‚СЂРѕР»СЊ РїРѕ Р·Р°РІРµСЂС€Р°СЋС‰РµРјСѓ Р±Р»РѕРєСѓ.",
        "review_index": 4,
        "review_tasks": [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
        "estimated_minutes": 45,
    },
    {
        "stage_number": 14,
        "kind": "revisit",
        "title": "Р¤РёРЅР°Р»СЊРЅРѕРµ Р·Р°РєСЂРµРїР»РµРЅРёРµ 16вЂ“27",
        "description": "РџРѕСЃР»РµРґРЅРёР№ РІРѕР·РІСЂР°С‚ РЅР°Р·Р°Рґ РїРµСЂРµРґ РїРѕР»РЅРѕС†РµРЅРЅС‹РјРё РїСЂРѕР±РЅРёРєР°РјРё.",
        "tasks": [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
        "min_attempts": 4,
        "min_accuracy": 76,
        "estimated_minutes": 120,
    },
    {
        "stage_number": 15,
        "kind": "mock",
        "title": "РџСЂРѕР±РЅРёРєРё Рё СЃС‚Р°Р±РёР»РёР·Р°С†РёСЏ",
        "description": "Р¤РѕСЂРјР°С‚, С‚Р°Р№РјРёРЅРі Рё РґРѕРІРѕРґРєР° СЃР»Р°Р±С‹С… РјРµСЃС‚.",
        "min_mock_exams": 1,
        "estimated_minutes": 235,
    },
]

TRAINING_MOCK_TASKS = [2, 5, 6, 8, 12, 14, 16, 17, 19, 23, 25, 27]

GENERAL_THEORY = {
    "title": "Общая стратегия ЕГЭ",
    "subtitle": "Как распределять время, порядок номеров и базовые Python-паттерны.",
    "short_theory": """## Общая теория: быстрый ориентир

- Сначала закрывайте базовые и средние номера, чтобы набрать устойчивые баллы.
- Для кодовых заданий начинайте с черновика: вход, проверка формата, затем основной алгоритм.
- После каждой ошибки фиксируйте причину: логика, формат ответа, граничный случай.
- В пробнике проверяйте ответы после полного прохода, как на реальном экзамене.
""",
    "full_theory": """## Общая теория подготовки к ЕГЭ

### 1. Порядок решения
- Первый проход: берите задания, где вероятность ошибки минимальна.
- Второй проход: средние задания с расчётом времени.
- Третий проход: сложные и ресурсные задачи.

### 2. Работа с ошибками
- Делите ошибки на типы: невнимательность, пробел в теме, неверный алгоритм.
- Повторяйте похожие задания, но не дословные копии.
- Проверяйте граничные случаи до отправки ответа.

### 3. Python без перегруза
- На старте достаточно базиса: `if`, `for`, функции, строки, списки.
- В кодовых номерах важнее корректный результат, чем «красивый» стиль.
- После стабилизации добавляйте оптимизации и более короткие конструкции.

### 4. Экзаменационный режим
- В пробнике отключайте обучающие элементы и решайте в тайминге экзамена.
- После завершения разбирайте только слабые места по отчёту.
""",
}


class ProfileCreate(BaseModel):
    name: str = "РЈС‡РµРЅРёРє"
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
    attempt_count: Optional[int] = None


class CodeRun(BaseModel):
    code: str
    stdin: str = ""
    stdin_path: Optional[str] = None


class CodeCheck(BaseModel):
    exercise_id: str
    code: str
    attempt_count: Optional[int] = None


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


class BaselineUpdate(BaseModel):
    python_level: str = "beginner"
    ege_level: str = "start"
    weekly_goal_hours: float = 6.0
    note: str = ""


class TaskBankCheck(BaseModel):
    exercise_id: str
    answer: Any = None
    code: Optional[str] = None
    attempt_count: Optional[int] = None


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


def load_static_content() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    try:
        from .content_data import THEORY_DATA, EXERCISES_DATA, ROADMAP_DATA, CONTENT_REGISTRY
    except ImportError:
        from content_data import THEORY_DATA, EXERCISES_DATA, ROADMAP_DATA, CONTENT_REGISTRY
    return THEORY_DATA, EXERCISES_DATA, ROADMAP_DATA, CONTENT_REGISTRY


async def ensure_storage_seeded(force: bool = False) -> dict[str, Any]:
    theory_data, exercises_data, roadmap_data, _ = load_static_content()
    return storage.seed_static_content(theory_data, exercises_data, roadmap_data, force=force)


def get_content_registry() -> dict[str, Any]:
    _, _, _, registry = load_static_content()
    return registry


def run_python_code(source_code: str, stdin_text: str = "") -> dict[str, Any]:
    sandbox_files_dir = PROJECT_ROOT / "content"
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
                cwd=str(sandbox_files_dir) if sandbox_files_dir.exists() else None,
            )
            return {
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "returncode": completed.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "РџСЂРµРІС‹С€РµРЅРѕ РІСЂРµРјСЏ РІС‹РїРѕР»РЅРµРЅРёСЏ (timeout 5 СЃРµРє).",
                "returncode": -1,
            }


def resolve_content_file_input(path_value: str) -> Optional[str]:
    candidate = resolve_content_file_path(path_value)
    if not candidate:
        return None
    try:
        return candidate.read_text(encoding="utf-8")
    except Exception:
        return None


def resolve_content_file_path(path_value: str) -> Optional[Path]:
    raw = str(path_value or "").strip().replace("\\", "/")
    if not raw:
        return None
    content_root = (PROJECT_ROOT / "content").resolve()
    candidate = (content_root / raw).resolve()
    if content_root not in candidate.parents and candidate != content_root:
        return None
    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate


def get_profile_core() -> dict[str, Any]:
    profile = storage.get_profile()
    if profile:
        baseline = profile.get("baseline") if isinstance(profile.get("baseline"), dict) else {}
        baseline.setdefault("completed", False)
        baseline.setdefault("python_level", "beginner")
        baseline.setdefault("ege_level", "start")
        baseline.setdefault("weekly_goal_hours", float(profile.get("weekly_hours", 10.0) or 10.0))
        baseline.setdefault("note", "")
        profile["baseline"] = baseline
        return profile
    profile = {
        "name": "РЈС‡РµРЅРёРє",
        "target_score": 80,
        "exam_date": "2026-06-01",
        "confidence_level": "medium",
        "daily_hours": 2.0,
        "weekly_hours": 10.0,
        "font_size": 14,
        "learning_mode": "guided",
        "total_exercises_done": 0,
        "total_correct": 0,
        "baseline": {
            "completed": False,
            "python_level": "beginner",
            "ege_level": "start",
            "weekly_goal_hours": 6.0,
            "note": "",
        },
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    storage.save_profile(profile)
    return profile


def get_profile_payload() -> dict[str, Any]:
    profile = get_profile_core().copy()
    baseline = profile.get("baseline") if isinstance(profile.get("baseline"), dict) else {}
    profile["baseline_completed"] = bool(baseline.get("completed"))
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
        raise HTTPException(404, "РўРµРѕСЂРёСЏ РЅРµ РЅР°Р№РґРµРЅР°")
    return item


def get_exercise_or_404(exercise_id: str) -> dict[str, Any]:
    exercise = storage.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(404, "РЈРїСЂР°Р¶РЅРµРЅРёРµ РЅРµ РЅР°Р№РґРµРЅРѕ")
    return normalize_exercise_contract(exercise)


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

    exercises = [normalize_exercise_contract(item) for item in storage.list_exercises(task_number=task_number, only_objective=True)]
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


def choose_random_exercise_for_task(
    task_number: int,
    *,
    prefer_prototype: bool = False,
    only_objective: bool = True,
) -> Optional[dict[str, Any]]:
    pool = [normalize_exercise_contract(item) for item in storage.list_exercises(task_number=task_number, only_objective=only_objective)]
    if not pool:
        return None

    if prefer_prototype:
        prototype_pool = [item for item in pool if item.get("exercise_mode") == "prototype"]
        if prototype_pool:
            pool = prototype_pool

    return random.choice(pool)


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


def get_exercise_explanation(exercise: dict[str, Any]) -> str:
    return str(exercise.get("full_explanation") or exercise.get("explanation") or "")


def normalize_exercise_contract(exercise: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(exercise)
    source = str(normalized.get("source", "")).strip().lower()
    normalized["source"] = source if source in {"fipi", "reshu", "author", "mixed"} else "mixed"
    normalized["source_visibility"] = str(normalized.get("source_visibility", "subtle")).strip() or "subtle"

    difficulty_stage = str(normalized.get("difficulty_stage", "")).strip().lower()
    if difficulty_stage not in {"basic", "medium", "exam", "exam_plus"}:
        difficulty = str(normalized.get("difficulty", "")).strip().lower()
        if difficulty == "easy":
            difficulty_stage = "basic"
        elif difficulty == "hard":
            difficulty_stage = "exam"
        else:
            difficulty_stage = "medium"
    normalized["difficulty_stage"] = difficulty_stage

    mode = str(normalized.get("exercise_mode", "")).strip().lower()
    if mode not in {"training", "prototype"}:
        mode = "prototype" if difficulty_stage in {"exam", "exam_plus"} else "training"
    normalized["exercise_mode"] = mode

    raw_hints = normalized.get("hints") or []
    hints = [str(item).strip() for item in raw_hints if str(item).strip()]
    if not hints and normalized.get("hint_after_first_error"):
        hints.append(str(normalized["hint_after_first_error"]).strip())
    if len(hints) == 0:
        hints = [
            "РЎРЅР°С‡Р°Р»Р° РІС‹РґРµР»РёС‚Рµ РґР°РЅРЅС‹Рµ РёР· СѓСЃР»РѕРІРёСЏ Рё РѕР¶РёРґР°РµРјС‹Р№ С„РѕСЂРјР°С‚ РѕС‚РІРµС‚Р°.",
            "РџСЂРѕРІРµСЂСЊС‚Рµ РїСЂРѕРјРµР¶СѓС‚РѕС‡РЅС‹Р№ С€Р°Рі СЂРµС€РµРЅРёСЏ РЅР° РєРѕСЂРѕС‚РєРѕРј РїСЂРёРјРµСЂРµ.",
            "РЎРІРµСЂСЊС‚Рµ РёС‚РѕРі СЃ РїРѕР»РЅС‹Рј СЂР°Р·Р±РѕСЂРѕРј Рё РёСЃРїСЂР°РІСЊС‚Рµ РјРµСЃС‚Рѕ, РіРґРµ Р»РѕРјР°РµС‚СЃСЏ Р»РѕРіРёРєР°.",
        ]
    if len(hints) == 1:
        hints.append("РџСЂРѕРІРµСЂСЊС‚Рµ РіСЂР°РЅРёС‡РЅС‹Рµ СЃР»СѓС‡Р°Рё Рё С„РѕСЂРјР°С‚ РІС‹РІРѕРґР°.")
    if len(hints) == 2:
        hints.append("Р•СЃР»Рё РЅРµ СЃС…РѕРґРёС‚СЃСЏ, РїРѕРІС‚РѕСЂРёС‚Рµ СЂРµС€РµРЅРёРµ РїРѕ С€Р°РіР°Рј РёР· РїРѕР»РЅРѕРіРѕ СЂР°Р·Р±РѕСЂР°.")
    normalized["hints"] = hints[:3]
    normalized["hint_after_first_error"] = normalized["hints"][0]

    attempt_policy = normalized.get("attempt_policy") if isinstance(normalized.get("attempt_policy"), dict) else {}
    normalized["attempt_policy"] = {
        "max_wrong_before_solution": int(attempt_policy.get("max_wrong_before_solution", 3)),
        "auto_retry_in_lesson_end": bool(attempt_policy.get("auto_retry_in_lesson_end", True)),
    }

    if normalized.get("exercise_type") == "code":
        code_step = str(normalized.get("code_step", "")).strip().lower()
        if code_step not in {"fragments", "fill_gaps", "full_code"}:
            if difficulty_stage == "basic":
                code_step = "fragments"
            elif difficulty_stage == "medium":
                code_step = "fill_gaps"
            else:
                code_step = "full_code"
        normalized["code_step"] = code_step
        normalized["evaluation"] = "tests"
        normalized["acceptance"] = str(normalized.get("acceptance", "output_first")).strip() or "output_first"
    else:
        normalized.setdefault("evaluation", "answer")
        normalized.setdefault("acceptance", "exact_match")
    return normalized


def build_attempt_feedback(exercise: dict[str, Any], *, correct: bool, attempt_count: Optional[int]) -> dict[str, Any]:
    normalized = normalize_exercise_contract(exercise)
    policy = normalized["attempt_policy"]
    max_wrong = max(1, int(policy.get("max_wrong_before_solution", 3)))
    current_attempt = max(1, safe_int(attempt_count, 1))

    if correct:
        return {
            "attempt_policy": policy,
            "wrong_attempts": max(0, current_attempt - 1),
            "hint_level": 0,
            "hints_shown": [],
            "hint": None,
            "reveal_solution": False,
            "should_retry_in_lesson_end": False,
        }

    wrong_attempts = current_attempt
    hint_level = min(wrong_attempts, len(normalized.get("hints", [])))
    hints_shown = normalized.get("hints", [])[:hint_level]
    reveal_solution = wrong_attempts >= max_wrong
    return {
        "attempt_policy": policy,
        "wrong_attempts": wrong_attempts,
        "hint_level": hint_level,
        "hints_shown": hints_shown,
        "hint": hints_shown[-1] if hints_shown else None,
        "reveal_solution": reveal_solution,
        "should_retry_in_lesson_end": bool(reveal_solution and policy.get("auto_retry_in_lesson_end")),
    }


def normalize_code_tests(exercise: dict[str, Any]) -> list[dict[str, Any]]:
    raw_tests = []
    if isinstance(exercise.get("tests_open"), list) or isinstance(exercise.get("tests_hidden"), list):
        raw_tests.extend(exercise.get("tests_open") or [])
        raw_tests.extend(exercise.get("tests_hidden") or [])
    if not raw_tests:
        raw_tests = exercise.get("tests") or exercise.get("test_cases") or []
    normalized: list[dict[str, Any]] = []
    for test in raw_tests:
        if not isinstance(test, dict):
            continue
        output = test.get("output", test.get("expected_output", ""))
        normalized.append(
            {
                "input": str(test.get("input", "")),
                "output": str(output),
                "is_public": bool(test.get("is_public", True)),
            }
        )
    return normalized


def find_missing_required_nodes(source_code: str, required_nodes: list[str]) -> tuple[list[str], Optional[str]]:
    if not required_nodes:
        return [], None

    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        return required_nodes, f"Syntax error: {exc.msg} (line {exc.lineno})"

    node_map: dict[str, Any] = {
        "for": ast.For,
        "while": ast.While,
        "if": ast.If,
        "listcomp": ast.ListComp,
        "dictcomp": ast.DictComp,
        "setcomp": ast.SetComp,
        "generator": ast.GeneratorExp,
        "function": ast.FunctionDef,
    }

    missing: list[str] = []
    walk_nodes = list(ast.walk(tree))
    functions = [node for node in walk_nodes if isinstance(node, ast.FunctionDef)]

    for raw_name in required_nodes:
        name = str(raw_name).strip().lower()
        if not name:
            continue

        if name == "recursion":
            has_recursion = False
            for fn in functions:
                for node in ast.walk(fn):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == fn.name:
                        has_recursion = True
                        break
                if has_recursion:
                    break
            if not has_recursion:
                missing.append(str(raw_name))
            continue

        node_type = node_map.get(name)
        if node_type is None:
            continue
        if not any(isinstance(node, node_type) for node in walk_nodes):
            missing.append(str(raw_name))

    return missing, None


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
    exercise = normalize_exercise_contract(exercise)
    tests = normalize_code_tests(exercise)
    explanation = get_exercise_explanation(exercise)
    hint = (exercise.get("hints") or [None])[0]

    required_nodes_raw = exercise.get("required_nodes") or exercise.get("required_constructs") or []
    required_nodes = [str(node) for node in required_nodes_raw if str(node).strip()]
    missing_nodes, syntax_error = find_missing_required_nodes(source_code, required_nodes)
    if syntax_error:
        return {
            "correct": False,
            "message": "Code check failed",
            "details": syntax_error,
            "test_results": [],
            "hint": hint,
            "explanation": explanation,
        }
    if missing_nodes:
        return {
            "correct": False,
            "message": "Code did not pass structure validation",
            "details": f"Missing required constructs: {', '.join(missing_nodes)}",
            "test_results": [],
            "hint": hint,
            "explanation": explanation,
        }

    if not tests:
        return {
            "correct": False,
            "message": "No tests configured for this exercise yet.",
            "details": "Automatic code validation is unavailable for this item.",
            "test_results": [],
            "hint": hint,
            "explanation": explanation,
        }

    failures: list[str] = []
    test_results: list[dict[str, Any]] = []
    all_passed = True

    for index, test in enumerate(tests, start=1):
        run_result = run_python_code(source_code, test.get("input", ""))
        actual_output = (run_result.get("stdout") or "").strip()
        expected_output = (test.get("output", "") or "").strip()

        if run_result.get("returncode") != 0:
            all_passed = False
            failures.append(f"Test {index}: runtime error.")
            test_results.append(
                {
                    "test_number": index,
                    "passed": False,
                    "expected": expected_output,
                    "actual": run_result.get("stderr", "").strip(),
                    "is_public": bool(test.get("is_public", True)),
                }
            )
            continue

        passed = actual_output == expected_output
        if not passed:
            all_passed = False
            failures.append(f"Test {index}: expected {expected_output!r}, got {actual_output!r}")
        test_results.append(
            {
                "test_number": index,
                "passed": passed,
                "expected": expected_output,
                "actual": actual_output,
                "is_public": bool(test.get("is_public", True)),
            }
        )

    public_results = [item for item in test_results if item.get("is_public", True)]

    return {
        "correct": all_passed,
        "message": "Code passed" if all_passed else "Code check failed",
        "details": "\n".join(failures),
        "test_results": public_results,
        "all_test_results": test_results,
        "hint": None if all_passed else hint,
        "explanation": explanation,
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
                "title": theory.get("title", f"Р—Р°РґР°РЅРёРµ {task_number}"),
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
            "РџСЂРѕРіРЅРѕР· РѕСЃРЅРѕРІР°РЅ РЅР° РїРѕРєСЂС‹С‚РёРё С‚РµРј, С‚РѕС‡РЅРѕСЃС‚Рё Рё Р·Р°РІРµСЂС€С‘РЅРЅС‹С… РїСЂРѕР±РЅРёРєР°С…."
            if started_tasks
            else "РќСѓР¶РЅС‹ РїРµСЂРІС‹Рµ СЂРµС€С‘РЅРЅС‹Рµ Р·Р°РґР°РЅРёСЏ, С‡С‚РѕР±С‹ СЃС‚СЂРѕРёС‚СЊ РїСЂРѕРіРЅРѕР·."
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
                "title": "РЎРЅР°С‡Р°Р»Р° РѕР±СЏР·Р°С‚РµР»СЊРЅС‹Р№ Weekly Review",
                "description": "Р”РѕСЂРѕР¶РєР° РѕСЃС‚Р°РЅРѕРІР»РµРЅР° РґРѕ РїСЂРѕС…РѕР¶РґРµРЅРёСЏ РєРѕРЅС‚СЂРѕР»СЊРЅРѕРіРѕ Р±Р»РѕРєР°.",
                "minutes": current_stage.get("estimated_minutes", 35),
                "href": "/weekly-review",
                "action_label": "РћС‚РєСЂС‹С‚СЊ Weekly Review",
            }
        )
    elif current_stage.get("kind") in {"learn", "revisit"}:
        for task_number in current_stage.get("tasks", [])[:3]:
            task_data = progress_metrics["task_map"].get(task_number, {})
            if task_data.get("total_attempts", 0) == 0:
                items.append(
                    {
                        "type": "theory",
                        "title": f"РљСЂР°С‚РєРѕ РїСЂРѕР№С‚Рё С‚РµРѕСЂРёСЋ РїРѕ Р·Р°РґР°РЅРёСЋ {task_number}",
                        "description": "РћС‚РєСЂС‹С‚СЊ РєСЂР°С‚РєСѓСЋ Рё РїРѕР»РЅСѓСЋ С‚РµРѕСЂРёСЋ, Р·Р°С‚РµРј РїРµСЂРµР№С‚Рё Рє РїСЂР°РєС‚РёРєРµ.",
                        "minutes": 15,
                        "href": f"/theory?task={task_number}",
                        "action_label": "Рљ С‚РµРѕСЂРёРё",
                    }
                )
                items.append(
                    {
                        "type": "practice",
                        "title": f"Р РµС€Р°С‚СЊ Р·Р°РґР°РЅРёРµ {task_number} РІ guided mode",
                        "description": "РќР°Р±РµСЂРёС‚Рµ РїРµСЂРІС‹Рµ РїРѕРїС‹С‚РєРё РїРѕ С‚РµРєСѓС‰РµРјСѓ СЌС‚Р°РїСѓ.",
                        "minutes": 20,
                        "href": f"/practice?task={task_number}&mode=guided",
                        "action_label": "Рљ РїСЂР°РєС‚РёРєРµ",
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
                    "title": f"Р”РѕР±СЂР°С‚СЊ С‚РѕС‡РЅРѕСЃС‚СЊ РїРѕ Р·Р°РґР°РЅРёСЋ {weakest_inside_stage.get('task_number')}",
                    "description": "Р­С‚Рѕ Р·Р°РґР°РЅРёРµ СЃРёР»СЊРЅРµРµ РІСЃРµРіРѕ С‚РѕСЂРјРѕР·РёС‚ РїРµСЂРµС…РѕРґ Рє СЃР»РµРґСѓСЋС‰РµРјСѓ СЌС‚Р°РїСѓ.",
                    "minutes": 25,
                    "href": f"/practice?task={weakest_inside_stage.get('task_number')}&mode=guided",
                    "action_label": "РћС‚РєСЂС‹С‚СЊ guided practice",
                }
            )
    else:
        items.append(
            {
                "type": "mock",
                "title": "РџРµСЂРµР№С‚Рё Рє РїСЂРѕР±РЅРёРєСѓ",
                "description": "Guided path РґРѕРІРµРґС‘РЅ РґРѕ СЂРµР¶РёРјР° СЃС‚Р°Р±РёР»РёР·Р°С†РёРё.",
                "minutes": 120,
                "href": "/mock-exam",
                "action_label": "РћС‚РєСЂС‹С‚СЊ РїСЂРѕР±РЅРёРє",
            }
        )

    if weak_details:
        task_number = weak_details[0]["task_number"]
        items.append(
            {
                "type": "weak",
                "title": f"Р’РµСЂРЅСѓС‚СЊСЃСЏ Рє СЃР»Р°Р±РѕР№ С‚РµРјРµ в„–{task_number}",
                "description": weak_details[0]["reason"],
                "minutes": 20,
                "href": f"/practice?task={task_number}&mode=weak",
                "action_label": "РЎР»Р°Р±С‹Рµ С‚РµРјС‹",
            }
        )

    if progress_metrics["mistake_tasks"]:
        task_number = progress_metrics["mistake_tasks"][0]
        items.append(
            {
                "type": "mistakes",
                "title": f"Р Р°Р·РѕР±СЂР°С‚СЊ РЅРµРґР°РІРЅРёРµ РѕС€РёР±РєРё РїРѕ в„–{task_number}",
                "description": "Р РµР¶РёРј РѕС€РёР±РѕРє РїРѕРєР°Р·С‹РІР°РµС‚ С‚РµРјС‹, РіРґРµ Р±С‹Р»Рё РїРѕСЃР»РµРґРЅРёРµ РїСЂРѕРјР°С…Рё.",
                "minutes": 15,
                "href": f"/practice?task={task_number}&mode=mistakes",
                "action_label": "Рљ РѕС€РёР±РєР°Рј",
            }
        )

    daily_hours = float(profile.get("daily_hours", 2) or 2)
    total_minutes = int(sum(item["minutes"] for item in items[:3]))
    return {
        "summary": "РџРѕРЅСЏС‚РЅС‹Р№ РїР»Р°РЅ РЅР° СЃРµРіРѕРґРЅСЏ Р±РµР· Р»РёС€РЅРµР№ РіРµР№РјРёС„РёРєР°С†РёРё.",
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
                    "РќРёР·РєР°СЏ С‚РѕС‡РЅРѕСЃС‚СЊ РїРѕСЃР»Рµ СЃРµСЂРёРё РїРѕРїС‹С‚РѕРє."
                    if item.get("accuracy", 0) < 60
                    else "Р—Р°РґР°РЅРёРµ СЂРµС€Р°РµС‚СЃСЏ РЅРµСЃС‚Р°Р±РёР»СЊРЅРѕ Рё С‚СЂРµР±СѓРµС‚ Р·Р°РєСЂРµРїР»РµРЅРёСЏ."
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
        "dashboard_title": "Р”Р°С€Р±РѕСЂРґ РїРѕРґРіРѕС‚РѕРІРєРё",
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
            {"label": "РЎРІРѕР±РѕРґРЅР°СЏ РїСЂР°РєС‚РёРєР°", "href": "/practice?mode=free"},
            {"label": "Guided path", "href": "/practice?mode=guided"},
            {"label": "Weekly Review", "href": "/weekly-review"},
            {"label": "РџСЂРѕР±РЅРёРє", "href": "/mock-exam"},
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
        "summary": "Weekly Review СЃРѕР±РёСЂР°РµС‚СЃСЏ РёР· С‚РµРєСѓС‰РµРіРѕ СЌС‚Р°РїР°, СЃР»Р°Р±С‹С… С‚РµРј Рё РЅРµРґР°РІРЅРёС… РѕС€РёР±РѕРє.",
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
    selection_mode = "prototype" if mode == "exam" else "training"
    exercise = choose_task_bank_exercise(task_number, mode=selection_mode)
    if not exercise:
        exercise = choose_random_exercise_for_task(task_number, prefer_prototype=(mode == "exam"))
    theory = storage.get_theory(task_number) or {}
    return {
        "task_number": task_number,
        "title": theory.get("title", f"Р—Р°РґР°РЅРёРµ {task_number}"),
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
                "label": "Р­РєР·Р°РјРµРЅР°С†РёРѕРЅРЅС‹Р№",
                "duration_minutes": 235,
                "tasks_count": 27,
                "description": "РњР°РєСЃРёРјР°Р»СЊРЅРѕ РїРѕС…РѕР¶Рµ РЅР° СЂРµР°Р»СЊРЅС‹Р№ СЌРєР·Р°РјРµРЅ.",
            },
            {
                "mode": "training",
                "label": "РўСЂРµРЅРёСЂРѕРІРѕС‡РЅС‹Р№",
                "duration_minutes": 120,
                "tasks_count": len(TRAINING_MOCK_TASKS),
                "description": "РЈРєРѕСЂРѕС‡РµРЅРЅС‹Р№ РїСЂРѕР±РЅРёРє СЃ Р°РєС†РµРЅС‚РѕРј РЅР° С‚СЂРµРЅРёСЂСѓРµРјС‹Рµ С‚РёРїС‹ Р·Р°РґР°С‡.",
            },
        ],
    }
    if active_exam:
        exam = active_exam.copy()
        exam["elapsed_seconds"] = mock_elapsed_seconds(exam)
        payload["exam"] = exam
    return payload


def build_task_bank_summary() -> dict[str, Any]:
    theory_items = storage.list_theory()
    attempts = storage.list_recent_task_bank_attempts(limit=2500)

    task_stats: dict[int, dict[str, Any]] = {}
    for theory in theory_items:
        task_number = int(theory.get("task_number", 0))
        task_stats[task_number] = {
            "task_number": task_number,
            "title": theory.get("title", f"Задание {task_number}"),
            "source": theory.get("source", "mixed"),
            "attempts": 0,
            "correct": 0,
            "accuracy": 0.0,
            "is_code_task": bool(theory.get("is_code_task") or task_number in CODE_TASKS),
        }

    for attempt in attempts:
        task_number = safe_int(attempt.get("task_number"), 0)
        row = task_stats.get(task_number)
        if not row:
            continue
        row["attempts"] += 1
        row["correct"] += 1 if attempt.get("correct") else 0

    for row in task_stats.values():
        row["accuracy"] = round((row["correct"] / row["attempts"]) * 100, 1) if row["attempts"] else 0.0

    items = sorted(task_stats.values(), key=lambda item: item["task_number"])
    total_attempts = sum(item["attempts"] for item in items)
    total_correct = sum(item["correct"] for item in items)
    overall_accuracy = round((total_correct / total_attempts) * 100, 1) if total_attempts else 0.0
    return {
        "tasks": items,
        "total_attempts": total_attempts,
        "total_correct": total_correct,
        "overall_accuracy": overall_accuracy,
    }


def choose_task_bank_exercise(task_number: int, mode: str = "any") -> Optional[dict[str, Any]]:
    normalized_mode = str(mode or "any").strip().lower()
    pool = [
        normalize_exercise_contract(item)
        for item in storage.list_exercises(task_number=task_number, only_objective=True)
    ]
    if not pool:
        return None

    if normalized_mode in {"training", "prototype"}:
        scoped_pool = [item for item in pool if item.get("exercise_mode") == normalized_mode]
        if scoped_pool:
            pool = scoped_pool
    elif normalized_mode == "exam":
        prototype_pool = [item for item in pool if item.get("exercise_mode") == "prototype"]
        if prototype_pool:
            pool = prototype_pool

    return random.choice(pool)


@app.get("/api/theory")
async def list_theory():
    return storage.list_theory()


@app.get("/api/theory/general")
async def get_general_theory():
    return GENERAL_THEORY


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


@app.get("/api/task-bank/summary")
async def get_task_bank_summary():
    return build_task_bank_summary()


@app.get("/api/task-bank/{task_number}/next")
async def get_task_bank_exercise(task_number: int, mode: str = "any"):
    exercise = choose_task_bank_exercise(task_number, mode=mode)
    if not exercise:
        raise HTTPException(404, "Для этого номера пока нет доступных заданий в банке.")
    return exercise


@app.post("/api/task-bank/check")
async def check_task_bank(payload: TaskBankCheck):
    exercise = get_exercise_or_404(payload.exercise_id)
    is_code = exercise.get("exercise_type") == "code"

    if is_code:
        if payload.code is None:
            raise HTTPException(400, "Для кодового задания передайте поле code.")
        result = evaluate_code_against_exercise(exercise, payload.code)
        correct = bool(result.get("correct"))
        extra_payload = {"submitted_code": payload.code}
    else:
        correct, expected_answer = evaluate_answer_against_exercise(exercise, payload.answer)
        result = {
            "correct": correct,
            "expected": expected_answer,
            "explanation": get_exercise_explanation(exercise),
        }
        extra_payload = {"submitted_answer": payload.answer, "correct_answer": expected_answer}

    feedback = build_attempt_feedback(exercise, correct=correct, attempt_count=payload.attempt_count)
    storage.add_task_bank_attempt(
        {
            "task_number": exercise["task_number"],
            "exercise_id": exercise["exercise_id"],
            "correct": correct,
            "timestamp": now_iso(),
            "source": exercise.get("source"),
            "mode": exercise.get("exercise_mode"),
            **extra_payload,
        }
    )

    result["source"] = exercise.get("source")
    result["source_visibility"] = exercise.get("source_visibility", "subtle")
    result.update(feedback)
    return result


@app.post("/api/check-answer")
async def check_answer(payload: AnswerCheck):
    exercise = get_exercise_or_404(payload.exercise_id)
    if exercise.get("exercise_type") == "code":
        raise HTTPException(400, "Р”Р»СЏ РєРѕРґРѕРІС‹С… Р·Р°РґР°С‡ РёСЃРїРѕР»СЊР·СѓР№С‚Рµ /api/check-code")

    correct, expected_answer = evaluate_answer_against_exercise(exercise, payload.answer)
    attempt_feedback = build_attempt_feedback(exercise, correct=correct, attempt_count=payload.attempt_count)
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
        "explanation": get_exercise_explanation(exercise),
        "source": exercise.get("source"),
        "source_visibility": exercise.get("source_visibility", "subtle"),
        **attempt_feedback,
    }


@app.post("/api/exercises/check")
async def check_answer_alias(payload: AnswerCheck):
    return await check_answer(payload)


@app.post("/api/run-code")
async def run_code(payload: CodeRun):
    stdin_text = payload.stdin or ""
    if payload.stdin_path:
        file_text = resolve_content_file_input(payload.stdin_path)
        if file_text is None:
            return {
                "stdout": "",
                "stderr": "Файл для входных данных не найден или недоступен.",
                "returncode": -1,
            }
        stdin_text = file_text
    return run_python_code(payload.code, stdin_text)


@app.post("/api/code/run")
async def run_code_alias(payload: CodeRun):
    return await run_code(payload)


@app.post("/api/check-code")
async def check_code(payload: CodeCheck):
    exercise = get_exercise_or_404(payload.exercise_id)
    result = evaluate_code_against_exercise(exercise, payload.code)
    attempt_feedback = build_attempt_feedback(exercise, correct=bool(result.get("correct")), attempt_count=payload.attempt_count)
    record_attempt(
        exercise["task_number"],
        exercise["exercise_id"],
        bool(result["correct"]),
        "practice_code",
        {
            "submitted_code": payload.code,
        },
    )
    result["source"] = exercise.get("source")
    result["source_visibility"] = exercise.get("source_visibility", "subtle")
    result.update(attempt_feedback)
    return result


@app.post("/api/code/check")
async def check_code_alias(payload: CodeCheck):
    return await check_code(payload)


@app.get("/api/profile")
async def get_profile():
    return get_profile_payload()


@app.get("/api/onboarding/baseline")
async def get_baseline():
    profile = get_profile_core()
    baseline = profile.get("baseline") if isinstance(profile.get("baseline"), dict) else {}
    return {
        "completed": bool(baseline.get("completed")),
        "python_level": baseline.get("python_level", "beginner"),
        "ege_level": baseline.get("ege_level", "start"),
        "weekly_goal_hours": float(baseline.get("weekly_goal_hours", profile.get("weekly_hours", 10.0) or 10.0)),
        "note": baseline.get("note", ""),
    }


@app.put("/api/onboarding/baseline")
async def save_baseline(payload: BaselineUpdate):
    profile = get_profile_core()
    profile["baseline"] = {
        "completed": True,
        "python_level": str(payload.python_level or "beginner"),
        "ege_level": str(payload.ege_level or "start"),
        "weekly_goal_hours": float(payload.weekly_goal_hours or 6.0),
        "note": str(payload.note or ""),
        "updated_at": now_iso(),
    }
    if payload.weekly_goal_hours and payload.weekly_goal_hours > 0:
        profile["weekly_hours"] = float(payload.weekly_goal_hours)
    save_profile(profile)
    return {"status": "ok", "baseline": profile["baseline"]}


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
        raise HTTPException(404, "РџСЂРѕРіСЂРµСЃСЃ РїРѕ Р·Р°РґР°РЅРёСЋ РЅРµ РЅР°Р№РґРµРЅ")
    return task


@app.get("/api/attempts/{task_number}")
async def get_attempts(task_number: int, limit: int = 20):
    return storage.list_attempts(task_number, limit=limit)


@app.get("/api/attempts/exercise/{exercise_id}")
async def get_attempts_by_exercise(exercise_id: str, limit: int = 20):
    return storage.list_attempts_by_exercise(exercise_id, limit=limit)


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
        raise HTTPException(400, "РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕР±СЂР°С‚СЊ Weekly Review: РЅРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ РѕР±СЉРµРєС‚РёРІРЅС‹С… Р·Р°РґР°РЅРёР№.")

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
        raise HTTPException(404, "РђРєС‚РёРІРЅС‹Р№ Weekly Review РЅРµ РЅР°Р№РґРµРЅ")

    exercise = next((item for item in review.get("exercises", []) if item.get("exercise_id") == payload.exercise_id), None)
    if not exercise:
        raise HTTPException(404, "Р—Р°РґР°РЅРёРµ РЅРµ РЅР°Р№РґРµРЅРѕ РІ Р°РєС‚РёРІРЅРѕРј Weekly Review")

    if exercise.get("exercise_type") == "code":
        raise HTTPException(400, "Weekly Review РїСЂРёРЅРёРјР°РµС‚ С‚РѕР»СЊРєРѕ РѕР±СЉРµРєС‚РёРІРЅС‹Рµ РѕС‚РІРµС‚С‹.")

    correct, expected_answer = evaluate_answer_against_exercise(exercise, payload.answer)
    review.setdefault("answers", {})[payload.exercise_id] = payload.answer
    review.setdefault("results", {})[payload.exercise_id] = {
        "correct": correct,
        "expected": expected_answer,
        "explanation": get_exercise_explanation(exercise),
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
        raise HTTPException(404, "РђРєС‚РёРІРЅС‹Р№ Weekly Review РЅРµ РЅР°Р№РґРµРЅ")

    total = len(review.get("exercises", []))
    answers_count = safe_int(review.get("answers_count"), 0)
    if total == 0:
        raise HTTPException(400, "Weekly Review РїСѓСЃС‚.")
    if answers_count < max(3, total - 1):
        raise HTTPException(400, "РќСѓР¶РЅРѕ РѕС‚РІРµС‚РёС‚СЊ РїРѕС‡С‚Рё РЅР° РІСЃРµ Р·Р°РґР°РЅРёСЏ review, РїСЂРµР¶РґРµ С‡РµРј Р·Р°РІРµСЂС€Р°С‚СЊ.")

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
        raise HTTPException(404, "РџСЂРѕР±РЅРёРє РЅРµ РЅР°Р№РґРµРЅ")
    if exam.get("status") == "completed":
        raise HTTPException(400, "РџСЂРѕР±РЅРёРє СѓР¶Рµ Р·Р°РІРµСЂС€С‘РЅ")

    updated = False
    for task in exam.get("tasks", []):
        if task["task_number"] == payload.task_number:
            task["answer"] = payload.answer
            task["code"] = payload.code
            task["status"] = "answered" if (payload.answer not in {None, ""} or payload.code) else "pending"
            updated = True
            break
    if not updated:
        raise HTTPException(404, "Р—Р°РґР°РЅРёРµ РЅРµ РЅР°Р№РґРµРЅРѕ РІ РїСЂРѕР±РЅРёРєРµ")

    storage.save_mock_exam(exam)
    return {"status": "ok"}


@app.put("/api/mock-exam/{exam_id}/flag")
async def flag_mock_exam_task(exam_id: str, payload: MockExamAnswer):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "РџСЂРѕР±РЅРёРє РЅРµ РЅР°Р№РґРµРЅ")

    for task in exam.get("tasks", []):
        if task["task_number"] == payload.task_number:
            task["flagged"] = not task.get("flagged", False)
            storage.save_mock_exam(exam)
            return {"status": "ok", "flagged": task["flagged"]}
    raise HTTPException(404, "Р—Р°РґР°РЅРёРµ РЅРµ РЅР°Р№РґРµРЅРѕ")


@app.put("/api/mock-exam/{exam_id}/flag/{task_number}")
async def flag_mock_exam_task_compat(exam_id: str, task_number: int):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "РџСЂРѕР±РЅРёРє РЅРµ РЅР°Р№РґРµРЅ")

    for task in exam.get("tasks", []):
        if task["task_number"] == task_number:
            task["flagged"] = not task.get("flagged", False)
            storage.save_mock_exam(exam)
            return {"status": "ok", "flagged": task["flagged"]}
    raise HTTPException(404, "Р—Р°РґР°РЅРёРµ РЅРµ РЅР°Р№РґРµРЅРѕ")


@app.post("/api/mock-exam/{exam_id}/pause")
async def pause_mock_exam(exam_id: str):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "РџСЂРѕР±РЅРёРє РЅРµ РЅР°Р№РґРµРЅ")
    if exam.get("status") == "paused":
        return {"status": "ok"}
    if exam.get("status") == "completed":
        raise HTTPException(400, "РџСЂРѕР±РЅРёРє СѓР¶Рµ Р·Р°РІРµСЂС€С‘РЅ")

    exam["elapsed_seconds"] = mock_elapsed_seconds(exam)
    exam["paused_at"] = now_iso()
    exam["status"] = "paused"
    storage.save_mock_exam(exam)
    return {"status": "ok", "elapsed_seconds": exam["elapsed_seconds"]}


@app.post("/api/mock-exam/{exam_id}/resume")
async def resume_mock_exam(exam_id: str):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "РџСЂРѕР±РЅРёРє РЅРµ РЅР°Р№РґРµРЅ")
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
        raise HTTPException(404, "РџСЂРѕР±РЅРёРє РЅРµ РЅР°Р№РґРµРЅ")
    if exam.get("status") == "completed":
        return exam

    results = []
    weak_tasks: list[dict[str, Any]] = []
    correct_count = 0

    for task in exam.get("tasks", []):
        exercise = task.get("exercise")
        task_number = task.get("task_number")
        if not exercise:
            weak_tasks.append(
                {
                    "task_number": task_number,
                    "reason": "exercise_missing",
                    "theory_link": f"/theory?task={task_number}",
                    "practice_link": f"/practice?task={task_number}&mode=weak",
                }
            )
            results.append(
                {
                    "task_number": task_number,
                    "correct": False,
                    "explanation": "Р”Р»СЏ СЌС‚РѕРіРѕ Р·Р°РґР°РЅРёСЏ РЅРµ РЅР°Р№РґРµРЅРѕ СѓРїСЂР°Р¶РЅРµРЅРёРµ РІ Р»РѕРєР°Р»СЊРЅРѕР№ Р±Р°Р·Рµ.",
                    "theory_link": f"/theory?task={task_number}",
                    "practice_link": f"/practice?task={task_number}&mode=weak",
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
                "explanation": get_exercise_explanation(exercise),
            }

        correct_count += 1 if correct else 0
        if not correct:
            weak_tasks.append(
                {
                    "task_number": task_number,
                    "reason": "incorrect_answer",
                    "theory_link": f"/theory?task={task_number}",
                    "practice_link": f"/practice?task={task_number}&mode=weak",
                }
            )
        results.append(
            {
                "task_number": task_number,
                "correct": correct,
                "explanation": evaluation.get("explanation", ""),
                "details": evaluation.get("details", ""),
                "theory_link": f"/theory?task={task_number}",
                "practice_link": f"/practice?task={task_number}&mode={'weak' if not correct else 'free'}",
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
        "weak_tasks": weak_tasks,
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
    registry = get_content_registry()
    return {
        "status": "ok",
        "timestamp": now_iso(),
        "storage": "sqlite",
        "db_path": str(storage.db_path),
        "serving_frontend_build": SERVE_FRONTEND_BUILD,
        "frontend_build_exists": build_index_exists,
        "content_registry_ok": registry.get("ok", True),
        "content_registry_missing": registry.get("missing", 0),
    }


@app.get("/api/content/registry")
async def content_registry():
    return get_content_registry()


@app.get("/api/content/file")
async def get_content_file(path: str = Query(...), download: bool = Query(default=False)):
    file_path = resolve_content_file_path(path)
    if not file_path:
        raise HTTPException(404, "Файл не найден.")

    media_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(
        file_path,
        media_type=media_type or "application/octet-stream",
        filename=file_path.name if download else None,
    )


@app.get("/api/content/text")
async def get_content_text(path: str = Query(...)):
    file_path = resolve_content_file_path(path)
    if not file_path:
        raise HTTPException(404, "Файл не найден.")
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise HTTPException(400, f"Файл нельзя прочитать как UTF-8: {exc}") from exc
    return {"path": path, "name": file_path.name, "text": text}


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
