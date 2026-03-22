<template>
  <div class="mode-switch">
    <button
      v-for="option in options"
      :key="option.value"
      :class="['mode-btn', { active: modelValue === option.value }]"
      @click="handleClick(option.value)"
    >
      <span v-html="option.icon"></span>
      {{ option.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
interface ModeOption {
  value: string | boolean | number
  label: string
  icon?: string
}

interface Props {
  modelValue: string | boolean | number
  options: ModeOption[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string | boolean | number]
  'change': [value: string | boolean | number]
}>()

const handleClick = (value: string | boolean | number) => {
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style lang="scss" scoped>
.mode-switch {
  display: flex;
  gap: 2px;
  padding: 3px;
  background: var(--bg-tertiary, #2a2e39);
  border-radius: 6px;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-secondary, #cbd5e1);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  :deep(svg) {
    width: 14px;
    height: 14px;
  }

  &:hover:not(.active) {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-primary, #d1d4dc);
  }

  &.active {
    background: var(--accent-blue, #2962ff);
    color: #fff;
  }
}
</style>
