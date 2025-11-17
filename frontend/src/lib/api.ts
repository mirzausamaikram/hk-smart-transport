/**
 * MOCK API FILE: Allows the frontend Svelte pages to compile and run 
 * before the Flask backend is fully implemented.
 * * NOTE: All functions mimic an asynchronous network call.
 */

// --- Type Definitions ---

// Route Planner Mock Params

interface RouteParams {
    start: string;
    end: string;
    preference: 'fastest' | 'cheapest' | 'fewest';
    transportMode: 'transit' | 'bus' | 'mtr' | 'taxi'; 
}

// CSDI GeoJSON Feature Structure (Simplified)
interface CSDIFeature {
    type: "Feature";
    properties: {
        name: string;
        // Add other properties that might be useful
        type: string;
    };
    geometry: {
        type: "Point";
        coordinates: [number, number]; // [lng, lat]
    };
}


// --- 1. Route Planner Mock (used by src/routes/+page.svelte) ---
/**
 * Mocks the route search API call, returning a pre-defined route.
 */
export async function searchRoute(params: RouteParams): Promise<any> {
    console.log('Mock searchRoute called with:', params);
    
    // Mock data for the Map: Central (Start) to Tsim Sha Tsui (End)
    const mockStartLat = 22.2855; 
    const mockStartLng = 114.1582; 
    const mockEndLat = 22.3193;
    const mockEndLng = 114.1694;
    
    // Simulate a network delay
    await new Promise(resolve => setTimeout(resolve, 300));

    return {
        routes: [
            {
                time: "55 min (MOCK)",
                fare: 14.5,
                transfers: 1,
                // Mock polyline covering the route. Must be encoded.
                polyline: "wvteEw~cEyLd@e@kBh@oAhBcD`AcCfA{C`@oA`@uAn@yB`A{E`AaDj@mBb@sAj@wA", 
                legs: [
                    {
                        start_location: { lat: mockStartLat, lng: mockStartLng }, 
                        end_location: { lat: mockEndLat, lng: mockEndLng } 
                    }
                ],
                steps: [
                    { instruction: `MOCK: Walk from ${params.start}` },
                    { instruction: `MOCK: Take ${params.transportMode.toUpperCase()} (${params.preference} route)` },
                    { instruction: `MOCK: Arrive at ${params.end}` }
                ]
            }
        ]
    };
}

// --- 2. Nearby Finder Mock (used by src/routes/nearby/+page.svelte) ---
/**
 * Mocks the API call to find transport stops and POIs near a location.
 */
export async function getNearby(lat: number, lng: number): Promise<any> {
    console.log('Mock getNearby called at:', lat, lng);
    
    // Simulate a network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Returns mock transport stops and general POIs near the query location
    return {
        stops: [
            { name: "MOCK Bus Stop", lat: lat + 0.005, lon: lng + 0.005, dist_m: 500, type: "bus" },
            { name: "MOCK MTR Station", lat: lat - 0.002, lon: lng + 0.001, dist_m: 250, type: "mtr" }
        ],
        pois: [
            { name: "MOCK Museum POI", lat: lat + 0.001, lon: lng - 0.004, type: "museum" }, 
            { name: "MOCK Park POI", lat: lat - 0.003, lon: lng - 0.001, type: "park" }
        ]
    };
}

// --- 3. Itinerary Solver Mock (used by src/routes/itinerary/+page.svelte) ---
/**
 * Mocks the API call to calculate an itinerary route.
 */
export async function solveItinerary(data: { stops: string[], tourist_mode: boolean }): Promise<any> {
    console.log('Mock solveItinerary called with:', data);
    
    // Simulate a network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    return {
        itinerary: {
            total_time: 120, // min
            total_fare: 45.0, // HKD
            stops: data.stops,
            pois: data.tourist_mode ? [{ name: "MOCK Museum", dwell_time: 120 }] : []
        }
    };
}

// Backwards-compatible export name expected by some routes
export const saveItinerary = solveItinerary;

// --- 4. CSDI API Data Fetcher Mock ---
/**
 * Mocks fetching GeoJSON data from a CSDI WFS endpoint.
 */
export async function fetchCediGeoJSON(layerName: string): Promise<CSDIFeature[]> {
    console.log(`Mock fetchCediGeoJSON called for layer: ${layerName}`);
    
    // Simulate GeoJSON output for the 'MAJOR_MINES_Layer' near a central HK location
    const mockMines = [
        {
            type: "Feature",
            properties: { name: "Mine Site A (MOCK)", type: "mine" },
            geometry: { type: "Point", coordinates: [114.1705, 22.3300] } // [lng, lat]
        },
        {
            type: "Feature",
            properties: { name: "Quarry Site B (MOCK)", type: "quarry" },
            geometry: { type: "Point", coordinates: [114.2000, 22.3500] } // [lng, lat]
        }
    ];

    // Simulate an API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return mockMines as CSDIFeature[];
}