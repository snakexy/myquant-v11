<template>
  <button
    :class="buttonClass"
    :disabled="disabled || loading"
    :type="nativeType"
    @click="handleClick"
  >
    <span v-if="loading" class="btn-loading">
      <svg class="loading-icon" viewBox="0 0 50 50">
        <circle
          cx="25"
          cy="25"
          r="20"
          fill="none"
          :stroke="currentColor"
          stroke-width="5"
        ></circle>
      </svg>
    </span>
    <span v-if="$slots.icon" class="btn-icon">
      <slot name="icon"></slot>
    </span>
    <span v-if="$slots.default" class="btn-content">
      <slot></slot>
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'text'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
  block?: boolean
  round?: boolean
  circle?: boolean
  plain?: boolean
  nativeType?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default',
  size: 'medium',
  disabled: false,
  loading: false,
  block: false,
  round: false,
  circle: false,
  plain: false,
  nativeType: 'button'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClass = computed(() => {
  return [
    'base-button',
    `btn-${props.type}`,
    `btn-${props.size}`,
    {
      'btn-disabled': props.disabled,
      'btn-loading': props.loading,
      'btn-block': props.block,
      'btn-round': props.round,
      'btn-circle': props.circle,
      'btn-plain': props.plain
    }
  ]
})

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-lg;
  font-size: $font-sm;
  font-weight: 500;
  line-height: 1.5;
  text-align: center;
  text-decoration: none;
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
  border: 1px solid transparent;
  border-radius: $radius-md;
  outline: none;
  transition: all $transition-base;
  position: relative;

  &:hover:not(.btn-disabled):not(.btn-loading) {
    opacity: 0.85;
  }

  &:active:not(.btn-disabled):not(.btn-loading) {
    transform: scale(0.98);
  }

  &.btn-disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &.btn-block {
    display: flex;
    width: 100%;
  }

  &.btn-round {
    border-radius: $radius-full;
  }

  &.btn-circle {
    border-radius: 50%;
    padding: 0;
    width: 36px;
    height: 36px;
  }

  &.btn-plain {
    background: transparent !important;
  }

  // 尺寸
  &.btn-small {
    padding: $spacing-xs $spacing-md;
    font-size: $font-xs;

    &.btn-circle {
      width: 28px;
      height: 28px;
    }
  }

  &.btn-medium {
    padding: $spacing-sm $spacing-lg;
    font-size: $font-sm;

    &.btn-circle {
      width: 36px;
      height: 36px;
    }
  }

  &.btn-large {
    padding: $spacing-md $spacing-xl;
    font-size: $font-md;

    &.btn-circle {
      width: 44px;
      height: 44px;
    }
  }

  // 类型
  &.btn-primary {
    background: $primary-color;
    border-color: $primary-color;
    color: white;

    &.btn-plain {
      border-color: $primary-color;
      color: $primary-color;
    }
  }

  &.btn-secondary {
    background: $secondary-color;
    border-color: $secondary-color;
    color: white;

    &.btn-plain {
      border-color: $secondary-color;
      color: $secondary-color;
    }
  }

  &.btn-success {
    background: $success-color;
    border-color: $success-color;
    color: white;

    &.btn-plain {
      border-color: $success-color;
      color: $success-color;
    }
  }

  &.btn-warning {
    background: $warning-color;
    border-color: $warning-color;
    color: white;

    &.btn-plain {
      border-color: $warning-color;
      color: $warning-color;
    }
  }

  &.btn-danger {
    background: $error-color;
    border-color: $error-color;
    color: white;

    &.btn-plain {
      border-color: $error-color;
      color: $error-color;
    }
  }

  &.btn-text {
    background: transparent;
    border-color: transparent;
    color: $text-primary;

    &:hover:not(.btn-disabled):not(.btn-loading) {
      background: $bg-hover;
    }
  }
}

.btn-loading {
  display: inline-flex;
  align-items: center;
}

.loading-icon {
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.btn-icon {
  display: inline-flex;
  align-items: center;
}

.btn-content {
  display: inline-flex;
  align-items: center;
}
</style>
