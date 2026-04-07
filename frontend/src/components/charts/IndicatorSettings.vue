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
        <!-- MA特殊处理：均线线条设置（带可见性复选框） -->
        <div v-if="indicatorId === 'MA'" class="settings-section">
          <div class="section-title">均线设置</div>
          <div v-for="line in maLineOptions" :key="line.key" class="line-setting-row">
            <!-- 可见性复选框 -->
            <label class="ma-visibility-checkbox">
              <input
                type="checkbox"
                :checked="visibleMaLines.includes(line.key)"
                @change="toggleMaLine(line.key)"
              />
            </label>
            <!-- 线条名称 -->
            <span class="line-label" :style="{ color: getLineColor(line.key, line.color) }">
              {{ line.label }}
            </span>
            <!-- 线条控制（颜色、线型、线宽） -->
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
                <option value="0">━━━ 实线</option>
                <option value="1">--- 虚线</option>
                <option value="2">··· 点线</option>
                <option value="3">·-·- 点虚线</option>
              </select>
              <input
                type="number"
                :value="getLineWidth(line.key, line.lineWidth || 1)"
                @input="setLineWidth(line.key, ($event.target as HTMLInputElement).value)"
                min="1"
                max="5"
                class="width-input"
              />
            </div>
          </div>
        </div>

        <!-- BOLL线条设置 -->
        <div v-else-if="indicatorId === 'BOLL'" class="settings-section">
          <div class="section-title">线条设置</div>
          <div v-for="line in bollLineOptions" :key="line.key" class="line-setting-row">
            <!-- 可见性复选框 -->
            <label class="ma-visibility-checkbox">
              <input
                type="checkbox"
                :checked="visibleBollLines.includes(line.key)"
                @change="toggleBollLine(line.key)"
              />
            </label>
            <!-- 线条名称 -->
            <span class="line-label" :style="{ color: getLineColor(line.key, line.color) }">
              {{ line.label }}
            </span>
            <!-- 线条控制（颜色、线型、线宽） -->
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
                <option value="0">━━━ 实线</option>
                <option value="1">--- 虚线</option>
                <option value="2">··· 点线</option>
                <option value="3">·-·- 点虚线</option>
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

        <!-- SMC指标设置 -->
        <div v-else-if="indicatorId === 'SMC'" class="settings-section">
          <div class="section-title">显示选项</div>

          <!-- 摆动点 -->
          <div class="param-row">
            <span class="param-label">显示摆动点</span>
            <input
              type="checkbox"
              :checked="smcOptions.show_swing_points"
              @change="toggleSmcOption('show_swing_points')"
              class="param-checkbox"
            />
          </div>

          <!-- BOS -->
          <div class="param-row">
            <span class="param-label">显示 BOS</span>
            <input
              type="checkbox"
              :checked="smcOptions.show_bos"
              @change="toggleSmcOption('show_bos')"
              class="param-checkbox"
            />
          </div>

          <!-- CHoCH -->
          <div class="param-row">
            <span class="param-label">显示 CHoCH</span>
            <input
              type="checkbox"
              :checked="smcOptions.show_choch"
              @change="toggleSmcOption('show_choch')"
              class="param-checkbox"
            />
          </div>

          <!-- 订单块 -->
          <div class="param-row">
            <span class="param-label">显示订单块</span>
            <input
              type="checkbox"
              :checked="smcOptions.show_ob"
              @change="toggleSmcOption('show_ob')"
              class="param-checkbox"
            />
          </div>

          <!-- FVG -->
          <div class="param-row">
            <span class="param-label">显示 FVG</span>
            <input
              type="checkbox"
              :checked="smcOptions.show_fvg"
              @change="toggleSmcOption('show_fvg')"
              class="param-checkbox"
            />
          </div>

          <div class="section-title" style="margin-top: 16px;">参数设置</div>

          <!-- 摆动检测周期 -->
          <div class="param-row">
            <span class="param-label">摆动周期</span>
            <input
              type="number"
              :value="getParamValue('swing_length', 50)"
              @input="setParamValue('swing_length', ($event.target as HTMLInputElement).value)"
              min="10"
              max="200"
              class="param-input"
            />
          </div>

          <div class="section-title" style="margin-top: 16px;">颜色设置</div>

          <!-- 摆动高点颜色 -->
          <div class="param-row">
            <span class="param-label">摆动高点</span>
            <input
              type="color"
              :value="getSmcColor('swing_highs_color', '#FF6B6B')"
              @input="setSmcColor('swing_highs_color', ($event.target as HTMLInputElement).value)"
              class="color-input"
            />
          </div>

          <!-- 摆动低点颜色 -->
          <div class="param-row">
            <span class="param-label">摆动低点</span>
            <input
              type="color"
              :value="getSmcColor('swing_lows_color', '#26A69A')"
              @input="setSmcColor('swing_lows_color', ($event.target as HTMLInputElement).value)"
              class="color-input"
            />
          </div>

          <!-- BOS 颜色 -->
          <div class="param-row">
            <span class="param-label">BOS</span>
            <input
              type="color"
              :value="getSmcColor('bos_color', '#FFD700')"
              @input="setSmcColor('bos_color', ($event.target as HTMLInputElement).value)"
              class="color-input"
            />
          </div>

          <!-- CHoCH 颜色 -->
          <div class="param-row">
            <span class="param-label">CHoCH</span>
            <input
              type="color"
              :value="getSmcColor('choch_color', '#9C27B0')"
              @input="setSmcColor('choch_color', ($event.target as HTMLInputElement).value)"
              class="color-input"
            />
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
                  <option value="0">━━━ 实线</option>
                  <option value="1">--- 虚线</option>
                  <option value="2">··· 点线</option>
                  <option value="3">·-·- 点虚线</option>
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
const visibleBollLines = ref<string[]>(['upper', 'middle', 'lower'])

// SMC 指标选项
const smcOptions = ref({
  show_swing_points: true,
  show_bos: true,
  show_choch: true,
  show_ob: true,
  show_fvg: true
})

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

function toggleBollLine(key: string) {
  const index = visibleBollLines.value.indexOf(key)
  if (index > -1) {
    visibleBollLines.value.splice(index, 1)
  } else {
    visibleBollLines.value.push(key)
  }
}

// SMC 指标相关函数
function toggleSmcOption(option: string) {
  smcOptions.value[option as keyof typeof smcOptions.value] = !smcOptions.value[option as keyof typeof smcOptions.value]
  formValue.value[option] = smcOptions.value[option as keyof typeof smcOptions.value]
}

function getSmcColor(key: string, defaultColor: string): string {
  return formValue.value[key] || defaultColor
}

function setSmcColor(key: string, color: string) {
  formValue.value[key] = color
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

  // 初始化BOLL可见性
  if (props.indicatorId === 'BOLL') {
    visibleBollLines.value = formValue.value.visibleLines || ['upper', 'middle', 'lower']
  }

  // 初始化SMC选项
  if (props.indicatorId === 'SMC') {
    smcOptions.value.show_swing_points = formValue.value.show_swing_points !== false
    smcOptions.value.show_bos = formValue.value.show_bos !== false
    smcOptions.value.show_choch = formValue.value.show_choch !== false
    smcOptions.value.show_ob = formValue.value.show_ob !== false
    smcOptions.value.show_fvg = formValue.value.show_fvg !== false
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
  visibleBollLines.value = ['upper', 'middle', 'lower']
  smcOptions.value = {
    show_swing_points: true,
    show_bos: true,
    show_choch: true,
    show_ob: true,
    show_fvg: true
  }
  initForm()
}

function handleConfirm() {
  const result: Record<string, any> = { ...formValue.value }

  // MA：保存可见线条
  if (props.indicatorId === 'MA') {
    result.visibleLines = [...visibleMaLines.value]
  }

  // BOLL：保存可见线条
  if (props.indicatorId === 'BOLL') {
    result.visibleLines = [...visibleBollLines.value]
  }

  // SMC：保存显示选项
  if (props.indicatorId === 'SMC') {
    result.show_swing_points = smcOptions.value.show_swing_points
    result.show_bos = smcOptions.value.show_bos
    result.show_choch = smcOptions.value.show_choch
    result.show_ob = smcOptions.value.show_ob
    result.show_fvg = smcOptions.value.show_fvg
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

.ma-visibility-checkbox {
  display: flex;
  align-items: center;
  margin-right: 8px;
  min-width: 20px;
}

.ma-visibility-checkbox input[type="checkbox"] {
  width: 14px;
  height: 14px;
  cursor: pointer;
  margin: 0;
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

.param-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
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
