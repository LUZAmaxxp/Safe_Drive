# Method 2: OBS Streaming Setup Guide

This guide explains how to use OBS (Open Broadcaster Software) to stream your camera to the Safe Drive application running in Docker.

## Overview

Instead of directly accessing the camera from Docker, we'll use OBS to capture the camera and stream it to a local HTTP server. The Safe Drive application will then read from this stream.

## Prerequisites

1. **OBS Studio** installed on your Windows machine
   - Download from: https://obsproject.com/

2. **Python 3.x** installed (for the streaming server)

3. **Safe Drive application** configured for streaming mode

## Setup Steps

### Step 1: Configure Safe Drive for Streaming Mode

1. Create a `.env` file in your Safe Drive directory with these settings:

```env
# Enable streaming mode
USE_STREAM=True
STREAM_URL=http://localhost:8080/stream.mjpg
STREAM_TYPE=mjpeg

# Optional: Adjust other settings as needed
CAMERA_INDEX=0
MAX_FPS=30
```

### Step 2: Start the Streaming Server

1. Open Command Prompt or PowerShell
2. Navigate to your Safe Drive directory
3. Run the streaming server:

```bash
python streaming_server.py --port 8080 --camera 0
```

You should see:
- "Camera 0 opened successfully"
- "Streaming server started on port 8080"
- "Stream URL: http://localhost:8080/stream.mjpg"

### Step 3: Configure OBS

1. **Open OBS Studio**

2. **Add Video Capture Device**:
   - Click the + button in Sources
   - Select "Video Capture Device"
   - Name it "Webcam" and click OK
   - Select your camera from the Device dropdown
   - Set Resolution/FPS to 640x480 @ 30fps (or your preference)
   - Click OK

3. **Start the Virtual Camera**:
   - In the main OBS window, find the "Controls" dock (usually on the bottom right).
   - Click "Start Virtual Camera".

This will make your OBS scene available as a new webcam on your system, which the `streaming_server.py` can then use.

### Step 4: Alternative - Use Built-in OBS Web Server

Instead of the Python streaming server, you can use OBS's built-in web server:

1. **Enable Web Server**:
   - Go to Tools → WebSocket Server Settings
   - Check "Enable WebSocket server"
   - Set Server Port: 8080
   - Set Password (optional)
   - Click OK

2. **Install OBS Virtual Camera Plugin** (if not available):
   - Some OBS versions have this built-in
   - Go to Tools → VirtualCam
   - Click "Start" to enable virtual camera

### Step 5: Build and Run Docker Container

1. **Build the Docker image**:
```bash
docker build -t safe-drive .
```

2. **Run the container**:
```bash
docker run -it --rm -p 5000:5000 safe-drive
```

### Step 6: Start Streaming

1. **Start OBS Streaming**:
   - Click "Start Streaming" in OBS
   - You should see the stream indicator turn green

2. **Verify Stream**:
   - Open browser and go to: `http://localhost:8080/stream.mjpg`
   - You should see your camera feed

3. **Check Safe Drive**:
   - Open the Safe Drive web interface: `http://localhost:5000`
   - You should see the camera feed being processed

## Troubleshooting

### Stream Connection Issues

1. **Port Conflicts**:
   - Make sure port 8080 is not in use: `netstat -ano | findstr :8080`
   - Change port in both streaming server and .env file if needed

2. **OBS Connection Failed**:
   - Check OBS is running and streaming started
   - Verify stream URL in .env matches your setup
   - Check firewall settings

3. **Docker Can't Connect**:
   - Use `host.docker.internal` instead of `localhost` in Docker:
   ```env
   STREAM_URL=http://host.docker.internal:8080/stream.mjpg
   ```

4. **Low Frame Rate**:
   - Reduce resolution in OBS
   - Lower bitrate settings
   - Check CPU usage

### Performance Optimization

1. **Reduce Resolution**:
   - Use 320x240 for faster processing
   - Adjust in OBS Video Capture Device settings

2. **Lower FPS**:
   - Set MAX_FPS=15 in .env file
   - Adjust in OBS settings

3. **Frame Skip**:
   - Set FRAME_SKIP=2 in .env file to process every 2nd frame

## Alternative Streaming Methods

### RTSP Stream (Advanced)

For RTSP streaming, you can use:

1. **Install RTSP server**:
```bash
# Using FFmpeg
ffmpeg -f dshow -i video="Your Camera Name" -vcodec libx264 -f rtsp rtsp://localhost:8554/stream
```

2. **Update .env**:
```env
STREAM_URL=rtsp://localhost:8554/stream
STREAM_TYPE=rtsp
```

### Direct Virtual Camera (Simplest)

If OBS Virtual Camera is available:

1. Enable Virtual Camera in OBS
2. Update Docker run command to use device access:
```bash
docker run -it --rm --device="class/{e5323777-f976-4f5b-9b55-b94699c46e44}/0000" -p 5000:5000 safe-drive
```

## Verification

Once everything is running:

1. **Check logs**:
   - Streaming server: Should show "Stream connected successfully"
   - Safe Drive: Should show "Using network stream mode"

2. **Test detection**:
   - Look at camera in Safe Drive web interface
   - Move your face, close eyes, show emotions
   - Check that detection works

3. **Monitor performance**:
   - Check CPU usage in Task Manager
   - Adjust settings if needed for smooth performance