# XtQuant API与功能映射 - 修正版

> 创建日期: 2026-02-05
> 修正：按实时性和数据类型分类，而不是按功能模块

---

## API分类策略

### 按实时性分类

#### 实时数据（交易时间内）⚡
- 特点：数据实时更新（3秒一次）
- API：`get_full_tick()` + `subscribe_quote()`
- 适用：行情列表、自选股、分时图

#### 近实时数据（1-5分钟更新）
- 特点：准实时，有延迟
- API：`get_market_data_ex()` 小周期
- 适用：K线图表（分钟级）

#### 历史数据（固定）
- 特点：稳定不变
- API：`get_market_data_ex()` 大周期 + `download_history_data()`
- 适用：回测、历史查询

---

### 按数据类型分类

#### L1: 实时快照（单股）
```python
# 最快：订阅缓存
data = xtdata.get_full_tick(['600519.SH'])  # < 1ms

# 返回最新价、买卖盘等完整信息
```

**适用场景**：
- ✅ 股票详情页头部
- ✅ 实时价格显示
- ✅ 买卖盘口

---

#### L2: 实时列表（多股）
```python
# 批量获取（需要先订阅）
for stock in stocks:
    xtdata.subscribe_quote(stock, period='1d')

data = xtdata.get_full_tick(stocks)  # 批量，< 50ms
```

**适用场景**：
- ✅ 行情列表（< 100只）
- ✅ 自选股
- ✅ 热门股监控

**限制**：
- 单实例订阅上限：~300只
- 超过需要多实例或分批

---

#### L3: 实时分时图 ⭐关键修正

**错误理解**：
```python
# ❌ 错误：用1分钟K线
data = xtdata.get_market_data_ex(period='1m', count=240)
```

**正确理解**：
```python
# ✅ 正确：用tick数据实时聚合

# 方案A: 订阅tick推送
xtdata.subscribe_quote('600519.SH', period='tick')

# 注册回调
def on_tick_update(data):
    # 实时更新分时图
    update_chart(data)

xtdata.register_callback(on_tick_update)

# 方案B: 定时拉取tick
def get_intraday_realtime(symbol):
    """获取实时分时数据"""
    while is_trading_time():
        # 获取最新tick
        tick_data = xtdata.get_market_data_ex(
            stock_list=[symbol],
            period='tick',
            count=1
        )
        # 聚合到分时图
        update_chart(tick_data)
        time.sleep(3)  # 3秒刷新
```

**适用场景**：
- ✅ **分时图**（实时更新）
- ✅ 盘中监控
- ✅ 实时走势分析

---

#### L4: K线图表（分钟级）

```python
# 分钟K线（准实时）
data = xtdata.get_market_data_ex(
    stock_list=['600519.SH'],
    period='5m',  # 5分钟K线
    count=120
)
```

**适用场景**：
- ✅ 5分钟K线图
- ✅ 15分钟K线图
- ✅ 30分钟K线图
- ✅ 60分钟K线图

**更新频率**：每个周期结束更新一次（5分钟、15分钟等）

---

#### L5: K线图表（日级）

```python
# 日K线（历史）
data = xtdata.get_market_data_ex(
    stock_list=['600519.SH'],
    period='1d',
    count=100
)

# 或者先下载再读取（更快）
xtdata.download_history_data(
    stock_code='600519.SH',
    period='1d',
    start_time='20240101',
    end_time='20241231'
)

data = xtdata.get_market_data_ex(
    stock_list=['600519.SH'],
    period='1d',
    start_time=20240101,
    end_time=20241231,
    count=0
)
```

**适用场景**：
- ✅ 日K线图
- ✅ 周K线图
- ✅ 月K线图
- ✅ 回测系统

**性能对比**：
- 在线获取：~500ms
- 下载+读取：~150ms（**快3倍**）

---

## 重新整理：按场景选择API

### 场景1: 实时行情列表

**需求**：显示股票列表的实时行情

**正确方案**：
```python
class RealtimeQuoteList:
    """实时行情列表"""

    def __init__(self):
        self.subscribed = set()

    def get_quotes(self, symbols):
        """获取行情（自动订阅管理）"""

        # 1. 确保已订阅
        for symbol in symbols:
            if symbol not in self.subscribed:
                xtdata.subscribe_quote(symbol, period='1d')
                self.subscribed.add(symbol)

        # 2. 从缓存获取
        return xtdata.get_full_tick(symbols)  # < 1ms

    def refresh(self):
        """定期刷新（3秒）"""
        while True:
            if self.is_trading_time():
                quotes = xtdata.get_full_tick(list(self.subscribed))
                push_to_frontend(quotes)
            time.sleep(3)
```

---

### 场景2: 实时分时图 ⭐修正

**需求**：显示当天的分时走势

**正确方案**：
```python
class RealtimeIntradayChart:
    """实时分时图"""

    def __init__(self, symbol):
        self.symbol = symbol
        self.data = []

    def start(self):
        """启动实时更新"""

        # 1. 订阅tick数据
        xtdata.subscribe_quote(self.symbol, period='tick')

        # 2. 注册回调
        def on_tick(tick_data):
            # 实时聚合为分钟数据
            minute_data = self._aggregate_to_minute(tick_data)
            # 更新图表
            update_chart(minute_data)

        xtdata.register_callback(on_tick)

    def _aggregate_to_minute(self, tick_data):
        """将tick聚合成分钟数据"""
        # tick → 1分钟K线
        return aggregate_tick_to_kline(tick_data, period='1m')
```

**错误方案** ❌：
```python
# ❌ 不要用1分钟K线作为分时图！
data = get_market_data_ex(period='1m', count=240)
# 问题：1分钟K线不是实时的，有延迟
```

---

### 场景3: K线图表（多周期）

**需求**：显示日K线、周K线、分钟K线

**正确方案**：
```python
def get_kline_chart(symbol, period, count):
    """获取K线数据（智能选择）"""

    # 分钟线：在线获取（16天限制）
    if period in ['1m', '5m', '15m', '30m', '60m']:
        return xtdata.get_market_data_ex(
            stock_list=[symbol],
            period=period,
            count=count,
            dividend_type='none'  # ⭐ 字符串
        )

    # 日K线：下载+读取（更快）
    if period in ['1d', '1w', '1M']:
        # 先下载
        xtdata.download_history_data(
            stock_code=symbol,
            period=period,
            start_time=calculate_start_date(count, period),
            end_time=get_today()
        )

        # 再读取
        return xtdata.get_market_data_ex(
            stock_list=[symbol],
            period=period,
            count=count
        )
```

---

### 场景4: 非交易时间显示

**需求**：周末、节假日、收盘后查看行情

**正确方案**：
```python
def get_quotes_smart(symbols):
    """智能获取行情（处理非交易时间）"""

    if is_trading_time():
        # 交易时间：实时数据
        return xtdata.get_full_tick(symbols)
    else:
        # 非交易时间：最后收盘价
        quotes = {}
        for symbol in symbols:
            kline = xtdata.get_market_data_ex(
                stock_list=[symbol],
                period='1d',
                count=1
            )
            if symbol in kline:
                last = kline[symbol].iloc[-1]
                quotes[symbol] = {
                    'lastPrice': last['close'],
                    'lastClose': last['close'],
                    'updateTime': kline[symbol].index[-1]
                }
        return quotes
```

---

## API选择决策树（修正版）

```
用户需求
    ↓
需要实时更新？
    ↓ 是
是否分时图？
    ↓ 是
→ subscribe_quote(period='tick') + 回调聚合  ⭐实时分时

    ↓ 否
→ get_full_tick() + subscribe_quote()  ⭐实时行情

    ↓ 否
需要历史数据？
    ↓ 是
分钟线（< 16天）？
    ↓ 是
→ get_market_data_ex(period='1m/5m')  ⭐分钟K线

    ↓ 否
日K线（大量数据）？
    ↓ 是
→ download_history_data() + get_market_data_ex()  ⭐下载+读取

    ↓ 否
→ get_market_data_ex()  ⭐通用方案
```

---

## 关键修正

### 修正1: 分时图是实时的

**错误** ❌：
```python
# 用1分钟K线作为分时图
data = get_market_data_ex(period='1m', count=240)
```

**正确** ✅：
```python
# 订阅tick实时推送
subscribe_quote(symbol, period='tick')
# 注册回调实时更新图表
```

---

### 修正2: 按实时性分类，不是按功能

| 实时性 | API | 适用 |
|--------|-----|------|
| **实时（< 1ms）** | `get_full_tick()` + `subscribe_quote()` | 自选股、详情页 |
| **实时分时** | `subscribe_quote('tick')` + 回调 | **分时图** ⭐ |
| **准实时（分钟）** | `get_market_data_ex(period='5m')` | 分钟K线图 |
| **历史（日/周）** | `download_history_data()` + `get_market_data_ex()` | 日K线、回测 |

---

## 总结

### 核心原则 ⭐

1. **分时图必须是实时的**：使用tick订阅
2. **行情列表优先订阅**：性能最优（< 1ms）
3. **K线图按周期选择**：分钟线在线，日线下载+读取
4. **非交易时间自动降级**：显示最后收盘价

### 最佳实践

```python
# 1. 自选股（实时）
subscribe_quote() + get_full_tick()

# 2. 分时图（实时）⭐
subscribe_quote(period='tick') + 回调聚合

# 3. 分钟K线（准实时）
get_market_data_ex(period='5m')

# 4. 日K线（历史）
download_history_data() + get_market_data_ex()

# 5. 非交易时间
get_market_data_ex(period='1d', count=1)
```

---

**修正完成：分时图是实时的，使用tick数据！**
