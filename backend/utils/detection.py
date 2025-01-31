import cv2
import torch
from pathlib import Path
from ultralytics import YOLO
from typing import List, Dict, Tuple, Generator, Optional
import numpy as np
from dataclasses import dataclass
import time
from PIL import Image
from torchvision import models


@dataclass
class Detection:
    class_name: str
    confidence: float
    bbox: np.ndarray
    frame_number: Optional[int] = None
    timestamp: Optional[float] = None

class VehicleDetector:
    def __init__(self, model_path: str = 'models/yolov8n.pt'):
        """Initialize the vehicle detector with a YOLO model"""
        self.model = YOLO(model_path)
        self.classes = {
            0: 'Ambulance',
            1: 'Fire Engine', 
            2: 'Police',
            3: 'Non Emergency'
        }
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
    def detect_frame(self, frame: np.ndarray, frame_number: Optional[int] = None) -> List[Detection]:
        """
        Detect vehicles in a single frame
        
        Args:
            frame: Input frame as numpy array
            frame_number: Optional frame number for tracking
            
        Returns:
            List of Detection objects
        """
        # Preprocess the frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        transform = models.resnet50(pretrained=True).transforms()
        image_tensor = transform(image).unsqueeze(0)  # Add batch dimension

        # Run inference
        results = self.model(image_tensor, device=self.device)

        # Check the shape and type of the input tensor
        print(image_tensor.shape)  # Should be [1, 3, H, W]
        print(image_tensor.dtype)  # Should be torch.float32
        
        # Process detections
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                if class_id in self.classes:
                    detection = Detection(
                        class_name=self.classes[class_id],
                        confidence=float(box.conf[0]),
                        bbox=box.xyxy[0].cpu().numpy(),
                        frame_number=frame_number,
                        timestamp=time.time()
                    )
                    detections.append(detection)
                    
        return detections

    def process_video(self, video_path: str) -> Generator[List[Detection], None, None]:
        """
        Process a video file frame by frame
        
        Args:
            video_path: Path to video file
            
        Yields:
            List of detections for each frame
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video at {video_path}")

        frame_count = 0
        frame_skip = 5  # Process every 5th frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Skip frames
            if frame_count % frame_skip != 0:
                frame_count += 1
                continue

            # Display the frame (for debugging)
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            detections = self.detect_frame(frame, frame_count)
            yield detections
            frame_count += 1

        cap.release()
        cv2.destroyAllWindows()

    def process_video_with_visualization(self, 
                                      video_path: str, 
                                      output_path: Optional[str] = None,
                                      start_frame: int = 0,
                                      end_frame: Optional[int] = None) -> None:
        """
        Process video and optionally save visualized output
        
        Args:
            video_path: Path to input video
            output_path: Path to save output video (optional)
            start_frame: Frame to start processing from
            end_frame: Frame to end processing at (optional)
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video at {video_path}")
            
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if end_frame is None:
            end_frame = total_frames
            
        # Initialize video writer if output path provided    
        writer = None
        if output_path:
            writer = cv2.VideoWriter(
                output_path, 
                cv2.VideoWriter_fourcc(*'mp4v'),
                fps, (width, height)
            )
            
        # Process frames
        frame_count = 0
        while frame_count < end_frame:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count >= start_frame:
                # Get detections
                detections = self.detect_frame(frame, frame_count)
                
                # Draw detections
                for det in detections:
                    bbox = det.bbox.astype(int)
                    label = f"{det.class_name} {det.confidence:.2f}"
                    
                    # Draw box
                    cv2.rectangle(
                        frame, 
                        (bbox[0], bbox[1]), 
                        (bbox[2], bbox[3]),
                        (0, 255, 0), 2
                    )
                    
                    # Draw label
                    cv2.putText(
                        frame, label,
                        (bbox[0], bbox[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2
                    )
                
                if writer:
                    writer.write(frame)
                    
                # Display frame
                cv2.imshow('Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            frame_count += 1
            
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()

    def start_realtime_detection(self, camera_id: int = 0) -> None:
        """
        Start real-time detection from webcam
        
        Args:
            camera_id: Camera device ID
        """
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            raise ValueError(f"Could not open camera {camera_id}")
            
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Get detections
            detections = self.detect_frame(frame, frame_count)
            
            # Draw detections
            for det in detections:
                bbox = det.bbox.astype(int)
                label = f"{det.class_name} {det.confidence:.2f}"
                
                # Draw box
                cv2.rectangle(
                    frame, 
                    (bbox[0], bbox[1]), 
                    (bbox[2], bbox[3]),
                    (0, 255, 0), 2
                )
                
                # Draw label
                cv2.putText(
                    frame, label,
                    (bbox[0], bbox[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2
                )
            
            # Display frame
            cv2.imshow('Live Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            frame_count += 1
            
        cap.release()
        cv2.destroyAllWindows()
