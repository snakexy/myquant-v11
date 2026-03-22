<template>
  <div class="realtime-quotes-view">
    <GlobalNavBar />

    <div class="main-container">
      <div class="content-area">
        <!-- 左侧股票列表 -->
        <div class="panel watchlist-panel">
          <div class="panel-header">
            <span>{{ isZh ? '自选列表' : 'Watchlist' }}</span>
            <div class="panel-actions">
              <button class="panel-btn" @click="showAddStock = true" :title="isZh ? '添加股票' : 'Add'">+</button>
            </div>
          </div>

          <!-- 搜索框 -->
          <div class="search-section">
            <input
              v-model="searchSymbol"
              type="text"
              :placeholder="isZh ? '输入代码 (如 600000.SH)' : 'Symbol (e.g. 600000.SH)'"
              class="search-input"
              @keyup.enter="addStock"
            />
            <button @click="addStock" class="add-btn">{{ isZh ? '添加' : 'Add' }}</button>
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
              <svg v-if="miniCharts[stock.code]" class="mini-chart" viewBox="0 0 120 28" preserveAspectRatio="none">
                <polyline
                  :points="sparklinePoints(miniCharts[stock.code])"
                  fill="none"
                  :stroke="sparklineColor(miniCharts[stock.code])"
                  stroke-width="1.5"
                  stroke-linejoin="round"
                />
              </svg>
              <div v-else class="mini-chart"></div>
              <div class="stock-right">
                <div :class="['stock-price', stock.change >= 0 ? 'positive' : 'negative']">
                  {{ stock.price }}
                </div>
                <div :class="['stock-change', stock.change >= 0 ? 'positive' : 'negative']">
                  {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
                </div>
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
            <span>{{ isZh ? '行情详情' : 'Quote' }}</span>
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
                <div v-for="(ask, i) in asks" :key="'ask'+i" class="order-row sell">
                  <span>{{ isZh ? '卖' : 'Sell' }} {{ 5 - i }}</span>
                  <span class="order-price">{{ ask.price }}</span>
                  <span class="order-size">{{ ask.size }}</span>
                </div>
              </div>
              <div class="order-column">
                <div v-for="(bid, i) in bids" :key="'bid'+i" class="order-row buy">
                  <span>{{ isZh ? '买' : 'Buy' }} {{ i + 1 }}</span>
                  <span class="order-price">{{ bid.price }}</span>
                  <span class="order-size">{{ bid.size }}</span>
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
import { useAppStore } from '@/stores/core/AppStore'
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

// 状态
const searchSymbol = ref('')
const selectedStock = ref('600000.SH')
const currentTimeframe = ref('1d')
const appStore = useAppStore()
const isZh = computed(() => appStore.language === 'zh')

const loading = ref(false)
const showAddStock = ref(false)
const adjustType = ref('qfq')

// 后端 change_pct 字段兼容工具（pytdx 返回 change_pct，部分接口返回 change_percent）
const getChangePct = (q: any): number => parseFloat(Number(q.change_pct ?? q.change_percent ?? 0).toFixed(2))

// 迷你折线图数据 symbol → close 价格数组
const miniCharts = ref<Record<string, number[]>>({})

// 沪深指数
const indices = ref([
  { code: '000001.SH', name: '上证', price: '--', change: 0 },
  { code: '399001.SZ', name: '深证', price: '--', change: 0 },
  { code: '399006.SZ', name: '创业板', price: '--', change: 0 },
])

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
let chart: ChartApi | null = null
let candleSeries: SeriesApi | null = null
let volumeSeries: SeriesApi | null = null
let updateTimer: number | null = null
let chartResizeObserver: ResizeObserver | null = null

// 十字光标悬停的 bar 数据
const hoverBar = ref<{ time: string; open: number; high: number; low: number; close: number; volume: number } | null>(null)

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

// 迷你折线图：获取自选股的当天 5 分钟收盘价
const loadMiniCharts = async () => {
  const tasks = watchlist.value.map(async (stock) => {
    try {
      const res = await fetchKline(stock.code, '5m', 50, 'none')
      if (res.data && res.data.length >= 2) {
        miniCharts.value[stock.code] = res.data.map((b: KlineItem) => Number(b.close))
      }
    } catch {}
  })
  await Promise.all(tasks)
}

// 将价格数组转为 SVG polyline points 字符串
const sparklinePoints = (prices: number[]): string => {
  if (!prices || prices.length < 2) return ''
  const W = 120, H = 28
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1
  return prices.map((p, i) => {
    const x = (i / (prices.length - 1)) * W
    const y = H - ((p - min) / range) * (H - 4) - 2
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
}

const sparklineColor = (prices: number[]): string => {
  if (!prices || prices.length < 2) return '#4a4f60'
  return prices[prices.length - 1] >= prices[0] ? '#ef5350' : '#26a69a'
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
        const beijingDate = new Date(date.getTime() + 8 * 60 * 60 * 1000)
        const year = beijingDate.getUTCFullYear()
        const month = String(beijingDate.getUTCMonth() + 1).padStart(2, '0')
        const day = String(beijingDate.getUTCDate()).padStart(2, '0')
        const hours = String(beijingDate.getUTCHours()).padStart(2, '0')
        const minutes = String(beijingDate.getUTCMinutes()).padStart(2, '0')
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
  chart.subscribeCrosshairMove((param) => {
    if (!param.time || !candleSeries) {
      hoverBar.value = null
      return
    }
    const bar = param.seriesData.get(candleSeries) as any
    const volBar = param.seriesData.get(volumeSeries) as any
    if (bar) {
      const ts = Number(param.time) * 1000
      const dt = new Date(ts + 8 * 3600 * 1000)
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

// 加载K线数据
const isInitialLoad = ref(true)  // 标记是否为初始加载

const loadKlineData = async () => {
  if (!selectedStock.value) return

  loading.value = true
  let lastBarsCount = 0  // 记录本次加载的 bar 数量，供 setVisibleLogicalRange 使用
  try {
    // 并行获取 K线数据、当前股票快照、所有自选股批量快照、指数
    const allSymbols = watchlist.value.map(s => s.code)
    const indexSymbols = indices.value.map(i => i.code)
    const [klineRes, snapshotRes, batchRes, indexRes] = await Promise.all([
      fetchKline(selectedStock.value, currentTimeframe.value, 800, adjustType.value),
      fetchSnapshot(selectedStock.value),
      fetchSnapshotBatch(allSymbols),
      fetchSnapshotBatch(indexSymbols),
    ])

    // 处理K线数据
    if (klineRes.data && klineRes.data.length > 0) {
      const isDaily = currentTimeframe.value === '1d' || currentTimeframe.value === '1w'
      const klineDataWithSeconds = klineRes.data
        .map((item: KlineItem) => {
          const ts = Number(item.time)
          const timeValue = Math.floor(ts / 1000)

          return {
            time: timeValue,
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
    }

    // 批量更新所有自选股的价格
    if (batchRes.data && batchRes.data.length > 0) {
      const quoteMap = new Map(batchRes.data.map((q: any) => [q.symbol || q.code, q]))
      for (const stock of watchlist.value) {
        const quote = quoteMap.get(stock.code)
        if (quote) {
          stock.price = quote.price ? Number(quote.price).toFixed(2) : '--'
          stock.change = getChangePct(quote)
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

    if (isInitialLoad.value) {
      const total = lastBarsCount
      if (total > 0) {
        chart?.timeScale().setVisibleLogicalRange({
          from: Math.max(0, total - 200),
          to: total - 1 + 10,
        })
      }
      // 临时开 autoScale 让价格自适应，之后关掉以允许手动上下拖动
      chart?.priceScale('right').applyOptions({ autoScale: true })
      // 等 setVisibleLogicalRange 和 autoScale 都生效后再锁定
      setTimeout(() => {
        chart?.priceScale('right').applyOptions({ autoScale: false })
      }, 200)
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
const updateQuoteFromSnapshot = (quote: any) => {
  const price = Number(quote.price) || 0
  const prevClose = Number(quote.pre_close ?? quote.prev_close ?? quote.last_close) || 0
  const changeAmt = Number(quote.change ?? (price - prevClose))
  currentQuote.value = {
    price: price ? price.toFixed(2) : '--',
    change: parseFloat(changeAmt.toFixed(2)),
    change_percent: getChangePct(quote),
    open: quote.open ? Number(quote.open).toFixed(2) : '--',
    high: quote.high ? Number(quote.high).toFixed(2) : '--',
    low: quote.low ? Number(quote.low).toFixed(2) : '--',
    prev_close: prevClose ? prevClose.toFixed(2) : '--',
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
  const getStatus = async (): Promise<MarketStatus | null> => {
    try { return await fetchMarketStatus() } catch { return null }
  }

  const status = await getStatus()
  const isOpen = status?.is_open ?? false
  const interval = (status?.refresh_interval ?? 30) * 1000

  updateTimer = window.setInterval(async () => {
    if (!selectedStock.value) return
    if (isOpen) {
      // 交易时间：完整刷新（K线 + 快照）
      loadKlineData()
    }
    // 非交易时间：不刷新，数据不变
  }, interval)
}

onMounted(() => {
  nextTick(() => {
    initChart()
    loadKlineData()
    loadMiniCharts()
    startRealtimeUpdate()
  })
})

onBeforeUnmount(() => {
  if (updateTimer) clearInterval(updateTimer)
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
