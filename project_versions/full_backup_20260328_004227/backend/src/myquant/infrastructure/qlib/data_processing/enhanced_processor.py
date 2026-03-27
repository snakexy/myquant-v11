"""
增强的数据处理器
整合数据质量控制、技术指标计算和因子生成功能
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any

# 添加项目根目录到路径
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
)

logger = logging.getLogger(__name__)

# 导入子模块
from qlib_core.data_processing.data_quality import get_quality_controller
from qlib_core.data_processing.technical_indicators import get_indicators_calculator
from qlib_core.data_processing.factor_generation import get_factor_generator


class EnhancedQLibDataProcessor:
    """
    增强的QLib数据处理器
    
    整合数据质量控制、技术指标计算和因子生成功能
    """
    
    def __init__(self, config=None):
        """
        初始化数据处理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.cache = {}
        self.cache_enabled = self.config.get('cache_enabled', True)
        
        # 初始化子模块
        self.quality_controller = get_quality_controller(config)
        self.indicators_calculator = get_indicators_calculator(config)
        self.factor_generator = get_factor_generator(config)
        
        # 技术指标参数
        self.indicator_windows = self.config.get(
            'indicator_windows', [5, 10, 20, 60]
        )
        
        logger.info("增强QLib数据处理器初始化完成")
    
    def preprocess_data_advanced(
        self, 
        data: pd.DataFrame,
        instrument: str = None
    ) -> pd.DataFrame:
        """
        高级数据预处理
        
        Args:
            data: 原始数据
            instrument: 股票代码（用于日志）
            
        Returns:
            预处理后的数据
        """
        return self.quality_controller.preprocess_data_advanced(data, instrument)
    
    def calculate_technical_indicators(
        self, 
        data: pd.DataFrame,
        indicators: List[str] = None
    ) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            data: 价格数据
            indicators: 指标列表
            
        Returns:
            包含技术指标的数据
        """
        return self.indicators_calculator.calculate_technical_indicators(
            data, indicators
        )
    
    def generate_factors(
        self,
        data: pd.DataFrame,
        factor_config: Dict[str, Any] = None
    ) -> pd.DataFrame:
        """
        生成因子
        
        Args:
            data: 价格数据
            factor_config: 因子配置
            
        Returns:
            因子数据
        """
        return self.factor_generator.generate_factors(data, factor_config)
    
    def process_data_complete(
        self,
        data: pd.DataFrame,
        instrument: str = None,
        indicators: List[str] = None,
        factor_config: Dict[str, Any] = None
    ) -> pd.DataFrame:
        """
        完整数据处理流程
        
        Args:
            data: 原始数据
            instrument: 股票代码
            indicators: 技术指标列表
            factor_config: 因子配置
            
        Returns:
            完整处理后的数据
        """
        try:
            logger.info(f"开始完整数据处理流程: {instrument or 'Unknown'}")
            
            # 1. 数据预处理
            processed_data = self.preprocess_data_advanced(data, instrument)
            
            # 2. 计算技术指标
            if indicators:
                processed_data = self.calculate_technical_indicators(
                    processed_data, indicators
                )
            
            # 3. 生成因子
            if factor_config:
                processed_data = self.generate_factors(
                    processed_data, factor_config
                )
            
            logger.info(f"完整数据处理流程完成: {len(processed_data)} 条记录")
            return processed_data
            
        except Exception as e:
            logger.error(f"完整数据处理流程失败: {e}")
            return data
    
    def get_available_indicators(self) -> List[str]:
        """
        获取可用的技术指标列表
        
        Returns:
            技术指标列表
        """
        return [
            'MA', 'EMA', 'RSI', 'MACD', 'BOLL', 
            'ATR', 'CCI', 'WILLR', 'MOM', 'KDJ'
        ]
    
    def get_available_factor_types(self) -> List[str]:
        """
        获取可用的因子类型列表
        
        Returns:
            因子类型列表
        """
        return [
            'momentum_factors',
            'reversal_factors',
            'volatility_factors',
            'volume_factors',
            'technical_factors',
            'cross_sectional_factors'
        ]


# 全局增强数据处理器实例
_global_enhanced_processor = None


def get_enhanced_data_processor(config=None) -> EnhancedQLibDataProcessor:
    """获取全局增强数据处理器实例"""
    global _global_enhanced_processor
    
    if _global_enhanced_processor is None:
        _global_enhanced_processor = EnhancedQLibDataProcessor(config)
    
    return _global_enhanced_processor


def test_enhanced_data_processor():
    """测试增强数据处理器"""
    print("=" * 70)
    print("测试增强QLib数据处理器")
    print("=" * 70)
    
    try:
        # 创建测试数据
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        test_data = pd.DataFrame({
            'datetime': dates,
            'open': 100 + np.random.randn(100).cumsum() * 0.1,
            'high': 100 + np.random.randn(100).cumsum() * 0.1 + np.random.rand(100) * 2,
            'low': 100 + np.random.randn(100).cumsum() * 0.1 - np.random.rand(100) * 2,
            'close': 100 + np.random.randn(100).cumsum() * 0.1,
            'volume': np.random.randint(1000, 10000, 100),
            'amount': np.random.randint(100000, 1000000, 100)
        })
        
        # 添加一些异常值和缺失值
        test_data.loc[10:15, 'close'] = 200  # 异常值
        test_data.loc[20:25, 'volume'] = np.nan  # 缺失值
        
        print(f"📊 测试数据: {len(test_data)} 条记录")
        
        # 创建增强处理器
        processor = EnhancedQLibDataProcessor({
            'outlier_method': 'iqr',
            'missing_method': 'interpolate',
            'indicator_windows': [5, 10, 20]
        })
        
        # 测试数据预处理
        processed_data = processor.preprocess_data_advanced(
            test_data, 'TEST000001'
        )
        print(f"✅ 数据预处理完成: {len(processed_data)} 条记录")
        print(f"📈 预处理后列数: {len(processed_data.columns)}")
        
        # 测试技术指标计算
        indicator_data = processor.calculate_technical_indicators(processed_data)
        print(f"🔧 技术指标计算完成: {len(indicator_data.columns)} 个指标")
        
        # 测试因子生成
        factor_config = {
            'momentum_factors': True,
            'reversal_factors': True,
            'volatility_factors': True,
            'volume_factors': True,
            'technical_factors': True,
            'cross_sectional_factors': True
        }
        factor_data = processor.generate_factors(processed_data, factor_config)
        print(f"📊 因子生成完成: {len(factor_data.columns)} 个因子")
        
        # 测试完整处理流程
        complete_data = processor.process_data_complete(
            test_data,
            instrument='TEST000001',
            indicators=['MA', 'EMA', 'RSI', 'MACD'],
            factor_config=factor_config
        )
        print(f"🎯 完整处理完成: {len(complete_data.columns)} 列")
        
        print("✅ 增强QLib数据处理器测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 增强QLib数据处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_enhanced_data_processor()