<template>
  <div class="security-type-selection">
    <div class="selection-header">
      <div class="selection-label">选择要转换的证券类型:</div>
      <div class="selection-hint">
        <el-icon><InfoFilled /></el-icon>
        <span>可选择多种证券类型进行转换</span>
      </div>
    </div>

    <div class="security-type-grid">
      <label
        v-for="type in securityTypes"
        :key="type.value"
        :class="[
          'security-type-option',
          { checked: modelValue.includes(type.value) },
          { disabled: type.disabled }
        ]"
      >
        <input
          type="checkbox"
          :value="type.value"
          :checked="modelValue.includes(type.value)"
          :disabled="type.disabled"
          @change="handleTypeChange"
        />
        <div class="type-content">
          <font-awesome-icon :icon="type.icon" />
          <div class="type-text">
            <span class="type-label">{{ type.label }}</span>
            <span class="type-count" v-if="type.count !== undefined">
              {{ type.count }} 只
            </span>
            <span class="available-freq" v-if="getAvailableFrequencies(type.value)">
              {{ getAvailableFrequencies(type.value) }}
            </span>
          </div>
          <div v-if="modelValue.includes(type.value)" class="checked-badge">
            <font-awesome-icon icon="check" />
          </div>
        </div>
        <el-tooltip v-if="type.disabled" :content="type.tooltip || '该类型暂无数据'" placement="top">
          <el-icon class="info-icon"><WarningFilled /></el-icon>
        </el-tooltip>
      </label>
    </div>

    <!-- 证券类型-频率矩阵 -->
    <div class="frequency-matrix" v-if="modelValue.length > 0">
      <div class="matrix-title">📊 可用数据频率矩阵</div>
      <div class="matrix-table">
        <div class="matrix-header">
          <div class="matrix-cell">证券类型</div>
          <div class="matrix-cell" v-for="freq in allFrequencies" :key="freq.value">
            {{ freq.label }}
          </div>
        </div>
        <div
          class="matrix-row"
          v-for="typeValue in modelValue"
          :key="typeValue"
        >
          <div class="matrix-cell type-name">
            <font-awesome-icon :icon="getSecurityTypeIcon(typeValue)" />
            {{ getSecurityTypeLabel(typeValue) }}
          </div>
          <div
            class="matrix-cell"
            v-for="freq in allFrequencies"
            :key="`${typeValue}-${freq.value}`"
            :class="{
              'available': isFrequencyAvailable(typeValue, freq.value),
              'not-available': !isFrequencyAvailable(typeValue, freq.value)
            }"
          >
            <font-awesome-icon
              :icon="isFrequencyAvailable(typeValue, freq.value) ? 'check-circle' : 'times-circle'"
            />
          </div>
        </div>
      </div>
      <div class="matrix-legend">
        <span class="legend-item">
          <font-awesome-icon icon="check-circle" />
          可用
        </span>
        <span class="legend-item">
          <font-awesome-icon icon="times-circle" />
          不可用
        </span>
      </div>
    </div>

    <!-- 已选择的证券类型汇总 -->
    <div v-if="modelValue.length > 0" class="selection-summary">
      <div class="summary-title">已选择 {{ modelValue.length }} 种证券类型</div>
      <div class="summary-list">
        <div v-for="selectedValue in modelValue" :key="selectedValue" class="summary-item">
          <font-awesome-icon :icon="getSecurityTypeIcon(selectedValue)" />
          <span>{{ getSecurityTypeLabel(selectedValue) }}</span>
          <span class="summary-count">({{ getSecurityTypeCount(selectedValue) }} 只)</span>
        </div>
      </div>
      <div class="summary-total">
        共计 <span class="total-highlight">{{ totalSelectedCount }}</span> 只标的
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { InfoFilled, WarningFilled } from '@element-plus/icons-vue'

export type SecurityTypeValue = 'stock' | 'fund' | 'index' | 'other'

interface SecurityTypeOption {
  value: SecurityTypeValue
  label: string
  icon: string
  count?: number
  disabled?: boolean
  tooltip?: string
}

interface FrequencyOption {
  value: string
  label: string
}

interface Props {
  securityTypes: SecurityTypeOption[]
  modelValue: SecurityTypeValue[]
  availableFrequencies?: FrequencyOption[]
}

const props = withDefaults(defineProps<Props>(), {
  availableFrequencies: () => [
    { value: '1min', label: '1分钟' },
    { value: '5min', label: '5分钟' },
    { value: '15min', label: '15分钟' },
    { value: '30min', label: '30分钟' },
    { value: '60min', label: '60分钟' },
    { value: 'day', label: '日线' }
  ]
})

const emit = defineEmits<{
  'update:modelValue': [value: SecurityTypeValue[]]
}>()

// 所有频率选项
const allFrequencies = computed(() => props.availableFrequencies)

// 证券类型与可用频率的映射（基于实际情况）
const SECURITY_TYPE_FREQUENCY_MAP: Record<SecurityTypeValue, string[]> = {
  'stock': ['day', '5min', '15min', '30min', '60min'],  // 股票：日线 + 分钟线都可用
  'fund': ['day'],  // 基金：通常只有日线数据
  'index': ['day', '5min'],  // 指数：日线和5分钟
  'other': ['day']  // 债券、回购：通常只有日线数据
}

// 检查某个频率对某类证券是否可用
const isFrequencyAvailable = (typeValue: SecurityTypeValue, freqValue: string): boolean => {
  return SECURITY_TYPE_FREQUENCY_MAP[typeValue]?.includes(freqValue) || false
}

// 获取证券类型的可用频率描述
const getAvailableFrequencies = (typeValue: SecurityTypeValue): string => {
  const freqs = SECURITY_TYPE_FREQUENCY_MAP[typeValue] || []
  const freqLabels = freqs.map(f => {
    const freq = props.availableFrequencies.find(af => af.value === f)
    return freq?.label || f
  })
  if (freqLabels.length === props.availableFrequencies.length) {
    return '全部频率'
  }
  return `可用: ${freqLabels.join(', ')}`
}

// 计算已选择的证券总数
const totalSelectedCount = computed(() => {
  return props.modelValue.reduce((total, typeValue) => {
    const type = props.securityTypes.find(t => t.value === typeValue)
    return total + (type?.count || 0)
  }, 0)
})

// 获取证券类型图标
const getSecurityTypeIcon = (typeValue: SecurityTypeValue): string => {
  const type = props.securityTypes.find(t => t.value === typeValue)
  return type?.icon || 'folder'
}

// 获取证券类型标签
const getSecurityTypeLabel = (typeValue: SecurityTypeValue): string => {
  const type = props.securityTypes.find(t => t.value === typeValue)
  return type?.label || typeValue
}

// 获取证券类型数量
const getSecurityTypeCount = (typeValue: SecurityTypeValue): number => {
  const type = props.securityTypes.find(t => t.value === typeValue)
  return type?.count || 0
}

// 处理证券类型变化
const handleTypeChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value as SecurityTypeValue
  const checked = target.checked

  let newValues = [...props.modelValue]

  if (checked) {
    if (!newValues.includes(value)) {
      newValues.push(value)
    }
  } else {
    newValues = newValues.filter(v => v !== value)
  }

  emit('update:modelValue', newValues)
}
</script>

<style scoped>
.security-type-selection {
  margin-bottom: 16px;
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.selection-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.selection-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(16, 185, 129, 0.8);
  background: rgba(16, 185, 129, 0.1);
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.selection-hint .el-icon {
  font-size: 14px;
}

.security-type-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.security-type-option {
  cursor: pointer;
  position: relative;
}

.security-type-option.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.security-type-option input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.security-type-option .type-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s;
  min-height: 60px;
}

.security-type-option:not(.disabled):hover .type-content {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
}

.security-type-option.checked .type-content {
  border-color: #2962ff;
  background: rgba(102, 126, 234, 0.1);
}

.security-type-option.disabled .type-content {
  border-color: rgba(239, 68, 68, 0.2);
  background: rgba(239, 68, 68, 0.05);
}

.type-content svg {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.7);
}

.security-type-option.checked .type-content svg {
  color: #2962ff;
}

.security-type-option.disabled .type-content svg {
  color: rgba(239, 68, 68, 0.6);
}

.type-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.type-label {
  font-size: 14px;
  font-weight: 500;
  color: white;
}

.type-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.available-freq {
  font-size: 10px;
  color: rgba(16, 185, 129, 0.8);
  margin-top: 2px;
}

.checked-badge {
  margin-left: auto;
  padding: 4px 8px;
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  color: white;
  font-size: 12px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-icon {
  position: absolute;
  top: 6px;
  right: 6px;
  font-size: 14px;
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
  padding: 2px;
  border-radius: 4px;
}

/* 已选择汇总 */
.selection-summary {
  margin-top: 16px;
  padding: 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.15);
}

.summary-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 12px;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
}

.summary-item svg {
  color: #2962ff;
}

.summary-count {
  margin-left: auto;
  color: rgba(255, 255, 255, 0.5);
}

.summary-total {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.total-highlight {
  font-size: 16px;
  font-weight: 600;
  color: #2962ff;
}

/* 频率矩阵 */
.frequency-matrix {
  margin-top: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.matrix-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 12px;
}

.matrix-table {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-x: auto;
}

.matrix-header {
  display: flex;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.matrix-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.matrix-cell {
  flex-shrink: 0;
  width: 80px;
  padding: 8px;
  text-align: center;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.matrix-cell.type-name {
  width: 100px;
  font-weight: 500;
  justify-content: flex-start;
  padding-left: 12px;
  background: rgba(102, 126, 234, 0.1);
}

.matrix-cell.available {
  color: rgba(16, 185, 129, 0.9);
  background: rgba(16, 185, 129, 0.1);
}

.matrix-cell.not-available {
  color: rgba(239, 68, 68, 0.6);
  background: rgba(239, 68, 68, 0.05);
}

.matrix-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 11px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.6);
}

.legend-item svg {
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 768px) {
  .security-type-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .selection-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
