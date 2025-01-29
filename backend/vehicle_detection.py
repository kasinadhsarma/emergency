import cv2
import torch
from pathlib import Path
from ultralytics import YOLO
from typing import List, Dict, Tuple
import numpy as np

class VehicleDetector:
    def __init__(self, model_path: str = 'yolov8n.pt'):
        """Initialize the vehicle detector with a YOLO model"""
        self.model = YOLO(model_path)
        self.classes = {
            0: 'Ambulance',
            1: 'Fire Engine', 
            2: 'Police',
            3: 'Non Emergency'
        }
        # Force CPU usage
        self.device = 'cpu'
        
    def detect_image(self, image_path: str) -> List[Dict]:
        """
        Detect vehicles in a single image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of detections, each containing class, confidence and bounding box
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")
            
        # Run inference
        results = self.model(img, device=self.device)
        
        # Process detections
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                if class_id in self.classes:
                    detection = {
                        'class': self.classes[class_id],
                        'confidence': float(box.conf[0]),
                        'bbox': box.xyxy[0].cpu().numpy()  # Convert to numpy array
                    }
                    detections.append(detection)
                    
        return detections
    
    def draw_detections(self, image_path: str, output_path: str = None) -> np.ndarray:
        """
        Draw detection results on the image
        
        Args:
            image_path: Path to input image
            output_path: Path to save annotated image (optional)
            
        Returns:
            Annotated image as numpy array
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")
            
        # Get detections
        detections = self.detect_image(image_path)
        
        # Draw bounding boxes and labels
        for det in detections:
            bbox = det['bbox'].astype(int)
            label = f"{det['class']} {det['confidence']:.2f}"
            
            # Draw box
            cv2.rectangle(img, 
                        (bbox[0], bbox[1]), 
                        (bbox[2], bbox[3]),
                        (0, 255, 0), 2)
            
            # Draw label
            cv2.putText(img, label,
                       (bbox[0], bbox[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (0, 255, 0), 2)
            
        # Save if output path provided
        if output_path:
            cv2.imwrite(output_path, img)
            
        return img
    
    @staticmethod
    def process_dataset(input_dir: str, output_dir: str = None):
        """
        Process a directory of images and save results
        
        Args:
            input_dir: Directory containing input images
            output_dir: Directory to save annotated images (optional)
        """
        detector = VehicleDetector()
        input_path = Path(input_dir)
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
        # Process each image
        for img_path in input_path.glob('*.jpg'):
            try:
                if output_dir:
                    out_path = output_path / f"detected_{img_path.name}"
                    detector.draw_detections(str(img_path), str(out_path))
                else:
                    detector.detect_image(str(img_path))
                    
            except Exception as e:
                print(f"Error processing {img_path}: {e}")

if __name__ == "__main__":
    # Example usage
    detector = VehicleDetector()
    
    # Single image detection
    image_path = "Dataset/test_image.jpg"
    try:
        detections = detector.detect_image(image_path)
        print(f"Found {len(detections)} vehicles:")
        for det in detections:
            print(f"- {det['class']} (confidence: {det['confidence']:.2f})")
            
    except Exception as e:
        print(f"Error: {e}")
