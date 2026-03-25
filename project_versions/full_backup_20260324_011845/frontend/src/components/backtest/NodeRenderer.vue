<template>
  <g 
    class="node-renderer"
    :class="{
      'node-selected': selected,
      'node-highlighted': highlighted,
      'node-dragging': isDragging,
      [`node-${node.status.toLowerCase()}`]: true
    }"
    :transform="`translate(${node.position.x}, ${node.position.y})`"
    @mousedown="handleMouseDown"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    @click="handleClick"
    @dblclick="handleDoubleClick"
    @contextmenu.prevent="handleRightClick"
  >
    <!-- 节点阴影 -->
    <rect
      class="node-shadow"
      :x="2"
      :y="2"
      :width="node.size.width"
      :height="node.size.height"
      :rx="borderRadius"
      fill="#000000"
      fill-opacity="0.1"
    />
    
    <!-- 节点背景 -->
    <rect
      class="node-background"
      :width="node.size.width"
      :height="node.size.height"
      :rx="borderRadius"
      :fill="backgroundColor"
      :stroke="borderColor"
      :stroke-width="borderWidth"
      :stroke-dasharray="isDragging ? '5,5' : 'none'"
    />
    
    <!-- 节点头部 -->
    <rect
      class="node-header"
      :width="node.size.width"
      :height="headerHeight"
      :rx="borderRadius"
      :fill="headerColor"
    />
    
    <!-- 节点图标 -->
    <foreignObject
      :x="iconPadding"
      :y="iconPadding"
      :width="iconSize"
      :height="iconSize"
    >
      <div class="node-icon">
        <el-icon :size="iconSize" :color="iconColor">
          <component :is="nodeIcon" />
        </el-icon>
      </div>
    </foreignObject>
    
    <!-- 节点标题 -->
    <text
      class="node-title"
      :x="iconSize + iconPadding * 2"
      :y="headerHeight / 2"
      dominant-baseline="middle"
      :fill="textColor"
      :font-size="titleFontSize"
      :font-weight="titleFontWeight"
    >
      {{ node.name }}
    </text>
    
    <!-- 节点状态指示器 -->
    <circle
      class="status-indicator"
      :cx="node.size.width - statusIndicatorSize - statusPadding"
      :cy="headerHeight / 2"
      :r="statusIndicatorSize / 2"
      :fill="statusColor"
      :stroke="statusBorderColor"
      :stroke-width="1"
    />
    
    <!-- 节点内容区域 -->
    <g v-if="viewMode === 'detail' || viewMode === 'edit'" class="node-content">
      <!-- 节点描述 -->
      <text
        v-if="node.description"
        class="node-description"
        :x="contentPadding"
        :y="headerHeight + descriptionPadding"
        :fill="descriptionColor"
        :font-size="descriptionFontSize"
      >
        {{ truncateText(node.description, maxDescriptionLength) }}
      </text>
      
      <!-- 节点参数 -->
      <g v-if="node.parameters && node.parameters.length > 0" class="node-parameters">
        <text
          class="parameters-title"
          :x="contentPadding"
          :y="headerHeight + descriptionPadding + (node.description ? descriptionFontSize + parameterPadding : 0)"
          :fill="parametersTitleColor"
          :font-size="parametersTitleFontSize"
          :font-weight="parametersTitleFontWeight"
        >
          参数:
        </text>
        
        <g
          v-for="(param, index) in visibleParameters"
          :key="param.name"
          class="parameter-item"
        >
          <text
            class="parameter-name"
            :x="contentPadding"
            :y="getParameterYPosition(index)"
            :fill="parameterNameColor"
            :font-size="parameterFontSize"
          >
            {{ param.displayName || param.name }}:
          </text>
          <text
            class="parameter-value"
            :x="contentPadding + parameterNameWidth"
            :y="getParameterYPosition(index)"
            :fill="parameterValueColor"
            :font-size="parameterFontSize"
          >
            {{ formatParameterValue(param.value) }}
          </text>
        </g>
      </g>
      
      <!-- 节点进度条 -->
      <g v-if="showProgress" class="node-progress">
        <rect
          class="progress-background"
          :x="contentPadding"
          :y="node.size.height - progressHeight - progressPadding"
          :width="node.size.width - contentPadding * 2"
          :height="progressHeight"
          :rx="progressHeight / 2"
          :fill="progressBackgroundColor"
        />
        <rect
          class="progress-bar"
          :x="contentPadding"
          :y="node.size.height - progressHeight - progressPadding"
          :width="(node.size.width - contentPadding * 2) * (node.execution?.progress || 0) / 100"
          :height="progressHeight"
          :rx="progressHeight / 2"
          :fill="progressColor"
        />
        <text
          class="progress-text"
          :x="node.size.width / 2"
          :y="node.size.height - progressPadding - progressHeight / 2"
          dominant-baseline="middle"
          text-anchor="middle"
          :fill="progressTextColor"
          :font-size="progressFontSize"
        >
          {{ node.execution?.progress || 0 }}%
        </text>
      </g>
    </g>
    
    <!-- 连接点 -->
    <g class="connection-points">
      <!-- 输入连接点 -->
      <g
        v-for="(input, index) in node.inputs"
        :key="`input-${index}`"
        class="input-point"
        :transform="`translate(0, ${getInputPointY(index)})`"
      >
        <circle
          :r="connectionPointRadius"
          :fill="connectionPointColor"
          :stroke="connectionPointBorderColor"
          :stroke-width="connectionPointBorderWidth"
          class="connection-point-circle"
        />
        <text
          class="connection-point-label"
          :x="connectionPointRadius + connectionPointLabelPadding"
          :y="connectionPointRadius / 2"
          dominant-baseline="middle"
          :fill="connectionPointLabelColor"
          :font-size="connectionPointLabelFontSize"
        >
          {{ input.name }}
        </text>
      </g>
      
      <!-- 输出连接点 -->
      <g
        v-for="(output, index) in node.outputs"
        :key="`output-${index}`"
        class="output-point"
        :transform="`translate(${node.size.width}, ${getOutputPointY(index)})`"
      >
        <circle
          :r="connectionPointRadius"
          :fill="connectionPointColor"
          :stroke="connectionPointBorderColor"
          :stroke-width="connectionPointBorderWidth"
          class="connection-point-circle"
        />
        <text
          class="connection-point-label"
          :x="-connectionPointRadius - connectionPointLabelPadding"
          :y="connectionPointRadius / 2"
          dominant-baseline="middle"
          text-anchor="end"
          :fill="connectionPointLabelColor"
          :font-size="connectionPointLabelFontSize"
        >
          {{ output.name }}
        </text>
      </g>
    </g>
    
    <!-- 错误指示器 -->
    <g v-if="node.error" class="error-indicator">
      <circle
        :cx="node.size.width - errorIndicatorSize - errorPadding"
        :cy="node.size.height - errorIndicatorSize - errorPadding"
        :r="errorIndicatorSize / 2"
        :fill="errorColor"
      />
      <text
        :x="node.size.width - errorIndicatorSize - errorPadding"
        :y="node.size.height - errorIndicatorSize - errorPadding"
        dominant-baseline="middle"
        text-anchor="middle"
        :fill="errorTextColor"
        :font-size="errorFontSize"
        :font-weight="bold"
      >
        !
      </text>
    </g>
  </g>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  DataLine, 
  Setting, 
  TrendCharts, 
  VideoPlay, 
  DataAnalysis, 
  PieChart, 
  Download 
} from '@element-plus/icons-vue'
import type { Node, NodeStatus, NodeType } from '@/types/node-system'

// Props
interface Props {
  node: Node
  selected?: boolean
  highlighted?: boolean
  viewMode?: 'overview' | 'detail' | 'edit'
  draggable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  highlighted: false,
  viewMode: 'overview',
  draggable: false
})

// Emits
const emit = defineEmits<{
  click: [node: Node, event: MouseEvent]
  dblclick: [node: Node]
  mousedown: [node: Node, event: MouseEvent]
  mouseenter: [node: Node]
  mouseleave: [node: Node]
  rightclick: [node: Node, event: MouseEvent]
}>()

// 常量
const borderRadius = 8
const headerHeight = 40
const iconSize = 20
const iconPadding = 8
const statusIndicatorSize = 12
const statusPadding = 12
const contentPadding = 12
const descriptionPadding = 8
const descriptionFontSize = 12
const maxDescriptionLength = 50
const parameterPadding = 8
const parametersTitleFontSize = 12
const parametersTitleFontWeight = 'bold'
const parameterFontSize = 11
const parameterNameWidth = 80
const progressHeight = 6
const progressPadding = 12
const progressFontSize = 10
const connectionPointRadius = 6
const connectionPointBorderWidth = 2
const connectionPointLabelPadding = 8
const connectionPointLabelFontSize = 10
const errorIndicatorSize = 16
const errorPadding = 12
const errorFontSize = 12

// 计算属性
const isDragging = computed(() => props.node.status === NodeStatus.RUNNING)

const backgroundColor = computed(() => {
  if (props.selected) return '#e6f7ff'
  if (props.highlighted) return '#f0f9ff'
  return '#ffffff'
})

const borderColor = computed(() => {
  if (props.selected) return '#1890ff'
  if (props.highlighted) return '#40a9ff'
  return '#d9d9d9'
})

const borderWidth = computed(() => {
  if (props.selected) return 2
  if (props.highlighted) return 2
  return 1
})

const headerColor = computed(() => {
  switch (props.node.type) {
    case NodeType.DATA_SOURCE:
      return '#f0f9ff'
    case NodeType.DATA_PROCESSING:
      return '#f6ffed'
    case NodeType.STRATEGY:
      return '#fff7e6'
    case NodeType.BACKTEST:
      return '#fff1f0'
    case NodeType.ANALYSIS:
      return '#f9f0ff'
    case NodeType.VISUALIZATION:
      return '#fff0f6'
    case NodeType.EXPORT:
      return '#e6f7ff'
    default:
      return '#fafafa'
  }
})

const textColor = computed(() => '#262626')
const titleFontSize = computed(() => '14px')
const titleFontWeight = computed(() => 'bold')
const iconColor = computed(() => '#1890ff')
const descriptionColor = computed(() => '#8c8c8c')
const parametersTitleColor = computed(() => '#595959')
const parameterNameColor = computed(() => '#8c8c8c')
const parameterValueColor = computed(() => '#262626')
const progressBackgroundColor = computed(() => '#f0f0f0')
const progressColor = computed(() => '#1890ff')
const progressTextColor = computed(() => '#ffffff')
const connectionPointColor = computed(() => '#ffffff')
const connectionPointBorderColor = computed(() => '#1890ff')
const connectionPointLabelColor = computed(() => '#8c8c8c')
const errorColor = computed(() => '#ff4d4f')
const errorTextColor = computed(() => '#ffffff')

const statusColor = computed(() => {
  switch (props.node.status) {
    case NodeStatus.RUNNING:
      return '#52c41a'
    case NodeStatus.COMPLETED:
      return '#1890ff'
    case NodeStatus.FAILED:
      return '#ff4d4f'
    case NodeStatus.PAUSED:
      return '#faad14'
    default:
      return '#d9d9d9'
  }
})

const statusBorderColor = computed(() => '#ffffff')

const nodeIcon = computed(() => {
  switch (props.node.type) {
    case NodeType.DATA_SOURCE:
      return DataLine
    case NodeType.DATA_PROCESSING:
      return Setting
    case NodeType.STRATEGY:
      return TrendCharts
    case NodeType.BACKTEST:
      return VideoPlay
    case NodeType.ANALYSIS:
      return DataAnalysis
    case NodeType.VISUALIZATION:
      return PieChart
    case NodeType.EXPORT:
      return Download
    default:
      return Setting
  }
})

const visibleParameters = computed(() => {
  if (!props.node.parameters) return []
  const maxVisible = props.viewMode === 'overview' ? 2 : 4
  return props.node.parameters.slice(0, maxVisible)
})

const showProgress = computed(() => {
  return props.node.execution && props.node.execution.progress !== undefined
})

// 方法
const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatParameterValue = (value: any): string => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'boolean') return value ? '是' : '否'
  if (typeof value === 'number') return value.toString()
  if (typeof value === 'string') return value
  return JSON.stringify(value)
}

const getInputPointY = (index: number): number => {
  const totalInputs = props.node.inputs?.length || 0
  if (totalInputs === 1) return props.node.size.height / 2
  
  const spacing = props.node.size.height / (totalInputs + 1)
  return spacing * (index + 1)
}

const getOutputPointY = (index: number): number => {
  const totalOutputs = props.node.outputs?.length || 0
  if (totalOutputs === 1) return props.node.size.height / 2
  
  const spacing = props.node.size.height / (totalOutputs + 1)
  return spacing * (index + 1)
}

const getParameterYPosition = (index: number): number => {
  const baseY = headerHeight + descriptionPadding + (props.node.description ? descriptionFontSize + parameterPadding : 0)
  return baseY + parametersTitleFontSize + parameterPadding + (index * (parameterFontSize + 4))
}

// 事件处理
const handleMouseDown = (event: MouseEvent) => {
  emit('mousedown', props.node, event)
}

const handleMouseEnter = () => {
  emit('mouseenter', props.node)
}

const handleMouseLeave = () => {
  emit('mouseleave', props.node)
}

const handleClick = (event: MouseEvent) => {
  emit('click', props.node, event)
}

const handleDoubleClick = () => {
  emit('dblclick', props.node)
}

const handleRightClick = (event: MouseEvent) => {
  emit('rightclick', props.node, event)
}
</script>

<style scoped>
.node-renderer {
  cursor: pointer;
  transition: all 0.2s ease;
}

.node-renderer:hover {
  filter: brightness(0.95);
}

.node-selected {
  filter: drop-shadow(0 0 8px rgba(24, 144, 255, 0.5));
}

.node-highlighted {
  filter: drop-shadow(0 0 4px rgba(64, 169, 255, 0.3));
}

.node-dragging {
  cursor: grabbing;
  opacity: 0.8;
}

.node-running {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    filter: drop-shadow(0 0 4px rgba(82, 196, 26, 0.5));
  }
  50% {
    filter: drop-shadow(0 0 8px rgba(82, 196, 26, 0.8));
  }
  100% {
    filter: drop-shadow(0 0 4px rgba(82, 196, 26, 0.5));
  }
}

.node-background {
  transition: all 0.2s ease;
}

.node-header {
  transition: all 0.2s ease;
}

.node-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.node-title {
  pointer-events: none;
  user-select: none;
}

.node-description {
  pointer-events: none;
  user-select: none;
}

.parameters-title {
  pointer-events: none;
  user-select: none;
}

.parameter-name {
  pointer-events: none;
  user-select: none;
}

.parameter-value {
  pointer-events: none;
  user-select: none;
  font-weight: 500;
}

.node-progress {
  pointer-events: none;
}

.progress-background {
  transition: all 0.2s ease;
}

.progress-bar {
  transition: width 0.3s ease;
}

.progress-text {
  pointer-events: none;
  user-select: none;
  font-weight: bold;
}

.connection-points {
  pointer-events: none;
}

.connection-point-circle {
  transition: all 0.2s ease;
}

.input-point:hover .connection-point-circle,
.output-point:hover .connection-point-circle {
  r: 8;
  fill: #1890ff;
}

.connection-point-label {
  pointer-events: none;
  user-select: none;
}

.error-indicator {
  animation: error-pulse 1s infinite;
}

@keyframes error-pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}
</style>