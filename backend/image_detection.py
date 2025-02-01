import cv2
import torch
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import torchvision.transforms as T
from ultralytics import YOLO
import torch.cuda
from torch.cuda.amp import autocast
from numba import jit
from concurrent.futures import ThreadPoolExecutor

class EmergencyVehicleDetector:
    def __init__(self, model_path: str = 'models/emergency_vehicle_detector_best.pt', batch_size: int = 4, num_threads: int = 4):
        """Initialize the image detector with our trained Faster R-CNN model"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.batch_size = batch_size

        # Initialize thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=num_threads)

        # Set up CUDA streams for parallel processing
        if torch.cuda.is_available():
            self.stream1 = torch.cuda.Stream()
            self.stream2 = torch.cuda.Stream()

        # Load and optimize the model
        self._setup_model('backend/runs/vehicle_detection_multi3/weights/best.pt')

        # Set up transforms on GPU if available
        self.transform = T.Compose([
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225])
        ])

        # Initialize frame buffer for batch processing
        self.frame_buffer = []

    def _setup_model(self, model_path: str):
        """Set up and optimize the model"""
        try:
            # Initialize YOLO model with our custom trained model
            self.model = YOLO('backend/runs/vehicle_detection_multi3/weights/best.pt')

            # Define class names from our custom dataset
            self.classes = {0: 'ambulance', 1: 'police', 2: 'firetruck'}

            # Set model to evaluation mode
            self.model.eval()

        except Exception as e:
            print(f"Error setting up model: {str(e)}")
            raise

    @jit(nopython=True)
    def _preprocess_numba(self, image: np.ndarray) -> np.ndarray:
        """Accelerated image preprocessing using Numba"""
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """CPU-accelerated image preprocessing"""
        # Fall back to Numba-accelerated CPU processing
        image_rgb = self._preprocess_numba(image)

        # Move tensor to GPU if available
        return self.transform(image_rgb).to(self.device)

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
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                }
                detections.append(detection)

            return detections

        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")

    def draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw detection results on the image

        Args:
            image: Input image as numpy array
            detections: List of detections

        Returns:
            Annotated image as numpy array
        """
        # Draw bounding boxes and labels
        for det in detections:
            bbox = det['bbox'].astype(int)
            label = f"{det['class']} {det['confidence']:.2f}"

            # Draw box
            cv2.rectangle(image,
                         (bbox[0], bbox[1]),
                         (bbox[2], bbox[3]),
                         (0, 255, 0), 2)

            # Draw label
            cv2.putText(image, label,
                       (bbox[0], bbox[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (0, 255, 0), 2)

        return image

if __name__ == "__main__":
    try:
        # Initialize detector with batch processing
        detector = EmergencyVehicleDetector(batch_size=4)

        # Single image detection
        image_path = "backend/Dataset/images/test/45.png"
        img = cv2.imread(image_path)
        if img is not None:
            detections = detector.detect_in_image(img)
            img_with_detections = detector.draw_detections(img, detections)
            cv2.imshow('Emergency Vehicle Detection', img_with_detections)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up CUDA memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
