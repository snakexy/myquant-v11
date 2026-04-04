---
name: fastapi-frontend-alias-routes
description: |
  FastAPI 为前端兼容性添加别名路由。Use when: (1) 前端期望 /api/v5/... 但后端挂载在
  /api/quotes/...，(2) 路由重构后前端路径不匹配，(3) 需要同时支持新旧两套路径。
  方案：在 main.py 里重复 include_router，使用不同 prefix。
author: Claude Code
version: 1.0.0
date: 2026-03-22
---

# FastAPI 前端兼容别名路由

## 问题
前端代码期望 `/api/v5/kline/realtime/{symbol}`，但后端 router 挂载在 `/api/quotes`，
修改前端成本高，需要让后端同时支持两个路径。

## 解决方案

在 `main.py` 里对同一个 router 使用不同的 prefix 挂载两次：

```python
# main.py

# 主路由
app.include_router(quotes_router, prefix="/api/quotes", tags=["行情"])
app.include_router(market_router, prefix="/api/market",  tags=["市场"])

# 前端兼容别名（前端期望的路径）
app.include_router(quotes_router, prefix="/api/v5",         tags=["行情(v5别名)"])
app.include_router(market_router, prefix="/api/v1/quotes",  tags=["市场(v1别名)"])
```

## 注意事项
- Router 自带 prefix（如 `APIRouter(prefix="/kline")`），挂载时不要重复加
  - 错误：`prefix="/api/quotes/kline"` + router 内 `prefix="/kline"` → `/api/quotes/kline/kline/...`
  - 正确：`prefix="/api/quotes"` + router 内 `prefix="/kline"` → `/api/quotes/kline/...`
- 同一 router 多次挂载不影响性能，共享同一份 handler 代码

## 验证
```bash
curl http://localhost:8000/api/quotes/kline/realtime/000001  # 主路由
curl http://localhost:8000/api/v5/kline/realtime/000001      # 别名路由
# 两者返回相同结果
```
