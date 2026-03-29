"""Content data aggregator for theory, exercises and roadmap.

Tasks 1-27 are loaded from root ``content/*`` when files exist.
Legacy in-code datasets are used as a fallback source.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from .theory_content import THEORY_DATA as LEGACY_THEORY_DATA
    from .exercises_content import EXERCISES_DATA as LEGACY_BASE_EXERCISES
    from .exercises_extra import EXTRA_EXERCISES
    from .exercises_extra_2 import EXTRA_EXERCISES_2
    from .roadmap_content import ROADMAP_DATA as LEGACY_ROADMAP_DATA
except ImportError:
    from theory_content import THEORY_DATA as LEGACY_THEORY_DATA
    from exercises_content import EXERCISES_DATA as LEGACY_BASE_EXERCISES
    from exercises_extra import EXTRA_EXERCISES
    from exercises_extra_2 import EXTRA_EXERCISES_2
    from roadmap_content import ROADMAP_DATA as LEGACY_ROADMAP_DATA

TASKS_FROM_ROOT = set(range(1, 28))
ROOT_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT_DIR / "content"
CODE_TASKS = {2, 5, 6, 8, 12, 13, 14, 15, 16, 17, 19, 20, 21, 23, 24, 25, 26, 27}

ALLOWED_SOURCES = {"fipi", "reshu", "author", "mixed"}
ALLOWED_EXERCISE_MODES = {"training", "prototype"}
ALLOWED_DIFFICULTY_STAGES = {"basic", "medium", "exam", "exam_plus"}
ALLOWED_CODE_STEPS = {"fragments", "fill_gaps", "full_code"}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_source(value: Any) -> str:
    source = str(value or "").strip().lower()
    return source if source in ALLOWED_SOURCES else "mixed"


def _difficulty_stage_from_difficulty(difficulty: Any) -> str:
    value = str(difficulty or "").strip().lower()
    if value == "easy":
        return "basic"
    if value == "hard":
        return "exam"
    return "medium"


def _exercise_mode_from_stage(stage: str) -> str:
    return "prototype" if stage in {"exam", "exam_plus"} else "training"


def _code_step_for_exercise(exercise: dict[str, Any]) -> str:
    raw = str(exercise.get("code_step", "")).strip().lower()
    if raw in ALLOWED_CODE_STEPS:
        return raw
    difficulty = str(exercise.get("difficulty", "")).strip().lower()
    if difficulty == "easy":
        return "fragments"
    if difficulty == "hard":
        return "full_code"
    return "fill_gaps"


def _normalize_hints(exercise: dict[str, Any]) -> list[str]:
    raw_hints = exercise.get("hints")
    hints = [str(item).strip() for item in (raw_hints or []) if str(item).strip()]

    if not hints and exercise.get("hint_after_first_error"):
        hints.append(str(exercise["hint_after_first_error"]).strip())

    if len(hints) == 1:
        hints.append("Проверьте граничные случаи и формат вывода.")
    if len(hints) == 2:
        hints.append("Сверьте шаги решения с полным разбором и исправьте ключевую ошибку.")
    if len(hints) == 0:
        hints = [
            "Сначала зафиксируйте, какие данные из условия действительно нужны.",
            "Разделите задачу на шаги и проверьте промежуточный результат.",
            "Сравните решение с разбором и исправьте место, где ломается логика.",
        ]
    return hints[:3]


def _normalize_code_tests(exercise: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tests = exercise.get("tests") or exercise.get("test_cases") or []
    open_tests: list[dict[str, Any]] = []
    hidden_tests: list[dict[str, Any]] = []

    for test in tests:
        if not isinstance(test, dict):
            continue
        normalized = {
            "input": str(test.get("input", "")),
            "output": str(test.get("output", test.get("expected_output", ""))),
            "is_public": bool(test.get("is_public", True)),
        }
        if normalized["is_public"]:
            open_tests.append(normalized)
        else:
            hidden_tests.append(normalized)

    return open_tests, hidden_tests


def _normalize_theory_item(item: dict[str, Any], task_number: int) -> dict[str, Any]:
    normalized = dict(item)
    normalized["task_number"] = int(normalized.get("task_number", task_number))
    normalized["source"] = _normalize_source(normalized.get("source"))
    normalized["source_visibility"] = str(normalized.get("source_visibility", "subtle")).strip() or "subtle"
    normalized["difficulty_stage"] = str(normalized.get("difficulty_stage", "")).strip().lower()
    if normalized["difficulty_stage"] not in ALLOWED_DIFFICULTY_STAGES:
        normalized["difficulty_stage"] = _difficulty_stage_from_difficulty(normalized.get("difficulty"))
    normalized.setdefault("media", [])
    normalized.setdefault("files", [])
    return normalized


def _normalize_exercise_item(exercise: dict[str, Any], task_number: int) -> dict[str, Any]:
    item = dict(exercise)
    item["task_number"] = int(item.get("task_number", task_number))
    item["source"] = _normalize_source(item.get("source"))
    item["source_visibility"] = str(item.get("source_visibility", "subtle")).strip() or "subtle"

    stage = str(item.get("difficulty_stage", "")).strip().lower()
    if stage not in ALLOWED_DIFFICULTY_STAGES:
        stage = _difficulty_stage_from_difficulty(item.get("difficulty"))
    item["difficulty_stage"] = stage

    mode = str(item.get("exercise_mode", "")).strip().lower()
    if mode not in ALLOWED_EXERCISE_MODES:
        mode = _exercise_mode_from_stage(stage)
    item["exercise_mode"] = mode

    attempt_policy = item.get("attempt_policy") if isinstance(item.get("attempt_policy"), dict) else {}
    item["attempt_policy"] = {
        "max_wrong_before_solution": int(attempt_policy.get("max_wrong_before_solution", 3)),
        "auto_retry_in_lesson_end": bool(attempt_policy.get("auto_retry_in_lesson_end", True)),
    }

    item["hints"] = _normalize_hints(item)
    item["hint_after_first_error"] = item["hints"][0]

    if item.get("exercise_type") == "code":
        item["code_step"] = _code_step_for_exercise(item)
        item["evaluation"] = "tests"
        open_tests, hidden_tests = _normalize_code_tests(item)
        item["tests_open"] = open_tests
        item["tests_hidden"] = hidden_tests
        if "tests" not in item:
            item["tests"] = open_tests + hidden_tests
        item["acceptance"] = str(item.get("acceptance", "output_first")).strip() or "output_first"
    else:
        item.setdefault("evaluation", "answer")
        item.setdefault("acceptance", "exact_match")

    item.setdefault("media", [])
    item.setdefault("files", [])
    return item


def _build_content_registry(
    theory_items: list[dict[str, Any]],
    exercise_items: list[dict[str, Any]],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []

    def collect(resource_value: Any, *, owner_type: str, owner_id: str, field_name: str) -> None:
        if isinstance(resource_value, str):
            candidates = [resource_value]
        elif isinstance(resource_value, list):
            candidates = [str(item) for item in resource_value if str(item).strip()]
        else:
            candidates = []

        for candidate in candidates:
            rel_path = candidate.strip()
            if not rel_path:
                continue
            absolute_path = (CONTENT_DIR / rel_path).resolve()
            exists = absolute_path.exists()
            entries.append(
                {
                    "owner_type": owner_type,
                    "owner_id": owner_id,
                    "field": field_name,
                    "relative_path": rel_path,
                    "exists": exists,
                }
            )

    for theory in theory_items:
        owner_id = f"task_{int(theory.get('task_number', 0)):02d}"
        collect(theory.get("media"), owner_type="theory", owner_id=owner_id, field_name="media")
        collect(theory.get("files"), owner_type="theory", owner_id=owner_id, field_name="files")

    for exercise in exercise_items:
        owner_id = str(exercise.get("exercise_id", ""))
        collect(exercise.get("media"), owner_type="exercise", owner_id=owner_id, field_name="media")
        collect(exercise.get("files"), owner_type="exercise", owner_id=owner_id, field_name="files")

    missing_count = sum(1 for entry in entries if not entry["exists"])
    return {
        "entries": entries,
        "total": len(entries),
        "missing": missing_count,
        "ok": missing_count == 0,
    }


def _load_root_theory() -> list[dict[str, Any]]:
    theory_items: list[dict[str, Any]] = []
    for task_number in sorted(TASKS_FROM_ROOT):
        path = CONTENT_DIR / "theory" / f"task{task_number:02d}.json"
        if not path.exists():
            return []
        payload = _load_json(path)
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid theory payload in {path}")
        theory_items.append(_normalize_theory_item(payload, task_number))
    return theory_items


def _load_root_exercises() -> list[dict[str, Any]]:
    exercise_items: list[dict[str, Any]] = []
    for task_number in sorted(TASKS_FROM_ROOT):
        path = CONTENT_DIR / "tasks" / f"task{task_number:02d}" / "lesson_01.json"
        if not path.exists():
            return []
        payload = _load_json(path)
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid lesson payload in {path}")
        exercises = payload.get("exercises")
        if not isinstance(exercises, list):
            raise ValueError(f"Invalid exercises list in {path}")
        for exercise in exercises:
            if not isinstance(exercise, dict):
                raise ValueError(f"Invalid exercise entry in {path}")
            exercise_items.append(_normalize_exercise_item(exercise, task_number))
    return exercise_items


def _load_root_roadmap() -> list[dict[str, Any]] | None:
    path = CONTENT_DIR / "roadmap" / "roadmap.json"
    if not path.exists():
        return None
    payload = _load_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"Invalid roadmap payload in {path}")
    return payload


def _merge_theory(
    root_theory: list[dict[str, Any]],
    legacy_theory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not root_theory:
        return legacy_theory
    legacy_tail = [item for item in legacy_theory if int(item.get("task_number", 0)) not in TASKS_FROM_ROOT]
    return sorted(root_theory + legacy_tail, key=lambda item: int(item["task_number"]))


def _merge_exercises(
    root_exercises: list[dict[str, Any]],
    legacy_exercises: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not root_exercises:
        return legacy_exercises
    legacy_tail = [item for item in legacy_exercises if int(item.get("task_number", 0)) not in TASKS_FROM_ROOT]
    merged = root_exercises + legacy_tail
    return sorted(merged, key=lambda item: (int(item.get("task_number", 0)), str(item.get("exercise_id", ""))))


LEGACY_EXERCISES_DATA = LEGACY_BASE_EXERCISES + EXTRA_EXERCISES + EXTRA_EXERCISES_2
ROOT_THEORY_DATA = _load_root_theory()
ROOT_EXERCISES_DATA = _load_root_exercises()
ROOT_ROADMAP_DATA = _load_root_roadmap()

THEORY_DATA = _merge_theory(ROOT_THEORY_DATA, LEGACY_THEORY_DATA)
EXERCISES_DATA = _merge_exercises(ROOT_EXERCISES_DATA, LEGACY_EXERCISES_DATA)
ROADMAP_DATA = ROOT_ROADMAP_DATA if ROOT_ROADMAP_DATA else LEGACY_ROADMAP_DATA
CONTENT_REGISTRY = _build_content_registry(THEORY_DATA, EXERCISES_DATA)

__all__ = ["THEORY_DATA", "EXERCISES_DATA", "ROADMAP_DATA", "CONTENT_REGISTRY"]
