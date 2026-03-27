<template>
  <div class="mini-chart" :class="{ 'mini-chart--loading': loading }">
    <!-- 图表头部 -->
    <div v-if="showHeader" class="mini-chart__header">
      <div class="mini-chart__title">
        <span v-if="title">{{ title }}</span>
        <span v-if="subtitle" class="mini-chart__subtitle">{{ subtitle }}</span>
      </div>
      <div v-if="showValue" class="mini-chart__value" :class="valueClass">
        {{ displayValue }}
      </div>
    </div>

    <!-- 图表主体 -->
    <div ref="chartContainer" class="mini-chart__container" :style="containerStyle">
      <svg v-if="!loading && hasData" :width="width" :height="height" class="mini-chart__svg">
        <!-- 网格线 -->
        <g v-if="showGrid" class="mini-chart__grid">
          <line
            v-for="tick in gridTicks"
            :key="`h-${tick}`"
            :x1="0"
            :y1="yScale(tick)"
            :x2="width"
            :y2="yScale(tick)"
            class="mini-chart__grid-line"
          />
          <line
            v-for="tick in xTicks"
            :key="`v-${tick}`"
            :x1="xScale(tick)"
            :y1="0"
            :x2="xScale(tick)"
            :y2="height"
            class="mini-chart__grid-line"
          />
        </g>

        <!-- 面积图 -->
        <defs v-if="type === 'area'">
          <linearGradient :id="gradientId" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" :stop-color="color" stop-opacity="0.3" />
            <stop offset="100%" :stop-color="color" stop-opacity="0.05" />
          </linearGradient>
        </defs>
        <path
          v-if="type === 'area'"
          :d="areaPath"
          :fill="`url(#${gradientId})`"
          class="mini-chart__area"
        />

        <!-- 线条 -->
        <path
          v-if="type === 'line' || type === 'area'"
          :d="linePath"
          :stroke="color"
          :stroke-width="strokeWidth"
          fill="none"
          class="mini-chart__line"
        />

        <!-- 柱状图 -->
        <g v-if="type === 'bar'">
          <rect
            v-for="(value, index) in displayData"
            :key="`bar-${index}`"
            :x="xScale(index) - barWidth / 2"
            :y="yScale(value)"
            :width="barWidth"
            :height="height - yScale(value)"
            :fill="color"
            class="mini-chart__bar"
            :class="{ 'mini-chart__bar--negative': isNegative && value < 0 }"
          />
        </g>

        <!-- 数据点 -->
        <g v-if="showPoints && (type === 'line' || type === 'area')">
          <circle
            v-for="(value, index) in displayData"
            :key="`point-${index}`"
            :cx="xScale(index)"
            :cy="yScale(value)"
            :r="pointRadius"
            :fill="color"
            class="mini-chart__point"
          />
        </g>

        <!-- 鼠标交互 -->
        <g v-if="showTooltip" class="mini-chart__tooltip-group">
          <rect
            :x="tooltipX - tooltipWidth / 2"
            :y="tooltipY - tooltipHeight - 10"
            :width="tooltipWidth"
            :height="tooltipHeight"
            :fill="tooltipBg"
            rx="4"
            class="mini-chart__tooltip-bg"
          />
          <text
            :x="tooltipX"
            :y="tooltipY - tooltipHeight / 2 - 2"
            :fill="tooltipColor"
            text-anchor="middle"
            class="mini-chart__tooltip-text"
          >
            {{ tooltipText }}
          </text>
        </g>
      </svg>

      <!-- 空状态 -->
      <div v-else-if="!loading" class="mini-chart__empty">
        <span class="mini-chart__empty-icon">📊</span>
        <span class="mini-chart__empty-text">{{ emptyText }}</span>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="mini-chart__loading">
        <div class="mini-chart__loading-spinner"></div>
        <span class="mini-chart__loading-text">{{ loadingText }}</span>
      </div>
    </div>

    <!-- 图例 -->
    <div v-if="showLegend && legend" class="mini-chart__legend">
      <span class="mini-chart__legend-item" :style="{ color }">{{ legend }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export type ChartType = 'line' | 'area' | 'bar'

interface DataPoint {
  value: number
  label?: string
  timestamp?: number
}

interface Props {
  // 数据
  data?: number[] | DataPoint[]

  // 图表类型
  type?: ChartType

  // 尺寸
  width?: number
  height?: number

  // 样式
  color?: string
  strokeWidth?: number
  backgroundColor?: string

  // 显示选项
  showHeader?: boolean
  showValue?: boolean
  showGrid?: boolean
  showPoints?: boolean
  showTooltip?: boolean
  showLegend?: boolean

  // 头部信息
  title?: string
  subtitle?: string
  legend?: string

  // 值显示
  valueFormat?: string
  valueDecimals?: number

  // 空状态
  emptyText?: string

  // 加载状态
  loading?: boolean
  loadingText?: string

  // 交互
  hoverable?: boolean

  // 特殊选项
  isNegative?: boolean  // 用于显示涨跌
  percentage?: boolean  // 显示百分比
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  type: 'line',
  width: 200,
  height: 80,
  color: '#8b5cf6',
  strokeWidth: 2,
  backgroundColor: 'transparent',
  showHeader: true,
  showValue: true,
  showGrid: false,
  showPoints: false,
  showTooltip: false,
  showLegend: false,
  title: '',
  subtitle: '',
  legend: '',
  valueFormat: 'auto',
  valueDecimals: 2,
  emptyText: '暂无数据',
  loading: false,
  loadingText: '加载中...',
  hoverable: true,
  isNegative: false,
  percentage: false
})

// 图表容器
const chartContainer = ref<HTMLElement>()
const tooltipX = ref(0)
const tooltipY = ref(0)
const tooltipText = ref('')
const tooltipWidth = 60
const tooltipHeight = 24

// 唯一ID
const gradientId = computed(() => `gradient-${Math.random().toString(36).substr(2, 9)}`)

// 处理数据
const displayData = computed(() => {
  if (!props.data || props.data.length === 0) return []

  if (Array.isArray(props.data[0])) {
    return (props.data as DataPoint[]).map(d => d.value)
  }

  return props.data as number[]
})

const hasData = computed(() => displayData.value.length > 0)

// 计算统计值
const latestValue = computed(() => {
  if (!hasData.value) return 0
  return displayData.value[displayData.value.length - 1]
})

const previousValue = computed(() => {
  if (!hasData.value || displayData.value.length < 2) return 0
  return displayData.value[displayData.value.length - 2]
})

const changePercent = computed(() => {
  if (previousValue.value === 0) return 0
  return ((latestValue.value - previousValue.value) / Math.abs(previousValue.value)) * 100
})

// 格式化显示值
const displayValue = computed(() => {
  if (!hasData.value) return '--'

  const value = props.percentage ? changePercent.value : latestValue.value

  if (props.valueFormat === 'currency') {
    return `¥${value.toFixed(props.valueDecimals)}`
  } else if (props.valueFormat === 'percent') {
    return `${value > 0 ? '+' : ''}${value.toFixed(props.valueDecimals)}%`
  } else if (props.valueFormat === 'change') {
    const sign = value > 0 ? '+' : ''
    return `${sign}${value.toFixed(props.valueDecimals)} (${changePercent.value > 0 ? '+' : ''}${changePercent.value.toFixed(2)}%)`
  } else {
    return value.toFixed(props.valueDecimals)
  }
})

// 值的样式类
const valueClass = computed(() => {
  if (!props.isNegative || !hasData.value) return ''

  const change = latestValue.value - previousValue.value
  return {
    'mini-chart__value--positive': change > 0,
    'mini-chart__value--negative': change < 0
  }
})

// 容器样式
const containerStyle = computed(() => ({
  width: `${props.width}px`,
  height: `${props.height}px`,
  backgroundColor: props.backgroundColor
}))

// 缩放函数
const xScale = computed(() => {
  return (index: number) => {
    if (displayData.value.length <= 1) return props.width / 2
    return (index / (displayData.value.length - 1)) * props.width
  }
})

const yScale = computed(() => {
  const minValue = Math.min(...displayData.value)
  const maxValue = Math.max(...displayData.value)
  const range = maxValue - minValue || 1
  const padding = range * 0.1

  return (value: number) => {
    return props.height - ((value - minValue + padding) / (range + padding * 2)) * props.height
  }
})

// 网格线
const gridTicks = computed(() => {
  const minValue = Math.min(...displayData.value)
  const maxValue = Math.max(...displayData.value)
  const range = maxValue - minValue || 1

  const ticks = []
  const tickCount = 3
  for (let i = 0; i <= tickCount; i++) {
    ticks.push(minValue + (range / tickCount) * i)
  }

  return ticks
})

const xTicks = computed(() => {
  const ticks = []
  const tickCount = Math.min(displayData.value.length - 1, 4)
  for (let i = 0; i <= tickCount; i++) {
    const index = Math.floor((displayData.value.length - 1) * (i / tickCount))
    ticks.push(index)
  }
  return ticks
})

// 路径生成
const linePath = computed(() => {
  if (!hasData.value) return ''

  const points = displayData.value.map((value, index) => {
    return `${xScale.value(index)},${yScale.value(value)}`
  })

  return `M ${points.join(' L ')}`
})

const areaPath = computed(() => {
  if (!hasData.value) return ''

  const linePoints = displayData.value.map((value, index) => {
    return `${xScale.value(index)},${yScale.value(value)}`
  })

  const bottomLeft = `0,${props.height}`
  const bottomRight = `${props.width},${props.height}`

  return `M 0,${props.height} L ${linePoints.join(' L ')} L ${bottomRight} Z`
})

// 柱状图
const barWidth = computed(() => {
  const padding = props.width * 0.2
  return (props.width - padding) / displayData.value.length * 0.6
})

// 鼠标交互
const handleMouseMove = (event: MouseEvent) => {
  if (!props.hoverable || !hasData.value) return

  const rect = chartContainer.value?.getBoundingClientRect()
  if (!rect) return

  const x = event.clientX - rect.left
  const index = Math.round((x / props.width) * (displayData.value.length - 1))

  if (index >= 0 && index < displayData.value.length) {
    const value = displayData.value[index]
    tooltipX.value = xScale.value(index)
    tooltipY.value = yScale.value(value)

    if (props.percentage) {
      tooltipText.value = `${value.toFixed(2)}%`
    } else {
      tooltipText.value = value.toFixed(props.valueDecimals)
    }
  }
}

// 生命周期
onMounted(() => {
  if (chartContainer.value && props.hoverable) {
    chartContainer.value.addEventListener('mousemove', handleMouseMove)
  }
})

onUnmounted(() => {
  if (chartContainer.value) {
    chartContainer.value.removeEventListener('mousemove', handleMouseMove)
  }
})
</script>

<style lang="scss" scoped>
.mini-chart {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  font-size: var(--font-size-sm);

  &--loading {
    opacity: 0.7;
  }

  // 头部
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  &__title {
    display: flex;
    flex-direction: column;
    gap: 2px;

    font-size: var(--font-size-xs);
    color: var(--text-secondary);
  }

  &__subtitle {
    opacity: 0.7;
  }

  &__value {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--text-primary);

    &--positive {
      color: var(--success-color);
    }

    &--negative {
      color: var(--error-color);
    }
  }

  // 容器
  &__container {
    position: relative;
    border-radius: var(--border-radius-base);
    overflow: hidden;
  }

  &__svg {
    width: 100%;
    height: 100%;
  }

  // 图表元素
  &__grid {
    opacity: 0.3;
  }

  &__grid-line {
    stroke: var(--border-color-base);
    stroke-width: 0.5;
    stroke-dasharray: 2 2;
  }

  &__line {
    transition: stroke-width 0.2s;

    &:hover {
      stroke-width: v-bind('strokeWidth * 1.5');
    }
  }

  &__area {
    opacity: 0.8;
  }

  &__bar {
    transition: opacity 0.2s;

    &:hover {
      opacity: 0.8;
    }

    &--negative {
      opacity: 0.7;
    }
  }

  &__point {
    r: 2;
    transition: r 0.2s;

    &:hover {
      r: 4;
    }
  }

  // 工具提示
  &__tooltip-group {
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s;

    &:hover {
      opacity: 1;
    }
  }

  &__tooltip-bg {
    fill: rgba(0, 0, 0, 0.8);
  }

  &__tooltip-text {
    font-size: 10px;
    fill: white;
  }

  // 空状态
  &__empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: var(--spacing-1);
    color: var(--text-disabled);
  }

  &__empty-icon {
    font-size: 24px;
    opacity: 0.5;
  }

  &__empty-text {
    font-size: var(--font-size-xs);
  }

  // 加载状态
  &__loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: var(--spacing-1);
    color: var(--text-secondary);
  }

  &__loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-color-base);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  &__loading-text {
    font-size: var(--font-size-xs);
  }

  // 图例
  &__legend {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__legend-item {
    font-size: var(--font-size-xs);
    display: flex;
    align-items: center;
    gap: 4px;

    &::before {
      content: '';
      width: 8px;
      height: 2px;
      background-color: currentColor;
      border-radius: 1px;
    }
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>