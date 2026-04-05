# QuoteService 重构设计

## 背景

### 问题
`RealtimeService` 不在 V5 场景化服务架构中，导致：
1. 职责不清晰（快照 + K线混合）
2. 与 KlineService 有重叠
3. 架构文档缺失，维护困难
4. 内存泄漏问题（前端每 5 秒调用）

### 当前状态
- 文件：`backend/src/myquant/core/market/services/realtime_service.py`
- 职责：快照数据 + K线数据
- 调用链：前端 → API → RealtimeService → 适配器

---

## 设计方案

### 1. 服务定位

**QuoteService（快照服务）** - V5 场景化服务之一

| 服务 | 职责 | 数据类型 | 调用方式 |
|------|------|----------|----------|
| **QuoteService** | 实时快照行情 | 最新价格、涨跌幅、五档盘口 | HTTP API |
| **KlineService** | K线数据 + WebSocket推送 | 时间序列OHLCV | WebSocket + HTTP |

### 2. V5 场景化服务架构

```
┌─────────────────────────────────────────────────────────────┐
│                      V5 场景化服务层                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ QuoteService │  │ KlineService │  │HotDBService  │      │
│  │  快照场景    │  │   K线场景    │  │  缓存场景    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                  ↓                  ↓              │
│         └──────────────────┴──────────────────┘            │
│                            ↓                                 │
│                  ┌──────────────────┐                       │
│                  │  适配器路由层     │                       │
│                  └──────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### 3. QuoteService 职责定义

#### 核心职责
1. **快照数据获取** - 最新价格、涨跌幅、成交量
2. **市场状态判断** - 交易时间、市场阶段
3. **数据源选择** - 根据交易时间自动切换

#### 数据流
```
前端请求
   ↓
API 层 (/api/market/quotes)
   ↓
QuoteService.get_realtime_quotes()
   ↓
选择适配器 (TdxQuant → PyTdx2)
   ↓
返回快照数据 + 缓存
```

### 4. 与 KlineService 的区别

| 维度 | QuoteService | KlineService |
|------|-------------|--------------|
| **数据类型** | 快照（点数据） | K线（时间序列） |
| **返回内容** | 最新价格、涨跌幅 | OHLCV 数组 |
| **传输方式** | HTTP API | WebSocket + HTTP |
| **调用频率** | 前端控制（每5秒） | 每秒轮询（交易时间） |
| **缓存策略** | 非交易时间长缓存 | 智能增量更新 |
| **典型场景** | 自选股列表、行情面板 | K线图表、技术分析 |

### 5. 内存优化策略

#### 缓存层级
```python
class QuoteService:
    def __init__(self):
        # L1: 交易时间缓存 (10秒 TTL)
        self._trading_cache = TTLCache(maxsize=500, ttl=10)

        # L2: 非交易时间缓存 (1小时 TTL)
        self._off_hours_cache = TTLCache(maxsize=500, ttl=3600)

        # L3: 财务指标缓存 (1天 TTL，变化不频繁)
        self._financial_cache = TTLCache(maxsize=200, ttl=86400)
```

#### 数据源选择
```python
def _select_adapter(self):
    is_trading = TradingTimeChecker.is_trading_time()

    if is_trading:
        # 交易时间：TdxQuant (最快) → PyTdx2
        return ['tdxquant', 'pytdx']
    else:
        # 非交易时间：PyTdx2（稳定）
        return ['pytdx']
```

---

## 实施计划

### 阶段 1：重命名和清理（1-2小时）
1. ✅ 重命名 `RealtimeService` → `QuoteService`
2. ✅ 移除 `get_kline()` 方法（应由 KlineService 负责）
3. ✅ 更新所有引用

### 阶段 2：优化缓存机制（2-3小时）
1. ✅ 实现三级缓存（交易/非交易/财务）
2. ✅ 添加定期清理逻辑
3. ✅ 监控缓存命中率

### 阶段 3：文档更新（1小时）
1. ✅ 更新 `KlineService重构-架构链路图.html`（已有v2版本包含QuoteService）
2. ✅ 添加 QuoteService 说明
3. ✅ 更新 API 路由文档

### 阶段 4：测试验证（1小时）
1. 单元测试：缓存逻辑
2. 集成测试：前端调用
3. 性能测试：内存监控

---

## 文件变更清单

### 需要修改的文件
1. `backend/src/myquant/core/market/services/realtime_service.py` → `quote_service.py`
2. `backend/src/myquant/api/dataget/market.py` - 更新引用
3. `frontend/src/views/market/RealtimeQuotes.vue` - 无需修改（API 不变）
4. `docs/项目设计/数据架构V5/KlineService重构-架构链路图.html` - 添加 QuoteService

### 新增文件
- `docs/项目设计/数据架构V5/08-QuoteService快照服务.md`

---

## 预期效果

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 内存占用 | 4.8GB 持续增长 | 稳定在 200-500MB |
| TdxQuant 调用 | 每 5 秒 | 非交易时间几乎不调用 |
| 缓存命中率 | ~10% | ~90%（非交易时间） |
| 架构清晰度 | 职责混乱 | 职责分离 |

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 重命名导致引用断裂 | 高 | 全局搜索替换 |
| 缓存策略错误 | 中 | 灰度发布，监控 |
| 性能回退 | 低 | A/B 测试 |

---

## 相关文档
- V5 架构总览：`docs/项目设计/数据架构V5/README.md`
- KlineService 架构：`docs/项目设计/数据架构V5/KlineService重构-架构链路图.html`
- 内存优化计划：`.claude/plans/memory-optimization-plan.md`

---

**创建日期**: 2026-03-30
**状态**: ✅ 全部完成（Stage 1-4）
**优先级**: 中（影响内存和架构清晰度）
