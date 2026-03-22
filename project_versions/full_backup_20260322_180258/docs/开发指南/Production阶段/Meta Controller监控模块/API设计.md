# Meta Controller监控模块 - API设计

> **阶段**: Production阶段
> **状态**: 🟡 文档完善中
> **最后更新**: 2026-02-14

---

## 📡 API端点总览

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/production/meta/status` | GET | 获取监控状态 | ⏸️ 待实现 |
| `/api/v1/production/meta/ic-tracking` | GET | IC/IR跟踪数据 | ⏸️ 待实现 |
| `/api/v1/production/meta/ic-history` | GET | IC历史趋势 | ⏸️ 待实现 |
| `/api/v1/production/meta/degradation/check` | GET | 衰减检测结果 | ⏸️ 待实现 |
| `/api/v1/production/meta/switch/auto` | POST | 触发自动切换 | ⏸️ 待实现 |
| `/api/v1/production/meta/switch/manual` | POST | 手动切换模型 | ⏸️ 待实现 |
| `/api/v1/production/meta/alerts` | GET | 获取告警列表 | ⏸️ 待实现 |
| `/api/v1/production/meta/alerts/acknowledge` | POST | 确认告警 | ⏸️ 待实现 |
| `/api/v1/production/meta/metrics` | GET | 性能指标汇总 | ⏸️ 待实现 |
| `/api/v1/production/meta/health` | GET | 健康检查 | ⏸️ 待实现 |

---

## 📝 详细API定义

### 1. 获取监控状态

**端点**: `GET /api/v1/production/meta/status`

**描述**: 获取Meta Controller当前监控状态

**响应结果**:
```json
{
  "success": true,
  "data": {
    "status": "active",
    "monitoring_since": "2026-02-14T09:00:00",
    "active_model": {
      "model_id": "xgb_v1.1",
      "model_name": "xgb_classification",
      "loaded_at": "2026-02-14T08:30:00"
    },
    "standby_models": [
      {
        "model_id": "xgb_v1.0",
        "status": "ready"
      }
    ],
    "current_ic": 0.042,
    "ic_trend": "stable",
    "degradation_risk": "low",
    "alerts_count": 0
  }
}
```

---

### 2. 获取IC/IR跟踪数据

**端点**: `GET /api/v1/production/meta/ic-tracking`

**查询参数**:
- `model_id` (可选): 指定模型ID
- `period` (可选): 时间周期 (1d/7d/30d)

**响应结果**:
```json
{
  "success": true,
  "data": {
    "model_id": "xgb_v1.1",
    "ic": {
      "current": 0.042,
      "ma7": 0.045,
      "ma14": 0.044,
      "ma30": 0.043
    },
    "ir": {
      "current": 0.62,
      "ma7": 0.58
    },
    "degradation_pct": 5.2,
    "trend": "stable",
    "data_points": 1000,
    "last_updated": "2026-02-14T10:30:00"
  }
}
```

---

### 3. 获取IC历史趋势

**端点**: `GET /api/v1/production/meta/ic-history`

**查询参数**:
- `model_id` (可选): 指定模型ID
- `start_date`: 开始日期
- `end_date`: 结束日期
- `interval`: 采样间隔 (1h/1d)

**响应结果**:
```json
{
  "success": true,
  "data": {
    "model_id": "xgb_v1.1",
    "history": [
      {
        "timestamp": "2026-02-14T10:00:00",
        "ic": 0.041,
        "ir": 0.60,
        "sample_size": 100
      },
      {
        "timestamp": "2026-02-14T09:00:00",
        "ic": 0.043,
        "ir": 0.63,
        "sample_size": 95
      }
    ],
    "statistics": {
      "min_ic": 0.035,
      "max_ic": 0.052,
      "avg_ic": 0.044,
      "std_ic": 0.008
    }
  }
}
```

---

### 4. 衰减检测

**端点**: `GET /api/v1/production/meta/degradation/check`

**描述**: 执行模型衰减检测并返回结果

**响应结果**:
```json
{
  "success": true,
  "data": {
    "model_id": "xgb_v1.1",
    "degradation_detected": false,
    "risk_level": "low",
    "signals": {
      "ic_decline": {
        "triggered": false,
        "value": 0.05,
        "threshold": 0.30
      },
      "distribution_shift": {
        "triggered": false,
        "ks_statistic": 0.08,
        "threshold": 0.20
      },
      "accuracy_decline": {
        "triggered": false,
        "current": 0.75,
        "baseline": 0.78,
        "decline_pct": 3.8
      }
    },
    "recommendation": "继续监控，暂无需切换",
    "next_check_at": "2026-02-14T11:00:00"
  }
}
```

---

### 5. 触发自动切换

**端点**: `POST /api/v1/production/meta/switch/auto`

**描述**: 根据衰减检测结果自动切换模型

**请求参数**:
```json
{
  "force": false,
  "target_model_id": null
}
```

**响应结果**:
```json
{
  "success": true,
  "data": {
    "switch_triggered": true,
    "reason": "IC衰减超过阈值 (65%)",
    "from_model": "xgb_v1.1",
    "to_model": "xgb_v1.0",
    "switched_at": "2026-02-14T10:35:00",
    "switch_time_ms": 45.2
  }
}
```

---

### 6. 手动切换模型

**端点**: `POST /api/v1/production/meta/switch/manual`

**描述**: 手动切换到指定模型

**请求参数**:
```json
{
  "target_model_id": "xgb_v1.0",
  "reason": "运维人员手动切换"
}
```

**响应结果**:
```json
{
  "success": true,
  "data": {
    "switched": true,
    "from_model": "xgb_v1.1",
    "to_model": "xgb_v1.0",
    "switched_at": "2026-02-14T10:40:00",
    "reason": "运维人员手动切换"
  }
}
```

---

### 7. 获取告警列表

**端点**: `GET /api/v1/production/meta/alerts`

**查询参数**:
- `status`: 告警状态 (active/acknowledged/resolved)
- `severity`: 严重程度 (critical/warning/info)
- `limit`: 返回数量

**响应结果**:
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "alert_id": "alert_20260214_001",
        "severity": "warning",
        "type": "ic_degradation",
        "message": "IC下降至0.025，接近阈值",
        "model_id": "xgb_v1.1",
        "triggered_at": "2026-02-14T10:30:00",
        "status": "active",
        "acknowledged_by": null
      }
    ],
    "total": 1,
    "active_count": 1,
    "warning_count": 1,
    "critical_count": 0
  }
}
```

---

### 8. 确认告警

**端点**: `POST /api/v1/production/meta/alerts/acknowledge`

**请求参数**:
```json
{
  "alert_id": "alert_20260214_001",
  "acknowledged_by": "admin",
  "note": "已知晓，正在处理"
}
```

**响应结果**:
```json
{
  "success": true,
  "data": {
    "alert_id": "alert_20260214_001",
    "status": "acknowledged",
    "acknowledged_at": "2026-02-14T10:45:00",
    "acknowledged_by": "admin"
  }
}
```

---

### 9. 性能指标汇总

**端点**: `GET /api/v1/production/meta/metrics`

**描述**: 获取所有监控指标的综合视图

**响应结果**:
```json
{
  "success": true,
  "data": {
    "model_metrics": {
      "model_id": "xgb_v1.1",
      "ic": 0.042,
      "ir": 0.62,
      "prediction_count_24h": 12500,
      "accuracy_5d": 0.75
    },
    "performance_metrics": {
      "avg_latency_ms": 28.5,
      "p95_latency_ms": 45.2,
      "p99_latency_ms": 68.3,
      "availability": 0.9995
    },
    "system_metrics": {
      "cpu_usage": 35.2,
      "memory_usage": 62.8,
      "active_connections": 150
    },
    "monitoring_metrics": {
      "uptime_hours": 168,
      "alerts_24h": 2,
      "switches_7d": 1
    }
  }
}
```

---

### 10. 健康检查

**端点**: `GET /api/v1/production/meta/health`

**响应结果**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2026-02-14T10:50:00",
    "components": {
      "ic_tracker": "healthy",
      "degradation_detector": "healthy",
      "auto_switcher": "healthy",
      "alert_manager": "healthy"
    },
    "last_ic_calculation": "2026-02-14T10:49:30",
    "last_degradation_check": "2026-02-14T10:45:00"
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

**创建时间**: 2026-02-11
**最后更新**: 2026-02-14
**状态**: 🟡 文档完善中
