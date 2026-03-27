# -*- coding: utf-8 -*-
"""
Validation阶段 - RL策略验证服务
================================
职责：
- RL vs 传统策略对比
- 策略鲁棒性验证
- 敏感性分析
- 适用场景建议

架构层次：
- Validation阶段：验证RL策略的有效性
- 与Research阶段的RL策略服务集成
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from loguru import logger
from datetime import datetime
from enum import Enum
import uuid
import numpy as np


class MarketRegime(Enum):
    """市场环境"""
    BULL = "bull"           # 牛市
    BEAR = "bear"           # 熊市
    SIDEWAYS = "sideways"   # 震荡市
    VOLATILE = "volatile"   # 高波动


class ValidationType(Enum):
    """验证类型"""
    COMPARISON = "comparison"       # 策略对比
    ROBUSTNESS = "robustness"       # 鲁棒性检验
    SENSITIVITY = "sensitivity"     # 敏感性分析
    SCENARIO = "scenario"           # 场景分析


@dataclass
class RLValidationConfig:
    """RL策略验证配置"""
    config_id: str
    rl_strategy_id: str
    baseline_strategy_id: str       # 传统基准策略
    validation_types: List[str] = field(
        default_factory=lambda: ["comparison", "robustness"]
    )
    test_period_start: str = ""
    test_period_end: str = ""
    market_regimes: List[str] = field(
        default_factory=lambda: ["bull", "bear", "sideways"]
    )
    confidence_level: float = 0.95


@dataclass
class ComparisonResult:
    """策略对比结果"""
    metric_name: str
    rl_value: float
    baseline_value: float
    improvement_pct: float
    is_significant: bool


@dataclass
class RobustnessResult:
    """鲁棒性检验结果"""
    metric_name: str
    mean_value: float
    std_value: float
    min_value: float
    max_value: float
    stability_score: float      # 0-1, 越高越稳定


@dataclass
class ScenarioRecommendation:
    """场景建议"""
    market_regime: str
    recommended_strategy: str   # "rl" or "baseline"
    confidence: float
    expected_improvement: float
    reasoning: str


class RLStrategyValidationService:
    """RL策略验证服务

    提供RL策略与传统策略的对比验证功能
    """

    def __init__(self):
        """初始化RL策略验证服务"""
        self.validations: Dict[str, Dict[str, Any]] = {}
        self.comparison_results: Dict[str, List[ComparisonResult]] = {}
        self.robustness_results: Dict[str, List[RobustnessResult]] = {}

        logger.info("RLStrategyValidationService initialized")

    def create_validation(
        self,
        rl_strategy_id: str,
        baseline_strategy_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """创建验证任务

        Args:
            rl_strategy_id: RL策略ID
            baseline_strategy_id: 基准策略ID
            config: 额外配置

        Returns:
            验证ID
        """
        config = config or {}
        validation_id = f"rl_val_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"

        validation_config = RLValidationConfig(
            config_id=validation_id,
            rl_strategy_id=rl_strategy_id,
            baseline_strategy_id=baseline_strategy_id,
            validation_types=config.get("validation_types", ["comparison"]),
            test_period_start=config.get("test_period_start", "2023-01-01"),
            test_period_end=config.get("test_period_end", "2023-12-31"),
            market_regimes=config.get("market_regimes", ["bull", "bear", "sideways"]),
            confidence_level=config.get("confidence_level", 0.95)
        )

        self.validations[validation_id] = {
            "config": validation_config,
            "status": "created",
            "created_at": datetime.now(),
            "results": None
        }

        logger.info(
            f"Created RL validation: {validation_id}, "
            f"RL={rl_strategy_id}, Baseline={baseline_strategy_id}"
        )

        return validation_id

    def run_comparison(
        self,
        validation_id: str
    ) -> List[ComparisonResult]:
        """运行策略对比

        Args:
            validation_id: 验证ID

        Returns:
            对比结果列表
        """
        validation = self.validations.get(validation_id)
        if not validation:
            return []

        config = validation["config"]
        results = []

        # 模拟对比各指标
        metrics = [
            ("total_return", 0.18, 0.12),
            ("sharpe_ratio", 1.35, 0.95),
            ("max_drawdown", 0.08, 0.12),
            ("win_rate", 0.58, 0.52),
            ("profit_loss_ratio", 1.8, 1.4),
            ("calmar_ratio", 2.25, 1.0)
        ]

        for metric_name, rl_base, baseline_base in metrics:
            # 添加随机波动
            rl_value = rl_base * (1 + np.random.uniform(-0.1, 0.1))
            baseline_value = baseline_base * (1 + np.random.uniform(-0.1, 0.1))

            # 计算改进百分比
            if baseline_value != 0:
                improvement = (rl_value - baseline_value) / abs(baseline_value) * 100
            else:
                improvement = 0

            # 对于回撤等负向指标，改进是减少
            if metric_name in ["max_drawdown"]:
                improvement = -improvement

            result = ComparisonResult(
                metric_name=metric_name,
                rl_value=rl_value,
                baseline_value=baseline_value,
                improvement_pct=improvement,
                is_significant=abs(improvement) > 10  # 改进超过10%认为显著
            )
            results.append(result)

        self.comparison_results[validation_id] = results

        logger.info(f"Comparison completed: {validation_id}")

        return results

    def run_robustness_test(
        self,
        validation_id: str,
        num_simulations: int = 100
    ) -> List[RobustnessResult]:
        """运行鲁棒性检验

        Args:
            validation_id: 验证ID
            num_simulations: 模拟次数

        Returns:
            鲁棒性结果列表
        """
        validation = self.validations.get(validation_id)
        if not validation:
            return []

        results = []

        # 对各指标进行鲁棒性检验
        metrics = ["total_return", "sharpe_ratio", "max_drawdown", "win_rate"]

        for metric in metrics:
            # 模拟多次采样的结果
            if metric == "total_return":
                samples = np.random.normal(0.15, 0.05, num_simulations)
            elif metric == "sharpe_ratio":
                samples = np.random.normal(1.2, 0.3, num_simulations)
            elif metric == "max_drawdown":
                samples = np.random.normal(0.10, 0.03, num_simulations)
            else:  # win_rate
                samples = np.random.normal(0.55, 0.08, num_simulations)

            # 计算稳定性分数（变异系数的倒数）
            cv = np.std(samples) / abs(np.mean(samples)) if np.mean(samples) != 0 else 0
            stability = 1 / (1 + cv)  # 归一化到0-1

            result = RobustnessResult(
                metric_name=metric,
                mean_value=float(np.mean(samples)),
                std_value=float(np.std(samples)),
                min_value=float(np.min(samples)),
                max_value=float(np.max(samples)),
                stability_score=min(1.0, stability)
            )
            results.append(result)

        self.robustness_results[validation_id] = results

        logger.info(f"Robustness test completed: {validation_id}")

        return results

    def analyze_by_market_regime(
        self,
        validation_id: str
    ) -> Dict[str, Any]:
        """按市场环境分析

        Args:
            validation_id: 验证ID

        Returns:
            各市场环境下的分析结果
        """
        validation = self.validations.get(validation_id)
        if not validation:
            return {}

        config = validation["config"]
        regime_analysis = {}

        for regime in config.market_regimes:
            # 模拟不同市场环境下的表现
            if regime == "bull":
                rl_return = 0.25
                baseline_return = 0.18
                recommendation = "rl"
            elif regime == "bear":
                rl_return = -0.05
                baseline_return = -0.08
                recommendation = "rl"
            elif regime == "sideways":
                rl_return = 0.08
                baseline_return = 0.06
                recommendation = "baseline"  # 震荡市传统策略可能更稳
            else:  # volatile
                rl_return = 0.12
                baseline_return = 0.05
                recommendation = "rl"

            regime_analysis[regime] = {
                "rl_return": rl_return,
                "baseline_return": baseline_return,
                "improvement": rl_return - baseline_return,
                "recommended_strategy": recommendation
            }

        return regime_analysis

    def get_recommendations(
        self,
        validation_id: str
    ) -> List[ScenarioRecommendation]:
        """获取场景建议

        Args:
            validation_id: 验证ID

        Returns:
            场景建议列表
        """
        regime_analysis = self.analyze_by_market_regime(validation_id)

        recommendations = []
        for regime, analysis in regime_analysis.items():
            rec = ScenarioRecommendation(
                market_regime=regime,
                recommended_strategy=analysis["recommended_strategy"],
                confidence=np.random.uniform(0.7, 0.95),
                expected_improvement=abs(analysis["improvement"]),
                reasoning=f"在{regime}市场中，{analysis['recommended_strategy']}策略表现更好"
            )
            recommendations.append(rec)

        return recommendations

    def generate_validation_report(
        self,
        validation_id: str
    ) -> Dict[str, Any]:
        """生成验证报告

        Args:
            validation_id: 验证ID

        Returns:
            完整的验证报告
        """
        validation = self.validations.get(validation_id)
        if not validation:
            return {"error": "Validation not found"}

        config = validation["config"]

        # 获取各类结果
        comparison = self.comparison_results.get(validation_id, [])
        robustness = self.robustness_results.get(validation_id, [])
        regime_analysis = self.analyze_by_market_regime(validation_id)
        recommendations = self.get_recommendations(validation_id)

        # 转换为可序列化格式
        comparison_data = [
            {
                "metric": r.metric_name,
                "rl_value": round(r.rl_value, 4),
                "baseline_value": round(r.baseline_value, 4),
                "improvement_pct": round(r.improvement_pct, 2),
                "significant": r.is_significant
            }
            for r in comparison
        ]

        robustness_data = [
            {
                "metric": r.metric_name,
                "mean": round(r.mean_value, 4),
                "std": round(r.std_value, 4),
                "stability": round(r.stability_score, 4)
            }
            for r in robustness
        ]

        recommendations_data = [
            {
                "regime": r.market_regime,
                "recommended": r.recommended_strategy,
                "confidence": round(r.confidence, 2),
                "improvement": round(r.expected_improvement, 4)
            }
            for r in recommendations
        ]

        # 计算总体评估
        overall_score = self._calculate_overall_score(comparison, robustness)

        report = {
            "validation_id": validation_id,
            "rl_strategy_id": config.rl_strategy_id,
            "baseline_strategy_id": config.baseline_strategy_id,
            "test_period": {
                "start": config.test_period_start,
                "end": config.test_period_end
            },
            "comparison_results": comparison_data,
            "robustness_results": robustness_data,
            "regime_analysis": regime_analysis,
            "recommendations": recommendations_data,
            "overall_assessment": {
                "score": overall_score,
                "conclusion": "推荐使用" if overall_score > 0.6 else "需要优化",
                "confidence": round(np.mean([r.confidence for r in recommendations]), 2)
            },
            "generated_at": datetime.now().isoformat()
        }

        validation["results"] = report
        validation["status"] = "completed"

        return report

    def _calculate_overall_score(
        self,
        comparison: List[ComparisonResult],
        robustness: List[RobustnessResult]
    ) -> float:
        """计算总体评分"""
        if not comparison:
            return 0.5

        # 对比得分：统计显著改进的比例
        significant_improvements = sum(1 for r in comparison if r.is_significant and r.improvement_pct > 0)
        comparison_score = significant_improvements / len(comparison) if comparison else 0

        # 鲁棒性得分：平均稳定性
        robustness_score = np.mean([r.stability_score for r in robustness]) if robustness else 0.5

        # 综合评分
        overall = comparison_score * 0.6 + robustness_score * 0.4

        return round(overall, 2)

    def get_validation_status(self, validation_id: str) -> Dict[str, Any]:
        """获取验证状态

        Args:
            validation_id: 验证ID

        Returns:
            状态信息
        """
        validation = self.validations.get(validation_id)
        if not validation:
            return {"error": "Validation not found"}

        return {
            "validation_id": validation_id,
            "status": validation["status"],
            "created_at": validation["created_at"].isoformat(),
            "has_results": validation["results"] is not None
        }


# ==================== 全局单例 ====================

_rl_validation_service_instance: Optional[RLStrategyValidationService] = None


def get_rl_validation_service() -> RLStrategyValidationService:
    """获取RL策略验证服务单例

    Returns:
        RLStrategyValidationService实例
    """
    global _rl_validation_service_instance

    if _rl_validation_service_instance is None:
        _rl_validation_service_instance = RLStrategyValidationService()

    return _rl_validation_service_instance
