"""测试 snapshot API 实际返回的字段名"""
import requests
import json

url = "http://localhost:8000/api/v1/quotes/snapshot/600519.SH"

try:
    resp = requests.get(url, timeout=10)
    data = resp.json()
    print("=== 返回字段 ===")
    if isinstance(data, list) and len(data) > 0:
        item = data[0]
        for k, v in item.items():
            print(f"  {k}: {v}")
    elif isinstance(data, dict):
        if 'data' in data and isinstance(data['data'], list):
            item = data['data'][0]
            for k, v in item.items():
                print(f"  {k}: {v}")
        else:
            for k, v in data.items():
                print(f"  {k}: {v}")
except Exception as e:
    print(f"请求失败: {e}")
