---
name: uvicorn-windows-reload
description: |
  uvicorn --reload 在 Windows 上不可靠。Use when: (1) 修改了代码但 API 行为没变，
  (2) WatchFiles 显示 "Reloading..." 但没有 "Application startup complete"，
  (3) 热重载触发后请求仍返回旧结果。解决方案：手动重启。
author: Claude Code
version: 1.0.0
date: 2026-03-22
---

# uvicorn --reload 在 Windows 上不可靠

## 问题
修改代码后 uvicorn 显示检测到变更并触发重载，但新进程启动失败，
旧进程继续服务，导致代码改了但行为没变。

## 症状
```
WARNING:  WatchFiles detected changes in 'src\myquant\...py'. Reloading...
# 之后没有: INFO: Application startup complete.
# 但请求仍然返回旧的错误
```

## 解决方案

**每次改代码后手动重启：**

```bash
# 停止进程（Windows）
powershell "Get-Process -Name python* | Stop-Process -Force"

# 重新启动
cd E:/MyQuant_v11/backend
E:/MyQuant_v11/.venv/Scripts/uvicorn.exe myquant.main:app --reload --port 8000
```

## 验证是否重载成功
重载成功的日志应该包含：
```
INFO: Started server process [xxxxx]
INFO: Waiting for application startup.
INFO: Application startup complete.
```

## 注意
- 不要依赖 --reload 的热重载，改完代码就手动重启
- 用 background task 启动后，检查日志确认 startup complete
