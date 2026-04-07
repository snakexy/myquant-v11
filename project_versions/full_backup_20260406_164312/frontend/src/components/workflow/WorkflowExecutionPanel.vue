<template>
  <div class="workflow-execution-panel">
    <!-- 执行控制栏 -->
    <div class="execution-controls">
      <div class="control-left">
        <h3 class="panel-title">工作流执行</h3>
        <span v-if="executionState" class="execution-status" :class="`status-${executionState.status}`">
          {{ getStatusText(executionState.status) }}
        </span>
      </div>

      <div class="control-right">
        <button
          v-if="!executionState || executionState.status === 'idle' || executionState.status === 'completed' || executionState.status === 'failed'"
          class="btn-execute"
          @click="startExecution"
          :disabled="!canExecute"
        >
          <Icon name="play" />
          执行工作流
        </button>

        <button
          v-if="executionState?.status === 'running'"
          class="btn-pause"
          @click="pauseExecution"
        >
          <Icon name="pause" />
          暂停
        </button>

        <button
          v-if="executionState?.status === 'paused'"
          class="btn-resume"
          @click="resumeExecution"
        >
          <Icon name="play" />
          继续
        </button>

        <button
          v-if="executionState?.status === 'running' || executionState?.status === 'paused'"
          class="btn-stop"
          @click="stopExecution"
        >
          <Icon name="stop" />
          停止
        </button>

        <button
          v-if="executionState?.status === 'completed'"
          class="btn-export"
          @click="exportResults"
        >
          <Icon name="download" />
          导出结果
        </button>
      </div>
    </div>

    <!-- 执行进度 -->
    <div v-if="executionState && (executionState.status === 'running' || executionState.status === 'paused')" class="execution-progress">
      <div class="progress-header">
        <span class="progress-step" v-if="executionState.currentStep">
          当前步骤: {{ executionState.currentStep }}
        </span>
        <span class="progress-percent">{{ executionState.progress }}%</span>
      </div>
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: `${executionState.progress}%` }"
        ></div>
      </div>
      <div v-if="executionState.startTime" class="progress-time">
        已耗时: {{ formatDuration(Date.now() - executionState.startTime) }}
      </div>
    </div>

    <!-- 执行日志 -->
    <div v-if="executionLogs.length > 0" class="execution-logs">
      <div class="logs-header">
        <h4>执行日志</h4>
        <button class="btn-clear-logs" @click="clearLogs">
          <Icon name="trash" />
          清空
        </button>
      </div>
      <div class="logs-container" ref="logsContainer">
        <div
          v-for="log in executionLogs"
          :key="log.timestamp"
          class="log-item"
          :class="`log-${log.level}`"
        >
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span v-if="log.nodeId" class="log-node">{{ log.nodeId }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>

    <!-- 执行结果 -->
    <div v-if="executionState?.status === 'completed'" class="execution-results">
      <h4>执行结果</h4>
      <div class="results-grid">
        <div
          v-for="(result, nodeId) in executionState.results"
          :key="nodeId"
          class="result-item"
        >
          <div class="result-header">
            <span class="result-node">{{ getNodeName(nodeId) }}</span>
            <span class="result-success">
              <Icon name="check-circle" />
            </span>
          </div>
          <div class="result-preview">
            {{ getResultPreview(result) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 错误信息 -->
    <div v-if="executionState?.errors.length > 0" class="execution-errors">
      <h4>错误信息</h4>
      <div class="errors-list">
        <div
          v-for="error in executionState.errors"
          :key="error.timestamp"
          class="error-item"
        >
          <span class="error-node">{{ getNodeName(error.nodeId) }}</span>
          <span class="error-message">{{ error.error }}</span>
          <span class="error-time">{{ formatTime(error.timestamp) }}</span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!executionState" class="empty-state">
      <Icon name="play-circle" class="empty-icon" />
      <p>点击"执行工作流"开始分析</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { workflowEngine, type WorkflowExecutionState } from '../../utils/workflowEngine'
import type { Node, Connection } from '../../views/NodeWorkflow.vue'

interface Props {
  nodes: Node[]
  connections: Connection[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'execution-completed': [results: Record<string, any>]
}>()

// 状态
const executionState = ref<WorkflowExecutionState | null>(null)
const executionLogs = ref<any[]>([])
const logsContainer = ref<HTMLElement>()

// 计算属性
const canExecute = computed(() => {
  return props.nodes.length > 0
})

// 监听执行状态变化
watch(() => workflowEngine.getExecutionState(), (newState) => {
  if (newState) {
    executionState.value = newState
    executionLogs.value = [...newState.logs]

    // 自动滚动到底部
    nextTick(() => {
      if (logsContainer.value) {
        logsContainer.value.scrollTop = logsContainer.value.scrollHeight
      }
    })

    // 当执行完成时，发送结果给父组件
    if (newState.status === 'completed' && newState.results) {
      console.log('[WorkflowExecutionPanel] 执行完成，发送结果给父组件:', newState.results)
      emit('execution-completed', newState.results)
    }
  }
}, { immediate: true })

// 获取状态文本
const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    'idle': '未开始',
    'running': '运行中',
    'paused': '已暂停',
    'completed': '已完成',
    'failed': '执行失败'
  }
  return statusMap[status] || status
}

// 格式化时间
const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 格式化持续时间
const formatDuration = (ms: number): string => {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (hours > 0) {
    return `${hours}小时${minutes % 60}分${seconds % 60}秒`
  } else if (minutes > 0) {
    return `${minutes}分${seconds % 60}秒`
  } else {
    return `${seconds}秒`
  }
}

// 获取节点名称
const getNodeName = (nodeId: string): string => {
  const node = props.nodes.find(n => n.id === nodeId)
  return node?.title || nodeId
}

// 获取结果预览
const getResultPreview = (result: any): string => {
  if (!result) return '无结果'

  if (typeof result === 'string') {
    return result.length > 50 ? result.substring(0, 50) + '...' : result
  }

  if (Array.isArray(result)) {
    return `数组 (${result.length} 项)`
  }

  if (typeof result === 'object') {
    const keys = Object.keys(result)
    return `对象 (${keys.length} 个属性: ${keys.slice(0, 3).join(', ')}${keys.length > 3 ? '...' : ''})`
  }

  return String(result)
}

// 开始执行
const startExecution = async () => {
  try {
    const state = await workflowEngine.executeWorkflow(
      props.nodes,
      props.connections,
      (state) => {
        // 进度回调
        executionState.value = state
      },
      (log) => {
        // 日志回调
        executionLogs.value.push(log)
      }
    )

    executionState.value = state
  } catch (error: any) {
    console.error('执行工作流失败:', error)
  }
}

// 暂停执行
const pauseExecution = () => {
  workflowEngine.pause()
}

// 恢复执行
const resumeExecution = () => {
  workflowEngine.resume()
}

// 停止执行
const stopExecution = () => {
  workflowEngine.stop()
}

// 导出结果
const exportResults = () => {
  if (!executionState.value) return

  const exportData = {
    executionId: executionState.value.id,
    startTime: executionState.value.startTime,
    endTime: executionState.value.endTime,
    status: executionState.value.status,
    progress: executionState.value.progress,
    results: executionState.value.results,
    logs: executionState.value.logs,
    errors: executionState.value.errors
  }

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `workflow-results-${executionState.value.id}.json`
  a.click()
  URL.revokeObjectURL(url)
}

// 清空日志
const clearLogs = () => {
  executionLogs.value = []
}
</script>

<style lang="scss" scoped>
.workflow-execution-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--bg-color-secondary);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color-base);
}

// 控制栏
.execution-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: var(--spacing-3);
  border-bottom: 1px solid var(--border-color-base);
}

.control-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.panel-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.execution-status {
  padding: 2px 8px;
  border-radius: var(--border-radius-base);
  font-size: var(--font-size-sm);
  font-weight: 500;

  &.status-idle {
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-secondary);
  }

  &.status-running {
    background: rgba(59, 130, 246, 0.2);
    color: #3b82f6;
  }

  &.status-paused {
    background: rgba(251, 191, 36, 0.2);
    color: #fbbf24;
  }

  &.status-completed {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
  }

  &.status-failed {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }
}

.control-right {
  display: flex;
  gap: var(--spacing-2);
}

// 按钮样式
.btn-execute,
.btn-pause,
.btn-resume,
.btn-stop,
.btn-export,
.btn-clear-logs {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-2) var(--spacing-3);
  border: none;
  border-radius: var(--border-radius-base);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-execute {
  background: var(--primary-color);
  color: white;

  &:hover:not(:disabled) {
    background: var(--primary-color-dark);
  }
}

.btn-pause {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;

  &:hover {
    background: rgba(251, 191, 36, 0.3);
  }
}

.btn-resume {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;

  &:hover {
    background: rgba(34, 197, 94, 0.3);
  }
}

.btn-stop {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;

  &:hover {
    background: rgba(239, 68, 68, 0.3);
  }
}

.btn-export {
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;

  &:hover {
    background: rgba(139, 92, 246, 0.3);
  }
}

.btn-clear-logs {
  background: transparent;
  color: var(--text-secondary);
  padding: var(--spacing-1);

  &:hover {
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.1);
  }
}

// 进度条
.execution-progress {
  padding: var(--spacing-3);
  background: var(--bg-color-base);
  border-radius: var(--border-radius-base);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2);
}

.progress-step {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.progress-percent {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--primary-color);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-time {
  margin-top: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  text-align: right;
}

// 日志
.execution-logs {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h4 {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }
}

.logs-container {
  max-height: 300px;
  overflow-y: auto;
  background: var(--bg-color-base);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-2);

  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
  }
}

.log-item {
  display: flex;
  gap: var(--spacing-2);
  padding: 4px 0;
  font-size: var(--font-size-sm);
  line-height: 1.4;

  &:not(:last-child) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 8px;
    margin-bottom: 4px;
  }

  .log-time {
    color: var(--text-secondary);
    font-family: monospace;
    min-width: 60px;
  }

  .log-node {
    color: var(--primary-color);
    min-width: 100px;
    font-weight: 500;
  }

  .log-message {
    color: var(--text-primary);
    flex: 1;
  }

  &.log-error {
    .log-message {
      color: #ef4444;
    }
  }

  &.log-warning {
    .log-message {
      color: #fbbf24;
    }
  }

  &.log-success {
    .log-message {
      color: #22c55e;
    }
  }
}

// 结果
.execution-results {
  h4 {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--spacing-3);
  }

  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-3);
  }

  .result-item {
    padding: var(--spacing-3);
    background: var(--bg-color-base);
    border-radius: var(--border-radius-base);
    border: 1px solid rgba(34, 197, 94, 0.2);
  }

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-2);
  }

  .result-node {
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: var(--text-primary);
  }

  .result-success {
    color: #22c55e;
  }

  .result-preview {
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
    font-family: monospace;
    word-break: break-all;
  }
}

// 错误
.execution-errors {
  h4 {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--spacing-3);
  }

  .errors-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2);
  }

  .error-item {
    display: flex;
    gap: var(--spacing-2);
    padding: var(--spacing-2);
    background: rgba(239, 68, 68, 0.1);
    border-radius: var(--border-radius-base);
    border: 1px solid rgba(239, 68, 68, 0.2);
  }

  .error-node {
    min-width: 100px;
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: #ef4444;
  }

  .error-message {
    flex: 1;
    font-size: var(--font-size-sm);
    color: var(--text-primary);
  }

  .error-time {
    font-size: var(--font-size-xs);
    color: var(--text-secondary);
    font-family: monospace;
  }
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-8);
  text-align: center;

  .empty-icon {
    font-size: 48px;
    color: var(--text-disabled);
    margin-bottom: var(--spacing-3);
  }

  p {
    font-size: var(--font-size-base);
    color: var(--text-secondary);
    margin: 0;
  }
}
</style>