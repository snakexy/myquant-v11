"""
跟踪误差控制详细测试

测试跟踪误差控制器的所有功能，包括动态跟踪误差限制和实时监控
"""

import unittest
import numpy as np
import pandas as pd
from datetime import timedelta
import sys
import os

# 添加项目根目录到路径
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', '..')
)
sys.path.insert(0, project_root)

from qlib_core.backtest.portfolio_management.strategy.enhanced_indexing.risk_management.tracking_error import TrackingErrorController


class TestTrackingErrorController(unittest.TestCase):
    """跟踪误差控制器详细测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.controller = TrackingErrorController(
            max_tracking_error=0.05,
            rebalance_threshold=0.02,
            verbose=True
        )
        
        # 创建测试数据
        self.n_assets = 50
        self.n_factors = 10
        
        # 创建因子暴露矩阵
        self.factor_exposure = np.random.randn(self.n_assets, self.n_factors)
        
        # 创建因子协方差矩阵
        self.factor_covariance = np.random.randn(self.n_factors, self.n_factors)
        self.factor_covariance = self.factor_covariance @ self.factor_covariance.T
        
        # 创建特定风险向量
        self.specific_risk = np.random.rand(self.n_assets) * 0.1 + 0.05
        
        # 创建投资组合权重
        self.portfolio_weights = np.random.rand(self.n_assets)
        self.portfolio_weights = self.portfolio_weights / np.sum(
            self.portfolio_weights
        )
        
        # 创建基准权重
        self.benchmark_weights = np.random.rand(self.n_assets)
        self.benchmark_weights = self.benchmark_weights / np.sum(
            self.benchmark_weights
        )
    
    def test_initialization(self):
        """测试初始化"""
        controller = TrackingErrorController(
            max_tracking_error=0.03,
            rebalance_threshold=0.01,
            verbose=False
        )
        
        self.assertEqual(controller.max_tracking_error, 0.03)
        self.assertEqual(controller.rebalance_threshold, 0.01)
        self.assertFalse(controller.verbose)
        self.assertEqual(len(controller.tracking_error_history), 0)
    
    def test_calculate_tracking_error_from_returns(self):
        """测试从收益率计算跟踪误差"""
        # 创建测试收益率序列
        dates = pd.date_range('2021-01-01', periods=100, freq='D')
        portfolio_returns = pd.Series(
            np.random.randn(100) * 0.01,
            index=dates
        )
        benchmark_returns = pd.Series(
            np.random.randn(100) * 0.01,
            index=dates
        )
        
        # 计算跟踪误差
        tracking_error = self.controller.calculate_tracking_error(
            portfolio_returns, benchmark_returns, annualize=True
        )
        
        # 验证结果
        self.assertIsInstance(tracking_error, float)
        self.assertGreater(tracking_error, 0)
        self.assertLess(tracking_error, 1.0)  # 合理范围内
        
        # 测试非年化
        tracking_error_non_annual = self.controller.calculate_tracking_error(
            portfolio_returns, benchmark_returns, annualize=False
        )
        
        # 年化应该大于非年化
        self.assertGreater(tracking_error, tracking_error_non_annual)
    
    def test_calculate_tracking_error_from_weights(self):
        """测试从权重计算跟踪误差"""
        tracking_error = self.controller.calculate_tracking_error_from_weights(
            self.portfolio_weights,
            self.benchmark_weights,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk,
            annualize=True
        )
        
        # 验证结果
        self.assertIsInstance(tracking_error, float)
        self.assertGreater(tracking_error, 0)
        self.assertLess(tracking_error, 1.0)  # 合理范围内
        
        # 测试相同权重的情况
        identical_tracking_error = self.controller.calculate_tracking_error_from_weights(
            self.portfolio_weights,
            self.portfolio_weights,  # 相同权重
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk,
            annualize=False
        )
        
        # 相同权重应该有很小的跟踪误差
        self.assertLess(identical_tracking_error, 0.1)
    
    def test_check_tracking_error_limit(self):
        """测试跟踪误差限制检查"""
        # 测试未超过限制
        within_limit = self.controller.check_tracking_error_limit(0.03)
        self.assertFalse(within_limit)
        
        # 测试超过限制
        exceeds_limit = self.controller.check_tracking_error_limit(0.06)
        self.assertTrue(exceeds_limit)
        
        # 测试边界情况
        at_limit = self.controller.check_tracking_error_limit(0.05)
        self.assertFalse(at_limit)  # 等于限制不算超过
    
    def test_should_rebalance(self):
        """测试再平衡判断"""
        # 测试超过限制的情况
        should_rebalance_1 = self.controller.should_rebalance(0.06)
        self.assertTrue(should_rebalance_1)
        
        # 测试变化超过阈值的情况
        should_rebalance_2 = self.controller.should_rebalance(
            current_tracking_error=0.03,
            previous_tracking_error=0.005
        )
        self.assertTrue(should_rebalance_2)
        
        # 测试不需要再平衡的情况
        should_rebalance_3 = self.controller.should_rebalance(
            current_tracking_error=0.03,
            previous_tracking_error=0.029
        )
        self.assertFalse(should_rebalance_3)
        
        # 测试无历史记录的情况
        should_rebalance_4 = self.controller.should_rebalance(0.03)
        self.assertFalse(should_rebalance_4)
    
    def test_tracking_error_contribution(self):
        """测试跟踪误差贡献计算"""
        factor_names = [f"factor_{i}" for i in range(self.n_factors)]
        
        contributions = self.controller.get_tracking_error_contribution(
            self.portfolio_weights,
            self.benchmark_weights,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk,
            factor_names
        )
        
        # 验证结果
        self.assertIsInstance(contributions, dict)
        self.assertEqual(len(contributions), self.n_factors + 1)  # +1 for idio
        
        # 验证所有贡献都是非负的
        for factor_name, contribution in contributions.items():
            self.assertGreaterEqual(contribution, 0)
        
        # 验证特定风险贡献存在
        self.assertIn("idiosyncratic", contributions)
        
        # 测试无因子名称的情况
        contributions_no_names = self.controller.get_tracking_error_contribution(
            self.portfolio_weights,
            self.benchmark_weights,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk
        )
        
        self.assertEqual(len(contributions_no_names), self.n_factors + 1)
    
    def test_tracking_error_history_update(self):
        """测试跟踪误差历史记录更新"""
        # 添加一些历史记录
        errors = [0.01, 0.02, 0.015, 0.025, 0.018]
        
        for i, error in enumerate(errors):
            timestamp = pd.Timestamp('2021-01-01') + timedelta(days=i)
            self.controller.update_tracking_error_history(error, timestamp)
        
        # 验证历史记录
        self.assertEqual(
            len(self.controller.tracking_error_history), 
            len(errors)
        )
        
        # 验证最新记录
        latest_record = self.controller.tracking_error_history[-1]
        self.assertEqual(latest_record['tracking_error'], errors[-1])
        
        # 测试自动时间戳
        self.controller.update_tracking_error_history(0.02)
        auto_timestamp_record = self.controller.tracking_error_history[-1]
        self.assertIsInstance(auto_timestamp_record['timestamp'], pd.Timestamp)
    
    def test_tracking_error_statistics(self):
        """测试跟踪误差统计信息"""
        # 添加一些历史记录
        errors = [0.01, 0.02, 0.015, 0.025, 0.018]
        
        for error in errors:
            self.controller.update_tracking_error_history(error)
        
        # 获取统计信息
        stats = self.controller.get_tracking_error_statistics()
        
        # 验证统计信息
        self.assertEqual(stats['count'], len(errors))
        self.assertAlmostEqual(stats['mean'], np.mean(errors), places=6)
        self.assertAlmostEqual(stats['std'], np.std(errors), places=6)
        self.assertAlmostEqual(stats['min'], np.min(errors), places=6)
        self.assertAlmostEqual(stats['max'], np.max(errors), places=6)
        self.assertAlmostEqual(stats['median'], np.median(errors), places=6)
        self.assertEqual(stats['current'], errors[-1])
        
        # 验证超限次数
        exceeds_count = sum(
            1 for e in errors if e > self.controller.max_tracking_error
        )
        self.assertEqual(stats['exceeds_limit'], exceeds_count)
        
        # 测试空历史记录
        empty_controller = TrackingErrorController()
        empty_stats = empty_controller.get_tracking_error_statistics()
        self.assertEqual(empty_stats, {})
    
    def test_dynamic_tracking_error_limit(self):
        """测试动态跟踪误差限制功能"""
        # 创建控制器
        dynamic_controller = TrackingErrorController(
            max_tracking_error=0.05,
            rebalance_threshold=0.02,
            verbose=True
        )
        
        # 模拟动态跟踪误差变化
        tracking_errors = [0.01, 0.02, 0.04, 0.06, 0.03, 0.08]
        
        for i, error in enumerate(tracking_errors):
            timestamp = pd.Timestamp('2021-01-01') + timedelta(days=i)
            dynamic_controller.update_tracking_error_history(error, timestamp)
            
            # 检查是否需要再平衡
            should_rebalance = dynamic_controller.should_rebalance(error)
            
            if i < 3:
                # 前几个误差较小，不需要再平衡
                self.assertFalse(should_rebalance)
            elif error > 0.05:
                # 超过限制，需要再平衡
                self.assertTrue(should_rebalance)
        
        # 验证统计信息
        stats = dynamic_controller.get_tracking_error_statistics()
        self.assertGreater(stats['exceeds_limit'], 0)
    
    def test_real_time_monitoring(self):
        """测试实时监控功能"""
        # 创建实时监控控制器
        monitor_controller = TrackingErrorController(
            max_tracking_error=0.03,
            rebalance_threshold=0.01,
            verbose=True
        )
        
        # 模拟实时数据流
        monitoring_period = 10  # 10个时间点
        base_error = 0.02
        
        for i in range(monitoring_period):
            # 添加一些随机波动
            current_error = base_error + np.random.randn() * 0.005
            
            # 更新历史记录
            timestamp = pd.Timestamp.now() + timedelta(minutes=i)
            monitor_controller.update_tracking_error_history(
                current_error, timestamp
            )
            
            # 检查监控状态
            if i > 0:
                previous_error = base_error + np.random.randn() * 0.005
                should_rebalance = monitor_controller.should_rebalance(
                    current_error, previous_error
                )
                
                # 验证监控逻辑
                if abs(current_error - previous_error) > 0.01:
                    self.assertTrue(should_rebalance)
        
        # 验证监控统计
        stats = monitor_controller.get_tracking_error_statistics()
        self.assertEqual(stats['count'], monitoring_period)
        self.assertIsInstance(stats['current'], float)
    
    def test_multiple_optimization_algorithms(self):
        """测试多种跟踪误差优化算法"""
        # 测试不同的优化场景
        scenarios = [
            {
                'name': '保守策略',
                'max_tracking_error': 0.02,
                'rebalance_threshold': 0.005
            },
            {
                'name': '平衡策略',
                'max_tracking_error': 0.05,
                'rebalance_threshold': 0.02
            },
            {
                'name': '激进策略',
                'max_tracking_error': 0.08,
                'rebalance_threshold': 0.04
            }
        ]
        
        results = {}
        
        for scenario in scenarios:
            controller = TrackingErrorController(
                max_tracking_error=scenario['max_tracking_error'],
                rebalance_threshold=scenario['rebalance_threshold'],
                verbose=False
            )
            
            # 测试相同的跟踪误差
            test_error = 0.03
            should_rebalance = controller.should_rebalance(test_error)
            
            results[scenario['name']] = {
                'should_rebalance': should_rebalance,
                'max_error': scenario['max_tracking_error'],
                'threshold': scenario['rebalance_threshold']
            }
        
        # 验证不同策略的行为
        self.assertFalse(results['保守策略']['should_rebalance'])
        self.assertTrue(results['激进策略']['should_rebalance'])
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试空数据
        empty_portfolio = pd.Series([], dtype=float)
        empty_benchmark = pd.Series([], dtype=float)
        
        error_empty = self.controller.calculate_tracking_error(
            empty_portfolio, empty_benchmark
        )
        self.assertEqual(error_empty, float('inf'))
        
        # 测试维度不匹配
        wrong_weights = np.random.rand(self.n_assets + 1)
        
        error_dimension = self.controller.calculate_tracking_error_from_weights(
            wrong_weights,
            self.benchmark_weights,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk
        )
        self.assertEqual(error_dimension, float('inf'))
    
    def test_performance_optimization(self):
        """测试性能优化"""
        import time
        
        # 大规模数据测试
        large_n_assets = 1000
        large_n_factors = 50
        
        large_factor_exposure = np.random.randn(
            large_n_assets, large_n_factors
        )
        large_factor_covariance = np.random.randn(
            large_n_factors, large_n_factors
        )
        large_factor_covariance = (
            large_factor_covariance @ large_factor_covariance.T
        )
        large_specific_risk = np.random.rand(large_n_assets) * 0.1 + 0.05
        large_portfolio_weights = np.random.rand(large_n_assets)
        large_portfolio_weights = (
            large_portfolio_weights / np.sum(large_portfolio_weights)
        )
        large_benchmark_weights = np.random.rand(large_n_assets)
        large_benchmark_weights = (
            large_benchmark_weights / np.sum(large_benchmark_weights)
        )
        
        # 测试计算性能
        start_time = time.time()
        
        for _ in range(10):  # 重复计算10次
            tracking_error = self.controller.calculate_tracking_error_from_weights(
                large_portfolio_weights,
                large_benchmark_weights,
                large_factor_exposure,
                large_factor_covariance,
                large_specific_risk,
                annualize=False
            )
        
        end_time = time.time()
        computation_time = end_time - start_time
        
        # 验证性能（应该在合理时间内完成）
        self.assertLess(computation_time, 5.0)  # 10次计算应在5秒内完成
        self.assertIsInstance(tracking_error, float)
        self.assertGreater(tracking_error, 0)


if __name__ == '__main__':
    unittest.main()