import cv2
import torch
import numpy as np
from pathlib import Path
import torchvision.transforms as T
from ultralytics import YOLO
from torch.cuda.amp import autocast
from concurrent.futures import ThreadPoolExecutor
from backend.utils.location import bbox_to_location, get_nearest_stations, get_path_traffic_density

class VehicleDetector:
    def __init__(self, model_path: str = 'models/emergency_vehicle_detector_best.pt', batch_size: int = 4, num_threads: int = 4):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.batch_size = batch_size
        self.thread_pool = ThreadPoolExecutor(max_workers=num_threads)
        self.model = YOLO(model_path).to(self.device)
        self.model.eval()
        self.classes = {0: 'ambulance', 1: 'police', 2: 'firetruck'}

    def detect(self, source: str, output_path: str = None):
        if source.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.avi', '.mov')):
            self._process_media(source, output_path)
        else:
            print("Error: Unsupported file format")

def _process_media(self, source: str, output_path: str = None):
    img = None
    if source.lower().endswith(('.jpg', '.jpeg', '.png')):
        img = cv2.imread(source)
        if img is None:
            print(f"Error: Unable to read image {source}")
            return
        detections = self._run_inference(img)
        result_img = self._draw_detections(img, detections)
        cv2.imshow('Emergency Vehicle Detection', result_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        if output_path:
            cv2.imwrite(output_path, result_img)

        # Add location detection, nearest station finding, and routing
        for detection in detections:
            bbox = detection['bbox']
            location = bbox_to_location(bbox, img.shape[:2], reference_coords=[17.0005, 81.7800])  # Provide reference coordinates
            if location is None:
                print(f"Error: Unable to determine location for bbox {bbox}")
                continue
            detection['location'] = location
            nearest_stations = get_nearest_stations(location, detection['class'])
            detection['nearest_stations'] = nearest_stations
            if nearest_stations:
                nearest_station = nearest_stations[0]
                route = get_path_traffic_density(location, nearest_station['location'])
                detection['route'] = route
    else:
        self._process_video(source, output_path)

    if img is not None:
        # Add location detection, nearest station finding, and routing
        for detection in detections:
            bbox = detection['bbox']
            location = bbox_to_location(bbox, img.shape[:2], reference_coords=[17.0005, 81.7800])  # Provide reference coordinates
            detection['location'] = location
            nearest_stations = get_nearest_stations(location, detection['class'])
            detection['nearest_stations'] = nearest_stations
            if nearest_stations:
                nearest_station = nearest_stations[0]
                route = get_path_traffic_density(location, nearest_station['location'])
                detection['route'] = route

    def _run_inference(self, image: np.ndarray):
        results = self.model(image)
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf.cpu().numpy()[0]
                cls = int(box.cls.cpu().numpy()[0])
                if conf > 0.5 and cls in self.classes:
                    detections.append({
                        'class': self.classes[cls],
                        'confidence': float(conf),
                        'bbox': np.array([x1, y1, x2, y2])
                    })
        return detections

    def _draw_detections(self, image: np.ndarray, detections):
        for det in detections:
            bbox = det['bbox'].astype(int)
            label = f"{det['class']} {det['confidence']:.2f}"
            color = (0, 255, 0)  # Default color
            if det['class'] == 'ambulance':
                color = (0, 0, 255)  # Red for ambulance
            elif det['class'] == 'police':
                color = (255, 0, 0)  # Blue for police
            elif det['class'] == 'firetruck':
                color = (0, 255, 255)  # Yellow for firetruck
            cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            cv2.putText(image, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return image

    def _process_video(self, video_path: str, output_path: str = None):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') if output_path else None
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4)))) if output_path else None
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            detections = self._run_inference(frame)
            frame_with_detections = self._draw_detections(frame, detections)
            if output_path and out:
                out.write(frame_with_detections)
            cv2.imshow('Emergency Vehicle Detection', frame_with_detections)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = VehicleDetector()
    image_path = "backend/Dataset/images/test/45.png"
    video_path = "backend/Dataset/videos/test_video.mp4"
    detector.detect(image_path, "output_image.png")
    detector.detect(video_path, "output_video.mp4")
