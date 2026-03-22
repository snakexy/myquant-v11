# 因子分析模块 - API设计

> **阶段**: Research阶段
> **状态**: ✅ 代码实现完成（100%）
> **版本**: v4.1
> **最后更新**: 2026-02-22

---

## 📡 API端点列表

### 已实现端点 (5个)

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/research/analysis/ic-ir` | POST | IC/IR分析 | ✅ |
| `/api/v1/research/analysis/distribution` | POST | 分布分析 | ✅ |
| `/api/v1/research/analysis/correlation` | POST | 相关性分析 | ✅ |
| `/api/v1/research/analysis/factors` | GET | 获取因子列表 | ✅ |
| `/api/v1/research/analysis/health` | GET | 健康检查 | ✅ |

---

## 📄 API详细说明

### 1. IC/IR分析

**端点**: `POST /api/v1/research/analysis/ic-ir`

**功能**: 计算因子的信息系数(IC)和信息比率(IR)

**请求参数**:
```json
{
  "factor_name": "custom_factor_001",
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "instruments": ["000001.SZ", "000002.SZ"],
  "period": "1d"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_name | string | ✅ | 因子名称 |
| start_date | string | ✅ | 开始日期 (YYYY-MM-DD) |
| end_date | string | ✅ | 结束日期 (YYYY-MM-DD) |
| instruments | array | ❌ | 股票列表 |
| period | string | ❌ | 周期，默认1d |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "factor_name": "custom_factor_001",
    "ic": {
      "mean": 0.0523,
      "std": 0.1234,
      "min": -0.2345,
      "max": 0.3456,
      "ic_series": [
        {"date": "2020-01-01", "ic": 0.0456},
        {"date": "2020-01-02", "ic": 0.0678}
      ]
    },
    "ir": 0.4238,
    "ic_positive_ratio": 0.5678,
    "t_stat": 3.4567,
    "p_value": 0.0001
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

---

### 2. 分布分析

**端点**: `POST /api/v1/research/analysis/distribution`

**功能**: 分析因子统计分布特性

**请求参数**:
```json
{
  "factor_name": "custom_factor_001",
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "bins": 50
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_name | string | ✅ | 因子名称 |
| start_date | string | ❌ | 开始日期 |
| end_date | string | ❌ | 结束日期 |
| bins | int | ❌ | 分箱数量，默认50 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "factor_name": "custom_factor_001",
    "statistics": {
      "count": 100000,
      "mean": 0.0523,
      "std": 0.1234,
      "min": -0.5678,
      "max": 0.7890,
      "skewness": 0.1234,
      "kurtosis": 2.5678
    },
    "histogram": {
      "bins": [-0.5, -0.4, -0.3, 0.0, 0.3, 0.4, 0.5],
      "counts": [100, 500, 2000, 50000, 2000, 500, 100]
    },
    "percentiles": {
      "1%": -0.3456,
      "5%": -0.2345,
      "25%": -0.1234,
      "50%": 0.0456,
      "75%": 0.2345,
      "95%": 0.4567,
      "99%": 0.5678
    }
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

---

### 3. 相关性分析

**端点**: `POST /api/v1/research/analysis/correlation`

**功能**: 计算多个因子之间的相关性矩阵

**请求参数**:
```json
{
  "factor_names": ["custom_factor_001", "custom_factor_002", "momentum_factor"],
  "start_date": "2020-01-01",
  "end_date": "2024-12-31",
  "method": "pearson"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_names | array | ✅ | 因子名称列表（至少2个） |
| start_date | string | ❌ | 开始日期 |
| end_date | string | ❌ | 结束日期 |
| method | string | ❌ | 相关性方法：pearson/spearman |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "factor_names": ["custom_factor_001", "custom_factor_002", "momentum_factor"],
    "correlation_matrix": [
      [1.0, 0.2345, 0.1234],
      [0.2345, 1.0, 0.3456],
      [0.1234, 0.3456, 1.0]
    ],
    "method": "pearson"
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

---

### 4. 获取因子列表

**端点**: `GET /api/v1/research/analysis/factors`

**功能**: 获取可用的因子名称列表

**请求参数**: 无

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "factors": [
      "alpha158_001",
      "alpha158_002",
      "custom_factor_001",
      "momentum_factor",
      "reversal_factor",
      "volatility_factor",
      "liquidity_factor"
    ]
  },
  "timestamp": "2026-02-11T15:30:00"
}
```

---

### 5. 健康检查

**端点**: `GET /api/v1/research/analysis/health`

**功能**: 检查服务健康状态

**请求参数**: 无

**响应示例**:
```json
{
  "service": "因子分析模块",
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

# 1. IC/IR分析
response = requests.post(
    "http://localhost:8000/api/v1/research/analysis/ic-ir",
    json={
        "factor_name": "custom_factor_001",
        "start_date": "2020-01-01",
        "end_date": "2024-12-31"
    }
)
result = response.json()
print(f"IC均值: {result['data']['ic']['mean']}")
print(f"IR: {result['data']['ir']}")

# 2. 分布分析
response = requests.post(
    "http://localhost:8000/api/v1/research/analysis/distribution",
    json={
        "factor_name": "custom_factor_001",
        "bins": 50
    }
)
result = response.json()
print(f"均值: {result['data']['statistics']['mean']}")
print(f"标准差: {result['data']['statistics']['std']}")

# 3. 相关性分析
response = requests.post(
    "http://localhost:8000/api/v1/research/analysis/correlation",
    json={
        "factor_names": ["custom_factor_001", "custom_factor_002"],
        "method": "pearson"
    }
)
result = response.json()
print(f"相关系数矩阵: {result['data']['correlation_matrix']}")
```

---

## 📁 文件结构

```
backend/
├── api/v1/research/
│   └── analysis_router.py          (298行) - API路由
├── services/research/
│   ├── factor_analysis_service.py  (439行) - 服务层
│   └── factor_analysis_storage.py  (存储层)
└── models/                         (数据模型)
```

---

**状态**: ✅ 代码实现完成（100%），路由已注册，真实数据集成测试通过（10/10）
