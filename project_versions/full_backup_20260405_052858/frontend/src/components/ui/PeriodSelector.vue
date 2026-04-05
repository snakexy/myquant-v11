<template>
  <div class="period-selector">
    <button
      v-for="option in options"
      :key="option.value"
      :class="['period-btn', { active: modelValue === option.value }]"
      @click="handleClick(option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
interface PeriodOption {
  value: string
  label: string
}

interface Props {
  modelValue: string
  options: PeriodOption[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const handleClick = (value: string) => {
  emit('update:modelValue', value)
}
</script>

<style lang="scss" scoped>
.period-selector {
  display: inline-flex;
  gap: 2px;
  padding: 3px;
  background: var(--bg-tertiary, #2a2e39);
  border-radius: 6px;
}

.period-btn {
  padding: 4px 12px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-secondary, #cbd5e1);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

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
