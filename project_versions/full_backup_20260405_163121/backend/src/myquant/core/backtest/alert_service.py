# -*- coding: utf-8 -*-
"""
Validation阶段 - 预警系统服务
==============================
职责：
- 预警规则管理
- 规则预警（阈值、变化率、模式匹配）
- AI智能预警
- 预警发送和确认

架构层次：
- Validation阶段：监控策略运行并触发预警
- 支持多种预警规则类型
- 可集成DeepSeek进行AI预警分析
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from loguru import logger
from datetime import datetime
from enum import Enum
import uuid
import pandas as pd
import numpy as np


class RuleType(Enum):
    """规则类型"""
    THRESHOLD = "threshold"                 # 阈值触发
    RATE_OF_CHANGE = "rate_of_change"     # 变化率触发
    PATTERN = "pattern"                    # 模式匹配


class Severity(Enum):
    """严重程度"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlertRule:
    """预警规则"""
    rule_id: str                           # 规则ID
    rule_name: str                         # 规则名称
    rule_type: str                         # 规则类型（threshold/rate_of_change/pattern）
    condition: Dict[str, Any]              # 触发条件
    severity: str                          # 严重程度（info/warning/critical）
    enabled: bool = True                   # 是否启用
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""                  # 规则描述


@dataclass
class Alert:
    """预警消息"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""                      # 关联规则ID
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "info"                 # 严重程度
    message: str = ""                      # 预警消息
    metrics: Dict[str, float] = field(default_factory=dict)
    is_acknowledged: bool = False          # 是否已确认
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


class AlertService:
    """预警系统服务

    提供规则预警和AI智能预警功能
    """

    def __init__(self):
        """初始化预警服务"""
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.metrics_history: List[Dict[str, Any]] = []

        logger.info("AlertService initialized")

    def create_rule(
        self,
        rule_id: str,
        rule_name: str,
        rule_type: str,
        condition: Dict[str, Any],
        severity: str = "warning",
        description: str = ""
    ) -> AlertRule:
        """创建预警规则

        Args:
            rule_id: 规则ID
            rule_name: 规则名称
            rule_type: 规则类型（threshold/rate_of_change/pattern）
            condition: 触发条件
            severity: 严重程度
            description: 规则描述

        Returns:
            创建的规则对象
        """
        rule = AlertRule(
            rule_id=rule_id,
            rule_name=rule_name,
            rule_type=rule_type,
            condition=condition,
            severity=severity,
            description=description
        )

        self.rules[rule_id] = rule

        logger.info(
            f"Alert rule created: '{rule_name}' ({rule_type}, {severity})"
        )

        return rule

    def evaluate_rules(self, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """评估所有启用的规则

        Args:
            current_metrics: 当前指标数据

        Returns:
            触发的预警列表
        """
        triggered_alerts = []

        # 保存历史指标
        self.metrics_history.append({
            "metrics": current_metrics.copy(),
            "timestamp": datetime.now()
        })

        # 只保留最近100条历史
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]

        # 评估每个启用的规则
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue

            if self._check_rule(rule, current_metrics):
                # 规则触发，创建预警
                alert = self._create_alert_from_rule(rule, current_metrics)
                self.alerts[alert.alert_id] = alert

                triggered_alerts.append({
                    "alert_id": alert.alert_id,
                    "rule_id": rule_id,
                    "rule_name": rule.rule_name,
                    "severity": rule.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat()
                })

                logger.warning(
                    f"Alert triggered: '{rule.rule_name}' - {alert.message}"
                )

        return triggered_alerts

    def _check_rule(self, rule: AlertRule, metrics: Dict[str, float]) -> bool:
        """检查单个规则是否触发

        Args:
            rule: 规则对象
            metrics: 当前指标

        Returns:
            是否触发
        """
        if rule.rule_type == RuleType.THRESHOLD.value:
            return self._check_threshold_rule(rule, metrics)
        elif rule.rule_type == RuleType.RATE_OF_CHANGE.value:
            return self._check_rate_of_change_rule(rule, metrics)
        elif rule.rule_type == RuleType.PATTERN.value:
            return self._check_pattern_rule(rule, metrics)
        return False

    def _check_threshold_rule(self, rule: AlertRule, metrics: Dict[str, float]) -> bool:
        """检查阈值规则

        Example condition:
        {
            "metric": "drawdown",
            "operator": ">",
            "value": 0.2
        }
        """
        metric_name = rule.condition.get("metric")
        operator = rule.condition.get("operator")
        threshold = rule.condition.get("value")

        if metric_name not in metrics:
            return False

        current_value = metrics[metric_name]

        if operator == ">":
            return current_value > threshold
        elif operator == ">=":
            return current_value >= threshold
        elif operator == "<":
            return current_value < threshold
        elif operator == "<=":
            return current_value <= threshold
        elif operator == "==":
            return current_value == threshold
        elif operator == "!=":
            return current_value != threshold

        return False

    def _check_rate_of_change_rule(self, rule: AlertRule, metrics: Dict[str, float]) -> bool:
        """检查变化率规则

        Example condition:
        {
            "metric": "return",
            "window": 5,          # 检查最近5个数据点
            "threshold": 0.05      # 变化超过5%触发
        }
        """
        metric_name = rule.condition.get("metric")
        window = rule.condition.get("window", 5)
        threshold = rule.condition.get("threshold", 0.05)

        if len(self.metrics_history) < window + 1:
            return False

        # 获取窗口前后的值
        old_value = self.metrics_history[-window - 1]["metrics"].get(metric_name)
        new_value = metrics.get(metric_name)

        if old_value is None or new_value is None:
            return False

        # 计算变化率
        if old_value != 0:
            rate_of_change = abs((new_value - old_value) / old_value)
        else:
            rate_of_change = 0.0

        return rate_of_change > threshold

    def _check_pattern_rule(self, rule: AlertRule, metrics: Dict[str, float]) -> bool:
        """检查模式规则

        Example condition:
        {
            "pattern": "consecutive_decline",  # 连续下跌
            "metric": "return",
            "days": 3                         # 连续3天下跌
        }
        """
        pattern = rule.condition.get("pattern")
        metric_name = rule.condition.get("metric")

        if pattern == "consecutive_decline":
            days = rule.condition.get("days", 3)
            if len(self.metrics_history) < days:
                return False

            # 检查最近N天是否连续下跌
            for i in range(days):
                hist_metrics = self.metrics_history[-i - 1]["metrics"]
                value = hist_metrics.get(metric_name, 0)
                if value >= 0:  # 非负值（非下跌）
                    return False
            return True

        return False

    def _create_alert_from_rule(self, rule: AlertRule, metrics: Dict[str, float]) -> Alert:
        """从规则创建预警

        Args:
            rule: 触发的规则
            metrics: 当前指标

        Returns:
            预警对象
        """
        # 生成预警消息
        if rule.rule_type == RuleType.THRESHOLD.value:
            metric_name = rule.condition.get("metric")
            operator = rule.condition.get("operator")
            threshold = rule.condition.get("value")
            value = metrics.get(metric_name, 0)

            message = (
                f"{rule.rule_name}: {metric_name}={value:.4f} "
                f"{operator} {threshold} (threshold exceeded)"
            )
        else:
            message = f"{rule.rule_name}: {rule.description or rule.rule_type}"

        alert = Alert(
            rule_id=rule.rule_id,
            severity=rule.severity,
            message=message,
            metrics=metrics.copy()
        )

        return alert

    def send_alert(
        self,
        rule_id: str,
        message: str,
        severity: str = "info",
        metrics: Dict[str, float] = None
    ) -> Alert:
        """手动发送预警

        Args:
            rule_id: 关联规则ID
            message: 预警消息
            severity: 严重程度
            metrics: 指标数据

        Returns:
            创建的预警对象
        """
        alert = Alert(
            rule_id=rule_id,
            severity=severity,
            message=message,
            metrics=metrics or {}
        )

        self.alerts[alert.alert_id] = alert

        logger.info(
            f"Alert sent: [{severity.upper()}] {message}"
        )

        return alert

    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str = "system"
    ) -> Dict[str, Any]:
        """确认预警

        Args:
            alert_id: 预警ID
            acknowledged_by: 确认人

        Returns:
            确认结果
        """
        if alert_id not in self.alerts:
            return {
                "success": False,
                "message": "Alert not found"
            }

        alert = self.alerts[alert_id]
        alert.is_acknowledged = True
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = acknowledged_by

        logger.info(f"Alert acknowledged: {alert_id}")

        return {
            "success": True,
            "alert_id": alert_id,
            "acknowledged_at": alert.acknowledged_at.isoformat(),
            "acknowledged_by": acknowledged_by
        }

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """获取单个预警

        Args:
            alert_id: 预警ID

        Returns:
            预警对象或None
        """
        return self.alerts.get(alert_id)

    def get_alerts(
        self,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        limit: int = 100
    ) -> List[Alert]:
        """获取预警列表

        Args:
            severity: 过滤严重程度
            acknowledged: 过滤确认状态
            limit: 返回数量限制

        Returns:
            预警列表
        """
        alerts = list(self.alerts.values())

        # 过滤
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if acknowledged is not None:
            alerts = [a for a in alerts if a.is_acknowledged == acknowledged]

        # 按时间倒序排序
        alerts.sort(key=lambda a: a.timestamp, reverse=True)

        # 限制数量
        return alerts[:limit]

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """获取规则

        Args:
            rule_id: 规则ID

        Returns:
            规则对象或None
        """
        return self.rules.get(rule_id)

    def get_rules(self, enabled_only: bool = False) -> List[AlertRule]:
        """获取规则列表

        Args:
            enabled_only: 只返回启用的规则

        Returns:
            规则列表
        """
        rules = list(self.rules.values())

        if enabled_only:
            rules = [r for r in rules if r.enabled]

        return rules

    def delete_rule(self, rule_id: str) -> bool:
        """删除规则

        Args:
            rule_id: 规则ID

        Returns:
            是否成功
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Rule deleted: {rule_id}")
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """启用规则

        Args:
            rule_id: 规则ID

        Returns:
            是否成功
        """
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            logger.info(f"Rule enabled: {rule_id}")
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """禁用规则

        Args:
            rule_id: 规则ID

        Returns:
            是否成功
        """
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            logger.info(f"Rule disabled: {rule_id}")
            return True
        return False

    def get_alert_statistics(self) -> Dict[str, Any]:
        """获取预警统计

        Returns:
            统计信息
        """
        total_alerts = len(self.alerts)
        unacknowledged = len([a for a in self.alerts.values() if not a.is_acknowledged])

        severity_count = {}
        for alert in self.alerts.values():
            severity_count[alert.severity] = severity_count.get(alert.severity, 0) + 1

        return {
            "total_alerts": total_alerts,
            "unacknowledged_alerts": unacknowledged,
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules.values() if r.enabled]),
            "severity_distribution": severity_count
        }
