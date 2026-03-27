"""
系统集成测试模块

该模块提供了完整的系统集成测试功能，
验证投资组合管理、回测和绩效分析系统的集成效果。
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any
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
from qlib_core.integration.portfolio_integration import get_portfolio_integration
from qlib_core.integration.qlib_integration import get_qlib_integration

logger = logging.getLogger(__name__)


class SystemIntegrationTest:
    """系统集成测试类"""
    
    def __init__(self):
        """初始化系统集成测试"""
        self.portfolio_integration = get_portfolio_integration()
        self.qlib_integration = get_qlib_integration()
        
        # 测试结果存储
        self.test_results = {}
        
        logger.info("系统集成测试初始化完成")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        运行所有系统测试
        
        Returns
        -------
        Dict[str, Any]
            测试结果汇总
        """
        try:
            logger.info("🚀 开始系统集成测试")
            
            # 1. 测试策略模块
            strategy_test_result = self.test_strategy_module()
            
            # 2. 测试回测执行器
            backtest_test_result = self.test_backtest_executor()
            
            # 3. 测试绩效分析器
            analysis_test_result = self.test_performance_analyzer()
            
            # 4. 测试投资组合集成
            portfolio_test_result = self.test_portfolio_integration()
            
            # 5. 测试QLib集成
            qlib_test_result = self.test_qlib_integration()
            
            # 6. 测试完整工作流
            workflow_test_result = self.test_complete_workflow()
            
            # 7. 测试策略比较
            comparison_test_result = self.test_strategy_comparison()
            
            # 8. 测试参数优化
            optimization_test_result = self.test_parameter_optimization()
            
            # 汇总测试结果
            all_results = {
                "strategy_module": strategy_test_result,
                "backtest_executor": backtest_test_result,
                "performance_analyzer": analysis_test_result,
                "portfolio_integration": portfolio_test_result,
                "qlib_integration": qlib_test_result,
                "complete_workflow": workflow_test_result,
                "strategy_comparison": comparison_test_result,
                "parameter_optimization": optimization_test_result,
                "overall_summary": self._generate_test_summary([
                    strategy_test_result, backtest_test_result, analysis_test_result,
                    portfolio_test_result, qlib_test_result, workflow_test_result,
                    comparison_test_result, optimization_test_result
                ])
            }
            
            # 存储测试结果
            self.test_results = all_results
            
            logger.info("✅ 系统集成测试完成")
            return all_results
            
        except Exception as e:
            logger.error(f"❌ 系统集成测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"系统集成测试失败: {str(e)}"
            }
    
    def test_strategy_module(self) -> Dict[str, Any]:
        """测试策略模块"""
        try:
            logger.info("🧪 测试策略模块")
            
            test_results = []
            
            # 测试TopkDropoutStrategy
            try:
                signal = pd.Series(np.random.randn(10), 
                                index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318', 
                                       'SH600519', 'SZ000858', 'SH600887', 'SZ002415'])
                
                strategy = TopkDropoutStrategy(
                    topk=30, n_drop=5, signal=signal
                )
                
                # 测试策略信息获取
                strategy_info = strategy.get_strategy_info()
                
                # 测试目标权重生成
                test_date = datetime.now()
                test_positions = pd.DataFrame({
                    'stock': ['SH600000', 'SZ000001'],
                    'weight': [0.5, 0.5]
                })
                test_positions.index = pd.MultiIndex.from_tuples(
                    [(test_date, stock) for stock in test_positions['stock']],
                    names=['datetime', 'instrument']
                )
                
                target_weights = strategy.generate_target_weight_position(
                    test_date, test_positions
                )
                
                test_results.append({
                    "test_name": "TopkDropoutStrategy",
                    "success": True,
                    "details": {
                        "strategy_info": strategy_info,
                        "target_weights_generated": len(target_weights) > 0
                    }
                })
                
            except Exception as e:
                test_results.append({
                    "test_name": "TopkDropoutStrategy",
                    "success": False,
                    "error": str(e)
                })
            
            # 测试EnhancedIndexingStrategy
            try:
                strategy = EnhancedIndexingStrategy(
                    benchmark_weights={'SH600000': 0.3, 'SZ000001': 0.7},
                    risk_model_type='factor',
                    tracking_error_limit=0.02
                )
                
                strategy_info = strategy.get_strategy_info()
                
                test_results.append({
                    "test_name": "EnhancedIndexingStrategy",
                    "success": True,
                    "details": {
                        "strategy_info": strategy_info
                    }
                })
                
            except Exception as e:
                test_results.append({
                    "test_name": "EnhancedIndexingStrategy",
                    "success": False,
                    "error": str(e)
                })
            
            # 计算成功率
            success_count = sum(1 for r in test_results if r["success"])
            total_count = len(test_results)
            success_rate = success_count / total_count if total_count > 0 else 0
            
            return {
                "success": success_rate >= 0.8,
                "success_rate": success_rate,
                "test_results": test_results,
                "summary": f"策略模块测试: {success_count}/{total_count} 通过"
            }
            
        except Exception as e:
            logger.error(f"策略模块测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "策略模块测试失败"
            }
    
    def test_backtest_executor(self) -> Dict[str, Any]:
        """测试回测执行器"""
        try:
            logger.info("🧪 测试回测执行器")
            
            # 创建测试策略
            strategy = TopkDropoutStrategy(
                topk=30, n_drop=5,
                signal=pd.Series(np.random.randn(5), 
                             index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318'])
            )
            
            # 创建配置
            data_config = {
                "start_date": "2020-01-01",
                "end_date": "2020-12-31",
                "universe": ["SH600000", "SZ000001", "SH600036", "SZ000002", "SH601318"]
            }
            
            backtest_config = {
                "initial_capital": 1000000,
                "benchmark": "SH000300",
                "frequency": "day"
            }
            
            # 运行回测
            result = self.portfolio_integration.backtest_executor.run_backtest(
                strategy, data_config, backtest_config
            )
            
            success = result.get("success", False)
            
            return {
                "success": success,
                "result": result,
                "summary": f"回测执行器测试: {'通过' if success else '失败'}"
            }
            
        except Exception as e:
            logger.error(f"回测执行器测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "回测执行器测试失败"
            }
    
    def test_performance_analyzer(self) -> Dict[str, Any]:
        """测试绩效分析器"""
        try:
            logger.info("🧪 测试绩效分析器")
            
            # 创建测试策略
            strategy = TopkDropoutStrategy(
                topk=30, n_drop=5,
                signal=pd.Series(np.random.randn(5), 
                             index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318'])
            )
            
            # 创建模拟回测结果
            backtest_result = {
                "strategy_name": "测试策略",
                "start_date": "2020-01-01",
                "end_date": "2020-12-31",
                "initial_capital": 1000000,
                "final_capital": 1150000,
                "result": {
                    "success": True,
                    "returns": np.random.normal(0.001, 0.02, 252).tolist(),
                    "dates": pd.date_range('2020-01-01', periods=252, freq='D').strftime('%Y-%m-%d').tolist(),
                    "nav_curve": (1 + np.random.normal(0.001, 0.02, 252)).cumprod().tolist()
                }
            }
            
            # 运行绩效分析
            result = self.portfolio_integration.performance_analyzer.analyze_strategy_performance(
                strategy, backtest_result
            )
            
            success = "analysis_id" in result
            
            return {
                "success": success,
                "result": result,
                "summary": f"绩效分析器测试: {'通过' if success else '失败'}"
            }
            
        except Exception as e:
            logger.error(f"绩效分析器测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "绩效分析器测试失败"
            }
    
    def test_portfolio_integration(self) -> Dict[str, Any]:
        """测试投资组合集成"""
        try:
            logger.info("🧪 测试投资组合集成")
            
            # 创建测试策略
            strategy = TopkDropoutStrategy(
                topk=30, n_drop=5,
                signal=pd.Series(np.random.randn(5), 
                             index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318'])
            )
            
            # 创建配置
            data_config = {
                "start_date": "2020-01-01",
                "end_date": "2020-12-31",
                "universe": ["SH600000", "SZ000001", "SH600036", "SZ000002", "SH601318"]
            }
            
            backtest_config = {
                "initial_capital": 1000000,
                "benchmark": "SH000300",
                "frequency": "day"
            }
            
            # 运行完整投资组合分析
            result = self.portfolio_integration.run_complete_portfolio_analysis(
                strategy, data_config, backtest_config
            )
            
            success = result.get("success", False)
            
            return {
                "success": success,
                "result": result,
                "summary": f"投资组合集成测试: {'通过' if success else '失败'}"
            }
            
        except Exception as e:
            logger.error(f"投资组合集成测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "投资组合集成测试失败"
            }
    
    def test_qlib_integration(self) -> Dict[str, Any]:
        """测试QLib集成"""
        try:
            logger.info("🧪 测试QLib集成")
            
            # 创建测试策略
            strategy = TopkDropoutStrategy(
                topk=30, n_drop=5,
                signal=pd.Series(np.random.randn(5), 
                             index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318'])
            )
            
            # 运行QLib兼容分析
            result = self.qlib_integration.run_comprehensive_analysis(
                strategy,
                "2020-01-01",
                "2020-12-31",
                "SH000300",
                use_qlib_native=True
            )
            
            success = result.get("success", False)
            
            return {
                "success": success,
                "result": result,
                "summary": f"QLib集成测试: {'通过' if success else '失败'}"
            }
            
        except Exception as e:
            logger.error(f"QLib集成测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "QLib集成测试失败"
            }
    
    def test_complete_workflow(self) -> Dict[str, Any]:
        """测试完整工作流"""
        try:
            logger.info("🧪 测试完整工作流")
            
            # 创建测试策略
            strategy = TopkDropoutStrategy(
                topk=30, n_drop=5,
                signal=pd.Series(np.random.randn(5), 
                             index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318'])
            )
            
            # 1. 运行完整分析
            result = self.portfolio_integration.run_complete_portfolio_analysis(
                strategy,
                {
                    "start_date": "2020-01-01",
                    "end_date": "2020-12-31",
                    "universe": ["SH600000", "SZ000001", "SH600036", "SZ000002", "SH601318"]
                },
                {
                    "initial_capital": 1000000,
                    "benchmark": "SH000300",
                    "frequency": "day"
                }
            )
            
            success = result.get("success", False)
            
            # 2. 测试报告导出
            if success:
                try:
                    export_path = self.portfolio_integration.export_integrated_report(
                        result, "json"
                    )
                    export_success = os.path.exists(export_path)
                except Exception:
                    export_success = False
            else:
                export_success = False
            
            overall_success = success and export_success
            
            return {
                "success": overall_success,
                "result": result,
                "export_success": export_success,
                "summary": f"完整工作流测试: {'通过' if overall_success else '失败'}"
            }
            
        except Exception as e:
            logger.error(f"完整工作流测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "完整工作流测试失败"
            }
    
    def test_strategy_comparison(self) -> Dict[str, Any]:
        """测试策略比较"""
        try:
            logger.info("🧪 测试策略比较")
            
            # 创建多个测试策略
            strategies = [
                TopkDropoutStrategy(
                    topk=30, n_drop=5,
                    signal=pd.Series(np.random.randn(5), 
                                 index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318'])
                ),
                TopkDropoutStrategy(
                    topk=20, n_drop=3,
                    signal=pd.Series(np.random.randn(5), 
                                 index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318'])
                )
            ]
            
            # 创建配置
            data_config = {
                "start_date": "2020-01-01",
                "end_date": "2020-12-31",
                "universe": ["SH600000", "SZ000001", "SH600036", "SZ000002", "SH601318"]
            }
            
            backtest_config = {
                "initial_capital": 1000000,
                "benchmark": "SH000300",
                "frequency": "day"
            }
            
            # 运行策略比较
            result = self.portfolio_integration.run_strategy_comparison(
                strategies, data_config, backtest_config
            )
            
            success = result.get("success", False)
            
            return {
                "success": success,
                "result": result,
                "summary": f"策略比较测试: {'通过' if success else '失败'}"
            }
            
        except Exception as e:
            logger.error(f"策略比较测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "策略比较测试失败"
            }
    
    def test_parameter_optimization(self) -> Dict[str, Any]:
        """测试参数优化"""
        try:
            logger.info("🧪 测试参数优化")
            
            # 创建参数网格
            parameter_grid = {
                "topk": [20, 30, 40],
                "n_drop": [3, 5, 7]
            }
            
            # 创建配置
            data_config = {
                "start_date": "2020-01-01",
                "end_date": "2020-06-30",  # 缩短时间以加快测试
                "universe": ["SH600000", "SZ000001", "SH600036", "SZ000002", "SH601318"]
            }
            
            backtest_config = {
                "initial_capital": 1000000,
                "benchmark": "SH000300",
                "frequency": "day"
            }
            
            # 运行参数优化
            result = self.portfolio_integration.run_parameter_optimization(
                TopkDropoutStrategy, parameter_grid, data_config, backtest_config
            )
            
            success = result.get("success", False)
            
            return {
                "success": success,
                "result": result,
                "summary": f"参数优化测试: {'通过' if success else '失败'}"
            }
            
        except Exception as e:
            logger.error(f"参数优化测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "参数优化测试失败"
            }
    
    def _generate_test_summary(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成测试摘要"""
        success_count = sum(1 for r in test_results if r.get("success", False))
        total_count = len(test_results)
        success_rate = success_count / total_count if total_count > 0 else 0
        
        # 详细结果
        detailed_results = {}
        for result in test_results:
            test_name = result.get("summary", "未知测试")
            detailed_results[test_name] = {
                "success": result.get("success", False),
                "details": result.get("result", {})
            }
        
        return {
            "total_tests": total_count,
            "passed_tests": success_count,
            "failed_tests": total_count - success_count,
            "success_rate": success_rate,
            "overall_status": "通过" if success_rate >= 0.8 else "失败",
            "detailed_results": detailed_results
        }
    
    def export_test_report(
        self,
        export_format: str = "json",
        output_dir: str = None
    ) -> str:
        """
        导出测试报告
        
        Parameters
        ----------
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
            output_dir = os.path.join(os.getcwd(), "system_test_reports")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_integration_test_{timestamp}.{export_format}"
        filepath = os.path.join(output_dir, filename)
        
        try:
            if export_format == "json":
                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(
                        self.test_results,
                        f,
                        ensure_ascii=False,
                        indent=2,
                        default=str
                    )
            
            elif export_format == "html":
                html_content = self._generate_html_test_report()
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            logger.info(f"✅ 系统测试报告已导出: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ 导出系统测试报告失败: {e}")
            raise
    
    def _generate_html_test_report(self) -> str:
        """生成HTML测试报告"""
        overall_summary = self.test_results.get("overall_summary", {})
        detailed_results = overall_summary.get("detailed_results", {})
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>系统集成测试报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .test-card {{ background: white; border: 1px solid #ddd; 
                             border-radius: 5px; padding: 15px; margin: 10px 0; }}
                .status-pass {{ color: #27ae60; }}
                .status-fail {{ color: #e74c3c; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧪 系统集成测试报告</h1>
                <p>测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h3>📊 测试摘要</h3>
                <div class="test-card">
                    <p><strong>总测试数:</strong> {overall_summary.get('total_tests', 0)}</p>
                    <p><strong>通过测试数:</strong> {overall_summary.get('passed_tests', 0)}</p>
                    <p><strong>失败测试数:</strong> {overall_summary.get('failed_tests', 0)}</p>
                    <p><strong>成功率:</strong> {overall_summary.get('success_rate', 0):.1%}</p>
                    <p><strong>总体状态:</strong> 
                       <span class="{'status-pass' if overall_summary.get('overall_status') == '通过' else 'status-fail'}">
                           {overall_summary.get('overall_status', '未知')}
                       </span>
                    </p>
                </div>
            </div>
            
            <div class="section">
                <h3>📋 详细测试结果</h3>
                <div class="test-card">
                    <table>
                        <tr><th>测试项目</th><th>状态</th><th>详情</th></tr>
        """
        
        # 添加详细测试结果
        for test_name, test_result in detailed_results.items():
            status = "通过" if test_result.get("success", False) else "失败"
            status_class = "status-pass" if test_result.get("success", False) else "status-fail"
            
            html += f"""
                        <tr>
                            <td>{test_name}</td>
                            <td><span class="{status_class}">{status}</span></td>
                            <td>{len(str(test_result.get('details', {})))} 个数据项</td>
                        </tr>
            """
        
        html += """
                    </table>
                </div>
            </div>
            
            <div class="section">
                <p><em>注：此报告由系统集成测试模块自动生成</em></p>
            </div>
        </body>
        </html>
        """
        
        return html


def run_system_integration_test():
    """运行系统集成测试"""
    print("=" * 70)
    print("运行系统集成测试")
    print("=" * 70)
    
    try:
        # 创建测试实例
        test_runner = SystemIntegrationTest()
        
        # 运行所有测试
        test_results = test_runner.run_all_tests()
        
        # 显示测试摘要
        overall_summary = test_results.get("overall_summary", {})
        print(f"📊 总测试数: {overall_summary.get('total_tests', 0)}")
        print(f"✅ 通过测试数: {overall_summary.get('passed_tests', 0)}")
        print(f"❌ 失败测试数: {overall_summary.get('failed_tests', 0)}")
        print(f"📈 成功率: {overall_summary.get('success_rate', 0):.1%}")
        print(f"🎯 总体状态: {overall_summary.get('overall_status', '未知')}")
        
        # 导出测试报告
        export_path = test_runner.export_test_report("html")
        print(f"💾 测试报告已导出: {export_path}")
        
        # 返回测试结果
        return test_results
        
    except Exception as e:
        print(f"❌ 系统集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    run_system_integration_test()