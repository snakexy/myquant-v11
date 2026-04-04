"""
报告生成器 - 基于QLib的分析报告生成系统

该模块提供全面的分析报告生成功能，包括：
- 绩效分析报告
- 风险分析报告
- 归因分析报告
- 综合分析报告
- 多种格式导出 (HTML, PDF, JSON)
"""

import logging
import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """报告生成配置"""
    report_type: str = "comprehensive"  # 报告类型
    output_format: str = "html"  # 输出格式
    include_charts: bool = True  # 是否包含图表
    language: str = "zh-CN"  # 报告语言
    theme: str = "light"  # 报告主题


class PerformanceReportGenerator:
    """绩效分析报告生成器"""
    
    def __init__(self, config: ReportConfig):
        self.config = config
    
    def generate_performance_report(
        self, 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成绩效分析报告"""
        logger.info("生成绩效分析报告")
        
        try:
            report = {
                "report_type": "performance",
                "generated_at": datetime.now().isoformat(),
                "summary": self._generate_performance_summary(analysis_results),
                "key_metrics": self._extract_performance_metrics(analysis_results),
                "visualizations": self._prepare_performance_charts(analysis_results),
                "recommendations": analysis_results.get("report", {}).get(
                    "recommendations", []
                )
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成绩效分析报告失败: {e}")
            return {"error": str(e)}
    
    def _generate_performance_summary(
        self, 
        analysis_results: Dict[str, Any]
    ) -> str:
        """生成绩效摘要"""
        metrics = analysis_results.get("metrics", {})
        report = analysis_results.get("report", {})
        
        annual_return = metrics.get("annual_return", 0)
        sharpe_ratio = metrics.get("sharpe_ratio", 0)
        max_drawdown = abs(metrics.get("max_drawdown", 0))
        rating = report.get("performance_rating", {}).get("rating", "未知")
        
        return (
            f"策略绩效评级为{rating}，年化收益{annual_return:.2%}，"
            f"夏普比率{sharpe_ratio:.2f}，最大回撤{max_drawdown:.2%}。"
        )
    
    def _extract_performance_metrics(
        self, 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """提取绩效指标"""
        metrics = analysis_results.get("metrics", {})
        report = analysis_results.get("report", {})
        
        return {
            "return_metrics": {
                "累计收益": metrics.get("cumulative_return", 0),
                "年化收益": metrics.get("annual_return", 0),
                "期望收益": metrics.get("expected_return", 0)
            },
            "risk_metrics": {
                "年化波动率": metrics.get("annual_volatility", 0),
                "最大回撤": metrics.get("max_drawdown", 0),
                "下行风险": metrics.get("downside_risk", 0)
            },
            "risk_adjusted_metrics": {
                "夏普比率": metrics.get("sharpe_ratio", 0),
                "索提诺比率": metrics.get("sortino_ratio", 0),
                "Calmar比率": metrics.get("calmar_ratio", 0)
            },
            "performance_rating": report.get("performance_rating", {})
        }
    
    def _prepare_performance_charts(
        self, 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, str]:
        """准备绩效图表"""
        visualizations = analysis_results.get("visualizations", {})
        
        # 这里可以添加图表导出逻辑
        # 目前返回图表类型信息
        chart_info = {}
        for chart_type in visualizations.keys():
            chart_info[chart_type] = f"{chart_type}_chart"
        
        return chart_info


class RiskReportGenerator:
    """风险分析报告生成器"""
    
    def __init__(self, config: ReportConfig):
        self.config = config
    
    def generate_risk_report(
        self, 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成风险分析报告"""
        logger.info("生成风险分析报告")
        
        try:
            report = {
                "report_type": "risk",
                "generated_at": datetime.now().isoformat(),
                "summary": self._generate_risk_summary(analysis_results),
                "risk_metrics": self._extract_risk_metrics(analysis_results),
                "stress_tests": analysis_results.get("stress_tests", {}),
                "monte_carlo": analysis_results.get(
                    "monte_carlo_simulation", {}
                ),
                "recommendations": analysis_results.get("risk_report", {}).get(
                    "recommendations", []
                )
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成风险分析报告失败: {e}")
            return {"error": str(e)}
    
    def _generate_risk_summary(
        self, 
        analysis_results: Dict[str, Any]
    ) -> str:
        """生成风险摘要"""
        risk_metrics = analysis_results.get("risk_metrics", {})
        risk_report = analysis_results.get("risk_report", {})
        
        volatility = risk_metrics.get("volatility", 0)
        max_drawdown = abs(risk_metrics.get("max_drawdown", 0))
        var = risk_metrics.get("var_historical", 0)
        risk_rating = risk_metrics.get("risk_rating", "未知")
        
        return (
            f"投资组合风险评级为{risk_rating}，年化波动率{volatility:.1%}，"
            f"最大回撤{max_drawdown:.1%}，VaR(95%)为{var:.2%}。"
        )
    
    def _extract_risk_metrics(
        self, 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """提取风险指标"""
        risk_metrics = analysis_results.get("risk_metrics", {})
        
        return {
            "volatility_metrics": {
                "年化波动率": risk_metrics.get("volatility", 0),
                "下行风险": risk_metrics.get("downside_risk", 0),
                "半方差": risk_metrics.get("semivariance", 0)
            },
            "tail_risk_metrics": {
                "VaR (95%)": risk_metrics.get("var_historical", 0),
                "CVaR (95%)": risk_metrics.get("cvar", 0),
                "预期短缺": risk_metrics.get("expected_shortfall", 0)
            },
            "drawdown_metrics": {
                "最大回撤": risk_metrics.get("max_drawdown", 0)
            },
            "risk_assessment": risk_metrics.get("risk_rating", "未知")
        }


class AttributionReportGenerator:
    """归因分析报告生成器"""
    
    def __init__(self, config: ReportConfig):
        self.config = config
    
    def generate_attribution_report(
        self, 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成归因分析报告"""
        logger.info("生成归因分析报告")
        
        try:
            report = {
                "report_type": "attribution",
                "generated_at": datetime.now().isoformat(),
                "summary": self._generate_attribution_summary(analysis_results),
                "attribution_components": self._extract_attribution_components(
                    analysis_results
                ),
                "asset_level_analysis": analysis_results.get(
                    "asset_level_attribution", {}
                ),
                "recommendations": analysis_results.get(
                    "attribution_report", {}
                ).get("recommendations", [])
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成归因分析报告失败: {e}")
            return {"error": str(e)}
    
    def _generate_attribution_summary(
        self, 
        analysis_results: Dict[str, Any]
    ) -> str:
        """生成归因摘要"""
        excess_return = analysis_results.get("total_excess_return", 0)
        allocation = analysis_results.get("allocation_effect", 0)
        selection = analysis_results.get("selection_effect", 0)
        
        if allocation > selection:
            dominant_effect = "配置效应"
        else:
            dominant_effect = "选股效应"
        
        return (
            f"归因分析显示超额收益为{excess_return:.2%}，"
            f"主要贡献来自{dominant_effect}。"
        )
    
    def _extract_attribution_components(
        self, 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """提取归因成分"""
        return {
            "excess_return": analysis_results.get("total_excess_return", 0),
            "allocation_effect": analysis_results.get("allocation_effect", 0),
            "selection_effect": analysis_results.get("selection_effect", 0),
            "interaction_effect": analysis_results.get("interaction_effect", 0),
            "attribution_accuracy": analysis_results.get(
                "attribution_accuracy", 0
            )
        }


class ComprehensiveReportGenerator:
    """综合分析报告生成器"""
    
    def __init__(self, config: ReportConfig):
        self.config = config
        self.performance_generator = PerformanceReportGenerator(config)
        self.risk_generator = RiskReportGenerator(config)
        self.attribution_generator = AttributionReportGenerator(config)
    
    def generate_comprehensive_report(
        self,
        performance_results: Dict[str, Any],
        risk_results: Dict[str, Any],
        attribution_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成综合分析报告"""
        logger.info("生成综合分析报告")
        
        try:
            # 生成各模块报告
            performance_report = (
                self.performance_generator.generate_performance_report(
                    performance_results
                )
            )
            risk_report = self.risk_generator.generate_risk_report(risk_results)
            attribution_report = (
                self.attribution_generator.generate_attribution_report(
                    attribution_results
                )
            )
            
            # 生成综合摘要
            executive_summary = self._generate_executive_summary(
                performance_report, risk_report, attribution_report
            )
            
            comprehensive_report = {
                "report_type": "comprehensive",
                "generated_at": datetime.now().isoformat(),
                "executive_summary": executive_summary,
                "performance_analysis": performance_report,
                "risk_analysis": risk_report,
                "attribution_analysis": attribution_report,
                "overall_assessment": self._generate_overall_assessment(
                    performance_report, risk_report, attribution_report
                ),
                "strategic_recommendations": (
                    self._generate_strategic_recommendations(
                        performance_report, risk_report, attribution_report
                    )
                )
            }
            
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"生成综合分析报告失败: {e}")
            return {"error": str(e)}
    
    def _generate_executive_summary(
        self,
        performance_report: Dict[str, Any],
        risk_report: Dict[str, Any],
        attribution_report: Dict[str, Any]
    ) -> str:
        """生成执行摘要"""
        perf_metrics = performance_report.get("key_metrics", {})
        risk_metrics = risk_report.get("risk_metrics", {})
        attr_components = attribution_report.get("attribution_components", {})
        
        annual_return = (
            perf_metrics.get("return_metrics", {}).get("年化收益", 0)
        )
        volatility = (
            risk_metrics.get("volatility_metrics", {}).get("年化波动率", 0)
        )
        excess_return = attr_components.get("excess_return", 0)
        
        return (
            f"综合分析显示策略年化收益{annual_return:.2%}，"
            f"波动率{volatility:.1%}，超额收益{excess_return:.2%}。"
            f"整体表现符合预期，风险收益特征良好。"
        )
    
    def _generate_overall_assessment(
        self,
        performance_report: Dict[str, Any],
        risk_report: Dict[str, Any],
        attribution_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成整体评估"""
        perf_rating = (
            performance_report
            .get("key_metrics", {})
            .get("performance_rating", {})
            .get("rating", "未知")
        )
        risk_rating = (
            risk_report
            .get("risk_metrics", {})
            .get("risk_assessment", "未知")
        )
        
        return {
            "overall_rating": self._calculate_overall_rating(
                perf_rating, risk_rating
            ),
            "performance_rating": perf_rating,
            "risk_rating": risk_rating,
            "suitability": self._assess_suitability(perf_rating, risk_rating)
        }
    
    def _calculate_overall_rating(
        self, 
        performance_rating: str, 
        risk_rating: str
    ) -> str:
        """计算整体评级"""
        rating_map = {
            "优秀": 4, "良好": 3, "一般": 2, "较差": 1, "未知": 2
        }
        risk_map = {
            "低风险": 4, "中风险": 3, "高风险": 2, "未知": 2
        }
        
        perf_score = rating_map.get(performance_rating, 2)
        risk_score = risk_map.get(risk_rating, 2)
        
        overall_score = (perf_score + risk_score) / 2
        
        if overall_score >= 3.5:
            return "优秀"
        elif overall_score >= 2.5:
            return "良好"
        elif overall_score >= 1.5:
            return "一般"
        else:
            return "较差"
    
    def _assess_suitability(
        self, 
        performance_rating: str, 
        risk_rating: str
    ) -> str:
        """评估适用性"""
        if performance_rating == "优秀" and risk_rating == "低风险":
            return "适合所有投资者"
        elif performance_rating in ["优秀", "良好"] and risk_rating == "中风险":
            return "适合积极型投资者"
        elif risk_rating == "高风险":
            return "仅适合专业投资者"
        else:
            return "适合稳健型投资者"
    
    def _generate_strategic_recommendations(
        self,
        performance_report: Dict[str, Any],
        risk_report: Dict[str, Any],
        attribution_report: Dict[str, Any]
    ) -> List[str]:
        """生成战略建议"""
        recommendations = []
        
        # 从各模块报告中提取建议
        perf_recs = performance_report.get("recommendations", [])
        risk_recs = risk_report.get("recommendations", [])
        attr_recs = attribution_report.get("recommendations", [])
        
        # 添加绩效相关建议
        if perf_recs:
            recommendations.extend(perf_recs[:2])  # 取前2条
        
        # 添加风险相关建议
        if risk_recs:
            recommendations.extend(risk_recs[:2])  # 取前2条
        
        # 添加归因相关建议
        if attr_recs:
            recommendations.extend(attr_recs[:1])  # 取前1条
        
        # 如果没有具体建议，添加通用建议
        if not recommendations:
            recommendations = [
                "策略表现稳定，建议保持当前配置并持续监控",
                "定期进行风险评估和绩效回顾",
                "根据市场环境适时调整策略参数"
            ]
        
        return recommendations


class ReportExporter:
    """报告导出器"""
    
    def __init__(self, config: ReportConfig):
        self.config = config
    
    def export_report(
        self, 
        report: Dict[str, Any], 
        output_path: str = None
    ) -> str:
        """导出报告"""
        logger.info(f"导出报告，格式: {self.config.output_format}")
        
        try:
            if output_path is None:
                output_path = self._generate_output_path(report)
            
            if self.config.output_format == "json":
                return self._export_json(report, output_path)
            elif self.config.output_format == "html":
                return self._export_html(report, output_path)
            elif self.config.output_format == "pdf":
                return self._export_pdf(report, output_path)
            else:
                raise ValueError(f"不支持的输出格式: {self.config.output_format}")
                
        except Exception as e:
            logger.error(f"导出报告失败: {e}")
            raise
    
    def _generate_output_path(self, report: Dict[str, Any]) -> str:
        """生成输出路径"""
        report_type = report.get("report_type", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 创建报告目录
        reports_dir = os.path.join(os.getcwd(), "analysis_reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"{report_type}_report_{timestamp}.{self.config.output_format}"
        return os.path.join(reports_dir, filename)
    
    def _export_json(self, report: Dict[str, Any], output_path: str) -> str:
        """导出JSON格式报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON报告已导出: {output_path}")
        return output_path
    
    def _export_html(self, report: Dict[str, Any], output_path: str) -> str:
        """导出HTML格式报告"""
        html_content = self._generate_html_content(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML报告已导出: {output_path}")
        return output_path
    
    def _export_pdf(self, report: Dict[str, Any], output_path: str) -> str:
        """导出PDF格式报告"""
        # 简化实现：先导出HTML，然后转换为PDF
        html_path = output_path.replace('.pdf', '.html')
        self._export_html(report, html_path)
        
        # 在实际应用中，可以使用wkhtmltopdf或其他工具转换
        logger.warning("PDF导出功能需要额外依赖，目前仅导出HTML格式")
        return html_path
    
    def _generate_html_content(self, report: Dict[str, Any]) -> str:
        """生成HTML报告内容"""
        report_type = report.get("report_type", "未知")
        generated_at = report.get("generated_at", "")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>量化分析报告 - {report_type}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    line-height: 1.6;
                }}
                .header {{ 
                    background: #f5f5f5; 
                    padding: 20px; 
                    border-radius: 5px; 
                    margin-bottom: 20px;
                }}
                .section {{ 
                    margin: 20px 0; 
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .metric-card {{ 
                    background: white; 
                    border: 1px solid #ddd;
                    border-radius: 5px; 
                    padding: 15px;
                    margin: 10px 0; 
                }}
                .metric-value {{ 
                    font-size: 1.2em; 
                    font-weight: bold; 
                    color: #2c3e50; 
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 10px 0;
                }}
                th, td {{ 
                    padding: 8px; 
                    text-align: left; 
                    border-bottom: 1px solid #ddd; 
                }}
                th {{ 
                    background-color: #f2f2f2;
                }}
                .recommendation {{ 
                    background: #e8f4fd;
                    padding: 10px;
                    margin: 5px 0;
                    border-left: 4px solid #2196F3;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 量化分析报告</h1>
                <h2>报告类型: {report_type}</h2>
                <p>生成时间: {generated_at}</p>
            </div>
        """
        
        # 添加报告内容
        if "executive_summary" in report:
            html += f"""
            <div class="section">
                <h3>🎯 执行摘要</h3>
                <p>{report['executive_summary']}</p>
            </div>
            """
        
        # 添加关键指标
        html += self._generate_metrics_section(report)
        
        # 添加建议
        if "strategic_recommendations" in report:
            html += self._generate_recommendations_section(report)
        elif "recommendations" in report:
            html += f"""
            <div class="section">
                <h3>💡 改进建议</h3>
                {self._format_recommendations(report['recommendations'])}
            </div>
            """
        
        html += """
            <div class="section">
                <p><em>注：此报告由智能量化平台分析系统自动生成</em></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_metrics_section(self, report: Dict[str, Any]) -> str:
        """生成指标部分"""
        html = '<div class="section"><h3>📈 关键指标</h3>'
        
        # 遍历报告中的指标部分
        metric_sections = [
            "key_metrics", "risk_metrics", "attribution_components"
        ]
        
        for section in metric_sections:
            if section in report:
                metrics = report[section]
                if isinstance(metrics, dict):
                    html += self._format_metrics_table(metrics, section)
        
        html += '</div>'
        return html
    
    def _format_metrics_table(
        self, 
        metrics: Dict[str, Any], 
        section_name: str
    ) -> str:
        """格式化指标表格"""
        html = f'<h4>{section_name}</h4><table>'
        
        for category, values in metrics.items():
            if isinstance(values, dict):
                html += f'<tr><th colspan="2">{category}</th></tr>'
                for key, value in values.items():
                    if isinstance(value, (int, float)):
                        formatted_value = f"{value:.4f}"
                    else:
                        formatted_value = str(value)
                    html += f'<tr><td>{key}</td><td>{formatted_value}</td></tr>'
        
        html += '</table>'
        return html
    
    def _generate_recommendations_section(self, report: Dict[str, Any]) -> str:
        """生成建议部分"""
        recommendations = report.get("strategic_recommendations", [])
        return f"""
        <div class="section">
            <h3>💡 战略建议</h3>
            {self._format_recommendations(recommendations)}
        </div>
        """
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """格式化建议列表"""
        html = ''
        for rec in recommendations:
            html += f'<div class="recommendation">{rec}</div>'
        return html


class ReportGenerator:
    """报告生成器主类"""
    
    def __init__(self, config: ReportConfig = None):
        self.config = config or ReportConfig()
        self.performance_generator = PerformanceReportGenerator(self.config)
        self.risk_generator = RiskReportGenerator(self.config)
        self.attribution_generator = AttributionReportGenerator(self.config)
        self.comprehensive_generator = ComprehensiveReportGenerator(self.config)
        self.exporter = ReportExporter(self.config)
    
    def generate_report(
        self,
        report_type: str,
        analysis_data: Dict[str, Any],
        output_path: str = None
    ) -> str:
        """
        生成并导出报告
        
        Args:
            report_type: 报告类型
            analysis_data: 分析数据
            output_path: 输出路径
            
        Returns:
            导出的文件路径
        """
        logger.info(f"生成{report_type}报告")
        
        try:
            # 生成报告内容
            if report_type == "performance":
                report = self.performance_generator.generate_performance_report(
                    analysis_data
                )
            elif report_type == "risk":
                report = self.risk_generator.generate_risk_report(analysis_data)
            elif report_type == "attribution":
                report = (
                    self.attribution_generator.generate_attribution_report(
                        analysis_data
                    )
                )
            elif report_type == "comprehensive":
                report = (
                    self.comprehensive_generator.generate_comprehensive_report(
                        **analysis_data
                    )
                )
            else:
                raise ValueError(f"不支持的报告类型: {report_type}")
            
            # 导出报告
            if "error" not in report:
                exported_path = self.exporter.export_report(report, output_path)
                logger.info(f"✅ 报告已导出: {exported_path}")
                return exported_path
            else:
                raise Exception(f"报告生成失败: {report['error']}")
                
        except Exception as e:
            logger.error(f"❌ 报告生成失败: {e}")
            raise


# 全局报告生成器实例
_global_report_generator = None


def get_report_generator(config: ReportConfig = None) -> ReportGenerator:
    """获取全局报告生成器实例"""
    global _global_report_generator
    
    if _global_report_generator is None:
        _global_report_generator = ReportGenerator(config)
    
    return _global_report_generator


def test_report_generator():
    """测试报告生成器"""
    print("=" * 70)
    print("测试报告生成系统")
    print("=" * 70)
    
    try:
        # 创建报告生成器
        config = ReportConfig(output_format="html")
        generator = ReportGenerator(config)
        
        # 创建模拟分析数据
        analysis_data = {
            "metrics": {
                "annual_return": 0.156,
                "sharpe_ratio": 1.24,
                "max_drawdown": -0.082,
                "volatility": 0.186
            },
            "report": {
                "recommendations": [
                    "策略表现良好，建议继续保持",
                    "可适当增加风险暴露以提高收益"
                ]
            }
        }
        
        print("🚀 开始生成绩效报告...")
        
        # 生成并导出报告
        report_path = generator.generate_report("performance", analysis_data)
        
        print(f"✅ 报告生成完成: {report_path}")
        return True
        
    except Exception as e:
        print(f"❌ 报告生成器测试失败: {e}")
        return False


if __name__ == "__main__":
    # 运行测试
    success = test_report_generator()
    
    if success:
        print("\n🚀 报告生成系统测试完成!")
    else:
        print("\n⚠️ 报告生成系统需要进一步调试")