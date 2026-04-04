"""
绩效分析系统
基于QLib最佳实践的全面绩效分析模块
支持多维度绩效指标计算、可视化、报告生成
"""

import os
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import json

# 配置日志
logger = logging.getLogger(__name__)

# 尝试导入高级图表库
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    logger.warning("Plotly不可用，将使用Matplotlib")
    PLOTLY_AVAILABLE = False

# 导入matplotlib
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    logger.warning("Matplotlib不可用，可视化功能将受限")
    MATPLOTLIB_AVAILABLE = False

# 定义类型别名，用于条件类型注解
if PLOTLY_AVAILABLE:
    PlotlyFigure = go.Figure
else:
    PlotlyFigure = type('DummyFigure', (), {})  # 虚拟类

if MATPLOTLIB_AVAILABLE:
    import matplotlib.figure
    MatplotlibFigure = matplotlib.figure.Figure
else:
    MatplotlibFigure = type('DummyMatplotlibFigure', (), {})  # 虚拟类


class PerformanceMetrics:
    """绩效指标计算器"""
    
    def __init__(self):
        self.metrics = {}
    
    def calculate_all_metrics(
        self, 
        returns: pd.Series,
        benchmark_returns: pd.Series = None,
        risk_free_rate: float = 0.03,
        trading_days: int = 252
    ) -> Dict[str, float]:
        """
        计算所有绩效指标
        
        Args:
            returns: 策略收益率序列
            benchmark_returns: 基准收益率序列
            risk_free_rate: 无风险利率
            trading_days: 年化交易天数
            
        Returns:
            绩效指标字典
        """
        metrics = {}
        
        # 基本收益指标
        metrics.update(self._calculate_return_metrics(returns, trading_days))
        
        # 风险指标
        metrics.update(self._calculate_risk_metrics(returns, trading_days))
        
        # 风险调整后收益指标
        metrics.update(self._calculate_risk_adjusted_metrics(
            returns, risk_free_rate, trading_days
        ))
        
        # 如果有基准，计算相对基准的指标
        if benchmark_returns is not None:
            metrics.update(self._calculate_benchmark_metrics(
                returns, benchmark_returns, risk_free_rate, trading_days
            ))
        
        # 其他高级指标
        metrics.update(self._calculate_advanced_metrics(returns, trading_days))
        
        self.metrics = metrics
        return metrics
    
    def _calculate_return_metrics(
        self, 
        returns: pd.Series, 
        trading_days: int
    ) -> Dict[str, float]:
        """计算收益相关指标"""
        metrics = {}
        
        # 累计收益
        cumulative_return = (1 + returns).prod() - 1
        metrics['cumulative_return'] = float(cumulative_return)
        
        # 年化收益
        if len(returns) > 0:
            days_ratio = trading_days / len(returns)
            annual_return = (1 + cumulative_return) ** days_ratio - 1
        else:
            annual_return = 0.0
        metrics['annual_return'] = float(annual_return)
        
        # 年化波动率
        annual_volatility = returns.std() * np.sqrt(trading_days)
        metrics['annual_volatility'] = float(annual_volatility)
        
        # 月度收益
        monthly_returns = self._calculate_monthly_returns(returns)
        metrics['best_monthly_return'] = float(monthly_returns.max())
        metrics['worst_monthly_return'] = float(monthly_returns.min())
        metrics['avg_monthly_return'] = float(monthly_returns.mean())
        
        return metrics
    
    def _calculate_risk_metrics(
        self, 
        returns: pd.Series, 
        trading_days: int
    ) -> Dict[str, float]:
        """计算风险相关指标"""
        metrics = {}
        
        # 最大回撤
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        metrics['max_drawdown'] = float(max_drawdown)
        
        # 回撤持续时间
        metrics['max_drawdown_duration'] = (
            self._calculate_max_drawdown_duration(drawdown)
        )
        
        # 下行风险
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            downside_risk = downside_returns.std() * np.sqrt(trading_days)
        else:
            downside_risk = 0.0
        metrics['downside_risk'] = float(downside_risk)
        
        # 偏度和峰度
        metrics['skewness'] = float(returns.skew())
        metrics['kurtosis'] = float(returns.kurtosis())
        
        # VaR (95%置信水平)
        var_95 = returns.quantile(0.05)
        metrics['var_95'] = float(var_95)
        
        # CVaR (条件VaR)
        cvar_95 = returns[returns <= var_95].mean()
        metrics['cvar_95'] = float(cvar_95)
        
        return metrics
    
    def _calculate_risk_adjusted_metrics(
        self,
        returns: pd.Series,
        risk_free_rate: float,
        trading_days: int
    ) -> Dict[str, float]:
        """计算风险调整后收益指标"""
        metrics = {}
        
        # 直接从收益数据计算，避免依赖其他指标
        annual_return = self.metrics.get('annual_return', 0)
        annual_volatility = self.metrics.get('annual_volatility', 0)
        max_drawdown = self.metrics.get('max_drawdown', 0)
        downside_risk = self.metrics.get('downside_risk', 0)
        
        # 夏普比率 - 修复计算逻辑
        # 使用日度收益计算超额收益，然后年化
        annual_excess_return = 0.0
        if len(returns) > 0:
            # 计算日度超额收益
            daily_rf = risk_free_rate / trading_days
            daily_excess_returns = returns - daily_rf
            
            # 计算年化超额收益
            cumulative_excess_return = (1 + daily_excess_returns).prod()
            days_ratio = trading_days / len(returns)
            annual_excess_return = cumulative_excess_return ** days_ratio - 1
            
            # 计算年化波动率（如果尚未计算）
            if annual_volatility <= 0:
                annual_volatility = returns.std() * np.sqrt(trading_days)
            
            # 计算夏普比率
            if annual_volatility > 0:
                sharpe_ratio = annual_excess_return / annual_volatility
            else:
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0
            
        metrics['sharpe_ratio'] = float(sharpe_ratio)
        
        # 索提诺比率
        if downside_risk > 0:
            sortino_ratio = annual_excess_return / downside_risk
        else:
            # 计算下行风险
            downside_returns = returns[returns < 0]
            if len(downside_returns) > 0:
                downside_risk = downside_returns.std() * np.sqrt(trading_days)
                if downside_risk > 0:
                    sortino_ratio = annual_excess_return / downside_risk
                else:
                    sortino_ratio = 0.0
            else:
                sortino_ratio = 0.0
        metrics['sortino_ratio'] = float(sortino_ratio)
        
        # Calmar比率
        if abs(max_drawdown) > 0:
            calmar_ratio = annual_return / abs(max_drawdown)
        else:
            calmar_ratio = 0.0
        metrics['calmar_ratio'] = float(calmar_ratio)
        
        return metrics
    
    def _calculate_benchmark_metrics(
        self, 
        returns: pd.Series,
        benchmark_returns: pd.Series,
        risk_free_rate: float,
        trading_days: int
    ) -> Dict[str, float]:
        """计算相对于基准的指标"""
        metrics = {}
        
        # 确保时间对齐
        aligned_data = pd.concat(
            [returns, benchmark_returns], axis=1, join='inner'
        )
        aligned_returns = aligned_data.iloc[:, 0]
        aligned_benchmark = aligned_data.iloc[:, 1]
        
        # 超额收益
        excess_returns = aligned_returns - aligned_benchmark
        metrics['excess_return'] = float((1 + excess_returns).prod() - 1)
        
        # 跟踪误差
        tracking_error = excess_returns.std() * np.sqrt(trading_days)
        metrics['tracking_error'] = float(tracking_error)
        
        # 信息比率
        if tracking_error > 0:
            information_ratio = metrics['excess_return'] / tracking_error
        else:
            information_ratio = 0.0
        metrics['information_ratio'] = float(information_ratio)
        
        # Alpha和Beta
        alpha, beta = self._calculate_alpha_beta(
            aligned_returns, aligned_benchmark, risk_free_rate, trading_days
        )
        metrics['alpha'] = float(alpha)
        metrics['beta'] = float(beta)
        
        # R-squared
        correlation = aligned_returns.corr(aligned_benchmark)
        metrics['r_squared'] = float(correlation ** 2)
        
        return metrics
    
    def _calculate_advanced_metrics(
        self, 
        returns: pd.Series, 
        trading_days: int
    ) -> Dict[str, float]:
        """计算高级指标"""
        metrics = {}
        
        # 胜率
        winning_trades = len(returns[returns > 0])
        total_trades = len(returns)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        metrics['win_rate'] = float(win_rate)
        
        # 盈亏比
        if len(returns[returns > 0]) > 0 and len(returns[returns < 0]) > 0:
            avg_win = returns[returns > 0].mean()
            avg_loss = abs(returns[returns < 0].mean())
            profit_loss_ratio = (
                avg_win / avg_loss if avg_loss > 0 else float('inf')
            )
        else:
            profit_loss_ratio = 0.0
        metrics['profit_loss_ratio'] = float(profit_loss_ratio)
        
        # 期望收益
        expected_return = returns.mean() * trading_days
        metrics['expected_return'] = float(expected_return)
        
        # 收益稳定性 (收益序列的自相关性)
        if len(returns) > 1:
            autocorrelation = returns.autocorr()
        else:
            autocorrelation = 0.0
        metrics['return_autocorrelation'] = float(autocorrelation)
        
        return metrics
    
    def _calculate_monthly_returns(self, returns: pd.Series) -> pd.Series:
        """计算月度收益"""
        if isinstance(returns.index, pd.DatetimeIndex):
            monthly_returns = returns.groupby(pd.Grouper(freq='ME')).apply(
                lambda x: (1 + x).prod() - 1
            )
        else:
            # 如果不是时间序列，返回空Series
            monthly_returns = pd.Series()
        return monthly_returns
    
    def _calculate_max_drawdown_duration(self, drawdown: pd.Series) -> int:
        """计算最大回撤持续时间（天数）"""
        if len(drawdown) == 0:
            return 0
        
        # 找到最大回撤的起始和结束时间
        max_dd_end = drawdown.idxmin()
        max_dd_start = drawdown[:max_dd_end].idxmax()
        
        # 计算持续时间
        if isinstance(drawdown.index, pd.DatetimeIndex):
            duration = (max_dd_end - max_dd_start).days
        else:
            duration = max_dd_end - max_dd_start
        
        return int(duration)
    
    def _calculate_alpha_beta(
        self, 
        returns: pd.Series, 
        benchmark_returns: pd.Series,
        risk_free_rate: float,
        trading_days: int
    ) -> Tuple[float, float]:
        """计算Alpha和Beta"""
        # 年化无风险利率
        daily_rf = (1 + risk_free_rate) ** (1/trading_days) - 1
        
        # 超额收益
        excess_returns = returns - daily_rf
        excess_benchmark = benchmark_returns - daily_rf
        
        # 计算Beta
        if excess_benchmark.var() > 0:
            beta = (
                excess_returns.cov(excess_benchmark) / excess_benchmark.var()
            )
        else:
            beta = 0.0
        
        # 计算Alpha
        alpha_mean = excess_returns.mean() - beta * excess_benchmark.mean()
        alpha = alpha_mean * trading_days
        
        return alpha, beta


class PerformanceVisualizer:
    """绩效可视化器"""
    
    def __init__(self, use_plotly: bool = None):
        """
        初始化可视化器
        
        Args:
            use_plotly: 是否使用Plotly，None时自动检测
        """
        if use_plotly is None:
            self.use_plotly = PLOTLY_AVAILABLE
        else:
            self.use_plotly = use_plotly
        
        # 设置中文字体（如果matplotlib可用）
        if MATPLOTLIB_AVAILABLE:
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
    
    def plot_nav_curve(
        self, 
        nav_data: pd.Series,
        benchmark_nav: pd.Series = None,
        title: str = "净值曲线"
    ) -> Any:
        """绘制净值曲线"""
        if self.use_plotly:
            return self._plot_nav_curve_plotly(nav_data, benchmark_nav, title)
        else:
            return self._plot_nav_curve_matplotlib(
                nav_data, benchmark_nav, title
            )
    
    def plot_drawdown(
        self, 
        drawdown_data: pd.Series,
        title: str = "回撤分析"
    ) -> Any:
        """绘制回撤图"""
        if self.use_plotly:
            return self._plot_drawdown_plotly(drawdown_data, title)
        else:
            return self._plot_drawdown_matplotlib(drawdown_data, title)
    
    def plot_monthly_returns_heatmap(
        self, 
        returns: pd.Series,
        title: str = "月度收益热力图"
    ) -> Any:
        """绘制月度收益热力图"""
        if self.use_plotly:
            return self._plot_monthly_returns_heatmap_plotly(returns, title)
        else:
            return self._plot_monthly_returns_heatmap_matplotlib(
                returns, title
            )
    
    def plot_performance_metrics_radar(
        self, 
        metrics: Dict[str, float],
        title: str = "绩效指标雷达图"
    ) -> Any:
        """绘制绩效指标雷达图"""
        if self.use_plotly:
            return self._plot_metrics_radar_plotly(metrics, title)
        else:
            return self._plot_metrics_radar_matplotlib(metrics, title)
    
    def _plot_nav_curve_plotly(
        self,
        nav_data: pd.Series,
        benchmark_nav: pd.Series = None,
        title: str = "净值曲线"
    ) -> PlotlyFigure:
        """使用Plotly绘制净值曲线"""
        fig = go.Figure()
        
        # 策略净值曲线
        fig.add_trace(go.Scatter(
            x=nav_data.index,
            y=nav_data.values,
            mode='lines',
            name='策略净值',
            line=dict(color='#1f77b4', width=2)
        ))
        
        # 基准净值曲线（如果有）
        if benchmark_nav is not None:
            fig.add_trace(go.Scatter(
                x=benchmark_nav.index,
                y=benchmark_nav.values,
                mode='lines',
                name='基准净值',
                line=dict(color='#ff7f0e', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="日期",
            yaxis_title="净值",
            hovermode='x unified',
            showlegend=True
        )
        
        return fig
    
    def _plot_nav_curve_matplotlib(
        self,
        nav_data: pd.Series,
        benchmark_nav: pd.Series = None,
        title: str = "净值曲线"
    ):
        """使用Matplotlib绘制净值曲线"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 策略净值曲线
        ax.plot(nav_data.index, nav_data.values, 
                label='策略净值', color='#1f77b4', linewidth=2)
        
        # 基准净值曲线（如果有）
        if benchmark_nav is not None:
            ax.plot(benchmark_nav.index, benchmark_nav.values,
                    label='基准净值', color='#ff7f0e', linestyle='--', linewidth=2)
        
        ax.set_title(title, fontsize=14)
        ax.set_xlabel('日期')
        ax.set_ylabel('净值')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def _plot_drawdown_plotly(
        self,
        drawdown_data: pd.Series,
        title: str = "回撤分析"
    ) -> PlotlyFigure:
        """使用Plotly绘制回撤图"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=drawdown_data.index,
            y=drawdown_data.values * 100,  # 转换为百分比
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.3)',
            line=dict(color='red', width=1),
            name='回撤'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="日期",
            yaxis_title="回撤 (%)",
            hovermode='x unified',
            showlegend=True
        )
        
        return fig
    
    def _plot_drawdown_matplotlib(
        self,
        drawdown_data: pd.Series,
        title: str = "回撤分析"
    ):
        """使用Matplotlib绘制回撤图"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.fill_between(
            drawdown_data.index,
            drawdown_data.values * 100,  # 转换为百分比
            0, alpha=0.3, color='red', label='回撤'
        )
        ax.plot(drawdown_data.index, drawdown_data.values * 100,
                color='red', linewidth=1)
        
        ax.set_title(title, fontsize=14)
        ax.set_xlabel('日期')
        ax.set_ylabel('回撤 (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def _plot_monthly_returns_heatmap_plotly(
        self,
        returns: pd.Series,
        title: str = "月度收益热力图"
    ) -> PlotlyFigure:
        """使用Plotly绘制月度收益热力图"""
        if not isinstance(returns.index, pd.DatetimeIndex):
            raise ValueError("收益序列必须包含时间索引")
        
        # 提取年份和月份
        monthly_returns = returns.groupby(
            [returns.index.year, returns.index.month]
        ).apply(lambda x: (1 + x).prod() - 1)
        
        # 创建数据透视表
        monthly_df = monthly_returns.reset_index()
        monthly_df.columns = ['year', 'month', 'return']
        pivot_table = monthly_df.pivot(
            index='year', columns='month', values='return'
        )
        
        # 创建热力图
        fig = px.imshow(
            pivot_table.values * 100,  # 转换为百分比
            x=pivot_table.columns,
            y=pivot_table.index,
            color_continuous_scale='RdYlGn',
            aspect="auto",
            title=title
        )
        
        fig.update_layout(
            xaxis_title="月份",
            yaxis_title="年份"
        )
        
        return fig
    
    def _plot_monthly_returns_heatmap_matplotlib(
        self,
        returns: pd.Series,
        title: str = "月度收益热力图"
    ):
        """使用Matplotlib绘制月度收益热力图"""
        if not isinstance(returns.index, pd.DatetimeIndex):
            raise ValueError("收益序列必须包含时间索引")
        
        # 提取年份和月份
        monthly_returns = returns.groupby(
            [returns.index.year, returns.index.month]
        ).apply(lambda x: (1 + x).prod() - 1)
        
        # 创建数据透视表
        monthly_df = monthly_returns.reset_index()
        monthly_df.columns = ['year', 'month', 'return']
        pivot_table = monthly_df.pivot(
            index='year', columns='month', values='return'
        )
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        im = ax.imshow(pivot_table.values * 100, cmap='RdYlGn', aspect='auto')
        
        # 设置坐标轴标签
        ax.set_xticks(range(len(pivot_table.columns)))
        ax.set_xticklabels(pivot_table.columns)
        ax.set_yticks(range(len(pivot_table.index)))
        ax.set_yticklabels(pivot_table.index)
        
        ax.set_xlabel('月份')
        ax.set_ylabel('年份')
        ax.set_title(title, fontsize=14)
        
        # 添加颜色条
        plt.colorbar(im, ax=ax, label='收益 (%)')
        
        plt.tight_layout()
        return fig
    
    def _plot_metrics_radar_plotly(
        self,
        metrics: Dict[str, float],
        title: str = "绩效指标雷达图"
    ) -> PlotlyFigure:
        """使用Plotly绘制雷达图"""
        # 选择关键指标
        key_metrics = {
            '年化收益': metrics.get('annual_return', 0),
            '夏普比率': metrics.get('sharpe_ratio', 0),
            '最大回撤': abs(metrics.get('max_drawdown', 0)),  # 取绝对值
            '信息比率': metrics.get('information_ratio', 0),
            '胜率': metrics.get('win_rate', 0),
            'Calmar比率': metrics.get('calmar_ratio', 0)
        }
        
        # 标准化指标值（0-1范围）
        max_values = {
            '年化收益': 0.5,  # 50%
            '夏普比率': 3.0,
            '最大回撤': 0.3,  # 30%
            '信息比率': 2.0,
            '胜率': 1.0,     # 100%
            'Calmar比率': 2.0
        }
        
        normalized_metrics = {}
        for key, value in key_metrics.items():
            max_val = max_values[key]
            normalized_value = min(value / max_val, 1.0) if max_val > 0 else 0
            normalized_metrics[key] = normalized_value
        
        categories = list(normalized_metrics.keys())
        values = list(normalized_metrics.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # 闭合图形
            theta=categories + [categories[0]],
            fill='toself',
            name='绩效指标'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=False,
            title=title
        )
        
        return fig
    
    def _plot_metrics_radar_matplotlib(
        self,
        metrics: Dict[str, float],
        title: str = "绩效指标雷达图"
    ):
        """使用Matplotlib绘制雷达图"""
        # 选择关键指标
        key_metrics = {
            '年化收益': metrics.get('annual_return', 0),
            '夏普比率': metrics.get('sharpe_ratio', 0),
            '最大回撤': abs(metrics.get('max_drawdown', 0)),
            '信息比率': metrics.get('information_ratio', 0),
            '胜率': metrics.get('win_rate', 0),
            'Calmar比率': metrics.get('calmar_ratio', 0)
        }
        
        # 标准化指标值
        max_values = {
            '年化收益': 0.5,
            '夏普比率': 3.0,
            '最大回撤': 0.3,
            '信息比率': 2.0,
            '胜率': 1.0,
            'Calmar比率': 2.0
        }
        
        normalized_metrics = {}
        for key, value in key_metrics.items():
            max_val = max_values[key]
            normalized_value = min(value / max_val, 1.0) if max_val > 0 else 0
            normalized_metrics[key] = normalized_value
        
        categories = list(normalized_metrics.keys())
        values = list(normalized_metrics.values())
        
        # 闭合图形
        values += values[:1]
        categories += categories[:1]
        
        # 计算角度
        angles = np.linspace(
            0, 2*np.pi, len(categories)-1, endpoint=False
        ).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(
            figsize=(8, 8), subplot_kw=dict(projection='polar')
        )
        
        ax.plot(angles, values, 'o-', linewidth=2, label='绩效指标')
        ax.fill(angles, values, alpha=0.25)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories[:-1])
        ax.set_ylim(0, 1)
        ax.set_title(title, size=14, y=1.08)
        
        plt.tight_layout()
        return fig


class PerformanceAnalyzer:
    """绩效分析器"""
    
    def __init__(self, use_plotly: bool = None):
        """
        初始化绩效分析器
        
        Args:
            use_plotly: 是否使用Plotly进行可视化
        """
        self.metrics_calculator = PerformanceMetrics()
        self.visualizer = PerformanceVisualizer(use_plotly)
        self.analysis_results = {}
    
    def analyze_backtest(
        self, 
        backtest_result: Dict[str, Any],
        benchmark_data: pd.Series = None,
        risk_free_rate: float = 0.03
    ) -> Dict[str, Any]:
        """
        分析回测结果
        
        Args:
            backtest_result: 回测结果字典
            benchmark_data: 基准数据（收益率序列）
            risk_free_rate: 无风险利率
            
        Returns:
            分析结果
        """
        try:
            # 提取收益数据
            returns = self._extract_returns_from_backtest(backtest_result)
            
            if returns.empty:
                raise ValueError("无法从回测结果中提取收益数据")
            
            # 计算所有绩效指标
            metrics = self.metrics_calculator.calculate_all_metrics(
                returns, benchmark_data, risk_free_rate
            )
            
            # 生成可视化图表
            visualizations = self._generate_visualizations(
                returns, benchmark_data, metrics
            )
            
            # 生成分析报告
            report = self._generate_analysis_report(backtest_result, metrics)
            
            # 存储结果
            analysis_id = f"analysis_{len(self.analysis_results) + 1}"
            result = {
                "analysis_id": analysis_id,
                "backtest_info": {
                    "strategy_name": backtest_result.get(
                        "strategy_name", "未知策略"
                    ),
                    "period": (
                        f"{backtest_result.get('start_date', '')} 到 "
                        f"{backtest_result.get('end_date', '')}"
                    ),
                    "initial_capital": backtest_result.get(
                        "initial_capital", 0
                    )
                },
                "metrics": metrics,
                "visualizations": visualizations,
                "report": report,
                "timestamp": datetime.now().isoformat()
            }
            
            self.analysis_results[analysis_id] = result
            logger.info(f"✅ 绩效分析完成: {analysis_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 绩效分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"绩效分析失败: {str(e)}"
            }
    
    def _extract_returns_from_backtest(
        self, backtest_result: Dict[str, Any]
    ) -> pd.Series:
        """从回测结果中提取收益数据"""
        result_data = backtest_result.get("result", {})
        
        # 尝试从不同位置提取收益数据
        if "returns" in result_data and len(result_data["returns"]) > 0:
            returns = pd.Series(result_data["returns"])
            if ("dates" in result_data
                    and len(result_data["dates"]) == len(returns)):
                try:
                    returns.index = pd.to_datetime(result_data["dates"])
                except Exception:
                    pass
            return returns
        
        elif "nav_curve" in result_data and len(result_data["nav_curve"]) > 1:
            # 从净值曲线计算收益
            nav_curve = pd.Series(result_data["nav_curve"])
            returns = nav_curve.pct_change().dropna()
            if ("dates" in result_data
                    and len(result_data["dates"]) == len(nav_curve)):
                try:
                    returns.index = pd.to_datetime(result_data["dates"][1:])
                except Exception:
                    pass
            return returns
        
        else:
            # 生成模拟收益数据
            logger.warning("使用模拟收益数据进行绩效分析")
            dates = pd.date_range('2020-01-01', periods=252, freq='D')
            np.random.seed(42)
            returns = pd.Series(
                np.random.normal(0.001, 0.02, 252), index=dates
            )
            return returns
    
    def _generate_visualizations(
        self, 
        returns: pd.Series,
        benchmark_data: pd.Series = None,
        metrics: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """生成可视化图表"""
        visualizations = {}
        
        try:
            # 计算净值曲线
            nav_curve = (1 + returns).cumprod()
            benchmark_nav = None
            if benchmark_data is not None:
                benchmark_nav = (1 + benchmark_data).cumprod()
            
            # 计算回撤
            running_max = nav_curve.expanding().max()
            drawdown = (nav_curve - running_max) / running_max
            
            # 生成图表
            visualizations["nav_curve"] = self.visualizer.plot_nav_curve(
                nav_curve, benchmark_nav, "净值曲线对比"
            )
            
            visualizations["drawdown"] = self.visualizer.plot_drawdown(
                drawdown, "回撤分析"
            )
            
            visualizations["monthly_heatmap"] = (
                self.visualizer.plot_monthly_returns_heatmap(
                    returns, "月度收益热力图"
                )
            )
            
            if metrics:
                visualizations["metrics_radar"] = (
                    self.visualizer.plot_performance_metrics_radar(
                        metrics, "绩效指标雷达图"
                    )
                )
            
        except Exception as e:
            logger.warning(f"可视化生成失败: {e}")
            visualizations["error"] = str(e)
        
        return visualizations
    
    def _generate_analysis_report(
        self, 
        backtest_result: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """生成分析报告"""
        report = {
            "summary": self._generate_summary(backtest_result, metrics),
            "detailed_metrics": self._categorize_metrics(metrics),
            "risk_assessment": self._assess_risk(metrics),
            "performance_rating": self._rate_performance(metrics),
            "recommendations": self._generate_recommendations(metrics)
        }
        
        return report
    
    def _generate_summary(
        self, 
        backtest_result: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """生成绩效摘要"""
        strategy_name = backtest_result.get("strategy_name", "未知策略")
        period = (
            f"{backtest_result.get('start_date', '')} 到 "
            f"{backtest_result.get('end_date', '')}"
        )
        
        summary = {
            "strategy_name": strategy_name,
            "period": period,
            "key_metrics": {
                "累计收益": f"{metrics.get('cumulative_return', 0):.2%}",
                "年化收益": f"{metrics.get('annual_return', 0):.2%}",
                "夏普比率": f"{metrics.get('sharpe_ratio', 0):.2f}",
                "最大回撤": f"{metrics.get('max_drawdown', 0):.2%}",
                "信息比率": f"{metrics.get('information_ratio', 0):.2f}"
            },
            "overall_assessment": self._get_overall_assessment(metrics)
        }
        
        return summary
    
    def _categorize_metrics(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """分类整理绩效指标"""
        categorized = {
            "return_metrics": {
                "累计收益": metrics.get('cumulative_return', 0),
                "年化收益": metrics.get('annual_return', 0),
                "期望收益": metrics.get('expected_return', 0),
                "最佳月度收益": metrics.get('best_monthly_return', 0),
                "最差月度收益": metrics.get('worst_monthly_return', 0),
                "平均月度收益": metrics.get('avg_monthly_return', 0)
            },
            "risk_metrics": {
                "年化波动率": metrics.get('annual_volatility', 0),
                "最大回撤": metrics.get('max_drawdown', 0),
                "回撤持续时间": metrics.get('max_drawdown_duration', 0),
                "下行风险": metrics.get('downside_risk', 0),
                "VaR_95": metrics.get('var_95', 0),
                "CVaR_95": metrics.get('cvar_95', 0)
            },
            "risk_adjusted_metrics": {
                "夏普比率": metrics.get('sharpe_ratio', 0),
                "索提诺比率": metrics.get('sortino_ratio', 0),
                "Calmar比率": metrics.get('calmar_ratio', 0)
            },
            "benchmark_metrics": {
                "超额收益": metrics.get('excess_return', 0),
                "跟踪误差": metrics.get('tracking_error', 0),
                "信息比率": metrics.get('information_ratio', 0),
                "Alpha": metrics.get('alpha', 0),
                "Beta": metrics.get('beta', 0),
                "R平方": metrics.get('r_squared', 0)
            },
            "advanced_metrics": {
                "胜率": metrics.get('win_rate', 0),
                "盈亏比": metrics.get('profit_loss_ratio', 0),
                "偏度": metrics.get('skewness', 0),
                "峰度": metrics.get('kurtosis', 0),
                "收益自相关性": metrics.get('return_autocorrelation', 0)
            }
        }
        
        return categorized
    
    def _assess_risk(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """风险评估"""
        max_drawdown = abs(metrics.get('max_drawdown', 0))
        var_95 = metrics.get('var_95', 0)
        downside_risk = metrics.get('downside_risk', 0)
        
        # 风险评估等级
        risk_level = "低风险"
        if max_drawdown > 0.15 or var_95 < -0.05:
            risk_level = "高风险"
        elif max_drawdown > 0.08:
            risk_level = "中风险"
        
        assessment = {
            "risk_level": risk_level,
            "max_drawdown_severity": (
                "严重" if max_drawdown > 0.15 
                else "中等" if max_drawdown > 0.08 
                else "轻微"
            ),
            "var_risk": (
                "高" if var_95 < -0.05 
                else "中" if var_95 < -0.03 
                else "低"
            ),
            "downside_risk_level": (
                "高" if downside_risk > 0.2 
                else "中" if downside_risk > 0.1 
                else "低"
            )
        }
        
        return assessment
    
    def _rate_performance(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """绩效评级"""
        annual_return = metrics.get('annual_return', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        max_drawdown = abs(metrics.get('max_drawdown', 0))
        information_ratio = metrics.get('information_ratio', 0)
        
        # 综合评分 (0-100分)
        return_score = min(annual_return * 200, 40)  # 收益部分最多40分
        risk_score = min(sharpe_ratio * 10, 30) if sharpe_ratio > 0 else 0
        drawdown_score = max(0, 20 - max_drawdown * 100)  # 回撤部分最多20分
        benchmark_score = (
            min(information_ratio * 5, 10) if information_ratio > 0 else 0
        )
        
        total_score = (
            return_score + risk_score + drawdown_score + benchmark_score
        )
        
        # 绩效等级
        if total_score >= 80:
            rating = "优秀"
        elif total_score >= 60:
            rating = "良好"
        elif total_score >= 40:
            rating = "一般"
        else:
            rating = "较差"
        
        return {
            "total_score": round(total_score, 1),
            "rating": rating,
            "component_scores": {
                "收益得分": round(return_score, 1),
                "风险调整得分": round(risk_score, 1),
                "回撤控制得分": round(drawdown_score, 1),
                "基准比较得分": round(benchmark_score, 1)
            }
        }
    
    def _generate_recommendations(
        self, metrics: Dict[str, float]
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        annual_return = metrics.get('annual_return', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        max_drawdown = abs(metrics.get('max_drawdown', 0))
        win_rate = metrics.get('win_rate', 0)
        
        if annual_return < 0.05:
            recommendations.append("策略收益偏低，建议优化选股逻辑或调整持仓周期")
        
        if sharpe_ratio < 1.0:
            recommendations.append("夏普比率较低，建议降低策略波动性或提高收益稳定性")
        
        if max_drawdown > 0.1:
            recommendations.append("最大回撤较大，建议加强风险控制或设置止损机制")
        
        if win_rate < 0.5:
            recommendations.append("胜率偏低，建议优化入场时机或改进信号过滤")
        
        if not recommendations:
            recommendations.append("策略表现良好，建议继续观察并适时调整参数")
        
        return recommendations
    
    def _get_overall_assessment(self, metrics: Dict[str, float]) -> str:
        """获取总体评估"""
        rating = self._rate_performance(metrics)
        
        if rating["rating"] == "优秀":
            return "策略表现优异，各项指标均衡，风险控制良好"
        elif rating["rating"] == "良好":
            return "策略表现良好，有进一步提升空间"
        elif rating["rating"] == "一般":
            return "策略表现一般，需要优化改进"
        else:
            return "策略表现较差，建议重新设计或大幅调整"
    
    def export_analysis_report(
        self,
        analysis_id: str,
        export_format: str = "json",
        output_dir: str = None
    ) -> str:
        """
        导出分析报告
        
        Args:
            analysis_id: 分析ID
            export_format: 导出格式 (json, html, pdf)
            output_dir: 输出目录
            
        Returns:
            导出文件路径
        """
        if analysis_id not in self.analysis_results:
            raise ValueError(f"分析ID不存在: {analysis_id}")
        
        analysis = self.analysis_results[analysis_id]
        
        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "reports", "performance")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"performance_analysis_{analysis_id}_{timestamp}.{export_format}"
        )
        filepath = os.path.join(output_dir, filename)
        
        try:
            if export_format == "json":
                # 创建可序列化的分析结果副本，移除可视化对象
                serializable_analysis = (
                    self._create_serializable_analysis(analysis)
                )
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(
                        serializable_analysis,
                        f,
                        ensure_ascii=False,
                        indent=2
                    )
            
            elif export_format == "html":
                self._export_html_report(analysis, filepath)
            
            elif export_format == "pdf":
                self._export_pdf_report(analysis, filepath)
            
            logger.info(f"✅ 绩效分析报告已导出: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ 导出绩效分析报告失败: {e}")
            raise
    
    def _export_html_report(self, analysis: Dict[str, Any], filepath: str):
        """导出HTML报告"""
        html_content = self._generate_html_content(analysis)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _export_pdf_report(self, analysis: Dict[str, Any], filepath: str):
        """导出PDF报告"""
        # 简化实现：先导出HTML，然后转换为PDF
        html_filepath = filepath.replace('.pdf', '.html')
        self._export_html_report(analysis, html_filepath)
        
        # 在实际应用中，可以使用wkhtmltopdf或其他工具转换
        logger.warning("PDF导出功能需要额外依赖，目前仅导出HTML格式")
        os.rename(html_filepath, filepath.replace('.pdf', '.html'))
    
    def _create_serializable_analysis(
        self,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建可序列化的分析结果副本
        
        移除不可序列化的可视化对象，用占位符替换
        """
        serializable_analysis = analysis.copy()
        
        # 移除可视化对象，因为它们包含matplotlib图形
        if "visualizations" in serializable_analysis:
            # 保留可视化类型信息但不保留实际图形对象
            serializable_analysis["visualizations"] = {
                key: f"可视化图表: {key}"
                for key in analysis["visualizations"].keys()
            }
        
        return serializable_analysis
    
    def _generate_html_content(self, analysis: Dict[str, Any]) -> str:
        """生成HTML报告内容"""
        strategy_name = analysis["backtest_info"]["strategy_name"]
        period = analysis["backtest_info"]["period"]
        _ = analysis["metrics"]  # 用于消除未使用变量的警告
        report = analysis["report"]
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>绩效分析报告 - {}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f5f5f5; padding: 20px; 
                         border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric-card {{ background: white; border: 1px solid #ddd;
                              border-radius: 5px; padding: 15px;
                              margin: 10px 0; }}
                .metric-value {{ font-size: 1.2em; font-weight: bold; 
                               color: #2c3e50; }}
                .rating-excellent {{ color: #27ae60; }}
                .rating-good {{ color: #f39c12; }}
                .rating-poor {{ color: #e74c3c; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; 
                         border-bottom: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 绩效分析报告</h1>
                <h2>策略: {}</h2>
                <p>回测周期: {}</p>
                <p>分析时间: {}</p>
            </div>
            
            <div class="section">
                <h3>🎯 绩效摘要</h3>
                <div class="metric-card">
        """.format(strategy_name, strategy_name, period, analysis['timestamp'])
        
        # 添加关键指标
        for key, value in report["summary"]["key_metrics"].items():
            html += (
                f'<p><strong>{key}:</strong> '
                f'<span class="metric-value">{value}</span></p>'
            )
        
        html += """
                </div>
                <p><strong>总体评估:</strong> {}</p>
                <p><strong>绩效评级:</strong>
                   <span class="rating-{}">{}</span> ({}分)</p>
            </div>
            
            <div class="section">
                <h3>📈 详细指标</h3>
                <table>
                    <tr><th>指标类别</th><th>指标名称</th><th>数值</th></tr>
        """.format(
            report["summary"]["overall_assessment"],
            report['performance_rating']['rating'],
            report['performance_rating']['rating'],
            report['performance_rating']['total_score']
        )
        
        # 添加详细指标表格
        for category, metrics_dict in report["detailed_metrics"].items():
            for metric_name, value in metrics_dict.items():
                if isinstance(value, float):
                    formatted_value = f"{value:.4f}"
                else:
                    formatted_value = str(value)
                html += (
                    f'<tr><td>{category}</td><td>{metric_name}</td>'
                    f'<td>{formatted_value}</td></tr>'
                )
        
        html += """
                </table>
            </div>
            
            <div class="section">
                <h3>⚠️ 风险评估</h3>
                <div class="metric-card">
        """
        
        for key, value in report["risk_assessment"].items():
            html += f'<p><strong>{key}:</strong> {value}</p>'
        
        html += """
                </div>
            </div>
            
            <div class="section">
                <h3>💡 改进建议</h3>
                <ul>
        """
        
        for recommendation in report["recommendations"]:
            html += f'<li>{recommendation}</li>'
        
        html += """
                </ul>
            </div>
            
            <div class="section">
                <p><em>注：此报告由量化平台绩效分析系统自动生成</em></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def get_analysis_result(self, analysis_id: str) -> Dict[str, Any]:
        """获取分析结果"""
        if analysis_id not in self.analysis_results:
            raise ValueError(f"分析ID不存在: {analysis_id}")
        
        return self.analysis_results[analysis_id]
    
    def get_all_analysis_results(self) -> List[Dict[str, Any]]:
        """获取所有分析结果"""
        return list(self.analysis_results.values())


# 全局绩效分析器实例
_global_performance_analyzer = None


def get_performance_analyzer(use_plotly: bool = None) -> PerformanceAnalyzer:
    """获取全局绩效分析器实例"""
    global _global_performance_analyzer
    
    if _global_performance_analyzer is None:
        _global_performance_analyzer = PerformanceAnalyzer(use_plotly)
    
    return _global_performance_analyzer


def test_performance_analyzer():
    """测试绩效分析器"""
    print("=" * 70)
    print("测试绩效分析系统")
    print("=" * 70)
    
    try:
        # 创建绩效分析器
        analyzer = PerformanceAnalyzer()
        
        # 创建模拟回测结果
        dates = pd.date_range('2020-01-01', periods=252, freq='D')
        np.random.seed(42)
        
        # 策略收益（略好于基准）
        strategy_returns = pd.Series(
            np.random.normal(0.001, 0.02, 252), index=dates
        )
        benchmark_returns = pd.Series(
            np.random.normal(0.0008, 0.018, 252), index=dates
        )
        
        # 创建模拟回测结果
        backtest_result = {
            "strategy_name": "测试TopK策略",
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            "initial_capital": 1000000,
            "benchmark": "SH000300",
            "result": {
                "success": True,
                "returns": strategy_returns.tolist(),
                "dates": dates.strftime('%Y-%m-%d').tolist(),
                "nav_curve": (1 + strategy_returns).cumprod().tolist()
            }
        }
        
        print("🚀 开始绩效分析...")
        
        # 运行绩效分析
        analysis_result = analyzer.analyze_backtest(
            backtest_result, benchmark_returns
        )
        
        if "analysis_id" in analysis_result:
            print("✅ 绩效分析完成!")
            
            # 显示关键指标
            metrics = analysis_result["metrics"]
            print(f"📈 累计收益: {metrics['cumulative_return']:.2%}")
            print(f"📊 年化收益: {metrics['annual_return']:.2%}")
            print(f"⚡ 夏普比率: {metrics['sharpe_ratio']:.2f}")
            print(f"📉 最大回撤: {metrics['max_drawdown']:.2%}")
            print(f"🎯 信息比率: {metrics['information_ratio']:.2f}")
            print(f"📊 胜率: {metrics['win_rate']:.2%}")
            
            # 显示绩效评级
            rating = analysis_result["report"]["performance_rating"]
            print(f"🏆 绩效评级: {rating['rating']} ({rating['total_score']}分)")
            
            # 测试导出功能
            export_path = analyzer.export_analysis_report(
                analysis_result["analysis_id"], "json"
            )
            print(f"💾 分析报告已导出: {export_path}")
            
        else:
            print(f"❌ 绩效分析失败: {analysis_result.get('error', '未知错误')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 绩效分析器测试失败: {e}")
        return False


if __name__ == "__main__":
    # 运行测试
    success = test_performance_analyzer()
    
    if success:
        print("\n🚀 绩效分析系统测试完成!")
    else:
        print("\n⚠️ 绩效分析系统需要进一步调试")