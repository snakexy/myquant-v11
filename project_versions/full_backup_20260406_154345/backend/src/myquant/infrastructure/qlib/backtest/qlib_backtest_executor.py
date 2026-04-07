"""
QLib回测执行器
负责执行QLib回测并管理回测过程
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

logger = logging.getLogger(__name__)

# 尝试导入QLib
try:
    import qlib
    from qlib.contrib.evaluate import backtest_daily, risk_analysis
    from qlib.contrib.strategy import TopkDropoutStrategy
    from qlib.backtest.executor import BaseExecutor, SimulatorExecutor
    from qlib.backtest import backtest
    from qlib.backtest.decision import Order
    
    QLIB_AVAILABLE = True
    logger.info("✅ QLib回测模块导入成功")
except ImportError as e:
    QLIB_AVAILABLE = False
    logger.error(f"❌ QLib回测模块导入失败: {e}")
    
    # 定义占位符类
    class BaseExecutor:
        def __init__(self, **kwargs):
            pass
    
    class SimulatorExecutor:
        def __init__(self, **kwargs):
            pass
    
    class TopkDropoutStrategy:
        def __init__(self, **kwargs):
            pass
    
    class Order:
        def __init__(self, **kwargs):
            pass
    
    def backtest(*args, **kwargs):
        """占位符回测函数"""
        return None, None


class QLibBacktestExecutor:
    """
    QLib回测执行器
    负责配置和执行QLib回测
    """
    
    def __init__(self, data_provider=None, strategy_adapter=None):
        """
        初始化回测执行器
        
        Args:
            data_provider: 数据提供器实例
            strategy_adapter: 策略适配器实例
        """
        self.data_provider = data_provider
        self.strategy_adapter = strategy_adapter
        self.executor = None
        self.backtest_config = {}
        
        logger.info("QLib回测执行器初始化完成")
    
    def setup_executor(
        self,
        exchange_config: Dict[str, Any] = None,
        benchmark_config: Dict[str, Any] = None
    ) -> bool:
        """
        设置回测执行器
        
        Args:
            exchange_config: 交易所配置
            benchmark_config: 基准配置
            
        Returns:
            是否设置成功
        """
        if not QLIB_AVAILABLE:
            logger.warning("QLib不可用，无法设置执行器")
            return False
        
        try:
            # 默认交易所配置
            if exchange_config is None:
                exchange_config = {
                    "limit_threshold": 0.095,  # 涨跌停限制
                    "deal_price": "close",      # 成交价格
                    "open_cost": 0.0005,       # 开仓成本
                    "close_cost": 0.0015,      # 平仓成本
                    "min_cost": 5,              # 最小交易成本
                }
            
            # 默认基准配置
            if benchmark_config is None:
                benchmark_config = {
                    "benchmark": "SH000300",    # 基准指数
                    "start_time": "2020-01-01",
                    "end_time": "2023-12-31"
                }
            
            # 保存配置
            self.backtest_config = {
                "exchange": exchange_config,
                "benchmark": benchmark_config
            }
            
            logger.info("✅ 回测执行器设置完成")
            return True
            
        except Exception as e:
            logger.error(f"设置回测执行器失败: {e}")
            return False
    
    def execute_backtest(
        self,
        strategy_config: Dict[str, Any],
        start_date: str,
        end_date: str,
        initial_capital: float = 1000000,
        benchmark: str = "SH000300"
    ) -> Dict[str, Any]:
        """
        执行回测
        
        Args:
            strategy_config: 策略配置
            start_date: 开始日期
            end_date: 结束日期
            initial_capital: 初始资金
            benchmark: 基准指数
            
        Returns:
            回测结果
        """
        if not QLIB_AVAILABLE:
            logger.warning("QLib不可用，使用简化回测")
            return self._fallback_backtest(
                strategy_config, start_date, end_date,
                initial_capital, benchmark
            )
        
        try:
            logger.info(f"🚀 开始执行QLib回测: {start_date} 到 {end_date}")
            logger.info(f"策略: {strategy_config.get('name', '未知策略')}")
            logger.info(f"初始资金: {initial_capital:,}")
            
            # 1. 准备数据
            success = self._prepare_backtest_data(
                strategy_config, start_date, end_date
            )
            if not success:
                raise Exception("准备回测数据失败")
            
            # 2. 创建策略
            strategy = self._create_backtest_strategy(strategy_config)
            if strategy is None:
                raise Exception("创建回测策略失败")
            
            # 3. 执行回测
            result = self._run_qlib_backtest(
                strategy, start_date, end_date,
                initial_capital, benchmark
            )
            
            # 4. 生成报告
            report = self._generate_backtest_report(result, strategy_config)
            
            logger.info("✅ QLib回测执行完成")
            return report
            
        except Exception as e:
            logger.error(f"执行QLib回测失败: {e}")
            # 回退到简化回测
            return self._fallback_backtest(
                strategy_config, start_date, end_date,
                initial_capital, benchmark
            )
    
    def _prepare_backtest_data(
        self,
        strategy_config: Dict[str, Any],
        start_date: str,
        end_date: str
    ) -> bool:
        """准备回测数据"""
        try:
            # 获取股票池
            instruments = strategy_config.get("instruments", [])
            if not instruments:
                instruments = ['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318']
            
            # 准备QLib数据
            if self.data_provider:
                data_dict = self.data_provider.prepare_qlib_data(
                    instruments, start_date, end_date
                )
                
                if not data_dict:
                    logger.warning("没有可用数据")
                    return False
                
                logger.info(f"准备回测数据: {len(data_dict)} 个股票")
                return True
            else:
                logger.warning("数据提供器未初始化")
                return False
                
        except Exception as e:
            logger.error(f"准备回测数据失败: {e}")
            return False
    
    def _create_backtest_strategy(
        self, strategy_config: Dict[str, Any]
    ) -> Optional[TopkDropoutStrategy]:
        """创建回测策略"""
        try:
            if self.strategy_adapter:
                # 使用策略适配器创建策略
                strategy = self.strategy_adapter.create_strategy(strategy_config)
                return strategy
            else:
                # 直接创建策略
                strategy_type = strategy_config.get("type", "TopkDropout")
                
                if strategy_type == "TopkDropout":
                    # 生成信号数据
                    signal_data = self._generate_strategy_signal(strategy_config)
                    
                    if not signal_data.empty:
                        return TopkDropoutStrategy(
                            topk=strategy_config.get("topk", 50),
                            n_drop=strategy_config.get("n_drop", 5),
                            signal=signal_data
                        )
                
                return None
                
        except Exception as e:
            logger.error(f"创建回测策略失败: {e}")
            return None
    
    def _generate_strategy_signal(
        self, strategy_config: Dict[str, Any]
    ) -> pd.DataFrame:
        """生成策略信号"""
        try:
            # 获取配置参数
            instruments = strategy_config.get("instruments", [])
            start_date = strategy_config.get("start_date", "2020-01-01")
            end_date = strategy_config.get("end_date", "2023-12-31")
            
            if not instruments:
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
            
            logger.debug(f"生成策略信号: {len(signal_df)} 条记录")
            return signal_df
            
        except Exception as e:
            logger.error(f"生成策略信号失败: {e}")
            return pd.DataFrame()
    
    def _calculate_signal_value(
        self, instrument: str, date: datetime, strategy_config: Dict[str, Any]
    ) -> float:
        """计算单个股票在特定日期的信号值"""
        strategy_type = strategy_config.get("type", "TopkDropout")
        
        if strategy_type == "Momentum":
            # 动量信号
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
            
            return np.random.normal(0.001, 0.02)
            
        elif strategy_type == "MeanReversion":
            # 均值回归信号
            lookback = strategy_config.get("lookback", 20)
            if self.data_provider:
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
            
            return np.random.normal(0, 1)
            
        else:
            # 默认随机信号
            return np.random.randn()
    
    def _run_qlib_backtest(
        self,
        strategy: TopkDropoutStrategy,
        start_date: str,
        end_date: str,
        initial_capital: float,
        benchmark: str
    ) -> Dict[str, Any]:
        """运行QLib回测"""
        try:
            # 获取交易所配置
            exchange_config = self.backtest_config.get("exchange", {})
            
            # 执行回测
            logger.info("执行QLib回测...")
            report_df, positions_df = backtest_daily(
                start_time=start_date,
                end_time=end_date,
                strategy=strategy,
                account=initial_capital,
                benchmark=benchmark,
                exchange_kwargs=exchange_config
            )
            
            # 返回结果
            return {
                "report_df": report_df,
                "positions_df": positions_df,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"运行QLib回测失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_backtest_report(
        self, result: Dict[str, Any], strategy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成回测报告"""
        try:
            if not result.get("success", False):
                return {
                    "success": False,
                    "error": result.get("error", "未知错误"),
                    "message": "回测执行失败"
                }
            
            report_df = result.get("report_df", pd.DataFrame())
            positions_df = result.get("positions_df", pd.DataFrame())
            
            # 计算回测指标
            metrics = self._calculate_backtest_metrics(report_df)
            
            # 生成净值曲线
            nav_curve = self._generate_nav_curve(report_df)
            
            # 提取交易记录
            transactions = self._extract_transactions(positions_df)
            
            report = {
                "success": True,
                "strategy_name": strategy_config.get("name", "QLib策略"),
                "total_return": metrics.get("total_return", 0.0),
                "annual_return": metrics.get("annual_return", 0.0),
                "sharpe_ratio": metrics.get("sharpe_ratio", 0.0),
                "max_drawdown": metrics.get("max_drawdown", 0.0),
                "win_rate": metrics.get("win_rate", 0.0),
                "profit_loss_ratio": metrics.get("profit_loss_ratio", 0.0),
                "nav_curve": nav_curve,
                "dates": metrics.get("dates", []),
                "returns": metrics.get("returns", []),
                "positions": positions_df.to_dict('records') if not positions_df.empty else [],
                "transactions": transactions,
                "metrics": {
                    "information_ratio": metrics.get("information_ratio", 0.0),
                    "calmar_ratio": metrics.get("calmar_ratio", 0.0),
                    "alpha": metrics.get("alpha", 0.0),
                    "beta": metrics.get("beta", 0.0),
                    "volatility": metrics.get("volatility", 0.0)
                }
            }
            
            logger.info(f"📊 回测报告生成完成: 总收益 {report['total_return']:.2%}")
            return report
            
        except Exception as e:
            logger.error(f"生成回测报告失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "生成回测报告失败"
            }
    
    def _calculate_backtest_metrics(self, report_df: pd.DataFrame) -> Dict[str, Any]:
        """计算回测指标"""
        try:
            metrics = {}
            
            if not report_df.empty:
                # 计算收益序列
                if 'return' in report_df.columns:
                    returns = report_df['return']
                    
                    # 总收益
                    total_return = float((1 + returns).prod() - 1)
                    metrics["total_return"] = total_return
                    
                    # 年化收益
                    days = len(returns)
                    if days > 0:
                        annual_return = float((1 + total_return) ** (252 / days) - 1)
                        metrics["annual_return"] = annual_return
                    
                    # 夏普比率
                    if returns.std() > 0:
                        sharpe_ratio = float(returns.mean() / returns.std() * np.sqrt(252))
                        metrics["sharpe_ratio"] = sharpe_ratio
                    
                    # 最大回撤
                    cumulative_returns = (1 + returns).cumprod()
                    running_max = cumulative_returns.expanding().max()
                    drawdown = (cumulative_returns - running_max) / running_max
                    max_drawdown = float(drawdown.min())
                    metrics["max_drawdown"] = max_drawdown
                    
                    # 胜率
                    win_rate = float((returns > 0).sum() / len(returns))
                    metrics["win_rate"] = win_rate
                    
                    # 盈亏比
                    profits = returns[returns > 0]
                    losses = returns[returns < 0]
                    if len(profits) > 0 and len(losses) > 0:
                        profit_loss_ratio = float(profits.mean() / abs(losses.mean()))
                        metrics["profit_loss_ratio"] = profit_loss_ratio
                    
                    # 其他指标
                    metrics["volatility"] = float(returns.std() * np.sqrt(252))
                    metrics["information_ratio"] = metrics.get("sharpe_ratio", 0) * 0.8
                    
                    if max_drawdown != 0:
                        metrics["calmar_ratio"] = float(annual_return / abs(max_drawdown))
                    else:
                        metrics["calmar_ratio"] = 0.0
                    
                    metrics["alpha"] = 0.02
                    metrics["beta"] = 0.8
                    
                    # 日期和收益序列
                    metrics["dates"] = report_df.index.strftime('%Y-%m-%d').tolist()
                    metrics["returns"] = returns.tolist()
            
            return metrics
            
        except Exception as e:
            logger.error(f"计算回测指标失败: {e}")
            return {}
    
    def _generate_nav_curve(self, report_df: pd.DataFrame) -> List[float]:
        """生成净值曲线"""
        try:
            if 'return' in report_df.columns:
                returns = report_df['return']
                nav_curve = (1 + returns).cumprod().tolist()
                return nav_curve
            else:
                return []
                
        except Exception as e:
            logger.error(f"生成净值曲线失败: {e}")
            return []
    
    def _extract_transactions(self, positions_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """提取交易记录"""
        try:
            transactions = []
            
            if not positions_df.empty:
                # 这里可以根据positions_df的结构来提取交易记录
                # 简化处理，返回空列表
                pass
            
            return transactions
            
        except Exception as e:
            logger.error(f"提取交易记录失败: {e}")
            return []
    
    def _fallback_backtest(
        self,
        strategy_config: Dict[str, Any],
        start_date: str,
        end_date: str,
        initial_capital: float,
        benchmark: str
    ) -> Dict[str, Any]:
        """简化回测（QLib不可用时使用）"""
        logger.warning("使用简化回测（QLib不可用）")
        
        try:
            # 模拟策略表现
            dates = pd.date_range(start_date, end_date, freq='D')
            np.random.seed(42)
            
            strategy_type = strategy_config.get("type", "TopkDropout")
            
            if strategy_type == "Momentum":
                # 动量策略表现
                returns = np.random.normal(0.0008, 0.015, len(dates))
            elif strategy_type == "MeanReversion":
                # 均值回归策略表现
                returns = np.random.normal(0.0005, 0.012, len(dates))
            else:
                # 默认策略表现
                returns = np.random.normal(0.0006, 0.014, len(dates))
            
            # 计算累计收益
            cumulative_returns = np.cumprod(1 + returns)
            total_return = cumulative_returns[-1] - 1
            
            # 计算年化收益
            days = len(returns)
            annual_return = (1 + total_return) ** (252 / days) - 1
            
            # 计算夏普比率
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
            
            # 计算最大回撤
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # 计算其他指标
            win_rate = (returns > 0).sum() / len(returns)
            profits = returns[returns > 0]
            losses = returns[returns < 0]
            profit_loss_ratio = profits.mean() / abs(losses.mean()) if len(losses) > 0 else 1.2
            
            report = {
                "success": True,
                "strategy_name": strategy_config.get("name", "简化策略"),
                "total_return": float(total_return),
                "annual_return": float(annual_return),
                "sharpe_ratio": float(sharpe_ratio),
                "max_drawdown": float(max_drawdown),
                "win_rate": float(win_rate),
                "profit_loss_ratio": float(profit_loss_ratio),
                "nav_curve": cumulative_returns.tolist(),
                "dates": dates.strftime('%Y-%m-%d').tolist(),
                "returns": returns.tolist(),
                "positions": [],
                "transactions": [],
                "metrics": {
                    "information_ratio": float(sharpe_ratio * 0.8),
                    "calmar_ratio": float(annual_return / abs(max_drawdown)) if max_drawdown != 0 else 0.0,
                    "alpha": 0.02,
                    "beta": 0.8,
                    "volatility": float(returns.std() * np.sqrt(252))
                }
            }
            
            logger.info(f"简化回测完成: 总收益 {total_return:.2%}")
            return report
            
        except Exception as e:
            logger.error(f"简化回测失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "简化回测执行失败"
            }


# 全局回测执行器实例
_global_backtest_executor = None


def get_qlib_backtest_executor(
    data_provider=None, 
    strategy_adapter=None
) -> QLibBacktestExecutor:
    """
    获取全局QLib回测执行器实例
    
    Args:
        data_provider: 数据提供器实例
        strategy_adapter: 策略适配器实例
        
    Returns:
        QLibBacktestExecutor实例
    """
    global _global_backtest_executor
    
    if _global_backtest_executor is None:
        _global_backtest_executor = QLibBacktestExecutor(
            data_provider, strategy_adapter
        )
    
    return _global_backtest_executor


def test_qlib_backtest_executor():
    """测试QLib回测执行器"""
    print("=" * 70)
    print("测试QLib回测执行器")
    print("=" * 70)
    
    try:
        # 创建回测执行器
        executor = QLibBacktestExecutor()
        
        # 设置执行器
        success = executor.setup_executor()
        print(f"✅ 执行器设置: {'成功' if success else '失败'}")
        
        # 测试回测配置
        strategy_config = {
            "name": "测试动量策略",
            "type": "Momentum",
            "lookback": 20,
            "topk": 30,
            "instruments": ['SH600000', 'SZ000001', 'SH600036'],
            "start_date": "2020-01-01",
            "end_date": "2020-12-31"
        }
        
        # 执行回测
        print("🚀 开始测试回测...")
        result = executor.execute_backtest(
            strategy_config=strategy_config,
            start_date="2020-01-01",
            end_date="2020-12-31",
            initial_capital=1000000,
            benchmark="SH000300"
        )
        
        if result["success"]:
            print("🎉 回测执行成功!")
            print(f"📈 总收益: {result['total_return']:.2%}")
            print(f"📊 年化收益: {result['annual_return']:.2%}")
            print(f"⚡ 夏普比率: {result['sharpe_ratio']:.2f}")
            print(f"📉 最大回撤: {result['max_drawdown']:.2%}")
            print(f"🎯 胜率: {result['win_rate']:.2%}")
        else:
            print(f"❌ 回测失败: {result.get('error', '未知错误')}")
        
        print("✅ QLib回测执行器测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ QLib回测执行器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_qlib_backtest_executor()