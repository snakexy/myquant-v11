# 实时监控模块 - API设计

> **阶段**: Validation阶段
> **状态**: ✅ 已实现
> **最后更新**: 2026-02-11

---

## 📡 API端点列表

### 1. 启动监控
`POST /api/v1/validation/monitoring/start`

### 2. 查询监控指标
`GET /api/v1/validation/monitoring/metrics/{strategy_id}`

### 3. 查询异常
`GET /api/v1/validation/monitoring/anomalies/{strategy_id}`

### 4. 获取监控报告
`GET /api/v1/validation/monitoring/report/{strategy_id}`

---

**状态**: ✅ 已实现（85%）
**代码位置**: `backend/api/v1/validation/routers.py`
