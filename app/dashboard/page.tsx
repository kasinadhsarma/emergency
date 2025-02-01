"use client";

import React, { useState, useEffect } from "react";
import Layout from '../../components/Layout';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Alert, AlertDescription, AlertTitle } from '../../components/ui/alert';
import {
  PhoneCall, ShieldAlert, History, MapPin, Upload, Video,
  Camera, Ambulance, Truck, AlertTriangle, CheckCircle2,
  ChevronRight, Activity
} from "lucide-react";
import dynamic from 'next/dynamic';

const Map = dynamic(() => import('../../components/Map'));
import { getStations, detectEmergencyInVideo, detectEmergencyInImage } from '../../lib/api';
import {
  EmergencyType,
  Detection,
  DetectionResponse,
  StationData,
  StationLocation
} from "../../lib/types";

const UserDashboard: React.FC = () => {
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [modelInitialized, setModelInitialized] = useState<boolean>(false);
  const [isInitializing, setIsInitializing] = useState<boolean>(true);
  const [stations, setStations] = useState<StationData>({
    ambulanceStations: [] as StationLocation[],
    fireStations: [] as StationLocation[],
    policeStations: [] as StationLocation[]
  });
  const [detectionResults, setDetectionResults] = useState<DetectionResponse | null>(null);
  const [activeEmergency, setActiveEmergency] = useState<boolean>(false);
  const [selectedService, setSelectedService] = useState<EmergencyType>('MEDICAL');

  // Cleanup URLs when component unmounts or new media is uploaded
  useEffect(() => {
    return () => {
      if (detectionResults?.originalImage) {
        URL.revokeObjectURL(detectionResults.originalImage); // Cleanup object URL
      }
      // processedImage is a base64 string and doesn't require cleanup
    };
  }, [detectionResults]);

  useEffect(() => {
    const initStations = async () => {
      setIsInitializing(true);
      try {
        const stationData = await getStations();
        setStations(stationData);
        setModelInitialized(true);
      } catch (error) {
        console.error("Error initializing stations:", error);
        setModelInitialized(false);
      } finally {
        setIsInitializing(false);
      }
    };
    initStations();
  }, []);

  const handleVideoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Cleanup previous original image URL
    if (detectionResults?.originalImage) {
      URL.revokeObjectURL(detectionResults.originalImage);
    }
    // No need to revoke processedImage as it's a base64 string

    setIsProcessing(true);
    setDetectionResults(null);

    try {
      const results = await detectEmergencyInVideo(file);
      setDetectionResults({
        ...results,
        originalImage: URL.createObjectURL(file),
        processedImage: results.processedImage || undefined,
      });
      if (results.emergencyDetected) {
        setActiveEmergency(true);
      }
    } catch (error) {
      console.error("Error processing video:", error);
      alert(
        error instanceof Error
          ? error.message
          : typeof error === "string"
          ? error
          : "Failed to process video"
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Cleanup previous original image URL
    if (detectionResults?.originalImage) {
      URL.revokeObjectURL(detectionResults.originalImage);
    }
    // No need to revoke processedImage as it's a base64 string

    setIsProcessing(true);
    setDetectionResults(null);

    try {
      const results = await detectEmergencyInImage(file);
      setDetectionResults({
        ...results,
        originalImage: URL.createObjectURL(file),
        processedImage: results.processedImage  // Now directly using the base64 image
      });
      if (results.emergencyDetected) {
        setActiveEmergency(true);
      }
    } catch (error) {
      console.error("Error processing image:", error);
      alert(
        error instanceof Error
          ? error.message
          : typeof error === "string"
          ? error
          : "Failed to process image"
      );
    } finally {
      setIsProcessing(false);
    }
  };

  // Status badge component with loading state
  const ModelStatusBadge = () => {
    let color = "bg-blue-400";
    if (isInitializing) {
      color = "bg-yellow-400";
    } else if (!modelInitialized) {
      color = "bg-red-400";
    }
    return (
      <Badge variant="outline" className={color}>
        {isInitializing ? "Initializing..." : modelInitialized ? "Ready" : "Error"}
      </Badge>
    );
  };

  const EmergencyStatusBadge: React.FC = () => (
    <Badge className={activeEmergency ? "bg-red-500" : "bg-green-500"}>
      {activeEmergency ? (
        <div className="flex items-center gap-1">
          <AlertTriangle className="h-4 w-4" />
          Active Emergency
        </div>
      ) : (
        <div className="flex items-center gap-1">
          <CheckCircle2 className="h-4 w-4" />
          All Clear
        </div>
      )}
    </Badge>
  );

  const emergencyNumbers = {
    medical: process.env.NEXT_PUBLIC_MEDICAL_EMERGENCY_NUMBER || "108",
    fire: process.env.NEXT_PUBLIC_FIRE_EMERGENCY_NUMBER || "101",
    police: process.env.NEXT_PUBLIC_POLICE_EMERGENCY_NUMBER || "100",
    general: process.env.NEXT_PUBLIC_GENERAL_EMERGENCY_NUMBER || "112",
  };

  return (
    <Layout>
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Emergency Response Dashboard</h1>
          <EmergencyStatusBadge />
        </div>

        {activeEmergency && (
          <Alert variant="destructive" className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Emergency Detected</AlertTitle>
            <AlertDescription>
              Emergency services have been notified and are en route to your location.
              Stay calm and follow emergency protocols.
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="shadow-lg border-l-4 border-blue-500">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Ambulance className="h-5 w-5 text-blue-500" />
                  Medical Services
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">Nearest Hospital: 2.3 miles</p>
                  <p className="text-sm text-gray-600">Available Units: 3</p>
                  <Button className="w-full mt-4">Request Ambulance</Button>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-lg border-l-4 border-red-500">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Truck className="h-5 w-5 text-red-500" />
                  Fire Services
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">Nearest Station: 1.8 miles</p>
                  <p className="text-sm text-gray-600">Available Units: 2</p>
                  <Button className="w-full mt-4">Request Fire Service</Button>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-lg border-l-4 border-yellow-500">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShieldAlert className="h-5 w-5 text-yellow-500" />
                  Police Services
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">Nearest Station: 1.5 miles</p>
                  <p className="text-sm text-gray-600">Available Units: 4</p>
                  <Button className="w-full mt-4">Request Police</Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="flex space-x-6">
            <Card className="shadow-lg flex-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  Emergency Response Map
                </CardTitle>
                <CardDescription>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-red-500"></div>
                    <span>Fire Engine</span>
                    <div className="w-4 h-4 rounded-full bg-orange-500"></div>
                    <span>Police Vehicle</span>
                    <div className="w-4 h-4 rounded-full bg-blue-500"></div>
                    <span>Ambulance</span>
                  </div>
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-96">
                  <Map
                    paths={[]}
                    markers={
                      detectionResults?.detections.map((detection) => ({
                        position: [detection.bbox[0], detection.bbox[1]],
                        type: detection.class_name,
                        confidence: detection.confidence,
                      })) || []
                    }
                    center={[81.7800, 16.9927]} // Rajahmundry coordinates (lng, lat)
                    zoom={12}
                    fireEngineIcon="/icons/fire-engine.png" // Ensure this path exists
                    policeVehicleIcon="/icons/police-vehicle.png" // Ensure this path exists
                  />
                </div>
              </CardContent>
            </Card>

            <div className="flex-1 space-y-6">
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    System Status
                  </CardTitle>
                  <CardDescription className="text-blue-100">
                    Real-time monitoring active
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span>Model Status</span>
                      <ModelStatusBadge />
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Response Time</span>
                      <Badge variant="outline" className="bg-blue-400">{"< 5 min"}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <History className="h-5 w-5" />
                    Recent Activity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { id: 1, time: "10:45 AM", event: "System Check Complete" },
                      { id: 2, time: "10:30 AM", event: "Location Updated" },
                      { id: 3, time: "10:15 AM", event: "Connection Verified" },
                    ].map((activity) => (
                      <div key={activity.id} className="flex items-center justify-between">
                        <span className="text-sm text-gray-300">{activity.time}</span>
                        <span>{activity.event}</span>
                        <ChevronRight className="h-4 w-4 text-gray-400" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Upload className="h-5 w-5" />
                    Quick Actions
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button className="w-full bg-red-500 hover:bg-red-600" aria-label="Make an emergency call">
                        <PhoneCall className="mr-2 h-4 w-4" />
                        Emergency Call
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Emergency Call</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <Button className="w-full" onClick={() => window.location.href = `tel:${emergencyNumbers.medical}`}>
                          <Ambulance className="mr-2 h-4 w-4" />
                          Medical Emergency
                        </Button>
                        <Button className="w-full" onClick={() => window.location.href = `tel:${emergencyNumbers.fire}`}>
                          <Truck className="mr-2 h-4 w-4" />
                          Fire Emergency
                        </Button>
                        <Button className="w-full" onClick={() => window.location.href = `tel:${emergencyNumbers.police}`}>
                          <ShieldAlert className="mr-2 h-4 w-4" />
                          Police Emergency
                        </Button>
                        <div className="p-4 bg-white shadow-md rounded-md">
                          <h2 className="text-xl font-bold mb-4">Emergency Numbers</h2>
                          <div className="space-y-2">
                            <div><span className="font-semibold">Medical Emergency:</span> {emergencyNumbers.medical}</div>
                            <div><span className="font-semibold">Fire Station:</span> {emergencyNumbers.fire}</div>
                            <div><span className="font-semibold">Police Emergency:</span> {emergencyNumbers.police}</div>
                            <div><span className="font-semibold">General Emergency:</span> {emergencyNumbers.general}</div>
                          </div>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                </CardContent>
              </Card>
            </div>
          </div>

          <div className="mt-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Upload className="h-5 w-5" />
                    Before Analysis
                  </CardTitle>
                  <CardDescription>Original uploaded media</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                    {detectionResults?.originalImage ? (
                      <img
                        src={detectionResults.originalImage}
                        alt="Original media"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <p className="text-gray-500">No media uploaded</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    After Analysis
                  </CardTitle>
                  <CardDescription>YOLO detection results</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                    {detectionResults?.processedImage ? (
                      <img
                        src={detectionResults.processedImage}
                        alt="Processed media with detections"
                        className="w-full h-full object-contain"
                        onError={(e) => {
                          console.error('Error loading processed image:', e);
                          e.currentTarget.src = '/path/to/fallback-image.png'; // Provide a fallback image
                        }}
                      />
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <p className="text-gray-500">No analysis results</p>
                      </div>
                    )}
                  </div>
                  {detectionResults && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <h3 className="font-semibold mb-2">Detection Summary</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Status:</span>
                          <Badge className={detectionResults.emergencyDetected ? "bg-red-400" : "bg-green-400"}>
                            {detectionResults.emergencyDetected ? "Emergency" : "Clear"}
                          </Badge>
                        </div>
                        {detectionResults.emergencyType && (
                          <div className="flex justify-between">
                            <span>Type:</span>
                            <Badge>{detectionResults.emergencyType}</Badge>
                          </div>
                        )}
                        {detectionResults.confidence && (
                          <div className="flex justify-between">
                            <span>Confidence:</span>
                            <Badge>{`${(detectionResults.confidence * 100).toFixed(1)}%`}</Badge>
                          </div>
                        )}
                        {detectionResults.detections.length > 0 && (
                          <div className="flex justify-between">
                            <span>Detected Vehicles:</span>
                            <Badge>
                              {detectionResults.detections.map(det => det.class_name).join(', ')}
                            </Badge>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="shadow-lg bg-gradient-to-br from-blue-500 to-blue-700 text-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Video className="h-5 w-5" />
                    Video Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <label className="block w-full p-4 border-2 border-white/20 rounded-lg text-center cursor-pointer hover:bg-white/10 transition-colors">
                    <Video className="mx-auto h-8 w-8 mb-2" />
                    <input
                      type="file"
                      accept="video/*"
                      onChange={handleVideoUpload}
                      className="hidden"
                      disabled={isProcessing || isInitializing}
                    />
                    <span className="block text-sm font-medium">
                      {isProcessing ? "Processing..." : "Upload Video"}
                    </span>
                    <Badge className="mt-2 bg-white/20">
                      {isInitializing ? "Initializing..." : modelInitialized ? "Ready" : "Error"}
                    </Badge>
                  </label>
                </CardContent>
              </Card>

              <Card className="shadow-lg bg-gradient-to-br from-purple-500 to-purple-700 text-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Camera className="h-5 w-5" />
                    Image Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <label className="block w-full p-4 border-2 border-white/20 rounded-lg text-center cursor-pointer hover:bg-white/10 transition-colors">
                    <Camera className="mx-auto h-8 w-8 mb-2" />
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                      disabled={isProcessing || isInitializing}
                    />
                    <span className="block text-sm font-medium">
                      {isProcessing ? "Processing..." : "Upload Image"}
                    </span>
                    <Badge className="mt-2 bg-white/20">
                      {isInitializing ? "Initializing..." : modelInitialized ? "Ready" : "Error"}
                    </Badge>
                  </label>
                </CardContent>
              </Card>
            </div>

            {detectionResults?.emergencyDetected && (
              <Alert variant="destructive" className="mt-6">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Emergency Services Notified</AlertTitle>
                <AlertDescription>
                  Based on the detection results, emergency services have been automatically notified.
                  Stay in your current location unless instructed otherwise.
                </AlertDescription>
              </Alert>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default UserDashboard;
