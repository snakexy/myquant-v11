# 风险控制模块 - API设计

> **阶段**: Production阶段
> **状态**: ✅ 已实现
> **最后更新**: 2026-02-11

---

## 📡 API端点列表

### 1. 风险检查
`POST /api/v1/production/risk/check`

### 2. 止损止损
`POST /api/v1/production/risk/stop-loss`

### 3. 风险限制
`GET /api/v1/production/risk/limits`

### 4. 风险报告
`GET /api/v1/production/risk/report`

---

**状态**: ✅ 已实现（75%）
**代码位置**: `backend/api/v1/production/risk_router.py`
