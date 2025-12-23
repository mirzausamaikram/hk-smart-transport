from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ItineraryRequest(BaseModel):
    places: list[str]

@router.post("/generate")
def generate(req: ItineraryRequest):
    steps = []
    for i, p in enumerate(req.places):
        if i == 0:
            steps.append(f"Start at {p}.")
        else:
            steps.append(f"Then travel to {p}.")
    steps.append("Itinerary complete.")
    return {"steps": steps}