<template>
  <div class="feature-importance-chart">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Histogram /></el-icon>
          <span>特征重要性</span>
          <div class="header-controls">
            <el-select v-model="chartType" size="small">
              <el-option label="柱状图" value="bar" />
              <el-option label="横向柱状图" value="horizontal" />
              <el-option label="饼图" value="pie" />
            </el-select>
            <el-input-number
              v-model="topN"
              :min="5"
              :max="50"
              size="small"
              controls-position="right"
              style="width: 120px"
            />
          </div>
        </div>
      </template>

      <div class="chart-content">
        <!-- 柱状图 -->
        <div v-if="chartType === 'bar'" ref="barChartRef" class="chart-container"></div>

        <!-- 横向柱状图 -->
        <div v-if="chartType === 'horizontal'" ref="horizontalChartRef" class="chart-container"></div>

        <!-- 饼图 -->
        <div v-if="chartType === 'pie'" ref="pieChartRef" class="chart-container"></div>

        <!-- 数据表格 -->
        <div class="feature-table">
          <el-table
            :data="topFeatures"
            stripe
            max-height="300"
            style="width: 100%"
          >
            <el-table-column type="index" label="#" width="60" />
            <el-table-column prop="feature" label="特征名称" />
            <el-table-column prop="importance" label="重要性" width="150" sortable>
              <template #default="{ row }">
                <span class="importance-value">{{ row.importance.toFixed(4) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="占比" width="120" sortable>
              <template #default="{ row }">
                <span class="percentage-value">{{ (row.importance * 100).toFixed(2) }}%</span>
              </template>
            </el-table-column>
            <el-table-column label="重要性等级" width="120">
              <template #default="{ row }">
                <el-tag :type="getImportanceLevel(row.importance)">
                  {{ getImportanceLabel(row.importance) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { Histogram } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Props ====================

interface FeatureData {
  feature: string
  importance: number
}

interface Props {
  data?: Record<string, number>
  topN?: number
}

const props = withDefaults(defineProps<Props>(), {
  topN: 15
})

// ==================== 数据 ====================

const chartType = ref<'bar' | 'horizontal' | 'pie'>('bar')
const topN = ref(props.topN)

// ==================== 计算属性 ====================

const features = computed(() => {
  if (!props.data) return []

  return Object.entries(props.data)
    .map(([feature, importance]) => ({ feature, importance }))
    .sort((a, b) => b.importance - a.importance)
})

const topFeatures = computed(() => {
  return features.value.slice(0, topN.value).map((item, index) => ({
    ...item,
    percentage: item.importance / features.value.reduce((sum, f) => sum + f.importance, 0)
  }))
})

const totalImportance = computed(() => {
  return features.value.reduce((sum, f) => sum + f.importance, 0)
})

// ==================== 方法 ====================

/**
 * 获取重要性等级
 */
const getImportanceLevel = (importance: number) => {
  const percentile = importance / totalImportance.value

  if (percentile > 0.2) return 'danger'
  if (percentile > 0.1) return 'warning'
  if (percentile > 0.05) return ''
  return 'info'
}

/**
 * 获取重要性标签
 */
const getImportanceLabel = (importance: number) => {
  const percentile = importance / totalImportance.value

  if (percentile > 0.2) return '非常重要'
  if (percentile > 0.1) return '重要'
  if (percentile > 0.05) return '一般'
  return '较低'
}

/**
 * 初始化柱状图
 */
const initBarChart = () => {
  const chartRef = document.querySelector('.chart-container') as HTMLElement
  if (!chartRef) return

  const chart = echarts.init(chartRef)

  const option = {
    title: {
      text: `Top ${topN.value} 特征重要性`,
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
      name: '特征',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: {
        color: '#94a3b8',
        rotate: 45,
        interval: 0,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: '重要性',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    series: [{
      name: '重要性',
      type: 'bar',
      data: topFeatures.value.map(f => f.importance),
      itemStyle: {
        color: (params: any) => {
          const colors = [
            '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b',
            '#ef4444', '#ec4899', '#8b5cf6', '#3b82f6',
            '#10b981', '#f59e0b', '#ef4444', '#ec4899'
          ]
          return colors[params.dataIndex % colors.length]
        }
      },
      label: {
        show: true,
        position: 'top',
        formatter: (params: any) => params.value.toFixed(4)
      }
    }]
  }

  chart.setOption(option)
}

/**
 * 初始化横向柱状图
 */
const initHorizontalChart = () => {
  const chartRef = document.querySelector('.chart-container') as HTMLElement
  if (!chartRef) return

  const chart = echarts.init(chartRef)

  const option = {
    title: {
      text: `Top ${topN.value} 特征重要性`,
      textStyle: { color: '#cbd5e1', fontSize: 14 },
      left: 'center'
    },
    grid: {
      left: '15%',
      right: '5%',
      top: '15%',
      bottom: '10%'
    },
    xAxis: {
      type: 'value',
      name: '重要性',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    yAxis: {
      type: 'category',
      name: '特征',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' },
      data: topFeatures.value.map(f => f.feature),
      inverse: true
    },
    series: [{
      name: '重要性',
      type: 'bar',
      data: topFeatures.value.map(f => f.importance),
      itemStyle: {
        color: (params: any) => {
          const importance = params.value as number
          if (importance > 0.1) return '#ef4444'
          if (importance > 0.05) return '#f59e0b'
          if (importance > 0.02) return '#8b5cf6'
          return '#3b82f6'
        }
      }
    }]
  }

  chart.setOption(option)
}

/**
 * 初始化饼图
 */
const initPieChart = () => {
  const chartRef = document.querySelector('.chart-container') as HTMLElement
  if (!chartRef) return

  const chart = echarts.init(chartRef)

  const option = {
    title: {
      text: '特征重要性分布',
      textStyle: { color: '#cbd5e1', fontSize: 14 },
      left: 'center'
    },
    grid: {
      left: '5%',
      right: '5%',
      top: '15%',
      bottom: '10%'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}{a}</b>: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: '#cbd5e1', fontSize: 11 }
    },
    series: [{
      name: '特征重要性',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      data: topFeatures.value.map(f => ({
        name: f.feature,
        value: f.importance
      })),
      itemStyle: {
        borderRadius: 6,
        borderColor: '#1a1a2e',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: (params: any) => {
          if (params.percent > 5) {
            return params.name
          }
          return ''
        }
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      }
    }]
  }

  chart.setOption(option)
}

/**
 * 初始化图表
 */
const initChart = () => {
  nextTick(() => {
    if (chartType.value === 'bar') {
      initBarChart()
    } else if (chartType.value === 'horizontal') {
      initHorizontalChart()
    } else if (chartType.value === 'pie') {
      initPieChart()
    }
  })
}

watch(() => chartType, () => {
  initChart()
})

watch(() => topN, () => {
  initChart()
})

onMounted(() => {
  initChart()
})
</script>

<style scoped lang="scss">
.feature-importance-chart {
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
      gap: 12px;
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

  .feature-table {
    .importance-value,
    .percentage-value {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 500;
    }

    .importance-value {
      color: var(--primary);
    }

    .percentage-value {
      color: #8b5cf6;
    }
  }
}
</style>
