<template>
  <div class="trade-table">
    <!-- 表格工具栏 -->
    <div class="table-toolbar">
      <div class="toolbar-left">
        <h3 class="table-title">📝 交易记录</h3>
        <span class="record-count">共 {{ orders.length }} 条记录</span>
      </div>
      <div class="toolbar-right">
        <el-select
          v-model="statusFilter"
          placeholder="全部状态"
          size="small"
          style="width: 120px"
          @change="handleFilterChange"
        >
          <el-option label="全部" value="" />
          <el-option label="待成交" value="pending" />
          <el-option label="已成交" value="filled" />
          <el-option label="已撤销" value="cancelled" />
          <el-option label="失败" value="failed" />
        </el-select>
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

    <!-- 交易记录表格 -->
    <el-table
      :data="filteredOrders"
      stripe
      border
      :height="tableHeight"
      :empty-text="emptyText"
      v-loading="loading"
    >
      <el-table-column prop="orderId" label="订单ID" width="180" fixed />
      <el-table-column prop="symbol" label="股票代码" width="100" />
      <el-table-column prop="side" label="方向" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.side === 'buy' ? 'success' : 'danger'" size="small">
            {{ row.side === 'buy' ? '买入' : '卖出' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="orderType" label="类型" width="80" align="center">
        <template #default="{ row }">
          <el-tag type="info" size="small">
            {{ row.orderType === 'market' ? '市价' : '限价' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="委托数量" width="100" align="right">
        <template #default="{ row }">
          <span class="number">{{ formatNumber(row.quantity) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="price" label="委托价格" width="100" align="right">
        <template #default="{ row }">
          <span class="number">¥{{ row.price.toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="filledQuantity" label="成交数量" width="100" align="right">
        <template #default="{ row }">
          <span class="number">{{ formatNumber(row.filledQuantity) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="filledPrice" label="成交价格" width="100" align="right">
        <template #default="{ row }">
          <span v-if="row.filledPrice > 0" class="number">¥{{ row.filledPrice.toFixed(2) }}</span>
          <span v-else class="empty-text">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="委托时间" width="180" />
      <el-table-column prop="updateTime" label="更新时间" width="180" />
    </el-table>

    <!-- 交易汇总 -->
    <div class="trade-summary">
      <div class="summary-item">
        <label>总委托数</label>
        <value class="number">{{ orders.length }}</value>
      </div>
      <div class="summary-item">
        <label>已成交</label>
        <value class="number">{{ filledCount }}</value>
      </div>
      <div class="summary-item">
        <label>成交率</label>
        <value class="number">{{ fillRate.toFixed(2) }}%</value>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download } from '@element-plus/icons-vue'
import type { Order } from '@/api/modules/simulation'

// Props
interface Props {
  orders?: Order[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  orders: () => [],
  loading: false
})

// Emits
const emit = defineEmits<{
  refresh: []
}>()

// State
const statusFilter = ref<string>('')
const refreshing = ref(false)
const tableHeight = ref(500)

// 计算空状态文本
const emptyText = computed(() => {
  return props.loading ? '加载中...' : '暂无交易记录'
})

// 计算筛选后的订单
const filteredOrders = computed(() => {
  if (!statusFilter.value) {
    return props.orders
  }
  return props.orders.filter(order => order.status === statusFilter.value)
})

// 获取状态标签类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    filled: 'success',
    cancelled: 'info',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待成交',
    filled: '已成交',
    cancelled: '已撤销',
    failed: '失败'
  }
  return textMap[status] || status
}

// 计算成交数量
const filledCount = computed(() => {
  return props.orders.filter(order => order.status === 'filled').length
})

// 计算成交率
const fillRate = computed(() => {
  if (props.orders.length === 0) return 0
  return (filledCount.value / props.orders.length) * 100
})

// 格式化数字
const formatNumber = (num: number) => {
  return Math.floor(num).toLocaleString('en-US')
}

// 筛选变化处理
const handleFilterChange = () => {
  // 筛选逻辑已在computed中实现
}

// 刷新交易记录
const handleRefresh = async () => {
  refreshing.value = true
  try {
    emit('refresh')
    ElMessage.success('交易记录已刷新')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 导出交易记录
const handleExport = () => {
  // TODO: 实现导出功能
  ElMessage.info('导出功能开发中...')
}
</script>

<style scoped lang="scss">
.trade-table {
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

  .empty-text {
    color: #c0c4cc;
    font-size: 13px;
  }

  .trade-summary {
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
