"use client";

import React, { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

// Initialize Mapbox token
mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";

interface MapProps {
  paths: Array<{
    start: [number, number];
    end: [number, number];
    vehicleDensity: number;
  }>;
  markers: Array<{
    position: [number, number];
    type: string;
    confidence?: number;
  }>;
  center?: [number, number];
  zoom?: number;
  fireEngineIcon?: string;
  policeVehicleIcon?: string;
}

const getMarkerColor = (type: string): string => {
  return type.toLowerCase().includes('ambulance') ? 'blue' :
         type.toLowerCase().includes('fire') ? 'red' :
         type.toLowerCase().includes('police') ? 'orange' : 'gray';
};

const Map: React.FC<MapProps> = ({
  paths,
  markers,
  center = [81.7800, 16.9927], // Rajahmundry coordinates (lng, lat)
  zoom = 12,
  fireEngineIcon,
  policeVehicleIcon
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markerRefs = useRef<mapboxgl.Marker[]>([]);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: center,
      zoom: zoom,
      attributionControl: true
    });

    map.current.on('load', () => {
      setMapLoaded(true);
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Handle markers
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    // Clear existing markers
    markerRefs.current.forEach(marker => marker.remove());
    markerRefs.current = [];

    // Add new markers
    markers.forEach(({ position, type, confidence }) => {
      const el = document.createElement('div');
      el.className = 'marker';
      el.style.width = '15px';
      el.style.height = '15px';
      el.style.borderRadius = '50%';
      el.style.backgroundColor = getMarkerColor(type);
      el.style.border = '2px solid white';
      el.style.boxShadow = '0 0 4px rgba(0,0,0,0.3)';

      if (position[0] >= -90 && position[0] <= 90 && position[1] >= -180 && position[1] <= 180) {
      const marker = new mapboxgl.Marker(el)
        .setLngLat([position[1], position[0]])
        .setPopup(new mapboxgl.Popup().setHTML(`<h3>${type}</h3><p>Confidence: ${confidence ? (confidence * 100).toFixed(1) : 'N/A'}%</p>`))
        .addTo(map.current!);

        markerRefs.current.push(marker);
      }
    });
  }, [markers, mapLoaded]);

  // Handle paths
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    // Remove existing paths
    if (map.current.getSource('routes')) {
      map.current.removeLayer('routes');
      map.current.removeSource('routes');
    }

    if (paths.length > 0) {
      const geojson = {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: paths.flatMap(path => [
            [path.start[1], path.start[0]],
            [path.end[1], path.end[0]]
          ])
        }
      };

      map.current.addSource('routes', {
        type: 'geojson',
        data: geojson as any
      });

      map.current.addLayer({
        id: 'routes',
        type: 'line',
        source: 'routes',
        layout: {
          'line-join': 'round',
          'line-cap': 'round'
        },
        paint: {
          'line-color': '#3b82f6',
          'line-width': 3,
          'line-opacity': 0.8
        }
      });
    }
  }, [paths, mapLoaded]);

  return (
    <div
      ref={mapContainer}
      className="w-full h-[400px] rounded-lg border border-gray-200 relative z-0 grid grid-cols-2 gap-4"
    >
      {fireEngineIcon && (
        <div
          className="absolute top-4 left-4 w-8 h-8 rounded-full bg-red-500"
        />
      )}
      {policeVehicleIcon && (
        <div
          className="absolute top-4 right-4 w-8 h-8 rounded-full bg-orange-500"
        />
      )}
      <div
        className="absolute top-4 left-24 w-8 h-8 rounded-full bg-blue-500"
      />
      <div
        className="absolute bottom-16 left-4 w-8 h-8 rounded-full bg-blue-500"
      />
      <div className="absolute bottom-4 left-4 w-8 h-8 rounded-full bg-blue-500">
        <span className="text-white">10:45</span>
      </div>
    </div>
  );
};

export default Map;
