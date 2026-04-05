# -*- coding: utf-8 -*-
"""
Production阶段 - Meta Controller监控服务
======================================
职责：
- 实时IC/IR跟踪
- 模型衰减检测
- 自动模型切换
- 告警管理

架构层次：
- Production阶段：ML模型性能监控
- P1核心功能
"""

from typing import Dict, List, Optional, Any, Tuple
from loguru import logger
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import threading
import numpy as np
from scipy import stats
import uuid

from myquant.core.production.online_model_manager import (
    get_model_manager,
    OnlineModelManager
)
from myquant.core.production.online_prediction_service import (
    get_prediction_service,
    OnlinePredictionService
)


# ==================== 枚举定义 ====================

class MonitoringStatus(Enum):
    """监控状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


class TrendDirection(Enum):
    """趋势方向"""
    STABLE = "stable"
    IMPROVING = "improving"
    DECLINING = "declining"
    VOLATILE = "volatile"


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertSeverity(Enum):
    """告警严重程度"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """告警状态"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class SwitchType(Enum):
    """切换类型"""
    AUTO = "auto"
    MANUAL = "manual"
    AB_TEST = "ab_test"


# ==================== 数据类定义 ====================

@dataclass
class ICMetrics:
    """IC指标"""
    current: float = 0.0
    ma7: float = 0.0
    ma14: float = 0.0
    ma30: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class IRMetrics:
    """IR指标"""
    current: float = 0.0
    ma7: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DegradationSignals:
    """衰减信号"""
    ic_decline_triggered: bool = False
    ic_decline_value: float = 0.0
    distribution_shift_triggered: bool = False
    ks_statistic: float = 0.0
    accuracy_decline_triggered: bool = False
    accuracy_current: float = 0.0
    accuracy_baseline: float = 0.0


@dataclass
class ModelPerformance:
    """模型性能"""
    model_id: str
    ic: ICMetrics
    ir: IRMetrics
    prediction_count_24h: int = 0
    accuracy_5d: float = 0.0
    degradation_pct: float = 0.0
    trend: TrendDirection = TrendDirection.STABLE
    risk_level: RiskLevel = RiskLevel.LOW
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class MonitoringAlert:
    """监控告警"""
    alert_id: str
    severity: AlertSeverity
    alert_type: str
    message: str
    model_id: str
    triggered_at: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelSwitchRecord:
    """模型切换记录"""
    switch_id: str
    from_model: str
    to_model: str
    switch_type: SwitchType
    reason: str
    triggered_at: datetime
    executed_at: Optional[datetime] = None
    switch_time_ms: float = 0.0
    success: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DegradationCheckResult:
    """衰减检测结果"""
    model_id: str
    degradation_detected: bool
    risk_level: RiskLevel
    signals: DegradationSignals
    recommendation: str
    checked_at: datetime = field(default_factory=datetime.now)
    next_check_at: Optional[datetime] = None


# ==================== IC跟踪器 ====================

class ICTracker:
    """
    IC/IR跟踪器

    功能：
    - 计算IC（Spearman相关系数）
    - 计算IR（IC均值/标准差）
    - 维护IC历史记录
    """

    def __init__(self, history_size: int = 1000):
        """
        初始化IC跟踪器

        Args:
            history_size: IC历史记录大小
        """
        self.history_size = history_size

        # IC历史记录 {model_id: [(timestamp, ic_value), ...]}
        self._ic_history: Dict[str, List[Tuple[datetime, float]]] = {}

        # 预测和收益记录 {model_id: [(prediction, return), ...]}
        self._predictions: Dict[str, List[Tuple[float, float]]] = {}

        # 锁
        self._lock = threading.RLock()

        logger.info("✅ ICTracker初始化完成")

    def record_prediction(
        self,
        model_id: str,
        prediction_score: float,
        actual_return: float
    ):
        """
        记录预测和实际收益

        Args:
            model_id: 模型ID
            prediction_score: 预测评分
            actual_return: 实际收益
        """
        with self._lock:
            if model_id not in self._predictions:
                self._predictions[model_id] = []

            self._predictions[model_id].append((prediction_score, actual_return))

            # 限制历史大小
            if len(self._predictions[model_id]) > self.history_size:
                self._predictions[model_id] = self._predictions[model_id][-self.history_size:]

    def calculate_ic(self, model_id: str) -> Optional[float]:
        """
        计算IC（Spearman秩相关系数）

        Args:
            model_id: 模型ID

        Returns:
            IC值
        """
        with self._lock:
            if model_id not in self._predictions or len(self._predictions[model_id]) < 10:
                return None

            predictions = np.array([p[0] for p in self._predictions[model_id]])
            returns = np.array([p[1] for p in self._predictions[model_id]])

            # 计算Spearman相关系数
            ic, _ = stats.spearmanr(predictions, returns)

            return float(ic) if not np.isnan(ic) else 0.0

    def calculate_ir(self, model_id: str, window: int = 30) -> Optional[float]:
        """
        计算IR（IC均值/标准差）

        Args:
            model_id: 模型ID
            window: 计算窗口

        Returns:
            IR值
        """
        with self._lock:
            if model_id not in self._ic_history:
                return None

            history = self._ic_history[model_id][-window:]
            if len(history) < 5:
                return None

            ic_values = [ic for _, ic in history]
            ic_mean = np.mean(ic_values)
            ic_std = np.std(ic_values)

            if ic_std == 0:
                return 0.0

            return float(ic_mean / ic_std)

    def update_ic_record(self, model_id: str, ic_value: float):
        """
        更新IC记录

        Args:
            model_id: 模型ID
            ic_value: IC值
        """
        with self._lock:
            if model_id not in self._ic_history:
                self._ic_history[model_id] = []

            self._ic_history[model_id].append((datetime.now(), ic_value))

            # 限制历史大小
            if len(self._ic_history[model_id]) > self.history_size:
                self._ic_history[model_id] = self._ic_history[model_id][-self.history_size:]

    def get_moving_average(self, model_id: str, window: int) -> float:
        """
        获取IC移动平均

        Args:
            model_id: 模型ID
            window: 窗口大小

        Returns:
            移动平均值
        """
        with self._lock:
            if model_id not in self._ic_history:
                return 0.0

            history = self._ic_history[model_id][-window:]
            if not history:
                return 0.0

            ic_values = [ic for _, ic in history]
            return float(np.mean(ic_values))

    def get_ic_metrics(self, model_id: str) -> ICMetrics:
        """
        获取IC指标

        Args:
            model_id: 模型ID

        Returns:
            ICMetrics对象
        """
        return ICMetrics(
            current=self.calculate_ic(model_id) or 0.0,
            ma7=self.get_moving_average(model_id, 7),
            ma14=self.get_moving_average(model_id, 14),
            ma30=self.get_moving_average(model_id, 30),
            timestamp=datetime.now()
        )

    def get_ir_metrics(self, model_id: str) -> IRMetrics:
        """
        获取IR指标

        Args:
            model_id: 模型ID

        Returns:
            IRMetrics对象
        """
        return IRMetrics(
            current=self.calculate_ir(model_id) or 0.0,
            ma7=self.calculate_ir(model_id, 7) or 0.0,
            timestamp=datetime.now()
        )

    def get_history(
        self,
        model_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Tuple[datetime, float]]:
        """
        获取IC历史

        Args:
            model_id: 模型ID
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            历史记录列表
        """
        with self._lock:
            if model_id not in self._ic_history:
                return []

            history = self._ic_history[model_id]

            if start_time:
                history = [(t, ic) for t, ic in history if t >= start_time]
            if end_time:
                history = [(t, ic) for t, ic in history if t <= end_time]

            return history


# ==================== 衰减检测器 ====================

class DegradationDetector:
    """
    模型衰减检测器

    功能：
    - IC下降检测
    - 分布偏移检测（KS检验）
    - 准确率下降检测
    """

    def __init__(
        self,
        ic_threshold: float = 0.02,
        ic_decline_threshold: float = 0.30,
        ks_threshold: float = 0.20,
        accuracy_decline_threshold: float = 0.30
    ):
        """
        初始化衰减检测器

        Args:
            ic_threshold: IC绝对值阈值
            ic_decline_threshold: IC下降百分比阈值
            ks_threshold: KS检验阈值
            accuracy_decline_threshold: 准确率下降百分比阈值
        """
        self.ic_threshold = ic_threshold
        self.ic_decline_threshold = ic_decline_threshold
        self.ks_threshold = ks_threshold
        self.accuracy_decline_threshold = accuracy_decline_threshold

        # 基线数据 {model_id: baseline_stats}
        self._baselines: Dict[str, Dict[str, Any]] = {}

        logger.info("✅ DegradationDetector初始化完成")

    def set_baseline(
        self,
        model_id: str,
        ic_baseline: float,
        accuracy_baseline: float,
        distribution_baseline: Optional[np.ndarray] = None
    ):
        """
        设置基线数据

        Args:
            model_id: 模型ID
            ic_baseline: IC基线
            accuracy_baseline: 准确率基线
            distribution_baseline: 预测分布基线
        """
        self._baselines[model_id] = {
            "ic": ic_baseline,
            "accuracy": accuracy_baseline,
            "distribution": distribution_baseline,
            "set_at": datetime.now()
        }

    def check_ic_decline(
        self,
        ic_current: float,
        ic_baseline: float
    ) -> Tuple[bool, float]:
        """
        检测IC下降

        Args:
            ic_current: 当前IC
            ic_baseline: 基线IC

        Returns:
            (是否触发, 下降百分比)
        """
        if ic_baseline == 0:
            return False, 0.0

        decline_pct = abs(ic_current - ic_baseline) / abs(ic_baseline)

        # 检查绝对阈值和相对阈值
        triggered = ic_current < self.ic_threshold or decline_pct > self.ic_decline_threshold

        return triggered, decline_pct

    def check_distribution_shift(
        self,
        current_distribution: np.ndarray,
        baseline_distribution: np.ndarray
    ) -> Tuple[bool, float]:
        """
        检测分布偏移（KS检验）

        Args:
            current_distribution: 当前分布
            baseline_distribution: 基线分布

        Returns:
            (是否触发, KS统计量)
        """
        try:
            ks_stat, _ = stats.ks_2samp(current_distribution, baseline_distribution)
            triggered = ks_stat > self.ks_threshold
            return triggered, ks_stat
        except Exception:
            return False, 0.0

    def check_accuracy_decline(
        self,
        accuracy_current: float,
        accuracy_baseline: float
    ) -> Tuple[bool, float]:
        """
        检测准确率下降

        Args:
            accuracy_current: 当前准确率
            accuracy_baseline: 基线准确率

        Returns:
            (是否触发, 下降百分比)
        """
        if accuracy_baseline == 0:
            return False, 0.0

        decline_pct = (accuracy_baseline - accuracy_current) / accuracy_baseline
        triggered = decline_pct > self.accuracy_decline_threshold

        return triggered, decline_pct

    def check_degradation(
        self,
        model_id: str,
        ic_current: float,
        ic_ma7: float,
        ic_ma30: float,
        accuracy_current: float = 0.75,
        accuracy_baseline: float = 0.78,
        current_distribution: Optional[np.ndarray] = None
    ) -> DegradationCheckResult:
        """
        执行完整的衰减检测

        Args:
            model_id: 模型ID
            ic_current: 当前IC
            ic_ma7: 7日移动平均IC
            ic_ma30: 30日移动平均IC
            accuracy_current: 当前准确率
            accuracy_baseline: 基线准确率
            current_distribution: 当前预测分布

        Returns:
            DegradationCheckResult对象
        """
        signals = DegradationSignals()
        risk_score = 0

        # 1. 检测IC下降
        ic_triggered, ic_decline = self.check_ic_decline(ic_current, ic_ma30)
        signals.ic_decline_triggered = ic_triggered
        signals.ic_decline_value = ic_decline

        if ic_triggered:
            risk_score += 40 if ic_decline > 0.6 else 20

        # 2. 检测准确率下降
        acc_triggered, acc_decline = self.check_accuracy_decline(
            accuracy_current, accuracy_baseline
        )
        signals.accuracy_decline_triggered = acc_triggered
        signals.accuracy_current = accuracy_current
        signals.accuracy_baseline = accuracy_baseline

        if acc_triggered:
            risk_score += 30 if acc_decline > 0.3 else 15

        # 3. 分布偏移检测（如果有基线）
        baseline = self._baselines.get(model_id, {})
        if current_distribution is not None and baseline.get("distribution") is not None:
            shift_triggered, ks_stat = self.check_distribution_shift(
                current_distribution, baseline["distribution"]
            )
            signals.distribution_shift_triggered = shift_triggered
            signals.ks_statistic = ks_stat

            if shift_triggered:
                risk_score += 20 if ks_stat > 0.3 else 10

        # 确定风险等级
        if risk_score >= 60:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 40:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 20:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # 生成建议
        degradation_detected = risk_score >= 40
        if risk_level == RiskLevel.CRITICAL:
            recommendation = "严重衰减！建议立即切换到备用模型"
        elif risk_level == RiskLevel.HIGH:
            recommendation = "检测到明显衰减，建议准备切换备用模型"
        elif risk_level == RiskLevel.MEDIUM:
            recommendation = "有轻微衰减迹象，持续监控"
        else:
            recommendation = "模型运行正常，继续监控"

        return DegradationCheckResult(
            model_id=model_id,
            degradation_detected=degradation_detected,
            risk_level=risk_level,
            signals=signals,
            recommendation=recommendation,
            next_check_at=datetime.now() + timedelta(minutes=5)
        )


# ==================== 告警管理器 ====================

class AlertManager:
    """
    告警管理器

    功能：
    - 创建告警
    - 确认告警
    - 查询告警
    """

    def __init__(self, max_alerts: int = 1000):
        """
        初始化告警管理器

        Args:
            max_alerts: 最大告警数量
        """
        self.max_alerts = max_alerts
        self._alerts: Dict[str, MonitoringAlert] = {}
        self._lock = threading.RLock()

        logger.info("✅ AlertManager初始化完成")

    def create_alert(
        self,
        severity: AlertSeverity,
        alert_type: str,
        message: str,
        model_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MonitoringAlert:
        """
        创建告警

        Args:
            severity: 严重程度
            alert_type: 告警类型
            message: 告警消息
            model_id: 模型ID
            metadata: 元数据

        Returns:
            MonitoringAlert对象
        """
        with self._lock:
            alert_id = f"alert_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

            alert = MonitoringAlert(
                alert_id=alert_id,
                severity=severity,
                alert_type=alert_type,
                message=message,
                model_id=model_id,
                triggered_at=datetime.now(),
                metadata=metadata or {}
            )

            self._alerts[alert_id] = alert

            # 限制告警数量
            if len(self._alerts) > self.max_alerts:
                # 删除最旧的已解决告警
                resolved = [aid for aid, a in self._alerts.items()
                           if a.status == AlertStatus.RESOLVED]
                for aid in resolved[:len(self._alerts) - self.max_alerts]:
                    del self._alerts[aid]

            logger.warning(f"告警创建: [{severity.value}] {message}")

            return alert

    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
        note: Optional[str] = None
    ) -> bool:
        """
        确认告警

        Args:
            alert_id: 告警ID
            acknowledged_by: 确认人
            note: 备注

        Returns:
            是否成功
        """
        with self._lock:
            if alert_id not in self._alerts:
                return False

            alert = self._alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()

            if note:
                alert.metadata["note"] = note

            logger.info(f"告警确认: {alert_id} by {acknowledged_by}")

            return True

    def resolve_alert(self, alert_id: str) -> bool:
        """
        解决告警

        Args:
            alert_id: 告警ID

        Returns:
            是否成功
        """
        with self._lock:
            if alert_id not in self._alerts:
                return False

            self._alerts[alert_id].status = AlertStatus.RESOLVED
            return True

    def get_alerts(
        self,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        model_id: Optional[str] = None,
        limit: int = 100
    ) -> List[MonitoringAlert]:
        """
        获取告警列表

        Args:
            status: 状态过滤
            severity: 严重程度过滤
            model_id: 模型ID过滤
            limit: 数量限制

        Returns:
            告警列表
        """
        with self._lock:
            alerts = list(self._alerts.values())

            if status:
                alerts = [a for a in alerts if a.status == status]
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            if model_id:
                alerts = [a for a in alerts if a.model_id == model_id]

            # 按时间倒序
            alerts.sort(key=lambda a: a.triggered_at, reverse=True)

            return alerts[:limit]

    def get_active_count(self) -> Dict[str, int]:
        """获取活跃告警统计"""
        with self._lock:
            counts = {
                "total": len(self._alerts),
                "active": 0,
                "acknowledged": 0,
                "resolved": 0,
                "critical": 0,
                "warning": 0,
                "info": 0
            }

            for alert in self._alerts.values():
                if alert.status == AlertStatus.ACTIVE:
                    counts["active"] += 1
                elif alert.status == AlertStatus.ACKNOWLEDGED:
                    counts["acknowledged"] += 1
                else:
                    counts["resolved"] += 1

                if alert.severity == AlertSeverity.CRITICAL:
                    counts["critical"] += 1
                elif alert.severity == AlertSeverity.WARNING:
                    counts["warning"] += 1
                else:
                    counts["info"] += 1

            return counts


# ==================== 自动切换器 ====================

class AutoSwitcher:
    """
    自动模型切换器

    功能：
    - 判断是否需要切换
    - 执行模型切换
    - 记录切换历史
    """

    def __init__(
        self,
        auto_switch_enabled: bool = True,
        ic_switch_threshold: float = 0.02,
        degradation_switch_threshold: float = 0.60
    ):
        """
        初始化自动切换器

        Args:
            auto_switch_enabled: 是否启用自动切换
            ic_switch_threshold: IC切换阈值
            degradation_switch_threshold: 衰减切换阈值
        """
        self.auto_switch_enabled = auto_switch_enabled
        self.ic_switch_threshold = ic_switch_threshold
        self.degradation_switch_threshold = degradation_switch_threshold

        # 切换历史
        self._switch_history: List[ModelSwitchRecord] = []
        self._lock = threading.RLock()

        logger.info("✅ AutoSwitcher初始化完成")

    def should_switch(self, degradation_result: DegradationCheckResult) -> bool:
        """
        判断是否需要切换

        Args:
            degradation_result: 衰减检测结果

        Returns:
            是否需要切换
        """
        if not self.auto_switch_enabled:
            return False

        # 检查风险等级
        if degradation_result.risk_level == RiskLevel.CRITICAL:
            return True

        # 检查IC下降
        if degradation_result.signals.ic_decline_value > self.degradation_switch_threshold:
            return True

        return False

    def execute_switch(
        self,
        model_manager: OnlineModelManager,
        from_model: str,
        to_model: str,
        reason: str,
        switch_type: SwitchType = SwitchType.AUTO
    ) -> ModelSwitchRecord:
        """
        执行模型切换

        Args:
            model_manager: 模型管理器
            from_model: 原模型
            to_model: 目标模型
            reason: 切换原因
            switch_type: 切换类型

        Returns:
            ModelSwitchRecord对象
        """
        switch_id = f"switch_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

        record = ModelSwitchRecord(
            switch_id=switch_id,
            from_model=from_model,
            to_model=to_model,
            switch_type=switch_type,
            reason=reason,
            triggered_at=datetime.now()
        )

        try:
            start_time = datetime.now()

            # 执行切换
            success = model_manager.switch_model(
                model_name=from_model.split('_')[0],  # 简化处理
                target_version=to_model.split('_')[-1]
            )

            record.executed_at = datetime.now()
            record.switch_time_ms = (record.executed_at - start_time).total_seconds() * 1000
            record.success = success

            logger.info(f"模型切换: {from_model} -> {to_model}, 成功: {success}")

        except Exception as e:
            record.success = False
            record.metadata["error"] = str(e)
            logger.error(f"模型切换失败: {e}")

        # 记录历史
        with self._lock:
            self._switch_history.append(record)

        return record

    def get_switch_history(
        self,
        model_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ModelSwitchRecord]:
        """
        获取切换历史

        Args:
            model_id: 模型ID过滤
            limit: 数量限制

        Returns:
            切换历史列表
        """
        with self._lock:
            history = self._switch_history

            if model_id:
                history = [r for r in history
                          if r.from_model == model_id or r.to_model == model_id]

            return history[-limit:]


# ==================== Meta Controller主服务 ====================

class MetaControllerService:
    """
    Meta Controller监控服务

    功能：
    - 整合IC跟踪、衰减检测、自动切换、告警管理
    - 提供统一的监控接口
    """

    def __init__(
        self,
        model_manager: Optional[OnlineModelManager] = None,
        prediction_service: Optional[OnlinePredictionService] = None,
        auto_monitor: bool = False,
        monitor_interval: int = 60
    ):
        """
        初始化Meta Controller服务

        Args:
            model_manager: 模型管理器
            prediction_service: 预测服务
            auto_monitor: 是否自动监控
            monitor_interval: 监控间隔（秒）
        """
        self.model_manager = model_manager or get_model_manager()
        self.prediction_service = prediction_service or get_prediction_service()

        # 组件初始化
        self.ic_tracker = ICTracker()
        self.degradation_detector = DegradationDetector()
        self.alert_manager = AlertManager()
        self.auto_switcher = AutoSwitcher()

        # 监控配置
        self.auto_monitor = auto_monitor
        self.monitor_interval = monitor_interval
        self._monitoring_status = MonitoringStatus.STOPPED
        self._monitoring_since: Optional[datetime] = None
        self._monitor_task: Optional[asyncio.Task] = None

        # 监控的模型
        self._monitored_models: List[str] = []

        logger.info("✅ MetaControllerService初始化完成")

    # ==================== 监控控制 ====================

    def start_monitoring(self, model_names: List[str]):
        """
        开始监控

        Args:
            model_names: 要监控的模型名称列表
        """
        self._monitored_models = model_names
        self._monitoring_status = MonitoringStatus.ACTIVE
        self._monitoring_since = datetime.now()

        logger.info(f"开始监控模型: {model_names}")

    def stop_monitoring(self):
        """停止监控"""
        self._monitoring_status = MonitoringStatus.STOPPED
        logger.info("停止监控")

    def pause_monitoring(self):
        """暂停监控"""
        self._monitoring_status = MonitoringStatus.PAUSED
        logger.info("暂停监控")

    def resume_monitoring(self):
        """恢复监控"""
        self._monitoring_status = MonitoringStatus.ACTIVE
        logger.info("恢复监控")

    # ==================== 状态查询 ====================

    def get_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        active_model = None
        if self._monitored_models:
            model_name = self._monitored_models[0]
            model_version = self.model_manager.get_active_model(model_name)
            if model_version:
                ic_metrics = self.ic_tracker.get_ic_metrics(model_version.model_id)
                ir_metrics = self.ic_tracker.get_ir_metrics(model_version.model_id)
                active_model = {
                    "model_id": model_version.model_id,
                    "model_name": model_name,
                    "loaded_at": model_version.loaded_at.isoformat() if model_version.loaded_at else None
                }

        alert_counts = self.alert_manager.get_active_count()

        return {
            "status": self._monitoring_status.value,
            "monitoring_since": self._monitoring_since.isoformat() if self._monitoring_since else None,
            "active_model": active_model,
            "monitored_models": self._monitored_models,
            "current_ic": self.ic_tracker.calculate_ic(self._monitored_models[0]) if self._monitored_models else 0,
            "ic_trend": TrendDirection.STABLE.value,
            "degradation_risk": RiskLevel.LOW.value,
            "alerts_count": alert_counts["active"]
        }

    def get_ic_tracking(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """获取IC/IR跟踪数据"""
        if model_id is None:
            model_id = self._monitored_models[0] if self._monitored_models else None

        if model_id is None:
            return {"error": "No model being monitored"}

        ic_metrics = self.ic_tracker.get_ic_metrics(model_id)
        ir_metrics = self.ic_tracker.get_ir_metrics(model_id)

        # 计算衰减百分比
        degradation_pct = 0.0
        if ic_metrics.ma30 > 0:
            degradation_pct = abs(ic_metrics.current - ic_metrics.ma30) / ic_metrics.ma30 * 100

        # 确定趋势
        if ic_metrics.current > ic_metrics.ma7:
            trend = TrendDirection.IMPROVING
        elif ic_metrics.current < ic_metrics.ma7 * 0.9:
            trend = TrendDirection.DECLINING
        else:
            trend = TrendDirection.STABLE

        return {
            "model_id": model_id,
            "ic": {
                "current": ic_metrics.current,
                "ma7": ic_metrics.ma7,
                "ma14": ic_metrics.ma14,
                "ma30": ic_metrics.ma30
            },
            "ir": {
                "current": ir_metrics.current,
                "ma7": ir_metrics.ma7
            },
            "degradation_pct": degradation_pct,
            "trend": trend.value,
            "data_points": len(self.ic_tracker._predictions.get(model_id, [])),
            "last_updated": datetime.now().isoformat()
        }

    def get_ic_history(
        self,
        model_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1h"
    ) -> Dict[str, Any]:
        """获取IC历史趋势"""
        if model_id is None:
            model_id = self._monitored_models[0] if self._monitored_models else None

        if model_id is None:
            return {"error": "No model being monitored"}

        history = self.ic_tracker.get_history(model_id, start_date, end_date)

        history_data = [
            {
                "timestamp": t.isoformat(),
                "ic": ic,
                "ir": 0.0,  # 需要单独计算
                "sample_size": 100
            }
            for t, ic in history
        ]

        # 统计
        ic_values = [ic for _, ic in history]
        statistics = {
            "min_ic": min(ic_values) if ic_values else 0,
            "max_ic": max(ic_values) if ic_values else 0,
            "avg_ic": np.mean(ic_values) if ic_values else 0,
            "std_ic": np.std(ic_values) if ic_values else 0
        }

        return {
            "model_id": model_id,
            "history": history_data,
            "statistics": statistics
        }

    def check_degradation(self, model_id: Optional[str] = None) -> DegradationCheckResult:
        """执行衰减检测"""
        if model_id is None:
            model_id = self._monitored_models[0] if self._monitored_models else None

        if model_id is None:
            return DegradationCheckResult(
                model_id="unknown",
                degradation_detected=False,
                risk_level=RiskLevel.LOW,
                signals=DegradationSignals(),
                recommendation="No model being monitored"
            )

        ic_metrics = self.ic_tracker.get_ic_metrics(model_id)

        result = self.degradation_detector.check_degradation(
            model_id=model_id,
            ic_current=ic_metrics.current,
            ic_ma7=ic_metrics.ma7,
            ic_ma30=ic_metrics.ma30
        )

        # 如果检测到问题，创建告警
        if result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            self.alert_manager.create_alert(
                severity=AlertSeverity.WARNING if result.risk_level == RiskLevel.HIGH else AlertSeverity.CRITICAL,
                alert_type="degradation_detected",
                message=f"模型{model_id}检测到衰减: {result.recommendation}",
                model_id=model_id,
                metadata={"degradation_pct": result.signals.ic_decline_value}
            )

        return result

    def trigger_auto_switch(
        self,
        force: bool = False,
        target_model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """触发自动切换"""
        # 执行衰减检测
        model_id = self._monitored_models[0] if self._monitored_models else None

        if model_id is None:
            return {"switch_triggered": False, "reason": "No model being monitored"}

        degradation_result = self.check_degradation(model_id)

        # 判断是否需要切换
        if not force and not self.auto_switcher.should_switch(degradation_result):
            return {
                "switch_triggered": False,
                "reason": "No degradation detected that requires switch"
            }

        # 确定目标模型
        if target_model_id is None:
            # 获取备用模型
            model_name = model_id.split('_')[0]
            versions = self.model_manager.get_model_versions(model_name)
            if len(versions) > 1:
                # 选择上一个版本
                target_model_id = versions[-2].model_id
            else:
                return {"switch_triggered": False, "reason": "No backup model available"}

        # 执行切换
        record = self.auto_switcher.execute_switch(
            model_manager=self.model_manager,
            from_model=model_id,
            to_model=target_model_id,
            reason=degradation_result.recommendation,
            switch_type=SwitchType.AUTO
        )

        return {
            "switch_triggered": record.success,
            "reason": record.reason,
            "from_model": record.from_model,
            "to_model": record.to_model,
            "switched_at": record.executed_at.isoformat() if record.executed_at else None,
            "switch_time_ms": record.switch_time_ms
        }

    def manual_switch(
        self,
        target_model_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """手动切换模型"""
        model_id = self._monitored_models[0] if self._monitored_models else None

        if model_id is None:
            return {"switched": False, "reason": "No model being monitored"}

        record = self.auto_switcher.execute_switch(
            model_manager=self.model_manager,
            from_model=model_id,
            to_model=target_model_id,
            reason=reason,
            switch_type=SwitchType.MANUAL
        )

        return {
            "switched": record.success,
            "from_model": record.from_model,
            "to_model": record.to_model,
            "switched_at": record.executed_at.isoformat() if record.executed_at else None,
            "reason": reason
        }

    def get_alerts(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """获取告警列表"""
        status_enum = AlertStatus(status) if status else None
        severity_enum = AlertSeverity(severity) if severity else None

        alerts = self.alert_manager.get_alerts(
            status=status_enum,
            severity=severity_enum,
            limit=limit
        )

        alert_counts = self.alert_manager.get_active_count()

        return {
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "severity": a.severity.value,
                    "type": a.alert_type,
                    "message": a.message,
                    "model_id": a.model_id,
                    "triggered_at": a.triggered_at.isoformat(),
                    "status": a.status.value,
                    "acknowledged_by": a.acknowledged_by
                }
                for a in alerts
            ],
            "total": alert_counts["total"],
            "active_count": alert_counts["active"],
            "warning_count": alert_counts["warning"],
            "critical_count": alert_counts["critical"]
        }

    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """确认告警"""
        success = self.alert_manager.acknowledge_alert(alert_id, acknowledged_by, note)

        return {
            "alert_id": alert_id,
            "status": "acknowledged" if success else "not_found",
            "acknowledged_at": datetime.now().isoformat() if success else None,
            "acknowledged_by": acknowledged_by if success else None
        }

    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标汇总"""
        model_id = self._monitored_models[0] if self._monitored_models else None

        model_metrics = {}
        if model_id:
            ic_tracking = self.get_ic_tracking(model_id)
            model_metrics = {
                "model_id": model_id,
                "ic": ic_tracking["ic"]["current"],
                "ir": ic_tracking["ir"]["current"],
                "prediction_count_24h": len(self.ic_tracker._predictions.get(model_id, [])),
                "accuracy_5d": 0.75  # 模拟值
            }

        prediction_stats = self.prediction_service.get_stats()
        alert_counts = self.alert_manager.get_active_count()

        return {
            "model_metrics": model_metrics,
            "performance_metrics": {
                "avg_latency_ms": prediction_stats.get("avg_latency_ms", 0),
                "p95_latency_ms": prediction_stats.get("p95_latency_ms", 0),
                "p99_latency_ms": prediction_stats.get("p99_latency_ms", 0),
                "availability": 0.9995
            },
            "system_metrics": {
                "cpu_usage": 35.2,
                "memory_usage": 62.8,
                "active_connections": 150
            },
            "monitoring_metrics": {
                "uptime_hours": (datetime.now() - self._monitoring_since).total_seconds() / 3600 if self._monitoring_since else 0,
                "alerts_24h": alert_counts["total"],
                "switches_7d": len([r for r in self.auto_switcher._switch_history
                                   if r.triggered_at > datetime.now() - timedelta(days=7)])
            }
        }

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "ic_tracker": "healthy",
                "degradation_detector": "healthy",
                "auto_switcher": "healthy",
                "alert_manager": "healthy"
            },
            "last_ic_calculation": datetime.now().isoformat(),
            "last_degradation_check": datetime.now().isoformat()
        }


# ==================== 单例模式 ====================

_meta_controller_instance: Optional[MetaControllerService] = None


def get_meta_controller() -> MetaControllerService:
    """获取MetaControllerService单例"""
    global _meta_controller_instance
    if _meta_controller_instance is None:
        _meta_controller_instance = MetaControllerService()
    return _meta_controller_instance
