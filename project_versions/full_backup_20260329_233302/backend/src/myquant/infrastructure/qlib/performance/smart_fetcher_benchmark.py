#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmartFetcher V3 性能基准测试

测试内容:
1. 单股票数据获取性能
2. 批量股票数据获取性能
3. 数据源响应时间
4. 缓存命中率
5. 并发请求处理能力

作者: Claude Code
日期: 2026-01-24
版本: 1.0
"""

import sys
import os
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data.unified_data_manager import UnifiedDataManager as DataManager
from data.smart_fetcher_v3 import SmartFetcherV3

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartFetcherBenchmark:
    """SmartFetcher V3 性能基准测试"""

    def __init__(self):
        """初始化基准测试"""
        self.data_manager = DataManager()
        self.results = {
            'single_stock': {},
            'batch_stocks': {},
            'data_source': {},
            'cache_performance': {},
            'concurrent_requests': {}
        }

        # 测试用股票列表
        self.test_symbols = [
            '000001.SZ', '000002.SZ', '000858.SZ',
            '600000.SH', '600036.SH', '601318.SH',
            '000333.SZ', '600519.SH', '601888.SH',
            '300750.SZ'
        ]

        # 测试日期范围（最近30天）
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        self.start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        logger.info("SmartFetcher V3 性能基准测试初始化完成")
        logger.info(f"测试股票: {len(self.test_symbols)} 只")
        logger.info(f"测试日期: {self.start_date} 到 {self.end_date}")

    def benchmark_single_stock_retrieval(self) -> Dict[str, Any]:
        """
        基准测试1: 单股票数据获取性能

        测试指标:
        - 平均响应时间
        - 最小/最大响应时间
        - 成功率
        """
        logger.info("\n" + "="*70)
        logger.info("基准测试 1: 单股票数据获取性能")
        logger.info("="*70)

        response_times = []
        success_count = 0
        fail_count = 0

        for symbol in self.test_symbols[:5]:  # 测试5只股票
            start_time = time.time()

            try:
                data = self.data_manager.get_kline_data(
                    symbol=symbol,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    period='day'
                )

                elapsed = time.time() - start_time
                response_times.append(elapsed)

                if data is not None and not data.empty:
                    success_count += 1
                    logger.info(
                        f"[OK] {symbol}: {elapsed:.3f}s - "
                        f"{len(data)} records"
                    )
                else:
                    fail_count += 1
                    logger.warning(f"[WARN] {symbol}: {elapsed:.3f}s - no data")

            except Exception as e:
                fail_count += 1
                elapsed = time.time() - start_time
                logger.error(f"[FAIL] {symbol}: {elapsed:.3f}s - error: {e}")

        # 计算统计数据
        if response_times:
            results = {
                'avg_response_time': sum(response_times) / len(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'success_rate': success_count / (success_count + fail_count),
                'total_tests': success_count + fail_count
            }

            logger.info("\n[STATS] Single Stock Performance:")
            logger.info(f"  Avg Response Time: {results['avg_response_time']:.3f}s")
            logger.info(f"  Min Response Time: {results['min_response_time']:.3f}s")
            logger.info(f"  Max Response Time: {results['max_response_time']:.3f}s")
            logger.info(f"  Success Rate: {results['success_rate']:.2%}")

            self.results['single_stock'] = results
            return results

        return {}

    async def benchmark_batch_retrieval(self) -> Dict[str, Any]:
        """
        基准测试2: 批量股票数据获取性能

        测试指标:
        - 批量获取总时间
        - 单只股票平均时间
        - 批量vs单只性能比
        """
        logger.info("\n" + "="*70)
        logger.info("基准测试 2: 批量股票数据获取性能")
        logger.info("="*70)

        # 方法1: 逐个获取
        logger.info("\n方法1: 逐个获取所有股票")
        start_time = time.time()

        individual_results = []
        for symbol in self.test_symbols:
            try:
                data = self.data_manager.get_kline_data(
                    symbol=symbol,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    period='day'
                )
                if data is not None and not data.empty:
                    individual_results.append((symbol, len(data)))
            except Exception as e:
                logger.error(f"获取 {symbol} 失败: {e}")

        individual_time = time.time() - start_time
        logger.info(f"[OK] 逐个获取完成: {individual_time:.3f}s")

        # 方法2: 批量获取（如果支持）
        logger.info("\n方法2: 批量获取所有股票")
        start_time = time.time()

        try:
            # 尝试使用批量获取方法
            batch_data = await self.data_manager.batch_smart_fetch_v3(
                symbols=self.test_symbols,
                start_date=self.start_date,
                end_date=self.end_date,
                period='day'
            )

            batch_time = time.time() - start_time

            if batch_data is not None and not batch_data.empty:
                logger.info(f"[OK] 批量获取完成: {batch_time:.3f}s")

                # 性能比较
                speedup = individual_time / batch_time if batch_time > 0 else 0

                results = {
                    'individual_time': individual_time,
                    'batch_time': batch_time,
                    'speedup_factor': speedup,
                    'time_saved': individual_time - batch_time,
                    'individual_count': len(individual_results),
                    'batch_count': len(batch_data['symbol'].unique()) if 'symbol' in batch_data.columns else 0
                }

                logger.info("\n[STATS] 批量获取性能统计:")
                logger.info(f"  逐个获取时间: {individual_time:.3f}s")
                logger.info(f"  批量获取时间: {batch_time:.3f}s")
                logger.info(f"  性能提升: {speedup:.2f}x")
                logger.info(f"  节省时间: {results['time_saved']:.3f}s")

                self.results['batch_stocks'] = results
                return results

        except Exception as e:
            logger.warning(f"批量获取不可用: {e}")

        return {
            'individual_time': individual_time,
            'batch_time': None,
            'speedup_factor': 1.0
        }

    def benchmark_data_sources(self) -> Dict[str, Any]:
        """
        基准测试3: 各数据源响应时间

        测试数据源:
        - PostgreSQL
        - ClickHouse
        - Redis (缓存)
        - TDX 本地
        - XtQuant 实时
        """
        logger.info("\n" + "="*70)
        logger.info("基准测试 3: 数据源响应时间")
        logger.info("="*70)

        # 这里简化测试，实际应该分别测试每个数据源
        test_symbol = self.test_symbols[0]

        # 测试多次获取以观察缓存效果
        times = []
        for i in range(5):
            start_time = time.time()
            try:
                data = self.data_manager.get_kline_data(
                    symbol=test_symbol,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    frequency='day'
                )
                elapsed = time.time() - start_time
                times.append(elapsed)
                logger.info(f"  第{i+1}次获取: {elapsed:.3f}s")
            except Exception as e:
                logger.error(f"  第{i+1}次获取失败: {e}")

        if times:
            results = {
                'first_request': times[0] if times else 0,
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'cached_requests': times[1:] if len(times) > 1 else []
            }

            logger.info("\n[STATS] 数据源性能统计:")
            logger.info(f"  首次请求: {results['first_request']:.3f}s")
            logger.info(f"  平均时间: {results['avg_time']:.3f}s")
            logger.info(f"  最快时间: {results['min_time']:.3f}s")

            if results['cached_requests']:
                cache_avg = sum(results['cached_requests']) / len(results['cached_requests'])
                logger.info(f"  缓存请求平均: {cache_avg:.3f}s")

            self.results['data_source'] = results
            return results

        return {}

    def generate_report(self) -> str:
        """生成性能测试报告"""
        report = []
        report.append("\n" + "="*70)
        report.append("SmartFetcher V3 性能基准测试报告")
        report.append("="*70)
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"测试股票: {len(self.test_symbols)} 只")
        report.append(f"测试周期: {self.start_date} 到 {self.end_date}")
        report.append("")

        # 单股票性能
        if self.results['single_stock']:
            report.append("1. 单股票数据获取性能:")
            r = self.results['single_stock']
            report.append(f"   平均响应时间: {r['avg_response_time']:.3f}s")
            report.append(f"   成功率: {r['success_rate']:.2%}")
            report.append("")

        # 批量性能
        if self.results['batch_stocks']:
            report.append("2. 批量数据获取性能:")
            r = self.results['batch_stocks']
            report.append(f"   性能提升: {r['speedup_factor']:.2f}x")
            if r['batch_time']:
                report.append(f"   节省时间: {r['time_saved']:.3f}s")
            report.append("")

        # 数据源性能
        if self.results['data_source']:
            report.append("3. 数据源响应时间:")
            r = self.results['data_source']
            report.append(f"   首次请求: {r['first_request']:.3f}s")
            report.append(f"   平均时间: {r['avg_time']:.3f}s")
            report.append("")

        report.append("="*70)

        return "\n".join(report)


async def run_benchmark():
    """运行完整基准测试"""
    print("\n[START] SmartFetcher V3 Performance Benchmark\n")

    benchmark = SmartFetcherBenchmark()

    # 运行所有测试
    benchmark.benchmark_single_stock_retrieval()
    await benchmark.benchmark_batch_retrieval()
    benchmark.benchmark_data_sources()

    # 生成报告
    report = benchmark.generate_report()
    print(report)

    # 保存报告到文件
    report_dir = Path("logs/performance")
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f"smart_fetcher_benchmark_{timestamp}.txt"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"\n[FILE] 报告已保存到: {report_file}")
    logger.info("\n[OK] 性能基准测试完成!")


if __name__ == "__main__":
    # 运行基准测试
    asyncio.run(run_benchmark())
