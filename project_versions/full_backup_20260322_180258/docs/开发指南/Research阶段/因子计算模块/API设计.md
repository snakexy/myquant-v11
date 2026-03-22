# 因子计算模块 - API设计

> **阶段**: Research阶段
> **状态**: ✅ 已实现
> **版本**: v3.0 (实际实现版本)
> **最后更新**: 2026-02-11

---

## 📡 API端点列表 (10个)

### 1. 技术指标列表
`GET /api/v1/research/calculation/indicators/list`

### 2. 计算技术指标
`POST /api/v1/research/calculation/indicators/calculate`

### 3. 计算Alpha158因子
`POST /api/v1/research/calculation/factors/alpha158`

### 4. 计算Alpha360因子
`POST /api/v1/research/calculation/factors/alpha360`

### 5. 计算自定义因子
`POST /api/v1/research/calculation/factors/custom`

### 6. 获取可用因子列表
`GET /api/v1/research/calculation/factors/list`

### 7. 服务状态统计
`GET /api/v1/research/calculation/service/stats`

### 8. 健康检查
`GET /api/v1/research/calculation/health`

---

**代码位置**: `backend/api/v1/research/calculation_router.py`
**状态**: ✅ 已实现
