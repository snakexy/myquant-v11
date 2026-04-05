"""检查 numpy/pandas 内存池状态"""
import numpy as np
import pandas as pd
import sys

def get_numpy_memory_info():
    """获取 numpy 内存信息"""
    print("=" * 80)
    print("NumPy 内存池分析")
    print("=" * 80)

    # 获取当前 numpy 的内存分配器信息
    try:
        # numpy 1.20+ 有这个属性
        if hasattr(np, 'memmap'):
            print(f"NumPy memmap: {np.memmap}")
    except:
        pass

    # 创建测试数组看看分配情况
    print("\n创建测试数组...")
    before = sys.getsizeof([])

    test_arr = np.zeros(1000000)  # 1M floats = 8MB
    after_arr = sys.getsizeof(test_arr)

    print(f"Python 看到的数组大小: {after_arr / 1024 / 1024:.2f} MB")
    print(f"实际占用: {test_arr.nbytes / 1024 / 1024:.2f} MB")
    print(f"差异: {(test_arr.nbytes - after_arr) / 1024 / 1024:.2f} MB")

    del test_arr

    # 检查 pandas
    print("\n" + "=" * 80)
    print("Pandas 内存分析")
    print("=" * 80)

    # 创建测试 DataFrame
    test_df = pd.DataFrame({
        'A': range(100000),
        'B': range(100000),
        'C': range(100000),
    })

    print(f"DataFrame 行数: {len(test_df)}")
    print(f"DataFrame 列数: {len(test_df.columns)}")
    print(f"Python 看到的对象大小: {sys.getsizeof(test_df) / 1024:.2f} KB")
    print(f"Pandas 报告的内存: {test_df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

    del test_df


def check_allocations():
    """检查内存分配情况"""
    import gc
    import psutil

    process = psutil.Process()
    gc.collect()

    before = process.memory_info().rss

    # 分配一些数据
    df = pd.DataFrame({
        'open': np.random.rand(10000),
        'high': np.random.rand(10000),
        'low': np.random.rand(10000),
        'close': np.random.rand(10000),
        'volume': np.random.rand(10000),
    })

    after = process.memory_info().rss

    print(f"\n分配前内存: {before / 1024 / 1024:.1f} MB")
    print(f"分配后内存: {after / 1024 / 1024:.1f} MB")
    print(f"增长: {(after - before) / 1024 / 1024:.1f} MB")
    print(f"Pandas 报告: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

    # 删除 DataFrame
    del df
    gc.collect()

    after_delete = process.memory_info().rss
    print(f"\n删除后内存: {after_delete / 1024 / 1024:.1f} MB")
    print(f"释放: {(after - after_delete) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    get_numpy_memory_info()
    check_allocations()
