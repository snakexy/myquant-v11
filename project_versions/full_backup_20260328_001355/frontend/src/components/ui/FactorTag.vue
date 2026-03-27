<template>
  <span
    class="factor-tag-item"
    :class="[size, { selected, clickable }]"
    :style="{ borderLeftColor: getBorderColor(), ...customStyle }"
    @click="handleClick"
  >
    <span class="factor-name">{{ factorName }}</span>
    <span v-if="showIc && ic !== null" class="factor-ic">(IC: {{ ic.toFixed(3) }})</span>
    <span v-if="selected" class="check-icon">✓</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  factorName: string
  ic?: number | null
  selected?: boolean
  clickable?: boolean
  showIc?: boolean
  size?: 'small' | 'medium' | 'large'
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  ic: null,
  selected: false,
  clickable: false,
  showIc: true,
  size: 'medium',
  color: undefined
})

// 用于接收外部传入的样式
const customStyle = computed(() => ({}))

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// 因子类型分类
const getFactorCategory = (name: string): string => {
  const n = name.toUpperCase()
  if (n.includes('MA') || n.includes('EMA') || n.includes('SMA') || n.includes('CROSS') || n.includes('ROC') || n.includes('RETURN')) return 'momentum'
  if (n.includes('VOL') || n.includes('VOLUME')) return 'volume'
  if (n.includes('STD') || n.includes('VAR') || n.includes('STD_DEV')) return 'volatility'
  if (n.includes('RSI') || n.includes('MACD') || n.includes('KDJ') || n.includes('CCI')) return 'technical'
  if (n.includes('BETA') || n.includes('ALPHA')) return 'factor'
  return 'other'
}

// 因子类型颜色映射
const categoryColors: Record<string, string> = {
  momentum: '#26a69a',    // 绿色 - 动量
  volatility: '#ff9800',  // 橙色 - 波动率
  volume: '#2962ff',      // 蓝色 - 成交量
  technical: '#9c27b0',   // 紫色 - 技术
  factor: '#ef5350',     // 红色 - 因子
  other: '#787b86'       // 灰色 - 其他
}

const getBorderColor = (): string => {
  return props.color || categoryColors[getFactorCategory(props.factorName)]
}

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
.factor-tag-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  background: var(--bg-tertiary, #f5f5f5);
  color: var(--text-secondary, #666);
  border-width: 1px;
  border-style: solid;
  border-color: transparent;
  border-left-width: 3px;
  border-left-style: solid;
  white-space: nowrap;
  transition: all 0.2s;

  &.clickable {
    cursor: pointer;

    &:hover {
      background: var(--bg-secondary, #eee);
    }
  }

  &.selected {
    .check-icon {
      color: #2962ff;
      font-weight: bold;
      margin-left: 4px;
    }
    .factor-name {
      color: #2962ff;
    }
  }

  // 尺寸
  &.small {
    padding: 2px 6px;
    font-size: 11px;
    border-left-width: 2px;

    .factor-ic {
      font-size: 10px;
    }
  }

  &.large {
    padding: 6px 12px;
    font-size: 14px;
    border-left-width: 4px;
  }

  .factor-name {
    font-weight: 500;
  }

  .factor-ic {
    font-size: 11px;
    opacity: 0.8;
  }

  .check-icon {
    font-size: 12px;
    margin-right: 4px;
  }
}
</style>
