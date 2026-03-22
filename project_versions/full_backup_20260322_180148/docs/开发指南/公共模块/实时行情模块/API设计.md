# 实时行情模块 - API设计

> **阶段**: 公共模块
> **版本**: v1.0
> **最后更新**: 2026-03-21
> **状态**: ⏳ 规划中

---

## 📡 API端点列表 (7个)

### 1. 获取K线数据

```
GET /api/v1/quotes/kline/{symbol}
```

**功能**: 获取单只股票的 K 线数据

**参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| symbol | path | 是 | - | 股票代码，如 `600000.SH` |
| period | query | 否 | `1d` | 周期：1m, 5m, 15m, 30m, 1h, 1d, 1w |
| count | query | 否 | 100 | K线根数，范围 1-1000 |

**数据源优先级**: LocalDB → XtQuant → PyTdx

**响应**:
```json
{
  "code": 0,
  "data": {
    "symbol": "600000.SH",
    "period": "1d",
    "data": [
      {
        "time": 1710950400000,
        "open": 7.50,
        "high": 7.80,
        "low": 7.40,
        "close": 7.65,
        "volume": 1500000,
        "amount": 11500000,
        "color": "#ef5350"
      }
    ],
    "data_source": "LocalDB",
    "count": 100
  },
  "message": "success"
}
```

**特殊处理**:
- 日 K 线（1d）自动填充周末/节假日空白（使用前一日收盘价）
- 中国股市配色：红涨 `#ef5350`、绿跌 `#26a69a`
- 时间戳为 UTC 毫秒（前端 lightweight-charts 要求）

---

### 2. 获取实时快照（批量）

```
GET /api/v1/quotes/snapshot?symbols=600000.SH,000001.SZ
```

**功能**: 批量获取股票实时行情

**参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| symbols | query | 是 | 逗号分隔的股票代码列表 |

**数据源优先级**: TdxQuant → XtQuant → PyTdx

**响应**:
```json
{
  "code": 0,
  "data": {
    "data": [
      {
        "symbol": "600000.SH",
        "name": "浦发银行",
        "price": 7.65,
        "change": 0.15,
        "change_percent": 2.0,
        "volume": 1500000,
        "amount": 11500000,
        "high": 7.80,
        "low": 7.40,
        "open": 7.50,
        "prev_close": 7.50,
        "timestamp": 1710950400000,
        "bid1": 7.64, "bid_vol1": 100,
        "ask1": 7.65, "ask_vol1": 200,
        "bid2": 7.63, "bid_vol2": 150,
        "ask2": 7.66, "ask_vol2": 180,
        "bid3": 7.62, "bid_vol3": 200,
        "ask3": 7.67, "ask_vol3": 160,
        "bid4": 7.61, "bid_vol4": 250,
        "ask4": 7.68, "ask_vol4": 140,
        "bid5": 7.60, "bid_vol5": 300,
        "ask5": 7.69, "ask_vol5": 120
      }
    ],
    "data_source": "TdxQuant",
    "count": 1,
    "timestamp": 1710950400000
  },
  "message": "success"
}
```

---

### 3. 获取实时快照（单只）

```
GET /api/v1/quotes/snapshot/{symbol}
```

**功能**: 获取单只股票实时行情

**参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| symbol | path | 是 | 股票代码 |

**响应**: 同上，但 `data` 直接是单个 QuoteSnapshot 对象（非数组）

---

### 4. K线健康检查

```
GET /api/v1/quotes/kline/health
```

**响应**:
```json
{
  "status": "healthy",
  "active_sources": 2,
  "data_sources": [
    {"name": "LocalDB", "status": "active", "description": "LocalDB数据源"},
    {"name": "XtQuant", "status": "active", "description": "XtQuant数据源"},
    {"name": "PyTdx", "status": "inactive", "description": "PyTdx数据源"}
  ]
}
```

---

### 5. 快照健康检查

```
GET /api/v1/quotes/snapshot/health
```

**响应格式**: 同上

---

### 6. 获取可用数据源

```
GET /api/v1/quotes/kline/data-sources
```

**响应**:
```json
{
  "data_sources": [
    {"name": "LocalDB", "status": "active", "description": "LocalDB数据源"},
    {"name": "XtQuant", "status": "active", "description": "XtQuant数据源"},
    {"name": "PyTdx", "status": "inactive", "description": "PyTdx数据源"}
  ]
}
```

---

### 7. 获取市场状态

```
GET /api/v1/quotes/market/status
```

**功能**: 获取当前市场交易状态，前端根据此状态动态调整刷新频率和 UI 显示

**响应**:
```json
{
  "code": 0,
  "data": {
    "is_open": true,
    "phase": "MORNING_ACTIVE",
    "phase_description": "上午活跃 (10:00-11:30)",
    "market": "A股",
    "date": "2026-03-21",
    "time": "10:30:15",
    "status": "交易中",
    "is_weekend": false,
    "refresh_interval": 5,
    "cache_ttl": 300
  },
  "message": "success"
}
```

**时段定义（TimePhase）**:

| 时段 | 值 | 时间范围 | 数据源策略 | 刷新间隔 |
|------|-----|---------|-----------|---------|
| 开盘前 | `PRE_MARKET` | 0:00-9:15 | PyTdx | 30s |
| 集合竞价 | `CALL_AUCTION` | 9:15-9:25 | TdxQuant/XtQuant | 3s |
| 等待开盘 | `WAIT_FOR_OPEN` | 9:25-9:30 | TdxQuant/XtQuant | 3s |
| 上午开盘 | `MORNING_OPENING` | 9:30-10:00 | TdxQuant → XtQuant | 3s |
| 上午活跃 | `MORNING_ACTIVE` | 10:00-11:30 | TdxQuant → XtQuant | 5s |
| 午休 | `LUNCH_BREAK` | 11:30-13:00 | PyTdx | 30s |
| 下午开盘 | `AFTERNOON_OPENING` | 13:00-14:00 | TdxQuant → XtQuant | 3s |
| 下午平稳 | `AFTERNOON_STABLE` | 14:00-15:00 | TdxQuant → XtQuant | 5s |
| 收盘后 | `AFTER_MARKET` | 15:00-24:00 | PyTdx | 30s |
| 周末 | `WEEKEND` | 全天 | PyTdx | 30s |

**关键逻辑**:
- 交易时间（9:15-15:00 工作日）→ 优先 TdxQuant/XtQuant（快）
- 非交易时间（收盘后、周末）→ 只能用 PyTdx（24/7 在线）
- `refresh_interval` 返回给前端，前端据此动态调整轮询频率

---

## 🏗️ 数据源选择逻辑

### K 线数据源选择

```
请求 K 线
    │
    ├── 日线 (1d, 1w)
    │   └── LocalDB(7-10ms) → XtQuant → PyTdx
    │
    └── 分钟线 (1m, 5m, 15m, 30m, 1h)
        ├── 交易时间
        │   └── XtQuant(0.90ms) → PyTdx
        └── 非交易时间
            └── PyTdx(10-19ms)  ← 唯一可用
```

### 快照数据源选择

```
请求快照
    │
    ├── 交易时间
    │   └── TdxQuant(0.60ms) → XtQuant → PyTdx
    └── 非交易时间
        └── PyTdx(10-19ms)  ← 唯一可用
```

### 关键限制

| 数据源 | 限制 | 影响 |
|--------|------|------|
| TdxQuant | ❌ 不支持当日分钟线 | 分钟K线必须用 XtQuant/PyTdx |
| TdxQuant | ❌ 仅交易时间可用 | 盘后只能用 PyTdx |
| XtQuant | ❌ 不支持板块数据 | 板块业务用 TdxQuant/PyTdx |
| PyTdx | ⚠️ 响应较慢（10-19ms） | 交易时间优先用其他源 |

---

## ⚠️ 错误码

| HTTP 状态码 | 场景 | 说明 |
|------------|------|------|
| 200 | 成功 | 正常返回数据 |
| 400 | 参数错误 | 股票代码为空、周期不合法 |
| 404 | 未找到 | 股票代码不存在 |
| 500 | 服务器错误 | 异常抛出 |
| 503 | 服务不可用 | 所有数据源均失败 |

**统一响应格式**:
```json
{
  "code": 0,
  "data": { ... },
  "message": "success"
}
```

---

## 📦 代码位置

| 文件 | 说明 | 状态 |
|------|------|------|
| `backend/api/v1/quotes/kline.py` | K线 API 路由 | ✅ 已有，待重构 |
| `backend/api/v1/quotes/snapshot.py` | 快照 API 路由 | ✅ 已有，待重构 |
| `backend/api/v1/quotes/__init__.py` | 路由注册 | ✅ 已有 |
| `backend/data_providers/services/realtime_market/service.py` | 场景服务 | ⚠️ 未接入 |
| `backend/data_providers/services/realtime_market/cache.py` | 三级缓存 | ⚠️ 未接入 |

---

## 📝 待清理的 V4 代码

以下代码使用了 `unified_data_manager`（V4 架构），违反项目红线，需移除：

| 文件 | 问题行 | V4 导入 |
|------|--------|---------|
| `backend/api/v1/market/routers.py` | L42, L82, L949, L1495 | `from data.unified_data_manager import ...` |

**处理方式**: 评估哪些端点有功能价值，有价值的迁移到 V5 适配器，无价值的直接删除。

---

## 📚 相关文档

- [概述](./概述.md)
- [数据模型](./数据模型.md)
- [前端组件](./前端组件.md)
- [实施计划](./实施计划.md)
- [V5 数据源使用指南](../../项目设计/最新数据架构V5/V5-数据源使用完整指南.html)

---

**创建时间**: 2026-03-21
**最后更新**: 2026-03-21
**状态**: ⏳ 规划中
