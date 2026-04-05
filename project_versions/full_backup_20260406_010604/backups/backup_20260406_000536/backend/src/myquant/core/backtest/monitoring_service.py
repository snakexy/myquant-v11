# -*- coding: utf-8 -*-
"""
Validation阶段 - 实时监控服务
==============================
职责：
- 实时策略性能监控
- 异常检测和预警
- 监控报告生成
- 多策略并行监控

架构层次：
- Validation阶段：实时监控策略运行状态
- 支持统计方法和机器学习异常检测
- 为AlertService提供数据支持
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from loguru import logger
from datetime import datetime
from decimal import Decimal
import pandas as pd
import numpy as np
from collections import deque


@dataclass
class MonitoringConfig:
    """监控配置"""
    strategy_id: str                       # 策略ID
    metrics: List[str] = field(default_factory=lambda: ["return", "drawdown", "sharpe"])
    update_frequency: int = 60             # 更新频率（秒）
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    # 默认阈值
    default_thresholds = {
        "max_return_drop": -0.10,          # 最大单日跌幅 -10%
        "max_drawdown_limit": 0.20,        # 最大回撤限制 20%
        "min_sharpe_ratio": 0.5            # 最小夏普比率
    }

    # 高级配置
    enable_anomaly_detection: bool = True  # 启用异常检测
    anomaly_method: str = "3sigma"         # 异常检测方法（3sigma/iqr/isolation_forest）
    history_window: int = 100              # 历史数据窗口


@dataclass
class MetricValue:
    """指标值"""
    name: str                              # 指标名称
    value: float                           # 指标值
    timestamp: datetime                    # 时间戳
    is_anomaly: bool = False               # 是否异常


@dataclass
class AnomalyRecord:
    """异常记录"""
    anomaly_id: str                        # 异常ID
    metric_name: str                       # 指标名称
    value: float                           # 异常值
    threshold: float                       # 阈值
    severity: str                          # 严重程度（info/warning/critical）
    timestamp: datetime                    # 检测时间
    description: str                       # 描述


class MonitoringService:
    """实时监控服务

    提供策略性能监控、异常检测和报告生成功能
    """

    def __init__(self, config: MonitoringConfig):
        """初始化监控服务

        Args:
            config: 监控配置
        """
        self.config = config
        self.is_monitoring = False
        self.start_time: Optional[datetime] = None
        self.metrics_history: Dict[str, deque] = {}
        self.anomalies: List[AnomalyRecord] = []

        # 初始化指标历史
        for metric in config.metrics:
            self.metrics_history[metric] = deque(maxlen=config.history_window)

        # 合并默认阈值和自定义阈值
        self.thresholds = {**config.default_thresholds, **config.alert_thresholds}

        # 初始化策略状态（用于计算真实指标）
        self._initial_capital: float = 1000000.0  # 初始资金
        self._current_capital: float = 1000000.0  # 当前资金
        self._peak_capital: float = 1000000.0     # 峰值资金
        self._total_trades: int = 0                # 总交易次数
        self._winning_trades: int = 0              # 盈利交易次数
        self._total_profit: float = 0.0            # 总盈利
        self._total_loss: float = 0.0              # 总亏损

        logger.info(
            f"MonitoringService initialized for strategy '{config.strategy_id}' "
            f"with {len(config.metrics)} metrics"
        )

    def update_strategy_state(
        self,
        current_capital: Optional[float] = None,
        trade_result: Optional[Dict[str, Any]] = None
    ) -> None:
        """更新策略状态（用于计算真实指标）

        Args:
            current_capital: 当前资金（可选）
            trade_result: 交易结果（可选），格式：
                {
                    "profit": float,  # 盈亏金额（正数=盈利，负数=亏损）
                    "is_win": bool    # 是否盈利
                }
        """
        # 更新资金
        if current_capital is not None:
            self._current_capital = current_capital
            if self._current_capital > self._peak_capital:
                self._peak_capital = self._current_capital

        # 更新交易统计
        if trade_result is not None:
            self._total_trades += 1
            profit = trade_result.get("profit", 0.0)

            if profit > 0:
                self._winning_trades += 1
                self._total_profit += profit
            else:
                self._total_loss += profit

        logger.debug(
            f"Strategy state updated: "
            f"capital={self._current_capital:.2f}, "
            f"trades={self._total_trades}, "
            f"wins={self._winning_trades}"
        )

    def start_monitoring(self) -> Dict[str, Any]:
        """启动监控

        Returns:
            启动结果
        """
        self.is_monitoring = True
        self.start_time = datetime.now()

        logger.info(f"Monitoring started for strategy '{self.config.strategy_id}'")

        return {
            "status": "started",
            "strategy_id": self.config.strategy_id,
            "start_time": self.start_time.isoformat(),
            "metrics": self.config.metrics,
            "update_frequency": self.config.update_frequency,
            "message": "Monitoring session started successfully"
        }

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """获取实时指标

        基于策略内部状态计算真实的性能指标，包括：
        - return: 收益率（基于当前资金vs初始资金）
        - drawdown: 回撤（基于峰值资金vs当前资金）
        - sharpe_ratio: 夏普比率（基于历史收益率计算）
        - volatility: 波动率（基于历史收益率计算）
        - win_rate: 胜率（盈利交易/总交易）
        - profit_loss_ratio: 盈亏比（平均盈利/平均亏损）

        Returns:
            实时指标数据
        """
        if not self.is_monitoring:
            return {
                "status": "error",
                "message": "Monitoring not started"
            }

        # 计算真实的性能指标
        total_return = (self._current_capital / self._initial_capital) - 1.0

        # 计算回撤
        if self._current_capital > self._peak_capital:
            self._peak_capital = self._current_capital
        drawdown = 0.0 if self._peak_capital <= 0 else (self._peak_capital - self._current_capital) / self._peak_capital

        # 计算胜率
        win_rate = 0.0 if self._total_trades == 0 else self._winning_trades / self._total_trades

        # 计算盈亏比
        avg_profit = 0.0 if self._winning_trades == 0 else self._total_profit / self._winning_trades
        avg_loss = 0.0 if (self._total_trades - self._winning_trades) == 0 else abs(self._total_loss / (self._total_trades - self._winning_trades))
        profit_loss_ratio = 0.0 if avg_loss == 0 else avg_profit / avg_loss

        # 基于历史数据计算夏普比率和波动率
        sharpe_ratio = 0.5
        volatility = 0.15

        if "return" in self.metrics_history and len(self.metrics_history["return"]) >= 10:
            returns_history = list(self.metrics_history["return"])
            volatility = float(np.std(returns_history))
            # 简化夏普比率计算：(年化收益率 - 无风险利率) / 年化波动率
            # 假设无风险利率为3%，年化因子为252个交易日
            annual_return = total_return * 252 / max(1, (datetime.now() - self.start_time).days / 7)
            sharpe_ratio = (annual_return - 0.03) / (volatility * np.sqrt(252)) if volatility > 0 else 0.0

        current_metrics = {
            "return": total_return,
            "drawdown": drawdown,
            "sharpe_ratio": sharpe_ratio,
            "volatility": volatility,
            "win_rate": win_rate,
            "profit_loss_ratio": profit_loss_ratio
        }

        # 更新历史数据
        for metric_name, metric_value in current_metrics.items():
            if metric_name in self.metrics_history:
                self.metrics_history[metric_name].append(metric_value)

        logger.debug(
            f"Real-time metrics for '{self.config.strategy_id}': "
            f"Return={current_metrics['return']:.2%}, "
            f"Drawdown={current_metrics['drawdown']:.2%}"
        )

        return {
            "status": "success",
            "strategy_id": self.config.strategy_id,
            "metrics": current_metrics,
            "timestamp": datetime.now().isoformat(),
            "monitoring_duration_seconds": (
                datetime.now() - self.start_time
            ).total_seconds() if self.start_time else 0
        }

    def detect_anomaly(self, current_data: Dict[str, float]) -> Dict[str, Any]:
        """检测异常

        Args:
            current_data: 当前指标数据

        Returns:
            异常检测结果
        """
        if not self.is_monitoring:
            return {
                "status": "error",
                "message": "Monitoring not started"
            }

        anomalies_detected = []

        # 方法1: 阈值检测
        for metric_name, metric_value in current_data.items():
            # 检查回撤阈值
            if metric_name == "drawdown":
                max_dd_limit = self.thresholds.get("max_drawdown_limit", 0.20)
                if metric_value > max_dd_limit:
                    anomalies_detected.append({
                        "metric": metric_name,
                        "value": metric_value,
                        "threshold": max_dd_limit,
                        "type": "threshold_exceeded",
                        "severity": "critical" if metric_value > max_dd_limit * 1.5 else "warning"
                    })

            # 检查收益率阈值
            if metric_name == "return":
                min_return = self.thresholds.get("max_return_drop", -0.10)
                if metric_value < min_return:
                    anomalies_detected.append({
                        "metric": metric_name,
                        "value": metric_value,
                        "threshold": min_return,
                        "type": "threshold_exceeded",
                        "severity": "warning"
                    })

        # 方法2: 统计异常检测（3-sigma）
        if self.config.enable_anomaly_detection and self.config.anomaly_method == "3sigma":
            for metric_name in current_data.keys():
                if metric_name in self.metrics_history and len(self.metrics_history[metric_name]) > 10:
                    history_values = list(self.metrics_history[metric_name])
                    mean = np.mean(history_values)
                    std = np.std(history_values)

                    if std > 0:
                        current_value = current_data[metric_name]
                        z_score = abs((current_value - mean) / std)

                        if z_score > 3:  # 3-sigma规则
                            anomalies_detected.append({
                                "metric": metric_name,
                                "value": current_value,
                                "mean": mean,
                                "std": std,
                                "z_score": z_score,
                                "type": "statistical_anomaly",
                                "severity": "warning" if z_score < 4 else "critical"
                            })

        # 记录异常
        anomaly_detected = len(anomalies_detected) > 0

        if anomaly_detected:
            for anomaly in anomalies_detected:
                record = AnomalyRecord(
                    anomaly_id=f"{self.config.strategy_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    metric_name=anomaly["metric"],
                    value=anomaly["value"],
                    threshold=anomaly.get("threshold", 0.0),
                    severity=anomaly["severity"],
                    timestamp=datetime.now(),
                    description=f"{anomaly['type']}: {anomaly['metric']}={anomaly['value']:.4f}"
                )
                self.anomalies.append(record)

            logger.warning(
                f"Anomalies detected for '{self.config.strategy_id}': "
                f"{len(anomalies_detected)} anomalies"
            )

        return {
            "anomaly_detected": anomaly_detected,
            "anomalies": anomalies_detected,
            "timestamp": datetime.now().isoformat(),
            "total_anomalies": len(self.anomalies)
        }

    def generate_monitoring_report(self) -> Dict[str, Any]:
        """生成监控报告

        Returns:
            监控报告
        """
        if not self.is_monitoring:
            return {
                "status": "error",
                "message": "Monitoring not started"
            }

        # 获取当前指标
        metrics_result = self.get_real_time_metrics()
        current_metrics = metrics_result.get("metrics", {})

        # 计算指标统计
        metrics_summary = {}
        for metric_name, history in self.metrics_history.items():
            if len(history) > 0:
                history_values = list(history)
                metrics_summary[metric_name] = {
                    "current": current_metrics.get(metric_name, 0.0),
                    "mean": np.mean(history_values),
                    "std": np.std(history_values),
                    "min": np.min(history_values),
                    "max": np.max(history_values),
                    "count": len(history_values)
                }

        # 最近异常
        recent_anomalies = [
            {
                "anomaly_id": a.anomaly_id,
                "metric": a.metric_name,
                "value": a.value,
                "severity": a.severity,
                "timestamp": a.timestamp.isoformat(),
                "description": a.description
            }
            for a in self.anomalies[-10:]  # 最近10条
        ]

        duration = (
            datetime.now() - self.start_time
        ).total_seconds() if self.start_time else 0

        return {
            "strategy_id": self.config.strategy_id,
            "monitoring_duration_seconds": duration,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "generated_at": datetime.now().isoformat(),
            "metrics_summary": metrics_summary,
            "anomalies": {
                "total_count": len(self.anomalies),
                "recent": recent_anomalies
            },
            "status": "active" if self.is_monitoring else "stopped"
        }

    def stop_monitoring(self) -> Dict[str, Any]:
        """停止监控

        Returns:
            停止结果
        """
        self.is_monitoring = False
        duration = (
            datetime.now() - self.start_time
        ).total_seconds() if self.start_time else 0

        logger.info(
            f"Monitoring stopped for strategy '{self.config.strategy_id}', "
            f"duration: {duration:.2f}s"
        )

        return {
            "status": "stopped",
            "strategy_id": self.config.strategy_id,
            "duration_seconds": duration,
            "total_anomalies_detected": len(self.anomalies),
            "timestamp": datetime.now().isoformat(),
            "message": "Monitoring session stopped"
        }

    def get_monitoring_info(self) -> Dict[str, Any]:
        """获取监控信息

        Returns:
            监控服务信息
        """
        return {
            "strategy_id": self.config.strategy_id,
            "is_monitoring": self.is_monitoring,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "metrics": self.config.metrics,
            "update_frequency": self.config.update_frequency,
            "thresholds": self.thresholds,
            "anomaly_detection": {
                "enabled": self.config.enable_anomaly_detection,
                "method": self.config.anomaly_method
            },
            "statistics": {
                "total_anomalies": len(self.anomalies),
                "metrics_count": len(self.metrics_history),
                "history_window": self.config.history_window
            }
        }
