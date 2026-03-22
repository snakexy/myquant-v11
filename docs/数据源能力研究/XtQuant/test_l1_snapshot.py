"""
L1: 实时快照测试

测试目标：
1. get_full_kline() - 最新K线快照
2. get_market_data() - 实时行情数据
3. 实时数据更新频率
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time

symbol = '600519.SH'

print("="*80)
print("L1: 实时快照测试")
print("="*80)
print(f"股票: {symbol}")
print()

# ===== 测试1: get_full_kline() - 最新K线快照 =====
print("[测试1] get_full_kline() - 最新K线快照")
print("-"*80)
try:
    start = time.time()
    data = xtdata.get_full_kline(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        count=1,  # 只获取最新1条
        dividend_type='none',
        fill_data=True
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 成功！耗时: {elapsed:.2f}ms")
        print(f"   获取 {len(df)} 条数据")
        if len(df) > 0:
            print(f"   日期: {df.index[-1]}")
            print(f"   收盘: {df['close'].iloc[-1]}")
    else:
        print(f"[FAIL] 无数据")
except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试2: get_market_data() - 实时行情 =====
print("[测试2] get_market_data() - 实时行情")
print("-"*80)
try:
    # 先订阅
    xtdata.subscribe_quote(symbol, period='1d', count=0)
    time.sleep(0.5)

    start = time.time()
    data = xtdata.get_market_data(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        start_time='',
        end_time='',
        count=1,
        dividend_type='none',
        fill_data=True
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 成功！耗时: {elapsed:.2f}ms")
        print(f"   获取 {len(df)} 条数据")
    else:
        print(f"[FAIL] 无数据")
except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试3: 多次调用查看实时更新 =====
print("[测试3] 多次调用查看实时更新（间隔1秒）")
print("-"*80)
try:
    for i in range(3):
        data = xtdata.get_full_kline(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period='1d',
            count=1,
            dividend_type='none'
        )

        if data and symbol in data:
            df = data[symbol]
            if len(df) > 0:
                print(f"   第{i+1}次 - 日期: {df.index[-1]}, 收盘: {df['close'].iloc[-1]}")

        time.sleep(1)

    print("[OK] 完成")
except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()
print("="*80)
print("结论:")
print("- get_full_kline() 适合获取最新实时快照")
print("- 性能: ~100-500ms")
print("="*80)
