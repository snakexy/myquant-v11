# Meta Controller模块 - API设计

> **阶段**: Research阶段
> **状态**: ✅ 已实现
> **最后更新**: 2026-02-11

---

## 📡 API端点列表

### 1. 因子组合优化
`POST /api/v1/research/meta/factor/optimize`

### 2. 模型选择
`POST /api/v1/research/meta/model/select`

### 3. 超参数优化
`POST /api/v1/research/meta/hpo/auto`

### 4. 优化历史
`GET /api/v1/research/meta/trials`

### 5. 优化结果详情
`GET /api/v1/research/meta/result/{optimization_id}`

### 6. 统计信息
`GET /api/v1/research/meta/statistics`

---

**状态**: ✅ 代码实现完成（100%）

---

## 📡 API端点详细说明

### 1. 因子组合优化

#### POST /api/v1/research/meta/factor/optimize

**功能**: 根据IC/IR等指标自动优化因子权重配置

**请求**:
```json
{
  "factor_metrics": {
    "factor_1": {
      "ic_mean": 0.05,
      "ir": 0.8,
      "ic_std": 0.12
    },
    "factor_2": {
      "ic_mean": 0.03,
      "ir": 0.6,
      "ic_std": 0.10
    }
  },
  "optimization_method": "auto",
  "target_metric": "ic_mean"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "optimization_id": "factor_opt_xxx",
    "optimization_type": "factor_optimize",
    "best_config": {
      "method": "ic_weighted",
      "target": "ic_mean",
      "weights": {
        "factor_1": 0.625,
        "factor_2": 0.375
      }
    },
    "best_metrics": {
      "combined_ic": 0.042
    },
    "all_trials": [...],
    "created_at": "2026-02-11T15:30:00",
    "trial_count": 3
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

**优化方法**:
- `ic_weighted`: 基于IC绝对值的权重
- `equal_weight`: 等权重
- `ir_weighted`: 基于IR的权重
- `auto`: 自动选择最佳方法

---

### 2. 模型选择

#### POST /api/v1/research/meta/model/select

**功能**: 在多个模型类型中自动选择最佳模型

**请求**:
```json
{
  "model_types": ["lightgbm", "xgboost", "rf"],
  "metric": "mse"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "optimization_id": "model_select_xxx",
    "optimization_type": "model_select",
    "best_config": {
      "model_type": "lightgbm"
    },
    "best_metrics": {
      "mse": 0.023,
      "mae": 0.12
    },
    "all_trials": [...],
    "created_at": "2026-02-11T15:30:00",
    "trial_count": 3,
    "best_model": "lightgbm"
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

**支持的模型类型**:
- `lightgbm`: LightGBM
- `xgboost`: XGBoost
- `rf`: RandomForest
- `mlp`: 多层感知机

**评估指标**:
- `mse`: 均方误差
- `mae`: 平均绝对误差
- `ic`: 信息系数

---

### 3. 超参数优化

#### POST /api/v1/research/meta/hpo/auto

**功能**: 使用网格搜索或随机搜索优化模型超参数

**请求**:
```json
{
  "model_type": "lightgbm",
  "task_id": "task_xxx",
  "param_grid": {
    "num_leaves": [31, 50, 100],
    "learning_rate": [0.01, 0.05, 0.1],
    "n_estimators": [100, 200, 500]
  },
  "search_method": "grid",
  "n_iter": 10,
  "cv": 3
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "optimization_id": "hpo_lightgbm_xxx",
    "optimization_type": "hpo",
    "best_config": {
      "num_leaves": 50,
      "learning_rate": 0.05,
      "n_estimators": 200
    },
    "best_metrics": {
      "best_score": -0.025,
      "val_mse": 0.023,
      "best_params": {...}
    },
    "all_trials": [...],
    "created_at": "2026-02-11T15:30:00",
    "trial_count": 27
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

**搜索方法**:
- `grid`: 网格搜索（遍历所有组合）
- `random`: 随机搜索（随机采样n_iter次）

---

### 4. 优化历史

#### GET /api/v1/research/meta/trials

**查询参数**:
- `optimization_type`: 优化类型过滤（可选）
- `limit`: 返回数量限制（默认20）

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 15,
    "history": [
      {
        "optimization_id": "factor_opt_xxx",
        "optimization_type": "factor_optimize",
        "best_config": {...},
        "best_metrics": {...},
        "created_at": "2026-02-11T15:30:00",
        "trial_count": 3
      }
    ]
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

---

### 5. 优化结果详情

#### GET /api/v1/research/meta/result/{optimization_id}

**路径参数**:
- `optimization_id`: 优化ID

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "optimization_id": "factor_opt_xxx",
    "optimization_type": "factor_optimize",
    "best_config": {...},
    "best_metrics": {...},
    "all_trials": [
      {
        "trial_id": "factor_opt_xxx_ic_weighted",
        "config": {"method": "ic_weighted"},
        "metrics": {"combined_ic": 0.042},
        "timestamp": "2026-02-11T15:30:00",
        "status": "completed"
      }
    ],
    "created_at": "2026-02-11T15:30:00",
    "trial_count": 3
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

---

### 6. 统计信息

#### GET /api/v1/research/meta/statistics

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_optimizations": 15,
    "by_type": {
      "factor_optimize": 8,
      "model_select": 5,
      "hpo": 2
    }
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

---

## 🔧 数据模型

### OptimizationConfig
```python
@dataclass
class OptimizationConfig:
    optimization_method: str = "ic_weighted"
    target_metric: str = "ic_mean"
    constraints: Dict[str, Any]
    max_iterations: int = 100
    timeout_seconds: int = 300
```

### ModelConfig
```python
@dataclass
class ModelConfig:
    model_type: str  # lightgbm, xgboost, mlp, rf
    hyperparameters: Dict[str, Any]
```

### OptimizationResult
```python
@dataclass
class OptimizationResult:
    optimization_id: str
    optimization_type: str
    best_config: Dict[str, Any]
    best_metrics: Dict[str, float]
    all_trials: List[OptimizationTrial]
    created_at: datetime
```

---

## 🔗 错误处理

所有API端点遵循统一的错误响应格式：

```json
{
  "code": 500,
  "message": "错误描述",
  "data": null,
  "timestamp": "2026-02-11T15:30:00"
}
```

常见错误码：
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 📝 使用示例

### 示例1: 因子组合优化
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/research/meta/factor/optimize",
    json={
        "factor_metrics": {
            "factor_1": {"ic_mean": 0.05, "ir": 0.8},
            "factor_2": {"ic_mean": 0.03, "ir": 0.6}
        },
        "optimization_method": "auto"
    }
)

result = response.json()
print(f"最佳权重: {result['data']['weights']}")
print(f"组合IC: {result['data']['combined_ic']}")
```

### 示例2: 模型选择
```python
response = requests.post(
    "http://localhost:8000/api/v1/research/meta/model/select",
    json={
        "model_types": ["lightgbm", "xgboost", "rf"],
        "metric": "mse"
    }
)

result = response.json()
print(f"最佳模型: {result['data']['best_model']}")
```

---

**实现文件**:
- Service层: `backend/services/research/meta_controller_service.py`
- API路由: `backend/api/v1/research/meta_router.py`
