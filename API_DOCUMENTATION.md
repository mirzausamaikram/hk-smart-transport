# HK Smart Transport - API Documentation

## Base URL
```
http://127.0.0.1:8000
```

## Overview
The HK Smart Transport API provides comprehensive route planning, transport information, and location services for Hong Kong's public transportation system. It integrates data from MTR, KMB Bus, Star Ferry, and other transport operators.

---

## 🔍 Geocoding APIs

### `GET /api/geocode/search`
Search for locations using OpenStreetMap's Nominatim service.

**Parameters:**
- `q` (string, required) - Search query (e.g., "Victoria Park", "Central Hong Kong")

**Response:**
```json
{
  "results": [
    {
      "name": "Location display name",
      "lat": 22.2849,
      "lng": 114.1589
    }
  ]
}
```

**Example:**
```
GET /api/geocode/search?q=Victoria%20Park
```

---

## 🚌 Bus APIs

### `GET /api/bus/eta/{stop_id}`
Get real-time bus ETA for a specific stop from KMB (Kowloon Motor Bus).

**Parameters:**
- `stop_id` (string, path) - Bus stop ID

**Response:**
```json
{
  "eta": [
    {
      "route": "2",
      "dest": "Causeway Bay",
      "eta": "2026-01-26T10:15:00"
    }
  ]
}
```

### `GET /api/bus/stops`
Get all KMB bus stops with coordinates.

**Response:**
```json
{
  "stops": [
    {
      "stop_id": "001",
      "name_en": "Star Ferry",
      "lat": 22.2849,
      "lng": 114.1589
    }
  ]
}
```

### `GET /api/citybus/eta/{company}/{stop_id}/{route}`
Get real-time ETA for City Bus or NWFB buses.

**Parameters:**
- `company` (string) - Bus company code (e.g., "CTB", "NWFB")
- `stop_id` (string) - Bus stop ID
- `route` (string) - Bus route number

**Response:**
```json
{
  "eta": [
    {
      "route": "6",
      "dest": "Chai Wan",
      "eta": "2026-01-26T10:20:00"
    }
  ]
}
```

---

## 🚇 MTR (Mass Transit Railway) APIs

### `GET /api/mtr-geo/stations`
Get all MTR stations with coordinates and line information.

**Response:**
```json
{
  "stations": [
    {
      "name": "Hong Kong",
      "line": "TWL",
      "lat": 22.2849,
      "lng": 114.1589,
      "color": "#ee2e24"
    }
  ]
}
```

### `GET /api/stations/bus-stops`
Get all bus stops (includes MTR integration data).

---

## 🗺️ Nearby Transport & POI APIs

### `GET /api/nearby/?lat={lat}&lng={lng}&radius={radius}&types={type}&limit={limit}`
Find nearby transport stops and points of interest.

**Parameters:**
- `lat` (float, required) - Latitude
- `lng` (float, required) - Longitude  
- `radius` (integer, optional) - Search radius in meters (default: 800)
- `types` (string, optional, repeatable) - Filter by type: `MTR`, `Bus Stop`, `Ferry Pier`, etc.
- `limit` (integer, optional) - Maximum results (default: 50)

**Response:**
```json
{
  "results": [
    {
      "type": "MTR",
      "name": "Admiralty",
      "lat": 22.2790,
      "lng": 114.1640,
      "distance": 245
    }
  ]
}
```

**Example:**
```
GET /api/nearby/?lat=22.2849&lng=114.1589&radius=500&types=MTR&types=Bus%20Stop&limit=10
```

### `GET /api/pois/nearby?lat={lat}&lng={lng}&radius={radius}&limit={limit}`
Get nearby Points of Interest (restaurants, attractions, landmarks) from local dataset.

**Parameters:**
- `lat` (float, required) - Latitude
- `lng` (float, required) - Longitude
- `radius` (integer, optional) - Search radius in meters (default: 800)
- `limit` (integer, optional) - Maximum results (default: 3)

**Response:**
```json
{
  "results": [
    {
      "name": "Victoria Peak",
      "type": "sightseeing",
      "lat": 22.3193,
      "lng": 114.1729,
      "distance": 1200,
      "description": "Highest point in Hong Kong",
      "opening_hours": "09:00-23:00"
    }
  ]
}
```

---

## 🛤️ Route Planning APIs

### `POST /api/route/plan`
Plan a multi-modal route between two locations.

**Request Body:**
```json
{
  "start_place": "Central Station",
  "end_place": "Victoria Peak",
  "start_lat": 22.2820,
  "start_lng": 114.1588,
  "end_lat": 22.3193,
  "end_lng": 114.1729,
  "transport_modes": ["MTR", "walk"],
  "avoid_highways": false
}
```

**Response:**
```json
{
  "routes": [
    {
      "summary": "MTR + Walk",
      "duration_minutes": 25,
      "distance_m": 1200,
      "steps": [
        {
          "instruction": "Board MTR from Central",
          "duration": 10,
          "distance": 800
        }
      ]
    }
  ]
}
```

---

## 📍 Itinerary APIs

### `POST /api/itinerary/generate`
Generate a simple itinerary for multiple places.

**Request Body:**
```json
{
  "places": ["Central", "Victoria Peak", "Star Ferry"]
}
```

**Response:**
```json
{
  "steps": [
    "Start at Central.",
    "Then travel to Victoria Peak.",
    "Then travel to Star Ferry.",
    "Itinerary complete."
  ]
}
```

### `POST /api/itinerary/ai`
Generate an AI-powered intelligent itinerary with detailed recommendations.

**Request Body:**
```json
{
  "start_place": "Central",
  "end_place": "Victoria Peak",
  "transport": "MTR",
  "preference": "scenic",
  "date": "2026-01-26",
  "time": "09:00",
  "budget": 200.00,
  "interests": ["sightseeing", "restaurants"],
  "num_options": 1
}
```

**Response:**
```json
{
  "itinerary": "# Central to Victoria Peak Itinerary\n\n**09:00-09:30** - Start at Central\n...",
  "cost_hkd": 150,
  "duration_hours": 3
}
```

---

## 🚌 Bus Route Shape APIs

### `GET /api/bus/shape/{route}`
Get the geographic shape/polyline of a bus route for map visualization.

**Parameters:**
- `route` (string, path) - Bus route number (e.g., "2", "6")

**Response:**
```json
{
  "polyline": [
    {"lat": 22.2849, "lng": 114.1589},
    {"lat": 22.2850, "lng": 114.1600},
    {"lat": 22.2851, "lng": 114.1610}
  ]
}
```

---

## Error Handling

All endpoints return error responses in the following format:

```json
{
  "error": "Error description",
  "results": []
}
```

Common HTTP Status Codes:
- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Resource not found
- `500` - Server error

---

## Data Sources

- **MTR**: Hong Kong Mass Transit Railway Corporation
- **Buses**: KMB, CityBus, NWFB via Government Data Portal
- **Geocoding**: OpenStreetMap Nominatim
- **Routing**: OSRM (Open Source Routing Machine)
- **POIs**: Local JSON dataset (`backend/data/pois.json`)

---

## Rate Limiting

No official rate limiting. External APIs (Nominatim, OSRM, Government Data Portal) have their own limits.

---

## Authentication

Not required. All endpoints are publicly accessible.

---

## CORS

CORS headers are enabled for all origins (`*`), allowing cross-origin requests from the frontend.

---

## Frontend Integration

The SvelteKit frontend communicates with these APIs through the following main pages:
- **Route Planner** (`/route-planner`) - Uses `/api/route/plan`
- **Itinerary** (`/itinerary`) - Uses `/api/itinerary/*`
- **Nearby Stations** (`/nearby-stations`) - Uses `/api/nearby`
- **Multi-route** (`/multi`) - Uses route planning with multiple waypoints
