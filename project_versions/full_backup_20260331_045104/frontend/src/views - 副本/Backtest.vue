<template>
  <div class="backtest-page">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-system" ref="particleSystem"></div>
      <div class="data-stream-overlay"></div>
      <div class="grid-pattern"></div>
    </div>

    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">回测中心</h1>
          <p class="page-subtitle">高性能策略回测与性能分析平台</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="createNewBacktest">
              <i class="fas fa-plus"></i>
              <span>新建回测</span>
            </button>
            <button class="secondary-btn" @click="showBatchTest">
              <i class="fas fa-layer-group"></i>
              <span>批量回测</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 回测统计 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card" v-for="stat in backtestStats" :key="stat.id">
            <div class="stat-icon">
              <i :class="stat.icon"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
            <div class="stat-trend" :class="stat.trend">
              <i :class="getTrendIcon(stat.trend)"></i>
              <span>{{ stat.change }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 快速回测 -->
      <section class="quick-backtest-section">
        <div class="section-header">
          <h2>快速回测</h2>
          <p>选择策略和参数进行快速回测</p>
        </div>
        
        <div class="backtest-interface">
          <div class="interface-left">
            <div class="form-group">
              <label>选择策略</label>
              <select v-model="selectedStrategy" @change="onStrategyChange">
                <option value="">请选择策略</option>
                <option v-for="strategy in strategies" :key="strategy.id" :value="strategy.id">
                  {{ strategy.name }}
                </option>
              </select>
            </div>
           
            <div class="form-group">
              <label>回测时间段</label>
              <div class="date-range">
                <input
                  type="date"
                  v-model="startDate"
                  :max="endDate"
                  class="date-input"
                >
                <span>至</span>
                <input
                  type="date"
                  v-model="endDate"
                  :min="startDate"
                  class="date-input"
                >
              </div>
            </div>
           
            <div class="form-group">
              <label>多时间框架</label>
              <div class="timeframe-selector">
                <div class="timeframe-options">
                  <label class="timeframe-checkbox" v-for="timeframe in availableTimeframes" :key="timeframe.value">
                    <input
                      type="checkbox"
                      :value="timeframe.value"
                      v-model="selectedTimeframes"
                    >
                    <span class="timeframe-label">{{ timeframe.label }}</span>
                    <span class="timeframe-desc">{{ timeframe.description }}</span>
                  </label>
                </div>
              </div>
            </div>
           
            <div class="form-group">
              <label>初始资金</label>
              <div class="amount-input">
                <input
                  type="number"
                  v-model="initialCapital"
                  min="10000"
                  step="10000"
                  class="capital-input"
                >
                <span class="currency">元</span>
              </div>
            </div>
           
            <div class="form-group">
              <label>基准指数</label>
              <select v-model="benchmark">
                <option value="000300">沪深300</option>
                <option value="000905">中证500</option>
                <option value="000016">上证50</option>
                <option value="399001">深证成指</option>
              </select>
            </div>
          </div>
          
          <div class="interface-right">
            <div class="strategy-preview" v-if="selectedStrategyData">
              <h3>{{ selectedStrategyData.name }}</h3>
              <p>{{ selectedStrategyData.description }}</p>
              <div class="strategy-params">
                <div class="param-item" v-for="param in selectedStrategyData.parameters" :key="param.name">
                  <span class="param-name">{{ param.name }}:</span>
                  <span class="param-value">{{ param.value }}</span>
                </div>
              </div>
            </div>
            
            <button class="start-backtest-btn" @click="startBacktest" :disabled="!canStartBacktest">
              <i class="fas fa-play"></i>
              <span>开始回测</span>
            </button>
          </div>
        </div>
      </section>

      <!-- 回测结果 -->
      <section class="results-section" v-if="backtestResults.length > 0">
        <div class="section-header">
          <h2>回测结果</h2>
          <div class="result-controls">
            <button class="compare-btn" @click="compareResults">
              <i class="fas fa-balance-scale"></i>
              <span>对比分析</span>
            </button>
            <button class="export-btn" @click="exportResults">
              <i class="fas fa-download"></i>
              <span>导出报告</span>
            </button>
          </div>
        </div>
        
        <div class="results-grid">
          <div 
            v-for="result in backtestResults" 
            :key="result.id"
            class="result-card"
            @click="showResultDetail(result)"
          >
            <div class="result-header">
              <div class="result-info">
                <h3>{{ result.strategyName }}</h3>
                <p>{{ result.timeRange }}</p>
                <div class="timeframe-badge" v-if="result.timeframeLabel">
                  <i class="fas fa-clock"></i>
                  <span>{{ result.timeframeLabel }}</span>
                </div>
              </div>
              <div class="result-status" :class="result.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ getStatusText(result.status) }}</span>
              </div>
            </div>
            
            <div class="result-metrics">
              <div class="metric-row">
                <div class="metric">
                  <span class="metric-label">总收益率</span>
                  <span class="metric-value" :class="getPerformanceClass(result.totalReturn)">
                    {{ result.totalReturn }}%
                  </span>
                </div>
                <div class="metric">
                  <span class="metric-label">年化收益</span>
                  <span class="metric-value" :class="getPerformanceClass(result.annualReturn)">
                    {{ result.annualReturn }}%
                  </span>
                </div>
              </div>
              
              <div class="metric-row">
                <div class="metric">
                  <span class="metric-label">最大回撤</span>
                  <span class="metric-value" :class="getRiskClass(result.maxDrawdown)">
                    {{ result.maxDrawdown }}%
                  </span>
                </div>
                <div class="metric">
                  <span class="metric-label">夏普比率</span>
                  <span class="metric-value">{{ result.sharpeRatio }}</span>
                </div>
              </div>
              
              <div class="metric-row">
                <div class="metric">
                  <span class="metric-label">胜率</span>
                  <span class="metric-value">{{ result.winRate }}%</span>
                </div>
                <div class="metric">
                  <span class="metric-label">盈亏比</span>
                  <span class="metric-value">{{ result.profitLossRatio }}</span>
                </div>
              </div>
            </div>
            
            <div class="result-chart">
              <div class="mini-chart" :id="`chart-${result.id}`"></div>
            </div>
            
            <div class="result-actions">
              <button class="action-btn" @click.stop="viewDetails(result)">
                <i class="fas fa-chart-line"></i>
              </button>
              <button class="action-btn" @click.stop="compareTimeframes(result)" v-if="hasMultipleTimeframes(result.strategyName)">
                <i class="fas fa-clock"></i>
              </button>
              <button class="action-btn" @click.stop="duplicateResult(result)">
                <i class="fas fa-copy"></i>
              </button>
              <button class="action-btn" @click.stop="deleteResult(result)">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 对比分析 -->
      <section class="comparison-section" v-if="showComparison">
        <div class="section-header">
          <h2>策略对比分析</h2>
          <button class="close-comparison-btn" @click="showComparison = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="comparison-table">
          <table class="comparison-grid">
            <thead>
              <tr>
                <th>策略名称</th>
                <th>年化收益</th>
                <th>最大回撤</th>
                <th>夏普比率</th>
                <th>胜率</th>
                <th>综合评分</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in backtestResults" :key="result.id">
                <td>{{ result.strategyName }}</td>
                <td :class="getPerformanceClass(result.annualReturn)">{{ result.annualReturn }}%</td>
                <td :class="getRiskClass(result.maxDrawdown)">{{ result.maxDrawdown }}%</td>
                <td>{{ result.sharpeRatio }}</td>
                <td>{{ result.winRate }}%</td>
                <td>
                  <div class="score-badge" :class="getScoreClass(result.compositeScore)">
                    {{ result.compositeScore }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>

    <!-- 时间框架对比弹窗 -->
    <div v-if="timeframeCompareModalVisible" class="timeframe-compare-modal">
      <div class="modal-overlay" @click="timeframeCompareModalVisible = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>时间框架对比 - {{ compareData.strategyName }}</h3>
          <button class="close-btn" @click="timeframeCompareModalVisible = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div v-if="compareData.results.length > 0" class="timeframe-compare-content">
          <div class="compare-overview">
            <h4>策略表现概览</h4>
            <div class="overview-grid">
              <div class="overview-item">
                <div class="overview-label">最佳时间框架</div>
                <div class="overview-value">{{ compareData.bestTimeframe }}</div>
              </div>
              <div class="overview-item">
                <div class="overview-label">收益率范围</div>
                <div class="overview-value">{{ compareData.returnRange.min.toFixed(2) }}% ~ {{ compareData.returnRange.max.toFixed(2) }}%</div>
              </div>
              <div class="overview-item">
                <div class="overview-label">夏普比率范围</div>
                <div class="overview-value">{{ compareData.sharpeRange.min.toFixed(2) }} ~ {{ compareData.sharpeRange.max.toFixed(2) }}</div>
              </div>
              <div class="overview-item">
                <div class="overview-label">最大回撤范围</div>
                <div class="overview-value">{{ compareData.drawdownRange.min.toFixed(2) }}% ~ {{ compareData.drawdownRange.max.toFixed(2) }}%</div>
              </div>
            </div>
          </div>

          <div class="compare-table">
            <h4>详细对比</h4>
            <table class="comparison-grid">
              <thead>
                <tr>
                  <th>时间框架</th>
                  <th>总收益率</th>
                  <th>年化收益率</th>
                  <th>最大回撤</th>
                  <th>夏普比率</th>
                  <th>胜率</th>
                  <th>盈亏比</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="result in compareData.results" :key="result.id">
                  <td>{{ result.timeframeLabel }}</td>
                  <td :class="getPerformanceClass(result.totalReturn)">{{ result.totalReturn.toFixed(2) }}%</td>
                  <td :class="getPerformanceClass(result.annualReturn)">{{ result.annualReturn.toFixed(2) }}%</td>
                  <td :class="getRiskClass(result.maxDrawdown)">{{ result.maxDrawdown.toFixed(2) }}%</td>
                  <td :class="getPerformanceClass(result.sharpeRatio, 1)">{{ result.sharpeRatio.toFixed(2) }}</td>
                  <td :class="getPerformanceClass(result.winRate, 50)">{{ result.winRate.toFixed(1) }}%</td>
                  <td :class="getPerformanceClass(result.profitLossRatio, 1)">{{ result.profitLossRatio.toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="compare-charts">
            <div class="chart-container">
              <h4>收益率对比</h4>
              <div id="returnCompareChart" class="chart"></div>
            </div>
            <div class="chart-container">
              <h4>风险收益散点图</h4>
              <div id="riskReturnChart" class="chart"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'

const router = useRouter()

// 响应式数据
const selectedStrategy = ref('')
const startDate = ref('2023-01-01')
const endDate = ref('2024-01-01')
const initialCapital = ref(1000000)
const benchmark = ref('000300')
const showComparison = ref(false)
const selectedTimeframes = ref(['1d', '1w'])

// 时间框架对比弹窗
const timeframeCompareModalVisible = ref(false)
const compareData = ref<{
  strategyName: string
  results: any[]
  bestTimeframe: string
  returnRange: { min: number; max: number }
  sharpeRange: { min: number; max: number }
  drawdownRange: { min: number; max: number }
}>({
  strategyName: '',
  results: [],
  bestTimeframe: '',
  returnRange: { min: 0, max: 0 },
  sharpeRange: { min: 0, max: 0 },
  drawdownRange: { min: 0, max: 0 }
})

// 回测统计
const backtestStats = ref([
  {
    id: 1,
    icon: 'fas fa-chart-line',
    label: '总回测数',
    value: '1,234',
    change: '+18%',
    trend: 'up'
  },
  {
    id: 2,
    icon: 'fas fa-clock',
    label: '平均耗时',
    value: '2.3分钟',
    change: '-12%',
    trend: 'down'
  },
  {
    id: 3,
    icon: 'fas fa-trophy',
    label: '高收益策略',
    value: '89',
    change: '+25%',
    trend: 'up'
  },
  {
    id: 4,
    icon: 'fas fa-server',
    label: '并行处理',
    value: '8核',
    change: '+33%',
    trend: 'up'
  }
])

// 策略数据
const strategies = ref([
  {
    id: 'strategy-1',
    name: '双均线趋势跟踪',
    description: '基于短期和长期均线的趋势跟踪策略',
    parameters: [
      { name: '短期均线', value: 'MA5' },
      { name: '长期均线', value: 'MA20' },
      { name: '止损比例', value: '2%' }
    ]
  },
  {
    id: 'strategy-2',
    name: 'RSI均值回归',
    description: '利用RSI指标进行均值回归交易',
    parameters: [
      { name: 'RSI周期', value: '14' },
      { name: '超卖线', value: '30' },
      { name: '超买线', value: '70' }
    ]
  },
  {
    id: 'strategy-3',
    name: '动量突破策略',
    description: '基于价格动量的突破交易策略',
    parameters: [
      { name: '动量周期', value: '10' },
      { name: '突破阈值', value: '1.5%' },
      { name: '持仓周期', value: '5天' }
    ]
  }
])

// 可用时间框架
const availableTimeframes = ref([
  { value: '1m', label: '1分钟', description: '超短线交易' },
  { value: '5m', label: '5分钟', description: '短线交易' },
  { value: '15m', label: '15分钟', description: '短线交易' },
  { value: '30m', label: '30分钟', description: '中短线交易' },
  { value: '1h', label: '1小时', description: '中长线交易' },
  { value: '4h', label: '4小时', description: '中长线交易' },
  { value: '1d', label: '日线', description: '长线交易' },
  { value: '1w', label: '周线', description: '长线交易' }
])

// 回测结果
const backtestResults = ref([
  {
    id: 1,
    strategyName: '双均线趋势跟踪',
    timeRange: '2023.01-01 至 2024.01-01',
    totalReturn: 15.2,
    annualReturn: 15.2,
    maxDrawdown: -8.5,
    sharpeRatio: 1.23,
    winRate: 58.3,
    profitLossRatio: 1.4,
    status: 'completed',
    compositeScore: 78
  },
  {
    id: 2,
    strategyName: 'RSI均值回归',
    timeRange: '2023.01-01 至 2024.01-01',
    totalReturn: 12.8,
    annualReturn: 12.8,
    maxDrawdown: -6.2,
    sharpeRatio: 1.05,
    winRate: 62.1,
    profitLossRatio: 1.6,
    status: 'completed',
    compositeScore: 72
  },
  {
    id: 3,
    strategyName: '动量突破策略',
    timeRange: '2023.01-01 至 2024.01-01',
    totalReturn: 22.5,
    annualReturn: 22.5,
    maxDrawdown: -12.8,
    sharpeRatio: 1.67,
    winRate: 55.2,
    profitLossRatio: 1.8,
    status: 'completed',
    compositeScore: 85
  }
])

// 计算属性
const selectedStrategyData = computed(() => {
  return strategies.value.find(s => s.id === selectedStrategy.value)
})

const canStartBacktest = computed(() => {
  return selectedStrategy.value && startDate.value && endDate.value && initialCapital.value > 0
})

// 方法
const getTrendIcon = (trend: string) => {
  const iconMap = {
    up: 'fas fa-arrow-up',
    down: 'fas fa-arrow-down',
    stable: 'fas fa-minus'
  }
  return iconMap[trend] || 'fas fa-minus'
}

const getStatusText = (status: string) => {
  const statusMap = {
    completed: '已完成',
    running: '运行中',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const getPerformanceClass = (value: number) => {
  if (value > 20) return 'excellent'
  if (value > 15) return 'good'
  if (value > 10) return 'normal'
  return 'poor'
}

const getRiskClass = (value: number) => {
  if (value > -5) return 'high'
  if (value > -10) return 'medium'
  return 'low'
}

const getScoreClass = (score: number) => {
  if (score >= 80) return 'excellent'
  if (score >= 70) return 'good'
  if (score >= 60) return 'normal'
  return 'poor'
}

const onStrategyChange = () => {
  // 策略变化时的处理
}

const createNewBacktest = () => {
  router.push('/function/backtest-lab/dashboard')
}

const showBatchTest = () => {
  console.log('批量回测')
}

const startBacktest = () => {
  console.log('开始多时间框架回测', {
    strategy: selectedStrategy.value,
    dateRange: [startDate.value, endDate.value],
    capital: initialCapital.value,
    benchmark: benchmark.value,
    timeframes: selectedTimeframes.value
  })
  
  // 模拟多时间框架回测完成
  setTimeout(() => {
    selectedTimeframes.value.forEach(timeframe => {
      const timeframeLabel = availableTimeframes.value.find(tf => tf.value === timeframe)?.label || timeframe
      const newResult = {
        id: Date.now() + Math.random(),
        strategyName: `${selectedStrategyData.value?.name || '自定义策略'} (${timeframeLabel})`,
        timeRange: `${startDate.value} 至 ${endDate.value}`,
        timeframe: timeframe,
        timeframeLabel: timeframeLabel,
        totalReturn: Math.random() * 30 - 5,
        annualReturn: Math.random() * 30 - 5,
        maxDrawdown: -Math.random() * 15 - 5,
        sharpeRatio: Math.random() * 2 + 0.5,
        winRate: Math.random() * 40 + 40,
        profitLossRatio: Math.random() * 2 + 0.5,
        status: 'completed',
        compositeScore: Math.floor(Math.random() * 40 + 60)
      }
      backtestResults.value.unshift(newResult)
    })
  }, 3000)
}

const showResultDetail = (result: any) => {
  console.log('显示结果详情', result)
}

const viewDetails = (result: any) => {
  router.push('/function/backtest-lab/architecture')
}

// 检查是否有多个时间框架的结果
const hasMultipleTimeframes = (strategyName: string): boolean => {
  const baseStrategyName = strategyName.replace(/ \([^)]+\)$/, '')
  const sameStrategyResults = backtestResults.value.filter(result =>
    result.strategyName.replace(/ \([^)]+\)$/, '') === baseStrategyName
  )
  return sameStrategyResults.length > 1
}

// 时间框架对比
const compareTimeframes = (result: any) => {
  const baseStrategyName = result.strategyName.replace(/ \([^)]+\)$/, '')
  const sameStrategyResults = backtestResults.value.filter(res =>
    res.strategyName.replace(/ \([^)]+\)$/, '') === baseStrategyName
  )
  
  // 计算统计信息
  const returns = sameStrategyResults.map(r => r.totalReturn)
  const sharpeRatios = sameStrategyResults.map(r => r.sharpeRatio)
  const drawdowns = sameStrategyResults.map(r => r.maxDrawdown)
  
  const bestResult = sameStrategyResults.reduce((best, current) =>
    current.sharpeRatio > best.sharpeRatio ? current : best
  )
  
  compareData.value = {
    strategyName: baseStrategyName,
    results: sameStrategyResults,
    bestTimeframe: bestResult.timeframeLabel || '未知',
    returnRange: {
      min: Math.min(...returns),
      max: Math.max(...returns)
    },
    sharpeRange: {
      min: Math.min(...sharpeRatios),
      max: Math.max(...sharpeRatios)
    },
    drawdownRange: {
      min: Math.min(...drawdowns),
      max: Math.max(...drawdowns)
    }
  }
  
  timeframeCompareModalVisible.value = true
  
  // 延迟绘制图表，确保DOM已渲染
  nextTick(() => {
    drawCompareCharts()
  })
}

const duplicateResult = (result: any) => {
  console.log('复制结果', result)
}

const deleteResult = (result: any) => {
  const index = backtestResults.value.findIndex(r => r.id === result.id)
  if (index > -1) {
    backtestResults.value.splice(index, 1)
  }
}

const compareResults = () => {
  showComparison.value = true
}

const exportResults = () => {
  console.log('导出回测结果')
}

// 绘制对比图表
const drawCompareCharts = () => {
  // 收益率对比柱状图
  const returnChartEl = document.querySelector('#returnCompareChart') as HTMLElement
  if (returnChartEl) {
    const returnChart = echarts.init(returnChartEl)
    const returnOption = {
      title: {
        text: '各时间框架收益率对比',
        textStyle: { color: '#f8fafc' }
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          let result = params[0].name + '<br/>'
          params.forEach((item: any) => {
            result += `${item.seriesName}: ${item.value.toFixed(2)}%<br/>`
          })
          return result
        }
      },
      legend: {
        data: ['总收益率', '年化收益率'],
        textStyle: { color: '#f8fafc' }
      },
      xAxis: {
        type: 'category',
        data: compareData.value.results.map(r => r.timeframeLabel),
        axisLabel: { color: '#f8fafc' }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          color: '#f8fafc',
          formatter: (value: number) => value.toFixed(1) + '%'
        }
      },
      series: [
        {
          name: '总收益率',
          type: 'bar',
          data: compareData.value.results.map(r => r.totalReturn),
          itemStyle: { color: '#2563eb' }
        },
        {
          name: '年化收益率',
          type: 'bar',
          data: compareData.value.results.map(r => r.annualReturn),
          itemStyle: { color: '#10b981' }
        }
      ]
    }
    returnChart.setOption(returnOption)
  }
  
  // 风险收益散点图
  const riskReturnChartEl = document.querySelector('#riskReturnChart') as HTMLElement
  if (riskReturnChartEl) {
    const riskReturnChart = echarts.init(riskReturnChartEl)
    const scatterData = compareData.value.results.map(r => ({
      name: r.timeframeLabel,
      value: [r.volatility || Math.random() * 0.3 + 0.1, r.annualReturn],
      itemStyle: { color: r.sharpeRatio > 1 ? '#10b981' : r.sharpeRatio > 0.5 ? '#f59e0b' : '#ef4444' }
    }))
    
    const scatterOption = {
      title: {
        text: '风险收益散点图',
        textStyle: { color: '#f8fafc' }
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          return `${params.data.name}<br/>
                  波动率: ${(params.data.value[0] * 100).toFixed(2)}%<br/>
                  年化收益率: ${params.data.value[1].toFixed(2)}%`
        }
      },
      xAxis: {
        type: 'value',
        name: '波动率',
        nameTextStyle: { color: '#f8fafc' },
        axisLabel: {
          color: '#f8fafc',
          formatter: (value: number) => (value * 100).toFixed(1) + '%'
        }
      },
      yAxis: {
        type: 'value',
        name: '年化收益率',
        nameTextStyle: { color: '#f8fafc' },
        axisLabel: {
          color: '#f8fafc',
          formatter: (value: number) => value.toFixed(1) + '%'
        }
      },
      series: [
        {
          type: 'scatter',
          data: scatterData,
          symbolSize: 20
        }
      ]
    }
    riskReturnChart.setOption(scatterOption)
  }
}

// 初始化粒子系统
const initParticleSystem = () => {
  const particleSystem = document.querySelector('.particle-system')
  if (!particleSystem) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  canvas.style.position = 'absolute'
  canvas.style.top = '0'
  canvas.style.left = '0'
  canvas.style.pointerEvents = 'none'
  
  particleSystem.appendChild(canvas)
  
  // 简单的粒子动画
  const particles: any[] = []
  for (let i = 0; i < 25; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.2
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach(particle => {
      particle.x += particle.vx
      particle.y += particle.vy
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx = -particle.vx
      if (particle.y < 0 || particle.y > canvas.height) particle.vy = -particle.vy
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(37, 99, 235, ${particle.opacity})`
      ctx.fill()
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 生命周期
onMounted(() => {
  initParticleSystem()
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.backtest-page {
  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family-primary);
  overflow-x: hidden;
}

// 沉浸式背景
.immersive-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  
  .particle-system {
    position: absolute;
    width: 100%;
    height: 100%;
  }
  
  .data-stream-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, 
      transparent 30%, 
      rgba(0, 255, 136, 0.03) 50%, 
      transparent 70%);
    animation: dataFlow 8s linear infinite;
  }
  
  .grid-pattern {
    position: absolute;
    width: 100%;
    height: 100%;
    background-image: 
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
  }
}

// 页面头部
.page-header {
  position: relative;
  z-index: 10;
  padding: 24px 40px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .header-left {
    .page-title {
      margin: 0 0 8px 0;
      font-size: 32px;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .page-subtitle {
      margin: 0;
      color: var(--text-secondary);
      font-size: 16px;
    }
  }
  
  .header-right {
    .action-buttons {
      display: flex;
      gap: 16px;
      
      .primary-btn, .secondary-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
      }
      
      .primary-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }
      }
      
      .secondary-btn {
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-primary);
        border: 1px solid rgba(255, 255, 255, 0.1);
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
      }
    }
  }
}

// 主内容区域
.main-content {
  position: relative;
  z-index: 5;
  padding: 40px;
}

// 统计区域
.stats-section {
  margin-bottom: 60px;
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    
    .stat-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 24px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      
      .stat-icon {
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        color: var(--primary);
        font-size: 20px;
      }
      
      .stat-content {
        flex: 1;
        
        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 14px;
          color: var(--text-secondary);
        }
      }
      
      .stat-trend {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        
        &.up {
          background: rgba(16, 185, 129, 0.1);
          color: var(--market-rise);
        }
        
        &.down {
          background: rgba(239, 68, 68, 0.1);
          color: var(--market-fall);
        }
        
        &.stable {
          background: rgba(245, 158, 11, 0.1);
          color: #f59e0b;
        }
      }
    }
  }
}

// 快速回测区域
.quick-backtest-section {
  margin-bottom: 60px;
  
  .section-header {
    text-align: center;
    margin-bottom: 40px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 36px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 18px;
    }
  }
  
  .backtest-interface {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    background: rgba(26, 26, 46, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 32px;
    
    .interface-left {
      .form-group {
        margin-bottom: 24px;
        
        label {
          display: block;
          margin-bottom: 8px;
          color: var(--text-primary);
          font-size: 14px;
          font-weight: 500;
        }
        
        select, input {
          width: 100%;
          padding: 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: var(--text-primary);
          font-size: 14px;
          
          &:focus {
            outline: none;
            border-color: var(--primary);
          }
        }
        
        .date-range {
          display: flex;
          align-items: center;
          gap: 12px;
          
          span {
            color: var(--text-secondary);
          }
        }
        
        .amount-input {
          display: flex;
          align-items: center;
          
          input {
            flex: 1;
          }
          
          .currency {
            margin-left: 8px;
            color: var(--text-secondary);
            font-weight: 500;
          }
        }
      }
    }
    
    .interface-right {
      display: flex;
      flex-direction: column;
      gap: 24px;
      
      .strategy-preview {
        padding: 20px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        
        h3 {
          margin: 0 0 12px 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        p {
          margin: 0 0 16px 0;
          color: var(--text-secondary);
          font-size: 14px;
          line-height: 1.5;
        }
        
        .strategy-params {
          .param-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 4px;
            
            .param-name {
              color: var(--text-secondary);
              font-size: 12px;
            }
            
            .param-value {
              color: var(--primary);
              font-weight: 500;
              font-size: 12px;
            }
          }
        }
      }
      
      .start-backtest-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 16px 32px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }
        
        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
    }
  }
}

// 回测结果区域
.results-section {
  margin-bottom: 60px;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32px;
    
    h2 {
      margin: 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    .result-controls {
      display: flex;
      gap: 16px;
      
      .compare-btn, .export-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        color: var(--text-primary);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
      }
    }
  }
  
  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
    gap: 24px;
    
    .result-card {
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      padding: 24px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-8px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
      }
      
      .result-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 20px;
        
        .result-info {
          flex: 1;
          
          h3 {
            margin: 0 0 8px 0;
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
          }
          
          p {
            margin: 0 0 8px 0;
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.5;
          }
          
          .timeframe-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 8px;
            background: rgba(37, 99, 235, 0.1);
            border: 1px solid rgba(37, 99, 235, 0.3);
            border-radius: 12px;
            font-size: 12px;
            color: #2563eb;
            
            i {
              font-size: 10px;
            }
          }
        }
        
        .result-status {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 4px 8px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          
          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            
            &.completed {
              background: var(--market-rise);
              animation: pulse 2s infinite;
            }
            
            &.running {
              background: #f59e0b;
            }
            
            &.failed {
              background: var(--market-fall);
            }
            
            &.cancelled {
              background: #6b7280;
            }
          }
          
          .status-text {
            font-size: 12px;
            color: var(--text-secondary);
          }
        }
      }
      
      .result-metrics {
        margin-bottom: 20px;
        
        .metric-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          margin-bottom: 12px;
          
          .metric {
            text-align: center;
            
            .metric-label {
              display: block;
              font-size: 12px;
              color: var(--text-secondary);
              margin-bottom: 4px;
            }
            
            .metric-value {
              font-size: 18px;
              font-weight: 600;
              
              &.excellent {
                color: var(--market-rise);
              }
              
              &.good {
                color: #84cc16;
              }
              
              &.normal {
                color: var(--text-primary);
              }
              
              &.poor {
                color: var(--market-fall);
              }
            }
          }
        }
      }
      
      .result-chart {
        height: 120px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 4px;
        position: relative;
        overflow: hidden;
        
        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(37, 99, 235, 0.3), transparent);
          animation: chartFlow 3s linear infinite;
        }
      }
      
      .result-actions {
        display: flex;
        justify-content: space-between;
        
        .action-btn {
          width: 36px;
          height: 36px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
          }
        }
      }
    }
  }
}

// 对比分析区域
.comparison-section {
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32px;
    
    h2 {
      margin: 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    .close-comparison-btn {
      width: 32px;
      height: 32px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 50%;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
      }
    }
  }
  
  .comparison-table {
    background: rgba(26, 26, 46, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    overflow: hidden;
    
    .comparison-grid {
      width: 100%;
      border-collapse: collapse;
      
      th, td {
        padding: 16px;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      }
      
      th {
        background: rgba(0, 0, 0, 0.2);
        color: var(--text-primary);
        font-weight: 600;
        font-size: 14px;
      }
      
      td {
        color: var(--text-primary);
        font-size: 14px;
        
        &.excellent {
          color: var(--market-rise);
        }
        
        &.good {
          color: #84cc16;
        }
        
        &.normal {
          color: var(--text-primary);
        }
        
        &.poor {
          color: var(--market-fall);
        }
      }
      
      .score-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        
        &.excellent {
          background: rgba(16, 185, 129, 0.2);
          color: var(--market-rise);
        }
        
        &.good {
          background: rgba(132, 204, 22, 0.2);
          color: #84cc16;
        }
        
        &.normal {
          background: rgba(255, 255, 255, 0.1);
          color: var(--text-primary);
        }
        
        &.poor {
          background: rgba(239, 68, 68, 0.2);
          color: var(--market-fall);
        }
      }
    }
  }
}

// 时间框架对比弹窗
.timeframe-compare-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .modal-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(5px);
  }
  
  .modal-content {
    position: relative;
    width: 90%;
    max-width: 1200px;
    max-height: 90vh;
    background: rgba(26, 26, 46, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    overflow: hidden;
    
    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 24px 32px;
      background: rgba(0, 0, 0, 0.2);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      
      h3 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .close-btn {
        width: 32px;
        height: 32px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          color: var(--text-primary);
        }
      }
    }
    
    .timeframe-compare-content {
      padding: 32px;
      overflow-y: auto;
      max-height: calc(90vh - 100px);
      
      .compare-overview {
        margin-bottom: 32px;
        
        h4 {
          margin: 0 0 16px 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .overview-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          
          .overview-item {
            padding: 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            
            .overview-label {
              font-size: 12px;
              color: var(--text-secondary);
              margin-bottom: 8px;
            }
            
            .overview-value {
              font-size: 16px;
              font-weight: 600;
              color: var(--text-primary);
            }
          }
        }
      }
      
      .compare-table {
        margin-bottom: 32px;
        
        h4 {
          margin: 0 0 16px 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .comparison-grid {
          width: 100%;
          border-collapse: collapse;
          background: rgba(255, 255, 255, 0.02);
          border-radius: 8px;
          overflow: hidden;
          
          th, td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
          }
          
          th {
            background: rgba(0, 0, 0, 0.2);
            color: var(--text-primary);
            font-weight: 600;
            font-size: 14px;
          }
          
          td {
            color: var(--text-primary);
            font-size: 14px;
            
            &.excellent {
              color: var(--market-rise);
            }
            
            &.good {
              color: #84cc16;
            }
            
            &.normal {
              color: var(--text-primary);
            }
            
            &.poor {
              color: var(--market-fall);
            }
          }
          
          tbody tr:hover {
            background: rgba(255, 255, 255, 0.05);
          }
        }
      }
      
      .compare-charts {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 32px;
        
        .chart-container {
          h4 {
            margin: 0 0 16px 0;
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
          }
          
          .chart {
            height: 300px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
          }
        }
      }
    }
  }
}

// 响应式设计增强
@media (max-width: 1024px) {
  .timeframe-compare-modal {
    .modal-content {
      width: 95%;
      max-height: 95vh;
      
      .timeframe-compare-content {
        padding: 20px;
        
        .compare-charts {
          grid-template-columns: 1fr;
          gap: 20px;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .timeframe-compare-modal {
    .modal-content {
      width: 98%;
      
      .modal-header {
        padding: 16px 20px;
        
        h3 {
          font-size: 20px;
        }
      }
      
      .timeframe-compare-content {
        padding: 16px;
        
        .overview-grid {
          grid-template-columns: repeat(2, 1fr);
        }
        
        .comparison-grid {
          th, td {
            padding: 8px 12px;
            font-size: 12px;
          }
        }
      }
    }
  }
}

// 动画
@keyframes dataFlow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes chartFlow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .backtest-interface {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .results-grid {
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 20px;
    
    .header-content {
      flex-direction: column;
      gap: 16px;
      text-align: center;
    }
  }
  
  .main-content {
    padding: 20px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .backtest-interface {
    padding: 20px;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .comparison-table {
    font-size: 12px;
    
    th, td {
      padding: 8px;
    }
  }
}
</style>