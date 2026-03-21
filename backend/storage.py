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
                CREATE INDEX IF NOT EXISTS idx_attempts_timestamp ON attempts(timestamp DESC);

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

    def _content_signature(
        self,
        theory_data: list[dict[str, Any]],
        exercises_data: list[dict[str, Any]],
        roadmap_data: list[dict[str, Any]],
    ) -> str:
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
        task_number: Optional[int] = None,
        difficulty: Optional[str] = None,
        exercise_type: Optional[str] = None,
        *,
        only_objective: bool = False,
        only_code: bool = False,
    ) -> list[dict[str, Any]]:
        query = "SELECT data_json FROM exercises WHERE 1=1"
        params: list[Any] = []

        if task_number is not None:
            query += " AND task_number = ?"
            params.append(task_number)
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        if exercise_type:
            query += " AND exercise_type = ?"
            params.append(exercise_type)
        if only_objective:
            query += " AND (answer_type IN ('single_choice', 'multiple_choice', 'number') OR exercise_type = 'code')"
        if only_code:
            query += " AND exercise_type = 'code'"

        query += " ORDER BY task_number ASC, exercise_id ASC"
        return self._fetch_many_docs(query, tuple(params))

    def list_exercises_for_task_limited(
        self,
        task_number: int,
        limit: int,
        *,
        only_objective: bool = False,
        only_code: bool = False,
    ) -> list[dict[str, Any]]:
        query = "SELECT data_json FROM exercises WHERE task_number = ?"
        params: list[Any] = [task_number]
        if only_objective:
            query += " AND (answer_type IN ('single_choice', 'multiple_choice', 'number') OR exercise_type = 'code')"
        if only_code:
            query += " AND exercise_type = 'code'"
        query += f" ORDER BY exercise_id ASC LIMIT {int(limit)}"
        return self._fetch_many_docs(query, tuple(params))

    def get_exercise(self, exercise_id: str) -> Optional[dict[str, Any]]:
        return self._fetch_one_doc("SELECT data_json FROM exercises WHERE exercise_id = ?", (exercise_id,))

    def save_progress(self, progress: dict[str, Any]) -> None:
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

    def add_attempt(self, attempt: dict[str, Any]) -> None:
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

    def list_attempts(self, task_number: int, limit: int = 20) -> list[dict[str, Any]]:
        query = f"SELECT data_json FROM attempts WHERE task_number = ? ORDER BY timestamp DESC LIMIT {int(limit)}"
        return self._fetch_many_docs(query, (task_number,))

    def list_recent_attempts(self, limit: int = 120) -> list[dict[str, Any]]:
        query = f"SELECT data_json FROM attempts ORDER BY timestamp DESC LIMIT {int(limit)}"
        return self._fetch_many_docs(query)

    def count_attempts(self, *, correct: Optional[bool] = None) -> int:
        query = "SELECT COUNT(*) AS c FROM attempts"
        params: tuple[Any, ...] = ()
        if correct is not None:
            query += " WHERE correct = ?"
            params = (1 if correct else 0,)
        with self._lock, self._connect() as conn:
            row = conn.execute(query, params).fetchone()
        return int(row["c"]) if row else 0

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

    def save_active_weekly_review(self, review: dict[str, Any]) -> None:
        self._execute(
            """
            UPDATE weekly_reviews
            SET status = ?, started_at = ?, completed_at = ?, data_json = ?
            WHERE id = (
                SELECT id FROM weekly_reviews
                WHERE status = 'active'
                ORDER BY started_at DESC
                LIMIT 1
            )
            """,
            (
                review.get("status", "active"),
                review.get("started_at"),
                review.get("completed_at"),
                _json_dumps(review),
            ),
        )

    def list_completed_weekly_reviews(self, limit: int = 10) -> list[dict[str, Any]]:
        query = f"SELECT data_json FROM weekly_reviews WHERE status = 'completed' ORDER BY completed_at DESC LIMIT {int(limit)}"
        return self._fetch_many_docs(query)

    def get_active_mock_exam(self) -> Optional[dict[str, Any]]:
        return self._fetch_one_doc(
            "SELECT data_json FROM mock_exams WHERE status IN ('active', 'paused') ORDER BY started_at DESC LIMIT 1"
        )

    def list_completed_mock_exams(self, limit: int = 10) -> list[dict[str, Any]]:
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

    def count_mock_exams(self, *, status: Optional[str] = None) -> int:
        query = "SELECT COUNT(*) AS c FROM mock_exams"
        params: tuple[Any, ...] = ()
        if status is not None:
            query += " WHERE status = ?"
            params = (status,)
        with self._lock, self._connect() as conn:
            row = conn.execute(query, params).fetchone()
        return int(row["c"]) if row else 0

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
