import math
from typing import List, Dict, Tuple, Optional
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

def get_nearest_stations(location: List[float], emergency_type: str, stations: Dict = None) -> List[Dict]:
    """
    Find nearest emergency stations based on vehicle type and location
    """
    if stations is None:
        # Mock data - in production, this would come from a database
        stations = {
            'MEDICAL': [
                {'id': 1, 'name': 'Government General Hospital', 'location': {'lat': 17.0005, 'lng': 81.7800}},
                {'id': 2, 'name': 'Hope Hospital', 'location': {'lat': 16.9921, 'lng': 81.7743}},
                {'id': 3, 'name': 'KIMS Hospital', 'location': {'lat': 16.9867, 'lng': 81.7889}}
            ],
            'FIRE': [
                {'id': 4, 'name': 'Fire Station Rajahmundry', 'location': {'lat': 16.9891, 'lng': 81.7840}},
                {'id': 5, 'name': 'District Fire Office', 'location': {'lat': 16.9927, 'lng': 81.7756}}
            ],
            'POLICE': [
                {'id': 6, 'name': 'Three Town Police Station', 'location': {'lat': 16.9927, 'lng': 81.7875}},
                {'id': 7, 'name': 'Two Town Police Station', 'location': {'lat': 16.9867, 'lng': 81.7830}},
                {'id': 8, 'name': 'One Town Police Station', 'location': {'lat': 17.0012, 'lng': 81.7799}}
            ]
        }

    relevant_stations = stations.get(emergency_type.upper(), [])
    if not relevant_stations:
        return []

    # Calculate distances to all relevant stations
    stations_with_distances = []
    for station in relevant_stations:
        station_location = [station['location']['lat'], station['location']['lng']]
        distance = calculate_distance(location, station_location)
        stations_with_distances.append({
            **station,
            'distance': distance
        })

    # Sort by distance and return a random station
    sorted_stations = sorted(stations_with_distances, key=lambda x: x['distance'])
    if sorted_stations:
        return [sorted_stations[np.random.randint(len(sorted_stations))]]
    return []

def bbox_to_location(bbox: List[int], image_size: Tuple[int, int], 
                    reference_coords: Optional[List[float]] = None) -> Dict[str, float]:
    """
    Convert bounding box coordinates to geographical coordinates
    If reference coordinates are not provided, returns relative position
    """
    # Get center point of bounding box
    center_x = (bbox[0] + bbox[2]) / 2
    center_y = (bbox[1] + bbox[3]) / 2
    
    # Normalize to 0-1 range
    norm_x = center_x / image_size[0]
    norm_y = center_y / image_size[1]
    
    if reference_coords is None:
        # Return normalized coordinates if no reference point
        return {"lat": norm_y, "lng": norm_x}
    
    # Calculate actual coordinates based on reference point
    # This is a simplified calculation - in production you'd need proper geo-referencing
    lat_range = 0.1  # Approx 11km at equator
    lon_range = 0.1
    
    lat = reference_coords[0] + (norm_y - 0.5) * lat_range
    lon = reference_coords[1] + (norm_x - 0.5) * lon_range
    
    return {"lat": lat, "lng": lon}

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
