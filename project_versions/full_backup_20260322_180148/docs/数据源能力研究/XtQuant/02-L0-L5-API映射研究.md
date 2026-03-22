# XtQuant L0-L5 API映射研究

> 研究目标：为每个数据级别找到正确的API函数和参数
>
> 研究日期: 2026-02-05

## L0: 订阅缓存

### 数据描述
已订阅股票的实时行情缓存（毫秒级响应）

### API函数

#### 1. subscribe_quote() - 订阅行情
```python
xtdata.subscribe_quote(
    stock_code='600519.SH',
    period='1d',
    count=0
)
```

#### 2. get_full_tick() - 获取订阅的实时行情
```python
data = xtdata.get_full_tick(['600519.SH', '000001.SZ'])
```

**返回格式**:
```python
{
    '600519.SH': {
        'lastPrice': 1525.0,
        'volume': 109123,
        'amount': 16444350000,
        ...
    }
}
```

**性能**: ~1ms（从缓存读取）

---

## L1: 实时快照

### 数据描述
当前时刻的完整行情快照（需要先订阅）

### API函数

#### 1. get_full_kline() - 最新K线快照
```python
data = xtdata.get_full_kline(
    field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
    stock_list=['600519.SH'],
    period='1d',
    count=1,
    dividend_type='none',
    fill_data=True
)
```

**用途**: 获取最新一根K线的实时数据（盘中更新）

#### 2. get_market_data() - 实时行情
```python
data = xtdata.get_market_data(
    field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
    stock_list=['600519.SH'],
    period='1d',
    start_time='',
    end_time='',
    count=1,
    dividend_type='none',
    fill_data=True
)
```

**注意**: 可能需要先调用 subscribe_quote()

---

## L2: 历史快照

### 数据描述
历史K线数据摘要（最近N天的数据）

### API函数

#### get_market_data_ex() - 在线获取历史K线 ⭐核心
```python
data = xtdata.get_market_data_ex(
    field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
    stock_list=['600519.SH'],
    period='1d',
    count=30,  # 获取最近30天
    dividend_type='none'
)
```

**返回格式**:
```python
{
    '600519.SH': DataFrame
}
```

**性能**: ~100-500ms（在线获取）

**限制**:
- ✅ 日K线：无限制
- ⚠️ 分钟线：16天

---

## L3: 完整数据

### 数据描述
完整的历史K线数据（可跨年）

### API函数

#### 1. download_history_data() - 下载历史数据到本地
```python
xtdata.download_history_data(
    stock_code='600519.SH',
    period='1d',
    start_time='20200101',
    end_time='20241231'
)
```

**说明**:
- 下载到本地缓存
- 首次使用必须先下载
- 后续可直接读取

#### 2. get_market_data_ex() - 读取本地数据
```python
data = xtdata.get_market_data_ex(
    field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
    stock_list=['600519.SH'],
    period='1d',
    start_time=20200101,  # 具体日期
    end_time=20241231,
    count=0,  # count=0表示使用时间范围
    dividend_type='none'
)
```

**策略**:
1. 首次：调用 download_history_data() 下载
2. 后续：调用 get_market_data_ex() 读取本地缓存

#### 3. get_market_data_list() - 批量获取多股票
```python
data = xtdata.get_market_data_list(
    stock_list=['600519.SH', '000001.SZ'],
    period='1d',
    field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
    start_time=20200101,
    end_time=20241231,
    dividend_type='none',
    fill_data=True
)
```

**返回格式**: 与 get_market_data_ex 相同

---

## L3.5: 公司治理数据

### 数据描述
股东信息、股本结构等

### API函数

#### get_instrument_detail() - 股票基本信息
```python
detail = xtdata.get_instrument_detail('600519.SH')
```

**返回格式**:
```python
{
    'InstrumentName': '贵州茅台',
    'ExchangeID': 'SH',
    'InstrumentID': '600519',
    ...
}
```

#### get_stock_list_in_sector() - 板块成分股
```python
stocks = xtdata.get_stock_list_in_sector('沪深300')
```

**返回**: ['600000.SH', '000001.SZ', ...]

---

## L4: 财务数据

### 数据描述
财务报表、财务指标

### API函数

#### get_financial_data() - 获取财务数据
```python
data = xtdata.get_financial_data(
    stock_list=['600519.SH'],
    table_list=['Balance', 'Profit', 'CashFlow', 'Growth'],
    report_date='2024-03-31',
    start_time=None,
    end_time=None
)
```

**返回格式**:
```python
{
    '600519.SH': DataFrame  # 财务数据
}
```

**注意**: 可能需要付费权限

---

## 关键参数对照表

### 1. period (周期)

| 数据级别 | period值 | 说明 |
|---------|----------|------|
| L0-L2 | 'tick' | 分笔 |
| L1-L3 | '1m', '5m', '15m', '30m', '60m' | 分钟K线 |
| L1-L3 | '1d' | 日K线 |
| L1-L3 | '1w', '1M' | 周K线、月K线 |

### 2. dividend_type (复权类型)

| 值 | 含义 | 类型 |
|---|------|------|
| 'none' | 不复权 | 字符串 ✅ |
| 'front' | 前复权 | 字符串 ✅ |
| 'back' | 后复权 | 字符串 ✅ |
| 0, 1, 2 | ❌ 数字会报错 | - |

### 3. 时间参数

| 参数 | 类型 | 示例 | 说明 |
|-----|------|------|------|
| count | int | 16 | 获取最新N条 |
| start_time | int | 20200101 | 起始日期 |
| end_time | int | 20241231 | 结束日期 |
| start_time | str | '' | 空字符串=不限制 |

---

## 数据获取流程设计

### 场景1: 获取最新16条日K线 (L2)

```python
# ✅ 直接在线获取
data = xtdata.get_market_data_ex(
    field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
    stock_list=['600519.SH'],
    period='1d',
    count=16,
    dividend_type='none'
)
```

### 场景2: 获取2024全年日K线 (L3)

```python
# 策略1: 先下载，再读取
xtdata.download_history_data(
    stock_code='600519.SH',
    period='1d',
    start_time='20240101',
    end_time='20241231'
)

data = xtdata.get_market_data_ex(
    field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
    stock_list=['600519.SH'],
    period='1d',
    start_time=20240101,
    end_time=20241231,
    count=0,
    dividend_type='none'
)
```

### 场景3: 获取120条5分钟K线 (L3 - 可能超过16天)

```python
# ⚠️ 120*5分钟 = 600分钟 = 10小时 < 16天，可以直接获取
data = xtdata.get_market_data_ex(
    field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
    stock_list=['600519.SH'],
    period='5m',
    count=120,
    dividend_type='none'
)

# 如果超过16天（如count=2000），需要先下载历史数据
```

### 场景4: 实时行情 (L0/L1)

```python
# 1. 先订阅
xtdata.subscribe_quote(
    stock_code='600519.SH',
    period='1d',
    count=0
)

# 2. 获取订阅缓存（~1ms）
tick_data = xtdata.get_full_tick(['600519.SH'])

# 3. 获取最新K线快照
kline_snapshot = xtdata.get_full_kline(
    field_list=['open', 'high', 'low', 'close', 'volume', 'amount'],
    stock_list=['600519.SH'],
    period='1d',
    count=1
)
```

---

## 待验证项目

### L0-L1: 订阅推送
- [x] subscribe_quote() 的订阅机制
- [ ] 推送回调函数注册
- [ ] 订阅缓存更新频率
- [x] 订阅上限（单实例可订阅500只，非300只）

### L2: 历史快照
- [x] get_market_data_ex() 基本用法
- [x] count参数行为
- [x] dividend_type参数类型（必须用字符串'none'/'front'/'back'）
- [ ] 分钟线16天限制验证
- [x] start_time/end_time参数行为（必须用空字符串''）

### L3: 完整数据
- [x] download_history_data() 下载速度（约50ms）
- [ ] 本地缓存位置
- [ ] 缓存数据更新机制
- [ ] 大量数据下载（1000+股票）

### L3.5-L4: 其他数据
- [ ] get_financial_data() 权限要求
- [ ] 财务数据完整性
- [ ] 股东信息获取

---

## 下一步测试脚本

1. `test_l0_subscription.py` - 测试订阅和推送
2. `test_l1_snapshot.py` - 测试实时快照
3. `test_l2_history.py` - 测试历史快照（已测试）
4. `test_l3_full.py` - 测试完整数据获取
5. `test_l35_company.py` - 测试公司数据
6. `test_l4_financial.py` - 测试财务数据
