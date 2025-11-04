import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [driverStatus, setDriverStatus] = useState({
    emotion: 'Unknown',
    sleep_status: 'Unknown',
    sleep_probability: 0.0
  });
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const intervalRef = useRef(null);
  const statusIntervalRef = useRef(null);

  // Use environment variable for API URL, fallback to localhost for development
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
  
  // Create a configured axios instance
  const axiosInstance = axios.create({
    baseURL: API_URL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json'
    },
    withCredentials: true
  });

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
    };
  }, []);

  const startStream = async () => {
    try {
      setError(null);
      
      // Create a configured axios instance
      const axiosInstance = axios.create({
        baseURL: API_URL,
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      // Start video streaming on backend with retry logic
      let retries = 3;
      while (retries > 0) {
        try {
          await axiosInstance.get('/start', {
            headers: {
              'Accept': 'application/json'
            }
          });
          break;
        } catch (error) {
          retries--;
          if (retries === 0) throw error;
          await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s between retries
        }
      }
      
      setIsStreaming(true);
      
      // Update frame every 50ms (20 FPS) - reduced for better stability
      intervalRef.current = setInterval(updateFrame, 50);
      
      // Update status every 500ms
      statusIntervalRef.current = setInterval(updateStatus, 500);
      
      // Initial updates with delay to ensure backend is ready
      setTimeout(() => {
        updateFrame();
        updateStatus();
      }, 1000);
    } catch (err) {
      console.error('Stream start error:', err);
      setError(`Failed to start video stream: ${err.response?.data?.error || err.message}`);
      setIsStreaming(false);
    }
  };

  const stopStream = async () => {
    try {
      await axios.get(`${API_URL}/stop`);
      setIsStreaming(false);
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
    } catch (err) {
      setError(`Failed to stop video stream: ${err.message}`);
    }
  };

  const updateFrame = async () => {
    if (!isStreaming || !videoRef.current) return;
    
    try {
      console.log('Fetching frame...');  // Debug log
      const response = await axios.get(`${API_URL}/frame`, {
        timeout: 5000,
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      
      if (response.data && response.data.frame) {
        const frameData = response.data.frame;
        console.log('Frame received, length:', frameData.length);  // Debug log
        
        if (frameData && frameData.length > 0) {
          const img = videoRef.current;
          img.src = `data:image/jpeg;base64,${frameData}`;
          setError(null);
        } else {
          console.warn('Received empty frame data');
          setError('Empty frame received');
        }
      }
    } catch (err) {
      console.error('Error updating frame:', err);
      if (!error) {  // Only set error if not already set
        const errorMessage = err.response?.status === 404 
          ? 'Camera not available. Please check your camera connection.'
          : 'Video stream connection lost. Trying to reconnect...';
        setError(errorMessage);
      }
      
      // If connection is lost, try to restart the stream
      if (err.response?.status === 500 || err.code === 'ECONNABORTED') {
        stopStream();
        setTimeout(startStream, 2000); // Try to restart after 2 seconds
      }
    }
  };

  const updateStatus = async () => {
    try {
      const response = await axiosInstance.get('/status');
      setDriverStatus(response.data);
    } catch (err) {
      console.error('Error updating status:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Awake':
        return '#10b981'; // Green
      case 'Asleep':
        return '#ef4444'; // Red
      case 'Possibly Asleep':
        return '#f59e0b'; // Amber
      default:
        return '#6b7280'; // Gray
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Awake':
        return '👁️';
      case 'Asleep':
        return '😴';
      case 'Possibly Asleep':
        return '😑';
      default:
        return '❓';
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">
            <span className="title-icon">🚗</span>
            Safe Drive
          </h1>
          <p className="subtitle">Driver Drowsiness Detection System</p>
        </header>

        <div className="control-panel">
          {!isStreaming ? (
            <button className="btn btn-start" onClick={startStream}>
              ▶ Start Monitoring
            </button>
          ) : (
            <button className="btn btn-stop" onClick={stopStream}>
              ⏸ Stop Monitoring
            </button>
          )}
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <div className="main-content">
          <div className="video-container">
            <div className="video-wrapper">
              {isStreaming ? (
                <img
                  ref={videoRef}
                  alt="Driver Video Stream"
                  className="video-stream"
                  style={{ 
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain',
                    backgroundColor: '#000',
                    imageRendering: 'crisp-edges'
                  }}
                  onError={(e) => {
                    console.error('Image load error:', e);
                    setError('Failed to load video frame');
                  }}
                  onLoad={() => {
                    console.log('Frame loaded successfully');
                    if (error) setError(null);
                  }}
                />
              ) : (
                <div className="video-placeholder">
                  <div className="placeholder-icon">🎥</div>
                  <p>Click "Start Monitoring" to begin</p>
                </div>
              )}
            </div>
          </div>

          <div className="status-container">
            <div className="status-card">
              <div className="status-header">
                <h2>Driver Status</h2>
              </div>
              
              <div className="status-main">
                <div
                  className="status-indicator"
                  style={{
                    backgroundColor: getStatusColor(driverStatus.sleep_status)
                  }}
                >
                  <div className="status-icon">
                    {getStatusIcon(driverStatus.sleep_status)}
                  </div>
                  <div className="status-text">
                    <h3>{driverStatus.sleep_status}</h3>
                  </div>
                </div>

                <div className="status-details">
                  <div className="detail-row">
                    <span className="detail-label">Emotion:</span>
                    <span className="detail-value">{driverStatus.emotion}</span>
                  </div>
                  
                  <div className="detail-row">
                    <span className="detail-label">Sleep Probability:</span>
                    <span className="detail-value">
                      {(driverStatus.sleep_probability * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="progress-bar-wrapper">
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${driverStatus.sleep_probability * 100}%`,
                          backgroundColor: getStatusColor(driverStatus.sleep_status)
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {driverStatus.sleep_status === 'Asleep' && (
                <div className="alert-banner">
                  <span className="alert-icon">⚠️</span>
                  <span className="alert-text">CRITICAL: Driver is asleep!</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <footer className="footer">
          <p>Safe Drive System v1.0 · Powered by FER & AI</p>
        </footer>
      </div>
    </div>
  );
}

export default App;

