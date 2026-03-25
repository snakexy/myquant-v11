"""
增强指数优化器测试

测试增强指数策略的优化器功能
"""

import unittest
import numpy as np
import pandas as pd
from unittest.mock import Mock

from ..optimizer.enhanced_indexing_optimizer import EnhancedIndexingOptimizer


class TestEnhancedIndexingOptimizer(unittest.TestCase):
    """增强指数优化器测试类"""
    
    def setUp(self):
        """测试前准备"""
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
        
        # 创建优化器实例
        self.optimizer = EnhancedIndexingOptimizer(
            verbose=False,
            delta=0.2,
            lambda_risk=0.5,
            lambda_return=0.5
        )
    
    def test_optimizer_initialization(self):
        """测试优化器初始化"""
        optimizer = EnhancedIndexingOptimizer(
            verbose=True,
            delta=0.3,
            lambda_risk=0.4,
            lambda_return=0.6
        )
        
        self.assertEqual(optimizer.delta, 0.3)
        self.assertEqual(optimizer.lambda_risk, 0.4)
        self.assertEqual(optimizer.lambda_return, 0.6)
        self.assertTrue(optimizer.verbose)
    
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
        
        # 测试无效维度
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
    
    def test_optimization(self):
        """测试优化过程"""
        # 创建预期收益
        expected_returns = np.random.randn(self.n_assets)
        
        # 执行优化
        optimized_weights = self.optimizer(
            expected_returns,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk**2,
            self.portfolio_weights,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        # 验证结果
        self.assertIsNotNone(optimized_weights)
        self.assertEqual(len(optimized_weights), self.n_assets)
        
        # 验证权重非负
        self.assertTrue(all(w >= 0 for w in optimized_weights))
        
        # 验证权重和接近1
        weight_sum = np.sum(optimized_weights)
        self.assertAlmostEqual(weight_sum, 1.0, places=6)
    
    def test_preprocessing(self):
        """测试输入预处理"""
        # 测试预处理
        r, F, cov_b, var_u, w0, wb, mfh, mfs = self.optimizer.preprocess_inputs(
            np.random.randn(self.n_assets),
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk,
            self.portfolio_weights,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        # 验证结果
        self.assertEqual(len(r), self.n_assets)
        self.assertEqual(F.shape, self.factor_exposure.shape)
        self.assertEqual(cov_b.shape, self.factor_covariance.shape)
        self.assertEqual(len(var_u), self.n_assets)
        self.assertEqual(len(w0), self.n_assets)
        self.assertEqual(len(wb), self.n_assets)
        self.assertEqual(len(mfh), self.n_assets)
        self.assertEqual(len(mfs), self.n_assets)
        
        # 验证权重归一化
        self.assertAlmostEqual(np.sum(w0), 1.0, places=6)
        self.assertAlmostEqual(np.sum(wb), 1.0, places=6)
    
    def test_alternative_method(self):
        """测试替代优化方法"""
        # 测试替代方法
        optimized_weights = self.optimizer._solve_with_alternative_method(
            np.random.randn(self.n_assets),
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk**2,
            self.portfolio_weights,
            self.benchmark_weights,
            self.mask_force_hold,
            self.mask_force_sell
        )
        
        # 验证结果
        self.assertIsNotNone(optimized_weights)
        self.assertEqual(len(optimized_weights), self.n_assets)
        
        # 验证权重非负
        self.assertTrue(all(w >= 0 for w in optimized_weights))
    
    def test_optimizer_info(self):
        """测试获取优化器信息"""
        info = self.optimizer.get_optimizer_info()
        
        # 验证结果
        self.assertIsInstance(info, dict)
        self.assertEqual(info['optimizer_type'], 'EnhancedIndexingOptimizer')
        self.assertEqual(info['delta'], 0.2)
        self.assertEqual(info['lambda_risk'], 0.5)
        self.assertEqual(info['lambda_return'], 0.5)
        self.assertEqual(info['solver'], 'ECOS')
        self.assertIn('verbose', info)
        self.assertIn('params', info)


if __name__ == '__main__':
    unittest.main()