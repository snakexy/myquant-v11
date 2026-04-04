# -*- coding: utf-8 -*-
"""
Production阶段 - ML信号生成器
==============================
职责：
- 将ML预测评分（0-1）转换为交易信号
- 结合其他因子生成综合信号
- 提供信号强度分级（WEAK/NORMAL/STRONG）

架构层次：
- Production阶段：信号生成
- P1核心功能
"""

from typing import Dict, List, Optional, Any
from loguru import logger
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

from myquant.core.production.online_prediction_service import (
    PredictionResult,
    PredictionDirection,
    get_prediction_service
)


class SignalType(Enum):
    """信号类型"""
    BUY = "BUY"              # 买入
    SELL = "SELL"            # 卖出
    HOLD = "HOLD"            # 持有
    OBSERVE = "OBSERVE"      # 观望


class SignalStrength(Enum):
    """信号强度"""
    STRONG = "STRONG"        # 强烈（置信度>80%）
    NORMAL = "NORMAL"        # 正常（置信度60-80%）
    WEAK = "WEAK"            # 弱（置信度<60%）


@dataclass
class TradingSignal:
    """交易信号"""
    signal_id: str                           # 信号ID
    instrument: str                          # 股票代码
    signal_type: SignalType                  # 信号类型
    strength: SignalStrength                 # 信号强度
    score: float                             # ML评分 (0-1)
    confidence: float                        # 置信度 (0-1)
    current_price: Optional[float] = None    # 当前价格
    target_price: Optional[float] = None     # 目标价格
    stop_loss_price: Optional[float] = None  # 止损价格
    reason: str = ""                         # 信号原因
    ml_model_id: str = ""                    # ML模型ID
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None    # 过期时间
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SignalValidationResult:
    """信号验证结果"""
    is_valid: bool
    signal: Optional[TradingSignal]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class MLSignalGenerator:
    """
    ML信号生成器

    功能：
    - 将ML预测转换为交易信号
    - 信号强度分级
    - 信号验证
    - 批量信号生成

    信号分级规则：
    | 评分范围 | 信号类型 | 强度 | 建议仓位 |
    |---------|---------|------|---------|
    | 0.8-1.0 | BUY     | STRONG | 100%  |
    | 0.6-0.8 | BUY     | NORMAL | 100%  |
    | 0.4-0.6 | HOLD    | WEAK   | 50%   |
    | 0.2-0.4 | SELL    | WEAK   | 50%   |
    | 0.0-0.2 | SELL    | STRONG | 0%    |
    """

    def __init__(
        self,
        buy_threshold: float = 0.6,
        sell_threshold: float = 0.4,
        strong_threshold: float = 0.8,
        weak_threshold: float = 0.6
    ):
        """
        初始化ML信号生成器

        Args:
            buy_threshold: 买入阈值（评分高于此值买入）
            sell_threshold: 卖出阈值（评分低于此值卖出）
            strong_threshold: 强信号阈值
            weak_threshold: 弱信号阈值
        """
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.strong_threshold = strong_threshold
        self.weak_threshold = weak_threshold

        # 信号历史
        self._signal_history: List[TradingSignal] = []

        # 信号配置
        self.target_price_multiplier = {
            SignalStrength.STRONG: 0.02,    # +2%
            SignalStrength.NORMAL: 0.01,    # +1%
            SignalStrength.WEAK: 0.005      # +0.5%
        }

        self.stop_loss_multiplier = {
            SignalStrength.STRONG: 0.03,    # -3%
            SignalStrength.NORMAL: 0.05,    # -5%
            SignalStrength.WEAK: 0.08       # -8%
        }

        logger.info("✅ MLSignalGenerator初始化完成")

    # ==================== 信号生成 ====================

    def generate_signal(
        self,
        ml_prediction: PredictionResult,
        current_price: Optional[float] = None,
        position_info: Optional[Dict[str, Any]] = None,
        additional_factors: Optional[Dict[str, Any]] = None
    ) -> TradingSignal:
        """
        生成交易信号

        Args:
            ml_prediction: ML预测结果
            current_price: 当前价格
            position_info: 持仓信息
            additional_factors: 额外因子（技术指标、风险等）

        Returns:
            TradingSignal对象
        """
        # 生成信号ID
        signal_id = f"sig_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

        # 确定信号类型
        signal_type = self._determine_signal_type(
            ml_prediction.prediction_score,
            position_info
        )

        # 确定信号强度
        strength = self._determine_signal_strength(
            ml_prediction.prediction_score,
            ml_prediction.confidence
        )

        # 计算目标价和止损价
        target_price = None
        stop_loss_price = None
        if current_price is not None:
            target_price, stop_loss_price = self._calculate_prices(
                current_price,
                signal_type,
                strength
            )

        # 生成原因说明
        reason = self._generate_reason(
            ml_prediction,
            signal_type,
            strength,
            additional_factors
        )

        # 创建信号
        signal = TradingSignal(
            signal_id=signal_id,
            instrument=ml_prediction.instrument,
            signal_type=signal_type,
            strength=strength,
            score=ml_prediction.prediction_score,
            confidence=ml_prediction.confidence,
            current_price=current_price,
            target_price=target_price,
            stop_loss_price=stop_loss_price,
            reason=reason,
            ml_model_id=ml_prediction.model_id,
            metadata={
                "model_version": ml_prediction.model_version,
                "features_used": ml_prediction.features_used,
                "prediction_latency_ms": ml_prediction.latency_ms,
                "additional_factors": additional_factors
            }
        )

        # 保存到历史
        self._signal_history.append(signal)

        # 只保留最近1000条
        if len(self._signal_history) > 1000:
            self._signal_history = self._signal_history[-1000:]

        logger.info(f"信号生成: {signal.instrument} {signal.signal_type.value} "
                   f"(评分:{signal.score:.2f}, 强度:{signal.strength.value})")

        return signal

    def _determine_signal_type(
        self,
        score: float,
        position_info: Optional[Dict[str, Any]]
    ) -> SignalType:
        """确定信号类型"""
        # 基于评分确定基本信号
        if score >= self.buy_threshold:
            return SignalType.BUY
        elif score <= self.sell_threshold:
            return SignalType.SELL
        else:
            return SignalType.HOLD

    def _determine_signal_strength(
        self,
        score: float,
        confidence: float
    ) -> SignalStrength:
        """确定信号强度"""
        # 结合评分和置信度
        combined = score * confidence

        if combined >= self.strong_threshold or confidence >= 0.8:
            return SignalStrength.STRONG
        elif combined >= self.weak_threshold or confidence >= 0.6:
            return SignalStrength.NORMAL
        else:
            return SignalStrength.WEAK

    def _calculate_prices(
        self,
        current_price: float,
        signal_type: SignalType,
        strength: SignalStrength
    ) -> tuple:
        """计算目标价和止损价"""
        if signal_type == SignalType.BUY:
            target_mult = self.target_price_multiplier[strength]
            stop_mult = self.stop_loss_multiplier[strength]
            target_price = current_price * (1 + target_mult)
            stop_loss_price = current_price * (1 - stop_mult)
        elif signal_type == SignalType.SELL:
            target_mult = self.target_price_multiplier[strength]
            target_price = current_price * (1 - target_mult)
            stop_loss_price = None  # 卖出无止损
        else:
            target_price = current_price
            stop_loss_price = None

        return target_price, stop_loss_price

    def _generate_reason(
        self,
        ml_prediction: PredictionResult,
        signal_type: SignalType,
        strength: SignalStrength,
        additional_factors: Optional[Dict[str, Any]]
    ) -> str:
        """生成信号原因"""
        reasons = []

        # ML预测原因
        reasons.append(
            f"ML预测评分:{ml_prediction.prediction_score:.2f},"
            f"置信度:{int(ml_prediction.confidence * 100)}%"
        )

        # 信号强度
        reasons.append(f"信号强度:{strength.value}")

        # 额外因子
        if additional_factors:
            if "rsi" in additional_factors:
                rsi = additional_factors["rsi"]
                if rsi < 30:
                    reasons.append("RSI超卖")
                elif rsi > 70:
                    reasons.append("RSI超买")

            if "macd_signal" in additional_factors:
                reasons.append(f"MACD:{additional_factors['macd_signal']}")

        return "; ".join(reasons)

    # ==================== 批量信号生成 ====================

    def generate_signals_batch(
        self,
        ml_predictions: List[PredictionResult],
        prices: Optional[Dict[str, float]] = None
    ) -> List[TradingSignal]:
        """
        批量生成信号

        Args:
            ml_predictions: ML预测结果列表
            prices: 价格字典 {instrument: price}

        Returns:
            信号列表
        """
        signals = []
        prices = prices or {}

        for pred in ml_predictions:
            price = prices.get(pred.instrument)
            signal = self.generate_signal(pred, current_price=price)
            signals.append(signal)

        logger.info(f"批量信号生成完成: {len(signals)}条")
        return signals

    # ==================== 信号验证 ====================

    def validate_signal(
        self,
        signal: TradingSignal,
        risk_limits: Optional[Dict[str, Any]] = None
    ) -> SignalValidationResult:
        """
        验证信号有效性

        Args:
            signal: 交易信号
            risk_limits: 风险限制

        Returns:
            SignalValidationResult对象
        """
        warnings = []
        errors = []

        # 基本验证
        if signal.score < 0 or signal.score > 1:
            errors.append(f"评分范围错误: {signal.score}")

        if signal.confidence < 0 or signal.confidence > 1:
            errors.append(f"置信度范围错误: {signal.confidence}")

        # 风险限制验证
        if risk_limits:
            # 检查最大仓位
            if "max_position_pct" in risk_limits:
                max_pos = risk_limits["max_position_pct"]
                if signal.signal_type == SignalType.BUY:
                    warnings.append(f"请确保不超过最大仓位限制: {max_pos}%")

            # 检查信号强度限制
            if "min_signal_strength" in risk_limits:
                min_strength = risk_limits["min_signal_strength"]
                strength_order = [SignalStrength.WEAK, SignalStrength.NORMAL, SignalStrength.STRONG]
                if strength_order.index(signal.strength) < strength_order.index(min_strength):
                    warnings.append(f"信号强度低于要求: {signal.strength.value} < {min_strength.value}")

        # 信号过期检查
        if signal.expires_at and datetime.now() > signal.expires_at:
            errors.append("信号已过期")

        is_valid = len(errors) == 0

        return SignalValidationResult(
            is_valid=is_valid,
            signal=signal if is_valid else None,
            warnings=warnings,
            errors=errors
        )

    # ==================== 查询方法 ====================

    def get_signal_history(
        self,
        instrument: Optional[str] = None,
        signal_type: Optional[SignalType] = None,
        limit: int = 100
    ) -> List[TradingSignal]:
        """
        获取信号历史

        Args:
            instrument: 股票代码过滤
            signal_type: 信号类型过滤
            limit: 返回数量限制

        Returns:
            信号列表
        """
        result = self._signal_history

        if instrument:
            result = [s for s in result if s.instrument == instrument]

        if signal_type:
            result = [s for s in result if s.signal_type == signal_type]

        return result[-limit:]

    def get_signal_stats(self) -> Dict[str, Any]:
        """获取信号统计"""
        if not self._signal_history:
            return {}

        signals = self._signal_history

        buy_count = sum(1 for s in signals if s.signal_type == SignalType.BUY)
        sell_count = sum(1 for s in signals if s.signal_type == SignalType.SELL)
        hold_count = sum(1 for s in signals if s.signal_type == SignalType.HOLD)

        strong_count = sum(1 for s in signals if s.strength == SignalStrength.STRONG)
        normal_count = sum(1 for s in signals if s.strength == SignalStrength.NORMAL)
        weak_count = sum(1 for s in signals if s.strength == SignalStrength.WEAK)

        avg_score = sum(s.score for s in signals) / len(signals)
        avg_confidence = sum(s.confidence for s in signals) / len(signals)

        return {
            "total_signals": len(signals),
            "by_type": {
                "buy": buy_count,
                "sell": sell_count,
                "hold": hold_count
            },
            "by_strength": {
                "strong": strong_count,
                "normal": normal_count,
                "weak": weak_count
            },
            "avg_score": avg_score,
            "avg_confidence": avg_confidence
        }


# ==================== 单例模式 ====================

_signal_generator_instance: Optional[MLSignalGenerator] = None


def get_signal_generator() -> MLSignalGenerator:
    """获取MLSignalGenerator单例"""
    global _signal_generator_instance
    if _signal_generator_instance is None:
        _signal_generator_instance = MLSignalGenerator()
    return _signal_generator_instance
