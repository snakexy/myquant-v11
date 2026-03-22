# Online Serving模块 - API设计

> **模块**: Online Serving - 在线因子服务
> **版本**: v1.0
> **最后更新**: 2026-02-22

---

## 📋 API端点总览

### Research阶段 API端点

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/research/online/health` | GET | 健康检查 | 📋 |
| `/api/v1/research/online/calculate` | POST | 在线因子计算 | 📋 |
| `/api/v1/research/online/cache` | GET | 获取缓存因子 | 📋 |
| `/api/v1/research/online/cache` | POST | 保存因子到缓存 | 📋 |
| `/api/v1/research/online/cache` | DELETE | 清除缓存 | 📋 |
| `/api/v1/research/online/incremental` | POST | 增量更新因子 | 📋 |
| `/api/v1/research/online/status` | GET | 服务状态统计 | 📋 |

---

## 1. 健康检查

### GET `/api/v1/research/online/health`

**描述**: 检查在线因子服务健康状态

**请求**: 无参数

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "service": "Online Serving模块",
    "status": "healthy",
    "cache_status": "connected",
    "cache_type": "redis",
    "uptime": 86400
  },
  "timestamp": "2026-02-22T10:00:00"
}
```

---

## 2. 在线因子计算

### POST `/api/v1/research/online/calculate`

**描述**: 计算因子数据，自动缓存结果

**请求体**:
```json
{
  "factor_names": ["factor_001", "factor_002", "factor_003"],
  "stock_codes": ["000001.SZ", "000002.SZ", "600000.SH"],
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "use_cache": true,
  "force_refresh": false,
  "parallel": true
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_names | string[] | 是 | 因子名称列表 |
| stock_codes | string[] | 是 | 股票代码列表 |
| start_date | string | 是 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 是 | 结束日期 (YYYY-MM-DD) |
| use_cache | boolean | 否 | 是否使用缓存，默认true |
| force_refresh | boolean | 否 | 强制刷新缓存，默认false |
| parallel | boolean | 否 | 并行计算，默认true |

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "calc_20260222_001",
    "status": "completed",
    "factor_count": 3,
    "stock_count": 3,
    "date_count": 244,
    "data_points": 2196,
    "cache_hit": false,
    "calculation_time": 1.23,
    "cached": true,
    "factors": {
      "factor_001": {
        "data": [
          {"date": "2025-01-01", "stock": "000001.SZ", "value": 0.123}
        ]
      }
    }
  },
  "timestamp": "2026-02-22T10:00:00"
}
```

---

## 3. 获取缓存因子

### GET `/api/v1/research/online/cache`

**描述**: 从缓存获取因子数据

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_names | string | 是 | 因子名称，逗号分隔 |
| stock_codes | string | 否 | 股票代码，逗号分隔（默认全部） |
| start_date | string | 是 | 开始日期 |
| end_date | string | 是 | 结束日期 |

**请求示例**:
```
GET /api/v1/research/online/cache?factor_names=factor_001,factor_002&start_date=2025-01-01&end_date=2025-01-31
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "factors": {
      "factor_001": {
        "data": [
          {"date": "2025-01-01", "stock": "000001.SZ", "value": 0.123},
          {"date": "2025-01-01", "stock": "000002.SZ", "value": 0.456},
          {"date": "2025-01-02", "stock": "000001.SZ", "value": 0.234}
        ],
        "cached_at": "2026-02-22T09:00:00",
        "expires_at": "2026-02-23T09:00:00",
        "data_points": 3
      },
      "factor_002": {
        "error": "not_cached",
        "message": "因子数据未缓存，请先计算"
      }
    },
    "from_cache": true,
    "cache_stats": {
      "hit": 1,
      "miss": 1,
      "hit_rate": 0.5
    }
  },
  "timestamp": "2026-02-22T10:00:00"
}
```

---

## 4. 保存因子到缓存

### POST `/api/v1/research/online/cache`

**描述**: 手动保存因子数据到缓存

**请求体**:
```json
{
  "factor_name": "factor_001",
  "data": [
    {"date": "2025-01-01", "stock": "000001.SZ", "value": 0.123},
    {"date": "2025-01-01", "stock": "000002.SZ", "value": 0.456}
  ],
  "ttl": 86400
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_name | string | 是 | 因子名称 |
| data | array | 是 | 因子数据数组 |
| ttl | int | 否 | 缓存过期时间（秒），默认86400 |

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "factor_name": "factor_001",
    "data_points": 2,
    "cached_at": "2026-02-22T10:00:00",
    "expires_at": "2026-02-23T10:00:00"
  },
  "timestamp": "2026-02-22T10:00:00"
}
```

---

## 5. 清除缓存

### DELETE `/api/v1/research/online/cache`

**描述**: 清除因子缓存

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_names | string | 否 | 因子名称，逗号分隔（默认全部） |
| all | boolean | 否 | 清除所有缓存，默认false |

**请求示例**:
```
DELETE /api/v1/research/online/cache?factor_names=factor_001,factor_002
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "cleared": 2,
    "factor_names": ["factor_001", "factor_002"]
  },
  "timestamp": "2026-02-22T10:00:00"
}
```

---

## 6. 增量更新因子

### POST `/api/v1/research/online/incremental`

**描述**: 增量更新因子数据（Updater功能）

**请求体**:
```json
{
  "factor_names": ["factor_001", "factor_002"],
  "update_type": "daily",
  "date": "2026-02-22"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| factor_names | string[] | 是 | 因子名称列表 |
| update_type | string | 否 | 更新类型: daily/weekly/monthly |
| date | string | 否 | 更新日期，默认今天 |

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "update_id": "upd_20260222_001",
    "status": "completed",
    "updated_factors": 2,
    "updated_stocks": 4000,
    "updated_data_points": 8000,
    "update_time": 0.56
  },
  "timestamp": "2026-02-22T10:00:00"
}
```

---

## 7. 服务状态统计

### GET `/api/v1/research/online/status`

**描述**: 获取服务状态和统计信息

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "service_status": "running",
    "uptime": 86400,
    "cache": {
      "type": "redis",
      "status": "connected",
      "memory_used": "256MB",
      "memory_limit": "1GB",
      "keys": 360,
      "hit_rate": 0.85
    },
    "statistics": {
      "total_calculations": 1000,
      "total_cache_hits": 850,
      "total_cache_misses": 150,
      "average_calculation_time": 1.23,
      "data_points_served": 1000000
    },
    "last_update": "2026-02-22T09:00:00"
  },
  "timestamp": "2026-02-22T10:00:00"
}
```

---

## 📐 数据模型

### FactorCacheData
```python
@dataclass
class FactorCacheData:
    """因子缓存数据"""
    factor_name: str
    data: List[FactorDataPoint]
    cached_at: datetime
    expires_at: datetime
    version: str = "1.0"

@dataclass
class FactorDataPoint:
    """因子数据点"""
    date: str          # 日期 YYYY-MM-DD
    stock: str         # 股票代码
    value: float       # 因子值
```

### CacheConfig
```python
@dataclass
class CacheConfig:
    """缓存配置"""
    backend: str = "redis"      # redis / memory
    ttl: int = 86400            # 默认过期时间（秒）
    max_memory: str = "1GB"     # 最大内存
    prefix: str = "factor:"     # 缓存键前缀
```

---

## 🔗 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 因子数据未找到 |
| 500 | 服务器内部错误 |
| 503 | 缓存服务不可用 |

---

## 📚 相关文档

- [概述](./概述.md) - 模块概述
- [缓存设计](./缓存设计.md) - 缓存机制设计 📋
- [实施记录](./实施记录.md) - 开发实施记录 📋

---

**创建时间**: 2026-02-22
**最后更新**: 2026-02-22
**状态**: 📋 设计中
