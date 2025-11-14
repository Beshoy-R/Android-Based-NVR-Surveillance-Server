#!/usr/bin/env bash
# start.sh - launch NVR backend quickly (for Termux/proot)
# run from project root: ./start.sh

export NVR_API_PORT=8080
# set to your actual camera source; can be RTSP or device
export NVR_SOURCE="${NVR_SOURCE:-rtsp://camera-link/stream1}"
export NVR_SEGMENT_SEC="${NVR_SEGMENT_SEC:-60}"

# ensure virtualenv optionally
python3 -m pip install -r requirements.txt

# run api in background (replace with gunicorn/uvicorn for production)
nohup python3 server.py > data/logs/server.out 2>&1 &
echo "server started"
