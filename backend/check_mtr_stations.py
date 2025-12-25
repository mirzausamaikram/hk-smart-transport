import asyncio
import httpx

async def check_mtr_data():
    MTR_URL = "https://rt.data.gov.hk/v1/transport/mtr/station_lat_lng.json"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(MTR_URL)
        data = response.json()
        
        print(f"Total MTR stations in API: {len(data.get('data', {}))}")
        print("\nAll station names:")
        print("=" * 60)
        
        stations = []
        for code, station in data.get("data", {}).items():
            name = station.get("name_en") or station.get("name")
            lat = station.get("lat")
            lng = station.get("lng")
            stations.append((code, name, lat, lng))
        
        # Sort by name
        stations.sort(key=lambda x: x[1])
        
        for code, name, lat, lng in stations:
            print(f"{code:6} | {name:40} | ({lat}, {lng})")
        
        # Check for Tsing Yi specifically
        print("\n" + "=" * 60)
        print("Searching for 'Tsing Yi':")
        for code, name, lat, lng in stations:
            if 'tsing' in name.lower() or 'yi' in name.lower():
                print(f"  Found: {code} | {name}")

if __name__ == "__main__":
    asyncio.run(check_mtr_data())
