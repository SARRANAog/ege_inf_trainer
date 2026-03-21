#!/usr/bin/env python3
"""Lightweight structural/content QA for tasks 1-11."""

from __future__ import annotations

import json
import re
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

RUS_CORE_DEFINITIONS = "\u0411\u0430\u0437\u043e\u0432\u044b\u0435 \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u044f"
RUS_MICROTOPICS = "\u041d\u0443\u0436\u043d\u044b\u0435 \u043c\u0438\u043a\u0440\u043e\u0442\u0435\u043c\u044b"
RUS_STEPS = "\u041f\u043e\u0448\u0430\u0433\u043e\u0432\u0430\u044f \u043b\u043e\u0433\u0438\u043a\u0430 \u0440\u0435\u0448\u0435\u043d\u0438\u044f"
RUS_MISTAKES = "\u0422\u0438\u043f\u0438\u0447\u043d\u044b\u0435 \u043e\u0448\u0438\u0431\u043a\u0438"
RUS_EXAMPLE = "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u044b\u0439 \u043f\u0440\u0438\u043c\u0435\u0440"
RUS_PYTHON = "Python-\u043f\u043e\u0434\u0445\u043e\u0434"
RUS_ANSWER = "\u041e\u0442\u0432\u0435\u0442"

PLACEHOLDER_MARKERS = [
    "Correct answer:",
    "Rebuild the solution path",
    "Estimate result magnitude first",
    "Split solution into small steps",
    "Run one final condition check",
    "Eliminate options",
]

OPTION_LABEL_RE = re.compile(r"^[A-Za-z]\)\s*")
ANSWER_FROM_EXPLANATION_RE = re.compile(rf"{RUS_ANSWER}\s*[:=]\s*([^\n]+)")
QUESTION_RUN_RE = re.compile(r"\?{3,}")

MOJIBAKE_MARKERS = [
    "\u00c2",
    "\u00c5",
    "\u00fd",
    "\u00d0",
    "\u00d1",
    "\u0420\u040e",
    "\u0420\u045f",
    "\u0413\u0452",
    "\u0413\u2018",
    "\u0440\u045f\u201e",
    "\ufffd",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def normalize_option_text(option: str) -> str:
    cleaned = OPTION_LABEL_RE.sub("", option.strip())
    return re.sub(r"\s+", " ", cleaned).strip()


def contains_placeholder(text: str) -> bool:
    return any(marker in text for marker in PLACEHOLDER_MARKERS)


def contains_mojibake_or_question_run(text: str) -> bool:
    if QUESTION_RUN_RE.search(text):
        return True
    return any(marker in text for marker in MOJIBAKE_MARKERS)


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

        required_sections = [
            (RUS_CORE_DEFINITIONS, "Core Definitions"),
            (RUS_MICROTOPICS, "Required Microtopics"),
            (RUS_STEPS, "Step-by-Step Strategy"),
            (RUS_MISTAKES, "Common Mistakes"),
            (RUS_EXAMPLE, "Detailed Example"),
        ]
        for ru, en in required_sections:
            if ru not in full_theory and en not in full_theory:
                fail(errors, f"[theory] task {task_number:02d} missing section: {ru!r} or {en!r}")

        if task_number in CODE_TASKS and RUS_PYTHON not in full_theory and "Python Workflow" not in full_theory:
            fail(errors, f"[theory] task {task_number:02d} must include Python section")


def validate_roadmap(errors: list[str]) -> None:
    if not ROADMAP_FILE.exists():
        fail(errors, f"[roadmap] missing file: {ROADMAP_FILE}")
        return

    payload = load_json(ROADMAP_FILE)
    if not isinstance(payload, list):
        fail(errors, "[roadmap] payload must be a list")
        return

    covered_tasks: set[int] = set()
    for stage in payload:
        covered_tasks.update(stage.get("tasks", []))

    missing = [task for task in TASKS if task not in covered_tasks]
    if missing:
        fail(errors, f"[roadmap] tasks 1-11 not fully covered, missing: {missing}")


def validate_answer_consistency(errors: list[str], task_number: int, exercise: dict[str, Any]) -> None:
    exercise_id = exercise.get("exercise_id")
    answer_type = exercise.get("answer_type")
    correct_answer = exercise.get("correct_answer")
    explanation = str(exercise.get("explanation", ""))
    match = ANSWER_FROM_EXPLANATION_RE.search(explanation)
    if not match:
        return

    declared = match.group(1).strip().split(".")[0].strip()
    if answer_type == "number":
        corr = str(correct_answer).strip()
        if corr not in declared and declared not in corr:
            fail(
                errors,
                f"[practice] task {task_number:02d} {exercise_id}: "
                f"possible contradiction in explanation answer ({declared!r}) vs correct_answer ({corr!r})",
            )
    elif answer_type == "single_choice":
        if declared and declared[0].upper() in {"A", "B", "C", "D", "E", "F"}:
            if declared[0].upper() != str(correct_answer).upper():
                fail(
                    errors,
                    f"[practice] task {task_number:02d} {exercise_id}: "
                    f"possible contradiction in explanation answer ({declared!r}) vs correct_answer ({correct_answer!r})",
                )


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

    difficulty_values: set[str] = set()
    code_count = 0

    for exercise in exercises:
        exercise_id = exercise.get("exercise_id")
        missing = required_fields - exercise.keys()
        if missing:
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} missing fields: {sorted(missing)}")
            continue

        if int(exercise.get("task_number", 0)) != task_number:
            fail(
                errors,
                f"[practice] task {task_number:02d} {exercise_id}: "
                f"task_number mismatch ({exercise.get('task_number')})",
            )

        difficulty = str(exercise.get("difficulty"))
        difficulty_values.add(difficulty)
        if difficulty not in {"easy", "medium", "hard"}:
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} invalid difficulty: {difficulty}")

        answer_type = exercise.get("answer_type")
        if answer_type not in {"single_choice", "multiple_choice", "number"}:
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} unsupported answer_type: {answer_type}")

        hints = exercise.get("hints")
        if not isinstance(hints, list) or not hints or not all(str(item).strip() for item in hints):
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} invalid hints list")
        elif any(contains_placeholder(str(item)) for item in hints):
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} hints contain placeholder text")
        elif any(contains_mojibake_or_question_run(str(item)) for item in hints):
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} hints contain mojibake or suspicious question marks")

        explanation = str(exercise.get("explanation", "")).strip()
        if not explanation:
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} explanation is empty")
        elif contains_placeholder(explanation):
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} explanation contains placeholder text")
        elif contains_mojibake_or_question_run(explanation):
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} explanation contains mojibake or suspicious question marks")

        title = str(exercise.get("title", ""))
        text = str(exercise.get("text", ""))
        if contains_mojibake_or_question_run(title):
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} title contains mojibake or suspicious question marks")
        if contains_mojibake_or_question_run(text):
            fail(errors, f"[practice] task {task_number:02d} {exercise_id} text contains mojibake or suspicious question marks")

        options = exercise.get("options")
        if answer_type in {"single_choice", "multiple_choice"}:
            if not isinstance(options, list) or not options:
                fail(errors, f"[practice] task {task_number:02d} {exercise_id} requires non-empty options")
            else:
                labels = [str(item).split(")")[0].strip() for item in options]
                bodies = [normalize_option_text(str(item)) for item in options]
                if len(bodies) != len(set(bodies)):
                    fail(errors, f"[practice] task {task_number:02d} {exercise_id} has duplicate option texts")

                if answer_type == "single_choice":
                    if str(exercise.get("correct_answer")) not in labels:
                        fail(
                            errors,
                            f"[practice] task {task_number:02d} {exercise_id} single_choice correct_answer "
                            f"not found in options labels",
                        )
                else:
                    correct = exercise.get("correct_answer")
                    if not isinstance(correct, list) or not correct:
                        fail(errors, f"[practice] task {task_number:02d} {exercise_id} multiple_choice expects non-empty list")
                    else:
                        unknown = [item for item in correct if str(item) not in labels]
                        if unknown:
                            fail(
                                errors,
                                f"[practice] task {task_number:02d} {exercise_id} multiple_choice unknown labels: {unknown}",
                            )
        else:
            if isinstance(options, list) and not options:
                fail(errors, f"[practice] task {task_number:02d} {exercise_id} has empty options array")

        exercise_type = exercise.get("exercise_type")
        if exercise_type == "code":
            code_count += 1
            code_template = str(exercise.get("code_template", "")).strip()
            if not code_template:
                fail(errors, f"[practice] task {task_number:02d} {exercise_id} missing code_template")

            tests = exercise.get("tests")
            if not isinstance(tests, list) or not tests:
                fail(errors, f"[practice] task {task_number:02d} {exercise_id} missing tests")
            else:
                for test in tests:
                    if not isinstance(test, dict) or "input" not in test or "output" not in test:
                        fail(errors, f"[practice] task {task_number:02d} {exercise_id} malformed test: {test}")
                        break

            hint_after = str(exercise.get("hint_after_first_error", "")).strip()
            if not hint_after:
                fail(errors, f"[practice] task {task_number:02d} {exercise_id} missing hint_after_first_error")
            elif contains_placeholder(hint_after):
                fail(errors, f"[practice] task {task_number:02d} {exercise_id} hint_after_first_error contains placeholder text")

            full_explanation = str(exercise.get("full_explanation", "")).strip()
            if not full_explanation:
                fail(errors, f"[practice] task {task_number:02d} {exercise_id} missing full_explanation")
            elif contains_placeholder(full_explanation):
                fail(errors, f"[practice] task {task_number:02d} {exercise_id} full_explanation contains placeholder text")
            elif contains_mojibake_or_question_run(full_explanation):
                fail(errors, f"[practice] task {task_number:02d} {exercise_id} full_explanation contains mojibake or suspicious question marks")

            required_nodes = exercise.get("required_nodes")
            if required_nodes is not None and not isinstance(required_nodes, list):
                fail(errors, f"[practice] task {task_number:02d} {exercise_id} required_nodes must be list")

            if isinstance(tests, list) and tests and tests[0].get("input", "") == "":
                expected = str(tests[0].get("output", "")).strip()
                corr = str(exercise.get("correct_answer", "")).strip()
                if expected and corr and expected != corr:
                    fail(
                        errors,
                        f"[practice] task {task_number:02d} {exercise_id} mismatch: tests[0].output={expected!r}, "
                        f"correct_answer={corr!r}",
                    )

        validate_answer_consistency(errors, task_number, exercise)

    if "easy" not in difficulty_values or "hard" not in difficulty_values:
        fail(errors, f"[practice] task {task_number:02d} should include both easy and hard exercises")

    if task_number in CODE_TASKS:
        ratio = code_count / len(exercises)
        if ratio < 0.7:
            fail(errors, f"[practice] task {task_number:02d} must be code-dominant, ratio={ratio:.2f}")
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
