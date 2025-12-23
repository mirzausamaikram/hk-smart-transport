import asyncio
from collections import Counter
from routers.nearby_utils import ensure_cache, query_nearby

async def test():
    await ensure_cache()
    

    print("=" * 60)
    print("Test 1: MTR stations within 2000m")
    print("=" * 60)
    mtr_results = await query_nearby(22.3117, 114.1768, 2000, types=['MTR'], limit=100)
    print(f'MTR stations found: {len(mtr_results)}')
    for mtr in mtr_results:
        print(f'  - {mtr["name"]} ({mtr.get("distance_m", "?")}m)')
    

    print("\n" + "=" * 60)
    print("Test 2: All transport types within 2000m (limit 200)")
    print("=" * 60)
    results = await query_nearby(22.3117, 114.1768, 2000, limit=200)
    print(f'Total results: {len(results)}')
    
    types = Counter([r['type'] for r in results])
    print('\nResults by type:')
    for transport_type, count in types.items():
        print(f'  {transport_type}: {count}')

if __name__ == '__main__':
    asyncio.run(test())
