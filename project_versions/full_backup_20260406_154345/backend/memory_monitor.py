# -*- coding: utf-8 -*-
"""
后端内存监控 - 定时检查和报警

使用方式:
    1. 作为独立脚本运行: python memory_monitor.py
    2. 或集成到系统监控中

功能:
    - 监控后端进程内存
    - 超过阈值时记录和报警
    - 自动检测内存泄漏
"""

import psutil
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# 监控配置
ALERT_THRESHOLD_MB = 300  # 报警阈值
CRITICAL_THRESHOLD_MB = 500  # 严重阈值
CHECK_INTERVAL = 10  # 检查间隔（秒）
LOG_FILE = Path(__file__).parent / "logs" / "memory_monitor.log"


class MemoryMonitor:
    """内存监控器"""

    def __init__(self, port: int = 8000):
        self.port = port
        self.backend_pid: Optional[int] = None
        self.history: List[Dict] = []
        self.max_history = 100

    def find_backend_pid(self) -> Optional[int]:
        """找到后端进程PID"""
        for conn in psutil.net_connections():
            if conn.laddr.port == self.port and conn.status == 'LISTEN':
                return conn.pid
        return None

    def check_memory(self) -> Optional[Dict]:
        """检查内存使用情况"""
        pid = self.find_backend_pid()
        if not pid:
            return None

        try:
            p = psutil.Process(pid)
            mem_info = p.memory_info()

            data = {
                'timestamp': datetime.now().isoformat(),
                'pid': pid,
                'rss_mb': round(mem_info.rss / 1024 / 1024, 1),
                'vms_mb': round(mem_info.vms / 1024 / 1024, 1),
                'percent': p.memory_percent(),
            }

            # 添加 USS 如果可用
            if hasattr(mem_info, 'uss'):
                data['uss_mb'] = round(mem_info.uss / 1024 / 1024, 1)

            # 添加到历史
            self.history.append(data)
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]

            return data

        except psutil.NoSuchProcess:
            return None

    def analyze_growth(self) -> Optional[str]:
        """分析内存增长趋势"""
        if len(self.history) < 3:
            return None

        # 计算最近几分钟的增长率
        recent = self.history[-10:]
        if len(recent) < 2:
            return None

        first = recent[0]['rss_mb']
        last = recent[-1]['rss_mb']
        growth = last - first

        if growth > 100:  # 增长超过100MB
            return f"内存快速增长: +{growth:.1f}MB"

        return None

    def log_status(self, data: Dict, alert: str = None):
        """记录状态"""
        # 确保日志目录存在
        LOG_FILE.parent.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%H:%M:%S')
        status = f"{timestamp} | RSS: {data['rss_mb']:6.1f}MB | VMS: {data['vms_mb']:6.1f}MB | {data['percent']:5.1f}%"

        if alert:
            status += f" | ⚠️ {alert}"

        print(status)

        # 写入日志文件
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(status + '\n')

    def run(self):
        """运行监控"""
        print("=" * 70)
        print(f"后端内存监控启动")
        print(f"报警阈值: {ALERT_THRESHOLD_MB}MB")
        print(f"严重阈值: {CRITICAL_THRESHOLD_MB}MB")
        print(f"检查间隔: {CHECK_INTERVAL}秒")
        print(f"日志文件: {LOG_FILE}")
        print("=" * 70)
        print()

        while True:
            try:
                data = self.check_memory()
                if not data:
                    print(f"{datetime.now().strftime('%H:%M:%S')} | 后端进程未找到")
                    time.sleep(CHECK_INTERVAL)
                    continue

                alert = None

                # 检查阈值
                if data['rss_mb'] > CRITICAL_THRESHOLD_MB:
                    alert = f"严重: 内存超过 {CRITICAL_THRESHOLD_MB}MB!"
                elif data['rss_mb'] > ALERT_THRESHOLD_MB:
                    alert = f"警告: 内存超过 {ALERT_THRESHOLD_MB}MB"

                # 检查增长趋势
                growth_alert = self.analyze_growth()
                if growth_alert:
                    alert = growth_alert if not alert else f"{alert}, {growth_alert}"

                self.log_status(data, alert)

                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                print("\n监控停止")
                break
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(CHECK_INTERVAL)


def check_once():
    """单次检查"""
    monitor = MemoryMonitor()
    data = monitor.check_memory()
    if data:
        print(f"后端内存: RSS={data['rss_mb']}MB, VMS={data['vms_mb']}MB")
        if data['rss_mb'] > 300:
            print("⚠️ 内存偏高")
    else:
        print("后端进程未运行")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        check_once()
    else:
        monitor = MemoryMonitor()
        monitor.run()
