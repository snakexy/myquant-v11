# 第6章 - 常见问题FAQ

**文档版本**: v3.2
**更新日期**: 2026-03-20

---

## 目录

- [6.1 数据源选择问题](#61-数据源选择问题)
- [6.2 时间段问题](#62-时间段问题)
- [6.3 性能优化问题](#63-性能优化问题)
- [6.4 板块数据问题](#64-板块数据问题)
- [6.5 V5架构问题](#65-v5架构问题)

---

## 6.1 数据源选择问题

### Q1: 为什么不能用TdxQuant获取当天分钟线？

**A**: TdxQuant API的限制。`get_kline()`只支持历史K线，不支持当天分钟级别的实时数据。

**正确做法**：
- 交易时间：`XtQuant.get_market_kline()` (0.90ms)
- 非交易时间：`PyTdx2.get_kline()` (10-19ms)

### Q2: 为什么不能用XtQuant获取板块数据？

**A**: 两个原因导致不适用

1. **功能限制**：XtQuant板块功能较弱，不完整
2. **代码映射不兼容**：XtQuant的板块代码系统与项目使用的板块代码映射表不是同一套系统

**正确做法**：
- 交易时间：`TdxQuant.get_sectors()` (6.99ms, 586板块) 🔥
- 非交易时间：`PyTdx2.get_sectors()` (~15ms)

### Q3: 非交易时间应该用什么数据源？

**A**: 按场景选择

**场景1: 需要板块数据**
```
首选 PyTdx2 (~15ms) 🔥 真正在线获取
（TdxQuant盘后只能获取昨天历史，不推荐）
```

**场景2: 只需要个股K线**
```
QMT运行 → XtQuant (9-15ms) ✅ 略快
QMT未连接 → PyTdx2 (10-19ms) ✅
```

### Q4: 追求极致性能应该怎么配置？

**A**: 按场景配置：

| 业务 | 最优配置 | 性能 |
|------|----------|------|
| L1快照 | TdxQuant | 0.60ms |
| 当天分钟线 | XtQuant | 0.90ms |
| 板块数据 | TdxQuant | 6.99ms |
| 历史K线 | QLib | 7-10ms |

---

## 6.2 时间段问题

### Q5: 如何判断当前是否为交易时间？

**A**: 使用`TradingTimeDetectorV2`或自行判断：

```python
from datetime import datetime, time

def is_trading_time():
    now = datetime.now()
    current_time = now.time()
    weekday = now.weekday()

    # 周末
    if weekday >= 5:
        return False

    # 交易时间
    morning_start = time(9, 30)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)

    return ((morning_start <= current_time <= morning_end) or
            (afternoon_start <= current_time <= afternoon_end))
```

### Q6: 盘后时间（15:00-24:00）能用哪些数据源？

**A**:
- ✅ TdxQuant（可用）
- ✅ XtQuant（可用）
- ✅ PyTdx2（可用）
- ✅ QLib（可用）

### Q7: 周末/节假日能用哪些数据源？

**A**:
- ❌ TdxQuant（不可用）
- ❌ XtQuant（不可用）
- ✅ PyTdx2（唯一在线数据源）
- ✅ QLib（本地数据库）

---

## 6.3 性能优化问题

### Q8: 批量获取大量股票应该用什么？

**A**: 按数量分段：

| 股票数量 | 数据源 | 原因 |
|----------|--------|------|
| <100 | TdxQuant | 0.60ms最快 |
| 100-300 | XtQuant | 6ms缓存 |
| 300-800 | PyTdx2 | 分批获取 |
| >800 | PyTdx2 | 分批获取 |

### Q9: 如何减少数据获取延迟？

**A**: 多级缓存策略

```python
# 1. 内存缓存（最快）
cache = {}

# 2. Redis缓存（次快）
redis.get(key)

# 3. 本地数据库（QLib）
qlib.get_data()

# 4. 在线数据源（最慢）
adapter.get_data()
```

### Q10: PyTdx2性能如何优化？

**A**: 四大优化已集成：

1. ✅ 动态服务器选速（已启用）
2. ✅ Redis缓存（已启用）
3. ✅ 异步支持（FastAPI场景）
4. ✅ 连接池（大批量并发）

---

## 6.4 板块数据问题 ⭐

### Q11: 为什么板块数据特别重要？

**A**: 板块数据在后期的**风险预测**中有关键作用：

1. **板块轮动分析**
   - 识别热点板块
   - 预测板块切换时机
   - 捕捉板块龙头

2. **系统性风险监控**
   - 板块整体涨跌
   - 市场情绪指标
   - 风险传导路径

3. **投资组合优化**
   - 板块配置权重
   - 行业分散度
   - 风险敞口控制

**没有板块数据的风险预测是不完整的！**

### Q12: 如何获取完整的板块数据？

**A**: 只能用TdxQuant（交易时间）

```python
def get_complete_sector_data():
    """
    获取完整板块数据 - 586个板块

    ⚠️ XtQuant不支持板块
    ✅ TdxQuant: 6.99ms, 586板块
    """
    if is_trading_time():
        return tdxquant_adapter.get_sectors(limit=586)
    else:
        logger.warning("非交易时间板块数据不完整")
        return pytdx2_adapter.get_sectors(limit=100)
```

### Q13: 板块成分股数据如何获取？

**A**:

```python
# TdxQuant（交易时间）
members = tdxquant.get_sector_members("880001")  # 板块代码

# PyTdx2（非交易时间）
members = pytdx2.get_sector_members("880001")
```

---

## 6.5 数据时效性问题 ⭐

### Q14: XtQuant的`get_market_data_ex`能否获取当天数据？

**A**: 取决于QMT本地数据库状态

**实际情况**：
- `get_market_data_ex` **读取QMT本地缓存**，并非真正"在线获取"
- 非交易时间：数据截止到最近一次收盘
- 交易时间：取决于QMT是否自动更新当天数据

**验证测试**：[验证测试-get_market_data_ex数据时效性.md](../../../数据源能力研究/XtQuant/验证测试-get_market_data_ex数据时效性.md)
- 测试时间：2026-03-20 04:52（凌晨）
- 最新数据：2026-03-19 15:00（昨天收盘）
- 结论：只能读取本地缓存

**获取当天数据的正确方式**：

```python
from xtquant import xtdata
from datetime import datetime

# 方式1: 确保QMT自动更新（交易时间有效）
# 需要QMT软件运行且配置了自动下载

# 方式2: 手动下载当天数据
today = datetime.now().strftime('%Y%m%d')
xtdata.download_history_data(
    stock_code='600519.SH',
    period='5m',
    start_time=today,
    end_time=today
)

# 然后再读取
data = xtdata.get_market_data_ex(
    field_list=['time', 'open', 'high', 'low', 'close', 'volume'],
    stock_list=['600519.SH'],
    period='5m',
    start_time=int(today),
    end_time=int(today),
    dividend_type='none'
)
```

### Q15: 为什么非交易时间XtQuant数据截止到昨天？

**A**: 正常现象

**原因**：
- QMT只在交易时间更新数据
- 非交易时间（晚上、周末）没有新的交易数据
- 本地缓存自然截止到最近一次收盘

**解决方案**：
- 交易时间：让QMT自动更新，或手动下载
- 非交易时间：使用PyTdx2（24/7在线数据源）

---

## 6.6 性能优化问题

### Q16: XtQuant和PyTdx2性能相当，如何选择？

**A**: 都可以用，还可以并行分工！

**性能对比**：
| 数据源 | 当天分钟线 | 历史K线 | 条件 |
|--------|-----------|---------|------|
| XtQuant | 9-15ms | 9ms | 需要QMT运行 |
| PyTdx2 | 10-19ms | ~19ms | 24/7可用 |

**💡 并行分工策略**：

```python
async def get_minute_kline_parallel(symbols, period='5m'):
    """
    并行获取K线数据：XtQuant + PyTdx2分工

    适用场景：
    - 股票数量 > 50只
    - QMT已连接（可用XtQuant）
    - 追求整体吞吐量
    """
    from xtquant import xtdata
    from pytdx import TdxMdxApi

    # 按数量分配
    mid = len(symbols) // 2
    batch1 = symbols[:mid]   # XtQuant处理
    batch2 = symbols[mid:]   # PyTdx2处理

    # 并行执行
    results = await asyncio.gather(
        xtquant_get_kline(batch1, period),
        pytdx2_get_kline(batch2, period)
    )

    # 合并结果
    return merge_results(results)
```

**优势**：
- ✅ 提升整体吞吐量（2个数据源并行）
- ✅ 降低单点故障风险
- ✅ 充分利用QMT和在线数据源

---

## 6.7 V5架构问题

### Q17: V5场景化服务相比V4有什么优势？

**A**:

| 对比项 | V4 | V5 |
|--------|----|----|
| 代码组织 | 3777行单文件 | ~500行/服务模块 |
| 维护难度 | 困难 | 独立测试 |
| 扩展性 | 修改核心 | 添加新服务 |
| 优化策略 | 全局统一 | 场景专属 |

### Q18: 如何选择场景服务？

**A**:

| 需求 | 使用服务 |
|------|----------|
| 热点发现 | MonitoringService |
| 填补缺失 | IncrementalService |
| K线推送 | KlineService |
| 批量转换 | ConversionService |

### Q19: 如何实现双层路由？

**A**:

```python
# 第一层：板块 vs 非板块
if is_sector_data:
    return get_sector_adapter()

# 第二层：时间 + 类型
if is_trading_time():
    if count <= 100:
        return tdxquant
    else:
        return xtquant
else:
    return pytdx2
```

---

## 速查表

### 关键限制速查

| 限制 | 数据源 | 影响 |
|------|--------|------|
| ❌ 不支持当天分钟线 | TdxQuant | 当天分钟必须用XtQuant/PyTdx2 |
| ❌ 不支持板块数据 | XtQuant | 板块必须用TdxQuant/PyTdx2 |
| ❌ 仅交易时间 | TdxQuant/XtQuant | 非交易时间用PyTdx2 |
| ⚠️ 在线获取有数据量限制 | XtQuant | K线图够用，长期回测建议先下载 |

### 数据源选择速查

| 业务 | 交易时间 | 非交易时间 |
|------|----------|-----------|
| L1快照 | TdxQuant(0.60ms) | PyTdx2(10-19ms) |
| 当天分钟线 | XtQuant(0.90ms) | PyTdx2(10-19ms) |
| 历史K线 | QLib(7-10ms) | QLib(7-10ms) |
| **板块数据** | **TdxQuant(6.99ms)** 🔥 | PyTdx2(~15ms) |

---

## 总结

### 三大数据源定位

1. **TdxQuant** - 交易时间王者
   - L1快照：0.60ms最快
   - 板块数据：6.99ms，586板块
   - ❌ 不支持当天分钟线

2. **XtQuant** - 当天分钟线专家
   - 当天分钟线：0.90ms
   - 订阅功能：300股
   - ❌ 不支持板块数据

3. **PyTdx2** - 非交易时间救星
   - 24/7可用
   - 非交易时间唯一选择

### 板块数据的重要性 ⭐

板块数据在风险预测中有关键作用：
- 板块轮动分析
- 系统性风险监控
- 投资组合优化

**务必使用TdxQuant获取完整板块数据（586个板块）！**

---

**文档版本**: v3.0
**完整目录**: 返回 [README.md](README.md)
