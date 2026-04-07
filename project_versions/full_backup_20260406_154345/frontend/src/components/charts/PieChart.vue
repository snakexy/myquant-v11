<template>
  <div class="pie-chart" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :viewBox="`-1 -1 2 2`" style="transform: rotate(-90deg)">
      <!-- 饼图扇区 -->
      <path
        v-for="(slice, index) in slices"
        :key="index"
        :d="slice.path"
        :fill="slice.color"
        :stroke="strokeColor"
        :stroke-width="strokeWidth"
        @mouseenter="hoveredIndex = index"
        @mouseleave="hoveredIndex = -1"
        :style="{ opacity: hoveredIndex === index || hoveredIndex === -1 ? 1 : 0.6 }"
      />
    </svg>

    <!-- 图例 -->
    <div v-if="showLegend" class="pie-legend">
      <div
        v-for="(item, index) in legendItems"
        :key="index"
        class="legend-item"
        @mouseenter="hoveredIndex = index"
        @mouseleave="hoveredIndex = -1"
      >
        <span class="legend-color" :style="{ background: item.color }"></span>
        <span class="legend-label">{{ item.label }}</span>
        <span class="legend-value">{{ item.value }}</span>
      </div>
    </div>

    <!-- 中心文字（用于圆环图） -->
    <div v-if="donut && centerText" class="donut-center">
      <span class="center-text">{{ centerText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface PieData {
  name: string
  value: number
  color?: string
}

interface Props {
  data: PieData[]
  size?: number
  donut?: boolean
  innerRadius?: number
  showLegend?: boolean
  centerText?: string
  strokeColor?: string
  strokeWidth?: number
}

const props = withDefaults(defineProps<Props>(), {
  size: 200,
  donut: false,
  innerRadius: 0.5,
  showLegend: true,
  centerText: '',
  strokeColor: '#1a1a2e',
  strokeWidth: 0.02
})

const hoveredIndex = ref(-1)

// 默认颜色方案
const defaultColors = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // orange
  '#ef4444', // red
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#84cc16', // lime
  '#f97316', // bright orange
  '#6366f1'  // indigo
]

// 计算总值
const total = computed(() => {
  return props.data.reduce((sum, item) => sum + item.value, 0)
})

// 生成饼图切片
const slices = computed(() => {
  let cumulativePercent = 0

  return props.data.map((item, index) => {
    const percent = item.value / total.value
    const color = item.color || defaultColors[index % defaultColors.length]

    // 计算起始和结束角度
    const startPercent = cumulativePercent
    const endPercent = cumulativePercent + percent
    cumulativePercent = endPercent

    // 生成SVG路径
    const startX = Math.cos(2 * Math.PI * startPercent)
    const startY = Math.sin(2 * Math.PI * startPercent)
    const endX = Math.cos(2 * Math.PI * endPercent)
    const endY = Math.sin(2 * Math.PI * endPercent)

    // 大圆弧标志
    const largeArcFlag = percent > 0.5 ? 1 : 0

    let path = ''

    if (props.donut) {
      // 圆环图路径
      const innerR = props.innerRadius
      const innerStartX = innerR * Math.cos(2 * Math.PI * startPercent)
      const innerStartY = innerR * Math.sin(2 * Math.PI * startPercent)
      const innerEndX = innerR * Math.cos(2 * Math.PI * endPercent)
      const innerEndY = innerR * Math.sin(2 * Math.PI * endPercent)

      path = `M ${startX} ${startY} A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY} L ${innerEndX} ${innerEndY} A ${innerR} ${innerR} 0 ${largeArcFlag} 0 ${innerStartX} ${innerStartY} Z`
    } else {
      // 饼图路径
      path = `M 0 0 L ${startX} ${startY} A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY} Z`
    }

    return { path, color, percent }
  })
})

// 生成图例
const legendItems = computed(() => {
  return props.data.map((item, index) => {
    const percent = (item.value / total.value * 100).toFixed(1)
    return {
      label: item.name,
      value: props.donut ? `${percent}%` : percent,
      color: item.color || defaultColors[index % defaultColors.length]
    }
  })
})
</script>

<style scoped lang="scss">
.pie-chart {
  position: relative;
  display: inline-block;

  svg {
    width: 100%;
    height: 100%;

    path {
      transition: opacity 0.2s ease;
      cursor: pointer;
    }
  }
}

.pie-legend {
  position: absolute;
  right: calc(100% + 16px);
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 120px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;

  &:hover {
    background: var(--bg-tertiary);
  }
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-label {
  color: var(--text-secondary);
  flex: 1;
}

.legend-value {
  color: var(--text-primary);
  font-weight: 600;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.center-text {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
</style>
