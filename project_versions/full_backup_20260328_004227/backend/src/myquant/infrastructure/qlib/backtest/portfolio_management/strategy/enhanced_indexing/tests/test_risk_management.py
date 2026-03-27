"""
风险管理测试

测试增强指数策略的风险管理功能
"""

import unittest
import numpy as np
import pandas as pd

from ..risk_management.tracking_error import TrackingErrorController
from ..risk_management.risk_exposure import RiskExposureManager
from ..risk_management.sector_exposure import SectorExposureManager


class TestRiskManagement(unittest.TestCase):
    """风险管理测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试数据
        self.n_assets = 100
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
        self.portfolio_weights = self.portfolio_weights / np.sum(self.portfolio_weights)
        
        # 创建基准权重
        self.benchmark_weights = np.random.rand(self.n_assets)
        self.benchmark_weights = self.benchmark_weights / np.sum(self.benchmark_weights)
        
        # 创建股票到行业的映射
        self.stock_sectors = {
            f"stock_{i:04d}": f"sector_{i % 5}" 
            for i in range(self.n_assets)
        }
    
    def test_tracking_error_controller(self):
        """测试跟踪误差控制器"""
        controller = TrackingErrorController(
            max_tracking_error=0.05,
            rebalance_threshold=0.02,
            verbose=False
        )
        
        # 测试跟踪误差计算
        tracking_error = controller.calculate_tracking_error_from_weights(
            self.portfolio_weights,
            self.benchmark_weights,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk
        )
        
        self.assertIsInstance(tracking_error, float)
        self.assertGreater(tracking_error, 0)
        
        # 测试跟踪误差限制检查
        exceeds_limit = controller.check_tracking_error_limit(0.1)
        self.assertTrue(exceeds_limit)
        
        # 测试再平衡判断
        should_rebalance = controller.should_rebalance(0.06, 0.04)
        self.assertTrue(should_rebalance)
        
        # 测试跟踪误差贡献
        contributions = controller.get_tracking_error_contribution(
            self.portfolio_weights,
            self.benchmark_weights,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk
        )
        
        self.assertIsInstance(contributions, dict)
        self.assertGreater(len(contributions), 0)
    
    def test_risk_exposure_manager(self):
        """测试风险暴露管理器"""
        manager = RiskExposureManager(
            factor_limits={'factor_0': 0.1, 'factor_1': 0.1},
            verbose=False
        )
        
        # 测试风险暴露计算
        exposure = manager.calculate_risk_exposure(
            self.portfolio_weights,
            self.factor_exposure
        )
        
        self.assertIsInstance(exposure, dict)
        self.assertGreater(len(exposure), 0)
        
        # 测试主动风险暴露
        active_exposure = manager.calculate_active_risk_exposure(
            self.portfolio_weights,
            self.benchmark_weights,
            self.factor_exposure
        )
        
        self.assertIsInstance(active_exposure, dict)
        self.assertGreater(len(active_exposure), 0)
        
        # 测试暴露限制检查
        risk_exposure = {
            f'factor_{i}': 0.05 * (i + 1) 
            for i in range(10)
        }
        
        limit_results = manager.check_exposure_limits(risk_exposure)
        self.assertIsInstance(limit_results, dict)
        self.assertGreater(len(limit_results), 0)
        
        # 测试风险贡献
        contributions = manager.calculate_exposure_contribution(
            self.portfolio_weights,
            self.factor_exposure,
            self.factor_covariance
        )
        
        self.assertIsInstance(contributions, dict)
        self.assertGreater(len(contributions), 0)
    
    def test_sector_exposure_manager(self):
        """测试行业暴露管理器"""
        manager = SectorExposureManager(
            sector_limits={'sector_0': 0.2, 'sector_1': 0.2},
            max_sector_weight=0.3,
            min_sectors=3,
            verbose=False
        )
        
        # 创建股票池
        stock_universe = [f"stock_{i:04d}" for i in range(self.n_assets)]
        
        # 测试行业暴露计算
        sector_exposure = manager.calculate_sector_exposure(
            self.portfolio_weights,
            self.stock_sectors,
            stock_universe
        )
        
        self.assertIsInstance(sector_exposure, dict)
        self.assertGreater(len(sector_exposure), 0)
        
        # 测试行业贡献
        contributions = manager.calculate_sector_contribution(
            self.portfolio_weights,
            self.stock_sectors
        )
        
        self.assertIsInstance(contributions, dict)
        self.assertGreater(len(contributions), 0)
        
        # 测试行业限制检查
        limit_results = manager.check_sector_limits(sector_exposure)
        self.assertIsInstance(limit_results, dict)
        self.assertGreater(len(limit_results), 0)
        
        # 测试分散化指标
        diversification = manager.check_diversification(sector_exposure)
        self.assertIsInstance(diversification, dict)
        self.assertIn('sector_count', diversification)
        self.assertIn('effective_sectors', diversification)
        self.assertIn('herfindahl_index', diversification)
        
        # 测试再平衡建议
        suggestions = manager.suggest_sector_rebalancing(sector_exposure)
        self.assertIsInstance(suggestions, dict)
        self.assertGreater(len(suggestions), 0)
    
    def test_integration(self):
        """测试风险管理组件集成"""
        # 创建跟踪误差控制器
        tracking_controller = TrackingErrorController(verbose=False)
        
        # 创建风险暴露管理器
        risk_manager = RiskExposureManager(verbose=False)
        
        # 创建行业暴露管理器
        sector_manager = SectorExposureManager(verbose=False)
        
        # 测试组件协作
        # 这里可以测试各个组件之间的协作和集成
        # 例如：跟踪误差控制器使用风险暴露管理器的数据
        
        # 计算风险暴露
        risk_exposure = risk_manager.calculate_risk_exposure(
            self.portfolio_weights,
            self.factor_exposure
        )
        
        # 计算跟踪误差
        tracking_error = tracking_controller.calculate_tracking_error_from_weights(
            self.portfolio_weights,
            self.benchmark_weights,
            self.factor_exposure,
            self.factor_covariance,
            self.specific_risk
        )
        
        # 验证结果
        self.assertIsInstance(risk_exposure, dict)
        self.assertIsInstance(tracking_error, float)
        self.assertGreater(len(risk_exposure), 0)
        self.assertGreater(tracking_error, 0)


if __name__ == '__main__':
    unittest.main()