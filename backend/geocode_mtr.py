import httpx
import csv
from io import StringIO
import asyncio
import time

print("Fetching all MTR stations and geocoding them...")


mtr_resp = httpx.get('https://opendata.mtr.com.hk/data/mtr_lines_and_stations.csv', timeout=10)
mtr_reader = csv.DictReader(StringIO(mtr_resp.text))

stations_dict = {}
for row in mtr_reader:
    code = row.get('Station Code', '').strip()
    name = row.get('English Name', '').strip()
    if code and name and code not in stations_dict:
        stations_dict[code] = name

print(f"Total unique MTR stations: {len(stations_dict)}")
print(f"Sample: {list(stations_dict.items())[:5]}")


print("\n\nGeocoding stations (this will take a while)...")
geocoded = {}

for code, name in list(stations_dict.items())[:20]:
    try:

        search_query = f"{name} MTR Station, Hong Kong"
        url = f"https://nominatim.openstreetmap.org/search?q={search_query}&format=json&limit=1"
        
        r = httpx.get(url, timeout=5, headers={'User-Agent': 'HK-Transport-App'})
        if r.status_code == 200:
            results = r.json()
            if results:
                result = results[0]
                geocoded[code] = {
                    "name": name,
                    "lat": float(result['lat']),
                    "lng": float(result['lon']),
                    "type": "MTR"
                }
                print(f"✓ {code}: {name:25} -> ({geocoded[code]['lat']:.4f}, {geocoded[code]['lng']:.4f})")
                time.sleep(1)
            else:
                print(f"✗ {code}: {name:25} -> No results")
        else:
            print(f"✗ {code}: {name:25} -> Error {r.status_code}")
    except Exception as e:
        print(f"✗ {code}: {name:25} -> {e}")

print(f"\n\nGeocoded {len(geocoded)} stations")
print("\nPython dict format for backend:")
print("MTR_STATIONS = {")
for code, data in geocoded.items():
    print(f'    "{code.lower()}": {{"name": "{data["name"]}", "lat": {data["lat"]}, "lng": {data["lng"]}}},')
print("}")
