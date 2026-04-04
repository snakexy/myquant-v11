<template>
  <div class="chart-card">
    <div class="chart-header">
      <div class="chart-title">
        <svg class="icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="16"></line>
          <line x1="8" y1="12" x2="16" y2="12"></line>
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
  data?: { name: string; value: number }[]
  colors?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [
    { name: '动量', value: 35 },
    { name: '价值', value: 25 },
    { name: '质量', value: 20 },
    { name: '低波动', value: 20 }
  ],
  colors: () => ['#2962ff', '#26a69a', '#9c27b0', '#ff9800']
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 检测容器宽度，返回是否需要水平布局
const needsHorizontalLayout = (containerWidth: number) => {
  return containerWidth < 200
}

const initChart = () => {
  if (!chartRef.value) return

  // 每次都销毁旧实例，确保尺寸正确
  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value, 'dark')

  // 获取容器实际尺寸
  const containerWidth = chartRef.value.clientWidth || 150
  const containerHeight = chartRef.value.clientHeight || 150

  // 根据容器尺寸决定布局
  const horizontal = needsHorizontalLayout(containerWidth)

  // 根据容器尺寸动态计算饼图半径
  const minDim = Math.min(containerWidth, containerHeight)
  const outerRadius = Math.min(minDim * 0.35, 70)
  const innerRadius = outerRadius * 0.65

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e222d',
      borderColor: '#363a45',
      textStyle: { color: '#d1d4dc' }
    },
    legend: {
      orient: 'horizontal',
      right: 'auto',
      left: 'center',
      top: 'auto',
      bottom: 0,
      textStyle: { color: '#d1d4dc', fontSize: 10 },
      itemWidth: 8,
      itemHeight: 8,
      formatter: (name: string) => {
        const item = props.data.find(d => d.name === name)
        if (item) {
          return `${name} ${item.value}%`
        }
        return name
      }
    },
    series: [
      {
        type: 'pie',
        radius: [`${innerRadius}px`, `${outerRadius}px`],
        center: ['50%', '40%'],
        avoidLabelOverlap: false,
        label: { show: false },
        labelLine: { show: false },
        animationType: 'scale',
        animationEasing: 'elasticOut',
        animationDelay: (idx: number) => idx * 100,
        data: props.data.map((item, index) => ({
          name: item.name,
          value: item.value,
          itemStyle: { color: props.colors[index] }
        }))
      }
    ]
  }

  chartInstance.setOption(option)
}

const resizeChart = () => {
  initChart() // 重新初始化以适应屏幕变化
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
.chart-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 20px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.chart-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
