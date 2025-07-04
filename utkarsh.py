# import cv2
# import torch

# # Input from RTSP camera
# camera_url = "rtsp://admin:admin@123@192.168.100.11:554/0"
# cap = cv2.VideoCapture(camera_url)

# # Load YOLOv5
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     results = model(frame)
#     annotated_frame = results.render()[0]
#     cv2.imshow("YOLOv5 RTSP Camera", annotated_frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()


import subprocess
import cv2
import numpy as np
import torch
from datetime import datetime
from pymongo import MongoClient

# RTSP stream URL from your IP camera
RTSP_URL = "rtsp://admin:admin@123@192.168.100.11:554/0"

# Define frame resolution (same as your camera stream)
WIDTH, HEIGHT = 640, 480

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["yolov5_logs"]
collection = db["detections"]

# Load YOLOv5 model
model = torch.hub.load("ultralytics/yolov5", "yolov5s", trust_repo=True)

# FFmpeg command to pull frames from RTSP
ffmpeg_cmd = [
    'ffmpeg',
    '-i', RTSP_URL,
    '-loglevel', 'quiet',
    '-an',  # disable audio
    '-f', 'rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', f'{WIDTH}x{HEIGHT}',
    '-r', '10',
    '-'
]

# Start FFmpeg process
process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE)

# Read and process frames
while True:
    raw_frame = process.stdout.read(WIDTH * HEIGHT * 3)
    if not raw_frame:
        print("No frame received.")
        break

    frame = np.frombuffer(raw_frame, np.uint8).reshape((HEIGHT, WIDTH, 3))

    # Run YOLOv5 detection
    results = model(frame)
    detections = results.pandas().xyxy[0]

    # Log each detection to MongoDB
    for _, row in detections.iterrows():
        
            
        detection_record = {
            
            "timestamp": datetime.utcnow().isoformat(),
            "label": row['name'],
            "confidence": int(row['confidence']),
            "bbox": {
                "xmin": float(row['xmin']),
                "ymin": float(row['ymin']),
                "xmax": float(row['xmax']),
                "ymax": float(row['ymax']),
            },
            "source": "IP_CAM_192.168.100.11"
        }
        collection.insert_one(detection_record)

    # Display frame
    annotated = results.render()[0]
    cv2.imshow("YOLOv5 RTSP Stream", annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
process.terminate()
cv2.destroyAllWindows()
