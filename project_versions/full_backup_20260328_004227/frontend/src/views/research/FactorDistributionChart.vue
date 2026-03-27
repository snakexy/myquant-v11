<template>
  <div class="factor-distribution-chart">
    <!-- 统计量卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2 L12 22 M6 12 L18 12"></path>
            <circle cx="12" cy="12" r="1" fill="currentColor"/>
          </svg>
        </div>
        <div>
          <div class="stat-label">{{ t.mean }}</div>
          <div class="stat-value">{{ formatNumber(statistics.mean) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2 L12 22 M6 12 L18 12"></path>
            <circle cx="12" cy="12" r="1" fill="currentColor"/>
          </svg>
        </div>
        <div>
          <div class="stat-label">{{ t.std }}</div>
          <div class="stat-value">{{ formatNumber(statistics.std) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="18 15 12 9 6 15"></polyline>
          </svg>
        </div>
        <div>
          <div class="stat-label">{{ t.min }}</div>
          <div class="stat-value">{{ formatNumber(statistics.min) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
        <div>
          <div class="stat-label">{{ t.max }}</div>
          <div class="stat-value">{{ formatNumber(statistics.max) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" :style="{ backgroundColor: getMedianQualityColor(statistics.median) + '20', borderColor: getMedianQualityColor(statistics.median) }">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :style="{ color: getMedianQualityColor(statistics.median) }">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <rect x="8" y="11" width="8" height="2" fill="currentColor"/>
          </svg>
        </div>
        <div>
          <div class="stat-label">{{ t.median }}</div>
          <div class="stat-value" :style="{ color: getMedianQualityColor(statistics.median) }">{{ formatNumber(statistics.median) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="3" x2="12" y2="21"></line>
            <line x1="5" y1="21" x2="19" y2="21"></line>
            <line x1="8" y1="18" x2="8" y2="21"></line>
          </svg>
        </div>
        <div>
          <div class="stat-label">{{ t.p25 }}</div>
          <div class="stat-value">{{ formatNumber(statistics.p25) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="3" x2="12" y2="21"></line>
            <line x1="5" y1="21" x2="19" y2="21"></line>
            <line x1="16" y1="18" x2="16" y2="21"></line>
          </svg>
        </div>
        <div>
          <div class="stat-label">{{ t.p75 }}</div>
          <div class="stat-value">{{ formatNumber(statistics.p75) }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="18" rx="1" stroke-width="1.5"/>
            <rect x="14" y="3" width="7" height="18" rx="1" stroke-width="1.5"/>
            <line x1="5" y1="8" x2="8" y2="8" stroke-width="1"/>
            <line x1="16" y1="8" x2="19" y2="8" stroke-width="1"/>
          </svg>
        </div>
        <div>
          <div class="stat-label">{{ t.count }}</div>
          <div class="stat-value">{{ formatNumber(statistics.count) }}</div>
        </div>
      </div>
    </div>

    <!-- 直方图 -->
    <div class="chart-container">
      <div class="chart-header">
        <h3>
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="20" x2="18" y2="10"></line>
            <line x1="12" y1="20" x2="12" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="14"></line>
          </svg>
          {{ t.histogramTitle }}
        </h3>
        <div class="chart-controls">
          <el-input-number
            v-model="localBins"
            :min="10"
            :max="200"
            :step="10"
            size="small"
            @change="loadDistributionData"
          />
          <span class="control-label">{{ t.bins }}</span>
        </div>
        <div class="legend-toggles">
          <span
            class="legend-toggle-item"
            :class="{ active: showActualDistribution }"
            @click="toggleActualDistribution"
          >
            <span class="legend-icon actual-distribution"></span>
            {{ t.actualDistribution }}
          </span>
          <span
            class="legend-toggle-item"
            :class="{ active: showExpectedDistribution }"
            @click="toggleExpectedDistribution"
          >
            <span class="legend-icon expected-distribution"></span>
            {{ t.expectedDistribution }}
          </span>
          <span
            class="legend-toggle-item"
            :class="{ active: showMedianLine }"
            @click="toggleMedianLine"
          >
            <span class="legend-icon median-line" :style="{ borderColor: getMedianQualityColor(statistics.median) }"></span>
            {{ t.medianLine }}
          </span>
          <span
            class="legend-toggle-item"
            :class="{ active: showIdealZone }"
            @click="toggleIdealZone"
          >
            <span class="legend-icon ideal-zone"></span>
            {{ t.idealZone }}
          </span>
        </div>
      </div>
      <div ref="chartRef" class="chart" v-loading="loading"></div>
    </div>

    <!-- 多因子切换标签 -->
    <div class="factor-tabs" v-if="availableFactors.length > 1">
      <el-radio-group v-model="selectedFactor" @change="loadDistributionData">
        <el-radio-button
          v-for="factor in availableFactors"
          :key="factor.name"
          :label="factor.name"
        >
          {{ factor.label }}
        </el-radio-button>
      </el-radio-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

// Props定义
interface Props {
  taskId: string
  bins?: number
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  bins: 50,
  isZh: true
})

// 多语言文本
const t = computed(() => ({
  mean: props.isZh ? '均值' : 'Mean',
  std: props.isZh ? '标准差' : 'Std',
  min: props.isZh ? '最小值' : 'Min',
  max: props.isZh ? '最大值' : 'Max',
  median: props.isZh ? '中位数' : 'Median',
  p25: props.isZh ? '25%分位' : '25%',
  p75: props.isZh ? '75%分位' : '75%',
  count: props.isZh ? '样本数' : 'Count',
  histogramTitle: props.isZh ? '因子分布直方图' : 'Factor Distribution Histogram',
  bins: props.isZh ? '分箱数' : 'Bins',
  range: props.isZh ? '区间' : 'Range',
  frequency: props.isZh ? '样本数' : 'Frequency',
  factorValue: props.isZh ? '因子值' : 'Factor Value',
  actualDistribution: props.isZh ? '实际分布' : 'Actual',
  expectedDistribution: props.isZh ? '理论分布' : 'Expected',
  medianLine: props.isZh ? '中位数线' : 'Median',
  idealZone: props.isZh ? '理想区域' : 'Ideal Zone'
}))

// 均值质量颜色计算
const getMeanQualityColor = (mean: number): string => {
  const absMean = Math.abs(mean)
  if (absMean <= 0.1) return '#ef5350'      // 红色：优秀
  if (absMean <= 0.3) return '#ffa726'      // 橙色：良好，需标准化
  if (absMean <= 0.5) return '#afb42b'      // 黄绿色：一般
  return '#26a69a'                          // 绿色：有问题
}

// 中位数质量颜色计算
const getMedianQualityColor = (median: number): string => {
  const absMedian = Math.abs(median)
  if (absMedian <= 0.1) return '#ef5350'      // 红色：优秀
  if (absMedian <= 0.3) return '#ffa726'      // 橙色：良好，需标准化
  if (absMedian <= 0.5) return '#afb42b'      // 黄绿色：一般
  return '#26a69a'                          // 绿色：有问题
}

// 中位数质量标签计算
const getMedianQualityLabel = (median: number): string => {
  const absMedian = Math.abs(median)
  if (absMedian <= 0.1) return props.isZh ? '优秀' : 'Excellent'
  if (absMedian <= 0.3) return props.isZh ? '需标准化' : 'Normalize'
  if (absMedian <= 0.5) return props.isZh ? '一般' : 'Fair'
  return props.isZh ? '检查因子' : 'Check Factor'
}

// 响应式状态
const loading = ref(false)
const localBins = ref(props.bins)
const selectedFactor = ref('factor')
const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 显示控制
const showActualDistribution = ref(true)
const showExpectedDistribution = ref(true)
const showMedianLine = ref(true)
const showIdealZone = ref(true)

// 切换函数
const toggleActualDistribution = () => {
  showActualDistribution.value = !showActualDistribution.value
  renderChart()
}

const toggleExpectedDistribution = () => {
  showExpectedDistribution.value = !showExpectedDistribution.value
  renderChart()
}

const toggleMedianLine = () => {
  showMedianLine.value = !showMedianLine.value
  renderChart()
}

const toggleIdealZone = () => {
  showIdealZone.value = !showIdealZone.value
  renderChart()
}

// 统计量数据
const statistics = ref({
  mean: 0,
  std: 0,
  min: 0,
  max: 0,
  median: 0,
  p25: 0,
  p75: 0,
  count: 0
})

// 可用因子列表
const availableFactors = ref([
  { name: 'factor', label: '因子值' }
])

// 分布数据
const distributionData = ref({
  bins: [] as number[],
  counts: [] as number[]
})

// 格式化数字
const formatNumber = (num: number): string => {
  if (Math.abs(num) >= 1000000) {
    return (num / 1000000).toFixed(2) + 'M'
  } else if (Math.abs(num) >= 1000) {
    return (num / 1000).toFixed(2) + 'K'
  } else if (Math.abs(num) >= 1) {
    return num.toFixed(4)
  } else {
    return num.toFixed(6)
  }
}

// 生成模拟数据
const generateMockData = () => {
  const n = localBins.value
  const bins: number[] = []
  const counts: number[] = []

  // 生成正态分布数据
  const mean = 0.05
  const std = 0.15

  // 根据均值 ± 4σ 来确定范围（覆盖99.99%的数据）
  const rangeStart = mean - 4 * std
  const rangeEnd = mean + 4 * std

  for (let i = 0; i <= n; i++) {
    bins.push(rangeStart + (rangeEnd - rangeStart) * (i / n))
  }

  for (let i = 0; i < n; i++) {
    // 简单的正态分布模拟
    const center = (bins[i] + bins[i + 1]) / 2
    const density = Math.exp(-0.5 * Math.pow((center - mean) / std, 2)) / (std * Math.sqrt(2 * Math.PI))
    counts.push(Math.floor(density * 1000 + Math.random() * 50))
  }

  return { bins, counts, mean, std }
}

// 加载分布数据
const loadDistributionData = async () => {
  loading.value = true

  try {
    // 如果没有taskId或taskId是'default'，使用模拟数据
    if (!props.taskId || props.taskId === 'default') {
      loadMockData()
      loading.value = false
      return
    }

    const response = await axios.post('/api/v1/research/factor/visualization/distribution', {
      task_id: props.taskId,
      bins: localBins.value,
      factor_name: selectedFactor.value
    })

    if (response.data.success && response.data.data && response.data.data.statistics) {
      const data = response.data.data

      // 更新统计量
      statistics.value = {
        mean: data.statistics?.mean || 0,
        std: data.statistics?.std || 0,
        min: data.statistics?.min || 0,
        max: data.statistics?.max || 0,
        median: data.statistics?.median || 0,
        p25: data.statistics?.p25 || 0,
        p75: data.statistics?.p75 || 0,
        count: data.statistics?.count || 0
      }

      // 更新分布数据
      distributionData.value = {
        bins: data.bins || [],
        counts: data.counts || []
      }

      // 更新可用因子列表
      if (data.available_factors) {
        availableFactors.value = data.available_factors
      }

      // 渲染图表
      renderChart()
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

  distributionData.value = {
    bins: mockData.bins,
    counts: mockData.counts
  }

  const total = mockData.counts.reduce((a, b) => a + b, 0)

  // 计算分位数的函数（基于累积分布）
  const calculatePercentile = (percentile: number): number => {
    const target = total * percentile
    let accumulated = 0
    for (let i = 0; i < mockData.counts.length; i++) {
      accumulated += mockData.counts[i]
      if (accumulated >= target) {
        // 线性插值
        const prevAccum = accumulated - mockData.counts[i]
        const ratio = (target - prevAccum) / mockData.counts[i]
        return mockData.bins[i] + ratio * (mockData.bins[i + 1] - mockData.bins[i])
      }
    }
    return mockData.bins[mockData.bins.length - 1]
  }

  statistics.value = {
    mean: mockData.mean,
    std: mockData.std,
    min: mockData.bins[0],
    max: mockData.bins[mockData.bins.length - 1],
    median: calculatePercentile(0.5),
    p25: calculatePercentile(0.25),
    p75: calculatePercentile(0.75),
    count: total
  }

  renderChart()
}

// 渲染图表
const renderChart = () => {
  if (!chartRef.value) {
    return
  }

  // 如果没有数据，加载模拟数据
  if (!distributionData.value.bins.length) {
    loadMockData()
    return
  }

  // 初始化图表实例
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value, 'dark')
  }

  // 准备图表数据
  const binEdges = distributionData.value.bins
  const counts = distributionData.value.counts

  // 计算每个bin的中心点
  const binCenters: number[] = []
  for (let i = 0; i < binEdges.length - 1; i++) {
    binCenters.push((binEdges[i] + binEdges[i + 1]) / 2)
  }

  // 找到最接近目标值的x轴索引
  const findXAxisIndex = (centers: number[], target: number): number => {
    let closest = 0
    let minDiff = Math.abs(centers[0] - target)
    for (let i = 1; i < centers.length; i++) {
      const diff = Math.abs(centers[i] - target)
      if (diff < minDiff) {
        minDiff = diff
        closest = i
      }
    }
    return closest
  }

  // 生成理论正态分布曲线
  const generateNormalDistributionCurve = (xValues: number[], mean: number, std: number, maxCount: number) => {
    return xValues.map(x => {
      const density = Math.exp(-0.5 * Math.pow((x - mean) / std, 2)) / (std * Math.sqrt(2 * Math.PI))
      // 缩放使得曲线最高点接近实际数据的最高点
      return Math.round(density * std * Math.sqrt(2 * Math.PI) * maxCount * 0.9)
    })
  }

  // 深色主题配色
  const darkTheme = {
    background: '#1e222d',
    text: '#d1d4dc',
    textSecondary: '#787b86',
    border: '#2a2e39',
    accent: '#2962ff'
  }

  // 图表配置
  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: darkTheme.background,
      borderColor: darkTheme.border,
      textStyle: { color: darkTheme.text },
      formatter: (params: any) => {
        const param = params[0]
        const binStart = binEdges[param.dataIndex]
        const binEnd = binEdges[param.dataIndex + 1]
        const count = param.value
        const percentage = ((count / statistics.value.count) * 100).toFixed(2)
        return `
          <div style="padding: 8px;">
            <div style="margin-bottom: 4px; font-weight: bold;">${t.value.range}</div>
            <div>[${formatNumber(binStart)}, ${formatNumber(binEnd)})</div>
            <div style="margin-top: 8px; margin-bottom: 4px; font-weight: bold;">${t.value.frequency}</div>
            <div>${count} (${percentage}%)</div>
          </div>
        `
      }
    },
    grid: {
      left: '10%',
      right: '5%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: binCenters.map(v => v.toFixed(4)),
      axisLabel: {
        interval: 'auto',
        rotate: 45,
        color: darkTheme.textSecondary,
        formatter: (value: string) => {
          const num = parseFloat(value)
          if (Math.abs(num) >= 1000) {
            return (num / 1000).toFixed(1) + 'K'
          }
          return num.toFixed(2)
        }
      },
      axisLine: { lineStyle: { color: darkTheme.border } },
      name: t.value.factorValue,
      nameLocation: 'middle',
      nameGap: 30,
      nameTextStyle: { color: darkTheme.textSecondary }
    },
    yAxis: {
      type: 'value',
      name: t.value.frequency,
      nameLocation: 'middle',
      nameGap: 50,
      axisLabel: { color: darkTheme.textSecondary },
      axisLine: { lineStyle: { color: darkTheme.border } },
      splitLine: { lineStyle: { color: darkTheme.border } },
      nameTextStyle: { color: darkTheme.textSecondary }
    },
    series: [
      {
        name: t.value.frequency,
        type: 'bar',
        data: showActualDistribution.value ? counts : [],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#2962ff' },
            { offset: 1, color: '#1e88e5' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#42a5f5' },
              { offset: 1, color: '#2962ff' }
            ])
          }
        },
        // 添加理想区域背景标记（0附近 ±0.1）
        markArea: showIdealZone.value ? {
          silent: true,
          itemStyle: {
            color: 'rgba(239, 83, 80, 0.35)'
          },
          data: [[
            {
              xAxis: findXAxisIndex(binCenters, -0.1)
            },
            {
              xAxis: findXAxisIndex(binCenters, 0.1)
            }
          ]]
        } : undefined,
        // 中位数参考线（颜色根据偏离程度变化）
        markLine: showMedianLine.value ? {
          silent: true,
          symbol: 'none',
          lineStyle: {
            type: 'dashed',
            width: 3
          },
          label: {
            show: true,
            position: 'end',
            distance: 10,
            formatter: () => {
              const median = statistics.value.median
              return props.isZh ?
                `${median.toFixed(3)} (${getMedianQualityLabel(median)})` :
                `${median.toFixed(3)} (${getMedianQualityLabel(median)})`
            },
            fontSize: 11,
            fontWeight: 'bold',
            color: getMedianQualityColor(statistics.value.median),
            backgroundColor: getMedianQualityColor(statistics.value.median) + '20',
            borderColor: getMedianQualityColor(statistics.value.median),
            borderWidth: 1,
            borderRadius: 4,
            padding: [4, 8]
          },
          data: [
            {
              name: props.isZh ? '中位数' : 'Median',
              xAxis: findXAxisIndex(binCenters, statistics.value.median),
              lineStyle: { color: getMedianQualityColor(statistics.value.median), width: 3 }
            }
          ]
        } : undefined
      },
      // 添加理论正态分布曲线作为参考
      {
        name: props.isZh ? '理论分布' : 'Expected',
        type: 'line',
        data: showExpectedDistribution.value ? generateNormalDistributionCurve(binCenters, statistics.value.mean, statistics.value.std, Math.max(...counts)) : [],
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#ffa726',
          width: 2,
          type: 'dashed'
        },
        itemStyle: {
          opacity: 0
        },
        z: 10
      }
    ],
    // 移除自动缩放，显示全部数据
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
        bottom: 10
      }
    ]
  }

  chartInstance.setOption(option)
}

// 监听taskId变化
watch(() => props.taskId, () => {
  loadDistributionData()
})

// 监听语言变化，重新渲染图表
watch(() => props.isZh, () => {
  // 销毁并重新创建图表实例以确保完全更新
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  // 使用nextTick确保DOM更新后再渲染
  setTimeout(() => {
    renderChart()
  }, 0)
})

// 窗口大小变化时重绘图表
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 生命周期钩子
onMounted(() => {
  loadDistributionData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
})

// 暴露方法给父组件
defineExpose({
  refresh: loadDistributionData
})
</script>

<style scoped lang="scss">
.factor-distribution-chart {
  padding: 20px;
  background: var(--bg-primary, #131722);
  border-radius: 8px;

  // 使用全局统一样式，移除本地覆盖

  :deep(.el-radio-group) {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

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

// 统计量卡片
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 16px;

  .stat-card {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--bg-secondary, #1e222d);
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid var(--border-color, #2a2e39);
    transition: all 0.2s;

    &:hover {
      background: var(--bg-primary, #131722);
    }

    .stat-icon {
      flex-shrink: 0;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(41, 98, 255, 0.1);
      border-radius: 6px;
      border: 1px solid rgba(41, 98, 255, 0.2);
      transition: all 0.2s;

      svg {
        width: 19px;
        height: 19px;
        color: var(--accent-blue, #2962ff);
        transition: color 0.2s;
      }
    }

    .stat-label {
      font-size: 10px;
      color: var(--text-primary, #d1d4dc);
      margin-bottom: 4px;
    }

    .stat-value {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      transition: color 0.2s;
    }
  }
}

// 图表容器
.chart-container {
  background: var(--bg-secondary, #1e222d);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color, #2a2e39);
  margin-bottom: 16px;

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
      gap: 8px;

      .control-label {
        font-size: 12px;
        color: var(--text-secondary, #787b86);
      }
    }

    .legend-toggles {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;

      .legend-toggle-item {
        font-size: 11px;
        font-weight: 500;
        cursor: pointer;
        padding: 4px 10px;
        border-radius: 4px;
        transition: all 0.2s;
        user-select: none;
        display: flex;
        align-items: center;
        gap: 6px;
        color: var(--text-secondary, #787b86);

        &:hover {
          background: rgba(41, 98, 255, 0.1);
        }

        &.active {
          color: var(--text-primary, #d1d4dc);
        }

        .legend-icon {
          width: 20px;
          height: 3px;
          display: inline-block;
          flex-shrink: 0;

          &.actual-distribution {
            height: 12px;
            background: linear-gradient(to bottom, #2962ff, #1e88e5);
            border-radius: 2px;
          }

          &.expected-distribution {
            height: 2px;
            border-bottom: 2px dashed #ffa726;
            background: transparent;
          }

          &.median-line {
            height: 2px;
            border-bottom: 2px dashed;
            border-color: inherit;
          }

          &.ideal-zone {
            height: 12px;
            background: rgba(239, 83, 80, 0.35);
            border-radius: 2px;
            border: 1px solid rgba(239, 83, 80, 0.5);
          }
        }
      }
    }
  }

  .chart {
    width: 100%;
    height: 350px;
    background: var(--bg-primary, #131722);
    border-radius: 4px;
  }
}

// 因子切换标签
.factor-tabs {
  background: var(--bg-secondary, #1e222d);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color, #2a2e39);
}
</style>
