<template>
  <div class="factor-evaluation-card">
    <div class="panel-header">
      <div class="panel-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 2 7 12 12 22 7 12 2"/>
          <polyline points="2 17 12 22 22 17"/>
          <polyline points="2 12 12 17 22 12"/>
        </svg>
        {{ title }}
      </div>
    </div>
    <div class="evaluation-metrics-panel">
      <!-- 左侧：指标列表（双列网格） -->
      <div class="evaluation-list">
        <div
          v-for="(ind, idx) in filteredIndicator"
          :key="idx"
          class="evaluation-item"
        >
          <div class="evaluation-item-icon">
            <!-- 根据指标名称显示不同图标 -->
            <svg v-if="ind.name === 'IC均值' || ind.name === 'IC Mean'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
            <svg v-else-if="ind.name === 'IC标准差' || ind.name === 'IC Std'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 3v18h18"></path>
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path>
            </svg>
            <svg v-else-if="ind.name === 'IC最大值' || ind.name === 'IC Max'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="17 11 12 6 7 11"></polyline>
              <polyline points="17 18 12 13 7 18"></polyline>
            </svg>
            <svg v-else-if="ind.name === 'IC最小值' || ind.name === 'IC Min'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="7 13 12 18 17 13"></polyline>
              <polyline points="7 6 12 11 17 6"></polyline>
            </svg>
            <svg v-else-if="ind.name === 'IR值' || ind.name === 'IR'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
            </svg>
            <svg v-else-if="ind.name === '正IC比率' || ind.name === 'IC+ Ratio'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <svg v-else-if="ind.name === 't统计量' || ind.name === 't-Stat'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="20" x2="12" y2="10"></line>
              <line x1="18" y1="20" x2="18" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="16"></line>
            </svg>
            <svg v-else-if="ind.name === 'p值' || ind.name === 'p-Value'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
            </svg>
            <svg v-else-if="ind.name === '单调性' || ind.name === 'Monotonicity'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
              <polyline points="17 6 23 6 23 12"></polyline>
            </svg>
            <svg v-else-if="ind.name === '稳定性' || ind.name === 'Stability'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
          </div>
          <span class="evaluation-item-label">{{ ind.name }}</span>
          <span class="evaluation-item-score" :style="{ color: getColor(idx) }">
            {{ getScore(idx) }}
          </span>
          <div class="evaluation-item-bar">
            <div
              class="evaluation-bar-fill"
              :style="{
                width: getScore(idx) + '%',
                backgroundColor: getColor(idx)
              }"
            ></div>
          </div>
          <span class="evaluation-item-raw">{{ getRawValue(idx) }}</span>
        </div>
        <!-- 综合评分 inline -->
        <div class="evaluation-total-score-inline" :style="totalScoreStyle">
          <div class="total-inline-header">
            <span class="total-inline-label" :style="{ color: getTotalColor() }">综合评分</span>
          </div>
          <div class="total-inline-value" :style="{ color: getTotalColor() }">
            {{ totalScore.toFixed(1) }}
          </div>
          <div class="total-inline-rating">
            <div class="star-rating" :style="{ color: getTotalColor() }">
              <svg v-for="i in 5" :key="i" class="star-icon" :class="{ filled: i <= starCount }" viewBox="0 0 24 24" :fill="i <= starCount ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="1.5">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
            </div>
            <div class="letter-grade" :style="{ color: getTotalColor() }">
              {{ letterGrade }}
            </div>
          </div>
          <div class="total-inline-bar">
            <div class="total-inline-fill" :style="{ width: (totalScore > 100 ? 100 : totalScore) + '%', backgroundColor: getTotalColor() }"></div>
          </div>
        </div>
      </div>
      <!-- 右侧雷达图 -->
      <div class="radar-chart-wrapper">
        <div ref="chartRef" class="radar-chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'

interface Indicator {
  name: string
  max?: number
}

interface RadarDataItem {
  name: string
  value: number[]
  color?: string
  areaColor?: string
  lineType?: 'solid' | 'dashed'
}

interface Props {
  title?: string
  indicator?: Indicator[]
  data?: RadarDataItem[]
  indicatorValues?: number[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '个体因子综合评估',
  indicator: () => [
    { name: 'IC均值', max: 100 },
    { name: 'IC标准差', max: 100 },
    { name: 'IC最大值', max: 100 },
    { name: 'IC最小值', max: 100 },
    { name: 'IR值', max: 100 },
    { name: '正IC比率', max: 100 },
    { name: 't统计量', max: 100 },
    { name: 'p值', max: 100 },
    { name: '单调性', max: 100 },
    { name: '稳定性', max: 100 }
  ],
  data: () => [
    {
      name: '当前因子',
      value: [75, 60, 80, 55, 70, 85, 65, 50, 72, 68],
      color: '#409ee1',
      areaColor: 'rgba(64, 158, 225, 0.3)',
      lineType: 'solid'
    },
    {
      name: '行业基准',
      value: [60, 55, 65, 45, 55, 70, 50, 60, 60, 55],
      color: '#ff9800',
      areaColor: 'rgba(255, 152, 0, 0.2)',
      lineType: 'dashed'
    }
  ],
  indicatorValues: () => [0.035, 0.02, 0.08, -0.02, 1.5, 0.65, 2.5, 0.03, 0.75, 0.8]
})

// Helper functions
const getScore = (idx: number) => {
  const dataValues = props.data[0]?.value || []
  const score = dataValues[idx] || 0
  // 分数显示1位小数
  return score.toFixed(1)
}

const getRawValue = (idx: number) => {
  const raw = props.indicatorValues[idx]
  if (raw === undefined) return '0'
  if (typeof raw === 'number') {
    const name = props.indicator[idx]?.name || ''

    // 比率类指标：显示为百分比（已经是百分比形式）
    if (name.includes('比率') || name.includes('Ratio') ||
        name.includes('单调性') || name.includes('Monotonicity') ||
        name.includes('稳定性') || name.includes('Stability')) {
      return raw.toFixed(1) + '%'
    }

    // 其他原始值：统一显示2位小数
    return raw.toFixed(2)
  }
  return raw
}

// 过滤掉综合评分，只显示普通指标
const filteredIndicator = computed(() => {
  return props.indicator.filter(ind => {
    const name = ind.name.toLowerCase()
    return !name.includes('综合') && !name.includes('overall') && !name.includes('total')
  })
})

// 获取综合评分在原数组中的索引
const totalScoreIndex = computed(() => {
  return props.indicator.findIndex(ind => {
    const name = ind.name.toLowerCase()
    return name.includes('综合') || name.includes('overall') || name.includes('total')
  })
})

const getColor = (idx: number) => {
  const score = getScore(idx)
  if (score > 100) return '#8b5cf6'
  if (score >= 80) return '#ef5350'
  if (score >= 60) return '#f97316'
  if (score >= 40) return '#2962ff'
  return '#26a69a'
}

// Total score - 使用综合评分指标的值，如果没有则计算平均值
const totalScore = computed(() => {
  // 如果有综合评分指标，使用其值
  if (totalScoreIndex.value >= 0) {
    const scores = props.data[0]?.value || []
    return scores[totalScoreIndex.value] || 0
  }
  // 否则计算所有指标的平均值
  const scores = props.data[0]?.value || []
  if (scores.length === 0) return 0
  return scores.reduce((a, b) => a + b, 0) / scores.length
})

// Star count
const starCount = computed(() => {
  const score = totalScore.value
  if (score >= 90) return 5
  if (score >= 75) return 4
  if (score >= 55) return 3
  if (score >= 35) return 2
  return 1
})

// Letter grade
const letterGrade = computed(() => {
  const score = totalScore.value
  if (score >= 90) return 'A+'
  if (score >= 80) return 'A'
  if (score >= 70) return 'B+'
  if (score >= 60) return 'B'
  if (score >= 50) return 'C+'
  if (score >= 40) return 'C'
  return 'D'
})

// Total score color
const getTotalColor = () => {
  const score = totalScore.value
  if (score > 100) return '#8b5cf6'
  if (score >= 80) return '#ef5350'
  if (score >= 60) return '#f97316'
  if (score >= 40) return '#2962ff'
  return '#26a69a'
}

// 底板样式（根据总分动态计算）
const totalScoreStyle = computed(() => {
  const color = getTotalColor()
  return {
    background: `linear-gradient(135deg, ${color}26 0%, rgba(30, 34, 45, 0.9) 100%)`,
    borderColor: `${color}4d`
  }
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value, 'dark')

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e222d',
      borderColor: '#363a45',
      textStyle: { color: '#d1d4dc' }
    },
    legend: {
      show: true,
      right: 10,
      top: 10,
      orient: 'vertical',
      itemWidth: 12,
      itemHeight: 6,
      textStyle: { color: '#d1d4dc', fontSize: 11 },
      data: props.data.map(d => ({ name: d.name, icon: 'roundRect' }))
    },
    radar: {
      indicator: props.indicator.map(ind => ({
        name: ind.name,
        max: ind.max || 100
      })),
      center: ['45%', '50%'],
      radius: '60%',
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        color: '#d1d4dc',
        fontSize: 11
      },
      splitLine: {
        lineStyle: { color: '#3a3f4b' }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(30, 34, 45, 0.2)', 'rgba(30, 34, 45, 0.3)', 'rgba(30, 34, 45, 0.4)', 'rgba(30, 34, 45, 0.5)', 'rgba(30, 34, 45, 0.6)']
        }
      },
      axisLine: {
        lineStyle: { color: '#3a3f4b' }
      }
    },
    series: [
      {
        type: 'radar',
        data: props.data.map(d => ({
          value: d.value,
          name: d.name,
          areaStyle: {
            color: d.areaColor
          },
          lineStyle: {
            color: d.color,
            width: 2,
            type: d.lineType || 'solid'
          },
          itemStyle: {
            color: d.color
          }
        }))
      }
    ]
  }

  chartInstance.setOption(option)
}

const resizeChart = () => {
  chartInstance?.resize()
}

onMounted(() => {
  nextTick(() => {
    initChart()
    window.addEventListener('resize', resizeChart)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})

watch(() => props.data, initChart, { deep: true })
</script>

<style lang="scss" scoped>
.factor-evaluation-card {
  width: 100%;
  box-sizing: border-box;
  background: #1e222d;
  border-radius: 8px;
  border: 1px solid #363a45;
  padding: 16px;
  margin-left: 0;

  .panel-header {
    padding: 4px 0 2px 0;
  }

  .panel-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #d1d4dc;
    margin-bottom: 4px;
  }

  .icon-sm {
    width: 16px;
    height: 16px;
    color: #409ee1;
  }

  .evaluation-metrics-panel {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 8px 0;
    align-items: stretch;
    min-width: 0;
    width: 100%;
  }

  .evaluation-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 16px;
    flex: 1 1 450px;
    min-width: 320px;
    padding-bottom: 0;
  }

  .evaluation-item {
    display: flex;
    align-items: center;
    gap: 5px;
    min-width: 140px;
    flex: 1 1 40%;
  }

  .evaluation-item-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;

    svg {
      width: 14px;
      height: 14px;
      color: #d1d4dc;
    }
  }

  .evaluation-item-label {
    min-width: 55px;
    font-size: 11px;
    color: #d1d4dc;
  }

  .evaluation-item-score {
    min-width: 32px;
    font-size: 13px;
    font-weight: 700;
    text-align: right;
  }

  .evaluation-item-bar {
    flex: 1;
    height: 5px;
    background: rgba(255,255,255,0.1);
    border-radius: 2px;
    overflow: hidden;
    min-width: 50px;
  }

  .evaluation-bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.3s ease;
  }

  .evaluation-item-raw {
    min-width: 45px;
    font-size: 10px;
    color: #d1d4dc;
    text-align: right;
    font-family: monospace;
  }

  .evaluation-total-score-inline {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 14px;
    border-radius: 8px;
    border: 1px solid;
    margin-top: 16px;
    flex: 1 1 45%;
    min-width: 150px;
    box-sizing: border-box;
  }

  .total-inline-header {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
    margin-bottom: 0;
  }

  .total-inline-label {
    font-size: 12px;
    font-weight: 600;
  }

  .total-inline-value {
    font-size: 24px;
    font-weight: 700;
    min-width: 50px;
    text-align: center;
  }

  .total-inline-rating {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .star-rating {
    display: flex;
    gap: 2px;
  }

  .star-icon {
    width: 12px;
    height: 12px;
    opacity: 0.3;

    &.filled {
      opacity: 1;
    }
  }

  .letter-grade {
    font-size: 14px;
    font-weight: 700;
  }

  .total-inline-bar {
    flex: 1;
    height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    overflow: hidden;
  }

  .total-inline-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
  }

  .radar-chart-wrapper {
    flex: 1 1 320px;
    min-width: 280px;
    min-height: 200px;
    max-height: 350px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .radar-chart {
    width: 100%;
    height: 100%;
  }
}
</style>
