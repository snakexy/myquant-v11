# Portfolio Strategy API设计

> **模块**: Portfolio Strategy - 投资组合策略
> **版本**: v1.0
> **最后更新**: 2026-02-23

---

## API 端点列表

| 端点 | 方法 | 功能 | 优先级 |
|------|------|------|--------|
| `/api/v1/research/portfolio/health` | GET | 健康检查 | P1 |
| `/api/v1/research/portfolio/strategies` | GET | 获取支持的策略列表 | P1 |
| `/api/v1/research/portfolio/config` | GET | 获取策略配置 | P1 |
| `/api/v1/research/portfolio/config` | POST | 保存策略配置 | P1 |
| `/api/v1/research/portfolio/generate` | POST | 生成投资组合 | P1 |
| `/api/v1/research/portfolio/backtest` | POST | 策略回测 | P2 |
| `/api/v1/research/portfolio/optimize` | POST | 参数优化 (供RL使用) | P2 |

---

## API 详细说明

### 1. 健康检查

**端点**: `GET /api/v1/research/portfolio/health`

**说明**: 检查 Portfolio Strategy 服务状态

**请求**: 无

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "supported_strategies": ["TopkDropoutStrategy", "EnhancedIndexingStrategy"]
  }
}
```

---

### 2. 获取支持的策略列表

**端点**: `GET /api/v1/research/portfolio/strategies`

**说明**: 获取所有支持的 Portfolio Strategy 类型

**请求**: 无

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "strategies": [
      {
        "name": "TopkDropoutStrategy",
        "display_name": "Topk-Drop策略",
        "description": "选择Top-K个股票，每天卖出N个并买入N个",
        "params": [
          {
            "name": "topk",
            "type": "integer",
            "default": 50,
            "min": 10,
            "max": 100,
            "description": "持有股票数量"
          },
          {
            "name": "n_drop",
            "type": "integer",
            "default": 5,
            "min": 1,
            "max": 20,
            "description": "每日卖出数量"
          }
        ]
      },
      {
        "name": "EnhancedIndexingStrategy",
        "display_name": "增强指数化策略",
        "description": "在跟踪基准指数的同时获取超额收益",
        "params": [
          {
            "name": "risk_thld",
            "type": "float",
            "default": 0.05,
            "description": "风险容忍度"
          }
        ]
      }
    ]
  }
}
```

---

### 3. 获取策略配置

**端点**: `GET /api/v1/research/portfolio/config`

**说明**: 获取当前策略配置

**请求**: 无

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "strategy_type": "TopkDropoutStrategy",
    "params": {
      "topk": 50,
      "n_drop": 5
    },
    "updated_at": "2026-02-23T10:00:00"
  }
}
```

---

### 4. 保存策略配置

**端点**: `POST /api/v1/research/portfolio/config`

**说明**: 保存策略配置

**请求**:
```json
{
  "strategy_type": "TopkDropoutStrategy",
  "params": {
    "topk": 50,
    "n_drop": 5
  }
}
```

**响应**:
```json
{
  "code": 200,
  "message": "策略配置保存成功",
  "data": {
    "config_id": "config_20260223_100000",
    "strategy_type": "TopkDropoutStrategy",
    "params": {
      "topk": 50,
      "n_drop": 5
    },
    "created_at": "2026-02-23T10:00:00"
  }
}
```

---

### 5. 生成投资组合

**端点**: `POST /api/v1/research/portfolio/generate`

**说明**: 根据ML预测分数生成投资组合

**请求**:
```json
{
  "signal_id": "pred_20260223_100000",
  "strategy_type": "TopkDropoutStrategy",
  "strategy_params": {
    "topk": 50,
    "n_drop": 5
  },
  "date": "2026-02-23"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "portfolio_id": "port_20260223_100000",
    "stocks": [
      {
        "instrument": "000001.SZ",
        "score": 0.85,
        "weight": 0.02,
        "action": "buy"
      },
      {
        "instrument": "000002.SZ",
        "score": 0.82,
        "weight": 0.02,
        "action": "hold"
      }
    ],
    "summary": {
      "total_stocks": 50,
      "buy_count": 5,
      "sell_count": 5,
      "hold_count": 40
    }
  }
}
```

---

### 6. 策略回测

**端点**: `POST /api/v1/research/portfolio/backtest`

**说明**: 在历史数据上回测策略

**请求**:
```json
{
  "strategy_type": "TopkDropoutStrategy",
  "strategy_params": {
    "topk": 50,
    "n_drop": 5
  },
  "signal_id": "pred_20260223_100000",
  "start_date": "2025-01-01",
  "end_date": "2026-02-23",
  "benchmark": "SH000300"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "回测完成",
  "data": {
    "backtest_id": "bt_20260223_100000",
    "metrics": {
      "annual_return": 0.1523,
      "sharpe_ratio": 1.75,
      "max_drawdown": -0.059,
      "win_rate": 0.58
    },
    "positions": [...]
  }
}
```

---

### 7. 参数优化 (供RL使用)

**端点**: `POST /api/v1/research/portfolio/optimize`

**说明**: 评估一组策略参数的性能（供 RL 优化使用）

**请求**:
```json
{
  "strategy_type": "TopkDropoutStrategy",
  "params": {
    "topk": 40,
    "n_drop": 3
  },
  "signal_id": "pred_20260223_100000",
  "start_date": "2025-01-01",
  "end_date": "2026-02-23"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "评估完成",
  "data": {
    "metrics": {
      "sharpe_ratio": 1.68,
      "annual_return": 0.148,
      "max_drawdown": -0.055
    },
    "score": 1.68
  }
}
```

**说明**: 这个接口会被 RL 模块调用，用于评估不同参数组合的性能。

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 策略类型不存在 |
| 500 | 服务器内部错误 |

---

## 数据模型

详见 [数据模型.md](./数据模型.md)

---

**创建时间**: 2026-02-23
**最后更新**: 2026-02-23
