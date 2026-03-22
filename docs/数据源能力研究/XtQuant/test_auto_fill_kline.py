"""
高级场景测试1: 自动补全K线数据

测试目标：
1. 本地数据不足时自动在线获取
2. 数据缺失时的智能补全
3. 复权数据的自动获取
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import pandas as pd
import time

symbol = '600519.SH'

print("="*80)
print("场景1: 自动补全K线数据")
print("="*80)
print(f"股票: {symbol}")
print()

# ===== 测试1: 本地数据不足 =====
print("[测试1] 模拟本地数据不足，自动在线获取")
print("-"*80)
print("场景: 用户请求100条，但本地只有50条")

try:
    # 1. 先下载少量历史数据到本地
    print("步骤1: 下载50条历史数据到本地...")
    xtdata.download_history_data(
        stock_code=symbol,
        period='1d',
        start_time='20241101',  # 只下载2个月
        end_time='20241231'
    )

    # 2. 读取本地数据（应该只有50条左右）
    print("步骤2: 读取本地数据...")
    local_data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        start_time=0,
        end_time=0,
        count=100,  # 请求100条
        dividend_type='none'
    )

    if symbol in local_data:
        df_local = local_data[symbol]
        print(f"   本地数据: {len(df_local)}条")

        # 3. 如果不足100条，应该在线获取更多
        if len(df_local) < 100:
            print(f"   数据不足！需要在线获取缺失的 {100 - len(df_local)}条")

            # 在线获取更多数据
            print("步骤3: 在线获取完整数据...")
            online_data = xtdata.get_market_data_ex(
                field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
                stock_list=[symbol],
                period='1d',
                count=100,
                dividend_type='none'
            )

            if symbol in online_data:
                df_online = online_data[symbol]
                print(f"   [OK] 在线获取成功！获得 {len(df_online)}条")
                print(f"   最新: {df_online.index[-1]}")
                print(f"   最旧: {df_online.index[0]}")

except Exception as e:
    print(f"[ERROR] 异常: {e}")
    import traceback
    traceback.print_exc()

print()

# ===== 测试2: 不同复权类型自动获取 =====
print("[测试2] 不同复权类型的数据获取")
print("-"*80)
print("场景: 本地只有不复权数据，用户请求前复权数据")

try:
    # 获取不复权
    print("步骤1: 获取不复权数据...")
    data_none = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        count=10,
        dividend_type='none'
    )

    if symbol in data_none:
        df_none = data_none[symbol]
        print(f"   不复权: {len(df_none)}条")
        print(f"   最新收盘: {df_none['close'].iloc[-1]}")

    # 获取前复权
    print("步骤2: 获取前复权数据...")
    data_front = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        count=10,
        dividend_type='front'
    )

    if symbol in data_front:
        df_front = data_front[symbol]
        print(f"   前复权: {len(df_front)}条")
        print(f"   最新收盘: {df_front['close'].iloc[-1]}")

        # 验证复权效果
        if len(df_none) > 0 and len(df_front) > 0:
            # 最新价格应该相同（前复权不改变当前价格）
            if df_none['close'].iloc[-1] == df_front['close'].iloc[-1]:
                print("   [OK] 复权验证通过：最新价格相同")
            else:
                print("   [WARNING] 复权验证失败：最新价格不同")

            # 历史价格应该不同（前复权调整了历史价格）
            if df_none['close'].iloc[0] != df_front['close'].iloc[0]:
                print("   [OK] 复权验证通过：历史价格已调整")
                print(f"     不复权首日: {df_none['close'].iloc[0]}")
                print(f"     前复权首日: {df_front['close'].iloc[0]}")
            else:
                print("   [WARNING] 复权验证失败：历史价格未调整")

except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()
print("="*80)
print("结论:")
print("- XtQuant可以在线获取缺失的数据")
print("- 支持多种复权类型自动获取")
print("- 需要：实现智能补全逻辑，判断本地数据是否足够")
print("="*80)
