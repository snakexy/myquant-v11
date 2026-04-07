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
    k?: number[]      // KDJ的k值
    d?: number[]      // KDJ的d值
    j?: number[]      // KDJ的j值
    sk?: number[]     // SKDJ的sk值
    sd?: number[]     // SKDJ的sd值
    sj?: number[]     // SKDJ的sj值
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
  if (!chart || !props.data) return

  const data = props.data

  // 判断是KDJ还是SKDJ数据格式
  const isSKDJ = data.sk !== undefined

  if (!isSKDJ && !data.k) return

  const timeData: Time[] = data.datetime.map((d) => {
    const timestamp = Math.floor(new Date(d).getTime() / 1000)
    return timestamp as Time
  })

  // 根据数据格式选择对应的字段
  const kData = (isSKDJ ? data.sk : data.k)
    .map((val, i) => ({ time: timeData[i], value: val }))

  const dData = (isSKDJ ? data.sd : data.d)
    .map((val, i) => ({ time: timeData[i], value: val }))

  const jData = (isSKDJ ? data.sj : data.j)
    .map((val, i) => ({ time: timeData[i], value: val }))


  kSeries?.setData(kData)
  dSeries?.setData(dData)

  // SKDJ可能没有SJ值，只有KDJ才有J值
  if (isSKDJ && data.sj) {
    jSeries?.setData(jData)
  } else if (!isSKDJ && data.j) {
    jSeries?.setData(jData)
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
