# XtQuant 原生聚合功能研究

> 目的: 研究XtQuant自带的聚合和统计功能
> 避免重复造轮子，优先使用官方功能

---

## XtQuant 可能提供的聚合功能

### 1. 技术指标计算

XtQuant可能提供的技术指标函数（需要验证）：

```python
# 可能存在的API
from xtquant import xtdata

# 移动平均线
ma_data = xtdata.get_ma_data(
    stock_list=['600519.SH'],
    period='1d',
    ma_type='SMA',  # 简单移动平均
    ma_period=5
)

# MACD指标
macd_data = xtdata.get_macd(
    stock_code='600519.SH',
    period='1d',
    start_time=20240101,
    end_time=20241231
)

# KDJ指标
kdj_data = xtdata.get_kdj(...)

# RSI指标
rsi_data = xtdata.get_rsi(...)
```

**需要验证**:
- [ ] XtQuant是否提供技术指标计算
- [ ] 支持哪些指标
- [ ] 参数格式是什么

---

### 2. 市场统计数据

可能的市场统计API：

```python
# 涨跌统计
market_stats = xtdata.get_market_stats(
    market='SH',  # 上海市场
    date='20240205'
)

# 返回可能包括：
# {
#     'up_count': 1200,      # 上涨股票数
#     'down_count': 800,     # 下跌股票数
#     'flat_count': 100,     # 平盘股票数
#     'limit_up_count': 20,  # 涨停股票数
#     'limit_down_count': 5  # 跌停股票数
# }

# 板块涨跌排名
sector_ranking = xtdata.get_sector_ranking(
    sector_type='industry',  # 行业板块
    sort_by='change_pct',    # 按涨跌幅排序
    top_n=10
)
```

**需要验证**:
- [ ] 是否有市场统计API
- [ ] 支持哪些统计维度
- [ ] 排序功能是否可用

---

### 3. 多周期自动获取

可能支持一次获取多周期数据：

```python
# 一次获取多周期K线
multi_period_data = xtdata.get_multi_period_kline(
    stock_code='600519.SH',
    periods=['1m', '5m', '15m', '30m', '60m', '1d'],
    count=100
)

# 返回格式：
# {
#     '1m': DataFrame(...),
#     '5m': DataFrame(...),
#     '1d': DataFrame(...)
# }
```

**需要验证**:
- [ ] 是否支持多周期同时获取
- [ ] 性能如何
- [ ] 参数格式

---

### 4. 分时数据聚合

直接获取分时数据（已聚合）：

```python
# 获取分时数据
intraday_data = xtdata.get_intraday_data(
    stock_code='600519.SH',
    period='1m'  # 1分钟聚合
)

# 可能返回格式：
# {
#     'time': ['09:30', '09:31', ..., '15:00'],
#     'price': [100.5, 100.6, ...],
#     'volume': [1000, 1200, ...],
#     'avg_price': [100.5, 100.55, ...]  # 均价
# }
```

---

## 需要研究验证的API

### 高优先级

1. **技术指标函数**
   - `xtdata.get_ma_data()`
   - `xtdata.get_macd()`
   - `xtdata.get_kdj()`
   - `xtdata.get_rsi()`
   - `xtdata.get_boll()`

2. **市场统计函数**
   - `xtdata.get_market_stats()`
   - `xtdata.get_sector_stats()`
   - `xtdata.get_stock_ranking()`

3. **多周期函数**
   - `xtdata.get_multi_period_kline()`
   - `xtdata.get_intraday_data()`

### 中优先级

4. **板块统计**
   - `xtdata.get_sector_performance()`
   - `xtdata.get_industry_ranking()`

5. **涨跌统计**
   - `xtdata.get_up_down_stats()`
   - `xtdata.get_limit_up_stocks()`

---

## 测试脚本

让我创建测试脚本验证这些功能：<tool_call>Write<arg_key>content</arg_key><arg_value>"""
测试XtQuant原生聚合功能

验证XtQuant是否自带聚合和统计功能
"""
import sys
sys.path.insert(0, 'e:\\MyQuant_v10.0.0\\backend')

from xtquant import xtdata
import inspect

print("="*80)
print("XtQuant 原生聚合功能测试")
print("="*80)
print()

# ===== 测试1: 查找所有包含'ma'、'macd'等技术指标的函数 =====
print("[测试1] 查找技术指标相关函数")
print("-"*80)

all_functions = [name for name in dir(xtdata) if not name.startswith('_')]

indicator_keywords = ['ma', 'macd', 'kdj', 'rsi', 'boll', 'atr', 'indicator']
indicator_functions = []

for func_name in all_functions:
    lower_name = func_name.lower()
    if any(keyword in lower_name for keyword in indicator_keywords):
        indicator_functions.append(func_name)

if indicator_functions:
    print(f"找到 {len(indicator_functions)} 个技术指标相关函数:")
    for func in indicator_functions:
        print(f"  - {func}")
else:
    print("未找到技术指标相关函数")
    print("可能的技术指标函数名:")
    print("  - get_ma_data")
    print("  - get_macd")
    print("  - get_kdj")
    print("  - 或其他命名")

print()

# ===== 测试2: 查找统计相关函数 =====
print("[测试2] 查找统计相关函数")
print("-"*80)

stats_keywords = ['stat', 'rank', 'summary', 'aggregate', 'performance']
stats_functions = []

for func_name in all_functions:
    lower_name = func_name.lower()
    if any(keyword in lower_name for keyword in stats_keywords):
        stats_functions.append(func_name)

if stats_functions:
    print(f"找到 {len(stats_functions)} 个统计相关函数:")
    for func in stats_functions:
        print(f"  - {func}")
else:
    print("未找到统计相关函数")

print()

# ===== 测试3: 尝试调用可能的聚合函数 =====
print("[测试3] 尝试调用可能的聚合函数")
print("-"*80)

test_functions = [
    'get_ma_data',
    'get_market_stats',
    'get_multi_period_kline',
    'get_intraday_data',
]

for func_name in test_functions:
    if hasattr(xtdata, func_name):
        print(f"✅ {func_name} 存在")
        func = getattr(xtdata, func_name)
        print(f"   函数签名: {inspect.signature(func) if callable(func) else 'N/A'}")
    else:
        print(f"❌ {func_name} 不存在")

print()

# ===== 测试4: get_market_data_ex的聚合参数 =====
print("[测试4] get_market_data_ex是否有聚合参数")
print("-"*80)

import inspect
sig = inspect.signature(xtdata.get_market_data_ex)
print(f"get_market_data_ex 参数:")
for param_name, param in sig.parameters.items():
    print(f"  {param_name}: {param.annotation if param.annotation != inspect.Parameter.empty else 'Any'}")

# 检查是否有聚合相关参数
params = list(sig.parameters.keys())
agg_params = [p for p in params if 'agg' in p.lower() or 'group' in p.lower()]

if agg_params:
    print(f"\n找到聚合相关参数: {agg_params}")
else:
    print("\n未找到明显的聚合参数")

print()

# ===== 测试5: 检查数据返回格式中是否包含聚合数据 =====
print("[测试5] 检查返回数据是否包含聚合信息")
print("-"*80)

symbol = '600519.SH'

try:
    # 获取K线数据
    data = xtdata.get_market_data_ex(
        field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
        stock_list=[symbol],
        period='1d',
        count=10
    )

    if symbol in data:
        df = data[symbol]
        print(f"K线数据列名: {list(df.columns)}")

        # 检查是否有聚合字段
        agg_columns = [col for col in df.columns if any(
            keyword in col.lower() for keyword in ['ma', 'avg', 'sum', 'stat']
        )]

        if agg_columns:
            print(f"发现聚合字段: {agg_columns}")
        else:
            print("未发现聚合字段（纯OHLCV数据）")

except Exception as e:
    print(f"获取数据失败: {e}")

print()
print("="*80)
print("结论：需要根据测试结果更新文档")
print("="*80)
