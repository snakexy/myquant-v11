<template>
  <div class="chart-card">
    <div class="chart-header">
      <div class="chart-title">
        <svg class="icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        {{ title }}
        <div class="period-toggle">
          <button
            v-for="opt in periodOptions"
            :key="opt.value"
            :class="['period-btn', { active: modelValue === opt.value }]"
            @click="$emit('update:modelValue', opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
      <button class="chart-type-toggle" @click="$emit('toggleType')">
        <svg v-if="chartType === 'heatmap'" class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="12" width="4" height="9"></rect>
          <rect x="10" y="8" width="4" height="13"></rect>
          <rect x="17" y="4" width="4" height="17"></rect>
        </svg>
        <svg v-else class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="10" y="3" width="7" height="7"></rect>
          <rect x="3" y="10" width="7" height="7"></rect>
          <rect x="10" y="10" width="7" height="7"></rect>
        </svg>
      </button>
    </div>
    <div class="chart-content">
      <!-- 热力图视图 -->
      <div v-if="chartType === 'heatmap'" class="heatmap" :style="{ gridTemplateColumns: `repeat(${gridCols}, 1fr)` }">
        <div v-for="(item, idx) in heatmapData" :key="idx" :class="['heatmap-cell', item.class]">
          {{ item.value }}%
          <span class="heatmap-label">{{ item.label }}</span>
        </div>
      </div>
      <!-- 3D柱状图视图 -->
      <div v-else class="bar-chart-3d-echarts">
        <slot name="barChart"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface HeatmapItem {
  label: string
  value: number
  class: string
}

interface Props {
  title?: string
  modelValue?: string
  chartType?: 'heatmap' | 'bar'
  gridCols?: number
  heatmapData?: HeatmapItem[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '收益统计',
  modelValue: 'monthly',
  chartType: 'heatmap',
  gridCols: 4,
  heatmapData: () => []
})

defineEmits<{
  'update:modelValue': [value: string]
  'toggleType': []
}>()

const periodOptions = [
  { value: 'daily', label: '日' },
  { value: 'weekly', label: '周' },
  { value: 'monthly', label: '月' }
]
</script>

<style lang="scss" scoped>
.chart-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 20px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.chart-header {
  flex-shrink: 0;
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
}

.icon-md {
  width: 18px;
  height: 18px;
  color: #ff9800;
}

.icon-sm {
  width: 14px;
  height: 14px;
  color: #787b86;
}

.period-toggle {
  display: flex;
  gap: 4px;
  margin-left: 12px;
}

.period-btn {
  padding: 2px 8px;
  font-size: 11px;
  background: transparent;
  border: 1px solid #2a2e39;
  color: #787b86;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #2a2e39;
    color: #d1d4dc;
  }

  &.active {
    background: #2962ff;
    border-color: #2962ff;
    color: white;
  }
}

.chart-type-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  margin-left: 8px;
  background: #2a2e39;
  border: 1px solid #3a3f4b;
  border-radius: 4px;
  cursor: pointer;
  color: #a0aec0;
  transition: all 0.15s;

  &:hover {
    background: #1e222d;
    color: #d1d4dc;
  }
}

.chart-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;

  .heatmap {
    display: grid;
    gap: 6px;
    padding-top: 8px;
    flex: 1;
    min-height: 180px;
    align-content: stretch;
  }

  .heatmap-cell {
    height: 100%;
    min-height: 50px;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 600;
    color: white;
    position: relative;
    padding: 4px;
    box-sizing: border-box;

    &.high { background: linear-gradient(135deg, #9c27b0, #ba68c8); }
    &.medium-high { background: linear-gradient(135deg, #ef5350, #ff8a80); }
    &.medium { background: linear-gradient(135deg, #ff9800, #ffb74d); }
    &.medium-low { background: linear-gradient(135deg, #2962ff, #5c95ff); }
    &.low { background: linear-gradient(135deg, #4caf50, #81c784); }
    &.empty { background: #2a2e39; }
  }

  .heatmap-label {
    position: absolute;
    bottom: 2px;
    font-size: 10px;
    opacity: 0.8;
  }

  .bar-chart-3d-echarts {
    width: 100%;
    height: 100%;
    min-height: 200px;
  }
}
</style>
