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
          <button class="action-btn" @click="resetChart" title="重置图表">
            <i class="fas fa-expand"></i>
          </button>
        </div>
      </slot>
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
const hasMoreData = ref(true)     // 是否还有更多历史数据
const earliestDataTime = ref<number | null>(null)  // 最早数据时间

// 指标窗格
const indicatorPaneRefs = ref<Map<string, HTMLElement>>(new Map())
const indicatorPanes = ref<Array<{ id: string; name: string; height: number }>>([])

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

  // 监听可见范围变化（拖动加载更多）
  chartApi.timeScale().subscribeVisibleLogicalRangeChange((range) => {
    if (range && chartApi) {
      const totalBars = chartData.value.length
      const visibleRange = chartApi.timeScale().getVisibleLogicalRange()

      if (visibleRange) {
        const start = range.from / visibleRange.to
        const end = range.to / visibleRange.to
        emit('dataZoom', start, end)

        // 检测是否拖动到左边缘（from < 5 表示接近最左边）
        if (range.from < 5 && !isLoadingMore.value && totalBars > 0) {
          loadMoreData()
        }
      }
    }
  })

  emit('chartReady')
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

    // ⭐ 调用统一数据API（/api/v1/data/unified）
    // 后端UnifiedDataManager会自动选择最优数据源
    const response = await getUnifiedKline(props.symbol, apiPeriod as any, 500)

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

/**
 * 加载更多历史数据（拖动到边缘时触发）
 */
const loadMoreData = async () => {
  if (isLoadingMore.value || !hasMoreData.value || chartData.value.length === 0) {
    return
  }

  isLoadingMore.value = true
  console.log('[TradingViewKLine] Loading more historical data...')

  try {
    // 获取当前最早的数据日期
    const oldestData = chartData.value[0]
    if (!oldestData) {
      isLoadingMore.value = false
      return
    }

    // 将时间戳转换为日期字符串 (YYYY-MM-DD)
    const oldestDate = new Date(oldestData.time * 1000)
    const endDateStr = oldestDate.toISOString().slice(0, 10)

    // 映射周期格式
    const apiPeriod = mapPeriodToApi(selectedPeriod.value)

    // 请求更早的数据（当前最早日期之前的数据）
    const response = await getUnifiedKline(props.symbol, apiPeriod as any, 500, endDateStr)

    if (response.code === 200 && response.data && response.data.length > 0) {
      const newMappedData = transformUnifiedKlineData(response.data)
        .filter((item: KLineDataItem) => {
          const isValid = item.volume > 0 ||
            (item.open !== item.high || item.high !== item.low || item.low !== item.close)
          return isValid
        })

      if (newMappedData.length === 0) {
        hasMoreData.value = false
        console.log('[TradingViewKLine] No more historical data available')
        isLoadingMore.value = false
        return
      }

      // 去重：排除已有的数据（按时间戳去重）
      const existingTimes = new Set(chartData.value.map(d => d.time))
      const uniqueNewData = newMappedData.filter((item: KLineDataItem) => !existingTimes.has(item.time))

      if (uniqueNewData.length === 0) {
        hasMoreData.value = false
        console.log('[TradingViewKLine] All data already loaded')
        isLoadingMore.value = false
        return
      }

      console.log(`[TradingViewKLine] Loaded ${uniqueNewData.length} more candles`)

      // 记录当前可见范围（用于加载后恢复位置）
      const currentRange = chartApi?.timeScale().getVisibleLogicalRange()

      // 将新数据前置到现有数据（按时间升序）
      const combinedData = [...uniqueNewData, ...chartData.value].sort((a, b) => a.time - b.time)
      chartData.value = combinedData

      // 更新图表数据（不调用fitContent，保持当前位置）
      if (candlestickSeries) {
        candlestickSeries.setData(chartData.value)
      }

      // 更新成交量
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

      // 恢复可见范围（保持用户当前查看的位置）
      if (chartApi && currentRange) {
        // 计算新增数据的偏移量
        const offset = uniqueNewData.length
        chartApi.timeScale().setVisibleLogicalRange({
          from: currentRange.from + offset,
          to: currentRange.to + offset
        })
      }

      // 更新指标
      await updateIndicators()

      emit('dataUpdate', chartData.value)
    } else {
      // 没有更多数据了
      hasMoreData.value = false
      console.log('[TradingViewKLine] Reached end of historical data')
    }
  } catch (error) {
    console.error('[TradingViewKLine] Failed to load more data:', error)
  } finally {
    isLoadingMore.value = false
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

  selectedPeriod.value = period
  await loadData(period)
  emit('periodChange', period)
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

// ==================== 生命周期 ====================

onMounted(async () => {
  await nextTick()
  initChart()
  await loadData(props.period)
  startRealtimeUpdate()

  // 响应窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  stopRealtimeUpdate()

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
    await loadData(selectedPeriod.value)
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
</style>
