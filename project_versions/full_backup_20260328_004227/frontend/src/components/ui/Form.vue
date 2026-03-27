<template>
  <form :class="formClass" @submit.prevent="handleSubmit">
    <slot />
    
    <!-- 表单操作按钮 -->
    <div v-if="showActions" class="quant-form__actions">
      <slot name="actions">
        <QuantButton
          v-if="showCancelButton"
          type="ghost"
          size="medium"
          @click="handleCancel"
        >
          {{ cancelText }}
        </QuantButton>
        <QuantButton
          v-if="showSubmitButton"
          type="primary"
          size="medium"
          :loading="loading"
          @click="handleSubmit"
        >
          {{ submitText }}
        </QuantButton>
      </slot>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, provide, ref, reactive, watch } from 'vue'
import QuantButton from './Button.vue'
import type { FormInstance, FormRules, FormItemRule } from '@/types/components'

interface Props {
  modelValue?: Record<string, any>
  rules?: FormRules
  labelWidth?: string | number
  labelPosition?: 'left' | 'right' | 'top'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  readonly?: boolean
  showActions?: boolean
  showCancelButton?: boolean
  showSubmitButton?: boolean
  submitText?: string
  cancelText?: string
  loading?: boolean
  validateOnRuleChange?: boolean
  hideRequiredAsterisk?: boolean
  showMessage?: boolean
  inlineMessage?: boolean
  statusIcon?: boolean
  scrollToError?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => ({}),
  rules: () => ({}),
  labelWidth: '120px',
  labelPosition: 'right',
  size: 'medium',
  disabled: false,
  readonly: false,
  showActions: true,
  showCancelButton: true,
  showSubmitButton: true,
  submitText: '提交',
  cancelText: '取消',
  loading: false,
  validateOnRuleChange: true,
  hideRequiredAsterisk: false,
  showMessage: true,
  inlineMessage: false,
  statusIcon: false,
  scrollToError: true
})

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
  submit: [isValid: boolean, errors: Record<string, string[]>]
  cancel: []
  validate: [isValid: boolean, errors: Record<string, string[]>]
}>()

// 表单数据
const formData = ref<Record<string, any>>({ ...props.modelValue })
const formFields = reactive<Record<string, any>>({})
const formErrors = reactive<Record<string, string[]>>({})

// 表单实例
const formInstance: FormInstance = {
  validate,
  validateField,
  resetFields,
  clearValidate,
  getFieldValue,
  setFieldValue,
  getFieldsValue,
  setFieldsValue
}

// 提供表单上下文
provide('formContext', {
  formData,
  formFields,
  formErrors,
  props,
  addField,
  removeField,
  validateField
})

const formClass = computed(() => {
  const classes = ['quant-form']
  
  if (props.size) classes.push(`quant-form--${props.size}`)
  if (props.disabled) classes.push('quant-form--disabled')
  if (props.readonly) classes.push('quant-form--readonly')
  if (props.labelPosition) classes.push(`quant-form--label-${props.labelPosition}`)
  
  return classes
})

// 添加字段
const addField = (field: any) => {
  formFields[field.prop] = field
}

// 移除字段
const removeField = (field: any) => {
  delete formFields[field.prop]
  delete formErrors[field.prop]
}

// 验证表单
const validate = (): Promise<boolean> => {
  return new Promise((resolve) => {
    const errors: Record<string, string[]> = {}
    let isValid = true
    
    // 验证所有字段
    Object.keys(formFields).forEach(prop => {
      const field = formFields[prop]
      const fieldErrors = validateField(prop, formData.value[prop])
      
      if (fieldErrors.length > 0) {
        errors[prop] = fieldErrors
        isValid = false
      }
    })
    
    // 更新错误信息
    Object.keys(formErrors).forEach(key => {
      delete formErrors[key]
    })
    Object.assign(formErrors, errors)
    
    // 滚动到第一个错误
    if (!isValid && props.scrollToError) {
      scrollToFirstError()
    }
    
    emit('validate', isValid, errors)
    resolve(isValid)
  })
}

// 验证单个字段
const validateField = (prop: string, value?: any): string[] => {
  const errors: string[] = []
  const rules = props.rules[prop]
  
  if (!rules || !Array.isArray(rules)) {
    return errors
  }
  
  const fieldValue = value !== undefined ? value : formData.value[prop]
  
  rules.forEach((rule: FormItemRule) => {
    const error = validateRule(rule, fieldValue, formData.value)
    if (error) {
      errors.push(error)
    }
  })
  
  // 更新字段错误
  if (errors.length > 0) {
    formErrors[prop] = errors
  } else {
    delete formErrors[prop]
  }
  
  return errors
}

// 验证单个规则
const validateRule = (
  rule: FormItemRule,
  value: any,
  formData: Record<string, any>
): string | null => {
  const { required, message, pattern, min, max, len, validator } = rule
  
  // 必填验证
  if (required && (value === undefined || value === null || value === '')) {
    return message || '该字段为必填项'
  }
  
  // 如果值为空且不是必填，跳过其他验证
  if (value === undefined || value === null || value === '') {
    return null
  }
  
  // 正则验证
  if (pattern && !pattern.test(String(value))) {
    return message || '格式不正确'
  }
  
  // 长度验证
  if (len !== undefined && String(value).length !== len) {
    return message || `长度必须为${len}`
  }
  
  if (min !== undefined && String(value).length < min) {
    return message || `长度不能少于${min}`
  }
  
  if (max !== undefined && String(value).length > max) {
    return message || `长度不能超过${max}`
  }
  
  // 自定义验证
  if (validator && typeof validator === 'function') {
    const result = validator(rule, value, formData)
    if (result === false || (typeof result === 'string' && result)) {
      return typeof result === 'string' ? result : (message || '验证失败')
    }
  }
  
  return null
}

// 重置表单
const resetFields = () => {
  // 重置表单数据
  Object.keys(formData.value).forEach(key => {
    formData.value[key] = undefined
  })
  
  // 清除验证错误
  Object.keys(formErrors).forEach(key => {
    delete formErrors[key]
  })
  
  // 重置字段状态
  Object.values(formFields).forEach((field: any) => {
    if (field.resetField) {
      field.resetField()
    }
  })
}

// 清除验证
const clearValidate = (props?: string | string[]) => {
  const fields = Array.isArray(props) ? props : (props ? [props] : Object.keys(formErrors))
  
  fields.forEach(field => {
    delete formErrors[field]
  })
}

// 获取字段值
const getFieldValue = (prop: string) => {
  return formData.value[prop]
}

// 设置字段值
const setFieldValue = (prop: string, value: any) => {
  formData.value[prop] = value
  emit('update:modelValue', { ...formData.value })
}

// 获取所有字段值
const getFieldsValue = () => {
  return { ...formData.value }
}

// 设置所有字段值
const setFieldsValue = (values: Record<string, any>) => {
  Object.assign(formData.value, values)
  emit('update:modelValue', { ...formData.value })
}

// 滚动到第一个错误
const scrollToFirstError = () => {
  const firstErrorField = document.querySelector('.quant-form-item--error')
  if (firstErrorField) {
    firstErrorField.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
}

// 处理提交
const handleSubmit = async () => {
  const isValid = await validate()
  emit('submit', isValid, { ...formErrors })
}

// 处理取消
const handleCancel = () => {
  emit('cancel')
}

// 监听modelValue变化
watch(() => props.modelValue, (newValue) => {
  if (newValue !== formData.value) {
    Object.assign(formData.value, newValue)
  }
}, { deep: true })

// 监听表单数据变化
watch(formData, (newValue) => {
  emit('update:modelValue', { ...newValue })
}, { deep: true })

// 暴露表单实例
defineExpose(formInstance)
</script>

<style lang="scss" scoped>
.quant-form {
  width: 100%;
  
  // 标签位置
  &--label-left {
    .quant-form-item {
      .quant-form-item__label {
        text-align: left;
      }
    }
  }
  
  &--label-right {
    .quant-form-item {
      .quant-form-item__label {
        text-align: right;
      }
    }
  }
  
  &--label-top {
    .quant-form-item {
      flex-direction: column;
      align-items: flex-start;
      
      .quant-form-item__label {
        text-align: left;
        margin-bottom: var(--spacing-1);
      }
    }
  }
  
  // 尺寸
  &--small {
    .quant-form-item {
      margin-bottom: var(--spacing-2);
    }
  }
  
  &--medium {
    .quant-form-item {
      margin-bottom: var(--spacing-3);
    }
  }
  
  &--large {
    .quant-form-item {
      margin-bottom: var(--spacing-4);
    }
  }
  
  // 状态
  &--disabled {
    pointer-events: none;
    opacity: 0.6;
  }
  
  &--readonly {
    .quant-form-item__content {
      pointer-events: none;
    }
  }
  
  // 操作按钮
  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-2);
    margin-top: var(--spacing-4);
    padding-top: var(--spacing-4);
    border-top: 1px solid var(--border-color)-base;
  }
}
</style>