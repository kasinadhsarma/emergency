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
  Phone, MapPin, Clock, BellRing, FileText, Globe, Lock, Code, Server,
  Navigation, MessageCircle, BarChart, AlertCircle, Users, Shield
} from "lucide-react"
import Map from "@/components/Map"

interface EmergencyContact {
  type: string;
  number: string;
  description: string;
}

interface EmergencyRequest {
  id: string
  type: "Medical" | "Fire" | "Police"
  status: "Pending" | "Dispatched" | "Completed"
  location: [number, number]
  address: string
  timestamp: string
  description: string
}

interface Vehicle {
  id: string
  type: string
  location: [number, number]
  status: string
  eta?: string
}

const EMERGENCY_CONTACTS: Record<string, EmergencyContact[]> = {
  Medical: [
    { type: "Ambulance", number: "102", description: "National Emergency Ambulance" },
    { type: "Medical Helpline", number: "108", description: "Emergency Medical Services" },
    { type: "COVID-19", number: "1075", description: "National COVID-19 Helpline" }
  ],
  Fire: [
    { type: "Fire Service", number: "101", description: "Fire Emergency Service" }
  ],
  Police: [
    { type: "Police", number: "100", description: "Police Control Room" },
    { type: "Women Helpline", number: "1091", description: "Women Safety Emergency" },
    { type: "Child Helpline", number: "1098", description: "Child Safety Emergency" }
  ]
};

export default function UserDashboard() {
  const [selectedEmergency, setSelectedEmergency] = useState<string | null>(null);
  const [isMapExpanded, setIsMapExpanded] = useState(false);
  const [requests, setRequests] = useState<EmergencyRequest[]>([
    {
      id: "REQ-001",
      type: "Medical",
      status: "Dispatched",
      location: [77.5946, 12.9716],
      address: "123 Main St",
      timestamp: "2 mins ago",
      description: "Medical emergency - chest pain"
    },
    {
      id: "REQ-002",
      type: "Fire",
      status: "Completed",
      location: [77.6047, 12.9783],
      address: "456 Oak Ave",
      timestamp: "1 hour ago",
      description: "Small kitchen fire"
    }
  ]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([
    { 
      id: "AMB-101", 
      type: "Ambulance", 
      location: [77.5946, 12.9816], 
      status: "En Route",
      eta: "5 mins"
    },
    { 
      id: "FT-202", 
      type: "Fire Truck", 
      location: [77.6047, 12.9883], 
      status: "Active",
      eta: "10 mins"
    }
  ]);
  const [emergencyLocations, setEmergencyLocations] = useState<any[]>([]);

  const handleEmergencyClick = (type: string) => {
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

  useEffect(() => {
    const fetchEmergencyLocations = async () => {
      try {
        const response = await fetch("/api/locations");
        if (!response.ok) {
          throw new Error("Failed to fetch emergency locations");
        }
        const data = await response.json();
        setEmergencyLocations(data.locations);
      } catch (error) {
        console.error("Error fetching emergency locations:", error);
      }
    };

    fetchEmergencyLocations();
  }, []);

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-indigo-600">Emergency Response Dashboard</h1>
            <div className="flex space-x-4">
              <Button variant="outline" className="text-indigo-600">
                <History className="mr-2 h-4 w-4" />
                History
              </Button>
              <Button variant="outline" className="text-indigo-600">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </Button>
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
              onClick={() => handleEmergencyClick("Medical")}
            />
            <EmergencyButton
              icon={<Siren className="h-6 w-6" />}
              title="Fire Emergency"
              titleHindi="अग्नि आपातकाल"
              description="Dial 101 for fire services"
              color="orange"
              onClick={() => handleEmergencyClick("Fire")}
            />
            <EmergencyButton
              icon={<ShieldAlert className="h-6 w-6" />}
              title="Police Emergency"
              titleHindi="पुलिस आपातकाल"
              description="Dial 100 for police assistance"
              color="blue"
              onClick={() => handleEmergencyClick("Police")}
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
                {selectedEmergency && EMERGENCY_CONTACTS[selectedEmergency].map((contact, index) => (
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
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => setIsMapExpanded(!isMapExpanded)}
                >
                  <Maximize2 className="h-4 w-4" />
                </Button>
              </CardHeader>
              <CardContent className="p-0">
                <div className={isMapExpanded ? "h-[800px]" : "h-[400px]"}>
                  <Map vehicles={vehicles} emergencyLocations={emergencyLocations} />
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
                        <Button className="w-full" variant="outline">
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

interface EmergencyButtonProps {
  icon: React.ReactNode;
  title: string;
  titleHindi: string;
  description: string;
  color: 'red' | 'orange' | 'blue';
  onClick: () => void;
}

function EmergencyButton({ icon, title, titleHindi, description, color, onClick }: EmergencyButtonProps) {
  const colorStyles = {
    red: "bg-red-600 hover:bg-red-700",
    orange: "bg-orange-600 hover:bg-orange-700",
    blue: "bg-blue-600 hover:bg-blue-700"
  }

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
  )
}

function RequestCard({ request }: { request: EmergencyRequest }) {
  const statusColors = {
    Pending: "bg-yellow-100 text-yellow-800",
    Dispatched: "bg-blue-100 text-blue-800",
    Completed: "bg-green-100 text-green-800"
  }

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-medium text-indigo-600">{request.type} Emergency</h3>
            <p className="text-sm text-gray-500">ID: {request.id}</p>
          </div>
          <Badge className={statusColors[request.status]}>{request.status}</Badge>
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

        {request.status === "Dispatched" && (
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-2">
              <span>Response Time</span>
              <span>2 mins</span>
            </div>
            <Progress value={66} className="h-2" />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
