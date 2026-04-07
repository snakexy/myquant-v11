<template>
  <div class="hotspot-analysis-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <i class="fas fa-fire"></i>
          热点分析
        </h1>
        <p class="page-subtitle">实时市场热点追踪与量化深度分析</p>
      </div>
      <div class="header-right">
        <div class="update-info">
          <span class="update-indicator" :class="{ active: isRealtime }"></span>
          <span class="update-text">{{ updateTimeText }}</span>
        </div>
        <button class="refresh-btn" @click="refreshData" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
          刷新
        </button>
      </div>
    </div>

    <!-- 市场涨跌分布（替换原来的快速统计） -->
    <div class="market-distribution-section" v-if="marketDistribution && marketStats">
      <MarketDistribution
        :distribution="marketDistribution"
        :marketStats="{
          total_amount_yi: Number(marketStats.totalAmount),
          limit_up_count: marketStats.limitUpCount,
          limit_down_count: marketStats.limitDownCount
        }"
        @showMarketKline="showMarketKline"
      />
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：实时排行榜 -->
      <div class="left-panel">
        <RealtimeRankings
          :rankings="rankings"
          :loading="loading"
          @stock-click="showStockDetail"
        />
      </div>

      <!-- 中间：板块监控 -->
      <div class="center-panel">
        <SectorMonitor
          :sectors="sectors"
          :loading="loading"
          @sector-click="filterBySector"
        />
      </div>

      <!-- 右侧：Qlib分析 -->
      <div class="right-panel">
        <QlibAnalysis
          :selected-stock="selectedStock"
          :loading="loading"
        />
      </div>
    </div>

    <!-- 底部：智能推荐 -->
    <div class="bottom-panel">
      <SmartRecommendations
        :recommendations="recommendations"
        :loading="loading"
        @stock-click="showStockDetail"
      />
    </div>

    <!-- 股票详情弹窗 -->
    <StockDetailModal
      :show="showDetail"
      :stock="selectedStock"
      @close="showDetail = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onActivated, onDeactivated } from 'vue'
import RealtimeRankings from '@/components/hotspot-analysis/RealtimeRankings.vue'
import SectorMonitor from '@/components/hotspot-analysis/SectorMonitor.vue'
import QlibAnalysis from '@/components/hotspot-analysis/QlibAnalysis.vue'
import SmartRecommendations from '@/components/hotspot-analysis/SmartRecommendations.vue'
import StockDetailModal from '@/components/hotspot-analysis/StockDetailModal.vue'
import MarketDistribution from '@/components/hotspot-analysis/MarketDistribution.vue'

interface Stock {
  code: string
  name: string
  changePercent: number
  volume: number
  amount: number
  market: string
}

interface Sector {
  id: string
  name: string
  changePercent: number
  stockCount: number
  topStocks: Stock[]
}

interface MarketStats {
  riseCount: number
  risePercent: number
  fallCount: number
  fallPercent: number
  limitUpCount: number
  limitDownCount: number  // 添加跌停统计
  totalAmount: string
}

// 状态管理
const loading = ref(false)
const isRealtime = ref(false)
const updateTimeText = ref('等待更新')
const selectedStock = ref<Stock | null>(null)
const showDetail = ref(false)

// 缓存管理
const lastFetchTime = ref<number>(0)
const CACHE_DURATION = 30000 // 30秒缓存
const isInitialized = ref(false) // 标记是否已初始化

// 数据
const rankings = ref({
  topRise: [] as Stock[],
  topFall: [] as Stock[],
  topAmount: [] as Stock[]
})

const sectors = ref<Sector[]>([])
const recommendations = ref({
  superHot: [] as Stock[],
  hot: [] as Stock[],
  watch: [] as Stock[]
})

const marketStats = ref<MarketStats>({
  riseCount: 0,
  risePercent: 0,
  fallCount: 0,
  fallPercent: 0,
  limitUpCount: 0,
  limitDownCount: 0,  // 初始化跌停统计
  totalAmount: '0'
})

// 涨跌分布数据
const marketDistribution = ref<any>(null)

// WebSocket连接
let ws: WebSocket | null = null
let reconnectTimer: NodeJS.Timeout | null = null

// 加载数据
const loadData = async () => {
  loading.value = true

  try {
    console.log('开始加载热点分析数据...')

    // 并行请求多个API
    const [categoriesRes, hotStocksRes, marketSummaryRes] = await Promise.all([
      fetch(`/api/v1/market/sector-performance?limit=50`),
      fetch(`/api/v1/market/hot-stocks?limit=100`),
      fetch(`/api/v1/market/market-summary`)
    ])

    const categoriesData = await categoriesRes.json()
    const hotStocksData = await hotStocksRes.json()
    const marketSummaryData = await marketSummaryRes.json()

    // 处理板块数据
    if (categoriesData.success && categoriesData.sectors) {
      const sectorsData = categoriesData.sectors

      // 提取板块数据
      sectors.value = sectorsData.map((s: any) => ({
        id: s.sector_code,
        name: s.sector_name,
        code: s.sector_code,
        changePercent: Number(s.change_pct).toFixed(2),  // 保留2位小数
        stockCount: s.stocks_count,
        amount: s.amount,
        price: s.price,
        topStocks: []  // 添加空数组，防止SectorMonitor组件报错
      }))
      console.log('板块数据:', sectors.value.length)
    }

    // 处理热门股票数据
    if (hotStocksData.success && hotStocksData.hot_stocks) {
      const stocks = hotStocksData.hot_stocks

      console.log('📊 原始股票数据样例:', stocks[0])

      // 按涨跌幅排序
      const sortedByRise = [...stocks].sort((a, b) => b.change_pct - a.change_pct)
      rankings.value.topRise = sortedByRise.slice(0, 100).map((s: any) => ({
        code: s.symbol,  // 映射: symbol -> code
        name: s.name,
        current_price: s.current_price,  // 映射: current_price -> current_price
        changePercent: Number(s.change_pct).toFixed(2),  // 格式化为2位小数
        amount: s.amount,
        volume: s.volume || 0,
        market: 'SH'  // 默认市场
      }))

      console.log('📈 涨幅榜样例:', rankings.value.topRise[0])

      // 按跌幅排序
      const sortedByFall = [...stocks].sort((a, b) => a.change_pct - b.change_pct)
      rankings.value.topFall = sortedByFall.slice(0, 100).map((s: any) => ({
        code: s.symbol,  // 映射: symbol -> code
        name: s.name,
        current_price: s.current_price,  // 映射: current_price -> current_price
        changePercent: Number(s.change_pct).toFixed(2),  // 格式化为2位小数
        amount: s.amount,
        volume: s.volume || 0,
        market: 'SH'  // 默认市场
      }))

      // 按成交额排序
      const sortedByAmount = [...stocks].sort((a, b) => b.amount - a.amount)
      rankings.value.topAmount = sortedByAmount.slice(0, 100).map((s: any) => ({
        code: s.symbol,  // 映射: symbol -> code
        name: s.name,
        current_price: s.current_price,  // 映射: current_price -> current_price
        changePercent: Number(s.change_pct).toFixed(2),  // 格式化为2位小数
        amount: s.amount,
        volume: s.volume || 0,
        market: 'SH'  // 默认市场
      }))

      console.log('✅ 排行榜数据:', rankings.value.topRise.length)
    }

    // 处理市场统计数据
    if (marketSummaryData.success && marketSummaryData.market_summary) {
      const summary = marketSummaryData.market_summary
      marketStats.value.riseCount = summary.rising_stocks
      marketStats.value.fallCount = summary.falling_stocks
      marketStats.value.limitUpCount = summary.limit_up_count
      marketStats.value.limitDownCount = summary.limit_down_count  // 添加跌停统计
      marketStats.value.totalAmount = Number(summary.total_amount_yi).toFixed(2)  // 保留2位小数
      marketStats.value.risePercent = Number(summary.rising_percent).toFixed(2)  // 保留2位小数
      marketStats.value.fallPercent = Number(summary.falling_percent).toFixed(2)  // 保留2位小数

      // 获取涨跌分布数据
      if (summary.distribution) {
        marketDistribution.value = summary.distribution
      }

      console.log('市场统计:', marketStats.value)
    }

    loading.value = false

    // 智能推荐（使用涨幅榜前100）
    const allRise = rankings.value.topRise || []
    recommendations.value.superHot = allRise.slice(0, 10)
    recommendations.value.hot = allRise.slice(10, 50)
    recommendations.value.watch = allRise.slice(50, 100)

    console.log('推荐数据:', recommendations.value)
    updateTimeText.value = '刚刚更新'
    lastUpdateTime = Date.now()
    lastFetchTime.value = Date.now() // 记录最后获取时间

  } catch (error) {
    console.error('加载热点分析数据失败:', error)
  } finally {
    loading.value = false
  }
}

let lastUpdateTime = Date.now()

// 刷新数据
const refreshData = () => {
  loadData()
}

// 显示股票详情
const showStockDetail = (stock: Stock) => {
  selectedStock.value = stock
  showDetail.value = true
}

// 显示市场指数K线图(880005)
const showMarketKline = () => {
  // 创建880005市场指数的stock对象
  const marketIndex: Stock = {
    code: '880005',
    name: 'A股大盘',
    changePercent: 0,
    volume: 0,
    amount: 0,
    market: '1'
  }

  selectedStock.value = marketIndex
  showDetail.value = true

  console.log('显示880005市场指数K线图', marketIndex)
}

// 按板块筛选
const filterBySector = (sector: Sector) => {
  console.log('筛选板块:', sector.name)
  // TODO: 实现板块筛选逻辑
}

// WebSocket实时推送
const connectWebSocket = () => {
  // 根据页面协议自动选择ws://或wss://
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}/api/v1/hotspot/stream`

  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    console.log('WebSocket连接成功')
    isRealtime.value = true
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)

    switch (data.type) {
      case 'rankings_update':
        rankings.value = data.data
        break
      case 'sectors_update':
        sectors.value = data.data.sectors
        marketStats.value = data.data.marketStats
        break
      case 'recommendations_update':
        recommendations.value = data.data
        break
    }

    lastUpdateTime = Date.now()
    updateTimeText.value = '实时更新'
  }

  ws.onerror = (error) => {
    console.error('WebSocket错误:', error)
    isRealtime.value = false
  }

  ws.onclose = () => {
    console.log('WebSocket连接关闭')
    isRealtime.value = false

    // 5秒后重连
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
    }
    reconnectTimer = setTimeout(() => {
      console.log('尝试重新连接WebSocket...')
      connectWebSocket()
    }, 5000)
  }
}

// 生命周期
onMounted(() => {
  console.log('onMounted: 初始加载数据')
  loadData()
  // WebSocket暂时禁用，等待后端完全配置
  // connectWebSocket()
})

// 页面激活时(从其他页面切换回来)
onActivated(() => {
  const now = Date.now()
  const timeSinceLastFetch = now - lastFetchTime.value
  const cacheAge = Math.floor(timeSinceLastFetch / 1000)

  console.log(`onActivated: 页面激活, 缓存时间 ${cacheAge}秒`)

  // 如果缓存过期(超过30秒)或者没有数据,则重新获取
  if (timeSinceLastFetch > CACHE_DURATION || !marketDistribution.value) {
    console.log('缓存已过期或无数据, 重新获取...')
    updateTimeText.value = '正在刷新...'
    loadData()
  } else {
    console.log(`使用缓存数据 (缓存有效期内, 还有${30 - cacheAge}秒过期)`)
    updateTimeText.value = `使用缓存 (${cacheAge}秒前更新)`
  }
})

// 页面失活时(切换到其他页面)
onDeactivated(() => {
  console.log('onDeactivated: 页面失活, 保持数据缓存')
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
  }
})
</script>

<style scoped lang="scss">
.hotspot-analysis-container {
  width: 100%;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: var(--bg-deep);
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: var(--bg-surface);
  border-radius: 16px;
  border: 1px solid var(--border-light);

  .header-left {
    .page-title {
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0 0 8px 0;
      display: flex;
      align-items: center;
      gap: 12px;

      i {
        color: #ef4444;
        animation: pulse 2s infinite;
      }
    }

    .page-subtitle {
      font-size: 14px;
      color: var(--text-secondary);
      margin: 0;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .update-info {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: var(--bg-elevated);
      border-radius: 20px;

      .update-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #9ca3af;
        transition: all 0.3s;

        &.active {
          background: #10b981;
          box-shadow: 0 0 8px #10b981;
        }
      }

      .update-text {
        font-size: 13px;
        color: var(--text-secondary);
      }
    }

    .refresh-btn {
      padding: 10px 20px;
      background: var(--primary-color);
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s;
      display: flex;
      align-items: center;
      gap: 8px;

      &:hover:not(:disabled) {
        opacity: 0.9;
        transform: translateY(-1px);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.market-distribution-section {
  margin-bottom: 16px;
}

.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  min-height: 0;

  .left-panel,
  .center-panel,
  .right-panel {
    background: var(--bg-surface);
    border-radius: 16px;
    border: 1px solid var(--border-light);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
}

.bottom-panel {
  height: 300px;
  background: var(--bg-surface);
  border-radius: 16px;
  border: 1px solid var(--border-light);
  overflow: hidden;
}

@media (max-width: 1400px) {
  .main-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    overflow-y: auto;
  }

  .quick-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* End of style */

</style>
