# Safe Drive - Docker Setup with Camera Access

This project provides two methods for accessing your camera from within a Docker container for the Safe Drive application.

## Quick Start

### Method 1: Direct Camera Access (Linux only)
```bash
# Build the Docker image
docker build -t safe-drive .

# Run with direct camera access (Linux only)
docker run -it --rm --device=/dev/video0 -p 5000:5000 safe-drive
```

### Method 2: OBS Streaming (Windows/Linux)
```bash
# Build the Docker image
docker build -t safe-drive .

# Set up streaming mode
copy .env.streaming .env

# Start streaming server (on host)
python streaming_server.py

# Run Docker container
docker run -it --rm -p 5000:5000 --env-file .env safe-drive
```

Access the application at: http://localhost:5000

## Methods Comparison

| Feature | Method 1 (Direct) | Method 2 (OBS Streaming) |
|---------|-------------------|---------------------------|
| **Platform** | Linux only | Windows & Linux |
| **Setup Complexity** | Simple | Moderate |
| **Performance** | High | Good |
| **Reliability** | High | Very High |
| **Camera Compatibility** | Limited | Excellent |
| **Multiple Cameras** | Difficult | Easy |
| **Video Processing** | Direct | Stream-based |

## Method 1: Direct Camera Access

**Best for:** Linux users who want simple, direct camera access

### Steps:
1. Build Docker image: `docker build -t safe-drive .`
2. Run container: `docker run -it --rm --device=/dev/video0 -p 5000:5000 safe-drive`
3. Access: http://localhost:5000

**Limitations:**
- Linux only
- May require device permissions
- Limited camera compatibility

## Method 2: OBS Streaming (Recommended)

**Best for:** Windows users, complex camera setups, maximum compatibility

### Prerequisites:
- OBS Studio (https://obsproject.com/)
- Python 3.x
- Docker

### Quick Setup:
1. **Configure streaming mode:**
   ```bash
   copy .env.streaming .env
   ```

2. **Start streaming server:**
   ```bash
   python streaming_server.py
   ```

3. **Set up OBS:**
   - Add Video Capture Device source
   - Configure output settings
   - Start streaming to localhost:8080

4. **Run Docker container:**
   ```bash
   docker run -it --rm -p 5000:5000 --env-file .env safe-drive
   ```

### Detailed OBS Setup:
See [OBS_SETUP_GUIDE.md](OBS_SETUP_GUIDE.md) for complete instructions.

### Windows Helper Scripts:
- `run_docker_streaming.bat` - Automated Docker setup for Windows
- `run_docker_streaming.sh` - Automated Docker setup for Linux

## Configuration

### Environment Variables

Create a `.env` file with your settings:

```env
# Camera Settings
USE_STREAM=False                    # Set to True for OBS streaming
STREAM_URL=http://localhost:8080/stream.mjpg
CAMERA_INDEX=0                      # Local camera index (Method 1)

# Performance Settings
MAX_FPS=30
FRAME_SKIP=1

# Model Settings
MODEL_PATH=models/emotion_model_trained.h5
SHAPE_PREDICTOR_PATH=models/shape_predictor_68_face_landmarks.dat
```

### Testing

Test your streaming setup:
```bash
python test_streaming.py
```

## Troubleshooting

### Common Issues

**Docker build fails:**
- Ensure you have enough disk space
- Check Docker daemon is running
- Try building with `--no-cache` flag

**Camera not detected (Method 1):**
- Check camera permissions: `ls -la /dev/video*`
- Try different camera index in .env file
- Ensure camera is not in use by another application

**Stream connection failed (Method 2):**
- Verify streaming server is running: `python streaming_server.py`
- Check OBS is streaming to correct URL
- Test stream URL in browser: http://localhost:8080/stream.mjpg
- Use `host.docker.internal` instead of `localhost` in Docker

**Low performance:**
- Reduce MAX_FPS in .env file
- Increase FRAME_SKIP to process fewer frames
- Lower camera resolution in OBS settings

**Windows camera access issues:**
- Grant camera permissions to Docker Desktop
- Try Method 2 (OBS streaming) instead
- Check Windows privacy settings for camera access

### Getting Help

1. Check the logs in your terminal
2. Verify all prerequisites are installed
3. Test components individually (streaming server, OBS, Docker)
4. Review the detailed setup guides

## File Structure

```
Safe_Drive/
├── app.py                    # Main application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker image definition
├── streaming_server.py      # MJPEG streaming server (Method 2)
├── test_streaming.py        # Streaming test utility
├── run_docker_streaming.bat # Windows launcher script
├── run_docker_streaming.sh  # Linux launcher script
├── .env.streaming           # Streaming mode configuration
├── OBS_SETUP_GUIDE.md       # Detailed OBS setup instructions
└── README.md               # This file
```

## Security Notes

- Change the default SECRET_KEY in production
- Use HTTPS for external deployments
- Be cautious with camera access permissions
- Review Docker security best practices

## Performance Tips

1. **Optimize frame processing:**
   - Use FRAME_SKIP to process every Nth frame
   - Lower MAX_FPS for reduced CPU usage
   - Resize frames before processing if needed

2. **Stream optimization:**
   - Use lower resolution for better performance
   - Adjust bitrate in OBS settings
   - Consider using RTSP for lower latency

3. **Docker optimization:**
   - Use multi-stage builds (already implemented)
   - Limit container resources if needed
   - Use appropriate base image size

## Contributing

Feel free to submit issues, feature requests, or improvements to the camera access methods!