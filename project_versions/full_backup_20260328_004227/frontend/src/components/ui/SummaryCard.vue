<template>
  <div class="summary-card">
    <div class="card-icon" :class="iconColorClass" v-html="iconSvg"></div>
    <div class="card-content">
      <div class="card-label">{{ label }}</div>
      <div class="card-value" :class="valueClass">{{ displayValue }}</div>
      <div v-if="subtitle" class="card-sub">{{ subtitle }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  icon: string
  value: string | number
  label: string
  subtitle?: string
  iconColor?: 'blue' | 'green' | 'red' | 'orange' | 'purple'
  valueColor?: 'default' | 'profit' | 'loss'
  prefix?: string
  suffix?: string
  currency?: boolean
  currencyUnit?: 'yuan' | 'wan'
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: 'blue',
  valueColor: 'default',
  prefix: '',
  suffix: '',
  currency: false,
  currencyUnit: 'yuan'
})

const iconColorClass = computed(() => {
  return props.iconColor
})

const iconSvg = computed(() => {
  return props.icon
})

const valueClass = computed(() => {
  return props.valueColor
})

const displayValue = computed(() => {
  if (typeof props.value === 'number') {
    let formatted: string
    const currencyPrefix = props.currency ? '¥' : ''
    if (props.currency) {
      // 人民币格式：不使用千位分隔符
      if (props.currencyUnit === 'wan' && Math.abs(props.value) >= 10000) {
        // 以万为单位
        formatted = currencyPrefix + (props.value / 10000).toFixed(2) + '万'
      } else {
        formatted = currencyPrefix + props.value.toFixed(2)
      }
    } else {
      formatted = props.value.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
    }
    return `${props.prefix}${formatted}${props.suffix}`
  }
  return `${props.prefix}${props.value}${props.suffix}`
})
</script>

<style lang="scss" scoped>
.summary-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--accent-blue, #409EFF);
  }
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  flex-shrink: 0;

  :deep(svg) {
    width: 20px;
    height: 20px;
  }

  &.blue {
    background: rgba(64, 158, 255, 0.15);
    color: #409EFF;
  }

  &.green {
    background: rgba(103, 194, 58, 0.15);
    color: #67C23A;
  }

  &.red {
    background: rgba(245, 108, 108, 0.15);
    color: #F56C6C;
  }

  &.orange {
    background: rgba(230, 162, 60, 0.15);
    color: #E6A23C;
  }

  &.purple {
    background: rgba(156, 39, 176, 0.15);
    color: #9C27B0;
  }
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-label {
  font-size: 12px;
  color: var(--text-secondary, #787b86);
  margin-bottom: 4px;
}

.card-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #d1d4dc);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  &.profit {
    color: #ef5350;
  }

  &.loss {
    color: #26a69a;
  }
}

.card-sub {
  font-size: 11px;
  color: var(--text-muted, #787b86);
  margin-top: 4px;
}
</style>
