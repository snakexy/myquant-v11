"""
QLib分析系统 - 基于QLib的全面分析框架

该模块提供完整的分析功能，包括：
- 性能分析 (Performance Analysis)
- 风险分析 (Risk Analysis) 
- 归因分析 (Attribution Analysis)
- 报告生成 (Report Generation)
- QLib桥接 (QLib Bridge)

主要组件:
- performance_analyzer: 绩效分析系统
- risk_analyzer: 风险分析系统
- attribution_analyzer: 归因分析系统
- report_generator: 报告生成系统
- qlib_analysis_bridge: QLib分析桥接器
"""

from .performance_analyzer import (
    PerformanceAnalyzer,
    PerformanceMetrics,
    PerformanceVisualizer,
    get_performance_analyzer,
    test_performance_analyzer
)

from .risk_analyzer import (
    RiskAnalyzer,
    RiskConfig,
    RiskMetricsCalculator,
    StressTester,
    MonteCarloSimulator,
    get_risk_analyzer,
    test_risk_analyzer
)

from .attribution_analyzer import (
    AttributionAnalyzer,
    AttributionConfig,
    BrinsonAttribution,
    CarinoAttribution,
    FactorAttribution,
    get_attribution_analyzer,
    test_attribution_analyzer
)

from .report_generator import (
    ReportGenerator,
    ReportConfig,
    PerformanceReportGenerator,
    RiskReportGenerator,
    AttributionReportGenerator,
    ComprehensiveReportGenerator,
    ReportExporter,
    get_report_generator,
    test_report_generator
)

from .qlib_analysis_bridge import (
    QLibAnalysisBridge,
    AnalysisConfig,
    AnalysisBridgeFactory,
    run_qlib_analysis,
    integrate_qlib_analysis
)

# 导出主要类
__all__ = [
    # 性能分析
    "PerformanceAnalyzer",
    "PerformanceMetrics", 
    "PerformanceVisualizer",
    "get_performance_analyzer",
    "test_performance_analyzer",
    
    # 风险分析
    "RiskAnalyzer",
    "RiskConfig",
    "RiskMetricsCalculator",
    "StressTester", 
    "MonteCarloSimulator",
    "get_risk_analyzer",
    "test_risk_analyzer",
    
    # 归因分析
    "AttributionAnalyzer",
    "AttributionConfig",
    "BrinsonAttribution",
    "CarinoAttribution",
    "FactorAttribution",
    "get_attribution_analyzer", 
    "test_attribution_analyzer",
    
    # 报告生成
    "ReportGenerator",
    "ReportConfig",
    "PerformanceReportGenerator",
    "RiskReportGenerator",
    "AttributionReportGenerator",
    "ComprehensiveReportGenerator",
    "ReportExporter",
    "get_report_generator",
    "test_report_generator",
    
    # QLib桥接
    "QLibAnalysisBridge",
    "AnalysisConfig", 
    "AnalysisBridgeFactory",
    "run_qlib_analysis",
    "integrate_qlib_analysis"
]


def test_analysis_system():
    """测试整个分析系统"""
    print("=" * 70)
    print("测试QLib分析系统")
    print("=" * 70)
    
    results = {}
    
    # 测试性能分析器
    print("\n1. 测试性能分析器...")
    try:
        results["performance"] = test_performance_analyzer()
    except Exception as e:
        print(f"❌ 性能分析器测试失败: {e}")
        results["performance"] = False
    
    # 测试风险分析器
    print("\n2. 测试风险分析器...")
    try:
        results["risk"] = test_risk_analyzer()
    except Exception as e:
        print(f"❌ 风险分析器测试失败: {e}")
        results["risk"] = False
    
    # 测试归因分析器
    print("\n3. 测试归因分析器...")
    try:
        results["attribution"] = test_attribution_analyzer()
    except Exception as e:
        print(f"❌ 归因分析器测试失败: {e}")
        results["attribution"] = False
    
    # 测试报告生成器
    print("\n4. 测试报告生成器...")
    try:
        results["report"] = test_report_generator()
    except Exception as e:
        print(f"❌ 报告生成器测试失败: {e}")
        results["report"] = False
    
    # 汇总结果
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print("\n" + "=" * 70)
    print("分析系统测试汇总")
    print("=" * 70)
    
    for component, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{component:15} {status}")
    
    print(f"\n测试结果: {successful_tests}/{total_tests} 通过")
    
    if successful_tests == total_tests:
        print("🎉 分析系统所有组件测试通过!")
        return True
    else:
        print("⚠️  部分组件需要进一步调试")
        return False


def get_analysis_system():
    """获取完整的分析系统实例"""
    return {
        "performance_analyzer": get_performance_analyzer(),
        "risk_analyzer": get_risk_analyzer(),
        "attribution_analyzer": get_attribution_analyzer(),
        "report_generator": get_report_generator()
    }


def create_comprehensive_analysis(
    backtest_results: dict,
    benchmark_data: dict = None
) -> dict:
    """
    创建综合分析
    
    Args:
        backtest_results: 回测结果
        benchmark_data: 基准数据
        
    Returns:
        综合分析结果
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("开始创建综合分析")
    
    try:
        analysis_system = get_analysis_system()
        
        # 运行性能分析
        performance_analyzer = analysis_system["performance_analyzer"]
        performance_results = performance_analyzer.analyze_backtest(
            backtest_results, benchmark_data
        )
        
        # 运行风险分析
        risk_analyzer = analysis_system["risk_analyzer"]
        returns = performance_analyzer._extract_returns_from_backtest(
            backtest_results
        )
        risk_results = risk_analyzer.analyze_risk(returns)
        
        # 运行归因分析（如果有基准数据）
        attribution_results = {}
        if benchmark_data and "returns" in benchmark_data:
            attribution_analyzer = analysis_system["attribution_analyzer"]
            # 这里需要提供归因分析所需的具体数据
            # attribution_results = attribution_analyzer.analyze_attribution(...)
        
        # 生成综合报告
        report_generator = analysis_system["report_generator"]
        comprehensive_report = report_generator.generate_report(
            "comprehensive",
            {
                "performance_results": performance_results,
                "risk_results": risk_results,
                "attribution_results": attribution_results
            }
        )
        
        logger.info("综合分析创建完成")
        
        return {
            "success": True,
            "performance_analysis": performance_results,
            "risk_analysis": risk_results,
            "attribution_analysis": attribution_results,
            "comprehensive_report": comprehensive_report
        }
        
    except Exception as e:
        logger.error(f"创建综合分析失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# 版本信息
__version__ = "1.0.0"
__author__ = "智能量化平台团队"
__description__ = "基于QLib的全面分析框架"


if __name__ == "__main__":
    # 运行系统测试
    test_analysis_system()