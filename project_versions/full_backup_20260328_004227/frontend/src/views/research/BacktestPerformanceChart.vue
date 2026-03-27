<template>
  <div class="backtest-performance">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-label">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="1" x2="12" y2="23"></line>
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
          {{ t.totalReturn }}
        </div>
        <div :class="['stat-value', { positive: summary.totalReturn > 0, negative: summary.totalReturn < 0 }]">
          {{ summary.totalReturn >= 0 ? '+' : '' }}{{ (summary.totalReturn * 100).toFixed(2) }}%
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-label">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          {{ t.annualReturn }}
        </div>
        <div :class="['stat-value', { positive: summary.annualReturn > 0 }]">
          {{ summary.annualReturn >= 0 ? '+' : '' }}{{ (summary.annualReturn * 100).toFixed(2) }}%
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-label">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
            <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
          </svg>
          {{ t.sharpeRatio }}
        </div>
        <div :class="['stat-value', { positive: summary.sharpeRatio > 1 }]">
          {{ summary.sharpeRatio.toFixed(2) }}
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-label">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
            <polyline points="17 18 23 18 23 12"></polyline>
          </svg>
          {{ t.maxDrawdown }}
        </div>
        <div class="stat-value negative">
          {{ (summary.maxDrawdown * 100).toFixed(2) }}%
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-label">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <circle cx="12" cy="12" r="6"></circle>
            <circle cx="12" cy="12" r="2"></circle>
          </svg>
          {{ t.winRate }}
        </div>
        <div :class="['stat-value', { positive: summary.winRate > 50 }]">
          {{ summary.winRate.toFixed(1) }}%
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-label">
          <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 3v18M3 12h18"></path>
            <line x1="18" y1="6" x2="6" y2="18"></line>
          </svg>
          {{ t.profitLossRatio }}
        </div>
        <div :class="['stat-value', { positive: summary.profitLossRatio > 1 }]">
          {{ summary.profitLossRatio.toFixed(2) }}
        </div>
      </div>
    </div>

    <!-- 净值曲线图 -->
    <div class="chart-section">
      <div class="chart-wrapper">
        <TVLineChart
          v-if="equityChartData.strategyData.length > 0"
          :title="t.equityCurve"
          :strategy-data="equityChartData.strategyData"
          :benchmark-data="equityChartData.benchmarkData"
          :dates="equityChartData.dates"
          :strategy-label="equityChartData.strategyLabel"
          :benchmark-label="equityChartData.benchmarkLabel"
          :strategy-color="equityChartData.strategyColor"
          :benchmark-color="equityChartData.benchmarkColor"
          :show-period-selector="true"
          :resizable="true"
          :locale="props.isZh ? 'zh' : 'en'"
        />
        <div v-else class="chart-empty" v-loading="loading">
          <span>暂无数据</span>
        </div>
      </div>
    </div>

    <!-- 双图表行 -->
    <div class="charts-row">
      <!-- 回撤图 -->
      <div class="chart-section half">
        <div class="chart-header">
          <h3>
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
              <polyline points="17 18 23 18 23 12"></polyline>
            </svg>
            {{ t.drawdownAnalysis }}
          </h3>
        </div>
        <div class="chart-wrapper" :style="{ height: drawdownChartHeight + 'px' }">
          <div ref="drawdownChartRef" class="chart" v-loading="loading"></div>
        </div>
        <div class="resize-handle" @mousedown="startResizeDrawdown">
          <div class="resize-line"></div>
        </div>
      </div>

      <!-- 月度收益 -->
      <div class="chart-section half">
        <div class="chart-header">
          <h3>
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            {{ t.monthlyReturns }}
          </h3>
        </div>
        <div class="chart-wrapper" :style="{ height: monthlyChartHeight + 'px' }">
          <div ref="monthlyChartRef" class="chart" v-loading="loading"></div>
        </div>
        <div class="resize-handle" @mousedown="startResizeMonthly">
          <div class="resize-line"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import TVLineChart, { type Time } from '@/components/charts/TVLineChart.vue'

// Props
interface Props {
  taskId: string
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isZh: true
})

// 多语言文本
const t = computed(() => ({
  totalReturn: props.isZh ? '总收益率' : 'Total Return',
  annualReturn: props.isZh ? '年化收益' : 'Annual Return',
  sharpeRatio: props.isZh ? '夏普比率' : 'Sharpe Ratio',
  maxDrawdown: props.isZh ? '最大回撤' : 'Max Drawdown',
  winRate: props.isZh ? '胜率' : 'Win Rate',
  profitLossRatio: props.isZh ? '盈亏比' : 'Profit/Loss',
  equityCurve: props.isZh ? '净值曲线' : 'Equity Curve',
  drawdownAnalysis: props.isZh ? '回撤分析' : 'Drawdown Analysis',
  monthlyReturns: props.isZh ? '月度收益' : 'Monthly Returns',
  drawdown: props.isZh ? '回撤' : 'Drawdown',
  monthlyProfit: props.isZh ? '月收益' : 'Monthly'
}))

// 状态
const loading = ref(false)

// 图表引用
const equityChartRef = ref<HTMLElement>()
const drawdownChartRef = ref<HTMLElement>()
const monthlyChartRef = ref<HTMLElement>()

// 图表实例
let equityChartInstance: echarts.ECharts | null = null
let drawdownChartInstance: echarts.ECharts | null = null
let monthlyChartInstance: echarts.ECharts | null = null

// 汇总数据
const summary = ref({
  totalReturn: 0.45,
  annualReturn: 0.18,
  sharpeRatio: 1.85,
  maxDrawdown: -0.12,
  winRate: 58.5,
  profitLossRatio: 1.65
})

// 净值数据
const equityData = ref({
  dates: [] as string[],
  values: [] as number[],
  benchmark: [] as number[]
})

// 净值曲线数据 - 适配TVLineChart
const equityChartData = computed(() => {
  const dates = equityData.value.dates
  const values = equityData.value.values
  const benchmark = equityData.value.benchmark

  if (!dates.length || !values.length) {
    return {
      strategyData: [],
      benchmarkData: [],
      dates: [],
      strategyLabel: '策略',
      benchmarkLabel: '基准',
      strategyColor: '#ef5350',
      benchmarkColor: '#787b86'
    }
  }

  const strategyData = dates.map((date, index) => ({
    time: date as Time,
    value: values[index]
  }))

  const benchmarkData = benchmark.length > 0
    ? dates.map((date, index) => ({
        time: date as Time,
        value: benchmark[index]
      }))
    : []

  // 根据收益率设置颜色 - 红涨绿跌
  const lastValue = values[values.length - 1]
  const firstValue = values[0]
  const returnPct = (lastValue - firstValue) / firstValue
  const strategyColor = returnPct >= 0 ? '#ef5350' : '#26a69a'

  return {
    strategyData,
    benchmarkData,
    dates,
    strategyLabel: '策略',
    benchmarkLabel: '基准',
    strategyColor,
    benchmarkColor: '#787b86'
  }
})

// 回撤数据
const drawdownData = ref({
  dates: [] as string[],
  values: [] as number[]
})

// 月度收益数据
const monthlyReturns = ref({
  months: [] as string[],
  returns: [] as number[]
})

// 图表高度持久化
const CHART_HEIGHT_KEY = 'myquant-backtest-chart-heights'
const equityChartHeight = ref(380)
const drawdownChartHeight = ref(300)
const monthlyChartHeight = ref(300)

// 从 localStorage 加载保存的高度
const loadSavedHeights = () => {
  try {
    const saved = localStorage.getItem(CHART_HEIGHT_KEY)
    if (saved) {
      const heights = JSON.parse(saved)
      if (heights.equity) equityChartHeight.value = heights.equity
      if (heights.drawdown) drawdownChartHeight.value = heights.drawdown
      if (heights.monthly) monthlyChartHeight.value = heights.monthly
    }
  } catch (e) {
    console.warn('Failed to load saved chart heights:', e)
  }
}

// 保存高度到 localStorage
const saveHeights = () => {
  try {
    const heights = {
      equity: equityChartHeight.value,
      drawdown: drawdownChartHeight.value,
      monthly: monthlyChartHeight.value
    }
    localStorage.setItem(CHART_HEIGHT_KEY, JSON.stringify(heights))
  } catch (e) {
    console.warn('Failed to save chart heights:', e)
  }
}

// 调整大小相关
const isResizingEquity = ref(false)
const isResizingDrawdown = ref(false)
const isResizingMonthly = ref(false)
const resizeStartY = ref(0)
const resizeStartHeight = ref(0)

const startResizeEquity = (e: MouseEvent) => {
  isResizingEquity.value = true
  resizeStartY.value = e.clientY
  resizeStartHeight.value = equityChartHeight.value
  document.addEventListener('mousemove', handleResizeEquity)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'ns-resize'
  document.body.style.userSelect = 'none'
}

const startResizeDrawdown = (e: MouseEvent) => {
  isResizingDrawdown.value = true
  resizeStartY.value = e.clientY
  resizeStartHeight.value = drawdownChartHeight.value
  document.addEventListener('mousemove', handleResizeDrawdown)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'ns-resize'
  document.body.style.userSelect = 'none'
}

const startResizeMonthly = (e: MouseEvent) => {
  isResizingMonthly.value = true
  resizeStartY.value = e.clientY
  resizeStartHeight.value = monthlyChartHeight.value
  document.addEventListener('mousemove', handleResizeMonthly)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = 'ns-resize'
  document.body.style.userSelect = 'none'
}

const handleResizeEquity = (e: MouseEvent) => {
  if (!isResizingEquity.value) return
  const delta = e.clientY - resizeStartY.value
  const newHeight = Math.max(200, Math.min(600, resizeStartHeight.value + delta))
  equityChartHeight.value = newHeight
  equityChartInstance?.resize()
}

const handleResizeDrawdown = (e: MouseEvent) => {
  if (!isResizingDrawdown.value) return
  const delta = e.clientY - resizeStartY.value
  const newHeight = Math.max(200, Math.min(600, resizeStartHeight.value + delta))
  drawdownChartHeight.value = newHeight
  drawdownChartInstance?.resize()
}

const handleResizeMonthly = (e: MouseEvent) => {
  if (!isResizingMonthly.value) return
  const delta = e.clientY - resizeStartY.value
  const newHeight = Math.max(200, Math.min(600, resizeStartHeight.value + delta))
  monthlyChartHeight.value = newHeight
  monthlyChartInstance?.resize()
}

const stopResize = () => {
  if (isResizingEquity.value || isResizingDrawdown.value || isResizingMonthly.value) {
    saveHeights()
  }
  isResizingEquity.value = false
  isResizingDrawdown.value = false
  isResizingMonthly.value = false
  document.removeEventListener('mousemove', handleResizeEquity)
  document.removeEventListener('mousemove', handleResizeDrawdown)
  document.removeEventListener('mousemove', handleResizeMonthly)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

// 生成模拟数据
const generateMockData = () => {
  // 生成日期序列（2年）
  const dates: string[] = []
  const values: number[] = [1.0]
  const benchmark: number[] = [1.0]
  const drawdowns: number[] = [0]

  const startDate = new Date('2022-01-01')
  const endDate = new Date('2024-01-01')

  for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
    if (d.getDay() !== 0 && d.getDay() !== 6) { // 跳过周末
      dates.push(d.toISOString().split('T')[0])

      // 随机收益率，带趋势
      const dailyReturn = (Math.random() - 0.45) * 0.03
      const benchmarkReturn = (Math.random() - 0.48) * 0.02

      values.push(values[values.length - 1] * (1 + dailyReturn))
      benchmark.push(benchmark[benchmark.length - 1] * (1 + benchmarkReturn))

      // 计算回撤
      const peak = Math.max(...values)
      drawdowns.push((values[values.length - 1] - peak) / peak)
    }
  }

  // 月度收益
  const months: string[] = []
  const returns: number[] = []
  for (let m = 0; m < 24; m++) {
    const date = new Date(2022, m, 1)
    months.push(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`)
    returns.push((Math.random() - 0.4) * 0.1)
  }

  return { dates, values, benchmark, drawdowns, months, returns }
}

// 加载数据
const loadData = async () => {
  loading.value = true

  try {
    const response = await axios.post('/api/v1/validation/backtest/performance', {
      task_id: props.taskId
    })

    if (response.data.success) {
      const data = response.data.data
      summary.value = data.summary
      equityData.value = data.equity
      drawdownData.value = data.drawdown
      monthlyReturns.value = data.monthly

      renderEquityChart()
      renderDrawdownChart()
      renderMonthlyChart()
    } else {
      loadMockData()
    }
  } catch (error: any) {
    console.warn('API调用失败，使用模拟数据:', error.message)
    loadMockData()
  } finally {
    loading.value = false
  }
}

// 加载模拟数据
const loadMockData = () => {
  const mockData = generateMockData()

  equityData.value = {
    dates: mockData.dates,
    values: mockData.values,
    benchmark: mockData.benchmark
  }

  drawdownData.value = {
    dates: mockData.dates,
    values: mockData.drawdowns
  }

  monthlyReturns.value = {
    months: mockData.months,
    returns: mockData.returns
  }

  renderEquityChart()
  renderDrawdownChart()
  renderMonthlyChart()
}

// 深色主题配色
const darkTheme = {
  background: '#1e222d',
  text: '#d1d4dc',
  textSecondary: '#787b86',
  border: '#2a2e39',
  up: '#2962ff',
  down: '#26a69a',
  accent: '#2962ff',
  benchmark: '#787b86'
}

// 渲染净值曲线图
const renderEquityChart = () => {
  if (!equityChartRef.value) return

  if (!equityChartInstance) {
    equityChartInstance = echarts.init(equityChartRef.value, 'dark')
  }

  const dates = equityData.value.dates
  const values = equityData.value.values
  const benchmark = equityData.value.benchmark

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: darkTheme.background,
      borderColor: darkTheme.border,
      textStyle: { color: darkTheme.text },
      formatter: (params: any) => {
        let result = `<div style="padding: 8px;">
          <div style="font-weight: bold; margin-bottom: 4px;">${params[0].name}</div>`
        params.forEach((param: any) => {
          result += `<div>${param.marker}${param.seriesName}: ${param.value.toFixed(4)}</div>`
        })
        result += '</div>'
        return result
      }
    },
    legend: {
      data: [t.value.equityCurve, '基准'],
      top: 10,
      textStyle: { color: darkTheme.text }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '18%',
      top: '18%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { color: darkTheme.textSecondary, interval: 'auto' },
      axisLine: { lineStyle: { color: darkTheme.border } },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: darkTheme.textSecondary,
        formatter: (v: number) => v.toFixed(2)
      },
      axisLine: { lineStyle: { color: darkTheme.border } },
      splitLine: { lineStyle: { color: darkTheme.border } }
    },
    series: [
      {
        name: t.value.equityCurve,
        type: 'line',
        data: values,
        symbol: 'none',
        lineStyle: { color: darkTheme.accent, width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(41, 98, 255, 0.3)' },
            { offset: 1, color: 'rgba(41, 98, 255, 0.05)' }
          ])
        }
      },
      {
        name: '基准',
        type: 'line',
        data: benchmark,
        symbol: 'none',
        lineStyle: { color: darkTheme.benchmark, width: 1.5, type: 'dashed' }
      }
    ],
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
        bottom: 8,
        borderColor: darkTheme.border,
        backgroundColor: '#131722',
        fillerColor: 'rgba(41, 98, 255, 0.2)',
        handleStyle: {
          color: darkTheme.accent,
          borderColor: darkTheme.accent
        },
        textStyle: { color: darkTheme.textSecondary }
      }
    ]
  }

  equityChartInstance.setOption(option)
}

// 渲染回撤图
const renderDrawdownChart = () => {
  if (!drawdownChartRef.value) return

  if (!drawdownChartInstance) {
    drawdownChartInstance = echarts.init(drawdownChartRef.value, 'dark')
  }

  const dates = drawdownData.value.dates
  const values = drawdownData.value.values

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: darkTheme.background,
      borderColor: darkTheme.border,
      textStyle: { color: darkTheme.text },
      formatter: (params: any) => {
        return `<div style="padding: 8px;">
          <div style="font-weight: bold; margin-bottom: 4px;">${params[0].name}</div>
          <div>${t.value.drawdown}: <span style="color: #26a69a;">${(params[0].value * 100).toFixed(2)}%</span></div>
        </div>`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { color: darkTheme.textSecondary, interval: 'auto' },
      axisLine: { lineStyle: { color: darkTheme.border } },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      min: -0.2,
      max: 0,
      axisLabel: {
        color: darkTheme.textSecondary,
        formatter: (v: number) => (v * 100).toFixed(0) + '%'
      },
      axisLine: { lineStyle: { color: darkTheme.border } },
      splitLine: { lineStyle: { color: darkTheme.border } }
    },
    series: [
      {
        name: t.value.drawdown,
        type: 'line',
        data: values,
        symbol: 'none',
        lineStyle: { color: darkTheme.down, width: 1.5 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(38, 166, 154, 0.3)' },
            { offset: 1, color: 'rgba(38, 166, 154, 0.05)' }
          ])
        }
      }
    ]
  }

  drawdownChartInstance.setOption(option)
}

// 渲染月度收益图
const renderMonthlyChart = () => {
  if (!monthlyChartRef.value) return

  if (!monthlyChartInstance) {
    monthlyChartInstance = echarts.init(monthlyChartRef.value, 'dark')
  }

  const months = monthlyReturns.value.months
  const returns = monthlyReturns.value.returns

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: darkTheme.background,
      borderColor: darkTheme.border,
      textStyle: { color: darkTheme.text },
      formatter: (params: any) => {
        const r = params[0].value
        return `<div style="padding: 8px;">
          <div style="font-weight: bold; margin-bottom: 4px;">${params[0].name}</div>
          <div style="color: ${r >= 0 ? '#ef5350' : '#26a69a'};">${r >= 0 ? '+' : ''}${(r * 100).toFixed(2)}%</div>
        </div>`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: { color: darkTheme.textSecondary, interval: 2, rotate: 45 },
      axisLine: { lineStyle: { color: darkTheme.border } },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: darkTheme.textSecondary,
        formatter: (v: number) => (v * 100).toFixed(0) + '%'
      },
      axisLine: { lineStyle: { color: darkTheme.border } },
      splitLine: { lineStyle: { color: darkTheme.border } }
    },
    series: [
      {
        name: t.value.monthlyProfit,
        type: 'bar',
        data: returns,
        itemStyle: {
          color: (params: any) => params.value >= 0 ? darkTheme.up : darkTheme.down,
          borderRadius: [2, 2, 0, 0]
        }
      }
    ]
  }

  monthlyChartInstance.setOption(option)
}

// 窗口大小变化
const handleResize = () => {
  equityChartInstance?.resize()
  drawdownChartInstance?.resize()
  monthlyChartInstance?.resize()
}

// 监听语言变化，重新渲染图表
watch(() => props.isZh, () => {
  // 销毁并重新创建图表实例以确保完全更新
  equityChartInstance?.dispose()
  equityChartInstance = null
  drawdownChartInstance?.dispose()
  drawdownChartInstance = null
  monthlyChartInstance?.dispose()
  monthlyChartInstance = null
  // 使用setTimeout确保DOM更新后再渲染
  setTimeout(() => {
    renderEquityChart()
    renderDrawdownChart()
    renderMonthlyChart()
  }, 0)
})

// 生命周期
onMounted(() => {
  loadSavedHeights()
  loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  equityChartInstance?.dispose()
  drawdownChartInstance?.dispose()
  monthlyChartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})

defineExpose({
  refresh: loadData
})
</script>

<style scoped lang="scss">
.backtest-performance {
  width: 100%;
  box-sizing: border-box;
  margin-bottom: 16px;

  // Element Plus深色主题覆盖
  :deep(.el-radio-group) {
    .el-radio-button__inner {
      background: var(--bg-secondary, #1e222d);
      border-color: var(--border-color, #2a2e39);
      color: var(--text-secondary, #787b86);
    }

    .el-radio-button__original-radio:checked + .el-radio-button__inner {
      background: var(--accent-blue, #2962ff);
      border-color: var(--accent-blue, #2962ff);
      color: white;
    }
  }
}

// 统计行 - 与Backtest Configuration对齐
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  box-sizing: border-box;
  margin-bottom: 16px;

  @media (max-width: 900px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }

  .stat-item {
    background: var(--bg-secondary, #1e222d);
    padding: 14px;
    border-radius: 8px;
    border: 1px solid var(--border-color, #2a2e39);
    text-align: center;

    .stat-label {
      font-size: 12px;
      color: var(--text-primary, #d1d4dc);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;

      .icon-xs {
        width: 24px;
        height: 24px;
        flex-shrink: 0;
      }
    }

    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: var(--text-primary, #d1d4dc);

      &.positive {
        color: #ef5350;
      }

      &.negative {
        color: #26a69a;
      }
    }
  }
}

// 图表区块 - 与Backtest Configuration对齐
.chart-section {
  background: var(--bg-secondary, #1e222d);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  position: relative;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    h3 {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      margin: 0;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .icon-sm {
      width: 16px;
      height: 16px;
      color: inherit;
    }
  }

  .chart-wrapper {
    position: relative;
    min-height: 200px;
  }

  .chart {
    width: 100%;
    height: 100%;
    background: var(--bg-primary, #131722);
    border-radius: 4px;
  }

  .chart-empty {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted, #787b86);
    background: var(--bg-primary, #131722);
    border-radius: 4px;
  }

  .resize-handle {
    position: absolute;
    bottom: -12px;
    left: 0;
    right: 0;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: ns-resize;
    z-index: 10;
    background: transparent;
  }

  .resize-line {
    width: 40px;
    height: 4px;
    background: var(--text-secondary, #787b86);
    border-radius: 2px;
    opacity: 0.3;
    transition: opacity 0.2s;
  }

  .resize-handle:hover .resize-line {
    opacity: 1;
    background: var(--accent-blue, #2962ff);
  }
}
// 双图表行
.charts-row {
  display: flex;
  gap: 16px;
  width: 100%;
  align-items: flex-start;
  box-sizing: border-box;
}

// 半宽图表卡片 - 独立卡片样式
.chart-section.half {
  flex: 1;
  margin-bottom: 0;
  padding: 20px;
  background: var(--bg-secondary, #1e222d);
  border-radius: 8px;
  border: none;
  height: auto;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

@media (max-width: 1200px) {
  .charts-row {
    flex-direction: column;
  }

  .chart-section.half {
    margin-bottom: 16px;
  }
}
</style>
