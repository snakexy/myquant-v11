<template>
  <div class="rl-model-management-view">
    <!-- 页面头部 -->
    <div class="view-header">
      <div class="header-left">
        <h2 class="view-title">RL模型管理</h2>
        <p class="view-subtitle">管理和查看训练好的RL策略模型</p>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="loadModels">刷新</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon total">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总模型数</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon ppo">
            <span>PPO</span>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.by_algorithm.PPO || 0 }}</div>
            <div class="stat-label">PPO模型</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon dqn">
            <span>DQN</span>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.by_algorithm.DQN || 0 }}</div>
            <div class="stat-label">DQN模型</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon a2c">
            <span>A2C</span>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.by_algorithm.A2C || 0 }}</div>
            <div class="stat-label">A2C模型</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主内容区域 -->
    <el-card class="main-card" shadow="hover">
      <!-- 工具栏 -->
      <template #header>
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索训练ID..."
              :prefix-icon="Search"
              clearable
              style="width: 250px"
              @input="handleSearch"
            />
            <el-select
              v-model="filterAlgorithm"
              placeholder="筛选算法"
              clearable
              style="width: 150px"
              @change="handleFilter"
            >
              <el-option label="PPO" value="PPO" />
              <el-option label="DQN" value="DQN" />
              <el-option label="A2C" value="A2C" />
            </el-select>
            <el-select
              v-model="filterScenario"
              placeholder="筛选场景"
              clearable
              style="width: 180px"
              @change="handleFilter"
            >
              <el-option label="订单执行" value="order_execution" />
              <el-option label="投资组合构建" value="portfolio_construction" />
            </el-select>
          </div>
          <div class="toolbar-right">
            <span class="total-info">共 {{ filteredModels.length }} 个模型</span>
          </div>
        </div>
      </template>

      <!-- 模型列表 -->
      <el-table
        :data="paginatedModels"
        stripe
        style="width: 100%"
        v-loading="loading"
        @row-click="viewModelDetails"
      >
        <el-table-column prop="training_id" label="训练ID" min-width="200">
          <template #default="{ row }">
            <el-text truncated>{{ row.training_id }}</el-text>
          </template>
        </el-table-column>

        <el-table-column prop="algorithm" label="算法" width="100">
          <template #default="{ row }">
            <el-tag :type="getAlgorithmTagType(row.algorithm)">
              {{ row.algorithm }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="scenario" label="场景" width="180">
          <template #default="{ row }">
            {{ formatScenario(row.scenario) }}
          </template>
        </el-table-column>

        <el-table-column prop="best_reward" label="最佳奖励" width="120" sortable>
          <template #default="{ row }">
            <span :class="getRewardClass(row.best_reward)">
              {{ row.best_reward?.toFixed(4) || 'N/A' }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ formatStatus(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="View"
              @click.stop="viewModelDetails(row)"
            >
              详情
            </el-button>
            <el-button
              type="success"
              size="small"
              :icon="Download"
              @click.stop="exportModel(row)"
            >
              导出
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click.stop="deleteModel(row)"
            />
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredModels.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 模型详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="模型详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedModel" class="model-detail-content">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h3 class="section-title">基本信息</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">训练ID</span>
              <span class="detail-value">{{ selectedModel.training_id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">算法</span>
              <el-tag :type="getAlgorithmTagType(selectedModel.algorithm)">
                {{ selectedModel.algorithm }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="detail-label">场景</span>
              <span class="detail-value">{{ formatScenario(selectedModel.scenario) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">状态</span>
              <el-tag :type="getStatusType(selectedModel.status)">
                {{ formatStatus(selectedModel.status) }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="detail-label">最佳奖励</span>
              <span class="detail-value highlight">{{
                selectedModel.best_reward?.toFixed(4) || 'N/A'
              }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">创建时间</span>
              <span class="detail-value">{{ formatDateTime(selectedModel.created_at) }}</span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">模型路径</span>
              <span class="detail-value monospace">{{
                selectedModel.model_path || '未保存'
              }}</span>
            </div>
          </div>
        </div>

        <!-- 训练配置 -->
        <div v-if="selectedModelDetail?.config" class="detail-section">
          <h3 class="section-title">训练配置</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="训练轮数">
              {{ selectedModelDetail.config.max_episodes || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="学习率">
              {{ selectedModelDetail.config.learning_rate?.toExponential(2) || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="隐藏层大小">
              {{ selectedModelDetail.config.hidden_size || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="批次大小">
              {{ selectedModelDetail.config.batch_size || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="折扣因子">
              {{ selectedModelDetail.config.gamma || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="状态维度">
              {{ selectedModelDetail.config.state_dim || 'N/A' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 训练结果 -->
        <div v-if="selectedModelDetail" class="detail-section">
          <h3 class="section-title">训练结果</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="最终奖励">
              {{ selectedModelDetail.final_reward?.toFixed(4) || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="平均奖励">
              {{ selectedModelDetail.average_reward?.toFixed(4) || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="最佳奖励">
              <span class="highlight">{{
                selectedModelDetail.best_reward?.toFixed(4) || 'N/A'
              }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="训练时长">
              {{ formatDuration(selectedModelDetail.training_duration) }}
            </el-descriptions-item>
            <el-descriptions-item label="总轮数" :span="2">
              {{ selectedModelDetail.total_episodes || 'N/A' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 训练历史图表 -->
        <div v-if="selectedModelDetail?.training_history" class="detail-section">
          <h3 class="section-title">奖励曲线</h3>
          <div ref="trainingChartRef" class="chart-container"></div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          type="primary"
          :loading="saving"
          :icon="Check"
          @click="saveCurrentModel"
        >
          保存模型
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Search, View, Download, Delete, Box, Check
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { rlAPI, type RLModelInfo, type RLStatistics } from '@/api/research'

// ==================== 数据 ====================

const models = ref<RLModelInfo[]>([])
const stats = ref<RLStatistics>({
  total_trainings: 0,
  total_models: 0,
  by_algorithm: {},
  by_scenario: {},
  dependencies: {}
})

// ==================== 状态 ====================

const loading = ref(false)
const searchKeyword = ref('')
const filterAlgorithm = ref('')
const filterScenario = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// ==================== 详情对话框 ====================

const detailDialogVisible = ref(false)
const selectedModel = ref<RLModelInfo | null>(null)
const selectedModelDetail: any = ref(null)
const saving = ref(false)
const trainingChartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

// ==================== 计算属性 ====================

const filteredModels = computed(() => {
  let result = models.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(m =>
      m.training_id.toLowerCase().includes(keyword)
    )
  }

  // 算法过滤
  if (filterAlgorithm.value) {
    result = result.filter(m => m.algorithm === filterAlgorithm.value)
  }

  // 场景过滤
  if (filterScenario.value) {
    result = result.filter(m => m.scenario === filterScenario.value)
  }

  return result
})

const paginatedModels = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredModels.value.slice(start, end)
})

// ==================== 方法 ====================

/**
 * 加载模型列表
 */
const loadModels = async () => {
  try {
    loading.value = true

    const response = await rlAPI.getModelList(100)

    if (response.code === 200) {
      models.value = response.data.models
      await loadStatistics()
    }
  } catch (error: any) {
    console.error('加载模型失败:', error)
    ElMessage.error('加载模型失败')
  } finally {
    loading.value = false
  }
}

/**
 * 加载统计信息
 */
const loadStatistics = async () => {
  try {
    const response = await rlAPI.getStatistics()

    if (response.code === 200) {
      stats.value = response.data
    }
  } catch (error: any) {
    console.error('加载统计信息失败:', error)
  }
}

/**
 * 搜索处理
 */
const handleSearch = () => {
  currentPage.value = 1
}

/**
 * 过滤处理
 */
const handleFilter = () => {
  currentPage.value = 1
}

/**
 * 分页大小变化
 */
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

/**
 * 页码变化
 */
const handlePageChange = (page: number) => {
  currentPage.value = page
}

/**
 * 查看模型详情
 */
const viewModelDetails = async (model: RLModelInfo) => {
  try {
    const response = await rlAPI.getModelDetails(model.training_id)

    if (response.code === 200) {
      selectedModel.value = model
      selectedModelDetail.value = response.data
      detailDialogVisible.value = true

      // 初始化图表
      await nextTick()
      initTrainingChart()
    }
  } catch (error: any) {
    console.error('加载模型详情失败:', error)
    ElMessage.error('加载模型详情失败')
  }
}

/**
 * 导出模型
 */
const exportModel = async (model: RLModelInfo) => {
  try {
    ElMessage.info('准备导出模型...')

    // 调用保存API
    const response = await rlAPI.saveModel(model.training_id)

    if (response.code === 200) {
      ElMessage.success('模型导出成功')
    }
  } catch (error: any) {
    console.error('导出模型失败:', error)
    ElMessage.error('导出模型失败')
  }
}

/**
 * 删除模型
 */
const deleteModel = async (model: RLModelInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 ${model.training_id} 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // TODO: 调用删除API
    ElMessage.success('模型已删除')
    await loadModels()
  } catch (error) {
    // 用户取消
  }
}

/**
 * 保存当前模型
 */
const saveCurrentModel = async () => {
  if (!selectedModel.value) return

  try {
    saving.value = true

    const response = await rlAPI.saveModel(selectedModel.value.training_id)

    if (response.code === 200) {
      ElMessage.success('模型保存成功')
      await loadModels()
    }
  } catch (error: any) {
    console.error('保存模型失败:', error)
    ElMessage.error('保存模型失败')
  } finally {
    saving.value = false
  }
}

/**
 * 获取算法标签类型
 */
const getAlgorithmTagType = (algorithm: string) => {
  const types: Record<string, any> = {
    'PPO': '',
    'DQN': 'success',
    'A2C': 'warning'
  }
  return types[algorithm] || 'info'
}

/**
 * 获取奖励样式类
 */
const getRewardClass = (reward: number) => {
  if (reward >= 0.8) return 'reward-excellent'
  if (reward >= 0.6) return 'reward-good'
  if (reward >= 0.4) return 'reward-average'
  return 'reward-poor'
}

/**
 * 获取状态标签类型
 */
const getStatusType = (status: string) => {
  if (status === 'completed') return 'success'
  if (status === 'running') return 'warning'
  if (status === 'failed') return 'danger'
  return 'info'
}

/**
 * 格式化场景
 */
const formatScenario = (scenario: string) => {
  const names: Record<string, string> = {
    'order_execution': '订单执行',
    'portfolio_construction': '投资组合构建'
  }
  return names[scenario] || scenario
}

/**
 * 格式化状态
 */
const formatStatus = (status: string) => {
  const names: Record<string, string> = {
    'completed': '已完成',
    'running': '训练中',
    'failed': '失败',
    'pending': '等待中'
  }
  return names[status] || status
}

/**
 * 格式化日期时间
 */
const formatDateTime = (datetime: string) => {
  if (!datetime) return 'N/A'
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN')
}

/**
 * 格式化时长
 */
const formatDuration = (seconds: number) => {
  if (!seconds) return 'N/A'

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
 * 初始化训练曲线图表
 */
const initTrainingChart = () => {
  if (!trainingChartRef.value || !selectedModelDetail.value?.training_history) return

  chart = echarts.init(trainingChartRef.value)

  const history = selectedModelDetail.value.training_history
  const episodes = history.map((h: any) => h.episode)
  const rewards = history.map((h: any) => h.reward)

  const option = {
    title: {
      text: '训练奖励曲线',
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
      axisLabel: { color: '#94a3b8' },
      data: episodes
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
      data: rewards,
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
  loadModels()
})
</script>

<style scoped lang="scss">
.rl-model-management-view {
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

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;

  .stat-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-light);

    :deep(.el-card__body) {
      padding: 16px;
    }

    .stat-content {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: var(--radius-lg);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      font-weight: 700;
      color: white;

      &.total {
        background: linear-gradient(135deg, #8b5cf6, #3b82f6);
      }

      &.ppo {
        background: linear-gradient(135deg, #f59e0b, #ef4444);
      }

      &.dqn {
        background: linear-gradient(135deg, #10b981, #059669);
      }

      &.a2c {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
      }
    }

    .stat-info {
      .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
      }

      .stat-label {
        font-size: 13px;
        color: var(--text-muted);
        margin-top: 4px;
      }
    }
  }
}

.main-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);

  :deep(.el-card__header) {
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border-light);
    padding: 12px 16px;
  }

  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .toolbar-left {
      display: flex;
      gap: 12px;
    }

    .toolbar-right {
      .total-info {
        font-size: 14px;
        color: var(--text-muted);
      }
    }
  }

  :deep(.el-card__body) {
    padding: 0;
  }

  :deep(.el-table) {
    background: transparent;

    .el-table__row {
      cursor: pointer;

      &:hover {
        background: var(--bg-hover);
      }
    }
  }
}

.pagination-container {
  padding: 16px;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border-light);
}

// 奖励样式
.reward-excellent { color: #10b981; font-weight: 700; }
.reward-good { color: #8b5cf6; font-weight: 600; }
.reward-average { color: #f59e0b; font-weight: 500; }
.reward-poor { color: var(--text-muted); }

// 详情对话框
.model-detail-content {
  .detail-section {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    .section-title {
      margin: 0 0 12px 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-light);
    }

    .detail-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;

      .detail-item {
        padding: 10px;
        background: var(--bg-elevated);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-light);

        &.full-width {
          grid-column: 1 / -1;
        }

        .detail-label {
          display: block;
          font-size: 12px;
          color: var(--text-muted);
          margin-bottom: 4px;
        }

        .detail-value {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
          word-break: break-all;

          &.highlight {
            color: #8b5cf6;
            font-weight: 600;
            font-size: 16px;
          }

          &.monospace {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
          }
        }
      }
    }

    .chart-container {
      height: 300px;
      margin-top: 12px;
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
