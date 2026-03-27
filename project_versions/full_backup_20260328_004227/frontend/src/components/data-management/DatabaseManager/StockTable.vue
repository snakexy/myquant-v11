<template>
  <div class="stock-table-wrapper">
    <el-table
      :data="data"
      :loading="loading"
      size="default"
      @selection-change="handleSelectionChange"
      :default-sort="{ prop: sortBy, order: sortOrder === 'asc' ? 'ascending' : 'descending' }"
      class="stocks-table"
      :row-key="rowKey"
      ref="tableRef"
    >
      <el-table-column type="selection" width="60" align="center" />
      <el-table-column prop="displayCode" label="股票代码" width="110" sortable align="center" />
      <el-table-column prop="name" label="股票名称" width="130" sortable align="left">
        <template #default="{ row }">
          <div style="display: flex; align-items: center; justify-content: flex-start; padding-left: 16px;">
            <span>{{ row.name || '-' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="frequency" label="周期" width="90" sortable align="center">
        <template #default="{ row }">
          <el-tag :type="getFrequencyTagType(row.frequency)" size="small">
            {{ getFrequencyLabel(row.frequency) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="startDate" label="开始日期" width="125" sortable align="center">
        <template #default="{ row }">
          <span style="white-space: nowrap; color: rgba(255, 255, 255, 0.8);">
            {{ row.startDate || '-' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="endDate" label="结束日期" width="125" sortable align="center">
        <template #default="{ row }">
          <span :class="getDataAgeClass(row.dataAge)" style="white-space: nowrap;">
            {{ row.endDate || '-' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="dataAge" label="数据年龄" width="120" sortable align="center">
        <template #default="{ row }">
          <el-tag :type="getDataAgeTagType(row.dataAge)" size="small">
            {{ row.dataAge || 0 }} 天
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="healthScore" label="健康度" width="110" sortable align="center">
        <template #default="{ row }">
          <div style="display: flex; align-items: center; justify-content: center;">
            <span :style="{
              fontSize: '13px',
              fontWeight: '500',
              color: getHealthColor(row.healthScore || 0)
            }">
              {{ row.healthScore || 0 }}%
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="110" align="center" fixed="right">
        <template #default="{ row }">
          <el-button-group size="small">
            <el-button @click="$emit('update', row)" :loading="row.updating">
              <font-awesome-icon icon="sync-alt" />
            </el-button>
            <el-button type="danger" @click="$emit('delete', row)">
              <font-awesome-icon icon="trash" />
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <div class="pagination-info">
        共 {{ total }} 条
      </div>
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[20, 50, 100]"
        :total="total"
        layout="prev, pager, next"
        size="small"
        @update:current-page="$emit('update:currentPage', $event)"
        @update:page-size="$emit('update:pageSize', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ElTable } from 'element-plus'

interface StockRow {
  code: string
  displayCode: string
  name: string
  frequency: string
  startDate: string
  endDate: string
  recordCount: number
  dataAge: number
  healthScore: number
  updating?: boolean
}

interface Props {
  data: StockRow[]
  loading?: boolean
  total: number
  currentPage: number
  pageSize: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  rowKey?: string | ((row: StockRow) => string)
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  sortBy: 'code',
  sortOrder: 'asc',
  rowKey: (row: StockRow) => row.code
})

const emit = defineEmits<{
  'selection-change': [selection: StockRow[]]
  'update': [row: StockRow]
  'delete': [row: StockRow]
  'update:currentPage': [page: number]
  'update:pageSize': [size: number]
}>()

const tableRef = ref<InstanceType<typeof ElTable>>()

// 获取数据年龄样式类
const getDataAgeClass = (age: number) => {
  if (age > 30) return 'text-danger'
  if (age > 14) return 'text-warning'
  return 'text-success'
}

// 获取数据年龄标签类型
const getDataAgeTagType = (age: number) => {
  if (age > 30) return 'danger'
  if (age > 14) return 'warning'
  return 'success'
}

// 获取健康度颜色
const getHealthColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

// 获取周期标签
const getFrequencyLabel = (freq: string) => {
  const freqMap: Record<string, string> = {
    'daily': '日线',
    '1min': '1分',
    '5min': '5分',
    '15min': '15分',
    '30min': '30分',
    '60min': '60分'
  }
  return freqMap[freq] || freq
}

// 获取周期标签类型
const getFrequencyTagType = (freq: string) => {
  const typeMap: Record<string, string> = {
    'daily': 'primary',
    '1min': 'info',
    '5min': 'info',
    '15min': 'success',
    '30min': 'warning',
    '60min': 'danger'
  }
  return typeMap[freq] || 'info'
}

// 处理选择变化
const handleSelectionChange = (selection: StockRow[]) => {
  emit('selection-change', selection)
}

// 暴露 tableRef 供父组件调用
defineExpose({
  tableRef
})
</script>

<style scoped>
.stock-table-wrapper {
  display: flex;
  flex-direction: column;
}

/* 表格样式 */
:deep(.el-table) {
  background: transparent;
  border-radius: 12px;
  overflow: hidden;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

:deep(.el-table__header-wrapper) {
  background: linear-gradient(180deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%);
}

:deep(.el-table__header th) {
  background: transparent !important;
  color: #ffffff !important;
  font-weight: 600;
  font-size: 13px;
  border-bottom: none;
  padding: 16px 12px;
  text-align: center;
  letter-spacing: 0.5px;
}

:deep(.el-table__header tr) {
  background: transparent !important;
}

/* 隐藏排序指示器 */
:deep(.el-table__header th .caret-wrapper) {
  display: none;
}

:deep(.el-table__body td) {
  border-bottom: none;
  padding: 14px 12px;
  color: rgba(255, 255, 255, 0.8);
}

:deep(.el-table__body tr) {
  transition: all 0.25s ease;
  background: transparent !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

:deep(.el-table__body tr:last-child) {
  border-bottom: none;
}

:deep(.el-table__body tr:hover > td) {
  background: rgba(102, 126, 234, 0.04) !important;
}

:deep(.el-table__body tr:hover) {
  transform: scale(1.002);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

:deep(.el-table--border .el-table__cell) {
  border-right: none;
}

:deep(.el-table--border::after),
:deep(.el-table--group::after),
:deep(.el-table::before) {
  display: none;
}

/* 斑马纹 */
:deep(.el-table__body tr:nth-child(even)) {
  background: rgba(0, 0, 0, 0.01) !important;
}

/* Tag 标签 */
:deep(.el-tag) {
  border-radius: 12px;
  padding: 2px 10px;
  font-weight: 500;
  border: none;
}

:deep(.el-tag--success) {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.15) 0%, rgba(103, 194, 58, 0.08) 100%);
  color: #67c23a;
}

:deep(.el-tag--warning) {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.15) 0%, rgba(230, 162, 60, 0.08) 100%);
  color: #e6a23c;
}

:deep(.el-tag--danger) {
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.15) 0%, rgba(245, 108, 108, 0.08) 100%);
  color: #f56c6c;
}

:deep(.el-tag--info) {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.08) 100%);
  color: #3b82f6;
}

:deep(.el-tag--primary) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(102, 126, 234, 0.08) 100%);
  color: #2962ff;
}

/* 按钮组 */
:deep(.el-button-group) {
  border: none;
  border-radius: 0;
  overflow: visible;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

:deep(.el-button-group .el-button) {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  padding: 6px 8px;
  transition: all 0.2s ease;
}

:deep(.el-button-group .el-button:hover) {
  background: #2962ff;
  color: white;
  transform: scale(1.1);
}

:deep(.el-button-group .el-button--danger:hover) {
  background: #f56c6c;
}

/* 分页 */
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}

.pagination-info {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

:deep(.el-pagination) {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
}

:deep(.el-pagination button) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
  transition: all 0.2s ease;
}

:deep(.el-pagination button:hover) {
  border-color: #2962ff;
  color: #2962ff;
}

:deep(.el-pagination .el-pager li) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  margin: 0 2px;
  transition: all 0.2s ease;
}

:deep(.el-pagination .el-pager li:hover) {
  border-color: #2962ff;
  color: #2962ff;
}

:deep(.el-pagination .el-pager li.is-active) {
  background: linear-gradient(135deg, #2962ff 0%, #5568d3 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-pagination .el-pager li.is-active:hover) {
  color: white;
}

.text-danger {
  color: #f56c6c;
}

.text-warning {
  color: #e6a23c;
}

.text-success {
  color: #67c23a;
}
</style>
