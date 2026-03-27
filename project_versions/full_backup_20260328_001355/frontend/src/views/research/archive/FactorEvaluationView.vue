<template>
  <div class="factor-evaluation-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="phase-badge research">🔬 研究阶段</div>
          <h1 class="page-title"><i class="fas fa-star"></i> 因子评估</h1>
          <p class="page-subtitle">因子有效性验证与组合评估</p>
        </div>
      </div>
    </div>

    <!-- 评分仪表盘区域 -->
    <el-card class="gauge-dashboard-card">
      <template #header>
        <div class="card-header">
          <span>因子评估仪表盘</span>
          <el-tag type="info" size="small">默认显示模拟数据</el-tag>
        </div>
      </template>
      <div class="gauge-dashboard">
        <div class="gauge-item">
          <el-progress
            type="dashboard"
            :percentage="dashboardData.icMeanScore"
            :width="120"
            :color="getGaugeColor(dashboardData.icMeanScore)"
          />
          <span class="gauge-label">IC均值得分</span>
          <span class="gauge-value">{{ dashboardData.icMeanValue }}</span>
        </div>
        <div class="gauge-item">
          <el-progress
            type="dashboard"
            :percentage="dashboardData.irScore"
            :width="120"
            :color="getGaugeColor(dashboardData.irScore)"
          />
          <span class="gauge-label">IR得分</span>
          <span class="gauge-value">{{ dashboardData.irValue }}</span>
        </div>
        <div class="gauge-item">
          <el-progress
            type="dashboard"
            :percentage="dashboardData.icPositiveScore"
            :width="120"
            :color="getGaugeColor(dashboardData.icPositiveScore)"
          />
          <span class="gauge-label">IC正数占比得分</span>
          <span class="gauge-value">{{ dashboardData.icPositiveValue }}</span>
        </div>
        <div class="gauge-item">
          <el-progress
            type="dashboard"
            :percentage="dashboardData.overallScore"
            :width="140"
            :color="getOverallColor(dashboardData.overallScore)"
          />
          <span class="gauge-label">综合评分</span>
          <span class="gauge-value overall">{{ dashboardData.overallScoreLabel }}</span>
        </div>
      </div>
      <el-alert
        v-if="!hasRealData"
        type="info"
        :closable="false"
        show-icon
        class="demo-alert"
      >
        <template #title>
          当前显示模拟数据，请输入因子名称并点击"开始评估"获取真实评估结果
        </template>
      </el-alert>
    </el-card>

    <!-- 功能标签页 -->
    <el-tabs v-model="activeTab" class="evaluation-tabs">
      <!-- 因子有效性验证 -->
      <el-tab-pane label="有效性验证" name="validity">
        <el-card class="validity-card">
          <template #header>
            <span>因子有效性验证</span>
          </template>

          <el-form :model="validityForm" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="因子名称">
                  <el-input
                    v-model="validityForm.factor_name"
                    placeholder="例如: custom_factor_001"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="validityForm.dateRange"
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
            </el-row>

            <el-divider content-position="left">阈值设置（可选）</el-divider>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="IC均值阈值">
                  <el-input-number
                    v-model="validityForm.threshold.ic_mean"
                    :step="0.01"
                    :precision="3"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="IR阈值">
                  <el-input-number
                    v-model="validityForm.threshold.ir"
                    :step="0.1"
                    :precision="2"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="IC正数占比阈值">
                  <el-input-number
                    v-model="validityForm.threshold.ic_positive_ratio"
                    :step="0.05"
                    :max="1"
                    :precision="2"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-button
                type="primary"
                @click="evaluateValidity"
                :loading="evaluatingValidity"
                size="large"
              >
                开始评估
              </el-button>
              <el-button @click="resetValidityForm">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 评估结果 -->
          <div v-if="validityResult" class="validity-result">
            <el-divider content-position="left">评估结果</el-divider>

            <el-row :gutter="20" class="result-summary">
              <el-col :span="8">
                <el-card :class="validityResult.is_valid ? 'success-card' : 'warning-card'">
                  <div class="result-item">
                    <span class="label">是否有效</span>
                    <el-tag :type="validityResult.is_valid ? 'success' : 'danger'" size="large">
                      {{ validityResult.is_valid ? '有效' : '无效' }}
                    </el-tag>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="score-card">
                  <div class="result-item">
                    <span class="label">总体评分</span>
                    <span class="score-value">{{ (validityResult.overall_score * 100).toFixed(0) }}分</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="recommendation-card">
                  <div class="result-item">
                    <span class="label">建议</span>
                    <span class="recommendation-text">{{ validityResult.recommendation }}</span>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 详细指标 -->
            <el-divider content-position="left">详细指标</el-divider>

            <el-table :data="getMetricsTableData()" border>
              <el-table-column prop="metric" label="指标" width="120" />
              <el-table-column prop="value" label="计算值" width="100">
                <template #default="{ row }">
                  <span :class="row.passed ? 'success-text' : 'warning-text'">
                    {{ row.value }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="threshold" label="阈值" width="100" />
              <el-table-column prop="passed" label="是否通过" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.passed ? 'success' : 'danger'" size="small">
                    {{ row.passed ? '通过' : '未通过' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="score" label="得分" width="100">
                <template #default="{ row }">
                  <el-progress
                    :percentage="row.score * 100"
                    :color="getProgressColor(row.score)"
                    :show-text="true"
                  />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 因子组合评估 -->
      <el-tab-pane label="组合评估" name="combination">
        <el-card class="combination-card">
          <template #header>
            <span>因子组合评估</span>
          </template>

          <el-form :model="combinationForm" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="选择因子">
                  <el-select
                    v-model="combinationForm.factor_names"
                    multiple
                    filterable
                    allow-create
                    placeholder="输入因子名称，可添加多个"
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
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="combinationForm.dateRange"
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
              <el-col :span="12">
                <el-form-item label="组合方法">
                  <el-select
                    v-model="combinationForm.combination_method"
                    placeholder="选择组合方法"
                    style="width: 100%"
                  >
                    <el-option label="等权重" value="equal_weight" />
                    <el-option label="IC加权" value="ic_weight" />
                    <el-option label="组合优化" value="optimization" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <!-- 自定义权重（仅当选择custom时显示） -->
            <el-row v-if="combinationForm.combination_method === 'custom'" :gutter="20">
              <el-col :span="24">
                <el-form-item label="自定义权重">
                  <div
                    v-for="(factor, index) in combinationForm.factor_names"
                    :key="factor"
                    class="weight-input-row"
                  >
                    <span class="factor-label">{{ factor }}</span>
                    <el-input-number
                      v-model="combinationForm.weights[index]"
                      :min="0"
                      :max="1"
                      :step="0.1"
                      :precision="2"
                      style="width: 200px"
                    />
                  </div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-button
                type="primary"
                @click="evaluateCombination"
                :loading="evaluatingCombination"
                size="large"
                :disabled="combinationForm.factor_names.length < 2"
              >
                开始评估
              </el-button>
              <el-button @click="resetCombinationForm">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 组合评估结果 -->
          <div v-if="combinationResult" class="combination-result">
            <el-divider content-position="left">组合评估结果</el-divider>

            <el-descriptions :column="2" border>
              <el-descriptions-item label="组合因子名称">
                {{ combinationResult.combined_factor_name }}
              </el-descriptions-item>
              <el-descriptions-item label="组合方法">
                {{ getCombinationMethodName(combinationResult.combination_method) }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- 权重分配 -->
            <el-divider content-position="left">权重分配</el-divider>

            <div class="weights-chart">
              <div
                v-for="(weight, factor) in combinationResult.weights"
                :key="factor"
                class="weight-bar-item"
              >
                <span class="factor-name">{{ factor }}</span>
                <el-progress
                  :percentage="weight * 100"
                  :format="() => (weight * 100).toFixed(1) + '%'"
                />
              </div>
            </div>

            <!-- 组合后指标 -->
            <el-divider content-position="left">组合后指标</el-divider>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="metric-card">
                  <div class="metric-item">
                    <span class="label">IC均值</span>
                    <span class="value">{{ combinationResult.evaluation.ic_mean.toFixed(4) }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="metric-card">
                  <div class="metric-item">
                    <span class="label">IR</span>
                    <span class="value">{{ combinationResult.evaluation.ir.toFixed(4) }}</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="metric-card">
                  <div class="metric-item">
                    <span class="label">IC正数占比</span>
                    <span class="value">{{ (combinationResult.evaluation.ic_positive_ratio * 100).toFixed(2) }}%</span>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 与最佳单因子比较 -->
            <el-divider content-position="left">与最佳单因子比较</el-divider>

            <el-alert
              :type="combinationResult.comparison.is_better ? 'success' : 'info'"
              :closable="false"
            >
              <template #title>
                <div>
                  最佳单因子: <strong>{{ combinationResult.comparison.best_factor }}</strong>
                  (IC均值: {{ combinationResult.comparison.best_factor_ic_mean.toFixed(4) }})
                  <br />
                  组合后IC均值:
                  <strong>{{ combinationResult.comparison.improvement.ic_mean >= 0 ? '+' : '' }}{{ combinationResult.comparison.improvement.ic_mean.toFixed(4) }}</strong>
                  {{ combinationResult.comparison.is_better ? '✅ 组合优于单因子' : '⚠️ 单因子更优' }}
                </div>
              </template>
            </el-alert>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// 状态
const activeTab = ref('validity')
const evaluatingValidity = ref(false)
const evaluatingCombination = ref(false)
const hasRealData = ref(false)

// 仪表盘数据（默认模拟数据）
const dashboardData = reactive({
  icMeanScore: 72,
  icMeanValue: '0.0456',
  irScore: 65,
  irValue: '0.82',
  icPositiveScore: 58,
  icPositiveValue: '56.2%',
  overallScore: 68,
  overallScoreLabel: '68分'
})

// 更新仪表盘数据
const updateDashboard = (metrics: any) => {
  if (!metrics) return

  // 计算得分
  dashboardData.icMeanScore = Math.round(metrics.ic_mean?.score * 100 || 0)
  dashboardData.icMeanValue = metrics.ic_mean?.value?.toFixed(4) || '0.0000'

  dashboardData.irScore = Math.round(metrics.ir?.score * 100 || 0)
  dashboardData.irValue = metrics.ir?.value?.toFixed(2) || '0.00'

  dashboardData.icPositiveScore = Math.round(metrics.ic_positive_ratio?.score * 100 || 0)
  dashboardData.icPositiveValue = ((metrics.ic_positive_ratio?.value || 0) * 100).toFixed(1) + '%'

  // 综合评分（取平均）
  const overall = Math.round((dashboardData.icMeanScore + dashboardData.irScore + dashboardData.icPositiveScore) / 3)
  dashboardData.overallScore = overall
  dashboardData.overallScoreLabel = overall + '分'

  hasRealData.value = true
}

// 仪表盘颜色
const getGaugeColor = (percentage: number) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 60) return '#e6a23c'
  if (percentage >= 40) return '#f56c6c'
  return '#909399'
}

const getOverallColor = (percentage: number) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 60) return '#409eff'
  if (percentage >= 40) return '#e6a23c'
  return '#f56c6c'
}

// 有效性验证表单
const validityForm = ref({
  factor_name: '',
  dateRange: ['2020-01-01', '2024-12-31'],
  threshold: {
    ic_mean: 0.03,
    ir: 0.5,
    ic_positive_ratio: 0.55
  }
})

// 组合评估表单
const combinationForm = ref({
  factor_names: [],
  dateRange: ['2020-01-01', '2024-12-31'],
  combination_method: 'equal_weight',
  weights: []
})

// 评估结果
const validityResult = ref<any>(null)
const combinationResult = ref<any>(null)

// 可选因子列表
const availableFactors = ref([
  'custom_factor_001',
  'custom_factor_002',
  'alpha158_001',
  'alpha158_002',
  'momentum_factor',
  'reversal_factor'
])

// API调用
const API_BASE = '/api/v1/research/eval'

const evaluateValidity = async () => {
  if (!validityForm.value.factor_name) {
    ElMessage.warning('请输入因子名称')
    return
  }

  evaluatingValidity.value = true
  try {
    const res = await fetch(`${API_BASE}/validity`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        factor_name: validityForm.value.factor_name,
        start_date: validityForm.value.dateRange[0],
        end_date: validityForm.value.dateRange[1],
        threshold: validityForm.value.threshold
      })
    })
    const data = await res.json()
    if (data.code === 200) {
      validityResult.value = data.data
      // 更新仪表盘数据
      updateDashboard(data.data.metrics)
      ElMessage.success('评估完成')
    }
  } catch (error: any) {
    ElMessage.error('评估失败: ' + error.message)
  } finally {
    evaluatingValidity.value = false
  }
}

const evaluateCombination = async () => {
  if (combinationForm.value.factor_names.length < 2) {
    ElMessage.warning('至少选择2个因子')
    return
  }

  evaluatingCombination.value = true
  try {
    const res = await fetch(`${API_BASE}/combine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        factor_names: combinationForm.value.factor_names,
        start_date: combinationForm.value.dateRange[0],
        end_date: combinationForm.value.dateRange[1],
        combination_method: combinationForm.value.combination_method,
        weights: combinationForm.value.weights.length > 0 ? combinationForm.value.weights : undefined
      })
    })
    const data = await res.json()
    if (data.code === 200) {
      combinationResult.value = data.data
      ElMessage.success('评估完成')
    }
  } catch (error: any) {
    ElMessage.error('评估失败: ' + error.message)
  } finally {
    evaluatingCombination.value = false
  }
}

// 辅助函数
const getMetricsTableData = () => {
  if (!validityResult.value) return []

  const metrics = validityResult.value.metrics
  return [
    {
      metric: 'IC均值',
      value: metrics.ic_mean.value.toFixed(4),
      threshold: metrics.ic_mean.threshold.toFixed(3),
      passed: metrics.ic_mean.passed,
      score: metrics.ic_mean.score
    },
    {
      metric: 'IR',
      value: metrics.ir.value.toFixed(4),
      threshold: metrics.ir.threshold.toFixed(2),
      passed: metrics.ir.passed,
      score: metrics.ir.score
    },
    {
      metric: 'IC正数占比',
      value: (metrics.ic_positive_ratio.value * 100).toFixed(2) + '%',
      threshold: (metrics.ic_positive_ratio.threshold * 100).toFixed(0) + '%',
      passed: metrics.ic_positive_ratio.passed,
      score: metrics.ic_positive_ratio.score
    }
  ]
}

const getProgressColor = (score: number) => {
  if (score >= 0.8) return '#67C23A'
  if (score >= 0.6) return '#E6A23C'
  return '#F56C6C'
}

const getCombinationMethodName = (method: string) => {
  const nameMap: Record<string, string> = {
    'equal_weight': '等权重',
    'ic_weight': 'IC加权',
    'optimization': '组合优化',
    'custom': '自定义'
  }
  return nameMap[method] || method
}

const resetValidityForm = () => {
  validityForm.value = {
    factor_name: '',
    dateRange: ['2020-01-01', '2024-12-31'],
    threshold: {
      ic_mean: 0.03,
      ir: 0.5,
      ic_positive_ratio: 0.55
    }
  }
  validityResult.value = null
}

const resetCombinationForm = () => {
  combinationForm.value = {
    factor_names: [],
    dateRange: ['2020-01-01', '2024-12-31'],
    combination_method: 'equal_weight',
    weights: []
  }
  combinationResult.value = null
}
</script>

<style scoped>
.factor-evaluation-view {
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

/* 仪表盘样式 */
.gauge-dashboard-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gauge-dashboard {
  display: flex;
  justify-content: center;
  gap: 50px;
  padding: 20px 0;
  flex-wrap: wrap;
}

.gauge-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.gauge-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.gauge-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.gauge-value.overall {
  font-size: 20px;
  color: #409eff;
}

.demo-alert {
  margin-top: 15px;
}

.evaluation-tabs {
  margin-top: 20px;
}

.validity-card,
.combination-card {
  margin-bottom: 20px;
}

.validity-result,
.combination-result {
  margin-top: 30px;
}

.result-summary {
  margin-bottom: 20px;
}

.result-item {
  text-align: center;
}

.result-item .label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
}

.success-card {
  background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
  color: white;
}

.warning-card {
  background: linear-gradient(135deg, #F56C6C 0%, #F78989 100%);
  color: white;
}

.score-card {
  background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);
  color: white;
}

.recommendation-card {
  background: linear-gradient(135deg, #E6A23C 0%, #EEBE77 100%);
  color: white;
}

.score-value {
  font-size: 32px;
  font-weight: bold;
}

.recommendation-text {
  font-size: 14px;
}

.success-text {
  color: #67C23A;
  font-weight: bold;
}

.warning-text {
  color: #F56C6C;
  font-weight: bold;
}

.weights-chart {
  margin: 20px 0;
}

.weight-bar-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.factor-name {
  width: 200px;
  font-weight: bold;
}

.metric-card {
  text-align: center;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric-item .label {
  font-size: 12px;
  color: #909399;
}

.metric-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.weight-input-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.factor-label {
  width: 200px;
}
</style>
