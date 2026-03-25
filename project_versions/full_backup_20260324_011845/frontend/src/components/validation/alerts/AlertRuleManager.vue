<template>
  <el-card class="alert-rule-card" shadow="never">
    <template #header>
      <div class="card-header">
        <span class="title">🚨 预警规则管理</span>
        <el-button type="primary" size="small" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          创建规则
        </el-button>
      </div>
    </template>

    <!-- 筛选器 -->
    <div class="filter-bar">
      <el-select
        v-model="filterSeverity"
        placeholder="全部级别"
        clearable
        size="small"
        style="width: 120px"
        @change="loadRules"
      >
        <el-option label="全部级别" value="" />
        <el-option label="严重" value="critical" />
        <el-option label="警告" value="warning" />
        <el-option label="信息" value="info" />
      </el-select>

      <el-select
        v-model="filterEnabled"
        placeholder="全部状态"
        clearable
        size="small"
        style="width: 120px"
        @change="loadRules"
      >
        <el-option label="全部状态" value="" />
        <el-option label="已启用" value="true" />
        <el-option label="已禁用" value="false" />
      </el-select>

      <el-button size="small" @click="loadRules" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 规则列表 -->
    <el-table :data="rules" v-loading="loading" style="width: 100%">
      <el-table-column prop="ruleName" label="规则名称" min-width="150" />
      <el-table-column prop="ruleType" label="类型" width="100">
        <template #default="scope">
          <el-tag :type="getRuleTypeTagType(scope.row.ruleType)" size="small">
            {{ getRuleTypeText(scope.row.ruleType) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="severity" label="级别" width="80">
        <template #default="scope">
          <el-tag :type="getSeverityTagType(scope.row.severity)" size="small">
            {{ getSeverityText(scope.row.severity) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="condition.metric" label="指标" width="120" />
      <el-table-column prop="condition" label="条件" width="150">
        <template #default="scope">
          {{ formatCondition(scope.row.condition) }}
        </template>
      </el-table-column>
      <el-table-column prop="enabled" label="状态" width="80">
        <template #default="scope">
          <el-switch
            v-model="scope.row.enabled"
            @change="(val) => handleToggleEnable(scope.row, val)"
            :loading="scope.row.toggling"
          />
        </template>
      </el-table-column>
      <el-table-column prop="triggerCount" label="触发次数" width="90" />
      <el-table-column prop="createdAt" label="创建时间" width="160">
        <template #default="scope">
          {{ formatDate(scope.row.createdAt) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="scope">
          <el-button
            link
            type="primary"
            size="small"
            @click="handleEdit(scope.row)"
          >
            编辑
          </el-button>
          <el-button
            link
            type="danger"
            size="small"
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑规则弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑规则' : '创建规则'"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="规则名称" prop="ruleName">
          <el-input
            v-model="formData.ruleName"
            placeholder="请输入规则名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="规则类型" prop="ruleType">
          <el-select v-model="formData.ruleType" placeholder="请选择规则类型">
            <el-option label="风险预警" value="risk" />
            <el-option label="机会预警" value="opportunity" />
            <el-option label="系统预警" value="system" />
          </el-select>
        </el-form-item>

        <el-form-item label="严重级别" prop="severity">
          <el-radio-group v-model="formData.severity">
            <el-radio label="info">信息</el-radio>
            <el-radio label="warning">警告</el-radio>
            <el-radio label="critical">严重</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-divider content-position="left">触发条件</el-divider>

        <el-form-item label="监控指标" prop="condition.metric">
          <el-select v-model="formData.condition.metric" placeholder="请选择指标">
            <el-option label="夏普比率" value="sharpe_ratio" />
            <el-option label="最大回撤" value="max_drawdown" />
            <el-option label="总收益率" value="total_return" />
            <el-option label="波动率" value="volatility" />
            <el-option label="胜率" value="win_rate" />
            <el-option label="盈亏比" value="profit_loss_ratio" />
          </el-select>
        </el-form-item>

        <el-form-item label="判断条件" prop="condition.operator">
          <el-select v-model="formData.condition.operator" placeholder="请选择条件">
            <el-option label="大于" value="gt" />
            <el-option label="小于" value="lt" />
            <el-option label="等于" value="eq" />
            <el-option label="大于等于" value="gte" />
            <el-option label="小于等于" value="lte" />
          </el-select>
        </el-form-item>

        <el-form-item label="阈值" prop="condition.threshold">
          <el-input-number
            v-model="formData.condition.threshold"
            :precision="2"
            :step="0.1"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="时间窗口(秒)" prop="condition.timeWindow">
          <el-input-number
            v-model="formData.condition.timeWindow"
            :min="0"
            :step="60"
            :precision="0"
            placeholder="0表示不限制"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="规则描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入规则描述（可选）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEditMode ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance, FormRules } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { alertApi } from '@/api/modules/alerts'
import type { AlertRule, CreateRuleRequest, UpdateRuleRequest } from '@/api/modules/alerts'

// 筛选器
const filterSeverity = ref<string>('')
const filterEnabled = ref<string>('')

// 规则列表
const rules = ref<AlertRule[]>([])
const loading = ref(false)

// 弹窗和表单
const dialogVisible = ref(false)
const isEditMode = ref(false)
const currentRuleId = ref<string>('')
const submitting = ref(false)

const formRef = ref<FormInstance>()

// 表单数据
const formData = reactive<CreateRuleRequest & { ruleId?: string }>({
  ruleName: '',
  ruleType: 'risk',
  severity: 'warning',
  condition: {
    metric: 'sharpe_ratio',
    operator: 'lt',
    threshold: 1.0,
    timeWindow: 0
  },
  description: ''
})

// 表单验证规则
const formRules: FormRules = {
  ruleName: [
    { required: true, message: '请输入规则名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  ruleType: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ],
  severity: [
    { required: true, message: '请选择严重级别', trigger: 'change' }
  ],
  'condition.metric': [
    { required: true, message: '请选择监控指标', trigger: 'change' }
  ],
  'condition.operator': [
    { required: true, message: '请选择判断条件', trigger: 'change' }
  ],
  'condition.threshold': [
    { required: true, message: '请输入阈值', trigger: 'blur' }
  ]
}

// 自动刷新定时器
let refreshInterval: number | null = null

// 加载规则列表
const loadRules = async () => {
  loading.value = true
  try {
    const enabledOnly = filterEnabled.value === 'true' ? true : filterEnabled.value === 'false' ? false : undefined
    const response = await alertApi.listRules(filterSeverity.value || undefined, enabledOnly)

    if (response.code === 200) {
      rules.value = response.data.rules.map(rule => ({
        ...rule,
        toggling: false
      }))
    }
  } catch (error) {
    console.error('加载规则列表失败:', error)
    // 降级方案：使用默认规则
    rules.value = [
      {
        ruleId: 'rule_1',
        ruleName: '夏普比率过低预警',
        ruleType: 'risk',
        severity: 'warning',
        condition: {
          metric: 'sharpe_ratio',
          operator: 'lt',
          threshold: 1.0,
          timeWindow: 3600
        },
        enabled: true,
        description: '当夏普比率低于1.0时发出预警',
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        updatedAt: new Date().toISOString(),
        triggerCount: 5,
        toggling: false
      },
      {
        ruleId: 'rule_2',
        ruleName: '最大回撤超限',
        ruleType: 'risk',
        severity: 'critical',
        condition: {
          metric: 'max_drawdown',
          operator: 'gt',
          threshold: 20.0,
          timeWindow: 0
        },
        enabled: true,
        description: '当最大回撤超过20%时发出严重预警',
        createdAt: new Date(Date.now() - 172800000).toISOString(),
        updatedAt: new Date().toISOString(),
        triggerCount: 2,
        toggling: false
      },
      {
        ruleId: 'rule_3',
        ruleName: '高收益机会',
        ruleType: 'opportunity',
        severity: 'info',
        condition: {
          metric: 'total_return',
          operator: 'gte',
          threshold: 10.0,
          timeWindow: 604800
        },
        enabled: false,
        description: '当周收益率超过10%时提示投资机会',
        createdAt: new Date(Date.now() - 259200000).toISOString(),
        updatedAt: new Date().toISOString(),
        triggerCount: 0,
        toggling: false
      }
    ]
    ElMessage.warning('使用默认规则数据')
  } finally {
    loading.value = false
  }
}

// 创建规则
const handleCreate = () => {
  isEditMode.value = false
  dialogVisible.value = true
}

// 编辑规则
const handleEdit = (rule: AlertRule) => {
  isEditMode.value = true
  currentRuleId.value = rule.ruleId

  // 填充表单数据
  formData.ruleId = rule.ruleId
  formData.ruleName = rule.ruleName
  formData.ruleType = rule.ruleType
  formData.severity = rule.severity
  formData.condition = { ...rule.condition }
  formData.description = rule.description

  dialogVisible.value = true
}

// 删除规则
const handleDelete = async (rule: AlertRule) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则 "${rule.ruleName}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await alertApi.deleteRule(rule.ruleId)
    if (response.code === 200) {
      ElMessage.success('规则已删除')
      await loadRules()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除规则失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 切换启用/禁用
const handleToggleEnable = async (rule: AlertRule & { toggling: boolean }, enabled: boolean) => {
  rule.toggling = true
  try {
    const response = enabled
      ? await alertApi.enableRule(rule.ruleId)
      : await alertApi.disableRule(rule.ruleId)

    if (response.code === 200) {
      rule.enabled = enabled
      ElMessage.success(enabled ? '规则已启用' : '规则已禁用')
    }
  } catch (error) {
    console.error('切换规则状态失败:', error)
    // 回滚状态
    rule.enabled = !enabled
    ElMessage.error('操作失败')
  } finally {
    rule.toggling = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    ElMessage.warning('请检查表单填写')
    return
  }

  submitting.value = true
  try {
    if (isEditMode.value) {
      // 编辑模式
      const updateRequest: UpdateRuleRequest = {
        ruleName: formData.ruleName,
        condition: formData.condition,
        severity: formData.severity,
        description: formData.description
      }

      const response = await alertApi.updateRule(currentRuleId.value, updateRequest)
      if (response.code === 200) {
        ElMessage.success('规则已更新')
        dialogVisible.value = false
        await loadRules()
      }
    } else {
      // 创建模式
      const createRequest: CreateRuleRequest = {
        ruleName: formData.ruleName,
        ruleType: formData.ruleType,
        condition: formData.condition,
        severity: formData.severity,
        description: formData.description
      }

      const response = await alertApi.createRule(createRequest)
      if (response.code === 200) {
        ElMessage.success('规则已创建')
        dialogVisible.value = false
        await loadRules()
      }
    }
  } catch (error) {
    console.error('提交规则失败:', error)
    ElMessage.error(isEditMode.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(formData, {
    ruleId: undefined,
    ruleName: '',
    ruleType: 'risk',
    severity: 'warning',
    condition: {
      metric: 'sharpe_ratio',
      operator: 'lt',
      threshold: 1.0,
      timeWindow: 0
    },
    description: ''
  })
  currentRuleId.value = ''
}

// 格式化条件显示
const formatCondition = (condition: any): string => {
  const operatorMap: Record<string, string> = {
    gt: '>',
    lt: '<',
    eq: '=',
    gte: '>=',
    lte: '<='
  }
  const operator = operatorMap[condition.operator] || condition.operator
  return `${condition.metric} ${operator} ${condition.threshold}`
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 规则类型标签类型
const getRuleTypeTagType = (type: string): string => {
  const typeMap: Record<string, string> = {
    risk: 'danger',
    opportunity: 'success',
    system: 'info'
  }
  return typeMap[type] || 'info'
}

// 规则类型文本
const getRuleTypeText = (type: string): string => {
  const typeMap: Record<string, string> = {
    risk: '风险',
    opportunity: '机会',
    system: '系统'
  }
  return typeMap[type] || type
}

// 严重级别标签类型
const getSeverityTagType = (severity: string): string => {
  const severityMap: Record<string, string> = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return severityMap[severity] || 'info'
}

// 严重级别文本
const getSeverityText = (severity: string): string => {
  const severityMap: Record<string, string> = {
    critical: '严重',
    warning: '警告',
    info: '信息'
  }
  return severityMap[severity] || severity
}

// 启动自动刷新
const startAutoRefresh = () => {
  refreshInterval = window.setInterval(() => {
    loadRules()
  }, 30000) // 每30秒刷新一次
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// 生命周期
onMounted(() => {
  loadRules()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

// 暴露方法给父组件
defineExpose({
  loadRules,
  refresh: loadRules
})
</script>

<style scoped lang="scss">
.alert-rule-card {
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

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    align-items: center;
  }

  :deep(.el-table) {
    .el-table__header th {
      background-color: #f5f7fa;
      font-weight: 600;
    }
  }

  :deep(.el-dialog) {
    .el-divider {
      margin: 16px 0;
    }

    .el-form-item {
      margin-bottom: 18px;
    }
  }
}
</style>
