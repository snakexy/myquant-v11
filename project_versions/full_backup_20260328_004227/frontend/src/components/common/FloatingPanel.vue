<template>
  <div
    ref="panelRef"
    :data-panel-id="id"
    :class="['floating-panel', { minimized, dragging, resizing }]"
    :style="panelStyle"
    @mousedown="handleMouseDown"
  >
    <!-- 面板头部 -->
    <div class="panel-header" @mousedown="startDrag">
      <div class="panel-title-section">
        <span class="panel-icon">{{ icon }}</span>
        <h3 class="panel-title">{{ title }}</h3>
      </div>
      <div class="panel-controls">
        <button 
          class="control-btn minimize-btn"
          @click.stop="toggleMinimize"
          :title="minimized ? '还原' : '最小化'"
        >
          <svg v-if="!minimized" width="12" height="12" viewBox="0 0 12 12">
            <rect x="2" y="5" width="8" height="2" fill="currentColor"/>
          </svg>
          <svg v-else width="12" height="12" viewBox="0 0 12 12">
            <rect x="2" y="3" width="8" height="6" fill="none" stroke="currentColor" stroke-width="1"/>
          </svg>
        </button>
        <button 
          class="control-btn close-btn"
          @click.stop="closePanel"
          title="关闭"
        >
          <svg width="12" height="12" viewBox="0 0 12 12">
            <path d="M2 2 L10 10 M10 2 L2 10" stroke="currentColor" stroke-width="1.5"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 面板内容 -->
    <div v-show="!minimized" class="panel-content-wrapper">
      <div class="panel-content">
        <slot></slot>
      </div>
    </div>

    <!-- 调整大小手柄 -->
    <div 
      v-show="!minimized"
      class="resize-handle"
      @mousedown="startResize"
    ></div>

    <!-- 玻璃拟态效果背景 -->
    <div class="glass-effect"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'

// Props 定义
interface Props {
  id: string
  title: string
  icon: string
  initialPosition?: { x: number; y: number }
  initialSize?: { width: number; height: number }
  minimized?: boolean
  resizable?: boolean
  draggable?: boolean
  zIndex?: number
}

const props = withDefaults(defineProps<Props>(), {
  initialPosition: () => ({ x: 100, y: 100 }),
  initialSize: () => ({ width: 400, height: 300 }),
  minimized: false,
  resizable: true,
  draggable: true,
  zIndex: 100
})

// Emits 定义
const emit = defineEmits<{
  minimize: [panelId: string, panelInfo: { title: string; icon: string }]
  restore: [panelId: string]
  close: [panelId: string]
  resize: [panelId: string, size: { width: number; height: number }]
  move: [panelId: string, position: { x: number; y: number }]
}>()

// 响应式数据
const panelRef = ref<HTMLElement>()
const minimized = ref(props.minimized)
const dragging = ref(false)
const resizing = ref(false)
const position = reactive({ ...props.initialPosition })
const size = reactive({ ...props.initialSize })
const currentZIndex = ref(props.zIndex)

// 拖拽相关状态
const dragState = reactive({
  startX: 0,
  startY: 0,
  initialX: 0,
  initialY: 0
})

// 调整大小相关状态
const resizeState = reactive({
  startX: 0,
  startY: 0,
  initialWidth: 0,
  initialHeight: 0
})

// 计算属性
const panelStyle = computed(() => ({
  left: `${position.x}px`,
  top: `${position.y}px`,
  width: `${size.width}px`,
  height: `${size.height}px`,
  zIndex: currentZIndex.value,
  transform: minimized.value ? 'scale(0.1)' : 'scale(1)',
  opacity: minimized.value ? 0 : 1,
  pointerEvents: minimized.value ? 'none' : 'auto'
}))

// 方法
const handleMouseDown = () => {
  // 提升面板到最前面
  currentZIndex.value = getHighestZIndex() + 1
}

const startDrag = (e: MouseEvent) => {
  if (!props.draggable || minimized.value) return
  
  dragging.value = true
  
  dragState.startX = e.clientX
  dragState.startY = e.clientY
  dragState.initialX = position.x
  dragState.initialY = position.y
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  
  e.preventDefault()
}

const onDrag = (e: MouseEvent) => {
  if (!dragging.value) return
  
  const deltaX = e.clientX - dragState.startX
  const deltaY = e.clientY - dragState.startY
  
  position.x = dragState.initialX + deltaX
  position.y = dragState.initialY + deltaY
  
  // 限制在视口内
  const maxX = window.innerWidth - size.width
  const maxY = window.innerHeight - size.height
  
  position.x = Math.max(0, Math.min(position.x, maxX))
  position.y = Math.max(0, Math.min(position.y, maxY))
  
  emit('move', props.id, { ...position })
}

const stopDrag = () => {
  dragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

const startResize = (e: MouseEvent) => {
  if (!props.resizable || minimized.value) return
  
  resizing.value = true
  
  resizeState.startX = e.clientX
  resizeState.startY = e.clientY
  resizeState.initialWidth = size.width
  resizeState.initialHeight = size.height
  
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  
  e.preventDefault()
  e.stopPropagation()
}

const onResize = (e: MouseEvent) => {
  if (!resizing.value) return
  
  const deltaX = e.clientX - resizeState.startX
  const deltaY = e.clientY - resizeState.startY
  
  size.width = Math.max(300, resizeState.initialWidth + deltaX)
  size.height = Math.max(200, resizeState.initialHeight + deltaY)
  
  emit('resize', props.id, { ...size })
}

const stopResize = () => {
  resizing.value = false
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
}

const toggleMinimize = () => {
  minimized.value = !minimized.value
  
  if (minimized.value) {
    emit('minimize', props.id, { title: props.title, icon: props.icon })
    
    // 添加最小化动画
    nextTick(() => {
      if (panelRef.value) {
        panelRef.value.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
      }
    })
  } else {
    emit('restore', props.id)
    
    // 还原动画
    nextTick(() => {
      if (panelRef.value) {
        panelRef.value.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
        setTimeout(() => {
          if (panelRef.value) {
            panelRef.value.style.transition = ''
          }
        }, 300)
      }
    })
  }
}

const closePanel = () => {
  // 添加关闭动画
  if (panelRef.value) {
    panelRef.value.style.transition = 'all 0.2s ease-out'
    panelRef.value.style.transform = 'scale(0.8)'
    panelRef.value.style.opacity = '0'
    
    setTimeout(() => {
      emit('close', props.id)
    }, 200)
  } else {
    emit('close', props.id)
  }
}

const restore = () => {
  minimized.value = false
  currentZIndex.value = getHighestZIndex() + 1
  
  nextTick(() => {
    if (panelRef.value) {
      panelRef.value.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
      setTimeout(() => {
        if (panelRef.value) {
          panelRef.value.style.transition = ''
        }
      }, 300)
    }
  })
}

const getHighestZIndex = (): number => {
  const panels = document.querySelectorAll('.floating-panel')
  let highest = 0
  
  panels.forEach(panel => {
    const zIndex = parseInt(window.getComputedStyle(panel).zIndex || '0')
    highest = Math.max(highest, zIndex)
  })
  
  return highest
}

// 监听最小化状态变化
watch(minimized, (newVal) => {
  if (newVal) {
    // 最小化时移除事件监听
    document.removeEventListener('mousemove', onDrag)
    document.removeEventListener('mouseup', stopDrag)
    document.removeEventListener('mousemove', onResize)
    document.removeEventListener('mouseup', stopResize)
  }
})

// 暴露方法给父组件
defineExpose({
  restore,
  minimize: () => toggleMinimize(),
  getPosition: () => ({ ...position }),
  getSize: () => ({ ...size }),
  setPosition: (newPosition: { x: number; y: number }) => {
    position.x = newPosition.x
    position.y = newPosition.y
  },
  setSize: (newSize: { width: number; height: number }) => {
    size.width = newSize.width
    size.height = newSize.height
  }
})

// 生命周期
onMounted(() => {
  // 确保面板在视口内
  nextTick(() => {
    const maxX = window.innerWidth - size.width
    const maxY = window.innerHeight - size.height
    
    position.x = Math.max(0, Math.min(position.x, maxX))
    position.y = Math.max(0, Math.min(position.y, maxY))
  })
  
  console.log(`FloatingPanel ${props.id} 已挂载`)
})

onUnmounted(() => {
  // 清理事件监听
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
  
  console.log(`FloatingPanel ${props.id} 已卸载`)
  
  // 确保DOM元素被移除
  if (panelRef.value && panelRef.value.parentNode) {
    panelRef.value.parentNode.removeChild(panelRef.value)
    console.log(`已从DOM中移除面板: ${props.id}`)
  }
})
</script>

<style lang="scss" scoped>
.floating-panel {
  position: absolute;
  background: rgba(26, 26, 46, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.3),
    0 2px 8px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
  user-select: none;
  
  &:hover {
    border-color: rgba(37, 99, 235, 0.3);
    box-shadow: 
      0 12px 40px rgba(0, 0, 0, 0.4),
      0 4px 12px rgba(0, 0, 0, 0.3),
      0 0 0 1px rgba(37, 99, 235, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.15);
  }
  
  &.dragging {
    cursor: move;
    box-shadow: 
      0 16px 48px rgba(0, 0, 0, 0.5),
      0 8px 24px rgba(0, 0, 0, 0.4),
      0 0 0 1px rgba(37, 99, 235, 0.3);
  }
  
  &.resizing {
    cursor: nwse-resize;
  }
  
  .glass-effect {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.05) 50%,
      rgba(255, 255, 255, 0.02) 100%
    );
    pointer-events: none;
    z-index: 1;
  }
}

.panel-header {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(
    135deg,
    rgba(37, 99, 235, 0.15) 0%,
    rgba(124, 58, 237, 0.1) 100%
  );
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: move;
  z-index: 3;
  
  .panel-title-section {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .panel-icon {
      font-size: 18px;
      line-height: 1;
    }
    
    .panel-title {
      font-size: 16px;
      font-weight: 600;
      color: #ffffff;
      margin: 0;
      background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }
  
  .panel-controls {
    display: flex;
    gap: 8px;
    
    .control-btn {
      width: 28px;
      height: 28px;
      border: none;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.1);
      color: rgba(255, 255, 255, 0.8);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
        color: #ffffff;
        transform: scale(1.05);
      }
      
      &:active {
        transform: scale(0.95);
      }
      
      &.minimize-btn:hover {
        background: rgba(59, 130, 246, 0.3);
        color: #3b82f6;
      }
      
      &.close-btn:hover {
        background: rgba(239, 68, 68, 0.3);
        color: var(--market-fall);
      }
    }
  }
}

.panel-content-wrapper {
  position: relative;
  height: calc(100% - 60px);
  z-index: 2;
}

.panel-content {
  width: 100%;
  height: 100%;
  overflow: auto;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(37, 99, 235, 0.5);
    border-radius: 3px;
    
    &:hover {
      background: rgba(37, 99, 235, 0.7);
    }
  }
}

.resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  cursor: nwse-resize;
  z-index: 4;
  
  &::before {
    content: '';
    position: absolute;
    bottom: 3px;
    right: 3px;
    width: 0;
    height: 0;
    border-style: solid;
    border-width: 0 0 8px 8px;
    border-color: transparent transparent rgba(255, 255, 255, 0.3) transparent;
  }
  
  &::after {
    content: '';
    position: absolute;
    bottom: 6px;
    right: 6px;
    width: 0;
    height: 0;
    border-style: solid;
    border-width: 0 0 5px 5px;
    border-color: transparent transparent rgba(255, 255, 255, 0.5) transparent;
  }
}

// 霓虹发光效果
@keyframes neonGlow {
  0%, 100% {
    box-shadow: 
      0 0 20px rgba(37, 99, 235, 0.5),
      0 0 40px rgba(37, 99, 235, 0.3),
      0 0 60px rgba(37, 99, 235, 0.1);
  }
  50% {
    box-shadow: 
      0 0 30px rgba(37, 99, 235, 0.7),
      0 0 60px rgba(37, 99, 235, 0.5),
      0 0 90px rgba(37, 99, 235, 0.3);
  }
}

.floating-panel:hover {
  animation: neonGlow 3s ease-in-out infinite;
}

// 响应式设计
@media (max-width: 768px) {
  .floating-panel {
    border-radius: 8px;
    
    .panel-header {
      padding: 12px 16px;
      
      .panel-title {
        font-size: 14px;
      }
      
      .control-btn {
        width: 24px;
        height: 24px;
      }
    }
  }
  
  .resize-handle {
    width: 16px;
    height: 16px;
  }
}
</style>