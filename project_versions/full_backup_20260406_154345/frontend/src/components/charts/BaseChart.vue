<template>
  <div ref="chartContainer" class="base-chart" :style="{ width, height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface Props {
  option: EChartsOption
  width?: string
  height?: string
  theme?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '400px',
  theme: 'dark',
  loading: false
})

const emit = defineEmits<{
  ready: []
  click: [params: any]
}>()

const chartContainer = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartContainer.value) return
  
  // 销毁已存在的实例
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  // 创建新实例
  chartInstance = echarts.init(chartContainer.value, props.theme)
  
  // 设置配置
  chartInstance.setOption(props.option)
  
  // 绑定事件
  chartInstance.on('click', (params) => {
    emit('click', params)
  })
  
  emit('ready')
}

const updateChart = () => {
  if (chartInstance) {
    chartInstance.setOption(props.option, true)
  }
}

const showLoading = () => {
  if (chartInstance) {
    chartInstance.showLoading('default', {
      text: '加载中...',
      color: '#2563eb',
      textColor: '#f8fafc',
      maskColor: 'rgba(0, 0, 0, 0.8)'
    })
  }
}

const hideLoading = () => {
  if (chartInstance) {
    chartInstance.hideLoading()
  }
}

const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 监听配置变化
watch(() => props.option, () => {
  updateChart()
}, { deep: true })

// 监听加载状态
watch(() => props.loading, (loading) => {
  if (loading) {
    showLoading()
  } else {
    hideLoading()
  }
})

// 监听主题变化
watch(() => props.theme, () => {
  initChart()
})

onMounted(() => {
  nextTick(() => {
    initChart()
    
    // 监听窗口大小变化
    window.addEventListener('resize', resizeChart)
  })
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  
  window.removeEventListener('resize', resizeChart)
})

// 暴露方法给父组件
defineExpose({
  getChart: () => chartInstance,
  resize: resizeChart,
  showLoading,
  hideLoading
})
</script>

<style lang="scss" scoped>
.base-chart {
  min-height: 300px;
}
</style>