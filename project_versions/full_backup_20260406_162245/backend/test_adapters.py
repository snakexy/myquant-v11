"""测试数据源连接"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend/src')

from myquant.core.market.adapters import get_adapter

print("=" * 50)
print("测试数据源连接")
print("=" * 50)

# 测试 PyTdx
print("\n1. 测试 PyTdx:")
try:
    pytdx = get_adapter('pytdx')
    if pytdx:
        print(f"   PyTdx 可用: {pytdx.is_available()}")
        if pytdx.is_available():
            quotes = pytdx.get_quote(['000001', '600519'])
            print(f"   获取行情: {len(quotes) if quotes else 0} 只股票")
            if quotes:
                for code, data in list(quotes.items())[:2]:
                    print(f"   {code}: price={data.get('price') if data else 'N/A'}")
    else:
        print("   PyTdx 初始化失败")
except Exception as e:
    print(f"   错误: {e}")

# 测试 TdxQuant
print("\n2. 测试 TdxQuant:")
try:
    tdxquant = get_adapter('tdxquant')
    if tdxquant:
        print(f"   TdxQuant 可用: {tdxquant.is_available()}")
        if tdxquant.is_available():
            quotes = tdxquant.get_quote(['000001', '600519'])
            print(f"   获取行情: {len(quotes) if quotes else 0} 只股票")
            if quotes:
                for code, data in list(quotes.items())[:2]:
                    print(f"   {code}: price={data.get('price') if data else 'N/A'}")
    else:
        print("   TdxQuant 初始化失败")
except Exception as e:
    print(f"   错误: {e}")

# 测试 XtQuant
print("\n3. 测试 XtQuant:")
try:
    xtquant = get_adapter('xtquant')
    if xtquant:
        print(f"   XtQuant 可用: {xtquant.is_available()}")
        if xtquant.is_available():
            quotes = xtquant.get_quote(['000001', '600519'])
            print(f"   获取行情: {len(quotes) if quotes else 0} 只股票")
            if quotes:
                for code, data in list(quotes.items())[:2]:
                    print(f"   {code}: price={data.get('price') if data else 'N/A'}")
    else:
        print("   XtQuant 初始化失败")
except Exception as e:
    print(f"   错误: {e}")

print("\n" + "=" * 50)
