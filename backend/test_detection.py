#!/usr/bin/env python3
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
import os

def plot_detection(image, results):
    """Plot detection results"""
    img = image.copy()
    class_names = ['Police', 'Fire_Engine', 'Ambulance']
    colors = {
        'Police': (255, 0, 0),      # Blue
        'Fire_Engine': (0, 165, 255), # Orange
        'Ambulance': (0, 255, 0)    # Green
    }

    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            class_name = class_names[cls]
            color = colors[class_name]

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            label = f'{class_name} {conf:.2f}'
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(img, (x1, y1-text_height-8), (x1+text_width, y1), color, -1)
            cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    return img

def process_image(img_path, model, output_path):
    """Process single image"""
    try:
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Error: Could not read image {img_path}")
            return None

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = model(img, conf=0.3)
        detected_img = plot_detection(img, results)

        output_file = output_path / f'{img_path.stem}_detected.jpg'
        plt.imsave(str(output_file), detected_img)

        print(f"\nResults for {img_path.name}:")
        for result in results:
            for box in result.boxes:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_names = ['Police', 'Fire_Engine', 'Ambulance']
                class_name = class_names[cls]
                print(f"- Detected {class_name} with confidence: {conf:.2f}")

        return output_file

    except Exception as e:
        print(f"Error processing image {img_path}: {e}")
        return None

def main():
    # Set paths for local usage
    model_path = Path('backend/best.pt')  # Update this path to your model location
    input_path = Path('backend/Dataset/images/test')     # Create this directory and put your images here
    output_path = Path('backend/Dataset/images/results')   # Results will be saved here

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        return

    print(f"Loading model from: {model_path}")
    model = YOLO(str(model_path))

    # Process all images in input directory
    image_files = list(input_path.glob('*.jpg')) + list(input_path.glob('*.png'))
    
    if not image_files:
        print("No images found in input directory")
        return

    for i, img_path in enumerate(image_files, 1):
        print(f"\nProcessing image {i}/{len(image_files)}: {img_path.name}")
        process_image(img_path, model, output_path)

    print(f"\nAll results saved to {output_path}")

if __name__ == '__main__':
    main()
