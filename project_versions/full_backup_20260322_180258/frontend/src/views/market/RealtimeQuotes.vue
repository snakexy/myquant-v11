<template>
  <div class="realtime-quotes-view">
    <div class="main-container">
      <div class="content-area">
        <!-- 左侧股票列表 -->
        <div class="panel watchlist-panel">
          <div class="panel-header">
            <span>自选列表</span>
            <div class="panel-actions">
              <button class="panel-btn" @click="showAddStock = true" title="添加股票">+</button>
            </div>
          </div>

          <!-- 搜索框 -->
          <div class="search-section">
            <input
              v-model="searchSymbol"
              type="text"
              placeholder="输入代码 (如 600000.SH)"
              class="search-input"
              @keyup.enter="addStock"
            />
            <button @click="addStock" class="add-btn">添加</button>
          </div>

          <div class="stock-list">
            <div
              v-for="stock in watchlist"
              :key="stock.code"
              :class="['stock-item', { selected: selectedStock === stock.code }]"
              @click="selectStock(stock.code)"
            >
              <div class="stock-info">
                <div class="stock-code">{{ stock.code }}</div>
                <div class="stock-name">{{ stock.name }}</div>
              </div>
              <div :class="['stock-price', stock.change >= 0 ? 'positive' : 'negative']">
                {{ stock.price }}
              </div>
              <div :class="['stock-change', stock.change >= 0 ? 'positive' : 'negative']">
                {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
              </div>
            </div>
          </div>
        </div>

        <!-- 中间图表区域 -->
        <div class="chart-area">
          <div class="chart-toolbar">
            <span class="current-stock-name">{{ currentStockName }}</span>
            <div class="toolbar-right">
              <button
                v-for="tf in timeframes"
                :key="tf.value"
                :class="['timeframe-btn', { active: currentTimeframe === tf.value }]"
                @click="changeTimeframe(tf.value)"
              >
                {{ tf.label }}
              </button>
              <div class="toolbar-divider-v"></div>
              <button
                :class="['timeframe-btn', { active: adjustType === 'none' }]"
                @click="changeAdjustType('none')"
              >
                不复权
              </button>
              <button
                :class="['timeframe-btn', { active: adjustType === 'qfq' }]"
                @click="changeAdjustType('qfq')"
              >
                前复权
              </button>
            </div>
          </div>

          <!-- K线图容器 -->
          <div class="chart-container">
            <div ref="chartContainer" class="kline-chart"></div>
            <div ref="volumeContainer" class="volume-chart"></div>

            <!-- 加载状态 -->
            <div v-if="loading" class="chart-loading">
              <div class="spinner"></div>
              <span>加载中...</span>
            </div>
          </div>
        </div>

        <!-- 右侧信息面板 -->
        <div class="panel info-panel">
          <div class="panel-header">
            <span>行情详情</span>
          </div>

          <div class="trade-section">
            <div class="price-display">
              <div :class="['current-price', currentQuote.change >= 0 ? 'positive' : 'negative']">
                {{ currentQuote.price || '--' }}
              </div>
              <div :class="['price-change', currentQuote.change >= 0 ? 'positive' : 'negative']">
                {{ currentQuote.change >= 0 ? '+' : '' }}{{ currentQuote.change }}
                ({{ currentQuote.change_percent >= 0 ? '+' : '' }}{{ currentQuote.change_percent }}%)
              </div>
            </div>
          </div>

          <div class="trade-section">
            <div class="section-title">五档盘口</div>
            <div class="order-book">
              <div class="order-column">
                <div v-for="(ask, i) in asks" :key="'ask'+i" class="order-row sell">
                  <span>卖 {{ 5 - i }}</span>
                  <span class="order-price">{{ ask.price }}</span>
                  <span class="order-size">{{ ask.size }}</span>
                </div>
              </div>
              <div class="order-column">
                <div v-for="(bid, i) in bids" :key="'bid'+i" class="order-row buy">
                  <span>买 {{ i + 1 }}</span>
                  <span class="order-price">{{ bid.price }}</span>
                  <span class="order-size">{{ bid.size }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="trade-section">
            <div class="section-title">统计数据</div>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">开盘</div>
                <div class="info-value">{{ currentQuote.open || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">最高</div>
                <div class="info-value">{{ currentQuote.high || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">最低</div>
                <div class="info-value">{{ currentQuote.low || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">昨收</div>
                <div class="info-value">{{ currentQuote.prev_close || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">成交量</div>
                <div class="info-value">{{ formatVolume(currentQuote.volume) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">成交额</div>
                <div class="info-value">{{ formatAmount(currentQuote.amount) }}</div>
              </div>
            </div>
          </div>

          <div class="trade-section">
            <div class="section-title">数据源</div>
            <div class="data-source-info">
              <span class="data-source-label">{{ dataSource }}</span>
              <span class="update-time">{{ updateTime }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部状态栏 -->
      <div class="statusbar">
        <div class="statusbar-section">
          <span class="stock-name-display">{{ currentStockName }}</span>
          <div class="statusbar-divider"></div>
          <span>成交: {{ formatAmount(currentQuote.amount) }}</span>
          <span style="margin-left: auto;">实时行情</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { createChart, CrosshairMode, CandlestickSeries, HistogramSeries } from 'lightweight-charts'
import {
  fetchKline,
  fetchSnapshot,
  fetchSnapshotBatch,
  fetchMarketStatus,
  type KlineItem,
  type QuoteSnapshot,
  type MarketStatus
} from '@/api/modules/quotes'

// 类型定义
type ChartApi = any
type SeriesApi = any

// 周期选项
const timeframes = [
  { label: '分时', value: '1m' },
  { label: '5分', value: '5m' },
  { label: '15分', value: '15m' },
  { label: '30分', value: '30m' },
  { label: '60分', value: '1h' },
  { label: '日K', value: '1d' },
  { label: '周K', value: '1w' }
]

// 状态
const searchSymbol = ref('')
const selectedStock = ref('600000.SH')
const currentTimeframe = ref('1d')
const loading = ref(false)
const showAddStock = ref(false)
const dataSource = ref('XtQuant')
const updateTime = ref('')
const adjustType = ref('qfq')

// 当前行情数据
const currentQuote = ref({
  price: '--',
  change: 0,
  change_percent: 0,
  open: '--',
  high: '--',
  low: '--',
  prev_close: '--',
  volume: 0,
  amount: 0
})

// 自选股列表
const watchlist = ref([
  { code: '600000.SH', name: '浦发银行', price: '--', change: 0 },
  { code: '000001.SZ', name: '平安银行', price: '--', change: 0 },
  { code: '600519.SH', name: '贵州茅台', price: '--', change: 0 },
  { code: '000858.SZ', name: '五粮液', price: '--', change: 0 }
])

// 五档盘口数据（从API获取）
const asks = ref([
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 }
])

const bids = ref([
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 },
  { price: '--', size: 0 }
])

// 图表实例
const chartContainer = ref<HTMLElement>()
const volumeContainer = ref<HTMLElement>()
let chart: ChartApi | null = null
let candleSeries: SeriesApi | null = null
let volumeSeries: SeriesApi | null = null
let updateTimer: number | null = null

// 当前股票名称
const currentStockName = computed(() => {
  const stock = watchlist.value.find(s => s.code === selectedStock.value)
  return stock ? `${stock.name} (${stock.code})` : selectedStock.value
})

// 格式化成交量
const formatVolume = (vol: number): string => {
  if (!vol) return '--'
  if (vol >= 100000000) return (vol / 100000000).toFixed(2) + '亿'
  if (vol >= 10000) return (vol / 10000).toFixed(2) + '万'
  return vol.toString()
}

// 格式化成交额
const formatAmount = (amt: number): string => {
  if (!amt) return '--'
  if (amt >= 100000000) return (amt / 100000000).toFixed(2) + '亿'
  if (amt >= 10000) return (amt / 10000).toFixed(2) + '万'
  return amt.toString()
}

// 初始化图表
const initChart = () => {
  if (!chartContainer.value || !volumeContainer.value) return

  // 创建主图表
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: chartContainer.value.clientHeight,
    layout: {
      background: { color: '#131722' },
      textColor: '#d1d4dc'
    },
    grid: {
      vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
      horzLines: { color: 'rgba(42, 46, 57, 0.5)' }
    },
    crosshair: {
      mode: CrosshairMode.Normal
    },
    rightPriceScale: {
      borderColor: 'rgba(197, 203, 206, 0.8)'
    },
    timeScale: {
      borderColor: 'rgba(197, 203, 206, 0.8)',
      timeVisible: true,
      secondsVisible: false,
      minBarSpacing: 0.5,     // 最小K线间距（0.5像素）
      rightOffset: 10,        // 右侧留白10%
      fixLeftEdge: true,      // 固定左边缘
      fixRightEdge: false     // 不固定右边缘，允许滚动
    },
    // 时间轴配置
    localization: {
      dateFormat: 'yyyy-MM-dd',
      timeFormatter: (timestamp: number) => {
        // 时间戳是 UTC，需要显示为北京时间
        const date = new Date(timestamp * 1000)
        // 使用 UTC 时间 + 8小时 = 北京时间
        const beijingDate = new Date(date.getTime() + 8 * 60 * 60 * 1000)
        const year = beijingDate.getUTCFullYear()
        const month = String(beijingDate.getUTCMonth() + 1).padStart(2, '0')
        const day = String(beijingDate.getUTCDate()).padStart(2, '0')
        const hours = String(beijingDate.getUTCHours()).padStart(2, '0')
        const minutes = String(beijingDate.getUTCMinutes()).padStart(2, '0')
        return `${year}-${month}-${day} ${hours}:${minutes}`
      }
    }
  })

  // 创建K线系列（中国股市：红涨绿跌）
  candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#ef5350',        // 上涨红色（默认）
    downColor: '#26a69a',      // 下跌绿色（默认）
    borderVisible: false,
    wickUpColor: '#ef5350',    // 上影线红色
    wickDownColor: '#26a69a',   // 下影线绿色
    // 使用自定义颜色对象，根据API返回的color字段设置每根K线的颜色
    // 注意：需要将数据格式转换为lightweight-charts支持的格式
  })

  // 创建成交量系列
  volumeSeries = chart.addSeries(HistogramSeries, {
    color: '#26a69a',
    priceFormat: {
      type: 'volume'
    },
    priceScaleId: 'volume'
  })

  chart.priceScale('volume').applyOptions({
    scaleMargins: {
      top: 0.8,
      bottom: 0
    }
  })

  // 响应式调整
  const resizeObserver = new ResizeObserver(() => {
    if (chart && chartContainer.value) {
      chart.applyOptions({
        width: chartContainer.value.clientWidth
      })
    }
  })
  resizeObserver.observe(chartContainer.value)
}

// 加载K线数据
const isInitialLoad = ref(true)  // 标记是否为初始加载

const loadKlineData = async () => {
  if (!selectedStock.value) return

  loading.value = true
  try {
    // 并行获取 K线数据、当前股票快照、所有自选股批量快照
    const allSymbols = watchlist.value.map(s => s.code)
    const [klineRes, snapshotRes, batchRes] = await Promise.all([
      fetchKline(selectedStock.value, currentTimeframe.value, 800, adjustType.value),
      fetchSnapshot(selectedStock.value),
      fetchSnapshotBatch(allSymbols)
    ])

    // 处理K线数据
    console.log('=== 调试：klineRes 完整内容 ===', klineRes)
    console.log('=== klineRes.data 类型 ===', typeof klineRes.data, Array.isArray(klineRes.data))

    if (klineRes.data && klineRes.data.length > 0) {
      dataSource.value = klineRes.data_source || 'Unknown'
      updateTime.value = new Date().toLocaleTimeString()

      // 调试：打印原始数据
      console.log('原始K线数据 (前3条):', klineRes.data.slice(0, 3))

      // 设置K线数据
      // 日K线使用 YYYY-MM-DD 字符串格式，避免时区问题
      const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
      const klineDataWithSeconds = klineRes.data
        .map((item: KlineItem, index: number) => {
          const ts = Number(item.time)

          if (index < 5) {
            console.log(`索引 ${index}:`, {
              original: item.time,
              date: new Date(ts).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
            })
          }

          // 统一使用秒级时间戳（后端已发送正确的时间戳）
          const timeValue = Math.floor(ts / 1000)

          // 验证
          if (isFinite(timeValue) && timeValue < 0) {
            console.error(`❌ 无效时间戳 (索引 ${index}):`, item)
            return null
          }

          return {
            time: timeValue,
            open: Number(item.open),
            high: Number(item.high),
            low: Number(item.low),
            close: Number(item.close),
            volume: Number(item.volume)
          }
        })
        .filter((item): item is { time: number | string } => item !== null)

      console.log('过滤后的数据量:', klineDataWithSeconds.length, '原始数据量:', klineRes.data.length)

      // 验证数据是否按时间排序
      const isSorted = klineDataWithSeconds.every((item, i) =>
        i === 0 || (item.time as number) >= (klineDataWithSeconds[i - 1].time as number)
      )
      console.log('数据是否按时间排序:', isSorted)

      if (!isSorted) {
        console.error('❌ 数据未按时间排序!')
        console.log('前5条数据:', klineDataWithSeconds.slice(0, 5))
      }

      console.log('准备设置的数据 (前3条):', klineDataWithSeconds.slice(0, 3))

      candleSeries?.setData(klineDataWithSeconds)

      // 设置成交量数据（统一使用秒级时间戳）
      const volumeData = klineRes.data.map((item: KlineItem) => {
        const ts = Number(item.time)
        const timeValue = Math.floor(ts / 1000)

        return {
          time: timeValue,
          value: item.volume,
          color: item.color ? item.color + '80' : '#ef535080'
        }
      })
      volumeSeries?.setData(volumeData)
    }

    // 批量更新所有自选股的价格
    if (batchRes.data && batchRes.data.length > 0) {
      const quoteMap = new Map(batchRes.data.map(q => [q.symbol, q]))
      for (const stock of watchlist.value) {
        const quote = quoteMap.get(stock.code)
        if (quote) {
          stock.price = quote.price.toFixed(2)
          stock.change = parseFloat(quote.change_percent.toFixed(2))
        }
      }
    }

    if (isInitialLoad.value) {
      chart?.timeScale().fitContent()
      isInitialLoad.value = false
    }

    // 处理当前股票快照数据（更新右侧详情面板）
    updateQuoteFromSnapshot(snapshotRes)
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 从快照数据更新当前行情和五档盘口
const updateQuoteFromSnapshot = (quote: QuoteSnapshot) => {
  currentQuote.value = {
    price: quote.price ? quote.price.toFixed(2) : '--',
    change: quote.change ? quote.change.toFixed(2) : 0,
    change_percent: quote.change_percent ? quote.change_percent.toFixed(2) : 0,
    open: quote.open ? quote.open.toFixed(2) : '--',
    high: quote.high ? quote.high.toFixed(2) : '--',
    low: quote.low ? quote.low.toFixed(2) : '--',
    prev_close: quote.prev_close ? quote.prev_close.toFixed(2) : '--',
    volume: quote.volume || 0,
    amount: quote.amount || 0
  }
  updateOrderBookFromSnapshot(quote)
}

// 从快照数据更新五档盘口
const updateOrderBookFromSnapshot = (quote: QuoteSnapshot) => {
  // 卖盘（价格从高到低：ask5 → ask1）
  // 注意：0 是有效值（无挂单），只有 null/undefined 才显示 '--'
  asks.value = [
    { price: quote.ask5 != null ? Number(quote.ask5).toFixed(2) : '--', size: quote.ask_vol5 ?? 0 },
    { price: quote.ask4 != null ? Number(quote.ask4).toFixed(2) : '--', size: quote.ask_vol4 ?? 0 },
    { price: quote.ask3 != null ? Number(quote.ask3).toFixed(2) : '--', size: quote.ask_vol3 ?? 0 },
    { price: quote.ask2 != null ? Number(quote.ask2).toFixed(2) : '--', size: quote.ask_vol2 ?? 0 },
    { price: quote.ask1 != null ? Number(quote.ask1).toFixed(2) : '--', size: quote.ask_vol1 ?? 0 }
  ]

  // 买盘（价格从低到高：bid1 → bid5）
  bids.value = [
    { price: quote.bid1 != null ? Number(quote.bid1).toFixed(2) : '--', size: quote.bid_vol1 ?? 0 },
    { price: quote.bid2 != null ? Number(quote.bid2).toFixed(2) : '--', size: quote.bid_vol2 ?? 0 },
    { price: quote.bid3 != null ? Number(quote.bid3).toFixed(2) : '--', size: quote.bid_vol3 ?? 0 },
    { price: quote.bid4 != null ? Number(quote.bid4).toFixed(2) : '--', size: quote.bid_vol4 ?? 0 },
    { price: quote.bid5 != null ? Number(quote.bid5).toFixed(2) : '--', size: quote.bid_vol5 ?? 0 }
  ]
}

// 选择股票
const selectStock = (code: string) => {
  selectedStock.value = code
  isInitialLoad.value = true  // 切换股票时重新适应显示范围
  loadKlineData()
}

// 切换周期
const changeTimeframe = (tf: string) => {
  currentTimeframe.value = tf
  isInitialLoad.value = true  // 切换周期时重新适应显示范围
  loadKlineData()
}

// 切换复权类型
const changeAdjustType = (type: string) => {
  adjustType.value = type
  isInitialLoad.value = true
  loadKlineData()
}

// 添加股票
const addStock = () => {
  const code = searchSymbol.value.trim().toUpperCase()
  if (code && !watchlist.value.find(s => s.code === code)) {
    watchlist.value.push({
      code,
      name: code,
      price: '--',
      change: 0
    })
    searchSymbol.value = ''
    selectStock(code)
  }
}

// 实时更新（根据市场状态动态调整刷新间隔）
const startRealtimeUpdate = async () => {
  const getRefreshInterval = async (): Promise<number> => {
    try {
      const status: MarketStatus = await fetchMarketStatus()
      return status.refresh_interval * 1000
    } catch {
      return 5000
    }
  }

  const interval = await getRefreshInterval()
  updateTimer = window.setInterval(async () => {
    if (selectedStock.value) {
      loadKlineData()
    }
  }, interval)
}

onMounted(() => {
  nextTick(() => {
    initChart()
    loadKlineData()
    startRealtimeUpdate()
  })
})

onBeforeUnmount(() => {
  if (updateTimer) {
    clearInterval(updateTimer)
  }
  if (chart) {
    chart.remove()
  }
})
</script>

<style scoped>
/* 使用全局配色 - TradingView 风格 */
.realtime-quotes-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #131722;
  color: #d1d4dc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 主容器 */
.main-container {
  display: grid;
  grid-template-rows: 1fr 28px;
  flex: 1;
  min-height: 0;
}

.content-area {
  display: grid;
  grid-template-columns: 260px 1fr 280px;
  gap: 1px;
  background: #2a2e39;
  overflow: hidden;
}

/* 面板 */
.panel {
  background: #131722;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  background: #1e222d;
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #d1d4dc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #2a2e39;
}

.panel-actions {
  display: flex;
  gap: 4px;
}

.panel-btn {
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  color: #787b86;
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.panel-btn:hover {
  background: #2a2e39;
  color: #d1d4dc;
}

/* 搜索区域 */
.search-section {
  padding: 10px;
  display: flex;
  gap: 6px;
  border-bottom: 1px solid #2a2e39;
}

.search-input {
  flex: 1;
  padding: 6px 10px;
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 12px;
}

.search-input:focus {
  outline: none;
  border-color: #ef5350;  /* 红色边框 */
}

.add-btn {
  padding: 6px 12px;
  background: #ef5350;  /* 红色按钮 */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.add-btn:hover {
  background: #e53935;  /* 深红色 */
}

/* 股票列表 */
.stock-list {
  flex: 1;
  overflow-y: auto;
}

.stock-item {
  display: grid;
  grid-template-columns: 1fr 70px 60px;
  gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid #2a2e39;
  cursor: pointer;
  transition: background 0.15s;
}

.stock-item:hover {
  background: #1e222d;
}

.stock-item.selected {
  background: #2a2e39;
  border-left: 2px solid #ef5350;  /* 红色左边框 */
}

.stock-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stock-code {
  color: #d1d4dc;
  font-size: 13px;
  font-weight: 600;
}

.stock-name {
  color: #787b86;
  font-size: 11px;
}

.stock-price {
  text-align: right;
  font-weight: 600;
  font-size: 13px;
}

/* 中国股市：红涨绿跌 */
.stock-price.positive { color: #ef5350; }  /* 上涨红色 */
.stock-price.negative { color: #26a69a; }  /* 下跌绿色 */

.stock-change {
  text-align: right;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.stock-change.positive {
  background: rgba(239, 83, 80, 0.15);
  color: #ef5350;
}

.stock-change.negative {
  background: rgba(38, 166, 154, 0.15);
  color: #26a69a;
}

/* 图表区域 */
.chart-area {
  display: flex;
  flex-direction: column;
  background: #131722;
}

.chart-toolbar {
  background: #1e222d;
  border-bottom: 1px solid #2a2e39;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.current-stock-name {
  color: #d1d4dc;
  font-weight: 600;
  font-size: 14px;
}

.toolbar-right {
  display: flex;
  gap: 4px;
}

.toolbar-divider-v {
  width: 1px;
  height: 20px;
  background: #363a45;
  margin: 0 6px;
  align-self: center;
}

.timeframe-btn {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #363a45;
  color: #d1d4dc;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  border-radius: 4px;
  transition: all 0.2s;
}

.timeframe-btn:hover {
  background: #2a2e39;
}

.timeframe-btn.active {
  background: #ef5350;  /* 激活状态红色 */
  border-color: #ef5350;
  color: white;
}

.chart-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.kline-chart {
  flex: 1;
}

.volume-chart {
  height: 100px;
  border-top: 1px solid #2a2e39;
}

.chart-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #d1d4dc;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #363a45;
  border-top-color: #ef5350;  /* 红色 spinner */
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 信息面板 */
.info-panel {
  display: flex;
  flex-direction: column;
}

.trade-section {
  padding: 16px;
  border-bottom: 1px solid #2a2e39;
}

.section-title {
  font-size: 11px;
  color: #787b86;
  margin-bottom: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.price-display {
  text-align: center;
}

.current-price {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.current-price.positive { color: #ef5350; }  /* 上涨红色 */
.current-price.negative { color: #26a69a; }  /* 下跌绿色 */

.price-change {
  font-size: 14px;
  margin-top: 6px;
  font-weight: 600;
}

.price-change.positive { color: #ef5350; }  /* 上涨红色 */
.price-change.negative { color: #26a69a; }  /* 下跌绿色 */

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-item {
  background: #1e222d;
  padding: 10px 12px;
  border-radius: 4px;
}

.info-label {
  font-size: 10px;
  color: #787b86;
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
}

.data-source-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-source-label {
  color: #ef5350;  /* 红色标签 */
  font-weight: 600;
  font-size: 13px;
}

.update-time {
  color: #787b86;
  font-size: 11px;
}

/* 五档盘口 */
.order-book {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.order-column {
  background: #1e222d;
  border-radius: 4px;
  overflow: hidden;
}

.order-row {
  display: grid;
  grid-template-columns: 1fr 1fr 45px;
  gap: 4px;
  padding: 6px 8px;
  font-size: 11px;
  border-bottom: 1px solid #2a2e39;
}

.order-row:last-child {
  border-bottom: none;
}

.order-row.buy { color: #ef5350; }  /* 买盘红色（主动买入） */
.order-row.sell { color: #26a69a; }  /* 卖盘绿色（主动卖出） */

.order-price {
  text-align: right;
  font-weight: 600;
}

.order-size {
  text-align: right;
}

/* 底部状态栏 */
.statusbar {
  background: #1e222d;
  border-top: 1px solid #2a2e39;
  padding: 0 16px;
  display: flex;
  align-items: center;
  font-size: 11px;
  color: #787b86;
}

.statusbar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 6px 0;
  width: 100%;
}

.statusbar-divider {
  width: 1px;
  height: 14px;
  background: #2a2e39;
}

.stock-name-display {
  color: #d1d4dc;
  font-weight: 600;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #131722;
}

::-webkit-scrollbar-thumb {
  background: #363a45;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #434651;
}
</style>
