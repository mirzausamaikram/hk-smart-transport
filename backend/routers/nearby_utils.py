import asyncio
import math
import os
import json
import time
from typing import List, Dict, Any, Tuple
import httpx
from geopy.distance import geodesic

# Data source URLs
BUS_URL = "https://data.etabus.gov.hk/v1/transport/kmb/stop"
MTR_URL = "https://rt.data.gov.hk/v1/transport/mtr/station_lat_lng.json"

# Hardcoded sample stations for other transport types (APIs returning 403)
SAMPLE_MINIBUS = [
    {"name": "Jordan Road Minibus Stop", "lat": 22.3047, "lng": 114.1719},
    {"name": "Mong Kok Minibus Terminal", "lat": 22.3193, "lng": 114.1694},
    {"name": "Tsim Sha Tsui Minibus Stop", "lat": 22.2976, "lng": 114.1722},
    {"name": "Ho Man Tin Minibus Stop", "lat": 22.3100, "lng": 114.1780},
    {"name": "Whampoa Minibus Stop", "lat": 22.3050, "lng": 114.1820},
]

SAMPLE_FERRY = [
    {"name": "Central Pier No. 7", "lat": 22.2875, "lng": 114.1594},
    {"name": "Wan Chai Ferry Pier", "lat": 22.2829, "lng": 114.1728},
    {"name": "North Point Ferry Pier", "lat": 22.2931, "lng": 114.2077},
    {"name": "Hung Hom Ferry Pier", "lat": 22.3030, "lng": 114.1830},
    {"name": "Star Ferry Central", "lat": 22.2847, "lng": 114.1589},
    {"name": "Star Ferry Tsim Sha Tsui", "lat": 22.2956, "lng": 114.1727},
    {"name": "Star Ferry Wan Chai", "lat": 22.2828, "lng": 114.1737},
]

SAMPLE_TAXI = [
    {"name": "Central Taxi Stand", "lat": 22.2812, "lng": 114.1577},
    {"name": "Causeway Bay Taxi Stand", "lat": 22.2799, "lng": 114.1851},
    {"name": "Tsim Sha Tsui Taxi Stand", "lat": 22.2989, "lng": 114.1727},
    {"name": "Jordan Taxi Stand", "lat": 22.3050, "lng": 114.1715},
    {"name": "Mong Kok Taxi Stand", "lat": 22.3190, "lng": 114.1700},
]

MTR_STATIONS = {
    "central": {"name": "Central Station", "lat": 22.2837, "lng": 114.1592},
    "admiralty": {"name": "Admiralty Station", "lat": 22.2766, "lng": 114.1637},
    "wanchai": {"name": "Wan Chai Station", "lat": 22.2749, "lng": 114.1744},
    "causeway": {"name": "Causeway Bay Station", "lat": 22.2766, "lng": 114.1899},
    "fortress_hill": {"name": "Fortress Hill Station", "lat": 22.2798, "lng": 114.1998},
    "north_point": {"name": "North Point Station", "lat": 22.2923, "lng": 114.2106},
    "quarry_bay": {"name": "Quarry Bay Station", "lat": 22.3036, "lng": 114.2181},
    "tai_koo": {"name": "Tai Koo Station", "lat": 22.3127, "lng": 114.2234},
    "sai_wan_ho": {"name": "Sai Wan Ho Station", "lat": 22.3214, "lng": 114.2305},
    "shau_kei_wan": {"name": "Shau Kei Wan Station", "lat": 22.2839, "lng": 114.2302},
    "jordan": {"name": "Jordan Station", "lat": 22.3047, "lng": 114.1719},
    "yau_ma_tei": {"name": "Yau Ma Tei Station", "lat": 22.3135, "lng": 114.1702},
    "mong_kok": {"name": "Mong Kok Station", "lat": 22.3193, "lng": 114.1694},
    "prince_edward": {"name": "Prince Edward Station", "lat": 22.3243, "lng": 114.1687},
    "sham_shui_po": {"name": "Sham Shui Po Station", "lat": 22.3307, "lng": 114.1621},
    "ho_man_tin": {"name": "Ho Man Tin Station", "lat": 22.3095, "lng": 114.1796},
    "whampoa": {"name": "Whampoa Station", "lat": 22.3052, "lng": 114.1822},
    "hung_hom": {"name": "Hung Hom Station", "lat": 22.3025, "lng": 114.1815},
    "tsim_sha_tsui": {"name": "Tsim Sha Tsui Station", "lat": 22.2976, "lng": 114.1722},
    "austin": {"name": "Austin Station", "lat": 22.3044, "lng": 114.1707},
}

# In-memory cache for source data and spatial index
_cache: Dict[str, Any] = {
    "fetched": False,
    "points": [],  # list of normalized points
    "grid": {},
    "cell_size_deg": 0.005,  # approx 500m at equator
}


def _data_dir() -> str:
    """Resolve backend/data directory relative to project root."""
    here = os.path.dirname(__file__)
    root = os.path.abspath(os.path.join(here, os.pardir, os.pardir))
    data_dir = os.path.join(root, "backend", "data")
    if not os.path.isdir(data_dir):
        # Fallback if running from backend package location
        data_dir = os.path.join(os.path.dirname(here), "data")
    return data_dir


def _mtr_json_path() -> str:
    return os.path.join(_data_dir(), "mtr_stations.json")


def _normalize_bus(item: Dict[str, Any]) -> Dict[str, Any]:
    lat = item.get("lat")
    lng = item.get("long") or item.get("lng") or item.get("lon")
    if lat is None or lng is None:
        return None
    return {
        "name": item.get("name_en" ) or item.get("name" ) or item.get("name_tc" , ""),
        "type": "Bus Stop",
        "lat": float(lat),
        "lng": float(lng),
    }


def _normalize_minibus(route_item: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for stop in route_item.get("stops", []):
        lat = stop.get("lat")
        lng = stop.get("lng")
        if lat is None or lng is None:
            continue
        out.append({
            "name": stop.get("name_en" , stop.get("name") ),
            "type": "Minibus",
            "lat": float(lat),
            "lng": float(lng),
        })
    return out


def _normalize_ferry(item: Dict[str, Any]) -> Dict[str, Any]:
    lat = item.get("lat")
    lng = item.get("lng")
    if lat is None or lng is None:
        return None
    return {
        "name": item.get("name_en") or item.get("name"),
        "type": "Ferry Pier",
        "lat": float(lat),
        "lng": float(lng),
    }


def _normalize_taxi(feature: Dict[str, Any]) -> Dict[str, Any]:
    props = feature.get("properties", {})
    coords = feature.get("geometry", {}).get("coordinates", [None, None])
    lng, lat = coords if len(coords) >= 2 else (None, None)
    if lat is None or lng is None:
        return None
    return {
        "name": props.get("stand_name_en") or props.get("stand_name") or props.get("standname"),
        "type": "Taxi Stand",
        "lat": float(lat),
        "lng": float(lng),
    }


def _normalize_mtr(code: str, station: Dict[str, Any]) -> Dict[str, Any]:
    lat = station.get("lat")
    lng = station.get("lng")
    if lat is None or lng is None:
        return None
    return {
        "name": station.get("name_en") or station.get("name"),
        "type": "MTR",
        "lat": float(lat),
        "lng": float(lng),
    }


async def _fetch_all_sources() -> List[Dict[str, Any]]:
    points: List[Dict[str, Any]] = []

    # BUS - fetch from API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(BUS_URL)
            if res.status_code == 200:
                data = res.json()
                for b in data.get("data", []):
                    try:
                        normalized = _normalize_bus(b)
                        if normalized:
                            points.append(normalized)
                    except Exception:
                        continue
    except Exception as e:
        print(f"BUS fetch error: {e}")

    # MINIBUS - use hardcoded samples
    for item in SAMPLE_MINIBUS:
        points.append({
            "name": item["name"],
            "type": "Minibus",
            "lat": item["lat"],
            "lng": item["lng"],
        })

    # FERRY - use hardcoded samples
    for item in SAMPLE_FERRY:
        points.append({
            "name": item["name"],
            "type": "Ferry Pier",
            "lat": item["lat"],
            "lng": item["lng"],
        })

    # TAXI - use hardcoded samples
    for item in SAMPLE_TAXI:
        points.append({
            "name": item["name"],
            "type": "Taxi Stand",
            "lat": item["lat"],
            "lng": item["lng"],
        })

    # MTR - load via cache/API with fallback
    try:
        mtr_points = await load_mtr_stations()
        points.extend(mtr_points)
    except Exception as e:
        print(f"MTR load error: {e}; using hardcoded fallback")
        for station_data in MTR_STATIONS.values():
            points.append({
                "name": station_data["name"],
                "type": "MTR",
                "lat": station_data["lat"],
                "lng": station_data["lng"],
            })

    # Deduplicate by lat/lng+name (simple)
    seen = set()
    dedup = []
    for p in points:
        key = (round(p.get("lat", 0), 6), round(p.get("lng", 0), 6), str(p.get("name", "")))
        if key in seen:
            continue
        seen.add(key)
        dedup.append(p)

    return dedup


def _grid_key(lat: float, lng: float, cell_size_deg: float) -> Tuple[int, int]:
    ix = int(math.floor(lat / cell_size_deg))
    iy = int(math.floor(lng / cell_size_deg))
    return ix, iy


def _build_grid(points: List[Dict[str, Any]], cell_size_deg: float) -> Dict[Tuple[int, int], List[Dict[str, Any]]]:
    grid: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
    for p in points:
        key = _grid_key(p["lat"], p["lng"], cell_size_deg)
        grid.setdefault(key, []).append(p)
    return grid


def _bbox_keys(lat: float, lng: float, radius_m: float, cell_size_deg: float) -> List[Tuple[int, int]]:
    # Convert meters to degrees approximately
    lat_deg = radius_m / 111320.0
    lng_deg = radius_m / (111320.0 * max(math.cos(math.radians(lat)), 0.0001))
    min_lat = lat - lat_deg
    max_lat = lat + lat_deg
    min_lng = lng - lng_deg
    max_lng = lng + lng_deg

    ix_min = int(math.floor(min_lat / cell_size_deg))
    ix_max = int(math.floor(max_lat / cell_size_deg))
    iy_min = int(math.floor(min_lng / cell_size_deg))
    iy_max = int(math.floor(max_lng / cell_size_deg))

    keys = []
    for ix in range(ix_min, ix_max + 1):
        for iy in range(iy_min, iy_max + 1):
            keys.append((ix, iy))
    return keys


async def ensure_cache():
    if _cache["fetched"]:
        return
    points = await _fetch_all_sources()
    _cache["points"] = points
    cell_size = _cache.get("cell_size_deg", 0.005)
    _cache["grid"] = _build_grid(points, cell_size)
    _cache["fetched"] = True


def _distance_m(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return geodesic(a, b).meters


async def query_nearby(lat: float, lng: float, radius_m: float = 800, types: List[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    # Cache should already be preloaded at startup, just use it
    if not _cache.get("fetched"):
        await ensure_cache()
    
    points = _cache.get("points", [])
    grid = _cache.get("grid", {})
    cell_size = _cache.get("cell_size_deg", 0.005)

    candidate_keys = _bbox_keys(lat, lng, radius_m, cell_size)
    candidates = []
    for k in candidate_keys:
        for p in grid.get(k, []):
            if types and p.get("type") not in types and (p.get("type") or "").lower() not in [t.lower() for t in types]:
                continue
            try:
                d = _distance_m((lat, lng), (p["lat"], p["lng"]))
            except Exception:
                continue
            if d <= radius_m:
                item = p.copy()
                item["distance"] = round(d)
                item["walk_min"] = round(d / 70)
                candidates.append(item)

    # sort by distance and return top `limit`
    candidates.sort(key=lambda x: x["distance"])
    return candidates[:limit]


async def load_mtr_stations(stale_days: int = 14) -> List[Dict[str, Any]]:
    """
    Safe loader for MTR stations:
    - Prefer local JSON cache (backend/data/mtr_stations.json)
    - If cache missing or stale, fetch from official API and refresh cache
    - Fallback to hardcoded sample if both fail
    Returns normalized points with name/type/lat/lng
    """
    path = _mtr_json_path()

    # Try local cache first
    cache_ok = False
    stations: List[Dict[str, Any]] = []
    try:
        if os.path.isfile(path):
            mtime = os.path.getmtime(path)
            age_days = (time.time() - mtime) / 86400.0
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict) and "stations" in raw:
                stations = raw.get("stations", [])
            elif isinstance(raw, list):
                stations = raw
            if stations and age_days <= stale_days:
                cache_ok = True
    except Exception as e:
        print(f"MTR cache read error: {e}")

    if cache_ok:
        points: List[Dict[str, Any]] = []
        for s in stations:
            try:
                name = s.get("name_en") or s.get("name")
                lat = s.get("lat")
                lng = s.get("lng")
                if lat is None or lng is None:
                    continue
                points.append({
                    "name": name,
                    "type": "MTR",
                    "lat": float(lat),
                    "lng": float(lng),
                })
            except Exception:
                continue
        return points

    # Fetch from API if cache missing or stale
    fetched_points: List[Dict[str, Any]] = []
    fetch_error: Exception | None = None
    try:
        async with httpx.AsyncClient(timeout=15.0, headers={
            "User-Agent": "HK Smart Transport/1.0 (+https://github.com/mirzausamaikram/hk-smart-transport)",
            "Accept": "application/json"
        }) as client:
            res = await client.get(MTR_URL)
            if res.status_code == 200:
                data = res.json()
                mtr_data = data.get("data", {})
                for code, station_info in mtr_data.items():
                    normalized = _normalize_mtr(code, station_info)
                    if normalized:
                        fetched_points.append(normalized)
            else:
                fetch_error = Exception(f"HTTP {res.status_code}")
    except Exception as e:
        fetch_error = e

    if fetched_points:
        try:
            os.makedirs(_data_dir(), exist_ok=True)
            to_store = {
                "updated_at": int(time.time()),
                "stations": [{
                    "name_en": p.get("name"),
                    "lat": p.get("lat"),
                    "lng": p.get("lng")
                } for p in fetched_points]
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(to_store, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"MTR cache write error: {e}")
        return fetched_points

    # If fetch failed but cache had data (stale), return normalized stale cache
    if stations:
        points: List[Dict[str, Any]] = []
        for s in stations:
            try:
                name = s.get("name_en") or s.get("name")
                lat = s.get("lat")
                lng = s.get("lng")
                if lat is None or lng is None:
                    continue
                points.append({
                    "name": name,
                    "type": "MTR",
                    "lat": float(lat),
                    "lng": float(lng),
                })
            except Exception:
                continue
        print("MTR API unavailable; using stale cache")
        return points

    # Final fallback: hardcoded small set
    print(f"MTR API/cache unavailable; using hardcoded fallback ({fetch_error})")
    fallback: List[Dict[str, Any]] = []
    for station_data in MTR_STATIONS.values():
        fallback.append({
            "name": station_data["name"],
            "type": "MTR",
            "lat": station_data["lat"],
            "lng": station_data["lng"],
        })
    return fallback
