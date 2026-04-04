<template>
  <button
    class="refresh-btn"
    :class="[size, { spinning: loading }]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-html="iconSvg" class="refresh-icon"></span>
    <span v-if="label" class="refresh-label">{{ label }}</span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  loading?: boolean
  disabled?: boolean
  label?: string
  icon?: string
  size?: 'default' | 'small'
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false,
  label: '',
  icon: '',
  size: 'default'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const defaultIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>'

const iconSvg = computed(() => props.icon || defaultIcon)

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<script lang="ts">
import { computed } from 'vue'
export default {
  name: 'RefreshButton'
}
</script>

<style lang="scss" scoped>
.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-tertiary, #2a2e39);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 4px;
  color: var(--text-primary, #d1d4dc);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &.small {
    padding: 6px;
    border-radius: 6px;

    .refresh-icon :deep(svg) {
      width: 14px;
      height: 14px;
    }
  }

  &:hover:not(:disabled) {
    border-color: var(--accent-blue, #2962ff);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .refresh-icon {
    display: flex;
    align-items: center;
    justify-content: center;

    :deep(svg) {
      width: 16px;
      height: 16px;
    }
  }

  &.spinning .refresh-icon {
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
