<template>
  <div class="step-factor-analysis-panel">
    <!-- Tabs -->
    <div class="content-tabs">
      <button
        v-for="tab in currentTabs"
        :key="tab.id"
        :class="['content-tab', { active: currentTab === tab.id }]"
        @click="switchTab(tab.id)"
      >
        <svg v-if="tab.id === 'overview'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="14" y="3" width="7" height="7"></rect>
          <rect x="14" y="14" width="7" height="7"></rect>
          <rect x="3" y="14" width="7" height="7"></rect>
        </svg>
        <svg v-else-if="tab.id === 'ic-ir'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
          <polyline points="17 6 23 6 23 12"></polyline>
        </svg>
        <svg v-else-if="tab.id === 'correlation'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="2"></circle>
          <path d="M16.24 7.76a6 6 0 010 8.49m-8.48-.01a6 6 0 010-8.49m11.31-2.82a10 10 0 010 14.14m-14.14 0a10 10 0 010-14.14"></path>
        </svg>
        <svg v-else-if="tab.id === 'distribution'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
        <svg v-else class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
        </svg>
        {{ isZh ? tab.nameZh : tab.name }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Overview Tab -->
      <div v-if="currentTab === 'overview'" class="tab-pane active">
        <!-- 因子库质量雷达图 -->
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
            <!-- 左侧：指标列表 -->
            <div class="quality-list">
              <!-- 平均IC -->
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
              <!-- IR比率 -->
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
              <!-- 通过率 -->
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
              <!-- 因子数量 -->
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
            <!-- 右侧：雷达图 -->
            <div class="radar-chart-wrapper">
              <div ref="factorQualityRadarRef" class="radar-chart"></div>
            </div>
          </div>
        </div>

        <!-- Progress -->
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
          <button class="btn btn-primary" @click="runFullAnalysis" :disabled="isAnalyzing">
            {{ isAnalyzing ? (isZh ? '分析中...' : 'Analyzing...') : (isZh ? '运行完整分析' : 'Run Full Analysis') }}
          </button>
          <button class="btn btn-success" @click="completeStep">
            {{ isZh ? '完成当前步骤' : 'Complete Step' }} ✓
          </button>
          <button class="btn btn-secondary" @click="exportResults">
            {{ isZh ? '导出结果' : 'Export Results' }}
          </button>
        </div>
      </div>

      <!-- IC/IR Tab -->
      <div v-if="currentTab === 'ic-ir'" class="tab-pane active">
        <ICIRTrendChart
          :task-id="taskId"
          :target-period="icConfig.targetPeriod"
          :method="icConfig.method"
          :is-zh="isZh"
        />
      </div>

      <!-- Correlation Tab -->
      <div v-if="currentTab === 'correlation'" class="tab-pane active">
        <FactorCorrelationHeatmap
          :task-id="taskId"
          :method="correlationMethod"
          :is-zh="isZh"
        />
      </div>

      <!-- Distribution Tab -->
      <div v-if="currentTab === 'distribution'" class="tab-pane active">
        <FactorDistributionChart
          :task-id="taskId"
          :bins="distributionConfig.bins"
          :is-zh="isZh"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import ICIRTrendChart from '../ICIRTrendChart.vue'
import FactorCorrelationHeatmap from '../FactorCorrelationHeatmap.vue'
import FactorDistributionChart from '../FactorDistributionChart.vue'
import { useAppStore } from '@/stores/core/AppStore'

interface Props {
  taskId: string
  isZh: boolean
  currentStep: number
}

interface Emits {
  stepComplete: [data: any]
  dataUpdate: [data: any]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// Tabs
const currentTab = ref('overview')
const currentTabs = ref([
  { id: 'overview', name: 'Overview', nameZh: '概览' },
  { id: 'ic-ir', name: 'IC/IR Analysis', nameZh: 'IC/IR分析' },
  { id: 'correlation', name: 'Correlation', nameZh: '相关性' },
  { id: 'distribution', name: 'Distribution', nameZh: '分布' }
])

const switchTab = (tabId: string) => {
  currentTab.value = tabId
}

// 统计数据
const stats = reactive({
  totalFactors: 168,
  icMean: 0.045,
  irRatio: 0.78,
  qualifiedCount: 45,
  passRate: 26.8,
  progress: 67
})

// 顶部因子
const topFactors = ref([
  { factor_name: 'MA60_Cross_Price', ic: 0.058, ir: 0.92, t_stat: 3.45, p_value: 0.001, status: 'pass' },
  { factor_name: 'RSM60_Std_Dev', ic: 0.052, ir: 0.85, t_stat: 3.12, p_value: 0.002, status: 'pass' },
  { factor_name: 'ROC20_Return', ic: 0.049, ir: 0.78, t_stat: 2.89, p_value: 0.004, status: 'pass' },
  { factor_name: 'Beta60_Price', ic: 0.022, ir: 0.45, t_stat: 1.56, p_value: 0.12, status: 'fail' },
  { factor_name: 'VOL30_Volume', ic: 0.041, ir: 0.72, t_stat: 2.67, p_value: 0.008, status: 'pass' }
])

// IC/IR配置
const icConfig = reactive({
  method: 'spearman' as 'pearson' | 'spearman',
  threshold: 0.03,
  targetPeriod: 1,
  includeAlpha158: true,
  includeAlpha360: false,
  includeCustom: true
})

// 相关性配置
const correlationMethod = ref<'pearson' | 'spearman'>('pearson')

// 分布配置
const distributionConfig = reactive({
  histogram: true,
  qqPlot: true,
  boxPlot: false,
  bins: 50
})

// 因子库质量雷达图
const factorQualityRadarRef = ref<HTMLElement>()

// 因子库质量数据
const factorQualityData = computed(() => {
  const icScore = Math.min((stats.icMean / 0.05) * 80, 100)
  const irScore = Math.min((stats.irRatio / 0.8) * 80, 100)
  const passScore = Math.min(stats.passRate * 1.2, 100)
  const countScore = Math.min((stats.totalFactors / 200) * 80, 100)
  return [icScore, irScore, passScore, countScore]
})

// 因子库质量颜色
const getFactorQualityColor = (score: number) => {
  if (score > 100) return '#8b5cf6'
  if (score >= 80) return '#ef5350'
  if (score >= 60) return '#f97316'
  if (score >= 40) return '#2962ff'
  return '#26a69a'
}

// 行业基准数据
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

// 初始化雷达图
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
      right: 10,
      top: 'center',
      orient: 'vertical',
      textStyle: { color: '#d1d4dc' }
    },
    radar: {
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

// 监听tab切换
watch(currentTab, (newTab) => {
  if (newTab === 'overview') {
    radarInitRetry = 0
    nextTick(() => {
      setTimeout(() => initFactorQualityRadar(), 200)
    })
  }
})

onMounted(() => {
  if (currentTab.value === 'overview') {
    radarInitRetry = 0
    nextTick(() => {
      setTimeout(() => initFactorQualityRadar(), 200)
    })
  }
  window.addEventListener('resize', () => {
    if (currentTab.value === 'overview') {
      const container = document.querySelector('.radar-chart') as HTMLElement
      if (container) {
        const chart = echarts.getInstanceByDom(container)
        chart?.resize()
      }
    }
  })
})

// 操作方法
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
.step-factor-analysis-panel {
  /* CSS 变量定义 - 继承自父组件 */
  --bg-primary: #131722;
  --bg-secondary: #1e222d;
  --bg-tertiary: #2a2e39;
  --text-primary: #d1d4dc;
  --text-secondary: #787b86;
  --accent-blue: #2962ff;
  --color-up: #ef5350;
  --color-down: #26a69a;
  --accent-red: #ef5350;
  --accent-green: #26a69a;
  --accent-orange: #ff9800;
  --border-color: #2a2e39;

  width: 100%;
}

.content-tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.content-tab {
  padding: 10px 16px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  border-bottom: 2px solid transparent;
}

.content-tab:hover {
  color: var(--text-primary);
  background: transparent;
}

.content-tab.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
}

.tab-icon {
  width: 14px;
  height: 14px;
}

.tab-content {
  .tab-pane {
    animation: fadeIn 0.3s ease;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.radar-section {
  margin-bottom: 24px;
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
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.quality-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.quality-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quality-item-icon {
  width: 28px;
  height: 28px;
  color: var(--text-secondary);
}

.quality-item-label {
  min-width: 60px;
  font-size: 12px;
  color: var(--text-secondary);
}

.quality-item-score {
  min-width: 40px;
  font-size: 16px;
  font-weight: 700;
  text-align: right;
}

.quality-item-bar {
  flex: 1;
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.quality-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.quality-item-raw {
  min-width: 50px;
  font-size: 12px;
  color: var(--text-secondary);
  text-align: right;
}

.radar-chart-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.radar-chart {
  width: 100%;
  height: 300px;
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

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-bottom: 20px;

  thead {
    background: var(--bg-secondary);

    th {
      padding: 10px 12px;
      text-align: left;
      font-weight: 600;
      color: var(--text-secondary);
      border-bottom: 1px solid var(--border-color);
    }
  }

  tbody {
    tr {
      border-bottom: 1px solid var(--border-color);

      &:hover {
        background: var(--bg-secondary);
      }

      td {
        padding: 10px 12px;
        color: var(--text-primary);
      }
    }
  }

  .value {
    &.positive {
      color: var(--accent-red);
    }

    &.negative {
      color: var(--accent-green);
    }
  }
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
