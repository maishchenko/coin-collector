import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path)
        try:
            with connection:
                connection.execute(
                    """CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nickname TEXT NOT NULL,
                        score INTEGER NOT NULL,
                        is_win INTEGER NOT NULL,
                        duration_ms INTEGER,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )"""
                )
                # Старые результаты сохраняются, но время для них неизвестно.
                columns = connection.execute("PRAGMA table_info(scores)").fetchall()
                if not any(column[1] == "duration_ms" for column in columns):
                    connection.execute("ALTER TABLE scores ADD COLUMN duration_ms INTEGER")
                # str.lower() поддерживает кириллицу, в отличие от SQLite LOWER().
                rows = connection.execute("SELECT id, nickname FROM scores").fetchall()
                connection.executemany(
                    "UPDATE scores SET nickname = ? WHERE id = ?",
                    [
                        (nickname.strip().lower(), score_id)
                        for score_id, nickname in rows
                        if nickname != nickname.strip().lower()
                    ],
                )
        finally:
            connection.close()

    def save_score(
        self, nickname: str, score: int, is_win: bool, duration_ms: int | None = None
    ) -> None:
        connection = sqlite3.connect(self.db_path)
        try:
            with connection:
                connection.execute(
                    """INSERT INTO scores (nickname, score, is_win, duration_ms)
                       VALUES (?, ?, ?, ?)""",
                    (nickname.strip().lower(), score, int(is_win), duration_ms),
                )
        finally:
            connection.close()

    def get_top_scores(self, limit: int = 5) -> list[tuple[str, int]]:
        connection = sqlite3.connect(self.db_path)
        try:
            return connection.execute(
                """WITH best_times AS (
                       SELECT nickname, MIN(duration_ms) AS duration_ms
                       FROM scores
                       WHERE is_win = 1 AND duration_ms IS NOT NULL
                       GROUP BY nickname
                   )
                   SELECT best.nickname, best.duration_ms
                   FROM best_times AS best
                   JOIN scores AS s ON s.nickname = best.nickname
                       AND s.duration_ms = best.duration_ms AND s.is_win = 1
                   GROUP BY best.nickname, best.duration_ms
                   ORDER BY best.duration_ms ASC, MIN(s.created_at) ASC, MIN(s.id) ASC
                   LIMIT ?""",
                (max(0, min(limit, 5)),),
            ).fetchall()
        finally:
            connection.close()
