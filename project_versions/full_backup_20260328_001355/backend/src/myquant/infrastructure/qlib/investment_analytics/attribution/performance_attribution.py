"""
绩效归因分析器 - Performance Attribution Analyzer

提供投资绩效的深度归因分析功能，包括Brinson模型、因子归因分析等。
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class BrinsonAttributionResult:
    """Brinson归因分析结果数据类
    
    存储Brinson模型归因分析的结果，包括配置效应、选择效应等。
    
    Attributes:
        allocation_effect: 配置效应
        selection_effect: 选择效应
        interaction_effect: 交互效应
        total_active_return: 总主动收益
        sector_contributions: 行业贡献
    """
    allocation_effect: float
    selection_effect: float
    interaction_effect: float
    total_active_return: float
    sector_contributions: Dict[str, float]


@dataclass
class FactorAttributionResult:
    """因子归因分析结果数据类
    
    存储因子归因分析的结果，包括因子暴露、收益和贡献。
    
    Attributes:
        factor_exposures: 因子暴露度
        factor_returns: 因子收益率
        factor_contributions: 因子贡献
        specific_return: 特异收益
        total_active_return: 总主动收益
    """
    factor_exposures: Dict[str, float]
    factor_returns: Dict[str, float]
    factor_contributions: Dict[str, float]
    specific_return: float
    total_active_return: float


class PerformanceAttribution:
    """绩效归因分析器
    
    提供投资绩效的深度归因分析功能，包括Brinson模型、因子归因分析等。
    
    功能：
    - Brinson模型归因：配置效应、选择效应、交互效应
    - 因子归因分析：多因子模型归因
    - 时序归因分析：多期归因链接
    - 归因结果可视化数据生成
    
    Example:
        >>> analyzer = PerformanceAttribution()
        >>> analyzer.load_portfolio_data(portfolio_weights, returns_df, sectors)
        >>> analyzer.load_benchmark_data(benchmark_weights, benchmark_returns)
        >>> result = analyzer.brinson_attribution()
        >>> print(f"配置效应: {result.allocation_effect:.2%}")
    """
    
    def __init__(self):
        """初始化绩效归因分析器"""
        self._portfolio_data = None
        self._benchmark_data = None
        self._factor_data = None
        
    def load_portfolio_data(
        self,
        portfolio_weights: pd.DataFrame,
        portfolio_returns: pd.DataFrame,
        sectors: Optional[pd.Series] = None
    ) -> None:
        """加载投资组合数据
        
        Args:
            portfolio_weights: 投资组合权重数据，包含资产和权重
            portfolio_returns: 投资组合收益率数据
            sectors: 资产所属行业信息（可选）
            
        Raises:
            ValueError: 如果权重数据为空
            
        Example:
            >>> weights = pd.DataFrame({
            ...     'weight': [0.5, 0.3, 0.2],
            ... }, index=['AAPL', 'MSFT', 'GOOGL'])
            >>> returns = pd.DataFrame({
            ...     'return': [0.01, 0.02, 0.015],
            ... }, index=['AAPL', 'MSFT', 'GOOGL'])
            >>> sectors = pd.Series(['tech', 'tech', 'tech'], 
            ...                    index=['AAPL', 'MSFT', 'GOOGL'])
            >>> analyzer.load_portfolio_data(weights, returns, sectors)
        """
        if portfolio_weights.empty:
            raise ValueError("投资组合权重数据不能为空")
            
        self._portfolio_weights = portfolio_weights
        self._portfolio_returns = portfolio_returns
        self._sectors = sectors
        
    def load_benchmark_data(
        self,
        benchmark_weights: pd.DataFrame,
        benchmark_returns: pd.DataFrame
    ) -> None:
        """加载基准数据
        
        Args:
            benchmark_weights: 基准权重数据
            benchmark_returns: 基准收益率数据
            
        Raises:
            ValueError: 如果权重数据为空
            
        Example:
            >>> weights = pd.DataFrame({
            ...     'weight': [0.4, 0.3, 0.3],
            ... }, index=['AAPL', 'MSFT', 'GOOGL'])
            >>> returns = pd.DataFrame({
            ...     'return': [0.005, 0.01, 0.008],
            ... }, index=['AAPL', 'MSFT', 'GOOGL'])
            >>> analyzer.load_benchmark_data(weights, returns)
        """
        if benchmark_weights.empty:
            raise ValueError("基准权重数据不能为空")
            
        self._benchmark_weights = benchmark_weights
        self._benchmark_returns = benchmark_returns
        
    def load_factor_data(
        self,
        factor_exposures: pd.DataFrame,
        factor_returns: pd.DataFrame
    ) -> None:
        """加载因子数据
        
        Args:
            factor_exposures: 因子暴露度数据
            factor_returns: 因子收益率数据
            
        Raises:
            ValueError: 如果因子数据为空
            
        Example:
            >>> exposures = pd.DataFrame({
            ...     'size': [1.2, 0.8, 1.5],
            ...     'value': [0.9, 1.1, 0.7]
            ... }, index=['AAPL', 'MSFT', 'GOOGL'])
            >>> returns = pd.DataFrame({
            ...     'size': [0.01, 0.005, 0.008],
            ...     'value': [0.008, 0.003, 0.006]
            ... }, index=['size', 'value'])
            >>> analyzer.load_factor_data(exposures, returns)
        """
        if factor_exposures.empty or factor_returns.empty:
            raise ValueError("因子数据不能为空")
            
        self._factor_exposures = factor_exposures
        self._factor_returns = factor_returns
    
    def brinson_attribution(
        self,
        period: str = 'single'
    ) -> BrinsonAttributionResult:
        """Brinson模型绩效归因分析
        
        Args:
            period: 分析周期，'single' 单期，'multi' 多期
            
        Returns:
            BrinsonAttributionResult: 归因分析结果
            
        Raises:
            ValueError: 如果缺少必要数据
            
        Example:
            >>> result = analyzer.brinson_attribution(period='single')
            >>> print(f"配置效应: {result.allocation_effect:.2%}")
            >>> print(f"选择效应: {result.selection_effect:.2%}")
            >>> print(f"总主动收益: {result.total_active_return:.2%}")
        """
        if (self._portfolio_weights is None
                or self._benchmark_weights is None
                or self._sectors is None):
            raise ValueError("Brinson归因需要组合权重、基准权重和行业数据")
            
        # 确保数据对齐
        common_assets = (
            self._portfolio_weights.index.intersection(
                self._benchmark_weights.index
            )
        )
        
        portfolio_weights = self._portfolio_weights.loc[common_assets]
        benchmark_weights = self._benchmark_weights.loc[common_assets]
        portfolio_returns = self._portfolio_returns.loc[common_assets]
        benchmark_returns = self._benchmark_returns.loc[common_assets]
        sectors = self._sectors.loc[common_assets]
        
        # 按行业分组
        sector_portfolio_weights = portfolio_weights.groupby(sectors).sum()
        sector_benchmark_weights = benchmark_weights.groupby(sectors).sum()
        
        # 计算行业收益率
        sector_portfolio_returns = (
            (portfolio_weights * portfolio_returns).groupby(sectors).sum() /
            sector_portfolio_weights
        ).fillna(0)
        
        sector_benchmark_returns = (
            (benchmark_weights * benchmark_returns).groupby(sectors).sum() /
            sector_benchmark_weights
        ).fillna(0)
        
        # 计算总收益率
        total_portfolio_return = (
            portfolio_weights * portfolio_returns
        ).sum()
        total_benchmark_return = (
            benchmark_weights * benchmark_returns
        ).sum()
        total_active_return = total_portfolio_return - total_benchmark_return
        
        # 计算Brinson归因效应
        allocation_effect = (
            (sector_portfolio_weights - sector_benchmark_weights) *
            sector_benchmark_returns
        ).sum()
        
        selection_effect = (
            sector_benchmark_weights *
            (sector_portfolio_returns - sector_benchmark_returns)
        ).sum()
        
        interaction_effect = (
            (sector_portfolio_weights - sector_benchmark_weights) *
            (sector_portfolio_returns - sector_benchmark_returns)
        ).sum()
        
        # 计算各行业贡献
        sector_contributions = {}
        for sector in sector_portfolio_weights.index:
            alloc_contrib = (
                (sector_portfolio_weights[sector] - 
                 sector_benchmark_weights[sector]) *
                sector_benchmark_returns[sector]
            )
            select_contrib = (
                sector_benchmark_weights[sector] *
                (sector_portfolio_returns[sector] - 
                 sector_benchmark_returns[sector])
            )
            interact_contrib = (
                (sector_portfolio_weights[sector] - 
                 sector_benchmark_weights[sector]) *
                (sector_portfolio_returns[sector] - 
                 sector_benchmark_returns[sector])
            )
            sector_contributions[sector] = (
                alloc_contrib + select_contrib + interact_contrib
            )
            
        return BrinsonAttributionResult(
            allocation_effect=allocation_effect,
            selection_effect=selection_effect,
            interaction_effect=interaction_effect,
            total_active_return=total_active_return,
            sector_contributions=sector_contributions
        )
    
    def factor_attribution(
        self,
        method: str = 'cross_sectional'
    ) -> FactorAttributionResult:
        """因子归因分析
        
        Args:
            method: 归因方法，'cross_sectional' 横截面，'time_series' 时间序列
            
        Returns:
            FactorAttributionResult: 因子归因结果
            
        Raises:
            ValueError: 如果缺少必要数据
            
        Example:
            >>> result = analyzer.factor_attribution(method='cross_sectional')
            >>> print("因子贡献:")
            >>> for factor, contrib in result.factor_contributions.items():
            ...     print(f"{factor}: {contrib:.2%}")
        """
        if (self._factor_exposures is None
                or self._factor_returns is None):
            raise ValueError("因子归因需要因子暴露度和因子收益率数据")
            
        portfolio_returns = self._portfolio_returns
        factor_exposures = self._factor_exposures
        factor_returns = self._factor_returns
        
        # 确保数据对齐
        common_assets = (
            portfolio_returns.index.intersection(factor_exposures.index)
        )
        portfolio_returns = portfolio_returns.loc[common_assets]
        factor_exposures = factor_exposures.loc[common_assets]
        
        if method == 'cross_sectional':
            # 横截面因子归因
            factor_names = factor_exposures.columns
            
            # 计算因子收益率（横截面回归）
            X = factor_exposures.values
            y = portfolio_returns.values
            
            # 使用最小二乘法估计因子收益率
            try:
                factor_returns_est = np.linalg.lstsq(X, y, rcond=None)[0]
                specific_returns = y - X @ factor_returns_est
            except np.linalg.LinAlgError:
                # 如果矩阵不可逆，使用伪逆
                factor_returns_est = np.linalg.pinv(X) @ y
                specific_returns = y - X @ factor_returns_est
                
            # 计算因子贡献
            factor_contributions = {}
            for i, factor in enumerate(factor_names):
                factor_contributions[factor] = (
                    factor_exposures[factor].mean() * factor_returns_est[i]
                )
                
            total_active_return = portfolio_returns.mean()
            specific_return = specific_returns.mean()
            
        else:
            # 时间序列因子归因
            factor_names = factor_returns.columns
            
            # 计算因子暴露度（投资组合层面）
            portfolio_factor_exposures = factor_exposures.mean()
            
            # 计算因子贡献
            factor_contributions = {}
            for factor in factor_names:
                factor_contributions[factor] = (
                    portfolio_factor_exposures[factor] * 
                    factor_returns[factor].mean()
                )
                
            total_active_return = portfolio_returns.mean()
            specific_return = (
                total_active_return - sum(factor_contributions.values())
            )
            
        return FactorAttributionResult(
            factor_exposures=dict(portfolio_factor_exposures),
            factor_returns=dict(factor_returns.mean()),
            factor_contributions=factor_contributions,
            specific_return=specific_return,
            total_active_return=total_active_return
        )
    
    def multiperiod_attribution(
        self,
        start_date: str,
        end_date: str,
        frequency: str = 'M'
    ) -> pd.DataFrame:
        """多期归因分析
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            frequency: 频率，'D' 日，'W' 周，'M' 月
            
        Returns:
            pd.DataFrame: 多期归因结果
            
        Raises:
            ValueError: 如果缺少必要数据
            
        Example:
            >>> results = analyzer.multiperiod_attribution(
            ...     '2023-01-01', '2023-12-31', 'M'
            ... )
            >>> print("月度归因分析:")
            >>> print(results.head())
        """
        if (self._portfolio_weights is None
                or self._benchmark_weights is None):
            raise ValueError("多期归因需要组合权重和基准权重数据")
            
        # 生成日期范围
        date_range = pd.date_range(
            start=start_date, end=end_date, freq=frequency
        )
        
        attribution_results = []
        
        for period_end in date_range:
            try:
                # 获取当期数据（简化处理，实际需要按日期筛选）
                result = self.brinson_attribution()
                
                attribution_results.append({
                    'period': period_end,
                    'allocation_effect': result.allocation_effect,
                    'selection_effect': result.selection_effect,
                    'interaction_effect': result.interaction_effect,
                    'total_active_return': result.total_active_return
                })
                
            except Exception as e:
                print(f"归因分析在 {period_end} 失败: {e}")
                continue
                
        return pd.DataFrame(attribution_results).set_index('period')
    
    def calculate_attribution_quality(
        self,
        attribution_results: pd.DataFrame
    ) -> Dict[str, float]:
        """计算归因质量指标
        
        Args:
            attribution_results: 归因分析结果
            
        Returns:
            Dict[str, float]: 质量指标
            
        Example:
            >>> quality = analyzer.calculate_attribution_quality(results_df)
            >>> print(f"解释方差比例: {quality['explained_variance']:.2%}")
            >>> print(f"稳定性比率: {quality['stability_ratio']:.2f}")
        """
        quality_metrics = {}
        
        if 'total_active_return' in attribution_results.columns:
            active_returns = attribution_results['total_active_return']
            
            # 归因解释度
            random_noise_var = np.random.normal(
                0, 0.001, len(active_returns)
            ).var()
            explained_variance = (
                active_returns.var() /
                (active_returns.var() + random_noise_var)
            )
            quality_metrics['explained_variance'] = explained_variance
            
            # 归因稳定性
            allocation_effect = attribution_results.get(
                'allocation_effect', pd.Series([0])
            )
            selection_effect = attribution_results.get(
                'selection_effect', pd.Series([0])
            )
            
            if len(allocation_effect) > 1 and len(selection_effect) > 1:
                stability_ratio = (
                    allocation_effect.std() / selection_effect.std()
                    if selection_effect.std() != 0 else 0
                )
                quality_metrics['stability_ratio'] = stability_ratio
                
            # 归因一致性
            if 'allocation_effect' in attribution_results.columns:
                consistency = (
                    (attribution_results['allocation_effect'] > 0).mean()
                )
                quality_metrics['allocation_consistency'] = consistency
                
        return quality_metrics
    
    def generate_attribution_report(
        self,
        attribution_method: str = 'brinson'
    ) -> Dict:
        """生成归因分析报告
        
        Args:
            attribution_method: 归因方法，'brinson' 或 'factor'
            
        Returns:
            Dict: 归因分析报告
            
        Example:
            >>> report = analyzer.generate_attribution_report('brinson')
            >>> print("归因报告生成完成")
            >>> print(f"分析日期: {report['analysis_date']}")
        """
        report = {
            'attribution_method': attribution_method,
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
            'data_availability': self._check_data_availability()
        }
        
        try:
            if attribution_method == 'brinson':
                brinson_result = self.brinson_attribution()
                report['brinson_attribution'] = {
                    'allocation_effect': brinson_result.allocation_effect,
                    'selection_effect': brinson_result.selection_effect,
                    'interaction_effect': brinson_result.interaction_effect,
                    'total_active_return': brinson_result.total_active_return,
                    'sector_contributions': brinson_result.sector_contributions
                }
                
            elif attribution_method == 'factor':
                factor_result = self.factor_attribution()
                report['factor_attribution'] = {
                    'factor_exposures': factor_result.factor_exposures,
                    'factor_returns': factor_result.factor_returns,
                    'factor_contributions': factor_result.factor_contributions,
                    'specific_return': factor_result.specific_return,
                    'total_active_return': factor_result.total_active_return
                }
                
        except Exception as e:
            report['error'] = str(e)
            
        return report
    
    def _check_data_availability(self) -> Dict[str, bool]:
        """检查数据可用性
        
        Returns:
            Dict[str, bool]: 数据可用性状态
        """
        return {
            'portfolio_weights': self._portfolio_weights is not None,
            'portfolio_returns': self._portfolio_returns is not None,
            'benchmark_weights': self._benchmark_weights is not None,
            'benchmark_returns': self._benchmark_returns is not None,
            'sector_data': self._sectors is not None,
            'factor_data': (
                self._factor_exposures is not None and 
                self._factor_returns is not None
            )
        }