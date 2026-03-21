#!/usr/bin/env python3
"""Lightweight QA checks for tasks 1-11 content payloads."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
THEORY_DIR = CONTENT_DIR / "theory"
TASKS_DIR = CONTENT_DIR / "tasks"
ROADMAP_FILE = CONTENT_DIR / "roadmap" / "roadmap.json"

TASKS = list(range(1, 12))
CODE_TASKS = {2, 5, 6, 8}
NON_CODE_TASKS = set(TASKS) - CODE_TASKS


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_theory(errors: list[str]) -> None:
    required_fields = {"task_number", "title", "short_theory", "full_theory", "is_code_task"}
    for task_number in TASKS:
        path = THEORY_DIR / f"task{task_number:02d}.json"
        if not path.exists():
            fail(errors, f"[theory] missing file: {path}")
            continue

        payload = load_json(path)
        missing = required_fields - payload.keys()
        if missing:
            fail(errors, f"[theory] task {task_number:02d} missing fields: {sorted(missing)}")
            continue

        short_theory = str(payload.get("short_theory", "")).strip()
        full_theory = str(payload.get("full_theory", "")).strip()
        if not short_theory:
            fail(errors, f"[theory] task {task_number:02d} short_theory is empty")
        if not full_theory:
            fail(errors, f"[theory] task {task_number:02d} full_theory is empty")
        if short_theory == full_theory:
            fail(errors, f"[theory] task {task_number:02d} short/full theory are identical")

        section_alternatives = [
            ("## Базовые определения", "## Core Definitions"),
            ("## Нужные микротемы", "## Required Microtopics"),
            ("## Пошаговая логика решения", "## Step-by-Step Strategy"),
            ("## Типичные ошибки", "## Common Mistakes"),
            ("## Подробный пример", "## Detailed Example"),
        ]
        for ru_section, en_section in section_alternatives:
            if ru_section not in full_theory and en_section not in full_theory:
                fail(
                    errors,
                    f"[theory] task {task_number:02d} missing required section "
                    f"(expected one of: {ru_section!r}, {en_section!r})",
                )

        if task_number in CODE_TASKS and "## Python-подход" not in full_theory and "## Python Workflow" not in full_theory:
            fail(errors, f"[theory] task {task_number:02d} must include Python section")


def validate_roadmap(errors: list[str]) -> None:
    if not ROADMAP_FILE.exists():
        fail(errors, f"[roadmap] missing file: {ROADMAP_FILE}")
        return
    payload = load_json(ROADMAP_FILE)
    if not isinstance(payload, list):
        fail(errors, "[roadmap] payload must be a list")
        return
    covered = set()
    for stage in payload:
        covered.update(stage.get("tasks", []))
    missing = [task for task in TASKS if task not in covered]
    if missing:
        fail(errors, f"[roadmap] tasks 1-11 not fully covered, missing: {missing}")


def validate_lesson(errors: list[str], task_number: int) -> None:
    path = TASKS_DIR / f"task{task_number:02d}" / "lesson_01.json"
    if not path.exists():
        fail(errors, f"[practice] missing file: {path}")
        return

    payload = load_json(path)
    exercises = payload.get("exercises")
    if not isinstance(exercises, list) or not exercises:
        fail(errors, f"[practice] task {task_number:02d} has empty exercises list")
        return

    if len(exercises) < 6:
        fail(errors, f"[practice] task {task_number:02d} should have >= 6 exercises for real training")

    required_fields = {
        "exercise_id",
        "task_number",
        "difficulty",
        "exercise_type",
        "answer_type",
        "title",
        "text",
        "correct_answer",
        "hints",
        "explanation",
    }
    difficulty_values = set()
    code_count = 0
    for exercise in exercises:
        missing = required_fields - exercise.keys()
        if missing:
            fail(
                errors,
                f"[practice] task {task_number:02d} exercise {exercise.get('exercise_id')} missing fields: {sorted(missing)}",
            )
            continue

        if int(exercise.get("task_number", 0)) != task_number:
            fail(
                errors,
                f"[practice] task mismatch in {exercise.get('exercise_id')}: expected {task_number}, got {exercise.get('task_number')}",
            )

        difficulty = str(exercise.get("difficulty"))
        difficulty_values.add(difficulty)
        if difficulty not in {"easy", "medium", "hard"}:
            fail(errors, f"[practice] {exercise.get('exercise_id')} has invalid difficulty: {difficulty}")

        answer_type = exercise.get("answer_type")
        if answer_type not in {"single_choice", "multiple_choice", "number"}:
            fail(errors, f"[practice] {exercise.get('exercise_id')} has unsupported answer_type: {answer_type}")

        hints = exercise.get("hints")
        if not isinstance(hints, list) or not hints:
            fail(errors, f"[practice] {exercise.get('exercise_id')} must contain non-empty hints")

        if not str(exercise.get("explanation", "")).strip():
            fail(errors, f"[practice] {exercise.get('exercise_id')} explanation is empty")

        exercise_type = exercise.get("exercise_type")
        if exercise_type == "code":
            code_count += 1
            if not str(exercise.get("code_template", "")).strip():
                fail(errors, f"[practice] {exercise.get('exercise_id')} missing code_template")
            tests = exercise.get("tests")
            if not isinstance(tests, list) or not tests:
                fail(errors, f"[practice] {exercise.get('exercise_id')} missing tests array")
            else:
                for test in tests:
                    if "input" not in test or "output" not in test:
                        fail(errors, f"[practice] {exercise.get('exercise_id')} has malformed test case: {test}")
                        break
            if "hint_after_first_error" not in exercise or not str(exercise.get("hint_after_first_error", "")).strip():
                fail(errors, f"[practice] {exercise.get('exercise_id')} missing hint_after_first_error")
            if "full_explanation" not in exercise or not str(exercise.get("full_explanation", "")).strip():
                fail(errors, f"[practice] {exercise.get('exercise_id')} missing full_explanation")

            required_nodes = exercise.get("required_nodes")
            if required_nodes is not None and not isinstance(required_nodes, list):
                fail(errors, f"[practice] {exercise.get('exercise_id')} required_nodes must be a list")

        if exercise_type != "code" and answer_type == "text":
            fail(errors, f"[practice] {exercise.get('exercise_id')} has forbidden free-text answer")

    if "easy" not in difficulty_values or "hard" not in difficulty_values:
        fail(errors, f"[practice] task {task_number:02d} should include at least easy and hard levels")

    if task_number in CODE_TASKS:
        ratio = code_count / len(exercises)
        if ratio < 0.7:
            fail(errors, f"[practice] task {task_number:02d} must be code-dominant, current ratio={ratio:.2f}")
    elif code_count > 0:
        fail(errors, f"[practice] task {task_number:02d} should not contain code exercises")


def validate_practice(errors: list[str]) -> None:
    for task_number in TASKS:
        validate_lesson(errors, task_number)


def main() -> int:
    errors: list[str] = []
    validate_roadmap(errors)
    validate_theory(errors)
    validate_practice(errors)

    if errors:
        print("QA FAILED")
        for item in errors:
            print(f"- {item}")
        return 1

    print("QA PASSED: tasks 1-11 content contracts are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
