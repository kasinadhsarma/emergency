#!/usr/bin/env python3
from ultralytics import YOLO
import torch
from pathlib import Path
import yaml
import os

def main():
    # Get absolute paths
    current_dir = Path(__file__).parent.absolute()
    dataset_yaml = current_dir / 'Dataset' / 'dataset.yaml'
    runs_dir = current_dir / 'runs'
    models_dir = current_dir / 'models'
    models_dir.mkdir(exist_ok=True)

    # Load dataset config
    with open(dataset_yaml, 'r') as f:
        config = yaml.safe_load(f)

    # Update config with absolute paths
    config['path'] = str(current_dir / 'Dataset')
    
    # Write updated config
    temp_yaml = current_dir / 'Dataset' / 'temp_dataset.yaml'
    with open(temp_yaml, 'w') as f:
        yaml.dump(config, f)

    # Initialize model - using a larger model
    print("Initializing YOLOv8 model...")
    model = YOLO('yolov8n.pt')  # Using nano model for memory efficiency

    # Train the model
    print("Starting training...")
    try:
        results = model.train(
            data=str(temp_yaml),
            epochs=100,           # Reduced epochs for initial training
            imgsz=416,           # Reduced image size for memory efficiency
            batch=2,             # Minimal batch size for memory efficiency
            name='vehicle_detection_multi',
            resume=False,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            patience=50,           # Increased patience
            save=True,
            project=str(runs_dir),
            optimizer='AdamW',     # Changed to AdamW
            lr0=0.0005,           # Reduced initial learning rate
            lrf=0.001,            # Adjusted final learning rate
            momentum=0.937,
            weight_decay=0.01,    # Increased weight decay
            warmup_epochs=5.0,    # Increased warmup
            warmup_momentum=0.8,
            warmup_bias_lr=0.1,
            box=8.0,              # Adjusted loss gains
            cls=1.0,
            dfl=2.0,
            close_mosaic=15,      # Adjusted mosaic closing
            augment=True,
            mixup=0.0,           # Disabled mixup for memory efficiency
            degrees=5.0,         # Reduced rotation augmentation
            translate=0.1,       # Reduced translation
            scale=0.3,          # Reduced scale augmentation
            shear=0.0,          # Disabled shear
            perspective=0.0,     # Disabled perspective
            flipud=0.0,         # Disabled vertical flip
            fliplr=0.5,         # Keep horizontal flip
            mosaic=0.0,         # Disabled mosaic for memory efficiency
            hsv_h=0.015,        # Minimal HSV augmentation
            hsv_s=0.3,
            hsv_v=0.2,
            cache=False         # Disable caching to reduce memory usage
        )

        # Validate the model
        print("Validating model...")
        metrics = model.val()
        
        # Export the model in multiple formats
        print("Exporting model...")
        model.export(format='onnx', save=True)  # ONNX format
        model.export(format='torchscript', save=True)  # TorchScript format
        
        # Save final model
        final_model_path = models_dir / 'vehicle_detection_final.pt'
        model.save(str(final_model_path))
        print(f"Final model saved to {final_model_path}")

    except Exception as e:
        print(f"Error during training: {e}")
    finally:
        # Cleanup temporary yaml
        if temp_yaml.exists():
            os.remove(temp_yaml)

if __name__ == '__main__':
    main()
