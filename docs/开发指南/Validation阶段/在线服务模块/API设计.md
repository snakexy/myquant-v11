# 在线服务模块 - API设计

> **阶段**: Validation阶段
> **状态**: ✅ 已实现
> **最后更新**: 2026-02-11

---

## 📡 API端点列表

### 1. 启动在线学习
`POST /api/v1/validation/online/start`

### 2. 更新模型
`POST /api/v1/validation/online/update/{model_id}`

### 3. 查询学习状态
`GET /api/v1/validation/online/status/{model_id}`

### 4. 回滚模型
`POST /api/v1/validation/online/rollback/{model_id}`

### 5. 评估性能
`GET /api/v1/validation/online/performance/{model_id}`

---

**状态**: ✅ 已实现（85%）
**代码位置**: `backend/api/v1/validation/routers.py`
