from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
from pathlib import Path
import cv2
import numpy as np
from typing import List, Optional
import json
from pydantic import BaseModel
import io

from utils.detection import VehicleDetector
from utils.pathfinding import PathFinder, Location

app = FastAPI(title="Emergency Vehicle Detection & Routing")

# Initialize our components
detector = VehicleDetector(model_path='models/yolov8_custom.pt')
pathfinder = PathFinder()

# Load emergency locations from JSON (you would typically load this from a database)
EMERGENCY_LOCATIONS = {
    'hospital': [
        Location("City Hospital", 12.9716, 77.5946, "hospital"),
        Location("General Hospital", 12.9783, 77.5933, "hospital")
    ],
    'fire_station': [
        Location("Central Fire Station", 12.9757, 77.5921, "fire_station"),
        Location("City Fire Station", 12.9692, 77.5945, "fire_station")
    ],
    'police_station': [
        Location("Central Police Station", 12.9716, 77.5946, "police_station"),
        Location("City Police Station", 12.9683, 77.5930, "police_station")
    ]
}

# Register emergency locations
for locations in EMERGENCY_LOCATIONS.values():
    for location in locations:
        pathfinder.add_emergency_location(location)

# Load city graph (you would typically do this based on the area of operation)
pathfinder.load_area_graph("Bangalore, India")

class RouteRequest(BaseModel):
    vehicle_type: str
    current_lat: float
    current_lon: float
    traffic_weights: Optional[dict] = None

@app.post("/detect/image")
async def detect_image(file: UploadFile = File(...)):
    """Detect emergency vehicles in an image"""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")
        
    detections = detector.detect_frame(img)
    
    # Convert detections to JSON-serializable format
    results = [
        {
            "class": det.class_name,
            "confidence": det.confidence,
            "bbox": det.bbox.tolist()
        }
        for det in detections
    ]
    
    return {"detections": results}

@app.post("/detect/video")
async def detect_video(file: UploadFile = File(...)):
    """Process video and return detections"""
    # Save uploaded video temporarily
    temp_path = Path("temp_video.mp4")
    with temp_path.open("wb") as f:
        f.write(await file.read())
    
    try:
        # Process video
        all_detections = []
        for frame_detections in detector.process_video(str(temp_path)):
            frame_results = [
                {
                    "class": det.class_name,
                    "confidence": det.confidence,
                    "bbox": det.bbox.tolist(),
                    "frame": det.frame_number,
                    "timestamp": det.timestamp
                }
                for det in frame_detections
            ]
            all_detections.extend(frame_results)
            
        return {"detections": all_detections}
        
    finally:
        # Cleanup
        temp_path.unlink()

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
        
        # Create route visualization
        map_vis = pathfinder.visualize_route(route_coords, destination)
        
        # Save map to bytes
        map_data = io.BytesIO()
        map_vis.save(map_data, close_file=False)
        map_data.seek(0)
        
        return StreamingResponse(
            map_data,
            media_type="text/html",
            headers={
                "Content-Disposition": "inline; filename=route_map.html"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/locations")
async def get_locations():
    """Get all emergency locations"""
    return {"locations": EMERGENCY_LOCATIONS}

@app.get("/api/vehicles")
async def get_vehicles():
    """Get all vehicles"""
    return {"vehicles": pathfinder.get_vehicles()}

@app.get("/api/requests")
async def get_requests():
    """Get all emergency requests"""
    return {"requests": pathfinder.get_requests()}

@app.get("/api/stations")
async def get_stations():
    """Get all stations"""
    return {"stations": pathfinder.get_stations()}

@app.post("/api/set_emergency_contacts")
async def set_emergency_contacts(contacts: List[EmergencyContact]):
    """Set emergency contacts"""
    # Save contacts to a database or file
    # For simplicity, we'll just print them
    for contact in contacts:
        print(f"Set emergency contact: {contact.type} - {contact.number}")
    return {"message": "Emergency contacts set successfully"}

@app.get("/api/medical_information")
async def get_medical_information():
    """Get medical information"""
    # Fetch medical information from a database or file
    # For simplicity, we'll just return a static response
    return {"medical_information": "This is a sample medical information."}

@app.get("/api/saved_locations")
async def get_saved_locations():
    """Get saved locations"""
    # Fetch saved locations from a database or file
    # For simplicity, we'll just return a static response
    return {"saved_locations": ["Home", "Work", "Gym"]}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
