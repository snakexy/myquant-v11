<template>
  <div class="model-training-config">
    <el-form label-position="top" size="small">
      <!-- 模型类型 -->
      <el-form-item label="模型类型">
        <el-select v-model="localParams.modelType" style="width: 100%">
          <el-option label="XGBoost" value="xgboost" />
          <el-option label="LightGBM" value="lightgbm" />
          <el-option label="LSTM" value="lstm" />
          <el-option label="Transformer" value="transformer" />
          <el-option label="线性回归" value="linear" />
          <el-option label="随机森林" value="random-forest" />
        </el-select>
        <div class="form-tip">选择要训练的模型类型</div>
      </el-form-item>

      <!-- 训练参数 -->
      <div class="section-title">训练参数</div>

      <el-form-item label="测试集比例">
        <el-slider
          v-model="localParams.trainParams.testSize"
          :min="0.1"
          :max="0.4"
          :step="0.05"
          :format-tooltip="(v) => (v * 100).toFixed(0) + '%'"
        />
        <div class="form-tip">测试集占总数据的比例</div>
      </el-form-item>

      <el-form-item label="交叉验证折数">
        <el-input-number
          v-model="localParams.trainParams.cvFolds"
          :min="2"
          :max="10"
          style="width: 100%"
        />
        <div class="form-tip">K折交叉验证的折数</div>
      </el-form-item>

      <el-form-item label="随机种子">
        <el-input-number
          v-model="localParams.trainParams.randomSeed"
          :min="0"
          :max="9999"
          style="width: 100%"
        />
        <div class="form-tip">用于结果复现的随机种子</div>
      </el-form-item>

      <!-- 目标变量 -->
      <div class="section-title">目标变量</div>

      <el-form-item label="目标列名">
        <el-input
          v-model="localParams.targetColumn"
          placeholder="return"
        />
        <div class="form-tip">预测目标变量的列名</div>
      </el-form-item>

      <!-- 评估指标 -->
      <div class="section-title">评估指标</div>

      <el-form-item label="选择指标">
        <el-checkbox-group v-model="localParams.metrics">
          <el-checkbox value="accuracy">准确率</el-checkbox>
          <el-checkbox value="precision">精确率</el-checkbox>
          <el-checkbox value="recall">召回率</el-checkbox>
          <el-checkbox value="f1">F1分数</el-checkbox>
          <el-checkbox value="sharpe">夏普比率</el-checkbox>
          <el-checkbox value="max-drawdown">最大回撤</el-checkbox>
          <el-checkbox value="win-rate">胜率</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
    </el-form>

    <!-- 训练状态显示 -->
    <div class="training-status" v-if="trainingStatus">
      <el-divider />
      <div class="status-header">训练状态</div>
      <div class="status-content">
        <el-tag :type="statusType" size="large">
          {{ statusText }}
        </el-tag>
        <div v-if="trainingStatus === 'completed'" class="metrics-display">
          <div class="metric-item">
            <span class="metric-label">准确率:</span>
            <span class="metric-value">{{ trainingData?.accuracy || '--' }}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">夏普比率:</span>
            <span class="metric-value">{{ trainingData?.sharpe || '--' }}</span>
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
  modelType: 'xgboost',
  trainParams: {
    testSize: 0.2,
    cvFolds: 5,
    randomSeed: 42
  },
  featureColumns: [],
  targetColumn: 'return',
  metrics: ['accuracy', 'precision', 'recall', 'sharpe', 'max-drawdown'],
  ...props.params
})

// 训练状态
const trainingStatus = computed(() => props.data?.content?.trainingStatus)
const trainingData = computed(() => props.data?.content)

const statusType = computed(() => {
  switch (trainingStatus.value) {
    case 'completed': return 'success'
    case 'training': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
})

const statusText = computed(() => {
  switch (trainingStatus.value) {
    case 'completed': return '训练完成'
    case 'training': return '训练中...'
    case 'failed': return '训练失败'
    case 'pending': return '待训练'
    case 'waiting': return '等待输入'
    default: return '未开始'
  }
})

// 监听参数变化
watch(localParams, (newParams) => {
  emit('update:params', { ...newParams })
}, { deep: true })
</script>

<style scoped>
.model-training-config {
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

.training-status {
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
  font-size: 12px;
  padding: 4px 8px;
  background: #f9fafb;
  border-radius: 4px;
}

.metric-label {
  color: #6b7280;
}

.metric-value {
  color: #374151;
  font-weight: 600;
}
</style>
