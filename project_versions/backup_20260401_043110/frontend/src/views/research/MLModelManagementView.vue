<template>
  <div class="ml-management-view">
    <GlobalNavBar />

    <!-- 页面头部 -->
    <div class="view-header">
      <div class="header-left">
        <h2 class="view-title">ML模型管理</h2>
        <p class="view-subtitle">管理和查看训练好的模型</p>
      </div>
      <div class="header-right">
        <el-button type="info" @click="startCompare" :disabled="selectedModels.length < 2">
          <el-icon><Connection /></el-icon>
          <span>对比模型 ({{ selectedModels.length }})</span>
        </el-button>
        <el-button type="danger" @click="batchDeleteModels" :disabled="selectedModels.length === 0">
          <el-icon><Delete /></el-icon>
          <span>批量删除 ({{ selectedModels.length }})</span>
        </el-button>
        <el-button type="primary" @click="refreshModels">
          <el-icon><Refresh /></el-icon>
          <span>刷新列表</span>
        </el-button>
        <el-button @click="goToTraining">
          <el-icon><Plus /></el-icon>
          <span>训练新模型</span>
        </el-button>
      </div>
    </div>

    <!-- 过滤器 -->
    <div class="filter-bar">
      <el-card shadow="hover">
        <div class="filter-content">
          <div class="filter-item">
            <span class="filter-label">模型类型</span>
            <el-select
              v-model="filters.model_type"
              placeholder="全部"
              clearable
              @change="applyFilters"
            >
              <el-option label="LightGBM" value="lightgbm" />
              <el-option label="XGBoost" value="xgboost" />
              <el-option label="Random Forest" value="random_forest" />
              <el-option label="Linear" value="linear" />
              <el-option label="LSTM" value="lstm" />
              <el-option label="GRU" value="gru" />
              <el-option label="MLP" value="mlp" />
            </el-select>
          </div>

          <div class="filter-item">
            <span class="filter-label">任务类型</span>
            <el-select
              v-model="filters.task_type"
              placeholder="全部"
              clearable
              @change="applyFilters"
            >
              <el-option label="分类" value="classification" />
              <el-option label="回归" value="regression" />
            </el-select>
          </div>

          <div class="filter-item">
            <span class="filter-label">训练状态</span>
            <el-select
              v-model="filters.status"
              placeholder="全部"
              clearable
              @change="applyFilters"
            >
              <el-option label="已完成" value="completed" />
              <el-option label="训练中" value="training" />
              <el-option label="失败" value="failed" />
              <el-option label="待处理" value="pending" />
            </el-select>
          </div>

          <div class="filter-item">
            <el-input
              v-model="searchText"
              placeholder="搜索模型ID..."
              prefix-icon="Search"
              clearable
              @input="onSearch"
            />
          </div>
        </div>
      </el-card>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ totalModels }}</span>
          <span class="stat-label">总模型数</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ completedModels }}</span>
          <span class="stat-label">已完成</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon warning">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ trainingModels }}</span>
          <span class="stat-label">训练中</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon danger">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ failedModels }}</span>
          <span class="stat-label">失败</span>
        </div>
      </div>
    </div>

    <!-- 模型列表 -->
    <div class="models-container">
      <el-table
        v-loading="loading"
        :data="filteredModels"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />

        <el-table-column prop="model_id" label="模型ID" width="200" sortable>
          <template #default="{ row }">
            <span class="model-id">{{ row.model_id.substring(0, 16) }}...</span>
          </template>
        </el-table-column>

        <el-table-column prop="model_type" label="模型类型" width="120" sortable>
          <template #default="{ row }">
            <el-tag size="small">{{ getModelTypeLabel(row.model_type) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="task_type" label="任务类型" width="100" sortable>
          <template #default="{ row }">
            <el-tag size="small" :type="row.task_type === 'classification' ? 'success' : 'warning'">
              {{ row.task_type === 'classification' ? '分类' : '回归' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="label_type" label="标签类型" width="100" sortable />

        <el-table-column prop="feature_count" label="特征数" width="80" sortable>
          <template #default="{ row }">
            <span class="feature-count">{{ row.feature_count }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="sample_count" label="样本数" width="100" sortable>
          <template #default="{ row }">
            <span class="sample-count">{{ formatNumber(row.sample_count) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="horizon" label="周期" width="70" sortable>
          <template #default="{ row }">
            <span>{{ row.horizon }}天</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100" sortable>
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="110" sortable>
          <template #default="{ row }">
            <span class="created-time">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                type="primary"
                size="small"
                link
                @click="viewDetails(row)"
              >
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button
                type="success"
                size="small"
                link
                :disabled="row.status !== 'completed'"
                @click="useForPrediction(row)"
              >
                <el-icon><TrendCharts /></el-icon>
                预测
              </el-button>
              <el-button
                type="warning"
                size="small"
                link
                :disabled="row.status !== 'completed'"
                @click="evaluateModel(row)"
              >
                <el-icon><DataAnalysis /></el-icon>
                评估
              </el-button>
              <el-button
                type="danger"
                size="small"
                link
                @click="deleteModel(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-empty
        v-if="filteredModels.length === 0 && !loading"
        description="暂无模型数据"
        :image-size="120"
      >
        <el-button type="primary" @click="goToTraining">训练第一个模型</el-button>
      </el-empty>
    </div>

    <!-- 模型详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="`模型详情 - ${selectedModel?.model_id || ''}`"
      width="900px"
    >
      <div v-if="selectedModel" class="model-detail-content">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4 class="section-title">基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">模型ID</span>
              <span class="info-value">{{ selectedModel.model_id }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">模型类型</span>
              <span class="info-value">{{ getModelTypeLabel(selectedModel.model_type) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">任务类型</span>
              <span class="info-value">{{ selectedModel.task_type === 'classification' ? '分类' : '回归' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">标签类型</span>
              <span class="info-value">{{ selectedModel.label_type }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">训练状态</span>
              <el-tag :type="getStatusType(selectedModel.status)">
                {{ getStatusLabel(selectedModel.status) }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatFullDate(selectedModel.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- 数据配置 -->
        <div class="detail-section">
          <h4 class="section-title">数据配置</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">数据范围</span>
              <span class="info-value">
                {{ selectedModel.data_range?.start_date }} ~ {{ selectedModel.data_range?.end_date }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">特征数量</span>
              <span class="info-value">{{ selectedModel.feature_count }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">样本数量</span>
              <span class="info-value">{{ formatNumber(selectedModel.sample_count) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">预测周期</span>
              <span class="info-value">{{ selectedModel.horizon }} 天</span>
            </div>
          </div>
        </div>

        <!-- 性能指标 -->
        <div v-if="selectedModel.performance_metrics" class="detail-section">
          <h4 class="section-title">性能指标</h4>
          <div class="metrics-grid">
            <template v-if="selectedModel.task_type === 'classification'">
              <div class="metric-card">
                <span class="metric-label">准确率</span>
                <span class="metric-value">{{ formatMetric(selectedModel.performance_metrics.accuracy) }}</span>
              </div>
              <div class="metric-card">
                <span class="metric-label">精确率</span>
                <span class="metric-value">{{ formatMetric(selectedModel.performance_metrics.precision) }}</span>
              </div>
              <div class="metric-card">
                <span class="metric-label">召回率</span>
                <span class="metric-value">{{ formatMetric(selectedModel.performance_metrics.recall) }}</span>
              </div>
              <div class="metric-card">
                <span class="metric-label">F1分数</span>
                <span class="metric-value">{{ formatMetric(selectedModel.performance_metrics.f1) }}</span>
              </div>
            </template>

            <template v-if="selectedModel.task_type === 'regression'">
              <div class="metric-card">
                <span class="metric-label">MSE</span>
                <span class="metric-value">{{ formatMetric(selectedModel.performance_metrics.mse) }}</span>
              </div>
              <div class="metric-card">
                <span class="metric-label">MAE</span>
                <span class="metric-value">{{ formatMetric(selectedModel.performance_metrics.mae) }}</span>
              </div>
              <div class="metric-card">
                <span class="metric-label">R²</span>
                <span class="metric-value">{{ formatMetric(selectedModel.performance_metrics.r2) }}</span>
              </div>
            </template>

            <div class="metric-card">
              <span class="metric-label">IC</span>
              <span class="metric-value">{{ formatMetric(selectedModel.performance_metrics.ic) }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">RankIC</span>
              <span class="metric-value">{{ formatMetric(selectedModel.performance_metrics.rank_ic) }}</span>
            </div>
          </div>
        </div>

        <!-- 特征重要性 -->
        <div v-if="selectedModel.feature_importance" class="detail-section">
          <h4 class="section-title">特征重要性 (Top 10)</h4>
          <div class="feature-list">
            <div
              v-for="(item, index) in sortedFeatures"
              :key="item.feature"
              class="feature-item"
            >
              <span class="feature-rank">{{ index + 1 }}</span>
              <span class="feature-name">{{ item.feature }}</span>
              <el-progress
                :percentage="item.importance * 100"
                :show-text="false"
                :stroke-width="8"
                :color="getFeatureColor(item.importance)"
              />
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="exportModel">导出模型</el-button>
      </template>
    </el-dialog>

    <!-- 评估结果对话框 -->
    <el-dialog
      v-model="evaluateDialogVisible"
      title="模型评估"
      width="600px"
    >
      <div v-if="evaluateResult" class="evaluate-result">
        <div class="metrics-grid">
          <div class="metric-card">
            <span class="metric-label">准确率</span>
            <span class="metric-value">{{ formatMetric(evaluateResult.accuracy) }}</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">IC</span>
            <span class="metric-value">{{ formatMetric(evaluateResult.ic) }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="evaluateDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="exportEvaluation">导出报告</el-button>
      </template>
    </el-dialog>

    <!-- 模型对比对话框 -->
    <el-dialog
      v-model="compareDialogVisible"
      title="模型性能对比"
      width="900px"
    >
      <div v-if="compareModels.length > 0" class="compare-container">
        <el-table :data="compareModels" stripe>
          <el-table-column prop="model_id" label="模型ID" width="180" />
          <el-table-column prop="model_type" label="模型类型" width="120" />
          <el-table-column prop="task_type" label="任务类型" width="100" />
          <el-table-column label="IC" width="100">
            <template #default="{ row }">
              {{ compareResults[row.model_id]?.performance_metrics?.ic?.toFixed(4) || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="RankIC" width="100">
            <template #default="{ row }">
              {{ compareResults[row.model_id]?.performance_metrics?.rank_ic?.toFixed(4) || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="准确率" width="100">
            <template #default="{ row }">
              {{ compareResults[row.model_id]?.performance_metrics?.accuracy?.toFixed(4) || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="AUC" width="100">
            <template #default="{ row }">
              {{ compareResults[row.model_id]?.performance_metrics?.auc_roc?.toFixed(4) || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="训练时间" />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="compareDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import GlobalNavBar from '@/components/GlobalNavBar.vue'
import {
  Refresh, Plus, View, TrendCharts, DataAnalysis, Delete, Box,
  CircleCheck, Loading, CircleClose, Search, Connection
} from '@element-plus/icons-vue'
import { mlAPI, type MLModelInfo } from '@/api/research'

// ==================== 路由 ====================

const router = useRouter()

// ==================== 数据 ====================

const models = ref<MLModelInfo[]>([])
const loading = ref(false)
const selectedModels = ref<MLModelInfo[]>([])

// 过滤器
const filters = ref({
  model_type: undefined as string | undefined,
  task_type: undefined as string | undefined,
  status: undefined as string | undefined
})

const searchText = ref('')

// 对话框
const detailDialogVisible = ref(false)
const evaluateDialogVisible = ref(false)
const compareDialogVisible = ref(false)
const selectedModel = ref<(MLModelInfo & {
  performance_metrics?: any
  feature_importance?: Record<string, number>
}) | null>(null)
const evaluateResult = ref<any>(null)

// 模型对比数据
const compareModels = ref<MLModelInfo[]>([])
const compareResults = ref<Record<string, any>>({})

// ==================== 计算属性 ====================

const filteredModels = computed(() => {
  let result = [...models.value]

  // 应用过滤器
  if (filters.value.model_type) {
    result = result.filter(m => m.model_type === filters.value.model_type)
  }
  if (filters.value.task_type) {
    result = result.filter(m => m.task_type === filters.value.task_type)
  }
  if (filters.value.status) {
    result = result.filter(m => m.status === filters.value.status)
  }

  // 应用搜索
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(m =>
      m.model_id.toLowerCase().includes(search)
    )
  }

  return result
})

const totalModels = computed(() => models.value.length)
const completedModels = computed(() => models.value.filter(m => m.status === 'completed').length)
const trainingModels = computed(() => models.value.filter(m => m.status === 'training').length)
const failedModels = computed(() => models.value.filter(m => m.status === 'failed').length)

const sortedFeatures = computed(() => {
  if (!selectedModel.value?.feature_importance) return []
  return Object.entries(selectedModel.value.feature_importance)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .map(([feature, importance]) => ({ feature, importance }))
})

// ==================== 方法 ====================

/**
 * 获取模型类型标签
 */
const getModelTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    lightgbm: 'LightGBM',
    xgboost: 'XGBoost',
    random_forest: 'RF',
    linear: 'Linear',
    lstm: 'LSTM',
    gru: 'GRU',
    mlp: 'MLP'
  }
  return labels[type] || type
}

/**
 * 获取状态类型
 */
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    completed: 'success',
    training: 'warning',
    failed: 'danger',
    pending: 'info'
  }
  return typeMap[status] || 'info'
}

/**
 * 获取状态标签
 */
const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    completed: '已完成',
    training: '训练中',
    failed: '失败',
    pending: '待处理'
  }
  return labels[status] || status
}

/**
 * 格式化数字
 */
const formatNumber = (num: number) => {
  if (num >= 10000) return `${(num / 10000).toFixed(1)}万`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}k`
  return num.toString()
}

/**
 * 格式化指标
 */
const formatMetric = (val?: number) => {
  if (val === undefined || val === null) return '--'
  return val.toFixed(4)
}

/**
 * 格式化日期
 */
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 格式化完整日期
 */
const formatFullDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

/**
 * 获取特征颜色
 */
const getFeatureColor = (importance: number) => {
  if (importance > 0.1) return '#ef4444'
  if (importance > 0.05) return '#f59e0b'
  return '#8b5cf6'
}

/**
 * 加载模型列表
 */
const loadModels = async () => {
  try {
    loading.value = true
    const response = await mlAPI.getModels()
    if (response.code === 200) {
      models.value = response.data.models
    }
  } catch (error) {
    console.error('加载模型列表失败:', error)
    ElMessage.error('加载模型列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 刷新列表
 */
const refreshModels = () => {
  loadModels()
  ElMessage.success('已刷新')
}

/**
 * 应用过滤器
 */
const applyFilters = () => {
  // 过滤器通过computed自动应用
}

/**
 * 搜索
 */
const onSearch = () => {
  // 搜索通过computed自动应用
}

/**
 * 多选变更
 */
const handleSelectionChange = (selection: MLModelInfo[]) => {
  selectedModels.value = selection
}

/**
 * 查看详情
 */
const viewDetails = async (model: MLModelInfo) => {
  try {
    const response = await mlAPI.getModelDetails(model.model_id)
    if (response.code === 200) {
      selectedModel.value = response.data
      detailDialogVisible.value = true
    }
  } catch (error) {
    console.error('获取模型详情失败:', error)
    ElMessage.error('获取模型详情失败')
  }
}

/**
 * 用于预测
 */
const useForPrediction = (model: MLModelInfo) => {
  router.push({
    name: 'MLModelPrediction',
    query: { model_id: model.model_id }
  })
}

/**
 * 评估模型
 */
const evaluateModel = async (model: MLModelInfo) => {
  try {
    const response = await mlAPI.evaluateModel(model.model_id)
    if (response.code === 200) {
      evaluateResult.value = response.data
      evaluateDialogVisible.value = true
    }
  } catch (error) {
    console.error('评估模型失败:', error)
    ElMessage.error('评估模型失败')
  }
}

/**
 * 删除模型
 */
const deleteModel = async (model: MLModelInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 ${model.model_id} 吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 调用删除API
    await mlAPI.deleteModel(model.model_id)
    ElMessage.success('模型已删除')

    // 重新加载列表
    await loadModels()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

/**
 * 导出模型
 */
const exportModel = async () => {
  // 优先导出选中的模型，如果没有选中则导出当前查看的模型
  const modelToExport = selectedModels.value[0] || selectedModel.value

  if (!modelToExport) {
    ElMessage.warning('请先选择一个模型')
    return
  }

  try {
    const response = await mlAPI.exportModel(modelToExport.model_id)

    if (response.code === 200) {
      ElMessage.success(`模型已导出到: ${response.data.export_path}`)
    } else {
      ElMessage.error('导出失败: ' + response.message)
    }
  } catch (error: any) {
    ElMessage.error('导出失败: ' + (error.message || '未知错误'))
  }
}

/**
 * 导出评估报告
 */
const exportEvaluation = () => {
  const modelToExport = selectedModels.value[0] || selectedModel.value

  if (!modelToExport) {
    ElMessage.warning('请先选择一个模型')
    return
  }

  // 生成评估报告
  const report = {
    model_id: modelToExport.model_id,
    model_type: modelToExport.model_type,
    task_type: modelToExport.task_type,
    created_at: modelToExport.created_at,
    performance_metrics: modelToExport.performance_metrics,
    data_range: modelToExport.data_range,
  }

  // 转换为JSON并下载
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `evaluation_${modelToExport.model_id}_${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('评估报告已导出')
}

/**
 * 对比模型
 */
const startCompare = async () => {
  const selection = selectedModels.value

  if (selection.length < 2) {
    ElMessage.warning('请至少选择2个模型进行对比')
    return
  }

  if (selection.length > 4) {
    ElMessage.warning('最多支持4个模型对比')
    return
  }

  try {
    // 获取每个模型的详细信息
    compareModels.value = selection
    const results: Record<string, any> = {}

    for (const model of selection) {
      try {
        const response = await mlAPI.getModelDetails(model.model_id)
        if (response.code === 200) {
          results[model.model_id] = response.data
        }
      } catch (e) {
        console.error(`获取模型详情失败: ${model.model_id}`, e)
      }
    }

    compareResults.value = results
    compareDialogVisible.value = true
  } catch (error) {
    console.error('模型对比失败:', error)
    ElMessage.error('模型对比失败')
  }
}

/**
 * 批量删除模型
 */
const batchDeleteModels = async () => {
  const selection = selectedModels.value

  if (selection.length === 0) {
    ElMessage.warning('请先选择要删除的模型')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selection.length} 个模型吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    loading.value = true
    const deleteResults: { model_id: string; success: boolean; message: string }[] = []

    for (const model of selection) {
      try {
        const response = await mlAPI.deleteModel(model.model_id)
        if (response.code === 200) {
          deleteResults.push({ model_id: model.model_id, success: true, message: '删除成功' })
        } else {
          deleteResults.push({ model_id: model.model_id, success: false, message: response.message || '删除失败' })
        }
      } catch (e) {
        deleteResults.push({ model_id: model.model_id, success: false, message: String(e) })
      }
    }

    const successCount = deleteResults.filter(r => r.success).length
    const failCount = deleteResults.filter(r => !r.success).length

    if (failCount > 0) {
      ElMessage.warning(`删除完成：成功 ${successCount} 个，失败 ${failCount} 个`)
    } else {
      ElMessage.success(`成功删除 ${successCount} 个模型`)
    }

    // 重新加载模型列表
    await loadModels()
    // 清空选择
    selectedModels.value = []
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 前往训练页面
 */
const goToTraining = () => {
  router.push({ name: 'MLModelTraining' })
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped lang="scss">
.ml-management-view {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 0;
  color: var(--text-primary);
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: var(--bg-secondary);
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

  .header-right {
    display: flex;
    gap: 12px;
  }
}

.filter-bar {
  margin: 0 20px;
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 16px;
  }

  .filter-content {
    display: flex;
    gap: 16px;
    align-items: center;

    .filter-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .filter-label {
        font-size: 14px;
        color: var(--text-secondary);
        white-space: nowrap;
      }
    }
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 0 20px;
  margin-bottom: 20px;

  .stat-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;

    .stat-icon {
      width: 50px;
      height: 50px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;

      &.total {
        background: rgba(41, 98, 255, 0.1);
        color: var(--accent-blue);
      }

      &.success {
        background: rgba(16, 185, 129, 0.1);
        color: var(--accent-green);
      }

      &.warning {
        background: rgba(245, 158, 11, 0.1);
        color: var(--accent-orange);
      }

      &.danger {
        background: rgba(239, 68, 68, 0.1);
        color: var(--accent-red);
      }
    }

    .stat-content {
      display: flex;
      flex-direction: column;
      gap: 4px;

      .stat-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--text-primary);
      }

      .stat-label {
        font-size: 13px;
        color: var(--text-secondary);
      }
    }
  }
}

.models-container {
  margin: 0 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 16px;

  .model-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--text-secondary);
  }

  .feature-count,
  .sample-count {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
  }

  .created-time {
    font-size: 12px;
    color: var(--text-muted);
  }

  .action-buttons {
    display: flex;
    gap: 4px;
  }
}

.model-detail-content {
  .detail-section {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 16px 0;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-light);
    }

    .info-grid,
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;

      .info-item,
      .metric-card {
        padding: 12px;
        background: var(--bg-elevated);
        border-radius: var(--radius-sm);
        display: flex;
        flex-direction: column;
        gap: 4px;

        .info-label,
        .metric-label {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .info-value,
        .metric-value {
          font-weight: 500;
          color: var(--text-primary);
        }
      }
    }
  }

  .feature-list {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .feature-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px;
      background: var(--bg-elevated);
      border-radius: var(--radius-sm);

      .feature-rank {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--primary);
        color: white;
        border-radius: var(--radius-sm);
        font-size: 12px;
        font-weight: 600;
        flex-shrink: 0;
      }

      .feature-name {
        flex: 1;
        font-size: 13px;
        color: var(--text-primary);
      }
    }
  }
}

.evaluate-result {
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;

    .metric-card {
      padding: 16px;
      background: var(--bg-elevated);
      border-radius: var(--radius-md);
      display: flex;
      flex-direction: column;
      gap: 4px;

      .metric-label {
        font-size: 12px;
        color: var(--text-secondary);
      }

      .metric-value {
        font-size: 20px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-primary);
      }
    }
  }
}

// 滚动条样式
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-elevated);
  border-radius: var(--radius-full);

  &:hover {
    background: var(--border-strong);
  }
}
</style>
