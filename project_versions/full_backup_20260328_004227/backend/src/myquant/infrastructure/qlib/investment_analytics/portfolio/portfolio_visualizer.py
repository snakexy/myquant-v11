"""
投资组合可视化器 - Portfolio Visualizer

提供专业的投资组合可视化功能，包括净值曲线、持仓分布图、风险贡献图等。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional, Tuple
import warnings
from matplotlib.figure import Figure
import io
import base64


class PortfolioVisualizer:
    """
    投资组合可视化器
    
    功能：
    - 净值曲线和基准对比
    - 持仓分布图（饼图、柱状图）
    - 风险贡献图
    - 绩效归因图
    - 回撤分析图
    - 有效前沿图
    """
    
    def __init__(self, style: str = 'seaborn'):
        """
        初始化可视化器
        
        Args:
            style: 图表样式，'seaborn' 或 'matplotlib'
        """
        self.style = style
        self._setup_plot_style()
        
    def _setup_plot_style(self) -> None:
        """设置图表样式"""
        if self.style == 'seaborn':
            plt.style.use('seaborn-v0_8-whitegrid')
            sns.set_palette("husl")
        else:
            plt.style.use('ggplot')
            
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False
        
    def plot_equity_curve(
        self,
        portfolio_values: pd.Series,
        benchmark_values: Optional[pd.Series] = None,
        title: str = "投资组合净值曲线",
        figsize: Tuple[int, int] = (12, 6)
    ) -> Figure:
        """
        绘制净值曲线
        
        Args:
            portfolio_values: 投资组合净值序列
            benchmark_values: 基准净值序列（可选）
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制组合净值
        ax.plot(portfolio_values.index, portfolio_values.values, 
                label='投资组合', linewidth=2, color='blue')
        
        # 绘制基准净值（如果有）
        if benchmark_values is not None:
            ax.plot(benchmark_values.index, benchmark_values.values,
                    label='基准', linewidth=2, color='red', alpha=0.7)
            
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('日期')
        ax.set_ylabel('净值')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 设置x轴格式
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_drawdown(
        self,
        portfolio_values: pd.Series,
        title: str = "投资组合回撤分析",
        figsize: Tuple[int, int] = (12, 6)
    ) -> Figure:
        """
        绘制回撤分析图
        
        Args:
            portfolio_values: 投资组合净值序列
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        # 计算回撤
        rolling_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - rolling_max) / rolling_max
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, 
                                       gridspec_kw={'height_ratios': [2, 1]})
        
        # 净值曲线
        ax1.plot(
            portfolio_values.index, portfolio_values.values,
            label='投资组合净值', linewidth=2, color='blue'
        )
        ax1.set_title('净值曲线', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 回撤图
        ax2.fill_between(
            drawdown.index, drawdown.values, 0,
            alpha=0.3, color='red', label='回撤'
        )
        ax2.plot(drawdown.index, drawdown.values, linewidth=1, color='red')
        ax2.set_title('回撤分析', fontweight='bold')
        ax2.set_ylabel('回撤比例')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 最大回撤标注
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()
        ax2.axhline(y=max_dd, color='darkred', linestyle='--', alpha=0.7)
        ax2.annotate(
            f'最大回撤: {max_dd:.2%}',
            xy=(max_dd_date, max_dd),
            xytext=(max_dd_date, max_dd * 0.8),
            arrowprops=dict(arrowstyle='->', color='darkred')
        )
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def plot_holdings_allocation(
        self,
        holdings: pd.DataFrame,
        top_n: int = 10,
        by: str = 'weight',
        title: str = "持仓分布",
        figsize: Tuple[int, int] = (12, 8)
    ) -> Figure:
        """
        绘制持仓分布图
        
        Args:
            holdings: 持仓数据，包含股票代码和权重
            top_n: 显示前N个持仓
            by: 按哪个字段排序，'weight' 或 'sector'
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        if by == 'sector' and 'sector' in holdings.columns:
            # 按行业分组
            sector_allocation = holdings.groupby('sector')['weight'].sum()
            data = sector_allocation.sort_values(ascending=False)
            plot_type = 'pie'
        else:
            # 按权重排序
            data = holdings.nlargest(top_n, 'weight')['weight']
            plot_type = 'bar'
            
        fig, ax = plt.subplots(figsize=figsize)
        
        if plot_type == 'pie':
            # 饼图
            wedges, texts, autotexts = ax.pie(
                data.values, 
                labels=data.index,
                autopct='%1.1f%%',
                startangle=90
            )
            ax.set_title(f'{title} - 按行业', fontweight='bold')
            
            # 美化文本
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                
        else:
            # 柱状图
            ax.bar(
                range(len(data)), data.values * 100,
                color=plt.cm.Set3(np.linspace(0, 1, len(data)))
            )
            ax.set_xticks(range(len(data)))
            ax.set_xticklabels(data.index, rotation=45, ha='right')
            ax.set_ylabel('权重 (%)')
            ax.set_title(f'{title} - 前{top_n}大持仓', fontweight='bold')
            
            # 在柱子上添加数值标签
            for i, v in enumerate(data.values):
                ax.text(
                    i, v * 100 + 0.5, f'{v*100:.1f}%',
                    ha='center', va='bottom', fontweight='bold'
                )
                
        plt.tight_layout()
        return fig
    
    def plot_risk_contribution(
        self,
        weights: pd.Series,
        cov_matrix: pd.DataFrame,
        top_n: int = 10,
        title: str = "风险贡献分析",
        figsize: Tuple[int, int] = (12, 6)
    ) -> Figure:
        """
        绘制风险贡献图
        
        Args:
            weights: 资产权重
            cov_matrix: 协方差矩阵
            top_n: 显示前N个资产
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        # 计算边际风险贡献
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        marginal_risk_contrib = (
            weights * np.dot(cov_matrix, weights) / portfolio_variance
        )
        
        # 选择前N个资产
        top_contrib = marginal_risk_contrib.nlargest(top_n)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # 风险贡献饼图
        wedges, texts, autotexts = ax1.pie(
            top_contrib.values,
            labels=top_contrib.index,
            autopct='%1.1f%%',
            startangle=90
        )
        ax1.set_title('风险贡献分布', fontweight='bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            
        # 权重 vs 风险贡献散点图
        total_weights = weights[top_contrib.index]
        ax2.scatter(
            total_weights * 100, top_contrib.values * 100,
            s=100, alpha=0.7
        )
        
        # 添加资产标签
        for i, asset in enumerate(top_contrib.index):
            ax2.annotate(
                asset,
                (total_weights[asset] * 100, top_contrib[asset] * 100),
                xytext=(5, 5), textcoords='offset points',
                fontsize=8
            )
            
        ax2.plot([0, 100], [0, 100], 'r--', alpha=0.5, label='等比例线')
        ax2.set_xlabel('权重 (%)')
        ax2.set_ylabel('风险贡献 (%)')
        ax2.set_title('权重 vs 风险贡献', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def plot_performance_attribution(
        self,
        attribution_data: pd.DataFrame,
        title: str = "绩效归因分析",
        figsize: Tuple[int, int] = (12, 8)
    ) -> Figure:
        """
        绘制绩效归因图
        
        Args:
            attribution_data: 归因数据，包含超额收益等信息
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
        
        # 超额收益时序图
        if 'excess_return' in attribution_data.columns:
            ax1.plot(
                attribution_data.index,
                attribution_data['excess_return'].cumsum() * 100,
                linewidth=2, color='green', label='累计超额收益'
            )
            ax1.set_ylabel('累计超额收益 (%)')
            ax1.set_title('超额收益时序图', fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
        # 月度超额收益柱状图
        if 'excess_return' in attribution_data.columns:
            monthly_excess = (
                attribution_data['excess_return'].resample('M').sum()
            )
            colors = ['green' if x >= 0 else 'red' for x in monthly_excess]
            ax2.bar(
                monthly_excess.index, monthly_excess.values * 100,
                color=colors, alpha=0.7
            )
            ax2.set_ylabel('月度超额收益 (%)')
            ax2.set_title('月度超额收益', fontweight='bold')
            ax2.grid(True, alpha=0.3)
            
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def plot_efficient_frontier(
        self,
        frontier_data: pd.DataFrame,
        optimal_point: Optional[Dict] = None,
        title: str = "有效前沿",
        figsize: Tuple[int, int] = (10, 6)
    ) -> Figure:
        """
        绘制有效前沿图
        
        Args:
            frontier_data: 有效前沿数据
            optimal_point: 最优点信息（可选）
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制有效前沿
        ax.plot(frontier_data['expected_volatility'] * 100,
                frontier_data['expected_return'] * 100,
                linewidth=2, color='blue', label='有效前沿')
        
        # 标记最优点（如果有）
        if optimal_point:
            ax.scatter(
                optimal_point['volatility'] * 100,
                optimal_point['return'] * 100,
                s=100, color='red', marker='*',
                label=optimal_point.get('label', '最优点')
            )
                      
        ax.set_xlabel('预期波动率 (%)')
        ax.set_ylabel('预期收益率 (%)')
        ax.set_title(title, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_correlation_heatmap(
        self,
        returns: pd.DataFrame,
        title: str = "资产相关性热图",
        figsize: Tuple[int, int] = (10, 8)
    ) -> Figure:
        """
        绘制资产相关性热图
        
        Args:
            returns: 资产收益率数据
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        # 计算相关性矩阵
        corr_matrix = returns.corr()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制热图
        sns.heatmap(
            corr_matrix,
            annot=True,
            cmap='coolwarm',
            center=0,
            square=True,
            ax=ax
        )
        
        ax.set_title(title, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def create_comprehensive_report(
        self,
        portfolio_analyzer,
        portfolio_optimizer,
        save_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        创建综合可视化报告
        
        Args:
            portfolio_analyzer: 投资组合分析器实例
            portfolio_optimizer: 投资组合优化器实例
            save_path: 保存路径（可选）
            
        Returns:
            Dict[str, str]: 包含图表base64编码的字典
        """
        report_images = {}
        
        try:
            # 1. 净值曲线
            fig1 = self.plot_equity_curve(
                portfolio_analyzer._portfolio_values,
                getattr(portfolio_analyzer, '_benchmark_values', None)
            )
            report_images['equity_curve'] = self._fig_to_base64(fig1)
            plt.close(fig1)
            
            # 2. 回撤分析
            fig2 = self.plot_drawdown(portfolio_analyzer._portfolio_values)
            report_images['drawdown'] = self._fig_to_base64(fig2)
            plt.close(fig2)
            
            # 3. 持仓分布（如果有持仓数据）
            if portfolio_analyzer._holdings is not None:
                fig3 = self.plot_holdings_allocation(
                    portfolio_analyzer._holdings
                )
                report_images['holdings'] = self._fig_to_base64(fig3)
                plt.close(fig3)
                
            # 4. 有效前沿（如果有优化数据）
            if (portfolio_optimizer._returns is not None
                    and portfolio_optimizer._cov_matrix is not None):
                frontier_data = (
                    portfolio_optimizer.calculate_efficient_frontier()
                )
                fig4 = self.plot_efficient_frontier(frontier_data)
                report_images['efficient_frontier'] = self._fig_to_base64(fig4)
                plt.close(fig4)
                
            # 5. 相关性热图
            if portfolio_optimizer._returns is not None:
                fig5 = self.plot_correlation_heatmap(
                    portfolio_optimizer._returns
                )
                report_images['correlation'] = self._fig_to_base64(fig5)
                plt.close(fig5)
                
        except Exception as e:
            warnings.warn(f"生成可视化报告时出错: {e}")
            
        return report_images
    
    def _fig_to_base64(self, fig: Figure) -> str:
        """
        将matplotlib图表转换为base64字符串
        
        Args:
            fig: matplotlib图表对象
            
        Returns:
            str: base64编码的图片字符串
        """
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        return img_str