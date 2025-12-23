import httpx
import json

print("Querying OpenStreetMap for all MTR stations in Hong Kong...")


overpass_query = """
[bbox:22.2,114.0,22.6,114.3];
(
  node["station"="subway"]["name:en"](22.2,114.0,22.6,114.3);
  way["station"="subway"]["name:en"](22.2,114.0,22.6,114.3);
  relation["station"="subway"]["name:en"](22.2,114.0,22.6,114.3);
);
out geom;
"""

try:
    url = "https://overpass-api.de/api/interpreter"
    response = httpx.post(url, data=overpass_query, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data.get('elements', []))} elements")
        
        stations = {}
        for element in data.get('elements', []):
            if element.get('type') == 'node' and 'lat' in element and 'lon' in element:
                name = element.get('tags', {}).get('name:en')
                if name:
                    stations[name] = {
                        "lat": element['lat'],
                        "lng": element['lon'],
                        "type": "MTR"
                    }
        
        print(f"\n✓ Found {len(stations)} MTR stations with coordinates\n")
        
        # Sort and print
        for name in sorted(stations.keys())[:30]:
            s = stations[name]
            print(f'    "{name}": {{"lat": {s["lat"]:.4f}, "lng": {s["lng"]:.4f}}},')
        
        if len(stations) > 30:
            print(f"    ... and {len(stations) - 30} more")
    else:
        print(f"Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"Error: {e}")
