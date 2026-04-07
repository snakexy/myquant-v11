import sys
sys.path.insert(0, 'e:/MyQuant_v11/backend/src')

from myquant.core.market.adapters import get_adapter

adapter = get_adapter('xtquant')
if adapter and adapter.is_available():
    quotes = adapter.get_quote(['000001.SZ'])
    if quotes:
        q = quotes.get('000001.SZ', {})
        print('XtQuant 5档数据:')
        for i in range(1, 6):
            bid_key = f'bid{i}'
            bid_vol_key = f'bid{i}_vol'
            print(f'  {bid_key}: {q.get(bid_key)} x {q.get(bid_vol_key)}')
        for i in range(1, 6):
            ask_key = f'ask{i}'
            ask_vol_key = f'ask{i}_vol'
            print(f'  {ask_key}: {q.get(ask_key)} x {q.get(ask_vol_key)}')
    else:
        print('返回空数据')
else:
    print('适配器不可用')