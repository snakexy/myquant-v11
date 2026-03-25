"""
风险暴露管理详细测试

测试全面的风险因子暴露管理，包括行业暴露管理和风险预算控制
"""

import unittest
import numpy as np
import pandas as pd
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_management.risk_exposure import RiskExposureManager


class TestRiskExposureManager(unittest.TestCase):
    """风险暴露管理器详细测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = RiskExposureManager(
            factor_limits={
                'factor_0': 0.1,
                'factor_1': 0.15,
                'factor_2': 0.08
            },
            verbose=True
        )
        
        # 创建测试数据
        self.n_assets = 100
        self.n_factors = 10
        
        # 创建因子暴露矩阵
        self.factor_exposure = np.random.randn(self.n_assets, self.n_factors)
        
        # 创建投资组合权重
        self.portfolio_weights = np.random.rand(self.n_assets)
        self.portfolio_weights = self.portfolio_weights / np.sum(self.portfolio_weights)
        
        # 创建基准权重
        self.benchmark_weights = np.random.rand(self.n_assets)
        self.benchmark_weights = self.benchmark_weights / np.sum(self.benchmark_weights)
        
        # 创建因子协方差矩阵
        self.factor_covariance = np.random.randn(self.n_factors, self.n_factors)
        self.factor_covariance = self.factor_covariance @ self.factor_covariance.T
    
    def test_initialization(self):
        """测试初始化"""
        manager = RiskExposureManager(
            factor_limits={'test_factor': 0.2},
            verbose=False
        )
        
        self.assertEqual(manager.factor_limits['test_factor'], 0.2)
        self.assertFalse(manager.verbose)
        
        # 测试默认初始化
        default_manager = RiskExposureManager()
        self.assertIsInstance(default_manager.factor_limits, dict)
        self.assertTrue(default_manager.verbose)
    
    def test_calculate_risk_exposure(self):
        """测试风险暴露计算"""
        exposure = self.manager.calculate_risk_exposure(
            self.portfolio_weights,
            self.factor_exposure
        )
        
        # 验证结果
        self.assertIsInstance(exposure, dict)
        self.assertEqual(len(exposure), self.n_factors)
        
        # 验证所有因子暴露都是数值
        for factor_name, factor_exposure in exposure.items():
            self.assertIsInstance(factor_exposure, (int, float))
        
        # 测试零权重的情况
        zero_weights = np.zeros(self.n_assets)
        zero_exposure = self.manager.calculate_risk_exposure(
            zero_weights, self.factor_exposure
        )
        
        for factor_exposure in zero_exposure.values():
            self.assertAlmostEqual(factor_exposure, 0, places=6)
    
    def test_calculate_active_risk_exposure(self):
        """测试主动风险暴露计算"""
        active_exposure = self.manager.calculate_active_risk_exposure(
            self.portfolio_weights,
            self.benchmark_weights,
            self.factor_exposure
        )
        
        # 验证结果
        self.assertIsInstance(active_exposure, dict)
        self.assertEqual(len(active_exposure), self.n_factors)
        
        # 验证主动暴露计算正确
        expected_active_exposure = {}
        for i in range(self.n_factors):
            factor_name = f'factor_{i}'
            portfolio_exposure = np.sum(
                self.portfolio_weights * self.factor_exposure[:, i]
            )
            benchmark_exposure = np.sum(
                self.benchmark_weights * self.factor_exposure[:, i]
            )
            expected_active_exposure[factor_name] = portfolio_exposure - benchmark_exposure
        
        for factor_name, exposure in active_exposure.items():
            self.assertAlmostEqual(
                exposure, expected_active_exposure[factor_name], places=6
            )
    
    def test_check_exposure_limits(self):
        """测试暴露限制检查"""
        # 创建测试暴露
        test_exposure = {
                'factor_0': 0.05,  # 在限制内
                'factor_1': 0.2,   # 超过限制
                'factor_2': 0.08,   # 等于限制
                'factor_3': 0.15   # 不在限制列表中
        }
        
        limit_results = self.manager.check_exposure_limits(test_exposure)
        
        # 验证结果
        self.assertIsInstance(limit_results, dict)
        self.assertEqual(len(limit_results), 4)
        
        # 验证限制检查结果
        self.assertFalse(limit_results['factor_0']['exceeds'])  # 0.05 < 0.1
        self.assertTrue(limit_results['factor_1']['exceeds'])   # 0.2 > 0.15
        self.assertFalse(limit_results['factor_2']['exceeds'])  # 0.08 == 0.08
        self.assertTrue(limit_results['factor_3']['exceeds'])   # 无限制，默认超限
        
        # 验证超限程度
        self.assertAlmostEqual(
            limit_results['factor_1']['excess'], 0.05, places=6
        )  # 0.2 - 0.15 = 0.05
    
    def test_calculate_exposure_contribution(self):
        """测试暴露贡献计算"""
        contributions = self.manager.calculate_exposure_contribution(
            self.portfolio_weights,
            self.factor_exposure,
            self.factor_covariance
        )
        
        # 验证结果
        self.assertIsInstance(contributions, dict)
        self.assertEqual(len(contributions), self.n_factors)
        
        # 验证所有贡献都是非负的
        for factor_name, contribution in contributions.items():
            self.assertGreaterEqual(contribution, 0)
        
        # 验证贡献计算正确
        for i in range(self.n_factors):
            factor_name = f'factor_{i}'
            expected_contribution = (
                self.factor_exposure[:, i].T @ 
                self.factor_covariance @ 
                self.factor_exposure[:, i]
            )
            self.assertAlmostEqual(
                contributions[factor_name], expected_contribution, places=6
            )
    
    def test_risk_budget_control(self):
        """测试风险预算控制"""
        # 设置风险预算
        risk_budget = {
                'total_budget': 0.1,
                'factor_budgets': {
                        'factor_0': 0.03,
                        'factor_1': 0.04,
                        'factor_2': 0.02
                }
        }
        
        # 创建预算管理器
        budget_manager = RiskExposureManager(
            factor_limits=risk_budget['factor_budgets'],
            risk_budget=risk_budget,
            verbose=True
        )
        
        # 测试预算检查
        test_exposure = {
                'factor_0': 0.025,  # 在预算内
                'factor_1': 0.05,   # 超过预算
                'factor_2': 0.02,   # 等于预算
                'factor_3': 0.01    # 不在预算中
        }
        
        budget_results = budget_manager.check_risk_budget(test_exposure)
        
        # 验证结果
        self.assertIsInstance(budget_results, dict)
        self.assertTrue(budget_results['within_total_budget'])
        self.assertFalse(budget_results['factor_1']['within_budget'])
        self.assertTrue(budget_results['factor_0']['within_budget'])
        self.assertTrue(budget_results['factor_2']['within_budget'])
        
        # 验证预算使用情况
        total_usage = budget_results['total_budget_usage']
        self.assertLess(total_usage, 1.0)  # 使用率应该小于100%
    
    def test_sector_exposure_integration(self):
        """测试行业暴露集成"""
        # 创建股票到行业的映射
        stock_sectors = {
                f'stock_{i:02d}': f'sector_{i % 5}' 
                for i in range(self.n_assets)
        }
        
        # 创建行业暴露管理器
        sector_manager = RiskExposureManager(
            sector_limits={
                    'sector_0': 0.25,
                    'sector_1': 0.3,
                    'sector_2': 0.2
            },
            stock_sectors=stock_sectors,
            verbose=True
        )
        
        # 计算行业暴露
        sector_exposure = sector_manager.calculate_sector_exposure(
            self.portfolio_weights, stock_sectors
        )
        
        # 验证结果
        self.assertIsInstance(sector_exposure, dict)
        self.assertGreater(len(sector_exposure), 0)
        
        # 验证行业暴露总和
        total_sector_exposure = sum(sector_exposure.values())
        self.assertAlmostEqual(total_sector_exposure, 1.0, places=6)
    
    def test_dynamic_risk_limits(self):
        """测试动态风险限制"""
        # 创建动态限制管理器
        dynamic_manager = RiskExposureManager(verbose=True)
        
        # 模拟动态限制调整
        market_volatility = 0.15  # 市场波动率
        dynamic_limits = dynamic_manager.calculate_dynamic_limits(
            market_volatility, base_limit=0.05
        )
        
        # 验证动态限制
        self.assertIsInstance(dynamic_limits, dict)
        self.assertGreater(len(dynamic_limits), 0)
        
        # 验证限制与市场波动相关
        for factor_name, limit in dynamic_limits.items():
            self.assertGreater(limit, 0)
            self.assertLess(limit, 0.1)  # 合理范围内
    
    def test_risk_attribution(self):
        """测试风险归因"""
        # 计算风险归因
        attribution = self.manager.calculate_risk_attribution(
            self.portfolio_weights,
            self.benchmark_weights,
            self.factor_exposure,
            self.factor_covariance
        )
        
        # 验证结果
        self.assertIsInstance(attribution, dict)
        self.assertIn('factor_attribution', attribution)
        self.assertIn('specific_attribution', attribution)
        self.assertIn('total_attribution', attribution)
        
        # 验证归因总和
        factor_attr_sum = sum(attribution['factor_attribution'].values())
        total_attr = (
            factor_attr_sum + attribution['specific_attribution']
        )
        self.assertAlmostEqual(
            attribution['total_attribution'], total_attr, places=6
        )
    
    def test_stress_testing(self):
        """测试压力测试"""
        # 创建压力场景
        stress_scenarios = [
                {
                        'name': '市场危机',
                        'factor_shocks': {
                                'factor_0': -0.1,
                                'factor_1': 0.15,
                                'factor_2': -0.08
                        }
                },
                {
                        'name': '行业轮动',
                        'factor_shocks': {
                                'factor_0': 0.05,
                                'factor_1': -0.05,
                                'factor_2': 0.03
                        }
                }
        ]
        
        # 执行压力测试
        stress_results = {}
        for scenario in stress_scenarios:
            result = self.manager.run_stress_test(
                    self.portfolio_weights,
                    self.factor_exposure,
                    scenario['factor_shocks']
            )
            stress_results[scenario['name']] = result
        
        # 验证压力测试结果
        for scenario_name, result in stress_results.items():
            self.assertIsInstance(result, dict)
            self.assertIn('portfolio_impact', result)
            self.assertIn('factor_impacts', result)
            self.assertIn('exceeds_limits', result)
    
    def test_risk_monitoring(self):
        """测试风险监控"""
        # 创建监控管理器
        monitor_manager = RiskExposureManager(
            monitoring_frequency='daily',
            alert_threshold=0.8,
            verbose=True
        )
        
        # 模拟监控数据
        monitoring_data = []
        for i in range(10):
            # 生成随机暴露数据
            daily_exposure = {
                    f'factor_{j}': np.random.rand() * 0.1 
                    for j in range(self.n_factors)
            }
            monitoring_data.append(daily_exposure)
        
        # 执行监控
        monitoring_results = monitor_manager.monitor_risk_exposure(monitoring_data)
        
        # 验证监控结果
        self.assertIsInstance(monitoring_results, dict)
        self.assertIn('average_exposure', monitoring_results)
        self.assertIn('max_exposure', monitoring_results)
        self.assertIn('exceedance_count', monitoring_results)
        self.assertIn('alert_triggered', monitoring_results)
    
    def test_portfolio_optimization(self):
        """测试投资组合优化"""
        # 设置优化目标
        optimization_objectives = {
                'minimize_tracking_error': True,
                'target_exposure': {
                        'factor_0': 0.02,
                        'factor_1': 0.03
                },
                'constraints': {
                        'max_turnover': 0.2,
                        'min_weight': 0.01,
                        'max_weight': 0.1
                }
        }
        
        # 执行优化
        optimized_weights = self.manager.optimize_portfolio(
            self.portfolio_weights,
            self.factor_exposure,
            self.factor_covariance,
            optimization_objectives
        )
        
        # 验证优化结果
        self.assertIsInstance(optimized_weights, np.ndarray)
        self.assertEqual(len(optimized_weights), self.n_assets)
        
        # 验证权重约束
        self.assertTrue(np.all(optimized_weights >= 0))  # 非负权重
        self.assertAlmostEqual(np.sum(optimized_weights), 1.0, places=6)  # 权重和为1
        
        # 验证最大权重约束
        self.assertTrue(np.all(optimized_weights <= 0.1))
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试空数据
        empty_weights = np.array([])
        empty_exposure = np.array([]).reshape(0, 0)
        
        with self.assertRaises(ValueError):
            self.manager.calculate_risk_exposure(empty_weights, empty_exposure)
        
        # 测试维度不匹配
        wrong_exposure = np.random.randn(self.n_assets, self.n_factors + 1)
        with self.assertRaises(ValueError):
            self.manager.calculate_risk_exposure(self.portfolio_weights, wrong_exposure)
        
        # 测试负权重
        negative_weights = -np.abs(self.portfolio_weights)
        with self.assertRaises(ValueError):
            self.manager.calculate_risk_exposure(negative_weights, self.factor_exposure)
    
    def test_performance_optimization(self):
        """测试性能优化"""
        import time
        
        # 大规模数据测试
        large_n_assets = 5000
        large_n_factors = 100
        
        large_exposure = np.random.randn(large_n_assets, large_n_factors)
        large_weights = np.random.rand(large_n_assets)
        large_weights = large_weights / np.sum(large_weights)
        
        # 测试计算性能
        start_time = time.time()
        
        for _ in range(10):  # 重复计算10次
            exposure = self.manager.calculate_risk_exposure(large_weights, large_exposure)
        
        end_time = time.time()
        computation_time = end_time - start_time
        
        # 验证性能
        self.assertLess(computation_time, 3.0)  # 10次计算应在3秒内完成
        self.assertIsInstance(exposure, dict)
        self.assertEqual(len(exposure), large_n_factors)


if __name__ == '__main__':
    unittest.main()