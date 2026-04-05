<template>
  <div class="factor-analysis-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="phase-badge research">🔬 研究阶段</div>
          <h1 class="page-title"><i class="fas fa-chart-bar"></i> 因子分析</h1>
          <p class="page-subtitle">IC/IR分析、分布分析、相关性分析</p>
        </div>
      </div>
    </div>

    <!-- 功能标签页 -->
    <el-tabs v-model="activeTab" class="analysis-tabs">
      <!-- IC/IR分析 -->
      <el-tab-pane label="IC/IR分析" name="icir">
        <el-card class="icir-card">
          <template #header>
            <span>信息系数/信息比率分析</span>
          </template>

          <el-form :model="icirForm" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="因子名称">
                  <el-select
                    v-model="icirForm.factor_name"
                    filterable
                    allow-create
                    placeholder="选择或输入因子名称"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="factor in availableFactors"
                      :key="factor"
                      :label="factor"
                      :value="factor"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="10">
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="icirForm.dateRange"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="周期">
                  <el-select v-model="icirForm.period" style="width: 100%">
                    <el-option label="日线" value="1d" />
                    <el-option label="周线" value="1w" />
                    <el-option label="1分钟" value="1m" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-button
                type="primary"
                @click="analyzeICIR"
                :loading="analyzingICIR"
              >
                开始分析
              </el-button>
              <el-button @click="resetICIRForm">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- IC/IR分析结果 -->
          <div v-if="icirResult" class="icir-result">
            <el-divider content-position="left">分析结果</el-divider>

            <!-- 统计指标卡片 -->
            <el-row :gutter="20" class="metrics-cards">
              <el-col :span="6">
                <el-card class="metric-card">
                  <div class="metric-item">
                    <span class="label">IC均值</span>
                    <span class="value">{{ icirResult.ic.mean.toFixed(4) }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="metric-card">
                  <div class="metric-item">
                    <span class="label">IR</span>
                    <span class="value">{{ icirResult.ir.toFixed(4) }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="metric-card">
                  <div class="metric-item">
                    <span class="label">IC正数占比</span>
                    <span class="value">{{ (icirResult.ic_positive_ratio * 100).toFixed(2) }}%</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="metric-card">
                  <div class="metric-item">
                    <span class="label">t统计量</span>
                    <span class="value">{{ icirResult.t_stat.toFixed(4) }}</span>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <!-- IC范围 -->
            <el-divider content-position="left">IC范围</el-divider>

            <el-row :gutter="20">
              <el-col :span="8">
                <div class="range-item">
                  <span class="label">最小值: </span>
                  <span class="value">{{ icirResult.ic.min.toFixed(4) }}</span>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="range-item">
                  <span class="label">最大值: </span>
                  <span class="value">{{ icirResult.ic.max.toFixed(4) }}</span>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="range-item">
                  <span class="label">标准差: </span>
                  <span class="value">{{ icirResult.ic.std.toFixed(4) }}</span>
                </div>
              </el-col>
            </el-row>

            <!-- IC序列图（简化版） -->
            <el-divider content-position="left">IC时间序列</el-divider>

            <div class="ic-series-chart">
              <div class="chart-container">
                <div
                  v-for="(point, index) in displayedICSeries"
                  :key="index"
                  class="chart-bar"
                  :style="{ height: getBarHeight(point.ic) + '%' }"
                  :title="`日期: ${point.date}, IC: ${point.ic.toFixed(4)}`"
                >
                  <span v-if="index % 10 === 0" class="chart-label">{{ point.date.substring(5) }}</span>
                </div>
              </div>
              <div class="chart-legend">
                <span class="legend-item positive">正值区域</span>
                <span class="legend-item negative">负值区域</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 分布分析 -->
      <el-tab-pane label="分布分析" name="distribution">
        <el-card class="distribution-card">
          <template #header>
            <span>因子分布分析</span>
          </template>

          <el-form :model="distributionForm" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="因子名称">
                  <el-select
                    v-model="distributionForm.factor_name"
                    filterable
                    allow-create
                    placeholder="选择或输入因子名称"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="factor in availableFactors"
                      :key="factor"
                      :label="factor"
                      :value="factor"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="分箱数量">
                  <el-input-number
                    v-model="distributionForm.bins"
                    :min="10"
                    :max="200"
                    :step="10"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="analyzeDistribution"
                    :loading="analyzingDistribution"
                  >
                    开始分析
                  </el-button>
                  <el-button @click="resetDistributionForm">重置</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <!-- 分布分析结果 -->
          <div v-if="distributionResult" class="distribution-result">
            <el-divider content-position="left">统计指标</el-divider>

            <el-table :data="getStatisticsTableData()" border>
              <el-table-column prop="metric" label="指标" width="120" />
              <el-table-column prop="value" label="值" />
            </el-table>

            <el-divider content-position="left">分位数</el-divider>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>百分位数</span>
                  </template>
                  <div class="percentiles-container">
                    <div v-for="(value, percentile) in distributionResult.percentiles" :key="percentile" class="percentile-item">
                      <span class="percentile-label">{{ percentile }}</span>
                      <span class="percentile-value">{{ value.toFixed(4) }}</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>分布直方图</span>
                  </template>
                  <div class="histogram-chart">
                    <div
                      v-for="(count, index) in distributionResult.histogram.counts"
                      :key="index"
                      class="histogram-bar"
                      :style="{ width: (count / Math.max(...distributionResult.histogram.counts) * 100) + '%' }"
                    >
                      <span v-if="count > 0" class="histogram-label">{{ count }}</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 相关性分析 -->
      <el-tab-pane label="相关性分析" name="correlation">
        <el-card class="correlation-card">
          <template #header>
            <span>因子相关性分析</span>
          </template>

          <el-form :model="correlationForm" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="选择因子">
                  <el-select
                    v-model="correlationForm.factor_names"
                    multiple
                    filterable
                    allow-create
                    placeholder="选择2个或更多因子"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="factor in availableFactors"
                      :key="factor"
                      :label="factor"
                      :value="factor"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="相关方法">
                  <el-radio-group v-model="correlationForm.method">
                    <el-radio label="pearson">Pearson</el-radio>
                    <el-radio label="spearman">Spearman</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="analyzeCorrelation"
                    :loading="analyzingCorrelation"
                    :disabled="correlationForm.factor_names.length < 2"
                  >
                    开始分析
                  </el-button>
                  <el-button @click="resetCorrelationForm">重置</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <!-- 相关性分析结果 -->
          <div v-if="correlationResult" class="correlation-result">
            <el-divider content-position="left">相关系数矩阵</el-divider>

            <div class="correlation-matrix">
              <el-table :data="getCorrelationTableData()" border>
                <el-table-column label="因子" width="150">
                  <template #default="{ row }">
                    <strong>{{ row.factor }}</strong>
                  </template>
                </el-table-column>
                <el-table-column
                  v-for="(factor, index) in correlationResult.factor_names"
                  :key="index"
                  :label="factor"
                >
                  <template #default="{ row }">
                    <span
                      :class="getCorrelationClass(row[factor])"
                    >
                      {{ row[factor].toFixed(3) }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div class="correlation-legend">
              <span class="legend-item strong-positive">强正相关 (>0.7)</span>
              <span class="legend-item moderate-positive">正相关 (0.3~0.7)</span>
              <span class="legend-item weak">弱相关 (-0.3~0.3)</span>
              <span class="legend-item moderate-negative">负相关 (-0.7~-0.3)</span>
              <span class="legend-item strong-negative">强负相关 (<-0.7)</span>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

// 状态
const activeTab = ref('icir')
const analyzingICIR = ref(false)
const analyzingDistribution = ref(false)
const analyzingCorrelation = ref(false)

// 可用因子列表
const availableFactors = ref([
  'custom_factor_001',
  'custom_factor_002',
  'alpha158_001',
  'alpha158_002',
  'momentum_factor',
  'reversal_factor'
])

// IC/IR分析表单
const icirForm = ref({
  factor_name: '',
  dateRange: ['2020-01-01', '2024-12-31'],
  period: '1d'
})

// 分布分析表单
const distributionForm = ref({
  factor_name: '',
  bins: 50
})

// 相关性分析表单
const correlationForm = ref({
  factor_names: [],
  method: 'pearson'
})

// 分析结果
const icirResult = ref<any>(null)
const distributionResult = ref<any>(null)
const correlationResult = ref<any>(null)

// API调用
const API_BASE = '/api/v1/research/analysis'

const analyzeICIR = async () => {
  if (!icirForm.value.factor_name) {
    ElMessage.warning('请输入因子名称')
    return
  }

  analyzingICIR.value = true
  try {
    const res = await fetch(`${API_BASE}/ic-ir`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        factor_name: icirForm.value.factor_name,
        start_date: icirForm.value.dateRange[0],
        end_date: icirForm.value.dateRange[1],
        period: icirForm.value.period
      })
    })
    const data = await res.json()
    if (data.code === 200) {
      icirResult.value = data.data
      ElMessage.success('分析完成')
    }
  } catch (error: any) {
    ElMessage.error('分析失败: ' + error.message)
  } finally {
    analyzingICIR.value = false
  }
}

const analyzeDistribution = async () => {
  if (!distributionForm.value.factor_name) {
    ElMessage.warning('请输入因子名称')
    return
  }

  analyzingDistribution.value = true
  try {
    const res = await fetch(`${API_BASE}/distribution`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(distributionForm.value)
    })
    const data = await res.json()
    if (data.code === 200) {
      distributionResult.value = data.data
      ElMessage.success('分析完成')
    }
  } catch (error: any) {
    ElMessage.error('分析失败: ' + error.message)
  } finally {
    analyzingDistribution.value = false
  }
}

const analyzeCorrelation = async () => {
  if (correlationForm.value.factor_names.length < 2) {
    ElMessage.warning('至少选择2个因子')
    return
  }

  analyzingCorrelation.value = true
  try {
    const res = await fetch(`${API_BASE}/correlation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(correlationForm.value)
    })
    const data = await res.json()
    if (data.code === 200) {
      correlationResult.value = data.data
      ElMessage.success('分析完成')
    }
  } catch (error: any) {
    ElMessage.error('分析失败: ' + error.message)
  } finally {
    analyzingCorrelation.value = false
  }
}

// 计算属性和辅助方法
const displayedICSeries = computed(() => {
  if (!icirResult.value || !icirResult.value.ic) return []
  return icirResult.value.ic.ic_series.slice(-50) // 只显示最近50个点
})

const getBarHeight = (ic: number) => {
  const maxIC = 0.15
  const minIC = -0.15
  const range = maxIC - minIC
  return Math.max(((ic - minIC) / range) * 100, 5)
}

const getStatisticsTableData = () => {
  if (!distributionResult.value) return []

  const stats = distributionResult.value.statistics
  return [
    { metric: '样本数量', value: stats.count.toLocaleString() },
    { metric: '均值', value: stats.mean.toFixed(4) },
    { metric: '标准差', value: stats.std.toFixed(4) },
    { metric: '最小值', value: stats.min.toFixed(4) },
    { metric: '最大值', value: stats.max.toFixed(4) },
    { metric: '偏度', value: stats.skewness.toFixed(4) },
    { metric: '峰度', value: stats.kurtosis.toFixed(4) }
  ]
}

const getCorrelationTableData = () => {
  if (!correlationResult.value) return []

  const matrix = correlationResult.value.correlation_matrix
  return correlationResult.value.factor_names.map((factor: string, index: number) => {
    const row: any = { factor }
    correlationResult.value.factor_names.forEach((f: string, i: number) => {
      row[f] = matrix[index][i]
    })
    return row
  })
}

const getCorrelationClass = (value: number) => {
  if (value > 0.7) return 'strong-positive'
  if (value > 0.3) return 'moderate-positive'
  if (value >= -0.3) return 'weak'
  if (value >= -0.7) return 'moderate-negative'
  return 'strong-negative'
}

// 重置表单
const resetICIRForm = () => {
  icirForm.value = {
    factor_name: '',
    dateRange: ['2020-01-01', '2024-12-31'],
    period: '1d'
  }
  icirResult.value = null
}

const resetDistributionForm = () => {
  distributionForm.value = {
    factor_name: '',
    bins: 50
  }
  distributionResult.value = null
}

const resetCorrelationForm = () => {
  correlationForm.value = {
    factor_names: [],
    method: 'pearson'
  }
  correlationResult.value = null
}
</script>

<style scoped>
.factor-analysis-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.phase-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
}

.phase-badge.research {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  color: white;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.page-subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.analysis-tabs {
  margin-top: 20px;
}

.icir-card,
.distribution-card,
.correlation-card {
  margin-bottom: 20px;
}

.icir-result,
.distribution-result,
.correlation-result {
  margin-top: 30px;
}

.metrics-cards {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  color: white;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric-item .label {
  font-size: 12px;
  opacity: 0.8;
}

.metric-item .value {
  font-size: 28px;
  font-weight: bold;
}

.range-item {
  text-align: center;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 10px;
}

.range-item .label {
  color: #606266;
  margin-right: 10px;
}

.range-item .value {
  font-weight: bold;
  font-size: 16px;
}

.ic-series-chart {
  margin-top: 20px;
}

.chart-container {
  display: flex;
  align-items: flex-end;
  height: 200px;
  background: #f5f7fa;
  border-radius: 4px;
  padding: 10px;
  gap: 2px;
}

.chart-bar {
  flex: 1;
  background: #409EFF;
  border-radius: 2px 2px 0 0;
  position: relative;
  min-height: 2px;
  transition: all 0.3s;
}

.chart-bar.negative {
  background: #F56C6C;
}

.chart-label {
  position: absolute;
  bottom: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: #909399;
  white-space: nowrap;
}

.chart-legend {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 10px;
  font-size: 12px;
}

.percentiles-container {
  padding: 10px 0;
}

.percentile-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #EBEEF5;
}

.percentile-item:last-child {
  border-bottom: none;
}

.percentile-label {
  color: #606266;
  font-weight: bold;
}

.percentile-value {
  font-family: monospace;
}

.histogram-chart {
  height: 200px;
  display: flex;
  align-items: flex-end;
  gap: 2px;
  padding: 10px 0;
}

.histogram-bar {
  flex: 1;
  background: #67C23A;
  border-radius: 2px 2px 0 0;
  min-height: 2px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 5px;
}

.histogram-label {
  font-size: 10px;
  color: white;
}

.correlation-matrix {
  margin-top: 20px;
}

.correlation-legend {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  font-size: 12px;
}

.strong-positive { color: #67C23A; font-weight: bold; }
.moderate-positive { color: #95D475; }
.weak { color: #909399; }
.moderate-negative { color: #F39C12; }
.strong-negative { color: #F56C6C; font-weight: bold; }
</style>
