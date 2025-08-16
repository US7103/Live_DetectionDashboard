# Live Detection Dashboard

A real-time detection dashboard for monitoring object detection from an IP camera stream, powered by YOLOv5, MongoDB, and a modern React dashboard frontend. This project is designed to capture RTSP video streams, perform real-time object detection, log results to a database, and visualize detections live in a web dashboard.

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Demo](#demo)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Project](#running-the-project)
- [File Structure](#file-structure)
- [Key Technologies](#key-technologies)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Real-Time Object Detection**: Captures video from an RTSP stream and uses YOLOv5 for object detection.
- **Detection Logging**: Stores detection results (label, confidence, bounding box, timestamp, etc.) in MongoDB.
- **Live Dashboard**: React-based web dashboard visualizes detections in real time using Socket.IO.
- **Configurable Thresholds**: Easily adjust detection confidence thresholds and video settings.
- **Scalable Backend**: Node.js/Express server with MongoDB for robust data management.
- **Graceful Reconnection**: Automatically attempts to reconnect to the RTSP stream if connection is lost.
- **Extensible**: Easily swap out models, video sources, or adjust to new application needs.

---

## Architecture Overview

```
                +---------------------+
                |   IP Camera (RTSP)  |
                +----------+----------+
                           |
                           v
+-------------------+   Frame Stream   +-----------------------+
| Python Detector   | ---------------> | YOLOv5 Model Inference|
| (rtsp_yolo_mongo) |                  +-----------------------+
|  - Reads RTSP     |                  |  - Object Detection   |
|  - Runs YOLOv5    |                  +-----------------------+
|  - Logs to Mongo  |                  |  - Stores in MongoDB  |
+-------------------+                  +-----------------------+
                           |                          |
                           v                          v
                  +-------------------+       +--------------------+
                  | Node.js/Express   |<----->|   MongoDB          |
                  | REST API + Socket |        +--------------------+
                  +-------------------+
                           |
                           v
                  +-------------------+
                  |  React Dashboard  |
                  |  (Vite + Tailwind)|
                  +-------------------+
```

---


## Getting Started

### Prerequisites

- Python 3.8+ (for detector)
- Node.js 16+ (for dashboard/server)
- MongoDB 4.x or newer (local or remote)
- (Optional) FFmpeg for advanced RTSP handling

### Installation

Clone this repository:

```sh
git clone https://github.com/US7103/Live_DetectionDashboard.git
cd Live_DetectionDashboard
```

#### 1. Backend (Detection & API Server)

- **Install Python dependencies**:

  ```sh
  pip install opencv-python torch pymongo requests
  ```

- **Install Node.js server dependencies**:

  ```sh
  cd server
  npm install
  ```

#### 2. Frontend (React Dashboard)

```sh
cd client
npm install
```

### Configuration

#### Python Detector (`rtsp_yolo_mongo.py`)

Update the `CONFIG` dict as needed:

```python
CONFIG = {
    "mongo_uri": "mongodb://localhost:27017/",
    "mongo_db": "yolov5_logs",
    "mongo_collection": "detections",
    "rtsp_url": RTSP_URL,
    "yolo_model": "yolov5s",
    "confidence_threshold": 0.3,
    ...
}
```

- Set your camera's RTSP URL.
- Adjust MongoDB URI if using remote MongoDB.
- Change `confidence_threshold` for detection sensitivity.

#### Node.js Server

- The server reads `MONGO_URI` from environment or defaults to `mongodb://localhost:27017/yolov5_logs`.

#### React Dashboard

- No special configuration required unless you want to change the API endpoint (defaults to `localhost:5000`).

### Running the Project

#### 1. Start MongoDB

Make sure MongoDB is running locally (`mongod`), or update URIs for remote DB.

#### 2. Start Detector

```sh
python rtsp_yolo_mongo.py
```

#### 3. Start Backend Server

```sh
cd server
npm start
```

#### 4. Start Frontend Dashboard

```sh
cd client
npm run dev
```

Access the dashboard at [http://localhost:5173](http://localhost:5173).

---

## File Structure

```
Live_DetectionDashboard/
│
├── client/                # React dashboard (Vite, TailwindCSS)
│   ├── src/
│   ├── public/
│   ├── index.html
│   ├── vite.config.js
│   └── ...
│
├── server/                # Node.js Express + Socket.IO API server
│   ├── models/
│   ├── routes/
│   ├── index.js
│   └── ...
│
├── rtsp_yolo_mongo.py     # Main detector script (Python + YOLOv5)
├── utkarsh.py             # Alternative/legacy YOLOv5 RTSP script
└── README.md              # This file
```

---

## Key Technologies

- **YOLOv5**: Real-time object detection.
- **OpenCV**: Video frame capture and manipulation.
- **MongoDB**: Logging and querying detection results.
- **Python**: Detection pipeline.
- **Node.js + Express + Socket.IO**: API and real-time event streaming.
- **React + Vite + TailwindCSS**: Modern, fast UI frontend.

---

## Customization

- **Detection Model**: Swap `yolov5s` for another YOLO model (`yolov5m`, `yolov5l`, etc.) in `CONFIG`.
- **RTSP Source**: Update `rtsp_url` to use a different camera.
- **Database**: Use a remote MongoDB instance for distributed deployments.
- **UI**: Extend the React dashboard for analytics, notifications, or custom visualizations.

---

## Troubleshooting

- **MongoDB Connection Errors**: Ensure MongoDB is running, and credentials/host are correct.
- **RTSP Stream Not Connecting**: Test your RTSP URL in VLC or FFmpeg.
- **YOLOv5 not loading**: Ensure torch and ultralytics/yolov5 are installed and compatible with your Python version.
- **Frontend API Errors**: Make sure the backend server is running and accessible from the frontend.

---

## License

MIT

---

### Acknowledgements

- [Ultralytics YOLOv5](https://github.com/ultralytics/yolov5)
- [Vite](https://vitejs.dev/)
- [React](https://react.dev/)
- [Socket.IO](https://socket.io/)
- [MongoDB](https://www.mongodb.com/)
