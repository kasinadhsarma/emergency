export type EmergencyType = 'FIRE' | 'MEDICAL' | 'POLICE' | 'OTHER';

export interface Detection {
  timestamp: string;
  location: {
    lat: number;
    lng: number;
  };
  type: EmergencyType;
  severity: number;
  bbox: [number, number, number, number];
  class_name: string;
  confidence: number;
}

export interface DetectionResponse {
  emergencyDetected: boolean;
  emergencyType: EmergencyType | null;
  confidence: number;
  timestamp: string;
  detections: Detection[];
  message?: string;
  originalImage?: string;  // Base64 or URL of original uploaded media
  processedImage?: string; // Base64 or URL of processed media with YOLO detections
}

export interface StationLocation {
  id: string;
  name: string;
  location: {
    lat: number;
    lng: number;
  };
  status: 'ACTIVE' | 'INACTIVE';
  units: number;
}

export interface StationData {
  ambulanceStations: StationLocation[];
  fireStations: StationLocation[];
  policeStations: StationLocation[];
}

export interface PathSegment {
  start: {
    lat: number;
    lng: number;
  };
  end: {
    lat: number;
    lng: number;
  };
  type: 'ROAD' | 'EMERGENCY_ROUTE';
}

export interface NearestLocation {
  station: StationLocation;
  distance: number;
  estimatedTime: number;
  type: EmergencyType;
}
