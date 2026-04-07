<template>
  <div v-if="visible" :class="containerClass" :style="containerStyle">
    <!-- 遮罩层 -->
    <div v-if="mask" class="quant-loading__mask" />
    
    <!-- 加载内容 -->
    <div :class="contentClass">
      <!-- 旋转图标 -->
      <div v-if="type === 'spinner'" class="quant-loading__spinner">
        <div :class="spinnerClass">
          <div v-for="i in 8" :key="i" :class="getDotClass(i)" />
        </div>
      </div>
      
      <!-- 圆形进度条 -->
      <div v-else-if="type === 'circle'" class="quant-loading__circle">
        <svg :class="circleClass" viewBox="25 25 50 50">
          <circle
            :class="circlePathClass"
            cx="50"
            cy="50"
            r="20"
            fill="none"
            stroke-width="4"
            stroke-miterlimit="10"
          />
        </svg>
      </div>
      
      <!-- 点状动画 -->
      <div v-else-if="type === 'dots'" class="quant-loading__dots">
        <div v-for="i in 3" :key="i" :class="getDotItemClass(i)" />
      </div>
      
      <!-- 波浪动画 -->
      <div v-else-if="type === 'wave'" class="quant-loading__wave">
        <div v-for="i in 5" :key="i" :class="getWaveItemClass(i)" />
      </div>
      
      <!-- 自定义图标 -->
      <div v-else-if="type === 'custom' && icon" class="quant-loading__custom">
        <n-icon :size="iconSize" :class="customIconClass">
          <component :is="icon" />
        </n-icon>
      </div>
      
      <!-- 加载文本 -->
      <div v-if="text" class="quant-loading__text">
        {{ text }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NIcon } from 'naive-ui'
import type { Component } from 'vue'

interface Props {
  visible?: boolean
  type?: 'spinner' | 'circle' | 'dots' | 'wave' | 'custom'
  size?: 'small' | 'medium' | 'large'
  color?: string
  backgroundColor?: string
  text?: string
  mask?: boolean
  maskColor?: string
  fullscreen?: boolean
  icon?: Component
  delay?: number
  zIndex?: number
}

const props = withDefaults(defineProps<Props>(), {
  visible: true,
  type: 'spinner',
  size: 'medium',
  color: '',
  backgroundColor: '',
  text: '',
  mask: true,
  maskColor: '',
  fullscreen: false,
  icon: undefined,
  delay: 0,
  zIndex: 1000
})

const containerClass = computed(() => {
  const classes = ['quant-loading']
  
  if (props.fullscreen) classes.push('quant-loading--fullscreen')
  if (props.mask) classes.push('quant-loading--masked')
  
  return classes
})

const contentClass = computed(() => {
  const classes = ['quant-loading__content']
  
  if (props.size) classes.push(`quant-loading__content--${props.size}`)
  
  return classes
})

const spinnerClass = computed(() => {
  const classes = ['quant-loading__spinner-inner']
  
  if (props.size) classes.push(`quant-loading__spinner-inner--${props.size}`)
  
  return classes
})

const circleClass = computed(() => {
  const classes = ['quant-loading__circle-svg']
  
  if (props.size) classes.push(`quant-loading__circle-svg--${props.size}`)
  
  return classes
})

const circlePathClass = computed(() => {
  const classes = ['quant-loading__circle-path']
  
  if (props.color) classes.push('quant-loading__circle-path--custom')
  
  return classes
})

const customIconClass = computed(() => {
  const classes = ['quant-loading__custom-icon']
  
  if (props.size) classes.push(`quant-loading__custom-icon--${props.size}`)
  
  return classes
})

const containerStyle = computed(() => {
  const style: Record<string, string> = {}
  
  if (props.zIndex) {
    style.zIndex = props.zIndex.toString()
  }
  
  return style
})

const iconSize = computed(() => {
  const sizeMap = {
    small: 24,
    medium: 32,
    large: 40
  }
  return sizeMap[props.size]
})

const getDotClass = (index: number) => {
  const classes = ['quant-loading__dot']
  
  if (props.size) classes.push(`quant-loading__dot--${props.size}`)
  
  return classes
}

const getDotItemClass = (index: number) => {
  const classes = ['quant-loading__dots-item']
  
  if (props.size) classes.push(`quant-loading__dots-item--${props.size}`)
  
  return classes
}

const getWaveItemClass = (index: number) => {
  const classes = ['quant-loading__wave-item']
  
  if (props.size) classes.push(`quant-loading__wave-item--${props.size}`)
  
  return classes
}
</script>

<style lang="scss" scoped>
.quant-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  
  &--fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
  }
  
  &--masked {
    pointer-events: none;
  }
  
  // 遮罩层
  &__mask {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(var(--bg-color-base), 0.7);
    backdrop-filter: blur(2px);
    z-index: -1;
  }
  
  // 内容容器
  &__content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-4);
    background-color: var(--bg-color-base);
    border-radius: var(--border-radius-base);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    
    &--small {
      padding: var(--spacing-2);
    }
    
    &--large {
      padding: var(--spacing-6);
    }
  }
  
  // 旋转图标
  &__spinner {
    &-inner {
      position: relative;
      display: inline-block;
      
      &--small {
        width: 24px;
        height: 24px;
      }
      
      &--medium {
        width: 32px;
        height: 32px;
      }
      
      &--large {
        width: 40px;
        height: 40px;
      }
    }
  }
  
  &__dot {
    position: absolute;
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background-color: var(--primary-color);
    animation: spinner-fade 1.2s linear infinite;
    
    &--small {
      width: 2px;
      height: 2px;
    }
    
    &--large {
      width: 4px;
      height: 4px;
    }
    
    @for $i from 1 through 8 {
      &:nth-child(#{$i}) {
        transform: rotate(#{($i - 1) * 45}deg) translateY(-10px);
        animation-delay: #{($i - 1) * 0.15}s;
        
        .quant-loading__spinner-inner--small & {
          transform: rotate(#{($i - 1) * 45}deg) translateY(-8px);
        }
        
        .quant-loading__spinner-inner--large & {
          transform: rotate(#{($i - 1) * 45}deg) translateY(-12px);
        }
      }
    }
  }
  
  // 圆形进度条
  &__circle {
    &-svg {
      animation: circle-rotate 2s linear infinite;
      
      &--small {
        width: 24px;
        height: 24px;
      }
      
      &--medium {
        width: 32px;
        height: 32px;
      }
      
      &--large {
        width: 40px;
        height: 40px;
      }
    }
    
    &-path {
      stroke: var(--primary-color);
      stroke-dasharray: 90, 150;
      stroke-dashoffset: 0;
      stroke-linecap: round;
      animation: circle-dash 1.5s ease-in-out infinite;
      
      &--custom {
        stroke: v-bind(color);
      }
    }
  }
  
  // 点状动画
  &__dots {
    display: flex;
    gap: var(--spacing-1);
    
    &-item {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--primary-color);
      animation: dots-bounce 1.4s ease-in-out infinite both;
      
      &--small {
        width: 6px;
        height: 6px;
      }
      
      &--large {
        width: 10px;
        height: 10px;
      }
      
      @for $i from 1 through 3 {
        &:nth-child(#{$i}) {
          animation-delay: #{($i - 1) * 0.16}s;
        }
      }
    }
  }
  
  // 波浪动画
  &__wave {
    display: flex;
    gap: 2px;
    
    &-item {
      width: 4px;
      background-color: var(--primary-color);
      border-radius: 2px;
      animation: wave-stretch 1.2s ease-in-out infinite;
      
      &--small {
        width: 3px;
        height: 16px;
      }
      
      &--medium {
        width: 4px;
        height: 20px;
      }
      
      &--large {
        width: 5px;
        height: 24px;
      }
      
      @for $i from 1 through 5 {
        &:nth-child(#{$i}) {
          animation-delay: #{($i - 1) * 0.1}s;
        }
      }
    }
  }
  
  // 自定义图标
  &__custom {
    &-icon {
      color: var(--primary-color);
      animation: custom-spin 1s linear infinite;
      
      &--small {
        animation-duration: 0.8s;
      }
      
      &--large {
        animation-duration: 1.2s;
      }
    }
  }
  
  // 文本
  &__text {
    margin-top: var(--spacing-2);
    font-size: var(--font-size-sm);
    color: var(--text-primary);
    text-align: center;
  }
}

// 动画
@keyframes spinner-fade {
  0%, 39%, 100% {
    opacity: 0.2;
  }
  40% {
    opacity: 1;
  }
}

@keyframes circle-rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes circle-dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

@keyframes dots-bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes wave-stretch {
  0%, 40%, 100% {
    transform: scaleY(0.4);
  }
  20% {
    transform: scaleY(1);
  }
}

@keyframes custom-spin {
  100% {
    transform: rotate(360deg);
  }
}
</style>