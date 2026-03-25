"""测试 pytdx get_finance_info 是否能拿到流通股本"""
from pytdx.hq import TdxHq_API

api = TdxHq_API()
with api.connect('119.147.212.81', 7709):
    info = api.get_finance_info(1, '600519')
    print(f"finance_info: {info}")

    quotes = api.get_security_quotes([(1, '600519')])
    if quotes:
        q = quotes[0]
        print(f"vol: {q.get('vol')}")
        if info:
            ltb = info.get('liutongguben', 0)
            vol = q.get('vol', 0)
            print(f"liutongguben = {ltb} (万股)")
            print(f"vol = {vol} (手)")
            if ltb > 0:
                tr = (vol * 100) / ltb * 100
                print(f"turnover_rate = {tr:.2f}%")
            else:
                print("liutongguben is 0, cannot calculate turnover_rate")
