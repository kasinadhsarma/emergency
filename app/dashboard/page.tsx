"use client"

import { useState, useEffect } from "react"
import Layout from "@/components/Layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { 
  PhoneCall, Siren, ShieldAlert, History, Settings, Maximize2,
  Phone, MapPin, Clock, BellRing, FileText
} from "lucide-react"
import Map from "@/components/Map"

// Enums for better type safety
enum EmergencyType {
  Medical = "Medical",
  Fire = "Fire",
  Police = "Police"
}

enum RequestStatus {
  Pending = "Pending",
  Dispatched = "Dispatched",
  Completed = "Completed"
}

// Interfaces with proper typing
interface EmergencyContact {
  type: string;
  number: string;
  description: string;
  emergencyType: EmergencyType;
}

interface EmergencyRequest {
  id: string;
  type: EmergencyType;
  status: RequestStatus;
  location: [number, number];
  address: string;
  timestamp: string;
  description: string;
  responseTime?: number;
}

interface Vehicle {
  id: string;
  type: string;
  location: [number, number];
  status: string;
  eta?: string;
}

interface Station {
  id: string;
  name: string;
  location: [number, number];
  address: string;
  contact: string;
  type: EmergencyType;
}

interface EmergencyLocation {
  id: string;
  type: string;
  location: [number, number];
  name: string;
}

// Constants
const EMERGENCY_CONTACTS: EmergencyContact[] = [
  {
    type: "Ambulance",
    emergencyType: EmergencyType.Medical,
    number: "102",
    description: "National Emergency Ambulance"
  },
  {
    type: "Fire Service",
    emergencyType: EmergencyType.Fire,
    number: "101",
    description: "Fire Emergency Service"
  },
  {
    type: "Police",
    emergencyType: EmergencyType.Police,
    number: "100",
    description: "Police Control Room"
  }
];

// Props interfaces
interface EmergencyButtonProps {
  icon: React.ReactNode;
  title: string;
  titleHindi: string;
  description: string;
  color: 'red' | 'orange' | 'blue';
  onClick: () => void;
}

interface RequestCardProps {
  request: EmergencyRequest;
}

// Helper functions
const getStatusColor = (status: RequestStatus): string => {
  const colors = {
    [RequestStatus.Pending]: "bg-yellow-100 text-yellow-800",
    [RequestStatus.Dispatched]: "bg-blue-100 text-blue-800",
    [RequestStatus.Completed]: "bg-green-100 text-green-800"
  };
  return colors[status];
};

const getEmergencyContacts = (type: EmergencyType): EmergencyContact[] => {
  return EMERGENCY_CONTACTS.filter(contact => contact.emergencyType === type);
};

// Component functions
const EmergencyButton = ({
  icon,
  title,
  titleHindi,
  description,
  color,
  onClick
}: EmergencyButtonProps) => {
  const colorStyles = {
    red: "bg-red-600 hover:bg-red-700",
    orange: "bg-orange-600 hover:bg-orange-700",
    blue: "bg-blue-600 hover:bg-blue-700"
  };

  return (
    <Button
      onClick={onClick}
      className={`w-full h-32 ${colorStyles[color]} flex flex-col items-center justify-center space-y-2`}
    >
      {icon}
      <div className="text-center">
        <div className="font-bold">{title}</div>
        <div className="text-sm font-medium">{titleHindi}</div>
        <div className="text-sm opacity-90">{description}</div>
      </div>
    </Button>
  );
};

const RequestCard = ({ request }: RequestCardProps) => {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-medium text-indigo-600">{request.type} Emergency</h3>
            <p className="text-sm text-gray-500">ID: {request.id}</p>
          </div>
          <Badge className={getStatusColor(request.status)}>{request.status}</Badge>
        </div>

        <div className="space-y-3 text-sm text-gray-600">
          <div className="flex items-center">
            <MapPin className="h-4 w-4 mr-2 text-gray-400" />
            <span>{request.address}</span>
          </div>
          <div className="flex items-center">
            <Clock className="h-4 w-4 mr-2 text-gray-400" />
            <span>{request.timestamp}</span>
          </div>
          <p className="text-sm">{request.description}</p>
        </div>

        {request.status === RequestStatus.Dispatched && request.responseTime && (
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-2">
              <span>Response Time</span>
              <span>{request.responseTime} mins</span>
            </div>
            <Progress value={66} className="h-2" />
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Main component
export default function UserDashboard() {
  const [selectedEmergency, setSelectedEmergency] = useState<EmergencyType | null>(null);
  const [isMapExpanded, setIsMapExpanded] = useState(false);
  const [requests, setRequests] = useState<EmergencyRequest[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [stations, setStations] = useState<Station[]>([]);
  const [emergencyLocations, setEmergencyLocations] = useState<EmergencyLocation[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    const fetchEmergencyData = async () => {
      try {
        const [locationsRes, requestsRes, vehiclesRes, stationsRes] = await Promise.all([
          fetch("/api/locations"),
          fetch("/api/requests"),
          fetch("/api/vehicles"),
          fetch("/api/stations")
        ]);

        if (!locationsRes.ok || !requestsRes.ok || !vehiclesRes.ok || !stationsRes.ok) {
          throw new Error("Failed to fetch emergency data");
        }

        const [locations, requests, vehicles, stations] = await Promise.all([
          locationsRes.json(),
          requestsRes.json(),
          vehiclesRes.json(),
          stationsRes.json()
        ]);

        setEmergencyLocations(locations);
        setRequests(requests);
        setVehicles(vehicles);
        setStations(stations);
      } catch (error) {
        console.error("Error fetching emergency data:", error);
      }
    };

    fetchEmergencyData();
  }, []);

  const handleEmergencyClick = (type: EmergencyType) => {
    setSelectedEmergency(type);
  };

const handleVideoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
  const file = event.target.files?.[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/api/detect/video", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to upload video");
    }

    const data = await response.json();
    console.log("Video detection results:", data);
  } catch (error) {
    console.error("Error uploading video:", error);
  }
};

const handleSetEmergencyContacts = async () => {
  const contacts = [
    { type: "Ambulance", number: "102", description: "National Emergency Ambulance", emergencyType: EmergencyType.Medical },
    { type: "Fire Service", number: "101", description: "Fire Emergency Service", emergencyType: EmergencyType.Fire },
    { type: "Police", number: "100", description: "Police Control Room", emergencyType: EmergencyType.Police }
  ];

  try {
    const response = await fetch("/api/set_emergency_contacts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(contacts)
    });

    if (!response.ok) {
      throw new Error("Failed to set emergency contacts");
    }

    const data = await response.json();
    console.log("Emergency contacts set:", data);
  } catch (error) {
    console.error("Error setting emergency contacts:", error);
  }
};

const handleGetMedicalInformation = async () => {
  try {
    const response = await fetch("/api/medical_information");

    if (!response.ok) {
      throw new Error("Failed to get medical information");
    }

    const data = await response.json();
    console.log("Medical information:", data);
  } catch (error) {
    console.error("Error getting medical information:", error);
  }
};

const handleGetSavedLocations = async () => {
  try {
    const response = await fetch("/api/saved_locations");

    if (!response.ok) {
      throw new Error("Failed to get saved locations");
    }

    const data = await response.json();
    console.log("Saved locations:", data);
  } catch (error) {
    console.error("Error getting saved locations:", error);
  }
};

  return (
    <Layout>
<div className="min-h-screen bg-gray-50">
  <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
    <div className="flex justify-between items-center mb-6">
      <h1 className="text-3xl font-bold text-indigo-600">EVS Dashboard</h1>
      <div className="relative">
        <div className="w-12 h-12 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold text-xl cursor-pointer" onClick={() => setShowDropdown(!showDropdown)}>
          U
        </div>
        {showDropdown && (
          <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg">
            <div className="py-1">
              <Button variant="outline" className="w-full text-indigo-600">
                <History className="mr-2 h-4 w-4" />
                History
              </Button>
              <Button variant="outline" className="w-full text-indigo-600">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <EmergencyButton
        icon={<PhoneCall className="h-6 w-6" />}
        title="Medical Emergency"
        titleHindi="चिकित्सा आपातकाल"
        description="Dial 102/108 for immediate assistance"
        color="red"
        onClick={() => handleEmergencyClick(EmergencyType.Medical)}
      />
      <EmergencyButton
        icon={<Siren className="h-6 w-6" />}
        title="Fire Emergency"
        titleHindi="अग्नि आपातकाल"
        description="Dial 101 for fire services"
        color="orange"
        onClick={() => handleEmergencyClick(EmergencyType.Fire)}
      />
      <EmergencyButton
        icon={<ShieldAlert className="h-6 w-6" />}
        title="Police Emergency"
        titleHindi="पुलिस आपातकाल"
        description="Dial 100 for police assistance"
        color="blue"
        onClick={() => handleEmergencyClick(EmergencyType.Police)}
      />
    </div>
    <Dialog open={!!selectedEmergency} onOpenChange={() => setSelectedEmergency(null)}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center text-xl font-bold text-indigo-600">
            {selectedEmergency} Emergency Contacts
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4 mt-4">
          {selectedEmergency && getEmergencyContacts(selectedEmergency).map((contact, index) => (
            <Card key={index} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-indigo-600">{contact.type}</h3>
                  <Badge variant="outline" className="text-indigo-600">
                    {contact.number}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">{contact.description}</p>
                <Button
                  className="w-full mt-4 bg-indigo-600 hover:bg-indigo-700"
                  onClick={() => window.location.href = `tel:${contact.number}`}
                >
                  <Phone className="mr-2 h-4 w-4" />
                  Call Now
                </Button>
              </CardContent>
            </Card>
          ))}
          <div className="text-sm text-gray-500 text-center mt-4">
            These are toll-free emergency numbers available 24x7 across India
          </div>
        </div>
      </DialogContent>
    </Dialog>
    <div className={`grid grid-cols-1 ${isMapExpanded ? '' : 'lg:grid-cols-3'} gap-6`}>
      <Card className={`${isMapExpanded ? '' : 'lg:col-span-2'} shadow-lg`}>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-indigo-600">Response Map</CardTitle>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              <div className="w-3 h-3 rounded-full bg-red-600 mr-2" />
              Ambulances
            </Button>
            <Button variant="outline" size="sm">
              <div className="w-3 h-3 rounded-full bg-orange-600 mr-2" />
              Fire Stations
            </Button>
            <Button variant="outline" size="sm">
              <div className="w-3 h-3 rounded-full bg-blue-600 mr-2" />
              Police Stations
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMapExpanded(!isMapExpanded)}
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className={isMapExpanded ? "h-[800px]" : "h-[400px]"}>
            <Map
              vehicles={vehicles}
              emergencyLocations={emergencyLocations}
              fireStations={stations.filter(station => station.type === EmergencyType.Fire)}
              policeStations={stations.filter(station => station.type === EmergencyType.Police)}
              ambulanceStations={stations.filter(station => station.type === EmergencyType.Medical)}
            />
          </div>
        </CardContent>
      </Card>
      {!isMapExpanded && (
        <div className="space-y-6">
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="text-indigo-600">Active Requests</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {requests.map((request) => (
                  <RequestCard key={request.id} request={request} />
                ))}
              </div>
            </CardContent>
          </Card>
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="text-indigo-600">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button className="w-full" variant="outline">
                  <BellRing className="mr-2 h-4 w-4" />
                  Set Emergency Contacts
                </Button>
                <Button className="w-full" variant="outline">
                  <FileText className="mr-2 h-4 w-4" />
                  Medical Information
                </Button>
                <Button className="w-full" variant="outline">
                  <MapPin className="mr-2 h-4 w-4" />
                  Saved Locations
                </Button>
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleVideoUpload}
                  className="hidden"
                  id="video-upload"
                />
                <label htmlFor="video-upload">
                  <Button className="w-full mt-2" variant="outline">
                    <FileText className="mr-2 h-4 w-4" />
                    Upload Video
                  </Button>
                </label>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  </div>
</div>

          {/* Emergency Buttons */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <EmergencyButton
              icon={<PhoneCall className="h-6 w-6" />}
              title="Medical Emergency"
              titleHindi="चिकित्सा आपातकाल"
              description="Dial 102/108 for immediate assistance"
              color="red"
              onClick={() => handleEmergencyClick(EmergencyType.Medical)}
            />
            <EmergencyButton
              icon={<Siren className="h-6 w-6" />}
              title="Fire Emergency"
              titleHindi="अग्नि आपातकाल"
              description="Dial 101 for fire services"
              color="orange"
              onClick={() => handleEmergencyClick(EmergencyType.Fire)}
            />
            <EmergencyButton
              icon={<ShieldAlert className="h-6 w-6" />}
              title="Police Emergency"
              titleHindi="पुलिस आपातकाल"
              description="Dial 100 for police assistance"
              color="blue"
              onClick={() => handleEmergencyClick(EmergencyType.Police)}
            />
          </div>

          {/* Emergency Contact Dialog */}
          <Dialog open={!!selectedEmergency} onOpenChange={() => setSelectedEmergency(null)}>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle className="text-center text-xl font-bold text-indigo-600">
                  {selectedEmergency} Emergency Contacts
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                {selectedEmergency && getEmergencyContacts(selectedEmergency).map((contact, index) => (
                  <Card key={index} className="hover:shadow-md transition-shadow">
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-indigo-600">{contact.type}</h3>
                        <Badge variant="outline" className="text-indigo-600">
                          {contact.number}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{contact.description}</p>
                      <Button
                        className="w-full mt-4 bg-indigo-600 hover:bg-indigo-700"
                        onClick={() => window.location.href = `tel:${contact.number}`}
                      >
                        <Phone className="mr-2 h-4 w-4" />
                        Call Now
                      </Button>
                    </CardContent>
                  </Card>
                ))}
                <div className="text-sm text-gray-500 text-center mt-4">
                  These are toll-free emergency numbers available 24x7 across India
                </div>
              </div>
            </DialogContent>
          </Dialog>

          {/* Map & Active Requests Section */}
          <div className={`grid grid-cols-1 ${isMapExpanded ? '' : 'lg:grid-cols-3'} gap-6`}>
            <Card className={`${isMapExpanded ? '' : 'lg:col-span-2'} shadow-lg`}>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-indigo-600">Response Map</CardTitle>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <div className="w-3 h-3 rounded-full bg-red-600 mr-2" />
                    Ambulances
                  </Button>
                  <Button variant="outline" size="sm">
                    <div className="w-3 h-3 rounded-full bg-orange-600 mr-2" />
                    Fire Stations
                  </Button>
                  <Button variant="outline" size="sm">
                    <div className="w-3 h-3 rounded-full bg-blue-600 mr-2" />
                    Police Stations
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setIsMapExpanded(!isMapExpanded)}
                  >
                    <Maximize2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className={isMapExpanded ? "h-[800px]" : "h-[400px]"}>
                  <Map
                    vehicles={vehicles}
                    emergencyLocations={emergencyLocations}
                    fireStations={stations.filter(station => station.type === EmergencyType.Fire)}
                    policeStations={stations.filter(station => station.type === EmergencyType.Police)}
                    ambulanceStations={stations.filter(station => station.type === EmergencyType.Medical)}
                  />
                </div>
              </CardContent>
            </Card>

            {!isMapExpanded && (
              <div className="space-y-6">
                <Card className="shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-indigo-600">Active Requests</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {requests.map((request) => (
                        <RequestCard key={request.id} request={request} />
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card className="shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-indigo-600">Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <Button className="w-full" variant="outline">
                        <BellRing className="mr-2 h-4 w-4" />
                        Set Emergency Contacts
                      </Button>
                      <Button className="w-full" variant="outline">
                        <FileText className="mr-2 h-4 w-4" />
                        Medical Information
                      </Button>
                      <Button className="w-full" variant="outline">
                        <MapPin className="mr-2 h-4 w-4" />
                        Saved Locations
                      </Button>
<input
  type="file"
  accept="video/*"
  onChange={handleVideoUpload}
  className="hidden"
  id="video-upload"
/>
<label htmlFor="video-upload">
  <Button className="w-full mt-2" variant="outline">
    <FileText className="mr-2 h-4 w-4" />
    Upload Video
  </Button>
</label>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
