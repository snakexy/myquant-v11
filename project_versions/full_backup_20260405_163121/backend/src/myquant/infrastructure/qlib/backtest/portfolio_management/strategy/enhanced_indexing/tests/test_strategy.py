"""
增强指数策略测试

测试增强指数策略的核心功能
"""

import unittest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import tempfile
import os

from ..strategy import EnhancedIndexingStrategy
from ..data_loaders.risk_data_loader import RiskDataLoader
from ..data_loaders.benchmark_loader import BenchmarkLoader


class TestEnhancedIndexingStrategy(unittest.TestCase):
    """增强指数策略测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试数据
        self.create_test_data()
        
        # 创建策略实例
        self.strategy = EnhancedIndexingStrategy(
            riskmodel_root=self.temp_dir,
            market="test_market",
            turn_limit=0.2,
            verbose=True
        )
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时目录
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_data(self):
        """创建测试数据"""
        # 创建风险模型目录
        risk_dir = os.path.join(self.temp_dir, "20210101")
        os.makedirs(risk_dir, exist_ok=True)
        
        # 创建因子暴露数据
        n_stocks = 100
        n_factors = 10
        
        factor_exp = pd.DataFrame(
            np.random.randn(n_stocks, n_factors),
            index=[f"stock_{i:04d}" for i in range(n_stocks)],
            columns=[f"factor_{i}" for i in range(n_factors)]
        )
        factor_exp.to_pickle(os.path.join(risk_dir, "factor_exp.pkl"))
        
        # 创建因子协方差矩阵
        factor_cov = pd.DataFrame(
            np.random.randn(n_factors, n_factors),
            index=[f"factor_{i}" for i in range(n_factors)],
            columns=[f"factor_{i}" for i in range(n_factors)]
        )
        factor_cov.to_pickle(os.path.join(risk_dir, "factor_cov.pkl"))
        
        # 创建特定风险数据
        specific_risk = pd.Series(
            np.random.rand(n_stocks) * 0.1 + 0.05,
            index=[f"stock_{i:04d}" for i in range(n_stocks)]
        )
        specific_risk.to_pickle(os.path.join(risk_dir, "specific_risk.pkl"))
    
    def test_strategy_initialization(self):
        """测试策略初始化"""
        # 测试正常初始化
        strategy = EnhancedIndexingStrategy(
            riskmodel_root=self.temp_dir,
            market="csi500",
            turn_limit=0.2,
            verbose=False
        )
        
        self.assertEqual(strategy.market, "csi500")
        self.assertEqual(strategy.turn_limit, 0.2)
        self.assertFalse(strategy.verbose)
        self.assertIsNotNone(strategy.optimizer)
    
    def test_generate_target_weight_position(self):
        """测试生成目标权重位置"""
        # 创建测试评分序列
        score_series = pd.Series(
            np.random.randn(100),
            index=[f"stock_{i:04d}" for i in range(100)]
        )
        
        # 创建当前持仓
        current_position = {
            f"stock_{i:04d}": np.random.rand() * 0.01
            for i in range(100)
        }
        
        # 测试生成目标权重
        target_weights = self.strategy.generate_target_weight_position(
            score_series, current_position
        )
        
        # 验证结果
        self.assertIsNotNone(target_weights)
        self.assertIsInstance(target_weights, dict)
        
        # 验证权重和为1
        total_weight = sum(target_weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=6)
    
    def test_load_risk_data(self):
        """测试风险数据加载"""
        # 测试加载存在的数据
        risk_data = self.strategy._load_risk_data(pd.Timestamp("2021-01-01"))
        
        self.assertIsNotNone(risk_data)
        self.assertEqual(len(risk_data), 5)  # factor_exp, factor_cov, specific_risk, universe, blacklist
        
        # 测试加载不存在的数据
        risk_data_none = self.strategy._load_risk_data(pd.Timestamp("2021-01-02"))
        self.assertIsNone(risk_data_none)
    
    def test_get_current_weight_dict(self):
        """测试获取当前权重字典"""
        # 创建测试数据
        current_position = {
            f"stock_{i:04d}": np.random.rand() * 0.01
            for i in range(100)
        }
        universe = [f"stock_{i:04d}" for i in range(100)]
        
        # 模拟风险暴露度
        with patch.object(self.strategy, 'get_risk_degree', return_value=1.0):
            cur_weight = self.strategy._get_current_weight_dict(
                current_position, universe
            )
            
            # 验证结果
            self.assertEqual(len(cur_weight), 100)
            self.assertTrue(all(w >= 0 for w in cur_weight))
            
            # 验证权重归一化
            total_weight = sum(cur_weight)
            self.assertAlmostEqual(total_weight, 1.0, places=6)
    
    def test_load_benchmark_weight(self):
        """测试加载基准权重"""
        # 创建测试数据
        pre_date = pd.Timestamp("2021-01-01")
        universe = [f"stock_{i:04d}" for i in range(100)]
        
        # 测试加载基准权重
        with patch.object(self.strategy, 'trade_exchange') as mock_exchange:
            mock_exchange.get_benchmark_weight.return_value = pd.Series(
                np.random.rand(100),
                index=universe
            )
            
            bench_weight = self.strategy._load_benchmark_weight(pre_date, universe)
            
            # 验证结果
            self.assertIsNotNone(bench_weight)
            self.assertEqual(len(bench_weight), 100)
            self.assertTrue(all(w >= 0 for w in bench_weight.values))
    
    def test_check_tradable_stocks(self):
        """测试检查股票可交易性"""
        # 创建测试数据
        pre_date = pd.Timestamp("2021-01-01")
        universe = [f"stock_{i:04d}" for i in range(100)]
        
        # 测试检查可交易性
        with patch.object(self.strategy, 'trade_exchange') as mock_exchange:
            # 模拟成交量数据
            volume_data = pd.Series(
                np.random.randint(0, 1000000, 100),
                index=universe
            )
            mock_exchange.get_volume.return_value = volume_data
            
            tradable = self.strategy._check_tradable_stocks(pre_date, universe)
            
            # 验证结果
            self.assertEqual(len(tradable), 100)
            self.assertIsInstance(tradable, np.ndarray)
            self.assertEqual(tradable.dtype, bool)
    
    def test_get_strategy_info(self):
        """测试获取策略信息"""
        # 测试获取策略信息
        info = self.strategy.get_strategy_info()
        
        # 验证结果
        self.assertIsInstance(info, dict)
        self.assertEqual(info['strategy_type'], 'EnhancedIndexingStrategy')
        self.assertEqual(info['riskmodel_root'], self.temp_dir)
        self.assertEqual(info['market'], "test_market")
        self.assertEqual(info['turn_limit'], 0.2)
        self.assertIn('optimizer_info', info)
        self.assertIn('cache_size', info)
    
    def test_reset(self):
        """测试重置策略状态"""
        # 添加一些缓存数据
        self.strategy._riskdata_cache["20210101"] = "test_data"
        
        # 重置策略
        self.strategy.reset()
        
        # 验证缓存已清空
        self.assertEqual(len(self.strategy._riskdata_cache), 0)


if __name__ == '__main__':
    unittest.main()