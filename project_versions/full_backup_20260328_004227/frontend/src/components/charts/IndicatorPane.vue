<template>
  <div
    v-if="visible"
    :ref="paneContainerRef"
    class="indicator-pane"
    :data-id="id"
    :style="{ height: `${height}px` }"
  >
    <!-- 拖拽手柄 -->
    <div
      v-if="resizable"
      class="resize-handle"
      @mousedown="startResize"
    ></div>

    <!-- 标题栏 -->
    <div class="pane-header">
      <span class="pane-title">{{ title }}</span>
      <button
        class="close-btn"
        @click="$emit('close')"
        title="关闭"
      >
        ×
      </button>
    </div>

    <!-- 图表容器 -->
    <div
      :ref="chartContainerRef"
      class="pane-chart"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import type { IChartApi } from 'lightweight-charts'

// Props
interface Props {
  id: string
  title: string
  height?: number
  minHeight?: number
  maxHeight?: number
  visible?: boolean
  resizable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: 120,
  minHeight: 80,
  maxHeight: 400,
  visible: true,
  resizable: true
})

// Emits
const emit = defineEmits<{
  ready: [chart: IChartApi]
  resize: [height: number]
  close: []
  'update:height': [height: number]
}>()

// Refs
const paneContainerRef = ref<HTMLElement>()
const chartContainerRef = ref<HTMLElement>()

// State
const currentHeight = ref(props.height)
const isResizing = ref(false)

// 暴露方法
const getChartContainer = () => chartContainerRef.value
const getPaneContainer = () => paneContainerRef.value

/**
 * 开始拖拽调整高度
 */
const startResize = (e: MouseEvent) => {
  isResizing.value = true

  const startY = e.clientY
  const startHeight = currentHeight.value

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing.value) return

    const deltaY = e.clientY - startY
    let newHeight = startHeight + deltaY

    // 限制高度范围
    newHeight = Math.max(props.minHeight, Math.min(props.maxHeight, newHeight))

    currentHeight.value = newHeight
    emit('resize', newHeight)
    emit('update:height', newHeight)
  }

  const handleMouseUp = () => {
    isResizing.value = false
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 监听高度变化
watch(() => props.height, (newHeight) => {
  currentHeight.value = newHeight
})

// 生命周期
onMounted(() => {
  // 组件挂载后，触发ready事件
  nextTick(() => {
    if (chartContainerRef.value) {
      // 图表实例将在父组件中创建
    }
  })
})

onUnmounted(() => {
  // 清理工作由父组件处理
})

// 暴露给父组件
defineExpose({
  getChartContainer,
  getPaneContainer,
  startResize
})
</script>

<style scoped lang="scss">
.indicator-pane {
  position: relative;
  width: 100%;
  background: #131722;
  border-top: 1px solid #2A2E39;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.resize-handle {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  cursor: ns-resize;
  background: transparent;
  transition: background 0.2s;
  z-index: 10;

  &:hover {
    background: rgba(102, 126, 234, 0.3);
  }

  &:active {
    background: rgba(102, 126, 234, 0.5);
  }
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  background: #1E222D;
  border-bottom: 1px solid #2A2E39;
  min-height: 28px;

  .pane-title {
    font-size: 11px;
    font-weight: 500;
    color: #B2B5BE;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .close-btn {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    color: #787B86;
    font-size: 16px;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.2s;
    line-height: 1;

    &:hover {
      background: rgba(239, 68, 68, 0.1);
      color: #ef5350;
    }
  }
}

.pane-chart {
  flex: 1;
  width: 100%;
  height: 100%;
}
</style>
