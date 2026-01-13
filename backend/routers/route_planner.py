from fastapi import APIRouter
from pydantic import BaseModel
import requests
import httpx
import re
import asyncio
import math
from . import tsp
from .nearby_utils import query_nearby
from .pedestrian_router import route_walking, load_pedestrian_network

router = APIRouter()

try:
    load_pedestrian_network()
    PEDESTRIAN_NETWORK_LOADED = True
except Exception as e:
    print(f"Warning: Pedestrian network not loaded: {e}")
    PEDESTRIAN_NETWORK_LOADED = False

OSRM_URL = "http://router.project-osrm.org/route/v1/driving/"
OSRM_WALK_URL = "http://router.project-osrm.org/route/v1/foot/"
KMB_API_BASE = "https://data.etabus.gov.hk/v1/transport/kmb"
WALKING_SPEED_M_PER_MIN = 83.3
API_TIMEOUT = 5.0

MTR_LINES = {
    "Tsuen Wan Line": ["Central", "Admiralty", "Tsim Sha Tsui", "Jordan", "Yau Ma Tei", "Mong Kok", "Prince Edward", "Sham Shui Po", "Cheung Sha Wan", "Lai Chi Kok", "Mei Foo", "Lai King", "Kwai Fong", "Kwai Hing", "Tai Wo Hau", "Tsuen Wan"],
    "Island Line": ["Kennedy Town", "HKU", "Sai Ying Pun", "Sheung Wan", "Central", "Admiralty", "Wan Chai", "Causeway Bay", "Tin Hau", "Fortress Hill", "North Point", "Quarry Bay", "Tai Koo", "Sai Wan Ho", "Shau Kei Wan", "Heng Fa Chuen", "Chai Wan"],
    "Kwun Tong Line": ["Whampoa", "Ho Man Tin", "Yau Ma Tei", "Mong Kok", "Prince Edward", "Shek Kip Mei", "Kowloon Tong", "Lok Fu", "Wong Tai Sin", "Diamond Hill", "Choi Hung", "Kowloon Bay", "Ngau Tau Kok", "Kwun Tong", "Lam Tin", "Yau Tong", "Tiu Keng Leng"],
    "Tuen Mun Line": ["Tuen Mun", "Siu Hong", "Tin Shui Wai", "Long Ping", "Yuen Long", "Kam Sheung Road", "Tsuen Wan West", "Mei Foo", "Nam Cheong", "Austin", "East Tsim Sha Tsui", "Hung Hom"],
    "Tung Chung Line": ["Hong Kong", "Kowloon", "Olympic", "Nam Cheong", "Lai King", "Tsing Yi", "Sunny Bay", "Tung Chung"],
    "East Rail Line": ["Admiralty", "Exhibition Centre", "Hung Hom", "Mong Kok East", "Kowloon Tong", "Tai Wai", "Sha Tin", "Fo Tan", "Racecourse", "University", "Tai Po Market", "Tai Wo", "Fanling", "Sheung Shui", "Lo Wu", "Lok Ma Chau"],
}

COMMON_HK_BUS_ROUTES = ["2", "6", "9", "13X", "41A", "68E"]



def format_distance(distance_m: int) -> str:
    """Format distance as km or m depending on size"""
    return f"{distance_m / 1000:.1f} km" if distance_m >= 1000 else f"{distance_m}m"


def calculate_walk_time(distance_m: int) -> int:
    """Calculate walking time in minutes based on distance"""
    return max(1, round(distance_m / WALKING_SPEED_M_PER_MIN))


async def get_bus_routes_for_stop(stop_id: str) -> list:
    """Get all bus routes serving a specific stop from KMB API"""
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(f"{KMB_API_BASE}/route-stop")
            if response.status_code == 200:
                data = response.json()
                routes = []
                for item in data.get("data", []):
                    if item.get("stop") == stop_id:
                        route_info = {
                            "route": item.get("route"),
                            "bound": item.get("bound"),
                            "service_type": item.get("service_type"),
                            "seq": item.get("seq")
                        }
                        if route_info not in routes:
                            routes.append(route_info)
                return routes
    except Exception:
        pass  # Silently fail and use fallback routes
    return []

async def get_stop_id_by_name(stop_name: str) -> str:
    """Get stop ID from stop name"""
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.get(f"{KMB_API_BASE}/stop")
            if response.status_code == 200:
                data = response.json()
                for stop in data.get("data", []):
                    if stop_name.upper() in stop.get("name_en", "").upper():
                        return stop.get("stop")
    except Exception:
        pass
    return None

def find_mtr_connection(start_station: str, end_station: str) -> dict:
    """Find MTR route between two stations with transfers"""
    # Find which lines contain each station
    start_lines = []
    end_lines = []
    
    for line_name, stations in MTR_LINES.items():
        if start_station in stations:
            start_lines.append((line_name, stations.index(start_station)))
        if end_station in stations:
            end_lines.append((line_name, stations.index(end_station)))
    
    # Check for direct line
    for start_line, start_idx in start_lines:
        for end_line, end_idx in end_lines:
            if start_line == end_line:
                return {
                    "direct": True,
                    "line": start_line,
                    "transfer_at": None
                }
    
    # Find transfer station
    for start_line, start_idx in start_lines:
        for end_line, end_idx in end_lines:
            # Find common stations between lines
            start_stations = set(MTR_LINES[start_line])
            end_stations = set(MTR_LINES[end_line])
            common = start_stations & end_stations
            
            if common:
                # Find the best transfer point
                transfer_station = list(common)[0]
                return {
                    "direct": False,
                    "start_line": start_line,
                    "end_line": end_line,
                    "transfer_at": transfer_station
                }
    
    return {"direct": False, "transfer_at": "Central"}  # Default fallback


# ----------------------------------------------------------
# MODELS
# ----------------------------------------------------------

class RouteRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    walk_only: bool = False  # For direct walk-to-stop routes


class MultiStopRequest(BaseModel):
    points: list[dict]


class OptimizeRequest(BaseModel):
    points: list[dict]


# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------

def osrm_polyline(coords: list[list[float]], style: str = "dotted"):
    """Convert OSRM LNG,LAT → LAT,LNG polyline format with style"""
    return [[lat, lng, style] for lng, lat in coords]



@router.post("/enhanced")
async def enhanced_route(req: RouteRequest):
    """Get detailed route with walking + transit instructions"""
    
    # Find nearby transit stops at start (within 500m)
    start_stops = await query_nearby(req.start_lat, req.start_lng, radius_m=500, limit=10)
    
    # Find nearby transit stops at end (within 500m)
    end_stops = await query_nearby(req.end_lat, req.end_lng, radius_m=500, limit=10)
    
    instructions = []
    total_distance = 0
    total_duration = 0
    polyline_out = []  # final polyline to return (lat,lng pairs)

    # Try pedestrian network first if available
    if PEDESTRIAN_NETWORK_LOADED and req.walk_only:
        polyline, distance = route_walking(req.start_lat, req.start_lng, req.end_lat, req.end_lng)
        if polyline:
            total_distance = round(distance)
            total_duration = calculate_walk_time(total_distance) * 60
            instructions = [{
                "type": "walk",
                "instruction": "Walk along pedestrian path",
                "distance_m": total_distance,
                "duration_s": round(total_duration)
            }]
            polyline_out = polyline
    
    # Fallback to OSRM if pedestrian network route not found
    if not polyline_out:
        walk_coords = f"{req.start_lng},{req.start_lat};{req.end_lng},{req.end_lat}"
        walk_url = f"{OSRM_WALK_URL}{walk_coords}?overview=full&geometries=geojson&steps=true"
        walk_resp = requests.get(walk_url).json()
        
        if walk_resp.get("routes"):
            route = walk_resp["routes"][0]
            total_distance = route["distance"]
            total_duration = route["duration"]
            
            # Parse walking steps
            for leg in route.get("legs", []):
                for step in leg.get("steps", []):
                    maneuver = step.get("maneuver", {})
                    instruction = maneuver.get("instruction", "")
                    distance = step.get("distance", 0)
                    duration = step.get("duration", 0)
                    
                    if instruction and distance > 10:  # Skip very short steps
                        instructions.append({
                            "type": "walk",
                            "instruction": instruction,
                            "distance_m": round(distance),
                            "duration_s": round(duration)
                        })

            # Use OSRM's actual routed path
            coords = route["geometry"]["coordinates"]
            polyline_out = osrm_polyline(coords)

    # Add nearby stops info only if not in walk-only mode
    transit_options = []
    
    if not req.walk_only:
        # Check for MTR near start
        mtr_start = [s for s in start_stops if s["type"] == "MTR"]
        if mtr_start:
            closest_mtr = mtr_start[0]
            # Calculate realistic walk time: 5 km/h = 83.3 m/min
            mtr_walk_time = calculate_walk_time(closest_mtr["distance"])
            mtr_distance_display = format_distance(closest_mtr["distance"])
            transit_options.append({
                "type": "MTR",
                "stop_name": closest_mtr["name"],
                "stop_lat": closest_mtr["lat"],
                "stop_lng": closest_mtr["lng"],
                "distance_to_stop_m": closest_mtr["distance"],
                "walk_time_min": mtr_walk_time,
                "instruction": f"Walk {mtr_distance_display} ({mtr_walk_time} min) to {closest_mtr['name']}"
            })
        
        # Check for Bus near start
        bus_start = [s for s in start_stops if s["type"] == "Bus Stop"]
        if bus_start:
            closest_bus = bus_start[0]
            bus_walk_time = calculate_walk_time(closest_bus["distance"])
            bus_distance_display = format_distance(closest_bus["distance"])
            transit_options.append({
                "type": "Bus",
                "stop_name": closest_bus["name"],
                "stop_lat": closest_bus["lat"],
                "stop_lng": closest_bus["lng"],
                "distance_to_stop_m": closest_bus["distance"],
                "walk_time_min": bus_walk_time,
                "instruction": f"Walk {bus_distance_display} ({bus_walk_time} min) to bus stop: {closest_bus['name']}"
            })
        
        # Check for Ferry near start
        ferry_start = [s for s in start_stops if s["type"] == "Ferry Pier"]
        if ferry_start:
            closest_ferry = ferry_start[0]
            ferry_walk_time = calculate_walk_time(closest_ferry["distance"])
            ferry_distance_display = format_distance(closest_ferry["distance"])
            transit_options.append({
                "type": "Ferry",
                "stop_name": closest_ferry["name"],
                "stop_lat": closest_ferry["lat"],
                "stop_lng": closest_ferry["lng"],
                "distance_to_stop_m": closest_ferry["distance"],
                "walk_time_min": ferry_walk_time,
                "instruction": f"Walk {ferry_distance_display} ({ferry_walk_time} min) to ferry pier: {closest_ferry['name']}"
            })
    
    return {
        "distance_m": round(total_distance),
        "duration_s": round(total_duration),
        "walk_distance_m": round(total_distance),
        "walk_duration_min": round(total_duration / 60),
        "polyline": polyline_out,
        "instructions": instructions,
        "transit_options": transit_options,
        "nearby_start_stops": start_stops[:5] if not req.walk_only else [],
        "nearby_end_stops": end_stops[:5] if not req.walk_only else []
    }


# ----------------------------------------------------------
# TRANSIT DETAIL - Get step-by-step instructions for specific transit option
# ----------------------------------------------------------

class TransitDetailRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    stop_name: str
    stop_type: str
    stop_lat: float
    stop_lng: float

@router.post("/transit-detail")
async def transit_detail(req: TransitDetailRequest):
    """Get detailed multi-modal journey options with real bus routes and MTR data"""
    
    route_options = []
    
    end_stops = await query_nearby(req.end_lat, req.end_lng, radius_m=800, limit=20)
    bus_stops_at_end = [s for s in end_stops if s["type"] == "Bus Stop"]
    mtr_stops_at_end = [s for s in end_stops if s["type"] == "MTR"]
    
    print(f"DEBUG: Found {len(bus_stops_at_end)} bus stops and {len(mtr_stops_at_end)} MTR stops near destination")
    walk_to_stop_coords = f"{req.start_lng},{req.start_lat};{req.stop_lng},{req.stop_lat}"
    walk_to_url = f"{OSRM_WALK_URL}{walk_to_stop_coords}?overview=full&geometries=geojson"
    walk_to_resp = requests.get(walk_to_url).json()
    initial_walk_dist = round(walk_to_resp["routes"][0]["distance"]) if walk_to_resp.get("routes") else 0
    initial_walk_time = max(1, round(initial_walk_dist / 83.3)) if initial_walk_dist > 0 else 0
    initial_walk_display = f"{initial_walk_dist / 1000:.1f} km" if initial_walk_dist >= 1000 else f"{initial_walk_dist}m"
    initial_walk_time = calculate_walk_time(initial_walk_dist) if initial_walk_dist > 0 else 0
    initial_walk_display = format_distance(initial_walk_dist)
    
    real_bus_routes = []
    if req.stop_type == "Bus":
        stop_id_match = re.search(r'\(([A-Z0-9-]+)\)', req.stop_name)
        if stop_id_match:
            stop_id = stop_id_match.group(1)
            real_bus_routes = await get_bus_routes_for_stop(stop_id)
    
    unique_routes = list(set([r["route"] for r in real_bus_routes[:10]])) if real_bus_routes else []
    
    if not unique_routes:
        unique_routes = COMMON_HK_BUS_ROUTES
    
    if req.stop_type == "Bus":
        destination_stop_name = bus_stops_at_end[0]["name"] if bus_stops_at_end else "destination area"
        final_walk_dist = round(bus_stops_at_end[0]["distance"]) if bus_stops_at_end else 200
        final_walk_time = calculate_walk_time(final_walk_dist)
        final_walk_display = format_distance(final_walk_dist)
        
        bus_list_str = ", ".join(unique_routes[:4]) if unique_routes else "available bus"
        
        direct_bus_option = {
            "option_name": "🚌 Direct Bus",
            "total_duration_min": initial_walk_time + 20 + final_walk_time,
            "steps": [
                {
                    "type": "walk",
                    "action": f"Walk to bus stop",
                    "instruction": f"Walk {initial_walk_display} ({initial_walk_time} min) to {req.stop_name}",
                    "distance_m": initial_walk_dist,
                    "duration_min": initial_walk_time
                },
                {
                    "type": "bus",
                    "action": "Board bus",
                    "instruction": f"Take bus {bus_list_str} towards destination",
                    "bus_number": bus_list_str,
                    "get_off_at": destination_stop_name,
                    "duration_min": 20
                },
                {
                    "type": "walk",
                    "action": "Walk to destination",
                    "instruction": f"Walk {final_walk_display} to your destination",
                    "distance_m": final_walk_dist,
                    "duration_min": final_walk_time
                }
            ]
        }
        route_options.append(direct_bus_option)
    
    if req.stop_type == "Bus" and bus_stops_at_end:
        nearby_major_stops = await query_nearby(req.stop_lat, req.stop_lng, radius_m=1500, limit=15, types=["Bus Stop"])
        
        interchange_stops = [s for s in nearby_major_stops if "INTERCHANGE" in s["name"].upper() or "TERMINUS" in s["name"].upper()]
        
        if interchange_stops:
            transfer_stop = interchange_stops[0]
            
            transfer_stop_match = re.search(r'\(([A-Z0-9-]+)\)', transfer_stop["name"])
            transfer_routes = []
            if transfer_stop_match:
                transfer_stop_id = transfer_stop_match.group(1)
                transfer_routes = await get_bus_routes_for_stop(transfer_stop_id)
            
            second_leg_routes = list(set([r["route"] for r in transfer_routes[:8]])) if transfer_routes else []
            second_bus_str = ", ".join(second_leg_routes[:4]) if second_leg_routes else "connecting bus"
            
            bus_transfer_option = {
                "option_name": "🚌 Bus with Transfer",
                "total_duration_min": 35,
                "steps": [
                    {
                        "type": "walk",
                        "action": f"Walk to bus stop",
                        "instruction": f"Walk {initial_walk_dist}m to {req.stop_name}",
                        "distance_m": initial_walk_dist,
                        "duration_min": initial_walk_time
                    },
                    {
                        "type": "bus",
                        "action": "Take first bus",
                        "instruction": f"Take bus {unique_routes[0] if unique_routes else 'from this stop'} to {transfer_stop['name']}",
                        "bus_number": unique_routes[0] if unique_routes else "Check schedule",
                        "get_off_at": transfer_stop["name"],
                        "duration_min": 15
                    },
                    {
                        "type": "transfer",
                        "action": "Transfer at interchange",
                        "instruction": f"Transfer to connecting bus at {transfer_stop['name']}",
                        "distance_m": 50,
                        "duration_min": 3
                    },
                    {
                        "type": "bus",
                        "action": "Take connecting bus",
                        "instruction": f"Board bus {second_bus_str} towards destination",
                        "bus_number": second_bus_str,
                        "get_off_at": bus_stops_at_end[0]["name"] if bus_stops_at_end else "destination stop",
                        "duration_min": 15
                    },
                    {
                        "type": "walk",
                        "action": "Walk to destination",
                        "instruction": f"Walk {round(bus_stops_at_end[0]['distance']) if bus_stops_at_end else 100}m to your destination",
                        "distance_m": round(bus_stops_at_end[0]["distance"]) if bus_stops_at_end else 100,
                        "duration_min": 2
                    }
                ]
            }
            route_options.append(bus_transfer_option)
    
    if mtr_stops_at_end:
        nearby_mtr = await query_nearby(req.stop_lat, req.stop_lng, radius_m=1500, limit=5, types=["MTR"])
        
        if nearby_mtr:
            start_mtr = nearby_mtr[0]
            end_mtr = mtr_stops_at_end[0]
            
            start_station_name = start_mtr['name'].replace(" Station", "")
            end_station_name = end_mtr['name'].replace(" Station", "")
            mtr_connection = find_mtr_connection(start_station_name, end_station_name)
            
            if mtr_connection.get("direct"):
                mtr_instruction = f"Take {mtr_connection['line']} from {start_station_name} to {end_station_name}"
                exit_suggestion = "Follow exit signs"
            elif mtr_connection.get("transfer_at"):
                mtr_instruction = f"Take {mtr_connection.get('start_line', 'MTR')} to {mtr_connection['transfer_at']}, then change to {mtr_connection.get('end_line', 'connecting line')} to {end_station_name}"
                exit_suggestion = f"Transfer at {mtr_connection['transfer_at']}"
            else:
                mtr_instruction = f"Take MTR from {start_station_name} to {end_station_name}"
                exit_suggestion = "Follow exit signs"
            
            mtr_walk_option = {
                "option_name": "🚇 MTR",
                "total_duration_min": 30,
                "steps": [
                    {
                        "type": "walk",
                        "action": f"Walk to MTR station",
                        "instruction": f"Walk {round(start_mtr['distance'])}m to {start_mtr['name']}",
                        "distance_m": round(start_mtr["distance"]),
                        "duration_min": max(1, round(start_mtr["walk_min"]))
                    },
                    {
                        "type": "mtr",
                        "action": "Take MTR",
                        "instruction": mtr_instruction,
                        "get_off_at": end_mtr["name"],
                        "exit_info": exit_suggestion,
                        "duration_min": 20
                    },
                    {
                        "type": "walk",
                        "action": "Walk to destination",
                        "instruction": f"Walk {round(end_mtr['distance'])}m to destination",
                        "distance_m": round(end_mtr["distance"]),
                        "duration_min": max(1, round(end_mtr["walk_min"]))
                    }
                ]
            }
            route_options.append(mtr_walk_option)
            
            if bus_stops_at_end:
                end_mtr_bus_stops = await query_nearby(end_mtr["lat"], end_mtr["lng"], radius_m=300, limit=5, types=["Bus Stop"])
                
                feeder_routes = []
                if end_mtr_bus_stops:
                    for stop in end_mtr_bus_stops:
                        stop_match = re.search(r'\(([A-Z0-9-]+)\)', stop["name"])
                        if stop_match:
                            stop_routes = await get_bus_routes_for_stop(stop_match.group(1))
                            feeder_routes.extend([r["route"] for r in stop_routes])
                
                unique_feeder = list(set(feeder_routes[:5]))
                feeder_bus_str = ", ".join(unique_feeder[:3]) if unique_feeder else "feeder bus"
                
                mtr_bus_option = {
                    "option_name": "🚇 MTR + Bus",
                    "total_duration_min": 32,
                    "steps": [
                        {
                            "type": "walk",
                            "action": f"Walk to MTR",
                            "instruction": f"Walk to {start_mtr['name']}",
                            "distance_m": round(start_mtr["distance"]),
                            "duration_min": max(1, round(start_mtr["walk_min"]))
                        },
                        {
                            "type": "mtr",
                            "action": "Take MTR",
                            "instruction": mtr_instruction,
                            "get_off_at": end_mtr["name"],
                            "exit_info": "Exit to bus stops",
                            "duration_min": 20
                        },
                        {
                            "type": "bus",
                            "action": "Take connecting bus",
                            "instruction": f"Take bus {feeder_bus_str} from MTR exit",
                            "bus_number": feeder_bus_str,
                            "get_off_at": bus_stops_at_end[0]["name"] if bus_stops_at_end else "destination stop",
                            "duration_min": 8
                        },
                        {
                            "type": "walk",
                            "action": "Walk to destination",
                            "instruction": f"Walk {round(bus_stops_at_end[0]['distance']) if bus_stops_at_end else 50}m to destination",
                            "distance_m": round(bus_stops_at_end[0]["distance"]) if bus_stops_at_end else 50,
                            "duration_min": 1
                        }
                    ]
                }
                route_options.append(mtr_bus_option)
    
    if req.stop_type == "Ferry":
        end_ferry_piers = [s for s in end_stops if s["type"] == "Ferry Pier"]
        
        if end_ferry_piers:
            ferry_option = {
                "option_name": "⛴️ Ferry",
                "total_duration_min": initial_walk_time + 15 + 5,
                "steps": [
                    {
                        "type": "walk",
                        "action": "Walk to ferry pier",
                        "instruction": f"Walk {initial_walk_display} ({initial_walk_time} min) to {req.stop_name}",
                        "distance_m": initial_walk_dist,
                        "duration_min": initial_walk_time
                    },
                    {
                        "type": "ferry",
                        "action": "Board ferry",
                        "instruction": f"Take ferry from {req.stop_name}",
                        "get_off_at": end_ferry_piers[0]["name"],
                        "duration_min": 15
                    },
                    {
                        "type": "walk",
                        "action": "Walk to destination",
                        "instruction": f"Walk {round(end_ferry_piers[0]['distance'])}m to destination",
                        "distance_m": round(end_ferry_piers[0]["distance"]),
                        "duration_min": 5
                    }
                ]
            }
            route_options.append(ferry_option)
    
    return {
        "route_options": route_options,
        "total_options": len(route_options)
    }



@router.post("/polyline")
def route_polyline(req: RouteRequest):

    start = f"{req.start_lng},{req.start_lat}"
    end = f"{req.end_lng},{req.end_lat}"

    url = f"{OSRM_URL}{start};{end}?overview=full&geometries=geojson"
    osrm = requests.get(url).json()

    coords = osrm["routes"][0]["geometry"]["coordinates"]

    return {
        "polyline": osrm_polyline(coords),
        "distance_m": osrm["routes"][0]["distance"],
        "duration_s": osrm["routes"][0]["duration"]
    }



@router.post("/multistop")
def multistop(req: MultiStopRequest):

    if len(req.points) < 2:
        return {"polyline": []}

    coord_list = ";".join([f"{p['lng']},{p['lat']}" for p in req.points])
    url = f"{OSRM_URL}{coord_list}?overview=full&geometries=geojson"

    try:
        osrm = requests.get(url, timeout=10).json()
        
        if not osrm.get("routes") or len(osrm["routes"]) == 0:
            return {"error": "No routes found. Please check your waypoints."}
        
        coords = osrm["routes"][0]["geometry"]["coordinates"]

        return {
            "polyline": osrm_polyline(coords),
            "distance_m": osrm["routes"][0]["distance"],
            "duration_s": osrm["routes"][0]["duration"]
        }
    except requests.exceptions.Timeout:
        return {"error": "Route service timeout. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to routing service. Please check your internet connection."}
    except Exception as e:
        return {"error": f"Routing error: {str(e)}"}



@router.post("/optimize")
def optimize(req: OptimizeRequest):
    pts = req.points

    if len(pts) < 3:
        return {"error": "Need at least 3 points"}

    coord_list = ";".join([f"{p['lng']},{p['lat']}" for p in pts])
    table_url = f"http://router.project-osrm.org/table/v1/driving/{coord_list}?annotations=distance,duration"

    try:
        tbl = requests.get(table_url, timeout=10).json()
    except requests.exceptions.Timeout:
        return {"error": "OSRM service timeout. Please try again."}
    except Exception as e:
        return {"error": f"OSRM table request failed: {str(e)}"}

    matrix = tbl.get("durations") or tbl.get("distances")
    if not matrix:
        return {"error": "OSRM table did not return a distances/durations matrix"}

    order = tsp.solve_tsp_nearest_2opt(matrix, start=0)

    ordered_pts = [pts[i] for i in order]
    coord_list_ordered = ";".join([f"{p['lng']},{p['lat']}" for p in ordered_pts])
    route_url = f"{OSRM_URL}{coord_list_ordered}?overview=full&geometries=geojson"

    try:
        osrm = requests.get(route_url, timeout=10).json()
        
        if not osrm.get("routes") or len(osrm["routes"]) == 0:
            return {"error": "No optimized route found.", "ordered_index": order}
        
        coords = osrm["routes"][0]["geometry"]["coordinates"]

        return {
            "optimized": ordered_pts,
            "ordered_index": order,
            "polyline": osrm_polyline(coords),
            "distance_m": osrm["routes"][0]["distance"],
            "duration_s": osrm["routes"][0]["duration"]
        }
    except requests.exceptions.Timeout:
        return {"error": "OSRM route service timeout. Please try again.", "ordered_index": order}
    except Exception as e:
        return {"error": f"OSRM route request failed: {str(e)}", "ordered_index": order}


class AlternativesRequest(BaseModel):
    points: list[dict]


@router.post('/alternatives')
def alternatives(req: AlternativesRequest):
    pts = req.points
    if not pts or len(pts) < 2:
        return {"alternatives": []}

    coord_list = ";".join([f"{p['lng']},{p['lat']}" for p in pts])
    url = f"{OSRM_URL}{coord_list}?overview=full&geometries=geojson"
    try:
        base = requests.get(url, timeout=10).json()
        base_coords = base['routes'][0]['geometry']['coordinates']
        base_obj = {
            'name': 'In-order',
            'polyline': osrm_polyline(base_coords),
            'distance_m': base['routes'][0]['distance'],
            'duration_s': base['routes'][0]['duration']
        }
    except Exception as e:
        base_obj = None

    try:
        table_coord_list = coord_list
        table_url = f"http://router.project-osrm.org/table/v1/driving/{table_coord_list}?annotations=distance,duration"
        tbl = requests.get(table_url, timeout=10).json()
        matrix = tbl.get('durations') or tbl.get('distances')
        if matrix:
            order = tsp.solve_tsp_nearest_2opt(matrix, start=0)
            ordered_pts = [pts[i] for i in order]
            coord_list_ordered = ";".join([f"{p['lng']},{p['lat']}" for p in ordered_pts])
            route_url = f"{OSRM_URL}{coord_list_ordered}?overview=full&geometries=geojson"
            osrm = requests.get(route_url, timeout=10).json()
            opt_coords = osrm['routes'][0]['geometry']['coordinates']
            opt_obj = {
                'name': 'Optimized',
                'polyline': osrm_polyline(opt_coords),
                'distance_m': osrm['routes'][0]['distance'],
                'duration_s': osrm['routes'][0]['duration'],
                'ordered_index': order
            }
        else:
            opt_obj = None
    except Exception:
        opt_obj = None

    alts = []
    if base_obj:
        alts.append(base_obj)
    if opt_obj:
        if not (base_obj and abs(base_obj['distance_m'] - opt_obj['distance_m']) < 1):
            alts.append(opt_obj)

    return {'alternatives': alts}
