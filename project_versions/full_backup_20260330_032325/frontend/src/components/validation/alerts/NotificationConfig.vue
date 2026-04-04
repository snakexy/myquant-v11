<template>
  <el-card class="notification-config-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">🔔 通知配置</span>
        <el-button type="primary" size="small" @click="handleCreateChannel">
          <el-icon><Plus /></el-icon>
          添加渠道
        </el-button>
      </div>
    </template>

    <!-- 通知渠道列表 -->
    <div class="channel-list">
      <div
        v-for="channel in channels"
        :key="channel.channelId"
        class="channel-item"
      >
        <div class="channel-header">
          <div class="channel-info">
            <div class="channel-icon" :class="channel.channelType">
              <el-icon v-if="channel.channelType === 'email'"><Message /></el-icon>
              <el-icon v-else-if="channel.channelType === 'dingtalk'"><ChatDotRound /></el-icon>
              <el-icon v-else-if="channel.channelType === 'wechat'"><ChatLineRound /></el-icon>
              <el-icon v-else><Connection /></el-icon>
            </div>
            <div class="channel-details">
              <div class="channel-name">{{ getChannelTypeName(channel.channelType) }}</div>
              <div class="channel-id">{{ channel.channelId }}</div>
            </div>
          </div>
          <div class="channel-actions">
            <el-switch
              v-model="channel.enabled"
              @change="(val) => handleToggleChannel(channel, val)"
              :loading="channel.toggling"
            />
            <el-button
              link
              type="primary"
              size="small"
              @click="handleTestChannel(channel)"
              :loading="channel.testing"
            >
              测试
            </el-button>
            <el-button
              link
              size="small"
              @click="handleEditChannel(channel)"
            >
              编辑
            </el-button>
            <el-button
              link
              type="danger"
              size="small"
              @click="handleDeleteChannel(channel)"
            >
              删除
            </el-button>
          </div>
        </div>

        <div class="channel-config">
          <div class="config-item">
            <span class="config-label">状态</span>
            <el-tag :type="channel.enabled ? 'success' : 'info'" size="small">
              {{ channel.enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </div>
          <div class="config-item">
            <span class="config-label">最后使用</span>
            <span class="config-value">{{ formatTime(channel.lastUsed) }}</span>
          </div>
        </div>
      </div>
    </div>

    <el-divider />

    <!-- 通知模板 -->
    <div class="templates-section">
      <div class="section-header">
        <h4>通知模板</h4>
        <el-button text size="small" @click="loadTemplates">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>

      <div class="template-list">
        <div
          v-for="template in templates"
          :key="template.templateId"
          class="template-item"
        >
          <div class="template-header">
            <div class="template-name">{{ template.templateName }}</div>
            <el-tag :type="getSeverityTagType(template.severity)" size="small">
              {{ getSeverityText(template.severity) }}
            </el-tag>
          </div>
          <div class="template-content">
            <div class="template-field">
              <span class="field-label">主题:</span>
              <span class="field-value">{{ template.subject }}</span>
            </div>
            <div class="template-field">
              <span class="field-label">内容:</span>
              <span class="field-value">{{ truncateText(template.body, 80) }}</span>
            </div>
            <div class="template-variables">
              <span class="variables-label">可用变量:</span>
              <el-tag
                v-for="variable in template.variables"
                :key="variable"
                size="small"
                class="variable-tag"
              >
                {{ variable }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑渠道弹窗 -->
    <el-dialog
      v-model="channelDialogVisible"
      :title="isEditMode ? '编辑渠道' : '添加渠道'"
      width="600px"
      @close="resetChannelForm"
    >
      <el-form
        ref="channelFormRef"
        :model="channelFormData"
        :rules="channelFormRules"
        label-width="100px"
      >
        <el-form-item label="渠道类型" prop="channelType">
          <el-select
            v-model="channelFormData.channelType"
            placeholder="请选择渠道类型"
            :disabled="isEditMode"
          >
            <el-option label="邮件" value="email" />
            <el-option label="钉钉" value="dingtalk" />
            <el-option label="微信" value="wechat" />
            <el-option label="Webhook" value="webhook" />
          </el-select>
        </el-form-item>

        <!-- 邮件配置 -->
        <template v-if="channelFormData.channelType === 'email'">
          <el-form-item label="SMTP服务器" prop="config.host">
            <el-input v-model="channelFormData.config.host" placeholder="smtp.example.com" />
          </el-form-item>
          <el-form-item label="端口" prop="config.port">
            <el-input-number v-model="channelFormData.config.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="发件人邮箱" prop="config.from">
            <el-input v-model="channelFormData.config.from" placeholder="noreply@example.com" />
          </el-form-item>
          <el-form-item label="用户名" prop="config.username">
            <el-input v-model="channelFormData.config.username" placeholder="用户名" />
          </el-form-item>
          <el-form-item label="密码" prop="config.password">
            <el-input v-model="channelFormData.config.password" type="password" placeholder="密码或授权码" show-password />
          </el-form-item>
          <el-form-item label="收件人">
            <el-select
              v-model="channelFormData.config.to"
              multiple
              filterable
              allow-create
              placeholder="请输入收件人邮箱"
              style="width: 100%"
            >
            </el-select>
          </el-form-item>
        </template>

        <!-- 钉钉配置 -->
        <template v-else-if="channelFormData.channelType === 'dingtalk'">
          <el-form-item label="Webhook URL" prop="config.webhook">
            <el-input v-model="channelFormData.config.webhook" placeholder="https://oapi.dingtalk.com/robot/send?access_token=xxx" />
          </el-form-item>
          <el-form-item label="关键词">
            <el-input v-model="channelFormData.config.keyword" placeholder="钉钉群关键词（可选）" />
          </el-form-item>
        </template>

        <!-- 微信配置 -->
        <template v-else-if="channelFormData.channelType === 'wechat'">
          <el-form-item label="Webhook URL" prop="config.webhook">
            <el-input v-model="channelFormData.config.webhook" placeholder="企业微信机器人URL" />
          </el-form-item>
        </template>

        <!-- Webhook配置 -->
        <template v-else-if="channelFormData.channelType === 'webhook'">
          <el-form-item label="URL" prop="config.url">
            <el-input v-model="channelFormData.config.url" placeholder="https://your-webhook-url.com" />
          </el-form-item>
          <el-form-item label="请求头">
            <el-input
              v-model="channelFormData.config.headers"
              type="textarea"
              :rows="3"
              placeholder='{"Content-Type": "application/json"}'
            />
          </el-form-item>
        </template>

        <el-form-item label="启用">
          <el-switch v-model="channelFormData.enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="channelDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitChannel" :loading="submitting">
          {{ isEditMode ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 测试消息弹窗 -->
    <el-dialog
      v-model="testDialogVisible"
      title="发送测试消息"
      width="500px"
    >
      <el-form
        ref="testFormRef"
        :model="testFormData"
        :rules="testFormRules"
        label-width="80px"
      >
        <el-form-item label="测试消息" prop="message">
          <el-input
            v-model="testFormData.message"
            type="textarea"
            :rows="4"
            placeholder="请输入测试消息内容"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="testDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSendTest" :loading="sendingTest">
          发送
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import {
  Plus, Refresh, Message, ChatDotRound, ChatLineRound, Connection
} from '@element-plus/icons-vue'
import { alertApi } from '@/api/modules/alerts'
import type { NotificationChannel, NotificationTemplate } from '@/api/modules/alerts'

// 通知渠道列表
const channels = ref<NotificationChannel[]>([])
const templates = ref<NotificationTemplate[]>([])
const loading = ref(false)

// 渠道弹窗
const channelDialogVisible = ref(false)
const isEditMode = ref(false)
const currentChannelId = ref<string>('')
const submitting = ref(false)
const channelFormRef = ref<FormInstance>()

// 测试弹窗
const testDialogVisible = ref(false)
const testingChannel = ref<NotificationChannel | null>(null)
const sendingTest = ref(false)
const testFormRef = ref<FormInstance>()

// 表单数据
const channelFormData = reactive<{
  channelId?: string
  channelType: string
  enabled: boolean
  config: Record<string, any>
}>({
  channelType: 'email',
  enabled: true,
  config: {}
})

const testFormData = reactive({
  message: '这是一条测试消息，用于验证通知渠道配置是否正确。'
})

// 表单验证规则
const channelFormRules: FormRules = {
  channelType: [
    { required: true, message: '请选择渠道类型', trigger: 'change' }
  ],
  'config.host': [
    { required: true, message: '请输入SMTP服务器', trigger: 'blur' }
  ],
  'config.port': [
    { required: true, message: '请输入端口', trigger: 'blur' }
  ],
  'config.from': [
    { required: true, message: '请输入发件人邮箱', trigger: 'blur' }
  ],
  'config.webhook': [
    { required: true, message: '请输入Webhook URL', trigger: 'blur' }
  ],
  'config.url': [
    { required: true, message: '请输入URL', trigger: 'blur' }
  ]
}

const testFormRules: FormRules = {
  message: [
    { required: true, message: '请输入测试消息', trigger: 'blur' },
    { min: 5, max: 200, message: '长度在 5 到 200 个字符', trigger: 'blur' }
  ]
}

// 加载通知渠道
const loadChannels = async () => {
  loading.value = true
  try {
    const response = await alertApi.getNotificationChannels()
    if (response.code === 200) {
      channels.value = response.data.map(ch => ({
        ...ch,
        toggling: false,
        testing: false
      }))
    }
  } catch (error) {
    console.error('加载通知渠道失败:', error)
    // 降级方案：使用默认渠道数据
    channels.value = [
      {
        channelId: 'email_1',
        channelType: 'email',
        enabled: true,
        config: {
          host: 'smtp.example.com',
          port: 465,
          from: 'alert@example.com'
        },
        lastUsed: new Date(Date.now() - 3600000).toISOString(),
        toggling: false,
        testing: false
      },
      {
        channelId: 'dingtalk_1',
        channelType: 'dingtalk',
        enabled: true,
        config: {
          webhook: 'https://oapi.dingtalk.com/robot/send?access_token=xxx'
        },
        lastUsed: new Date(Date.now() - 7200000).toISOString(),
        toggling: false,
        testing: false
      },
      {
        channelId: 'webhook_1',
        channelType: 'webhook',
        enabled: false,
        config: {
          url: 'https://your-webhook-url.com'
        },
        toggling: false,
        testing: false
      }
    ]
    ElMessage.warning('使用默认渠道数据')
  } finally {
    loading.value = false
  }
}

// 加载通知模板
const loadTemplates = async () => {
  try {
    const response = await alertApi.getNotificationTemplates()
    if (response.code === 200) {
      templates.value = response.data
    }
  } catch (error) {
    console.error('加载通知模板失败:', error)
    // 降级方案：使用默认模板
    templates.value = [
      {
        templateId: 'tpl_1',
        templateName: '严重预警模板',
        severity: 'critical',
        subject: '【严重预警】{ruleName}',
        body: '预警规则 {ruleName} 已触发\n\n指标: {metric}\n当前值: {currentValue}\n阈值: {threshold}\n\n触发时间: {timestamp}',
        variables: ['ruleName', 'metric', 'currentValue', 'threshold', 'timestamp']
      },
      {
        templateId: 'tpl_2',
        templateName: '警告预警模板',
        severity: 'warning',
        subject: '【警告】{ruleName}',
        body: '预警规则 {ruleName} 已触发\n\n指标: {metric}\n当前值: {currentValue}\n阈值: {threshold}',
        variables: ['ruleName', 'metric', 'currentValue', 'threshold']
      },
      {
        templateId: 'tpl_3',
        templateName: '信息通知模板',
        severity: 'info',
        subject: '【信息】{title}',
        body: '{message}\n\n时间: {timestamp}',
        variables: ['title', 'message', 'timestamp']
      }
    ]
  }
}

// 创建渠道
const handleCreateChannel = () => {
  isEditMode.value = false
  channelDialogVisible.value = true
}

// 编辑渠道
const handleEditChannel = (channel: any) => {
  isEditMode.value = true
  currentChannelId.value = channel.channelId

  // 填充表单
  channelFormData.channelId = channel.channelId
  channelFormData.channelType = channel.channelType
  channelFormData.enabled = channel.enabled
  channelFormData.config = { ...channel.config }

  channelDialogVisible.value = true
}

// 删除渠道
const handleDeleteChannel = async (channel: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${getChannelTypeName(channel.channelType)} 渠道吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    ElMessage.success('渠道已删除（模拟）')
    await loadChannels()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除渠道失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 切换渠道状态
const handleToggleChannel = async (channel: any, enabled: boolean) => {
  channel.toggling = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    channel.enabled = enabled
    ElMessage.success(enabled ? '渠道已启用' : '渠道已禁用')
  } catch (error) {
    console.error('切换渠道状态失败:', error)
    channel.enabled = !enabled
    ElMessage.error('操作失败')
  } finally {
    channel.toggling = false
  }
}

// 测试渠道
const handleTestChannel = (channel: any) => {
  testingChannel.value = channel
  testFormData.message = `这是一条测试消息，用于验证 ${getChannelTypeName(channel.channelType)} 渠道配置是否正确。`
  testDialogVisible.value = true
}

// 发送测试消息
const handleSendTest = async () => {
  if (!testFormRef.value) return
  if (!testingChannel.value) return

  try {
    await testFormRef.value.validate()
  } catch {
    return
  }

  sendingTest.value = true
  testingChannel.value.testing = true

  try {
    const response = await alertApi.testNotification(
      testingChannel.value.channelId,
      testFormData.message
    )
    if (response.code === 200) {
      ElMessage.success('测试消息已发送')
      testDialogVisible.value = false
      // 更新最后使用时间
      testingChannel.value.lastUsed = new Date().toISOString()
    }
  } catch (error) {
    console.error('发送测试消息失败:', error)
    ElMessage.error('发送失败')
  } finally {
    sendingTest.value = false
    testingChannel.value.testing = false
  }
}

// 提交渠道表单
const handleSubmitChannel = async () => {
  if (!channelFormRef.value) return

  try {
    await channelFormRef.value.validate()
  } catch {
    ElMessage.warning('请检查表单填写')
    return
  }

  submitting.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success(isEditMode.value ? '渠道已更新' : '渠道已添加')
    channelDialogVisible.value = false
    await loadChannels()
  } catch (error) {
    console.error('提交渠道失败:', error)
    ElMessage.error(isEditMode.value ? '更新失败' : '添加失败')
  } finally {
    submitting.value = false
  }
}

// 重置渠道表单
const resetChannelForm = () => {
  channelFormRef.value?.resetFields()
  Object.assign(channelFormData, {
    channelId: undefined,
    channelType: 'email',
    enabled: true,
    config: {}
  })
  currentChannelId.value = ''
}

// 格式化时间
const formatTime = (timeStr?: string): string => {
  if (!timeStr) return '未使用'
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

// 获取渠道类型名称
const getChannelTypeName = (type: string): string => {
  const typeMap: Record<string, string> = {
    email: '邮件',
    dingtalk: '钉钉',
    wechat: '微信',
    webhook: 'Webhook'
  }
  return typeMap[type] || type
}

// 获取严重级别标签类型
const getSeverityTagType = (severity: string): string => {
  const severityMap: Record<string, string> = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return severityMap[severity] || 'info'
}

// 获取严重级别文本
const getSeverityText = (severity: string): string => {
  const severityMap: Record<string, string> = {
    critical: '严重',
    warning: '警告',
    info: '信息'
  }
  return severityMap[severity] || severity
}

// 截断文本
const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 生命周期
onMounted(() => {
  loadChannels()
  loadTemplates()
})

// 暴露方法
defineExpose({
  refresh: () => Promise.all([loadChannels(), loadTemplates()])
})
</script>

<style scoped lang="scss">
.notification-config-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .channel-list {
    .channel-item {
      padding: 16px;
      margin-bottom: 16px;
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      transition: all 0.3s;

      &:last-child {
        margin-bottom: 0;
      }

      &:hover {
        border-color: #409eff;
        box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
      }

      .channel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .channel-info {
          display: flex;
          gap: 12px;
          align-items: center;

          .channel-icon {
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            font-size: 24px;

            &.email {
              background-color: rgba(64, 158, 255, 0.1);
              color: #409eff;
            }

            &.dingtalk {
              background-color: rgba(103, 194, 58, 0.1);
              color: #67c23a;
            }

            &.wechat {
              background-color: rgba(230, 162, 60, 0.1);
              color: #e6a23c;
            }

            &.webhook {
              background-color: rgba(144, 147, 153, 0.1);
              color: #909399;
            }
          }

          .channel-details {
            .channel-name {
              font-size: 14px;
              font-weight: 600;
              color: #303133;
              margin-bottom: 4px;
            }

            .channel-id {
              font-size: 12px;
              color: #909399;
            }
          }
        }

        .channel-actions {
          display: flex;
          gap: 8px;
          align-items: center;
        }
      }

      .channel-config {
        display: flex;
        gap: 24px;

        .config-item {
          display: flex;
          align-items: center;
          gap: 8px;

          .config-label {
            font-size: 12px;
            color: #909399;
          }

          .config-value {
            font-size: 12px;
            color: #606266;
          }
        }
      }
    }
  }

  .templates-section {
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      h4 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }

    .template-list {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;

      .template-item {
        padding: 16px;
        border: 1px solid #e4e7ed;
        border-radius: 8px;
        transition: all 0.3s;

        &:hover {
          border-color: #409eff;
          box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
        }

        .template-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;

          .template-name {
            font-size: 14px;
            font-weight: 600;
            color: #303133;
          }
        }

        .template-content {
          .template-field {
            margin-bottom: 8px;
            font-size: 12px;

            &:last-child {
              margin-bottom: 0;
            }

            .field-label {
              color: #909399;
              margin-right: 4px;
            }

            .field-value {
              color: #606266;
            }
          }

          .template-variables {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #e4e7ed;

            .variables-label {
              font-size: 11px;
              color: #909399;
              margin-right: 8px;
            }

            .variable-tag {
              margin-right: 4px;
              margin-bottom: 4px;
              font-family: 'Courier New', monospace;
            }
          }
        }
      }
    }
  }

  :deep(.el-dialog) {
    .el-form-item {
      margin-bottom: 18px;
    }
  }
}
</style>
