#!/usr/bin/env python3
"""检查TdxQuant返回的原始数据单位"""
import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')

from myquant.core.market.adapters import get_adapter
import pandas as pd

symbol = '000001.SZ'
period = '5m'

print("=" * 60)
print("验证TdxQuant返回的数据单位")
print("=" * 60)

# 获取TdxQuant适配器
tdx = get_adapter('tdxquant')
if tdx and tdx._ensure_initialized():
    # 获取3月9日的数据
    df_dict = tdx.get_kline([symbol], period=period, count=100)

    if symbol in df_dict and not df_dict[symbol].empty:
        df = df_dict[symbol]
        df['datetime'] = pd.to_datetime(df.index)

        # 查找3月9日的数据
        march_9_start = pd.Timestamp('2026-03-09 09:30:00')
        march_9_end = pd.Timestamp('2026-03-09 15:00:00')

        df_march_9 = df[(df['datetime'] >= march_9_start) & (df['datetime'] <= march_9_end)]

        print(f"\nTdxQuant返回的3月9日数据:")
        if not df_march_9.empty:
            print(df_march_9[['volume', 'open', 'close']].head())
            sample_vol = df_march_9['volume'].iloc[0]
            print(f"\n样本volume: {sample_vol:,.0f}")
            if sample_vol > 1000000:
                print("(股单位 - 数值过大，未转换)")
            else:
                print("(手单位 - 已转换)")
        else:
            print("无3月9日数据")

        # 对比HotDB中的3月9日数据
        print("\n" + "=" * 60)
        print("对比HotDB中的3月9日数据:")
        print("=" * 60)

        hotdb = get_adapter('hotdb')
        df_dict_hot = hotdb.get_kline([symbol], period=period, count=5000, allow_stale=True)

        if symbol in df_dict_hot and not df_dict_hot[symbol].empty:
            df_hot = df_dict_hot[symbol]
            df_hot['datetime'] = pd.to_datetime(df_hot['datetime'])
            df_hot_march_9 = df_hot[(df_hot['datetime'] >= march_9_start) & (df_hot['datetime'] <= march_9_end)]

            if not df_hot_march_9.empty:
                print(df_hot_march_9[['datetime', 'volume', 'open', 'close']].head())
                hot_sample_vol = df_hot_march_9['volume'].iloc[0]
                print(f"\nHotDB样本volume: {hot_sample_vol:,.0f}")
                if hot_sample_vol > 1000000:
                    print("(股单位 - 未转换)")
                else:
                    print("(手单位 - 已转换)")
            else:
                print("HotDB中无3月9日数据")
    else:
        print("TdxQuant未返回数据")
else:
    print("TdxQuant不可用")
