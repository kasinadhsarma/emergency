import math
from typing import List, Dict, Tuple, Optional, Union
import numpy as np

def calculate_distance(point1: List[float], point2: List[float]) -> float:
    """
    Calculate Haversine distance between two points
    """
    lat1, lon1 = point1
    lat2, lon2 = point2
    
    R = 6371  # Earth's radius in kilometers

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = math.sin(d_lat/2) * math.sin(d_lat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(d_lon/2) * math.sin(d_lon/2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def get_nearest_stations(location: List[float], emergency_type: str) -> List[Dict]:
    """
    Get nearest emergency stations based on location and emergency type.
    Uses mock data for demonstration.
    """
    base_lat, base_lng = 16.9927, 81.7800  # Rajahmundry center
    
    # Mock station data with random offsets
    stations = {
        'MEDICAL': [
            {"id": 1, "name": "City Hospital", "type": "MEDICAL"},
            {"id": 2, "name": "General Hospital", "type": "MEDICAL"}
        ],
        'FIRE': [
            {"id": 3, "name": "Central Fire Station", "type": "FIRE"},
            {"id": 4, "name": "North Fire Station", "type": "FIRE"}
        ],
        'POLICE': [
            {"id": 5, "name": "City Police HQ", "type": "POLICE"},
            {"id": 6, "name": "Traffic Police Station", "type": "POLICE"}
        ]
    }
    
    # Get relevant stations based on emergency type
    relevant_stations = stations.get(emergency_type, [])
    
    # Add random locations to stations
    for station in relevant_stations:
        station['location'] = {
            'lat': base_lat + np.random.uniform(-0.02, 0.02),
            'lng': base_lng + np.random.uniform(-0.02, 0.02)
        }
    
    return relevant_stations

def bbox_to_location(bbox: List[float], image_dims: tuple, reference_coords: List[float]) -> Dict[str, float]:
    """
    Convert bounding box to geo coordinates using reference point
    """
    base_lat, base_lng = reference_coords
    
    # Generate a location with small random offset from reference point
    return {
        'lat': base_lat + np.random.uniform(-0.01, 0.01),
        'lng': base_lng + np.random.uniform(-0.01, 0.01)
    }

def get_path_traffic_density(start: List[float], end: List[float]) -> float:
    """
    Calculate traffic density between two points
    This is a mock implementation - in production this would use real traffic data
    """
    # Mock traffic density calculation
    distance = calculate_distance(start, end)
    # Generate semi-random traffic density based on distance
    base_density = 50  # Base traffic density
    distance_factor = math.sin(distance * math.pi) * 20  # Variation based on distance
    random_factor = np.random.normal(0, 10)  # Random variation
    
    density = base_density + distance_factor + random_factor
    return max(0, min(100, density))  # Clamp between 0 and 100
