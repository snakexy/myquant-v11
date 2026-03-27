<template>
  <div class="node-config-form">
    <el-tabs v-model="activeTab" type="card">
      <!-- 基本配置 -->
      <el-tab-pane label="基本配置" name="basic">
        <el-form :model="nodeConfig" label-width="120px">
          <el-form-item label="节点名称" required>
            <el-input v-model="nodeConfig.name" placeholder="请输入节点名称" />
          </el-form-item>
          
          <el-form-item label="显示名称">
            <el-input v-model="nodeConfig.displayName" placeholder="请输入显示名称" />
          </el-form-item>
          
          <el-form-item label="描述">
            <el-input
              v-model="nodeConfig.description"
              type="textarea"
              :rows="3"
              placeholder="请输入节点描述"
            />
          </el-form-item>
          
          <el-form-item label="节点类型">
            <el-select v-model="nodeConfig.type" placeholder="请选择节点类型" :disabled="!isNewNode">
              <el-option
                v-for="type in nodeTypes"
                :key="type.value"
                :label="type.label"
                :value="type.value"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="位置">
            <div class="position-inputs">
              <el-input-number
                v-model="nodeConfig.position.x"
                :min="0"
                placeholder="X坐标"
                style="width: 120px"
              />
              <el-input-number
                v-model="nodeConfig.position.y"
                :min="0"
                placeholder="Y坐标"
                style="width: 120px"
              />
            </div>
          </el-form-item>
          
          <el-form-item label="大小">
            <div class="size-inputs">
              <el-input-number
                v-model="nodeConfig.size.width"
                :min="100"
                placeholder="宽度"
                style="width: 120px"
              />
              <el-input-number
                v-model="nodeConfig.size.height"
                :min="60"
                placeholder="高度"
                style="width: 120px"
              />
            </div>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 参数配置 -->
      <el-tab-pane label="参数配置" name="parameters">
        <div class="parameters-header">
          <el-button @click="addParameter" type="primary" size="small">
            <el-icon><Plus /></el-icon>
            添加参数
          </el-button>
          <el-button @click="importParameters" size="small">
            <el-icon><Upload /></el-icon>
            导入参数
          </el-button>
        </div>
        
        <div class="parameters-list">
          <div
            v-for="(param, index) in nodeConfig.parameters"
            :key="param.id"
            class="parameter-item"
          >
            <div class="parameter-header">
              <el-input
                v-model="param.name"
                placeholder="参数名称"
                style="width: 150px"
              />
              <el-input
                v-model="param.displayName"
                placeholder="显示名称"
                style="width: 150px"
              />
              <el-select v-model="param.type" placeholder="类型" style="width: 120px">
                <el-option label="字符串" value="string" />
                <el-option label="数字" value="number" />
                <el-option label="布尔值" value="boolean" />
                <el-option label="选择" value="select" />
                <el-option label="文件" value="file" />
                <el-option label="数组" value="array" />
                <el-option label="对象" value="object" />
              </el-select>
              <el-button @click="removeParameter(index)" type="danger" size="small" text>
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            
            <div class="parameter-details">
              <el-input
                v-model="param.description"
                placeholder="参数描述"
                style="width: 100%"
              />
              
              <div class="parameter-config">
                <el-checkbox v-model="param.required">必填</el-checkbox>
                <el-checkbox v-model="param.advanced">高级</el-checkbox>
                <el-checkbox v-model="param.hidden">隐藏</el-checkbox>
              </div>
              
              <!-- 默认值配置 -->
              <div class="parameter-value">
                <label class="value-label">默认值:</label>
                <component
                  :is="getParameterValueComponent(param.type)"
                  v-model="param.value"
                  v-bind="getParameterValueProps(param)"
                />
              </div>
              
              <!-- 验证规则配置 -->
              <div v-if="param.type === 'number'" class="parameter-validation">
                <label class="validation-label">验证规则:</label>
                <div class="validation-rules">
                  <el-input-number
                    v-model="param.validation.min"
                    placeholder="最小值"
                    :min="0"
                    style="width: 100px"
                  />
                  <el-input-number
                    v-model="param.validation.max"
                    placeholder="最大值"
                    style="width: 100px"
                  />
                </div>
              </div>
              
              <!-- 选项配置 -->
              <div v-if="param.type === 'select'" class="parameter-options">
                <label class="options-label">选项:</label>
                <div class="options-list">
                  <div
                    v-for="(option, optionIndex) in param.options"
                    :key="optionIndex"
                    class="option-item"
                  >
                    <el-input
                      v-model="option.label"
                      placeholder="选项标签"
                      style="width: 120px"
                    />
                    <el-input
                      v-model="option.value"
                      placeholder="选项值"
                      style="width: 120px"
                    />
                    <el-button @click="removeOption(param, optionIndex)" type="danger" size="small" text>
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  <el-button @click="addOption(param)" type="primary" size="small" text>
                    <el-icon><Plus /></el-icon>
                    添加选项
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 输入输出配置 -->
      <el-tab-pane label="输入输出" name="ports">
        <div class="ports-section">
          <div class="ports-header">
            <h4>输入端口</h4>
            <el-button @click="addInputPort" type="primary" size="small">
              <el-icon><Plus /></el-icon>
              添加输入
            </el-button>
          </div>
          
          <div class="ports-list">
            <div
              v-for="(port, index) in nodeConfig.inputs"
              :key="port.id"
              class="port-item"
            >
              <el-input
                v-model="port.name"
                placeholder="端口名称"
                style="width: 120px"
              />
              <el-input
                v-model="port.displayName"
                placeholder="显示名称"
                style="width: 120px"
              />
              <el-select v-model="port.dataType" placeholder="数据类型" style="width: 120px">
                <el-option label="字符串" value="string" />
                <el-option label="数字" value="number" />
                <el-option label="布尔值" value="boolean" />
                <el-option label="数组" value="array" />
                <el-option label="对象" value="object" />
              </el-select>
              <el-checkbox v-model="port.required">必填</el-checkbox>
              <el-button @click="removeInputPort(index)" type="danger" size="small" text>
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
        
        <div class="ports-section">
          <div class="ports-header">
            <h4>输出端口</h4>
            <el-button @click="addOutputPort" type="primary" size="small">
              <el-icon><Plus /></el-icon>
              添加输出
            </el-button>
          </div>
          
          <div class="ports-list">
            <div
              v-for="(port, index) in nodeConfig.outputs"
              :key="port.id"
              class="port-item"
            >
              <el-input
                v-model="port.name"
                placeholder="端口名称"
                style="width: 120px"
              />
              <el-input
                v-model="port.displayName"
                placeholder="显示名称"
                style="width: 120px"
              />
              <el-select v-model="port.dataType" placeholder="数据类型" style="width: 120px">
                <el-option label="字符串" value="string" />
                <el-option label="数字" value="number" />
                <el-option label="布尔值" value="boolean" />
                <el-option label="数组" value="array" />
                <el-option label="对象" value="object" />
              </el-select>
              <el-checkbox v-model="port.multiple">多值</el-checkbox>
              <el-button @click="removeOutputPort(index)" type="danger" size="small" text>
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 高级配置 -->
      <el-tab-pane label="高级配置" name="advanced">
        <el-form :model="nodeConfig.config" label-width="120px">
          <el-form-item label="自动执行">
            <el-switch v-model="nodeConfig.config.autoExecute" />
          </el-form-item>
          
          <el-form-item label="重试次数">
            <el-input-number
              v-model="nodeConfig.config.retryCount"
              :min="0"
              :max="10"
              placeholder="重试次数"
            />
          </el-form-item>
          
          <el-form-item label="超时时间(秒)">
            <el-input-number
              v-model="nodeConfig.config.timeout"
              :min="1"
              placeholder="超时时间"
            />
          </el-form-item>
          
          <el-form-item label="并行执行">
            <el-switch v-model="nodeConfig.config.parallel" />
          </el-form-item>
        </el-form>
        
        <div class="ui-config">
          <h4>UI配置</h4>
          <el-form :model="nodeConfig.ui" label-width="120px">
            <el-form-item label="节点颜色">
              <el-color-picker v-model="nodeConfig.ui.color" />
            </el-form-item>
            
            <el-form-item label="自定义样式">
              <el-input
                v-model="customStyleText"
                type="textarea"
                :rows="4"
                placeholder="请输入JSON格式的样式配置"
                @blur="parseCustomStyle"
              />
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <div class="form-actions">
      <el-button @click="resetForm">重置</el-button>
      <el-button @click="cancelConfig">取消</el-button>
      <el-button type="primary" @click="saveConfig" :loading="saving">
        保存配置
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Upload } from '@element-plus/icons-vue'
import type { Node, NodeType, NodeParameter, NodePort } from '@/types/node-system'

// Props
interface Props {
  node: Node
  mode?: 'overview' | 'detail' | 'edit'
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'edit'
})

// Emits
const emit = defineEmits<{
  'config-changed': [config: Partial<Node>]
  'config-saved': [node: Node]
}>()

// 响应式数据
const activeTab = ref('basic')
const saving = ref(false)
const customStyleText = ref('')

const nodeConfig = reactive<Partial<Node>>({
  name: '',
  displayName: '',
  description: '',
  type: NodeType.DATA_SOURCE,
  position: { x: 0, y: 0 },
  size: { width: 200, height: 120 },
  parameters: [],
  inputs: [],
  outputs: [],
  config: {
    autoExecute: false,
    retryCount: 3,
    timeout: 300,
    parallel: false
  },
  ui: {
    color: '#409EFF',
    customStyle: {}
  }
})

// 计算属性
const isNewNode = computed(() => !props.node.id)

const nodeTypes = computed(() => [
  { label: '配置', value: NodeType.CONFIG },
  { label: '数据源', value: NodeType.DATA_SOURCE },
  { label: '数据处理', value: NodeType.DATA_PROCESSING },
  { label: '策略', value: NodeType.STRATEGY },
  { label: '回测', value: NodeType.BACKTEST },
  { label: '分析', value: NodeType.ANALYSIS },
  { label: '可视化', value: NodeType.VISUALIZATION },
  { label: '导出', value: NodeType.EXPORT }
])

// 方法
const getParameterValueComponent = (type: string) => {
  switch (type) {
    case 'string':
      return 'el-input'
    case 'number':
      return 'el-input-number'
    case 'boolean':
      return 'el-switch'
    case 'select':
      return 'el-select'
    case 'file':
      return 'el-upload'
    default:
      return 'el-input'
  }
}

const getParameterValueProps = (param: NodeParameter) => {
  const props: any = {}
  
  switch (param.type) {
    case 'string':
      props.placeholder = '请输入字符串值'
      break
    case 'number':
      props.placeholder = '请输入数字值'
      if (param.validation?.min !== undefined) props.min = param.validation.min
      if (param.validation?.max !== undefined) props.max = param.validation.max
      break
    case 'boolean':
      props.activeText = '是'
      props.inactiveText = '否'
      break
    case 'select':
      props.placeholder = '请选择选项'
      props.options = param.options || []
      break
  }
  
  return props
}

const addParameter = () => {
  const newParam: NodeParameter = {
    id: `param_${Date.now()}`,
    name: '',
    displayName: '',
    type: 'string',
    value: '',
    required: false,
    description: '',
    validation: {},
    group: 'basic',
    order: nodeConfig.parameters?.length || 0,
    advanced: false,
    hidden: false
  }
  
  if (!nodeConfig.parameters) {
    nodeConfig.parameters = []
  }
  nodeConfig.parameters.push(newParam)
}

const removeParameter = (index: number) => {
  nodeConfig.parameters?.splice(index, 1)
}

const addOption = (param: NodeParameter) => {
  if (!param.options) {
    param.options = []
  }
  param.options.push({
    label: '',
    value: ''
  })
}

const removeOption = (param: NodeParameter, optionIndex: number) => {
  param.options?.splice(optionIndex, 1)
}

const addInputPort = () => {
  const newPort: NodePort = {
    id: `input_${Date.now()}`,
    name: '',
    displayName: '',
    type: 'input',
    dataType: 'string',
    required: false,
    description: ''
  }
  
  if (!nodeConfig.inputs) {
    nodeConfig.inputs = []
  }
  nodeConfig.inputs.push(newPort)
}

const removeInputPort = (index: number) => {
  nodeConfig.inputs?.splice(index, 1)
}

const addOutputPort = () => {
  const newPort: NodePort = {
    id: `output_${Date.now()}`,
    name: '',
    displayName: '',
    type: 'output',
    dataType: 'string',
    required: false,
    description: '',
    multiple: false
  }
  
  if (!nodeConfig.outputs) {
    nodeConfig.outputs = []
  }
  nodeConfig.outputs.push(newPort)
}

const removeOutputPort = (index: number) => {
  nodeConfig.outputs?.splice(index, 1)
}

const importParameters = () => {
  ElMessage.info('导入参数功能开发中...')
}

const parseCustomStyle = () => {
  try {
    if (customStyleText.value.trim()) {
      nodeConfig.ui!.customStyle = JSON.parse(customStyleText.value)
    } else {
      nodeConfig.ui!.customStyle = {}
    }
  } catch (error) {
    ElMessage.error('自定义样式格式错误，请输入有效的JSON格式')
  }
}

const resetForm = () => {
  Object.assign(nodeConfig, {
    name: '',
    displayName: '',
    description: '',
    type: NodeType.DATA_SOURCE,
    position: { x: 0, y: 0 },
    size: { width: 200, height: 120 },
    parameters: [],
    inputs: [],
    outputs: [],
    config: {
      autoExecute: false,
      retryCount: 3,
      timeout: 300,
      parallel: false
    },
    ui: {
      color: '#409EFF',
      customStyle: {}
    }
  })
  customStyleText.value = ''
}

const cancelConfig = () => {
  emit('config-saved', props.node)
}

const saveConfig = async () => {
  try {
    saving.value = true
    
    // 验证必填字段
    if (!nodeConfig.name?.trim()) {
      ElMessage.warning('请输入节点名称')
      return
    }
    
    // 构建完整的节点对象
    const updatedNode: Node = {
      ...props.node,
      ...nodeConfig as Node,
      id: props.node.id || `node_${Date.now()}`,
      status: props.node.status || 'idle',
      permissions: props.node.permissions,
      metadata: {
        ...props.node.metadata,
        updatedAt: new Date().toISOString()
      }
    }
    
    emit('config-changed', nodeConfig)
    emit('config-saved', updatedNode)
    
    ElMessage.success('节点配置保存成功')
  } catch (error) {
    ElMessage.error('节点配置保存失败')
    console.error('节点配置保存错误:', error)
  } finally {
    saving.value = false
  }
}

// 监听器
watch(() => props.node, (newNode) => {
  if (newNode) {
    Object.assign(nodeConfig, newNode)
    if (newNode.ui?.customStyle) {
      customStyleText.value = JSON.stringify(newNode.ui.customStyle, null, 2)
    }
  }
}, { immediate: true, deep: true })

watch(nodeConfig, () => {
  emit('config-changed', nodeConfig)
}, { deep: true })

// 生命周期
onMounted(() => {
  if (props.node) {
    Object.assign(nodeConfig, props.node)
    if (props.node.ui?.customStyle) {
      customStyleText.value = JSON.stringify(props.node.ui.customStyle, null, 2)
    }
  }
})
</script>

<style scoped>
.node-config-form {
  padding: 16px;
}

.parameters-header,
.ports-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.parameters-list,
.ports-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px;
}

.parameter-item,
.port-item {
  padding: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  margin-bottom: 8px;
  background: #fafafa;
}

.parameter-header,
.port-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.parameter-details {
  margin-top: 8px;
}

.parameter-config {
  display: flex;
  gap: 16px;
  margin: 8px 0;
}

.parameter-value,
.parameter-validation,
.parameter-options {
  margin-top: 8px;
}

.value-label,
.validation-label,
.options-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.validation-rules {
  display: flex;
  gap: 8px;
}

.options-list {
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  padding: 8px;
  background: white;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.ports-section {
  margin-bottom: 24px;
}

.ports-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.ui-config {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.ui-config h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.position-inputs,
.size-inputs {
  display: flex;
  gap: 8px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
</style>