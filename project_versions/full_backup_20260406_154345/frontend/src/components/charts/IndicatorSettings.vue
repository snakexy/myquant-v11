<template>
  <teleport to="body">
    <div v-if="visible" class="indicator-settings-overlay" @click="handleCancel"></div>
    <div
      v-if="visible"
      class="indicator-settings-panel"
      :style="panelStyle"
      @click.stop
    >
      <div class="settings-header">
        <span>{{ config?.name }} 参数设置</span>
        <button class="settings-close-btn" @click="handleCancel">×</button>
      </div>

      <div class="settings-content">
        <!-- MA特殊处理：均线勾选 -->
        <div v-if="indicatorId === 'MA'" class="settings-section">
          <div class="section-title">显示均线</div>
          <div class="ma-checkboxes">
            <label
              v-for="ma in maLineOptions"
              :key="ma.key"
              class="ma-checkbox-item"
            >
              <input
                type="checkbox"
                :checked="visibleMaLines.includes(ma.key)"
                @change="toggleMaLine(ma.key)"
              />
              <span class="ma-label" :style="{ color: ma.color }">{{ ma.label }}</span>
            </label>
          </div>
        </div>

        <!-- BOLL线条设置 -->
        <div v-else-if="indicatorId === 'BOLL'" class="settings-section">
          <div class="section-title">线条设置</div>
          <div v-for="line in bollLineOptions" :key="line.key" class="line-setting-row">
            <span class="line-label" :style="{ color: getLineColor(line.key, line.color) }">
              {{ line.label }}
            </span>
            <div class="line-controls">
              <input
                type="color"
                :value="getLineColor(line.key, line.color)"
                @input="setLineColor(line.key, ($event.target as HTMLInputElement).value)"
                class="color-input"
              />
              <select
                :value="getLineStyle(line.key)"
                @change="setLineStyle(line.key, ($event.target as HTMLSelectElement).value)"
                class="style-select"
              >
                <option value="0">实线</option>
                <option value="1">虚线</option>
                <option value="2">点线</option>
                <option value="3">点虚线</option>
              </select>
              <input
                type="number"
                :value="getLineWidth(line.key, 1)"
                @input="setLineWidth(line.key, ($event.target as HTMLInputElement).value)"
                min="1"
                max="5"
                class="width-input"
              />
            </div>
          </div>
        </div>

        <!-- 通用指标：MACD/KDJ/RSI等 -->
        <template v-else>
          <!-- 数值参数 -->
          <div v-if="Object.keys(numericParams).length > 0" class="settings-section">
            <div class="section-title">参数设置</div>
            <div v-for="(value, key) in numericParams" :key="key" class="param-row">
              <span class="param-label">{{ getParamLabel(key as string) }}</span>
              <input
                type="number"
                :value="getParamValue(key as string, value)"
                @input="setParamValue(key as string, ($event.target as HTMLInputElement).value)"
                min="1"
                max="200"
                class="param-input"
              />
            </div>
          </div>

          <!-- 线条设置 -->
          <div v-if="lineSettings.length > 0" class="settings-section">
            <div class="section-title">线条设置</div>
            <div v-for="line in lineSettings" :key="line.key" class="line-setting-row">
              <span class="line-label" :style="{ color: getLineColor(line.key, line.color) }">
                {{ line.label }}
              </span>
              <div class="line-controls">
                <input
                  type="color"
                  :value="getLineColor(line.key, line.color)"
                  @input="setLineColor(line.key, ($event.target as HTMLInputElement).value)"
                  class="color-input"
                />
                <select
                  :value="getLineStyle(line.key)"
                  @change="setLineStyle(line.key, ($event.target as HTMLSelectElement).value)"
                  class="style-select"
                >
                  <option value="0">实线</option>
                  <option value="1">虚线</option>
                  <option value="2">点线</option>
                  <option value="3">点虚线</option>
                </select>
                <input
                  type="number"
                  :value="getLineWidth(line.key, line.lineWidth || 2)"
                  @input="setLineWidth(line.key, ($event.target as HTMLInputElement).value)"
                  min="1"
                  max="5"
                  class="width-input"
                />
              </div>
            </div>
          </div>
        </template>
      </div>

      <div class="settings-footer">
        <button class="settings-btn reset" @click="handleReset">恢复默认</button>
        <button class="settings-btn cancel" @click="handleCancel">取消</button>
        <button class="settings-btn confirm" @click="handleConfirm">应用</button>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { getIndicatorConfig } from './indicator-registry'

interface Props {
  visible: boolean
  indicatorId: string
  currentParams: Record<string, any>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: [params: Record<string, any>]
  cancel: []
}>()

const formValue = ref<Record<string, any>>({})
const visibleMaLines = ref<string[]>(['ma5', 'ma10', 'ma20', 'ma30', 'ma60'])

// 面板位置
const panelStyle = {
  position: 'fixed' as const,
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  zIndex: 1001
}

// 获取指标配置
const config = computed(() => getIndicatorConfig(props.indicatorId))

// MA线条选项
const maLineOptions = [
  { key: 'ma5', label: 'MA5', color: '#FFFFFF' },
  { key: 'ma10', label: 'MA10', color: '#FFFF00' },
  { key: 'ma20', label: 'MA20', color: '#FF00FF' },
  { key: 'ma30', label: 'MA30', color: '#00FFFF' },
  { key: 'ma60', label: 'MA60', color: '#00FF00' }
]

// BOLL线条选项
const bollLineOptions = [
  { key: 'upper', label: '上轨', color: '#FF6B6B' },
  { key: 'middle', label: '中轨', color: '#26A69A' },
  { key: 'lower', label: '下轨', color: '#FF6B6B' }
]

// 通用指标：数值参数
const numericParams = computed(() => {
  const result: Record<string, number> = {}
  const c = config.value
  if (!c?.defaultParams) return result

  Object.entries(c.defaultParams).forEach(([key, value]) => {
    if (typeof value === 'number' && !Array.isArray(value)) {
      result[key] = value
    }
  })
  return result
})

// 通用指标：线条设置
const lineSettings = computed(() => {
  return config.value?.series || []
})

// 参数标签映射
const paramLabels: Record<string, string> = {
  fast: '快线周期',
  slow: '慢线周期',
  signal: '信号周期',
  kPeriod: 'K周期',
  dPeriod: 'D周期',
  jPeriod: 'J周期',
  period: '周期',
  stdDev: '标准差'
}

function getParamLabel(key: string): string {
  return paramLabels[key] || key
}

function getParamValue(key: string, defaultValue: number): number {
  return formValue.value[key] ?? defaultValue
}

function setParamValue(key: string, value: string) {
  formValue.value[key] = parseInt(value) || 1
}

function getLineColor(key: string, defaultColor: string): string {
  return formValue.value[key]?.color || defaultColor
}

function setLineColor(key: string, color: string) {
  if (!formValue.value[key]) formValue.value[key] = {}
  formValue.value[key].color = color
}

function getLineStyle(key: string): number {
  return formValue.value[key]?.lineStyle ?? 0
}

function setLineStyle(key: string, style: string) {
  if (!formValue.value[key]) formValue.value[key] = {}
  formValue.value[key].lineStyle = parseInt(style)
}

function getLineWidth(key: string, defaultWidth: number): number {
  return formValue.value[key]?.lineWidth || defaultWidth
}

function setLineWidth(key: string, width: string) {
  if (!formValue.value[key]) formValue.value[key] = {}
  formValue.value[key].lineWidth = Math.max(1, Math.min(5, parseInt(width) || 1))
}

function toggleMaLine(key: string) {
  const index = visibleMaLines.value.indexOf(key)
  if (index > -1) {
    visibleMaLines.value.splice(index, 1)
  } else {
    visibleMaLines.value.push(key)
  }
}

// 初始化表单
function initForm() {
  if (!config.value) return

  if (props.currentParams && Object.keys(props.currentParams).length > 0) {
    formValue.value = JSON.parse(JSON.stringify(props.currentParams))
  } else {
    formValue.value = {}
  }

  // 初始化MA可见性
  if (props.indicatorId === 'MA') {
    visibleMaLines.value = formValue.value.visibleLines || ['ma5', 'ma10', 'ma20', 'ma30', 'ma60']
  }

  // 初始化线条设置（使用默认值）
  config.value.series?.forEach(s => {
    if (!formValue.value[s.key]) {
      formValue.value[s.key] = {
        color: s.color,
        lineStyle: 0,
        lineWidth: s.lineWidth || 2
      }
    }
  })
}

// 监听打开时初始化
watch(() => props.visible, (newVal) => {
  if (newVal) initForm()
})

function handleCancel() {
  emit('cancel')
  emit('update:visible', false)
}

function handleReset() {
  formValue.value = {}
  visibleMaLines.value = ['ma5', 'ma10', 'ma20', 'ma30', 'ma60']
  initForm()
}

function handleConfirm() {
  const result: Record<string, any> = { ...formValue.value }

  // MA：保存可见线条
  if (props.indicatorId === 'MA') {
    result.visibleLines = [...visibleMaLines.value]
  }

  emit('confirm', result)
  emit('update:visible', false)
}
</script>

<style scoped>
.indicator-settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.indicator-settings-panel {
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
  min-width: 320px;
  max-width: 400px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.settings-header {
  padding: 12px 16px;
  border-bottom: 1px solid #2a2e39;
  font-size: 14px;
  font-weight: 600;
  color: #d1d4dc;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-close-btn {
  background: none;
  border: none;
  color: #787b86;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.settings-close-btn:hover {
  color: #d1d4dc;
}

.settings-content {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
}

.settings-section {
  margin-bottom: 16px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 12px;
  color: #787b86;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ma-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ma-checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.ma-checkbox-item input[type="checkbox"] {
  width: 14px;
  height: 14px;
  cursor: pointer;
}

.ma-label {
  font-size: 13px;
}

.line-setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #2a2e39;
}

.line-setting-row:last-child {
  border-bottom: none;
}

.line-label {
  font-size: 13px;
  min-width: 50px;
}

.line-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-input {
  width: 28px;
  height: 28px;
  border: 1px solid #2a2e39;
  border-radius: 4px;
  cursor: pointer;
  background: none;
  padding: 2px;
}

.color-input::-webkit-color-swatch-wrapper {
  padding: 0;
}

.color-input::-webkit-color-swatch {
  border: none;
  border-radius: 2px;
}

.style-select {
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 12px;
  padding: 4px 8px;
  cursor: pointer;
}

.width-input {
  width: 40px;
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 12px;
  padding: 4px 6px;
  text-align: center;
}

.param-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.param-label {
  font-size: 13px;
  color: #d1d4dc;
}

.param-input {
  width: 80px;
  background: #2a2e39;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  font-size: 13px;
  padding: 6px 10px;
  text-align: center;
}

.settings-footer {
  padding: 12px 16px;
  border-top: 1px solid #2a2e39;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.settings-btn {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  border: none;
}

.settings-btn.reset {
  background: transparent;
  color: #787b86;
}

.settings-btn.reset:hover {
  color: #d1d4dc;
}

.settings-btn.cancel {
  background: #363a45;
  color: #d1d4dc;
}

.settings-btn.cancel:hover {
  background: #434754;
}

.settings-btn.confirm {
  background: #2962ff;
  color: #fff;
}

.settings-btn.confirm:hover {
  background: #1e53e4;
}
</style>
