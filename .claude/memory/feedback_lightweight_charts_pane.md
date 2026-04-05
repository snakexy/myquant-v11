---
name: lightweight-charts pane管理经验
description: Vue3 + lightweight-charts 的pane生命周期管理注意事项
type: feedback
---

## 规则

**不要使用 `chart.removePane()` 移除指标pane**

**Why:** 移除pane会改变剩余pane的索引，导致后续操作引用错误的pane，引发数据错乱和显示异常。

**How to apply:**
- 隐藏pane时：使用 `pane.setHeight(0)` 而非 `removePane()`
- 显示pane时：恢复 `pane.setStretchFactor(n)` 或设置固定高度

```javascript
// ✅ 正确：隐藏pane
macdPane.setHeight(0)

// ✅ 正确：恢复显示
macdPane.setStretchFactor(1)

// ❌ 错误：移除pane会破坏索引
chart.removePane(1)  // 会导致其他pane索引变化
```

---

## 相关问题：Vue3 reactive 与 Map

**不要使用 `reactive()` 包装 `Map` 或 `Set`**

**Why:** Vue3 的 `reactive()` 对 Map/Set 的方法（`has()`、`get()`、`set()`）代理不完整，会导致判断失效。

**How to apply:**
```javascript
// ✅ 正确
const panes = ref<Map<string, PaneState>>(new Map())
panes.value.has(id)  // 正常工作

// ❌ 错误
const panes = reactive<Map<string, PaneState>>(new Map())
panes.has(id)  // 可能返回错误结果
```

---

## 问题现象

1. 切换周期后时间轴出现空白（如60分钟切日线显示4天间隔）
2. MACD窗口取消后pane不消失，或重复创建多个pane
3. 数据显示在错误的pane上
