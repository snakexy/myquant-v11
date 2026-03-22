"""
L4: 财务数据测试

测试目标：
1. get_financial_data() - 财务报表数据
2. 支持的财务表类型
3. 数据完整性
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import pandas as pd

symbol = '600519.SH'

print("="*80)
print("L4: 财务数据测试")
print("="*80)
print(f"股票: {symbol}")
print()

# ===== 测试1: 获取所有财务表 =====
print("[测试1] 获取所有财务表（Balance, Profit, CashFlow, Growth）")
print("-"*80)
try:
    data = xtdata.get_financial_data(
        stock_list=[symbol],
        table_list=['Balance', 'Profit', 'CashFlow', 'Growth'],
        report_date='2024-03-31',
        start_time=None,
        end_time=None
    )

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 成功！")
        print(f"   数据类型: {type(df)}")
        print(f"   形状: {df.shape if isinstance(df, pd.DataFrame) else 'N/A'}")

        if isinstance(df, pd.DataFrame):
            print(f"   列名: {list(df.columns)}")
            if len(df) > 0:
                print(f"   最新一条数据:")
                print(df.iloc[-1])
    else:
        print(f"[FAIL] 无数据")
        print(f"   返回结果: {data}")

except Exception as e:
    print(f"[ERROR] 异常: {e}")
    import traceback
    traceback.print_exc()

print()

# ===== 测试2: 单独获取资产负债表 =====
print("[测试2] 单独获取资产负债表 (Balance)")
print("-"*80)
try:
    data = xtdata.get_financial_data(
        stock_list=[symbol],
        table_list=['Balance'],
        report_date='2024-03-31'
    )

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 成功！")
        if isinstance(df, pd.DataFrame) and len(df) > 0:
            print(f"   形状: {df.shape}")
            print(f"   主要字段: {list(df.columns)[:10]}")
    else:
        print(f"[FAIL] 无数据")

except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试3: 单独获取利润表 =====
print("[测试3] 单独获取利润表 (Profit)")
print("-"*80)
try:
    data = xtdata.get_financial_data(
        stock_list=[symbol],
        table_list=['Profit'],
        report_date='2024-03-31'
    )

    if data and symbol in data:
        df = data[symbol]
        print(f"[OK] 成功！")
        if isinstance(df, pd.DataFrame) and len(df) > 0:
            print(f"   形状: {df.shape}")
            print(f"   主要字段: {list(df.columns)[:10]}")
    else:
        print(f"[FAIL] 无数据")

except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试4: 批量获取多股票财务数据 =====
print("[测试4] 批量获取多股票财务数据")
print("-"*80)
symbols = [f"60{i:04d}.SH" for i in range(5)]

try:
    data = xtdata.get_financial_data(
        stock_list=symbols,
        table_list=['Balance', 'Profit'],
        report_date='2024-03-31'
    )

    print(f"[OK] 获取 {len(data)} 只股票财务数据")
    for sym in list(data.keys())[:3]:
        print(f"   {sym}: {type(data[sym])}")

except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试5: 不同报告期 =====
print("[测试5] 测试不同报告期")
print("-"*80)
report_dates = ['2024-03-31', '2023-12-31', '2023-09-30', '2023-06-30']

for date in report_dates:
    try:
        data = xtdata.get_financial_data(
            stock_list=[symbol],
            table_list=['Profit'],
            report_date=date
        )

        if data and symbol in data:
            df = data[symbol]
            if isinstance(df, pd.DataFrame):
                print(f"   {date}: {len(df)}条数据")
            else:
                print(f"   {date}: 非DataFrame格式")
        else:
            print(f"   {date}: 无数据")

    except Exception as e:
        print(f"   {date}: 异常 - {e}")

print()
print("="*80)
print("结论:")
print("- 财务数据可能需要付费权限")
print("- 支持的表: Balance, Profit, CashFlow, Growth")
print("- 数据格式: DataFrame")
print("="*80)
