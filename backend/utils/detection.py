import cv2
import torch
from pathlib import Path
from ultralytics import YOLO
from typing import List, Dict, Tuple, Generator, Optional, Set
import numpy as np
from dataclasses import dataclass
import time
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import gc

@dataclass
class Detection:
    class_name: str
    confidence: float
    bbox: np.ndarray
    frame_number: Optional[int] = None
    timestamp: Optional[float] = None

class VehicleDetector:
    def __init__(self, model_path: str = 'models/yolov8n.pt', batch_size: int = 8, num_threads: int = 4):
        """Initialize the vehicle detector with optimizations"""
        self.model = YOLO(model_path)
        self.classes = {
            0: 'Ambulance',
            1: 'Fire Engine',
            2: 'Police',
            3: 'Non Emergency'
        }
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.batch_size = batch_size

        # Initialize thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=num_threads)
        self.cache_lock = Lock()

        # Initialize memory-efficient cache with LRU eviction
        self.max_cache_size = 1000
        self.detection_cache: Dict[str, List[Detection]] = {}
        self.cache_access_count: Dict[str, int] = {}

        # Enable FP16 for faster inference if using CPU
        if self.device == 'cpu':
            self.model.half()

    @lru_cache(maxsize=128)
    def _get_cached_detection_key(self, frame_hash: str) -> str:
        """Generate cache key for frame detection"""
        return f"detection_{frame_hash}"

    def _preprocess_frame(self, frame: np.ndarray) -> torch.Tensor:
        """Memory efficient frame preprocessing"""
        # Resize if needed to reduce memory usage
        if frame.shape[0] > 1080 or frame.shape[1] > 1920:
            frame = cv2.resize(frame, (1920, 1080))

        # Convert to float32 for better numerical precision
        frame = frame.astype(np.float32) / 255.0

        # Convert to torch tensor
        frame_tensor = torch.from_numpy(frame).to(self.device)
        if self.device == 'cpu':
            frame_tensor = frame_tensor.half()  # Use FP16 on CPU

        return frame_tensor

    def detect_frame(self, frame: np.ndarray, frame_number: Optional[int] = None, use_cache: bool = True) -> List[Detection]:
        """
        Detect vehicles in a single frame with caching and CPU optimization
        """
        if use_cache:
            # Generate frame hash for caching
            frame_hash = str(hash(frame.tobytes()))
            cache_key = self._get_cached_detection_key(frame_hash)

            # Check cache
            with self.cache_lock:
                if cache_key in self.detection_cache:
                    self.cache_access_count[cache_key] += 1
                    return self.detection_cache[cache_key]

        # Preprocess frame
        frame_tensor = self._preprocess_frame(frame)

        # Run inference
        results = self.model(frame_tensor, device=self.device)

        # Process detections
        detections = self._process_detections(results[0], frame_number)

        # Cache result if enabled
        if use_cache:
            with self.cache_lock:
                if len(self.detection_cache) >= self.max_cache_size:
                    # Evict least recently used cache entry
                    lru_key = min(self.cache_access_count, key=self.cache_access_count.get)
                    del self.detection_cache[lru_key]
                    del self.cache_access_count[lru_key]
                self.detection_cache[cache_key] = detections
                self.cache_access_count[cache_key] = 1

        return detections

    def _process_detections(self, result, frame_number: Optional[int] = None) -> List[Detection]:
        """Process detection results efficiently"""
        detections = []
        boxes = result.boxes

        # Batch process boxes
        if len(boxes) > 0:
            class_ids = boxes.cls.cpu().numpy().astype(int)
            confidences = boxes.conf.cpu().numpy()
            bboxes = boxes.xyxy.cpu().numpy()

            # Filter valid class IDs
            valid_mask = np.isin(class_ids, list(self.classes.keys()))
            class_ids = class_ids[valid_mask]
            confidences = confidences[valid_mask]
            bboxes = bboxes[valid_mask]

            # Create detections efficiently
            for class_id, conf, bbox in zip(class_ids, confidences, bboxes):
                detection = Detection(
                    class_name=self.classes[class_id],
                    confidence=float(conf),
                    bbox=bbox,
                    frame_number=frame_number,
                    timestamp=time.time()
                )
                detections.append(detection)

        return detections

    def _draw_detection_batch(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """Optimized batch drawing of detections"""
        # Pre-allocate arrays for better performance
        if not detections:
            return frame

        boxes = np.array([det.bbox.astype(int) for det in detections])
        colors = np.full((len(detections), 3), [0, 255, 0])

        # Draw boxes in batch
        for box, det in zip(boxes, detections):
            # Draw box
            cv2.rectangle(
                frame,
                (box[0], box[1]),
                (box[2], box[3]),
                (0, 255, 0),
                2
            )

            # Draw label
            label = f"{det.class_name} {det.confidence:.2f}"
            cv2.putText(
                frame,
                label,
                (box[0], box[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return frame

    def process_video(self, video_path: str) -> Generator[List[Detection], None, None]:
        """Process a video file with batch processing"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video at {video_path}")

        frame_buffer = []
        frame_numbers = []
        frame_count = 0

        while True:
            # Read batch_size frames
            for _ in range(self.batch_size):
                ret, frame = cap.read()
                if not ret:
                    break
                frame_buffer.append(frame)
                frame_numbers.append(frame_count)
                frame_count += 1

            if not frame_buffer:
                break

            # Process frames in parallel using thread pool
            futures = [self.thread_pool.submit(self.detect_frame, frame, frame_num) for frame, frame_num in zip(frame_buffer, frame_numbers)]
            results = [future.result() for future in futures]

            # Yield results
            for detections in results:
                yield detections

            # Clear buffers
            frame_buffer.clear()
            frame_numbers.clear()

            # Trigger garbage collection to free up memory
            gc.collect()

        cap.release()

    def process_video_with_visualization(self, video_path: str, output_path: Optional[str] = None, start_frame: int = 0, end_frame: Optional[int] = None) -> None:
        """Process video with batch processing and visualization"""
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

        frame_buffer = []
        frame_numbers = []
        frame_count = 0

        while frame_count < end_frame:
            # Read batch_size frames
            for _ in range(self.batch_size):
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count >= start_frame:
                    frame_buffer.append(frame)
                    frame_numbers.append(frame_count)
                frame_count += 1

            if not frame_buffer:
                break

            # Process frames in parallel using thread pool
            futures = [self.thread_pool.submit(self.detect_frame, frame, frame_num) for frame, frame_num in zip(frame_buffer, frame_numbers)]
            results = [future.result() for future in futures]

            # Process and display results
            for frame, detections in zip(frame_buffer, results):
                frame = self._draw_detection_batch(frame, detections)

                if writer:
                    writer.write(frame)

                cv2.imshow('Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Clear buffers
            frame_buffer.clear()
            frame_numbers.clear()

            # Trigger garbage collection to free up memory
            gc.collect()

        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()

    def start_realtime_detection(self, camera_id: int = 0, buffer_size: int = 4) -> None:
        """Real-time detection with frame buffering"""
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            raise ValueError(f"Could not open camera {camera_id}")

        frame_buffer = []
        frame_count = 0

        try:
            while True:
                # Fill buffer
                while len(frame_buffer) < buffer_size:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_buffer.append((frame, frame_count))
                    frame_count += 1

                if not frame_buffer:
                    break

                # Process buffer
                frames = [f[0] for f in frame_buffer]
                futures = [self.thread_pool.submit(self.detect_frame, frame) for frame in frames]
                results = [future.result() for future in futures]

                # Display results
                for (frame, _), detections in zip(frame_buffer, results):
                    frame = self._draw_detection_batch(frame, detections)
                    cv2.imshow('Live Detection', frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        return

                # Clear buffer and read new frames
                frame_buffer.clear()

                # Trigger garbage collection to free up memory
                gc.collect()

        finally:
            cap.release()
            cv2.destroyAllWindows()
            if self.device == 'cuda':
                torch.cuda.empty_cache()
