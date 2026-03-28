<template>
  <div class="realtime-quotes-view">
    <GlobalNavBar />

    <div class="main-container">
      <div class="content-area">
        <!-- 左侧股票列表 -->
        <WatchlistPanel
          :selected-stock="selectedStock"
          :mini-charts-data="miniChartsData"
          @select-stock="selectStock"
        />

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
                {{ isZh ? '不复权' : 'Raw' }}
              </button>
              <button
                :class="['timeframe-btn', { active: adjustType === 'qfq' }]"
                @click="changeAdjustType('qfq')"
              >
                {{ isZh ? '前复权' : 'Adj' }}
              </button>
            </div>
          </div>

          <!-- K线图容器（副图指标通过 chart.addPane() 在同一实例内开） -->
          <div class="chart-container">
            <div ref="chartContainer" class="kline-chart"></div>

            <!-- OHLCV legend 悬浮在图表左上角 -->
            <div v-if="hoverBar" class="chart-legend-overlay">
              <span class="legend-time">{{ hoverBar.time }}</span>
              <span class="legend-item">O <em :class="hoverBar.close>=hoverBar.open?'positive':'negative'">{{ hoverBar.open?.toFixed(2) }}</em></span>
              <span class="legend-item">H <em :class="hoverBar.close>=hoverBar.open?'positive':'negative'">{{ hoverBar.high?.toFixed(2) }}</em></span>
              <span class="legend-item">L <em :class="hoverBar.close>=hoverBar.open?'positive':'negative'">{{ hoverBar.low?.toFixed(2) }}</em></span>
              <span class="legend-item">C <em :class="hoverBar.close>=hoverBar.open?'positive':'negative'">{{ hoverBar.close?.toFixed(2) }}</em></span>
              <span class="legend-item">V <em>{{ formatVolume(hoverBar.volume) }}</em></span>
            </div>

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
            <div class="stock-info-header">
              <div class="stock-name-large">{{ currentStockName || '--' }}</div>
              <div class="stock-code-small">{{ selectedStock || '--' }}</div>
            </div>
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
            <div class="section-title">{{ isZh ? '五档盘口' : 'Order Book' }}</div>
            <div class="order-book">
              <div class="order-column">
                <div v-for="(ask, i) in asks.slice().reverse()" :key="'ask'+i" class="order-row sell">
                  <span>{{ isZh ? '卖' : 'Sell' }} {{ i + 1 }}</span>
                  <span class="order-price">{{ ask.price }}</span>
                  <span class="order-size">
                    <span class="size-bar" :style="{ width: getSizePercent(ask.size) + '%' }"></span>
                    {{ formatOrderSize(ask.size) }}
                  </span>
                </div>
              </div>
              <div class="order-column">
                <div v-for="(bid, i) in bids" :key="'bid'+i" class="order-row buy">
                  <span>{{ isZh ? '买' : 'Buy' }} {{ i + 1 }}</span>
                  <span class="order-price">{{ bid.price }}</span>
                  <span class="order-size">
                    <span class="size-bar" :style="{ width: getSizePercent(bid.size) + '%' }"></span>
                    {{ formatOrderSize(bid.size) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="trade-section">
            <div class="section-title">{{ isZh ? '统计数据' : 'Stats' }}</div>
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">{{ isZh ? '开盘' : 'Open' }}</div>
                <div class="info-value">{{ currentQuote.open || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '最高' : 'High' }}</div>
                <div class="info-value">{{ currentQuote.high || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '最低' : 'Low' }}</div>
                <div class="info-value">{{ currentQuote.low || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '昨收' : 'Prev' }}</div>
                <div class="info-value">{{ currentQuote.prev_close || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '成交量' : 'Volume' }}</div>
                <div class="info-value">{{ formatVolume(currentQuote.volume) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '成交额' : 'Amount' }}</div>
                <div class="info-value">{{ formatAmount(currentQuote.amount) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '换手率' : 'Turnover' }}</div>
                <div class="info-value">{{ currentQuote.turnover_rate ? currentQuote.turnover_rate + '%' : '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '总量' : 'Volume' }}</div>
                <div class="info-value">{{ formatVolume(currentQuote.volume) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '振幅' : 'Amplitude' }}</div>
                <div class="info-value">{{ currentQuote.amplitude ? currentQuote.amplitude + '%' : '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '量比' : 'Vol Ratio' }}</div>
                <div class="info-value" :class="currentQuote.volume_ratio > 1 ? 'positive' : currentQuote.volume_ratio < 1 ? 'negative' : ''">{{ currentQuote.volume_ratio || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '外盘' : 'Outer' }}</div>
                <div class="info-value positive">{{ formatVol(currentQuote.outer_vol) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '内盘' : 'Inner' }}</div>
                <div class="info-value negative">{{ formatVol(currentQuote.inner_vol) }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '市盈率' : 'P/E' }}</div>
                <div class="info-value">{{ currentQuote.pe_ratio || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '市净率' : 'P/B' }}</div>
                <div class="info-value">{{ currentQuote.pb_ratio || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '股息率' : 'Div Yield' }}</div>
                <div class="info-value">{{ currentQuote.dy_ratio ? currentQuote.dy_ratio + '%' : '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '涨停价' : 'Limit Up' }}</div>
                <div class="info-value positive">{{ currentQuote.zt_price || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '跌停价' : 'Limit Down' }}</div>
                <div class="info-value negative">{{ currentQuote.dt_price || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '贝塔系数' : 'Beta' }}</div>
                <div class="info-value">{{ currentQuote.beta || '--' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">{{ isZh ? '总股本' : 'Shares' }}</div>
                <div class="info-value">{{ formatShares(currentQuote.total_shares) }}</div>
              </div>
              <div class="info-item" style="grid-column: 1 / -1;">
                <div class="data-source-info">
                  <span class="data-source-label">{{ isZh ? '数据源' : 'Source' }}</span>
                  <span class="data-source-value">{{ currentQuote.data_source }}</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- 底部状态栏 -->
      <div class="statusbar">
        <div class="statusbar-section">
          <span class="stock-name-display">{{ currentStockName }}</span>
          <div class="statusbar-divider"></div>
          <span>{{ isZh ? '成交' : 'Vol' }}: {{ formatAmount(currentQuote.amount) }}</span>
          <div class="statusbar-divider"></div>
          <template v-for="idx in indices" :key="idx.code">
            <span class="index-item">
              <span class="index-name">{{ idx.name }}</span>
              <span :class="['index-price', idx.change >= 0 ? 'positive' : 'negative']">{{ idx.price }}</span>
              <span :class="['index-change', idx.change >= 0 ? 'positive' : 'negative']">
                {{ idx.change >= 0 ? '+' : '' }}{{ idx.change }}%
              </span>
            </span>
            <div class="statusbar-divider"></div>
          </template>
          <span style="margin-left: auto; color: #4a4f60;">实时行情</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { createChart, CrosshairMode, CandlestickSeries, HistogramSeries } from 'lightweight-charts'
import GlobalNavBar from '@/components/GlobalNavBar.vue'
import WatchlistPanel from '@/components/watchlist/WatchlistPanel.vue'
import { useAppStore } from '@/stores/core/AppStore'
import { useDataStore } from '@/stores/core/DataStore'
import {
  fetchKline,
  fetchSnapshot,
  fetchSnapshotBatch,
  fetchMarketStatus,
  type KlineItem,
  type QuoteSnapshot,
  type MarketStatus
} from '@/api/modules/quotes'
import { createKlineWebSocket, type KlineBar } from '@/services/klineWebSocket'
import { createKlineAggregator, type Timeframe } from '@/services/klineAggregator'

// 类型定义
type ChartApi = any
type SeriesApi = any

interface QuoteData {
  price: string | number
  change: number
  change_percent: number
  open: string | number
  high: string | number
  low: string | number
  prev_close: string | number
  volume: number
  amount: number
  turnover_rate: number
  amplitude: number
  volume_ratio: number
  outer_vol: number
  inner_vol: number
  pe_ratio: number
  pb_ratio: number
  dy_ratio: number
  zt_price: string | number
  dt_price: string | number
  beta: number
  total_shares: number
  data_source: string
}

// 周期选项（响应语言切换）
const timeframes = computed(() => [
  { label: isZh.value ? '分时' : '1m',   value: '1m' },
  { label: isZh.value ? '5分' : '5m',    value: '5m' },
  { label: isZh.value ? '15分' : '15m',  value: '15m' },
  { label: isZh.value ? '30分' : '30m',  value: '30m' },
  { label: isZh.value ? '60分' : '1h',   value: '1h' },
  { label: isZh.value ? '日K' : 'Day',   value: '1d' },
  { label: isZh.value ? '周K' : 'Week',  value: '1w' },
  { label: isZh.value ? '月K' : 'Month', value: '1M' },
])

// 从 localStorage 恢复上次选中的股票和周期
const getLastSelectedStock = (): string => {
  try {
    const saved = localStorage.getItem('realtime_quotes_last_stock')
    // 检查值是否有效（非空、不是 "undefined" 字符串）
    if (saved && saved !== 'undefined' && saved.trim()) {
      return saved
    }
  } catch (e) {}
  return ''
}

const getLastTimeframe = (): string => {
  try {
    const saved = localStorage.getItem('realtime_quotes_last_timeframe')
    // 检查值是否有效
    if (saved && saved !== 'undefined' && saved.trim()) {
      return saved
    }
  } catch (e) {}
  return '1d'  // 默认日线
}

const selectedStock = ref(getLastSelectedStock())
const currentTimeframe = ref(getLastTimeframe())
const appStore = useAppStore()
const dataStore = useDataStore()
const isZh = computed(() => appStore.language === 'zh')

const loading = ref(false)
const adjustType = ref('qfq')

// 后端 change_pct 字段兼容工具（pytdx 返回 change_pct，部分接口返回 change_percent）
const getChangePct = (q: any): number => parseFloat(Number(q.change_pct ?? q.change_percent ?? 0).toFixed(2))

// miniCharts removed, using miniChartsData with time-based X-axis instead

// 沪深指数
const indices = ref([
  { code: '000001.SH', name: '上证', price: '--', change: 0 },
  { code: '399001.SZ', name: '深证', price: '--', change: 0 },
  { code: '399006.SZ', name: '创业板', price: '--', change: 0 },
])

// 当前行情数据
const currentQuote = ref<QuoteData>({
  price: '--',
  change: 0,
  change_percent: 0,
  open: '--',
  high: '--',
  low: '--',
  prev_close: '--',
  volume: 0,
  amount: 0,
  turnover_rate: 0,
  amplitude: 0,
  volume_ratio: 0,
  outer_vol: 0,
  inner_vol: 0,
  pe_ratio: 0,
  pb_ratio: 0,
  dy_ratio: 0,
  zt_price: '--',
  dt_price: '--',
  beta: 0,
  total_shares: 0,
  data_source: 'unknown'
})

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
let chart: ChartApi | null = null
let candleSeries: SeriesApi | null = null
let volumeSeries: SeriesApi | null = null
let updateTimer: number | null = null
let statusTimer: number | null = null
let chartResizeObserver: ResizeObserver | null = null

// WebSocket 实例（1分钟线实时推送）
let klineWs: any = null  // KlineWebSocket
let aggregator: any = null  // Kline聚合器（所有周期都用WS，前端聚合）
const wsConnected = ref(false)

// 十字光标悬停的 bar 数据
const hoverBar = ref<{ time: string; open: number; high: number; low: number; close: number; volume: number } | null>(null)

// 当前股票名称（从行情数据获取）
const currentStockName = ref('')

// 格式化成交量
const formatVolume = (vol: number): string => {
  if (!vol) return '--'
  if (vol >= 100000000) return (vol / 100000000).toFixed(2) + '亿'
  if (vol >= 10000) return (vol / 10000).toFixed(2) + '万'
  return vol.toString()
}

// 迷你折线图数据：存储带时间戳的K线 {time: Date, close: number}
const miniChartsData = ref<Record<string, Array<{time: Date, close: number}>>>({})

// 后台预加载自选股列表的K线数据（无感缓存）
let preloadAbortController: AbortController | null = null

const preloadWatchlistKlines = async () => {
  const currentStocks = dataStore.activeGroup?.stocks || []
  const otherStocks = currentStocks.filter((s: any) => s.symbol !== selectedStock.value)
  if (otherStocks.length === 0) return

  // 要预加载的周期（当前周期 + 常用周期）
  const periodsToPreload = Array.from(new Set([
    currentTimeframe.value,
    '1m', '5m', '1d'  // 常用周期
  ]))

  console.log('[Preload] 开始后台预加载', otherStocks.length, '只自选股，周期:', periodsToPreload)

  // 取消之前的预加载任务
  if (preloadAbortController) {
    preloadAbortController.abort()
  }
  preloadAbortController = new AbortController()
  const signal = preloadAbortController.signal

  let completed = 0
  const total = otherStocks.length * periodsToPreload.length

  for (const stock of otherStocks) {
    for (const period of periodsToPreload) {
      // 检查是否被取消
      if (signal.aborted) return

      // 验证股票代码有效性
      const code = stock.code || stock.symbol
      if (!code || code === 'undefined' || !code.trim()) {
        console.warn('[Preload] 跳过无效股票:', stock)
        continue
      }

      // 延迟执行，避免阻塞主线程和突发请求
      await new Promise(resolve => setTimeout(resolve, 100))

      try {
        // 低优先级获取，只缓存不显示（count=300足够近期使用）
        await fetchKline(code, period, 300, adjustType.value)
        completed++

        // 每完成5个打印一次日志
        if (completed % 5 === 0 || completed === total) {
          console.log(`[Preload] 进度: ${completed}/${total}`)
        }
      } catch (e) {
        // 静默失败，不影响用户体验
        console.debug(`[Preload] ${code} ${period} 预加载失败`)
      }
    }
  }

  console.log('[Preload] 预加载完成，已缓存', completed, '条数据')
}

// 迷你折线图定时刷新器
let miniChartsTimer: number | null = null

// 迷你折线图：获取自选股的当天 1 分钟收盘价
const loadMiniCharts = async () => {
  const currentStocks = dataStore.activeGroup?.stocks || []
  console.log('[loadMiniCharts] 开始加载，股票数量:', currentStocks.length)
  const tasks = currentStocks.map(async (stock: any) => {
    try {
      // 兼容 symbol 和 code 字段
      const symbol = stock.symbol || stock.code
      // 更严格的检查：排除空值、undefined、"undefined" 字符串
      if (!symbol || symbol === 'undefined' || !symbol.trim()) {
        console.warn('[loadMiniCharts] 跳过无效股票:', stock)
        return
      }
      console.log(`[loadMiniCharts] 正在加载 ${symbol}...`)
      const res = await fetchKline(symbol, '1m', 240, 'none')  // 1分钟，全天240根
      if (res.data && res.data.length >= 5) {
        // 转换为带时间戳的数据，并按时间排序
        const barsWithTime = res.data
          .map((b: KlineItem) => ({
            time: new Date(Number(b.time)),
            close: Number(b.close)
          }))
          .sort((a, b) => a.time.getTime() - b.time.getTime())

        // 找到最新一天的开盘时间
        const latestTime = barsWithTime[barsWithTime.length - 1].time
        const dayOpen = new Date(latestTime)
        dayOpen.setHours(9, 30, 0, 0)

        // 只保留当天开盘之后的数据
        const todayBars = barsWithTime.filter(b => b.time >= dayOpen)
        console.log(`[loadMiniCharts] ${symbol} 成功，数据点数:`, todayBars.length)
        miniChartsData.value[symbol] = todayBars
      } else {
        console.log(`[loadMiniCharts] ${symbol} 数据不足，res.data.length:`, res.data?.length)
        miniChartsData.value[symbol] = []
      }
    } catch (e) {
      console.error(`[loadMiniCharts] ${stock.symbol || stock.code} 加载失败:`, e)
      const symbol = stock.symbol || stock.code
      if (symbol) miniChartsData.value[symbol] = []
    }
  })
  await Promise.all(tasks)
  console.log('[loadMiniCharts] 加载完成，miniChartsData:', Object.keys(miniChartsData.value))
}

// 将带时间戳的价格数组转为 SVG polyline points 字符串
// X轴：按交易分钟数映射（A股240个交易分钟）
// Y轴：价格映射
const sparklinePoints = (data: Array<{time: Date, close: number}>): string => {
  if (!data || data.length < 2) return ''
  const W = 120, H = 28

  // A股交易时间：240个1分钟K线
  // 上午：9:30-11:30（120分钟）
  // 下午：13:00-15:00（120分钟）
  const TOTAL_TRADING_MINUTES = 240

  const prices = data.map(d => d.close)
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1

  return data.map((d) => {
    const hour = d.time.getHours()
    const minute = d.time.getMinutes()

    // 计算交易分钟数（从0开始）
    // 北京时间：上午 9:30-11:30，下午 13:00-15:00
    let tradingMinutes = (hour - 9) * 60 + (minute - 30)

    // 下午时段减去中午休市的90分钟（11:30-13:00）
    if (hour >= 13) {
      tradingMinutes -= 90
    }

    // 计算在240个交易分钟中的位置（0-1）
    const position = tradingMinutes / TOTAL_TRADING_MINUTES

    // 限制在 0-1 范围内
    const clampedPos = Math.max(0, Math.min(1, position))
    const x = clampedPos * W
    const y = H - ((d.close - min) / range) * (H - 4) - 2
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
}

const sparklineColor = (data: Array<{time: Date, close: number}>): string => {
  if (!data || data.length < 2) return '#4a4f60'
  return data[data.length - 1].close >= data[0].close ? '#ef5350' : '#26a69a'
}

// 格式化成交额
const formatAmount = (amt: number): string => {
  if (!amt) return '--'
  if (amt >= 100000000) return (amt / 100000000).toFixed(2) + '亿'
  if (amt >= 10000) return (amt / 10000).toFixed(2) + '万'
  return amt.toString()
}

// 格式化股本（总股本）
const formatShares = (shares: number): string => {
  if (!shares) return '--'
  if (shares >= 100000000) return (shares / 100000000).toFixed(2) + '亿'
  if (shares >= 10000) return (shares / 10000).toFixed(2) + '万'
  return shares.toLocaleString()
}

// 格式化内外盘（股）
const formatVol = (vol: number): string => {
  if (!vol) return '--'
  if (vol >= 10000) return (vol / 10000).toFixed(2) + '万'
  return vol.toLocaleString()
}

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return

  // 创建主图表（先用 fallback 尺寸，之后通过轮询拿到真实高度）
  const w = chartContainer.value.clientWidth || 600
  const h = chartContainer.value.clientHeight
         || (window.innerHeight - 56 - 42 - 28 - 100) // nav+toolbar+status+volume
  chart = createChart(chartContainer.value, {
    width: w,
    height: h,
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
      borderColor: 'transparent',
      autoScale: false,
    },
    handleScroll: {
      mouseWheel: true,
      pressedMouseMove: true,
      horzTouchDrag: true,
      vertTouchDrag: true,
    },
    handleScale: {
      axisPressedMouseMove: {
        time: true,
        price: true,
      },
    },
    timeScale: {
      borderColor: 'rgba(42, 46, 57, 0.8)',
      timeVisible: true,
      secondsVisible: false,
      minBarSpacing: 0.5,
      rightOffset: 10,
      fixLeftEdge: true,
      fixRightEdge: false
    },
    // 时间轴配置
    localization: {
      dateFormat: 'yyyy-MM-dd',
      timeFormatter: (timestamp: number) => {
        const date = new Date(timestamp * 1000)
        const year = date.getUTCFullYear()
        const month = String(date.getUTCMonth() + 1).padStart(2, '0')
        const day = String(date.getUTCDate()).padStart(2, '0')
        const hours = String(date.getUTCHours()).padStart(2, '0')
        const minutes = String(date.getUTCMinutes()).padStart(2, '0')
        // 日线/周线只显示日期，分钟线显示日期+时间
        const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
        return isDaily
          ? `${year}-${month}-${day}`
          : `${year}-${month}-${day} ${hours}:${minutes}`
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

  // 从 chart-area 反算正确高度（避免 canvas 干扰 clientHeight 读取）
  let retries = 0
  const syncSize = () => {
    if (!chart || !chartContainer.value) return
    const chartArea = chartContainer.value.closest('.chart-area') as HTMLElement
    if (chartArea) {
      const areaH = chartArea.getBoundingClientRect().height
      const toolbar = chartArea.querySelector('.chart-toolbar') as HTMLElement
      const toolbarH = toolbar?.getBoundingClientRect().height || 42
      const targetH = areaH - toolbarH
      const targetW = chartContainer.value.getBoundingClientRect().width
      if (targetH > 50 && targetW > 0) {
        chart.resize(targetW, targetH)
        return
      }
    }
    if (retries++ < 30) requestAnimationFrame(syncSize)
  }
  requestAnimationFrame(syncSize)

  // ResizeObserver 持续同步宽高
  chartResizeObserver = new ResizeObserver(() => {
    if (chart && chartContainer.value) {
      const rect = chartContainer.value.getBoundingClientRect()
      if (rect.width > 0 && rect.height > 0) {
        chart.resize(rect.width, rect.height)
      }
    }
  })
  chartResizeObserver.observe(chartContainer.value)

  // 十字光标移动 → 更新 hoverBar
  chart.subscribeCrosshairMove((param: any) => {
    if (!param.time || !candleSeries) {
      hoverBar.value = null
      return
    }
    const bar = param.seriesData.get(candleSeries) as any
    const volBar = param.seriesData.get(volumeSeries) as any
    if (bar) {
      const ts = Number(param.time) * 1000
      // 修改版插件已处理时区，不加偏移
      const dt = new Date(ts)
      const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
      const timeStr = isDaily
        ? `${dt.getUTCFullYear()}-${String(dt.getUTCMonth()+1).padStart(2,'0')}-${String(dt.getUTCDate()).padStart(2,'0')}`
        : `${String(dt.getUTCMonth()+1).padStart(2,'0')}-${String(dt.getUTCDate()).padStart(2,'0')} ${String(dt.getUTCHours()).padStart(2,'0')}:${String(dt.getUTCMinutes()).padStart(2,'0')}`
      hoverBar.value = {
        time: timeStr,
        open: bar.open,
        high: bar.high,
        low: bar.low,
        close: bar.close,
        volume: volBar?.value ?? 0,
      }
    } else {
      hoverBar.value = null
    }
  })
}

// 加载K线数据（优化版：优先加载K线，其他数据延后）
const isInitialLoad = ref(true)  // 标记是否为初始加载

// 启动迷你折线图定时刷新
const startMiniChartsRefresh = () => {
  // 清除旧定时器
  if (miniChartsTimer) {
    clearInterval(miniChartsTimer)
    miniChartsTimer = null
  }

  // 每分钟刷新一次分时图
  miniChartsTimer = window.setInterval(() => {
    const now = new Date()
    const hour = now.getHours()
    const minute = now.getMinutes()

    // 只在交易时间内刷新（9:30 - 15:00）
    const isInTradingTime = (hour > 9 || (hour === 9 && minute >= 30)) && hour < 15

    if (isInTradingTime) {
      loadMiniCharts()
    }
  }, 60000)  // 60秒刷新一次
}

const loadKlineData = async () => {
  if (!selectedStock.value) return

  loading.value = true
  let lastBarsCount = 0  // 记录本次加载的 bar 数量，供 setVisibleLogicalRange 使用

  try {
    // 第一步：优先只加载K线数据（最核心的）
    const klineRes = await fetchKline(selectedStock.value, currentTimeframe.value, 800, adjustType.value)

    // 处理K线数据
    if (klineRes.data && klineRes.data.length > 0) {
      const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
      const klineDataWithSeconds = klineRes.data
        .map((item: KlineItem) => {
          // 后端返回毫秒时间戳（UTC时间）
          // 需要加8小时偏移才能显示北京时间
          let timeValue: number
          if (typeof item.time === 'string') {
            timeValue = Math.floor(new Date(item.time).getTime() / 1000)
          } else {
            const numTime = Number(item.time)
            // 判断是毫秒还是秒：毫秒时间戳 > 1e11
            timeValue = numTime > 100000000000 ? Math.floor(numTime / 1000) : numTime
          }

          // 前端传北京时间戳（+8小时），插件不加偏移
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
        .filter((item): item is { time: number; open: number; high: number; low: number; close: number; volume: number } => item !== null)

      // 日线去重：同一天可能有本地(00:00 CST)和在线(15:00 CST)两条，保留后一条
      const deduped = isDaily
        ? Array.from(
            klineDataWithSeconds.reduce((map, item) => {
              map.set(item.time, item)  // 相同时间戳后面覆盖前面
              return map
            }, new Map<number, typeof klineDataWithSeconds[0]>()).values()
          ).sort((a, b) => a.time - b.time)
        : klineDataWithSeconds.sort((a, b) => (a.time as number) - (b.time as number))

      candleSeries?.setData(deduped)
      lastBarsCount = deduped.length

      // 成交量数据与 deduped K线保持一致的时间戳
      const volumeData = deduped.map(d => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? '#ef535080' : '#26a69a80'
      }))
      volumeSeries?.setData(volumeData)

      // K线加载完成，立即结束loading（提升用户体验）
      loading.value = false

      // 设置图表显示范围
      if (isInitialLoad.value) {
        const total = lastBarsCount
        if (total > 0) {
          chart?.timeScale().setVisibleLogicalRange({
            from: Math.max(0, total - 200),
            to: total - 1 + 10,
          })
        }
        chart?.priceScale('right').applyOptions({ autoScale: true })
        setTimeout(() => {
          chart?.priceScale('right').applyOptions({ autoScale: false })
        }, 200)
        isInitialLoad.value = false
      }
    }

    // 第二步：后台加载其他数据（不阻塞K线显示）
    setTimeout(async () => {
      try {
        const currentStocks = dataStore.activeGroup?.stocks || []
        const allSymbols = currentStocks.map((s: any) => s.symbol)
        const indexSymbols = indices.value.map(i => i.code)

        // 并行加载快照、自选股、指数
        const [snapshotRes, batchRes, indexRes] = await Promise.all([
          fetchSnapshot(selectedStock.value),
          fetchSnapshotBatch(allSymbols),
          fetchSnapshotBatch(indexSymbols),
        ])

        // 更新当前股票快照（右侧详情面板）
        updateQuoteFromSnapshot(snapshotRes)

        // 批量更新所有自选股的价格
        if (batchRes.data && batchRes.data.length > 0) {
          const quoteMap = new Map(batchRes.data.map((q: any) => [q.symbol || q.code, q]))
          const currentStocks = dataStore.activeGroup?.stocks || []
          for (const stock of currentStocks) {
            const quote = quoteMap.get(stock.symbol)
            if (quote) {
              dataStore.updateQuote(quote)
            }
          }
        }

        // 更新指数
        if (indexRes.data && indexRes.data.length > 0) {
          const indexMap = new Map(indexRes.data.map((q: any) => [q.symbol || q.code, q]))
          for (const idx of indices.value) {
            const q = indexMap.get(idx.code)
            if (q) {
              idx.price = q.price ? Number(q.price).toFixed(2) : '--'
              idx.change = getChangePct(q)
            }
          }
        }

        // 第三步：后台预加载其他自选股K线
        preloadWatchlistKlines()
      } catch (error) {
        console.error('后台加载数据失败:', error)
      }
    }, 100)  // 延迟100ms，让K线先渲染

  } catch (error) {
    console.error('加载K线失败:', error)
    loading.value = false
  }
}

// ─────────────────────────────────────────────
// WebSocket 消息处理函数
// ─────────────────────────────────────────────

/** 将后端 bar 格式转换为 lightweight-charts 格式 */
const convertBarForChart = (bar: any): { time: number; open: number; high: number; low: number; close: number; volume: number } => {
  // 后端格式：{time: "2026-03-24 09:31:00", open, high, low, close, volume}
  // 需转换为：{time: Unix秒, open, high, low, close, volume}
  const timestamp = bar.time instanceof Date ? bar.time.getTime() : Date.parse(String(bar.time))
  return {
    time: Math.floor(timestamp / 1000),
    open: Number(bar.open),
    high: Number(bar.high),
    low: Number(bar.low),
    close: Number(bar.close),
    volume: Number(bar.volume)
  }
}

/** 处理 WebSocket 历史数据消息（已弃用：所有周期都用HTTP加载历史数据） */
const onWsHistory = (bars: KlineBar[]) => {
  // 不再使用WebSocket历史数据，所有周期都通过HTTP API加载历史数据
  console.log('[RealtimeQuotes] 收到WS历史数据（忽略）:', bars.length, '根')
  // 只用于初始化聚合器，不设置图表数据
  if (aggregator && bars.length > 0) {
    const convertedBars = bars.map(bar => {
      const timeField = (bar as any).datetime || bar.time
      const timestamp = new Date(timeField).getTime() / 1000
      return { time: timestamp, open: Number(bar.open), high: Number(bar.high), low: Number(bar.low), close: Number(bar.close), volume: Number(bar.volume) }
    }).filter(bar => !isNaN(bar.time))
    aggregator.setHistory(convertedBars)
  }
}

/** 处理 WebSocket bar_update 消息（更新最后一根 K线） */
const onWsBarUpdate = (bar: KlineBar) => {
  if (!candleSeries || !volumeSeries || !aggregator) return

  // 日线及以上周期：检查是否是当天数据
  const isDailyOrAbove = ['1d', '1w', '1M'].includes(currentTimeframe.value)

  // 转换后端数据格式
  const timeField = (bar as any).datetime || bar.time
  const timestamp = new Date(timeField).getTime() / 1000
  if (isNaN(timestamp)) return

  // 日线周期：只更新当天的最后一根K线，不处理历史数据
  if (isDailyOrAbove) {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime() / 1000

    // 只处理当天的数据（用于更新最后一根K线的收盘价）
    if (timestamp >= today) {
      const chartBar = {
        time: today,
        open: Number(bar.open),
        high: Number(bar.high),
        low: Number(bar.low),
        close: Number(bar.close),
        volume: Number(bar.volume)
      }
      candleSeries.update(chartBar)
      volumeSeries.update({
        time: today,
        value: chartBar.volume,
        color: chartBar.close >= chartBar.open ? '#ef535080' : '#26a69a80'
      })
      console.log('[RealtimeQuotes] 日线更新:', chartBar)
    }
    return
  }

  // 分钟线周期：正常聚合
  const convertedBar: KlineBar = {
    time: timestamp,
    open: Number(bar.open),
    high: Number(bar.high),
    low: Number(bar.low),
    close: Number(bar.close),
    volume: Number(bar.volume)
  }

  const result = aggregator.aggregateBar(convertedBar, true)

  // 更新图表
  if (result.update) {
    const chartBar = result.update
    candleSeries.update(chartBar)
    volumeSeries.update({
      time: chartBar.time,
      value: chartBar.volume,
      color: chartBar.close >= chartBar.open ? '#ef535080' : '#26a69a80'
    })
    console.log('[RealtimeQuotes] K线更新:', chartBar)
  }
}

/** 处理 WebSocket bar_close 消息（上一根收线，新一根开始） */
const onWsBarClose = (bar: KlineBar) => {
  if (!candleSeries || !volumeSeries) return

  // 日线及以上周期：不处理收线消息（因为历史数据已通过HTTP加载）
  const isDailyOrAbove = ['1d', '1w', '1M'].includes(currentTimeframe.value)
  if (isDailyOrAbove) {
    return
  }

  // 分钟线周期：正常处理
  if (!aggregator) return

  // 转换后端数据格式
  const timeField = (bar as any).datetime || bar.time
  const timestamp = new Date(timeField).getTime() / 1000
  if (isNaN(timestamp)) return

  const convertedBar: KlineBar = {
    time: timestamp,
    open: Number(bar.open),
    high: Number(bar.high),
    low: Number(bar.low),
    close: Number(bar.close),
    volume: Number(bar.volume)
  }

  const result = aggregator.aggregateBar(convertedBar, true)

  // 如果有新bar收线，更新图表
  if (result.close) {
    const chartBar = result.close
    candleSeries.update(chartBar)
    volumeSeries.update({
      time: chartBar.time,
      value: chartBar.volume,
      color: chartBar.close >= chartBar.open ? '#ef535080' : '#26a69a80'
    })
    console.log('[RealtimeQuotes] 新K线收线:', chartBar)
  }

  // 更新当前正在形成的bar
  if (result.update) {
    const chartBar = result.update
    candleSeries.update(chartBar)
    volumeSeries.update({
      time: chartBar.time,
      value: chartBar.volume,
      color: chartBar.close >= chartBar.open ? '#ef535080' : '#26a69a80'
    })
    console.log('[RealtimeQuotes] 新K线开始:', chartBar)
  }
}

// ─────────────────────────────────────────────
// 从快照数据更新当前行情和五档盘口
// ─────────────────────────────────────────────
const updateQuoteFromSnapshot = (quote: any) => {
  console.log('[updateQuoteFromSnapshot] quote keys:', Object.keys(quote))
  console.log('[updateQuoteFromSnapshot] quote.name:', quote.name)

  const price = Number(quote.price) || 0
  const prevClose = Number(quote.pre_close ?? quote.prev_close ?? quote.last_close) || 0
  const changeAmt = Number(quote.change ?? (price - prevClose))

  // 更新股票名称（优先从快照数据，如果没有则从自选股列表查找）
  if (quote.name && quote.name !== '--') {
    currentStockName.value = quote.name
    console.log('[updateQuoteFromSnapshot] 更新股票名称（来自快照）:', quote.name)
  } else {
    // 从自选股列表中查找股票名称
    const stockInWatchlist = dataStore.activeGroup?.stocks?.find((s: any) =>
      s.symbol === selectedStock.value || s.code === selectedStock.value
    )
    if (stockInWatchlist?.name) {
      currentStockName.value = stockInWatchlist.name
      console.log('[updateQuoteFromSnapshot] 更新股票名称（来自自选股列表）:', stockInWatchlist.name)
    }
  }

  currentQuote.value = {
    price: price ? price.toFixed(2) : '--',
    change: parseFloat(changeAmt.toFixed(2)),
    change_percent: getChangePct(quote),
    open: quote.open ? Number(quote.open).toFixed(2) : '--',
    high: quote.high ? Number(quote.high).toFixed(2) : '--',
    low: quote.low ? Number(quote.low).toFixed(2) : '--',
    prev_close: prevClose ? prevClose.toFixed(2) : '--',
    volume: quote.volume || 0,
    amount: quote.amount || 0,
    // 新增扩展指标
    turnover_rate: quote.turnover_rate || quote.turnover || 0,
    volume_ratio: quote.volume_ratio || quote.LB || 0,
    amplitude: quote.amplitude || quote.ZAF || 0,
    pe_ratio: quote.pe_ratio || quote.dyna_pe || 0,
    pb_ratio: quote.pb_ratio || quote.pb_mrq || 0,
    dy_ratio: quote.dy_ratio || quote.dyr || 0,
    zt_price: quote.zt_price ? Number(quote.zt_price).toFixed(2) : '--',
    dt_price: quote.dt_price ? Number(quote.dt_price).toFixed(2) : '--',
    beta: quote.beta || quote.BetaValue || 0,
    total_shares: quote.total_shares || quote.J_zgb || 0,
    inner_vol: quote.inner_vol || 0,
    outer_vol: quote.outer_vol || 0,
    data_source: quote.data_source || 'unknown'
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

/** 刷新快照数据：当前股票快照 + 自选股批量快照 + 指数（不含 K线） */
const refreshSnapshots = async () => {
  console.log('[refreshSnapshots] 开始执行')
  if (!selectedStock.value) {
    console.log('[refreshSnapshots] 没有选中股票，返回')
    return
  }

  try {
    const currentStocks = dataStore.activeGroup?.stocks || []
    const allSymbols = currentStocks.map((s: any) => s.symbol)
    console.log('[refreshSnapshots] 当前自选股:', allSymbols)
    const indexSymbols = indices.value.map(i => i.code)
    const [snapshotRes, batchRes, indexRes] = await Promise.all([
      fetchSnapshot(selectedStock.value),
      fetchSnapshotBatch(allSymbols),
      fetchSnapshotBatch(indexSymbols),
    ])

    console.log('[refreshSnapshots] batchRes:', batchRes)

    // 更新当前股票快照（API 直接返回 QuoteSnapshot，无需解包）
    updateQuoteFromSnapshot(snapshotRes)

    // 批量更新所有自选股的价格
    if (batchRes.data && batchRes.data.length > 0) {
      console.log('[refreshSnapshots] batchRes.data:', batchRes.data)
      const quoteMap = new Map(batchRes.data.map((q: any) => [q.symbol || q.code, q]))
      console.log('[refreshSnapshots] quoteMap keys:', Array.from(quoteMap.keys()))
      const currentStocks = dataStore.activeGroup?.stocks || []
      for (const stock of currentStocks) {
        const quote = quoteMap.get(stock.symbol)
        console.log(`[refreshSnapshots] ${stock.symbol}:`, quote ? '找到' : '未找到')
        if (quote) {
          dataStore.updateQuote(quote)
          console.log(`[refreshSnapshots] 已更新 ${stock.symbol}:`, quote)
        }
      }
    } else {
      console.log('[refreshSnapshots] batchRes.data 为空或不存在')
    }

    // 更新指数
    if (indexRes.data && indexRes.data.length > 0) {
      const indexMap = new Map(indexRes.data.map((q: any) => [q.symbol || q.code, q]))
      for (const idx of indices.value) {
        const q = indexMap.get(idx.code)
        if (q) {
          idx.price = q.price ? Number(q.price).toFixed(2) : '--'
          idx.change = getChangePct(q)
        }
      }
    }
  } catch (error) {
    console.error('刷新快照失败:', error)
  }
}

// 计算最大订单数量（用于进度条基准）
const maxOrderSize = computed(() => {
  const allSizes = [...asks.value, ...bids.value].map(item => item.size)
  return Math.max(...allSizes, 1) // 至少为1，避免除以0
})

// 获取数量百分比（用于进度条宽度）
const getSizePercent = (size: number) => {
  if (!size || maxOrderSize.value === 0) return 0
  // 最小保留15%宽度，确保小数字也能看到进度条
  const percent = (size / maxOrderSize.value) * 100
  return Math.max(percent, 15)
}

// 格式化盘口数量（转为"手"）
const formatOrderSize = (size: number): string => {
  if (!size) return '0'
  // 后端返回的已经是手，无需再转换
  if (size >= 10000) {
    return (size / 10000).toFixed(1) + '万'
  }
  return Math.floor(size).toLocaleString()
}

// ─────────────────────────────────────────────
// WebSocket 连接管理
// ─────────────────────────────────────────────

/** 连接 K线 WebSocket（所有周期：HTTP加载历史，WS更新最后一根） */
const connectKlineWs = () => {
  if (!selectedStock.value) return

  // 如果已连接且股票没变，只更新聚合器周期
  if (klineWs && klineWs.isConnected() && selectedStock.value === (klineWs as any).symbol) {
    console.log('[RealtimeQuotes] WS 已连接，更新聚合器周期:', currentTimeframe.value)
    if (aggregator) {
      aggregator.setTimeframe(currentTimeframe.value as Timeframe)
    } else {
      aggregator = createKlineAggregator(currentTimeframe.value as Timeframe)
    }
    return
  }

  disconnectKlineWs()  // 先断开旧连接

  console.log('[RealtimeQuotes] 连接 WS:', selectedStock.value, '周期:', currentTimeframe.value)

  // 初始化聚合器
  aggregator = createKlineAggregator(currentTimeframe.value as Timeframe)

  klineWs = createKlineWebSocket(selectedStock.value, {
    onConnected: () => {
      wsConnected.value = true
      console.log('[RealtimeQuotes] WS 已连接')
    },
    onDisconnected: () => {
      wsConnected.value = false
      console.log('[RealtimeQuotes] WS 已断开')
    },
    onHistory: onWsHistory,  // 所有周期都不用WS历史数据，只用于初始化聚合器
    onBarUpdate: onWsBarUpdate,
    onBarClose: onWsBarClose,
    onError: (msg) => {
      console.error('[RealtimeQuotes] WS 错误:', msg)
    }
  })
  klineWs.connect()

  // 注意：loadKlineData 由调用方（如 selectStock）负责调用，避免重复请求
}

/** 断开 K线 WebSocket */
const disconnectKlineWs = () => {
  if (klineWs) {
    console.log('[RealtimeQuotes] 断开 WS')
    klineWs.disconnect()
    klineWs = null
    wsConnected.value = false
  }
  // 清空聚合器
  aggregator?.clear()
  aggregator = null
}

// ─────────────────────────────────────────────
// 选择股票
const selectStock = (code: string) => {
  if (!code || code === 'undefined') {
    console.warn('[selectStock] 无效的股票代码:', code)
    return
  }

  selectedStock.value = code

  // 保存到 localStorage（只保存有效值）
  try {
    localStorage.setItem('realtime_quotes_last_stock', code)
  } catch (e) {
    console.error('[selectStock] 保存失败:', e)
  }

  isInitialLoad.value = true  // 切换股票时重新适应显示范围

  // 取消之前的预加载任务
  if (preloadAbortController) {
    preloadAbortController.abort()
    preloadAbortController = null
  }

  // 切换 WebSocket 连接到新股票
  connectKlineWs()

  // 立即加载新股票的历史数据（HTTP兜底，确保数据即时显示正确的周期）
  loadKlineData()
}

// 切换周期（先加载数据，避免图表闪空白）
const changeTimeframe = async (tf: string) => {
  if (currentTimeframe.value === tf) return  // 周期没变，不处理

  if (!tf || tf === 'undefined') {
    console.warn('[changeTimeframe] 无效的周期:', tf)
    return
  }

  console.log('[RealtimeQuotes] 切换周期:', currentTimeframe.value, '->', tf)
  currentTimeframe.value = tf

  // 保存到 localStorage（只保存有效值）
  try {
    localStorage.setItem('realtime_quotes_last_timeframe', tf)
  } catch (e) {
    console.error('[changeTimeframe] 保存失败:', e)
  }

  isInitialLoad.value = true

  // 先加载数据（利用TTL缓存，瞬间完成）
  console.log('[RealtimeQuotes] 切换周期，加载历史数据:', tf)
  await loadKlineData()

  // 数据加载完成后再切换聚合器（避免图表闪空白）
  if (aggregator) {
    aggregator.clear()
  }
  aggregator = createKlineAggregator(tf as Timeframe)
  console.log('[RealtimeQuotes] 聚合器已切换:', tf)

  // WebSocket 保持连接（始终推1分钟线），无需重连
  // 聚合器会自动将1分钟线聚合到目标周期
}

// 切换复权类型
const changeAdjustType = (type: string) => {
  adjustType.value = type
  isInitialLoad.value = true
  loadKlineData()
}

// 市场状态缓存
const marketStatusCache = ref<MarketStatus | null>(null)

// 实时更新（根据市场状态动态调整刷新间隔）
const startRealtimeUpdate = async () => {
  const getStatus = async (): Promise<MarketStatus | null> => {
    try { return await fetchMarketStatus() } catch { return null }
  }

  const updateStatus = async () => {
    marketStatusCache.value = await getStatus()
  }

  // 初始获取状态
  await updateStatus()

  // 每30秒更新一次市场状态
  statusTimer = window.setInterval(updateStatus, 30000)

  // 主刷新循环
  updateTimer = window.setInterval(async () => {
    if (!selectedStock.value) return

    const status = marketStatusCache.value
    const isOpen = status?.is_open ?? false

    // 收盘后不刷新
    if (!isOpen) {
      return
    }

    // 始终刷新快照（包含自选股列表的价格）
    refreshSnapshots()

    // 交易中：根据连接状态决定是否加载K线
    if (!wsConnected.value) {
      // WebSocket 未连接：用 HTTP 加载当前股票K线
      loadKlineData()
    }
    // WebSocket 已连接：K线由 WS 推送，不需要 HTTP 加载
  }, 5000)  // 固定5秒检查一次，实际是否刷新由市场状态决定
}

onMounted(() => {
  nextTick(() => {
    // 先设置选中的股票，再初始化其他功能
    if (!selectedStock.value) {
      const firstStock = dataStore.activeGroup?.stocks?.[0]
      if (firstStock) {
        selectedStock.value = firstStock.symbol || firstStock.code
        console.log('[onMounted] 使用列表第一只股票:', selectedStock.value)
      } else {
        // 如果列表也是空的，使用默认值
        selectedStock.value = '600000.SH'
        console.log('[onMounted] 使用默认股票:', selectedStock.value)
      }
    }

    // 确保 selectedStock 已设置后再初始化
    console.log('[onMounted] 当前选中股票:', selectedStock.value)

    initChart()
    loadMiniCharts()
    startMiniChartsRefresh()  // 启动分时图定时刷新
    refreshSnapshots()  // 立即加载一次快照数据
    startRealtimeUpdate()
    // 连接 WebSocket 并加载历史数据（所有周期：HTTP加载历史，WS实时更新）
    connectKlineWs()
  })
})

onBeforeUnmount(() => {
  if (updateTimer) clearInterval(updateTimer)
  if (statusTimer) clearInterval(statusTimer)
  if (miniChartsTimer) clearInterval(miniChartsTimer)  // 清理分时图定时器
  disconnectKlineWs()  // 断开 WebSocket
  chartResizeObserver?.disconnect()
  if (chart) chart.remove()
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
  min-height: 0;
}

/* 面板 */
.panel {
  background: #131722;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  background: #1e222d;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #d1d4dc;
  border-bottom: 1px solid #2a2e39;
}

.stock-info-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stock-name-large {
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
}

.stock-code-small {
  font-size: 11px;
  font-weight: 400;
  color: #787b86;
  font-family: 'Courier New', monospace;
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
  grid-template-columns: 1fr 80px 52px;
  gap: 6px;
  padding: 8px 14px;
  border-bottom: 1px solid #2a2e39;
  cursor: pointer;
  transition: background 0.15s;
  align-items: center;
}

.mini-chart {
  width: 80px;
  height: 28px;
  opacity: 0.9;
}

.stock-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.stock-row1, .stock-row2, .mini-chart-placeholder { display: none; }

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
  flex: 1;
  min-height: 0;
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

.chart-legend-overlay {
  position: absolute;
  top: 8px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #d1d4dc;
  pointer-events: none;
  z-index: 10;
  background: rgba(19, 23, 34, 0.75);
  padding: 4px 12px;
  border-radius: 4px;
}
.chart-legend-overlay .legend-time { color: #9ca3af; margin-right: 4px; }
.chart-legend-overlay .legend-item { display: flex; align-items: center; gap: 4px; }
.chart-legend-overlay .legend-item em { font-style: normal; font-weight: 600; font-size: 13px; color: #e6edf3; }

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
  min-height: 0;
  display: flex;
  flex-direction: column;
  position: relative;
}

.kline-chart {
  flex: 1;
  min-height: 0;
}

.volume-chart {
  display: none;
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
  gap: 8px;
}

.info-item {
  background: #1e222d;
  padding: 8px 10px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.info-label {
  font-size: 10px;
  color: #787b86;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
}
.info-value.positive { color: #ef5350; }
.info-value.negative { color: #26a69a; }

.data-source-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.data-source-label {
  color: #787b86;
  font-size: 10px;
  text-transform: uppercase;
}

.data-source-value {
  color: #4caf50;
  font-weight: 600;
  font-size: 12px;
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
  min-height: 24px;
  align-items: center;
  white-space: nowrap;
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
  position: relative;
  z-index: 1;
}

/* 盘口数量进度条 */
.size-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 0;
  transition: width 0.3s ease;
}

/* 买盘红色背景条 */
.order-row.buy .size-bar {
  background: rgba(239, 83, 80, 0.45);
}

/* 卖盘绿色背景条 */
.order-row.sell .size-bar {
  background: rgba(38, 166, 154, 0.45);
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

.index-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.index-name { color: #6e7681; }
.index-price { color: #d1d4dc; font-weight: 600; }
.index-change { font-size: 10px; }
.index-price.positive, .index-change.positive { color: #ef5350; }
.index-price.negative, .index-change.negative { color: #26a69a; }

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
