"""
QLib策略适配器
将自定义策略转换为QLib可用的策略格式
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

logger = logging.getLogger(__name__)

# 尝试导入QLib
try:
    from qlib.strategy.base import BaseStrategy
    from qlib.contrib.strategy import TopkDropoutStrategy
    # BaseSignalStrategy 位于 qlib.contrib.strategy.signal_strategy 中
    from qlib.contrib.strategy.signal_strategy import BaseSignalStrategy
    # Position 可能位于 qlib.backtest.position 或 qlib.contrib.strategy.signal_strategy
    from qlib.contrib.strategy.signal_strategy import Position
    
    QLIB_AVAILABLE = True
    logger.info("✅ QLib策略模块导入成功")
except ImportError as e:
    QLIB_AVAILABLE = False
    logger.error(f"❌ QLib策略模块导入失败: {e}")
    
    # 定义占位符类
    class BaseStrategy:
        def __init__(self, **kwargs):
            pass
    
    class TopkDropoutStrategy:
        def __init__(self, **kwargs):
            pass
    
    class BaseSignalStrategy:
        def __init__(self, **kwargs):
            pass
    
    class Position:
        def __init__(self, **kwargs):
            pass


class QLibStrategyAdapter:
    """
    QLib策略适配器
    负责将自定义策略配置转换为QLib策略对象
    """
    
    def __init__(self, data_provider=None):
        """
        初始化策略适配器
        
        Args:
            data_provider: 数据提供器实例
        """
        self.data_provider = data_provider
        self.strategy_cache = {}

        logger.info("QLib策略适配器初始化完成")

    def list_strategies(self) -> List[Dict[str, Any]]:
        """
        获取支持的策略列表

        Returns:
            策略列表，每个策略包含name、type、description等信息
        """
        strategies = [
            {
                "name": "TopkDropout",
                "type": "TopkDropout",
                "description": "Topk跌停策略 - 选择表现最好的N个股票，并定期调整",
                "parameters": {
                    "topk": {"type": "int", "default": 50, "description": "保留股票数量"},
                    "n_drop": {"type": "int", "default": 5, "description": "每次调仓时丢弃的股票数量"}
                }
            },
            {
                "name": "Signal",
                "type": "Signal",
                "description": "信号策略 - 基于自定义信号进行股票选择和调仓",
                "parameters": {
                    "signal": {"type": "str", "default": "$close", "description": "信号表达式"}
                }
            },
            {
                "name": "Momentum",
                "type": "Momentum",
                "description": "动量策略 - 基于股票动量因子进行投资",
                "parameters": {
                    "window": {"type": "int", "default": 20, "description": "动量计算窗口"},
                    "topk": {"type": "int", "default": 30, "description": "选择股票数量"}
                }
            },
            {
                "name": "MeanReversion",
                "type": "MeanReversion",
                "description": "均值回归策略 - 基于价格均值回归进行投资",
                "parameters": {
                    "window": {"type": "int", "default": 20, "description": "均值计算窗口"},
                    "topk": {"type": "int", "default": 30, "description": "选择股票数量"}
                }
            }
        ]

        logger.info(f"返回策略列表，共 {len(strategies)} 个策略")
        return strategies

    def create_strategy(
        self, 
        strategy_config: Dict[str, Any],
        signal_data: pd.DataFrame = None
    ) -> Optional[BaseStrategy]:
        """
        创建QLib策略对象
        
        Args:
            strategy_config: 策略配置
            signal_data: 信号数据
            
        Returns:
            QLib策略对象
        """
        if not QLIB_AVAILABLE:
            logger.warning("QLib不可用，无法创建策略")
            return None
        
        try:
            strategy_type = strategy_config.get("type", "TopkDropout")
            
            if strategy_type == "TopkDropout":
                return self._create_topk_dropout_strategy(
                    strategy_config, signal_data
                )
            elif strategy_type == "Signal":
                return self._create_signal_strategy(
                    strategy_config, signal_data
                )
            elif strategy_type == "Momentum":
                return self._create_momentum_strategy(
                    strategy_config, signal_data
                )
            elif strategy_type == "MeanReversion":
                return self._create_mean_reversion_strategy(
                    strategy_config, signal_data
                )
            else:
                logger.error(f"不支持的策略类型: {strategy_type}")
                return None
                
        except Exception as e:
            logger.error(f"创建策略失败: {e}")
            return None
    
    def _create_topk_dropout_strategy(
        self, 
        strategy_config: Dict[str, Any],
        signal_data: pd.DataFrame = None
    ) -> Optional[TopkDropoutStrategy]:
        """创建TopkDropout策略"""
        try:
            # 获取策略参数
            topk = strategy_config.get("topk", 50)
            n_drop = strategy_config.get("n_drop", 5)
            
            # 生成或使用信号数据
            if signal_data is None:
                signal_data = self._generate_signal_data(strategy_config)
            
            if signal_data.empty:
                logger.warning("信号数据为空，无法创建策略")
                return None
            
            # 创建策略
            strategy = TopkDropoutStrategy(
                topk=topk,
                n_drop=n_drop,
                signal=signal_data
            )
            
            logger.info(f"✅ 创建TopkDropout策略: topk={topk}, n_drop={n_drop}")
            return strategy
            
        except Exception as e:
            logger.error(f"创建TopkDropout策略失败: {e}")
            return None
    
    def _create_signal_strategy(
        self, 
        strategy_config: Dict[str, Any],
        signal_data: pd.DataFrame = None
    ) -> Optional[BaseSignalStrategy]:
        """创建信号策略"""
        try:
            # 获取策略参数
            model = strategy_config.get("model", None)
            
            # 生成或使用信号数据
            if signal_data is None:
                signal_data = self._generate_signal_data(strategy_config)
            
            if signal_data.empty:
                logger.warning("信号数据为空，无法创建策略")
                return None
            
            # 创建策略
            strategy = BaseSignalStrategy(signal=signal_data, model=model)
            
            logger.info(f"✅ 创建信号策略: model={model}")
            return strategy
            
        except Exception as e:
            logger.error(f"创建信号策略失败: {e}")
            return None
    
    def _create_momentum_strategy(
        self, 
        strategy_config: Dict[str, Any],
        signal_data: pd.DataFrame = None
    ) -> Optional[TopkDropoutStrategy]:
        """创建动量策略（基于TopkDropout）"""
        try:
            # 获取动量策略参数
            lookback = strategy_config.get("lookback", 20)
            topk = strategy_config.get("topk", 30)
            
            # 生成动量信号
            if signal_data is None:
                signal_data = self._generate_momentum_signal(
                    strategy_config, lookback
                )
            
            if signal_data.empty:
                logger.warning("动量信号数据为空，无法创建策略")
                return None
            
            # 创建策略
            strategy = TopkDropoutStrategy(
                topk=topk,
                n_drop=3,
                signal=signal_data
            )
            
            logger.info(f"✅ 创建动量策略: lookback={lookback}, topk={topk}")
            return strategy
            
        except Exception as e:
            logger.error(f"创建动量策略失败: {e}")
            return None
    
    def _create_mean_reversion_strategy(
        self, 
        strategy_config: Dict[str, Any],
        signal_data: pd.DataFrame = None
    ) -> Optional[TopkDropoutStrategy]:
        """创建均值回归策略（基于TopkDropout）"""
        try:
            # 获取均值回归策略参数
            lookback = strategy_config.get("lookback", 20)
            zscore_threshold = strategy_config.get("zscore_threshold", 2.0)
            topk = strategy_config.get("topk", 30)
            
            # 生成均值回归信号
            if signal_data is None:
                signal_data = self._generate_mean_reversion_signal(
                    strategy_config, lookback, zscore_threshold
                )
            
            if signal_data.empty:
                logger.warning("均值回归信号数据为空，无法创建策略")
                return None
            
            # 创建策略
            strategy = TopkDropoutStrategy(
                topk=topk,
                n_drop=3,
                signal=signal_data
            )
            
            logger.info(f"✅ 创建均值回归策略: lookback={lookback}, threshold={zscore_threshold}")
            return strategy
            
        except Exception as e:
            logger.error(f"创建均值回归策略失败: {e}")
            return None
    
    def _generate_signal_data(self, strategy_config: Dict[str, Any]) -> pd.DataFrame:
        """生成策略信号数据"""
        try:
            # 获取配置参数
            instruments = strategy_config.get("instruments", [])
            start_date = strategy_config.get("start_date", "2020-01-01")
            end_date = strategy_config.get("end_date", "2023-12-31")
            
            if not instruments:
                logger.warning("未指定股票池，使用默认股票")
                instruments = ['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318']
            
            # 创建日期范围
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # 生成信号数据
            records = []
            for date in dates:
                for instrument in instruments:
                    # 根据策略类型生成不同的信号
                    signal_value = self._calculate_signal_value(
                        instrument, date, strategy_config
                    )
                    records.append({
                        'datetime': date,
                        'instrument': instrument,
                        'score': signal_value
                    })
            
            signal_df = pd.DataFrame(records)
            signal_df = signal_df.set_index(['datetime', 'instrument'])
            
            logger.debug(f"生成信号数据: {len(signal_df)} 条记录")
            return signal_df
            
        except Exception as e:
            logger.error(f"生成信号数据失败: {e}")
            return pd.DataFrame()
    
    def _generate_momentum_signal(
        self, 
        strategy_config: Dict[str, Any], 
        lookback: int
    ) -> pd.DataFrame:
        """生成动量信号"""
        try:
            instruments = strategy_config.get("instruments", [])
            start_date = strategy_config.get("start_date", "2020-01-01")
            end_date = strategy_config.get("end_date", "2023-12-31")
            
            if not instruments:
                instruments = ['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318']
            
            records = []
            
            for instrument in instruments:
                if self.data_provider:
                    # 从数据提供器获取价格数据
                    data = self.data_provider.prepare_qlib_data(
                        [instrument], start_date, end_date
                    )
                    
                    if instrument in data:
                        price_data = data[instrument]
                        # 计算动量信号
                        for i, (date, row) in enumerate(price_data.iterrows()):
                            if i >= lookback:
                                momentum = (row['close'] / price_data.iloc[i-lookback]['close'] - 1)
                                records.append({
                                    'datetime': date,
                                    'instrument': instrument,
                                    'score': momentum
                                })
                else:
                    # 生成模拟动量信号
                    dates = pd.date_range(start=start_date, end=end_date, freq='D')
                    for date in dates:
                        momentum = np.random.normal(0.001, 0.02)
                        records.append({
                            'datetime': date,
                            'instrument': instrument,
                            'score': momentum
                        })
            
            signal_df = pd.DataFrame(records)
            if not signal_df.empty:
                signal_df = signal_df.set_index(['datetime', 'instrument'])
            
            return signal_df
            
        except Exception as e:
            logger.error(f"生成动量信号失败: {e}")
            return pd.DataFrame()
    
    def _generate_mean_reversion_signal(
        self, 
        strategy_config: Dict[str, Any], 
        lookback: int,
        zscore_threshold: float
    ) -> pd.DataFrame:
        """生成均值回归信号"""
        try:
            instruments = strategy_config.get("instruments", [])
            start_date = strategy_config.get("start_date", "2020-01-01")
            end_date = strategy_config.get("end_date", "2023-12-31")
            
            if not instruments:
                instruments = ['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318']
            
            records = []
            
            for instrument in instruments:
                if self.data_provider:
                    # 从数据提供器获取价格数据
                    data = self.data_provider.prepare_qlib_data(
                        [instrument], start_date, end_date
                    )
                    
                    if instrument in data:
                        price_data = data[instrument]
                        # 计算均值回归信号
                        for i, (date, row) in enumerate(price_data.iterrows()):
                            if i >= lookback:
                                # 计算Z分数
                                prices = price_data.iloc[i-lookback:i]['close']
                                mean_price = prices.mean()
                                std_price = prices.std()
                                zscore = (row['close'] - mean_price) / std_price
                                
                                # 均值回归信号：负的Z分数
                                signal_value = -zscore
                                records.append({
                                    'datetime': date,
                                    'instrument': instrument,
                                    'score': signal_value
                                })
                else:
                    # 生成模拟均值回归信号
                    dates = pd.date_range(start=start_date, end=end_date, freq='D')
                    for date in dates:
                        signal_value = np.random.normal(0, 1)
                        records.append({
                            'datetime': date,
                            'instrument': instrument,
                            'score': signal_value
                        })
            
            signal_df = pd.DataFrame(records)
            if not signal_df.empty:
                signal_df = signal_df.set_index(['datetime', 'instrument'])
            
            return signal_df
            
        except Exception as e:
            logger.error(f"生成均值回归信号失败: {e}")
            return pd.DataFrame()
    
    def _calculate_signal_value(
        self, 
        instrument: str, 
        date: datetime, 
        strategy_config: Dict[str, Any]
    ) -> float:
        """计算单个股票在特定日期的信号值"""
        strategy_type = strategy_config.get("type", "TopkDropout")
        
        if strategy_type == "Momentum":
            return self._calculate_momentum_signal(instrument, date, strategy_config)
        elif strategy_type == "MeanReversion":
            return self._calculate_mean_reversion_signal(instrument, date, strategy_config)
        else:
            # 默认随机信号
            return np.random.randn()
    
    def _calculate_momentum_signal(
        self, 
        instrument: str, 
        date: datetime, 
        strategy_config: Dict[str, Any]
    ) -> float:
        """计算动量信号"""
        try:
            lookback = strategy_config.get("lookback", 20)
            
            if self.data_provider:
                # 从数据提供器获取历史数据
                end_date = date.strftime('%Y-%m-%d')
                start_date = (date - timedelta(days=lookback*2)).strftime('%Y-%m-%d')
                
                data = self.data_provider.prepare_qlib_data(
                    [instrument], start_date, end_date
                )
                
                if instrument in data and len(data[instrument]) >= lookback:
                    price_data = data[instrument]
                    momentum = (price_data['close'].iloc[-1] / price_data['close'].iloc[-lookback] - 1)
                    return float(momentum)
            
            # 回退到随机信号
            return np.random.normal(0.001, 0.02)
            
        except Exception as e:
            logger.debug(f"计算动量信号失败: {e}")
            return np.random.randn()
    
    def _calculate_mean_reversion_signal(
        self, 
        instrument: str, 
        date: datetime, 
        strategy_config: Dict[str, Any]
    ) -> float:
        """计算均值回归信号"""
        try:
            lookback = strategy_config.get("lookback", 20)
            
            if self.data_provider:
                # 从数据提供器获取历史数据
                end_date = date.strftime('%Y-%m-%d')
                start_date = (date - timedelta(days=lookback*2)).strftime('%Y-%m-%d')
                
                data = self.data_provider.prepare_qlib_data(
                    [instrument], start_date, end_date
                )
                
                if instrument in data and len(data[instrument]) >= lookback:
                    price_data = data[instrument]
                    prices = price_data['close'].iloc[-lookback:]
                    mean_price = prices.mean()
                    std_price = prices.std()
                    zscore = (price_data['close'].iloc[-1] - mean_price) / std_price
                    return -float(zscore)  # 均值回归，负的Z分数
            
            # 回退到随机信号
            return np.random.randn()
            
        except Exception as e:
            logger.debug(f"计算均值回归信号失败: {e}")
            return np.random.randn()
    
    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """获取可用策略列表"""
        strategies = [
            {
                "name": "TopK策略",
                "type": "TopkDropout",
                "description": "基于因子排名的TopK选股策略",
                "parameters": {
                    "topk": {"type": "int", "default": 50, "min": 10, "max": 200},
                    "n_drop": {"type": "int", "default": 5, "min": 0, "max": 20}
                }
            },
            {
                "name": "信号策略",
                "type": "Signal",
                "description": "基于预测信号的策略",
                "parameters": {
                    "model": {"type": "str", "default": "lgb", "options": ["lgb", "linear"]}
                }
            },
            {
                "name": "动量策略",
                "type": "Momentum",
                "description": "基于价格动量的选股策略",
                "parameters": {
                    "lookback": {"type": "int", "default": 20, "min": 5, "max": 60},
                    "topk": {"type": "int", "default": 30, "min": 10, "max": 100}
                }
            },
            {
                "name": "均值回归策略",
                "type": "MeanReversion",
                "description": "基于均值回归的选股策略",
                "parameters": {
                    "lookback": {"type": "int", "default": 20, "min": 5, "max": 60},
                    "zscore_threshold": {"type": "float", "default": 2.0, "min": 1.0, "max": 3.0},
                    "topk": {"type": "int", "default": 30, "min": 10, "max": 100}
                }
            }
        ]
        
        return strategies
    
    def validate_strategy_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """验证策略配置"""
        required_fields = ["name", "type"]
        
        for field in required_fields:
            if field not in config:
                return False, f"缺少必需字段: {field}"
        
        # 验证策略类型
        available_strategies = self.get_available_strategies()
        strategy_types = [s["type"] for s in available_strategies]
        
        if config["type"] not in strategy_types:
            return False, f"不支持的策略类型: {config['type']}"
        
        return True, "配置验证通过"


# 全局策略适配器实例
_global_strategy_adapter = None


def get_qlib_strategy_adapter(data_provider=None) -> QLibStrategyAdapter:
    """
    获取全局QLib策略适配器实例
    
    Args:
        data_provider: 数据提供器实例
        
    Returns:
        QLibStrategyAdapter实例
    """
    global _global_strategy_adapter
    
    if _global_strategy_adapter is None:
        _global_strategy_adapter = QLibStrategyAdapter(data_provider)
    
    return _global_strategy_adapter


def test_qlib_strategy_adapter():
    """测试QLib策略适配器"""
    print("=" * 70)
    print("测试QLib策略适配器")
    print("=" * 70)
    
    try:
        # 创建策略适配器
        adapter = QLibStrategyAdapter()
        
        # 测试策略列表
        strategies = adapter.get_available_strategies()
        print(f"📋 可用策略: {len(strategies)} 个")
        for strategy in strategies:
            print(f"   📊 {strategy['name']}: {strategy['description']}")
        
        # 测试策略创建
        test_configs = [
            {
                "name": "测试TopK策略",
                "type": "TopkDropout",
                "topk": 30,
                "n_drop": 3,
                "instruments": ['SH600000', 'SZ000001', 'SH600036'],
                "start_date": "2020-01-01",
                "end_date": "2020-12-31"
            },
            {
                "name": "测试动量策略",
                "type": "Momentum",
                "lookback": 20,
                "topk": 30,
                "instruments": ['SH600000', 'SZ000001', 'SH600036'],
                "start_date": "2020-01-01",
                "end_date": "2020-12-31"
            }
        ]
        
        for config in test_configs:
            # 验证配置
            is_valid, message = adapter.validate_strategy_config(config)
            print(f"✅ 策略配置验证: {message}")
            
            if is_valid:
                # 创建策略
                strategy = adapter.create_strategy(config)
                if strategy:
                    print(f"🎉 策略创建成功: {config['name']}")
                else:
                    print(f"❌ 策略创建失败: {config['name']}")
        
        print("✅ QLib策略适配器测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ QLib策略适配器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_qlib_strategy_adapter()