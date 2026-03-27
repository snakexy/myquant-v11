<template>
  <el-card class="chart-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">📈 收益曲线</span>
        <div class="actions">
          <el-radio-group v-model="selectedPeriod" size="small" @change="handlePeriodChange">
            <el-radio-button label="day">1日</el-radio-button>
            <el-radio-button label="week">1周</el-radio-button>
            <el-radio-button label="month">1月</el-radio-button>
          </el-radio-group>
          <el-button size="small" @click="handleRefresh" :loading="loading">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </div>
    </template>

    <div class="chart-container">
      <div v-if="loading" class="chart-loading">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <div v-else-if="error" class="chart-error">
        <el-icon :size="32"><WarningFilled /></el-icon>
        <span>{{ error }}</span>
        <el-button size="small" @click="handleRefresh">重试</el-button>
      </div>
      <div v-else ref="chartRef" class="chart-content" :style="{ height: chartHeight }"></div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Loading, WarningFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { monitoringApi } from '@/api/modules/monitoring'
import type { ReturnCurvePoint, TimePeriod } from '@/api/modules/monitoring'

// Props
interface Props {
  chartHeight?: string
  autoRefresh?: boolean
  refreshInterval?: number // 秒
}

const props = withDefaults(defineProps<Props>(), {
  chartHeight: '400px',
  autoRefresh: false,
  refreshInterval: 60
})

// Emits
const emit = defineEmits<{
  dataLoaded: [data: ReturnCurvePoint[]]
  periodChange: [period: TimePeriod]
}>()

// State
const chartRef = ref<HTMLDivElement>()
const chartInstance = ref<echarts.ECharts>()
const selectedPeriod = ref<TimePeriod>('day')
const loading = ref(false)
const error = ref('')
const curveData = ref<ReturnCurvePoint[]>([])

let refreshTimer: number | null = null

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chartInstance.value = echarts.init(chartRef.value)
  updateChart()

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

// 更新图表
const updateChart = () => {
  if (!chartInstance.value || curveData.value.length === 0) return

  const times = curveData.value.map(point => {
    const date = new Date(point.time)
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  })

  const values = curveData.value.map(point => point.value)

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      },
      formatter: (params: any) => {
        const param = params[0]
        const value = param.value as number
        return `
          <div style="padding: 8px;">
            <div style="font-weight: 600; margin-bottom: 4px;">${param.axisValue}</div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="display: inline-block; width: 10px; height: 10px; background: ${param.color}; border-radius: 50%;"></span>
              <span>收益率:</span>
              <span style="font-weight: 600; color: ${value >= 0 ? '#f56c6c' : '#67c23a'};">
                ${value >= 0 ? '+' : ''}${value.toFixed(2)}%
              </span>
            </div>
          </div>
        `
      }
    },
    legend: {
      data: ['收益率'],
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: times,
      axisLine: {
        lineStyle: {
          color: '#e4e7ed'
        }
      },
      axisLabel: {
        color: '#909399',
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#e4e7ed'
        }
      },
      axisLabel: {
        formatter: '{value}%',
        color: '#909399',
        fontSize: 12
      },
      splitLine: {
        lineStyle: {
          color: '#f2f3f5',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '收益率',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        data: values,
        itemStyle: {
          color: (params: any) => {
            return params.value >= 0 ? '#f56c6c' : '#67c23a'
          }
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
            ]
          }
        },
        lineStyle: {
          width: 2,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#409eff' },
              { offset: 1, color: '#67c23a' }
            ]
          }
        }
      }
    ]
  }

  chartInstance.value.setOption(option)
}

// 加载收益曲线数据
const loadReturnCurve = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await monitoringApi.getReturnCurve(selectedPeriod.value)
    if (response.code === 200) {
      curveData.value = response.data
      emit('dataLoaded', response.data)

      if (response.data.length === 0) {
        error.value = '暂无数据'
      } else {
        await nextTick()
        updateChart()
      }
    } else {
      error.value = '加载失败'
      ElMessage.error('加载收益曲线失败')
    }
  } catch (err) {
    console.error('加载收益曲线失败:', err)
    error.value = '加载失败'
    // 使用模拟数据作为降级方案
    curveData.value = generateMockData()
    await nextTick()
    updateChart()
    ElMessage.warning('使用模拟数据')
  } finally {
    loading.value = false
  }
}

// 生成模拟数据
const generateMockData = (): ReturnCurvePoint[] => {
  const data: ReturnCurvePoint[] = []
  const now = new Date()
  let value = 0

  const points = selectedPeriod.value === 'day' ? 24 : selectedPeriod.value === 'week' ? 7 : 30

  for (let i = points; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    value += (Math.random() - 0.45) * 2 // -0.9 to 1.1
    data.push({
      time: time.toISOString(),
      value: parseFloat(value.toFixed(2))
    })
  }

  return data
}

// 时间周期切换
const handlePeriodChange = () => {
  emit('periodChange', selectedPeriod.value)
  loadReturnCurve()
}

// 刷新
const handleRefresh = () => {
  loadReturnCurve()
}

// 窗口大小变化处理
const handleResize = () => {
  chartInstance.value?.resize()
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (!props.autoRefresh) return

  refreshTimer = window.setInterval(() => {
    loadReturnCurve()
  }, props.refreshInterval * 1000)
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(async () => {
  await nextTick()
  initChart()
  await loadReturnCurve()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  window.removeEventListener('resize', handleResize)
  chartInstance.value?.dispose()
})

// 暴露方法给父组件
defineExpose({
  refresh: loadReturnCurve,
  getData: () => curveData.value,
  getChart: () => chartInstance.value
})
</script>

<style scoped lang="scss">
.chart-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }

    .actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .chart-container {
    position: relative;

    .chart-loading,
    .chart-error {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12px;
      padding: 60px 20px;
      min-height: 400px;
      color: #909399;

      .el-icon {
        font-size: 32px;
      }

      span {
        font-size: 14px;
      }
    }

    .chart-content {
      width: 100%;
    }
  }
}
</style>
