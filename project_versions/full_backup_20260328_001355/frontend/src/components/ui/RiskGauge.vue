<template>
  <div class="risk-gauge">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <!-- 背景圆 -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke="bgColor"
        :stroke-width="strokeWidth"
      />
      <!-- 进度圆 -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke="gaugeColor"
        :stroke-width="strokeWidth"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        stroke-linecap="round"
        class="risk-gauge-progress"
        :style="{ transform: 'rotate(-90deg)', transformOrigin: 'center' }"
      />
      <!-- 中心文字 -->
      <text
        :x="center"
        :y="center"
        text-anchor="middle"
        :fill="textColor"
        class="risk-gauge-value"
        :style="{ fontSize: `${size * 0.28}px` }"
      >
        {{ displayValue }}
      </text>
      <text
        :x="center"
        :y="center + size * 0.18"
        text-anchor="middle"
        fill="#787b86"
        class="risk-gauge-label"
        :style="{ fontSize: `${size * 0.1}px` }"
      >
        {{ label }}
      </text>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: number
  max?: number
  label?: string
  size?: number
  strokeWidth?: number
  decimals?: number
}

const props = withDefaults(defineProps<Props>(), {
  max: 100,
  label: '风险指数',
  size: 120,
  strokeWidth: 10,
  decimals: 0
})

// 中心点
const center = computed(() => props.size / 2)

// 半径
const radius = computed(() => (props.size - props.strokeWidth) / 2)

// 周长
const circumference = computed(() => 2 * Math.PI * radius.value)

// dashoffset
const dashOffset = computed(() => {
  const percent = Math.min(props.value / props.max, 1)
  return circumference.value * (1 - percent)
})

// 显示值
const displayValue = computed(() => props.value.toFixed(props.decimals))

// 背景色
const bgColor = computed(() => 'rgba(255, 255, 255, 0.1)')

// 根据值获取颜色
const gaugeColor = computed(() => {
  const percent = (props.value / props.max) * 100
  if (percent >= 80) return '#9c27b0'  // 紫色 - 高风险
  if (percent >= 60) return '#ff9800'  // 橙色 - 中风险
  return '#2962ff'                     // 蓝色 - 低风险
})

// 文字颜色
const textColor = computed(() => gaugeColor.value)
</script>

<style lang="scss" scoped>
.risk-gauge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.risk-gauge-progress {
  transition: stroke-dashoffset 0.5s ease;
}

.risk-gauge-value {
  font-weight: 700;
}

.risk-gauge-label {
  font-weight: 500;
}
</style>
