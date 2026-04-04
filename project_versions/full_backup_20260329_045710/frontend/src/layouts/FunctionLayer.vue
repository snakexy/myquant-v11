<template>
  <div class="function-layer">
    <!-- 智能层级导航 -->
    <LayerNavigation 
      :current-function="currentFunction"
      :current-layer="currentLayer"
      @layer-change="handleLayerChange"
      @navigate-to-engineer="navigateToEngineerToolbox"
    />
    
    <!-- 主内容区域 -->
    <div class="layer-content">
      <!-- 第一层：主界面 -->
      <Dashboard 
        v-if="currentLayer === 1"
        :function-id="functionId"
        @enter-function="enterFunction"
      />
      
      <!-- 第二层：架构图 -->
      <ArchitectureLayer 
        v-else-if="currentLayer === 2"
        :function-id="functionId"
        @enter-monitoring="enterMonitoring"
      />
      
      <!-- 第三层：监控层 -->
      <MonitoringLayer 
        v-else-if="currentLayer === 3"
        :function-id="functionId"
      />
    </div>
    
    <!-- 层级切换动画 -->
    <transition name="layer-transition" mode="out-in">
      <div :key="currentLayer" class="transition-overlay"></div>
    </transition>
    
    <!-- 状态保持指示器 -->
    <div class="state-indicator" v-if="isStateLoading">
      <div class="loading-spinner"></div>
      <span>正在保持状态...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores'
import { functionModules } from '@/configs/functionConfig'
import LayerNavigation from '@/components/navigation/LayerNavigation.vue'
import Dashboard from '@/pages/Dashboard.vue'
import ArchitectureLayer from '@/layers/ArchitectureLayer.vue'
import MonitoringLayer from '@/layers/MonitoringLayer.vue'

// 路由和状态管理
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

// 响应式数据
const functionId = computed(() => route.params.functionId as string)
const currentLayer = ref(1)
const isStateLoading = ref(false)
const stateSaveTimer = ref<number | null>(null)

// 当前功能信息
const currentFunction = computed(() => {
  return functionModules.find(module => module.id === functionId.value)
})

// 监听路由变化，恢复层级状态
watch(() => route.path, (newPath) => {
  const pathParts = newPath.split('/')
  const layerIndex = pathParts.findIndex(part => ['dashboard', 'architecture', 'monitoring'].includes(part))
  
  if (layerIndex !== -1) {
    const layerMap: Record<string, number> = {
      'dashboard': 1,
      'architecture': 2,
      'monitoring': 3
    }
    currentLayer.value = layerMap[pathParts[layerIndex]] || 1
  }
}, { immediate: true })

// 监听层级变化，更新路由
watch(currentLayer, (newLayer) => {
  updateRouteForLayer(newLayer)
})

// 处理层级变化
const handleLayerChange = (layer: number) => {
  if (layer === currentLayer.value) return
  
  // 保存当前状态
  saveCurrentState()
  
  // 切换层级
  currentLayer.value = layer
  
  // 恢复目标层级状态
  restoreLayerState(layer)
}

// 进入功能
const enterFunction = (moduleId: string) => {
  saveCurrentState()
  // 更新当前功能ID
  if (moduleId !== functionId.value) {
    router.push(`/function/${moduleId}/dashboard`)
  } else {
    currentLayer.value = 2
    updateRouteForLayer(2)
  }
}

// 进入监控
const enterMonitoring = () => {
  saveCurrentState()
  currentLayer.value = 3
  updateRouteForLayer(3)
}

// 导航到工程师工具箱
const navigateToEngineerToolbox = () => {
  saveCurrentState()
  router.push('/engineer-toolbox')
}

// 更新路由以匹配当前层级
const updateRouteForLayer = (layer: number) => {
  const layerMap: Record<number, string> = {
    1: 'dashboard',
    2: 'architecture',
    3: 'monitoring'
  }
  
  const layerPath = layerMap[layer]
  if (!layerPath) return
  
  const currentPath = route.path
  const newPath = `/function/${functionId.value}/${layerPath}`
  
  if (currentPath !== newPath) {
    router.replace(newPath)
  }
}

// 保存当前状态
const saveCurrentState = () => {
  isStateLoading.value = true
  
  // 收集当前状态
  const currentState = {
    functionId: functionId.value,
    layer: currentLayer.value,
    timestamp: Date.now(),
    data: collectCurrentLayerData()
  }
  
  // 保存到状态存储
  appStore.saveLayerState(functionId.value, currentLayer.value, currentState)
  
  // 设置自动保存定时器
  if (stateSaveTimer.value) {
    clearTimeout(stateSaveTimer.value)
  }
  
  stateSaveTimer.value = setTimeout(() => {
    isStateLoading.value = false
  }, 500) as unknown as number
}

// 收集当前层数据
const collectCurrentLayerData = () => {
  switch (currentLayer.value) {
    case 1:
      return collectDashboardData()
    case 2:
      return collectArchitectureData()
    case 3:
      return collectMonitoringData()
    default:
      return {}
  }
}

// 收集仪表板数据
const collectDashboardData = () => {
  // 从DOM或组件实例收集数据
  const dashboardElement = document.querySelector('.dashboard')
  if (!dashboardElement) return {}
  
  return {
    scrollPosition: {
      x: dashboardElement.scrollLeft,
      y: dashboardElement.scrollTop
    },
    selectedCards: Array.from(document.querySelectorAll('.function-card.selected')).map(el => 
      (el as HTMLElement).dataset.cardId
    ),
    viewMode: (document.querySelector('.view-mode-selector .active') as HTMLElement)?.dataset.mode || 'grid',
    searchTerm: (document.querySelector('.global-search input') as HTMLInputElement)?.value || ''
  }
}

// 收集架构图数据
const collectArchitectureData = () => {
  const architectureElement = document.querySelector('.architecture-layer')
  if (!architectureElement) return {}
  
  return {
    viewMode: (document.querySelector('.view-mode-selector .active') as HTMLElement)?.dataset.mode || '2d',
    selectedNodes: Array.from(document.querySelectorAll('.network-node.selected')).map(el => 
      (el as HTMLElement).dataset.nodeId
    ),
    zoomLevel: parseFloat((document.querySelector('.zoom-controls .zoom-level') as HTMLElement)?.textContent || '1'),
    panPosition: {
      x: parseFloat((document.querySelector('.network-canvas') as HTMLElement)?.style.transform?.match(/translateX\(([-\d.]+)px\)/)?.[1] || '0'),
      y: parseFloat((document.querySelector('.network-canvas') as HTMLElement)?.style.transform?.match(/translateY\(([-\d.]+)px\)/)?.[1] || '0')
    }
  }
}

// 收集监控数据
const collectMonitoringData = () => {
  const monitoringElement = document.querySelector('.monitoring-layer')
  if (!monitoringElement) return {}
  
  return {
    viewMode: (document.querySelector('.view-mode-selector .active') as HTMLElement)?.dataset.mode || 'multi-screen',
    screenLayout: Array.from(document.querySelectorAll('.monitor-screen')).map(el => ({
      id: (el as HTMLElement).dataset.screenId,
      position: {
        left: (el as HTMLElement).style.left,
        top: (el as HTMLElement).style.top,
        width: (el as HTMLElement).style.width,
        height: (el as HTMLElement).style.height
      }
    })),
    alertFilters: {
      levels: Array.from(document.querySelectorAll('.alert-filters input:checked')).map(el => (el as HTMLInputElement).value),
      types: Array.from(document.querySelectorAll('.alert-filters input:checked')).map(el => (el as HTMLInputElement).value)
    }
  }
}

// 恢复层级状态
const restoreLayerState = (layer: number) => {
  isStateLoading.value = true
  
  const savedState = appStore.getLayerState(functionId.value, layer)
  
  if (savedState) {
    // 延迟恢复，确保DOM已渲染
    setTimeout(() => {
      applyLayerState(layer, savedState.data)
      isStateLoading.value = false
    }, 100)
  } else {
    isStateLoading.value = false
  }
}

// 应用层级状态
const applyLayerState = (layer: number, stateData: any) => {
  switch (layer) {
    case 1:
      applyDashboardState(stateData)
      break
    case 2:
      applyArchitectureState(stateData)
      break
    case 3:
      applyMonitoringState(stateData)
      break
  }
}

// 应用仪表板状态
const applyDashboardState = (state: any) => {
  const dashboardElement = document.querySelector('.dashboard')
  if (!dashboardElement || !state) return
  
  // 恢复滚动位置
  if (state.scrollPosition) {
    dashboardElement.scrollLeft = state.scrollPosition.x
    dashboardElement.scrollTop = state.scrollPosition.y
  }
  
  // 恢复选中的卡片
  if (state.selectedCards) {
    document.querySelectorAll('.function-card').forEach(card => {
      const cardId = (card as HTMLElement).dataset.cardId
      if (state.selectedCards.includes(cardId)) {
        card.classList.add('selected')
      }
    })
  }
  
  // 恢复视图模式
  if (state.viewMode) {
    const viewModeBtn = document.querySelector(`.view-mode-btn[data-mode="${state.viewMode}"]`)
    if (viewModeBtn) {
      (viewModeBtn as HTMLElement).click()
    }
  }
  
  // 恢复搜索词
  if (state.searchTerm) {
    const searchInput = document.querySelector('.global-search input') as HTMLInputElement
    if (searchInput) {
      searchInput.value = state.searchTerm
    }
  }
}

// 应用架构图状态
const applyArchitectureState = (state: any) => {
  const architectureElement = document.querySelector('.architecture-layer')
  if (!architectureElement || !state) return
  
  // 恢复视图模式
  if (state.viewMode) {
    const viewModeBtn = document.querySelector(`.view-mode-btn[data-mode="${state.viewMode}"]`)
    if (viewModeBtn) {
      (viewModeBtn as HTMLElement).click()
    }
  }
  
  // 恢复选中的节点
  if (state.selectedNodes) {
    document.querySelectorAll('.network-node').forEach(node => {
      const nodeId = (node as HTMLElement).dataset.nodeId
      if (state.selectedNodes.includes(nodeId)) {
        node.classList.add('selected')
      }
    })
  }
  
  // 恢复缩放级别
  if (state.zoomLevel) {
    const zoomLevelElement = document.querySelector('.zoom-level')
    if (zoomLevelElement) {
      zoomLevelElement.textContent = state.zoomLevel.toString()
    }
  }
  
  // 恢复平移位置
  if (state.panPosition) {
    const canvas = document.querySelector('.network-canvas') as HTMLElement
    if (canvas) {
      canvas.style.transform = `translate(${state.panPosition.x}px, ${state.panPosition.y}px)`
    }
  }
}

// 应用监控状态
const applyMonitoringState = (state: any) => {
  const monitoringElement = document.querySelector('.monitoring-layer')
  if (!monitoringElement || !state) return
  
  // 恢复视图模式
  if (state.viewMode) {
    const viewModeBtn = document.querySelector(`.view-mode-btn[data-mode="${state.viewMode}"]`)
    if (viewModeBtn) {
      (viewModeBtn as HTMLElement).click()
    }
  }
  
  // 恢复屏幕布局
  if (state.screenLayout) {
    state.screenLayout.forEach((screen: any) => {
      const screenElement = document.querySelector(`[data-screen-id="${screen.id}"]`) as HTMLElement
      if (screenElement) {
        Object.assign(screenElement.style, screen.position)
      }
    })
  }
  
  // 恢复预警筛选
  if (state.alertFilters) {
    // 重置所有筛选器
    document.querySelectorAll('.alert-filters input').forEach(input => {
      (input as HTMLInputElement).checked = false
    })
    
    // 应用保存的筛选器
    if (state.alertFilters.levels) {
      state.alertFilters.levels.forEach((level: string) => {
        const input = document.querySelector(`.alert-filters input[value="${level}"]`) as HTMLInputElement
        if (input) input.checked = true
      })
    }
    
    if (state.alertFilters.types) {
      state.alertFilters.types.forEach((type: string) => {
        const input = document.querySelector(`.alert-filters input[value="${type}"]`) as HTMLInputElement
        if (input) input.checked = true
      })
    }
  }
}

// 键盘快捷键处理
const handleKeyboardShortcuts = (event: KeyboardEvent) => {
  // Alt + 1/2/3: 切换层级
  if (event.altKey) {
    switch (event.key) {
      case '1':
        event.preventDefault()
        handleLayerChange(1)
        break
      case '2':
        event.preventDefault()
        handleLayerChange(2)
        break
      case '3':
        event.preventDefault()
        handleLayerChange(3)
        break
    }
  }
  
  // Ctrl + S: 保存状态
  if (event.ctrlKey && event.key === 's') {
    event.preventDefault()
    saveCurrentState()
  }
  
  // Ctrl + E: 打开工程师工具箱
  if (event.ctrlKey && event.key === 'e') {
    event.preventDefault()
    navigateToEngineerToolbox()
  }
}

// 生命周期
onMounted(() => {
  // 添加键盘事件监听
  document.addEventListener('keydown', handleKeyboardShortcuts)
  
  // 恢复初始状态
  restoreLayerState(currentLayer.value)
  
  // 初始化状态存储
  appStore.initializeFunctionState(functionId.value)
})

onUnmounted(() => {
  // 保存最终状态
  saveCurrentState()
  
  // 清理定时器
  if (stateSaveTimer.value) {
    clearTimeout(stateSaveTimer.value)
  }
  
  // 移除事件监听
  document.removeEventListener('keydown', handleKeyboardShortcuts)
})
</script>

<style lang="scss" scoped>
.function-layer {
  position: relative;
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-deep);
  overflow: hidden;
}

.layer-content {
  flex: 1;
  position: relative;
  overflow: hidden;
}

// 层级切换动画
.layer-transition-enter-active,
.layer-transition-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.layer-transition-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.layer-transition-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.transition-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, 
    rgba(37, 99, 235, 0.1) 0%, 
    rgba(124, 58, 237, 0.1) 50%, 
    rgba(16, 185, 129, 0.1) 100%);
  pointer-events: none;
  z-index: 100;
}

// 状态保持指示器
.state-indicator {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: rgba(26, 26, 46, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  z-index: 1000;
  
  .loading-spinner {
    width: 24px;
    height: 24px;
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-top: 2px solid var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  span {
    color: var(--text-primary);
    font-size: 14px;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>