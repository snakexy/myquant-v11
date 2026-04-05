"""验证 60m 数据"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend')

from myquant.core.market.adapters import get_adapter

symbol = "300046.SZ"

hotdb = get_adapter('hotdb')
if hotdb and hotdb.is_available():
    # 60m
    info_1h = hotdb.get_data_info(symbol, '1h')
    print(f"[HotDB] 60m 数据信息:")
    print(f"  has_data: {info_1h.get('has_data')}")
    print(f"  count: {info_1h.get('count')}")
    print(f"  earliest: {info_1h.get('earliest')}")
    print(f"  latest: {info_1h.get('latest')}")

    # 最新几条
    df_1h = hotdb.get_kline(symbols=[symbol], period='1h', count=5)
    if symbol in df_1h and not df_1h[symbol].empty:
        df = df_1h[symbol].sort_values('datetime', ascending=False).head(5)
        print(f"\n[HotDB] 60m 最新5条:")
        for _, row in df.iterrows():
            print(f"  {row['datetime']}  volume={int(row['volume']):>10} 手")
