<template>
  <div class="voice-assistant">
    <!-- 语音助手触发按钮 -->
    <div class="voice-trigger" @click="toggleVoiceAssistant">
      <div class="voice-button" :class="{ 'active': isListening, 'processing': isProcessing }">
        <n-icon size="24" :component="isListening ? StopOutline : MicOutline" />
      </div>
      <div class="voice-pulse" v-if="isListening"></div>
      <span class="voice-hint">{{ isListening ? '正在听取...' : '点击说话' }}</span>
    </div>

    <!-- 语音识别结果弹窗 -->
    <n-modal v-model:show="showVoiceModal" preset="card" style="max-width: 500px;" title="语音助手">
      <div class="voice-content">
        <!-- 识别状态指示器 -->
        <div class="voice-status">
          <div class="status-indicator" :class="getStatusClass()">
            <n-icon size="32" :component="getStatusIcon()" />
          </div>
          <div class="status-text">{{ getStatusText() }}</div>
        </div>

        <!-- 识别结果 -->
        <div class="voice-result" v-if="transcript || processedResult">
          <div class="transcript-section" v-if="transcript">
            <div class="section-title">识别内容</div>
            <div class="transcript-text">{{ transcript }}</div>
          </div>
          
          <div class="result-section" v-if="processedResult">
            <div class="section-title">处理结果</div>
            <div class="result-text" v-html="processedResult"></div>
          </div>
        </div>

        <!-- 音频波形 -->
        <div class="audio-waveform" v-if="isListening">
          <canvas ref="waveformCanvas" width="400" height="100"></canvas>
        </div>

        <!-- 快捷命令 -->
        <div class="quick-commands">
          <div class="section-title">快捷命令</div>
          <div class="command-list">
            <n-tag
              v-for="cmd in quickCommands"
              :key="cmd.text"
              :type="cmd.type"
              @click="executeCommand(cmd)"
              style="margin: 4px; cursor: pointer;"
            >
              {{ cmd.text }}
            </n-tag>
          </div>
        </div>
      </div>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="stopListening" v-if="isListening">停止录音</n-button>
          <n-button @click="retryRecognition" v-if="error">重试</n-button>
          <n-button type="primary" @click="closeModal">关闭</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 语音设置弹窗 -->
    <n-modal v-model:show="showSettings" preset="card" style="max-width: 400px;" title="语音设置">
      <div class="voice-settings">
        <n-form :model="voiceSettings" label-placement="left" label-width="80">
          <n-form-item label="语言">
            <n-select
              v-model:value="voiceSettings.language"
              :options="languageOptions"
            />
          </n-form-item>
          <n-form-item label="引擎">
            <n-select
              v-model:value="voiceSettings.engine"
              :options="engineOptions"
            />
          </n-form-item>
          <n-form-item label="语音合成">
            <n-switch v-model:value="voiceSettings.synthesisEnabled" />
          </n-form-item>
          <n-form-item label="自动执行">
            <n-switch v-model:value="voiceSettings.autoExecute" />
          </n-form-item>
        </n-form>
      </div>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showSettings = false">取消</n-button>
          <n-button type="primary" @click="saveSettings">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import { useStrategyStore, useDataStore } from '@/stores'
import { aiApi } from '@/api'
import {
  MicOutline,
  StopOutline,
  CheckmarkOutline,
  CloseOutline,
  SettingsOutline,
  VolumeHighOutline,
  VolumeMuteOutline
} from '@vicons/ionicons5'

// 组件属性定义
interface Props {
  size?: 'small' | 'medium' | 'large'
  position?: 'fixed' | 'relative'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  position: 'fixed'
})

// 路由和状态管理
const router = useRouter()
const message = useMessage()
const strategyStore = useStrategyStore()
const dataStore = useDataStore()

// 响应式数据
const isListening = ref(false)
const isProcessing = ref(false)
const transcript = ref('')
const processedResult = ref('')
const showVoiceModal = ref(false)
const showSettings = ref(false)
const error = ref('')

// DOM引用
const waveformCanvas = ref<HTMLCanvasElement | null>(null)

// 语音识别实例
let recognition: any = null
let audioContext: AudioContext | null = null
let analyser: AnalyserNode | null = null
let microphone: MediaStreamAudioSourceNode | null = null
let animationId: number | null = null

// 语音设置
const voiceSettings = reactive({
  language: 'zh-CN',
  engine: 'webkit',
  synthesisEnabled: true,
  autoExecute: false
})

// 语言选项
const languageOptions = [
  { label: '中文', value: 'zh-CN' },
  { label: '英文', value: 'en-US' }
]

// 引擎选项
const engineOptions = [
  { label: 'Webkit', value: 'webkit' },
  { label: 'Google', value: 'google' }
]

// 快捷命令
const quickCommands = [
  { text: '生成策略', type: 'info', action: 'generate_strategy' },
  { text: '市场分析', type: 'success', action: 'market_analysis' },
  { text: '股票筛选', type: 'warning', action: 'stock_filter' },
  { text: '回测结果', type: 'error', action: 'backtest_results' }
]

// 方法
const toggleVoiceAssistant = () => {
  if (isListening.value) {
    stopListening()
  } else {
    startListening()
  }
}

const startListening = () => {
  // 检查浏览器支持
  if (!checkBrowserSupport()) {
    return
  }

  transcript.value = ''
  processedResult.value = ''
  error.value = ''
  isListening.value = true
  showVoiceModal.value = true

  // 初始化语音识别
  initSpeechRecognition()
  
  // 初始化音频波形
  initAudioWaveform()
  
  // 开始识别
  if (recognition) {
    recognition.start()
  }
}

const stopListening = () => {
  isListening.value = false
  
  if (recognition) {
    recognition.stop()
  }
  
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  
  if (microphone) {
    microphone.disconnect()
    microphone = null
  }
  
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
}

const checkBrowserSupport = () => {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  
  if (!SpeechRecognition) {
    message.error('您的浏览器不支持语音识别功能')
    return false
  }
  
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    message.error('您的浏览器不支持音频录制功能')
    return false
  }
  
  return true
}

const initSpeechRecognition = () => {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  recognition = new SpeechRecognition()
  
  recognition.lang = voiceSettings.language
  recognition.continuous = false
  recognition.interimResults = true
  recognition.maxAlternatives = 1

  recognition.onstart = () => {
    console.log('语音识别开始')
  }

  recognition.onresult = (event: any) => {
    let finalTranscript = ''
    let interimTranscript = ''

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript
      if (event.results[i].isFinal) {
        finalTranscript += transcript
      } else {
        interimTranscript += transcript
      }
    }

    transcript.value = finalTranscript || interimTranscript
  }

  recognition.onerror = (event: any) => {
    console.error('语音识别错误:', event.error)
    error.value = `识别失败: ${event.error}`
    isListening.value = false
    
    if (event.error === 'no-speech') {
      message.warning('未检测到语音，请重试')
    } else {
      message.error('语音识别失败，请重试')
    }
  }

  recognition.onend = () => {
    console.log('语音识别结束')
    isListening.value = false
    
    if (transcript.value && !error.value) {
      processTranscript()
    }
  }
}

const initAudioWaveform = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    
    audioContext = new AudioContext()
    analyser = audioContext.createAnalyser()
    microphone = audioContext.createMediaStreamSource(stream)
    
    analyser.fftSize = 256
    microphone.connect(analyser)
    
    drawWaveform()
  } catch (error) {
    console.error('初始化音频波形失败:', error)
  }
}

const drawWaveform = () => {
  if (!waveformCanvas.value || !analyser) return
  
  const canvas = waveformCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const bufferLength = analyser.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)
  
  const draw = () => {
    if (!isListening.value) return
    
    animationId = requestAnimationFrame(draw)
    
    analyser.getByteTimeDomainData(dataArray)
    
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    ctx.lineWidth = 2
    ctx.strokeStyle = '#2563eb'
    ctx.beginPath()
    
    const sliceWidth = canvas.width / bufferLength
    let x = 0
    
    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0
      const y = v * canvas.height / 2
      
      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
      
      x += sliceWidth
    }
    
    ctx.lineTo(canvas.width, canvas.height / 2)
    ctx.stroke()
  }
  
  draw()
}

const processTranscript = async () => {
  if (!transcript.value.trim()) return
  
  isProcessing.value = true
  
  try {
    // 调用AI API处理语音识别结果
    const response = await aiApi.processVoiceCommand({
      command: transcript.value,
      context: 'voice_assistant'
    })
    
    processedResult.value = response.result
    
    // 执行相应操作
    if (response.action && voiceSettings.autoExecute) {
      await executeVoiceAction(response.action)
    }
    
    // 语音合成
    if (voiceSettings.synthesisEnabled && response.speech) {
      await synthesizeSpeech(response.speech)
    }
    
  } catch (error) {
    console.error('处理语音命令失败:', error)
    processedResult.value = '处理失败，请重试'
    message.error('处理语音命令失败')
  } finally {
    isProcessing.value = false
  }
}

const executeVoiceAction = async (action: any) => {
  switch (action.type) {
    case 'navigate':
      await router.push(action.path)
      break
    case 'generate_strategy':
      await router.push('/ai')
      break
    case 'stock_filter':
      await router.push('/dashboard')
      break
    case 'backtest':
      if (action.strategyId) {
        await strategyStore.loadStrategy(action.strategyId)
        await router.push('/backtest')
      }
      break
    case 'market_analysis':
      await router.push('/monitor')
      break
    default:
      console.warn('未知的语音操作:', action)
  }
}

const synthesizeSpeech = async (text: string) => {
  if (!('speechSynthesis' in window)) {
    console.warn('浏览器不支持语音合成')
    return
  }
  
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = voiceSettings.language
  utterance.rate = 1.0
  utterance.pitch = 1.0
  utterance.volume = 1.0
  
  window.speechSynthesis.speak(utterance)
}

const retryRecognition = () => {
  error.value = ''
  startListening()
}

const executeCommand = (cmd: any) => {
  switch (cmd.action) {
    case 'generate_strategy':
      transcript.value = '请帮我生成一个量化交易策略'
      break
    case 'market_analysis':
      transcript.value = '请分析当前市场状况'
      break
    case 'stock_filter':
      transcript.value = '请帮我筛选一些优质股票'
      break
    case 'backtest_results':
      transcript.value = '请显示最近的回测结果'
      break
  }
  
  processTranscript()
}

const closeModal = () => {
  showVoiceModal.value = false
  stopListening()
}

const saveSettings = () => {
  // 保存设置到本地存储
  localStorage.setItem('voiceSettings', JSON.stringify(voiceSettings))
  showSettings.value = false
  message.success('设置已保存')
}

const loadSettings = () => {
  const saved = localStorage.getItem('voiceSettings')
  if (saved) {
    try {
      const settings = JSON.parse(saved)
      Object.assign(voiceSettings, settings)
    } catch (error) {
      console.error('加载语音设置失败:', error)
    }
  }
}

// 辅助方法
const getStatusClass = () => {
  if (error.value) return 'error'
  if (isProcessing.value) return 'processing'
  if (isListening.value) return 'listening'
  return 'idle'
}

const getStatusIcon = () => {
  if (error.value) return CloseOutline
  if (isProcessing.value) return VolumeHighOutline
  if (isListening.value) return MicOutline
  return CheckmarkOutline
}

const getStatusText = () => {
  if (error.value) return '识别失败'
  if (isProcessing.value) return '处理中...'
  if (isListening.value) return '正在听取...'
  return '准备就绪'
}

// 生命周期
onMounted(() => {
  loadSettings()
})

onUnmounted(() => {
  stopListening()
})
</script>

<style lang="scss" scoped>
.voice-assistant {
  position: v-bind('props.position');
  bottom: var(--spacing-6);
  right: var(--spacing-6);
  z-index: 1000;

  .voice-trigger {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    position: relative;

    .voice-button {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: rgba(37, 99, 235, 0.9);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
      transition: all 0.3s ease;
      backdrop-filter: blur(10px);
      border: 2px solid rgba(255, 255, 255, 0.2);

      &:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 30px rgba(37, 99, 235, 0.6);
      }

      &.active {
        background: rgba(239, 68, 68, 0.9);
        animation: pulse 1.5s infinite;
      }

      &.processing {
        background: rgba(245, 158, 11, 0.9);
      }
    }

    .voice-pulse {
      position: absolute;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      border: 2px solid rgba(37, 99, 235, 0.6);
      animation: pulseRing 1.5s infinite;
    }

    .voice-hint {
      margin-top: var(--spacing-2);
      font-size: var(--font-size-xs);
      color: var(--text-secondary);
      background: rgba(0, 0, 0, 0.8);
      padding: 4px 8px;
      border-radius: var(--border-radius-sm)all;
      white-space: nowrap;
    }
  }

  .voice-content {
    .voice-status {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: var(--spacing-4);

      .status-indicator {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: var(--spacing-2);

        &.listening {
          background: rgba(37, 99, 235, 0.1);
          color: var(--primary-color);
        }

        &.processing {
          background: rgba(245, 158, 11, 0.1);
          color: var(--warning-color);
        }

        &.error {
          background: rgba(239, 68, 68, 0.1);
          color: var(--danger-color);
        }

        &.idle {
          background: rgba(16, 185, 129, 0.1);
          color: var(--success-color);
        }
      }

      .status-text {
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
      }
    }

    .voice-result {
      margin-bottom: var(--spacing-4);

      .transcript-section,
      .result-section {
        margin-bottom: var(--spacing-3);

        .section-title {
          font-size: var(--font-size-sm);
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: var(--spacing-1);
        }

        .transcript-text {
          font-size: var(--font-size-base);
          color: var(--text-primary);
          padding: var(--spacing-2);
          background: rgba(0, 0, 0, 0.2);
          border-radius: var(--border-radius-sm)all;
          border-left: 3px solid var(--primary-color);
        }

        .result-text {
          font-size: var(--font-size-sm);
          color: var(--text-secondary);
          padding: var(--spacing-2);
          background: rgba(255, 255, 255, 0.05);
          border-radius: var(--border-radius-sm)all;
          line-height: 1.6;
        }
      }
    }

    .audio-waveform {
      margin-bottom: var(--spacing-4);
      display: flex;
      justify-content: center;

      canvas {
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-sm)all;
        background: rgba(0, 0, 0, 0.2);
      }
    }

    .quick-commands {
      .section-title {
        font-size: var(--font-size-sm);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-2);
      }

      .command-list {
        display: flex;
        flex-wrap: wrap;
        gap: var(--spacing-1);
      }
    }
  }

  .voice-settings {
    padding: var(--spacing-2);
  }
}

// 动画
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(37, 99, 235, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(37, 99, 235, 0);
  }
}

@keyframes pulseRing {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}
</style>