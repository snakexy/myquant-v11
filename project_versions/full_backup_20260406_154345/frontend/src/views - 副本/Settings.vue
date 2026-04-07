<template>
  <div class="settings-page">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-system" ref="particleSystem"></div>
      <div class="data-stream-overlay"></div>
      <div class="grid-pattern"></div>
    </div>

    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">系统设置</h1>
          <p class="page-subtitle">个性化配置与系统管理</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="saveAllSettings">
              <i class="fas fa-save"></i>
              <span>保存设置</span>
            </button>
            <button class="secondary-btn" @click="resetSettings">
              <i class="fas fa-undo"></i>
              <span>重置默认</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 设置导航 -->
      <section class="settings-nav">
        <div class="nav-tabs">
          <button 
            v-for="tab in settingsTabs" 
            :key="tab.id"
            class="nav-tab"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <i :class="tab.icon"></i>
            <span>{{ tab.name }}</span>
          </button>
        </div>
      </section>

      <!-- 设置内容 -->
      <section class="settings-content">
        <!-- 通用设置 -->
        <div v-if="activeTab === 'general'" class="settings-panel">
          <h2>通用设置</h2>
          
          <div class="settings-group">
            <h3>界面设置</h3>
            
            <div class="setting-item">
              <label>主题模式</label>
              <div class="setting-control">
                <select v-model="settings.general.theme">
                  <option value="dark">暗黑模式</option>
                  <option value="light">明亮模式</option>
                  <option value="auto">跟随系统</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <label>语言设置</label>
              <div class="setting-control">
                <select v-model="settings.general.language">
                  <option value="zh">简体中文</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <label>动画效果</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.general.animations">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>粒子效果</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.general.particles">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
          
          <div class="settings-group">
            <h3>布局设置</h3>
            
            <div class="setting-item">
              <label>默认布局</label>
              <div class="setting-control">
                <select v-model="settings.general.defaultLayout">
                  <option value="grid">网格布局</option>
                  <option value="list">列表布局</option>
                  <option value="cards">卡片布局</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <label>侧边栏位置</label>
              <div class="setting-control">
                <select v-model="settings.general.sidebarPosition">
                  <option value="left">左侧</option>
                  <option value="right">右侧</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <label>紧凑模式</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.general.compactMode">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据设置 -->
        <div v-if="activeTab === 'data'" class="settings-panel">
          <h2>数据设置</h2>
          
          <div class="settings-group">
            <h3>数据源配置</h3>
            
            <div class="setting-item">
              <label>主要数据源</label>
              <div class="setting-control">
                <select v-model="settings.data.primarySource">
                  <option value="tushare">Tushare</option>
                  <option value="akshare">AKShare</option>
                  <option value="wind">Wind</option>
                  <option value="custom">自定义</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <label>备用数据源</label>
              <div class="setting-control">
                <select v-model="settings.data.backupSource">
                  <option value="none">无</option>
                  <option value="tushare">Tushare</option>
                  <option value="akshare">AKShare</option>
                  <option value="wind">Wind</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <label>数据更新频率</label>
              <div class="setting-control">
                <select v-model="settings.data.updateFrequency">
                  <option value="realtime">实时</option>
                  <option value="1min">1分钟</option>
                  <option value="5min">5分钟</option>
                  <option value="15min">15分钟</option>
                  <option value="1hour">1小时</option>
                </select>
              </div>
            </div>
          </div>
          
          <div class="settings-group">
            <h3>缓存设置</h3>
            
            <div class="setting-item">
              <label>启用缓存</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.data.enableCache">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>缓存大小</label>
              <div class="setting-control">
                <input 
                  type="number" 
                  v-model="settings.data.cacheSize"
                  min="100"
                  max="10000"
                  step="100"
                >
                <span class="unit">MB</span>
              </div>
            </div>
            
            <div class="setting-item">
              <label>缓存过期时间</label>
              <div class="setting-control">
                <select v-model="settings.data.cacheExpiry">
                  <option value="1hour">1小时</option>
                  <option value="6hour">6小时</option>
                  <option value="1day">1天</option>
                  <option value="1week">1周</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- 策略设置 -->
        <div v-if="activeTab === 'strategy'" class="settings-panel">
          <h2>策略设置</h2>
          
          <div class="settings-group">
            <h3>默认参数</h3>
            
            <div class="setting-item">
              <label>初始资金</label>
              <div class="setting-control">
                <input 
                  type="number" 
                  v-model="settings.strategy.initialCapital"
                  min="10000"
                  step="10000"
                >
                <span class="unit">元</span>
              </div>
            </div>
            
            <div class="setting-item">
              <label>默认止损比例</label>
              <div class="setting-control">
                <input 
                  type="number" 
                  v-model="settings.strategy.defaultStopLoss"
                  min="0.1"
                  max="50"
                  step="0.1"
                >
                <span class="unit">%</span>
              </div>
            </div>
            
            <div class="setting-item">
              <label>默认止盈比例</label>
              <div class="setting-control">
                <input 
                  type="number" 
                  v-model="settings.strategy.defaultTakeProfit"
                  min="0.1"
                  max="100"
                  step="0.1"
                >
                <span class="unit">%</span>
              </div>
            </div>
            
            <div class="setting-item">
              <label>最大持仓数量</label>
              <div class="setting-control">
                <input 
                  type="number" 
                  v-model="settings.strategy.maxPositions"
                  min="1"
                  max="50"
                  step="1"
                >
                <span class="unit">只</span>
              </div>
            </div>
          </div>
          
          <div class="settings-group">
            <h3>回测设置</h3>
            
            <div class="setting-item">
              <label>默认回测周期</label>
              <div class="setting-control">
                <select v-model="settings.strategy.defaultBacktestPeriod">
                  <option value="1month">1个月</option>
                  <option value="3months">3个月</option>
                  <option value="6months">6个月</option>
                  <option value="1year">1年</option>
                  <option value="2years">2年</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <label>基准指数</label>
              <div class="setting-control">
                <select v-model="settings.strategy.benchmark">
                  <option value="000300">沪深300</option>
                  <option value="000905">中证500</option>
                  <option value="000016">上证50</option>
                  <option value="399001">深证成指</option>
                </select>
              </div>
            </div>
            
            <div class="setting-item">
              <label>手续费率</label>
              <div class="setting-control">
                <input 
                  type="number" 
                  v-model="settings.strategy.commissionRate"
                  min="0.0001"
                  max="0.01"
                  step="0.0001"
                >
                <span class="unit">%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 通知设置 -->
        <div v-if="activeTab === 'notifications'" class="settings-panel">
          <h2>通知设置</h2>
          
          <div class="settings-group">
            <h3>系统通知</h3>
            
            <div class="setting-item">
              <label>启用系统通知</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.notifications.enableSystem">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>策略执行通知</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.notifications.strategyExecution">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>风险预警通知</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.notifications.riskAlerts">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>数据异常通知</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.notifications.dataAnomalies">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
          
          <div class="settings-group">
            <h3>通知方式</h3>
            
            <div class="setting-item">
              <label>浏览器通知</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.notifications.browser">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>邮件通知</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.notifications.email">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>短信通知</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.notifications.sms">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>微信通知</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.notifications.wechat">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- 安全设置 -->
        <div v-if="activeTab === 'security'" class="settings-panel">
          <h2>安全设置</h2>
          
          <div class="settings-group">
            <h3>账户安全</h3>
            
            <div class="setting-item">
              <label>双因素认证</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.security.twoFactorAuth">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>登录提醒</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.security.loginAlerts">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>自动锁定时间</label>
              <div class="setting-control">
                <select v-model="settings.security.autoLockTime">
                  <option value="5">5分钟</option>
                  <option value="10">10分钟</option>
                  <option value="30">30分钟</option>
                  <option value="60">1小时</option>
                  <option value="never">从不</option>
                </select>
              </div>
            </div>
          </div>
          
          <div class="settings-group">
            <h3>数据安全</h3>
            
            <div class="setting-item">
              <label>数据加密</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.security.dataEncryption">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>访问日志</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.security.accessLogs">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>IP白名单</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.security.ipWhitelist">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- 高级设置 -->
        <div v-if="activeTab === 'advanced'" class="settings-panel">
          <h2>高级设置</h2>
          
          <div class="settings-group">
            <h3>性能设置</h3>
            
            <div class="setting-item">
              <label>GPU加速</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.advanced.gpuAcceleration">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>多线程处理</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.advanced.multiThreading">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>内存限制</label>
              <div class="setting-control">
                <input 
                  type="number" 
                  v-model="settings.advanced.memoryLimit"
                  min="512"
                  max="16384"
                  step="512"
                >
                <span class="unit">MB</span>
              </div>
            </div>
          </div>
          
          <div class="settings-group">
            <h3>开发者选项</h3>
            
            <div class="setting-item">
              <label>调试模式</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.advanced.debugMode">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>开发者工具</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.advanced.devTools">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="setting-item">
              <label>实验性功能</label>
              <div class="setting-control">
                <label class="switch">
                  <input type="checkbox" v-model="settings.advanced.experimentalFeatures">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 响应式数据
const activeTab = ref('general')

// 设置标签页
const settingsTabs = ref([
  { id: 'general', name: '通用', icon: 'fas fa-cog' },
  { id: 'data', name: '数据', icon: 'fas fa-database' },
  { id: 'strategy', name: '策略', icon: 'fas fa-chart-line' },
  { id: 'notifications', name: '通知', icon: 'fas fa-bell' },
  { id: 'security', name: '安全', icon: 'fas fa-shield-alt' },
  { id: 'advanced', name: '高级', icon: 'fas fa-sliders-h' }
])

// 设置数据
const settings = ref({
  general: {
    theme: 'dark',
    language: 'zh',
    animations: true,
    particles: true,
    defaultLayout: 'grid',
    sidebarPosition: 'left',
    compactMode: false
  },
  data: {
    primarySource: 'tushare',
    backupSource: 'akshare',
    updateFrequency: 'realtime',
    enableCache: true,
    cacheSize: 1000,
    cacheExpiry: '1day'
  },
  strategy: {
    initialCapital: 1000000,
    defaultStopLoss: 5.0,
    defaultTakeProfit: 10.0,
    maxPositions: 10,
    defaultBacktestPeriod: '1year',
    benchmark: '000300',
    commissionRate: 0.0003
  },
  notifications: {
    enableSystem: true,
    strategyExecution: true,
    riskAlerts: true,
    dataAnomalies: true,
    browser: true,
    email: false,
    sms: false,
    wechat: false
  },
  security: {
    twoFactorAuth: false,
    loginAlerts: true,
    autoLockTime: '30',
    dataEncryption: true,
    accessLogs: true,
    ipWhitelist: false
  },
  advanced: {
    gpuAcceleration: false,
    multiThreading: true,
    memoryLimit: 4096,
    debugMode: false,
    devTools: false,
    experimentalFeatures: false
  }
})

// 方法
const saveAllSettings = () => {
  // 保存设置到本地存储
  localStorage.setItem('quant-ui-settings', JSON.stringify(settings.value))
  console.log('设置已保存')
}

const resetSettings = () => {
  // 重置为默认设置
  const defaultSettings = {
    general: {
      theme: 'dark',
      language: 'zh',
      animations: true,
      particles: true,
      defaultLayout: 'grid',
      sidebarPosition: 'left',
      compactMode: false
    },
    data: {
      primarySource: 'tushare',
      backupSource: 'akshare',
      updateFrequency: 'realtime',
      enableCache: true,
      cacheSize: 1000,
      cacheExpiry: '1day'
    },
    strategy: {
      initialCapital: 1000000,
      defaultStopLoss: 5.0,
      defaultTakeProfit: 10.0,
      maxPositions: 10,
      defaultBacktestPeriod: '1year',
      benchmark: '000300',
      commissionRate: 0.0003
    },
    notifications: {
      enableSystem: true,
      strategyExecution: true,
      riskAlerts: true,
      dataAnomalies: true,
      browser: true,
      email: false,
      sms: false,
      wechat: false
    },
    security: {
      twoFactorAuth: false,
      loginAlerts: true,
      autoLockTime: '30',
      dataEncryption: true,
      accessLogs: true,
      ipWhitelist: false
    },
    advanced: {
      gpuAcceleration: false,
      multiThreading: true,
      memoryLimit: 4096,
      debugMode: false,
      devTools: false,
      experimentalFeatures: false
    }
  }
  
  settings.value = defaultSettings
  console.log('设置已重置为默认值')
}

// 初始化粒子系统
const initParticleSystem = () => {
  const particleSystem = document.querySelector('.particle-system')
  if (!particleSystem) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  canvas.style.position = 'absolute'
  canvas.style.top = '0'
  canvas.style.left = '0'
  canvas.style.pointerEvents = 'none'
  
  particleSystem.appendChild(canvas)
  
  // 简单的粒子动画
  const particles: any[] = []
  for (let i = 0; i < 25; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.2
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach(particle => {
      particle.x += particle.vx
      particle.y += particle.vy
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx = -particle.vx
      if (particle.y < 0 || particle.y > canvas.height) particle.vy = -particle.vy
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(107, 114, 128, ${particle.opacity})`
      ctx.fill()
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 生命周期
onMounted(() => {
  // 从本地存储加载设置
  const savedSettings = localStorage.getItem('quant-ui-settings')
  if (savedSettings) {
    try {
      const parsed = JSON.parse(savedSettings)
      settings.value = { ...settings.value, ...parsed }
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  }
  
  // 初始化粒子系统
  if (settings.value.general.particles) {
    initParticleSystem()
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.settings-page {
  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family-primary);
  overflow-x: hidden;
}

// 沉浸式背景
.immersive-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  
  .particle-system {
    position: absolute;
    width: 100%;
    height: 100%;
  }
  
  .data-stream-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, 
      transparent 30%, 
      rgba(107, 114, 128, 0.03) 50%, 
      transparent 70%);
    animation: dataFlow 8s linear infinite;
  }
  
  .grid-pattern {
    position: absolute;
    width: 100%;
    height: 100%;
    background-image: 
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
  }
}

// 页面头部
.page-header {
  position: relative;
  z-index: 10;
  padding: 24px 40px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .header-left {
    .page-title {
      margin: 0 0 8px 0;
      font-size: 32px;
      font-weight: 700;
      background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .page-subtitle {
      margin: 0;
      color: var(--text-secondary);
      font-size: 16px;
    }
  }
  
  .header-right {
    .action-buttons {
      display: flex;
      gap: 16px;
      
      .primary-btn, .secondary-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
      }
      
      .primary-btn {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        color: white;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(107, 114, 128, 0.3);
        }
      }
      
      .secondary-btn {
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-primary);
        border: 1px solid rgba(255, 255, 255, 0.1);
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
      }
    }
  }
}

// 主内容区域
.main-content {
  position: relative;
  z-index: 5;
  padding: 40px;
  display: flex;
  gap: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

// 设置导航
.settings-nav {
  width: 240px;
  flex-shrink: 0;
  
  .nav-tabs {
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .nav-tab {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 16px 20px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover, &.active {
        background: rgba(107, 114, 128, 0.1);
        color: var(--text-primary);
        border-color: rgba(107, 114, 128, 0.3);
        transform: translateX(4px);
      }
      
      i {
        width: 20px;
        text-align: center;
      }
      
      span {
        font-size: 14px;
        font-weight: 500;
      }
    }
  }
}

// 设置内容
.settings-content {
  flex: 1;
  
  .settings-panel {
    background: rgba(26, 26, 46, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 32px;
    
    h2 {
      margin: 0 0 32px 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    .settings-group {
      margin-bottom: 40px;
      
      h3 {
        margin: 0 0 24px 0;
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      }
      
      .setting-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        
        label {
          font-size: 14px;
          color: var(--text-primary);
          font-weight: 500;
        }
        
        .setting-control {
          display: flex;
          align-items: center;
          gap: 8px;
          
          select, input[type="number"] {
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 14px;
            outline: none;
            
            &:focus {
              border-color: #6b7280;
            }
          }
          
          select {
            min-width: 120px;
          }
          
          input[type="number"] {
            width: 100px;
          }
          
          .unit {
            font-size: 12px;
            color: var(--text-secondary);
          }
          
          // 开关样式
          .switch {
            position: relative;
            display: inline-block;
            width: 48px;
            height: 24px;
            
            input {
              opacity: 0;
              width: 0;
              height: 0;
            }
            
            .slider {
              position: absolute;
              cursor: pointer;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              background-color: rgba(255, 255, 255, 0.1);
              transition: .4s;
              border-radius: 24px;
              
              &:before {
                position: absolute;
                content: "";
                height: 18px;
                width: 18px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
              }
            }
            
            input:checked + .slider {
              background-color: #6b7280;
            }
            
            input:checked + .slider:before {
              transform: translateX(24px);
            }
          }
        }
      }
    }
  }
}

// 动画
@keyframes dataFlow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
    gap: 24px;
  }
  
  .settings-nav {
    width: 100%;
    
    .nav-tabs {
      flex-direction: row;
      flex-wrap: wrap;
      
      .nav-tab {
        flex: 1;
        min-width: 120px;
        justify-content: center;
        
        &:hover, &.active {
          transform: translateY(-2px);
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 20px;
    
    .header-content {
      flex-direction: column;
      gap: 16px;
      text-align: center;
    }
  }
  
  .main-content {
    padding: 20px;
  }
  
  .settings-panel {
    padding: 20px;
    
    h2 {
      font-size: 24px;
      margin-bottom: 24px;
    }
    
    .settings-group {
      margin-bottom: 32px;
      
      h3 {
        font-size: 16px;
        margin-bottom: 16px;
      }
      
      .setting-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
        
        .setting-control {
          width: 100%;
          justify-content: space-between;
          
          select, input[type="number"] {
            flex: 1;
          }
        }
      }
    }
  }
  
  .nav-tabs {
    .nav-tab {
      padding: 12px 16px;
      
      span {
        font-size: 12px;
      }
    }
  }
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