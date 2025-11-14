# recorder/cleanup.py
# background cleanup utility: removes DB entries for missing files, optional orphan detection

import threading
import time
from pathlib import Path

class Cleaner:
    def __init__(self, db, base_recordings_dir: Path, interval_seconds: int = 3600):
        self.db = db
        self.base = Path(base_recordings_dir)
        self.interval = interval_seconds
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)

    def _run(self):
        while not self._stop.is_set():
            try:
                self._sweep_once()
            except Exception as e:
                # swallow errors, log to stdout
                print("Cleaner error:", e)
            self._stop.wait(self.interval)

    def _sweep_once(self):
        # iterate DB records and remove entries whose files are missing
        records = self.db.search(limit=10000, offset=0)  # small projects only; adjust for scale
        for r in records:
            p = Path(r["path"])
            if not p.exists():
                print("Cleaner: file missing, removing DB record:", r["path"])
                self.db.delete_by_path(r["path"])
