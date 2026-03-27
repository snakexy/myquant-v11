"""
系统监控和报警机制
监控投资组合管理和回测系统的运行状态，提供实时报警功能
"""

import os
import sys
import time
import logging
import psutil
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """报警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """监控指标类型"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    STRATEGY_PERFORMANCE = "strategy_performance"
    DATA_QUALITY = "data_quality"
    SYSTEM_HEALTH = "system_health"


@dataclass
class AlertConfig:
    """报警配置"""
    enabled: bool = True
    cpu_threshold: float = 80.0  # CPU使用率阈值(%)
    memory_threshold: float = 85.0  # 内存使用率阈值(%)
    disk_threshold: float = 90.0  # 磁盘使用率阈值(%)
    performance_threshold: float = -0.05  # 策略性能阈值(负5%)
    data_quality_threshold: float = 0.95  # 数据质量阈值(95%)
    
    # 邮件通知配置
    email_enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_recipients: List[str] = None
    
    # 日志配置
    log_file: str = "logs/system_monitor.log"
    max_log_size: int = 10 * 1024 * 1024  # 10MB


@dataclass
class SystemMetric:
    """系统指标"""
    timestamp: datetime
    metric_type: MetricType
    value: float
    unit: str
    status: str
    details: Dict[str, Any] = None


class SystemMonitor:
    """
    系统监控器
    
    监控系统资源使用情况、策略性能和数据质量
    """
    
    def __init__(self, config: AlertConfig = None):
        """
        初始化系统监控器
        
        Args:
            config: 报警配置
        """
        self.config = config or AlertConfig()
        self.metrics_history = []
        self.alert_callbacks = []
        self.monitoring_active = False
        self.monitor_thread = None
        
        # 设置日志
        self._setup_logging()
        
        logger.info("系统监控器初始化完成")
    
    def _setup_logging(self):
        """设置日志"""
        log_dir = os.path.dirname(self.config.log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 配置日志格式
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
    
    def add_alert_callback(self, callback: Callable[[AlertLevel, str, Dict[str, Any]], None]):
        """
        添加报警回调函数
        
        Args:
            callback: 回调函数，接收(level, message, details)参数
        """
        self.alert_callbacks.append(callback)
    
    def start_monitoring(self, interval: int = 60):
        """
        开始监控
        
        Args:
            interval: 监控间隔(秒)
        """
        if self.monitoring_active:
            logger.warning("监控已在运行中")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info(f"系统监控已启动，监控间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("系统监控已停止")
    
    def _monitoring_loop(self, interval: int):
        """监控循环"""
        while self.monitoring_active:
            try:
                # 收集系统指标
                self._collect_system_metrics()
                
                # 检查报警条件
                self._check_alerts()
                
                # 等待下一次监控
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self):
        """收集系统指标"""
        timestamp = datetime.now()
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics_history.append(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.CPU_USAGE,
            value=cpu_percent,
            unit="%",
            status="normal" if cpu_percent < self.config.cpu_threshold else "warning"
        ))
        
        # 内存使用率
        memory = psutil.virtual_memory()
        self.metrics_history.append(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.MEMORY_USAGE,
            value=memory.percent,
            unit="%",
            status="normal" if memory.percent < self.config.memory_threshold else "warning"
        ))
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self.metrics_history.append(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.DISK_USAGE,
            value=disk_percent,
            unit="%",
            status="normal" if disk_percent < self.config.disk_threshold else "warning"
        ))
        
        # 保留最近1小时的指标
        cutoff_time = timestamp - timedelta(hours=1)
        self.metrics_history = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]
    
    def _check_alerts(self):
        """检查报警条件"""
        if not self.config.enabled:
            return
        
        latest_metrics = {m.metric_type: m for m in self.metrics_history[-10:]}
        
        # CPU报警
        if MetricType.CPU_USAGE in latest_metrics:
            cpu_metric = latest_metrics[MetricType.CPU_USAGE]
            if cpu_metric.value > self.config.cpu_threshold:
                self._trigger_alert(
                    AlertLevel.WARNING,
                    f"CPU使用率过高: {cpu_metric.value:.1f}%",
                    {
                        "metric": "cpu_usage",
                        "value": cpu_metric.value,
                        "threshold": self.config.cpu_threshold,
                        "timestamp": cpu_metric.timestamp.isoformat()
                    }
                )
        
        # 内存报警
        if MetricType.MEMORY_USAGE in latest_metrics:
            memory_metric = latest_metrics[MetricType.MEMORY_USAGE]
            if memory_metric.value > self.config.memory_threshold:
                self._trigger_alert(
                    AlertLevel.WARNING,
                    f"内存使用率过高: {memory_metric.value:.1f}%",
                    {
                        "metric": "memory_usage",
                        "value": memory_metric.value,
                        "threshold": self.config.memory_threshold,
                        "timestamp": memory_metric.timestamp.isoformat()
                    }
                )
        
        # 磁盘报警
        if MetricType.DISK_USAGE in latest_metrics:
            disk_metric = latest_metrics[MetricType.DISK_USAGE]
            if disk_metric.value > self.config.disk_threshold:
                self._trigger_alert(
                    AlertLevel.WARNING,
                    f"磁盘使用率过高: {disk_metric.value:.1f}%",
                    {
                        "metric": "disk_usage",
                        "value": disk_metric.value,
                        "threshold": self.config.disk_threshold,
                        "timestamp": disk_metric.timestamp.isoformat()
                    }
                )
    
    def _trigger_alert(self, level: AlertLevel, message: str, details: Dict[str, Any]):
        """触发报警"""
        logger.warning(f"报警触发 [{level.value}]: {message}")
        
        # 调用回调函数
        for callback in self.alert_callbacks:
            try:
                callback(level, message, details)
            except Exception as e:
                logger.error(f"报警回调函数执行失败: {e}")
        
        # 发送邮件通知
        if self.config.email_enabled:
            self._send_email_alert(level, message, details)
    
    def _send_email_alert(self, level: AlertLevel, message: str, details: Dict[str, Any]):
        """发送邮件报警"""
        try:
            if not self.config.email_recipients:
                return
            
            # 创建邮件内容
            msg = MIMEMultipart()
            msg['From'] = self.config.email_user
            msg['To'] = ', '.join(self.config.email_recipients)
            msg['Subject'] = f"[{level.value.upper()}] 系统监控报警"
            
            # 邮件正文
            body = f"""
            报警级别: {level.value.upper()}
            报警时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            报警信息: {message}
            
            详细信息:
            {json.dumps(details, indent=2, ensure_ascii=False)}
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_user, self.config.email_password)
                server.send_message(msg)
            
            logger.info(f"邮件报警已发送: {message}")
            
        except Exception as e:
            logger.error(f"发送邮件报警失败: {e}")
    
    def log_strategy_performance(self, strategy_name: str, performance: float, details: Dict[str, Any] = None):
        """
        记录策略性能
        
        Args:
            strategy_name: 策略名称
            performance: 性能指标(如收益率)
            details: 详细信息
        """
        timestamp = datetime.now()
        
        self.metrics_history.append(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.STRATEGY_PERFORMANCE,
            value=performance,
            unit="%",
            status="normal" if performance > self.config.performance_threshold else "warning",
            details={
                "strategy_name": strategy_name,
                **(details or {})
            }
        ))
        
        # 检查性能报警
        if performance < self.config.performance_threshold:
            self._trigger_alert(
                AlertLevel.WARNING,
                f"策略性能异常: {strategy_name} 收益率 {performance:.2%}",
                {
                    "metric": "strategy_performance",
                    "strategy_name": strategy_name,
                    "performance": performance,
                    "threshold": self.config.performance_threshold,
                    "timestamp": timestamp.isoformat(),
                    **(details or {})
                }
            )
    
    def log_data_quality(self, quality_score: float, details: Dict[str, Any] = None):
        """
        记录数据质量
        
        Args:
            quality_score: 数据质量评分(0-1)
            details: 详细信息
        """
        timestamp = datetime.now()
        
        self.metrics_history.append(SystemMetric(
            timestamp=timestamp,
            metric_type=MetricType.DATA_QUALITY,
            value=quality_score,
            unit="score",
            status="normal" if quality_score > self.config.data_quality_threshold else "warning",
            details=details or {}
        ))
        
        # 检查数据质量报警
        if quality_score < self.config.data_quality_threshold:
            self._trigger_alert(
                AlertLevel.WARNING,
                f"数据质量异常: 质量评分 {quality_score:.3f}",
                {
                    "metric": "data_quality",
                    "quality_score": quality_score,
                    "threshold": self.config.data_quality_threshold,
                    "timestamp": timestamp.isoformat(),
                    **(details or {})
                }
            )
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """
        获取指标摘要
        
        Args:
            hours: 统计时间范围(小时)
            
        Returns:
            指标摘要
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {}
        
        # 按类型分组
        metrics_by_type = {}
        for metric in recent_metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric)
        
        # 计算摘要
        summary = {}
        for metric_type, metrics in metrics_by_type.items():
            values = [m.value for m in metrics]
            summary[metric_type.value] = {
                "current": values[-1] if values else 0,
                "average": np.mean(values) if values else 0,
                "max": np.max(values) if values else 0,
                "min": np.min(values) if values else 0,
                "count": len(values),
                "unit": metrics[0].unit if metrics else ""
            }
        
        return summary
    
    def export_metrics(self, filename: str, hours: int = 24):
        """
        导出指标数据
        
        Args:
            filename: 导出文件名
            hours: 导出时间范围(小时)
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            logger.warning("没有可导出的指标数据")
            return
        
        # 转换为DataFrame
        data = []
        for metric in recent_metrics:
            data.append({
                "timestamp": metric.timestamp,
                "metric_type": metric.metric_type.value,
                "value": metric.value,
                "unit": metric.unit,
                "status": metric.status,
                "details": json.dumps(metric.details or {}) if metric.details else ""
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"指标数据已导出到: {filename}")


# 全局系统监控器实例
_global_monitor = None


def get_system_monitor(config: AlertConfig = None) -> SystemMonitor:
    """获取全局系统监控器实例"""
    global _global_monitor
    
    if _global_monitor is None:
        _global_monitor = SystemMonitor(config)
    
    return _global_monitor


def test_system_monitor():
    """测试系统监控器"""
    print("=" * 70)
    print("测试系统监控器")
    print("=" * 70)
    
    try:
        # 创建监控配置
        config = AlertConfig(
            enabled=True,
            cpu_threshold=70.0,
            memory_threshold=80.0,
            email_enabled=False
        )
        
        # 创建监控器
        monitor = SystemMonitor(config)
        
        # 添加报警回调
        def alert_callback(level, message, details):
            print(f"🚨 报警 [{level.value}]: {message}")
        
        monitor.add_alert_callback(alert_callback)
        
        # 手动记录一些测试数据
        monitor.log_strategy_performance("TestStrategy", -0.08, {"test": True})
        monitor.log_data_quality(0.85, {"test": True})
        
        # 获取指标摘要
        summary = monitor.get_metrics_summary()
        print(f"📊 指标摘要: {summary}")
        
        print("✅ 系统监控器测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 系统监控器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_system_monitor()