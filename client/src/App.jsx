import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import axios from 'axios';
import DetectionTable from './components/DetectionTable';
import DetectionChart from './components/DetectionChart';

// Hardcode URLs (no .env)
const API_URL = 'http://localhost:5000';
const SOCKET_URL = 'http://localhost:5000';
const socket = io(SOCKET_URL);

function App() {
  const [detections, setDetections] = useState([]);

  // Fetch initial detections
  useEffect(() => {
    const fetchDetections = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/detections`);
        setDetections(response.data.reverse()); // Reverse to show newest first
      } catch (err) {
        console.error('Error fetching detections:', err);
      }
    };
    fetchDetections();
  }, []);

  // Listen for new detections via Socket.IO
  useEffect(() => {
    socket.on('newDetection', (detection) => {
      setDetections((prev) => [detection, ...prev].slice(0, 50)); // Keep latest 50
    });

    return () => {
      socket.off('newDetection');
    };
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">YOLOv5 Detection Dashboard</h1>
      <DetectionChart detections={detections} />
      <h2 className="text-2xl font-semibold mt-8 mb-4 text-gray-700">Recent Detections</h2>
      <DetectionTable detections={detections} />
    </div>
  );
}

export default App;