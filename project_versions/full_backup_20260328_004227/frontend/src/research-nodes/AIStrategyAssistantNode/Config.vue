<template>
  <div class="ai-strategy-assistant-config">
    <el-form label-position="top" size="small">
      <!-- API配置状态 -->
      <div class="api-status-banner" v-if="!apiConfigured">
        <el-alert
          title="DeepSeek API未配置"
          type="warning"
          description="请先配置DeepSeek API密钥才能使用AI生成功能"
          :closable="false"
        >
          <template #default>
            <el-button type="primary" size="small" @click="showApiKeyDialog = true">
              配置API密钥
            </el-button>
          </template>
        </el-alert>
      </div>

      <!-- 策略类型 -->
      <el-form-item label="策略类型">
        <el-select v-model="localParams.strategyType" style="width: 100%">
          <el-option label="趋势跟踪" value="trend-following" />
          <el-option label="均值回归" value="mean-reversion" />
          <el-option label="动量策略" value="momentum" />
          <el-option label="自定义" value="custom" />
        </el-select>
        <div class="form-tip">选择策略的基本类型</div>
      </el-form-item>

      <!-- 市场环境 -->
      <el-form-item label="市场环境">
        <el-select v-model="localParams.marketCondition" style="width: 100%">
          <el-option label="震荡市" value="震荡市" />
          <el-option label="趋势市" value="趋势市" />
          <el-option label="熊市" value="熊市" />
          <el-option label="牛市" value="牛市" />
          <el-option label="不确定" value="不确定" />
        </el-select>
        <div class="form-tip">选择目标市场环境</div>
      </el-form-item>

      <!-- 策略描述 -->
      <el-form-item label="策略描述">
        <el-input
          v-model="localParams.description"
          type="textarea"
          :rows="5"
          placeholder="描述您想要的策略想法...&#10;例如：基于均线交叉的趋势跟踪策略，结合成交量确认"
        />
        <div class="form-tip">详细描述您的策略想法，AI将根据描述生成QLib兼容的策略代码</div>
      </el-form-item>

      <!-- 风险偏好 -->
      <el-form-item label="风险偏好">
        <el-radio-group v-model="localParams.riskLevel">
          <el-radio value="conservative">保守</el-radio>
          <el-radio value="moderate">中等</el-radio>
          <el-radio value="aggressive">激进</el-radio>
        </el-radio-group>
        <div class="form-tip">选择策略的风险等级</div>
      </el-form-item>

      <!-- 生成选项 -->
      <div class="section-title">生成选项</div>

      <el-form-item>
        <el-checkbox v-model="localParams.includeStopLoss">
          包含止损
        </el-checkbox>
        <div class="form-tip">生成的策略包含止损条件</div>
      </el-form-item>

      <el-form-item>
        <el-checkbox v-model="localParams.includeTakeProfit">
          包含止盈
        </el-checkbox>
        <div class="form-tip">生成的策略包含止盈条件</div>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button
        type="primary"
        :loading="generating"
        :disabled="!localParams.description || !apiConfigured"
        @click="generateStrategy"
        style="width: 100%"
      >
        <el-icon v-if="!generating"><MagicStick /></el-icon>
        {{ generating ? 'AI生成中...' : '生成策略代码' }}
      </el-button>
    </div>

    <!-- 生成状态显示 -->
    <div class="generation-status" v-if="generationData">
      <el-divider />
      <div class="status-header">生成结果</div>
      <div class="status-content">
        <el-tag type="success" size="large" v-if="generationData.success">策略生成成功</el-tag>
        <el-tag type="danger" size="large" v-else>生成失败</el-tag>

        <!-- AI回复 -->
        <div v-if="generationData.reply" class="ai-reply">
          <div class="reply-header">AI说明:</div>
          <div class="reply-content">{{ generationData.reply }}</div>
        </div>

        <!-- 策略描述 -->
        <div v-if="generationData.description" class="strategy-description">
          <div class="description-header">策略说明:</div>
          <div class="description-overview">{{ generationData.description.overview }}</div>
          <div v-if="generationData.description.usage" class="description-usage">
            <strong>使用方法:</strong> {{ generationData.description.usage }}
          </div>
        </div>

        <!-- 生成的代码 -->
        <div v-if="generationData.code" class="generated-code">
          <div class="code-header">
            <span>生成的代码:</span>
            <el-button
              type="primary"
              size="small"
              @click="copyCode"
              style="margin-left: auto"
            >
              复制代码
            </el-button>
          </div>
          <el-input
            type="textarea"
            :model-value="generationData.code"
            :rows="15"
            readonly
            class="code-textarea"
          />
        </div>
      </div>
    </div>

    <!-- API密钥配置对话框 -->
    <el-dialog
      v-model="showApiKeyDialog"
      title="配置DeepSeek API"
      width="500px"
    >
      <el-form label-position="top">
        <el-form-item label="API密钥">
          <el-input
            v-model="apiKeyInput"
            type="password"
            placeholder="sk-..."
            show-password
          />
          <div class="form-tip">
            请输入您的DeepSeek API密钥。密钥将被安全保存在服务器配置文件中。
            <br>
            <a href="https://platform.deepseek.com/api_keys" target="_blank">
              获取API密钥 →
            </a>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showApiKeyDialog = false">取消</el-button>
        <el-button type="primary" @click="saveApiKey" :loading="savingApiKey">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import axios from 'axios'

interface Props {
  params: Record<string, any>
  data?: any
}

interface Emits {
  (e: 'update:params', value: Record<string, any>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 本地参数副本
const localParams = ref<Record<string, any>>({
  strategyType: 'trend-following',
  marketCondition: '震荡市',
  description: '',
  riskLevel: 'moderate',
  includeStopLoss: true,
  includeTakeProfit: true,
  ...props.params
})

// API配置状态
const apiConfigured = ref(false)
const showApiKeyDialog = ref(false)
const apiKeyInput = ref('')
const savingApiKey = ref(false)

// 生成状态
const generating = ref(false)
const generationData = ref<any>(null)

// 检查API配置状态
const checkApiConfig = async () => {
  try {
    const response = await axios.get('/api/v1/research/ai/config')
    if (response.data.success) {
      apiConfigured.value = response.data.data.configured
    }
  } catch (error) {
    console.error('检查API配置失败:', error)
  }
}

// 保存API密钥
const saveApiKey = async () => {
  if (!apiKeyInput.value.trim()) {
    ElMessage.warning('请输入API密钥')
    return
  }

  savingApiKey.value = true
  try {
    const response = await axios.post('/api/v1/research/ai/config', {
      api_key: apiKeyInput.value.trim()
    })

    if (response.data.success) {
      ElMessage.success('API密钥保存成功')
      showApiKeyDialog.value = false
      apiConfigured.value = true
      apiKeyInput.value = ''
    } else {
      ElMessage.error('API密钥保存失败')
    }
  } catch (error: any) {
    console.error('保存API密钥失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    savingApiKey.value = false
  }
}

// 生成策略
const generateStrategy = async () => {
  if (!localParams.value.description.trim()) {
    ElMessage.warning('请输入策略描述')
    return
  }

  generating.value = true
  generationData.value = null

  try {
    const response = await axios.post('/api/v1/research/ai/generate', {
      prompt: localParams.value.description,
      strategy_type: localParams.value.strategyType,
      market_condition: localParams.value.marketCondition
    })

    if (response.data.success && response.data.data) {
      generationData.value = response.data.data
      ElMessage.success('策略生成成功')
    } else {
      ElMessage.error(response.data.error || '生成失败')
    }
  } catch (error: any) {
    console.error('生成策略失败:', error)
    ElMessage.error(error.response?.data?.detail || '生成失败')
  } finally {
    generating.value = false
  }
}

// 复制代码
const copyCode = async () => {
  if (!generationData.value?.code) return

  try {
    await navigator.clipboard.writeText(generationData.value.code)
    ElMessage.success('代码已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 监听参数变化
watch(localParams, (newParams) => {
  emit('update:params', { ...newParams })
}, { deep: true })

// 组件挂载时检查API配置
onMounted(() => {
  checkApiConfig()
})
</script>

<style scoped>
.ai-strategy-assistant-config {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.api-status-banner {
  margin-bottom: 8px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin: 12px 0 8px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #e5e7eb;
}

.form-tip {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
  line-height: 1.4;
}

.form-tip a {
  color: #2563eb;
  text-decoration: none;
}

.form-tip a:hover {
  text-decoration: underline;
}

.action-buttons {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.generation-status {
  margin-top: 16px;
}

.status-header {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-reply {
  padding: 12px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
}

.reply-header {
  font-size: 12px;
  font-weight: 600;
  color: #0369a1;
  margin-bottom: 6px;
}

.reply-content {
  font-size: 13px;
  color: #0c4a6e;
  line-height: 1.6;
  white-space: pre-wrap;
}

.strategy-description {
  padding: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.description-header {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}

.description-overview {
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
  margin-bottom: 8px;
}

.description-usage {
  font-size: 12px;
  color: #4b5563;
  line-height: 1.5;
  padding: 8px;
  background: #f3f4f6;
  border-radius: 4px;
}

.generated-code {
  margin-top: 8px;
}

.code-header {
  display: flex;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.code-textarea {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.code-textarea :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  background-color: #1e1e1e;
  color: #d4d4d4;
}
</style>
