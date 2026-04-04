<template>
  <div class="ml-prediction-view">
    <!-- 页面头部 -->
    <div class="view-header">
      <div class="header-left">
        <h2 class="view-title">ML模型预测</h2>
        <p class="view-subtitle">使用训练好的模型进行预测</p>
      </div>
      <div class="header-right">
        <el-button @click="historyDialogVisible = true" :disabled="predictionHistory.length === 0">
          <el-icon><Clock /></el-icon>
          <span>历史记录 ({{ predictionHistory.length }})</span>
        </el-button>
        <el-button
          type="primary"
          :loading="predicting"
          :disabled="!canPredict"
          @click="startPrediction"
        >
          <el-icon v-if="!predicting"><TrendCharts /></el-icon>
          <span>{{ predicting ? '预测中...' : '开始预测' }}</span>
        </el-button>
        <el-button @click="exportResults" :disabled="!predictionResult">
          <el-icon><Download /></el-icon>
          <span>导出结果</span>
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="view-content">
      <!-- 左侧：配置面板 -->
      <div class="config-panel">
        <!-- 模型选择 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Box /></el-icon>
              <span>模型选择</span>
            </div>
          </template>

          <el-form label-width="100px" label-position="left">
            <el-form-item label="选择模型">
              <el-select
                v-model="selectedModelId"
                placeholder="选择训练好的模型"
                filterable
                @change="onModelChange"
                style="width: 100%"
              >
                <el-option
                  v-for="model in models"
                  :key="model.model_id"
                  :label="`${model.model_type} - ${model.task_type}`"
                  :value="model.model_id"
                >
                  <div class="model-option">
                    <span class="model-type">{{ model.model_type }}</span>
                    <span class="model-task">{{ model.task_type }}</span>
                    <el-tag size="small" :type="getStatusType(model.status)">
                      {{ model.status }}
                    </el-tag>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <div v-if="selectedModel" class="model-info">
              <div class="info-item">
                <span class="info-label">模型类型</span>
                <span class="info-value">{{ selectedModel.model_type }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">任务类型</span>
                <span class="info-value">{{ selectedModel.task_type }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">标签类型</span>
                <span class="info-value">{{ selectedModel.label_type }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">特征数量</span>
                <span class="info-value">{{ selectedModel.feature_count }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">预测周期</span>
                <span class="info-value">{{ selectedModel.horizon }}天</span>
              </div>
              <div class="info-item">
                <span class="info-label">训练时间</span>
                <span class="info-value">{{ formatDate(selectedModel.created_at) }}</span>
              </div>
            </div>
          </el-form>
        </el-card>

        <!-- 预测配置 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>预测配置</span>
            </div>
          </template>

          <el-form :model="form" label-width="100px" label-position="left">
            <!-- 股票池 -->
            <el-form-item label="股票代码">
              <el-select
                v-model="form.instruments"
                multiple
                filterable
                allow-create
                placeholder="输入股票代码"
                style="width: 100%"
              >
                <el-option
                  v-for="stock in stockOptions"
                  :key="stock"
                  :label="stock"
                  :value="stock"
                />
              </el-select>
            </el-form-item>

            <!-- 日期范围 -->
            <el-form-item label="预测日期">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>

            <!-- 批量预测模式 -->
            <el-form-item label="预测模式">
              <el-radio-group v-model="predictionMode">
                <el-radio-button label="single">单次预测</el-radio-button>
                <el-radio-button label="batch">批量预测</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <!-- 批量配置 -->
            <template v-if="predictionMode === 'batch'">
              <el-form-item label="滚动窗口">
                <el-input-number
                  v-model="batchConfig.rolling_window"
                  :min="1"
                  :max="252"
                  :step="1"
                  controls-position="right"
                  style="width: 100%"
                />
                <span style="margin-left: 8px; color: var(--text-muted);">天</span>
              </el-form-item>

              <el-form-item label="滚动步长">
                <el-input-number
                  v-model="batchConfig.roll_step"
                  :min="1"
                  :max="20"
                  :step="1"
                  controls-position="right"
                  style="width: 100%"
                />
                <span style="margin-left: 8px; color: var(--text-muted);">天</span>
              </el-form-item>
            </template>
          </el-form>
        </el-card>

        <!-- 预测结果概览 -->
        <el-card v-if="predictionResult" class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataLine /></el-icon>
              <span>预测概览</span>
            </div>
          </template>

          <div class="prediction-summary">
            <div class="summary-item">
              <span class="summary-label">预测数量</span>
              <span class="summary-value">{{ predictionResult.predictions?.length || 0 }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">预测时间</span>
              <span class="summary-value">{{ formatDate(predictionResult.timestamp) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">预测范围</span>
              <span class="summary-value">{{ form.start_date }} ~ {{ form.end_date }}</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧：预测结果表格 -->
      <div class="results-panel">
        <el-card class="results-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><List /></el-icon>
              <span>预测结果</span>
              <el-input
                v-model="searchText"
                placeholder="搜索股票..."
                prefix-icon="Search"
                size="small"
                style="width: 200px"
              />
            </div>
          </template>

          <div class="results-content">
            <el-table
              :data="filteredPredictions"
              stripe
              :max-height="600"
              style="width: 100%"
            >
              <el-table-column prop="instrument" label="股票代码" width="120" sortable />
              <el-table-column prop="date" label="预测日期" width="120" sortable />
              <el-table-column label="预测值" width="150" sortable>
                <template #default="{ row }">
                  <span :class="getPredictionClass(row)">
                    {{ formatPrediction(row) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column v-if="selectedModel?.task_type === 'classification'" label="概率" width="120" sortable>
                <template #default="{ row }">
                  <span :class="getProbabilityClass(row)">
                    {{ formatProbability(row) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="信号" width="100">
                <template #default="{ row }">
                  <el-tag :type="getSignalType(row)" size="small">
                    {{ getSignal(row) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    size="small"
                    link
                    @click="viewDetail(row)"
                  >
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-empty
              v-if="filteredPredictions.length === 0"
              description="暂无预测数据"
              :image-size="100"
            />
          </div>
        </el-card>

        <!-- 预测分布图 -->
        <el-card v-if="predictionResult" class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>预测分布</span>
            </div>
          </template>

          <div ref="chartRef" class="chart-container"></div>
        </el-card>
      </div>
    </div>

    <!-- 预测详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="预测详情"
      width="600px"
    >
      <div v-if="selectedPrediction" class="prediction-detail">
        <div class="detail-grid">
          <div class="detail-row">
            <span class="detail-label">股票代码</span>
            <span class="detail-value">{{ selectedPrediction.instrument }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">预测日期</span>
            <span class="detail-value">{{ selectedPrediction.date }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">预测值</span>
            <span class="detail-value">{{ formatPrediction(selectedPrediction) }}</span>
          </div>
          <div v-if="selectedPrediction.probability !== undefined" class="detail-row">
            <span class="detail-label">预测概率</span>
            <span class="detail-value">{{ formatProbability(selectedPrediction) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">信号</span>
            <el-tag :type="getSignalType(selectedPrediction)">
              {{ getSignal(selectedPrediction) }}
            </el-tag>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 预测历史对话框 -->
    <el-dialog
      v-model="historyDialogVisible"
      title="预测历史"
      width="700px"
    >
      <div class="history-dialog-content">
        <div class="history-actions">
          <el-button size="small" type="danger" @click="clearHistory" :disabled="predictionHistory.length === 0">
            清空历史
          </el-button>
        </div>

        <el-table :data="predictionHistory" max-height="400" stripe>
          <el-table-column label="时间" width="160">
            <template #default="{ row }">
              {{ formatHistoryTime(row.timestamp) }}
            </template>
          </el-table-column>
          <el-table-column prop="modelType" label="模型类型" width="100" />
          <el-table-column prop="stockCount" label="股票数" width="80" />
          <el-table-column prop="dateRange" label="日期范围" width="180" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="loadFromHistory(row)">
                加载
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="predictionHistory.length === 0" description="暂无预测历史" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts, Setting, Box, DataLine, List, Download, Search, Clock
} from '@element-plus/icons-vue'
import { mlAPI, type MLPredictionRequest, type MLPredictionResult, type MLModelInfo } from '@/api/research'
import { getStockList } from '@/api/market'
import * as echarts from 'echarts'

// ==================== 常量 ====================

// 常用股票池（备用）
const COMMON_STOCKS = [
  '000001.SZ', '000002.SZ', '600000.SH', '600036.SH',
  '600519.SH', '000858.SZ', '601318.SH', '600276.SH',
  '600887.SH', '601166.SH', '600030.SH', '601398.SH',
  '600016.SH', '601288.SH', '601088.SH', '600028.SH',
  '601857.SH', '600309.SH', '600900.SH', '601688.SH'
]

// ==================== 表单数据 ====================

const selectedModelId = ref<string>('')
const selectedModel = ref<MLModelInfo | null>(null)

const form = ref<MLPredictionRequest>({
  model_id: '',
  instruments: COMMON_STOCKS.slice(0, 5),
  start_date: '',
  end_date: '',
  features: undefined
})

const dateRange = ref<[Date, Date]>([
  new Date('2024-01-01'),
  new Date('2024-01-31')
])

const predictionMode = ref<'single' | 'batch'>('single')
const batchConfig = ref({
  rolling_window: 20,
  roll_step: 5
})

const searchText = ref('')

// ==================== 预测状态 ====================

const predicting = ref(false)
const predictionResult = ref<MLPredictionResult | null>(null)
const models = ref<MLModelInfo[]>([])

// ==================== 预测历史 ====================

interface PredictionHistoryItem {
  id: string
  modelId: string
  modelType: string
  timestamp: Date
  stockCount: number
  dateRange: string
  result: MLPredictionResult | null
}

const predictionHistory = ref<PredictionHistoryItem[]>([])
const historyDialogVisible = ref(false)

const addToHistory = (result: MLPredictionResult | null) => {
  if (!result || !selectedModelId.value) return

  const model = models.value.find(m => m.model_id === selectedModelId.value)
  const historyItem: PredictionHistoryItem = {
    id: `pred_${Date.now()}`,
    modelId: selectedModelId.value,
    modelType: model?.model_type || 'Unknown',
    timestamp: new Date(),
    stockCount: result.predictions?.length || 0,
    dateRange: `${form.value.start_date} ~ ${form.value.end_date}`,
    result
  }

  predictionHistory.value.unshift(historyItem)

  // 最多保留50条历史
  if (predictionHistory.value.length > 50) {
    predictionHistory.value = predictionHistory.value.slice(0, 50)
  }
}

const loadFromHistory = (item: PredictionHistoryItem) => {
  if (item.result) {
    predictionResult.value = item.result
    selectedModelId.value = item.modelId
  }
  historyDialogVisible.value = false
}

const clearHistory = () => {
  predictionHistory.value = []
  ElMessage.success('历史记录已清空')
}

const formatHistoryTime = (date: Date) => {
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// ==================== 对话框 ====================

const detailDialogVisible = ref(false)
const selectedPrediction = ref<{
  instrument: string
  date: string
  prediction: number
  probability?: number
} | null>(null)

// ==================== 图表 ====================

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

// ==================== 计算属性 ====================

// 股票选项（从API加载或使用常用股票）
const stockOptions = ref<string[]>(COMMON_STOCKS)

// 加载股票列表
const loadStockOptions = async () => {
  try {
    // 尝试获取上海和深圳市场的股票列表
    const [shResponse, szResponse] = await Promise.allSettled([
      getStockList('SH'),
      getStockList('SZ')
    ])

    const stocks: string[] = [...COMMON_STOCKS]

    if (shResponse.status === 'fulfilled' && shResponse.value.code === 200) {
      const shList = shResponse.value.data?.list || []
      stocks.push(...shList.map((item: any) => item.symbol))
    }

    if (szResponse.status === 'fulfilled' && szResponse.value.code === 200) {
      const szList = szResponse.value.data?.list || []
      stocks.push(...szList.map((item: any) => item.symbol))
    }

    // 去重并限制数量
    stockOptions.value = [...new Set(stocks)].slice(0, 200)
  } catch (error) {
    console.warn('加载股票列表失败，使用默认列表')
    stockOptions.value = COMMON_STOCKS
  }
}

const canPredict = computed(() => {
  return (
    !predicting.value &&
    selectedModelId.value &&
    form.value.instruments.length > 0 &&
    dateRange.value &&
    dateRange.value.length === 2
  )
})

const filteredPredictions = computed(() => {
  if (!predictionResult.value?.predictions) return []
  if (!searchText.value) return predictionResult.value.predictions

  const search = searchText.value.toLowerCase()
  return predictionResult.value.predictions.filter(p =>
    p.instrument.toLowerCase().includes(search)
  )
})

// ==================== 方法 ====================

/**
 * 获取状态标签类型
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
 * 格式化日期
 */
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

/**
 * 格式化预测值
 */
const formatPrediction = (row: { prediction: number }) => {
  return row.prediction.toFixed(4)
}

/**
 * 格式化概率
 */
const formatProbability = (row: { probability?: number }) => {
  if (row.probability === undefined) return '--'
  return `${(row.probability * 100).toFixed(2)}%`
}

/**
 * 获取预测值样式类
 */
const getPredictionClass = (row: { prediction: number }) => {
  if (row.prediction > 0.5) return 'positive'
  if (row.prediction < 0.5) return 'negative'
  return 'neutral'
}

/**
 * 获取概率样式类
 */
const getProbabilityClass = (row: { probability?: number }) => {
  if (row.probability === undefined) return ''
  if (row.probability > 0.6) return 'positive'
  if (row.probability < 0.4) return 'negative'
  return 'neutral'
}

/**
 * 获取信号
 */
const getSignal = (row: { prediction: number }) => {
  if (row.prediction > 0.6) return '强烈买入'
  if (row.prediction > 0.5) return '买入'
  if (row.prediction < 0.4) return '卖出'
  if (row.prediction < 0.3) return '强烈卖出'
  return '持有'
}

/**
 * 获取信号类型
 */
const getSignalType = (row: { prediction: number }) => {
  if (row.prediction > 0.6) return 'success'
  if (row.prediction < 0.4) return 'danger'
  return 'warning'
}

/**
 * 模型变更
 */
const onModelChange = async (modelId: string) => {
  const model = models.value.find(m => m.model_id === modelId)
  if (model) {
    selectedModel.value = model
    form.value.model_id = modelId
  }
}

/**
 * 开始预测
 */
const startPrediction = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  try {
    predicting.value = true
    predictionResult.value = null

    // 更新表单日期
    form.value.start_date = dateRange.value[0].toISOString().split('T')[0]
    form.value.end_date = dateRange.value[1].toISOString().split('T')[0]

    ElMessage.info('开始预测...')

    // 调用API
    const response = await mlAPI.predict(form.value)

    if (response.code === 200) {
      predictionResult.value = response.data
      ElMessage.success(`预测完成！共 ${response.data.predictions.length} 条结果`)
      initChart()
      // 添加到历史记录
      addToHistory(response.data)
    }
  } catch (error: any) {
    console.error('预测失败:', error)
    ElMessage.error('预测失败，请检查配置')
  } finally {
    predicting.value = false
  }
}

/**
 * 导出结果
 */
const exportResults = () => {
  if (!predictionResult.value) return

  const predictions = predictionResult.value.predictions
  const headers = ['股票代码', '预测日期', '预测值', '概率', '信号']
  const rows = predictions.map(p => [
    p.instrument,
    p.date,
    p.prediction.toFixed(4),
    p.probability !== undefined ? p.probability.toFixed(4) : '',
    getSignal(p)
  ])

  const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  link.setAttribute('href', url)
  link.setAttribute('download', `predictions_${Date.now()}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  ElMessage.success('导出成功')
}

/**
 * 查看详情
 */
const viewDetail = (row: any) => {
  selectedPrediction.value = row
  detailDialogVisible.value = true
}

/**
 * 加载模型列表
 */
const loadModels = async () => {
  try {
    const response = await mlAPI.getModels()
    if (response.code === 200) {
      models.value = response.data.models
    }
  } catch (error) {
    console.error('加载模型列表失败:', error)
  }
}

/**
 * 初始化图表
 */
const initChart = () => {
  if (!chartRef.value || !predictionResult.value) return

  if (chart) {
    chart.dispose()
  }

  chart = echarts.init(chartRef.value)

  const predictions = predictionResult.value.predictions

  const option = {
    title: {
      text: '预测分布',
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
      name: '股票',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8', rotate: 45 }
    },
    yAxis: {
      type: 'value',
      name: '预测值',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }
    },
    series: [{
      name: '预测值',
      type: 'bar',
      data: predictions.slice(0, 20).map(p => ({
        value: p.prediction,
        name: p.instrument
      })),
      itemStyle: {
        color: (params: any) => {
          if (params.value > 0.6) return '#10b981'
          if (params.value < 0.4) return '#ef4444'
          return '#94a3b8'
        }
      },
      label: {
        show: true,
        position: 'top',
        formatter: (params: any) => params.value.toFixed(3)
      }
    }]
  }

  chart.setOption(option)
}

onMounted(() => {
  loadModels()
  loadStockOptions()
})
</script>

<style scoped lang="scss">
.ml-prediction-view {
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

  .header-right {
    display: flex;
    gap: 12px;
  }
}

.view-content {
  display: grid;
  grid-template-columns: 400px 1fr;
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
      display: flex;
      justify-content: space-between;
      align-items: center;
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
  }

  .model-option {
    display: flex;
    align-items: center;
    gap: 8px;

    .model-type {
      font-weight: 500;
    }

    .model-task {
      font-size: 12px;
      color: var(--text-muted);
    }
  }

  .model-info {
    margin-top: 16px;
    padding: 12px;
    background: var(--bg-elevated);
    border-radius: var(--radius-md);
    border: 1px solid var(--border-light);
    display: flex;
    flex-direction: column;
    gap: 8px;

    .info-item {
      display: flex;
      justify-content: space-between;
      font-size: 13px;

      .info-label {
        color: var(--text-secondary);
      }

      .info-value {
        font-weight: 500;
        color: var(--text-primary);
      }
    }
  }

  .prediction-summary {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .summary-item {
      display: flex;
      justify-content: space-between;
      padding: 8px;
      background: var(--bg-elevated);
      border-radius: var(--radius-sm);

      .summary-label {
        font-size: 13px;
        color: var(--text-secondary);
      }

      .summary-value {
        font-weight: 500;
        font-family: 'JetBrains Mono', monospace;
        color: var(--primary);
      }
    }
  }
}

.results-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.results-card,
.chart-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);

  :deep(.el-card__header) {
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border-light);
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
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
}

.positive {
  color: #ef4444;
  font-weight: 600;
}

.negative {
  color: #10b981;
  font-weight: 600;
}

.neutral {
  color: var(--text-secondary);
}

.chart-container {
  height: 300px;
  width: 100%;
}

.prediction-detail {
  .detail-grid {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px;
      background: var(--bg-elevated);
      border-radius: var(--radius-md);

      .detail-label {
        font-size: 14px;
        color: var(--text-secondary);
      }

      .detail-value {
        font-weight: 500;
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
  background: var(--bg-deep);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-elevated);
  border-radius: var(--radius-full);

  &:hover {
    background: var(--border-strong);
  }
}

.history-dialog-content {
  .history-actions {
    margin-bottom: 16px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
