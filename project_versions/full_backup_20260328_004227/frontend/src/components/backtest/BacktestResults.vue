<template>
  <div class="backtest-results">
    <!-- 绩效指标卡片 -->
    <el-row :gutter="16" class="metrics-cards">
      <el-col :span="4" v-for="metric in metrics" :key="metric.key">
        <el-card class="metric-card" shadow="hover">
          <div class="metric-content">
            <div class="metric-label">{{ metric.label }}</div>
            <div
              class="metric-value"
              :class="getMetricClass(metric.key, metric.value)"
            >
              {{ formatMetricValue(metric.key, metric.value) }}
            </div>
            <div v-if="metric.tooltip" class="metric-tooltip">
              <el-icon><QuestionFilled /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 净值曲线图表 -->
    <el-card class="chart-card" shadow="never">
      <TVLineChart
        v-if="equityChartData.strategyData.length > 0"
        :title="isZh ? '净值曲线' : 'Equity Curve'"
        :strategy-data="equityChartData.strategyData"
        :benchmark-data="equityChartData.benchmarkData"
        :dates="equityChartData.dates"
        :strategy-label="equityChartData.strategyLabel"
        :benchmark-label="equityChartData.benchmarkLabel"
        :strategy-color="equityChartData.strategyColor"
        :benchmark-color="equityChartData.benchmarkColor"
        :show-period-selector="true"
        :resizable="true"
        :height="350"
      />
      <div v-else class="chart-empty">
        <el-empty description="暂无净值数据" />
      </div>
    </el-card>

    <!-- 详细信息 -->
    <el-row :gutter="16">
      <!-- 交易记录 -->
      <el-col :span="12">
        <el-card class="transactions-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">💰 交易记录</span>
              <el-switch
                v-model="showTransactions"
                active-text="显示"
                inactive-text="隐藏"
              />
            </div>
          </template>
          <el-table
            :data="displayTransactions"
            v-loading="transactionsLoading"
            stripe
            max-height="400"
          >
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column prop="symbol" label="股票代码" width="100" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-tag :type="row.action === 'buy' ? 'success' : 'danger'" size="small">
                  {{ row.action === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="数量" width="80" />
            <el-table-column label="价格" width="100">
              <template #default="{ row }">
                ¥{{ row.price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="金额" width="120">
              <template #default="{ row }">
                ¥{{ row.value.toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 持仓记录 -->
      <el-col :span="12">
        <el-card class="positions-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">📊 持仓记录</span>
              <el-switch
                v-model="showPositions"
                active-text="显示"
                inactive-text="隐藏"
              />
            </div>
          </template>
          <el-table
            :data="displayPositions"
            v-loading="positionsLoading"
            stripe
            max-height="400"
          >
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column prop="symbol" label="股票代码" width="100" />
            <el-table-column prop="amount" label="持仓数量" width="100" />
            <el-table-column label="持仓市值" width="150">
              <template #default="{ row }">
                ¥{{ row.value.toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { useAppStore } from '@/stores/core/AppStore'
import type {
  BacktestResultData,
  PerformanceMetrics,
  NavCurveItem,
  TransactionRecord,
  PositionRecord
} from '@/api/unifiedBacktest'
import { formatPercent } from '@/api/unifiedBacktest'
import TVLineChart, { type Time } from '@/components/charts/TVLineChart.vue'

// Props
interface Props {
  result?: BacktestResultData
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isZh: true
})

// 全局语言设置
const appStore = useAppStore()
const isZh = computed(() => appStore.language === 'zh')

// Data
const chartRef = ref<HTMLElement>()
const chartLoading = ref(false)
const transactionsLoading = ref(false)
const positionsLoading = ref(false)
const showTransactions = ref(true)
const showPositions = ref(true)
const chartTimeRange = ref('ALL')

// 净值曲线数据 - 适配TVLineChart
const equityChartData = computed(() => {
  const currentIsZh = isZh.value
  const navCurve = props.result?.nav_curve || []
  if (!navCurve.length) {
    return {
      strategyData: [],
      benchmarkData: [],
      dates: [],
      strategyLabel: currentIsZh ? '策略' : 'Strategy',
      benchmarkLabel: currentIsZh ? '基准' : 'Benchmark',
      strategyColor: '#ef5350',
      benchmarkColor: '#787b86'
    }
  }

  const strategyData = navCurve.map((item: NavCurveItem) => ({
    time: item.date as Time,
    value: item.value
  }))

  const benchmarkData = navCurve.map((item: NavCurveItem) => ({
    time: item.date as Time,
    value: item.benchmark
  }))

  const dates = navCurve.map((item: NavCurveItem) => item.date)

  // 根据收益率设置颜色 - 红涨绿跌
  const lastValue = navCurve[navCurve.length - 1]?.value || 1
  const firstValue = navCurve[0]?.value || 1
  const returnPct = (lastValue - firstValue) / firstValue
  const strategyColor = returnPct >= 0 ? '#ef5350' : '#26a69a'

  return {
    strategyData,
    benchmarkData,
    dates,
    strategyLabel: currentIsZh ? '策略' : 'Strategy',
    benchmarkLabel: currentIsZh ? '基准' : 'Benchmark',
    strategyColor,
    benchmarkColor: '#787b86'
  }
})

// Chart instance
let chartInstance: echarts.ECharts | null = null

// Metrics
const metrics = computed(() => {
  const perf = props.result?.performance_metrics
  if (!perf) return []

  return [
    {
      key: 'total_return',
      label: '总收益率',
      value: perf.total_return,
      tooltip: true
    },
    {
      key: 'annual_return',
      label: '年化收益率',
      value: perf.annual_return,
      tooltip: true
    },
    {
      key: 'max_drawdown',
      label: '最大回撤',
      value: perf.max_drawdown,
      tooltip: true
    },
    {
      key: 'sharpe_ratio',
      label: '夏普比率',
      value: perf.sharpe_ratio,
      tooltip: true
    },
    {
      key: 'win_rate',
      label: '胜率',
      value: perf.win_rate,
      tooltip: true
    },
    {
      key: 'profit_loss_ratio',
      label: '盈亏比',
      value: perf.profit_loss_ratio,
      tooltip: true
    }
  ]
})

// Display data
const displayTransactions = computed(() => {
  if (!showTransactions.value) return []
  return props.result?.transactions || []
})

const displayPositions = computed(() => {
  if (!showPositions.value) return []
  return props.result?.positions || []
})

// Format metric value
const formatMetricValue = (key: string, value: number) => {
  if (key.includes('return') || key === 'max_drawdown' || key === 'win_rate') {
    return formatPercent(value)
  }
  if (key === 'sharpe_ratio' || key === 'profit_loss_ratio') {
    return value.toFixed(2)
  }
  return value.toString()
}

// Get metric class
const getMetricClass = (key: string, value: number) => {
  if (key.includes('return') && value > 0) return 'positive'
  if (key === 'max_drawdown' && value < 0) return 'positive'
  return ''
}

// Change chart time range
const changeChartTimeRange = (range: string) => {
  chartTimeRange.value = range
  renderChart()
}

// Render chart
const renderChart = () => {
  if (!chartRef.value || !props.result?.nav_curve) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const navCurve = props.result.nav_curve
  let displayData = navCurve

  // Filter by time range
  if (chartTimeRange.value !== 'ALL') {
    const rangeMap: Record<string, number> = {
      '1M': 30,
      '3M': 90,
      '6M': 180
    }
    const days = rangeMap[chartTimeRange.value]
    if (days) {
      displayData = navCurve.slice(-days)
    }
  }

  const dates = displayData.map(item => item.date)
  const values = displayData.map(item => item.value)
  const benchmarks = displayData.map(item => item.benchmark)

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['策略净值', '基准净值']
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
      data: dates
    },
    yAxis: {
      type: 'value',
      scale: true
    },
    series: [
      {
        name: '策略净值',
        type: 'line',
        smooth: true,
        data: values,
        lineStyle: {
          width: 2
        },
        areaStyle: {
          opacity: 0.3
        }
      },
      {
        name: '基准净值',
        type: 'line',
        smooth: true,
        data: benchmarks,
        lineStyle: {
          width: 2,
          type: 'dashed'
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

// Watch result changes
watch(
  () => props.result,
  () => {
    if (props.result) {
      nextTick(() => {
        renderChart()
      })
    }
  },
  { immediate: true }
)

// Lifecycle
onMounted(() => {
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
})

// Expose refresh method
defineExpose({
  refreshChart: renderChart
})
</script>

<style scoped lang="scss">
.backtest-results {
  .metrics-cards {
    margin-bottom: 16px;

    .metric-card {
      .metric-content {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .metric-label {
          font-size: 14px;
          color: #909399;
        }

        .metric-value {
          font-size: 24px;
          font-weight: 600;
          color: #303133;

          &.positive {
            color: #f56c6c;
          }

          &.negative {
            color: #67c23a;
          }
        }

        .metric-tooltip {
          align-self: flex-end;
          color: #909399;
          cursor: help;
        }
      }
    }
  }

  .chart-card {
    margin-bottom: 16px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .title {
        font-size: 16px;
        font-weight: 600;
      }
    }

    .chart-container {
      width: 100%;
      height: 400px;
    }

    .chart-empty {
      width: 100%;
      height: 350px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }

  .transactions-card,
  .positions-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .title {
        font-size: 16px;
        font-weight: 600;
      }
    }
  }
}
</style>
