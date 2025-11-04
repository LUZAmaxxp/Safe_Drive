import cv2
import time
from flask import Flask, Response, jsonify
from flask_cors import CORS
from fer import FER
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

# Configure CORS for development
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:3000"],  # React dev server
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Cache-Control", "Pragma"],
             "expose_headers": ["Content-Type"]
         }
     },
     supports_credentials=True
)

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
    
    def initialize(self):
        """Initialize camera and detectors."""
        try:
            try:
                # Initialize FER detector; wrap in try/except because model init can
                # raise fatal TensorFlow errors on some environments. If it fails,
                # log and continue without emotion detection so the video stream
                # can still run.
                self.emotion_detector = FER(mtcnn=True)
            except Exception as e:
                logger.error(f"Failed to initialize FER detector: {e}")
                self.emotion_detector = None
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor(Config.SHAPE_PREDICTOR_PATH)
            self.cap = secure_camera_capture(
                Config.CAMERA_INDEX,
                Config.CAMERA_FALLBACK_INDEX
            )
            if self.cap is None:
                raise RuntimeError("Could not initialize camera")
            
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
            if self.emotion_detector is None:
                # No detector available; skip emotion detection
                return "no_model", "Unknown", 0.0

            # Ensure frame is in RGB format (FER expects RGB)
            if len(frame.shape) == 2:  # Convert grayscale to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            elif frame.shape[2] == 4:  # Convert RGBA to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
            elif frame.shape[2] == 3 and frame.dtype == np.uint8:
                # Convert BGR to RGB if necessary
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
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
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Failed to read frame from camera")
                break
            
            # Debug logging for frame info
            logger.info(f"Frame captured: shape={frame.shape if frame is not None else 'None'}, type={frame.dtype if frame is not None else 'None'}")
            
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
        try:
            with self.frame_lock:
                if self.frame is None:
                    logger.warning("No frame available in buffer")
                    return None
                
                # Log frame properties for debugging
                logger.debug(f"Frame properties: shape={self.frame.shape}, dtype={self.frame.dtype}")
                
                # Ensure frame is valid
                if not isinstance(self.frame, np.ndarray) or self.frame.size == 0:
                    logger.error(f"Invalid frame format: type={type(self.frame)}, size={getattr(self.frame, 'size', 0)}")
                    return None
                
                # Convert frame to BGR format for encoding
                frame_to_encode = self.frame.copy()  # Create a copy to prevent race conditions
                if len(frame_to_encode.shape) == 2:
                    logger.debug("Converting grayscale to BGR")
                    frame_to_encode = cv2.cvtColor(frame_to_encode, cv2.COLOR_GRAY2BGR)
                elif frame_to_encode.shape[2] == 4:
                    logger.debug("Converting RGBA to BGR")
                    frame_to_encode = cv2.cvtColor(frame_to_encode, cv2.COLOR_RGBA2BGR)
                elif frame_to_encode.shape[2] == 3 and frame_to_encode.dtype == np.uint8:
                    logger.debug("Converting RGB to BGR")
                    frame_to_encode = cv2.cvtColor(frame_to_encode, cv2.COLOR_RGB2BGR)
                
                # Optimize image for web transmission
                encode_params = [
                    cv2.IMWRITE_JPEG_QUALITY, 85,
                    cv2.IMWRITE_JPEG_OPTIMIZE, 1,
                    cv2.IMWRITE_JPEG_PROGRESSIVE, 1
                ]
                
                # Encode frame
                success, buffer = cv2.imencode('.jpg', frame_to_encode, encode_params)
                if not success or buffer is None or buffer.size == 0:
                    logger.error("Failed to encode frame to JPEG")
                    return None
                
                try:
                    # Convert to base64
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    logger.debug(f"Successfully encoded frame: {len(frame_base64)} bytes")
                    return frame_base64
                except Exception as e:
                    logger.error(f"Failed to encode frame to base64: {str(e)}")
                    return None
        except Exception as e:
            logger.error(f"Error in get_frame_base64: {str(e)}")
            return None
    
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
@app.route('/status')
def get_status():
    """Get current driver status."""
    try:
        status = video_handler.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/video')
@app.route('/api/video')
def video_feed():
    """Stream video frames as JPEG images."""
    def generate():
        while video_handler.running:
            try:
                frame_base64 = video_handler.get_frame_base64()
                if frame_base64:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n'
                           b'Content-Length: ' + str(len(frame_base64)).encode() + b'\r\n\r\n' +
                           base64.b64decode(frame_base64) + b'\r\n')
                else:
                    time.sleep(0.033)
            except Exception as e:
                logger.error(f"Error in video feed: {e}")
                time.sleep(0.033)
    
    response = Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.route('/api/frame')
@app.route('/frame')
def get_frame():
    """Get a single frame as base64."""
    try:
        if not video_handler.running:
            logger.warning("Frame requested but video is not running")
            return jsonify({'error': 'Video stream not running'}), 400
        
        frame_base64 = video_handler.get_frame_base64()
        if frame_base64:
            logger.debug(f"Sending frame: length={len(frame_base64)} bytes")
            response = jsonify({'frame': frame_base64})
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        else:
            logger.warning("No frame available from video handler")
            return jsonify({'error': 'No frame available'}), 404
    except Exception as e:
        logger.error(f"Error getting frame: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start')
@app.route('/start')
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
@app.route('/stop')
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

