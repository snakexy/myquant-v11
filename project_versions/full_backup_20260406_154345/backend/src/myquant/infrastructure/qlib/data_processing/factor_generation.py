"""
因子生成模块
提供各种量化因子的生成功能
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
)

logger = logging.getLogger(__name__)

# 尝试导入高级数据处理库
try:
    from sklearn.preprocessing import RobustScaler
    SKLEARN_AVAILABLE = True
    logger.info("✅ Scikit-learn数据预处理库导入成功")
except ImportError as e:
    SKLEARN_AVAILABLE = False
    logger.warning(f"⚠️ Scikit-learn不可用，将使用基础标准化: {e}")


class FactorGenerator:
    """
    因子生成器
    
    提供各种量化因子的生成功能
    """
    
    def __init__(self, config=None):
        """
        初始化因子生成器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        
        logger.info("因子生成器初始化完成")
    
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
        if factor_config is None:
            factor_config = {
                'momentum_factors': True,
                'reversal_factors': True,
                'volatility_factors': True,
                'volume_factors': True,
                'technical_factors': True,
                'cross_sectional_factors': True
            }
        
        try:
            factor_data = data.copy()
            
            # 动量因子
            if factor_config.get('momentum_factors', False):
                factor_data = self._generate_momentum_factors(factor_data)
            
            # 反转因子
            if factor_config.get('reversal_factors', False):
                factor_data = self._generate_reversal_factors(factor_data)
            
            # 波动率因子
            if factor_config.get('volatility_factors', False):
                factor_data = self._generate_volatility_factors(factor_data)
            
            # 成交量因子
            if factor_config.get('volume_factors', False):
                factor_data = self._generate_volume_factors(factor_data)
            
            # 技术因子
            if factor_config.get('technical_factors', False):
                factor_data = self._generate_technical_factors(factor_data)
            
            # 截面因子
            if factor_config.get('cross_sectional_factors', False):
                factor_data = self._generate_cross_sectional_factors(factor_data)
            
            # 因子标准化
            factor_data = self._standardize_factors(factor_data)
            
            logger.debug(f"生成高级因子: {len(factor_data.columns)} 个因子")
            return factor_data
            
        except Exception as e:
            logger.error(f"生成高级因子失败: {e}")
            return data
    
    def _generate_momentum_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成动量因子"""
        if 'close' not in data.columns:
            return data
        
        # 确保close列为float64类型
        data['close'] = data['close'].astype('float64')
        
        # 价格动量
        for period in [5, 10, 20, 60]:
            if len(data) > period:
                col_name = f'momentum_{period}'
                data[col_name] = data['close'].pct_change(period).astype('float64')
        
        # 技术动量
        if len(data) > 20:
            ma20 = data['close'].rolling(20).mean().astype('float64')
            data['price_ma20_ratio'] = (data['close'] / ma20).astype('float64')
        
        return data
    
    def _generate_reversal_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成反转因子"""
        if 'close' not in data.columns:
            return data
        
        # 确保数值列为float64类型
        for col in ['close', 'high', 'low']:
            if col in data.columns:
                data[col] = data[col].astype('float64')
        
        # 短期反转
        for period in [1, 3, 5]:
            if len(data) > period:
                col_name = f'reversal_{period}'
                data[col_name] = (-data['close'].pct_change(period)).astype('float64')
        
        # 价格位置
        if len(data) > 20 and all(col in data.columns for col in ['high', 'low']):
            high20 = data['high'].rolling(20).max().astype('float64')
            low20 = data['low'].rolling(20).min().astype('float64')
            # 避免除零错误
            denominator = (high20 - low20)
            denominator = denominator.replace(0, np.nan)  # 避免除零
            data['price_position'] = (
                (data['close'] - low20) / denominator
            ).astype('float64')
        
        return data
    
    def _generate_volatility_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成波动率因子"""
        if 'close' not in data.columns:
            return data
        
        # 确保数值列为float64类型
        for col in ['close', 'high', 'low']:
            if col in data.columns:
                data[col] = data[col].astype('float64')
        
        # 已实现波动率
        for period in [5, 10, 20]:
            if len(data) > period:
                col_name = f'volatility_{period}'
                data[col_name] = (
                    data['close'].pct_change().rolling(period).std().astype('float64')
                )
        
        # ATR波动率
        if all(col in data.columns for col in ['high', 'low']):
            # 计算ATR
            tr1 = data['high'] - data['low']
            tr2 = abs(data['high'] - data['close'].shift(1))
            tr3 = abs(data['low'] - data['close'].shift(1))
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            data['ATR'] = true_range.rolling(14).mean()
            
            if 'ATR' in data.columns:
                # 避免除零错误
                close_values = data['close'].replace(0, np.nan)
                data['atr_ratio'] = (data['ATR'] / close_values).astype('float64')
        
        return data
    
    def _generate_volume_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成成交量因子"""
        if 'volume' not in data.columns:
            return data
        
        # 确保数值列为float64类型
        for col in ['volume', 'close']:
            if col in data.columns:
                data[col] = data[col].astype('float64')
        
        # 成交量移动平均
        for period in [5, 10, 20]:
            if len(data) > period:
                ma_col = f'volume_ma_{period}'
                ratio_col = f'volume_ratio_{period}'
                data[ma_col] = data['volume'].rolling(period).mean().astype('float64')
                # 避免除零错误
                volume_ma = data[ma_col].replace(0, np.nan)
                data[ratio_col] = (data['volume'] / volume_ma).astype('float64')
        
        # 价量关系
        if 'close' in data.columns:
            data['price_volume_trend'] = (
                (data['close'] * data['volume']).astype('float64')
            )
        
        return data
    
    def _generate_technical_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成技术因子"""
        # 这里可以调用技术指标计算模块
        from .technical_indicators import get_indicators_calculator
        
        try:
            calculator = get_indicators_calculator()
            data = calculator.calculate_technical_indicators(data)
            
            # 技术指标衍生因子
            if 'RSI' in data.columns:
                data['RSI_overbought'] = (data['RSI'] > 70).astype(int)
                data['RSI_oversold'] = (data['RSI'] < 30).astype(int)
            
            if 'MACD' in data.columns and 'MACD_signal' in data.columns:
                data['MACD_bullish'] = (
                    data['MACD'] > data['MACD_signal']
                ).astype(int)
            
        except Exception as e:
            logger.warning(f"技术因子生成失败: {e}")
        
        return data
    
    def _generate_cross_sectional_factors(
        self, data: pd.DataFrame
    ) -> pd.DataFrame:
        """生成截面因子"""
        # 这里需要多股票数据，单股票数据暂时跳过
        return data
    
    def _standardize_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """标准化因子"""
        # 确保只处理数值型因子列
        factor_columns = []
        for col in data.columns:
            if col not in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                # 检查是否为数值类型
                if pd.api.types.is_numeric_dtype(data[col]):
                    factor_columns.append(col)
        
        if not SKLEARN_AVAILABLE:
            # 使用简单的Z-Score标准化
            for col in factor_columns:
                if data[col].std() > 0:
                    # 确保数据类型为float64以避免精度问题
                    data[col] = data[col].astype('float64')
                    mean_val = data[col].mean()
                    std_val = data[col].std()
                    data[col] = (data[col] - mean_val) / std_val
            
            return data
        
        # 使用RobustScaler标准化（对异常值更鲁棒）
        if factor_columns:
            # 确保数据类型兼容性
            for col in factor_columns:
                data[col] = data[col].astype('float64')
            
            scaler = RobustScaler()
            data[factor_columns] = scaler.fit_transform(data[factor_columns])
        
        return data


# 全局因子生成器实例
_global_factor_generator = None


def get_factor_generator(config=None) -> FactorGenerator:
    """获取全局因子生成器实例"""
    global _global_factor_generator
    
    if _global_factor_generator is None:
        _global_factor_generator = FactorGenerator(config)
    
    return _global_factor_generator