import asyncio
from collections import Counter
from routers.nearby_utils import ensure_cache, query_nearby, _cache

async def test():
    await ensure_cache()
    
    print("Cache contents:")
    print(f"Total points: {len(_cache['points'])}")
    
    types = Counter([p['type'] for p in _cache['points']])
    print("\nPoints by type in cache:")
    for t, count in types.items():
        print(f"  {t}: {count}")
    

    ferry_points = [p for p in _cache['points'] if p['type'] == 'Ferry Pier']
    print(f"\nFerry Piers in cache: {len(ferry_points)}")
    for fp in ferry_points:
        print(f"  - {fp.get('name', '?')} at ({fp['lat']}, {fp['lng']})")
    

    print("\n\nQuerying Ferry Pier within 2000m:")
    results = await query_nearby(22.3117, 114.1768, 2000, types=['Ferry Pier'], limit=100)
    print(f"Results found: {len(results)}")
    for r in results:
        print(f"  - {r['name']}")

asyncio.run(test())
