# -*- coding: utf-8 -*-
"""
分钟线测试 - 使用正确参数（参考adapter实现）
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time

symbol = '600519.SH'

print("="*80)
print("分钟线测试 - 使用adapter的正确参数")
print("="*80)
print("股票: %s" % symbol)
print()

# ===== 测试1: 5分钟K线（参考adapter的实现）=====
print("[测试1] 5分钟K线 - 使用空字符串参数")
print("-"*80)
try:
    # 先订阅（参考adapter line 663-667）
    xtdata.subscribe_quote(
        stock_code=symbol,
        period='5m',
        count=0
    )
    print("[OK] 订阅成功")

    # 获取数据（参考adapter line 676-685）
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='5m',
        start_time='',  # 空字符串=不限制起始时间
        end_time='',    # 空字符串=不限制结束时间
        count=120,      # 获取最新120条
        dividend_type='none',  # 字符串类型
        fill_data=True
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print("[OK] 获取成功！耗时: %.2fms" % elapsed)
        print("   数据条数: %d" % len(df))
        if len(df) > 0:
            print("   最新: %s" % str(df.index[-1]))
            print("   最旧: %s" % str(df.index[0]))
            print("   时间跨度: %d * 5分钟 = %.1f小时" % (len(df), len(df)*5/60.0))
    else:
        print("[FAIL] 无数据")

except Exception as e:
    print("[ERROR] 错误: %s" % str(e))
    import traceback
    traceback.print_exc()

print()

# ===== 测试2: 1分钟K线 =====
print("[测试2] 1分钟K线 - 使用空字符串参数")
print("-"*80)
try:
    # 先订阅
    xtdata.subscribe_quote(
        stock_code=symbol,
        period='1m',
        count=0
    )
    print("[OK] 订阅成功")

    # 获取数据
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1m',
        start_time='',
        end_time='',
        count=240,  # 240条1分钟 = 4小时
        dividend_type='none',
        fill_data=True
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print("[OK] 获取成功！耗时: %.2fms" % elapsed)
        print("   数据条数: %d" % len(df))
        if len(df) > 0:
            print("   最新: %s" % str(df.index[-1]))
            print("   最旧: %s" % str(df.index[0]))
            print("   时间跨度: %d分钟 = %.1f小时" % (len(df), len(df)/60.0))
    else:
        print("[FAIL] 无数据")

except Exception as e:
    print("[ERROR] 错误: %s" % str(e))

print()

# ===== 测试3: 日K线（对比）=====
print("[测试3] 日K线 - 使用空字符串参数（对比）")
print("-"*80)
try:
    # 先订阅
    xtdata.subscribe_quote(
        stock_code=symbol,
        period='1d',
        count=0
    )
    print("[OK] 订阅成功")

    # 获取数据
    start = time.time()
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        start_time='',
        end_time='',
        count=30,  # 30天
        dividend_type='none',
        fill_data=True
    )
    elapsed = (time.time() - start) * 1000

    if data and symbol in data:
        df = data[symbol]
        print("[OK] 获取成功！耗时: %.2fms" % elapsed)
        print("   数据条数: %d" % len(df))
        if len(df) > 0:
            print("   最新: %s" % str(df.index[-1]))
            print("   最旧: %s" % str(df.index[0]))
    else:
        print("[FAIL] 无数据")

except Exception as e:
    print("[ERROR] 错误: %s" % str(e))

print()
print("="*80)
print("结论:")
print("- start_time和end_time必须用空字符串''")
print("- dividend_type必须是字符串'none'而不是数字0")
print("- 需要先订阅再用get_market_data_ex获取")
print("="*80)
