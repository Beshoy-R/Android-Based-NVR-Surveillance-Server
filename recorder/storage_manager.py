# recorder/storage_manager.py
# handles file placement, rotation and cleanup, and indexing into sqlite
import os
from pathlib import Path
import shutil
from datetime import datetime, timedelta
import sqlite3
import psutil

from .models import Database
from .motion_detector import analyze_segment_for_motion
from .thumbnailer import generate_thumbnail

class StorageManager:
    def __init__(self, base_dir: Path, db: Database, retention_days: int = 7, thumbs_dir: str = None):
        self.base = Path(base_dir)
        self.db = db
        self.retention_days = retention_days
        self.thumbs_dir = Path(thumbs_dir) if thumbs_dir else (self.base.parent / "thumbnails")
        self.thumbs_dir.mkdir(parents=True, exist_ok=True)

    def _day_dir(self, dt: datetime):
        return self.base / dt.strftime("%Y-%m-%d")

    def store_segment(self, src_path: str, start_ts: datetime, end_ts: datetime):
        dt = start_ts
        day_dir = self._day_dir(dt)
        day_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{start_ts.strftime('%H%M%S')}_{end_ts.strftime('%H%M%S')}.mp4"
        dst = day_dir / filename
        # move the temp file into recordings dir
        shutil.move(src_path, str(dst))
        size = dst.stat().st_size
        duration = (end_ts - start_ts).total_seconds()
        # initial DB add without motion/thumbnail; we'll analyze and update
        rec_id = self.db.add_recording(filename, str(dst), start_ts.isoformat(), end_ts.isoformat(), size=size, duration=duration)
        # run lightweight motion detection (FFmpeg scene detection)
        try:
            motion = analyze_segment_for_motion(str(dst))
            if motion:
                self.db.set_motion(rec_id, True)
        except Exception as e:
            print("Motion analyze error:", e)
        # generate thumbnail (best-effort)
        try:
            thumb = generate_thumbnail(str(dst), str(self.thumbs_dir), rec_id)
            if thumb:
                self.db.set_thumbnail(rec_id, thumb)
        except Exception as e:
            print("Thumbnail error:", e)
        return rec_id

    def recordings_for_date(self, date_str):
        return self.db.list_by_date(date_str)

    def days_with_recordings(self):
        return self.db.list_days()

    def delete_recording(self, path):
        p = Path(path)
        if p.exists():
            p.unlink()
        # clean db record
        self.db.delete_by_path(path)

    def sweep_retention(self):
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        days = [d for d in self.base.iterdir() if d.is_dir()]
        for day in days:
            try:
                day_dt = datetime.strptime(day.name, "%Y-%m-%d")
            except Exception:
                continue
            if day_dt < cutoff:
                shutil.rmtree(day)
        # optionally clean DB for missing files (the Cleaner handles DB-only cleanup)

    def disk_free(self):
        usage = psutil.disk_usage(str(self.base))
        return usage.free
