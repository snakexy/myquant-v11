<template>
  <Teleport to="body">
    <div v-if="visible" class="node-detail-modal-overlay" @click="handleClose">
    <div :class="['node-detail-modal', { 'node-detail-modal-wide': node?.id === 'data-cleaning' }]" @click.stop>
      <!-- 头部 -->
      <div class="modal-header">
        <h2>{{ node?.icon || '' }} {{ node?.title || '节点详情' }}</h2>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <!-- 内容 -->
      <div class="modal-content">
        <!-- 数据管理节点 - 使用 Display 组件（内部包含模式切换） -->
        <component
          v-if="node?.id === 'data-cleaning'"
          :is="dataManagementDetailComponents['default']"
          v-model="nodeSpecificConfig"
          :nodeData="node"
          :nodes="nodes"
        />

        <!-- 节点特殊配置 -->
        <component
          v-else-if="nodeConfigComponent"
          :is="nodeConfigComponent"
          v-model="nodeSpecificConfig"
          :nodeData="node"
          :nodes="nodes"
        />

        <!-- 通用配置（如果没有特殊配置组件） -->
        <div v-else class="generic-config">
  
          <!-- 配置参数 -->
          <section class="detail-section" v-if="nodeConfig.params && Object.keys(nodeConfig.params).length > 0">
            <h3 class="section-title">配置参数</h3>
            <div class="params-list">
              <div v-for="(param, key) in nodeConfig.params" :key="key" class="param-item">
                <label class="param-label">{{ key }}:</label>
                <div class="param-control">
                  <!-- 根据参数类型使用不同的控件 -->
                  <input
                    v-if="typeof param === 'string'"
                    v-model="nodeConfig.params[key]"
                    class="quant-input"
                    :placeholder="`请输入${key}`"
                  />
                  <input
                    v-else-if="typeof param === 'number'"
                    v-model="nodeConfig.params[key]"
                    type="number"
                    class="quant-input"
                    :placeholder="`请输入${key}`"
                  />
                  <label v-else-if="typeof param === 'boolean'" class="checkbox-wrapper">
                    <input
                      type="checkbox"
                      v-model="nodeConfig.params[key]"
                    />
                    {{ key }}
                  </label>
                  <!-- 可以为对象或数组的类型 -->
                  <input
                    v-else
                    v-model="nodeConfig.params[key]"
                    class="quant-input"
                    :placeholder="`请输入${key}(JSON格式)`"
                  />
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>

      <!-- 底部 -->
      <div class="modal-footer">
        <button class="btn-cancel" @click="handleClose">关闭</button>
        <button class="btn-confirm" @click="handleApplyChanges">
          应用更改
        </button>
      </div>
    </div>
  </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, markRaw } from 'vue'
import type { Node } from '../../views/NodeWorkflow.vue'
// 从研究阶段节点模块导入配置组件
import StockSelectionConfig from '../../research-nodes/StockSelectionNode/Config.vue'
import IndexSelectionConfig from '../../research-nodes/IndexSelectionNode/Config.vue'
import DataManagementDisplay from '../../research-nodes/DataCleaningNode/Display.vue'
import FactorEngineConfig from '../../research-nodes/FactorEngineNode/Config.vue'

// 节点配置组件映射（用于非 data-cleaning 节点）
const nodeConfigComponents = {
  'stock-selection': markRaw(StockSelectionConfig),
  'index-selection': markRaw(IndexSelectionConfig),
  'factor-engine': markRaw(FactorEngineConfig),
  // 注意：data-cleaning 使用 DataManagementDisplay（包含模式切换和报告/管理界面）
  // 可以在这里添加更多节点的配置组件
}

// 数据管理详情组件映射
const dataManagementDetailComponents = {
  'default': markRaw(DataManagementDisplay),
}

interface Props {
  visible?: boolean
  node?: Node | null
  connections?: Array<{ from: string; to: string; toInputId?: string; enabled?: boolean }>
  nodes?: Node[]  // 🔧 添加所有节点数据
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  node: null,
  connections: () => [],
  nodes: () => []  // 🔧 添加默认值
})

const emit = defineEmits<{
  'update:visible': [visible: boolean]
  'update-node': [nodeId: string, config: any]
}>()

// 节点配置
const nodeConfig = ref({
  params: {} as Record<string, any>
})

// 节点特定配置
const nodeSpecificConfig = ref<any>({})

// 配置标题映射
const configTitles = {
  'stock-selection': '股票选择',
  'index-selection': '指数选择',
  'data-cleaning': '数据管理',
  'factor-engine': '因子计算引擎',
  'feature-engineering': '特征工程配置',
  'pattern-recognition': '模式识别配置',
  'model-training': '模型训练配置',
  'ai-assistant': 'AI助手配置',
  'strategy-conception': '策略构思配置',
  'preliminary-validation': '验证配置'
}

// 模拟日志数据
const nodeLogs = ref([
  {
    timestamp: Date.now() - 60000,
    level: 'info',
    message: '节点初始化完成'
  },
  {
    timestamp: Date.now() - 30000,
    level: 'success',
    message: '数据处理成功'
  }
])

// 监听节点变化，更新配置
watch(() => props.node, (newNode) => {
  console.log('[NodeDetailModal] props.node 变化:', newNode?.id, newNode)
  if (newNode) {
    nodeConfig.value = {
      params: newNode.params || {}
    }

    // 根据节点类型初始化特定配置
    if (newNode.id === 'stock-selection') {
      // 初始化股票选择节点配置，保留之前的选择
      nodeSpecificConfig.value = {
        stockCode: newNode.params?.stockCode || '', // 保留之前输入的股票代码
        timeRange: newNode.params?.timeRange || '1Y',
        startDate: newNode.params?.startDate || '',
        endDate: newNode.params?.endDate || '',
        frequency: newNode.params?.frequency || 'daily',
        includeDividends: newNode.params?.includeDividends ?? false,
        adjustPrices: newNode.params?.adjustPrices ?? true,
        includeVolume: newNode.params?.includeVolume ?? true,
        marketType: newNode.params?.marketType || 'A股',
        stockType: newNode.params?.stockType || 'all',
        sortBy: newNode.params?.sortBy || 'code',
        maxStocks: newNode.params?.maxStocks || 50,
        ...newNode.params
      }
    } else if (newNode.id === 'index-selection') {
      // 初始化指数选择节点配置
      nodeSpecificConfig.value = {
        indexCode: newNode.params?.indexCode || '000001.SH',
        timeRange: newNode.params?.timeRange || '3M',
        startDate: newNode.params?.startDate || '',
        endDate: newNode.params?.endDate || '',
        frequency: newNode.params?.frequency || 'daily',
        frequencies: newNode.params?.frequencies || ['daily'], // 🔧 添加 frequencies 字段
        forwardAdjust: newNode.params?.forwardAdjust ?? false,
        ...newNode.params
      }
    } else if (newNode.id === 'data-cleaning') {
      // 🔧 添加日志
      console.log('[NodeDetailModal] data-cleaning 节点初始化')
      console.log('[NodeDetailModal] newNode.data:', newNode.data)
      console.log('[NodeDetailModal] newNode.data?.metadata:', newNode.data?.metadata)
      console.log('[NodeDetailModal] newNode.params:', newNode.params)
      console.log('[NodeDetailModal] newNode (完整):', newNode)

      // 初始化数据管理节点配置
      nodeSpecificConfig.value = {
        mode: newNode.params?.mode || 'cleaning',
        // 数据清洗配置
        qlibDataPath: newNode.params?.qlibDataPath || 'E:\\MyQuant_v8.0.1\\data\\qlib_data',
        frequency: newNode.params?.frequency || 'daily',
        frequencies: newNode.params?.frequencies || ['daily'],
        dropMissing: newNode.params?.dropMissing ?? true,
        maxMissingRatio: newNode.params?.maxMissingRatio ?? 0.3,
        forwardFill: newNode.params?.forwardFill ?? true,
        handleOutliers: newNode.params?.handleOutliers ?? false,
        outlierMethod: newNode.params?.outlierMethod || 'clip',
        normalize: newNode.params?.normalize ?? false,
        includeIndex: newNode.params?.includeIndex ?? true,
        // 🔧 已选标的（从 metadata 中恢复）
        selectedStockCodes: newNode.data?.metadata?.selectedStockCodes || [],
        selectedStockCount: newNode.data?.metadata?.selectedStockCount || 0,
        // 数据库管理配置
        database: {
          autoRefresh: newNode.params?.database?.autoRefresh ?? false,
          showNeedsUpdateOnly: newNode.params?.database?.showNeedsUpdateOnly ?? false,
          sortBy: newNode.params?.database?.sortBy || 'code',
          sortOrder: newNode.params?.database?.sortOrder || 'asc',
          expiryThreshold: newNode.params?.database?.expiryThreshold ?? 7,
          batchUpdateLimit: newNode.params?.database?.batchUpdateLimit ?? 10
        },
        ...newNode.params
      }

      console.log('[NodeDetailModal] 初始化后的 nodeSpecificConfig.value.selectedStockCodes:', nodeSpecificConfig.value.selectedStockCodes)
      console.log('[NodeDetailModal] 初始化后的 nodeSpecificConfig.value.selectedStockCount:', nodeSpecificConfig.value.selectedStockCount)
    } else if (newNode.id === 'factor-engine') {
      // 初始化因子计算引擎节点配置
      nodeSpecificConfig.value = {
        factorTemplate: newNode.params?.factorTemplate || 'alpha158',
        alpha158: newNode.params?.alpha158 ?? true,
        alpha360: newNode.params?.alpha360 ?? false,
        customFactors: newNode.params?.customFactors || [],
        normalize: newNode.params?.normalize ?? true,
        neutralize: newNode.params?.neutralize ?? true,
        frequency: newNode.params?.frequency || 'daily',
        ...newNode.params
      }
    } else {
      // 其他节点使用默认配置
      nodeSpecificConfig.value = { ...newNode.params }
    }
  }
}, { immediate: true })

// 监听 visible 变化
watch(() => props.visible, (newVisible, oldVisible) => {
  console.log('[NodeDetailModal] visible 变化:', { oldVisible, newVisible, nodeId: props.node?.id })
  console.log('[NodeDetailModal] props.nodes:', props.nodes)

  // 🔧 当弹窗关闭时（从 true 变为 false），触发 update-node 事件以更新连线状态
  if (oldVisible === true && newVisible === false && props.node) {
    console.log('[NodeDetailModal] 弹窗关闭，触发 update-node 事件')
    emit('update-node', props.node.id, {
      inputs: props.node.inputs
    })
  }
}, { immediate: true })

// 动态获取节点配置组件
const nodeConfigComponent = computed(() => {
  if (!props.node) return null

  return nodeConfigComponents[props.node.id as keyof typeof nodeConfigComponents] || null
})

// 动态获取配置标题
const configTitle = computed(() => {
  return props.node ? configTitles[props.node.id as keyof typeof configTitles] || '节点配置' : '节点配置'
})

// 获取状态类型
const getStatusType = (status?: string) => {
  switch (status) {
    case 'RUNNING': return 'info'
    case 'COMPLETED': return 'success'
    case 'FAILED': return 'error'
    case 'PAUSED': return 'warning'
    default: return 'default'
  }
}

// 获取状态文本
const getStatusText = (status?: string) => {
  switch (status) {
    case 'IDLE': return '空闲'
    case 'RUNNING': return '运行中'
    case 'COMPLETED': return '已完成'
    case 'FAILED': return '失败'
    case 'PAUSED': return '暂停'
    case 'DISABLED': return '禁用'
    default: return '未知'
  }
}

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 应用更改
const handleApplyChanges = () => {
  if (props.node) {
    const updateConfig: any = {
      params: { ...nodeConfig.value.params }
    }

    // 保存节点特定配置
    if (props.node.id === 'stock-selection') {
      // 股票选择节点需要特殊处理：将stockCode转换为symbols数组
      const stockConfig = { ...nodeSpecificConfig.value }

      // 如果有stockCode，将其转换为symbols数组
      if (stockConfig.stockCode) {
        stockConfig.symbols = stockConfig.stockCode.split(/[,，]/)
          .map(code => code.trim())
          .filter(code => code)
      }

      updateConfig.params = { ...updateConfig.params, ...stockConfig }
    } else if (props.node.id === 'index-selection') {
      // 指数选择节点配置
      const indexConfig = { ...nodeSpecificConfig.value }
      updateConfig.params = { ...updateConfig.params, ...indexConfig }
    } else if (props.node.id === 'data-cleaning' || props.node.id === 'data-management') {
      // 数据清洗/数据管理节点配置
      const managementConfig = { ...nodeSpecificConfig.value }
      updateConfig.params = { ...updateConfig.params, ...managementConfig }
    } else if (props.node.id === 'factor-engine') {
      // 因子计算引擎节点配置
      const factorConfig = { ...nodeSpecificConfig.value }
      updateConfig.params = { ...updateConfig.params, ...factorConfig }
    } else {
      // 其他节点
      updateConfig.params = { ...updateConfig.params, ...nodeSpecificConfig.value }
    }

    emit('update-node', props.node.id, updateConfig)
  }
  handleClose()
}

// 关闭弹窗
const handleClose = () => {
  emit('update:visible', false)
}

// 🔧 监听 nodeSpecificConfig 的变化，实时更新节点数据（特别是 selectedStockCount）
watch(() => nodeSpecificConfig.value.selectedStockCount, (newCount) => {
  if (props.node && newCount !== undefined) {
    console.log('[NodeDetailModal] selectedStockCount 变化:', newCount)

    // 实时更新节点配置，不需要用户点击"应用更改"
    const updateConfig: any = {
      params: {
        selectedStockCount: newCount,
        selectedStockCodes: nodeSpecificConfig.value.selectedStockCodes
      }
    }

    // 触发更新节点配置
    emit('update-node', props.node.id, updateConfig)
  }
}, { deep: true })

// 🔧 监听 frequencies 的变化，实时更新节点数据
watch(() => nodeSpecificConfig.value.frequencies, (newFrequencies) => {
  if (props.node && newFrequencies && newFrequencies.length > 0) {
    console.log('[NodeDetailModal] frequencies 变化:', newFrequencies)

    // 实时更新节点配置，不需要用户点击"应用更改"
    const updateConfig: any = {
      params: {
        frequencies: newFrequencies
      }
    }

    // 触发更新节点配置
    emit('update-node', props.node.id, updateConfig)
  }
}, { deep: true })
</script>

<style lang="scss" scoped>
.node-detail-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.node-detail-modal {
  background: #1a1a2e;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  max-width: 800px;
  width: 90vw;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  // 数据清洗节点使用更宽的弹窗
  &.node-detail-modal-wide {
    max-width: 1400px;
    width: 95vw;
    max-height: 90vh;
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);

  h2 {
    margin: 0;
    color: #fff;
    font-size: 1.2rem;
  }
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
}

.modal-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  color: #fff;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-cancel,
.btn-confirm {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
}

.btn-confirm {
  background: #8b5cf6;
  color: #fff;

  &:hover {
    background: #7c3aed;
  }
}

.detail-section {
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;

  label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
    font-weight: 500;
  }

  span {
    font-size: 14px;
  }
}

.quant-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 8px 12px;
  color: #fff;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: #8b5cf6;
    background: rgba(255, 255, 255, 0.08);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;

  &.status-default {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.6);
  }

  &.status-success {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
  }

  &.status-info {
    background: rgba(59, 130, 246, 0.2);
    color: #3b82f6;
  }

  &.status-warning {
    background: rgba(251, 191, 36, 0.2);
    color: #fbbf24;
  }

  &.status-error {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }
}

.params-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 12px;

  .param-label {
    min-width: 100px;
    font-size: 14px;
    font-weight: 500;
  }

  .param-control {
    flex: 1;
  }
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.ports-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.port-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  transition: background-color 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
  }
}

.port-info {
  display: flex;
  align-items: center;
  gap: 8px;

  .port-id {
    font-family: monospace;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
    background: rgba(255, 255, 255, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
  }

  .port-label {
    font-size: 14px;
  }
}

.connections-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.connection-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;

  .connection-info {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;

    .connection-from,
    .connection-to {
      color: #fff;
    }

    .connection-arrow {
      color: rgba(255, 255, 255, 0.6);
      font-size: 16px;
    }
  }
}

.result-content {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 12px;
  max-height: 200px;
  overflow: auto;

  pre {
    margin: 0;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.5;
    color: #fff;
  }
}

.logs-container {
  max-height: 150px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 8px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
  font-size: 12px;
  line-height: 1.4;

  &:not(:last-child) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 6px;
    margin-bottom: 2px;
  }

  .log-time {
    color: rgba(255, 255, 255, 0.6);
    font-family: monospace;
    min-width: 60px;
  }

  .log-level {
    font-weight: 600;
    min-width: 50px;
    text-align: center;

    &--INFO {
      color: #3b82f6;
    }

    &--SUCCESS {
      color: #22c55e;
    }

    &--WARNING {
      color: #fbbf24;
    }

    &--ERROR {
      color: #ef4444;
    }
  }

  .log-message {
    color: #fff;
    flex: 1;
  }
}
</style>