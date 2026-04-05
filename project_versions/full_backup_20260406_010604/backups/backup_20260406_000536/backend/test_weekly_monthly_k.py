"""测试周K月K数据源"""
from myquant.core.market.adapters import get_adapter
from loguru import logger
import pandas as pd

# 测试601628.SH的周K和月K
symbol = '601628.SH'

results = {}

# 测试 pytdx
print('=' * 60)
print('测试 pytdx 周K/月K')
print('=' * 60)
try:
    pytdx = get_adapter('pytdx')
    if pytdx and pytdx.is_available():
        kline_1w = pytdx.get_kline([symbol], period='1w', count=800)
        if kline_1w and symbol in kline_1w:
            df_1w = kline_1w[symbol]
            print(f'pytdx 周K: {len(df_1w)} 条')
            if not df_1w.empty:
                print(f'  日期范围: {df_1w["datetime"].min()} 到 {df_1w["datetime"].max()}')
                results['pytdx_1w'] = (len(df_1w), str(df_1w["datetime"].min()), str(df_1w["datetime"].max()))
        else:
            print('pytdx 周K: 无数据')

        kline_1M = pytdx.get_kline([symbol], period='1M', count=800)
        if kline_1M and symbol in kline_1M:
            df_1M = kline_1M[symbol]
            print(f'pytdx 月K: {len(df_1M)} 条')
            if not df_1M.empty:
                print(f'  日期范围: {df_1M["datetime"].min()} 到 {df_1M["datetime"].max()}')
                results['pytdx_1M'] = (len(df_1M), str(df_1M["datetime"].min()), str(df_1M["datetime"].max()))
        else:
            print('pytdx 月K: 无数据')
    else:
        print('pytdx 不可用')
except Exception as e:
    print(f'pytdx 错误: {e}')

# 测试 xtquant
print()
print('=' * 60)
print('测试 xtquant 周K/月K')
print('=' * 60)
try:
    xtquant = get_adapter('xtquant')
    if xtquant and xtquant.is_available():
        kline_1w = xtquant.get_kline([symbol], period='1w', count=800)
        if kline_1w and symbol in kline_1w:
            df_1w = kline_1w[symbol]
            print(f'xtquant 周K: {len(df_1w)} 条')
            if not df_1w.empty:
                print(f'  日期范围: {df_1w["datetime"].min()} 到 {df_1w["datetime"].max()}')
                results['xtquant_1w'] = (len(df_1w), str(df_1w["datetime"].min()), str(df_1w["datetime"].max()))
        else:
            print('xtquant 周K: 无数据')

        kline_1M = xtquant.get_kline([symbol], period='1M', count=800)
        if kline_1M and symbol in kline_1M:
            df_1M = kline_1M[symbol]
            print(f'xtquant 月K: {len(df_1M)} 条')
            if not df_1M.empty:
                print(f'  日期范围: {df_1M["datetime"].min()} 到 {df_1M["datetime"].max()}')
                results['xtquant_1M'] = (len(df_1M), str(df_1M["datetime"].min()), str(df_1M["datetime"].max()))
        else:
            print('xtquant 月K: 无数据')
    else:
        print('xtquant 不可用')
except Exception as e:
    print(f'xtquant 错误: {e}')

# 测试 tdxquant
print()
print('=' * 60)
print('测试 tdxquant 周K/月K')
print('=' * 60)
try:
    tdxquant = get_adapter('tdxquant')
    if tdxquant and tdxquant.is_available():
        kline_1w = tdxquant.get_kline([symbol], period='1w', count=800)
        if kline_1w and symbol in kline_1w:
            df_1w = kline_1w[symbol]
            print(f'tdxquant 周K: {len(df_1w)} 条')
            if not df_1w.empty:
                print(f'  日期范围: {df_1w["datetime"].min()} 到 {df_1w["datetime"].max()}')
                results['tdxquant_1w'] = (len(df_1w), str(df_1w["datetime"].min()), str(df_1w["datetime"].max()))
        else:
            print('tdxquant 周K: 无数据')

        kline_1M = tdxquant.get_kline([symbol], period='1M', count=800)
        if kline_1M and symbol in kline_1M:
            df_1M = kline_1M[symbol]
            print(f'tdxquant 月K: {len(df_1M)} 条')
            if not df_1M.empty:
                print(f'  日期范围: {df_1M["datetime"].min()} 到 {df_1M["datetime"].max()}')
                results['tdxquant_1M'] = (len(df_1M), str(df_1M["datetime"].min()), str(df_1M["datetime"].max()))
        else:
            print('tdxquant 月K: 无数据')
    else:
        print('tdxquant 不可用')
except Exception as e:
    print(f'tdxquant 错误: {e}')

print()
print('=' * 60)
print('汇总结果')
print('=' * 60)
for key, val in results.items():
    print(f'{key}: {val[0]} 条, {val[1]} 到 {val[2]}')
