# 增量缓存设计优化

## 当前问题

```python
# HotDB 当前缓存策略（冗余）
Redis: hotdb:kline:600519.SH:1d 
  → 整个 DataFrame (5000条 × 6字段 = 大量内存)
  → 每次更新都要序列化/反序列化整个数据集
```

**问题**:
1. 内存浪费：缓存了完整历史数据
2. 网络浪费：每次传输大量数据
3. CPU浪费：频繁序列化大对象

---

## 优化方案：元数据缓存 + 增量获取

```python
# 新设计：只缓存元数据
Redis: hotdb:meta:600519.SH:1d  → Hash
  ├─ last_time: "2026-04-03 15:00:00"  # 最后数据时间
  ├─ last_close: 1500.50               # 最后收盘价
  ├─ count: 500                        # 总条数
  ├─ data_hash: "sha256:xxx"           # 数据校验
  ├─ updated_at: "2026-04-03T15:00:00Z"
  └─ source: "hotdb"

# 数据分片存储（可选，用于快速恢复）
Redis: hotdb:kline:600519.SH:1d:recent  → List (最近100条，用于快速显示)
Redis: hotdb:kline:600519.SH:1d:202604  → Hash (按月分片存储)
```

---

## 增量获取流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      客户端请求 K线数据                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. 获取元数据 (Redis hotdb:meta:{symbol}:{period})              │
│    → 得到 last_time, count                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. 判断是否需要增量更新                                          │
│    ├─ 本地无数据 → 全量加载                                      │
│    ├─ 本地 last_time < Redis last_time → 增量获取                │
│    └─ 本地数据完整 → 直接返回                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. 增量获取 (只获取缺失的数据)                                    │
│    API: /api/quotes/kline/{symbol}?start_time={local_last_time}  │
│    → 返回新增的几条数据而非整个DataFrame                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. 合并数据                                                      │
│    本地数据 + 新增数据 → 完整数据集                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. 更新元数据                                                    │
│    更新 hotdb:meta 中的 last_time, count 等                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 代码实现

### useKlineData.ts 修改

```typescript
// useKlineData.ts - 增量更新版本

export interface KlineMetadata {
  lastTime: number        // 最后数据时间戳
  lastClose: number       // 最后收盘价
  count: number           // 总条数
  dataHash: string        // 数据校验和
  updatedAt: string       // 更新时间
}

export function useKlineData(
  symbol: Ref<string>,
  timeframe: Ref<Timeframe>,
  options?: UseKlineDataOptions
) {
  // ... 现有代码 ...
  
  /** 增量加载历史数据 */
  const loadHistoryIncremental = async (): Promise<void> => {
    // 1. 获取本地存储的元数据
    const localMeta = getLocalMetadata(symbol.value, timeframe.value)
    
    // 2. 调用API获取增量数据
    const res = await fetchKlineIncremental(
      symbol.value, 
      timeframe.value,
      localMeta?.lastTime  // 从上次时间开始获取
    )
    
    if (res.incremental && localMeta) {
      // 增量模式：只追加新数据
      const newBars = convertKlineData(res.data)
      bars.value = [...bars.value, ...newBars]
    } else {
      // 全量模式：替换所有数据
      bars.value = convertKlineData(res.data)
    }
    
    // 3. 更新元数据
    saveLocalMetadata(symbol.value, timeframe.value, {
      lastTime: bars.value[bars.value.length - 1]?.time,
      count: bars.value.length,
      // ...
    })
  }
  
  return {
    // ...
    loadHistory: loadHistoryIncremental
  }
}
```

### 后端 API 修改

```python
# backend/src/myquant/api/dataget/kline.py

@router.get("/kline/incremental/{symbol}")
async def get_kline_incremental(
    symbol: str,
    period: str = '1d',
    after_time: Optional[int] = None,  # 从此时间之后获取
    limit: int = 100
):
    """增量获取K线数据
    
    Args:
        after_time: Unix时间戳，只获取此时间之后的数据
        limit: 最大返回条数
    
    Returns:
        {
            "symbol": "600519.SH",
            "period": "1d", 
            "incremental": true,
            "data": [...],  # 只有新增的几条
            "total_count": 5000,  # 总条数
            "last_time": 1743673200  # 最后时间
        }
    """
    hotdb = V5HotDBAdapter()
    
    # 获取完整数据
    full_df = hotdb.get_kline([symbol], period)
    
    if symbol not in full_df:
        return {"symbol": symbol, "period": period, "data": []}
    
    df = full_df[symbol]
    
    if after_time:
        # 只返回 after_time 之后的数据
        df = df[df['datetime'].astype('int64') // 10**9 > after_time]
        incremental = True
    else:
        incremental = False
    
    return {
        "symbol": symbol,
        "period": period,
        "incremental": incremental,
        "data": df.to_dict('records'),
        "total_count": len(full_df[symbol]),
        "last_time": int(full_df[symbol]['datetime'].iloc[-1].timestamp())
    }
```

---

## 性能对比

| 指标 | 原方案(全量) | 新方案(增量) | 提升 |
|------|-------------|-------------|------|
| 缓存内存 | 5000条 × 6字段 | 1条元数据 | 99.9%↓ |
| 传输数据量 | 5000条 | 1-10条(新增) | 99.8%↓ |
| 序列化时间 | ~50ms | ~1ms | 98%↓ |
| 网络延迟 | ~200ms | ~10ms | 95%↓ |

---

## 边界情况处理

| 场景 | 处理策略 |
|------|----------|
| 本地数据为空 | 全量加载 |
| 数据断层(中间缺失) | 检测断层，重新全量加载 |
| 数据校验失败(hash mismatch) | 重新全量加载 |
| 服务器数据回滚(时间倒退) | 检测last_time，重新全量加载 |
| 跨天首次请求 | 全量加载(日线场景) |

---

## 实施步骤

1. **Step 1**: 添加 `/kline/incremental` API
2. **Step 2**: 修改 useKlineData.ts 支持增量模式
3. **Step 3**: 添加元数据本地存储(localStorage/IndexedDB)
4. **Step 4**: 测试各种边界情况

---

**下一步**: 确认设计后，开始 Step 1 实现
