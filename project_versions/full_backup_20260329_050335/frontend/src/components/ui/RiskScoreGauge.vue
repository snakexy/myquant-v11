<template>
  <div class="risk-score-gauge" :style="{ '--level-color': levelColor }">
    <!-- 仪表盘 -->
    <div class="gauge-container">
      <svg viewBox="0 0 200 120" class="gauge-svg">
        <!-- 背景弧 -->
        <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#2a2e39" stroke-width="20" stroke-linecap="round" opacity="0.7"/>
        <!-- 渐变背景 -->
        <defs>
          <linearGradient id="riskGradientBg" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#26a69a"/>
            <stop offset="35%" style="stop-color:#8bc34a"/>
            <stop offset="60%" style="stop-color:#ff9800"/>
            <stop offset="85%" style="stop-color:#f44336"/>
            <stop offset="100%" style="stop-color:#9c27b0"/>
          </linearGradient>
          <!-- 发光滤镜 -->
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#riskGradientBg)" stroke-width="16" stroke-linecap="round" opacity="0.2"/>
        <!-- 得分弧 - 带发光效果 -->
        <path :d="scoreArcPath" fill="none" :stroke="levelColor" stroke-width="10" stroke-linecap="round" filter="url(#glow)" opacity="0.85"/>
        <!-- 指针 - 带发光效果 -->
        <circle :cx="pointerPos.x" :cy="pointerPos.y" r="5" :fill="levelColor" filter="url(#glow)" opacity="0.9"/>
        <!-- 高光 - 模糊 -->
        <path :d="scoreArcPath" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" opacity="0.15" filter="url(#glow)"/>
      </svg>
      <!-- 分数显示 -->
      <div class="score-display">
        <span class="score-value" :style="{ color: levelColor }">{{ displayScore }}</span>
        <span class="score-max">/100</span>
      </div>
      <!-- 刻度标签 -->
      <div class="gauge-labels">
        <span class="gauge-label" :style="{ color: progress >= 0 ? '#26a69a' : '#575e6a' }">低</span>
        <span class="gauge-label" :style="{ color: progress >= 0.33 ? '#f7931a' : '#575e6a' }">中</span>
        <span class="gauge-label" :style="{ color: progress >= 0.66 ? '#ef5350' : '#575e6a' }">高</span>
        <span class="gauge-label" :style="{ color: progress >= 0.85 ? '#7b1fa2' : '#575e6a' }">危</span>
      </div>
    </div>

    <!-- 风险等级 -->
    <div class="score-level" :style="{ color: levelColor }">
      {{ levelText }}
    </div>

    <!-- 维度进度条 -->
    <div class="score-dimensions">
      <div class="dimension-item" v-for="dim in dimensions" :key="dim.name">
        <div class="dimension-header">
          <span class="dimension-name">{{ dim.name }}</span>
          <span class="dimension-score" :style="{ color: getDimensionColor(dim.score / dim.maxScore) }">
            {{ dim.score.toFixed(0) }}/{{ dim.maxScore }}
          </span>
        </div>
        <div class="dimension-bar">
          <div
            class="dimension-fill"
            :style="{
              width: `${(dim.score / dim.maxScore) * 100}%`,
              background: getDimensionGradient(dim.score / dim.maxScore)
            }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Dimension {
  name: string
  score: number
  maxScore: number
}

interface Props {
  score: number
  level?: string
  dimensions?: Dimension[]
}

const props = withDefaults(defineProps<Props>(), {
  score: 0,
  level: 'low',
  dimensions: () => [
    { name: '仓位风险', score: 15, maxScore: 25 },
    { name: '回撤风险', score: 12, maxScore: 25 },
    { name: 'VaR/CVaR', score: 18, maxScore: 25 },
    { name: 'Beta/因子', score: 10, maxScore: 25 }
  ]
})

// 计算进度 (0-1)
const progress = computed(() => props.score / 100)

// 计算风险等级
const riskLevel = computed(() => {
  const s = props.score
  if (s < 30) return 'low'
  if (s < 50) return 'medium'
  if (s < 70) return 'high'
  return 'critical'
})

// 根据位置动态计算颜色
const levelColor = computed(() => {
  const p = progress.value

  const colors = [
    { pos: 0.0, r: 38, g: 166, b: 154 },    // 绿色
    { pos: 0.25, r: 77, g: 182, b: 172 },   // 浅绿色
    { pos: 0.5, r: 247, g: 147, b: 26 },    // 橙色
    { pos: 0.65, r: 255, g: 87, b: 34 },    // 橘红色
    { pos: 0.8, r: 220, g: 53, b: 69 },     // 深红色
    { pos: 0.9, r: 176, g: 38, b: 88 },     // 玫红色
    { pos: 1.0, r: 123, g: 31, b: 162 }     // 深紫色
  ]

  let startColor = colors[0]
  let endColor = colors[colors.length - 1]

  for (let i = 0; i < colors.length - 1; i++) {
    if (p >= colors[i].pos && p <= colors[i + 1].pos) {
      startColor = colors[i]
      endColor = colors[i + 1]
      break
    }
  }

  const range = endColor.pos - startColor.pos
  const localProgress = range > 0 ? (p - startColor.pos) / range : 0

  const r = Math.round(startColor.r + (endColor.r - startColor.r) * localProgress)
  const g = Math.round(startColor.g + (endColor.g - startColor.g) * localProgress)
  const b = Math.round(startColor.b + (endColor.b - startColor.b) * localProgress)

  return `rgb(${r}, ${g}, ${b})`
})

// 风险等级文本
const levelText = computed(() => {
  const texts: Record<string, string> = {
    low: '低风险',
    medium: '中风险',
    high: '高风险',
    critical: '危险'
  }
  return texts[riskLevel.value] || '未知'
})

// 显示分数
const displayScore = computed(() => Math.round(props.score))

// 计算分数弧路径 - 从左(绿/低风险)向右(红/高风险)填充
const scoreArcPath = computed(() => {
  const s = props.score
  if (s <= 0) return ''

  const maxAngle = 180
  const angle = (Math.min(s, 100) / 100) * maxAngle

  // 从左侧(180°)开始，向右侧(0°)填充
  const startAngle = 180
  const endAngle = 180 - angle

  const radius = 80
  const cx = 100
  const cy = 100

  const startRad = (startAngle * Math.PI) / 180
  const endRad = (endAngle * Math.PI) / 180

  // 计算起点和终点坐标
  const x1 = cx + radius * Math.cos(startRad)
  const y1 = cy - radius * Math.sin(startRad)
  const x2 = cx + radius * Math.cos(endRad)
  const y2 = cy - radius * Math.sin(endRad)

  const largeArc = angle > 180 ? 1 : 0

  // 使用 sweep-flag=1 顺时针绘制上半圆弧
  return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`
})

// 计算指针位置 - 从左侧(180°)向右侧(0°)移动
const pointerPos = computed(() => {
  const s = props.score
  const maxAngle = 180
  const angle = 180 - (Math.min(s, 100) / 100) * maxAngle

  const radius = 80
  const cx = 100
  const cy = 100

  const rad = (angle * Math.PI) / 180
  return {
    x: cx + radius * Math.cos(rad),
    y: cy - radius * Math.sin(rad)
  }
})

// 获取维度颜色
const getDimensionColor = (ratio: number) => {
  if (ratio > 0.8) return '#ef5350'
  if (ratio > 0.6) return '#f7931a'
  if (ratio > 0.4) return '#4db6ac'
  return '#26a69a'
}

// 获取维度渐变
const getDimensionGradient = (ratio: number) => {
  if (ratio < 0.33) {
    return `linear-gradient(90deg, #26a69a 0%, #4db6ac 100%)`
  } else if (ratio < 0.5) {
    return `linear-gradient(90deg, #26a69a 0%, #4db6ac 50%, #f7931a 100%)`
  } else if (ratio < 0.65) {
    return `linear-gradient(90deg, #26a69a 0%, #4db6ac 33%, #f7931a 66%, #ff5722 100%)`
  } else if (ratio < 0.8) {
    return `linear-gradient(90deg, #26a69a 0%, #4db6ac 25%, #f7931a 50%, #ff5722 75%, #dc3545 100%)`
  } else {
    return `linear-gradient(90deg, #26a69a 0%, #4db6ac 20%, #f7931a 40%, #ff5722 60%, #dc3545 80%, #b02658 100%)`
  }
}
</script>

<style lang="scss" scoped>
.risk-score-gauge {
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 12px;
  padding: 20px;
}

.gauge-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.gauge-svg {
  width: 200px;
  height: 120px;
}

.score-display {
  position: absolute;
  top: 75px;
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.score-value {
  font-size: 42px;
  font-weight: 700;
  line-height: 1;
}

.score-max {
  font-size: 14px;
  color: #787b86;
}

.gauge-labels {
  display: flex;
  justify-content: space-between;
  width: 180px;
  margin-top: -5px;
}

.gauge-label {
  font-size: 10px;
  transition: color 0.3s;
}

.score-level {
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  margin-top: 8px;
}

.score-dimensions {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dimension-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dimension-name {
  font-size: 12px;
  color: #787b86;
}

.dimension-score {
  font-size: 12px;
  font-weight: 600;
}

.dimension-bar {
  height: 8px;
  background: #2a2e39;
  border-radius: 4px;
  overflow: hidden;
}

.dimension-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}
</style>
