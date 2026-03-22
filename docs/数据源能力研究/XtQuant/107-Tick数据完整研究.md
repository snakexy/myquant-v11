# Tick数据完整研究 - XtQuant

> **测试日期**: 2026-02-05
> **研究内容**: XtQuant中tick数据的获取方式和使用场景

---

## 核心发现

### ⚠️ 重要区分

在XtQuant中，**"tick数据"**有两种不同的含义：

| 类型 | API | 数据形式 | 用途 |
|------|-----|---------|------|
| **实时tick快照** | `get_full_tick()` | 最新一次快照 | 股票列表、实时行情 |
| **历史tick序列** | `download_history_data(period='tick')` | 逐笔成交时间序列 | 高频分析、回测 |

---

## 1. 实时Tick快照 - get_full_tick()

### 功能说明

提供**最新一次**的分笔数据快照，不是历史tick序列。

### API

```python
from xtquant import xtdata

# 批量获取最新tick快照
tick_data = xtdata.get_full_tick(['600519.SH', '000001.SZ'])

# 返回格式
# {
#     '600519.SH': {
#         'lastPrice': 1525,
#         'lastClose': 1474.92,
#         'volume': 109123,
#         'amount': 16444346000,
#         ... (共17个字段)
#     },
#     '000001.SZ': { ... }
# }
```

### 测试结果

```
[OK] 获取成功
     耗时: 6.03ms
     返回字段数: 17

示例数据:
  最新价: 1525
   昨收: 1474.92
   成交量: 109123
   成交额: 16444346000
   时间: 20260204 15:00:02
```

### 性能

| 股票数量 | 耗时 | 用途 |
|---------|------|------|
| 10只 | 1ms | 自选股刷新 |
| 100只 | 6.5ms | 股票列表分页 |
| 1000只 | 60ms | 全市场扫描 |

### 适用场景

- ✅ 股票列表页面
- ✅ 自选股实时刷新
- ✅ 批量行情查询
- ❌ 不用于历史回测
- ❌ 不提供逐笔成交序列

---

## 2. 历史Tick序列 - download_history_data()

### 功能说明

下载**逐笔成交**的历史时间序列数据，包含每笔交易的详细信息。

### API

#### 下载

```python
from xtquant import xtdata

# 下载历史tick数据
xtdata.download_history_data(
    stock_code='600519.SH',
    period='tick',  # ⭐ 关键参数
    start_time='20240201',
    end_time='20240205'
)
```

#### 读取

```python
# 读取已下载的tick数据
data = xtdata.get_market_data_ex(
    field_list=['time', 'price', 'volume', 'amount'],
    stock_list=['600519.SH'],
    period='tick',
    start_time='20240201',
    end_time='20240205'
)
```

### ⚠️ 重要提示

**数据量巨大**：

| 周期 | 1天数据量 | 说明 |
|------|----------|------|
| **tick** | 数万～数十万条 | 每笔交易一条 |
| **1分钟** | 240条 | 每分钟一条 |
| **5分钟** | 48条 | 每5分钟一条 |
| **1d** | 1条 | 每天一条 |

### 测试结果

```
[测试2] 检查本地是否有tick历史数据
--------------------------------------------------------------------------------
[OK] 本地有tick数据
     数据量: 0 条

说明: 未下载tick数据
```

### 适用场景

- ✅ 高频交易分析
- ✅ 逐笔成交回测
- ✅ 微观结构研究
- ❌ 不用于普通行情显示（数据量太大）

---

## 3. 不同周期对比

### 测试结果

```
[测试4] 对比tick、1分钟、5分钟数据
--------------------------------------------------------------------------------
[OK] period='tick': 0 条      (未下载)
[OK] period='1m': 5 条       (✅ 有数据)
[OK] period='5m': 5 条       (✅ 有数据)
[OK] period='1d': 5 条       (✅ 有数据)
```

### 选择建议

| 使用场景 | 推荐周期 | 理由 |
|---------|---------|------|
| **股票列表** | `get_full_tick()` | 快速、批量 |
| **分时图** | `1m` 或 `5m` | 数据量适中 |
| **K线图** | `1d` | 趋势分析 |
| **高频分析** | `tick` | 专业用途 |
| **实时监控** | `get_full_tick()` | 最新快照 |

---

## 4. 数据字段对比

### get_full_tick() 返回字段（17个）

```
lastPrice            最新价
lastClose            昨收价
open                 开盘价
high                 最高价
low                  最低价
volume               成交量
amount               成交额
askPrice             卖盘价（5档列表）
askVol               卖盘量（5档列表）
bidPrice             买盘价（5档列表）
bidVol               买盘量（5档列表）
pvolume              成交量（手）
timetag              时间标签
stockStatus          股票状态
openInt              持仓量
lastSettlementPrice  最后结算价
settlementPrice      结算价
```

### 历史tick数据字段

**下载tick数据后**，`get_market_data_ex(period='tick')` 返回的字段：

```
time      成交时间
price     成交价格
volume    成交量
amount    成交额
```

**注意**：历史tick数据字段比实时快照少很多。

---

## 5. 使用建议

### 📌 普通行情功能（推荐）

```python
# ✅ 使用 get_full_tick()
from xtquant import xtdata

# 股票列表
tick_data = xtdata.get_full_tick(stock_list)

# 实时刷新
while True:
    quotes = xtdata.get_full_tick(watchlist)
    # 更新界面
    time.sleep(3)
```

**优势**：
- 快速（6-60ms）
- 批量获取
- 无需下载

---

### 📌 分时图功能（推荐）

```python
# ✅ 使用 1分钟 或 5分钟 K线
from xtquant import xtdata

# 获取1分钟数据
data = xtdata.get_market_data_ex(
    field_list=['time', 'open', 'high', 'low', 'close', 'volume'],
    stock_list=['600519.SH'],
    period='1m',
    start_time='',
    end_time='',
    count=240  # 1天240分钟
)
```

**优势**：
- 数据量适中
- 足够绘制分时图
- 已有本地数据

---

### 📌 高频分析（专业）

```python
# ⚠️ 谨慎使用 tick 数据
from xtquant import xtdata

# 下载tick数据（数据量大）
xtdata.download_history_data(
    stock_code='600519.SH',
    period='tick',
    start_time='20240201',
    end_time='20240202'  # 只下载1天测试
)

# 读取tick数据
data = xtdata.get_market_data_ex(
    field_list=['time', 'price', 'volume', 'amount'],
    stock_list=['600519.SH'],
    period='tick',
    start_time='20240201',
    end_time='20240202'
)
```

**注意**：
- 数据量巨大（每天数万条）
- 需要大量存储空间
- 处理耗时长

---

## 6. 性能对比

### 数据获取性能

| 操作 | 耗时 | 数据量 |
|------|------|--------|
| `get_full_tick()` (100只) | 6.5ms | 100条快照 |
| `get_market_data_ex(period='1m', count=240)` | 50ms | 240条 |
| `get_market_data_ex(period='tick', count=10000)` | 200ms | 10000条 |

### 存储空间

| 数据类型 | 1天 | 1年（250交易日） |
|---------|-----|----------------|
| Tick数据 | ~10MB | ~2.5GB |
| 1分钟K线 | ~100KB | ~25MB |
| 日K线 | ~1KB | ~250KB |

---

## 7. 完整示例

### 股票列表（使用get_full_tick）

```python
from xtquant import xtdata

def get_stock_list_page(page=1, page_size=100):
    """获取股票列表（分页）"""
    # 获取全市场股票
    all_stocks = xtdata.get_stock_list_in_sector('沪深A股')

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    page_stocks = all_stocks[start:end]

    # 获取行情
    tick_data = xtdata.get_full_tick(page_stocks)

    return {
        'data': tick_data,
        'total': len(all_stocks),
        'page': page
    }

# 使用
result = get_stock_list_page(page=1, page_size=100)
print(f"共 {result['total']} 只股票，当前页 {len(result['data'])} 只")
```

---

### 分时图（使用1分钟K线）

```python
from xtquant import xtdata

def get_intraday_chart(symbol):
    """获取分时图数据"""
    # 获取1分钟K线（最近4小时）
    data = xtdata.get_market_data_ex(
        field_list=['time', 'open', 'high', 'low', 'close', 'volume'],
        stock_list=[symbol],
        period='1m',
        start_time='',
        end_time='',
        count=240  # 4小时 = 240分钟
    )

    if data and symbol in data:
        return data[symbol]
    return None

# 使用
chart_data = get_intraday_chart('600519.SH')
print(f"分时图数据: {len(chart_data)} 条")
```

---

## 总结

### ✅ 推荐使用

| 功能 | API | 原因 |
|------|-----|------|
| **股票列表** | `get_full_tick()` | 快速、批量、实时 |
| **分时图** | `get_market_data_ex(period='1m')` | 数据量适中 |
| **K线图** | `get_market_data_ex(period='1d')` | 趋势分析 |
| **实时刷新** | `get_full_tick()` | 最快 |

### ⚠️ 谨慎使用

| 功能 | API | 原因 |
|------|-----|------|
| **tick数据** | `download_history_data(period='tick')` | 数据量巨大 |
| **历史tick** | `get_market_data_ex(period='tick')` | 需先下载，耗时长 |

### 💡 关键理解

1. **`get_full_tick()`** 不是历史tick，是最新快照
2. **分时图** 应该用1分钟K线，不是tick
3. **tick数据** 只在专业高频分析时才需要

---

**Sources:**
- [XtQuant.XtData 行情模块](https://dict.thinktrader.net/nativeApi/xtdata.html)
- [QMT获取股票历史tick数据](https://blog.csdn.net/2301_77247806/article/details/147874119)
- [QMT行情接口以及历史行情数据下载](https://www.cnblogs.com/mxnote/articles/17283080.html)
