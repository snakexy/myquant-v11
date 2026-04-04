<template>
  <el-card class="control-panel-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">🎮 模拟实盘控制</span>
      </div>
    </template>

    <!-- 策略选择 -->
    <div class="strategy-section">
      <el-form-item label="选择策略">
        <el-select
          v-model="selectedStrategy"
          placeholder="请选择策略"
          @change="handleStrategyChange"
        >
          <el-option
            v-for="strategy in strategies"
            :key="strategy.id"
            :label="strategy.name"
            :value="strategy.id"
          />
        </el-select>
      </el-form-item>
    </div>

    <!-- 状态卡片 -->
    <SimulationStatusCard
      :simulation-status="simulationStatus"
      :metrics="metrics"
    />

    <!-- 控制按钮 -->
    <div class="control-buttons">
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        :disabled="simulationStatus === 'running'"
        @click="handleStart"
      >
        <el-icon><VideoPlay /></el-icon>
        启动模拟
      </el-button>
      <el-button
        type="danger"
        size="large"
        :disabled="simulationStatus === 'stopped'"
        @click="handleStop"
      >
        <el-icon><VideoPause /></el-icon>
        停止模拟
      </el-button>
      <el-button
        size="large"
        :loading="refreshing"
        @click="handleRefresh"
      >
        <el-icon><Refresh /></el-icon>
        刷新状态
      </el-button>
    </div>

    <!-- 在线滚动训练状态 -->
    <el-divider />
    <div class="learning-section">
      <h4>📚 在线滚动训练</h4>
      <div class="learning-status">
        <div class="model-version">
          <span class="label">模型版本:</span>
          <span class="value">{{ learningInfo.modelVersion }}</span>
        </div>
        <div class="last-update">
          <span class="label">最后更新:</span>
          <span class="value">{{ learningInfo.lastUpdate }}</span>
        </div>
        <div class="learning-progress">
          <el-progress :percentage="learningInfo.progress" />
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, VideoPause, Refresh } from '@element-plus/icons-vue'
import { simulationApi } from '@/api/modules/simulation'
import type { Strategy, SimulationMetrics, OnlineTrainingStatus } from '@/api/modules/simulation'
import SimulationStatusCard from './SimulationStatusCard.vue'

// 策略列表
const strategies = ref<Strategy[]>([])

// 选中的策略
const selectedStrategy = ref<string>('')

// 模拟状态
const simulationStatus = ref<'running' | 'stopped' | 'paused'>('stopped')
const loading = ref(false)
const refreshing = ref(false)

// 核心指标
const metrics = reactive<SimulationMetrics>({
  currentAssets: 0,
  totalReturn: 0,
  totalReturnRate: 0,
  maxDrawdown: 0,
  sharpeRatio: 0,
  positionCount: 0,
  lastUpdateTime: ''
})

// 在线训练信息
const learningInfo = reactive<OnlineTrainingStatus>({
  modelVersion: '',
  lastUpdateTime: '',
  trainingProgress: 0,
  status: 'completed'
})

// 加载策略列表
const loadStrategies = async () => {
  try {
    const response = await simulationApi.getStrategies()
    if (response.code === 200) {
      strategies.value = response.data
      if (strategies.value.length > 0 && !selectedStrategy.value) {
        selectedStrategy.value = strategies.value[0].id
      }
    }
  } catch (error) {
    console.error('加载策略列表失败:', error)
    // 失败时使用默认数据作为降级方案
    strategies.value = [
      { id: 'strategy_1', name: '双均线策略', type: 'trend_following', status: 'active' },
      { id: 'strategy_2', name: '多因子策略', type: 'mean_reversion', status: 'active' },
      { id: 'strategy_3', name: '机器学习策略', type: 'ml_based', status: 'active' },
      { id: 'strategy_4', name: '动量策略', type: 'momentum', status: 'active' }
    ]
    if (!selectedStrategy.value) {
      selectedStrategy.value = strategies.value[0].id
    }
  }
}

// 加载模拟状态
const loadSimulationStatus = async () => {
  try {
    const response = await simulationApi.getStatus()
    if (response.code === 200) {
      const data = response.data
      simulationStatus.value = data.status
      Object.assign(metrics, {
        currentAssets: data.currentAssets,
        totalReturn: data.totalReturn,
        totalReturnRate: data.totalReturnRate,
        maxDrawdown: data.maxDrawdown,
        sharpeRatio: data.sharpeRatio,
        positionCount: data.positionCount,
        lastUpdateTime: data.lastUpdateTime
      })
      Object.assign(learningInfo, data.onlineTraining)
    }
  } catch (error) {
    console.error('加载模拟状态失败:', error)
    // 失败时使用默认数据作为降级方案
    Object.assign(metrics, {
      currentAssets: 1000000,
      totalReturn: 0,
      totalReturnRate: 0,
      maxDrawdown: 0,
      sharpeRatio: 0,
      positionCount: 0,
      lastUpdateTime: new Date().toISOString()
    })
  }
}

// 策略切换处理
const handleStrategyChange = async (strategyId: string) => {
  try {
    const response = await simulationApi.switchStrategy(strategyId)
    if (response.code === 200) {
      ElMessage.success('策略已切换，配置已更新')
      await loadSimulationStatus()
    }
  } catch (error) {
    console.error('切换策略失败:', error)
    ElMessage.error('策略切换失败')
  }
}

// 启动模拟
const handleStart = async () => {
  loading.value = true
  try {
    const response = await simulationApi.startSimulation(selectedStrategy.value)
    if (response.code === 200) {
      simulationStatus.value = response.data.status
      ElMessage.success('模拟已启动')
      await loadSimulationStatus()
    }
  } catch (error) {
    console.error('启动模拟失败:', error)
    ElMessage.error('启动失败')
  } finally {
    loading.value = false
  }
}

// 停止模拟
const handleStop = async () => {
  try {
    const response = await simulationApi.stopSimulation()
    if (response.code === 200) {
      simulationStatus.value = 'stopped'
      ElMessage.info('模拟已停止')
      await loadSimulationStatus()
    }
  } catch (error) {
    console.error('停止模拟失败:', error)
    ElMessage.error('停止失败')
  }
}

// 刷新状态
const handleRefresh = async () => {
  refreshing.value = true
  try {
    await loadSimulationStatus()
    ElMessage.success('状态已刷新')
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([
    loadStrategies(),
    loadSimulationStatus()
  ])
})
</script>

<style scoped lang="scss">
.control-panel-card {
  .card-header {
    .title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .strategy-section {
    margin-bottom: 16px;

    :deep(.el-form-item) {
      margin-bottom: 0;
    }

    :deep(.el-select) {
      width: 100%;
    }
  }

  .control-buttons {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .learning-section {
    h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      font-weight: 600;
      color: #606266;
    }

    .learning-status {
      .model-version,
      .last-update {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 13px;

        .label {
          color: #909399;
        }

        .value {
          color: #303133;
          font-weight: 500;
        }
      }

      .learning-progress {
        margin-top: 12px;
      }
    }
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
