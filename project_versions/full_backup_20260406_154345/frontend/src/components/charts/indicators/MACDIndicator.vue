/**
 * MACD 指标组件 - 使用正确的 lightweight-charts API
 */

<template>
  <div ref="chartContainer" class="macd-indicator"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { createChart, LineSeries, HistogramSeries } from 'lightweight-charts'
import type { IChartApi, Time } from 'lightweight-charts'

interface Props {
  data?: {
    macd: number[]
    signal: number[]
    histogram: number[]
    datetime: string[]
  }
  width: number
  height: number
  colors?: {
    macd?: string
    signal?: string
    histogramPositive?: string
    histogramNegative?: string
  }
}

const props = withDefaults(defineProps<Props>(), {
  colors: () => ({
    macd: '#2962FF',
    signal: '#FF6D00',
    histogramPositive: '#26A69A',
    histogramNegative: '#EF5350'
  })
})

const chartContainer = ref<HTMLElement>()
let chart: IChartApi | null = null
let macdSeries: ReturnType<typeof LineSeries> | null = null
let signalSeries: ReturnType<typeof LineSeries> | null = null
let histogramSeries: ReturnType<typeof HistogramSeries> | null = null

const initChart = () => {
  console.log('[MACD] initChart 被调用', chartContainer.value)
  if (!chartContainer.value) {
    console.log('[MACD] chartContainer 为空，跳过')
    return
  }

  chart = createChart(chartContainer.value, {
    width: props.width === 0 ? '100%' : props.width,
    height: props.height,
    layout: {
      background: { type: 'solid', color: '#131722' },
      textColor: '#B2B5BE'
    },
    rightPriceScale: {
      visible: true,
      borderVisible: false,
      width: 60,
      autoScale: true,
      scaleMargins: {
        top: 0.1,
        bottom: 0.1
      }
    },
    timeScale: {
      visible: false,
      borderColor: '#2A2E39'
    },
    grid: {
      vertLines: { visible: false },
      horzLines: { color: '#2A2E39' }
    },
    handleScale: false,
    handleScroll: false
  })

  // MACD 线
  macdSeries = chart.addSeries(LineSeries, {
    color: props.colors.macd,
    lineWidth: 2,
    priceLineVisible: false
  })

  // Signal 线
  signalSeries = chart.addSeries(LineSeries, {
    color: props.colors.signal,
    lineWidth: 2,
    priceLineVisible: false
  })

  // Histogram 柱状图
  histogramSeries = chart.addSeries(HistogramSeries, {
    color: props.colors.histogramNegative,
    priceFormat: {
      type: 'volume'
    },
    priceScaleId: ''
  })

  updateChart()
}

const updateChart = () => {
  if (!chart || !props.data || !props.data.macd) return

  const data = props.data

  const timeData: Time[] = data.datetime.map((d) => {
    const timestamp = Math.floor(new Date(d).getTime() / 1000)
    return timestamp as Time
  })

  // 过滤 null/None/NaN 值
  const macdData = data.macd
    .map((val, i) => ({ time: timeData[i], value: val }))
    .filter(item => item.value !== null && item.value !== undefined && !isNaN(item.value))
  macdSeries?.setData(macdData)

  const signalData = data.signal
    .map((val, i) => ({ time: timeData[i], value: val }))
    .filter(item => item.value !== null && item.value !== undefined && !isNaN(item.value))
  signalSeries?.setData(signalData)

  if (data.histogram && histogramSeries) {
    const histogramData = data.histogram
      .map((val, i) => ({
        time: timeData[i],
        value: Math.abs(val),
        color: val >= 0 ? props.colors.histogramPositive : props.colors.histogramNegative
      }))
      .filter(item => item.value !== null && item.value !== undefined && !isNaN(item.value))
    histogramSeries?.setData(histogramData)
  }
}

const resize = (width: number, height: number) => {
  if (chart) {
    chart.applyOptions({ width, height })
  }
}

const setVisibleLogicalRange = (range: any) => {
  if (chart && range && !isNaN(range.from) && !isNaN(range.to)) {
    try {
      chart.timeScale().setVisibleLogicalRange(range)
    } catch (e) {
      // 忽略设置范围时的错误
    }
  }
}

const getTimeScale = () => {
  return chart?.timeScale() || null
}

watch(() => props.data, updateChart, { deep: true })
watch(() => [props.width, props.height], () => {
  if (chart) {
    chart.applyOptions({ width: props.width, height: props.height })
  }
})

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
    chart = null
  }
})

defineExpose({ resize, setVisibleLogicalRange, getTimeScale })
</script>

<style scoped>
.macd-indicator {
  width: 100%;
  height: 100%;
}
</style>
