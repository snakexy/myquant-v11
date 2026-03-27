<template>
  <n-card class="data-overview-card" hoverable>
    <template #header>
      <div class="card-header">
        <div class="card-icon">
          <n-icon size="24" :color="iconColor">
            <component :is="iconComponent" />
          </n-icon>
        </div>
        <div class="card-title">
          <h3>{{ title }}</h3>
          <p class="card-subtitle">{{ subtitle }}</p>
        </div>
        <div class="card-actions">
          <n-dropdown trigger="hover" placement="bottom-end">
            <template #trigger>
              <n-button circle size="small" quaternary>
                <template #icon>
                  <n-icon><EllipsisVertical /></n-icon>
                </template>
              </n-button>
            </template>
            <template #dropdown>
              <n-doption @click="refreshData">
                <template #icon>
                  <n-icon><Refresh /></n-icon>
                </template>
                刷新数据
              </n-doption>
              <n-doption @click="exportData">
                <template #icon>
                  <n-icon><Download /></n-icon>
                </template>
                导出数据
              </n-doption>
              <n-doption @click="showDetails">
                <template #icon>
                  <n-icon><Eye /></n-icon>
                </template>
                查看详情
              </n-doption>
            </template>
          </n-dropdown>
        </div>
      </div>
    </template>
    
    <div class="card-content">
      <!-- 主要指标 -->
      <div class="metrics-grid">
        <div
          v-for="metric in mainMetrics"
          :key="metric.key"
          class="metric-item"
          :class="{ 'metric-positive': metric.trend > 0, 'metric-negative': metric.trend < 0 }"
        >
          <div class="metric-value">
            <n-number
              :value="metric.value"
              :precision="metric.precision || 0"
              :show-separator="metric.showSeparator"
              :prefix="metric.prefix"
              :suffix="metric.suffix"
            />
          </div>
          <div class="metric-label">{{ metric.label }}</div>
          <div v-if="metric.trend !== undefined" class="metric-trend">
            <n-icon
              :component="metric.trend > 0 ? TrendingUp : TrendingDown"
              :color="metric.trend > 0 ? 'var(--market-rise)' : 'var(--market-fall)'"
              size="14"
            />
            <span class="trend-value">{{ Math.abs(metric.trend) }}%</span>
          </div>
        </div>
      </div>
      
      <!-- 迷你图表 -->
      <div v-if="showChart" class="mini-chart">
        <BaseChart
          :option="chartOption"
          width="100%"
          height="120px"
          :theme="isDark ? 'dark' : 'light'"
        />
      </div>
      
      <!-- 状态指示器 -->
      <div class="status-indicators">
        <div
          v-for="indicator in statusIndicators"
          :key="indicator.key"
          class="status-item"
        >
          <div class="status-dot" :class="`status-${indicator.status}`"></div>
          <span class="status-text">{{ indicator.text }}</span>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="card-loading">
      <n-spin size="large" />
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NIcon, NButton, NDropdown, NDropdownOption, NNumber, NSpin } from 'naive-ui'
import { EllipsisVertical, Refresh, Download, Eye, TrendingUp, TrendingDown, Database, BarChart, Activity, AlertCircle } from '@vicons/ionicons5'
import BaseChart from '../charts/BaseChart.vue'
import { useAppStore } from '@/stores'
import type { EChartsOption } from 'echarts'

interface MetricItem {
  key: string
  label: string
  value: number
  trend?: number
  precision?: number
  showSeparator?: boolean
  prefix?: string
  suffix?: string
}

interface StatusIndicator {
  key: string
  text: string
  status: 'success' | 'warning' | 'error' | 'info'
}

interface ChartDataPoint {
  timestamp: number
  value: number
}

interface Props {
  title: string
  subtitle: string
  icon: string
  iconColor?: string
  mainMetrics: MetricItem[]
  statusIndicators?: StatusIndicator[]
  chartData?: ChartDataPoint[]
  showChart?: boolean
  loading?: boolean
  refreshAction?: () => Promise<void>
  exportAction?: () => Promise<void>
  detailsAction?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: '#2563eb',
  showChart: true,
  loading: false,
  statusIndicators: () => []
})

const emit = defineEmits<{
  refresh: []
  export: []
  details: []
}>()

const appStore = useAppStore()
const isDark = computed(() => appStore.currentThemeMode === 'dark')

// 图标组件映射
const iconComponents: Record<string, any> = {
  database: Database,
  chart: BarChart,
  activity: Activity,
  alert: AlertCircle
}

// 获取图标组件
const iconComponent = computed(() => {
  return iconComponents[props.icon] || Database
})

// 生成迷你图表配置
const chartOption = computed<EChartsOption>(() => {
  if (!props.chartData || props.chartData.length === 0) {
    return {}
  }
  
  return {
    grid: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0
    },
    xAxis: {
      type: 'category',
      show: false,
      data: props.chartData.map(item => item.timestamp)
    },
    yAxis: {
      type: 'value',
      show: false,
      min: 'dataMin',
      max: 'dataMax'
    },
    series: [
      {
        type: 'line',
        data: props.chartData.map(item => item.value),
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#2563eb',
          width: 2
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(37, 99, 235, 0.3)' },
              { offset: 1, color: 'rgba(37, 99, 235, 0.1)' }
            ]
          }
        }
      }
    ]
  }
})

// 刷新数据
const refreshData = async () => {
  if (props.refreshAction) {
    emit('refresh')
    await props.refreshAction()
  }
}

// 导出数据
const exportData = async () => {
  if (props.exportAction) {
    emit('export')
    await props.exportAction()
  }
}

// 显示详情
const showDetails = () => {
  if (props.detailsAction) {
    emit('details')
    props.detailsAction()
  }
}

onMounted(() => {
  // 组件挂载后的初始化逻辑
})
</script>

<style lang="scss" scoped>
.data-overview-card {
  height: 100%;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    
    .card-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: rgba(37, 99, 235, 0.1);
      border: 1px solid rgba(37, 99, 235, 0.2);
    }
    
    .card-title {
      flex: 1;
      margin-left: 12px;
      
      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #f8fafc;
        line-height: 1.2;
      }
      
      .card-subtitle {
        margin: 4px 0 0 0;
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.2;
      }
    }
    
    .card-actions {
      margin-left: auto;
    }
  }
  
  .card-content {
    position: relative;
    
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
      
      .metric-item {
        text-align: center;
        padding: 12px;
        border-radius: 8px;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.1);
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(15, 23, 42, 0.8);
          transform: translateY(-1px);
        }
        
        .metric-value {
          font-size: 20px;
          font-weight: 600;
          color: #f8fafc;
          line-height: 1.2;
        }
        
        .metric-label {
          font-size: 12px;
          color: #94a3b8;
          margin-top: 4px;
        }
        
        .metric-trend {
          display: flex;
          align-items: center;
          justify-content: center;
          margin-top: 4px;
          font-size: 12px;
          
          .trend-value {
            margin-left: 4px;
          }
        }
        
        &.metric-positive {
          border-color: rgba(16, 185, 129, 0.3);
        }
        
        &.metric-negative {
          border-color: rgba(239, 68, 68, 0.3);
        }
      }
    }
    
    .mini-chart {
      margin-bottom: 16px;
      border-radius: 8px;
      overflow: hidden;
      background: rgba(15, 23, 42, 0.4);
      border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .status-indicators {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      
      .status-item {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 10px;
        border-radius: 6px;
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(148, 163, 184, 0.1);
        
        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          
          &.status-success {
            background: var(--market-rise);
            box-shadow: 0 0 4px rgba(16, 185, 129, 0.4);
          }
          
          &.status-warning {
            background: #f59e0b;
            box-shadow: 0 0 4px rgba(245, 158, 11, 0.4);
          }
          
          &.status-error {
            background: var(--market-fall);
            box-shadow: 0 0 4px rgba(239, 68, 68, 0.4);
          }
          
          &.status-info {
            background: #3b82f6;
            box-shadow: 0 0 4px rgba(59, 130, 246, 0.4);
          }
        }
        
        .status-text {
          font-size: 12px;
          color: #94a3b8;
        }
      }
    }
  }
  
  .card-loading {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(2px);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
  }
}
</style>