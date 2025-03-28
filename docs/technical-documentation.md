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

## Software Requirement Specification

### 4.1 PURPOSE
The purpose of this project is to develop a system that can detect emergency vehicles in video feeds and provide optimal routing to emergency locations. This system aims to improve response times for emergency services by leveraging real-time video analysis and route optimization.

### 4.2 SCOPE
The scope of this project includes:
- Real-time detection of emergency vehicles (ambulances, fire engines, police vehicles) in video feeds.
- Optimal route calculation considering traffic density and other factors.
- Integration with existing emergency response systems.
- Providing a user-friendly interface for monitoring and managing emergency responses.

### 4.3 OBJECTIVES
The objectives of this project are:
- To develop a robust and accurate emergency vehicle detection system using YOLOv8.
- To implement a route optimization algorithm that considers traffic conditions and other relevant factors.
- To create an intuitive user interface for emergency response management.
- To ensure the system is scalable and can handle real-time video feeds from multiple sources.

### 4.4 EXISTING SYSTEM
Currently, emergency response systems rely on manual monitoring and dispatching of emergency vehicles. This process can be slow and inefficient, leading to delays in response times. Existing systems may not have the capability to analyze real-time video feeds or optimize routes based on current traffic conditions.

### 4.5 PROPOSED SYSTEM
The proposed system will automate the detection of emergency vehicles in video feeds and provide optimal routing to emergency locations. Key features of the proposed system include:
- Real-time video analysis using YOLOv8 for emergency vehicle detection.
- Route optimization considering traffic density and other factors.
- Integration with existing emergency response systems for seamless operation.
- A user-friendly interface for monitoring and managing emergency responses.

### 4.6 REQUIREMENTS
The requirements for this project are divided into software and hardware requirements.

#### 4.6.1 SOFTWARE REQUIREMENTS
- Python 3.9 or higher
- FastAPI
- YOLOv8
- OpenCV
- NumPy
- Torch
- Uvicorn
- Pydantic
- PIL
- Base64
- Shutil
- Logging
- Re
- Matplotlib
- Pandas
- Seaborn

#### 4.6.2 HARDWARE REQUIREMENTS
- A computer with at least 8GB of RAM
- A GPU with at least 4GB of VRAM for model training and inference
- A high-definition camera for video feed input
- Stable internet connection for accessing real-time traffic data

## System Analysis & Design

### 5.1 SYSTEM ARCHITECTURE / METHODOLOGY
The system architecture consists of the following components:
- **Video Input**: Captures real-time video feeds from cameras.
- **Vehicle Detection Module**: Uses YOLOv8 to detect emergency vehicles in the video feeds.
- **Route Optimization Module**: Calculates the optimal route to the emergency location considering traffic density.
- **User Interface**: Provides a dashboard for monitoring and managing emergency responses.
- **Backend API**: Handles requests from the user interface and communicates with the detection and optimization modules.

### 5.2 UML DIAGRAMS
The following UML diagrams illustrate the system design. For detailed diagrams, see [UML Diagrams](./uml-diagrams.md).

#### 5.2.1 USE CASE DIAGRAM
This diagram shows the interactions between actors (Dispatcher, Emergency Vehicle Driver) and the system's functionalities.

#### 5.2.2 CLASS DIAGRAM
The class diagram outlines the system's structure including VideoProcessor, ObjectDetection, RouteOptimizer, and UserInterface classes.

#### 5.2.3 SEQUENCE DIAGRAM
The sequence diagram illustrates the interactions between system components during emergency vehicle detection and route optimization.

### 5.3 DATABASE DESIGN
The database design includes the following tables:
- **Users**: Stores user information and credentials.
- **Vehicles**: Stores information about detected emergency vehicles.
- **Routes**: Stores information about calculated routes.
- **Stations**: Stores information about emergency stations (hospitals, fire stations, police stations).

## Implementation

### 6.1 TECHNOLOGIES USED
The following technologies are used in this project:
- **Programming Languages**: Python, JavaScript
- **Frameworks**: FastAPI, React
- **Libraries**: YOLOv8, OpenCV, NumPy, Torch, Matplotlib, Pandas, Seaborn
- **Tools**: Git, Docker, Jupyter Notebook

### 6.2 MODULES IMPLEMENTATION
The project is divided into the following modules:
- **Vehicle Detection Module**: Implements the YOLOv8 model for detecting emergency vehicles in video feeds.
- **Route Optimization Module**: Implements the algorithm for calculating the optimal route to the emergency location.
- **User Interface Module**: Implements the dashboard for monitoring and managing emergency responses.
- **Backend API Module**: Implements the FastAPI backend for handling requests and communicating with the detection and optimization modules.

## Testing & Result Analysis

### 7.1 TEST CASES
The following test cases are used to validate the system:
- **Test Case 1**: Verify that the system can detect emergency vehicles in video feeds with high accuracy.
- **Test Case 2**: Verify that the system can calculate the optimal route to the emergency location considering traffic density.
- **Test Case 3**: Verify that the user interface is intuitive and easy to use.
- **Test Case 4**: Verify that the system can handle real-time video feeds from multiple sources.

### 7.2 RESULT ANALYSIS
The result analysis includes the following metrics:
- **Detection Accuracy**: Measures the accuracy of the emergency vehicle detection module.
- **Route Optimization Efficiency**: Measures the efficiency of the route optimization module in calculating the optimal route.
- **User Satisfaction**: Measures the satisfaction of users with the system's user interface and overall performance.

## Conclusion & Future Scope
The project successfully implements a system for detecting emergency vehicles in video feeds and providing optimal routing to emergency locations. The system improves response times for emergency services by leveraging real-time video analysis and route optimization. Future work includes integrating additional features such as real-time traffic updates and expanding the system to support more types of emergency vehicles.

## References
- YOLOv8 Documentation: https://docs.ultralytics.com/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- OpenCV Documentation: https://docs.opencv.org/
- NumPy Documentation: https://numpy.org/doc/
- Torch Documentation: https://pytorch.org/docs/
- Matplotlib Documentation: https://matplotlib.org/stable/contents.html
- Pandas Documentation: https://pandas.pydata.org/docs/
- Seaborn Documentation: https://seaborn.pydata.org/

## Appendix

### 1. SAMPLE CODE
```python
import cv2
import numpy as np
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')

# Load an image
image = cv2.imread('image.jpg')

# Perform detection
results = model(image)

# Draw bounding boxes on the image
for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        class_name = result.names[cls]
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f'{class_name} {conf:.2f}'
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Save the image with bounding boxes
cv2.imwrite('image_with_boxes.jpg', image)
```

### 2. SCREENS
![Dashboard Screen](images/dashboard_screen.png)
![Detection Screen](images/detection_screen.png)
![Route Optimization Screen](images/route_optimization_screen.png)

### 3. PUBLISHED / PROPOSED PAPER
- Title: "Real-Time Emergency Vehicle Detection and Routing System"
- Authors: [Author Names]
- Abstract: This paper presents a real-time system for detecting emergency vehicles in video feeds and providing optimal routing to emergency locations. The system leverages YOLOv8 for vehicle detection and a custom route optimization algorithm that considers traffic density. The proposed system aims to improve response times for emergency services and enhance overall public safety.

### 4. PLAGIARISM REPORT FOR THE PROJECT
- The project has been checked for plagiarism using [Plagiarism Detection Tool].
- The report indicates that the project is original and does not contain any plagiarized content.
