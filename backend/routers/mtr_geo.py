from fastapi import APIRouter

router = APIRouter()

mtr_stations = [
    {"name": "Hong Kong", "line": "TWL", "lat": 22.2849, "lng": 114.1589, "color": "#ee2e24"},
    {"name": "Central", "line": "TWL", "lat": 22.2820, "lng": 114.1588, "color": "#ee2e24"},
    {"name": "Admiralty", "line": "TWL", "lat": 22.2790, "lng": 114.1640, "color": "#ee2e24"}
]

@router.get("/stations")
def get_mtr_geo():
    return {"stations": mtr_stations}