<template>
  <div class="preliminary-validation-config">
    <el-form label-position="top" size="small">
      <!-- 回测时间范围 -->
      <div class="section-title">回测时间范围</div>

      <el-form-item label="开始日期">
        <el-date-picker
          v-model="startDateValue"
          type="date"
          placeholder="选择开始日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="结束日期">
        <el-date-picker
          v-model="endDateValue"
          type="date"
          placeholder="选择结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>

      <!-- 交易参数 -->
      <div class="section-title">交易参数</div>

      <el-form-item label="初始资金">
        <el-input-number
          v-model="localParams.initialCapital"
          :min="1000"
          :max="10000000"
          :step="10000"
          style="width: 100%"
        />
        <div class="form-tip">回测的初始资金量</div>
      </el-form-item>

      <el-form-item label="手续费率">
        <el-slider
          v-model="localParams.commission"
          :min="0"
          :max="0.001"
          :step="0.00001"
          :format-tooltip="(v) => (v * 10000).toFixed(1) + '‱'"
        />
        <div class="form-tip">交易手续费率（默认万三）</div>
      </el-form-item>

      <el-form-item label="滑点率">
        <el-slider
          v-model="localParams.slippage"
          :min="0"
          :max="0.001"
          :step="0.00001"
          :format-tooltip="(v) => (v * 10000).toFixed(1) + '‱'"
        />
        <div class="form-tip">交易滑点率</div>
      </el-form-item>

      <!-- 评估指标 -->
      <div class="section-title">评估指标</div>

      <el-form-item label="选择指标">
        <el-checkbox-group v-model="localParams.metrics">
          <el-checkbox value="return">总收益率</el-checkbox>
          <el-checkbox value="annual-return">年化收益率</el-checkbox>
          <el-checkbox value="sharpe">夏普比率</el-checkbox>
          <el-checkbox value="max-drawdown">最大回撤</el-checkbox>
          <el-checkbox value="win-rate">胜率</el-checkbox>
          <el-checkbox value="profit-factor">盈亏比</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
    </el-form>

    <!-- 验证状态显示 -->
    <div class="validation-status" v-if="validationStatus">
      <el-divider />
      <div class="status-header">回测结果</div>
      <div class="status-content">
        <el-tag :type="statusType" size="large">
          {{ statusText }}
        </el-tag>
        <div v-if="validationStatus === 'completed'" class="metrics-display">
          <div class="metric-item success">
            <span class="metric-label">总收益率:</span>
            <span class="metric-value">{{ validationData?.totalReturn || '--' }}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">夏普比率:</span>
            <span class="metric-value">{{ validationData?.sharpeRatio || '--' }}</span>
          </div>
          <div class="metric-item danger">
            <span class="metric-label">最大回撤:</span>
            <span class="metric-value">{{ validationData?.maxDrawdown || '--' }}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">胜率:</span>
            <span class="metric-value">{{ validationData?.winRate || '--' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  params: Record<string, any>
  data?: any
}

interface Emits {
  (e: 'update:params', value: Record<string, any>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 本地参数副本
const localParams = ref<Record<string, any>>({
  backtestPeriod: {
    start: '',
    end: ''
  },
  initialCapital: 100000,
  commission: 0.0003,
  slippage: 0.0001,
  metrics: ['return', 'sharpe', 'max-drawdown', 'win-rate', 'profit-factor'],
  ...props.params
})

// 日期值
const startDateValue = computed({
  get: () => localParams.value.backtestPeriod?.start || '',
  set: (val) => {
    if (!localParams.value.backtestPeriod) {
      localParams.value.backtestPeriod = {}
    }
    localParams.value.backtestPeriod.start = val
    emitParams()
  }
})

const endDateValue = computed({
  get: () => localParams.value.backtestPeriod?.end || '',
  set: (val) => {
    if (!localParams.value.backtestPeriod) {
      localParams.value.backtestPeriod = {}
    }
    localParams.value.backtestPeriod.end = val
    emitParams()
  }
})

// 验证状态
const validationStatus = computed(() => props.data?.content?.validationStatus)
const validationData = computed(() => props.data?.content)

const statusType = computed(() => {
  switch (validationStatus.value) {
    case 'completed': return 'success'
    case 'validating': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
})

const statusText = computed(() => {
  switch (validationStatus.value) {
    case 'completed': return '验证完成'
    case 'validating': return '验证中...'
    case 'failed': return '验证失败'
    case 'pending': return '待验证'
    case 'waiting': return '等待模型'
    default: return '未开始'
  }
})

// 发送参数更新
const emitParams = () => {
  emit('update:params', { ...localParams.value })
}

// 监听参数变化
watch(localParams, () => {
  emitParams()
}, { deep: true })
</script>

<style scoped>
.preliminary-validation-config {
  padding: 8px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin: 12px 0 8px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #e5e7eb;
}

.form-tip {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
  line-height: 1.4;
}

.validation-status {
  margin-top: 16px;
}

.status-header {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metrics-display {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding: 6px 8px;
  background: #f9fafb;
  border-radius: 4px;
}

.metric-item.success {
  background: #ecfdf5;
  border-left: 3px solid #10b981;
}

.metric-item.danger {
  background: #fef2f2;
  border-left: 3px solid #ef4444;
}

.metric-label {
  color: #6b7280;
  font-weight: 500;
}

.metric-value {
  color: #374151;
  font-weight: 700;
  font-size: 13px;
}
</style>
