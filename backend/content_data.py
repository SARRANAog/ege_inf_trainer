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


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_root_theory() -> list[dict[str, Any]]:
    theory_items: list[dict[str, Any]] = []
    for task_number in sorted(TASKS_FROM_ROOT):
        path = CONTENT_DIR / "theory" / f"task{task_number:02d}.json"
        if not path.exists():
            return []
        payload = _load_json(path)
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid theory payload in {path}")
        payload["task_number"] = int(payload.get("task_number", task_number))
        theory_items.append(payload)
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
            item = exercise.copy()
            item["task_number"] = int(item.get("task_number", task_number))
            exercise_items.append(item)
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

__all__ = ["THEORY_DATA", "EXERCISES_DATA", "ROADMAP_DATA"]
