<template>
  <div class="rl-optimization-view">
    <!-- 页面头部 -->
    <div class="view-header">
      <div class="header-left">
        <h2 class="view-title">RL策略超参数优化</h2>
        <p class="view-subtitle">自动搜索最优超参数组合</p>
      </div>
      <div class="header-right">
        <el-button
          type="primary"
          :loading="optimizing"
          :disabled="!canStartOptimization"
          @click="startOptimization"
        >
          <el-icon v-if="!optimizing"><Search /></el-icon>
          <span>{{ optimizing ? '优化中...' : '开始优化' }}</span>
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="view-content">
      <!-- 左侧：优化配置面板 -->
      <div class="config-panel">
        <!-- 算法配置 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>基础配置</span>
            </div>
          </template>

          <el-form :model="form" label-width="120px" label-position="left">
            <!-- 算法选择 -->
            <el-form-item label="算法类型">
              <el-select v-model="form.algorithm" placeholder="选择算法">
                <el-option label="PPO (Proximal Policy Optimization)" value="PPO" />
                <el-option label="DQN (Deep Q-Network)" value="DQN" />
                <el-option label="A2C (Advantage Actor-Critic)" value="A2C" />
              </el-select>
            </el-form-item>

            <!-- 应用场景 -->
            <el-form-item label="应用场景">
              <el-select v-model="form.scenario" placeholder="选择场景">
                <el-option label="订单执行 (Order Execution)" value="order_execution" />
                <el-option label="投资组合构建 (Portfolio Construction)" value="portfolio_construction" />
              </el-select>
            </el-form-item>

            <!-- 试验次数 -->
            <el-form-item label="试验次数">
              <el-input-number
                v-model="form.n_trials"
                :min="5"
                :max="100"
                :step="5"
                controls-position="right"
              />
              <div class="form-tip">
                预计搜索 {{ form.n_trials }} 组参数组合
              </div>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 参数网格配置 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Grid /></el-icon>
              <span>参数网格</span>
            </div>
          </template>

          <div class="param-grid-config">
            <!-- 学习率 -->
            <div class="param-item">
              <div class="param-header">
                <span class="param-name">学习率</span>
                <el-button
                  size="small"
                  :icon="Plus"
                  @click="addParamValue('learning_rate')"
                />
              </div>
              <div class="param-values">
                <el-tag
                  v-for="(value, index) in paramGrid.learning_rate"
                  :key="index"
                  closable
                  @close="removeParamValue('learning_rate', index)"
                >
                  {{ formatLearningRate(value) }}
                </el-tag>
                <el-button
                  v-if="paramGrid.learning_rate.length === 0"
                  size="small"
                  type="primary"
                  plain
                  @click="addDefaultValue('learning_rate', [0.0001, 0.0003, 0.001])"
                >
                  添加默认值
                </el-button>
              </div>
            </div>

            <!-- 隐藏层大小 -->
            <div class="param-item">
              <div class="param-header">
                <span class="param-name">隐藏层大小</span>
                <el-button
                  size="small"
                  :icon="Plus"
                  @click="addParamValue('hidden_size')"
                />
              </div>
              <div class="param-values">
                <el-tag
                  v-for="(value, index) in paramGrid.hidden_size"
                  :key="index"
                  closable
                  @close="removeParamValue('hidden_size', index)"
                >
                  {{ value }}
                </el-tag>
                <el-button
                  v-if="paramGrid.hidden_size.length === 0"
                  size="small"
                  type="primary"
                  plain
                  @click="addDefaultValue('hidden_size', [64, 128, 256])"
                >
                  添加默认值
                </el-button>
              </div>
            </div>

            <!-- 批次大小 -->
            <div class="param-item">
              <div class="param-header">
                <span class="param-name">批次大小</span>
                <el-button
                  size="small"
                  :icon="Plus"
                  @click="addParamValue('batch_size')"
                />
              </div>
              <div class="param-values">
                <el-tag
                  v-for="(value, index) in paramGrid.batch_size"
                  :key="index"
                  closable
                  @close="removeParamValue('batch_size', index)"
                >
                  {{ value }}
                </el-tag>
                <el-button
                  v-if="paramGrid.batch_size.length === 0"
                  size="small"
                  type="primary"
                  plain
                  @click="addDefaultValue('batch_size', [32, 64, 128])"
                >
                  添加默认值
                </el-button>
              </div>
            </div>

            <!-- 折扣因子 -->
            <div class="param-item">
              <div class="param-header">
                <span class="param-name">折扣因子 (γ)</span>
                <el-button
                  size="small"
                  :icon="Plus"
                  @click="addParamValue('gamma')"
                />
              </div>
              <div class="param-values">
                <el-tag
                  v-for="(value, index) in paramGrid.gamma"
                  :key="index"
                  closable
                  @close="removeParamValue('gamma', index)"
                >
                  {{ value }}
                </el-tag>
                <el-button
                  v-if="paramGrid.gamma.length === 0"
                  size="small"
                  type="primary"
                  plain
                  @click="addDefaultValue('gamma', [0.95, 0.99, 0.995])"
                >
                  添加默认值
                </el-button>
              </div>
            </div>

            <!-- PPO特定参数 -->
            <template v-if="form.algorithm === 'PPO'">
              <div class="param-item">
                <div class="param-header">
                  <span class="param-name">裁剪参数 (ε)</span>
                  <el-button
                    size="small"
                    :icon="Plus"
                    @click="addParamValue('clip_param')"
                  />
                </div>
                <div class="param-values">
                  <el-tag
                    v-for="(value, index) in paramGrid.clip_param"
                    :key="index"
                    closable
                    @close="removeParamValue('clip_param', index)"
                  >
                    {{ value }}
                  </el-tag>
                  <el-button
                    v-if="paramGrid.clip_param?.length === 0"
                    size="small"
                    type="primary"
                    plain
                    @click="addDefaultValue('clip_param', [0.1, 0.2, 0.3])"
                  >
                    添加默认值
                  </el-button>
                </div>
              </div>

              <div class="param-item">
                <div class="param-header">
                  <span class="param-name">熵系数</span>
                  <el-button
                    size="small"
                    :icon="Plus"
                    @click="addParamValue('entropy_coef')"
                  />
                </div>
                <div class="param-values">
                  <el-tag
                    v-for="(value, index) in paramGrid.entropy_coef"
                    :key="index"
                    closable
                    @close="removeParamValue('entropy_coef', index)"
                  >
                    {{ formatEntropy(value) }}
                  </el-tag>
                  <el-button
                    v-if="paramGrid.entropy_coef?.length === 0"
                    size="small"
                    type="primary"
                    plain
                    @click="addDefaultValue('entropy_coef', [0.001, 0.01, 0.05])"
                  >
                    添加默认值
                  </el-button>
                </div>
              </div>
            </template>
          </div>

          <!-- 组合数量提示 -->
          <div class="combination-info">
            <el-alert
              :title="`总参数组合数: ${totalCombinations}`"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <div>
                  <p>将在 {{ form.n_trials }} 次试验中搜索最优参数</p>
                  <p v-if="totalCombinations > form.n_trials" class="warning">
                    参数组合数 ({{ totalCombinations }}) 超过试验次数，将使用随机搜索策略
                  </p>
                </div>
              </template>
            </el-alert>
          </div>
        </el-card>

        <!-- 快速预设 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><MagicStick /></el-icon>
              <span>快速预设</span>
            </div>
          </template>

          <div class="preset-buttons">
            <el-button
              type="primary"
              plain
              @click="applyPreset('quick')"
            >
              快速搜索（5组参数）
            </el-button>
            <el-button
              type="primary"
              plain
              @click="applyPreset('standard')"
            >
              标准搜索（10组参数）
            </el-button>
            <el-button
              type="primary"
              plain
              @click="applyPreset('thorough')"
            >
              深度搜索（20组参数）
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 右侧：优化结果面板 -->
      <div class="result-panel">
        <!-- 优化状态 -->
        <el-card class="result-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>优化结果</span>
            </div>
          </template>

          <div v-if="optimizationResult" class="result-content">
            <!-- 最佳参数 -->
            <div class="best-params">
              <h3 class="section-title">最佳参数</h3>
              <div class="param-grid">
                <div
                  v-for="(value, key) in optimizationResult.best_params"
                  :key="key"
                  class="param-display"
                >
                  <span class="param-label">{{ formatParamName(key) }}</span>
                  <span class="param-value">{{ formatParamValue(key, value) }}</span>
                </div>
              </div>
            </div>

            <!-- 最佳指标 -->
            <div class="best-metrics">
              <h3 class="section-title">最佳指标</h3>
              <div class="metric-grid">
                <div class="metric-item primary">
                  <span class="metric-label">最佳奖励</span>
                  <span class="metric-value">{{
                    optimizationResult.best_metrics.best_reward.toFixed(4)
                  }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">试验次数</span>
                  <span class="metric-value">{{
                    optimizationResult.best_metrics.n_trials
                  }}</span>
                </div>
              </div>
            </div>

            <!-- 优化进度 -->
            <div v-if="optimizing" class="optimization-progress">
              <el-progress
                :percentage="optimizationProgress"
                :status="optimizing ? 'warning' : 'success'"
              >
                <span>{{ optimizationProgress }}%</span>
              </el-progress>
            </div>
          </div>

          <div v-else class="no-result">
            <el-empty description="暂无优化结果">
              <el-icon class="empty-icon"><Box /></el-icon>
            </el-empty>
          </div>
        </el-card>

        <!-- 所有试验结果 -->
        <el-card v-if="optimizationResult && optimizationResult.all_trials" class="trials-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><List /></el-icon>
              <span>所有试验</span>
            </div>
          </template>

          <div class="trials-content">
            <el-table :data="paginatedTrials" stripe style="width: 100%" max-height="400">
              <el-table-column prop="episode" label="试验" width="80" />
              <el-table-column label="参数" min-width="200">
                <template #default="{ row }">
                  <el-tag
                    v-for="(value, key) in row.params"
                    :key="key"
                    size="small"
                    class="param-tag"
                  >
                    {{ formatParamName(key) }}: {{ formatParamValue(key, value) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="reward" label="奖励" width="120">
                <template #default="{ row }">
                  <span
                    :class="{
                      'reward-best': row.reward === bestReward,
                      'reward-good': row.reward > averageReward
                    }"
                  >
                    {{ row.reward.toFixed(4) }}
                  </span>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="optimizationResult.all_trials.length"
                layout="prev, pager, next"
                small
              />
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search, Setting, Grid, Plus, MagicStick, DataAnalysis,
  List, Box
} from '@element-plus/icons-vue'
import { rlAPI, type RLOptimizationRequest, type RLOptimizationResult } from '@/api/research'

// ==================== 表单数据 ====================

const form = ref<{
  algorithm: 'PPO' | 'DQN' | 'A2C'
  scenario: 'order_execution' | 'portfolio_construction'
  n_trials: number
}>({
  algorithm: 'PPO',
  scenario: 'order_execution',
  n_trials: 10
})

// ==================== 参数网格 ====================

const paramGrid = ref<Record<string, number[]>>({
  learning_rate: [],
  hidden_size: [],
  batch_size: [],
  gamma: [],
  clip_param: [],
  entropy_coef: []
})

// ==================== 优化状态 ====================

const optimizing = ref(false)
const optimizationProgress = ref(0)
const optimizationResult = ref<RLOptimizationResult | null>(null)

// ==================== 分页 ====================

const currentPage = ref(1)
const pageSize = ref(10)

// ==================== 计算属性 ====================

const canStartOptimization = computed(() => {
  return !optimizing.value &&
         form.value.algorithm &&
         form.value.scenario &&
         hasRequiredParams.value
})

const hasRequiredParams = computed(() => {
  return paramGrid.value.learning_rate.length > 0 &&
         paramGrid.value.hidden_size.length > 0 &&
         paramGrid.value.batch_size.length > 0 &&
         paramGrid.value.gamma.length > 0
})

const totalCombinations = computed(() => {
  let total = 1
  for (const values of Object.values(paramGrid.value)) {
    if (values.length > 0) {
      total *= values.length
    }
  }
  return total
})

const paginatedTrials = computed(() => {
  if (!optimizationResult.value?.all_trials) return []

  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return optimizationResult.value.all_trials.slice(start, end)
})

const bestReward = computed(() => {
  if (!optimizationResult.value?.all_trials) return 0
  return Math.max(...optimizationResult.value.all_trials.map(t => t.reward))
})

const averageReward = computed(() => {
  if (!optimizationResult.value?.all_trials) return 0
  const sum = optimizationResult.value.all_trials.reduce((acc, t) => acc + t.reward, 0)
  return sum / optimizationResult.value.all_trials.length
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
 * 格式化参数名称
 */
const formatParamName = (key: string) => {
  const names: Record<string, string> = {
    learning_rate: '学习率',
    hidden_size: '隐藏层',
    batch_size: '批次',
    gamma: '折扣因子',
    clip_param: '裁剪参数',
    entropy_coef: '熵系数'
  }
  return names[key] || key
}

/**
 * 格式化参数值
 */
const formatParamValue = (key: string, value: number) => {
  if (key === 'learning_rate' || key === 'entropy_coef') {
    return value.toExponential(2)
  }
  return value
}

/**
 * 添加参数值
 */
const addParamValue = (param: string) => {
  const dialog = require('element-plus').ElMessageBox
  const input = require('element-plus').ElInput

  dialog.prompt('请输入参数值', '添加参数', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /^\d+(\.\d+)?$/,
    inputErrorMessage: '请输入有效的数字'
  }).then(({ value }) => {
    const numValue = parseFloat(value)
    if (!paramGrid.value[param]) {
      paramGrid.value[param] = []
    }
    paramGrid.value[param].push(numValue)
  }).catch(() => {})
}

/**
 * 移除参数值
 */
const removeParamValue = (param: string, index: number) => {
  paramGrid.value[param].splice(index, 1)
}

/**
 * 添加默认值
 */
const addDefaultValue = (param: string, values: number[]) => {
  paramGrid.value[param] = [...values]
}

/**
 * 应用预设
 */
const applyPreset = (preset: 'quick' | 'standard' | 'thorough') => {
  const presets = {
    quick: {
      n_trials: 5,
      learning_rate: [0.0001, 0.001],
      hidden_size: [64, 128],
      batch_size: [32, 64],
      gamma: [0.99]
    },
    standard: {
      n_trials: 10,
      learning_rate: [0.0001, 0.0003, 0.001],
      hidden_size: [64, 128, 256],
      batch_size: [32, 64, 128],
      gamma: [0.95, 0.99]
    },
    thorough: {
      n_trials: 20,
      learning_rate: [0.0001, 0.0003, 0.001, 0.003],
      hidden_size: [64, 128, 256, 512],
      batch_size: [32, 64, 128, 256],
      gamma: [0.95, 0.99, 0.995]
    }
  }

  const selected = presets[preset]
  form.value.n_trials = selected.n_trials

  Object.entries(selected).forEach(([key, value]) => {
    if (key !== 'n_trials' && Array.isArray(value)) {
      paramGrid.value[key] = value
    }
  })

  ElMessage.success(`已应用${preset === 'quick' ? '快速' : preset === 'standard' ? '标准' : '深度'}搜索预设`)
}

/**
 * 开始优化
 */
const startOptimization = async () => {
  try {
    optimizing.value = true
    optimizationProgress.value = 0
    optimizationResult.value = null

    // 构建请求
    const request: RLOptimizationRequest = {
      algorithm: form.value.algorithm,
      scenario: form.value.scenario,
      param_grid: paramGrid.value,
      n_trials: form.value.n_trials
    }

    ElMessage.info('开始超参数优化...')

    // 模拟进度
    const progressInterval = setInterval(() => {
      if (optimizationProgress.value < 90) {
        optimizationProgress.value += 10
      }
    }, 500)

    // 调用API
    const response = await rlAPI.optimizeStrategy(request)

    clearInterval(progressInterval)
    optimizationProgress.value = 100

    if (response.code === 200) {
      optimizationResult.value = response.data
      ElMessage.success('优化完成！')
    }
  } catch (error: any) {
    console.error('优化失败:', error)
    ElMessage.error('优化失败，请检查配置')
  } finally {
    optimizing.value = false
  }
}
</script>

<style scoped lang="scss">
.rl-optimization-view {
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
  grid-template-columns: 450px 1fr;
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

    .form-tip {
      margin-top: 4px;
      font-size: 12px;
      color: var(--text-muted);
    }

    .combination-info {
      margin-top: 16px;

      .warning {
        color: #f59e0b;
        margin-top: 8px;
      }
    }
  }

  .param-grid-config {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .param-item {
    .param-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .param-name {
        font-size: 14px;
        font-weight: 500;
        color: var(--text-primary);
      }
    }

    .param-values {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      min-height: 32px;

      .el-tag {
        background: var(--bg-elevated);
        border-color: var(--border-medium);
        color: var(--text-primary);
      }
    }
  }

  .preset-buttons {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
}

.result-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.result-card {
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

  .result-content {
    .best-params,
    .best-metrics {
      margin-bottom: 20px;

      .section-title {
        margin: 0 0 12px 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }

      .param-grid,
      .metric-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
      }

      .param-display,
      .metric-item {
        padding: 10px;
        background: var(--bg-elevated);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-light);

        .param-label,
        .metric-label {
          display: block;
          font-size: 12px;
          color: var(--text-muted);
          margin-bottom: 4px;
        }

        .param-value,
        .metric-value {
          display: block;
          font-size: 16px;
          font-weight: 600;
          font-family: 'JetBrains Mono', monospace;
          color: var(--text-primary);
        }

        &.primary {
          background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
          border-color: rgba(139, 92, 246, 0.3);

          .metric-value {
            color: #8b5cf6;
          }
        }
      }
    }

    .optimization-progress {
      margin-top: 16px;
    }
  }

  .no-result {
    text-align: center;
    padding: 40px 0;

    .empty-icon {
      font-size: 48px;
      color: var(--text-muted);
    }
  }
}

.trials-card {
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

  .trials-content {
    padding: 16px;
    flex: 1;
    display: flex;
    flex-direction: column;

    .param-tag {
      margin-right: 4px;
      margin-bottom: 4px;
    }

    .reward-best {
      color: #10b981;
      font-weight: 700;
    }

    .reward-good {
      color: #8b5cf6;
      font-weight: 600;
    }

    .pagination-container {
      margin-top: 16px;
      display: flex;
      justify-content: center;
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
