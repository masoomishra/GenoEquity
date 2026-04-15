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
                    created_at REAL NOT NULL,
                    expires_at REAL
                )
                """
            )
            columns = {
                row[1] for row in conn.execute("PRAGMA table_info(cache)").fetchall()
            }
            if "expires_at" not in columns:
                conn.execute("ALTER TABLE cache ADD COLUMN expires_at REAL")

    def get(self, key: str, ttl_seconds: Optional[int] = None) -> Optional[Any]:
        found, payload = self.get_with_presence(key, ttl_seconds=ttl_seconds)
        if not found:
            return None
        return payload

    def get_with_presence(self, key: str, ttl_seconds: Optional[int] = None) -> tuple[bool, Any]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload, created_at, expires_at FROM cache WHERE key = ?",
                (key,),
            ).fetchone()
            if not row:
                return False, None
            payload, created_at, expires_at = row
            if expires_at is not None and time.time() > expires_at:
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                return False, None
            if ttl_seconds is not None and time.time() - created_at > ttl_seconds:
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                return False, None
            return True, json.loads(payload)

    def set(self, key: str, payload: Any, ttl_seconds: Optional[int] = None) -> None:
        data = json.dumps(payload)
        now = time.time()
        expires_at = now + ttl_seconds if ttl_seconds is not None else None
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, payload, created_at, expires_at) VALUES (?, ?, ?, ?)",
                (key, data, now, expires_at),
            )
