import torch
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import functional as F
from PIL import Image
import cv2
import numpy as np
import os

# Load the trained model
model = fasterrcnn_resnet50_fpn(pretrained=False)
model.load_state_dict(torch.load("backend/yolo_model/yolo_model.pth"))
model.eval()

# Define the transformations
def get_transform():
    return F.Compose([
        F.ToTensor()
    ])

# Function to detect emergency vehicles in an image
def detect_emergency_vehicles(image):
    transform = get_transform()
    img = Image.fromarray(image)
    img = transform(img)
    img = img.unsqueeze(0)
    with torch.no_grad():
        predictions = model(img)
    return predictions

# Function to process video input
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        predictions = detect_emergency_vehicles(frame)
        for prediction in predictions:
            for box in prediction['boxes']:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            # Determine vehicle type (placeholder logic)
            vehicle_type = determine_vehicle_type(prediction['labels'])
            # Add pathfinding logic here
            optimal_path = find_optimal_path(frame, predictions, vehicle_type)
            for path in optimal_path:
                cv2.line(frame, path[0], path[1], (0, 0, 255), 2)
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Function to find the optimal path
def find_optimal_path(frame, predictions, vehicle_type):
    # Placeholder for pathfinding logic
    # This function should return a list of paths
    # For simplicity, we'll use a basic A* algorithm to find the optimal path
    from queue import PriorityQueue

    def heuristic(a, b):
        return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

    def astar(start, goal, grid):
        open_set = PriorityQueue()
        open_set.put((0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}

        while not open_set.empty():
            current = open_set.get()[1]

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            for neighbor in get_neighbors(current, grid):
                tentative_g_score = g_score[current] + heuristic(current, neighbor)

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    open_set.put((f_score[neighbor], neighbor))

        return []

    def get_neighbors(node, grid):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for direction in directions:
            neighbor = (node[0] + direction[0], node[1] + direction[1])
            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1] and grid[neighbor[0], neighbor[1]] == 0:
                neighbors.append(neighbor)
        return neighbors

    # Create a grid representation of the frame
    grid = np.zeros((frame.shape[0], frame.shape[1]), dtype=int)
    for prediction in predictions:
        for box in prediction['boxes']:
            x1, y1, x2, y2 = box
            grid[int(y1):int(y2), int(x1):int(x2)] = 1

    # Define start and goal points based on vehicle type
    start = (0, 0)
    if vehicle_type == 'ambulance':
        goal = (frame.shape[0] - 1, frame.shape[1] - 1)  # Example goal for ambulance
    elif vehicle_type == 'fire_engine':
        goal = (frame.shape[0] - 1, 0)  # Example goal for fire engine
    elif vehicle_type == 'police':
        goal = (0, frame.shape[1] - 1)  # Example goal for police
    else:
        goal = (frame.shape[0] - 1, frame.shape[1] - 1)  # Default goal

    # Find the optimal path
    path = astar(start, goal, grid)

    # Convert path to a list of line segments
    optimal_path = []
    for i in range(len(path) - 1):
        optimal_path.append((path[i], path[i + 1]))

    return optimal_path

# Function to process image input
def process_image(image_path):
    image = cv2.imread(image_path)
    predictions = detect_emergency_vehicles(image)
    for prediction in predictions:
        for box in prediction['boxes']:
            x1, y1, x2, y2 = box
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        # Determine vehicle type (placeholder logic)
        vehicle_type = determine_vehicle_type(prediction['labels'])
        # Add pathfinding logic here
        optimal_path = find_optimal_path(image, predictions, vehicle_type)
        for path in optimal_path:
            cv2.line(image, path[0], path[1], (0, 0, 255), 2)
    cv2.imshow('Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Function to determine vehicle type
def determine_vehicle_type(labels):
    # Placeholder logic to determine vehicle type based on labels
    if 1 in labels:  # Assuming label 1 corresponds to ambulance
        return 'ambulance'
    elif 2 in labels:  # Assuming label 2 corresponds to fire engine
        return 'fire_engine'
    elif 3 in labels:  # Assuming label 3 corresponds to police
        return 'police'
    else:
        return 'unknown'

# Example usage
if __name__ == "__main__":
    video_path = "path/to/your/video.mp4"
    process_video(video_path)
