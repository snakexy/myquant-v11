import { createPinia } from 'pinia'

const pinia = createPinia()

// ========== 核心Store（新架构）==========
// M2-17重构：6个核心Store
export { useAppStore } from './core/AppStore'
export { useDataStore } from './core/DataStore'
export { useStrategyStore } from './core/StrategyStore'
export { useTradingStore } from './core/TradingStore'
export { useUserStore } from './core/UserStore'
export { useWebSocketStore } from './websocket'

// ========== M2-19清理说明 ==========
// 旧Store文件已在M2-19中删除：
// - app.ts (已合并到 AppStore.ts)
// - state.ts (已合并到 AppStore.ts)
// - theme.ts (已合并到 AppStore.ts)
// - data.ts (已合并到 DataStore.ts)
// - market.ts (已合并到 DataStore.ts)
// - sector.ts (已合并到 DataStore.ts)
// - strategy.ts (已合并到 StrategyStore.ts)
// - backtest.ts (已合并到 StrategyStore.ts)
// - user.ts (已合并到 UserStore.ts)
// - userSettings.ts (已合并到 UserStore.ts)
// - ui.ts (已合并到 UserStore.ts)

// 导出pinia实例
export default pinia