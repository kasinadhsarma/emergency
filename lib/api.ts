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
  return {
    ...result,
    originalImage: originalVideoUrl
  };
};

export const detectEmergencyInImage = async (file: File): Promise<DetectionResponse> => {
  // Create a URL for the original image preview
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
  return {
    ...result,
    originalImage: originalImageUrl
  };
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
