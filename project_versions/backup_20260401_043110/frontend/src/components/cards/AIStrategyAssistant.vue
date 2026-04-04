<template>
  <div class="ai-strategy-assistant-card">
    <!-- 卡片头部 -->
    <div class="card-header">
      <div class="card-title">
        <span class="card-icon">🤖</span>
        <span>AI策略助手</span>
      </div>
      <div class="card-actions">
        <n-button
          quaternary
          circle
          size="small"
          @click="toggleVoiceAssistant"
          :class="{ 'voice-active': isVoiceActive }"
        >
          <template #icon>
            <n-icon :component="MicOutline" />
          </template>
        </n-button>
        <n-button quaternary circle size="small" @click="refreshStrategies">
          <template #icon>
            <n-icon :component="RefreshOutline" />
          </template>
        </n-button>
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-content">
      <!-- AI聊天界面 -->
      <div class="chat-container" ref="chatContainer">
        <div class="chat-messages" ref="messagesContainer">
          <div
            v-for="message in messages"
            :key="message.id"
            class="message"
            :class="{ 'user-message': message.role === 'user', 'ai-message': message.role === 'assistant' }"
          >
            <div class="message-avatar">
              <n-avatar
                v-if="message.role === 'user'"
                round
                size="small"
                :fallback-src="userAvatar"
              >
                <n-icon :component="PersonOutline" />
              </n-avatar>
              <n-avatar
                v-else
                round
                size="small"
                :style="{ backgroundColor: '#7c3aed' }"
              >
                <n-icon :component="SparklesOutline" />
              </n-avatar>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(message.content)"></div>
              <div v-if="message.marketData" class="market-data">
                <h4>市场数据</h4>
                <div class="market-overview">
                  <div class="market-item">
                    <span class="label">市场情绪:</span>
                    <n-tag :type="getMarketSentimentType(message.marketData.sentiment)">
                      {{ message.marketData.sentiment }}
                    </n-tag>
                  </div>
                  <div class="market-item">
                    <span class="label">热门板块:</span>
                    <n-tag type="info">{{ message.marketData.hotSector }}</n-tag>
                  </div>
                  <div class="market-item">
                    <span class="label">风险等级:</span>
                    <n-tag :type="getRiskLevelType(message.marketData.riskLevel)">
                      {{ message.marketData.riskLevel }}
                    </n-tag>
                  </div>
                </div>
              </div>
              <div v-if="message.optimizedIndicators" class="optimized-indicators">
                <h4>优化结果</h4>
                <div class="indicators-table">
                  <div class="table-header">
                    <div class="header-cell">指标</div>
                    <div class="header-cell">原始参数</div>
                    <div class="header-cell">优化参数</div>
                  </div>
                  <div
                    v-for="indicator in message.optimizedIndicators"
                    :key="indicator.name"
                    class="table-row"
                  >
                    <div class="table-cell">{{ indicator.name }}</div>
                    <div class="table-cell">
                      周期: {{ indicator.original.period }}, 阈值: {{ indicator.original.threshold }}
                    </div>
                    <div class="table-cell">
                      周期: {{ indicator.optimized.period }}, 阈值: {{ indicator.optimized.threshold }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input">
          <n-input
            v-model:value="inputMessage"
            placeholder="输入您的策略需求，如：帮我写一个均线策略..."
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            @keydown.enter.prevent="handleSendMessage"
            :loading="isGenerating"
          >
            <template #suffix>
              <n-button
                quaternary
                circle
                size="small"
                @click="handleSendMessage"
                :disabled="!inputMessage.trim() || isGenerating"
                :loading="isGenerating"
              >
                <template #icon>
                  <n-icon :component="SendOutline" />
                </template>
              </n-button>
            </template>
          </n-input>
        </div>
      </div>

      <!-- 快捷功能按钮 -->
      <div class="quick-actions">
        <n-button-group size="small">
          <n-button @click="generateStrategy('trend')">
            <template #icon>
              <n-icon :component="TrendingUpOutline" />
            </template>
            趋势策略
          </n-button>
          <n-button @click="generateStrategy('mean_reversion')">
            <template #icon>
              <n-icon :component="SwapHorizontalOutline" />
            </template>
            均值回归
          </n-button>
          <n-button @click="generateStrategy('momentum')">
            <template #icon>
              <n-icon :component="FlashOutline" />
            </template>
            动量策略
          </n-button>
          <n-button @click="analyzeMarket()">
            <template #icon>
              <n-icon :component="AnalyticsOutline" />
            </template>
            市场分析
          </n-button>
          <n-button @click="optimizeIndicators()">
            <template #icon>
              <n-icon :component="BuildOutline" />
            </template>
            指标优化
          </n-button>
        </n-button-group>
      </div>

      <!-- 最近生成的策略 -->
      <div class="recent-strategies" v-if="recentStrategies.length > 0">
        <div class="section-title">最近生成的策略</div>
        <div class="strategy-list">
          <div
            v-for="strategy in recentStrategies.slice(0, 3)"
            :key="strategy.id"
            class="strategy-item"
            @click="viewStrategy(strategy)"
          >
            <div class="strategy-info">
              <div class="strategy-name">{{ strategy.name }}</div>
              <div class="strategy-desc">{{ strategy.description }}</div>
            </div>
            <div class="strategy-actions">
              <n-button quaternary circle size="tiny" @click.stop="backtestStrategy(strategy)">
                <template #icon>
                  <n-icon :component="PlayOutline" />
                </template>
              </n-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 语音识别指示器 -->
    <div class="voice-indicator" v-if="isVoiceActive">
      <div class="voice-pulse"></div>
      <span>正在听取您的指令...</span>
    </div>

    <!-- 策略详情弹窗 -->
    <n-modal v-model:show="showStrategyModal" preset="card" style="max-width: 600px;" title="策略详情">
      <div v-if="selectedStrategy" class="strategy-detail">
        <div class="detail-section">
          <h4>策略名称</h4>
          <p>{{ selectedStrategy.name }}</p>
        </div>
        <div class="detail-section">
          <h4>策略描述</h4>
          <p>{{ selectedStrategy.description }}</p>
        </div>
        <div class="detail-section">
          <h4>策略代码</h4>
          <n-code :code="selectedStrategy.code" language="python" show-line-numbers />
        </div>
        <div class="detail-section">
          <h4>参数配置</h4>
          <n-descriptions :column="2" size="small">
            <n-descriptions-item
              v-for="(value, key) in selectedStrategy.parameters"
              :key="key"
              :label="key"
            >
              {{ value }}
            </n-descriptions-item>
          </n-descriptions>
        </div>
      </div>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showStrategyModal = false">关闭</n-button>
          <n-button type="primary" @click="backtestStrategy(selectedStrategy)">运行回测</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { useStrategyStore } from '@/stores'
import { aiApi } from '@/api'
import {
  MicOutline,
  RefreshOutline,
  PersonOutline,
  SparklesOutline,
  SendOutline,
  TrendingUpOutline,
  SwapHorizontalOutline,
  FlashOutline,
  AnalyticsOutline,
  PlayOutline,
  BuildOutline
} from '@vicons/ionicons5'

// 组件属性定义
interface Props {
  size?: 'small' | 'medium' | 'large'
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  height: 400
})

// 路由和状态管理
const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const strategyStore = useStrategyStore()

// 响应式数据
const inputMessage = ref('')
const isGenerating = ref(false)
const isVoiceActive = ref(false)
const showStrategyModal = ref(false)
const selectedStrategy = ref<any>(null)
const userAvatar = ref('/default-avatar.png')
const isAnalyzing = ref(false)
const isOptimizing = ref(false)
const selectedIndicators = ref<string[]>(['MACD', 'RSI', 'KDJ'])

// 聊天消息
interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  marketData?: any
  optimizedIndicators?: any[]
}

const messages = ref<ChatMessage[]>([
  {
    id: '1',
    role: 'assistant',
    content: '您好！我是您的AI策略助手。我可以帮您：<br/>• 生成量化交易策略<br/>• 分析回测结果<br/>• 提供市场建议<br/>• 解答技术问题<br/><br/>请问有什么可以帮助您的吗？',
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  }
])

// 最近生成的策略
interface GeneratedStrategy {
  id: string
  name: string
  description: string
  code: string
  parameters: Record<string, any>
  createdAt: Date
}

const recentStrategies = ref<GeneratedStrategy[]>([
  {
    id: '1',
    name: '双均线交叉策略',
    description: '基于5日和20日均线的交叉信号进行买卖',
    code: '# 双均线交叉策略\ndef initialize(context):\n    context.short_window = 5\n    context.long_window = 20\n\ndef handle_data(context, data):\n    short_ma = data.history(context.short_window, \'close\').mean()\n    long_ma = data.history(context.long_window, \'close\').mean()\n    \n    if short_ma > long_ma and context.portfolio.positions[context.asset].amount == 0:\n        order_target_percent(context.asset, 1.0)\n    elif short_ma < long_ma and context.portfolio.positions[context.asset].amount > 0:\n        order_target_percent(context.asset, 0.0)',
    parameters: {
      '短期窗口': 5,
      '长期窗口': 20,
      '初始资金': '100000',
      '基准指数': '000300.SH'
    },
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000)
  },
  {
    id: '2',
    name: 'RSI均值回归策略',
    description: '利用RSI指标识别超买超卖机会',
    code: '# RSI均值回归策略\nimport talib\n\ndef initialize(context):\n    context.rsi_period = 14\n    context.rsi_oversold = 30\n    context.rsi_overbought = 70\n\ndef handle_data(context, data):\n    prices = data.history(context.rsi_period + 1, \'close\')\n    rsi = talib.RSI(prices.values, timeperiod=context.rsi_period)[-1]\n    \n    if rsi < context.rsi_oversold and context.portfolio.positions[context.asset].amount == 0:\n        order_target_percent(context.asset, 1.0)\n    elif rsi > context.rsi_overbought and context.portfolio.positions[context.asset].amount > 0:\n        order_target_percent(context.asset, 0.0)',
    parameters: {
      'RSI周期': 14,
      '超卖阈值': 30,
      '超买阈值': 70,
      '初始资金': '100000'
    },
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000)
  }
])

// DOM引用
const chatContainer = ref<HTMLElement | null>(null)
const messagesContainer = ref<HTMLElement | null>(null)

// 计算属性
const cardHeight = computed(() => {
  switch (props.size) {
    case 'small':
      return '300px'
    case 'medium':
      return '400px'
    case 'large':
      return '500px'
    default:
      return '400px'
  }
})

// 方法
const handleSendMessage = async () => {
  if (!inputMessage.value.trim() || isGenerating.value) return

  const userMessage: ChatMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage.value,
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const userInput = inputMessage.value
  inputMessage.value = ''
  isGenerating.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 调用AI API
    const response = await aiApi.chat({
      message: userInput,
      context: 'strategy_generation'
    })

    const aiMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: response.response,
      timestamp: new Date()
    }

    messages.value.push(aiMessage)

    // 如果AI返回了策略代码，解析并保存
    if (response.strategy) {
      const strategy: GeneratedStrategy = {
        id: response.strategy.id || Date.now().toString(),
        name: response.strategy.name || 'AI生成策略',
        description: response.strategy.description || '',
        code: response.strategy.code || '',
        parameters: response.strategy.parameters || {},
        createdAt: new Date()
      }
      recentStrategies.value.unshift(strategy)
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    message.error('发送消息失败，请重试')
    
    const errorMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '抱歉，我遇到了一些问题。请稍后再试或重新表述您的问题。',
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
  } finally {
    isGenerating.value = false
    await nextTick()
    scrollToBottom()
  }
}

const generateStrategy = async (type: string) => {
  const prompts = {
    trend: '请生成一个基于趋势跟踪的量化交易策略，使用移动平均线作为主要指标',
    mean_reversion: '请生成一个均值回归策略，利用价格偏离移动平均线的程度进行交易',
    momentum: '请生成一个动量策略，基于价格动量和技术指标识别强势股票'
  }

  inputMessage.value = prompts[type] || prompts.trend
  await handleSendMessage()
}

const analyzeMarket = async () => {
  if (isAnalyzing.value) return
  
  isAnalyzing.value = true
  
  try {
    if (props.onAnalyzeMarket) {
      const result = await props.onAnalyzeMarket()
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.content,
        timestamp: new Date(),
        marketData: result.marketData
      }
      messages.value.push(aiMessage)
    } else {
      // 模拟市场分析
      inputMessage.value = '请分析当前市场状况，并给出投资建议'
      await handleSendMessage()
    }
  } catch (error) {
    console.error('市场分析失败:', error)
    message.error('市场分析失败，请重试')
  } finally {
    isAnalyzing.value = false
  }
}

const optimizeIndicators = async () => {
  if (isOptimizing.value) return
  
  isOptimizing.value = true
  
  try {
    if (props.onOptimizeIndicators) {
      const result = await props.onOptimizeIndicators(selectedIndicators.value)
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.content,
        timestamp: new Date(),
        optimizedIndicators: result.optimizedIndicators
      }
      messages.value.push(aiMessage)
    } else {
      // 模拟指标优化
      inputMessage.value = `请优化以下技术指标组合: ${selectedIndicators.value.join(', ')}`
      await handleSendMessage()
    }
  } catch (error) {
    console.error('指标优化失败:', error)
    message.error('指标优化失败，请重试')
  } finally {
    isOptimizing.value = false
  }
}

const toggleVoiceAssistant = () => {
  isVoiceActive.value = !isVoiceActive.value
  
  if (isVoiceActive.value) {
    // 启动语音识别
    startVoiceRecognition()
  } else {
    // 停止语音识别
    stopVoiceRecognition()
  }
}

const startVoiceRecognition = () => {
  // 检查浏览器是否支持语音识别
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    message.warning('您的浏览器不支持语音识别功能')
    isVoiceActive.value = false
    return
  }

  try {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    
    recognition.lang = 'zh-CN'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      inputMessage.value = transcript
      isVoiceActive.value = false
      handleSendMessage()
    }

    recognition.onerror = () => {
      message.error('语音识别失败，请重试')
      isVoiceActive.value = false
    }

    recognition.onend = () => {
      isVoiceActive.value = false
    }

    recognition.start()
  } catch (error) {
    console.error('启动语音识别失败:', error)
    message.error('启动语音识别失败')
    isVoiceActive.value = false
  }
}

const stopVoiceRecognition = () => {
  // 语音识别会自动停止
}

const refreshStrategies = () => {
  // 刷新最近策略列表
  message.success('策略列表已刷新')
}

const viewStrategy = (strategy: GeneratedStrategy) => {
  selectedStrategy.value = strategy
  showStrategyModal.value = true
}

const backtestStrategy = (strategy: GeneratedStrategy) => {
  // 设置当前策略并跳转到回测页面
  strategyStore.setCurrentStrategy({
    id: strategy.id,
    name: strategy.name,
    description: strategy.description,
    code: strategy.code,
    parameters: strategy.parameters
  })
  
  showStrategyModal.value = false
  router.push('/backtest')
}

const formatMessage = (content: string) => {
  // 简单的markdown格式化
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const formatTime = (timestamp: Date) => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  
  if (diff < 60 * 1000) {
    return '刚刚'
  } else if (diff < 60 * 60 * 1000) {
    return `${Math.floor(diff / (60 * 1000))}分钟前`
  } else if (diff < 24 * 60 * 60 * 1000) {
    return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  } else {
    return timestamp.toLocaleDateString()
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 生命周期
onMounted(() => {
  scrollToBottom()
})
</script>

<style lang="scss" scoped>
.ai-strategy-assistant-card {
  @include card-style;
  height: v-bind(cardHeight);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;

  .card-header {
    @include card-header;
    flex-shrink: 0;

    .card-title {
      display: flex;
      align-items: center;
      gap: var(--spacing-2);

      .card-icon {
        font-size: var(--font-size-lg);
      }
    }

    .card-actions {
      display: flex;
      gap: var(--spacing-1);

      .voice-active {
        color: var(--primary-color);
        animation: pulse 1.5s infinite;
      }
    }
  }

  .card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: var(--spacing-4);
    gap: var(--spacing-4);

    .chat-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      border: 1px solid var(--border-color);
      border-radius: var(--border-radius-medium);
      background: rgba(0, 0, 0, 0.2);

      .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: var(--spacing-3);

        .message {
          display: flex;
          margin-bottom: var(--spacing-3);
          gap: var(--spacing-2);

          &.user-message {
            flex-direction: row-reverse;

            .message-content {
              background: var(--primary-color);
              color: white;
              border-radius: var(--border-radius-medium) var(--border-radius-medium) var(--border-radius-medium) $border-radius-large;
            }

            .message-time {
              text-align: right;
            }
          }

          &.ai-message {
            .message-content {
              background: rgba(255, 255, 255, 0.1);
              border-radius: var(--border-radius-medium) var(--border-radius-medium) $border-radius-large var(--border-radius-medium);
            }
          }

          .message-avatar {
            flex-shrink: 0;
          }

          .message-content {
            max-width: 70%;
            padding: var(--spacing-2) var(--spacing-3);

            .message-text {
              font-size: var(--font-size-sm);
              line-height: 1.5;
              margin-bottom: var(--spacing-1);
            }

            .message-time {
              font-size: var(--font-size-xs);
              opacity: 0.7;
            }
            
            .market-data {
              margin-top: var(--spacing-2);
              padding: var(--spacing-2);
              background: rgba(0, 0, 0, 0.1);
              border-radius: var(--border-radius-sm)all;
              
              h4 {
                margin-bottom: var(--spacing-2);
                color: var(--text-primary);
              }
              
              .market-overview {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: var(--spacing-2);
                
                .market-item {
                  display: flex;
                  flex-direction: column;
                  gap: var(--spacing-1);
                  
                  .label {
                    font-size: var(--font-size-xs);
                    color: var(--text-secondary);
                  }
                }
              }
            }
            
            .optimized-indicators {
              margin-top: var(--spacing-2);
              padding: var(--spacing-2);
              background: rgba(0, 0, 0, 0.1);
              border-radius: var(--border-radius-sm)all;
              
              h4 {
                margin-bottom: var(--spacing-2);
                color: var(--text-primary);
              }
              
              .indicators-table {
                .table-header {
                  display: grid;
                  grid-template-columns: repeat(3, 1fr);
                  gap: var(--spacing-1);
                  padding-bottom: var(--spacing-1);
                  border-bottom: 1px solid var(--border-color);
                  margin-bottom: var(--spacing-1);
                  
                  .header-cell {
                    font-size: var(--font-size-xs);
                    font-weight: 600;
                    color: var(--text-secondary);
                  }
                }
                
                .table-row {
                  display: grid;
                  grid-template-columns: repeat(3, 1fr);
                  gap: var(--spacing-1);
                  padding: var(--spacing-1) 0;
                  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                  
                  &:last-child {
                    border-bottom: none;
                  }
                  
                  .table-cell {
                    font-size: var(--font-size-xs);
                    color: var(--text-secondary);
                    line-height: 1.4;
                  }
                }
              }
            }
          }
        }
      }

      .chat-input {
        padding: var(--spacing-3);
        border-top: 1px solid var(--border-color);
      }
    }

    .quick-actions {
      flex-shrink: 0;
    }

    .recent-strategies {
      flex-shrink: 0;

      .section-title {
        font-size: var(--font-size-sm);
        font-weight: 600;
        margin-bottom: var(--spacing-2);
        color: var(--text-secondary);
      }

      .strategy-list {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-2);

        .strategy-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: var(--spacing-2);
          background: rgba(255, 255, 255, 0.05);
          border-radius: var(--border-radius-sm)all;
          cursor: pointer;
          transition: all 0.2s ease;

          &:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(4px);
          }

          .strategy-info {
            flex: 1;
            min-width: 0;

            .strategy-name {
              font-size: var(--font-size-sm);
              font-weight: 600;
              margin-bottom: var(--spacing-1);
              @include text-ellipsis;
            }

            .strategy-desc {
              font-size: var(--font-size-xs);
              color: var(--text-secondary);
              @include text-ellipsis;
            }
          }

          .strategy-actions {
            flex-shrink: 0;
          }
        }
      }
    }
  }

  .voice-indicator {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-3);
    padding: var(--spacing-6);
    background: rgba(0, 0, 0, 0.9);
    border-radius: $border-radius-large;
    backdrop-filter: blur(10px);
    z-index: 10;

    .voice-pulse {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: var(--primary-color);
      animation: voicePulse 1.5s infinite;
    }

    span {
      font-size: var(--font-size-sm);
      color: var(--text-primary);
    }
  }

  .strategy-detail {
    .detail-section {
      margin-bottom: var(--spacing-4);

      h4 {
        margin-bottom: var(--spacing-2);
        color: var(--text-primary);
      }

      p {
        color: var(--text-secondary);
        line-height: 1.6;
      }
    }
  }
}

// 动画
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--primary-color), 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(var(--primary-color), 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(var(--primary-color), 0);
  }
}

@keyframes voicePulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>