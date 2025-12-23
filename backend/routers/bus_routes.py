from fastapi import APIRouter
import httpx

router = APIRouter()

@router.get("/shape/{route}")
async def get_bus_route(route: str):
    url = f"https://data.etabus.gov.hk/gtfs/route_shape/{route}.json"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
    data = r.json()

    shape = [{"lat": p["shape_pt_lat"], "lng": p["shape_pt_lon"]} for p in data]
    return {"polyline": shape}