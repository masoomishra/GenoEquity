"""SQLite cache layer for API responses."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

DEFAULT_DB_PATH = Path("data/cache.sqlite")


class Cache:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )

    def get(self, key: str, ttl_seconds: Optional[int] = None) -> Optional[Any]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT payload, created_at FROM cache WHERE key = ?", (key,)).fetchone()
        if not row:
            return None
        payload, created_at = row
        if ttl_seconds is not None and time.time() - created_at > ttl_seconds:
            return None
        return json.loads(payload)

    def set(self, key: str, payload: Any) -> None:
        data = json.dumps(payload)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, payload, created_at) VALUES (?, ?, ?)",
                (key, data, time.time()),
            )
