# 时区修复最终版本备份

**备份时间**: 2026-03-27  
**状态**: ✅ 已验证可用

## 问题

lightweight-charts 显示 A 股 K 线时，X 轴时间和数据点位置都错误。

## 解决方案

**核心**: 修改版插件 + 前端偏移

### 关键文件

1. **default-tick-mark-formatter.ts** - 插件核心修改
   - 用 `getUTCHours()` 替代 `toLocaleString()`
   - 避免 `toLocaleString()` 在中国浏览器中的 +8 小时二次偏移

2. **RealtimeQuotes.vue** - 前端数据处理
   - 数据处理：`timeValue + 8 * 3600`（加偏移）
   - hoverBar：不加偏移（param.time 已经是北京时间戳）

3. **vite.config.ts** - 插件路径配置
   - alias 指向 `../lightweight-charts-modified`

4. **lightweight-charts时区修复方案.md** - 完整文档

## 数据流

```
后端: 北京时间 15:00 → UTC 时间戳 1761721200（UTC 07:00）
  ↓
前端: +8小时 → 1761750000（UTC 15:00）
  ↓
图表: 数据点在 UTC 15:00 位置（下午3点）✅
  ↓
插件: getUTCHours() 直接读取 → 显示 "15:00" ✅
```

## 验证结果

- ✅ X 轴显示 15:00（北京时间）
- ✅ 数据点位置正确（下午3点）
- ✅ hoverBar 显示正确

## 恢复使用

```bash
# 1. 恢复插件源码
cp default-tick-mark-formatter.ts ../../lightweight-charts-modified/src/model/horz-scale-behavior-time/

# 2. 重新构建插件
cd ../../lightweight-charts-modified
npm run build

# 3. 恢复前端文件
cp RealtimeQuotes.vue ../../frontend/src/views/market/
cp vite.config.ts ../../frontend/

# 4. 重启前端服务
cd ../../frontend
npm run dev
```
