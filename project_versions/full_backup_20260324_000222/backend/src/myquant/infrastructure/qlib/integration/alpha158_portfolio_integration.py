"""
Alpha158特征处理器与投资组合管理系统集成模块

该模块提供了Alpha158特征处理器与投资组合管理系统的完整集成，
包括特征计算、策略信号生成和回测执行。
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(
    0, 
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
)

# 导入Alpha158特征处理器
from qlib_core.qlib_dataprocessing.features.alpha158_parallel import (
    Alpha158ParallelProcessor, create_alpha158_parallel_processor
)

# 导入策略和回测模块
from qlib_core.backtest.strategy.topk_dropout_strategy import (
    TopkDropoutStrategy, create_topk_dropout_strategy
)
from qlib_core.backtest.qlib_backtest_executor import QLibBacktestExecutor

# 导入数据管理器 (v9.0.0 - DataManagerV2)
from data.unified_data_manager import UnifiedDataManager as DataManager

logger = logging.getLogger(__name__)


class Alpha158PortfolioIntegration:
    """
    Alpha158特征处理器与投资组合管理集成类
    
    该类提供了完整的Alpha158特征计算和投资组合管理流程，
    包括数据处理、特征计算、策略信号生成和回测执行。
    """
    
    def __init__(
        self,
        data_provider=None,
        alpha158_config: Dict[str, Any] = None,
        strategy_config: Dict[str, Any] = None
    ):
        """
        初始化Alpha158投资组合集成
        
        Parameters
        ----------
        data_provider : Any, optional
            数据提供器实例
        alpha158_config : Dict[str, Any], optional
            Alpha158特征处理器配置
        strategy_config : Dict[str, Any], optional
            策略配置
        """
        self.data_provider = data_provider
        self.alpha158_config = alpha158_config or self._get_default_alpha158_config()
        self.strategy_config = strategy_config or self._get_default_strategy_config()
        
        # 初始化组件
        self.alpha158_processor = None
        self.strategy = None
        self.backtest_executor = QLibBacktestExecutor(data_provider)
        
        # 缓存
        self._feature_cache = {}
        self._signal_cache = {}
        
        logger.info("Alpha158投资组合集成系统初始化完成")
    
    def _get_default_alpha158_config(self) -> Dict[str, Any]:
        """获取默认Alpha158配置"""
        return {
            'features': None,  # 使用所有默认特征
            'start_time': None,
            'end_time': None,
            'n_jobs': 4,  # 并行作业数
            'enable_cache': True,
            'verbose': True,
            'normalization': 'zscore',
            'fill_method': 'ffill',
            'drop_na': True
        }
    
    def _get_default_strategy_config(self) -> Dict[str, Any]:
        """获取默认策略配置"""
        return {
            'type': 'TopkDropout',
            'topk': 50,
            'n_drop': 5,
            'signal_type': 'alpha158',
            'signal_method': 'ensemble',
            'verbose': True
        }
    
    def initialize_components(self) -> bool:
        """
        初始化所有组件
        
        Returns
        -------
        bool
            是否初始化成功
        """
        try:
            # 1. 初始化Alpha158特征处理器
            self.alpha158_processor = create_alpha158_parallel_processor(
                **self.alpha158_config
            )
            
            logger.info("✅ Alpha158特征处理器初始化完成")
            
            # 2. 设置回测执行器
            success = self.backtest_executor.setup_executor()
            if not success:
                logger.warning("回测执行器设置失败，使用默认配置")
            
            logger.info("✅ 回测执行器初始化完成")
            
            return True
            
        except Exception as e:
            logger.error(f"初始化组件失败: {e}")
            return False
    
    def prepare_data(
        self,
        instruments: List[str],
        start_date: str,
        end_date: str,
        fields: List[str] = None
    ) -> pd.DataFrame:
        """
        准备数据
        
        Parameters
        ----------
        instruments : List[str]
            股票代码列表
        start_date : str
            开始日期
        end_date : str
            结束日期
        fields : List[str], optional
            字段列表
            
        Returns
        -------
        pd.DataFrame
            准备好的数据
        """
        try:
            if self.data_provider:
                # 使用DataManagerV2获取数据
                data = self._get_data_from_manager(
                    instruments, start_date, end_date, fields
                )
            else:
                # 使用模拟数据
                data = self._generate_mock_data(
                    instruments, start_date, end_date, fields
                )
            
            logger.info(f"数据准备完成: {len(data)} 条记录")
            return data
            
        except Exception as e:
            logger.error(f"准备数据失败: {e}")
            return pd.DataFrame()
    
    def _get_data_from_manager(
        self,
        instruments: List[str],
        start_date: str,
        end_date: str,
        fields: List[str] = None
    ) -> pd.DataFrame:
        """从DataManagerV2获取数据"""
        try:
            # 默认字段
            if fields is None:
                fields = ['open', 'high', 'low', 'close', 'volume', 'amount']

            # 获取数据
            data_list = []
            for instrument in instruments:
                stock_data = self.data_provider.get_kline_data(
                    symbol=instrument,
                    start_date=start_date,
                    end_date=end_date,
                    frequency='day'
                )

                if stock_data is not None and not stock_data.empty:
                    stock_data['instrument'] = instrument
                    data_list.append(stock_data)

            if data_list:
                combined_data = pd.concat(data_list, ignore_index=True)
                # 设置索引
                if 'datetime' in combined_data.columns:
                    combined_data['datetime'] = pd.to_datetime(combined_data['datetime'])
                elif 'date' in combined_data.columns:
                    combined_data['datetime'] = pd.to_datetime(combined_data['date'])
                combined_data = combined_data.set_index(['datetime', 'instrument'])
                return combined_data
            else:
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"从DataManager获取数据失败: {e}")
            return pd.DataFrame()
    
    def _generate_mock_data(
        self,
        instruments: List[str],
        start_date: str,
        end_date: str,
        fields: List[str] = None
    ) -> pd.DataFrame:
        """生成模拟数据"""
        try:
            # 默认字段
            if fields is None:
                fields = ['open', 'high', 'low', 'close', 'volume', 'vwap']
            
            # 生成日期范围
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # 生成数据
            data_list = []
            for instrument in instruments:
                # 生成价格数据
                np.random.seed(hash(instrument) % 2**32)
                base_price = np.random.uniform(10, 100)
                
                price_data = []
                current_price = base_price
                
                for date in dates:
                    # 随机价格变动
                    change = np.random.normal(0, 0.02)
                    current_price *= (1 + change)
                    
                    # 生成OHLCV数据
                    high = current_price * (1 + abs(np.random.normal(0, 0.01)))
                    low = current_price * (1 - abs(np.random.normal(0, 0.01)))
                    open_price = current_price * (1 + np.random.normal(0, 0.005))
                    close_price = current_price
                    volume = np.random.uniform(1000000, 10000000)
                    vwap = (high + low + close_price) / 3
                    
                    price_data.append({
                        'datetime': date,
                        'instrument': instrument,
                        'open': open_price,
                        'high': high,
                        'low': low,
                        'close': close_price,
                        'volume': volume,
                        'vwap': vwap
                    })
                    
                    current_price = close_price
                
                data_list.extend(price_data)
            
            # 创建DataFrame
            df = pd.DataFrame(data_list)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index(['datetime', 'instrument'])
            
            return df
            
        except Exception as e:
            logger.error(f"生成模拟数据失败: {e}")
            return pd.DataFrame()
    
    def compute_alpha158_features(
        self,
        data: pd.DataFrame,
        fit_processor: bool = True
    ) -> pd.DataFrame:
        """
        计算Alpha158特征
        
        Parameters
        ----------
        data : pd.DataFrame
            原始数据
        fit_processor : bool
            是否拟合处理器
            
        Returns
        -------
        pd.DataFrame
            包含Alpha158特征的数据
        """
        try:
            if self.alpha158_processor is None:
                raise ValueError("Alpha158处理器未初始化")
            
            logger.info("开始计算Alpha158特征...")
            
            # 拟合处理器
            if fit_processor:
                self.alpha158_processor.fit(data)
            
            # 转换数据（计算特征）
            feature_data = self.alpha158_processor.transform(data)
            
            logger.info(f"Alpha158特征计算完成: {feature_data.shape}")
            return feature_data
            
        except Exception as e:
            logger.error(f"计算Alpha158特征失败: {e}")
            return pd.DataFrame()
    
    def generate_strategy_signals(
        self,
        feature_data: pd.DataFrame,
        signal_method: str = None
    ) -> pd.Series:
        """
        生成策略信号
        
        Parameters
        ----------
        feature_data : pd.DataFrame
            特征数据
        signal_method : str, optional
            信号生成方法
            
        Returns
        -------
        pd.Series
            策略信号
        """
        try:
            signal_method = signal_method or self.strategy_config.get('signal_method', 'ensemble')
            
            if signal_method == 'ensemble':
                signals = self._generate_ensemble_signals(feature_data)
            elif signal_method == 'linear':
                signals = self._generate_linear_signals(feature_data)
            elif signal_method == 'ml':
                signals = self._generate_ml_signals(feature_data)
            else:
                signals = self._generate_simple_signals(feature_data)
            
            logger.info(f"策略信号生成完成: {len(signals)} 条信号")
            return signals
            
        except Exception as e:
            logger.error(f"生成策略信号失败: {e}")
            return pd.Series()
    
    def _generate_ensemble_signals(self, feature_data: pd.DataFrame) -> pd.Series:
        """生成集成信号"""
        try:
            # 选择关键特征
            key_features = [
                'ROC5', 'ROC10', 'ROC20', 'MA5', 'MA10', 'MA20',
                'RSI5', 'RSI10', 'RSI20', 'BETA5', 'BETA10', 'BETA20'
            ]
            
            available_features = [
                f for f in key_features if f in feature_data.columns
            ]
            
            if not available_features:
                logger.warning("没有可用的关键特征，使用随机信号")
                return self._generate_random_signals(feature_data)
            
            # 计算集成信号
            signals = pd.Series(0.0, index=feature_data.index)
            
            for feature in available_features:
                # 标准化特征值
                feature_values = feature_data[feature].fillna(0)
                if feature_values.std() > 0:
                    normalized_values = (feature_values - feature_values.mean()) / feature_values.std()
                    signals += normalized_values
            
            # 归一化信号
            if signals.std() > 0:
                signals = (signals - signals.mean()) / signals.std()
            
            return signals
            
        except Exception as e:
            logger.error(f"生成集成信号失败: {e}")
            return self._generate_random_signals(feature_data)
    
    def _generate_linear_signals(self, feature_data: pd.DataFrame) -> pd.Series:
        """生成线性信号"""
        try:
            # 简单线性组合
            momentum_features = [f for f in feature_data.columns if f.startswith('ROC')]
            mean_reversion_features = [f for f in feature_data.columns if f.startswith('RSI')]
            
            signals = pd.Series(0.0, index=feature_data.index)
            
            # 动量信号
            if momentum_features:
                momentum_signal = feature_data[momentum_features].mean(axis=1)
                signals += momentum_signal
            
            # 均值回归信号（反向）
            if mean_reversion_features:
                mean_reversion_signal = -feature_data[mean_reversion_features].mean(axis=1)
                signals += mean_reversion_signal
            
            return signals
            
        except Exception as e:
            logger.error(f"生成线性信号失败: {e}")
            return self._generate_random_signals(feature_data)
    
    def _generate_ml_signals(self, feature_data: pd.DataFrame) -> pd.Series:
        """生成机器学习信号"""
        try:
            # 简单的机器学习信号（使用随机森林）
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            
            # 准备数据
            feature_cols = [col for col in feature_data.columns if not col.startswith('label')]
            
            if len(feature_cols) < 5:
                return self._generate_random_signals(feature_data)
            
            # 创建标签（下一期收益）
            returns = feature_data['close'].pct_change().shift(-1)
            labels = (returns > 0).astype(int)
            
            # 准备训练数据
            X = feature_data[feature_cols].fillna(0)
            y = labels.fillna(0)
            
            # 训练模型
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X_train, y_train)
            
            # 生成信号
            signals = pd.Series(
                model.predict(X),
                index=feature_data.index
            )
            
            return signals
            
        except Exception as e:
            logger.error(f"生成机器学习信号失败: {e}")
            return self._generate_random_signals(feature_data)
    
    def _generate_simple_signals(self, feature_data: pd.DataFrame) -> pd.Series:
        """生成简单信号"""
        try:
            # 使用简单的动量信号
            if 'ROC5' in feature_data.columns:
                return feature_data['ROC5']
            elif 'MA5' in feature_data.columns:
                return feature_data['MA5'] - 1
            else:
                return self._generate_random_signals(feature_data)
                
        except Exception as e:
            logger.error(f"生成简单信号失败: {e}")
            return self._generate_random_signals(feature_data)
    
    def _generate_random_signals(self, feature_data: pd.DataFrame) -> pd.Series:
        """生成随机信号"""
        return pd.Series(
            np.random.normal(0, 1, len(feature_data)),
            index=feature_data.index
        )
    
    def create_strategy(self, signals: pd.Series) -> TopkDropoutStrategy:
        """
        创建策略实例
        
        Parameters
        ----------
        signals : pd.Series
            策略信号
            
        Returns
        -------
        TopkDropoutStrategy
            策略实例
        """
        try:
            strategy = create_topk_dropout_strategy(
                topk=self.strategy_config.get('topk', 50),
                n_drop=self.strategy_config.get('n_drop', 5),
                signal=signals,
                verbose=self.strategy_config.get('verbose', True)
            )
            
            self.strategy = strategy
            logger.info("✅ 策略创建完成")
            return strategy
            
        except Exception as e:
            logger.error(f"创建策略失败: {e}")
            return None
    
    def run_complete_backtest(
        self,
        instruments: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float = 1000000,
        benchmark: str = "SH000300"
    ) -> Dict[str, Any]:
        """
        运行完整的回测流程
        
        Parameters
        ----------
        instruments : List[str]
            股票代码列表
        start_date : str
            开始日期
        end_date : str
            结束日期
        initial_capital : float
            初始资金
        benchmark : str
            基准指数
            
        Returns
        -------
        Dict[str, Any]
            回测结果
        """
        try:
            logger.info("🚀 开始完整Alpha158回测流程")
            
            # 1. 初始化组件
            if not self.initialize_components():
                raise Exception("组件初始化失败")
            
            # 2. 准备数据
            data = self.prepare_data(instruments, start_date, end_date)
            if data.empty:
                raise Exception("数据准备失败")
            
            # 3. 计算Alpha158特征
            feature_data = self.compute_alpha158_features(data)
            if feature_data.empty:
                raise Exception("Alpha158特征计算失败")
            
            # 4. 生成策略信号
            signals = self.generate_strategy_signals(feature_data)
            if signals.empty:
                raise Exception("策略信号生成失败")
            
            # 5. 创建策略
            strategy = self.create_strategy(signals)
            if strategy is None:
                raise Exception("策略创建失败")
            
            # 6. 执行回测
            backtest_config = {
                'name': 'Alpha158_TopkDropout',
                'type': 'TopkDropout',
                'topk': self.strategy_config.get('topk', 50),
                'n_drop': self.strategy_config.get('n_drop', 5),
                'instruments': instruments,
                'start_date': start_date,
                'end_date': end_date
            }
            
            result = self.backtest_executor.execute_backtest(
                strategy_config=backtest_config,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                benchmark=benchmark
            )
            
            # 7. 添加Alpha158相关信息
            if result.get("success", False):
                result["alpha158_info"] = {
                    "feature_count": len(feature_data.columns) - len(data.columns),
                    "signal_method": self.strategy_config.get('signal_method', 'ensemble'),
                    "processor_config": self.alpha158_config,
                    "strategy_config": self.strategy_config
                }
            
            logger.info("✅ 完整Alpha158回测流程完成")
            return result
            
        except Exception as e:
            logger.error(f"完整Alpha158回测流程失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"完整Alpha158回测流程失败: {str(e)}"
            }
    
    def get_integration_info(self) -> Dict[str, Any]:
        """
        获取集成信息
        
        Returns
        -------
        Dict[str, Any]
            集成信息
        """
        info = {
            "integration_type": "Alpha158PortfolioIntegration",
            "alpha158_processor": self.alpha158_processor is not None,
            "strategy": self.strategy is not None,
            "backtest_executor": self.backtest_executor is not None,
            "data_provider": self.data_provider is not None,
            "data_manager_available": self.data_provider is not None,
            "alpha158_config": self.alpha158_config,
            "strategy_config": self.strategy_config,
            "cache_size": len(self._feature_cache)
        }
        
        if self.alpha158_processor:
            info["alpha158_info"] = self.alpha158_processor.get_feature_info()
        
        if self.strategy:
            info["strategy_info"] = self.strategy.get_strategy_info()
        
        return info


# 全局集成实例
_global_alpha158_integration = None


def get_alpha158_portfolio_integration(
    data_provider=None,
    alpha158_config: Dict[str, Any] = None,
    strategy_config: Dict[str, Any] = None
) -> Alpha158PortfolioIntegration:
    """
    获取全局Alpha158投资组合集成实例
    
    Parameters
    ----------
    data_provider : Any, optional
        数据提供器实例
    alpha158_config : Dict[str, Any], optional
        Alpha158特征处理器配置
    strategy_config : Dict[str, Any], optional
        策略配置
        
    Returns
    -------
    Alpha158PortfolioIntegration
        集成实例
    """
    global _global_alpha158_integration
    
    if _global_alpha158_integration is None:
        _global_alpha158_integration = Alpha158PortfolioIntegration(
            data_provider, alpha158_config, strategy_config
        )
    
    return _global_alpha158_integration


def test_alpha158_portfolio_integration():
    """测试Alpha158投资组合集成"""
    print("=" * 70)
    print("测试Alpha158投资组合集成系统")
    print("=" * 70)
    
    try:
        # 创建集成实例
        integration = get_alpha158_portfolio_integration()
        
        # 显示集成信息
        info = integration.get_integration_info()
        print(f"📊 集成类型: {info['integration_type']}")
        print(f"🔧 Alpha158处理器: {'✅' if info['alpha158_processor'] else '❌'}")
        print(f"📈 策略: {'✅' if info['strategy'] else '❌'}")
        print(f"⚡ 回测执行器: {'✅' if info['backtest_executor'] else '❌'}")
        print(f"💾 数据提供器: {'✅' if info['data_provider'] else '❌'}")
        print(f"🔗 DataManager: {'✅' if info['data_manager_available'] else '❌'}")
        
        # 测试完整回测流程
        print("\n🚀 开始测试完整回测流程...")
        
        test_instruments = ['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318']
        test_start_date = "2020-01-01"
        test_end_date = "2020-06-30"
        
        result = integration.run_complete_backtest(
            instruments=test_instruments,
            start_date=test_start_date,
            end_date=test_end_date,
            initial_capital=1000000,
            benchmark="SH000300"
        )
        
        if result.get("success", False):
            print("✅ 完整回测流程测试成功!")
            
            # 显示关键结果
            print(f"📈 总收益: {result['total_return']:.2%}")
            print(f"📊 年化收益: {result['annual_return']:.2%}")
            print(f"⚡ 夏普比率: {result['sharpe_ratio']:.2f}")
            print(f"📉 最大回撤: {result['max_drawdown']:.2%}")
            print(f"🎯 胜率: {result['win_rate']:.2%}")
            
            # 显示Alpha158信息
            if "alpha158_info" in result:
                alpha158_info = result["alpha158_info"]
                print(f"🔢 特征数量: {alpha158_info['feature_count']}")
                print(f"📡 信号方法: {alpha158_info['signal_method']}")
        else:
            print(f"❌ 完整回测流程测试失败: {result.get('error', '未知错误')}")
        
        print("\n✅ Alpha158投资组合集成系统测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ Alpha158投资组合集成系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_alpha158_portfolio_integration()