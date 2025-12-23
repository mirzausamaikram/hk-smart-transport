import json
import urllib.request

BASE = 'http://127.0.0.1:8000'

def post(path, payload):
    url = BASE + path
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode()

if __name__ == '__main__':
    try:
        print('POST /api/itinerary/summary')
        r = post('/api/itinerary/summary', {'stops':[{'lat':22.3027,'lng':114.1772,'title':'Start'},{'lat':22.3193,'lng':114.1694,'title':'End'}]})
        print(r)
    except Exception as e:
        print('Summary error:', e)

    try:
        print('\nPOST /api/route/alternatives')
        r2 = post('/api/route/alternatives', {'points':[{'lat':22.3027,'lng':114.1772},{'lat':22.3193,'lng':114.1694}]})
        print(r2)
    except Exception as e:
        print('Alternatives error:', e)
