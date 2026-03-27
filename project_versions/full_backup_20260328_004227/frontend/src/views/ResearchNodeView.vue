<template>
  <div class="node-view">
    <div class="node-canvas" ref="nodeCanvas">
      <!-- 节点连接线 -->
      <svg class="connections-layer">
        <g v-for="connection in nodeConnections" :key="`${connection.from}-${connection.to}`">
          <path 
            :d="getConnectionPath(connection)"
            :class="getConnectionClass(connection)"
            fill="none"
            stroke-width="2"
          />
        </g>
      </svg>
      
      <!-- 节点 -->
      <div 
        v-for="node in workflowNodes" 
        :key="node.id"
        class="node-element"
        :class="getNodeElementClass(node)"
        :style="getNodeStyle(node)"
        @click="handleNodeClick(node)"
        @dblclick="handleNodeDoubleClick(node)"
        @mousedown="startDragNode(node, $event)"
      >
        <div class="node-header">
          <div class="node-icon">{{ node.icon }}</div>
          <div class="node-status" :class="node.status"></div>
        </div>
        <div class="node-content">
          <h4 class="node-title">{{ node.name }}</h4>
          <p class="node-description">{{ node.description }}</p>
        </div>
        <div class="node-ports">
          <div class="port input"></div>
          <div class="port output"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { NodeStateInfo } from '@/types/node-system'

// Props
interface Props {
  selectedWorkflow: string
  workflowNodes: NodeStateInfo[]
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  nodeClick: [node: NodeStateInfo]
  nodeDoubleClick: [node: NodeStateInfo]
}>()

// 节点连接关系
const nodeConnections = computed(() => {
  // 根据选择的工作流程返回不同的连接关系
  switch (props.selectedWorkflow) {
    case 'data-driven':
      return getDataDrivenConnections()
    case 'ai-assistant':
      return getAIAssistantConnections()
    case 'hybrid':
      return getHybridConnections()
    default:
      return []
  }
})

// 获取数据驱动入口的连接关系
function getDataDrivenConnections() {
  return [
    { from: 'data-acquisition', to: 'data-cleaning', type: 'data' },
    { from: 'data-cleaning', to: 'feature-engineering', type: 'data' },
    { from: 'feature-engineering', to: 'pattern-recognition', type: 'data' },
    { from: 'pattern-recognition', to: 'model-training', type: 'data' }
  ]
}

// 获取AI助手入口的连接关系
function getAIAssistantConnections() {
  return [
    { from: 'ai-strategy-conception', to: 'strategy-development', type: 'control' },
    { from: 'strategy-development', to: 'model-training', type: 'data' }
  ]
}

// 获取混合模式的连接关系
function getHybridConnections() {
  return [
    { from: 'data-acquisition', to: 'data-cleaning', type: 'data' },
    { from: 'data-cleaning', to: 'feature-engineering', type: 'data' },
    { from: 'feature-engineering', to: 'pattern-recognition', type: 'data' },
    { from: 'pattern-recognition', to: 'model-training', type: 'data' },
    { from: 'ai-strategy-conception', to: 'strategy-development', type: 'control' },
    { from: 'strategy-development', to: 'model-training', type: 'data' }
  ]
}

// 节点点击处理
function handleNodeClick(node: NodeStateInfo) {
  emit('nodeClick', node)
}

// 节点双击处理
function handleNodeDoubleClick(node: NodeStateInfo) {
  emit('nodeDoubleClick', node)
}

// 获取节点元素样式类
function getNodeElementClass(node: NodeStateInfo) {
  return [
    `status-${node.status}`,
    { 'can-execute': canExecuteNode(node) }
  ]
}

// 获取节点样式
function getNodeStyle(node: NodeStateInfo) {
  return {
    left: `${node.x}px`,
    top: `${node.y}px`,
    width: `${node.width}px`,
    height: `${node.height}px`
  }
}

// 获取连接路径
function getConnectionPath(connection: any) {
  const fromNode = props.workflowNodes.find(n => n.id === connection.from)
  const toNode = props.workflowNodes.find(n => n.id === connection.to)
  
  if (!fromNode || !toNode) return ''
  
  const x1 = fromNode.x + fromNode.width
  const y1 = fromNode.y + fromNode.height / 2
  const x2 = toNode.x
  const y2 = toNode.y + toNode.height / 2
  
  return `M ${x1} ${y1} C ${x1 + 50} ${y1}, ${x2 - 50} ${y2}, ${x2} ${y2}`
}

// 获取连接样式类
function getConnectionClass(connection: any) {
  return `connection-${connection.type}`
}

// 判断节点是否可以执行
function canExecuteNode(node: NodeStateInfo): boolean {
  // 检查依赖节点是否已完成
  return node.dependencies.every(depId => {
    const depNode = props.workflowNodes.find(n => n.id === depId)
    return depNode && depNode.status === 'completed'
  })
}

// 节点拖拽相关
const nodeCanvas = ref<HTMLElement | null>(null)
let draggedNode: NodeStateInfo | null = null
let dragOffset = { x: 0, y: 0 }

function startDragNode(node: NodeStateInfo, event: MouseEvent) {
  draggedNode = node
  dragOffset.x = event.clientX - node.x
  dragOffset.y = event.clientY - node.y
  
  document.addEventListener('mousemove', onDragNode)
  document.addEventListener('mouseup', stopDragNode)
}

function onDragNode(event: MouseEvent) {
  if (!draggedNode) return
  
  const nodeIndex = props.workflowNodes.findIndex(n => n.id === draggedNode!.id)
  if (nodeIndex !== -1) {
    props.workflowNodes[nodeIndex].x = event.clientX - dragOffset.x
    props.workflowNodes[nodeIndex].y = event.clientY - dragOffset.y
  }
}

function stopDragNode() {
  draggedNode = null
  document.removeEventListener('mousemove', onDragNode)
  document.removeEventListener('mouseup', stopDragNode)
}
</script>

<style scoped>
.node-view {
  flex: 1;
  position: relative;
  overflow: hidden;
  border-radius: 12px;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.node-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: auto;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.connection-data {
  stroke: #3498db;
}

.connection-control {
  stroke: #9b59b6;
  stroke-dasharray: 5, 5;
}

.node-element {
  position: absolute;
  background-color: #fff;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: move;
  transition: all 0.3s ease;
  z-index: 2;
  display: flex;
  flex-direction: column;
}

.node-element:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.node-element.status-completed {
  border-color: #27ae60;
}

.node-element.status-running {
  border-color: #f39c12;
}

.node-element.status-failed {
  border-color: #e74c3c;
}

.node-element.can-execute {
  border-color: #3498db;
}

.node-element .node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.node-element .node-content {
  flex: 1;
}

.node-element .node-title {
  margin: 0 0 5px 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.node-element .node-description {
  margin: 0;
  font-size: 12px;
  color: #7f8c8d;
  line-height: 1.3;
}

.node-ports {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.port {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #3498db;
  pointer-events: all;
}

.port.input {
  left: -5px;
  top: 50%;
  transform: translateY(-50%);
}

.port.output {
  right: -5px;
  top: 50%;
  transform: translateY(-50%);
}
</style>
