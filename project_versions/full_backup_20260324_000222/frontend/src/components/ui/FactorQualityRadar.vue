<template>
  <div class="radar-card">
    <div class="panel-header">
      <div class="panel-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15 8.5 22 9 17 14 18.5 21 12 17.5 5.5 21 7 14 2 9 9 2 12 2"/>
        </svg>
        {{ title }}
      </div>
    </div>
    <div class="quality-metrics-panel">
      <!-- 左侧指标列表 -->
      <div class="quality-list">
        <div
          v-for="(ind, idx) in indicator"
          :key="idx"
          class="quality-item"
        >
          <div class="quality-item-icon">
            <!-- 平均IC: 折线图 -->
            <svg v-if="ind.name === '平均IC'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
            <!-- IR比率: 金字塔 -->
            <svg v-else-if="ind.name === 'IR比率'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
            </svg>
            <!-- 通过率: 对勾 -->
            <svg v-else-if="ind.name === '通过率'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <!-- 因子数量: 网格 -->
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
          </div>
          <span class="quality-item-label">{{ ind.name }}</span>
          <span class="quality-item-score" :style="{ color: getColor(idx) }">
            {{ getScore(idx) }}
          </span>
          <div class="quality-item-bar">
            <div
              class="quality-bar-fill"
              :style="{
                width: getScore(idx) + '%',
                backgroundColor: getColor(idx)
              }"
            ></div>
          </div>
          <span class="quality-item-raw">{{ getRawValue(idx) }}</span>
        </div>
      </div>
      <!-- 综合评分 -->
      <div class="quality-total-score" :style="hoverStyle ? totalScoreHoverStyle : totalScoreStyle">
        <div class="quality-total-header">
          <span class="quality-total-label" :style="{ color: getTotalColor() }">综合评分</span>
        </div>
        <div class="quality-total-value" :style="{ color: getTotalColor() }">
          {{ totalScore.toFixed(1) }}
        </div>
        <div class="quality-rating">
          <div class="star-rating" :style="{ color: getTotalColor() }">
            <svg v-for="i in 5" :key="i" class="star-icon" :class="{ filled: i <= starCount }" viewBox="0 0 24 24" :fill="i <= starCount ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="1.5">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
          </div>
          <div class="letter-grade" :style="{ color: getTotalColor() }">
            {{ letterGrade }}
          </div>
        </div>
        <div class="quality-total-bar">
          <div class="quality-total-fill" :style="{ width: (totalScore > 100 ? 100 : totalScore) + '%', backgroundColor: getTotalColor() }"></div>
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
  title: '因子库整体质量',
  indicator: () => [
    { name: '平均IC', max: 100 },
    { name: 'IR比率', max: 100 },
    { name: '通过率', max: 100 },
    { name: '因子数量', max: 100 }
  ],
  data: () => [
    {
      name: '当前因子库',
      value: [75, 68, 82, 90],
      color: '#409ee1',
      areaColor: 'rgba(64, 158, 225, 0.3)',
      lineType: 'solid'
    },
    {
      name: '行业基准',
      value: [60, 55, 70, 80],
      color: '#ff9800',
      areaColor: 'rgba(255, 152, 0, 0.2)',
      lineType: 'dashed'
    }
  ],
  indicatorValues: () => [0.035, 0.85, 0.72, 150]
})

// Helper functions for indicator display
const getScore = (idx: number) => {
  const dataValues = props.data[0]?.value || []
  const score = dataValues[idx] || 0
  return Number(score.toFixed(1))
}

const getRawValue = (idx: number) => {
  const raw = props.indicatorValues[idx]
  if (raw === undefined || raw === null || isNaN(raw)) return '-'
  const val = Number(raw)

  // 根据指标名称显示不同格式
  const name = props.indicator[idx]?.name || ''

  // 因子数量：显示整数
  if (name.includes('数量') || name.includes('Count') || name.includes('因子')) {
    return Math.round(val).toString()
  }

  // IC/IR：直接显示原始值
  if (name.includes('IC') || name.includes('IR')) {
    return val.toFixed(2)
  }

  // 通过率：已经是百分比格式
  if (name.includes('率') || name.includes('Rate') || name.includes('通过')) {
    if (val > 100) {
      return Math.round(val).toString()
    }
    return val.toFixed(1) + '%'
  }

  // 默认处理
  if (Math.abs(val) < 1) return val.toFixed(3)
  if (Math.abs(val) < 100) return val.toFixed(2)
  return Math.round(val).toString()
}

const getColor = (idx: number) => {
  const score = getScore(idx)

  if (score > 100) return '#8b5cf6'
  if (score >= 80) return '#ef5350'
  if (score >= 60) return '#f97316'
  if (score >= 40) return '#2962ff'
  return '#26a69a'
}

// Total score (综合评分)
const totalScore = computed(() => {
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

// 底板颜色样式（根据总分动态计算）
const totalScoreStyle = computed(() => {
  const color = getTotalColor()
  return {
    background: `linear-gradient(135deg, ${color}26 0%, rgba(30, 34, 45, 0.9) 100%)`,
    borderColor: `${color}4d`
  }
})

// hover 时的底板颜色
const totalScoreHoverStyle = computed(() => {
  const color = getTotalColor()
  return {
    borderColor: `${color}80`,
    background: `linear-gradient(135deg, ${color}33 0%, rgba(30, 34, 45, 0.95) 100%)`
  }
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null
const hoverStyle = ref(false)

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
      shape: 'polygon',
      splitNumber: 4,
      center: ['45%', '50%'],
      radius: '60%',
      axisNameGap: 8,
      axisName: {
        color: '#d1d4dc',
        fontSize: 12
      },
      splitLine: {
        lineStyle: { color: '#3a3f4b' }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(30, 34, 45, 0.2)', 'rgba(30, 34, 45, 0.4)', 'rgba(30, 34, 45, 0.6)', 'rgba(30, 34, 45, 0.8)']
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
.radar-card {
  width: 100%;
  box-sizing: border-box;
  background: #1e222d;
  border-radius: 8px;
  border: 1px solid #363a45;
  padding: 12px;

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
    width: 18px;
    height: 18px;
    color: #409ee1;
  }

  .quality-metrics-panel {
    display: flex;
    flex-wrap: wrap;
    gap: 0;
    padding: 4px 0;
    align-items: center;
  }

  .quality-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
    min-width: 150px;
    padding-left: 0;
  }

  .quality-item {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .quality-item-icon {
    width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;

    svg {
      width: 12px;
      height: 12px;
      color: #d1d4dc;
    }
  }

  .quality-item-label {
    min-width: 60px;
    font-size: 12px;
    color: #d1d4dc;
  }

  .quality-item-score {
    font-size: 20px;
    font-weight: 700;
    width: 45px;
    text-align: right;
  }

  .quality-item-bar {
    flex: 1;
    height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    overflow: hidden;
    min-width: 80px;
  }

  .quality-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
  }

  .quality-item-raw {
    font-size: 12px;
    color: #d1d4dc;
    width: 40px;
    text-align: right;
    font-family: monospace;
  }

  .quality-total-score {
    flex: 0 0 160px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 16px 12px;
    border-radius: 10px;
    border: 1px solid;
    margin-left: 16px;
    transition: all 0.3s;
  }

  .quality-total-header {
    margin-bottom: 8px;
  }

  .quality-total-label {
    font-size: 14px;
    font-weight: 600;
  }

  .quality-total-value {
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
  }

  .quality-rating {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
  }

  .star-rating {
    display: flex;
    gap: 2px;
  }

  .star-icon {
    width: 14px;
    height: 14px;
    opacity: 0.3;

    &.filled {
      opacity: 1;
    }
  }

  .letter-grade {
    font-size: 16px;
    font-weight: 700;
  }

  .quality-total-bar {
    width: 100%;
    height: 6px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 12px;
  }

  .quality-total-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
  }

  .radar-chart-wrapper {
    flex: 1;
    min-width: 180px;
    aspect-ratio: 1;
    max-height: 220px;
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
