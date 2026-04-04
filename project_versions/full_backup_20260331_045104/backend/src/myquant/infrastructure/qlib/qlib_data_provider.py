"""
QLib数据提供器
将DataManagerV2的数据提供给QLib使用
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

logger = logging.getLogger(__name__)

# 尝试导入QLib
try:
    import qlib
    from qlib.data.dataset import Dataset
    from qlib.data.dataset.handler import DataHandlerLP
    from qlib.contrib.data.handler import Alpha158
    # 注意：qlib.data.ops 中的指标函数在0.9.8.dev15中可能不存在，我们避免导入
    # 如果需要使用这些函数，可以通过其他方式实现
    # 尝试导入EMA，如果不存在则设置为None
    try:
        from qlib.data.ops import EMA
    except ImportError:
        EMA = None
    # MACD, RSI, MA, REF, DELTA, SIGN, POW 可能不存在，我们将用自定义实现
    # 尝试导入TopkDropoutStrategy，它可能在 qlib.contrib.strategy 中
    from qlib.contrib.strategy import TopkDropoutStrategy
    
    QLIB_AVAILABLE = True
    logger.info("✅ QLib数据模块导入成功")
except ImportError as e:
    QLIB_AVAILABLE = False
    logger.error(f"❌ QLib数据模块导入失败: {e}")
    
    # 定义占位符类
    class Dataset:
        def __init__(self, **kwargs):
            pass
    
    class DataHandlerLP:
        def __init__(self, **kwargs):
            pass
    
    class Alpha158:
        def __init__(self, **kwargs):
            pass

# 尝试导入TA-Lib用于技术指标计算
try:
    import talib
    TA_LIB_AVAILABLE = True
    logger.info("✅ TA-Lib模块导入成功")
except ImportError as e:
    TA_LIB_AVAILABLE = False
    logger.warning(f"❌ TA-Lib模块导入失败，将使用自定义技术指标计算: {e}")


class QLibDataProvider:
    """
    QLib数据提供器
    负责将DataManagerV2的数据转换为QLib可用的格式
    """

    def __init__(self, data_hub=None, config=None):
        """
        初始化数据提供器

        Args:
            data_hub: DataManagerV2实例
            config: 配置参数
        """
        self.data_hub = data_hub
        self.config = config or {}
        self.cache = {}
        self.cache_enabled = self.config.get('cache_enabled', True)

        logger.info("QLib数据提供器初始化完成")
    
    def prepare_qlib_data(
        self, 
        instruments: List[str], 
        start_date: str, 
        end_date: str,
        fields: List[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        准备QLib数据
        
        Args:
            instruments: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            fields: 需要的字段列表
            
        Returns:
            股票数据字典 {股票代码: DataFrame}
        """
        if not self.data_hub:
            logger.error("数据中枢未初始化")
            return {}
        
        # 默认字段
        if fields is None:
            fields = ['open', 'high', 'low', 'close', 'volume', 'amount']
        
        data_dict = {}
        
        for instrument in instruments:
            try:
                # 检查缓存
                cache_key = f"{instrument}_{start_date}_{end_date}"
                if self.cache_enabled and cache_key in self.cache:
                    data_dict[instrument] = self.cache[cache_key]
                    continue

                # 从DataManagerV2获取数据
                data = self.data_hub.get_kline_data(
                    symbol=instrument,
                    start_date=start_date,
                    end_date=end_date,
                    frequency='day'
                )
                
                if not data.empty:
                    # 确保包含所需字段
                    missing_fields = [f for f in fields if f not in data.columns]
                    if missing_fields:
                        logger.warning(f"{instrument} 缺少字段: {missing_fields}")
                        continue
                    
                    # 数据清洗和预处理
                    data = self._preprocess_data(data)
                    
                    # 缓存数据
                    if self.cache_enabled:
                        self.cache[cache_key] = data
                    
                    data_dict[instrument] = data
                    logger.debug(f"准备 {instrument} 数据: {len(data)} 条记录")
                else:
                    logger.warning(f"{instrument} 数据为空")
                    
            except Exception as e:
                logger.error(f"准备 {instrument} 数据失败: {e}")
                continue
        
        logger.info(f"✅ 准备QLib数据完成: {len(data_dict)} 个股票")
        return data_dict
    
    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        数据预处理
        
        Args:
            data: 原始数据
            
        Returns:
            预处理后的数据
        """
        try:
            # 确保日期索引
            if 'datetime' in data.columns:
                data['date'] = pd.to_datetime(data['datetime'])
                data.set_index('date', inplace=True)
            elif 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
                data.set_index('date', inplace=True)
            
            # 数据类型转换
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in numeric_columns:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            # 处理缺失值
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            # 移除异常值
            for col in numeric_columns:
                if col in data.columns:
                    # 使用3σ规则移除异常值
                    mean = data[col].mean()
                    std = data[col].std()
                    data[col] = np.clip(data[col], mean - 3*std, mean + 3*std)
            
            return data
            
        except Exception as e:
            logger.error(f"数据预处理失败: {e}")
            return data
    
    def create_qlib_dataset(
        self,
        instruments: List[str],
        start_date: str,
        end_date: str,
        features: List[str] = None
    ) -> Optional[Dataset]:
        """
        创建QLib数据集
        
        Args:
            instruments: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            features: 特征列表
            
        Returns:
            QLib数据集
        """
        if not QLIB_AVAILABLE:
            logger.warning("QLib不可用，无法创建数据集")
            return None
        
        try:
            # 准备数据
            data_dict = self.prepare_qlib_data(instruments, start_date, end_date)
            
            if not data_dict:
                logger.error("没有可用数据，无法创建数据集")
                return None
            
            # 创建Alpha158处理器
            handler_config = {
                "class": "Alpha158",
                "module_path": "qlib.contrib.data.handler",
                "kwargs": {
                    "start_time": start_date,
                    "end_time": end_date,
                    "instruments": instruments,
                    "fit_start_time": start_date,
                    "fit_end_time": end_date
                }
            }
            
            # 创建数据集
            dataset = Dataset(
                handler=handler_config,
                segments={
                    "train": (start_date, end_date)
                }
            )
            
            logger.info("✅ QLib数据集创建成功")
            return dataset
            
        except Exception as e:
            logger.error(f"创建QLib数据集失败: {e}")
            return None
    
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
        if indicators is None:
            indicators = ['MA5', 'MA20', 'RSI', 'MACD', 'EMA12']
        
        try:
            result_data = data.copy()
            
            # 移动平均线
            if 'MA5' in indicators:
                result_data['MA5'] = data['close'].rolling(window=5).mean()
            if 'MA20' in indicators:
                result_data['MA20'] = data['close'].rolling(window=20).mean()
            
            # 指数移动平均
            if 'EMA12' in indicators:
                result_data['EMA12'] = data['close'].ewm(span=12).mean()
            
            # RSI
            if 'RSI' in indicators:
                delta = data['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                result_data['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            if 'MACD' in indicators:
                ema12 = data['close'].ewm(span=12).mean()
                ema26 = data['close'].ewm(span=26).mean()
                result_data['MACD'] = ema12 - ema26
                result_data['MACD_signal'] = result_data['MACD'].ewm(span=9).mean()
                result_data['MACD_hist'] = result_data['MACD'] - result_data['MACD_signal']
            
            logger.debug(f"计算技术指标: {indicators}")
            return result_data
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return data
    
    def generate_factor_data(
        self,
        instruments: List[str],
        start_date: str,
        end_date: str,
        factor_config: Dict[str, Any] = None
    ) -> pd.DataFrame:
        """
        生成因子数据
        
        Args:
            instruments: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            factor_config: 因子配置
            
        Returns:
            因子数据DataFrame
        """
        if factor_config is None:
            factor_config = {
                'momentum': {'window': 20},
                'reversal': {'window': 5},
                'volatility': {'window': 20},
                'volume': {'window': 20}
            }
        
        try:
            all_factors = []
            
            for instrument in instruments:
                # 获取价格数据
                data = self.data_hub.get_kline_data(
                    symbol=instrument,
                    start_date=start_date,
                    end_date=end_date,
                    frequency='day'
                )
                
                if data.empty:
                    continue
                
                # 计算各种因子
                factor_data = pd.DataFrame(index=data.index)
                factor_data['instrument'] = instrument
                
                # 动量因子
                if 'momentum' in factor_config:
                    window = factor_config['momentum']['window']
                    factor_data['momentum'] = data['close'].pct_change(window)
                
                # 反转因子
                if 'reversal' in factor_config:
                    window = factor_config['reversal']['window']
                    factor_data['reversal'] = -data['close'].pct_change(window)
                
                # 波动率因子
                if 'volatility' in factor_config:
                    window = factor_config['volatility']['window']
                    factor_data['volatility'] = data['close'].pct_change().rolling(window).std()
                
                # 成交量因子
                if 'volume' in factor_config:
                    window = factor_config['volume']['window']
                    factor_data['volume_ma'] = data['volume'].rolling(window).mean()
                    factor_data['volume_ratio'] = data['volume'] / factor_data['volume_ma']
                
                all_factors.append(factor_data)
            
            if all_factors:
                result_df = pd.concat(all_factors, ignore_index=False)
                logger.info(f"✅ 生成因子数据: {len(result_df)} 条记录")
                return result_df
            else:
                logger.warning("没有生成任何因子数据")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"生成因子数据失败: {e}")
            return pd.DataFrame()
    
    def get_universe_data(
        self,
        universe: str = 'csi300',
        start_date: str = None,
        end_date: str = None
    ) -> List[str]:
        """
        获取股票池数据
        
        Args:
            universe: 股票池类型
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            股票代码列表
        """
        try:
            if universe == 'csi300':
                # CSI300成分股（示例）
                instruments = [
                    'SH600000', 'SH600036', 'SH600519', 'SH601318',
                    'SZ000001', 'SZ000002', 'SZ000858', 'SZ002415'
                ]
            elif universe == 'csi500':
                # CSI500成分股（示例）
                instruments = [
                    'SH600000', 'SH600036', 'SH600519',
                    'SZ000001', 'SZ000002', 'SZ000858'
                ]
            else:
                # 默认股票池
                instruments = ['SH600000', 'SZ000001', 'SH600036', 'SZ000002']
            
            logger.info(f"获取股票池 {universe}: {len(instruments)} 个股票")
            return instruments
            
        except Exception as e:
            logger.error(f"获取股票池数据失败: {e}")
            return []
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("数据缓存已清空")


# 全局数据提供器实例
_global_data_provider = None


def get_qlib_data_provider(data_hub=None, config=None) -> QLibDataProvider:
    """
    获取全局QLib数据提供器实例
    
    Args:
        data_hub: 数据中枢实例
        config: 配置参数
        
    Returns:
        QLibDataProvider实例
    """
    global _global_data_provider
    
    if _global_data_provider is None:
        _global_data_provider = QLibDataProvider(data_hub, config)
    
    return _global_data_provider


def create_qlib_custom_provider():
    """创建自定义QLib数据提供器（兼容性函数）"""
    return QLibDataProvider()


def test_qlib_data_provider():
    """测试QLib数据提供器"""
    print("=" * 70)
    print("测试QLib数据提供器")
    print("=" * 70)
    
    try:
        # 创建数据提供器
        provider = QLibDataProvider()
        
        # 测试获取股票池
        universe = provider.get_universe_data('csi300')
        print(f"📊 股票池: {len(universe)} 个股票")
        
        # 测试准备数据
        if universe:
            test_instruments = universe[:3]  # 只测试前3个股票
            data_dict = provider.prepare_qlib_data(
                test_instruments, 
                "2020-01-01", 
                "2020-01-31"
            )
            
            print(f"📈 准备数据: {len(data_dict)} 个股票")
            for symbol, data in data_dict.items():
                print(f"   {symbol}: {len(data)} 条记录")
        
        # 测试技术指标计算
        if data_dict:
            test_data = list(data_dict.values())[0]
            indicator_data = provider.calculate_technical_indicators(test_data)
            print(f"🔧 技术指标: {len(indicator_data.columns)} 个指标")
        
        # 测试因子生成
        if universe:
            factor_data = provider.generate_factor_data(
                universe[:3],
                "2020-01-01",
                "2020-01-31"
            )
            print(f"📊 因子数据: {len(factor_data)} 条记录")
        
        print("✅ QLib数据提供器测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ QLib数据提供器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_qlib_data_provider()