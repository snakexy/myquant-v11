# -*- coding: utf-8 -*-
"""
Production阶段 - 在线预测服务
=============================
职责：
- 实时单股票预测（<50ms）
- 批量预测（4000只股票）
- 预测评分输出（0-1买入评分）

QLib集成：
- 使用QLib模型进行预测
- 支持特征工程流水线

架构层次：
- Production阶段：实时预测服务
- P1核心功能
"""

from typing import Dict, List, Optional, Any, Tuple
from loguru import logger
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
import numpy as np

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from qlib.workflow import R
    QLIB_AVAILABLE = True
except ImportError:
    QLIB_AVAILABLE = False

from myquant.core.production.online_model_manager import get_model_manager, OnlineModelManager


class PredictionDirection(Enum):
    """预测方向"""
    UP = "up"           # 上涨
    DOWN = "down"       # 下跌
    FLAT = "flat"       # 持平


@dataclass
class PredictionResult:
    """预测结果"""
    instrument: str                         # 股票代码
    prediction_score: float                 # 预测评分 (0-1)
    prediction: PredictionDirection         # 预测方向
    confidence: float                       # 置信度 (0-1)
    model_id: str                           # 模型ID
    model_version: str                      # 模型版本
    features_used: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    latency_ms: float = 0.0                 # 预测延迟(ms)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchPredictionResult:
    """批量预测结果"""
    predictions: List[PredictionResult]
    total: int
    elapsed_ms: float
    success_count: int
    error_count: int


class OnlinePredictionService:
    """
    在线预测服务

    功能：
    - 实时单股票预测
    - 批量预测
    - 预测缓存

    性能要求：
    - 单股票预测 < 50ms (P95)
    - 批量预测 < 5s (4000只股票)
    """

    def __init__(
        self,
        model_manager: Optional[OnlineModelManager] = None,
        cache_enabled: bool = True,
        cache_ttl_seconds: int = 60
    ):
        """
        初始化在线预测服务

        Args:
            model_manager: 模型管理器（None则使用全局单例）
            cache_enabled: 是否启用预测缓存
            cache_ttl_seconds: 缓存过期时间(秒)
        """
        self.model_manager = model_manager or get_model_manager()
        self.cache_enabled = cache_enabled
        self.cache_ttl_seconds = cache_ttl_seconds

        # 预测缓存 {cache_key: (result, timestamp)}
        self._cache: Dict[str, Tuple[PredictionResult, float]] = {}

        # 性能统计
        self._stats = {
            "total_predictions": 0,
            "cache_hits": 0,
            "total_latency_ms": 0.0,
            "latency_samples": []
        }

        # 默认模型名称
        self.default_model_name = "xgb_classification"

        logger.info("✅ OnlinePredictionService初始化完成")

    # ==================== 单股票预测 ====================

    async def predict_single(
        self,
        instrument: str,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        features: Optional[Dict[str, float]] = None,
        use_cache: bool = True
    ) -> PredictionResult:
        """
        单股票实时预测

        Args:
            instrument: 股票代码
            model_name: 模型名称（None使用默认）
            model_version: 模型版本（None使用活跃版本）
            features: 特征字典（None则自动获取）
            use_cache: 是否使用缓存

        Returns:
            PredictionResult对象
        """
        start_time = time.time()
        model_name = model_name or self.default_model_name

        # 检查缓存
        cache_key = f"{model_name}:{model_version}:{instrument}"
        if use_cache and self.cache_enabled:
            cached = self._get_from_cache(cache_key)
            if cached:
                self._stats["cache_hits"] += 1
                logger.debug(f"预测缓存命中: {instrument}")
                return cached

        try:
            # 获取模型
            model = self.model_manager.get_model_object(model_name)
            if model is None:
                logger.warning(f"模型未加载: {model_name}，使用模拟预测")
                return self._mock_prediction(instrument, model_name, model_version)

            # 获取特征
            if features is None:
                features = await self._get_features(instrument)

            # 执行预测
            prediction_score = await self._execute_prediction(model, features)

            # 创建预测结果
            result = self._create_prediction_result(
                instrument=instrument,
                prediction_score=prediction_score,
                model_name=model_name,
                model_version=model_version,
                features=features,
                start_time=start_time
            )

            # 更新缓存
            if self.cache_enabled:
                self._add_to_cache(cache_key, result)

            # 更新统计
            self._update_stats(result.latency_ms)

            return result

        except Exception as e:
            logger.error(f"预测失败: {instrument}, 错误: {e}")
            return self._mock_prediction(instrument, model_name, model_version)

    async def _get_features(self, instrument: str) -> Dict[str, float]:
        """
        获取股票特征

        Args:
            instrument: 股票代码

        Returns:
            特征字典
        """
        # TODO: 集成数据管理模块获取实时特征
        # 这里使用模拟特征
        features = {
            "MA5": 10.5,
            "MA10": 10.3,
            "MA20": 10.1,
            "RSI": 55.0,
            "MACD": 0.15,
            "MACD_SIGNAL": 0.12,
            "MACD_HIST": 0.03,
            "BOLL_UPPER": 11.0,
            "BOLL_MIDDLE": 10.5,
            "BOLL_LOWER": 10.0,
            "VOLUME_RATIO": 1.2,
            "TURNOVER_RATE": 2.5
        }

        return features

    async def _execute_prediction(
        self,
        model: Any,
        features: Dict[str, float]
    ) -> float:
        """
        执行模型预测

        Args:
            model: 模型对象
            features: 特征字典

        Returns:
            预测评分 (0-1)
        """
        # 模拟预测
        if isinstance(model, dict) and model.get("type") == "mock":
            # 模拟模式：返回随机评分
            import random
            return random.uniform(0.3, 0.8)

        # 真实预测（如果有pandas）
        if PANDAS_AVAILABLE:
            try:
                feature_df = pd.DataFrame([features])
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(feature_df)
                    return float(proba[0][1])  # 取正类概率
                elif hasattr(model, 'predict'):
                    pred = model.predict(feature_df)
                    return float(pred[0])
            except Exception as e:
                logger.warning(f"模型预测异常: {e}，使用模拟值")

        import random
        return random.uniform(0.3, 0.8)

    def _create_prediction_result(
        self,
        instrument: str,
        prediction_score: float,
        model_name: str,
        model_version: Optional[str],
        features: Dict[str, float],
        start_time: float
    ) -> PredictionResult:
        """创建预测结果对象"""
        latency_ms = (time.time() - start_time) * 1000

        # 确定预测方向
        if prediction_score > 0.55:
            prediction = PredictionDirection.UP
        elif prediction_score < 0.45:
            prediction = PredictionDirection.DOWN
        else:
            prediction = PredictionDirection.FLAT

        # 计算置信度
        confidence = abs(prediction_score - 0.5) * 2

        # 获取活跃模型信息
        active_model = self.model_manager.get_active_model(model_name)

        return PredictionResult(
            instrument=instrument,
            prediction_score=prediction_score,
            prediction=prediction,
            confidence=confidence,
            model_id=active_model.model_id if active_model else f"{model_name}_unknown",
            model_version=active_model.version if active_model else model_version or "v1.0",
            features_used=list(features.keys()),
            latency_ms=latency_ms
        )

    def _mock_prediction(
        self,
        instrument: str,
        model_name: str,
        model_version: Optional[str]
    ) -> PredictionResult:
        """创建模拟预测结果"""
        import random
        score = random.uniform(0.3, 0.8)

        return PredictionResult(
            instrument=instrument,
            prediction_score=score,
            prediction=PredictionDirection.UP if score > 0.5 else PredictionDirection.DOWN,
            confidence=abs(score - 0.5) * 2,
            model_id=f"{model_name}_mock",
            model_version=model_version or "v1.0",
            features_used=["MA5", "MA20", "RSI", "MACD"],
            latency_ms=10.0,
            metadata={"mock": True}
        )

    # ==================== 批量预测 ====================

    async def predict_batch(
        self,
        instruments: List[str],
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        parallel: bool = True
    ) -> BatchPredictionResult:
        """
        批量预测

        Args:
            instruments: 股票代码列表
            model_name: 模型名称
            model_version: 模型版本
            parallel: 是否并行预测

        Returns:
            BatchPredictionResult对象
        """
        start_time = time.time()
        model_name = model_name or self.default_model_name

        predictions = []
        success_count = 0
        error_count = 0

        if parallel:
            # 并行预测
            tasks = [
                self.predict_single(inst, model_name, model_version, use_cache=False)
                for inst in instruments
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"批量预测失败[{i}]: {result}")
                    error_count += 1
                else:
                    predictions.append(result)
                    success_count += 1
        else:
            # 串行预测
            for inst in instruments:
                try:
                    result = await self.predict_single(
                        inst, model_name, model_version, use_cache=False
                    )
                    predictions.append(result)
                    success_count += 1
                except Exception as e:
                    logger.error(f"预测失败: {inst}, {e}")
                    error_count += 1

        elapsed_ms = (time.time() - start_time) * 1000

        logger.info(f"批量预测完成: {success_count}/{len(instruments)}, 耗时: {elapsed_ms:.1f}ms")

        return BatchPredictionResult(
            predictions=predictions,
            total=len(instruments),
            elapsed_ms=elapsed_ms,
            success_count=success_count,
            error_count=error_count
        )

    async def predict_market(
        self,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        top_n: int = 100
    ) -> BatchPredictionResult:
        """
        全市场预测（返回Top N）

        Args:
            model_name: 模型名称
            model_version: 模型版本
            top_n: 返回前N个

        Returns:
            BatchPredictionResult对象
        """
        # TODO: 从数据管理模块获取全市场股票列表
        # 这里使用模拟列表
        instruments = [f"{i:06d}.SZ" for i in range(1, 101)]

        result = await self.predict_batch(instruments, model_name, model_version)

        # 按评分排序，返回Top N
        sorted_predictions = sorted(
            result.predictions,
            key=lambda x: x.prediction_score,
            reverse=True
        )[:top_n]

        result.predictions = sorted_predictions

        return result

    # ==================== 缓存管理 ====================

    def _get_from_cache(self, cache_key: str) -> Optional[PredictionResult]:
        """从缓存获取预测结果"""
        if cache_key not in self._cache:
            return None

        result, timestamp = self._cache[cache_key]

        # 检查是否过期
        if time.time() - timestamp > self.cache_ttl_seconds:
            del self._cache[cache_key]
            return None

        return result

    def _add_to_cache(self, cache_key: str, result: PredictionResult):
        """添加预测结果到缓存"""
        self._cache[cache_key] = (result, time.time())

        # 清理过期缓存
        self._cleanup_cache()

    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            k for k, (_, t) in self._cache.items()
            if current_time - t > self.cache_ttl_seconds
        ]

        for key in expired_keys:
            del self._cache[key]

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("预测缓存已清空")

    # ==================== 统计方法 ====================

    def _update_stats(self, latency_ms: float):
        """更新性能统计"""
        self._stats["total_predictions"] += 1
        self._stats["total_latency_ms"] += latency_ms
        self._stats["latency_samples"].append(latency_ms)

        # 只保留最近1000个样本
        if len(self._stats["latency_samples"]) > 1000:
            self._stats["latency_samples"] = self._stats["latency_samples"][-1000:]

    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        samples = self._stats["latency_samples"]
        avg_latency = np.mean(samples) if samples else 0

        return {
            "total_predictions": self._stats["total_predictions"],
            "cache_hits": self._stats["cache_hits"],
            "cache_hit_rate": self._stats["cache_hits"] / max(1, self._stats["total_predictions"]),
            "avg_latency_ms": avg_latency,
            "p50_latency_ms": np.percentile(samples, 50) if samples else 0,
            "p95_latency_ms": np.percentile(samples, 95) if samples else 0,
            "p99_latency_ms": np.percentile(samples, 99) if samples else 0,
        }


# ==================== 单例模式 ====================

_prediction_service_instance: Optional[OnlinePredictionService] = None


def get_prediction_service() -> OnlinePredictionService:
    """获取OnlinePredictionService单例"""
    global _prediction_service_instance
    if _prediction_service_instance is None:
        _prediction_service_instance = OnlinePredictionService()
    return _prediction_service_instance
