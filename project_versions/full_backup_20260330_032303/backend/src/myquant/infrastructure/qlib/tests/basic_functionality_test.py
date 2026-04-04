"""
基础功能测试
测试各个模块的基本功能，避免复杂操作
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """测试模块导入"""
    logger.info("🧪 测试模块导入...")
    
    try:
        # 测试策略模块导入
        from qlib_core.backtest.portfolio_management.strategy.topk_dropout_strategy import TopkDropoutStrategy
        logger.info("✅ TopkDropoutStrategy导入成功")
        
        # 测试分析器导入
        from qlib_core.analysis.enhanced_performance_analyzer import EnhancedPerformanceAnalyzer
        logger.info("✅ EnhancedPerformanceAnalyzer导入成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 模块导入失败: {e}")
        return False

def test_strategy_creation():
    """测试策略创建"""
    logger.info("🧪 测试策略创建...")
    
    try:
        from qlib_core.backtest.portfolio_management.strategy.topk_dropout_strategy import TopkDropoutStrategy
        
        # 创建简单的预测数据
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        instruments = ['SH600000', 'SZ000001']
        
        data = []
        for date in dates:
            for instrument in instruments:
                score = np.random.randn()
                data.append((date, instrument, score))
        
        pred_score = pd.DataFrame(data, columns=['datetime', 'instrument', 'score'])
        pred_score = pred_score.set_index(['datetime', 'instrument'])['score']
        
        # 创建策略
        strategy = TopkDropoutStrategy(
            topk=2,
            n_drop=1,
            signal=pred_score
        )
        
        logger.info("✅ TopkDropoutStrategy创建成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 策略创建失败: {e}")
        return False

def test_analyzer_creation():
    """测试分析器创建"""
    logger.info("🧪 测试分析器创建...")
    
    try:
        from qlib_core.analysis.enhanced_performance_analyzer import EnhancedPerformanceAnalyzer
        
        # 创建分析器
        analyzer = EnhancedPerformanceAnalyzer()
        
        logger.info("✅ EnhancedPerformanceAnalyzer创建成功")
        return True
        
    except Exception as e:
        logger.error(f"❌ 分析器创建失败: {e}")
        return False

def test_simple_data_processing():
    """测试简单数据处理"""
    logger.info("🧪 测试简单数据处理...")
    
    try:
        # 创建简单数据
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        returns = np.random.normal(0.001, 0.02, len(dates))
        
        # 创建Series
        return_series = pd.Series(returns, index=dates)
        
        # 计算基本统计
        mean_return = return_series.mean()
        std_return = return_series.std()
        
        logger.info(f"✅ 数据处理成功，均值: {mean_return:.4f}, 标准差: {std_return:.4f}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据处理失败: {e}")
        return False

def run_basic_functionality_test():
    """运行基础功能测试"""
    logger.info("=" * 70)
    logger.info("运行基础功能测试")
    logger.info("=" * 70)
    
    test_results = []
    
    # 测试模块导入
    result1 = test_imports()
    test_results.append(("模块导入", result1))
    
    # 测试策略创建
    result2 = test_strategy_creation()
    test_results.append(("策略创建", result2))
    
    # 测试分析器创建
    result3 = test_analyzer_creation()
    test_results.append(("分析器创建", result3))
    
    # 测试简单数据处理
    result4 = test_simple_data_processing()
    test_results.append(("数据处理", result4))
    
    # 统计结果
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result in test_results if result)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # 输出结果
    logger.info("\n" + "=" * 50)
    logger.info("测试结果汇总")
    logger.info("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n📊 总测试数: {total_tests}")
    logger.info(f"✅ 通过测试数: {passed_tests}")
    logger.info(f"❌ 失败测试数: {failed_tests}")
    logger.info(f"📈 成功率: {success_rate:.1f}%")
    
    # 判断总体状态
    if success_rate >= 75:
        logger.info("🎯 总体状态: 良好")
        overall_status = "良好"
    elif success_rate >= 50:
        logger.info("🎯 总体状态: 需要改进")
        overall_status = "需要改进"
    else:
        logger.info("🎯 总体状态: 严重问题")
        overall_status = "严重问题"
    
    # 保存测试报告
    test_report = {
        "test_time": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": success_rate,
        "overall_status": overall_status,
        "test_details": [
            {
                "test_name": test_name,
                "result": result,
                "status": "通过" if result else "失败"
            }
            for test_name, result in test_results
        ]
    }
    
    # 创建报告目录
    report_dir = "system_test_reports"
    os.makedirs(report_dir, exist_ok=True)
    
    # 保存报告
    report_path = os.path.join(
        report_dir,
        f"basic_functionality_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    import json
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 测试报告已导出: {report_path}")
    
    return test_report

if __name__ == "__main__":
    run_basic_functionality_test()