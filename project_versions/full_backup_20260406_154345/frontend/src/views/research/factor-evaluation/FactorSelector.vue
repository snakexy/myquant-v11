<template>
  <div class="factor-selector">
    <div class="selector-header">
      <label class="selector-label">{{ label }}</label>
      <el-tag v-if="selectedCount > 0" type="info" size="small">
        {{ selectedCountText }}: {{ selectedCount }}
      </el-tag>
    </div>

    <el-select
      :model-value="modelValue"
      @update:model-value="handleUpdate"
      :placeholder="placeholder"
      :multiple="multiple"
      :filterable="filterable"
      style="width: 100%;"
    >
      <el-option
        v-for="factor in factors"
        :key="factor.value"
        :label="factor.label"
        :value="factor.value"
      />
    </el-select>

    <!-- 快速选择按钮 -->
    <div v-if="showQuickSelect" class="quick-select">
      <el-button size="small" @click="selectAll">{{ selectAllText }}</el-button>
      <el-button size="small" @click="clearAll">{{ clearAllText }}</el-button>
    </div>

    <!-- 已选因子标签 -->
    <div v-if="showTags && selectedCount > 0" class="selected-tags">
      <el-tag
        v-for="factor in selectedFactors"
        :key="factor"
        closable
        @close="removeFactor(factor)"
        size="small"
      >
        {{ factor }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface FactorOption {
  label: string
  value: string
}

interface Props {
  modelValue: string | string[]
  factors: FactorOption[]
  multiple?: boolean
  filterable?: boolean
  showQuickSelect?: boolean
  showTags?: boolean
  isZh?: boolean
  label?: string
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  multiple: true,
  filterable: true,
  showQuickSelect: true,
  showTags: true,
  isZh: true,
  label: '',
  placeholder: ''
})

const emit = defineEmits<{
  'update:modelValue': [value: string | string[]]
}>()

const selectedCount = computed(() => {
  return Array.isArray(props.modelValue) ? props.modelValue.length : 0
})

const selectedFactors = computed(() => {
  return Array.isArray(props.modelValue) ? props.modelValue : []
})

const label = computed(() => props.label || (props.isZh ? '选择因子' : 'Select Factors'))
const placeholder = computed(() => props.placeholder || (props.isZh ? '请选择因子' : 'Please select factors'))
const selectedCountText = computed(() => props.isZh ? '已选' : 'Selected')
const selectAllText = computed(() => props.isZh ? '全选' : 'Select All')
const clearAllText = computed(() => props.isZh ? '清空' : 'Clear')

const handleUpdate = (value: string | string[]) => {
  emit('update:modelValue', value)
}

const selectAll = () => {
  emit('update:modelValue', props.factors.map(f => f.value))
}

const clearAll = () => {
  emit('update:modelValue', [])
}

const removeFactor = (factor: string) => {
  if (Array.isArray(props.modelValue)) {
    emit('update:modelValue', props.modelValue.filter(f => f !== factor))
  }
}
</script>

<style scoped lang="scss">
.factor-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selector-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.quick-select {
  display: flex;
  gap: 8px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 100px;
  overflow-y: auto;
}
</style>
