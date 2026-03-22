# 嵌套决策执行模块 - API设计

> **阶段**: Validation阶段
> **状态**: ✅ 已实现
> **最后更新**: 2026-02-11

---

## 📡 API端点列表

### 1. 首次训练
`POST /api/v1/validation/nested/first-train`

### 2. 查询训练进度
`GET /api/v1/validation/nested/progress/{model_id}`

### 3. 定时执行
`POST /api/v1/validation/nested/routine`

### 4. 查询信号
`GET /api/v1/validation/nested/signals/{model_id}`

### 5. 启动定时任务
`POST /api/v1/validation/nested/schedule/start`

### 6. 查询定时状态
`GET /api/v1/validation/nested/schedule/status/{model_id}`

### 7. 停止定时任务
`POST /api/v1/validation/nested/schedule/stop`

---

**状态**: ✅ 已实现（80%）
**代码位置**: `backend/api/v1/validation/routers.py`
