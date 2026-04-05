<template>
  <div class="training-curve-chart">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><TrendCharts /></el-icon>
          <span>训练曲线</span>
          <div class="header-controls">
            <el-select v-model="chartType" size="small">
              <el-option label="单指标" value="single" />
              <el-option label="多指标对比" value="multi" />
            </el-select>
            <el-select v-model="selectedMetric" size="small">
              <el-option label="损失" value="loss" />
              <el-option label="准确率" value="accuracy" />
              <el-option label="IC/IR" value="ic" />
              <el-option label="奖励" value="reward" />
            </el-select>
            <el-select v-model="timeRange" size="small">
              <el-option label="全部" value="all" />
              <el-option label="最近50轮" value="50" />
              <el-option label="最近100轮" value="100" />
            </el-select>
          </div>
        </div>
      </template>

      <div class="chart-content">
        <!-- 单指标图表 -->
        <div v-if="chartType === 'single'" ref="singleChartRef" class="chart-container"></div>

        <!-- 多指标对比图表 -->
        <div v-if="chartType === 'multi'" ref="multiChartRef" class="chart-container"></div>

        <!-- 图例 -->
        <div class="legend-info">
          <div v-if="statistics" class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">最佳{{ selectedMetricLabel }}</span>
              <span class="stat-value">{{ formatValue(statistics.best) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均{{ selectedMetricLabel }}</span>
              <span class="stat-value">{{ formatValue(statistics.mean) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最差{{ selectedMetricLabel }}</span>
              <span class="stat-value">{{ formatValue(statistics.worst) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">标准差</span>
              <span class="stat-value">{{ formatValue(statistics.std) }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Props ====================

interface TrainingDataPoint {
  epoch: number
  loss?: number
  accuracy?: number
  precision?: number
  recall?: number
  f1?: number
  ic?: number
  rank_ic?: number
  reward?: number
}

interface Props {
  data?: TrainingDataPoint[]
}

const props = defineProps<Props>()

// ==================== 数据 ====================

const chartType = ref<'single' | 'multi'>('single')
const selectedMetric = ref<'loss' | 'accuracy' | 'ic' | 'reward'>('loss')
const timeRange = ref<'all' | '50' | '100'>('all')

// ==================== 计算属性 ====================

const selectedMetricLabel = computed(() => {
  const labels: Record<string, string> = {
    loss: '损失',
    accuracy: '准确率',
    ic: 'IC',
    reward: '奖励'
  }
  return labels[selectedMetric.value]
})

const filteredData = computed(() => {
  if (!props.data) return []

  if (timeRange.value === 'all') return props.data

  const limit = parseInt(timeRange.value)
  return props.data.slice(-limit)
})

const statistics = computed(() => {
  const data = filteredData.value
  if (data.length === 0) return null

  let getValue: (point: TrainingDataPoint) => number | undefined

  switch (selectedMetric.value) {
    case 'loss':
      getValue = (p) => p.loss
      break
    case 'accuracy':
      getValue = (p) => p.accuracy
      break
    case 'ic':
      getValue = (p) => p.ic
      break
    case 'reward':
      getValue = (p) => p.reward
      break
    default:
      return null
  }

  const values = data.map(getValue).filter((v): v is number => v !== undefined)

  if (values.length === 0) return null

  const best = Math.max(...values)
  const worst = Math.min(...values)
  const mean = values.reduce((sum, v) => sum + v, 0) / values.length
  const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length
  const std = Math.sqrt(variance)

  return { best, mean, worst, std }
})

// ==================== 方法 ====================

/**
 * 格式化数值
 */
const formatValue = (val: number | null) => {
  if (val === null) return '--'
  return val.toFixed(4)
}

/**
 * 初始化单指标图表
 */
const initSingleChart = () => {
  const chartRef = document.querySelector('.chart-container') as HTMLElement
  if (!chartRef) return

  const chart = echarts.init(chartRef)

  const xAxisData = filteredData.value.map(d => d.epoch)
  let seriesData: number[] = []
  let seriesName = ''
  let yAxisName = ''
  let color = '#8b5cf6'

  switch (selectedMetric.value) {
    case 'loss':
      seriesData = filteredData.value.map(d => d.loss || 0).filter(v => v !== undefined)
      seriesName = '损失'
      yAxisName = 'Loss'
      color = '#ef4444'
      break
    case 'accuracy':
      seriesData = filteredData.value.map(d => d.accuracy || 0).filter(v => v !== undefined)
      seriesName = '准确率'
      yAxisName = 'Accuracy'
      color = '#10b981'
      break
    case 'ic':
      seriesData = filteredData.value.map(d => d.ic || 0).filter(v => v !== undefined)
      seriesName = 'IC'
      yAxisName = 'IC'
      color = '#3b82f6'
      break
    case 'reward':
      seriesData = filteredData.value.map(d => d.reward || 0).filter(v => v !== undefined)
      seriesName = '奖励'
      yAxisName = 'Reward'
      color = '#8b5cf6'
      break
  }

  const option = {
    title: {
      text: `${seriesName}曲线`,
      textStyle: { color: '#cbd5e1', fontSize: 14 },
      left: 'center'
    },
    grid: {
      left: '10%',
      right: '5%',
      top: '15%',
      bottom: '10%'
    },
    xAxis: {
      type: 'category',
      name: '训练轮数',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: {
      type: 'value',
      name: yAxisName,
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    series: [{
      name: seriesName,
      type: 'line',
      smooth: true,
      data: seriesData,
      lineStyle: { color, width: 2 },
      itemStyle: { color },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: `${color}40` },
            { offset: 1, color: `${color}05` }
          ]
        }
      }
    }],
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        return `${params.name}<br/>轮数: ${params.name}<br/>值: ${params.value.toFixed(4)}`
      }
    }
  }

  chart.setOption(option)
}

/**
 * 初始化多指标对比图表
 */
const initMultiChart = () => {
  const chartRef = document.querySelector('.chart-container') as HTMLElement
  if (!chartRef) return

  const chart = echarts.init(chartRef)

  const xAxisData = filteredData.value.map(d => d.epoch)

  const series: any[] = []

  // 添加损失（反向显示）
  if (filteredData.value.some(d => d.loss !== undefined)) {
    series.push({
      name: '损失',
      type: 'line',
      smooth: true,
      data: filteredData.value.map(d => -(d.loss || 0)),
      lineStyle: { color: '#ef4444', width: 2 },
      itemStyle: { color: '#ef4444' }
    })
  }

  // 添加准确率
  if (filteredData.value.some(d => d.accuracy !== undefined)) {
    series.push({
      name: '准确率',
      type: 'line',
      smooth: true,
      data: filteredData.value.map(d => d.accuracy || 0),
      lineStyle: { color: '#10b981', width: 2 },
      itemStyle: { color: '#10b981' }
    })
  }

  // 添加IC
  if (filteredData.value.some(d => d.ic !== undefined)) {
    series.push({
      name: 'IC',
      type: 'line',
      smooth: true,
      data: filteredData.value.map(d => d.ic || 0),
      lineStyle: { color: '#3b82f6', width: 2 },
      itemStyle: { color: '#3b82f6' }
    })
  }

  // 添加奖励
  if (filteredData.value.some(d => d.reward !== undefined)) {
    series.push({
      name: '奖励',
      type: 'line',
      smooth: true,
      data: filteredData.value.map(d => d.reward || 0),
      lineStyle: { color: '#8b5cf6', width: 2 },
      itemStyle: { color: '#8b5cf6' }
    })
  }

  const option = {
    title: {
      text: '训练曲线对比',
      textStyle: { color: '#cbd5e1', fontSize: 14 },
      left: 'center'
    },
    grid: {
      left: '10%',
      right: '5%',
      top: '15%',
      bottom: '10%'
    },
    xAxis: {
      type: 'category',
      name: '训练轮数',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: {
      type: 'value',
      name: '指标值',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    legend: {
      data: series.map(s => s.name),
      textStyle: { color: '#cbd5e1' },
      top: '5%'
    },
    series: series,
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const value = params.seriesName === '损失' ? -params.value : params.value
        return `${params.seriesName}<br/>轮数: ${params.name}<br/>值: ${value.toFixed(4)}`
      }
    }
  }

  chart.setOption(option)
}

/**
 * 初始化图表
 */
const initChart = () => {
  nextTick(() => {
    if (chartType.value === 'single') {
      initSingleChart()
    } else if (chartType.value === 'multi') {
      initMultiChart()
    }
  })
}

watch(() => chartType, () => {
  initChart()
})

watch(() => selectedMetric, () => {
  initChart()
})

watch(() => timeRange, () => {
  initChart()
})

onMounted(() => {
  initChart()
})
</script>

<style scoped lang="scss">
.training-curve-chart {
  :deep(.el-card__body) {
    padding: 20px;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    font-weight: 500;
    color: var(--text-primary);

    .header-controls {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }
}

.chart-content {
  .chart-container {
    height: 400px;
    width: 100%;
    margin-bottom: 20px;
  }

  .legend-info {
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;

      .stat-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
        padding: 12px;
        background: var(--bg-elevated);
        border-radius: var(--radius-sm);

        .stat-label {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .stat-value {
          font-size: 16px;
          font-weight: 600;
          font-family: 'JetBrains Mono', monospace;
          color: var(--primary);
        }
      }
    }
  }
}
</style>
