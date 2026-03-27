<template>
  <div class="filter-panel">
    <div class="panel-header">
      <!-- 周期筛选 -->
      <div class="frequency-filter">
        <label class="filter-label">周期:</label>
        <div class="frequency-chips">
          <label
            v-for="freq in frequencies"
            :key="freq.value"
            :class="['freq-chip', { active: modelValue.includes(freq.value) }]"
          >
            <input
              type="checkbox"
              :value="freq.value"
              @change="toggleFrequency(freq.value)"
            />
            <span>{{ freq.label }}</span>
          </label>
        </div>
      </div>
    </div>

    <div class="panel-actions">
      <input
        :value="searchText"
        @input="handleSearchInput"
        class="search-input"
        placeholder="搜索代码/名称/拼音(如: pfyh, pufayinhang)"
      />

      <el-dropdown trigger="click" @command="handleBatchAction">
        <el-button size="small" :disabled="selectedCount === 0">
          批量操作
          <font-awesome-icon icon="caret-down" style="margin-left: 4px" />
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="update">
              <font-awesome-icon icon="sync-alt" style="margin-right: 8px" />
              批量更新
            </el-dropdown-item>
            <el-dropdown-item command="export">
              <font-awesome-icon icon="download" style="margin-right: 8px" />
              导出清单
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface FrequencyOption {
  label: string
  value: string
}

interface Props {
  frequencies: FrequencyOption[]
  modelValue: string[]
  selectedCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  selectedCount: 0
})

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
  'search': [text: string]
  'batch-action': [command: string]
}>()

const searchText = ref('')

// 切换频率选择
const toggleFrequency = (value: string) => {
  const newValue = [...props.modelValue]
  const index = newValue.indexOf(value)

  if (index > -1) {
    newValue.splice(index, 1)
  } else {
    newValue.push(value)
  }

  emit('update:modelValue', newValue)
}

// 处理搜索输入
const handleSearchInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  searchText.value = target.value
  emit('search', target.value)
}

// 处理批量操作
const handleBatchAction = (command: string) => {
  emit('batch-action', command)
}
</script>

<style scoped>
.filter-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 16px;
}

.panel-header {
  display: flex;
  align-items: center;
  flex: 1;
}

.frequency-filter {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  white-space: nowrap;
}

.frequency-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.freq-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.freq-chip:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.freq-chip.active {
  background: rgba(102, 126, 234, 0.2);
  border-color: #2962ff;
  color: #2962ff;
}

.freq-chip input[type="checkbox"] {
  display: none;
}

.freq-chip span {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.freq-chip.active span {
  color: #2962ff;
}

.panel-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-input {
  width: 200px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 8px 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #2962ff;
  background: rgba(255, 255, 255, 0.08);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .panel-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .panel-actions {
    justify-content: space-between;
  }

  .search-input {
    flex: 1;
  }
}
</style>

<style>
/* 下拉菜单全局样式 */
.filter-panel .el-dropdown-menu {
  background: #1e293b !important;
  border: 1px solid #334155 !important;
  border-radius: 8px !important;
  padding: 8px !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
  min-width: 170px !important;
}

.filter-panel .el-dropdown-menu__item {
  color: #94a3b8 !important;
  border-radius: 6px !important;
  padding: 12px 16px !important;
  transition: all 0.2s ease !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  margin: 3px 0 !important;
  background: transparent !important;
}

.filter-panel .el-dropdown-menu__item:hover {
  background: #3b82f6 !important;
  color: #ffffff !important;
  cursor: pointer !important;
}
</style>
