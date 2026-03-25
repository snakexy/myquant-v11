<template>
  <div class="ml-metrics-chart">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>模型性能指标</span>
          <el-select v-model="selectedMetric" size="small" style="width: 150px">
            <el-option label="全部指标" value="all" />
            <el-option label="分类指标" value="classification" />
            <el-option label="回归指标" value="regression" />
            <el-option label="IC/IR" value="ic" />
          </el-select>
        </div>
      </template>

      <div class="chart-content">
        <!-- 分类指标 -->
        <div v-if="showClassificationMetrics" class="metrics-group">
          <h4 class="group-title">分类指标</h4>
          <div class="metrics-grid">
            <div
              v-for="metric in classificationMetrics"
              :key="metric.name"
              class="metric-item"
              :class="{ 'metric-highlight': metric.highlight }"
            >
              <div class="metric-value" :style="{ color: metric.color }">
                {{ formatMetricValue(metric.value) }}
              </div>
              <div class="metric-name">{{ metric.name }}</div>
              <div v-if="metric.delta !== undefined" class="metric-delta">
                <span :class="metric.delta > 0 ? 'positive' : 'negative'">
                  {{ metric.delta > 0 ? '+' : '' }}{{ metric.delta.toFixed(4) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 回归指标 -->
        <div v-if="showRegressionMetrics" class="metrics-group">
          <h4 class="group-title">回归指标</h4>
          <div class="metrics-grid">
            <div
              v-for="metric in regressionMetrics"
              :key="metric.name"
              class="metric-item"
              :class="{ 'metric-highlight': metric.highlight }"
            >
              <div class="metric-value" :style="{ color: metric.color }">
                {{ formatMetricValue(metric.value) }}
              </div>
              <div class="metric-name">{{ metric.name }}</div>
              <div v-if="metric.delta !== undefined" class="metric-delta">
                <span :class="metric.delta > 0 ? 'positive' : 'negative'">
                  {{ metric.delta > 0 ? '+' : '' }}{{ metric.delta.toFixed(4) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- IC/IR指标 -->
        <div v-if="showICMetrics" class="metrics-group">
          <h4 class="group-title">IC/IR 指标</h4>
          <div class="metrics-grid">
            <div
              v-for="metric in icMetrics"
              :key="metric.name"
              class="metric-item"
              :class="{ 'metric-highlight': metric.highlight }"
            >
              <div class="metric-value" :style="{ color: metric.color }">
                {{ formatMetricValue(metric.value) }}
              </div>
              <div class="metric-name">{{ metric.name }}</div>
              <div v-if="metric.delta !== undefined" class="metric-delta">
                <span :class="metric.delta > 0 ? 'positive' : 'negative'">
                  {{ metric.delta > 0 ? '+' : '' }}{{ metric.delta.toFixed(4) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 雷达图 -->
        <div v-if="showRadarChart" class="radar-section">
          <div ref="radarChartRef" class="radar-chart"></div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { DataAnalysis } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Props ====================

interface MetricsData {
  accuracy?: number
  precision?: number
  recall?: number
  f1?: number
  mse?: number
  mae?: number
  r2?: number
  ic?: number
  rank_ic?: number
}

interface Props {
  metrics?: MetricsData
  taskType?: 'classification' | 'regression'
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  taskType: 'classification',
  height: '400px'
})

// ==================== 数据 ====================

const selectedMetric = ref<'all' | 'classification' | 'regression' | 'ic'>('all')

// ==================== 计算属性 ====================

const showClassificationMetrics = computed(() => {
  return selectedMetric.value === 'all' || selectedMetric.value === 'classification'
})

const showRegressionMetrics = computed(() => {
  return selectedMetric.value === 'all' || selectedMetric.value === 'regression'
})

const showICMetrics = computed(() => {
  return selectedMetric.value === 'all' || selectedMetric.value === 'ic'
})

const showRadarChart = computed(() => {
  return selectedMetric.value === 'all'
})

const classificationMetrics = computed(() => {
  const metrics = props.metrics
  if (!metrics) return []

  const result = [
    {
      name: 'Accuracy',
      value: metrics.accuracy,
      color: getMetricColor(metrics.accuracy, 'accuracy'),
      highlight: metrics.accuracy !== undefined && metrics.accuracy > 0.8,
      delta: metrics.accuracy !== undefined ? metrics.accuracy - 0.75 : undefined
    },
    {
      name: 'Precision',
      value: metrics.precision,
      color: getMetricColor(metrics.precision, 'precision'),
      highlight: metrics.precision !== undefined && metrics.precision > 0.75
    },
    {
      name: 'Recall',
      value: metrics.recall,
      color: getMetricColor(metrics.recall, 'recall'),
      highlight: metrics.recall !== undefined && metrics.recall > 0.75
    },
    {
      name: 'F1 Score',
      value: metrics.f1,
      color: getMetricColor(metrics.f1, 'f1'),
      highlight: metrics.f1 !== undefined && metrics.f1 > 0.75
    }
  ]

  return result.filter(m => m.value !== undefined)
})

const regressionMetrics = computed(() => {
  const metrics = props.metrics
  if (!metrics) return []

  const result = [
    {
      name: 'MSE',
      value: metrics.mse,
      color: getMetricColor(metrics.mse, 'mse'),
      highlight: metrics.mse !== undefined && metrics.mse < 0.1
    },
    {
      name: 'MAE',
      value: metrics.mae,
      color: getMetricColor(metrics.mae, 'mae'),
      highlight: metrics.mae !== undefined && metrics.mae < 0.1
    },
    {
      name: 'R²',
      value: metrics.r2,
      color: getMetricColor(metrics.r2, 'r2'),
      highlight: metrics.r2 !== undefined && metrics.r2 > 0.8,
      delta: metrics.r2 !== undefined ? metrics.r2 - 0.7 : undefined
    }
  ]

  return result.filter(m => m.value !== undefined)
})

const icMetrics = computed(() => {
  const metrics = props.metrics
  if (!metrics) return []

  const result = [
    {
      name: 'IC',
      value: metrics.ic,
      color: getMetricColor(metrics.ic, 'ic'),
      highlight: metrics.ic !== undefined && Math.abs(metrics.ic) > 0.03,
      delta: metrics.ic !== undefined ? metrics.ic - 0.03 : undefined
    },
    {
      name: 'Rank IC',
      value: metrics.rank_ic,
      color: getMetricColor(metrics.rank_ic, 'rank_ic'),
      highlight: metrics.rank_ic !== undefined && Math.abs(metrics.rank_ic) > 0.03,
      delta: metrics.rank_ic !== undefined ? metrics.rank_ic - 0.03 : undefined
    }
  ]

  return result.filter(m => m.value !== undefined)
})

// ==================== 方法 ====================

/**
 * 获取指标颜色
 */
const getMetricColor = (value: number | undefined, type: string) => {
  if (value === undefined) return '#94a3b8'

  switch (type) {
    case 'accuracy':
    case 'precision':
    case 'recall':
    case 'f1':
      return value > 0.8 ? '#10b981' : value > 0.6 ? '#8b5cf6' : '#f59e0b'
    case 'mse':
    case 'mae':
      return value < 0.05 ? '#10b981' : value < 0.1 ? '#8b5cf6' : '#f59e0b'
    case 'r2':
      return value > 0.8 ? '#10b981' : value > 0.6 ? '#8b5cf6' : '#f59e0b'
    case 'ic':
    case 'rank_ic':
      return Math.abs(value) > 0.05 ? '#10b981' : Math.abs(value) > 0.03 ? '#8b5cf6' : '#f59e0b'
    default:
      return '#94a3b8'
  }
}

/**
 * 格式化指标值
 */
const formatMetricValue = (value: number | undefined) => {
  if (value === undefined) return '--'
  return value.toFixed(4)
}

/**
 * 初始化雷达图
 */
const initRadarChart = () => {
  const radarChartRef = document.querySelector('.radar-chart') as HTMLElement
  if (!radarChartRef) return

  const chart = echarts.init(radarChartRef)

  const metrics = props.metrics
  if (!metrics) return

  // 构建雷达图数据
  const data: any[] = []
  const indicator: any[] = []

  if (metrics.accuracy !== undefined) {
    data.push(metrics.accuracy)
    indicator.push({ name: 'Accuracy', max: 1 })
  }
  if (metrics.precision !== undefined) {
    data.push(metrics.precision)
    indicator.push({ name: 'Precision', max: 1 })
  }
  if (metrics.recall !== undefined) {
    data.push(metrics.recall)
    indicator.push({ name: 'Recall', max: 1 })
  }
  if (metrics.f1 !== undefined) {
    data.push(metrics.f1)
    indicator.push({ name: 'F1', max: 1 })
  }

  const option = {
    radar: {
      indicator: indicator,
      shape: 'circle',
      splitNumber: 4,
      name: {
        textStyle: { color: '#cbd5e1' }
      },
      splitLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      },
      splitArea: {
        show: true,
        areaStyle: { color: ['rgba(139, 92, 246, 0.1)'] }
      },
      axisLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    },
    series: [{
      name: 'Metrics',
      type: 'radar',
      data: [data],
      symbolSize: 6,
      lineStyle: { color: '#8b5cf6', width: 2 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
            { offset: 1, color: 'rgba(139, 92, 246, 0.1)' }
          ]
        }
      },
      itemStyle: { color: '#8b5cf6' }
    }]
  }

  chart.setOption(option)
}

onMounted(() => {
  if (showRadarChart.value) {
    nextTick(() => {
      initRadarChart()
    })
  }
})

watch(() => props.metrics, () => {
  if (showRadarChart.value) {
    nextTick(() => {
      initRadarChart()
    })
  }
}, { deep: true })
</script>

<style scoped lang="scss">
.ml-metrics-chart {
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
  }
}

.chart-content {
  .metrics-group {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    .group-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 16px 0;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-light);
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 16px;
    }

    .metric-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 20px;
      background: var(--bg-elevated);
      border-radius: var(--radius-md);
      border: 1px solid var(--border-light);
      transition: all 0.3s;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }

      &.metric-highlight {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
      }

      .metric-value {
        font-size: 28px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1;
      }

      .metric-name {
        font-size: 13px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .metric-delta {
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;

        .positive {
          color: #10b981;
        }

        .negative {
          color: #ef4444;
        }
      }
    }
  }

  .radar-section {
    .radar-chart {
      height: 300px;
      width: 100%;
    }
  }
}
</style>
