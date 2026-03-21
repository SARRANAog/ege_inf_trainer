# Полные тексты изменённых файлов

## .gitattributes

```text
* text=auto eol=lf
*.ps1 text eol=crlf
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.db binary
*.sqlite3 binary

```

## .gitignore

```text
# Environment
.env
.env.*
!.env.example

# Node / frontend
frontend/node_modules/
frontend/build/
frontend/dist/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Python / backend
__pycache__/
*.py[cod]
*.pyo
*.pyd
.pytest_cache/
.mypy_cache/
.ruff_cache/
.venv/
venv/

# Local app data
backend/data/
*.db
*.sqlite3

# OS / editors
.DS_Store
Thumbs.db
.vscode/
.idea/

# Test / generated artifacts
coverage/
htmlcov/
test_reports/
.emergent/

```

## README.md

```markdown
# EGE Informatics Trainer

Локальный тренажёр для подготовки к ЕГЭ по информатике на стеке **React 18 + FastAPI + Monaco + SQLite**.

Проект приведён к архитектуре, которая подходит для финального офлайн-продукта на одном изолированном Windows-ПК:
- **без MongoDB-сервиса**
- **с одним встроенным локальным хранилищем**
- **с сохранением текущих API-контрактов**
- **с возможностью раздавать собранный frontend прямо из backend**
- **с локальным profile/progress/mock/review persistence**
- **с основой под autosave через drafts API**

---

## Что теперь является текущим runtime

### Dev-режим
- backend: FastAPI на `http://127.0.0.1:8001`
- frontend: CRA dev server на `http://localhost:3000`
- storage: локальный SQLite-файл `backend/data/ege_trainer.sqlite3`

### Product-direction runtime
Если frontend собран (`frontend/build` существует), backend умеет раздавать его сам.
Это значит, что следующий шаг к desktop/exe уже не требует отдельного CRA-runtime в проде.

---

## Почему SQLite вместо MongoDB

Для одного офлайн-ПК SQLite лучше подходит, чем MongoDB, потому что:
- не нужен отдельный сервис и отдельный процесс БД
- нет дополнительной установки и администрирования
- база хранится в одном локальном файле
- проще упаковать в exe/setup
- надёжнее для single-user desktop сценария
- достаточно быстрый для профиля, прогресса, истории попыток, weekly review и mock exam

MongoDB была удобна как dev-сервис, но мешала реальному **one-click isolated-PC** сценарию.

---

## Что хранится локально

SQLite хранит:
- профиль ученика
- теорию
- практические задания
- прогресс по заданиям
- историю попыток
- weekly review
- mock exams
- drafts/autosave foundation
- metadata для seed/version контроля контента

База создаётся автоматически при первом старте backend.

---

## Переменные окружения

### `backend/.env`
```env
APP_DATA_DIR=./data
APP_DB_NAME=ege_trainer.sqlite3
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
SERVE_FRONTEND_BUILD=1
```

### `frontend/.env`
```env
REACT_APP_BACKEND_URL=http://127.0.0.1:8001
```

---

## Быстрый запуск под Windows

### 1. Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn server:app --host 127.0.0.1 --port 8001 --reload
```

### 2. Frontend (dev)
В новом окне PowerShell:
```powershell
cd frontend
npm install
npm start
```

---

## Проверка backend

```powershell
python backend_test.py
```

---

## Проверка product-direction режима

Собрать frontend и запустить только backend:

```powershell
cd frontend
npm install
npm run build

cd ..\backend
.\.venv\Scripts\Activate.ps1
uvicorn server:app --host 127.0.0.1 --port 8001
```

После этого приложение будет доступно через один backend-процесс на:
- `http://127.0.0.1:8001`

---

## Полезные endpoints

### Системные
- `GET /api/health`
- `POST /api/reseed`

### Профиль
- `GET /api/profile`
- `POST /api/profile`
- `PUT /api/profile`
- `POST /api/profile/reset`

### Теория и практика
- `GET /api/theory`
- `GET /api/theory/{task_number}`
- `GET /api/exercises/{task_number}`
- `GET /api/exercise/{exercise_id}`
- `POST /api/exercises/check`
- `POST /api/code/run`
- `POST /api/code/check`

### Прогресс и история
- `GET /api/progress`
- `GET /api/progress/{task_number}`
- `GET /api/attempts/{task_number}`

### Weekly review / mock exam
- `GET /api/weekly-review`
- `POST /api/weekly-review/start`
- `POST /api/weekly-review/complete`
- `GET /api/mock-exam`
- `POST /api/mock-exam/start`
- `PUT /api/mock-exam/{exam_id}/answer`
- `POST /api/mock-exam/{exam_id}/submit`
- `PUT /api/mock-exam/{exam_id}/flag`

### Drafts / autosave foundation
- `GET /api/drafts/{scope}`
- `PUT /api/drafts/{scope}`
- `DELETE /api/drafts/{scope}`

---

## Что уже учитывает архитектура

- один локальный профиль
- полностью офлайн-совместимое локальное хранилище
- отсутствие зависимости от внешней БД
- хранение истории попыток и прогресса в одном месте
- основа для autosave
- основа для будущей упаковки backend + frontend build в один локальный продукт
- UTF-8 как основная кодировка для текста и кода

---

## Что пока не является финальным packaging-этапом

В этой задаче **не делались**:
- финальный exe/setup
- финальная desktop-обёртка
- окончательный UI polish
- полный пересмотр всех 27 заданий

Но архитектура теперь подготовлена так, чтобы эти шаги делать уже без MongoDB и без лишних runtime-зависимостей.

```

## backend/.env

```text
APP_DATA_DIR=./data
APP_DB_NAME=ege_trainer.sqlite3
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
SERVE_FRONTEND_BUILD=1

```

## backend/.env.example

```text
APP_DATA_DIR=./data
APP_DB_NAME=ege_trainer.sqlite3
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
SERVE_FRONTEND_BUILD=1

```

## backend/requirements.txt

```text
fastapi==0.110.1
python-dotenv==1.2.1
python-multipart==0.0.22
requests==2.32.5
uvicorn==0.25.0

```

## backend/server.py

```python
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
    prog["accuracy"] = round(correct_attempts / total_attempts * 100, 1) if total_attempts > 0 else 0
    prog["last_practiced"] = current_time
    prog["updated_at"] = current_time
    prog.setdefault("status", "started")
    storage.upsert_progress(prog)
    await bump_profile_counters()


# ============== PROFILE ==============

@app.get("/api/profile")
async def get_profile():
    profile = await get_profile_doc()
    if not profile:
        return {"exists": False}
    payload = {**profile, "exists": True}
    return payload


@app.post("/api/profile")
async def create_profile(data: ProfileCreate):
    existing = await get_profile_doc()
    created_at = existing.get("created_at") if existing else now_iso()
    profile_data = {
        **data.model_dump(),
        "created_at": created_at,
        "updated_at": now_iso(),
        "roadmap_stage": existing.get("roadmap_stage", 1) if existing else 1,
        "weekly_review_due": existing.get("weekly_review_due", False) if existing else False,
        "last_weekly_review": existing.get("last_weekly_review") if existing else None,
        "total_exercises_done": existing.get("total_exercises_done", 0) if existing else 0,
        "total_correct": existing.get("total_correct", 0) if existing else 0,
    }
    await save_profile_doc(profile_data)
    return {"status": "ok"}


@app.put("/api/profile")
async def update_profile(data: ProfileUpdate):
    profile = await get_profile_doc()
    if not profile:
        raise HTTPException(404, "Профиль не найден")
    updates = {key: value for key, value in data.model_dump().items() if value is not None}
    profile.update(updates)
    profile["updated_at"] = now_iso()
    await save_profile_doc(profile)
    return {"status": "ok"}


@app.post("/api/profile/reset")
async def reset_profile_progress():
    storage.clear_progress_state()
    profile = await get_profile_doc()
    if profile:
        profile.update(
            {
                "updated_at": now_iso(),
                "roadmap_stage": 1,
                "weekly_review_due": False,
                "last_weekly_review": None,
                "total_exercises_done": 0,
                "total_correct": 0,
            }
        )
        await save_profile_doc(profile)
    return {"status": "ok"}


# ============== THEORY ==============

@app.get("/api/theory")
async def list_theory():
    docs = storage.list_theory()
    payload = []
    for doc in docs:
        payload.append({key: value for key, value in doc.items() if key not in {"full_theory", "short_theory"}})
    return payload


@app.get("/api/theory/{task_number}")
async def get_theory(task_number: int):
    doc = storage.get_theory(task_number)
    if not doc:
        raise HTTPException(404, "Theory not found")
    return doc


# ============== EXERCISES ==============

@app.get("/api/exercises/{task_number}")
async def get_exercises(task_number: int, difficulty: str = None, exercise_type: str = None):
    return storage.list_exercises(task_number, difficulty=difficulty, exercise_type=exercise_type)


@app.get("/api/exercise/{exercise_id}")
async def get_exercise(exercise_id: str):
    doc = storage.get_exercise(exercise_id)
    if not doc:
        raise HTTPException(404, "Exercise not found")
    return doc


@app.post("/api/exercises/check")
async def check_answer(data: AnswerCheck):
    exercise = storage.get_exercise(data.exercise_id)
    if not exercise:
        raise HTTPException(404, "Exercise not found")

    if exercise.get("exercise_type") == "code":
        return {"error": "Use /api/code/check for code exercises"}

    correct = False
    feedback = ""
    correct_answer = exercise.get("correct_answer")
    etype = exercise.get("answer_type", "single_choice")

    if etype == "single_choice":
        correct = str(data.answer) == str(correct_answer)
        feedback = "Правильно!" if correct else f"Неправильно. Верный ответ: {correct_answer}"
    elif etype == "multiple_choice":
        user_set = set(data.answer) if isinstance(data.answer, list) else set()
        correct_set = set(correct_answer) if isinstance(correct_answer, list) else set()
        correct = user_set == correct_set
        feedback = "Правильно!" if correct else f"Неправильно. Верный ответ: {', '.join(map(str, correct_answer))}"
    elif etype == "number":
        try:
            correct = float(data.answer) == float(correct_answer)
        except (ValueError, TypeError):
            correct = False
        feedback = "Правильно!" if correct else f"Неправильно. Верный ответ: {correct_answer}"
    elif etype == "matching":
        correct = data.answer == correct_answer
        feedback = "Правильно!" if correct else "Неправильно. Проверьте соответствия."
    elif etype == "ordering":
        correct = data.answer == correct_answer
        feedback = "Правильно!" if correct else "Неправильный порядок."
    else:
        correct = str(data.answer).strip() == str(correct_answer).strip()
        feedback = "Правильно!" if correct else f"Неправильно. Верный ответ: {correct_answer}"

    attempt = {
        "exercise_id": data.exercise_id,
        "task_number": exercise.get("task_number"),
        "answer": data.answer,
        "correct": correct,
        "timestamp": now_iso(),
    }
    storage.insert_attempt(attempt)
    await update_progress_after_attempt(exercise.get("task_number"), correct)

    return {
        "correct": correct,
        "feedback": feedback,
        "explanation": exercise.get("explanation", ""),
    }


# ============== CODE EXECUTION ==============

@app.post("/api/code/run")
async def run_code(data: CodeRun):
    return execute_python_code(data.code, data.stdin, timeout=10)


@app.post("/api/code/check")
async def check_code(data: CodeCheck):
    exercise = storage.get_exercise(data.exercise_id)
    if not exercise:
        raise HTTPException(404, "Exercise not found")

    test_cases = exercise.get("test_cases", [])
    required_constructs = exercise.get("required_constructs", [])
    banned_constructs = exercise.get("banned_constructs", [])

    ast_result = check_ast(data.code, required_constructs, banned_constructs)
    if not ast_result["ok"]:
        return {
            "passed": False,
            "feedback": ast_result["message"],
            "test_results": [],
            "ast_issues": ast_result.get("issues", []),
        }

    test_results = []
    all_passed = True
    for idx, test_case in enumerate(test_cases):
        result = execute_python_code(data.code, test_case.get("input", ""), timeout=5)
        expected = str(test_case.get("expected_output", "")).strip()
        actual = str(result.get("stdout", "")).strip()
        passed = actual == expected

        test_results.append(
            {
                "test_number": idx + 1,
                "passed": passed,
                "input": test_case.get("input", ""),
                "expected": expected,
                "actual": actual,
                "is_public": test_case.get("is_public", True),
                "error": result.get("stderr", ""),
            }
        )
        if not passed:
            all_passed = False

    attempt = {
        "exercise_id": data.exercise_id,
        "task_number": exercise.get("task_number"),
        "code": data.code,
        "correct": all_passed,
        "timestamp": now_iso(),
        "test_results": test_results,
    }
    storage.insert_attempt(attempt)
    await update_progress_after_attempt(exercise.get("task_number"), all_passed)

    return {
        "passed": all_passed,
        "test_results": test_results,
        "feedback": "Все тесты пройдены!" if all_passed else "Некоторые тесты не пройдены.",
    }


def execute_python_code(code: str, stdin: str = "", timeout: int = 10) -> dict[str, Any]:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
            temp_file.write(code)
            temp_file.flush()
            tmp_path = temp_file.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
            env={
                **os.environ,
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONIOENCODING": "utf-8",
            },
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "timeout": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Превышено время выполнения",
            "exit_code": -1,
            "timeout": True,
        }
    except Exception as exc:
        return {
            "stdout": "",
            "stderr": str(exc),
            "exit_code": -1,
            "timeout": False,
        }
    finally:
        if tmp_path and Path(tmp_path).exists():
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def check_ast(code: str, required_constructs: Optional[list[str]] = None, banned_constructs: Optional[list[str]] = None) -> dict[str, Any]:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {
            "ok": False,
            "message": f"Синтаксическая ошибка: {exc.msg} (строка {exc.lineno})",
            "issues": [str(exc)],
        }

    node_names = [type(node).__name__ for node in ast.walk(tree)]
    issues = []

    if required_constructs:
        mapping = {
            "for": "For",
            "while": "While",
            "if": "If",
            "def": "FunctionDef",
            "class": "ClassDef",
            "list_comprehension": "ListComp",
            "dict_comprehension": "DictComp",
            "lambda": "Lambda",
            "try": "Try",
            "with": "With",
            "import": "Import",
            "return": "Return",
        }
        for construct in required_constructs:
            if mapping.get(construct, construct) not in node_names:
                issues.append(f"Требуется конструкция: {construct}")

    if banned_constructs:
        banned_set = set(banned_constructs)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in banned_set:
                issues.append(f"Запрещённая конструкция: {node.func.id}")

    if issues:
        return {"ok": False, "message": "Проблемы со структурой кода", "issues": issues}

    return {"ok": True, "message": ""}


# ============== PROGRESS ==============

@app.get("/api/progress")
async def get_progress():
    tasks = storage.list_progress()
    total_attempts = storage.count_attempts()
    total_correct = storage.count_attempts(correct=True)
    tasks_with_practice = len([task for task in tasks if task.get("total_attempts", 0) > 0])

    avg_accuracy = 0.0
    task_accuracies = [task.get("accuracy", 0) for task in tasks if task.get("total_attempts", 0) > 0]
    if task_accuracies:
        avg_accuracy = round(sum(task_accuracies) / len(task_accuracies), 1)

    mock_count = len(storage.list_completed_mock_exams(limit=1000))
    review_count = storage.count_weekly_reviews(status="completed")

    estimated_score = estimate_ege_score(tasks, avg_accuracy, tasks_with_practice)

    return {
        "tasks": tasks,
        "total_tasks": 27,
        "tasks_practiced": tasks_with_practice,
        "total_attempts": total_attempts,
        "total_correct": total_correct,
        "avg_accuracy": avg_accuracy,
        "mock_exams_completed": mock_count,
        "weekly_reviews_completed": review_count,
        "estimated_score": estimated_score,
        "coverage": round(tasks_with_practice / 27 * 100, 1),
    }


def estimate_ege_score(tasks: list[dict[str, Any]], avg_accuracy: float, practiced_count: int) -> dict[str, Any]:
    if practiced_count == 0:
        return {"min": 0, "max": 0, "level": "not_started", "description": "Начните решать задания"}

    coverage = practiced_count / 27
    score_base = avg_accuracy * 0.7 + coverage * 100 * 0.3
    min_score = max(0, int(score_base * 0.8))
    max_score = min(100, int(score_base * 1.1))

    level = "beginner"
    if score_base >= 80:
        level = "strong"
    elif score_base >= 60:
        level = "good"
    elif score_base >= 40:
        level = "medium"

    descriptions = {
        "strong": "Отличная подготовка. Продолжайте закреплять материал.",
        "good": "Хорошая подготовка. Есть зоны для улучшения.",
        "medium": "Средний уровень. Рекомендуем больше практики.",
        "beginner": "Начальный этап. Следуйте дорожке обучения.",
    }
    return {
        "min": min_score,
        "max": max_score,
        "level": level,
        "description": descriptions.get(level, ""),
    }


@app.get("/api/progress/{task_number}")
async def get_task_progress(task_number: int):
    prog = storage.get_progress(task_number)
    if not prog:
        return {"task_number": task_number, "status": "not_started", "total_attempts": 0, "accuracy": 0}
    return prog


@app.get("/api/attempts/{task_number}")
async def get_attempts(task_number: int, limit: int = 20):
    return storage.list_attempts(task_number, limit)


# ============== ROADMAP ==============

@app.get("/api/roadmap")
async def get_roadmap():
    stages = storage.list_roadmap()
    profile = await get_profile_doc()
    progress_data = storage.list_progress()

    current_stage = profile.get("roadmap_stage", 1) if profile else 1
    review_due = profile.get("weekly_review_due", False) if profile else False

    weak_tasks = []
    for progress_item in progress_data:
        if progress_item.get("accuracy", 0) < 60 and progress_item.get("total_attempts", 0) >= 3:
            weak_tasks.append(progress_item["task_number"])

    return {
        "stages": stages,
        "current_stage": current_stage,
        "weekly_review_due": review_due,
        "weak_tasks": weak_tasks[:5],
        "progress_data": {item["task_number"]: item for item in progress_data},
    }


# ============== WEEKLY REVIEW ==============

@app.get("/api/weekly-review")
async def get_weekly_review():
    active = storage.get_active_weekly_review()
    if active:
        return active

    progress_data = storage.list_progress()
    weak_tasks = []
    old_tasks = []
    for progress_item in progress_data:
        if progress_item.get("accuracy", 0) < 60 and progress_item.get("total_attempts", 0) >= 2:
            weak_tasks.append(progress_item["task_number"])
        elif progress_item.get("last_practiced"):
            old_tasks.append(progress_item["task_number"])

    review_tasks = list(dict.fromkeys(weak_tasks[:8] + old_tasks[:6]))
    if not review_tasks:
        review_tasks = list(range(1, min(8, 28)))

    exercises = []
    for task_number in review_tasks:
        exercises.extend(storage.list_exercises_for_task_limited(task_number, limit=2))

    return {
        "status": "pending",
        "exercises": exercises,
        "total_exercises": len(exercises),
        "weak_tasks": weak_tasks,
        "review_tasks": review_tasks,
        "estimated_time": len(exercises) * 3,
    }


@app.post("/api/weekly-review/start")
async def start_weekly_review():
    review_data = await get_weekly_review()
    review = {
        "status": "active",
        "exercises": review_data.get("exercises", []),
        "completed_exercises": [],
        "results": [],
        "started_at": now_iso(),
        "total_exercises": review_data.get("total_exercises", 0),
    }
    storage.insert_weekly_review(review)
    return {"status": "ok"}


@app.post("/api/weekly-review/complete")
async def complete_weekly_review():
    completed_at = now_iso()
    storage.complete_active_weekly_review(completed_at)
    profile = await get_profile_doc()
    if profile:
        profile["weekly_review_due"] = False
        profile["last_weekly_review"] = completed_at
        profile["updated_at"] = completed_at
        await save_profile_doc(profile)
    return {"status": "ok"}


# ============== MOCK EXAM ==============

@app.get("/api/mock-exam")
async def get_mock_exam_status():
    active = storage.get_active_mock_exam()
    if active:
        return {"has_active": True, "exam": active}
    return {"has_active": False, "recent_exams": storage.list_completed_mock_exams(limit=5)}


@app.post("/api/mock-exam/start")
async def start_mock_exam():
    existing = storage.get_active_mock_exam()
    if existing:
        raise HTTPException(400, "Уже есть активный пробник")

    tasks_data = []
    for task_number in range(1, 28):
        exercises = storage.list_exercises_for_task_limited(task_number, limit=1)
        if exercises:
            tasks_data.append(
                {
                    "task_number": task_number,
                    "exercise": exercises[0],
                    "answer": None,
                    "code": None,
                    "status": "not_opened",
                    "flagged": False,
                }
            )

    exam_id = f"exam_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    exam = {
        "exam_id": exam_id,
        "status": "active",
        "tasks": tasks_data,
        "started_at": now_iso(),
        "time_spent": 0,
        "total_tasks": len(tasks_data),
    }
    storage.save_mock_exam(exam)
    return {"exam_id": exam_id, "total_tasks": len(tasks_data)}


@app.put("/api/mock-exam/{exam_id}/answer")
async def save_mock_answer(exam_id: str, data: MockExamAnswer):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "Пробник не найден")

    for task in exam.get("tasks", []):
        if task["task_number"] == data.task_number:
            task["answer"] = data.answer
            if data.code is not None:
                task["code"] = data.code
            task["status"] = "answered"
            break

    storage.save_mock_exam(exam)
    return {"status": "ok"}


@app.post("/api/mock-exam/{exam_id}/submit")
async def submit_mock_exam(exam_id: str):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "Пробник не найден")

    tasks = exam.get("tasks", [])
    total = len(tasks)
    correct = 0
    results = []

    for task in tasks:
        exercise = task.get("exercise", {})
        is_correct = False

        if exercise.get("exercise_type") == "code" and task.get("code"):
            test_cases = exercise.get("test_cases", [])
            is_correct = True
            for test_case in test_cases:
                result = execute_python_code(task["code"], test_case.get("input", ""), timeout=5)
                if str(result.get("stdout", "")).strip() != str(test_case.get("expected_output", "")).strip():
                    is_correct = False
                    break
        elif task.get("answer") is not None:
            correct_answer = exercise.get("correct_answer")
            if exercise.get("answer_type") == "multiple_choice":
                is_correct = set(task["answer"]) == set(correct_answer) if isinstance(correct_answer, list) else False
            else:
                is_correct = str(task["answer"]).strip() == str(correct_answer).strip()

        if is_correct:
            correct += 1

        results.append(
            {
                "task_number": task["task_number"],
                "correct": is_correct,
                "user_answer": task.get("answer"),
                "correct_answer": exercise.get("correct_answer"),
            }
        )

    score = round(correct / total * 100, 1) if total > 0 else 0
    exam.update(
        {
            "status": "completed",
            "completed_at": now_iso(),
            "results": results,
            "score": score,
            "correct_count": correct,
            "total_count": total,
        }
    )
    storage.save_mock_exam(exam)

    return {
        "score": score,
        "correct": correct,
        "total": total,
        "results": results,
    }


@app.put("/api/mock-exam/{exam_id}/flag")
async def flag_mock_task(exam_id: str, task_number: int):
    exam = storage.get_mock_exam(exam_id)
    if not exam:
        raise HTTPException(404, "Пробник не найден")

    for task in exam.get("tasks", []):
        if task["task_number"] == task_number:
            task["flagged"] = not task.get("flagged", False)
            break

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
    return {
        "status": "ok",
        "timestamp": now_iso(),
        "storage": "sqlite",
        "db_path": str(storage.db_path),
        "serving_frontend_build": SERVE_FRONTEND_BUILD and FRONTEND_BUILD_DIR.exists(),
    }


# ============== OPTIONAL FRONTEND BUILD HOSTING ==============

if SERVE_FRONTEND_BUILD and FRONTEND_BUILD_DIR.exists():
    @app.get("/", include_in_schema=False)
    async def serve_frontend_index():
        return FileResponse(FRONTEND_BUILD_DIR / "index.html")


    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend_app(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(404, "Not found")

        target = FRONTEND_BUILD_DIR / full_path
        if target.exists() and target.is_file():
            return FileResponse(target)

        if Path(full_path).suffix:
            raise HTTPException(404, "Static asset not found")

        return FileResponse(FRONTEND_BUILD_DIR / "index.html")

```

## backend/storage.py

```python
import hashlib
import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any, Optional


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


class LocalSQLiteStorage:
    def __init__(self, base_dir: Path):
        raw_data_dir = os.environ.get("APP_DATA_DIR", "./data")
        data_dir = Path(raw_data_dir)
        if not data_dir.is_absolute():
            data_dir = (base_dir / data_dir).resolve()
        db_name = os.environ.get("APP_DB_NAME", "ege_trainer.sqlite3")
        self.data_dir = data_dir
        self.db_path = data_dir / db_name
        self._lock = threading.RLock()

    def initialize(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode = WAL;
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS app_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    updated_at TEXT NOT NULL,
                    data_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS theory (
                    task_number INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    data_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS exercises (
                    exercise_id TEXT PRIMARY KEY,
                    task_number INTEGER NOT NULL,
                    difficulty TEXT,
                    exercise_type TEXT,
                    answer_type TEXT,
                    title TEXT NOT NULL,
                    data_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_exercises_task_number ON exercises(task_number);
                CREATE INDEX IF NOT EXISTS idx_exercises_filters ON exercises(task_number, difficulty, exercise_type);

                CREATE TABLE IF NOT EXISTS progress (
                    task_number INTEGER PRIMARY KEY,
                    total_attempts INTEGER NOT NULL DEFAULT 0,
                    correct_attempts INTEGER NOT NULL DEFAULT 0,
                    accuracy REAL NOT NULL DEFAULT 0,
                    last_practiced TEXT,
                    status TEXT NOT NULL DEFAULT 'not_started',
                    updated_at TEXT NOT NULL,
                    data_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_number INTEGER NOT NULL,
                    exercise_id TEXT,
                    correct INTEGER NOT NULL DEFAULT 0,
                    timestamp TEXT NOT NULL,
                    data_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_attempts_task_time ON attempts(task_number, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_attempts_correct ON attempts(correct);

                CREATE TABLE IF NOT EXISTS weekly_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    data_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_weekly_reviews_status ON weekly_reviews(status, started_at DESC);

                CREATE TABLE IF NOT EXISTS mock_exams (
                    exam_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    score REAL,
                    correct_count INTEGER,
                    total_count INTEGER,
                    data_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_mock_exams_status ON mock_exams(status, completed_at DESC);

                CREATE TABLE IF NOT EXISTS roadmap (
                    stage_number INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    data_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS drafts (
                    scope TEXT PRIMARY KEY,
                    draft_type TEXT NOT NULL,
                    task_number INTEGER,
                    exercise_id TEXT,
                    updated_at TEXT NOT NULL,
                    data_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_drafts_task_number ON drafts(task_number, updated_at DESC);
                """
            )
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _fetch_one_doc(self, query: str, params: tuple[Any, ...] = ()) -> Optional[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            row = conn.execute(query, params).fetchone()
        if not row:
            return None
        return json.loads(row["data_json"])

    def _fetch_many_docs(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [json.loads(row["data_json"]) for row in rows]

    def _execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(query, params)
            conn.commit()

    def _executemany(self, query: str, params_seq: list[tuple[Any, ...]]) -> None:
        with self._lock, self._connect() as conn:
            conn.executemany(query, params_seq)
            conn.commit()

    def get_meta(self, key: str) -> Optional[str]:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT value FROM app_meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def set_meta(self, key: str, value: str) -> None:
        self._execute(
            """
            INSERT INTO app_meta (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )

    def _content_signature(self, theory_data: list[dict[str, Any]], exercises_data: list[dict[str, Any]], roadmap_data: list[dict[str, Any]]) -> str:
        payload = _json_dumps(
            {
                "theory": theory_data,
                "exercises": exercises_data,
                "roadmap": roadmap_data,
            }
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def seed_static_content(
        self,
        theory_data: list[dict[str, Any]],
        exercises_data: list[dict[str, Any]],
        roadmap_data: list[dict[str, Any]],
        *,
        force: bool = False,
    ) -> dict[str, Any]:
        signature = self._content_signature(theory_data, exercises_data, roadmap_data)
        current_signature = self.get_meta("content_signature")

        with self._lock, self._connect() as conn:
            theory_count = conn.execute("SELECT COUNT(*) AS c FROM theory").fetchone()["c"]
            exercise_count = conn.execute("SELECT COUNT(*) AS c FROM exercises").fetchone()["c"]
            roadmap_count = conn.execute("SELECT COUNT(*) AS c FROM roadmap").fetchone()["c"]

        needs_seed = force or current_signature != signature or theory_count < 27 or exercise_count == 0 or roadmap_count == 0
        if not needs_seed:
            return {
                "seeded": False,
                "theory": theory_count,
                "exercises": exercise_count,
                "roadmap": roadmap_count,
                "signature": signature,
            }

        theory_rows = [
            (doc["task_number"], doc.get("title", f"Задание {doc['task_number']}"), _json_dumps(doc))
            for doc in theory_data
        ]
        exercise_rows = [
            (
                doc["exercise_id"],
                doc["task_number"],
                doc.get("difficulty"),
                doc.get("exercise_type"),
                doc.get("answer_type"),
                doc.get("title", doc["exercise_id"]),
                _json_dumps(doc),
            )
            for doc in exercises_data
        ]
        roadmap_rows = [
            (doc["stage_number"], doc.get("title", f"Этап {doc['stage_number']}"), _json_dumps(doc))
            for doc in roadmap_data
        ]

        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM theory")
            conn.execute("DELETE FROM exercises")
            conn.execute("DELETE FROM roadmap")
            conn.executemany(
                "INSERT INTO theory (task_number, title, data_json) VALUES (?, ?, ?)",
                theory_rows,
            )
            conn.executemany(
                """
                INSERT INTO exercises (exercise_id, task_number, difficulty, exercise_type, answer_type, title, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                exercise_rows,
            )
            conn.executemany(
                "INSERT INTO roadmap (stage_number, title, data_json) VALUES (?, ?, ?)",
                roadmap_rows,
            )
            conn.execute(
                """
                INSERT INTO app_meta (key, value)
                VALUES ('content_signature', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (signature,),
            )
            conn.commit()

        return {
            "seeded": True,
            "theory": len(theory_rows),
            "exercises": len(exercise_rows),
            "roadmap": len(roadmap_rows),
            "signature": signature,
        }

    def get_profile(self) -> Optional[dict[str, Any]]:
        return self._fetch_one_doc("SELECT data_json FROM profile WHERE id = 1")

    def save_profile(self, profile: dict[str, Any]) -> None:
        updated_at = profile.get("updated_at") or ""
        self._execute(
            """
            INSERT INTO profile (id, updated_at, data_json)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET updated_at = excluded.updated_at, data_json = excluded.data_json
            """,
            (updated_at, _json_dumps(profile)),
        )

    def list_theory(self) -> list[dict[str, Any]]:
        return self._fetch_many_docs("SELECT data_json FROM theory ORDER BY task_number ASC")

    def get_theory(self, task_number: int) -> Optional[dict[str, Any]]:
        return self._fetch_one_doc("SELECT data_json FROM theory WHERE task_number = ?", (task_number,))

    def list_exercises(
        self,
        task_number: int,
        difficulty: Optional[str] = None,
        exercise_type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        query = "SELECT data_json FROM exercises WHERE task_number = ?"
        params: list[Any] = [task_number]
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        if exercise_type:
            query += " AND exercise_type = ?"
            params.append(exercise_type)
        query += " ORDER BY exercise_id ASC"
        return self._fetch_many_docs(query, tuple(params))

    def get_exercise(self, exercise_id: str) -> Optional[dict[str, Any]]:
        return self._fetch_one_doc("SELECT data_json FROM exercises WHERE exercise_id = ?", (exercise_id,))

    def list_exercises_for_task_limited(self, task_number: int, limit: int) -> list[dict[str, Any]]:
        query = f"SELECT data_json FROM exercises WHERE task_number = ? ORDER BY exercise_id ASC LIMIT {int(limit)}"
        return self._fetch_many_docs(query, (task_number,))

    def upsert_progress(self, progress: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO progress (task_number, total_attempts, correct_attempts, accuracy, last_practiced, status, updated_at, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_number) DO UPDATE SET
                total_attempts = excluded.total_attempts,
                correct_attempts = excluded.correct_attempts,
                accuracy = excluded.accuracy,
                last_practiced = excluded.last_practiced,
                status = excluded.status,
                updated_at = excluded.updated_at,
                data_json = excluded.data_json
            """,
            (
                progress["task_number"],
                progress.get("total_attempts", 0),
                progress.get("correct_attempts", 0),
                progress.get("accuracy", 0),
                progress.get("last_practiced"),
                progress.get("status", "not_started"),
                progress.get("updated_at", ""),
                _json_dumps(progress),
            ),
        )

    def get_progress(self, task_number: int) -> Optional[dict[str, Any]]:
        return self._fetch_one_doc("SELECT data_json FROM progress WHERE task_number = ?", (task_number,))

    def list_progress(self) -> list[dict[str, Any]]:
        return self._fetch_many_docs("SELECT data_json FROM progress ORDER BY task_number ASC")

    def clear_progress_state(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM progress")
            conn.execute("DELETE FROM attempts")
            conn.execute("DELETE FROM weekly_reviews")
            conn.execute("DELETE FROM mock_exams")
            conn.execute("DELETE FROM drafts")
            conn.commit()

    def insert_attempt(self, attempt: dict[str, Any]) -> None:
        self._execute(
            "INSERT INTO attempts (task_number, exercise_id, correct, timestamp, data_json) VALUES (?, ?, ?, ?, ?)",
            (
                attempt.get("task_number", 0),
                attempt.get("exercise_id"),
                1 if attempt.get("correct") else 0,
                attempt.get("timestamp", ""),
                _json_dumps(attempt),
            ),
        )

    def count_attempts(self, *, correct: Optional[bool] = None) -> int:
        query = "SELECT COUNT(*) AS c FROM attempts"
        params: tuple[Any, ...] = ()
        if correct is not None:
            query += " WHERE correct = ?"
            params = (1 if correct else 0,)
        with self._lock, self._connect() as conn:
            row = conn.execute(query, params).fetchone()
        return int(row["c"]) if row else 0

    def list_attempts(self, task_number: int, limit: int) -> list[dict[str, Any]]:
        query = f"SELECT data_json FROM attempts WHERE task_number = ? ORDER BY timestamp DESC LIMIT {int(limit)}"
        return self._fetch_many_docs(query, (task_number,))

    def list_roadmap(self) -> list[dict[str, Any]]:
        return self._fetch_many_docs("SELECT data_json FROM roadmap ORDER BY stage_number ASC")


    def count_weekly_reviews(self, *, status: Optional[str] = None) -> int:
        query = "SELECT COUNT(*) AS c FROM weekly_reviews"
        params: tuple[Any, ...] = ()
        if status is not None:
            query += " WHERE status = ?"
            params = (status,)
        with self._lock, self._connect() as conn:
            row = conn.execute(query, params).fetchone()
        return int(row["c"]) if row else 0

    def get_active_weekly_review(self) -> Optional[dict[str, Any]]:
        return self._fetch_one_doc(
            "SELECT data_json FROM weekly_reviews WHERE status = 'active' ORDER BY started_at DESC LIMIT 1"
        )

    def insert_weekly_review(self, review: dict[str, Any]) -> None:
        self._execute(
            "INSERT INTO weekly_reviews (status, started_at, completed_at, data_json) VALUES (?, ?, ?, ?)",
            (
                review.get("status", "active"),
                review.get("started_at"),
                review.get("completed_at"),
                _json_dumps(review),
            ),
        )

    def complete_active_weekly_review(self, completed_at: str) -> None:
        active = self.get_active_weekly_review()
        if not active:
            return
        active["status"] = "completed"
        active["completed_at"] = completed_at
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                UPDATE weekly_reviews
                SET status = ?, completed_at = ?, data_json = ?
                WHERE status = 'active'
                """,
                (active["status"], active["completed_at"], _json_dumps(active)),
            )
            conn.commit()

    def get_active_mock_exam(self) -> Optional[dict[str, Any]]:
        return self._fetch_one_doc(
            "SELECT data_json FROM mock_exams WHERE status = 'active' ORDER BY started_at DESC LIMIT 1"
        )

    def list_completed_mock_exams(self, limit: int) -> list[dict[str, Any]]:
        query = f"SELECT data_json FROM mock_exams WHERE status = 'completed' ORDER BY completed_at DESC LIMIT {int(limit)}"
        return self._fetch_many_docs(query)

    def save_mock_exam(self, exam: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO mock_exams (exam_id, status, started_at, completed_at, score, correct_count, total_count, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(exam_id) DO UPDATE SET
                status = excluded.status,
                started_at = excluded.started_at,
                completed_at = excluded.completed_at,
                score = excluded.score,
                correct_count = excluded.correct_count,
                total_count = excluded.total_count,
                data_json = excluded.data_json
            """,
            (
                exam["exam_id"],
                exam.get("status", "active"),
                exam.get("started_at"),
                exam.get("completed_at"),
                exam.get("score"),
                exam.get("correct_count"),
                exam.get("total_count"),
                _json_dumps(exam),
            ),
        )

    def get_mock_exam(self, exam_id: str) -> Optional[dict[str, Any]]:
        return self._fetch_one_doc("SELECT data_json FROM mock_exams WHERE exam_id = ?", (exam_id,))

    def get_draft(self, scope: str) -> Optional[dict[str, Any]]:
        return self._fetch_one_doc("SELECT data_json FROM drafts WHERE scope = ?", (scope,))

    def save_draft(self, scope: str, draft: dict[str, Any]) -> None:
        self._execute(
            """
            INSERT INTO drafts (scope, draft_type, task_number, exercise_id, updated_at, data_json)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(scope) DO UPDATE SET
                draft_type = excluded.draft_type,
                task_number = excluded.task_number,
                exercise_id = excluded.exercise_id,
                updated_at = excluded.updated_at,
                data_json = excluded.data_json
            """,
            (
                scope,
                draft.get("draft_type", "generic"),
                draft.get("task_number"),
                draft.get("exercise_id"),
                draft.get("updated_at", ""),
                _json_dumps(draft),
            ),
        )

    def delete_draft(self, scope: str) -> None:
        self._execute("DELETE FROM drafts WHERE scope = ?", (scope,))

```

## backend_test.py

```python
#!/usr/bin/env python3
import requests
import sys


class EGETrainerAPITester:
    def __init__(self, base_url="http://127.0.0.1:8001"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        headers = headers or {'Content-Type': 'application/json'}
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except Exception:
                    return True, response.text

            print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
            return False, {}
        except requests.exceptions.Timeout:
            print("❌ Failed - Timeout")
            self.failed_tests.append(f"{name}: Timeout")
            return False, {}
        except Exception as exc:
            print(f"❌ Failed - Error: {exc}")
            self.failed_tests.append(f"{name}: {exc}")
            return False, {}

    def run_all_tests(self):
        print("🚀 Starting EGE Trainer API Tests")
        print("=" * 50)

        self.run_test("Health Check", "GET", "/api/health", 200)
        self.run_test("Get Profile", "GET", "/api/profile", 200)
        self.run_test("List Theory", "GET", "/api/theory", 200)
        self.run_test("Get Exercises Task 1", "GET", "/api/exercises/1", 200)
        self.run_test("Get Progress", "GET", "/api/progress", 200)
        self.run_test("Get Roadmap", "GET", "/api/roadmap", 200)
        self.run_test("Get Weekly Review", "GET", "/api/weekly-review", 200)
        self.run_test("Get Mock Exam Status", "GET", "/api/mock-exam", 200)
        self.run_test(
            "Save Draft",
            "PUT",
            "/api/drafts/test-scope",
            200,
            {
                "draft_type": "practice",
                "task_number": 2,
                "exercise_id": "demo_exercise",
                "payload": {"code": "print(123)"},
            },
        )
        self.run_test("Get Draft", "GET", "/api/drafts/test-scope", 200)
        self.run_test("Delete Draft", "DELETE", "/api/drafts/test-scope", 200)
        self.run_test("Reset Progress Endpoint", "POST", "/api/profile/reset", 200, {})

        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for fail in self.failed_tests:
                print(f"   - {fail}")
        else:
            print("\n🎉 All tests passed!")
        return self.tests_passed == self.tests_run


def main():
    tester = EGETrainerAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

```

## frontend/.env

```text
REACT_APP_BACKEND_URL=http://127.0.0.1:8001

```

## frontend/.env.example

```text
REACT_APP_BACKEND_URL=http://127.0.0.1:8001

```

## frontend/src/pages/Practice.js

```javascript
import React, { useState, useEffect, useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';

const API = process.env.REACT_APP_BACKEND_URL;

function normalizeTaskNumber(value, fallback = 1) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 27) return fallback;
  return parsed;
}

function normalizeMode(value) {
  return ['training', 'control', 'weak'].includes(value) ? value : 'training';
}

function ExerciseCard({ exercise, onNext, theoryLink }) {
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [multiAnswers, setMultiAnswers] = useState([]);
  const [numberAnswer, setNumberAnswer] = useState('');
  const [code, setCode] = useState(exercise.code_template || '');
  const [result, setResult] = useState(null);
  const [output, setOutput] = useState(null);
  const [checking, setChecking] = useState(false);
  const [running, setRunning] = useState(false);
  const [hintIdx, setHintIdx] = useState(-1);
  const [draftReady, setDraftReady] = useState(false);
  const isFirstAutosave = useRef(true);

  const isCode = exercise.exercise_type === 'code';
  const atype = exercise.answer_type;
  const draftScope = `practice:${exercise.exercise_id}`;

  useEffect(() => {
    let cancelled = false;

    const loadDraft = async () => {
      setSelectedAnswer(null);
      setMultiAnswers([]);
      setNumberAnswer('');
      setCode(exercise.code_template || '');
      setResult(null);
      setOutput(null);
      setHintIdx(-1);
      setDraftReady(false);
      isFirstAutosave.current = true;

      try {
        const res = await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`);
        if (!res.ok) {
          if (res.status !== 404) {
            console.error('Failed to load draft', res.status);
          }
          return;
        }

        const draft = await res.json();
        const payload = draft?.payload || {};
        if (cancelled) return;

        setSelectedAnswer(payload.selectedAnswer ?? null);
        setMultiAnswers(Array.isArray(payload.multiAnswers) ? payload.multiAnswers : []);
        setNumberAnswer(payload.numberAnswer ?? '');
        setCode(payload.code ?? (exercise.code_template || ''));
      } catch (error) {
        console.error(error);
      } finally {
        if (!cancelled) {
          setDraftReady(true);
        }
      }
    };

    loadDraft();
    return () => {
      cancelled = true;
    };
  }, [draftScope, exercise.code_template]);

  useEffect(() => {
    if (!draftReady) return undefined;

    if (isFirstAutosave.current) {
      isFirstAutosave.current = false;
      return undefined;
    }

    const timer = setTimeout(async () => {
      try {
        await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            draft_type: 'practice',
            task_number: exercise.task_number,
            exercise_id: exercise.exercise_id,
            payload: {
              selectedAnswer,
              multiAnswers,
              numberAnswer,
              code,
            },
          }),
        });
      } catch (error) {
        console.error(error);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [code, draftReady, draftScope, exercise.exercise_id, exercise.task_number, multiAnswers, numberAnswer, selectedAnswer]);

  const handleCheck = async () => {
    setChecking(true);
    try {
      if (isCode) {
        const res = await fetch(`${API}/api/code/check`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ exercise_id: exercise.exercise_id, code }),
        });
        setResult(await res.json());
      } else {
        let answer = selectedAnswer;
        if (atype === 'multiple_choice') answer = multiAnswers;
        else if (atype === 'number') answer = numberAnswer;
        const res = await fetch(`${API}/api/exercises/check`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ exercise_id: exercise.exercise_id, answer }),
        });
        setResult(await res.json());
      }
    } catch (e) {
      console.error(e);
    }
    setChecking(false);
  };

  const handleRun = async () => {
    setRunning(true);
    try {
      const res = await fetch(`${API}/api/code/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, stdin: '' }),
      });
      setOutput(await res.json());
    } catch (e) {
      console.error(e);
    }
    setRunning(false);
  };

  const handleReset = async () => {
    setSelectedAnswer(null);
    setMultiAnswers([]);
    setNumberAnswer('');
    setCode(exercise.code_template || '');
    setResult(null);
    setOutput(null);
    setHintIdx(-1);
    isFirstAutosave.current = true;

    try {
      await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`, { method: 'DELETE' });
    } catch (error) {
      console.error(error);
    } finally {
      setDraftReady(true);
    }
  };

  const toggleMulti = (opt) => {
    setMultiAnswers(prev => prev.includes(opt) ? prev.filter(x => x !== opt) : [...prev, opt]);
  };

  return (
    <div className="card fade-in" style={{ padding: 24 }} data-testid={`exercise-${exercise.exercise_id}`}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span className="badge badge-accent">№{exercise.task_number}</span>
        <span className={`badge ${exercise.difficulty === 'easy' ? 'badge-success' : exercise.difficulty === 'hard' ? 'badge-danger' : 'badge-warning'}`}>
          {exercise.difficulty === 'easy' ? 'Лёгкое' : exercise.difficulty === 'hard' ? 'Сложное' : 'Среднее'}
        </span>
        {isCode && <span className="badge badge-accent">Python</span>}
        <span style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: 12 }}>Локальный автосейв</span>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>{exercise.title}</h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.7, marginBottom: 20, whiteSpace: 'pre-wrap' }}>{exercise.text}</p>

      {isCode ? (
        <div style={{ marginBottom: 16 }}>
          <div style={{ border: '1px solid var(--border)', borderRadius: 12, overflow: 'hidden' }}>
            <Editor
              height="260px"
              language="python"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                fontSize: 14,
                minimap: { enabled: false },
                wordWrap: 'on',
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
                padding: { top: 12 },
              }}
            />
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            <button className="btn btn-secondary btn-sm" onClick={handleRun} disabled={running} data-testid="run-code-btn">
              {running ? 'Выполняется...' : 'Запустить код'}
            </button>
            <button className="btn btn-primary btn-sm" onClick={handleCheck} disabled={checking} data-testid="check-code-btn">
              {checking ? 'Проверка...' : 'Проверить решение'}
            </button>
          </div>
          {output && (
            <div className="code-block" style={{ marginTop: 12, fontSize: 13 }}>
              {output.stdout && <div style={{ color: 'var(--text-primary)' }}>Вывод: {output.stdout}</div>}
              {output.stderr && <div style={{ color: 'var(--danger)' }}>Ошибка: {output.stderr}</div>}
              {output.timeout && <div style={{ color: 'var(--warning)' }}>Превышено время выполнения</div>}
            </div>
          )}
        </div>
      ) : atype === 'single_choice' && exercise.options ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
          {exercise.options.map((opt, i) => (
            <button
              key={i}
              onClick={() => setSelectedAnswer(opt.charAt(0))}
              style={{
                padding: '10px 16px', borderRadius: 10, border: '1px solid', textAlign: 'left', cursor: 'pointer', fontSize: 14,
                borderColor: selectedAnswer === opt.charAt(0) ? 'var(--accent)' : 'var(--border)',
                background: selectedAnswer === opt.charAt(0) ? 'rgba(108,127,216,0.1)' : 'var(--bg-elevated)',
                color: 'var(--text-primary)',
              }}
              data-testid={`option-${i}`}
            >
              {opt}
            </button>
          ))}
        </div>
      ) : atype === 'multiple_choice' && exercise.options ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
          {exercise.options.map((opt, i) => (
            <button
              key={i}
              onClick={() => toggleMulti(opt.charAt(0))}
              style={{
                padding: '10px 16px', borderRadius: 10, border: '1px solid', textAlign: 'left', cursor: 'pointer', fontSize: 14,
                borderColor: multiAnswers.includes(opt.charAt(0)) ? 'var(--accent)' : 'var(--border)',
                background: multiAnswers.includes(opt.charAt(0)) ? 'rgba(108,127,216,0.1)' : 'var(--bg-elevated)',
                color: 'var(--text-primary)',
              }}
              data-testid={`option-multi-${i}`}
            >
              <span style={{ marginRight: 8 }}>{multiAnswers.includes(opt.charAt(0)) ? '☑' : '☐'}</span>
              {opt}
            </button>
          ))}
        </div>
      ) : (
        <div style={{ marginBottom: 16 }}>
          <input
            className="input"
            type={atype === 'number' ? 'number' : 'text'}
            value={numberAnswer}
            onChange={e => setNumberAnswer(e.target.value)}
            placeholder="Введите ответ"
            style={{ maxWidth: 300 }}
            data-testid="number-answer-input"
          />
        </div>
      )}

      {result && (
        <div
          style={{
            padding: 14,
            borderRadius: 12,
            marginBottom: 16,
            background: result.correct || result.passed ? 'rgba(92,184,122,0.08)' : 'rgba(224,96,112,0.08)',
            border: `1px solid ${result.correct || result.passed ? 'var(--success)' : 'var(--danger)'}`,
          }}
          data-testid="exercise-result"
        >
          <div style={{ fontWeight: 600, fontSize: 14, color: result.correct || result.passed ? 'var(--success)' : 'var(--danger)', marginBottom: 4 }}>
            {result.correct || result.passed ? 'Правильно!' : 'Неправильно'}
          </div>
          {result.feedback && <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{result.feedback}</div>}
          {result.explanation && <div style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 6 }}>{result.explanation}</div>}
          {result.test_results && result.test_results.length > 0 && (
            <div style={{ marginTop: 8 }}>
              {result.test_results.filter(t => t.is_public).map((t, i) => (
                <div key={i} style={{ fontSize: 12, color: t.passed ? 'var(--success)' : 'var(--danger)', marginTop: 4 }}>
                  Тест {t.test_number}: {t.passed ? 'пройден' : `ожидалось "${t.expected}", получено "${t.actual}"`}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        {!isCode && !result && (
          <button
            className="btn btn-primary btn-sm"
            onClick={handleCheck}
            disabled={checking || (atype === 'single_choice' && !selectedAnswer) || (atype === 'number' && !numberAnswer)}
            data-testid="check-answer-btn"
          >
            {checking ? 'Проверка...' : 'Проверить ответ'}
          </button>
        )}
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => setHintIdx(Math.min(hintIdx + 1, (exercise.hints || []).length - 1))}
          disabled={!exercise.hints || exercise.hints.length === 0 || hintIdx >= exercise.hints.length - 1}
          data-testid="hint-btn"
        >
          Подсказка {hintIdx >= 0 ? `(${hintIdx + 1}/${exercise.hints?.length || 0})` : ''}
        </button>
        <button className="btn btn-ghost btn-sm" onClick={handleReset} data-testid="reset-btn">Сбросить</button>
        <button className="btn btn-secondary btn-sm" onClick={onNext} style={{ marginLeft: 'auto' }} data-testid="next-exercise-btn">Следующее</button>
        <Link to={theoryLink} className="btn btn-ghost btn-sm">К теории</Link>
      </div>

      {hintIdx >= 0 && exercise.hints && (
        <div style={{ marginTop: 12, padding: 12, background: 'rgba(108,127,216,0.06)', borderRadius: 10, border: '1px solid rgba(108,127,216,0.15)' }}>
          {exercise.hints.slice(0, hintIdx + 1).map((hint, index) => (
            <div key={index} style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: index > 0 ? 6 : 0 }}>
              Подсказка {index + 1}: {hint}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PracticePage() {
  const [taskNumber, setTaskNumber] = useState(1);
  const [exercises, setExercises] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [tasks, setTasks] = useState([]);
  const [progress, setProgress] = useState([]);
  const [mode, setMode] = useState('training');
  const [loading, setLoading] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    const nextTask = normalizeTaskNumber(searchParams.get('task'), 1);
    const nextMode = normalizeMode(searchParams.get('mode'));
    setTaskNumber(nextTask);
    setMode(nextMode);
  }, [searchParams]);

  useEffect(() => {
    fetch(`${API}/api/theory`).then(r => r.json()).then(setTasks).catch(() => {});
    fetch(`${API}/api/progress`).then(r => r.json()).then(data => setProgress(data.tasks || [])).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);

    const load = async () => {
      try {
        if (mode === 'weak') {
          const weakTasks = (progress || [])
            .filter(item => (item.accuracy || 0) < 60 && (item.total_attempts || 0) >= 3)
            .map(item => item.task_number);
          const fallbackTask = weakTasks[0] || taskNumber;
          const targetTask = weakTasks.includes(taskNumber) ? taskNumber : fallbackTask;
          if (targetTask !== taskNumber) {
            setSearchParams({ task: String(targetTask), mode: 'weak' });
            return;
          }
        }

        const response = await fetch(`${API}/api/exercises/${taskNumber}`);
        let data = await response.json();

        if (mode === 'control') {
          const sorted = [...data].sort((a, b) => {
            const diffOrder = { easy: 0, medium: 1, hard: 2 };
            return (diffOrder[a.difficulty] ?? 1) - (diffOrder[b.difficulty] ?? 1);
          });
          data = sorted.slice(0, Math.min(sorted.length, 5));
        }

        setExercises(data);
        setCurrentIdx(0);
      } catch (error) {
        console.error(error);
      }
      setLoading(false);
    };

    if (progress.length > 0 || mode !== 'weak') {
      load();
    } else {
      setLoading(false);
    }
  }, [taskNumber, mode, progress, setSearchParams]);

  const handleNext = () => {
    if (currentIdx < exercises.length - 1) setCurrentIdx(currentIdx + 1);
    else setCurrentIdx(0);
  };

  const updateRoute = (nextTask, nextMode = mode) => {
    setSearchParams({ task: String(nextTask), mode: nextMode });
  };

  const weakTaskNumbers = (progress || [])
    .filter(item => (item.accuracy || 0) < 60 && (item.total_attempts || 0) >= 3)
    .map(item => item.task_number);

  return (
    <div className="fade-in" style={{ display: 'flex', gap: 20, height: 'calc(100vh - 104px)' }}>
      <div style={{ width: 200, minWidth: 200, overflowY: 'auto' }} data-testid="practice-task-list">
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 12 }}>Задание</div>
        {(tasks.length > 0 ? tasks : Array.from({ length: 27 }, (_, i) => ({ task_number: i + 1, title: `№${i + 1}` }))).map(t => {
          const isWeak = weakTaskNumbers.includes(t.task_number);
          return (
            <button
              key={t.task_number}
              onClick={() => updateRoute(t.task_number)}
              className={`nav-item ${taskNumber === t.task_number ? 'active' : ''}`}
              style={{ width: '100%', textAlign: 'left', border: 'none', fontSize: 13 }}
              data-testid={`practice-task-${t.task_number}`}
            >
              <span style={{
                width: 22, height: 22, borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 600,
                background: taskNumber === t.task_number ? 'var(--accent)' : 'var(--bg-elevated)',
                color: taskNumber === t.task_number ? 'white' : 'var(--text-secondary)', flexShrink: 0,
              }}>{t.task_number}</span>
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.title || `Задание ${t.task_number}`}</span>
              {isWeak && <span className="badge badge-danger" style={{ marginLeft: 'auto', fontSize: 10 }}>weak</span>}
            </button>
          );
        })}
      </div>

      <div style={{ flex: 1, overflowY: 'auto', minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
          <div className="segment-control" data-testid="practice-mode">
            {[{ v: 'training', l: 'Тренировка' }, { v: 'control', l: 'Контроль' }, { v: 'weak', l: 'Слабые места' }].map(item => (
              <button
                key={item.v}
                className={`segment-btn ${mode === item.v ? 'active' : ''}`}
                onClick={() => updateRoute(taskNumber, item.v)}
                data-testid={`mode-${item.v}`}
              >
                {item.l}
              </button>
            ))}
          </div>
          {mode === 'control' && <span style={{ color: 'var(--warning)', fontSize: 13 }}>Контроль: показываем до 5 заданий по номеру, отсортированных по сложности.</span>}
          {mode === 'weak' && <span style={{ color: 'var(--danger)', fontSize: 13 }}>Режим слабых мест фокусируется на темах с точностью ниже 60% после 3+ попыток.</span>}
          {exercises.length > 0 && (
            <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>
              Задание {currentIdx + 1} из {exercises.length}
            </span>
          )}
        </div>

        {loading ? (
          <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Загрузка заданий...</div>
        ) : exercises.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: 40 }}>
            <div style={{ fontSize: 15, color: 'var(--text-secondary)' }}>
              {mode === 'weak'
                ? 'Пока нет слабых мест по заданию правил режима. Сначала накопите хотя бы 3 попытки с точностью ниже 60%.'
                : 'Задания для этого номера пока не добавлены'}
            </div>
            <Link to={`/theory?task=${taskNumber}`} className="btn btn-secondary btn-sm" style={{ marginTop: 16 }}>Изучить теорию</Link>
          </div>
        ) : (
          <ExerciseCard
            key={exercises[currentIdx]?.exercise_id}
            exercise={exercises[currentIdx]}
            onNext={handleNext}
            theoryLink={`/theory?task=${taskNumber}`}
          />
        )}
      </div>
    </div>
  );
}

```
