# recorder/models.py
# sqlite wrapper for recordings metadata, with extra fields for motion and thumbnail

import sqlite3
from pathlib import Path
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = str(db_path)
        self._ensure_tables()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _ensure_tables(self):
        conn = self._conn()
        cur = conn.cursor()
        # Add the motion_detected and thumbnail_path columns
        cur.execute("""
        CREATE TABLE IF NOT EXISTS recordings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE,
            start_ts TEXT,
            end_ts TEXT,
            size_bytes INTEGER,
            duration_seconds REAL,
            motion_detected INTEGER DEFAULT 0,
            thumbnail_path TEXT DEFAULT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()

    def add_recording(self, filename, path, start_ts=None, end_ts=None, size=0, duration=0, motion=False, thumbnail_path=None):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO recordings (filename, path, start_ts, end_ts, size_bytes, duration_seconds, motion_detected, thumbnail_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (filename, path, start_ts, end_ts, size, duration, int(bool(motion)), thumbnail_path))
        conn.commit()
        rec_id = cur.lastrowid
        conn.close()
        return rec_id

    def set_motion(self, rec_id, motion=True):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("UPDATE recordings SET motion_detected=? WHERE id=?", (int(bool(motion)), rec_id))
        conn.commit()
        conn.close()

    def set_thumbnail(self, rec_id, thumbnail_path):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("UPDATE recordings SET thumbnail_path=? WHERE id=?", (thumbnail_path, rec_id))
        conn.commit()
        conn.close()

    def get_recording(self, rec_id):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT id, filename, path, start_ts, end_ts, size_bytes, duration_seconds, motion_detected, thumbnail_path FROM recordings WHERE id = ?", (rec_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        keys = ["id", "filename", "path", "start_ts", "end_ts", "size_bytes", "duration_seconds", "motion_detected", "thumbnail_path"]
        return dict(zip(keys, row))

    def list_by_date(self, date_str):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT id, filename, path, start_ts, end_ts, size_bytes, duration_seconds, motion_detected, thumbnail_path FROM recordings WHERE DATE(created_at)=? ORDER BY start_ts", (date_str,))
        rows = cur.fetchall()
        conn.close()
        keys = ["id", "filename", "path", "start_ts", "end_ts", "size_bytes", "duration_seconds", "motion_detected", "thumbnail_path"]
        return [dict(zip(keys, r)) for r in rows]

    def list_days(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT DATE(created_at) as day, COUNT(*) as cnt FROM recordings GROUP BY day ORDER BY day DESC")
        rows = cur.fetchall()
        conn.close()
        return [{"day": r[0], "count": r[1]} for r in rows]

    def delete_by_path(self, path):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM recordings WHERE path=?", (path,))
        conn.commit()
        conn.close()

    def search(self, date_from=None, date_to=None, min_duration=None, max_duration=None, min_size=None, max_size=None, motion=None, limit=200, offset=0):
        q = "SELECT id, filename, path, start_ts, end_ts, size_bytes, duration_seconds, motion_detected, thumbnail_path FROM recordings WHERE 1=1"
        params = []
        if date_from:
            q += " AND DATE(start_ts) >= ?"
            params.append(date_from)
        if date_to:
            q += " AND DATE(start_ts) <= ?"
            params.append(date_to)
        if min_duration is not None:
            q += " AND duration_seconds >= ?"
            params.append(min_duration)
        if max_duration is not None:
            q += " AND duration_seconds <= ?"
            params.append(max_duration)
        if min_size is not None:
            q += " AND size_bytes >= ?"
            params.append(min_size)
        if max_size is not None:
            q += " AND size_bytes <= ?"
            params.append(max_size)
        if motion is not None:
            q += " AND motion_detected = ?"
            params.append(1 if motion else 0)
        q += " ORDER BY start_ts DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        conn = self._conn()
        cur = conn.cursor()
        cur.execute(q, tuple(params))
        rows = cur.fetchall()
        conn.close()
        keys = ["id", "filename", "path", "start_ts", "end_ts", "size_bytes", "duration_seconds", "motion_detected", "thumbnail_path"]
        return [dict(zip(keys, r)) for r in rows]
