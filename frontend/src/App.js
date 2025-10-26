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

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

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
      
      // Start video streaming on backend
      await axios.get(`${API_URL}/start`);
      
      setIsStreaming(true);
      
      // Update frame every 33ms (30 FPS)
      intervalRef.current = setInterval(updateFrame, 33);
      
      // Update status every 500ms
      statusIntervalRef.current = setInterval(updateStatus, 500);
      
      // Initial updates
      updateFrame();
      updateStatus();
    } catch (err) {
      setError(`Failed to start video stream: ${err.message}`);
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
    try {
      const response = await axios.get(`${API_URL}/frame`);
      if (response.data.frame && videoRef.current) {
        videoRef.current.src = `data:image/jpeg;base64,${response.data.frame}`;
      }
    } catch (err) {
      console.error('Error updating frame:', err);
    }
  };

  const updateStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/status`);
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
              <img
                ref={videoRef}
                alt="Driver Video Stream"
                className="video-stream"
                style={{ display: isStreaming ? 'block' : 'none' }}
              />
              {!isStreaming && (
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

