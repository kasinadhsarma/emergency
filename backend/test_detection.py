#!/usr/bin/env python3
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

def process_video(video_path, model, output_path):
    """Process video file for vehicle detection and save key frames"""
    # Open video file
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Create output video writer
    output_video = str(output_path / f'{video_path.stem}_detected.mp4')
    out = cv2.VideoWriter(output_video, 
                         cv2.VideoWriter_fourcc(*'mp4v'),
                         fps, 
                         (frame_width, frame_height))
    
    # Create directory for video frames
    frames_dir = output_path / f'{video_path.stem}_frames'
    frames_dir.mkdir(exist_ok=True)
    
    frame_count = 0
    save_interval = 30  # Save every 30th frame
    
    # Add detection statistics
    class_detections = {
        'Ambulance': 0,
        'Fire Engine': 0,
        'Police': 0,
        'Non Emergency': 0
    }
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        print(f"\rProcessing frame {frame_count}", end="")
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Run inference with adjusted confidence threshold
        results = model(frame_rgb, conf=0.25, iou=0.45)  # Lowered confidence threshold, added IOU threshold
        
        # Update detection statistics
        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                class_names = ['Ambulance', 'Fire Engine', 'Police', 'Non Emergency']
                class_name = class_names[cls]
                class_detections[class_name] += 1
        
        # Plot detections on frame
        detected_frame = plot_detection(frame_rgb, results)
        
        # Convert back to BGR for video writing
        detected_frame = cv2.cvtColor(detected_frame, cv2.COLOR_RGB2BGR)
        
        # Write frame to video
        out.write(detected_frame)
        
        # Save key frames and show detections
        if frame_count % save_interval == 0:
            frame_path = frames_dir / f'frame_{frame_count:04d}.jpg'
            cv2.imwrite(str(frame_path), detected_frame)
            
            # Print detection results for this frame
            print(f"\nDetections in frame {frame_count}:")
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_names = ['Ambulance', 'Fire Engine', 'Police', 'Non Emergency']
                    class_name = class_names[cls]
                    print(f"- Detected {class_name} with confidence: {conf:.2f}")
        
    print(f"\nProcessed {frame_count} frames")
    print(f"Saved detected video to {output_video}")
    print(f"Saved key frames to {frames_dir}")
    
    # Print detection statistics
    print("\nDetection Statistics:")
    for class_name, count in class_detections.items():
        print(f"{class_name}: {count} detections")
    
    # Release resources
    cap.release()
    out.release()

def add_legend(img):
    """Add color-coded legend to the top of the image"""
    # Define class names and colors (BGR format)
    class_names = ['Ambulance', 'Fire Engine', 'Police', 'Non Emergency']
    colors = {
        'Ambulance': (0, 0, 255),       # Red
        'Fire Engine': (0, 165, 255),    # Orange
        'Police': (255, 255, 0),         # Cyan
        'Non Emergency': (0, 255, 0)     # Green
    }
    
    # Calculate legend dimensions
    legend_height = 40
    padding = 10
    font_scale = 0.7
    thickness = 2
    
    # Create legend background
    legend = img.copy()
    cv2.rectangle(legend, (0, 0), (img.shape[1], legend_height), (0, 0, 0), -1)
    
    # Add color boxes and labels
    x_pos = padding
    y_pos = 30
    box_size = 20
    
    for class_name in class_names:
        color = colors[class_name]
        # Draw color box
        cv2.rectangle(legend, (x_pos, y_pos-box_size), (x_pos+box_size, y_pos), color, -1)
        # Add label
        cv2.putText(legend, class_name, (x_pos+box_size+5, y_pos-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
        # Update x position for next item
        x_pos += len(class_name)*15 + box_size + padding
    
    return legend

def plot_detection(image, results):
    """Plot detection results on the image"""
    img = image.copy()
    
    # Define class names and colors (BGR format)
    class_names = ['Ambulance', 'Fire Engine', 'Police', 'Non Emergency']
    colors = {
        'Ambulance': (0, 0, 255),       # Red
        'Fire Engine': (0, 165, 255),    # Orange
        'Police': (255, 255, 0),         # Cyan
        'Non Emergency': (0, 255, 0)     # Green
    }

    for result in results:
        boxes = result.boxes  # Boxes object for bbox outputs

        for box in boxes:
            # Get box coordinates and confidence
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            # Get class name and color
            class_name = class_names[cls]
            color = colors[class_name]
            
            # Draw bounding box with class-specific color
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            # Add label with the same color
            label = f'{class_name} {conf:.2f}'
            # Add dark background to text for better visibility
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(img, (x1, y1-text_height-8), (x1+text_width, y1), color, -1)
            cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    # Add legend at the top
    img = add_legend(img)

    return img

def process_image(img_path, model, output_path):
    """Process single image for vehicle detection"""
    img = cv2.imread(str(img_path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    results = model(img, conf=0.3)  # Increase confidence threshold
    detected_img = plot_detection(img, results)
    
    output_file = output_path / f'{img_path.stem}_detected.jpg'
    plt.imsave(str(output_file), detected_img)
    
    print(f"\nResults for {img_path.name}:")
    for result in results:
        for box in result.boxes:
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            class_names = ['Ambulance', 'Fire Engine', 'Police', 'Non Emergency']
            class_name = class_names[cls]
            print(f"- Detected {class_name} with confidence: {conf:.2f}")
    
    return output_file

def main():
    # Load the trained model
    model_path = Path('backend/models/vehicle_detection_final.pt')
    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        return

    print(f"Model path: {model_path}")
    print(f"Model exists: {model_path.exists()}")

    model = YOLO(str(model_path))

    # Create output directory
    output_path = Path('backend/runs/vehicle_detection_multi/test_results')
    output_path.mkdir(parents=True, exist_ok=True)

    # Get test files from both directories
    image_test_dir = Path('backend/Dataset/images/test')
    video_test_dir = Path('backend/Dataset/test')
    
    # Get image files
    image_files = []
    if image_test_dir.exists():
        for ext in ('*.png', '*.jpg', '*.jpeg'):
            image_files.extend(image_test_dir.glob(ext))
    else:
        print("Image test directory not found")
    
    # Get video files
    video_files = []
    if video_test_dir.exists():
        for ext in ('*.mp4', '*.avi'):
            video_files.extend(video_test_dir.glob(ext))
    else:
        print("Video test directory not found")

    # Process images
    if image_files:
        print(f"\nFound {len(image_files)} images")
        for i, img_path in enumerate(image_files, 1):
            print(f"\nProcessing image {i}/{len(image_files)}: {img_path}")
            process_image(img_path, model, output_path)

    # Process videos
    if video_files:
        print(f"\nFound {len(video_files)} videos")
        for i, video_path in enumerate(video_files, 1):
            print(f"\nProcessing video {i}/{len(video_files)}: {video_path}")
            process_video(video_path, model, output_path)

    print(f"\nAll results saved to {output_path}")

if __name__ == '__main__':
    main()
