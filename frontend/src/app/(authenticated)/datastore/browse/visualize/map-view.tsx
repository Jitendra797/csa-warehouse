"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import dynamic from "next/dynamic";
import { useEffect, useState, useRef } from "react";
import "leaflet/dist/leaflet.css";
import { Feature, FeatureCollection } from "geojson";
import { Layer, LeafletMouseEvent, Map as LeafletMap } from "leaflet";
import { Loader2 } from "lucide-react";

interface GeoJSONFeature extends Feature {
  properties: {
    name: string;
    magnitude?: number;
    [key: string]: unknown;
  };
}

interface GeoJSONData extends FeatureCollection {
  features: GeoJSONFeature[];
}

interface MapViewProps {
  data: [];
}

// Dynamically import Leaflet components with no SSR
const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  {
    ssr: false,
    loading: () => (
      <div className="h-full w-full flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2 text-muted-foreground">Loading map...</span>
      </div>
    ),
  },
);
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false },
);
const GeoJSON = dynamic(
  () => import("react-leaflet").then((mod) => mod.GeoJSON),
  { ssr: false },
);

// Color bins and scale for legend and map coloring
const colorScale = [
  "#FFEDA0", // 0
  "#FED976", // 1
  "#FEB24C", // 2
  "#FD8D3C", // 3
  "#FC4E2A", // 4
  "#E31A1C", // 5
  "#BD0026", // 6
  "#800026", // 7+
];

function getColor(d: number) {
  if (d > 7) return colorScale[7];
  if (d > 6) return colorScale[6];
  if (d > 5) return colorScale[5];
  if (d > 4) return colorScale[4];
  if (d > 3) return colorScale[3];
  if (d > 2) return colorScale[2];
  if (d > 1) return colorScale[1];
  if (d > 0) return colorScale[0];
  return "#f4f4f4"; // No data pattern (light gray)
}

export function MapView({ data }: MapViewProps) {
  const [mounted, setMounted] = useState(false);
  const [mapInitialized, setMapInitialized] = useState(false);
  const [countries, setCountries] = useState<GeoJSONData | null>(null);
  const geojsonRef = useRef<L.GeoJSON | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);

  useEffect(() => {
    const initMap = async () => {
      try {
        // Import Leaflet CSS only on client side
        await import("leaflet/dist/leaflet.css");

        // Fetch countries GeoJSON data
        const response = await fetch(
          "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson",
        );
        const geoData: GeoJSONData = await response.json();
        setCountries(geoData);
        setMounted(true);
      } catch (error) {
        console.error("Error initializing map:", error);
      }
    };

    initMap();
  }, [data]);

  const highlightFeature = (e: LeafletMouseEvent) => {
    const layer = e.target;
    layer.setStyle({
      weight: 2,
      color: "#666",
      dashArray: "",
      fillOpacity: 0.7,
      fillColor: "#e6e6e6",
    });
    layer.bringToFront();
  };

  const resetHighlight = (e: LeafletMouseEvent) => {
    geojsonRef.current?.resetStyle(e.target);
  };

  // Style function for GeoJSON
  function style(feature: Feature | undefined) {
    if (!feature || !feature.properties) {
      return {
        fillColor: "#f4f4f4",
        weight: 1.5,
        opacity: 1,
        color: "#d1d5db",
        fillOpacity: 0.1, // Make non-data countries very transparent
      };
    }
    const mag = (feature.properties as { magnitude?: number }).magnitude || 0;
    if (mag === 0) {
      return {
        fillColor: "#f4f4f4",
        weight: 1.5,
        opacity: 1,
        color: "#d1d5db",
        fillOpacity: 0.1, // Make countries with no data very transparent
      };
    }
    return {
      fillColor: getColor(mag),
      weight: 1.5,
      opacity: 1,
      color: "#d1d5db",
      fillOpacity: 0.9,
    };
  }

  // Tooltip for each country
  const onEachFeature = (feature: GeoJSONFeature, layer: Layer) => {
    layer.on({
      mouseover: highlightFeature,
      mouseout: resetHighlight,
    });
  };

  const onMapReady = () => {
    if (mapRef.current) {
      // Create custom pane for labels
      mapRef.current.createPane("labels");
      const labelsPane = mapRef.current.getPane("labels");
      if (labelsPane) {
        labelsPane.style.zIndex = "650";
        labelsPane.style.pointerEvents = "none";
      }
      setMapInitialized(true);
    }
  };

  if (!mounted) {
    return (
      <Card className="h-[450px] w-full max-w-[1200px] mx-auto overflow-hidden">
        <CardHeader className="flex-none">
          <CardTitle>Map</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 relative h-full w-full max-w-[1200px] p-0">
          <div className="flex h-full w-full items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-2 text-muted-foreground">Loading map...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const center: [number, number] = [20, 0];
  const bounds: [[number, number], [number, number]] = [
    [-60, -180],
    [90, 180],
  ];

  return (
    <Card className="h-[450px] w-full max-w-[1200px] mx-auto overflow-hidden">
      <CardContent className="relative h-full w-full max-w-[1200px] p-0">
        <style>{`
          .leaflet-tooltip.country-label {
            background: none !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            font-size: 16px;
            font-weight: bold;
            color: #222;
            text-shadow: 0 1px 2px #fff, 0 0 2px #fff;
            pointer-events: none;
            min-width: 0 !important;
            min-height: 0 !important;
          }
        `}</style>
        <div className="absolute inset-0 h-full w-full">
          <MapContainer
            center={center}
            zoom={2.2}
            minZoom={2}
            maxZoom={18}
            className="h-full w-full rounded-md"
            zoomControl={false}
            dragging={false}
            doubleClickZoom={false}
            scrollWheelZoom={false}
            touchZoom={false}
            keyboard={false}
            ref={mapRef}
            whenReady={onMapReady}
            bounds={bounds}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png"
              noWrap={true}
            />
            {countries && (
              <GeoJSON
                ref={geojsonRef}
                data={countries}
                style={style}
                onEachFeature={onEachFeature}
              />
            )}
            {mounted && mapInitialized && (
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}.png"
                pane="labels"
                noWrap={true}
              />
            )}
          </MapContainer>
        </div>
      </CardContent>
    </Card>
  );
}
