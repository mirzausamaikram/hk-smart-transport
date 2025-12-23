import httpx
import csv
from io import StringIO

print("Fetching Star Ferry timetable data...")

urls = [
    "http://www.starferry.com.hk/sites/default/files/ferry_sf_central_tsimshatsui_timetable_updatedon022018_eng.csv",
    "http://www.starferry.com.hk/sites/default/files/ferry_sf_wanchai_tsimshatsui_timetable_updatedon022018_eng.csv",
]

for url in urls:
    try:
        print(f"\n{'='*60}")
        print(f"Fetching: {url.split('/')[-1]}")
        print('='*60)
        r = httpx.get(url, timeout=10)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            lines = r.text.strip().split('\n')
            print(f"Total lines: {len(lines)}")
            print(f"\nFirst 5 lines:")
            for i, line in enumerate(lines[:5]):
                print(f"  {i}: {line}")
            

            reader = csv.DictReader(StringIO(r.text))
            if reader.fieldnames:
                print(f"\nCSV Columns: {reader.fieldnames}")
                rows = list(reader)
                print(f"Data rows: {len(rows)}")
                if rows:
                    print(f"First row: {rows[0]}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("Analysis complete")
