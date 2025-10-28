# Safe Drive - React Frontend

This is the React frontend application for the Safe Drive driver drowsiness detection system.

## Features

- 🎥 Real-time video streaming of the driver
- 😊 Live emotion detection display
- 💤 Driver sleep/wake status monitoring
- 📊 Sleep probability visualization
- 🎨 Modern, aesthetic UI design
- ⚠️ Critical alerts for drowsy drivers

## Installation

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

## Running the Application

### Backend (Flask API)

1. Make sure you have all Python dependencies installed:
```bash
pip install -r requirements.txt
```

2. Start the Flask backend server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend (React App)

1. Install dependencies (if not already done):
```bash
cd frontend
npm install
```

2. Start the React development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

1. Start both the backend and frontend servers
2. Open your browser and navigate to `http://localhost:3000`
3. Click "Start Monitoring" to begin detecting the driver's status
4. The system will show:
   - Live video feed from the camera
   - Current emotional state
   - Driver's sleep/wake status
   - Sleep probability percentage
   - Visual alerts if the driver is asleep

## API Endpoints

The backend provides the following endpoints:

- `GET /api/start` - Start video streaming
- `GET /api/stop` - Stop video streaming
- `GET /api/status` - Get current driver status
- `GET /api/frame` - Get current video frame
- `GET /api/video` - Stream video feed

## Technology Stack

- **Frontend**: React 18, CSS3
- **Backend**: Flask, OpenCV, FER (Facial Emotion Recognition)
- **AI/ML**: TensorFlow, dlib, imutils

## Project Structure

```
Safe_Drive/
├── app.py                  # Flask backend API
├── config.py               # Configuration settings
├── utils.py                # Utility functions
├── main_secure.py          # Original desktop app
├── models/                 # AI models and data
└── frontend/               # React frontend
    ├── public/
    │   └── index.html
    └── src/
        ├── App.js          # Main App component
        ├── App.css         # Styling
        ├── index.js        # Entry point
        └── index.css       # Global styles
```

## Features in Detail

### Video Streaming
- Real-time video feed from webcam
- Base64 encoded JPEG streaming at ~30 FPS
- Automatic frame updates

### Driver Status Monitoring
- **Awake**: Driver is alert and active (Green indicator)
- **Asleep**: Driver is sleeping (Red indicator with alert)
- **Possibly Asleep**: Driver might be drowsy (Amber indicator)

### Emotion Detection
The system detects 7 different emotions:
- Happy 😊
- Sad 😢
- Angry 😠
- Fear 😨
- Surprise 😲
- Disgust 🤢
- Neutral 😐

### Sleep Probability
Calculated based on:
- Eye closure duration
- Emotional state
- Facial expressions

## Troubleshooting

### Camera not working
- Check if camera permissions are granted
- Ensure no other application is using the camera
- Try changing the camera index in config.py

### API connection errors
- Make sure the Flask backend is running
- Check if port 5000 is not blocked by firewall
- Verify API_URL in App.js

### Installation issues
```bash
# For Python dependencies
pip install -r requirements.txt

# For React dependencies
cd frontend
npm install
```

## Development

### Adding new features
- Frontend components: Edit files in `frontend/src/`
- Backend logic: Edit `app.py`
- Utils and helpers: Edit `utils.py`

### Customization
- UI colors: Edit `frontend/src/App.css`
- API endpoints: Edit `app.py`
- Model parameters: Edit `utils.py`

## License

MIT License

