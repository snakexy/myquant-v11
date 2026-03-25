<template>
  <div class="equity-chart-wrapper" ref="wrapperRef">
    <!-- 图表头部（标题、时间范围选择器、图例） -->
    <div class="chart-header">
      <div class="header-left">
        <div class="chart-title">
          <svg class="icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
          </svg>
          {{ title }}
        </div>
      </div>

      <!-- 时间范围选择器 -->
      <div class="time-range-selector" v-if="showTimeRange">
        <button
          v-for="range in timeRanges"
          :key="range.value"
          :class="['range-btn', { active: selectedRange === range.value }]"
          @click="selectTimeRange(range.value)"
        >
          {{ range.label }}
        </button>
      </div>

      <!-- 缩放控制 -->
      <div class="zoom-controls" v-if="showZoomControls">
        <button class="zoom-btn" @click="zoomIn" :disabled="!canZoomIn" title="放大">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="11" y1="8" x2="11" y2="14"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
        </button>
        <button class="zoom-btn" @click="zoomOut" :disabled="!canZoomOut" title="缩小">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
        </button>
        <button class="zoom-btn" @click="resetZoom" title="重置">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="1 4 1 10 7 10"></polyline>
            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
          </svg>
        </button>
      </div>

      <!-- 图例 -->
      <div class="chart-legend" v-if="showLegend">
        <div class="legend-item strategy">
          <span class="legend-line"></span>
          <span>{{ strategyLabel }}</span>
        </div>
        <div class="legend-item benchmark" v-if="benchmarkData.length > 0">
          <span class="legend-line"></span>
          <span>{{ benchmarkLabel }}</span>
        </div>
      </div>
    </div>

    <!-- 图表主体 -->
    <div class="chart-body">
      <!-- Y轴标签 -->
      <div class="y-axis" ref="yAxisRef">
        <span
          v-for="(label, idx) in visibleYAxisLabels"
          :key="idx"
          class="y-label"
          :style="{ top: label.position + '%' }"
        >{{ label.text }}</span>
      </div>

      <!-- SVG图表区域 -->
      <div
        class="chart-area"
        ref="chartAreaRef"
        @wheel="handleWheel"
        @mousedown="startDrag"
        @mousemove="handleMouseMove"
        @mouseup="endDrag"
        @mouseleave="handleMouseLeave"
      >
        <svg
          class="equity-svg"
          :viewBox="`${viewBoxX} ${viewBoxY} ${viewBoxWidth} ${viewBoxHeight}`"
          preserveAspectRatio="none"
          ref="svgRef"
        >
          <defs>
            <!-- 策略线渐变填充 -->
            <linearGradient :id="strategyGradientId" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" :style="`stop-color:${strategyColor};stop-opacity:0.3`"/>
              <stop offset="50%" :style="`stop-color:${strategyColor};stop-opacity:0.1`"/>
              <stop offset="100%" :style="`stop-color:${strategyColor};stop-opacity:0`"/>
            </linearGradient>

            <!-- 策略线发光效果 -->
            <filter :id="glowFilterId" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>

            <!-- 网格线样式 -->
            <pattern :id="gridPatternId" :width="gridStepX" :height="gridStepY" patternUnits="userSpaceOnUse">
              <path :d="`M ${gridStepX} 0 L 0 0 0 ${gridStepY}`" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
            </pattern>

            <!-- 区域选择渐变 -->
            <linearGradient :id="selectionGradientId" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style="stop-color:#2962ff;stop-opacity:0.2"/>
              <stop offset="100%" style="stop-color:#2962ff;stop-opacity:0.05"/>
            </linearGradient>
          </defs>

          <!-- 背景网格 -->
          <rect width="100%" height="100%" :fill="`url(#${gridPatternId})`"/>

          <!-- 水平参考线 -->
          <g class="grid-lines">
            <line
              v-for="(y, idx) in gridYPositions"
              :key="'h'+idx"
              :x1="0"
              :y1="y"
              :x2="chartWidth"
              :y2="y"
              stroke="rgba(255,255,255,0.06)"
              stroke-width="1"
            />
            <!-- 1.0 基准线（如果有） -->
            <line
              v-if="baseLineY !== null"
              :x1="0"
              :y1="baseLineY"
              :x2="chartWidth"
              :y2="baseLineY"
              stroke="rgba(255,255,255,0.15)"
              stroke-width="1"
              stroke-dasharray="5,5"
            />
          </g>

          <!-- 垂直参考线（时间标记） -->
          <g class="vertical-grid">
            <line
              v-for="(x, idx) in verticalGridPositions"
              :key="'v'+idx"
              :x1="x"
              :y1="0"
              :x2="x"
              :y2="chartHeight"
              stroke="rgba(255,255,255,0.04)"
              stroke-width="1"
            />
          </g>

          <!-- 基准线（如果有） -->
          <polyline
            v-if="benchmarkData.length > 0"
            class="benchmark-line"
            fill="none"
            :stroke="benchmarkColor"
            stroke-width="2"
            stroke-dasharray="6,4"
            stroke-linecap="round"
            stroke-linejoin="round"
            :points="visibleBenchmarkPoints"
          />

          <!-- 策略净值填充区域 -->
          <path
            class="strategy-fill"
            :fill="`url(#${strategyGradientId})`"
            :d="visibleStrategyFillPath"
          />

          <!-- 策略净值曲线 -->
          <polyline
            class="strategy-line"
            fill="none"
            :stroke="strategyColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            :filter="`url(#${glowFilterId})`"
            :points="visibleStrategyPoints"
          />

          <!-- 关键数据点 -->
          <g class="data-points" v-if="showDataPoints && zoomLevel <= 2">
            <!-- 起始点 -->
            <circle
              v-if="visibleStrategyData.length > 0"
              :cx="0"
              :cy="scaleY(visibleStrategyData[0].value)"
              r="4"
              fill="#1e222d"
              :stroke="strategyColor"
              stroke-width="2"
            />
            <!-- 最高点 -->
            <circle
              v-if="visibleStrategyData.length > 0 && maxPoint"
              :cx="maxPoint.x"
              :cy="maxPoint.y"
              r="4"
              fill="#1e222d"
              stroke="#9c27b0"
              stroke-width="2"
            />
            <!-- 最低点 -->
            <circle
              v-if="visibleStrategyData.length > 0 && minPoint"
              :cx="minPoint.x"
              :cy="minPoint.y"
              r="4"
              fill="#1e222d"
              stroke="#26a69a"
              stroke-width="2"
            />
          </g>

          <!-- 当前最新点高亮动画 -->
          <g v-if="visibleStrategyData.length > 0 && animateLatest">
            <circle
              :cx="chartWidth"
              :cy="scaleY(visibleStrategyData[visibleStrategyData.length - 1].value)"
              r="8"
              :fill="strategyColor"
              fill-opacity="0.2"
            >
              <animate attributeName="r" values="8;12;8" dur="2s" repeatCount="indefinite"/>
              <animate attributeName="opacity" values="0.3;0.1;0.3" dur="2s" repeatCount="indefinite"/>
            </circle>
            <circle
              :cx="chartWidth"
              :cy="scaleY(visibleStrategyData[visibleStrategyData.length - 1].value)"
              r="5"
              fill="#1e222d"
              :stroke="strategyColor"
              stroke-width="2"
            />
          </g>

          <!-- 收益标注 -->
          <g class="return-label" v-if="showReturnLabel && visibleReturn !== null">
            <rect
              :x="chartWidth - 55"
              :y="scaleY(visibleStrategyData[visibleStrategyData.length - 1]?.value) - 15"
              width="50"
              height="20"
              rx="4"
              :fill="returnLabelBg"
            />
            <text
              :x="chartWidth - 30"
              :y="scaleY(visibleStrategyData[visibleStrategyData.length - 1]?.value) - 1"
              :fill="returnLabelColor"
              font-size="11"
              font-weight="600"
              text-anchor="middle"
            >
              {{ formatReturn(visibleReturn) }}
            </text>
          </g>
        </svg>

        <!-- 十字光标 -->
        <div
          class="crosshair"
          v-if="showCrosshair"
          :style="crosshairStyle"
        >
          <div class="crosshair-h"></div>
          <div class="crosshair-v"></div>
        </div>

        <!-- 数据提示框 -->
        <div
          class="tooltip"
          v-if="showTooltip && tooltipData"
          :style="tooltipStyle"
        >
          <div class="tooltip-header">
            <span class="tooltip-date">{{ tooltipData.date }}</span>
          </div>
          <div class="tooltip-content">
            <div class="tooltip-row strategy">
              <span class="tooltip-label">{{ strategyLabel }}</span>
              <span class="tooltip-value">{{ tooltipData.strategyValue.toFixed(4) }}</span>
              <span :class="['tooltip-change', tooltipData.strategyChange >= 0 ? 'positive' : 'negative']">
                {{ formatReturn(tooltipData.strategyChange) }}
              </span>
            </div>
            <div class="tooltip-row benchmark" v-if="benchmarkData.length > 0 && tooltipData.benchmarkValue">
              <span class="tooltip-label">{{ benchmarkLabel }}</span>
              <span class="tooltip-value">{{ tooltipData.benchmarkValue.toFixed(4) }}</span>
              <span :class="['tooltip-change', tooltipData.benchmarkChange >= 0 ? 'positive' : 'negative']">
                {{ formatReturn(tooltipData.benchmarkChange) }}
              </span>
            </div>
          </div>
        </div>

        <!-- X轴标签 -->
        <div class="x-axis">
          <span
            v-for="(label, idx) in visibleXAxisLabels"
            :key="idx"
            class="x-label"
            :style="{ left: label.position + '%' }"
          >{{ label.text }}</span>
        </div>
      </div>
    </div>

    <!-- 缩放/拖拽提示 -->
    <div class="interaction-hint" v-if="showHint">
      <span>滚轮缩放 · 拖拽平移</span>
    </div>

    <!-- 底部统计信息 -->
    <div class="chart-stats" v-if="showStats && stats.length > 0">
      <div
        v-for="(stat, idx) in stats"
        :key="idx"
        class="stat-item"
      >
        <span class="stat-label">{{ stat.label }}</span>
        <span :class="['stat-value', stat.class]">{{ stat.value }}</span>
      </div>
    </div>

    <!-- 迷你时间轴导航 -->
    <div class="time-navigator" v-if="showNavigator">
      <div class="navigator-track" ref="navigatorRef">
        <div
          class="navigator-window"
          :style="navigatorWindowStyle"
          @mousedown="startNavigatorDrag"
        ></div>
        <svg class="navigator-chart" :viewBox="`0 0 ${chartWidth} 50`" preserveAspectRatio="none">
          <!-- 基准线 -->
          <polyline
            v-if="benchmarkData.length > 0"
            fill="none"
            :stroke="benchmarkColor"
            stroke-width="1"
            :points="navigatorBenchmarkPoints"
            opacity="0.5"
            stroke-dasharray="3,2"
          />
          <!-- 策略线 -->
          <polyline
            fill="none"
            :stroke="strategyColor"
            stroke-width="1.5"
            :points="navigatorPoints"
            opacity="0.7"
          />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'

interface DataPoint {
  index: number
  value: number
}

interface Props {
  // 标题配置
  title?: string
  showHeader?: boolean
  showLegend?: boolean
  strategyLabel?: string
  benchmarkLabel?: string

  // 数据
  strategyData: number[]          // 策略净值数据点
  benchmarkData?: number[]        // 基准净值数据点
  xAxisLabels?: string[]          // X轴标签

  // Y轴配置
  yAxisMin?: number
  yAxisMax?: number
  yAxisStep?: number
  yAxisDecimal?: number

  // 颜色配置
  strategyColor?: string
  benchmarkColor?: string

  // 图表尺寸
  chartWidth?: number
  chartHeight?: number

  // 功能开关
  showDataPoints?: boolean
  showReturnLabel?: boolean
  showStats?: boolean
  animateLatest?: boolean
  showTimeRange?: boolean
  showZoomControls?: boolean
  showCrosshair?: boolean
  showNavigator?: boolean

  // 统计数据
  strategyReturn?: number
  benchmarkReturn?: number
  excessReturn?: number
  correlation?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '净值曲线 vs 基准',
  showHeader: true,
  showLegend: true,
  strategyLabel: '策略净值',
  benchmarkLabel: '沪深300',
  strategyData: () => [],
  benchmarkData: () => [],
  xAxisLabels: () => [],
  yAxisDecimal: 2,
  strategyColor: '#ef5350',
  benchmarkColor: '#787b86',
  chartWidth: 600,
  chartHeight: 200,
  showDataPoints: true,
  showReturnLabel: true,
  showStats: true,
  animateLatest: true,
  showTimeRange: true,
  showZoomControls: true,
  showCrosshair: true,
  showNavigator: true
})

// 唯一ID
const uid = ref(Math.random().toString(36).substring(2, 9))
const strategyGradientId = computed(() => `strategyGradient_${uid.value}`)
const glowFilterId = computed(() => `glow_${uid.value}`)
const gridPatternId = computed(() => `grid_${uid.value}`)
const selectionGradientId = computed(() => `selection_${uid.value}`)

// 时间范围选项
const timeRanges = [
  { label: '1周', value: 7 },
  { label: '1月', value: 30 },
  { label: '3月', value: 90 },
  { label: '6月', value: 180 },
  { label: '1年', value: 365 },
  { label: '全部', value: 0 }
]
const selectedRange = ref(0)

// 缩放和平移状态
const zoomLevel = ref(1)
const panOffset = ref(0)
const maxZoom = 8
const minZoom = 1

// 拖拽状态
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartOffset = ref(0)

// 十字光标和提示
const showCrosshair = ref(false)
const showTooltip = ref(false)
const crosshairX = ref(0)
const crosshairY = ref(0)
const tooltipData = ref<any>(null)

// 提示显示
const showHint = ref(true)

// refs
const chartAreaRef = ref<HTMLElement>()

// 计算实际Y轴范围
const actualYAxisMin = computed(() => {
  if (props.yAxisMin !== undefined) return props.yAxisMin
  const allData = [...visibleStrategyData.value.map(d => d.value), ...(props.benchmarkData || [])]
  const min = Math.min(...allData)
  return Math.floor(min * 100 - 5) / 100
})

const actualYAxisMax = computed(() => {
  if (props.yAxisMax !== undefined) return props.yAxisMax
  const allData = [...visibleStrategyData.value.map(d => d.value), ...(props.benchmarkData || [])]
  const max = Math.max(...allData)
  return Math.ceil(max * 100 + 5) / 100
})

const actualYAxisStep = computed(() => {
  if (props.yAxisStep !== undefined) return props.yAxisStep
  const range = actualYAxisMax.value - actualYAxisMin.value
  return Math.ceil(range / 5 * 100) / 100
})

// 可见数据范围
const visibleStartIndex = computed(() => {
  if (selectedRange.value === 0) return 0
  const dataLength = props.strategyData.length
  const visibleCount = Math.ceil(dataLength / zoomLevel.value)
  return Math.max(0, Math.min(panOffset.value, dataLength - visibleCount))
})

const visibleEndIndex = computed(() => {
  const dataLength = props.strategyData.length
  if (selectedRange.value === 0) {
    const visibleCount = Math.ceil(dataLength / zoomLevel.value)
    return Math.min(dataLength, visibleStartIndex.value + visibleCount)
  }
  return Math.min(dataLength, visibleStartIndex.value + selectedRange.value)
})

// 可见策略数据
const visibleStrategyData = computed<DataPoint[]>(() => {
  if (selectedRange.value === 0) {
    // 全部数据时按缩放级别显示
    const step = Math.max(1, Math.floor(1 / zoomLevel.value))
    const result: DataPoint[] = []
    for (let i = visibleStartIndex.value; i < Math.min(visibleEndIndex.value, props.strategyData.length); i += step) {
      result.push({ index: i, value: props.strategyData[i] })
    }
    // 确保最后一个点包含
    if (result.length > 0 && result[result.length - 1].index !== props.strategyData.length - 1) {
      result.push({ index: props.strategyData.length - 1, value: props.strategyData[props.strategyData.length - 1] })
    }
    return result
  } else {
    // 按时间范围显示
    const startIdx = Math.max(0, props.strategyData.length - selectedRange.value)
    return props.strategyData.slice(startIdx).map((value, idx) => ({
      index: startIdx + idx,
      value
    }))
  }
})

// Y值到SVG坐标的映射
const scaleY = (value: number): number => {
  const range = actualYAxisMax.value - actualYAxisMin.value
  const normalizedValue = (value - actualYAxisMin.value) / range
  return props.chartHeight * (1 - normalizedValue)
}

// X值到SVG坐标的映射
const scaleX = (index: number, data: DataPoint[]): number => {
  if (data.length <= 1) return 0
  const visibleIndex = data.findIndex(d => d.index === index)
  if (visibleIndex === -1) return props.chartWidth
  return (visibleIndex / (data.length - 1)) * props.chartWidth
}

// 网格配置
const gridStepX = computed(() => props.chartWidth / 10)
const gridStepY = computed(() => props.chartHeight / 5)

// Y轴标签
const visibleYAxisLabels = computed(() => {
  const labels: Array<{ text: string; position: number }> = []
  const steps = Math.round((actualYAxisMax.value - actualYAxisMin.value) / actualYAxisStep.value)
  for (let i = 0; i <= steps; i++) {
    const value = actualYAxisMax.value - i * actualYAxisStep.value
    labels.push({
      text: value.toFixed(props.yAxisDecimal),
      position: (i / steps) * 100
    })
  }
  return labels
})

// 网格Y位置
const gridYPositions = computed(() => {
  const positions: number[] = []
  const steps = Math.round((actualYAxisMax.value - actualYAxisMin.value) / actualYAxisStep.value)
  const stepHeight = props.chartHeight / steps
  for (let i = 0; i <= steps; i++) {
    positions.push(i * stepHeight)
  }
  return positions
})

// 垂直网格位置
const verticalGridPositions = computed(() => {
  const positions: number[] = []
  const count = 6
  for (let i = 1; i < count; i++) {
    positions.push((props.chartWidth / count) * i)
  }
  return positions
})

// 1.0基准线位置
const baseLineY = computed(() => {
  if (actualYAxisMin.value <= 1.0 && actualYAxisMax.value >= 1.0) {
    return scaleY(1.0)
  }
  return null
})

// 策略线点坐标
const visibleStrategyPoints = computed(() => {
  return visibleStrategyData.value
    .map(d => `${scaleX(d.index, visibleStrategyData.value)},${scaleY(d.value)}`)
    .join(' ')
})

// 基准线点坐标
const visibleBenchmarkPoints = computed(() => {
  if (props.benchmarkData.length === 0) return ''

  const visibleBenchmark = visibleStrategyData.value.map(d => ({
    index: d.index,
    value: props.benchmarkData[d.index] || 1
  }))

  return visibleBenchmark
    .map(d => `${scaleX(d.index, visibleStrategyData.value)},${scaleY(d.value)}`)
    .join(' ')
})

// 策略填充路径
const visibleStrategyFillPath = computed(() => {
  if (visibleStrategyData.value.length === 0) return ''

  const points = visibleStrategyData.value.map(d => ({
    x: scaleX(d.index, visibleStrategyData.value),
    y: scaleY(d.value)
  }))

  let path = `M ${points[0].x},${points[0].y}`
  for (let i = 1; i < points.length; i++) {
    path += ` L ${points[i].x},${points[i].y}`
  }
  path += ` L ${points[points.length - 1].x},${props.chartHeight} L ${points[0].x},${props.chartHeight} Z`

  return path
})

// X轴标签
const visibleXAxisLabels = computed(() => {
  if (props.xAxisLabels.length === 0) return []

  const labels: Array<{ text: string; position: number }> = []
  const dataLength = visibleStrategyData.value.length
  const labelCount = Math.min(7, dataLength)
  const step = Math.floor(dataLength / labelCount)

  for (let i = 0; i < labelCount; i++) {
    const idx = i * step
    const originalIndex = visibleStrategyData.value[idx]?.index ?? idx
    if (originalIndex < props.xAxisLabels.length) {
      labels.push({
        text: props.xAxisLabels[originalIndex],
        position: (i / (labelCount - 1)) * 100
      })
    }
  }

  return labels
})

// 最高/最低点
const maxPoint = computed(() => {
  if (visibleStrategyData.value.length === 0) return null
  let max = visibleStrategyData.value[0]
  for (const d of visibleStrategyData.value) {
    if (d.value > max.value) max = d
  }
  return {
    x: scaleX(max.index, visibleStrategyData.value),
    y: scaleY(max.value)
  }
})

const minPoint = computed(() => {
  if (visibleStrategyData.value.length === 0) return null
  let min = visibleStrategyData.value[0]
  for (const d of visibleStrategyData.value) {
    if (d.value < min.value) min = d
  }
  return {
    x: scaleX(min.index, visibleStrategyData.value),
    y: scaleY(min.value)
  }
})

// 可见收益率
const visibleReturn = computed(() => {
  if (visibleStrategyData.value.length < 2) return null
  const start = visibleStrategyData.value[0].value
  const end = visibleStrategyData.value[visibleStrategyData.value.length - 1].value
  return end - start
})

// 收益标注颜色
const returnLabelColor = computed(() => {
  if (visibleReturn.value === null) return props.strategyColor
  return visibleReturn.value >= 0 ? '#ef5350' : '#26a69a'
})

const returnLabelBg = computed(() => {
  if (visibleReturn.value === null) return 'rgba(239,83,80,0.15)'
  return visibleReturn.value >= 0 ? 'rgba(239,83,80,0.2)' : 'rgba(38,166,154,0.2)'
})

// 格式化收益率
const formatReturn = (value: number): string => {
  const pct = value * 100
  return `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%`
}

// 统计数据
const stats = computed(() => {
  const result: Array<{ label: string; value: string; class?: string }> = []

  if (props.strategyReturn !== undefined) {
    result.push({
      label: '策略收益',
      value: formatReturn(props.strategyReturn),
      class: props.strategyReturn >= 0 ? 'positive' : 'negative'
    })
  }

  if (props.benchmarkReturn !== undefined) {
    result.push({
      label: '基准收益',
      value: formatReturn(props.benchmarkReturn)
    })
  }

  if (props.excessReturn !== undefined) {
    result.push({
      label: '超额收益',
      value: formatReturn(props.excessReturn),
      class: props.excessReturn >= 0 ? 'positive' : 'negative'
    })
  }

  if (props.correlation !== undefined) {
    result.push({
      label: '相关性',
      value: props.correlation.toFixed(2)
    })
  }

  return result
})

// ViewBox计算
const viewBoxX = computed(() => 0)
const viewBoxY = computed(() => 0)
const viewBoxWidth = computed(() => props.chartWidth)
const viewBoxHeight = computed(() => props.chartHeight)

// 缩放能力
const canZoomIn = computed(() => zoomLevel.value < maxZoom)
const canZoomOut = computed(() => zoomLevel.value > minZoom)

// 时间范围选择
const selectTimeRange = (value: number) => {
  selectedRange.value = value
  if (value > 0) {
    zoomLevel.value = 1
    panOffset.value = 0
  }
}

// 缩放功能
const zoomIn = () => {
  if (canZoomIn.value) {
    zoomLevel.value = Math.min(maxZoom, zoomLevel.value * 1.5)
  }
}

const zoomOut = () => {
  if (canZoomOut.value) {
    zoomLevel.value = Math.max(minZoom, zoomLevel.value / 1.5)
    // 确保不会平移出边界
    const dataLength = props.strategyData.length
    const visibleCount = Math.ceil(dataLength / zoomLevel.value)
    panOffset.value = Math.min(panOffset.value, dataLength - visibleCount)
  }
}

const resetZoom = () => {
  zoomLevel.value = 1
  panOffset.value = 0
  selectedRange.value = 0
}

// 滚轮缩放
const handleWheel = (e: WheelEvent) => {
  e.preventDefault()
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  const newZoom = Math.max(minZoom, Math.min(maxZoom, zoomLevel.value * delta))

  if (newZoom !== zoomLevel.value) {
    zoomLevel.value = newZoom
    showHint.value = false
  }
}

// 拖拽功能
const startDrag = (e: MouseEvent) => {
  if (e.button !== 0) return
  isDragging.value = true
  dragStartX.value = e.clientX
  dragStartOffset.value = panOffset.value
  if (chartAreaRef.value) {
    chartAreaRef.value.style.cursor = 'grabbing'
  }
}

const endDrag = () => {
  isDragging.value = false
  if (chartAreaRef.value) {
    chartAreaRef.value.style.cursor = 'crosshair'
  }
}

// 鼠标移动处理
const handleMouseMove = (e: MouseEvent) => {
  if (!chartAreaRef.value) return

  const rect = chartAreaRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  if (isDragging.value && selectedRange.value === 0) {
    const deltaX = e.clientX - dragStartX.value
    const sensitivity = 2
    panOffset.value = Math.max(0, dragStartOffset.value - deltaX * sensitivity / zoomLevel.value)
    showHint.value = false
  }

  // 十字光标
  if (x >= 0 && x <= rect.width && y >= 0 && y <= rect.height) {
    showCrosshair.value = true
    crosshairX.value = x
    crosshairY.value = y

    // 计算数据点
    const dataLength = visibleStrategyData.value.length
    if (dataLength > 0) {
      const idx = Math.round((x / rect.width) * (dataLength - 1))
      const dataPoint = visibleStrategyData.value[Math.max(0, Math.min(idx, dataLength - 1))]

      if (dataPoint) {
        tooltipData.value = {
          date: props.xAxisLabels[dataPoint.index] || `第${dataPoint.index + 1}期`,
          strategyValue: dataPoint.value,
          strategyChange: dataPoint.value - visibleStrategyData.value[0].value,
          benchmarkValue: props.benchmarkData[dataPoint.index],
          benchmarkChange: props.benchmarkData[dataPoint.index] - props.benchmarkData[visibleStrategyData.value[0].index]
        }
        showTooltip.value = true
      }
    }
  }
}

const handleMouseLeave = () => {
  showCrosshair.value = false
  showTooltip.value = false
  isDragging.value = false
}

// 十字光标样式
const crosshairStyle = computed(() => ({
  '--x': crosshairX.value + 'px',
  '--y': crosshairY.value + 'px'
}))

// 提示框样式
const tooltipStyle = computed(() => {
  const x = crosshairX.value
  const y = crosshairY.value
  const offset = 15

  let left = x + offset
  let top = y - 60

  // 防止超出右边界
  if (left > (chartAreaRef.value?.clientWidth || 400) - 180) {
    left = x - 180 - offset
  }

  // 防止超出上边界
  if (top < 10) {
    top = y + offset
  }

  return {
    left: left + 'px',
    top: top + 'px'
  }
})

// 导航器窗口样式
const navigatorWindowStyle = computed(() => {
  const dataLength = props.strategyData.length
  const windowWidth = selectedRange.value > 0
    ? selectedRange.value / dataLength * 100
    : 100 / zoomLevel.value
  const windowLeft = selectedRange.value > 0
    ? (dataLength - selectedRange.value) / dataLength * 100
    : panOffset.value / dataLength * 100

  return {
    width: windowWidth + '%',
    left: windowLeft + '%'
  }
})

// 导航器点坐标
const navigatorPoints = computed(() => {
  if (props.strategyData.length < 2) return ''

  const min = actualYAxisMin.value
  const max = actualYAxisMax.value
  const range = max - min
  if (range <= 0) return ''

  return props.strategyData
    .map((value, index) => {
      const x = (index / (props.strategyData.length - 1)) * props.chartWidth
      const normalizedValue = (value - min) / range
      const y = 35 - normalizedValue * 30  // 从35到5的范围内绘制
      return `${x},${y}`
    })
    .join(' ')
})

// 导航器基准线点坐标
const navigatorBenchmarkPoints = computed(() => {
  if (!props.benchmarkData || props.benchmarkData.length < 2) return ''

  const min = actualYAxisMin.value
  const max = actualYAxisMax.value
  const range = max - min
  if (range <= 0) return ''

  return props.benchmarkData
    .map((value, index) => {
      const x = (index / (props.benchmarkData!.length - 1)) * props.chartWidth
      const normalizedValue = (value - min) / range
      const y = 35 - normalizedValue * 30
      return `${x},${y}`
    })
    .join(' ')
})

// 导航器拖拽
const startNavigatorDrag = (e: MouseEvent) => {
  e.preventDefault()
  // TODO: 实现导航器拖拽
}

// 3秒后隐藏提示
onMounted(() => {
  setTimeout(() => {
    showHint.value = false
  }, 5000)
})

// 导出方法
defineExpose({
  zoomIn,
  zoomOut,
  resetZoom,
  selectTimeRange
})
</script>

<style lang="scss" scoped>
.equity-chart-wrapper {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 16px;
  position: relative;
  user-select: none;
}

// 图表头部
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 16px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary, #d1d4dc);
}

.icon-md {
  width: 16px;
  height: 16px;
}

// 时间范围选择器
.time-range-selector {
  display: flex;
  background: var(--bg-tertiary, #2a2e39);
  border-radius: 6px;
  padding: 2px;
  gap: 2px;
}

.range-btn {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-secondary, #787b86);
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    color: var(--text-primary, #d1d4dc);
  }

  &.active {
    background: var(--accent-blue, #2962ff);
    color: white;
  }
}

// 缩放控制
.zoom-controls {
  display: flex;
  gap: 4px;
}

.zoom-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary, #2a2e39);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 4px;
  color: var(--text-secondary, #787b86);
  cursor: pointer;
  transition: all 0.15s;

  svg {
    width: 14px;
    height: 14px;
  }

  &:hover:not(:disabled) {
    background: var(--bg-hover, rgba(255,255,255,0.05));
    color: var(--text-primary, #d1d4dc);
    border-color: var(--accent-blue, #2962ff);
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

// 图例
.chart-legend {
  display: flex;
  gap: 16px;

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--text-secondary, #cbd5e1);

    .legend-line {
      width: 20px;
      height: 3px;
      border-radius: 2px;
    }

    &.strategy .legend-line {
      background: #ef5350;
    }

    &.benchmark .legend-line {
      background: #787b86;
      background: repeating-linear-gradient(
        90deg,
        #787b86,
        #787b86 4px,
        transparent 4px,
        transparent 8px
      );
    }
  }
}

// 图表主体
.chart-body {
  display: flex;
  gap: 8px;
}

// Y轴
.y-axis {
  position: relative;
  width: 40px;
  height: 200px;

  .y-label {
    position: absolute;
    right: 8px;
    font-size: 10px;
    color: var(--text-secondary, #787b86);
    font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
    transform: translateY(-50%);
  }
}

// 图表区域
.chart-area {
  flex: 1;
  position: relative;
  cursor: crosshair;
}

.equity-svg {
  width: 100%;
  height: 200px;
  display: block;
}

// X轴
.x-axis {
  position: relative;
  height: 20px;
  margin-top: 4px;

  .x-label {
    position: absolute;
    transform: translateX(-50%);
    font-size: 10px;
    color: var(--text-secondary, #787b86);
  }
}

// 十字光标
.crosshair {
  pointer-events: none;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 20px;

  .crosshair-h {
    position: absolute;
    left: 0;
    right: 0;
    top: var(--y);
    height: 1px;
    background: rgba(255, 255, 255, 0.2);
  }

  .crosshair-v {
    position: absolute;
    top: 0;
    bottom: 0;
    left: var(--x);
    width: 1px;
    background: rgba(255, 255, 255, 0.2);
  }
}

// 提示框
.tooltip {
  position: absolute;
  background: var(--bg-primary, #131722);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 6px;
  padding: 8px 12px;
  min-width: 160px;
  pointer-events: none;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);

  .tooltip-header {
    margin-bottom: 6px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border-color, #2a2e39);

    .tooltip-date {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
    }
  }

  .tooltip-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin: 4px 0;
    font-size: 11px;

    &.strategy .tooltip-label { color: #ef5350; }
    &.benchmark .tooltip-label { color: #787b86; }

    .tooltip-value {
      font-family: 'SF Mono', 'Monaco', monospace;
      color: var(--text-primary, #d1d4dc);
    }

    .tooltip-change {
      font-weight: 600;

      &.positive { color: #ef5350; }
      &.negative { color: #26a69a; }
    }
  }
}

// 交互提示
.interaction-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.7);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 11px;
  color: var(--text-secondary, #787b86);
  pointer-events: none;
  opacity: 0.7;
}

// 底部统计
.chart-stats {
  display: flex;
  gap: 24px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color, #2a2e39);

  .stat-item {
    display: flex;
    flex-direction: column;
    gap: 2px;

    .stat-label {
      font-size: 10px;
      color: var(--text-secondary, #787b86);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .stat-value {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);

      &.positive { color: #ef5350; }
      &.negative { color: #26a69a; }
    }
  }
}

// 时间导航器
.time-navigator {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color, #2a2e39);
}

.navigator-track {
  position: relative;
  height: 50px;
  background: var(--bg-primary, #131722);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--border-color, #2a2e39);
}

.navigator-chart {
  width: 100%;
  height: 100%;
}

.navigator-window {
  position: absolute;
  top: 0;
  height: 100%;
  background: rgba(41, 98, 255, 0.2);
  border: 2px solid rgba(41, 98, 255, 0.6);
  border-radius: 4px;
  cursor: ew-resize;
  transition: background 0.2s;

  &:hover {
    background: rgba(41, 98, 255, 0.3);
  }
}
</style>
