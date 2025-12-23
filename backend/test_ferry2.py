import asyncio
from routers.nearby_utils import query_nearby

async def test():

    print("Test 1: Query with types=['Ferry Pier']")
    results = await query_nearby(22.3117, 114.1768, 2000, types=['Ferry Pier'], limit=100)
    print(f"Found: {len(results)}")
    for r in results:
        print(f"  - {r['name']} ({r['type']})")
    

    print("\nTest 2: Query with types=['Hung Hom Ferry Pier'] (exact name)")
    results = await query_nearby(22.3117, 114.1768, 2000, types=['Hung Hom Ferry Pier'], limit=100)
    print(f"Found: {len(results)}")
    

    print("\nTest 3: Query all types and filter locally for Ferry Pier")
    results = await query_nearby(22.3117, 114.1768, 2000, types=None, limit=500)
    ferry = [r for r in results if r['type'] == 'Ferry Pier']
    print(f"Found: {len(ferry)} Ferry Pier entries")
    for r in ferry:
        print(f"  - {r['name']}")

asyncio.run(test())
