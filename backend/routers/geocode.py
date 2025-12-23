from fastapi import APIRouter, Query
import requests

router = APIRouter()

@router.get("/search")
def geocode_search(q: str = Query(...)):
    """Simple Nominatim geocoder"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": q,
            "format": "json",
            "limit": 5,
            "addressdetails": 1
        }

        res = requests.get(url, params=params, headers={
            "User-Agent": "HK-Smart-Transport-FYP"
        })

        data = res.json()

        results = [
            {
                "name": x.get("display_name"),
                "lat": float(x["lat"]),
                "lng": float(x["lon"])
            }
            for x in data
        ]

        return {"results": results}

    except Exception as e:
        return {"error": str(e)}
