<template>
  <div class="architecture-graph">
    <!-- 图表工具栏 -->
    <div class="graph-toolbar">
      <div class="toolbar-left">
        <n-button-group size="small">
          <n-button @click="resetView" title="重置视图">
            <template #icon>
              <n-icon :component="HomeOutline" />
            </template>
          </n-button>
          <n-button @click="fitToScreen" title="适应屏幕">
            <template #icon>
              <n-icon :component="ExpandOutline" />
            </template>
          </n-button>
          <n-button @click="toggleFullscreen" title="全屏">
            <template #icon>
              <n-icon :component="ResizeOutline" />
            </template>
          </n-button>
        </n-button-group>
        
        <n-divider vertical />
        
        <n-button-group size="small">
          <n-button @click="zoomIn" title="放大">
            <template #icon>
              <n-icon :component="AddOutline" />
            </template>
          </n-button>
          <n-button @click="zoomOut" title="缩小">
            <template #icon>
              <n-icon :component="RemoveOutline" />
            </template>
          </n-button>
        </n-button-group>
      </div>
      
      <div class="toolbar-center">
        <n-select
          v-model:value="selectedLayout"
          :options="layoutOptions"
          size="small"
          style="width: 120px"
          @update:value="changeLayout"
        />
      </div>
      
      <div class="toolbar-right">
        <n-button-group size="small">
          <n-button @click="exportImage" title="导出图片">
            <template #icon>
              <n-icon :component="DownloadOutline" />
            </template>
          </n-button>
          <n-button @click="toggleAnimation" :type="animationEnabled ? 'primary' : 'default'" title="动画开关">
            <template #icon>
              <n-icon :component="PlayOutline" />
            </template>
          </n-button>
          <n-button @click="showSettings = true" title="设置">
            <template #icon>
              <n-icon :component="SettingsOutline" />
            </template>
          </n-button>
        </n-button-group>
      </div>
    </div>

    <!-- 图表容器 -->
    <div class="graph-container" ref="graphContainer">
      <div ref="networkContainer" class="network-container"></div>
      
      <!-- 节点信息悬浮框 -->
      <div
        v-if="hoveredNode"
        class="node-tooltip"
        :style="{ left: tooltipPosition.x + 'px', top: tooltipPosition.y + 'px' }"
      >
        <div class="tooltip-header">
          <span class="node-title">{{ hoveredNode.label }}</span>
          <span class="node-type">{{ getNodeTypeLabel(hoveredNode.type) }}</span>
        </div>
        <div class="tooltip-content">
          <div class="tooltip-row">
            <span class="label">状态:</span>
            <span class="value" :class="getStatusClass(hoveredNode.status)">
              {{ getStatusLabel(hoveredNode.status) }}
            </span>
          </div>
          <div class="tooltip-row" v-if="hoveredNode.description">
            <span class="label">描述:</span>
            <span class="value">{{ hoveredNode.description }}</span>
          </div>
          <div class="tooltip-row" v-if="hoveredNode.metrics">
            <span class="label">性能:</span>
            <span class="value">{{ hoveredNode.metrics }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图例 -->
    <div class="graph-legend">
      <div class="legend-title">节点类型</div>
      <div class="legend-items">
        <div class="legend-item" v-for="item in nodeTypeLegend" :key="item.type">
          <div class="legend-icon" :style="{ backgroundColor: item.color }"></div>
          <span class="legend-label">{{ item.label }}</span>
        </div>
      </div>
    </div>

    <!-- 设置弹窗 -->
    <n-modal v-model:show="showSettings" preset="card" style="max-width: 500px;" title="图表设置">
      <div class="settings-form">
        <n-form :model="graphSettings" label-placement="left" label-width="100">
          <n-form-item label="节点大小">
            <n-slider v-model:value="graphSettings.nodeSize" :min="10" :max="50" />
          </n-form-item>
          <n-form-item label="边宽度">
            <n-slider v-model:value="graphSettings.edgeWidth" :min="1" :max="10" />
          </n-form-item>
          <n-form-item label="动画速度">
            <n-slider v-model:value="graphSettings.animationSpeed" :min="0.5" :max="3" :step="0.1" />
          </n-form-item>
          <n-form-item label="显示标签">
            <n-switch v-model:value="graphSettings.showLabels" />
          </n-form-item>
          <n-form-item label="显示指标">
            <n-switch v-model:value="graphSettings.showMetrics" />
          </n-form-item>
          <n-form-item label="物理模拟">
            <n-switch v-model:value="graphSettings.physicsEnabled" />
          </n-form-item>
        </n-form>
      </div>
      <template #footer>
        <n-space justify="end">
          <n-button @click="resetSettings">重置</n-button>
          <n-button type="primary" @click="applySettings">应用</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { Network, DataSet, Edge, Node, Options } from 'vis-network/standalone'
import {
  HomeOutline,
  ExpandOutline,
  ResizeOutline,
  AddOutline,
  RemoveOutline,
  DownloadOutline,
  PlayOutline,
  SettingsOutline
} from '@vicons/ionicons5'

// 组件属性定义
interface Props {
  data?: {
    nodes: any[]
    edges: any[]
  }
  height?: number
  functionId?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: 500,
  functionId: ''
})

// 消息提示
const message = useMessage()

// DOM引用
const graphContainer = ref<HTMLElement | null>(null)
const networkContainer = ref<HTMLElement | null>(null)

// 响应式数据
let network: Network | null = null
const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])
const selectedLayout = ref('hierarchical')
const animationEnabled = ref(true)
const showSettings = ref(false)
const hoveredNode = ref<any>(null)
const tooltipPosition = reactive({ x: 0, y: 0 })

// 图表设置
const graphSettings = reactive({
  nodeSize: 25,
  edgeWidth: 2,
  animationSpeed: 1,
  showLabels: true,
  showMetrics: true,
  physicsEnabled: true
})

// 布局选项
const layoutOptions = [
  { label: '层次布局', value: 'hierarchical' },
  { label: '力导向布局', value: 'physics' },
  { label: '环形布局', value: 'circular' },
  { label: '网格布局', value: 'grid' }
]

// 节点类型图例
const nodeTypeLegend = [
  { type: 'data', label: '数据源', color: '#e65100' },
  { type: 'processor', label: '处理器', color: '#01579b' },
  { type: 'model', label: '模型', color: '#1b5e20' },
  { type: 'strategy', label: '策略', color: '#4a148c' },
  { type: 'output', label: '输出', color: '#00695c' }
]

// 生成示例数据
const generateSampleData = () => {
  const sampleNodes: Node[] = [
    { id: 1, label: '数据源', type: 'data', status: 'active', description: '股票数据获取', group: 'data' },
    { id: 2, label: '数据清洗', type: 'processor', status: 'active', description: '数据预处理', group: 'processor' },
    { id: 3, label: '特征工程', type: 'processor', status: 'active', description: '技术指标计算', group: 'processor' },
    { id: 4, label: 'LSTM模型', type: 'model', status: 'training', description: '深度学习预测模型', group: 'model' },
    { id: 5, label: '策略引擎', type: 'strategy', status: 'active', description: '交易策略执行', group: 'strategy' },
    { id: 6, label: '风险管理', type: 'strategy', status: 'active', description: '风险控制模块', group: 'strategy' },
    { id: 7, label: '交易输出', type: 'output', status: 'active', description: '交易信号输出', group: 'output' }
  ]

  const sampleEdges: Edge[] = [
    { from: 1, to: 2, label: '原始数据' },
    { from: 2, to: 3, label: '清洗数据' },
    { from: 3, to: 4, label: '特征数据' },
    { from: 4, to: 5, label: '预测结果' },
    { from: 5, to: 6, label: '策略信号' },
    { from: 6, to: 7, label: '风险调整' },
    { from: 5, to: 7, label: '直接输出', dashes: true }
  ]

  return { nodes: sampleNodes, edges: sampleEdges }
}

// 初始化网络图
const initNetwork = () => {
  if (!networkContainer.value) return

  // 获取数据
  let graphData
  if (props.data && props.data.nodes && props.data.edges) {
    graphData = props.data
  } else {
    graphData = generateSampleData()
  }

  // 处理节点数据
  nodes.value = graphData.nodes.map(node => ({
    ...node,
    shape: getNodeShape(node.type),
    color: getNodeColor(node.type, node.status),
    font: {
      color: '#ffffff',
      size: graphSettings.showLabels ? 12 : 0
    },
    size: graphSettings.nodeSize,
    borderWidth: 2,
    borderWidthSelected: 3
  }))

  // 处理边数据
  edges.value = graphData.edges.map(edge => ({
    ...edge,
    width: graphSettings.edgeWidth,
    color: { color: 'rgba(255, 255, 255, 0.6)', highlight: '#2563eb' },
    font: {
      color: '#ffffff',
      size: 10,
      strokeWidth: 3,
      strokeColor: 'rgba(0, 0, 0, 0.5)'
    },
    smooth: {
      type: 'curvedCW',
      roundness: 0.2
    }
  }))

  // 网络配置
  const options: Options = {
    nodes: {
      shape: 'dot',
      scaling: {
        min: 20,
        max: 40
      },
      font: {
        color: '#ffffff',
        size: 12,
        face: 'Inter'
      },
      borderWidth: 2,
      shadow: true
    },
    edges: {
      width: 2,
      color: {
        color: 'rgba(255, 255, 255, 0.6)',
        highlight: '#2563eb',
        hover: '#3b82f6'
      },
      smooth: {
        type: 'curvedCW',
        roundness: 0.2
      },
      shadow: true
    },
    physics: {
      enabled: graphSettings.physicsEnabled,
      barnesHut: {
        gravitationalConstant: -2000,
        centralGravity: 0.3,
        springLength: 120,
        springConstant: 0.04,
        damping: 0.09
      },
      stabilization: {
        enabled: true,
        iterations: 200,
        updateInterval: 25
      }
    },
    interaction: {
      hover: true,
      tooltipDelay: 200,
      zoomView: true,
      dragView: true
    },
    layout: getLayoutOptions(selectedLayout.value)
  }

  // 创建网络
  const data = { nodes: new DataSet(nodes.value), edges: new DataSet(edges.value) }
  network = new Network(networkContainer.value, data, options)

  // 绑定事件
  network.on('hoverNode', (params) => {
    const nodeId = params.node
    const node = nodes.value.find(n => n.id === nodeId)
    if (node) {
      hoveredNode.value = node
      tooltipPosition.x = params.event.pageX + 10
      tooltipPosition.y = params.event.pageY + 10
    }
  })

  network.on('blurNode', () => {
    hoveredNode.value = null
  })

  network.on('click', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = nodes.value.find(n => n.id === nodeId)
      if (node) {
        handleNodeClick(node)
      }
    }
  })

  // 启动动画
  if (animationEnabled.value) {
    startDataFlowAnimation()
  }
}

// 获取节点形状
const getNodeShape = (type: string) => {
  const shapes = {
    data: 'database',
    processor: 'box',
    model: 'diamond',
    strategy: 'hexagon',
    output: 'circle'
  }
  return shapes[type] || 'dot'
}

// 获取节点颜色
const getNodeColor = (type: string, status: string) => {
  const typeColors = {
    data: '#e65100',
    processor: '#01579b',
    model: '#1b5e20',
    strategy: '#4a148c',
    output: '#00695c'
  }

  const statusColors = {
    active: '',
    inactive: 'rgba(128, 128, 128, 0.5)',
    error: 'rgba(239, 68, 68, 0.8)',
    training: 'rgba(245, 158, 11, 0.8)'
  }

  const baseColor = typeColors[type] || '#666666'
  const statusColor = statusColors[status] || ''

  if (statusColor) {
    return {
      background: statusColor,
      border: baseColor,
      highlight: {
        background: baseColor,
        border: '#ffffff'
      }
    }
  }

  return {
    background: baseColor,
    border: '#ffffff',
    highlight: {
      background: baseColor,
      border: '#ffffff'
    }
  }
}

// 获取布局选项
const getLayoutOptions = (layout: string) => {
  switch (layout) {
    case 'hierarchical':
      return {
        hierarchical: {
          direction: 'UD',
          sortMethod: 'directed',
          levelSeparation: 100,
          nodeSpacing: 100,
          treeSpacing: 200
        }
      }
    case 'circular':
      return {
        improvedLayout: true
      }
    case 'grid':
      return {
        randomSeed: 2
      }
    default:
      return {
        randomSeed: 2
      }
  }
}

// 处理节点点击
const handleNodeClick = (node: any) => {
  console.log('Node clicked:', node)
  // 这里可以添加节点点击后的处理逻辑
  // 比如显示详细信息、进入配置页面等
}

// 获取节点类型标签
const getNodeTypeLabel = (type: string) => {
  const labels = {
    data: '数据源',
    processor: '处理器',
    model: '模型',
    strategy: '策略',
    output: '输出'
  }
  return labels[type] || '未知'
}

// 获取状态标签
const getStatusLabel = (status: string) => {
  const labels = {
    active: '运行中',
    inactive: '已停止',
    error: '错误',
    training: '训练中'
  }
  return labels[status] || '未知'
}

// 获取状态样式类
const getStatusClass = (status: string) => {
  return `status-${status}`
}

// 数据流动画
const startDataFlowAnimation = () => {
  if (!network || !animationEnabled.value) return

  // 创建数据流动画效果
  setInterval(() => {
    if (!network || !animationEnabled.value) return

    // 随机选择一条边进行动画
    const edgeIds = network.getEdgeIds()
    if (edgeIds.length > 0) {
      const randomEdge = edgeIds[Math.floor(Math.random() * edgeIds.length)]
      network.selectEdges([randomEdge])
      
      setTimeout(() => {
        if (network) {
          network.unselectAll()
        }
      }, 1000)
    }
  }, 3000)
}

// 工具栏功能
const resetView = () => {
  if (network) {
    network.fit({
      animation: {
        duration: 1000,
        easingFunction: 'easeInOutQuad'
      }
    })
  }
}

const fitToScreen = () => {
  if (network) {
    network.fit({
      animation: {
        duration: 1000,
        easingFunction: 'easeInOutQuad'
      }
    })
  }
}

const toggleFullscreen = () => {
  if (graphContainer.value) {
    if (!document.fullscreenElement) {
      graphContainer.value.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
  }
}

const zoomIn = () => {
  if (network) {
    const scale = network.getScale()
    network.moveTo({ scale: scale * 1.2 })
  }
}

const zoomOut = () => {
  if (network) {
    const scale = network.getScale()
    network.moveTo({ scale: scale * 0.8 })
  }
}

const changeLayout = (layout: string) => {
  if (network) {
    network.setOptions({
      layout: getLayoutOptions(layout)
    })
  }
}

const exportImage = () => {
  if (network) {
    const canvas = network.canvas.frame.canvas
    const link = document.createElement('a')
    link.download = 'architecture-graph.png'
    link.href = canvas.toDataURL()
    link.click()
    message.success('图表已导出')
  }
}

const toggleAnimation = () => {
  animationEnabled.value = !animationEnabled.value
  if (animationEnabled.value) {
    startDataFlowAnimation()
  }
}

// 设置功能
const applySettings = () => {
  if (network) {
    network.setOptions({
      nodes: {
        size: graphSettings.nodeSize,
        font: {
          size: graphSettings.showLabels ? 12 : 0
        }
      },
      edges: {
        width: graphSettings.edgeWidth
      },
      physics: {
        enabled: graphSettings.physicsEnabled
      }
    })
  }
  showSettings.value = false
  message.success('设置已应用')
}

const resetSettings = () => {
  graphSettings.nodeSize = 25
  graphSettings.edgeWidth = 2
  graphSettings.animationSpeed = 1
  graphSettings.showLabels = true
  graphSettings.showMetrics = true
  graphSettings.physicsEnabled = true
  applySettings()
}

// 监听数据变化
watch(() => props.data, (newData) => {
  if (newData && network) {
    // 更新网络数据
    initNetwork()
  }
}, { deep: true })

// 监听高度变化
watch(() => props.height, () => {
  if (network) {
    nextTick(() => {
      network.redraw()
      network.fit()
    })
  }
})

// 生命周期
onMounted(() => {
  nextTick(() => {
    initNetwork()
  })
})

onUnmounted(() => {
  if (network) {
    network.destroy()
    network = null
  }
})
</script>

<style lang="scss" scoped>
.architecture-graph {
  position: relative;
  width: 100%;
  height: v-bind('props.height + "px"');
  background: var(--bg-deep);
  border-radius: var(--border-radius-medium);
  overflow: hidden;
  display: flex;
  flex-direction: column;

  .graph-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-2) var(--spacing-3);
    background: rgba(0, 0, 0, 0.3);
    border-bottom: 1px solid var(--border-color);
    flex-shrink: 0;

    .toolbar-left,
    .toolbar-right {
      display: flex;
      align-items: center;
      gap: var(--spacing-2);
    }

    .toolbar-center {
      display: flex;
      align-items: center;
    }
  }

  .graph-container {
    flex: 1;
    position: relative;
    overflow: hidden;

    .network-container {
      width: 100%;
      height: 100%;
    }

    .node-tooltip {
      position: fixed;
      background: rgba(0, 0, 0, 0.9);
      color: var(--text-primary);
      padding: var(--spacing-2) var(--spacing-3);
      border-radius: var(--border-radius-sm)all;
      font-size: var(--font-size-sm);
      pointer-events: none;
      z-index: 1000;
      backdrop-filter: blur(10px);
      border: 1px solid var(--border-color);
      max-width: 250px;

      .tooltip-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-1);
        border-bottom: 1px solid var(--border-color);
        padding-bottom: var(--spacing-1);

        .node-title {
          font-weight: 600;
          color: var(--text-primary);
        }

        .node-type {
          font-size: var(--font-size-xs);
          color: var(--text-secondary);
          background: rgba(255, 255, 255, 0.1);
          padding: 2px 6px;
          border-radius: var(--border-radius-sm)all;
        }
      }

      .tooltip-content {
        .tooltip-row {
          display: flex;
          margin-bottom: var(--spacing-1);
          font-size: var(--font-size-xs);

          &:last-child {
            margin-bottom: 0;
          }

          .label {
            color: var(--text-secondary);
            margin-right: var(--spacing-2);
            min-width: 40px;
          }

          .value {
            color: var(--text-primary);
            flex: 1;

            &.status-active {
              color: var(--success-color);
            }

            &.status-inactive {
              color: var(--text-secondary);
            }

            &.status-error {
              color: var(--danger-color);
            }

            &.status-training {
              color: var(--warning-color);
            }
          }
        }
      }
    }
  }

  .graph-legend {
    position: absolute;
    bottom: var(--spacing-3);
    right: var(--spacing-3);
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm)all;
    padding: var(--spacing-2);
    z-index: 100;

    .legend-title {
      font-size: var(--font-size-xs);
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: var(--spacing-1);
    }

    .legend-items {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-1);

      .legend-item {
        display: flex;
        align-items: center;
        gap: var(--spacing-1);

        .legend-icon {
          width: 12px;
          height: 12px;
          border-radius: 2px;
        }

        .legend-label {
          font-size: var(--font-size-xs);
          color: var(--text-secondary);
        }
      }
    }
  }

  .settings-form {
    padding: var(--spacing-2);
  }
}

// 全屏样式
:deep(.vis-network) {
  outline: none;
}

:deep(.vis-tooltip) {
  display: none !important;
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