<template>
  <div class="position-table">
    <!-- 表格工具栏 -->
    <div class="table-toolbar">
      <div class="toolbar-left">
        <h3 class="table-title">📊 持仓列表</h3>
        <span class="record-count">共 {{ positions.length }} 只股票</span>
      </div>
      <div class="toolbar-right">
        <el-button size="small" @click="handleRefresh" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button size="small" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 持仓表格 -->
    <el-table
      :data="positions"
      stripe
      border
      :height="tableHeight"
      :empty-text="emptyText"
      v-loading="loading"
    >
      <el-table-column prop="symbol" label="代码" width="100" fixed />
      <el-table-column prop="symbolName" label="名称" width="120" fixed />
      <el-table-column prop="quantity" label="持仓数量" width="120" align="right">
        <template #default="{ row }">
          <span class="number">{{ formatNumber(row.quantity) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="avgPrice" label="成本价" width="100" align="right">
        <template #default="{ row }">
          <span class="number">¥{{ row.avgPrice.toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="currentPrice" label="现价" width="100" align="right">
        <template #default="{ row }">
          <span class="number">¥{{ row.currentPrice.toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="marketValue" label="市值" width="120" align="right">
        <template #default="{ row }">
          <span class="number">¥{{ formatNumber(row.marketValue) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="unrealizedPnl" label="盈亏" width="120" align="right">
        <template #default="{ row }">
          <span :class="['number', 'pnl-value', row.unrealizedPnl >= 0 ? 'positive' : 'negative']">
            {{ row.unrealizedPnl >= 0 ? '+' : '' }}¥{{ formatNumber(row.unrealizedPnl) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="unrealizedPnlRate" label="盈亏%" width="100" align="right">
        <template #default="{ row }">
          <span :class="['number', row.unrealizedPnlRate >= 0 ? 'positive' : 'negative']">
            {{ row.unrealizedPnlRate >= 0 ? '+' : '' }}{{ row.unrealizedPnlRate.toFixed(2) }}%
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="weight" label="仓位占比" width="100" align="right">
        <template #default="{ row }">
          <span class="number">{{ row.weight.toFixed(2) }}%</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 持仓汇总 -->
    <div class="position-summary">
      <div class="summary-item">
        <label>持仓市值</label>
        <value class="number">¥{{ formatNumber(totalMarketValue) }}</value>
      </div>
      <div class="summary-item">
        <label>总盈亏</label>
        <value :class="['number', totalPnl >= 0 ? 'positive' : 'negative']">
          {{ totalPnl >= 0 ? '+' : '' }}¥{{ formatNumber(totalPnl) }}
        </value>
      </div>
      <div class="summary-item">
        <label>盈亏比例</label>
        <value :class="['number', totalPnlRate >= 0 ? 'positive' : 'negative']">
          {{ totalPnlRate >= 0 ? '+' : '' }}{{ totalPnlRate.toFixed(2) }}%
        </value>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download } from '@element-plus/icons-vue'
import { simulationApi } from '@/api/modules/simulation'
import type { Position } from '@/api/modules/simulation'

// Props
interface Props {
  accountId?: string
  positions?: Position[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  accountId: 'default_account',
  positions: () => [],
  loading: false
})

// Emits
const emit = defineEmits<{
  refresh: []
}>()

// State
const refreshing = ref(false)
const tableHeight = ref(500)

// 计算空状态文本
const emptyText = computed(() => {
  return props.loading ? '加载中...' : '暂无持仓数据'
})

// 计算持仓汇总
const totalMarketValue = computed(() => {
  return props.positions.reduce((sum, pos) => sum + pos.marketValue, 0)
})

const totalPnl = computed(() => {
  return props.positions.reduce((sum, pos) => sum + pos.unrealizedPnl, 0)
})

const totalPnlRate = computed(() => {
  if (totalMarketValue.value === 0) return 0
  return (totalPnl.value / totalMarketValue.value) * 100
})

// 格式化数字
const formatNumber = (num: number) => {
  return Math.floor(num).toLocaleString('en-US')
}

// 刷新持仓数据
const handleRefresh = async () => {
  refreshing.value = true
  try {
    emit('refresh')
    ElMessage.success('持仓数据已刷新')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 导出持仓数据
const handleExport = () => {
  // TODO: 实现导出功能
  ElMessage.info('导出功能开发中...')
}
</script>

<style scoped lang="scss">
.position-table {
  .table-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .toolbar-left {
      display: flex;
      align-items: baseline;
      gap: 12px;

      .table-title {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }

      .record-count {
        font-size: 13px;
        color: #909399;
      }
    }

    .toolbar-right {
      display: flex;
      gap: 8px;
    }
  }

  .number {
    font-family: 'Consolas', 'Monaco', monospace;
    font-weight: 600;
  }

  .pnl-value {
    &.positive {
      color: #f56c6c; // 红色表示盈利
    }

    &.negative {
      color: #67c23a; // 绿色表示亏损
    }
  }

  .positive {
    color: #f56c6c;
  }

  .negative {
    color: #67c23a;
  }

  .position-summary {
    display: flex;
    gap: 24px;
    padding: 16px;
    margin-top: 16px;
    background-color: #f9fafb;
    border-radius: 8px;

    .summary-item {
      display: flex;
      flex-direction: column;
      gap: 4px;

      label {
        font-size: 12px;
        color: #909399;
      }

      value {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
  }
}
</style>
