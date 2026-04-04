<template>
  <div class="portfolio-analysis-section">
    <!-- 头部 -->
    <div class="section-header">
      <div class="section-title">
        <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7" rx="1"></rect>
          <rect x="14" y="3" width="7" height="7" rx="1"></rect>
          <rect x="3" y="14" width="7" height="7" rx="1"></rect>
          <rect x="14" y="14" width="7" height="7" rx="1"></rect>
        </svg>
        <span>{{ title }}</span>
      </div>
      <!-- 整体风险区间 -->
      <div class="overall-risk-zone">
        <span class="zone-label">风险区间:</span>
        <div class="zone-bar">
          <div class="zone-segment safe"></div>
          <div class="zone-segment caution"></div>
          <div class="zone-segment warning"></div>
          <div class="zone-segment danger"></div>
          <div class="zone-indicator" :style="{ left: riskPosition + '%' }"></div>
        </div>
        <span class="zone-text" :class="riskLevel">{{ riskLabel }}</span>
      </div>
    </div>

    <!-- 指标卡片网格 -->
    <div class="analysis-cards">
      <div
        v-for="(metric, idx) in metrics"
        :key="idx"
        class="metric-card"
        :class="getSignalClass(metric)"
      >
        <!-- 卡片标题 -->
        <div class="card-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <component :is="getIconComponent(metric.iconType)" />
          </svg>
          <span>{{ metric.name }}</span>
          <span class="title-period">{{ metric.period }}</span>
        </div>

        <!-- 卡片主体 -->
        <div class="card-body">
          <!-- 左侧区域 -->
          <div class="left-section">
            <!-- 信号灯和数值 -->
            <div class="signal-row">
              <div class="signal-light" :class="getSignalClass(metric)"></div>
              <div class="metric-value" :class="getValueClass(metric)">{{ metric.value }}</div>
            </div>

            <!-- 进度条 -->
            <div class="value-progress-bar">
              <div class="progress-track" :class="getTrackClass(metric)">
                <div v-if="metric.isBeta" class="progress-center-line"></div>
                <div v-if="metric.name === '年化收益' || metric.iconType === 'return'" class="progress-center-line"></div>
                <div class="progress-clip" :style="getClipStyle(metric)">
                  <div class="progress-fill" :style="{ width: '100%', background: getFillGradient(metric) }"></div>
                </div>
                <div class="progress-indicator" :style="{ left: getProgressWidth(metric) + '%', background: getIndicatorColor(metric) }"></div>
              </div>
              <div class="progress-markers">
                <span v-for="(marker, i) in metric.markers" :key="i">{{ marker }}</span>
              </div>
            </div>

            <!-- 基线和趋势 -->
            <div class="metric-baseline" :style="{ color: getBaselineColor(metric) }">
              <span class="baseline-dir" :class="metric.baselineDir">
                {{ metric.baselineDir === 'up' ? '▲' : metric.baselineDir === 'down' ? '▼' : '●' }}
              </span>
              <span class="baseline-text">{{ metric.baselineText }}</span>
            </div>
            <div class="metric-trend" :class="'trend-' + getTrend(metric)" :style="{ color: getBaselineColor(metric), background: getTrendBackground(metric) }">
              <span class="trend-text">{{ getTrendLabel(metric) }}</span>
              <!-- 勾：stable / up -->
              <svg v-if="getTrend(metric) === 'stable' || getTrend(metric) === 'up'" class="trend-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              <!-- 警告三角：unstable -->
              <svg v-else-if="getTrend(metric) === 'unstable'" class="trend-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M12 9v4"></path>
                <path d="M12 17h.01"></path>
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              </svg>
              <!-- 叉：down -->
              <svg v-else class="trend-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </div>
          </div>

          <!-- 右侧区域 -->
          <div class="right-section">
            <div class="sparkline-container">
              <svg viewBox="0 0 80 40" preserveAspectRatio="none" class="sparkline-chart">
                <line class="sparkline-ref-line" x1="0" :y1="20" x2="80" y2="20" stroke="#b0b3bc" stroke-width="0.8" stroke-dasharray="3,3" opacity="0.8"/>
                <rect :x="getSparklineHighPoint(metric).x - 5" :y="getSparklineHighPoint(metric).y - 3" width="10" height="10" :fill="getSparklineHighColor(metric)" rx="2"/>
                <rect :x="getSparklineLowPoint(metric).x - 5" :y="getSparklineLowPoint(metric).y - 3" width="10" height="10" :fill="getSparklineLowColor(metric)" rx="2"/>
                <polyline :points="metric.sparklinePoints" fill="none" stroke="#d1d4dc" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <circle class="sparkline-endpoint" :cx="getEndPoint(metric).x" :cy="getEndPoint(metric).y" r="2" fill="#d1d4dc"/>
              </svg>
            </div>
            <div class="metric-hint">{{ metric.hint }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { h, computed } from 'vue'

interface Metric {
  name: string
  value: string
  period: string
  hint: string
  iconType: 'volatility' | 'beta' | 'drawdown' | 'turnover' | 'return' | 'tracking'
  rawValue: number
  isBeta?: boolean
  isDrawdown?: boolean
  /** 指标方向：lower-better=越低越好, higher-better=越高越好, neutral=接近基准最好 */
  direction?: 'lower-better' | 'higher-better' | 'neutral'
  markers: string[]
  baselineDir: 'up' | 'down' | 'neutral'
  baselineText: string
  trend: 'up' | 'down' | 'stable' | 'unstable'
  trendLabel: string
  sparklinePoints: string
}

interface Props {
  title?: string
  metrics?: Metric[]
  /** 整体风险位置 0-100，不传则自动计算 */
  riskPositionOverride?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '组合分析指标',
  metrics: () => [
    {
      name: '波动率',
      value: '18.5%',
      period: '60日年化',
      hint: '↓ 越低越好',
      iconType: 'volatility',
      rawValue: 18.5,
      direction: 'lower-better',
      markers: ['0', '15%', '30%'],
      baselineDir: 'down',
      baselineText: '低于均值',
      trend: 'stable',
      trendLabel: '稳定',
      sparklinePoints: '5,20 15,18 25,25 35,15 45,22 55,17 65,20 75,18'
    },
    {
      name: 'Beta',
      value: '1.12',
      period: '沪深300',
      hint: '≈ 1 为宜',
      iconType: 'beta',
      rawValue: 1.12,
      isBeta: true,
      direction: 'neutral',
      markers: ['0.5', '1.0', '1.5'],
      baselineDir: 'up',
      baselineText: '略高于1',
      trend: 'unstable',
      trendLabel: '注意',
      sparklinePoints: '5,20 15,18 25,22 35,20 45,19 55,21 65,20 75,20'
    },
    {
      name: '最大回撤',
      value: '-8.2%',
      period: '历史最大',
      hint: '↓ 越小越好',
      iconType: 'drawdown',
      rawValue: 8.2,
      isDrawdown: true,
      direction: 'lower-better',
      markers: ['0', '-10%', '-20%'],
      baselineDir: 'down',
      baselineText: '轻度回撤',
      trend: 'unstable',
      trendLabel: '注意',
      sparklinePoints: '5,15 15,18 25,12 35,20 45,16 55,14 65,18 75,15'
    },
    {
      name: '换手率',
      value: '42%',
      period: '近30天',
      hint: '~ 适中为宜',
      iconType: 'turnover',
      rawValue: 42,
      direction: 'neutral',
      markers: ['0', '50%', '100%'],
      baselineDir: 'neutral',
      baselineText: '正常交易区间',
      trend: 'up',
      trendLabel: '交易活跃',
      sparklinePoints: '5,22 15,18 25,20 35,16 45,24 55,18 65,20 75,22'
    },
    {
      name: '年化收益',
      value: '15.6%',
      period: '今年以来',
      hint: '↑ 越高越好',
      iconType: 'return',
      rawValue: 15.6,
      direction: 'higher-better',
      markers: ['-20%', '0%', '+20%'],
      baselineDir: 'up',
      baselineText: '正收益 +15.6%',
      trend: 'up',
      trendLabel: '正收益',
      sparklinePoints: '5,25 15,22 25,20 35,18 45,15 55,14 65,12 75,10'
    },
    {
      name: '跟踪误差',
      value: '3.5%',
      period: '60日',
      hint: '↓ 越低越好',
      iconType: 'tracking',
      rawValue: 3.5,
      direction: 'lower-better',
      markers: ['0', '3%', '6%'],
      baselineDir: 'neutral',
      baselineText: '适度分散',
      trend: 'stable',
      trendLabel: '稳定',
      sparklinePoints: '5,20 15,22 25,18 35,20 45,19 55,21 65,18 75,20'
    }
  ]
})

// ========== 整体风险区间计算 ==========
const riskPosition = computed(() => {
  // 如果传入覆盖值，直接使用
  if (props.riskPositionOverride !== undefined) {
    return props.riskPositionOverride
  }
  // 否则基于metrics自动计算
  let score = 0
  for (const m of props.metrics) {
    const progress = getProgressWidth(m)
    if (progress >= 75) score += 20
    else if (progress >= 50) score += 10
  }
  return Math.min(score, 100)
})

const riskLevel = computed(() => {
  const pos = riskPosition.value
  if (pos < 25) return 'safe'
  if (pos < 50) return 'caution'
  if (pos < 75) return 'warning'
  return 'danger'
})

const riskLabel = computed(() => {
  const labels: Record<string, string> = {
    safe: '低风险',
    caution: '中风险',
    warning: '高风险',
    danger: '危险'
  }
  return labels[riskLevel.value]
})

// 图标组件
const getIconComponent = (type: string) => {
  const icons: Record<string, any> = {
    volatility: () => h('polyline', { points: '22 12 18 12 15 21 9 3 6 12 2 12' }),
    beta: () => [
      h('line', { x1: 18, y1: 20, x2: 18, y2: 10 }),
      h('line', { x1: 12, y1: 20, x2: 12, y2: 4 }),
      h('line', { x1: 6, y1: 20, x2: 6, y2: 14 })
    ],
    drawdown: () => [
      h('polyline', { points: '23 18 13.5 8.5 8.5 13.5 1 6' }),
      h('polyline', { points: '17 18 23 18 23 12' })
    ],
    turnover: () => [
      h('polyline', { points: '23 4 23 10 17 10' }),
      h('path', { d: 'M20.49 15a9 9 0 1 1-2.12-9.36L23 10' })
    ],
    return: () => [
      h('line', { x1: 12, y1: 20, x2: 12, y2: 10 }),
      h('polyline', { points: '18 14 12 8 6 14' })
    ],
    tracking: () => [
      h('circle', { cx: 12, cy: 12, r: 10 }),
      h('line', { x1: 12, y1: 8, x2: 12, y2: 12 }),
      h('line', { x1: 12, y1: 16, x2: 12.01, y2: 16 })
    ]
  }
  return icons[type] || icons.volatility
}

// 获取信号等级（每个指标单独阈值）
const getSignalClass = (metric: Metric): string => {
  const progress = getProgressWidth(metric)

  // 年化收益: 正收益=无信号灯，负收益=绿色
  if (metric.name === '年化收益' || metric.iconType === 'return') {
    // 正收益不需要警告信号灯，负收益显示绿色
    return metric.rawValue >= 0 ? '' : 'signal-green'
  }

  // 最大回撤: 3%以下=蓝，3%-10%=黄，10%以上=紫
  if (metric.isDrawdown || metric.iconType === 'drawdown') {
    if (progress < 15) return 'signal-blue'
    if (progress < 50) return 'signal-yellow'
    return 'signal-purple'
  }

  // Beta: 接近1最好，使用距离中心的距离
  if (metric.isBeta || metric.iconType === 'beta') {
    const distanceFromCenter = Math.abs(progress - 50)
    if (distanceFromCenter < 15) return 'signal-blue'  // 接近中心
    if (distanceFromCenter < 40) return 'signal-yellow' // 偏离中心
    return 'signal-purple' // 远离中心
  }

  // 波动率: 50%以下=蓝，50%-75%=黄，75%以上=紫
  if (metric.name === '波动率' || metric.iconType === 'volatility') {
    if (progress < 50) return 'signal-blue'
    if (progress < 75) return 'signal-yellow'
    return 'signal-purple'
  }

  // 换手率: 50%以下=蓝，50%-75%=黄，75%以上=紫
  if (metric.name === '换手率' || metric.iconType === 'turnover') {
    if (progress < 50) return 'signal-blue'
    if (progress < 75) return 'signal-yellow'
    return 'signal-purple'
  }

  // 跟踪误差: 50%以下=蓝，50%-75%=黄，75%以上=紫
  if (metric.name === '跟踪误差' || metric.iconType === 'tracking') {
    if (progress < 50) return 'signal-blue'
    if (progress < 75) return 'signal-yellow'
    return 'signal-purple'
  }

  // 默认: 50%以下=蓝，50%-75%=黄，75%以上=紫
  if (progress < 50) return 'signal-blue'
  if (progress < 75) return 'signal-yellow'
  return 'signal-purple'
}

// 获取数值样式类（与信号灯一致）
const getValueClass = (metric: Metric): string => {
  const signal = getSignalClass(metric)

  // 年化收益: 正收益=positive（红色），负收益=negative（绿色）
  if (metric.name === '年化收益' || metric.iconType === 'return') {
    return metric.rawValue >= 0 ? 'positive' : 'negative'
  }

  // 最大回撤数值颜色和指示器一致
  if (metric.isDrawdown || metric.iconType === 'drawdown') {
    const progress = getProgressWidth(metric)
    if (progress < 15) return 'drawdown-safe'
    if (progress < 50) return 'drawdown-warning'
    return 'drawdown-danger'
  }

  // Beta: 使用距离中心的距离
  if (metric.isBeta || metric.iconType === 'beta') {
    const progress = getProgressWidth(metric)
    const distanceFromCenter = Math.abs(progress - 50)
    if (distanceFromCenter >= 40) return 'loss' // 远离中心=紫色
    if (distanceFromCenter >= 15) return 'warning' // 偏离中心=黄色
    return 'profit' // 接近中心=蓝色
  }

  // 其他: 根据信号灯
  if (signal === 'signal-blue') return 'profit'
  if (signal === 'signal-purple') return 'loss'
  if (signal === 'signal-yellow') return 'warning'
  return ''
}

// 获取进度条轨道类
const getTrackClass = (metric: Metric): string => {
  if (metric.isBeta) return 'beta-track'
  if (metric.isDrawdown) return 'drawdown-track'
  if (metric.name === '年化收益' || metric.iconType === 'return') return 'return-track'
  return ''
}

// 根据指标类型计算进度百分比（基于 markers 计算）
const getMetricPercent = (metric: Metric): number => {
  const raw = metric.rawValue

  // 获取 markers 中的最大值
  const getMaxMarker = () => {
    const lastMarker = metric.markers[metric.markers.length - 1]
    // 移除百分号并转为数字
    return parseFloat(lastMarker.replace('%', '')) || 100
  }

  // 年化收益: -20%到+20%范围，0%在中间（50%位置）
  // 计算公式：(rawValue + 20) / 40 * 100
  if (metric.name === '年化收益' || metric.iconType === 'return') {
    return Math.min(Math.max((raw + 20) * 2.5, 0), 100)
  }

  // Beta: 范围 0.5 到 1.5
  if (metric.isBeta || metric.iconType === 'beta') {
    // 0.5 = 0%, 1.0 = 50%, 1.5 = 100%
    return Math.min(Math.max((raw - 0.5) * 100, 0), 100)
  }

  // 最大回撤: 0-20% 映射到 0-100%
  if (metric.isDrawdown || metric.iconType === 'drawdown') {
    return Math.min((raw / 20) * 100, 100)
  }

  // 其他指标: 基于 markers 最大值计算
  const maxMarker = getMaxMarker()
  return Math.min((raw / maxMarker) * 100, 100)
}

// 获取进度条宽度（保留用于兼容性）
const getProgressWidth = (metric: Metric): number => {
  return getMetricPercent(metric)
}

// 获取clip样式（年化收益从中间开始）
const getClipStyle = (metric: Metric): Record<string, string> => {
  const progress = getProgressWidth(metric)

  // 年化收益特殊处理：从中间（50%）开始
  if (metric.name === '年化收益' || metric.iconType === 'return') {
    if (progress < 50) {
      // 负收益：从中间往左延伸
      return {
        left: progress + '%',
        width: (50 - progress) + '%'
      }
    } else {
      // 正收益：从中间往右延伸
      return {
        left: '50%',
        width: (progress - 50) + '%'
      }
    }
  }

  // Beta特殊处理：从中间（50%）开始
  if (metric.isBeta || metric.iconType === 'beta') {
    if (progress < 50) {
      // 小于1.0：从中间往左延伸
      return {
        left: progress + '%',
        width: (50 - progress) + '%'
      }
    } else {
      // 大于1.0：从中间往右延伸
      return {
        left: '50%',
        width: (progress - 50) + '%'
      }
    }
  }

  // 默认：从左边开始
  return {
    left: '0%',
    width: progress + '%'
  }
}

// 获取填充宽度（补偿渐变）
const getFillWidth = (metric: Metric): string => {
  const progress = getProgressWidth(metric)
  if (progress <= 0) return '0%'
  if (progress >= 100) return '100%'
  return (10000 / progress) + '%'
}

// 获取进度条填充渐变（根据当前位置动态生成）
const getFillGradient = (metric: Metric): string => {
  const progress = getProgressWidth(metric)

  // 年化收益特殊处理：从中间（50%）分开
  if (metric.name === '年化收益' || metric.iconType === 'return') {
    if (progress < 50) {
      // 负收益区域：只显示绿色
      return `#26a69a`
    } else {
      // 正收益区域：只显示红色
      return `#ef5350`
    }
  }

  // Beta 特殊处理：从中间分开蓝→黄→紫，两边都是
  if (metric.isBeta) {
    // 计算距离中心的距离
    const distanceFromCenter = Math.abs(progress - 50)
    if (distanceFromCenter < 15) {
      return `#3b82f6` // 接近中心=蓝色
    } else if (distanceFromCenter < 40) {
      return `#ff9800` // 偏离中心=黄色
    } else {
      return `#8b5cf6` // 远离中心=紫色
    }
  }

  // 根据指标类型确定颜色阈值
  let thresholds: number[] = [50, 75] // 默认阈值

  // 最大回撤: 15%, 50%
  if (metric.isDrawdown) {
    thresholds = [15, 50]
  }

  // 根据当前位置生成渐变
  const colors: string[] = []
  let currentPos = 0

  // 遍历每个阈值，添加对应颜色的渐变段
  for (let i = 0; i < thresholds.length + 1; i++) {
    const nextPos = i < thresholds.length ? thresholds[i] : 100

    if (progress > currentPos) {
      const endPos = Math.min(progress, nextPos)

      // 根据当前段确定颜色
      let color = '#3b82f6' // 蓝色
      if (i === 1) color = '#ff9800' // 黄色
      if (i >= 2) color = '#8b5cf6' // 紫色

      colors.push(`${color} ${currentPos}% ${endPos}%`)
    }
    currentPos = nextPos

    if (progress <= currentPos) break
  }

  // 构建渐变字符串
  if (colors.length === 0) return '#3b82f6'
  if (colors.length === 1) return colors[0].split(' ')[0]

  return `linear-gradient(to right, ${colors.join(', ')})`
}

// 获取进度条填充颜色（单一颜色，用于滑块）
const getFillColor = (metric: Metric): string => {
  const signalClass = getSignalClass(metric)
  if (signalClass === 'signal-blue') return '#3b82f6'  // 蓝色-安全
  if (signalClass === 'signal-yellow') return '#ff9800' // 黄色-注意
  if (signalClass === 'signal-purple') return '#8b5cf6'  // 紫色-危险
  if (signalClass === 'signal-green') return '#26a69a'  // 绿色-负收益
  if (signalClass === 'signal-red') return '#ef5350'    // 红色-正收益
  return '#3b82f6'
}

// 获取指示器颜色
const getIndicatorColor = (metric: Metric): string => {
  const signalClass = getSignalClass(metric)

  // 年化收益特殊处理
  if (metric.name === '年化收益' || metric.iconType === 'return') {
    if (metric.rawValue >= 0) return '#ef5350' // 正收益=红色
    return '#26a69a' // 负收益=绿色
  }

  if (signalClass === 'signal-blue') return '#3b82f6'
  if (signalClass === 'signal-yellow') return '#ff9800'
  if (signalClass === 'signal-purple') return '#8b5cf6'
  if (signalClass === 'signal-green') return '#26a69a'
  if (signalClass === 'signal-red') return '#ef5350'
  return '#3b82f6'
}

// 获取baseline区域颜色（与指示器一致）
const getBaselineColor = (metric: Metric): string => {
  // 年化收益
  if (metric.name === '年化收益' || metric.iconType === 'return') {
    return metric.rawValue >= 0 ? '#ef5350' : '#26a69a'
  }
  // 最大回撤
  if (metric.isDrawdown || metric.iconType === 'drawdown') {
    const progress = getProgressWidth(metric)
    if (progress < 15) return '#3b82f6'
    if (progress < 50) return '#ff9800'
    return '#8b5cf6'
  }
  // Beta
  if (metric.isBeta || metric.iconType === 'beta') {
    const distanceFromCenter = Math.abs(getProgressWidth(metric) - 50)
    if (distanceFromCenter < 15) return '#3b82f6' // 接近中心=蓝色
    if (distanceFromCenter < 40) return '#ff9800' // 偏离中心=黄色
    return '#8b5cf6' // 远离中心=紫色
  }
  // 其他指标
  const progress = getProgressWidth(metric)
  if (progress < 50) return '#3b82f6'
  if (progress < 75) return '#ff9800'
  return '#8b5cf6'
}

// 获取趋势区域背景色（与指示器一致但更淡）
const getTrendBackground = (metric: Metric): string => {
  const color = getBaselineColor(metric)
  // 将 hex 颜色转为 rgba 背景
  const r = parseInt(color.slice(1, 3), 16)
  const g = parseInt(color.slice(3, 5), 16)
  const b = parseInt(color.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, 0.15)`
}

// 解析 sparklinePoints
const parseSparklinePoints = (pointsStr: string): { x: number; y: number }[] => {
  if (!pointsStr) return []
  return pointsStr.split(' ').map(point => {
    const [x, y] = point.split(',').map(Number)
    return { x, y }
  })
}

// 获取最高点
const getSparklineHighPoint = (metric: Metric): { x: number; y: number } => {
  const points = parseSparklinePoints(metric.sparklinePoints)
  if (points.length === 0) return { x: 40, y: 10 }
  let high = points[0]
  for (const p of points) {
    if (p.y < high.y) high = p
  }
  return high
}

// 获取最低点
const getSparklineLowPoint = (metric: Metric): { x: number; y: number } => {
  const points = parseSparklinePoints(metric.sparklinePoints)
  if (points.length === 0) return { x: 40, y: 30 }
  let low = points[0]
  for (const p of points) {
    if (p.y > low.y) low = p
  }
  return low
}

// 获取终点
const getEndPoint = (metric: Metric): { x: number; y: number } => {
  const points = parseSparklinePoints(metric.sparklinePoints)
  if (points.length === 0) return { x: 75, y: 20 }
  return points[points.length - 1]
}

// 动态获取趋势状态
const getTrend = (metric: Metric): string => {
  const progress = getProgressWidth(metric)
  const signal = getSignalClass(metric)

  // 年化收益: 正收益=稳定，负收益=注意
  if (metric.name === '年化收益' || metric.iconType === 'return') {
    if (metric.rawValue >= 0) return 'stable' // 正收益
    return 'unstable' // 负收益
  }

  // Beta: 根据距离中心的距离计算
  if (metric.isBeta || metric.iconType === 'beta') {
    const distanceFromCenter = Math.abs(progress - 50)
    if (distanceFromCenter < 15) return 'stable' // 接近中心
    return 'unstable' // 偏离或远离中心
  }

  // 根据信号灯颜色判断：蓝色=稳定，黄色/紫色=注意
  if (signal === 'signal-blue') return 'stable'
  return 'unstable'
}

// 动态获取趋势标签
const getTrendLabel = (metric: Metric): string => {
  const progress = getProgressWidth(metric)
  const signal = getSignalClass(metric)

  // 年化收益: 正收益=稳定，负收益=注意
  if (metric.name === '年化收益' || metric.iconType === 'return') {
    if (metric.rawValue >= 0) return '稳定' // 正收益
    return '注意' // 负收益
  }

  // Beta: 根据距离中心的距离计算
  if (metric.isBeta || metric.iconType === 'beta') {
    const distanceFromCenter = Math.abs(progress - 50)
    if (distanceFromCenter < 15) return '稳定' // 接近中心
    return '注意' // 偏离或远离中心
  }

  // 根据信号灯颜色判断：蓝色=稳定，黄色/紫色=注意
  if (signal === 'signal-blue') return '稳定'
  return '注意'
}

// 获取走势图高点颜色（统一：高区域=红色）
const getSparklineHighColor = (metric: Metric): string => {
  return 'rgba(239, 83, 80, 0.4)' // 红色
}

// 获取走势图低点颜色（统一：低区域=绿色）
const getSparklineLowColor = (metric: Metric): string => {
  return 'rgba(38, 166, 154, 0.4)' // 绿色
}
</script>

<style lang="scss" scoped>
.portfolio-analysis-section {
  background: #131722;
  border-radius: 8px;
  overflow: visible;
  margin: 16px 20px 20px;
  padding: 0;

  @media (max-width: 1200px) {
    margin: 16px 16px 20px;
  }

  @media (max-width: 768px) {
    margin: 16px 12px 20px;
  }
}

.section-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #d1d4dc;

  .title-icon {
    width: 18px;
    height: 18px;
    color: #409EFF;
  }
}

// 整体风险区间条
.overall-risk-zone {
  display: flex;
  align-items: center;
  gap: 10px;

  .zone-label {
    font-size: 11px;
    color: #787b86;
  }

  .zone-bar {
    width: 120px;
    height: 8px;
    border-radius: 4px;
    display: flex;
    overflow: hidden;
    position: relative;

    .zone-segment {
      flex: 1;
      &.safe { background: #3b82f6; }
      &.caution { background: #ff9800; }
      &.warning { background: #8b5cf6; }
      &.danger { background: #8b5cf6; }
    }

    .zone-indicator {
      position: absolute;
      top: -4px;
      width: 4px;
      height: 16px;
      background: #fff;
      border-radius: 2px;
      box-shadow: 0 0 6px rgba(255,255,255,0.5);
      transition: left 0.5s ease;
    }
  }

  .zone-text {
    font-size: 11px;
    font-weight: 600;
    &.safe { color: #3b82f6; }
    &.caution { color: #ff9800; }
    &.warning { color: #ff5722; }
    &.danger { color: #8b5cf6; }
  }
}

.analysis-cards {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  padding: 16px;
}

.metric-card {
  background: #1e222d;
  border: 2px solid #2a2e39;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;

  &.signal-yellow {
    border-color: rgba(255, 152, 0, 0.8);
    box-shadow: 0 0 12px rgba(255, 152, 0, 0.3), inset 0 0 20px rgba(255, 152, 0, 0.05);
    background: linear-gradient(135deg, rgba(255, 152, 0, 0.08) 0%, #1e222d 100%);
  }

  &.signal-red {
    border-color: rgba(244, 67, 54, 0.8);
    box-shadow: 0 0 12px rgba(244, 67, 54, 0.3), inset 0 0 20px rgba(244, 67, 54, 0.05);
    background: linear-gradient(135deg, rgba(244, 67, 54, 0.08) 0%, #1e222d 100%);
  }
}

.card-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding-bottom: 8px;
  border-bottom: 1px solid #2a2e39;
  margin-bottom: 8px;

  .title-icon {
    width: 14px;
    height: 14px;
    color: #d1d4dc;
  }

  span:nth-child(2) {
    font-size: 12px;
    font-weight: 500;
    color: #d1d4dc;
  }

  .title-period {
    font-size: 9px;
    color: #787b86;
    background: #2a2e39;
    padding: 1px 4px;
    border-radius: 3px;
  }
}

.card-body {
  display: flex;
  gap: 10px;
  flex: 1;
  min-height: 85px;
}

.left-section {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 0 0 auto;
  width: clamp(80px, 30%, 100px);
  min-width: 70px;
}

.signal-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.signal-light {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;

  &.signal-blue {
    background: #3b82f6;
    box-shadow: 0 0 8px #3b82f6;
    animation: pulse-blue 2s infinite;
  }

  &.signal-yellow {
    background: #ff9800;
    box-shadow: 0 0 8px #ff9800;
    animation: pulse-yellow 2s infinite;
  }

  &.signal-purple {
    background: #8b5cf6;
    box-shadow: 0 0 8px #8b5cf6;
    animation: pulse-purple 1.5s infinite;
  }

  &.signal-green {
    background: #26a69a;
    box-shadow: 0 0 8px #26a69a;
    animation: pulse-green 2s infinite;
  }

  &.signal-red {
    background: #ef5350;
    box-shadow: 0 0 8px #ef5350;
    animation: pulse-red 1.5s infinite;
  }
}

@keyframes pulse-blue {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes pulse-yellow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes pulse-purple {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px #8b5cf6; }
  50% { opacity: 0.8; box-shadow: 0 0 16px #8b5cf6; }
}

@keyframes pulse-green {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes pulse-red {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px #ef5350; }
  50% { opacity: 0.8; box-shadow: 0 0 16px #ef5350; }
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: #d1d4dc;

  // 大多数指标：蓝色=安全，紫色=危险
  &.profit { color: #3b82f6; }
  &.loss { color: #8b5cf6; }
  &.warning { color: #ff9800; }  // 黄色-警戒

  // 年化收益专用：红色=正收益，绿色=负收益
  &.positive { color: #ef5350; }
  &.negative { color: #26a69a; }

  // 最大回撤专用：数值颜色和指示器一致
  &.drawdown-safe { color: #3b82f6; }    // 蓝色-安全
  &.drawdown-warning { color: #ff9800; }  // 黄色-注意
  &.drawdown-danger { color: #8b5cf6; }   // 紫色-危险
}

.value-progress-bar {
  margin: 2px 0;

  .progress-track {
    height: 6px;
    border-radius: 3px;
    position: relative;
    // 颜色分区：蓝(0-50%)→黄(50-75%)→紫(75-100%)
    background: linear-gradient(to right,
      rgba(59, 130, 246, 0.2) 0%,
      rgba(59, 130, 246, 0.2) 50%,
      rgba(255, 152, 0, 0.2) 50%,
      rgba(255, 152, 0, 0.2) 75%,
      rgba(139, 92, 246, 0.2) 75%,
      rgba(139, 92, 246, 0.2) 100%
    );

    .progress-center-line {
      position: absolute;
      left: 50%;
      top: 0;
      bottom: 0;
      width: 2px;
      background: rgba(255, 255, 255, 0.6);
      z-index: 2;
    }

    .progress-clip {
      position: absolute;
      top: 0;
      left: 0;
      height: 100%;
      border-radius: 3px;
      overflow: hidden;
      z-index: 1;

      .progress-fill {
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        border-radius: 2px;
      }
    }

    // 最大回撤专用
    &.drawdown-track {
      background: linear-gradient(to right,
        rgba(59, 130, 246, 0.2) 0%,
        rgba(59, 130, 246, 0.2) 15%,
        rgba(255, 152, 0, 0.2) 15%,
        rgba(255, 152, 0, 0.2) 50%,
        rgba(139, 92, 246, 0.2) 50%,
        rgba(139, 92, 246, 0.2) 100%
      );
      .progress-clip .progress-fill {
        background: linear-gradient(to right,
          #3b82f6 0%,
          #3b82f6 15%,
          #ff9800 15%,
          #ff9800 50%,
          #8b5cf6 50%,
          #8b5cf6 100%
        );
      }
    }

    // Beta专用：从中间分开，两边颜色对称
    &.beta-track {
      background: linear-gradient(to right,
        rgba(139, 92, 246, 0.2) 0%,
        rgba(139, 92, 246, 0.2) 15%,
        rgba(255, 152, 0, 0.2) 15%,
        rgba(255, 152, 0, 0.2) 35%,
        rgba(59, 130, 246, 0.2) 35%,
        rgba(59, 130, 246, 0.2) 65%,
        rgba(255, 152, 0, 0.2) 65%,
        rgba(255, 152, 0, 0.2) 85%,
        rgba(139, 92, 246, 0.2) 85%,
        rgba(139, 92, 246, 0.2) 100%
      );
      .progress-clip .progress-fill {
        background: linear-gradient(to right,
          #8b5cf6 0%,
          #8b5cf6 15%,
          #ff9800 15%,
          #ff9800 35%,
          #3b82f6 35%,
          #3b82f6 65%,
          #ff9800 65%,
          #ff9800 85%,
          #8b5cf6 85%,
          #8b5cf6 100%
        );
      }
    }

    // 年化收益专用：从中间分开，左边绿色（负收益），右边红色（正收益）
    &.return-track {
      background: linear-gradient(to right,
        rgba(38, 166, 154, 0.2) 0%,
        rgba(38, 166, 154, 0.2) 45%,
        rgba(120, 123, 134, 0.15) 45%,
        rgba(120, 123, 134, 0.15) 55%,
        rgba(239, 83, 80, 0.2) 55%,
        rgba(239, 83, 80, 0.2) 100%
      );
    }

    .progress-indicator {
      position: absolute;
      top: -4px;
      width: 3px;
      height: 14px;
      border-radius: 2px;
      transform: translateX(-50%);
      transition: left 0.3s ease;
      z-index: 3;
    }
  }

  .progress-markers {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
    font-size: 9px;
    color: #575e6a;
  }
}

.metric-baseline {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  color: #d1d4dc;

  .baseline-dir {
    font-size: 8px;

    &.up { color: #8b5cf6; }
    &.down { color: #3b82f6; }
    &.neutral { color: #d1d4dc; }
  }

  .baseline-text {
    color: #d1d4dc;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.metric-trend {
  display: inline-block;
  font-size: 9px;
  font-weight: 500;
  padding: 1px 4px;
  border-radius: 4px;

  .trend-icon {
    width: 9px;
    height: 9px;
    margin-left: 3px;
    vertical-align: middle;
  }

  &.trend-stable {
    color: #3b82f6;
  }

  &.trend-up {
    color: #8b5cf6;
  }

  &.trend-down {
    color: #3b82f6;
  }

  &.trend-unstable {
    color: #ff9800;
  }
}

.right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  min-width: 50px;
  padding-bottom: 2px;

  .sparkline-container {
    position: relative;
    width: 100%;
    flex: 1;

    .sparkline-chart {
      width: 100%;
      height: 100%;
      overflow: visible;
    }
  }
}

.sparkline-ref-line {
  stroke: #b0b3bc;
  stroke-width: 0.8;
  stroke-dasharray: 3,3;
}

.sparkline-endpoint {
  fill: #d1d4dc;
}

.metric-hint {
  font-size: 9px;
  color: #787b86;
  margin-top: 4px;
}

// 响应式
@media (max-width: 1400px) {
  .analysis-cards { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 900px) {
  .analysis-cards { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
  .analysis-cards { grid-template-columns: 1fr; }
}
</style>
