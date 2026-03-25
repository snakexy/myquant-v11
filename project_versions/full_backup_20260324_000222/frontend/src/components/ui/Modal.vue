<template>
  <teleport to="body">
    <transition name="quant-modal" appear>
      <div v-if="visible" :class="containerClass" @click="handleMaskClick">
        <div :class="dialogClass" :style="dialogStyle" @click.stop>
          <!-- 头部 -->
          <div v-if="showHeader" :class="headerClass">
            <div :class="titleClass">
              <n-icon v-if="icon" :size="20" class="quant-modal__icon">
                <component :is="icon" />
              </n-icon>
              <slot name="title">{{ title }}</slot>
            </div>
            <button v-if="closable" :class="closeClass" @click="handleClose">
              <n-icon :size="16">
                <CloseOutline />
              </n-icon>
            </button>
          </div>
          
          <!-- 内容 -->
          <div :class="bodyClass">
            <slot />
          </div>
          
          <!-- 底部 -->
          <div v-if="showFooter" :class="footerClass">
            <slot name="footer">
              <QuantButton
                v-if="showCancelButton"
                type="ghost"
                size="medium"
                @click="handleCancel"
              >
                {{ cancelText }}
              </QuantButton>
              <QuantButton
                v-if="showConfirmButton"
                type="primary"
                size="medium"
                :loading="confirmLoading"
                @click="handleConfirm"
              >
                {{ confirmText }}
              </QuantButton>
            </slot>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { computed, watch, nextTick, ref } from 'vue'
import { NIcon } from 'naive-ui'
import { CloseOutline } from '@vicons/ionicons5'
import QuantButton from './Button.vue'
import type { Component } from 'vue'

interface Props {
  visible?: boolean
  title?: string
  width?: string | number
  height?: string | number
  maxWidth?: string | number
  maxHeight?: string | number
  centered?: boolean
  closable?: boolean
  maskClosable?: boolean
  showHeader?: boolean
  showFooter?: boolean
  showCancelButton?: boolean
  showConfirmButton?: boolean
  cancelText?: string
  confirmText?: string
  confirmLoading?: boolean
  destroyOnClose?: boolean
  zIndex?: number
  icon?: Component
  mask?: boolean
  lockScroll?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  title: '',
  width: '520px',
  height: 'auto',
  maxWidth: '90vw',
  maxHeight: '90vh',
  centered: false,
  closable: true,
  maskClosable: true,
  showHeader: true,
  showFooter: true,
  showCancelButton: true,
  showConfirmButton: true,
  cancelText: '取消',
  confirmText: '确定',
  confirmLoading: false,
  destroyOnClose: false,
  zIndex: 1000,
  icon: undefined,
  mask: true,
  lockScroll: true
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  close: []
  cancel: []
  confirm: []
  afterOpen: []
  afterClose: []
}>()

const dialogRef = ref<HTMLElement>()

const containerClass = computed(() => {
  const classes = ['quant-modal']
  
  if (props.mask) classes.push('quant-modal--mask')
  if (props.centered) classes.push('quant-modal--centered')
  
  return classes
})

const dialogClass = computed(() => {
  const classes = ['quant-modal__dialog']
  
  if (!props.showHeader) classes.push('quant-modal__dialog--no-header')
  if (!props.showFooter) classes.push('quant-modal__dialog--no-footer')
  
  return classes
})

const headerClass = computed(() => {
  const classes = ['quant-modal__header']
  
  if (props.icon) classes.push('quant-modal__header--with-icon')
  
  return classes
})

const titleClass = computed(() => {
  const classes = ['quant-modal__title']
  
  if (props.icon) classes.push('quant-modal__title--with-icon')
  
  return classes
})

const closeClass = computed(() => {
  return ['quant-modal__close']
})

const bodyClass = computed(() => {
  return ['quant-modal__body']
})

const footerClass = computed(() => {
  return ['quant-modal__footer']
})

const dialogStyle = computed(() => {
  const style: Record<string, string> = {}
  
  // 宽度
  if (typeof props.width === 'number') {
    style.width = `${props.width}px`
  } else {
    style.width = props.width
  }
  
  // 高度
  if (typeof props.height === 'number') {
    style.height = `${props.height}px`
  } else if (props.height !== 'auto') {
    style.height = props.height
  }
  
  // 最大宽�?
  if (typeof props.maxWidth === 'number') {
    style.maxWidth = `${props.maxWidth}px`
  } else {
    style.maxWidth = props.maxWidth
  }
  
  // 最大高�?
  if (typeof props.maxHeight === 'number') {
    style.maxHeight = `${props.maxHeight}px`
  } else {
    style.maxHeight = props.maxHeight
  }
  
  // 层级
  style.zIndex = props.zIndex.toString()
  
  return style
})

const handleMaskClick = () => {
  if (props.maskClosable && props.mask) {
    handleClose()
  }
}

const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleCancel = () => {
  emit('update:visible', false)
  emit('cancel')
}

const handleConfirm = () => {
  emit('confirm')
}

// 监听visible变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    // 打开时锁定滚�?
    if (props.lockScroll) {
      document.body.style.overflow = 'hidden'
    }
    
    nextTick(() => {
      emit('afterOpen')
    })
  } else {
    // 关闭时恢复滚�?
    if (props.lockScroll) {
      document.body.style.overflow = ''
    }
    
    nextTick(() => {
      emit('afterClose')
    })
  }
})

// 暴露方法
defineExpose({
  dialogRef
})
</script>

<style lang="scss" scoped>
.quant-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--spacing-4);
  overflow: auto;
  z-index: 1000;
  
  &--mask {
    background-color: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(2px);
  }
  
  &--centered {
    align-items: center;
  }
  
  // 对话�?
  &__dialog {
    position: relative;
    display: flex;
    flex-direction: column;
    background-color: var(--bg-color-base);
    border-radius: var(--border-radius-lg);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    overflow: hidden;
    transform: scale(0.8);
    opacity: 0;
    transition: all var(--transition-duration-base) var(--transition-timing-function-base);
    
    &--no-header {
      border-top-left-radius: var(--border-radius-lg);
      border-top-right-radius: var(--border-radius-lg);
    }
    
    &--no-footer {
      border-bottom-left-radius: var(--border-radius-lg);
      border-bottom-right-radius: var(--border-radius-lg);
    }
  }
  
  // 头部
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-4) var(--spacing-4) var(--spacing-3);
    border-bottom: 1px solid var(--border-color)-base;
    
    &--with-icon {
      padding-left: var(--spacing-3);
    }
  }
  
  // 标题
  &__title {
    display: flex;
    align-items: center;
    font-size: var(--font-size-lg);
    font-weight: 600;
    color: var(--text-primary);
    
    &--with-icon {
      gap: var(--spacing-2);
    }
  }
  
  // 图标
  &__icon {
    color: var(--primary-color);
  }
  
  // 关闭按钮
  &__close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border: none;
    border-radius: var(--border-radius-base);
    background-color: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--transition-duration-base) var(--transition-timing-function-base);
    
    &:hover {
      background-color: var(--bg-color-secondary);
      color: var(--text-primary);
    }
  }
  
  // 内容
  &__body {
    flex: 1;
    padding: var(--spacing-4);
    overflow: auto;
    color: var(--text-primary);
    line-height: 1.6;
  }
  
  // 底部
  &__footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: var(--spacing-2);
    padding: var(--spacing-3) var(--spacing-4) var(--spacing-4);
    border-top: 1px solid var(--border-color)-base;
  }
}

// 动画
.quant-modal-enter-active,
.quant-modal-leave-active {
  transition: all var(--transition-duration-base) var(--transition-timing-function-base);
}

.quant-modal-enter-from,
.quant-modal-leave-to {
  opacity: 0;
  
  .quant-modal__dialog {
    transform: scale(0.8) translateY(-20px);
  }
}

.quant-modal-enter-to,
.quant-modal-leave-from {
  opacity: 1;
  
  .quant-modal__dialog {
    transform: scale(1) translateY(0);
  }
}
</style>
