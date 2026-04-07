"""快速诊断"""
import sys
sys.path.insert(0, 'E:/MyQuant_v11/backend')

from myquant.core.market.adapters import get_adapter

# 快速检查 HotDB 5m 数据
hotdb = get_adapter('hotdb')
df = hotdb.get_kline(symbols=['300046.SZ'], period='5m', count=10)

if '300046.SZ' in df:
    df_300046 = df['300046.SZ'].sort_values('datetime', ascending=False)
    print("台基股份 5m 最新10条:")
    print(df_300046[['datetime', 'volume', 'amount']].to_string())
    print(f"\n最新时间: {df_300046.iloc[0]['datetime']}")
