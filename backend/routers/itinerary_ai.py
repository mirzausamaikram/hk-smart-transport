from fastapi import APIRouter
from pydantic import BaseModel
import requests
from datetime import datetime, timedelta
import os
import json
from typing import List, Optional, Tuple
import math

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL = os.getenv("HUGGINGFACE_MODEL", "gpt2")

POIS: List[dict] = []
try:
    pois_path = os.path.join(os.path.dirname(__file__), "..", "data", "pois.json")
    with open(os.path.normpath(pois_path), "r", encoding="utf-8") as f:
        POIS = json.load(f)
except Exception:
    POIS = []


class AIRequest(BaseModel):
    start_place: str
    end_place: str
    transport: str = "MTR"
    preference: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    budget: Optional[float] = None
    interests: Optional[List[str]] = None
    num_options: Optional[int] = 1


def build_system_prompt() -> str:
    return (
        "You are a professional full-time traveller who knows Hong Kong like a local. "
        "Give a concise, realistic 1-day itinerary (8 hours) that starts at the first location "
        "and ends at the second location. Include:\n"
        "- Exact times (e.g., 09:00-09:30)\n"
        "- Transport method (MTR, bus, tram, ferry, walk, taxi)\n"
        "- Short beautiful descriptions\n"
        "- Estimated cost in HKD\n"
        "- Lunch & coffee suggestions\n"
        "Respond in Markdown with headings and bold text."
    )


def haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    lat1, lon1 = a
    lat2, lon2 = b
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(x))


def pick_pois_for_interests(interests: Optional[List[str]], origin: Optional[Tuple[float, float]] = None, max_pois: int = 3) -> List[dict]:
    """Select nearest POIs that match interests, fallback to nearest sightseeing POIs."""
    if not POIS:
        return []

    candidates: List[Tuple[float, dict]] = []
    for poi in POIS:
        poi_type = poi.get("type", "").lower()
        match = False
        if interests:
            for intr in interests:
                if intr.lower() in poi_type or poi_type in intr.lower():
                    match = True
                    break
        # compute distance (large number if origin not available)
        if origin:
            poi_coord = (poi.get("lat"), poi.get("lng"))
            try:
                dist_km = haversine_km(origin, (float(poi_coord[0]), float(poi_coord[1])))
            except Exception:
                dist_km = 9999.0
        else:
            dist_km = 9999.0


        score = dist_km - (5.0 if match else 0.0)
        candidates.append((score, poi))

    candidates.sort(key=lambda x: x[0])

    picks = [c[1] for c in candidates[:max_pois]]

    if len(picks) < max_pois and origin:
        sightseeing = [p for p in POIS if p.get("type") == "sightseeing" and p not in picks]
        sightseeing.sort(key=lambda p: haversine_km(origin, (float(p.get("lat")), float(p.get("lng")))))
        for p in sightseeing:
            picks.append(p)
            if len(picks) >= max_pois:
                break

    return picks


def fallback_itinerary(start: str, end: str, transport: str, interests: Optional[List[str]] = None, budget: Optional[float] = None, pois: Optional[List[dict]] = None, time: Optional[str] = None) -> str:
    """Create a simple deterministic itinerary enriched with local POIs."""
    if time:
        try:
            time_parts = time.split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            start_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        except Exception:
            start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    else:
        start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    slots = [60, 90, 60, 120, 90]

    origin = None
    try:
        origin = geocode_place(start)
    except Exception:
        origin = None

    if pois is None:
        desired = max(3, (len(interests) * 2) if interests else 3)
        pois = pick_pois_for_interests(interests, origin=origin, max_pois=desired)
    poi_texts = [f"Visit **{p['name']}** — {p.get('description','')}" for p in pois]

    activities = [
        f"Arrive at **{start}** and have a local breakfast (dim sum or congee).",
        poi_texts[0] if len(poi_texts) > 0 else "Explore nearby attractions and neighborhoods on foot; take photos and enjoy local markets.",
        "Lunch at a recommended mid-range restaurant; try local specialties.",
        poi_texts[1] if len(poi_texts) > 1 else "Visit a highlight attraction or museum; enjoy panoramic views if available.",
        f"Head towards **{end}**, using {transport} where appropriate, and finish the day at the destination."
    ]

    lines = []
    current = start_time
    total_cost = 0
    for dur, act in zip(slots, activities):
        end_slot = current + timedelta(minutes=dur)
        lines.append(f"**{current.strftime('%H:%M')} - {end_slot.strftime('%H:%M')}** — {act}")
        lines.append("")
        current = end_slot

    food_est = 150
    poi_costs = sum([p.get('avg_cost_hkd', 0) for p in (pois or [])])
    total_cost = food_est + poi_costs
    if budget and total_cost > budget:
        cost_note = f"Estimated cost: ~HKD {total_cost} (this exceeds your budget of HKD {budget})"
    else:
        cost_note = f"Estimated cost: ~HKD {total_cost}"

    lines.append(f"**{cost_note}**")
    lines.append("")
    lines.append("**Transport tips:** Use Octopus card for convenience; prefer MTR for longer hops.")

    if pois:
        lines.append("")
        lines.append("**Recommended stops:**")
        for p in pois:
            lines.append(f"- {p['name']}: {p.get('description','')} (avg. HKD {p.get('avg_cost_hkd', 'N/A')})")

    return "\n".join(lines)


def call_huggingface(prompt: str) -> Optional[str]:
    if not HF_API_KEY:
        return None
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=45)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return data[0]["generated_text"]
        if isinstance(data, dict) and data.get("generated_text"):
            return data.get("generated_text")
    except Exception:
        return None
    return None

def geocode_place(place: str) -> Optional[Tuple[float, float]]:
    """Geocode with Nominatim (OpenStreetMap). Returns (lat, lng) or None."""
    try:
        params = {"format": "json", "q": f"{place}, Hong Kong", "limit": 1}
        r = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers={"User-Agent": "HK-Smart-Transport/1.0"}, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data and isinstance(data, list) and len(data) > 0:
            lat = float(data[0].get("lat"))
            lon = float(data[0].get("lon"))
            return (lat, lon)
    except Exception:
        return None
    return None


@router.post("/ai")
def generate_ai_itinerary(req: AIRequest):
    system_prompt = build_system_prompt()
    user_prompt = (
        f"Plan a 1-day Hong Kong itinerary starting at **{req.start_place.strip()}** "
        f"and ending at **{req.end_place.strip()}**. Preferred transport: {req.transport}. "
    )
    if req.preference:
        user_prompt += f"Preference: {req.preference}. "
    if req.date:
        user_prompt += f"Date: {req.date}. "
    if req.time:
        user_prompt += f"Start time: {req.time}. "
    if req.budget:
        user_prompt += f"Budget: HKD {req.budget}. "
    if req.interests:
        user_prompt += f"Interests: {', '.join(req.interests)}. "

    user_prompt += f"Today is {datetime.now().strftime('%Y-%m-%d')}."

    origin = geocode_place(req.start_place) if req.start_place else None
    desired = max(3, (len(req.interests) * 2) if req.interests else 3)
    selected_pois = pick_pois_for_interests(req.interests, origin=origin, max_pois=desired)

    if OPENAI_API_KEY:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1200,
        }
        try:
            resp = requests.post(OPENAI_ENDPOINT, json=payload, headers=headers, timeout=45)
            resp.raise_for_status()
            data = resp.json()
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0].get("message", {}).get("content") or data["choices"][0].get("text")
                if content:
                    return {"itinerary": content, "pois": selected_pois}
            return {"error": "No content returned from LLM", "pois": selected_pois}
        except Exception as e:
            hf_text = call_huggingface(system_prompt + "\n" + user_prompt)
            if hf_text:
                return {"itinerary": hf_text, "pois": selected_pois}
            return {"error": f"LLM request failed: {str(e)}", "itinerary": fallback_itinerary(req.start_place, req.end_place, req.transport, req.interests, req.budget, pois=selected_pois, time=req.time), "pois": selected_pois}

    if HF_API_KEY:
        hf_text = call_huggingface(system_prompt + "\n" + user_prompt)
        if hf_text:
            return {"itinerary": hf_text, "pois": selected_pois}

    itinerary = fallback_itinerary(req.start_place, req.end_place, req.transport, req.interests, req.budget, pois=selected_pois, time=req.time)
    return {"itinerary": itinerary, "pois": selected_pois}


class SummaryRequest(BaseModel):
    stops: list[dict]


@router.post("/summary")
def ai_summary(req: SummaryRequest):
    stops = req.stops or []
    if len(stops) == 0:
        return {"summary": "No stops provided."}

    start_name = stops[0].get('title') or f"{stops[0].get('lat')},{stops[0].get('lng')}"
    end_name = stops[-1].get('title') or f"{stops[-1].get('lat')},{stops[-1].get('lng')}"

    text = fallback_itinerary(start_name, end_name, transport="MTR", interests=None, budget=None)
    lines = [l for l in text.splitlines() if l.strip()]
    summary = "\n".join(lines[:6])
    return {"summary": summary}
