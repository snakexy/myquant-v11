# 机器学习训练模块 - API设计

> **版本**: v1.0
> **创建时间**: 2026-02-12
> **状态**: 🟡 设计阶段
> **最后更新**: 2026-02-13

---

## 🔗 QLib集成说明

本模块深度集成QLib高级模块：

| QLib模块 | API集成点 | 作用 |
|---------|---------|------|
| **Workflow管理模块** | `/api/v1/research/ml/train` | 使用QLib Workflow编排训练流程 |
| **Task任务管理模块** | `/api/v1/research/ml/optimize` | 使用TaskGen生成滚动训练任务 |

### QLib Workflow集成示例

```python
# 训练API内部使用QLib Workflow
from qlib.workflow import R
from qlib.workflow.task.gen import *


def train_with_qlib(task_config):
    # 1. 创建任务
    task = {
        "model": {"class": task_config.model_type},
        "dataset": {
            "class": "DatasetH",
            "kwargs": {
                "handler": "Alpha158",
                "segments": {
                    "train": (task_config.start_date, task_config.end_date),
                    "valid": (task_config.val_start, task_config.val_end)
                }
            }
        }
    }

    # 2. 使用Recorder追踪
    with R.start(experiment_name="ml_training"):
        R.log_params(**task_config.model_params)
        model = task["model"]["class"](**task_config.model_params)
        model.fit(task["dataset"])
        R.save_objects(model=model)

    # 3. 返回Recorder ID供后续查询
    return R.get_recorder().id
```

---

## 📋 API概览

### 基础信息
- **基础路径**: `/api/v1/research/ml`
- **认证方式**: 暂无（后续可添加JWT）
- **请求格式**: `application/json`
- **响应格式**: `application/json`

### 标准响应格式

**成功响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": { ... },
  "timestamp": "2026-02-12T10:30:00"
}
```

**错误响应**:
```json
{
  "code": 400/404/500,
  "message": "错误描述",
  "detail": "详细错误信息",
  "timestamp": "2026-02-12T10:30:00"
}
```

---

## 🎯 API端点详细设计

### 1. 训练ML模型

#### 端点信息
- **路径**: `/api/v1/research/ml/train`
- **方法**: `POST`
- **功能**: 训练机器学习模型

#### 请求参数

```python
class MLTrainingRequest(BaseModel):
    """机器学习训练请求"""

    # 基础配置
    model_type: str = "LGB"  # LGB, XGB, RF, Linear, LSTM, GRU, MLP
    task_type: str = "classification"  # classification, regression

    # 数据配置
    instruments: List[str]  # 股票池，如 ['000001.SZ', '600000.SH']
    start_date: str  # 训练开始日期，如 '2020-01-01'
    end_date: str  # 训练结束日期，如 '2024-12-31'

    # 特征配置
    features: List[str]  # 特征列表，如 ['MA5', 'MA20', 'RSI', 'MACD']
    feature_engineering: bool = True  # 是否自动特征工程

    # 标签配置
    label: str = "return"  # 标签类型：return, direction, volatility
    label_horizon: int = 5  # 预测 horizon（天）

    # 模型参数
    model_params: Dict[str, Any] = {}  # 模型特定参数

    # 训练参数
    train_split: float = 0.8  # 训练集比例
    val_split: float = 0.1  # 验证集比例
    test_split: float = 0.1  # 测试集比例

    # 评估配置
    metrics: List[str] = ["accuracy"]  # 评估指标
    early_stopping_rounds: Optional[int] = None  # 早停轮数
```

#### 请求示例

```json
{
  "model_type": "LGB",
  "task_type": "classification",
  "instruments": ["000001.SZ", "600000.SH"],
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "features": ["MA5", "MA20", "RSI", "MACD", "BOLL_UPPER"],
  "feature_engineering": true,
  "label": "direction",
  "label_horizon": 5,
  "model_params": {
    "num_leaves": 31,
    "learning_rate": 0.05,
    "n_estimators": 100
  },
  "train_split": 0.7,
  "val_split": 0.15,
  "test_split": 0.15,
  "metrics": ["accuracy", "precision", "recall", "f1"],
  "early_stopping_rounds": 10
}
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "model_id": "lgb_classification_20260212_103000",
    "model_type": "LGB",
    "task_type": "classification",
    "training_status": "completed",
    "training_duration": 45.67,
    "feature_count": 5,
    "sample_count": 1500,
    "metrics": {
      "train": {
        "accuracy": 0.85,
        "precision": 0.83,
        "recall": 0.87,
        "f1": 0.85
      },
      "val": {
        "accuracy": 0.78,
        "precision": 0.76,
        "recall": 0.81,
        "f1": 0.78
      },
      "test": {
        "accuracy": 0.75,
        "precision": 0.73,
        "recall": 0.79,
        "f1": 0.76
      }
    },
    "feature_importance": {
      "MA5": 0.35,
      "MA20": 0.28,
      "RSI": 0.18,
      "MACD": 0.12,
      "BOLL_UPPER": 0.07
    },
    "model_path": "/models/lgb_classification_20260212_103000.pkl"
  },
  "timestamp": "2026-02-12T10:30:00"
}
```

---

### 2. 模型预测

#### 端点信息
- **路径**: `/api/v1/research/ml/predict`
- **方法**: `POST`
- **功能**: 使用训练好的模型进行预测

#### 请求参数

```python
class MLPredictionRequest(BaseModel):
    """预测请求"""

    model_id: str  # 模型ID
    instruments: List[str]  # 要预测的股票列表
    start_date: str  # 预测开始日期
    end_date: str  # 预测结束日期（可选）

    # 特征数据（可选，如果不提供则从数据库加载）
    features: Optional[pd.DataFrame] = None
```

#### 请求示例

```json
{
  "model_id": "lgb_classification_20260212_103000",
  "instruments": ["000001.SZ"],
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "model_id": "lgb_classification_20260212_103000",
    "predictions": [
      {
        "instrument": "000001.SZ",
        "date": "2025-01-02",
        "prediction": 1,  // 1: 涨, 0: 跌
        "probability": {
          "0": 0.35,  // 跌概率
          "1": 0.65   // 涨概率
        },
        "confidence": 0.75
      },
      {
        "instrument": "000001.SZ",
        "date": "2025-01-03",
        "prediction": 1,
        "probability": {
          "0": 0.28,
          "1": 0.72
        },
        "confidence": 0.82
      }
    ]
  },
  "timestamp": "2026-02-12T10:35:00"
}
```

---

### 3. 获取模型列表

#### 端点信息
- **路径**: `/api/v1/research/ml/models`
- **方法**: `GET`
- **功能**: 列出所有训练好的模型

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|--------|------|
| limit | int | 否 | 返回数量限制，默认20 |
| offset | int | 否 | 偏移量，默认0 |
| model_type | str | 否 | 筛选模型类型 |
| task_type | str | 否 | 筛选任务类型 |

#### 请求示例

```
GET /api/v1/research/ml/models?limit=20&model_type=LGB
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 5,
    "models": [
      {
        "model_id": "lgb_classification_20260212_103000",
        "model_type": "LGB",
        "task_type": "classification",
        "created_at": "2026-02-12T10:30:00",
        "metrics": {
          "test_accuracy": 0.75,
          "test_f1": 0.76
        },
        "feature_count": 5,
        "status": "completed"
      },
      {
        "model_id": "xgb_regression_20260211_150000",
        "model_type": "XGB",
        "task_type": "regression",
        "created_at": "2026-02-11T15:00:00",
        "metrics": {
          "test_mse": 0.0023,
          "test_r2": 0.68
        },
        "feature_count": 8,
        "status": "completed"
      }
    ]
  },
  "timestamp": "2026-02-12T10:40:00"
}
```

---

### 4. 获取模型详情

#### 端点信息
- **路径**: `/api/v1/research/ml/models/{model_id}`
- **方法**: `GET`
- **功能**: 获取模型详细信息

#### 请求示例

```
GET /api/v1/research/ml/models/lgb_classification_20260212_103000
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "model_id": "lgb_classification_20260212_103000",
    "model_type": "LGB",
    "task_type": "classification",
    "created_at": "2026-02-12T10:30:00",
    "status": "completed",

    "config": {
      "instruments": ["000001.SZ", "600000.SH"],
      "start_date": "2020-01-01",
      "end_date": "2024-12-31",
      "features": ["MA5", "MA20", "RSI", "MACD"],
      "label": "direction",
      "label_horizon": 5,
      "train_split": 0.7,
      "val_split": 0.15,
      "test_split": 0.15
    },

    "model_params": {
      "num_leaves": 31,
      "learning_rate": 0.05,
      "n_estimators": 100,
      "verbose": -1
    },

    "feature_importance": {
      "MA5": 0.35,
      "MA20": 0.28,
      "RSI": 0.18,
      "MACD": 0.12,
      "BOLL_UPPER": 0.07
    },

    "metrics": {
      "train": {
        "accuracy": 0.85,
        "precision": 0.83,
        "recall": 0.87,
        "f1": 0.85
      },
      "val": {
        "accuracy": 0.78,
        "precision": 0.76,
        "recall": 0.81,
        "f1": 0.78
      },
      "test": {
        "accuracy": 0.75,
        "precision": 0.73,
        "recall": 0.79,
        "f1": 0.76
      }
    },

    "training_history": [
      {
        "iteration": 10,
        "train_loss": 0.45,
        "val_loss": 0.52
      },
      {
        "iteration": 20,
        "train_loss": 0.38,
        "val_loss": 0.48
      }
    ],

    "model_path": "/models/lgb_classification_20260212_103000.pkl",
    "training_duration": 45.67
  },
  "timestamp": "2026-02-12T10:42:00"
}
```

---

### 5. 评估模型

#### 端点信息
- **路径**: `/api/v1/research/ml/models/{model_id}/evaluate`
- **方法**: `POST`
- **功能**: 使用测试集评估模型性能

#### 请求参数

```python
class MLEvaluationRequest(BaseModel):
    """模型评估请求"""

    test_data: Optional[pd.DataFrame] = None  # 测试数据（可选）
    metrics: List[str] = ["accuracy"]  # 评估指标
    detailed: bool = False  # 是否返回详细结果
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "model_id": "lgb_classification_20260212_103000",
    "evaluation_results": {
      "accuracy": 0.75,
      "precision": 0.73,
      "recall": 0.79,
      "f1": 0.76,
      "confusion_matrix": [[180, 45], [32, 165]],
      "roc_auc": 0.82
    },
    "classification_report": {
      "0": {
        "precision": 0.73,
        "recall": 0.80,
        "f1-score": 0.76,
        "support": 225
      },
      "1": {
        "precision": 0.77,
        "recall": 0.70,
        "f1-score": 0.73,
        "support": 197
      }
    }
  },
  "timestamp": "2026-02-12T10:45:00"
}
```

---

### 6. 超参数优化

#### 端点信息
- **路径**: `/api/v1/research/ml/optimize`
- **方法**: `POST`
- **功能**: 自动搜索最优超参数

#### 请求参数

```python
class MLOptimizationRequest(BaseModel):
    """超参数优化请求"""

    model_id: str  # 基础模型ID
    param_space: Dict[str, List[Any]]  # 参数空间
    n_trials: int = 10  # 试验次数
    optimization_method: str = "random"  # random, grid, bayesian, optuna
    timeout: Optional[int] = None  # 超时时间（秒）
```

#### 请求示例

```json
{
  "model_id": "lgb_classification_20260212_103000",
  "param_space": {
    "num_leaves": [15, 31, 63, 127],
    "learning_rate": [0.01, 0.05, 0.1],
    "n_estimators": [50, 100, 200],
    "min_child_samples": [10, 20, 30]
  },
  "n_trials": 20,
  "optimization_method": "optuna",
  "timeout": 300
}
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "optimization_id": "opt_lgb_20260212_104500",
    "base_model_id": "lgb_classification_20260212_103000",
    "optimization_method": "optuna",
    "best_params": {
      "num_leaves": 31,
      "learning_rate": 0.05,
      "n_estimators": 200,
      "min_child_samples": 20
    },
    "best_score": {
      "accuracy": 0.82,
      "f1": 0.81
    },
    "all_trials": [
      {
        "trial_number": 1,
        "params": {
          "num_leaves": 15,
          "learning_rate": 0.01,
          "n_estimators": 50
        },
        "score": {
          "accuracy": 0.76,
          "f1": 0.75
        }
      },
      {
        "trial_number": 2,
        "params": {
          "num_leaves": 31,
          "learning_rate": 0.05,
          "n_estimators": 200
        },
        "score": {
          "accuracy": 0.82,
          "f1": 0.81
        }
      }
    ]
  },
  "timestamp": "2026-02-12T11:00:00"
}
```

---

### 7. 获取特征重要性

#### 端点信息
- **路径**: `/api/v1/research/ml/features`
- **方法**: `GET`
- **功能**: 获取模型特征重要性

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|--------|------|
| model_id | str | 是 | 模型ID |
| top_n | int | 否 | 返回前N个特征，默认全部 |

#### 请求示例

```
GET /api/v1/research/ml/features?model_id=lgb_classification_20260212_103000&top_n=10
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "model_id": "lgb_classification_20260212_103000",
    "feature_importance": [
      {
        "feature": "MA5",
        "importance": 0.35,
        "rank": 1
      },
      {
        "feature": "MA20",
        "importance": 0.28,
        "rank": 2
      },
      {
        "feature": "RSI",
        "importance": 0.18,
        "rank": 3
      },
      {
        "feature": "MACD",
        "importance": 0.12,
        "rank": 4
      },
      {
        "feature": "BOLL_UPPER",
        "importance": 0.07,
        "rank": 5
      }
    ],
    "total_features": 5
  },
  "timestamp": "2026-02-12T11:05:00"
}
```

---

### 8. 特征选择

#### 端点信息
- **路径**: `/api/v1/research/ml/features/select`
- **方法**: `POST`
- **功能**: 基于重要性或相关性选择特征

#### 请求体

| 参数 | 类型 | 必填 | 说明 |
|------|------|--------|------|
| X | List[List[float]] | 是 | 特征矩阵 |
| y | List[float] | 是 | 标签向量 |
| feature_names | List[str] | 否 | 特征名称列表 |
| method | str | 否 | 选择方法: importance/correlation，默认importance |
| top_k | int | 否 | 选择前k个特征（importance方法），默认20 |
| threshold | float | 否 | 相关系数阈值（correlation方法），默认0.3 |
| correlation_method | str | 否 | pearson/spearman，默认pearson |

#### 请求示例

```json
POST /api/v1/research/ml/features/select
{
  "X": [[0.1, 0.2, 0.3], ...],
  "y": [0, 1, 1, 0],
  "feature_names": ["MA5", "MA20", "RSI"],
  "method": "importance",
  "top_k": 5
}
```

#### 响应示例

```json
{
  "selected_features": ["MA5", "RSI", "MA20"],
  "selected_indices": [0, 2, 1],
  "method": "importance",
  "message": "成功选择3个特征"
}
```

---

### 9. 特征变换

#### 端点信息
- **路径**: `/api/v1/research/ml/features/transform`
- **方法**: `POST`
- **功能**: 标准化/归一化/对数变换

#### 请求体

| 参数 | 类型 | 必填 | 说明 |
|------|------|--------|------|
| X | List[List[float]] | 是 | 特征矩阵 |
| method | str | 否 | 变换方法: standard/minmax/robust/log，默认standard |
| return_stats | bool | 否 | 是否返回变换参数，默认true |

#### 请求示例

```json
POST /api/v1/research/ml/features/transform
{
  "X": [[0.1, 0.2], [0.3, 0.4]],
  "method": "standard"
}
```

#### 响应示例

```json
{
  "X_transformed": [[-1.2, 0.5], [1.2, -0.5]],
  "method": "standard",
  "stats": {"mean": [0.2, 0.3], "std": [0.1, 0.08]},
  "original_shape": [2, 2],
  "transformed_shape": [2, 2]
}
```

---

### 10. 去除高度相关特征

#### 端点信息
- **路径**: `/api/v1/research/ml/features/remove-correlated`
- **方法**: `POST`
- **功能**: 移除特征间相关性过高的特征

#### 请求体

| 参数 | 类型 | 必填 | 说明 |
|------|------|--------|------|
| X | List[List[float]] | 是 | 特征矩阵 |
| feature_names | List[str] | 否 | 特征名称列表 |
| threshold | float | 否 | 相关性阈值，默认0.9 |

#### 响应示例

```json
{
  "selected_features": ["MA5", "RSI"],
  "selected_indices": [0, 2],
  "method": "remove_correlated",
  "message": "移除了1个高度相关特征，保留2个特征"
}
```

---

### 11. 创建多项式特征

#### 端点信息
- **路径**: `/api/v1/research/ml/features/polynomial`
- **方法**: `POST`
- **功能**: 创建交互特征捕捉非线性关系

#### 请求体

| 参数 | 类型 | 必填 | 说明 |
|------|------|--------|------|
| X | List[List[float]] | 是 | 特征矩阵 |
| degree | int | 否 | 多项式度数，默认2 |
| interaction_only | bool | 否 | 是否只创建交互特征，默认false |

#### 响应示例

```json
{
  "X_polynomial": [[1, 0.1, 0.2, 0.01, 0.02, 0.04]],
  "original_shape": [1, 2],
  "polynomial_shape": [1, 6],
  "method": "polynomial",
  "message": "从2个特征扩展到6个特征"
}
```

---

## 🔐 错误代码

| 错误码 | 说明 | 示例 |
|--------|------|--------|
| 400 | 请求参数错误 | 特征列表为空 |
| 404 | 模型不存在 | 模型ID未找到 |
| 500 | 服务器内部错误 | 训练失败 |

---

## 📊 数据模型

### 模型信息（ModelInfo）
```python
class ModelInfo:
    model_id: str
    model_type: str
    task_type: str
    created_at: str
    metrics: Dict[str, float]
    feature_count: int
    status: str
```

### 预测结果（PredictionResult）
```python
class PredictionResult:
    instrument: str
    date: str
    prediction: Union[int, float]  # 分类为int，回归为float
    probability: Optional[Dict]  # 分类概率
    confidence: float
```

---

**创建时间**: 2026-02-12
**最后更新**: 2026-02-12
**状态**: 🟡 设计阶段
