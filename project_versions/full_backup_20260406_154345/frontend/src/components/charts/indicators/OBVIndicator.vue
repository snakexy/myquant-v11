/**
 * OBV 指标组件
 * 简化版：只显示 OBV 线（暂时不支持柱状图）
 */

<template>
  <div ref="chartContainer" class="obv-indicator"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { createChart } from 'lightweight-charts'
import type { IChartApi, IChartSeriesApi, Time } from 'lightweight-charts'

interface Props {
  data?: {
    obv: number[]
    volume: number[]
    datetime: string[]
  }
  width: number
  height: number
  color?: string
  showVolume?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  color: '#607D8B',
  showVolume: false
})

const chartContainer = ref<HTMLElement>()
let chart: IChartApi | null = null
let obvSeries: IChartSeriesApi | null = null

const initChart = () => {
  if (!chartContainer.value) return

  console.log('[OBVIndicator] 初始化图表')

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

  // OBV 线
  obvSeries = chart.addLineSeries({
    color: props.color,
    lineWidth: 2,
    priceLineVisible: false,
    lastPriceAnimation: 1
  })

  console.log('[OBVIndicator] 系列已创建')
  updateChart()
}

const updateChart = () => {
  if (!chart || !props.data || !props.data.obv || props.data.obv.length === 0) {
    console.log('[OBVIndicator] 没有数据，跳过更新')
    return
  }

  const data = props.data
  console.log('[OBVIndicator] 更新图表, 数据量:', data.obv.length)

  const timeData: Time[] = data.datetime.map((d) => {
    const timestamp = Math.floor(new Date(d).getTime() / 1000)
    return timestamp as Time
  })

  // 过滤 null/NaN 值
  const obvData = data.obv
    .map((val, i) => ({ time: timeData[i], value: val }))
    
  obvSeries?.setData(obvData)

  console.log('[OBVIndicator] 图表已更新')
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

watch(() => props.data, (newData) => {
  console.log('[OBVIndicator] props.data 变化:', {
    hasData: !!newData,
    hasObv: !!newData?.obv,
    obvLength: newData?.obv?.length || 0
  })
  updateChart()
}, { deep: true })

watch(() => [props.width, props.height], () => {
  if (chart) {
    chart.applyOptions({ width: props.width, height: props.height })
  }
})

onMounted(() => {
  console.log('[OBVIndicator] onMounted')
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
.obv-indicator {
  width: 100%;
  height: 100%;
}
</style>
