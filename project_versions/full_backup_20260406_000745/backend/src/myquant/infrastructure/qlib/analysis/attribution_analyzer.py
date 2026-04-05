"""
归因分析器 - 基于QLib的业绩归因系统

该模块提供投资组合业绩归因分析功能，包括：
- Brinson归因模型
- Carino归因模型
- 因子归因分析
- 持仓归因分析
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AttributionConfig:
    """归因分析配置"""
    attribution_model: str = "brinson"  # 归因模型: brinson, carino, factor
    time_period: str = "monthly"  # 分析周期: daily, weekly, monthly
    include_interaction: bool = True  # 是否包含交互项
    factor_models: List[str] = None  # 因子模型列表


class BrinsonAttribution:
    """Brinson归因分析"""
    
    def __init__(self, config: AttributionConfig):
        self.config = config
    
    def calculate_attribution(
        self,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series
    ) -> Dict[str, Any]:
        """
        Brinson归因分析
        
        Args:
            portfolio_returns: 投资组合收益率
            benchmark_returns: 基准收益率
            portfolio_weights: 投资组合权重
            benchmark_weights: 基准权重
            
        Returns:
            归因分析结果
        """
        logger.info("开始Brinson归因分析")
        
        try:
            # 确保数据对齐
            common_assets = (
                portfolio_weights.index
                .intersection(benchmark_weights.index)
                .intersection(portfolio_returns.index)
                .intersection(benchmark_returns.index)
            )
            
            if len(common_assets) == 0:
                raise ValueError("没有共同的资产进行归因分析")
            
            # 提取共同资产的数据
            p_weights = portfolio_weights[common_assets]
            b_weights = benchmark_weights[common_assets]
            p_returns = portfolio_returns[common_assets]
            b_returns = benchmark_returns[common_assets]
            
            # 计算总超额收益
            total_portfolio_return = (p_weights * p_returns).sum()
            total_benchmark_return = (b_weights * b_returns).sum()
            total_excess_return = total_portfolio_return - total_benchmark_return
            
            # 计算归因成分
            allocation_effect = self._calculate_allocation_effect(
                p_weights, b_weights, b_returns
            )
            selection_effect = self._calculate_selection_effect(
                p_weights, p_returns, b_returns
            )
            
            # 交互效应
            interaction_effect = 0.0
            if self.config.include_interaction:
                interaction_effect = self._calculate_interaction_effect(
                    p_weights, b_weights, p_returns, b_returns
                )
            
            # 验证归因结果
            attribution_sum = allocation_effect + selection_effect + interaction_effect
            attribution_error = total_excess_return - attribution_sum
            
            results = {
                "total_portfolio_return": float(total_portfolio_return),
                "total_benchmark_return": float(total_benchmark_return),
                "total_excess_return": float(total_excess_return),
                "allocation_effect": float(allocation_effect),
                "selection_effect": float(selection_effect),
                "interaction_effect": float(interaction_effect),
                "attribution_error": float(attribution_error),
                "attribution_accuracy": float(1 - abs(attribution_error) / 
                    (abs(total_excess_return) + 1e-8))
            }
            
            # 按资产分解归因
            asset_level_attribution = (
                self._calculate_asset_level_attribution(
                    p_weights, b_weights, p_returns, b_returns
                )
            )
            results["asset_level_attribution"] = asset_level_attribution
            
            logger.info("Brinson归因分析完成")
            return results
            
        except Exception as e:
            logger.error(f"Brinson归因分析失败: {e}")
            return {"error": str(e)}
    
    def _calculate_allocation_effect(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        benchmark_returns: pd.Series
    ) -> float:
        """计算配置效应"""
        # 配置效应 = Σ(wi_p - wi_b) * (Ri_b - R_b)
        benchmark_total_return = benchmark_returns.mean()
        allocation_effect = (
            (portfolio_weights - benchmark_weights) * 
            (benchmark_returns - benchmark_total_return)
        ).sum()
        
        return allocation_effect
    
    def _calculate_selection_effect(
        self,
        portfolio_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> float:
        """计算选股效应"""
        # 选股效应 = Σwi_b * (Ri_p - Ri_b)
        selection_effect = (
            portfolio_weights * (portfolio_returns - benchmark_returns)
        ).sum()
        
        return selection_effect
    
    def _calculate_interaction_effect(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> float:
        """计算交互效应"""
        # 交互效应 = Σ(wi_p - wi_b) * (Ri_p - Ri_b)
        interaction_effect = (
            (portfolio_weights - benchmark_weights) * 
            (portfolio_returns - benchmark_returns)
        ).sum()
        
        return interaction_effect
    
    def _calculate_asset_level_attribution(
        self,
        portfolio_weights: pd.Series,
        benchmark_weights: pd.Series,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> Dict[str, Dict[str, float]]:
        """计算资产级别的归因"""
        asset_attribution = {}
        benchmark_total_return = benchmark_returns.mean()
        
        for asset in portfolio_weights.index:
            if asset in benchmark_weights.index:
                allocation = (
                    (portfolio_weights[asset] - benchmark_weights[asset]) *
                    (benchmark_returns[asset] - benchmark_total_return)
                )
                
                selection = (
                    benchmark_weights[asset] * 
                    (portfolio_returns[asset] - benchmark_returns[asset])
                )
                
                interaction = (
                    (portfolio_weights[asset] - benchmark_weights[asset]) *
                    (portfolio_returns[asset] - benchmark_returns[asset])
                )
                
                asset_attribution[asset] = {
                    "allocation_effect": float(allocation),
                    "selection_effect": float(selection),
                    "interaction_effect": float(interaction),
                    "total_attribution": float(allocation + selection + interaction)
                }
        
        return asset_attribution


class CarinoAttribution:
    """Carino多期归因分析"""
    
    def __init__(self, config: AttributionConfig):
        self.config = config
    
    def calculate_multi_period_attribution(
        self,
        portfolio_returns: pd.DataFrame,
        benchmark_returns: pd.DataFrame,
        portfolio_weights: pd.DataFrame,
        benchmark_weights: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Carino多期归因分析
        
        Args:
            portfolio_returns: 多期投资组合收益率
            benchmark_returns: 多期基准收益率
            portfolio_weights: 多期投资组合权重
            benchmark_weights: 多期基准权重
            
        Returns:
            多期归因分析结果
        """
        logger.info("开始Carino多期归因分析")
        
        try:
            # 确保时间周期一致
            common_periods = (
                portfolio_returns.index
                .intersection(benchmark_returns.index)
                .intersection(portfolio_weights.index)
                .intersection(benchmark_weights.index)
            )
            
            if len(common_periods) == 0:
                raise ValueError("没有共同的时间周期进行多期归因分析")
            
            # 提取共同周期的数据
            p_returns = portfolio_returns.loc[common_periods]
            b_returns = benchmark_returns.loc[common_periods]
            p_weights = portfolio_weights.loc[common_periods]
            b_weights = benchmark_weights.loc[common_periods]
            
            # 计算累积收益
            cumulative_portfolio_return = (1 + p_returns.sum(axis=1)).prod() - 1
            cumulative_benchmark_return = (1 + b_returns.sum(axis=1)).prod() - 1
            cumulative_excess_return = (
                cumulative_portfolio_return - cumulative_benchmark_return
            )
            
            # 计算Carino系数
            carino_coefficients = self._calculate_carino_coefficients(
                cumulative_portfolio_return, cumulative_benchmark_return,
                p_returns.sum(axis=1), b_returns.sum(axis=1)
            )
            
            # 计算单期归因
            period_attributions = []
            total_allocation = 0.0
            total_selection = 0.0
            total_interaction = 0.0
            
            for period in common_periods:
                brinson = BrinsonAttribution(self.config)
                period_result = brinson.calculate_attribution(
                    p_returns.loc[period], b_returns.loc[period],
                    p_weights.loc[period], b_weights.loc[period]
                )
                
                if "error" not in period_result:
                    # 使用Carino系数调整单期归因
                    k = carino_coefficients.get(period, 1.0)
                    period_allocation = period_result["allocation_effect"] * k
                    period_selection = period_result["selection_effect"] * k
                    period_interaction = period_result["interaction_effect"] * k
                    
                    total_allocation += period_allocation
                    total_selection += period_selection
                    total_interaction += period_interaction
                    
                    period_attributions.append({
                        "period": period,
                        "allocation_effect": float(period_allocation),
                        "selection_effect": float(period_selection),
                        "interaction_effect": float(period_interaction),
                        "carino_coefficient": float(k)
                    })
            
            # 计算归因误差
            attribution_sum = total_allocation + total_selection + total_interaction
            attribution_error = cumulative_excess_return - attribution_sum
            
            results = {
                "cumulative_portfolio_return": float(cumulative_portfolio_return),
                "cumulative_benchmark_return": float(cumulative_benchmark_return),
                "cumulative_excess_return": float(cumulative_excess_return),
                "total_allocation_effect": float(total_allocation),
                "total_selection_effect": float(total_selection),
                "total_interaction_effect": float(total_interaction),
                "attribution_error": float(attribution_error),
                "attribution_accuracy": float(1 - abs(attribution_error) / 
                    (abs(cumulative_excess_return) + 1e-8)),
                "period_attributions": period_attributions,
                "carino_coefficients": carino_coefficients
            }
            
            logger.info("Carino多期归因分析完成")
            return results
            
        except Exception as e:
            logger.error(f"Carino多期归因分析失败: {e}")
            return {"error": str(e)}
    
    def _calculate_carino_coefficients(
        self,
        cumulative_portfolio_return: float,
        cumulative_benchmark_return: float,
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> Dict[Any, float]:
        """计算Carino系数"""
        coefficients = {}
        
        # 计算对数收益率
        log_portfolio = np.log(1 + cumulative_portfolio_return)
        log_benchmark = np.log(1 + cumulative_benchmark_return)
        
        for period, (p_return, b_return) in zip(
            portfolio_returns.index, 
            zip(portfolio_returns, benchmark_returns)
        ):
            log_p = np.log(1 + p_return)
            log_b = np.log(1 + b_return)
            
            if abs(log_portfolio - log_benchmark) > 1e-8:
                k = (log_p - log_b) / (log_portfolio - log_benchmark)
            else:
                k = 1.0  # 避免除零
            
            coefficients[period] = k
        
        return coefficients


class FactorAttribution:
    """因子归因分析"""
    
    def __init__(self, config: AttributionConfig):
        self.config = config
    
    def calculate_factor_attribution(
        self,
        portfolio_returns: pd.Series,
        factor_returns: pd.DataFrame,
        factor_exposures: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        因子归因分析
        
        Args:
            portfolio_returns: 投资组合收益率
            factor_returns: 因子收益率
            factor_exposures: 因子暴露度
            
        Returns:
            因子归因结果
        """
        logger.info("开始因子归因分析")
        
        try:
            # 确保数据对齐
            common_periods = (
                portfolio_returns.index
                .intersection(factor_returns.index)
                .intersection(factor_exposures.index)
            )
            
            if len(common_periods) == 0:
                raise ValueError("没有共同的时间周期进行因子归因分析")
            
            # 提取共同周期的数据
            p_returns = portfolio_returns[common_periods]
            f_returns = factor_returns.loc[common_periods]
            f_exposures = factor_exposures.loc[common_periods]
            
            # 计算因子归因
            factor_contributions = {}
            total_factor_return = 0.0
            
            for factor in f_returns.columns:
                if factor in f_exposures.columns:
                    # 因子贡献 = 因子暴露度 * 因子收益率
                    factor_contribution = (
                        f_exposures[factor] * f_returns[factor]
                    ).mean()
                    
                    factor_contributions[factor] = {
                        "contribution": float(factor_contribution),
                        "average_exposure": float(f_exposures[factor].mean()),
                        "average_return": float(f_returns[factor].mean())
                    }
                    
                    total_factor_return += factor_contribution
            
            # 计算残差（无法由因子解释的部分）
            average_portfolio_return = p_returns.mean()
            residual_return = average_portfolio_return - total_factor_return
            
            results = {
                "average_portfolio_return": float(average_portfolio_return),
                "total_factor_return": float(total_factor_return),
                "residual_return": float(residual_return),
                "r_squared": float(
                    total_factor_return / 
                    (average_portfolio_return + 1e-8)
                ),
                "factor_contributions": factor_contributions
            }
            
            logger.info("因子归因分析完成")
            return results
            
        except Exception as e:
            logger.error(f"因子归因分析失败: {e}")
            return {"error": str(e)}


class AttributionAnalyzer:
    """归因分析器主类"""
    
    def __init__(self, config: AttributionConfig = None):
        self.config = config or AttributionConfig()
        self.brinson_attribution = BrinsonAttribution(self.config)
        self.carino_attribution = CarinoAttribution(self.config)
        self.factor_attribution = FactorAttribution(self.config)
        self.analysis_results = {}
    
    def analyze_attribution(
        self,
        analysis_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行归因分析
        
        Args:
            analysis_type: 分析类型 (brinson, carino, factor)
            **kwargs: 分析所需参数
            
        Returns:
            归因分析结果
        """
        logger.info(f"开始{analysis_type}归因分析")
        
        try:
            analysis_id = f"attribution_{analysis_type}_{len(self.analysis_results) + 1}"
            
            if analysis_type == "brinson":
                results = self.brinson_attribution.calculate_attribution(**kwargs)
            elif analysis_type == "carino":
                results = self.carino_attribution.calculate_multi_period_attribution(
                    **kwargs
                )
            elif analysis_type == "factor":
                results = self.factor_attribution.calculate_factor_attribution(
                    **kwargs
                )
            else:
                raise ValueError(f"不支持的归因分析类型: {analysis_type}")
            
            if "error" not in results:
                # 生成归因报告
                results["attribution_report"] = (
                    self._generate_attribution_report(results, analysis_type)
                )
                results["analysis_id"] = analysis_id
                results["timestamp"] = pd.Timestamp.now().isoformat()
                
                self.analysis_results[analysis_id] = results
                logger.info(f"✅ {analysis_type}归因分析完成: {analysis_id}")
            else:
                logger.error(f"❌ {analysis_type}归因分析失败: {results['error']}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 归因分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"归因分析失败: {str(e)}"
            }
    
    def _generate_attribution_report(
        self, 
        results: Dict[str, Any], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """生成归因分析报告"""
        report = {
            "analysis_type": analysis_type,
            "summary": self._generate_attribution_summary(results, analysis_type),
            "key_findings": self._extract_key_findings(results, analysis_type),
            "recommendations": self._generate_attribution_recommendations(results)
        }
        
        return report
    
    def _generate_attribution_summary(
        self, 
        results: Dict[str, Any], 
        analysis_type: str
    ) -> str:
        """生成归因摘要"""
        if analysis_type == "brinson":
            excess_return = results.get("total_excess_return", 0)
            allocation = results.get("allocation_effect", 0)
            selection = results.get("selection_effect", 0)
            
            if allocation > selection:
                dominant_effect = "配置效应"
            else:
                dominant_effect = "选股效应"
            
            return (
                f"Brinson归因分析显示超额收益为{excess_return:.2%}，"
                f"主要贡献来自{dominant_effect}。"
            )
        
        elif analysis_type == "carino":
            excess_return = results.get("cumulative_excess_return", 0)
            return f"Carino多期归因分析显示累计超额收益为{excess_return:.2%}。"
        
        elif analysis_type == "factor":
            r_squared = results.get("r_squared", 0)
            return f"因子归因分析显示模型解释度为{r_squared:.1%}。"
        
        else:
            return "归因分析完成。"
    
    def _extract_key_findings(
        self, 
        results: Dict[str, Any], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """提取关键发现"""
        findings = {}
        
        if analysis_type == "brinson":
            findings["excess_return"] = results.get("total_excess_return", 0)
            findings["allocation_contribution"] = results.get("allocation_effect", 0)
            findings["selection_contribution"] = results.get("selection_effect", 0)
            findings["attribution_accuracy"] = results.get("attribution_accuracy", 0)
        
        elif analysis_type == "carino":
            findings["cumulative_excess_return"] = (
                results.get("cumulative_excess_return", 0)
            )
            findings["total_allocation"] = results.get("total_allocation_effect", 0)
            findings["total_selection"] = results.get("total_selection_effect", 0)
        
        elif analysis_type == "factor":
            findings["r_squared"] = results.get("r_squared", 0)
            findings["residual_return"] = results.get("residual_return", 0)
        
        return findings
    
    def _generate_attribution_recommendations(
        self, 
        results: Dict[str, Any]
    ) -> List[str]:
        """生成归因改进建议"""
        recommendations = []
        
        # 基于Brinson归因的建议
        if "allocation_effect" in results and "selection_effect" in results:
            allocation = results["allocation_effect"]
            selection = results["selection_effect"]
            
            if allocation < 0:
                recommendations.append("配置效应为负，建议优化资产配置权重")
            
            if selection < 0:
                recommendations.append("选股效应为负，建议改进个股选择能力")
        
        # 基于因子归因的建议
        if "r_squared" in results:
            r_squared = results["r_squared"]
            if r_squared < 0.7:
                recommendations.append("因子解释度较低，建议增加更多有效因子")
        
        if not recommendations:
            recommendations.append("归因结果良好，建议继续保持当前策略")
        
        return recommendations


# 全局归因分析器实例
_global_attribution_analyzer = None


def get_attribution_analyzer(config: AttributionConfig = None) -> AttributionAnalyzer:
    """获取全局归因分析器实例"""
    global _global_attribution_analyzer
    
    if _global_attribution_analyzer is None:
        _global_attribution_analyzer = AttributionAnalyzer(config)
    
    return _global_attribution_analyzer


def test_attribution_analyzer():
    """测试归因分析器"""
    print("=" * 70)
    print("测试归因分析系统")
    print("=" * 70)
    
    try:
        # 创建归因分析器
        analyzer = AttributionAnalyzer()
        
        # 创建模拟数据
        assets = ['Stock_A', 'Stock_B', 'Stock_C', 'Stock_D']
        dates = pd.date_range('2020-01-01', periods=5, freq='M')
        
        np.random.seed(42)
        
        # 投资组合权重（主动偏离基准）
        benchmark_weights = pd.Series([0.25, 0.25, 0.25, 0.25], index=assets)
        portfolio_weights = pd.Series([0.3, 0.2, 0.35, 0.15], index=assets)
        
        # 收益率数据
        benchmark_returns = pd.Series(
            np.random.normal(0.01, 0.02, len(assets)), index=assets
        )
        portfolio_returns = pd.Series(
            np.random.normal(0.012, 0.02, len(assets)), index=assets
        )
        
        print("🚀 开始Brinson归因分析...")
        
        # 运行Brinson归因分析
        brinson_result = analyzer.analyze_attribution(
            "brinson",
            portfolio_returns=portfolio_returns,
            benchmark_returns=benchmark_returns,
            portfolio_weights=portfolio_weights,
            benchmark_weights=benchmark_weights
        )
        
        if "analysis_id" in brinson_result:
            print("✅ Brinson归因分析完成!")
            print(f"📈 超额收益: {brinson_result['total_excess_return']:.2%}")
            print(f"📊 配置效应: {brinson_result['allocation_effect']:.2%}")
            print(f"🎯 选股效应: {brinson_result['selection_effect']:.2%}")
            print(f"🔗 交互效应: {brinson_result['interaction_effect']:.2%}")
            
            return True
        else:
            print(f"❌ 归因分析失败: {brinson_result.get('error', '未知错误')}")
            return False
        
    except Exception as e:
        print(f"❌ 归因分析器测试失败: {e}")
        return False


if __name__ == "__main__":
    # 运行测试
    success = test_attribution_analyzer()
    
    if success:
        print("\n🚀 归因分析系统测试完成!")
    else:
        print("\n⚠️ 归因分析系统需要进一步调试")