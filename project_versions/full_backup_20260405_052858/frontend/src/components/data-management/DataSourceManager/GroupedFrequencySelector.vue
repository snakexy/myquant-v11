<template>
  <div class="grouped-frequency-selection">
    <el-tabs v-model="activeTab" class="group-tabs">
      <!-- 股票 -->
      <el-tab-pane label="股票" name="stock">
        <template #label>
          <div class="tab-label">
            <el-checkbox
              :model-value="isGroupEnabled('stock')"
              @change="toggleGroup('stock', $event)"
              @click.native.stop
              class="tab-checkbox"
            />
            <font-awesome-icon icon="chart-line" />
            <span>股票</span>
            <span class="tab-count">{{ formatNumber(tdxInfo?.stockCounts?.day || 0) }}</span>
            <el-badge
              :value="getSelectedCount('stock')"
              :hidden="getSelectedCount('stock') === 0"
              class="tab-badge"
            />
          </div>
        </template>
        <FrequencySelector
          :frequencies="frequencies"
          :modelValue="selectedFrequencies.stock"
          :availableFrequencies="availableFrequenciesMap.stock"
          @update:modelValue="(val) => updateFrequencies('stock', val)"
        />
      </el-tab-pane>

      <!-- 基金 -->
      <el-tab-pane label="基金" name="fund">
        <template #label>
          <div class="tab-label">
            <el-checkbox
              :model-value="isGroupEnabled('fund')"
              @change="toggleGroup('fund', $event)"
              @click.native.stop
              class="tab-checkbox"
            />
            <font-awesome-icon icon="piggy-bank" />
            <span>基金</span>
            <span class="tab-count">{{ formatNumber(tdxInfo?.fundCounts?.day || 0) }}</span>
            <el-badge
              :value="getSelectedCount('fund')"
              :hidden="getSelectedCount('fund') === 0"
              class="tab-badge"
            />
          </div>
        </template>
        <FrequencySelector
          :frequencies="frequencies"
          :modelValue="selectedFrequencies.fund"
          :availableFrequencies="availableFrequenciesMap.fund"
          @update:modelValue="(val) => updateFrequencies('fund', val)"
        />
      </el-tab-pane>

      <!-- 指数 -->
      <el-tab-pane label="指数" name="index">
        <template #label>
          <div class="tab-label">
            <el-checkbox
              :model-value="isGroupEnabled('index')"
              @change="toggleGroup('index', $event)"
              @click.native.stop
              class="tab-checkbox"
            />
            <font-awesome-icon icon="chart-area" />
            <span>指数</span>
            <span class="tab-count">{{ formatNumber(tdxInfo?.indexCounts?.day || 0) }}</span>
            <el-badge
              :value="getSelectedCount('index')"
              :hidden="getSelectedCount('index') === 0"
              class="tab-badge"
            />
          </div>
        </template>
        <FrequencySelector
          :frequencies="frequencies"
          :modelValue="selectedFrequencies.index"
          :availableFrequencies="availableFrequenciesMap.index"
          @update:modelValue="(val) => updateFrequencies('index', val)"
        />
      </el-tab-pane>

      <!-- 债券、回购 -->
      <el-tab-pane label="债券、回购" name="other">
        <template #label>
          <div class="tab-label">
            <el-checkbox
              :model-value="isGroupEnabled('other')"
              @change="toggleGroup('other', $event)"
              @click.native.stop
              class="tab-checkbox"
            />
            <font-awesome-icon icon="money-bill-wave" />
            <span>债券、回购</span>
            <span class="tab-count">{{ formatNumber(tdxInfo?.otherCounts?.day || 0) }}</span>
            <el-badge
              :value="getSelectedCount('other')"
              :hidden="getSelectedCount('other') === 0"
              class="tab-badge"
            />
          </div>
        </template>
        <FrequencySelector
          :frequencies="frequencies"
          :modelValue="selectedFrequencies.other"
          :availableFrequencies="availableFrequenciesMap.other"
          @update:modelValue="(val) => updateFrequencies('other', val)"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'
import FrequencySelector from './FrequencySelector.vue'
import type { FrequencyType, TDXInfo } from '../shared/types'
import { AVAILABLE_FREQUENCIES } from '../shared/constants'

interface Props {
  tdxInfo: TDXInfo | null
  modelValue: Record<string, FrequencyType[]>
  availableFrequencies?: Record<string, FrequencyType[]>
  enabledGroups?: string[]  // 新增：启用的分组列表
}

const props = withDefaults(defineProps<Props>(), {
  availableFrequencies: () => ({
    stock: [],
    fund: [],
    index: [],
    other: []
  }),
  enabledGroups: () => ['stock', 'fund', 'index', 'other']  // 默认全部启用
})

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, FrequencyType[]>]
  'update:enabledGroups': [value: string[]]
  'toggleGroup': [group: string, enabled: boolean]
}>()

// 当前激活的标签页
const activeTab = ref('stock')

// 频率选项 - 类型断言以匹配 FrequencySelector 的期望
const frequencies = AVAILABLE_FREQUENCIES as any

// 可用频率（直接引用 props）
const availableFrequenciesMap = computed(() => props.availableFrequencies)

// 选中的频率
const selectedFrequencies = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// TDX 信息
const tdxInfo = computed(() => props.tdxInfo)

// 更新某个分组的频率
const updateFrequencies = (group: string, frequencies: FrequencyType[]) => {
  emit('update:modelValue', {
    ...selectedFrequencies.value,
    [group]: frequencies
  })
}

// 获取某个分组的选中数量
const getSelectedCount = (group: string): number => {
  return selectedFrequencies.value[group]?.length || 0
}

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

// 判断分组是否启用
const isGroupEnabled = (group: string): boolean => {
  return props.enabledGroups?.includes(group) || false
}

// 切换分组启用状态
const toggleGroup = (group: string, enabled: boolean | Event) => {
  // Element Plus checkbox 会传递事件对象，需要处理
  const isChecked = typeof enabled === 'boolean' ? enabled : (enabled as any).target?.checked !== undefined ? (enabled as any).target.checked : enabled

  const currentGroups = [...(props.enabledGroups || [])]
  if (isChecked) {
    if (!currentGroups.includes(group)) {
      currentGroups.push(group)
    }
  } else {
    const index = currentGroups.indexOf(group)
    if (index > -1) {
      currentGroups.splice(index, 1)
    }
  }
  emit('update:enabledGroups', currentGroups)
  emit('toggleGroup', group, isChecked)
}
</script>

<style scoped>
.grouped-frequency-selection {
  margin-bottom: 16px;
}

/* 标签页样式 */
.group-tabs {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 16px;
}

.group-tabs :deep(.el-tabs__header) {
  margin: 0 0 16px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.group-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.group-tabs :deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  padding: 0 16px;
  height: 40px;
  line-height: 40px;
}

.group-tabs :deep(.el-tabs__item:hover) {
  color: rgba(255, 255, 255, 0.8);
}

.group-tabs :deep(.el-tabs__item.is-active) {
  color: #2962ff;
}

.group-tabs :deep(.el-tabs__active-bar) {
  background: #2962ff;
}

.group-tabs :deep(.el-tabs__content) {
  padding: 0;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  padding-right: 8px;
}

.tab-label .tab-checkbox {
  margin: 0;
  flex-shrink: 0;
}

/* 只在未选中时设置半透明背景 */
.tab-label .tab-checkbox :deep(.el-checkbox__input:not(.is-checked) .el-checkbox__inner) {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.tab-label svg {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.tab-label span {
  font-size: 14px;
}

.tab-label .tab-count {
  margin-left: 8px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(16, 185, 129, 0.9);
  padding: 2px 8px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 4px;
}

.tab-label .tab-badge {
  position: absolute;
  top: -4px;
  right: -8px;
}

.tab-badge :deep(.el-badge__content) {
  background: #2962ff;
  border: 2px solid rgba(30, 41, 59, 0.9);
}

/* 分组统计 */
.group-stats {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.group-stats .stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.group-stats .stat-item svg {
  font-size: 14px;
  color: rgba(102, 126, 234, 0.8);
}

/* 响应式 */
@media (max-width: 768px) {
  .selection-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
