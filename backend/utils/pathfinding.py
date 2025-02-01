from typing import List, Tuple, Dict
import numpy as np
from .location import calculate_distance, get_path_traffic_density

class Node:
    def __init__(self, position: List[float], g: float = float('inf'), 
                 h: float = 0, parent = None):
        self.position = position
        self.g = g  # Cost from start to current node
        self.h = h  # Heuristic (estimated cost from current node to goal)
        self.f = g + h  # Total cost
        self.parent = parent

def heuristic(start: List[float], goal: List[float]) -> float:
    """
    Calculate heuristic cost between two points using Haversine distance
    """
    return calculate_distance(start, goal)

def get_neighbors(position: List[float], grid_size: float = 0.001) -> List[List[float]]:
    """
    Generate neighboring points in a grid
    """
    lat, lon = position
    neighbors = []
    for d_lat in [-grid_size, 0, grid_size]:
        for d_lon in [-grid_size, 0, grid_size]:
            if d_lat == 0 and d_lon == 0:
                continue
            neighbors.append([lat + d_lat, lon + d_lon])
    return neighbors

def calculate_optimal_path(
    start: List[float],
    end: List[float],
    emergency_type: str = 'MEDICAL',
    traffic_threshold: float = 70.0
) -> Dict:
    """
    Calculate optimal path using A* algorithm with traffic consideration
    """
    start_node = Node(start, g=0, h=heuristic(start, end))
    open_list = [start_node]
    closed_list = []
    
    max_iterations = 100  # Limit iterations for performance
    iterations = 0
    
    while open_list and iterations < max_iterations:
        iterations += 1
        
        # Get node with lowest total cost
        current = min(open_list, key=lambda x: x.f)
        
        if calculate_distance(current.position, end) < 0.1:  # Within 100m
            # Reconstruct path
            path = []
            current_node = current
            while current_node:
                path.append({
                    'position': current_node.position,
                    'traffic_density': get_path_traffic_density(
                        current_node.position,
                        current_node.parent.position if current_node.parent else current_node.position
                    )
                })
                current_node = current_node.parent
            
            # Calculate path metrics
            total_distance = sum(calculate_distance(path[i]['position'], path[i-1]['position']) 
                               for i in range(1, len(path)))
            avg_traffic = np.mean([p['traffic_density'] for p in path])
            
            return {
                'path': list(reversed(path)),
                'total_distance': round(total_distance, 2),
                'average_traffic_density': round(avg_traffic, 2),
                'emergency_type': emergency_type
            }
        
        open_list.remove(current)
        closed_list.append(current)
        
        # Generate neighbors
        for neighbor_pos in get_neighbors(current.position):
            if any(n.position == neighbor_pos for n in closed_list):
                continue
                
            # Calculate costs
            traffic_density = get_path_traffic_density(current.position, neighbor_pos)
            traffic_penalty = 2.0 if traffic_density > traffic_threshold else 1.0
            movement_cost = calculate_distance(current.position, neighbor_pos) * traffic_penalty
            
            tentative_g = current.g + movement_cost
            
            neighbor = next((n for n in open_list if n.position == neighbor_pos), None)
            if not neighbor:
                neighbor = Node(
                    neighbor_pos,
                    g=tentative_g,
                    h=heuristic(neighbor_pos, end),
                    parent=current
                )
                open_list.append(neighbor)
            elif tentative_g < neighbor.g:
                neighbor.g = tentative_g
                neighbor.f = neighbor.g + neighbor.h
                neighbor.parent = current
    
    # If no path found, return straight line with traffic info
    direct_path = [{
        'position': start,
        'traffic_density': get_path_traffic_density(start, end)
    }, {
        'position': end,
        'traffic_density': get_path_traffic_density(start, end)
    }]
    
    return {
        'path': direct_path,
        'total_distance': calculate_distance(start, end),
        'average_traffic_density': direct_path[0]['traffic_density'],
        'emergency_type': emergency_type,
        'note': 'Direct path used - optimal path not found'
    }
