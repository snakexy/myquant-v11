<template>
  <div class="risk-monitor-container">
    <!-- 左侧：综合风险评分 -->
    <div class="risk-score-panel">
      <div class="panel-header">
        <span>{{ t.comprehensiveRiskScore }}</span>
      </div>
      <div class="panel-content">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>{{ t.loading }}</span>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-container">
          <el-icon><WarningFilled /></el-icon>
          <span>{{ error }}</span>
          <el-button size="small" @click="loadComprehensiveScore">{{ t.retry }}</el-button>
        </div>

        <!-- 综合风险评分内容 -->
        <template v-else>
          <!-- 总分仪表盘 -->
          <div class="risk-gauge">
            <svg viewBox="0 0 200 100" class="gauge-svg">
              <path
                class="gauge-arc gauge-bg"
                d="M 20 100 A 80 80 0 0 1 180 100"
              />
              <path
                class="gauge-arc gauge-fill"
                :class="riskLevelClass"
                d="M 20 100 A 80 80 0 0 1 180 100"
                :stroke-dasharray="251"
                :stroke-dashoffset="gaugeOffset"
                :stroke="gaugeColor"
              />
            </svg>
            <div class="gauge-value" :style="{ color: gaugeColor }">{{ comprehensiveScore.score }}</div>
            <div class="gauge-label">{{ riskLevelText }}</div>
          </div>

          <!-- 维度评分卡片 -->
          <div class="dimension-cards">
            <div class="dimension-card">
              <div class="dimension-header">
                <span class="dimension-icon">📊</span>
                <span class="dimension-name">{{ t.positionRisk }}</span>
              </div>
              <div class="dimension-score">
                <span class="score-value" :class="getDimensionClass(comprehensiveScore.dimensions?.position?.score)">
                  {{ comprehensiveScore.dimensions?.position?.score ?? '-' }}
                </span>
                <span class="score-max">/ {{ comprehensiveScore.dimensions?.position?.max_score ?? 25 }}</span>
              </div>
              <div class="dimension-detail">{{ comprehensiveScore.dimensions?.position?.details ?? '-' }}</div>
            </div>

            <div class="dimension-card">
              <div class="dimension-header">
                <span class="dimension-icon">📉</span>
                <span class="dimension-name">{{ t.drawdownRisk }}</span>
              </div>
              <div class="dimension-score">
                <span class="score-value" :class="getDimensionClass(comprehensiveScore.dimensions?.drawdown?.score)">
                  {{ comprehensiveScore.dimensions?.drawdown?.score ?? '-' }}
                </span>
                <span class="score-max">/ {{ comprehensiveScore.dimensions?.drawdown?.max_score ?? 25 }}</span>
              </div>
              <div class="dimension-detail">{{ comprehensiveScore.dimensions?.drawdown?.details ?? '-' }}</div>
            </div>

            <div class="dimension-card">
              <div class="dimension-header">
                <span class="dimension-icon">⚠️</span>
                <span class="dimension-name">{{ t.varCvarRisk }}</span>
              </div>
              <div class="dimension-score">
                <span class="score-value" :class="getDimensionClass(comprehensiveScore.dimensions?.var_cvar?.score)">
                  {{ comprehensiveScore.dimensions?.var_cvar?.score ?? '-' }}
                </span>
                <span class="score-max">/ {{ comprehensiveScore.dimensions?.var_cvar?.max_score ?? 25 }}</span>
              </div>
              <div class="dimension-detail">{{ comprehensiveScore.dimensions?.var_cvar?.details ?? '-' }}</div>
            </div>

            <div class="dimension-card">
              <div class="dimension-header">
                <span class="dimension-icon">📈</span>
                <span class="dimension-name">{{ t.betaFactorRisk }}</span>
              </div>
              <div class="dimension-score">
                <span class="score-value" :class="getDimensionClass(comprehensiveScore.dimensions?.beta_factor?.score)">
                  {{ comprehensiveScore.dimensions?.beta_factor?.score ?? '-' }}
                </span>
                <span class="score-max">/ {{ comprehensiveScore.dimensions?.beta_factor?.max_score ?? 25 }}</span>
              </div>
              <div class="dimension-detail">{{ comprehensiveScore.dimensions?.beta_factor?.details ?? '-' }}</div>
            </div>
          </div>

          <!-- 统计卡片 -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-label">{{ t.totalScore }}</div>
              <div class="stat-value" :class="riskLevelClass">{{ comprehensiveScore.score }}</div>
              <div class="stat-sub">{{ t.outOf100 }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">{{ t.riskLevel }}</div>
              <div class="stat-value" :class="riskLevelClass">{{ riskLevelText }}</div>
              <div class="stat-sub">{{ comprehensiveScore.top_risks?.length ?? 0 }} {{ t.riskFactors }}</div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 中间：风险指标 -->
    <div class="risk-metrics-panel">
      <div class="panel-header">
        <span>{{ t.riskMetrics }}</span>
        <div class="header-score-badge" :class="riskLevelClass">
          <span class="badge-score">{{ comprehensiveScore.score }}</span>
          <span class="badge-label">{{ t.scoreLabel }}</span>
        </div>
      </div>
      <div class="panel-content">
        <!-- 核心指标仪表盘区域 -->
        <div class="key-metrics-gauges">
          <div class="metric-gauge-card">
            <div class="gauge-ring">
              <svg viewBox="0 0 60 60">
                <circle class="gauge-ring-bg" cx="30" cy="30" r="24" />
                <circle
                  class="gauge-ring-fill"
                  :class="getCvarGaugeClass"
                  cx="30" cy="30" r="24"
                  :stroke-dasharray="150.8"
                  :stroke-dashoffset="getCvarGaugeOffset"
                />
              </svg>
              <div class="gauge-ring-value" :class="getCvarGaugeClass">
                {{ getCvarDisplay }}
              </div>
            </div>
            <div class="gauge-ring-label">{{ t.cvarGauge }}</div>
            <div class="gauge-ring-desc">{{ t.cvarDesc }}</div>
          </div>

          <div class="metric-gauge-card">
            <div class="gauge-ring">
              <svg viewBox="0 0 60 60">
                <circle class="gauge-ring-bg" cx="30" cy="30" r="24" />
                <circle
                  class="gauge-ring-fill"
                  :class="getBetaGaugeClass"
                  cx="30" cy="30" r="24"
                  :stroke-dasharray="150.8"
                  :stroke-dashoffset="getBetaGaugeOffset"
                />
              </svg>
              <div class="gauge-ring-value" :class="getBetaGaugeClass">
                {{ getBetaDisplay }}
              </div>
            </div>
            <div class="gauge-ring-label">{{ t.betaGauge }}</div>
            <div class="gauge-ring-desc">{{ t.betaDesc }}</div>
          </div>

          <div class="metric-gauge-card">
            <div class="gauge-ring">
              <svg viewBox="0 0 60 60">
                <circle class="gauge-ring-bg" cx="30" cy="30" r="24" />
                <circle
                  class="gauge-ring-fill"
                  :class="getDrawdownGaugeClass"
                  cx="30" cy="30" r="24"
                  :stroke-dasharray="150.8"
                  :stroke-dashoffset="getDrawdownGaugeOffset"
                />
              </svg>
              <div class="gauge-ring-value" :class="getDrawdownGaugeClass">
                {{ getDrawdownDisplay }}
              </div>
            </div>
            <div class="gauge-ring-label">{{ t.drawdownGauge }}</div>
            <div class="gauge-ring-desc">{{ t.drawdownDesc }}</div>
          </div>
        </div>

        <h1 class="page-title">{{ t.riskOverview }}</h1>
        <p class="page-subtitle">{{ t.riskOverviewDesc }}</p>

        <div class="risk-items">
          <div
            class="risk-item"
            v-for="item in riskMetrics"
            :key="item.key"
          >
            <div class="risk-header">
              <span class="risk-title">{{ item.label }}</span>
              <span class="risk-status" :class="item.status">{{ item.statusText }}</span>
            </div>
            <div class="risk-bar">
              <div
                class="risk-bar-fill"
                :class="item.status"
                :style="{ width: item.percentage + '%' }"
              ></div>
            </div>
            <div class="risk-details">
              <span>{{ t.current }}: {{ item.currentDisplay }}</span>
              <span>{{ t.limit }}: {{ item.limitDisplay }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：限额配置和事件 -->
    <div class="limits-events-panel">
      <div class="panel-header">
        <span>{{ t.limitsAndEvents }}</span>
      </div>
      <div class="panel-split">
        <!-- 限额配置 -->
        <div class="limits-panel">
          <div class="limits-section">
            <div class="limits-section-title">{{ t.positionLimits }}</div>
            <div class="limit-item">
              <span class="limit-label">{{ t.maxSinglePosition }}</span>
              <div class="limit-value">
                <input
                  type="number"
                  class="limit-input"
                  v-model.number="limits.maxSinglePosition"
                  @change="saveLimits"
                />
                <span class="limit-unit">%</span>
              </div>
            </div>
            <div class="limit-item">
              <span class="limit-label">{{ t.maxSectorExposure }}</span>
              <div class="limit-value">
                <input
                  type="number"
                  class="limit-input"
                  v-model.number="limits.maxSectorExposure"
                  @change="saveLimits"
                />
                <span class="limit-unit">%</span>
              </div>
            </div>
            <div class="limit-item">
              <span class="limit-label">{{ t.maxPositions }}</span>
              <div class="limit-value">
                <input
                  type="number"
                  class="limit-input"
                  v-model.number="limits.maxPositions"
                  @change="saveLimits"
                />
                <span class="limit-unit">{{ t.count }}</span>
              </div>
            </div>
          </div>

          <div class="limits-section">
            <div class="limits-section-title">{{ t.lossLimits }}</div>
            <div class="limit-item">
              <span class="limit-label">{{ t.maxDailyLoss }}</span>
              <div class="limit-value">
                <input
                  type="number"
                  class="limit-input"
                  v-model.number="limits.maxDailyLoss"
                  @change="saveLimits"
                />
                <span class="limit-unit">%</span>
              </div>
            </div>
            <div class="limit-item">
              <span class="limit-label">{{ t.maxDrawdown }}</span>
              <div class="limit-value">
                <input
                  type="number"
                  class="limit-input"
                  v-model.number="limits.maxDrawdown"
                  @change="saveLimits"
                />
                <span class="limit-unit">%</span>
              </div>
            </div>
            <div class="limit-item">
              <span class="limit-label">{{ t.stopLoss }}</span>
              <div class="limit-value">
                <input
                  type="number"
                  class="limit-input"
                  v-model.number="limits.stopLoss"
                  @change="saveLimits"
                />
                <span class="limit-unit">%</span>
              </div>
            </div>
          </div>

          <div class="limits-section">
            <div class="limits-section-title">{{ t.autoControls }}</div>
            <div class="limit-item">
              <span class="limit-label">{{ t.autoStopLoss }}</span>
              <el-switch
                v-model="autoControls.autoStopLoss"
                size="small"
                @change="saveLimits"
              />
            </div>
            <div class="limit-item">
              <span class="limit-label">{{ t.autoReducePosition }}</span>
              <el-switch
                v-model="autoControls.autoReducePosition"
                size="small"
                @change="saveLimits"
              />
            </div>
            <div class="limit-item">
              <span class="limit-label">{{ t.haltOnLimitBreach }}</span>
              <el-switch
                v-model="autoControls.haltOnLimitBreach"
                size="small"
                @change="saveLimits"
              />
            </div>
          </div>
        </div>

        <!-- 最近事件 -->
        <div class="events-section">
          <div class="panel-header sub-header">
            <span>{{ t.recentEvents }}</span>
          </div>
          <div class="risk-events">
            <div
              class="event-item"
              v-for="event in recentEvents"
              :key="event.id"
            >
              <div class="event-header">
                <span class="event-type" :style="{ color: getEventColor(event.type) }">{{ event.title }}</span>
                <span class="event-time">{{ event.time }}</span>
              </div>
              <div class="event-desc">{{ event.description }}</div>
              <div class="event-action">{{ event.action }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import { riskAnalysisApi, type ComprehensiveRiskScore } from '@/api/modules/production'

// Props
interface Props {
  taskId?: string
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  taskId: 'default',
  isZh: true
})

// 多语言文本
const t = computed(() => ({
  riskScore: props.isZh ? '风险评分' : 'Risk Score',
  comprehensiveRiskScore: props.isZh ? '综合风险评分' : 'Comprehensive Risk Score',
  riskMetrics: props.isZh ? '风险指标' : 'Risk Metrics',
  limitsAndEvents: props.isZh ? '限额与事件' : 'Limits & Events',
  riskOverview: props.isZh ? '风险概览' : 'Risk Overview',
  riskOverviewDesc: props.isZh ? '实时风险监控与控制' : 'Real-time risk monitoring and control',
  activeAlerts: props.isZh ? '活跃告警' : 'Active Alerts',
  outOf100: props.isZh ? '满分 100' : 'Out of 100',
  warning: props.isZh ? '警告' : 'warning',
  danger: props.isZh ? '危险' : 'danger',
  safe: props.isZh ? '安全' : 'Safe',
  warningStatus: props.isZh ? '警告' : 'Warning',
  dangerStatus: props.isZh ? '危险' : 'Danger',
  current: props.isZh ? '当前' : 'Current',
  limit: props.isZh ? '限额' : 'Limit',
  loading: props.isZh ? '加载中...' : 'Loading...',
  retry: props.isZh ? '重试' : 'Retry',
  totalScore: props.isZh ? '总分' : 'Total Score',
  riskLevel: props.isZh ? '风险等级' : 'Risk Level',
  riskFactors: props.isZh ? '个风险因素' : 'risk factors',
  // 维度名称
  positionRisk: props.isZh ? '仓位风险' : 'Position Risk',
  drawdownRisk: props.isZh ? '回撤风险' : 'Drawdown Risk',
  varCvarRisk: props.isZh ? 'VaR/CVaR' : 'VaR/CVaR',
  betaFactorRisk: props.isZh ? 'Beta/因子' : 'Beta/Factor',
  // 风险指标
  singlePositionLimit: props.isZh ? '单一持仓限额' : 'Single Position Limit',
  sectorConcentration: props.isZh ? '行业集中度' : 'Sector Concentration',
  currentDrawdown: props.isZh ? '当前回撤' : 'Current Drawdown',
  dailyVolatility: props.isZh ? '日波动率' : 'Daily Volatility',
  turnoverRate: props.isZh ? '换手率' : 'Turnover Rate',
  dailyLossLimit: props.isZh ? '日亏损限额' : 'Daily Loss Limit',
  portfolioVolatility: props.isZh ? '组合波动率' : 'Portfolio Volatility',
  leverageRatio: props.isZh ? '杠杆比率' : 'Leverage Ratio',
  var95: props.isZh ? 'VaR (95%)' : 'VaR (95%)',
  // 限额配置
  positionLimits: props.isZh ? '仓位限制' : 'Position Limits',
  maxSinglePosition: props.isZh ? '最大单仓' : 'Max Single Position',
  maxSectorExposure: props.isZh ? '最大行业敞口' : 'Max Sector Exposure',
  maxPositions: props.isZh ? '最大持仓数' : 'Max Positions',
  count: props.isZh ? '个' : 'count',
  lossLimits: props.isZh ? '亏损限制' : 'Loss Limits',
  maxDailyLoss: props.isZh ? '最大日亏损' : 'Max Daily Loss',
  maxDrawdown: props.isZh ? '最大回撤' : 'Max Drawdown',
  stopLoss: props.isZh ? '止损比例' : 'Stop Loss %',
  autoControls: props.isZh ? '自动控制' : 'Auto Controls',
  autoStopLoss: props.isZh ? '自动止损' : 'Auto Stop Loss',
  autoReducePosition: props.isZh ? '自动减仓' : 'Auto Reduce Position',
  haltOnLimitBreach: props.isZh ? '超限暂停' : 'Halt on Limit Breach',
  recentEvents: props.isZh ? '最近事件' : 'Recent Events',
  // 事件类型
  leverageAlert: props.isZh ? '杠杆警告' : 'Leverage Alert',
  sectorWarning: props.isZh ? '行业警告' : 'Sector Warning',
  positionClosed: props.isZh ? '平仓' : 'Position Closed',
  systemCheck: props.isZh ? '系统检查' : 'System Check',
  autoReduceTriggered: props.isZh ? '已触发自动减仓' : 'Auto-reduce triggered',
  monitoring: props.isZh ? '监控中' : 'Monitoring',
  allMetricsNormal: props.isZh ? '所有指标正常' : 'All metrics normal',
  // 风险等级
  lowRisk: props.isZh ? '低风险' : 'Low Risk',
  mediumRisk: props.isZh ? '中风险' : 'Medium Risk',
  highRisk: props.isZh ? '高风险' : 'High Risk',
  criticalRisk: props.isZh ? '危险' : 'Critical',
  // 仪表盘标签
  scoreLabel: props.isZh ? '分' : 'pts',
  cvarGauge: 'CVaR(95%)',
  cvarDesc: props.isZh ? '条件风险价值' : 'Conditional VaR',
  betaGauge: 'Beta',
  betaDesc: props.isZh ? '相对沪深300' : 'vs HS300',
  drawdownGauge: props.isZh ? '当前回撤' : 'Drawdown',
  drawdownDesc: props.isZh ? '从净值高点' : 'From peak'
}))

// 综合风险评分状态
const loading = ref(false)
const error = ref<string | null>(null)
const comprehensiveScore = ref<ComprehensiveRiskScore>({
  account_id: 'default',
  score: 0,
  level: 'unknown',
  dimensions: {
    position: { score: 0, weight: 0.25, max_score: 25, details: '-' },
    drawdown: { score: 0, weight: 0.25, max_score: 25, details: '-' },
    var_cvar: { score: 0, weight: 0.25, max_score: 25, details: '-' },
    beta_factor: { score: 0, weight: 0.25, max_score: 25, details: '-' }
  },
  top_risks: [],
  recommendations: [],
  timestamp: new Date().toISOString()
})

// 风险等级
const riskLevel = computed(() => {
  const level = comprehensiveScore.value.level
  if (level === 'low') return 'low'
  if (level === 'medium') return 'medium'
  if (level === 'high') return 'high'
  if (level === 'critical') return 'critical'
  // 根据分数计算
  const score = comprehensiveScore.value.score
  if (score <= 30) return 'low'
  if (score <= 60) return 'medium'
  if (score <= 80) return 'high'
  return 'critical'
})

// 获取维度评分的CSS类
const getDimensionClass = (score: number | undefined): string => {
  if (score === undefined) return ''
  if (score >= 20) return 'low'
  if (score >= 15) return 'medium'
  if (score >= 10) return 'high'
  return 'critical'
}

// 加载综合风险评分
const loadComprehensiveScore = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await riskAnalysisApi.getScore(props.taskId || 'default')
    if (response.success && response.data) {
      comprehensiveScore.value = response.data
    } else {
      error.value = props.isZh ? '获取风险评分失败' : 'Failed to get risk score'
    }
  } catch (err: any) {
    console.error('Failed to load comprehensive risk score:', err)
    error.value = props.isZh ? '无法连接到风险服务' : 'Cannot connect to risk service'
  } finally {
    loading.value = false
  }
}

// 风险评分 (兼容旧代码)
const riskScore = computed(() => comprehensiveScore.value.score)

const riskLevelClass = computed(() => riskLevel.value)

const riskLevelText = computed(() => {
  const level = riskLevel.value
  const map: Record<string, string> = {
    low: t.value.lowRisk,
    medium: t.value.mediumRisk,
    high: t.value.highRisk,
    critical: t.value.criticalRisk
  }
  return map[level]
})

const gaugeColor = computed(() => {
  const level = riskLevel.value
  const map: Record<string, string> = {
    low: '#26a69a',
    medium: '#f7931a',
    high: '#ef5350',
    critical: '#b71c1c'
  }
  return map[level]
})

const gaugeOffset = computed(() => {
  // 计算仪表盘偏移量 (251 是半圆弧长)
  const ratio = riskScore.value / 100
  return 251 * (1 - ratio)
})

// 格式化百分比
const formatPercent = (value: number): string => {
  return `${(value * 100).toFixed(2)}%`
}

// CVaR 仪表盘计算 (0-10%范围, 150.8是圆周长)
const getCvarGaugeClass = computed(() => {
  const cvar = Math.abs(comprehensiveScore.value.raw_metrics?.cvar_95 ?? 0.032)
  if (cvar > 0.08) return 'critical'
  if (cvar > 0.05) return 'high'
  if (cvar > 0.03) return 'medium'
  return 'low'
})

const getCvarGaugeOffset = computed(() => {
  const cvar = Math.abs(comprehensiveScore.value.raw_metrics?.cvar_95 ?? 0.032)
  const ratio = Math.min(cvar / 0.10, 1) // 0-10%范围
  return 150.8 * (1 - ratio)
})

const getCvarDisplay = computed(() => {
  const cvar = comprehensiveScore.value.raw_metrics?.cvar_95 ?? 0.032
  return formatPercent(Math.abs(cvar))
})

// Beta 仪表盘计算 (0-2范围)
const getBetaGaugeClass = computed(() => {
  const beta = Math.abs(comprehensiveScore.value.raw_metrics?.beta ?? 1.0)
  if (beta > 1.5) return 'critical'
  if (beta > 1.2) return 'high'
  if (beta > 0.8) return 'medium'
  return 'low'
})

const getBetaGaugeOffset = computed(() => {
  const beta = Math.abs(comprehensiveScore.value.raw_metrics?.beta ?? 1.0)
  const ratio = Math.min(beta / 2.0, 1) // 0-2范围
  return 150.8 * (1 - ratio)
})

const getBetaDisplay = computed(() => {
  return (comprehensiveScore.value.raw_metrics?.beta ?? 1.0).toFixed(2)
})

// 回撤仪表盘计算 (0-20%范围)
const getDrawdownGaugeClass = computed(() => {
  const dd = Math.abs(comprehensiveScore.value.raw_metrics?.current_drawdown ?? 0.035)
  if (dd > 0.15) return 'critical'
  if (dd > 0.10) return 'high'
  if (dd > 0.05) return 'medium'
  return 'low'
})

const getDrawdownGaugeOffset = computed(() => {
  const dd = Math.abs(comprehensiveScore.value.raw_metrics?.current_drawdown ?? 0.035)
  const ratio = Math.min(dd / 0.20, 1) // 0-20%范围
  return 150.8 * (1 - ratio)
})

const getDrawdownDisplay = computed(() => {
  const dd = comprehensiveScore.value.raw_metrics?.current_drawdown ?? -0.035
  return formatPercent(dd)
})

// 告警数量
const alertCounts = computed(() => {
  let warning = 0
  let danger = 0
  riskMetrics.value.forEach(item => {
    if (item.status === 'warning') warning++
    if (item.status === 'danger') danger++
  })
  return { warning, danger, total: warning + danger }
})

// 风险指标数据
const riskMetrics = computed(() => {
  const data = riskData.value
  return [
    {
      key: 'singlePosition',
      label: t.value.singlePositionLimit,
      current: data.singlePosition.current,
      limit: data.singlePosition.limit,
      percentage: (data.singlePosition.current / data.singlePosition.limit) * 100,
      status: getStatus(data.singlePosition.current, data.singlePosition.limit),
      statusText: getStatusText(data.singlePosition.current, data.singlePosition.limit),
      currentDisplay: `${(data.singlePosition.current * 100).toFixed(0)}%`,
      limitDisplay: `${(data.singlePosition.limit * 100).toFixed(0)}%`
    },
    {
      key: 'sectorConcentration',
      label: t.value.sectorConcentration,
      current: data.sectorConcentration.current,
      limit: data.sectorConcentration.limit,
      percentage: (data.sectorConcentration.current / data.sectorConcentration.limit) * 100,
      status: getStatus(data.sectorConcentration.current, data.sectorConcentration.limit),
      statusText: getStatusText(data.sectorConcentration.current, data.sectorConcentration.limit),
      currentDisplay: `${(data.sectorConcentration.current * 100).toFixed(0)}%`,
      limitDisplay: `${(data.sectorConcentration.limit * 100).toFixed(0)}%`
    },
    {
      key: 'drawdown',
      label: t.value.currentDrawdown,
      current: data.drawdown.current,
      limit: data.drawdown.limit,
      percentage: (data.drawdown.current / data.drawdown.limit) * 100,
      status: getStatus(data.drawdown.current, data.drawdown.limit),
      statusText: getStatusText(data.drawdown.current, data.drawdown.limit),
      currentDisplay: `${(data.drawdown.current * 100).toFixed(1)}%`,
      limitDisplay: `${(data.drawdown.limit * 100).toFixed(0)}%`
    },
    {
      key: 'dailyLoss',
      label: t.value.dailyLossLimit,
      current: data.dailyLoss.current,
      limit: data.dailyLoss.limit,
      percentage: (data.dailyLoss.current / data.dailyLoss.limit) * 100,
      status: getStatus(data.dailyLoss.current, data.dailyLoss.limit),
      statusText: getStatusText(data.dailyLoss.current, data.dailyLoss.limit),
      currentDisplay: `${(data.dailyLoss.current * 100).toFixed(1)}%`,
      limitDisplay: `${(data.dailyLoss.limit * 100).toFixed(0)}%`
    },
    {
      key: 'dailyVolatility',
      label: t.value.dailyVolatility,
      current: data.dailyVolatility.current,
      limit: data.dailyVolatility.limit,
      percentage: (data.dailyVolatility.current / data.dailyVolatility.limit) * 100,
      status: getStatus(data.dailyVolatility.current, data.dailyVolatility.limit),
      statusText: getStatusText(data.dailyVolatility.current, data.dailyVolatility.limit),
      currentDisplay: `${(data.dailyVolatility.current * 100).toFixed(1)}%`,
      limitDisplay: `${(data.dailyVolatility.limit * 100).toFixed(0)}%`
    },
    {
      key: 'turnoverRate',
      label: t.value.turnoverRate,
      current: data.turnoverRate.current,
      limit: data.turnoverRate.limit,
      percentage: (data.turnoverRate.current / data.turnoverRate.limit) * 100,
      status: getStatus(data.turnoverRate.current, data.turnoverRate.limit),
      statusText: getStatusText(data.turnoverRate.current, data.turnoverRate.limit),
      currentDisplay: `${(data.turnoverRate.current * 100).toFixed(0)}%/${props.isZh ? '月' : 'mo'}`,
      limitDisplay: `${(data.turnoverRate.limit * 100).toFixed(0)}%/${props.isZh ? '月' : 'mo'}`
    },
    {
      key: 'leverage',
      label: t.value.leverageRatio,
      current: data.leverage.current,
      limit: data.leverage.limit,
      percentage: (data.leverage.current / data.leverage.limit) * 100,
      status: getStatus(data.leverage.current, data.leverage.limit),
      statusText: getStatusText(data.leverage.current, data.leverage.limit),
      currentDisplay: `${data.leverage.current.toFixed(1)}x`,
      limitDisplay: `${data.leverage.limit.toFixed(1)}x`
    },
    {
      key: 'var95',
      label: t.value.var95,
      current: data.var95.current,
      limit: data.var95.limit,
      percentage: (data.var95.current / data.var95.limit) * 100,
      status: getStatus(data.var95.current, data.var95.limit),
      statusText: getStatusText(data.var95.current, data.var95.limit),
      currentDisplay: `${(data.var95.current * 100).toFixed(1)}%`,
      limitDisplay: `${(data.var95.limit * 100).toFixed(0)}%`
    }
  ]
})

// 获取状态
const getStatus = (current: number, limit: number): string => {
  const ratio = current / limit
  if (ratio < 0.7) return 'low'
  if (ratio < 0.9) return 'medium'
  return 'high'
}

const getStatusText = (current: number, limit: number): string => {
  const status = getStatus(current, limit)
  const map: Record<string, string> = {
    low: t.value.safe,
    medium: t.value.warningStatus,
    high: t.value.dangerStatus
  }
  return map[status]
}

// 风险数据 - 指标阈值遵循 MyQuant架构文档 06-风险管理模块.html 规范
const riskData = ref({
  // 组合层风险 - 文档阈值
  singlePosition: { current: 0.08, limit: 0.10 },      // 单股仓位 < 10%
  sectorConcentration: { current: 0.25, limit: 0.30 }, // 行业集中度 < 30%
  drawdown: { current: 0.032, limit: 0.15 },           // 最大回撤 < 15%
  dailyVolatility: { current: 0.025, limit: 0.03 },    // 日波动率 < 3%
  turnoverRate: { current: 0.42, limit: 0.50 },        // 换手率 < 50%/月
  // 交易层风险
  dailyLoss: { current: 0.008, limit: 0.05 },          // 日亏损限额
  leverage: { current: 1.9, limit: 2.0 },              // 杠杆比率
  var95: { current: 0.025, limit: 0.10 }               // VaR (95%)
})

// 限额配置 - 遵循 MyQuant架构文档 06-风险管理模块.html 规范
const limits = ref({
  maxSinglePosition: 10,      // 单股仓位 < 10%
  maxSectorExposure: 30,      // 行业集中度 < 30%
  maxPositions: 30,
  maxDailyLoss: 5,
  maxDrawdown: 15,            // 最大回撤 < 15%
  stopLoss: 3
})

// 自动控制
const autoControls = ref({
  autoStopLoss: true,
  autoReducePosition: false,
  haltOnLimitBreach: true
})

// 最近事件
const recentEvents = computed(() => [
  {
    id: 1,
    type: 'danger',
    title: t.value.leverageAlert,
    time: '10:35:12',
    description: props.isZh ? '杠杆接近上限 (1.9x / 2.0x)' : 'Leverage approaching limit (1.9x / 2.0x)',
    action: t.value.autoReduceTriggered
  },
  {
    id: 2,
    type: 'warning',
    title: t.value.sectorWarning,
    time: '10:28:45',
    description: props.isZh ? '金融行业集中度达到 35%' : 'Financial sector concentration at 35%',
    action: t.value.monitoring
  },
  {
    id: 3,
    type: 'success',
    title: t.value.positionClosed,
    time: '10:15:30',
    description: props.isZh ? '000858 触发止损' : 'Stop loss triggered for 000858',
    action: '-2.5%'
  },
  {
    id: 4,
    type: 'info',
    title: t.value.systemCheck,
    time: '10:00:00',
    description: props.isZh ? '每日风险评估已完成' : 'Daily risk assessment completed',
    action: t.value.allMetricsNormal
  }
])

// 获取事件颜色
const getEventColor = (type: string): string => {
  const map: Record<string, string> = {
    danger: '#ef5350',
    warning: '#f7931a',
    success: '#26a69a',
    info: '#2962ff'
  }
  return map[type] || '#787b86'
}

// 保存限额配置
const saveLimits = async () => {
  try {
    // TODO: 调用API保存配置
    ElMessage.success(props.isZh ? '配置已保存' : 'Settings saved')
  } catch (error) {
    console.error('Failed to save limits:', error)
  }
}

// 加载数据
const loadData = async () => {
  // 加载综合风险评分
  await loadComprehensiveScore()
}

// 暴露方法
defineExpose({
  refresh: loadData
})

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.risk-monitor-container {
  display: grid;
  grid-template-columns: 320px 1fr 300px;
  width: 100%;
  height: 100%;
  min-height: 0;
  gap: 1px;
  background: var(--border-color, #2a2e39);
}

.panel-header {
  background: var(--bg-secondary, #1e222d);
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary, #d1d4dc);
  border-bottom: 1px solid var(--border-color, #2a2e39);
  display: flex;
  justify-content: space-between;
  align-items: center;

  &.sub-header {
    padding: 10px 16px;
    font-size: 11px;
  }
}

// 头部评分徽章
.header-score-badge {
  display: flex;
  align-items: baseline;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: 600;

  &.low { background: rgba(38, 166, 154, 0.2); color: #26a69a; }
  &.medium { background: rgba(247, 147, 26, 0.2); color: #f7931a; }
  &.high { background: rgba(239, 83, 80, 0.2); color: #ef5350; }
  &.critical { background: rgba(183, 28, 28, 0.2); color: #b71c1c; }

  .badge-score {
    font-size: 18px;
  }

  .badge-label {
    font-size: 10px;
    opacity: 0.8;
  }
}

.panel-content {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
  background: var(--bg-primary, #131722);
}

// 左侧面板
.risk-score-panel {
  display: flex;
  flex-direction: column;
  background: var(--bg-primary, #131722);
}

// 仪表盘
.risk-gauge {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  text-align: center;
}

.gauge-svg {
  width: 200px;
  height: 100px;
}

.gauge-arc {
  fill: none;
  stroke-width: 20;
}

.gauge-bg {
  stroke: var(--bg-tertiary, #2a2e39);
}

.gauge-fill {
  transition: stroke-dashoffset 0.5s, stroke 0.3s;
}

.gauge-value {
  font-size: 36px;
  font-weight: 700;
  margin-top: 16px;
  transition: color 0.3s;
}

.gauge-label {
  font-size: 12px;
  color: var(--text-secondary, #787b86);
  margin-top: 4px;
}

// 统计卡片
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

// 加载状态
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-secondary, #787b86);
  gap: 12px;

  .el-icon {
    font-size: 24px;
  }

  &.error-container {
    color: var(--danger-color, #ef5350);
  }
}

// 维度卡片
.dimension-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}

.dimension-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 6px;
  padding: 12px;
}

.dimension-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.dimension-icon {
  font-size: 14px;
}

.dimension-name {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-secondary, #787b86);
}

.dimension-score {
  margin-bottom: 4px;

  .score-value {
    font-size: 20px;
    font-weight: 700;

    &.low { color: #26a69a; }
    &.medium { color: #f7931a; }
    &.high { color: #ef5350; }
    &.critical { color: #b71c1c; }
  }

  .score-max {
    font-size: 12px;
    color: var(--text-secondary, #787b86);
  }
}

.dimension-detail {
  font-size: 10px;
  color: var(--text-muted, #5d606b);
  line-height: 1.3;
}

.stat-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 6px;
  padding: 16px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-secondary, #787b86);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #d1d4dc);

  &.low { color: #26a69a; }
  &.medium { color: #f7931a; }
  &.high { color: #ef5350; }
  &.critical { color: #b71c1c; }
  &.negative { color: #ef5350; }
}

.stat-sub {
  font-size: 11px;
  color: var(--text-secondary, #787b86);
  margin-top: 4px;
}

// 中间面板
.risk-metrics-panel {
  display: flex;
  flex-direction: column;
  background: var(--bg-primary, #131722);
  overflow: hidden;
}

// 核心指标仪表盘区域
.key-metrics-gauges {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.metric-gauge-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.gauge-ring {
  position: relative;
  width: 60px;
  height: 60px;
  margin: 0 auto 8px;

  svg {
    width: 60px;
    height: 60px;
    transform: rotate(-90deg);
  }
}

.gauge-ring-bg {
  fill: none;
  stroke: var(--bg-tertiary, #363a45);
  stroke-width: 6;
}

.gauge-ring-fill {
  fill: none;
  stroke: #5a6378;  // 默认灰色，防止无类时不可见
  stroke-width: 6;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.5s, stroke 0.3s;

  &.low { stroke: #26a69a; }
  &.medium { stroke: #f7931a; }
  &.high { stroke: #ef5350; }
  &.critical { stroke: #b71c1c; }
}

.gauge-ring-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: 700;
  color: #d1d4dc;  // 默认颜色

  &.low { color: #26a69a; }
  &.medium { color: #f7931a; }
  &.high { color: #ef5350; }
  &.critical { color: #b71c1c; }
}

.gauge-ring-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary, #d1d4dc);
  margin-bottom: 2px;
}

.gauge-ring-desc {
  font-size: 10px;
  color: var(--text-secondary, #787b86);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #d1d4dc);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-secondary, #787b86);
  margin-bottom: 24px;
}

// 风险指标列表
.risk-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-item {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 6px;
  padding: 16px;
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.risk-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary, #d1d4dc);
}

.risk-status {
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;

  &.low {
    background: rgba(38, 166, 154, 0.2);
    color: #26a69a;
  }

  &.medium {
    background: rgba(247, 147, 26, 0.2);
    color: #f7931a;
  }

  &.high {
    background: rgba(239, 83, 80, 0.2);
    color: #ef5350;
  }

  &.critical {
    background: rgba(183, 28, 28, 0.2);
    color: #b71c1c;
  }
}

.risk-bar {
  height: 8px;
  background: var(--bg-tertiary, #2a2e39);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.risk-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;

  &.low { background: #26a69a; }
  &.medium { background: #f7931a; }
  &.high { background: #ef5350; }
  &.critical { background: #b71c1c; }
}

.risk-details {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-secondary, #787b86);
}

// 右侧面板
.limits-events-panel {
  display: flex;
  flex-direction: column;
  background: var(--bg-primary, #131722);
  overflow: hidden;
}

.panel-split {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

// 限额配置面板
.limits-panel {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
}

.limits-section {
  margin-bottom: 24px;
}

.limits-section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary, #787b86);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color, #2a2e39);
}

.limit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color, #2a2e39);
}

.limit-label {
  font-size: 12px;
  color: var(--text-primary, #d1d4dc);
}

.limit-value {
  display: flex;
  align-items: center;
  gap: 8px;
}

.limit-input {
  width: 60px;
  padding: 4px 8px;
  background: var(--bg-tertiary, #2a2e39);
  border: 1px solid var(--border-color, #2a2e39);
  color: var(--text-primary, #d1d4dc);
  font-size: 12px;
  border-radius: 3px;
  text-align: right;

  &:focus {
    outline: none;
    border-color: var(--accent-blue, #2962ff);
  }
}

.limit-unit {
  font-size: 11px;
  color: var(--text-secondary, #787b86);
}

// 事件面板
.events-section {
  border-top: 1px solid var(--border-color, #2a2e39);
  display: flex;
  flex-direction: column;
  max-height: 280px;
}

.risk-events {
  padding: 12px;
  overflow-y: auto;
  flex: 1;
  background: var(--bg-primary, #131722);
}

.event-item {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 8px;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.event-type {
  font-size: 12px;
  font-weight: 600;
}

.event-time {
  font-size: 11px;
  color: var(--text-secondary, #787b86);
}

.event-desc {
  font-size: 12px;
  color: var(--text-primary, #d1d4dc);
  margin-bottom: 6px;
}

.event-action {
  font-size: 11px;
  color: var(--accent-blue, #2962ff);
}

// Element Plus 覆盖
:deep(.el-switch) {
  --el-switch-on-color: #2962ff;
  --el-switch-off-color: #2a2e39;
}

@media (max-width: 1400px) {
  .risk-monitor-container {
    grid-template-columns: 280px 1fr 260px;
  }
}

@media (max-width: 1200px) {
  .risk-monitor-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }

  .limits-events-panel {
    max-height: 400px;
  }
}
</style>
