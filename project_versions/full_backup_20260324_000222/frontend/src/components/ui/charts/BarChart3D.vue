<template>
  <div class="return-stats-container">
    <!-- 头部 -->
    <div class="chart-header">
      <div class="chart-title">
        <svg class="icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        {{ title }}
        <!-- 期间切换 -->
        <div class="period-toggle">
          <button
            v-for="opt in periodOptions"
            :key="opt.value"
            :class="['period-btn', { active: selectedPeriod === opt.value }]"
            @click="selectedPeriod = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
      <!-- 图表类型切换 -->
      <button
        class="chart-type-toggle"
        @click="chartType = chartType === 'heatmap' ? 'bar' : 'heatmap'"
      >
        <svg v-if="chartType === 'heatmap'" class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="12" width="4" height="9"></rect>
          <rect x="10" y="8" width="4" height="13"></rect>
          <rect x="17" y="4" width="4" height="17"></rect>
        </svg>
        <svg v-else class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="10" y="3" width="7" height="7"></rect>
          <rect x="3" y="10" width="7" height="7"></rect>
          <rect x="10" y="10" width="7" height="7"></rect>
        </svg>
      </button>
    </div>

    <!-- 热力图视图 -->
    <div v-if="chartType === 'heatmap'" class="heatmap" :style="{ gridTemplateColumns: `repeat(${heatmapCols}, 1fr)` }">
      <div v-for="(item, idx) in displayData" :key="idx" :class="['heatmap-cell', item.class]">
        {{ item.value }}%
        <span class="heatmap-label">{{ item.label }}</span>
      </div>
    </div>

    <!-- 3D柱状图视图 -->
    <div v-else ref="chartRef" class="bar-chart-3d-echarts"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import 'echarts-gl'

interface Props {
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '收益统计'
})

// 期间选项
const periodOptions = [
  { value: 'day', label: '日' },
  { value: 'week', label: '周' },
  { value: 'month', label: '月' }
]

// 状态
const selectedPeriod = ref('month')
const chartType = ref<'heatmap' | 'bar'>('heatmap')
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 获取当前月的实际天数
const getDaysInMonth = (): number => {
  const now = new Date()
  return new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
}

// 热力图列数 - 根据周期动态计算
const heatmapCols = computed(() => {
  if (selectedPeriod.value === 'day') return 7  // 7列日历形式
  return 4  // 周数据和月数据都用4列
})

const displayData = computed(() => {
  const daysInMonth = getDaysInMonth()
  // 固定数据模板
  const dayTemplate = [
    { value: 1.2, class: 'medium' }, { value: -0.8, class: 'medium-low' }, { value: 2.5, class: 'medium-high' },
    { value: -1.5, class: 'low' }, { value: 3.2, class: 'high' }, { value: 0.5, class: 'medium' },
    { value: -2.1, class: 'low' }, { value: 1.8, class: 'medium' }, { value: -0.3, class: 'medium-low' },
    { value: 2.8, class: 'medium-high' }, { value: -1.2, class: 'low' }, { value: 4.1, class: 'high' },
    { value: 0.9, class: 'medium' }, { value: -0.5, class: 'medium-low' }, { value: 1.5, class: 'medium' },
    { value: -2.5, class: 'low' }, { value: 3.5, class: 'high' }, { value: -0.8, class: 'medium-low' },
    { value: 2.2, class: 'medium-high' }, { value: -1.0, class: 'low' }, { value: 1.1, class: 'medium' },
    { value: -0.2, class: 'medium-low' }, { value: 2.9, class: 'high' }, { value: -1.8, class: 'low' },
    { value: 0.6, class: 'medium' }, { value: -3.2, class: 'low' }, { value: 1.9, class: 'medium' },
    { value: -0.4, class: 'medium-low' }
  ]
  const periodData: Record<string, { label: string; value: number; class: string }[]> = {
    day: Array.from({ length: daysInMonth }, (_, i) => {
      const template = dayTemplate[i % dayTemplate.length]
      return {
        label: `${i + 1}日`,
        value: template.value,
        class: template.class
      }
    }),
    week: [
      { label: '第1周', value: 2.5, class: 'medium-high' },
      { label: '第2周', value: -1.2, class: 'medium-low' },
      { label: '第3周', value: 3.8, class: 'high' },
      { label: '第4周', value: 1.5, class: 'medium' }
    ],
    month: [
      { label: '1月', value: 5.2, class: 'high' },
      { label: '2月', value: -2.1, class: 'low' },
      { label: '3月', value: 3.8, class: 'medium-high' },
      { label: '4月', value: 1.5, class: 'medium' },
      { label: '5月', value: -0.8, class: 'medium-low' },
      { label: '6月', value: 4.2, class: 'medium-high' },
      { label: '7月', value: -1.5, class: 'medium-low' },
      { label: '8月', value: 2.8, class: 'medium-high' },
      { label: '9月', value: -0.3, class: 'medium-low' },
      { label: '10月', value: 1.9, class: 'medium' },
      { label: '11月', value: 3.5, class: 'medium-high' },
      { label: '12月', value: -1.2, class: 'medium-low' }
    ]
  }
  return periodData[selectedPeriod.value] || periodData.month
})

// 颜色映射
const colorMap: Record<string, string> = {
  'high': '#9c27b0',
  'medium-high': '#ef5350',
  'medium': '#ff9800',
  'medium-low': '#2962ff',
  'low': '#4caf50'
}

// 按行分组用于3D图
const dataRows = computed(() => {
  const cols = heatmapCols.value
  const rows: any[] = []
  for (let i = 0; i < displayData.value.length; i += cols) {
    rows.push(displayData.value.slice(i, i + cols))
  }
  return rows
})

const initChart = () => {
  if (!chartRef.value || chartType.value !== 'bar') {
    return
  }

  // 检查容器尺寸
  const rect = chartRef.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    setTimeout(() => initChart(), 100)
    return
  }

  if (!chartInstance) {
    try {
      chartInstance = echarts.init(chartRef.value, 'dark')
    } catch (e) {
      console.error('ECharts init error:', e)
      return
    }
  }

  // 按行分组计算3D图尺寸 - 使用固定值匹配原始代码
  const rowCount = Math.ceil(displayData.value.length / heatmapCols.value)
  let boxWidth: number, boxDepth: number, barSize: number, distance: number

  if (selectedPeriod.value === 'day') {
    // 日数据：7列 x 4-5行
    boxWidth = 80
    boxDepth = 120
    barSize = 10
    distance = 120
  } else if (selectedPeriod.value === 'week') {
    // 周数据
    boxWidth = 60
    boxDepth = 100
    barSize = 14
    distance = 100
  } else {
    // 月数据：4列 x 3行
    boxWidth = 60
    boxDepth = 100
    barSize = 12
    distance = 100
  }

  // 构建3D数据 - [rowIndex, colIndex, value]
  const bar3DData: any[] = []
  const itemColors: string[] = []

  dataRows.value.forEach((row: any, rowIndex: number) => {
    row.forEach((item: any, colIndex: number) => {
      bar3DData.push({
        value: [rowIndex, colIndex, item.value],
        originalValue: item.value,
        label: item.label
      })
      itemColors.push(colorMap[item.class] || '#2962ff')
    })
  })

  const option: any = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e222d',
      borderColor: '#363a45',
      textStyle: { color: '#d1d4dc' },
      formatter: (params: any) => {
        const data = params.data
        return `${data.label}<br/>收益率: ${data.originalValue}%`
      }
    },
    visualMap: {
      show: false,
      min: 0,
      max: 10,
      inRange: {
        color: ['#4caf50', '#2962ff', '#ff9800', '#ef5350', '#9c27b0']
      }
    },
    xAxis3D: {
      type: 'category',
      data: Array.from({ length: rowCount }, (_, i) => `${i + 1}`),
      axisLabel: { show: false },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { show: false },
      axisPointer: { show: false }
    },
    yAxis3D: {
      type: 'category',
      data: Array.from({ length: heatmapCols.value }, (_, i) => `${i + 1}`),
      axisLabel: { show: false },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { show: false },
      axisPointer: { show: false }
    },
    zAxis3D: {
      type: 'value',
      min: -10,
      max: 10,
      axisLabel: { show: false },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { show: false },
      axisPointer: { show: false }
    },
    grid3D: {
      boxWidth,
      boxHeight: 60,
      boxDepth,
      viewControl: {
        autoRotate: false,
        distance,
        alpha: 30,
        beta: 40
      },
      light: {
        main: {
          intensity: 1.8,
          shadow: true
        },
        ambient: {
          intensity: 0.5
        }
      },
      environment: 'none',
      show: false
    },
    series: [
      {
        type: 'bar3D',
        data: bar3DData.map((item, index) => ({
          value: item.value,
          originalValue: item.originalValue,
          monthLabel: item.label,
          itemStyle: {
            color: itemColors[index],
            opacity: 0.85
          }
        })),
        shading: 'realistic',
        realisticMaterial: {
          roughness: 0.3,
          metalness: 0.1
        },
        barSize,
        bevelSize: 0,
        label: {
          show: selectedPeriod.value !== 'day',
          distance: 2,
          formatter: (params: any) => {
            const val = params.data.originalValue
            const label = params.data.monthLabel
            return label + '\n' + (val > 0 ? '+' : '') + val.toFixed(1) + '%'
          },
          textStyle: {
            fontSize: 14,
            fontWeight: 'bold',
            color: '#fff',
            textBorderColor: 'rgba(0,0,0,0.8)',
            textBorderWidth: 2
          }
        },
        emphasis: {
          itemStyle: {
            opacity: 1
          }
        }
      }
    ]
  }

  try {
    chartInstance.setOption(option as any)
  } catch (e) {
    console.error('setOption error:', e)
  }
}

const resizeChart = () => {
  chartInstance?.resize()
}

watch(chartType, (newType, oldType) => {
  if (oldType === 'bar') {
    // 离开柱状图视图时销毁实例
    chartInstance?.dispose()
    chartInstance = null
  }
  if (newType === 'bar') {
    nextTick(() => {
      setTimeout(initChart, 100)
    })
  }
})

watch(selectedPeriod, () => {
  if (chartType.value === 'bar') {
    setTimeout(initChart, 100)
  }
})

onMounted(() => {
  if (chartType.value === 'bar') {
    initChart()
  }
  window.addEventListener('resize', resizeChart)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})
</script>

<style lang="scss" scoped>
.return-stats-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-md {
  width: 18px;
  height: 18px;
  color: #ff9800;
}

.icon-sm {
  width: 14px;
  height: 14px;
  color: #787b86;
}

// 期间切换
.period-toggle {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

.period-btn {
  padding: 2px 8px;
  font-size: 11px;
  background: transparent;
  border: 1px solid var(--border-color, #2a2e39);
  color: var(--text-secondary, #787b86);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--bg-tertiary, #2a2e39);
    color: var(--text-primary, #d1d4dc);
  }

  &.active {
    background: var(--accent-blue, #2962ff);
    border-color: var(--accent-blue, #2962ff);
    color: white;
  }
}

// 图表类型切换
.chart-type-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  margin-left: 8px;
  background: var(--bg-tertiary, #2a2e39);
  border: 1px solid var(--border-color, #3a3f4b);
  border-radius: 4px;
  cursor: pointer;
  color: var(--text-secondary, #a0aec0);
  transition: all 0.15s;

  &:hover {
    background: var(--bg-secondary, #1e222d);
    color: var(--text-primary, #d1d4dc);
  }
}

// 热力图
.heatmap {
  display: grid;
  gap: 4px;
  padding-top: 28px;
  flex: 1;
}

.heatmap-cell {
  min-height: 48px;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  color: white;
  position: relative;
  padding: 2px;

  &.high { background: linear-gradient(135deg, #9c27b0, #ba68c8); }
  &.medium-high { background: linear-gradient(135deg, #ef5350, #ff8a80); }
  &.medium { background: linear-gradient(135deg, #ff9800, #ffb74d); }
  &.medium-low { background: linear-gradient(135deg, #2962ff, #5c95ff); }
  &.low { background: linear-gradient(135deg, #4caf50, #81c784); }
  &.empty { background: var(--bg-tertiary, #2a2e39); }
}

.heatmap-label {
  position: absolute;
  bottom: 2px;
  font-size: 12px;
  opacity: 0.8;
}

// 3D柱状图
.bar-chart-3d-echarts {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
