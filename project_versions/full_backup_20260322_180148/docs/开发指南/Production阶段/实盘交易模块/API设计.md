# 实盘交易模块 - API设计

> **阶段**: Production阶段
> **状态**: 🔄 开发中
> **版本**: v3.0
> **最后更新**: 2026-02-11

---

## 📡 API端点列表 (规划中)

### 1. 下单
`POST /api/v1/production/trading/order`

### 2. 撤单
`DELETE /api/v1/production/trading/order/{order_id}`

### 3. 查询订单
`GET /api/v1/production/trading/orders`

### 4. 查询持仓
`GET /api/v1/production/trading/positions`

### 5. 查询账户
`GET /api/v1/production/trading/account`

---

**状态**: 🔄 代码实现中（60%）
**代码位置**: `backend/api/v1/production/trading_router.py`
