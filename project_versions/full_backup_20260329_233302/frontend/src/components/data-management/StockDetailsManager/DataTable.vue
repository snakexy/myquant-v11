<template>
  <div class="data-table-container">
    <el-table :data="data" stripe max-height="500" class="stock-data-table">
      <el-table-column prop="date" label="日期" width="120" />
      <el-table-column prop="open" label="开盘" width="100">
        <template #default="{ row }">
          <span :class="row.change >= 0 ? 'up' : 'down'">{{ row.open }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="high" label="最高" width="100">
        <template #default="{ row }">
          <span :class="row.change >= 0 ? 'up' : 'down'">{{ row.high }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="low" label="最低" width="100">
        <template #default="{ row }">
          <span :class="row.change >= 0 ? 'up' : 'down'">{{ row.low }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="close" label="收盘" width="100">
        <template #default="{ row }">
          <span :class="row.change >= 0 ? 'up' : 'down'">{{ row.close }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="volume" label="成交量" width="120">
        <template #default="{ row }">
          {{ formatVolume(row.volume) }}
        </template>
      </el-table-column>
      <el-table-column prop="amount" label="成交额" width="120">
        <template #default="{ row }">
          {{ formatAmount(row.amount) }}
        </template>
      </el-table-column>
      <el-table-column prop="change" label="涨跌幅" width="100">
        <template #default="{ row }">
          <span :class="row.change >= 0 ? 'up' : 'down'">
            {{ row.change >= 0 ? '+' : '' }}{{ row.change.toFixed(2) }}%
          </span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { formatVolume, formatAmount } from '@/components/data-management/shared/utils'

interface StockDataRecord {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
  change: number
}

interface Props {
  data: StockDataRecord[]
}

defineProps<Props>()
</script>

<style scoped>
.data-table-container {
  padding: 16px 0;
}

:deep(.el-table) {
  background: rgba(255, 255, 255, 0.02);
  color: #ffffff;
  border-radius: 6px;
}

:deep(.el-table th) {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-table td) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

:deep(.el-table tr:hover > td) {
  background: rgba(255, 255, 255, 0.05) !important;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: rgba(0, 0, 0, 0.02);
}

.up {
  color: #ef4444;
}

.down {
  color: #10b981;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-table) {
    font-size: 12px;
  }

  :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }
}
</style>
