/**
 * IndicatorConfigPanel - 指标配置面板
 *
 * 提供指标的添加、删除、参数配置功能
 */

<template>
  <div class="config-panel-overlay" @click="handleClose">
    <div class="config-panel" @click.stop>
      <!-- 标题栏 -->
      <div class="panel-header">
        <h3>技术指标配置</h3>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <!-- 内容区 -->
      <div class="panel-content">
        <!-- 主图指标 -->
        <section class="config-section">
          <div class="section-title">主图叠加指标</div>
          <div class="indicator-list">
            <div
              v-for="indicator in availableMainIndicators"
              :key="indicator.id"
              class="indicator-item"
              :class="{ active: hasMainIndicator(indicator.id) }"
            >
              <span class="indicator-name">{{ indicator.name }}</span>
              <button
                class="action-btn"
                @click="toggleMainIndicator(indicator.id)"
              >
                {{ hasMainIndicator(indicator.id) ? '移除' : '添加' }}
              </button>
            </div>
          </div>
        </section>

        <!-- 副图指标 -->
        <section class="config-section">
          <div class="section-title">副图独立指标</div>
          <div class="indicator-list">
            <div
              v-for="indicator in availableSubIndicators"
              :key="indicator.id"
              class="indicator-item"
              :class="{ active: hasSubIndicator(indicator.id) }"
            >
              <span class="indicator-name">{{ indicator.name }}</span>
              <span class="indicator-desc">{{ indicator.description }}</span>
              <div class="indicator-actions">
                <button
                  v-if="hasSubIndicator(indicator.id)"
                  class="action-btn secondary"
                  @click="toggleSubIndicator(indicator.id)"
                >
                  隐藏
                </button>
                <button
                  v-else
                  class="action-btn"
                  @click="addSubIndicator(indicator.id)"
                >
                  添加
                </button>
                <button
                  v-if="hasSubIndicator(indicator.id)"
                  class="config-btn"
                  @click="openParamConfig(indicator)"
                >
                  ⚙️
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- 参数配置区域 -->
        <section v-if="configuringIndicator" class="config-section">
          <div class="section-title">
            {{ configIndicatorName }} 参数配置
          </div>
          <div class="params-list">
            <div
              v-for="(param, index) in currentIndicatorParams"
              :key="index"
              class="param-item"
            >
              <label class="param-label">{{ param.name || param.key }}</label>
              <input
                v-if="param.type === 'number'"
                type="number"
                :value="param.value"
                :min="param.min"
                :max="param.max"
                :step="param.step || 1"
                @input="updateParam(param.key, $event.target.value)"
                class="param-input"
              />
              <select
                v-else-if="param.type === 'select'"
                :value="param.value"
                @change="updateParam(param.key, $event.target.value)"
                class="param-input"
              >
                <option
                  v-for="option in param.options"
                  :key="option"
                  :value="option"
                >
                  {{ option }}
                </option>
              </select>
              <span v-else class="param-value">{{ param.value }}</span>
            </div>
          </div>
          <div class="params-actions">
            <button class="btn btn-secondary" @click="cancelConfig">取消</button>
            <button class="btn btn-primary" @click="applyConfig">应用</button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface IndicatorMeta {
  id: string
  name: string
  type: 'main' | 'sub'
  description?: string
  params?: any
}

interface Props {
  availableIndicators: {
    main: IndicatorMeta[]
    sub: IndicatorMeta[]
  }
  activeMainIndicators: any[]
  activeSubIndicators: any[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'add-main': [indicator: string]
  'add-sub': [indicator: string]
  'remove-main': [indicator: string]
  'remove-sub': [indicator: string]
  'update-params': [indicator: string, params: any]
  close: []
}>()

// UI 状态
const configuringIndicator = ref<string | null>(null)
const currentIndicatorParams = ref<any[]>([])

// 可用指标
const availableMainIndicators = computed(() => props.availableIndicators.main)
const availableSubIndicators = computed(() => props.availableIndicators.sub)

/**
 * 检查主图指标是否已添加
 */
const hasMainIndicator = (indicatorId: string): boolean => {
  return props.activeMainIndicators.some((ind: any) => ind.id === indicatorId)
}

/**
 * 检查副图指标是否已添加
 */
const hasSubIndicator = (indicatorId: string): boolean => {
  return props.activeSubIndicators.some((ind: any) => ind.id === indicatorId)
}

/**
 * 切换主图指标
 */
const toggleMainIndicator = (indicatorId: string) => {
  if (hasMainIndicator(indicatorId)) {
    emit('remove-main', indicatorId)
  } else {
    emit('add-main', indicatorId)
  }
}

/**
 * 切换副图指标
 */
const toggleSubIndicator = (indicatorId: string) => {
  emit('remove-sub', indicatorId)
}

/**
 * 添加副图指标
 */
const addSubIndicator = (indicatorId: string) => {
  emit('add-sub', indicatorId)
}

/**
 * 打开参数配置
 */
const openParamConfig = (indicator: any) => {
  configuringIndicator.value = indicator.id

  // 构建参数列表
  const params = getIndicatorParams(indicator.id)
  currentIndicatorParams.value = Object.entries(params).map(([key, value]) => ({
    key,
    name: getParamDisplayName(indicator.id, key),
    type: getParamType(indicator.id, key),
    value,
    ...getParamConstraints(indicator.id, key)
  }))
}

/**
 * 更新参数
 */
const updateParam = (key: string, value: any) => {
  const param = currentIndicatorParams.value.find(p => p.key === key)
  if (param) {
    param.value = value
  }
}

/**
 * 取消配置
 */
const cancelConfig = () => {
  configuringIndicator.value = null
  currentIndicatorParams.value = []
}

/**
 * 应用配置
 */
const applyConfig = () => {
  if (!configuringIndicator.value) return

  const params: any = {}
  for (const param of currentIndicatorParams.value) {
    params[param.key] = param.value
  }

  emit('update-params', configuringIndicator.value, params)
  configuringIndicator.value = null
  currentIndicatorParams.value = []
}

/**
 * 获取指标参数定义
 */
function getIndicatorParams(indicatorId: string): Record<string, any> {
  const paramsMap: Record<string, any> = {
    MA: { periods: [5, 10, 20, 30, 60] },
    BOLL: { period: 20, stdDev: 2 },
    MACD: { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 },
    KDJ: { fastKPeriod: 9, slowKPeriod: 3, slowDPeriod: 3 },
    RSI: { period: 14 },
    CCI: { period: 14 },
    OBV: {},
    ATR: { period: 14 }
  }

  return paramsMap[indicatorId] || {}
}

/**
 * 获取参数显示名称
 */
function getParamDisplayName(indicatorId: string, key: string): string {
  const names: Record<string, Record<string, string>> = {
    MA: {
      periods: '均线周期'
    },
    BOLL: {
      period: '周期',
      stdDev: '标准差倍数'
    },
    MACD: {
      fastPeriod: '快线周期',
      slowPeriod: '慢线周期',
      signalPeriod: '信号线周期'
    },
    KDJ: {
      fastKPeriod: 'K值周期',
      slowKPeriod: 'K值平滑',
      slowDPeriod: 'D值周期'
    },
    RSI: {
      period: '周期'
    },
    CCI: {
      period: '周期'
    },
    ATR: {
      period: '周期'
    }
  }

  return names[indicatorId]?.[key] || key
}

/**
 * 获取参数类型
 */
function getParamType(indicatorId: string, key: string): string {
  if (indicatorId === 'MA' && key === 'periods') {
    return 'select'
  }
  return 'number'
}

/**
 * 获取参数约束
 */
function getParamConstraints(indicatorId: string, key: string) {
  const constraints: Record<string, Record<string, any>> = {
    MACD: {
      fastPeriod: { min: 5, max: 50, step: 1 },
      slowPeriod: { min: 10, max: 100, step: 1 },
      signalPeriod: { min: 2, max: 20, step: 1 }
    },
    KDJ: {
      fastKPeriod: { min: 3, max: 30, step: 1 },
      slowKPeriod: { min: 1, max: 10, step: 1 },
      slowDPeriod: { min: 1, max: 10, step: 1 }
    },
    RSI: {
      period: { min: 2, max: 50, step: 1 }
    },
    CCI: {
      period: { min: 5, max: 50, step: 1 }
    },
    ATR: {
      period: { min: 5, max: 50, step: 1 }
    }
  }

  return constraints[indicatorId]?.[key] || {}
}

/**
 * 关闭面板
 */
const handleClose = () => {
  emit('close')
}

const configIndicatorName = computed(() => {
  const names: Record<string, string> = {
    MACD: 'MACD',
    KDJ: 'KDJ',
    RSI: 'RSI',
    CCI: 'CCI',
    OBV: 'OBV',
    ATR: 'ATR',
    BOLL: '布林带',
    MA: '移动平均'
  }
  return configuringIndicator.value ? names[configuringIndicator.value] || configuringIndicator.value : ''
})
</script>

<style scoped lang="scss">
.config-panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.config-panel {
  background: #1E222D;
  border-radius: 8px;
  width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #2A2E39;

  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #E1E4E8;
  }

  .close-btn {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    color: #787B86;
    font-size: 20px;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.2s;

    &:hover {
      background: rgba(239, 68, 68, 0.1);
      color: #ef5350;
    }
  }
}

.panel-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.config-section {
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

.indicator-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.indicator-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: #2A2E39;
  border-radius: 6px;
  border: 1px solid transparent;
  transition: all 0.2s;

  &.active {
    border-color: #2962FF;
    background: rgba(41, 98, 255, 0.1);
  }

  .indicator-name {
    font-weight: 500;
    color: #E1E4E8;
  }

  .indicator-desc {
    font-size: 12px;
    color: #787B86;
  }

  .indicator-actions {
    display: flex;
    gap: 8px;
  }
}

.action-btn {
  padding: 6px 12px;
  border: 1px solid #2962FF;
  background: transparent;
  color: #2962FF;
  font-size: 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(41, 98, 255, 0.1);
  }

  &.secondary {
    border-color: #787B86;
    color: #787B86;

    &:hover {
      background: rgba(120, 123, 134, 0.1);
    }
  }
}

.config-btn {
  padding: 4px 8px;
  background: #1E222D;
  border: none;
  color: #9CA3AF;
  font-size: 14px;
  cursor: pointer;
  border-radius: 4px;

  &:hover {
    color: #D1D5DB;
  }
}

.params-list {
  margin: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.param-label {
  font-size: 13px;
  color: #9CA3AF;
}

.param-input {
  width: 120px;
  padding: 6px 10px;
  background: #131722;
  border: 1px solid #2A2E39;
  border-radius: 4px;
  color: #E1E4E8;
  font-size: 13px;

  &:focus {
    outline: none;
    border-color: #2962FF;
  }
}

.params-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #2A2E39;
}

.btn {
  flex: 1;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;

  &.primary {
    background: #2962FF;
    border: none;
    color: white;

    &:hover {
      background: #1E5BFF;
    }
  }

  &.secondary {
    background: #2A2E39;
    border: 1px solid #2A2E39;
    color: #B2B5BE;

    &:hover {
      background: #1E222D;
      color: #E1E4E8;
    }
  }
}
</style>
