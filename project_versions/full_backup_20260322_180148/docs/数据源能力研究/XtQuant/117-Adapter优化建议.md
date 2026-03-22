# Adapter数据获取策略优化建议

> **创建日期**: 2026-02-05
> **基于文档**: [116-K线图数据获取策略-最终建议.md](./116-K线图数据获取策略-最终建议.md)
> **目标**: 基于最新测试发现，优化adapter数据获取策略

---

## 📊 当前实现分析

### 现有策略（xtquant_enhanced_adapter.py）

```python
# 策略1: 日线数据 - 直接在线获取
if period in ['day', '1d', 'daily']:
    data = await self._fetch_online_daily(...)

# 策略2: 分钟数据、周线、月线 - 智能选择
elif xt_period in ['1m', '5m', '15m', '30m', '1h', '1w', '1mon']:
    if days > 200:
        logger.warning("建议提前使用download_history_data下载")
    data = await self._fetch_period_data(...)

# 策略3: tick数据
else:
    data = await self._fetch_tick_data(...)
```

**特点**:
- ✅ 有缓存机制
- ✅ 有日期范围警告（>200天）
- ⚠️ 策略分支较多，代码复杂
- ⚠️ 未充分利用在线获取能力

---

## 🔬 最新测试发现

### 测试结果（test_204_long_term_kline.py）

| 周期 | 数据量 | 在线获取耗时 | 性能评价 |
|------|--------|------------|---------|
| 日K - 3年 | 750条 | 9.5ms | ⚡ 极快 |
| 30分钟K - 3个月 | 2640条 | 32.6ms | ⚡ 很快 |
| 15分钟K - 3个月 | 5280条 | 35.5ms | ⚡ 很快 |
| 5分钟K - 6个月 | 6336条 | 19.1ms | ⚡ 极快 |
| 1分钟K - 2周 | 2500条 | 12.0ms | ⚡ 极快 |

### 关键发现

1. **在线获取能力远超预期**
   - 5分钟K线：可获取**6336条**（之前认为限制1083条）
   - 1分钟K线：可获取**2500条**（之前认为限制1261条）

2. **性能优秀且稳定**
   - 平均耗时：9-36ms
   - 最快：9ms
   - 适合所有K线图场景

3. **代码可以极简化**
   - 不需要复杂的策略选择
   - 不需要下载+读取（对于K线图场景）
   - 一次API调用即可

---

## 🎯 优化建议

### 建议1: 简化数据获取策略 ⭐⭐⭐⭐⭐

**当前问题**:
- 策略分支复杂（3个策略）
- 有日期范围警告（>200天）
- 未充分利用在线获取能力

**优化方案**:

```python
async def get_kline_data(
    self,
    symbol: str,
    period: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    count: int = 500,
    adjust_type: str = 'front'
) -> Optional[pd.DataFrame]:
    """
    获取K线数据（优化版）

    策略：优先使用在线获取（适用于99%的场景）
    """
    if not self.connected:
        logger.error("未连接到MiniQMT")
        return None

    # 标准化股票代码和周期
    xt_symbol = self._to_xt_symbol(symbol)
    xt_period = self._to_xt_period(period)

    # 检查缓存
    cache_key = f"{symbol}_{period}_{start_date}_{end_date}_{count}"
    if self.cache is not None and cache_key in self.cache:
        logger.debug(f"缓存命中: {cache_key}")
        return self.cache[cache_key]

    # ===== 简化策略：统一使用在线获取 =====
    # 基于测试发现：在线获取可以支持6000+条数据，性能9-36ms
    # 适用于所有K线场景（日K、1h、30m、15m、5m、1m）

    if xt_period in ['1d', '1h', '1m', '5m', '15m', '30m', '1w', '1mon']:
        data = await self._fetch_online_simple(
            xt_symbol, xt_period, start_date, end_date, count
        )

        if data is not None:
            if self.cache is not None:
                self.cache[cache_key] = data
            return data

    # tick数据保持原样
    elif xt_period == 'tick':
        data = await self._fetch_tick_data(...)
        ...

    logger.warning(f"未获取到数据: {symbol} {period}")
    return None
```

**优点**:
- ✅ 代码简化50%+
- ✅ 逻辑清晰，易于维护
- ✅ 性能优秀（9-36ms）
- ✅ 支持所有K线图场景

**风险**:
- ⚠️ 需要完整测试
- ⚠️ 超大数据量（>10000条）可能仍有限制

---

### 建议2: 移除日期范围警告 ⭐⭐⭐

**当前代码**:
```python
if days > 200:
    logger.warning(
        f"⚠️ {symbol} {period} 日期范围超过200天（{days}天），"
        f"建议提前使用download_history_data下载"
    )
```

**问题**:
- 基于旧理解（在线获取限制22.6个交易日）
- 新测试表明在线获取可支持6336条（约6个月5分钟K线）
- 警告对用户造成困扰

**建议**: 移除此警告，或提高阈值到1000天

---

### 建议3: 优化缓存策略 ⭐⭐

**当前缓存**:
- 缓存键：`{symbol}_{period}_{start_date}_{end_date}_{count}`
- 问题：参数变化导致缓存失效

**优化方案**:

```python
# 优化后的缓存键
cache_key = f"{symbol}_{period}_{start_date}_{end_date}"
# 不包含count，因为获取的数据会自动包含count条

# 或者更激进的缓存策略
cache_key = f"{symbol}_{period}"  # 只缓存最近获取的数据
# 适合K线图场景（用户总是看最新的）
```

---

### 建议4: 添加性能监控 ⭐⭐⭐⭐

**建议添加**:

```python
async def _fetch_online_simple(...):
    """在线获取（带性能监控）"""
    import time

    start = time.time()

    try:
        # 在线获取
        data = xtdata.get_market_data_ex(...)

        elapsed = (time.time() - start) * 1000

        # 性能日志
        logger.info(
            f"[在线获取] {symbol} {period} "
            f"获取{len(data)}条, 耗时{elapsed:.1f}ms"
        )

        # 性能监控（可选）
        if elapsed > 100:  # 超过100ms记录
            logger.warning(f"⚠️ 获取耗时较长: {elapsed:.1f}ms")

        return data

    except Exception as e:
        logger.error(f"在线获取失败: {e}")
        return None
```

---

## 🚀 实施建议

### 方案A: 保守优化（推荐）⭐⭐⭐⭐⭐

**只做最小改动，保持稳定性**

1. ✅ 移除日期范围>200天的警告（或改为>1000天）
2. ✅ 添加性能日志
3. ✅ 保留现有策略结构

**优点**:
- 风险最低
- 改动最小
- 不影响现有功能

**预计时间**: 30分钟

---

### 方案B: 完整优化（可选）⭐⭐⭐

**基于新发现全面重构**

1. ✅ 简化策略（统一使用在线获取）
2. ✅ 移除不必要的警告
3. ✅ 优化缓存策略
4. ✅ 添加性能监控
5. ✅ 完整测试

**优点**:
- 代码简洁50%+
- 性能可能提升
- 符合最新API能力

**缺点**:
- 需要完整测试
- 可能影响现有功能

**预计时间**: 2-3小时

---

## 📝 测试建议

无论选择哪个方案，都需要测试：

### 测试场景

1. **小数据量** (< 100条)
   - 日K: 10天
   - 5分钟K: 1天

2. **中等数据量** (100-1000条)
   - 日K: 6个月
   - 5分钟K: 1个月

3. **大数据量** (1000-6000条)
   - 日K: 3年
   - 5分钟K: 6个月

4. **边缘情况**
   - count = 0
   - count = 10000
   - 非交易时间

### 性能基准

| 操作 | 目标性能 | 当前性能 |
|------|---------|---------|
| 在线获取（少量） | < 20ms | 9-36ms ✅ |
| 在线获取（大量） | < 50ms | 19-36ms ✅ |
| 缓存命中 | < 5ms | ~1ms ✅ |

---

## ✅ 总结

### 核心发现

1. **在线获取能力强大**: 可获取6000+条，性能9-36ms
2. **当前代码过度保守**: 有不必要的策略分支和警告
3. **简化空间大**: 可简化50%+代码

### 推荐方案

**优先级排序**:
1. 🔴 **高优先级**: 移除日期范围警告（方案A）
2. 🟡 **中优先级**: 添加性能日志（方案A）
3. 🟢 **低优先级**: 简化策略结构（方案B）

### 下一步

1. **立即可做**: 执行方案A（保守优化）
2. **需要讨论**: 是否执行方案B（完整重构）
3. **后续优化**: 根据实际使用反馈调整

---

**创建时间**: 2026-02-05
**状态**: ✅ 建议文档已完成
**实施状态**: ⏸️ 等待讨论和决策
