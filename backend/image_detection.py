import cv2
import numpy as np
from ultralytics import YOLO
import os
from typing import List, Dict, Union
from utils.location import bbox_to_location

class ImageDetector:
    """
    A class to handle emergency vehicle detection using a YOLO model
    """
    def __init__(self, model_path: str = None):
        """
        Initialize the detector with a YOLO model

        Args:
            model_path (str, optional): Path to the YOLO model file. If None,
                                      uses default path from project structure
        """
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'pick_best.pt')

        self.model = YOLO(model_path)
        self.confidence_threshold = 0.5

    def _process_detections(self, results, frame_number: int = None) -> List[Dict[str, Union[str, float, List[int]]]]:
        """
        Process YOLO detection results into a standardized format

        Args:
            results: YOLO detection results
            frame_number: Optional frame number for video processing

        Returns:
            List of detection dictionaries
        """
        detections = []

        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, conf, cls = r
            detection = {
                'class_name': results.names[int(cls)],
                'confidence': round(float(conf), 3),
                'bbox': [float(x1), float(y1), float(x2), float(y2)]
            }

            if frame_number is not None:
                detection['frame'] = frame_number

            try:
                location_obj = bbox_to_location(
                    [float(x1), float(y1), float(x2), float(y2)],  # Ensure bbox values are float
                    (int(results.imgs[0].shape[1]), int(results.imgs[0].shape[0])),  # Ensure dimensions are int
                    reference_coords=[16.9927, 81.7800]  # Rajahmundry reference coordinates [lat, lng]
                )
                detection['location'] = location_obj  # Add location to detection object
            except Exception as e:
                detection['location'] = {"lat": 16.9927, "lng": 81.7800}  # Default to Rajahmundry center

            detections.append(detection)

        return detections

    def detect_in_video(self, video_path: str, frame_skip: int = 5) -> List[Dict[str, Union[str, float, List[int]]]]:
        """
        Detect emergency vehicles in video using trained YOLO model

        Args:
            video_path (str): Path to the video file
            frame_skip (int): Number of frames to skip between detections for efficiency

        Returns:
            List of detection dictionaries with best confidence scores per class
        """
        detections = []
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Process frames based on frame_skip parameter
            if frame_count % frame_skip == 0:
                results = self.model(frame, conf=self.confidence_threshold)[0]
                frame_detections = self._process_detections(results, frame_count)
                detections.extend(frame_detections)

            frame_count += 1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        return self._get_best_detections(detections)

    def detect_in_image(self, image_path: str) -> List[Dict[str, Union[str, float, List[int]]]]:
        """
        Detect emergency vehicles in a single image using trained YOLO model
        """
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError(f"Could not read image from {image_path}")

        try:
            results = self.model(frame)[0]  # Get first result
            detections = []
            
            # Process detections
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                class_name = results.names[cls]

                detection = {
                    'class_name': class_name,
                    'confidence': conf,
                    'bbox': [float(x1), float(y1), float(x2), float(y2)]
                }

                try:
                    location_obj = bbox_to_location(
                        [float(x1), float(y1), float(x2), float(y2)],  # Ensure bbox values are float
                        (int(frame.shape[1]), int(frame.shape[0])),  # Ensure dimensions are int
                        reference_coords=[16.9927, 81.7800]  # Rajahmundry reference coordinates [lat, lng]
                    )
                    detection['location'] = location_obj  # Add location to detection object
                except Exception as e:
                    detection['location'] = {"lat": 16.9927, "lng": 81.7800}  # Default to Rajahmundry center

                detections.append(detection)

            return detections

        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")

    def _get_best_detections(self, detections: List[Dict[str, Union[str, float, List[int]]]]) -> List[Dict[str, Union[str, float, List[int]]]]:
        """
        Group detections by class and return the highest confidence detection for each class

        Args:
            detections: List of all detections

        Returns:
            List of best detections per class
        """
        grouped_detections = {}
        for det in detections:
            class_name = det['class_name']
            if class_name not in grouped_detections:
                grouped_detections[class_name] = []
            grouped_detections[class_name].append(det)

        final_detections = []
        for class_name, class_detections in grouped_detections.items():
            best_detection = max(class_detections, key=lambda x: x['confidence'])
            final_detections.append(best_detection)

        return final_detections

if __name__ == "__main__":
    detector = ImageDetector()

    # Image detection example
    image_detections = detector.detect_in_image("path/to/image.jpg")
    print("Image detections:", image_detections)

    # Video detection example
    video_detections = detector.detect_in_video("path/to/video.mp4")
    print("Video detections:", video_detections)
