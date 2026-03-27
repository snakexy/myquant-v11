<template>
  <div class="metric-card">
    <div class="metric-card-header">
      <div class="metric-card-icon" :style="iconStyle">
        <n-icon :size="20">
          <component :is="icon" />
        </n-icon>
      </div>
      <div v-if="showTrend" class="metric-card-trend" :class="{ up: trend > 0, down: trend < 0 }">
        <n-icon :size="14">
          <ArrowUpOutline v-if="trend > 0" />
          <ArrowDownOutline v-else-if="trend < 0" />
          <RemoveOutline v-else />
        </n-icon>
        <span>{{ Math.abs(trend) }}%</span>
      </div>
    </div>
    <div class="metric-card-value">{{ displayValue }}</div>
    <div class="metric-card-label">{{ label }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NIcon } from 'naive-ui'
import { ArrowUpOutline, ArrowDownOutline, RemoveOutline } from '@vicons/ionicons5'
import type { Component } from 'vue'

interface Props {
  icon: Component
  value: number | string
  label: string
  trend?: number
  precision?: number
  prefix?: string
  suffix?: string
  iconColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  trend: 0,
  precision: 2,
  prefix: '',
  suffix: '',
  iconColor: '#2962ff'
})

// 显示值
const displayValue = computed(() => {
  const val = typeof props.value === 'number' ? props.value.toFixed(props.precision) : props.value
  return `${props.prefix}${val}${props.suffix}`
})

// 图标样式
const iconStyle = computed(() => ({
  background: `${props.iconColor}20`,
  color: props.iconColor
}))

// 是否显示趋势
const showTrend = computed(() => props.trend !== undefined && props.trend !== 0)
</script>

<style lang="scss" scoped>
.metric-card {
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: #1e222d;
  border: 1px solid #363a45;
  border-radius: 12px;
}

.metric-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.metric-card-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.metric-card-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;

  &.up {
    color: #ef5350;
  }

  &.down {
    color: #26a69a;
  }
}

.metric-card-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  color: #d1d4dc;
}

.metric-card-label {
  font-size: 14px;
  color: #787b86;
  margin-top: 4px;
}
</style>
