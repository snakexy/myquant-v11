"""
投资组合优化器 - Portfolio Optimizer

提供现代投资组合理论优化功能，包括马科维茨优化、风险平价模型等。
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import warnings
from scipy.optimize import minimize


@dataclass
class OptimizationResult:
    """优化结果数据类
    
    存储投资组合优化的结果，包括最优权重、预期收益等。
    
    Attributes:
        optimal_weights: 最优权重
        expected_return: 预期收益率
        expected_volatility: 预期波动率
        sharpe_ratio: 夏普比率
        optimization_method: 优化方法
        constraints_satisfied: 约束是否满足
    """
    optimal_weights: pd.Series
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    optimization_method: str
    constraints_satisfied: bool


@dataclass
class EfficientFrontierPoint:
    """有效前沿点数据类
    
    存储有效前沿上的一个点，包括预期收益、波动率和权重。
    
    Attributes:
        expected_return: 预期收益率
        expected_volatility: 预期波动率
        weights: 权重
        sharpe_ratio: 夏普比率
    """
    expected_return: float
    expected_volatility: float
    weights: pd.Series
    sharpe_ratio: float


class PortfolioOptimizer:
    """投资组合优化器
    
    提供现代投资组合理论优化功能，包括马科维茨优化、风险平价模型等。
    
    功能：
    - 马科维茨均值-方差优化
    - 风险平价模型优化
    - 最小方差组合优化
    - 最大夏普比率组合优化
    - 有效前沿计算
    - 约束优化（权重约束、行业约束等）
    
    Attributes:
        risk_free_rate: 无风险利率
        
    Example:
        >>> optimizer = PortfolioOptimizer(risk_free_rate=0.03)
        >>> returns_df = pd.DataFrame({
        ...     'AAPL': [0.01, 0.02, 0.015],
        ...     'MSFT': [0.015, 0.01, 0.02],
        ...     'GOOGL': [0.02, 0.015, 0.01]
        ... })
        >>> optimizer.load_returns_data(returns_df)
        >>> result = optimizer.maximum_sharpe_optimization()
        >>> print(f"最优权重: {result.optimal_weights.to_dict()}")
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """初始化投资组合优化器
        
        Args:
            risk_free_rate: 无风险利率，默认为2%
            
        Note:
            无风险利率用于计算夏普比率等风险调整收益指标。
        """
        self.risk_free_rate = risk_free_rate
        self._returns = None
        self._cov_matrix = None
        self._expected_returns = None
        self._constraints = []
        self._bounds = None
        
    def load_returns_data(self, returns: pd.DataFrame) -> None:
        """加载收益率数据
        
        Args:
            returns: 资产收益率数据
            
        Raises:
            ValueError: 如果收益率数据为空
            
        Example:
            >>> returns = pd.DataFrame({
            ...     'AAPL': [0.01, 0.02, 0.015],
            ...     'MSFT': [0.015, 0.01, 0.02],
            ...     'GOOGL': [0.02, 0.015, 0.01]
            ... })
            >>> optimizer.load_returns_data(returns)
        """
        if returns.empty:
            raise ValueError("收益率数据不能为空")
            
        self._returns = returns
        self._expected_returns = returns.mean()
        self._cov_matrix = returns.cov()
        
    def load_covariance_matrix(self, cov_matrix: pd.DataFrame) -> None:
        """加载协方差矩阵
        
        Args:
            cov_matrix: 资产协方差矩阵
            
        Raises:
            ValueError: 如果协方差矩阵为空
            
        Example:
            >>> cov_matrix = pd.DataFrame({
            ...     'AAPL': [0.0001, 0.0002, 0.00015],
            ...     'MSFT': [0.0002, 0.0001, 0.0002],
            ...     'GOOGL': [0.00015, 0.0002, 0.0001]
            ... })
            >>> optimizer.load_covariance_matrix(cov_matrix)
        """
        if cov_matrix.empty:
            raise ValueError("协方差矩阵不能为空")
            
        self._cov_matrix = cov_matrix
        
    def set_expected_returns(self, expected_returns: pd.Series) -> None:
        """设置预期收益率
        
        Args:
            expected_returns: 预期收益率
            
        Raises:
            ValueError: 如果预期收益率为空
            
        Example:
            >>> expected_returns = pd.Series([0.015, 0.015, 0.015], 
            ...                           index=['AAPL', 'MSFT', 'GOOGL'])
            >>> optimizer.set_expected_returns(expected_returns)
        """
        if expected_returns.empty:
            raise ValueError("预期收益率不能为空")
            
        self._expected_returns = expected_returns
        
    def set_constraints(
        self,
        constraints: List[Dict],
        bounds: Optional[List[Tuple]] = None
    ) -> None:
        """设置优化约束
        
        Args:
            constraints: 优化约束列表
            bounds: 权重边界约束
            
        Example:
            >>> constraints = [
            ...     {'type': 'eq', 'fun': lambda w: sum(w) - 1}
            ... ]
            >>> bounds = [(0, 1), (0, 1), (0, 1)]
            >>> optimizer.set_constraints(constraints, bounds)
        """
        self._constraints = constraints
        self._bounds = bounds
        
    def mean_variance_optimization(
        self,
        target_return: Optional[float] = None,
        risk_aversion: float = 1.0
    ) -> OptimizationResult:
        """马科维茨均值-方差优化
        
        Args:
            target_return: 目标收益率（可选）
            risk_aversion: 风险厌恶系数
            
        Returns:
            OptimizationResult: 优化结果
            
        Raises:
            ValueError: 如果缺少必要数据
            
        Example:
            >>> result = optimizer.mean_variance_optimization(
            ...     target_return=0.15, risk_aversion=2.0
            ... )
            >>> print(f"预期收益率: {result.expected_return:.2%}")
            >>> print(f"预期波动率: {result.expected_volatility:.2%}")
        """
        if self._expected_returns is None or self._cov_matrix is None:
            raise ValueError("需要预期收益率和协方差矩阵数据")
            
        n_assets = len(self._expected_returns)
        
        # 初始权重（等权重）
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # 目标函数
        if target_return is not None:
            # 在目标收益率下最小化方差
            def objective(weights):
                portfolio_variance = (
                    weights.T @ self._cov_matrix @ weights
                )
                return portfolio_variance
                
            # 添加收益率约束
            return_constraint = {
                'type': 'eq',
                'fun': lambda w: w @ self._expected_returns - target_return
            }
            constraints = self._constraints + [return_constraint]
            
        else:
            # 效用函数最大化
            def objective(weights):
                portfolio_return = weights @ self._expected_returns
                portfolio_variance = (
                    weights.T @ self._cov_matrix @ weights
                )
                utility = (
                    portfolio_return - 0.5 * risk_aversion * portfolio_variance
                )
                return -utility  # 最小化负效用
                
            constraints = self._constraints
            
        # 权重和为1的约束
        weight_sum_constraint = {
            'type': 'eq',
            'fun': lambda w: np.sum(w) - 1
        }
        constraints = constraints + [weight_sum_constraint]
        
        # 默认边界（0到1）
        if self._bounds is None:
            bounds = [(0, 1) for _ in range(n_assets)]
        else:
            bounds = self._bounds
            
        # 优化
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            warnings.warn(f"优化失败: {result.message}")
            
        optimal_weights = pd.Series(
            result.x, index=self._expected_returns.index
        )
        expected_return = optimal_weights @ self._expected_returns
        expected_volatility = np.sqrt(
            optimal_weights.T @ self._cov_matrix @ optimal_weights
        )
        sharpe_ratio = (
            (expected_return - self.risk_free_rate) / expected_volatility
            if expected_volatility != 0 else 0
        )
        
        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            sharpe_ratio=sharpe_ratio,
            optimization_method='mean_variance',
            constraints_satisfied=result.success
        )
    
    def risk_parity_optimization(
        self,
        target_risk_contributions: Optional[Dict] = None
    ) -> OptimizationResult:
        """风险平价优化
        
        Args:
            target_risk_contributions: 目标风险贡献（可选）
            
        Returns:
            OptimizationResult: 优化结果
            
        Raises:
            ValueError: 如果缺少必要数据
            
        Example:
            >>> result = optimizer.risk_parity_optimization()
            >>> print(f"预期收益率: {result.expected_return:.2%}")
            >>> print(f"预期波动率: {result.expected_volatility:.2%}")
        """
        if self._cov_matrix is None:
            raise ValueError("需要协方差矩阵数据")
            
        n_assets = len(self._cov_matrix)
        
        # 初始权重（等权重）
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # 如果没有目标风险贡献，使用等风险贡献
        if target_risk_contributions is None:
            target_risk_contributions = {
                asset: 1.0 / n_assets for asset in self._cov_matrix.index
            }
            
        # 目标函数：最小化风险贡献偏差
        def objective(weights):
            portfolio_variance = weights.T @ self._cov_matrix @ weights
            marginal_risk_contrib = (
                weights * (self._cov_matrix @ weights) / portfolio_variance
            )
   
            # 计算风险贡献偏差
            risk_contrib_deviation = 0
            for i, asset in enumerate(self._cov_matrix.index):
                actual_contrib = marginal_risk_contrib[i]
                target_contrib = target_risk_contributions.get(asset, 0)
                deviation = actual_contrib - target_contrib
                risk_contrib_deviation += deviation ** 2
                
            return risk_contrib_deviation
            
        # 约束
        weight_sum_constraint = {
            'type': 'eq',
            'fun': lambda w: np.sum(w) - 1
        }
        constraints = self._constraints + [weight_sum_constraint]
        
        # 边界
        if self._bounds is None:
            bounds = [(0, 1) for _ in range(n_assets)]
        else:
            bounds = self._bounds
            
        # 优化
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            warnings.warn(f"风险平价优化失败: {result.message}")
            
        optimal_weights = pd.Series(result.x, index=self._cov_matrix.index)
        
        # 计算预期指标
        expected_return = (
            optimal_weights @ self._expected_returns
            if self._expected_returns is not None else 0
        )
        expected_volatility = np.sqrt(
            optimal_weights.T @ self._cov_matrix @ optimal_weights
        )
        sharpe_ratio = (
            (expected_return - self.risk_free_rate) / expected_volatility
            if expected_volatility != 0 else 0
        )
        
        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            sharpe_ratio=sharpe_ratio,
            optimization_method='risk_parity',
            constraints_satisfied=result.success
        )
    
    def minimum_variance_optimization(self) -> OptimizationResult:
        """最小方差组合优化
        
        Returns:
            OptimizationResult: 优化结果
            
        Raises:
            ValueError: 如果缺少必要数据
            
        Example:
            >>> result = optimizer.minimum_variance_optimization()
            >>> print(f"预期收益率: {result.expected_return:.2%}")
            >>> print(f"预期波动率: {result.expected_volatility:.2%}")
        """
        if self._cov_matrix is None:
            raise ValueError("需要协方差矩阵数据")
            
        n_assets = len(self._cov_matrix)
        
        # 目标函数：最小化方差
        def objective(weights):
            return weights.T @ self._cov_matrix @ weights
            
        # 约束
        weight_sum_constraint = {
            'type': 'eq',
            'fun': lambda w: np.sum(w) - 1
        }
        constraints = self._constraints + [weight_sum_constraint]
        
        # 边界
        if self._bounds is None:
            bounds = [(0, 1) for _ in range(n_assets)]
        else:
            bounds = self._bounds
            
        # 初始权重
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # 优化
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            warnings.warn(f"最小方差优化失败: {result.message}")
            
        optimal_weights = pd.Series(result.x, index=self._cov_matrix.index)
        
        # 计算预期指标
        expected_return = (
            optimal_weights @ self._expected_returns
            if self._expected_returns is not None else 0
        )
        expected_volatility = np.sqrt(result.fun)
        sharpe_ratio = (
            (expected_return - self.risk_free_rate) / expected_volatility
            if expected_volatility != 0 else 0
        )
        
        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            sharpe_ratio=sharpe_ratio,
            optimization_method='minimum_variance',
            constraints_satisfied=result.success
        )
    
    def maximum_sharpe_optimization(self) -> OptimizationResult:
        """最大夏普比率组合优化
        
        Returns:
            OptimizationResult: 优化结果
            
        Raises:
            ValueError: 如果缺少必要数据
            
        Example:
            >>> result = optimizer.maximum_sharpe_optimization()
            >>> print(f"夏普比率: {result.sharpe_ratio:.2f}")
            >>> print(f"预期收益率: {result.expected_return:.2%}")
        """
        if self._expected_returns is None or self._cov_matrix is None:
            raise ValueError("需要预期收益率和协方差矩阵数据")
            
        n_assets = len(self._expected_returns)
        
        # 目标函数：最大化夏普比率（通过最小化负夏普比率）
        def objective(weights):
            portfolio_return = weights @ self._expected_returns
            portfolio_variance = weights.T @ self._cov_matrix @ weights
            portfolio_volatility = np.sqrt(portfolio_variance)
   
            if portfolio_volatility == 0:
                return 1e10  # 很大的数
                
            sharpe_ratio = (
                portfolio_return - self.risk_free_rate
            ) / portfolio_volatility
                
            return -sharpe_ratio  # 最小化负夏普比率
            
        # 约束
        weight_sum_constraint = {
            'type': 'eq',
            'fun': lambda w: np.sum(w) - 1
        }
        constraints = self._constraints + [weight_sum_constraint]
        
        # 边界
        if self._bounds is None:
            bounds = [(0, 1) for _ in range(n_assets)]
        else:
            bounds = self._bounds
            
        # 初始权重
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # 优化
        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            warnings.warn(f"最大夏普优化失败: {result.message}")
            
        optimal_weights = pd.Series(
            result.x, index=self._expected_returns.index
        )
        expected_return = optimal_weights @ self._expected_returns
        expected_volatility = np.sqrt(
            optimal_weights.T @ self._cov_matrix @ optimal_weights
        )
        sharpe_ratio = -result.fun  # 恢复为正的夏普比率
        
        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            sharpe_ratio=sharpe_ratio,
            optimization_method='maximum_sharpe',
            constraints_satisfied=result.success
        )
    
    def calculate_efficient_frontier(
        self,
        num_points: int = 50
    ) -> pd.DataFrame:
        """计算有效前沿
        
        Args:
            num_points: 前沿点数
            
        Returns:
            pd.DataFrame: 有效前沿数据
            
        Raises:
            ValueError: 如果缺少必要数据
            
        Example:
            >>> frontier = optimizer.calculate_efficient_frontier(num_points=20)
            >>> print("有效前沿计算完成")
            >>> print(frontier.head())
        """
        if self._expected_returns is None or self._cov_matrix is None:
            raise ValueError("需要预期收益率和协方差矩阵数据")
            
        # 计算最小方差组合和最大收益率组合
        min_var_result = self.minimum_variance_optimization()
        max_return = self._expected_returns.max()
        
        # 生成目标收益率范围
        target_returns = np.linspace(
            min_var_result.expected_return,
            max_return,
            num_points
        )
        
        frontier_points = []
        
        for target_return in target_returns:
            try:
                result = self.mean_variance_optimization(
                    target_return=target_return
                )
                
                if result.constraints_satisfied:
                    frontier_points.append({
                        'expected_return': result.expected_return,
                        'expected_volatility': result.expected_volatility,
                        'sharpe_ratio': result.sharpe_ratio,
                        'weights': result.optimal_weights
                    })
                    
            except Exception as e:
                warnings.warn(f"计算有效前沿点时出错: {e}")
                continue
                
        return pd.DataFrame(frontier_points)
    
    def black_litterman_optimization(
        self,
        prior_weights: pd.Series,
        views: Dict[str, float],
        view_confidences: Dict[str, float],
        tau: float = 0.05
    ) -> OptimizationResult:
        """Black-Litterman模型优化
        
        Args:
            prior_weights: 先验权重
            views: 观点字典，{资产: 预期超额收益}
            view_confidences: 观点置信度
            tau: 不确定性参数
            
        Returns:
            OptimizationResult: 优化结果
            
        Raises:
            ValueError: 如果缺少必要数据
            
        Example:
            >>> prior = pd.Series([0.4, 0.3, 0.3], 
            ...                    index=['AAPL', 'MSFT', 'GOOGL'])
            >>> views = {'AAPL': 0.02, 'MSFT': -0.01}
            >>> confidences = {'AAPL': 0.7, 'MSFT': 0.8}
            >>> result = optimizer.black_litterman_optimization(
            ...     prior, views, confidences
            ... )
            >>> print(f"优化权重: {result.optimal_weights.to_dict()}")
        """
        if self._cov_matrix is None:
            raise ValueError("需要协方差矩阵数据")
            
        # 计算隐含均衡收益率
        risk_aversion = 1.0  # 简化处理
        implied_returns = risk_aversion * self._cov_matrix @ prior_weights
        
        # 构建观点矩阵
        assets = self._cov_matrix.index
        n_assets = len(assets)
        n_views = len(views)
        
        P = np.zeros((n_views, n_assets))  # 观点矩阵
        Q = np.zeros(n_views)  # 观点向量
        Omega = np.zeros((n_views, n_views))  # 观点不确定性
        
        for i, (asset, view_return) in enumerate(views.items()):
            asset_idx = assets.get_loc(asset)
            P[i, asset_idx] = 1
            Q[i] = view_return
            Omega[i, i] = view_confidences.get(asset, 1.0)
            
        # Black-Litterman公式
        tau_sigma = tau * self._cov_matrix
        M = np.linalg.inv(
            np.linalg.inv(tau_sigma) + P.T @ np.linalg.inv(Omega) @ P
        )
        posterior_returns = M @ (
            np.linalg.inv(tau_sigma) @ implied_returns + 
            P.T @ np.linalg.inv(Omega) @ Q
        )
        
        # 使用后验收益率进行均值-方差优化
        self._expected_returns = pd.Series(posterior_returns, index=assets)
        result = self.mean_variance_optimization()
        
        return OptimizationResult(
            optimal_weights=result.optimal_weights,
            expected_return=result.expected_return,
            expected_volatility=result.expected_volatility,
            sharpe_ratio=result.sharpe_ratio,
            optimization_method='black_litterman',
            constraints_satisfied=result.constraints_satisfied
        )
    
    def hierarchical_risk_parity(
        self,
        linkage_method: str = 'ward'
    ) -> OptimizationResult:
        """分层风险平价优化
        
        Args:
            linkage_method: 聚类方法
            
        Returns:
            OptimizationResult: 优化结果
            
        Raises:
            ValueError: 如果缺少必要数据
            
        Example:
            >>> result = optimizer.hierarchical_risk_parity('ward')
            >>> print(f"预期收益率: {result.expected_return:.2%}")
            >>> print(f"预期波动率: {result.expected_volatility:.2%}")
        """
        if self._cov_matrix is None:
            raise ValueError("需要协方差矩阵数据")
            
        try:
            from scipy.cluster.hierarchy import linkage
            from scipy.spatial.distance import squareform
            
            # 计算相关性矩阵
            corr_matrix = self._calculate_correlation_matrix()
            
            # 计算距离矩阵
            distance_matrix = np.sqrt(0.5 * (1 - corr_matrix))
            
            # 层次聚类
            linkage_matrix = linkage(
                squareform(distance_matrix), method=linkage_method
            )
            
            # 简化的HRP权重计算
            weights = self._hrp_weights(linkage_matrix, distance_matrix)
            
        except ImportError:
            warnings.warn("scipy不可用，使用简化版风险平价")
            return self.risk_parity_optimization()
            
        optimal_weights = pd.Series(weights, index=self._cov_matrix.index)
        
        # 计算预期指标
        expected_return = (
            optimal_weights @ self._expected_returns
            if self._expected_returns is not None else 0
        )
        expected_volatility = np.sqrt(
            optimal_weights.T @ self._cov_matrix @ optimal_weights
        )
        sharpe_ratio = (
            (expected_return - self.risk_free_rate) / expected_volatility
            if expected_volatility != 0 else 0
        )
        
        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            sharpe_ratio=sharpe_ratio,
            optimization_method='hierarchical_risk_parity',
            constraints_satisfied=True
        )
    
    def _calculate_correlation_matrix(self) -> pd.DataFrame:
        """计算相关性矩阵"""
        if self._returns is not None:
            return self._returns.corr()
        else:
            # 从协方差矩阵推导相关性矩阵
            std_dev = np.sqrt(np.diag(self._cov_matrix))
            corr_matrix = self._cov_matrix / np.outer(std_dev, std_dev)
            return pd.DataFrame(
                corr_matrix,
                index=self._cov_matrix.index,
                columns=self._cov_matrix.columns
            )
    
    def _hrp_weights(self, linkage_matrix, distance_matrix) -> np.ndarray:
        """计算HRP权重（简化版）"""
        # n_assets 用于未来扩展
        _ = len(self._cov_matrix)
        
        # 简化的HRP实现
        # 实际HRP实现更复杂，这里使用逆方差加权作为近似
        variances = np.diag(self._cov_matrix)
        weights = 1 / variances
        weights = weights / np.sum(weights)
        
        return weights
    
    def generate_optimization_report(
        self,
        methods: List[str] = None
    ) -> Dict:
        """生成优化分析报告
        
        Args:
            methods: 优化方法列表
            
        Returns:
            Dict: 优化分析报告
            
        Example:
            >>> report = optimizer.generate_optimization_report(
            ...     ['mean_variance', 'risk_parity', 'maximum_sharpe']
            ... )
            >>> print("优化报告生成完成")
            >>> print(f"分析日期: {report['analysis_date']}")
        """
        if methods is None:
            methods = [
                'mean_variance', 'risk_parity', 'minimum_variance',
                'maximum_sharpe'
            ]
            
        report = {
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
            'risk_free_rate': self.risk_free_rate,
            'data_availability': self._check_data_availability()
        }
        
        optimization_results = {}
        
        for method in methods:
            try:
                if method == 'mean_variance':
                    result = self.mean_variance_optimization()
                elif method == 'risk_parity':
                    result = self.risk_parity_optimization()
                elif method == 'minimum_variance':
                    result = self.minimum_variance_optimization()
                elif method == 'maximum_sharpe':
                    result = self.maximum_sharpe_optimization()
                else:
                    continue
                    
                optimization_results[method] = {
                    'optimal_weights': result.optimal_weights.to_dict(),
                    'expected_return': result.expected_return,
                    'expected_volatility': result.expected_volatility,
                    'sharpe_ratio': result.sharpe_ratio,
                    'constraints_satisfied': result.constraints_satisfied
                }
                    
            except Exception as e:
                optimization_results[method] = {'error': str(e)}
                
        report['optimization_results'] = optimization_results
        
        # 有效前沿分析
        try:
            frontier_data = self.calculate_efficient_frontier()
            report['efficient_frontier'] = {
                'num_points': len(frontier_data),
                'min_volatility': frontier_data['expected_volatility'].min(),
                'max_return': frontier_data['expected_return'].max(),
                'max_sharpe': frontier_data['sharpe_ratio'].max()
            }
        except Exception as e:
            report['efficient_frontier'] = {'error': str(e)}
            
        return report
    
    def _check_data_availability(self) -> Dict[str, bool]:
        """检查数据可用性
        
        Returns:
            Dict[str, bool]: 数据可用性状态
        """
        return {
            'returns_data': self._returns is not None,
            'cov_matrix': self._cov_matrix is not None,
            'expected_returns': self._expected_returns is not None,
            'constraints': len(self._constraints) > 0,
            'bounds': self._bounds is not None
        }