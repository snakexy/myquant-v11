<template>
  <div class="factor-analysis-overview">
    <!-- Factor Library Quality Radar Chart -->
    <div class="radar-section">
      <h3 class="section-title">
        <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
          <polyline points="2 17 12 22 22 17"></polyline>
          <polyline points="2 12 12 17 22 12"></polyline>
        </svg>
        {{ isZh ? '因子库整体质量' : 'Factor Library Quality' }}
      </h3>
      <div class="quality-metrics-panel">
        <!-- Left: Quality Metrics List -->
        <div class="quality-list">
          <!-- Average IC -->
          <div class="quality-item">
            <div class="quality-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
            </div>
            <span class="quality-item-label">{{ isZh ? '平均IC' : 'Avg IC' }}</span>
            <span class="quality-item-score" :style="{ color: getFactorQualityColor((stats.icMean / 0.05) * 80) }">
              {{ ((stats.icMean / 0.05) * 80).toFixed(1) }}
            </span>
            <div class="quality-item-bar">
              <div class="quality-bar-fill" :style="{ width: Math.min((stats.icMean / 0.05) * 80, 100) + '%', backgroundColor: getFactorQualityColor((stats.icMean / 0.05) * 80) }"></div>
            </div>
            <span class="quality-item-raw">{{ stats.icMean.toFixed(3) }}</span>
          </div>
          <!-- IR Ratio -->
          <div class="quality-item">
            <div class="quality-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
              </svg>
            </div>
            <span class="quality-item-label">{{ isZh ? 'IR比率' : 'IR Ratio' }}</span>
            <span class="quality-item-score" :style="{ color: getFactorQualityColor((stats.irRatio / 0.8) * 80) }">
              {{ ((stats.irRatio / 0.8) * 80).toFixed(1) }}
            </span>
            <div class="quality-item-bar">
              <div class="quality-bar-fill" :style="{ width: Math.min((stats.irRatio / 0.8) * 80, 100) + '%', backgroundColor: getFactorQualityColor((stats.irRatio / 0.8) * 80) }"></div>
            </div>
            <span class="quality-item-raw">{{ stats.irRatio.toFixed(2) }}</span>
          </div>
          <!-- Pass Rate -->
          <div class="quality-item">
            <div class="quality-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
            <span class="quality-item-label">{{ isZh ? '通过率' : 'Pass Rate' }}</span>
            <span class="quality-item-score" :style="{ color: getFactorQualityColor(stats.passRate * 1.2) }">
              {{ (stats.passRate * 1.2).toFixed(1) }}
            </span>
            <div class="quality-item-bar">
              <div class="quality-bar-fill" :style="{ width: Math.min(stats.passRate * 1.2, 100) + '%', backgroundColor: getFactorQualityColor(stats.passRate * 1.2) }"></div>
            </div>
            <span class="quality-item-raw">{{ stats.passRate.toFixed(1) }}%</span>
          </div>
          <!-- Factor Count -->
          <div class="quality-item">
            <div class="quality-item-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
              </svg>
            </div>
            <span class="quality-item-label">{{ isZh ? '因子数量' : 'Factor Count' }}</span>
            <span class="quality-item-score" :style="{ color: getFactorQualityColor((stats.totalFactors / 200) * 80) }">
              {{ ((stats.totalFactors / 200) * 80).toFixed(1) }}
            </span>
            <div class="quality-item-bar">
              <div class="quality-bar-fill" :style="{ width: Math.min((stats.totalFactors / 200) * 80, 100) + '%', backgroundColor: getFactorQualityColor((stats.totalFactors / 200) * 80) }"></div>
            </div>
            <span class="quality-item-raw">{{ stats.totalFactors }}</span>
          </div>
        </div>
        <!-- 综合评分 -->
        <div class="quality-total-score">
          <div class="quality-total-header">
            <span class="quality-total-label" :style="{ color: getFactorQualityColor(factorLibraryTotalScore) }">{{ isZh ? '综合评分' : 'Total' }}</span>
          </div>
          <div class="quality-total-value" :style="{ color: getFactorQualityColor(factorLibraryTotalScore) }">
            {{ factorLibraryTotalScore.toFixed(1) }}
          </div>
          <!-- 星级和字母等级 -->
          <div class="quality-rating">
            <div class="star-rating" :style="{ color: getFactorQualityColor(factorLibraryTotalScore) }">
              <svg v-for="i in 5" :key="i" class="star-icon" :class="{ filled: i <= getStarCount(factorLibraryTotalScore) }" viewBox="0 0 24 24" :fill="i <= getStarCount(factorLibraryTotalScore) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="1.5">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
            </div>
            <div class="letter-grade" :style="{ color: getFactorQualityColor(factorLibraryTotalScore) }">
              {{ getLetterGrade(factorLibraryTotalScore) }}
            </div>
          </div>
          <div class="quality-total-bar">
            <div class="quality-total-fill" :style="{ width: Math.min(factorLibraryTotalScore, 100) + '%', backgroundColor: getFactorQualityColor(factorLibraryTotalScore) }"></div>
          </div>
        </div>
        <!-- Right: Radar Chart -->
        <div class="radar-chart-wrapper">
          <div ref="factorQualityRadarRef" class="radar-chart"></div>
        </div>
      </div>
    </div>

    <!-- Progress Section -->
    <div class="progress-section">
      <div class="progress-header">
        <span class="progress-title">
          <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          {{ isZh ? '分析进度' : 'Analysis Progress' }}
        </span>
        <span class="progress-percent">{{ stats.progress }}%</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${stats.progress}%` }"></div>
      </div>
    </div>

    <!-- Top Factors Table -->
    <h3 class="section-title">
      <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
      </svg>
      {{ isZh ? '表现最佳因子' : 'Top Performing Factors' }}
    </h3>
    <table class="data-table">
      <thead>
        <tr>
          <th>{{ isZh ? '因子名称' : 'Factor Name' }}</th>
          <th>{{ isZh ? 'IC均值' : 'IC Mean' }}</th>
          <th>IR</th>
          <th>t-Stat</th>
          <th>{{ isZh ? '状态' : 'Status' }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="factor in topFactors" :key="factor.factor_name">
          <td>{{ factor.factor_name }}</td>
          <td :class="['value', { positive: factor.ic > 0.03, negative: factor.ic < 0 }]">
            {{ factor.ic.toFixed(3) }}
          </td>
          <td :class="['value', { positive: factor.ir > 0.5, negative: factor.ir < 0 }]">
            {{ factor.ir.toFixed(2) }}
          </td>
          <td :class="['value', { positive: factor.t_stat > 2 }]">
            {{ factor.t_stat.toFixed(2) }}
          </td>
          <td>
            <span :class="['status-badge', factor.status]">
              {{ factor.status === 'pass' ? (isZh ? '通过' : 'Pass') : (isZh ? '失败' : 'Fail') }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <ActionButton
        type="primary"
        :label="isAnalyzing ? (isZh ? '分析中...' : 'Analyzing...') : (isZh ? '运行完整分析' : 'Run Full Analysis')"
        :loading="isAnalyzing"
        :disabled="isAnalyzing"
        @click="runFullAnalysis"
      />
      <ActionButton
        type="success"
        :label="isZh ? '完成当前步骤' : 'Complete Step'"
        @click="completeStep"
      />
      <ActionButton
        type="default"
        :label="isZh ? '导出结果' : 'Export Results'"
        @click="exportResults"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import * as echarts from 'echarts'
import { useAppStore } from '@/stores/core/AppStore'

interface Props {
  taskId: string
  isZh: boolean
}

interface Emits {
  stepComplete: [data: any]
  dataUpdate: [data: any]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// Statistics data
const stats = reactive({
  totalFactors: 168,
  icMean: 0.045,
  irRatio: 0.78,
  qualifiedCount: 45,
  passRate: 26.8,
  progress: 67
})

// Top factors
const topFactors = ref([
  { factor_name: 'MA60_Cross_Price', ic: 0.058, ir: 0.92, t_stat: 3.45, p_value: 0.001, status: 'pass' },
  { factor_name: 'RSM60_Std_Dev', ic: 0.052, ir: 0.85, t_stat: 3.12, p_value: 0.002, status: 'pass' },
  { factor_name: 'ROC20_Return', ic: 0.049, ir: 0.78, t_stat: 2.89, p_value: 0.004, status: 'pass' },
  { factor_name: 'Beta60_Price', ic: 0.022, ir: 0.45, t_stat: 1.56, p_value: 0.12, status: 'fail' },
  { factor_name: 'VOL30_Volume', ic: 0.041, ir: 0.72, t_stat: 2.67, p_value: 0.008, status: 'pass' }
])

// Factor Quality Radar Chart
const factorQualityRadarRef = ref<HTMLElement>()

// Factor quality data
const factorQualityData = computed(() => {
  const icScore = Math.min((stats.icMean / 0.05) * 80, 100)
  const irScore = Math.min((stats.irRatio / 0.8) * 80, 100)
  const passScore = Math.min(stats.passRate * 1.2, 100)
  const countScore = Math.min((stats.totalFactors / 200) * 80, 100)
  return [icScore, irScore, passScore, countScore]
})

// Factor quality color
const getFactorQualityColor = (score: number) => {
  if (score > 100) return '#8b5cf6'
  if (score >= 80) return '#ef5350'
  if (score >= 60) return '#f97316'
  if (score >= 40) return '#2962ff'
  return '#26a69a'
}

// Get star count
const getStarCount = (score: number): number => {
  if (score >= 90) return 5
  if (score >= 75) return 4
  if (score >= 55) return 3
  if (score >= 35) return 2
  return 1
}

// Get letter grade
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

// Factor library total score
const factorLibraryTotalScore = computed(() => {
  const scores = factorQualityData.value
  // 权重: IC(30%) + IR(30%) + 通过率(25%) + 因子数量(15%)
  const weights = [30, 30, 25, 15]
  let weightedSum = 0
  let totalWeight = 0
  scores.forEach((score, i) => {
    weightedSum += score * weights[i]
    totalWeight += weights[i]
  })
  return weightedSum / totalWeight
})

// Industry benchmark data
const factorQualityBenchmark = computed(() => {
  const icBenchmark = 0.03
  const irBenchmark = 0.4
  const passBenchmark = 30
  const countBenchmark = 158

  const icScore = Math.min((icBenchmark / 0.05) * 80, 100)
  const irScore = Math.min((irBenchmark / 0.8) * 80, 100)
  const passScore = Math.min(passBenchmark * 1.2, 100)
  const countScore = Math.min((countBenchmark / 200) * 80, 100)

  return [icScore, irScore, passScore, countScore]
})

// Initialize radar chart
let radarInitRetry = 0
const initFactorQualityRadar = () => {
  radarInitRetry++
  if (radarInitRetry > 10) {
    return
  }

  const container = document.querySelector('.radar-chart') as HTMLElement
  if (!container) {
    setTimeout(() => initFactorQualityRadar(), 300)
    return
  }

  let chart = echarts.getInstanceByDom(container)
  if (!chart) {
    chart = echarts.init(container)
  }

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e222d',
      borderColor: '#3a3f4b',
      textStyle: { color: '#d1d4dc' }
    },
    legend: {
      data: [isZh.value ? '当前因子库' : 'Current', isZh.value ? '行业基准' : 'Benchmark'],
      right: 30,
      top: 10,
      orient: 'vertical',
      textStyle: { color: '#d1d4dc', fontSize: 11 }
    },
    radar: {
      center: ['45%', '50%'],
      radius: '60%',
      indicator: [
        { name: isZh.value ? '平均IC' : 'Avg IC', max: 100 },
        { name: isZh.value ? 'IR比率' : 'IR Ratio', max: 100 },
        { name: isZh.value ? '通过率' : 'Pass Rate', max: 100 },
        { name: isZh.value ? '因子数量' : 'Factor Count', max: 100 }
      ],
      shape: 'polygon',
      splitNumber: 4,
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
        data: [
          {
            value: factorQualityData.value,
            name: isZh.value ? '当前因子库' : 'Current',
            areaStyle: {
              color: 'rgba(64, 158, 225, 0.3)'
            },
            lineStyle: {
              color: '#409ee1',
              width: 2
            },
            itemStyle: {
              color: '#409ee1'
            }
          },
          {
            value: factorQualityBenchmark.value,
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
  chart.resize()
}

// Listen to component mount
onMounted(() => {
  radarInitRetry = 0
  nextTick(() => {
    setTimeout(() => initFactorQualityRadar(), 200)
  })
  window.addEventListener('resize', () => {
    const container = document.querySelector('.radar-chart') as HTMLElement
    if (container) {
      const chart = echarts.getInstanceByDom(container)
      chart?.resize()
    }
  })
})

// Action methods
const isAnalyzing = ref(false)

const runFullAnalysis = async () => {
  isAnalyzing.value = true
  try {
    for (let i = 0; i <= 100; i += 5) {
      stats.progress = i
      await new Promise(resolve => setTimeout(resolve, 200))
    }
    nextTick(() => {
      initFactorQualityRadar()
    })
    isAnalyzing.value = false
    emit('dataUpdate', { analysisComplete: true })
  } catch (error) {
    console.error('Analysis failed:', error)
    isAnalyzing.value = false
  }
}

const exportResults = () => {
  console.log('Exporting results...')
}

const completeStep = () => {
  emit('stepComplete', { step: 3, stats: stats })
}
</script>

<style scoped lang="scss">
@import '../../../styles/_variables.scss';

.factor-analysis-overview {
  --accent-blue: #2962ff;
  --color-up: #ef5350;
  --color-down: #26a69a;
  --accent-red: #ef5350;
  --accent-green: #26a69a;
  --accent-orange: #ff9800;
  --border-color: #2a2e39;

  width: 100%;
}

.radar-section {
  width: 100%;
  box-sizing: border-box;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
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

.quality-metrics-panel {
  display: flex;
  gap: 0;
  padding: 12px 0;
  align-items: center;
}

.quality-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 0 0 500px;
  padding-left: 20px;
}

.quality-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quality-item-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
}

.quality-item-label {
  min-width: 70px;
  font-size: 12px;
  color: var(--text-primary);
}

.quality-item-score {
  font-size: 20px;
  font-weight: 700;
  width: 50px;
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
  color: var(--text-primary);
  width: 50px;
  text-align: right;
}

.quality-total-score {
  flex: 0 0 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(239, 83, 80, 0.15) 0%, rgba(30, 34, 45, 0.9) 100%);
  border-radius: 10px;
  border: 1px solid rgba(239, 83, 80, 0.3);
  margin-left: 16px;
  transition: all 0.3s;

  &:hover {
    border-color: rgba(239, 83, 80, 0.5);
    background: linear-gradient(135deg, rgba(239, 83, 80, 0.2) 0%, rgba(30, 34, 45, 0.95) 100%);
  }
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
  min-width: 300px;
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radar-chart {
  width: 100%;
  height: 100%;
}

.progress-section {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  margin-bottom: 24px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.progress-percent {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent-blue);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-blue), var(--accent-orange));
  transition: width 0.3s ease;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.pass {
  background: rgba(38, 166, 154, 0.2);
  color: var(--accent-green);
}

.status-badge.fail {
  background: rgba(239, 83, 80, 0.2);
  color: var(--accent-red);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2952cc;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-success {
  background: var(--accent-green);
  color: white;
}

.btn-success:hover {
  background: #229a8f;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-secondary);
}
</style>
