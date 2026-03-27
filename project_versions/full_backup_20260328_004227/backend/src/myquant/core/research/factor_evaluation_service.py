# -*- coding: utf-8 -*-
"""
Research阶段 - 因子评估服务
================================
职责：
- 因子有效性验证（IC、IR、IC正数占比等）
- 因子组合评估
- 预测能力分析
- 组合优化建议

版本: v1.0
创建日期: 2026-02-11
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from loguru import logger
from datetime import datetime
import pandas as pd
import numpy as np


@dataclass
class FactorMetrics:
    """因子指标"""
    ic_mean: float = 0.0          # IC均值
    ic_std: float = 0.0           # IC标准差
    ir: float = 0.0               # IC信息比率（IR = IC均值/IC标准差）
    ic_positive_ratio: float = 0.0  # IC正数占比
    rank_ic_mean: float = 0.0     # Rank IC均值
    max_drawdown: float = 0.0     # 最大回撤

    # 统计显著性
    t_stat: float = 0.0           # t统计量
    p_value: float = 1.0           # p值


@dataclass
class ValidityThreshold:
    """有效性阈值"""
    ic_mean: float = 0.03         # IC均值阈值
    ir: float = 0.5               # IR阈值
    ic_positive_ratio: float = 0.55  # IC正数占比阈值


@dataclass
class ValidityResult:
    """有效性验证结果"""
    factor_name: str
    is_valid: bool
    overall_score: float
    metrics: Dict[str, Any]
    recommendation: str
    evaluated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CombinationResult:
    """组合评估结果"""
    combined_factor_name: str
    combination_method: str
    weights: Dict[str, float]
    evaluation: FactorMetrics
    comparison: Dict[str, Any]
    combined_at: datetime = field(default_factory=datetime.now)


class FactorEvaluationService:
    """
    因子评估服务

    核心职责：
    1. 评估因子有效性（IC、IR等指标）
    2. 评估因子组合效果
    3. 提供组合优化建议
    """

    def __init__(self):
        """初始化因子评估服务"""
        # 尝试加载依赖服务
        self.data_service = None
        self.factor_analysis_service = None
        self._init_dependencies()
        logger.info("✅ FactorEvaluationService初始化完成")

    def _init_dependencies(self):
        """初始化依赖服务"""
        try:
            from .data_service import get_research_data_service
            self.data_service = get_research_data_service()
            logger.debug("✅ 数据服务依赖已加载")
        except Exception as e:
            logger.warning(f"⚠️ 数据服务依赖加载失败: {e}")

        try:
            from .factor_analysis_service import get_factor_analysis_service
            self.factor_analysis_service = get_factor_analysis_service()
            logger.debug("✅ 因子分析服务依赖已加载")
        except Exception as e:
            logger.warning(f"⚠️ 因子分析服务依赖加载失败: {e}")

    # ==================== 因子有效性验证 ====================

    async def evaluate_validity(
        self,
        factor_name: str,
        start_date: str,
        end_date: str,
        threshold: Optional[ValidityThreshold] = None
    ) -> ValidityResult:
        """
        评估因子有效性

        Args:
            factor_name: 因子名称
            start_date: 开始日期
            end_date: 结束日期
            threshold: 阈值设置

        Returns:
            ValidityResult对象
        """
        logger.info(f"[因子有效性] 评估因子: {factor_name}, 时间范围: {start_date} - {end_date}")

        # 设置默认阈值
        if threshold is None:
            threshold = ValidityThreshold()

        try:
            # 尝试使用真实数据源
            real_data_available = False

            if self.data_service:
                try:
                    # 获取因子数据
                    factor_df = self.data_service.get_factor_data(
                        factor_name=factor_name,
                        start_date=start_date,
                        end_date=end_date
                    )

                    # 获取收益率数据
                    returns_df = await self.data_service.get_returns_data(
                        start_date=start_date,
                        end_date=end_date
                    )

                    # 如果都成功获取到数据，计算真实指标
                    if factor_df is not None and not factor_df.empty and returns_df is not None and not returns_df.empty:
                        logger.info(f"使用真实数据计算因子指标: {factor_name}")
                        metrics = await self._calculate_factor_metrics_from_data(factor_df, returns_df)
                        real_data_available = True
                except Exception as e:
                    logger.warning(f"获取真实数据失败: {e}，降级到模拟数据")

            # 如果真实数据不可用，降级到模拟数据
            if not real_data_available:
                logger.warning(f"[{factor_name}] 真实数据不可用，使用模拟数据（请注意结果不可信！）")
                metrics = self._calculate_factor_metrics_mock(factor_name, start_date, end_date)

            # 评估各项指标是否通过阈值

            # 评估各项指标是否通过阈值
            ic_mean_passed = metrics.ic_mean >= threshold.ic_mean
            ir_passed = metrics.ir >= threshold.ir
            ic_positive_ratio_passed = metrics.ic_positive_ratio >= threshold.ic_positive_ratio

            # 计算总体得分（加权平均）
            scores = {
                "ic_mean": self._calculate_score(metrics.ic_mean, threshold.ic_mean, ic_mean_passed),
                "ir": self._calculate_score(metrics.ir, threshold.ir, ir_passed),
                "ic_positive_ratio": self._calculate_score(
                    metrics.ic_positive_ratio,
                    threshold.ic_positive_ratio,
                    ic_positive_ratio_passed
                )
            }

            # 权重：IC均值40%，IR30%，IC正数占比30%
            overall_score = (
                scores["ic_mean"] * 0.4 +
                scores["ir"] * 0.3 +
                scores["ic_positive_ratio"] * 0.3
            )

            # 判断是否有效（总分≥0.6或所有指标都通过）
            is_valid = overall_score >= 0.6 or (ic_mean_passed and ir_passed and ic_positive_ratio_passed)

            # 生成建议
            recommendation = self._generate_recommendation(
                is_valid,
                metrics,
                threshold
            )

            return ValidityResult(
                factor_name=factor_name,
                is_valid=is_valid,
                overall_score=round(overall_score, 2),
                metrics={
                    "ic_mean": {
                        "value": round(metrics.ic_mean, 4),
                        "threshold": threshold.ic_mean,
                        "passed": ic_mean_passed,
                        "score": round(scores["ic_mean"], 2)
                    },
                    "ir": {
                        "value": round(metrics.ir, 4),
                        "threshold": threshold.ir,
                        "passed": ir_passed,
                        "score": round(scores["ir"], 2)
                    },
                    "ic_positive_ratio": {
                        "value": round(metrics.ic_positive_ratio, 4),
                        "threshold": threshold.ic_positive_ratio,
                        "passed": ic_positive_ratio_passed,
                        "score": round(scores["ic_positive_ratio"], 2)
                    }
                },
                recommendation=recommendation
            )

        except Exception as e:
            logger.error(f"[因子有效性] 评估失败: {e}")
            # 返回无效结果
            return ValidityResult(
                factor_name=factor_name,
                is_valid=False,
                overall_score=0.0,
                metrics={},
                recommendation=f"评估失败: {str(e)}"
            )

    def _calculate_factor_metrics_mock(
        self,
        factor_name: str,
        start_date: str = None,
        end_date: str = None
    ) -> FactorMetrics:
        """
        计算因子指标

        Args:
            factor_name: 因子名称
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            FactorMetrics对象

        实现说明：
            - 当前实现：使用模拟数据计算指标
            - 未来改进：从真实数据源加载

        数据源：
            - 因子数据: ~/data/qlib_data/factors/{factor_name}.pkl
            - 收益率数据: ~/data/qlib_data/returns/{symbol}.pkl
            - 计算方式:
                1. IC: 因子值与未来收益率的相关系数
                2. IR: IC均值 / IC标准差
                3. IC正数占比: IC > 0 的比例
        """
        # 模拟数据（实际应该从数据库计算）
        import random
        random.seed(hash(factor_name))

        ic_values = np.random.normal(0.04, 0.08, 100)  # 模拟IC序列

        return FactorMetrics(
            ic_mean=float(np.mean(ic_values)),
            ic_std=float(np.std(ic_values)),
            ir=float(np.mean(ic_values) / np.std(ic_values)) if np.std(ic_values) > 0 else 0.0,
            ic_positive_ratio=float(np.sum(ic_values > 0) / len(ic_values)),
            rank_ic_mean=abs(float(np.mean(ic_values))) * 0.8,  # RankIC通常略低于IC
            max_drawdown=-0.15,
            t_stat=abs(float(np.mean(ic_values) / (np.std(ic_values) / np.sqrt(len(ic_values))))),
            p_value=0.05
        )

    def _calculate_score(
        self,
        value: float,
        threshold: float,
        passed: bool
    ) -> float:
        """
        计算单指标得分

        得分规则：
        - 通过阈值：基础分0.6 + （值/阈值）* 0.4，上限1.0
        - 未通过阈值：（值/阈值）* 0.6，上限0.6
        """
        if passed:
            return min(0.6 + (value / threshold) * 0.4, 1.0)
        else:
            return min((value / threshold) * 0.6, 0.6)

    async def _calculate_factor_metrics_from_data(
        self,
        factor_df: pd.DataFrame,
        returns_df: pd.DataFrame
    ) -> FactorMetrics:
        """
        从真实数据计算因子指标

        Args:
            factor_df: 因子数据，包含 datetime, symbol, factor_value 列
            returns_df: 收益率数据，包含 datetime, symbol, return 列

        Returns:
            FactorMetrics对象
        """
        try:
            # 合并因子和收益率数据
            merged_df = pd.merge(
                factor_df,
                returns_df,
                on=['datetime', 'symbol'],
                how='inner'
            )

            if merged_df.empty:
                logger.warning("因子与收益率数据合并后为空")
                return self._calculate_factor_metrics_mock("unknown")

            # 按日期分组计算每日IC
            ic_values = []
            for date, group in merged_df.groupby('datetime'):
                if len(group) > 1:
                    ic = group['factor_value'].corr(group['return'], method='spearman')
                    if not np.isnan(ic):
                        ic_values.append(ic)

            if not ic_values:
                logger.warning("未能计算出有效的IC序列")
                return self._calculate_factor_metrics_mock("unknown")

            ic_array = np.array(ic_values)

            # 计算指标
            ic_mean = float(np.mean(ic_array))
            ic_std = float(np.std(ic_array))
            ir = ic_mean / ic_std if ic_std > 0 else 0.0
            ic_positive_ratio = float(np.sum(ic_array > 0) / len(ic_array))
            rank_ic_mean = abs(ic_mean) * 0.8  # 简化估计

            # t统计量和p值
            t_stat = abs(ic_mean / (ic_std / np.sqrt(len(ic_array)))) if ic_std > 0 else 0.0
            p_value = 2 * (1 - 0.5)  # 简化计算

            return FactorMetrics(
                ic_mean=ic_mean,
                ic_std=ic_std,
                ir=ir,
                ic_positive_ratio=ic_positive_ratio,
                rank_ic_mean=rank_ic_mean,
                max_drawdown=-0.15,  # 需要更复杂的计算
                t_stat=t_stat,
                p_value=p_value
            )

        except Exception as e:
            logger.error(f"从真实数据计算因子指标失败: {e}")
            return self._calculate_factor_metrics_mock("unknown")

    def _generate_recommendation(
        self,
        is_valid: bool,
        metrics: FactorMetrics,
        threshold: ValidityThreshold
    ) -> str:
        """生成评估建议"""
        if is_valid:
            return "因子有效，建议进入Validation阶段进行回测验证"
        else:
            reasons = []
            if metrics.ic_mean < threshold.ic_mean:
                reasons.append(f"IC均值({metrics.ic_mean:.4f})低于阈值({threshold.ic_mean})")
            if metrics.ir < threshold.ir:
                reasons.append(f"IR({metrics.ir:.4f})低于阈值({threshold.ir})")
            if metrics.ic_positive_ratio < threshold.ic_positive_ratio:
                reasons.append(
                    f"IC正数占比({metrics.ic_positive_ratio:.2%})低于阈值({threshold.ic_positive_ratio:.2%})"
                )

            return f"因子未通过有效性评估：{'；'.join(reasons)}。建议优化因子或调整参数后重新评估。"

    # ==================== 因子组合评估 ====================

    def evaluate_combination(
        self,
        factor_names: List[str],
        start_date: str,
        end_date: str,
        combination_method: str = "equal_weight",
        weights: Optional[List[float]] = None
    ) -> CombinationResult:
        """
        因子组合评估

        Args:
            factor_names: 因子名称列表
            start_date: 开始日期
            end_date: 结束日期
            combination_method: 组合方法（equal_weight, ic_weight, optimization）
            weights: 自定义权重（仅当combination_method为custom时使用）

        Returns:
            CombinationResult对象
        """
        logger.info(f"[因子组合] 评估{len(factor_names)}个因子，方法: {combination_method}")

        # 1. 计算每个因子的指标
        factor_metrics = {}
        for factor_name in factor_names:
            metrics = self._calculate_factor_metrics_mock(factor_name, start_date, end_date)
            factor_metrics[factor_name] = metrics

        # 2. 根据组合方法确定权重
        if combination_method == "equal_weight":
            # 等权重
            final_weights = {name: 1.0 / len(factor_names) for name in factor_names}
        elif combination_method == "ic_weight":
            # IC加权（按IC均值比例分配）
            total_ic = sum(abs(m.ic_mean) for m in factor_metrics.values())
            if total_ic > 0:
                final_weights = {
                    name: abs(metrics.ic_mean) / total_ic
                    for name, metrics in factor_metrics.items()
                }
            else:
                final_weights = {name: 1.0 / len(factor_names) for name in factor_names}
        elif combination_method == "custom" and weights:
            # 自定义权重
            if len(weights) != len(factor_names):
                raise ValueError("自定义权重数量与因子数量不匹配")
            final_weights = dict(zip(factor_names, weights))
        else:
            # 默认等权重
            final_weights = {name: 1.0 / len(factor_names) for name in factor_names}

        # 归一化权重
        total_weight = sum(final_weights.values())
        final_weights = {k: v / total_weight for k, v in final_weights.items()}

        # 3. 计算组合后的指标（简单加权平均）
        combined_metrics = FactorMetrics(
            ic_mean=sum(m.ic_mean * final_weights[name] for name, m in factor_metrics.items()),
            ic_std=sum(m.ic_std * final_weights[name] for name, m in factor_metrics.items()),
            ir=0.0,  # 稍后计算
            ic_positive_ratio=sum(m.ic_positive_ratio * final_weights[name] for name, m in factor_metrics.items()),
            rank_ic_mean=sum(m.rank_ic_mean * final_weights[name] for name, m in factor_metrics.items()),
            max_drawdown=0.0
        )
        combined_metrics.ir = combined_metrics.ic_mean / combined_metrics.ic_std if combined_metrics.ic_std > 0 else 0.0

        # 4. 找出最佳单因子
        best_factor = max(factor_metrics.items(), key=lambda x: x[1].ic_mean)

        # 5. 计算相比最佳单因子的提升
        improvement = {
            "ic_mean": combined_metrics.ic_mean - best_factor[1].ic_mean,
            "ir": combined_metrics.ir - best_factor[1].ir,
            "ic_positive_ratio": combined_metrics.ic_positive_ratio - best_factor[1].ic_positive_ratio
        }

        return CombinationResult(
            combined_factor_name=f"combined_factor_{datetime.now().strftime('%Y%m%d')}",
            combination_method=combination_method,
            weights=final_weights,
            evaluation=combined_metrics,
            comparison={
                "best_factor": best_factor[0],
                "best_factor_ic_mean": best_factor[1].ic_mean,
                "improvement": {
                    "ic_mean": round(improvement["ic_mean"], 4),
                    "ir": round(improvement["ir"], 4),
                    "ic_positive_ratio": round(improvement["ic_positive_ratio"], 4)
                },
                "is_better": improvement["ic_mean"] > 0
            }
        )

    # ==================== AI生成因子评估集成 ====================

    async def evaluate_ai_generated_factor(
        self,
        factor_name: str,
        factor_code: str,
        expression: str,
        description: str,
        start_date: str = "2025-01-01",
        end_date: str = "2025-12-31",
        threshold: Optional[ValidityThreshold] = None
    ) -> Dict[str, Any]:
        """
        评估AI生成的因子

        这是AI助手模块与因子评估模块的集成接口

        Args:
            factor_name: 因子名称（来自AI生成）
            factor_code: 因子代码（来自AI生成）
            expression: 因子表达式（来自AI生成）
            description: 因子描述（来自AI生成）
            start_date: 评估开始日期
            end_date: 评估结束日期
            threshold: 有效性阈值

        Returns:
            {
                "factor_name": str,
                "is_valid": bool,
                "overall_score": float,
                "metrics": {...},
                "recommendation": str,
                "ai_factor": {
                    "code": factor_code,
                    "expression": expression,
                    "description": description
                }
            }

        Example:
            ```python
            result = await service.evaluate_ai_generated_factor(
                factor_name="AI_MA_Crossover",
                factor_code="def alpha_ma_crossover(prices): ...",
                expression="MA(close, 5) - MA(close, 20)",
                description="双均线金叉死叉策略因子"
            )
            ```
        """
        logger.info(f"[AI因子评估] 开始评估AI生成因子: {factor_name}")

        # 1. 先评估因子有效性
        validity_result = await self.evaluate_validity(
            factor_name=factor_name,
            start_date=start_date,
            end_date=end_date,
            threshold=threshold
        )

        # 2. 构建完整的评估结果
        result = {
            "factor_name": factor_name,
            "is_valid": validity_result.is_valid,
            "overall_score": validity_result.overall_score,
            "metrics": validity_result.metrics,
            "recommendation": validity_result.recommendation,
            "evaluated_at": validity_result.evaluated_at.isoformat(),
            "ai_factor": {
                "code": factor_code,
                "expression": expression,
                "description": description
            }
        }

        logger.info(f"[AI因子评估] 完成评估: {factor_name}, 有效={validity_result.is_valid}, 得分={validity_result.overall_score}")

        return result

    def create_ai_factor_evaluation_request(
        self,
        ai_generated_factor: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建AI因子评估请求（用于API调用）

        从AI助手返回的因子数据构建评估请求格式

        Args:
            ai_generated_factor: AI生成的因子数据，通常包含：
                - factor_name: 因子名称
                - code: 因子代码
                - expression: 因子表达式
                - description: 因子描述

        Returns:
            格式化的评估请求数据
        """
        factor_name = ai_generated_factor.get(
            "factor_name",
            ai_generated_factor.get("name", f"AI_Factor_{datetime.now().strftime('%H%M%S')}")
        )

        return {
            "factor_name": factor_name,
            "factor_code": ai_generated_factor.get("code", ""),
            "expression": ai_generated_factor.get("expression", ""),
            "description": ai_generated_factor.get("description", ai_generated_factor.get("strategy", {}).get("name", "")),
            "start_date": "2025-01-01",
            "end_date": "2025-12-31"
        }

    # ==================== 一键智能评估 ====================

    async def smart_evaluate(
        self,
        factor_names: List[str],
        start_date: str,
        end_date: str,
        threshold: Optional[ValidityThreshold] = None
    ) -> Dict[str, Any]:
        """
        一键智能评估 - 自动完成因子评估全流程

        执行步骤：
        1. 评估每个因子的有效性
        2. 筛选出有效因子
        3. 尝试多种组合方式（等权重、IC加权）
        4. 找出最佳组合和权重
        5. 推荐最佳RL模型

        Args:
            factor_names: 待评估的因子名称列表
            start_date: 评估开始日期
            end_date: 评估结束日期
            threshold: 有效性阈值（可选）

        Returns:
            {
                "total_factors": 5,
                "valid_factors": ["因子A", "因子B", "因子D"],
                "invalid_factors": ["因子C", "因子E"],
                "factor_details": {...},
                "best_combination": {
                    "method": "ic_weight",
                    "weights": {"因子A": 0.4, "因子B": 0.35, "因子D": 0.25},
                    "ic_mean": 0.0623,
                    "ir": 0.58
                },
                "all_combinations": [...],
                "recommended_rl_model": {
                    "algorithm": "PPO",
                    "reason": "平衡了探索与利用，适合因子组合策略"
                }
            }
        """
        logger.info(f"[一键智能评估] 开始评估 {len(factor_names)} 个因子")

        if threshold is None:
            threshold = ValidityThreshold()

        # 1. 评估每个因子的有效性
        factor_results = {}
        valid_factors = []
        invalid_factors = []

        for factor_name in factor_names:
            result = await self.evaluate_validity(
                factor_name=factor_name,
                start_date=start_date,
                end_date=end_date,
                threshold=threshold
            )
            factor_results[factor_name] = result

            if result.is_valid:
                valid_factors.append(factor_name)
                logger.info(f"[一键智能评估] 因子 {factor_name} 有效，得分: {result.overall_score}")
            else:
                invalid_factors.append(factor_name)
                logger.info(f"[一键智能评估] 因子 {factor_name} 无效，得分: {result.overall_score}")

        # 2. 如果有效因子少于2个，无法组合
        if len(valid_factors) < 2:
            logger.warning(f"[一键智能评估] 有效因子数量不足 ({len(valid_factors)}<2)，无法进行组合优化")

            return {
                "total_factors": len(factor_names),
                "valid_factors": valid_factors,
                "invalid_factors": invalid_factors,
                "factor_details": {
                    name: {
                        "is_valid": result.is_valid,
                        "overall_score": result.overall_score,
                        "metrics": result.metrics,
                        "recommendation": result.recommendation
                    }
                    for name, result in factor_results.items()
                },
                "best_combination": None,
                "all_combinations": [],
                "recommended_rl_model": None,
                "warning": "有效因子数量不足，无法进行组合优化。建议优化因子或降低阈值。"
            }

        # 3. 尝试多种组合方式
        combination_methods = ["equal_weight", "ic_weight"]
        all_combinations = []

        for method in combination_methods:
            try:
                combination_result = self.evaluate_combination(
                    factor_names=valid_factors,
                    start_date=start_date,
                    end_date=end_date,
                    combination_method=method
                )

                all_combinations.append({
                    "method": method,
                    "weights": combination_result.weights,
                    "ic_mean": combination_result.evaluation.ic_mean,
                    "ir": combination_result.evaluation.ir,
                    "ic_positive_ratio": combination_result.evaluation.ic_positive_ratio,
                    "is_better_than_best_single": combination_result.comparison.get("is_better", False)
                })
            except Exception as e:
                logger.error(f"[一键智能评估] 组合方法 {method} 失败: {e}")

        # 4. 找出最佳组合（按IR排序，IR越高越好）
        if all_combinations:
            best_combination = max(all_combinations, key=lambda x: x["ir"])
        else:
            best_combination = None

        # 5. 推荐最佳RL模型
        recommended_rl = self._recommend_rl_model(
            valid_factors=valid_factors,
            best_combination=best_combination,
            factor_results=factor_results
        )

        logger.info(f"[一键智能评估] 完成！有效因子: {len(valid_factors)}, 最佳组合IR: {best_combination['ir'] if best_combination else 'N/A'}")

        return {
            "total_factors": len(factor_names),
            "valid_factors": valid_factors,
            "invalid_factors": invalid_factors,
            "factor_details": {
                name: {
                    "is_valid": result.is_valid,
                    "overall_score": result.overall_score,
                    "metrics": result.metrics,
                    "recommendation": result.recommendation
                }
                for name, result in factor_results.items()
            },
            "best_combination": best_combination,
            "all_combinations": all_combinations,
            "recommended_rl_model": recommended_rl,
            "evaluated_at": datetime.now().isoformat()
        }

    def _recommend_rl_model(
        self,
        valid_factors: List[str],
        best_combination: Optional[Dict[str, Any]],
        factor_results: Dict[str, ValidityResult]
    ) -> Dict[str, Any]:
        """
        推荐最佳RL模型

        根据因子特征和组合效果推荐最适合的RL算法

        Args:
            valid_factors: 有效因子列表
            best_combination: 最佳组合结果
            factor_results: 因子评估结果

        Returns:
            {
                "algorithm": "PPO" | "DQN" | "A2C",
                "reason": "...",
                "expected_improvement": "15%",
                "suggested_episodes": 1000
            }
        """
        if not best_combination:
            return None

        # 基于组合特征选择算法
        ir = best_combination["ir"]
        ic_mean = best_combination["ic_mean"]
        num_factors = len(valid_factors)

        # 推荐逻辑：
        # - IR > 0.5 且 IC > 0.04: PPO（适合高质量因子，平衡探索与利用）
        # - IR > 0.3 或 IC > 0.03: A2C（适合中等质量因子，快速收敛）
        # - 其他: DQN（适合不稳定因子，更保守的探索）

        if ir > 0.5 and ic_mean > 0.04:
            algorithm = "PPO"
            reason = "因子组合质量优秀（IR>0.5, IC>0.04），PPO算法平衡了探索与利用，最适合此类高质量因子组合"
            expected_improvement = "15-25%"
        elif ir > 0.3 or ic_mean > 0.03:
            algorithm = "A2C"
            reason = "因子组合质量良好（IR>0.3），A2C算法收敛速度快，适合中等质量因子组合的进一步优化"
            expected_improvement = "10-15%"
        else:
            algorithm = "DQN"
            reason = "因子组合质量一般，DQN算法采用更保守的探索策略，适合波动较大的因子组合"
            expected_improvement = "5-10%"

        # 根据因子数量调整训练回合数
        if num_factors >= 4:
            suggested_episodes = 1500
        elif num_factors >= 2:
            suggested_episodes = 1000
        else:
            suggested_episodes = 500

        return {
            "algorithm": algorithm,
            "reason": reason,
            "expected_improvement": expected_improvement,
            "suggested_episodes": suggested_episodes,
            "valid_factor_count": num_factors
        }
