<template>
  <div class="step-feasibility-check-panel">
    <!-- 检查配置 -->
    <div class="config-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        {{ isZh ? '可行性检查配置' : 'Feasibility Check Configuration' }}
      </h3>

      <div class="config-form">
        <div class="form-group">
          <label class="form-label">{{ isZh ? '检查范围' : 'Check Scope' }}</label>
          <el-checkbox-group v-model="checkConfig.scope">
            <el-checkbox label="data">{{ isZh ? '数据可用性' : 'Data Availability' }}</el-checkbox>
            <el-checkbox label="performance">{{ isZh ? '性能指标' : 'Performance' }}</el-checkbox>
            <el-checkbox label="risk">{{ isZh ? '风险评估' : 'Risk Assessment' }}</el-checkbox>
            <el-checkbox label="stability">{{ isZh ? '稳定性测试' : 'Stability Test' }}</el-checkbox>
          </el-checkbox-group>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '测试周期' : 'Test Period' }}</label>
          <el-select v-model="checkConfig.testPeriod" style="width: 100%;">
            <el-option :label="isZh ? '最近1个月' : 'Last 1 Month'" value="1m"></el-option>
            <el-option :label="isZh ? '最近3个月' : 'Last 3 Months'" value="3m"></el-option>
            <el-option :label="isZh ? '最近6个月' : 'Last 6 Months'" value="6m"></el-option>
            <el-option :label="isZh ? '最近1年' : 'Last 1 Year'" value="1y"></el-option>
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '回测频率' : 'Backtest Frequency' }}</label>
          <el-select v-model="checkConfig.frequency" style="width: 100%;">
            <el-option :label="isZh ? '每日' : 'Daily'" value="daily"></el-option>
            <el-option :label="isZh ? '每周' : 'Weekly'" value="weekly"></el-option>
            <el-option :label="isZh ? '每月' : 'Monthly'" value="monthly"></el-option>
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '回测次数' : 'Backtest Runs' }}</label>
          <el-input-number v-model="checkConfig.runs" :min="1" :max="100" style="width: 100%;" />
        </div>
      </div>
    </div>

    <!-- 检查结果 -->
    <div class="results-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
        </svg>
        {{ isZh ? '检查结果' : 'Check Results' }}
      </h3>

      <div v-if="checkResults.completed" class="results-content">
        <!-- 总体结果 -->
        <div class="overall-result">
          <div :class="['result-status', checkResults.overallPass ? 'pass' : 'fail']">
            <svg v-if="checkResults.overallPass" class="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <svg v-else class="status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="15" y1="9" x2="9" y2="15"></line>
              <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
            <div class="status-text">
              <div class="status-title">{{ isZh ? '总体评估' : 'Overall Assessment' }}</div>
              <div class="status-value">
                {{ checkResults.overallPass ? (isZh ? '通过' : 'Passed') : (isZh ? '未通过' : 'Failed') }}
              </div>
            </div>
          </div>

          <div class="score-card">
            <div class="score-label">{{ isZh ? '综合得分' : 'Overall Score' }}</div>
            <div :class="['score-value', getScoreClass(checkResults.overallScore)]">
              {{ checkResults.overallScore }}
            </div>
          </div>
        </div>

        <!-- 详细结果 -->
        <div class="detailed-results">
          <div
            v-for="result in checkResults.details"
            :key="result.category"
            :class="['result-item', result.pass ? 'pass' : 'fail']"
          >
            <div class="result-icon">
              <svg v-if="result.pass" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
            </div>
            <div class="result-info">
              <div class="result-category">{{ result.category }}</div>
              <div class="result-score">Score: {{ result.score }}</div>
            </div>
            <div class="result-status">{{ result.pass ? (isZh ? '通过' : 'Pass') : (isZh ? '未通过' : 'Fail') }}</div>
          </div>
        </div>

        <!-- 详细说明 -->
        <div class="result-summary">
          <h4 class="summary-title">{{ isZh ? '检查摘要' : 'Check Summary' }}</h4>
          <p class="summary-text">{{ checkResults.summary }}</p>

          <div v-if="!checkResults.overallPass" class="recommendations">
            <h5>{{ isZh ? '改进建议' : 'Recommendations' }}</h5>
            <ul>
              <li v-for="(rec, index) in checkResults.recommendations" :key="index">
                {{ rec }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div v-else class="results-placeholder">
        <div class="placeholder-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <p>{{ isZh ? '点击下方按钮开始检查' : 'Click the button below to start checking' }}</p>
      </div>
    </div>

    <!-- 检查历史 -->
    <div class="history-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        {{ isZh ? '检查历史' : 'Check History' }}
      </h3>

      <div v-if="checkHistory.length === 0" class="history-placeholder">
        <p>{{ isZh ? '暂无检查历史' : 'No check history' }}</p>
      </div>

      <div v-else class="history-list">
        <div
          v-for="record in checkHistory"
          :key="record.id"
          :class="['history-item', record.overallPass ? 'pass' : 'fail']"
        >
          <div class="history-time">{{ record.checkTime }}</div>
          <div class="history-score">Score: {{ record.score }}</div>
          <div class="history-status">
            {{ record.overallPass ? (isZh ? '通过' : 'Pass') : (isZh ? '失败' : 'Fail') }}
          </div>
          <el-button size="small" link @click="viewHistory(record)">
            {{ isZh ? '查看' : 'View' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <ActionButton
        type="primary"
        :label="isChecking ? (isZh ? '检查中...' : 'Checking...') : (isZh ? '开始检查' : 'Start Check')"
        :loading="isChecking"
        :disabled="isChecking"
        @click="runFeasibilityCheck"
      />
      <ActionButton
        type="default"
        :label="isZh ? '导出报告' : 'Export Report'"
        :disabled="!checkResults.completed"
        @click="exportReport"
      />
      <ActionButton
        type="success"
        :label="isZh ? '完成当前步骤' : 'Complete Step'"
        :disabled="!checkResults.overallPass"
        @click="completeStep"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/core/AppStore'

interface Props {
  taskId: string
  isZh: boolean
  currentStep: number
}

interface Emits {
  stepComplete: [data: any]
  dataUpdate: [data: any]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// 检查配置
const checkConfig = reactive({
  scope: ['data', 'performance', 'risk', 'stability'],
  testPeriod: '3m',
  frequency: 'daily',
  runs: 10
})

// 检查结果
const checkResults = reactive({
  completed: false,
  overallPass: false,
  overallScore: 0,
  summary: '',
  recommendations: [] as string[],
  details: [] as {
    category: string
    score: number
    pass: boolean
  }[]
})

// 检查历史
const checkHistory = ref<{
  id: string
  checkTime: string
  score: number
  overallPass: boolean
}[]>([])

const isChecking = ref(false)

// 获取样式类
const getScoreClass = (score: number) => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'average'
  return 'poor'
}

// 运行可行性检查
const runFeasibilityCheck = async () => {
  if (checkConfig.scope.length === 0) {
    ElMessage.warning(isZh.value ? '请至少选择一个检查范围' : 'Please select at least one check scope')
    return
  }

  isChecking.value = true

  try {
    // 模拟检查过程
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 生成检查结果
    const dataScore = 90 + Math.random() * 10
    const performanceScore = 75 + Math.random() * 20
    const riskScore = 70 + Math.random() * 25
    const stabilityScore = 65 + Math.random() * 30

    checkResults.completed = true
    checkResults.overallScore = Math.round((dataScore + performanceScore + riskScore + stabilityScore) / 4)
    checkResults.overallPass = checkResults.overallScore >= 70

    checkResults.details = [
      {
        category: isZh.value ? '数据可用性' : 'Data Availability',
        score: Math.round(dataScore),
        pass: dataScore >= 70
      },
      {
        category: isZh.value ? '性能指标' : 'Performance',
        score: Math.round(performanceScore),
        pass: performanceScore >= 70
      },
      {
        category: isZh.value ? '风险评估' : 'Risk Assessment',
        score: Math.round(riskScore),
        pass: riskScore >= 70
      },
      {
        category: isZh.value ? '稳定性测试' : 'Stability Test',
        score: Math.round(stabilityScore),
        pass: stabilityScore >= 70
      }
    ]

    checkResults.summary = isZh.value
      ? `本次可行性检查共评估了 ${checkConfig.scope.length} 个维度，综合得分为 ${checkResults.overallScore} 分。${checkResults.overallPass ? '各项指标均达到要求，模型可以进入验证阶段。' : '部分指标未达标，建议根据以下建议进行优化后再进行验证。'}`
      : `Evaluated ${checkConfig.scope.length} dimensions, overall score: ${checkResults.overallScore}. ${checkResults.overallPass ? 'All metrics meet requirements, model is ready for validation.' : 'Some metrics below threshold, consider optimization before validation.'}`

    if (!checkResults.overallPass) {
      checkResults.recommendations = isZh.value
        ? [
            '建议增加历史数据回测周期，验证模型在不同市场环境下的表现',
            '考虑引入更多样化的风险控制指标，提高模型的稳健性',
            '对因子进行更严格的筛选和降相关处理',
            '在实盘前先进行模拟交易，验证模型的实际表现'
          ]
        : [
            'Consider extending backtest period to validate model performance across different market conditions',
            'Introduce more diverse risk control metrics to improve model robustness',
            'Apply stricter factor screening and decorrelation',
            'Conduct paper trading before live deployment to verify actual performance'
          ]
    }

    // 添加到历史记录
    checkHistory.value.unshift({
      id: `check_${Date.now()}`,
      checkTime: new Date().toLocaleString(),
      score: checkResults.overallScore,
      overallPass: checkResults.overallPass
    })

    ElMessage.success(isZh.value ? '检查完成' : 'Check completed')
    emit('dataUpdate', checkResults)
  } catch (error) {
    console.error('Feasibility check failed:', error)
    ElMessage.error(isZh.value ? '检查失败' : 'Check failed')
  } finally {
    isChecking.value = false
  }
}

// 导出报告
const exportReport = () => {
  console.log('Exporting feasibility report...')
  ElMessage.success(isZh.value ? '报告已导出' : 'Report exported')
}

// 查看历史记录
const viewHistory = (record: any) => {
  console.log('Viewing history record:', record)
}

// 完成步骤
const completeStep = () => {
  emit('stepComplete', { step: 6, checkResults })
}
</script>

<style scoped lang="scss">
.step-feasibility-check-panel {
  width: 100%;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.icon-sm {
  width: 16px;
  height: 16px;
}

.config-section,
.results-section,
.history-section {
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  padding: 16px;
  margin-bottom: 20px;
}

.config-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.results-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.overall-result {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.result-status {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 2px solid;

  &.pass {
    border-color: var(--accent-green);
    background: rgba(38, 166, 154, 0.1);
  }

  &.fail {
    border-color: var(--accent-red);
    background: rgba(239, 83, 80, 0.1);
  }
}

.status-icon {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.status-text {
  .status-title {
    font-size: 11px;
    color: var(--text-secondary);
    margin-bottom: 4px;
  }

  .status-value {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
  }
}

.score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.score-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);

  &.excellent {
    color: var(--accent-blue);
  }

  &.good {
    color: var(--accent-green);
  }

  &.average {
    color: var(--accent-orange);
  }

  &.poor {
    color: var(--accent-red);
  }
}

.detailed-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  border-left: 3px solid;

  &.pass {
    border-left-color: var(--accent-green);
  }

  &.fail {
    border-left-color: var(--accent-red);
  }
}

.result-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;

  &.pass {
    color: var(--accent-green);
  }

  &.fail {
    color: var(--accent-red);
  }
}

.result-info {
  flex: 1;
}

.result-category {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.result-score {
  font-size: 11px;
  color: var(--text-secondary);
}

.result-status {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.result-summary {
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.summary-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.summary-text {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.recommendations {
  h5 {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 8px 0;
  }

  ul {
    margin: 0;
    padding-left: 20px;

    li {
      font-size: 12px;
      color: var(--text-secondary);
      line-height: 1.6;
      margin-bottom: 4px;
    }
  }
}

.results-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--text-secondary);

  .placeholder-icon {
    width: 48px;
    height: 48px;
    opacity: 0.5;
  }

  p {
    font-size: 13px;
    margin: 0;
  }
}

.history-placeholder {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
  font-size: 13px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: var(--bg-primary);
  border-radius: 4px;
  border-left: 3px solid;

  &.pass {
    border-left-color: var(--accent-green);
  }

  &.fail {
    border-left-color: var(--accent-red);
  }
}

.history-time {
  flex: 1;
  font-size: 11px;
  color: var(--text-secondary);
}

.history-score {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.history-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;

  background: var(--bg-tertiary);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2952cc;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-secondary);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-success {
  background: var(--accent-green);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #229a8f;
}

.btn-success:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
