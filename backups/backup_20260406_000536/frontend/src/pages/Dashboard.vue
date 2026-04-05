<template>
  <div class="dashboard">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-system" ref="particleSystem"></div>
      <div class="data-flow-field" ref="dataFlowField"></div>
      <div class="grid-overlay" ref="gridOverlay"></div>
    </div>

    <!-- 主界面容器 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <div class="top-navigation">
        <div class="nav-left">
          <div class="brand-section">
            <div class="brand-logo">
              <div class="logo-core"></div>
              <span class="brand-text">Quant-UI</span>
            </div>
            <div class="brand-subtitle">智能量化交易平台</div>
          </div>
        </div>
        
        <div class="nav-center">
          <div class="view-switcher">
            <div
              v-for="view in viewModes"
              :key="view.id"
              :class="['view-mode', { active: currentView === view.id }]"
              @click="switchView(view.id)"
            >
              <n-icon size="20" :component="view.icon" />
              <span>{{ view.name }}</span>
            </div>
          </div>
        </div>
        
        <div class="nav-right">
          <div class="user-section">
            <n-dropdown trigger="hover" :options="userMenuOptions">
              <div class="user-avatar">
                <div class="avatar-glow"></div>
                <n-avatar round size="medium">
                  {{ userStore.profile?.name?.charAt(0) || 'U' }}
                </n-avatar>
              </div>
            </n-dropdown>
          </div>
          
          <div class="global-actions">
            <n-button circle size="large" text @click="toggleGlobalSearch">
              <n-icon size="20" :component="SearchIcon" />
            </n-button>
            
            <n-button circle size="large" text @click="toggleNotifications">
              <n-icon size="20" :component="NotificationsIcon" />
              <n-badge :value="notificationCount" :max="99" />
            </n-button>
            
            <n-button circle size="large" text @click="openEngineerToolbox">
              <n-icon size="20" :component="ToolsIcon" />
            </n-button>
          </div>
        </div>
      </div>

      <!-- 功能卡片展示区 -->
      <div class="function-cards-area" ref="cardsContainer">
        <!-- 网格视图 -->
        <div v-if="currentView === 'grid'" class="grid-view">
          <div
            v-for="module in functionModules"
            :key="module.id"
            :class="['function-card', { dragging: isDragging(module.id) }]"
            :style="getCardStyle(module)"
            @click="enterFunction(module)"
            @mousedown="startDrag(module, $event)"
            @mouseenter="highlightCard(module)"
            @mouseleave="unhighlightCard(module)"
          >
            <!-- 卡片光环效果 -->
            <div class="card-aura" :class="{ active: highlightedCard === module.id }"></div>
            
            <!-- 卡片内容 -->
            <div class="card-content">
              <div class="card-header">
                <div class="card-icon-wrapper">
                  <n-icon size="32" :component="getModuleIcon(module.icon)" />
                  <div class="status-indicator" :class="module.status"></div>
                </div>
                
                <div class="card-category">
                  <span class="category-badge" :style="{ backgroundColor: getCategoryColor(module.category) }">
                    {{ getCategoryName(module.category) }}
                  </span>
                </div>
              </div>
              
              <div class="card-body">
                <h3 class="card-title">{{ module.name }}</h3>
                <p class="card-description">{{ module.description }}</p>
                
                <div class="card-metrics" v-if="module.metrics">
                  <div
                    v-for="metric in module.metrics"
                    :key="metric.label"
                    class="metric-item"
                  >
                    <span class="metric-label">{{ metric.label }}</span>
                    <div class="metric-value-wrapper">
                      <span class="metric-value">{{ metric.value }}</span>
                      <n-icon
                        v-if="metric.trend"
                        size="14"
                        :component="getTrendIcon(metric.trend)"
                        :class="['trend-icon', metric.trend]"
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="card-footer">
                <div class="card-actions">
                  <n-button size="small" type="primary" ghost>
                    进入功能
                  </n-button>
                  <n-button size="small" text>
                    <n-icon :component="MoreIcon" />
                  </n-button>
                </div>
              </div>
            </div>
            
            <!-- 拖拽手柄 -->
            <div v-if="isDragMode" class="drag-handle">
              <n-icon :component="DragIcon" />
            </div>
          </div>
        </div>

        <!-- 3D视图 -->
        <div v-else-if="currentView === '3d'" class="three-d-view">
          <div class="three-d-container" ref="threeDContainer">
            <!-- 3D功能卡片将在这里渲染 -->
            <div class="three-d-placeholder">
              <n-icon size="64" :component="CubeIcon" />
              <p>3D视图开发中...</p>
            </div>
          </div>
        </div>

        <!-- 时间线视图 -->
        <div v-else-if="currentView === 'timeline'" class="timeline-view">
          <div class="timeline-container" ref="timelineContainer">
            <div class="timeline-track">
              <div
                v-for="(event, index) in timelineEvents"
                :key="index"
                class="timeline-event"
              >
                <div class="event-marker">
                  <div class="marker-dot"></div>
                  <div class="marker-line"></div>
                </div>
                <div class="event-content">
                  <h4>{{ event.title }}</h4>
                  <p>{{ event.description }}</p>
                  <span class="event-time">{{ event.time }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部状态栏 -->
      <div class="bottom-status-bar">
        <div class="status-left">
          <div class="status-item">
            <div class="status-indicator online"></div>
            <span>系统正常</span>
          </div>
          <div class="status-item">
            <span>{{ functionModules.length }} 个功能模块</span>
          </div>
          <div class="status-item">
            <span>数据延迟: {{ dataLatency }}ms</span>
          </div>
        </div>
        
        <div class="status-center">
          <div class="quick-launch">
            <span class="quick-launch-label">快速启动</span>
            <div class="quick-launch-buttons">
              <n-button
                v-for="quick in quickLaunchItems"
                :key="quick.id"
                size="small"
                type="tertiary"
                @click="quickLaunch(quick.id)"
              >
                <n-icon size="14" :component="quick.icon" />
              </n-button>
            </div>
          </div>
        </div>
        
        <div class="status-right">
          <div class="system-info">
            <span>CPU: {{ systemMetrics.cpu }}%</span>
            <span>内存: {{ systemMetrics.memory }}%</span>
            <span>{{ currentTime }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 全局搜索模态 -->
    <div v-if="showGlobalSearch" class="global-search-modal" @click="closeGlobalSearch">
      <div class="search-modal-content" @click.stop>
        <div class="search-input-wrapper">
          <n-input
            v-model:value="globalSearchQuery"
            size="large"
            placeholder="搜索功能、数据、设置..."
            ref="globalSearchInput"
            @keydown="handleGlobalSearchKeydown"
          >
            <template #prefix>
              <n-icon size="24" :component="SearchIcon" />
            </template>
          </n-input>
        </div>
        
        <div v-if="globalSearchResults.length > 0" class="search-results">
          <div
            v-for="result in globalSearchResults"
            :key="result.id"
            class="search-result-item"
            @click="navigateToResult(result)"
          >
            <n-icon size="20" :component="result.icon" />
            <div class="result-info">
              <div class="result-title">{{ result.title }}</div>
              <div class="result-description">{{ result.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore, useAppStore } from '@/stores'
import { functionModules, functionCategories } from '@/configs/functionConfig'
import {
  SearchOutline as SearchIcon,
  NotificationsOutline as NotificationsIcon,
  ConstructOutline as ToolsIcon,
  GridOutline as GridIcon,
  CubeOutline as CubeIcon,
  TimeOutline as TimeIcon,
  EllipsisHorizontalOutline as MoreIcon,
  TrendingUpOutline as TrendUpIcon,
  TrendingDownOutline as TrendDownIcon,
  RemoveOutline as TrendStableIcon,
  ReorderFourOutline as DragIcon,
  AnalyticsOutline as AnalyticsIcon,
  ServerOutline as DatabaseIcon,
  FlaskOutline as ExperimentIcon,
  AccessibilityOutline as RobotIcon,
  TrendingUpOutline as TradingIcon,
  DesktopOutline as MonitorIcon,
  BarChartOutline as ChartIcon
} from '@vicons/ionicons5'

// 状态管理
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

// 响应式数据
const currentView = ref('grid')
const showGlobalSearch = ref(false)
const globalSearchQuery = ref('')
const globalSearchResults = ref<any[]>([])
const highlightedCard = ref<string | null>(null)
const isDragMode = ref(false)
const draggingCard = ref<string | null>(null)
const cardPositions = ref<Record<string, { x: number, y: number }>>({})
const notificationCount = ref(5)
const dataLatency = ref(24)
const currentTime = ref('')
const systemMetrics = ref({
  cpu: 45,
  memory: 62
})

// DOM引用
const particleSystem = ref<HTMLElement>()
const dataFlowField = ref<HTMLElement>()
const gridOverlay = ref<HTMLElement>()
const cardsContainer = ref<HTMLElement>()
const threeDContainer = ref<HTMLElement>()
const timelineContainer = ref<HTMLElement>()
const globalSearchInput = ref()

// 视图模式
const viewModes = [
  { id: 'grid', name: '网格视图', icon: GridIcon },
  { id: '3d', name: '3D视图', icon: CubeIcon },
  { id: 'timeline', name: '时间线', icon: TimeIcon }
]

// 用户菜单选项
const userMenuOptions = [
  { label: '个人设置', key: 'profile' },
  { label: '系统设置', key: 'settings' },
  { label: '退出登录', key: 'logout' }
]

// 快速启动项
const quickLaunchItems = [
  { id: 'data-management', icon: DatabaseIcon },
  { id: 'backtest', icon: ExperimentIcon },
  { id: 'ai-strategy', icon: RobotIcon }
]

// 时间线事件
const timelineEvents = ref([
  {
    title: '系统启动',
    description: 'Quant-UI系统成功启动，所有模块正常运行',
    time: '09:00:00'
  },
  {
    title: '数据更新',
    description: '股票数据已更新，共4,521支股票',
    time: '09:15:32'
  },
  {
    title: 'AI训练完成',
    description: '模型训练任务完成，准确率提升至92.1%',
    time: '10:30:15'
  }
])

// 计算属性
const getModuleIcon = (iconName: string) => {
  const iconMap: Record<string, any> = {
    'database': DatabaseIcon,
    'experiment': ExperimentIcon,
    'robot': RobotIcon,
    'trading': TradingIcon,
    'monitor': MonitorIcon,
    'chart': ChartIcon,
    'tools': ToolsIcon,
    'grid': GridIcon,
    'architecture': AnalyticsIcon,
    'dashboard': GridIcon,
    'database-debug': DatabaseIcon,
    'experiment-debug': ExperimentIcon,
    'robot-debug': RobotIcon,
    'trading-debug': TradingIcon,
    'monitor-debug': MonitorIcon,
    'chart-debug': ChartIcon
  }
  return iconMap[iconName] || GridIcon
}

const getCategoryColor = (categoryId: string) => {
  const category = functionCategories.find(c => c.id === categoryId)
  return category?.color || '#2563eb'
}

const getCategoryName = (categoryId: string) => {
  const category = functionCategories.find(c => c.id === categoryId)
  return category?.name || '未知'
}

const getTrendIcon = (trend: string) => {
  const iconMap: Record<string, any> = {
    'up': TrendUpIcon,
    'down': TrendDownIcon,
    'stable': TrendStableIcon
  }
  return iconMap[trend] || TrendStableIcon
}

const getCardStyle = (module: any) => {
  const position = cardPositions.value[module.id]
  if (!position) return {}
  
  return {
    transform: `translate(${position.x}px, ${position.y}px)`,
    zIndex: draggingCard.value === module.id ? 1000 : 1
  }
}

// 方法
const switchView = (viewId: string) => {
  currentView.value = viewId
}

const enterFunction = (module: any) => {
  // 直接跳转到第二层架构图
  router.push(`/function/${module.id}/architecture`)
}

const openEngineerToolbox = () => {
  router.push('/engineer-toolbox')
}

const toggleGlobalSearch = () => {
  showGlobalSearch.value = true
  nextTick(() => {
    globalSearchInput.value?.focus()
  })
}

const closeGlobalSearch = () => {
  showGlobalSearch.value = false
  globalSearchQuery.value = ''
  globalSearchResults.value = []
}

const handleGlobalSearchKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    closeGlobalSearch()
  }
}

const toggleNotifications = () => {
  // 实现通知面板
  console.log('Toggle notifications')
}

const highlightCard = (module: any) => {
  highlightedCard.value = module.id
}

const unhighlightCard = (module: any) => {
  if (highlightedCard.value === module.id) {
    highlightedCard.value = null
  }
}

const quickLaunch = (moduleId: string) => {
  const module = functionModules.find(m => m.id === moduleId)
  if (module) {
    enterFunction(module)
  }
}

const navigateToResult = (result: any) => {
  router.push(result.path)
  closeGlobalSearch()
}

// 拖拽功能
const startDrag = (module: any, event: MouseEvent) => {
  if (!isDragMode.value) return
  
  draggingCard.value = module.id
  const startX = event.clientX - cardPositions.value[module.id].x
  const startY = event.clientY - cardPositions.value[module.id].y
  
  const handleMouseMove = (e: MouseEvent) => {
    if (draggingCard.value === module.id) {
      cardPositions.value[module.id] = {
        x: e.clientX - startX,
        y: e.clientY - startY
      }
    }
  }
  
  const handleMouseUp = () => {
    draggingCard.value = null
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const isDragging = (moduleId: string) => {
  return draggingCard.value === moduleId
}

// 初始化卡片位置
const initializeCardPositions = () => {
  const positions: Record<string, { x: number, y: number }> = {}
  const cols = 4
  const cardWidth = 320
  const cardHeight = 240
  const gap = 24
  
  functionModules.forEach((module, index) => {
    const row = Math.floor(index / cols)
    const col = index % cols
    positions[module.id] = {
      x: col * (cardWidth + gap),
      y: row * (cardHeight + gap)
    }
  })
  
  cardPositions.value = positions
}

// 粒子系统
const initParticleSystem = () => {
  if (!particleSystem.value) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  particleSystem.value.appendChild(canvas)
  
  const particles: any[] = []
  const particleCount = 80
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      size: Math.random() * 1.5 + 0.5,
      opacity: Math.random() * 0.3 + 0.1,
      color: `hsl(${Math.random() * 60 + 200}, 70%, 50%)`
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    particles.forEach(particle => {
      particle.x += particle.vx
      particle.y += particle.vy
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1
      if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fillStyle = particle.color.replace('50%)', `${particle.opacity * 100}%)`)
      ctx.fill()
    })
    
    // 连接临近粒子
    particles.forEach((p1, i) => {
      particles.slice(i + 1).forEach(p2 => {
        const distance = Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
        if (distance < 100) {
          ctx.beginPath()
          ctx.moveTo(p1.x, p1.y)
          ctx.lineTo(p2.x, p2.y)
          ctx.strokeStyle = `rgba(139, 92, 246, ${0.1 * (1 - distance / 100)})`
          ctx.stroke()
        }
      })
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 数据流动画
const initDataFlowAnimation = () => {
  if (!dataFlowField.value) return
  
  const createDataFlow = () => {
    const flow = document.createElement('div')
    flow.className = 'data-flow-line'
    flow.style.cssText = `
      position: absolute;
      width: 1px;
      height: 80px;
      background: linear-gradient(to bottom, transparent, #8b5cf6, transparent);
      left: ${Math.random() * 100}%;
      top: -80px;
      opacity: 0.4;
      animation: dataFlow 4s linear infinite;
      transform: rotate(${Math.random() * 60 - 30}deg);
    `
    
    dataFlowField.value.appendChild(flow)
    
    setTimeout(() => {
      flow.remove()
    }, 4000)
  }
  
  setInterval(createDataFlow, 800)
}

// 网格背景
const initGridOverlay = () => {
  if (!gridOverlay.value) return
  
  const grid = document.createElement('div')
  grid.className = 'grid-pattern'
  grid.style.cssText = `
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
      linear-gradient(rgba(139, 92, 246, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(139, 92, 246, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
  `
  
  gridOverlay.value.appendChild(grid)
}

// 更新时间
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN')
}

// 监听搜索
watch(globalSearchQuery, (newQuery) => {
  if (newQuery.trim()) {
    // 模拟搜索结果
    globalSearchResults.value = functionModules
      .filter(module =>
        module.name.toLowerCase().includes(newQuery.toLowerCase()) ||
        module.description.toLowerCase().includes(newQuery.toLowerCase())
      )
      .map(module => ({
        id: module.id,
        title: module.name,
        description: module.description,
        icon: getModuleIcon(module.icon),
        path: `/function/${module.id}`
      }))
  } else {
    globalSearchResults.value = []
  }
})

// 生命周期
onMounted(() => {
  initializeCardPositions()
  
  nextTick(() => {
    initParticleSystem()
    initDataFlowAnimation()
    initGridOverlay()
  })
  
  updateTime()
  setInterval(updateTime, 1000)
  
  // 键盘快捷键
  const handleKeydown = (event: KeyboardEvent) => {
    if (event.ctrlKey || event.metaKey) {
      switch (event.key) {
        case 'k':
          event.preventDefault()
          toggleGlobalSearch()
          break
        case 'd':
          event.preventDefault()
          isDragMode.value = !isDragMode.value
          break
      }
    }
  }
  
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  // 清理动画
  if (particleSystem.value) {
    particleSystem.value.innerHTML = ''
  }
  if (dataFlowField.value) {
    dataFlowField.value.innerHTML = ''
  }
})
</script>

<style lang="scss" scoped>
.dashboard {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-deep);
  
  .immersive-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    
    .particle-system {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    
    .data-flow-field {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
    }
    
    .grid-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
  }
  
  .main-container {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  
  .top-navigation {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-4) var(--spacing-6);
    background: rgba(var(--surface-color), 0.05);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(var(--border-color), 0.1);
    
    .nav-left {
      .brand-section {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-1);
        
        .brand-logo {
          display: flex;
          align-items: center;
          gap: var(--spacing-2);
          
          .logo-core {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            border-radius: var(--border-radius-lg);
            position: relative;
            
            &::after {
              content: '';
              position: absolute;
              top: -4px;
              right: -4px;
              width: 8px;
              height: 8px;
              background: var(--success-color);
              border-radius: 50%;
              box-shadow: 0 0 8px rgba(var(--success-color), 0.6);
            }
          }
          
          .brand-text {
            font-size: var(--font-size-xl);
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: 1px;
          }
        }
        
        .brand-subtitle {
          font-size: var(--font-size-xs);
          color: var(--text-secondary);
          margin-left: var(--spacing-10);
        }
      }
    }
    
    .nav-center {
      .view-switcher {
        display: flex;
        gap: var(--spacing-2);
        background: rgba(var(--surface-color), 0.1);
        border-radius: var(--border-radius-lg);
        padding: var(--spacing-1);
        
        .view-mode {
          display: flex;
          align-items: center;
          gap: var(--spacing-1);
          padding: var(--spacing-2) var(--spacing-3);
          border-radius: var(--border-radius-md);
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            background: rgba(var(--primary-color), 0.1);
          }
          
          &.active {
            background: var(--primary-color);
            color: white;
          }
        }
      }
    }
    
    .nav-right {
      display: flex;
      align-items: center;
      gap: var(--spacing-4);
      
      .user-section {
        .user-avatar {
          position: relative;
          cursor: pointer;
          
          .avatar-glow {
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            border-radius: 50%;
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            z-index: -1;
            opacity: 0.6;
          }
        }
      }
      
      .global-actions {
        display: flex;
        gap: var(--spacing-2);
      }
    }
  }
  
  .function-cards-area {
    flex: 1;
    position: relative;
    padding: var(--spacing-6);
    overflow: auto;
    
    .grid-view {
      position: relative;
      min-height: 100%;
      
      .function-card {
        position: absolute;
        width: 320px;
        height: 240px;
        background: rgba(var(--surface-color), 0.1);
        border: 1px solid rgba(var(--border-color), 0.2);
        border-radius: var(--border-radius-xl);
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
        
        &:hover {
          transform: translateY(-8px) scale(1.02);
          background: rgba(var(--surface-color), 0.2);
          border-color: rgba(var(--primary-color), 0.4);
          
          .card-aura {
            opacity: 1;
          }
        }
        
        &.dragging {
          cursor: grabbing;
          z-index: 1000;
          opacity: 0.8;
        }
        
        .card-aura {
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: radial-gradient(circle, rgba(var(--primary-color), 0.1) 0%, transparent 70%);
          opacity: 0;
          transition: opacity 0.4s ease;
          pointer-events: none;
        }
        
        .card-content {
          position: relative;
          z-index: 2;
          padding: var(--spacing-5);
          height: 100%;
          display: flex;
          flex-direction: column;
          
          .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: var(--spacing-3);
            
            .card-icon-wrapper {
              position: relative;
              
              .status-indicator {
                position: absolute;
                top: -4px;
                right: -4px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                
                &.online {
                  background: var(--success-color);
                  box-shadow: 0 0 8px rgba(var(--success-color), 0.6);
                }
                
                &.offline {
                  background: var(--error-color);
                  box-shadow: 0 0 8px rgba(var(--error-color), 0.6);
                }
                
                &.warning {
                  background: var(--warning-color);
                  box-shadow: 0 0 8px rgba(var(--warning-color), 0.6);
                }
              }
            }
            
            .card-category {
              .category-badge {
                padding: var(--spacing-1) var(--spacing-2);
                border-radius: var(--border-radius-full);
                font-size: var(--font-size-xs);
                font-weight: 500;
                color: white;
              }
            }
          }
          
          .card-body {
            flex: 1;
            
            .card-title {
              font-size: var(--font-size-lg);
              font-weight: 600;
              color: var(--text-primary);
              margin: 0 0 var(--spacing-2) 0;
            }
            
            .card-description {
              color: var(--text-secondary);
              font-size: var(--font-size-sm);
              line-height: 1.4;
              margin: 0 0 var(--spacing-4) 0;
            }
            
            .card-metrics {
              display: flex;
              flex-direction: column;
              gap: var(--spacing-2);
              
              .metric-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                
                .metric-label {
                  font-size: var(--font-size-xs);
                  color: var(--text-tertiary);
                }
                
                .metric-value-wrapper {
                  display: flex;
                  align-items: center;
                  gap: var(--spacing-1);
                  
                  .metric-value {
                    font-size: var(--font-size-sm);
                    font-weight: 600;
                    color: var(--text-primary);
                  }
                  
                  .trend-icon {
                    &.up {
                      color: var(--success-color);
                    }
                    
                    &.down {
                      color: var(--error-color);
                    }
                    
                    &.stable {
                      color: var(--text-secondary);
                    }
                  }
                }
              }
            }
          }
          
          .card-footer {
            .card-actions {
              display: flex;
              justify-content: space-between;
              align-items: center;
            }
          }
        }
        
        .drag-handle {
          position: absolute;
          top: var(--spacing-2);
          right: var(--spacing-2);
          opacity: 0;
          transition: opacity 0.3s ease;
          color: var(--text-tertiary);
        }
        
        &:hover .drag-handle {
          opacity: 1;
        }
      }
    }
    
    .three-d-view {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .three-d-placeholder {
        text-align: center;
        color: var(--text-secondary);
      }
    }
    
    .timeline-view {
      height: 100%;
      overflow-y: auto;
      
      .timeline-container {
        padding: var(--spacing-6);
        
        .timeline-track {
          position: relative;
          padding-left: var(--spacing-6);
          
          .timeline-event {
            position: relative;
            margin-bottom: var(--spacing-6);
            
            .event-marker {
              position: absolute;
              left: calc(-1 * var(--spacing-6));
              top: 0;
              
              .marker-dot {
                width: 12px;
                height: 12px;
                background: var(--primary-color);
                border-radius: 50%;
                box-shadow: 0 0 12px rgba(var(--primary-color), 0.4);
              }
              
              .marker-line {
                position: absolute;
                top: 12px;
                left: 5px;
                width: 2px;
                height: calc(100% + var(--spacing-4));
                background: linear-gradient(to bottom, var(--primary-color), transparent);
              }
            }
            
            .event-content {
              background: rgba(var(--surface-color), 0.1);
              border: 1px solid rgba(var(--border-color), 0.2);
              border-radius: var(--border-radius-lg);
              padding: var(--spacing-4);
              
              h4 {
                margin: 0 0 var(--spacing-2) 0;
                color: var(--text-primary);
              }
              
              p {
                margin: 0 0 var(--spacing-2) 0;
                color: var(--text-secondary);
                font-size: var(--font-size-sm);
              }
              
              .event-time {
                font-size: var(--font-size-xs);
                color: var(--text-tertiary);
              }
            }
          }
        }
      }
    }
  }
  
  .bottom-status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-3) var(--spacing-6);
    background: rgba(var(--surface-color), 0.05);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(var(--border-color), 0.1);
    
    .status-left {
      display: flex;
      gap: var(--spacing-6);
      
      .status-item {
        display: flex;
        align-items: center;
        gap: var(--spacing-2);
        
        .status-indicator {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          
          &.online {
            background: var(--success-color);
            box-shadow: 0 0 8px rgba(var(--success-color), 0.6);
          }
        }
      }
    }
    
    .status-center {
      .quick-launch {
        display: flex;
        align-items: center;
        gap: var(--spacing-3);
        
        .quick-launch-label {
          font-size: var(--font-size-sm);
          color: var(--text-secondary);
        }
        
        .quick-launch-buttons {
          display: flex;
          gap: var(--spacing-1);
        }
      }
    }
    
    .status-right {
      .system-info {
        display: flex;
        gap: var(--spacing-4);
        font-size: var(--font-size-xs);
        color: var(--text-tertiary);
        font-family: 'JetBrains Mono', monospace;
      }
    }
  }
  
  .global-search-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(var(--bg-deep), 0.95);
    backdrop-filter: blur(20px);
    z-index: 1000;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 15vh;
    
    .search-modal-content {
      background: rgba(var(--surface-color), 0.9);
      border: 1px solid rgba(var(--border-color), 0.2);
      border-radius: var(--border-radius-xl);
      padding: var(--spacing-6);
      width: 600px;
      max-width: 90vw;
      
      .search-input-wrapper {
        margin-bottom: var(--spacing-4);
      }
      
      .search-results {
        max-height: 400px;
        overflow-y: auto;
        
        .search-result-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-3);
          padding: var(--spacing-3);
          border-radius: var(--border-radius-lg);
          cursor: pointer;
          transition: background 0.2s ease;
          
          &:hover {
            background: rgba(var(--primary-color), 0.1);
          }
          
          .result-info {
            .result-title {
              font-size: var(--font-size-sm);
              color: var(--text-primary);
              font-weight: 500;
            }
            
            .result-description {
              font-size: var(--font-size-xs);
              color: var(--text-secondary);
              margin-top: var(--spacing-1);
            }
          }
        }
      }
    }
  }
}

// 动画定义
@keyframes dataFlow {
  0% {
    transform: translateY(-80px);
  }
  100% {
    transform: translateY(calc(100vh + 80px));
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .dashboard {
    .function-cards-area {
      .grid-view .function-card {
        width: 280px;
        height: 200px;
      }
    }
  }
}

@media (max-width: 768px) {
  .dashboard {
    .top-navigation {
      flex-direction: column;
      gap: var(--spacing-4);
      padding: var(--spacing-3);
      
      .nav-left .brand-section .brand-subtitle {
        margin-left: 0;
      }
      
      .nav-center .view-switcher {
        order: -1;
      }
    }
    
    .function-cards-area {
      padding: var(--spacing-3);
      
      .grid-view .function-card {
        width: 100%;
        height: auto;
        position: relative;
        margin-bottom: var(--spacing-3);
      }
    }
    
    .bottom-status-bar {
      flex-direction: column;
      gap: var(--spacing-3);
      padding: var(--spacing-3);
      
      .status-left,
      .status-center,
      .status-right {
        width: 100%;
        justify-content: center;
      }
    }
    
    .global-search-modal .search-modal-content {
      width: 95vw;
    }
  }
}
</style>