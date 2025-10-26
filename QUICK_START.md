# Quick Start Guide - Safe Drive System

This guide will help you get the Safe Drive Driver Drowsiness Detection System up and running quickly.

## Prerequisites

- Python 3.8 or higher
- Node.js 14.0 or higher
- Webcam

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Safe_Drive
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install React Dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Configure Environment (Optional)
If you want to customize settings, copy the example env file:
```bash
copy .env.example .env
# or on Linux/Mac:
# cp .env.example .env
```

Edit `.env` with your preferred settings.

## Running the Application

### Step 1: Start the Backend Server

Open a terminal and run:
```bash
python app.py
```

You should see output like:
```
Starting Safe Drive API Server...
 * Running on http://0.0.0.0:5000
```

### Step 2: Start the React Frontend

Open a **new terminal** (keep the backend running) and run:
```bash
cd frontend
npm start
```

The browser should automatically open to `http://localhost:3000`

### Step 3: Start Monitoring

1. Click the "▶️ Start Monitoring" button
2. The video stream will appear
3. Watch the status indicators for real-time driver monitoring

## Usage Tips

### Video Feed
- The left side shows live camera feed
- Frame rate is approximately 30 FPS
- Click "⏸️ Stop Monitoring" to pause

### Status Indicators
- **Green (Awake)**: Driver is alert
- **Amber (Possibly Asleep)**: Driver might be drowsy
- **Red (Asleep)**: Driver is sleeping - CRITICAL ALERT!

### Metrics Displayed
- **Emotion**: Current detected emotion (happy, sad, neutral, etc.)
- **Sleep Probability**: Percentage indicating likelihood of drowsiness
- **Sleep Status**: Main driver state (Awake/Asleep)

### Alerts
When the driver falls asleep, you'll see a pulsing red alert banner at the bottom of the status card.

## Troubleshooting

### Camera Not Detected
- Check camera permissions
- Ensure no other app is using the camera
- Try changing `CAMERA_INDEX` in `.env`

### Backend Connection Error
- Ensure backend is running on port 5000
- Check firewall settings
- Verify no conflicts with other services

### Frontend Not Loading
- Ensure `npm install` completed successfully
- Check for errors in the terminal
- Clear browser cache and reload

## Stopping the Application

1. Click "⏸️ Stop Monitoring" to stop video processing
2. Press `Ctrl+C` in the backend terminal to stop the Flask server
3. Press `Ctrl+C` in the frontend terminal to stop the React app

## Advanced: Desktop Application

If you prefer the original OpenCV desktop interface:
```bash
python main_secure.py
```

Press 'q' to quit the desktop application.

## Performance Tips

- For better performance, adjust `FRAME_SKIP` in `.env`
- Lower values = more accurate but slower
- Higher values = faster but less frequent updates

## Support

For detailed documentation, see:
- `README.md` - Main documentation
- `README_FRONTEND.md` - Frontend details
- Check `logs/app.log` for error messages

## License

MIT License

