import cv2
import time
from flask import Flask, Response, jsonify
from flask_cors import CORS
try:
    from fer import FER
except ImportError:
    # Fallback for versions where FER is under fer.fer
    try:
        from fer.fer import FER
    except Exception as e:
        # If both imports fail, raise a clear error
        raise ImportError("Failed to import FER from 'fer' library. Ensure compatible 'fer' is installed.") from e

import numpy as np
from config import Config
from logger import logger
from utils import (
    secure_camera_capture,
    validate_frame,
    sanitize_emotion_label,
    calculate_sleep_probability,
    detect_eye_closure,
    safe_release_resources
)
import dlib
import threading
import base64

# Sleep status constants
SLEEP_STATUS_ASLEEP = "Asleep"
SLEEP_STATUS_AWAKE = "Awake"
SLEEP_STATUS_POSSIBLY_ASLEEP = "Possibly Asleep"

app = Flask(__name__)

# Configure CORS for production
# This allows the frontend from any domain to access the API
# For production, you might want to restrict this to specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # Allow all origins
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

class VideoStreamHandler:
    """Manages video streaming and driver status detection."""
    
    def __init__(self):
        self.frame = None
        self.status_data = {
            'emotion': 'Unknown',
            'sleep_status': 'Unknown',
            'sleep_probability': 0.0
        }
        self.running = False
        self.cap = None
        self.emotion_detector = None
        self.detector = None
        self.predictor = None
        self.eye_closed_start = None
        self.frame_count = 0
        self.frame_lock = threading.Lock()
        self.status_lock = threading.Lock()
    
    def _initialize_stream(self):
        """Initialize network stream capture."""
        try:
            logger.info(f"Connecting to stream: {Config.STREAM_URL}")
            cap = cv2.VideoCapture(Config.STREAM_URL)
            
            # Test connection
            if not cap.isOpened():
                logger.error("Failed to open stream connection")
                return None
            
            # Test first frame
            ret, frame = cap.read()
            if not ret or frame is None:
                logger.error("Failed to read first frame from stream")
                cap.release()
                return None
            
            logger.info(f"Stream connected successfully, frame size: {frame.shape}")
            return cap
            
        except Exception as e:
            logger.error(f"Stream initialization error: {e}")
            return None
    
    def initialize(self):
        """Initialize camera and detectors."""
        try:
            self.emotion_detector = FER(mtcnn=True)
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor(Config.SHAPE_PREDICTOR_PATH)
            
            # Initialize camera based on configuration
            if Config.USE_STREAM:
                logger.info(f"Using network stream mode - URL: {Config.STREAM_URL}")
                self.cap = self._initialize_stream()
            else:
                logger.info(f"Using local camera mode - Index: {Config.CAMERA_INDEX}")
                self.cap = secure_camera_capture(
                    Config.CAMERA_INDEX,
                    Config.CAMERA_FALLBACK_INDEX
                )
            
            if self.cap is None:
                raise RuntimeError("Could not initialize camera/stream")
            
            logger.info("Video handler initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize video handler: {e}")
            return False
    
    def detect_emotion_and_sleep(self, frame: np.ndarray):
        """Detect emotions and determine sleep status."""
        if not validate_frame(frame):
            return "invalid_frame", "Unknown", 0.0
        
        try:
            emotions = self.emotion_detector.detect_emotions(frame)
            
            if emotions:
                dominant_emotion = sanitize_emotion_label(
                    max(emotions[0]['emotions'], key=emotions[0]['emotions'].get)
                )
                
                sleep_prob = calculate_sleep_probability(emotions[0]['emotions'])
                sleep_status = self.determine_sleep_status(frame, sleep_prob)
                
                return dominant_emotion, sleep_status, sleep_prob
            else:
                return "no_face", "Unknown", 0.0
                
        except Exception as e:
            logger.warning(f"Error in emotion detection: {e}")
            return "error", "Unknown", 0.0
    
    def determine_sleep_status(self, frame: np.ndarray, sleep_prob: float) -> str:
        """Determine sleep status based on eye closure duration and emotion probability."""
        current_time = time.time()
        eyes_closed = detect_eye_closure(frame, self.detector, self.predictor)
        
        if eyes_closed:
            return self._handle_eyes_closed(current_time)
        else:
            return self._handle_eyes_open(current_time, sleep_prob)
    
    def _handle_eyes_closed(self, current_time: float) -> str:
        """Handle the case when eyes are closed."""
        if self.eye_closed_start is None:
            self.eye_closed_start = current_time
            return SLEEP_STATUS_POSSIBLY_ASLEEP
        
        closed_duration = current_time - self.eye_closed_start
        if closed_duration >= 5:
            return SLEEP_STATUS_ASLEEP
        
        return SLEEP_STATUS_POSSIBLY_ASLEEP
    
    def _handle_eyes_open(self, current_time: float, sleep_prob: float) -> str:
        """Handle the case when eyes are open."""
        if self.eye_closed_start is not None:
            closed_duration = current_time - self.eye_closed_start
            self.eye_closed_start = None
            if closed_duration >= 10:
                return SLEEP_STATUS_AWAKE
        
        return SLEEP_STATUS_POSSIBLY_ASLEEP if sleep_prob > 0.7 else SLEEP_STATUS_AWAKE
    
    def process_frame(self, frame: np.ndarray):
        """Process frame and update status."""
        emotion, sleep_status, sleep_prob = self.detect_emotion_and_sleep(frame)
        
        with self.status_lock:
            self.status_data = {
                'emotion': emotion,
                'sleep_status': sleep_status,
                'sleep_probability': round(sleep_prob, 2)
            }
        
        return frame
    
    def run(self):
        """Main video capture loop."""
        self.running = True
        logger.info("Starting video capture...")
        consecutive_failures = 0
        max_failures = 10
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                consecutive_failures += 1
                logger.warning(f"Failed to read frame from camera/stream (attempt {consecutive_failures}/{max_failures})")
                
                # Try to reconnect if using stream
                if Config.USE_STREAM and consecutive_failures >= max_failures:
                    logger.info("Attempting to reconnect to stream...")
                    if self.cap:
                        self.cap.release()
                    self.cap = self._initialize_stream()
                    if self.cap is None:
                        logger.error("Failed to reconnect to stream")
                        time.sleep(5)  # Wait longer before retry
                        continue
                    consecutive_failures = 0
                
                time.sleep(0.1)
                continue
            
            # Reset failure counter on successful read
            consecutive_failures = 0
            
            self.frame_count += 1
            
            # Skip frames for performance
            if self.frame_count % Config.FRAME_SKIP == 0:
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Store frame with lock
                with self.frame_lock:
                    self.frame = processed_frame
            
            # Control frame rate (~30 FPS)
            time.sleep(0.033)
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up video handler...")
        self.running = False
        safe_release_resources(self.cap)
        cv2.destroyAllWindows()
    
    def get_frame_base64(self):
        """Get current frame as base64 encoded string."""
        with self.frame_lock:
            if self.frame is None:
                return None
            
            _, buffer = cv2.imencode('.jpg', self.frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return frame_base64
    
    def get_status(self):
        """Get current driver status."""
        with self.status_lock:
            return self.status_data

# Global video handler
video_handler = VideoStreamHandler()
video_thread = None

@app.route('/')
def index():
    """Serve the index page."""
    return Response(open('frontend/public/index.html').read(), mimetype='text/html')

@app.route('/api/status')
def get_status():
    """Get current driver status."""
    try:
        status = video_handler.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/video')
def video_feed():
    """Stream video frames as JPEG images."""
    def generate():
        while video_handler.running:
            frame_base64 = video_handler.get_frame_base64()
            if frame_base64:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + str(len(frame_base64)).encode() + b'\r\n\r\n' +
                       base64.b64decode(frame_base64) + b'\r\n')
            else:
                time.sleep(0.033)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/frame')
def get_frame():
    """Get a single frame as base64."""
    try:
        frame_base64 = video_handler.get_frame_base64()
        if frame_base64:
            return jsonify({'frame': frame_base64})
        else:
            return jsonify({'error': 'No frame available'}), 404
    except Exception as e:
        logger.error(f"Error getting frame: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start')
def start_video():
    """Start video streaming."""
    global video_handler, video_thread
    
    if not video_handler.running:
        if video_handler.initialize():
            video_thread = threading.Thread(target=video_handler.run, daemon=True)
            video_thread.start()
            return jsonify({'message': 'Video streaming started'})
        else:
            return jsonify({'error': 'Failed to initialize camera'}), 500
    else:
        return jsonify({'message': 'Video streaming already running'})

@app.route('/api/stop')
def stop_video():
    """Stop video streaming."""
    global video_handler
    
    if video_handler.running:
        video_handler.cleanup()
        return jsonify({'message': 'Video streaming stopped'})
    else:
        return jsonify({'message': 'Video streaming not running'})

if __name__ == '__main__':
    logger.info("Starting Safe Drive API Server...")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

