# 因子评估模块 - API设计

> **阶段**: Research阶段
> **状态**: ✅ 代码实现完成（90%）
> **版本**: v4.0
> **最后更新**: 2026-02-11

---

## 📡 API端点列表

### 已实现端点 (4个)

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/research/eval/validity` | POST | 因子有效性验证 | ✅ |
| `/api/v1/research/eval/combine` | POST | 因子组合评估 | ✅ |
| `/api/v1/research/eval/smart` | POST | 智能因子评估 | ✅ |
| `/api/v1/research/eval/health` | GET | 健康检查 | ✅ |

---

## 📄 API详细说明

### 1. 因子有效性验证

**端点**: `POST /api/v1/research/eval/validity`

**功能**: 评估因子的有效性（IC、IR、IC正数占比等指标）

**请求参数**:
```json
{
  "factor_name": "custom_factor_001",
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "threshold": {
    "ic_mean": 0.03,
    "ir": 0.5,
    "ic_positive_ratio": 0.55
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_name | string | ✅ | 因子名称 |
| start_date | string | ✅ | 开始日期 (YYYY-MM-DD) |
| end_date | string | ✅ | 结束日期 (YYYY-MM-DD) |
| threshold | object | ❌ | 阈值设置 |
| threshold.ic_mean | float | ❌ | IC均值阈值，默认0.03 |
| threshold.ir | float | ❌ | IR阈值，默认0.5 |
| threshold.ic_positive_ratio | float | ❌ | IC正数占比阈值，默认0.55 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "factor_name": "custom_factor_001",
    "is_valid": true,
    "overall_score": 0.75,
    "metrics": {
      "ic_mean": {
        "value": 0.0523,
        "threshold": 0.03,
        "passed": true,
        "score": 0.87
      },
      "ir": {
        "value": 0.4238,
        "threshold": 0.5,
        "passed": false,
        "score": 0.51
      },
      "ic_positive_ratio": {
        "value": 0.5678,
        "threshold": 0.55,
        "passed": true,
        "score": 0.86
      }
    },
    "recommendation": "因子有效，建议进入Validation阶段进行回测验证",
    "evaluated_at": "2026-02-11T15:30:00"
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

---

### 2. 因子组合评估

**端点**: `POST /api/v1/research/eval/combine`

**功能**: 评估多个因子组合后的效果

**请求参数**:
```json
{
  "factor_names": ["custom_factor_001", "custom_factor_002", "momentum_factor"],
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "combination_method": "equal_weight",
  "weights": [0.5, 0.3, 0.2]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_names | array | ✅ | 因子名称列表（至少2个） |
| start_date | string | ✅ | 开始日期 (YYYY-MM-DD) |
| end_date | string | ✅ | 结束日期 (YYYY-MM-DD) |
| combination_method | string | ❌ | 组合方法：equal_weight/ic_weight/custom |
| weights | array | ❌ | 自定义权重（仅custom方法需要） |

**组合方法说明**:
- `equal_weight`: 等权重组合
- `ic_weight`: 按IC均值比例分配权重
- `custom`: 自定义权重

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "combined_factor_name": "combined_factor_20240210",
    "combination_method": "equal_weight",
    "weights": {
      "custom_factor_001": 0.3333,
      "custom_factor_002": 0.3333,
      "momentum_factor": 0.3333
    },
    "evaluation": {
      "ic_mean": 0.0589,
      "ic_std": 0.1156,
      "ir": 0.5095,
      "ic_positive_ratio": 0.5890,
      "rank_ic_mean": 0.0471,
      "max_drawdown": 0.0
    },
    "comparison": {
      "best_factor": "custom_factor_001",
      "best_factor_ic_mean": 0.0523,
      "improvement": {
        "ic_mean": 0.0066,
        "ir": 0.0857,
        "ic_positive_ratio": 0.0212
      },
      "is_better": true
    },
    "combined_at": "2026-02-11T15:30:00"
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

---

### 3. 健康检查

**端点**: `GET /api/v1/research/eval/health`

**功能**: 检查服务健康状态

**请求参数**: 无

**响应示例**:
```json
{
  "service": "因子评估模块",
  "status": "healthy",
  "timestamp": "2026-02-11T15:30:00"
}
```

---

## 🔗 使用示例

### Python示例

```python
import requests
import json

# 1. 因子有效性验证
response = requests.post(
    "http://localhost:8000/api/v1/research/eval/validity",
    json={
        "factor_name": "custom_factor_001",
        "start_date": "2020-01-01",
        "end_date": "2024-12-31",
        "threshold": {
            "ic_mean": 0.03,
            "ir": 0.5,
            "ic_positive_ratio": 0.55
        }
    }
)
result = response.json()
print(f"因子有效性: {result['data']['is_valid']}")
print(f"总体得分: {result['data']['overall_score']}")
print(f"建议: {result['data']['recommendation']}")

# 2. 因子组合评估（等权重）
response = requests.post(
    "http://localhost:8000/api/v1/research/eval/combine",
    json={
        "factor_names": ["custom_factor_001", "custom_factor_002"],
        "start_date": "2020-01-01",
        "end_date": "2024-12-31",
        "combination_method": "equal_weight"
    }
)
result = response.json()
print(f"组合因子: {result['data']['combined_factor_name']}")
print(f"权重: {result['data']['weights']}")
print(f"组合IC: {result['data']['evaluation']['ic_mean']}")
print(f"是否优于单因子: {result['data']['comparison']['is_better']}")

# 3. 因子组合评估（自定义权重）
response = requests.post(
    "http://localhost:8000/api/v1/research/eval/combine",
    json={
        "factor_names": ["custom_factor_001", "custom_factor_002"],
        "start_date": "2020-01-01",
        "end_date": "2024-12-31",
        "combination_method": "custom",
        "weights": [0.7, 0.3]
    }
)
result = response.json()
print(f"自定义权重组合结果: {result['data']}")
```

---

## 📁 文件结构

```
backend/
├── api/v1/research/
│   └── eval_router.py              (211行) - API路由
├── services/research/
│   └── factor_evaluation_service.py  (410行) - 服务层
└── models/                            (数据模型)
```

---

## 💡 评分机制

### 有效性评分规则

因子有效性评分由三个指标加权计算：

| 指标 | 权重 | 计算方式 |
|------|------|----------|
| IC均值 | 40% | 通过阈值：0.6 + (值/阈值) × 0.4 |
| IR | 30% | 同上 |
| IC正数占比 | 30% | 同上 |

### 判断标准

- **有效**: 总分 ≥ 0.6 或 所有指标都通过阈值
- **建议**: 根据未通过的指标给出优化建议

---

**状态**: ✅ 代码实现完成（90%），路由已注册
