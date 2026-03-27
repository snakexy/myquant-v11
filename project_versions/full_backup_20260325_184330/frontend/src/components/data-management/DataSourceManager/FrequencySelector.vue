<template>
  <div class="frequency-selection">
    <div class="selection-header">
      <div class="selection-label">选择要转换的数据频率:</div>
      <div class="selection-hint">
        <el-icon><InfoFilled /></el-icon>
        <span>除1分钟外，其他频率可自动合成</span>
      </div>
    </div>

    <div class="frequency-grid">
      <label
        v-for="freq in frequenciesWithStatus"
        :key="freq.value"
        :class="[
          'frequency-option',
          { checked: modelValue.includes(freq.value) },
          { disabled: freq.disabled },
          { 'synthesis-available': freq.canSynthesize }
        ]"
      >
        <input
          type="checkbox"
          :value="freq.value"
          :checked="modelValue.includes(freq.value)"
          :disabled="freq.disabled"
          @change="handleFrequencyChange"
        />
        <div class="freq-content">
          <font-awesome-icon :icon="freq.icon" />
          <div class="freq-text">
            <span class="freq-label">{{ freq.label }}</span>
            <span class="freq-desc" v-if="freq.description">{{ freq.description }}</span>
          </div>
          <div v-if="freq.source === 'derived'" class="derived-badge">
            {{ freq.canSynthesize ? '可合成' : '合成' }}
          </div>
          <div v-if="freq.disabled" class="disabled-badge">
            需1分钟
          </div>
        </div>
        <el-tooltip v-if="freq.disabled" :content="freq.tooltip || '需要1分钟数据支持'" placement="top">
          <el-icon class="info-icon"><WarningFilled /></el-icon>
        </el-tooltip>
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { InfoFilled, WarningFilled } from '@element-plus/icons-vue'
import type { FrequencyType } from '../../shared/types'

interface FrequencyOption {
  value: FrequencyType
  label: string
  icon: string
  description: string
  source?: 'direct' | 'derived'
  disabled?: boolean
  canSynthesize?: boolean
  tooltip?: string
}

interface Props {
  frequencies: FrequencyOption[]
  modelValue: FrequencyType[]
  availableFrequencies?: FrequencyType[]  // 实际可用的频率（从数据源检测到的）
}

const props = withDefaults(defineProps<Props>(), {
  availableFrequencies: () => []
})

const emit = defineEmits<{
  'update:modelValue': [value: FrequencyType[]]
}>()

// 频率合成规则映射
const SYNTHESIS_SOURCES: Record<FrequencyType, FrequencyType[] | null> = {
  '1min': null,  // 1分钟无法合成，需要原始数据
  '5min': null,  // 5分钟是直接数据源，不能合成
  '15min': ['5min'],  // 15分钟从5分钟合成
  '30min': ['5min'],  // 30分钟从5分钟合成
  '60min': ['5min'],  // 60分钟从5分钟合成
  'day': null,  // 日线需要原始数据
  'weekly': ['day'],
  'monthly': ['day']
}

// 计算每个频率的状态
const frequenciesWithStatus = computed(() => {
  return props.frequencies.map(freq => {
    // 1分钟：如果没有实际数据，则禁用
    if (freq.value === '1min') {
      return {
        ...freq,
        disabled: !props.availableFrequencies.includes('1min'),
        canSynthesize: false,
        tooltip: !props.availableFrequencies.includes('1min')
          ? '数据源中未检测到1分钟数据，无法选择'
          : undefined
      }
    }

    // 日线：如果没有实际数据，则禁用
    if (freq.value === 'day') {
      return {
        ...freq,
        disabled: !props.availableFrequencies.includes('day'),
        canSynthesize: false,
        tooltip: !props.availableFrequencies.includes('day')
          ? '数据源中未检测到日线数据，无法选择'
          : undefined
      }
    }

    // 5分钟：直接数据源，如果没有数据则禁用
    if (freq.value === '5min') {
      return {
        ...freq,
        disabled: !props.availableFrequencies.includes('5min'),
        canSynthesize: false,
        tooltip: !props.availableFrequencies.includes('5min')
          ? '数据源中未检测到5分钟数据，无法选择'
          : undefined
      }
    }

    // 其他频率（15分钟、30分钟、60分钟）：检查是否可以直接使用或合成
    const hasData = props.availableFrequencies.includes(freq.value)
    if (hasData) {
      // 如果数据源中已有该频率的数据，直接可用
      return {
        ...freq,
        disabled: false,
        canSynthesize: false,
        tooltip: '数据源中已检测到该频率数据'
      }
    }

    // 没有直接数据，检查是否可以合成
    const sources = SYNTHESIS_SOURCES[freq.value]
    const canSynthesize = sources !== null

    // 生成tooltip
    let tooltip: string | undefined
    if (canSynthesize && sources) {
      const sourceLabels = sources.map(s => ({
        '1min': '1分钟',
        '5min': '5分钟',
        '15min': '15分钟',
        '30min': '30分钟',
        'day': '日线'
      }[s] || s))
      tooltip = `可从${sourceLabels.join('、')}合成`
    }

    return {
      ...freq,
      disabled: false,  // 可合成的频率不禁用
      canSynthesize,
      tooltip
    }
  })
})

// 处理频率变化
const handleFrequencyChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value as FrequencyType
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
.frequency-selection {
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

.frequency-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.frequency-option {
  cursor: pointer;
  position: relative;
}

.frequency-option.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.frequency-option input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.frequency-option .freq-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s;
}

.frequency-option:not(.disabled):hover .freq-content {
  background: rgba(255, 255, 255, 0.08);
}

.frequency-option.checked .freq-content {
  border-color: #2962ff;
  background: rgba(102, 126, 234, 0.1);
}

.frequency-option.synthesis-available .freq-content {
  border-color: rgba(245, 158, 11, 0.3);
  background: rgba(245, 158, 11, 0.03);
}

.frequency-option.synthesis-available.checked .freq-content {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.15);
}

.frequency-option.disabled .freq-content {
  border-color: rgba(239, 68, 68, 0.2);
  background: rgba(239, 68, 68, 0.05);
}

.freq-content svg {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.7);
}

.frequency-option.checked .freq-content svg {
  color: #2962ff;
}

.frequency-option.synthesis-available .freq-content svg {
  color: rgba(245, 158, 11, 0.8);
}

.frequency-option.disabled .freq-content svg {
  color: rgba(239, 68, 68, 0.6);
}

.freq-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.freq-label {
  font-size: 14px;
  font-weight: 500;
  color: white;
}

.freq-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.derived-badge {
  margin-left: auto;
  padding: 3px 10px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  font-size: 10px;
  font-weight: 600;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.disabled-badge {
  margin-left: auto;
  padding: 3px 10px;
  background: rgba(239, 68, 68, 0.2);
  color: rgba(239, 68, 68, 0.9);
  font-size: 10px;
  font-weight: 600;
  border-radius: 4px;
  border: 1px solid rgba(239, 68, 68, 0.3);
  white-space: nowrap;
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

/* 合成规则说明 */
.synthesis-rules {
  margin-top: 16px;
  padding: 16px;
  background: rgba(245, 158, 11, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.15);
}

.rules-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 12px;
}

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rule-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
}

/* 响应式 */
@media (max-width: 768px) {
  .frequency-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .selection-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
