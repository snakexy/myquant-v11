# V5 数据架构设计原则

> 来源: docs/项目设计/数据架构V5/

## 核心概念: L0-L5 数据分层

| 层级 | 名称 | 延迟 | 数据源 | 适用场景 |
|------|------|------|--------|----------|
| L0 | 订阅缓存 | <1ms | XtQuant订阅 | 实时推送、高频更新 |
| L1 | 实时快照 | 1-17ms | TdxQuant/XtQuant | 实时行情显示 |
| L2 | 历史摘要 | 7-17ms | LocalDB/XtQuant | 历史数据概览 |
| L3 | 完整K线 | 5-18ms | PyTdx/XtQuant/LocalDB | K线图表 |
| L4 | 财务数据 | 100-300ms | TdxQuant | 财务报表 |
| L5 | 板块/特色 | 10-500ms | TdxQuant/PyTdx | 板块分析 |

## 数据源能力矩阵

| 数据源 | L0 | L1 | L2 | L3 | L4 | L5 | 可用时间 |
|--------|----|----|----|----|----|----|----------|
| XtQuant | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | 交易+盘后 |《——盘后分钟数据一直很飘忽，需要再次测试！
| TdxQuant | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | 仅交易时间 |
| PyTdx | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | 24/7 |
| LocalDB | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | 24/7 |

## 数据源优先级 (按交易时间)

**交易时间 (9:30-15:00):**
```
L1实时: TdxQuant → XtQuant → PyTdx
L3K线:  TdxQuant → XtQuant → PyTdx → LocalDB
L5板块: TdxQuant → PyTdx
```

**非交易时间:**
```
L1实时: XtQuant → PyTdx (TdxQuant不可用)
L3K线:  PyTdx → XtQuant → LocalDB
```

## 场景化服务映射

| 前端场景 | 服务 | 数据层级 | 主要数据源 |
|----------|------|----------|------------|
| 实时K线 | SeamlessKlineService | L3 | LocalDB+实时补充 |
| 日内分钟线 | IntradayKlineService | L0+L3 | XtQuant订阅+在线获取 |
| 热点监控 | MonitoringService | L1+L5 | TdxQuant |
| 数据补全 | IncrementalService | L3 | PyTdx/XtQuant |
| 批量转换 | ConversionService | L2+L3 | LocalDB+PyTdx |

## 关键决策规则

1. **板块数据必须用 TdxQuant**（交易时间）或 PyTdx（非交易时间），XtQuant 不支持
2. **当天分钟线不支持 TdxQuant**，优先 XtQuant
3. **>300只股票批量查询** 必须用 PyTdx，其他数据源有数量限制
4. **复权计算在服务层统一处理**，所有适配器返回不复权原始数据

## 错误处理原则

```python
# 1. 优先尝试主数据源
try:
    return primary_adapter.get_data()
except DataSourceUnavailable:
    # 2. 降级到备用数据源
    return fallback_adapter.get_data()
except DataNotFound:
    # 3. 返回空结果，不抛异常
    return EmptyResult()
```

## 性能基准

| 操作 | 目标延迟 | 实际典型值 |
|------|----------|------------|
| L1 单股快照 | <10ms | 0.6ms (TdxQuant) |
| L3 单股K线(100条) | <20ms | 7-10ms (LocalDB) |
| L3 单股K线(800条) | <50ms | 15-19ms (PyTdx) |
| L5 板块列表 | <10ms | 6.99ms (TdxQuant) |

## 引用文档

详细设计见: `docs/项目设计/数据架构V5/`
- 01-数据源能力详解.md
- 03-业务场景决策矩阵.md
- 04-场景服务配置指南.md
