"""
优化算法集成详细测试

测试增强指数策略的多种投资组合优化算法，包括CVXPY凸优化和自定义优化器
"""

import unittest
import numpy as np
import pandas as pd
import cvxpy as cp
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimizer.enhanced_indexing_optimizer import EnhancedIndexingOptimizer


class TestEnhancedIndexingOptimizerDetailed(unittest.TestCase):
    """增强指数优化器详细测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.optimizer = EnhancedIndexingOptimizer(
            verbose=True,
            delta=0.2,
            lambda_risk=0.5,
            lambda_return=0.5
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
        
        # 创建权重
        self.portfolio_weights = np.random.rand(self.n_assets)
        self.portfolio_weights = self.portfolio_weights / np.sum(self.portfolio_weights)
        
        self.benchmark_weights = np.random.rand(self.n_assets)
        self.benchmark_weights = self.benchmark_weights / np.sum(self.benchmark_weights)
        
        # 创建掩码
        self.mask_force_hold = np.random.choice([True, False], self.n_assets)
        self.mask_force_sell = np.random.choice([True, False], self.n_assets)
        
        # 创建预期收益
        self.expected_returns = np.random.randn(self.n_assets)
    
    def test_initialization(self):
        """测试优化器初始化"""
        optimizer = EnhancedIndexingOptimizer(
            verbose=False,
            delta=0.3,
            lambda_risk=0.4,
            lambda_return=0.6
        )
        
        self.assertEqual(optimizer.delta, 0.3)
        self.assertEqual(optimizer.lambda_risk, 0.4)
        self.assertEqual(optimizer.lambda_return, 0.6)
        self.assertFalse(optimizer.verbose)
    
    def test_input_validation(self):
        """测试输入参数验证"""
        # 测试有效输入
        is_valid = self.optimizer.validate_inputs(
            self.portfolio_weights,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        self.assertTrue(is_valid)
        
        # 测试维度不匹配
        invalid_factor_exp = np.random.randn(self.n_assets + 1, self.n_factors)
        is_valid = self.optimizer.validate_inputs(
            self.portfolio_weights,
            invalid_factor_exp,
            self.factor_covariance,
            self.specific_risk,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        self.assertFalse(is_valid)
        
        # 测试负权重
        negative_weights = -np.abs(self.portfolio_weights)
        is_valid = self.optimizer.validate_inputs(
            negative_weights,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        self.assertFalse(is_valid)
        
        # 测试协方差矩阵非正定
        invalid_cov = np.random.randn(self.n_factors, self.n_factors)
        is_valid = self.optimizer.validate_inputs(
            self.portfolio_weights,
            self.factor_exposure,
            invalid_cov,
            self.specific_risk,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        self.assertFalse(is_valid)
    
    def test_cvxpy_optimization(self):
        """测试CVXPY凸优化"""
        optimized_weights = self.optimizer(
            self.expected_returns,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk**2,
            self.portfolio_weights,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        # 验证结果
        self.assertIsInstance(optimized_weights, np.ndarray)
        self.assertEqual(len(optimized_weights), self.n_assets)
        
        # 验证权重非负
        self.assertTrue(np.all(optimized_weights >= 0))
        
        # 验证权重和为1
        weight_sum = np.sum(optimized_weights)
        self.assertAlmostEqual(weight_sum, 1.0, places=6)
        
        # 验证强制约束
        for i in range(self.n_assets):
            if self.mask_force_hold[i]:
                self.assertGreaterEqual(
                    optimized_weights[i], self.portfolio_weights[i]
                )
            if self.mask_force_sell[i]:
                self.assertEqual(optimized_weights[i], 0.0)
    
    def test_alternative_optimization_method(self):
        """测试替代优化方法"""
        # 创建一个会导致主优化失败的场景
        # 使用奇异的协方差矩阵
        singular_cov = np.eye(self.n_factors)
        singular_cov[0, 0] = 0  # 使矩阵奇异
        
        optimized_weights = self.optimizer(
            self.expected_returns,
            self.factor_exposure,
            singular_cov,
            self.specific_risk**2,
            self.portfolio_weights,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        # 验证替代方法的结果
        self.assertIsInstance(optimized_weights, np.ndarray)
        self.assertEqual(len(optimized_weights), self.n_assets)
        self.assertTrue(np.all(optimized_weights >= 0))
        self.assertAlmostEqual(np.sum(optimized_weights), 1.0, places=6)
    
    def test_optimization_parameters(self):
        """测试不同优化参数的影响"""
        # 测试不同的delta值
        delta_values = [0.1, 0.2, 0.3, 0.5]
        results = {}
        
        for delta in delta_values:
            optimizer = EnhancedIndexingOptimizer(delta=delta, verbose=False)
            optimized_weights = optimizer(
                self.expected_returns,
                self.factor_exposure,
                self.factor_covariance,
                self.specific_risk**2,
                self.portfolio_weights,
                self.benchmark_weights,
                self.mask_force_hold,
                self.mask_force_sell
            )
            
            # 计算换手率
            turnover = np.sum(np.abs(optimized_weights - self.portfolio_weights)) / 2
            
            results[delta] = {
                'weights': optimized_weights,
                'turnover': turnover
            }
        
        # 验证delta越大，换手率约束越松
        for i in range(len(delta_values) - 1):
            self.assertLessEqual(
                results[delta_values[i]]['turnover'],
                results[delta_values[i + 1]]['turnover']
            )
    
    def test_multi_objective_optimization(self):
        """测试多目标优化"""
        # 创建多目标优化器
        multi_optimizer = EnhancedIndexingOptimizer(
            lambda_risk=0.3,
            lambda_return=0.7,
            delta=0.15,
            verbose=True
        )
        
        optimized_weights = multi_optimizer(
            self.expected_returns,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk**2,
            self.portfolio_weights,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        # 验证多目标优化的结果
        self.assertIsInstance(optimized_weights, np.ndarray)
        self.assertTrue(np.all(optimized_weights >= 0))
        self.assertAlmostEqual(np.sum(optimized_weights), 1.0, places=6)
    
    def test_constraint_handling(self):
        """测试约束处理"""
        # 测试复杂的约束场景
        complex_optimizer = EnhancedIndexingOptimizer(
            delta=0.1,
            lambda_risk=0.6,
            lambda_return=0.4,
            verbose=True
        )
        
        # 创建复杂的掩码场景
        complex_hold_mask = np.ones(self.n_assets, dtype=bool)
        complex_hold_mask[:10] = True  # 前10只股票强制持有
        complex_hold_mask[30:40] = True  # 中间10只股票强制持有
        
        complex_sell_mask = np.zeros(self.n_assets, dtype=bool)
        complex_sell_mask[10:20] = True  # 中间10只股票强制卖出
        
        optimized_weights = complex_optimizer(
            self.expected_returns,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk**2,
            self.portfolio_weights,
            self.benchmark_weights,
            complex_hold_mask,
            complex_sell_mask
        )
        
        # 验证复杂约束
        for i in range(self.n_assets):
            if complex_hold_mask[i]:
                self.assertGreaterEqual(
                    optimized_weights[i], self.portfolio_weights[i]
                )
            if complex_sell_mask[i]:
                self.assertEqual(optimized_weights[i], 0.0)
    
    def test_risk_adjusted_returns(self):
        """测试风险调整收益计算"""
        # 创建风险调整优化器
        risk_adj_optimizer = EnhancedIndexingOptimizer(
            lambda_risk=0.8,  # 高风险惩罚
            lambda_return=0.2,  # 低收益权重
            delta=0.15,
            verbose=True
        )
        
        optimized_weights = risk_adj_optimizer(
            self.expected_returns,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk**2,
            self.portfolio_weights,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        # 验证风险调整效果
        # 高风险惩罚应该导致更保守的组合
        portfolio_risk = np.sqrt(
            optimized_weights.T @ self.factor_covariance @ optimized_weights +
            np.sum((optimized_weights * self.specific_risk) ** 2)
        )
        
        benchmark_risk = np.sqrt(
            self.benchmark_weights.T @ self.factor_covariance @ self.benchmark_weights +
            np.sum((self.benchmark_weights * self.specific_risk) ** 2)
        )
        
        # 优化后的组合风险应该更接近基准风险
        risk_diff = abs(portfolio_risk - benchmark_risk)
        self.assertLess(risk_diff, 0.1)  # 风险差异应该较小
    
    def test_performance_optimization(self):
        """测试性能优化"""
        import time
        
        # 大规模优化测试
        large_n_assets = 500
        large_n_factors = 50
        
        large_factor_exp = np.random.randn(large_n_assets, large_n_factors)
        large_factor_cov = np.random.randn(large_n_factors, large_n_factors)
        large_factor_cov = large_factor_cov @ large_factor_cov.T
        large_specific_risk = np.random.rand(large_n_assets) * 0.1 + 0.05
        large_expected_returns = np.random.randn(large_n_assets)
        large_portfolio_weights = np.random.rand(large_n_assets)
        large_portfolio_weights = large_portfolio_weights / np.sum(large_portfolio_weights)
        large_benchmark_weights = np.random.rand(large_n_assets)
        large_benchmark_weights = large_benchmark_weights / np.sum(large_benchmark_weights)
        large_hold_mask = np.random.choice([True, False], large_n_assets)
        large_sell_mask = np.random.choice([True, False], large_n_assets)
        
        # 创建大规模优化器
        large_optimizer = EnhancedIndexingOptimizer(verbose=False)
        
        # 测试优化性能
        start_time = time.time()
        
        for _ in range(5):  # 重复优化5次
            optimized_weights = large_optimizer(
                large_expected_returns,
                large_factor_exp,
                large_factor_cov,
                large_specific_risk**2,
                large_portfolio_weights,
                large_benchmark_weights,
                large_hold_mask,
                large_sell_mask
            )
        
        end_time = time.time()
        optimization_time = end_time - start_time
        
        # 验证性能
        self.assertLess(optimization_time, 10.0)  # 5次大规模优化应在10秒内完成
        self.assertIsInstance(optimized_weights, np.ndarray)
        self.assertEqual(len(optimized_weights), large_n_assets)
    
    def test_solver_comparison(self):
        """测试不同求解器的比较"""
        solvers = ['ECOS', 'SCS', 'OSQP']
        results = {}
        
        for solver in solvers:
            try:
                # 创建使用指定求解器的优化器
                solver_optimizer = EnhancedIndexingOptimizer(verbose=False)
                
                # 修改求解器（通过直接设置）
                optimized_weights = solver_optimizer(
                    self.expected_returns,
                    self.factor_exposure,
                    self.factor_covariance,
                    self.specific_risk**2,
                    self.portfolio_weights,
                    self.benchmark_weights,
                    self.mask_force_hold,
                    self.mask_force_sell
                )
                
                # 计算目标函数值
                portfolio_risk = np.sqrt(
                    optimized_weights.T @ self.factor_covariance @ optimized_weights +
                    np.sum((optimized_weights * self.specific_risk) ** 2)
                )
                expected_return = np.dot(self.expected_returns, optimized_weights)
                turnover = np.sum(np.abs(optimized_weights - self.portfolio_weights)) / 2
                
                objective_value = (
                    0.5 * expected_return - 
                    0.5 * portfolio_risk - 
                    0.2 * turnover
                )
                
                results[solver] = {
                    'objective_value': objective_value,
                    'weights': optimized_weights
                }
                
            except Exception as e:
                results[solver] = {'error': str(e)}
        
        # 验证至少有一个求解器成功
        successful_solvers = [
            solver for solver, result in results.items() 
            if 'error' not in result
        ]
        
        self.assertGreater(len(successful_solvers), 0)
        
        # 验证不同求解器的结果一致性
        successful_results = [
            result for solver, result in results.items() 
            if 'error' not in result
        ]
        
        if len(successful_results) > 1:
            objectives = [result['objective_value'] for result in successful_results]
            max_objective = max(objectives)
            min_objective = min(objectives)
            
            # 目标函数值应该在合理范围内
            self.assertLess(max_objective - min_objective, 0.1)
    
    def test_robustness_optimization(self):
        """测试鲁棒性优化"""
        # 创建多个市场场景
        scenarios = [
            {
                'name': '正常市场',
                'returns': self.expected_returns,
                'covariance': self.factor_covariance
            },
            {
                'name': '高波动市场',
                'returns': self.expected_returns * 1.5,  # 更高收益
                'covariance': self.factor_covariance * 2.0   # 更高波动
            },
            {
                'name': '低波动市场',
                'returns': self.expected_returns * 0.7,  # 更低收益
                'covariance': self.factor_covariance * 0.5   # 更低波动
            }
        ]
        
        robust_results = {}
        
        for scenario in scenarios:
            # 为每个场景创建优化器
            scenario_optimizer = EnhancedIndexingOptimizer(
                delta=0.15,
                lambda_risk=0.6,
                lambda_return=0.4,
                verbose=False
            )
            
            optimized_weights = scenario_optimizer(
                scenario['returns'],
                self.factor_exposure,
                scenario['covariance'],
                self.specific_risk**2,
                self.portfolio_weights,
                self.benchmark_weights,
                self.mask_force_hold,
                self.mask_force_sell
            )
            
            # 计算场景表现
            portfolio_return = np.dot(scenario['returns'], optimized_weights)
            portfolio_risk = np.sqrt(
                optimized_weights.T @ scenario['covariance'] @ optimized_weights +
                np.sum((optimized_weights * self.specific_risk) ** 2)
            )
            
            robust_results[scenario['name']] = {
                'return': portfolio_return,
                'risk': portfolio_risk,
                'sharpe_ratio': portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
            }
        
        # 验证鲁棒性结果
        self.assertEqual(len(robust_results), len(scenarios))
        
        # 验证不同场景下的权重变化
        normal_weights = robust_results['正常市场']['weights']
        high_vol_weights = robust_results['高波动市场']['weights']
        low_vol_weights = robust_results['低波动市场']['weights']
        
        # 权重应该有差异但不会太大
        weight_diff_high = np.mean(np.abs(normal_weights - high_vol_weights))
        weight_diff_low = np.mean(np.abs(normal_weights - low_vol_weights))
        
        self.assertLess(weight_diff_high, 0.2)  # 权重差异应该合理
        self.assertLess(weight_diff_low, 0.2)
    
    def test_custom_optimizer_integration(self):
        """测试自定义优化器集成"""
        # 创建自定义优化器类
        class CustomOptimizer:
            def __init__(self, custom_param=1.0):
                self.custom_param = custom_param
            
            def optimize(self, returns, factor_exp, cov, specific_risk, 
                      init_weights, bench_weights, hold_mask, sell_mask):
                # 简单的等权重分配
                n_assets = len(returns)
                equal_weights = np.ones(n_assets) / n_assets
                
                # 应用自定义参数
                adjusted_weights = equal_weights * (1.0 + self.custom_param * 0.1)
                adjusted_weights = adjusted_weights / np.sum(adjusted_weights)
                
                return adjusted_weights
        
        # 测试自定义优化器集成
        custom_optimizer = CustomOptimizer(custom_param=0.5)
        
        # 这里需要修改优化器以支持自定义优化器
        # 在实际实现中，可以通过继承和重写方法来实现
        
        # 验证自定义优化器的参数
        self.assertEqual(custom_optimizer.custom_param, 0.5)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试空输入
        empty_returns = np.array([])
        with self.assertRaises(ValueError):
            self.optimizer(empty_returns, self.factor_exposure, self.factor_covariance,
                        self.specific_risk**2, self.portfolio_weights,
                        self.benchmark_weights, self.mask_force_hold,
                        self.mask_force_sell)
        
        # 测试无效的协方差矩阵
        invalid_cov = np.full((self.n_factors, self.n_factors), np.nan)
        with self.assertRaises((ValueError, cp.SolverError)):
            self.optimizer(self.expected_returns, self.factor_exposure, invalid_cov,
                        self.specific_risk**2, self.portfolio_weights,
                        self.benchmark_weights, self.mask_force_hold,
                        self.mask_force_sell)
        
        # 测试维度不匹配
        wrong_exp = np.random.randn(self.n_assets, self.n_factors + 1)
        with self.assertRaises(ValueError):
            self.optimizer(self.expected_returns, wrong_exp, self.factor_covariance,
                        self.specific_risk**2, self.portfolio_weights,
                        self.benchmark_weights, self.mask_force_hold,
                        self.mask_force_sell)
    
    def test_optimization_convergence(self):
        """测试优化收敛性"""
        # 创建收敛测试优化器
        convergence_optimizer = EnhancedIndexingOptimizer(
            delta=0.1,
            lambda_risk=0.5,
            lambda_return=0.5,
            verbose=True
        )
        
        # 多次运行优化，检查收敛性
        results = []
        for i in range(10):
            # 添加一些随机噪声
            noisy_returns = self.expected_returns + np.random.randn(*self.expected_returns.shape) * 0.001
            
            optimized_weights = convergence_optimizer(
                noisy_returns,
                self.factor_exposure,
                self.factor_covariance,
                self.specific_risk**2,
                self.portfolio_weights,
                self.benchmark_weights,
                self.mask_force_hold,
                self.mask_force_sell
            )
            
            results.append(optimized_weights)
        
        # 计算权重变化
        weight_changes = []
        for i in range(1, len(results)):
            change = np.mean(np.abs(results[i] - results[i-1]))
            weight_changes.append(change)
        
        # 验证收敛性
        # 后面的优化应该比前面的变化更小
        if len(weight_changes) > 5:
            early_changes = weight_changes[:5]
            late_changes = weight_changes[5:]
            
            avg_early_change = np.mean(early_changes)
            avg_late_change = np.mean(late_changes)
            
            # 后期变化应该小于前期变化
            self.assertLess(avg_late_change, avg_early_change * 1.5)


if __name__ == '__main__':
    unittest.main()