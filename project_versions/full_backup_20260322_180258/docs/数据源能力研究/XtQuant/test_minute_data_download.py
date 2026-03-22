"""
分钟线数据下载测试

测试目标：
1. 下载分钟线数据
2. 验证16天限制
3. 对比下载前后
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime, timedelta

symbol = '600519.SH'

print("="*80)
print("分钟线数据下载测试")
print("="*80)
print(f"股票: {symbol}")
print()

# 计算时间范围
end_date = datetime.now()
start_date_7days = end_date - timedelta(days=7)
start_date_20days = end_date - timedelta(days=20)

print(f"今天: {end_date.strftime('%Y%m%d')}")
print(f"7天前: {start_date_7days.strftime('%Y%m%d')}")
print(f"20天前: {start_date_20days.strftime('%Y%m%d')}")
print()

# ===== 测试1: 先尝试在线获取（不下载）=====
print("[测试1] 在线获取5分钟K线（不下载）")
print("-"*80)
try:
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        count=120,  # 120 * 5分钟 = 10小时
        dividend_type='none'
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 获取 {len(df)} 条数据，耗时 {elapsed:.2f}ms")
        if len(df) > 0:
            print(f"   最新: {df.index[-1]}")
            print(f"   最旧: {df.index[0]}")
    else:
        print(f"[FAIL] 无数据")
except Exception as e:
    print(f"[ERROR] {e}")

print()

# ===== 测试2: 下载7天分钟数据 =====
print("[测试2] 下载最近7天5分钟K线数据")
print("-"*80)
try:
    start = time.time()
    result = xtdata.download_history_data(
        stock_code=symbol,
        period='5m',
        start_time=start_date_7days.strftime('%Y%m%d'),
        end_time=end_date.strftime('%Y%m%d')
    )
    elapsed = time.time() - start

    print(f"[OK] 下载完成！耗时: {elapsed:.2f}秒")
    print(f"   返回: {result}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

# ===== 测试3: 下载后读取 =====
print("[测试3] 读取下载后的5分钟K线")
print("-"*80)
try:
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time=int(start_date_7days.strftime('%Y%m%d')),
        end_time=int(end_date.strftime('%Y%m%d')),
        count=0,
        dividend_type='none'
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 获取 {len(df)} 条数据，耗时 {elapsed:.2f}ms")
        if len(df) > 0:
            print(f"   最新: {df.index[-1]}")
            print(f"   最旧: {df.index[0]}")
            print(f"   时间跨度: {len(df)} * 5分钟 = {len(df)*5/60:.1f}小时 = {len(df)*5/60/24:.2f}天")
    else:
        print(f"[FAIL] 无数据")

except Exception as e:
    print(f"[ERROR] {e}")

print()

# ===== 测试4: 尝试下载20天（测试16天限制）=====
print("[测试4] 尝试下载20天数据（测试16天限制）")
print("-"*80)
try:
    start = time.time()
    result = xtdata.download_history_data(
        stock_code=symbol,
        period='5m',
        start_time=start_date_20days.strftime('%Y%m%d'),
        end_time=end_date.strftime('%Y%m%d')
    )
    elapsed = time.time() - start

    print(f"[下载完成] 耗时: {elapsed:.2f}秒")

    # 尝试读取
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time=int(start_date_20days.strftime('%Y%m%d')),
        end_time=int(end_date.strftime('%Y%m%d')),
        count=0,
        dividend_type='none'
    )

    if data and symbol in data:
        df = data[symbol]
        print(f"[读取] 获取 {len(df)} 条数据")
        if len(df) > 0:
            print(f"   时间跨度: {len(df)*5/60/24:.2f}天")
            if len(df)*5/60/24 < 16:
                print(f"   ⚠️  可能存在16天限制")
    else:
        print(f"[读取] 无数据")

except Exception as e:
    print(f"[ERROR] {e}")

print()

# ===== 测试5: 1分钟K线下载 =====
print("[测试5] 下载最近1天1分钟K线")
print("-"*80)
try:
    start = time.time()
    result = xtdata.download_history_data(
        stock_code=symbol,
        period='1m',
        start_time=start_date_7days.strftime('%Y%m%d'),
        end_time=end_date.strftime('%Y%m%d')
    )
    elapsed = time.time() - start

    print(f"[下载完成] 耗时: {elapsed:.2f}秒")

    # 读取
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1m',
        start_time=int(start_date_7days.strftime('%Y%m%d')),
        end_time=int(end_date.strftime('%Y%m%d')),
        count=0,
        dividend_type='none'
    )

    if data and symbol in data:
        df = data[symbol]
        print(f"[读取] 获取 {len(df)} 条1分钟数据")
        if len(df) > 0:
            print(f"   时间跨度: {len(df)}分钟 = {len(df)/60:.1f}小时")
    else:
        print(f"[读取] 无数据")

except Exception as e:
    print(f"[ERROR] {e}")

print()
print("="*80)
print("结论:")
print("- 分钟线必须先下载才能读取")
print("- 需要验证是否存在16天限制")
print("- 下载+读取策略有效")
print("="*80)
