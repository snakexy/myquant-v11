# PyTdx2 数据源能力研究 - 索引

> **最后更新**: 2026-03-20
> **研究状态**: ✅ 已验证并集成

## 文档列表

### 核心文档

| 文档 | 说明 | 状态 |
|------|------|------|
| [README.md](./README.md) | 总览文档 | ✅ 完成 |

### 测试脚本

| 脚本 | 说明 | 状态 |
|------|------|------|
| [test_01_l0_l5_capability_matrix.py](./test_01_l0_l5_capability_matrix.py) | L0-L5能力矩阵测试 | ✅ 8/8通过 |
| [test_02_adjustment_capability.py](./test_02_adjustment_capability.py) | 复权功能测试 | ✅ 验证通过 |

## 研究结论

### ✅ 已验证功能

1. **L1 实时快照** - ~10ms 批量获取
2. **L3 K线数据** - 支持所有周期（1m/5m/15m/30m/60m/日/周/月）
3. **L3.2 分笔成交** - 最多2000条/请求
4. **L4 财务数据** - 37个字段
5. **L5 板块数据** - 自选/分类/概念板块
6. **复权功能** - 完整的前复权计算

### ❌ 不支持功能

1. **L0 订阅推送** - 轮询模式，无事件驱动

## 集成状态

- **适配器**: `backend/data/adapters/pytdx_adapter.py` (已使用PyTdx2)
- **配置**: `backend/data/adapters/pytdx2_config.py`
- **路由**: `backend/data/core/data_source_router.py`
- **数据源配置**: `backend/data/config/data_source_config.py`

## 快速开始

```python
from data.adapters.pytdx_adapter import PyTdxAdapter

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
```

## 相关文档

- [XtQuant 研究文档](../XtQuant/README.md)
- [TdxQuant 研究文档](../TdxQuant/README.md)
- [数据源配置文档](../../../data/config/data_source_config.py)
