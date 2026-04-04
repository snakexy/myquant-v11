import sys
sys.path.insert(0, r'E:\MyQuant_v11\backend\src')
from myquant.core.market.adapters import get_adapter

symbol = '601628.SH'
hotdb = get_adapter('hotdb')
df_dict = hotdb.get_kline([symbol], period='1d', count=5)
if symbol in df_dict and not df_dict[symbol].empty:
    print(f"Data still exists: {len(df_dict[symbol])} rows")
else:
    print("Data cleared successfully")
