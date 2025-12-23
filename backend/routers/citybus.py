from fastapi import APIRouter
import httpx

router = APIRouter()

@router.get("/eta/{company}/{stop_id}/{route}")
async def citybus_eta(company: str, stop_id: str, route: str):
    url = f"https://rt.data.gov.hk/v1/transport/citybus-nwfb/eta/{company}/{stop_id}/{route}"

    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    raw = res.json().get("data", [])

    eta = []
    for e in raw:
        if e["eta"]:
            eta.append({
                "route": e["route"],
                "dest": e["dest_en"],
                "eta": e["eta"]
            })

    return {"eta": eta}