# server.py
import os
import sqlite3
from flask import Flask, jsonify, send_file, request, abort, Response, make_response, stream_with_context
from flask_cors import CORS
from datetime import datetime
from pathlib import Path
import mimetypes

from recorder.storage_manager import StorageManager
from recorder.models import Database
from recorder.ffmpeg_runner import RecorderController
from recorder.cleanup import Cleaner

BASE_DIR = Path(__file__).resolve().parent
WEB_DIST = BASE_DIR / "web" / "dist"

DATA_DIR = BASE_DIR / "data" / "recordings"
DB_PATH = BASE_DIR / "data" / "nvr.db"
FFMPEG_LOG_DIR = BASE_DIR / "data" / "logs"
THUMBS_DIR = BASE_DIR / "data" / "thumbnails"

API_PORT = int(os.environ.get("NVR_API_PORT", 8080))

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FFMPEG_LOG_DIR, exist_ok=True)
os.makedirs(DB_PATH.parent, exist_ok=True)
os.makedirs(THUMBS_DIR, exist_ok=True)

app = Flask(__name__, static_folder=None)
CORS(app)

db = Database(DB_PATH)
storage = StorageManager(DATA_DIR, db, thumbs_dir=str(THUMBS_DIR))
recorder = RecorderController(storage, log_dir=FFMPEG_LOG_DIR)
cleaner = Cleaner(db, DATA_DIR, interval_seconds=3600)
cleaner.start()


import os
from flask import send_file, abort

WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "web", "dist"))

print("==== DEBUG STATIC PATHS ====")
print("WEB_ROOT =", WEB_ROOT)
print("INDEX =", os.path.join(WEB_ROOT, "index.html"))
print("============================")

@app.route("/")
def root():
    index_file = os.path.join(WEB_ROOT, "index.html")
    print("[DEBUG] Request for / ->", index_file, "Exists:", os.path.exists(index_file))
    if not os.path.exists(index_file):
        return f"index.html NOT FOUND at: {index_file}", 404
    return send_file(index_file)


@app.route("/assets/<path:filename>")
def assets(filename):
    asset_path = os.path.join(WEB_ROOT, "assets", filename)
    print("[DEBUG] Request for asset ->", asset_path, "Exists:", os.path.exists(asset_path))
    if not os.path.exists(asset_path):
        return f"Asset NOT FOUND at: {asset_path}", 404
    return send_file(asset_path)


# ========== BYTE-RANGE STREAMING HELPERS ==========
def _range_response(path, request):
    file_size = os.path.getsize(path)
    range_header = request.headers.get("Range")

    if not range_header:
        return send_file(path, as_attachment=False)

    try:
        range_val = range_header.split("=")[1]
        start_str, end_str = range_val.split("-")
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1
    except Exception:
        return make_response("Invalid Range header", 416)

    if start >= file_size:
        return make_response("Requested Range Not Satisfiable", 416)

    end = min(end, file_size - 1)
    chunk_size = end - start + 1

    def generate():
        with open(path, "rb") as f:
            f.seek(start)
            remaining = chunk_size
            bufsize = 8192
            while remaining > 0:
                data = f.read(min(bufsize, remaining))
                if not data:
                    break
                remaining -= len(data)
                yield data

    response = Response(
        stream_with_context(generate()),
        status=206,
        mimetype=mimetypes.guess_type(path)[0] or "application/octet-stream"
    )
    response.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
    response.headers["Accept-Ranges"] = "bytes"
    response.headers["Content-Length"] = str(chunk_size)

    return response


# ========== API ROUTES ==========
@app.route("/api/status")
def api_status():
    return jsonify({
        "recorder_running": recorder.is_running(),
        "disk_free_bytes": storage.disk_free(),
        "recording_target": recorder.config.get("source")
    })


@app.route("/api/calendar")
def api_calendar():
    return jsonify({"days": storage.days_with_recordings()})


@app.route("/api/recordings")
def api_recordings():
    date = request.args.get("date")
    if not date:
        abort(400, "Missing date")
    return jsonify({
        "date": date,
        "recordings": storage.recordings_for_date(date)
    })


@app.route("/api/recording/<int:recording_id>/file")
def api_file(recording_id):
    rec = db.get_recording(recording_id)
    if not rec:
        abort(404)
    if not os.path.exists(rec["path"]):
        abort(404)
    return _range_response(rec["path"], request)


@app.route("/api/thumbnail/<int:recording_id>")
def api_thumbnail(recording_id):
    rec = db.get_recording(recording_id)
    if not rec:
        abort(404)
    thumb = rec.get("thumbnail_path")
    if not thumb or not os.path.exists(thumb):
        abort(404)
    return send_file(thumb, mimetype="image/jpeg")


@app.route("/api/delete/<int:recording_id>", methods=["DELETE"])
def api_delete(recording_id):
    rec = db.get_recording(recording_id)
    if not rec:
        abort(404)
    storage.delete_recording(rec["path"])
    return jsonify({"status": "deleted"})


@app.route("/api/recorder/start", methods=["POST"])
def api_start():
    if recorder.is_running():
        return jsonify({"status": "already_running"})
    recorder.start()
    return jsonify({"status": "started"})


@app.route("/api/recorder/stop", methods=["POST"])
def api_stop():
    if not recorder.is_running():
        return jsonify({"status": "not_running"})
    recorder.stop()
    return jsonify({"status": "stopped"})


@app.route("/api/search")
def api_search():
    return jsonify({
        "results": db.search(
            date_from=request.args.get("date_from"),
            date_to=request.args.get("date_to"),
            min_duration=request.args.get("min_duration"),
            max_duration=request.args.get("max_duration"),
            min_size=request.args.get("min_size"),
            max_size=request.args.get("max_size"),
            motion=request.args.get("motion"),
            limit=int(request.args.get("limit", 200)),
            offset=int(request.args.get("offset", 0)),
        )
    })


if __name__ == "__main__":
    print(f"Serving UI + API at http://0.0.0.0:{API_PORT}/")
    app.run(host="0.0.0.0", port=API_PORT)
