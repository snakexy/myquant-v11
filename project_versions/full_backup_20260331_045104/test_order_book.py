# -*- coding: utf-8 -*-
"""测试盘口数据修复"""

import requests
import json

codes = ["600519.SH", "600000.SH", "000001.SZ"]

resp = requests.post(
    "http://127.0.0.1:8000/api/market/quotes",
    json=codes,
    timeout=10
)

if resp.status_code == 200:
    result = resp.json()
    print("=" * 60)
    # API 返回格式: {code, data: {count, quotes: {...}}, message}
    quotes_data = result.get('data', {}).get('quotes', {})
    for code, quote in quotes_data.items():
        print(f"\n{code} ({quote.get('price', 0)}元):")
        print("买盘5档数量:", end=" ")
        for i in range(1, 6):
            vol = quote.get(f'bid_vol{i}', 0)
            print(f"{vol}", end=" ")
        print("\n卖盘5档数量:", end=" ")
        for i in range(1, 6):
            vol = quote.get(f'ask_vol{i}', 0)
            print(f"{vol}", end=" ")
        print()
else:
    print(f"请求失败: {resp.status_code}")
