import cv2
import torch
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import torchvision.transforms as T
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
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
        self._setup_model(model_path)

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
        checkpoint = torch.load(model_path, map_location=self.device)
        self.classes = checkpoint['class_names']
        num_classes = checkpoint['num_classes']

        # Initialize model architecture
        self.model = fasterrcnn_resnet50_fpn_v2(pretrained=False)
        in_features = self.model.roi_heads.box_predictor.cls_score.in_features
        self.model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

        # Load trained weights
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        # Optimize model
        if self.device.type == 'cuda':
            # Convert to TorchScript for faster inference
            self.model = torch.jit.script(self.model)
            # Quantize model for better performance
            self.model = torch.quantization.quantize_dynamic(
                self.model, {torch.nn.Linear}, dtype=torch.qint8
            )
        
        self.model.to(self.device)
        self.model.eval()

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
        # Preprocess image
        img_tensor = self.preprocess_image(image)
        
        # Run inference with automatic mixed precision
        with torch.no_grad(), autocast():
            if self.device.type == 'cuda':
                with self.stream1:
                    prediction = self.model([img_tensor])
            else:
                prediction = self.model([img_tensor])

        # Process detections
        detections = []
        boxes = prediction[0]['boxes'].cpu().numpy()
        scores = prediction[0]['scores'].cpu().numpy()
        labels = prediction[0]['labels'].cpu().numpy()

        # Filter detections with confidence > 0.5
        for box, score, label in zip(boxes, scores, labels):
            if score > 0.5 and int(label) in self.classes:
                detection = {
                    'class': self.classes[int(label)],
                    'confidence': float(score),
                    'bbox': box
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
        Process a video with batch processing and parallel streams
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video at {video_path}")
            return

        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 20.0,
                                (int(cap.get(3)), int(cap.get(4))))

        frames_buffer = []
        detections_buffer = []
        
        while cap.isOpened():
            # Read batch_size frames
            for _ in range(self.batch_size):
                ret, frame = cap.read()
                if not ret:
                    break
                frames_buffer.append(frame)
                
            if not frames_buffer:
                break
                
            # Process batch
            if self.device.type == 'cuda':
                # Use parallel CUDA streams
                with self.stream1:
                    batch_tensors = [self.preprocess_image(frame) for frame in frames_buffer]
                    batch_input = torch.stack(batch_tensors)

                with self.stream2:
                    with torch.no_grad(), autocast():
                        batch_predictions = self.model(batch_input)

                torch.cuda.synchronize()
            else:
                # CPU processing
                batch_tensors = [self.preprocess_image(frame) for frame in frames_buffer]
                batch_input = torch.stack(batch_tensors)
                with torch.no_grad():
                    batch_predictions = self.model(batch_input)
            
            # Process predictions
            for frame, predictions in zip(frames_buffer, batch_predictions):
                detections = self._process_predictions(predictions)
                frame_with_detections = self.draw_detections(frame, detections)
                
                if output_path:
                    out.write(frame_with_detections)
                
                cv2.imshow('Emergency Vehicle Detection', frame_with_detections)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            frames_buffer.clear()

        # Release the capture and close windows
        cap.release()
        if output_path:
            out.release()
        cv2.destroyAllWindows()

    def _process_predictions(self, prediction) -> List[Dict]:
        """Process model predictions with optimized tensor operations"""
        detections = []
        if self.device.type == 'cuda':
            boxes = prediction['boxes'].cpu().numpy()
            scores = prediction['scores'].cpu().numpy()
            labels = prediction['labels'].cpu().numpy()
        else:
            boxes = prediction['boxes'].numpy()
            scores = prediction['scores'].numpy()
            labels = prediction['labels'].numpy()

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
        image_path = "Dataset/test_image.jpg"
        img = cv2.imread(image_path)
        if img is not None:
            detections = detector.detect_image(img)
            img_with_detections = detector.draw_detections(img, detections)
            cv2.imshow('Emergency Vehicle Detection', img_with_detections)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        # Video detection with batch processing
        video_path = "Dataset/test_video.mp4"
        detector.process_video(video_path)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up CUDA memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
