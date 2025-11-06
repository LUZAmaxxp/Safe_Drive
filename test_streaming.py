#!/usr/bin/env python3
"""
Test script to verify streaming setup works correctly.
This tests both the streaming server and the Safe Drive stream reading.
"""

import cv2
import requests
import time
import sys
from streaming_server import StreamingServer
import threading

def test_streaming_server():
    """Test if the streaming server works."""
    print("Testing streaming server...")
    
    # Start streaming server
    server = StreamingServer(port=8081, camera_index=0)  # Use port 8081 for testing
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # Give server time to start
    time.sleep(3)
    
    # Test if stream is accessible
    try:
        response = requests.get('http://localhost:8081/stream.mjpg', stream=True, timeout=10)
        if response.status_code == 200:
            print("✓ Streaming server is working!")
            
            # Try to read a few frames
            chunk_size = 1024
            bytes_data = b''
            frame_count = 0
            
            for chunk in response.iter_content(chunk_size=chunk_size):
                bytes_data += chunk
                # Look for JPEG start/end markers
                start = bytes_data.find(b'\xff\xd8')
                end = bytes_data.find(b'\xff\xd9')
                
                if start != -1 and end != -1:
                    jpg = bytes_data[start:end+2]
                    bytes_data = bytes_data[end+2:]
                    
                    # Decode JPEG
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        frame_count += 1
                        if frame_count >= 3:  # Test first 3 frames
                            break
            
            if frame_count > 0:
                print(f"✓ Successfully read {frame_count} frames from stream")
            else:
                print("✗ Could not decode frames from stream")
                
        else:
            print(f"✗ Streaming server returned status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Could not connect to streaming server: {e}")
    except Exception as e:
        print(f"✗ Error testing streaming server: {e}")
    
    server.running = False
    return True

def test_opencv_stream():
    """Test OpenCV stream reading directly."""
    print("\nTesting OpenCV stream reading...")
    
    # Test with a simple test pattern first
    print("Creating test stream...")
    
    # Create a simple test server that serves a test pattern
    import http.server
    import socketserver
    import numpy as np
    
    class TestHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/test.jpg':
                # Create a simple test image
                img = np.zeros((480, 640, 3), dtype=np.uint8)
                img[:] = (0, 255, 0)  # Green background
                cv2.putText(img, "TEST STREAM", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
                
                _, jpg = cv2.imencode('.jpg', img)
                
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', str(len(jpg.tobytes())))
                self.end_headers()
                self.wfile.write(jpg.tobytes())
            else:
                self.send_error(404)
        
        def log_message(self, format, *args):
            pass
    
    # Start test server
    with socketserver.TCPServer(("", 8082), TestHandler) as httpd:
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Give server time to start
        time.sleep(2)
        
        # Test OpenCV reading
        try:
            cap = cv2.VideoCapture('http://localhost:8082/test.jpg')
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print("✓ OpenCV can read from HTTP stream")
                    print(f"  Frame shape: {frame.shape}")
                else:
                    print("✗ OpenCV could not read frame from stream")
                cap.release()
            else:
                print("✗ OpenCV could not open stream connection")
                
        except Exception as e:
            print(f"✗ Error testing OpenCV stream: {e}")
        
        httpd.shutdown()
    
    return True

def main():
    """Run all tests."""
    print("Safe Drive Streaming Test Suite")
    print("===============================")
    print()
    
    # Check if we should test streaming server
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        test_streaming_server()
    else:
        test_opencv_stream()
    
    print("\nTest completed!")
    print("\nTo test the full setup:")
    print("1. Start streaming server: python streaming_server.py")
    print("2. Configure OBS to stream to localhost:8080")
    print("3. Set USE_STREAM=True in your .env file")
    print("4. Run Docker container: docker run -it --rm -p 5000:5000 --env-file .env safe-drive")
    print("5. Access Safe Drive at: http://localhost:5000")

if __name__ == "__main__":
    main()