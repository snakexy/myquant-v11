<!--
  ResearchStep2FactorCalculation.vue
  因子计算步骤组件 - 完全自包含

  功能:
  - 因子计算类型选择 (Alpha158, Alpha360, 自定义)
  - 技术指标配置
  - 预设组合选择
  - 自定义因子编辑
  - 计算任务管理
  - 结果查看和导出
-->

<template>
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
            :type="selectedPresets.includes('oscillator') ? 'primary' : 'info'"
            :plain="!selectedPresets.includes('oscillator')"
            @click="togglePreset('oscillator')"
          >{{ isZh ? '震荡' : 'Oscillator' }}</el-button>
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
        <el-select v-model="selectedIndicators" multiple filterable :placeholder="isZh ? '选择指标(可多选)' : 'Select indicators'" style="width: 100%;">
          <el-option v-for="ind in allIndicators" :key="ind.value" :label="ind.label" :value="ind.value" />
        </el-select>
      </div>
    </div>

    <!-- 自定义表达式 -->
    <div v-if="selectedCalcTypes.includes('custom')" class="calc-options" style="margin-top: 16px;">
      <el-input v-model="customFactorExpression" type="textarea" :rows="3" :placeholder="isZh ? '输入因子表达式' : 'Enter factor expression'" />
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
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps<{
  isZh?: boolean
  taskId?: string
}>()

// 因子计算相关变量（支持多选）
const selectedCalcTypes = ref<string[]>(['alpha158'])
const customFactorExpression = ref('')
const isCalculating = ref(false)

// 计算任务接口
interface CalculationTask {
  task_id: string
  expression: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  created_at: string
}

const calculationTasks = ref<CalculationTask[]>([])
const currentResultTaskId = ref<string | null>(null)

// 因子结果查看器相关变量
interface CalculationResultData {
  instrument: string
  name?: string
  datetime: string
  value: number
}

interface CalculationResult {
  factor_name: string
  statistics: {
    count: number
    mean: number
    std: number
    min: number
    max: number
  }
  data: CalculationResultData[]
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
  const map: Record<string, { zh: string; en: string }> = {
    pending: { zh: '待执行', en: 'Pending' },
    running: { zh: '计算中', en: 'Running' },
    completed: { zh: '已完成', en: 'Completed' },
    failed: { zh: '失败', en: 'Failed' }
  }
  const text = map[status]
  return props.isZh ? text?.zh || status : text?.en || status
}

// 查看任务结果
const viewTaskResult = (taskId: string) => {
  currentResultTaskId.value = taskId
  // 模拟结果数据（正式环境中从后端API获取股票名称）
  currentResult.value = {
    factor_name: `Factor_${taskId.slice(0, 8)}`,
    statistics: {
      count: 1250,
      mean: 0.0234,
      std: 1.2456,
      min: -3.4521,
      max: 3.8721
    },
    data: Array.from({ length: 20 }, (_, i) => ({
      instrument: `00000${i + 1}.SZ`,
      name: `股票${i + 1}`,
      datetime: '2024-01-15',
      value: Math.random() * 2 - 1
    }))
  }
  resultPage.value = 1
}

// 重试任务
const retryTask = (taskId: string) => {
  const task = calculationTasks.value.find(t => t.task_id === taskId)
  if (task) {
    task.status = 'pending'
    task.progress = 0
    runCalculation()
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
  ElMessage.success(props.isZh ? `已导出为${format.toUpperCase()}` : `Exported as ${format.toUpperCase()}`)
}

// 保存为QLib格式
const saveToQlib = () => {
  console.log('Saving to QLib format')
  ElMessage.success(props.isZh ? '已保存为QLib格式' : 'Saved as QLib format')
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
  trend: ['MA', 'EMA', 'SMA'],
  volume: ['VOL', 'OBV', 'VMA'],
  oscillator: ['MACD', 'RSI', 'KDJ'],
  momentum: ['MOM', 'ROC', 'BIAS'],
  volatility: ['ATR', 'STDDEV', 'BOLL'],
  cycle: ['CYCLE', 'FFT', 'WAVE']
}

// 切换预设组合（多选）
const togglePreset = (type: string) => {
  const index = selectedPresets.value.indexOf(type)
  if (index === -1) {
    selectedPresets.value.push(type)
    // 添加该预设的指标
    const indicators = presetMap[type] || []
    indicators.forEach(ind => {
      if (!selectedIndicators.value.includes(ind)) {
        selectedIndicators.value.push(ind)
      }
    })
  } else {
    selectedPresets.value.splice(index, 1)
    // 移除该预设的指标（如果不在其他预设中）
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
  // 趋势指标
  { label: 'MA(简单移动平均)', value: 'MA', category: 'trend' },
  { label: 'EMA(指数移动平均)', value: 'EMA', category: 'trend' },
  { label: 'SMA(平滑移动平均)', value: 'SMA', category: 'trend' },
  { label: 'WMA(加权移动平均)', value: 'WMA', category: 'trend' },
  { label: 'BOLL(布林带)', value: 'BOLL', category: 'trend' },
  // 量价指标
  { label: 'VOL(成交量)', value: 'VOL', category: 'volume' },
  { label: 'OBV(能量潮)', value: 'OBV', category: 'volume' },
  { label: 'VMA(量均线)', value: 'VMA', category: 'volume' },
  { label: 'VR(成交量率)', value: 'VR', category: 'volume' },
  // 震荡指标
  { label: 'MACD(指数平滑异同移动平均线)', value: 'MACD', category: 'oscillator' },
  { label: 'RSI(相对强弱指标)', value: 'RSI', category: 'oscillator' },
  { label: 'KDJ(随机指标)', value: 'KDJ', category: 'oscillator' },
  { label: 'CCI(顺势指标)', value: 'CCI', category: 'oscillator' },
  { label: 'WR(威廉指标)', value: 'WR', category: 'oscillator' },
  // 动量指标
  { label: 'MOM(动量)', value: 'MOM', category: 'momentum' },
  { label: 'ROC(变动率)', value: 'ROC', category: 'momentum' },
  { label: 'BIAS(乖离率)', value: 'BIAS', category: 'momentum' },
  { label: 'DPO(区间振荡线)', value: 'DPO', category: 'momentum' },
  // 波动指标
  { label: 'ATR(真实波幅)', value: 'ATR', category: 'volatility' },
  { label: 'STDDEV(标准差)', value: 'STDDEV', category: 'volatility' },
  { label: 'BOLL(布林带)', value: 'BOLL', category: 'volatility' },
  { label: 'KELTNER(肯特纳通道)', value: 'KELTNER', category: 'volatility' },
  // 周期指标
  { label: 'CYCLE(周期线)', value: 'CYCLE', category: 'cycle' },
  { label: 'FFT(快速傅里叶变换)', value: 'FFT', category: 'cycle' },
  { label: 'WAVE(波形分析)', value: 'WAVE', category: 'cycle' }
])

// 计算函数
const runCalculation = async () => {
  if (!props.taskId) return
  isCalculating.value = true

  try {
    const hasFactors = selectedCalcTypes.value.length > 0
    const hasIndicators = selectedIndicators.value.length > 0

    if (!hasFactors && !hasIndicators) {
      ElMessage.warning(props.isZh ? '请至少选择一个计算类型' : 'Please select at least one calculation type')
      return
    }

    // 创建新任务
    const newTask: CalculationTask = {
      task_id: `task_${Date.now()}`,
      expression: selectedCalcTypes.value.join(', ') + (selectedIndicators.value.length > 0 ? ` + ${selectedIndicators.value.length} indicators` : ''),
      status: 'running',
      progress: 0,
      created_at: new Date().toLocaleString()
    }
    calculationTasks.value.unshift(newTask)

    console.log('Factor calculation:', selectedCalcTypes.value, customFactorExpression.value)
    console.log('Indicator calculation:', selectedIndicators.value)

    // 模拟计算进度（每200ms更新一次，更平滑）
    const updateInterval = setInterval(() => {
      if (newTask.progress < 100) {
        newTask.progress += 2
        // 强制触发Vue响应式更新
        calculationTasks.value = [...calculationTasks.value]
      } else {
        clearInterval(updateInterval)
        newTask.status = 'completed'
        calculationTasks.value = [...calculationTasks.value]

        // 自动显示结果
        viewTaskResult(newTask.task_id)
        ElMessage.success(props.isZh ? '计算完成' : 'Calculation complete')
      }
    }, 200)
  } catch (error: any) {
    console.error('Calculation error:', error)
    ElMessage.error(error.message || (props.isZh ? '计算失败' : 'Calculation failed'))

    // 标记任务为失败
    if (calculationTasks.value.length > 0) {
      calculationTasks.value[0].status = 'failed'
    }
  } finally {
    isCalculating.value = false
  }
}
</script>

<style scoped lang="scss">
.factor-calc-section {
  width: 100%;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.icon-sm {
  width: 20px;
  height: 20px;
  color: var(--primary-color);
}

/* 计算类型卡片 */
.type-cards {
  display: flex;
  gap: 12px;
}

.type-card {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.type-card:hover {
  background: var(--bg-tertiary);
  border-color: var(--primary-color);
}

.type-card.active {
  background: var(--primary-color-light);
  border-color: var(--primary-color);
}

.type-card-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 6px;
  margin-right: 12px;
}

.type-card-icon svg {
  width: 24px;
  height: 24px;
}

.type-card-content {
  flex: 1;
}

.type-card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.type-card-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.type-card-check {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon {
  width: 20px;
  height: 20px;
  color: var(--primary-color);
}

/* 技术指标区域 */
.indicator-section {
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.indicator-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.indicator-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.indicator-icon {
  width: 18px;
  height: 18px;
  color: var(--primary-color);
}

/* 预设按钮 */
.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;

  .el-button {
    transition: all 0.2s !important;
    border-radius: 4px !important;
    font-size: 12px !important;
    padding: 4px 12px !important;
  }
}

/* 计算选项 */
.calc-options {
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

/* 操作按钮 */
.action-buttons {
  margin-top: 16px;
}

.btn {
  padding: 8px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-color-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 任务列表 */
.task-list-section {
  margin-top: 24px;
}

/* 结果查看器 */
.result-viewer-section {
  width: 100%;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-top: 16px;
  margin-bottom: 16px;
}

.result-stats .stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  transition: all 0.2s;
}

.result-stats .stat-card:hover {
  border-color: var(--accent-blue);
}

.result-stats .stat-icon {
  width: 24px;
  height: 24px;
  margin: 0 auto 8px;
  color: var(--primary-color);
}

.result-stats .stat-icon svg {
  width: 100%;
  height: 100%;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 结果操作 */
.result-actions {
  display: flex;
  gap: 8px;
}

.result-btn-group {
  display: flex;
}

.icon-xs {
  width: 14px;
  height: 14px;
  margin-right: 4px;
}

/* 数据表格 */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead {
  background: var(--bg-secondary);
}

.data-table th {
  padding: 12px 8px;
  text-align: left;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
}

.data-table tbody tr {
  border-bottom: 1px solid var(--border-color);
}

.data-table tbody tr:hover {
  background: var(--bg-secondary);
}

.data-table td {
  padding: 10px 8px;
  color: var(--text-primary);
}

.data-table .value {
  font-family: monospace;
  font-weight: 500;
}

.data-table .value.positive {
  color: var(--success-color);
}

.data-table .value.negative {
  color: var(--danger-color);
}

/* 状态徽章 */
.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.pass {
  background: rgba(103, 194, 58, 0.2);
  color: var(--success-color);
}

.status-badge.fail {
  background: rgba(245, 108, 108, 0.2);
  color: var(--danger-color);
}

.status-badge.running {
  background: rgba(64, 158, 255, 0.2);
  color: var(--primary-color);
}

.status-badge.pending {
  background: rgba(230, 162, 60, 0.2);
  color: var(--warning-color);
}
</style>
