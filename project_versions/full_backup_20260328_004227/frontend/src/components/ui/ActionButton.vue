<template>
  <button
    class="action-btn"
    :class="[type, size, { loading, disabled, 'icon-only': iconOnly }]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="spinner"></span>
    <span v-else-if="icon" v-html="icon" class="btn-icon"></span>
    <span v-if="!iconOnly && label" class="btn-label">{{ label }}</span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  label?: string
  icon?: string
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'default'
  size?: 'small' | 'medium' | 'large'
  loading?: boolean
  disabled?: boolean
  iconOnly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  label: '',
  icon: '',
  type: 'default',
  size: 'medium',
  loading: false,
  disabled: false,
  iconOnly: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid transparent;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-icon {
    display: flex;
    align-items: center;
    justify-content: center;

    :deep(svg) {
      width: 14px;
      height: 14px;
    }
  }

  // 尺寸
  &.small {
    padding: 4px 10px;
    font-size: 11px;
    height: 26px;
    box-sizing: border-box;

    &.icon-only {
      padding: 4px;
      width: 26px;
    }

    .btn-icon :deep(svg) {
      width: 12px;
      height: 12px;
    }
  }

  &.medium {
    padding: 6px 14px;
    font-size: 12px;
  }

  &.large {
    padding: 8px 18px;
    font-size: 14px;
  }

  // 类型
  &.primary {
    background: var(--accent-blue, #2962ff);
    color: #fff;

    &:hover:not(:disabled) {
      background: #1e4cd9;
    }
  }

  &.success {
    background: #26a69a;
    color: #fff;

    &:hover:not(:disabled) {
      background: #1e8a80;
    }
  }

  &.warning {
    background: #ff9800;
    color: #fff;

    &:hover:not(:disabled) {
      background: #e68a00;
    }
  }

  &.danger {
    background: #ef5350;
    color: #fff;

    &:hover:not(:disabled) {
      background: #d32f2f;
    }
  }

  &.default {
    background: var(--bg-tertiary, #2a2e39);
    border-color: var(--border-color, #2a2e39);
    color: var(--text-primary, #d1d4dc);

    &:hover:not(:disabled) {
      border-color: var(--accent-blue, #2962ff);
    }
  }

  // 仅图标
  &.icon-only {
    &.small { width: 26px; }
    &.medium { width: 28px; height: 28px; }
    &.large { width: 32px; height: 32px; }
  }

  // 加载状态
  &.loading {
    position: relative;
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
