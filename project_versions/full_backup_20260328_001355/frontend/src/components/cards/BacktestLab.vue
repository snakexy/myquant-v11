<template>
  <n-card class="backtest-lab" hoverable>
    <template #header>
      <div class="card-header">
        <div class="card-icon">
          <n-icon size="24" color="#f59e0b">
            <Flask />
          </n-icon>
        </div>
        <div class="card-title">
          <h3>回测实验室</h3>
          <p class="card-subtitle">策略回测与优化</p>
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
              <n-doption @click="loadTemplate">
                <template #icon>
                  <n-icon><Document /></n-icon>
                </template>
                加载模板
              </n-doption>
              <n-doption @click="saveConfig">
                <template #icon>
                  <n-icon><Save /></n-icon>
                </template>
                保存配置
              </n-doption>
              <n-doption @click="exportResults">
                <template #icon>
                  <n-icon><Download /></n-icon>
                </template>
                导出结果
              </n-doption>
            </template>
          </n-dropdown>
        </div>
      </div>
    </template>
    
    <div class="card-content">
      <!-- 回测配置 -->
      <div class="config-section">
        <n-tabs v-model:value="activeTab" type="segment">
          <n-tab-pane name="basic" tab="基础配置">
            <div class="config-grid">
              <div class="config-item">
                <n-label>策略类型</n-label>
                <n-select
                  v-model:value="config.strategyType"
                  :options="strategyOptions"
                  placeholder="选择策略类型"
                />
              </div>
              <div class="config-item">
                <n-label>股票代码</n-label>
                <n-dynamic-tags
                  v-model:value="config.symbols"
                  :max="10"
                  placeholder="输入股票代码，如 000001.SZ"
                />
              </div>
              <div class="config-item">
                <n-label>回测周期</n-label>
                <n-date-picker
                  v-model:value="config.dateRange"
                  type="daterange"
                  clearable
                />
              </div>
              <div class="config-item">
                <n-label>初始资金</n-label>
                <n-input-number
                  v-model:value="config.initialCapital"
                  :min="10000"
                  :max="100000000"
                  :precision="2"
                  placeholder="1000000"
                />
              </div>
            </div>
          </n-tab-pane>
          
          <n-tab-pane name="advanced" tab="高级配置">
            <div class="config-grid">
              <div class="config-item">
                <n-label>基准指数</n-label>
                <n-select
                  v-model:value="config.benchmark"
                  :options="benchmarkOptions"
                  placeholder="选择基准指数"
                  clearable
                />
              </div>
              <div class="config-item">
                <n-label>手续费率</n-label>
                <n-input-number
                  v-model:value="config.commissionRate"
                  :min="0"
                  :max="0.01"
                  :step="0.0001"
                  :precision="4"
                  placeholder="0.0003"
                />
              </div>
              <div class="config-item">
                <n-label>滑点模型</n-label>
                <n-select
                  v-model:value="config.slippageModel"
                  :options="slippageOptions"
                  placeholder="选择滑点模型"
                />
              </div>
              <div class="config-item">
                <n-label>仓位管理</n-label>
                <n-select
                  v-model:value="config.positionSizing"
                  :options="positionSizingOptions"
                  placeholder="选择仓位管理方式"
                />
              </div>
            </div>
          </n-tab-pane>
          
          <n-tab-pane name="optimization" tab="参数优化">
            <div class="config-grid">
              <div class="config-item">
                <n-label>优化目标</n-label>
                <n-select
                  v-model:value="config.optimizationTarget"
                  :options="optimizationOptions"
                  placeholder="选择优化目标"
                />
              </div>
              <div class="config-item">
                <n-label>参数范围</n-label>
                <div class="parameter-ranges">
                  <div
                    v-for="(range, index) in config.parameterRanges"
                    :key="index"
                    class="parameter-range"
                  >
                    <n-input
                      v-model:value="range.parameter"
                      placeholder="参数名"
                      style="margin-bottom: 8px;"
                    />
                    <n-input-number
                      v-model:value="range.min"
                      placeholder="最小值"
                      style="margin-bottom: 8px;"
                    />
                    <n-input-number
                      v-model:value="range.max"
                      placeholder="最大值"
                      style="margin-bottom: 8px;"
                    />
                    <n-input-number
                      v-model:value="range.step"
                      placeholder="步长"
                    />
                    <n-button
                      @click="removeParameterRange(index)"
                      size="small"
                      type="error"
                      quaternary
                    >
                      <template #icon>
                        <n-icon><Remove /></n-icon>
                      </template>
                    </n-button>
                  </div>
                  <n-button
                    @click="addParameterRange"
                    size="small"
                    type="primary"
                    dashed
                  >
                    <template #icon>
                      <n-icon><Add /></n-icon>
                    </template>
                    添加参数
                  </n-button>
                </div>
              </div>
            </div>
          </n-tab-pane>
        </n-tabs>
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-section">
        <n-space>
          <n-button
            type="primary"
            :loading="isRunning"
            @click="runBacktest"
          >
            <template #icon>
              <n-icon><Play /></n-icon>
            </template>
            {{ isOptimizing ? '开始优化' : '开始回测' }}
          </n-button>
          <n-button
            type="info"
            @click="runComparison"
            :disabled="config.symbols.length < 2"
          >
            <template #icon>
              <n-icon><GitCompare /></n-icon>
            </template>
            模型对比
          </n-button>
          <n-button
            @click="runComparison"
            :disabled="config.symbols.length < 2"
          >
            <template #icon>
              <n-icon><GitCompare /></n-icon>
            </template>
            对比回测
          </n-button>
          <n-button
            @click="stopBacktest"
            :disabled="!isRunning"
            type="error"
          >
            <template #icon>
              <n-icon><Stop /></n-icon>
            </template>
            停止
          </n-button>
        </n-space>
      </div>
      
      <!-- 回测结果 -->
      <div v-if="backtestResults.length > 0" class="results-section">
        <div class="results-header">
          <n-space justify="space-between">
            <n-text>回测结果 ({{ backtestResults.length }}个)</n-text>
            <n-button @click="clearResults" size="small" quaternary>
              <template #icon>
                <n-icon><Trash /></n-icon>
              </template>
              清空结果
            </n-button>
          </n-space>
        </div>
        
        <div class="results-tabs">
          <n-tabs v-model:value="resultsTab" type="card">
            <n-tab-pane name="overview" tab="概览">
              <div class="overview-grid">
                <div
                  v-for="result in backtestResults"
                  :key="result.id"
                  class="overview-item"
                  @click="selectResult(result)"
                  :class="{ active: selectedResult?.id === result.id }"
                >
                  <div class="result-header">
                    <n-text strong>{{ result.strategyName }}</n-text>
                    <n-tag :type="getResultStatusType(result.status)" size="small">
                      {{ result.status }}
                    </n-tag>
                  </div>
                  <div class="result-metrics">
                    <div class="metric">
                      <span class="metric-label">总收益</span>
                      <span class="metric-value" :class="getReturnClass(result.totalReturn)">
                        {{ (result.totalReturn * 100).toFixed(2) }}%
                      </span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">夏普比率</span>
                      <span class="metric-value">{{ result.sharpeRatio.toFixed(2) }}</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">最大回撤</span>
                      <span class="metric-value negative">{{ (result.maxDrawdown * 100).toFixed(2) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </n-tab-pane>
            
            <n-tab-pane name="details" tab="详细对比">
              <div class="comparison-table">
                <n-data-table
                  :columns="comparisonColumns"
                  :data="backtestResults"
                  size="small"
                  striped
                  :pagination="false"
                />
              </div>
            </n-tab-pane>
            
           <n-tab-pane name="charts" tab="图表分析">
             <div class="charts-container">
               <div class="chart-item">
                 <h4>净值曲线</h4>
                 <TVLineChart
                   v-if="equityChartData.strategyData.length > 0"
                   :title="''"
                   :strategy-data="equityChartData.strategyData"
                   :extra-series="equityChartData.extraSeries"
                   :dates="equityChartData.dates"
                   :strategy-label="equityChartData.strategyLabel"
                   :strategy-color="equityChartData.strategyColor"
                   :show-period-selector="true"
                   :resizable="true"
                   :height="300"
                 />
                 <div v-else class="chart-empty">
                   <span>暂无数据</span>
                 </div>
               </div>
               <div class="chart-item">
                 <h4>收益分布</h4>
                 <BaseChart
                   :option="returnDistributionOption"
                   width="100%"
                   height="300px"
                 />
               </div>
               <div v-if="backtestResults.some(r => r.strategyName.includes('多目标优化'))" class="chart-item">
                 <h4>Pareto前沿分析</h4>
                 <BaseChart
                   :option="paretoFrontOption"
                   width="100%"
                   height="400px"
                 />
               </div>
             </div>
           </n-tab-pane>
          </n-tabs>
        </div>
      </div>
      
      <!-- 实时进度 -->
      <div v-if="isRunning" class="progress-section">
        <n-card title="回测进度" size="small">
          <div class="progress-content">
            <n-progress
              type="line"
              :percentage="progress.percentage"
              :status="progress.status"
              :show-indicator="progress.showIndicator"
            />
            <div class="progress-info">
              <n-space>
                <n-text>当前进度: {{ progress.current }}/{{ progress.total }}</n-text>
                <n-text>预计剩余: {{ progress.estimatedTime }}</n-text>
              </n-space>
            </div>
          </div>
        </n-card>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NIcon, NButton, NDropdown, NDropdownOption, NTabs, NTabPane, NLabel, NSelect, NDynamicTags, NDatePicker, NInputNumber, NSpace, NText, NDataTable, NTag, NProgress, NInput } from 'naive-ui'
import { EllipsisVertical, Document, Save, Download, Flask, Play, GitCompare, Stop, Trash, Remove, Add, Settings, GitBranch } from '@vicons/ionicons5'
import BaseChart from '../charts/BaseChart.vue'
import type { EChartsOption } from 'echarts'
import TVLineChart, { type Time } from '../charts/TVLineChart.vue'

interface BacktestConfig {
  strategyType: string
  symbols: string[]
  dateRange: [number, number] | null
  initialCapital: number
  benchmark: string
  commissionRate: number
  slippageModel: string
  positionSizing: string
  optimizationTarget: string
  optimizationAlgorithm: string
  parameterRanges: Array<{
    parameter: string
    min: number
    max: number
    step: number
  }>
}

interface BacktestResult {
  id: string
  strategyName: string
  status: 'completed' | 'running' | 'failed'
  totalReturn: number
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
  profitLossRatio: number
  totalTrades: number
  equityCurve: Array<{ timestamp: number, value: number }>
  returnDistribution: Array<{ range: string, count: number, return: number }>
}

interface Props {
  onRunBacktest?: (config: BacktestConfig) => Promise<BacktestResult>
  onRunComparison?: (configs: BacktestConfig[]) => Promise<BacktestResult[]>
  onRunOptimization?: (config: BacktestConfig) => Promise<BacktestResult>
  onStopBacktest?: () => void
}

const props = defineProps<Props>()

const emit = defineEmits<{
  configSaved: [config: BacktestConfig]
  resultsExported: [results: BacktestResult[]]
}>()

// 配置状态
const activeTab = ref('basic')
const config = ref<BacktestConfig>({
  strategyType: '',
  symbols: [],
  dateRange: null,
  initialCapital: 1000000,
  benchmark: '',
  commissionRate: 0.0003,
  slippageModel: '',
  positionSizing: '',
  optimizationTarget: 'sharpe_ratio',
  optimizationAlgorithm: 'grid_search',
  parameterRanges: []
})

// 运行状态
const isRunning = ref(false)
const isOptimizing = ref(false)
const progress = ref({
  percentage: 0,
  current: 0,
  total: 100,
  estimatedTime: '计算中...',
  status: 'default' as 'default' | 'success' | 'warning' | 'error',
  showIndicator: true
})

// 结果状态
const resultsTab = ref('overview')
const backtestResults = ref<BacktestResult[]>([])
const selectedResult = ref<BacktestResult | null>(null)

// 选项配置
const strategyOptions = [
  { label: '动量策略', value: 'momentum' },
  { label: '均值回归', value: 'mean_reversion' },
  { label: '突破策略', value: 'breakout' },
  { label: '增强指数', value: 'enhanced_indexing' }
]

const benchmarkOptions = [
  { label: '沪深300', value: '000300.SH' },
  { label: '中证500', value: '000905.SH' },
  { label: '创业板指', value: '399006.SZ' },
  { label: '科创50', value: '000688.SH' }
]

const slippageOptions = [
  { label: '固定滑点', value: 'fixed' },
  { label: '百分比滑点', value: 'percentage' },
  { label: '波动率调整', value: 'volatility' }
]

const positionSizingOptions = [
  { label: '固定数量', value: 'fixed' },
  { label: '百分比资金', value: 'percentage' },
  { label: '波动率调整', value: 'volatility' },
  { label: '凯利公式', value: 'kelly' }
]

const optimizationOptions = [
  { label: '夏普比率', value: 'sharpe_ratio' },
  { label: '总收益', value: 'total_return' },
  { label: '最大回撤', value: 'max_drawdown' },
  { label: '胜率', value: 'win_rate' },
  { label: '信息比率', value: 'information_ratio' },
  { label: '卡尔玛比率', value: 'calmar_ratio' }
]

const algorithmOptions = [
  { label: '网格搜索', value: 'grid_search' },
  { label: '贝叶斯优化', value: 'bayesian' },
  { label: '遗传算法', value: 'genetic' },
  { label: '粒子群优化', value: 'particle_swarm' },
  { label: '模拟退火', value: 'simulated_annealing' }
]

// 对比表格列
const comparisonColumns = computed(() => [
  { title: '策略名称', key: 'strategyName', width: 120 },
  { title: '状态', key: 'status', width: 80, render: (row: BacktestResult) => row.status },
  { title: '总收益', key: 'totalReturn', width: 100, render: (row: BacktestResult) => `${(row.totalReturn * 100).toFixed(2)}%` },
  { title: '夏普比率', key: 'sharpeRatio', width: 100, render: (row: BacktestResult) => row.sharpeRatio.toFixed(2) },
  { title: '最大回撤', key: 'maxDrawdown', width: 100, render: (row: BacktestResult) => `${(row.maxDrawdown * 100).toFixed(2)}%` },
  { title: '胜率', key: 'winRate', width: 80, render: (row: BacktestResult) => `${(row.winRate * 100).toFixed(1)}%` },
  { title: '交易次数', key: 'totalTrades', width: 80 }
])

// 净值曲线配置
const equityCurveOption = computed<EChartsOption>(() => {
  if (backtestResults.value.length === 0) return {}

  const series = backtestResults.value.map(result => ({
    name: result.strategyName,
    type: 'line',
    data: result.equityCurve || [],
    smooth: true
  }))

  return {
    title: { text: '净值曲线对比' },
    tooltip: { trigger: 'axis' },
    legend: { data: backtestResults.value.map(r => r.strategyName) },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'time' },
    yAxis: { type: 'value' },
    series
  }
})

// 净值曲线数据 - 适配TVLineChart
const equityChartData = computed(() => {
  if (backtestResults.value.length === 0) {
    return {
      strategyData: [],
      extraSeries: [],
      dates: [],
      strategyLabel: '策略',
      strategyColor: '#ef5350'
    }
  }

  // 使用第一个策略作为主策略
  const firstResult = backtestResults.value[0]
  const dates: string[] = []

  // 从第一个策略的equityCurve生成日期
  if (firstResult.equityCurve && firstResult.equityCurve.length > 0) {
    const today = new Date()
    for (let i = firstResult.equityCurve.length - 1; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      dates.push(date.toISOString().split('T')[0])
    }
  }

  // 第一个策略的数据
  const strategyData = dates.map((date, index) => ({
    time: date as Time,
    value: firstResult.equityCurve?.[index]?.value || 1
  }))

  // 其他策略作为额外系列
  const extraSeries = backtestResults.value.slice(1).map((result, idx) => {
    const colors = ['#2962ff', '#9c27b0', '#ff9800', '#26a69a']
    const data = dates.map((date, index) => ({
      time: date as Time,
      value: result.equityCurve?.[index]?.value || 1
    }))
    return {
      data,
      label: result.strategyName,
      color: colors[idx % colors.length]
    }
  })

  // 根据收益率设置颜色 - 红涨绿跌
  const lastValue = strategyData[strategyData.length - 1]?.value || 1
  const firstValue = strategyData[0]?.value || 1
  const returnPct = (lastValue - firstValue) / firstValue
  const strategyColor = returnPct >= 0 ? '#ef5350' : '#26a69a'

  return {
    strategyData,
    extraSeries,
    dates,
    strategyLabel: firstResult.strategyName,
    strategyColor
  }
})

// 收益分布配置
const returnDistributionOption = computed<EChartsOption>(() => {
  if (backtestResults.value.length === 0) return {}
  
  const result = backtestResults.value[0]
  if (!result?.returnDistribution) return {}
  
  return {
    title: { text: '收益分布' },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        data: result.returnDistribution.map(item => ({
          name: item.range,
          value: item.count
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

// Pareto前沿配置
const paretoFrontOption = computed<EChartsOption>(() => {
  const paretoResults = backtestResults.value.filter(r => r.strategyName.includes('多目标优化'))
  if (paretoResults.length === 0) return {}
  
  return {
    title: { text: '多目标优化Pareto前沿', left: 'center' },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const data = params.data
        return `
          <div>
            <strong>${data.name}</strong><br/>
            夏普比率: ${data.value[0].toFixed(3)}<br/>
            总收益率: ${(data.value[1] * 100).toFixed(2)}%<br/>
            最大回撤: ${(data.value[2] * 100).toFixed(2)}%<br/>
            胜率: ${(data.value[3] * 100).toFixed(1)}%
          </div>
        `
      }
    },
    legend: {
      data: ['Pareto最优解', '普通解'],
      top: 30
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '夏普比率',
      nameLocation: 'middle',
      nameGap: 30,
      axisLabel: {
        formatter: '{value}'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '总收益率',
      nameLocation: 'middle',
      nameGap: 40,
      axisLabel: {
        formatter: (value: number) => `${(value * 100).toFixed(0)}%`
      },
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    visualMap: {
      show: true,
      dimension: 2, // 使用最大回撤作为颜色映射
      min: 0,
      max: 0.2,
      inRange: {
        color: ['#50a3ba', '#eac736', '#d94e5d']
      },
      text: ['低回撤', '高回撤'],
      textStyle: {
        color: '#fff'
      },
      calculable: true,
      left: 'right',
      top: 'bottom'
    },
    series: [
      {
        name: 'Pareto最优解',
        type: 'scatter',
        symbolSize: (data: number[]) => {
          // 根据胜率调整点的大小
          return Math.max(10, data[3] * 50)
        },
        data: paretoResults.map(result => ({
          name: result.strategyName,
          value: [
            result.sharpeRatio,
            result.totalReturn,
            result.maxDrawdown,
            result.winRate
          ]
        })),
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 2
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      },
      {
        name: '普通解',
        type: 'scatter',
        symbolSize: (data: number[]) => {
          return Math.max(8, data[3] * 40)
        },
        data: backtestResults.value
          .filter(r => !r.strategyName.includes('多目标优化'))
          .map(result => ({
            name: result.strategyName,
            value: [
              result.sharpeRatio,
              result.totalReturn,
              result.maxDrawdown,
              result.winRate
            ]
          })),
        itemStyle: {
          opacity: 0.6,
          borderColor: '#666',
          borderWidth: 1
        }
      }
    ]
  }
})

// 运行回测
const runBacktest = async () => {
  if (!config.value.strategyType || config.value.symbols.length === 0) {
    return
  }
  
  isRunning.value = true
  progress.value = {
    percentage: 0,
    current: 0,
    total: 100,
    estimatedTime: '计算中...',
    status: 'default',
    showIndicator: true
  }
  
  try {
    let result: BacktestResult
    
    if (props.onRunBacktest) {
      result = await props.onRunBacktest(config.value)
    } else {
      // 模拟回测结果
      result = generateMockResult()
    }
    
    backtestResults.value.unshift(result)
    selectedResult.value = result
    
    // 模拟进度更新
    let progressValue = 0
    const progressInterval = setInterval(() => {
      progressValue += Math.random() * 15
      if (progressValue >= 100) {
        progressValue = 100
        clearInterval(progressInterval)
        isRunning.value = false
      }
      
      progress.value = {
        percentage: progressValue,
        current: Math.floor(progressValue),
        total: 100,
        estimatedTime: Math.max(1, Math.floor((100 - progressValue) / 15)) + '秒',
        status: progressValue > 80 ? 'success' : progressValue > 50 ? 'warning' : 'default',
        showIndicator: true
      }
    }, 1000)
  } catch (error) {
    console.error('回测失败:', error)
    isRunning.value = false
    progress.value.status = 'error'
  }
}

// 运行对比
const runComparison = async () => {
  if (config.value.symbols.length < 2) {
    return
  }
  
  isRunning.value = true
  isOptimizing.value = true
  
  try {
    let results: BacktestResult[]
    
    if (props.onRunComparison) {
      const configs = generateComparisonConfigs()
      results = await props.onRunComparison(configs)
    } else {
      // 模拟对比结果
      results = Array(3).fill(null).map(() => generateMockResult())
    }
    
    backtestResults.value = results
    isRunning.value = false
    isOptimizing.value = false
  } catch (error) {
    console.error('对比回测失败:', error)
    isRunning.value = false
    isOptimizing.value = false
  }
}

// 运行参数优化
const runOptimization = async () => {
  if (!config.value.strategyType || config.value.parameterRanges.length === 0) {
    return
  }
  
  isOptimizing.value = true
  progress.value = {
    percentage: 0,
    current: 0,
    total: 100,
    estimatedTime: '优化中...',
    status: 'default',
    showIndicator: true
  }
  
  try {
    let bestResult: BacktestResult
    
    if (props.onRunOptimization) {
      bestResult = await props.onRunOptimization(config.value)
    } else {
      // 模拟优化过程
      const iterations = 20
      let bestScore = -Infinity
      
      for (let i = 0; i < iterations; i++) {
        const testConfig = generateOptimizedConfig(i)
        const result = generateMockResult()
        
        // 根据优化目标计算综合得分
        let score = 0
        switch (config.value.optimizationTarget) {
          case 'sharpe_ratio':
            score = result.sharpeRatio
            break
          case 'total_return':
            score = result.totalReturn
            break
          case 'max_drawdown':
            score = -result.maxDrawdown // 负值，越小越好
            break
          case 'win_rate':
            score = result.winRate
            break
          case 'information_ratio':
            score = result.sharpeRatio * 0.8 // 模拟信息比率
            break
          case 'calmar_ratio':
            score = result.totalReturn / Math.max(result.maxDrawdown, 0.01) // 模拟卡尔玛比率
            break
          default:
            score = result.sharpeRatio
        }
        
        if (score > bestScore) {
          bestScore = score
          bestResult = result
        }
        
        // 更新进度
        progress.value = {
          percentage: (i / iterations) * 100,
          current: i + 1,
          total: iterations,
          estimatedTime: `${Math.max(1, Math.floor((iterations - i) * 2))}秒`,
          status: i > iterations * 0.8 ? 'success' : i > iterations * 0.5 ? 'warning' : 'default',
          showIndicator: true
        }
        
        // 模拟延迟
        await new Promise(resolve => setTimeout(resolve, 200))
      }
    }
    
    backtestResults.value.unshift(bestResult)
    selectedResult.value = bestResult
  } catch (error) {
    console.error('参数优化失败:', error)
    progress.value.status = 'error'
  } finally {
    isOptimizing.value = false
  }
}

// 运行多目标优化
const runMultiObjectiveOptimization = async () => {
  if (!config.value.strategyType || config.value.parameterRanges.length < 2) {
    return
  }
  
  isOptimizing.value = true
  progress.value = {
    percentage: 0,
    current: 0,
    total: 100,
    estimatedTime: '多目标优化中...',
    status: 'default',
    showIndicator: true
  }
  
  try {
    let paretoResults: BacktestResult[] = []
    
    if (props.onRunOptimization) {
      // 实际项目中调用后端多目标优化API
      const bestResult = await props.onRunOptimization(config.value)
      paretoResults = [bestResult]
    } else {
      // 模拟多目标优化过程 (Pareto前沿)
      const iterations = 50
      const objectives = ['sharpe_ratio', 'total_return', 'max_drawdown']
      const paretoFront: BacktestResult[] = []
      
      for (let i = 0; i < iterations; i++) {
        const testConfig = generateOptimizedConfig(i)
        const result = generateMockResult()
        
        // 检查是否在Pareto前沿上
        let isDominated = false
        for (const existing of paretoFront) {
          if (
            existing.sharpeRatio >= result.sharpeRatio &&
            existing.totalReturn >= result.totalReturn &&
            existing.maxDrawdown <= result.maxDrawdown &&
            (existing.sharpeRatio > result.sharpeRatio ||
             existing.totalReturn > result.totalReturn ||
             existing.maxDrawdown < result.maxDrawdown)
          ) {
            isDominated = true
            break
          }
        }
        
        // 移除被当前结果支配的解
        if (!isDominated) {
          for (let j = paretoFront.length - 1; j >= 0; j--) {
            const existing = paretoFront[j]
            if (
              result.sharpeRatio >= existing.sharpeRatio &&
              result.totalReturn >= existing.totalReturn &&
              result.maxDrawdown <= existing.maxDrawdown &&
              (result.sharpeRatio > existing.sharpeRatio ||
               result.totalReturn > existing.totalReturn ||
               result.maxDrawdown < existing.maxDrawdown)
            ) {
              paretoFront.splice(j, 1)
            }
          }
          paretoFront.push(result)
        }
        
        // 更新进度
        progress.value = {
          percentage: (i / iterations) * 100,
          current: i + 1,
          total: iterations,
          estimatedTime: `${Math.max(1, Math.floor((iterations - i) * 3))}秒`,
          status: i > iterations * 0.8 ? 'success' : i > iterations * 0.5 ? 'warning' : 'default',
          showIndicator: true
        }
        
        // 模拟延迟
        await new Promise(resolve => setTimeout(resolve, 150))
      }
      
      paretoResults = paretoFront.slice(0, 10) // 取前10个Pareto最优解
    }
    
    // 添加多目标优化结果
    paretoResults.forEach((result, index) => {
      result.strategyName = `${config.value.strategyType}_多目标优化_${index + 1}`
    })
    
    backtestResults.value.unshift(...paretoResults)
    selectedResult.value = paretoResults[0]
  } catch (error) {
    console.error('多目标优化失败:', error)
    progress.value.status = 'error'
  } finally {
    isOptimizing.value = false
  }
}

// 生成优化配置
const generateOptimizedConfig = (iteration: number) => {
  const baseConfig = { ...config.value }
  
  // 根据迭代次数调整参数
  config.value.parameterRanges.forEach((range, index) => {
    const factor = 1 + (Math.sin(iteration * 0.5 + index) * 0.1)
    const optimizedValue = range.min + (range.max - range.min) * (0.5 + Math.sin(iteration * 0.3 + index * 0.5) * 0.5)
    baseConfig[range.parameter] = optimizedValue
  })
  
  return baseConfig
}

// 停止回测
const stopBacktest = () => {
  if (props.onStopBacktest) {
    props.onStopBacktest()
  }
  
  isRunning.value = false
  progress.value = {
    percentage: 0,
    current: 0,
    total: 100,
    estimatedTime: '已停止',
    status: 'warning',
    showIndicator: false
  }
}

// 生成对比配置
const generateComparisonConfigs = (): BacktestConfig[] => {
  const strategies = ['momentum', 'mean_reversion', 'breakout']
  return strategies.map((strategy, index) => ({
    ...config.value,
    strategyType: strategy,
    parameterRanges: [
      {
        parameter: `lookback_period`,
        min: 5 + index * 5,
        max: 20 + index * 10,
        step: 5
      }
    ]
  }))
}

// 生成模拟结果
const generateMockResult = (): BacktestResult => {
  const id = `bt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  const totalReturn = (Math.random() - 0.5) * 0.5
  const sharpeRatio = Math.random() * 2 + 0.5
  const maxDrawdown = Math.random() * 0.2 + 0.05
  const winRate = Math.random() * 0.3 + 0.4
  
  return {
    id,
    strategyName: config.value.strategyType || '测试策略',
    status: 'completed',
    totalReturn,
    sharpeRatio,
    maxDrawdown,
    winRate,
    profitLossRatio: winRate / (1 - winRate),
    totalTrades: Math.floor(Math.random() * 1000 + 100),
    equityCurve: generateEquityCurve(totalReturn, maxDrawdown),
    returnDistribution: generateReturnDistribution()
  }
}

// 生成净值曲线
const generateEquityCurve = (totalReturn: number, maxDrawdown: number) => {
  const points = []
  const days = 252 // 一年交易日
  let currentValue = 1
  
  for (let i = 0; i < days; i++) {
    const dailyReturn = (totalReturn / days) + (Math.random() - 0.5) * 0.02
    currentValue *= (1 + dailyReturn)
    
    // 添加回撤
    if (Math.random() < 0.1) {
      currentValue *= (1 - maxDrawdown * 0.1)
    }
    
    points.push({
      timestamp: Date.now() - (days - i) * 24 * 60 * 60 * 1000,
      value: currentValue
    })
  }
  
  return points
}

// 生成收益分布
const generateReturnDistribution = () => {
  return [
    { range: '负收益', count: 20, return: -0.05 },
    { range: '0-5%', count: 30, return: 0.025 },
    { range: '5-10%', count: 25, return: 0.075 },
    { range: '10-15%', count: 15, return: 0.125 },
    { range: '15-20%', count: 8, return: 0.175 },
    { range: '20%+', count: 2, return: 0.25 }
  ]
}

// 获取结果状态类型
const getResultStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    completed: 'success',
    running: 'info',
    failed: 'error'
  }
  return typeMap[status] || 'default'
}

// 获取收益样式
const getReturnClass = (returnValue: number) => {
  return returnValue > 0 ? 'positive' : 'negative'
}

// 选择结果
const selectResult = (result: BacktestResult) => {
  selectedResult.value = result
}

// 清空结果
const clearResults = () => {
  backtestResults.value = []
  selectedResult.value = null
}

// 加载模板
const loadTemplate = () => {
  // 加载预设模板
}

// 保存配置
const saveConfig = () => {
  emit('configSaved', config.value)
}

// 导出结果
const exportResults = () => {
  emit('resultsExported', backtestResults.value)
}

// 添加参数范围
const addParameterRange = () => {
  config.value.parameterRanges.push({
    parameter: '',
    min: 0,
    max: 100,
    step: 1
  })
}

// 移除参数范围
const removeParameterRange = (index: number) => {
  config.value.parameterRanges.splice(index, 1)
}

onMounted(() => {
  // 组件初始化
})
</script>

<style lang="scss" scoped>
.backtest-lab {
  height: 100%;
  
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
      background: rgba(245, 158, 11, 0.1);
      border: 1px solid rgba(245, 158, 11, 0.2);
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
    .config-section {
      margin-bottom: 20px;
      
      .config-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 16px;
        
        .config-item {
          .n-label {
            margin-bottom: 8px;
            color: #94a3b8;
          }
        }
      }
      
      .parameter-ranges {
        .parameter-range {
          padding: 16px;
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 8px;
          background: rgba(15, 23, 42, 0.4);
          margin-bottom: 12px;
        }
      }
    }
    
    .action-section {
      margin-bottom: 20px;
      padding: 16px;
      background: rgba(15, 23, 42, 0.4);
      border-radius: 8px;
      border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .results-section {
      .results-header {
        margin-bottom: 16px;
        padding: 12px;
        background: rgba(245, 158, 11, 0.1);
        border-radius: 6px;
        border: 1px solid rgba(245, 158, 11, 0.2);
      }
      
      .results-tabs {
        .overview-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 16px;
          
          .overview-item {
            padding: 16px;
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 8px;
            background: rgba(15, 23, 42, 0.4);
            cursor: pointer;
            transition: all 0.3s ease;
            
            &:hover {
              background: rgba(15, 23, 42, 0.6);
              transform: translateY(-2px);
            }
            
            &.active {
              border-color: #2563eb;
              background: rgba(37, 99, 235, 0.1);
            }
            
            .result-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 12px;
            }
            
            .result-metrics {
              display: grid;
              grid-template-columns: repeat(3, 1fr);
              gap: 8px;
              
              .metric {
                text-align: center;
                
                .metric-label {
                  display: block;
                  font-size: 12px;
                  color: #94a3b8;
                  margin-bottom: 4px;
                }
                
                .metric-value {
                  display: block;
                  font-size: 16px;
                  font-weight: 600;
                  
                  &.positive {
                    color: var(--market-rise);
                  }
                  
                  &.negative {
                    color: var(--market-fall);
                  }
                }
              }
            }
          }
        }
        
        .comparison-table {
          border-radius: 8px;
          overflow: hidden;
        }
        
        .charts-container {
          .chart-item {
            margin-bottom: 20px;

            h4 {
              margin: 0 0 12px 0;
              color: #f8fafc;
            }

            .chart-empty {
              width: 100%;
              height: 300px;
              display: flex;
              align-items: center;
              justify-content: center;
              background: #1e222d;
              border-radius: 8px;
              color: #787b86;
            }
          }
        }
      }
    }
    
    .progress-section {
      .progress-content {
        .progress-info {
          margin-top: 12px;
        }
      }
    }
  }
}
</style>