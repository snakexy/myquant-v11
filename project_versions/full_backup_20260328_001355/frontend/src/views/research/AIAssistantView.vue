<template>
  <div class="ai-assistant-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="phase-badge research">🔬 研究阶段</div>
          <h1 class="page-title"><i class="fas fa-lightbulb"></i> AI助手策略构思</h1>
          <p class="page-subtitle">自然语言交互 → 策略代码生成 → 参数优化建议</p>
        </div>
      </div>
    </div>

    <!-- AI对话区域 -->
    <div class="chat-container">
      <div class="chat-messages" ref="chatMessagesRef">
        <div
          v-for="(message, index) in chatHistory"
          :key="index"
          :class="['message-item', message.role]"
        >
          <div class="message-avatar">
            <el-icon v-if="message.role === 'user'"><User /></el-icon>
            <el-icon v-else><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="message.content"></div>
            <div class="message-time">{{ message.time }}</div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="aiThinking" class="message-item assistant">
          <div class="message-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            <div class="thinking-animation">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-container">
        <el-input
          v-model="userInput"
          type="textarea"
          :rows="3"
          placeholder="输入您的策略想法，AI助手将帮您生成策略代码..."
          @keydown.enter.ctrl="sendMessage"
          :disabled="aiThinking"
        ></el-input>
        <div class="input-actions">
          <div class="quick-prompts">
            <el-tag
              v-for="prompt in quickPrompts"
              :key="prompt"
              @click="useQuickPrompt(prompt)"
              class="quick-prompt-tag"
            >
              {{ prompt }}
            </el-tag>
          </div>
          <el-button
            type="primary"
            @click="sendMessage"
            :loading="aiThinking"
            :disabled="!userInput.trim()"
          >
            <el-icon><Promotion /></el-icon>
            发送 (Ctrl+Enter)
          </el-button>
        </div>
      </div>
    </div>

    <!-- 侧边栏：策略模板和历史 -->
    <div class="sidebar">
      <el-tabs v-model="sidebarTab">
        <el-tab-pane label="策略模板" name="templates">
          <div class="templates-list">
            <div
              v-for="template in strategyTemplates"
              :key="template.id"
              class="template-item"
              @click="useTemplate(template)"
            >
              <div class="template-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="template-info">
                <h4>{{ template.name }}</h4>
                <p>{{ template.description }}</p>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="生成历史" name="history">
          <div class="history-list">
            <div
              v-for="item in generationHistory"
              :key="item.id"
              class="history-item"
            >
              <div class="history-time">{{ item.time }}</div>
              <div class="history-content">{{ item.prompt }}</div>
              <el-button size="small" @click="viewHistory(item)">查看</el-button>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="策略参数" name="parameters">
          <div class="parameters-panel">
            <h4>当前策略参数</h4>
            <div v-if="currentStrategy" class="strategy-params">
              <div v-for="(value, key) in currentStrategy.parameters" :key="key" class="param-item">
                <span class="param-label">{{ key }}</span>
                <span class="param-value">{{ value }}</span>
              </div>
            </div>
            <div v-else class="no-params">
              <el-empty description="暂无策略参数" :image-size="80"></el-empty>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 策略预览对话框 -->
    <el-dialog v-model="showStrategyPreview" title="生成的策略代码" width="900px">
      <div class="strategy-preview">
        <el-tabs v-model="previewTab">
          <el-tab-pane label="策略代码" name="code">
            <pre class="code-block"><code>{{ generatedCode }}</code></pre>
            <div class="code-actions">
              <el-button @click="copyCode">
                <el-icon><DocumentCopy /></el-icon>
                复制代码
              </el-button>
              <el-button type="primary" @click="saveStrategy">
                <el-icon><FolderOpened /></el-icon>
                保存策略
              </el-button>
              <el-button @click="backtestStrategy">
                <el-icon><TrendCharts /></el-icon>
                去回测
              </el-button>
            </div>
          </el-tab-pane>

          <el-tab-pane label="策略说明" name="description">
            <div class="strategy-description">
              <h3>策略概述</h3>
              <p>{{ strategyDescription.overview }}</p>

              <h3>策略逻辑</h3>
              <p>{{ strategyDescription.logic }}</p>

              <h3>适用场景</h3>
              <ul>
                <li v-for="scene in strategyDescription.scenarios" :key="scene">{{ scene }}</li>
              </ul>

              <h3>风险提示</h3>
              <p class="risk-warning">{{ strategyDescription.risk }}</p>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { User, ChatDotRound, Promotion, Document, DocumentCopy, FolderOpened, TrendCharts } from '@element-plus/icons-vue'
import axios from 'axios'

// API基础URL
const API_BASE = '/api/v1/research/ai'

// 状态定义
const userInput = ref('')
const aiThinking = ref(false)
const showStrategyPreview = ref(false)
const sidebarTab = ref('templates')
const previewTab = ref('code')
const chatMessagesRef = ref<HTMLElement>()

// 聊天历史
const chatHistory = ref([
  {
    role: 'assistant',
    content: '您好！我是AI策略助手。我可以帮您：<br>1. 根据您的想法生成策略代码<br>2. 优化策略参数<br>3. 解释策略逻辑<br><br>请告诉我您想实现什么样的交易策略？',
    time: '刚刚'
  }
])

// 快捷提示词
const quickPrompts = ref([
  '基于MACD的策略',
  '双均线策略',
  '布林带突破策略',
  'RSI超卖反弹',
  '成交量突破'
])

// 策略模板
const strategyTemplates = ref([
  {
    id: 1,
    name: '动量策略',
    description: '基于价格动量的趋势跟踪策略',
    prompt: '生成一个基于20日均线的动量策略，当价格突破MA20时买入，跌破时卖出'
  },
  {
    id: 2,
    name: '均值回归策略',
    description: '价格偏离均值时的回归策略',
    prompt: '生成一个布林带均值回归策略，当价格触及上轨时卖出，触及下轨时买入'
  },
  {
    id: 3,
    name: '波动率策略',
    description: '基于波动率变化的策略',
    prompt: '生成一个基于ATR波动率的策略，高波动时减仓，低波动时加仓'
  }
])

// 生成历史
const generationHistory = ref([
  {
    id: 1,
    time: '2026-02-04 00:30',
    prompt: '双均线策略',
    code: '...'
  }
])

// 当前策略
const currentStrategy = ref<any>(null)

// 生成的代码
const generatedCode = ref('')

// 策略说明
const strategyDescription = ref({
  overview: '',
  logic: '',
  scenarios: [] as string[],
  risk: ''
})

// 组件挂载时加载历史记录和健康检查
onMounted(async () => {
  // 健康检查
  try {
    const healthRes = await axios.get(`${API_BASE}/health`)
    if (healthRes.data.code === 200) {
      ElMessage.success('AI助手服务已连接')
    }
  } catch (error) {
    console.warn('AI助手健康检查失败:', error)
  }

  // 加载历史记录
  await loadHistory()
})

// 从后端加载历史记录
const loadHistory = async () => {
  try {
    const response = await axios.get(`${API_BASE}/history`, {
      params: { page: 1, page_size: 20 }
    })
    if (response.data.code === 200) {
      generationHistory.value = response.data.data.items.map((item: any) => ({
        id: item.id,
        time: new Date(item.created_at).toLocaleString(),
        prompt: item.prompt,
        code: item.generated_code || ''
      }))
    }
  } catch (error) {
    console.warn('加载历史记录失败:', error)
  }
}

// 方法
const sendMessage = async () => {
  if (!userInput.value.trim() || aiThinking.value) return

  // 添加用户消息
  const userMessage = {
    role: 'user',
    content: userInput.value,
    time: new Date().toLocaleTimeString()
  }
  chatHistory.value.push(userMessage)

  const prompt = userInput.value
  userInput.value = ''

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // AI思考中
  aiThinking.value = true

  try {
    // 调用AI助手API
    const response = await axios.post(`${API_BASE}/generate`, {
      prompt: prompt
    })

    if (response.data.code === 200 && response.data.data.success) {
      const aiMessage = {
        role: 'assistant',
        content: response.data.data.reply,
        time: new Date().toLocaleTimeString()
      }
      chatHistory.value.push(aiMessage)

      // 如果生成了代码
      if (response.data.data.code) {
        generatedCode.value = response.data.data.code
        strategyDescription.value = response.data.data.description || {}
        currentStrategy.value = response.data.data.strategy

        showStrategyPreview.value = true
      }

      // 添加到历史记录
      generationHistory.value.unshift({
        id: Date.now(),
        time: new Date().toLocaleString(),
        prompt: prompt,
        code: response.data.data.code || ''
      })
    } else {
      ElMessage.error(response.data.message || 'AI助手暂时不可用')
    }
  } catch (error) {
    console.error('AI助手调用失败:', error)
    ElMessage.error('网络错误，请稍后重试')

    // 添加错误消息
    const errorMessage = {
      role: 'assistant',
      content: '抱歉，我遇到了一些技术问题。请稍后再试。',
      time: new Date().toLocaleTimeString()
    }
    chatHistory.value.push(errorMessage)
  } finally {
    aiThinking.value = false
    await nextTick()
    scrollToBottom()
  }
}

const useQuickPrompt = (prompt: string) => {
  userInput.value = prompt
}

const useTemplate = (template: any) => {
  userInput.value = template.prompt
}

const viewHistory = (item: any) => {
  generatedCode.value = item.code
  showStrategyPreview.value = true
}

const copyCode = () => {
  navigator.clipboard.writeText(generatedCode.value)
  ElMessage.success('代码已复制到剪贴板')
}

const saveStrategy = async () => {
  if (!generatedCode.value) {
    ElMessage.warning('没有可保存的策略')
    return
  }

  try {
    const response = await axios.post(`${API_BASE}/save`, {
      factor_name: `AI策略_${new Date().toLocaleDateString()}`,
      expression: currentStrategy.value?.name || 'AI生成策略',
      description: strategyDescription.value.overview || 'AI生成的量化策略',
      code: generatedCode.value,
      source: 'ai_generated'
    })

    if (response.data.code === 200) {
      ElMessage.success('策略保存成功')
      showStrategyPreview.value = false
      // 刷新历史记录
      await loadHistory()
    } else {
      ElMessage.error(response.data.message || '保存失败')
    }
  } catch (error: any) {
    console.error('保存策略失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败，请稍后重试')
  }
}

const backtestStrategy = () => {
  ElMessage.info('跳转到回测页面...')
  // TODO: 实现跳转到回测页面
}

const scrollToBottom = () => {
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}
</script>

<style scoped lang="scss">
.ai-assistant-view {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

.page-header {
  flex-shrink: 0;
  padding: 20px;
  background: white;
  border-bottom: 1px solid #ecf0f1;

  .header-content {
    .header-left {
      .phase-badge {
        display: inline-block;
        padding: 4px 12px;
        background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 10px;
      }

      .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #2c3e50;
        margin: 0 0 8px 0;
      }

      .page-subtitle {
        font-size: 14px;
        color: #7f8c8d;
        margin: 0;
      }
    }
  }
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;

  .message-item {
    display: flex;
    margin-bottom: 20px;
    gap: 12px;

    &.user {
      flex-direction: row-reverse;

      .message-avatar {
        background: #2962ff;
        color: white;
      }

      .message-content {
        background: #2962ff;
        color: white;
      }
    }

    &.assistant {
      .message-avatar {
        background: linear-gradient(135deg, #764ba2 0%, #2962ff 100%);
        color: white;
      }

      .message-content {
        background: white;
        color: #2c3e50;
      }
    }

    .message-avatar {
      flex-shrink: 0;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .message-content {
      max-width: 70%;
      padding: 12px 16px;
      border-radius: 12px;

      .message-text {
        font-size: 14px;
        line-height: 1.6;
        white-space: pre-wrap;
      }

      .message-time {
        font-size: 11px;
        margin-top: 6px;
        opacity: 0.7;
      }
    }

    .thinking-animation {
      display: flex;
      gap: 4px;

      .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #bdc3c7;
        animation: thinking 1.4s infinite;

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

@keyframes thinking {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

.chat-input-container {
  flex-shrink: 0;
  padding: 20px;
  background: white;
  border-top: 1px solid #ecf0f1;

  .input-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;

    .quick-prompts {
      display: flex;
      gap: 8px;
      flex: 1;

      .quick-prompt-tag {
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background: #2962ff;
          color: white;
        }
      }
    }
  }
}

.sidebar {
  flex-shrink: 0;
  width: 320px;
  background: white;
  border-left: 1px solid #ecf0f1;
  display: flex;
  flex-direction: column;

  .templates-list,
  .history-list {
    padding: 15px;
    max-height: calc(100vh - 200px);
    overflow-y: auto;
  }

  .template-item {
    display: flex;
    gap: 12px;
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid #ecf0f1;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      border-color: #2962ff;
      background: #f0f4ff;
    }

    .template-icon {
      font-size: 24px;
      color: #2962ff;
    }

    .template-info {
      flex: 1;

      h4 {
        font-size: 14px;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 4px 0;
      }

      p {
        font-size: 12px;
        color: #7f8c8d;
        margin: 0;
      }
    }
  }

  .history-item {
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid #ecf0f1;
    border-radius: 8px;

    .history-time {
      font-size: 11px;
      color: #95a5a6;
      margin-bottom: 6px;
    }

    .history-content {
      font-size: 13px;
      color: #2c3e50;
      margin-bottom: 8px;
    }

    .el-button {
      width: 100%;
    }
  }

  .parameters-panel {
    padding: 15px;

    h4 {
      font-size: 14px;
      font-weight: 600;
      color: #2c3e50;
      margin: 0 0 15px 0;
    }

    .strategy-params {
      .param-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #ecf0f1;

        .param-label {
          font-size: 13px;
          color: #7f8c8d;
        }

        .param-value {
          font-size: 13px;
          color: #2c3e50;
          font-weight: 600;
        }
      }
    }

    .no-params {
      text-align: center;
      padding: 40px 0;
    }
  }
}

.strategy-preview {
  .code-block {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    overflow-x: auto;
    margin-bottom: 20px;

    code {
      font-family: 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.6;
      color: #2c3e50;
    }
  }

  .code-actions {
    display: flex;
    gap: 10px;
  }

  .strategy-description {
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: #2c3e50;
      margin: 20px 0 10px 0;
    }

    p {
      font-size: 14px;
      color: #5a6c7d;
      line-height: 1.6;
      margin: 0 0 15px 0;
    }

    ul {
      margin: 0 0 15px 0;
      padding-left: 20px;

      li {
        font-size: 14px;
        color: #5a6c7d;
        margin-bottom: 6px;
      }
    }

    .risk-warning {
      padding: 12px;
      background: #ffebee;
      color: #c62828;
      border-radius: 6px;
      margin: 0;
    }
  }
}
</style>
