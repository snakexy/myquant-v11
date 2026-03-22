"""
风险归因分析器 - Risk Attribution Analyzer

提供投资组合风险的深度归因分析功能，包括风险因子分解、VaR贡献度分析等。
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class RiskAttributionResult:
    """风险归因分析结果数据类"""
    total_risk: float
    factor_risk_contributions: Dict[str, float]
    specific_risk: float
    diversification_benefit: float
    marginal_risk_contributions: Dict[str, float]


@dataclass
class VaRAttributionResult:
    """VaR归因分析结果数据类"""
    portfolio_var: float
    component_var_contributions: Dict[str, float]
    marginal_var_contributions: Dict[str, float]
    var_decomposition: Dict[str, float]


class RiskAttribution:
    """
    风险归因分析器
    
    功能：
    - 风险因子分解：多因子模型风险归因
    - VaR贡献度分析：在险价值归因
    - CVaR贡献度分析：条件在险价值归因
    - 风险预算分析：风险预算分配和监控
    """
    
    def __init__(self, confidence_level: float = 0.95):
        """
        初始化风险归因分析器
        
        Args:
            confidence_level: 置信水平，默认为95%
        """
        self.confidence_level = confidence_level
        self._portfolio_weights = None
        self._cov_matrix = None
        self._factor_data = None
        self._returns_data = None
        
    def load_portfolio_data(
        self,
        portfolio_weights: pd.Series,
        cov_matrix: pd.DataFrame
    ) -> None:
        """
        加载投资组合数据
        
        Args:
            portfolio_weights: 投资组合权重
            cov_matrix: 协方差矩阵
        """
        self._portfolio_weights = portfolio_weights
        self._cov_matrix = cov_matrix
        
    def load_returns_data(self, returns: pd.DataFrame) -> None:
        """
        加载收益率数据
        
        Args:
            returns: 资产收益率数据
        """
        self._returns_data = returns
        
    def load_factor_data(
        self,
        factor_exposures: pd.DataFrame,
        factor_cov_matrix: pd.DataFrame,
        specific_risks: pd.Series
    ) -> None:
        """
        加载因子数据
        
        Args:
            factor_exposures: 因子暴露度
            factor_cov_matrix: 因子协方差矩阵
            specific_risks: 特质风险
        """
        self._factor_exposures = factor_exposures
        self._factor_cov_matrix = factor_cov_matrix
        self._specific_risks = specific_risks
    
    def factor_risk_attribution(self) -> RiskAttributionResult:
        """
        因子风险归因分析
        
        Returns:
            RiskAttributionResult: 风险归因结果
        """
        if (self._factor_exposures is None or
                self._factor_cov_matrix is None or
                self._specific_risks is None):
            raise ValueError("因子风险归因需要因子暴露度、因子协方差和特质风险数据")
            
        # 计算组合层面的因子暴露
        portfolio_factor_exposures = (
            self._portfolio_weights @ self._factor_exposures
        )
        
        # 计算因子风险贡献
        factor_risk_contributions = {}
        total_factor_risk = 0
        
        for factor in portfolio_factor_exposures.index:
            factor_variance = (
                portfolio_factor_exposures[factor] ** 2 *
                self._factor_cov_matrix.loc[factor, factor]
            )
            factor_risk_contributions[factor] = factor_variance
            total_factor_risk += factor_variance
            
        # 计算特质风险
        specific_risk = (
            (self._portfolio_weights ** 2 * self._specific_risks ** 2).sum()
        )
        
        # 计算总风险
        total_risk = np.sqrt(total_factor_risk + specific_risk)
        
        # 计算分散化收益
        undiversified_risk = np.sqrt(
            sum(factor_risk_contributions.values()) + specific_risk
        )
        diversification_benefit = (
            undiversified_risk - total_risk
        ) / undiversified_risk if undiversified_risk != 0 else 0
        
        # 计算边际风险贡献
        marginal_risk_contributions = {}
        for asset in self._portfolio_weights.index:
            marginal_contrib = (
                self._portfolio_weights[asset] *
                self._cov_matrix.loc[asset, :] @ self._portfolio_weights
            ) / total_risk if total_risk != 0 else 0
            marginal_risk_contributions[asset] = marginal_contrib
            
        return RiskAttributionResult(
            total_risk=total_risk,
            factor_risk_contributions=factor_risk_contributions,
            specific_risk=specific_risk,
            diversification_benefit=diversification_benefit,
            marginal_risk_contributions=marginal_risk_contributions
        )
    
    def var_attribution(
        self,
        method: str = 'parametric'
    ) -> VaRAttributionResult:
        """
        VaR归因分析
        
        Args:
            method: 计算方法，'parametric' 参数法，'historical' 历史法
            
        Returns:
            VaRAttributionResult: VaR归因结果
        """
        if self._portfolio_weights is None:
            raise ValueError("VaR归因需要投资组合权重数据")
            
        portfolio_weights = self._portfolio_weights
        
        if method == 'parametric':
            # 参数法VaR
            if self._cov_matrix is None:
                raise ValueError("参数法VaR需要协方差矩阵")
                
            # 计算组合标准差
            portfolio_std = np.sqrt(
                portfolio_weights.T @ self._cov_matrix @ portfolio_weights
            )
            
            # 计算VaR（假设均值为0）
            z_score = self._get_z_score()
            portfolio_var = z_score * portfolio_std
            
            # 计算边际VaR贡献
            marginal_var_contributions = {}
            component_var_contributions = {}
            
            for asset in portfolio_weights.index:
                marginal_var = (
                    z_score *
                    (self._cov_matrix.loc[asset, :] @ portfolio_weights) /
                    portfolio_std
                ) if portfolio_std != 0 else 0
                marginal_var_contributions[asset] = marginal_var
                component_var_contributions[asset] = (
                    portfolio_weights[asset] * marginal_var
                )
                
        else:
            # 历史法VaR
            if self._returns_data is None:
                raise ValueError("历史法VaR需要收益率数据")
                
            # 计算组合收益率
            portfolio_returns = self._returns_data @ portfolio_weights
            
            # 计算VaR
            portfolio_var = -np.percentile(
                portfolio_returns, (1 - self.confidence_level) * 100
            )
            
            # 简化版的边际VaR计算
            marginal_var_contributions = {}
            component_var_contributions = {}
            
            for asset in portfolio_weights.index:
                # 使用协方差近似计算边际VaR
                asset_cov = portfolio_returns.cov(self._returns_data[asset])
                marginal_var = (
                    asset_cov / portfolio_returns.var() * portfolio_var
                    if portfolio_returns.var() != 0 else 0
                )
                marginal_var_contributions[asset] = marginal_var
                component_var_contributions[asset] = (
                    portfolio_weights[asset] * marginal_var
                )
                
        # VaR分解
        var_decomposition = {
            'systematic_var': sum(component_var_contributions.values()),
            'diversification_effect': (
                portfolio_var - sum(component_var_contributions.values())
            )
        }
        
        return VaRAttributionResult(
            portfolio_var=portfolio_var,
            component_var_contributions=component_var_contributions,
            marginal_var_contributions=marginal_var_contributions,
            var_decomposition=var_decomposition
        )
    
    def cvar_attribution(self) -> Dict[str, float]:
        """
        CVaR归因分析
        
        Returns:
            Dict[str, float]: CVaR归因结果
        """
        if self._returns_data is None:
            raise ValueError("CVaR归因需要收益率数据")
            
        portfolio_weights = self._portfolio_weights
        portfolio_returns = self._returns_data @ portfolio_weights
        
        # 计算CVaR
        var_threshold = -np.percentile(
            portfolio_returns, (1 - self.confidence_level) * 100
        )
        tail_returns = portfolio_returns[portfolio_returns <= -var_threshold]
        portfolio_cvar = -tail_returns.mean()
        
        # 计算边际CVaR贡献（简化版）
        marginal_cvar_contributions = {}
        
        for asset in portfolio_weights.index:
            # 使用条件协方差计算边际CVaR
            tail_asset_returns = self._returns_data[asset][
                portfolio_returns <= -var_threshold
            ]
            conditional_cov = tail_returns.cov(tail_asset_returns)
            marginal_cvar = (
                conditional_cov / tail_returns.var() * portfolio_cvar
                if tail_returns.var() != 0 else 0
            )
            marginal_cvar_contributions[asset] = marginal_cvar
            
        return {
            'portfolio_cvar': portfolio_cvar,
            'marginal_cvar_contributions': marginal_cvar_contributions
        }
    
    def risk_budget_analysis(
        self,
        target_risk_contributions: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        风险预算分析
        
        Args:
            target_risk_contributions: 目标风险贡献（可选）
            
        Returns:
            Dict[str, float]: 风险预算分析结果
        """
        if self._portfolio_weights is None:
            raise ValueError("风险预算分析需要投资组合权重数据")
            
        # 计算当前风险贡献
        risk_attribution = self.factor_risk_attribution()
        current_risk_contributions = (
            risk_attribution.marginal_risk_contributions
        )
        
        # 如果没有目标风险贡献，使用等风险贡献
        if target_risk_contributions is None:
            n_assets = len(current_risk_contributions)
            target_risk_contributions = {
                asset: 1.0 / n_assets for asset in current_risk_contributions
            }
            
        # 计算风险预算偏差
        risk_budget_deviations = {}
        total_risk = risk_attribution.total_risk
        
        for asset in current_risk_contributions:
            current_contrib = (
                current_risk_contributions[asset] / total_risk
                if total_risk != 0 else 0
            )
            target_contrib = target_risk_contributions.get(asset, 0)
            deviation = current_contrib - target_contrib
            risk_budget_deviations[asset] = deviation
            
        return {
            'current_risk_contributions': current_risk_contributions,
            'target_risk_contributions': target_risk_contributions,
            'risk_budget_deviations': risk_budget_deviations,
            'total_risk_budget_deviation': sum(
                abs(d) for d in risk_budget_deviations.values()
            )
        }
    
    def stress_test_analysis(
        self,
        stress_scenarios: Dict[str, float]
    ) -> Dict[str, float]:
        """
        压力测试分析
        
        Args:
            stress_scenarios: 压力情景，因子变化幅度
            
        Returns:
            Dict[str, float]: 压力测试结果
        """
        if (self._factor_exposures is None or
                self._factor_cov_matrix is None):
            raise ValueError("压力测试需要因子数据")
            
        # 计算基准风险
        baseline_risk = self.factor_risk_attribution().total_risk
        
        # 计算压力情景下的风险
        stressed_risks = {}
        
        for scenario_name, stress_factor in stress_scenarios.items():
            # 应用压力情景到因子协方差矩阵
            stressed_cov_matrix = self._factor_cov_matrix.copy()
            
            if scenario_name in stressed_cov_matrix.index:
                # 单个因子压力测试
                stressed_cov_matrix.loc[scenario_name, scenario_name] *= (
                    1 + stress_factor
                )
            else:
                # 系统性压力测试（所有因子相关性增加）
                stressed_cov_matrix *= (1 + stress_factor)
                
            # 计算压力情景下的风险
            portfolio_factor_exposures = (
                self._portfolio_weights @ self._factor_exposures
            )
            stressed_risk = np.sqrt(
                portfolio_factor_exposures.T @
                stressed_cov_matrix @
                portfolio_factor_exposures
            )
            stressed_risks[scenario_name] = stressed_risk
            
        return {
            'baseline_risk': baseline_risk,
            'stressed_risks': stressed_risks,
            'risk_increases': {
                scenario: risk - baseline_risk
                for scenario, risk in stressed_risks.items()
            }
        }
    
    def generate_risk_report(self) -> Dict:
        """
        生成风险归因报告
        
        Returns:
            Dict: 风险归因报告
        """
        report = {
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
            'confidence_level': self.confidence_level,
            'data_availability': self._check_data_availability()
        }
        
        try:
            # 因子风险归因
            factor_risk_result = self.factor_risk_attribution()
            report['factor_risk_attribution'] = {
                'total_risk': factor_risk_result.total_risk,
                'factor_risk_contributions': (
                    factor_risk_result.factor_risk_contributions
                ),
                'specific_risk': factor_risk_result.specific_risk,
                'diversification_benefit': (
                    factor_risk_result.diversification_benefit
                )
            }
            
            # VaR归因
            var_result = self.var_attribution()
            report['var_attribution'] = {
                'portfolio_var': var_result.portfolio_var,
                'component_var_contributions': (
                    var_result.component_var_contributions
                ),
                'var_decomposition': var_result.var_decomposition
            }
            
            # 风险预算分析
            risk_budget_result = self.risk_budget_analysis()
            report['risk_budget_analysis'] = risk_budget_result
            
        except Exception as e:
            report['error'] = str(e)
            
        return report
    
    def _get_z_score(self) -> float:
        """
        获取Z分数
        
        Returns:
            float: 对应置信水平的Z分数
        """
        from scipy import stats
        
        if self.confidence_level == 0.95:
            return 1.645
        elif self.confidence_level == 0.99:
            return 2.326
        else:
            return stats.norm.ppf(self.confidence_level)
    
    def _check_data_availability(self) -> Dict[str, bool]:
        """
        检查数据可用性
        
        Returns:
            Dict[str, bool]: 数据可用性状态
        """
        return {
            'portfolio_weights': self._portfolio_weights is not None,
            'cov_matrix': self._cov_matrix is not None,
            'returns_data': self._returns_data is not None,
            'factor_data': (
                self._factor_exposures is not None and
                self._factor_cov_matrix is not None and
                self._specific_risks is not None
            )
        }