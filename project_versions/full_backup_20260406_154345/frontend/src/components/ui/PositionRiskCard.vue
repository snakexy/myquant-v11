<template>
  <div class="position-risk-section">
    <!-- 头部 -->
    <div class="position-risk-header">
      <div class="section-header">
        <div class="section-title">
          <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          <span>{{ title }}</span>
        </div>
      </div>
    </div>

    <!-- 指标卡片行 -->
    <div class="key-metrics-row">
      <!-- VaR 仪表盘 -->
      <div
        v-for="(metric, idx) in metrics"
        :key="idx"
        class="metric-card gauge-card enhanced"
        :class="getSignalClass(metric)"
      >
        <div class="gauge-header">
          <div class="gauge-icon" :class="metric.iconClass">
            <component :is="getIconComponent(metric.iconType)" />
          </div>
          <div class="gauge-title-row">
            <div class="gauge-title-left">
              <span class="gauge-title">{{ metric.name }}</span>
              <div class="signal-light" :class="getSignalClass(metric)"></div>
            </div>
            <span class="metric-hint">{{ metric.hint }}</span>
          </div>
        </div>
        <div class="gauge-main">
          <div class="gauge-value-row">
            <div class="gauge-value" :class="getLevelClass(metric)">{{ metric.value }}</div>
            <div class="gauge-sparkline-mini">
              <svg viewBox="0 0 150 60" preserveAspectRatio="none" class="sparkline-chart-mini">
                <line class="sparkline-avg-line" x1="0" :y1="30" x2="150" y2="30" stroke="#b0b3bc" stroke-width="0.8" stroke-dasharray="3,3" opacity="0.8"/>
                <rect :x="getSparklineHighPoint(metric).x" :y="getSparklineHighPoint(metric).y" width="12" height="12" fill="rgba(244,67,54,0.4)" rx="2"/>
                <rect :x="getSparklineLowPoint(metric).x" :y="getSparklineLowPoint(metric).y" width="12" height="12" fill="rgba(38,166,154,0.4)" rx="2"/>
                <polyline :points="metric.sparklinePoints || defaultSparklinePoints" fill="none" stroke="#d1d4dc" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <circle class="sparkline-endpoint" :cx="getSparklineEndPoint(metric).x" :cy="getSparklineEndPoint(metric).y" r="3" fill="#d1d4dc"/>
              </svg>
            </div>
          </div>
          <div class="gauge-bar-wrapper">
            <div class="gauge-bar">
              <div class="gauge-fill" :style="{ width: getBarWidth(metric) + '%' }" :class="getLevelClass(metric)"></div>
            </div>
            <div class="gauge-scale">
              <span>低</span>
              <span>中</span>
              <span>高</span>
              <span>危</span>
            </div>
          </div>
        </div>
        <div class="gauge-status">
          <div class="metric-baseline">
            <span class="baseline-dir" :class="metric.baselineDir">
              {{ metric.baselineDir === 'up' ? '▲' : metric.baselineDir === 'down' ? '▼' : '●' }}
            </span>
            <span>{{ metric.baselineText }}</span>
          </div>
          <div class="metric-trend" :class="metric.trend">{{ metric.trendLabel }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue'

interface Metric {
  name: string
  value: string
  hint: string
  iconType: 'var' | 'cvar' | 'drawdown' | 'beta' | 'volatility'
  iconClass: string
  rawValue: number
  thresholds: { low: number; medium: number; high: number }
  baselineDir: 'up' | 'down' | 'neutral'
  baselineText: string
  trend: 'stable' | 'rising' | 'falling'
  trendLabel: string
  sparklinePoints?: string
  sparklineHigh?: { x: number; y: number }
  sparklineLow?: { x: number; y: number }
}

interface Props {
  title?: string
  metrics?: Metric[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '持仓风险指标',
  metrics: () => [
    {
      name: 'VaR(95%)',
      value: '2.50%',
      hint: '↓ 越低越好',
      iconType: 'var',
      iconClass: 'var-icon',
      rawValue: 25,
      thresholds: { low: 50, medium: 75, high: 100 },
      baselineDir: 'down',
      baselineText: '低于均值',
      trend: 'stable',
      trendLabel: '稳定',
      sparklinePoints: '10,30 30,25 50,35 70,20 90,28 110,22',
      sparklineHigh: { x: 65, y: 15 },
      sparklineLow: { x: 45, y: 35 }
    },
    {
      name: 'CVaR(95%)',
      value: '3.20%',
      hint: '↓ 越低越好',
      iconType: 'cvar',
      iconClass: 'cvar-icon',
      rawValue: 32,
      thresholds: { low: 50, medium: 75, high: 100 },
      baselineDir: 'neutral',
      baselineText: '接近VaR',
      trend: 'stable',
      trendLabel: '稳定',
      sparklinePoints: '10,25 30,30 50,22 70,28 90,18 110,24',
      sparklineHigh: { x: 85, y: 12 },
      sparklineLow: { x: 45, y: 32 }
    },
    {
      name: '当前回撤',
      value: '3.50%',
      hint: '↓ 越低越好',
      iconType: 'drawdown',
      iconClass: 'drawdown-icon',
      rawValue: 35,
      thresholds: { low: 50, medium: 75, high: 100 },
      baselineDir: 'down',
      baselineText: '轻度回撤',
      trend: 'stable',
      trendLabel: '稳定',
      sparklinePoints: '10,20 30,28 50,25 70,32 90,26 110,30',
      sparklineHigh: { x: 65, y: 28 },
      sparklineLow: { x: 5, y: 16 }
    },
    {
      name: 'Beta',
      value: '1.05',
      hint: '≈ 1 为宜',
      iconType: 'beta',
      iconClass: 'beta-icon',
      rawValue: 52,
      thresholds: { low: 50, medium: 75, high: 100 },
      baselineDir: 'neutral',
      baselineText: '接近基准',
      trend: 'stable',
      trendLabel: '稳定',
      sparklinePoints: '10,24 30,22 50,26 70,24 90,25 110,24',
      sparklineHigh: { x: 45, y: 22 },
      sparklineLow: { x: 25, y: 26 }
    },
    {
      name: '日波动率',
      value: '1.80%',
      hint: '↓ 越低越好',
      iconType: 'volatility',
      iconClass: 'volatility-icon',
      rawValue: 18,
      thresholds: { low: 50, medium: 75, high: 100 },
      baselineDir: 'down',
      baselineText: '低于均值',
      trend: 'stable',
      trendLabel: '稳定',
      sparklinePoints: '10,28 30,32 50,26 70,30 90,24 110,28',
      sparklineHigh: { x: 25, y: 28 },
      sparklineLow: { x: 85, y: 20 }
    }
  ]
})

const defaultSparklinePoints = '10,30 30,25 50,35 70,20 90,28 110,22'

// 图标组件
const getIconComponent = (type: string) => {
  const icons: Record<string, any> = {
    var: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('path', { d: 'M12 2L2 7l10 5 10-5-10-5z' }),
      h('path', { d: 'M2 17l10 5 10-5M2 12l10 5 10-5' })
    ]),
    cvar: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('polyline', { points: '22 12 18 12 15 21 9 3 6 12 2 12' })
    ]),
    drawdown: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('polyline', { points: '23 18 13.5 8.5 8.5 13.5 1 6' }),
      h('polyline', { points: '17 18 23 18 23 12' })
    ]),
    beta: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('circle', { cx: '12', cy: '12', r: '10' }),
      h('line', { x1: '12', y1: '8', x2: '12', y2: '12' }),
      h('line', { x1: '12', y1: '16', x2: '12.01', y2: '16' })
    ]),
    volatility: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
      h('polyline', { points: '22 12 18 12 15 21 9 3 6 12 2 12' })
    ])
  }
  return icons[type] || icons.var
}

// 获取信号等级
const getSignalClass = (metric: Metric): string => {
  const level = getLevel(metric)
  return level
}

// 获取等级
const getLevel = (metric: Metric): 'low' | 'medium' | 'high' | 'critical' => {
  const v = Math.abs(metric.rawValue)
  const { low, medium, high } = metric.thresholds
  if (v < low) return 'low'
  if (v < medium) return 'medium'
  if (v < high) return 'high'
  return 'critical'
}

// 获取等级类名
const getLevelClass = (metric: Metric): string => {
  return getLevel(metric)
}

// 获取进度条宽度
const getBarWidth = (metric: Metric): number => {
  const v = Math.abs(metric.rawValue)
  const { high } = metric.thresholds
  return Math.min((v / high) * 100, 100)
}

// 解析 sparklinePoints 字符串为坐标数组
const parseSparklinePoints = (pointsStr: string): { x: number; y: number }[] => {
  if (!pointsStr) return []
  return pointsStr.split(' ').map(point => {
    const [x, y] = point.split(',').map(Number)
    return { x, y }
  })
}

// 获取最高点位置（y值最小的点）
const getSparklineHighPoint = (metric: Metric): { x: number; y: number } => {
  const points = parseSparklinePoints(metric.sparklinePoints || defaultSparklinePoints)
  if (points.length === 0) return { x: 60, y: 10 }

  let highPoint = points[0]
  for (const point of points) {
    if (point.y < highPoint.y) {
      highPoint = point
    }
  }
  return { x: highPoint.x - 5, y: highPoint.y - 5 }
}

// 获取最低点位置（y值最大的点）
const getSparklineLowPoint = (metric: Metric): { x: number; y: number } => {
  const points = parseSparklinePoints(metric.sparklinePoints || defaultSparklinePoints)
  if (points.length === 0) return { x: 30, y: 35 }

  let lowPoint = points[0]
  for (const point of points) {
    if (point.y > lowPoint.y) {
      lowPoint = point
    }
  }
  return { x: lowPoint.x - 5, y: lowPoint.y - 5 }
}

// 获取终点位置
const getSparklineEndPoint = (metric: Metric): { x: number; y: number } => {
  const points = parseSparklinePoints(metric.sparklinePoints || defaultSparklinePoints)
  if (points.length === 0) return { x: 110, y: 20 }
  return points[points.length - 1]
}
</script>

<style lang="scss" scoped>
.position-risk-section {
  background: #131722;
  border-radius: 8px;
  overflow: hidden;
}

.position-risk-header {
  padding: 16px 20px 8px 20px;
  background: #131722;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 1px;
    background: #2a2e39;
  }
}

.section-header {
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

  .section-icon {
    width: 18px;
    height: 18px;
    color: #26a69a;
  }
}

.key-metrics-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 0 16px 16px 16px;
}

.metric-card {
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  padding: 14px;
  flex: 1;
  min-width: 180px;
  transition: all 0.3s;

  &.low {
    // 低风险不显示边框发光
  }

  &.medium {
    border-color: rgba(255, 152, 0, 0.8);
    box-shadow: 0 0 12px rgba(255, 152, 0, 0.3), inset 0 0 20px rgba(255, 152, 0, 0.05);
    background: linear-gradient(135deg, rgba(255, 152, 0, 0.08) 0%, #1e222d 100%);
  }

  &.high, &.critical {
    border-color: rgba(244, 67, 54, 0.8);
    box-shadow: 0 0 12px rgba(244, 67, 54, 0.3), inset 0 0 20px rgba(244, 67, 54, 0.05);
    background: linear-gradient(135deg, rgba(244, 67, 54, 0.08) 0%, #1e222d 100%);
  }
}

.gauge-card {
  flex-direction: column;
  align-items: stretch;
}

.gauge-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.gauge-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
  position: relative;

  svg {
    width: 18px;
    height: 18px;
  }

  &.var-icon { background: rgba(41, 98, 255, 0.15); svg { color: #2962ff; } }
  &.cvar-icon { background: rgba(239, 83, 80, 0.15); svg { color: #ef5350; } }
  &.drawdown-icon { background: rgba(38, 166, 154, 0.15); svg { color: #26a69a; } }
  &.beta-icon { background: rgba(255, 152, 0, 0.15); svg { color: #ff9800; } }
  &.volatility-icon { background: rgba(156, 39, 176, 0.15); svg { color: #9c27b0; } }
}

.gauge-title-row {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.gauge-title-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.gauge-title {
  font-size: 12px;
  font-weight: 600;
  color: #d1d4dc;
}

.signal-light {
  width: 8px;
  height: 8px;
  border-radius: 50%;

  &.low { background: #26a69a; box-shadow: 0 0 6px #26a69a; }
  &.medium { background: #ff9800; box-shadow: 0 0 6px #ff9800; }
  &.high { background: #f44336; box-shadow: 0 0 6px #f44336; }
  &.critical { background: #b71c1c; box-shadow: 0 0 6px #b71c1c; }
}

.metric-hint {
  font-size: 10px;
  color: #787b86;
}

.gauge-main {
  flex: 1;
}

.gauge-value-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.gauge-value {
  font-size: 22px;
  font-weight: 700;
  color: #d1d4dc;

  &.low { color: #26a69a; }
  &.medium { color: #8bc34a; }
  &.high { color: #ff9800; }
  &.critical { color: #f44336; }
}

.gauge-sparkline-mini {
  width: 160px;
  height: 64px;
}

.sparkline-chart-mini {
  width: 100%;
  height: 100%;
}

.sparkline-avg-line {
  stroke: #b0b3bc;
  stroke-width: 0.8;
  stroke-dasharray: 3,3;
}

.sparkline-endpoint {
  fill: #d1d4dc;
}

.gauge-bar-wrapper {
  margin-bottom: 8px;
}

.gauge-bar {
  width: 100%;
  height: 6px;
  background: #2a2e39;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.gauge-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;

  &.low { background: linear-gradient(90deg, #26a69a, #4caf50); }
  &.medium { background: linear-gradient(90deg, #8bc34a, #cddc39); }
  &.high { background: linear-gradient(90deg, #ff9800, #ffb300); }
  &.critical { background: linear-gradient(90deg, #f44336, #ff5722); }
}

.gauge-scale {
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: 9px;
  color: #787b86;

  span:nth-child(1) { color: #26a69a; }
  span:nth-child(2) { color: #8bc34a; }
  span:nth-child(3) { color: #ff9800; }
  span:nth-child(4) { color: #f44336; }
}

.gauge-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-baseline {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: #787b86;

  .baseline-dir {
    &.up { color: #ef5350; }
    &.down { color: #26a69a; }
    &.neutral { color: #787b86; }
  }
}

.metric-trend {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 4px;

  &.stable {
    background: rgba(38, 166, 154, 0.15);
    color: #26a69a;
  }

  &.rising {
    background: rgba(239, 83, 80, 0.15);
    color: #ef5350;
  }

  &.falling {
    background: rgba(38, 166, 154, 0.15);
    color: #26a69a;
  }
}
</style>
