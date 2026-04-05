<template>
  <button
    :class="buttonClass"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <n-icon v-if="loading" :size="iconSize" class="loading-icon">
      <LoadingOutlined />
    </n-icon>
    <n-icon v-if="icon && !loading" :size="iconSize" :class="iconClass">
      <component :is="icon" />
    </n-icon>
    <span v-if="$slots.default" :class="textClass">
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NIcon } from 'naive-ui'
// 使用简单的SVG图标替代
const LoadingOutlined = {
  template: `
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2a1 1 0 0 1 1 1v2.101a7.002 7.002 0 0 1 5.899 5.899L21 11a1 1 0 1 1 0 2l-2.101-.001A7.002 7.002 0 0 1 13 18.899V21a1 1 0 1 1-2 0v-2.101a7.002 7.002 0 0 1-5.899-5.899L3 13a1 1 0 1 1 0-2l2.101.001A7.002 7.002 0 0 1 11 5.101V3a1 1 0 0 1 1-1z"/>
    </svg>
  `
}
import type { Component } from 'vue'

interface Props {
  type?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'ghost'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
  icon?: Component
  block?: boolean
  round?: boolean
  circle?: boolean
  text?: boolean
  link?: boolean
  className?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  disabled: false,
  loading: false,
  icon: undefined,
  block: false,
  round: false,
  circle: false,
  text: false,
  link: false,
  className: ''
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}

const buttonClass = computed(() => {
  const classes = ['quant-button']
  
  // 类型
  classes.push(`btn-${props.type}`)
  
  // 尺寸
  classes.push(`btn-${props.size}`)
  
  // 状态
  if (props.disabled) classes.push('btn-disabled')
  if (props.loading) classes.push('btn-loading')
  
  // 形状
  if (props.block) classes.push('btn-block')
  if (props.round) classes.push('btn-round')
  if (props.circle) classes.push('btn-circle')
  if (props.text) classes.push('btn-text')
  if (props.link) classes.push('btn-link')
  
  // 自定义类名
  if (props.className) classes.push(props.className)
  
  return classes
})

const iconClass = computed(() => {
  const classes = ['btn-icon']
  if (props.loading) classes.push('btn-icon--hidden')
  return classes
})

const textClass = computed(() => {
  const classes = ['btn-text']
  if (props.loading) classes.push('btn-text--loading')
  return classes
})

const iconSize = computed(() => {
  const sizeMap = {
    small: 14,
    medium: 16,
    large: 18
  }
  return sizeMap[props.size]
})
</script>

<style lang="scss" scoped>
.quant-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-1);
  border: 1px solid transparent;
  border-radius: var(--border-radius-base);
  font-family: var(--font-family-primary);
  font-weight: 500;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-duration-base) var(--transition-timing-function-base);
  user-select: none;
  white-space: nowrap;
  outline: none;
  background: transparent;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  // 尺寸
  &.btn-small {
    height: 28px;
    padding: 0 var(--spacing-2);
    font-size: var(--font-size-xs);
    line-height: 26px;
  }
  
  &.btn-medium {
    height: 36px;
    padding: 0 var(--spacing-3);
    font-size: var(--font-size-sm);
    line-height: 34px;
  }
  
  &.btn-large {
    height: 44px;
    padding: 0 var(--spacing-4);
    font-size: var(--font-size-base);
    line-height: 42px;
  }
  
  // 类型
  &.btn-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-color)-dark);
    border-color: var(--primary-color);
    color: var(--white);
    
    &:hover {
      background: linear-gradient(135deg, var(--primary-color)-light, var(--primary-color));
      border-color: var(--primary-color)-light;
    }
  }
  
  &.btn-secondary {
    background: linear-gradient(135deg, var(--secondary-color), var(--secondary-color)-dark);
    border-color: var(--secondary-color);
    color: var(--white);
    
    &:hover {
      background: linear-gradient(135deg, var(--secondary-color)-light, var(--secondary-color));
      border-color: var(--secondary-color)-light;
    }
  }
  
  &.btn-success {
    background: linear-gradient(135deg, var(--success-color), var(--success-color)-dark);
    border-color: var(--success-color);
    color: var(--white);
    
    &:hover {
      background: linear-gradient(135deg, var(--success-color)-light, var(--success-color));
      border-color: var(--success-color)-light;
    }
  }
  
  &.btn-warning {
    background: linear-gradient(135deg, var(--warning-color), var(--warning-color)-dark);
    border-color: var(--warning-color);
    color: var(--white);
    
    &:hover {
      background: linear-gradient(135deg, var(--warning-color)-light, var(--warning-color));
      border-color: var(--warning-color)-light;
    }
  }
  
  &.btn-danger {
    background: linear-gradient(135deg, var(--danger-color), var(--danger-color)-dark);
    border-color: var(--danger-color);
    color: var(--white);
    
    &:hover {
      background: linear-gradient(135deg, var(--danger-color)-light, var(--danger-color));
      border-color: var(--danger-color)-light;
    }
  }
  
  &.btn-info {
    background: linear-gradient(135deg, var(--info-color), var(--info-color)-dark);
    border-color: var(--info-color);
    color: var(--white);
    
    &:hover {
      background: linear-gradient(135deg, var(--info-color)-light, var(--info-color));
      border-color: var(--info-color)-light;
    }
  }
  
  &.btn-ghost {
    background: transparent;
    border-color: var(--border-color)-base;
    color: var(--text-primary);
    
    &:hover {
      background: var(--bg-color-secondary);
      border-color: var(--primary-color);
      color: var(--primary-color);
    }
  }
  
  // 状态
  &.btn-disabled {
    opacity: 0.6;
    cursor: not-allowed;
    
    &:hover {
      transform: none;
      box-shadow: none;
    }
  }
  
  &.btn-loading {
    cursor: default;
    
    &:hover {
      transform: none;
      box-shadow: none;
    }
  }
  
  // 形状
  &.btn-block {
    width: 100%;
  }
  
  &.btn-round {
    border-radius: var(--border-radius-round);
  }
  
  &.btn-circle {
    border-radius: 50%;
    padding: 0;
    
    &.btn-small {
      width: 28px;
    }
    
    &.btn-medium {
      width: 36px;
    }
    
    &.btn-large {
      width: 44px;
    }
  }
  
  &.btn-text {
    background: transparent;
    border-color: transparent;
    color: var(--primary-color);
    
    &:hover {
      background: var(--bg-color-secondary);
    }
  }
  
  &.btn-link {
    background: transparent;
    border-color: transparent;
    color: var(--primary-color);
    text-decoration: underline;
    
    &:hover {
      color: var(--primary-color)-light;
    }
  }
  
  // 图标
  .btn-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    
    &--hidden {
      opacity: 0;
    }
  }
  
  // 文本
  .btn-text {
    &--loading {
      opacity: 0.7;
    }
  }
  
  // 加载图标
  .loading-icon {
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>