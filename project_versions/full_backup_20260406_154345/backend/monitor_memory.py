# -*- coding: utf-8 -*-
"""内存监控脚本 - 持续追踪后端内存"""
import psutil
import time
import sys

print("=" * 60)
print("后端内存监控 - 按 Ctrl+C 停止")
print("=" * 60)

# 找到后端进程
backend_pid = None
for conn in psutil.net_connections():
    if conn.laddr.port == 8000 and conn.status == 'LISTEN':
        backend_pid = conn.pid
        break

if not backend_pid:
    print("后端进程未找到")
    sys.exit(1)

print(f"监控后端 PID: {backend_pid}")
print()

prev_mem = 0
max_mem = 0

# 持续监控
try:
    while True:
        try:
            p = psutil.Process(backend_pid)
            mem_mb = p.memory_info().rss / 1024 / 1024
            max_mem = max(max_mem, mem_mb)
            
            delta = mem_mb - prev_mem
            if abs(delta) > 5 or mem_mb > 200:  # 变化大于5MB或超过200MB时显示
                print(f"{time.strftime('%H:%M:%S')} | {mem_mb:.1f} MB | 变化: {delta:+.1f} MB | 峰值: {max_mem:.1f} MB")
            
            prev_mem = mem_mb
            time.sleep(2)
        except psutil.NoSuchProcess:
            print("后端进程已退出")
            break
except KeyboardInterrupt:
    print(f"\n监控结束 | 峰值内存: {max_mem:.1f} MB")
