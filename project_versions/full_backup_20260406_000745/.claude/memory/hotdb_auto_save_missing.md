# HotDB 自动回写功能缺失

## 问题描述

当 KlineService 从在线源获取到新数据时，设计上应该自动回写到 HotDB 数据库，但当前实现没有做到。

## 当前行为

```
KlineService.get_historical_kline()
  ├─ HotDB (快速通道)
  ├─ LocalDB (冷数据库)  
  └─ 在线源 (pytdx/xtquant) → 返回数据，但❌没有保存到 HotDB
```

## 期望行为

```
KlineService.get_historical_kline()
  ├─ HotDB (快速通道)
  ├─ LocalDB (冷数据库)
  └─ 在线源 (pytdx/xtquant) → ✅保存到 HotDB → 返回数据
```

## 影响范围

- 周线/月线数据：每次都要从在线源获取（pytdx 连接慢 ~5秒）
- 自选股新数据：无法缓存到 HotDB 快速通道
- 违背了"HotDB 作为快速热数据库"的设计初衷

## 待实现

1. **KlineService 添加回写逻辑**
   - 在 `get_historical_kline()` 第3层（在线源）获取数据后
   - 调用 `hotdb.save_kline()` 保存到 HotDB
   - 注意：去掉 `source` 列再保存（HotDB 不需要）

2. **可选：智能保存策略**
   - 只保存真正的"新数据"（与 HotDB 现有数据去重）
   - 或者覆盖式保存（简单但可能丢失手动修正的数据）

## 相关文件

- `backend/src/myquant/core/market/services/kline_service.py` - 需要添加保存逻辑
- `backend/src/myquant/core/market/adapters/hotdb_adapter.py` - 已有 save_kline() 方法

## 状态

- [x] 已在 KlineService 添加自动保存代码（2026-04-05）
- [ ] 待测试验证
