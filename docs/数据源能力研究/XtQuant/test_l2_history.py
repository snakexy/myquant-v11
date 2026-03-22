"""
L2: 历史快照测试

测试目标：
1. get_market_data_ex() - 在线获取历史K线
2. 不同周期的行为
3. count参数限制
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time

symbol = '600519.SH'

print("="*80)
print("L2: 历史快照测试")
print("="*80)
print(f"股票: {symbol}")
print()

# ===== 测试1: 日K线 - 获取最近30天 =====
print("[测试1] 日K线 - 获取最近30天")
print("-"*80)
try:
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        count=30,
        dividend_type='none'
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 成功！耗时: {elapsed:.2f}ms")
        print(f"   获取 {len(df)} 条数据")
        print(f"   最新: {df.index[-1]}, 收盘: {df['close'].iloc[-1]}")
        print(f"   最旧: {df.index[0]}, 收盘: {df['close'].iloc[0]}")
    else:
        print(f"[FAIL] 无数据")
except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试2: 分钟线 - 获取最近120条5分钟 =====
print("[测试2] 分钟线 - 获取最近120条5分钟K线")
print("-"*80)
try:
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        count=120,
        dividend_type='none'
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 成功！耗时: {elapsed:.2f}ms")
        print(f"   获取 {len(df)} 条数据")
        if len(df) > 0:
            print(f"   最新: {df.index[-1]}")
            print(f"   最旧: {df.index[0]}")
            print(f"   时间跨度: {len(df)} * 5分钟 = {len(df)*5}分钟 = {len(df)*5/60:.1f}小时")
            print(f"   是否超过16天(384小时): {'是' if len(df)*5 >= 384*60 else '否'}")
    else:
        print(f"[FAIL] 无数据")
except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试3: 分钟线 - 获取大量数据（测试16天限制）=====
print("[测试3] 分钟线 - 获取2000条5分钟K线（测试16天限制）")
print("-"*80)
print("说明: 2000 * 5分钟 = 10000分钟 = 166.7小时 = 6.9天 < 16天，应该可以获取")
try:
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        count=2000,
        dividend_type='none'
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 成功！耗时: {elapsed:.2f}ms")
        print(f"   获取 {len(df)} 条数据")
        print(f"   时间跨度: {len(df)*5/60:.1f}小时 = {len(df)*5/60/24:.2f}天")
    else:
        print(f"[FAIL] 无数据（可能超过16天限制）")
except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试4: 1分钟K线 =====
print("[测试4] 1分钟K线 - 获取240条（测试16天限制）")
print("-"*80)
print("说明: 240 * 1分钟 = 240分钟 = 4小时 < 16天，应该可以获取")
try:
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1m',
        count=240,
        dividend_type='none'
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 成功！耗时: {elapsed:.2f}ms")
        print(f"   获取 {len(df)} 条数据")
        print(f"   时间跨度: {len(df)}分钟 = {len(df)/60:.1f}小时")
    else:
        print(f"[FAIL] 无数据")
except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()
print("="*80)
print("结论:")
print("- 日K线: 无明显限制")
print("- 分钟线: 16天限制需要验证")
print("="*80)
