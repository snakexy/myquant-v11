<template>
  <div class="step-factor-evaluation-panel">
    <!-- 评估配置 -->
    <div class="config-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
        {{ isZh ? '因子评估配置' : 'Factor Evaluation Configuration' }}
      </h3>

      <div class="config-form">
        <div class="form-group">
          <label class="form-label">{{ isZh ? '评估方法' : 'Evaluation Method' }}</label>
          <el-select v-model="evaluationConfig.method" style="width: 100%;">
            <el-option :label="isZh ? 'IC/IR分析' : 'IC/IR Analysis'" value="icir"></el-option>
            <el-option :label="isZh ? '回测分析' : 'Backtest Analysis'" value="backtest"></el-option>
            <el-option :label="isZh ? '稳定性测试' : 'Stability Test'" value="stability"></el-option>
            <el-option :label="isZh ? '组合评估' : 'Combined' value="combined"></el-option>
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '评估周期' : 'Evaluation Period' }}</label>
          <el-select v-model="evaluationConfig.period" style="width: 100%;">
            <el-option label="1 {{ isZh ? '天' : 'Day' }}" value="1d"></el-option>
            <el-option label="5 {{ isZh ? '天' : 'Days' }}" value="5d"></el-option>
            <el-option label="10 {{ isZh ? '天' : 'Days' }}" value="10d"></el-option>
            <el-option label="20 {{ isZh ? '天' : 'Days' }}" value="20d"></el-option>
            <el-option label="60 {{ isZh ? '天' : 'Days' }}" value="60d"></el-option>
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? 'IC阈值' : 'IC Threshold' }}</label>
          <el-slider
            v-model="evaluationConfig.icThreshold"
            :min="0"
            :max="0.1"
            :step="0.005"
            :format-tooltip="formatICThreshold"
          />
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? 'IR阈值' : 'IR Threshold' }}</label>
          <el-slider
            v-model="evaluationConfig.irThreshold"
            :min="0"
            :max="2"
            :step="0.1"
            :format-tooltip="formatIRThreshold"
          />
        </div>
      </div>
    </div>

    <!-- 评估指标 -->
    <div class="metrics-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="3" y1="9" x2="21" y2="9"></line>
          <line x1="9" y1="21" x2="9" y2="9"></line>
        </svg>
        {{ isZh ? '评估指标' : 'Evaluation Metrics' }}
      </h3>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
          </div>
          <div class="metric-label">{{ isZh ? '平均IC' : 'Avg IC' }}</div>
          <div class="metric-value" :class="getICClass(evaluationResult.avgIC)">
            {{ evaluationResult.avgIC?.toFixed(4) || '-' }}
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
              <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
            </svg>
          </div>
          <div class="metric-label">IR</div>
          <div class="metric-value" :class="getIRClass(evaluationResult.ir)">
            {{ evaluationResult.ir?.toFixed(4) || '-' }}
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 3v18h18"/>
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
            </svg>
          </div>
          <div class="metric-label">{{ isZh ? 'Rank IC' : 'Rank IC' }}</div>
          <div class="metric-value" :class="getICClass(evaluationResult.rankIC)">
            {{ evaluationResult.rankIC?.toFixed(4) || '-' }}
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div class="metric-label">{{ isZh ? 'IC胜率' : 'IC Win Rate' }}</div>
          <div class="metric-value" :class="getWinRateClass(evaluationResult.icWinRate)">
            {{ evaluationResult.icWinRate ? `${(evaluationResult.icWinRate * 100).toFixed(1)}%` : '-' }}
          </div>
        </div>
      </div>
    </div>

    <!-- 评估报告 -->
    <div class="report-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
        {{ isZh ? '评估报告' : 'Evaluation Report' }}
      </h3>

      <div v-if="evaluationResult.completed" class="report-content">
        <div class="report-summary">
          <div class="summary-item">
            <span class="summary-label">{{ isZh ? '评估状态' : 'Status' }}:</span>
            <span :class="['summary-value', getStatusClass(evaluationResult.status)]">
              {{ isZh ? (evaluationResult.status === 'pass' ? '通过' : '未通过') : evaluationResult.status }}
            </span>
          </div>
          <div class="summary-item">
            <span class="summary-label">{{ isZh ? '评估时间' : 'Evaluated At' }}:</span>
            <span class="summary-value">{{ evaluationResult.evaluatedAt }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">{{ isZh ? '评估因子数' : 'Factors Evaluated' }}:</span>
            <span class="summary-value">{{ evaluationResult.totalFactors }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">{{ isZh ? '合格因子数' : 'Qualified Factors' }}:</span>
            <span class="summary-value">{{ evaluationResult.qualifiedFactors }}</span>
          </div>
        </div>

        <div class="report-details">
          <h4 class="details-title">{{ isZh ? '详细说明' : 'Details' }}</h4>
          <p class="details-text">{{ evaluationResult.details }}</p>
        </div>
      </div>

      <div v-else class="report-placeholder">
        <div class="placeholder-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="12" y1="18" x2="12" y2="12"/>
            <line x1="9" y1="15" x2="15" y2="15"/>
          </svg>
        </div>
        <p>{{ isZh ? '点击下方按钮开始评估' : 'Click the button below to start evaluation' }}</p>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <button class="btn btn-primary" @click="runEvaluation" :disabled="isEvaluating">
        {{ isEvaluating ? (isZh ? '评估中...' : 'Evaluating...') : (isZh ? '开始评估' : 'Start Evaluation') }}
      </button>
      <button class="btn btn-secondary" @click="exportReport" :disabled="!evaluationResult.completed">
        {{ isZh ? '导出报告' : 'Export Report' }}
      </button>
      <button class="btn btn-success" @click="completeStep" :disabled="!evaluationResult.completed">
        {{ isZh ? '完成当前步骤' : 'Complete Step' }} ✓
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
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

// 评估配置
const evaluationConfig = reactive({
  method: 'icir',
  period: '5d',
  icThreshold: 0.03,
  irThreshold: 0.5
})

// 评估结果
const evaluationResult = reactive({
  completed: false,
  status: 'pass',
  avgIC: 0.0456,
  ir: 0.78,
  rankIC: 0.0523,
  icWinRate: 0.65,
  totalFactors: 168,
  qualifiedFactors: 98,
  evaluatedAt: '',
  details: ''
})

const isEvaluating = ref(false)

// 格式化阈值
const formatICThreshold = (value: number) => {
  return value.toFixed(3)
}

const formatIRThreshold = (value: number) => {
  return value.toFixed(2)
}

// 获取样式类
const getICClass = (ic: number | undefined) => {
  if (!ic) return ''
  if (ic >= 0.05) return 'excellent'
  if (ic >= 0.03) return 'good'
  if (ic >= 0) return 'average'
  return 'poor'
}

const getIRClass = (ir: number | undefined) => {
  if (!ir) return ''
  if (ir >= 1.0) return 'excellent'
  if (ir >= 0.5) return 'good'
  if (ir >= 0) return 'average'
  return 'poor'
}

const getWinRateClass = (rate: number | undefined) => {
  if (!rate) return ''
  if (rate >= 0.6) return 'excellent'
  if (rate >= 0.5) return 'good'
  if (rate >= 0) return 'average'
  return 'poor'
}

const getStatusClass = (status: string) => {
  return status === 'pass' ? 'pass' : 'fail'
}

// 运行评估
const runEvaluation = async () => {
  isEvaluating.value = true
  try {
    // 模拟评估过程
    await new Promise(resolve => setTimeout(resolve, 2000))

    evaluationResult.completed = true
    evaluationResult.status = evaluationResult.avgIC >= evaluationConfig.icThreshold ? 'pass' : 'fail'
    evaluationResult.evaluatedAt = new Date().toLocaleString()
    evaluationResult.qualifiedFactors = Math.round(evaluationResult.totalFactors * 0.58)

    evaluationResult.details = isZh.value
      ? `本次评估共测试 ${evaluationResult.totalFactors} 个因子，其中 ${evaluationResult.qualifiedFactors} 个因子通过评估。平均IC为 ${evaluationResult.avgIC.toFixed(4)}，IR为 ${evaluationResult.ir.toFixed(4)}，IC胜率为 ${(evaluationResult.icWinRate * 100).toFixed(1)}%。根据设定的阈值（IC ≥ ${evaluationConfig.icThreshold.toFixed(3)}, IR ≥ ${evaluationConfig.irThreshold.toFixed(2)}），${evaluationResult.status === 'pass' ? '因子整体表现良好，建议进入下一阶段。' : '因子表现未达标，建议调整因子或参数。'}`
      : `Evaluated ${evaluationResult.totalFactors} factors, ${evaluationResult.qualifiedFactors} passed. Average IC: ${evaluationResult.avgIC.toFixed(4)}, IR: ${evaluationResult.ir.toFixed(4)}, IC Win Rate: ${(evaluationResult.icWinRate * 100).toFixed(1)}%. Based on threshold (IC ≥ ${evaluationConfig.icThreshold.toFixed(3)}, IR ≥ ${evaluationConfig.irThreshold.toFixed(2)}), ${evaluationResult.status === 'pass' ? 'Factors perform well, proceed to next stage.' : 'Factors underperform, consider adjustment.'}`

    ElMessage.success(isZh.value ? '评估完成' : 'Evaluation completed')
    emit('dataUpdate', evaluationResult)
  } catch (error) {
    console.error('Evaluation failed:', error)
    ElMessage.error(isZh.value ? '评估失败' : 'Evaluation failed')
  } finally {
    isEvaluating.value = false
  }
}

// 导出报告
const exportReport = () => {
  console.log('Exporting evaluation report...')
  ElMessage.success(isZh.value ? '报告已导出' : 'Report exported')
}

// 完成步骤
const completeStep = () => {
  emit('stepComplete', { step: 4, evaluationResult })
}
</script>

<style scoped lang="scss">
.step-factor-evaluation-panel {
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
.metrics-section,
.report-section {
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

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.metric-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.metric-icon {
  width: 28px;
  height: 28px;
  color: var(--text-secondary);
}

.metric-label {
  font-size: 11px;
  color: var(--text-secondary);
  text-align: center;
}

.metric-value {
  font-size: 18px;
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

.report-content {
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

.report-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
}

.summary-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.summary-value {
  font-size: 12px;
  color: var(--text-primary);
  font-weight: 600;

  &.pass {
    color: var(--accent-green);
  }

  &.fail {
    color: var(--accent-red);
  }
}

.report-details {
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.details-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.details-text {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.report-placeholder {
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
