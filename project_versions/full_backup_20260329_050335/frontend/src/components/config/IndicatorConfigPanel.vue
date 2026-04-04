<template>
  <div class="indicator-config-panel">
    <div class="panel-header">
      <h3>指标参数配置</h3>
      <button class="close-btn" @click="$emit('close')">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <div class="panel-content">
      <!-- MA均线配置 -->
      <div class="config-section">
        <h4>MA均线参数</h4>
        <div class="param-grid">
          <div class="param-item">
            <label>MA5周期</label>
            <input
              type="number"
              v-model.number="localConfig.ma5"
              min="2"
              max="200"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>MA10周期</label>
            <input
              type="number"
              v-model.number="localConfig.ma10"
              min="2"
              max="200"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>MA20周期</label>
            <input
              type="number"
              v-model.number="localConfig.ma20"
              min="2"
              max="200"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>MA30周期</label>
            <input
              type="number"
              v-model.number="localConfig.ma30"
              min="2"
              max="200"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>MA60周期</label>
            <input
              type="number"
              v-model.number="localConfig.ma60"
              min="2"
              max="200"
              class="param-input"
            />
          </div>
        </div>
      </div>

      <!-- BOLL布林带配置 -->
      <div class="config-section">
        <h4>BOLL布林带参数</h4>
        <div class="param-grid">
          <div class="param-item">
            <label>周期</label>
            <input
              type="number"
              v-model.number="localConfig.bollPeriod"
              min="5"
              max="50"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>标准差倍数</label>
            <input
              type="number"
              v-model.number="localConfig.bollStdDev"
              min="1"
              max="5"
              step="0.5"
              class="param-input"
            />
          </div>
        </div>
      </div>

      <!-- MACD配置 -->
      <div class="config-section">
        <h4>MACD参数</h4>
        <div class="param-grid">
          <div class="param-item">
            <label>快线周期</label>
            <input
              type="number"
              v-model.number="localConfig.macdFast"
              min="5"
              max="50"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>慢线周期</label>
            <input
              type="number"
              v-model.number="localConfig.macdSlow"
              min="10"
              max="100"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>信号周期</label>
            <input
              type="number"
              v-model.number="localConfig.macdSignal"
              min="5"
              max="50"
              class="param-input"
            />
          </div>
        </div>
      </div>

      <!-- RSI配置 -->
      <div class="config-section">
        <h4>RSI参数</h4>
        <div class="param-grid">
          <div class="param-item">
            <label>RSI6周期</label>
            <input
              type="number"
              v-model.number="localConfig.rsi6"
              min="2"
              max="50"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>RSI12周期</label>
            <input
              type="number"
              v-model.number="localConfig.rsi12"
              min="2"
              max="50"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>RSI24周期</label>
            <input
              type="number"
              v-model.number="localConfig.rsi24"
              min="2"
              max="50"
              class="param-input"
            />
          </div>
        </div>
      </div>

      <!-- KDJ配置 -->
      <div class="config-section">
        <h4>KDJ参数</h4>
        <div class="param-grid">
          <div class="param-item">
            <label>K周期</label>
            <input
              type="number"
              v-model.number="localConfig.kdjK"
              min="2"
              max="50"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>D周期</label>
            <input
              type="number"
              v-model.number="localConfig.kdjD"
              min="2"
              max="50"
              class="param-input"
            />
          </div>
          <div class="param-item">
            <label>J周期</label>
            <input
              type="number"
              v-model.number="localConfig.kdjJ"
              min="2"
              max="50"
              class="param-input"
            />
          </div>
        </div>
      </div>

      <!-- 快速预设 -->
      <div class="config-section preset-section">
        <h4>快速预设</h4>
        <div class="preset-buttons">
          <button
            class="preset-btn"
            :class="{ active: localConfig.preset === 'short' }"
            @click="applyPreset('short')"
          >
            短线
          </button>
          <button
            class="preset-btn"
            :class="{ active: localConfig.preset === 'medium' }"
            @click="applyPreset('medium')"
          >
            中线
          </button>
          <button
            class="preset-btn"
            :class="{ active: localConfig.preset === 'long' }"
            @click="applyPreset('long')"
          >
            长线
          </button>
          <button
            class="preset-btn preset-btn-custom"
            @click="showSaveDialog = true"
            title="保存为自定义配置"
          >
            <i class="fas fa-plus"></i>
            保存
          </button>
        </div>

        <!-- 自定义配置列表 -->
        <div v-if="customConfigs.length > 0" class="custom-configs">
          <div class="custom-configs-header">
            <span>我的配置</span>
            <button class="edit-btn" @click="showManageDialog = true" title="管理自定义配置">
              <i class="fas fa-cog"></i>
            </button>
          </div>
          <div class="custom-config-buttons">
            <button
              v-for="config in customConfigs"
              :key="config.id"
              class="preset-btn preset-btn-custom"
              :class="{ active: appliedConfigId === config.id }"
              @click="applyCustomConfig(config)"
              :title="config.description || config.name"
            >
              {{ config.name }}
            </button>
          </div>
        </div>
      </div>

      <!-- 保存自定义配置对话框 -->
      <div v-if="showSaveDialog" class="dialog-overlay" @click="showSaveDialog = false">
        <div class="dialog-container" @click.stop>
          <div class="dialog-header">
            <h4>保存自定义配置</h4>
            <button class="close-btn" @click="showSaveDialog = false">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="dialog-content">
            <div class="form-group">
              <label>配置名称 <span class="required">*</span></label>
              <input
                v-model="newConfigName"
                type="text"
                class="form-input"
                placeholder="例如：激进短线、稳健波段"
                maxlength="20"
              />
            </div>
            <div class="form-group">
              <label>描述（可选）</label>
              <textarea
                v-model="newConfigDescription"
                class="form-textarea"
                placeholder="简单描述这个配置的特点"
                rows="3"
                maxlength="100"
              ></textarea>
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="showSaveDialog = false">
              取消
            </button>
            <button class="btn btn-primary" @click="saveCustomConfig" :disabled="!newConfigName.trim()">
              保存
            </button>
          </div>
        </div>
      </div>

      <!-- 管理自定义配置对话框 -->
      <div v-if="showManageDialog" class="dialog-overlay" @click="showManageDialog = false">
        <div class="dialog-container dialog-large" @click.stop>
          <div class="dialog-header">
            <h4>管理自定义配置</h4>
            <button class="close-btn" @click="showManageDialog = false">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="dialog-content">
            <div v-if="customConfigs.length === 0" class="empty-state">
              <i class="fas fa-folder-open"></i>
              <p>还没有保存的自定义配置</p>
            </div>
            <div v-else class="config-list">
              <div
                v-for="config in customConfigs"
                :key="config.id"
                class="config-list-item"
              >
                <div class="config-info">
                  <div class="config-name">{{ config.name }}</div>
                  <div class="config-description">{{ config.description || '无描述' }}</div>
                  <div class="config-meta">
                    <span class="config-date">{{ formatDate(config.createdAt) }}</span>
                  </div>
                </div>
                <div class="config-actions">
                  <button
                    class="action-btn"
                    @click="editConfig(config)"
                    title="编辑"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    class="action-btn action-btn-danger"
                    @click="deleteConfig(config.id)"
                    title="删除"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="panel-footer">
      <button class="btn btn-secondary" @click="resetToDefault">
        重置默认
      </button>
      <button class="btn btn-primary" @click="saveConfig">
        保存配置
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'

interface IndicatorConfig {
  // MA均线
  ma5: number
  ma10: number
  ma20: number
  ma30: number
  ma60: number

  // BOLL
  bollPeriod: number
  bollStdDev: number

  // MACD
  macdFast: number
  macdSlow: number
  macdSignal: number

  // RSI
  rsi6: number
  rsi12: number
  rsi24: number

  // KDJ
  kdjK: number
  kdjD: number
  kdjJ: number

  // 预设
  preset?: string
}

// 自定义配置接口
interface SavedIndicatorConfig {
  id: string
  name: string
  description?: string
  config: IndicatorConfig
  createdAt: number
  updatedAt: number
}

interface Props {
  stockCode?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  configChange: [config: IndicatorConfig]
}>()

// 默认配置
const defaultConfig: IndicatorConfig = {
  ma5: 5,
  ma10: 10,
  ma20: 20,
  ma30: 30,
  ma60: 60,
  bollPeriod: 20,
  bollStdDev: 2,
  macdFast: 12,
  macdSlow: 26,
  macdSignal: 9,
  rsi6: 6,
  rsi12: 12,
  rsi24: 24,
  kdjK: 9,
  kdjD: 3,
  kdjJ: 3,
  preset: 'medium'
}

// 预设配置
const presets = {
  short: {
    ma5: 5,
    ma10: 10,
    ma20: 20,
    ma30: 30,
    ma60: 60,
    bollPeriod: 20,
    bollStdDev: 2,
    macdFast: 12,
    macdSlow: 26,
    macdSignal: 9,
    rsi6: 6,
    rsi12: 12,
    rsi24: 24,
    kdjK: 9,
    kdjD: 3,
    kdjJ: 3,
    preset: 'short'
  },
  medium: {
    ma5: 5,
    ma10: 10,
    ma20: 20,
    ma30: 30,
    ma60: 60,
    bollPeriod: 20,
    bollStdDev: 2,
    macdFast: 12,
    macdSlow: 26,
    macdSignal: 9,
    rsi6: 6,
    rsi12: 12,
    rsi24: 24,
    kdjK: 9,
    kdjD: 3,
    kdjJ: 3,
    preset: 'medium'
  },
  long: {
    ma5: 5,
    ma10: 10,
    ma20: 20,
    ma30: 30,
    ma60: 60,
    bollPeriod: 20,
    bollStdDev: 2,
    macdFast: 12,
    macdSlow: 26,
    macdSignal: 9,
    rsi6: 6,
    rsi12: 12,
    rsi24: 24,
    kdjK: 9,
    kdjD: 3,
    kdjJ: 3,
    preset: 'long'
  }
}

// 本地配置（从localStorage加载）
const localConfig = ref<IndicatorConfig>({ ...defaultConfig })

// 自定义配置管理
const customConfigs = ref<SavedIndicatorConfig[]>([])
const appliedConfigId = ref<string | null>(null)
const showSaveDialog = ref(false)
const showManageDialog = ref(false)
const newConfigName = ref('')
const newConfigDescription = ref('')
const editingConfigId = ref<string | null>(null)

// 加载保存的配置
const loadConfig = () => {
  const saved = localStorage.getItem('indicatorConfig')
  if (saved) {
    try {
      localConfig.value = { ...defaultConfig, ...JSON.parse(saved) }
    } catch (error) {
      console.error('加载配置失败:', error)
      localConfig.value = { ...defaultConfig }
    }
  } else {
    localConfig.value = { ...defaultConfig }
  }
}

// 保存配置
const saveConfig = async () => {
  try {
    // 保存到localStorage
    localStorage.setItem('indicatorConfig', JSON.stringify(localConfig.value))

    // TODO: 发送到后端保存
    // await fetch('/api/v1/user/indicator-config', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(localConfig.value)
    // })

    emit('configChange', localConfig.value)
    alert('配置保存成功！')
  } catch (error) {
    console.error('保存配置失败:', error)
    alert('保存失败，请重试')
  }
}

// 重置为默认值
const resetToDefault = () => {
  localConfig.value = { ...defaultConfig }
}

// 应用预设
const applyPreset = (preset: 'short' | 'medium' | 'long') => {
  localConfig.value = { ...presets[preset] }
  appliedConfigId.value = null
}

// 加载自定义配置列表
const loadCustomConfigs = () => {
  const saved = localStorage.getItem('customIndicatorConfigs')
  if (saved) {
    try {
      customConfigs.value = JSON.parse(saved)
    } catch (error) {
      console.error('加载自定义配置失败:', error)
      customConfigs.value = []
    }
  } else {
    customConfigs.value = []
  }
}

// 保存自定义配置列表
const saveCustomConfigsList = () => {
  localStorage.setItem('customIndicatorConfigs', JSON.stringify(customConfigs.value))
}

// 保存为自定义配置
const saveCustomConfig = () => {
  if (!newConfigName.value.trim()) {
    return
  }

  const config: SavedIndicatorConfig = {
    id: editingConfigId.value || Date.now().toString(),
    name: newConfigName.value.trim(),
    description: newConfigDescription.value.trim(),
    config: { ...localConfig.value },
    createdAt: editingConfigId.value ? customConfigs.value.find(c => c.id === editingConfigId.value)?.createdAt || Date.now() : Date.now(),
    updatedAt: Date.now()
  }

  if (editingConfigId.value) {
    // 更新现有配置
    const index = customConfigs.value.findIndex(c => c.id === editingConfigId.value)
    if (index !== -1) {
      customConfigs.value[index] = config
    }
    editingConfigId.value = null
  } else {
    // 添加新配置
    customConfigs.value.push(config)
  }

  saveCustomConfigsList()

  // 清空输入
  newConfigName.value = ''
  newConfigDescription.value = ''
  showSaveDialog.value = false

  alert('配置保存成功！')
}

// 应用自定义配置
const applyCustomConfig = (savedConfig: SavedIndicatorConfig) => {
  localConfig.value = { ...savedConfig.config }
  appliedConfigId.value = savedConfig.id
  console.log('已应用自定义配置:', savedConfig.name)
}

// 编辑配置
const editConfig = (savedConfig: SavedIndicatorConfig) => {
  // 先应用配置到界面
  localConfig.value = { ...savedConfig.config }
  appliedConfigId.value = savedConfig.id

  // 打开保存对话框
  newConfigName.value = savedConfig.name
  newConfigDescription.value = savedConfig.description || ''
  editingConfigId.value = savedConfig.id
  showManageDialog.value = false
  showSaveDialog.value = true
}

// 删除配置
const deleteConfig = (id: string) => {
  if (confirm('确定要删除这个配置吗？')) {
    customConfigs.value = customConfigs.value.filter(c => c.id !== id)
    saveCustomConfigsList()

    // 如果删除的是当前应用的配置，清除标记
    if (appliedConfigId.value === id) {
      appliedConfigId.value = null
    }
  }
}

// 格式化日期
const formatDate = (timestamp: number) => {
  const date = new Date(timestamp)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

// 组件挂载时加载配置
onMounted(() => {
  loadConfig()
  loadCustomConfigs()
})

// 暴露方法
defineExpose({
  saveConfig,
  resetToDefault,
  getConfig: () => localConfig.value
})
</script>

<style scoped>
.indicator-config-panel {
  background: #1a1a2e;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #252530;
  border-bottom: 1px solid #374151;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #f8fafc;
}

.close-btn {
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #374151;
  color: #f8fafc;
}

.panel-content {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.config-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #374151;
}

.config-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.config-section h4 {
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 500;
  color: #cbd5e1;
}

.param-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.param-item label {
  font-size: 11px;
  color: #9ca3af;
}

.param-input {
  background: #0f0f23;
  border: 1px solid #374151;
  border-radius: 4px;
  padding: 6px 10px;
  color: #f8fafc;
  font-size: 12px;
  font-family: 'Roboto Mono', monospace;
  transition: all 0.2s;
}

.param-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.preset-section {
  border-bottom: none;
}

.preset-buttons {
  display: flex;
  gap: 8px;
}

.preset-btn {
  flex: 1;
  background: #252530;
  border: 1px solid #374151;
  color: #9ca3af;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.preset-btn:hover {
  background: #374151;
  color: #f8fafc;
}

.preset-btn.active {
  background: #1e40af;
  border-color: #3b82f6;
  color: #f8fafc;
}

.panel-footer {
  display: flex;
  gap: 8px;
  padding: 16px 20px;
  background: #252530;
  border-top: 1px solid #374151;
}

.btn {
  flex: 1;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: #374151;
  color: #f8fafc;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-primary {
  background: #3b82f6;
  color: #ffffff;
}

.btn-primary:hover {
  background: #2563eb;
}

/* 滚动条样式 */
.panel-content::-webkit-scrollbar {
  width: 6px;
}

.panel-content::-webkit-scrollbar-track {
  background: #1a1a2e;
}

.panel-content::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 3px;
}

.panel-content::-webkit-scrollbar-thumb:hover {
  background: #4b5563;
}

/* 自定义配置样式 */
.preset-btn-custom {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: #2a2a3e;
  border-color: #2962ff;
  color: #2962ff;
}

.preset-btn-custom:hover {
  background: #373750;
  border-color: #7c8ef5;
  color: #7c8ef5;
}

.custom-configs {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #374151;
}

.custom-configs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.custom-configs-header span {
  font-size: 12px;
  font-weight: 500;
  color: #cbd5e1;
}

.edit-btn {
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: #374151;
  color: #f8fafc;
}

.custom-config-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 对话框样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.dialog-container {
  background: #1a1a2e;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.3s ease;
}

.dialog-large {
  max-width: 600px;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #252530;
  border-bottom: 1px solid #374151;
}

.dialog-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #f8fafc;
}

.dialog-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  background: #252530;
  border-top: 1px solid #374151;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: #cbd5e1;
  margin-bottom: 8px;
}

.required {
  color: #ef4444;
}

.form-input,
.form-textarea {
  width: 100%;
  background: #0f0f23;
  border: 1px solid #374151;
  border-radius: 6px;
  padding: 10px 12px;
  color: #f8fafc;
  font-size: 13px;
  transition: all 0.2s;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 60px;
}

/* 配置列表样式 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

.config-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #0f0f23;
  border: 1px solid #374151;
  border-radius: 8px;
  transition: all 0.2s;
}

.config-list-item:hover {
  border-color: #4b5563;
  background: #1a1a2e;
}

.config-info {
  flex: 1;
  min-width: 0;
}

.config-name {
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc;
  margin-bottom: 4px;
}

.config-description {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.config-meta {
  font-size: 11px;
  color: #6b7280;
}

.config-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  background: #252530;
  border: 1px solid #374151;
  color: #9ca3af;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #374151;
  color: #f8fafc;
}

.action-btn-danger:hover {
  background: #ef4444;
  border-color: #ef4444;
  color: #ffffff;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
