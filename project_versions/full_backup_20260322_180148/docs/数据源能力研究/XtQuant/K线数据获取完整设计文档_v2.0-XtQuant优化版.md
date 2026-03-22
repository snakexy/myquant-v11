# K线数据获取完整设计文档 v2.0 - XtQuant优化版

> **版本**: v2.0
> **更新日期**: 2026-02-05
> **适用系统**: MyQuant v10.0.0（使用XtQuant数据源）
> **基于**: v1.0（v9.0.0）+ XtQuant能力验证结果

---

## 📊 更新概览

### v2.0 核心改进

| 改进点 | v1.0（PyTdx） | v2.0（XtQuant） | 提升 |
|--------|--------------|----------------|------|
| **分钟线加载** | 仅在线获取（限制16天） | **下载+读取（无限制）** | ✅ 突破限制 |
| **日K线加载** | 5-18ms | **下载+读取 5-10ms** | ✅ 更快 |
| **5分钟K线（1个月）** | 不支持 | **下载+读取 ~1秒** | ✅ 新增能力 |
| **预加载策略** | 后台预加载 | **启动时预下载** | ✅ 更主动 |
| **切换周期体验** | 5-18ms | **缓存读取 <10ms** | ✅ 无感切换 |

---

## 1. XtQuant数据能力总结

基于[XtQuant数据能力研究](../数据源能力研究/XtQuant/100-最终正确报告-分钟线下载能力.md)的验证结果：

### 1.1 核心发现

| 能力 | 限制 | 性能 | 实际含义 |
|------|------|------|---------|
| **在线获取（count方式）** | 最多3.8天（1083条5分钟K线） | 首次760ms，后续6-8ms | 适合实时数据 |
| **下载+读取** | **无时间限制** | 下载1个月~1秒，读取6-8ms | 适合历史数据 |
| **订阅缓存** | 单实例600只 | 0.5-1ms | 适合自选股 |

### 1.2 关键参数规范

```python
# ✅ 正确用法
xtdata.download_history_data(
    stock_code='600519.SH',
    period='5m',
    start_time='20240101',  # ⭐ 字符串格式
    end_time='20241231'      # ⭐ 字符串格式
)

# ✅ 读取已下载数据
xtdata.get_market_data_ex(
    stock_list=['600519.SH'],
    period='5m',
    start_time='20240101',  # ⭐ 字符串格式
    end_time='20241231',    # ⭐ 字符串格式
    count=0,                # ⭐ count=0表示使用时间范围
    dividend_type='none'    # ⭐ 字符串格式
)
```

---

## 2. 优化后的三层加载策略

### 2.1 完整数据流（v2.0优化）

```
┌─────────────────────────────────────────────────────────────┐
│ 第0层：应用启动预加载（新增）                                  │
│ - 目标：用户打开股票时数据已在本地                            │
│ - 数据：自选股的常用周期数据                                  │
│ - 时机：应用启动时后台执行                                    │
│ - 速度：不阻塞用户操作                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 第一层：即时显示（优化：优先使用下载）                         │
│ - 目标：0.3秒内首屏显示（v1.0是0.5秒）                        │
│ - 数据：100根K线                                             │
│ - 策略：本地读取 > 在线获取                                   │
│ - 速度：6-8ms（本地） ~ 760ms（在线）                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 第二层：智能扩展（优化：后台下载+无缝更新）                     │
│ - 目标：扩展到完整历史                                        │
│ - 数据：根据周期动态决定                                      │
│ - 策略：后台下载→自动更新图表                                  │
│ - 速度：下载1秒，更新<100ms                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 第三层：实时更新（保持）                                      │
│ - 目标：保持最新K线"活着"                                     │
│ - 数据：最新1根K线                                           │
│ - 速度：~1ms（订阅缓存）                                     │
│ - 频率：每3秒（仅交易时间）                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 两种实现方案

基于XtQuant的能力，我们提供两种实现方案，可根据实际需求选择：

### 3.1 方案对比

| 特性 | **方案A：订阅版** | **方案B：无订阅版** |
|------|-----------------|------------------|
| **核心机制** | 订阅缓存 + 极速响应 | 本地读取 + 在线获取 |
| **首次加载** | 0.5-1ms ⚡ | 760ms（首次），6-8ms（已下载） |
| **后续加载** | 0.5-1ms ⚡ | 6-8ms ✅ |
| **股票数量** | 500只+（实测） | 无限制 |
| **数据获取率** | 约72%（362/500） | 100%（按需获取） |
| **复杂度** | 需要管理订阅 | 简单直接 |
| **适用场景** | 自选股、热门股 | 全市场、冷门股 |

### 3.2 方案选择指南

**选择方案A（订阅版）如果：**
- ✅ 自选股数量 < 400只（稳定）
- ✅ 需要极致性能（0.5-1ms）
- ✅ 频繁切换同一批股票
- ✅ 自选股相对固定

**选择方案B（无订阅版）如果：**
- ✅ 需要查看全市场股票
- ✅ 自选股数量不固定
- ✅ 偶尔查看各种股票
- ✅ 简单直接，不想管理订阅

**混合方案（推荐）：**
- 自选股前100只：方案A（极速）
- 其他股票：方案B（灵活）

---

### 3.3 方案A：订阅版 - 完整设计

> **详细文档**: [方案A-订阅版-K线加载设计.md](./方案A-订阅版-K线加载设计.md)

#### 核心机制

```python
class SubscriptionManager:
    """订阅管理器"""

    def __init__(self):
        self.subscriptions = {}  # {symbol: {period: bool}}

    def add_watchlist(self, symbols: List[str]):
        """添加自选股到订阅列表"""
        for symbol in symbols:
            if symbol not in self.subscriptions:
                self.subscriptions[symbol] = {
                    '1d': True,
                    '5m': True,
                    '15m': True,
                    '30m': True,
                    '60m': True
                }
                # 执行订阅
                self._subscribe(symbol)

    def _subscribe(self, symbol: str):
        """执行订阅"""
        import xtdata

        for period in ['1d', '5m', '15m', '30m', '60m']:
            try:
                xtdata.subscribe_quote(
                    stock_code=symbol,
                    period=period,
                    count=0
                )
                logger.info(f"[订阅] {symbol} {period} 已订阅")
            except Exception as e:
                logger.error(f"[订阅] {symbol} {period} 失败: {e}")
```

#### 数据加载流程

```python
async def load_stock_with_subscription(symbol: str, period: str):
    """加载股票数据（订阅版）"""

    # 1. 检查订阅状态
    if not is_subscribed(symbol):
        subscribe_stock(symbol)
        await asyncio.sleep(0.1)  # 等待订阅生效

    # 2. 极速获取（订阅缓存，0.5-1ms）
    start = time.time()
    quote_data = xtdata.get_full_tick([symbol])
    elapsed = (time.time() - start) * 1000

    logger.info(f"[订阅缓存] 获取成功，耗时: {elapsed:.2f}ms")

    # 3. 获取完整K线
    kline_data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period=period,
        start_time='',
        end_time='',
        count=500,
        dividend_type='none'
    )

    return kline_data
```

#### 性能指标

| 操作 | 速度 | 用户体验 |
|------|------|---------|
| **获取快照** | 0.5-1ms | ⚡ 极速 |
| **获取K线** | 5-10ms | ✅ 快速 |
| **切换股票** | 0.5-1ms | ⚡ 无感 |
| **切换周期** | 5-10ms | ✅ 无感 |

#### 订阅限制（实测）

- **订阅能力**: 500只+ ✅
- **数据获取率**: 约72%（362/500）
- **建议**: 实际使用控制在300-400只为佳

---

### 3.4 方案B：无订阅版 - 完整设计

> **详细文档**: [方案B-无订阅版-K线加载设计.md](./方案B-无订阅版-K线加载设计.md)

#### 核心机制

```python
class SmartDataLoader:
    """智能数据加载器（无订阅版）"""

    def load_kline_data(self, symbol: str, period: str, count: int):
        """加载K线数据（三级策略）"""

        # 策略1: 优先本地读取（6-8ms）
        local_data = self._read_local(symbol, period, count)
        if local_data is not None:
            return local_data

        # 策略2: 在线获取（760ms首次，6-8ms后续）
        online_data = self._fetch_online(symbol, period, count)

        # 策略3: 后台下载完整数据
        self._download_in_background(symbol, period)

        return online_data
```

#### 本地数据读取

```python
def _read_local(symbol: str, period: str, count: int):
    """读取本地已下载数据"""
    import xtdata
    from datetime import datetime, timedelta

    # 根据周期计算时间范围
    if period == '1d':
        start_date = (datetime.now() - timedelta(days=count*2)).strftime('%Y%m%d')
    elif period == '5m':
        start_date = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')
    elif period == '15min':
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
    else:
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')

    end_date = datetime.now().strftime('%Y%m%d')

    # 读取本地数据
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period=period,
        start_time=start_date,  # 字符串格式
        end_date=end_date,
        count=0,
        dividend_type='none'
    )

    if data and symbol in data and len(data[symbol]) > 0:
        return data[symbol]

    return None
```

#### 后台下载策略

```python
def _download_in_background(symbol: str, period: str):
    """后台下载完整数据"""
    import threading
    import xtdata
    from datetime import datetime, timedelta

    def download_thread():
        # 计算下载时间范围
        if period == '1d':
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y%m%d')
        elif period == '5m':
            start_date = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')
        else:
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')

        end_date = datetime.now().strftime('%Y%m%d')

        # 下载
        xtdata.download_history_data(
            stock_code=symbol,
            period=period,
            start_time=start_date,
            end_time=end_date
        )

    # 启动后台线程
    thread = threading.Thread(target=download_thread, daemon=True)
    thread.start()
```

#### 性能指标

| 操作 | 首次 | 后续（已下载） | 用户体验 |
|------|------|--------------|---------|
| **本地读取** | - | 6-8ms | ⚡ 极速 |
| **在线获取** | 760ms | 6-8ms | ✅ 可接受 |
| **切换股票** | 760ms | 6-8ms | ✅ 快速 |
| **切换周期** | 760ms | 6-8ms | ✅ 快速 |

---

## 4. 前端配置优化

### 3.1 KLINE_CONFIG v2.0

```typescript
const KLINE_CONFIG: Record<string, {
  immediate: number      // 即时加载根数
  preload: number        // 后台预加载根数
  preload_time: string   // 后台预下载时间范围（新增）
  name: string           // 中文名称
}> = {
  // ========== 常用周期：三层加载 ==========
  'day': {
    immediate: 100,         // 即时：100根（约3个月）
    preload: 480,           // 后台：480根（约2年）
    preload_time: '2years', // 预下载：2年数据
    name: '日线'
  },
  '30min': {
    immediate: 100,         // 即时：100根（约2天）
    preload: 384,           // 后台：384根（约8天）
    preload_time: '3months',// 预下载：3个月数据
    name: '30分钟'
  },
  '60min': {
    immediate: 100,         // 即时：100根（约4天）
    preload: 384,           // 后台：384根（约16天）
    preload_time: '6months',// 预下载：6个月数据
    name: '60分钟'
  },
  'week': {
    immediate: 100,         // 即时：100周（约2年）
    preload: 250,           // 后台：250周（约5年）
    preload_time: '5years', // 预下载：5年数据
    name: '周线'
  },

  // ========== 分钟线：优化加载 ==========
  '5min': {
    immediate: 120,         // 即时：120根（约1周）
    preload: 1056,          // 后台：1056根（约1个月）⭐ 新增
    preload_time: '2months',// 预下载：2个月数据
    name: '5分钟'
  },
  '15min': {
    immediate: 80,          // 即时：80根（约1周）
    preload: 480,           // 后台：480根（约2个月）⭐ 新增
    preload_time: '3months',// 预下载：3个月数据
    name: '15分钟'
  },

  // ========== 特殊周期：仅即时加载 ==========
  'month': {
    immediate: 200,         // 即时：200根（约16年）
    preload: 0,             // 不预加载
    preload_time: '0',
    name: '月线'
  }
}
```

---

## 4. 后端API优化

### 4.1 新增：智能预下载API

**端点**: `POST /api/v1/market/kline-preload`

```python
@router.post("/kline-preload")
async def preload_kline_data(
    symbols: List[str] = Body(..., description="股票代码列表"),
    periods: List[str] = Body(['day', '5min'], description="周期列表")
):
    """
    预下载K线数据（后台执行）

    功能：
    - 后台下载指定股票的多周期数据
    - 不阻塞用户操作
    - 返回立即响应，下载在后台进行

    使用场景：
    - 应用启动时预加载自选股
    - 用户打开股票时预加载其他周期
    """
    import threading
    import xtdata
    from datetime import datetime, timedelta

    def download_in_background():
        """后台下载线程"""
        end_date = datetime.now().strftime('%Y%m%d')

        for symbol in symbols:
            for period in periods:
                # 计算时间范围
                if period == 'day':
                    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y%m%d')  # 2年
                elif period == '5min':
                    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')   # 2个月
                elif period == '15min':
                    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')   # 3个月
                else:
                    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')  # 半年

                # 下载
                try:
                    xtdata.download_history_data(
                        stock_code=symbol,
                        period=period,
                        start_time=start_date,
                        end_time=end_date
                    )
                    logger.info(f"[预下载] {symbol} {period} 数据已下载")
                except Exception as e:
                    logger.error(f"[预下载] {symbol} {period} 失败: {e}")

    # 启动后台线程
    thread = threading.Thread(target=download_in_background, daemon=True)
    thread.start()

    return {
        'code': 200,
        'message': '预下载任务已启动（后台执行）',
        'data': {
            'symbols': symbols,
            'periods': periods,
            'status': 'running'
        }
    }
```

---

### 4.2 优化：智能K线数据获取API

**端点**: `GET /api/v1/market/kline-data`（保持v1.0参数，增强后端逻辑）

```python
@router.get("/kline-data", response_model=Dict[str, Any])
async def get_kline_data(
    symbol: str = Query(...),
    period: str = Query("day"),
    count: int = Query(120),
    end_date: Optional[str] = Query(None)  # 新增：支持指定结束日期
):
    """
    获取K线数据（智能选择最优方式）

    优化策略：
    1. 优先尝试本地读取（已下载的数据）⭐ 新增
    2. 如果本地无数据，使用在线获取
    3. 返回数据来源信息

    数据源优先级：
    - 本地已下载（6-8ms） ⭐ 最快
    - XtQuant在线获取（760ms首次，6-8ms后续）
    - PyTdx备用（50ms+）
    """

    # ===== 策略1：优先尝试本地读取 =====
    local_data = _try_read_local_data(symbol, period, count, end_date)
    if local_data is not None:
        logger.info(f"[K线数据] 本地读取成功: {symbol} {period} {len(local_data)}根")
        return {
            'code': 200,
            'data': local_data.to_dict('records'),
            'data_source': 'local_cache',  # ⭐ 标记来源
            'load_time': '6-8ms'
        }

    # ===== 策略2：本地无数据，在线获取 =====
    logger.info(f"[K线数据] 本地无数据，在线获取: {symbol} {period}")

    # 使用XtQuant在线获取
    try:
        import xtdata

        # 先订阅
        xtdata.subscribe_quote(symbol, period=period, count=0)

        # 获取数据
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period=period,
            start_time='',  # ⭐ 使用count方式
            end_time='',
            count=count,
            dividend_type='none',
            fill_data=True
        )

        if data and symbol in data:
            df = data[symbol]
            logger.info(f"[K线数据] 在线获取成功: {symbol} {period} {len(df)}根")

            return {
                'code': 200,
                'data': df.to_dict('records'),
                'data_source': 'xtquant_online',
                'load_time': '~760ms（首次），6-8ms（后续）'
            }
    except Exception as e:
        logger.error(f"[K线数据] XtQuant获取失败: {e}")

    # ===== 策略3：备用PyTdx =====
    logger.info(f"[K线数据] 尝试PyTdx备用: {symbol} {period}")
    # ... PyTdx获取逻辑 ...

def _try_read_local_data(symbol, period, count, end_date):
    """尝试读取本地已下载数据"""
    import xtdata
    from datetime import datetime, timedelta

    try:
        # 根据周期计算时间范围
        if period == 'day':
            start_date = (datetime.now() - timedelta(days=count*2)).strftime('%Y%m%d')
        elif period == '5m':
            start_date = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')
        elif period == '15min':
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
        else:
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')

        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')

        # 读取本地数据
        data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period=period,
            start_time=start_date,
            end_time=end_date,
            count=0,
            dividend_type='none'
        )

        if data and symbol in data and len(data[symbol]) > 0:
            return data[symbol]

        return None

    except Exception as e:
        logger.debug(f"[本地读取] 失败: {e}")
        return None
```

---

## 5. 前端实现优化

### 5.1 应用启动时预加载

**文件**: `frontend/src/App.vue` 或 `frontend/src/main.ts`

```typescript
/**
 * 应用启动时预加载常用数据
 */
onMounted(async () => {
  console.log('[App启动] 开始预加载K线数据...')

  // 获取用户自选股
  const watchlist = getUserWatchlist()  // 从localStorage或API获取

  if (watchlist && watchlist.length > 0) {
    const symbols = watchlist.slice(0, 10)  // 预加载前10只

    // 常用周期
    const periods = ['day', '5min', '30min', '60min']

    // 调用预下载API（后台执行）
    await http.post('/api/v1/market/kline-preload', {
      symbols,
      periods
    })

    console.log(`[App启动] ✅ 已启动预加载: ${symbols.join(', ')}`)
    console.log(`[App启动] 预加载周期: ${periods.join(', ')}`)
  }
})
```

---

### 5.2 用户打开股票时的加载流程（优化）

**文件**: `frontend/src/views/TradingViewKLineChart.vue`

```typescript
/**
 * 加载K线数据（优化版）
 * @param period 周期
 * @param symbol 股票代码
 */
const loadKlineData = async (period: string, symbol: string) => {
  const config = KLINE_CONFIG[period] || KLINE_CONFIG['day']
  const immediateCount = config.immediate

  console.log(`[K线加载] 开始: ${symbol} ${period}`)
  console.log(`[K线加载] 配置: immediate=${immediateCount}, preload=${config.preload}`)

  try {
    // ===== 第一步：立即显示（优先本地）=====
    const result1 = await http.get('/api/v1/market/kline-data', {
      params: {
        symbol,
        period,
        count: immediateCount
      }
    })

    if (result1.data.code === 200) {
      const klineData = result1.data.data
      const dataSource = result1.data.data_source  // 'local_cache' 或 'xtquant_online'

      // 渲染图表
      renderChart(klineData)

      console.log(`[K线加载] ✅ 首屏显示: ${klineData.length}根 (${dataSource})`)
      console.log(`[K线加载] 数据来源: ${dataSource}`)

      // ===== 第二步：后台扩展（如果需要预加载）=====
      if (config.preload > 0) {
        console.log(`[K线加载] 后台扩展: 预加载${config.preload}根...`)

        // 延迟执行，避免阻塞首屏
        setTimeout(async () => {
          await expandKlineData(symbol, period, config.preload)
        }, 100)
      }

      // ===== 第三步：启动实时更新 =====
      startRealtimeUpdate()
    }
  } catch (error) {
    console.error('[K线加载] 加载失败:', error)
    ElMessage.error('K线数据加载失败，请稍后重试')
  }
}

/**
 * 扩展K线数据（后台预加载）
 */
const expandKlineData = async (symbol: string, period: string, preloadCount: number) => {
  console.log(`[K线扩展] 开始: ${symbol} ${period} +${preloadCount}根`)

  try:
    // 尝试读取更多本地数据（如果有）
    const result = await http.get('/api/v1/market/kline-data', {
      params: {
        symbol,
        period,
        count: preloadCount
      }
    })

    if (result.data.code === 200) {
      const newData = result.data.data
      const dataSource = result.data.data_source

      if (dataSource === 'local_cache' && newData.length > currentDataCount) {
        // 本地有更多数据，无缝更新图表
        updateChartWithNewData(newData)
        console.log(`[K线扩展] ✅ 已扩展: ${newData.length}根 (本地)`)
      } else if (dataSource === 'xtquant_online') {
        // 在线获取到的数据，可能需要触发下载
        console.log(`[K线扩展] ⚠️ 本地数据不足，触发后台下载...`)

        // 触发后台下载
        http.post('/api/v1/market/kline-preload', {
          symbols: [symbol],
          periods: [period]
        })
      }
    }
  } catch (error) {
    console.error('[K线扩展] 失败:', error)
  }
}

/**
 * 渲染图表
 */
const renderChart = (klineData: any[]) => {
  // 转换为lightweight-charts格式
  const bars = klineData.map(item => ({
    time: new Date(item.datetime).getTime() / 1000,
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
    volume: item.volume
  }))

  // 设置图表数据
  candlestickSeries.setData(bars)
  volumeSeries.setData(bars.map(bar => ({
    time: bar.time,
    value: bar.volume,
    color: bar.close >= bar.open
      ? 'rgba(38, 166, 154, 0.5)'
      : 'rgba(239, 83, 80, 0.5)'
  })))

  // 保存当前数据
  currentDataCount = bars.length
}

/**
 * 无缝更新图表数据
 */
const updateChartWithNewData = (newData: any[]) => {
  // 转换格式
  const newBars = newData.map(item => ({
    time: new Date(item.datetime).getTime() / 1000,
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
    volume: item.volume
  }))

  // 合并数据（去重）
  const existingBars = candlestickSeries.data()
  const allBars = [...existingBars, ...newBars]

  // 去重（按时间）
  const uniqueBars = Array.from(
    new Map(allBars.map(bar => [bar.time, bar])).values()
  ).sort((a, b) => a.time - b.time)

  // 更新图表
  candlestickSeries.setData(uniqueBars)

  currentDataCount = uniqueBars.length
}
```

---

### 5.3 切换周期优化（无感切换）

```typescript
/**
 * 切换周期（优化版）
 */
const switchPeriod = async (newPeriod: string) => {
  console.log(`[周期切换] ${currentPeriod.value} -> ${newPeriod}`)

  // 检查是否已预加载（在内存中）
  if (periodDataCache[newPeriod]) {
    // ✅ 已缓存，直接显示（无感！）
    console.log(`[周期切换] ✅ 使用缓存: ${newPeriod}`)

    const cachedData = periodDataCache[newPeriod]
    renderChart(cachedData)
    currentPeriod.value = newPeriod

    return
  }

  // ⚠️ 未缓存，需要加载
  console.log(`[周期切换] 加载数据: ${newPeriod}`)

  // 加载新周期数据
  await loadKlineData(newPeriod, currentSymbol.value)
  currentPeriod.value = newPeriod
}
```

---

## 6. 性能优化总结

### 6.1 性能对比

| 操作 | v1.0（PyTdx） | v2.0（XtQuant） | 提升 |
|------|--------------|----------------|------|
| **首次打开股票** | ~20ms | **6-8ms**（本地） | 3x 更快 |
| **切换周期（已缓存）** | <50ms | **<10ms** | 5x 更快 |
| **切换周期（未缓存）** | 5-18ms | **760ms（首次），6-8ms（后续）** | 首次慢，后续快 |
| **加载5分钟K线（1个月）** | 不支持 | **~1秒** | ✅ 新增能力 |

### 6.2 用户体验流程

```
用户操作流程：

t=0ms:     用户点击"贵州茅台"
t=8ms:     ✅ 显示日K线（本地已预下载）← 无感！
t=100ms:   后台预加载其他周期（5分钟、30分钟等）

t=用户操作: 用户点击"5分钟K线"
t=8ms:     ✅ 显示5分钟K线（已预加载）← 无感！

t=用户操作: 用户点击"30分钟K线"
t=8ms:     ✅ 显示30分钟K线（已预加载）← 无感！

⭐ 整个过程完全无感切换！
```

---

## 7. 完整实施步骤

### 步骤1: 后端实现

- [ ] 实现预下载API `/api/v1/market/kline-preload`
- [ ] 优化K线数据获取API，优先本地读取
- [ ] 添加数据来源标记（local_cache / xtquant_online）
- [ ] 实现本地数据读取逻辑

### 步骤2: 前端实现

- [ ] 应用启动时预加载自选股
- [ ] 优化loadKlineData函数，支持数据来源判断
- [ ] 实现后台扩展数据逻辑
- [ ] 实现周期数据缓存（内存级）

### 步骤3: 测试验证

- [ ] 测试应用启动预加载
- [ ] 测试首次打开股票速度
- [ ] 测试切换周期响应速度
- [ ] 测试不同周期的数据完整性

---

## 8. 关键要点总结

### 8.1 v2.0 核心优势

1. ✅ **应用启动预加载** - 用户打开股票时数据已在本地
2. ✅ **优先本地读取** - 6-8ms vs 760ms在线获取
3. ✅ **后台智能扩展** - 无缝扩展到完整历史
4. ✅ **无感周期切换** - 已预加载的周期<10ms切换

### 8.2 数据使用原则

| 场景 | 优先使用 | 原因 |
|------|---------|------|
| **启动预加载** | download_history_data | 后台不阻塞，一次下载永久使用 |
| **首次打开** | 本地读取（如已预加载）> 在线获取 | 6-8ms vs 760ms |
| **扩展数据** | download_history_data + 本地读取 | 无时间限制，速度快 |
| **实时更新** | subscribe_quote + get_full_tick | 1ms订阅缓存 |

---

**文档版本**: v2.0
**更新日期**: 2026-02-05
**状态**: ✅ 完成优化设计
