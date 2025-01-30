"use client"

import { useEffect, useRef, useState } from "react"
import mapboxgl from "mapbox-gl"
import "mapbox-gl/dist/mapbox-gl.css"

interface Vehicle {
  id: string
  type: string
  location: [number, number]
  status: string
}

interface EmergencyLocation {
  id: string
  type: string
  location: [number, number]
  name: string
}

interface Station {
  id: string
  name: string
  location: [number, number]
  address: string
  contact: string
}

interface MapProps {
  vehicles: Vehicle[]
  emergencyLocations: EmergencyLocation[]
  fireStations: Station[]
  policeStations: Station[]
  ambulanceStations: Station[]
}

export default function Map({ 
  vehicles, 
  emergencyLocations, 
  fireStations, 
  policeStations,
  ambulanceStations 
}: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const [map, setMap] = useState<mapboxgl.Map | null>(null)
  const markersRef = useRef<mapboxgl.Marker[]>([])

  useEffect(() => {
    if (!mapContainer.current || map) return

    if (!process.env.NEXT_PUBLIC_MAPBOX_TOKEN) {
      console.error("Mapbox token missing")
      return
    }

    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN

    const initializeMap = new mapboxgl.Map({
      container: mapContainer.current,
      style: "mapbox://styles/mapbox/streets-v11",
      center: [78.9629, 20.5937], // Center of India
      zoom: 4,
      minZoom: 3,
      maxZoom: 15,
      maxBounds: [
        [68.7, 6.5],  // Southwest coordinates of India
        [97.25, 35.5] // Northeast coordinates of India
      ]
    })

    initializeMap.addControl(new mapboxgl.NavigationControl(), "top-right")

    initializeMap.on('load', () => {
      setMap(initializeMap)
    })

    return () => {
      markersRef.current.forEach(marker => marker.remove())
      initializeMap.remove()
    }
  }, [])

  useEffect(() => {
    if (!map) return

    // Remove existing markers
    markersRef.current.forEach(marker => marker.remove())
    markersRef.current = []

    // Add fire stations (orange markers)
    fireStations.forEach((station) => {
      const el = document.createElement("div")
      el.className = "w-5 h-5 rounded-full bg-orange-600 border-2 border-white shadow-md"

      const marker = new mapboxgl.Marker(el)
        .setLngLat(station.location)
        .setPopup(
          new mapboxgl.Popup({ offset: 25 }).setHTML(
            `<div class="p-2">
              <h3 class="font-bold text-orange-600">${station.name}</h3>
              <p class="text-gray-600">${station.address}</p>
              <p class="text-gray-600">Contact: ${station.contact}</p>
            </div>`
          )
        )
        .addTo(map)

      markersRef.current.push(marker)
    })

    // Add police stations (blue markers)
    policeStations.forEach((station) => {
      const el = document.createElement("div")
      el.className = "w-5 h-5 rounded-full bg-blue-600 border-2 border-white shadow-md"

      const marker = new mapboxgl.Marker(el)
        .setLngLat(station.location)
        .setPopup(
          new mapboxgl.Popup({ offset: 25 }).setHTML(
            `<div class="p-2">
              <h3 class="font-bold text-blue-600">${station.name}</h3>
              <p class="text-gray-600">${station.address}</p>
              <p class="text-gray-600">Contact: ${station.contact}</p>
            </div>`
          )
        )
        .addTo(map)

      markersRef.current.push(marker)
    })

    // Add ambulance stations (red markers)
    ambulanceStations.forEach((station) => {
      const el = document.createElement("div")
      el.className = "w-5 h-5 rounded-full bg-red-600 border-2 border-white shadow-md"

      const marker = new mapboxgl.Marker(el)
        .setLngLat(station.location)
        .setPopup(
          new mapboxgl.Popup({ offset: 25 }).setHTML(
            `<div class="p-2">
              <h3 class="font-bold text-red-600">${station.name}</h3>
              <p class="text-gray-600">${station.address}</p>
              <p class="text-gray-600">Contact: ${station.contact}</p>
            </div>`
          )
        )
        .addTo(map)

      markersRef.current.push(marker)
    })

    // Add active vehicles (purple markers)
    vehicles.forEach((vehicle) => {
      const el = document.createElement("div")
      el.className = "w-5 h-5 rounded-full bg-indigo-600 border-2 border-white shadow-md animate-pulse"

      const marker = new mapboxgl.Marker(el)
        .setLngLat(vehicle.location)
        .setPopup(
          new mapboxgl.Popup({ offset: 25 }).setHTML(
            `<div class="p-2">
              <h3 class="font-bold text-indigo-600">${vehicle.type}</h3>
              <p class="text-gray-600">ID: ${vehicle.id}</p>
              <p class="text-gray-600">Status: ${vehicle.status}</p>
            </div>`
          )
        )
        .addTo(map)

      markersRef.current.push(marker)
    })

    // Add emergency locations (yellow markers)
    emergencyLocations.forEach((location) => {
      const el = document.createElement("div")
      el.className = "w-5 h-5 rounded-full bg-yellow-400 border-2 border-white shadow-md animate-ping"

      const marker = new mapboxgl.Marker(el)
        .setLngLat(location.location)
        .setPopup(
          new mapboxgl.Popup({ offset: 25 }).setHTML(
            `<div class="p-2">
              <h3 class="font-bold text-yellow-600">${location.name}</h3>
              <p class="text-gray-600">Type: ${location.type}</p>
            </div>`
          )
        )
        .addTo(map)

      markersRef.current.push(marker)
    })
  }, [vehicles, emergencyLocations, fireStations, policeStations, ambulanceStations, map])

  return (
    <div
      ref={mapContainer}
      className="h-full w-full rounded-lg overflow-hidden min-h-[400px]"
    />
  )
}