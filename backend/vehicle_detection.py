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

class VehicleDetector:
    def __init__(self, model_path: str = 'models/emergency_vehicle_detector_best.pt', batch_size: int = 4, num_threads: int = 4):
        """Initialize the vehicle detector with our trained Faster R-CNN model"""
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
            self.classes = {0: 'AMBULANCE', 1: 'POLICE', 2: 'FIRE_ENGINE'}
            
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

    def detect_image(self, image: np.ndarray) -> List[Dict]:
        """
        Detect vehicles in a single image using optimized inference
        """
        # YOLO expects BGR images in numpy format directly
        results = self.model(image)
        
        # Process detections
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Get the box coordinates, confidence and class
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf.cpu().numpy()[0]
                cls = int(box.cls.cpu().numpy()[0])
                
                if conf > 0.5 and cls in self.classes:
                    detection = {
                        'class': self.classes[cls],
                        'confidence': float(conf),
                        'bbox': np.array([x1, y1, x2, y2])
                    }
                    detections.append(detection)
        
        return detections

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

    def process_video(self, video_path: str, output_path: Optional[str] = None):
        """
        Process a video using YOLO's built-in video processing
        """
        # Process video using YOLO's built-in method
        try:
            results = self.model(source=video_path, stream=True)
            
            # Open video capture to get frame dimensions
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Error: Could not open video at {video_path}")
                return
                
            # Set up video writer if output path is provided
            if output_path:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, 20.0,
                                    (int(cap.get(3)), int(cap.get(4))))
                
            # Process each frame
            for r in results:
                frame = r.orig_img
                detections = []
                
                # Extract detections
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf.cpu().numpy()[0]
                    cls = int(box.cls.cpu().numpy()[0])
                    
                    if conf > 0.5 and cls in self.classes:
                        detection = {
                            'class': self.classes[cls],
                            'confidence': float(conf),
                            'bbox': np.array([x1, y1, x2, y2])
                        }
                        detections.append(detection)
                
                # Draw detections on frame
                frame_with_detections = self.draw_detections(frame, detections)
                
                if output_path:
                    out.write(frame_with_detections)
                    
                cv2.imshow('Emergency Vehicle Detection', frame_with_detections)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            # Clean up
            if output_path:
                out.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            print(f"Error processing video: {str(e)}")
            
        finally:
            if 'cap' in locals():
                cap.release()
            if 'out' in locals() and output_path:
                out.release()
            cv2.destroyAllWindows()

    def _process_predictions(self, prediction) -> List[Dict]:
        """Process model predictions with optimized tensor operations"""
        detections = []
        if self.device.type == 'cuda':
            boxes = prediction[0].boxes.xyxy.cpu().numpy()
            scores = prediction[0].boxes.conf.cpu().numpy()
            labels = prediction[0].boxes.cls.cpu().numpy()
        else:
            boxes = prediction[0].boxes.xyxy.numpy()
            scores = prediction[0].boxes.conf.numpy()
            labels = prediction[0].boxes.cls.numpy()

        # Vectorized filtering
        mask = scores > 0.5
        boxes = boxes[mask]
        scores = scores[mask]
        labels = labels[mask]

        for box, score, label in zip(boxes, scores, labels):
            if int(label) in self.classes:
                detection = {
                    'class': self.classes[int(label)],
                    'confidence': float(score),
                    'bbox': box
                }
                detections.append(detection)

        return detections

if __name__ == "__main__":
    try:
        # Initialize detector with batch processing
        detector = VehicleDetector(batch_size=4)
        
        # Single image detection
        image_path = "backend/Dataset/images/test/45.png"
        img = cv2.imread(image_path)
        if img is not None:
            detections = detector.detect_image(img)
            img_with_detections = detector.draw_detections(img, detections)
            cv2.imshow('Emergency Vehicle Detection', img_with_detections)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        # Video detection with batch processing
        video_path = "backend/runs/vehicle_detection_multi/test_results/ambulance_detected.mp4"
        detector.process_video(video_path)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up CUDA memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
