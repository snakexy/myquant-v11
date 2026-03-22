<template>
  <div :class="containerClass">
    <label v-if="label" :for="inputId" :class="labelClass">
      {{ label }}
      <span v-if="required" class="quant-input__required">*</span>
    </label>
    
    <div :class="wrapperClass">
      <n-icon v-if="prefixIcon" :size="iconSize" class="quant-input__prefix-icon">
        <component :is="prefixIcon" />
      </n-icon>
      
      <input
        :id="inputId"
        ref="inputRef"
        :class="inputClass"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        :autocomplete="autocomplete"
        :name="name"
        @input="handleInput"
        @change="handleChange"
        @focus="handleFocus"
        @blur="handleBlur"
        @keyup="handleKeyup"
        @keydown="handleKeydown"
      />
      
      <n-icon v-if="suffixIcon" :size="iconSize" class="quant-input__suffix-icon">
        <component :is="suffixIcon" />
      </n-icon>
      
      <n-icon v-if="showPasswordToggle" :size="iconSize" class="quant-input__password-toggle" @click="togglePasswordVisibility">
        <EyeOutline v-if="showPassword" />
        <EyeOffOutline v-else />
      </n-icon>
      
      <div v-if="showWordLimit && maxlength" class="quant-input__word-limit">
        {{ currentLength }}/{{ maxlength }}
      </div>
    </div>
    
    <div v-if="helperText || errorMessage" :class="messageClass">
      {{ errorMessage || helperText }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, watch } from 'vue'
import { NIcon } from 'naive-ui'
import { EyeOutline, EyeOffOutline } from '@vicons/ionicons5'
import type { Component } from 'vue'

interface Props {
  modelValue?: string | number
  type?: 'text' | 'password' | 'number' | 'email' | 'tel' | 'url'
  size?: 'small' | 'medium' | 'large'
  label?: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  clearable?: boolean
  showPassword?: boolean
  showWordLimit?: boolean
  maxlength?: number
  autocomplete?: string
  name?: string
  prefixIcon?: Component
  suffixIcon?: Component
  helperText?: string
  errorMessage?: string
  validateTrigger?: 'blur' | 'change' | 'both'
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  type: 'text',
  size: 'medium',
  placeholder: '',
  disabled: false,
  readonly: false,
  required: false,
  clearable: false,
  showPassword: false,
  showWordLimit: false,
  maxlength: undefined,
  autocomplete: 'off',
  name: '',
  prefixIcon: undefined,
  suffixIcon: undefined,
  helperText: '',
  errorMessage: '',
  validateTrigger: 'blur'
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  input: [event: Event, value: string | number]
  change: [event: Event, value: string | number]
  focus: [event: FocusEvent]
  blur: [event: FocusEvent]
  keyup: [event: KeyboardEvent]
  keydown: [event: KeyboardEvent]
  clear: []
}>()

const inputRef = ref<HTMLInputElement>()
const isFocused = ref(false)
const showPassword = ref(props.type === 'password' ? false : true)
const inputId = computed(() => `quant-input-${Math.random().toString(36).substr(2, 9)}`)

const currentLength = computed(() => {
  const value = props.modelValue || ''
  return value.toString().length
})

const containerClass = computed(() => {
  const classes = ['quant-input']
  
  if (props.size) classes.push(`quant-input--${props.size}`)
  if (props.disabled) classes.push('quant-input--disabled')
  if (props.readonly) classes.push('quant-input--readonly')
  if (props.errorMessage) classes.push('quant-input--error')
  if (isFocused.value) classes.push('quant-input--focused')
  
  return classes
})

const labelClass = computed(() => {
  const classes = ['quant-input__label']
  if (props.required) classes.push('quant-input__label--required')
  return classes
})

const wrapperClass = computed(() => {
  const classes = ['quant-input__wrapper']
  
  if (props.prefixIcon) classes.push('quant-input__wrapper--prefix')
  if (props.suffixIcon || props.showPassword || props.showWordLimit) classes.push('quant-input__wrapper--suffix')
  
  return classes
})

const inputClass = computed(() => {
  const classes = ['quant-input__inner']
  
  if (props.prefixIcon) classes.push('quant-input__inner--prefix')
  if (props.suffixIcon || props.showPassword || props.showWordLimit) classes.push('quant-input__inner--suffix')
  
  return classes
})

const messageClass = computed(() => {
  const classes = ['quant-input__message']
  if (props.errorMessage) classes.push('quant-input__message--error')
  return classes
})

const iconSize = computed(() => {
  const sizeMap = {
    small: 14,
    medium: 16,
    large: 18
  }
  return sizeMap[props.size]
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  let value: string | number = target.value
  
  if (props.type === 'number') {
    value = target.valueAsNumber || 0
  }
  
  emit('update:modelValue', value)
  emit('input', event, value)
  
  if (props.validateTrigger === 'change' || props.validateTrigger === 'both') {
    // 触发验证
  }
}

const handleChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  let value: string | number = target.value
  
  if (props.type === 'number') {
    value = target.valueAsNumber || 0
  }
  
  emit('change', event, value)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
  
  if (props.validateTrigger === 'blur' || props.validateTrigger === 'both') {
    // 触发验证
  }
}

const handleKeyup = (event: KeyboardEvent) => {
  emit('keyup', event)
}

const handleKeydown = (event: KeyboardEvent) => {
  emit('keydown', event)
}

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const focus = () => {
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const blur = () => {
  nextTick(() => {
    inputRef.value?.blur()
  })
}

const select = () => {
  nextTick(() => {
    inputRef.value?.select()
  })
}

// 监听showPassword属性变化
watch(() => props.showPassword, (newVal) => {
  showPassword.value = newVal
})

// 暴露方法
defineExpose({
  focus,
  blur,
  select,
  inputRef
})
</script>

<style lang="scss" scoped>
.quant-input {
  width: 100%;
  
  // 标签
  &__label {
    display: block;
    margin-bottom: var(--spacing-1);
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--text-primary);
    
    &--required {
      .quant-input__required {
        color: var(--danger-color);
        margin-left: 2px;
      }
    }
  }
  
  // 输入框容器
  &__wrapper {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
    background-color: var(--bg-color-base);
    border: 1px solid var(--border-color)-base;
    border-radius: var(--border-radius-base);
    transition: all var(--transition-duration-base) var(--transition-timing-function-base);
    
    &:hover {
      border-color: var(--border-color)-hover;
    }
    
    &--prefix {
      .quant-input__inner {
        padding-left: 32px;
      }
    }
    
    &--suffix {
      .quant-input__inner {
        padding-right: 32px;
      }
    }
  }
  
  // 输入框
  &__inner {
    width: 100%;
    height: 100%;
    padding: 0 var(--spacing-2);
    font-size: var(--font-size-sm);
    color: var(--text-primary);
    background-color: transparent;
    border: none;
    outline: none;
    transition: all var(--transition-duration-base) var(--transition-timing-function-base);
    
    &::placeholder {
      color: var(--text-muted);
    }
    
    &:disabled {
      cursor: not-allowed;
      color: var(--text-disabled);
    }
    
    &:readonly {
      cursor: default;
      color: var(--text-secondary);
    }
    
    &--prefix {
      padding-left: 32px;
    }
    
    &--suffix {
      padding-right: 32px;
    }
  }
  
  // 前缀图标
  &__prefix-icon {
    position: absolute;
    left: var(--spacing-2);
    color: var(--text-muted);
    pointer-events: none;
  }
  
  // 后缀图标
  &__suffix-icon {
    position: absolute;
    right: var(--spacing-2);
    color: var(--text-muted);
    pointer-events: none;
  }
  
  // 密码切换图标
  &__password-toggle {
    position: absolute;
    right: var(--spacing-2);
    color: var(--text-muted);
    cursor: pointer;
    transition: color var(--transition-duration-base) var(--transition-timing-function-base);
    
    &:hover {
      color: var(--text-primary);
    }
  }
  
  // 字数限制
  &__word-limit {
    position: absolute;
    right: var(--spacing-2);
    font-size: var(--font-size-xs);
    color: var(--text-muted);
    pointer-events: none;
  }
  
  // 错误信息
  &__message {
    margin-top: var(--spacing-1);
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
    
    &--error {
      color: var(--danger-color);
    }
  }
  
  // 尺寸
  &--small {
    .quant-input__wrapper {
      height: 28px;
    }
    
    .quant-input__inner {
      font-size: var(--font-size-xs);
      padding: 0 var(--spacing-1);
    }
    
    .quant-input__prefix-icon,
    .quant-input__suffix-icon,
    .quant-input__password-toggle {
      left: var(--spacing-1);
      right: var(--spacing-1);
    }
  }
  
  &--medium {
    .quant-input__wrapper {
      height: 36px;
    }
    
    .quant-input__inner {
      padding: 0 var(--spacing-2);
    }
  }
  
  &--large {
    .quant-input__wrapper {
      height: 44px;
    }
    
    .quant-input__inner {
      font-size: var(--font-size-base);
      padding: 0 var(--spacing-3);
    }
    
    .quant-input__prefix-icon,
    .quant-input__suffix-icon,
    .quant-input__password-toggle {
      left: var(--spacing-3);
      right: var(--spacing-3);
    }
  }
  
  // 状态
  &--disabled {
    .quant-input__wrapper {
      background-color: #2a2e39;
      border-color: var(--border-color)-disabled;
      cursor: not-allowed;
    }
  }
  
  &--readonly {
    .quant-input__wrapper {
      background-color: var(--bg-color-secondary);
      cursor: default;
    }
  }
  
  &--error {
    .quant-input__wrapper {
      border-color: var(--danger-color);
    }
  }
  
  &--focused {
    .quant-input__wrapper {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 2px rgba(var(--primary-color), 0.2);
    }
  }
}
</style>