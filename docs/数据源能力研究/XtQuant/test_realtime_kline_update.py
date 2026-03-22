"""
高级场景测试2: 实时K线更新

测试目标：
1. 盘中实时数据更新
2. 订阅推送机制
3. 更新频率验证
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import time
from datetime import datetime

symbol = '600519.SH'

print("="*80)
print("场景2: 实时K线更新")
print("="*80)
print(f"股票: {symbol}")
print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 检查是否交易时间
def is_trading_time():
    now = datetime.now()
    current_time = now.strftime('%H%M%S')

    # 交易时间: 9:30-11:30, 13:00-15:00
    morning = '093000' <= current_time <= '113000'
    afternoon = '130000' <= current_time <= '150000'

    return morning or afternoon

trading = is_trading_time()
print(f"是否交易时间: {'是' if trading else '否'}")
print()

if not trading:
    print("[WARNING] 当前不是交易时间，实时更新测试可能无法看到数据变化")
    print("         建议在9:30-15:00之间运行此测试")
    print()

# ===== 测试1: 订阅 + 多次获取 =====
print("[测试1] 订阅股票，多次获取查看实时更新")
print("-"*80)

try:
    # 1. 订阅
    print("步骤1: 订阅股票...")
    xtdata.subscribe_quote(
        stock_code=symbol,
        period='1d',
        count=0
    )
    print("   [OK] 订阅成功")

    # 等待订阅生效
    time.sleep(1)

    # 2. 多次获取（每隔5秒）
    print("步骤2: 每隔5秒获取一次，共10次...")
    print()

    quotes_history = []
    for i in range(10):
        # 获取订阅缓存
        tick_data = xtdata.get_full_tick([symbol])

        if symbol in tick_data:
            data = tick_data[symbol]
            price = data.get('lastPrice', 0)
            volume = data.get('volume', 0)

            timestamp = datetime.now().strftime('%H:%M:%S')
            quotes_history.append({
                'time': timestamp,
                'price': price,
                'volume': volume
            })

            print(f"   [{timestamp}] 价格: {price:.2f}, 成交量: {volume}")

        time.sleep(5)

    # 3. 分析数据
    print()
    print("步骤3: 数据分析...")

    if quotes_history:
        prices = [q['price'] for q in quotes_history]
        volumes = [q['volume'] for q in quotes_history]

        price_changed = len(set(prices)) > 1
        volume_changed = len(set(volumes)) > 1

        print(f"   价格变化: {'是' if price_changed else '否'}")
        print(f"   成交量变化: {'是' if volume_changed else '否'}")

        if price_changed:
            print(f"   最高价: {max(prices):.2f}")
            print(f"   最低价: {min(prices):.2f}")
            print(f"   价格波动: {max(prices) - min(prices):.2f}")

        if trading:
            if price_changed or volume_changed:
                print("   [OK] 实时更新正常：数据在变化")
            else:
                print("   [WARNING] 数据未变化（可能是非交易时间或市场静止）")
        else:
            print("   [INFO] 非交易时间，数据不变化是正常的")

except Exception as e:
    print(f"[ERROR] 异常: {e}")
    import traceback
    traceback.print_exc()

print()

# ===== 测试2: get_full_kline 实时快照 =====
print("[测试2] get_full_kline() - 获取最新K线快照")
print("-"*80)

try:
    # 多次获取最新K线
    print("每隔5秒获取一次最新K线，共5次...")
    print()

    kline_history = []
    for i in range(5):
        data = xtdata.get_full_kline(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period='1d',
            count=1,
            dividend_type='none',
            fill_data=True
        )

        if symbol in data:
            df = data[symbol]
            if len(df) > 0:
                kline = {
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'open': df['open'].iloc[-1],
                    'high': df['high'].iloc[-1],
                    'low': df['low'].iloc[-1],
                    'close': df['close'].iloc[-1],
                    'volume': df['volume'].iloc[-1]
                }
                kline_history.append(kline)

                print(f"   [{kline['time']}] 开:{kline['open']:.2f} 高:{kline['high']:.2f} "
                      f"低:{kline['low']:.2f} 收:{kline['close']:.2f} 量:{kline['volume']}")

        time.sleep(5)

    # 分析
    print()
    if kline_history:
        closes = [k['close'] for k in kline_history]

        if len(set(closes)) > 1:
            print("[OK] K线实时更新：收盘价在变化")
        else:
            print("[INFO] K线未变化（可能是非交易时间）")

except Exception as e:
    print(f"[ERROR] 异常: {e}")

print()
print("="*80)
print("结论:")
print("- subscribe_quote() + get_full_tick() 适合获取实时报价")
print("- get_full_kline() 适合获取最新K线快照")
print("- 盘中数据会实时更新，收盘后数据稳定")
print("="*80)
