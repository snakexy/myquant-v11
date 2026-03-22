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
          <div class="adjust-tabs">
            <button
              v-for="adjust in adjustOptions"
              :key="adjust.value"
              :class="['adjust-btn', { active: selectedAdjustType === adjust.value }]"
              @click="handleAdjustTypeChange(adjust.value)"
              :title="adjust.label"
            >
              {{ adjust.label }}
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
    <div class="tvk-charts-area" :style="chartsAreaHeight ? { height: chartsAreaHeight } : undefined">
      <!-- 主图容器 -->
      <div class="tvk-main-chart-wrapper">
        <div
          ref="mainChartContainer"
          class="tvk-main-chart"
        ></div>
        <!-- 自定义收盘价标签，不依赖 lightweight-charts 的 lastValueVisible -->
        <div
          ref="priceLabelEl"
          class="tvk-price-label"
          :class="lastPriceUp ? 'tvk-price-up' : 'tvk-price-down'"
          :style="{ top: priceLabelY + 'px' }"
        >{{ priceLabelText }}</div>
      </div>

      <!-- 成交量已作为overlay集成到主图中 -->

      <!-- 拖拽分隔条（仅MACD可见时显示，在主图和MACD之间） -->
      <div
        v-if="activeIndicators.has('macd')"
        class="tvk-resize-handle"
        @mousedown="onResizeStart"
        title="拖拽调整高度"
      >
        <div class="resize-handle-bar"></div>
      </div>

      <!-- MACD 独立窗格 -->
      <div
        v-if="activeIndicators.has('macd')"
        ref="macdChartContainer"
        class="tvk-macd-pane"
        :style="{ height: macdHeight + 'px' }"
      >
        <!-- MACD label rendered by lightweight-charts lastValueVisible -->
      </div>

      <!-- 指标窗格 -->
      <div
        v-for="pane in indicatorPanes"
        :key="pane.id"
        :ref="el => setIndicatorPaneRef(pane.id, el)"
        class="tvk-indicator-pane"
      ></div>

      <!-- 自定义图例 - 跟随十字光标移动 -->
      <div v-if="showLegend" class="tvk-legend" :style="legendStyle">
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
    </div>

    <!-- 自定义加载状态 -->
    <div v-if="displayLoading" class="tvk-loading">
      <slot name="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </slot>
    </div>

    <!-- 自定义覆盖层 -->
    <slot name="overlay" :chart="chartApi" :data="currentData"></slot>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
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
import {
  getSeamlessKline,
  transformKlineData,
  DEFAULT_KLINE_CONFIG,
  type KlineDataItem,
  type KlineResponse
} from '@/api/kline'

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
  adjustType?: 'none' | 'qfq' | 'hfq'  // 复权类型

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

/**
 * 判断是否为分钟级周期
 * 分钟级周期需要显示时间，日线及以上只显示日期
 */
const isIntradayPeriod = computed(() => {
  const period = props.period || 'day'
  return ['1m', '5m', '15m', '30m', '1h', '60m', '1min'].includes(period)
})

// 图例跟随十字光标的动态样式
const legendStyle = computed(() => {
  if (crosshairX.value === null || !mainChartContainer.value) {
    return { top: '8px', left: '16px' }
  }
  const chartWidth = mainChartContainer.value.clientWidth
  const estimatedLegendWidth = 420
  let x = crosshairX.value + 15
  // 如果超出右边界，移到光标左侧
  if (x + estimatedLegendWidth > chartWidth - 10) {
    x = crosshairX.value - estimatedLegendWidth - 15
  }
  // 限制在图表范围内
  x = Math.max(10, Math.min(x, chartWidth - 100))
  return { top: '8px', left: `${x}px` }
})

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '600px',
  showToolbar: true,
  showDataZoom: true,
  mainChartHeight: 400,
  showLegend: true,
  period: 'day',
  adjustType: 'none',  // 默认不复权
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
    candlestickUpColor: '#F23645',
    candlestickDownColor: '#089981',
    volumeUpColor: 'rgba(242, 54, 69, 0.5)',
    volumeDownColor: 'rgba(8, 153, 129, 0.5)',
    crosshairColor: '#758696',
    gridColor: '#1E222D',
    textColor: '#D1D4DC'
  },
  light: {
    backgroundColor: '#FFFFFF',
    lineColor: '#2196F3',
    candlestickUpColor: '#F23645',
    candlestickDownColor: '#089981',
    volumeUpColor: 'rgba(242, 54, 69, 0.5)',
    volumeDownColor: 'rgba(8, 153, 129, 0.5)',
    crosshairColor: '#758696',
    gridColor: '#E0E3EB',
    textColor: '#131722'
  }
}

// ==================== 响应式状态 ====================

const mainChartContainer = ref<HTMLElement>()
const macdChartContainer = ref<HTMLElement>()
// volumeChartContainer 已移除 - 成交量作为overlay集成到主图

// ==================== 图表设置持久化 ====================

const CHART_PREFS_KEY = 'myquant_chart_prefs'

interface ChartPrefs {
  activeIndicators: string[]
  macdHeight: number
}

const loadChartPrefs = (): ChartPrefs => {
  try {
    const saved = localStorage.getItem(CHART_PREFS_KEY)
    if (saved) return JSON.parse(saved)
  } catch { /* ignore */ }
  return { activeIndicators: [], macdHeight: 120 }
}

const saveChartPrefs = () => {
  try {
    localStorage.setItem(CHART_PREFS_KEY, JSON.stringify({
      activeIndicators: [...activeIndicators.value],
      macdHeight: macdHeight.value,
    }))
  } catch { /* ignore */ }
}

// ==================== 自定义收盘价标签 ====================
const priceLabelEl = ref<HTMLElement | null>(null)
const priceLabelY = ref(0)
const priceLabelText = ref('')
const lastPriceUp = ref(true)

const updatePriceLabel = () => {
  if (!candlestickSeries || !chartApi || chartData.value.length === 0) {
    if (priceLabelEl.value) priceLabelEl.value.style.display = 'none'
    return
  }
  const last = chartData.value[chartData.value.length - 1]
  const close = last.close ?? 0
  const open = last.open ?? 0
  const coord = candlestickSeries.priceToCoordinate(close)
  if (coord === null || priceLabelEl.value === null) return

  priceLabelEl.value.style.display = ''
  priceLabelY.value = coord
  priceLabelText.value = close.toFixed(2)
  lastPriceUp.value = close >= open
}

// 图表实例
let chartApi: ReturnType<typeof createChart> | null = null
let candlestickSeries: CandlestickSeries | null = null
let volumeSeries: HistogramSeries | null = null
let macdChartApi: ReturnType<typeof createChart> | null = null
let macdDifSeries: LineSeries | null = null
let macdDeaSeries: LineSeries | null = null
let macdHistSeries: HistogramSeries | null = null

// 从持久化恢复设置
const savedPrefs = loadChartPrefs()
const macdHeight = ref(savedPrefs.macdHeight)
const MACD_MIN_HEIGHT = 60
const MACD_MAX_HEIGHT = 400
const indicatorSeries = ref<Map<string, LineSeries | HistogramSeries>>(new Map())

// 数据状态
const chartData = ref<KLineDataItem[]>([])
const selectedPeriod = ref(props.period)
const selectedAdjustType = ref<'none' | 'qfq' | 'hfq'>(props.adjustType || 'none')
const activeIndicators = ref<Set<string>>(new Set(savedPrefs.activeIndicators))
const realtimePrice = ref<RealtimePrice | null>(null)
const currentData = ref<KLineDataItem | null>(null)
const crosshairX = ref<number | null>(null)  // 十字光标X坐标（用于图例跟随）
const isLoadingMore = ref(false)  // 是否正在加载更多数据

// 指标窗格
const indicatorPaneRefs = ref<Map<string, HTMLElement>>(new Map())
const indicatorPanes = ref<Array<{ id: string; name: string; height: number }>>([])

// 计算属性
const availablePeriods = computed(() => AVAILABLE_PERIODS)
const availableIndicators = computed(() => AVAILABLE_INDICATORS)
const displayLoading = computed(() => props.loading)

// 复权类型选项
const adjustOptions = [
  { value: 'none' as const, label: '不复权' },
  { value: 'qfq' as const, label: '前复权' },
  { value: 'hfq' as const, label: '后复权' }
]

/**
 * 动态调整主图/成交量边距
 * MACD 显示时压缩成交量区域，让 K 线更紧凑
 */
const updateChartMargins = () => {
  if (!candlestickSeries || !volumeSeries) return

  const hasMacd = activeIndicators.value.has('macd')
  const hasVol = activeIndicators.value.has('vol')

  // 确定K线边距
  let candleMargins: { top: number; bottom: number }
  let volMargins: { top: number; bottom: number } | null = null

  if (hasMacd && hasVol) {
    candleMargins = { top: 0.1, bottom: 0.25 }
    volMargins = { top: 0.8, bottom: 0 }
  } else if (hasMacd && !hasVol) {
    candleMargins = { top: 0.05, bottom: 0.1 }
  } else if (!hasMacd && hasVol) {
    candleMargins = { top: 0.1, bottom: 0.4 }
    volMargins = { top: 0.7, bottom: 0 }
  } else {
    candleMargins = { top: 0.05, bottom: 0.05 }
  }

  candlestickSeries.priceScale().applyOptions({ scaleMargins: candleMargins })

  if (volMargins && volumeSeries) {
    volumeSeries.priceScale().applyOptions({ scaleMargins: volMargins })
  }
}

// ==================== 图表初始化 ====================

const initChart = () => {
  if (!mainChartContainer.value) return

  // 合并颜色配置
  const colors = { ...DEFAULT_COLORS[props.theme], ...props.colors }

  // 创建图表（高度取容器实际高度，而非固定值）
  const containerHeight = mainChartContainer.value.clientHeight || props.mainChartHeight
  chartApi = createChart(mainChartContainer.value, {
    width: mainChartContainer.value.clientWidth,
    height: containerHeight,
    layout: {
      background: { type: 'solid', color: colors.backgroundColor },
      textColor: colors.textColor
    },
    rightPriceScale: {
      visible: true,
      borderColor: colors.gridColor,
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
    timeScale: {
      borderColor: colors.gridColor,
      timeVisible: isIntradayPeriod.value,  // 分钟级显示时间，日线及以上不显示
      secondsVisible: false,
      // 调整右边距，让图表更紧凑
      rightOffset: 5,
      // 增加K线间距，让假期间隙不那么明显
      minBarSpacing: 3,
      barSpacing: 10
    },
    animation: props.animationEnabled
  })

  // 创建K线系列（使用默认right价格轴，按官方文档方式配置）
  candlestickSeries = chartApi.addSeries(CandlestickSeries, {
    upColor: colors.candlestickUpColor,
    downColor: colors.candlestickDownColor,
    borderUpColor: colors.candlestickUpColor,
    borderDownColor: colors.candlestickDownColor,
    wickUpColor: colors.candlestickUpColor,
    wickDownColor: colors.candlestickDownColor,
    lastValueVisible: true,
  })

  // 按官方文档：通过 series.priceScale() 配置主图位置
  candlestickSeries.priceScale().applyOptions({
    scaleMargins: {
      top: 0.1,
      bottom: 0.4  // 留出底部40%给成交量
    }
  })

  // 创建成交量系列（overlay方式 + 强制从0开始缩放）
  volumeSeries = chartApi.addSeries(HistogramSeries, {
    priceLineVisible: false,
    lastValueVisible: false,
    priceFormat: {
      type: 'volume',
    },
    priceScaleId: '',
    // 关键修复：强制价格轴从0开始，防止底部被裁剪导致柱状图平坦
    autoscaleProvider: (callback: (info: { priceRange: { minValue: number; maxValue: number } } | null) => void) => {
      const data = chartData.value
      if (!data || data.length === 0) {
        callback(null)
        return
      }
      const vols = data.map((d: any) => d.volume || 0).filter((v: number) => v > 0)
      if (vols.length === 0) {
        callback(null)
        return
      }
      const maxVol = Math.max(...vols)
      callback({
        priceRange: {
          minValue: 0,
          maxValue: maxVol * 1.05  // 留5%顶部空间
        }
      })
    }
  })

  volumeSeries.priceScale().applyOptions({
    scaleMargins: {
      top: 0.7,
      bottom: 0
    }
  })

  console.log('[Volume] 成交量系列已创建（overlay + autoscaleProvider，强制从0开始）')

  // 根据当前指标状态设置主图/成交量边距
  updateChartMargins()

  // 监听十字光标移动
  chartApi.subscribeCrosshairMove((param) => {
    if (param.time) {
      const dataPoint = chartData.value.find(d => d.time === param.time)
      currentData.value = dataPoint || null
      // 记录光标X坐标，用于图例跟随
      if (param.point) {
        crosshairX.value = param.point.x
      }
    } else {
      // 鼠标离开图表时，图例回到默认位置
      crosshairX.value = null
    }
    emit('crosshairMove', param)
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
    updatePriceLabel()
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

    // 加载足够多的数据，用户可滚动查看历史
    const count = DEFAULT_KLINE_CONFIG.defaultCount[apiPeriod] || 500
    const response: KlineResponse = await getSeamlessKline(
      props.symbol,
      apiPeriod as any,
      count,
      selectedAdjustType.value
    )

    if (response.code === 200 && response.data && response.data.length > 0) {
      const elapsedMs = response.elapsed_ms || 0
      const dataSource = response.data_source || 'seamless_v5'

      console.log(
        `[TradingViewKLine] ✅ Loaded ${response.data.length} candles ` +
        `from ${dataSource} in ${elapsedMs}ms`
      )

      // ⭐ 使用无缝K线数据转换函数
      const mappedData = transformKlineData(response.data, true, period)

      // 数据排序：按时间升序排列（从旧到新）
      chartData.value = mappedData.sort((a, b) => (a.time as number) - (b.time as number))

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
    const colors = { ...DEFAULT_COLORS[props.theme], ...props.colors }

    // 确保volume字段存在
    const volumeData = chartData.value.map((d: any) => {
      const vol = typeof d.volume === 'number' ? d.volume : 0
      return {
        time: d.time,
        value: vol,
        color: (d.close || 0) >= (d.open || 0) ? colors.volumeUpColor : colors.volumeDownColor
      }
    })

    // 统计volume分布
    const volumes = volumeData.map(d => d.value)
    const sortedVolumes = [...volumes].sort((a, b) => a - b)
    const minVolume = sortedVolumes[0]
    const maxVolume = sortedVolumes[sortedVolumes.length - 1]
    const medianVolume = sortedVolumes[Math.floor(sortedVolumes.length / 2)]

    console.log('[Volume] 成交量分布:', {
      最小值: minVolume,
      最大值: maxVolume,
      中位数: medianVolume,
      前3个值: volumes.slice(0, 3),
      后3个值: volumes.slice(-3)
    })

    volumeSeries.setData(volumeData)
  } else {
    console.error('[Volume] volumeSeries为null!')
  }

  // 更新指标
  await updateIndicators()
  updatePriceLabel()

  emit('dataUpdate', chartData.value)
}

/**
 * 设置图表可见范围为最后 N 根K线
 * 使用 setVisibleLogicalRange 避免与周期切换冲突
 */
const setVisibleToLastBars = (count: number = 120) => {
  if (!chartApi || !chartData.value || chartData.value.length === 0) return

  const dataLen = chartData.value.length
  if (dataLen <= count) {
    // 数据量少于目标，直接适配全部
    chartApi.timeScale().fitContent()
    return
  }

  // 计算逻辑范围：最后 count 根K线
  const fromIndex = dataLen - count
  const toIndex = dataLen - 1
  try {
    chartApi.timeScale().setVisibleLogicalRange({
      from: fromIndex,
      to: toIndex
    })
  } catch (e) {
    // 降级到 fitContent
    chartApi.timeScale().fitContent()
  }
}

/**
 * 计算 SMA (简单移动平均线)
 */
const calculateSMA = (
  data: Array<{ time: number; close: number }>,
  period: number
): Array<{ time: number; value: number }> => {
  const result: Array<{ time: number; value: number }> = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) continue
    let sum = 0
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close
    }
    result.push({ time: data[i].time, value: parseFloat((sum / period).toFixed(2)) })
  }
  return result
}

/**
 * 计算 EMA (指数移动平均线)
 */
const calculateEMA = (
  data: Array<{ time: number; close: number }>,
  period: number
): Array<{ time: number; value: number }> => {
  const result: Array<{ time: number; value: number }> = []
  const k = 2 / (period + 1)

  for (let i = 0; i < data.length; i++) {
    if (i === 0) {
      result.push({ time: data[i].time, value: data[i].close })
      continue
    }
    const prev = result[result.length - 1].value
    const ema = data[i].close * k + prev * (1 - k)
    result.push({ time: data[i].time, value: parseFloat(ema.toFixed(2)) })
  }
  return result
}

/**
 * 计算 BOLL (布林带) - 返回 upper, middle, lower 三条线
 */
const calculateBOLL = (
  data: Array<{ time: number; close: number }>,
  period: number = 20,
  stdMultiplier: number = 2
): { upper: Array<{ time: number; value: number }>; middle: Array<{ time: number; value: number }>; lower: Array<{ time: number; value: number }> } => {
  const sma = calculateSMA(data, period)
  const upper: Array<{ time: number; value: number }> = []
  const middle: Array<{ time: number; value: number }> = []
  const lower: Array<{ time: number; value: number }> = []

  // sma 的第一条数据对应的原始数据索引 = period - 1
  for (let i = 0; i < sma.length; i++) {
    const dataIdx = i + period - 1
    let sumSq = 0
    for (let j = 0; j < period; j++) {
      const diff = data[dataIdx - j].close - sma[i].value
      sumSq += diff * diff
    }
    const std = Math.sqrt(sumSq / period)
    upper.push({ time: sma[i].time, value: parseFloat((sma[i].value + stdMultiplier * std).toFixed(2)) })
    middle.push({ time: sma[i].time, value: sma[i].value })
    lower.push({ time: sma[i].time, value: parseFloat((sma[i].value - stdMultiplier * std).toFixed(2)) })
  }

  return { upper, middle, lower }
}

/**
 * 计算 MACD
 * DIF = EMA(close, 12) - EMA(close, 26)
 * DEA = EMA(DIF, 9)
 * MACD柱 = (DIF - DEA) * 2
 */
const calculateMACD = (
  data: Array<{ time: number; close: number }>
): { dif: Array<{ time: number; value: number }>; dea: Array<{ time: number; value: number }>; histogram: Array<{ time: number; value: number; color: string }> } => {
  if (data.length < 26) return { dif: [], dea: [], histogram: [] }

  // 计算 DIF (12日EMA - 26日EMA)
  const ema12 = calculateEMA(data, 12)
  const ema26 = calculateEMA(data, 26)

  const dif: Array<{ time: number; value: number }> = []
  for (let i = 0; i < ema12.length && i < ema26.length; i++) {
    if (ema12[i].time !== ema26[i].time) continue
    const val = parseFloat((ema12[i].value - ema26[i].value).toFixed(4))
    dif.push({ time: ema12[i].time, value: val })
  }

  if (dif.length === 0) return { dif: [], dea: [], histogram: [] }

  // 计算 DEA (9日EMA of DIF)
  const dea: Array<{ time: number; value: number }> = []
  const k = 2 / (9 + 1)
  for (let i = 0; i < dif.length; i++) {
    if (i === 0) {
      dea.push({ time: dif[i].time, value: dif[i].value })
    } else {
      const val = parseFloat((dif[i].value * k + dea[i - 1].value * (1 - k)).toFixed(4))
      dea.push({ time: dif[i].time, value: val })
    }
  }

  // 计算 MACD 柱状图
  const histogram: Array<{ time: number; value: number; color: string }> = []
  for (let i = 0; i < dif.length; i++) {
    const val = parseFloat(((dif[i].value - dea[i].value) * 2).toFixed(4))
    histogram.push({
      time: dif[i].time,
      value: val,
      color: val >= 0 ? 'rgba(242, 54, 69, 0.7)' : 'rgba(8, 153, 129, 0.7)'
    })
  }

  return { dif, dea, histogram }
}

// 将 hex 颜色转为半透明 rgba
const updateIndicators = async () => {
  const closes = chartData.value.map((d: any) => ({
    time: d.time as number,
    close: (d.close || 0) as number
  }))

  if (closes.length === 0) return

  for (const indicatorKey of activeIndicators.value) {
    const indicatorConfig = AVAILABLE_INDICATORS.find(i => i.key === indicatorKey)
    if (!indicatorConfig) continue

    if (indicatorConfig.type === 'overlay') {
      // MA 叠加指标
      let indicatorData: Array<{ time: number; value: number }> = []
      const maMatch = indicatorKey.match(/^ma(\d+)$/)
      if (maMatch) {
        const period = parseInt(maMatch[1])
        indicatorData = calculateSMA(closes, period)
      }
      if (indicatorData.length === 0) continue

      if (!indicatorSeries.value.has(indicatorKey)) {
        const series = chartApi!.addSeries(LineSeries, {
          color: indicatorConfig.color,
          lineWidth: 1,
          crosshairMarkerVisible: false,
          priceLineVisible: false,
          lastValueVisible: false,
          priceScaleId: 'right',
        })
        indicatorSeries.value.set(indicatorKey, series)
      }

      const series = indicatorSeries.value.get(indicatorKey) as LineSeries
      series.setData(indicatorData)

    } else if (indicatorConfig.type === 'separate' && indicatorKey === 'macd') {
      // MACD 独立窗格 - 使用独立图表实例
      const macd = calculateMACD(closes)
      if (macd.dif.length === 0) continue

      // 确保 MACD 图表已创建
      if (!macdChartApi && macdChartContainer.value) {
        const colors = { ...DEFAULT_COLORS[props.theme], ...props.colors }
        macdChartApi = createChart(macdChartContainer.value, {
          width: macdChartContainer.value.clientWidth,
          height: macdHeight.value,
          layout: {
            background: { type: 'solid', color: colors.backgroundColor },
            textColor: colors.textColor
          },
          grid: {
            vertLines: { color: colors.gridColor },
            horzLines: { color: colors.gridColor }
          },
          rightPriceScale: {
            borderColor: colors.gridColor,
            visible: true,
          },
          timeScale: {
            visible: false,
          },
          crosshair: {
            mode: 1,
            vertLine: { color: colors.crosshairColor, width: 1, style: 3 },
            horzLine: { color: colors.crosshairColor, width: 1, style: 3 },
          },
          animation: false,
        })

        // DIF 线
        macdDifSeries = macdChartApi.addSeries(LineSeries, {
          color: '#2196F3',
          lineWidth: 1,
          crosshairMarkerVisible: false,
          title: 'DIF',
          priceLineVisible: false,
          lastValueVisible: true,
        })

        // DEA 线
        macdDeaSeries = macdChartApi.addSeries(LineSeries, {
          color: '#FF9800',
          lineWidth: 1,
          crosshairMarkerVisible: false,
          title: 'DEA',
          priceLineVisible: false,
          lastValueVisible: true,
        })

        // MACD 柱状图（半透明）
        macdHistSeries = macdChartApi.addSeries(HistogramSeries, {
          priceLineVisible: false,
          lastValueVisible: false,
        })

        // 双向同步时间轴：主图 ↔ MACD
        let syncing = false
        chartApi?.timeScale().subscribeVisibleLogicalRangeChange((range) => {
          if (syncing || !range || !macdChartApi) return
          syncing = true
          macdChartApi.timeScale().setVisibleLogicalRange(range)
          syncing = false
        })
        macdChartApi.timeScale().subscribeVisibleLogicalRangeChange((range) => {
          if (syncing || !range || !chartApi) return
          syncing = true
          chartApi.timeScale().setVisibleLogicalRange(range)
          syncing = false
        })
      }

      // 更新 MACD 数据
      if (macdChartApi && macdDifSeries && macdDeaSeries && macdHistSeries) {
        macdDifSeries.setData(macd.dif)
        macdDeaSeries.setData(macd.dea)
        macdHistSeries.setData(
          macd.histogram.map(h => ({ time: h.time, value: h.value, color: h.color }))
        )
      }
    }
  }

  // overlay 方案不影响 right 轴，无需恢复
}

// ==================== 指标管理 ====================

const handleIndicatorToggle = (indicatorKey: string) => {
  if (activeIndicators.value.has(indicatorKey)) {
    activeIndicators.value.delete(indicatorKey)
    removeIndicatorSeries(indicatorKey)
    // VOL 隐藏成交量 + 调整边距
    if (indicatorKey === 'vol') {
      if (volumeSeries) {
        volumeSeries.applyOptions({ visible: false })
      }
      nextTick(() => updateChartMargins())
    }
    // MACD 切换时动态调整主图/成交量边距
    if (indicatorKey === 'macd') {
      nextTick(() => updateChartMargins())
    }
  } else {
    activeIndicators.value.add(indicatorKey)
    // v-if 条件渲染需要等 DOM 更新后再创建指标
    nextTick(() => {
      updateIndicators()
      // VOL 显示成交量 + 调整边距
      if (indicatorKey === 'vol') {
        if (volumeSeries) {
          volumeSeries.applyOptions({ visible: true })
        }
        updateChartMargins()
      }
      if (indicatorKey === 'macd') {
        updateChartMargins()
      }
    })
  }

  saveChartPrefs()
  emit('indicatorToggle', indicatorKey, activeIndicators.value.has(indicatorKey))
}

const removeIndicatorSeries = (indicatorKey: string) => {
  // MACD 有独立图表实例，需要销毁
  if (indicatorKey === 'macd') {
    // 清理主图上可能残留的 MACD 系列（兼容旧逻辑）
    for (const subKey of ['macd_dif', 'macd_dea', 'macd_hist']) {
      const series = indicatorSeries.value.get(subKey)
      if (series) {
        chartApi?.removeSeries(series)
        indicatorSeries.value.delete(subKey)
      }
    }
    // 销毁 MACD 独立图表
    if (macdChartApi) {
      macdChartApi.remove()
      macdChartApi = null
      macdDifSeries = null
      macdDeaSeries = null
      macdHistSeries = null
    }
    return
  }

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

  // 更新时间轴显示设置（日线及以上不显示时间）
  if (chartApi) {
    const isIntraday = ['1m', '5m', '15m', '30m', '1h', '60m', '1min'].includes(period)
    chartApi.timeScale().applyOptions({
      timeVisible: isIntraday
    })
  }

  await loadData(period)
  emit('periodChange', period)

  // 切换周期后显示最后120根K线
  nextTick(() => {
    setVisibleToLastBars(120)
  })
}

// 切换复权类型
const handleAdjustTypeChange = async (adjustType: 'none' | 'qfq' | 'hfq') => {
  if (adjustType === selectedAdjustType.value) return

  selectedAdjustType.value = adjustType
  await loadData(selectedPeriod.value)

  // 切换复权类型后显示最后120根K线
  nextTick(() => {
    setVisibleToLastBars(120)
  })
}

// ==================== 工具方法 ====================

const resetChart = () => {
  if (!chartApi) return
  setVisibleToLastBars(120)
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

  // ResizeObserver 监听容器尺寸变化，确保图表始终填满容器
  resizeObserver = new ResizeObserver(() => {
    if (mainChartContainer.value && chartApi) {
      chartApi.applyOptions({
        width: mainChartContainer.value.clientWidth,
        height: mainChartContainer.value.clientHeight,
      })
    }
    if (macdChartContainer.value && macdChartApi) {
      macdChartApi.applyOptions({
        width: macdChartContainer.value.clientWidth,
        height: macdChartContainer.value.clientHeight,
      })
    }
  })
  if (mainChartContainer.value) {
    resizeObserver.observe(mainChartContainer.value)
  }

  // 等待图表完全渲染后再加载数据
  await new Promise(resolve => setTimeout(resolve, 100))
  await loadData(props.period)
  setVisibleToLastBars(120)

  // 恢复上次保存的指标
  if (activeIndicators.value.size > 0) {
    await nextTick()
    // VOL 可见性由 initChart 时的默认状态决定，这里同步
    if (volumeSeries) {
      volumeSeries.applyOptions({ visible: activeIndicators.value.has('vol') })
    }
    updateIndicators()
    updateChartMargins()
  }

  startRealtimeUpdate()

  // 响应窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  stopRealtimeUpdate()

  // 清理拖拽事件
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeEnd)

  // 清理图表
  if (macdChartApi) {
    macdChartApi.remove()
    macdChartApi = null
  }
  if (chartApi) {
    chartApi.remove()
    chartApi = null
  }
})

// ==================== 监听器 ====================

// ==================== MACD 窗格拖拽调整大小 ====================

let isDragging = false
let dragStartY = 0
let dragStartHeight = 0
let dragStartMainHeight = 0

const onResizeStart = (e: MouseEvent) => {
  isDragging = true
  dragStartY = e.clientY
  dragStartHeight = macdHeight.value
  dragStartMainHeight = mainChartContainer.value?.clientHeight || 0

  // 防止文本选中
  document.body.style.cursor = 'ns-resize'
  document.body.style.userSelect = 'none'

  document.addEventListener('mousemove', onResizeMove)
  document.addEventListener('mouseup', onResizeEnd)
}

const onResizeMove = (e: MouseEvent) => {
  if (!isDragging) return

  const deltaY = dragStartY - e.clientY
  const newMacdHeight = Math.max(MACD_MIN_HEIGHT, Math.min(MACD_MAX_HEIGHT, dragStartHeight + deltaY))

  macdHeight.value = newMacdHeight
  // 图表高度由 ResizeObserver 自动同步，不需要手动 applyOptions
}

const onResizeEnd = () => {
  isDragging = false
  document.body.style.cursor = ''
  document.body.style.userSelect = ''

  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeEnd)

  saveChartPrefs()
}

// ==================== 窗口大小响应 ====================

// ResizeObserver 监听容器尺寸变化，同步图表尺寸
let resizeObserver: ResizeObserver | null = null

const handleResize = () => {
  if (mainChartContainer.value && chartApi) {
    chartApi.applyOptions({
      width: mainChartContainer.value.clientWidth,
      height: mainChartContainer.value.clientHeight,
    })
  }
  if (macdChartContainer.value && macdChartApi) {
    macdChartApi.applyOptions({
      width: macdChartContainer.value.clientWidth,
      height: macdChartContainer.value.clientHeight,
    })
  }
}

// 监听symbol变化 - 确保切换股票后自动适配视图
watch(() => props.symbol, async (newSymbol, oldSymbol) => {
  if (newSymbol !== oldSymbol) {
    console.log(`[TradingViewKLine] Symbol changed from ${oldSymbol} to ${newSymbol}`)

    // 确保图表已初始化
    if (!chartApi || !candlestickSeries) {
      console.warn('[TradingViewKLine] Chart not initialized, skipping data update')
      return
    }

    // 清空现有数据，避免时间轴混乱
    candlestickSeries.setData([])
    if (volumeSeries) {
      volumeSeries.setData([])
    }
    // 清空指标数据
    for (const [key, series] of indicatorSeries.value) {
      if (series) {
        series.setData([])
      }
    }
    chartData.value = []

    // 等待图表处理完成后再加载新数据
    await new Promise(resolve => setTimeout(resolve, 50))

    await loadData(selectedPeriod.value)

    // 切换股票后显示最后120根K线
    chartApi.timeScale().scrollToPosition(0, false)
    setVisibleToLastBars(120)
    console.log('[TradingViewKLine] Chart fitted after symbol change')
  }
})

// 监听周期变化
watch(() => props.period, async (newPeriod) => {
  if (newPeriod && newPeriod !== selectedPeriod.value) {
    selectedPeriod.value = newPeriod

    // 更新时间轴显示设置
    if (chartApi) {
      const isIntraday = ['1m', '5m', '15m', '30m', '1h', '60m', '1min'].includes(newPeriod)
      chartApi.timeScale().applyOptions({
        timeVisible: isIntraday
      })
    }

    await loadData(newPeriod)
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
  display: flex;
  flex-direction: column;
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
  color: #F23645;
}

.down {
  color: #00A854;
}

/* 周期标签 */
.period-tabs,
.adjust-tabs,
.indicator-btns {
  display: flex;
  gap: 4px;
}

.adjust-tabs {
  margin-left: 12px;
  padding-left: 12px;
  border-left: 1px solid var(--tvk-border-color, #363C4E);
}

.period-btn,
.adjust-btn,
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
.adjust-btn:hover,
.indicator-btn:hover {
  background-color: var(--tvk-hover-bg, #2A2E39);
}

.period-btn.active,
.adjust-btn.active,
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
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.tvk-main-chart-wrapper {
  flex: 1;
  min-height: 0;
  position: relative;
}

.tvk-main-chart {
  width: 100%;
  height: 100%;
  position: relative;
}

.tvk-price-label {
  position: absolute;
  right: 0;
  z-index: 10;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 2px 0 0 2px;
  transform: translateY(-50%);
  pointer-events: none;
  white-space: nowrap;
}

.tvk-price-up {
  background: rgba(242, 54, 69, 0.85);
  color: #fff;
}

.tvk-price-down {
  background: rgba(8, 153, 129, 0.85);
  color: #fff;
}

.tvk-indicator-pane {
  width: 100%;
}

/* 拖拽分隔条 */
.tvk-resize-handle {
  width: 100%;
  height: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: ns-resize;
  background: transparent;
  position: relative;
  z-index: 5;
}

.tvk-resize-handle:hover .resize-handle-bar,
.tvk-resize-handle:active .resize-handle-bar {
  background-color: var(--tvk-active-bg, #2196F3);
  height: 3px;
}

.resize-handle-bar {
  width: 60px;
  height: 2px;
  border-radius: 1px;
  background-color: var(--tvk-border-color, #363C4E);
  transition: background-color 0.15s, height 0.15s;
  pointer-events: none;
}

/* MACD 独立窗格 */
.tvk-macd-pane {
  width: 100%;
  border-top: 1px solid var(--tvk-grid-color, #293040);
  position: relative;
}

.macd-pane-label {
  position: absolute;
  top: 4px;
  left: 12px;
  font-size: 10px;
  color: rgba(209, 212, 220, 0.5);
  z-index: 1;
  pointer-events: none;
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
  transition: left 0.08s ease-out;
  white-space: nowrap;
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
