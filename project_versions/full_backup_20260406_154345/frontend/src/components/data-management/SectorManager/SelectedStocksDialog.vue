<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="选中股票列表"
    width="800px"
    append-to-body
    custom-class="selected-stocks-dialog"
    :z-index="20000"
  >
    <el-table :data="stocks" max-height="500">
      <el-table-column prop="code" label="股票代码" width="120" />
      <el-table-column prop="name" label="股票名称" width="150" />
      <el-table-column label="市场" width="80">
        <template #default="{ row }">
          <el-tag :type="getMarketTagType(row.market)" size="small">{{ row.market }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="industry" label="所属行业" />
    </el-table>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">关闭</el-button>
      <el-button type="primary" @click="handleConfirm">
        确认并查看详情
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
interface StockInfo {
  code: string
  name: string
  market: string
  industry: string
}

interface Props {
  visible: boolean
  stocks: StockInfo[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'confirm': [stocks: StockInfo[]]
}>()

// 获取市场标签类型
const getMarketTagType = (market: string) => {
  const typeMap: Record<string, string> = {
    '上海': 'success',
    '深圳': 'warning',
    '北交所': 'info'
  }
  return typeMap[market] || 'info'
}

// 确认选择
const handleConfirm = () => {
  emit('confirm', props.stocks)
  emit('update:visible', false)
}
</script>

<style>
/* 全局样式 - 确保对话框在导航栏之上 */
.selected-stocks-dialog .el-dialog {
  z-index: 20000 !important;
}

.selected-stocks-dialog .el-dialog__header {
  z-index: 20001 !important;
}

.selected-stocks-dialog .el-dialog__body {
  z-index: 20000 !important;
}

.selected-stocks-dialog .el-overlay {
  z-index: 19999 !important;
}
</style>

<style scoped>
:deep(.el-table) {
  background: rgba(255, 255, 255, 0.02);
  color: #ffffff;
}

:deep(.el-table th) {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
}

:deep(.el-table tr:hover > td) {
  background: rgba(255, 255, 255, 0.05) !important;
}

:deep(.el-dialog) {
  background: rgba(26, 26, 46, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-dialog__title) {
  color: #ffffff;
}

:deep(.el-dialog__body) {
  color: rgba(255, 255, 255, 0.8);
}
</style>
