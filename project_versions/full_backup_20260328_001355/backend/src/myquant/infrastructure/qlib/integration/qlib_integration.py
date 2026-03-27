"""
QLib接口集成模块

该模块提供了与QLib官方功能的完整集成接口，
确保我们的系统与QLib标准完全兼容。
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(
    0, 
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
)

# 尝试导入QLib
try:
    import qlib
    from qlib.data import D
    from qlib.backtest import backtest, executor
    from qlib.contrib.strategy import TopkDropoutStrategy as QlibTopkDropoutStrategy
    from qlib.contrib.evaluate import risk_analysis
    from qlib.utils import flatten_dict
    QLIB_AVAILABLE = True
except ImportError:
    QLIB_AVAILABLE = False
    logging.warning("QLib不可用，将使用模拟数据")

# 导入我们的模块
from qlib_core.backtest.portfolio_management.strategy.base_strategy import BaseStrategy
from qlib_core.backtest.portfolio_management.strategy.topk_dropout_strategy import TopkDropoutStrategy
from qlib_core.backtest.portfolio_management.strategy.enhanced_indexing_strategy import EnhancedIndexingStrategy
from qlib_core.backtest.enhanced_backtest_executor import EnhancedBacktestExecutor
from qlib_core.analysis.enhanced_performance_analyzer import (
    EnhancedPerformanceAnalyzer, get_enhanced_performance_analyzer
)

logger = logging.getLogger(__name__)


class QlibIntegration:
    """QLib集成类"""
    
    def __init__(self, provider_uri: str = None, region: str = "cn"):
        """
        初始化QLib集成
        
        Parameters
        ----------
        provider_uri : str
            数据提供者URI
        region : str
            区域设置
        """
        self.provider_uri = provider_uri
        self.region = region
        self.qlib_initialized = False
        
        # 初始化我们的组件
        self.backtest_executor = EnhancedBacktestExecutor()
        self.performance_analyzer = get_enhanced_performance_analyzer()
        
        # 初始化QLib
        self._initialize_qlib()
        
        logger.info("QLib集成系统初始化完成")
    
    def _initialize_qlib(self):
        """初始化QLib"""
        if not QLIB_AVAILABLE:
            logger.warning("QLib不可用，跳过初始化")
            return
        
        try:
            if self.provider_uri:
                qlib.init(provider_uri=self.provider_uri, region=self.region)
            else:
                qlib.init(region=self.region)
            
            self.qlib_initialized = True
            logger.info("QLib初始化成功")
            
        except Exception as e:
            logger.error(f"QLib初始化失败: {e}")
            self.qlib_initialized = False
    
    def run_qlib_compatible_backtest(
        self,
        strategy: BaseStrategy,
        start_time: str,
        end_time: str,
        account: float = 100000000,
        benchmark: str = "SH000300",
        exchange_kwargs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        运行QLib兼容的回测
        
        Parameters
        ----------
        strategy : BaseStrategy
            投资组合策略
        start_time : str
            开始时间
        end_time : str
            结束时间
        account : float
            初始资金
        benchmark : str
            基准指数
        exchange_kwargs : Dict[str, Any]
            交易所配置
            
        Returns
        -------
        Dict[str, Any]
            回测结果
        """
        try:
            logger.info(f"🚀 开始QLib兼容回测: {strategy.__class__.__name__}")
            
            # 默认交易所配置
            if exchange_kwargs is None:
                exchange_kwargs = {
                    "limit_threshold": 0.095,
                    "deal_price": "close",
                    "open_cost": 0.0005,
                    "close_cost": 0.0015,
                    "min_cost": 5
                }
            
            # 如果QLib可用且策略是QLib兼容的，使用QLib回测
            if (self.qlib_initialized and 
                isinstance(strategy, TopkDropoutStrategy)):
                return self._run_qlib_native_backtest(
                    strategy, start_time, end_time, account, benchmark, exchange_kwargs
                )
            else:
                # 使用我们的增强回测执行器
                return self._run_enhanced_backtest(
                    strategy, start_time, end_time, account, benchmark, exchange_kwargs
                )
                
        except Exception as e:
            logger.error(f"❌ QLib兼容回测失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"QLib兼容回测失败: {str(e)}"
            }
    
    def _run_qlib_native_backtest(
        self,
        strategy: TopkDropoutStrategy,
        start_time: str,
        end_time: str,
        account: float,
        benchmark: str,
        exchange_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行QLib原生回测"""
        try:
            # 创建QLib兼容的策略
            qlib_strategy = self._convert_to_qlib_strategy(strategy)
            
            # 创建执行器
            executor_obj = executor.SimulatorExecutor(time_per_step="day")
            
            # 限制并行工作进程数量以避免资源耗尽
            import os
            original_workers = os.environ.get('NUMBA_NUM_THREADS', None)
            os.environ['NUMBA_NUM_THREADS'] = '2'  # 限制为2个工作进程
            
            try:
                # 运行回测
                portfolio_metric_dict, indicator_dict = backtest(
                    executor=executor_obj,
                    strategy=qlib_strategy,
                    start_time=start_time,
                    end_time=end_time,
                    account=account,
                    benchmark=benchmark,
                    exchange_kwargs=exchange_kwargs
                )
            finally:
                # 恢复原始设置
                if original_workers is not None:
                    os.environ['NUMBA_NUM_THREADS'] = original_workers
                else:
                    os.environ.pop('NUMBA_NUM_THREADS', None)
            
            # 转换结果格式
            return self._convert_qlib_result(
                portfolio_metric_dict, indicator_dict, strategy
            )
            
        except Exception as e:
            logger.error(f"QLib原生回测失败: {e}")
            raise
    
    def _run_enhanced_backtest(
        self,
        strategy: BaseStrategy,
        start_time: str,
        end_time: str,
        account: float,
        benchmark: str,
        exchange_kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """运行增强回测"""
        # 创建数据配置
        data_config = {
            "start_date": start_time,
            "end_date": end_time,
            "benchmark": benchmark
        }
        
        # 创建回测配置
        backtest_config = {
            "initial_capital": account,
            "benchmark": benchmark,
            "exchange_kwargs": exchange_kwargs
        }
        
        # 使用我们的增强回测执行器
        return self.backtest_executor.run_backtest(
            strategy, data_config, backtest_config
        )
    
    def _convert_to_qlib_strategy(
        self, strategy: TopkDropoutStrategy
    ) -> QlibTopkDropoutStrategy:
        """转换为QLib策略"""
        # 获取策略参数
        strategy_config = strategy.get_strategy_info()
        
        # 获取预测信号
        signal = strategy.signal
        
        # 创建QLib策略
        qlib_strategy = QlibTopkDropoutStrategy(
            topk=strategy_config.get("topk", 50),
            n_drop=strategy_config.get("n_drop", 5),
            signal=signal
        )
        
        return qlib_strategy
    
    def _convert_qlib_result(
        self,
        portfolio_metric_dict: Dict[str, Any],
        indicator_dict: Dict[str, Any],
        strategy: BaseStrategy
    ) -> Dict[str, Any]:
        """转换QLib结果格式"""
        try:
            # 提取关键指标
            analysis_freq = "day"
            
            if analysis_freq in portfolio_metric_dict:
                report_normal, positions_normal = portfolio_metric_dict[analysis_freq]
            else:
                # 如果没有日度数据，使用第一个可用频率
                available_freqs = list(portfolio_metric_dict.keys())
                if available_freqs:
                    freq = available_freqs[0]
                    report_normal, positions_normal = portfolio_metric_dict[freq]
                else:
                    raise ValueError("无法从QLib结果中提取数据")
            
            # 转换为我们的格式
            result = {
                "success": True,
                "strategy_name": strategy.__class__.__name__,
                "start_date": indicator_dict.get("start_time", ""),
                "end_date": indicator_dict.get("end_time", ""),
                "initial_capital": indicator_dict.get("account", 0),
                "final_capital": indicator_dict.get("final_account", 0),
                "result": {
                    "returns": report_normal.get("return", []).tolist(),
                    "dates": report_normal.index.strftime('%Y-%m-%d').tolist(),
                    "nav_curve": (1 + report_normal["return"]).cumprod().tolist(),
                    "positions": self._convert_positions(positions_normal),
                    "benchmark": indicator_dict.get("benchmark", ""),
                    "qlib_indicator": indicator_dict
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"QLib结果转换失败: {e}")
            raise
    
    def _convert_positions(self, positions_normal: Any) -> List[Dict[str, Any]]:
        """转换持仓数据"""
        try:
            if hasattr(positions_normal, 'to_dict'):
                # 如果是DataFrame，转换为字典列表
                return positions_normal.to_dict('records')
            elif isinstance(positions_normal, dict):
                # 如果是字典，转换为列表
                return [positions_normal]
            else:
                # 其他类型，返回空列表
                return []
        except Exception:
            return []
    
    def run_qlib_risk_analysis(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series = None,
        freq: str = "day"
    ) -> Dict[str, Any]:
        """
        运行QLib风险分析
        
        Parameters
        ----------
        returns : pd.Series
            收益率序列
        benchmark_returns : pd.Series, optional
            基准收益率序列
        freq : str
            频率
            
        Returns
        -------
        Dict[str, Any]
            风险分析结果
        """
        try:
            if not self.qlib_initialized:
                logger.warning("QLib未初始化，使用内置风险分析")
                return self._run_builtin_risk_analysis(returns, benchmark_returns)
            
            # 使用QLib风险分析
            if benchmark_returns is not None:
                excess_returns = returns - benchmark_returns
                analysis = risk_analysis(excess_returns, freq=freq)
            else:
                analysis = risk_analysis(returns, freq=freq)
            
            # 转换结果格式
            return {
                "risk_analysis": analysis,
                "flattened_analysis": flatten_dict(analysis),
                "freq": freq,
                "using_qlib": True
            }
            
        except Exception as e:
            logger.error(f"QLib风险分析失败: {e}")
            return self._run_builtin_risk_analysis(returns, benchmark_returns)
    
    def _run_builtin_risk_analysis(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series = None
    ) -> Dict[str, Any]:
        """运行内置风险分析"""
        try:
            # 使用我们的绩效分析器
            metrics = self.performance_analyzer.metrics_calculator.calculate_enhanced_metrics(
                returns, benchmark_returns
            )
            
            return {
                "risk_analysis": metrics,
                "using_qlib": False
            }
            
        except Exception as e:
            logger.error(f"内置风险分析失败: {e}")
            return {
                "error": str(e),
                "using_qlib": False
            }
    
    def get_qlib_data(
        self,
        instruments: List[str],
        fields: List[str],
        start_time: str = None,
        end_time: str = None,
        freq: str = "day"
    ) -> pd.DataFrame:
        """
        获取QLib数据
        
        Parameters
        ----------
        instruments : List[str]
            股票代码列表
        fields : List[str]
            字段列表
        start_time : str, optional
            开始时间
        end_time : str, optional
            结束时间
        freq : str
            频率
            
        Returns
        -------
        pd.DataFrame
            数据
        """
        try:
            if not self.qlib_initialized:
                logger.warning("QLib未初始化，生成模拟数据")
                return self._generate_mock_data(instruments, fields, start_time, end_time)
            
            # 使用QLib获取数据
            data = D.features(
                instruments=instruments,
                fields=fields,
                start_time=start_time,
                end_time=end_time,
                freq=freq
            )
            
            return data
            
        except Exception as e:
            logger.error(f"QLib数据获取失败: {e}")
            return self._generate_mock_data(instruments, fields, start_time, end_time)
    
    def _generate_mock_data(
        self,
        instruments: List[str],
        fields: List[str],
        start_time: str = None,
        end_time: str = None
    ) -> pd.DataFrame:
        """生成模拟数据"""
        try:
            # 设置默认时间范围
            if start_time is None:
                start_time = "2020-01-01"
            if end_time is None:
                end_time = "2020-12-31"
            
            # 创建时间索引
            date_range = pd.date_range(start_time, end_time, freq='D')
            
            # 生成模拟数据
            data_dict = {}
            for field in fields:
                if field in ['$close', '$open', '$high', '$low']:
                    # 价格数据，生成随机价格序列
                    base_price = 100.0
                    prices = [base_price]
                    for _ in range(1, len(date_range)):
                        change = np.random.normal(0, 0.02)
                        new_price = prices[-1] * (1 + change)
                        prices.append(max(new_price, 1.0))
                    
                    data_dict[field] = prices
                elif field in ['$volume']:
                    # 成交量数据
                    data_dict[field] = np.random.randint(1000000, 10000000, len(date_range))
                elif field in ['$vwap']:
                    # VWAP数据
                    data_dict[field] = data_dict.get('$close', [100] * len(date_range))
                else:
                    # 其他数据
                    data_dict[field] = np.random.normal(0, 1, len(date_range))
            
            # 创建多索引DataFrame
            multi_index = pd.MultiIndex.from_product(
                [instruments, date_range],
                names=['instrument', 'datetime']
            )
            
            # 创建DataFrame
            df_data = []
            for instrument in instruments:
                for i, date in enumerate(date_range):
                    row = {}
                    for field in fields:
                        row[field] = data_dict[field][i] if i < len(data_dict[field]) else 0
                    df_data.append(row)
            
            result = pd.DataFrame(df_data, index=multi_index)
            
            return result
            
        except Exception as e:
            logger.error(f"模拟数据生成失败: {e}")
            return pd.DataFrame()
    
    def run_comprehensive_analysis(
        self,
        strategy: BaseStrategy,
        start_time: str,
        end_time: str,
        benchmark: str = "SH000300",
        use_qlib_native: bool = True
    ) -> Dict[str, Any]:
        """
        运行综合分析
        
        Parameters
        ----------
        strategy : BaseStrategy
            投资组合策略
        start_time : str
            开始时间
        end_time : str
            结束时间
        benchmark : str
            基准指数
        use_qlib_native : bool
            是否使用QLib原生功能
            
        Returns
        -------
        Dict[str, Any]
            综合分析结果
        """
        try:
            logger.info(f"🚀 开始综合分析: {strategy.__class__.__name__}")
            
            # 1. 运行回测
            backtest_result = self.run_qlib_compatible_backtest(
                strategy, start_time, end_time, 100000000, benchmark
            )
            
            if not backtest_result.get("success", False):
                raise ValueError(f"回测失败: {backtest_result.get('error', '未知错误')}")
            
            # 2. 获取基准数据
            benchmark_data = None
            if use_qlib_native and self.qlib_initialized:
                try:
                    benchmark_data = self.get_qlib_data(
                        [benchmark], ['$close'], start_time, end_time
                    )
                    if not benchmark_data.empty:
                        benchmark_returns = benchmark_data.xs(benchmark, level='instrument')['$close'].pct_change()
                        benchmark_data = benchmark_returns.dropna()
                except Exception as e:
                    logger.warning(f"基准数据获取失败: {e}")
            
            # 3. 执行绩效分析
            analysis_result = self.performance_analyzer.analyze_strategy_performance(
                strategy, backtest_result, benchmark_data
            )
            
            # 4. 执行QLib风险分析
            if backtest_result.get("result", {}).get("returns"):
                returns = pd.Series(backtest_result["result"]["returns"])
                risk_analysis_result = self.run_qlib_risk_analysis(
                    returns, benchmark_data
                )
            else:
                risk_analysis_result = {"error": "无收益数据"}
            
            # 5. 生成综合报告
            comprehensive_result = {
                "strategy_info": {
                    "name": strategy.__class__.__name__,
                    "type": strategy.__class__.__bases__[0].__name__
                },
                "backtest_result": backtest_result,
                "analysis_result": analysis_result,
                "risk_analysis": risk_analysis_result,
                "qlib_integration": {
                    "qlib_available": QLIB_AVAILABLE,
                    "qlib_initialized": self.qlib_initialized,
                    "use_qlib_native": use_qlib_native
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("✅ 综合分析完成")
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"❌ 综合分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"综合分析失败: {str(e)}"
            }
    
    def export_qlib_compatible_report(
        self,
        result: Dict[str, Any],
        export_format: str = "json",
        output_dir: str = None
    ) -> str:
        """
        导出QLib兼容报告
        
        Parameters
        ----------
        result : Dict[str, Any]
            分析结果
        export_format : str
            导出格式
        output_dir : str
            输出目录
            
        Returns
        -------
        str
            导出文件路径
        """
        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "qlib_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        strategy_name = result.get("strategy_info", {}).get("name", "unknown")
        filename = f"qlib_report_{strategy_name}_{timestamp}.{export_format}"
        filepath = os.path.join(output_dir, filename)
        
        try:
            if export_format == "json":
                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(
                        result,
                        f,
                        ensure_ascii=False,
                        indent=2,
                        default=str
                    )
            
            elif export_format == "html":
                html_content = self._generate_qlib_html_report(result)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            logger.info(f"✅ QLib兼容报告已导出: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ 导出QLib兼容报告失败: {e}")
            raise
    
    def _generate_qlib_html_report(self, result: Dict[str, Any]) -> str:
        """生成QLib兼容HTML报告"""
        strategy_info = result.get("strategy_info", {})
        qlib_integration = result.get("qlib_integration", {})
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>QLib兼容分析报告 - {strategy_info.get('name', '未知')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric-card {{ background: white; border: 1px solid #ddd; 
                              border-radius: 5px; padding: 15px; margin: 10px 0; }}
                .status-ok {{ color: #27ae60; }}
                .status-warning {{ color: #f39c12; }}
                .status-error {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 QLib兼容分析报告</h1>
                <h2>策略: {strategy_info.get('name', '未知')}</h2>
                <p>策略类型: {strategy_info.get('type', '未知')}</p>
                <p>分析时间: {result.get('timestamp', '未知')}</p>
            </div>
            
            <div class="section">
                <h3>🔧 QLib集成状态</h3>
                <div class="metric-card">
                    <p><strong>QLib可用:</strong> 
                       <span class="{'status-ok' if qlib_integration.get('qlib_available') else 'status-error'}">
                           {'是' if qlib_integration.get('qlib_available') else '否'}
                       </span>
                    </p>
                    <p><strong>QLib初始化:</strong> 
                       <span class="{'status-ok' if qlib_integration.get('qlib_initialized') else 'status-warning'}">
                           {'成功' if qlib_integration.get('qlib_initialized') else '失败'}
                       </span>
                    </p>
                    <p><strong>使用QLib原生:</strong> 
                       <span class="{'status-ok' if qlib_integration.get('use_qlib_native') else 'status-warning'}">
                           {'是' if qlib_integration.get('use_qlib_native') else '否'}
                       </span>
                    </p>
                </div>
            </div>
            
            <div class="section">
                <p><em>注：此报告由QLib集成系统自动生成</em></p>
            </div>
        </body>
        </html>
        """
        
        return html


# 全局QLib集成实例
_global_qlib_integration = None


def get_qlib_integration(provider_uri: str = None, region: str = "cn") -> QlibIntegration:
    """获取全局QLib集成实例"""
    global _global_qlib_integration
    
    if _global_qlib_integration is None:
        _global_qlib_integration = QlibIntegration(provider_uri, region)
    
    return _global_qlib_integration


def test_qlib_integration():
    """测试QLib集成"""
    print("=" * 70)
    print("测试QLib集成系统")
    print("=" * 70)
    
    try:
        # 创建QLib集成
        qlib_integration = get_qlib_integration()
        
        # 创建测试策略
        strategy = TopkDropoutStrategy(
            topk=30,
            n_drop=5,
            signal=pd.Series(np.random.randn(10), 
                         index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318', 
                                'SH600519', 'SZ000858', 'SH600887', 'SZ002415'])
        )
        
        print("🚀 开始QLib兼容综合分析...")
        
        # 运行综合分析
        result = qlib_integration.run_comprehensive_analysis(
            strategy,
            "2020-01-01",
            "2020-12-31",
            "SH000300",
            use_qlib_native=True
        )
        
        if result.get("success", False):
            print("✅ QLib兼容综合分析完成!")
            
            # 显示QLib集成状态
            qlib_integration_info = result.get("qlib_integration", {})
            print(f"🔧 QLib可用: {'是' if qlib_integration_info.get('qlib_available') else '否'}")
            print(f"🔧 QLib初始化: {'成功' if qlib_integration_info.get('qlib_initialized') else '失败'}")
            print(f"🔧 使用QLib原生: {'是' if qlib_integration_info.get('use_qlib_native') else '否'}")
            
            # 测试导出功能
            export_path = qlib_integration.export_qlib_compatible_report(
                result, "html"
            )
            print(f"💾 QLib兼容报告已导出: {export_path}")
        
        else:
            print(f"❌ QLib兼容综合分析失败: {result.get('error', '未知错误')}")
        
        print("✅ QLib集成系统测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ QLib集成系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_qlib_integration()