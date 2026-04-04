<template>
  <div class="intelligent-analysis">
    <!-- 分析头部 -->
    <div class="analysis-header">
      <h3 class="analysis-title">
        <Icon name="brain" class="title-icon" />
        AI 智能分析
      </h3>
      <div class="analysis-controls">
        <button
          class="analyze-btn"
          :class="{ loading: analyzing }"
          @click="runAnalysis"
          :disabled="!hasData || analyzing"
        >
          <Icon v-if="analyzing" name="loading" class="animate-spin" />
          {{ analyzing ? '分析中...' : '开始分析' }}
        </button>
        <button
          class="export-btn"
          @click="exportReport"
          :disabled="!hasResults"
        >
          <Icon name="download" />
          导出报告
        </button>
      </div>
    </div>

    <!-- 分析内容 -->
    <div class="analysis-content">
      <!-- 数据概览 -->
      <div v-if="hasData" class="data-overview">
        <h4 class="section-title">数据概览</h4>
        <div class="overview-grid">
          <div v-for="metric in dataMetrics" :key="metric.key" class="overview-item">
            <div class="metric-icon" :style="{ color: metric.color }">
              <Icon :name="metric.icon" />
            </div>
            <div class="metric-info">
              <span class="metric-label">{{ metric.label }}</span>
              <span class="metric-value">{{ metric.value }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- AI 分析结果 -->
      <div v-if="hasResults" class="analysis-results">
        <!-- 总体评分 -->
        <div class="overall-score">
          <h4 class="section-title">综合评分</h4>
          <div class="score-display">
            <div class="score-circle" :class="getScoreClass(analysisResult.overallScore)">
              <span class="score-value">{{ analysisResult.overallScore }}</span>
              <span class="score-max">/100</span>
            </div>
            <div class="score-details">
              <div class="score-item" v-for="score in analysisResult.categoryScores" :key="score.category">
                <span class="score-label">{{ score.category }}</span>
                <div class="score-bar">
                  <div
                    class="score-fill"
                    :style="{ width: `${score.score}%`, backgroundColor: score.color }"
                  ></div>
                </div>
                <span class="score-value">{{ score.score }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 关键洞察 -->
        <div class="key-insights">
          <h4 class="section-title">关键洞察</h4>
          <div class="insights-list">
            <div
              v-for="insight in analysisResult.insights"
              :key="insight.id"
              class="insight-item"
              :class="`insight--${insight.type}`"
            >
              <div class="insight-icon">
                <Icon :name="getInsightIcon(insight.type)" />
              </div>
              <div class="insight-content">
                <h5 class="insight-title">{{ insight.title }}</h5>
                <p class="insight-description">{{ insight.description }}</p>
                <div v-if="insight.data" class="insight-data">
                  <MiniChart
                    :data="insight.data"
                    :type="insight.chartType"
                    :width="200"
                    :height="60"
                    :color="getInsightColor(insight.type)"
                  />
                </div>
              </div>
              <div class="insight-confidence">
                <span class="confidence-label">置信度</span>
                <div class="confidence-bar">
                  <div
                    class="confidence-fill"
                    :style="{ width: `${insight.confidence}%` }"
                  ></div>
                </div>
                <span class="confidence-value">{{ insight.confidence }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 预测与建议 -->
        <div class="predictions">
          <h4 class="section-title">预测与建议</h4>
          <div class="prediction-grid">
            <div
              v-for="prediction in analysisResult.predictions"
              :key="prediction.id"
              class="prediction-card"
              :class="`prediction--${prediction.sentiment}`"
            >
              <div class="prediction-header">
                <span class="prediction-timeframe">{{ prediction.timeframe }}</span>
                <span class="prediction-sentiment">{{ prediction.sentimentText }}</span>
              </div>
              <div class="prediction-body">
                <div class="prediction-target">
                  <span class="target-label">目标价位</span>
                  <span class="target-value">¥{{ prediction.targetPrice }}</span>
                  <span class="target-change" :class="prediction.changeClass">
                    {{ prediction.changeText }}
                  </span>
                </div>
                <div class="prediction-probability">
                  <span class="probability-label">概率</span>
                  <div class="probability-bar">
                    <div
                      class="probability-fill"
                      :style="{ width: `${prediction.probability}%` }"
                    ></div>
                  </div>
                  <span class="probability-value">{{ prediction.probability }}%</span>
                </div>
              </div>
              <div class="prediction-reason">
                <p>{{ prediction.reason }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 风险评估 -->
        <div class="risk-assessment">
          <h4 class="section-title">风险评估</h4>
          <div class="risk-factors">
            <div
              v-for="risk in analysisResult.riskFactors"
              :key="risk.factor"
              class="risk-item"
              :class="`risk--${risk.level}`"
            >
              <div class="risk-icon">
                <Icon :name="getRiskIcon(risk.level)" />
              </div>
              <div class="risk-content">
                <h5 class="risk-factor">{{ risk.factor }}</h5>
                <p class="risk-description">{{ risk.description }}</p>
              </div>
              <div class="risk-level">
                <span class="risk-label">风险等级</span>
                <span class="risk-value">{{ risk.levelText }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 技术指标分析 -->
        <div class="technical-indicators">
          <h4 class="section-title">技术指标分析</h4>
          <div class="indicators-grid">
            <div
              v-for="indicator in analysisResult.technicalIndicators"
              :key="indicator.name"
              class="indicator-item"
            >
              <div class="indicator-header">
                <span class="indicator-name">{{ indicator.name }}</span>
                <span class="indicator-value" :class="indicator.signalClass">
                  {{ indicator.value }}
                </span>
              </div>
              <div class="indicator-signal">
                <span class="signal-label">信号</span>
                <span class="signal-value" :class="indicator.signalClass">
                  {{ indicator.signal }}
                </span>
              </div>
              <div class="indicator-description">
                <p>{{ indicator.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!hasData" class="empty-state">
        <Icon name="chart-line" class="empty-icon" />
        <p class="empty-text">请先选择股票数据以开始分析</p>
      </div>

      <!-- 分析中状态 -->
      <div v-else-if="analyzing" class="analyzing-state">
        <div class="analyzing-animation">
          <div class="brain-pulse"></div>
          <Icon name="brain" class="brain-icon" />
        </div>
        <p class="analyzing-text">AI 正在深度分析数据...</p>
        <div class="analyzing-progress">
          <div
            class="progress-fill"
            :style="{ width: `${analysisProgress}%` }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import MiniChart from '../charts/MiniChart.vue'

interface StockData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface AnalysisResult {
  overallScore: number
  categoryScores: Array<{
    category: string
    score: number
    color: string
  }>
  insights: Array<{
    id: string
    type: 'positive' | 'negative' | 'neutral'
    title: string
    description: string
    data?: number[]
    chartType?: 'line' | 'bar' | 'area'
    confidence: number
  }>
  predictions: Array<{
    id: string
    timeframe: string
    sentiment: 'bullish' | 'bearish' | 'neutral'
    sentimentText: string
    targetPrice: number
    changeText: string
    changeClass: string
    probability: number
    reason: string
  }>
  riskFactors: Array<{
    factor: string
    level: 'low' | 'medium' | 'high'
    levelText: string
    description: string
  }>
  technicalIndicators: Array<{
    name: string
    value: string
    signal: string
    signalClass: string
    description: string
  }>
}

interface Props {
  data?: StockData[]
  stockCode?: string
  stockName?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  stockCode: '',
  stockName: ''
})

const emit = defineEmits<{
  analysis-complete: [result: AnalysisResult]
}>()

// 状态
const analyzing = ref(false)
const analysisProgress = ref(0)
const analysisResult = ref<AnalysisResult | null>(null)

// 计算属性
const hasData = computed(() => props.data && props.data.length > 0)
const hasResults = computed(() => analysisResult.value !== null)

// 数据指标
const dataMetrics = computed(() => {
  if (!hasData.value) return []

  const prices = props.data.map(d => d.close)
  const volumes = props.data.map(d => d.volume)
  const latestPrice = prices[prices.length - 1]
  const firstPrice = prices[0]
  const maxPrice = Math.max(...prices)
  const minPrice = Math.min(...prices)
  const avgVolume = volumes.reduce((a, b) => a + b, 0) / volumes.length

  const change = ((latestPrice - firstPrice) / firstPrice) * 100
  const volatility = calculateVolatility(prices)

  return [
    {
      key: 'price',
      label: '最新价格',
      value: `¥${latestPrice.toFixed(2)}`,
      icon: 'trending-up',
      color: change >= 0 ? '#22c55e' : '#ef4444'
    },
    {
      key: 'change',
      label: '涨跌幅',
      value: `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`,
      icon: 'percent',
      color: change >= 0 ? '#22c55e' : '#ef4444'
    },
    {
      key: 'volume',
      label: '平均成交量',
      value: formatVolume(avgVolume),
      icon: 'bar-chart',
      color: '#8b5cf6'
    },
    {
      key: 'volatility',
      label: '波动率',
      value: `${(volatility * 100).toFixed(2)}%`,
      icon: 'activity',
      color: '#f59e0b'
    }
  ]
})

// 计算波动率
const calculateVolatility = (prices: number[]): number => {
  const returns = []
  for (let i = 1; i < prices.length; i++) {
    returns.push((prices[i] - prices[i - 1]) / prices[i - 1])
  }

  const mean = returns.reduce((a, b) => a + b, 0) / returns.length
  const variance = returns.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / returns.length

  return Math.sqrt(variance)
}

// 格式化成交量
const formatVolume = (volume: number): string => {
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(1)}亿`
  } else if (volume >= 10000) {
    return `${(volume / 10000).toFixed(1)}万`
  }
  return volume.toFixed(0)
}

// 获取评分样式类
const getScoreClass = (score: number): string => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'average'
  return 'poor'
}

// 获取洞察图标
const getInsightIcon = (type: string): string => {
  switch (type) {
    case 'positive': return 'trending-up'
    case 'negative': return 'trending-down'
    default: return 'minus'
  }
}

// 获取洞察颜色
const getInsightColor = (type: string): string => {
  switch (type) {
    case 'positive': return '#22c55e'
    case 'negative': return '#ef4444'
    default: return '#8b5cf6'
  }
}

// 获取风险图标
const getRiskIcon = (level: string): string => {
  switch (level) {
    case 'high': return 'alert-triangle'
    case 'medium': return 'alert-circle'
    default: return 'shield'
  }
}

// 运行分析
const runAnalysis = async () => {
  if (!hasData.value) return

  analyzing.value = true
  analysisProgress.value = 0

  // 模拟分析进度
  const progressSteps = [10, 25, 40, 60, 75, 90, 100]
  for (const step of progressSteps) {
    await new Promise(resolve => setTimeout(resolve, 300))
    analysisProgress.value = step
  }

  // 生成模拟分析结果
  const mockResult: AnalysisResult = {
    overallScore: Math.floor(Math.random() * 40) + 60,
    categoryScores: [
      { category: '趋势强度', score: Math.floor(Math.random() * 40) + 60, color: '#8b5cf6' },
      { category: '技术面', score: Math.floor(Math.random() * 40) + 60, color: '#3b82f6' },
      { category: '成交量', score: Math.floor(Math.random() * 40) + 60, color: '#10b981' },
      { category: '波动性', score: Math.floor(Math.random() * 40) + 60, color: '#f59e0b' }
    ],
    insights: [
      {
        id: '1',
        type: 'positive',
        title: '上升趋势形成',
        description: '股价已突破关键阻力位，形成新的上升趋势。',
        data: props.data.slice(-20).map(d => d.close),
        chartType: 'line',
        confidence: 85
      },
      {
        id: '2',
        type: 'neutral',
        title: '成交量温和放大',
        description: '近期成交量呈温和放大态势，显示市场参与度提升。',
        data: props.data.slice(-20).map(d => d.volume),
        chartType: 'bar',
        confidence: 72
      }
    ],
    predictions: [
      {
        id: '1',
        timeframe: '1周',
        sentiment: 'bullish',
        sentimentText: '看涨',
        targetPrice: props.data[props.data.length - 1].close * 1.05,
        changeText: '+5.0%',
        changeClass: 'positive',
        probability: 68,
        reason: '技术指标显示买入信号，预计短期内将继续上涨。'
      },
      {
        id: '2',
        timeframe: '1月',
        sentiment: 'neutral',
        sentimentText: '中性',
        targetPrice: props.data[props.data.length - 1].close * 1.02,
        changeText: '+2.0%',
        changeClass: 'positive',
        probability: 55,
        reason: '长期趋势尚不明朗，建议密切关注成交量变化。'
      }
    ],
    riskFactors: [
      {
        factor: '市场风险',
        level: 'medium',
        levelText: '中等',
        description: '当前市场波动较大，需注意系统性风险。'
      },
      {
        factor: '流动性风险',
        level: 'low',
        levelText: '较低',
        description: '股票流动性良好，交易活跃。'
      }
    ],
    technicalIndicators: [
      {
        name: 'MACD',
        value: '0.25',
        signal: '买入',
        signalClass: 'buy',
        description: 'MACD线向上突破信号线，显示买入信号。'
      },
      {
        name: 'RSI',
        value: '58.5',
        signal: '中性',
        signalClass: 'neutral',
        description: 'RSI处于中性区域，既未超买也未超卖。'
      }
    ]
  }

  analysisResult.value = mockResult
  analyzing.value = false
  emit('analysis-complete', mockResult)
}

// 导出报告
const exportReport = () => {
  if (!analysisResult.value) return

  const report = {
    stockCode: props.stockCode,
    stockName: props.stockName,
    analysisDate: new Date().toISOString(),
    result: analysisResult.value
  }

  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `analysis-report-${props.stockCode}-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style lang="scss" scoped>
.intelligent-analysis {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--bg-color-secondary);
  border-radius: var(--border-radius-lg);
}

// 头部
.analysis-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.analysis-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;

  .title-icon {
    color: var(--primary-color);
  }
}

.analysis-controls {
  display: flex;
  gap: var(--spacing-2);
}

.analyze-btn,
.export-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-2) var(--spacing-3);
  border: none;
  border-radius: var(--border-radius-base);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.analyze-btn {
  background: var(--primary-color);
  color: white;

  &:hover:not(:disabled) {
    background: var(--primary-color-dark);
  }

  &.loading {
    opacity: 0.8;
    cursor: not-allowed;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.export-btn {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);

  &:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.15);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

// 内容
.analysis-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-5);
}

.section-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-3);
}

// 数据概览
.data-overview {
  .overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-3);
  }

  .overview-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
    padding: var(--spacing-3);
    background: var(--bg-color-base);
    border-radius: var(--border-radius-base);
  }

  .metric-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius-base);
    font-size: 20px;
  }

  .metric-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .metric-label {
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
  }

  .metric-value {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--text-primary);
  }
}

// 分析结果
.analysis-results {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-5);
}

// 综合评分
.overall-score {
  .score-display {
    display: flex;
    align-items: center;
    gap: var(--spacing-5);
  }

  .score-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    background: conic-gradient(
      from 0deg,
      var(--primary-color) 0deg,
      var(--primary-color) calc(var(--score) * 3.6deg),
      rgba(255, 255, 255, 0.1) calc(var(--score) * 3.6deg)
    );

    &::before {
      content: '';
      position: absolute;
      width: 100px;
      height: 100px;
      background: var(--bg-color-secondary);
      border-radius: 50%;
    }

    &.excellent {
      --score: 80;
      --primary-color: #22c55e;
    }

    &.good {
      --score: 60;
      --primary-color: #3b82f6;
    }

    &.average {
      --score: 40;
      --primary-color: #f59e0b;
    }

    &.poor {
      --score: 20;
      --primary-color: #ef4444;
    }

    .score-value {
      font-size: 32px;
      font-weight: 600;
      color: var(--text-primary);
      position: relative;
      z-index: 1;
    }

    .score-max {
      font-size: var(--font-size-sm);
      color: var(--text-secondary);
      position: relative;
      z-index: 1;
    }
  }

  .score-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2);
  }

  .score-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
  }

  .score-label {
    min-width: 80px;
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
  }

  .score-bar {
    flex: 1;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
  }

  .score-fill {
    height: 100%;
    transition: width 0.5s ease;
  }

  .score-value {
    min-width: 40px;
    text-align: right;
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--text-primary);
  }
}

// 关键洞察
.key-insights {
  .insights-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-3);
  }

  .insight-item {
    display: flex;
    gap: var(--spacing-3);
    padding: var(--spacing-3);
    background: var(--bg-color-base);
    border-radius: var(--border-radius-base);
    border-left: 4px solid;

    &--positive {
      border-left-color: #22c55e;
    }

    &--negative {
      border-left-color: #ef4444;
    }

    &--neutral {
      border-left-color: #8b5cf6;
    }
  }

  .insight-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius-base);
  }

  .insight-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-1);
  }

  .insight-title {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .insight-description {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    margin: 0;
  }

  .insight-confidence {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
    min-width: 100px;
  }

  .confidence-label {
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
  }

  .confidence-bar {
    width: 100%;
    height: 4px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
  }

  .confidence-fill {
    height: 100%;
    background: var(--primary-color);
    transition: width 0.5s ease;
  }

  .confidence-value {
    font-size: var(--font-size-xs);
    color: var(--text-primary);
  }
}

// 预测与建议
.predictions {
  .prediction-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-3);
  }

  .prediction-card {
    padding: var(--spacing-3);
    background: var(--bg-color-base);
    border-radius: var(--border-radius-base);
    border: 1px solid;

    &--bullish {
      border-color: #22c55e;
    }

    &--bearish {
      border-color: #ef4444;
    }

    &--neutral {
      border-color: #8b5cf6;
    }
  }

  .prediction-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-2);
  }

  .prediction-timeframe {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
  }

  .prediction-sentiment {
    font-size: var(--font-size-sm);
    font-weight: 600;
  }

  .prediction-body {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2);
    margin-bottom: var(--spacing-2);
  }

  .prediction-target {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .target-label {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
  }

  .target-value {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--text-primary);
  }

  .target-change {
    font-size: var(--font-size-sm);
    font-weight: 500;

    &.positive {
      color: #22c55e;
    }

    &.negative {
      color: #ef4444;
    }
  }

  .prediction-probability {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
  }

  .probability-label {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
  }

  .probability-bar {
    flex: 1;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
  }

  .probability-fill {
    height: 100%;
    background: var(--primary-color);
    transition: width 0.5s ease;
  }

  .probability-value {
    min-width: 40px;
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--text-primary);
  }

  .prediction-reason {
    padding-top: var(--spacing-2);
    border-top: 1px solid rgba(255, 255, 255, 0.1);

    p {
      font-size: var(--font-size-sm);
      color: var(--text-secondary);
      margin: 0;
    }
  }
}

// 风险评估
.risk-assessment {
  .risk-factors {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-3);
  }

  .risk-item {
    display: flex;
    gap: var(--spacing-3);
    padding: var(--spacing-3);
    background: var(--bg-color-base);
    border-radius: var(--border-radius-base);

    &--high {
      border-left: 4px solid #ef4444;
    }

    &--medium {
      border-left: 4px solid #f59e0b;
    }

    &--low {
      border-left: 4px solid #22c55e;
    }
  }

  .risk-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius-base);
  }

  .risk-content {
    flex: 1;
  }

  .risk-factor {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 var(--spacing-1) 0;
  }

  .risk-description {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    margin: 0;
  }

  .risk-level {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
  }

  .risk-label {
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
  }

  .risk-value {
    font-size: var(--font-size-sm);
    font-weight: 600;
  }
}

// 技术指标
.technical-indicators {
  .indicators-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-3);
  }

  .indicator-item {
    padding: var(--spacing-3);
    background: var(--bg-color-base);
    border-radius: var(--border-radius-base);
  }

  .indicator-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-2);
  }

  .indicator-name {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--text-primary);
  }

  .indicator-value {
    font-size: var(--font-size-base);
    font-weight: 600;

    &.buy {
      color: #22c55e;
    }

    &.sell {
      color: #ef4444;
    }

    &.neutral {
      color: #8b5cf6;
    }
  }

  .indicator-signal {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-2);
  }

  .signal-label {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
  }

  .signal-value {
    font-size: var(--font-size-sm);
    font-weight: 600;

    &.buy {
      color: #22c55e;
    }

    &.sell {
      color: #ef4444;
    }

    &.neutral {
      color: #8b5cf6;
    }
  }

  .indicator-description {
    p {
      font-size: var(--font-size-sm);
      color: var(--text-secondary);
      margin: 0;
    }
  }
}

// 空状态和分析中状态
.empty-state,
.analyzing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-8);
  text-align: center;
}

.empty-icon,
.brain-icon {
  font-size: 64px;
  color: var(--text-disabled);
  margin-bottom: var(--spacing-3);
}

.empty-text,
.analyzing-text {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  margin: 0;
}

// 分析中动画
.analyzing-animation {
  position: relative;
  margin-bottom: var(--spacing-3);
}

.brain-pulse {
  position: absolute;
  width: 100px;
  height: 100px;
  border: 2px solid var(--primary-color);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.brain-icon {
  font-size: 48px;
  color: var(--primary-color);
  position: relative;
  z-index: 1;
}

.analyzing-progress {
  width: 300px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-top: var(--spacing-3);
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.5;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

// 动画
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>