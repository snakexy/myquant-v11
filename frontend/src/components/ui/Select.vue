<template>
  <div class="quant-select" :class="selectClass">
    <div
      class="quant-select__wrapper"
      @click="handleToggle"
    >
      <div class="quant-select__input">
        <span v-if="multiple && Array.isArray(modelValue)" class="quant-select__tags">
          <span
            v-for="item in selectedItems"
            :key="item.value"
            class="quant-select__tag"
          >
            {{ item.label }}
            <span class="quant-select__tag-close" @click.stop="handleRemoveTag(item)">
              ×
            </span>
          </span>
        </span>
        <span v-else class="quant-select__value">
          {{ displayText }}
        </span>
      </div>
      <div class="quant-select__suffix">
        <n-icon v-if="loading" class="quant-select__loading">
          <RefreshOutline />
        </n-icon>
        <n-icon v-else class="quant-select__arrow" :class="{ 'is-reverse': dropdownVisible }">
          <ChevronDownOutline />
        </n-icon>
        <n-icon
          v-if="clearable && hasValue"
          class="quant-select__clear"
          @click.stop="handleClear"
        >
          <CloseCircle />
        </n-icon>
      </div>
    </div>
    
    <div v-show="dropdownVisible" class="quant-select__dropdown">
      <div v-if="filterable" class="quant-select__search">
        <QuantInput
          v-model:value="searchQuery"
          placeholder="搜索..."
          prefix-icon="SearchOutline"
          @input="handleSearch"
        />
      </div>
      
      <div v-if="filteredOptions.length === 0" class="quant-select__empty">
        {{ noDataText }}
      </div>
      
      <div v-else class="quant-select__options">
        <div
          v-for="option in filteredOptions"
          :key="option.value"
          class="quant-select__option"
          :class="getOptionClass(option)"
          @click="handleSelect(option)"
        >
          <QuantCheckbox
            v-if="multiple"
            :model-value="isSelected(option)"
            @update:model-value="() => handleSelect(option)"
          />
          <span class="quant-select__option-text">{{ option.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { NIcon } from 'naive-ui'
import {
  RefreshOutline,
  ChevronDownOutline,
  CloseCircle,
  SearchOutline
} from '@vicons/ionicons5'
import QuantInput from './Input.vue'
import QuantCheckbox from './Checkbox.vue'
import type { SelectProps, OptionProps } from '@/types/components'

const props = withDefaults(defineProps<SelectProps>(), {
  placeholder: '请选择',
  clearable: false,
  multiple: false,
  filterable: false,
  loading: false,
  loadingText: '加载中...',
  noMatchText: '无匹配数据',
  noDataText: '无数据',
  teleported: false,
  persistent: true,
  automaticDropdown: false,
  fitInputWidth: true,
  size: 'medium'
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | Array<string | number>]
  'change': [value: string | number | Array<string | number>]
  'visible-change': [visible: boolean]
  'remove-tag': [value: string | number]
  'clear': []
  'blur': [event: FocusEvent]
  'focus': [event: FocusEvent]
}>()

// 响应式数据
const dropdownVisible = ref(false)
const searchQuery = ref('')
const selectRef = ref<HTMLElement>()

// 计算属性
const selectClass = computed(() => [
  `quant-select--${props.size}`,
  {
    'is-disabled': props.disabled,
    'is-loading': props.loading
  }
])

const hasValue = computed(() => {
  if (props.multiple) {
    return Array.isArray(props.modelValue) && props.modelValue.length > 0
  }
  return props.modelValue !== undefined && props.modelValue !== null && props.modelValue !== ''
})

const selectedItems = computed(() => {
  if (props.multiple && Array.isArray(props.modelValue)) {
    return props.modelValue.map(value => 
      props.options?.find(option => option.value === value) || { value, label: String(value) }
    )
  }
  return []
})

const displayText = computed(() => {
  if (!hasValue.value) return props.placeholder
  
  if (props.multiple) {
    return `${(props.modelValue as Array<string | number>).length} 项已选择`
  }
  
  const selectedOption = props.options?.find(option => option.value === props.modelValue)
  return selectedOption?.label || String(props.modelValue)
})

const filteredOptions = computed(() => {
  if (!props.options) return []
  
  if (!props.filterable || !searchQuery.value) {
    return props.options
  }
  
  const query = searchQuery.value.toLowerCase()
  return props.options.filter(option =>
    String(option.label).toLowerCase().includes(query)
  )
})

// 方法
const handleToggle = () => {
  if (props.disabled || props.loading) return
  
  dropdownVisible.value = !dropdownVisible.value
  emit('visible-change', dropdownVisible.value)
}

const handleSelect = (option: OptionProps) => {
  if (option.disabled) return
  
  if (props.multiple) {
    const currentValue = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    const index = currentValue.indexOf(option.value)
    
    if (index > -1) {
      currentValue.splice(index, 1)
    } else {
      currentValue.push(option.value)
    }
    
    emit('update:modelValue', currentValue)
    emit('change', currentValue)
  } else {
    emit('update:modelValue', option.value)
    emit('change', option.value)
    dropdownVisible.value = false
  }
}

const isSelected = (option: OptionProps) => {
  if (props.multiple && Array.isArray(props.modelValue)) {
    return props.modelValue.includes(option.value)
  }
  return props.modelValue === option.value
}

const getOptionClass = (option: OptionProps) => ({
  'is-selected': isSelected(option),
  'is-disabled': option.disabled
})

const handleRemoveTag = (item: any) => {
  if (props.multiple && Array.isArray(props.modelValue)) {
    const newValue = props.modelValue.filter(value => value !== item.value)
    emit('update:modelValue', newValue)
    emit('change', newValue)
    emit('remove-tag', item.value)
  }
}

const handleClear = () => {
  if (props.multiple) {
    emit('update:modelValue', [])
    emit('change', [])
  } else {
    emit('update:modelValue', '')
    emit('change', '')
  }
  emit('clear')
}

const handleSearch = (query: string) => {
  searchQuery.value = query
}

const handleClickOutside = (event: MouseEvent) => {
  if (selectRef.value && !selectRef.value.contains(event.target as Node)) {
    dropdownVisible.value = false
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 监听
watch(dropdownVisible, (visible) => {
  if (visible) {
    searchQuery.value = ''
  }
})
</script>

<style lang="scss" scoped>
.quant-select {
  position: relative;
  width: 100%;
  
  &__wrapper {
    position: relative;
    display: flex;
    align-items: center;
    padding: 0 var(--spacing-2);
    height: 32px;
    background-color: var(--bg-color-base);
    border: 1px solid var(--border-color)-base;
    border-radius: var(--border-radius-base);
    cursor: pointer;
    transition: all var(--transition-duration-base) var(--transition-timing-function-base);
    
    &:hover {
      border-color: var(--primary-color);
    }
    
    &:focus {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px rgba(var(--primary-color), 0.2);
    }
  }
  
  &--small &__wrapper {
    height: 24px;
    padding: 0 var(--spacing-1);
    font-size: var(--font-size-sm);
  }
  
  &--large &__wrapper {
    height: 40px;
    padding: 0 var(--spacing-3);
    font-size: var(--font-size-lg);
  }
  
  &--disabled &__wrapper {
    background-color: var(--bg-color-secondary);
    color: var(--text-disabled);
    cursor: not-allowed;
  }
  
  &__input {
    flex: 1;
    overflow: hidden;
  }
  
  &__tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-1);
  }
  
  &__tag {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-1);
    padding: 0 var(--spacing-1);
    background-color: var(--primary-color);
    color: white;
    border-radius: var(--border-radius-sm);
    font-size: var(--font-size-sm);
  }
  
  &__tag-close {
    cursor: pointer;
    opacity: 0.7;
    
    &:hover {
      opacity: 1;
    }
  }
  
  &__value {
    color: var(--text-primary);
  }
  
  &__suffix {
    display: flex;
    align-items: center;
    gap: var(--spacing-1);
    color: var(--text-secondary);
  }
  
  &__arrow {
    transition: transform var(--transition-duration-base) var(--transition-timing-function-base);
    
    &.is-reverse {
      transform: rotate(180deg);
    }
  }
  
  &__clear {
    cursor: pointer;
    color: var(--text-secondary);
    
    &:hover {
      color: var(--text-primary);
    }
  }
  
  &__dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    z-index: 1000;
    background-color: var(--bg-color-base);
    border: 1px solid var(--border-color)-base;
    border-radius: var(--border-radius-base);
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-top: 4px;
  }
  
  &__search {
    padding: var(--spacing-2);
    border-bottom: 1px solid var(--border-color)-base;
  }
  
  &__empty {
    padding: var(--spacing-3);
    text-align: center;
    color: var(--text-secondary);
  }
  
  &__options {
    max-height: 200px;
    overflow-y: auto;
  }
  
  &__option {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
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
  
  &__option-text {
    flex: 1;
  }
}
</style>