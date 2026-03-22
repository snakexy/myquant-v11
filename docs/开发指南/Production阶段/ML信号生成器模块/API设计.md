# ML信号生成器 - API设计

> **版本**: v1.0
> **创建时间**: 2026-02-13
> **状态**: 🟡 设计阶段
> **最后更新**: 2026-02-13

---

## 🔗 QLib集成说明

本模块深度集成QLib高级模块：

| QLib模块 | API集成点 | 作用 |
|---------|---------|------|
| **Workflow管理模块** | `/api/v1/production/ml/predict/*` | 使用QLib Workflow编排预测流程 |
| **Online Serving** | 实时预测端点 | QLib高性能在线预测服务 |

### QLib Online Serving集成示例

```python
# 实时预测使用QLib Online Serving
from qlib.workflow import R
from qlib.online.update import PeriodicUpdater

class MLOnlinePredictor:
    """基于QLib Online的预测服务"""

    def __init__(self, model_path):
        # 1. 加载模型
        self.model = R.load_obj(model_path)

        # 2. 初始化预测服务
        self.server = QLibPredictionService(
            model=self.model,
            batch_size=100,
            max_latency_ms=50
        )

    async def predict(self, instrument: str) -> PredictionResult:
        # 3. 执行预测（<50ms）
        features = await self._get_features(instrument)
        prediction = self.server.predict(features)
        return prediction

    def get_latency_ms(self) -> float:
        return self.server.get_latency()
```

---

## 📊 API端点总览

### 1. 模型管理

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/production/ml/models/register` | POST | 注册模型版本 | ⏸️ 待实现 |
| `/api/v1/production/ml/models/load` | POST | 热加载模型 | ⏸️ 待实现 |
| `/api/v1/production/ml/models/versions` | GET | 查看模型版本 | ⏸️ 待实现 |
| `/api/v1/production/ml/models/switch` | POST | 切换模型 | ⏸️ 待实现 |
| `/api/v1/production/ml/models/rollback` | POST | 回滚模型 | ⏸️ 待实现 |
| `/api/v1/production/ml/models/ab-test` | POST | A/B测试 | ⏸️ 待实现 |

### 2. 实时预测

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/production/ml/predict/single` | POST | 单股票预测 | ⏸️ 待实现 |
| `/api/v1/production/ml/predict/batch` | POST | 批量预测 | ⏸️ 待实现 |
| `/api/v1/production/ml/predict/market` | POST | 全市场预测 | ⏸️ 待实现 |
| `/api/v1/production/ml/prediction/status` | GET | 预测状态查询 | ⏸️ 待实现 |

### 3. ML信号生成

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/trading/ml/signals/generate` | POST | 生成ML交易信号 | ⏸️ 待实现 |
| `/api/v1/trading/ml/signals/batch` | POST | 批量生成交易信号 | ⏸️ 待实现 |
| `/api/v1/trading/ml/signals/validate` | POST | 验证信号有效性 | ⏸️ 待实现 |

### 4. ML仓位计算

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/trading/ml/position/calculate` | POST | 计算ML驱动仓位 | ⏸️ 待实现 |
| `/api/v1/trading/ml/position/recommend` | POST | 获取仓位建议 | ⏸️ 待实现 |

### 5. ML风险评估

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/trading/ml/risk/assess` | POST | 评估组合风险 | ⏸️ 待实现 |
| `/api/v1/trading/ml/risk/adjust` | POST | 调整风险参数 | ⏸️ 待实现 |

### 6. 性能监控

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/production/ml/monitoring/performance` | GET | 获取性能指标 | ⏸️ 待实现 |
| `/api/v1/production/ml/monitoring/degradation` | GET | 检测模型衰减 | ⏸️ 待实现 |
| `/api/v1/production/ml/monitoring/switch` | POST | 手动切换模型 | ⏸️ 待实现 |
| WS `/api/v1/production/ml/monitoring/stream` | WebSocket | 实时监控流 | ⏸️ 待实现 |

---

## 📝 详细API定义

### 1. 注册模型版本

**端点**: `POST /api/v1/production/ml/models/register`

**请求参数**:
```json
{
  "model_name": "xgb_classification",
  "model_id": "xgb_v1.1",
  "model_path": "/models/xgb_v1.1.pkl",
  "metadata": {
    "version": "1.1",
    "trained_at": "2026-02-12",
    "ic": 0.045,
    "features": ["MA5", "MA20", "RSI", "MACD"]
  }
}
```

**响应结果**:
```json
{
  "success": true,
  "data": {
    "model_id": "xgb_v1.1",
    "status": "ready",
    "message": "模型注册成功"
  }
}
```

---

### 2. 热加载模型

**端点**: `POST /api/v1/production/ml/models/load`

**请求参数**:
```json
{
  "model_name": "xgb_classification",
  "target_version": "v1.1"
}
```

**响应结果**:
```json
{
  "success": true,
  "data": {
    "success": true,
    "new_version": "v1.1",
    "load_time_ms": 45.2
  }
}
```

---

### 3. 单股票实时预测

**端点**: `POST /api/v1/production/ml/predict/single`

**请求参数**:
```json
{
  "instrument": "000001.SZ",
  "model_version": "latest"
}
```

**响应结果**:
```json
{
  "success": true,
  "data": {
    "instrument": "000001.SZ",
    "prediction_score": 0.78,
    "prediction": "up",
    "confidence": 0.85,
    "buy_recommendation": "STRONG",
    "model_id": "xgb_classification_v1",
    "model_version": "v1.1",
    "features_used": ["MA5", "MA20", "RSI", "MACD", "BOLL_UPPER"],
    "timestamp": "2026-02-13T09:30:00",
    "latency_ms": 23.5
  }
}
```

---

### 4. 批量预测

**端点**: `POST /api/v1/production/ml/predict/batch`

**请求参数**:
```json
{
  "instruments": ["000001.SZ", "000002.SZ", "000003.SZ"],
  "model_version": "latest"
}
```

**响应结果**:
```json
{
  "success": true,
  "data": {
    "predictions": [
      {
        "instrument": "000001.SZ",
        "prediction_score": 0.78,
        "prediction": "up"
      },
      {
        "instrument": "000002.SZ",
        "prediction_score": 0.65,
        "prediction": "up"
      }
    ],
    "total": 2,
    "elapsed_ms": 1250
  }
}
```

---

### 5. 生成ML交易信号

**端点**: `POST /api/v1/trading/ml/signals/generate`

**请求参数**:
```json
{
  "ml_prediction": {
    "instrument": "000001.SZ",
    "prediction_score": 0.78,
    "prediction": "up",
    "confidence": 0.85,
    "model_id": "xgb_v1.1",
    "features_used": ["MA5", "MA20", "RSI"]
  },
  "current_price": 10.5,
  "position_info": {
    "current_position": 1000,
    "avg_cost": 10.2,
    "unrealized_pnl": 300
  }
}
```

**响应结果**:
```json
{
  "success": true,
  "data": {
    "signal_id": "sig_20260213_001",
    "instrument": "000001.SZ",
    "signal_type": "BUY",
    "strength": "NORMAL",
    "score": 0.78,
    "confidence": 0.85,
    "current_price": 10.5,
    "target_price": 10.605,
    "reason": "ML预测评分:0.78,置信度:85%",
    "ml_model_id": "xgb_v1.1",
    "timestamp": "2026-02-13T10:30:00Z"
  }
}
```

---

### 6. 评估组合风险

**端点**: `POST /api/v1/trading/ml/risk/assess`

**请求参数**:
```json
{
  "ml_predictions": [
    {
      "instrument": "000001.SZ",
      "prediction": "up",
      "confidence": 0.85
    },
    {
      "instrument": "000002.SZ",
      "prediction": "up",
      "confidence": 0.90
    }
  ]
}
```

**响应结果**:
```json
{
  "success": true,
  "data": {
    "risk_level": "MEDIUM",
    "concentration_ratio": 1.0,
    "up_count": 2,
    "down_count": 0,
    "avg_confidence": 0.875,
    "recommendation": "预测全部集中在上涨，注意控制仓位或考虑对冲"
  }
}
```

---

### 7. 获取性能指标

**端点**: `GET /api/v1/production/ml/monitoring/performance`

**响应结果**:
```json
{
  "success": true,
  "data": {
    "model_id": "xgb_v1.1",
    "ic": 0.042,
    "ic_ma7": 0.045,
    "ic_ma14": 0.044,
    "ic_ma30": 0.043,
    "avg_latency_ms": 28.5,
    "prediction_count_24h": 12500,
    "status": "healthy"
  }
}
```

---

## 🔗 相关文档

- [概述](./概述.md)
- [数据模型](./数据模型.md)
- [前端组件](./前端组件.md)
- [实施记录](./实施记录.md)

---

**创建时间**: 2026-02-13
**最后更新**: 2026-02-13
