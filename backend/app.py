from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import cv2
import numpy as np
from typing import List, Optional, Dict
import json
from pydantic import BaseModel
import io
from datetime import datetime
from contextlib import asynccontextmanager

# Mock imports for utils (replace with actual implementations)
from utils.detection import VehicleDetector
from utils.pathfinding import PathFinder, Location

# Initialize components
detector = VehicleDetector(model_path='runs/vehicle_detection_multi4/weights/best.pt')
pathfinder = PathFinder()

# Load emergency locations for Rajahmundry
EMERGENCY_LOCATIONS = {
    'hospital': [
        Location("Kalyan Nursing Home", 16.9780, 81.7830, "hospital"),
        Location("Kranthi Nursing Home", 16.9785, 81.7790, "hospital"),
        Location("Gowthami Nursing Home", 16.9805, 81.7750, "hospital")
    ],
    'fire_station': [
        Location("Aryapuram Fire Station", 16.9786, 81.7778, "fire_station"),
        Location("AP State Disaster Response & Fire Services Department", 16.9800, 81.7833, "fire_station")
    ],
    'police_station': [
        Location("One Town Police Station", 16.9780, 81.7830, "police_station"),
        Location("Two Town Police Station", 16.9785, 81.7790, "police_station"),
        Location("Three Town Police Station", 16.9805, 81.7750, "police_station")
    ]
}

AREA_BOUNDARY = {
    'north': 17.0100,
    'south': 16.9600,
    'east': 81.8000,
    'west': 81.7500
}

# Storage for emergency requests
EMERGENCY_REQUESTS = []

MOCK_VEHICLES = [
    {
        "id": "vehicle-1",
        "type": "ambulance",
        "location": [16.9780, 81.7830],  # [lat, lon]
        "status": "available",
        "eta": None
    },
    {
        "id": "vehicle-2",
        "type": "fire_engine",
        "location": [16.9786, 81.7778],  # [lat, lon]
        "status": "available",
        "eta": None
    },
    {
        "id": "vehicle-3",
        "type": "police",
        "location": [16.9785, 81.7790],  # [lat, lon]
        "status": "available",
        "eta": None
    }
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    try:
        for locations in EMERGENCY_LOCATIONS.values():
            for location in locations:
                pathfinder.add_emergency_location(location)
        pathfinder.load_area_boundary(AREA_BOUNDARY)
        print("Area graph loaded successfully")
    except Exception as e:
        print(f"Warning: Failed to load area graph: {e}")
    yield
    print("Shutting down application...")

# Initialize FastAPI with lifespan
app = FastAPI(title="Emergency Vehicle Detection & Routing", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class RouteRequest(BaseModel):
    vehicle_type: str
    current_lat: float
    current_lon: float
    traffic_weights: Optional[dict] = None

class EmergencyContact(BaseModel):
    type: str
    number: str
    description: str
    emergencyType: str

class EmergencyRequest(BaseModel):
    type: str
    location: List[float]
    address: str
    description: str

class Vehicle(BaseModel):
    id: str
    type: str
    location: List[float]
    status: str
    eta: Optional[str] = None

class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]
    frame_number: Optional[int] = None
    timestamp: Optional[float] = None

# Detection endpoints
@app.post("/detect/image")
async def detect_image(file: UploadFile = File(...)):
    """Detect emergency vehicles in an image"""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        detections = detector.detect_frame(img)
        results = [
            Detection(
                class_name=det.class_name,
                confidence=det.confidence,
                bbox=det.bbox.tolist()
            )
            for det in detections
        ]

        return {"detections": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/video")
async def detect_video(file: UploadFile = File(...)):
    """Process video and return detections"""
    try:
        temp_path = Path("temp_video.mp4")
        with temp_path.open("wb") as f:
            f.write(await file.read())

        all_detections = []
        for frame_detections in detector.process_video(str(temp_path)):
            frame_results = [
                Detection(
                    class_name=det.class_name,
                    confidence=det.confidence,
                    bbox=det.bbox.tolist(),
                    frame_number=det.frame_number,
                    timestamp=det.timestamp
                )
                for det in frame_detections
            ]
            all_detections.extend(frame_results)

        return {"detections": all_detections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path.exists():
            temp_path.unlink()

# Routing endpoint
@app.post("/route")
async def find_route(request: RouteRequest):
    """Find optimal route for emergency vehicle"""
    try:
        route_coords, destination = pathfinder.find_optimal_route(
            request.current_lat,
            request.current_lon,
            request.vehicle_type,
            request.traffic_weights
        )

        map_vis = pathfinder.visualize_route(route_coords, destination)
        map_data = io.BytesIO()
        map_vis.save(map_data, close_file=False)
        map_data.seek(0)

        return StreamingResponse(
            map_data,
            media_type="text/html",
            headers={"Content-Disposition": "inline; filename=route_map.html"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API endpoints
@app.get("/api/locations")
async def get_locations():
    """Get all emergency locations"""
    return EMERGENCY_LOCATIONS

@app.get("/api/stations")
async def get_stations():
    """Get all emergency service stations"""
    try:
        stations = {
            "fireStations": [
                {
                    "id": f"fire-{i}",
                    "name": loc.name,
                    "location": {"latitude": loc.lat, "longitude": loc.lon},
                    "address": f"{loc.name}, Rajahmundry",
                    "contact": "+91 1234567890"
                }
                for i, loc in enumerate(EMERGENCY_LOCATIONS['fire_station'])
            ],
            "policeStations": [
                {
                    "id": f"police-{i}",
                    "name": loc.name,
                    "location": {"latitude": loc.lat, "longitude": loc.lon},
                    "address": f"{loc.name}, Rajahmundry",
                    "contact": "+91 1234567890"
                }
                for i, loc in enumerate(EMERGENCY_LOCATIONS['police_station'])
            ],
            "ambulanceStations": [
                {
                    "id": f"hospital-{i}",
                    "name": loc.name,
                    "location": {"latitude": loc.lat, "longitude": loc.lon},
                    "address": f"{loc.name}, Rajahmundry",
                    "contact": "+91 1234567890"
                }
                for i, loc in enumerate(EMERGENCY_LOCATIONS['hospital'])
            ]
        }
        return JSONResponse(content=stations, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/requests")
async def get_requests():
    """Get all emergency requests"""
    return JSONResponse(content=EMERGENCY_REQUESTS, status_code=200)

@app.post("/api/requests")
async def create_request(request: EmergencyRequest):
    """Create a new emergency request"""
    try:
        new_request = {
            "id": f"REQ-{len(EMERGENCY_REQUESTS) + 1}",
            "type": request.type,
            "status": "Pending",
            "location": request.location,
            "address": request.address,
            "description": request.description,
            "timestamp": datetime.now().isoformat()
        }
        EMERGENCY_REQUESTS.append(new_request)
        return new_request
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vehicles")
async def get_vehicles():
    """Get all emergency vehicles"""
    return MOCK_VEHICLES

@app.post("/api/set_emergency_contacts")
async def set_emergency_contacts(contacts: List[EmergencyContact]):
    """Set emergency contacts for a user"""
    try:
        return {"message": "Emergency contacts updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/medical_information")
async def get_medical_information():
    """Get user's medical information"""
    return {
        "blood_type": "O+",
        "allergies": ["Penicillin"],
        "conditions": ["None"],
        "emergency_contact": {
            "name": "John Doe",
            "relationship": "Father",
            "phone": "+91 9876543210"
        }
    }

@app.get("/api/saved_locations")
async def get_saved_locations():
    """Get user's saved locations"""
    return [
        {
            "id": "home",
            "name": "Home",
            "address": "123 Main St, Rajahmundry",
            "location": [16.9780, 81.7830]  # [lat, lon]
        },
        {
            "id": "work",
            "name": "Work",
            "address": "456 Tech Park, Rajahmundry",
            "location": [16.9790, 81.7795]  # [lat, lon]
        }
    ]

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
