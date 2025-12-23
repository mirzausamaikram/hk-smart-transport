import httpx
import csv
from io import StringIO
import json

print("=" * 60)
print("Fetching MTR and Bus data from HK Open Data APIs")
print("=" * 60)


print("\n1. Fetching MTR stations with coordinates...")
try:
    mtr_resp = httpx.get('https://opendata.mtr.com.hk/data/mtr_lines_and_stations.csv', timeout=10)
    mtr_lines = mtr_resp.text.strip().split('\n')
    mtr_reader = csv.DictReader(StringIO(mtr_resp.text))
    

    stations = {}
    for row in mtr_reader:
        code = row.get('Station Code', '')
        name = row.get('English Name', '')
        if code and code not in stations:
            stations[code] = name
    
    print(f"✓ Found {len(stations)} unique MTR stations")
    print(f"  Sample: {list(stations.items())[:3]}")
except Exception as e:
    print(f"✗ Error fetching MTR: {e}")


print("\n2. Looking for MTR station coordinates...")
urls_to_try = [
    'https://opendata.mtr.com.hk/data/mtr_station_geometry.geojson',
    'https://opendata.mtr.com.hk/data/mtr_stations.geojson',
    'https://opendata.mtr.com.hk/data/stations.geojson',
]

found_coords = False
for url in urls_to_try:
    try:
        resp = httpx.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ Found at: {url}")
            print(f"  Type: {data.get('type', 'unknown')}")
            if data.get('type') == 'FeatureCollection':
                print(f"  Features: {len(data.get('features', []))}")
            found_coords = True
            break
    except:
        pass

if not found_coords:
    print("✗ Could not find MTR coordinate files")


print("\n3. Fetching Bus stop data...")
try:
    bus_resp = httpx.get('https://data.etabus.gov.hk/v1/transport/kmb/stop', timeout=10)
    if bus_resp.status_code == 200:
        bus_data = bus_resp.json()
        print(f"✓ Found bus data")
        print(f"  Status: {bus_data.get('status')}")
        if 'data' in bus_data:
            print(f"  Stops: {len(bus_data['data'])}")
except Exception as e:
    print(f"✗ Error fetching bus: {e}")

print("\n" + "=" * 60)
print("Summary: Check the logs above to see what's available")
print("=" * 60)
