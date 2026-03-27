<template>
  <div class="market-view">
    <!-- 连接状态 -->
    <div class="connection-status" :class="{ connected: wsConnected }">
      <el-icon><Connection /></el-icon>
      <span>{{ wsConnected ? '实时连接中' : '未连接' }}</span>
    </div>

    <!-- 市场概览 -->
    <div class="market-overview">
      <div class="overview-card">
        <div class="card-title">上证指数</div>
        <div class="card-value" :class="getIndexClass(indexData.sh?.change_percent)">
          {{ indexData.sh?.price || '--' }}
        </div>
        <div class="card-change" :class="getIndexClass(indexData.sh?.change_percent)">
          {{ indexData.sh?.change_percent?.toFixed(2) || '--' }}%
        </div>
      </div>
      <div class="overview-card">
        <div class="card-title">深证成指</div>
        <div class="card-value" :class="getIndexClass(indexData.sz?.change_percent)">
          {{ indexData.sz?.price || '--' }}
        </div>
        <div class="card-change" :class="getIndexClass(indexData.sz?.change_percent)">
          {{ indexData.sz?.change_percent?.toFixed(2) || '--' }}%
        </div>
      </div>
      <div class="overview-card">
        <div class="card-title">沪深300</div>
        <div class="card-value" :class="getIndexClass(indexData.hs300?.change_percent)">
          {{ indexData.hs300?.price || '--' }}
        </div>
        <div class="card-change" :class="getIndexClass(indexData.hs300?.change_percent)">
          {{ indexData.hs300?.change_percent?.toFixed(2) || '--' }}%
        </div>
      </div>
      <div class="overview-card stats">
        <div class="stats-row">
          <span class="stats-label">上涨:</span>
          <span class="stats-value text-up">{{ marketStats.rise }}</span>
        </div>
        <div class="stats-row">
          <span class="stats-label">下跌:</span>
          <span class="stats-value text-down">{{ marketStats.fall }}</span>
        </div>
        <div class="stats-row">
          <span class="stats-label">平盘:</span>
          <span class="stats-value text-flat">{{ marketStats.flat }}</span>
        </div>
      </div>
    </div>

    <!-- 股票列表 -->
    <div class="stock-list-section">
      <div class="section-header">
        <h3 class="section-title">股票行情 (实时更新)</h3>
        <div class="update-time" v-if="lastUpdateTime">
          最后更新: {{ lastUpdateTime }}
        </div>
      </div>

      <el-table
        :data="stockList"
        stripe
        @row-click="handleRowClick"
        class="stock-table"
      >
        <el-table-column prop="symbol" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column label="现价" width="100">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_percent)" class="price-cell">
              {{ row.price?.toFixed(2) || '--' }}
              <el-icon v-if="row.justUpdated" class="update-icon"><Refresh /></el-icon>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="涨跌幅" width="100">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_percent)">
              {{ row.change_percent?.toFixed(2) || '--' }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量(手)" width="120">
          <template #default="{ row }">
            {{ formatNumber(row.volume) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="成交额" width="120">
          <template #default="{ row }">
            {{ formatAmount(row.amount) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Connection, Refresh } from '@element-plus/icons-vue'
import { getMarketOverview, getQuotes } from '@/api/market'
import { useGlobalWebSocket } from '@/composables/useWebSocket'

const router = useRouter()

// WebSocket
const { connected: wsConnected, onQuoteUpdate, subscribe } = useGlobalWebSocket()

// 数据
const indexData = ref<any>({
  sh: null,
  sz: null,
  hs300: null
})

const marketStats = ref({
  rise: 0,
  fall: 0,
  flat: 0
})

const stockList = ref<any[]>([])
const lastUpdateTime = ref('')

// 热门股票列表
const hotSymbols = [
  '600000', '600519', '600036', '601318', '601398',
  '000001', '000002', '000858', '002415', '000333'
]

// 获取市场概览
const fetchMarketOverview = async () => {
  try {
    const data = await getMarketOverview()

    if (data.indexes) {
      data.indexes.forEach((item: any) => {
        if (item.symbol === '000001') indexData.value.sh = item
        else if (item.symbol === '399001') indexData.value.sz = item
        else if (item.symbol === '000300') indexData.value.hs300 = item
      })
    }

    if (data.statistics) {
      marketStats.value = data.statistics
    }
  } catch (error) {
    console.error('Failed to fetch market overview:', error)
  }
}

// 获取股票列表
const fetchStockList = async () => {
  try {
    const data = await getQuotes(hotSymbols.join(','))
    stockList.value = data.map((item: any) => ({
      ...item,
      justUpdated: false
    }))
  } catch (error) {
    console.error('Failed to fetch stock list:', error)
  }
}

// 更新单只股票行情
const updateStockQuote = (symbol: string, data: any) => {
  const index = stockList.value.findIndex(s => s.symbol === symbol)
  if (index !== -1) {
    // 标记为刚更新
    stockList.value[index] = {
      ...data,
      justUpdated: true
    }
    lastUpdateTime.value = new Date().toLocaleTimeString()

    // 500ms后移除更新标记
    setTimeout(() => {
      if (stockList.value[index]) {
        stockList.value[index].justUpdated = false
      }
    }, 500)
  }
}

// 行点击
const handleRowClick = (row: any) => {
  router.push({
    name: 'stock',
    query: { symbol: row.symbol }
  })
}

// 格式化数字
const formatNumber = (num: number) => {
  if (!num) return '--'
  return num.toLocaleString()
}

// 格式化金额
const formatAmount = (amount: number) => {
  if (!amount) return '--'
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toFixed(2)
}

// 获取颜色类
const getChangeClass = (value: number) => {
  if (!value) return ''
  if (value > 0) return 'text-up'
  if (value < 0) return 'text-down'
  return 'text-flat'
}

const getIndexClass = (value: number) => {
  return getChangeClass(value)
}

// WebSocket 行情更新回调
onQuoteUpdate.value = (update: any) => {
  if (update.type === 'quote_update' || update.type === 'quote_snapshot') {
    updateStockQuote(update.symbol, update.data)
  }
}

// 定时器引用
let refreshTimer: ReturnType<typeof setInterval> | null = null

// 初始化
onMounted(async () => {
  await fetchMarketOverview()
  await fetchStockList()

  // 订阅热门股票
  subscribe(hotSymbols)

  // 定期刷新市场概览（指数数据）- 改为5分钟刷新一次
  refreshTimer = setInterval(() => {
    fetchMarketOverview()
  }, 300000)
})

onUnmounted(() => {
  // 清理定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})
</script>

<style scoped>
.market-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.connection-status {
  position: fixed;
  top: 80px;
  right: 20px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  padding: 10px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 100;
  transition: all 0.3s;
}

.connection-status.connected {
  background: rgba(16, 185, 129, 0.1);
  border-color: var(--color-up);
}

.market-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.overview-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.card-title {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 4px;
}

.card-change {
  font-size: 16px;
}

.stats {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  padding: 0 8px;
}

.stats-label {
  color: var(--text-secondary);
}

.stats-value {
  font-weight: bold;
}

.stock-list-section {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
}

.update-time {
  color: var(--text-muted);
  font-size: 14px;
}

.stock-table {
  cursor: pointer;
}

.stock-table :deep(.el-table__row) {
  transition: background 0.2s;
}

.stock-table :deep(.el-table__row:hover) {
  background: var(--bg-elevated);
}

.price-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}

.update-icon {
  font-size: 12px;
  animation: pulse 0.5s;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.text-up {
  color: var(--color-up);
}

.text-down {
  color: var(--color-down);
}

.text-flat {
  color: var(--text-secondary);
}
</style>
