from fastapi import APIRouter, Query
import httpx

router = APIRouter()

@router.get("/schedule")
async def mtr_schedule(line: str = Query(...), station: str = Query(...)):
    url = f"https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line={line}&sta={station}"

    async with httpx.AsyncClient() as client:
        res = await client.get(url)

    data = res.json()


    return data