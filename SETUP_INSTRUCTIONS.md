# Safe Drive - Complete Setup Instructions

This document provides complete step-by-step instructions for setting up and running the Safe Drive Driver Drowsiness Detection System with React frontend.

## 🎯 What You're Building

A complete web-based driver monitoring system that:
- Captures real-time video from your webcam
- Detects facial emotions using AI/ML
- Monitors eye closure to detect drowsiness
- Displays results in a beautiful React UI
- Provides real-time status updates

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Python 3.8+** installed
   ```bash
   python --version  # Should show 3.8 or higher
   ```

2. **Node.js 14+ and npm** installed
   ```bash
   node --version
   npm --version
   ```

3. **A webcam** connected to your computer

4. **Required Model Files**:
   - Download shape predictor: https://dlib.net/files/shape_predictor_68_face_landmarks.dat
   - Place it in: `models/shape_predictor_68_face_landmarks.dat`

## 🚀 Installation Process

### Step 1: Install Python Dependencies

```bash
# Navigate to project directory
cd C:\Users\pc\Desktop\Safe_Drive

# Install requirements
pip install -r requirements.txt
```

**Important**: Installation may take a while. The dependencies include:
- OpenCV for video processing
- TensorFlow for ML models
- FER for emotion recognition
- Flask for web API
- dlib for facial landmarks

**If you encounter issues with dlib installation:**

On Windows, you might need to install Visual Studio Build Tools first.

Alternative: Use pre-built wheel
```bash
pip install dlib
```

### Step 2: Install React Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install Node modules
npm install

# Return to root directory
cd ..
```

This installs:
- React 18
- Axios for API calls
- react-scripts for development

### Step 3: Download Required Model File (if not already present)

The eye closure detection requires the dlib shape predictor file.

**Option A: Automatic Download**

Update your `.env` file to include:
```
Dlib_URL=https://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
```

Then create a script to download and extract it.

**Option B: Manual Download**

1. Go to: https://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
2. Download the file
3. Extract it to: `models/shape_predictor_68_face_landmarks.dat`

## ▶️ Running the Application

### Terminal 1: Start Backend Server

```bash
python app.py
```

You should see:
```
Starting Safe Drive API Server...
 * Running on http://0.0.0.0:5000
```

**Common Issues:**
- Port 5000 already in use: Change port in app.py or kill the process using it
- Camera not found: Check if camera is connected and not used by another app
- Module import errors: Make sure all pip packages installed correctly

### Terminal 2: Start React Frontend

```bash
cd frontend
npm start
```

Browser should automatically open to `http://localhost:3000`

**Common Issues:**
- Port 3000 already in use: React will ask to use another port
- npm start fails: Run `npm install` again in frontend directory
- Module not found: Delete `node_modules` folder and run `npm install`

## 🎮 Using the Application

### 1. Start Monitoring

Click the **"▶️ Start Monitoring"** button on the web interface.

This will:
- Initialize the camera
- Start emotion detection
- Begin eye closure monitoring
- Start streaming video to your browser

### 2. Understanding the Display

**Left Side - Video Stream**
- Shows live camera feed
- Updates in real-time (~30 FPS)
- Center the driver in the frame for best results

**Right Side - Status Panel**

**Status Card:**
- 🎯 **Sleep Status**: Main indicator (Awake/Asleep/Possibly Asleep)
- Color changes based on state:
  - 🟢 Green = Awake (good)
  - 🟡 Amber = Possibly Asleep (caution)
  - 🔴 Red = Asleep (alert!)

**Details Section:**
- **Emotion**: Current detected emotion (happy, sad, neutral, etc.)
- **Sleep Probability**: Percentage showing likelihood of drowsiness
- **Progress Bar**: Visual representation of sleep probability

**Alert Banner:**
- Appears when driver is asleep
- Pulsing red banner with warning icon
- Critical alert for immediate attention

### 3. Stop Monitoring

Click **"⏸️ Stop Monitoring"** to pause video processing.

## 🛠️ Troubleshooting

### Backend Issues

**Problem**: "Failed to initialize camera"
**Solution**: 
- Check camera permissions in system settings
- Close other apps using camera (Skype, Zoom, etc.)
- Try different camera index in config.py

**Problem**: "Module 'fer' has no attribute 'FER'"
**Solution**:
```bash
pip install --upgrade fer
pip install --upgrade tensorflow
```

**Problem**: Import errors for dlib
**Solution**:
```bash
pip uninstall dlib
pip install dlib
# May need Visual Studio C++ Build Tools
```

### Frontend Issues

**Problem**: Can't connect to backend API
**Solution**:
- Ensure backend is running
- Check `http://localhost:5000/api/status` in browser
- Verify API_URL in React code

**Problem**: Video stream is black or frozen
**Solution**:
- Check browser console for errors
- Verify camera is working in backend
- Try refreshing the page

**Problem**: npm install fails
**Solution**:
```bash
cd frontend
rm -rf node_modules  # or del /s node_modules on Windows
npm cache clean --force
npm install
```

### Performance Issues

**Problem**: Video is laggy or slow
**Solution**:
- Increase FRAME_SKIP in .env (skips frames for speed)
- Close other applications
- Reduce camera resolution in config

**Problem**: High CPU usage
**Solution**:
- Increase FRAME_SKIP value
- Process frames less frequently
- Use lighter model if available

## 📁 Project Structure

```
Safe_Drive/
├── app.py                    # Flask backend API
├── main_secure.py           # Desktop app (OpenCV)
├── config.py                # Configuration settings
├── utils.py                 # Utility functions
├── logger.py                # Logging system
├── requirements.txt         # Python dependencies
├── models/                  # AI models
│   ├── shape_predictor_68_face_landmarks.dat
│   └── emotion_model.h5
├── frontend/                # React frontend
│   ├── src/
│   │   ├── App.js          # Main component
│   │   └── App.css         # Styling
│   └── package.json
└── README.md
```

## 🔧 Configuration Options

Edit `.env` file to customize:

```env
# Camera settings
CAMERA_INDEX=0              # Primary camera (try 0 or 1)
CAMERA_FALLBACK_INDEX=1     # Backup camera

# Performance settings
FRAME_SKIP=1                # Process every Nth frame (1=all, 2=half)
MAX_FPS=30                  # Target frame rate

# Model paths
SHAPE_PREDICTOR_PATH=models/shape_predictor_68_face_landmarks.dat
MODEL_PATH=models/emotion_model_trained.h5
```

## 📊 How It Works

### 1. Video Capture
- Backend captures frames from webcam
- Processes at configured frame rate
- Applies face detection

### 2. Emotion Detection
- FER library analyzes facial expressions
- Detects 7 emotions: happy, sad, angry, fear, surprise, disgust, neutral
- Calculates emotion probabilities

### 3. Eye Closure Detection
- dlib extracts facial landmarks
- Calculates Eye Aspect Ratio (EAR)
- Detects when eyes are closed

### 4. Status Determination
- Combines emotion data + eye state
- Tracks duration of eye closure
- Determines: Awake / Possibly Asleep / Asleep

### 5. Web Display
- Frontend polls backend for updates
- Refreshes at ~2 updates per second
- Displays status with visual indicators

## 🎨 Customization

### Changing Colors

Edit `frontend/src/App.css`:
```css
.btn-start {
  background: linear-gradient(135deg, #your-color 0%, #your-color2 100%);
}
```

### Adjusting Update Frequency

Edit `frontend/src/App.js`:
```javascript
// Update status every 500ms (change to 1000 for 1 second)
statusIntervalRef.current = setInterval(updateStatus, 500);
```

### Modifying Sleep Detection Logic

Edit `app.py` in the `determine_sleep_status` method:
```python
if closed_duration >= 5:  # Change threshold
    return SLEEP_STATUS_ASLEEP
```

## 📝 Next Steps

After setup:

1. Test the system with yourself as the driver
2. Adjust detection thresholds in `utils.py`
3. Customize the UI colors and layout
4. Add more features like audio alerts
5. Integrate with vehicle systems

## 📞 Support

For issues or questions:
- Check the logs: `logs/app.log`
- Browser console: F12 in browser
- Python terminal: Check for error messages

## 🎉 You're Ready!

Follow these steps and you'll have a fully functional driver drowsiness detection system with a beautiful React interface!

**Quick Command Summary:**

```bash
# Terminal 1 - Backend
python app.py

# Terminal 2 - Frontend
cd frontend && npm start

# Open browser to http://localhost:3000
# Click "Start Monitoring"
```

Enjoy your new Safe Drive system! 🚗💤

