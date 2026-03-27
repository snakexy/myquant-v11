<template>
  <div class="bar-chart" :style="{ height: height + 'px' }">
    <div class="chart-container">
      <!-- Y轴标签 -->
      <div class="y-axis">
        <div
          v-for="(tick, index) in yTicks"
          :key="index"
          class="y-tick"
          :style="{ bottom: ((tick.value - minValue) / (maxValue - minValue) * 80) + '%' }"
        >
          <span class="tick-label">{{ tick.label }}</span>
          <span class="tick-line"></span>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="chart-area">
        <!-- 网格线 -->
        <div
          v-for="(tick, index) in yTicks"
          :key="'grid-' + index"
          class="grid-line"
          :style="{ bottom: ((tick.value - minValue) / (maxValue - minValue) * 80) + '%' }"
        ></div>

        <!-- 柱状图 -->
        <div class="bars-container">
          <div
            v-for="(item, index) in data"
            :key="index"
            class="bar-group"
          >
            <!-- IC柱 -->
            <div
              v-if="item.ic !== undefined"
              class="bar ic-bar"
              :style="{
                height: getBarHeight(item.ic),
                background: item.ic >= 0 ? icColor : negativeColor
              }"
              :title="`${item.name}: IC=${item.ic.toFixed(4)}`"
            ></div>

            <!-- IR柱 -->
            <div
              v-if="item.ir !== undefined"
              class="bar ir-bar"
              :style="{
                height: getBarHeight(item.ir),
                background: item.ir >= 0 ? irColor : negativeColor
              }"
              :title="`${item.name}: IR=${item.ir.toFixed(4)}`"
            ></div>

            <!-- X轴标签 -->
            <span class="bar-label" :title="item.name">{{ truncateLabel(item.name) }}</span>
          </div>
        </div>
      </div>

      <!-- 图例 -->
      <div class="legend">
        <div class="legend-item">
          <span class="legend-color" :style="{ background: icColor }"></span>
          <span class="legend-label">{{ icLabel }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" :style="{ background: irColor }"></span>
          <span class="legend-label">{{ irLabel }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface BarData {
  name: string
  ic?: number
  ir?: number
  value?: number // 兼容单值模式
}

interface Props {
  data: BarData[]
  height?: number
  icLabel?: string
  irLabel?: string
  icColor?: string
  irColor?: string
  negativeColor?: string
  minValue?: number
  maxValue?: number
}

const props = withDefaults(defineProps<Props>(), {
  height: 300,
  icLabel: 'IC',
  irLabel: 'IR',
  icColor: '#3b82f6',
  irColor: '#10b981',
  negativeColor: '#ef4444',
  minValue: -0.1,
  maxValue: 0.15
})

// 生成Y轴刻度
const yTicks = computed(() => {
  const range = props.maxValue - props.minValue
  const tickCount = 5
  const step = range / (tickCount - 1)

  return Array.from({ length: tickCount }, (_, i) => {
    const value = props.minValue + step * i
    return {
      value,
      label: value.toFixed(3)
    }
  })
})

// 计算柱子高度百分比
const getBarHeight = (value: number) => {
  const range = props.maxValue - props.minValue
  const percent = (value - props.minValue) / range * 80
  return Math.max(0, Math.min(80, percent)) + '%'
}

// 截断标签
const truncateLabel = (label: string) => {
  if (label.length > 8) {
    return label.substring(0, 6) + '..'
  }
  return label
}
</script>

<style scoped lang="scss">
.bar-chart {
  width: 100%;
}

.chart-container {
  position: relative;
  height: 100%;
  padding: 20px 40px 40px 50px;
}

.y-axis {
  position: absolute;
  left: 0;
  top: 20px;
  bottom: 40px;
  width: 45px;
}

.y-tick {
  position: absolute;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  transform: translateY(50%);
}

.tick-label {
  font-size: 10px;
  color: var(--text-secondary);
  margin-right: 4px;
}

.tick-line {
  width: 6px;
  height: 1px;
  background: var(--border-color);
}

.chart-area {
  position: relative;
  height: 100%;
  border-left: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.grid-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--border-color);
  opacity: 0.3;
}

.bars-container {
  position: absolute;
  left: 10px;
  right: 10px;
  top: 0;
  bottom: 0;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding-bottom: 2px;
}

.bar-group {
  position: relative;
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 100%;
  flex: 1;
  max-width: 40px;
}

.bar {
  width: 100%;
  min-height: 2px;
  border-radius: 2px 2px 0 0;
  transition: height 0.3s ease;
  position: relative;
}

.ic-bar {
  flex: 1;
}

.ir-bar {
  flex: 1;
}

.bar:hover {
  opacity: 0.8;
}

.bar-label {
  position: absolute;
  bottom: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.legend {
  position: absolute;
  top: 5px;
  right: 10px;
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-label {
  font-size: 11px;
  color: var(--text-secondary);
}
</style>
