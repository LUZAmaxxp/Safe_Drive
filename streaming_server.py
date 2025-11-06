#!/usr/bin/env python3
"""
Simple MJPEG streaming server for OBS integration.
This server captures from local camera and streams MJPEG that can be consumed by the main app.
"""

import cv2
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingServer:
    def __init__(self, port=8080, camera_index=0):
        self.port = port
        self.camera_index = camera_index
        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        
    def capture_frames(self):
        """Capture frames from camera in a separate thread."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera {self.camera_index}")
            return
            
        logger.info(f"Camera {self.camera_index} opened successfully")
        
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame.copy()
            
    def get_frame(self):
        """Get the current frame."""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def start(self):
        """Start the streaming server."""
        self.running = True
        
        # Start camera capture thread
        capture_thread = threading.Thread(target=self.capture_frames)
        capture_thread.daemon = True
        capture_thread.start()
        
        # Define MJPEG streaming handler
        class MJPEGHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/stream.mjpg':
                    self.send_response(200)
                    self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
                    # Additional headers to avoid caching and keep connection predictable
                    self.send_header('Cache-Control', 'no-cache, private')
                    self.send_header('Pragma', 'no-cache')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    
                    while server.running:
                        frame = server.get_frame()
                        if frame is not None:
                            try:
                                # Encode frame as JPEG
                                _, jpeg = cv2.imencode('.jpg', frame)
                                payload = jpeg.tobytes()
                                self.wfile.write(b'--frame\r\n')
                                self.send_header('Content-Type', 'image/jpeg')
                                self.send_header('Content-Length', str(len(payload)))
                                self.end_headers()
                                self.wfile.write(payload)
                                self.wfile.write(b'\r\n')
                                try:
                                    self.wfile.flush()
                                except Exception:
                                    pass
                            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                                logger.info("Client disconnected from stream")
                                break
                            except Exception as e:
                                logger.warning(f"Streaming error: {e}")
                                break
                        
                        threading.Event().wait(0.033)  # ~30 FPS
                else:
                    self.send_error(404)
            
            def log_message(self, format, *args):
                # Suppress HTTP server logs
                pass
        
        # Start HTTP server
        server = self  # Make server available to handler
        httpd = HTTPServer(('', self.port), MJPEGHandler)
        logger.info(f"Streaming server started on port {self.port}")
        logger.info(f"Stream URL: http://localhost:{self.port}/stream.mjpg")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down streaming server...")
        finally:
            self.running = False
            if self.cap:
                self.cap.release()
            httpd.shutdown()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MJPEG Streaming Server for OBS")
    parser.add_argument("--port", type=int, default=8080, help="Port to run server on")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    args = parser.parse_args()
    
    server = StreamingServer(port=args.port, camera_index=args.camera)
    server.start()