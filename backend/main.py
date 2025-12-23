from fastapi import FastAPI
from routers import itinerary_ai 
from fastapi.middleware.cors import CORSMiddleware


from routers import (
    geocode,
    bus_routes,
    citybus,
    itinerary,
    itinerary_ai,
    mtr_geo,
    route_planner,
    stations,
    nearby,
    pois
)

app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(geocode, prefix="/api/geocode")
app.include_router(route_planner, prefix="/api/route")
app.include_router(stations, prefix="/api/stations")
app.include_router(itinerary, prefix="/api/itinerary")
app.include_router(bus_routes, prefix="/api/bus")
app.include_router(citybus, prefix="/api/citybus")
app.include_router(mtr_geo, prefix="/api/mtr-geo")
app.include_router(nearby, prefix="/api/nearby")
app.include_router(pois.router, prefix="/api/pois")
app.include_router(itinerary_ai, prefix="/api/itinerary")


@app.get("/")
def root():
    return {"message": "HK Smart Transport API Running"}
