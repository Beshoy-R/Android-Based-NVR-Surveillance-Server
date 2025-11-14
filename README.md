Android-Based NVR Surveillance Server

A lightweight Network Video Recorder (NVR) system that transforms an Android device into a fully functional surveillance server. This project uses a custom Ubuntu environment running inside Termux to provide continuous video recording, motion detection, LAN-accessible playback, and a polished web interface.

Features

Android-based server
Runs entirely on an Android phone using Termux + Ubuntu (proot), with no root required.

Continuous video recording
Uses FFmpeg to capture camera streams and organize footage by date and hour.

Motion detection
Optional detection pipeline to reduce storage usage and highlight relevant footage.

Modern web interface
LAN-accessible UI with:

Monthly calendar view

Days marked with available recordings

Video viewer with theatre-style layout

Timeline scrubbing

Playback speeds (0.5x, 1x, 2x)

Zoom controls

Auto-start on boot
Recording and server processes launch automatically when the device powers on.

Local LAN access
Access the server from any PC on the same network with:
http://<phone-ip>:8080

Optional remote access
Secure external access via Tailscale, without port forwarding.

Storage management
Automatic cleanup of old recordings based on retention settings.

System Architecture

Android device running Termux

Ubuntu (proot) environment hosting the backend

FFmpeg for camera recording

Python backend for file management and APIs

Node.js web server for the UI

SQLite for indexing recordings

REST API for fetching recordings, metadata, and timeline segments

Installation
1. Install Termux

Download the official Termux build (not Play Store).

2. Install Ubuntu (proot)
pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu

3. Install dependencies
apt update
apt install ffmpeg python3 python3-pip nodejs npm sqlite3

4. Clone the project
git clone https://github.com/yourusername/android-nvr
cd android-nvr

5. Install backend requirements
pip install -r requirements.txt

6. Install web UI dependencies
cd web
npm install
npm run build
cd ..

7. Start the server

Backend:

python3 server.py


Web UI:

node web/dist/server.js

8. Access the NVR

From any device on the same LAN:

http://<android-ip>:8080

Auto-Start Setup

You can create a Termux ~/.bashrc script or use termux-wake-lock with a boot receiver to launch the NVR automatically when the phone powers on.

Project Structure
android-nvr/
│
├── recorder/
│   ├── ffmpeg_runner.py
│   ├── scheduler.py
│   └── storage_manager.py
│
├── server/
│   ├── api.py
│   └── models.py
│
├── web/
│   ├── src/
│   └── dist/
│
├── data/
│   └── recordings/
│
└── README.md

Requirements

Android device (preferably with good thermal performance)

Termux

Minimum 2 GB free storage

Stable LAN connection

Notes

Works fine on old Android phones as long as they stay cool.

Video quality depends on camera support and FFmpeg configuration.

Tailscale is optional but extremely useful for remote access.

License

MIT License