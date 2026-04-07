<template>
  <div class="bar-chart-container">
    <div v-if="title" class="chart-header">
      <div class="chart-title">{{ title }}</div>
    </div>
    <div ref="chartRef" class="chart-content"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  title?: string
  data?: { name: string; value: number }[]
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [
    { name: 'Sharpe', value: 85 },
    { name: 'Calmar', value: 72 },
    { name: '收益', value: 90 },
    { name: '波动', value: 65 },
    { name: '回撤', value: 78 }
  ],
  color: '#2962ff'
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, 'dark')

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    grid: {
      top: 20,
      bottom: 30,
      left: 50,
      right: 20
    },
    xAxis: {
      type: 'category',
      data: props.data.map(item => item.name),
      axisLine: { lineStyle: { color: '#363a45' } },
      axisLabel: { color: '#787b86', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#2a2e39' } },
      axisLabel: { color: '#787b86' }
    },
    series: [
      {
        type: 'bar',
        data: props.data.map(item => item.value),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: props.color },
            { offset: 1, color: `${props.color}40` }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '60%'
      }
    ]
  }

  chartInstance.setOption(option)
}

const resizeChart = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})

watch(() => props.data, initChart, { deep: true })
</script>

<style lang="scss" scoped>
.bar-chart-container {
  width: 100%;
  height: 100%;
}

.chart-header {
  padding-bottom: 12px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
}

.chart-content {
  width: 100%;
  height: 200px;
}
</style>
