<template>
  <div class="circular-progress-container">
    <div class="circular-progress-wrapper">
      <svg
        class="circular-progress"
        :width="size"
        :height="size"
        viewBox="0 0 100 100"
      >
        <!-- 背景圆 -->
        <circle
          class="circular-progress-bg"
          cx="50"
          cy="50"
          :r="radius"
          :stroke-width="strokeWidth"
          fill="none"
        />
        <!-- 进度圆 -->
        <circle
          class="circular-progress-fill"
          :class="progressClass"
          cx="50"
          cy="50"
          :r="radius"
          :stroke-width="strokeWidth"
          fill="none"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="dashOffset"
          stroke-linecap="round"
          transform="rotate(-90 50 50)"
        />
        <!-- 中心文本 -->
        <text
          class="circular-progress-text"
          x="50"
          y="50"
          text-anchor="middle"
          dy="0.3em"
        >
          {{ displayValue }}
        </text>
        <!-- 标签文本 -->
        <text
          class="circular-progress-label"
          x="50"
          y="65"
          text-anchor="middle"
        >
          {{ label }}
        </text>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: number // 0-100
  size?: number // SVG大小
  strokeWidth?: number // 线条宽度
  label?: string // 标签文本
  color?: string // 自定义颜色
  showLabel?: boolean // 是否显示标签
}

const props = withDefaults(defineProps<Props>(), {
  size: 80,
  strokeWidth: 8,
  label: '完成度',
  color: '',
  showLabel: true
})

// 计算半径
const radius = computed(() => 50 - props.strokeWidth / 2)

// 计算圆周长
const circumference = computed(() => 2 * Math.PI * radius.value)

// 计算进度偏移量
const dashOffset = computed(() => {
  const progress = Math.min(Math.max(props.value, 0), 100)
  return circumference.value * (1 - progress / 100)
})

// 显示值
const displayValue = computed(() => {
  return `${Math.round(props.value)}%`
})

// 根据值确定颜色类
const progressClass = computed(() => {
  if (props.color) return ''
  
  const value = props.value
  if (value >= 90) return 'progress-success'
  if (value >= 70) return 'progress-warning'
  return 'progress-danger'
})

// 获取进度条颜色
const getProgressColor = computed(() => {
  if (props.color) return props.color
  
  const value = props.value
  if (value >= 90) return '#10b981' // 绿色
  if (value >= 70) return '#f59e0b' // 橙色
  return '#ef4444' // 红色
})
</script>

<style scoped>
.circular-progress-container {
  display: inline-block;
  position: relative;
}

.circular-progress-wrapper {
  position: relative;
}

.circular-progress {
  display: block;
}

.circular-progress-bg {
  stroke: rgba(255, 255, 255, 0.1);
}

.circular-progress-fill {
  stroke: #2962ff; /* 默认蓝色 */
  transition: stroke-dashoffset 0.5s ease, stroke 0.3s ease;
}

.circular-progress-fill.progress-success {
  stroke: #10b981; /* 绿色 */
}

.circular-progress-fill.progress-warning {
  stroke: #f59e0b; /* 橙色 */
}

.circular-progress-fill.progress-danger {
  stroke: #ef4444; /* 红色 */
}

.circular-progress-text {
  font-size: 16px;
  font-weight: 600;
  fill: white;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.circular-progress-label {
  font-size: 10px;
  fill: rgba(255, 255, 255, 0.7);
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* 迷你版本 - 用于小组件 */
.circular-progress.mini {
  width: 40px;
  height: 40px;
}

.circular-progress.mini .circular-progress-text {
  font-size: 10px;
}

.circular-progress.mini .circular-progress-label {
  font-size: 8px;
}
</style>