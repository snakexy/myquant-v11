"""
行业暴露管理模块

实现投资组合行业暴露的计算和管理功能
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class SectorExposureManager:
    """
    行业暴露管理器
    
    提供投资组合行业暴露的计算、分析和控制功能，
    帮助投资组合保持在合适的行业分布范围内。
    """
    
    def __init__(
        self, 
        sector_limits: Optional[Dict[str, float]] = None,
        max_sector_weight: float = 0.4,
        min_sectors: int = 5,
        verbose: bool = False
    ):
        """
        初始化行业暴露管理器
        
        Parameters
        ----------
        sector_limits : Dict[str, float], optional
            行业暴露限制
        max_sector_weight : float, default 0.4
            单个行业最大权重
        min_sectors : int, default 5
            最少行业数量
        verbose : bool, default False
            是否输出详细日志
        """
        self.sector_limits = sector_limits or {}
        self.max_sector_weight = max_sector_weight
        self.min_sectors = min_sectors
        self.verbose = verbose
        
        # 历史行业暴露记录
        self.sector_exposure_history = []
        
        if self.verbose:
            logger.info("行业暴露管理器初始化完成")
            if self.sector_limits:
                logger.info(f"行业暴露限制: {self.sector_limits}")
            logger.info(f"单个行业最大权重: {max_sector_weight}")
            logger.info(f"最少行业数量: {min_sectors}")
    
    def calculate_sector_exposure(
        self,
        portfolio_weights: np.ndarray,
        stock_sectors: Dict[str, str],
        stock_universe: List[str]
    ) -> Dict[str, float]:
        """
        计算投资组合的行业暴露
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        stock_sectors : Dict[str, str]
            股票到行业的映射
        stock_universe : List[str]
            股票池
            
        Returns
        -------
        Dict[str, float]
            行业暴露字典
        """
        try:
            # 初始化行业暴露字典
            sector_exposure = {}
            
            # 计算每个行业的总权重
            for i, stock in enumerate(stock_universe):
                if i < len(portfolio_weights):
                    weight = portfolio_weights[i]
                    sector = stock_sectors.get(stock, "其他")
                    sector_exposure[sector] = sector_exposure.get(sector, 0) + weight
            
            if self.verbose:
                logger.info(f"行业暴露计算完成，共{len(sector_exposure)}个行业")
            
            return sector_exposure
            
        except Exception as e:
            logger.error(f"计算行业暴露失败: {e}")
            return {}
    
    def calculate_sector_contribution(
        self,
        portfolio_weights: np.ndarray,
        stock_sectors: Dict[str, str],
        stock_returns: Optional[np.ndarray] = None,
        benchmark_returns: Optional[np.ndarray] = None,
        stock_universe: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        计算各行业的贡献（收益和风险）
        
        Parameters
        ----------
        portfolio_weights : np.ndarray
            投资组合权重
        stock_sectors : Dict[str, str]
            股票到行业的映射
        stock_returns : np.ndarray, optional
            股票收益率
        benchmark_returns : np.ndarray, optional
            基准收益率
        stock_universe : List[str], optional
            股票池
            
        Returns
        -------
        Dict[str, Dict[str, float]]
            各行业的贡献字典
        """
        try:
            if stock_universe is None:
                stock_universe = list(stock_sectors.keys())
            
            # 计算行业暴露
            sector_exposure = self.calculate_sector_exposure(
                portfolio_weights, stock_sectors, stock_universe
            )
            
            # 初始化行业贡献字典
            sector_contributions = {}
            
            # 计算各行业的收益贡献
            if stock_returns is not None and benchmark_returns is not None:
                for sector, exposure in sector_exposure.items():
                    # 计算行业内的股票收益
                    sector_stocks = [
                        stock for stock, sec in stock_sectors.items() 
                        if sec == sector and stock in stock_universe
                    ]
                    
                    if sector_stocks:
                        # 获取行业股票的权重和收益
                        sector_weights = []
                        sector_stock_returns = []
                        sector_bench_returns = []
                        
                        for stock in sector_stocks:
                            try:
                                stock_idx = stock_universe.index(stock)
                                if stock_idx < len(portfolio_weights):
                                    sector_weights.append(portfolio_weights[stock_idx])
                                    sector_stock_returns.append(stock_returns[stock_idx])
                                    sector_bench_returns.append(benchmark_returns[stock_idx])
                            except (ValueError, IndexError):
                                continue
                        
                        if sector_weights:
                            # 计算行业主动收益
                            sector_active_returns = (
                                np.array(sector_stock_returns) - 
                                np.array(sector_bench_returns)
                            )
                            sector_active_return = np.sum(
                                np.array(sector_weights) * sector_active_returns
                            ) / np.sum(sector_weights)
                            
                            # 计算行业风险（收益的标准差）
                            sector_risk = np.std(sector_active_returns)
                            
                            sector_contributions[sector] = {
                                'weight': exposure,
                                'active_return': sector_active_return,
                                'risk': sector_risk,
                                'stock_count': len(sector_stocks)
                            }
                    else:
                        sector_contributions[sector] = {
                            'weight': exposure,
                            'active_return': 0,
                            'risk': 0,
                            'stock_count': 0
                        }
            else:
                # 只计算权重贡献
                for sector, exposure in sector_exposure.items():
                    sector_contributions[sector] = {
                        'weight': exposure,
                        'active_return': 0,
                        'risk': 0,
                        'stock_count': 0
                    }
            
            if self.verbose:
                logger.info(f"行业贡献计算完成，共{len(sector_contributions)}个行业")
            
            return sector_contributions
            
        except Exception as e:
            logger.error(f"计算行业贡献失败: {e}")
            return {}
    
    def check_sector_limits(
        self,
        sector_exposure: Dict[str, float]
    ) -> Dict[str, bool]:
        """
        检查行业暴露是否超过限制
        
        Parameters
        ----------
        sector_exposure : Dict[str, float]
            行业暴露字典
            
        Returns
        -------
        Dict[str, bool]
            各行业是否超过限制
        """
        limit_results = {}
        
        # 检查自定义限制
        for sector, limit in self.sector_limits.items():
            exposure = sector_exposure.get(sector, 0)
            exceeds_limit = exposure > limit
            limit_results[sector] = exceeds_limit
            
            if exceeds_limit and self.verbose:
                logger.warning(
                    f"行业{sector}暴露{exposure:.4f}超过限制{limit:.4f}"
                )
        
        # 检查单个行业最大权重
        for sector, exposure in sector_exposure.items():
            exceeds_max_weight = exposure > self.max_sector_weight
            limit_key = f"{sector}_max_weight"
            limit_results[limit_key] = exceeds_max_weight
            
            if exceeds_max_weight and self.verbose:
                logger.warning(
                    f"行业{sector}权重{exposure:.4f}超过最大值{self.max_sector_weight:.4f}"
                )
        
        return limit_results
    
    def check_diversification(
        self,
        sector_exposure: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        检查行业分散化程度
        
        Parameters
        ----------
        sector_exposure : Dict[str, float]
            行业暴露字典
            
        Returns
        -------
        Dict[str, Any]
            分散化指标
        """
        try:
            # 计算基本统计信息
            total_weight = sum(sector_exposure.values())
            sector_count = len(sector_exposure)
            
            # 计算权重分布
            weights = list(sector_exposure.values())
            
            # 计算赫芬达尔指数（衡量集中度）
            herfindahl_index = sum(w**2 for w in weights)
            
            # 计算有效行业数量（权重大于1%的行业）
            effective_sectors = sum(1 for w in weights if w > 0.01)
            
            # 计算最大行业权重
            max_sector_weight = max(weights) if weights else 0
            
            # 计算行业权重标准差
            weight_std = np.std(weights)
            
            # 计算基尼系数
            sorted_weights = sorted(weights)
            n = len(sorted_weights)
            cum_weights = np.cumsum(sorted_weights)
            gini = (n + 1 - 2 * sum((n + 1 - i) * w for i, w in enumerate(sorted_weights))) / (n * sum(sorted_weights))
            
            diversification_metrics = {
                'sector_count': sector_count,
                'effective_sectors': effective_sectors,
                'herfindahl_index': herfindahl_index,
                'max_sector_weight': max_sector_weight,
                'weight_std': weight_std,
                'gini_coefficient': gini,
                'meets_min_sectors': sector_count >= self.min_sectors,
                'max_weight_ratio': max_sector_weight / total_weight if total_weight > 0 else 0
            }
            
            if self.verbose:
                logger.info(f"行业分散化指标计算完成")
                logger.info(f"行业数量: {sector_count}, 有效行业: {effective_sectors}")
                logger.info(f"赫芬达尔指数: {herfindahl_index:.4f}")
            
            return diversification_metrics
            
        except Exception as e:
            logger.error(f"计算行业分散化指标失败: {e}")
            return {}
    
    def suggest_sector_rebalancing(
        self,
        current_sector_exposure: Dict[str, float],
        target_sector_exposure: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        建议行业再平衡方案
        
        Parameters
        ----------
        current_sector_exposure : Dict[str, float]
            当前行业暴露
        target_sector_exposure : Dict[str, float], optional
            目标行业暴露
            
        Returns
        -------
        Dict[str, float]
            建议的行业权重调整
        """
        try:
            # 如果没有目标暴露，使用等权重
            if target_sector_exposure is None:
                all_sectors = set(current_sector_exposure.keys())
                target_weight = 1.0 / len(all_sectors)
                target_sector_exposure = {
                    sector: target_weight for sector in all_sectors
                }
            
            # 计算调整建议
            rebalancing_suggestions = {}
            
            for sector, target_weight in target_sector_exposure.items():
                current_weight = current_sector_exposure.get(sector, 0)
                adjustment = target_weight - current_weight
                
                # 应用限制
                if abs(adjustment) > 0.1:  # 最大单次调整10%
                    adjustment = 0.1 * np.sign(adjustment)
                
                rebalancing_suggestions[sector] = adjustment
            
            if self.verbose:
                logger.info(f"行业再平衡建议计算完成")
            
            return rebalancing_suggestions
            
        except Exception as e:
            logger.error(f"计算行业再平衡建议失败: {e}")
            return {}
    
    def update_sector_exposure_history(
        self,
        sector_exposure: Dict[str, float],
        timestamp: Optional[pd.Timestamp] = None
    ) -> None:
        """
        更新行业暴露历史记录
        
        Parameters
        ----------
        sector_exposure : Dict[str, float]
            当前行业暴露
        timestamp : pd.Timestamp, optional
            时间戳
        """
        if timestamp is None:
            timestamp = pd.Timestamp.now()
        
        self.sector_exposure_history.append({
            'timestamp': timestamp,
            'sector_exposure': sector_exposure.copy()
        })
        
        # 保持历史记录在合理范围内
        max_history_size = 1000
        if len(self.sector_exposure_history) > max_history_size:
            self.sector_exposure_history = self.sector_exposure_history[-max_history_size:]
        
        if self.verbose:
            logger.info(f"行业暴露历史记录已更新，当前记录数: {len(self.sector_exposure_history)}")
    
    def get_sector_exposure_statistics(self) -> Dict[str, Any]:
        """
        获取行业暴露统计信息
        
        Returns
        -------
        Dict[str, Any]
            行业暴露统计信息
        """
        if not self.sector_exposure_history:
            return {}
        
        # 收集所有行业的历史数据
        all_sectors = set()
        for record in self.sector_exposure_history:
            all_sectors.update(record['sector_exposure'].keys())
        
        # 计算每个行业的统计信息
        statistics = {
            'record_count': len(self.sector_exposure_history),
            'sector_statistics': {}
        }
        
        for sector in all_sectors:
            sector_values = [
                record['sector_exposure'].get(sector, 0) 
                for record in self.sector_exposure_history
            ]
            
            sector_stats = {
                'mean': np.mean(sector_values),
                'std': np.std(sector_values),
                'min': np.min(sector_values),
                'max': np.max(sector_values),
                'median': np.median(sector_values),
                'current': sector_values[-1] if sector_values else 0
            }
            
            # 检查是否有限制
            if sector in self.sector_limits:
                sector_stats['limit'] = self.sector_limits[sector]
                sector_stats['exceeds_limit'] = (
                    sector_stats['current'] > sector_stats['limit']
                )
            
            # 检查是否超过最大权重
            sector_stats['exceeds_max_weight'] = (
                sector_stats['current'] > self.max_sector_weight
            )
            
            statistics['sector_statistics'][sector] = sector_stats
        
        return statistics