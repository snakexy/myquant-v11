<template>
  <div class="backtest">
    <div class="backtest-header">
      <h1 class="backtest-title">回测实验室</h1>
      <p class="backtest-subtitle">验证策略表现，优化投资参数</p>
    </div>
    
    <div class="backtest-container">
      <!-- 回测配置 -->
      <div class="backtest-config-section">
        <div class="section-header">
          <h3>回测配置</h3>
          <QuantButton
            type="primary"
            size="small"
            :loading="backtestLoading"
            @click="handleRunBacktest"
          >
            运行回测
          </QuantButton>
        </div>
        
        <div class="config-form">
          <QuantForm
            :model-value="backtestConfig"
            :rules="configRules"
            label-width="120px"
            size="medium"
          >
            <QuantFormItem label="策略选择" prop="strategyId">
              <QuantSelect
                v-model:value="backtestConfig.strategyId"
                :options="strategyOptions"
                placeholder="选择要回测的策略"
              />
            </QuantFormItem>
            
            <QuantFormItem label="时间范围" prop="dateRange">
              <div class="date-range">
                <QuantInput
                  v-model:value="backtestConfig.startDate"
                  type="date"
                  placeholder="开始日期"
                />
                <span class="date-separator">至</span>
                <QuantInput
                  v-model:value="backtestConfig.endDate"
                  type="date"
                  placeholder="结束日期"
                />
              </div>
            </QuantFormItem>
            
            <QuantFormItem label="股票池" prop="stockPool">
              <QuantInput
                v-model:value="backtestConfig.stockPool"
                type="textarea"
                :rows="3"
                placeholder="输入股票代码，如：000001.SZ,000002.SZ"
              />
            </QuantFormItem>
            
            <QuantFormItem label="初始资金" prop="initialCapital">
              <QuantInput
                v-model:value="backtestConfig.initialCapital"
                type="number"
                placeholder="100000"
                :suffix="'元'"
              />
            </QuantFormItem>
            
            <QuantFormItem label="基准指数" prop="benchmark">
              <QuantSelect
                v-model:value="backtestConfig.benchmark"
                :options="benchmarkOptions"
                placeholder="选择基准指数"
              />
            </QuantFormItem>
            
            <QuantFormItem label="手续费率" prop="commissionRate">
              <QuantInput
                v-model:value="backtestConfig.commissionRate"
                type="number"
                placeholder="0.0003"
                :suffix="'%'"
              />
            </QuantFormItem>
          </QuantForm>
        </div>
        
        <!-- 高级配置 -->
        <div class="advanced-config">
          <div class="section-header">
            <h4>高级配置</h4>
            <QuantButton
              type="ghost"
              size="small"
              @click="toggleAdvanced"
            >
              {{ showAdvanced ? '收起' : '展开' }}
            </QuantButton>
          </div>
          
          <div v-show="showAdvanced" class="advanced-form">
            <QuantForm
              :model-value="backtestConfig"
              label-width="120px"
              size="medium"
            >
              <QuantFormItem label="最大持仓" prop="maxPosition">
                <QuantInput
                  v-model:value="backtestConfig.maxPosition"
                  type="number"
                  placeholder="10"
                />
              </QuantFormItem>
              
              <QuantFormItem label="止损比例" prop="stopLoss">
                <QuantInput
                  v-model:value="backtestConfig.stopLoss"
                  type="number"
                  placeholder="0.05"
                  :suffix="'%'"
                />
              </QuantFormItem>
              
              <QuantFormItem label="止盈比例" prop="takeProfit">
                <QuantInput
                  v-model:value="backtestConfig.takeProfit"
                  type="number"
                  placeholder="0.1"
                  :suffix="'%'"
                />
              </QuantFormItem>
              
              <QuantFormItem label="再平衡频率" prop="rebalanceFrequency">
                <QuantSelect
                  v-model:value="backtestConfig.rebalanceFrequency"
                  :options="rebalanceOptions"
                  placeholder="选择再平衡频率"
                />
              </QuantFormItem>
            </QuantForm>
          </div>
        </div>
      </div>
      
      <!-- 回测结果 -->
      <div class="backtest-results-section">
        <div class="section-header">
          <h3>回测结果</h3>
          <div class="section-actions">
            <QuantButton
              v-if="backtestResult"
              type="ghost"
              size="small"
              icon="DownloadOutline"
              @click="handleExportResults"
            >
              导出结果
            </QuantButton>
            <QuantButton
              v-if="backtestResult"
              type="ghost"
              size="small"
              icon="ShareSocialOutline"
              @click="handleShareResults"
            >
              分享结果
            </QuantButton>
          </div>
        </div>
        
        <div v-if="!backtestResult" class="results-placeholder">
          <div class="placeholder-content">
            <n-icon size="48" color="#999">
              <BarChartOutline />
            </n-icon>
            <p>暂无回测结果</p>
            <p>配置参数并点击"运行回测"开始分析</p>
          </div>
        </div>
        
        <div v-else class="results-content">
          <!-- 关键指标 -->
          <div class="key-metrics">
            <h4>关键指标</h4>
            <div class="metrics-grid">
              <div class="metric-item">
                <label>总收益率</label>
                <span :class="getPerformanceClass(backtestResult.totalReturn)">
                  {{ formatPercent(backtestResult.totalReturn) }}
                </span>
              </div>
              <div class="metric-item">
                <label>年化收益率</label>
                <span :class="getPerformanceClass(backtestResult.annualReturn)">
                  {{ formatPercent(backtestResult.annualReturn) }}
                </span>
              </div>
              <div class="metric-item">
                <label>最大回撤</label>
                <span :class="getPerformanceClass(-backtestResult.maxDrawdown)">
                  {{ formatPercent(backtestResult.maxDrawdown) }}
                </span>
              </div>
              <div class="metric-item">
                <label>夏普比率</label>
                <span>{{ backtestResult.sharpeRatio?.toFixed(2) }}</span>
              </div>
              <div class="metric-item">
                <label>胜率</label>
                <span>{{ formatPercent(backtestResult.winRate) }}</span>
              </div>
              <div class="metric-item">
                <label>盈亏比</label>
                <span>{{ backtestResult.profitLossRatio?.toFixed(2) }}</span>
              </div>
              <div class="metric-item">
                <label>总交易次数</label>
                <span>{{ backtestResult.totalTrades }}</span>
              </div>
              <div class="metric-item">
                <label>信息比率</label>
                <span>{{ backtestResult.informationRatio?.toFixed(2) }}</span>
              </div>
            </div>
          </div>
          
          <!-- 收益曲线 -->
          <div class="return-curve">
            <h4>收益曲线</h4>
            <BaseChart
              :option="returnCurveOption"
              :loading="chartLoading"
              height="300px"
            />
          </div>
          
          <!-- 回撤分析 -->
          <div class="drawdown-analysis">
            <h4>回撤分析</h4>
            <BaseChart
              :option="drawdownOption"
              :loading="chartLoading"
              height="200px"
            />
          </div>
          
          <!-- 月度收益 -->
          <div class="monthly-returns">
            <h4>月度收益</h4>
            <BaseChart
              :option="monthlyReturnOption"
              :loading="chartLoading"
              height="250px"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { NIcon } from 'naive-ui'
import { BarChartOutline, DownloadOutline, ShareSocialOutline } from '@vicons/ionicons5'
import { useBacktestStore, useMessage } from '@/stores'
import QuantButton from '@/components/ui/Button.vue'
import QuantInput from '@/components/ui/Input.vue'
import QuantSelect from '@/components/ui/Select.vue'
import QuantForm from '@/components/ui/Form.vue'
import QuantFormItem from '@/components/ui/Form.vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import { formatPercent, formatDate } from '@/utils/format'
import { generateReturnCurveOption, generateDrawdownOption, generateMonthlyReturnOption } from '@/utils/chart'

const backtestStore = useBacktestStore()
const message = useMessage()

// 响应式数据
const backtestLoading = ref(false)
const chartLoading = ref(false)
const showAdvanced = ref(false)

const backtestConfig = reactive({
  strategyId: '',
  startDate: '',
  endDate: '',
  stockPool: '',
  initialCapital: 100000,
  benchmark: '000300.SH',
  commissionRate: 0.03,
  maxPosition: 10,
  stopLoss: 0.05,
  takeProfit: 0.1,
  rebalanceFrequency: 'monthly'
})

const backtestResult = ref(null)

// 配置规则
const configRules = {
  strategyId: [
    { required: true, message: '请选择策略', trigger: 'change' }
  ],
  startDate: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  endDate: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ],
  stockPool: [
    { required: true, message: '请输入股票代码', trigger: 'blur' }
  ],
  initialCapital: [
    { required: true, message: '请输入初始资金', trigger: 'blur' }
  ]
}

// 选项数据
const strategyOptions = computed(() => backtestStore.strategies.map(strategy => ({
  label: strategy.name,
  value: strategy.id
})))

const benchmarkOptions = [
  { label: '沪深300', value: '000300.SH' },
  { label: '上证50', value: '000016.SH' },
  { label: '中证500', value: '000905.SH' },
  { label: '创业板指', value: '399006.SZ' },
  { label: '科创50', value: '000688.SH' }
]

const rebalanceOptions = [
  { label: '每日', value: 'daily' },
  { label: '每周', value: 'weekly' },
  { label: '每月', value: 'monthly' },
  { label: '每季度', value: 'quarterly' }
]

// 图表选项
const returnCurveOption = computed(() => {
  if (!backtestResult.value) return {}
  
  return generateReturnCurveOption(backtestResult.value.returnCurve || [])
})

const drawdownOption = computed(() => {
  if (!backtestResult.value) return {}
  
  return generateDrawdownOption(backtestResult.value.drawdownData || [])
})

const monthlyReturnOption = computed(() => {
  if (!backtestResult.value) return {}
  
  return generateMonthlyReturnOption(backtestResult.value.monthlyReturns || [])
})

// 事件处理函数
const handleRunBacktest = async () => {
  backtestLoading.value = true
  try {
    const result = await backtestStore.runBacktest({
      ...backtestConfig,
      stockPool: backtestConfig.stockPool.split(',').map(code => code.trim())
    })
    
    backtestResult.value = result
    message.success('回测完成')
  } catch (error) {
    console.error('回测失败:', error)
    message.error('回测失败')
  } finally {
    backtestLoading.value = false
  }
}

const toggleAdvanced = () => {
  showAdvanced.value = !showAdvanced.value
}

const handleExportResults = () => {
  if (!backtestResult.value) return
  
  // 实现结果导出逻辑
  const dataStr = JSON.stringify(backtestResult.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `backtest_result_${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)
  
  message.success('结果已导出')
}

const handleShareResults = () => {
  if (!backtestResult.value) return
  
  // 实现结果分享逻辑
  const shareUrl = `${window.location.origin}/backtest/share/${backtestResult.value.id}`
  
  if (navigator.clipboard) {
    navigator.clipboard.writeText(shareUrl)
    message.success('分享链接已复制到剪贴板')
  } else {
    message.error('浏览器不支持剪贴板功能')
  }
}

// 工具函数
const getPerformanceClass = (value: number) => {
  if (value > 0) return 'performance-positive'
  if (value < 0) return 'performance-negative'
  return 'performance-neutral'
}

// 生命周期
onMounted(async () => {
  try {
    await backtestStore.fetchStrategies()
  } catch (error) {
    console.error('获取策略列表失败:', error)
    message.error('获取策略列表失败')
  }
})
</script>

<style lang="scss" scoped>
.backtest {
  padding: var(--spacing-4);
  max-width: 1400px;
  margin: 0 auto;
  
  &-header {
    text-align: center;
    margin-bottom: var(--spacing-6);
  }
  
  &-title {
    font-size: var(--font-size-xl);
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 var(--spacing-2) 0;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  &-subtitle {
    font-size: var(--font-size-base);
    color: var(--text-secondary);
    margin: 0;
  }
  
  &-container {
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: var(--spacing-4);
  }
  
  &-config-section, &-results-section {
    background: var(--bg-color-base);
    border: 1px solid var(--border-color)-base;
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-4);
  }
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-4);
    
    h3 {
      font-size: var(--font-size-lg);
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
    
    h4 {
      font-size: var(--font-size-base);
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
    
    .section-actions {
      display: flex;
      gap: var(--spacing-2);
    }
  }
  
  .config-form {
    margin-bottom: var(--spacing-4);
  }
  
  .advanced-config {
    border-top: 1px solid var(--border-color)-light;
    padding-top: var(--spacing-4);
    
    .advanced-form {
      margin-top: var(--spacing-4);
    }
  }
  
  .date-range {
    display: flex;
    align-items: center;
    gap: var(--spacing-2);
    
    .date-separator {
      color: var(--text-secondary);
      font-size: var(--font-size-sm);
    }
  }
  
  .results-placeholder {
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .placeholder-content {
      text-align: center;
      color: var(--text-secondary);
      
      p {
        margin: var(--spacing-2) 0;
      }
    }
  }
  
  .results-content {
    .key-metrics {
      margin-bottom: var(--spacing-4);
      
      .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: var(--spacing-3);
        
        .metric-item {
          padding: var(--spacing-3);
          background-color: var(--bg-color-secondary);
          border-radius: var(--border-radius-base);
          
          label {
            display: block;
            font-size: var(--font-size-sm);
            color: var(--text-secondary);
            margin-bottom: var(--spacing-1);
          }
          
          span {
            font-size: var(--font-size-lg);
            font-weight: 600;
            color: var(--text-primary);
          }
        }
      }
    }
    
    .return-curve, .drawdown-analysis, .monthly-returns {
      margin-bottom: var(--spacing-4);
      
      h4 {
        font-size: var(--font-size-base);
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 var(--spacing-3) 0;
      }
    }
  }
}

.performance-positive {
  color: var(--success-color);
}

.performance-negative {
  color: var(--danger-color);
}

.performance-neutral {
  color: var(--text-primary);
}

// 响应式设计
@media (max-width: 1200px) {
  .backtest {
    &-container {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 768px) {
  .backtest {
    padding: var(--spacing-2);
    
    .metrics-grid {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .date-range {
      flex-direction: column;
      align-items: stretch;
      gap: var(--spacing-2);
      
      .date-separator {
        text-align: center;
      }
    }
    
    .section-header {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--spacing-2);
    }
  }
}
</style>