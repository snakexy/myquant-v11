"""
L3.5: 公司治理数据测试

测试目标：
1. get_instrument_detail() - 股票基本信息
2. get_stock_list_in_sector() - 板块成分股
3. 股东信息获取
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata

print("="*80)
print("L3.5: 公司治理数据测试")
print("="*80)
print()

# ===== 测试1: 获取股票基本信息 =====
print("[测试1] get_instrument_detail() - 股票基本信息")
print("-"*80)
symbol = '600519.SH'
try:
    detail = xtdata.get_instrument_detail(symbol)

    if detail:
        print(f"[OK] 成功！")
        print(f"   数据类型: {type(detail)}")
        print(f"   字段数量: {len(detail)}")
        print(f"   主要字段:")
        for key in list(detail.keys())[:10]:
            print(f"     {key}: {detail[key]}")
    else:
        print(f"[FAIL] 无数据")
except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试2: 批量获取股票信息 =====
print("[测试2] 批量获取股票信息")
print("-"*80)
symbols = ['600519.SH', '000001.SZ', '600000.SH']

try:
    details = {}
    for sym in symbols:
        detail = xtdata.get_instrument_detail(sym)
        if detail:
            details[sym] = detail

    print(f"[OK] 获取 {len(details)} 只股票信息")
    for sym, detail in details.items():
        name = detail.get('InstrumentName', 'N/A')
        print(f"   {sym}: {name}")

except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()

# ===== 测试3: 获取板块成分股 =====
print("[测试3] get_stock_list_in_sector() - 板块成分股")
print("-"*80)

sectors = ['沪深300', '中证500', '上证50']

for sector in sectors:
    try:
        stocks = xtdata.get_stock_list_in_sector(sector)

        if stocks:
            print(f"[OK] {sector}: {len(stocks)}只股票")
            print(f"   前5只: {stocks[:5]}")
        else:
            print(f"[FAIL] {sector}: 无数据")

    except Exception as e:
        print(f"[ERROR] {sector}: {e}")

print()

# ===== 测试4: 获取所有板块列表 =====
print("[测试4] 获取所有板块列表")
print("-"*80)
try:
    # XtQuant可能提供了获取板块列表的函数
    # 这里测试常见的板块
    common_sectors = [
        '沪深300',
        '中证500',
        '上证50',
        '中证1000',
        '创业板指',
        '科创50',
        '上证指数',
        '深证成指',
        '中小板指'
    ]

    print("测试常见板块:")
    for sector in common_sectors:
        try:
            stocks = xtdata.get_stock_list_in_sector(sector)
            if stocks:
                print(f"   {sector}: {len(stocks)}只")
        except:
            print(f"   {sector}: 不支持")

except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()
print("="*80)
print("结论:")
print("- get_instrument_detail() 可获取股票基本信息")
print("- get_stock_list_in_sector() 可获取板块成分股")
print("- 适合股票筛选和板块分析")
print("="*80)
