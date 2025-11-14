# recorder/motion_detector.py
# Very lightweight FFmpeg scene-detection-based motion heuristic.
# It runs ffmpeg over the clip with select=gt(scene,THRESH) filter and parses stderr for pts_time lines.
# If any scene-change frames are found above threshold, we consider this clip to contain motion.

import subprocess
import re
from pathlib import Path

# tune this threshold: lower = more sensitive
DEFAULT_SCENE_THRESHOLD = 0.003  # small motion sensitivity

_scene_regex = re.compile(r"pts_time:(\d+(\.\d+)?)")

def analyze_segment_for_motion(path: str, threshold: float = DEFAULT_SCENE_THRESHOLD, max_frames_check:int=500):
    """
    Returns True if ffmpeg detect scene changes above threshold.
    Uses ffmpeg -filter:v "select='gt(scene,threshold)'" -an -f null -
    Parses ffmpeg stderr for 'pts_time:' occurrences.
    """
    p = Path(path)
    if not p.exists():
        return False
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "info",
        "-i", str(p),
        "-vf", f"select='gt(scene,{threshold})'",
        "-an",
        "-f", "null", "-"
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        return False
    # ffmpeg outputs selected frame info in stderr; search for pts_time=
    hits = _scene_regex.findall(stderr or "")
    if len(hits) > 0:
        # optionally limit false positives by checking number of hits
        return True
    return False
