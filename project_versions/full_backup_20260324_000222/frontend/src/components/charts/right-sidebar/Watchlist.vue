<template>
  <div class="watchlist">
    <div class="watchlist-header">
      <span class="header-title">观察列表</span>
      <div class="header-actions">
        <button class="icon-btn" title="添加股票" @click="addStock">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
        </button>
        <button class="icon-btn" title="排序">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="watchlist-tabs">
      <button :class="['tab-btn', { active: activeTab === 'watchlist' }]" @click="activeTab = 'watchlist'">
        我的列表
      </button>
      <button :class="['tab-btn', { active: activeTab === 'hot' }]" @click="activeTab = 'hot'">
        热门
      </button>
    </div>

    <div class="watchlist-list" v-if="activeTab === 'watchlist'">
      <div
        v-for="stock in stocks"
        :key="stock.symbol"
        v-memo="[stock.symbol, stock.price, stock.changePercent]"
        :class="['watchlist-item', { active: stock.symbol === currentStock?.symbol }]"
        @click="selectStock(stock)"
      >
        <div class="item-left">
          <span class="stock-symbol">{{ stock.symbol }}</span>
          <span class="stock-name">{{ stock.name }}</span>
        </div>
        <div class="item-right">
          <div class="stock-price" :class="getChangeClass(stock.changePercent)">
            {{ stock.price.toFixed(2) }}
          </div>
          <div class="stock-change-box" :class="getChangeClass(stock.changePercent)">
            <span class="change-value">{{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}</span>
            <span class="change-percent">{{ stock.changePercent >= 0 ? '+' : '' }}{{ stock.changePercent.toFixed(2) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="watchlist-list" v-else>
      <div
        v-for="stock in hotStocks"
        :key="stock.symbol"
        v-memo="[stock.symbol, stock.price, stock.changePercent]"
        :class="['watchlist-item']"
        @click="selectStock(stock)"
      >
        <div class="item-left">
          <span class="stock-symbol">{{ stock.symbol }}</span>
          <span class="stock-name">{{ stock.name }}</span>
        </div>
        <div class="item-right">
          <div class="stock-price" :class="getChangeClass(stock.changePercent)">
            {{ stock.price.toFixed(2) }}
          </div>
          <div class="stock-change-box" :class="getChangeClass(stock.changePercent)">
            <span class="change-value">{{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}</span>
            <span class="change-percent">{{ stock.changePercent >= 0 ? '+' : '' }}{{ stock.changePercent.toFixed(2) }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface StockQuote {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
}

const props = defineProps<{
  currentStock?: { symbol: string; name: string }
  watchlist?: StockQuote[]
}>()

const emit = defineEmits<{
  selectStock: [stock: StockQuote]
}>()

const activeTab = ref<'watchlist' | 'hot'>('watchlist')
const loading = ref(false)
const error = ref<string | null>(null)
const backendAvailable = ref(false)  // 后端可用性标记

// 观察列表数据
const stocks = ref<StockQuote[]>([
  { symbol: '000001', name: '平安银行', price: 10.96, change: 0.06, changePercent: 0.55 },
  { symbol: '600000', name: '浦发银行', price: 7.26, change: 0.06, changePercent: 0.83 },
  { symbol: '600519', name: '贵州茅台', price: 1676.00, change: -12.50, changePercent: -0.74 },
  { symbol: '000002', name: '万科A', price: 8.95, change: 0.03, changePercent: 0.34 },
])

// 热门股票数据
const hotStocks = ref<StockQuote[]>([
  { symbol: '600036', name: '招商银行', price: 32.50, change: 0.85, changePercent: 2.68 },
  { symbol: '601318', name: '中国平安', price: 45.20, change: -0.30, changePercent: -0.66 },
  { symbol: '000858', name: '五粮液', price: 158.00, change: 2.50, changePercent: 1.61 },
])

/**
 * 获取股票实时行情
 */
const fetchStockQuote = async (symbol: string): Promise<StockQuote | null> => {
  try {
    const response = await fetch(`/api/v1/market/quotes?symbols=${symbol}`)
    const result = await response.json()

    if (result.success && result.data && result.data.length > 0) {
      const item = result.data[0]
      return {
        symbol: item.symbol || symbol,
        name: item.name || symbol,
        price: item.current_price || item.price || 0,
        change: item.change || 0,
        changePercent: item.change_percent || item.changePercent || 0,
      }
    }
    return null
  } catch (err) {
    console.error(`[Watchlist] 获取股票 ${symbol} 行情失败:`, err)
    return null
  }
}

/**
 * 检查后端健康状态
 */
const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch('/api/v1/market/health', {
      method: 'GET',
      signal: AbortSignal.timeout(2000)  // 2秒超时
    })
    const isHealthy = response.ok
    if (!backendAvailable.value && isHealthy) {
      console.log('[Watchlist] ✅ 后端已连接')
      backendAvailable.value = true
    }
    return isHealthy
  } catch {
    if (backendAvailable.value) {
      console.warn('[Watchlist] ⚠️ 后端连接断开')
      backendAvailable.value = false
    }
    return false
  }
}

/**
 * 批量更新股票行情
 */
const updateStockQuotes = async () => {
  if (loading.value) return

  // 检查后端是否可用（如果之前检测到不可用）
  if (!backendAvailable.value) {
    const isHealthy = await checkBackendHealth()
    if (!isHealthy) {
      console.log('[Watchlist] ⏸️ 后端不可用，跳过刷新')
      return
    }
  }

  loading.value = true
  error.value = null

  try {
    // 获取观察列表所有股票代码
    const symbols = stocks.value.map(s => s.symbol).join(',')

    if (!symbols) {
      console.warn('[Watchlist] 没有需要更新的股票')
      return
    }

    const response = await fetch(`/api/v1/market/quotes?symbols=${symbols}`)
    const result = await response.json()

    if (result.success && result.data) {
      // 更新观察列表
      stocks.value = stocks.value.map(stock => {
        const quote = result.data.find((q: any) => q.symbol === stock.symbol)
        if (quote) {
          return {
            ...stock,
            price: quote.current_price || quote.price || stock.price,
            change: quote.change || stock.change,
            changePercent: quote.change_percent || quote.changePercent || stock.changePercent,
          }
        }
        return stock
      })

      // 更新热门列表
      if (activeTab.value === 'hot') {
        const hotSymbols = hotStocks.value.map(s => s.symbol).join(',')
        const hotResponse = await fetch(`/api/v1/market/quotes?symbols=${hotSymbols}`)
        const hotResult = await hotResponse.json()

        if (hotResult.success && hotResult.data) {
          hotStocks.value = hotStocks.value.map(stock => {
            const quote = hotResult.data.find((q: any) => q.symbol === stock.symbol)
            if (quote) {
              return {
                ...stock,
                                        price: quote.current_price || quote.price || stock.price,
                change: quote.change || stock.change,
                changePercent: quote.change_percent || quote.changePercent || stock.changePercent,
              }
            }
            return stock
          })
        }
      }

      console.log(`[Watchlist] ✅ 行情更新成功`)
    } else {
      console.error('[Watchlist] ❌ 行情数据格式错误:', result)
      error.value = '行情数据格式错误'
    }
  } catch (err) {
    console.error('[Watchlist] ❌ 获取行情失败:', err)
    error.value = '获取行情失败'
  } finally {
    loading.value = false
  }
}

/**
 * 选择股票
 */
const selectStock = (stock: StockQuote) => {
  console.log('[Watchlist] 选择股票:', stock)
  emit('selectStock', stock)
}

/**
 * 添加股票到观察列表
 */
const addStock = () => {
  // TODO: 打开添加股票对话框
  // 可以使用 prompt() 或创建一个自定义对话框组件
  const symbol = prompt('请输入股票代码（例如：000001）:')
  if (symbol) {
    fetchStockQuote(symbol).then(quote => {
      if (quote && !stocks.value.find(s => s.symbol === quote.symbol)) {
        stocks.value.push(quote)
        console.log('[Watchlist] ✅ 添加股票成功:', quote)
      } else if (stocks.value.find(s => s.symbol === symbol)) {
        alert('该股票已在观察列表中')
      } else {
        alert('添加失败，请检查股票代码')
      }
    })
  }
}

/**
 * 涨跌样式
 */
const getChangeClass = (percent: number) => {
  return percent > 0 ? 'up' : percent < 0 ? 'down' : 'flat'
}

// 自动刷新定时器
let refreshTimer: number | null = null
let strategyCheckTimer: number | null = null

/**
 * 获取刷新策略
 */
const fetchRefreshStrategy = async (): Promise<{ shouldRefresh: boolean; interval: number } | null> => {
  try {
    const response = await fetch('/api/v1/market/refresh-strategy?data_type=watchlist')
    const result = await response.json()
    if (result.success && result.data) {
      return {
        shouldRefresh: result.data.should_refresh,
        interval: result.data.interval || 3000  // 默认3秒
      }
    }
    return null
  } catch (err) {
    console.error('[Watchlist] 获取刷新策略失败:', err)
    return null
  }
}

/**
 * 启动自动刷新（遵守刷新规则）
 */
const startAutoRefresh = async () => {
  // 先获取刷新策略
  const strategy = await fetchRefreshStrategy()

  if (!strategy) {
    console.warn('[Watchlist] ⚠️ 无法获取刷新策略，暂停自动刷新')
    // 每30秒重新尝试获取策略
    if (strategyCheckTimer) {
      clearInterval(strategyCheckTimer)
    }
    strategyCheckTimer = window.setInterval(() => {
      startAutoRefresh()
    }, 30000)
    return
  }

  if (!strategy.shouldRefresh) {
    console.log(`[Watchlist] ⏸️ 当前时段不刷新`)
    // 每60秒重新检查一次策略
    if (strategyCheckTimer) {
      clearInterval(strategyCheckTimer)
    }
    strategyCheckTimer = window.setInterval(() => {
      startAutoRefresh()
    }, 60000)
    return
  }

  // 使用策略返回的间隔（交易时段通常为3秒）
  const interval = strategy.interval
  console.log(`[Watchlist] ▶️ 使用刷新策略: ${interval}秒间隔`)

  // 清除旧的定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (strategyCheckTimer) {
    clearInterval(strategyCheckTimer)
  }

  refreshTimer = window.setInterval(() => {
    updateStockQuotes()
  }, interval)

  // 每60秒重新检查一次策略（应对时段变化）
  strategyCheckTimer = window.setInterval(() => {
    startAutoRefresh()
  }, 60000)
}

/**
 * 停止自动刷新
 */
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (strategyCheckTimer) {
    clearInterval(strategyCheckTimer)
    strategyCheckTimer = null
  }
}

// 组件挂载时
onMounted(() => {
  console.log('[Watchlist] 组件已挂载')
  // 初始加载行情
  updateStockQuotes()
  // 启动自动刷新
  startAutoRefresh()
})

// 组件卸载时
onUnmounted(() => {
  console.log('[Watchlist] 组件已卸载')
  stopAutoRefresh()
})

// 暴露方法供父组件调用
defineExpose({
  updateStockQuotes,
  refresh: updateStockQuotes,
})
</script>

<style scoped lang="scss">
// TradingView 官方紧凑设计
.watchlist {
  width: 280px;
  height: 100%;
  background: #131722;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.watchlist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #2a2e39;
  min-height: 40px;

  .header-title {
    font-size: 13px;
    font-weight: 600;
    color: #d1d4dc;
  }

  .header-actions {
    display: flex;
    gap: 4px;

    .icon-btn {
      width: 24px;
      height: 24px;
      border: none;
      background: transparent;
      color: #787b86;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;

      &:hover {
        background: #2a2e39;
        color: #d1d4dc;
      }
    }
  }
}

.watchlist-tabs {
  display: flex;
  gap: 1px;
  padding: 4px 8px 0;
  border-bottom: 1px solid #2a2e39;

  .tab-btn {
    flex: 1;
    padding: 6px 8px;
    background: transparent;
    border: none;
    color: #787b86;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    border-radius: 4px 4px 0 0;
    transition: all 0.15s ease;
    border-bottom: 2px solid transparent;

    &:hover {
      color: #d1d4dc;
      background: #1e222d;
    }

    &.active {
      color: #2962ff;
      border-bottom-color: #2962ff;
    }
  }
}

.watchlist-list {
  flex: 1;
  overflow-y: auto;

  /* 自定义滚动条 - TradingView风格 */
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #131722;
  }

  &::-webkit-scrollbar-thumb {
    background: #2a2e39;
    border-radius: 3px;

    &:hover {
      background: #363a45;
    }
  }
}

.watchlist-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #2a2e39;
  cursor: pointer;
  transition: background 0.1s ease;

  &:hover {
    background: #1e222d;
  }

  &.active {
    background: #2a2e39;
  }

  .item-left {
    display: flex;
    flex-direction: column;
    gap: 2px;
    flex: 1;
    min-width: 0;

    .stock-symbol {
      font-weight: 600;
      color: #d1d4dc;
      font-size: 13px;
    }

    .stock-name {
      font-size: 11px;
      color: #787b86;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .item-right {
    display: flex;
    flex-direction: column;
    gap: 2px;
    align-items: flex-end;
    margin-left: 8px;

    .stock-price {
      font-size: 14px;
      font-weight: 600;
      font-family: 'Roboto', 'Arial', sans-serif;

      &.up { color: #26A69A; }
      &.down { color: #EF5350; }
      &.flat { color: #d1d4dc; }
    }

    .stock-change-box {
      display: flex;
      gap: 6px;
      font-size: 11px;
      font-family: 'Roboto', 'Arial', sans-serif;
      padding: 2px 6px;
      border-radius: 3px;

      &.up {
        color: #26A69A;
        background: rgba(38, 166, 154, 0.1);
      }

      &.down {
        color: #EF5350;
        background: rgba(239, 83, 80, 0.1);
      }

      &.flat {
        color: #787b86;
      }

      .change-value,
      .change-percent {
        white-space: nowrap;
      }
    }
  }
}
</style>
