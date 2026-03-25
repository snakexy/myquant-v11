"""
投资组合管理集成模块

该模块提供了完整的投资组合管理、回测和绩效分析集成功能，
将策略、回测执行器和绩效分析器无缝连接。
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

# 导入我们的模块
from qlib_core.backtest.portfolio_management.strategy.base_strategy import BaseStrategy
from qlib_core.backtest.portfolio_management.strategy.topk_dropout_strategy import TopkDropoutStrategy
from qlib_core.backtest.portfolio_management.strategy.enhanced_indexing_strategy import EnhancedIndexingStrategy
from qlib_core.backtest.enhanced_backtest_executor import EnhancedBacktestExecutor
from qlib_core.analysis.enhanced_performance_analyzer import (
    EnhancedPerformanceAnalyzer, get_enhanced_performance_analyzer
)

logger = logging.getLogger(__name__)


class PortfolioIntegration:
    """投资组合管理集成类"""
    
    def __init__(self):
        """初始化投资组合管理集成"""
        self.backtest_executor = EnhancedBacktestExecutor()
        self.performance_analyzer = get_enhanced_performance_analyzer()
        
        # 存储历史记录
        self.strategy_history = {}
        self.backtest_history = {}
        self.analysis_history = {}
        
        logger.info("投资组合管理集成系统初始化完成")
    
    def run_complete_portfolio_analysis(
        self,
        strategy: BaseStrategy,
        data_config: Dict[str, Any],
        backtest_config: Dict[str, Any],
        benchmark_data: pd.Series = None,
        analysis_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        运行完整的投资组合分析流程
        
        Parameters
        ----------
        strategy : BaseStrategy
            投资组合策略
        data_config : Dict[str, Any]
            数据配置
        backtest_config : Dict[str, Any]
            回测配置
        benchmark_data : pd.Series, optional
            基准数据
        analysis_config : Dict[str, Any], optional
            分析配置
            
        Returns
        -------
        Dict[str, Any]
            完整分析结果
        """
        try:
            logger.info(f"🚀 开始完整投资组合分析: {strategy.__class__.__name__}")
            
            # 1. 执行回测
            backtest_result = self.backtest_executor.run_backtest(
                strategy, data_config, backtest_config
            )
            
            if not backtest_result.get("success", False):
                raise ValueError(f"回测失败: {backtest_result.get('error', '未知错误')}")
            
            # 2. 执行绩效分析
            analysis_result = self.performance_analyzer.analyze_strategy_performance(
                strategy, backtest_result, benchmark_data, analysis_config
            )
            
            # 3. 生成集成报告
            integrated_result = self._generate_integrated_report(
                strategy, backtest_result, analysis_result
            )
            
            # 4. 存储历史记录
            self._store_history(strategy, backtest_result, analysis_result)
            
            logger.info("✅ 完整投资组合分析完成")
            return integrated_result
            
        except Exception as e:
            logger.error(f"❌ 完整投资组合分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"完整投资组合分析失败: {str(e)}"
            }
    
    def run_strategy_comparison(
        self,
        strategies: List[BaseStrategy],
        data_config: Dict[str, Any],
        backtest_config: Dict[str, Any],
        benchmark_data: pd.Series = None
    ) -> Dict[str, Any]:
        """
        运行策略比较分析
        
        Parameters
        ----------
        strategies : List[BaseStrategy]
            策略列表
        data_config : Dict[str, Any]
            数据配置
        backtest_config : Dict[str, Any]
            回测配置
        benchmark_data : pd.Series, optional
            基准数据
            
        Returns
        -------
        Dict[str, Any]
            策略比较结果
        """
        try:
            logger.info(f"🚀 开始策略比较分析: {len(strategies)}个策略")
            
            comparison_results = {}
            
            for strategy in strategies:
                strategy_name = strategy.__class__.__name__
                
                # 运行单个策略分析
                result = self.run_complete_portfolio_analysis(
                    strategy, data_config, backtest_config, benchmark_data
                )
                
                if result.get("success", False):
                    comparison_results[strategy_name] = result
                else:
                    comparison_results[strategy_name] = {
                        "success": False,
                        "error": result.get("error", "未知错误")
                    }
            
            # 生成比较报告
            comparison_report = self._generate_comparison_report(comparison_results)
            
            logger.info("✅ 策略比较分析完成")
            return {
                "success": True,
                "comparison_results": comparison_results,
                "comparison_report": comparison_report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 策略比较分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"策略比较分析失败: {str(e)}"
            }
    
    def run_parameter_optimization(
        self,
        strategy_class: type,
        parameter_grid: Dict[str, List[Any]],
        data_config: Dict[str, Any],
        backtest_config: Dict[str, Any],
        benchmark_data: pd.Series = None,
        optimization_metric: str = "sharpe_ratio"
    ) -> Dict[str, Any]:
        """
        运行参数优化
        
        Parameters
        ----------
        strategy_class : type
            策略类
        parameter_grid : Dict[str, List[Any]]
            参数网格
        data_config : Dict[str, Any]
            数据配置
        backtest_config : Dict[str, Any]
            回测配置
        benchmark_data : pd.Series, optional
            基准数据
        optimization_metric : str
            优化指标
            
        Returns
        -------
        Dict[str, Any]
            参数优化结果
        """
        try:
            logger.info(f"🚀 开始参数优化: {strategy_class.__name__}")
            
            optimization_results = []
            
            # 生成参数组合
            parameter_combinations = self._generate_parameter_combinations(
                parameter_grid
            )
            
            logger.info(f"总共需要测试 {len(parameter_combinations)} 个参数组合")
            
            for i, params in enumerate(parameter_combinations):
                logger.info(f"测试参数组合 {i+1}/{len(parameter_combinations)}: {params}")
                
                # 创建策略实例
                strategy = strategy_class(**params)
                
                # 运行分析
                result = self.run_complete_portfolio_analysis(
                    strategy, data_config, backtest_config, benchmark_data
                )
                
                if result.get("success", False):
                    # 提取优化指标值
                    metric_value = self._extract_metric_value(
                        result, optimization_metric
                    )
                    
                    optimization_results.append({
                        "parameters": params,
                        "metric_value": metric_value,
                        "result": result
                    })
                else:
                    logger.warning(f"参数组合 {params} 测试失败")
            
            # 找出最优参数
            best_result = self._find_best_parameters(
                optimization_results, optimization_metric
            )
            
            # 生成优化报告
            optimization_report = self._generate_optimization_report(
                optimization_results, best_result, optimization_metric
            )
            
            logger.info("✅ 参数优化完成")
            return {
                "success": True,
                "best_parameters": best_result["parameters"],
                "best_metric_value": best_result["metric_value"],
                "best_result": best_result["result"],
                "optimization_results": optimization_results,
                "optimization_report": optimization_report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 参数优化失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"参数优化失败: {str(e)}"
            }
    
    def _generate_integrated_report(
        self,
        strategy: BaseStrategy,
        backtest_result: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成集成报告"""
        return {
            "strategy_info": {
                "name": strategy.__class__.__name__,
                "type": strategy.__class__.__bases__[0].__name__
            },
            "backtest_result": backtest_result,
            "analysis_result": analysis_result,
            "summary": {
                "overall_performance": analysis_result.get(
                    "comprehensive_assessment", {}
                ).get("performance_rating", "未知"),
                "key_metrics": self._extract_key_metrics(analysis_result),
                "recommendations": analysis_result.get(
                    "comprehensive_assessment", {}
                ).get("recommendations", [])
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_comparison_report(
        self, comparison_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成比较报告"""
        successful_results = {
            name: result for name, result in comparison_results.items()
            if result.get("success", False)
        }
        
        if not successful_results:
            return {"message": "没有成功的策略结果可供比较"}
        
        # 提取关键指标进行比较
        comparison_table = []
        for strategy_name, result in successful_results.items():
            basic_metrics = result.get("analysis_result", {}).get("basic_metrics", {})
            assessment = result.get("analysis_result", {}).get(
                "comprehensive_assessment", {}
            )
            
            comparison_table.append({
                "strategy": strategy_name,
                "annual_return": basic_metrics.get("annual_return", 0),
                "sharpe_ratio": basic_metrics.get("sharpe_ratio", 0),
                "max_drawdown": basic_metrics.get("max_drawdown", 0),
                "overall_score": assessment.get("overall_score", 0),
                "performance_rating": assessment.get("performance_rating", "未知")
            })
        
        # 排序
        comparison_table.sort(
            key=lambda x: x["overall_score"], reverse=True
        )
        
        return {
            "comparison_table": comparison_table,
            "best_strategy": comparison_table[0]["strategy"] if comparison_table else None,
            "ranking": {
                item["strategy"]: rank + 1
                for rank, item in enumerate(comparison_table)
            }
        }
    
    def _generate_parameter_combinations(
        self, parameter_grid: Dict[str, List[Any]]
    ) -> List[Dict[str, Any]]:
        """生成参数组合"""
        import itertools
        
        keys = list(parameter_grid.keys())
        values = list(parameter_grid.values())
        
        combinations = []
        for combination in itertools.product(*values):
            param_dict = dict(zip(keys, combination))
            combinations.append(param_dict)
        
        return combinations
    
    def _extract_metric_value(
        self, result: Dict[str, Any], metric_name: str
    ) -> float:
        """提取指标值"""
        try:
            basic_metrics = result.get("analysis_result", {}).get("basic_metrics", {})
            return basic_metrics.get(metric_name, 0.0)
        except Exception:
            return 0.0
    
    def _find_best_parameters(
        self,
        optimization_results: List[Dict[str, Any]],
        optimization_metric: str
    ) -> Dict[str, Any]:
        """找出最优参数"""
        if not optimization_results:
            return {}
        
        # 根据指标类型确定排序方向
        if optimization_metric in ["sharpe_ratio", "annual_return", "overall_score"]:
            # 越大越好的指标
            best_result = max(
                optimization_results, 
                key=lambda x: x["metric_value"]
            )
        else:
            # 越小越好的指标（如最大回撤）
            best_result = min(
                optimization_results, 
                key=lambda x: x["metric_value"]
            )
        
        return best_result
    
    def _generate_optimization_report(
        self,
        optimization_results: List[Dict[str, Any]],
        best_result: Dict[str, Any],
        optimization_metric: str
    ) -> Dict[str, Any]:
        """生成优化报告"""
        # 统计信息
        metric_values = [r["metric_value"] for r in optimization_results]
        
        return {
            "optimization_metric": optimization_metric,
            "total_combinations": len(optimization_results),
            "best_parameters": best_result.get("parameters", {}),
            "best_metric_value": best_result.get("metric_value", 0),
            "metric_statistics": {
                "mean": np.mean(metric_values),
                "std": np.std(metric_values),
                "min": np.min(metric_values),
                "max": np.max(metric_values)
            },
            "top_5_results": sorted(
                optimization_results,
                key=lambda x: x["metric_value"],
                reverse=True
            )[:5]
        }
    
    def _extract_key_metrics(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """提取关键指标"""
        basic_metrics = analysis_result.get("basic_metrics", {})
        
        return {
            "annual_return": basic_metrics.get("annual_return", 0),
            "sharpe_ratio": basic_metrics.get("sharpe_ratio", 0),
            "max_drawdown": basic_metrics.get("max_drawdown", 0),
            "win_rate": basic_metrics.get("win_rate", 0),
            "information_ratio": basic_metrics.get("information_ratio", 0)
        }
    
    def _store_history(
        self,
        strategy: BaseStrategy,
        backtest_result: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ):
        """存储历史记录"""
        strategy_name = strategy.__class__.__name__
        timestamp = datetime.now().isoformat()
        
        # 存储策略历史
        self.strategy_history[strategy_name] = {
            "strategy_info": {
                "name": strategy_name,
                "type": strategy.__class__.__bases__[0].__name__
            },
            "timestamp": timestamp
        }
        
        # 存储回测历史
        self.backtest_history[strategy_name] = backtest_result
        
        # 存储分析历史
        self.analysis_history[strategy_name] = analysis_result
    
    def get_strategy_history(self) -> Dict[str, Any]:
        """获取策略历史"""
        return self.strategy_history
    
    def get_backtest_history(self) -> Dict[str, Any]:
        """获取回测历史"""
        return self.backtest_history
    
    def get_analysis_history(self) -> Dict[str, Any]:
        """获取分析历史"""
        return self.analysis_history
    
    def export_integrated_report(
        self,
        result: Dict[str, Any],
        export_format: str = "json",
        output_dir: str = None
    ) -> str:
        """
        导出集成报告
        
        Parameters
        ----------
        result : Dict[str, Any]
            集成结果
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
            output_dir = os.path.join(os.getcwd(), "portfolio_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        strategy_name = result.get("strategy_info", {}).get("name", "unknown")
        filename = f"portfolio_report_{strategy_name}_{timestamp}.{export_format}"
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
                html_content = self._generate_html_report(result)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            logger.info(f"✅ 集成报告已导出: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ 导出集成报告失败: {e}")
            raise
    
    def _generate_html_report(self, result: Dict[str, Any]) -> str:
        """生成HTML报告"""
        strategy_info = result.get("strategy_info", {})
        summary = result.get("summary", {})
        key_metrics = summary.get("key_metrics", {})
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>投资组合分析报告 - {strategy_info.get('name', '未知')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric-card {{ background: white; border: 1px solid #ddd; 
                              border-radius: 5px; padding: 15px; margin: 10px 0; }}
                .metric-value {{ font-size: 1.2em; font-weight: bold; color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 投资组合分析报告</h1>
                <h2>策略: {strategy_info.get('name', '未知')}</h2>
                <p>策略类型: {strategy_info.get('type', '未知')}</p>
                <p>分析时间: {result.get('timestamp', '未知')}</p>
            </div>
            
            <div class="section">
                <h3>🎯 关键指标</h3>
                <div class="metric-card">
                    <p><strong>年化收益:</strong> <span class="metric-value">{key_metrics.get('annual_return', 0):.2%}</span></p>
                    <p><strong>夏普比率:</strong> <span class="metric-value">{key_metrics.get('sharpe_ratio', 0):.2f}</span></p>
                    <p><strong>最大回撤:</strong> <span class="metric-value">{key_metrics.get('max_drawdown', 0):.2%}</span></p>
                    <p><strong>胜率:</strong> <span class="metric-value">{key_metrics.get('win_rate', 0):.2%}</span></p>
                    <p><strong>信息比率:</strong> <span class="metric-value">{key_metrics.get('information_ratio', 0):.2f}</span></p>
                </div>
            </div>
            
            <div class="section">
                <h3>📈 绩效评估</h3>
                <div class="metric-card">
                    <p><strong>总体评级:</strong> {summary.get('overall_performance', '未知')}</p>
                </div>
            </div>
            
            <div class="section">
                <h3>💡 改进建议</h3>
                <div class="metric-card">
        """
        
        # 添加建议
        for recommendation in summary.get('recommendations', []):
            html += f'<p>• {recommendation}</p>'
        
        html += """
                </div>
            </div>
            
            <div class="section">
                <p><em>注：此报告由投资组合管理集成系统自动生成</em></p>
            </div>
        </body>
        </html>
        """
        
        return html


# 全局投资组合集成实例
_global_portfolio_integration = None


def get_portfolio_integration() -> PortfolioIntegration:
    """获取全局投资组合集成实例"""
    global _global_portfolio_integration
    
    if _global_portfolio_integration is None:
        _global_portfolio_integration = PortfolioIntegration()
    
    return _global_portfolio_integration


def test_portfolio_integration():
    """测试投资组合集成"""
    print("=" * 70)
    print("测试投资组合管理集成系统")
    print("=" * 70)
    
    try:
        # 创建投资组合集成
        integration = get_portfolio_integration()
        
        # 创建测试策略
        strategy = TopkDropoutStrategy(
            topk=30,
            n_drop=5,
            signal=pd.Series(np.random.randn(10), 
                         index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318', 
                                'SH600519', 'SZ000858', 'SH600887', 'SZ002415'])
        )
        
        # 创建配置
        data_config = {
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            "universe": ["SH600000", "SZ000001", "SH600036", "SZ000002"]
        }
        
        backtest_config = {
            "initial_capital": 1000000,
            "benchmark": "SH000300",
            "frequency": "day"
        }
        
        print("🚀 开始完整投资组合分析...")
        
        # 运行完整分析
        result = integration.run_complete_portfolio_analysis(
            strategy, data_config, backtest_config
        )
        
        if result.get("success", False):
            print("✅ 完整投资组合分析完成!")
            
            # 显示关键信息
            strategy_info = result.get("strategy_info", {})
            summary = result.get("summary", {})
            key_metrics = summary.get("key_metrics", {})
            
            print(f"📊 策略名称: {strategy_info.get('name', '未知')}")
            print(f"📈 年化收益: {key_metrics.get('annual_return', 0):.2%}")
            print(f"⚡ 夏普比率: {key_metrics.get('sharpe_ratio', 0):.2f}")
            print(f"📉 最大回撤: {key_metrics.get('max_drawdown', 0):.2%}")
            print(f"🎯 总体评级: {summary.get('overall_performance', '未知')}")
            
            # 测试导出功能
            export_path = integration.export_integrated_report(
                result, "html"
            )
            print(f"💾 集成报告已导出: {export_path}")
        
        else:
            print(f"❌ 完整投资组合分析失败: {result.get('error', '未知错误')}")
        
        print("✅ 投资组合管理集成系统测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 投资组合管理集成系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_portfolio_integration()