<template>
  <el-card class="task-list-card">
    <template #header>
      <div class="card-header">
        <h3>计算任务</h3>
        <el-space>
          <el-badge :value="runningCount" :hidden="runningCount === 0">
            <el-button size="small" :loading="loading" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-badge>
        </el-space>
      </div>
    </template>

    <el-table
      :data="tasks"
      stripe
      :empty-description="emptyText"
      max-height="300"
    >
      <el-table-column prop="task_id" label="任务ID" width="180" />
      <el-table-column prop="type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getTypeColor(row.type)" size="small">
            {{ getTypeText(row.type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            <el-icon v-if="row.status === 'running'" class="is-loading"><Loading /></el-icon>
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="进度" width="150">
        <template #default="{ row }">
          <el-progress
            v-if="row.status === 'running'"
            :percentage="row.progress?.percentage || 0"
            :stroke-width="12"
          />
          <span v-else class="text-muted">
            {{ row.progress?.completed || 0 }} / {{ row.progress?.total || 0 }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button-group>
            <el-button
              v-if="row.status === 'completed'"
              size="small"
              @click="handleViewResult(row)"
            >
              查看结果
            </el-button>
            <el-button
              v-if="row.status === 'failed'"
              size="small"
              type="warning"
              @click="handleRetry(row)"
            >
              重试
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <div v-if="tasks.length === 0" class="empty-placeholder">
      <el-empty description="暂无计算任务" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Refresh, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 类型定义
interface TaskProgress {
  total: number
  completed: number
  percentage: number
}

interface TaskInfo {
  task_id: string
  type: 'indicator' | 'alpha158' | 'alpha360' | 'custom'
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: TaskProgress
  created_at: string
  result?: any
}

// Props
interface Props {
  loading?: boolean
  tasks?: TaskInfo[]
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  tasks: () => []
})

// Emits
const emit = defineEmits<{
  (e: 'refresh'): void
  (e: 'view-result', task: TaskInfo): void
  (e: 'retry', task: TaskInfo): void
  (e: 'delete', task: TaskInfo): void
}>()

// 计算属性
const runningCount = computed(() => {
  return props.tasks.filter(t => t.status === 'running').length
})

const emptyText = computed(() => {
  return props.loading ? '加载中...' : '暂无任务'
})

// 方法
const handleRefresh = () => {
  emit('refresh')
}

const handleViewResult = (task: TaskInfo) => {
  emit('view-result', task)
}

const handleRetry = (task: TaskInfo) => {
  ElMessageBox.confirm(
    `确定要重新执行任务 ${task.task_id} 吗？`,
    '重试确认',
    {
      type: 'warning'
    }
  ).then(() => {
    emit('retry', task)
  }).catch(() => {
    // 用户取消
  })
}

const handleDelete = (task: TaskInfo) => {
  ElMessageBox.confirm(
    `确定要删除任务 ${task.task_id} 吗？`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).then(() => {
    emit('delete', task)
    ElMessage.success('任务已删除')
  }).catch(() => {
    // 用户取消
  })
}

const getTypeText = (type: string) => {
  const map: Record<string, string> = {
    indicator: '技术指标',
    alpha158: 'Alpha158',
    alpha360: 'Alpha360',
    custom: '自定义'
  }
  return map[type] || type
}

const getTypeColor = (type: string) => {
  const map: Record<string, any> = {
    indicator: '',
    alpha158: 'success',
    alpha360: 'warning',
    custom: 'info'
  }
  return map[type] || ''
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待执行',
    running: '计算中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}

// 自动刷新（仅当有运行中的任务时）
let refreshTimer: number | null = null

onMounted(() => {
  // 可以在这里启动定时刷新逻辑
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped lang="scss">
.task-list-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }
}

.text-muted {
  color: #909399;
  font-size: 13px;
}

.empty-placeholder {
  padding: 20px 0;
}

:deep(.el-table) {
  .el-button-group {
    display: flex;
  }
}
</style>
