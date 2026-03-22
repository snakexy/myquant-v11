# -*- coding: utf-8 -*-
"""
测试: get_full_tick() 完整字段列表

查看get_full_tick()返回的所有字段
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import json

print("="*80)
print("测试: get_full_tick() 完整字段列表")
print("="*80)
print()

# 获取几只股票的行情
test_stocks = ['600519.SH', '000001.SZ', '600036.SH']

try:
    tick_data = xtdata.get_full_tick(test_stocks)

    if tick_data:
        # 分析第一只股票的所有字段
        first_stock = test_stocks[0]
        if first_stock in tick_data:
            data = tick_data[first_stock]

            print(f"股票: {first_stock}")
            print(f"字段数量: {len(data)}")
            print()
            print("所有字段:")
            print("-"*80)

            # 按字段名排序并打印
            for key, value in sorted(data.items()):
                value_type = type(value).__name__
                print(f"{key:20s} : {value_type:10s} = {value}")

        print()
        print("="*80)
        print("分析: 常用字段说明")
        print("-"*80)

        # 常用字段说明
        field_descriptions = {
            # 基础行情
            'lastPrice': '最新价',
            'lastClose': '昨收价',
            'open': '开盘价',
            'high': '最高价',
            'low': '最低价',
            'amount': '成交额',
            'volume': '成交量',

            # 涨跌
            'pMove': '涨跌幅',
            'pMoveVal': '涨跌额',

            # 五档行情
            'askPrice1': '卖一价',
            'askVolume1': '卖一量',
            'askPrice2': '卖二价',
            'askVolume2': '卖二量',
            'askPrice3': '卖三价',
            'askVolume3': '卖三量',
            'bidPrice1': '买一价',
            'bidVolume1': '买一量',
            'bidPrice2': '买二价',
            'bidVolume2': '买二量',
            'bidPrice3': '买三价',
            'bidVolume3': '买三量',

            # 其他
            'pSnap': '涨速',
            'pe': '市盈率',
            'marketValue': '总市值',
            'circulationValue': '流通市值',
        }

        for field, desc in sorted(field_descriptions.items()):
            if field in data:
                print(f"{field:20s} : {desc}")

    else:
        print("未获取到数据")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
