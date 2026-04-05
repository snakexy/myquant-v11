<template>
  <g 
    class="connection-renderer"
    :class="{
      'connection-selected': selected,
      'connection-highlighted': highlighted,
      'connection-animated': isAnimated,
      [`connection-${connection.type}`]: true
    }"
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- 连接路径 -->
    <path
      :d="connectionPath"
      :stroke="strokeColor"
      :stroke-width="strokeWidth"
      :stroke-dasharray="strokeDasharray"
      :fill="none"
      :marker-end="markerEnd"
      class="connection-path"
    />
    
    <!-- 连接标签背景 -->
    <rect
      v-if="showLabel && connection.label"
      class="connection-label-background"
      :x="labelPosition.x - labelWidth / 2 - labelPadding"
      :y="labelPosition.y - labelHeight / 2 - labelPadding"
      :width="labelWidth + labelPadding * 2"
      :height="labelHeight + labelPadding * 2"
      :rx="labelBorderRadius"
      :fill="labelBackgroundColor"
      :stroke="labelBorderColor"
      :stroke-width="1"
    />
    
    <!-- 连接标签文本 -->
    <text
      v-if="showLabel && connection.label"
      class="connection-label"
      :x="labelPosition.x"
      :y="labelPosition.y"
      dominant-baseline="middle"
      text-anchor="middle"
      :fill="labelTextColor"
      :font-size="labelFontSize"
      :font-weight="labelFontWeight"
    >
      {{ connection.label }}
    </text>
    
    <!-- 数据流动画 -->
    <circle
      v-if="isAnimated && showDataFlow"
      class="data-flow-dot"
      :r="dataFlowDotRadius"
      :fill="dataFlowDotColor"
    >
      <animateMotion
        :dur="dataFlowDuration"
        repeatCount="indefinite"
        :path="connectionPath"
      />
    </circle>
    
    <!-- 连接点装饰 -->
    <circle
      v-if="showSourceDecoration"
      class="source-decoration"
      :cx="sourcePoint.x"
      :cy="sourcePoint.y"
      :r="decorationRadius"
      :fill="sourceDecorationColor"
      :stroke="sourceDecorationBorderColor"
      :stroke-width="1"
    />
    
    <circle
      v-if="showTargetDecoration"
      class="target-decoration"
      :cx="targetPoint.x"
      :cy="targetPoint.y"
      :r="decorationRadius"
      :fill="targetDecorationColor"
      :stroke="targetDecorationBorderColor"
      :stroke-width="1"
    />
    
    <!-- 错误指示器 -->
    <g v-if="connection.error" class="error-indicator">
      <circle
        :cx="errorPosition.x"
        :cy="errorPosition.y"
        :r="errorIndicatorRadius"
        :fill="errorColor"
      />
      <text
        :x="errorPosition.x"
        :y="errorPosition.y"
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
import type { Connection, ConnectionType, Node } from '@/types/node-system'

// Props
interface Props {
  connection: Connection
  sourceNode?: Node
  targetNode?: Node
  selected?: boolean
  highlighted?: boolean
  showLabel?: boolean
  showDataFlow?: boolean
  showSourceDecoration?: boolean
  showTargetDecoration?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  selected: false,
  highlighted: false,
  showLabel: true,
  showDataFlow: true,
  showSourceDecoration: false,
  showTargetDecoration: false
})

// Emits
const emit = defineEmits<{
  click: [connection: Connection, event: MouseEvent]
  mouseenter: [connection: Connection]
  mouseleave: [connection: Connection]
}>()

// 常量
const strokeWidth = 2
const selectedStrokeWidth = 3
const highlightedStrokeWidth = 3
const labelPadding = 6
const labelBorderRadius = 4
const labelFontSize = 12
const labelFontWeight = 'normal'
const dataFlowDotRadius = 4
const dataFlowDuration = '2s'
const decorationRadius = 6
const errorIndicatorRadius = 8
const errorFontSize = 10

// 计算属性
const isAnimated = computed(() => {
  return props.connection.status === 'active' || props.connection.status === 'transferring'
})

const strokeColor = computed(() => {
  if (props.selected) return '#1890ff'
  if (props.highlighted) return '#40a9ff'
  
  switch (props.connection.status) {
    case 'active':
      return '#52c41a'
    case 'transferring':
      return '#1890ff'
    case 'error':
      return '#ff4d4f'
    case 'warning':
      return '#faad14'
    case 'inactive':
      return '#d9d9d9'
    default:
      return '#8c8c8c'
  }
})

const strokeWidthComputed = computed(() => {
  if (props.selected) return selectedStrokeWidth
  if (props.highlighted) return highlightedStrokeWidth
  return strokeWidth
})

const strokeDasharray = computed(() => {
  switch (props.connection.type) {
    case ConnectionType.DATA:
      return 'none'
    case ConnectionType.CONTROL:
      return '5,5'
    case ConnectionType.EVENT:
      return '2,2'
    case ConnectionType.DEPENDENCY:
      return '10,5'
    default:
      return 'none'
  }
})

const markerEnd = computed(() => {
  if (props.selected) return 'url(#arrowhead-highlight)'
  return 'url(#arrowhead)'
})

const sourcePoint = computed(() => {
  if (!props.sourceNode) return { x: 0, y: 0 }
  
  const outputIndex = props.sourceNode.outputs?.findIndex(
    output => output.id === props.connection.sourceOutputId
  ) ?? 0
  
  const x = props.sourceNode.position.x + props.sourceNode.size.width
  const y = props.sourceNode.position.y + getSourceOutputY(outputIndex)
  
  return { x, y }
})

const targetPoint = computed(() => {
  if (!props.targetNode) return { x: 0, y: 0 }
  
  const inputIndex = props.targetNode.inputs?.findIndex(
    input => input.id === props.connection.targetInputId
  ) ?? 0
  
  const x = props.targetNode.position.x
  const y = props.targetNode.position.y + getTargetInputY(inputIndex)
  
  return { x, y }
})

const connectionPath = computed(() => {
  const start = sourcePoint.value
  const end = targetPoint.value
  
  // 计算控制点
  const controlPoint1X = start.x + (end.x - start.x) * 0.5
  const controlPoint1Y = start.y
  const controlPoint2X = start.x + (end.x - start.x) * 0.5
  const controlPoint2Y = end.y
  
  // 使用贝塞尔曲线创建平滑连接
  return `M ${start.x} ${start.y} C ${controlPoint1X} ${controlPoint1Y}, ${controlPoint2X} ${controlPoint2Y}, ${end.x} ${end.y}`
})

const labelPosition = computed(() => {
  const start = sourcePoint.value
  const end = targetPoint.value
  
  // 在路径中点放置标签
  return {
    x: (start.x + end.x) / 2,
    y: (start.y + end.y) / 2 - 10
  }
})

const labelWidth = computed(() => {
  if (!props.connection.label) return 0
  return props.connection.label.length * labelFontSize * 0.6
})

const labelHeight = computed(() => {
  return labelFontSize
})

const labelBackgroundColor = computed(() => '#ffffff')
const labelBorderColor = computed(() => '#d9d9d9')
const labelTextColor = computed(() => '#595959')

const dataFlowDotColor = computed(() => '#1890ff')

const sourceDecorationColor = computed(() => '#52c41a')
const sourceDecorationBorderColor = computed(() => '#ffffff')

const targetDecorationColor = computed(() => '#1890ff')
const targetDecorationBorderColor = computed(() => '#ffffff')

const errorPosition = computed(() => {
  const start = sourcePoint.value
  const end = targetPoint.value
  
  return {
    x: (start.x + end.x) / 2 + 20,
    y: (start.y + end.y) / 2
  }
})

const errorColor = computed(() => '#ff4d4f')
const errorTextColor = computed(() => '#ffffff')

// 方法
const getSourceOutputY = (index: number): number => {
  if (!props.sourceNode?.outputs) return 0
  const totalOutputs = props.sourceNode.outputs.length
  if (totalOutputs === 1) return props.sourceNode.size.height / 2
  
  const spacing = props.sourceNode.size.height / (totalOutputs + 1)
  return spacing * (index + 1)
}

const getTargetInputY = (index: number): number => {
  if (!props.targetNode?.inputs) return 0
  const totalInputs = props.targetNode.inputs.length
  if (totalInputs === 1) return props.targetNode.size.height / 2
  
  const spacing = props.targetNode.size.height / (totalInputs + 1)
  return spacing * (index + 1)
}

// 事件处理
const handleClick = (event: MouseEvent) => {
  emit('click', props.connection, event)
}

const handleMouseEnter = () => {
  emit('mouseenter', props.connection)
}

const handleMouseLeave = () => {
  emit('mouseleave', props.connection)
}
</script>

<style scoped>
.connection-renderer {
  cursor: pointer;
  transition: all 0.2s ease;
}

.connection-renderer:hover {
  filter: brightness(0.9);
}

.connection-selected {
  filter: drop-shadow(0 0 4px rgba(24, 144, 255, 0.5));
}

.connection-highlighted {
  filter: drop-shadow(0 0 2px rgba(64, 169, 255, 0.3));
}

.connection-animated {
  animation: connection-pulse 2s infinite;
}

@keyframes connection-pulse {
  0% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.7;
  }
}

.connection-path {
  transition: all 0.2s ease;
}

.connection-label-background {
  transition: all 0.2s ease;
}

.connection-label {
  pointer-events: none;
  user-select: none;
}

.data-flow-dot {
  filter: drop-shadow(0 0 2px rgba(24, 144, 255, 0.5));
}

.source-decoration,
.target-decoration {
  transition: all 0.2s ease;
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

/* 连接类型特定样式 */
.connection-data .connection-path {
  stroke-linecap: round;
}

.connection-control .connection-path {
  stroke-linecap: square;
}

.connection-event .connection-path {
  stroke-linecap: round;
}

.connection-dependency .connection-path {
  stroke-linecap: butt;
}
</style>