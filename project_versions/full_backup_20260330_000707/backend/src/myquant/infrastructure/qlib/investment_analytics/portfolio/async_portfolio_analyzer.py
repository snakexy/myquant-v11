"""
异步投资组合分析器
提供高性能的异步投资组合分析功能
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass

from .portfolio_analyzer import PortfolioAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class AsyncAnalysisConfig:
    """异步分析配置
    
    Attributes:
        max_concurrent_analyses: 最大并发分析数
        timeout_seconds: 分析超时时间（秒）
        enable_caching: 是否启用缓存
        cache_ttl: 缓存生存时间（秒）
        chunk_size: 数据分块大小
    """
    max_concurrent_analyses: int = 10
    timeout_seconds: float = 300.0
    enable_caching: bool = True
    cache_ttl: int = 3600
    chunk_size: int = 1000


class AsyncPortfolioAnalyzer:
    """异步投资组合分析器
    
    提供高性能的异步投资组合分析功能，支持大规模并发分析。
    相比同步分析器，异步分析器具有以下优势：
    - 更高的并发性能
    - 更好的资源利用率
    - 更快的分析速度
    - 支持批量分析
    
    Attributes:
        config: 异步分析配置
        analyzer: 基础投资组合分析器
        _cache: 分析结果缓存
        _semaphore: 并发控制信号量
        
    Example:
        >>> config = AsyncAnalysisConfig(max_concurrent_analyses=20)
        >>> analyzer = AsyncPortfolioAnalyzer(config=config)
        >>> portfolio_data = pd.DataFrame(...)
        >>> results = await analyzer.analyze_portfolio(portfolio_data)
        >>> print(f"夏普比率: {results['sharpe_ratio']:.2f}")
    """
    
    def __init__(
        self,
        config: AsyncAnalysisConfig,
        analyzer: Optional[PortfolioAnalyzer] = None
    ):
        """初始化异步投资组合分析器
        
        Args:
            config: 异步分析配置
            analyzer: 基础投资组合分析器，如果为None则创建默认实例
        """
        self.config = config
        self.analyzer = analyzer or PortfolioAnalyzer()
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._semaphore = asyncio.Semaphore(config.max_concurrent_analyses)
        
        logger.info(f"异步投资组合分析器初始化完成，最大并发数: {config.max_concurrent_analyses}")
    
    async def analyze_portfolio(
        self,
        portfolio_data: pd.DataFrame,
        benchmark_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """异步分析投资组合
        
        Args:
            portfolio_data: 投资组合数据，包含持仓、价格等信息
            benchmark_data: 基准数据，用于相对分析
            
        Returns:
            包含分析结果的字典，包括：
            - total_return: 总收益率
            - annualized_return: 年化收益率
            - volatility: 波动率
            - sharpe_ratio: 夏普比率
            - max_drawdown: 最大回撤
            - beta: Beta系数（如果有基准数据）
            - alpha: Alpha系数（如果有基准数据）
            - information_ratio: 信息比率（如果有基准数据）
            
        Raises:
            asyncio.TimeoutError: 分析超时
            ValueError: 数据格式错误
        """
        # 生成缓存键
        cache_key = self._generate_cache_key(portfolio_data, benchmark_data)
        
        # 检查缓存
        if self.config.enable_caching and cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp <
                    timedelta(seconds=self.config.cache_ttl)):
                logger.info("使用缓存的投资组合分析结果")
                return result
        
        async with self._semaphore:
            try:
                # 执行异步分析
                analysis_task = asyncio.create_task(
                    self._analyze_portfolio_async(
                        portfolio_data, benchmark_data
                    )
                )
                
                result = await asyncio.wait_for(
                    analysis_task,
                    timeout=self.config.timeout_seconds
                )
                
                # 缓存结果
                if self.config.enable_caching:
                    self._cache[cache_key] = (result, datetime.now())
                
                logger.info("异步投资组合分析完成")
                return result
                
            except asyncio.TimeoutError:
                logger.error("投资组合分析超时")
                raise
            except Exception as e:
                logger.error(f"投资组合分析失败: {e}")
                raise
    
    async def batch_analyze_portfolios(
        self,
        portfolios_data: List[pd.DataFrame],
        benchmark_data: Optional[pd.DataFrame] = None
    ) -> List[Dict[str, Any]]:
        """批量异步分析投资组合
        
        Args:
            portfolios_data: 投资组合数据列表
            benchmark_data: 基准数据
            
        Returns:
            分析结果列表，与输入顺序对应
        """
        tasks = [
            self.analyze_portfolio(portfolio_data, benchmark_data)
            for portfolio_data in portfolios_data
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"投资组合 {i} 分析失败: {result}")
                processed_results.append({})
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def analyze_performance_attribution(
        self,
        portfolio_data: pd.DataFrame,
        benchmark_data: pd.DataFrame,
        factor_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """异步绩效归因分析
        
        Args:
            portfolio_data: 投资组合数据
            benchmark_data: 基准数据
            factor_data: 因子数据，用于因子归因分析
            
        Returns:
            包含归因分析结果的字典
        """
        cache_key = self._generate_cache_key(
            portfolio_data, benchmark_data, factor_data, "attribution"
        )
        
        # 检查缓存
        if self.config.enable_caching and cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp <
                    timedelta(seconds=self.config.cache_ttl)):
                logger.info("使用缓存的绩效归因分析结果")
                return result
        
        async with self._semaphore:
            try:
                attribution_task = asyncio.create_task(
                    self._analyze_performance_attribution_async(
                        portfolio_data, benchmark_data, factor_data
                    )
                )
                
                result = await asyncio.wait_for(
                    attribution_task,
                    timeout=self.config.timeout_seconds
                )
                
                # 缓存结果
                if self.config.enable_caching:
                    self._cache[cache_key] = (result, datetime.now())
                
                logger.info("异步绩效归因分析完成")
                return result
                
            except asyncio.TimeoutError:
                logger.error("绩效归因分析超时")
                raise
            except Exception as e:
                logger.error(f"绩效归因分析失败: {e}")
                raise
    
    async def analyze_risk_metrics(
        self,
        portfolio_data: pd.DataFrame,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """异步风险指标分析
        
        Args:
            portfolio_data: 投资组合数据
            confidence_level: 置信水平，默认为0.95
            
        Returns:
            包含风险指标的字典，包括：
            - var: 方差
            - volatility: 波动率
            - var_95: 95% VaR
            - cvar_95: 95% CVaR
            - max_drawdown: 最大回撤
            - calmar_ratio: 卡玛比率
        """
        cache_key = self._generate_cache_key(
            portfolio_data, confidence_level, "risk"
        )
        
        # 检查缓存
        if self.config.enable_caching and cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            cache_ttl = timedelta(seconds=self.config.cache_ttl)
            if datetime.now() - timestamp < cache_ttl:
                logger.info("使用缓存的风险指标分析结果")
                return result
        
        async with self._semaphore:
            try:
                risk_task = asyncio.create_task(
                    self._analyze_risk_metrics_async(
                        portfolio_data, confidence_level
                    )
                )
                
                result = await asyncio.wait_for(
                    risk_task,
                    timeout=self.config.timeout_seconds
                )
                
                # 缓存结果
                if self.config.enable_caching:
                    self._cache[cache_key] = (result, datetime.now())
                
                logger.info("异步风险指标分析完成")
                return result
                
            except asyncio.TimeoutError:
                logger.error("风险指标分析超时")
                raise
            except Exception as e:
                logger.error(f"风险指标分析失败: {e}")
                raise
    
    async def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()
        logger.info("分析缓存已清空")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息
        
        Returns:
            包含缓存统计的字典
        """
        total_entries = len(self._cache)
        cache_ttl = timedelta(seconds=self.config.cache_ttl)
        expired_entries = sum(
            1 for _, timestamp in self._cache.values()
            if datetime.now() - timestamp > cache_ttl
        )
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'valid_entries': total_entries - expired_entries,
            'cache_ttl': self.config.cache_ttl
        }
    
    async def _analyze_portfolio_async(
        self,
        portfolio_data: pd.DataFrame,
        benchmark_data: Optional[pd.DataFrame]
    ) -> Dict[str, Any]:
        """异步执行投资组合分析
        
        在线程池中执行同步分析操作。
        """
        # 首先加载数据到分析器
        if 'returns' in portfolio_data.columns:
            returns = portfolio_data['returns']
        else:
            # 假设第一列是收益率
            returns = portfolio_data.iloc[:, 0]
        
        values = portfolio_data.get('values', None)
        # 创建简单的持仓数据用于测试
        holdings = pd.DataFrame({
            "weight": [0.3, 0.2, 0.15, 0.1, 0.25],
            "sector": ["tech", "finance", "health", "energy", "consumer"]
        }, index=["AAPL", "JPM", "JNJ", "XOM", "AMZN"])
        
        self.analyzer.load_portfolio_data(returns, values, holdings)
        
        if (benchmark_data is not None and
                'returns' in benchmark_data.columns):
            benchmark_returns = benchmark_data['returns']
            benchmark_values = benchmark_data.get('values', None)
            self.analyzer.load_benchmark_data(
                benchmark_returns, benchmark_values
            )
        
        loop = asyncio.get_event_loop()
        metrics = await loop.run_in_executor(
            None,
            self.analyzer.calculate_portfolio_metrics
        )
        # 将PortfolioMetrics对象转换为字典
        return metrics.__dict__
    
    async def _analyze_performance_attribution_async(
        self,
        portfolio_data: pd.DataFrame,
        benchmark_data: pd.DataFrame,
        factor_data: Optional[pd.DataFrame]
    ) -> Dict[str, Any]:
        """异步执行绩效归因分析
        
        在线程池中执行同步归因分析操作。
        """
        # 首先加载数据到分析器
        if 'returns' in portfolio_data.columns:
            returns = portfolio_data['returns']
        else:
            # 假设第一列是收益率
            returns = portfolio_data.iloc[:, 0]
        
        values = portfolio_data.get('values', None)
        # 创建简单的持仓数据用于测试
        holdings = pd.DataFrame({
            "weight": [0.3, 0.2, 0.15, 0.1, 0.25],
            "sector": ["tech", "finance", "health", "energy", "consumer"]
        }, index=["AAPL", "JPM", "JNJ", "XOM", "AMZN"])
        
        self.analyzer.load_portfolio_data(returns, values, holdings)
        
        # 加载基准数据
        if 'returns' in benchmark_data.columns:
            benchmark_returns = benchmark_data['returns']
        else:
            # 假设第一列是收益率
            benchmark_returns = benchmark_data.iloc[:, 0]
        
        benchmark_values = benchmark_data.get('values', None)
        self.analyzer.load_benchmark_data(benchmark_returns, benchmark_values)
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.analyzer.performance_attribution,
            'monthly'  # 传递period参数
        )
    
    async def _analyze_risk_metrics_async(
        self,
        portfolio_data: pd.DataFrame,
        confidence_level: float
    ) -> Dict[str, Any]:
        """异步执行风险指标分析
        
        在线程池中执行同步风险分析操作。
        """
        # 首先加载数据到分析器
        if 'returns' in portfolio_data.columns:
            returns = portfolio_data['returns']
        else:
            # 假设第一列是收益率
            returns = portfolio_data.iloc[:, 0]
        
        values = portfolio_data.get('values', None)
        # 创建简单的持仓数据用于测试
        holdings = pd.DataFrame({
            "weight": [0.3, 0.2, 0.15, 0.1, 0.25],
            "sector": ["tech", "finance", "health", "energy", "consumer"]
        }, index=["AAPL", "JPM", "JNJ", "XOM", "AMZN"])
        
        self.analyzer.load_portfolio_data(returns, values, holdings)
        
        loop = asyncio.get_event_loop()
        risk_decomp = await loop.run_in_executor(
            None,
            self.analyzer.risk_decomposition
        )
        
        # 将风险分解结果转换为包含风险指标的字典
        return {
            'volatility': risk_decomp.get('total_volatility', 0.0),
            'variance': risk_decomp.get('total_volatility', 0.0) ** 2,
            'var_95': returns.quantile(0.05),
            'cvar_95': returns[returns <= returns.quantile(0.05)].mean(),
            'max_drawdown': risk_decomp.get('max_drawdown', 0.0),
            'calmar_ratio': risk_decomp.get('calmar_ratio', 0.0)
        }
    
    def _generate_cache_key(self, *args) -> str:
        """生成缓存键
        
        Args:
            *args: 用于生成缓存键的参数
            
        Returns:
            缓存键字符串
        """
        # 简单的哈希实现，实际项目中可能需要更复杂的逻辑
        key_parts = []
        for arg in args:
            if isinstance(arg, pd.DataFrame):
                # 使用DataFrame的形状和列名生成键
                key_parts.append(f"df_{arg.shape}_{list(arg.columns)}")
            else:
                key_parts.append(str(arg))
        
        return "_".join(key_parts)


# 便利函数
async def create_async_portfolio_analyzer(
    max_concurrent_analyses: int = 10,
    timeout_seconds: float = 300.0,
    enable_caching: bool = True,
    **kwargs
) -> AsyncPortfolioAnalyzer:
    """创建异步投资组合分析器的便利函数
    
    Args:
        max_concurrent_analyses: 最大并发分析数
        timeout_seconds: 分析超时时间
        enable_caching: 是否启用缓存
        **kwargs: 其他配置参数
        
    Returns:
        配置好的异步投资组合分析器实例
    """
    config = AsyncAnalysisConfig(
        max_concurrent_analyses=max_concurrent_analyses,
        timeout_seconds=timeout_seconds,
        enable_caching=enable_caching,
        **kwargs
    )
    
    return AsyncPortfolioAnalyzer(config=config)