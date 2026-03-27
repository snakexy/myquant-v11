<template>
  <div class="node-config-panel">
    <!-- 数据获取配置 -->
    <div class="config-section">
      <h3 class="section-title">
        <n-icon :component="TrendingUpOutline" />
        数据获取
      </h3>

      <!-- 时间范围选择 -->
      <div class="config-group">
        <label class="config-label">时间范围</label>
        <div class="time-presets">
          <button
            v-for="preset in timePresets"
            :key="preset.value"
            class="preset-btn"
            :class="{ active: selectedTimeRange === preset.value }"
            @click="selectTimeRange(preset.value)"
          >
            {{ preset.label }}
          </button>
        </div>

        <!-- 自定义日期范围 -->
        <div class="custom-range">
          <div class="date-inputs">
            <div class="date-input-group">
              <label>开始日期</label>
              <input
                v-model="customStartDate"
                type="date"
                class="quant-input"
                :max="today"
              />
            </div>
            <div class="date-input-group">
              <label>结束日期</label>
              <input
                v-model="customEndDate"
                type="date"
                class="quant-input"
                :max="today"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 数据选项 -->
      <div class="config-group">
        <label class="config-label">数据选项</label>
        <div class="checkbox-group">
          <label class="checkbox-item">
            <input type="checkbox" v-model="config.includeVolume" />
            <span>包含成交量</span>
          </label>
          <label class="checkbox-item">
            <input type="checkbox" v-model="config.adjustPrices" />
            <span>复权价格</span>
          </label>
          <label class="checkbox-item">
            <input type="checkbox" v-model="config.includeDividends" />
            <span>包含分红</span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { NIcon } from 'naive-ui'
import { TrendingUpOutline } from '@vicons/ionicons5'

interface Config {
  timeRange: string
  startDate?: string
  endDate?: string
  includeVolume: boolean
  adjustPrices: boolean
  includeDividends: boolean
}

interface Props {
  modelValue?: Config
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => ({
    timeRange: '1Y',
    includeVolume: true,
    adjustPrices: true,
    includeDividends: false
  })
})

const emit = defineEmits<{
  'update:modelValue': [config: Config]
}>()

// 时间预设
const timePresets = [
  { label: '近1周', value: '1W', days: 7 },
  { label: '近1月', value: '1M', days: 30 },
  { label: '近3月', value: '3M', days: 90 },
  { label: '近6月', value: '6M', days: 180 },
  { label: '近1年', value: '1Y', days: 365 },
  { label: '近2年', value: '2Y', days: 730 },
]

// 响应式数据
const config = ref<Config>({ ...props.modelValue })
const selectedTimeRange = ref(props.modelValue.timeRange)
const customStartDate = ref('')
const customEndDate = ref('')
const today = new Date().toISOString().split('T')[0]

// 选择时间范围
const selectTimeRange = (range: string) => {
  selectedTimeRange.value = range
  config.value.timeRange = range

  // 自动计算日期
  const preset = timePresets.find(p => p.value === range)
  if (preset) {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(endDate.getDate() - preset.days)

    customEndDate.value = endDate.toISOString().split('T')[0]
    customStartDate.value = startDate.toISOString().split('T')[0]

    config.value.endDate = customEndDate.value
    config.value.startDate = customStartDate.value
  }
}

// 监听配置变化
watch(config, (newConfig) => {
  emit('update:modelValue', newConfig)
}, { deep: true })

// 初始化
if (config.value.timeRange) {
  selectTimeRange(config.value.timeRange)
}
</script>

<style lang="scss" scoped>
.node-config-panel {
  padding: var(--spacing-4);
}

.config-section {
  margin-bottom: var(--spacing-6);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-4);
  padding-bottom: var(--spacing-2);
  border-bottom: 1px solid var(--border-color-base);
}

.config-group {
  margin-bottom: var(--spacing-4);

  &:last-child {
    margin-bottom: 0;
  }
}

.config-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: var(--spacing-2);
}

// 时间预设按钮
.time-presets {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-3);
}

.preset-btn {
  padding: var(--spacing-1) var(--spacing-3);
  background: var(--bg-color-base);
  border: 1px solid var(--border-color-base);
  border-radius: var(--border-radius-base);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--bg-color-tertiary);
    color: var(--text-primary);
  }

  &.active {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
  }
}

// 自定义日期范围
.custom-range {
  padding: var(--spacing-3);
  background: var(--bg-color-base);
  border-radius: var(--border-radius-base);
}

.date-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-3);
}

.date-input-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);

  label {
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
  }
}

// 复选框组
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  cursor: pointer;

  input[type="checkbox"] {
    width: 16px;
    height: 16px;
  }

  span {
    font-size: var(--font-size-sm);
    color: var(--text-primary);
  }
}
</style>