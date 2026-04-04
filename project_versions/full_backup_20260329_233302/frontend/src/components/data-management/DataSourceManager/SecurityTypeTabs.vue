<template>
  <div class="security-type-tabs">
    <el-tabs v-model="activeTab" type="border-card" class="security-tabs">
      <el-tab-pane
        v-for="type in securityTypes"
        :key="type.value"
        :name="type.value"
      >
        <template #label>
          <div class="tab-label" @click.stop>
            <el-checkbox
              :model-value="isTypeEnabled(type.value)"
              @update:model-value="handleTypeToggle(type.value, $event)"
              @click.stop
            />
            <font-awesome-icon :icon="type.icon" />
            <span class="label-text">{{ type.label }}</span>
            <span class="label-count">{{ type.count }} 只</span>
          </div>
        </template>

        <div class="tab-content">
          <!-- 该类型的频率选择 - 复用 FrequencySelector 的样式 -->
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
                v-for="freq in frequenciesWithStatus(type.value)"
                :key="freq.value"
                :class="[
                  'frequency-option',
                  { checked: isFrequencySelected(type.value, freq.value) },
                  { disabled: freq.disabled },
                  { 'synthesis-available': freq.canSynthesize }
                ]"
              >
                <input
                  type="checkbox"
                  :value="freq.value"
                  :checked="isFrequencySelected(type.value, freq.value)"
                  :disabled="freq.disabled"
                  @change="handleFrequencyChange(type.value, freq.value, $event)"
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
              </label>
            </div>

            <!-- 合成规则说明 -->
            <div v-if="selectedFrequenciesForType(type.value).length > 0" class="synthesis-rules">
              <div class="rules-title">📊 自动合成规则</div>
              <div class="rules-list">
                <div v-for="rule in synthesisRulesForType(type.value)" :key="rule.target" class="rule-item">
                  <span class="rule-source">{{ rule.source }}</span>
                  <font-awesome-icon icon="arrow-right" class="rule-arrow" />
                  <span class="rule-target">{{ rule.target }}</span>
                </div>
              </div>
            </div>

            <!-- 已选频率汇总 -->
            <div v-if="selectedFrequenciesForType(type.value).length > 0" class="selected-summary">
              <div class="summary-text">
                已选择 <strong>{{ selectedFrequenciesForType(type.value).length }}</strong> 种频率
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 全局汇总 -->
    <div class="global-summary">
      <div class="summary-title">📊 转换计划汇总</div>
      <div class="summary-list">
        <div
          v-for="type in enabledTypes"
          :key="type.value"
          class="summary-item"
        >
          <font-awesome-icon :icon="type.icon" />
          <span class="item-name">{{ type.label }}</span>
          <span class="item-count">({{ type.count }} 只)</span>
          <span class="item-freqs">{{ getSelectedFrequencies(type.value).join(', ') || '未选择频率' }}</span>
        </div>
      </div>
      <div v-if="enabledTypes.length === 0" class="empty-hint">
        请至少勾选一种证券类型并选择对应频率
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'
import type { SecurityTypeValue } from './SecurityTypeSelector.vue'

export type SecurityTypeValue = 'stock' | 'fund' | 'index' | 'other'

interface SecurityTypeOption {
  value: SecurityTypeValue
  label: string
  icon: string
  count: number
}

interface FrequencyOption {
  value: string
  label: string
  icon: string
  description: string
  source?: 'direct' | 'derived'
  disabled?: boolean
  canSynthesize?: boolean
}

interface TypeFrequencyConfig {
  type: SecurityTypeValue
  enabled: boolean
  frequencies: string[]
}

interface Props {
  securityTypes: SecurityTypeOption[]
  modelValue: TypeFrequencyConfig[]
}

const props = withDefaults(defineProps<Props>(), {})

const emit = defineEmits<{
  'update:modelValue': [value: TypeFrequencyConfig[]]
}>()

const activeTab = ref<SecurityTypeValue>('stock')

// 所有可用频率选项（参考 FrequencySelector）
const ALL_FREQUENCIES: FrequencyOption[] = [
  { value: '1min', label: '1分钟', icon: 'clock', description: '1分钟K线', source: 'direct' as const },
  { value: '5min', label: '5分钟', icon: 'clock', description: '5分钟K线', source: 'direct' as const },
  { value: '15min', label: '15分钟', icon: 'clock', description: '15分钟K线', source: 'derived' as const },
  { value: '30min', label: '30分钟', icon: 'clock', description: '30分钟K线', source: 'derived' as const },
  { value: '60min', label: '60分钟', icon: 'clock', description: '60分钟K线', source: 'derived' as const },
  { value: 'day', label: '日线', icon: 'calendar-day', description: '每日K线', source: 'direct' as const },
  { value: 'weekly', label: '周线', icon: 'calendar-week', description: '每周K线', source: 'derived' as const },
  { value: 'monthly', label: '月线', icon: 'calendar', description: '每月K线', source: 'derived' as const }
]

// 证券类型与可用频率的映射
const SECURITY_TYPE_FREQUENCY_MAP: Record<SecurityTypeValue, string[]> = {
  'stock': ['day', 'weekly', 'monthly', '5min', '15min', '30min', '60min'],
  'fund': ['day', 'weekly', 'monthly'],
  'index': ['day', 'weekly', 'monthly', '5min', '15min', '30min', '60min'],
  'other': ['day', 'weekly', 'monthly']
}

// 默认频率配置
const DEFAULT_FREQUENCIES: Record<SecurityTypeValue, string[]> = {
  'stock': ['day', '60min'],
  'fund': ['day'],
  'index': ['day', '60min'],
  'other': ['day']
}

// 频率合成规则映射
const SYNTHESIS_SOURCES: Record<string, string[] | null> = {
  '1min': null,
  '5min': ['1min'],
  '15min': ['5min', '1min'],
  '30min': ['5min', '1min'],
  '60min': ['5min', '1min'],
  'day': null,
  'weekly': ['day'],
  'monthly': ['day']
}

// 获取某类型可用的频率选项（带状态）
const frequenciesWithStatus = (typeValue: SecurityTypeValue) => {
  const availableFreqs = SECURITY_TYPE_FREQUENCY_MAP[typeValue] || []

  return ALL_FREQUENCIES.map(freq => {
    const isAvailable = availableFreqs.includes(freq.value)

    // 1分钟：如果没有数据，则禁用
    if (freq.value === '1min') {
      return {
        ...freq,
        disabled: !isAvailable,
        canSynthesize: false
      }
    }

    // 其他频率：检查是否可以合成
    if (!isAvailable) {
      return {
        ...freq,
        disabled: true,
        canSynthesize: false
      }
    }

    // 可用的频率
    return {
      ...freq,
      disabled: false,
      canSynthesize: freq.source === 'derived'
    }
  })
}

// 获取某类型的配置
const getTypeConfig = (typeValue: SecurityTypeValue): TypeFrequencyConfig => {
  const existing = props.modelValue.find(c => c.type === typeValue)
  if (existing) return existing

  return {
    type: typeValue,
    enabled: false,
    frequencies: DEFAULT_FREQUENCIES[typeValue] || []
  }
}

// 检查某类型是否启用
const isTypeEnabled = (typeValue: SecurityTypeValue): boolean => {
  return getTypeConfig(typeValue).enabled
}

// 检查某类型的某频率是否选中
const isFrequencySelected = (typeValue: SecurityTypeValue, freqValue: string): boolean => {
  const config = getTypeConfig(typeValue)
  return config.frequencies.includes(freqValue)
}

// 获取某类型已选的频率
const selectedFrequenciesForType = (typeValue: SecurityTypeValue): string[] => {
  const config = getTypeConfig(typeValue)
  return config.frequencies
}

// 获取合成规则
const synthesisRulesForType = (typeValue: SecurityTypeValue) => {
  const selectedFreqs = selectedFrequenciesForType(typeValue)
  const rules: Array<{ source: string; target: string }> = []

  selectedFreqs.forEach(freq => {
    const sources = SYNTHESIS_SOURCES[freq]
    if (sources && !selectedFreqs.includes(sources[0])) {
      const sourceLabel = {
        '1min': '1分钟',
        '5min': '5分钟',
        'day': '日线'
      }[sources[0]] || sources[0]

      const targetLabel = ALL_FREQUENCIES.find(f => f.value === freq)?.label || freq
      rules.push({ source: sourceLabel, target: targetLabel })
    }
  })

  return rules
}

// 获取某类型已选的频率列表（显示用）
const getSelectedFrequencies = (typeValue: SecurityTypeValue): string[] => {
  const config = getTypeConfig(typeValue)
  return config.frequencies.map(f => {
    const freq = ALL_FREQUENCIES.find(af => af.value === f)
    return freq?.label || f
  })
}

// 处理类型启用/禁用切换
const handleTypeToggle = (typeValue: SecurityTypeValue, enabled: boolean) => {
  const newConfigs = [...props.modelValue]
  const existingIndex = newConfigs.findIndex(c => c.type === typeValue)

  if (existingIndex >= 0) {
    newConfigs[existingIndex] = { ...newConfigs[existingIndex], enabled }
  } else {
    newConfigs.push({
      type: typeValue,
      enabled,
      frequencies: DEFAULT_FREQUENCIES[typeValue] || []
    })
  }

  emit('update:modelValue', newConfigs)
}

// 处理频率选择变化
const handleFrequencyChange = (typeValue: SecurityTypeValue, freqValue: string, event: Event) => {
  const target = event.target as HTMLInputElement
  const checked = target.checked

  const config = getTypeConfig(typeValue)
  let newFrequencies = [...config.frequencies]

  if (checked) {
    if (!newFrequencies.includes(freqValue)) {
      newFrequencies.push(freqValue)
    }
  } else {
    newFrequencies = newFrequencies.filter(f => f !== freqValue)
  }

  const newConfigs = [...props.modelValue]
  const existingIndex = newConfigs.findIndex(c => c.type === typeValue)

  if (existingIndex >= 0) {
    newConfigs[existingIndex] = { ...config, frequencies: newFrequencies, enabled: true }
  } else {
    newConfigs.push({
      type: typeValue,
      enabled: true,
      frequencies: newFrequencies
    })
  }

  emit('update:modelValue', newConfigs)
}

// 已启用的类型列表
const enabledTypes = computed(() => {
  return props.securityTypes.filter(type => {
    const config = props.modelValue.find(c => c.type === type.value)
    return config?.enabled || false
  })
})
</script>

<style scoped>
.security-type-tabs {
  margin-bottom: 16px;
}

.security-tabs {
  background: rgba(26, 26, 46, 0.95);
}

:deep(.el-tabs--border-card) {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-tabs__header) {
  background: rgba(255, 255, 255, 0.03);
  margin: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-tabs__nav) {
  border: none;
}

:deep(.el-tabs__item) {
  background: transparent;
  border: none;
  padding: 0 8px;
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
}

:deep(.el-tabs__item.is-active) {
  color: #2962ff;
  background: transparent;
}

:deep(.el-tabs__item:hover) {
  color: #2962ff;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-label:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
}

:deep(.el-tabs__item.is-active .tab-label) {
  background: rgba(102, 126, 234, 0.15);
  border-color: #2962ff;
}

.tab-label svg {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
}

:deep(.el-tabs__item.is-active .tab-label svg) {
  color: #2962ff;
}

.label-text {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
}

.label-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
}

.tab-content {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
}

/* 频率选择样式 - 完全复制 FrequencySelector */
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

.rule-source {
  color: rgba(16, 185, 129, 0.9);
  font-weight: 500;
}

.rule-arrow {
  color: rgba(255, 255, 255, 0.4);
  font-size: 10px;
}

.rule-target {
  color: rgba(245, 158, 11, 0.9);
  font-weight: 600;
}

/* 已选汇总 */
.selected-summary {
  margin-top: 12px;
  padding: 12px 16px;
  background: rgba(16, 185, 129, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(16, 185, 129, 0.15);
}

.summary-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.summary-text strong {
  color: #10b981;
  font-weight: 600;
}

/* 全局汇总 */
.global-summary {
  margin-top: 20px;
  padding: 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.15);
}

.summary-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 12px;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  font-size: 12px;
}

.summary-item svg {
  color: #2962ff;
  font-size: 14px;
}

.item-name {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
}

.item-count {
  margin-left: 8px;
  color: rgba(255, 255, 255, 0.5);
}

.item-freqs {
  margin-left: auto;
  color: rgba(16, 185, 129, 0.9);
  font-weight: 500;
}

.empty-hint {
  text-align: center;
  padding: 20px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

/* 响应式 */
@media (max-width: 768px) {
  .frequency-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .tab-label {
    padding: 6px 12px;
  }

  .label-text {
    font-size: 12px;
  }
}
</style>
