<template>
  <div class="custom-select" ref="selectRef">
    <div
      class="select-trigger"
      :class="{ disabled, focused }"
      @click="toggleDropdown"
      @keydown="handleKeydown"
      tabindex="0"
    >
      <span class="select-value">{{ displayValue }}</span>
      <svg class="select-arrow" :class="{ open: isOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </div>

    <Transition name="dropdown">
      <div v-if="isOpen" class="select-dropdown">
        <div
          v-for="option in options"
          :key="option.value"
          class="select-option"
          :class="{ selected: option.value === modelValue, highlighted: option.value === highlightedValue }"
          @click="selectOption(option)"
          @mouseenter="highlightedValue = option.value"
        >
          <span class="option-text">{{ option.label }}</span>
          <svg v-if="option.value === modelValue" class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Option {
  value: string | number
  label: string
}

const props = defineProps<{
  modelValue: string | number
  options: Option[]
  disabled?: boolean
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
}>()

const selectRef = ref<HTMLElement | null>(null)
const isOpen = ref(false)
const focused = ref(false)
const highlightedValue = ref<string | number | null>(null)

const displayValue = computed(() => {
  const option = props.options.find(opt => opt.value === props.modelValue)
  return option ? option.label : props.placeholder || 'Select...'
})

const toggleDropdown = () => {
  if (props.disabled) return
  isOpen.value = !isOpen.value
  if (isOpen.value && props.options.length > 0) {
    highlightedValue.value = props.modelValue
  }
}

const selectOption = (option: Option) => {
  emit('update:modelValue', option.value)
  isOpen.value = false
}

const handleKeydown = (e: KeyboardEvent) => {
  if (props.disabled) return

  switch (e.key) {
    case 'Enter':
    case ' ':
      e.preventDefault()
      if (isOpen.value && highlightedValue.value !== null) {
        const option = props.options.find(opt => opt.value === highlightedValue.value)
        if (option) selectOption(option)
      } else {
        toggleDropdown()
      }
      break
    case 'Escape':
      isOpen.value = false
      break
    case 'ArrowDown':
      e.preventDefault()
      navigateOption(1)
      break
    case 'ArrowUp':
      e.preventDefault()
      navigateOption(-1)
      break
  }
}

const navigateOption = (direction: number) => {
  if (!isOpen.value) {
    toggleDropdown()
    return
  }

  const currentIndex = props.options.findIndex(opt => opt.value === highlightedValue.value)
  let newIndex = currentIndex + direction

  if (newIndex < 0) newIndex = props.options.length - 1
  if (newIndex >= props.options.length) newIndex = 0

  highlightedValue.value = props.options[newIndex].value
}

const handleClickOutside = (e: MouseEvent) => {
  if (selectRef.value && !selectRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.custom-select {
  position: relative;
  width: 100%;
}

.select-trigger {
  padding: 10px 12px;
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 4px;
  color: var(--text-primary, #d1d4dc);
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: border-color 0.15s, box-shadow 0.15s;
  user-select: none;
}

.select-trigger:hover {
  border-color: var(--accent-blue, #2962ff);
}

.select-trigger.focused {
  border-color: var(--accent-blue, #2962ff);
  box-shadow: 0 0 0 2px rgba(41, 98, 255, 0.2);
}

.select-trigger.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.select-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-arrow {
  width: 16px;
  height: 16px;
  color: var(--text-secondary, #787b86);
  transition: transform 0.2s;
  flex-shrink: 0;
  margin-left: 8px;
}

.select-arrow.open {
  transform: rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  max-height: 240px;
  overflow-y: auto;
}

.select-option {
  padding: 10px 12px;
  color: var(--text-primary, #d1d4dc);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background 0.1s;
}

.select-option:hover,
.select-option.highlighted {
  background: var(--bg-tertiary, #2a2e39);
}

.select-option.selected {
  color: var(--accent-blue, #2962ff);
  background: rgba(41, 98, 255, 0.1);
}

.select-option.selected:hover,
.select-option.selected.highlighted {
  background: rgba(41, 98, 255, 0.15);
}

.option-text {
  flex: 1;
}

.check-icon {
  width: 14px;
  height: 14px;
  color: var(--accent-blue, #2962ff);
  flex-shrink: 0;
}

/* Dropdown animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Scrollbar */
.select-dropdown::-webkit-scrollbar {
  width: 6px;
}

.select-dropdown::-webkit-scrollbar-track {
  background: var(--bg-primary, #131722);
}

.select-dropdown::-webkit-scrollbar-thumb {
  background: var(--bg-tertiary, #2a2e39);
  border-radius: 3px;
}

.select-dropdown::-webkit-scrollbar-thumb:hover {
  background: #363a45;
}
</style>
