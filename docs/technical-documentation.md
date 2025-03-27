# Technical Documentation

## Project Overview

This project implements a system for detecting emergency vehicles (ambulances, fire engines, police vehicles) in video feeds and providing optimal routing to emergency locations.

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd emergency-vehicle-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

Run the FastAPI server:
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

1. **Detect Vehicles in Image**
   ```
   POST /detect/image
   ```
   Upload an image file to detect emergency vehicles.

2. **Process Video**
   ```
   POST /detect/video
   ```
   Upload a video file to process and detect emergency vehicles.

3. **Find Optimal Route**
   ```
   POST /route
   ```
   Request body:
   ```json
   {
     "vehicle_type": "ambulance",
     "current_lat": 12.9716,
     "current_lon": 77.5946,
     "traffic_weights": {}
   }
   ```

4. **Get Emergency Locations**
   ```
   GET /locations/{type}
   ```
   Get list of emergency locations by type (hospital, fire_station, police_station)

## Model Details

The system uses YOLOv8 for vehicle detection:

- Custom trained on Indian emergency vehicles
- Detects four classes: Ambulance, Fire Engine, Police, Non Emergency
- Optimized for real-time detection

## Route Optimization

The pathfinding system:

- Uses OpenStreetMap data for road networks
- Considers traffic density for route optimization
- Provides interactive map visualization
- Finds nearest appropriate emergency location based on vehicle type

## Development

### Training Custom Model

1. Prepare dataset in YOLO format
2. Train model using YOLOv8:
```bash
yolo task=detect mode=train data=dataset.yaml model=yolov8n.pt epochs=100
```

### Running the Model Training Notebook

1. Open the Jupyter notebook `2_model_training.ipynb` located in the `backend/notebooks` directory.
2. Follow the instructions in the notebook to load the dataset, define the YOLOv8 model architecture, train the model, and save the trained model to a file.

### Adding New Emergency Locations

Update the `EMERGENCY_LOCATIONS` dictionary in `app.py` with new locations:

```python
EMERGENCY_LOCATIONS = {
    'hospital': [
        Location("New Hospital", lat, lon, "hospital"),
        ...
    ],
    ...
}
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

[License Type] - See LICENSE file for details
