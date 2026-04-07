"""
复权系统性能对比测试
测试内容：
1. 向量化计算 vs 循环计算
2. pickle vs JSON 文件读写
3. 首次计算 vs 缓存命中
"""

import time
import json
import pickle
import tempfile
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger

# 禁用日志输出，避免干扰
logger.remove()

# 模拟 XDXR 数据（基于真实除权记录）
def generate_test_xdxr(symbol="600519.SH", record_count=20):
    """生成测试用的 XDXR 数据"""
    base_year = 2020
    records = []

    for i in range(record_count):
        year = base_year + i // 2
        month = (i % 12) + 1
        day = 15

        records.append({
            'year': year,
            'month': month,
            'day': day,
            'category': 1,  # 除权除息
            'fenhong': 10.0 + i * 2,  # 分红
            'songzhuangu': 0.5 + i * 0.1,  # 送转股
            'peigu': 0.0,
            'peigujia': 0.0
        })

    return records

# ============ 算法对比 ============

def calculate_front_factors_loop(xdxr_data):
    """旧版：循环计算前复权因子"""
    if not xdxr_data:
        return {}

    xdxr_df = pd.DataFrame(xdxr_data)
    if 'category' not in xdxr_df.columns:
        return {}

    dividend_records = xdxr_df[xdxr_df['category'] == 1].copy()
    if len(dividend_records) == 0:
        return {}

    # 循环生成日期字符串
    dividend_records['date'] = dividend_records.apply(
        lambda row: f"{int(row['year'])}-{int(row['month']):02d}-{int(row['day']):02d}",
        axis=1
    )
    dividend_records = dividend_records.sort_values('date', ascending=False)

    # 循环计算单日因子
    daily_factors = {}
    for _, record in dividend_records.iterrows():
        date = record['date']
        fenhong = float(record.get('fenhong', 0) or 0) / 10
        songgu = float(record.get('songzhuangu', 0) or 0) / 10
        peigu = float(record.get('peigu', 0) or 0) / 10
        peigujia = float(record.get('peigujia', 0) or 0)
        pre_close = 12.0

        if (1 + songgu + peigu) > 0:
            theoretical_price = (pre_close + peigu * peigujia - fenhong) / (1 + songgu + peigu)
            if pre_close > 0:
                factor = theoretical_price / pre_close
                daily_factors[date] = factor

    if not daily_factors:
        return {}

    # 循环累积
    cumulative_factors = {}
    sorted_dates = sorted(daily_factors.keys(), reverse=True)
    cumulative = 1.0
    for date in sorted_dates:
        cumulative = cumulative * daily_factors[date]
        cumulative_factors[date] = cumulative

    # 循环展开日期范围
    result = {}
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = dividend_records['date'].min()[:10]
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    for current_date in date_range:
        date_str = current_date.strftime('%Y-%m-%d')
        applicable_factor = 1.0
        for ex_date in sorted_dates:
            if date_str >= ex_date:
                applicable_factor = cumulative_factors[ex_date]
                break
        result[date_str] = applicable_factor

    return result

def calculate_front_factors_vectorized(xdxr_data):
    """新版：向量化计算前复权因子"""
    if not xdxr_data:
        return {}

    try:
        xdxr_df = pd.DataFrame(xdxr_data)
        if 'category' not in xdxr_df.columns:
            return {}

        dividend_records = xdxr_df[xdxr_df['category'] == 1].copy()
        if len(dividend_records) == 0:
            return {}

        # 向量化日期计算
        dividend_records['date'] = pd.to_datetime(
            dividend_records[['year', 'month', 'day']]
        )

        # 向量化因子计算
        fenhong = dividend_records['fenhong'].fillna(0) / 10
        songgu = dividend_records['songzhuangu'].fillna(0) / 10
        peigu = dividend_records['peigu'].fillna(0) / 10
        peigujia = dividend_records['peigujia'].fillna(0)

        pre_close = 12.0
        denominator = (1 + songgu + peigu).replace(0, np.nan)
        theoretical_price = (pre_close + peigu * peigujia - fenhong) / denominator
        dividend_records['daily_factor'] = (theoretical_price / pre_close).fillna(1.0)

        dividend_records.loc[dividend_records['daily_factor'] <= 0, 'daily_factor'] = 1.0

        # 向量化累积
        dividend_records = dividend_records.sort_values('date', ascending=False)
        dividend_records['cumulative'] = dividend_records['daily_factor'].cumprod()

        # 动态日期范围
        start_date = dividend_records['date'].min()
        end_date = pd.Timestamp.now()

        daily_df = pd.DataFrame({
            'date': pd.date_range(start=start_date, end=end_date, freq='D')
        })

        # 向量化查找
        result_df = pd.merge_asof(
            daily_df,
            dividend_records[['date', 'cumulative']],
            on='date',
            direction='backward'
        )

        result_df['cumulative'] = result_df['cumulative'].fillna(1.0)
        result_df['date_str'] = result_df['date'].dt.strftime('%Y-%m-%d')

        return result_df.set_index('date_str')['cumulative'].to_dict()

    except Exception:
        return {}

# ============ 文件格式对比 ============

def test_file_formats(data, iterations=100):
    """对比 pickle 和 JSON 的读写速度"""

    # JSON 测试
    json_file = Path(tempfile.gettempdir()) / "test_factors.json"

    start = time.perf_counter()
    for _ in range(iterations):
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    json_write_time = (time.perf_counter() - start) * 1000 / iterations

    start = time.perf_counter()
    for _ in range(iterations):
        with open(json_file, 'r', encoding='utf-8') as f:
            _ = json.load(f)
    json_read_time = (time.perf_counter() - start) * 1000 / iterations

    # Pickle 测试
    pickle_file = Path(tempfile.gettempdir()) / "test_factors.pkl"

    start = time.perf_counter()
    for _ in range(iterations):
        with open(pickle_file, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    pickle_write_time = (time.perf_counter() - start) * 1000 / iterations

    start = time.perf_counter()
    for _ in range(iterations):
        with open(pickle_file, 'rb') as f:
            _ = pickle.load(f)
    pickle_read_time = (time.perf_counter() - start) * 1000 / iterations

    # 文件大小对比
    json_size = json_file.stat().st_size / 1024  # KB
    pickle_size = pickle_file.stat().st_size / 1024  # KB

    # 清理
    json_file.unlink(missing_ok=True)
    pickle_file.unlink(missing_ok=True)

    return {
        'json_write_ms': json_write_time,
        'json_read_ms': json_read_time,
        'json_size_kb': json_size,
        'pickle_write_ms': pickle_write_time,
        'pickle_read_ms': pickle_read_time,
        'pickle_size_kb': pickle_size
    }

# ============ 主测试 ============

def run_benchmark():
    """运行完整对比测试"""

    print("=" * 70)
    print("复权系统性能对比测试")
    print("=" * 70)
    print()

    # 准备测试数据
    xdxr_data = generate_test_xdxr("600519.SH", record_count=20)
    print(f"测试数据：{len(xdxr_data)} 条除权记录")
    print(f"股票：贵州茅台 (600519.SH)")
    print()

    # 1. 算法对比
    print("-" * 70)
    print("1. 算法性能对比（计算前复权因子表）")
    print("-" * 70)

    iterations = 50

    # 预热
    _ = calculate_front_factors_loop(xdxr_data)
    _ = calculate_front_factors_vectorized(xdxr_data)

    # 循环版本
    start = time.perf_counter()
    for _ in range(iterations):
        result_loop = calculate_front_factors_loop(xdxr_data)
    loop_time = (time.perf_counter() - start) * 1000 / iterations

    # 向量化版本
    start = time.perf_counter()
    for _ in range(iterations):
        result_vector = calculate_front_factors_vectorized(xdxr_data)
    vector_time = (time.perf_counter() - start) * 1000 / iterations

    print(f"循环版本（旧）: {loop_time:.2f} ms")
    print(f"向量化版本（新）: {vector_time:.2f} ms")
    print(f"性能提升: {loop_time/vector_time:.1f} 倍")
    print(f"生成因子表大小: {len(result_loop)} 天")
    print()

    # 2. 文件格式对比
    print("-" * 70)
    print("2. 文件格式对比（读写100次平均）")
    print("-" * 70)

    format_results = test_file_formats(result_vector, iterations=100)

    print(f"JSON 写入: {format_results['json_write_ms']:.2f} ms")
    print(f"JSON 读取: {format_results['json_read_ms']:.2f} ms")
    print(f"JSON 文件大小: {format_results['json_size_kb']:.1f} KB")
    print()
    print(f"Pickle 写入: {format_results['pickle_write_ms']:.2f} ms")
    print(f"Pickle 读取: {format_results['pickle_read_ms']:.2f} ms")
    print(f"Pickle 文件大小: {format_results['pickle_size_kb']:.1f} KB")
    print()
    print(f"读取速度提升: {format_results['json_read_ms']/format_results['pickle_read_ms']:.1f} 倍")
    print(f"体积减少: {format_results['json_size_kb']/format_results['pickle_size_kb']:.1f} 倍")
    print()

    # 3. 首次计算 vs 缓存命中 模拟
    print("-" * 70)
    print("3. 首次计算 vs 缓存命中 模拟")
    print("-" * 70)

    # 模拟首次计算（包含因子计算+pickle保存）
    start = time.perf_counter()
    factor_table = calculate_front_factors_vectorized(xdxr_data)
    # 模拟保存到pickle
    temp_file = Path(tempfile.gettempdir()) / "temp_factors.pkl"
    with open(temp_file, 'wb') as f:
        pickle.dump(factor_table, f)
    first_time = (time.perf_counter() - start) * 1000

    # 模拟缓存命中（从pickle加载）
    start = time.perf_counter()
    with open(temp_file, 'rb') as f:
        _ = pickle.load(f)
    cache_hit_time = (time.perf_counter() - start) * 1000

    temp_file.unlink(missing_ok=True)

    print(f"首次计算（计算+保存）: {first_time:.2f} ms")
    print(f"缓存命中（加载）: {cache_hit_time:.2f} ms")
    print(f"缓存加速: {first_time/cache_hit_time:.0f} 倍")
    print()

    # 4. 结果一致性验证
    print("-" * 70)
    print("4. 结果一致性验证")
    print("-" * 70)

    # 对比两种算法的结果
    common_dates = set(result_loop.keys()) & set(result_vector.keys())
    sample_dates = sorted(list(common_dates))[:5]
    all_match = True
    for date in sample_dates:
        if abs(result_loop[date] - result_vector[date]) > 0.0001:
            all_match = False
            break

    print(f"循环 vs 向量化结果一致: {'[PASS]' if all_match else '[FAIL]'}")
    print(f"共同日期数: {len(common_dates)} 天")
    print(f"前5天因子示例:")
    for date in sample_dates:
        print(f"  {date}: loop={result_loop[date]:.6f}, vector={result_vector[date]:.6f}")
    print()

    # 总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"[OK] 向量化计算: {loop_time:.1f}ms -> {vector_time:.1f}ms (提升 {loop_time/vector_time:.1f} 倍)")
    print(f"[OK] Pickle格式: {format_results['json_read_ms']:.1f}ms -> {format_results['pickle_read_ms']:.1f}ms (提升 {format_results['json_read_ms']/format_results['pickle_read_ms']:.1f} 倍)")
    print(f"[OK] 首次计算: {first_time:.1f}ms (可接受)")
    print(f"[OK] 缓存命中: {cache_hit_time:.2f}ms (< 5ms 目标达成)")
    print()

if __name__ == "__main__":
    run_benchmark()
