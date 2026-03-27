<template>
  <div :class="cardClass" :style="cardStyle">
    <!-- 卡片头部 -->
    <div v-if="showHeader || $slots.header" :class="headerClass">
      <slot name="header">
        <div v-if="title || $slots.title" class="quant-card__title-content">
          <n-icon v-if="icon" :size="iconSize" class="quant-card__icon">
            <component :is="icon" />
          </n-icon>
          <slot name="title">{{ title }}</slot>
        </div>
        <div v-if="$slots.extra" class="quant-card__extra">
          <slot name="extra" />
        </div>
      </slot>
    </div>
    
    <!-- 卡片内容 -->
    <div :class="bodyClass" :style="bodyStyle">
      <slot />
    </div>
    
    <!-- 卡片底部 -->
    <div v-if="showFooter || $slots.footer" :class="footerClass">
      <slot name="footer" />
    </div>
    
    <!-- 加载遮罩 -->
    <div v-if="loading" class="quant-card__loading">
      <n-spin :size="loadingSize" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NIcon, NSpin } from 'naive-ui'
import type { Component } from 'vue'

interface Props {
  title?: string
  icon?: Component
  size?: 'small' | 'medium' | 'large'
  shadow?: 'never' | 'hover' | 'always'
  bordered?: boolean
  hoverable?: boolean
  loading?: boolean
  showHeader?: boolean
  showFooter?: boolean
  padding?: string | number
  margin?: string | number
  width?: string | number
  height?: string | number
  maxWidth?: string | number
  maxHeight?: string | number
  bodyStyle?: Record<string, string>
  headerStyle?: Record<string, string>
  footerStyle?: Record<string, string>
  loadingSize?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  icon: undefined,
  size: 'medium',
  shadow: 'hover',
  bordered: true,
  hoverable: false,
  loading: false,
  showHeader: true,
  showFooter: false,
  padding: undefined,
  margin: undefined,
  width: 'auto',
  height: 'auto',
  maxWidth: 'auto',
  maxHeight: 'auto',
  bodyStyle: () => ({}),
  headerStyle: () => ({}),
  footerStyle: () => ({}),
  loadingSize: 'medium'
})

const cardClass = computed(() => {
  const classes = ['quant-card']
  
  if (props.size) classes.push(`quant-card--${props.size}`)
  if (props.shadow) classes.push(`quant-card--shadow-${props.shadow}`)
  if (props.bordered) classes.push('quant-card--bordered')
  if (props.hoverable) classes.push('quant-card--hoverable')
  if (props.loading) classes.push('quant-card--loading')
  
  return classes
})

const headerClass = computed(() => {
  const classes = ['quant-card__header']
  
  if (props.icon) classes.push('quant-card__header--with-icon')
  
  return classes
})

const bodyClass = computed(() => {
  return ['quant-card__body']
})

const footerClass = computed(() => {
  return ['quant-card__footer']
})

const cardStyle = computed(() => {
  const style: Record<string, string> = {}
  
  // 宽度
  if (typeof props.width === 'number') {
    style.width = `${props.width}px`
  } else if (props.width !== 'auto') {
    style.width = props.width
  }
  
  // 高度
  if (typeof props.height === 'number') {
    style.height = `${props.height}px`
  } else if (props.height !== 'auto') {
    style.height = props.height
  }
  
  // 最大宽度
  if (typeof props.maxWidth === 'number') {
    style.maxWidth = `${props.maxWidth}px`
  } else if (props.maxWidth !== 'auto') {
    style.maxWidth = props.maxWidth
  }
  
  // 最大高度
  if (typeof props.maxHeight === 'number') {
    style.maxHeight = `${props.maxHeight}px`
  } else if (props.maxHeight !== 'auto') {
    style.maxHeight = props.maxHeight
  }
  
  // 外边距
  if (typeof props.margin === 'number') {
    style.margin = `${props.margin}px`
  } else if (props.margin) {
    style.margin = props.margin
  }
  
  return style
})

const iconSize = computed(() => {
  const sizeMap = {
    small: 16,
    medium: 18,
    large: 20
  }
  return sizeMap[props.size]
})
</script>

<style lang="scss" scoped>
.quant-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color-base);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  transition: all var(--transition-duration-base) var(--transition-timing-function-base);
  
  // 尺寸
  &--small {
    .quant-card__header {
      padding: var(--spacing-2) var(--spacing-3);
      min-height: 40px;
    }
    
    .quant-card__body {
      padding: var(--spacing-2) var(--spacing-3);
    }
    
    .quant-card__footer {
      padding: var(--spacing-2) var(--spacing-3);
    }
  }
  
  &--medium {
    .quant-card__header {
      padding: var(--spacing-3) var(--spacing-4);
      min-height: 48px;
    }
    
    .quant-card__body {
      padding: var(--spacing-3) var(--spacing-4);
    }
    
    .quant-card__footer {
      padding: var(--spacing-3) var(--spacing-4);
    }
  }
  
  &--large {
    .quant-card__header {
      padding: var(--spacing-4) var(--spacing-5);
      min-height: 56px;
    }
    
    .quant-card__body {
      padding: var(--spacing-4) var(--spacing-5);
    }
    
    .quant-card__footer {
      padding: var(--spacing-4) var(--spacing-5);
    }
  }
  
  // 阴影
  &--shadow-never {
    box-shadow: none;
  }
  
  &--shadow-hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    
    &:hover {
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
      transform: translateY(-2px);
    }
  }
  
  &--shadow-always {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  }
  
  // 边框
  &--bordered {
    border: 1px solid var(--border-color)-base;
  }
  
  // 悬停效果
  &--hoverable {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }
  }
  
  // 加载状态
  &--loading {
    pointer-events: none;
    
    .quant-card__header,
    .quant-card__body,
    .quant-card__footer {
      opacity: 0.6;
    }
  }
  
  // 头部
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border-color)-light;
    background-color: var(--bg-color-secondary);
    
    &--with-icon {
      .quant-card__title-content {
        display: flex;
        align-items: center;
      }
    }
  }
  
  // 标题内容
  &__title-content {
    display: flex;
    align-items: center;
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--text-primary);
  }
  
  // 图标
  &__icon {
    margin-right: var(--spacing-2);
    color: var(--primary-color);
  }
  
  // 额外内容
  &__extra {
    display: flex;
    align-items: center;
    color: var(--text-secondary);
  }
  
  // 内容
  &__body {
    flex: 1;
    color: var(--text-primary);
    line-height: 1.6;
  }
  
  // 底部
  &__footer {
    border-top: 1px solid var(--border-color)-light;
    background-color: var(--bg-color-secondary);
  }
  
  // 加载遮罩
  &__loading {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(var(--bg-color-base), 0.8);
    backdrop-filter: blur(2px);
    z-index: 10;
  }
}
</style>