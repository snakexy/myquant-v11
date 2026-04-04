#!/usr/bin/env python3
"""修复中国人寿数据 - 删除月线混入日线的异常记录"""
import sys
import os
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')
from myquant.core.market.adapters import get_adapter
import pandas as pd
import pickle

symbol = '601628.SH'
period = '1d'

print("=" * 60)
print(f"修复 {symbol} {period} 数据")
print("=" * 60)

# 直接读取HotDB的feather文件
safe_symbol = symbol.replace('/', '_').replace('\', '_')
cache_file = os.path.join(r'E:\MyQuant_v11\data\hotdata', f"{safe_symbol}_{period}.feather")
meta_file = os.path.join(r'E:\MyQuant_v11\data\hotdata', f"{safe_symbol}_{period}.pkl")

print(f"\n读取文件: {cache_file}")

if os.path.exists(cache_file):
    # 读取feather文件
    df = pd.read_feather(cache_file)
    
    print(f"\n原始数据: {len(df)} 条")
    print(f"\n2026-03-27的数据:")
    mask_0327 = df['datetime'].astype(str).str.contains('2026-03-27')
    print(df[mask_0327][['datetime', 'open', 'high', 'low', 'close', 'volume']].to_string())
    
    # 删除异常记录（volume > 4000000 的）
    mask_large_volume = df['volume'] > 4000000
    if mask_large_volume.any():
        print(f"\n发现异常记录: {mask_large_volume.sum()} 条")
        print(df[mask_large_volume][['datetime', 'open', 'high', 'low', 'close', 'volume']].to_string())
        
        # 删除异常记录
        df_clean = df[~mask_large_volume].copy()
        print(f"\n清理后数据: {len(df_clean)} 条")
        
        # 保存回原文件
        print(f"\n保存清理后的数据...")
        df_clean.to_feather(cache_file)
        
        # 更新meta文件
        if os.path.exists(meta_file):
            with open(meta_file, 'rb') as f:
                meta = pickle.load(f)
            meta['total_rows'] = len(df_clean)
            with open(meta_file, 'wb') as f:
                pickle.dump(meta, f)
            print(f"更新meta: {meta}")
        
        print("✓ 修复完成")
    else:
        print("\n未发现异常大成交量记录")
else:
    print(f"文件不存在: {cache_file}")
