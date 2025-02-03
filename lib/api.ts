import { EmergencyType, StationLocation, StationData, Detection, DetectionResponse, NearestLocation } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export const getStations = async (): Promise<StationData> => {
  const response = await fetch(`${API_URL}/api/stations`);
  if (!response.ok) {
    throw new Error('Failed to fetch stations');
  }
  return response.json();
};

export const detectEmergencyInVideo = async (file: File): Promise<DetectionResponse> => {
  // Create a URL for the original video preview
  const originalVideoUrl = URL.createObjectURL(file);
  
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/api/detect/video`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error('Failed to detect emergency in video');
  }
  
  const result = await response.json();
  
  // Process detection results to match backend format
  const detections = result.detections || [];
  const emergencyDetected = detections.some((det: Detection) => 
    ['Ambulance', 'Fire_Engine', 'Police'].includes(det.class_name)
  );
  
  // Use emergency_mapping to derive the valid EmergencyType from the first detection
  const emergency_mapping: Record<string, EmergencyType> = {
    'Ambulance': 'MEDICAL',
    'Fire_Engine': 'FIRE',
    'Police': 'POLICE'
  };

  // Add return statement with results
  return {
    detections,
    emergencyDetected,
    type: emergencyDetected && detections.length > 0 ? (emergency_mapping[detections[0].class_name] || null) : null,
    emergencyType: emergencyDetected && detections.length > 0 ? (emergency_mapping[detections[0].class_name] || null) : null,
    confidence: 0,
    timestamp: new Date().toISOString(),
    status: emergencyDetected ? 'Emergency' : 'Clear',
    originalImage: URL.createObjectURL(file),
    processedImage: result.processedImage || undefined,
    detectedVehicles: detections.map((det: Detection) => det.class_name).join(', ')
  };
};

export const detectEmergencyInImage = async (file: File): Promise<DetectionResponse> => {
  const originalImageUrl = URL.createObjectURL(file);

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/api/detect/image`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error('Failed to detect emergency in image');
  }

  const result = await response.json();

  // Process detection results with improved type handling
  const detections = result.detections || [];
  const emergencyDetected = detections.some((det: Detection) => 
    ['Police', 'Ambulance', 'Fire_Engine'].includes(det.class_name)
  );

  // Map emergency types consistently
  const emergencyTypeMap: Record<string, string> = {
    'Police': 'POLICE',
    'Ambulance': 'MEDICAL',
    'Fire_Engine': 'FIRE'
  };

  const emergencyType = result.emergencyType || (
    emergencyDetected ? (emergencyTypeMap[detections[0]?.class_name as keyof typeof emergencyTypeMap] || 'EMERGENCY_VEHICLE') : null
  );

  return {
    ...result,
    originalImage: originalImageUrl,
    status: emergencyDetected ? "Emergency" : "Clear",
    type: emergencyType,
    emergencyType: emergencyType,
    confidence: Math.max(0, result.confidence || 0),
    detectedVehicles: result.detectedVehicles || detections.map((det: Detection) => det.class_name).join(', '),
    emergencyDetected,
    detections
  };
};

export const fetchRouteData = async (start: [number, number], end: [number, number], emergencyType: EmergencyType) => {
  const response = await fetch(`${API_URL}/api/route`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      start_lat: start[0],
      start_lng: start[1],
      end_lat: end[0],
      end_lng: end[1],
      emergency_type: emergencyType
    })
  });

  if (!response.ok) {
    throw new Error('Failed to fetch route data');
  }

  return response.json();
};

export const fetchTrafficPatterns = async (): Promise<any[]> => {
  const response = await fetch(`${API_URL}/api/traffic-patterns`);
  if (!response.ok) {
    throw new Error('Failed to fetch traffic patterns');
  }
  return response.json();
};

export const fetchHistoricalData = async (): Promise<any[]> => {
  const response = await fetch(`${API_URL}/api/historical-data`);
  if (!response.ok) {
    throw new Error('Failed to fetch historical data');
  }
  return response.json();
};

export async function getEmergencyLocations() {
  // Implement in future
  return [];
}

export async function getRequests() {
  // Implement in future
  return [];
}

export async function getVehicles() {
  // Implement in future
  return [];
}
