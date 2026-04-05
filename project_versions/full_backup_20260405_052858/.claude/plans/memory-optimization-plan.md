# 内存优化计划

## 问题背景
后端 Python 进程占用 4.8GB 内存，持续增长。

## 已完成的优化（2026-03-30）

### 1. TdxQuant 财务指标缓存
**文件**: `backend/src/myquant/core/market/adapters/tdxquant_adapter.py`
- 添加 `_stock_info_cache` 字典，缓存 `get_stock_info()` 结果（TTL 1小时）
- **效果**: 每个股票的财务指标只调用一次/小时，减少 SDK 调用

### 2. 非交易时间优先用 PyTdx
**文件**: `backend/src/myquant/core/market/services/realtime_service.py`
- `_select_snapshot_adapter()`: 非交易时间优先使用 PyTdx，避免 TdxQuant SDK
- **效果**: 避免非交易时间的 TdxQuant 内存泄漏

### 3. 非交易时间长缓存
**文件**: `backend/src/myquant/core/market/services/realtime_service.py`
- 添加 `_off_hours_cache`，TTL 1小时
- 非交易时间首次获取后，后续请求直接返回缓存
- **效果**: 非交易时间几乎不调用 TdxQuant

### 4. 调试 API 端点
**文件**: `backend/src/myquant/api/debug.py`
- `/debug/memory` - 查看各服务缓存状态
- `/debug/memory/clear` - 清理所有缓存
- `/debug/memory/gc` - 强制垃圾回收

---

## 待处理的架构问题

### ⚠️ RealtimeService 不在 V5 架构设计中

**问题**:
- RealtimeService 负责快照数据和 K 线获取，但不在官方架构图
- 前端每 5 秒调用 `refreshSnapshots()` → RealtimeService → TdxQuant
- 职责与 KlineService 有重叠

**当前状态**: 已添加临时优化（长缓存、PyTdx 降级）

**待决策**:
1. **方案 A**: 把 RealtimeService 纳入 V5 架构文档，明确职责
2. **方案 B**: 废弃 RealtimeService，快照请求改用 KlineService
3. **方案 C**: 重构为 QuoteService（只负责快照）+ KlineService（负责 K 线）

**相关文档**:
- `docs/项目设计/数据架构V5/KlineService重构-架构链路图.html`

---

## 内存监控

### 诊断工具
```bash
# 查看各服务缓存状态
curl http://localhost:8000/debug/memory

# 清理缓存
curl -X POST http://localhost:8000/debug/memory/clear

# 强制 GC
curl -X POST http://localhost:8000/debug/memory/gc
```

### 进程监控
```bash
# Windows PowerShell
Get-Process python* | Format-Table Id,ProcessName, @{Name='Memory(MB)';Expression={[math]::Round($_.WorkingSet64/1MB,2)}}
```

---

## 下一步行动

### 短期（1-2天）
1. ✅ 重启后端，观察内存变化
2. ⏳ 监控非交易时间内存是否稳定
3. ⏳ 监控交易时间内存增长速度

### 中期（1周内）
1. ⏳ 决定 RealtimeService 的架构位置
2. ⏳ 更新架构文档
3. ⏳ 如果内存还在增长，添加更多优化：
   - 线程池优化（`_save_to_hotdb_async`）
   - 前端减少请求频率
   - HotDB 定期清理过期缓存

### 长期
1. ⏳ 完善 V5 架构文档，补充所有服务
2. ⏳ 建立内存监控告警机制
3. ⏳ 性能基准测试

---

## 相关文件
- 优化: `backend/src/myquant/core/market/services/realtime_service.py`
- 优化: `backend/src/myquant/core/market/adapters/tdxquant_adapter.py`
- 诊断: `backend/src/myquant/api/debug.py`
- 前端调用: `frontend/src/views/market/RealtimeQuotes.vue`

## 更新记录
- 2026-03-30: 创建计划，完成 4 项优化
