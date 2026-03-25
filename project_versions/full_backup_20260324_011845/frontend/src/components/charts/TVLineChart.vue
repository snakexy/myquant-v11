<template>
  <div class="tv-line-chart" ref="containerRef">
    <!-- 工具栏 -->
    <div class="tv-toolbar" v-if="showToolbar">
      <div class="toolbar-left">
        <svg class="chart-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
        </svg>
        <span class="chart-title">{{ title }}</span>
      </div>
      <div class="toolbar-center period-buttons" v-if="showPeriodSelector">
        <button
          v-for="period in periods"
          :key="period.value"
          :class="['period-btn', { active: selectedPeriod === period.value }]"
          @click="selectPeriod(period.value)"
        >
          {{ period.label }}
        </button>
      </div>
      <div class="toolbar-right">
        <div class="legend" v-if="showLegend">
          <div class="legend-item strategy">
            <span class="legend-color" :style="{ background: strategyColor }"></span>
            <span class="legend-text">{{ strategyLabelText }}</span>
          </div>
          <div
            v-for="(series, idx) in extraSeries"
            :key="'extra-' + idx"
            class="legend-item"
          >
            <span class="legend-color" :style="{ background: series.color }"></span>
            <span class="legend-text">{{ series.label }}</span>
          </div>
          <div class="legend-item benchmark" v-if="hasBenchmark">
            <span class="legend-color dashed" :style="{ background: benchmarkColor }"></span>
            <span class="legend-text">{{ benchmarkLabelText }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="tv-chart-area" ref="chartAreaRef"></div>

    <!-- 高度调节手柄 -->
    <div
      v-if="resizable"
      class="resize-handle"
      @mousedown="startResize"
    ></div>

    <!-- 自定义tooltip -->
    <div class="tv-tooltip" v-if="tooltipVisible" :style="tooltipStyle">
      <div class="tooltip-date">{{ tooltipData.date }}</div>
      <div class="tooltip-row strategy">
        <span class="tooltip-label">{{ strategyLabelText }}</span>
        <span class="tooltip-value">{{ tooltipData.strategyValue?.toFixed(4) }}</span>
        <span :class="['tooltip-change', tooltipData.strategyChange >= 0 ? 'positive' : 'negative']">
          {{ formatChange(tooltipData.strategyChange) }}
        </span>
      </div>
      <div class="tooltip-row benchmark" v-if="hasBenchmark && tooltipData.benchmarkValue">
        <span class="tooltip-label">{{ benchmarkLabelText }}</span>
        <span class="tooltip-value">{{ tooltipData.benchmarkValue?.toFixed(4) }}</span>
        <span :class="['tooltip-change', tooltipData.benchmarkChange >= 0 ? 'positive' : 'negative']">
          {{ formatChange(tooltipData.benchmarkChange) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { createChart, LineSeries, type Time, type IChartApi, type ISeriesApi, ColorType } from 'lightweight-charts'

// 导出Time类型供外部使用
export type { Time } from 'lightweight-charts'

interface DataPoint {
  time: Time
  value: number
}

// 多系列数据
interface SeriesData {
  data: DataPoint[]
  label: string
  color: string
}

interface Props {
  // 标题
  title?: string

  // 数据
  strategyData?: DataPoint[]     // 策略净值数据
  benchmarkData?: DataPoint[]   // 基准净值数据
  extraSeries?: SeriesData[]     // 额外的数据系列（支持多策略对比）
  dates?: string[]              // 日期标签

  // 标签
  strategyLabel?: string
  benchmarkLabel?: string

  // 颜色
  strategyColor?: string
  benchmarkColor?: string

  // 功能开关
  showToolbar?: boolean
  showPeriodSelector?: boolean
  showLegend?: boolean
  resizable?: boolean           // 是否可调节高度

  // 图表配置
  height?: number
  darkMode?: boolean
  locale?: string               // 语言设置 'zh' 或 'en'
  customPeriods?: { label: string; value: string }[]  // 自定义周期选项
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Equity Curve',
  strategyData: () => [],
  benchmarkData: () => [],
  extraSeries: () => [],
  dates: () => [],
  strategyLabel: 'Strategy',
  benchmarkLabel: 'Benchmark',
  strategyColor: '#ef5350',
  benchmarkColor: '#787b86',
  showToolbar: true,
  showPeriodSelector: false,
  showLegend: true,
  resizable: false,
  height: 300,
  darkMode: true,
  locale: 'zh',
  customPeriods: () => []
})

const chartHeight = ref(props.height || 300)

// 强制响应式标签
const strategyLabelText = computed(() => props.strategyLabel || 'Strategy')
const benchmarkLabelText = computed(() => props.benchmarkLabel || 'Benchmark')

// Refs
const containerRef = ref<HTMLElement>()
const chartAreaRef = ref<HTMLElement>()
let chart: IChartApi | null = null
let strategySeries: ISeriesApi<'Line'> | null = null
let benchmarkSeries: ISeriesApi<'Line'> | null = null
let extraSeriesInstances: ISeriesApi<'Line'>[] = []

// 状态
const selectedPeriod = ref('all')
const defaultPeriods = [
  { label: '1W', value: '1w' },
  { label: '1M', value: '1m' },
  { label: '3M', value: '3m' },
  { label: '6M', value: '6m' },
  { label: '1Y', value: '1y' },
  { label: 'All', value: 'all' }
]
const periods = computed(() => props.customPeriods?.length ? props.customPeriods : defaultPeriods)

// 根据周期过滤数据
const filteredStrategyData = computed(() => {
  const data = props.strategyData
  if (!data.length) return []
  if (selectedPeriod.value === 'all') return data

  // 获取数据中最后一个日期作为基准
  const lastDataPoint = data[data.length - 1]
  const lastDate = typeof lastDataPoint.time === 'string'
    ? new Date(lastDataPoint.time)
    : new Date()

  let cutoffDate: Date

  switch (selectedPeriod.value) {
    case '1h':
      // 小时 - 显示最近1天数据
      cutoffDate = new Date(lastDate.getTime() - 1 * 24 * 60 * 60 * 1000)
      break
    case '1d':
      // 日线 - 显示最近1天数据
      cutoffDate = new Date(lastDate.getTime() - 1 * 24 * 60 * 60 * 1000)
      break
    case '1w':
      cutoffDate = new Date(lastDate.getTime() - 7 * 24 * 60 * 60 * 1000)
      break
    case '1m':
      cutoffDate = new Date(lastDate.getTime() - 30 * 24 * 60 * 60 * 1000)
      break
    case '3m':
      cutoffDate = new Date(lastDate.getTime() - 90 * 24 * 60 * 60 * 1000)
      break
    case '6m':
      cutoffDate = new Date(lastDate.getTime() - 180 * 24 * 60 * 60 * 1000)
      break
    case '1y':
      cutoffDate = new Date(lastDate.getTime() - 365 * 24 * 60 * 60 * 1000)
      break
    default:
      return data
  }

  return data.filter(d => {
    const time = d.time
    if (typeof time === 'string') {
      return new Date(time) >= cutoffDate
    }
    return true
  })
})

const filteredBenchmarkData = computed(() => {
  const data = props.benchmarkData
  if (!data.length) return []
  if (selectedPeriod.value === 'all') return data

  // 获取数据中最后一个日期作为基准
  const lastDataPoint = data[data.length - 1]
  const lastDate = typeof lastDataPoint.time === 'string'
    ? new Date(lastDataPoint.time)
    : new Date()

  let cutoffDate: Date

  switch (selectedPeriod.value) {
    case '1h':
      // 小时 - 显示最近1天数据
      cutoffDate = new Date(lastDate.getTime() - 1 * 24 * 60 * 60 * 1000)
      break
    case '1d':
      // 日线 - 显示最近1天数据
      cutoffDate = new Date(lastDate.getTime() - 1 * 24 * 60 * 60 * 1000)
      break
    case '1w':
      cutoffDate = new Date(lastDate.getTime() - 7 * 24 * 60 * 60 * 1000)
      break
    case '1m':
      cutoffDate = new Date(lastDate.getTime() - 30 * 24 * 60 * 60 * 1000)
      break
    case '3m':
      cutoffDate = new Date(lastDate.getTime() - 90 * 24 * 60 * 60 * 1000)
      break
    case '6m':
      cutoffDate = new Date(lastDate.getTime() - 180 * 24 * 60 * 60 * 1000)
      break
    case '1y':
      cutoffDate = new Date(lastDate.getTime() - 365 * 24 * 60 * 60 * 1000)
      break
    default:
      return data
  }

  return data.filter(d => {
    const time = d.time
    if (typeof time === 'string') {
      return new Date(time) >= cutoffDate
    }
    return true
  })
})

// Tooltip
const tooltipVisible = ref(false)
const tooltipData = ref<any>({
  date: '',
  strategyValue: 0,
  strategyChange: 0,
  benchmarkValue: 0,
  benchmarkChange: 0
})
const tooltipPosition = ref({ x: 0, y: 0 })

const hasBenchmark = computed(() => props.benchmarkData.length > 0)

// Tooltip样式
const tooltipStyle = computed(() => {
  let x = tooltipPosition.value.x + 15
  let y = tooltipPosition.value.y - 60

  // 边界检测
  const containerWidth = containerRef.value?.clientWidth || 400
  if (x + 180 > containerWidth) {
    x = tooltipPosition.value.x - 190
  }
  if (y < 10) {
    y = tooltipPosition.value.y + 15
  }

  return {
    left: x + 'px',
    top: y + 'px'
  }
})

// 格式化收益率变化
const formatChange = (value: number | undefined): string => {
  if (value === undefined || value === null) return '--'
  const pct = value * 100
  return `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`
}

// 初始化图表
const initChart = () => {
  if (!chartAreaRef.value) {
    console.warn('TVLineChart: chartAreaRef is null')
    return
  }

  const containerWidth = chartAreaRef.value.clientWidth || 600
  const containerHeight = chartAreaRef.value.clientHeight || (chartHeight.value - 45)

  console.log('TVLineChart init:', { containerWidth, containerHeight, dataLength: props.strategyData.length })

  // 清除旧图表
  if (chart) {
    chart.remove()
    chart = null
    strategySeries = null
    benchmarkSeries = null
    extraSeriesInstances = []
  }

  const bgColor = props.darkMode ? '#131722' : '#ffffff'
  const textColor = props.darkMode ? '#d1d4dc' : '#333333'
  const gridColor = props.darkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'

  // 根据语言设置日期格式
  const chartLocale = props.locale === 'zh' ? 'zh-CN' : 'en-US'
  const dateFormat = props.locale === 'zh' ? 'yyyy年M月' : 'MMM yyyy'

  chart = createChart(chartAreaRef.value, {
    width: containerWidth,
    height: containerHeight,
    layout: {
      background: { type: ColorType.Solid, color: bgColor },
      textColor: textColor
    },
    grid: {
      vertLines: { color: gridColor, style: 1 },
      horzLines: { color: gridColor, style: 1 }
    },
    rightPriceScale: {
      borderColor: props.darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
      scaleMargins: { top: 0.1, bottom: 0.2 }
    },
    timeScale: {
      borderColor: props.darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
      timeVisible: true,
      secondsVisible: false
    },
    localization: {
      locale: chartLocale,
      dateFormat: dateFormat
    },
    crosshair: {
      mode: 1,
      vertLine: {
        color: props.darkMode ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
        width: 1,
        style: 2,
        labelBackgroundColor: props.darkMode ? '#2a2e39' : '#e0e0e0'
      },
      horzLine: {
        color: props.darkMode ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)',
        width: 1,
        style: 2,
        labelBackgroundColor: props.darkMode ? '#2a2e39' : '#e0e0e0'
      }
    },
    handleScale: {
      axisPressedMouseMove: true
    },
    handleScroll: {
      mouseWheel: true,
      pressedMouseMove: true,
      horzTouchDrag: true,
      vertTouchDrag: true
    }
  } as any)

  // 添加策略线
  strategySeries = chart.addSeries(LineSeries, {
    color: props.strategyColor,
    lineWidth: 2,
    priceFormat: {
      type: 'custom',
      formatter: (price: number) => price.toFixed(4)
    },
    lastValueVisible: false,
    priceLineVisible: false
  })

  // 添加基准线
  if (hasBenchmark.value) {
    benchmarkSeries = chart.addSeries(LineSeries, {
      color: props.benchmarkColor,
      lineWidth: 1,
      lineStyle: 2, // 虚线
      priceFormat: {
        type: 'custom',
        formatter: (price: number) => price.toFixed(4)
      },
      lastValueVisible: false,
      priceLineVisible: false
    })
  }

  // 添加额外系列（支持多策略对比）
  extraSeriesInstances = []
  if (props.extraSeries && props.extraSeries.length > 0) {
    for (const series of props.extraSeries) {
      const extra = chart.addSeries(LineSeries, {
        color: series.color,
        lineWidth: 2,
        priceFormat: {
          type: 'custom',
          formatter: (price: number) => price.toFixed(4)
        },
        lastValueVisible: false,
        priceLineVisible: false
      })
      extraSeriesInstances.push(extra)
    }
  }

  // 设置数据（使用过滤后的数据）
  if (filteredStrategyData.value.length > 0) {
    strategySeries.setData(filteredStrategyData.value)
  }
  if (hasBenchmark.value && filteredBenchmarkData.value.length > 0 && benchmarkSeries) {
    benchmarkSeries.setData(filteredBenchmarkData.value)
  }

  // 设置额外系列数据
  if (props.extraSeries && props.extraSeries.length > 0) {
    for (let i = 0; i < props.extraSeries.length; i++) {
      const series = props.extraSeries[i]
      if (extraSeriesInstances[i] && series.data.length > 0) {
        extraSeriesInstances[i].setData(series.data)
      }
    }
  }

  // 自动缩放
  chart.timeScale().fitContent()

  // 十字线移动事件
  chart.subscribeCrosshairMove((param) => {
    if (!param.point || !param.time) {
      tooltipVisible.value = false
      return
    }

    const time = param.time as string
    const dataIndex = filteredStrategyData.value.findIndex(d => d.time === time)

    if (dataIndex >= 0) {
      const strategyValue = filteredStrategyData.value[dataIndex]?.value || 0
      const firstValue = filteredStrategyData.value[0]?.value || 1

      let benchmarkValue: number | undefined
      let benchmarkChange: number | undefined
      if (hasBenchmark.value && filteredBenchmarkData.value[dataIndex]) {
        benchmarkValue = filteredBenchmarkData.value[dataIndex].value
        benchmarkChange = benchmarkValue - (props.benchmarkData[0]?.value || 1)
      }

      tooltipData.value = {
        date: props.dates[dataIndex] || time,
        strategyValue: strategyValue,
        strategyChange: strategyValue - firstValue,
        benchmarkValue: benchmarkValue,
        benchmarkChange: benchmarkChange
      }

      tooltipPosition.value = { x: param.point.x, y: param.point.y }
      tooltipVisible.value = true
    }
  })

  // 处理窗口大小变化
  const resizeObserver = new ResizeObserver(() => {
    if (chart && chartAreaRef.value) {
      chart.applyOptions({
        width: chartAreaRef.value.clientWidth,
        height: chartAreaRef.value.clientHeight
      })
    }
  })
  resizeObserver.observe(chartAreaRef.value)
}

// 周期选择
const selectPeriod = (period: string) => {
  selectedPeriod.value = period
  // TODO: 根据周期筛选数据
}

// 高度调节功能
const isResizing = ref(false)
const startY = ref(0)
const startHeight = ref(0)

const startResize = (e: MouseEvent) => {
  isResizing.value = true
  startY.value = e.clientY
  startHeight.value = chartHeight.value || 300
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
}

const handleResize = (e: MouseEvent) => {
  if (!isResizing.value) return
  const delta = e.clientY - startY.value
  const newHeight = Math.max(150, startHeight.value + delta)
  chartHeight.value = newHeight
  nextTick(() => {
    if (chart) {
      initChart()
    }
  })
}

const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

// 暴露方法
defineExpose({
  initChart,
  selectPeriod,
  refresh: () => {
    if (chart) {
      initChart()
    }
  }
})

// 监听周期变化
watch(selectedPeriod, (newVal) => {
  console.log('Period changed to:', newVal, 'Filtered data length:', filteredStrategyData.value.length)
  if (chart) {
    initChart()
  }
})

// 监听数据变化
watch([() => props.strategyData, () => props.benchmarkData], () => {
  nextTick(() => {
    if (chart) {
      initChart()
    }
  })
}, { deep: true })

// 监听语言变化
watch(() => props.locale, () => {
  nextTick(() => {
    if (chart) {
      initChart()
    }
  })
})

// 生命周期
onMounted(() => {
  nextTick(() => {
    initChart()
  })
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
    chart = null
  }
})
</script>

<style>
.tv-line-chart .tv-logo,
.tv-line-chart .lightweight-charts-logo,
.tv-line-chart .tradingview-logo,
.tv-line-chart a[href*="tradingview"],
.tv-line-chart div[class*="logo"] {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
}
</style>

<style scoped lang="scss">
.tv-line-chart {
  position: relative;
  width: 100%;
  height: v-bind('chartHeight + "px"');
  min-height: v-bind('chartHeight + "px"');

  :deep(.tv-logo),
  :deep(.lightweight-charts-logo) {
    display: none !important;
  }
}

.tv-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
  background: v-bind('darkMode ? "#1e222d" : "#f5f5f5"');
  border-bottom: 1px solid v-bind('darkMode ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)"');

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 6px;

    .chart-icon {
      width: 16px;
      height: 16px;
      color: v-bind('darkMode ? "#d1d4dc" : "#333"');
    }

    .chart-title {
      font-size: 14px;
      font-weight: 600;
      color: v-bind('darkMode ? "#d1d4dc" : "#333"');
    }
  }

  .toolbar-center {
    display: flex;
    gap: 4px;

    .period-btn {
      padding: 4px 10px;
      font-size: 11px;
      background: transparent;
      border: none;
      border-radius: 4px;
      color: v-bind('darkMode ? "#787b86" : "#666"');
      cursor: pointer;
      transition: all 0.15s;

      &:hover {
        color: v-bind('darkMode ? "#d1d4dc" : "#333"');
      }

      &.active {
        background: v-bind('darkMode ? "#2962ff" : "#1976d2"');
        color: white;
      }
    }

    .period-buttons {
      display: flex;
      gap: 4px;
      flex-wrap: wrap;

      .period-btn {
        padding: 4px 10px;
        font-size: 11px;
        background: transparent;
        border: 1px solid v-bind('darkMode ? "#3a3f4b" : "#ddd"');
        border-radius: 4px;
        color: v-bind('darkMode ? "#9ca3af" : "#666"');
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          border-color: v-bind('darkMode ? "#2962ff" : "#1976d2"');
          color: v-bind('darkMode ? "#d1d4dc" : "#333"');
        }

        &.active {
          background: v-bind('darkMode ? "#2962ff" : "#1976d2"');
          border-color: v-bind('darkMode ? "#2962ff" : "#1976d2"');
          color: #fff;
        }
      }
    }

    .period-dropdown {
      padding: 4px 8px;
      font-size: 11px;
      background: v-bind('darkMode ? "#2a2e39" : "#f5f5f5"');
      border: 1px solid v-bind('darkMode ? "#3a3f4b" : "#ddd"');
      border-radius: 4px;
      color: v-bind('darkMode ? "#d1d4dc" : "#333"');
      cursor: pointer;
      outline: none;

      &:hover {
        border-color: v-bind('darkMode ? "#2962ff" : "#1976d2"');
      }

      &:focus {
        border-color: v-bind('darkMode ? "#2962ff" : "#1976d2"');
      }
    }
  }

  .toolbar-right {
    .legend {
      display: flex;
      gap: 16px;

      .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: v-bind('darkMode ? "#cbd5e1" : "#666"');

        .legend-color {
          width: 16px;
          height: 3px;
          border-radius: 2px;

          &.dashed {
            background: repeating-linear-gradient(
              90deg,
              v-bind(benchmarkColor),
              v-bind(benchmarkColor) 4px,
              transparent 4px,
              transparent 8px
            );
          }
        }
      }
    }
  }
}

.tv-chart-area {
  width: 100%;
  height: calc(100% - 20px);
}

.tv-tooltip {
  position: absolute;
  background: v-bind('darkMode ? "#131722" : "#fff"');
  border: 1px solid v-bind('darkMode ? "#2a2e39" : "#e0e0e0"');
  border-radius: 6px;
  padding: 8px 12px;
  min-width: 160px;
  pointer-events: none;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);

  .tooltip-date {
    font-size: 11px;
    font-weight: 600;
    color: v-bind('darkMode ? "#d1d4dc" : "#333"');
    margin-bottom: 6px;
    padding-bottom: 6px;
    border-bottom: 1px solid v-bind('darkMode ? "#2a2e39" : "#e0e0e0"');
  }

  .tooltip-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin: 4px 0;
    font-size: 11px;

    .tooltip-label {
      color: v-bind(strategyColor);
    }

    &.benchmark .tooltip-label {
      color: v-bind(benchmarkColor);
    }

    .tooltip-value {
      font-family: 'SF Mono', 'Monaco', monospace;
      color: v-bind('darkMode ? "#d1d4dc" : "#333"');
    }

    .tooltip-change {
      font-weight: 600;

      &.positive {
        color: #ef5350;
      }

      &.negative {
        color: #26a69a;
      }
    }
  }
}

.resize-handle {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: transparent;
  cursor: ns-resize;
  z-index: 10;

  &:hover {
    background: rgba(41, 98, 255, 0.3);
  }
}
</style>
