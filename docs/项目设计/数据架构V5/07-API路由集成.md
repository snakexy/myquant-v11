# V5 API 路由集成

> **FastAPI 路由集成文档** - V5 场景化服务的 API 接口说明

**更新日期**: 2026-03-20
**适用架构**: V5 场景化服务
**API 基础路径**: `/api/v5`

---

## 📡 API 概览

V5 场景化服务提供 **25 个 API 端点**，分为 5 大服务模块：

| 服务 | 端点数 | 基础路径 | 说明 |
|------|--------|----------|------|
| **K线服务** | 6 | `/api/v5/kline` | 实时K线、无缝K线、历史K线 |
| **监控服务** | 4 | `/api/v5/monitoring` | 热点板块、热点股票、异常检测 |
| **增量更新服务** | 5 | `/api/v5/incremental` | 数据更新、缺失检测 |
| **数据转换服务** | 3 | `/api/v5/conversion` | 批量转换TDX数据 |
| **实时行情服务** | 7 | `/api/v5/market` | 实时行情、热点扫描 |

---

## 🚀 K线服务 `/api/v5/kline`

### 1. 获取实时K线（订阅+聚合）

```http
POST /api/v5/kline/intraday
Content-Type: application/json

{
  "symbols": ["600000.SH", "000001.SZ"],
  "period": "1m",
  "count": 100,
  "subscribe": true
}
```

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "600000.SH": {
      "symbol": "600000.SH",
      "period": "1m",
      "data": [...],
      "source": "subscription"
    }
  },
  "message": "success"
}
```

### 2. 获取无缝K线（历史+实时衔接）

```http
POST /api/v5/kline/seamless
Content-Type: application/json

{
  "symbols": ["600000.SH"],
  "period": "1d",
  "end_date": "2026-03-20",
  "days_back": 5
}
```

### 3. 获取单只股票实时K线

```http
GET /api/v5/kline/realtime/600000.SH?period=1m&count=100
```

### 4. 获取历史K线

```http
POST /api/v5/kline/history/600000.SH?period=1d&start_date=2026-03-01&end_date=2026-03-20
```

### 5. 获取订阅状态

```http
GET /api/v5/kline/subscription/status
```

### 6. 更新订阅列表

```http
POST /api/v5/kline/subscription/update
Content-Type: application/json

["600000.SH", "000001.SZ", "300001.SZ"]
```

---

## 🔍 监控服务 `/api/v5/monitoring`

### 1. 获取热点板块

```http
GET /api/v5/monitoring/hot-sectors?limit=20&min_change_pct=0.5
```

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "count": 20,
    "sectors": [
      {
        "code": "880001",
        "name": "银行",
        "index": 3500.5,
        "change_pct": 2.5,
        "up_count": 25,
        "down_count": 3,
        "component_count": 42,
        "amount": 1500000000,
        "timestamp": "2026-03-20T15:00:00"
      }
    ]
  }
}
```

### 2. 获取热点股票

```http
GET /api/v5/monitoring/hot-stocks?sector_code=880001&limit=50&min_change_pct=3.0
```

### 3. 异常检测

```http
POST /api/v5/monitoring/anomaly?volume_ratio_threshold=3.0&swing_threshold=5.0
Content-Type: application/json

["600000.SH", "000001.SZ", "300001.SZ"]
```

### 4. 获取市场概览

```http
GET /api/v5/monitoring/market-summary
```

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "timestamp": "2026-03-20T15:00:00",
    "indices": {
      "000001.SH": {
        "name": "上证指数",
        "price": 3050.5,
        "change_pct": 0.8
      }
    },
    "hot_sectors": [...],
    "hot_stocks": [...]
  }
}
```

---

## 📥 增量更新服务 `/api/v5/incremental`

### 1. 更新股票数据

```http
POST /api/v5/incremental/update
Content-Type: application/json

{
  "symbols": ["600000.SH", "000001.SZ"],
  "period": "1d",
  "days_back": 7,
  "save_to_db": false,
  "parallel": true
}
```

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "total": 2,
    "success": 2,
    "failed": 0,
    "total_records": 14,
    "duration": 1.25,
    "success_rate": "100.0%"
  }
}
```

### 2. 异步更新

```http
POST /api/v5/incremental/update-async
Content-Type: application/json

{
  "symbols": ["600000.SH"],
  "period": "1d",
  "days_back": 7,
  "save_to_db": false,
  "parallel": true
}
```

### 3. 检测缺失数据

```http
POST /api/v5/incremental/detect
Content-Type: application/json

{
  "symbols": ["600000.SH"],
  "period": "1d",
  "days_back": 30
}
```

### 4. 获取当天收盘快照

```http
POST /api/v5/incremental/snapshot
Content-Type: application/json

["600000.SH", "000001.SZ"]
```

### 5. 获取服务状态

```http
GET /api/v5/incremental/status
```

---

## 🔄 数据转换服务 `/api/v5/conversion`

### 1. 批量转换数据

```http
POST /api/v5/conversion/convert
Content-Type: application/json

{
  "symbols": ["600000.SH", "000001.SZ"],
  "period": "1d",
  "start_date": "2026-01-01",
  "end_date": "2026-03-20",
  "save_to_qlib": true,
  "parallel": true
}
```

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "total": 2,
    "success": 2,
    "failed": 0,
    "total_records": 120,
    "duration": 3.5,
    "success_rate": "100.0%"
  }
}
```

### 2. 获取转换进度

```http
GET /api/v5/conversion/progress
```

### 3. 异步转换

```http
POST /api/v5/conversion/convert-async
```

---

## 📊 实时行情服务 `/api/v5/market`

### 1. 获取实时行情

```http
POST /api/v5/market/quotes?use_cache=true
Content-Type: application/json

["600000.SH", "000001.SZ"]
```

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "count": 2,
    "quotes": {
      "600000.SH": {
        "code": "600000.SH",
        "name": "浦发银行",
        "price": 10.5,
        "change": 0.25,
        "change_pct": 2.44,
        "volume": 15000000,
        "amount": 157500000,
        "timestamp": "2026-03-20T15:00:00"
      }
    }
  }
}
```

### 2. 扫描热点股票

```http
GET /api/v5/market/hot-stocks/scan?market=all&min_change_pct=3.0&limit=50
```

### 3. 获取热点股票池

```http
GET /api/v5/market/hot-stocks/pool?limit=20
```

### 4. 更新订阅列表

```http
POST /api/v5/market/subscriptions/update
Content-Type: application/json

["600000.SH", "000001.SZ"]
```

### 5. 获取K线数据

```http
GET /api/v5/market/kline/600000.SH?period=1m&count=100
```

### 6. 获取服务状态

```http
GET /api/v5/market/status
```

### 7. 获取缓存统计

```http
GET /api/v5/market/cache/stats
```

---

## 📁 代码结构

```
backend/
├── data_providers/          # 数据提供者层
│   ├── models/              # 数据模型
│   ├── routing/             # 路由逻辑
│   ├── adapters/            # 数据源适配器
│   └── services/            # 场景化服务
│       ├── kline/           # K线服务
│       ├── monitoring/      # 监控服务
│       ├── incremental/     # 增量更新服务
│       ├── conversion/      # 数据转换服务
│       └── realtime_market/ # 实时行情服务
│
└── api/
    └── v5/                  # V5 API 路由
        ├── __init__.py
        ├── kline.py         # K线服务路由
        ├── monitoring.py    # 监控服务路由
        ├── incremental.py   # 增量更新路由
        ├── conversion.py    # 数据转换路由
        └── market.py        # 实时行情路由
```

---

## 🚀 快速开始

### 1. 启动服务器

```bash
cd backend
python -m api.main
```

服务器将在 `http://localhost:8000` 启动。

### 2. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 测试 API

```bash
# 获取热点板块
curl http://localhost:8000/api/v5/monitoring/hot-sectors?limit=10

# 获取实时K线
curl -X POST http://localhost:8000/api/v5/kline/intraday \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["600000.SH"], "period": "1m", "count": 100}'
```

---

## 📝 统一响应格式

所有 API 响应遵循统一格式：

```json
{
  "code": 0,          // 0 表示成功，非 0 表示错误
  "data": {...},      // 响应数据
  "message": "success"  // 响应消息
}
```

**错误响应示例**：
```json
{
  "code": 404,
  "data": null,
  "message": "未找到股票 600000.SH 的数据"
}
```

---

## ⚠️ 注意事项

### 1. 数据源可用性

- **TdxQuant**: 仅交易时间可用
- **XtQuant**: 交易+盘后可用，需 QMT 连接
- **PyTdx2**: 24/7 可用
- **QLib**: 24/7 可用

### 2. 订阅限制

- **XtQuant**: 最多订阅 300 只股票
- **TdxQuant**: 最多订阅 100 只股票

### 3. 请求频率建议

- **实时行情**: 建议轮询间隔 ≥ 1 秒
- **热点扫描**: 建议间隔 ≥ 10 秒
- **批量操作**: 建议批量大小 ≤ 500 只股票

---

**文档版本**: v1.0
**更新日期**: 2026-03-20
**维护者**: MyQuant 开发团队
