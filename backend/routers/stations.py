from fastapi import APIRouter
import httpx

router = APIRouter()


# ---------------------------
# 1. Get ALL KMB Bus Stops
# ---------------------------
@router.get("/bus-stops")
async def bus_stops():
    url = "https://data.etabus.gov.hk/v1/transport/kmb/stop"
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    data = res.json()

    stops = [
        {
            "stop_id": item["stop"],
            "name_en": item["name_en"],
            "lat": float(item["lat"]),
            "lng": float(item["long"])
        }
        for item in data["data"]
    ]

    return {"stops": stops}


# ---------------------------
# 2. Get ETA for a stop
# ---------------------------
@router.get("/eta/{stop_id}")
async def bus_eta(stop_id: str):
    url = f"https://data.etabus.gov.hk/v1/transport/kmb/eta/{stop_id}/"
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    data = res.json()

    eta_list = []
    for item in data["data"]:
        if item["eta"]:
            eta_list.append({
                "route": item["route"],
                "dest": item["dest_en"],
                "eta": item["eta"]
            })

    return {"eta": eta_list}
