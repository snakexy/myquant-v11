<template>
  <div class="status-light" :class="[`status-light--${status}`, { 'status-light--pulse': pulse }]">
    <span class="status-light-dot" :style="dotStyle"></span>
    <span v-if="showLabel" class="status-light-label">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type StatusType = 'normal' | 'warning' | 'risk' | 'success' | 'danger'

interface Props {
  status: StatusType
  label?: string
  showLabel?: boolean
  pulse?: boolean
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  label: '',
  showLabel: true,
  pulse: true,
  size: 'medium'
})

// 状态颜色映射
const statusColorMap: Record<StatusType, string> = {
  normal: '#2962ff',   // 蓝色 - 正常
  warning: '#ff9800',  // 橙色 - 警告
  risk: '#9c27b0',    // 紫色 - 风险
  success: '#ef5350',  // 红色 - 成功 (A股涨)
  danger: '#26a69a'   // 绿色 - 危险 (A股跌)
}

// 点颜色
const dotColor = computed(() => statusColorMap[props.status] || statusColorMap.normal)

// 点样式
const dotStyle = computed(() => {
  const sizeMap = { small: 8, medium: 10, large: 12 }
  return {
    width: `${sizeMap[props.size]}px`,
    height: `${sizeMap[props.size]}px`,
    backgroundColor: dotColor.value,
    boxShadow: `0 0 8px ${dotColor.value}`
  }
})

// 标签
const label = computed(() => {
  const labelMap: Record<StatusType, string> = {
    normal: '正常',
    warning: '警告',
    risk: '风险',
    success: '成功',
    danger: '失败'
  }
  return props.label || labelMap[props.status]
})
</script>

<style lang="scss" scoped>
.status-light {
  display: inline-flex;
  align-items: center;
  gap: 6px;

  &--pulse {
    .status-light-dot {
      animation: pulse 2s infinite;
    }
  }
}

.status-light-dot {
  border-radius: 50%;
  transition: all 0.3s ease;
}

.status-light-label {
  font-size: 14px;
  color: #d1d4dc;
}

@keyframes pulse {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
