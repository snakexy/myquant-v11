<template>
  <div class="index-selection-config">
    <!-- 指数代码输入 -->
    <div class="config-section">
      <h4 class="section-title">指数代码</h4>
      <div class="code-input-group">
        <textarea
          v-model="config.indexCode"
          placeholder="请输入指数代码，用逗号或换行分隔&#10;常用指数：&#10;• 000001.SH - 上证指数&#10;• 399001.SZ - 深证成指&#10;• 000300.SH - 沪深300&#10;• 000905.SH - 中证500&#10;• 399006.SZ - 创业板指"
          class="code-textarea"
          rows="5"
          @input="onCodeInput"
        ></textarea>

        <!-- 常用指数快捷选择 -->
        <div class="quick-select">
          <span class="quick-label">快捷选择：</span>
          <button
            v-for="preset in commonIndexes"
            :key="preset.code"
            class="quick-btn"
            :class="{ selected: isIndexSelected(preset.code) }"
            @click="toggleIndex(preset.code)"
            :title="preset.name"
          >
            {{ preset.label }}
          </button>
        </div>
      </div>

      <!-- 预览选中的指数 -->
      <div v-if="selectedIndexes.length > 0" class="selected-preview">
        <div class="preview-header">
          <span>已选择 {{ selectedIndexes.length }} 个指数</span>
          <button class="clear-btn" @click="clearIndexes">清空</button>
        </div>
        <div class="preview-list">
          <div v-for="idx in selectedIndexes" :key="idx.code" class="preview-item">
            <span class="index-code">{{ idx.code }}</span>
            <span class="index-name">{{ idx.name || '加载中...' }}</span>
            <button class="remove-btn" @click="removeIndex(idx.code)">×</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 时间范围 -->
    <div class="config-section">
      <h4 class="section-title">时间范围</h4>
      <div class="time-presets">
        <button
          v-for="preset in timePresets"
          :key="preset.value"
          class="preset-btn"
          :class="{ active: config.timeRange === preset.value }"
          @click="selectTimeRange(preset)"
        >
          {{ preset.label }}
        </button>
      </div>
      <div class="custom-range">
        <div class="range-inputs">
          <div class="range-input-group">
            <label>开始日期：</label>
            <input
              type="date"
              v-model="config.startDate"
              class="date-input"
              :max="config.endDate || today"
            />
          </div>
          <div class="range-input-group">
            <label>结束日期：</label>
            <input
              type="date"
              v-model="config.endDate"
              class="date-input"
              :min="config.startDate"
              :max="today"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 数据频率 -->
    <div class="config-section">
      <h4 class="section-title">数据频率</h4>
      <div class="frequency-group">
        <label class="radio-option" v-for="freq in dataFrequencies" :key="freq.value">
          <input
            type="radio"
            :value="freq.value"
            v-model="config.frequency"
          />
          <span>{{ freq.label }}</span>
          <small v-if="freq.description">{{ freq.description }}</small>
        </label>
      </div>
    </div>

    <!-- 其他选项 -->
    <div class="config-section">
      <h4 class="section-title">其他选项</h4>
      <div class="other-options">
        <label class="checkbox-option">
          <input type="checkbox" v-model="config.forwardAdjust" />
          <span>前复权</span>
          <small>调整历史价格以反映分红派息</small>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'

// 常用指数预设
const commonIndexes = [
  { code: '000001.SH', label: '上证指数', name: '上证指数' },
  { code: '399001.SZ', label: '深证成指', name: '深证成指' },
  { code: '000300.SH', label: '沪深300', name: '沪深300' },
  { code: '000905.SH', label: '中证500', name: '中证500' },
  { code: '000852.SH', label: '中证1000', name: '中证1000' },
  { code: '399006.SZ', label: '创业板指', name: '创业板指' },
  { code: '399102.SZ', label: '创业板综', name: '创业板综' },
  { code: '000016.SH', label: '上证180', name: '上证180' },
  { code: '000688.SH', label: '上证380', name: '上证380' },
  { code: '399303.SZ', label: '国证1000', name: '国证1000' }
]

// 时间范围预设
const timePresets = [
  { label: '近1周', value: '1W', days: 7 },
  { label: '近1个月', value: '1M', days: 30 },
  { label: '近3个月', value: '3M', days: 90 },
  { label: '近6个月', value: '6M', days: 180 },
  { label: '近1年', value: '1Y', days: 365 },
  { label: '近2年', value: '2Y', days: 730 }
]

// 数据频率选项（指数通常不需要分钟级数据）
const dataFrequencies = [
  { label: '日线', value: 'daily', description: '每日交易数据' },
  { label: '周线', value: 'weekly', description: '每周交易数据' },
  { label: '月线', value: 'monthly', description: '每月交易数据' }
]

interface IndexInfo {
  code: string
  name: string
}

const props = defineProps<{
  modelValue: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void
}>()

const config = reactive({
  ...props.modelValue,
  indexCode: props.modelValue?.indexCode || '',
  startDate: props.modelValue?.startDate || '',
  endDate: props.modelValue?.endDate || '',
  timeRange: props.modelValue?.timeRange || '3M',
  frequency: props.modelValue?.frequency || 'daily',
  forwardAdjust: props.modelValue?.forwardAdjust ?? false
})

// 选中的指数列表
const selectedIndexes = ref<IndexInfo[]>([])

// 解析指数代码
const parseIndexCodes = (codes: string): string[] => {
  if (!codes) return []
  return codes
    .split(/[,，\n]/)
    .map(code => code.trim())
    .filter(code => code)
}

// 检查指数是否已选中
const isIndexSelected = (code: string): boolean => {
  const codes = parseIndexCodes(config.indexCode)
  return codes.includes(code)
}

// 切换指数选择状态
const toggleIndex = (code: string) => {
  const codes = parseIndexCodes(config.indexCode)
  const index = codes.indexOf(code)

  if (index >= 0) {
    // 已选中，移除
    codes.splice(index, 1)
  } else {
    // 未选中，添加
    codes.push(code)
  }

  config.indexCode = codes.join(',')
  updateSelectedIndexes()
}

// 移除指数
const removeIndex = (code: string) => {
  const codes = parseIndexCodes(config.indexCode)
  const index = codes.indexOf(code)
  if (index >= 0) {
    codes.splice(index, 1)
    config.indexCode = codes.join(',')
    updateSelectedIndexes()
  }
}

// 清空所有指数
const clearIndexes = () => {
  config.indexCode = ''
  selectedIndexes.value = []
}

// 更新选中的指数列表（获取名称）
const updateSelectedIndexes = async () => {
  const codes = parseIndexCodes(config.indexCode)

  if (codes.length === 0) {
    selectedIndexes.value = []
    return
  }

  // 从预设列表中获取名称
  const results: IndexInfo[] = []
  for (const code of codes) {
    const preset = commonIndexes.find(idx => idx.code === code)
    results.push({
      code,
      name: preset?.name || code
    })
  }

  selectedIndexes.value = results
}

// 选择时间范围
const selectTimeRange = (preset: { label: string; value: string; days: number }) => {
  config.timeRange = preset.value

  const endDate = new Date()
  const startDate = new Date()
  startDate.setDate(endDate.getDate() - preset.days)

  config.endDate = endDate.toISOString().split('T')[0]
  config.startDate = startDate.toISOString().split('T')[0]
}

// 今天日期
const today = computed(() => {
  const date = new Date()
  return date.toISOString().split('T')[0]
})

// 代码输入处理
const onCodeInput = () => {
  updateSelectedIndexes()
}

// 监听配置变化
watch(config, () => {
  emit('update:modelValue', { ...config })
}, { deep: true })

// 初始化
onMounted(() => {
  // 设置默认时间范围
  if (!config.startDate || !config.endDate) {
    selectTimeRange(timePresets.find(p => p.value === '3M') || timePresets[2])
  }

  // 如果没有预选指数，默认只选中上证指数
  if (!config.indexCode || config.indexCode.trim() === '') {
    config.indexCode = '000001.SH'
  }

  // 解析已有代码
  updateSelectedIndexes()
})
</script>

<style scoped>
.index-selection-config {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.code-input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.code-textarea {
  width: 100%;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  resize: vertical;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #8b5cf6;
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }
}

.quick-select {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.quick-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.quick-btn {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.9);
  }

  &.selected {
    background: rgba(139, 92, 246, 0.2);
    border-color: #8b5cf6;
    color: #8b5cf6;
  }
}

.selected-preview {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 10px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.clear-btn {
  padding: 2px 8px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.5);
    color: #ef4444;
  }
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 150px;
  overflow-y: auto;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  font-size: 12px;
}

.index-code {
  font-family: 'Consolas', 'Monaco', monospace;
  color: #8b5cf6;
  font-weight: 500;
}

.index-name {
  color: rgba(255, 255, 255, 0.7);
  flex: 1;
}

.remove-btn {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  transition: all 0.2s;

  &:hover {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }
}

.time-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preset-btn {
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.9);
  }

  &.active {
    background: #8b5cf6;
    border-color: #8b5cf6;
    color: #fff;
  }
}

.custom-range {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.range-inputs {
  display: flex;
  gap: 12px;
}

.range-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;

  label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
    white-space: nowrap;
  }
}

.date-input {
  flex: 1;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #8b5cf6;
  }

  &::-webkit-calendar-picker-indicator {
    filter: invert(0.5);
    cursor: pointer;
  }
}

.frequency-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }

  small {
    margin-left: auto;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
  }
}

.other-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }

  small {
    margin-left: auto;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
  }
}
</style>
