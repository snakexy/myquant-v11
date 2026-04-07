"""检查 PyTdx 日K成交量单位"""
from pytdx2.hq import TdxHq_API
import pandas as pd

api = TdxHq_API()
if api.connect("180.153.18.172", 80):
    api.setup()

    # 获取日K数据
    data_1d = api.get_security_bars(9, 0, "300046", 0, 5)
    df = pd.DataFrame(data_1d)

    print("=" * 70)
    print("PyTdx 日K原始数据（300046 台基股份）:")
    print("=" * 70)
    for _, row in df.iterrows():
        vol = row.get('vol', 0)
        amount = row.get('amount', 0)
        print(f"日期: {row['datetime']}  vol: {vol:>10}  amount: {amount:>15}")

    print("\n" + "=" * 70)
    print("验证：")
    # 成交额(元) / 成交量(手) = 平均价(元)
    # 如果 vol 是手，则 amount/vol ≈ 股价
    # 如果 vol 是股，则 amount/(vol/100) ≈ 股价

    for _, row in df.iterrows():
        vol = row.get('vol', 0)
        amount = row.get('amount', 0)
        if vol > 0 and amount > 0:
            # 假设 vol 是手
            avg_price_lots = amount / vol
            # 假设 vol 是股
            avg_price_shares = amount / (vol / 100)

            print(f"日期: {row['datetime']}")
            print(f"  假设 vol 是手: 成交额{amount:.0f} / {vol}手 = {avg_price_lots:.2f} 元/手")
            print(f"  假设 vol 是股: 成交额{amount:.0f} / {vol}股 = {avg_price_shares:.2f} 元/100股 = {avg_price_shares/100:.4f} 元/股")
            print()

    api.disconnect()
