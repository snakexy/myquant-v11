<template>
  <div class="step-data-config-panel">
    <!-- 任务配置信息 -->
    <div class="task-config-info">
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
            size="small"
            placeholder="选择"
            @update:model-value="handleStockPoolChange"
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
          <el-button v-if="stockPool === 'custom'" size="small" @click="showCustomStockDialog = true">
            {{ isZh ? '编辑' : 'Edit' }}
          </el-button>
        </div>
      </div>
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
          start-placeholder="Start"
          end-placeholder="End"
          size="small"
          :cell-class-name="getDateCellClass"
          style="width: 240px;"
        />
      </div>
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
          @update:model-value="handlePeriodsChange"
          multiple
          size="small"
          style="width: auto; min-width: 100px;"
          placeholder="选择周期"
        >
          <el-option
            v-for="p in periodOptions"
            :key="p.value"
            :label="isZh ? p.label : p.value"
            :value="p.value"
          />
        </el-select>
      </div>
    </div>

    <!-- 自定义股票池弹窗 -->
    <el-dialog v-model="showCustomStockDialog" width="500px" :show-close="true">
      <template #header>
        <div class="dialog-header-with-icon">
          <svg class="dialog-header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"/>
            <rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/>
            <rect x="3" y="14" width="7" height="7"/>
          </svg>
          <span>{{ isZh ? '自定义股票池' : 'Custom Stock Pool' }}</span>
        </div>
      </template>
      <div class="custom-stock-dialog-content">
        <p class="dialog-desc">{{ isZh ? '输入股票代码，每行一个' : 'Enter stock codes, one per line' }}</p>
        <el-input v-model="localCustomStocks" type="textarea" :rows="10" placeholder="000001.SZ&#10;000002.SZ&#10;000004.SZ" />
        <div class="dialog-tips">
          <p>{{ isZh ? '提示：支持以下格式' : 'Tips: Supports formats below' }}</p>
          <ul>
            <li>{{ isZh ? '沪深A股：000001.SZ, 600000.SH' : 'A-shares: 000001.SZ, 600000.SH' }}</li>
            <li>{{ isZh ? '每行一个代码，或用逗号分隔' : 'One code per line, or comma separated' }}</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="showCustomStockDialog = false">{{ isZh ? '取消' : 'Cancel' }}</el-button>
        <el-button @click="confirmCustomStocks" style="background: var(--accent-blue); border-color: var(--accent-blue); color: white;">
          {{ isZh ? '确定' : 'Confirm' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useAppStore } from '@/stores/core/AppStore'

interface Props {
  taskId?: string
  isZh?: boolean
  modelStockPool?: string
  modelCustomStocks?: string
  modelDateRange?: Date[] | null
  modelPeriods?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  taskId: '',
  isZh: true,
  modelStockPool: 'CSI300',
  modelCustomStocks: '',
  modelDateRange: null,
  modelPeriods: () => ['1d']
})

const emit = defineEmits<{
  'update:modelStockPool': [value: string]
  'update:modelCustomStocks': [value: string]
  'update:modelDateRange': [value: Date[] | null]
  'update:modelPeriods': [value: string[]]
}>()

const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// 本地状态
const stockPool = ref(props.modelStockPool)
const customStocks = ref(props.modelCustomStocks)
const dateRange = ref<Date[] | null>(props.modelDateRange)
const periods = ref<string[]>(props.modelPeriods)
const showCustomStockDialog = ref(false)
const localCustomStocks = ref('')

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
  { label: '60分钟', value: '60m' },
]

// 监听 props 变化
watch(() => props.modelStockPool, (newVal) => {
  stockPool.value = newVal
})

watch(() => props.modelCustomStocks, (newVal) => {
  customStocks.value = newVal
})

watch(() => props.modelDateRange, (newVal) => {
  dateRange.value = newVal
}, { deep: true })

watch(() => props.modelPeriods, (newVal) => {
  periods.value = newVal
}, { deep: true })

// 处理股票池变更
const handleStockPoolChange = (val: string) => {
  stockPool.value = val
  emit('update:modelStockPool', val)
  if (val === 'custom') {
    localCustomStocks.value = customStocks.value
    showCustomStockDialog.value = true
  } else {
    customStocks.value = ''
    emit('update:modelCustomStocks', '')
  }
}

// 确认自定义股票
const confirmCustomStocks = () => {
  customStocks.value = localCustomStocks.value
  emit('update:modelCustomStocks', localCustomStocks.value)
  showCustomStockDialog.value = false
}

// 处理日期范围变更
const handleDateRangeChange = (val: Date[] | null) => {
  dateRange.value = val
  emit('update:modelDateRange', val)
}

// 处理周期变更
const handlePeriodsChange = (val: string[]) => {
  periods.value = val
  emit('update:modelPeriods', val)
}

// 日期单元格类名
const getDateCellClass = (data: { date: Date }) => {
  if (!dateRange.value || !Array.isArray(dateRange.value) || dateRange.value.length < 2) {
    return ''
  }
  const cellDate = new Date(data.date)
  const startDate = new Date(dateRange.value[0])
  const endDate = new Date(dateRange.value[1])

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
.step-data-config-panel {
  width: 100%;
}

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
  margin-left: 8px;
}

.dialog-header-with-icon {
  display: flex;
  align-items: center;
  gap: 10px;

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
</style>
