/**
 * KDJ 指标组件
 */

<template>
  <div ref="chartContainer" class="kdj-indicator"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { createChart } from 'lightweight-charts'
import type { IChartApi, IChartSeriesApi, Time } from 'lightweight-charts'

interface Props {
  data?: {
    k: number[]
    d: number[]
    j: number[]
    datetime: string[]
  }
  width: number
  height: number
  colors?: {
    k?: string
    d?: string
    j?: string
    overbought?: string
    oversold?: string
  }
  overbought?: number
  oversold?: number
}

const props = withDefaults(defineProps<Props>(), {
  colors: () => ({
    k: '#2962FF',
    d: '#FF6D00',
    j: '#26A69A',
    overbought: 'rgba(255, 77, 77, 0.3)',
    oversold: 'rgba(77, 255, 77, 0.3)'
  }),
  overbought: 80,
  oversold: 20
})

const chartContainer = ref<HTMLElement>()
let chart: IChartApi | null = null
let kSeries: IChartSeriesApi | null = null
let dSeries: IChartSeriesApi | null = null
let jSeries: IChartSeriesApi | null = null

const initChart = () => {
  if (!chartContainer.value) return

  chart = createChart(chartContainer.value, {
    width: props.width === 0 ? '100%' : props.width,
    height: props.height,
    layout: {
      background: { type: 'solid', color: '#131722' },
      textColor: '#B2B5BE'
    },
    rightPriceScale: {
      visible: false
    },
    timeScale: {
      visible: false,
      borderColor: '#2A2E39'
    },
    grid: {
      vertLines: { visible: false },
      horzLines: { color: '#2A2E39' }
    }
  })

  // 添加超买超卖区域
  chart.addLineSeries({
    priceLine: {
      price: props.overbought,
      color: props.colors.overbought,
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: false
    }
  })

  chart.addLineSeries({
    priceLine: {
      price: props.oversold,
      color: props.colors.oversold,
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: false
    }
  })

  // K 线
  kSeries = chart.addLineSeries({
    color: props.colors.k,
    lineWidth: 2
  })

  // D 线
  dSeries = chart.addLineSeries({
    color: props.colors.d,
    lineWidth: 2
  })

  // J 线
  jSeries = chart.addLineSeries({
    color: props.colors.j,
    lineWidth: 2
  })

  updateChart()
}

const updateChart = () => {
  if (!chart || !props.data || !props.data.k) return

  const data = props.data
  const timeData: Time[] = data.datetime.map((d) => {
    const timestamp = Math.floor(new Date(d).getTime() / 1000)
    return timestamp as Time
  })

  // 过滤 null/NaN 值
  const kData = data.k
    .map((val, i) => ({ time: timeData[i], value: val }))
    
  const dData = data.d
    .map((val, i) => ({ time: timeData[i], value: val }))
    
  const jData = data.j
    .map((val, i) => ({ time: timeData[i], value: val }))
    

  kSeries?.setData(kData)
  dSeries?.setData(dData)
  jSeries?.setData(jData)
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
      // 忽略设置范围时的错误（数据可能未完全加载）
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
.kdj-indicator {
  width: 100%;
  height: 100%;
}
</style>
