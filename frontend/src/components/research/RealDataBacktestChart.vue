<template>
  <div class="backtest-chart">
    <!-- 标题栏 -->
    <div v-if="showHeader" class="chart-header">
      <h3 class="chart-title">回测结果可视化</h3>
      <div class="chart-actions">
        <el-button-group>
          <el-button
            :type="viewMode === 'return' ? 'primary' : ''"
            size="small"
            @click="viewMode = 'return'"
          >
            收益曲线
          </el-button>
          <el-button
            :type="viewMode === 'drawdown' ? 'primary' : ''"
            size="small"
            @click="viewMode = 'drawdown'"
          >
            回撤分析
          </el-button>
          <el-button
            :type="viewMode === 'overview' ? 'primary' : ''"
            size="small"
            @click="viewMode = 'overview'"
          >
            综合视图
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <div v-if="showMetrics && metrics" class="metrics-row">
      <div class="metric-card">
        <span class="metric-label">总收益率</span>
        <span :class="['metric-value', getReturnClass()]">
          {{ formatPercent(metrics.total_return) }}
        </span>
      </div>
      <div class="metric-card">
        <span class="metric-label">最大回撤</span>
        <span :class="['metric-value', getDrawdownClass()]">
          {{ formatPercent(metrics.max_drawdown) }}
        </span>
      </div>
      <div class="metric-card">
        <span class="metric-label">夏普比率</span>
        <span :class="['metric-value', getSharpeClass()]">
          {{ metrics.sharpe_ratio?.toFixed(2) || 'N/A' }}
        </span>
      </div>
      <div v-if="metrics.win_rate !== undefined" class="metric-card">
        <span class="metric-label">胜率</span>
        <span :class="['metric-value', getWinRateClass()]">
          {{ formatPercent(metrics.win_rate) }}
        </span>
      </div>
    </div>

    <!-- 图表容器 -->
    <div class="chart-container">
      <!-- 收益曲线视图 -->
      <div
        v-show="viewMode === 'return' || viewMode === 'overview'"
        ref="returnChartRef"
        class="chart"
      ></div>

      <!-- 回撤分析视图 -->
      <div
        v-show="viewMode === 'drawdown' || viewMode === 'overview'"
        ref="drawdownChartRef"
        class="chart"
      ></div>

      <!-- 空状态 -->
      <div v-if="!hasData" class="empty-state">
        <el-empty :image-size="100" description="暂无回测数据" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

/**
 * 回测指标接口
 */
export interface BacktestMetrics {
  /** 总收益率 */
  total_return: number
  /** 最大回撤 */
  max_drawdown: number
  /** 夏普比率 */
  sharpe_ratio: number
  /** 胜率（可选） */
  win_rate?: number
  /** 年化收益率（可选） */
  annual_return?: number
  /** 波动率（可选） */
  volatility?: number
}

/**
 * 回测数据点接口
 */
export interface BacktestDataPoint {
  /** 日期 */
  date: string
  /** 净值 */
  net_value: number
  /** 收益率 */
  return: number
  /** 回撤 */
  drawdown: number
  /** 持仓（可选） */
  position?: number
}

// ==================== Props ====================

interface Props {
  /** 回测指标 */
  metrics?: BacktestMetrics
  /** 回测数据 */
  data?: BacktestDataPoint[]
  /** 显示高度 */
  height?: number
  /** 是否显示头部 */
  showHeader?: boolean
  /** 是否显示指标卡片 */
  showMetrics?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: 400,
  showHeader: true,
  showMetrics: true
})

// ==================== 状态 ====================

const viewMode = ref<'return' | 'drawdown' | 'overview'>('overview')
const returnChartRef = ref<HTMLElement>()
const drawdownChartRef = ref<HTMLElement>()
let returnChart: echarts.ECharts | null = null
let drawdownChart: echarts.ECharts | null = null

// ==================== 计算属性 ====================

const hasData = computed(() => {
  return props.data && props.data.length > 0
})

// ==================== 方法 ====================

/**
 * 格式化百分比
 */
const formatPercent = (value: number) => {
  if (value === undefined || value === null) return 'N/A'
  return `${(value * 100).toFixed(2)}%`
}

/**
 * 获取收益率样式类
 */
const getReturnClass = () => {
  if (!props.metrics) return ''
  const value = props.metrics.total_return
  if (value > 0.2) return 'excellent'
  if (value > 0.1) return 'good'
  if (value > 0) return 'positive'
  if (value === 0) return 'neutral'
  return 'negative'
}

/**
 * 获取回撤样式类
 */
const getDrawdownClass = () => {
  if (!props.metrics) return ''
  const value = props.metrics.max_drawdown
  if (value < 0.05) return 'excellent'
  if (value < 0.1) return 'good'
  if (value < 0.2) return 'acceptable'
  return 'poor'
}

/**
 * 获取夏普比率样式类
 */
const getSharpeClass = () => {
  if (!props.metrics) return ''
  const value = props.metrics.sharpe_ratio
  if (value > 2) return 'excellent'
  if (value > 1) return 'good'
  if (value > 0) return 'acceptable'
  return 'poor'
}

/**
 * 获取胜率样式类
 */
const getWinRateClass = () => {
  if (props.metrics?.win_rate === undefined) return ''
  const value = props.metrics.win_rate
  if (value > 0.6) return 'excellent'
  if (value > 0.5) return 'good'
  return 'poor'
}

/**
 * 初始化收益曲线图表
 */
const initReturnChart = () => {
  if (!returnChartRef.value || !hasData.value) return

  if (returnChart) {
    returnChart.dispose()
  }

  returnChart = echarts.init(returnChartRef.value)

  const dates = props.data!.map(d => d.date)
  const netValues = props.data!.map(d => d.net_value)
  const returns = props.data!.map(d => d.return)

  // 计算累计收益
  let cumulativeReturn = 0
  const cumulativeReturns = props.data!.map(d => {
    cumulativeReturn += d.return
    return cumulativeReturn
  })

  const option = {
    title: {
      text: '净值曲线 & 累计收益',
      textStyle: { color: '#cbd5e1', fontSize: 14 },
      left: 'center'
    },
    grid: [
      {
        left: '8%',
        right: '3%',
        top: '15%',
        height: '35%'
      },
      {
        left: '8%',
        right: '3%',
        top: '57%',
        height: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        gridIndex: 0,
        axisLabel: { color: '#94a3b8' },
        axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
      },
      {
        type: 'category',
        data: dates,
        gridIndex: 1,
        axisLabel: { show: false },
        axisLine: { show: false }
      }
    ],
    yAxis: [
      {
        scale: true,
        gridIndex: 0,
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
      },
      {
        scale: true,
        gridIndex: 1,
        axisLabel: { color: '#94a3b8' },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        xAxisIndex: [0, 1],
        start: 0,
        end: 100,
        height: 20,
        bottom: 5
      }
    ],
    series: [
      {
        name: '净值',
        type: 'line',
        data: netValues,
        xAxisIndex: 0,
        yAxisIndex: 0,
        smooth: true,
        lineStyle: { color: '#8b5cf6', width: 2 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
              { offset: 1, color: 'rgba(139, 92, 246, 0)' }
            ]
          }
        }
      },
      {
        name: '累计收益',
        type: 'bar',
        data: returns,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: {
          color: (params: any) => {
            const value = params.data
            return value >= 0 ? '#ef4444' : '#10b981'
          }
        }
      }
    ],
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['净值', '累计收益'],
      textStyle: { color: '#cbd5e1' },
      top: 25
    }
  }

  returnChart.setOption(option)
}

/**
 * 初始化回撤分析图表
 */
const initDrawdownChart = () => {
  if (!drawdownChartRef.value || !hasData.value) return

  if (drawdownChart) {
    drawdownChart.dispose()
  }

  drawdownChart = echarts.init(drawdownChartRef.value)

  const dates = props.data!.map(d => d.date)
  const drawdowns = props.data!.map(d => d.drawdown * 100)

  const option = {
    title: {
      text: '回撤分析',
      textStyle: { color: '#cbd5e1', fontSize: 14 },
      left: 'center'
    },
    grid: {
      left: '8%',
      right: '3%',
      top: '15%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }
    },
    yAxis: {
      type: 'value',
      name: '回撤 (%)',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: {
        color: '#94a3b8',
        formatter: '{value}%'
      },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100,
        height: 20,
        bottom: 5
      }
    ],
    series: [{
      name: '回撤',
      type: 'line',
      data: drawdowns,
      smooth: true,
      lineStyle: { color: '#ef4444', width: 2 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(239, 68, 68, 0.3)' },
            { offset: 1, color: 'rgba(239, 68, 68, 0)' }
          ]
        }
      },
      markLine: {
        data: [{
          yAxis: props.metrics?.max_drawdown * 100 || -10,
          label: {
            formatter: `最大回撤: {formatPercent(props.metrics?.max_drawdown || 0)}`,
            position: 'end'
          },
          lineStyle: { color: '#ef4444', type: 'dashed' }
        }]
      }
    }],
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>回撤: {c}%'
    }
  }

  drawdownChart.setOption(option)
}

/**
 * 初始化所有图表
 */
const initCharts = () => {
  if (!hasData.value) return

  if (viewMode.value === 'return' || viewMode.value === 'overview') {
    initReturnChart()
  }

  if (viewMode.value === 'drawdown' || viewMode.value === 'overview') {
    nextTick(() => {
      initDrawdownChart()
    })
  }
}

// ==================== 监听 ====================

watch(() => props.data, () => {
  initCharts()
}, { deep: true })

watch(() => props.metrics, () => {
  initCharts()
}, { deep: true })

watch(viewMode, () => {
  initCharts()
})

// ==================== 生命周期 ====================

onMounted(() => {
  initCharts()
})
</script>

<style scoped lang="scss">
.backtest-chart {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 16px;
  color: var(--text-primary);

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .chart-title {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 16px;

    .metric-card {
      padding: 12px;
      background: var(--bg-elevated);
      border: 1px solid var(--border-light);
      border-radius: var(--radius-md);
      display: flex;
      flex-direction: column;
      align-items: center;

      .metric-label {
        font-size: 12px;
        color: var(--text-muted);
        margin-bottom: 4px;
      }

      .metric-value {
        font-size: 20px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;

        &.excellent {
          color: #10b981;
        }

        &.good {
          color: #3b82f6;
        }

        &.positive {
          color: #ef4444;
        }

        &.neutral {
          color: var(--text-secondary);
        }

        &.negative {
          color: #94a3b8;
        }

        &.acceptable {
          color: #f59e0b;
        }

        &.poor {
          color: #ef4444;
        }
      }
    }
  }

  .chart-container {
    position: relative;

    .chart {
      height: v-bind('props.height + "px"');
      min-height: 300px;

      & + .chart {
        margin-top: 16px;
      }
    }

    .empty-state {
      height: v-bind('props.height + "px"');
      min-height: 300px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

// 滚动条样式
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-deep);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-elevated);
  border-radius: var(--radius-full);

  &:hover {
    background: var(--border-strong);
  }
}
</style>
