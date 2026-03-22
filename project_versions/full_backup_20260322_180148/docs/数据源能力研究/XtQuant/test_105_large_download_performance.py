# -*- coding: utf-8 -*-
"""
测试大量数据下载性能

目的:
1. 测试批量下载多只股票的性能
2. 测试是否有并发限制
3. 测试是否有频率限制
4. 评估实际使用场景的可行性
"""

from xtquant import xtdata
import time
import threading

def test_batch_download():
    """测试批量下载性能"""

    print("=" * 80)
    print("测试: 大量数据下载性能")
    print("=" * 80)
    print()

    # 测试不同规模
    test_cases = [
        {'count': 10, 'name': '小规模（10只）'},
        {'count': 50, 'name': '中规模（50只）'},
        {'count': 100, 'name': '较大规模（100只）'},
        {'count': 300, 'name': '大规模（300只）'},
    ]

    for case in test_cases:
        print(f"\n{'='*80}")
        print(f"[测试] {case['name']}")
        print(f"{'='*80}")

        # 生成股票列表
        symbols = [f"60{i:04d}.SH" for i in range(1, case['count'] + 1)]
        print(f"股票数量: {len(symbols)}")
        print(f"时间范围: 20240101 - 20240131 (1个月)")
        print()

        # 开始计时
        start_time = time.time()
        success_count = 0
        fail_count = 0

        for i, symbol in enumerate(symbols, 1):
            try:
                # 下载日K线数据
                xtdata.download_history_data(
                    stock_code=symbol,
                    period='1d',
                    start_time='20240101',
                    end_time='20240131'
                )
                success_count += 1

                # 每下载50只显示进度
                if i % 50 == 0:
                    elapsed = time.time() - start_time
                    print(f"[进度] 已下载 {i}/{len(symbols)} 只，"
                          f"耗时: {elapsed:.1f}秒，"
                          f"成功: {success_count}")

            except Exception as e:
                fail_count += 1
                if fail_count <= 5:  # 只显示前5个错误
                    print(f"[ERROR] {symbol} 下载失败: {e}")

        # 统计结果
        total_time = time.time() - start_time
        avg_time = total_time / len(symbols)

        print()
        print(f"[结果] 总耗时: {total_time:.1f}秒")
        print(f"[结果] 平均每只: {avg_time:.3f}秒")
        print(f"[结果] 成功: {success_count}，失败: {fail_count}")
        print(f"[结果] 速度: {len(symbols)/total_time:.2f} 只/秒")
        print()


def test_concurrent_download():
    """测试并发下载（多线程）"""

    print("=" * 80)
    print("测试: 并发下载性能（多线程）")
    print("=" * 80)
    print()

    symbols = [f"60{i:04d}.SH" for i in range(1, 51)]  # 50只
    print(f"股票数量: {len(symbols)}")
    print(f"线程数: 4")
    print()

    start_time = time.time()

    def download_worker(symbols_chunk):
        """下载worker"""
        results = {'success': 0, 'fail': 0}
        for symbol in symbols_chunk:
            try:
                xtdata.download_history_data(
                    stock_code=symbol,
                    period='1d',
                    start_time='20240101',
                    end_time='20240131'
                )
                results['success'] += 1
            except:
                results['fail'] += 1
        return results

    # 分成4份
    chunk_size = len(symbols) // 4
    chunks = [
        symbols[i:i+chunk_size]
        for i in range(0, len(symbols), chunk_size)
    ]

    # 创建线程
    threads = []
    for chunk in chunks:
        thread = threading.Thread(target=download_worker, args=(chunk,))
        threads.append(thread)
        thread.start()

    # 等待完成
    for thread in threads:
        thread.join()

    total_time = time.time() - start_time

    print(f"[结果] 总耗时: {total_time:.1f}秒")
    print(f"[结果] 速度: {len(symbols)/total_time:.2f} 只/秒")
    print()


def test_frequency_limit():
    """测试频率限制"""

    print("=" * 80)
    print("测试: 频率限制（连续快速调用）")
    print("=" * 80)
    print()

    symbol = '600519.SH'
    test_count = 20

    print(f"测试股票: {symbol}")
    print(f"连续下载次数: {test_count}")
    print()

    times = []
    errors = []

    for i in range(test_count):
        start = time.time()

        try:
            xtdata.download_history_data(
                stock_code=symbol,
                period='1d',
                start_time='20240101',
                end_time='20240110'
            )
            elapsed = time.time() - start
            times.append(elapsed)

        except Exception as e:
            errors.append(str(e))
            elapsed = time.time() - start
            times.append(elapsed)

        # 短暂延迟（模拟实际使用）
        time.sleep(0.1)

    # 统计
    print(f"[成功] {len(times) - len(errors)} 次")
    print(f"[失败] {len(errors)} 次")

    if errors:
        print(f"[错误示例]")
        for error in errors[:3]:
            print(f"  - {error}")

    print()
    print(f"[耗时统计]")
    print(f"  总耗时: {sum(times):.2f}秒")
    print(f"  平均: {sum(times)/len(times):.3f}秒/次")
    print(f"  最快: {min(times):.3f}秒")
    print(f"  最慢: {max(times):.3f}秒")
    print()


def test_download_then_read():
    """测试下载+读取的完整流程性能"""

    print("=" * 80)
    print("测试: 下载+读取完整流程")
    print("=" * 80)
    print()

    symbols = [f"60{i:04d}.SH" for i in range(1, 101)]  # 100只
    print(f"股票数量: {len(symbols)}")
    print()

    # 阶段1: 下载
    print("[阶段1] 批量下载")
    download_start = time.time()

    for symbol in symbols:
        try:
            xtdata.download_history_data(
                stock_code=symbol,
                period='1d',
                start_time='20240101',
                end_time='20240131'
            )
        except:
            pass

    download_time = time.time() - download_start
    print(f"  下载耗时: {download_time:.1f}秒")
    print(f"  平均: {download_time/len(symbols):.3f}秒/只")
    print()

    # 阶段2: 读取
    print("[阶段2] 批量读取")
    read_start = time.time()

    read_success = 0
    for symbol in symbols:
        try:
            data = xtdata.get_market_data_ex(
                stock_list=[symbol],
                period='1d',
                start_time=20240101,
                end_time=20240131,
                count=0
            )
            if data and symbol in data:
                read_success += 1
        except:
            pass

    read_time = time.time() - read_start
    print(f"  读取耗时: {read_time:.1f}秒")
    print(f"  成功: {read_success}/{len(symbols)}")
    print(f"  平均: {read_time/len(symbols):.3f}秒/只")
    print()

    # 总结
    total_time = download_time + read_time
    print(f"[总结] 完整流程耗时: {total_time:.1f}秒")
    print(f"  - 下载: {download_time:.1f}秒 ({download_time/total_time*100:.1f}%)")
    print(f"  - 读取: {read_time:.1f}秒 ({read_time/total_time*100:.1f}%)")
    print()


if __name__ == '__main__':
    try:
        # 测试1: 不同规模的批量下载
        test_batch_download()

        print("\n" + "="*80 + "\n")

        # 测试2: 并发下载
        test_concurrent_download()

        print("\n" + "="*80 + "\n")

        # 测试3: 频率限制
        test_frequency_limit()

        print("\n" + "="*80 + "\n")

        # 测试4: 下载+读取完整流程
        test_download_then_read()

        print("="*80)
        print("[测试完成]")
        print("="*80)

    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
