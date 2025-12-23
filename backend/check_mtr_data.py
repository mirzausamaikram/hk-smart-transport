import httpx
import csv
from io import StringIO

print("Checking MTR CSV columns and sampling data...")
mtr_resp = httpx.get('https://opendata.mtr.com.hk/data/mtr_lines_and_stations.csv', timeout=10)
mtr_reader = csv.DictReader(StringIO(mtr_resp.text))

print(f"CSV Columns: {list(mtr_reader.fieldnames)}")

seen_codes = set()
print("\nSample MTR stations (first 5):")
for i, row in enumerate(mtr_resp.text.split('\n')[:6]):
    try:

        cleaned = row.replace('\ufeff', '').encode('utf-8', errors='replace').decode('utf-8')
        print(cleaned[:80])
    except:
        print(f"  [Row {i}]")


print("\n\nTrying different geometry file names...")
urls = [
    'https://opendata.mtr.com.hk/data/mtr_station_locations.geojson',
    'https://opendata.mtr.com.hk/data/mtr_stations_geometry.geojson',
    'https://opendata.mtr.com.hk/data/nts_mtr_passenger_flow.geojson',
]

for url in urls:
    try:
        r = httpx.get(url, timeout=5)
        if r.status_code == 200:
            print(f"✓ Found: {url}")
    except:
        pass


print("\n\nChecking MTR open data directory...")
try:
    r = httpx.get('https://opendata.mtr.com.hk/data/', timeout=5)
    if r.status_code == 200:

        import re
        files = re.findall(r'href=["\']([^"\']+\.(?:csv|json|geojson))["\']', r.text)
        print(f"Available files: {set(files)}")
except Exception as e:
    print(f"Could not list directory: {e}")
