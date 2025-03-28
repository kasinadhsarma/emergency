# UML Diagrams

## 5.2.1 Use Case Diagram

```mermaid
graph TB
    %% Actors
    Dispatcher((Dispatcher))
    Driver((Emergency Vehicle Driver))
    System((System))
    
    %% Use Cases
    DetectVehicle[Detect Emergency Vehicle]
    OptimizeRoute[Optimize Route]
    ProcessVideo[Process Video Feed]
    ManageAlerts[Manage Alerts]
    ViewRoute[View Route]
    UpdateLocation[Update Vehicle Location]
    
    %% Relationships
    Dispatcher --> DetectVehicle
    Dispatcher --> ManageAlerts
    Dispatcher --> ViewRoute
    Driver --> UpdateLocation
    Driver --> ViewRoute
    
    System --> ProcessVideo
    ProcessVideo --> DetectVehicle
    DetectVehicle --> OptimizeRoute
    OptimizeRoute --> ViewRoute
    UpdateLocation --> OptimizeRoute
```

## 5.2.2 Class Diagram

```mermaid
classDiagram
    class VideoProcessor {
        -model: YOLOModel
        -frame_buffer: Array
        +process_frame(frame: Image)
        +detect_emergency_vehicle(frame: Image)
        +get_vehicle_location()
    }
    
    class ObjectDetection {
        -model_weights: String
        -confidence_threshold: Float
        +load_model()
        +predict(frame: Image)
        +filter_detections(predictions: Array)
    }
    
    class RouteOptimizer {
        -graph: Graph
        -current_route: Array
        +calculate_route(start: Point, end: Point)
        +update_route(vehicle_location: Point)
        +get_optimal_path()
    }
    
    class UserInterface {
        -map_view: MapComponent
        -alert_system: AlertSystem
        +display_route(route: Array)
        +show_vehicle_location(location: Point)
        +update_alerts(message: String)
    }
    
    class AlertSystem {
        -notification_queue: Queue
        +send_alert(message: String)
        +clear_alerts()
        +get_active_alerts()
    }
    
    VideoProcessor --> ObjectDetection
    RouteOptimizer --> UserInterface
    UserInterface --> AlertSystem
```

## 5.2.3 Sequence Diagram

```mermaid
sequenceDiagram
    participant D as Dispatcher
    participant UI as UserInterface
    participant VP as VideoProcessor
    participant OD as ObjectDetection
    participant RO as RouteOptimizer
    
    D->>UI: Initialize system
    UI->>VP: Start video processing
    
    loop Every Frame
        VP->>OD: Process frame
        OD-->>VP: Return detections
        
        alt Emergency Vehicle Detected
            VP->>UI: Alert detection
            UI->>D: Show alert
            VP->>RO: Send vehicle location
            RO->>RO: Calculate optimal route
            RO-->>UI: Update route display
            UI-->>D: Show updated route
        end
    end
    
    D->>UI: Acknowledge alert
    UI->>RO: Confirm route
    RO-->>UI: Provide turn-by-turn directions
    UI-->>D: Display navigation instructions
