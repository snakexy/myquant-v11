<template>
  <div class="factor-calculation-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="phase-badge research">🔬 研究阶段</div>
          <h1 class="page-title"><i class="fas fa-calculator"></i> 因子计算</h1>
          <p class="page-subtitle">技术指标 • Alpha158 • Alpha360 • 自定义因子</p>
        </div>
      </div>
    </div>

    <!-- 功能标签页 -->
    <el-tabs v-model="activeTab" class="calculation-tabs">
      <!-- 技术指标计算 -->
      <el-tab-pane label="技术指标" name="indicators">
        <el-card class="indicators-card">
          <template #header>
            <span>技术指标计算</span>
          </template>

          <el-form :model="indicatorForm" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="股票代码">
                  <el-input
                    v-model="indicatorForm.symbol"
                    placeholder="例如: 000001.SZ"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="indicatorForm.dateRange"
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

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="K线周期">
                  <el-select v-model="indicatorForm.period">
                    <el-option label="日线" value="day" />
                    <el-option label="周线" value="week" />
                    <el-option label="月线" value="month" />
                    <el-option label="1分钟" value="1min" />
                    <el-option label="5分钟" value="5min" />
                    <el-option label="15分钟" value="15min" />
                    <el-option label="30分钟" value="30min" />
                    <el-option label="60分钟" value="60min" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="选择指标">
                  <el-select
                    v-model="indicatorForm.selectedIndicators"
                    multiple
                    placeholder="选择要计算的技术指标"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="ind in availableIndicators"
                      :key="ind.name"
                      :label="`${ind.name} - ${ind.description}`"
                      :value="ind.name"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <!-- 指标分类快速选择 -->
            <el-form-item label="快速选择">
              <el-space>
                <el-button size="small" @click="selectIndicatorsByType('overlay')">趋势指标</el-button>
                <el-button size="small" @click="selectIndicatorsByType('oscillator')">震荡指标</el-button>
                <el-button size="small" @click="selectIndicatorsByType('momentum')">动量指标</el-button>
                <el-button size="small" @click="selectIndicatorsByType('volume')">成交量指标</el-button>
              </el-space>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="calculateIndicators"
                :loading="calculatingIndicators"
                :disabled="!indicatorForm.symbol || indicatorForm.selectedIndicators.length === 0"
              >
                <el-icon><DataAnalysis /></el-icon>
                开始计算
              </el-button>
              <el-button @click="resetIndicatorForm">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 计算结果 -->
          <div v-if="indicatorResult" class="result-section">
            <el-divider content-position="left">计算结果</el-divider>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="股票代码">
                {{ indicatorResult.symbol }}
              </el-descriptions-item>
              <el-descriptions-item label="计算指标数">
                {{ Object.keys(indicatorResult.indicators).length }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- 指标数据表格 -->
            <el-table :data="getIndicatorTableData()" border style="margin-top: 20px">
              <el-table-column prop="name" label="指标名称" width="150" />
              <el-table-column label="数据预览" width="200">
                <template #default="{ row }">
                  <span v-if="row.preview">{{ row.preview }}</span>
                  <span v-else class="text-muted">...</span>
                </template>
              </el-table-column>
              <el-table-column label="数据点数" width="100">
                <template #default="{ row }">
                  {{ row.count }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- Alpha158因子 -->
      <el-tab-pane label="Alpha158" name="alpha158">
        <el-card class="alpha158-card">
          <template #header>
            <span>Alpha158因子计算</span>
          </template>

          <el-form :model="alpha158Form" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="股票代码">
                  <el-select
                    v-model="alpha158Form.symbols"
                    multiple
                    filterable
                    allow-create
                    placeholder="输入股票代码，可添加多个"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="stock in availableStocks"
                      :key="stock"
                      :label="stock"
                      :value="stock"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="alpha158Form.dateRange"
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
                <el-form-item label="K线周期">
                  <el-select v-model="alpha158Form.period">
                    <el-option label="日线" value="day" />
                    <el-option label="周线" value="week" />
                    <el-option label="月线" value="month" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-alert
                title="Alpha158因子"
                type="info"
                :closable="false"
                style="margin-bottom: 20px"
              >
                158个经典Alpha因子，涵盖价格、成交量、技术指标等多个维度
              </el-alert>

              <el-button
                type="primary"
                @click="calculateAlpha158"
                :loading="calculatingAlpha158"
                :disabled="alpha158Form.symbols.length === 0"
              >
                <el-icon><DataAnalysis /></el-icon>
                开始计算
              </el-button>
              <el-button @click="resetAlpha158Form">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 计算结果 -->
          <div v-if="alpha158Result" class="result-section">
            <el-divider content-position="left">计算结果</el-divider>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="股票数量">
                {{ alpha158Result.symbols.length }}
              </el-descriptions-item>
              <el-descriptions-item label="因子数量">
                158
              </el-descriptions-item>
              <el-descriptions-item label="开始日期" :span="2">
                {{ alpha158Result.start_date }}
              </el-descriptions-item>
              <el-descriptions-item label="结束日期" :span="2">
                {{ alpha158Result.end_date }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- 因子数据预览 -->
            <el-divider content-position="left">因子预览</el-divider>
            <el-table :data="Object.keys(alpha158Result.factors).slice(0, 10)" border>
              <el-table-column prop label="因子名称" width="150" />
              <el-table-column label="数据预览">
                <template #default="{ row }">
                  {{ getFactorPreview(row) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- Alpha360因子 -->
      <el-tab-pane label="Alpha360" name="alpha360">
        <el-card class="alpha360-card">
          <template #header>
            <span>Alpha360因子计算</span>
          </template>

          <el-form :model="alpha360Form" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="股票代码">
                  <el-select
                    v-model="alpha360Form.symbols"
                    multiple
                    filterable
                    allow-create
                    placeholder="输入股票代码，可添加多个"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="stock in availableStocks"
                      :key="stock"
                      :label="stock"
                      :value="stock"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="alpha360Form.dateRange"
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
                <el-form-item label="K线周期">
                  <el-select v-model="alpha360Form.period">
                    <el-option label="日线" value="day" />
                    <el-option label="周线" value="week" />
                    <el-option label="月线" value="month" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-alert
                title="Alpha360因子"
                type="warning"
                :closable="false"
                style="margin-bottom: 20px"
              >
                360个扩展Alpha因子，在Alpha158基础上增加了更多技术指标组合
              </el-alert>

              <el-button
                type="primary"
                @click="calculateAlpha360"
                :loading="calculatingAlpha360"
                :disabled="alpha360Form.symbols.length === 0"
              >
                <el-icon><DataAnalysis /></el-icon>
                开始计算
              </el-button>
              <el-button @click="resetAlpha360Form">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 计算结果 -->
          <div v-if="alpha360Result" class="result-section">
            <el-divider content-position="left">计算结果</el-divider>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="股票数量">
                {{ alpha360Result.symbols.length }}
              </el-descriptions-item>
              <el-descriptions-item label="因子数量">
                360
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 自定义因子 -->
      <el-tab-pane label="自定义因子" name="custom">
        <el-card class="custom-factor-card">
          <template #header>
            <span>自定义因子计算</span>
          </template>

          <el-form :model="customForm" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="股票代码">
                  <el-select
                    v-model="customForm.symbols"
                    multiple
                    filterable
                    allow-create
                    placeholder="输入股票代码，可添加多个"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="stock in availableStocks"
                      :key="stock"
                      :label="stock"
                      :value="stock"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="因子表达式">
                  <el-input
                    v-model="customForm.expression"
                    type="textarea"
                    :rows="3"
                    placeholder="输入因子表达式，例如: $close / Ref($close, 20) - 1"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="customForm.dateRange"
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
                <el-form-item label="K线周期">
                  <el-select v-model="customForm.period">
                    <el-option label="日线" value="day" />
                    <el-option label="周线" value="week" />
                    <el-option label="月线" value="month" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-alert
                title="表达式语法"
                type="info"
                :closable="false"
                style="margin-bottom: 20px"
              >
                <div class="expression-help">
                  <p><strong>可用变量:</strong></p>
                  <ul>
                    <li>$open - 开盘价</li>
                    <li>$high - 最高价</li>
                    <li>$low - 最低价</li>
                    <li>$close - 收盘价</li>
                    <li>$volume - 成交量</li>
                  </ul>
                  <p><strong>可用函数:</strong></p>
                  <ul>
                    <li>Ref($close, 20) - 20日前的收盘价</li>
                    <li>Ma($close, 20) - 20日均线</li>
                    <li>Std($close, 20) - 20日标准差</li>
                  </ul>
                </div>
              </el-alert>

              <el-button
                type="primary"
                @click="calculateCustomFactor"
                :loading="calculatingCustom"
                :disabled="!customForm.expression || customForm.symbols.length === 0"
              >
                <el-icon><DataAnalysis /></el-icon>
                开始计算
              </el-button>
              <el-button @click="resetCustomForm">重置</el-button>
            </el-form-item>
          </el-form>

          <!-- 计算结果 -->
          <div v-if="customResult" class="result-section">
            <el-divider content-position="left">计算结果</el-divider>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="表达式">
                {{ customResult.expression }}
              </el-descriptions-item>
              <el-descriptions-item label="股票数量">
                {{ customResult.symbols.length }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis } from '@element-plus/icons-vue'

// 状态
const activeTab = ref('indicators')
const calculatingIndicators = ref(false)
const calculatingAlpha158 = ref(false)
const calculatingAlpha360 = ref(false)
const calculatingCustom = ref(false)

// 技术指标表单
const indicatorForm = ref({
  symbol: '',
  dateRange: ['2024-01-01', '2024-12-31'],
  period: 'day',
  selectedIndicators: []
})

// Alpha158表单
const alpha158Form = ref({
  symbols: [],
  dateRange: ['2024-01-01', '2024-12-31'],
  period: 'day'
})

// Alpha360表单
const alpha360Form = ref({
  symbols: [],
  dateRange: ['2024-01-01', '2024-12-31'],
  period: 'day'
})

// 自定义因子表单
const customForm = ref({
  symbols: [],
  expression: '',
  dateRange: ['2024-01-01', '2024-12-31'],
  period: 'day'
})

// 计算结果
const indicatorResult = ref<any>(null)
const alpha158Result = ref<any>(null)
const alpha360Result = ref<any>(null)
const customResult = ref<any>(null)

// 可用数据
const availableIndicators = ref([
  { name: 'SMA', description: '简单移动平均', type: 'overlay' },
  { name: 'EMA', description: '指数移动平均', type: 'overlay' },
  { name: 'BOLL', description: '布林带', type: 'overlay' },
  { name: 'RSI', description: '相对强弱指标', type: 'oscillator' },
  { name: 'KDJ', description: '随机指标', type: 'oscillator' },
  { name: 'MACD', description: '指数平滑异同移动平均线', type: 'oscillator' },
  { name: 'ATR', description: '真实波幅', type: 'volatility' },
  { name: 'OBV', description: '能量潮', type: 'volume' },
  { name: 'MOM', description: '动量', type: 'momentum' },
  { name: 'ROC', description: '变动率', type: 'momentum' }
])

const availableStocks = ref([
  '000001.SZ', '000002.SZ', '600000.SH', '600036.SH', '600519.SH'
])

// API调用
const API_BASE = '/api/v1/research/calculation'

// 方法
const calculateIndicators = async () => {
  if (!indicatorForm.value.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  calculatingIndicators.value = true
  try {
    const res = await fetch(`${API_BASE}/indicators/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol: indicatorForm.value.symbol,
        start_date: indicatorForm.value.dateRange[0],
        end_date: indicatorForm.value.dateRange[1],
        period: indicatorForm.value.period,
        indicators: indicatorForm.value.selectedIndicators
      })
    })
    const data = await res.json()
    if (data.code === 200) {
      indicatorResult.value = data.data
      ElMessage.success('指标计算完成')
    }
  } catch (error: any) {
    ElMessage.error('计算失败: ' + error.message)
  } finally {
    calculatingIndicators.value = false
  }
}

const calculateAlpha158 = async () => {
  if (alpha158Form.value.symbols.length === 0) {
    ElMessage.warning('请选择股票代码')
    return
  }

  calculatingAlpha158.value = true
  try {
    const res = await fetch(`${API_BASE}/factors/alpha158`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbols: alpha158Form.value.symbols,
        start_date: alpha158Form.value.dateRange[0],
        end_date: alpha158Form.value.dateRange[1],
        period: alpha158Form.value.period
      })
    })
    const data = await res.json()
    if (data.code === 200) {
      alpha158Result.value = data.data
      ElMessage.success('Alpha158因子计算完成')
    }
  } catch (error: any) {
    ElMessage.error('计算失败: ' + error.message)
  } finally {
    calculatingAlpha158.value = false
  }
}

const calculateAlpha360 = async () => {
  if (alpha360Form.value.symbols.length === 0) {
    ElMessage.warning('请选择股票代码')
    return
  }

  calculatingAlpha360.value = true
  try {
    const res = await fetch(`${API_BASE}/factors/alpha360`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbols: alpha360Form.value.symbols,
        start_date: alpha360Form.value.dateRange[0],
        end_date: alpha360Form.value.dateRange[1],
        period: alpha360Form.value.period
      })
    })
    const data = await res.json()
    if (data.code === 200) {
      alpha360Result.value = data.data
      ElMessage.success('Alpha360因子计算完成')
    }
  } catch (error: any) {
    ElMessage.error('计算失败: ' + error.message)
  } finally {
    calculatingAlpha360.value = false
  }
}

const calculateCustomFactor = async () => {
  if (!customForm.value.expression) {
    ElMessage.warning('请输入因子表达式')
    return
  }
  if (customForm.value.symbols.length === 0) {
    ElMessage.warning('请选择股票代码')
    return
  }

  calculatingCustom.value = true
  try {
    const res = await fetch(`${API_BASE}/factors/custom`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbols: customForm.value.symbols,
        expression: customForm.value.expression,
        start_date: customForm.value.dateRange[0],
        end_date: customForm.value.dateRange[1],
        period: customForm.value.period
      })
    })
    const data = await res.json()
    if (data.code === 200) {
      customResult.value = data.data
      ElMessage.success('自定义因子计算完成')
    }
  } catch (error: any) {
    ElMessage.error('计算失败: ' + error.message)
  } finally {
    calculatingCustom.value = false
  }
}

// 辅助函数
const getIndicatorTableData = () => {
  if (!indicatorResult.value) return []

  return Object.entries(indicatorResult.value.indicators).map(([name, data]) => {
    const values = data.values || []
    return {
      name,
      preview: values.slice(0, 5).join(', '),
      count: values.length
    }
  })
}

const getFactorPreview = (factorKey: string) => {
  // 简单预览，显示前5个值
  return '模拟数据预览...'
}

const selectIndicatorsByType = (type: string) => {
  const indicators = availableIndicators.value.filter(ind => ind.type === type)
  indicatorForm.value.selectedIndicators = indicators.map(ind => ind.name)
  ElMessage.success(`已选择${type}指标`)
}

const resetIndicatorForm = () => {
  indicatorForm.value = {
    symbol: '',
    dateRange: ['2024-01-01', '2024-12-31'],
    period: 'day',
    selectedIndicators: []
  }
  indicatorResult.value = null
}

const resetAlpha158Form = () => {
  alpha158Form.value = {
    symbols: [],
    dateRange: ['2024-01-01', '2024-12-31'],
    period: 'day'
  }
  alpha158Result.value = null
}

const resetAlpha360Form = () => {
  alpha360Form.value = {
    symbols: [],
    dateRange: ['2024-01-01', '2024-12-31'],
    period: 'day'
  }
  alpha360Result.value = null
}

const resetCustomForm = () => {
  customForm.value = {
    symbols: [],
    expression: '',
    dateRange: ['2024-01-01', '2024-12-31'],
    period: 'day'
  }
  customResult.value = null
}
</script>

<style scoped lang="scss">
.factor-calculation-view {
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
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  color: white;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
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

.calculation-tabs {
  margin-top: 20px;
}

.indicators-card,
.alpha158-card,
.alpha360-card,
.custom-factor-card {
  margin-bottom: 20px;
}

.result-section {
  margin-top: 30px;
}

.expression-help {
  font-size: 13px;
  line-height: 1.6;

  p {
    margin: 5px 0;
  }

  ul {
    margin: 5px 0;
    padding-left: 20px;
  }
}

.text-muted {
  color: #909399;
}
</style>
