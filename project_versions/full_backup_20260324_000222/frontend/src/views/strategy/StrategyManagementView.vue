<template>
  <div class="strategy-management">
    <GlobalNavBar />

    <!-- 三栏布局: 策略列表 | 详情 | 侧边栏 -->
    <div class="main-container">
      <!-- 左侧: 策略列表 -->
      <div class="panel strategy-list-panel">
        <div class="panel-header">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
          </svg>
          <span>{{ isZh ? '策略库' : 'Strategy Library' }}</span>
          <ActionButton type="primary" size="small" :icon="iconAdd" :label="isZh ? '新建' : 'New'" @click="createNewStrategy" />
        </div>
        <div class="strategy-list">
          <div
            v-for="strategy in strategies"
            :key="strategy.id"
            :class="['strategy-item', { selected: selectedStrategy?.id === strategy.id }]"
            @click="selectStrategy(strategy)"
          >
            <div class="strategy-header-row">
              <div class="strategy-name">
                <span :class="['strategy-status', strategy.status]"></span>
                {{ isZh ? strategy.name : strategy.nameEn }}
              </div>
              <div :class="['strategy-score', strategy.scoreClass]">
                <svg class="star-icon" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
                {{ strategy.score }}
              </div>
            </div>
            <div class="strategy-desc">{{ isZh ? strategy.description : strategy.descriptionEn }}</div>
            <div class="strategy-metrics">
              <div class="metric">
                <svg class="icon-sm rise" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                </svg>
                <span :class="['metric-value', strategy.return >= 0 ? 'positive' : 'negative']">
                  {{ strategy.return >= 0 ? '+' : '' }}{{ (strategy.return * 100).toFixed(1) }}%
                </span>
              </div>
              <div class="metric">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span class="metric-value">{{ strategy.sharpe }}</span>
              </div>
              <div class="metric">
                <svg class="icon-sm warn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M23 18l-9.5-9.5-5 5L1 6"></path>
                </svg>
                <span class="metric-value">{{ (strategy.maxDrawdown * 100).toFixed(1) }}%</span>
              </div>
            </div>
            <div class="strategy-stage">
              <span :class="['stage-tag', strategy.stage]">{{ getStageText(strategy.stage) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间: 策略详情 -->
      <div class="panel strategy-detail-panel">
        <div class="content-area" v-if="selectedStrategy">
          <div class="strategy-header">
            <div class="header-info">
              <h1 class="page-title">{{ isZh ? selectedStrategy.name : selectedStrategy.nameEn }}</h1>
              <p class="page-subtitle">{{ isZh ? selectedStrategy.description : selectedStrategy.descriptionEn }}</p>
            </div>
            <div class="strategy-actions">
              <ActionButton v-if="selectedStrategy.status !== 'active'" type="success" size="small" :icon="iconPlay" :label="isZh ? '启动' : 'Start'" @click="startStrategy" />
              <ActionButton v-if="selectedStrategy.status === 'active'" type="warning" size="small" :icon="iconPause" :label="isZh ? '暂停' : 'Pause'" @click="pauseStrategy" />
              <ActionButton type="default" size="small" icon-only :icon="iconEdit" :title="isZh ? '编辑' : 'Edit'" @click="editStrategy" />
              <ActionButton type="danger" size="small" icon-only :icon="iconDelete" :title="isZh ? '删除' : 'Delete'" @click="deleteStrategy" />
            </div>
          </div>

          <!-- 评分卡片 -->
          <div class="score-section" v-if="selectedStrategy">
            <ScoreBarChart
              :title="isZh ? '策略评分' : 'Strategy Score'"
              :score="selectedStrategy.score * 20"
              :grade="getScoreGrade(selectedStrategy.score)"
              :data="scoreBarData"
            />
          </div>

          <!-- 统计卡片 -->
          <div class="stats-grid">
            <SummaryCard
              :icon="iconReturn"
              :value="selectedStrategy.return >= 0 ? '+' + (selectedStrategy.return * 100).toFixed(1) + '%' : (selectedStrategy.return * 100).toFixed(1) + '%'"
              :label="isZh ? '总收益' : 'Total Return'"
              :subtitle="isZh ? '今年以来' : 'YTD'"
              icon-color="orange"
              :value-color="selectedStrategy.return >= 0 ? 'profit' : 'loss'"
            />
            <SummaryCard
              :icon="iconSharpe"
              :value="selectedStrategy.sharpe.toString()"
              :label="isZh ? '夏普比率' : 'Sharpe Ratio'"
              :subtitle="isZh ? '年化' : 'Annualized'"
              icon-color="blue"
              value-color="profit"
            />
            <SummaryCard
              :icon="iconDrawdown"
              :value="(selectedStrategy.maxDrawdown * 100).toFixed(1) + '%'"
              :label="isZh ? '最大回撤' : 'Max Drawdown'"
              :subtitle="isZh ? '历史最大' : 'Peak to Trough'"
              icon-color="green"
              value-color="loss"
            />
            <SummaryCard
              :icon="iconWinRate"
              :value="(selectedStrategy.winRate * 100).toFixed(1) + '%'"
              :label="isZh ? '胜率' : 'Win Rate'"
              :subtitle="isZh ? '近100笔交易' : 'Last 100 trades'"
              icon-color="orange"
            />
          </div>

          <!-- 图表行 -->
          <div class="charts-grid">
            <!-- 月度收益热力图 -->
            <ReturnStatsCard
              :title="isZh ? '收益统计' : 'Return Statistics'"
              :model-value="selectedPeriod"
              :chart-type="returnChartType"
              :grid-cols="heatmapCols"
              :heatmap-data="computedHeatmapData"
              @update:model-value="selectedPeriod = $event"
              @toggle-type="returnChartType = returnChartType === 'heatmap' ? 'bar' : 'heatmap'"
            >
              <!-- 3D柱状图视图 -->
              <template #barChart>
                <div ref="bar3DChartRef" class="bar-chart-3d-echarts"></div>
              </template>
            </ReturnStatsCard>

            <!-- 综合分析：因子权重+雷达+风险指标 -->
            <div class="analysis-card">
              <!-- 第一行：因子权重 + 性能雷达 -->
              <div class="analysis-row">
                <!-- 因子权重 -->
                <div class="analysis-left">
                  <DonutChart :title="isZh ? '因子权重' : 'Factor Weights'" :data="factorWeightsData" />
                </div>

                <!-- 性能雷达 -->
                <div class="analysis-right">
                  <PerformanceRadarCard :title="isZh ? '性能雷达' : 'Performance Radar'">
                    <RadarChart
                      :indicator="radarIndicator"
                      :data="radarData"
                      :benchmark="radarBenchmark"
                      color="#2962ff"
                    />
                  </PerformanceRadarCard>
                </div>
              </div>

              <!-- 第二行：风险指标对比 -->
              <div class="analysis-row full-width">
                <RiskMetricsCard
                  :title="isZh ? '风险指标对比' : 'Risk Metrics Comparison'"
                  :data="riskMetricsData"
                  :benchmark-label="isZh ? '基准' : 'Benchmark'"
                />
              </div>
            </div>
          </div>

          <!-- 净值曲线 -->
          <div class="chart-card performance-section">
            <TVLineChart
              v-if="selectedStrategy"
              :title="isZh ? '净值曲线 vs 基准' : 'Equity Curve vs Benchmark'"
              :strategy-data="equityChartData.strategyData"
              :benchmark-data="equityChartData.benchmarkData"
              :dates="equityChartData.dates"
              :strategy-label="equityChartData.strategyLabel"
              :benchmark-label="equityChartData.benchmarkLabel"
              :strategy-color="equityChartData.strategyColor"
              :benchmark-color="equityChartData.benchmarkColor"
              :show-period-selector="true"
              :resizable="true"
              :height="300"
              :locale="appStore.language"
            />
          </div>
        </div>

        <!-- 空状态 -->
        <div class="empty-state" v-else>
          <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          <p>选择一个策略查看详情</p>
          <button class="btn-primary" @click="createNewStrategy">创建新策略</button>
        </div>
      </div>

      <!-- 右侧: 详情面板 -->
      <div class="panel details-panel" v-if="selectedStrategy">
        <div class="panel-header">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <span>{{ isZh ? '策略详情' : 'Strategy Details' }}</span>
        </div>
        <div class="details-content">
          <div class="detail-group">
            <div class="detail-group-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              {{ isZh ? '状态' : 'Status' }}
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '运行状态' : 'Running Status' }}</span>
              <span :class="['detail-value', selectedStrategy.status]">{{ getStatusText(selectedStrategy.status) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '所属阶段' : 'Stage' }}</span>
              <span :class="['stage-tag', selectedStrategy.stage]">{{ getStageText(selectedStrategy.stage) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '创建时间' : 'Created' }}</span>
              <span class="detail-value">{{ selectedStrategy.createdAt }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '运行天数' : 'Running Days' }}</span>
              <span class="detail-value">{{ selectedStrategy.runningDays }} {{ isZh ? '天' : 'days' }}</span>
            </div>
          </div>

          <div class="detail-group">
            <div class="detail-group-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                <path d="M2 17l10 5 10-5"></path>
                <path d="M2 12l10 5 10-5"></path>
              </svg>
              {{ isZh ? '因子组成' : 'Factor Composition' }}
            </div>
            <div class="factor-list">
              <div class="factor-item" v-for="(factor, idx) in translatedFactors" :key="idx">
                <span class="factor-name">{{ factor.displayName }}</span>
                <span class="factor-weight">{{ factor.weight }}%</span>
              </div>
            </div>
          </div>

          <div class="detail-group">
            <div class="detail-group-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              {{ isZh ? '风险指标' : 'Risk Metrics' }}
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '年化波动率' : 'Ann. Volatility' }}</span>
              <span class="detail-value">{{ (selectedStrategy.volatility * 100).toFixed(1) }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? 'Sortino比率' : 'Sortino Ratio' }}</span>
              <span class="detail-value">{{ selectedStrategy.sortino }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? 'Calmar比率' : 'Calmar Ratio' }}</span>
              <span class="detail-value">{{ selectedStrategy.calmar.toFixed(2) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">VaR (95%)</span>
              <span class="detail-value">{{ (selectedStrategy.var95 * 100).toFixed(1) }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Beta</span>
              <span class="detail-value">{{ selectedStrategy.beta.toFixed(2) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Alpha</span>
              <span class="detail-value positive">+{{ (selectedStrategy.alpha * 100).toFixed(1) }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '信息比率' : 'Info Ratio' }}</span>
              <span class="detail-value">{{ selectedStrategy.infoRatio.toFixed(2) }}</span>
            </div>
          </div>

          <div class="detail-group">
            <div class="detail-group-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
              {{ isZh ? '交易统计' : 'Trading Stats' }}
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '总交易次数' : 'Total Trades' }}</span>
              <span class="detail-value">{{ selectedStrategy.totalTrades }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '平均持仓' : 'Avg Holding' }}</span>
              <span class="detail-value">{{ selectedStrategy.avgHoldDays }} {{ isZh ? '天' : 'days' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '换手率' : 'Turnover' }}</span>
              <span class="detail-value">{{ (selectedStrategy.turnover * 100).toFixed(0) }}{{ isZh ? '%/月' : '%/mo' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '当前持仓' : 'Positions' }}</span>
              <span class="detail-value">{{ selectedStrategy.currentPositions }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '交易成功率' : 'Win Rate' }}</span>
              <span class="detail-value positive">{{ (selectedStrategy.tradeSuccessRate * 100).toFixed(1) }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '盈利因子' : 'Profit Factor' }}</span>
              <span class="detail-value">{{ selectedStrategy.profitFactor.toFixed(2) }}</span>
            </div>
          </div>

          <div class="detail-group">
            <div class="detail-group-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
              </svg>
              {{ isZh ? '策略参数' : 'Strategy Params' }}
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '股票池' : 'Universe' }}</span>
              <span class="detail-value">{{ isZh ? selectedStrategy.universe : selectedStrategy.universeEn }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '调仓频率' : 'Rebalance' }}</span>
              <span class="detail-value">{{ isZh ? selectedStrategy.rebalance : selectedStrategy.rebalanceEn }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '最大持仓数' : 'Max Positions' }}</span>
              <span class="detail-value">{{ selectedStrategy.maxPositions }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '仓位分配' : 'Position Sizing' }}</span>
              <span class="detail-value">{{ isZh ? selectedStrategy.positionSizing : selectedStrategy.positionSizingEn }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '止损' : 'Stop Loss' }}</span>
              <span class="detail-value">{{ (selectedStrategy.stopLoss * 100).toFixed(0) }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '止盈' : 'Take Profit' }}</span>
              <span class="detail-value">{{ (selectedStrategy.takeProfit * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import GlobalNavBar from '@/components/GlobalNavBar.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
// 导入 echarts-gl 以支持 3D 图表
import 'echarts-gl'
import TVLineChart, { type Time } from '@/components/charts/TVLineChart.vue'
import DonutChart from '@/components/ui/charts/DonutChart.vue'
import RadarChart from '@/components/ui/charts/RadarChart.vue'
import PerformanceRadarCard from '@/components/ui/charts/PerformanceRadarCard.vue'
import ReturnStatsCard from '@/components/ui/charts/ReturnStatsCard.vue'
import RiskCompareCard from '@/components/ui/charts/RiskCompareCard.vue'
import RiskMetricsCard from '@/components/ui/charts/RiskMetricsCard.vue'
import ScoreBarChart from '@/components/ui/charts/ScoreBarChart.vue'
import HorizontalBarChart from '@/components/ui/charts/HorizontalBarChart.vue'
import SummaryCard from '@/components/ui/SummaryCard.vue'
import { ActionButton } from '@/components/ui'
import { useAppStore } from '@/stores/core/AppStore'

const router = useRouter()
const appStore = useAppStore()
const isZh = computed(() => appStore.language === 'zh')

// 雷达图数据
const radarIndicator = computed(() => [
  { name: isZh.value ? '收益' : 'Return', max: 100 },
  { name: isZh.value ? '夏普' : 'Sharpe', max: 100 },
  { name: isZh.value ? '稳定性' : 'Stability', max: 100 },
  { name: isZh.value ? '容量' : 'Capacity', max: 100 },
  { name: isZh.value ? '成本' : 'Cost', max: 100 },
  { name: isZh.value ? '回撤' : 'Drawdown', max: 100 }
])

const radarData = computed(() => {
  if (!selectedStrategy.value) return [85, 80, 75, 70, 65, 72]
  const s = selectedStrategy.value
  return [
    s.scoreDetails.return,
    s.scoreDetails.riskAdj,
    s.scoreDetails.stability,
    s.scoreDetails.capacity,
    Math.round(100 - (s.turnover * 100)),
    Math.round(100 + s.maxDrawdown * 200)
  ]
})

const radarBenchmark = computed(() => [70, 65, 60, 55, 50, 60])

// 图标常量
const iconPlay = '<svg viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>'
const iconPause = '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>'
const iconEdit = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>'
const iconDelete = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>'
const iconAdd = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>'

// SummaryCard 图标
const iconReturn = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
const iconSharpe = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"></path><path d="M2 17l10 5 10-5"></path><path d="M2 12l10 5 10-5"></path></svg>'
const iconDrawdown = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>'
const iconWinRate = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'

// 收益周期切换
type PeriodType = 'daily' | 'weekly' | 'monthly'
const selectedPeriod = ref<PeriodType>('monthly')

// 收益图表类型切换（热力图/柱状图）
type ReturnChartType = 'heatmap' | 'bar'
const returnChartType = ref<ReturnChartType>('heatmap')

const periodOptions = computed(() => [
  { value: 'daily', label: isZh.value ? '日' : 'Day' },
  { value: 'weekly', label: isZh.value ? '周' : 'Week' },
  { value: 'monthly', label: isZh.value ? '月' : 'Month' }
])

// 根据收益值计算颜色分类
const getReturnClass = (value: number): string => {
  if (value > 5) return 'high'
  if (value > 1) return 'medium-high'
  if (value > 0) return 'medium'
  if (value > -1) return 'medium-low'
  return 'low'
}

const getReturnsByPeriod = (strategy: Strategy) => {
  if (selectedPeriod.value === 'monthly') {
    // 月度数据也需要重新计算颜色分类
    return strategy.monthlyReturns.map(item => ({
      ...item,
      class: getReturnClass(item.value)
    }))
  }
  // 模拟周数据
  if (selectedPeriod.value === 'weekly') {
    return [
      { label: 'W1', value: 2.5, class: getReturnClass(2.5) },
      { label: 'W2', value: -1.2, class: getReturnClass(-1.2) },
      { label: 'W3', value: 3.8, class: getReturnClass(3.8) },
      { label: 'W4', value: 1.5, class: getReturnClass(1.5) },
    ]
  }
  // 日 - 获取当月实际天数
  const now = new Date()
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
  return Array.from({ length: daysInMonth }, (_, i) => {
    const value = parseFloat((Math.random() * 8 - 3).toFixed(1))
    return {
      label: `${i + 1}`,
      value,
      class: getReturnClass(value)
    }
  })
}

// 获取热力图列数
const heatmapCols = computed(() => {
  if (selectedPeriod.value === 'daily') return 7  // 7列日历
  if (selectedPeriod.value === 'weekly') return 4  // 4周
  return 4  // 月度 - 12个月 = 3x4
})

// 转换为组件需要的数据格式
const computedHeatmapData = computed(() => {
  const rawData = getReturnsByPeriod(selectedStrategy.value)
  return rawData.map(item => ({
    label: isZh.value ? item.label : getMonthLabelEn(item.label),
    value: item.value,
    class: item.class
  }))
})

// 将收益数据按行分组（用于3D柱状图）
const returnsRows = computed(() => {
  const data = getReturnsByPeriod(selectedStrategy.value)
  const cols = heatmapCols.value
  const rows: typeof data[] = []
  for (let i = 0; i < data.length; i += cols) {
    rows.push(data.slice(i, i + cols))
  }
  return rows
})

const currentNav = computed(() => 'strategy')

// 图表相关
const radarChartRef = ref<HTMLElement>()
let radarChartInstance: echarts.ECharts | null = null

// 3D柱状图相关
const bar3DChartRef = ref<HTMLElement>()
let bar3DChartInstance: echarts.ECharts | null = null

const goTo = (path: string) => {
  router.push(path)
}

const toggleLanguage = () => {
  appStore.setLanguage(isZh.value ? 'en' : 'zh')
}

const showNotifications = () => {
  ElMessage.info(isZh.value ? '暂无新通知' : 'No new notifications')
}

interface Strategy {
  id: string
  name: string
  nameEn: string
  description: string
  descriptionEn: string
  status: 'active' | 'paused' | 'stopped'
  stage: 'research' | 'validation' | 'production'
  score: number
  scoreClass: string
  return: number
  sharpe: number
  maxDrawdown: number
  winRate: number
  createdAt: string
  runningDays: number
  scoreDetails: { return: number; riskAdj: number; stability: number; capacity: number }
  factorWeights: number[]
  factors: { name: string; nameEn: string; weight: number }[]
  monthlyReturns: { label: string; value: number; class: string }[]
  volatility: number
  sortino: number
  calmar: number
  var95: number
  beta: number
  alpha: number
  infoRatio: number
  totalTrades: number
  avgHoldDays: number
  turnover: number
  currentPositions: number
  tradeSuccessRate: number
  profitFactor: number
  universe: string
  universeEn: string
  rebalance: string
  rebalanceEn: string
  maxPositions: number
  positionSizing: string
  positionSizingEn: string
  stopLoss: number
  takeProfit: number
  // 净值曲线数据
  equityData: number[]
  benchmarkData: number[]
  xAxisLabels: string[]
}

// [生产环境] 策略列表应从后端获取 - GET /api/v1/strategies
// 当前为演示数据，各阶段生成的策略都会保存在这里
const strategies = ref<Strategy[]>([
  {
    id: '1',
    name: '多因子Alpha策略 v1.0',
    nameEn: 'Multi-Factor Alpha Strategy v1.0',
    description: '基于动量和价值因子的多因子选股策略',
    descriptionEn: 'Multi-factor stock selection strategy based on momentum and value factors',
    status: 'active',
    stage: 'production',
    score: 4.8,
    scoreClass: 'excellent',
    return: 0.152,
    sharpe: 1.8,
    maxDrawdown: -0.085,
    winRate: 0.625,
    createdAt: '2024-01-15',
    runningDays: 27,
    scoreDetails: { return: 92, riskAdj: 88, stability: 85, capacity: 78 },
    factorWeights: [35, 25, 20],
    factors: [
      { name: '动量因子', nameEn: 'Momentum', weight: 35 },
      { name: '价值因子(PE)', nameEn: 'Value (PE)', weight: 25 },
      { name: '质量因子(ROE)', nameEn: 'Quality (ROE)', weight: 20 }
    ],
    monthlyReturns: [
      { label: '1月', value: 5.2, class: 'high' },
      { label: '2月', value: 3.1, class: 'medium-high' },
      { label: '3月', value: 1.8, class: 'medium' },
      { label: '4月', value: 4.5, class: 'high' },
      { label: '5月', value: -0.5, class: 'low' },
      { label: '6月', value: 2.8, class: 'medium-high' },
      { label: '7月', value: 1.2, class: 'medium' },
      { label: '8月', value: 3.6, class: 'medium-high' },
      { label: '9月', value: 2.1, class: 'medium' },
      { label: '10月', value: -1.5, class: 'low' },
      { label: '11月', value: 4.2, class: 'high' },
      { label: '12月', value: 3.8, class: 'medium-high' }
    ],
    volatility: 0.125,
    sortino: 2.3,
    calmar: 1.8,
    var95: 0.021,
    beta: 0.68,
    alpha: 0.072,
    infoRatio: 1.45,
    totalTrades: 1245,
    avgHoldDays: 12,
    turnover: 0.45,
    currentPositions: 42,
    tradeSuccessRate: 0.625,
    profitFactor: 1.85,
    universe: '中证800',
    universeEn: 'CSI 800',
    rebalance: '每周',
    rebalanceEn: 'Weekly',
    maxPositions: 50,
    positionSizing: '等权',
    positionSizingEn: 'Equal Weight',
    stopLoss: 0.05,
    takeProfit: 0.15,
    // 净值曲线数据
    equityData: [1.00, 1.012, 1.025, 1.048, 1.062, 1.078, 1.095, 1.108, 1.122, 1.135, 1.148, 1.152],
    benchmarkData: [1.00, 1.008, 1.015, 1.022, 1.018, 1.025, 1.032, 1.028, 1.035, 1.040, 1.043, 1.045],
    xAxisLabels: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  },
  {
    id: '2',
    name: '动量轮动策略 v2.0',
    nameEn: 'Momentum Rotation Strategy v2.0',
    description: '基于动量指标的板块轮动策略',
    descriptionEn: 'Sector rotation strategy based on momentum indicators',
    status: 'active',
    stage: 'validation',
    score: 4.6,
    scoreClass: 'excellent',
    return: 0.228,
    sharpe: 2.1,
    maxDrawdown: -0.123,
    winRate: 0.58,
    createdAt: '2024-02-01',
    runningDays: 15,
    scoreDetails: { return: 95, riskAdj: 82, stability: 78, capacity: 85 },
    factorWeights: [50, 30, 20],
    factors: [
      { name: '动量因子', nameEn: 'Momentum', weight: 50 },
      { name: '波动率因子', nameEn: 'Volatility', weight: 30 },
      { name: '流动性因子', nameEn: 'Liquidity', weight: 20 }
    ],
    monthlyReturns: [
      { label: '1月', value: 6.8, class: 'high' },
      { label: '2月', value: 4.2, class: 'medium-high' },
      { label: '3月', value: 2.5, class: 'medium' },
      { label: '4月', value: 5.1, class: 'high' },
      { label: '5月', value: 1.2, class: 'medium' },
      { label: '6月', value: 3.8, class: 'medium-high' },
      { label: '7月', value: -1.5, class: 'low' },
      { label: '8月', value: 4.5, class: 'high' },
      { label: '9月', value: 2.8, class: 'medium-high' },
      { label: '10月', value: 1.5, class: 'medium' },
      { label: '11月', value: 3.2, class: 'medium-high' },
      { label: '12月', value: 5.5, class: 'high' }
    ],
    volatility: 0.165,
    sortino: 2.8,
    calmar: 1.85,
    var95: 0.028,
    beta: 1.05,
    alpha: 0.095,
    infoRatio: 1.32,
    totalTrades: 856,
    avgHoldDays: 8,
    turnover: 0.72,
    currentPositions: 28,
    tradeSuccessRate: 0.58,
    profitFactor: 1.72,
    universe: '沪深300',
    universeEn: 'CSI 300',
    rebalance: '每两周',
    rebalanceEn: 'Bi-weekly',
    maxPositions: 30,
    positionSizing: '等权',
    positionSizingEn: 'Equal Weight',
    stopLoss: 0.08,
    takeProfit: 0.12,
    // 净值曲线数据
    equityData: [1.00, 1.035, 1.072, 1.088, 1.125, 1.142, 1.165, 1.138, 1.168, 1.195, 1.212, 1.228],
    benchmarkData: [1.00, 1.012, 1.025, 1.035, 1.042, 1.048, 1.055, 1.045, 1.052, 1.058, 1.062, 1.068],
    xAxisLabels: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  },
  {
    id: '3',
    name: '均值回归配对策略',
    nameEn: 'Mean Reversion Pairs Strategy',
    description: '统计套利配对交易策略',
    descriptionEn: 'Statistical arbitrage pairs trading strategy',
    status: 'paused',
    stage: 'validation',
    score: 4.2,
    scoreClass: 'good',
    return: 0.085,
    sharpe: 1.5,
    maxDrawdown: -0.042,
    winRate: 0.65,
    createdAt: '2024-01-20',
    runningDays: 10,
    scoreDetails: { return: 72, riskAdj: 85, stability: 90, capacity: 65 },
    factorWeights: [40, 35, 25],
    factors: [
      { name: '协整因子', nameEn: 'Cointegration', weight: 40 },
      { name: '价差因子', nameEn: 'Spread', weight: 35 },
      { name: '相关性因子', nameEn: 'Correlation', weight: 25 }
    ],
    monthlyReturns: [
      { label: '1月', value: 1.8, class: 'medium' },
      { label: '2月', value: 2.2, class: 'medium-high' },
      { label: '3月', value: 1.5, class: 'medium' },
      { label: '4月', value: 2.8, class: 'medium-high' },
      { label: '5月', value: 0.8, class: 'medium-low' },
      { label: '6月', value: 1.2, class: 'medium' },
      { label: '7月', value: 2.5, class: 'medium-high' },
      { label: '8月', value: 1.1, class: 'medium' },
      { label: '9月', value: 1.8, class: 'medium' },
      { label: '10月', value: 2.0, class: 'medium-high' },
      { label: '11月', value: 1.5, class: 'medium' },
      { label: '12月', value: 2.2, class: 'medium-high' }
    ],
    volatility: 0.085,
    sortino: 2.1,
    calmar: 2.0,
    var95: 0.012,
    beta: 0.15,
    alpha: 0.068,
    infoRatio: 0.95,
    totalTrades: 2340,
    avgHoldDays: 3,
    turnover: 1.5,
    currentPositions: 18,
    tradeSuccessRate: 0.65,
    profitFactor: 2.1,
    universe: '全A股',
    universeEn: 'All A-Shares',
    rebalance: '每日',
    rebalanceEn: 'Daily',
    maxPositions: 20,
    positionSizing: '等权',
    positionSizingEn: 'Equal Weight',
    stopLoss: 0.03,
    takeProfit: 0.05,
    // 净值曲线数据
    equityData: [1.00, 1.008, 1.018, 1.025, 1.035, 1.042, 1.052, 1.062, 1.070, 1.078, 1.082, 1.085],
    benchmarkData: [1.00, 1.010, 1.022, 1.028, 1.038, 1.042, 1.052, 1.045, 1.052, 1.058, 1.062, 1.068],
    xAxisLabels: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  },
  {
    id: '4',
    name: '机器学习预测策略',
    nameEn: 'Machine Learning Prediction Strategy',
    description: '基于GRU模型的股价预测策略',
    descriptionEn: 'Stock price prediction strategy based on GRU model',
    status: 'stopped',
    stage: 'research',
    score: 3.2,
    scoreClass: 'average',
    return: -0.035,
    sharpe: 0.8,
    maxDrawdown: -0.156,
    winRate: 0.52,
    createdAt: '2024-02-10',
    runningDays: 0,
    scoreDetails: { return: 45, riskAdj: 55, stability: 60, capacity: 70 },
    factorWeights: [100],
    factors: [
      { name: 'GRU模型预测', nameEn: 'GRU Model Prediction', weight: 100 }
    ],
    monthlyReturns: [
      { label: '1月', value: -1.2, class: 'low' },
      { label: '2月', value: 0.8, class: 'medium-low' },
      { label: '3月', value: -0.5, class: 'low' },
      { label: '4月', value: 1.5, class: 'medium' },
      { label: '5月', value: -2.1, class: 'low' },
      { label: '6月', value: 0.2, class: 'medium-low' },
      { label: '7月', value: -0.8, class: 'low' },
      { label: '8月', value: 0.5, class: 'medium-low' },
      { label: '9月', value: -1.5, class: 'low' },
      { label: '10月', value: 0.3, class: 'medium-low' },
      { label: '11月', value: -0.2, class: 'low' },
      { label: '12月', value: 1.2, class: 'medium' }
    ],
    volatility: 0.22,
    sortino: 1.1,
    calmar: -0.2,
    var95: 0.035,
    beta: 1.25,
    alpha: -0.025,
    infoRatio: -0.3,
    totalTrades: 456,
    avgHoldDays: 5,
    turnover: 0.85,
    currentPositions: 0,
    tradeSuccessRate: 0.52,
    profitFactor: 0.92,
    universe: '中证500',
    universeEn: 'CSI 500',
    rebalance: '每日',
    rebalanceEn: 'Daily',
    maxPositions: 40,
    positionSizing: '等权',
    positionSizingEn: 'Equal Weight',
    stopLoss: 0.1,
    takeProfit: 0.2,
    // 净值曲线数据
    equityData: [1.00, 0.988, 0.995, 0.982, 0.978, 0.965, 0.972, 0.968, 0.975, 0.968, 0.970, 0.965],
    benchmarkData: [1.00, 1.008, 1.015, 1.022, 1.018, 1.025, 1.032, 1.028, 1.035, 1.040, 1.043, 1.045],
    xAxisLabels: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  }
])

const selectedStrategy = ref<Strategy | null>(null)

// 因子权重计算
const factorWeightsSafe = computed(() => {
  if (!selectedStrategy.value) return { w1: 0, w2: 0, w3: 0, w4: 0 }
  const w = selectedStrategy.value.factorWeights
  const w1 = w[0] || 0
  const w2 = w[1] || 0
  const w3 = w[2] || 0
  const w4 = Math.max(0, 100 - w1 - w2 - w3)
  return { w1, w2, w3, w4 }
})

// 因子权重数据 - 供DonutChart使用
const factorWeightsData = computed(() => [
  { name: isZh.value ? '动量' : 'Momentum', value: factorWeightsSafe.value.w1 },
  { name: isZh.value ? '价值' : 'Value', value: factorWeightsSafe.value.w2 },
  { name: isZh.value ? '质量' : 'Quality', value: factorWeightsSafe.value.w3 },
  { name: isZh.value ? '低波动' : 'Low Vol', value: factorWeightsSafe.value.w4 }
])

// 因子名称翻译
const translatedFactors = computed(() => {
  if (!selectedStrategy.value) return []
  const factorMap: Record<string, { zh: string; en: string }> = {
    '动量因子': { zh: '动量因子', en: 'Momentum' },
    '波动率因子': { zh: '波动率因子', en: 'Volatility' },
    '流动性因子': { zh: '流动性因子', en: 'Liquidity' },
    '价值因子': { zh: '价值因子', en: 'Value' },
    '质量因子': { zh: '质量因子', en: 'Quality' },
    '价值因子(PE)': { zh: '价值因子(PE)', en: 'Value (PE)' },
    '质量因子(ROE)': { zh: '质量因子(ROE)', en: 'Quality (ROE)' },
    '协整因子': { zh: '协整因子', en: 'Cointegration' },
    '价差因子': { zh: '价差因子', en: 'Spread' },
    '相关性因子': { zh: '相关性因子', en: 'Correlation' },
    'GRU模型预测': { zh: 'GRU模型预测', en: 'GRU Model Prediction' }
  }
  return selectedStrategy.value.factors.map(f => ({
    ...f,
    displayName: factorMap[f.name] ? (isZh.value ? factorMap[f.name].zh : factorMap[f.name].en) : f.name
  }))
})

// 风险指标条形宽度计算
const riskBarWidths = computed(() => {
  if (!selectedStrategy.value) return { volatility: '0%', maxDrawdown: '0%' }
  const vol = selectedStrategy.value.volatility || 0
  const dd = Math.abs(selectedStrategy.value.maxDrawdown || 0)
  return {
    volatility: Math.min(vol * 800, 100) + '%',
    maxDrawdown: Math.min(dd * 500, 100) + '%'
  }
})

// 策略评分数据
const scoreBarData = computed(() => {
  if (!selectedStrategy.value) return []
  return [
    { name: isZh.value ? '收益' : 'Return', value: selectedStrategy.value.scoreDetails.return, color: 'red' },
    { name: isZh.value ? '风险调整' : 'Risk Adj', value: selectedStrategy.value.scoreDetails.riskAdj, color: 'blue' },
    { name: isZh.value ? '稳定性' : 'Stability', value: selectedStrategy.value.scoreDetails.stability, color: 'purple' },
    { name: isZh.value ? '容量' : 'Capacity', value: selectedStrategy.value.scoreDetails.capacity, color: 'cyan' }
  ]
})

// 风险指标对比数据
const riskMetricsData = computed(() => {
  if (!selectedStrategy.value) return []
  return [
    {
      name: isZh.value ? '波动率' : 'Volatility',
      value: selectedStrategy.value.volatility * 100,
      benchmark: 17.2,
      max: 25,
      color: '#2962ff',
      higherIsBetter: false
    },
    {
      name: isZh.value ? '最大回撤' : 'Max Drawdown',
      value: Math.abs(selectedStrategy.value.maxDrawdown * 100),
      benchmark: 15.8,
      max: 25,
      color: '#ff9800',
      higherIsBetter: false
    }
  ]
})

// 净值曲线图数据 - 适配TradingView组件
const equityChartData = computed(() => {
  if (!selectedStrategy.value) {
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

  const strategy = selectedStrategy.value
  const strategyReturn = parseFloat(((strategy.equityData[strategy.equityData.length - 1] - 1) * 100).toFixed(1))
  const benchmarkReturn = parseFloat(((strategy.benchmarkData[strategy.benchmarkData.length - 1] - 1) * 100).toFixed(1))

  // 红涨绿跌 - 正收益用红色，负收益用绿色
  const strategyColor = strategyReturn >= 0 ? '#ef5350' : '#26a69a'
  const strategyPrefix = strategyReturn >= 0 ? '+' : ''
  const benchmarkPrefix = benchmarkReturn >= 0 ? '+' : ''

  // 转换数据格式 - 使用日期字符串格式 (YYYY-MM-DD)
  const generateDates = (count: number): string[] => {
    const dates: string[] = []
    const today = new Date()
    for (let i = count - 1; i >= 0; i--) {
      const date = new Date(today)
      date.setMonth(date.getMonth() - i)
      dates.push(date.toISOString().split('T')[0])
    }
    return dates
  }

  const dates = generateDates(strategy.equityData.length)

  const strategyData = strategy.equityData.map((value, index) => ({
    time: dates[index] as Time,
    value: value
  }))

  const benchmarkData = strategy.benchmarkData.map((value, index) => ({
    time: dates[index] as Time,
    value: value
  }))

  return {
    strategyData,
    benchmarkData,
    dates: strategy.xAxisLabels || [],
    strategyLabel: isZh.value ? `策略 (${strategyPrefix}${strategyReturn}%)` : `Strategy (${strategyPrefix}${strategyReturn}%)`,
    benchmarkLabel: isZh.value ? `基准 (${benchmarkPrefix}${benchmarkReturn}%)` : `Benchmark (${benchmarkPrefix}${benchmarkReturn}%)`,
    strategyColor,
    benchmarkColor: '#787b86'
  }
})

const selectStrategy = (strategy: Strategy) => {
  selectedStrategy.value = strategy
}

const createNewStrategy = () => {
  router.push('/research/detail')
}

const startStrategy = () => {
  if (selectedStrategy.value) {
    selectedStrategy.value.status = 'active'
    ElMessage.success('策略已启动')
  }
}

const pauseStrategy = () => {
  if (selectedStrategy.value) {
    selectedStrategy.value.status = 'paused'
    ElMessage.success('策略已暂停')
  }
}

const editStrategy = () => {
  if (selectedStrategy.value) {
    router.push(`/research/detail?id=${selectedStrategy.value.id}`)
  }
}

const deleteStrategy = async () => {
  if (!selectedStrategy.value) return
  try {
    await ElMessageBox.confirm('确定要删除这个策略吗？', '确认删除', { type: 'warning' })
    const idx = strategies.value.findIndex(s => s.id === selectedStrategy.value!.id)
    if (idx > -1) {
      strategies.value.splice(idx, 1)
      selectedStrategy.value = null
      ElMessage.success('策略已删除')
    }
  } catch {}
}

const getStatusText = (status: string) => {
  const mapZh: Record<string, string> = { active: '运行中', paused: '已暂停', stopped: '已停止' }
  const mapEn: Record<string, string> = { active: 'Running', paused: 'Paused', stopped: 'Stopped' }
  return isZh.value ? (mapZh[status] || status) : (mapEn[status] || status)
}

const getStageText = (stage: string) => {
  const mapZh: Record<string, string> = { research: '研究', validation: '验证', production: '生产' }
  const mapEn: Record<string, string> = { research: 'Research', validation: 'Validation', production: 'Production' }
  return isZh.value ? (mapZh[stage] || stage) : (mapEn[stage] || stage)
}

const getMonthLabelEn = (label: string) => {
  const map: Record<string, string> = { '1月': 'Jan', '2月': 'Feb', '3月': 'Mar', '4月': 'Apr', '5月': 'May', '6月': 'Jun', '7月': 'Jul', '8月': 'Aug', '9月': 'Sep', '10月': 'Oct', '11月': 'Nov', '12月': 'Dec' }
  return map[label] || label
}

const getScoreGrade = (score: number) => {
  if (score >= 4.5) return 'A+'
  if (score >= 4.0) return 'A'
  if (score >= 3.5) return 'B+'
  if (score >= 3.0) return 'B'
  return 'C'
}

// 深色主题配色
const darkTheme = {
  background: '#1e222d',
  text: '#d1d4dc',
  textSecondary: '#787b86',
  border: '#2a2e39',
  up: '#ef5350',
  down: '#26a69a',
  accent: '#2962ff',
  benchmark: '#787b86'
}

// 渲染雷达图
const renderRadarChart = () => {
  if (!radarChartRef.value || !selectedStrategy.value) return

  if (!radarChartInstance) {
    radarChartInstance = echarts.init(radarChartRef.value, 'dark')
  }

  const strategy = selectedStrategy.value
  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: darkTheme.background,
      borderColor: darkTheme.border,
      textStyle: { color: darkTheme.text }
    },
    radar: {
      indicator: [
        { name: isZh.value ? '收益' : 'Return', max: 100 },
        { name: isZh.value ? '夏普' : 'Sharpe', max: 100 },
        { name: isZh.value ? '稳定性' : 'Stability', max: 100 },
        { name: isZh.value ? '容量' : 'Capacity', max: 100 },
        { name: isZh.value ? '成本' : 'Cost', max: 100 },
        { name: isZh.value ? '回撤' : 'Drawdown', max: 100 }
      ],
      center: ['50%', '55%'],
      axisNameGap: 0,
      axisName: {
        color: darkTheme.textSecondary,
        fontSize: 12
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(42, 46, 57, 0.2)', 'rgba(42, 46, 57, 0.4)']
        }
      },
      axisLine: {
        lineStyle: { color: darkTheme.border }
      },
      splitLine: {
        lineStyle: { color: darkTheme.border }
      }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [
              strategy.scoreDetails.return,
              strategy.scoreDetails.riskAdj,
              strategy.scoreDetails.stability,
              strategy.scoreDetails.capacity,
              Math.round(100 - (strategy.turnover * 100)),
              Math.round(100 + strategy.maxDrawdown * 200)
            ],
            name: '策略评分',
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: { color: darkTheme.up },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(239, 83, 80, 0.3)' },
                { offset: 1, color: 'rgba(239, 83, 80, 0.1)' }
              ])
            },
            lineStyle: { color: darkTheme.up, width: 2 }
          }
        ]
      }
    ]
  }

  radarChartInstance.setOption(option)
}

// 渲染3D柱状图
const renderBar3DChart = () => {
  if (!bar3DChartRef.value || !selectedStrategy.value) {
    console.log('bar3DChartRef or selectedStrategy is null')
    return
  }

  // 检查容器尺寸
  const rect = bar3DChartRef.value.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) {
    console.log('Container has zero size, retrying...')
    setTimeout(() => renderBar3DChart(), 100)
    return
  }

  if (!bar3DChartInstance) {
    bar3DChartInstance = echarts.init(bar3DChartRef.value, 'dark')
  }

  const data = getReturnsByPeriod(selectedStrategy.value)
  const rows = returnsRows.value

  // 根据周期类型动态调整参数
  const rowCount = rows.length
  const colCount = rows[0]?.length || 1

  // 动态计算图表尺寸和柱体大小
  let boxWidth: number, boxDepth: number, barSize: number, showLabel: boolean, distance: number
  if (selectedPeriod.value === 'daily') {
    // 日数据：7列 x 4-5行，数据多，柱体小，不显示标签
    boxWidth = 80
    boxDepth = 120
    barSize = 10
    showLabel = false
    distance = 120
  } else if (selectedPeriod.value === 'weekly') {
    // 周数据：4列 x 1行，柱体比例和月一致
    boxWidth = 60
    boxDepth = 100
    barSize = 14
    showLabel = true
    distance = 100
  } else {
    // 月数据：4列 x 3行
    boxWidth = 60
    boxDepth = 100
    barSize = 12
    showLabel = true
    distance = 100
  }

  // 颜色映射
  const colorMap: Record<string, string> = {
    'high': '#9c27b0',        // 紫色
    'medium-high': '#ef5350', // 红色
    'medium': '#ff9800',      // 橙色
    'medium-low': '#2962ff',  // 蓝色
    'low': '#4caf50'          // 绿色
  }

  // 构建3D柱状图数据 - 交换行列以匹配热力图布局
  const bar3DData: { value: [number, number, number], originalValue: number, label: string }[] = []
  const itemColors: string[] = []

  rows.forEach((row, rowIndex) => {
    row.forEach((item, colIndex) => {
      // 交换 x 和 y 坐标，负数值保持负数以便向下延伸
      bar3DData.push({
        value: [rowIndex, colIndex, item.value],
        originalValue: item.value,
        label: item.label
      })
      itemColors.push(colorMap[item.class] || '#2962ff')
    })
  })

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: darkTheme.background,
      borderColor: darkTheme.border,
      textStyle: { color: darkTheme.text },
      formatter: (params: unknown) => {
        const p = params as { data: { value: [number, number, number], originalValue: number } }
        const [row, col] = p.data.value
        const rowData = rows[row]
        const item = rowData?.[col]
        if (item) {
          return `${item.label}<br/>${isZh.value ? '收益率' : 'Return'}: ${item.value}%`
        }
        return ''
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
      data: rows.map((_, i) => `${i + 1}`) || [],
      axisLabel: { show: false },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { show: false },
      axisPointer: { show: false }
    },
    yAxis3D: {
      type: 'category',
      data: rows[0]?.map((_, i) => `${i + 1}`) || [],
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
      boxWidth: boxWidth,
      boxHeight: 60,
      boxDepth: boxDepth,
      viewControl: {
        autoRotate: false,
        distance: distance,
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
        type: 'bar3D' as const,
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
        barSize: barSize,
        bevelSize: 0,
        label: {
          show: showLabel,
          distance: 2,
          formatter: function(params: unknown) {
            const p = params as { data: { monthLabel: string, originalValue: number } }
            const val = p.data.originalValue
            const label = isZh.value ? p.data.monthLabel : getMonthLabelEn(p.data.monthLabel)
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

  bar3DChartInstance.setOption(option, true)
  setTimeout(() => bar3DChartInstance?.resize(), 50)
}

// 窗口大小变化
const handleResize = () => {
  radarChartInstance?.resize()
  bar3DChartInstance?.resize()
}

// 监听选中策略变化
watch(selectedStrategy, () => {
  setTimeout(() => {
    renderRadarChart()
    if (returnChartType.value === 'bar') {
      renderBar3DChart()
    }
  }, 0)
})

// 监听语言变化
watch(isZh, () => {
  setTimeout(() => {
    renderRadarChart()
    if (returnChartType.value === 'bar') {
      renderBar3DChart()
    }
  }, 0)
})

// 监听图表类型切换
watch(returnChartType, (newType, oldType) => {
  if (oldType === 'bar') {
    // 离开柱状图视图时销毁实例
    bar3DChartInstance?.dispose()
    bar3DChartInstance = null
  }
  if (newType === 'bar') {
    nextTick(() => {
      setTimeout(() => {
        renderBar3DChart()
      }, 100)
    })
  }
})

// 监听周期切换
watch(selectedPeriod, () => {
  if (returnChartType.value === 'bar') {
    nextTick(() => {
      setTimeout(() => {
        renderBar3DChart()
      }, 50)
    })
  }
})

// 默认选中第一个
if (strategies.value.length > 0) {
  selectedStrategy.value = strategies.value[0]
}

// 生命周期钩子
onMounted(() => {
  nextTick(() => {
    renderRadarChart()
  })
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  radarChartInstance?.dispose()
  bar3DChartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.strategy-management {
  height: 100vh;
  background: var(--bg-primary, #131722);
  color: var(--text-primary, #d1d4dc);
  font-size: 13px;
  display: flex;
  flex-direction: column;
}

// 顶部导航栏
.main-container {
  display: grid;
  grid-template-columns: 300px 1fr 320px;
  height: calc(100vh - 56px);
  gap: 1px;
  background: var(--border-color, #2a2e39);
}

.panel {
  background: var(--bg-primary, #131722);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  background: var(--bg-secondary, #1e222d);
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color, #2a2e39);
}

// 策略列表
.strategy-list {
  flex: 1;
  overflow-y: auto;
}

.strategy-item {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color, #2a2e39);
  cursor: pointer;
  transition: background 0.15s;

  &:hover { background: var(--bg-secondary, #1e222d); }
  &.selected {
    background: var(--bg-tertiary, #2a2e39);
    border-left: 2px solid var(--accent-blue, #2962ff);
  }
}

.strategy-header-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.strategy-name {
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.strategy-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  &.active { background: #26a69a; box-shadow: 0 0 6px #26a69a; }
  &.paused { background: #ff9800; }
  &.stopped { background: #787b86; }
}

.strategy-score {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 700;
  &.excellent { color: #9c27b0; }
  &.good { color: #ef5350; }
  &.average { color: #ff9800; }
  &.poor { color: #26a69a; }
}

.star-icon { width: 12px; height: 12px; }

.strategy-desc {
  font-size: 11px;
  color: var(--text-secondary, #cbd5e1);
  margin-bottom: 8px;
}

.strategy-metrics {
  display: flex;
  gap: 12px;
  font-size: 11px;
  .metric {
    display: flex;
    align-items: center;
    gap: 3px;
  }
  .metric-value {
    font-weight: 600;
    &.positive { color: #ef5350; }
    &.negative { color: #26a69a; }
  }
}

.strategy-stage {
  margin-top: 8px;
}

.stage-tag {
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  &.research { background: rgba(41, 98, 255, 0.2); color: #2962ff; }
  &.validation { background: rgba(255, 152, 0, 0.2); color: #ff9800; }
  &.production { background: rgba(38, 166, 154, 0.2); color: #26a69a; }
}

.icon-sm { width: 14px; height: 14px; }
.icon-md { width: 16px; height: 16px; }
.icon-xs { width: 12px; height: 12px; }
.rise { color: #ef5350; }
.warn { color: #ff9800; }

// 详情面板
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color, #2a2e39);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-secondary, #cbd5e1);
  margin: 0;
}

.strategy-actions {
  display: flex;
  gap: 6px;
  align-items: center;
}

// 评分卡片区域
.score-section {
  margin-bottom: 24px;
}

// 统计卡片
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 6px;
  padding: 16px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 3px;
    height: 100%;
    background: var(--accent-blue, #2962ff);
  }
  &.success::before { background: #ef5350; }
  &.warning::before { background: #26a69a; }

  .stat-label {
    font-size: 11px;
    color: var(--text-secondary, #787b86);
    margin-bottom: 8px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .stat-value { font-size: 20px; font-weight: 700; &.positive { color: #ef5350; } &.negative { color: #26a69a; } }
  .stat-sub { font-size: 11px; color: var(--text-secondary, #787b86); margin-top: 4px; }
}

// 图表网格
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.chart-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 20px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.bar-chart-3d-echarts {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

.chart-header {
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
  position: relative;
  z-index: 1;

  .icon-md {
    width: 18px;
    height: 18px;
  }
}

// 周期切换
.period-toggle {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

// 图表类型切换按钮
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

  .icon-sm {
    width: 14px;
    height: 14px;
  }
}

// 综合分析卡片 2+1布局
.analysis-card {
  .analysis-row {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    flex-wrap: wrap;

    &.full-width {
      width: 100%;
    }

    &:last-child {
      margin-bottom: 0;
    }
  }

  .analysis-left {
    flex: 1;
    min-width: 250px;
  }

  .analysis-right {
    flex: 1;
    min-width: 300px;
  }

  .risk-card {
    width: 100%;
  }
}

.period-btn {
  padding: 2px 8px;
  font-size: 11px;
  border: 1px solid var(--border-color, #2a2e39);
  background: transparent;
  color: var(--text-secondary, #787b86);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--bg-tertiary, #2a2e39);
  }

  &.active {
    background: var(--accent-blue, #2962ff);
    border-color: var(--accent-blue, #2962ff);
    color: white;
  }
}

// 环形图 - 垂直排列避免遮挡
.donut-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.donut-legend {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  white-space: nowrap;
}

// SVG饼图 - 自适应容器
.donut-chart svg {
  width: 100%;
  max-width: 80px;
  height: auto;
  aspect-ratio: 1;
}

.donut-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  &.blue { background: #2962ff; }
  &.green { background: #26a69a; }
  &.purple { background: #9c27b0; }
  &.orange { background: #ff9800; }
}

// 净值曲线
.performance-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;

  h4 {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary, #d1d4dc);
    margin: 0;
  }
}

.equity-chart {
  width: 100%;
  height: clamp(280px, 35vh, 450px);
  background: transparent;
  border-radius: 8px;
  position: relative;

  // 调整手柄
  &::after {
    content: '';
    position: absolute;
    bottom: -12px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 4px;
    background: transparent;
    cursor: ns-resize;
    opacity: 0.3;
    border-radius: 2px;

    &::before {
      content: '';
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      width: 30px;
      height: 3px;
      background: var(--text-secondary, #787b86);
      border-radius: 2px;
    }
  }
}

// 雷达图
.radar-chart {
  width: 100%;
  height: 180px;
}

// 水平条形图
.h-bar-chart {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 28px;
}

.h-bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.h-bar-label {
  min-width: 55px;
  font-size: 11px;
  color: var(--text-primary, #d1d4dc);
  font-weight: 600;
}

.h-bar-track {
  flex: 1;
  height: 6px;
  background: var(--bg-tertiary, #2a2e39);
  border-radius: 3px;
  overflow: hidden;
}

.h-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.h-bar-value {
  min-width: 50px;
  text-align: right;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary, #d1d4dc);
}

// 详情面板
.details-panel {
  .details-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }
}

.detail-group {
  margin-bottom: 20px;
}

.detail-group-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary, #cbd5e1);
  text-transform: uppercase;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-color, #2a2e39);
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color, #2a2e39);
  font-size: 12px;
}

.detail-label { color: var(--text-secondary, #787b86); }
.detail-value {
  font-weight: 600;
  &.active { color: #26a69a; }
  &.paused { color: #ff9800; }
  &.stopped { color: #787b86; }
  &.positive { color: #ef5350; }
}

.factor-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.factor-item {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 4px;
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.factor-name { font-weight: 600; }
.factor-weight { color: #2962ff; font-weight: 600; }

// 空状态
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #cbd5e1);

  .empty-icon { width: 64px; height: 64px; margin-bottom: 16px; opacity: 0.5; }
  p { margin-bottom: 16px; }
}
</style>
