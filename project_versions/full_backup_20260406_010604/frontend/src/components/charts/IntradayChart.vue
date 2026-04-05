<template>
  <div class="intraday-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar" v-if="showToolbar">
      <div class="toolbar-left">
        <div class="stock-info">
          <span class="stock-name">{{ stockName }}</span>
          <span class="stock-code">{{ stockCode }}</span>
        </div>
        <div class="price-info" v-if="currentPrice">
          <span class="current-price" :class="getPriceChangeClass()">
            {{ currentPrice.toFixed(2) }}
          </span>
          <span class="price-change" :class="getPriceChangeClass()">
            {{ formatPriceChange() }}
          </span>
          <span class="price-time">{{ currentTime }}</span>
        </div>
      </div>
      <div class="toolbar-right">
        <button class="action-btn" @click="resetChart" title="重置">
          <i class="fas fa-expand"></i>
        </button>
      </div>
    </div>

    <!-- 图表容器 -->
    <div ref="chartContainer" class="chart" :style="{ height: chartHeight }"></div>

    <!-- 加载状态 -->
    <div v-if="loading" class="chart-loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { createChart } from 'lightweight-charts'

// 定义 lightweight-charts 相关类型
type IChartApi = any
type ISeriesApi<T = any> = any
type ColorType = any
type CrosshairMode = any
type LineData = any
type HistogramData = any
type Time = any

interface IntradayData {
  time: string
  price: number
  volume: number
  avg_price: number
}

interface Props {
  stockCode?: string
  stockName?: string
  data?: IntradayData[]
  height?: string
  loading?: boolean
  showToolbar?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
  loading: false,
  showToolbar: true
})

const emit = defineEmits<{
  ready: []
}>()

// DOM引用
const chartContainer = ref<HTMLElement>()

// 图表实例
let chart: IChartApi | null = null
let priceSeries: ISeriesApi<'Line'> | null = null
let avgPriceSeries: ISeriesApi<'Line'> | null = null
let volumeSeries: ISeriesApi<'Histogram'> | null = null

// 状态
const internalData = ref<IntradayData[]>([])
const currentPrice = ref(0)
const priceChange = ref(0)
const prevClose = ref(0)
const currentTime = ref('')

// 图表高度
const chartHeight = computed(() => {
  return props.showToolbar ? `calc(${props.height} - 50px)` : props.height
})

// 显示的数据
const displayData = computed(() => {
  return props.data && props.data.length > 0 ? props.data : internalData.value
})

const displayLoading = computed(() => {
  return props.loading
})

// 颜色配置
const colors = {
  bgColor: '#0f0f23',
  lineColor: '#ffffff',
  avgLineColor: '#FFEB3B',
  volumeUp: '#ef4444',
  volumeDown: '#10b981',
  gridColor: '#1a1a2e',
  textColor: '#f8fafc'
}

// 获取价格变化颜色类
const getPriceChangeClass = () => {
  if (priceChange.value > 0) return 'price-up'
  if (priceChange.value < 0) return 'price-down'
  return 'price-flat'
}

// 格式化价格变化
const formatPriceChange = () => {
  const sign = priceChange.value >= 0 ? '+' : ''
  return `${sign}${priceChange.value.toFixed(2)}%`
}

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return

  // 创建图表
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: parseInt(chartHeight.value),
    layout: {
      background: { type: ColorType.Solid, color: colors.bgColor },
      textColor: colors.textColor
    },
    grid: {
      vertLines: { color: colors.gridColor },
      horzLines: { color: colors.gridColor }
    },
    crosshair: {
      mode: CrosshairMode.Normal,
      vertLine: {
        color: '#758696',
        width: 1,
        style: 3,
        labelBackgroundColor: colors.bgColor
      },
      horzLine: {
        color: '#758696',
        width: 1,
        style: 3,
        labelBackgroundColor: colors.bgColor
      }
    },
    rightPriceScale: {
      borderColor: colors.gridColor
    },
    timeScale: {
      borderColor: colors.gridColor,
      timeVisible: true,
      secondsVisible: false
    }
  })

  // 添加价格线
  priceSeries = chart.addLineSeries({
    color: colors.lineColor,
    lineWidth: 2,
    priceLineVisible: true,
    lastValueVisible: true,
    crosshairMarkerVisible: true,
    crosshairMarkerRadius: 4
  })

  // 添加均价线
  avgPriceSeries = chart.addLineSeries({
    color: colors.avgLineColor,
    lineWidth: 1,
    priceLineVisible: false,
    lastValueVisible: false,
    crosshairMarkerVisible: true,
    crosshairMarkerRadius: 3
  })

  // 添加成交量柱状图
  volumeSeries = chart.addHistogramSeries({
    color: '#26A69A',
    priceFormat: {
      type: 'volume'
    },
    priceScaleId: '',
    scaleMargins: {
      top: 0.8,
      bottom: 0
    }
  })

  // 响应式调整
  const resizeObserver = new ResizeObserver(entries => {
    if (chart && chartContainer.value) {
      const { width, height } = entries[0].contentRect
      chart.applyOptions({ width, height })
    }
  })

  resizeObserver.observe(chartContainer.value)

  emit('ready')
}

// 更新图表数据
const updateChartData = () => {
  if (!chart || !priceSeries || !avgPriceSeries || !volumeSeries) return

  const data = displayData.value
  if (!data || data.length === 0) return

  // 转换价格线数据
  const priceData: LineData[] = data.map(item => ({
    time: (new Date(item.time).getTime() / 1000) as Time,
    value: item.price
  }))

  // 转换均价线数据
  const avgPriceData: LineData[] = data.map(item => ({
    time: (new Date(item.time).getTime() / 1000) as Time,
    value: item.avg_price
  }))

  // 转换成交量数据
  const prevPrice = prevClose.value || data[0]?.price || 0
  const volumeData: HistogramData[] = data.map(item => ({
    time: (new Date(item.time).getTime() / 1000) as Time,
    value: item.volume,
    color: item.price >= prevPrice ? colors.volumeUp : colors.volumeDown
  }))

  // 设置数据
  priceSeries.setData(priceData)
  avgPriceSeries.setData(avgPriceData)
  volumeSeries.setData(volumeData)

  // 更新当前价格
  if (data.length > 0) {
    const latest = data[data.length - 1]
    currentPrice.value = latest.price
    if (prevClose.value > 0) {
      priceChange.value = ((latest.price - prevClose.value) / prevClose.value) * 100
    }
    currentTime.value = new Date(latest.time).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 自适应视图
  chart.timeScale().fitContent()
}

// 获取分时数据
const fetchIntradayData = async () => {
  if (!props.stockCode) return

  try {
    // 请求1分钟K线数据作为分时数据
    const response = await fetch(`/api/v1/core/stock/${props.stockCode}/kline?period=1min&count=500`)
    const result = await response.json()

    if (result.data && result.data.length > 0) {
      // 转换数据格式
      internalData.value = result.data.map((item: any) => ({
        time: item.date,
        price: item.close,
        volume: item.volume,
        avg_price: item.amount / (item.volume || 1) // 简化计算均价
      }))

      // 设置昨收价
      if (result.data.length > 1) {
        prevClose.value = result.data[0].close // 使用第一根K线的收盘价作为昨收价的近似
      }

      updateChartData()
    }
  } catch (error) {
    console.error('获取分时数据失败:', error)
  }
}

// 重置图表
const resetChart = () => {
  if (chart) {
    chart.timeScale().fitContent()
  }
}

// 监听数据变化
watch(() => displayData.value, () => {
  updateChartData()
}, { deep: true })

// 组件挂载
onMounted(() => {
  initChart()
  fetchIntradayData()
})

// 组件卸载
onUnmounted(() => {
  if (chart) {
    chart.remove()
    chart = null
  }
})

// 暴露方法
defineExpose({
  resetChart,
  refreshData: fetchIntradayData
})
</script>

<style scoped>
.intraday-container {
  position: relative;
  width: 100%;
  background: #0f0f23;
  border-radius: 8px;
  overflow: hidden;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #1a1a2e;
  border-bottom: 1px solid #252530;
  min-height: 50px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stock-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stock-name {
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc;
}

.stock-code {
  font-size: 12px;
  color: #cbd5e1;
}

.price-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.current-price {
  font-size: 18px;
  font-weight: 700;
  font-family: 'Roboto Mono', monospace;
}

.price-change {
  font-size: 12px;
  font-family: 'Roboto Mono', monospace;
}

.price-time {
  font-size: 11px;
  color: #6b7280;
}

.price-up {
  color: #ef4444;
}

.price-down {
  color: #10b981;
}

.price-flat {
  color: #6b7280;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: #252530;
  border: 1px solid #374151;
  color: #f8fafc;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
}

.action-btn:hover {
  background: #374151;
}

/* 图表容器 */
.chart {
  width: 100%;
}

/* 加载状态 */
.chart-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(15, 15, 35, 0.9);
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #252530;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.chart-loading p {
  margin-top: 12px;
  color: #f8fafc;
  font-size: 14px;
}
</style>
