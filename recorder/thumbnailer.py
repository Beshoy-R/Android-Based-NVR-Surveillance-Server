# recorder/thumbnailer.py
# simple ffmpeg-based thumbnailer. generates 1-frame thumbnails at 3 seconds into clip (or middle)

import subprocess
from pathlib import Path
from datetime import datetime

def generate_thumbnail(video_path: str, out_dir: str, rec_id: int, at_seconds: float = None):
    video = Path(video_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    thumb_path = out / f"{rec_id}.jpg"
    # choose seek time: if at_seconds given use it, otherwise try 3s
    seek = at_seconds if at_seconds is not None else 3
    # If file shorter than seek, ffmpeg will still try; it's fine.
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(seek),
        "-i", str(video),
        "-vframes", "1",
        "-q:v", "3",
        str(thumb_path)
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(thumb_path)
    except Exception as e:
        # best-effort fallback: try at 0s
        try:
            cmd2 = ["ffmpeg", "-y", "-ss", "0", "-i", str(video), "-vframes", "1", "-q:v", "3", str(thumb_path)]
            subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return str(thumb_path)
        except Exception:
            return None
