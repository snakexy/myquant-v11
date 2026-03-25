# -*- coding: utf-8 -*-
"""直接测试 XtQuant get_full_tick 返回的数据"""

from xtquant import xtdata
import json

symbol = '600519.SH'
data = xtdata.get_full_tick([symbol])

if data and symbol in data:
    quote = data[symbol]

    # 打印所有字段
    print("=== 所有字段 ===")
    for k, v in sorted(quote.items()):
        if isinstance(v, list):
            print(f"{k}: {v[:10]}...")  # 列表只打印前10个
        else:
            print(f"{k}: {v}")

    # 专门查找盘口相关
    print("\n=== 盘口相关字段 ===")
    for k in sorted(quote.keys()):
        k_lower = k.lower()
        if any(x in k_lower for x in ['bid', 'ask', 'buy', 'sell', 'order']):
            print(f"{k}: {quote[k]}")
else:
    print("无数据")
