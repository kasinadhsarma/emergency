from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import cv2
import numpy as np
from datetime import datetime
import shutil
import logging
import sys
import os
import re  # Add this import at the top if not already present
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.detection import EmergencyVehicleDetector
import base64
from io import BytesIO
from PIL import Image
from utils.pathfinding import calculate_optimal_path
from utils.location import get_nearest_stations, bbox_to_location

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """Application configuration"""
    API_VERSION = "1.0.0"
    API_TITLE = "Emergency Response API"
    API_DESCRIPTION = "API for emergency vehicle detection and response management"

    UPLOAD_FOLDER = 'uploads'
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Initialize FastAPI app
app = FastAPI(
    title=Config.API_TITLE,
    description=Config.API_DESCRIPTION,
    version=Config.API_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

def validate_file(file: UploadFile, allowed_extensions: set) -> tuple[bool, str]:
    """Validate uploaded file format and size"""
    if not file.filename:
        return False, "No filename provided"

    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
    if file_ext not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"

    try:
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)

        if size > Config.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum limit of {Config.MAX_FILE_SIZE/1024/1024}MB"

        if size == 0:
            return False, "File is empty"
    except Exception as e:
        logger.error(f"Error validating file: {str(e)}")
        return False, f"Error validating file: {str(e)}"

    return True, ""

async def save_upload_file(file: UploadFile) -> str:
    """Save uploaded file and return filepath"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize filename to remove problematic characters
        safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename)
        filename = f"{timestamp}_{safe_filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        # Ensure the parent directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved successfully: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

def cleanup_file(filepath: str):
    """Background task to cleanup uploaded files"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Cleaned up file: {filepath}")
    except FileNotFoundError:
        logger.warning(f"File not found for cleanup: {filepath}")
    except Exception as e:
        logger.error(f"Error cleaning up file {filepath}: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": Config.API_VERSION
    }

# Initialize detector at module level
detector = EmergencyVehicleDetector()

async def process_and_encode_image(filepath: str, detections: list) -> str:
    try:
        img = cv2.imread(filepath)
        if img is None:
            raise ValueError("Could not read image")

        for det in detections:
            try:
                # Ensure all values are properly converted to float
                bbox = [float(coord) for coord in det['bbox']]
                conf = float(det['confidence'])
                class_name = str(det['class_name'])

                # Draw bounding box
                cv2.rectangle(
                    img,
                    (int(bbox[0]), int(bbox[1])),
                    (int(bbox[2]), int(bbox[3])),
                    (0, 255, 0),
                    2
                )

                # Draw label
                label = f"{class_name} {conf:.2f}"
                cv2.putText(
                    img,
                    label,
                    (int(bbox[0]), int(bbox[1] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )
            except Exception as e:
                logger.error(f"Error drawing detection: {e}")
                continue

        # Convert to RGB for PIL
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)

        # Save to bytes
        img_byte_arr = BytesIO()
        pil_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Encode to base64
        base64_encoded = base64.b64encode(img_byte_arr).decode('utf-8')
        return f"data:image/png;base64,{base64_encoded}"

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return None

@app.post("/api/detect/video")
async def detect_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Detect emergency vehicles in video
    """
    logger.info(f"Received video detection request for file: {file.filename}")

    # Validate video file
    is_valid, error_message = validate_file(file, Config.ALLOWED_VIDEO_EXTENSIONS)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    try:
        # Save and process file
        filepath = await save_upload_file(file)

        # Use detector instance instead of undefined function
        detections = detector.detect_in_video(filepath)

        # Define emergency mapping outside the loop
        emergency_mapping = {
            'Ambulance': 'MEDICAL',
            'Fire_Engine': 'FIRE',
            'Police': 'POLICE'
        }

        # Get the last frame or a representative frame
        cap = cv2.VideoCapture(filepath)
        ret, frame = cap.read()
        cap.release()

        if ret:
            # Save frame temporarily
            frame_path = filepath + "_last_frame.jpg"
            cv2.imwrite(frame_path, frame)

            # Process frame with detections
            processed_image = await process_and_encode_image(frame_path, detections)

            # Cleanup frame
            background_tasks.add_task(cleanup_file, frame_path)
        else:
            processed_image = None

        # Process results
        emergency_detected = len(detections) > 0
        max_confidence = max((float(d['confidence']) for d in detections), default=0.0)

        # Generate random locations around Rajahmundry for each vehicle type
        base_lat, base_lng = 16.9927, 81.7800  # Rajahmundry center
        routes = []

        for det in detections:
            # Generate a random offset (±0.01 degrees, roughly 1km)
            random_lat = base_lat + np.random.uniform(-0.01, 0.01)
            random_lng = base_lng + np.random.uniform(-0.01, 0.01)

            vehicle_type = det['class_name']

            # Add mapping using external emergency_mapping
            emergency_type = emergency_mapping.get(vehicle_type, 'UNKNOWN')

            # Add location to detection
            det['location'] = {
                'lat': float(random_lat),
                'lng': float(random_lng)
            }

            # Get nearest station based on vehicle type
            nearest_stations = get_nearest_stations([random_lat, random_lng], emergency_type)
            if nearest_stations and len(nearest_stations) > 0:
                nearest_station = nearest_stations[0]
                route = calculate_optimal_path(
                    [random_lat, random_lng],
                    [float(nearest_station['location']['lat']), float(nearest_station['location']['lng'])]
                )
                routes.append(route)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "emergencyDetected": emergency_detected,
                "detections": detections,
                "confidence": max_confidence,
                "emergencyType": emergency_mapping.get(detections[0]['class_name'], 'UNKNOWN') if detections else None,
                "timestamp": datetime.now().isoformat(),
                "processedImage": processed_image,
                "routes": routes
            }
        )

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        if 'filepath' in locals():
            background_tasks.add_task(cleanup_file, filepath)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/detect/image")
async def detect_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    try:
        is_valid, error_message = validate_file(file, Config.ALLOWED_IMAGE_EXTENSIONS)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)

        filepath = await save_upload_file(file)

        # Get detections
        detections = detector.detect_in_image(filepath)

        # Process image with detections
        processed_image = await process_and_encode_image(filepath, detections)

        # Map vehicle types to emergency types with standardized names
        vehicle_to_emergency = {
            'Police': 'POLICE',
            'Ambulance': 'MEDICAL',
            'Fire_Engine': 'FIRE'
        }

        emergency_detected = False
        emergency_type = None
        routes = []

        # Process detections
        if detections:
            for det in detections:
                # Ensure class name is standardized
                vehicle_type = det['class_name']
                if vehicle_type in vehicle_to_emergency:
                    emergency_detected = True
                    emergency_type = vehicle_to_emergency[vehicle_type]

                    # Generate random location for demo
                    base_lat, base_lng = 16.9927, 81.7800
                    location_obj = {
                        'lat': base_lat + np.random.uniform(-0.01, 0.01),
                        'lng': base_lng + np.random.uniform(-0.01, 0.01)
                    }
                    det['location'] = location_obj

                    # Get nearest station
                    nearest_stations = get_nearest_stations(
                        [location_obj['lat'], location_obj['lng']],
                        emergency_type
                    )

                    if nearest_stations:
                        route = calculate_optimal_path(
                            [location_obj['lat'], location_obj['lng']],
                            [nearest_stations[0]['location']['lat'],
                             nearest_stations[0]['location']['lng']]
                        )
                        routes.append(route)

        # Clean up
        background_tasks.add_task(cleanup_file, filepath)

        return JSONResponse(
            status_code=200,
            content={
                "status": "Emergency" if emergency_detected else "Clear",
                "emergencyDetected": emergency_detected,
                "detections": detections,
                "confidence": max((float(d['confidence']) for d in detections), default=0.0),
                "emergencyType": emergency_type,
                "type": emergency_type,  # Add explicit type field
                "timestamp": datetime.now().isoformat(),
                "processedImage": processed_image,
                "detectedVehicles": ", ".join(d['class_name'] for d in detections) if detections else "",
                "routes": routes
            }
        )

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        if 'filepath' in locals():
            background_tasks.add_task(cleanup_file, filepath)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stations")
async def get_stations():
    """
    Get list of stations
    """
    # Return station data matching the StationData type expected by frontend
    return JSONResponse(
        status_code=200,
        content={
            "ambulanceStations": [
                {"id": 1, "name": "City Hospital", "location": {"lat": 16.9927, "lng": 81.7800}, "type": "MEDICAL"},
                {"id": 2, "name": "General Hospital", "location": {"lat": 16.9827, "lng": 81.7700}, "type": "MEDICAL"}
            ],
            "fireStations": [
                {"id": 3, "name": "Central Fire Station", "location": {"lat": 16.9927, "lng": 81.7900}, "type": "FIRE"},
                {"id": 4, "name": "North Fire Station", "location": {"lat": 17.0027, "lng": 81.7800}, "type": "FIRE"}
            ],
            "policeStations": [
                {"id": 5, "name": "City Police HQ", "location": {"lat": 16.9927, "lng": 81.7700}, "type": "POLICE"},
                {"id": 6, "name": "Traffic Police Station", "location": {"lat": 16.9827, "lng": 81.7800}, "type": "POLICE"}
            ]
        }
    )

@app.post("/api/route")
async def calculate_route(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    emergency_type: str
):
    """
    Calculate optimal route from start to end location
    """
    try:
        start = [start_lat, start_lng]
        end = [end_lat, end_lng]
        route = calculate_optimal_path(start, end, emergency_type)
        return JSONResponse(
            status_code=200,
            content=route
        )
    except Exception as e:
        logger.error(f"Error calculating route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traffic-patterns")
async def get_traffic_patterns():
    """
    Get daily traffic patterns
    """
    try:
        # Mock data for daily traffic patterns
        traffic_patterns = [
            {"time": "00:00", "flow": 10},
            {"time": "01:00", "flow": 15},
            {"time": "02:00", "flow": 12},
            {"time": "03:00", "flow": 8},
            {"time": "04:00", "flow": 5},
            {"time": "05:00", "flow": 7},
            {"time": "06:00", "flow": 20},
            {"time": "07:00", "flow": 35},
            {"time": "08:00", "flow": 50},
            {"time": "09:00", "flow": 60},
            {"time": "10:00", "flow": 55},
            {"time": "11:00", "flow": 50},
            {"time": "12:00", "flow": 45},
            {"time": "13:00", "flow": 40},
            {"time": "14:00", "flow": 35},
            {"time": "15:00", "flow": 30},
            {"time": "16:00", "flow": 25},
            {"time": "17:00", "flow": 20},
            {"time": "18:00", "flow": 15},
            {"time": "19:00", "flow": 10},
            {"time": "20:00", "flow": 8},
            {"time": "21:00", "flow": 6},
            {"time": "22:00", "flow": 5},
            {"time": "23:00", "flow": 4}
        ]
        return JSONResponse(
            status_code=200,
            content=traffic_patterns
        )
    except Exception as e:
        logger.error(f"Error fetching traffic patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/historical-data")
async def get_historical_data():
    """
    Get historical traffic data
    """
    try:
        # Mock data for historical traffic impact by conditions
        historical_data = [
            {"condition": "Rain", "impact": 30},
            {"condition": "Snow", "impact": 50},
            {"condition": "Clear", "impact": 10},
            {"condition": "Fog", "impact": 20},
            {"condition": "Wind", "impact": 15}
        ]
        return JSONResponse(
            status_code=200,
            content=historical_data
        )
    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Resource not found",
            "path": request.url.path
        }
    )

@app.exception_handler(500)
async def server_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
