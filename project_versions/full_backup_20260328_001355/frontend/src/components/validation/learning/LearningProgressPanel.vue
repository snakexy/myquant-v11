<template>
  <el-card class="progress-panel-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">📊 训练进度监控</span>
        <div class="actions">
          <el-tag :type="trainingStatusType" size="small">
            {{ trainingStatusText }}
          </el-tag>
          <el-button size="small" @click="handleRefresh" :loading="loading">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </div>
    </template>

    <!-- 在线训练状态（新增） -->
    <div class="online-training-status" style="margin-bottom: 20px;">
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="运行状态">
          <el-tag :type="onlineManagerStatus.isRunning ? 'success' : 'info'" size="small">
            {{ onlineManagerStatus.isRunning ? '运行中' : '未启动' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="在线模型">
          <el-tag v-if="onlineManagerStatus.currentOnlineModel" type="primary" size="small">
            {{ onlineManagerStatus.currentOnlineModel }}
          </el-tag>
          <span v-else style="color: #909399; font-size: 13px;">-</span>
        </el-descriptions-item>
        <el-descriptions-item label="例行更新次数">
          <el-tag type="info" size="small">
            {{ onlineManagerStatus.totalRoutines }} 次
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 训练进度总览 -->
    <div v-if="trainingProgress" class="progress-overview">
      <div class="overview-item">
        <span class="label">训练进度</span>
        <span class="value">{{ trainingProgress.progress.toFixed(1) }}%</span>
      </div>
      <div class="overview-item">
        <span class="label">当前轮次</span>
        <span class="value">{{ trainingProgress.currentEpoch }}/{{ trainingProgress.totalEpochs }}</span>
      </div>
      <div class="overview-item">
        <span class="label">当前损失</span>
        <span class="value">{{ trainingProgress.loss.toFixed(4) }}</span>
      </div>
      <div v-if="trainingProgress.accuracy !== undefined" class="overview-item">
        <span class="label">准确率</span>
        <span class="value">{{ (trainingProgress.accuracy * 100).toFixed(2) }}%</span>
      </div>
      <div class="overview-item">
        <span class="label">预计剩余</span>
        <span class="value">{{ formatTime(estimatedTime) }}</span>
      </div>
    </div>

    <!-- 进度条 -->
    <div class="main-progress">
      <el-progress 
        :percentage="trainingProgress?.progress || 0" 
        :status="progressStatus"
        :stroke-width="20"
      />
    </div>

    <!-- 训练曲线 -->
    <div v-if="!loading && !error" ref="lossChartRef" class="chart-container" style="height: 350px; margin-top: 24px;"></div>
    <div v-if="loading" class="chart-loading">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    <div v-if="error" class="chart-error">
      <el-icon :size="32"><WarningFilled /></el-icon>
      <span>{{ error }}</span>
      <el-button size="small" @click="handleRefresh">重试</el-button>
    </div>

    <!-- 训练日志 -->
    <el-divider style="margin: 24px 0;" />

    <div class="training-logs">
      <h4>训练日志</h4>
      <div class="log-list">
        <div 
          v-for="log in trainingLogs" 
          :key="log.id" 
          class="log-item"
          :class="'log-' + log.type"
        >
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        <el-empty v-if="trainingLogs.length === 0" description="暂无训练日志" :image-size="80" />
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Loading, WarningFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { learningApi } from '@/api/modules/learning'
import type { TrainingProgress, ModelVersion } from '@/api/modules/learning'

// Props
interface Props {
  modelId?: string
  autoRefresh?: boolean
  refreshInterval?: number // 秒
}

const props = withDefaults(defineProps<Props>(), {
  modelId: 'default_model',
  autoRefresh: true,
  refreshInterval: 10
})

// Emits
const emit = defineEmits<{
  trainingComplete: [versionId: string]
  statusChange: [status: 'training' | 'completed' | 'idle']
}>()

// State
const lossChartRef = ref<HTMLDivElement>()
const lossChartInstance = ref<echarts.ECharts>()
const trainingProgress = ref<TrainingProgress | null>(null)
const trainingLogs = ref<any[]>([])
const loading = ref(false)
const error = ref('')

// OnlineManager状态（新增）
const onlineManagerStatus = ref<{
  isRunning: boolean
  currentOnlineModel: string | null
  totalRoutines: number
  lastRoutineTime: string | null
}>({
  isRunning: false,
  currentOnlineModel: null,
  totalRoutines: 0,
  lastRoutineTime: null
})

// 训练历史数据（用于绘制曲线）
const lossHistory = ref<number[]>([])
const accuracyHistory = ref<number[]>([])
const epochHistory = ref<number[]>([])

let refreshTimer: number | null = null

// 计算训练状态文本
const trainingStatusText = computed(() => {
  if (!trainingProgress.value) return '未启动'
  if (trainingProgress.value.isTraining) return '训练中'
  return '已完成'
})

// 计算训练状态标签类型
const trainingStatusType = computed(() => {
  if (!trainingProgress.value) return 'info'
  if (trainingProgress.value.isTraining) return 'success'
  return 'info'
})

// 计算进度条状态
const progressStatus = computed(() => {
  if (!trainingProgress.value) return undefined
  if (trainingProgress.value.progress >= 100) return 'success'
  return undefined
})

// 计算预计剩余时间
const estimatedTime = computed(() => {
  if (!trainingProgress.value || !trainingProgress.value.estimatedEndTime) return 0
  const endTime = new Date(trainingProgress.value.estimatedEndTime).getTime()
  const now = Date.now()
  return Math.max(0, endTime - now) / 1000 // 秒
})

// 格式化时间
const formatTime = (seconds: number): string => {
  if (seconds < 60) return `${Math.ceil(seconds)}秒`
  if (seconds < 3600) return `${Math.ceil(seconds / 60)}分钟`
  return `${Math.ceil(seconds / 3600)}小时`
}

// 初始化图表
const initCharts = () => {
  if (!lossChartRef.value) return

  lossChartInstance.value = echarts.init(lossChartRef.value)
  updateCharts()

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

// 更新图表
const updateCharts = () => {
  if (!lossChartInstance.value || lossHistory.value.length === 0) return

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['损失', '准确率'],
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: epochHistory.value,
      name: '轮次',
      axisLine: {
        lineStyle: { color: '#e4e7ed' }
      },
      axisLabel: {
        color: '#909399',
        fontSize: 12
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '损失',
        position: 'left',
        axisLine: {
          lineStyle: { color: '#e4e7ed' }
        },
        axisLabel: {
          color: '#909399',
          fontSize: 12
        },
        splitLine: {
          lineStyle: { color: '#f2f3f5', type: 'dashed' }
        }
      },
      {
        type: 'value',
        name: '准确率',
        position: 'right',
        axisLine: {
          lineStyle: { color: '#e4e7ed' }
        },
        axisLabel: {
          formatter: '{value}%',
          color: '#909399',
          fontSize: 12
        },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '损失',
        type: 'line',
        smooth: true,
        data: lossHistory.value,
        itemStyle: {
          color: '#f56c6c'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
              { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
            ]
          }
        }
      },
      {
        name: '准确率',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        data: accuracyHistory.value,
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }

  lossChartInstance.value.setOption(option)
}

// 加载训练进度
const loadTrainingProgress = async () => {
  loading.value = true
  error.value = ''

  try {
    // 获取旧的训练进度数据
    const response = await learningApi.getTrainingProgress(props.modelId)
    if (response.code === 200) {
      trainingProgress.value = response.data

      // 模拟训练历史数据（实际应该从后端获取）
      if (lossHistory.value.length === 0) {
        generateMockHistoryData()
      }

      await nextTick()
      updateCharts()

      // 检查训练是否完成
      if (response.data.progress >= 100 && response.data.isTraining === false) {
        emit('trainingComplete', props.modelId)
        emit('statusChange', 'completed')
        ElMessage.success('训练完成！')
      }
    }

    // 获取OnlineManager状态（新增）
    try {
      const progressResponse = await learningApi.getProgressV2(props.modelId)
      if (progressResponse.code === 200) {
        onlineManagerStatus.value = {
          isRunning: progressResponse.data.isRunning,
          currentOnlineModel: progressResponse.data.currentOnlineModel,
          totalRoutines: progressResponse.data.totalRoutines,
          lastRoutineTime: progressResponse.data.lastRoutineTime
        }
      }
    } catch (err) {
      console.warn('获取OnlineManager状态失败，可能尚未启动训练:', err)
      // 不显示错误，静默失败
    }

  } catch (err) {
    console.error('加载训练进度失败:', err)
    error.value = '加载失败'

    // 降级方案：使用模拟数据
    trainingProgress.value = {
      isTraining: false,
      currentEpoch: 50,
      totalEpochs: 100,
      progress: 50,
      loss: 0.3524,
      accuracy: 0.7845,
      startTime: new Date(Date.now() - 3600000).toISOString(),
      estimatedEndTime: new Date(Date.now() + 3600000).toISOString()
    }
    generateMockHistoryData()

    await nextTick()
    updateCharts()
    ElMessage.warning('使用模拟数据')
  } finally {
    loading.value = false
  }
}

// 生成模拟历史数据
const generateMockHistoryData = () => {
  const epochs = 50
  lossHistory.value = []
  accuracyHistory.value = []
  epochHistory.value = []

  let loss = 0.8
  let accuracy = 0.5

  for (let i = 0; i < epochs; i++) {
    epochHistory.value.push(i + 1)
    
    // 损失逐渐下降
    loss = loss * (1 - Math.random() * 0.05)
    loss = Math.max(0.1, loss)
    lossHistory.value.push(parseFloat(loss.toFixed(4)))
    
    // 准确率逐渐上升
    accuracy = accuracy + Math.random() * 0.02
    accuracy = Math.min(0.95, accuracy)
    accuracyHistory.value.push(parseFloat(accuracy.toFixed(4)))
  }
}

// 刷新
const handleRefresh = () => {
  loadTrainingProgress()
}

// 窗口大小变化处理
const handleResize = () => {
  lossChartInstance.value?.resize()
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (!props.autoRefresh) return

  refreshTimer = window.setInterval(() => {
    loadTrainingProgress()
  }, props.refreshInterval * 1000)
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生成模拟日志
const generateMockLogs = () => {
  trainingLogs.value = [
    { id: 1, time: '14:30:15', type: 'info', message: '开始训练: TopkDropout-v2.3.1' },
    { id: 2, time: '14:35:22', type: 'success', message: 'Epoch 10/100 - Loss: 0.5234, Accuracy: 65.23%' },
    { id: 3, time: '14:40:18', type: 'success', message: 'Epoch 20/100 - Loss: 0.4356, Accuracy: 72.45%' },
    { id: 4, time: '14:45:30', type: 'warning', message: '检测到性能波动，调整学习率' },
    { id: 5, time: '14:50:25', type: 'success', message: 'Epoch 30/100 - Loss: 0.3821, Accuracy: 78.12%' }
  ]
}

// 生命周期
onMounted(async () => {
  await nextTick()
  initCharts()
  await loadTrainingProgress()
  generateMockLogs()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  window.removeEventListener('resize', handleResize)
  lossChartInstance.value?.dispose()
})

// 暴露方法给父组件
defineExpose({
  refresh: loadTrainingProgress,
  getData: () => trainingProgress.value
})
</script>

<style scoped lang="scss">
.progress-panel-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }

    .actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .progress-overview {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    padding: 16px;
    margin-bottom: 20px;
    background-color: #f9fafb;
    border-radius: 8px;

    .overview-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;

      .label {
        font-size: 12px;
        color: #909399;
        text-align: center;
      }

      .value {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
        font-family: 'Consolas', 'Monaco', monospace;
      }
    }
  }

  .main-progress {
    margin-bottom: 20px;
  }

  .chart-loading,
  .chart-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 80px 20px;
    background-color: #f5f7fa;
    border-radius: 8px;
    min-height: 350px;
    color: #909399;
  }

  .training-logs {
    h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }

    .log-list {
      max-height: 250px;
      overflow-y: auto;

      .log-item {
        display: flex;
        gap: 12px;
        padding: 10px 12px;
        margin-bottom: 8px;
        border-radius: 6px;
        font-size: 13px;
        background-color: #f9fafb;
        border-left: 3px solid #e4e7ed;

        .log-time {
          color: #909399;
          font-family: 'Consolas', 'Monaco', monospace;
          min-width: 80px;
        }

        .log-message {
          flex: 1;
          color: #606266;
        }

        &.log-info {
          border-left-color: #409eff;
        }

        &.log-success {
          border-left-color: #67c23a;
          background-color: #f0f9ff;
        }

        &.log-warning {
          border-left-color: #e6a23c;
          background-color: #fdf6ec;
        }

        &.log-error {
          border-left-color: #f56c6c;
          background-color: #fef0f0;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .progress-panel-card {
    .progress-overview {
      grid-template-columns: repeat(3, 1fr);
    }
  }
}

@media (max-width: 768px) {
  .progress-panel-card {
    .progress-overview {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}
</style>
