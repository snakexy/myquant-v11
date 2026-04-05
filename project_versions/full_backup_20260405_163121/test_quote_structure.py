# -*- coding: utf-8 -*-
"""测试 XtQuant 盘口数据结构"""

from xtquant import xtdata
import json

symbol = '600519.SH'
data = xtdata.get_full_tick([symbol])

if data and symbol in data:
    quote = data[symbol]

    # 查找所有字段
    print("=== 所有字段 ===")
    for k, v in sorted(quote.items()):
        print(f"{k}: {v}")

    # 查找盘口相关字段
    print("\n=== 盘口相关字段 ===")
    for k, v in quote.items():
        k_lower = k.lower()
        if any(x in k_lower for x in ['buy', 'sell', 'bid', 'ask', 'vol']):
            print(f"{k}: {v}")
else:
    print("无数据")
