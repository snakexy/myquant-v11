<template>
  <el-card class="task-list-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">📋 回测任务列表</span>
        <el-button type="primary" size="small" @click="refreshList">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </template>

    <!-- 筛选条件 -->
    <div class="filter-bar">
      <el-select
        v-model="filters.status"
        placeholder="全部状态"
        clearable
        @change="handleFilterChange"
        style="width: 120px; margin-right: 12px"
      >
        <el-option label="排队中" value="pending" />
        <el-option label="运行中" value="running" />
        <el-option label="已完成" value="completed" />
        <el-option label="失败" value="failed" />
      </el-select>

      <el-input
        v-model="filters.strategyName"
        placeholder="策略名称"
        clearable
        @change="handleFilterChange"
        style="width: 200px; margin-right: 12px"
      />
    </div>

    <!-- 任务表格 -->
    <el-table
      :data="taskList"
      v-loading="loading"
      stripe
      style="width: 100%"
      @row-click="handleRowClick"
    >
      <el-table-column prop="task_id" label="任务ID" width="160" />

      <el-table-column prop="strategy_name" label="策略名称" width="180" />

      <el-table-column prop="period" label="回测期间" width="180" />

      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="总收益率" width="100" v-if="showMetrics">
        <template #default="{ row }">
          <span
            :class="{
              'positive': row.total_return && row.total_return > 0,
              'negative': row.total_return && row.total_return < 0
            }"
          >
            {{ row.total_return ? formatPercent(row.total_return) : '-' }}
          </span>
        </template>
      </el-table-column>

      <el-table-column label="夏普比率" width="100" v-if="showMetrics">
        <template #default="{ row }">
          {{ row.sharpe_ratio ? row.sharpe_ratio.toFixed(2) : '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            link
            @click.stop="handleViewDetail(row)"
          >
            详情
          </el-button>
          <el-button
            type="info"
            size="small"
            link
            @click.stop="handleCompare(row)"
            v-if="row.status === 'completed'"
          >
            对比
          </el-button>
          <el-button
            type="danger"
            size="small"
            link
            @click.stop="handleDelete(row)"
            v-if="row.status === 'completed' || row.status === 'failed'"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getTaskList, type TaskSummary, TaskStatus, formatPercent } from '@/api/unifiedBacktest'

// Emits
const emit = defineEmits<{
  viewDetail: [task: TaskSummary]
  compare: [task: TaskSummary]
}>()

// Data
const loading = ref(false)
const taskList = ref<TaskSummary[]>([])

// Filters
const filters = reactive({
  status: '',
  strategyName: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// Show metrics
const showMetrics = computed(() => {
  return taskList.value.some(task => task.status === TaskStatus.COMPLETED)
})

// Load task list
const loadTaskList = async () => {
  loading.value = true
  try {
    const result = await getTaskList({
      page: pagination.page,
      pageSize: pagination.pageSize,
      status: filters.status || undefined,
      strategyName: filters.strategyName || undefined,
      sortBy: 'created_at',
      order: 'desc'
    })

    taskList.value = result.tasks
    pagination.total = result.total
  } catch (error) {
    ElMessage.error('加载任务列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// Refresh list
const refreshList = () => {
  loadTaskList()
}

// Handle filter change
const handleFilterChange = () => {
  pagination.page = 1
  loadTaskList()
}

// Handle page change
const handlePageChange = (page: number) => {
  pagination.page = page
  loadTaskList()
}

// Handle size change
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  loadTaskList()
}

// Handle row click
const handleRowClick = (row: TaskSummary) => {
  emit('viewDetail', row)
}

// Handle view detail
const handleViewDetail = (row: TaskSummary) => {
  emit('viewDetail', row)
}

// Handle compare
const handleCompare = (row: TaskSummary) => {
  emit('compare', row)
}

// Handle delete
const handleDelete = async (row: TaskSummary) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${row.task_id}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // TODO: 调用删除API
    ElMessage.success('删除成功')
    refreshList()
  } catch {
    // 用户取消
  }
}

// Get status type
const getStatusType = (status: TaskStatus) => {
  const typeMap: Record<TaskStatus, any> = {
    [TaskStatus.PENDING]: 'info',
    [TaskStatus.RUNNING]: 'primary',
    [TaskStatus.COMPLETED]: 'success',
    [TaskStatus.FAILED]: 'danger',
    [TaskStatus.CANCELLED]: 'warning'
  }
  return typeMap[status] || 'default'
}

// Get status text
const getStatusText = (status: TaskStatus) => {
  const textMap: Record<TaskStatus, string> = {
    [TaskStatus.PENDING]: '排队中',
    [TaskStatus.RUNNING]: '运行中',
    [TaskStatus.COMPLETED]: '已完成',
    [TaskStatus.FAILED]: '失败',
    [TaskStatus.CANCELLED]: '已取消'
  }
  return textMap[status] || status
}

// Format date
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  loadTaskList()
})

// Expose refresh method
defineExpose({
  refresh: refreshList
})
</script>

<style scoped lang="scss">
.task-list-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .filter-bar {
    margin-bottom: 16px;
    display: flex;
  }

  .pagination {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }

  :deep(.el-table) {
    .el-table__row {
      cursor: pointer;

      &:hover {
        background-color: #f5f7fa;
      }
    }
  }

  .positive {
    color: #f56c6c;
  }

  .negative {
    color: #67c23a;
  }
}
</style>
