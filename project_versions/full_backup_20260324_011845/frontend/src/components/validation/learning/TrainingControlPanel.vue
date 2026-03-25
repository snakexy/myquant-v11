<template>
  <el-card class="training-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">📚 训练控制</span>
      </div>
    </template>

    <!-- 模型选择 -->
    <div class="model-selection">
      <el-form-item label="选择模型">
        <el-select
          v-model="selectedModel"
          placeholder="请选择模型"
          @change="handleModelChange"
        >
          <el-option
            v-for="model in models"
            :key="model.id"
            :label="model.name"
            :value="model.id"
          />
        </el-select>
      </el-form-item>
    </div>

    <!-- 当前模型信息 -->
    <div class="model-info">
      <div class="info-item">
        <span class="label">当前模型</span>
        <span class="value">{{ currentModelInfo.name }}</span>
      </div>
      <div class="info-item">
        <span class="label">训练状态</span>
        <el-tag :type="trainingStatusType" size="small">
          {{ trainingStatusText }}
        </el-tag>
      </div>
    </div>

    <!-- 训练进度 -->
    <div v-if="trainingStatus !== 'idle'" class="training-progress">
      <div class="progress-header">
        <span class="label">训练进度</span>
        <span class="percentage">{{ trainingProgress }}%</span>
      </div>
      <el-progress :percentage="trainingProgress" :status="progressStatus" />
      <div class="progress-details">
        <span>已训练: {{ trainedEpochs }}/{{ totalEpochs }} 轮</span>
        <span>剩余时间: {{ estimatedTime }}</span>
      </div>
    </div>

    <el-divider />

    <!-- 训练按钮 -->
    <div class="training-buttons">
      <el-button
        type="primary"
        size="large"
        block
        :loading="loading"
        :disabled="trainingStatus === 'running'"
        @click="handleStartTraining"
      >
        <el-icon><VideoPlay /></el-icon>
        启动在线训练
      </el-button>
      <el-button
        size="large"
        block
        :disabled="trainingStatus === 'idle' || trainingStatus === 'completed'"
        @click="handlePauseTraining"
      >
        <el-icon><VideoPause /></el-icon>
        暂停训练
      </el-button>
      <el-button
        size="large"
        block
        @click="handleStopTraining"
      >
        <el-icon><CircleClose /></el-icon>
        停止训练
      </el-button>
    </div>

    <!-- 定时调度配置 ⭐ 新增 -->
    <el-divider />

    <div class="schedule-config">
      <h4>
        <el-icon><Clock /></el-icon>
        定时调度
      </h4>

      <!-- 调度状态 -->
      <div v-if="scheduleStatus.scheduled" class="schedule-status">
        <el-alert
          :type="scheduleStatus.enabled ? 'success' : 'info'"
          :closable="false"
          show-icon
        >
          <template #title>
            <div v-if="scheduleStatus.enabled">
              <span>定时调度运行中：每天 {{ scheduleStatus.schedule_time }}</span>
              <el-button
                type="danger"
                size="small"
                text
                @click="handleStopSchedule"
                style="margin-left: 12px"
              >
                停止调度
              </el-button>
            </div>
            <span v-else>调度已停止</span>
          </template>
        </el-alert>
      </div>

      <!-- 调度配置表单 -->
      <div v-if="!scheduleStatus.scheduled || !scheduleStatus.enabled" class="schedule-form">
        <div class="param-item">
          <span class="param-label">训练时间</span>
          <el-time-picker
            v-model="scheduleTime"
            placeholder="选择训练时间"
            format="HH:mm"
            value-format="HH:mm"
            :clearable="false"
          />
        </div>

        <el-button
          type="success"
          size="default"
          block
          :loading="scheduleLoading"
          @click="handleStartSchedule"
        >
          <el-icon><AlarmClock /></el-icon>
          启动定时训练
        </el-button>
      </div>

      <!-- 手动触发更新 -->
      <div class="manual-trigger" style="margin-top: 12px">
        <el-button
          type="primary"
          size="default"
          block
          plain
          :loading="routineLoading"
          @click="handleManualRoutine"
        >
          <el-icon><Refresh /></el-icon>
          手动触发例行更新
        </el-button>
      </div>
    </div>

    <!-- 训练参数 -->
    <el-divider />

    <div class="training-params">
      <h4>训练参数</h4>
      <div class="param-item">
        <span class="param-label">训练窗口</span>
        <el-input-number
          v-model="trainingParams.trainingWindow"
          :min="100"
          :max="1000"
          :step="10"
          size="small"
        />
      </div>
      <div class="param-item">
        <span class="param-label">滚动周期</span>
        <el-input-number
          v-model="trainingParams.rebalanceFrequency"
          :min="5"
          :max="50"
          :step="1"
          size="small"
        />
      </div>
      <div class="param-item">
        <span class="param-label">最小收益率</span>
        <el-input-number
          v-model="trainingParams.minReturnRate"
          :min="0"
          :max="20"
          :step="0.5"
          :precision="1"
          size="small"
        />
        <span class="unit">%</span>
      </div>

      <el-button
        type="primary"
        size="small"
        plain
        style="width: 100%; margin-top: 12px"
        @click="handleUpdateParams"
      >
        更新参数
      </el-button>
    </div>

    <!-- 训练历史 -->
    <el-divider />

    <div class="training-history">
      <h4>训练历史</h4>
      <el-timeline>
        <el-timeline-item
          v-for="record in trainingHistory"
          :key="record.id"
          :timestamp="record.time"
          :type="record.type"
        >
          {{ record.message }}
        </el-timeline-item>
      </el-timeline>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, VideoPause, CircleClose, Clock, AlarmClock, Refresh } from '@element-plus/icons-vue'
import { learningApi } from '@/api/modules/learning'
import type { Model, TrainingParams, TrainingHistory } from '@/api/modules/training'

// 模型列表
const models = ref<Model[]>([])

// 选中的模型
const selectedModel = ref<string>('')

// 当前模型信息
const currentModelInfo = reactive({
  id: '',
  name: '',
  version: ''
})

// 训练状态
const trainingStatus = ref<'idle' | 'running' | 'paused' | 'completed'>('idle')
const loading = ref(false)

// 训练进度
const trainingProgress = ref(0)
const trainedEpochs = ref(0)
const totalEpochs = ref(100)
const estimatedTime = ref('计算中...')

// 训练参数
const trainingParams = reactive<TrainingParams>({
  trainingWindow: 252,
  rebalanceFrequency: 21,
  minReturnRate: 5.0
})

// 训练历史
const trainingHistory = ref<any[]>([])

// 进度更新定时器
let progressInterval: number | null = null

// 计算训练状态文本
const trainingStatusText = computed(() => {
  const statusMap = {
    idle: '空闲',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成'
  }
  return statusMap[trainingStatus.value]
})

// 计算训练状态标签类型
const trainingStatusType = computed(() => {
  const typeMap = {
    idle: 'info',
    running: 'success',
    paused: 'warning',
    completed: 'success'
  }
  return typeMap[trainingStatus.value] as any
})

// 计算进度条状态
const progressStatus = computed(() => {
  if (trainingStatus.value === 'completed') return 'success'
  if (trainingStatus.value === 'running') return undefined
  return 'exception'
})

// ⭐ 新增：调度相关状态
const scheduleTime = ref('15:00')  // 默认15:00
const scheduleLoading = ref(false)
const routineLoading = ref(false)
const scheduleStatus = reactive<{
  scheduled: boolean
  enabled: boolean
  schedule_time: string
  is_running: boolean
}>({
  scheduled: false,
  enabled: false,
  schedule_time: '',
  is_running: false
})

// 加载模型列表（使用默认列表，暂不支持从API获取）
const loadModels = async () => {
  // 降级方案：使用默认模型列表
  models.value = [
    { id: 'model_topk_dropout_v2', name: 'TopkDropout-v2.3.1', version: 'v2.3.1', type: 'topk_dropout', status: 'idle' },
    { id: 'model_lstm_v1', name: 'LSTM-v1.5.0', version: 'v1.5.0', type: 'lstm', status: 'idle' },
    { id: 'model_transformer_v3', name: 'Transformer-v3.0.0', version: 'v3.0.0', type: 'transformer', status: 'idle' },
    { id: 'model_gru_v2', name: 'GRU-v2.1.0', version: 'v2.1.0', type: 'gru', status: 'idle' }
  ]
  if (!selectedModel.value) {
    selectedModel.value = models.value[0].id
    currentModelInfo.id = models.value[0].id
    currentModelInfo.name = models.value[0].name
    currentModelInfo.version = models.value[0].version
  }
}

// 加载训练状态
const loadTrainingStatus = async () => {
  try {
    // 尝试获取当前选中模型的训练进度
    if (selectedModel.value) {
      const response = await learningApi.getTrainingProgress(selectedModel.value)
      if (response.code === 200 || response.success || response.data) {
        const data = response.data
        trainingStatus.value = data.is_training ? 'running' : 'idle'
        trainingProgress.value = data.progress || 0
        trainedEpochs.value = data.current_epoch || 0
        totalEpochs.value = data.total_epochs || 100
        if (data.estimated_end_time) {
          estimatedTime.value = formatTime(data.estimated_end_time - Date.now() / 1000)
        }
      }
    }
  } catch (error) {
    console.error('加载训练状态失败:', error)
    // 降级方案：保持默认状态
    trainingStatus.value = 'idle'
  }
}

// 加载训练参数（使用默认参数）
const loadTrainingParams = async () => {
  // 使用默认参数，暂不支持从API获取
  // trainingParams 已在定义时设置默认值
}

// 加载训练历史（使用默认历史记录）
const loadTrainingHistory = async () => {
  // 降级方案：使用默认历史记录
  trainingHistory.value = [
    {
      id: 1,
      time: '2026-02-07 14:30',
      type: 'success',
      message: 'TopkDropout-v2.3.1 训练完成，收益率: 8.5%'
    }
  ]
}

// 格式化时间
const formatTime = (seconds: number): string => {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.ceil(seconds / 60)}分钟`
  return `${Math.ceil(seconds / 3600)}小时`
}

// 启动进度轮询
const startProgressPolling = () => {
  if (progressInterval) return

  progressInterval = window.setInterval(async () => {
    try {
      const response = await learningApi.getProgress()
      if (response.code === 200) {
        const progress = response.data
        trainingProgress.value = progress.progress
        trainedEpochs.value = progress.currentEpoch
        estimatedTime.value = formatTime(progress.remainingTime)

        // 如果训练完成，停止轮询
        if (progress.progress >= 100) {
          trainingStatus.value = 'completed'
          stopProgressPolling()
          await loadTrainingHistory() // 刷新历史记录
          ElMessage.success('训练完成！')
        }
      }
    } catch (error) {
      console.error('获取训练进度失败:', error)
    }
  }, 2000) // 每2秒轮询一次
}

// 停止进度轮询
const stopProgressPolling = () => {
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
}

// 模型切换处理
const handleModelChange = async (modelId: string) => {
  try {
    const response = await learningApi.switchModel(modelId)
    if (response.code === 200) {
      const model = models.value.find(m => m.id === modelId)
      if (model) {
        currentModelInfo.name = model.name
        currentModelInfo.id = model.id
        currentModelInfo.version = model.version
        ElMessage.success(`已切换到模型: ${model.name}`)
      }
    }
  } catch (error) {
    console.error('切换模型失败:', error)
    ElMessage.error('切换模型失败')
  }
}

// 开始训练
const handleStartTraining = async () => {
  loading.value = true
  try {
    // 使用新的OnlineManager API
    const response = await learningApi.firstTrain(selectedModel.value)
    if (response.code === 200) {
      trainingStatus.value = 'running'
      trainingProgress.value = 0
      trainedEpochs.value = 0

      ElMessage.success('在线训练已启动')

      // 启动进度轮询
      startProgressPolling()
    }
  } catch (error) {
    console.error('启动训练失败:', error)
    ElMessage.error('启动训练失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 暂停训练（暂不支持）
const handlePauseTraining = async () => {
  ElMessage.info('暂停功能暂不支持，可使用停止功能')
}

// 停止训练
const handleStopTraining = async () => {
  try {
    const response = await learningApi.stopTraining()
    if (response.code === 200) {
      trainingStatus.value = 'idle'
      trainingProgress.value = 0
      trainedEpochs.value = 0
      stopProgressPolling()
      ElMessage.warning('训练已停止')
    }
  } catch (error) {
    console.error('停止训练失败:', error)
    ElMessage.error('停止失败')
  }
}

// 更新参数（暂不支持）
const handleUpdateParams = async () => {
  ElMessage.info('参数更新功能将在后续版本中支持')
}

// ⭐ 新增：启动定时调度
const handleStartSchedule = async () => {
  scheduleLoading.value = true
  try {
    const [hour, minute] = scheduleTime.value.split(':').map(Number)

    const response = await learningApi.startSchedule(
      selectedModel.value,
      hour,
      minute
    )

    if (response.code === 200) {
      ElMessage.success(`定时调度已启动：每天 ${scheduleTime.value}`)

      // 重新加载调度状态
      await loadScheduleStatus()
    }
  } catch (error) {
    console.error('启动调度失败:', error)
    ElMessage.error('启动调度失败，请稍后重试')
  } finally {
    scheduleLoading.value = false
  }
}

// ⭐ 新增：停止调度
const handleStopSchedule = async () => {
  try {
    const response = await learningApi.stopSchedule(selectedModel.value)

    if (response.code === 200) {
      ElMessage.info('调度已停止')

      // 重新加载调度状态
      await loadScheduleStatus()
    }
  } catch (error) {
    console.error('停止调度失败:', error)
    ElMessage.error('停止调度失败')
  }
}

// ⭐ 新增：手动触发例行更新
const handleManualRoutine = async () => {
  routineLoading.value = true
  try {
    const response = await learningApi.routine(
      selectedModel.value,
      new Date().toISOString().split('T')[0]
    )

    if (response.code === 200) {
      ElMessage.success('例行更新已完成')

      // 刷新进度和信号
      await loadTrainingStatus()
      await loadScheduleStatus()

      // 通知其他组件刷新
      window.dispatchEvent(new CustomEvent('routine-completed'))
    }
  } catch (error) {
    console.error('手动触发更新失败:', error)
    ElMessage.error('触发更新失败，请稍后重试')
  } finally {
    routineLoading.value = false
  }
}

// ⭐ 新增：加载调度状态
const loadScheduleStatus = async () => {
  try {
    const response = await learningApi.getScheduleStatus(selectedModel.value)

    if (response.code === 200) {
      Object.assign(scheduleStatus, response.data)
    }
  } catch (error) {
    // 调度可能还未配置，静默失败
    console.warn('获取调度状态失败，可能尚未配置:', error)
  }
}

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([
    loadModels(),
    loadTrainingStatus(),
    loadTrainingParams(),
    loadTrainingHistory(),
    loadScheduleStatus()  // ⭐ 新增：加载调度状态
  ])

  // 如果正在训练，启动进度轮询
  if (trainingStatus.value === 'running') {
    startProgressPolling()
  }
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopProgressPolling()
})
</script>

<style scoped lang="scss">
.training-card {
  .card-header {
    .title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .model-selection {
    margin-bottom: 16px;

    :deep(.el-form-item) {
      margin-bottom: 0;
    }

    :deep(.el-select) {
      width: 100%;
    }
  }

  .model-info {
    margin-bottom: 16px;

    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      &:last-child {
        margin-bottom: 0;
      }

      .label {
        font-size: 14px;
        color: #606266;
      }

      .value {
        font-size: 14px;
        color: #303133;
        font-weight: 500;
      }
    }
  }

  .training-progress {
    margin-bottom: 16px;
    padding: 16px;
    background-color: #f9fafb;
    border-radius: 8px;

    .progress-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;

      .label {
        font-size: 13px;
        color: #606266;
        font-weight: 500;
      }

      .percentage {
        font-size: 14px;
        font-weight: 600;
        color: #409eff;
      }
    }

    .progress-details {
      display: flex;
      justify-content: space-between;
      margin-top: 12px;
      font-size: 12px;
      color: #909399;
    }
  }

  .training-buttons {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .training-params {
    h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      font-weight: 600;
      color: #606266;
    }

    .param-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;

      .param-label {
        font-size: 13px;
        color: #909399;
        flex: 1;
      }

      :deep(.el-input-number) {
        width: 120px;
      }

      .unit {
        margin-left: 8px;
        font-size: 12px;
        color: #909399;
        width: 20px;
      }
    }
  }

  .training-history {
    h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      font-weight: 600;
      color: #606266;
    }

    :deep(.el-timeline) {
      padding-left: 0;
      max-height: 200px;
      overflow-y: auto;
    }

    :deep(.el-timeline-item__timestamp) {
      font-size: 11px;
      color: #909399;
    }

    :deep(.el-timeline-item__content) {
      font-size: 12px;
    }
  }
}
</style>
