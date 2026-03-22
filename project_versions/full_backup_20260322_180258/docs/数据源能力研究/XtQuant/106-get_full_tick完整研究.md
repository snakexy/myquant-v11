# get_full_tick() 完整研究 - 聚合数据API

> **测试日期**: 2026-02-05
> **状态**: ✅ 已验证可用
> **性能**: 优秀（6-60ms批量获取）

---

## 功能概述

**`get_full_tick()`** 是XtQuant提供的**聚合数据API**，用于批量获取多只股票的实时行情数据。

### 核心特性

- ✅ **批量获取**：一次调用获取多只股票行情
- ✅ **性能优秀**：100只股票 ~6.5ms，1000只股票 ~60ms
- ✅ **全市场支持**：可获取全市场5186只A股
- ✅ **无需下载**：直接调用，无需预下载
- ✅ **实时更新**：返回最新行情数据

---

## API文档

### 函数签名

```python
from xtquant import xtdata

tick_data = xtdata.get_full_tick(stock_list)
```

### 参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| **stock_list** | list[str] | 股票代码列表 | `['600000.SH', '000001.SZ']` |

### 返回值

**类型**: `dict[str, dict]`

**格式**: `{股票代码: 行情数据}`

```python
{
    '600000.SH': {
        'lastPrice': 10.50,      # 最新价
        'lastClose': 10.45,      # 昨收价
        'amount': 236604400,     # 成交额
        'volume': 260200,        # 成交量
        'askPrice1': 10.51,      # 卖一价
        'bidPrice1': 10.50,      # 买一价
        # ... 更多字段
    },
    '000001.SZ': { ... }
}
```

---

## 性能测试结果

### 实测数据（2026-02-05）

| 股票数量 | 耗时 | 平均耗时/只 | 数据量 |
|---------|------|------------|--------|
| 10只 | 1.00ms | 0.1ms | 100% |
| 100只 | 6.52ms | 0.065ms | 100% |
| 500只 | 29.56ms | 0.059ms | 100% |
| 1000只 | 59.17ms | 0.059ms | 100% |

**结论**:
- ✅ 性能随股票数量线性增长
- ✅ 适合批量获取
- ✅ 推荐每批100-500只

---

## 使用场景

### 场景1: 股票列表页面（推荐）

```python
# 1. 获取全市场股票
all_stocks = xtdata.get_stock_list_in_sector('沪深A股')
# 返回 5186只

# 2. 分页获取行情
page_size = 100
page = 1

# 计算当前页的股票
start = (page - 1) * page_size
end = start + page_size
page_stocks = all_stocks[start:end]

# 3. 批量获取行情
tick_data = xtdata.get_full_tick(page_stocks)

# 4. 渲染到前端
# 返回给前端显示
```

**性能**:
- 首次加载: ~17ms (获取列表 + 获取100只行情)
- 翻页加载: ~6.5ms

---

### 场景2: 自选股列表（推荐）

```python
# 从数据库/配置读取自选股
watchlist = ['600519.SH', '000001.SZ', '600036.SH', ...]

# 批量获取行情
tick_data = xtdata.get_full_tick(watchlist)

# 返回格式
# {
#     '600519.SH': {'lastPrice': 1650.00, ...},
#     '000001.SZ': {'lastPrice': 10.50, ...},
#     ...
# }
```

**性能**:
- 200只自选股: ~12ms
- 适合实时刷新（每3秒）

---

### 场景3: 实时刷新（推荐）

```python
import time

# 股票列表
symbols = ['600519.SH', '000001.SZ', '600036.SH']

# 循环刷新
while True:
    # 获取最新行情
    tick_data = xtdata.get_full_tick(symbols)

    # 更新界面
    for symbol, data in tick_data.items():
        print(f"{symbol}: {data['lastPrice']}")

    # 等待3秒
    time.sleep(3)
```

**性能**:
- 每次刷新: ~1ms（3只股票）
- 适合实时监控

---

## 返回字段说明

### 基础字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `lastPrice` | float | 最新价 | 10.50 |
| `lastClose` | float | 昨收价 | 10.45 |
| `amount` | int | 成交额（元） | 236604400 |
| `volume` | int | 成交量（手） | 260200 |

### 五档行情

| 字段 | 类型 | 说明 |
|------|------|------|
| `askPrice1-5` | float | 卖一到卖五价 |
| `askVolume1-5` | int | 卖一到卖五量 |
| `bidPrice1-5` | float | 买一到买五价 |
| `bidVolume1-5` | int | 买一到买五量 |

### 其他字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `pSnap` | int | 涨速 |

---

## 最佳实践

### 1. 分页加载

```python
def get_stock_list_page(page=1, page_size=100):
    """分页获取股票列表"""
    # 获取全市场股票
    all_stocks = xtdata.get_stock_list_in_sector('沪深A股')

    # 计算分页
    total = len(all_stocks)
    start = (page - 1) * page_size
    end = min(start + page_size, total)

    # 获取当前页股票行情
    page_stocks = all_stocks[start:end]
    tick_data = xtdata.get_full_tick(page_stocks)

    return {
        'data': tick_data,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    }
```

---

### 2. 前端缓存

```typescript
// 前端缓存
const quoteCache = new Map<string, QuoteData>();

// 定时刷新
setInterval(async () => {
    const symbols = Array.from(quoteCache.keys());
    const response = await fetch('/api/quotes', {
        method: 'POST',
        body: JSON.stringify({ symbols })
    });

    const data = await response.json();

    // 更新缓存
    for (const [symbol, quote] of Object.entries(data)) {
        quoteCache.set(symbol, quote);
    }
}, 3000); // 每3秒刷新
```

---

### 3. 错误处理

```python
def get_quotes_safe(symbols):
    """安全的行情获取（带错误处理）"""
    try:
        tick_data = xtdata.get_full_tick(symbols)

        # 检查返回数据
        if not tick_data:
            logger.warning("获取行情失败：返回空数据")
            return {}

        # 过滤无效数据
        valid_data = {
            symbol: data
            for symbol, data in tick_data.items()
            if data and data.get('lastPrice', 0) > 0
        }

        if len(valid_data) < len(symbols):
            logger.warning(f"部分股票无数据：{len(valid_data)}/{len(symbols)}")

        return valid_data

    except Exception as e:
        logger.error(f"获取行情异常: {e}")
        return {}
```

---

## 注意事项

### ⚠️ 非交易时间

- **返回值**: 最后收盘价或昨收价
- **建议**: 显示"非交易时间"提示

### ⚠️ 停牌股票

- **返回值**: 可能有数据或为空
- **建议**: 检查 `lastPrice` 是否为0

### ⚠️ 新股

- **返回值**: 可能有延迟
- **建议**: 使用前先检查股票是否存在

---

## 与其他API对比

| API | 功能 | 性能 | 使用场景 |
|-----|------|------|---------|
| **get_full_tick()** | 批量获取实时行情 | 6-60ms | ✅ 股票列表、自选股 |
| **get_market_data_ex()** | 获取K线数据 | 760ms首次 | K线图表 |
| **subscribe_quote()** | 订阅实时推送 | 0.5-1ms | 高频实时监控 |

---

## 完整示例代码

### 后端API

```python
from fastapi import APIRouter
from xtquant import xtdata

router = APIRouter()

@router.post("/api/v1/market/quotes")
async def get_quotes(symbols: list[str]):
    """
    批量获取股票行情

    参数:
        symbols: 股票代码列表

    返回:
        {
            'code': 200,
            'data': {
                '600000.SH': {'lastPrice': 10.50, ...},
                ...
            }
        }
    """
    try:
        # 获取行情
        tick_data = xtdata.get_full_tick(symbols)

        return {
            'code': 200,
            'data': tick_data,
            'count': len(tick_data)
        }

    except Exception as e:
        return {
            'code': 500,
            'message': str(e)
        }


@router.get("/api/v1/market/stock-list")
async def get_stock_list(
    sector: str = "沪深A股",
    page: int = 1,
    page_size: int = 100
):
    """
    获取股票列表（分页）

    参数:
        sector: 板块名称
        page: 页码
        page_size: 每页数量

    返回:
        {
            'code': 200,
            'data': {...},
            'total': 5186,
            'page': 1
        }
    """
    try:
        # 获取股票列表
        all_stocks = xtdata.get_stock_list_in_sector(sector)

        # 分页
        total = len(all_stocks)
        start = (page - 1) * page_size
        end = min(start + page_size, total)

        page_stocks = all_stocks[start:end]

        # 获取行情
        tick_data = xtdata.get_full_tick(page_stocks)

        return {
            'code': 200,
            'data': tick_data,
            'total': total,
            'page': page,
            'page_size': page_size
        }

    except Exception as e:
        return {
            'code': 500,
            'message': str(e)
        }
```

---

## 总结

### ✅ 优势

1. **性能优秀**: 批量获取，性能线性增长
2. **使用简单**: 一个函数搞定，无需配置
3. **无需下载**: 直接调用，立即可用
4. **全市场支持**: 5186只A股全部支持

### 🎯 适用场景

- ✅ 股票列表页面
- ✅ 自选股列表
- ✅ 实时行情刷新
- ✅ 批量数据查询

### 📝 建议

1. **分页加载**: 每页100-500只股票
2. **前端缓存**: 减少重复请求
3. **定时刷新**: 每3秒刷新一次
4. **错误处理**: 处理非交易时间、停牌等情况

---

**Sources:**
- [XtQuant.XtData 行情模块文档](https://dict.thinktrader.net/nativeApi/xtdata.html)
- [QMT量化编程之最新分笔数据接口get_full_tick](https://zhuanlan.zhihu.com/p/680368683)
- [迅投QMT实时行情接口接入](https://juejin.cn/post/7127204744178712612)
