#!/usr/bin/env python3
"""
Test K-line API endpoints
"""
import requests
import time

def test_kline_api():
    base_url = "http://127.0.0.1:8000/api/quotes"

    # Test 1: Daily K-line
    print("=== Test 1: 000858.SZ Daily ===")
    try:
        response = requests.get(
            f"{base_url}/api/kline/realtime/000858.SZ",
            params={"period": "1d", "count": 10},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Got {len(data.get('data', []))} daily items")
            if data.get('data'):
                print(f"First item: {data['data'][0]}")
        else:
            print(f"FAIL: HTTP {response.status_code}")
            print(response.text[:200])
    except Exception as e:
        print(f"ERROR: {e}")

    # Test 2: 30min K-line
    print("\n=== Test 2: 000858.SZ 30min ===")
    try:
        response = requests.get(
            f"{base_url}/api/kline/realtime/000858.SZ",
            params={"period": "30m", "count": 10},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', [])
            print(f"SUCCESS: Got {len(items)} 30min items")
            if len(items) >= 2:
                t1 = items[0]['time']
                t2 = items[1]['time']
                diff_minutes = (t2 - t1) / (1000 * 60)
                print(f"Time diff: {diff_minutes} minutes")
                if diff_minutes == 30:
                    print("OK: Time interval is correct (30min)")
                else:
                    print(f"WARNING: Expected 30min, got {diff_minutes}min")
        else:
            print(f"FAIL: HTTP {response.status_code}")
            print(response.text[:200])
    except Exception as e:
        print(f"ERROR: {e}")

    # Test 3: 5min K-line
    print("\n=== Test 3: 000858.SZ 5min ===")
    try:
        response = requests.get(
            f"{base_url}/api/kline/realtime/000858.SZ",
            params={"period": "5m", "count": 10},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', [])
            print(f"SUCCESS: Got {len(items)} 5min items")
            if len(items) >= 2:
                t1 = items[0]['time']
                t2 = items[1]['time']
                diff_minutes = (t2 - t1) / (1000 * 60)
                if diff_minutes == 5:
                    print("OK: Time interval is correct (5min)")
                else:
                    print(f"WARNING: Expected 5min, got {diff_minutes}min")
        else:
            print(f"FAIL: HTTP {response.status_code}")
            print(response.text[:200])
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_kline_api()
