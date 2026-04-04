"""
风险分析器 - 基于QLib的风险分析系统

该模块提供全面的风险分析功能，包括：
- 风险指标计算（VaR, CVaR, 波动率等）
- 风险因子分析
- 压力测试
- 风险归因分析
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import scipy.stats as stats

logger = logging.getLogger(__name__)


@dataclass
class RiskConfig:
    """风险分析配置"""
    confidence_level: float = 0.95  # 置信水平
    lookback_period: int = 252  # 回看期
    risk_free_rate: float = 0.03  # 无风险利率
    monte_carlo_simulations: int = 10000  # 蒙特卡洛模拟次数
    stress_test_scenarios: List[str] = None  # 压力测试场景


class RiskMetricsCalculator:
    """风险指标计算器"""
    
    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
        self.risk_metrics = {}
    
    def calculate_comprehensive_risk(
        self, 
        returns: pd.Series,
        portfolio_weights: pd.Series = None,
        covariance_matrix: pd.DataFrame = None
    ) -> Dict[str, Any]:
        """
        计算全面风险指标
        
        Args:
            returns: 收益率序列
            portfolio_weights: 投资组合权重
            covariance_matrix: 协方差矩阵
            
        Returns:
            风险指标字典
        """
        logger.info("开始计算全面风险指标")
        
        risk_metrics = {}
        
        # 基本风险指标
        risk_metrics.update(self._calculate_basic_risk_metrics(returns))
        
        # 高级风险指标
        risk_metrics.update(self._calculate_advanced_risk_metrics(returns))
        
        # 如果提供了权重和协方差矩阵，计算组合风险
        if portfolio_weights is not None and covariance_matrix is not None:
            risk_metrics.update(
                self._calculate_portfolio_risk(
                    portfolio_weights, covariance_matrix
                )
            )
        
        # 风险评级
        risk_metrics["risk_rating"] = self._assess_risk_rating(risk_metrics)
        
        self.risk_metrics = risk_metrics
        return risk_metrics
    
    def _calculate_basic_risk_metrics(
        self, returns: pd.Series
    ) -> Dict[str, float]:
        """计算基本风险指标"""
        metrics = {}
        
        # 波动率
        metrics["volatility"] = float(returns.std() * np.sqrt(252))
        metrics["annualized_volatility"] = metrics["volatility"]
        
        # 下行风险
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            metrics["downside_risk"] = float(
                downside_returns.std() * np.sqrt(252)
            )
        else:
            metrics["downside_risk"] = 0.0
        
        # 偏度和峰度
        metrics["skewness"] = float(returns.skew())
        metrics["kurtosis"] = float(returns.kurtosis())
        
        # 最大回撤
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        metrics["max_drawdown"] = float(drawdown.min())
        
        return metrics
    
    def _calculate_advanced_risk_metrics(
        self, returns: pd.Series
    ) -> Dict[str, float]:
        """计算高级风险指标"""
        metrics = {}
        
        # VaR (历史模拟法)
        var_historical = returns.quantile(1 - self.config.confidence_level)
        metrics["var_historical"] = float(var_historical)
        
        # VaR (参数法 - 正态分布)
        var_parametric = stats.norm.ppf(
            1 - self.config.confidence_level, returns.mean(), returns.std()
        )
        metrics["var_parametric"] = float(var_parametric)
        
        # CVaR (条件VaR)
        cvar_threshold = returns.quantile(1 - self.config.confidence_level)
        cvar_returns = returns[returns <= cvar_threshold]
        metrics["cvar"] = float(cvar_returns.mean())
        
        # 预期短缺 (Expected Shortfall)
        metrics["expected_shortfall"] = metrics["cvar"]
        
        # 半方差
        negative_returns = returns[returns < 0]
        if len(negative_returns) > 0:
            metrics["semivariance"] = float(negative_returns.var())
        else:
            metrics["semivariance"] = 0.0
        
        # 风险价值比率 (VaR Ratio)
        annual_return = ((1 + returns).prod() - 1) * (252 / len(returns))
        metrics["var_ratio"] = (
            float(annual_return / abs(metrics["var_historical"]))
            if abs(metrics["var_historical"]) > 0 else 0.0
        )
        
        return metrics
    
    def _calculate_portfolio_risk(
        self, 
        weights: pd.Series, 
        covariance_matrix: pd.DataFrame
    ) -> Dict[str, float]:
        """计算投资组合风险"""
        metrics = {}
        
        try:
            # 确保权重和协方差矩阵对齐
            common_assets = weights.index.intersection(covariance_matrix.index)
            if len(common_assets) == 0:
                logger.warning("权重和协方差矩阵没有共同资产")
                return metrics
            
            weights = weights[common_assets]
            cov_matrix = covariance_matrix.loc[common_assets, common_assets]
            
            # 组合波动率
            portfolio_variance = weights.T @ cov_matrix @ weights
            metrics["portfolio_volatility"] = float(np.sqrt(portfolio_variance))
            
            # 组合Beta (相对于市场)
            # 这里假设市场组合为等权重
            market_weights = pd.Series(
                1/len(common_assets), index=common_assets
            )
            market_variance = market_weights.T @ cov_matrix @ market_weights
            covariance_with_market = weights.T @ cov_matrix @ market_weights
            
            if market_variance > 0:
                metrics["portfolio_beta"] = float(
                    covariance_with_market / market_variance
                )
            else:
                metrics["portfolio_beta"] = 0.0
            
            # 跟踪误差 (如果与基准比较)
            metrics["tracking_error"] = metrics["portfolio_volatility"]
            
        except Exception as e:
            logger.error(f"计算投资组合风险失败: {e}")
        
        return metrics
    
    def _assess_risk_rating(self, risk_metrics: Dict[str, float]) -> str:
        """风险评估"""
        volatility = risk_metrics.get("volatility", 0)
        max_drawdown = abs(risk_metrics.get("max_drawdown", 0))
        var_historical = risk_metrics.get("var_historical", 0)
        
        risk_score = 0
        
        # 波动率评分
        if volatility > 0.25:
            risk_score += 3
        elif volatility > 0.15:
            risk_score += 2
        elif volatility > 0.08:
            risk_score += 1
        
        # 最大回撤评分
        if max_drawdown > 0.2:
            risk_score += 3
        elif max_drawdown > 0.12:
            risk_score += 2
        elif max_drawdown > 0.06:
            risk_score += 1
        
        # VaR评分
        if var_historical < -0.08:
            risk_score += 3
        elif var_historical < -0.05:
            risk_score += 2
        elif var_historical < -0.03:
            risk_score += 1
        
        # 风险等级
        if risk_score >= 7:
            return "高风险"
        elif risk_score >= 4:
            return "中风险"
        else:
            return "低风险"


class StressTester:
    """压力测试器"""
    
    def __init__(self, config: RiskConfig):
        self.config = config
    
    def run_stress_tests(
        self, 
        returns: pd.Series,
        scenarios: List[str] = None
    ) -> Dict[str, Any]:
        """
        运行压力测试
        
        Args:
            returns: 收益率序列
            scenarios: 压力测试场景列表
            
        Returns:
            压力测试结果
        """
        if scenarios is None:
            scenarios = ["market_crash", "volatility_spike", "liquidity_crisis"]
        
        results = {}
        
        for scenario in scenarios:
            try:
                if scenario == "market_crash":
                    results[scenario] = self._market_crash_test(returns)
                elif scenario == "volatility_spike":
                    results[scenario] = self._volatility_spike_test(returns)
                elif scenario == "liquidity_crisis":
                    results[scenario] = self._liquidity_crisis_test(returns)
                else:
                    logger.warning(f"未知的压力测试场景: {scenario}")
            except Exception as e:
                logger.error(f"压力测试 {scenario} 失败: {e}")
                results[scenario] = {"error": str(e)}
        
        return results
    
    def _market_crash_test(self, returns: pd.Series) -> Dict[str, float]:
        """市场崩盘压力测试"""
        # 模拟市场崩盘：收益率下降2个标准差
        crash_returns = returns - 2 * returns.std()
        
        calculator = RiskMetricsCalculator(self.config)
        risk_metrics = calculator.calculate_comprehensive_risk(crash_returns)
        
        return {
            "scenario": "market_crash",
            "impact_on_var": (
                risk_metrics.get("var_historical", 0) - 
                returns.quantile(0.05)
            ),
            "impact_on_cvar": (
                risk_metrics.get("cvar", 0) - 
                returns[returns <= returns.quantile(0.05)].mean()
            ),
            "max_drawdown_under_stress": risk_metrics.get("max_drawdown", 0)
        }
    
    def _volatility_spike_test(self, returns: pd.Series) -> Dict[str, float]:
        """波动率飙升压力测试"""
        # 模拟波动率飙升：波动率增加50%
        volatility_multiplier = 1.5
        spike_returns = returns * volatility_multiplier
        
        calculator = RiskMetricsCalculator(self.config)
        risk_metrics = calculator.calculate_comprehensive_risk(spike_returns)
        
        return {
            "scenario": "volatility_spike",
            "volatility_increase": volatility_multiplier,
            "new_volatility": risk_metrics.get("volatility", 0),
            "var_under_stress": risk_metrics.get("var_historical", 0)
        }
    
    def _liquidity_crisis_test(self, returns: pd.Series) -> Dict[str, float]:
        """流动性危机压力测试"""
        # 模拟流动性危机：增加交易成本和冲击成本
        liquidity_impact = 0.02  # 2%的流动性冲击
        crisis_returns = returns - liquidity_impact
        
        calculator = RiskMetricsCalculator(self.config)
        risk_metrics = calculator.calculate_comprehensive_risk(crisis_returns)
        
        return {
            "scenario": "liquidity_crisis",
            "liquidity_impact": liquidity_impact,
            "impact_on_returns": -liquidity_impact,
            "risk_metrics_under_stress": {
                "var": risk_metrics.get("var_historical", 0),
                "cvar": risk_metrics.get("cvar", 0),
                "max_drawdown": risk_metrics.get("max_drawdown", 0)
            }
        }


class MonteCarloSimulator:
    """蒙特卡洛模拟器"""
    
    def __init__(self, config: RiskConfig):
        self.config = config
    
    def run_monte_carlo_simulation(
        self, 
        returns: pd.Series,
        periods: int = 252,
        simulations: int = None
    ) -> Dict[str, Any]:
        """
        运行蒙特卡洛模拟
        
        Args:
            returns: 历史收益率序列
            periods: 模拟期数
            simulations: 模拟次数
            
        Returns:
            蒙特卡洛模拟结果
        """
        if simulations is None:
            simulations = self.config.monte_carlo_simulations
        
        logger.info(f"开始蒙特卡洛模拟: {simulations}次, {periods}期")
        
        try:
            # 基于历史收益率的参数估计
            mu = returns.mean()
            sigma = returns.std()
            
            # 生成随机路径
            np.random.seed(42)  # 保证结果可重现
            simulated_paths = np.random.normal(
                mu, sigma, (simulations, periods)
            )
            
            # 计算模拟路径的统计量
            final_values = (1 + simulated_paths).prod(axis=1)
            mean_final_value = final_values.mean()
            var_95 = np.percentile(final_values, 5)
            cvar_95 = final_values[final_values <= var_95].mean()
            
            # 计算风险指标
            risk_metrics = {
                "mean_final_value": float(mean_final_value),
                "var_95": float(var_95),
                "cvar_95": float(cvar_95),
                "probability_of_loss": float(np.mean(final_values < 1)),
                "expected_shortfall": float(1 - cvar_95),
                "best_case": float(final_values.max()),
                "worst_case": float(final_values.min())
            }
            
            return {
                "success": True,
                "simulation_parameters": {
                    "simulations": simulations,
                    "periods": periods,
                    "mean_return": mu,
                    "volatility": sigma
                },
                "risk_metrics": risk_metrics,
                "simulated_paths": simulated_paths.tolist()  # 转换为列表便于序列化
            }
            
        except Exception as e:
            logger.error(f"蒙特卡洛模拟失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class RiskAnalyzer:
    """风险分析器主类"""
    
    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
        self.metrics_calculator = RiskMetricsCalculator(self.config)
        self.stress_tester = StressTester(self.config)
        self.monte_carlo_simulator = MonteCarloSimulator(self.config)
        self.analysis_results = {}
    
    def analyze_risk(
        self, 
        returns: pd.Series,
        portfolio_weights: pd.Series = None,
        covariance_matrix: pd.DataFrame = None,
        run_stress_tests: bool = True,
        run_monte_carlo: bool = True
    ) -> Dict[str, Any]:
        """
        执行全面风险分析
        
        Args:
            returns: 收益率序列
            portfolio_weights: 投资组合权重
            covariance_matrix: 协方差矩阵
            run_stress_tests: 是否运行压力测试
            run_monte_carlo: 是否运行蒙特卡洛模拟
            
        Returns:
            风险分析结果
        """
        logger.info("开始全面风险分析")
        
        try:
            analysis_id = f"risk_analysis_{len(self.analysis_results) + 1}"
            
            # 计算基本风险指标
            risk_metrics = self.metrics_calculator.calculate_comprehensive_risk(
                returns, portfolio_weights, covariance_matrix
            )
            
            results = {
                "analysis_id": analysis_id,
                "risk_metrics": risk_metrics,
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
            # 运行压力测试
            if run_stress_tests:
                stress_test_results = self.stress_tester.run_stress_tests(
                    returns
                )
                results["stress_tests"] = stress_test_results
            
            # 运行蒙特卡洛模拟
            if run_monte_carlo:
                monte_carlo_results = (
                    self.monte_carlo_simulator.run_monte_carlo_simulation(
                        returns
                    )
                )
                results["monte_carlo_simulation"] = monte_carlo_results
            
            # 生成风险报告
            results["risk_report"] = self._generate_risk_report(results)
            
            self.analysis_results[analysis_id] = results
            logger.info(f"✅ 风险分析完成: {analysis_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 风险分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"风险分析失败: {str(e)}"
            }
    
    def _generate_risk_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成风险分析报告"""
        risk_metrics = analysis_results.get("risk_metrics", {})
        
        report = {
            "executive_summary": self._generate_executive_summary(risk_metrics),
            "key_risk_indicators": self._extract_key_risk_indicators(risk_metrics),
            "risk_assessment": self._assess_overall_risk(risk_metrics),
            "recommendations": self._generate_risk_recommendations(risk_metrics)
        }
        
        return report
    
    def _generate_executive_summary(self, risk_metrics: Dict[str, float]) -> str:
        """生成执行摘要"""
        volatility = risk_metrics.get("volatility", 0)
        max_drawdown = abs(risk_metrics.get("max_drawdown", 0))
        var = risk_metrics.get("var_historical", 0)
        risk_rating = risk_metrics.get("risk_rating", "未知")
        
        if risk_rating == "高风险":
            summary = (
                f"投资组合风险较高（{risk_rating}），波动率{volatility:.1%}，"
                f"最大回撤{max_drawdown:.1%}，建议加强风险控制。"
            )
        elif risk_rating == "中风险":
            summary = (
                f"投资组合风险适中（{risk_rating}），波动率{volatility:.1%}，"
                f"在正常市场环境下风险可控。"
            )
        else:
            summary = (
                f"投资组合风险较低（{risk_rating}），波动率{volatility:.1%}，"
                f"适合风险厌恶型投资者。"
            )
        
        return summary
    
    def _extract_key_risk_indicators(self, risk_metrics: Dict[str, float]) -> Dict[str, Any]:
        """提取关键风险指标"""
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
            "distribution_metrics": {
                "偏度": risk_metrics.get("skewness", 0),
                "峰度": risk_metrics.get("kurtosis", 0)
            }
        }
    
    def _assess_overall_risk(self, risk_metrics: Dict[str, float]) -> Dict[str, Any]:
        """评估整体风险"""
        return {
            "risk_rating": risk_metrics.get("risk_rating", "未知"),
            "volatility_level": (
                "高" if risk_metrics.get("volatility", 0) > 0.2
                else "中" if risk_metrics.get("volatility", 0) > 0.1
                else "低"
            ),
            "tail_risk_level": (
                "高" if risk_metrics.get("var_historical", 0) < -0.05
                else "中" if risk_metrics.get("var_historical", 0) < -0.03
                else "低"
            ),
            "drawdown_risk_level": (
                "高" if abs(risk_metrics.get("max_drawdown", 0)) > 0.15
                else "中" if abs(risk_metrics.get("max_drawdown", 0)) > 0.08
                else "低"
            )
        }
    
    def _generate_risk_recommendations(self, risk_metrics: Dict[str, float]) -> List[str]:
        """生成风险改进建议"""
        recommendations = []
        
        volatility = risk_metrics.get("volatility", 0)
        max_drawdown = abs(risk_metrics.get("max_drawdown", 0))
        var = risk_metrics.get("var_historical", 0)
        
        if volatility > 0.2:
            recommendations.append("波动率较高，建议增加防御性资产配置")
        
        if max_drawdown > 0.15:
            recommendations.append("最大回撤较大，建议设置止损机制")
        
        if var < -0.05:
            recommendations.append("尾部风险较高，建议购买保护性期权")
        
        if not recommendations:
            recommendations.append("风险水平适中，建议保持当前配置并定期监控")
        
        return recommendations


# 全局风险分析器实例
_global_risk_analyzer = None


def get_risk_analyzer(config: RiskConfig = None) -> RiskAnalyzer:
    """获取全局风险分析器实例"""
    global _global_risk_analyzer
    
    if _global_risk_analyzer is None:
        _global_risk_analyzer = RiskAnalyzer(config)
    
    return _global_risk_analyzer


def test_risk_analyzer():
    """测试风险分析器"""
    print("=" * 70)
    print("测试风险分析系统")
    print("=" * 70)
    
    try:
        # 创建风险分析器
        analyzer = RiskAnalyzer()
        
        # 创建模拟收益率数据
        dates = pd.date_range('2020-01-01', periods=252, freq='D')
        np.random.seed(42)
        returns = pd.Series(
            np.random.normal(0.001, 0.02, 252), index=dates
        )
        
        print("🚀 开始风险分析...")
        
        # 运行风险分析
        analysis_result = analyzer.analyze_risk(returns)
        
        if "analysis_id" in analysis_result:
            print("✅ 风险分析完成!")
            
            # 显示关键风险指标
            risk_metrics = analysis_result["risk_metrics"]
            print(f"📊 年化波动率: {risk_metrics['volatility']:.2%}")
            print(f"📉 最大回撤: {risk_metrics['max_drawdown']:.2%}")
            print(f"⚠️  VaR (95%): {risk_metrics['var_historical']:.2%}")
            print(f"🔥  CVaR (95%): {risk_metrics['cvar']:.2%}")
            print(f"🏷️  风险评级: {risk_metrics['risk_rating']}")
            
            # 显示压力测试结果
            if "stress_tests" in analysis_result:
                print("\n📋 压力测试结果:")
                for scenario, result in analysis_result["stress_tests"].items():
                    if "error" not in result:
                        print(f"  - {scenario}: VaR影响 {result.get('impact_on_var', 0):.2%}")
            
            return True
            
        else:
            print(f"❌ 风险分析失败: {analysis_result.get('error', '未知错误')}")
            return False
        
    except Exception as e:
        print(f"❌ 风险分析器测试失败: {e}")
        return False


if __name__ == "__main__":
    # 运行测试
    success = test_risk_analyzer()
    
    if success:
        print("\n🚀 风险分析系统测试完成!")
    else:
        print("\n⚠️ 风险分析系统需要进一步调试")