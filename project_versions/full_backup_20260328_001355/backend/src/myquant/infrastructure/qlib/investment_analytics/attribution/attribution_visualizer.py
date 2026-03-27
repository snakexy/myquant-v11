"""
归因可视化器 - Attribution Visualizer

提供归因分析的专业可视化功能，包括归因瀑布图、贡献度饼图、风险归因图等。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional, Tuple
from matplotlib.figure import Figure
import warnings


class AttributionVisualizer:
    """
    归因可视化器
    
    功能：
    - 绩效归因瀑布图
    - 风险归因饼图
    - 多期归因时序图
    - 因子贡献度热图
    - VaR归因分解图
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
        
    def plot_attribution_waterfall(
        self,
        attribution_results: Dict[str, float],
        title: str = "绩效归因瀑布图",
        figsize: Tuple[int, int] = (12, 8)
    ) -> Figure:
        """
        绘制绩效归因瀑布图
        
        Args:
            attribution_results: 归因分析结果
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 提取归因数据
        components = []
        values = []
        colors = []
        
        # 基准收益率
        if 'benchmark_return' in attribution_results:
            components.append('基准收益率')
            values.append(attribution_results['benchmark_return'])
            colors.append('lightgray')
            
        # 配置效应
        if 'allocation_effect' in attribution_results:
            components.append('配置效应')
            values.append(attribution_results['allocation_effect'])
            alloc_color = (
                'blue' if attribution_results['allocation_effect'] >= 0
                else 'red'
            )
            colors.append(alloc_color)
            
        # 选择效应
        if 'selection_effect' in attribution_results:
            components.append('选择效应')
            values.append(attribution_results['selection_effect'])
            select_color = (
                'green' if attribution_results['selection_effect'] >= 0
                else 'red'
            )
            colors.append(select_color)
            
        # 交互效应
        if 'interaction_effect' in attribution_results:
            components.append('交互效应')
            values.append(attribution_results['interaction_effect'])
            interact_color = (
                'orange' if attribution_results['interaction_effect'] >= 0
                else 'red'
            )
            colors.append(interact_color)
            
        # 总超额收益
        if 'total_active_return' in attribution_results:
            components.append('总超额收益')
            values.append(attribution_results['total_active_return'])
            colors.append('purple')
            
        # 计算累积值
        cumulative = [0]
        for i, value in enumerate(values):
            cumulative.append(cumulative[-1] + value)
            
        # 绘制瀑布图
        bars = ax.bar(
            range(len(components)),
            values,
            bottom=cumulative[:-1],
            color=colors,
            alpha=0.7
        )
        
        # 添加数值标签
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            y_pos = cumulative[i] + height / 2
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                y_pos,
                f'{value:.2%}',
                ha='center',
                va='center',
                fontweight='bold',
                fontsize=10
            )
            
        # 设置图表属性
        ax.set_xticks(range(len(components)))
        ax.set_xticklabels(components, rotation=45, ha='right')
        ax.set_ylabel('收益率贡献')
        ax.set_title(title, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # 添加基准线
        ax.axhline(y=0, color='black', linewidth=0.8)
        
        plt.tight_layout()
        return fig
    
    def plot_factor_contributions(
        self,
        factor_contributions: Dict[str, float],
        title: str = "因子贡献度分析",
        figsize: Tuple[int, int] = (10, 6)
    ) -> Figure:
        """
        绘制因子贡献度图
        
        Args:
            factor_contributions: 因子贡献度数据
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # 饼图 - 相对贡献
        contributions_series = pd.Series(factor_contributions)
        positive_contributions = contributions_series[contributions_series > 0]
        # negative_contributions 用于未来扩展负向贡献分析
        _ = contributions_series[contributions_series < 0]
        
        if len(positive_contributions) > 0:
            wedges, texts, autotexts = ax1.pie(
                positive_contributions.values,
                labels=positive_contributions.index,
                autopct='%1.1f%%',
                startangle=90
            )
            ax1.set_title('正向因子贡献', fontweight='bold')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                
        # 柱状图 - 绝对贡献
        colors = ['green' if x >= 0 else 'red' for x in contributions_series]
        bars = ax2.bar(
            range(len(contributions_series)),
            contributions_series.values * 100,
            color=colors,
            alpha=0.7
        )
        
        ax2.set_xticks(range(len(contributions_series)))
        ax2.set_xticklabels(
            contributions_series.index, rotation=45, ha='right'
        )
        ax2.set_ylabel('贡献度 (%)')
        ax2.set_title('因子绝对贡献', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 添加数值标签
        for i, (bar, value) in enumerate(zip(bars, contributions_series)):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height + (0.5 if height >= 0 else -5),
                f'{value*100:.2f}%',
                ha='center',
                va='bottom' if height >= 0 else 'top',
                fontweight='bold',
                fontsize=8
            )
            
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def plot_risk_attribution(
        self,
        risk_attribution_results: Dict,
        title: str = "风险归因分析",
        figsize: Tuple[int, int] = (12, 8)
    ) -> Figure:
        """
        绘制风险归因图
        
        Args:
            risk_attribution_results: 风险归因结果
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # 1. 风险贡献饼图
        if 'factor_risk_contributions' in risk_attribution_results:
            factor_risks = (
                risk_attribution_results['factor_risk_contributions']
            )
            specific_risk = risk_attribution_results.get('specific_risk', 0)
            
            # 合并因子风险和特质风险
            all_risks = factor_risks.copy()
            all_risks['特质风险'] = specific_risk
            
            wedges, texts, autotexts = ax1.pie(
                all_risks.values(),
                labels=all_risks.keys(),
                autopct='%1.1f%%',
                startangle=90
            )
            ax1.set_title('风险贡献分布', fontweight='bold')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                
        # 2. 边际风险贡献
        if 'marginal_risk_contributions' in risk_attribution_results:
            marginal_risks = (
                risk_attribution_results['marginal_risk_contributions']
            )
            top_assets = pd.Series(marginal_risks).nlargest(10)
            
            colors = plt.cm.viridis(np.linspace(0, 1, len(top_assets)))
            bars = ax2.bar(
                range(len(top_assets)),
                top_assets.values * 100,
                color=colors
            )
            
            ax2.set_xticks(range(len(top_assets)))
            ax2.set_xticklabels(top_assets.index, rotation=45, ha='right')
            ax2.set_ylabel('边际风险贡献 (%)')
            ax2.set_title('前10大边际风险贡献', fontweight='bold')
            ax2.grid(True, alpha=0.3)
            
        # 3. VaR分解
        if 'var_attribution' in risk_attribution_results:
            var_data = risk_attribution_results['var_attribution']
            if 'var_decomposition' in var_data:
                var_decomp = var_data['var_decomposition']
                
                components = list(var_decomp.keys())
                values = list(var_decomp.values())
                
                colors = ['lightblue', 'lightcoral', 'lightgreen']
                bars = ax3.bar(components, values, color=colors, alpha=0.7)
                ax3.set_ylabel('VaR贡献')
                ax3.set_title('VaR分解', fontweight='bold')
                ax3.grid(True, alpha=0.3)
                
                # 添加数值标签
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax3.text(
                        bar.get_x() + bar.get_width() / 2,
                        height + 0.01,
                        f'{value:.3f}',
                        ha='center',
                        va='bottom',
                        fontweight='bold'
                    )
                    
        # 4. 风险预算偏差
        if 'risk_budget_analysis' in risk_attribution_results:
            risk_budget = risk_attribution_results['risk_budget_analysis']
            if 'risk_budget_deviations' in risk_budget:
                deviations = risk_budget['risk_budget_deviations']
                top_deviations = pd.Series(deviations).nlargest(8)
                
                colors = ['red' if x > 0 else 'blue' for x in top_deviations]
                bars = ax4.bar(
                    range(len(top_deviations)),
                    top_deviations.values * 100,
                    color=colors,
                    alpha=0.7
                )
                
                ax4.set_xticks(range(len(top_deviations)))
                ax4.set_xticklabels(
                    top_deviations.index, rotation=45, ha='right'
                )
                ax4.set_ylabel('风险预算偏差 (%)')
                ax4.set_title('风险预算偏差分析', fontweight='bold')
                ax4.grid(True, alpha=0.3)
                ax4.axhline(y=0, color='black', linewidth=0.8)
                
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def plot_multiperiod_attribution(
        self,
        multiperiod_data: pd.DataFrame,
        title: str = "多期归因分析",
        figsize: Tuple[int, int] = (14, 10)
    ) -> Figure:
        """
        绘制多期归因分析图
        
        Args:
            multiperiod_data: 多期归因数据
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # 1. 超额收益时序图
        if 'total_active_return' in multiperiod_data.columns:
            cumulative_excess = (
                1 + multiperiod_data['total_active_return']
            ).cumprod() - 1
            
            ax1.plot(
                multiperiod_data.index,
                cumulative_excess * 100,
                linewidth=2,
                color='blue',
                label='累计超额收益'
            )
            ax1.set_ylabel('累计超额收益 (%)')
            ax1.set_title('超额收益时序图', fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
        # 2. 归因效应堆叠面积图
        if all(col in multiperiod_data.columns for col in [
            'allocation_effect', 'selection_effect', 'interaction_effect'
        ]):
            attribution_components = multiperiod_data[[
                'allocation_effect', 'selection_effect', 'interaction_effect'
            ]].cumsum()
            
            ax2.stackplot(
                multiperiod_data.index,
                attribution_components.T,
                labels=['配置效应', '选择效应', '交互效应'],
                alpha=0.7
            )
            ax2.set_ylabel('累计归因贡献')
            ax2.set_title('归因效应累积贡献', fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
        # 3. 月度归因贡献热图
        if 'allocation_effect' in multiperiod_data.columns:
            monthly_data = multiperiod_data.resample('M').sum()
            attribution_matrix = monthly_data[[
                'allocation_effect', 'selection_effect', 'interaction_effect'
            ]].T
            
            im = ax3.imshow(
                attribution_matrix.values * 100,
                cmap='RdYlGn',
                aspect='auto'
            )
            ax3.set_xticks(range(len(monthly_data)))
            ax3.set_xticklabels(
                [d.strftime('%Y-%m') for d in monthly_data.index],
                rotation=45
            )
            ax3.set_yticks(range(3))
            ax3.set_yticklabels(['配置', '选择', '交互'])
            ax3.set_title('月度归因贡献热图 (%)', fontweight='bold')
            
            # 添加颜色条
            plt.colorbar(im, ax=ax3)
            
        # 4. 滚动归因稳定性
        if 'total_active_return' in multiperiod_data.columns:
            rolling_window = min(12, len(multiperiod_data) // 4)
            if rolling_window > 1:
                rolling_attribution = multiperiod_data.rolling(
                    rolling_window
                ).mean()
                
                ax4.plot(
                    rolling_attribution.index,
                    rolling_attribution['allocation_effect'] * 100,
                    label='配置效应',
                    linewidth=2
                )
                ax4.plot(
                    rolling_attribution.index,
                    rolling_attribution['selection_effect'] * 100,
                    label='选择效应',
                    linewidth=2
                )
                ax4.set_ylabel(f'{rolling_window}期滚动平均 (%)')
                ax4.set_title('归因效应稳定性分析', fontweight='bold')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
                
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def plot_attribution_quality(
        self,
        quality_metrics: Dict[str, float],
        title: str = "归因质量分析",
        figsize: Tuple[int, int] = (10, 6)
    ) -> Figure:
        """
        绘制归因质量分析图
        
        Args:
            quality_metrics: 归因质量指标
            title: 图表标题
            figsize: 图表尺寸
            
        Returns:
            Figure: matplotlib图表对象
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # 1. 质量指标雷达图
        metrics_to_plot = {
            k: v for k, v in quality_metrics.items() 
            if isinstance(v, (int, float)) and 0 <= v <= 1
        }
        
        if metrics_to_plot:
            categories = list(metrics_to_plot.keys())
            values = list(metrics_to_plot.values())
            
            # 完成雷达图
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
            values = np.concatenate((values, [values[0]]))
            angles = np.concatenate((angles, [angles[0]]))
            categories = categories + [categories[0]]
            
            ax1.plot(angles, values, 'o-', linewidth=2)
            ax1.fill(angles, values, alpha=0.25)
            ax1.set_thetagrids(angles[:-1] * 180/np.pi, categories[:-1])
            ax1.set_ylim(0, 1)
            ax1.set_title('归因质量雷达图', fontweight='bold')
            
        # 2. 质量指标柱状图
        all_metrics = {
            k: v for k, v in quality_metrics.items() 
            if isinstance(v, (int, float))
        }
        
        if all_metrics:
            metrics_series = pd.Series(all_metrics)
            colors = plt.cm.viridis(np.linspace(0, 1, len(metrics_series)))
            
            bars = ax2.bar(
                range(len(metrics_series)),
                metrics_series.values,
                color=colors
            )
            
            ax2.set_xticks(range(len(metrics_series)))
            ax2.set_xticklabels(
                metrics_series.index, rotation=45, ha='right'
            )
            ax2.set_ylabel('指标值')
            ax2.set_title('归因质量指标', fontweight='bold')
            ax2.grid(True, alpha=0.3)
            
            # 添加数值标签
            for bar, value in zip(bars, metrics_series.values):
                height = bar.get_height()
                ax2.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 0.01,
                    f'{value:.3f}',
                    ha='center',
                    va='bottom',
                    fontweight='bold'
                )
                
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    def create_comprehensive_attribution_report(
        self,
        performance_attribution,
        risk_attribution,
        multiperiod_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Figure]:
        """
        创建综合归因分析报告
        
        Args:
            performance_attribution: 绩效归因分析器实例
            risk_attribution: 风险归因分析器实例
            multiperiod_data: 多期归因数据（可选）
            
        Returns:
            Dict[str, Figure]: 包含图表对象的字典
        """
        report_figures = {}
        
        try:
            # 1. 绩效归因报告
            perf_report = performance_attribution.generate_attribution_report()
            if 'brinson_attribution' in perf_report:
                brinson_data = perf_report['brinson_attribution']
                
                # 绩效归因瀑布图
                fig1 = self.plot_attribution_waterfall(brinson_data)
                report_figures['performance_waterfall'] = fig1
                
            # 2. 风险归因报告
            risk_report = risk_attribution.generate_risk_report()
            
            # 风险归因综合图
            fig2 = self.plot_risk_attribution(risk_report)
            report_figures['risk_attribution'] = fig2
            
            # 3. 多期归因分析（如果有数据）
            if multiperiod_data is not None:
                fig3 = self.plot_multiperiod_attribution(multiperiod_data)
                report_figures['multiperiod_analysis'] = fig3
                
            # 4. 因子贡献分析
            factor_attrib_available = (
                'factor_attribution' in perf_report and
                'factor_contributions' in perf_report['factor_attribution']
            )
            if factor_attrib_available:
                factor_data = perf_report['factor_attribution']
                fig4 = self.plot_factor_contributions(
                    factor_data['factor_contributions']
                )
                report_figures['factor_contributions'] = fig4
                
            # 5. 归因质量分析
            if multiperiod_data is not None:
                quality_metrics = (
                    performance_attribution.calculate_attribution_quality(
                        multiperiod_data
                    )
                )
                fig5 = self.plot_attribution_quality(quality_metrics)
                report_figures['attribution_quality'] = fig5
                
        except Exception as e:
            warnings.warn(f"生成归因可视化报告时出错: {e}")
            
        return report_figures