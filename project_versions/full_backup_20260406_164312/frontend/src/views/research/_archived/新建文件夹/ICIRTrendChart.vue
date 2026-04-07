<template>
  <div class="icir-trend-chart">
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：配置控制 -->
      <div class="controls-panel">
        <div class="panel-section">
          <h4>
            <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
            {{ t.analysisParams }}
          </h4>
          <div class="control-group">
            <label>{{ t.targetPeriod }}</label>
            <el-input-number
              v-model="localTargetPeriod"
              :min="1"
              :max="20"
              size="small"
              @change="loadICIRData"
            />
            <span class="unit">{{ t.day }}</span>
          </div>
          <div class="control-group">
            <label>{{ t.correlationMethod }}</label>
            <el-select v-model="localMethod" size="small" @change="loadICIRData">
              <el-option label="Pearson" value="pearson"></el-option>
              <el-option label="Spearman" value="spearman"></el-option>
            </el-select>
          </div>
        </div>

        <div class="panel-section">
          <h4>
            <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
            {{ t.icStatistics }}
          </h4>
          <div class="stat-row">
            <span class="stat-label">{{ t.icSamples }}</span>
            <span class="stat-value">{{ summary.icCount }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">{{ t.icAbsMean }}</span>
            <span class="stat-value">{{ formatNumber(summary.icAbsMean) }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">{{ t.maxIC }}</span>
            <span class="stat-value positive">{{ formatNumber(summary.maxIC) }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">{{ t.minIC }}</span>
            <span class="stat-value negative">{{ formatNumber(summary.minIC) }}</span>
          </div>
        </div>

        <div class="panel-section">
          <el-button type="primary" @click="loadICIRData" :loading="loading" style="width: 100%">
            <el-icon><Refresh /></el-icon>
            {{ t.refresh }}
          </el-button>
        </div>
      </div>

      <!-- 右侧：图表区域 -->
      <div class="charts-panel">
        <!-- IC时间序列图 -->
        <div class="chart-section">
          <div class="chart-header">
            <h3>
              <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                <polyline points="17 6 23 6 23 12"></polyline>
              </svg>
              {{ t.icTrend }}
            </h3>
            <div class="chart-controls">
              <!-- 图表类型切换 -->
              <el-radio-group v-model="chartType" size="small">
                <el-radio-button label="line">{{ t.lineChart }}</el-radio-button>
                <el-radio-button label="bar">{{ t.barChart }}</el-radio-button>
              </el-radio-group>
            </div>
          </div>
          <div class="chart-wrapper" :style="{ height: icChartHeight + 'px' }">
            <div ref="icChartRef" class="chart" v-loading="loading"></div>
          </div>
          <div class="resize-handle" @mousedown="startResizeIC">
            <div class="resize-line"></div>
          </div>
        </div>

        <!-- 月度IC分解图 -->
        <div class="chart-section">
          <div class="chart-header">
            <h3>
              <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              {{ t.monthlyBreakdown }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

// Props定义
interface Props {
  taskId: string
  targetPeriod?: number
  method?: 'pearson' | 'spearman'
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  targetPeriod: 1,
  method: 'pearson',
  isZh: true
})

// 多语言文本
const t = computed(() => ({
  icMean: props.isZh ? 'IC均值' : 'IC Mean',
  icStd: props.isZh ? 'IC标准差' : 'IC Std',
  irValue: props.isZh ? 'IR值' : 'IR',
  positiveRatio: props.isZh ? '正IC比率' : 'Positive Ratio',
  analysisParams: props.isZh ? '分析参数' : 'Analysis Params',
  targetPeriod: props.isZh ? '目标周期' : 'Target Period',
  correlationMethod: props.isZh ? '相关性方法' : 'Method',
  icStatistics: props.isZh ? 'IC统计' : 'IC Statistics',
  icSamples: props.isZh ? 'IC样本数' : 'IC Samples',
  icAbsMean: props.isZh ? 'IC绝对值均值' : 'IC Abs Mean',
  maxIC: props.isZh ? '最大IC' : 'Max IC',
  minIC: props.isZh ? '最小IC' : 'Min IC',
  refresh: props.isZh ? '刷新数据' : 'Refresh',
  icTrend: props.isZh ? 'IC时间序列趋势' : 'IC Time Series Trend',
  lineChart: props.isZh ? '折线图' : 'Line',
  barChart: props.isZh ? '柱状图' : 'Bar',
  monthlyBreakdown: props.isZh ? '月度IC分解' : 'Monthly IC Breakdown',
  icValue: props.isZh ? 'IC值' : 'IC Value',
  icMeanLine: props.isZh ? 'IC均值' : 'IC Mean',
  monthlyICMean: props.isZh ? '月度IC均值' : 'Monthly IC Mean',
  monthlyICStd: props.isZh ? '月度IC标准差' : 'Monthly IC Std',
  zeroLine: props.isZh ? '零线' : 'Zero Line',
  day: props.isZh ? '天' : 'day'
}))

// 响应式状态
const loading = ref(false)
const localTargetPeriod = ref(props.targetPeriod)
const localMethod = ref<'pearson' | 'spearman'>(props.method)
const chartType = ref<'line' | 'bar'>('line')

const icChartRef = ref<HTMLElement>()
const monthlyChartRef = ref<HTMLElement>()

let icChartInstance: echarts.ECharts | null = null
let monthlyChartInstance: echarts.ECharts | null = null

// IC/IR汇总数据
const summary = ref({
  icMean: 0,
  icStd: 0,
  ir: 0,
  positiveRatio: 0,
  icCount: 0,
  icAbsMean: 0,
  maxIC: 0,
  minIC: 0
})

// 图表高度持久化
const CHART_HEIGHT_KEY = 'myquant-chart-heights'
const icChartHeight = ref(350)
const monthlyChartHeight = ref(300)

// 从 localStorage 加载保存的高度
const loadSavedHeights = () => {
  try {
    const saved = localStorage.getItem(CHART_HEIGHT_KEY)
    if (saved) {
      const heights = JSON.parse(saved)
      if (heights.icTrend) icChartHeight.value = heights.icTrend
      if (heights.monthlyIC) monthlyChartHeight.value = heights.monthlyIC
    }
  } catch (e) {
    console.warn('Failed to load saved chart heights:', e)
  }
}

// 保存高度到 localStorage
const saveHeights = () => {
  try {
    const saved = localStorage.getItem(CHART_HEIGHT_KEY)
    const heights = saved ? JSON.parse(saved) : {}
    heights.icTrend = icChartHeight.value
    heights.monthlyIC = monthlyChartHeight.value
    localStorage.setItem(CHART_HEIGHT_KEY, JSON.stringify(heights))
  } catch (e) {
    console.warn('Failed to save chart heights:', e)
  }
}

// 调整大小相关
const isResizingIC = ref(false)
const isResizingMonthly = ref(false)
const resizeStartY = ref(0)
const resizeStartHeight = ref(0)

const startResizeIC = (e: MouseEvent) => {
  isResizingIC.value = true
  resizeStartY.value = e.clientY
  resizeStartHeight.value = icChartHeight.value
  document.addEventListener('mousemove', handleResizeIC)
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

const handleResizeIC = (e: MouseEvent) => {
  if (!isResizingIC.value) return
  const delta = e.clientY - resizeStartY.value
  const newHeight = Math.max(200, Math.min(600, resizeStartHeight.value + delta))
  icChartHeight.value = newHeight
  icChartInstance?.resize()
}

const handleResizeMonthly = (e: MouseEvent) => {
  if (!isResizingMonthly.value) return
  const delta = e.clientY - resizeStartY.value
  const newHeight = Math.max(200, Math.min(600, resizeStartHeight.value + delta))
  monthlyChartHeight.value = newHeight
  monthlyChartInstance?.resize()
}

const stopResize = () => {
  if (isResizingIC.value || isResizingMonthly.value) {
    saveHeights()
  }
  isResizingIC.value = false
  isResizingMonthly.value = false
  document.removeEventListener('mousemove', handleResizeIC)
  document.removeEventListener('mousemove', handleResizeMonthly)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

// IC时间序列数据
const icTimeSeries = ref({
  dates: [] as string[],
  icValues: [] as number[]
})

// 月度IC数据
const monthlyIC = ref({
  months: [] as string[],
  icMeans: [] as number[],
  icStds: [] as number[]
})

// 格式化数字
const formatNumber = (num: number): string => {
  if (Math.abs(num) >= 1) {
    return num.toFixed(4)
  } else {
    return num.toFixed(6)
  }
}

// 格式化百分比
const formatPercent = (num: number): string => {
  return (num * 100).toFixed(2) + '%'
}

// 生成模拟数据
const generateMockData = () => {
  // 生成日期序列（最近60个交易日）
  const dates: string[] = []
  const icValues: number[] = []
  const today = new Date()

  for (let i = 59; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])
    // 生成随机IC值，均值为0.05左右
    icValues.push((Math.random() - 0.3) * 0.15)
  }

  // 生成月度数据
  const months: string[] = []
  const icMeans: number[] = []
  const icStds: number[] = []
  for (let i = 11; i >= 0; i--) {
    const date = new Date(today)
    date.setMonth(date.getMonth() - i)
    months.push(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`)
    icMeans.push((Math.random() - 0.2) * 0.12)
    icStds.push(Math.random() * 0.05 + 0.02)
  }

  return { dates, icValues, months, icMeans, icStds }
}

// 加载IC/IR数据
const loadICIRData = async () => {
  loading.value = true

  try {
    // 如果没有taskId或taskId是'default'，使用模拟数据
    if (!props.taskId || props.taskId === 'default') {
      loadMockData()
      loading.value = false
      return
    }

    const response = await axios.post('/api/v1/research/factor/analysis/ic-ir', {
      task_id: props.taskId,
      target_period: localTargetPeriod.value,
      method: localMethod.value
    })

    if (response.data.success && response.data.data && response.data.data.summary) {
      const data = response.data.data

      // 更新汇总指标
      summary.value = {
        icMean: data.summary?.ic_mean || 0,
        icStd: data.summary?.ic_std || 0,
        ir: data.summary?.ir || 0,
        positiveRatio: data.summary?.positive_ratio || 0,
        icCount: data.summary?.ic_count || 0,
        icAbsMean: data.summary?.ic_abs_mean || 0,
        maxIC: data.summary?.max_ic || 0,
        minIC: data.summary?.min_ic || 0
      }

      // 更新IC时间序列数据
      icTimeSeries.value = {
        dates: data.time_series?.dates || [],
        icValues: data.time_series?.ic_values || []
      }

      // 更新月度IC数据
      monthlyIC.value = {
        months: data.monthly?.months || [],
        icMeans: data.monthly?.ic_means || [],
        icStds: data.monthly?.ic_stds || []
      }

      // 渲染图表
      renderICChart()
      renderMonthlyChart()
    } else {
      // 使用模拟数据
      loadMockData()
    }
  } catch (error: any) {
    console.warn('API调用失败，使用模拟数据:', error.message)
    // 使用模拟数据
    loadMockData()
  } finally {
    loading.value = false
  }
}

// 加载模拟数据
const loadMockData = () => {
  const mockData = generateMockData()

  // 计算汇总指标
  const icValues = mockData.icValues
  const positiveValues = icValues.filter(v => v > 0)

  summary.value = {
    icMean: icValues.reduce((a, b) => a + b, 0) / icValues.length,
    icStd: Math.sqrt(icValues.reduce((a, b) => a + b * b, 0) / icValues.length),
    ir: icValues.reduce((a, b) => a + b, 0) / icValues.length / (Math.sqrt(icValues.reduce((a, b) => a + b * b, 0) / icValues.length) || 0.01),
    positiveRatio: positiveValues.length / icValues.length,
    icCount: icValues.length,
    icAbsMean: icValues.reduce((a, b) => a + Math.abs(b), 0) / icValues.length,
    maxIC: Math.max(...icValues),
    minIC: Math.min(...icValues)
  }

  icTimeSeries.value = {
    dates: mockData.dates,
    icValues: mockData.icValues
  }

  monthlyIC.value = {
    months: mockData.months,
    icMeans: mockData.icMeans,
    icStds: mockData.icStds
  }

  renderICChart()
  renderMonthlyChart()
}

// 渲染IC时间序列图
const renderICChart = () => {
  if (!icChartRef.value) {
    return
  }

  // 如果没有数据，使用模拟数据
  if (!icTimeSeries.value.dates.length) {
    loadMockData()
    return
  }

  if (!icChartInstance) {
    icChartInstance = echarts.init(icChartRef.value, 'dark')
  }

  const dates = icTimeSeries.value.dates
  const icValues = icTimeSeries.value.icValues

  // 计算IC均值线
  const meanLine = new Array(dates.length).fill(summary.value.icMean)

  // 深色主题配色 - TradingView风格 + 中国股市配色
  const darkTheme = {
    background: '#1e222d',
    text: '#d1d4dc',
    textSecondary: '#787b86',
    border: '#2a2e39',
    up: '#ef5350',     // 红色代表正向/上涨
    down: '#26a69a',   // 绿色代表负向/下跌
    accent: '#2962ff'
  }

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e222d',
      borderColor: '#2a2e39',
      textStyle: { color: '#d1d4dc' },
      formatter: (params: any) => {
        const date = params[0].name
        let result = `<div style="padding: 8px;"><div style="margin-bottom: 4px; font-weight: bold;">${date}</div>`
        params.forEach((param: any) => {
          result += `<div style="margin: 4px 0;">${param.marker}${param.seriesName}: ${formatNumber(param.value)}</div>`
        })
        result += '</div>'
        return result
      }
    },
    legend: {
      data: [t.value.icValue, t.value.icMeanLine],
      top: 10,
      textStyle: { color: '#d1d4dc' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '18%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        interval: 'auto',
        rotate: 45,
        color: '#787b86'
      },
      axisLine: { lineStyle: { color: '#2a2e39' } },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => value.toFixed(4),
        color: '#787b86'
      },
      axisLine: { lineStyle: { color: '#2a2e39' } },
      splitLine: { lineStyle: { color: '#2a2e39' } }
    },
    series: [
      {
        name: t.value.icValue,
        type: chartType.value,
        data: icValues,
        itemStyle: {
          color: (params: any) => {
            return params.value >= 0 ? darkTheme.up : darkTheme.down
          }
        },
        markLine: {
          data: [
            { yAxis: 0, name: t.value.zeroLine, lineStyle: { color: '#787b86', type: 'dashed' } }
          ]
        }
      },
      {
        name: t.value.icMeanLine,
        type: 'line',
        data: meanLine,
        lineStyle: {
          color: darkTheme.accent,
          type: 'dashed',
          width: 2
        },
        symbol: 'none'
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
        borderColor: '#2a2e39',
        backgroundColor: '#131722',
        fillerColor: 'rgba(41, 98, 255, 0.2)',
        handleStyle: {
          color: '#2962ff',
          borderColor: '#2962ff'
        },
        textStyle: { color: '#787b86' }
      }
    ]
  }

  icChartInstance.setOption(option)
}

// 渲染月度IC图
const renderMonthlyChart = () => {
  if (!monthlyChartRef.value) {
    return
  }

  // 如果没有数据，使用模拟数据
  if (!monthlyIC.value.months.length) {
    loadMockData()
    return
  }

  if (!monthlyChartInstance) {
    monthlyChartInstance = echarts.init(monthlyChartRef.value, 'dark')
  }

  const months = monthlyIC.value.months
  const icMeans = monthlyIC.value.icMeans
  const icStds = monthlyIC.value.icStds

  // 深色主题配色 - 中国股市配色（红涨绿跌）
  const darkTheme = {
    up: '#ef5350',
    down: '#26a69a',
    accent: '#2962ff'
  }

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e222d',
      borderColor: '#2a2e39',
      textStyle: { color: '#d1d4dc' },
      formatter: (params: any) => {
        const month = params[0].name
        let result = `<div style="padding: 8px;"><div style="margin-bottom: 4px; font-weight: bold;">${month}</div>`
        params.forEach((param: any) => {
          result += `<div style="margin: 4px 0;">${param.marker}${param.seriesName}: ${formatNumber(param.value)}</div>`
        })
        result += '</div>'
        return result
      }
    },
    legend: {
      data: [t.value.monthlyICMean, t.value.monthlyICStd],
      top: 10,
      textStyle: { color: '#d1d4dc' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: { color: '#787b86' },
      axisLine: { lineStyle: { color: '#2a2e39' } },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => value.toFixed(4),
        color: '#787b86'
      },
      axisLine: { lineStyle: { color: '#2a2e39' } },
      splitLine: { lineStyle: { color: '#2a2e39' } }
    },
    series: [
      {
        name: t.value.monthlyICMean,
        type: 'bar',
        data: icMeans,
        itemStyle: {
          color: (params: any) => {
            return params.value >= 0 ? darkTheme.up : darkTheme.down
          }
        }
      },
      {
        name: t.value.monthlyICStd,
        type: 'line',
        data: icStds,
        itemStyle: {
          color: darkTheme.accent
        }
      }
    ]
  }

  monthlyChartInstance.setOption(option)
}

// 监听图表类型变化
watch(chartType, () => {
  renderICChart()
})

// 监听语言变化，重新渲染图表
watch(() => props.isZh, () => {
  // 销毁并重新创建图表实例以确保完全更新
  if (icChartInstance) {
    icChartInstance.dispose()
    icChartInstance = null
  }
  if (monthlyChartInstance) {
    monthlyChartInstance.dispose()
    monthlyChartInstance = null
  }
  // 使用nextTick确保DOM更新后再渲染
  setTimeout(() => {
    renderICChart()
    renderMonthlyChart()
  }, 0)
})

// 监听taskId变化
watch(() => props.taskId, () => {
  loadICIRData()
})

// 窗口大小变化时重绘图表
const handleResize = () => {
  if (icChartInstance) {
    icChartInstance.resize()
  }
  if (monthlyChartInstance) {
    monthlyChartInstance.resize()
  }
}

// 生命周期钩子
onMounted(() => {
  loadSavedHeights()
  loadICIRData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  if (icChartInstance) {
    icChartInstance.dispose()
    icChartInstance = null
  }
  if (monthlyChartInstance) {
    monthlyChartInstance.dispose()
    monthlyChartInstance = null
  }
  window.removeEventListener('resize', handleResize)
})

// 暴露方法给父组件
defineExpose({
  refresh: loadICIRData
})
</script>

<style scoped lang="scss">
.icir-trend-chart {
  padding: 20px;
  background: var(--bg-primary, #131722);
  border-radius: 8px;

  // Element Plus深色主题覆盖
  :deep(.el-input-number) {
    .el-input__wrapper {
      background: var(--bg-primary, #131722);
      border-color: var(--border-color, #2a2e39);
      box-shadow: none;

      &:hover {
        border-color: var(--accent-blue, #2962ff);
      }
    }

    .el-input__inner {
      color: var(--text-primary, #d1d4dc);
    }

    .el-input-number__decrease,
    .el-input-number__increase {
      background: var(--bg-secondary, #1e222d);
      border-color: var(--border-color, #2a2e39);
      color: var(--text-primary, #d1d4dc);

      &:hover {
        color: var(--accent-blue, #2962ff);
      }
    }
  }

  :deep(.el-select) {
    .el-input__wrapper {
      background: var(--bg-primary, #131722);
      border-color: var(--border-color, #2a2e39);
      box-shadow: none;
    }

    .el-input__inner {
      color: var(--text-primary, #d1d4dc);
    }
  }

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

  :deep(.el-button--primary) {
    background: var(--accent-blue, #2962ff);
    border-color: var(--accent-blue, #2962ff);

    &:hover {
      background: #1e5fff;
      border-color: #1e5fff;
    }
  }
}

// 主要内容区域
.main-content {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 16px;
}

// 左侧控制面板
.controls-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;

  .panel-section {
    background: var(--bg-secondary, #1e222d);
    padding: 16px;
    border-radius: 8px;
    border: 1px solid var(--border-color, #2a2e39);

    h4 {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      margin: 0 0 12px 0;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-color, #2a2e39);
      display: flex;
      align-items: center;
      gap: 8px;

      .title-icon {
        width: 16px;
        height: 16px;
        flex-shrink: 0;
      }
    }

    .control-group {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;

      label {
        font-size: 12px;
        color: var(--text-secondary, #787b86);
        min-width: 70px;
      }

      .unit {
        font-size: 11px;
        color: var(--text-secondary, #787b86);
      }
    }

    .stat-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 0;
      border-bottom: 1px solid var(--border-color, #2a2e39);

      &:last-child {
        border-bottom: none;
      }

      .stat-label {
        font-size: 11px;
        color: var(--text-secondary, #787b86);
      }

      .stat-value {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-primary, #d1d4dc);

        &.positive {
          color: #ef5350;  // 红色代表正向
        }

        &.negative {
          color: #26a69a;  // 绿色代表负向
        }
      }
    }
  }
}

// 右侧图表面板
.charts-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;

  .chart-section {
    background: var(--bg-secondary, #1e222d);
    padding: 16px;
    border-radius: 8px;
    border: 1px solid var(--border-color, #2a2e39);
    position: relative;

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      h3 {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary, #d1d4dc);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;

        .title-icon {
          width: 18px;
          height: 18px;
          flex-shrink: 0;
        }
      }

      .chart-controls {
        display: flex;
        align-items: center;
        gap: 16px;
      }
    }

    .chart-wrapper {
      position: relative;
      min-height: 200px;
      max-height: 600px;
    }

    .chart {
      width: 100%;
      height: 100%;
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
}
</style>
