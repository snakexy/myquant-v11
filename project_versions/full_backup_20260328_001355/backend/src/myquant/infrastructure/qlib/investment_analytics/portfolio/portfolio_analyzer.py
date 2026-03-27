"""
投资组合分析器 - Portfolio Analyzer

提供投资组合的深度分析功能，包括组合绩效评估、风险分析、持仓分析等。
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class PortfolioMetrics:
    """投资组合指标数据类
    
    存储投资组合的各种绩效指标，包括收益率、风险指标等。
    
    Attributes:
        total_return: 总收益率
        annual_return: 年化收益率
        volatility: 波动率
        sharpe_ratio: 夏普比率
        max_drawdown: 最大回撤
        calmar_ratio: 卡玛比率
        information_ratio: 信息比率
        alpha: 阿尔法值
        beta: 贝塔值
        tracking_error: 跟踪误差
        var_95: 95% VaR值
        cvar_95: 95% CVaR值
    """
    total_return: float
    annual_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    calmar_ratio: float
    information_ratio: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
    tracking_error: Optional[float] = None
    var_95: Optional[float] = None
    cvar_95: Optional[float] = None


@dataclass
class HoldingAnalysis:
    """持仓分析数据类
    
    存储投资组合的持仓分析结果，包括行业配置、风格暴露等。
    
    Attributes:
        top_holdings: 前十大持仓
        sector_allocation: 行业配置
        style_exposure: 风格暴露
        concentration_ratio: 集中度比率
        turnover_rate: 换手率
    """
    top_holdings: pd.DataFrame
    sector_allocation: pd.DataFrame
    style_exposure: pd.DataFrame
    concentration_ratio: float
    turnover_rate: float


class PortfolioAnalyzer:
    """投资组合分析器
    
    提供投资组合的深度分析功能，包括组合绩效评估、风险分析、持仓分析等。
    
    功能：
    - 组合绩效分析：收益率、夏普比率、最大回撤等
    - 风险分析：波动率、VaR、CVaR等
    - 持仓分析：行业配置、风格暴露、集中度等
    - 基准比较：与市场基准的相对表现分析
    
    Attributes:
        risk_free_rate: 无风险利率
        
    Example:
        >>> analyzer = PortfolioAnalyzer(risk_free_rate=0.03)
        >>> analyzer.load_portfolio_data(returns_series, values_series, holdings_df)
        >>> analyzer.load_benchmark_data(benchmark_returns, benchmark_values)
        >>> metrics = analyzer.calculate_portfolio_metrics()
        >>> print(f"夏普比率: {metrics.sharpe_ratio:.2f}")
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """初始化投资组合分析器
        
        Args:
            risk_free_rate: 无风险利率，默认为2%
            
        Note:
            无风险利率用于计算夏普比率等风险调整收益指标。
        """
        self.risk_free_rate = risk_free_rate
        self._portfolio_data = None
        self._benchmark_data = None
        
    def load_portfolio_data(
        self, 
        portfolio_returns: pd.Series,
        portfolio_values: Optional[pd.Series] = None,
        holdings: Optional[pd.DataFrame] = None
    ) -> None:
        """加载投资组合数据
        
        Args:
            portfolio_returns: 投资组合收益率序列
            portfolio_values: 投资组合净值序列（可选）
            holdings: 持仓数据，包含股票代码、权重、行业等信息
            
        Raises:
            ValueError: 如果收益率数据为空
            
        Example:
            >>> returns = pd.Series([0.01, -0.02, 0.03], index=pd.date_range('2023-01-01', periods=3))
            >>> values = pd.Series([1.0, 0.98, 1.01], index=returns.index)
            >>> holdings = pd.DataFrame({
            ...     'weight': [0.5, 0.3, 0.2],
            ...     'sector': ['tech', 'finance', 'health']
            ... }, index=['AAPL', 'JPM', 'JNJ'])
            >>> analyzer.load_portfolio_data(returns, values, holdings)
        """
        if portfolio_returns.empty:
            raise ValueError("收益率数据不能为空")
            
        self._portfolio_returns = portfolio_returns
        self._portfolio_values = portfolio_values
        self._holdings = holdings
        
        if portfolio_values is None:
            # 从收益率计算净值
            self._portfolio_values = (1 + portfolio_returns).cumprod()
            
    def load_benchmark_data(
        self, 
        benchmark_returns: pd.Series,
        benchmark_values: Optional[pd.Series] = None
    ) -> None:
        """加载基准数据
        
        Args:
            benchmark_returns: 基准收益率序列
            benchmark_values: 基准净值序列（可选）
            
        Raises:
            ValueError: 如果收益率数据为空
            
        Example:
            >>> benchmark_returns = pd.Series([0.005, -0.01, 0.02], index=pd.date_range('2023-01-01', periods=3))
            >>> benchmark_values = pd.Series([1.0, 0.995, 1.015], index=benchmark_returns.index)
            >>> analyzer.load_benchmark_data(benchmark_returns, benchmark_values)
        """
        if benchmark_returns.empty:
            raise ValueError("基准收益率数据不能为空")
            
        self._benchmark_returns = benchmark_returns
        self._benchmark_values = benchmark_values
        
        if benchmark_values is None:
            self._benchmark_values = (1 + benchmark_returns).cumprod()
    
    def calculate_portfolio_metrics(self) -> PortfolioMetrics:
        """计算投资组合核心指标
        
        Returns:
            PortfolioMetrics: 投资组合指标对象
            
        Raises:
            ValueError: 如果未加载投资组合数据
            
        Example:
            >>> metrics = analyzer.calculate_portfolio_metrics()
            >>> print(f"年化收益率: {metrics.annual_return:.2%}")
            >>> print(f"夏普比率: {metrics.sharpe_ratio:.2f}")
            >>> print(f"最大回撤: {metrics.max_drawdown:.2%}")
        """
        if self._portfolio_returns is None:
            raise ValueError("请先加载投资组合数据")
            
        returns = self._portfolio_returns
        values = self._portfolio_values
        
        # 基础指标
        total_return = values.iloc[-1] / values.iloc[0] - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (annual_return - self.risk_free_rate) / volatility
        
        # 最大回撤
        rolling_max = values.expanding().max()
        drawdowns = (values - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        calmar_ratio = (
            annual_return / abs(max_drawdown)
            if max_drawdown != 0 else 0
        )
        
        metrics = PortfolioMetrics(
            total_return=total_return,
            annual_return=annual_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar_ratio
        )
        
        # 如果有基准数据，计算相对指标
        if hasattr(self, '_benchmark_returns'):
            excess_returns = returns - self._benchmark_returns
            tracking_error = excess_returns.std() * np.sqrt(252)
            information_ratio = (
                excess_returns.mean() * np.sqrt(252) / tracking_error
            )
   
            # Alpha和Beta计算
            covariance = returns.cov(self._benchmark_returns)
            benchmark_variance = self._benchmark_returns.var()
            beta = (
                covariance / benchmark_variance
                if benchmark_variance != 0 else 0
            )
            alpha = (annual_return - self.risk_free_rate) - beta * (
                self._benchmark_returns.mean() * 252 - self.risk_free_rate
            )
   
            metrics.information_ratio = information_ratio
            metrics.alpha = alpha
            metrics.beta = beta
            metrics.tracking_error = tracking_error
   
        # 风险指标
        if len(returns) > 0:
            var_95 = returns.quantile(0.05)
            cvar_95 = returns[returns <= var_95].mean()
            metrics.var_95 = var_95
            metrics.cvar_95 = cvar_95
   
        return metrics
    
    def analyze_holdings(self) -> HoldingAnalysis:
        """分析持仓结构
        
        Returns:
            HoldingAnalysis: 持仓分析结果
            
        Raises:
            ValueError: 如果未加载持仓数据
            
        Example:
            >>> analysis = analyzer.analyze_holdings()
            >>> print(f"集中度比率: {analysis.concentration_ratio:.2%}")
            >>> print("行业配置:")
            >>> print(analysis.sector_allocation)
        """
        if self._holdings is None:
            raise ValueError("请先加载持仓数据")
            
        holdings = self._holdings.copy()
        
        # 前十大持仓
        top_holdings = holdings.nlargest(10, 'weight')
        
        # 行业配置
        if 'sector' in holdings.columns:
            sector_allocation = (
                holdings.groupby('sector')['weight']
                .sum().sort_values(ascending=False)
            )
        else:
            sector_allocation = pd.Series([], dtype=float)
   
        # 风格暴露（简化版）
        style_exposure = pd.DataFrame()
        if 'market_cap' in holdings.columns:
            style_exposure['size'] = holdings['market_cap'].mean()
   
        # 集中度指标
        concentration_ratio = holdings['weight'].nlargest(5).sum()
        
        # 换手率（需要历史持仓数据，这里简化处理）
        turnover_rate = 0.0  # 实际应用中需要计算
        
        return HoldingAnalysis(
            top_holdings=top_holdings,
            sector_allocation=sector_allocation,
            style_exposure=style_exposure,
            concentration_ratio=concentration_ratio,
            turnover_rate=turnover_rate
        )
    
    def performance_attribution(self, period: str = 'monthly') -> pd.DataFrame:
        """绩效归因分析
        
        Args:
            period: 归因周期，'daily', 'weekly', 'monthly'
            
        Returns:
            pd.DataFrame: 归因分析结果
            
        Raises:
            ValueError: 如果未加载基准数据
            
        Example:
            >>> attribution = analyzer.performance_attribution('monthly')
            >>> print("月度归因分析:")
            >>> print(attribution)
        """
        if not hasattr(self, '_benchmark_returns'):
            raise ValueError("绩效归因需要基准数据")
            
        # 简化版的Brinson归因模型
        portfolio_returns = self._portfolio_returns
        benchmark_returns = self._benchmark_returns
        
        # 计算超额收益
        excess_returns = portfolio_returns - benchmark_returns
        
        # 按周期重采样
        if period == 'monthly':
            freq = 'M'
        elif period == 'weekly':
            freq = 'W'
        else:
            freq = 'D'
   
        excess_returns_resampled = excess_returns.resample(freq).apply(
            lambda x: (1 + x).prod() - 1
        )
        
        attribution_df = pd.DataFrame({
            'excess_return': excess_returns_resampled,
            'cumulative_excess': (1 + excess_returns_resampled).cumprod() - 1
        })
        
        return attribution_df
    
    def risk_decomposition(self) -> Dict[str, float]:
        """风险分解分析
        
        Returns:
            Dict[str, float]: 风险分解结果
            
        Raises:
            ValueError: 如果未加载持仓数据
            
        Example:
            >>> decomp = analyzer.risk_decomposition()
            >>> print(f"总波动率: {decomp['total_volatility']:.2%}")
            >>> print(f"多元化收益: {decomp['diversification_benefit']:.2%}")
        """
        if self._holdings is None:
            raise ValueError("风险分解需要持仓数据")
            
        # 简化版风险分解
        holdings = self._holdings
        
        # 假设有协方差矩阵（实际应用中需要真实的协方差数据）
        # 这里使用等权重假设计算近似风险贡献
        n_assets = len(holdings)
        if n_assets > 0:
            avg_vol = (
                holdings['weight'].std()
                if 'weight' in holdings.columns else 0.1
            )
            total_risk = avg_vol * np.sqrt(252)
   
            # 计算边际风险贡献（简化）
            marginal_risk_contrib = holdings['weight'] * avg_vol / total_risk
   
            risk_decomp = {
                'total_volatility': total_risk,
                'diversification_benefit': (
                    1 - total_risk / (avg_vol * np.sqrt(252) * n_assets)
                ),
                'top_5_contributors': marginal_risk_contrib.nlargest(5).sum()
            }
        else:
            risk_decomp = {
                'total_volatility': 0,
                'diversification_benefit': 0,
                'top_5_contributors': 0
            }
   
        return risk_decomp
    
    def generate_analysis_report(self) -> Dict:
        """生成完整的投资组合分析报告
        
        Returns:
            Dict: 包含所有分析结果的字典
            
        Example:
            >>> report = analyzer.generate_analysis_report()
            >>> print("分析报告生成完成")
            >>> print(f"分析日期: {report['analysis_date']}")
        """
        metrics = self.calculate_portfolio_metrics()
        holdings_analysis = (
            self.analyze_holdings()
            if self._holdings is not None else None
        )
        risk_decomp = self.risk_decomposition()
        
        report = {
            'portfolio_metrics': metrics.__dict__,
            'risk_decomposition': risk_decomp,
            'has_benchmark': hasattr(self, '_benchmark_returns'),
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d')
        }
        
        if holdings_analysis is not None:
            report['holdings_analysis'] = {
                'top_holdings': (
                    holdings_analysis.top_holdings.to_dict('records')
                ),
                'sector_allocation': (
                    holdings_analysis.sector_allocation.to_dict()
                ),
                'concentration_ratio': holdings_analysis.concentration_ratio,
                'turnover_rate': holdings_analysis.turnover_rate
            }
   
        return report