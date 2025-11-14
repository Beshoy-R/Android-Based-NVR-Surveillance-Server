# recorder/ffmpeg_runner.py
# spawns FFmpeg to record continuous segments and hands them to StorageManager
# configurable: record_source (rtsp/URL/device), segment length

import os
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import signal
import uuid

class RecorderController:
    """
    Minimal controller that records into temp segment files using FFmpeg's segment muxer (or timelapse)
    and then calls StorageManager.store_segment for each closed file.
    """

    def __init__(self, storage_manager, log_dir: Path = None, config: dict = None):
        self.storage = storage_manager
        self.log_dir = Path(log_dir) if log_dir else None
        self.config = {
            "source": os.environ.get("NVR_SOURCE", "rtsp://camera-link/stream1"),
            "segment_seconds": int(os.environ.get("NVR_SEGMENT_SEC", "60")),  # default 60s
            "tmp_dir": str(Path("/tmp") / "nvr_segments"),
            "video_codec": "copy",  # or h264_omx / libx264 depending on device
            **(config or {})
        }
        Path(self.config["tmp_dir"]).mkdir(parents=True, exist_ok=True)
        self._proc = None
        self._monitor_thread = None
        self._stop_flag = threading.Event()

    def is_running(self):
        return self._proc is not None and self._proc.poll() is None

    def start(self):
        if self.is_running():
            return
        self._stop_flag.clear()
        self._monitor_thread = threading.Thread(target=self._run_ffmpeg_loop, daemon=True)
        self._monitor_thread.start()

    def stop(self):
        self._stop_flag.set()
        if self._proc:
            try:
                self._proc.send_signal(signal.SIGINT)
            except Exception:
                self._proc.terminate()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)

    def _run_ffmpeg_loop(self):
        """
        Uses segment muxer to create fixed-length files then moves them.
        Example ffmpeg command:
        ffmpeg -i <source> -c:v copy -f segment -segment_time 60 -reset_timestamps 1 tmp/out%03d.mp4
        """
        tmp_dir = Path(self.config["tmp_dir"])
        segment_time = int(self.config["segment_seconds"])
        src = self.config["source"]
        # create a random prefix to avoid collisions across runs
        prefix = uuid.uuid4().hex[:8]
        out_pattern = str(tmp_dir / f"{prefix}_%03d.mp4")
        cmd = [
            "ffmpeg",
            "-hide_banner", "-loglevel", "info",
            "-i", src,
            "-c:v", self.config.get("video_codec", "copy"),
            "-c:a", "aac",
            "-f", "segment",
            "-segment_time", str(segment_time),
            "-reset_timestamps", "1",
            out_pattern
        ]
        if self.log_dir:
            log_file = self.log_dir / f"ffmpeg_{prefix}.log"
            lf = open(str(log_file), "ab")
        else:
            lf = subprocess.DEVNULL

        # spawn ffmpeg
        self._proc = subprocess.Popen(cmd, stdout=lf, stderr=lf)
        try:
            last_index = -1
            while not self._stop_flag.is_set():
                # look for segment files
                files = sorted([p for p in tmp_dir.iterdir() if p.name.startswith(prefix) and p.suffix == ".mp4"])
                # for every file not yet processed, move it into storage
                for f in files:
                    idx_part = f.stem.split("_")[-1]
                    try:
                        idx = int(idx_part)
                    except ValueError:
                        idx = None
                    if idx is None:
                        continue
                    if idx > last_index:
                        # compute start/end based on file mtime and segment_time - approximate
                        end_ts = datetime.utcfromtimestamp(f.stat().st_mtime)
                        start_ts = end_ts - timedelta(seconds=segment_time)
                        # move file
                        # StorageManager.store_segment expects a path that will be moved
                        try:
                            rec_id = self.storage.store_segment(str(f), start_ts, end_ts)
                        except Exception as e:
                            # if storage fails, leave file; wait and retry later
                            print("Storage error:", e)
                            continue
                        last_index = idx
                time.sleep(1)
            # on stop: terminate ffmpeg gracefully
            if self._proc and self._proc.poll() is None:
                self._proc.send_signal(signal.SIGINT)
                try:
                    self._proc.wait(timeout=5)
                except Exception:
                    self._proc.terminate()
        finally:
            if lf not in (None, subprocess.DEVNULL):
                try:
                    lf.close()
                except Exception:
                    pass
            self._proc = None
