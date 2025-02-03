"use client";

import React, { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

// Initialize Mapbox token
mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "pk.eyJ1Ijoia2FzaW5hZGhzYXJtYSIsImEiOiJjbHQya2RoNTEwaWxpMm1xYjFhNm5pb2JzIn0.NQJMGBAig4N4YwUG95L8Ww";

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
  return type.toLowerCase().includes('ambulance') ? '#3b82f6' :  // Blue
         type.toLowerCase().includes('fire engine') ? '#ef4444' :       // Red
         type.toLowerCase().includes('police') ? '#f97316' :     // Orange
         '#6b7280';  // Gray (default)
};

const Map: React.FC<MapProps> = ({
  paths,
  markers,
  center = [16.9927, 81.7800], // Rajahmundry coordinates (lat, lng)
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
      center: [center[1], center[0]], // Convert to [lng, lat] for Mapbox
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
      el.style.width = '20px';
      el.style.height = '20px';
      el.style.borderRadius = '50%';
      el.style.backgroundColor = getMarkerColor(type);
      el.style.border = '3px solid white';
      el.style.boxShadow = '0 0 6px rgba(0,0,0,0.4)';

      // Validate coordinates
      const [lat, lng] = position;
      if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
        const marker = new mapboxgl.Marker(el)
          .setLngLat([lng, lat])  // Mapbox expects [lng, lat]
          .setPopup(new mapboxgl.Popup().setHTML(`
            <div class="p-2">
              <h3 class="font-bold">${type}</h3>
              <p>Confidence: ${confidence ? (confidence * 100).toFixed(1) : 'N/A'}%</p>
            </div>
          `))
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
            [path.start[1], path.start[0]],  // Convert [lat, lng] to [lng, lat] for Mapbox
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
          'line-width': 4,
          'line-opacity': 0.8
        }
      });
    }
  }, [paths, mapLoaded]);

  return (
    <div
      ref={mapContainer}
      className="w-full h-full min-h-[400px] rounded-lg border border-gray-200 relative"
    />
  );
};

export default Map;
