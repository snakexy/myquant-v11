/**
 * 顶底背离指标组件
 * 显示风险值、买卖信号、背离标记
 */

<template>
  <div ref="chartContainer" class="topbottom-indicator"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { createChart } from 'lightweight-charts'
import type { IChartApi, IChartSeriesApi, Time } from 'lightweight-charts'

interface Props {
  data?: {
    risk_value_34?: number[]
    risk_value_170?: number[]
    risk_value_1020?: number[]
    buy_signal?: number[]
    sell_signal?: number[]
    macd_div_top?: number[]
    macd_div_bottom?: number[]
    kdj_div_top?: number[]
    kdj_div_bottom?: number[]
    rsi_div_top?: number[]
    rsi_div_bottom?: number[]
    datetime: string[]
  }
  width: number
  height: number
}

const props = withDefaults(defineProps<Props>(), {
  width: 0,
  height: 150
})

const chartContainer = ref<HTMLElement>()
let chart: IChartApi | null = null
let risk34Series: IChartSeriesApi | null = null
let risk170Series: IChartSeriesApi | null = null
let buyMarkers: any[] = []
let sellMarkers: any[] = []

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
      visible: true,
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
    }
  })

  // 超买超卖区域线
  chart.addLineSeries({
    priceLine: {
      price: 80,
      color: 'rgba(244, 67, 54, 0.5)',
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: true
    }
  })

  chart.addLineSeries({
    priceLine: {
      price: 20,
      color: 'rgba(76, 175, 80, 0.5)',
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: true
    }
  })

  // 风险值34（主线）
  risk34Series = chart.addLineSeries({
    color: '#2196F3',
    lineWidth: 2,
    title: '风险值'
  })

  // 风险值170（副线）
  risk170Series = chart.addLineSeries({
    color: '#FF9800',
    lineWidth: 1,
    title: '风险5'
  })

  updateChart()
}

const updateChart = () => {
  if (!chart || !props.data || !props.data.datetime) return

  const data = props.data
  const timeData: Time[] = data.datetime.map((d) => {
    const timestamp = Math.floor(new Date(d).getTime() / 1000)
    return timestamp as Time
  })

  // 风险值34数据
  if (data.risk_value_34) {
    const risk34Data = data.risk_value_34
      .map((val, i) => ({ time: timeData[i], value: val }))
      .filter(d => !isNaN(d.value))
    risk34Series?.setData(risk34Data)
  }

  // 风险值170数据
  if (data.risk_value_170) {
    const risk170Data = data.risk_value_170
      .map((val, i) => ({ time: timeData[i], value: val }))
      .filter(d => !isNaN(d.value))
    risk170Series?.setData(risk170Data)
  }

  // 添加买卖信号标记
  if (data.buy_signal && risk34Series) {
    const buySignals = data.buy_signal
      .map((signal, i) => ({ time: timeData[i], value: signal, index: i }))
      .filter(d => d.value === 1 && !isNaN(d.time))

    // 清除旧标记
    buyMarkers.forEach(m => m.remove())
    buyMarkers = []

    buySignals.forEach(signal => {
      if (data.risk_value_34 && data.risk_value_34[signal.index]) {
        const marker = risk34Series.createPriceLine({
          price: data.risk_value_34[signal.index],
          color: '#4CAF50',
          lineWidth: 2,
          lineStyle: 2,
          axisLabelVisible: false
        })
        buyMarkers.push(marker)
      }
    })
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
.topbottom-indicator {
  width: 100%;
  height: 100%;
}
</style>
