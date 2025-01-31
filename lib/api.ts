const API_BASE_URL = 'http://localhost:8000';

// User Profile
export const getUserProfile = async () => {
  // Mock data for demonstration purposes
  return {
    name: "John Doe",
    email: "john.doe@example.com",
    role: "Admin"
  }
}

// Emergency Locations and Stations
export const getEmergencyLocations = async () => {
  const response = await fetch(`${API_BASE_URL}/api/locations`);
  if (!response.ok) throw new Error('Failed to fetch emergency locations');
  return response.json();
}

export const getStations = async () => {
  const response = await fetch(`${API_BASE_URL}/api/stations`);
  if (!response.ok) throw new Error('Failed to fetch stations');
  const data = await response.json();
  return {
    fireStations: data.fireStations,
    policeStations: data.policeStations.map((station: any) => ({
      ...station,
      address: `${station.name}, Rajamahendra`
    })),
    ambulanceStations: data.ambulanceStations
  };
}

export const getVehicles = async () => {
  const response = await fetch(`${API_BASE_URL}/api/vehicles`);
  if (!response.ok) throw new Error('Failed to fetch vehicles');
  return response.json();
}

export const getRequests = async () => {
  const response = await fetch(`${API_BASE_URL}/api/requests`);
  if (!response.ok) throw new Error('Failed to fetch requests');
  return response.json();
}

// Emergency Contacts
export const setEmergencyContacts = async (contacts: any) => {
  const response = await fetch(`${API_BASE_URL}/api/set_emergency_contacts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(contacts),
  });
  if (!response.ok) throw new Error('Failed to set emergency contacts');
  return response.json();
}

// Medical Information
export const getMedicalInformation = async () => {
  const response = await fetch(`${API_BASE_URL}/api/medical_information`);
  if (!response.ok) throw new Error('Failed to fetch medical information');
  return response.json();
}

// Saved Locations
export const getSavedLocations = async () => {
  const response = await fetch(`${API_BASE_URL}/api/saved_locations`);
  if (!response.ok) throw new Error('Failed to fetch saved locations');
  return response.json();
}

// Emergency Detection
export const detectEmergencyInImage = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/detect/image`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to process image');
  return response.json();
}

export const detectEmergencyInVideo = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/detect/video`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to process video');
  return response.json();
}

// Emergency Requests
export const createEmergencyRequest = async (request: {
  type: string;
  location: [number, number];
  address: string;
  description: string;
}) => {
  const response = await fetch(`${API_BASE_URL}/api/requests`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Failed to create emergency request');
  return response.json();
}

// Routing
export const findOptimalRoute = async (request: {
  vehicle_type: string;
  current_lat: number;
  current_lon: number;
  traffic_weights?: { [key: string]: number };
}) => {
  const response = await fetch(`${API_BASE_URL}/route`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Failed to find route');
  return response.json();
}
