<template>
  <div class="factor-analysis-icir">
    <!-- 个体因子综合评估 -->
    <FactorEvaluationCard
      :title="isZh ? '个体因子综合评估' : 'Individual Factor Evaluation'"
      :indicator="individualFactorIndicator"
      :indicator-values="individualFactorValues"
    />

    <ICIRTrendChart
      :task-id="taskId"
      :target-period="icConfig.targetPeriod"
      :method="icConfig.method"
      :is-zh="isZh"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import FactorEvaluationCard from '@/components/ui/FactorEvaluationCard.vue'
import * as echarts from 'echarts'
import ICIRTrendChart from '../../../ICIRTrendChart.vue'
import { useAppStore } from '@/stores/core/AppStore'

interface Props {
  taskId: string
  isZh: boolean
}

const props = defineProps<Props>()

const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// IC/IR配置
const icConfig = reactive({
  method: 'spearman' as 'pearson' | 'spearman',
  threshold: 0.03,
  targetPeriod: 1,
  includeAlpha158: true,
  includeAlpha360: false,
  includeCustom: true
})

// 个体因子评估雷达图
const individualFactorRadarRef = ref<HTMLElement>()

// 个体因子IC/IR数据
const individualFactorData = ref({
  ic_mean: 0,
  ic_std: 0,
  ic_min: 0,
  ic_max: 0,
  ir: 0,
  ic_positive_ratio: 0,
  t_stat: 0,
  p_value: 0,
  monotonicity_score: 0,
  stability_score: 0
})

// 归一化辅助函数
// IC均值：使用绝对值，越大越好（无论正负）
const normalizeIC = (value: number) => Math.max(0, Math.min((Math.abs(value) / 0.05) * 80, 100))
// IC标准差：范围0-0.35，越小越好（波动小更稳定），所以用inverse
const normalizeStd = (value: number) => Math.max(0, Math.min((1 - value / 0.35) * 100, 100))
// IR值：使用绝对值，越大越好
const normalizeRange = (value: number, min: number, max: number) => Math.max(0, (Math.abs(value) / Math.abs(max)) * 100)
const normalizeAbs = (value: number, max: number) => Math.min((Math.abs(value) / max) * 100, 100)
// p值：使用对数归一化，-log10(p)越大越显著，最大取2（对应p=0.01）
const normalizePValue = (value: number) => Math.max(0, Math.min((-Math.log10(Math.max(value, 1e-10)) / 2) * 100, 100))
// IC最小值：越接近0越好（波动小）
const normalizeAbsMin = (value: number) => Math.min((1 - Math.abs(value)) * 100, 100)

// 个体因子综合评估 - 指标配置
const individualFactorIndicator = computed(() => [
  { name: isZh ? 'IC均值' : 'IC Mean', max: 100 },
  { name: isZh ? 'IC标准差' : 'IC Std', max: 100 },
  { name: isZh ? 'IC最大值' : 'IC Max', max: 100 },
  { name: isZh ? 'IC最小值' : 'IC Min', max: 100 },
  { name: isZh ? 'IR值' : 'IR', max: 100 },
  { name: isZh ? '正IC比率' : 'IC+ Ratio', max: 100 },
  { name: isZh ? 't统计量' : 't-Stat', max: 100 },
  { name: isZh ? 'p值' : 'p-Value', max: 100 },
  { name: isZh ? '单调性' : 'Monotonicity', max: 100 },
  { name: isZh ? '稳定性' : 'Stability', max: 100 }
])

// 个体因子综合评估 - 指标值
const individualFactorValues = computed(() => [
  normalizeIC(individualFactorData.value.ic_mean),
  normalizeStd(individualFactorData.value.ic_std),
  normalizeRange(individualFactorData.value.ic_max, -1, 1),
  normalizeAbsMin(individualFactorData.value.ic_min),
  normalizeRange(individualFactorData.value.ir, -2, 2),
  individualFactorData.value.ic_positive_ratio * 100,
  normalizeAbs(individualFactorData.value.t_stat, 5),
  normalizePValue(individualFactorData.value.p_value),
  individualFactorData.value.monotonicity_score * 100,
  individualFactorData.value.stability_score * 100
])

// 综合评分计算
const totalEvaluationScore = computed(() => {
  const scores = [
    normalizeIC(individualFactorData.value.ic_mean),
    normalizeStd(individualFactorData.value.ic_std),
    normalizeRange(individualFactorData.value.ic_max, -1, 1),
    normalizeAbsMin(individualFactorData.value.ic_min),
    normalizeRange(individualFactorData.value.ir, -2, 2),
    individualFactorData.value.ic_positive_ratio * 100,
    normalizeAbs(individualFactorData.value.t_stat, 5),
    normalizePValue(individualFactorData.value.p_value),
    individualFactorData.value.monotonicity_score * 100,
    individualFactorData.value.stability_score * 100
  ]

  const weights = [15, 10, 5, 5, 15, 10, 10, 5, 15, 20]
  let totalWeight = 0
  let weightedSum = 0

  scores.forEach((score, i) => {
    weightedSum += score * weights[i]
    totalWeight += weights[i]
  })

  // 确保评分不低于0
  return Math.max(0, weightedSum / totalWeight)
})

// 获取星星数量
const getStarCount = (score: number): number => {
  if (score >= 90) return 5
  if (score >= 75) return 4
  if (score >= 55) return 3
  if (score >= 35) return 2
  return 1
}

// 获取字母等级
const getLetterGrade = (score: number): string => {
  if (score >= 95) return 'A+'
  if (score >= 85) return 'A'
  if (score >= 75) return 'B+'
  if (score >= 65) return 'B'
  if (score >= 55) return 'C+'
  if (score >= 45) return 'C'
  if (score >= 35) return 'D'
  return 'F'
}

// 因子质量颜色
const getFactorQualityColor = (score: number) => {
  if (score > 100) return '#8b5cf6'
  if (score >= 80) return '#ef5350'
  if (score >= 60) return '#f97316'
  if (score >= 40) return '#2962ff'
  return '#26a69a'
}

// 初始化个体因子雷达图
const initIndividualFactorRadar = () => {
  if (!individualFactorRadarRef.value) return

  const chart = echarts.init(individualFactorRadarRef.value)

  const normalizeValue = (value: number, max: number, min: number = 0, inverse: boolean = false) => {
    const normalized = ((value - min) / (max - min)) * 100
    const clamped = Math.max(0, Math.min(100, normalized))
    return inverse ? (100 - clamped) : clamped
  }

  const radarValues = [
    normalizeValue(individualFactorData.value.ic_mean, 0.1, -0.1),
    // IC标准差：范围0-0.35，inverse=true表示越小越好（波动小更稳定）
    normalizeValue(individualFactorData.value.ic_std, 0.35, 0, true),
    normalizeValue(individualFactorData.value.ic_max, 1, -1),
    normalizeValue(1 - Math.abs(individualFactorData.value.ic_min), 1, 0),
    normalizeValue(individualFactorData.value.ir, 2, -2),
    normalizeValue(individualFactorData.value.ic_positive_ratio, 1, 0),
    normalizeValue(Math.abs(individualFactorData.value.t_stat), 5, 0),
    // p值：使用对数归一化，-log10(p)越大越好（更显著）
    normalizeValue(-Math.log10(Math.max(individualFactorData.value.p_value, 1e-10)), 2, 0, true),
    normalizeValue(individualFactorData.value.monotonicity_score, 1, 0),
    normalizeValue(individualFactorData.value.stability_score, 1, 0)
  ]

  const benchmarkValues = [
    normalizeValue(0.03, 0.1, -0.1),
    normalizeValue(0.08, 0.35, 0, true),
    normalizeValue(0.3, 1, -1),
    normalizeValue(1 - 0.3, 1, 0),
    normalizeValue(0.5, 2, -2),
    normalizeValue(0.55, 1, 0),
    normalizeValue(2.0, 5, 0),
    // 基准p值：0.05对应的-log10(0.05)=1.3
    normalizeValue(-Math.log10(0.05), 2, 0, true),
    normalizeValue(0.6, 1, 0),
    normalizeValue(0.7, 1, 0)
  ]

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e222d',
      borderColor: '#3a3f4b',
      textStyle: { color: '#d1d4dc' },
      formatter: (params: any) => {
        const labels = [
          isZh.value ? 'IC均值' : 'IC Mean',
          isZh.value ? 'IC标准差' : 'IC Std',
          isZh.value ? 'IC最大值' : 'IC Max',
          isZh.value ? 'IC最小值' : 'IC Min',
          isZh.value ? 'IR值' : 'IR',
          isZh.value ? '正IC比率' : 'IC+ Ratio',
          isZh.value ? 't统计量' : 't-Stat',
          isZh.value ? 'p值' : 'p-Value',
          isZh.value ? '单调性' : 'Monotonicity',
          isZh.value ? '稳定性' : 'Stability'
        ]
        const rawValues = [
          individualFactorData.value.ic_mean.toFixed(4),
          individualFactorData.value.ic_std.toFixed(4),
          individualFactorData.value.ic_max.toFixed(4),
          individualFactorData.value.ic_min.toFixed(4),
          individualFactorData.value.ir.toFixed(4),
          (individualFactorData.value.ic_positive_ratio * 100).toFixed(1) + '%',
          individualFactorData.value.t_stat.toFixed(4),
          // p值使用科学计数法显示
          individualFactorData.value.p_value < 0.0001
            ? individualFactorData.value.p_value.toExponential(2)
            : individualFactorData.value.p_value.toFixed(4),
          individualFactorData.value.monotonicity_score.toFixed(2),
          individualFactorData.value.stability_score.toFixed(2)
        ]
        let html = `<div style="padding: 8px;"><strong>${params.name}</strong><br/>`
        labels.forEach((label, i) => {
          html += `<div style="margin-top: 4px;">${label}: ${rawValues[i]}</div>`
        })
        html += '</div>'
        return html
      }
    },
    legend: {
      data: [isZh.value ? '当前因子' : 'Current', isZh.value ? '行业基准' : 'Benchmark'],
      right: 10,
      top: 10,
      orient: 'vertical',
      textStyle: { color: '#d1d4dc', fontSize: 11 }
    },
    radar: {
      center: ['45%', '50%'],
      radius: '60%',
      indicator: [
        { name: isZh.value ? 'IC均值' : 'IC Mean', max: 100 },
        { name: isZh.value ? 'IC标准差' : 'IC Std', max: 100 },
        { name: isZh.value ? 'IC最大值' : 'IC Max', max: 100 },
        { name: isZh.value ? 'IC最小值' : 'IC Min', max: 100 },
        { name: isZh.value ? 'IR值' : 'IR', max: 100 },
        { name: isZh.value ? '正IC比率' : 'IC+ Ratio', max: 100 },
        { name: isZh.value ? 't统计量' : 't-Stat', max: 100 },
        { name: isZh.value ? 'p值' : 'p-Value', max: 100 },
        { name: isZh.value ? '单调性' : 'Monotonicity', max: 100 },
        { name: isZh.value ? '稳定性' : 'Stability', max: 100 }
      ],
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
        data: [
          {
            value: radarValues,
            name: isZh.value ? '当前因子' : 'Current',
            areaStyle: {
              color: 'rgba(239, 83, 80, 0.3)'
            },
            lineStyle: {
              color: '#ef5350',
              width: 2
            },
            itemStyle: {
              color: '#ef5350'
            }
          },
          {
            value: benchmarkValues,
            name: isZh.value ? '行业基准' : 'Benchmark',
            areaStyle: {
              color: 'rgba(255, 152, 0, 0.2)'
            },
            lineStyle: {
              color: '#ff9800',
              width: 2,
              type: 'dashed'
            },
            itemStyle: {
              color: '#ff9800'
            }
          }
        ]
      }
    ]
  }

  chart.setOption(option)
}

// 加载模拟数据
const loadMockData = () => {
  individualFactorData.value = {
    ic_mean: 0.0423,
    ic_std: 0.0821,
    ic_min: -0.2315,
    ic_max: 0.3142,
    ir: 0.5152,
    ic_positive_ratio: 0.5823,
    t_stat: 2.3421,
    p_value: 0.0198,
    monotonicity_score: 0.72,
    stability_score: 0.85
  }
}

// 监听数据变化更新雷达图
watch(individualFactorData, () => {
  nextTick(() => {
    initIndividualFactorRadar()
  })
}, { deep: true })

onMounted(() => {
  loadMockData()
  nextTick(() => {
    setTimeout(() => initIndividualFactorRadar(), 200)
  })
  window.addEventListener('resize', () => {
    if (individualFactorRadarRef.value) {
      const chart = echarts.getInstanceByDom(individualFactorRadarRef.value)
      chart?.resize()
    }
  })
})
</script>

<style scoped lang="scss">
@import '../../../styles/_variables.scss';

.factor-analysis-icir {
  --accent-blue: #2962ff;
  --color-up: #ef5350;
  --color-down: #26a69a;
  --accent-red: #ef5350;
  --accent-green: #26a69a;
  --accent-orange: #ff9800;
  --border-color: #2a2e39;

  width: 100%;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.section-icon {
  width: 16px;
  height: 16px;
}

.single-factor-evaluation-section {
  background: var(--bg-secondary);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  margin-bottom: 4px;
}

.evaluation-metrics-panel {
  display: flex;
  gap: 0;
  padding: 12px 0;
  align-items: flex-start;
}

.evaluation-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 24px;
  flex: 0 0 620px;
  padding-bottom: 0;
}

.evaluation-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.evaluation-item-icon {
  width: 24px;
  height: 24px;
  color: var(--text-primary);
}

.evaluation-item-label {
  min-width: 60px;
  font-size: 12px;
  color: var(--text-primary);
}

.evaluation-item-score {
  min-width: 36px;
  font-size: 14px;
  font-weight: 700;
  text-align: right;
}

.evaluation-item-bar {
  flex: 1;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.evaluation-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.evaluation-item-raw {
  min-width: 50px;
  font-size: 11px;
  color: var(--text-primary);
  text-align: right;
}

.evaluation-total-score-inline {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(239, 83, 80, 0.15) 0%, rgba(30, 34, 45, 0.9) 100%);
  border-radius: 10px;
  border: 1px solid rgba(239, 83, 80, 0.3);
  margin-top: 32px;
}

.total-inline-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  margin-bottom: 0;
}

.total-inline-label {
  font-size: 14px;
  font-weight: 600;
}

.total-inline-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.total-inline-value {
  font-size: 28px;
  font-weight: 700;
}

.total-inline-rating {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.star-rating-inline {
  display: flex;
  gap: 2px;
}

.star-icon-inline {
  width: 14px;
  height: 14px;
}

.letter-grade-inline {
  font-size: 14px;
  font-weight: 700;
}

.total-inline-bar {
  flex: 1;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.total-inline-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.evaluation-radar-wrapper {
  flex: 1;
  min-width: 280px;
  height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radar-chart {
  width: 100%;
  height: 100%;
}
</style>
