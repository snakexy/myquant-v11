<template>
  <div class="trading-view-kline-unified" :class="`theme-${theme}`">
    <!-- 自定义工具栏插槽 -->
    <div v-if="showToolbar" class="tvk-toolbar">
      <slot name="toolbar">
        <!-- 默认工具栏 -->
        <div class="toolbar-left">
          <div class="stock-info">
            <span class="stock-name">{{ stockName || symbol }}</span>
            <span v-if="stockCode" class="stock-code">{{ stockCode }}</span>
          </div>
          <div v-if="realtimePrice" class="price-info">
            <span class="current-price" :class="getPriceChangeClass(realtimePrice.changePercent)">
              {{ realtimePrice.price?.toFixed(2) || '--' }}
            </span>
            <span class="price-change" :class="getPriceChangeClass(realtimePrice.changePercent)">
              {{ formatPriceChange(realtimePrice.changePercent) }}
            </span>
          </div>
        </div>

        <div class="toolbar-center">
          <div class="period-tabs">
            <button
              v-for="period in availablePeriods"
              :key="period.value"
              :class="['period-btn', { active: selectedPeriod === period.value }]"
              @click="handlePeriodChange(period.value)"
            >
              {{ period.label }}
            </button>
          </div>
        </div>

        <div class="toolbar-right">
          <div class="indicator-btns">
            <button
              v-for="indicator in availableIndicators"
              :key="indicator.key"
              :class="['indicator-btn', { active: activeIndicators.has(indicator.key) }]"
              @click="handleIndicatorToggle(indicator.key)"
              :title="indicator.label"
            >
              {{ indicator.label }}
            </button>
          </div>
          <!-- 价格线按钮 -->
          <button
            class="action-btn"
            :class="{ active: showPriceAlertPanel }"
            @click="togglePriceAlertPanel"
            title="价格提醒"
          >
            🔔
          </button>
          <button class="action-btn" @click="resetChart" title="重置图表">
            <i class="fas fa-expand"></i>
          </button>
        </div>
      </slot>
    </div>

    <!-- 价格线面板 -->
    <div v-if="showPriceAlertPanel" class="price-alert-panel">
      <div class="panel-header">
        <span>价格提醒</span>
        <button class="close-btn" @click="showPriceAlertPanel = false">&times;</button>
      </div>
      <div class="panel-content">
        <div class="input-row">
          <input
            v-model.number="priceAlertInput"
            type="number"
            step="0.01"
            placeholder="输入目标价格"
            class="price-input"
            @keyup.enter="addPriceAlert"
          />
          <button class="add-btn" @click="addPriceAlert">添加</button>
        </div>
        <div class="alerts-list">
          <div
            v-for="alert in getPriceAlerts()"
            :key="alert.id"
            class="alert-item"
          >
            <span class="alert-price">{{ alert.price.toFixed(2) }}</span>
            <button class="remove-btn" @click="removePriceAlert(alert.id)">&times;</button>
          </div>
          <div v-if="getPriceAlerts().length === 0" class="no-alerts">
            暂无价格提醒
          </div>
        </div>
        <button v-if="getPriceAlerts().length > 0" class="clear-btn" @click="clearAllPriceAlerts">
          清除全部
        </button>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="tvk-charts-area" :style="{ height: chartsAreaHeight || height }">
      <!-- 主图容器 -->
      <div
        ref="mainChartContainer"
        class="tvk-main-chart"
      ></div>

      <!-- 成交量图 -->
      <div
        ref="volumeChartContainer"
        class="tvk-volume-chart"
      ></div>

      <!-- 指标窗格 -->
      <div
        v-for="pane in indicatorPanes"
        :key="pane.id"
        :ref="el => setIndicatorPaneRef(pane.id, el)"
        class="tvk-indicator-pane"
      ></div>
    </div>

    <!-- 自定义加载状态 -->
    <div v-if="displayLoading" class="tvk-loading">
      <slot name="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </slot>
    </div>

    <!-- 自定义图例 -->
    <div v-if="showLegend" class="tvk-legend">
      <slot name="legend" :data="currentData">
        <div class="legend-content">
          <span v-if="currentData" class="legend-date">
            {{ formatDate(currentData.time) }}
          </span>
          <span v-if="currentData" class="legend-ohlc">
            O: {{ currentData.open.toFixed(2) }}
            H: {{ currentData.high.toFixed(2) }}
            L: {{ currentData.low.toFixed(2) }}
            C: {{ currentData.close.toFixed(2) }}
          </span>
          <span v-if="currentData?.volume" class="legend-volume">
            Vol: {{ formatVolume(currentData.volume) }}
          </span>
        </div>
      </slot>
    </div>

    <!-- 自定义覆盖层 -->
    <slot name="overlay" :chart="chartApi" :data="currentData"></slot>
  </div>
</template>

<script setup lang="ts">
/**
 * TradingViewKLineUnified.vue
 * 统一K线图组件
 *
 * 基于lightweight-charts库，提供完整的K线图功能
 *
 * @features
 * - K线图 + 成交量
 * - 技术指标（MA/EMA/VOL/MACD/KDJ）
 * - 实时数据更新
 * - 主题切换
 * - 响应式设计
 *
 * @author MyQuant v10.0.0 Team
 * @created 2026-02-04
 */

import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { createChart, CandlestickSeries, HistogramSeries, LineSeries } from 'lightweight-charts'
import type { Time, ChartOptions, CandlestickSeriesPartialOptions } from 'lightweight-charts'
import { getUnifiedKline, transformUnifiedKlineData, type KlineDataItem as UnifiedKlineDataItem } from '@/api/unified'
import { cachedFetch } from '@/utils/cacheManager'
import { createKlineWebSocket, type KlineBar, type KlineWebSocketConfig } from '@/services/klineWebSocket'
import { createKlineAggregator, type Timeframe } from '@/services/klineAggregator'
// 导入价格线插件
import { UserPriceAlerts, ExpiringPriceAlerts } from './plugins'

// ==================== 类型定义 ====================

/**
 * K线数据项
 */
export interface KLineDataItem {
  time: Time
  open: number
  high: number
  low: number
  close: number
  volume: number
  ma5?: number
  ma10?: number
  ma20?: number
  ma30?: number
  ma60?: number
  ema6?: number
  ema12?: number
  ema26?: number
}

/**
 * 技术指标配置
 */
export interface IndicatorConfig {
  key: string
  label: string
  type: 'overlay' | 'separate'  // overlay: 叠加在主图，separate: 独立窗格
  color?: string
  params?: Record<string, any>
}

/**
 * 实时价格数据
 */
interface RealtimePrice {
  price: number
  changePercent: number
}

/**
 * 颜色配置
 */
interface TradingViewColors {
  backgroundColor: string
  lineColor: string
  candlestickUpColor: string
  candlestickDownColor: string
  volumeUpColor: string
  volumeDownColor: string
  crosshairColor: string
  gridColor: string
  textColor: string
}

// ==================== Props & Emits ====================

interface Props {
  // 基础配置
  symbol: string
  stockName?: string
  stockCode?: string

  // 布局配置
  width?: string
  height?: string
  showToolbar?: boolean
  showDataZoom?: boolean
  mainChartHeight?: number
  chartsAreaHeight?: string
  showLegend?: boolean

  // 数据配置
  period?: string
  startDate?: string
  endDate?: string
  initialData?: KLineDataItem[]

  // 指标配置
  indicators?: IndicatorConfig[]
  showIndicatorPanes?: boolean

  // 实时配置
  enableRealtime?: boolean
  websocketUrl?: string
  realtimeUpdateInterval?: number

  // 主题配置
  theme?: 'light' | 'dark'
  colors?: Partial<TradingViewColors>

  // 性能配置
  animationEnabled?: boolean
  maxDataPoints?: number

  // 加载状态
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '600px',
  showToolbar: true,
  showDataZoom: true,
  mainChartHeight: 400,
  showLegend: true,
  period: 'day',
  enableRealtime: true,
  theme: 'dark',
  animationEnabled: false,
  maxDataPoints: 1000,
  loading: false
})

const emit = defineEmits<{
  chartReady: []
  dataUpdate: [data: KLineDataItem[]]
  periodChange: [period: string]
  indicatorToggle: [indicator: string, enabled: boolean]
  dataZoom: [start: number, end: number]
  crosshairMove: [data: any]
  dataClick: [data: KLineDataItem]
}>()

// ==================== 常量定义 ====================

// 可用周期
const AVAILABLE_PERIODS = [
  { value: '1m', label: '1分' },
  { value: '5m', label: '5分' },
  { value: '15m', label: '15分' },
  { value: '30m', label: '30分' },
  { value: '60m', label: '60分' },
  { value: 'day', label: '日线' },
  { value: 'week', label: '周线' },
  { value: 'month', label: '月线' }
]

// 可用指标
const AVAILABLE_INDICATORS: IndicatorConfig[] = [
  { key: 'ma5', label: 'MA5', type: 'overlay', color: '#F23645' },
  { key: 'ma10', label: 'MA10', type: 'overlay', color: '#FFC107' },
  { key: 'ma20', label: 'MA20', type: 'overlay', color: '#089981' },
  { key: 'ma30', label: 'MA30', type: 'overlay', color: '#2196F3' },
  { key: 'ma60', label: 'MA60', type: 'overlay', color: '#9C27B0' },
  { key: 'vol', label: 'VOL', type: 'separate' },
  { key: 'macd', label: 'MACD', type: 'separate' }
]

// 默认颜色配置
const DEFAULT_COLORS: Record<'light' | 'dark', TradingViewColors> = {
  dark: {
    backgroundColor: '#131722',
    lineColor: '#2196F3',
    candlestickUpColor: '#089981',
    candlestickDownColor: '#F23645',
    volumeUpColor: 'rgba(8, 153, 129, 0.5)',
    volumeDownColor: 'rgba(242, 54, 69, 0.5)',
    crosshairColor: '#758696',
    gridColor: '#1E222D',
    textColor: '#D1D4DC'
  },
  light: {
    backgroundColor: '#FFFFFF',
    lineColor: '#2196F3',
    candlestickUpColor: '#089981',
    candlestickDownColor: '#F23645',
    volumeUpColor: 'rgba(8, 153, 129, 0.5)',
    volumeDownColor: 'rgba(242, 54, 69, 0.5)',
    crosshairColor: '#758696',
    gridColor: '#E0E3EB',
    textColor: '#131722'
  }
}

// ==================== 响应式状态 ====================

const mainChartContainer = ref<HTMLElement>()
const volumeChartContainer = ref<HTMLElement>()

// 图表实例
let chartApi: ReturnType<typeof createChart> | null = null
let candlestickSeries: CandlestickSeries | null = null
let volumeSeries: HistogramSeries | null = null
const indicatorSeries = ref<Map<string, LineSeries | HistogramSeries>>(new Map())

// 数据状态
const chartData = ref<KLineDataItem[]>([])
const selectedPeriod = ref(props.period)
const activeIndicators = ref<Set<string>>(new Set())
const realtimePrice = ref<RealtimePrice | null>(null)
const currentData = ref<KLineDataItem | null>(null)
const isLoadingMore = ref(false)  // 是否正在加载更多数据

// WebSocket 和聚合器
let klineWs: ReturnType<typeof createKlineWebSocket> | null = null
let aggregator: ReturnType<typeof createKlineAggregator> | null = null
const wsConnected = ref(false)
const useWebSocket = ref(true)  // 是否启用 WebSocket（失败后自动降级）

// 指标窗格
const indicatorPaneRefs = ref<Map<string, HTMLElement>>(new Map())
const indicatorPanes = ref<Array<{ id: string; name: string; height: number }>>([])

// 价格线插件
let userPriceAlerts: UserPriceAlerts | null = null
let expiringPriceAlerts: ExpiringPriceAlerts | null = null
const priceAlertsEnabled = ref(false)
const expiringAlertsEnabled = ref(false)
const priceAlertInput = ref<number | null>(null)
const showPriceAlertPanel = ref(false)

// 计算属性
const availablePeriods = computed(() => AVAILABLE_PERIODS)
const availableIndicators = computed(() => AVAILABLE_INDICATORS)
const displayLoading = computed(() => props.loading)

// ==================== 图表初始化 ====================

const initChart = () => {
  if (!mainChartContainer.value) return

  // 合并颜色配置
  const colors = { ...DEFAULT_COLORS[props.theme], ...props.colors }

  // 创建图表
  chartApi = createChart(mainChartContainer.value, {
    width: mainChartContainer.value.clientWidth,
    height: props.mainChartHeight,
    layout: {
      background: { type: 'solid', color: colors.backgroundColor },
      textColor: colors.textColor
    },
    grid: {
      vertLines: { color: colors.gridColor },
      horzLines: { color: colors.gridColor }
    },
    crosshair: {
      mode: 1,
      vertLine: {
        color: colors.crosshairColor,
        width: 1,
        style: 3
      },
      horzLine: {
        color: colors.crosshairColor,
        width: 1,
        style: 3
      }
    },
    rightPriceScale: {
      borderColor: colors.gridColor
    },
    timeScale: {
      borderColor: colors.gridColor,
      timeVisible: true,
      secondsVisible: false,
      // 调整右边距，让图表更紧凑
      rightOffset: 5,
      // 增加K线间距，让假期间隙不那么明显
      minBarSpacing: 3,
      barSpacing: 10
    },
    animation: props.animationEnabled
  })

  // 创建K线系列
  candlestickSeries = chartApi.addSeries(CandlestickSeries, {
    upColor: colors.candlestickUpColor,
    downColor: colors.candlestickDownColor,
    borderUpColor: colors.candlestickUpColor,
    borderDownColor: colors.candlestickDownColor,
    wickUpColor: colors.candlestickUpColor,
    wickDownColor: colors.candlestickDownColor
  })

  // 创建成交量系列
  if (volumeChartContainer.value) {
    volumeSeries = chartApi.addSeries(HistogramSeries, {
      color: colors.volumeUpColor,
      priceFormat: {
        type: 'volume'
      },
      priceScaleId: ''
    })
  }

  // 监听十字光标移动
  chartApi.subscribeCrosshairMove((param) => {
    if (param.time) {
      const dataPoint = chartData.value.find(d => d.time === param.time)
      currentData.value = dataPoint || null
      emit('crosshairMove', param)
    }
  })

  // 监听点击事件
  chartApi.subscribeClick((param) => {
    if (param.time && candlestickSeries) {
      const dataPoint = chartData.value.find(d => d.time === param.time)
      if (dataPoint) {
        emit('dataClick', dataPoint)
      }
    }
  })

  // 监听可见范围变化（数据缩放）
  chartApi.timeScale().subscribeVisibleLogicalRangeChange((range) => {
    if (range) {
      const start = range.from / chartApi!.timeScale().getVisibleLogicalRange()!.to
      const end = range.to / chartApi!.timeScale().getVisibleLogicalRange()!.to
      emit('dataZoom', start, end)
    }
  })

  // 初始化价格线插件
  initPriceAlertPlugins()

  emit('chartReady')
}

// ==================== 价格线插件 ====================

/**
 * 初始化价格线插件
 */
const initPriceAlertPlugins = () => {
  if (!chartApi || !candlestickSeries) return

  // 初始化用户价格线插件
  if (!userPriceAlerts) {
    userPriceAlerts = new UserPriceAlerts({
      color: props.theme === 'dark' ? '#2196F3' : '#1976D2',
      lineWidth: 1,
      lineStyle: 2, // dashed
      axisLabelVisible: true,
    })
    userPriceAlerts.attach(chartApi, candlestickSeries)

    // 加载已保存的价格线
    if (props.symbol) {
      userPriceAlerts.loadFromStorage(props.symbol)
    }
  }

  // 初始化过期价格线插件
  if (!expiringPriceAlerts) {
    expiringPriceAlerts = new ExpiringPriceAlerts({
      color: props.theme === 'dark' ? '#FF9800' : '#F57C00',
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: true,
      clearTimeout: 5000,
    })
    expiringPriceAlerts.attach(chartApi, candlestickSeries)
  }
}

/**
 * 切换价格线面板显示
 */
const togglePriceAlertPanel = () => {
  showPriceAlertPanel.value = !showPriceAlertPanel.value
}

/**
 * 添加价格线
 */
const addPriceAlert = () => {
  if (!userPriceAlerts || !priceAlertInput.value) return

  const price = Number(priceAlertInput.value)
  if (isNaN(price) || price <= 0) {
    alert('请输入有效的价格')
    return
  }

  userPriceAlerts.addAlert(price, {
    title: `目标: ${price.toFixed(2)}`,
  })

  // 保存到本地存储
  if (props.symbol) {
    userPriceAlerts.saveToStorage(props.symbol)
  }

  priceAlertInput.value = null
}

/**
 * 删除价格线
 */
const removePriceAlert = (id: string) => {
  if (!userPriceAlerts) return

  userPriceAlerts.removeAlert(id)

  // 更新本地存储
  if (props.symbol) {
    userPriceAlerts.saveToStorage(props.symbol)
  }
}

/**
 * 获取当前所有价格线
 */
const getPriceAlerts = () => {
  if (!userPriceAlerts) return []
  return userPriceAlerts.getAlerts()
}

/**
 * 清除所有价格线
 */
const clearAllPriceAlerts = () => {
  if (!userPriceAlerts) return

  userPriceAlerts.clearAll()

  // 清除本地存储
  if (props.symbol) {
    localStorage.removeItem(`price_alerts_${props.symbol}`)
  }
}

/**
 * 添加过期价格线（用于测试）
 */
const addExpiringAlert = (price: number, durationMinutes: number = 5) => {
  if (!expiringPriceAlerts) return

  const now = Date.now() / 1000
  const startTime = now
  const endTime = now + durationMinutes * 60

  expiringPriceAlerts.addAlert(price, startTime, endTime, {
    title: `限时: ${price.toFixed(2)}`,
  })
}

// ==================== 数据加载 ====================

/**
 * 周期映射：将组件周期转换为API周期格式
 */
const mapPeriodToApi = (period: string): string => {
  const periodMap: Record<string, string> = {
    '1m': '1m',
    '5m': '5m',
    '15m': '15m',
    '30m': '30m',
    '60m': '1h',
    'day': '1d',
    'week': '1w',
    'month': '1mon'
  }
  return periodMap[period] || period
}

const loadData = async (period: string) => {
  try {
    console.log(`[TradingViewKLine] Loading data for ${props.symbol}, period: ${period}`)

    // 映射周期格式
    const apiPeriod = mapPeriodToApi(period)

    // ⭐ 缓存策略优化
    // - 缓存键包含数据源标识，避免不同源的数据混淆
    // - 缩短 TTL 到 5 分钟，避免长时间持有错误数据
    // - HotDB 已经是持久化存储，前端短缓存即可
    const cacheKey = `kline_${props.symbol}_${apiPeriod}`
    const cacheTTL = 5 * 60 * 1000  // 5分钟缓存（后端 HotDB 已经很快）

    const response = await cachedFetch(cacheKey, async () => {
      // ⭐ 修复：传入前端格式的 period（'day'/'month'），而非 apiPeriod（'1d'/'1mon'）
      // getUnifiedKline 内部会自行映射到后端格式
      console.log(`[TradingViewKLine] API调用: period=${period} (mapped from frontend to backend)`)
      const result = await getUnifiedKline(props.symbol, period as any, 500)
      console.log(`[TradingViewKLine] API原始响应:`, result)
      return result
    }, cacheTTL)

    if (response.code === 200 && response.data && response.data.length > 0) {
      const elapsedMs = response.metadata?.elapsed_ms || 0
      const dataSource = response.metadata?.source || 'unknown'

      console.log(`[TradingViewKLine] ✅ Loaded ${response.data.length} candles from ${dataSource} in ${elapsedMs}ms`)

      // ⭐ 使用统一数据转换函数
      const mappedData = transformUnifiedKlineData(response.data)
        .filter((item: KLineDataItem) => {
          // 过滤无效数据：成交量为0且价格全部相同的数据（停牌数据）
          const isValid = item.volume > 0 ||
            (item.open !== item.high || item.high !== item.low || item.low !== item.close)
          return isValid
        })

      console.log(`[TradingViewKLine] Filtered to ${mappedData.length} valid candles (removed ${response.data.length - mappedData.length} invalid)`)

      // 数据排序：按时间升序排列（从旧到新）
      chartData.value = mappedData.sort((a, b) => a.time - b.time)

      await updateChart()
    } else {
      // 数据为空的提示
      const emptyReason = response.code === 200 && (!response.data || response.data.length === 0)
        ? '该股票暂无K线数据（可能是数据源问题，请尝试其他股票）'
        : response.message

      console.warn(`[TradingViewKLine] API returned no data: ${emptyReason}`)

      // 显示空状态
      if (!chartData.value || chartData.value.length === 0) {
        console.warn(`[TradingViewKLine] 股票 ${props.symbol} 无数据，请检查：`)
        console.warn('  1. 股票代码格式是否正确（如 600000.SH, 000001.SZ）')
        console.warn('  2. 该股票是否在数据源中可用')
        console.warn('  3. 建议尝试上海市场股票（.SH后缀）')
      }
      // 降级使用props数据
      if (props.initialData && props.initialData.length > 0) {
        chartData.value = props.initialData
        await updateChart()
      }
    }
  } catch (error) {
    console.error('[TradingViewKLine] Failed to load data:', error)
    // 降级使用props数据
    if (props.initialData && props.initialData.length > 0) {
      chartData.value = props.initialData
      await updateChart()
    }
  }
}

const updateChart = async () => {
  if (!candlestickSeries) return

  // 更新K线数据
  candlestickSeries.setData(chartData.value)

  // 更新成交量数据
  if (volumeSeries) {
    const volumeData = chartData.value.map(d => ({
      time: d.time,
      value: d.volume,
      color: d.close >= d.open
        ? DEFAULT_COLORS[props.theme].volumeUpColor
        : DEFAULT_COLORS[props.theme].volumeDownColor
    }))
    volumeSeries.setData(volumeData)
  }

  // 更新指标
  await updateIndicators()

  // 自动适配视图范围（确保所有K线可见）
  if (chartApi) {
    chartApi.timeScale().fitContent()
  }

  emit('dataUpdate', chartData.value)
}

const updateIndicators = async () => {
  // 更新MA指标
  for (const indicatorKey of activeIndicators.value) {
    const indicatorConfig = AVAILABLE_INDICATORS.find(i => i.key === indicatorKey)
    if (!indicatorConfig || indicatorConfig.type !== 'overlay') continue

    // 获取指标数据
    const indicatorData = chartData.value
      .filter(d => d[indicatorKey as keyof KLineDataItem] !== undefined)
      .map(d => ({
        time: d.time,
        value: d[indicatorKey as keyof KLineDataItem] as number
      }))

    // 创建或更新系列
    if (!indicatorSeries.value.has(indicatorKey)) {
      const series = chartApi!.addSeries(LineSeries, {
        color: indicatorConfig.color,
        lineWidth: 1,
        title: indicatorConfig.label
      })
      indicatorSeries.value.set(indicatorKey, series)
    }

    const series = indicatorSeries.value.get(indicatorKey) as LineSeries
    series.setData(indicatorData)
  }
}

// ==================== 指标管理 ====================

const handleIndicatorToggle = (indicatorKey: string) => {
  if (activeIndicators.value.has(indicatorKey)) {
    activeIndicators.value.delete(indicatorKey)
    removeIndicatorSeries(indicatorKey)
  } else {
    activeIndicators.value.add(indicatorKey)
    updateIndicators()
  }

  emit('indicatorToggle', indicatorKey, activeIndicators.value.has(indicatorKey))
}

const removeIndicatorSeries = (indicatorKey: string) => {
  const series = indicatorSeries.value.get(indicatorKey)
  if (series) {
    chartApi?.removeSeries(series)
    indicatorSeries.value.delete(indicatorKey)
  }
}

// ==================== 周期切换 ====================

const handlePeriodChange = async (period: string) => {
  if (period === selectedPeriod.value) return

  try {
    // 断开旧连接
    disconnectKlineWs()

    // ⭐ 不再清除缓存！各周期缓存独立，按周期键存储不会互相污染
    // kline_${symbol}_1d 和 kline_${symbol}_1mon 是不同的键

    selectedPeriod.value = period
    await loadData(period)
    emit('periodChange', period)

    // 重新连接 WebSocket（使用新周期）
    if (props.enableRealtime) {
      // 延迟重连，确保图表已更新完成
      await nextTick()
      connectKlineWs()
    }
  } catch (error) {
    console.error('[handlePeriodChange] 切换周期失败:', error)
    // 尝试恢复
    await loadData(selectedPeriod.value)
  }
}

// ==================== 工具方法 ====================

const resetChart = () => {
  chartApi?.timeScale().fitContent()
}

const getPriceChangeClass = (percent: number) => {
  if (percent > 0) return 'up'
  if (percent < 0) return 'down'
  return ''
}

const formatPriceChange = (percent: number) => {
  const sign = percent >= 0 ? '+' : ''
  return `${sign}${percent.toFixed(2)}%`
}

const formatDate = (time: Time): string => {
  if (typeof time === 'number') {
    const date = new Date(time * 1000)
    return date.toLocaleDateString('zh-CN')
  }
  return String(time)
}

const formatVolume = (volume: number): string => {
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(2)}亿`
  }
  if (volume >= 10000) {
    return `${(volume / 10000).toFixed(2)}万`
  }
  return volume.toString()
}

const setIndicatorPaneRef = (id: string, el: any) => {
  if (el) {
    indicatorPaneRefs.value.set(id, el)
  }
}

// ==================== 实时更新 ====================

let realtimeTimer: ReturnType<typeof setInterval> | null = null

const startRealtimeUpdate = () => {
  if (!props.enableRealtime || realtimeTimer) return

  const interval = props.realtimeUpdateInterval || 3000 // 默认3秒

  realtimeTimer = setInterval(async () => {
    try {
      // 只在交易时间内更新
      const now = new Date()
      const hour = now.getHours()
      const minute = now.getMinutes()
      const currentTime = hour * 60 + minute

      // A股交易时间：9:30-11:30, 13:00-15:00
      const isMorning = currentTime >= 9 * 60 + 30 && currentTime <= 11 * 60 + 30
      const isAfternoon = currentTime >= 13 * 60 && currentTime <= 15 * 60
      const isWeekend = now.getDay() === 0 || now.getDay() === 6

      if (!isWeekend && (isMorning || isAfternoon)) {
        // 只在日K线级别才实时更新
        if (['day', '1d'].includes(selectedPeriod.value)) {
          await loadData(selectedPeriod.value)
        }
      }
    } catch (error) {
      console.error('[TradingViewKLine] Realtime update failed:', error)
    }
  }, interval)

  console.log(`[TradingViewKLine] Realtime update started (interval: ${interval}ms)`)
}

const stopRealtimeUpdate = () => {
  if (realtimeTimer) {
    clearInterval(realtimeTimer)
    realtimeTimer = null
    console.log('[TradingViewKLine] Realtime update stopped')
  }
}

// ==================== WebSocket 实时推送 ====================

/**
 * 连接 K线 WebSocket
 */
const connectKlineWs = () => {
  if (!props.enableRealtime || !useWebSocket.value) return
  if (klineWs) return  // 已连接

  console.log('[TradingViewKLine] 连接 WebSocket:', props.symbol)

  // 将组件周期转换为 Timeframe
  const periodMap: Record<string, Timeframe> = {
    '1m': '1m',
    '5m': '5m',
    '15m': '15m',
    '30m': '30m',
    '60m': '60m',
    'day': '1d',
    'week': '1w',
    'month': '1M'
  }

  const timeframe = periodMap[selectedPeriod.value] || '1d'

  // 初始化聚合器
  aggregator = createKlineAggregator(timeframe)

  const wsConfig: KlineWebSocketConfig = {
    onConnected: () => {
      wsConnected.value = true
      console.log('[TradingViewKLine] WebSocket 已连接')
    },
    onDisconnected: () => {
      wsConnected.value = false
      console.log('[TradingViewKLine] WebSocket 已断开')
    },
    onHistory: (bars: KlineBar[]) => {
      // WebSocket 历史数据只用于初始化聚合器
      console.log('[TradingViewKLine] WS 历史数据:', bars.length, '根')
      if (aggregator && bars.length > 0) {
        aggregator.onHistory(bars)
      }
    },
    onBarUpdate: (bar: KlineBar) => {
      // 最后一根 K线更新
      console.log('[TradingViewKLine] WS Bar 更新:', bar)
      if (!aggregator) return

      const aggregated = aggregator.onBarUpdate(bar)
      if (aggregated) {
        updateLastBar(aggregated)
      }
    },
    onBarClose: (bar: KlineBar) => {
      // K线收线
      console.log('[TradingViewKLine] WS Bar 收线:', bar)
      if (!aggregator) return

      const aggregated = aggregator.onBarClose(bar)
      if (aggregated) {
        updateLastBar(aggregated)
      }
    },
    onError: (message: string) => {
      console.error('[TradingViewKLine] WebSocket 错误:', message)
      // WebSocket 失败，降级到定时轮询
      if (useWebSocket.value) {
        console.log('[TradingViewKLine] WebSocket 失败，降级到定时轮询')
        useWebSocket.value = false
        startRealtimeUpdate()
      }
    }
  }

  klineWs = createKlineWebSocket(props.symbol, wsConfig)
  klineWs.connect()
}

/**
 * 断开 WebSocket
 */
const disconnectKlineWs = () => {
  if (klineWs) {
    klineWs.disconnect()
    klineWs = null
  }
  wsConnected.value = false
  aggregator = null
}

/**
 * 更新最后一根 K线
 */
const updateLastBar = (bar: KlineBar) => {
  if (!chartData.value || chartData.value.length === 0) return

  // 转换时间格式
  let time: Time
  if (typeof bar.time === 'string') {
    time = new Date(bar.time).getTime() / 1000 as Time
  } else {
    time = bar.time as Time
  }

  const lastBar = {
    time,
    open: bar.open,
    high: bar.high,
    low: bar.low,
    close: bar.close,
    volume: bar.volume
  }

  // 更新最后一根
  const lastIndex = chartData.value.length - 1
  chartData.value[lastIndex] = lastBar

  // 更新图表
  if (candlestickSeries) {
    candlestickSeries.update(lastBar)
  }
}

// ==================== 生命周期 ====================

onMounted(async () => {
  await nextTick()
  initChart()
  await loadData(props.period)

  // 优先使用 WebSocket 实时推送
  if (props.enableRealtime) {
    connectKlineWs()
    // 如果 WebSocket 连接失败，会自动降级到定时轮询
  }

  // 响应窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)

  // 清理实时更新
  stopRealtimeUpdate()
  disconnectKlineWs()

  // 清理图表
  if (chartApi) {
    chartApi.remove()
    chartApi = null
  }
})

// ==================== 监听器 ====================

const handleResize = () => {
  if (mainChartContainer.value && chartApi) {
    chartApi.applyOptions({
      width: mainChartContainer.value.clientWidth
    })
  }
}

// 监听symbol变化
watch(() => props.symbol, async (newSymbol, oldSymbol) => {
  if (newSymbol !== oldSymbol) {
    // 断开旧连接
    disconnectKlineWs()

    // 加载新股票数据
    await loadData(selectedPeriod.value)

    // 重新连接 WebSocket
    if (props.enableRealtime) {
      connectKlineWs()
    }

    // 重新加载价格线
    if (userPriceAlerts && newSymbol) {
      userPriceAlerts.clearAll()
      userPriceAlerts.loadFromStorage(newSymbol)
    }
  }
})

// 监听主题变化
watch(() => props.theme, (newTheme) => {
  if (chartApi) {
    const colors = DEFAULT_COLORS[newTheme]
    chartApi.applyOptions({
      layout: {
        background: { type: 'solid', color: colors.backgroundColor },
        textColor: colors.textColor
      },
      grid: {
        vertLines: { color: colors.gridColor },
        horzLines: { color: colors.gridColor }
      }
    })
  }
})

// 监听initialData变化
watch(() => props.initialData, async (newData) => {
  if (newData && newData.length > 0) {
    chartData.value = newData
    await updateChart()
  }
})

// 监听实时更新开关
watch(() => props.enableRealtime, (enabled) => {
  if (enabled) {
    startRealtimeUpdate()
  } else {
    stopRealtimeUpdate()
  }
})
</script>

<style scoped>
.trading-view-kline-unified {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: var(--tvk-bg-color, #131722);
  color: var(--tvk-text-color, #D1D4DC);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 工具栏 */
.tvk-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background-color: var(--tvk-toolbar-bg, #1E222D);
  border-bottom: 1px solid var(--tvk-border-color, #2A2E39);
  user-select: none;
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-info {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.stock-name {
  font-size: 16px;
  font-weight: 600;
}

.stock-code {
  font-size: 12px;
  opacity: 0.7;
}

.price-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-price {
  font-size: 18px;
  font-weight: 600;
}

.price-change {
  font-size: 12px;
}

.up {
  color: #089981;
}

.down {
  color: #F23645;
}

/* 周期标签 */
.period-tabs,
.indicator-btns {
  display: flex;
  gap: 4px;
}

.period-btn,
.indicator-btn {
  padding: 4px 12px;
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.period-btn:hover,
.indicator-btn:hover {
  background-color: var(--tvk-hover-bg, #2A2E39);
}

.period-btn.active,
.indicator-btn.active {
  background-color: var(--tvk-active-bg, #2196F3);
  color: white;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  border-radius: 4px;
}

.action-btn:hover {
  background-color: var(--tvk-hover-bg, #2A2E39);
}

/* 图表区域 */
.tvk-charts-area {
  position: relative;
}

.tvk-main-chart,
.tvk-volume-chart,
.tvk-indicator-pane {
  width: 100%;
}

/* 加载状态 */
.tvk-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 100;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 图例 */
.tvk-legend {
  position: absolute;
  top: 8px;
  left: 16px;
  padding: 4px 8px;
  background-color: rgba(0, 0, 0, 0.7);
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 10;
}

.legend-content {
  display: flex;
  gap: 12px;
}

/* 主题样式 */
.theme-light {
  --tvk-bg-color: #FFFFFF;
  --tvk-text-color: #131722;
  --tvk-toolbar-bg: #F0F3FA;
  --tvk-border-color: #E0E3EB;
  --tvk-hover-bg: #E0E3EB;
  --tvk-active-bg: #2196F3;
}

.theme-dark {
  --tvk-bg-color: #131722;
  --tvk-text-color: #D1D4DC;
  --tvk-toolbar-bg: #1E222D;
  --tvk-border-color: #2A2E39;
  --tvk-hover-bg: #2A2E39;
  --tvk-active-bg: #2196F3;
}

/* 价格线面板 */
.price-alert-panel {
  position: absolute;
  top: 50px;
  right: 16px;
  width: 220px;
  background-color: var(--tvk-bg-color, #1E222D);
  border: 1px solid var(--tvk-border-color, #2A2E39);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 100;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid var(--tvk-border-color, #2A2E39);
  font-weight: 500;
  font-size: 13px;
}

.close-btn {
  background: none;
  border: none;
  color: var(--tvk-text-color, #D1D4DC);
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: var(--tvk-up-color, #F23645);
}

.panel-content {
  padding: 12px;
}

.input-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.price-input {
  flex: 1;
  padding: 6px 10px;
  background-color: var(--tvk-toolbar-bg, #2A2E39);
  border: 1px solid var(--tvk-border-color, #363A45);
  border-radius: 3px;
  color: var(--tvk-text-color, #D1D4DC);
  font-size: 13px;
}

.price-input:focus {
  outline: none;
  border-color: var(--tvk-active-bg, #2196F3);
}

.add-btn {
  padding: 6px 12px;
  background-color: var(--tvk-active-bg, #2196F3);
  border: none;
  border-radius: 3px;
  color: white;
  font-size: 12px;
  cursor: pointer;
}

.add-btn:hover {
  background-color: #1976D2;
}

.alerts-list {
  max-height: 150px;
  overflow-y: auto;
  margin-bottom: 10px;
}

.alert-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background-color: var(--tvk-toolbar-bg, #2A2E39);
  border-radius: 3px;
  margin-bottom: 6px;
}

.alert-price {
  font-size: 13px;
  font-weight: 500;
  color: var(--tvk-active-bg, #2196F3);
}

.remove-btn {
  background: none;
  border: none;
  color: var(--tvk-down-color, #F23645);
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  color: #FF5252;
}

.no-alerts {
  text-align: center;
  padding: 16px;
  color: var(--tvk-text-secondary, #758696);
  font-size: 12px;
}

.clear-btn {
  width: 100%;
  padding: 6px;
  background-color: transparent;
  border: 1px solid var(--tvk-down-color, #F23645);
  border-radius: 3px;
  color: var(--tvk-down-color, #F23645);
  font-size: 12px;
  cursor: pointer;
}

.clear-btn:hover {
  background-color: rgba(242, 54, 69, 0.1);
}

/* 浅色主题适配 */
.theme-light .price-alert-panel {
  --tvk-bg-color: #FFFFFF;
  --tvk-border-color: #E0E3EB;
  --tvk-toolbar-bg: #F8F9FA;
  --tvk-text-color: #131722;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.theme-light .price-input {
  background-color: #FFFFFF;
  border-color: #E0E3EB;
  color: #131722;
}

.theme-light .alert-item {
  background-color: #F8F9FA;
}
</style>
