<template>
  <div class="circuit-board-view">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-content">
        <div class="logo-section">
          <h1 class="app-title">
            <i class="fas fa-microchip"></i>
            MyQuant 电路板架构
          </h1>
          <p class="app-subtitle">智能节点激活系统 - 总体架构电路板</p>
        </div>
        
        <div class="header-actions">
          <button class="header-btn" @click="toggleFullscreen">
            <i class="fas fa-expand"></i>
            全屏
          </button>
          <button class="header-btn" @click="showHelp">
            <i class="fas fa-question-circle"></i>
            帮助
          </button>
          <button class="header-btn" @click="openSettings">
            <i class="fas fa-cog"></i>
            设置
          </button>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 电路板架构组件 -->
      <CircuitBoardArchitecture ref="circuitBoard" />
    </main>

    <!-- 帮助模态框 -->
    <div v-if="showHelpModal" class="modal-overlay" @click="closeHelp">
      <div class="modal-content help-modal" @click.stop>
        <div class="modal-header">
          <h3>电路板架构使用指南</h3>
          <button class="close-btn" @click="closeHelp">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="help-section">
            <h4>🎯 基本操作</h4>
            <ul>
              <li><strong>功能选择：</strong>点击顶部功能按钮选择要激活的功能模块</li>
              <li><strong>节点激活：</strong>点击画布上的节点进行单独激活/停用</li>
              <li><strong>批量激活：</strong>选择功能后点击"激活选中功能"批量激活相关节点</li>
              <li><strong>视图控制：</strong>使用缩放按钮或鼠标滚轮调整视图大小</li>
            </ul>
          </div>
          
          <div class="help-section">
            <h4>🔧 高级功能</h4>
            <ul>
              <li><strong>自动优化：</strong>点击"自动优化"让系统智能推荐最佳节点配置</li>
              <li><strong>配置导入/导出：</strong>保存和加载节点配置状态</li>
              <li><strong>多视图模式：</strong>切换电路板、层级、功能、3D等不同视图</li>
              <li><strong>实时监控：</strong>底部状态栏显示系统实时状态</li>
            </ul>
          </div>
          
          <div class="help-section">
            <h4>🎨 视觉说明</h4>
            <ul>
              <li><span class="status-indicator active"></span> 绿色：节点已激活</li>
              <li><span class="status-indicator running"></span> 橙色：节点运行中</li>
              <li><span class="status-indicator recommended"></span> 金色：推荐激活</li>
              <li><span class="status-indicator error"></span> 红色：节点错误</li>
              <li><span class="status-indicator inactive"></span> 灰色：节点未激活</li>
            </ul>
          </div>
          
          <div class="help-section">
            <h4>⚡ 快捷键</h4>
            <ul>
              <li><kbd>Space</kbd> - 激活选中功能</li>
              <li><kbd>Esc</kbd> - 取消所有激活</li>
              <li><kbd>F</kbd> - 全屏模式</li>
              <li><kbd>R</kbd> - 重置视图</li>
              <li><kbd>O</kbd> - 自动优化</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 设置模态框 -->
    <div v-if="showSettingsModal" class="modal-overlay" @click="closeSettings">
      <div class="modal-content settings-modal" @click.stop>
        <div class="modal-header">
          <h3>电路板设置</h3>
          <button class="close-btn" @click="closeSettings">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="settings-section">
            <h4>🎨 视觉设置</h4>
            <div class="setting-item">
              <label>动画速度</label>
              <input 
                v-model="settings.animationSpeed" 
                type="range" 
                min="0.5" 
                max="3" 
                step="0.1"
                class="setting-slider"
              />
              <span>{{ settings.animationSpeed }}x</span>
            </div>
            <div class="setting-item">
              <label>节点大小</label>
              <input 
                v-model="settings.nodeSize" 
                type="range" 
                min="0.5" 
                max="2" 
                step="0.1"
                class="setting-slider"
              />
              <span>{{ settings.nodeSize }}x</span>
            </div>
            <div class="setting-item">
              <label>连接线粗细</label>
              <input 
                v-model="settings.connectionWidth" 
                type="range" 
                min="1" 
                max="5" 
                step="0.5"
                class="setting-slider"
              />
              <span>{{ settings.connectionWidth }}px</span>
            </div>
          </div>
          
          <div class="settings-section">
            <h4>⚡ 性能设置</h4>
            <div class="setting-item">
              <label>
                <input 
                  v-model="settings.enableAnimations" 
                  type="checkbox"
                />
                启用动画效果
              </label>
            </div>
            <div class="setting-item">
              <label>
                <input 
                  v-model="settings.enableGlowEffects" 
                  type="checkbox"
                />
                启用发光效果
              </label>
            </div>
            <div class="setting-item">
              <label>
                <input 
                  v-model="settings.enableCurrentFlow" 
                  type="checkbox"
                />
                启用电流动画
              </label>
            </div>
          </div>
          
          <div class="settings-section">
            <h4>🔊 音效设置</h4>
            <div class="setting-item">
              <label>
                <input 
                  v-model="settings.enableSoundEffects" 
                  type="checkbox"
                />
                启用音效
              </label>
            </div>
            <div class="setting-item">
              <label>音量</label>
              <input 
                v-model="settings.soundVolume" 
                type="range" 
                min="0" 
                max="100" 
                step="5"
                class="setting-slider"
              />
              <span>{{ settings.soundVolume }}%</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-primary" @click="saveSettings">保存设置</button>
          <button class="btn-secondary" @click="resetSettings">重置默认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import CircuitBoardArchitecture from '@/components/CircuitBoardArchitecture.vue'

// 响应式数据
const circuitBoard = ref<InstanceType<typeof CircuitBoardArchitecture>>()
const showHelpModal = ref(false)
const showSettingsModal = ref(false)

// 设置数据
const settings = ref({
  animationSpeed: 1,
  nodeSize: 1,
  connectionWidth: 2,
  enableAnimations: true,
  enableGlowEffects: true,
  enableCurrentFlow: true,
  enableSoundEffects: false,
  soundVolume: 50
})

// 方法
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const showHelp = () => {
  showHelpModal.value = true
}

const closeHelp = () => {
  showHelpModal.value = false
}

const openSettings = () => {
  showSettingsModal.value = true
}

const closeSettings = () => {
  showSettingsModal.value = false
}

const saveSettings = () => {
  // 保存设置到本地存储
  localStorage.setItem('circuitBoardSettings', JSON.stringify(settings.value))
  closeSettings()
}

const resetSettings = () => {
  settings.value = {
    animationSpeed: 1,
    nodeSize: 1,
    connectionWidth: 2,
    enableAnimations: true,
    enableGlowEffects: true,
    enableCurrentFlow: true,
    enableSoundEffects: false,
    soundVolume: 50
  }
}

const loadSettings = () => {
  const savedSettings = localStorage.getItem('circuitBoardSettings')
  if (savedSettings) {
    try {
      settings.value = { ...settings.value, ...JSON.parse(savedSettings) }
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  }
}

const handleKeyboardShortcuts = (event: KeyboardEvent) => {
  // 防止在输入框中触发快捷键
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
    return
  }

  switch (event.key.toLowerCase()) {
    case ' ':
      event.preventDefault()
      // 激活选中功能
      break
    case 'escape':
      // 取消所有激活
      break
    case 'f':
      event.preventDefault()
      toggleFullscreen()
      break
    case 'r':
      // 重置视图
      break
    case 'o':
      event.preventDefault()
      // 自动优化
      break
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
  document.addEventListener('keydown', handleKeyboardShortcuts)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyboardShortcuts)
})
</script>

<style scoped>
.circuit-board-view {
  width: 100%;
  height: 100vh;
  background: #0a0a0f;
  color: #e0e0e0;
  font-family: 'Courier New', monospace;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.app-header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-bottom: 2px solid #0f3460;
  padding: 15px 30px;
  box-shadow: 0 4px 20px rgba(0, 255, 136, 0.1);
  z-index: 1000;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.app-title {
  font-size: 24px;
  font-weight: bold;
  color: #00ff88;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.app-subtitle {
  font-size: 14px;
  color: #888;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.header-btn {
  background: linear-gradient(135deg, #2d3561 0%, #1f2937 100%);
  border: 1px solid #0f3460;
  color: #e0e0e0;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.header-btn:hover {
  background: linear-gradient(135deg, #3d4571 0%, #2f3947 100%);
  border-color: #00ff88;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
}

.main-content {
  flex: 1;
  position: relative;
  overflow: hidden;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 2px solid #0f3460;
  border-radius: 12px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #0f3460;
}

.modal-header h3 {
  color: #00ff88;
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: #ff4444;
}

.modal-body {
  padding: 20px;
}

.help-section {
  margin-bottom: 25px;
}

.help-section h4 {
  color: #00ff88;
  margin-bottom: 10px;
  font-size: 16px;
}

.help-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.help-section li {
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.4;
}

.help-section strong {
  color: #ffaa00;
}

.status-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: middle;
}

.status-indicator.active {
  background: #00ff88;
  box-shadow: 0 0 5px #00ff88;
}

.status-indicator.running {
  background: #ffaa00;
  box-shadow: 0 0 5px #ffaa00;
}

.status-indicator.recommended {
  background: #ffaa00;
  box-shadow: 0 0 5px #ffaa00;
}

.status-indicator.error {
  background: #ff4444;
  box-shadow: 0 0 5px #ff4444;
}

.status-indicator.inactive {
  background: #333;
}

kbd {
  background: #2d3561;
  border: 1px solid #0f3460;
  border-radius: 4px;
  padding: 2px 6px;
  font-family: monospace;
  font-size: 12px;
  color: #00ff88;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* 设置模态框样式 */
.settings-section {
  margin-bottom: 25px;
}

.settings-section h4 {
  color: #00ff88;
  margin-bottom: 15px;
  font-size: 16px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  font-size: 14px;
}

.setting-item label {
  color: #e0e0e0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #00ff88;
}

.setting-slider {
  width: 150px;
  height: 6px;
  background: #2d3561;
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
}

.setting-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  background: #00ff88;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.setting-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: #00ff88;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #0f3460;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  color: #0a0a0f;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #00cc6a 0%, #00aa55 100%);
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #2d3561 0%, #1f2937 100%);
  color: #e0e0e0;
  border: 1px solid #0f3460;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #3d4571 0%, #2f3947 100%);
  border-color: #00ff88;
}

/* 滚动条样式 */
.modal-content::-webkit-scrollbar {
  width: 8px;
}

.modal-content::-webkit-scrollbar-track {
  background: #1a1a2e;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #0f3460;
  border-radius: 4px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: #00ff88;
}

  /* 统一滑杆样式覆盖 */
  .parameter-range {
    /* 使用全局滑杆样式 */
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 6px;
    background: var(--border-color);
    border-radius: 3px;
    outline: none;
    transition: all 0.3s ease;
    border: none;
    padding: 0;
  }

  .parameter-range::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    background: var(--bg-white);
    border: 3px solid var(--primary-color);
    border-radius: 50%;
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
  }

  .parameter-range::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .parameter-range::-webkit-slider-thumb:active {
    cursor: grabbing;
    transform: scale(1.1);
  }

  .parameter-range::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: var(--bg-white);
    border: 3px solid var(--primary-color);
    border-radius: 50%;
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
    border: none;
  }

  .parameter-range::-moz-range-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .parameter-range::-moz-range-thumb:active {
    cursor: grabbing;
    transform: scale(1.1);
  }

  .parameter-range::-webkit-slider-runnable-track {
    height: 100%;
    border-radius: 3px;
  }

  .parameter-range::-moz-range-track {
    height: 100%;
    border-radius: 3px;
  }

  .range-input-group {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 0;
  }

  .range-value {
    min-width: 60px;
    padding: 4px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: var(--primary-color);
    text-align: center;
    transition: all 0.3s ease;
  }

  /* 参数配置滑杆样式增强 */
  .parameter-slider {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px;
    background: var(--bg-secondary);
    border-radius: var(--border-radius);
    transition: all 0.3s ease;
  }

  .parameter-slider:hover {
    background: var(--bg-hover);
  }

  .parameter-slider .parameter-info {
    flex: 1;
  }

  .parameter-slider .parameter-name {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .parameter-slider .parameter-desc {
    font-size: var(--font-size-xs);
    color: var(--text-regular);
  }

  .parameter-slider .parameter-control {
    flex: 2;
    display: flex;
    align-items: center;
    gap: 12px;
  }

</style>