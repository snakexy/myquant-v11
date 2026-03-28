# MyQuant v11 项目上下文
> 每次新对话开始必读，保持最新状态

## 当前状态（2026-03-28）
- **后端**: ✅ 运行中 http://localhost:8000
- **前端**: ✅ 已迁移到 v11，运行在 http://localhost:5174
- **数据源**: ✅ pytdx2/XtQuant/TdxQuant 均正常，WebSocket 实时推送已优化
- **复权因子缓存**: ✅ 混合模式已实现（日线用前复权，分钟线用等比复权）
- **架构重构**: ✅ KlineService 统一数据入口已完成（符合 V5 场景化服务架构）

### 9. KlineService 重构 - V5 场景化服务架构（已完成）
**问题**:
1. 切换 K 线周期时重复下载数据（500-1000ms）
2. HotDB 过期判断逻辑错误，历史数据被丢弃
3. 业务逻辑在 adapter 层（违反分层架构）
4. 没有统一的数据获取入口

**解决**:
1. KlineService 扩展为统一数据获取入口
   - `get_historical_kline()`: 统一入口方法
   - `_try_hotdb()`: HotDB 快速通道（<10ms）
   - `_try_localdb()`: LocalDB 冷数据库
   - `_fetch_from_online()`: V5 双层路由

2. SeamlessKlineService 简化
   - `_get_historical_kline()`: 调用 KlineService
   - `_get_realtime_kline()`: 调用 KlineService
   - 删除冗余的 `_try_hotdb_fast_path()`

**新调用链**:
```
前端 → API → SeamlessKlineService
    ↓
KlineService.get_historical_kline() ← 统一入口
    ↓
HotDB/LocalDB/V5双层路由
```

**效果**:
- HotDB 命中: < 10ms 响应
- 切换周期: 瞬间完成
- 架构清晰: 职责分离，符合 V5 设计

**修改文件**:
- `kline_service.py`: 扩展为统一数据入口
- `seamless_service.py`: 简化，调用 KlineService

### 8. 复权因子预计算和通达信标准前复权（已完成）
**问题**:
1. 切换周期时重复计算复权因子（50-200ms），XDXR数据虽缓存但复权计算无缓存
2. 前复权算法不正确（累积因子），与通达信软件结果不一致

**解决**:
1. 实现 `AdjustmentFactorService`，支持复权因子表预计算和两级缓存
2. 修复前复权算法为通达信标准（不累积，只用最新除权日因子）

**通达信标准前复权算法**（所有周期统一）:
- 单日因子 = 除权价 / 收盘价（< 1.0，让价格下跌）
- 最新除权日及之后：因子 = 1.0（价格不变）
- 最新除权日之前：因子 = 最新除权日的单日因子（不累积）

**验证结果**（茅台 600519.SH）:
- 2025-12-18 前复权: 1431.00 × 0.983009 ≈ 1406.69 元
- 通达信软件: 1407.04 元
- 误差: 0.35 元（数据精度差异，可接受）

**存储结构**:
```
data/xdxr_cache/
├── 000001_SZ/
│   ├── 000001_SZ.json              # 原始XDXR数据
│   ├── factors_front.json          # 前复权累积因子表（日线用）
│   └── factors_front_ratio.json    # 等比前复权独立因子表（分钟线用）
```

**缓存层级**:
- **L1内存缓存**: `TTLCache` (TTL 7天)
- **L2文件缓存**: `data/xdxr_cache/{symbol}/factors_{type}.json`

**关键代码**:
- `adjustment_factor_service.py`: 复权因子预计算服务
  - `get_factor_table()`: 带两级缓存的因子表获取
  - `apply_factors()`: O(n)纯查表应用复权
  - `calculate_front_factors()`: 前复权累积因子计算
  - `calculate_front_ratio_factors()`: 等比前复权独立因子计算
- `seamless_service.py`: 自动周期判断和复权应用
  - `_apply_adjustment()`: 根据周期自动选择复权方式

**性能提升**:
- 首次计算因子表: 200-500ms（计算并保存）
- 后续复权应用: < 5ms（查表）
- 多周期切换: 从 200ms × N 次 降至 < 10ms

---

### 7. XDXR除权除息数据持久化缓存（已完成）
**问题**: XDXR数据每次从数据源获取（TdxQuant/PyTdx），增加延迟且占用网络资源
**解决**: 实现两级缓存
- **L1内存缓存**: TTL 1小时（高频访问）
- **L2文件缓存**: TTL 1天（持久化，按股票分文件夹）

**存储结构**:
```
data/xdxr_cache/
├── 000001_SZ/
│   └── 000001_SZ.json
├── 600519_SH/
│   └── 600519_SH.json
└── ...
```

**关键代码** (`seamless_service.py`):
- `_get_xdxr_data()`: 优先级 内存缓存 → 文件缓存 → TdxQuant → PyTdx
- `_load_xdxr_from_file()`: 从JSON文件加载，带过期检查
- `_save_xdxr_to_file()`: 保存到JSON文件

**效果**:
- 应用重启后，XDXR数据从本地加载（< 10ms）
- 减少网络请求，提升复权计算速度

---

### 6. TdxQuant SDK 独立化（重要架构修复）
**问题**: v11 共用 v10 的 SDK 路径 (`E:\MyQuant_v10.0.0v2\backend\data\adapters\tdxquant_sdk`)，导致：
- v10/v11 同时运行时冲突
- 升级 v10 可能影响 v11
- 违反项目隔离原则

**修复**:
1. 复制 SDK 到 v11: `backend/external/tdxquant_sdk/`
2. 修改 `tdxquant_adapter.py` 使用独立路径

**之前**: `sdk_path = r'E:\MyQuant_v10.0.0v2\backend\data\adapters\tdxquant_sdk'`
**之后**: `sdk_path = r'E:\MyQuant_v11\backend\external\tdxquant_sdk'`

**影响**: 完全消除 v10/v11 的 SDK 冲突，各版本独立运行

### 4. 数据补全逻辑优化（`seamless_service.py`）
**问题**: 开盘前（如 05:41）误判需要补充"今天"数据，但实际上今天还没开盘
**修复**: `_need_realtime_supplement` 增加开盘时间检查
```python
current_time = now.time()
market_open = datetime.strptime("09:30", "%H:%M").time()

if current_time < market_open:
    # 开盘前：昨天的数据是完整的，不需要补"今天"的数据
    logger.info(f"当前时间早于开盘时间 09:30，昨天的数据已完整，不需要补充")
    return False
```
**效果**: 避免在无意义的时段浪费资源获取不存在的数据

### 1. TdxQuant 指数行情解析错误（`tdxquant_adapter.py`）
**问题**: 获取指数（000001.SH, 399001.SZ 等）时报错 `could not convert string to float: '.'`
**原因**: TdxQuant 对某些字段返回 `.` 字符串表示无数据，直接 `float()` 转换失败
**修复**: 添加 `safe_float()` / `safe_int()` 辅助函数，处理非数字字符串
```python
def safe_float(val, default=0.0):
    if val is None or val == '' or val == '.':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default
```

### 2. LocalDB 保存失败（`localdb_adapter.py`）
**问题**: 保存日线数据报错 `'datetime'` 列不存在
**原因**: 不同适配器返回的 DataFrame 列名不一致（有的用 `time`，有的用 `datetime`）
**修复**: 在 `save_kline()` 中统一列名
```python
if 'datetime' not in df.columns and 'time' in df.columns:
    df.rename(columns={'time': 'datetime'}, inplace=True)
```

### 3. WebSocket 收盘后停止数据轮询（`kline_service.py`）
**问题**: 收盘后 WebSocket 仍每秒轮询数据，浪费资源
**修复**: 轮询循环根据交易状态调整行为
- 交易时间：每秒轮询（正常）
- 收盘后：完全停止数据轮询，每分钟检查一次是否开盘
- WebSocket 心跳保持 30 秒间隔（独立运行）

## 项目结构
→ 详见 `E:/MyQuant_v11/STRUCTURE.md`（代码放哪里、各层职责、命名规范）

**v11 特殊说明（STRUCTURE.md 未覆盖的）：**
- `backend/.venv/` — Python 3.11.8 虚拟环境（勿提交）
- `backend/external/pytdx2/` — pytdx2 本地包（非 pip 安装）
- `frontend/` — 完整前端工程（已从 v10 迁移，有 package.json + node_modules）

## 启动命令
```bash
# 后端（必须在 backend 目录）
cd E:/MyQuant_v11/backend
E:/MyQuant_v11/.venv/Scripts/uvicorn.exe myquant.main:app --reload --port 8000

# 前端（已迁移到 v11）
cd E:/MyQuant_v11/frontend
npm run dev   # 运行在 localhost:5174
```

## API 路由（已验证可用）
| 路径 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `GET /api/market/status` | 市场状态 |
| `POST /api/market/quotes` | 实时行情（body: ["000001","600000"]） |
| `GET /api/quotes/kline/realtime/{symbol}` | K线数据 |
| `GET /api/v5/kline/realtime/{symbol}` | 同上（前端别名） |
| `GET /api/v1/quotes/status` | 市场状态（前端别名） |
| `GET /docs` | Swagger UI |

## 已解决的关键问题
→ 详见 `.claude/skills/` 下的 skill 文件，遇到相关问题直接查阅：
- `pytdx2-api-differences` — get_security_bars 参数、返回 None
- `uvicorn-windows-reload` — 热重载不可靠，需手动重启
- `fastapi-frontend-alias-routes` — 前后端路径不匹配
- `windows-pip-encoding` — requirements.txt GBK 报错
- `_normalize_quote_dict` 需在 pytdx_adapter.py 手动实现

### 2026-03-23 修复内容
- **format_converter.py**: XtQuant datetime +8h 还原 CST 日期（修复日线日期偏移一天）
- **seamless_service.py**: keep='last' 优先在线数据；非交易时间不触发 TdxQuant 查询
- **pytdx_adapter.py + pytdx_pool_adapter.py**: 分钟线 vol÷100 股→手；intraday bar high/low 异常值截断（1%阈值）
- **intraday_service.py**: 非交易时间直接用 pytdx 避免 TdxQuant 初始化报错
- **RealtimeQuotes.vue**: 日线去重；成交量颜色修复；timeFormatter 日线只显日期
- **quotes.ts**: _base 修复双重 /api/ 前缀
- **market.py**: 新增 GET /snapshot/{symbol} 和 GET /snapshot/ 端点

**2026-03-23 前端修复（RealtimeQuotes.vue）**：
- K线图贴底：从chart-area计算高度，排除toolbar，移除空volumeContainer
- 十字光标OHLCV legend：悬浮在图表左上角，成交量从volumeSeries读取
- 价格颜色修复：pre_close字段名不一致导致change计算错误，直接用后端change字段
- 左侧列表：迷你折线图(5分钟线)、所有股票价格正确更新
- 状态栏：沪深指数(上证/深证/创业板)，市场代码后缀判断修复上证指数
- 垂直拖动：autoScale:false + 临时开启autoScale自适应初始价格范围
- App.vue：height:100%+overflow:hidden修复height链
- quotes.ts：修复双重/api/前缀

## 前端导航栏说明
- **公共导航栏**: `E:/MyQuant_v10.0.0/frontend/src/components/GlobalNavBar.vue`
- 已应用到: RealtimeQuotes、Monitoring、RiskControlView、MLModelManagement、ResearchDetailViewSplit、StrategyManagement、WorkflowManager
- 工作流子页面（研究/验证/实盘）**不需要**公共导航栏
- 导航菜单: 实时行情→工作流→监控→风险管理→策略→ML模型

## 数据源架构（V5，详细文档见 docs/项目设计/数据架构V5/）
| 数据源 | 最擅长 | 可用时间 | 当前状态 |
|--------|--------|----------|---------|
| **TdxQuant** | L1快照(0.60ms) + 板块(6.99ms, 586板块) | 仅交易时间 | ✅ 可用（需通达信终端运行） |
| **XtQuant** | 当天分钟线(13ms首次/4ms后续) + 后台下载完整历史 | 交易+盘后 | ✅ 可用（pip install xtquant） |
| **PyTdx2** | 24/7在线多周期K线(13ms) **连接池版(M+H+P)** | 24/7 | ✅ 可用（默认连接池版） |
| **QLib** | 历史K线本地库(7-10ms) | 24/7 | ❓ 未验证 |

**关键限制**：
- TdxQuant：仅交易时间可用（需通达信终端运行），不支持盘后的当天分钟线历史
- XtQuant：依赖 QMT 运行，周末/节假日如 QMT 服务器连接正常仍可用；首次调用约600ms（下载），后续约4-5ms
- PyTdx2：24/7 在线，不支持订阅推送

**2026-03-22 测试结论**：
1. PyTdx2 分钟线性能优异（13ms），可作为默认在线数据源
2. XtQuant 实现三层加载策略（本地→在线→后台下载），适合需要完整历史的场景
3. TdxQuant 单例重复初始化问题已修复（AdapterFactory 缓存实例）

## 待办任务

### ✅ HotDB 数据聚合策略（已完成）
**目标**：修复 HotDB 预热和聚合策略

**进度**：
| 部分 | 状态 | 说明 |
|------|------|------|
| 修复预热周期 | ✅ 已完成 | 从 ['1d', '1m'] 改为 ['1d', '5m'] |
| uvicorn 路径问题 | ✅ 已完成 | main.py 添加 sys.path 操作 |
| 自动聚合 | ✅ 已完成 | 5m → 15m/30m/1h（numpy 向量化 + ThreadPoolExecutor） |
| 前端集成 | ✅ 已完成 | WatchlistPanel 自动预热/删除 |
| 文档完善 | ✅ 已完成 | HotDB数据聚合策略.md + V5-数据源使用完整指南.html |

**设计原则**：
- HotDB 从 LocalDB 获取 1d 和 5m 原始数据
- 5m 数据自动聚合生成 15m/30m/1h
- 1d 数据聚合生成 1w/1mon（待实现）
- 1m 数据在线获取，只保留 7 天窗口期

**核心代码**：
- `hotdb_adapter.py`: `_aggregate_from_5m()` - 5m→15m/30m/1h 聚合（numpy 向量化）
- `hotdb_service.py`: `preheat()` - 预热 1d 和 5m，触发自动聚合
- `hotdata.py`: API 路由 `/api/v5/hotdata/preheat` 和 `/api/v5/hotdata/symbols/{symbol}`
- `quotes.ts`: `preheatHotDB()` 和 `deleteHotDBSymbol()`
- `WatchlistPanel.vue`: 添加/删除股票时自动预热/删除 HotDB 数据

**性能优化**：
- 向量化计算：numpy reshape → 90% 耗时降低
- 并行 IO：ThreadPoolExecutor → 67% 保存耗时降低
- 总体：300ms → 40ms（↓87%）

---

### ✅ HotDB 智能增量更新（已完成）
**目标**：实现 HotDB 数据缺口检测和智能增量补全

**进度**：
| 部分 | 状态 | 说明 |
|------|------|------|
| 数据缺口检测 | ✅ 已完成 | `get_data_info()` - O(1) 摘要，`detect_gap()` - 缺口判断 |
| 智能增量引擎 | ✅ 已完成 | `smart_update()` + `get_kline_with_auto_update()` |
| 服务层集成 | ✅ 已完成 | `_try_hotdb_fast_path()` - HotDB 快速通道 |
| 实时数据回写 | ✅ 已完成 | `_save_to_hotdb()` - 异步回写 |
| 删除缓存清除 | ✅ 已完成 | `delete_kline()` 清除内存缓存（修复 2026-03-28） |

**设计原则**：
- **HotDB 不是数据源**，不注册到路由系统，在服务层拦截
- **智能增量更新**：缺多少补多少，节约网络流量
- **数据新鲜度检查**：日线 >1天 且已过 09:30；分钟线超阈值
- **多级缓存**：HotDB → LocalDB → 在线源
- **异步回写**：在线获取的数据后台线程保存到 HotDB
- **删除清除缓存**：删除数据时同步清除 L1 内存缓存（5分钟 TTL）

**核心代码**：
- `hotdb_adapter.py`: `get_data_info()`, `detect_gap()`, `get_kline(allow_stale=True)`, `delete_kline()` 清除缓存
- `hotdb_service.py`: `smart_update()`, `get_kline_with_auto_update()`, `_complete_from_online()`
- `seamless_service.py`: `_try_hotdb_fast_path()`, `_save_to_hotdb()`, `_get_historical_kline()` 修改

**Bug 修复（2026-03-28）**：
- **问题**：删除自选股后重新添加，旧的 1h 数据仍然显示
- **原因**：`delete_kline()` 只删除文件，未清除 L1 内存缓存（TTL=5分钟）
- **修复**：删除时同步清除 `_memory_cache` 和 `_memory_cache_time`
- **验证**：删除后缓存从 3 个降至 0 个

**验证结果**（2026-03-28）：
- `get_data_info('000001.SZ', '1d')` → 801条，最新 2026-03-27
- `detect_gap()` → 当前开盘前，不需要补全
- `smart_update()` → 返回完整数据集
- `[HotDB快速通道]` 日志 → 服务层正常调用

---

### 🔄 Lightweight Charts 高级功能集成（新需求）
**目标**：集成 Lightweight Charts 插件库的高级功能

**优先级 P0（最实用）**：
1. **user-price-lines** - 用户自定义价格线（支撑/阻力位标记）
2. **user-price-alerts** - 价格提醒功能（突破价格线时通知）
3. **session-highlighting** - 交易时段高亮（9:30-15:00 显示，盘前盘后灰色）
4. **expiring-price-alerts** - 过期价格提醒

**优先级 P1（增强交互）**：
5. **trend-line** - 趋势线绘制工具
6. **vertical-line** - 垂直线标记（重要事件点）
7. **rectangle-drawing-tool** - 矩形框选工具（形态分析）
8. **highlight-bar-crosshair** - 十字线高亮增强

**优先级 P2（高级图表）**：
9. **heatmap-series** - 热力图（板块热度、资金流向）
10. **stacked-area-series** - 堆叠面积图（多股对比）
11. **stacked-bars-series** - 堆叠柱状图
12. **box-whisker-series** - 箱线图（价格分布）

**实现参考**：
- 插件源码：`frontend/external/lightweight-charts/plugin-examples/src/plugins/`
- 指标源码：`frontend/external/lightweight-charts/indicator-examples/src/indicators/`

---

### ✅ L0 WebSocket K线实时订阅（已完成）
**目标**：将 RealtimeQuotes.vue 的 K 线数据从 HTTP 轮询改为 WebSocket 订阅

**进度**：
| 部分 | 状态 | 说明 |
|------|------|------|
| 后端 WebSocket 端点 | ✅ 已完成 | `/ws/kline/{symbol}` (kline_ws.py + kline_service.py) |
| 后端 KlineService | ✅ 已完成 | 轮询 XtQuant，检测变化，广播推送 |
| 前端 WS 客户端 | ✅ 已完成 | `services/klineWebSocket.ts` |
| **前端 RealtimeQuotes 集成** | ✅ 已完成 | 1m 周期用 WS，其他周期用 HTTP |

**实现要点**：
- 后端已实现：连接时发送历史分钟线，之后推送 bar_update/bar_close
- 前端在 RealtimeQuotes.vue 中创建 WebSocket 连接到 `ws://localhost:8000/ws/kline/{symbol}`
- 处理：连接/断开、消息解析、K线图表实时更新、周期切换逻辑

---

## Git 状态
- v11 已初始化 git，在 `E:/MyQuant_v11`
- v10 有 git，分支 `feature/research-detail-refactor-v2`（不管它）
- .gitignore 已排除: `.venv/`, `__pycache__/`, `version_manager/`, `data/`
