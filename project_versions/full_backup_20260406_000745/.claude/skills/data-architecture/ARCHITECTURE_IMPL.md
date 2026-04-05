# V5 场景化服务架构 - 详细实现规范

> **目的**：让 AI 准确理解架构，不再看错

---

## 1. 分层架构总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        第1层：前端层                                │
│                                                                     │
│   组件（只渲染UI）           Composable（统一入口）        缓存      │
│   RealtimeQuotes.vue  ───→  useKlineData.ts  ←────→  IndexedDB     │
│   TradingViewKLine.vue       │                                   │
│                              ├─ HTTP 加载历史                     │
│                              ├─ WS 连接管理                       │
│                              ├─ IndexedDB 读写                    │
│                              └─ 状态管理                          │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        第2层：API层                                 │
│                                                                     │
│   /api/market/quotes              - 快照接口                        │
│   /api/v5/kline/realtime/{symbol} - K线历史（所有周期）            │
│   /ws/kline/{symbol}              - WebSocket（只推1分钟线）        │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        第3层：服务层（5个服务）                      │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │ 🔴 RealtimeMarketService                                    │  │
│   │    • get_realtime_quotes() - 获取快照                       │  │
│   │    • WebSocket 推送 - 只推1分钟线                           │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │ 🟢 KlineService                                             │  │
│   │    • get_historical_kline() - 统一数据入口                   │  │
│   │    • 路由：HotDB → LocalDB → 在线源                         │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │ 🟡 SeamlessKlineService                                     │  │
│   │    • get_kline() - 拼接 + 复权                              │  │
│   │    • HTTP API 调用此服务                                    │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │ ⚪ AdjustmentFactorService                                  │  │
│   │    • get_factor_table() - 获取复权因子表                    │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │ 🟠 HotDBService                                             │  │
│   │    • smart_update() - 智能缺口检测 + 自动补全               │  │
│   │    • 通过 KlineService 补全（不直接调在线源）                │  │
│   └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        第4层：适配器层（5个适配器）                  │
│                                                                     │
│   【本地存储适配器】              【在线数据源适配器】              │
│   • hotdb_adapter               • tdxquant_adapter（交易时间）      │
│   • localdb_adapter             • xtquant_adapter（交易+盘后）      │
│                                 • pytdx_adapter  （24/7）           │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        第5层：数据源                                │
│                                                                     │
│   HotDB    - 热数据库（最近数据，硬盘）                             │
│   LocalDB  - 冷数据库（历史数据，QLib格式）                         │
│   Online   - 在线数据源（通达信/迅投服务器）                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 数据流向（必须遵守）

### 2.1 HTTP 请求流

```
前端组件
    │
    ▼
useKlineData.ts（Composable）
    │
    ▼
fetchKline() ─────────────────────────────────────────┐
    │                                                 │
    ▼                                                 │
HTTP /api/v5/kline/realtime/{symbol}?period=5m       │
    │                                                 │
    ▼                                                 │
SeamlessKlineService.get_kline()                     │
    │                                                 │
    ├──────────────────┬──────────────────┐           │
    ▼                  ▼                  ▼           │
KlineService     AdjustmentFactorService  拼接        │
    │                                                 │
    ├──────┬──────┬──────┐                            │
    ▼      ▼      ▼      ▼                            │
hotdb  localdb tdxquant pytdx                         │
    │                                                 │
    ▼                                                 │
返回数据（UTC秒级时间戳）─────────────────────────────┘
```

### 2.2 WebSocket 数据流

```
前端 useKlineData.ts
    │
    ▼
WebSocket /ws/kline/{symbol}
    │
    ▼
RealtimeMarketService
    │
    ▼
只推送 1 分钟线
    │
    ▼
前端更新最后一根 K 线
```

---

## 3. 服务职责详解

### 3.1 KlineService（统一数据入口）

**文件**：`backend/src/myquant/core/market/services/kline_service.py`

**职责**：
- 所有数据获取的统一入口
- 路由选择：HotDB → LocalDB → 在线源
- **不被其他服务直接调用适配器**

**接口**：
```python
def get_historical_kline(symbol, period, count, start_date, end_date) -> DataFrame:
    """
    统一数据入口
    
    路由优先级：
    1. HotDB（快速通道）
    2. LocalDB（冷数据）
    3. 在线源（tdxquant → pytdx → xtquant）
    """
```

### 3.2 SeamlessKlineService（拼接服务）

**文件**：`backend/src/myquant/core/market/services/seamless_service.py`

**职责**：
- HTTP API 的入口服务
- 历史数据拼接
- 调用 AdjustmentFactorService 复权
- **调用 KlineService 获取数据，不直接调适配器**

**接口**：
```python
def get_kline(symbol, period, count, adjust_type) -> DataFrame:
    """
    拼接 + 复权
    
    调用链：
    1. KlineService.get_historical_kline() 获取原始数据
    2. AdjustmentFactorService.get_factor_table() 获取复权因子
    3. 应用复权
    """
```

### 3.3 HotDBService（智能补全服务）

**文件**：`backend/src/myquant/core/market/services/hotdb_service.py`

**职责**：
- 检测数据缺口
- 检查数据新鲜度
- 自动补全缺失数据
- **通过 KlineService 补全，不直接调在线源**

**接口**：
```python
def smart_update(symbol, period) -> dict:
    """
    智能补全流程：
    1. _detect_gap() - 检测缺口
    2. _is_data_fresh() - 检查新鲜度
    3. 有缺口/过期 → KlineService.get_historical_kline() 补全
    4. 写入 hotdb_adapter
    """
```

### 3.4 RealtimeMarketService（实时行情）

**文件**：`backend/src/myquant/core/market/services/realtime_service.py`

**职责**：
- 获取实时快照
- WebSocket 推送（只推 1 分钟线）

### 3.5 AdjustmentFactorService（复权服务）

**文件**：`backend/src/myquant/core/market/services/adjustment_factor_service.py`

**职责**：
- 获取复权因子表
- 缓存因子（两级缓存）

### 3.6 XdxrService（除权数据服务）

**文件**：`backend/src/myquant/core/market/services/xdxr_service.py`

**职责**：
- 统一管理除权除息数据获取
- 两级缓存：内存（L1）+ 文件（L2）
- 通过 `get_adapter()` 获取适配器

**状态**：未使用（2026-04-04）- 短期策略不需要复权

**调用链**：
```
AdjustmentFactorService
    → XdxrService.get_xdxr_data()
        → get_adapter('pytdx').get_xdxr_info()
```

---

## 4. 适配器职责

### 4.1 本地适配器

| 适配器 | 文件 | 说明 |
|--------|------|------|
| hotdb_adapter | `adapters/hotdb_adapter.py` | 热数据（自选股最新数据，qlib格式） |
| localdb_adapter | `adapters/localdb_adapter.py` | 冷数据（通达信历史数据） |
| tdxlocal_adapter | `adapters/tdxlocal_adapter.py` | 通达信本地数据 |

### 4.2 在线适配器

| 适配器 | 文件 | 可用时间 |
|--------|------|----------|
| pytdx_pool_adapter | `adapters/pytdx_pool_adapter.py` | 24/7（连接池版，默认） |
| xtquant_adapter | `adapters/xtquant_adapter.py` | 交易+盘后 |
| tdxquant_adapter | `adapters/tdxquant_adapter.py` | 交易时间 |

---

## 5. 禁止行为（违规检测）

### ❌ 禁止跳层调用

```python
# ❌ 错误：API层直接调适配器
from myquant.core.market.adapters import get_adapter
adapter = get_adapter('hotdb')

# ✅ 正确：API层调服务层
from myquant.core.market.services import get_seamless_kline_service
service = get_seamless_kline_service()
```

### ❌ 禁止服务直接访问适配器内部

```python
# ❌ 错误：直接访问适配器内部属性
tdxquant = get_adapter('tdxquant')
xdxr_data = tdxquant._tq.get_xdxr_info([symbol])

# ✅ 正确：通过 XdxrService 获取
from myquant.core.market.services.xdxr_service import get_xdxr_service
xdxr_service = get_xdxr_service()
xdxr_data = xdxr_service.get_xdxr_data(symbol)
```

### ❌ 禁止循环依赖

```python
# ❌ 错误：A → B → A 循环导入
# AdjustmentFactorService → SeamlessKlineService → AdjustmentFactorService

# ✅ 正确：单向依赖链
# SeamlessKlineService → AdjustmentFactorService → XdxrService → get_adapter
```

### ❌ 禁止前端直接调 API

```typescript
// ❌ 错误：组件直接调 fetchKline
import { fetchKline } from '@/api/modules/quotes'
const data = await fetchKline(...)

// ✅ 正确：组件用 Composable
import { useKlineData } from '@/composables/useKlineData'
const { bars, loadHistory } = useKlineData(symbol, timeframe)
```

---

## 6. 文件位置速查

### 服务层
```
backend/src/myquant/core/market/services/
├── kline_service.py           # KlineService
├── seamless_service.py        # SeamlessKlineService
├── hotdb_service.py           # HotDBService（需创建）
├── realtime_service.py        # RealtimeMarketService
├── adjustment_factor_service.py  # AdjustmentFactorService
```

### 适配器层
```
backend/src/myquant/core/market/adapters/
├── hotdb_adapter.py           # HotDB适配器（需创建）
├── localdb_adapter.py         # LocalDB适配器
├── tdxquant_adapter.py        # 通达信量化
├── xtquant_adapter.py         # 迅投QMT
├── pytdx_adapter.py           # 通达信服务器
```

### 前端
```
frontend/src/
├── composables/
│   └── useKlineData.ts        # Composable 统一入口
├── services/
│   └── idbKline.ts            # IndexedDB 缓存
├── views/market/
│   └── RealtimeQuotes.vue    # 只渲染UI，用 useKlineData
```

---

## 7. 检查清单

每次修改架构相关代码前，确认：

- [ ] 已阅读本文档
- [ ] 确认调用链：`API → Service → Adapter → 数据源`
- [ ] 没有跳层调用
- [ ] 前端用 `useKlineData`，不直接调 `fetchKline`
- [ ] 服务通过 `get_adapter()` 获取适配器，不直接 import
