<template>
  <div class="radar-chart-container">
    <div v-if="title" class="chart-header">
      <div class="chart-title">
        <svg class="icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15 8.5 22 9 17 14 18.5 21 12 17.5 5.5 21 7 14 2 9 9 2 12 2"/>
        </svg>
        {{ title }}
      </div>
    </div>
    <div ref="chartRef" class="chart-content"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  title?: string
  indicator?: { name: string; max: number }[]
  data?: number[]
  benchmark?: number[]
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  indicator: () => [
    { name: '收益', max: 100 },
    { name: '夏普', max: 100 },
    { name: '稳定性', max: 100 },
    { name: '容量', max: 100 },
    { name: '成本', max: 100 },
    { name: '回撤', max: 100 }
  ],
  data: () => [85, 80, 75, 70, 65, 72],
  benchmark: () => [70, 65, 60, 55, 50, 60],
  color: '#2962ff'
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, 'dark')

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e222d',
      borderColor: '#363a45',
      textStyle: { color: '#d1d4dc' }
    },
    legend: {
      show: true,
      top: 0,
      right: 10,
      orient: 'vertical',
      itemWidth: 12,
      itemHeight: 6,
      textStyle: { color: '#787b86', fontSize: 10 },
      data: [
        { name: '策略', icon: 'roundRect' },
        { name: '基准', icon: 'roundRect' }
      ]
    },
    radar: {
      indicator: props.indicator,
      shape: 'polygon',
      splitNumber: 4,
      center: ['50%', '50%'],
      radius: '85%',
      axisNameGap: 3,
      axisName: {
        color: '#787b86',
        fontSize: 10
      },
      splitLine: {
        lineStyle: { color: '#2a2e39' }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['#1e222d', '#1e222d']
        }
      },
      axisLine: {
        lineStyle: { color: '#363a45' }
      }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: props.data,
            name: '策略',
            areaStyle: {
              color: `${props.color}30`
            },
            lineStyle: {
              color: props.color,
              width: 2
            },
            itemStyle: {
              color: props.color
            }
          },
          {
            value: props.benchmark,
            name: '基准',
            areaStyle: {
              color: '#787b8630'
            },
            lineStyle: {
              color: '#787b86',
              width: 2,
              type: 'dashed'
            },
            itemStyle: {
              color: '#787b86'
            }
          }
        ]
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

watch(() => [props.data, props.benchmark], initChart, { deep: true })
</script>

<style lang="scss" scoped>
.radar-chart-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: visible;
}

.chart-header {
  flex-shrink: 0;
  padding-bottom: 12px;
}

.chart-title {
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-md {
  width: 18px;
  height: 18px;
  color: #ff9800;
}

.chart-content {
  width: 100%;
  flex: 1;
  min-height: 180px;
}
</style>
