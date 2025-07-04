import cv2
import torch
import numpy as np
from pymongo import MongoClient
import requests
import json
from bson import ObjectId
import time
from datetime import datetime
import threading
import logging
import signal
import sys


# Configuration
CONFIG = {
    "mongo_uri": "mongodb://localhost:27017/",
    "mongo_db": "yolov5_logs",
    "mongo_collection": "detections",
    "rtsp_url": "rtsp://admin:admin@123@192.168.100.11:554/0",
    "yolo_model": "yolov5s",
    "ollama_url": "http://192.168.100.67:11434/api/generate",
    "ollama_model": "llama3.2-vision:latest",  # Use text model for better JSON processing
    "frame_skip": 5,  # Process every 5th frame
    "request_timeout": 10,  # Seconds
    "max_retries": 3,
    "poll_interval": 1,  # Seconds to check for new documents
}


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# MongoDB connection
try:
    client = MongoClient(CONFIG["mongo_uri"], serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client[CONFIG["mongo_db"]]
    collection = db[CONFIG["mongo_collection"]]
    # Create index on timestamp for efficient queries
    collection.create_index([("timestamp", -1)])
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    sys.exit(1)

# Clean ObjectId for JSON serialization
def clean_mongo_data(data):
    if isinstance(data, dict):
        return {k: clean_mongo_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_mongo_data(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data

# Load YOLOvpillar model
try:
    model = torch.hub.load('ultralytics/yolov5', CONFIG["yolo_model"], pretrained=True)
except Exception as e:
    logger.error(f"Failed to load YOLOv5 model: {e}")
    sys.exit(1)

# Initialize video capture
cap = cv2.VideoCapture(CONFIG["rtsp_url"])
if not cap.isOpened():
    logger.error(f"Failed to open RTSP stream: {CONFIG['rtsp_url']}")
    sys.exit(1)

# Process RTSP stream and save detections to MongoDB
def process_rtsp_stream():
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            logger.warning("Failed to read frame from RTSP stream. Retrying...")
            cap.release()
            time.sleep(1)
            cap = cv2.VideoCapture(CONFIG["rtsp_url"])
            continue

        frame_count += 1
        if frame_count % CONFIG["frame_skip"] != 0:
            continue

        # Resize frame for faster processing
        frame = cv2.resize(frame, (640, 480))
        results = model(frame)
        detections = results.pandas().xyxy[0].to_dict('records')

        # Prepare batch of detections
        batch = []
        for det in detections:
            if 'name' not in det or 'confidence' not in det:
                continue
            detection_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "label": det['name'],
                "confidence": round(float(det['confidence']), 4),
                "bbox": {
                    "xmin": round(float(det['xmin']), 2),
                    "ymin": round(float(det['ymin']), 2),
                    "xmax": round(float(det['xmax']), 2),
                    "ymax": round(float(det['ymax']), 2)
                },
                "source": "IP_CAM_192.168.100.11"
            }
            batch.append(detection_data)

        if batch:
            try:
                collection.insert_many(batch)
                logger.info(f"Inserted {len(batch)} detections into MongoDB")
            except Exception as e:
                logger.error(f"Failed to insert detections: {e}")

        time.sleep(0.1)  # Prevent CPU overload

# Format and send detection to Ollama
def format_detection(new_doc):
    required_fields = ["timestamp", "label", "confidence", "bbox", "source"]
    if not all(field in new_doc for field in required_fields):
        logger.warning(f"Skipping invalid document: {new_doc}")
        return

    prompt = f"""
You are an assistant that formats YOLOv5 detection logs into a clean structured report.

Here is the raw detection data in JSON:
{json.dumps(new_doc, indent=2)}

Please format it into a readable bullet-style report including:
- Timestamp
- Object Detected (from 'label')
- Confidence (as a percentage, rounded to 2 decimal places)
- Bounding Box with top-left (xmin, ymin) and bottom-right (xmax, ymax) coordinates (rounded to 2 decimal places)
- Source camera name (from 'source')

Do NOT summarize or skip any field. Just reformat it clearly and completely.
"""
    for attempt in range(CONFIG["max_retries"]):
        try:
            response = requests.post(
                CONFIG["ollama_url"],
                json={"model": CONFIG["ollama_model"], "prompt": prompt, "stream": False},
                timeout=CONFIG["request_timeout"]
            )
            if response.status_code == 200:
                res_json = response.json()
                if 'response' in res_json:
                    logger.info("New Detection Report:")
                    print(res_json['response'])
                else:
                    logger.error(f"Unexpected response format: {json.dumps(res_json, indent=2)}")
                break
            else:
                logger.error(f"Ollama request failed: {response.text}")
        except Exception as e:
            logger.error(f"Failed to send to Ollama: {e}")
        time.sleep(1)
    else:
        logger.error("Max retries reached for Ollama request")

# Poll MongoDB for new detections
def poll_mongodb():
    last_timestamp = None
    while True:
        try:
            query = {} if last_timestamp is None else {"timestamp": {"$gt": last_timestamp}}
            new_docs = list(collection.find(query).sort("timestamp", -1).limit(10))
            if new_docs:
                last_timestamp = new_docs[0]["timestamp"]  # Update to the latest timestamp
                for doc in reversed(new_docs):  # Process in ascending order
                    format_detection(clean_mongo_data(doc))
            else:
                logger.debug("No new detections found")
        except Exception as e:
            logger.error(f"Error polling MongoDB: {e}")
            time.sleep(5)  # Wait before retrying
        time.sleep(CONFIG["poll_interval"])

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    logger.info("Stopping RTSP stream and MongoDB polling...")
    cap.release()
    client.close()
    sys.exit(0)

# Main function
def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    rtsp_thread = threading.Thread(target=process_rtsp_stream, daemon=True)
    rtsp_thread.start()
    poll_mongodb()

if __name__ == "__main__":
    main()