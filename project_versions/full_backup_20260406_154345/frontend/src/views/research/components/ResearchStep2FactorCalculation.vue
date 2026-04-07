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
            <el-button
              size="small"
              :type="selectedPresets.includes('other') ? 'primary' : 'info'"
              :plain="!selectedPresets.includes('other')"
              @click="togglePreset('other')"
            >{{ isZh ? '其他' : 'Other' }}</el-button>
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
        <ActionButton
          type="primary"
          :label="isCalculating ? (isZh ? '计算中...' : 'Calculating...') : (isZh ? '开始计算' : 'Calculate')"
          :loading="isCalculating"
          :disabled="isCalculating"
          @click="runCalculation"
        />
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
import { ref, computed, inject, type Ref } from 'vue'
import ActionButton from '@/components/ui/ActionButton.vue'

interface Props {
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isZh: true
})

// 类型定义
interface CalculationTask {
  task_id: string
  expression: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  created_at: string
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
  data: Array<{
    instrument: string
    name: string
    datetime: string
    value: number
  }>
}

// 状态变量
const selectedCalcTypes = ref<string[]>(['alpha158'])
const customFactorExpression = ref('')
const isCalculating = ref(false)
const calculationTasks = ref<CalculationTask[]>([])
const currentResultTaskId = ref<string | null>(null)
const currentResult = ref<CalculationResult | null>(null)
const resultPage = ref(1)
const resultPageSize = 50
const showIndicators = ref(false)
const selectedIndicators = ref<string[]>([])
const selectedPresets = ref<string[]>([])

// 计算属性
const paginatedResultData = computed(() => {
  if (!currentResult.value?.data) return []
  const start = (resultPage.value - 1) * resultPageSize
  return currentResult.value.data.slice(start, start + resultPageSize)
})

// 所有指标列表（40+指标）
const allIndicators = ref([
  // 趋势指标
  { label: 'MA(简单移动平均)', value: 'MA', category: 'trend' },
  { label: 'EMA(指数移动平均)', value: 'EMA', category: 'trend' },
  { label: 'WMA(加权移动平均)', value: 'WMA', category: 'trend' },
  { label: 'DEMA(双指数移动平均)', value: 'DEMA', category: 'trend' },
  { label: 'TEMA(三重指数移动平均)', value: 'TEMA', category: 'trend' },
  { label: 'T3(三重指数移动平均)', value: 'T3', category: 'trend' },
  { label: 'KAMA(考夫曼自适应均线)', value: 'KAMA', category: 'trend' },
  { label: 'BOLL(布林带)', value: 'BOLL', category: 'trend' },
  { label: 'SAR(抛物线转向)', value: 'SAR', category: 'trend' },
  { label: 'HT_TRENDLINE(希尔伯特趋势线)', value: 'HT_TRENDLINE', category: 'trend' },
  // 震荡指标
  { label: 'RSI(相对强弱指标)', value: 'RSI', category: 'oscillator' },
  { label: 'KDJ(随机指标)', value: 'KDJ', category: 'oscillator' },
  { label: 'STOCH(随机指标)', value: 'STOCH', category: 'oscillator' },
  { label: 'STOCHF(快速随机指标)', value: 'STOCHF', category: 'oscillator' },
  { label: 'MACD', value: 'MACD', category: 'oscillator' },
  { label: 'STOCHRSI(相对强弱随机指标)', value: 'STOCHRSI', category: 'oscillator' },
  { label: 'ULTOSC(终极振荡指标)', value: 'ULTOSC', category: 'oscillator' },
  { label: 'CCI(顺势指标)', value: 'CCI', category: 'oscillator' },
  { label: 'DX(趋向指标)', value: 'DX', category: 'oscillator' },
  { label: 'TRIX(三重指数平滑平均线)', value: 'TRIX', category: 'oscillator' },
  { label: 'APO(绝对价格振荡指标)', value: 'APO', category: 'oscillator' },
  { label: 'PPO(百分比价格振荡指标)', value: 'PPO', category: 'oscillator' },
  { label: 'WR(威廉指标)', value: 'WR', category: 'oscillator' },
  // 成交量指标
  { label: 'AD(累积/派发线)', value: 'AD', category: 'volume' },
  { label: 'ADOSC(累积/派发振荡指标)', value: 'ADOSC', category: 'volume' },
  { label: 'OBV(能量潮)', value: 'OBV', category: 'volume' },
  { label: 'VOL_MA(成交量移动平均)', value: 'VOL_MA', category: 'volume' },
  { label: 'VR(成交量比率)', value: 'VR', category: 'volume' },
  { label: 'PVT(价量趋势)', value: 'PVT', category: 'volume' },
  // 动量指标
  { label: 'MOM(动量)', value: 'MOM', category: 'momentum' },
  { label: 'ROC(变动率)', value: 'ROC', category: 'momentum' },
  { label: 'ROCP(变动率百分比)', value: 'ROCP', category: 'momentum' },
  { label: 'ROCR(变动率比值)', value: 'ROCR', category: 'momentum' },
  { label: 'ROCR100(变动率比值*100)', value: 'ROCR100', category: 'momentum' },
  { label: 'MFI(资金流量指标)', value: 'MFI', category: 'momentum' },
  { label: 'BIAS(乖离率)', value: 'BIAS', category: 'momentum' },
  { label: 'AROON(阿隆指标)', value: 'AROON', category: 'momentum' },
  // 波动率指标
  { label: 'ATR(真实波幅)', value: 'ATR', category: 'volatility' },
  { label: 'NATR(归一化真实波幅)', value: 'NATR', category: 'volatility' },
  { label: 'STDDEV(标准差)', value: 'STDDEV', category: 'volatility' },
  { label: 'HV(历史波动率)', value: 'HV', category: 'volatility' },
  // 周期指标
  { label: 'DPO(区间震荡线)', value: 'DPO', category: 'cycle' },
  { label: 'HT_DCPERIOD(希尔伯特周期)', value: 'HT_DCPERIOD', category: 'cycle' },
  { label: 'HT_SINE(希尔伯特正弦波)', value: 'HT_SINE', category: 'cycle' },
  { label: 'HT_TRENDMODE(希尔伯特趋势模式)', value: 'HT_TRENDMODE', category: 'cycle' },
  { label: 'FIB(斐波那契周期)', value: 'FIB', category: 'cycle' },
  // 其他
  { label: 'VWAP(成交量加权平均价)', value: 'VWAP', category: 'other' },
  { label: 'TYP(典型价格)', value: 'TYP', category: 'other' },
  { label: 'MEDPRICE(中位价)', value: 'MEDPRICE', category: 'other' },
])

// 预设指标映射
const presetIndicators: Record<string, string[]> = {
  trend: ['MA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'T3', 'KAMA', 'BOLL', 'SAR', 'HT_TRENDLINE'],
  volume: ['AD', 'ADOSC', 'OBV', 'VOL_MA', 'VR', 'PVT'],
  oscillator: ['RSI', 'KDJ', 'STOCH', 'STOCHF', 'MACD', 'STOCHRSI', 'ULTOSC', 'CCI', 'DX', 'TRIX', 'APO', 'PPO', 'WR'],
  momentum: ['MOM', 'ROC', 'ROCP', 'ROCR', 'ROCR100', 'MFI', 'BIAS', 'AROON'],
  volatility: ['ATR', 'NATR', 'STDDEV', 'HV'],
  cycle: ['DPO', 'HT_DCPERIOD', 'HT_SINE', 'HT_TRENDMODE', 'FIB'],
  other: ['VWAP', 'TYP', 'MEDPRICE']
}

// 方法
const toggleCalcType = (type: string) => {
  const index = selectedCalcTypes.value.indexOf(type)
  if (index === -1) {
    selectedCalcTypes.value.push(type)
  } else {
    selectedCalcTypes.value.splice(index, 1)
  }
}

const togglePreset = (type: string) => {
  const index = selectedPresets.value.indexOf(type)
  if (index === -1) {
    selectedPresets.value.push(type)
    const inds = presetIndicators[type] || []
    for (const ind of inds) {
      if (!selectedIndicators.value.includes(ind)) {
        selectedIndicators.value.push(ind)
      }
    }
  } else {
    selectedPresets.value.splice(index, 1)
    const inds = presetIndicators[type] || []
    for (const ind of inds) {
      // 只删除只属于当前 preset 的指标
      const belongsToOther = Object.entries(presetIndicators)
        .filter(([key]) => key !== type && selectedPresets.value.includes(key))
        .some(([, inds]) => inds.includes(ind))
      if (!belongsToOther) {
        selectedIndicators.value = selectedIndicators.value.filter(i => i !== ind)
      }
    }
  }
}

const getTaskStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: props.isZh ? '等待中' : 'Pending',
    running: props.isZh ? '运行中' : 'Running',
    completed: props.isZh ? '已完成' : 'Completed',
    failed: props.isZh ? '失败' : 'Failed'
  }
  return map[status] || status
}

const runCalculation = async () => {
  isCalculating.value = true
  try {
    const hasFactors = selectedCalcTypes.value.length > 0
    const hasIndicators = selectedIndicators.value.length > 0
    if (!hasFactors && !hasIndicators) {
      return
    }

    const newTask: CalculationTask = {
      task_id: `task_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
      expression: selectedCalcTypes.value.join(', ') + (selectedIndicators.value.length > 0 ? ` + ${selectedIndicators.value.length} indicators` : ''),
      status: 'running',
      progress: 0,
      created_at: new Date().toLocaleString()
    }

    calculationTasks.value.unshift(newTask)
    console.log('Factor calculation:', selectedCalcTypes.value, customFactorExpression.value)
    console.log('Indicator calculation:', selectedIndicators.value)

    // 模拟计算进度
    for (let i = 0; i <= 100; i += 10) {
      await new Promise(r => setTimeout(r, 100))
      newTask.progress = i
      calculationTasks.value = [...calculationTasks.value]
    }

    newTask.status = 'completed'
    calculationTasks.value = [...calculationTasks.value]

    // 显示结果
    viewTaskResult(newTask.task_id)
  } catch (e) {
    if (calculationTasks.value.length > 0) {
      calculationTasks.value[0].status = 'failed'
    }
  } finally {
    isCalculating.value = false
  }
}

const viewTaskResult = (taskId: string) => {
  currentResultTaskId.value = taskId
  currentResult.value = {
    factor_name: 'Alpha158_Composite',
    statistics: {
      count: 12500,
      mean: 0.0023,
      std: 0.0145,
      min: -0.0832,
      max: 0.0915
    },
    data: Array.from({ length: 100 }, (_, i) => ({
      instrument: `00000${(i + 1).toString().padStart(2, '0')}.SZ`,
      name: `股票${i + 1}`,
      datetime: '2024-01-15',
      value: (Math.random() - 0.5) * 0.1
    }))
  }
}

const retryTask = (taskId: string) => {
  const task = calculationTasks.value.find(t => t.task_id === taskId)
  if (task) {
    task.status = 'running'
    task.progress = 0
    runCalculation()
  }
}

const deleteTask = (taskId: string) => {
  calculationTasks.value = calculationTasks.value.filter(t => t.task_id !== taskId)
  if (currentResultTaskId.value === taskId) {
    currentResult.value = null
    currentResultTaskId.value = null
  }
}

const exportResult = (format: 'csv' | 'excel') => {
  console.log('Export result as:', format)
}

const saveToQlib = () => {
  console.log('Save to QLib format')
}
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
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.type-card {
  flex: 1;
  min-width: 150px;
  max-width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;

  &:hover {
    border-color: var(--accent-blue);
  }

  &.active {
    border-color: var(--accent-blue);
    background: rgba(41, 98, 255, 0.1);
  }

  .type-card-icon {
    width: 32px;
    height: 32px;
    margin-bottom: 8px;
    color: var(--text-primary);
  }

  .type-card-content {
    text-align: center;
  }

  .type-card-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .type-card-desc {
    font-size: 11px;
    color: var(--text-secondary);
    margin-top: 4px;
  }

  .type-card-check {
    position: absolute;
    top: 8px;
    right: 8px;

    .check-icon {
      width: 16px;
      height: 16px;
      color: var(--accent-blue);
    }
  }
}

.indicator-section {
  .indicator-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .indicator-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--text-primary);
  }

  .indicator-icon {
    width: 16px;
    height: 16px;
  }
}

.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.action-buttons {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;

  &.btn-primary {
    background: var(--accent-blue);
    color: white;
    border: none;

    &:hover:not(:disabled) {
      background: #1a4fd8;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

.task-list-section {
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;

  &.pass, &.completed {
    background: rgba(38, 166, 154, 0.2);
    color: var(--color-down);
  }

  &.fail, &.failed {
    background: rgba(239, 83, 80, 0.2);
    color: var(--color-up);
  }

  &.running {
    background: rgba(41, 98, 255, 0.2);
    color: var(--accent-blue);
  }

  &.pending {
    background: rgba(120, 123, 134, 0.2);
    color: var(--text-secondary);
  }
}

.result-viewer-section {
  .result-stats {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .stat-card {
    flex: 1;
    min-width: 100px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 12px;
    text-align: center;

    .stat-icon {
      width: 24px;
      height: 24px;
      margin: 0 auto 8px;
      color: var(--text-secondary);
    }

    .stat-label {
      font-size: 10px;
      color: var(--text-secondary);
      text-transform: uppercase;
    }

    .stat-value {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin-top: 4px;
    }
  }
}

.result-actions {
  .result-btn-group {
    display: flex;
    gap: 0;
  }
}

.icon-xs {
  width: 12px;
  height: 12px;
  margin-right: 4px;
  vertical-align: middle;
}

.icon-sm {
  width: 16px;
  height: 16px;
}

.result-table {
}
</style>
