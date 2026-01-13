from fastapi import APIRouter, Query
from typing import List, Optional
from .nearby_utils import query_nearby

router = APIRouter(tags=["nearby"])


@router.get("/")
async def get_nearby(lat: float = Query(...), lng: float = Query(...), radius: int = Query(800), types: Optional[List[str]] = Query(None), limit: int = Query(50)):
    """Return nearby transport stops and POIs. Supports optional `types` filter (repeatable), `radius` in meters, and `limit`."""
    try:
        # types can be provided multiple times: ?types=Bus Stop&types=MTR
        # query_nearby expects list of types or None
        results = await query_nearby(lat, lng, radius_m=radius, types=types, limit=limit)
        return {"results": results}
    except Exception as e:
        return {"results": [], "error": str(e)}
