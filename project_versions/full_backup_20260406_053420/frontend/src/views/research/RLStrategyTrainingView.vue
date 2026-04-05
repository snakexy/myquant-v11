<template>
  <div class="rl-training-view">
    <!-- 页面头部 -->
    <div class="view-header">
      <div class="header-left">
        <h2 class="view-title">RL策略训练</h2>
        <p class="view-subtitle">配置并训练强化学习策略</p>
      </div>
      <div class="header-right">
        <el-button
          type="primary"
          :loading="training"
          :disabled="!canStartTraining"
          @click="startTraining"
        >
          <el-icon v-if="!training"><VideoPlay /></el-icon>
          <span>{{ training ? '训练中...' : '开始训练' }}</span>
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="view-content">
      <!-- 左侧：配置面板 -->
      <div class="config-panel">
        <!-- 算法配置 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>算法配置</span>
            </div>
          </template>

          <el-form :model="form" label-width="120px" label-position="left">
            <!-- 算法选择 -->
            <el-form-item label="算法类型">
              <el-select v-model="form.algorithm" placeholder="选择算法">
                <el-option label="自动选择最优 (Auto)" value="AUTO" />
                <el-option label="PPO (Proximal Policy Optimization)" value="PPO" />
                <el-option label="DQN (Deep Q-Network)" value="DQN" />
                <el-option label="A2C (Advantage Actor-Critic)" value="A2C" />
              </el-select>
            </el-form-item>

            <!-- 设备选择 -->
            <el-form-item label="计算设备">
              <el-select v-model="form.device" placeholder="选择设备">
                <el-option label="自动 (Auto)" value="auto" />
                <el-option label="GPU (CUDA)" value="cuda" />
                <el-option label="CPU" value="cpu" />
              </el-select>
            </el-form-item>

            <!-- 应用场景 -->
            <el-form-item label="应用场景">
              <el-select v-model="form.scenario" placeholder="选择场景">
                <el-option label="订单执行 (Order Execution)" value="order_execution" />
                <el-option label="投资组合构建 (Portfolio Construction)" value="portfolio_construction" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 训练参数 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>训练参数</span>
            </div>
          </template>

          <el-form :model="form" label-width="120px" label-position="left">
            <!-- 最大训练轮数 -->
            <el-form-item label="最大训练轮数">
              <el-input-number
                v-model="form.max_episodes"
                :min="100"
                :max="10000"
                :step="100"
                controls-position="right"
              />
            </el-form-item>

            <!-- 每轮最大步数 -->
            <el-form-item label="每轮最大步数">
              <el-input-number
                v-model="form.max_steps_per_episode"
                :min="10"
                :max="1000"
                :step="10"
                controls-position="right"
              />
            </el-form-item>

            <!-- 学习率 -->
            <el-form-item label="学习率">
              <el-slider
                v-model="form.learning_rate"
                :min="0.0001"
                :max="0.01"
                :step="0.0001"
                :format-tooltip="formatLearningRate"
                show-input
                :show-input-controls="false"
              />
            </el-form-item>

            <!-- 折扣因子 -->
            <el-form-item label="折扣因子 (γ)">
              <el-slider
                v-model="form.gamma"
                :min="0.9"
                :max="0.999"
                :step="0.001"
                show-input
                :show-input-controls="false"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 网络参数 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>网络参数</span>
            </div>
          </template>

          <el-form :model="form" label-width="120px" label-position="left">
            <!-- 隐藏层大小 -->
            <el-form-item label="隐藏层大小">
              <el-select v-model="form.hidden_size">
                <el-option label="64" :value="64" />
                <el-option label="128" :value="128" />
                <el-option label="256" :value="256" />
                <el-option label="512" :value="512" />
              </el-select>
            </el-form-item>

            <!-- 网络层数 -->
            <el-form-item label="网络层数">
              <el-input-number
                v-model="form.num_layers"
                :min="1"
                :max="5"
                controls-position="right"
              />
            </el-form-item>

            <!-- 批次大小 -->
            <el-form-item label="批次大小">
              <el-select v-model="form.batch_size">
                <el-option label="32" :value="32" />
                <el-option label="64" :value="64" />
                <el-option label="128" :value="128" />
                <el-option label="256" :value="256" />
              </el-select>
            </el-form-item>

            <!-- 经验池大小 -->
            <el-form-item label="经验池大小">
              <el-select v-model="form.buffer_size">
                <el-option label="10000" :value="10000" />
                <el-option label="50000" :value="50000" />
                <el-option label="100000" :value="100000" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 环境参数 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Odometer /></el-icon>
              <span>环境参数</span>
            </div>
          </template>

          <el-form :model="form" label-width="120px" label-position="left">
            <!-- 状态维度 -->
            <el-form-item label="状态维度">
              <el-input-number
                v-model="form.state_dim"
                :min="1"
                :max="100"
                controls-position="right"
              />
            </el-form-item>

            <!-- 动作维度 -->
            <el-form-item label="动作维度">
              <el-input-number
                v-model="form.action_dim"
                :min="2"
                :max="20"
                controls-position="right"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 算法特定参数 -->
        <el-card v-if="form.algorithm === 'PPO'" class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Tools /></el-icon>
              <span>PPO特定参数</span>
            </div>
          </template>

          <el-form :model="form" label-width="140px" label-position="left">
            <!-- 裁剪参数 -->
            <el-form-item label="裁剪参数 (ε)">
              <el-slider
                v-model="form.clip_param"
                :min="0.1"
                :max="0.3"
                :step="0.05"
                show-input
                :show-input-controls="false"
              />
            </el-form-item>

            <!-- 熵系数 -->
            <el-form-item label="熵系数">
              <el-slider
                v-model="form.entropy_coef"
                :min="0.001"
                :max="0.1"
                :step="0.001"
                :format-tooltip="formatEntropy"
                show-input
                :show-input-controls="false"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <el-card v-if="form.algorithm === 'DQN'" class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Tools /></el-icon>
              <span>DQN特定参数</span>
            </div>
          </template>

          <el-form :model="form" label-width="140px" label-position="left">
            <!-- 探索起始值 -->
            <el-form-item label="探索起始值">
              <el-slider
                v-model="form.epsilon_start"
                :min="0.5"
                :max="1.0"
                :step="0.1"
                show-input
                :show-input-controls="false"
              />
            </el-form-item>

            <!-- 探索结束值 -->
            <el-form-item label="探索结束值">
              <el-slider
                v-model="form.epsilon_end"
                :min="0.01"
                :max="0.1"
                :step="0.01"
                show-input
                :show-input-controls="false"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 右侧：训练进度和日志 -->
      <div class="progress-panel">
        <!-- 训练进度 -->
        <el-card class="progress-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Timer /></el-icon>
              <span>训练进度</span>
            </div>
          </template>

          <div v-if="trainingResult" class="progress-content">
            <!-- 训练状态 -->
            <div class="status-item">
              <span class="status-label">训练状态</span>
              <el-tag :type="training ? 'warning' : 'success'">
                {{ training ? '训练中' : '已完成' }}
              </el-tag>
            </div>

            <!-- 训练进度条 -->
            <div class="status-item">
              <span class="status-label">训练进度</span>
              <el-progress
                :percentage="trainingProgress"
                :status="training ? 'warning' : 'success'"
              />
            </div>

            <!-- 当前奖励 -->
            <div class="status-item">
              <span class="status-label">当前奖励</span>
              <span class="status-value">{{ trainingResult.final_reward?.toFixed(4) || '0.0000' }}</span>
            </div>

            <!-- 最佳奖励 -->
            <div class="status-item">
              <span class="status-label">最佳奖励</span>
              <span class="status-value best">{{ trainingResult.best_reward?.toFixed(4) || '0.0000' }}</span>
            </div>

            <!-- 平均奖励 -->
            <div class="status-item">
              <span class="status-label">平均奖励</span>
              <span class="status-value">{{ trainingResult.average_reward?.toFixed(4) || '0.0000' }}</span>
            </div>

            <!-- 训练时长 -->
            <div class="status-item">
              <span class="status-label">训练时长</span>
              <span class="status-value">{{ formatDuration(trainingDuration) }}</span>
            </div>

            <!-- 训练曲线 -->
            <div v-if="rewardHistory.length > 0" class="reward-chart">
              <div ref="rewardChartRef" class="chart-container"></div>
            </div>
          </div>

          <div v-else class="no-training">
            <el-empty description="暂无训练数据">
              <el-icon class="empty-icon"><Box /></el-icon>
            </el-empty>
          </div>
        </el-card>

        <!-- 训练日志 -->
        <el-card class="log-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>训练日志</span>
            </div>
          </template>

          <div ref="logContainerRef" class="log-container">
            <div
              v-for="(log, index) in logs"
              :key="index"
              :class="['log-item', `log-${log.type}`]"
            >
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <div v-if="logs.length === 0" class="no-logs">
              <el-empty description="暂无日志" :image-size="80" />
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  VideoPlay, Setting, DataAnalysis, Connection, Odometer,
  Tools, Timer, Document, Box
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { rlAPI, type RLTrainingRequest, type RLTrainingResult } from '@/api/research'
import { rlStrategyAPI, type RLAutoSelectionResult } from '@/api/rlStrategy'

// ==================== 表单数据 ====================

const form = ref<RLTrainingRequest & { device: string }>({
  algorithm: 'AUTO',
  scenario: 'order_execution',
  max_episodes: 1000,
  max_steps_per_episode: 100,
  hidden_size: 128,
  num_layers: 2,
  learning_rate: 0.0003,
  state_dim: 10,
  action_dim: 3,
  gamma: 0.99,
  buffer_size: 10000,
  batch_size: 64,
  clip_param: 0.2,
  entropy_coef: 0.01,
  epsilon_start: 1.0,
  epsilon_end: 0.01,
  device: 'auto'
})

// ==================== 训练状态 ====================

const training = ref(false)
const trainingResult = ref<RLTrainingResult | null>(null)
const trainingDuration = ref(0)
const rewardHistory = ref<Array<{ episode: number; reward: number }>>([])

// ==================== 日志 ====================

interface LogItem {
  time: string
  type: 'info' | 'success' | 'warning' | 'error'
  message: string
}

const logs = ref<LogItem[]>([])
const logContainerRef = ref<HTMLElement>()

// ==================== 计算属性 ====================

const canStartTraining = computed(() => {
  return !training.value && form.value.algorithm && form.value.scenario
})

const trainingProgress = computed(() => {
  if (!trainingResult.value) return 0
  const progress = (trainingResult.value.total_episodes / form.value.max_episodes) * 100
  return Math.min(progress, 100)
})

// ==================== 方法 ====================

/**
 * 格式化学习率
 */
const formatLearningRate = (val: number) => {
  return val.toExponential(2)
}

/**
 * 格式化熵系数
 */
const formatEntropy = (val: number) => {
  return val.toExponential(2)
}

/**
 * 格式化时长
 */
const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  } else {
    return `${secs}s`
  }
}

/**
 * 添加日志
 */
const addLog = (message: string, type: LogItem['type'] = 'info') => {
  const now = new Date()
  const time = now.toLocaleTimeString('zh-CN', { hour12: false })

  logs.value.push({ time, type, message })

  // 自动滚动到底部
  nextTick(() => {
    if (logContainerRef.value) {
      logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
    }
  })
}

/**
 * 开始训练
 */
const startTraining = async () => {
  try {
    training.value = true
    trainingDuration.value = 0
    trainingResult.value = null
    rewardHistory.value = []
    logs.value = []

    addLog('开始初始化训练...', 'info')
    addLog(`算法: ${form.value.algorithm}`, 'info')
    addLog(`场景: ${form.value.scenario}`, 'info')
    addLog(`设备: ${form.value.device}`, 'info')
    addLog(`训练轮数: ${form.value.max_episodes}`, 'info')

    // 判断是否为自动选择模式
    if (form.value.algorithm === 'AUTO') {
      // 自动选择最优算法
      addLog('启动自动算法选择模式...', 'info')
      addLog('将训练 DQN、PPO、A2C 三种算法并选择最优', 'info')

      const response = await rlStrategyAPI.autoSelect({
        scenario: form.value.scenario,
        max_episodes: form.value.max_episodes,
        device: form.value.device
      })

      if (response.code === 200) {
        const autoResult: RLAutoSelectionResult = response.data

        // 显示各算法结果
        addLog('========== 自动选择结果 ==========', 'success')
        for (const [algo, result] of Object.entries(autoResult.results_by_algorithm)) {
          if (result.status === 'completed') {
            addLog(`${algo}: best_reward=${result.best_reward?.toFixed(4) || 'N/A'}`, 'info')
          } else {
            addLog(`${algo}: 训练失败 - ${result.error || '未知错误'}`, 'warning')
          }
        }

        addLog('================================', 'success')
        addLog(`最优算法: ${autoResult.best_algorithm}`, 'success')
        addLog(`最佳奖励: ${autoResult.best_reward.toFixed(4)}`, 'success')
        addLog(`总训练时长: ${formatDuration(autoResult.training_duration)}`, 'info')

        // 设置训练结果
        trainingResult.value = {
          training_id: autoResult.best_training_id,
          status: 'completed',
          episode: 0,
          total_episodes: form.value.max_episodes,
          reward: autoResult.best_reward,
          avg_reward: autoResult.best_reward,
          best_avg_reward: autoResult.best_reward
        }
        trainingDuration.value = autoResult.training_duration

        ElMessage.success(`自动选择完成！最优算法: ${autoResult.best_algorithm}`)
      }
    } else {
      // 单算法训练模式
      const response = await rlAPI.trainRLStrategy({
        ...form.value,
        device: form.value.device
      })

      if (response.code === 200) {
        trainingResult.value = response.data
        trainingDuration.value = response.data.training_duration

        // 模拟奖励历史
        for (let i = 0; i < response.data.total_episodes; i++) {
          rewardHistory.value.push({
            episode: i + 1,
            reward: response.data.final_reward * (0.5 + Math.random() * 0.5)
          })
        }

        addLog('训练完成！', 'success')
        addLog(`最终奖励: ${response.data.final_reward.toFixed(4)}`, 'info')
        addLog(`最佳奖励: ${response.data.best_reward.toFixed(4)}`, 'info')
        addLog(`平均奖励: ${response.data.average_reward.toFixed(4)}`, 'info')
        addLog(`训练时长: ${formatDuration(response.data.training_duration)}`, 'info')

        ElMessage.success('训练完成！')
      }
    }
  } catch (error: any) {
    console.error('训练失败:', error)
    addLog(`训练失败: ${error.message || error}`, 'error')
    ElMessage.error('训练失败，请检查配置')
  } finally {
    training.value = false
  }
}

// ==================== 图表 ====================

const rewardChartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!rewardChartRef.value) return

  chart = echarts.init(rewardChartRef.value)

  const option = {
    title: {
      text: '奖励曲线',
      textStyle: { color: '#cbd5e1', fontSize: 14 },
      left: 'center'
    },
    grid: {
      left: '10%',
      right: '5%',
      top: '15%',
      bottom: '10%'
    },
    xAxis: {
      type: 'category',
      name: 'Episode',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: {
      type: 'value',
      name: 'Reward',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    series: [{
      name: 'Reward',
      type: 'line',
      data: rewardHistory.value.map(item => item.reward),
      smooth: true,
      lineStyle: { color: '#8b5cf6', width: 2 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
            { offset: 1, color: 'rgba(139, 92, 246, 0)' }
          ]
        }
      }
    }]
  }

  chart.setOption(option)
}

// ==================== 生命周期 ====================

onMounted(() => {
  addLog('RL策略训练界面已就绪', 'info')
  addLog('请配置训练参数并开始训练', 'info')
})
</script>

<style scoped lang="scss">
.rl-training-view {
  min-height: 100vh;
  background: var(--bg-deep);
  padding: 20px;
  color: var(--text-primary);
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);

  .header-left {
    .view-title {
      margin: 0 0 4px 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .view-subtitle {
      margin: 0;
      font-size: 14px;
      color: var(--text-muted);
    }
  }
}

.view-content {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 20px;
  height: calc(100vh - 140px);
}

.config-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  padding-right: 4px;

  .config-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-light);

    :deep(.el-card__header) {
      background: var(--bg-elevated);
      border-bottom: 1px solid var(--border-light);
      padding: 12px 16px;
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
      color: var(--text-primary);
    }

    :deep(.el-card__body) {
      padding: 16px;
    }

    .el-form-item {
      margin-bottom: 16px;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

.progress-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.progress-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);

  :deep(.el-card__header) {
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border-light);
    padding: 12px 16px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    color: var(--text-primary);
  }

  :deep(.el-card__body) {
    padding: 16px;
  }

  .progress-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .status-label {
      font-size: 14px;
      color: var(--text-secondary);
    }

    .status-value {
      font-size: 16px;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-primary);

      &.best {
        color: #8b5cf6;
      }
    }
  }

  .reward-chart {
    height: 200px;
    margin-top: 8px;

    .chart-container {
      width: 100%;
      height: 100%;
    }
  }

  .no-training {
    text-align: center;
    padding: 40px 0;

    .empty-icon {
      font-size: 48px;
      color: var(--text-muted);
    }
  }
}

.log-card {
  flex: 1;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;

  :deep(.el-card__header) {
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border-light);
    padding: 12px 16px;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    color: var(--text-primary);
  }

  :deep(.el-card__body) {
    padding: 0;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .log-container {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.6;
    background: #0a0a0f;

    .log-item {
      display: flex;
      gap: 8px;
      padding: 4px 0;

      &.log-info {
        .log-time { color: #3b82f6; }
        .log-message { color: var(--text-secondary); }
      }

      &.log-success {
        .log-time { color: #10b981; }
        .log-message { color: #10b981; }
      }

      &.log-warning {
        .log-time { color: #f59e0b; }
        .log-message { color: #f59e0b; }
      }

      &.log-error {
        .log-time { color: #ef4444; }
        .log-message { color: #ef4444; }
      }

      .log-time {
        flex-shrink: 0;
        opacity: 0.8;
      }

      .log-message {
        flex: 1;
        word-break: break-all;
      }
    }

    .no-logs {
      text-align: center;
      padding: 40px 0;
    }
  }
}

// 滚动条样式
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-deep);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-elevated);
  border-radius: var(--radius-full);

  &:hover {
    background: var(--border-strong);
  }
}
</style>
