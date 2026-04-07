"""检查 pytdx 原始返回的成交量"""
from pytdx2.hq import TdxHq_API

api = TdxHq_API()
if api.connect("180.153.18.172", 80):
    api.setup()

    # 获取 5m 数据
    data_5m = api.get_security_bars(0, 0, "300046", 0, 3)
    print("=" * 60)
    print("PyTdx 5m 原始数据（前3条）:")
    print("=" * 60)
    for bar in data_5m:
        print(f"日期: {bar.get('datetime')}  成交量(vol): {bar.get('vol')}")

    # 获取日K数据
    data_1d = api.get_security_bars(9, 0, "300046", 0, 3)
    print("\n" + "=" * 60)
    print("PyTdx 1d 原始数据（前3条）:")
    print("=" * 60)
    for bar in data_1d:
        print(f"日期: {bar.get('datetime')}  成交量(vol): {bar.get('vol')}")

    api.disconnect()
