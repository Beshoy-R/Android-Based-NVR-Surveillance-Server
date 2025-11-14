# Android-Based NVR Surveillance Server

A lightweight Network Video Recorder (NVR) system that turns an Android device into a fully functional surveillance server. It uses a custom Ubuntu environment running inside Termux to provide continuous recording, optional motion detection, LAN playback, and a modern web interface.

## Features

### Android-based server
Runs entirely on an Android phone using Termux and Ubuntu (proot). No root required.

### Continuous video recording
Uses FFmpeg to capture camera streams and organizes footage by date and hour.

### Motion detection
Optional detection pipeline that helps reduce storage usage and highlight important events.

### Modern web interface
Accessible over LAN, offering:
- Monthly calendar view
- Days marked with available recordings
- Theatre-style video viewer
- Timeline scrubbing
- Playback speeds (0.5x, 1x, 2x)
- Zoom controls

### Auto-start on boot
The recorder and server processes launch automatically when the device powers on.

### Local LAN access
Access the server from:
```
http://<phone-ip>:8080
```

### Optional remote access
Integrates cleanly with Tailscale for secure remote access without port forwarding.

### Storage management
Automatically cleans up old recordings based on retention settings.

## System Architecture

- Android device running Termux  
- Ubuntu (proot) environment hosting the backend  
- FFmpeg for camera recording  
- Python backend for file management and APIs  
- Node.js web server for the UI  
- SQLite for indexing recordings  
- REST API for recordings, metadata, and timeline data  

## Installation

### 1. Install Termux
Download the official Termux build (not from the Play Store).

### 2. Install Ubuntu (proot)
```sh
pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu
```

### 3. Install dependencies
```sh
apt update
apt install ffmpeg python3 python3-pip nodejs npm sqlite3
```

### 4. Clone the project
```sh
git clone https://github.com/yourusername/android-nvr
cd android-nvr
```

### 5. Install backend requirements
```sh
pip install -r requirements.txt
```

### 6. Install web UI dependencies
```sh
cd web
npm install
npm run build
cd ..
```

### 7. Start the server

Backend:
```sh
python3 server.py
```

Web UI:
```sh
node web/dist/server.js
```

### 8. Access the NVR
From any device on the same LAN:
```
http://<android-ip>:8080
```

## Auto-Start Setup
You can use a Termux `~/.bashrc` script or a boot receiver with `termux-wake-lock` to launch the NVR automatically when the device powers on.

## Project Structure
```
android-nvr/
├── recorder/
│   ├── ffmpeg_runner.py
│   ├── scheduler.py
│   └── storage_manager.py
├── server/
│   ├── api.py
│   └── models.py
├── web/
│   ├── src/
│   └── dist/
├── data/
│   └── recordings/
└── README.md
```

## Requirements
- Android device (preferably thermally stable)
- Termux
- Minimum 2 GB free storage
- Reliable LAN connection

## Notes
- Works well on older Android phones if heat is managed.
- Video quality depends on camera support and FFmpeg settings.
- Tailscale is optional but highly recommended for remote access.

## License
MIT License
