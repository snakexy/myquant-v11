<template>
  <el-card class="backtest-form-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">📊 回测配置</span>
        <el-button type="primary" size="small" @click="resetForm">重置</el-button>
      </div>
    </template>

    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      label-position="left"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <div class="section-title">基本信息</div>

        <el-form-item label="策略名称" prop="strategy_name">
          <el-input
            v-model="formData.strategy_name"
            placeholder="请输入策略名称"
            clearable
          />
        </el-form-item>

        <el-form-item label="策略类型" prop="strategy_type">
          <el-select
            v-model="formData.strategy_type"
            placeholder="请选择策略类型"
            style="width: 100%"
          >
            <el-option
              v-for="type in strategyTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>
      </div>

      <!-- 回测时间范围 -->
      <div class="form-section">
        <div class="section-title">回测时间范围</div>

        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="formData.start_date"
            type="date"
            placeholder="选择开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="formData.end_date"
            type="date"
            placeholder="选择结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </div>

      <!-- 资金与股票池 -->
      <div class="form-section">
        <div class="section-title">资金与股票池</div>

        <el-form-item label="初始资金" prop="initial_capital">
          <el-input-number
            v-model="formData.initial_capital"
            :min="10000"
            :max="100000000"
            :step="100000"
            :precision="0"
            placeholder="请输入初始资金"
            style="width: 100%"
          />
          <div class="form-tip">建议金额: 100万 - 1000万</div>
        </el-form-item>

        <el-form-item label="股票池" prop="symbols">
          <el-select
            v-model="formData.symbols"
            multiple
            filterable
            allow-create
            placeholder="请选择或输入股票代码"
            style="width: 100%"
          >
            <el-option
              v-for="stock in commonStocks"
              :key="stock.code"
              :label="`${stock.code} - ${stock.name}`"
              :value="stock.code"
            />
          </el-select>
          <div class="form-tip">已选择 {{ formData.symbols.length }} 只股票（最多500只）</div>
        </el-form-item>

        <el-form-item label="基准指数" prop="benchmark">
          <el-select
            v-model="formData.benchmark"
            placeholder="请选择基准指数"
            style="width: 100%"
          >
            <el-option
              v-for="index in benchmarkIndexes"
              :key="index.code"
              :label="`${index.code} - ${index.name}`"
              :value="index.code"
            />
          </el-select>
        </el-form-item>
      </div>

      <!-- 交易参数 -->
      <div class="form-section">
        <div class="section-title">
          交易参数
          <el-tooltip content="设置交易手续费和滑点" placement="top">
            <el-icon><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>

        <el-form-item label="手续费率" prop="commission">
          <el-slider
            v-model="formData.commission"
            :min="0"
            :max="0.005"
            :step="0.0001"
            :format-tooltip="(val) => `${(val * 100).toFixed(3)}%`"
            show-input
            :show-input-controls="false"
          />
          <div class="form-tip">当前: {{ (formData.commission * 100).toFixed(3) }}%</div>
        </el-form-item>

        <el-form-item label="滑点率" prop="slippage">
          <el-slider
            v-model="formData.slippage"
            :min="0"
            :max="0.01"
            :step="0.001"
            :format-tooltip="(val) => `${(val * 100).toFixed(2)}%`"
            show-input
            :show-input-controls="false"
          />
          <div class="form-tip">当前: {{ (formData.slippage * 100).toFixed(2) }}%</div>
        </el-form-item>
      </div>

      <!-- 策略参数 -->
      <div class="form-section" v-if="showStrategyParams">
        <div class="section-title">策略参数</div>

        <!-- TopkDropout策略参数 -->
        <template v-if="formData.strategy_type === 'topk_dropout'">
          <el-form-item label="Top-K">
            <el-input-number
              v-model="formData.parameters.topk"
              :min="1"
              :max="100"
              placeholder="持仓股票数"
            />
          </el-form-item>

          <el-form-item label="Drop-N">
            <el-input-number
              v-model="formData.parameters.n_drop"
              :min="1"
              :max="20"
              placeholder="调仓股票数"
            />
          </el-form-item>
        </template>

        <!-- 其他策略参数可以继续添加 -->
      </div>

      <!-- 提交按钮 -->
      <div class="form-actions">
        <el-button @click="resetForm">重置</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ loading ? '提交中...' : '开始回测' }}
        </el-button>
      </div>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import type { BacktestExecuteRequest } from '@/api/unifiedBacktest'

// Props
interface Props {
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// Emits
const emit = defineEmits<{
  submit: [data: BacktestExecuteRequest]
}>()

// Form ref
const formRef = ref<FormInstance>()

// Form data
const formData = reactive<BacktestExecuteRequest>({
  strategy_name: '',
  strategy_type: 'topk_dropout',
  start_date: '2020-01-01',
  end_date: '2023-12-31',
  initial_capital: 1000000,
  symbols: [],
  benchmark: 'SH000300',
  parameters: {
    topk: 30,
    n_drop: 5,
    signal: '$pred'
  },
  commission: 0.0003,
  slippage: 0.0
})

// Strategy types
const strategyTypes = [
  { label: 'TopkDropout策略', value: 'topk_dropout' },
  { label: '动量策略', value: 'momentum' },
  { label: '均值回归策略', value: 'mean_reversion' },
  { label: '双均线策略', value: 'dual_ma' }
]

// Common stocks
const commonStocks = [
  { code: '600519.SH', name: '贵州茅台' },
  { code: '000858.SZ', name: '五粮液' },
  { code: '600036.SH', name: '招商银行' },
  { code: '000001.SZ', name: '平安银行' },
  { code: '601318.SH', name: '中国平安' },
  { code: '600276.SH', name: '恒瑞医药' },
  { code: '000333.SZ', name: '美的集团' },
  { code: '600900.SH', name: '长江电力' }
]

// Benchmark indexes
const benchmarkIndexes = [
  { code: 'SH000300', name: '沪深300' },
  { code: 'SH000905', name: '中证500' },
  { code: 'SZ399001', name: '深证成指' },
  { code: 'SH000016', name: '上证50' },
  { code: 'SZ399006', name: '创业板指' }
]

// Form rules
const formRules: FormRules = {
  strategy_name: [
    { required: true, message: '请输入策略名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' },
    {
      validator: (rule, value, callback) => {
        if (new Date(value) <= new Date(formData.start_date)) {
          callback(new Error('结束日期必须大于开始日期'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  initial_capital: [
    { required: true, message: '请输入初始资金', trigger: 'blur' },
    { type: 'number', min: 10000, message: '初始资金不能小于10000', trigger: 'blur' }
  ],
  symbols: [
    { required: true, message: '请选择股票池', trigger: 'change' },
    {
      validator: (rule, value, callback) => {
        if (value.length === 0) {
          callback(new Error('至少选择1只股票'))
        } else if (value.length > 500) {
          callback(new Error('最多选择500只股票'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  benchmark: [
    { required: true, message: '请选择基准指数', trigger: 'change' }
  ]
}

// Show strategy params
const showStrategyParams = computed(() => {
  return formData.strategy_type === 'topk_dropout'
})

// Reset form
const resetForm = () => {
  formRef.value?.resetFields()
  formData.strategy_name = ''
  formData.strategy_type = 'topk_dropout'
  formData.start_date = '2020-01-01'
  formData.end_date = '2023-12-31'
  formData.initial_capital = 1000000
  formData.symbols = []
  formData.benchmark = 'SH000300'
  formData.parameters = {
    topk: 30,
    n_drop: 5,
    signal: '$pred'
  }
  formData.commission = 0.0003
  formData.slippage = 0.0
}

// Handle submit
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    if (formData.symbols.length === 0) {
      ElMessage.warning('请至少选择1只股票')
      return
    }

    emit('submit', { ...formData })
  } catch (error) {
    ElMessage.error('请检查表单填写是否正确')
  }
}
</script>

<style scoped lang="scss">
.backtest-form-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .form-section {
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid #ebeef5;

    &:last-of-type {
      border-bottom: none;
    }

    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: #606266;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
  }
}
</style>
