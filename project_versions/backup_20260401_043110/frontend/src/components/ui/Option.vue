<template>
  <div
    class="quant-option"
    :class="optionClass"
    @click="handleClick"
  >
    <slot>{{ label }}</slot>
  </div>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'
import type { OptionProps } from '@/types/components'

const props = withDefaults(defineProps<OptionProps>(), {
  disabled: false
})

const emit = defineEmits<{
  click: [value: any]
}>()

// 注入父组件的select实例
const select = inject('select', null)

const optionClass = computed(() => [
  {
    'is-disabled': props.disabled,
    'is-selected': select?.isSelected?.(props.value)
  }
])

const handleClick = () => {
  if (props.disabled) return
  emit('click', props.value)
  select?.handleSelect?.(props)
}
</script>

<style lang="scss" scoped>
.quant-option {
  padding: var(--spacing-2) var(--spacing-3);
  cursor: pointer;
  transition: background-color var(--transition-duration-base) var(--transition-timing-function-base);
  
  &:hover {
    background-color: var(--bg-color-secondary);
  }
  
  &.is-selected {
    background-color: rgba(var(--primary-color), 0.1);
    color: var(--primary-color);
  }
  
  &.is-disabled {
    color: var(--text-disabled);
    cursor: not-allowed;
  }
}
</style>