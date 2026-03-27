<template>
  <label class="quant-checkbox" :class="checkboxClass">
    <input
      ref="checkboxRef"
      type="checkbox"
      class="quant-checkbox__input"
      :disabled="disabled"
      :indeterminate="indeterminate"
      :checked="modelValue"
      @change="handleChange"
    />
    <span class="quant-checkbox__inner">
      <n-icon v-if="modelValue && !indeterminate" class="quant-checkbox__icon">
        <CheckmarkOutline />
      </n-icon>
      <n-icon v-else-if="indeterminate" class="quant-checkbox__icon">
        <RemoveOutline />
      </n-icon>
    </span>
    <span v-if="$slots.default" class="quant-checkbox__label">
      <slot></slot>
    </span>
  </label>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { NIcon } from 'naive-ui'
import { CheckmarkOutline, RemoveOutline } from '@vicons/ionicons5'

interface Props {
  modelValue?: boolean
  disabled?: boolean
  indeterminate?: boolean
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  disabled: false,
  indeterminate: false,
  size: 'medium'
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'change': [value: boolean]
}>()

const checkboxRef = ref<HTMLInputElement>()

const checkboxClass = computed(() => [
  `quant-checkbox--${props.size}`,
  {
    'is-disabled': props.disabled,
    'is-indeterminate': props.indeterminate
  }
])

const handleChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.checked
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style lang="scss" scoped>
.quant-checkbox {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
  
  &__input {
    position: absolute;
    opacity: 0;
    outline: none;
    margin: 0;
    width: 0;
    height: 0;
  }
  
  &__inner {
    position: relative;
    display: inline-block;
    width: 14px;
    height: 14px;
    background-color: var(--bg-color-base);
    border: 1px solid var(--border-color)-base;
    border-radius: var(--border-radius-sm);
    transition: all var(--transition-duration-base) var(--transition-timing-function-base);
    
    &::after {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%) scale(0);
      width: 6px;
      height: 6px;
      background-color: white;
      border-radius: 50%;
      transition: transform var(--transition-duration-base) var(--transition-timing-function-base);
    }
  }
  
  &__icon {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 10px;
    color: white;
  }
  
  &__label {
    margin-left: var(--spacing-2);
    color: var(--text-primary);
  }
  
  &:hover &__inner {
    border-color: var(--primary-color);
  }
  
  &--small &__inner {
    width: 12px;
    height: 12px;
    
    .quant-checkbox__icon {
      font-size: 8px;
    }
  }
  
  &--large &__inner {
    width: 16px;
    height: 16px;
    
    .quant-checkbox__icon {
      font-size: 12px;
    }
  }
  
  &.is-disabled {
    cursor: not-allowed;
    
    .quant-checkbox__inner {
      background-color: var(--bg-color-secondary);
      border-color: var(--border-color)-light;
    }
    
    .quant-checkbox__label {
      color: var(--text-disabled);
    }
  }
  
  &.is-indeterminate {
    .quant-checkbox__inner {
      background-color: var(--primary-color);
      border-color: var(--primary-color);
    }
  }
  
  .quant-checkbox__input:checked + &__inner {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
  }
}
</style>