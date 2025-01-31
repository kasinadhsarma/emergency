import osmnx as ox
import networkx as nx
from typing import Tuple, List, Dict, Optional
import folium
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

ox.settings.log_console = True
ox.settings.use_cache = True

@dataclass
class Location:
    name: str
    lat: float
    lon: float
    type: str  # 'hospital', 'fire_station', 'police_station'

class PathFinder:
    def __init__(self):
        """Initialize the PathFinder with OpenStreetMap data"""
        self._graph = None
        self._emergency_locations: Dict[str, List[Location]] = {
            'hospital': [],
            'fire_station': [],
            'police_station': []
        }

    def load_area_boundary(self, boundary: Dict[str, float]):
        """Load the road network graph for a specific area boundary"""
        required_keys = ['north', 'south', 'east', 'west']
        if not all(key in boundary for key in required_keys):
            raise ValueError(f"Boundary must contain {required_keys} keys")
        
        try:
            self._graph = ox.graph_from_bbox(
                boundary['north'],
                boundary['south'],
                boundary['east'],
                boundary['west'],
                network_type='drive',
                simplify=True,
                truncate_by_edge=True
            )
            self._graph = ox.add_edge_speeds(self._graph)
            self._graph = ox.add_edge_travel_times(self._graph)
        except Exception as e:
            raise RuntimeError(f"Failed to load graph: {e}")

    def add_emergency_location(self, location: Location):
        """Add an emergency service location to the system"""
        if location.type not in self._emergency_locations:
            raise ValueError(f"Invalid location type: {location.type}")
        self._emergency_locations[location.type].append(location)

    def _get_nearest_node(self, lat: float, lon: float) -> int:
        """Get the nearest node in the road network to a point"""
        return ox.nearest_nodes(self._graph, lon, lat)

    def _calculate_route(self, 
                        start_node: int, 
                        end_node: int,
                        traffic_weights: Optional[Dict[int, float]] = None
                        ) -> Tuple[Optional[List[int]], Optional[float]]:
        """Calculate the optimal route between two nodes"""
        try:
            weight = 'travel_time'
            if traffic_weights:
                def weight_func(u, v, d):
                    base_time = d.get('travel_time', 1)
                    osm_id = d.get('osmid', '')
                    if isinstance(osm_id, list):
                        for oid in osm_id:
                            if oid in traffic_weights:
                                return base_time * traffic_weights[oid]
                        return base_time
                    return base_time * traffic_weights.get(osm_id, 1.0)
                weight = weight_func

            route = nx.shortest_path(
                self._graph, 
                start_node, 
                end_node, 
                weight=weight
            )
            
            # Calculate route length
            length = 0.0
            for u, v in zip(route[:-1], route[1:]):
                edge_data = self._graph.get_edge_data(u, v)
                if edge_data:
                    # Get first edge (assuming simplified graph)
                    key = next(iter(edge_data))
                    length += edge_data[key].get('length', 0)
            
            return route, length
        except nx.NetworkXNoPath:
            return None, None
        except Exception as e:
            print(f"Route calculation failed: {e}")
            return None, None

    def find_optimal_route(self,
                          current_lat: float,
                          current_lon: float,
                          vehicle_type: str,
                          traffic_weights: Optional[Dict[int, float]] = None
                          ) -> Tuple[List[Tuple[float, float]], Location]:
        """Find optimal route to nearest appropriate emergency service"""
        if not self._graph:
            raise RuntimeError("No graph loaded. Call load_area_boundary first.")

        type_map = {
            'ambulance': 'hospital',
            'fire_engine': 'fire_station',
            'police': 'police_station'
        }
        location_type = type_map.get(vehicle_type.lower())
        if not location_type:
            raise ValueError(f"Invalid vehicle type: {vehicle_type}")

        locations = self._emergency_locations[location_type]
        if not locations:
            raise ValueError(f"No {location_type}s available")

        start_node = self._get_nearest_node(current_lat, current_lon)

        best_route = None
        best_length = float('inf')
        best_location = None

        with ThreadPoolExecutor() as executor:
            futures = []
            for loc in locations:
                futures.append(executor.submit(
                    self._process_location,
                    start_node,
                    loc,
                    traffic_weights
                ))

            for future in futures:
                route, length, loc = future.result()
                if route and length < best_length:
                    best_route = route
                    best_length = length
                    best_location = loc

        if not best_route:
            raise RuntimeError("No valid route found")

        route_coords = [
            (self._graph.nodes[node]['y'], self._graph.nodes[node]['x'])
            for node in best_route
        ]
        return route_coords, best_location

    def _process_location(self, start_node, loc, traffic_weights):
        end_node = self._get_nearest_node(loc.lat, loc.lon)
        route, length = self._calculate_route(start_node, end_node, traffic_weights)
        return route, length, loc

    def visualize_route(self, 
                       route_coords: List[Tuple[float, float]], 
                       destination: Location
                       ) -> folium.Map:
        """Create an interactive map visualization of the route"""
        m = folium.Map(
            location=[route_coords[0][0], route_coords[0][1]], 
            zoom_start=13
        )
        
        folium.PolyLine(
            route_coords,
            color='red',
            weight=2.5,
            opacity=0.8
        ).add_to(m)
        
        folium.Marker(
            route_coords[0],
            popup='Start',
            icon=folium.Icon(color='green')
        ).add_to(m)
        
        folium.Marker(
            [destination.lat, destination.lon],
            popup=f'{destination.name} ({destination.type})',
            icon=folium.Icon(color='blue')
        ).add_to(m)
        
        return m
