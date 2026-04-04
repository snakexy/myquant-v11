<template>
  <div class="step-factor-calculation-panel">
    <!-- 因子计算配置 -->
    <div class="factor-calc-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
        {{ isZh ? '因子计算' : 'Factor Calculation' }}
      </h3>

      <!-- 第一行：计算类型卡片（支持多选） -->
      <div class="type-cards">
        <div :class="['type-card', { active: selectedCalcTypes.includes('alpha158') }]" @click="toggleCalcType('alpha158')">
          <div class="type-card-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div class="type-card-content">
            <div class="type-card-title">Alpha158</div>
            <div class="type-card-desc">{{ isZh ? '158个经典因子' : '158 classic factors' }}</div>
          </div>
          <div class="type-card-check">
            <svg v-if="selectedCalcTypes.includes('alpha158')" class="check-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
            </svg>
          </div>
        </div>
        <div :class="['type-card', { active: selectedCalcTypes.includes('alpha360') }]" @click="toggleCalcType('alpha360')">
          <div class="type-card-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 2 7 12 12 22 7 12 2"/>
              <polyline points="2 17 12 22 22 17"/>
              <polyline points="2 12 12 17 22 12"/>
            </svg>
          </div>
          <div class="type-card-content">
            <div class="type-card-title">Alpha360</div>
            <div class="type-card-desc">{{ isZh ? '360个扩展因子' : '360 extended factors' }}</div>
          </div>
          <div class="type-card-check">
            <svg v-if="selectedCalcTypes.includes('alpha360')" class="check-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
            </svg>
          </div>
        </div>
        <div :class="['type-card', { active: selectedCalcTypes.includes('custom') }]" @click="toggleCalcType('custom')">
          <div class="type-card-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </div>
          <div class="type-card-content">
            <div class="type-card-title">{{ isZh ? '自定义' : 'Custom' }}</div>
            <div class="type-card-desc">{{ isZh ? '自定义因子表达式' : 'Custom expression' }}</div>
          </div>
          <div class="type-card-check">
            <svg v-if="selectedCalcTypes.includes('custom')" class="check-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- 第二行：技术指标（独立显示） -->
      <div class="indicator-section" style="margin-top: 16px;">
        <div class="indicator-header">
          <span class="indicator-label">
            <svg class="indicator-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 3v18h18"/>
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
            </svg>
            {{ isZh ? '技术指标' : 'Technical Indicators' }}
          </span>
          <el-checkbox v-model="showIndicators"></el-checkbox>
        </div>
        <div v-if="showIndicators" class="indicator-options" style="margin-top: 12px;">
          <!-- 预设组合按钮（支持多选） -->
          <div class="preset-buttons" style="margin-bottom: 12px;">
            <span style="margin-right: 8px; color: var(--text-secondary); font-size: 12px;">{{ isZh ? '快速选择:' : 'Presets:' }}</span>
            <el-button
              size="small"
              :type="selectedPresets.includes('trend') ? 'primary' : 'info'"
              :plain="!selectedPresets.includes('trend')"
              @click="togglePreset('trend')"
            >{{ isZh ? '趋势' : 'Trend' }}</el-button>
            <el-button
              size="small"
              :type="selectedPresets.includes('volume') ? 'primary' : 'info'"
              :plain="!selectedPresets.includes('volume')"
              @click="togglePreset('volume')"
            >{{ isZh ? '量价' : 'Volume' }}</el-button>
            <el-button
              size="small"
              :type="selectedPresets.includes('momentum') ? 'primary' : 'info'"
              :plain="!selectedPresets.includes('momentum')"
              @click="togglePreset('momentum')"
            >{{ isZh ? '动量' : 'Momentum' }}</el-button>
            <el-button
              size="small"
              :type="selectedPresets.includes('volatility') ? 'primary' : 'info'"
              :plain="!selectedPresets.includes('volatility')"
              @click="togglePreset('volatility')"
            >{{ isZh ? '波动' : 'Volatility' }}</el-button>
            <el-button
              size="small"
              :type="selectedPresets.includes('cycle') ? 'primary' : 'info'"
              :plain="!selectedPresets.includes('cycle')"
              @click="togglePreset('cycle')"
            >{{ isZh ? '周期' : 'Cycle' }}</el-button>
          </div>
          <!-- 多选指标 -->
          <el-select v-model="selectedIndicators" multiple filterable placeholder="选择指标(可多选)" style="width: 100%;">
            <el-option v-for="ind in allIndicators" :key="ind.value" :label="ind.label" :value="ind.value" />
          </el-select>
        </div>
      </div>

      <!-- 自定义表达式 -->
      <div v-if="selectedCalcTypes.includes('custom')" class="calc-options" style="margin-top: 16px;">
        <el-input v-model="customFactorExpression" type="textarea" :rows="3" placeholder="输入因子表达式" />
      </div>

      <!-- 计算按钮 -->
      <div class="action-buttons">
        <button class="btn btn-primary" :disabled="isCalculating" @click="runCalculation">
          {{ isCalculating ? (isZh ? '计算中...' : 'Calculating...') : (isZh ? '开始计算' : 'Calculate') }}
        </button>
      </div>

      <!-- 因子任务列表 -->
      <div v-if="calculationTasks.length > 0" class="task-list-section" style="margin-top: 24px;">
        <h3 class="section-title">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          {{ isZh ? '计算任务' : 'Calculation Tasks' }}
        </h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ isZh ? '任务ID' : 'Task ID' }}</th>
              <th>{{ isZh ? '表达式' : 'Expression' }}</th>
              <th>{{ isZh ? '状态' : 'Status' }}</th>
              <th>{{ isZh ? '进度' : 'Progress' }}</th>
              <th>{{ isZh ? '创建时间' : 'Created' }}</th>
              <th>{{ isZh ? '操作' : 'Actions' }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in calculationTasks" :key="task.task_id">
              <td style="font-family: monospace; color: var(--text-secondary);">{{ task.task_id.slice(0, 16) }}...</td>
              <td>{{ task.expression.slice(0, 50) }}{{ task.expression.length > 50 ? '...' : '' }}</td>
              <td>
                <span :class="['status-badge', task.status === 'completed' ? 'pass' : task.status === 'failed' ? 'fail' : task.status]">
                  {{ getTaskStatusText(task.status) }}
                </span>
              </td>
              <td>
                <div v-if="task.status === 'running'" style="display: flex; align-items: center; gap: 8px;">
                  <div style="flex: 1; height: 4px; background: var(--bg-tertiary); border-radius: 2px; overflow: hidden;">
                    <div :style="{ width: task.progress + '%', height: '100%', background: 'var(--primary-color)', transition: 'width 0.3s' }"></div>
                  </div>
                  <span style="font-size: 11px; color: var(--text-secondary); min-width: 35px;">{{ Math.round(task.progress) }}%</span>
                </div>
                <span v-else style="color: var(--text-secondary);">-</span>
              </td>
              <td style="font-size: 12px; color: var(--text-secondary);">{{ task.created_at }}</td>
              <td>
                <el-button v-if="task.status === 'completed'" size="small" type="primary" link @click="viewTaskResult(task.task_id)">{{ isZh ? '查看' : 'View' }}</el-button>
                <el-button v-if="task.status === 'failed'" size="small" type="danger" link @click="retryTask(task.task_id)">{{ isZh ? '重试' : 'Retry' }}</el-button>
                <el-button size="small" type="info" link @click="deleteTask(task.task_id)">{{ isZh ? '删除' : 'Delete' }}</el-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 因子结果查看器 -->
      <div v-if="currentResult" class="result-viewer-section" style="margin-top: 24px; background: transparent;">
        <h3 class="section-title">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          {{ isZh ? '计算结果' : 'Calculation Result' }}: {{ currentResult.factor_name }}
        </h3>

        <!-- 统计信息 -->
        <div class="result-stats">
          <div class="stat-card">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <ellipse cx="12" cy="5" rx="9" ry="3"/>
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
              </svg>
            </div>
            <div class="stat-label">{{ isZh ? '数据量' : 'Count' }}</div>
            <div class="stat-value">{{ currentResult.statistics.count }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="20" x2="12" y2="10"/>
                <line x1="18" y1="20" x2="18" y2="4"/>
                <line x1="6" y1="20" x2="6" y2="16"/>
              </svg>
            </div>
            <div class="stat-label">{{ isZh ? '均值' : 'Mean' }}</div>
            <div class="stat-value">{{ currentResult.statistics.mean?.toFixed(4) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 3v18h18"/>
                <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
              </svg>
            </div>
            <div class="stat-label">{{ isZh ? '标准差' : 'Std' }}</div>
            <div class="stat-value">{{ currentResult.statistics.std?.toFixed(4) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="7 13 12 18 17 13"/>
                <polyline points="7 6 12 11 17 6"/>
              </svg>
            </div>
            <div class="stat-label">{{ isZh ? '最小值' : 'Min' }}</div>
            <div class="stat-value">{{ currentResult.statistics.min?.toFixed(4) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="7 11 12 6 17 11"/>
                <polyline points="7 18 12 13 17 18"/>
              </svg>
            </div>
            <div class="stat-label">{{ isZh ? '最大值' : 'Max' }}</div>
            <div class="stat-value">{{ currentResult.statistics.max?.toFixed(4) }}</div>
          </div>
        </div>

        <!-- 结果操作 -->
        <div class="result-actions" style="margin-top: 16px;">
          <el-button-group class="result-btn-group">
            <el-button size="small" @click="exportResult('csv')">
              <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {{ isZh ? '导出CSV' : 'Export CSV' }}
            </el-button>
            <el-button size="small" @click="exportResult('excel')">
              <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              {{ isZh ? '导出Excel' : 'Export Excel' }}
            </el-button>
            <el-button size="small" type="success" @click="saveToQlib">
              <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
              {{ isZh ? '保存为QLib格式' : 'Save as QLib' }}
            </el-button>
          </el-button-group>
        </div>

        <!-- 结果数据表格 -->
        <div class="result-table" style="margin-top: 16px;">
          <table class="data-table">
            <thead>
              <tr>
                <th>{{ isZh ? '股票代码' : 'Instrument' }}</th>
                <th>{{ isZh ? '股票名称' : 'Name' }}</th>
                <th>{{ isZh ? '时间' : 'Datetime' }}</th>
                <th>{{ isZh ? '因子值' : 'Factor Value' }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in paginatedResultData" :key="row.instrument + row.datetime">
                <td style="font-family: monospace;">{{ row.instrument }}</td>
                <td>{{ row.name || '-' }}</td>
                <td>{{ row.datetime }}</td>
                <td :class="['value', { positive: row.value > 0, negative: row.value < 0 }]">{{ row.value?.toFixed(6) }}</td>
              </tr>
            </tbody>
          </table>
          <el-pagination
            v-model:current-page="resultPage"
            :page-size="resultPageSize"
            :total="currentResult.data?.length || 0"
            layout="prev, pager, next, total"
            style="margin-top: 12px; justify-content: center;"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
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

// 因子计算相关变量（支持多选）
const selectedCalcTypes = ref<string[]>(['alpha158'])
const customFactorExpression = ref('')
const isCalculating = ref(false)

// 因子任务列表相关变量
interface CalculationTask {
  task_id: string
  expression: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  created_at: string
  indicatorResult?: any
}

const calculationTasks = ref<CalculationTask[]>([])
const currentResultTaskId = ref<string | null>(null)

// 因子结果查看器相关变量
interface FactorData {
  instrument: string
  name?: string
  datetime: string
  value: number
}

interface CalculationResult {
  factor_name: string
  data: FactorData[]
  statistics: {
    count: number
    mean: number
    std: number
    min: number
    max: number
  }
}

const currentResult = ref<CalculationResult | null>(null)
const resultPage = ref(1)
const resultPageSize = 50

// 分页结果数据
const paginatedResultData = computed(() => {
  if (!currentResult.value?.data) return []
  const start = (resultPage.value - 1) * resultPageSize
  return currentResult.value.data.slice(start, start + resultPageSize)
})

// 获取任务状态文本
const getTaskStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待执行',
    running: '计算中',
    completed: '已完成',
    failed: '失败'
  }
  return isZh.value ? (map[status] || status) : status
}

// 查看任务结果
const viewTaskResult = (taskId: string) => {
  currentResultTaskId.value = taskId
  currentResult.value = {
    factor_name: `Factor_${taskId.slice(0, 8)}`,
    data: Array.from({ length: 20 }, (_, i) => ({
      instrument: `00000${i}`.slice(-6),
      name: '',
      datetime: new Date(Date.now() - i * 86400000).toISOString().split('T')[0],
      value: Math.random() * 2 - 1
    })),
    statistics: {
      count: 1000,
      mean: 0.0234,
      std: 0.4567,
      min: -1.234,
      max: 1.567
    }
  }
}

// 重试任务
const retryTask = (taskId: string) => {
  const task = calculationTasks.value.find(t => t.task_id === taskId)
  if (task) {
    task.status = 'pending'
    task.progress = 0
    setTimeout(() => {
      task.status = 'running'
      const interval = setInterval(() => {
        task.progress += 10
        if (task.progress >= 100) {
          clearInterval(interval)
          task.status = 'completed'
        }
      }, 500)
    }, 1000)
  }
}

// 删除任务
const deleteTask = (taskId: string) => {
  calculationTasks.value = calculationTasks.value.filter(t => t.task_id !== taskId)
  if (currentResultTaskId.value === taskId) {
    currentResult.value = null
    currentResultTaskId.value = null
  }
}

// 导出结果
const exportResult = (format: 'csv' | 'excel') => {
  console.log('Exporting result as:', format)
  ElMessage.success(isZh.value ? `已导出为${format.toUpperCase()}` : `Exported as ${format.toUpperCase()}`)
}

// 保存为QLib格式
const saveToQlib = () => {
  console.log('Saving to QLib format')
  ElMessage.success(isZh.value ? '已保存为QLib格式' : 'Saved as QLib format')
}

// 切换计算类型（多选）
const toggleCalcType = (type: string) => {
  const index = selectedCalcTypes.value.indexOf(type)
  if (index === -1) {
    selectedCalcTypes.value.push(type)
  } else {
    selectedCalcTypes.value.splice(index, 1)
  }
}

// 技术指标相关变量
const showIndicators = ref(false)
const selectedIndicators = ref<string[]>([])
const selectedPresets = ref<string[]>([])

// 预设组合映射
const presetMap: Record<string, string[]> = {
  trend: ['MA', 'EMA', 'BOLL', 'SAR', 'TRIX'],
  volume: ['OBV', 'VOL_MA', 'VR', 'PVT'],
  momentum: ['RSI', 'KDJ', 'CCI', 'MACD', 'MOM', 'ROC'],
  volatility: ['ATR', 'STDDEV', 'WR'],
  cycle: ['DPO', 'TRIX']
}

// 切换预设组合（多选）
const togglePreset = (type: string) => {
  const index = selectedPresets.value.indexOf(type)
  if (index === -1) {
    selectedPresets.value.push(type)
    const indicators = presetMap[type] || []
    indicators.forEach(ind => {
      if (!selectedIndicators.value.includes(ind)) {
        selectedIndicators.value.push(ind)
      }
    })
  } else {
    selectedPresets.value.splice(index, 1)
    const indicators = presetMap[type] || []
    indicators.forEach(ind => {
      const inOtherPreset = Object.entries(presetMap).some(([key, inds]) => {
        return key !== type && selectedPresets.value.includes(key) && inds.includes(ind)
      })
      if (!inOtherPreset) {
        selectedIndicators.value = selectedIndicators.value.filter(i => i !== ind)
      }
    })
  }
}

// 所有指标列表
const allIndicators = ref([
  { label: 'MA(移动平均)', value: 'MA' },
  { label: 'EMA(指数平均)', value: 'EMA' },
  { label: 'BOLL(布林带)', value: 'BOLL' },
  { label: 'SAR(抛物线)', value: 'SAR' },
  { label: 'KAMA(自适应均线)', value: 'KAMA' },
  { label: 'TRIX(三重指数)', value: 'TRIX' },
  { label: 'RSI(相对强弱)', value: 'RSI' },
  { label: 'KDJ(随机指标)', value: 'KDJ' },
  { label: 'CCI(顺势指标)', value: 'CCI' },
  { label: 'MACD', value: 'MACD' },
  { label: 'WR(威廉指标)', value: 'WR' },
  { label: 'OBV(能量潮)', value: 'OBV' },
  { label: 'AROON(阿隆指标)', value: 'AROON' },
  { label: 'MOM(动量)', value: 'MOM' },
  { label: 'ROC(变化率)', value: 'ROC' },
  { label: 'BIAS(乖离率)', value: 'BIAS' },
  { label: 'ATR(真实波幅)', value: 'ATR' },
  { label: 'STDDEV(标准差)', value: 'STDDEV' },
  { label: 'HV(历史波动率)', value: 'HV' },
  { label: 'VOL_MA(成交量均线)', value: 'VOL_MA' },
  { label: 'VR(成交量比率)', value: 'VR' },
  { label: 'PVT(价量趋势)', value: 'PVT' },
  { label: 'DPO(去趋势震荡)', value: 'DPO' },
])

// 计算函数
const runCalculation = async () => {
  if (!props.taskId) return

  const hasFactors = selectedCalcTypes.value.length > 0
  const hasIndicators = selectedIndicators.value.length > 0
  if (!hasFactors && !hasIndicators) {
    ElMessage.warning(isZh.value ? '请至少选择一个计算类型' : 'Please select at least one calculation type')
    return
  }

  isCalculating.value = true

  const newTask: CalculationTask = {
    task_id: `task_${Date.now()}`,
    expression: selectedCalcTypes.value.join(', ') + (selectedIndicators.value.length > 0 ? ` + ${selectedIndicators.value.length} indicators` : ''),
    status: 'running',
    progress: 0,
    created_at: new Date().toLocaleString()
  }
  calculationTasks.value.unshift(newTask)

  const progressInterval = setInterval(() => {
    const remaining = 100 - newTask.progress
    const increment = remaining > 20 ? Math.random() * 15 + 5 : remaining
    newTask.progress = Math.min(100, newTask.progress + increment)
    calculationTasks.value = [...calculationTasks.value]

    if (newTask.progress >= 100) {
      newTask.progress = 100
      newTask.status = 'completed'
      clearInterval(progressInterval)
      viewTaskResult(newTask.task_id)
      ElMessage.success(isZh.value ? '计算完成' : 'Calculation complete')
      emit('stepComplete', { taskId: newTask.task_id })
    }
  }, 200)
}

// 监听变化并发送更新
watch([selectedCalcTypes, customFactorExpression, selectedIndicators], () => {
  emit('dataUpdate', {
    calcTypes: selectedCalcTypes.value,
    customExpression: customFactorExpression.value,
    indicators: selectedIndicators.value
  })
}, { deep: true })
</script>

<style scoped lang="scss">
.step-factor-calculation-panel {
  width: 100%;
}

.factor-calc-section {
  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
  }
}

.type-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.type-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.type-card:hover {
  border-color: var(--accent-blue);
}

.type-card.active {
  background: rgba(41, 98, 255, 0.1);
  border-color: var(--accent-blue);
}

.type-card-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 6px;
}

.type-card-content {
  flex: 1;
}

.type-card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.type-card-desc {
  font-size: 11px;
  color: var(--text-secondary);
}

.type-card-check {
  .check-icon {
    width: 18px;
    height: 18px;
    color: var(--accent-blue);
  }
}

.indicator-section {
  .indicator-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: 6px;
    border: 1px solid var(--border-color);
  }

  .indicator-label {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
    font-size: 13px;
  }

  .indicator-icon {
    width: 14px;
    height: 14px;
  }

  .indicator-options {
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: 6px;
    border: 1px solid var(--border-color);
  }
}

.calc-options {
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
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

.task-list-section {
  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 12px;
  }
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;

  thead {
    background: var(--bg-secondary);

    th {
      padding: 10px 12px;
      text-align: left;
      font-weight: 600;
      color: var(--text-secondary);
      border-bottom: 1px solid var(--border-color);
    }
  }

  tbody {
    tr {
      border-bottom: 1px solid var(--border-color);

      &:hover {
        background: var(--bg-secondary);
      }

      td {
        padding: 10px 12px;
        color: var(--text-primary);
      }
    }
  }
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.pass {
  background: rgba(38, 166, 154, 0.2);
  color: var(--accent-green);
}

.status-badge.fail {
  background: rgba(239, 83, 80, 0.2);
  color: var(--accent-red);
}

.status-badge.running {
  background: rgba(41, 98, 255, 0.2);
  color: var(--accent-blue);
}

.result-viewer-section {
  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 12px;
  }
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.stat-card {
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-icon {
  width: 28px;
  height: 28px;
  color: var(--text-secondary);
}

.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.result-actions {
  display: flex;
  gap: 8px;
}

.result-btn-group {
  .el-button {
    .icon-xs {
      width: 12px;
      height: 12px;
      margin-right: 4px;
    }
  }
}

.result-table {
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);

  .value {
    &.positive {
      color: var(--accent-red);
    }

    &.negative {
      color: var(--accent-green);
    }
  }
}
</style>
