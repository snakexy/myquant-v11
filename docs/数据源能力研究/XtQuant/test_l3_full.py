"""
L3: 完整数据测试

测试目标：
1. download_history_data() - 历史数据下载
2. get_market_data_ex() - 读取本地完整数据
3. 大时间范围数据获取
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time

symbol = '600519.SH'

print("="*80)
print("L3: 完整数据测试")
print("="*80)
print(f"股票: {symbol}")
print()

# ===== 测试1: 下载历史数据到本地 =====
print("[测试1] 下载2024年历史数据")
print("-"*80)
print("说明: 这会下载数据到本地缓存，首次使用必须执行")
try:
    start = time.time()
    result = xtdata.download_history_data(
        stock_code=symbol,
        period='1d',
        start_time='20240101',
        end_time='20241231'
    )
    elapsed = time.time() - start

    print(f"[OK] 下载完成！耗时: {elapsed:.2f}秒")
    print(f"   返回结果: {result}")

except Exception as e:
    print(f"[ERROR] 异常: {e}")
    import traceback
    traceback.print_exc()

print()

# ===== 测试2: 读取本地完整数据 =====
print("[测试2] 读取2024年本地数据")
print("-"*80)
try:
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        start_time=20240101,
        end_time=20241231,
        count=0,  # count=0表示使用时间范围
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
    else:
        print(f"[FAIL] 无数据（可能需要先下载）")

except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试3: 跨年数据获取 =====
print("[测试3] 获取2020-2024完整数据")
print("-"*80)
try:
    # 先下载（如果还没下载）
    print("步骤1: 下载历史数据...")
    xtdata.download_history_data(
        stock_code=symbol,
        period='1d',
        start_time='20200101',
        end_time='20241231'
    )

    print("步骤2: 读取数据...")
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        start_time=20200101,
        end_time=20241231,
        count=0,
        dividend_type='none'
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 成功！耗时: {elapsed:.2f}ms")
        print(f"   获取 {len(df)} 条数据（约5年）")
        print(f"   最新: {df.index[-1]}")
        print(f"   最旧: {df.index[0]}")
    else:
        print(f"[FAIL] 无数据")

except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试4: 批量获取多股票完整数据 =====
print("[测试4] 批量获取多股票完整数据")
print("-"*80)
symbols = [f"60{i:04d}.SH" for i in range(10)]  # 10只股票

try:
    # 先批量下载
    print("步骤1: 批量下载...")
    for sym in symbols:
        try:
            xtdata.download_history_data(
                stock_code=sym,
                period='1d',
                start_time='20240101',
                end_time='20241231'
            )
        except:
            pass  # 忽略已下载的

    print("步骤2: 批量读取...")
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=symbols,
        period='1d',
        start_time=20240101,
        end_time=20241231,
        count=0,
        dividend_type='none'
    )
    elapsed = (time.time() - start) * 1000

    print(f"[OK] 获取 {len(data)} 只股票数据")
    print(f"   耗时: {elapsed:.2f}ms")
    print(f"   平均每只: {elapsed/len(data):.2f}ms")

except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()
print("="*80)
print("结论:")
print("- 完整数据必须先下载到本地")
print("- 下载速度: 取决于网络和数据量")
print("- 本地读取速度: 非常快")
print("="*80)
