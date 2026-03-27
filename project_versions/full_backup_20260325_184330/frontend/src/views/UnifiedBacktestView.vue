<template>
  <div class="unified-backtest-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">🚀 统一回测系统</h1>
        <p class="page-subtitle">基于M3-3统一API的现代化回测界面</p>
      </div>
      <div class="header-right">
        <el-button @click="handleBack">返回</el-button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <el-row :gutter="16">
      <!-- 左侧：回测表单 -->
      <el-col :span="8">
        <BacktestForm
          :loading="submitting"
          @submit="handleSubmitBacktest"
        />
      </el-col>

      <!-- 右侧：结果展示 -->
      <el-col :span="16">
        <el-tabs v-model="activeTab" class="result-tabs">
          <!-- 当前回测结果 -->
          <el-tab-pane label="当前回测" name="current">
            <div v-if="currentResult" class="result-container">
              <BacktestResults :result="currentResult" />
            </div>
            <el-empty
              v-else
              description="请先提交回测任务"
              :image-size="200"
            />
          </el-tab-pane>

          <!-- 历史任务列表 -->
          <el-tab-pane label="历史任务" name="history">
            <TaskList
              ref="taskListRef"
              @viewDetail="handleViewDetail"
              @compare="handleCompare"
            />
          </el-tab-pane>

          <!-- 对比分析 -->
          <el-tab-pane label="对比分析" name="compare">
            <div v-if="compareTasks.length > 0" class="compare-container">
              <div class="compare-header">
                <h3>已选择 {{ compareTasks.length }} 个任务</h3>
                <el-button
                  type="primary"
                  size="small"
                  @click="handleExecuteCompare"
                  :disabled="compareTasks.length < 2"
                >
                  开始对比
                </el-button>
                <el-button
                  size="small"
                  @click="handleClearCompare"
                >
                  清空
                </el-button>
              </div>

              <el-table :data="compareTasks" stripe>
                <el-table-column prop="task_id" label="任务ID" width="160" />
                <el-table-column prop="strategy_name" label="策略名称" />
                <el-table-column label="操作">
                  <template #default="{ row }">
                    <el-button
                      type="danger"
                      size="small"
                      link
                      @click="handleRemoveCompare(row)"
                    >
                      移除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <el-empty
              v-else
              description="请从历史任务列表中选择至少2个任务进行对比"
              :image-size="200"
            />
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>

    <!-- 任务进度对话框 -->
    <el-dialog
      v-model="showProgressDialog"
      title="回测进行中"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <div class="progress-dialog">
        <div class="task-info">
          <div class="info-item">
            <span class="label">任务ID:</span>
            <span class="value">{{ currentTaskId }}</span>
          </div>
          <div class="info-item">
            <span class="label">策略名称:</span>
            <span class="value">{{ currentTaskName }}</span>
          </div>
        </div>

        <el-progress
          :percentage="progressPercentage"
          :status="progressStatus"
        >
          <span class="progress-text">{{ progressText }}</span>
        </el-progress>

        <div class="progress-steps">
          <el-steps :active="currentStep" finish-status="success" simple>
            <el-step title="排队" />
            <el-step title="准备数据" />
            <el-step title="执行回测" />
            <el-step title="生成报告" />
            <el-step title="完成" />
          </el-steps>
        </div>
      </div>

      <template #footer>
        <el-button @click="handleCancelTask" :disabled="taskCompleted">
          取消任务
        </el-button>
        <el-button
          type="primary"
          @click="handleViewResult"
          :disabled="!taskCompleted"
        >
          查看结果
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import BacktestForm from '@/components/backtest/BacktestForm.vue'
import TaskList from '@/components/backtest/TaskList.vue'
import BacktestResults from '@/components/backtest/BacktestResults.vue'
import {
  executeBacktest,
  getTaskStatus,
  getTaskResults,
  pollTaskStatus,
  compareBacktests,
  type BacktestExecuteRequest,
  type BacktestResultData,
  type TaskSummary,
  type TaskStatusResponse,
  TaskStatus
} from '@/api/unifiedBacktest'

const router = useRouter()

// State
const activeTab = ref('current')
const submitting = ref(false)
const currentResult = ref<BacktestResultData>()
const taskListRef = ref()
const compareTasks = ref<TaskSummary[]>([])

// Progress dialog
const showProgressDialog = ref(false)
const currentTaskId = ref('')
const currentTaskName = ref('')
const currentProgress = ref(0)
const currentStep = ref(0)
const currentStatus = ref<TaskStatus>(TaskStatus.PENDING)
const taskCompleted = ref(false)

// Submit backtest
const handleSubmitBacktest = async (data: BacktestExecuteRequest) => {
  submitting.value = true

  try {
    // Submit task
    const result = await executeBacktest(data)

    ElMessage.success('回测任务已提交')

    // Show progress dialog
    currentTaskId.value = result.task_id
    currentTaskName.value = data.strategy_name
    currentProgress.value = 0
    currentStep.value = 0
    currentStatus.value = TaskStatus.PENDING
    taskCompleted.value = false
    showProgressDialog.value = true

    // Poll task status
    pollTask(result.task_id)
  } catch (error) {
    ElMessage.error('提交回测任务失败')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

// Poll task status
const pollTask = async (taskId: string) => {
  try {
    const status = await pollTaskStatus(
      taskId,
      (progress) => {
        // Update progress
        currentProgress.value = progress.progress * 100

        // Update step based on progress
        if (progress.progress < 0.2) {
          currentStep.value = 0
        } else if (progress.progress < 0.4) {
          currentStep.value = 1
        } else if (progress.progress < 0.7) {
          currentStep.value = 2
        } else if (progress.progress < 0.9) {
          currentStep.value = 3
        } else {
          currentStep.value = 4
        }

        currentStatus.value = progress.status
      },
      2000 // Poll every 2 seconds
    )

    // Task completed
    taskCompleted.value = true
    currentProgress.value = 100
    currentStep.value = 4
    currentStatus.value = status.status

    if (status.status === TaskStatus.COMPLETED) {
      ElMessage.success('回测任务完成')

      // Get results
      const result = await getTaskResults(taskId)
      currentResult.value = result
      activeTab.value = 'current'
    } else if (status.status === TaskStatus.FAILED) {
      ElMessage.error(`回测任务失败: ${status.error_message}`)
    }

    // Refresh task list
    taskListRef.value?.refresh()
  } catch (error) {
    ElMessage.error('查询任务状态失败')
    console.error(error)
  }
}

// Cancel task
const handleCancelTask = () => {
  ElMessageBox.confirm('确定要取消当前任务吗？', '确认', {
    type: 'warning'
  }).then(() => {
    // TODO: Implement cancel API
    showProgressDialog.value = false
    ElMessage.info('任务已取消')
  }).catch(() => {
    // User cancelled
  })
}

// View result
const handleViewResult = () => {
  showProgressDialog.value = false
  activeTab.value = 'current'
}

// View detail
const handleViewDetail = async (task: TaskSummary) => {
  try {
    const result = await getTaskResults(task.task_id)
    currentResult.value = result
    activeTab.value = 'current'
  } catch (error) {
    ElMessage.error('获取回测结果失败')
    console.error(error)
  }
}

// Compare
const handleCompare = (task: TaskSummary) => {
  if (compareTasks.value.find(t => t.task_id === task.task_id)) {
    ElMessage.warning('该任务已在对比列表中')
    return
  }

  if (compareTasks.value.length >= 10) {
    ElMessage.warning('最多只能对比10个任务')
    return
  }

  compareTasks.value.push(task)
  activeTab.value = 'compare'
}

// Remove compare
const handleRemoveCompare = (task: TaskSummary) => {
  const index = compareTasks.value.findIndex(t => t.task_id === task.task_id)
  if (index > -1) {
    compareTasks.value.splice(index, 1)
  }
}

// Clear compare
const handleClearCompare = () => {
  compareTasks.value = []
}

// Execute compare
const handleExecuteCompare = async () => {
  if (compareTasks.value.length < 2) {
    ElMessage.warning('请至少选择2个任务进行对比')
    return
  }

  try {
    const result = await compareBacktests({
      task_ids: compareTasks.value.map(t => t.task_id),
      compare_metrics: ['total_return', 'sharpe_ratio', 'max_drawdown']
    })

    ElMessage.success('对比完成')

    // TODO: Show compare result dialog
    console.log('Compare result:', result)
  } catch (error) {
    ElMessage.error('对比失败')
    console.error(error)
  }
}

// Back
const handleBack = () => {
  router.back()
}

// Computed
const progressPercentage = computed(() => Math.round(currentProgress.value))
const progressStatus = computed(() => {
  if (currentStatus.value === TaskStatus.COMPLETED) return 'success'
  if (currentStatus.value === TaskStatus.FAILED) return 'exception'
  return undefined
})
const progressText = computed(() => {
  if (currentStatus.value === TaskStatus.PENDING) return '排队中...'
  if (currentStatus.value === TaskStatus.RUNNING) return '运行中...'
  if (currentStatus.value === TaskStatus.COMPLETED) return '已完成'
  if (currentStatus.value === TaskStatus.FAILED) return '失败'
  return ''
})
</script>

<style scoped lang="scss">
.unified-backtest-view {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .header-left {
      .page-title {
        font-size: 28px;
        font-weight: 600;
        color: #303133;
        margin: 0 0 8px 0;
      }

      .page-subtitle {
        font-size: 14px;
        color: #909399;
        margin: 0;
      }
    }
  }

  .result-tabs {
    :deep(.el-tabs__content) {
      padding-top: 16px;
    }

    .result-container {
      min-height: 600px;
    }

    .compare-container {
      .compare-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid #ebeef5;

        h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
        }
      }
    }
  }

  .progress-dialog {
    .task-info {
      margin-bottom: 24px;

      .info-item {
        display: flex;
        margin-bottom: 12px;

        .label {
          font-weight: 600;
          margin-right: 8px;
          color: #606266;
        }

        .value {
          color: #303133;
        }
      }
    }

    .progress-text {
      font-size: 14px;
      color: #606266;
    }

    .progress-steps {
      margin-top: 24px;
    }
  }
}
</style>
