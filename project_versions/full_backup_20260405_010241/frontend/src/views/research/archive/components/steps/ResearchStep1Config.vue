<!--
  ResearchStep1Config.vue
  步骤1：数据配置组件
  包含股票池选择、日期范围选择、周期选择功能
-->
<template>
  <div class="task-config-info">
    <!-- 股票池配置 -->
    <div class="config-item">
      <span class="config-label">
        <svg class="config-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
          <path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"></path>
        </svg>
        {{ isZh ? '股票池' : 'Stock Pool' }}
      </span>
      <div class="stock-pool-wrap">
        <el-select
          :model-value="stockPool"
          @change="handleStockPoolChange"
          size="small"
          :placeholder="isZh ? '选择' : 'Select'"
        >
          <el-option label="沪深300" value="CSI300"></el-option>
          <el-option label="中证500" value="CSI500"></el-option>
          <el-option label="中证1000" value="CSI1000"></el-option>
          <el-option label="全市场" value="All A-shares"></el-option>
          <el-option label="自定义" value="custom"></el-option>
        </el-select>
        <span v-if="stockPool === 'custom' && customStocks" class="custom-stocks-count">
          {{ customStocks.split(',').length }} {{ isZh ? '只' : 'stocks' }}
        </span>
        <el-button
          v-if="stockPool === 'custom'"
          size="small"
          @click="handleEditCustomStocks"
        >
          {{ isZh ? '编辑' : 'Edit' }}
        </el-button>
      </div>
    </div>

    <!-- 日期范围配置 -->
    <div class="config-item">
      <span class="config-label">
        <svg class="config-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        {{ isZh ? '日期范围' : 'Date Range' }}
      </span>
      <el-date-picker
        :model-value="dateRange"
        @update:model-value="handleDateRangeChange"
        type="daterange"
        range-separator="~"
        :start-placeholder="isZh ? '开始日期' : 'Start'"
        :end-placeholder="isZh ? '结束日期' : 'End'"
        size="small"
        :cell-class-name="getDateCellClass"
        style="width: 240px;"
      />
    </div>

    <!-- 周期配置 -->
    <div class="config-item">
      <span class="config-label">
        <svg class="config-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        {{ isZh ? '周期' : 'Period' }}
      </span>
      <el-select
        :model-value="periods"
        @change="handlePeriodsChange"
        multiple
        size="small"
        style="width: auto; min-width: 100px;"
        :placeholder="isZh ? '选择周期' : 'Select periods'"
      >
        <el-option
          v-for="p in periodOptions"
          :key="p.value"
          :label="isZh ? p.label : p.value"
          :value="p.value"
        />
      </el-select>
    </div>

    <!-- 自定义股票编辑对话框 -->
    <el-dialog
      v-model="showCustomStockDialog"
      :title="isZh ? '自定义股票池' : 'Custom Stock Pool'"
      width="500px"
      class="custom-stock-dialog"
    >
      <div class="dialog-header-with-icon">
        <svg class="dialog-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
          <path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"></path>
        </svg>
        <span>{{ isZh ? '自定义股票池' : 'Custom Stock Pool' }}</span>
      </div>

      <div class="custom-stock-dialog-content">
        <p class="dialog-desc">
          {{ isZh ? '请输入股票代码，用逗号或换行分隔' : 'Enter stock codes, separated by commas or newlines' }}
        </p>
        <el-input
          v-model="customStocksInput"
          type="textarea"
          :rows="8"
          :placeholder="isZh ? '例如：000001, 000002, 600000' : 'Example: 000001, 000002, 600000'"
        />
        <div class="dialog-tips">
          <p>{{ isZh ? '提示：' : 'Tips:' }}</p>
          <ul>
            <li>{{ isZh ? '支持A股6位代码' : 'Support A-share 6-digit codes' }}</li>
            <li>{{ isZh ? '可使用逗号、空格或换行分隔' : 'Can use commas, spaces, or newlines to separate' }}</li>
            <li>{{ isZh ? '最多支持1000只股票' : 'Maximum 1000 stocks' }}</li>
          </ul>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCustomStockDialog = false">
            {{ isZh ? '取消' : 'Cancel' }}
          </el-button>
          <el-button type="primary" @click="handleSaveCustomStocks">
            {{ isZh ? '保存' : 'Save' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, PropType } from 'vue'

// Props定义
const props = defineProps({
  stockPool: {
    type: String,
    required: true
  },
  customStocks: {
    type: String,
    default: ''
  },
  dateRange: {
    type: Array as PropType<Date[] | null>,
    default: null
  },
  periods: {
    type: Array as PropType<string[]>,
    required: true
  },
  isZh: {
    type: Boolean,
    default: true
  }
})

// Emits定义
const emit = defineEmits<{
  'update:stockPool': [value: string]
  'update:customStocks': [value: string]
  'update:dateRange': [value: Date[] | null]
  'update:periods': [value: string[]]
}>()

// 本地状态
const showCustomStockDialog = ref(false)
const customStocksInput = ref('')

// 周期选项
const periodOptions = [
  { label: '日线', value: '1d' },
  { label: '周线', value: '1w' },
  { label: '月线', value: '1M' },
  { label: '季线', value: '1q' },
  { label: '年线', value: '1y' },
  { label: '5分钟', value: '5m' },
  { label: '15分钟', value: '15m' },
  { label: '30分钟', value: '30m' },
  { label: '60分钟', value: '60m' }
]

// 处理股票池变化
const handleStockPoolChange = (val: string) => {
  emit('update:stockPool', val)
  if (val === 'custom') {
    showCustomStockDialog.value = true
  } else {
    emit('update:customStocks', '')
  }
}

// 处理编辑自定义股票
const handleEditCustomStocks = () => {
  customStocksInput.value = props.customStocks
  showCustomStockDialog.value = true
}

// 处理保存自定义股票
const handleSaveCustomStocks = () => {
  // 清理输入：去除空格、空行，统一用逗号分隔
  const stocks = customStocksInput.value
    .split(/[,\s\n]+/)
    .map(s => s.trim())
    .filter(s => s.length > 0)
    .join(',')

  emit('update:customStocks', stocks)
  showCustomStockDialog.value = false
}

// 处理日期范围变化
const handleDateRangeChange = (value: Date[] | null) => {
  emit('update:dateRange', value)
}

// 处理周期变化
const handlePeriodsChange = (value: string[]) => {
  emit('update:periods', value)
}

// 日期单元格类名（用于自定义日期范围样式）
const getDateCellClass = (data: { date: Date }) => {
  if (!props.dateRange || !Array.isArray(props.dateRange) || props.dateRange.length < 2) {
    return ''
  }
  const cellDate = new Date(data.date)
  const startDate = new Date(props.dateRange[0])
  const endDate = new Date(props.dateRange[1])

  // 设置时间为0点进行比较
  cellDate.setHours(0, 0, 0, 0)
  startDate.setHours(0, 0, 0, 0)
  endDate.setHours(0, 0, 0, 0)

  if (cellDate.getTime() === startDate.getTime()) {
    return 'custom-date-start'
  }
  if (cellDate.getTime() === endDate.getTime()) {
    return 'custom-date-end'
  }
  if (cellDate > startDate && cellDate < endDate) {
    return 'custom-date-inrange'
  }
  return ''
}
</script>

<style scoped lang="scss">
.task-config-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 8px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stock-pool-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stock-pool-wrap .el-select {
  width: auto;
  min-width: 100px;
}

.custom-stocks-count {
  font-size: 12px;
  color: var(--accent-blue);
  margin-left: 0;
}

.config-label {
  font-size: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.config-icon {
  width: 12px;
  height: 12px;
}

.dialog-header-with-icon {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;

  .dialog-header-icon {
    width: 20px;
    height: 20px;
    color: var(--accent-blue);
  }

  span {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.custom-stock-dialog-content {
  .dialog-desc {
    margin-bottom: 12px;
    color: var(--text-secondary);
  }

  :deep(.el-textarea__inner) {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border-color: var(--border-color);
  }

  .dialog-tips {
    margin-top: 12px;
    padding: 12px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    font-size: 12px;
    color: var(--text-secondary);

    p {
      margin-bottom: 8px;
      font-weight: 600;
    }

    ul {
      margin: 0;
      padding-left: 20px;
    }

    li {
      margin-bottom: 4px;
    }
  }
}

/* 日期选择器样式修复 */
:deep(.el-date-editor) {
  background: rgba(255, 255, 255, 0.05) !important;
}

/* 强制所有日期编辑器背景透明 */
:deep(.el-date-editor.el-range-editor),
:deep(.el-date-editor.el-range-editor.el-input__wrapper),
:deep(.el-date-editor.el-range-editor .el-range-input),
:deep(.el-range-editor .el-range-input) {
  background: transparent !important;
  background-color: transparent !important;
}

:deep(.el-date-editor .el-range-input) {
  color: #e0e0e0 !important;
  background: transparent !important;
}

:deep(.el-date-editor .el-range-input::placeholder) {
  color: rgba(255, 255, 255, 0.4) !important;
}

:deep(.el-date-editor .el-range-separator) {
  color: rgba(255, 255, 255, 0.4) !important;
}

/* 日期范围编辑器背景强制透明 */
:deep(.el-range-editor.el-input__wrapper),
:deep(.el-range-editor.el-input__wrapper:hover),
:deep(.el-range-editor.el-input__wrapper.is-focus) {
  background: transparent !important;
  box-shadow: none !important;
}

/* 自定义日期单元格样式 */
:deep(.custom-date-start .cell),
:deep(.custom-date-end .cell) {
  background: var(--el-color-primary) !important;
  color: #fff !important;
}

:deep(.custom-date-inrange .cell) {
  background: rgba(var(--el-color-primary-rgb), 0.2) !important;
}

/* 对话框样式 */
:deep(.custom-stock-dialog) {
  .el-dialog__header {
    padding: 0;
    margin-bottom: 16px;
  }

  .el-dialog__body {
    padding: 0;
  }

  .el-dialog__footer {
    padding: 0;
    margin-top: 16px;
  }
}
</style>
