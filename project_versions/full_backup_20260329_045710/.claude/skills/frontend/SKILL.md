# MyQuant v11 前端开发规范

## 运行环境
- Vue3 + TypeScript + Vite
- 前端源码：`E:/MyQuant_v10.0.0/frontend/src/`（v10 frontend 运行 v11 backend）
- 开发服务器：`localhost:5174`，代理 `/api` → `localhost:8000`
- 启动：`cd E:/MyQuant_v10.0.0/frontend && npm run dev`

## API 调用规范
- **只通过 `/api/*` 路由调用后端，不直接调用数据库或底层服务**
- 使用 `fetch` 或 `axios`，统一处理错误

```typescript
// 正确
const res = await fetch('/api/market/quotes', { method: 'POST', body: JSON.stringify(symbols) })

// 错误 ❌ 不能绕过后端
```

## 已知路由（可用的 API）

| 路径 | 说明 |
|------|------|
| `POST /api/market/quotes` | 实时行情（body: ["000001","600000"]） |
| `GET /api/market/status` | 市场状态 |
| `GET /api/quotes/kline/realtime/{symbol}` | K线数据 |
| `GET /api/v5/kline/realtime/{symbol}` | 同上（前端别名） |
| `GET /api/v1/quotes/status` | 市场状态（前端别名） |

## 公共导航栏

已有公共导航栏：`src/components/GlobalNavBar.vue`

**已应用的页面**：RealtimeQuotes、Monitoring、RiskControlView、MLModelManagement、ResearchDetailViewSplit、StrategyManagement、WorkflowManager

**不需要导航栏的页面**：工作流子页面（研究/验证/实盘）

## 组件目录结构

```
src/
  components/
    base/          # 基础组件（BaseButton、BaseCard、BaseModal）
    charts/        # 图表组件（K线、指标等）
    cards/         # 功能卡片
  views/
    market/        # 行情相关页面
    research/      # 研究相关页面
  router/
    index.ts       # 路由配置
```

## 代码风格
- `<script setup lang="ts">` 组合式 API
- Props 用 `defineProps<{}>()` 带类型
- Emit 用 `defineEmits<{}>()` 带类型
- 响应式用 `ref`/`reactive`，计算属性用 `computed`
