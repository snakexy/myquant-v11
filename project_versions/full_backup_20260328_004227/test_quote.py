import sys
sys.path.insert(0, 'e:/MyQuant_v11/backend/src')

from myquant.core.market.adapters import get_adapter

# 测试 XtQuant 5档
xtquant = get_adapter('xtquant')
if xtquant and xtquant.is_available():
    quotes = xtquant.get_quote(['000001.SZ'])
    if quotes:
        q = quotes.get('000001.SZ', {})
        print('XtQuant 原始返回:')
        print(f"  bid1: {q.get('bid1')} x {q.get('bid1_vol')}")
        print(f"  bid2: {q.get('bid2')} x {q.get('bid2_vol')}")
        print(f"  ask1: {q.get('ask1')} x {q.get('ask1_vol')}")
        print(f"  ask2: {q.get('ask2')} x {q.get('ask2_vol')}")
        print()
        print('所有keys:', [k for k in q.keys() if 'bid' in k or 'ask' in k])
    else:
        print('XtQuant 返回空')
else:
    print('XtQuant 不可用')

# 测试 PyTdx 5档
print('\n' + '='*50)
pytdx = get_adapter('pytdx')
if pytdx and pytdx.is_available():
    quotes = pytdx.get_quote(['000001.SZ'])
    if quotes:
        q = quotes.get('000001.SZ', {})
        print('PyTdx 原始返回:')
        print(f"  bid1: {q.get('bid1')} x {q.get('bid1_vol')}")
        print(f"  bid2: {q.get('bid2')} x {q.get('bid2_vol')}")
        print(f"  ask1: {q.get('ask1')} x {q.get('ask1_vol')}")
        print(f"  ask2: {q.get('ask2')} x {q.get('ask2_vol')}")
        print()
        print('所有keys:', [k for k in q.keys() if 'bid' in k or 'ask' in k])
    else:
        print('PyTdx 返回空')
else:
    print('PyTdx 不可用')