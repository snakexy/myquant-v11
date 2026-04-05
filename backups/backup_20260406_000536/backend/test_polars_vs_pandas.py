"""验证 Polars 是否能解决内存泄漏问题"""
import gc
import psutil
import time
from datetime import datetime

def test_pandas_memory():
    """测试 pandas 内存行为"""
    print("=" * 80)
    print("测试 pandas 内存行为")
    print("=" * 80)

    import pandas as pd

    process = psutil.Process()
    gc.collect()

    # 基础内存
    base_memory = process.memory_info().rss / 1024 / 1024
    print(f"基础内存: {base_memory:.1f} MB")

    # 模拟你的使用场景：重复创建和删除 DataFrame
    for i in range(10):
        # 创建 DataFrame（模拟获取 K线数据）
        df = pd.DataFrame({
            'datetime': pd.date_range('2020-01-01', periods=1000, freq='D'),
            'open': range(1000),
            'high': range(1000),
            'low': range(1000),
            'close': range(1000),
            'volume': range(1000),
        })

        # 转换为字典列表（模拟发送给前端）
        items = df.to_dict('records')

        # 删除 DataFrame
        del df, items
        gc.collect()

        if i % 5 == 0:
            current_memory = process.memory_info().rss / 1024 / 1024
            print(f"第 {i} 轮后: {current_memory:.1f} MB (增长: {current_memory - base_memory:.1f} MB)")

    final_memory = process.memory_info().rss / 1024 / 1024
    print(f"\n最终内存: {final_memory:.1f} MB")
    print(f"总增长: {final_memory - base_memory:.1f} MB")


def test_polars_memory():
    """测试 Polars 内存行为"""
    print("\n" + "=" * 80)
    print("测试 Polars 内存行为")
    print("=" * 80)

    import polars as pl

    process = psutil.Process()
    gc.collect()

    # 基础内存
    base_memory = process.memory_info().rss / 1024 / 1024
    print(f"基础内存: {base_memory:.1f} MB")

    # 模拟同样的使用场景
    for i in range(10):
        # 创建 DataFrame（使用列表避免 date_range 问题）
        df = pl.DataFrame({
            'datetime': [datetime(2020, 1, 1) for _ in range(1000)],
            'open': range(1000),
            'high': range(1000),
            'low': range(1000),
            'close': range(1000),
            'volume': range(1000),
        })

        # 转换为字典列表
        items = df.to_dicts()

        # 删除
        del df, items
        gc.collect()

        if i % 5 == 0:
            current_memory = process.memory_info().rss / 1024 / 1024
            print(f"第 {i} 轮后: {current_memory:.1f} MB (增长: {current_memory - base_memory:.1f} MB)")

    final_memory = process.memory_info().rss / 1024 / 1024
    print(f"\n最终内存: {final_memory:.1f} MB")
    print(f"总增长: {final_memory - base_memory:.1f} MB")


def test_mixed_scenario():
    """测试混合场景：pandas + Polars"""
    print("\n" + "=" * 80)
    print("测试混合场景")
    print("=" * 80)

    process = psutil.Process()
    gc.collect()

    base_memory = process.memory_info().rss / 1024 / 1024
    print(f"基础内存: {base_memory:.1f} MB")

    # 先用 pandas 创建一些数据
    import pandas as pd
    df_pd = pd.DataFrame({'value': range(1000)})
    del df_pd
    gc.collect()

    mem1 = process.memory_info().rss / 1024 / 1024
    print(f"pandas 操作后: {mem1:.1f} MB")

    # 再用 polars
    import polars as pl
    df_pl = pl.DataFrame({'value': range(1000)})
    del df_pl
    gc.collect()

    mem2 = process.memory_info().rss / 1024 / 1024
    print(f"polars 操作后: {mem2:.1f} MB")


if __name__ == "__main__":
    test_pandas_memory()
    test_polars_memory()
    test_mixed_scenario()
