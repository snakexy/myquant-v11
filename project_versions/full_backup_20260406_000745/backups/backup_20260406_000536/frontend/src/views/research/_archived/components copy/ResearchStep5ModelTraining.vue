<template>
  <div class="step-model-training-panel">
    <!-- 模型配置 -->
    <div class="config-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
        {{ isZh ? '模型配置' : 'Model Configuration' }}
      </h3>

      <div class="config-form">
        <div class="form-group">
          <label class="form-label">{{ isZh ? '模型类型' : 'Model Type' }}</label>
          <el-select v-model="modelConfig.type" style="width: 100%;" @change="onModelTypeChange">
            <el-option :label="isZh ? '线性回归' : 'Linear Regression'" value="linear"></el-option>
            <el-option :label="isZh ? '随机森林' : 'Random Forest'" value="rf"></el-option>
            <el-option :label="isZh ? 'LightGBM' : 'LightGBM'" value="lgbm"></el-option>
            <el-option :label="isZh ? 'XGBoost' : 'XGBoost'" value="xgb"></el-option>
            <el-option :label="isZh ? '神经网络' : 'Neural Network'" value="nn"></el-option>
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '训练目标' : 'Training Target' }}</label>
          <el-select v-model="modelConfig.target" style="width: 100%;">
            <el-option :label="isZh ? '未来1天收益' : 'Return 1D'" value="return_1d"></el-option>
            <el-option :label="isZh ? '未来5天收益' : 'Return 5D'" value="return_5d"></el-option>
            <el-option :label="isZh ? '未来20天收益' : 'Return 20D'" value="return_20d"></el-option>
            <el-option :label="isZh ? '超额收益' : 'Excess Return'" value="excess_return"></el-option>
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '训练集比例' : 'Train Ratio' }}</label>
          <el-slider
            v-model="modelConfig.trainRatio"
            :min="0.5"
            :max="0.8"
            :step="0.05"
            :format-tooltip="formatRatio"
          />
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '验证集比例' : 'Validation Ratio' }}</label>
          <el-slider
            v-model="modelConfig.valRatio"
            :min="0.1"
            :max="0.3"
            :step="0.05"
            :format-tooltip="formatRatio"
          />
        </div>
      </div>

      <!-- 高级参数 -->
      <div class="advanced-params">
        <el-collapse v-model="advancedParamsExpanded">
          <el-collapse-item :title="isZh ? '高级参数' : 'Advanced Parameters'" name="advanced">
            <div class="params-grid">
              <div class="param-item">
                <label class="param-label">n_estimators</label>
                <el-input-number v-model="modelConfig.params.n_estimators" :min="10" :max="1000" />
              </div>
              <div class="param-item">
                <label class="param-label">max_depth</label>
                <el-input-number v-model="modelConfig.params.max_depth" :min="1" :max="20" />
              </div>
              <div class="param-item">
                <label class="param-label">learning_rate</label>
                <el-input-number v-model="modelConfig.params.learning_rate" :min="0.001" :max="1" :step="0.01" :precision="3" />
              </div>
              <div class="param-item">
                <label class="param-label">subsample</label>
                <el-input-number v-model="modelConfig.params.subsample" :min="0.1" :max="1" :step="0.1" :precision="1" />
              </div>
              <div class="param-item">
                <label class="param-label">colsample_bytree</label>
                <el-input-number v-model="modelConfig.params.colsample_bytree" :min="0.1" :max="1" :step="0.1" :precision="1" />
              </div>
              <div class="param-item">
                <label class="param-label">reg_alpha</label>
                <el-input-number v-model="modelConfig.params.reg_alpha" :min="0" :max="10" :step="0.1" :precision="1" />
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <!-- 训练任务 -->
    <div class="tasks-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
        {{ isZh ? '训练任务' : 'Training Tasks' }}
      </h3>

      <div v-if="trainingTasks.length === 0" class="tasks-placeholder">
        <div class="placeholder-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
            <line x1="8" y1="21" x2="16" y2="21"></line>
            <line x1="12" y1="17" x2="12" y2="21"></line>
          </svg>
        </div>
        <p>{{ isZh ? '暂无训练任务' : 'No training tasks' }}</p>
      </div>

      <div v-else class="task-list">
        <div
          v-for="task in trainingTasks"
          :key="task.taskId"
          :class="['task-item', task.status]"
        >
          <div class="task-header">
            <div class="task-name">{{ task.modelType }} - {{ task.target }}</div>
            <div :class="['task-status', task.status]">
              {{ getTaskStatusText(task.status) }}
            </div>
          </div>

          <div v-if="task.status === 'running'" class="task-progress">
            <el-progress
              :percentage="Math.round(task.progress)"
              :status="task.status === 'completed' ? 'success' : undefined"
            />
          </div>

          <div class="task-meta">
            <span class="meta-item">
              <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              {{ task.createdAt }}
            </span>
            <span class="meta-item">
              <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
              </svg>
              {{ task.iterations || '-' }}
            </span>
          </div>

          <div class="task-actions">
            <el-button
              v-if="task.status === 'completed'"
              size="small"
              type="primary"
              @click="viewTaskResult(task)"
            >
              {{ isZh ? '查看结果' : 'View Result' }}
            </el-button>
            <el-button
              v-if="task.status === 'failed'"
              size="small"
              type="danger"
              @click="retryTask(task)"
            >
              {{ isZh ? '重试' : 'Retry' }}
            </el-button>
            <el-button
              v-if="task.status === 'running'"
              size="small"
              type="warning"
              @click="stopTask(task)"
            >
              {{ isZh ? '停止' : 'Stop' }}
            </el-button>
            <el-button
              size="small"
              type="info"
              @click="deleteTask(task)"
            >
              {{ isZh ? '删除' : 'Delete' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 训练结果 -->
    <div v-if="currentTaskResult" class="result-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        {{ isZh ? '训练结果' : 'Training Result' }}: {{ currentTaskResult.modelType }}
      </h3>

      <div class="result-metrics">
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '训练集IC' : 'Train IC' }}:</span>
          <span class="metric-value" :class="getICClass(currentTaskResult.trainIC)">
            {{ currentTaskResult.trainIC?.toFixed(4) || '-' }}
          </span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '验证集IC' : 'Validation IC' }}:</span>
          <span class="metric-value" :class="getICClass(currentTaskResult.valIC)">
            {{ currentTaskResult.valIC?.toFixed(4) || '-' }}
          </span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '训练集IR' : 'Train IR' }}:</span>
          <span class="metric-value" :class="getIRClass(currentTaskResult.trainIR)">
            {{ currentTaskResult.trainIR?.toFixed(4) || '-' }}
          </span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '验证集IR' : 'Validation IR' }}:</span>
          <span class="metric-value" :class="getIRClass(currentTaskResult.valIR)">
            {{ currentTaskResult.valIR?.toFixed(4) || '-' }}
          </span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '训练轮数' : 'Iterations' }}:</span>
          <span class="metric-value">{{ currentTaskResult.iterations }}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '训练时间' : 'Training Time' }}:</span>
          <span class="metric-value">{{ currentTaskResult.trainingTime }}</span>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <button class="btn btn-primary" @click="startTraining" :disabled="isTraining">
        {{ isTraining ? (isZh ? '训练中...' : 'Training...') : (isZh ? '开始训练' : 'Start Training') }}
      </button>
      <button class="btn btn-success" @click="completeStep" :disabled="!hasCompletedTask">
        {{ isZh ? '完成当前步骤' : 'Complete Step' }} ✓
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/core/AppStore'

interface Props {
  taskId: string
  isZh: boolean
  currentStep: number
}

interface Emits {
  stepComplete: [data: any]
  dataUpdate: [data: any]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// 模型配置
const modelConfig = reactive({
  type: 'lgbm',
  target: 'return_5d',
  trainRatio: 0.7,
  valRatio: 0.15,
  params: {
    n_estimators: 100,
    max_depth: 6,
    learning_rate: 0.1,
    subsample: 0.8,
    colsample_bytree: 0.8,
    reg_alpha: 0.1
  }
})

const advancedParamsExpanded = ref([])

// 训练任务
interface TrainingTask {
  taskId: string
  modelType: string
  target: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  createdAt: string
  iterations?: number
}

const trainingTasks = ref<TrainingTask[]>([])

// 训练结果
interface TrainingResult {
  taskId: string
  modelType: string
  trainIC: number
  valIC: number
  trainIR: number
  valIR: number
  iterations: number
  trainingTime: string
}

const currentTaskResult = ref<TrainingResult | null>(null)
const isTraining = ref(false)

const hasCompletedTask = computed(() => {
  return trainingTasks.value.some(t => t.status === 'completed')
})

// 格式化比例
const formatRatio = (value: number) => {
  return `${(value * 100).toFixed(0)}%`
}

// 获取任务状态文本
const getTaskStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: isZh.value ? '待处理' : 'Pending',
    running: isZh.value ? '训练中' : 'Training',
    completed: isZh.value ? '已完成' : 'Completed',
    failed: isZh.value ? '失败' : 'Failed'
  }
  return map[status] || status
}

// 获取样式类
const getICClass = (ic: number | undefined) => {
  if (!ic) return ''
  if (ic >= 0.05) return 'excellent'
  if (ic >= 0.03) return 'good'
  if (ic >= 0) return 'average'
  return 'poor'
}

const getIRClass = (ir: number | undefined) => {
  if (!ir) return ''
  if (ir >= 1.0) return 'excellent'
  if (ir >= 0.5) return 'good'
  if (ir >= 0) return 'average'
  return 'poor'
}

// 模型类型变化
const onModelTypeChange = () => {
  emit('dataUpdate', { modelType: modelConfig.type })
}

// 开始训练
const startTraining = async () => {
  isTraining.value = true

  const newTask: TrainingTask = {
    taskId: `train_${Date.now()}`,
    modelType: getModelTypeName(modelConfig.type),
    target: getTargetName(modelConfig.target),
    status: 'running',
    progress: 0,
    createdAt: new Date().toLocaleString()
  }

  trainingTasks.value.unshift(newTask)

  try {
    // 模拟训练过程
    for (let i = 0; i <= 100; i += 5) {
      newTask.progress = i
      newTask.iterations = Math.round(i * modelConfig.params.n_estimators / 100)
      await new Promise(resolve => setTimeout(resolve, 200))
    }

    newTask.status = 'completed'
    newTask.progress = 100

    // 生成训练结果
    currentTaskResult.value = {
      taskId: newTask.taskId,
      modelType: newTask.modelType,
      trainIC: 0.0678 + Math.random() * 0.02,
      valIC: 0.0456 + Math.random() * 0.02,
      trainIR: 0.89 + Math.random() * 0.2,
      valIR: 0.72 + Math.random() * 0.2,
      iterations: modelConfig.params.n_estimators,
      trainingTime: `${(Math.random() * 60 + 30).toFixed(1)}s`
    }

    ElMessage.success(isZh.value ? '训练完成' : 'Training completed')
    emit('dataUpdate', { task: newTask, result: currentTaskResult.value })
  } catch (error) {
    console.error('Training failed:', error)
    newTask.status = 'failed'
    ElMessage.error(isZh.value ? '训练失败' : 'Training failed')
  } finally {
    isTraining.value = false
  }
}

// 获取模型类型名称
const getModelTypeName = (type: string) => {
  const names: Record<string, string> = {
    linear: 'Linear Regression',
    rf: 'Random Forest',
    lgbm: 'LightGBM',
    xgb: 'XGBoost',
    nn: 'Neural Network'
  }
  return names[type] || type
}

// 获取目标名称
const getTargetName = (target: string) => {
  const names: Record<string, string> = {
    return_1d: 'Return 1D',
    return_5d: 'Return 5D',
    return_20d: 'Return 20D',
    excess_return: 'Excess Return'
  }
  return names[target] || target
}

// 查看任务结果
const viewTaskResult = (task: TrainingTask) => {
  currentTaskResult.value = {
    taskId: task.taskId,
    modelType: task.modelType,
    trainIC: 0.0678,
    valIC: 0.0456,
    trainIR: 0.89,
    valIR: 0.72,
    iterations: task.iterations || 100,
    trainingTime: '45.2s'
  }
}

// 重试任务
const retryTask = (task: TrainingTask) => {
  task.status = 'pending'
  task.progress = 0
  setTimeout(() => {
    task.status = 'running'
    startTraining()
  }, 1000)
}

// 停止任务
const stopTask = (task: TrainingTask) => {
  task.status = 'failed'
  ElMessage.info(isZh.value ? '任务已停止' : 'Task stopped')
}

// 删除任务
const deleteTask = (task: TrainingTask) => {
  const index = trainingTasks.value.indexOf(task)
  if (index > -1) {
    trainingTasks.value.splice(index, 1)
    if (currentTaskResult.value?.taskId === task.taskId) {
      currentTaskResult.value = null
    }
  }
}

// 完成步骤
const completeStep = () => {
  emit('stepComplete', { step: 5, modelResult: currentTaskResult.value })
}
</script>

<style scoped lang="scss">
.step-model-training-panel {
  width: 100%;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.icon-sm,
.icon-xs {
  width: 16px;
  height: 16px;
}

.config-section,
.tasks-section,
.result-section {
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  padding: 16px;
  margin-bottom: 20px;
}

.config-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.advanced-params {
  .params-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 12px;
  }

  .param-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .param-label {
    font-size: 11px;
    color: var(--text-secondary);
  }
}

.tasks-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--text-secondary);

  .placeholder-icon {
    width: 48px;
    height: 48px;
    opacity: 0.5;
  }

  p {
    font-size: 13px;
    margin: 0;
  }
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);

  &.running {
    border-color: var(--accent-blue);
  }

  &.completed {
    border-color: var(--accent-green);
  }

  &.failed {
    border-color: var(--accent-red);
  }
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.task-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;

  &.running {
    background: rgba(41, 98, 255, 0.2);
    color: var(--accent-blue);
  }

  &.completed {
    background: rgba(38, 166, 154, 0.2);
    color: var(--accent-green);
  }

  &.failed {
    background: rgba(239, 83, 80, 0.2);
    color: var(--accent-red);
  }
}

.task-progress {
  margin-bottom: 8px;
}

.task-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-secondary);
}

.task-actions {
  display: flex;
  gap: 8px;
}

.result-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
}

.metric-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);

  &.excellent {
    color: var(--accent-blue);
  }

  &.good {
    color: var(--accent-green);
  }

  &.average {
    color: var(--accent-orange);
  }

  &.poor {
    color: var(--accent-red);
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2952cc;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-success {
  background: var(--accent-green);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #229a8f;
}

.btn-success:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
