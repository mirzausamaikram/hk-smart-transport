from fastapi import APIRouter, Query
import os
import json
from typing import List
from geopy.distance import geodesic

router = APIRouter()

DATA_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'pois.json'))

def load_pois():
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


@router.get('/nearby')
def pois_nearby(lat: float = Query(...), lng: float = Query(...), radius: int = Query(800), limit: int = Query(3)):
    """Return nearest POIs from local dataset with opening info if present"""
    pois = load_pois()
    out = []
    try:
        for p in pois:
            try:
                dist = round(geodesic((lat, lng), (float(p.get('lat')), float(p.get('lng')))).meters)
            except Exception:
                continue
            if dist <= radius:
                item = p.copy()
                item['distance'] = dist
                out.append(item)
        out.sort(key=lambda x: x['distance'])
        return {'results': out[:limit]}
    except Exception as e:
        return {'results': [], 'error': str(e)}
