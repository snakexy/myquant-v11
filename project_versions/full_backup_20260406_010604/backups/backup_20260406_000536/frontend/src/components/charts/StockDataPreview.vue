<template>
  <div class="stock-data-preview">
    <!-- 股票信息头部 -->
    <div class="stock-preview__header">
      <div class="stock-info">
        <h3 class="stock-name">{{ stockName || stockCode }}</h3>
        <span v-if="stockCode" class="stock-code">{{ stockCode }}</span>
      </div>
      <!-- 显示成交量信息 -->
      <div v-if="showVolume && volume" class="volume-info">
        <div class="volume-label">成交量</div>
        <div class="volume-value">{{ formatNumber(volume) }}</div>
        <div class="volume-unit">手</div>
      </div>

      <!-- 显示价格信息 -->
      <div v-else-if="!showVolume && latestPrice" class="stock-price">
        <span class="price" :class="changeClass">{{ formatPrice(latestPrice) }}</span>
        <span class="change" :class="changeClass">
          {{ formatChange(changeAmount, changePercent) }}
        </span>
      </div>
    </div>

    <!-- 价格走势图 -->
    <MiniChart
      :data="priceData"
      type="line"
      :width="chartWidth"
      :height="chartHeight"
      :color="chartColor"
      :stroke-width="2"
      :show-grid="showGrid"
      :show-points="false"
      :loading="loading"
      :is-negative="true"
      value-format="currency"
      :value-decimals="2"
    />

    <!-- 成交量图 -->
    <div v-if="showVolume" class="volume-section">
      <MiniChart
        :data="volumeData"
        type="bar"
        :width="chartWidth"
        :height="40"
        color="rgba(139, 92, 246, 0.4)"
        :loading="loading"
        title="成交量"
        :show-header="true"
        :show-value="false"
      />
    </div>

    <!-- 关键指标 -->
    <div v-if="showMetrics && metrics" class="metrics-section">
      <div class="metrics-grid">
        <div v-for="metric in displayMetrics" :key="metric.key" class="metric-item">
          <label class="metric-label">{{ metric.label }}</label>
          <span class="metric-value" :class="metric.class">
            {{ metric.value }}
          </span>
        </div>
      </div>
    </div>

    <!-- 时间范围选择器 -->
    <div v-if="showTimeRange" class="time-range-section">
      <div class="time-range-buttons">
        <button
          v-for="range in timeRanges"
          :key="range.value"
          class="range-btn"
          :class="{ active: selectedRange === range.value }"
          @click="handleRangeChange(range.value)"
        >
          {{ range.label }}
        </button>
      </div>
    </div>

    <!-- 数据报告 -->
    <div v-if="showDataReport && !loading" class="data-report-section">
      <div class="data-report-item">
        <span class="report-label">显示数据量</span>
        <span class="report-value">{{ dataReport.filteredDataCount > 0 ? dataReport.formattedDataCount : '暂无数据' }}</span>
      </div>
      <div v-if="selectedRange !== 'ALL' && dataReport.totalDataCount > dataReport.filteredDataCount" class="data-report-item">
        <span class="report-label">总数据量</span>
        <span class="report-value-secondary">{{ formatDataCount(dataReport.totalDataCount) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import MiniChart from './MiniChart.vue'

export interface StockData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface StockMetrics {
  ma5?: number
  ma10?: number
  ma20?: number
  ma60?: number
  rsi?: number
  macd?: number
  kdj?: {
    k?: number
    d?: number
    j?: number
  }
  pe?: number
  pb?: number
}

interface Props {
  // 基础信息
  stockCode?: string
  stockName?: string

  // 数据
  data?: StockData[]
  metrics?: StockMetrics

  // 图表配置
  chartWidth?: number
  chartHeight?: number
  showGrid?: boolean
  showVolume?: boolean
  showMetrics?: boolean
  showTimeRange?: boolean
  showDataReport?: boolean  // 新增：是否显示数据报告

  // 状态
  loading?: boolean

  // 默认时间范围
  defaultRange?: string
}

const props = withDefaults(defineProps<Props>(), {
  stockCode: '',
  stockName: '',
  data: () => [],
  chartWidth: 280,
  chartHeight: 120,
  showGrid: true,
  showVolume: false,
  showMetrics: true,
  showTimeRange: true,
  showDataReport: true,  // 默认显示数据报告
  loading: false,
  defaultRange: '1M'
})

const emit = defineEmits<{
  'range-change': [range: string]
}>()

// 时间范围选项
const timeRanges = [
  { label: '5日', value: '5D' },
  { label: '1月', value: '1M' },
  { label: '3月', value: '3M' },
  { label: '6月', value: '6M' },
  { label: '1年', value: '1Y' },
  { label: '全部', value: 'ALL' }
]

// 选中的时间范围
const selectedRange = ref(props.defaultRange)

// 监听 defaultRange 变化，同步更新 selectedRange
watch(() => props.defaultRange, (newRange) => {
  if (newRange && newRange !== selectedRange.value) {
    selectedRange.value = newRange
  }
})

// 根据时间范围过滤数据
const filteredData = computed(() => {
  if (!props.data || props.data.length === 0) return []

  const range = selectedRange.value

  // 如果是'ALL'，返回全部数据
  if (range === 'ALL') {
    return props.data
  }

  // 计算要显示的数据点数量
  // 假设每个交易日约250个数据点/年
  const dataPointsPerYear = 250
  let targetCount = 0

  switch (range) {
    case '5D':
      targetCount = 5
      break
    case '1M':
      targetCount = Math.ceil(dataPointsPerYear / 12) // 约21个交易日
      break
    case '3M':
      targetCount = Math.ceil(dataPointsPerYear / 4) // 约63个交易日
      break
    case '6M':
      targetCount = Math.ceil(dataPointsPerYear / 2) // 约125个交易日
      break
    case '1Y':
      targetCount = dataPointsPerYear
      break
    default:
      return props.data
  }

  // 返回最后N个数据点
  const startIndex = Math.max(0, props.data.length - targetCount)
  return props.data.slice(startIndex)
})

// 计算价格数据
const priceData = computed(() => {
  if (filteredData.value.length === 0) return []
  return filteredData.value.map(d => d.close)
})

const volumeData = computed(() => {
  if (filteredData.value.length === 0) return []
  return filteredData.value.map(d => d.volume)
})

// 最新成交量
const volume = computed(() => {
  if (filteredData.value.length === 0) return null
  return filteredData.value[filteredData.value.length - 1].volume
})

// 最新价格
const latestPrice = computed(() => {
  if (filteredData.value.length === 0) return null
  return filteredData.value[filteredData.value.length - 1].close
})

const previousPrice = computed(() => {
  if (filteredData.value.length < 2) return null
  return filteredData.value[filteredData.value.length - 2].close
})

// 价格变化
const changeAmount = computed(() => {
  if (!latestPrice.value || !previousPrice.value) return 0
  return latestPrice.value - previousPrice.value
})

const changePercent = computed(() => {
  if (!previousPrice.value || previousPrice.value === 0) return 0
  return (changeAmount.value / previousPrice.value) * 100
})

// 图表颜色
const chartColor = computed(() => {
  // 中国股市颜色标准：涨红跌绿
  return changePercent.value >= 0 ? '#ef4444' : '#22c55e'
})

// 变化样式
const changeClass = computed(() => ({
  'positive': changePercent.value > 0,
  'negative': changePercent.value < 0
}))

// 显示的指标
const displayMetrics = computed(() => {
  if (!props.metrics) return []

  const metrics = []

  if (props.metrics.ma5 !== undefined) {
    metrics.push({
      key: 'ma5',
      label: 'MA5',
      value: formatPrice(props.metrics.ma5),
      class: getMetricClass(props.metrics.ma5, latestPrice.value)
    })
  }

  if (props.metrics.ma20 !== undefined) {
    metrics.push({
      key: 'ma20',
      label: 'MA20',
      value: formatPrice(props.metrics.ma20),
      class: getMetricClass(props.metrics.ma20, latestPrice.value)
    })
  }

  if (props.metrics.rsi !== undefined) {
    metrics.push({
      key: 'rsi',
      label: 'RSI',
      value: props.metrics.rsi.toFixed(2),
      class: props.metrics.rsi > 70 ? 'overbought' : props.metrics.rsi < 30 ? 'oversold' : ''
    })
  }

  if (props.metrics.pe !== undefined) {
    metrics.push({
      key: 'pe',
      label: 'PE',
      value: props.metrics.pe.toFixed(2),
      class: props.metrics.pe > 30 ? 'high' : props.metrics.pe < 10 ? 'low' : ''
    })
  }

  return metrics.slice(0, 4) // 最多显示4个指标
})

// 格式化函数
const formatPrice = (price: number) => {
  return `¥${price.toFixed(2)}`
}

const formatChange = (amount: number, percent: number) => {
  const sign = amount >= 0 ? '+' : ''
  return `${sign}${amount.toFixed(2)} (${sign}${percent.toFixed(2)}%)`
}

const formatNumber = (num: number) => {
  if (num >= 100000000) {
    return (num / 100000000).toFixed(2) + '亿'
  } else if (num >= 10000) {
    return (num / 10000).toFixed(2) + '万'
  } else {
    return num.toFixed(0)
  }
}

const getMetricClass = (metricValue: number, priceValue?: number) => {
  if (!priceValue) return ''

  if (metricValue > priceValue) {
    return 'positive'
  } else if (metricValue < priceValue) {
    return 'negative'
  }
  return ''
}

// 处理时间范围变化
const handleRangeChange = (range: string) => {
  selectedRange.value = range
  emit('range-change', range)
}

// 数据报告
const dataReport = computed(() => {
  const totalDataCount = props.data?.length || 0
  const filteredDataCount = filteredData.value.length
  return {
    totalDataCount,
    filteredDataCount,
    formattedDataCount: formatDataCount(filteredDataCount)
  }
})

// 格式化数据量显示
const formatDataCount = (count: number): string => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万条'
  }
  return count + '条'
}

</script>

<style lang="scss" scoped>
.stock-data-preview {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  width: 100%;  // 使用100%宽度，自适应父容器
  min-width: 360px;  // 增加最小宽度，确保有足够空间显示完整的股票代码
  background: var(--bg-surface);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
}

// 头部
.stock-preview__header {
  display: flex;
  align-items: center;
  justify-content: flex-start;  // 改为左对齐，不使用 space-between
  margin-bottom: var(--spacing-1);
  gap: 12px;
  flex-wrap: nowrap;
  width: 100%;
}

.stock-info {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  gap: 8px;
  flex: 0 0 auto;  // 不伸缩，按内容宽度
  min-width: 0;
  overflow: visible;
}

.stock-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  white-space: nowrap;
  flex-shrink: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stock-code {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  flex-shrink: 0;
  overflow: visible;
  letter-spacing: 0.3px;
  font-weight: 500;
}

.stock-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  margin-left: auto;  // 自动推到右侧
  flex-shrink: 0;
}

.price {
  font-size: var(--font-size-lg);
  font-weight: 600;
  // 移除默认颜色，将使用动态的 changeClass 来设置颜色
}

.change {
  font-size: var(--font-size-sm);
  font-weight: 500;

  // 中国股市颜色标准：涨红跌绿
  &.positive {
    color: #ef4444;  // 红色表示上涨
  }

  &.negative {
    color: #22c55e;  // 绿色表示下跌
  }
}

// 成交量部分
.volume-section {
  margin-top: var(--spacing-1);
}

.volume-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.volume-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.volume-value {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.volume-unit {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

// 指标部分
.metrics-section {
  margin-top: var(--spacing-2);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-2);
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-1) var(--spacing-2);
  background: var(--bg-color-base);
  border-radius: var(--border-radius-base);
}

.metric-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.metric-value {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);

  // 中国股市颜色标准：涨红跌绿
  &.positive {
    color: #ef4444;  // 红色表示上涨/高于现价
  }

  &.negative {
    color: #22c55e;  // 绿色表示下跌/低于现价
  }

  &.overbought {
    color: var(--warning-color);
  }

  &.oversold {
    color: var(--primary-color);
  }

  &.high {
    color: var(--warning-color);
  }

  &.low {
    color: var(--primary-color);
  }
}

// 时间范围选择器
.time-range-section {
  margin-top: var(--spacing-2);
}

.time-range-buttons {
  display: flex;
  gap: var(--spacing-1);
  padding: var(--spacing-1);
  background: var(--bg-color-base);
  border-radius: var(--border-radius-base);
}

.range-btn {
  flex: 1;
  padding: var(--spacing-1) var(--spacing-2);
  background: transparent;
  border: 1px solid var(--border-color-base);
  border-radius: var(--border-radius-base);
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--bg-color-tertiary);
    color: var(--text-primary);
  }

  &.active {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
  }
}

// 数据报告部分
.data-report-section {
  margin-top: var(--spacing-2);
  padding: var(--spacing-2);
  background: var(--glass-bg);
  border-radius: var(--border-radius-base);
  border: 1px solid var(--glass-border);
}

.data-report-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.report-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--primary-color);
}

.report-value-secondary {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-secondary);
}
</style>