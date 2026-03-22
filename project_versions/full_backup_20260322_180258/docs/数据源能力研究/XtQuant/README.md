# XtQuant 数据能力测试指南

## 测试套件概述

本测试套件系统性地验证 XtQuant 在 L0-L5 各个数据级别的能力，为后续适配器设计和数据获取策略提供实测依据。

## 测试文件清单

| 测试文件 | 数据级别 | 测试目标 | 预计耗时 |
|---------|---------|---------|---------|
| [test_l0_subscription.py](test_l0_subscription.py) | L0 订阅缓存 | 订阅机制、缓存性能、推送回调 | ~10秒 |
| [test_l1_snapshot.py](test_l1_snapshot.py) | L1 实时快照 | 最新K线、实时数据更新 | ~15秒 |
| [test_l2_history.py](test_l2_history.py) | L2 历史快照 | 在线获取、分钟线限制 | ~20秒 |
| [test_l3_full.py](test_l3_full.py) | L3 完整数据 | 历史下载、本地读取 | ~60秒 |
| [test_l35_company.py](test_l35_company.py) | L3.5 公司数据 | 股票信息、板块成分股 | ~10秒 |
| [test_l4_financial.py](test_l4_financial.py) | L4 财务数据 | 财务报表、报告期 | ~15秒 |
| [run_all_tests.py](run_all_tests.py) - 全部 | 完整测试套件 | 一键运行所有测试 | ~130秒 |

## 快速开始

### 方式1: 运行所有测试（推荐）

```bash
cd docs/数据源能力研究/XtQuant
python run_all_tests.py
```

### 方式2: 单独运行某个测试

```bash
cd docs/数据源能力研究/XtQuant

# 测试订阅缓存
python test_l0_subscription.py

# 测试实时快照
python test_l1_snapshot.py

# 测试历史快照
python test_l2_history.py
```

## 测试目标详解

### L0: 订阅缓存测试

**验证内容**:
- ✅ `subscribe_quote()` 订阅功能
- ✅ `get_full_tick()` 缓存读取性能（目标: ~1ms）
- ✅ 批量订阅和批量获取
- ⚠️ 订阅上限（单实例300只？）

**关键指标**:
```python
# 性能目标
缓存读取: < 5ms
批量获取(10只): < 50ms
```

### L1: 实时快照测试

**验证内容**:
- ✅ `get_full_kline()` 最新K线快照
- ✅ `get_market_data()` 实时行情
- ✅ 实时数据更新频率

**关键指标**:
```python
# 性能目标
单股票快照: < 500ms
实时更新: 盘中每3秒
```

### L2: 历史快照测试

**验证内容**:
- ✅ `get_market_data_ex()` 在线获取
- ✅ 不同周期（1d, 5m, 1m）
- ⚠️ **分钟线16天限制验证**
- ✅ count参数行为

**关键验证**:
```python
# 日K线
count=30  # ✅ 应该成功

# 分钟线
count=120, period='5m'   # 120*5=600分钟=10小时 < 16天 ✅
count=240, period='1m'   # 240*1=240分钟=4小时 < 16天 ✅
count=2000, period='5m'  # 2000*5=10000分钟=166小时 < 16天 ⚠️
```

### L3: 完整数据测试

**验证内容**:
- ✅ `download_history_data()` 历史下载
- ✅ `get_market_data_ex()` 本地读取
- ✅ 大时间范围（2020-2024，5年）
- ✅ 批量多股票获取

**关键验证**:
```python
# 下载速度
1年日K线: < 10秒
5年日K线: < 30秒

# 本地读取速度
1年日K线: < 100ms
5年日K线: < 200ms
```

### L3.5: 公司数据测试

**验证内容**:
- ✅ `get_instrument_detail()` 股票基本信息
- ✅ `get_stock_list_in_sector()` 板块成分股
- ✅ 常见板块支持（沪深300、中证500等）

**关键数据**:
```python
# 股票信息字段
InstrumentName  # 股票名称
ExchangeID      # 交易所
InstrumentID    # 股票代码
```

### L4: 财务数据测试

**验证内容**:
- ✅ `get_financial_data()` 财务报表
- ✅ 支持的表类型（Balance, Profit, CashFlow, Growth）
- ✅ 不同报告期
- ⚠️ 付费权限要求

**关键数据**:
```python
# 支持的财务表
Balance    # 资产负债表
Profit     # 利润表
CashFlow   # 现金流量表
Growth     # 增长数据

# 报告期格式
'2024-03-31'  # 季报
'2023-12-31'  # 年报
```

## 测试结果记录

测试完成后，请将结果记录到 [01-参数实测报告.md](01-参数实测报告.md)：

### 记录格式

```markdown
## 测试结果 (2026-02-05)

### L0: 订阅缓存
- [x] 订阅成功
- [x] 缓存读取性能: 2ms ✅
- [ ] 订阅上限: 待测试

### L1: 实时快照
- [x] get_full_kline() 成功
- [x] 性能: 350ms ✅

### L2: 历史快照
- [x] 日K线 count=30: 成功 ✅
- [x] 5分钟K线 count=120: 成功 ✅
- [ ] 5分钟K线 count=2000: 待测试
- [ ] 1分钟K线 count=240: 待测试

...
```

## 已知问题

### 问题1: dividend_type 类型错误 🔴

**位置**: `backend/data/adapters/xtquant_dual_instance_adapter.py:842, 918`

**错误**:
```python
# ❌ 错误
dividend_type_map = {"none": 0, "front": 1, "back": 2}
```

**修复**:
```python
# ✅ 正确
dividend_type_map = {"none": 'none', "front": 'front', "back": 'back'}
```

**影响**: 批量获取K线功能完全不可用

**优先级**: 🔴 高

## 下一步行动

1. **运行完整测试套件**
   ```bash
   python run_all_tests.py
   ```

2. **记录测试结果**
   - 更新 `01-参数实测报告.md`
   - 记录每个API的实际行为
   - 记录性能数据

3. **识别限制和边界**
   - 分钟线16天限制验证
   - 订阅上限测试
   - 财务数据权限确认

4. **对比其他数据源**
   - PyTdx 能力测试
   - 本地数据库能力
   - 生成对比报告

5. **更新适配器设计**
   - 根据实测结果修复bug
   - 优化参数传递
   - 实现最佳实践

## 参考资料

- [XtQuant官方文档](http://dict.thinktrader.net/nativeApi/start_now.html)
- [02-L0-L5-API映射研究.md](02-L0-L5-API映射研究.md)
- [01-参数实测报告.md](01-参数实测报告.md)

## 贡献

发现新的API或测试用例，请：
1. 创建对应的测试脚本
2. 更新本文档
3. 记录测试结果

---

**重要**: 在进行大规模开发之前，**必须完成所有测试并记录结果**！
