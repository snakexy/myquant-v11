<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" :class="modalClass" @click="handleMaskClick">
        <!-- 遮罩 -->
        <div v-if="mask" class="modal-mask" @click="handleMaskClick"></div>

        <!-- 弹窗内容 -->
        <div
          :class="modalContentClass"
          :style="modalStyle"
          @click.stop
        >
          <!-- 关闭按钮 -->
          <div v-if="closable" class="modal-close" @click="handleClose">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </div>

          <!-- 头部 -->
          <div v-if="title || $slots.header" class="modal-header">
            <slot name="header">
              <h3 class="modal-title">{{ title }}</h3>
            </slot>
          </div>

          <!-- 内容 -->
          <div class="modal-body" :class="{ 'no-padding': noPadding }">
            <slot></slot>
          </div>

          <!-- 底部 -->
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch, nextTick } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  width?: string | number
  fullscreen?: boolean
  closable?: boolean
  maskClosable?: boolean
  mask?: boolean
  noPadding?: boolean
  centered?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  width: '520px',
  fullscreen: false,
  closable: true,
  maskClosable: true,
  mask: true,
  noPadding: false,
  centered: false
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  open: []
  close: []
  'after-open': []
  'after-close': []
}>()

const modalClass = computed(() => {
  return [
    'base-modal',
    {
      'modal-centered': props.centered
    }
  ]
})

const modalContentClass = computed(() => {
  return [
    'modal-content',
    {
      'modal-fullscreen': props.fullscreen
    }
  ]
})

const modalStyle = computed(() => {
  if (props.fullscreen) {
    return {}
  }
  return {
    width: typeof props.width === 'number' ? `${props.width}px` : props.width
  }
})

const handleMaskClick = () => {
  if (props.maskClosable && props.mask) {
    handleClose()
  }
}

const handleClose = () => {
  emit('update:modelValue', false)
}

// 监听显示状态
watch(
  () => props.modelValue,
  (value) => {
    if (value) {
      emit('open')
      nextTick(() => {
        emit('after-open')
      })
    } else {
      emit('close')
      nextTick(() => {
        emit('after-close')
      })
    }
  }
)

// ESC键关闭
if (typeof window !== 'undefined') {
  const handleEsc = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && props.modelValue && props.closable) {
      handleClose()
    }
  }
  window.addEventListener('keydown', handleEsc)
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.base-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: $z-modal;
  display: flex;
  overflow: hidden;

  &.modal-centered {
    align-items: center;
    justify-content: center;
  }
}

.modal-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal-content {
  position: relative;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  background: $bg-surface;
  border-radius: $radius-lg;
  box-shadow: $shadow-xl;
  overflow: hidden;
  margin: auto;

  &.modal-fullscreen {
    width: 100vw;
    height: 100vh;
    max-height: 100vh;
    border-radius: 0;
  }
}

.modal-close {
  position: absolute;
  top: $spacing-md;
  right: $spacing-md;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  color: $text-secondary;
  cursor: pointer;
  border-radius: $radius-md;
  transition: all $transition-base;
  z-index: 1;

  &:hover {
    background: $bg-hover;
    color: $text-primary;
  }

  svg {
    width: 20px;
    height: 20px;
  }
}

.modal-header {
  flex-shrink: 0;
  padding: $spacing-lg $spacing-xl;
  border-bottom: 1px solid $border-light;

  .modal-title {
    margin: 0;
    font-size: $font-lg;
    font-weight: 600;
    color: $text-primary;
  }
}

.modal-body {
  flex: 1;
  padding: $spacing-xl;
  overflow-y: auto;

  &.no-padding {
    padding: 0;
  }
}

.modal-footer {
  flex-shrink: 0;
  padding: $spacing-lg $spacing-xl;
  border-top: 1px solid $border-light;
}

// 过渡动画
.modal-enter-active,
.modal-leave-active {
  transition: all $transition-base;

  .modal-mask {
    transition: opacity $transition-base;
  }

  .modal-content {
    transition: all $transition-base;
  }
}

.modal-enter-from,
.modal-leave-to {
  .modal-mask {
    opacity: 0;
  }

  .modal-content {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
}

.modal-enter-to,
.modal-leave-from {
  .modal-mask {
    opacity: 1;
  }

  .modal-content {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
