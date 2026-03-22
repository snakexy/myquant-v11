# PyTdx2 数据源能力研究

> **研究日期**: 2026-03-20
> **研究状态**: ✅ 已验证并集成
> **版本**: v1.0

## 概述

PyTdx2 是通达信数据接口的优化版本，相比原版 PyTdx 有以下改进：

- 连接后自动调用 `setup()` 进行初始化握手，提升稳定性
- 预定义最优服务器列表（113个服务器）
- 更好的线程安全机制
- 内置心跳机制保持长连接
- 支持服务器 fallback

## 核心API列表

| API | 说明 | 支持情况 |
|-----|------|----------|
| `get_security_quotes()` | 实时快照 | ✅ 支持 |
| `get_security_bars()` | K线数据 | ✅ 支持 |
| `get_index_bars()` | 指数K线 | ✅ 支持 |
| `get_xdxr_info()` | 除权除息 | ✅ 支持 |
| `get_finance_info()` | 财务数据 | ✅ 支持 |
| `get_security_list()` | 股票列表 | ✅ 支持 |
| `get_security_count()` | 股票数量 | ✅ 支持 |
| `get_minute_time_data()` | 分时数据 | ✅ 支持 |
| `get_history_minute_time_data()` | 历史分时 | ✅ 支持 |
| `get_transaction_data()` | 分笔成交 | ✅ 支持 |
| `get_history_transaction_data()` | 历史分笔 | ✅ 支持 |
| `get_company_info_category()` | 公司信息目录 | ✅ 支持 |
| `get_company_info_content()` | 公司信息内容 | ✅ 支持 |
| `get_block_info()` | 板块信息 | ✅ 支持 |
| `get_k_data()` | 日线数据获取 | ✅ 支持 |

## L0-L5 能力矩阵

| 层级 | 说明 | 支持情况 | 备注 |
|------|------|----------|------|
| **L0** | 订阅推送 | ❌ 不支持 | 轮询模式，无订阅功能 |
| **L1** | 实时快照 | ✅ 支持 | ~10ms 批量获取 |
| **L2** | 历史摘要 | ✅ 支持 | 基于K线计算 |
| **L3** | K线数据 | ✅ 支持 | 最多800条/请求 |
| **L3.2** | 分笔成交 | ✅ 支持 | 最多2000条/请求 |
| **L4** | 财务数据 | ✅ 支持 | 37个字段 |
| **L5** | 板块数据 | ✅ 支持 | 自选/分类/概念板块 |

## K线周期支持

| 周期 | category 值 | 说明 |
|------|-------------|------|
| 1分钟 | 8 | KLINE_TYPE_1MIN |
| 5分钟 | 0 | KLINE_TYPE_5MIN |
| 15分钟 | 1 | KLINE_TYPE_15MIN |
| 30分钟 | 2 | KLINE_TYPE_30MIN |
| 60分钟 | 3 | KLINE_TYPE_1HOUR |
| 日线 | 9 | KLINE_TYPE_RI_K (推荐) |
| 周线 | 5 | KLINE_TYPE_WEEKLY |
| 月线 | 6 | KLINE_TYPE_MONTHLY |

## 复权功能

### 除权除息信息 API

`get_xdxr_info(market, code)` 返回除权除息信息，包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| year | int | 年份 |
| month | int | 月份 |
| day | int | 日期 |
| category | int | 类别（1=除权除息） |
| name | str | 类别名称 |
| fenhong | float | 分红（元/10股） |
| songzhuangu | float | 送股（股/10股） |
| peigu | float | 配股（股/10股） |
| peigujia | float | 配股价（元/股） |
| panqianliutong | float | 盘前流通 |
| panhouliutong | float | 盘后流通 |
| qianzongguben | float | 前总股本 |
| houzongguben | float | 后总股本 |

### 除权类别

| category | 名称 | 说明 |
|----------|------|------|
| 1 | 除权除息 | 分红、送股、配股 |
| 2 | 送配股上市 | 送股/配股上市日 |
| 5 | 股本变化 | 股本变动 |
| 11 | 扩缩股 | 扩股/缩股 |

### 前复权计算

PyTdx2 实现了完整的前复权计算，公式：

```
除权后理论价格 = (原收盘价 + 配股比例 × 配股价 - 每股分红) / (1 + 送股比例 + 配股比例)

复权因子 = 除权后价格 / 除权前价格
```

## 数据限制

| 限制类型 | 限制值 | 说明 |
|----------|--------|------|
| K线数据 | 800条/请求 | 需要分批获取更多数据 |
| 分笔成交 | 2000条/请求 | MAX_TRANSACTION_COUNT |
| 无频率限制 | 无 | 可快速连续调用 |
| 无并发限制 | 无 | 支持多线程 |

## 性能数据（实测2026-03-20）

| 操作 | 性能 | 说明 |
|------|------|------|
| 单股快照 | 10.50ms | 实时行情 |
| 批量快照 | 10.07ms (5只) | 2.01ms/股 |
| K线 100条 | 10.50-13.00ms | 各周期 |
| K线 500条 | 15.00ms | 日线 |
| K线 800条 | 19.00ms | 最大量 |
| 分笔成交 | 12.00ms | 100条 |
| 财务数据 | 12.00ms | 37字段 |

**评估**: 比TdxQuant(0.60ms)慢约15-20倍，但功能完整，可作为备用。

## 与其他数据源对比

| 特性 | PyTdx2 | XtQuant | TdxQuant |
|------|--------|---------|----------|
| **L0 订阅** | ❌ | ✅ 0.5ms (300只) | ⚠️ |
| **L1 快照** | 10.50ms | 0.90ms | 0.60ms |
| **L3 K线在线** | 10-19ms(每次在线) | 720ms下载后6ms读缓存 | 0.60ms(每次在线) |
| **L3 说明** | 纯在线，每次都获取 | 首次下载+后续读本地缓存 | 纯在线 |
| **L4 财务** | ✅ 37字段 | ⚠️ 需VIP | ✅ 46字段 |
| **板块数据** | ✅ | ❌ | ✅ 586板块 |
| **依赖** | 无 | MiniQMT | 通达信 |
| **24/7可用** | ✅ 完全 | ✅ tick仅交易时 | ⚠️ 非交易时无在线数据 |

## 适用场景

### 🟢 最佳场景（不可替代）

| 场景 | PyTdx2 | TdxQuant | XtQuant |
|------|--------|----------|---------|
| **离线环境** | ✅ 唯一选择 | ❌ | ❌ |
| **无MiniQMT/通达信** | ✅ 唯一选择 | ❌ | ❌ |
| **非交易时间** | ✅ | ❌ | ✅ 优先 |
| **周末/节假日** | ✅ | ❌ | ✅ 优先 |

### ⚠️ 交易时间对比

| 操作 | PyTdx2 | TdxQuant | XtQuant | 说明 |
|------|--------|----------|---------|------|
| L0 订阅 | ❌ | - | **0.5ms** | XtQuant订阅最快 |
| L1 快照 | 10.50ms | **0.60ms** | 0.90ms | TdxQuant最快 |
| L3 K线在线 | 10-19ms(800条) | **0.60ms** | ~500ms(22天限制) | TdxQuant最快 |
| L3 K线历史 | 需分批获取 | 1088条/次 | 下载后无限制 | 各有优势 |

**结论**:

| 场景 | 推荐数据源 | 说明 |
|------|-----------|------|
| 交易时间 | XtQuant缓存(6ms) → TdxQuant(0.60ms) → PyTdx2(10ms) | XtQuant实时更新 |
| 非交易时间 | PyTdx2(10-19ms) → XtQuant缓存(6ms) | PyTdx2数据更新 |
| 已下载历史 | XtQuant缓存(6ms) | 最快 |
| 离线环境 | PyTdx2 ✅ | 唯一选择 |

## 代码集成

### 已集成位置

- **适配器**: `backend/data/adapters/pytdx_adapter.py`
- **配置**: `backend/data/adapters/pytdx2_config.py`
- **路由**: `backend/data/core/data_source_router.py`
- **配置文件**: `backend/data/config/data_source_config.py`

### 使用示例

```python
from data.adapters.pytdx_adapter import PyTdxAdapter

# 创建适配器
adapter = PyTdxAdapter()

# 获取实时快照
quotes = adapter.get_realtime_quote(['600000', '000001'])

# 获取K线数据（支持前复权）
kline = adapter.get_kline_data(
    symbols=['600000'],
    period='day',
    count=100,
    adjust_type='front'  # 前复权
)

# 获取财务数据
financial = adapter.get_financial_data(['600000'])

# 获取股票列表
stocks = adapter.get_stock_list(market=1)
```

## 优化建议

### 已实现的优化 ✅

1. **服务器列表** - 使用预定义最优服务器
2. **心跳机制** - 保持长连接
3. **Fallback机制** - 自动切换备用服务器
4. **重试机制** - API调用失败自动重试
5. **前复权计算** - 完整的除权除息处理

### 未来优化方向

1. **连接池** - 多连接并发提升性能
2. **本地缓存** - 缓存除权信息减少请求
3. **智能路由** - 根据服务器延迟自动选择

## 测试脚本

| 脚本 | 说明 |
|------|------|
| `test_01_l0_l5_capability_matrix.py` | L0-L5能力矩阵测试 |
| `test_02_adjustment_capability.py` | 复权功能测试 |

## 参考文档

- [PyTdx2 GitHub](https://github.com/Shawda/pytdx2)
- [数据源配置](../../../data/config/data_source_config.py)
- [适配器实现](../../../data/adapters/pytdx_adapter.py)

## 总结

### 核心价值：🟢 24/7可用

**TdxQuant非交易时间无法获取数据，PyTdx2是主要选择。**

### 优势 ⭐
1. ✅ **24/7可用** - 非交易时间、周末、节假日都能获取数据
2. ✅ **无依赖** - 不需要安装其他软件
3. ✅ **完整数据** - 支持K线、财务、板块等
4. ✅ **前复权** - 完整的除权除息计算
5. ✅ **性能合格** - 500条K线 15ms

### 劣势 ⚠️
1. ⚠️ **交易时间较慢** - 比TdxQuant慢15-25倍
2. ❌ **无订阅推送** - 轮询模式
3. ⚠️ **K线限制** - 每次最多800条

### 定位
| 场景 | 优先数据源 |
|------|-----------|
| 交易时间 | TdxQuant → XtQuant → PyTdx2 |
| 非交易时间 | XtQuant → PyTdx2 |
| 离线环境 | PyTdx2 ✅ 唯一选择 |

---

**研究完成时间**: 2026-03-20
**集成状态**: ✅ 已完全集成
**核心价值**: 🟢 **24/7可用** - 非交易时间主要选择
