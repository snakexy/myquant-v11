"""
简化的系统集成测试

该模块提供了一个简化的系统集成测试，避免QLib复杂数据处理问题。
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

logger = logging.getLogger(__name__)


def run_simple_integration_test():
    """运行简化的集成测试"""
    print("=" * 70)
    print("运行简化的系统集成测试")
    print("=" * 70)
    
    try:
        # 创建投资组合集成
        integration = get_portfolio_integration()
        
        test_results = []
        
        # 1. 测试策略模块
        print("🧪 测试策略模块...")
        try:
            # 创建测试策略
            signal = pd.Series(np.random.randn(5), 
                                index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318'])
            
            strategy = TopkDropoutStrategy(
                topk=30, n_drop=5, signal=signal
            )
            
            # 测试策略信息获取
            strategy_info = strategy.get_strategy_info()
            
            test_results.append({
                "test_name": "TopkDropoutStrategy",
                "success": True,
                "details": {
                    "strategy_info": strategy_info,
                    "signal_length": len(signal)
                }
            })
            
            print("✅ TopkDropoutStrategy测试通过")
            
        except Exception as e:
            test_results.append({
                "test_name": "TopkDropoutStrategy",
                "success": False,
                "error": str(e)
            })
            print(f"❌ TopkDropoutStrategy测试失败: {e}")
        
        # 2. 测试增强回测执行器（使用模拟数据）
        print("🧪 测试增强回测执行器...")
        try:
            # 创建测试策略
            strategy = TopkDropoutStrategy(
                topk=30, n_drop=5,
                signal=pd.Series(np.random.randn(5), 
                             index=['SH600000', 'SZ000001', 'SH600036', 'SZ000002', 'SH601318'])
            )
            
            # 创建配置
            data_config = {
                "start_date": "2020-01-01",
                "end_date": "2020-01-31",  # 缩短时间范围
                "universe": ["SH600000", "SZ000001", "SH600036", "SZ000002", "SH601318"]
            }
            
            backtest_config = {
                "initial_capital": 1000000,
                "benchmark": "SH000300",
                "frequency": "day"
            }
            
            # 运行回测（使用模拟数据）
            result = integration.backtest_executor.execute_enhanced_backtest(
                strategy_config={
                    "name": "测试TopkDropout策略",
                    "type": "TopkDropout",
                    "topk": 30,
                    "n_drop": 5,
                    "instruments": data_config["universe"]
                },
                start_date=data_config["start_date"],
                end_date=data_config["end_date"],
                initial_capital=backtest_config["initial_capital"],
                benchmark=backtest_config["benchmark"]
            )
            
            success = result.get("success", False)
            
            test_results.append({
                "test_name": "增强回测执行器",
                "success": success,
                "result": result
            })
            
            if success:
                print("✅ 增强回测执行器测试通过")
                basic_metrics = result.get("basic_metrics", {})
                if basic_metrics:
                    print(f"   📈 年化收益: {basic_metrics.get('annual_return', 0):.2%}")
                    print(f"   ⚡ 夏普比率: {basic_metrics.get('sharpe_ratio', 0):.2f}")
                    print(f"   📉 最大回撤: {basic_metrics.get('max_drawdown', 0):.2%}")
            else:
                print(f"❌ 增强回测执行器测试失败: {result.get('error', '未知错误')}")
            
        except Exception as e:
            test_results.append({
                "test_name": "增强回测执行器",
                "success": False,
                "error": str(e)
            })
            print(f"❌ 增强回测执行器测试失败: {e}")
        
        # 3. 测试绩效分析器
        print("🧪 测试绩效分析器...")
        try:
            # 创建模拟回测结果
            backtest_result = {
                "success": True,
                "basic_metrics": {
                    "annual_return": 0.15,
                    "sharpe_ratio": 1.2,
                    "max_drawdown": -0.08,
                    "win_rate": 0.55,
                    "volatility": 0.18
                },
                "returns": np.random.normal(0.001, 0.02, 30).tolist(),
                "dates": pd.date_range('2020-01-01', periods=30, freq='D').strftime('%Y-%m-%d').tolist()
            }
            
            # 运行绩效分析
            result = integration.performance_analyzer.analyze_strategy_performance(
                strategy, backtest_result
            )
            
            success = "analysis_id" in result
            
            test_results.append({
                "test_name": "绩效分析器",
                "success": success,
                "result": result
            })
            
            if success:
                print("✅ 绩效分析器测试通过")
            else:
                print(f"❌ 绩效分析器测试失败")
            
        except Exception as e:
            test_results.append({
                "test_name": "绩效分析器",
                "success": False,
                "error": str(e)
            })
            print(f"❌ 绩效分析器测试失败: {e}")
        
        # 计算成功率
        success_count = sum(1 for r in test_results if r["success"])
        total_count = len(test_results)
        success_rate = success_count / total_count if total_count > 0 else 0
        
        # 显示测试摘要
        print(f"\n📊 总测试数: {total_count}")
        print(f"✅ 通过测试数: {success_count}")
        print(f"❌ 失败测试数: {total_count - success_count}")
        print(f"📈 成功率: {success_rate:.1%}")
        print(f"🎯 总体状态: {'通过' if success_rate >= 0.8 else '失败'}")
        
        # 导出测试报告
        export_dir = os.path.join(os.getcwd(), "system_test_reports")
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(export_dir, f"simple_integration_test_{timestamp}.json")
        
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_results": test_results,
                "summary": {
                    "total_tests": total_count,
                    "passed_tests": success_count,
                    "failed_tests": total_count - success_count,
                    "success_rate": success_rate,
                    "overall_status": "通过" if success_rate >= 0.8 else "失败"
                },
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 测试报告已导出: {report_file}")
        
        # 返回测试结果
        return {
            "success": success_rate >= 0.8,
            "test_results": test_results,
            "summary": {
                "total_tests": total_count,
                "passed_tests": success_count,
                "failed_tests": total_count - success_count,
                "success_rate": success_rate,
                "overall_status": "通过" if success_rate >= 0.8 else "失败"
            }
        }
        
    except Exception as e:
        print(f"❌ 简化集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": f"简化集成测试失败: {str(e)}"
        }


if __name__ == "__main__":
    run_simple_integration_test()