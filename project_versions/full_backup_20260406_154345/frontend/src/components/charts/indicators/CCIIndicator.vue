/**
 * CCI 指标组件
 */

<template>
  <div ref="chartContainer" class="cci-indicator"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { createChart } from 'lightweight-charts'
import type { IChartApi, IChartSeriesApi, Time } from 'lightweight-charts'

interface Props {
  data?: {
    cci: number[]
    datetime: string[]
  }
  width: number
  height: number
  color?: string
  overbought?: number
  oversold?: number
}

const props = withDefaults(defineProps<Props>(), {
  color: '#E91E63',
  overbought: 100,
  oversold: -100
})

const chartContainer = ref<HTMLElement>()
let chart: IChartApi | null = null
let cciSeries: IChartSeriesApi | null = null

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

  // 超买超卖线
  chart.addLineSeries({
    priceLine: {
      price: props.overbought,
      color: 'rgba(239, 68, 68, 0.5)',
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: false
    }
  })

  chart.addLineSeries({
    priceLine: {
      price: props.oversold,
      color: 'rgba(76, 175, 80, 0.5)',
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: false
    }
  })

  // CCI 线
  cciSeries = chart.addLineSeries({
    color: props.color,
    lineWidth: 2
  })

  updateChart()
}

const updateChart = () => {
  if (!chart || !props.data || !props.data.cci) return

  const data = props.data
  const timeData: Time[] = data.datetime.map((d) => {
    const timestamp = Math.floor(new Date(d).getTime() / 1000)
    return timestamp as Time
  })

  // 过滤 null/NaN 值
  const cciData = data.cci
    .map((val, i) => ({ time: timeData[i], value: val }))
    

  cciSeries?.setData(cciData)
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
.cci-indicator {
  width: 100%;
  height: 100%;
}
</style>
