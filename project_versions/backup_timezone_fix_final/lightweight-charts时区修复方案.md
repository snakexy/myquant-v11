# lightweight-charts 时区修复方案

## 问题描述

使用 TradingView 的 lightweight-charts 图表库显示 A 股 K 线时，时间轴显示不正确：

- **X 轴时间标签**显示的是 UTC 时间（如 07:00），而不是北京时间（15:00）
- **数据时间**和 **X 轴时间**不一致

## 根本原因

**lightweight-charts 的 X 轴时间标签硬编码为 UTC 时区，无法通过配置改变**。

标准版的 `default-tick-mark-formatter.ts` 使用了 `toLocaleString()` 方法，会根据浏览器时区自动转换时间，这导致：
1. 如果前端不加偏移：数据点在 UTC 位置（早上7点），但显示正确（15:00）
2. 如果前端加偏移：数据点位置正确（15:00），但 `toLocaleString()` 再转8小时显示成23:00

## 最终解决方案

### 核心思路

**前端偏移 + 修改版插件**：
1. 前端时间戳加 8 小时，把数据点"搬"到正确位置
2. 修改版插件用 `getUTCHours()` 直接读取，跳过 `toLocaleString()` 的时区转换

### 标准版 vs 修改版对比

#### 标准版的两难困境

```
【方案1：前端不加偏移】
前端传：1761721200（UTC 07:00）
      ↓
插件 toLocaleString() 转换：UTC 07:00 → 北京时间 15:00
      ↓
显示：15:00 ✅ | 数据点位置：UTC 07:00（早上7点）❌

【方案2：前端加偏移】
前端传：1761750000（UTC 15:00）
      ↓
插件 toLocaleString() 转换：UTC 15:00 → 北京时间 23:00
      ↓
显示：23:00 ❌ | 数据点位置：UTC 15:00（下午3点）✅
```

**标准版无法同时满足显示正确和位置正确！**

#### 修改版的解决

```
前端传：1761750000（UTC 15:00）
      ↓
插件 getUTCHours() 直接读取：15
      ↓
显示：15:00 ✅ | 数据点位置：UTC 15:00（下午3点）✅
```

### 实现细节

#### 1. 后端（保持不变）

返回 UTC 时间戳（毫秒级）：

```python
# backend/src/myquant/api/dataget/quotes.py
def _to_unix_timestamp(dt) -> int:
    """将 datetime 转换为 UTC 毫秒时间戳，naive datetime 视为北京时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')

    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = beijing_tz.localize(dt)
        return int(dt.timestamp() * 1000)
    # ...
```

**说明**：
- 北京时间 2025-12-29 15:00:00
- 标记为 Asia/Shanghai
- `.timestamp()` 返回 UTC 时间戳：1761721200（对应 UTC 07:00）
- 前端收到：1761721200000 毫秒

#### 2. 修改 lightweight-charts 插件

修改 `lightweight-charts-modified/src/model/horz-scale-behavior-time/default-tick-mark-formatter.ts`：

```typescript
// 【修改前】标准版使用 toLocaleString，会根据浏览器时区转换
const localDateFromUtc = new Date(date.getTime() + 8 * 60 * 60 * 1000);
return localDateFromUtc.toLocaleString(locale, formatOptions);  // ❌ 二次偏移

// 【修改后】直接用 UTC 方法读取，不转换
switch (tickMarkType) {
    case TickMarkType.Time:
        return `${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')}`;
    // ...
}
```

构建修改版：
```bash
cd lightweight-charts-modified
npm run build
```

#### 3. 前端配置

**a) vite.config.ts 指向修改版**

```typescript
// frontend/vite.config.ts
resolve: {
  alias: {
    '@': resolve(__dirname, 'src'),
    'lightweight-charts': resolve(__dirname, '../lightweight-charts-modified'),
  },
},
```

**b) 数据处理加偏移**

```typescript
// frontend/src/views/market/RealtimeQuotes.vue
const klineDataWithSeconds = klineRes.data
  .map((item: KlineItem) => {
    let timeValue: number
    if (typeof item.time === 'string') {
      timeValue = Math.floor(new Date(item.time).getTime() / 1000)
    } else {
      const numTime = Number(item.time)
      // 判断是毫秒还是秒：毫秒时间戳 > 1e11
      timeValue = numTime > 100000000000 ? Math.floor(numTime / 1000) : numTime
    }

    // 【关键】前端加 8 小时偏移，把数据点"搬"到正确位置
    const beijingTime = timeValue + 8 * 3600

    return {
      time: beijingTime,
      open: Number(item.open),
      high: Number(item.high),
      low: Number(item.low),
      close: Number(item.close),
      volume: Number(item.volume)
    }
  })
```

**c) hoverBar 不加偏移**

```typescript
// 十字光标移动 → 更新 hoverBar
chart.subscribeCrosshairMove((param: any) => {
  if (!param.time || !candleSeries) {
    hoverBar.value = null
    return
  }
  const bar = param.seriesData.get(candleSeries) as any
  if (bar) {
    const ts = Number(param.time) * 1000
    const dt = new Date(ts)  // 不加偏移，param.time 已经是北京时间戳
    const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
    const timeStr = isDaily
      ? `${dt.getUTCFullYear()}-${String(dt.getUTCMonth()+1).padStart(2,'0')}-${String(dt.getUTCDate()).padStart(2,'0')}`
      : `${String(dt.getUTCMonth()+1).padStart(2,'0')}-${String(dt.getUTCDate()).padStart(2,'0')} ${String(dt.getUTCHours()).padStart(2,'0')}:${String(dt.getUTCMinutes()).padStart(2,'0')}`
    // ...
  }
})
```

#### 4. timeFormatter 配置

前端 timeFormatter 可以去掉（插件已处理）：

```typescript
localization: {
  dateFormat: 'yyyy-MM-dd',
  // timeFormatter 可省略，使用插件默认
}
```

## 数据流示意图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         数据流（时区处理）                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  数据库存储                                                          │
│  ┌─────────────────────────────────────┐                            │
│  │ datetime: 2026-03-27 15:00:00      │  (naive，视为北京时间)      │
│  └─────────────────────────────────────┘                            │
│                          ↓                                           │
│  后端处理                                                            │
│  ┌─────────────────────────────────────┐                            │
│  │ dt.tz_localize('Asia/Shanghai')     │  → 北京时间 15:00           │
│  │ .timestamp()                        │  → 1745794800 (UTC秒级)    │
│  └─────────────────────────────────────┘                            │
│     返回：1761721200000 毫秒（对应 UTC 07:00）                        │
│                          ↓                                           │
│  前端接收                                                            │
│  ┌─────────────────────────────────────┐                            │
│  │ timeValue: 1761721200 (UTC 07:00)  │                            │
│  └─────────────────────────────────────┘                            │
│                          ↓                                           │
│  前端时间戳偏移（+8小时）                                             │
│  ┌─────────────────────────────────────┐                            │
│  │ 1761721200 + 28800 = 1761750000    │  (UTC 15:00)               │
│  └─────────────────────────────────────┘                            │
│                          ↓                                           │
│  lightweight-charts（修改版）                                         │
│  ┌─────────────────────────────────────┐                            │
│  │ 数据点位置：UTC 15:00 的位置         │  → 下午3点 ✅              │
│  │ 插件 getUTCHours() 直接读取          │  → 显示 "15:00" ✅         │
│  └─────────────────────────────────────┘                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 关键问题与解决

### 🔴 关键问题：标准版的 `toLocaleString()` 二次偏移

**问题根源**：
- 标准版插件使用 `toLocaleString(locale, formatOptions)` 显示时间
- `toLocaleString` 会根据**浏览器时区**自动转换时间
- 在中国浏览器（UTC+8）中，UTC 时间会自动 +8 小时显示

**导致的困境**：
```
前端不加偏移 → 数据点错（早上7点），显示对（15:00）
前端加偏移   → 数据点对（15:00），显示错（23:00）← 二次偏移！
```

### ✅ 解决方案：修改版插件跳过 `toLocaleString()`

**修改文件**：`lightweight-charts-modified/src/model/horz-scale-behavior-time/default-tick-mark-formatter.ts`

**核心改动**：
```typescript
// 【标准版 - 有问题】
return localDateFromUtc.toLocaleString(locale, formatOptions);  // 自动时区转换

// 【修改版 - 解决】
return `${String(date.getUTCHours()).padStart(2, '0')}:...`;  // 直接读取，不转换
```

**为什么有效**：
- `getUTCHours()` 直接读取时间戳对应的小时数，不经过时区转换
- 前端传 UTC 15:00 的时间戳 → `getUTCHours()` 返回 15 → 显示 "15:00"
- 配合前端 +8 小时偏移，数据点和显示都正确

### 🎯 完整方案的三要素

| 层级 | 操作 | 作用 |
|------|------|------|
| **前端** | 时间戳 +8 小时 | 把数据点"搬"到 UTC 15:00 的位置 |
| **插件** | 用 `getUTCHours()` 直接读取 | 避免 `toLocaleString()` 的二次偏移 |
| **hoverBar** | 不加偏移 | `param.time` 已经是北京时间戳 |

## 为什么不直接修改后端返回北京时间的时间戳？

如果后端直接返回北京时间的时间戳（不加 UTC 转换）：
- 北京时间 15:00 → 时间戳对应 UTC 07:00
- lightweight-charts 显示：`07:00`（错误）

所以必须在前端做偏移，让"UTC 时间"等于"北京时间"。

## 异常时间戳过滤

后端需要过滤异常数据，避免前端收到错误时间戳：

```python
# 正常范围：2020-01-01 到 2030-12-31
if timestamp < 1577836800 or timestamp > 1924905600:
    logger.warning(f"过滤异常时间戳: {timestamp}")
    continue
```

## 修改文件清单

| 文件 | 修改内容 | 状态 |
|------|---------|------|
| `lightweight-charts-modified/src/model/horz-scale-behavior-time/default-tick-mark-formatter.ts` | 用 `getUTCHours()` 替代 `toLocaleString()` | ✅ 关键修改 |
| `frontend/vite.config.ts` | alias 指向修改版插件 | ✅ |
| `frontend/src/views/market/RealtimeQuotes.vue` | 数据处理 +8 小时偏移 | ✅ |
| `frontend/src/views/market/RealtimeQuotes.vue` | hoverBar 不加偏移 | ✅ |

## 替代方案（不推荐）

如果不想用时间戳偏移，可以考虑换图表库：

| 方案 | 优点 | 缺点 |
|------|------|------|
| **继续用 lightweight-charts** | TradingView 官方，效果好 | 需要时间戳偏移 hack |
| **换 ECharts** | 中国开发，文档完善 | 不是专业金融图表 |
| **换 HQChart** | 专门支持 A 股 | 效果不如 TradingView |

## 总结

1. **问题根源**：
   - lightweight-charts 标准版的 `toLocaleString()` 会根据浏览器时区自动转换
   - 在中国浏览器中，UTC 时间会 +8 小时显示，导致二次偏移

2. **解决方案**：
   - 修改插件：用 `getUTCHours()` 替代 `toLocaleString()`
   - 前端偏移：时间戳 +8 小时，把数据点放到正确位置
   - hoverBar 同步：不加偏移

3. **关键点**：
   - 后端返回 UTC 时间戳（北京时间 15:00 = UTC 07:00）
   - 前端传北京时间戳（+8 小时 = UTC 15:00）
   - 插件直接读取（getUTCHours），不转换

---

**文档创建时间**：2026-03-27
**问题状态**：✅ 已解决
**测试环境**：Windows 11 + Chrome
