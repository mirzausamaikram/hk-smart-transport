import asyncio
import math
from typing import List, Dict, Any, Tuple
import httpx
from geopy.distance import geodesic


BUS_URL = "https://data.etabus.gov.hk/v1/transport/kmb/stop"
MINIBUS_URL = "https://static.data.gov.hk/transport/minibus.json"
FERRY_URL = "https://static.data.gov.hk/td/ferry.json"
TAXI_URL = "https://static.data.gov.hk/transport/taxi_stands.json"
MTR_URL = "https://rt.data.gov.hk/v1/transport/mtr/station_lat_lng.json"


_cache: Dict[str, Any] = {
    "fetched": False,
    "points": [],
    "grid": {},
    "cell_size_deg": 0.005,
}


def _normalize_bus(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": item.get("name_en" ) or item.get("name" ) or item.get("name_tc" , ""),
        "type": "Bus Stop",
        "lat": float(item.get("lat")),
        "lng": float(item.get("long") or item.get("lng") or item.get("lon")),
    }


def _normalize_minibus(route_item: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for stop in route_item.get("stops", []):
        out.append({
            "name": stop.get("name_en" , stop.get("name") ),
            "type": "Minibus",
            "lat": float(stop.get("lat")),
            "lng": float(stop.get("lng")),
        })
    return out


def _normalize_ferry(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": item.get("name_en") or item.get("name"),
        "type": "Ferry Pier",
        "lat": float(item.get("lat")),
        "lng": float(item.get("lng")),
    }


def _normalize_taxi(feature: Dict[str, Any]) -> Dict[str, Any]:
    props = feature.get("properties", {})
    coords = feature.get("geometry", {}).get("coordinates", [None, None])
    lng, lat = coords if len(coords) >= 2 else (None, None)
    return {
        "name": props.get("stand_name_en") or props.get("stand_name") or props.get("standname"),
        "type": "Taxi Stand",
        "lat": float(lat),
        "lng": float(lng),
    }


def _normalize_mtr(code: str, station: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": station.get("name_en") or station.get("name"),
        "type": "MTR",
        "lat": float(station.get("lat")),
        "lng": float(station.get("lng")),
    }


async def _fetch_all_sources() -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [
            client.get(BUS_URL),
            client.get(MINIBUS_URL),
            client.get(FERRY_URL),
            client.get(TAXI_URL),
            client.get(MTR_URL),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    points: List[Dict[str, Any]] = []


    try:
        res = results[0]
        if not isinstance(res, Exception):
            data = res.json()
            for b in data.get("data", []):
                try:
                    points.append(_normalize_bus(b))
                except Exception:
                    continue
    except Exception:
        pass


    try:
        res = results[1]
        if not isinstance(res, Exception):
            data = res.json()
            for route in data.get("data", {}).get("routes", []):
                try:
                    points.extend(_normalize_minibus(route))
                except Exception:
                    continue
    except Exception:
        pass


    try:
        res = results[2]
        if not isinstance(res, Exception):
            data = res.json()
            for f in data:
                try:
                    points.append(_normalize_ferry(f))
                except Exception:
                    continue
    except Exception:
        pass


    try:
        res = results[3]
        if not isinstance(res, Exception):
            data = res.json()
            for feat in data.get("features", []):
                try:
                    points.append(_normalize_taxi(feat))
                except Exception:
                    continue
    except Exception:
        pass


    try:
        res = results[4]
        if not isinstance(res, Exception):
            data = res.json()
            for code, station in data.get("data", {}).items():
                try:
                    points.append(_normalize_mtr(code, station))
                except Exception:
                    continue
    except Exception:
        pass


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
    await ensure_cache()
    points = _cache["points"]
    grid = _cache["grid"]
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


    candidates.sort(key=lambda x: x["distance"])
    return candidates[:limit]
