# 模拟实盘模块 - API设计

> **阶段**: Validation阶段
> **状态**: ✅ 部分实现
> **最后更新**: 2026-02-11

---

## 📡 API端点列表

### 1. 创建模拟账户
`POST /api/v1/validation/simulation/account/create`

### 2. 查询模拟账户
`GET /api/v1/validation/simulation/account/{account_id}`

### 3. 下模拟订单
`POST /api/v1/validation/simulation/order/place`

### 4. 查询持仓
`GET /api/v1/validation/simulation/positions/{account_id}`

### 5. 查询订单历史
`GET /api/v1/validation/simulation/orders/{account_id}`

---

**状态**: ✅ 部分实现（80%）
**代码位置**: `backend/api/v1/validation/routers.py`
