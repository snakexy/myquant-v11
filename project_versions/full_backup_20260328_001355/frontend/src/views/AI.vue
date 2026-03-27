<template>
  <div class="ai-page">
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
          <h1 class="page-title"><i class="fas fa-robot"></i> AI助手</h1>
          <p class="page-subtitle">智能量化交易AI助手平台</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="startVoiceChat">
              <i class="fas fa-microphone"></i>
              <span>语音对话</span>
            </button>
            <button class="secondary-btn" @click="showHistory">
              <i class="fas fa-history"></i>
              <span>对话历史</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- AI统计 -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card" v-for="stat in aiStats" :key="stat.id">
            <div class="stat-icon">
              <i :class="stat.icon"></i>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
            <div class="stat-trend" :class="stat.trend">
              <i :class="getTrendIcon(stat.trend)"></i>
              <span>{{ stat.change }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- AI对话界面 -->
      <section class="chat-section">
        <div class="section-header">
          <h2><i class="fas fa-comments"></i> AI对话</h2>
          <div class="chat-controls">
            <div class="mode-selector">
              <button 
                v-for="mode in chatModes" 
                :key="mode.id"
                class="mode-btn"
                :class="{ active: currentChatMode === mode.id }"
                @click="currentChatMode = mode.id"
              >
                <i :class="mode.icon"></i>
                <span>{{ mode.name }}</span>
              </button>
            </div>
            <button class="clear-chat-btn" @click="clearChat">
              <i class="fas fa-trash"></i>
              <span>清空对话</span>
            </button>
          </div>
        </div>
        
        <div class="chat-container">
          <div class="chat-messages" ref="chatMessages">
            <div 
              v-for="message in chatMessages" 
              :key="message.id"
              class="message"
              :class="message.type"
            >
              <div class="message-avatar">
                <i :class="message.type === 'user' ? 'fas fa-user' : 'fas fa-robot'"></i>
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-sender">{{ message.sender }}</span>
                  <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                </div>
                <div class="message-text" v-html="message.content"></div>
                <div class="message-actions" v-if="message.type === 'ai'">
                  <button class="action-btn" @click="copyMessage(message)">
                    <i class="fas fa-copy"></i>
                  </button>
                  <button class="action-btn" @click="regenerateResponse(message)">
                    <i class="fas fa-redo"></i>
                  </button>
                  <button class="action-btn" @click="rateMessage(message, 'good')">
                    <i class="fas fa-thumbs-up"></i>
                  </button>
                  <button class="action-btn" @click="rateMessage(message, 'bad')">
                    <i class="fas fa-thumbs-down"></i>
                  </button>
                </div>
              </div>
            </div>
            
            <div class="typing-indicator" v-if="isTyping">
              <div class="typing-avatar">
                <i class="fas fa-robot"></i>
              </div>
              <div class="typing-content">
                <div class="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="chat-input">
            <div class="input-container">
              <textarea 
                v-model="currentMessage"
                placeholder="输入您的问题..."
                rows="3"
                @keydown.enter.prevent="sendMessage"
                @keydown.shift.enter="currentMessage += '\n'"
              ></textarea>
              <div class="input-actions">
                <button class="voice-btn" @click="toggleVoiceInput">
                  <i :class="isListening ? 'fas fa-stop' : 'fas fa-microphone'"></i>
                </button>
                <button class="send-btn" @click="sendMessage" :disabled="!currentMessage.trim()">
                  <i class="fas fa-paper-plane"></i>
                </button>
              </div>
            </div>
            <div class="quick-actions">
              <button 
                v-for="action in quickActions" 
                :key="action.id"
                class="quick-action-btn"
                @click="useQuickAction(action)"
              >
                {{ action.text }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- AI功能模块 -->
      <section class="ai-modules-section">
        <div class="section-header">
          <h2>AI功能模块</h2>
          <p>选择AI功能模块，获取专业服务</p>
        </div>
        
        <div class="modules-grid">
          <div 
            v-for="module in aiModules" 
            :key="module.id"
            class="module-card"
            @click="openModule(module)"
          >
            <div class="module-icon">
              <i :class="module.icon"></i>
            </div>
            <div class="module-content">
              <h3>{{ module.name }}</h3>
              <p>{{ module.description }}</p>
              <div class="module-features">
                <span 
                  v-for="feature in module.features" 
                  :key="feature"
                  class="feature-tag"
                >
                  {{ feature }}
                </span>
              </div>
            </div>
            <div class="module-status" :class="module.status">
              <span class="status-dot"></span>
              <span class="status-text">{{ getModuleStatusText(module.status) }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 策略生成器 -->
      <section class="strategy-generator-section">
        <div class="section-header">
          <h2>AI策略生成器</h2>
          <p>使用AI快速生成量化交易策略</p>
        </div>
        
        <div class="generator-container">
          <div class="generator-input">
            <div class="input-group">
              <label>策略类型</label>
              <select v-model="strategyType">
                <option value="trend">趋势跟踪</option>
                <option value="mean-reversion">均值回归</option>
                <option value="momentum">动量策略</option>
                <option value="arbitrage">套利策略</option>
                <option value="custom">自定义</option>
              </select>
            </div>
            
            <div class="input-group">
              <label>市场类型</label>
              <select v-model="marketType">
                <option value="stock">股票</option>
                <option value="futures">期货</option>
                <option value="crypto">加密货币</option>
                <option value="forex">外汇</option>
              </select>
            </div>
            
            <div class="input-group">
              <label>风险偏好</label>
              <div class="risk-slider">
                <input 
                  type="range" 
                  min="1" 
                  max="5" 
                  v-model="riskLevel"
                  class="slider"
                >
                <div class="risk-labels">
                  <span>保守</span>
                  <span>稳健</span>
                  <span>平衡</span>
                  <span>积极</span>
                  <span>激进</span>
                </div>
              </div>
            </div>
            
            <div class="input-group">
              <label>策略描述</label>
              <textarea 
                v-model="strategyDescription"
                placeholder="描述您想要的策略特征..."
                rows="4"
              ></textarea>
            </div>
            
            <button 
              class="generate-btn" 
              @click="generateStrategy"
              :disabled="isGenerating || !strategyDescription"
            >
              <i class="fas fa-magic" v-if="!isGenerating"></i>
              <i class="fas fa-spinner fa-spin" v-if="isGenerating"></i>
              <span>{{ isGenerating ? '生成中...' : '生成策略' }}</span>
            </button>
          </div>
          
          <div class="generator-output">
            <div class="generated-strategy" v-if="generatedStrategy">
              <h3>生成的策略</h3>
              <div class="strategy-preview">
                <div class="preview-header">
                  <h4>{{ generatedStrategy.name }}</h4>
                  <div class="preview-score">
                    <span class="score-label">AI评分</span>
                    <span class="score-value">{{ generatedStrategy.aiScore }}</span>
                  </div>
                </div>
                
                <div class="preview-content">
                  <p>{{ generatedStrategy.description }}</p>
                  
                  <div class="preview-params">
                    <h5>策略参数</h5>
                    <div class="params-list">
                      <div 
                        v-for="param in generatedStrategy.parameters" 
                        :key="param.name"
                        class="param-item"
                      >
                        <span class="param-name">{{ param.name }}:</span>
                        <span class="param-value">{{ param.value }}</span>
                        <span class="param-desc">{{ param.description }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="preview-actions">
                    <button class="accept-btn" @click="acceptGeneratedStrategy">
                      <i class="fas fa-check"></i>
                      <span>采纳策略</span>
                    </button>
                    <button class="regenerate-btn" @click="regenerateStrategy">
                      <i class="fas fa-redo"></i>
                      <span>重新生成</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const currentChatMode = ref('general')
const currentMessage = ref('')
const isTyping = ref(false)
const isListening = ref(false)
const isGenerating = ref(false)
const strategyType = ref('trend')
const marketType = ref('stock')
const riskLevel = ref(3)
const strategyDescription = ref('')
const generatedStrategy = ref(null)

// AI统计
const aiStats = ref([
  {
    id: 1,
    icon: 'fas fa-comments',
    label: '今日对话',
    value: '156',
    change: '+23',
    trend: 'up'
  },
  {
    id: 2,
    icon: 'fas fa-lightbulb',
    label: '策略生成',
    value: '42',
    change: '+8',
    trend: 'up'
  },
  {
    id: 3,
    icon: 'fas fa-chart-line',
    label: '分析报告',
    value: '28',
    change: '+5',
    trend: 'up'
  },
  {
    id: 4,
    icon: 'fas fa-clock',
    label: '响应时间',
    value: '1.2s',
    change: '-0.3s',
    trend: 'down'
  }
])

// 对话模式
const chatModes = ref([
  { id: 'general', name: '通用对话', icon: 'fas fa-comments' },
  { id: 'strategy', name: '策略咨询', icon: 'fas fa-chart-line' },
  { id: 'analysis', name: '市场分析', icon: 'fas fa-chart-bar' },
  { id: 'technical', name: '技术问答', icon: 'fas fa-cog' }
])

// 对话消息
const chatMessages = ref([
  {
    id: 1,
    type: 'ai',
    sender: 'AI助手',
    content: '您好！我是您的量化交易AI助手。我可以帮助您：<br>• 生成交易策略<br>• 分析市场数据<br>• 回测策略<br>• 技术指标解释<br>请告诉我您需要什么帮助？',
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  }
])

// 快捷操作
const quickActions = ref([
  { id: 1, text: '生成趋势跟踪策略' },
  { id: 2, text: '分析当前市场行情' },
  { id: 3, text: '解释MACD指标' },
  { id: 4, text: '优化现有策略' }
])

// AI功能模块
const aiModules = ref([
  {
    id: 1,
    name: '策略生成器',
    description: '使用AI快速生成量化交易策略',
    icon: 'fas fa-magic',
    features: ['自动生成', '参数优化', '风险评估'],
    status: 'active'
  },
  {
    id: 2,
    name: '市场分析',
    description: 'AI驱动的市场分析和预测',
    icon: 'fas fa-chart-bar',
    features: ['趋势分析', '情绪分析', '价格预测'],
    status: 'active'
  },
  {
    id: 3,
    name: '回测优化',
    description: '智能回测参数优化',
    icon: 'fas fa-cogs',
    features: ['参数调优', '性能分析', '风险评估'],
    status: 'active'
  },
  {
    id: 4,
    name: '风险管理',
    description: 'AI风险监控和预警',
    icon: 'fas fa-shield-alt',
    features: ['风险识别', '实时监控', '预警系统'],
    status: 'testing'
  }
])

// 方法
const getTrendIcon = (trend: string) => {
  const iconMap = {
    up: 'fas fa-arrow-up',
    down: 'fas fa-arrow-down',
    stable: 'fas fa-minus'
  }
  return iconMap[trend] || 'fas fa-minus'
}

const getModuleStatusText = (status: string) => {
  const statusMap = {
    active: '运行中',
    testing: '测试中',
    inactive: '已停止'
  }
  return statusMap[status] || status
}

const formatTime = (timestamp: Date) => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

const startVoiceChat = () => {
  console.log('开始语音对话')
  isListening.value = true
}

const showHistory = () => {
  console.log('显示对话历史')
}

const clearChat = () => {
  chatMessages.value = []
}

const sendMessage = async () => {
  if (!currentMessage.value.trim()) return
  
  const userMessage = {
    id: Date.now(),
    type: 'user',
    sender: '用户',
    content: currentMessage.value,
    timestamp: new Date()
  }
  
  chatMessages.value.push(userMessage)
  
  const messageText = currentMessage.value
  currentMessage.value = ''
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 显示AI正在输入
  isTyping.value = true
  
  // 模拟AI响应
  setTimeout(() => {
    const aiResponse = generateAIResponse(messageText)
    const aiMessage = {
      id: Date.now(),
      type: 'ai',
      sender: 'AI助手',
      content: aiResponse,
      timestamp: new Date()
    }
    
    chatMessages.value.push(aiMessage)
    isTyping.value = false
    
    // 滚动到底部
    nextTick(() => {
      scrollToBottom()
    })
  }, 2000)
}

const generateAIResponse = (message: string) => {
  // 简单的AI响应生成逻辑
  if (message.includes('策略')) {
    return '我可以帮您生成量化交易策略。请告诉我：<br>• 您偏好的策略类型（趋势、均值回归等）<br>• 目标市场（股票、期货等）<br>• 风险偏好<br>• 其他特殊要求'
  } else if (message.includes('分析')) {
    return '我可以为您提供市场分析服务，包括：<br>• 技术指标分析<br>• 市场趋势判断<br>• 情绪分析<br>• 价格预测<br>请告诉我您想分析的具体内容。'
  } else if (message.includes('回测')) {
    return '回测分析可以帮助您评估策略效果。我可以协助：<br>• 回测参数设置<br>• 性能指标分析<br>• 风险评估<br>• 策略优化建议<br>请提供您的策略或回测需求。'
  } else {
    return '我理解您的问题。作为量化交易AI助手，我可以帮助您：<br>• 生成和优化交易策略<br>• 分析市场数据和趋势<br>• 提供技术指标解释<br>• 进行回测分析<br>• 风险管理和预警<br><br>请告诉我您的具体需求，我会为您提供专业建议。'
  }
}

const scrollToBottom = () => {
  const chatMessages = document.querySelector('.chat-messages')
  if (chatMessages) {
    chatMessages.scrollTop = chatMessages.scrollHeight
  }
}

const toggleVoiceInput = () => {
  isListening.value = !isListening.value
  if (isListening.value) {
    // 开始语音识别
    console.log('开始语音识别')
  } else {
    // 停止语音识别
    console.log('停止语音识别')
  }
}

const useQuickAction = (action: any) => {
  currentMessage.value = action.text
  sendMessage()
}

const copyMessage = (message: any) => {
  navigator.clipboard.writeText(message.content.replace(/<[^>]*>/g, ''))
  console.log('消息已复制')
}

const regenerateResponse = (message: any) => {
  // 重新生成响应
  console.log('重新生成响应', message)
}

const rateMessage = (message: any, rating: string) => {
  console.log('评价消息', message, rating)
}

const openModule = (module: any) => {
  console.log('打开模块', module)
  router.push(`/function/ai-assistant/${module.id}`)
}

const generateStrategy = async () => {
  isGenerating.value = true
  
  // 模拟AI生成策略
  setTimeout(() => {
    generatedStrategy.value = {
      name: 'AI生成策略_' + Date.now(),
      description: '基于您的需求，AI生成了一个结合趋势跟踪和风险控制的量化策略',
      aiScore: 8.5,
      parameters: [
        { name: '短期均线', value: 'MA5', description: '短期趋势指标' },
        { name: '长期均线', value: 'MA20', description: '长期趋势指标' },
        { name: 'RSI周期', value: '14', description: '超买超卖指标' },
        { name: '止损比例', value: '2%', description: '风险控制参数' }
      ]
    }
    isGenerating.value = false
  }, 3000)
}

const acceptGeneratedStrategy = () => {
  if (generatedStrategy.value) {
    console.log('采纳策略', generatedStrategy.value)
    // 跳转到策略页面
    router.push('/function/strategy-center/dashboard')
  }
}

const regenerateStrategy = () => {
  generateStrategy()
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
      ctx.fillStyle = `rgba(16, 185, 129, ${particle.opacity})`
      ctx.fill()
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 生命周期
onMounted(() => {
  initParticleSystem()
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.ai-page {
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
      rgba(16, 185, 129, 0.03) 50%, 
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
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
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
}

// 统计区域
.stats-section {
  margin-bottom: 60px;
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    
    .stat-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 24px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      
      .stat-icon {
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        color: var(--market-rise);
        font-size: 20px;
      }
      
      .stat-content {
        flex: 1;
        
        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 14px;
          color: var(--text-secondary);
        }
      }
      
      .stat-trend {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        
        &.up {
          background: rgba(16, 185, 129, 0.1);
          color: var(--market-rise);
        }
        
        &.down {
          background: rgba(239, 68, 68, 0.1);
          color: var(--market-fall);
        }
        
        &.stable {
          background: rgba(245, 158, 11, 0.1);
          color: #f59e0b;
        }
      }
    }
  }
}

// 对话区域
.chat-section {
  margin-bottom: 60px;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32px;
    
    h2 {
      margin: 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    .chat-controls {
      display: flex;
      align-items: center;
      gap: 24px;
      
      .mode-selector {
        display: flex;
        gap: 8px;
        
        .mode-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover, &.active {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            border-color: var(--market-rise);
          }
        }
      }
      
      .clear-chat-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 12px;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 6px;
        color: var(--market-fall);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(239, 68, 68, 0.2);
          border-color: rgba(239, 68, 68, 0.5);
        }
      }
    }
  }
  
  .chat-container {
    background: rgba(26, 26, 46, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    height: 600px;
    display: flex;
    flex-direction: column;
    
    .chat-messages {
      flex: 1;
      overflow-y: auto;
      margin-bottom: 20px;
      padding-right: 8px;
      
      .message {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
        
        &.user {
          flex-direction: row-reverse;
          
          .message-avatar {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
          }
          
          .message-content {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
          }
        }
        
        &.ai {
          .message-avatar {
            background: rgba(16, 185, 129, 0.2);
            color: var(--market-rise);
          }
          
          .message-content {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
          }
        }
        
        .message-avatar {
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          font-size: 16px;
          flex-shrink: 0;
        }
        
        .message-content {
          flex: 1;
          padding: 12px 16px;
          border-radius: 12px;
          
          .message-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
            
            .message-sender {
              font-size: 12px;
              font-weight: 600;
              color: var(--text-primary);
            }
            
            .message-time {
              font-size: 10px;
              color: var(--text-secondary);
            }
          }
          
          .message-text {
            font-size: 14px;
            line-height: 1.5;
            color: var(--text-primary);
            margin-bottom: 8px;
          }
          
          .message-actions {
            display: flex;
            gap: 8px;
            
            .action-btn {
              width: 24px;
              height: 24px;
              background: rgba(255, 255, 255, 0.05);
              border: 1px solid rgba(255, 255, 255, 0.1);
              border-radius: 4px;
              color: var(--text-secondary);
              cursor: pointer;
              transition: all 0.3s ease;
              
              &:hover {
                background: rgba(255, 255, 255, 0.1);
                color: var(--text-primary);
              }
            }
          }
        }
      }
      
      .typing-indicator {
        display: flex;
        gap: 12px;
        
        .typing-avatar {
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(16, 185, 129, 0.2);
          color: var(--market-rise);
          border-radius: 50%;
          font-size: 16px;
          flex-shrink: 0;
        }
        
        .typing-content {
          padding: 12px 16px;
          background: rgba(16, 185, 129, 0.1);
          border: 1px solid rgba(16, 185, 129, 0.3);
          border-radius: 12px;
          
          .typing-dots {
            display: flex;
            gap: 4px;
            
            span {
              width: 8px;
              height: 8px;
              background: var(--market-rise);
              border-radius: 50%;
              animation: typing 1.4s infinite;
              
              &:nth-child(2) {
                animation-delay: 0.2s;
              }
              
              &:nth-child(3) {
                animation-delay: 0.4s;
              }
            }
          }
        }
      }
    }
    
    .chat-input {
      .input-container {
        display: flex;
        gap: 12px;
        margin-bottom: 12px;
        
        textarea {
          flex: 1;
          padding: 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          color: var(--text-primary);
          font-size: 14px;
          resize: none;
          outline: none;
          
          &:focus {
            border-color: var(--market-rise);
          }
        }
        
        .input-actions {
          display: flex;
          gap: 8px;
          
          .voice-btn, .send-btn {
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
          }
          
          .voice-btn {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
            
            &:hover {
              background: rgba(255, 255, 255, 0.1);
              color: var(--text-primary);
            }
          }
          
          .send-btn {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            
            &:hover:not(:disabled) {
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            }
            
            &:disabled {
              opacity: 0.5;
              cursor: not-allowed;
            }
          }
        }
      }
      
      .quick-actions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        
        .quick-action-btn {
          padding: 6px 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 16px;
          color: var(--text-secondary);
          font-size: 12px;
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            border-color: rgba(255, 255, 255, 0.2);
          }
        }
      }
    }
  }
}

// AI功能模块区域
.ai-modules-section {
  margin-bottom: 60px;
  
  .section-header {
    text-align: center;
    margin-bottom: 40px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 36px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 18px;
    }
  }
  
  .modules-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    
    .module-card {
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      padding: 24px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-8px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
      }
      
      .module-icon {
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(16, 185, 129, 0.1);
        border-radius: 12px;
        color: var(--market-rise);
        font-size: 24px;
        margin-bottom: 16px;
      }
      
      .module-content {
        flex: 1;
        
        h3 {
          margin: 0 0 8px 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        p {
          margin: 0 0 16px 0;
          color: var(--text-secondary);
          font-size: 14px;
          line-height: 1.5;
        }
        
        .module-features {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          
          .feature-tag {
            padding: 4px 8px;
            background: rgba(16, 185, 129, 0.1);
            color: var(--market-rise);
            border-radius: 4px;
            font-size: 12px;
          }
        }
      }
      
      .module-status {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        
        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          
          &.active {
            background: var(--market-rise);
            animation: pulse 2s infinite;
          }
          
          &.testing {
            background: #f59e0b;
          }
          
          &.inactive {
            background: #6b7280;
          }
        }
        
        .status-text {
          font-size: 12px;
          color: var(--text-secondary);
        }
      }
    }
  }
}

// 策略生成器区域
.strategy-generator-section {
  .section-header {
    text-align: center;
    margin-bottom: 40px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 36px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 18px;
    }
  }
  
  .generator-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    background: rgba(26, 26, 46, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 32px;
    
    .generator-input {
      .input-group {
        margin-bottom: 24px;
        
        label {
          display: block;
          margin-bottom: 8px;
          color: var(--text-primary);
          font-size: 14px;
          font-weight: 500;
        }
        
        select, textarea {
          width: 100%;
          padding: 12px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: var(--text-primary);
          font-size: 14px;
          
          &:focus {
            outline: none;
            border-color: var(--market-rise);
          }
        }
        
        textarea {
          resize: vertical;
          min-height: 100px;
        }
        
        .risk-slider {
          .slider {
            width: 100%;
            margin-bottom: 8px;
          }
          
          .risk-labels {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-secondary);
          }
        }
      }
      
      .generate-btn {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 16px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
        }
        
        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
    }
    
    .generator-output {
      .generated-strategy {
        .strategy-preview {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          padding: 20px;
          
          h3 {
            margin: 0 0 16px 0;
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
          }
          
          .preview-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            
            h4 {
              margin: 0;
              font-size: 16px;
              font-weight: 600;
              color: var(--text-primary);
            }
            
            .preview-score {
              text-align: center;
              
              .score-label {
                display: block;
                font-size: 12px;
                color: var(--text-secondary);
                margin-bottom: 4px;
              }
              
              .score-value {
                font-size: 20px;
                font-weight: 700;
                color: var(--market-rise);
              }
            }
          }
          
          .preview-content {
            p {
              margin: 0 0 16px 0;
              color: var(--text-secondary);
              font-size: 14px;
              line-height: 1.5;
            }
            
            .preview-params {
              margin-bottom: 20px;
              
              h5 {
                margin: 0 0 12px 0;
                font-size: 14px;
                font-weight: 600;
                color: var(--text-primary);
              }
              
              .params-list {
                .param-item {
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  margin-bottom: 8px;
                  padding: 8px;
                  background: rgba(255, 255, 255, 0.02);
                  border-radius: 4px;
                  
                  .param-name {
                    font-size: 12px;
                    color: var(--text-secondary);
                    min-width: 80px;
                  }
                  
                  .param-value {
                    font-size: 12px;
                    color: var(--market-rise);
                    font-weight: 500;
                    min-width: 60px;
                  }
                  
                  .param-desc {
                    font-size: 12px;
                    color: var(--text-secondary);
                    flex: 1;
                  }
                }
              }
            }
            
            .preview-actions {
              display: flex;
              gap: 12px;
              
              .accept-btn, .regenerate-btn {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                border: none;
              }
              
              .accept-btn {
                background: rgba(16, 185, 129, 0.2);
                color: var(--market-rise);
                
                &:hover {
                  background: rgba(16, 185, 129, 0.3);
                }
              }
              
              .regenerate-btn {
                background: rgba(255, 255, 255, 0.05);
                color: var(--text-primary);
                border: 1px solid rgba(255, 255, 255, 0.1);
                
                &:hover {
                  background: rgba(255, 255, 255, 0.1);
                }
              }
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

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .generator-container {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .modules-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    .chat-controls {
      flex-direction: column;
      gap: 12px;
      align-items: flex-start;
    }
  }
  
  .chat-container {
    height: 500px;
  }
  
  .modules-grid {
    grid-template-columns: 1fr;
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