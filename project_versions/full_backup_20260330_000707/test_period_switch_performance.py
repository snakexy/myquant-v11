# -*- coding: utf-8 -*-
"""
测试切换 K线周期的性能瓶颈

模拟前端切换周期，分析每个步骤的耗时
"""
import time
import sys
from pathlib import Path

# 添加 backend 路径
backend_path = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from myquant.core.market.services import get_seamless_kline_service

# 测试参数
TEST_SYMBOL = "600000.SH"
TEST_COUNT = 100
PERIODS = ["1d", "5m", "1m", "15m", "30m"]


def test_period_switch():
    """测试周期切换性能"""
    print("=" * 70)
    print("K线周期切换性能测试")
    print("=" * 70)
    print("股票: {}, 数量: {}".format(TEST_SYMBOL, TEST_COUNT))
    print("测试周期: {}".format(', '.join(PERIODS)))
    print()

    service = get_seamless_kline_service()

    # 第一次请求（冷启动）
    print("[1] 第一次请求（冷启动）- {}".format(PERIODS[0]))
    print("-" * 70)
    start = time.time()
    df1 = service.get_kline(
        symbol=TEST_SYMBOL,
        period=PERIODS[0],
        count=TEST_COUNT,
        adjust_type='none'
    )
    elapsed1 = time.time() - start
    print("耗时: {:.2f} ms, 数据量: {} 条".format(elapsed1 * 1000, len(df1)))
    print()

    # 切换到其他周期
    for i, period in enumerate(PERIODS[1:], 1):
        print("[{}] 切换到 {}".format(i + 1, period))
        print("-" * 70)

        start = time.time()
        df = service.get_kline(
            symbol=TEST_SYMBOL,
            period=period,
            count=TEST_COUNT,
            adjust_type='none'
        )
        elapsed = time.time() - start
        print("耗时: {:.2f} ms, 数据量: {} 条".format(elapsed * 1000, len(df)))

        # 显示时间范围
        if not df.empty:
            print("时间范围: {} 至 {}".format(
                df['datetime'].iloc[0], df['datetime'].iloc[-1]
            ))
        print()

    # 再次切换回第一个周期（测试缓存）
    print("[{}] 再次请求 {} (测试缓存)".format(len(PERIODS) + 1, PERIODS[0]))
    print("-" * 70)
    start = time.time()
    df_cached = service.get_kline(
        symbol=TEST_SYMBOL,
        period=PERIODS[0],
        count=TEST_COUNT,
        adjust_type='none'
    )
    elapsed_cached = time.time() - start
    print("耗时: {:.2f} ms, 数据量: {} 条".format(elapsed_cached * 1000, len(df_cached)))
    print()

    # 总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    print("第一次请求（{}）: {:.2f} ms".format(PERIODS[0], elapsed1 * 1000))
    print("缓存请求（{}）: {:.2f} ms".format(PERIODS[0], elapsed_cached * 1000))
    if elapsed_cached < elapsed1:
        print("缓存加速: {:.1f}%".format((1 - elapsed_cached / elapsed1) * 100))
    else:
        print("缓存未生效（可能TTL过期）")


if __name__ == "__main__":
    test_period_switch()
