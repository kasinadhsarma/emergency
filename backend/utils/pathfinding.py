import osmnx as ox
import networkx as nx
from typing import Tuple, List, Dict
import folium
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import numpy as np

@dataclass
class Location:
    name: str
    lat: float
    lon: float
    type: str  # 'hospital', 'fire_station', 'police_station'

class PathFinder:
    def __init__(self):
        """Initialize the PathFinder with OpenStreetMap data"""
        # Cache for graph data
        self._graph = None
        self._emergency_locations: Dict[str, List[Location]] = {
            'hospital': [],
            'fire_station': [],
            'police_station': []
        }

    def load_area_graph(self, city: str):
        """Load the road network graph for a specific city"""
        try:
            self._graph = ox.graph_from_place(city, network_type='drive')
            self._graph = ox.add_edge_speeds(self._graph)
            self._graph = ox.add_edge_travel_times(self._graph)
        except Exception as e:
            raise Exception(f"Failed to load graph for {city}: {e}")

    def add_emergency_location(self, location: Location):
        """Add an emergency service location to the system"""
        if location.type not in self._emergency_locations:
            raise ValueError(f"Invalid location type: {location.type}")
        self._emergency_locations[location.type].append(location)

    def _get_nearest_node(self, lat: float, lon: float) -> int:
        """Get the nearest node in the road network to a point"""
        return ox.nearest_nodes(self._graph, lon, lat)

    def _calculate_route(self, start_node: int, end_node: int,
                        traffic_weights: Dict[int, float] = None) -> Tuple[List[int], float, Dict[int, float]]:
        """Calculate the optimal route between two nodes"""
        if traffic_weights:
            # Apply traffic density weights to travel times
            for edge in self._graph.edges:
                edge_id = edge[2]
                if edge_id in traffic_weights:
                    self._graph.edges[edge]['weight'] = (
                        self._graph.edges[edge]['travel_time'] *
                        traffic_weights[edge_id]
                    )
                else:
                    self._graph.edges[edge]['weight'] = self._graph.edges[edge]['travel_time']

        try:
            route = nx.shortest_path(
                self._graph,
                start_node,
                end_node,
                weight='weight'
            )
            route_length = sum(
                self._graph.edges[edge]['length']
                for edge in zip(route[:-1], route[1:])
            )
            return route, route_length, traffic_weights
        except nx.NetworkXNoPath:
            return None, None, None

    def find_optimal_route(self,
                          current_lat: float,
                          current_lon: float,
                          vehicle_type: str,
                          traffic_weights: Dict[int, float] = None) -> Tuple[List[Tuple[float, float]], Location, Dict[int, float]]:
        """
        Find the optimal route to the nearest appropriate emergency service location

        Args:
            current_lat: Current latitude
            current_lon: Current longitude
            vehicle_type: Type of emergency vehicle ('ambulance', 'fire_engine', 'police')
            traffic_weights: Dictionary of edge IDs to traffic density weights

        Returns:
            Tuple of (route coordinates, destination location)
        """
        if not self._graph:
            raise ValueError("No area graph loaded. Call load_area_graph first.")

        # Map vehicle types to location types
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
            raise ValueError(f"No {location_type}s registered in the system")

        start_node = self._get_nearest_node(current_lat, current_lon)

        # Find best route to each possible destination in parallel
        best_route = None
        best_length = float('inf')
        best_location = None
        best_traffic_weights = None

        def process_location(loc: Location) -> Tuple[List[int], float, Location, Dict[int, float]]:
            end_node = self._get_nearest_node(loc.lat, loc.lon)
            route, length, traffic_weights = self._calculate_route(start_node, end_node, traffic_weights)
            return route, length, loc, traffic_weights

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_location, loc)
                for loc in locations
            ]

            for future in futures:
                route, length, loc, traffic_weights = future.result()
                if route and length < best_length:
                    best_route = route
                    best_length = length
                    best_location = loc
                    best_traffic_weights = traffic_weights

        if not best_route:
            raise ValueError("No valid route found to any appropriate destination")

        # Convert node IDs to coordinates
        route_coords = [
            (self._graph.nodes[node]['y'], self._graph.nodes[node]['x'])
            for node in best_route
        ]

        return route_coords, best_location, best_traffic_weights

    def visualize_route(self, route_coords: List[Tuple[float, float]],
                       destination: Location) -> folium.Map:
        """Create an interactive map visualization of the route"""
        # Create base map centered on route
        center_lat = sum(lat for lat, _ in route_coords) / len(route_coords)
        center_lon = sum(lon for _, lon in route_coords) / len(route_coords)
        m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

        # Draw route
        folium.PolyLine(
            route_coords,
            weight=2,
            color='red',
            opacity=0.8
        ).add_to(m)

        # Add markers for start and end points
        folium.Marker(
            route_coords[0],
            popup='Start',
            icon=folium.Icon(color='green')
        ).add_to(m)

        folium.Marker(
            [destination.lat, destination.lon],
            popup=f'{destination.name}\n{destination.type}',
            icon=folium.Icon(color='red')
        ).add_to(m)

        return m
