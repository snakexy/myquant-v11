# 历史回测模块 - API设计

> **阶段**: Validation阶段
> **状态**: 🔄 开发中
> **版本**: v3.0
> **最后更新**: 2026-02-11

---

## 📡 API端点列表 (规划中)

### 1. 创建回测任务
`POST /api/v1/validation/backtest/create`

### 2. 执行回测
`POST /api/v1/validation/backtest/run`

### 3. 查询回测结果
`GET /api/v1/validation/backtest/results/{task_id}`

### 4. 回测性能分析
`GET /api/v1/validation/backtest/performance/{task_id}`

---

**状态**: 🔄 代码实现中（70%）
**代码位置**: `backend/api/v1/validation/routers.py`
