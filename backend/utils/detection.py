import cv2
import numpy as np
from ultralytics import YOLO
import os
from typing import List, Dict, Union

class EmergencyVehicleDetector:
    """Emergency vehicle detector using YOLO"""

    def __init__(self, model_path: str = None):
        if not model_path:
            model_path = "/home/kasinadhsarma/emergency/backend/best.pt"  # Update with your model path
        self.model = YOLO(model_path)
        self.confidence_threshold = 0.15  # Lower threshold for better detection
        # Update vehicle types to handle different case variations
        self.vehicle_types = {
            'Police', 'police', 'POLICE',
            'Ambulance', 'ambulance', 'AMBULANCE',
            'Fire_Engine', 'fire_engine', 'FIRE_ENGINE',
            'Fire Engine', 'fire engine', 'FireEngine'
        }
        # Mapping to standardize class names
        self.class_mapping = {
            'police': 'Police',
            'POLICE': 'Police',
            'ambulance': 'Ambulance',
            'AMBULANCE': 'Ambulance',
            'fire_engine': 'Fire_Engine',
            'FIRE_ENGINE': 'Fire_Engine',
            'Fire Engine': 'Fire_Engine',
            'fire engine': 'Fire_Engine',
            'FireEngine': 'Fire_Engine'
        }

    def _standardize_class_name(self, class_name: str) -> str:
        """Standardize class names to consistent format"""
        return self.class_mapping.get(class_name, class_name)

    def detect_in_image(self, image_path: str) -> List[Dict]:
        """Detect emergency vehicles in image"""
        try:
            # Read image
            frame = cv2.imread(image_path)
            if frame is None:
                raise ValueError(f"Could not read image from {image_path}")

            # Improve detection with better parameters
            results = self.model(frame, conf=self.confidence_threshold, iou=0.45)[0]
            detections = []

            # Process each detection
            for box in results.boxes:
                # Convert tensor values to float
                try:
                    # Ensure all values are converted to Python floats
                    coords = box.xyxy[0].cpu().numpy().astype(float)
                    x1, y1, x2, y2 = coords.tolist()
                    conf = float(box.conf[0].cpu().numpy())
                    cls = int(box.cls[0].cpu().numpy())
                    class_name = str(results.names[cls])  # Ensure class name is string

                    # Standardize class name
                    class_name = self._standardize_class_name(class_name)

                    # Only include emergency vehicles
                    if class_name in {'Police', 'Ambulance', 'Fire_Engine'}:
                        detection = {
                            'class_name': class_name,
                            'confidence': float(conf),  # Ensure confidence is float
                            'bbox': [float(x1), float(y1), float(x2), float(y2)]  # Ensure bbox values are float
                        }
                        detections.append(detection)
                except Exception as e:
                    print(f"Error processing detection: {e}")
                    continue

            return detections

        except Exception as e:
            raise ValueError(f"Error in detect_in_image: {str(e)}")

    def detect_in_video(self, video_path: str) -> List[Dict]:
        """Detect emergency vehicles in video"""
        try:
            cap = cv2.VideoCapture(video_path)
            detections = []
            frame_count = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % 5 == 0:  # Process every 5th frame
                    results = self.model(frame)[0]

                    for box in results.boxes:
                        try:
                            coords = box.xyxy[0].cpu().numpy()
                            x1, y1, x2, y2 = map(float, coords)
                            conf = float(box.conf[0].cpu().numpy())
                            cls = int(box.cls[0].cpu().numpy())
                            class_name = results.names[cls]

                            if class_name in self.vehicle_types and conf > self.confidence_threshold:
                                detection = {
                                    'class_name': class_name,
                                    'confidence': float(conf),
                                    'bbox': [x1, y1, x2, y2],
                                    'frame': frame_count
                                }
                                detections.append(detection)
                        except Exception as e:
                            print(f"Error processing video detection: {e}")
                            continue

                frame_count += 1

            cap.release()
            return self._get_best_detections(detections)

        except Exception as e:
            raise ValueError(f"Error in detect_in_video: {str(e)}")

    def _get_best_detections(self, detections: List[Dict]) -> List[Dict]:
        """Get best detection for each vehicle type"""
        best_detections = {}

        for det in detections:
            class_name = det['class_name']
            if class_name not in best_detections or det['confidence'] > best_detections[class_name]['confidence']:
                best_detections[class_name] = det

        return list(best_detections.values())

# Example usage
if __name__ == "__main__":
    detector = EmergencyVehicleDetector()

    # Image detection example
    image_detections = detector.detect_in_image("path/to/image.jpg")
    print("Image detections:", image_detections)

    # Video detection example
    video_detections = detector.detect_in_video("path/to/video.mp4")
    print("Video detections:", video_detections)
