<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="top-header">
      <div class="header-left">
        <div class="logo">
          <img src="/logo.svg" alt="Quant-UI" class="logo-image" />
          <span class="logo-text">Quant-UI</span>
        </div>
        <nav class="main-nav">
          <router-link 
            v-for="item in navigationItems" 
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path.startsWith(item.path) }"
          >
            <i :class="item.icon"></i>
            <span>{{ item.name }}</span>
          </router-link>
        </nav>
      </div>
      
      <div class="header-right">
        <!-- 全局搜索 -->
        <div class="global-search">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            placeholder="搜索功能、数据或设置..."
            v-model="searchQuery"
            @keyup.enter="handleSearch"
          />
        </div>
        
        <!-- 语音助手 -->
        <button class="voice-assistant" @click="toggleVoiceAssistant">
          <i class="fas fa-microphone"></i>
        </button>
        
        <!-- 用户菜单 -->
        <div class="user-menu" @click="toggleUserMenu">
          <img :src="userAvatar" alt="用户头像" class="user-avatar" />
          <span class="user-name">{{ userName }}</span>
          <i class="fas fa-chevron-down"></i>
        </div>
        
        <!-- 主题切换 -->
        <button class="theme-toggle" @click="toggleTheme">
          <i :class="isDarkTheme ? 'fas fa-sun' : 'fas fa-moon'"></i>
        </button>
      </div>
    </header>
    
    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <h3>快捷操作</h3>
          <button class="collapse-btn" @click="toggleSidebar">
            <i :class="sidebarCollapsed ? 'fas fa-expand' : 'fas fa-compress'"></i>
          </button>
        </div>
        
        <div class="sidebar-content">
          <!-- 快捷操作 -->
          <div class="quick-actions">
            <div 
              v-for="action in quickActions" 
              :key="action.id"
              class="action-item"
              @click="handleQuickAction(action)"
            >
              <i :class="action.icon"></i>
              <span v-if="!sidebarCollapsed">{{ action.name }}</span>
            </div>
          </div>
          
          <!-- 功能卡片 -->
          <div class="function-cards" v-if="!sidebarCollapsed">
            <h4>功能卡片</h4>
            <div 
              v-for="card in functionCards" 
              :key="card.id"
              class="card-item"
              :class="{ active: activeCard === card.id }"
              @click="handleCardSelect(card)"
            >
              <i :class="card.icon"></i>
              <span>{{ card.name }}</span>
              <div class="card-status" :class="card.status"></div>
            </div>
          </div>
          
          <!-- 系统监控 -->
          <div class="system-monitor" v-if="!sidebarCollapsed">
            <h4>系统监控</h4>
            <div class="monitor-item">
              <span>CPU使用率</span>
              <div class="progress-bar">
                <div class="progress" :style="{ width: systemStatus.cpu + '%' }"></div>
              </div>
              <span>{{ systemStatus.cpu }}%</span>
            </div>
            <div class="monitor-item">
              <span>内存使用</span>
              <div class="progress-bar">
                <div class="progress" :style="{ width: systemStatus.memory + '%' }"></div>
              </div>
              <span>{{ systemStatus.memory }}%</span>
            </div>
            <div class="monitor-item">
              <span>数据延迟</span>
              <span class="delay-value">{{ systemStatus.dataDelay }}ms</span>
            </div>
          </div>
        </div>
      </aside>
      
      <!-- 页面内容 -->
      <main class="page-content">
        <router-view />
      </main>
    </div>
    
    <!-- 底部状态栏 -->
    <footer class="bottom-status">
      <div class="status-left">
        <div class="status-item">
          <i class="fas fa-server"></i>
          <span>系统状态: {{ systemStatus.overall }}</span>
        </div>
        <div class="status-item">
          <i class="fas fa-database"></i>
          <span>数据延迟: {{ systemStatus.dataDelay }}ms</span>
        </div>
        <div class="status-item">
          <i class="fas fa-memory"></i>
          <span>内存使用: {{ systemStatus.memory }}%</span>
        </div>
      </div>
      
      <div class="status-center">
        <div class="realtime-data">
          <i class="fas fa-chart-line pulse"></i>
          <span>实时数据流</span>
        </div>
      </div>
      
      <div class="status-right">
        <!-- 数据更新进度条 -->
        <DataUpdateProgress ref="dataUpdateProgressRef" />

        <div class="alert-item" v-if="hasAlerts">
          <i class="fas fa-exclamation-triangle"></i>
          <span>{{ alertCount }} 条预警</span>
        </div>
        <div class="time-display">
          {{ currentTime }}
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore, useUserStore } from '@/stores'
import { storeToRefs } from 'pinia'
import DataUpdateProgress from '@/components/common/DataUpdateProgress.vue'

// 路由和状态管理
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

// 数据更新进度条引用
const dataUpdateProgressRef = ref<InstanceType<typeof DataUpdateProgress> | null>(null)

// 性能优化：使用storeToRefs解构（M2-16）
const { theme } = storeToRefs(appStore)
const { profile } = storeToRefs(userStore)

// 响应式数据
const searchQuery = ref('')
const sidebarCollapsed = ref(false)
const activeCard = ref('')
const currentTime = ref('')
const timeTimer = ref<number | null>(null)

// 导航项
const navigationItems = [
  { path: '/RealtimeQuotes', name: '实时行情', icon: 'fas fa-chart-line' },
  { path: '/function', name: '功能', icon: 'fas fa-cube' },
  { path: '/strategy', name: '策略', icon: 'fas fa-chess' },
  { path: '/backtest', name: '回测', icon: 'fas fa-flask' },
  { path: '/workflow', name: '工作流', icon: 'fas fa-project-diagram' },
  { path: '/research/ml/management', name: 'ML模型', icon: 'fas fa-brain' },
  { path: '/monitoring', name: '监控', icon: 'fas fa-chart-area' },
  { path: '/ai', name: 'AI助手', icon: 'fas fa-robot' }
]

// 快捷操作
const quickActions = [
  { id: 'new-strategy', name: '新建策略', icon: 'fas fa-plus' },
  { id: 'quick-backtest', name: '快速回测', icon: 'fas fa-play' },
  { id: 'data-refresh', name: '数据刷新', icon: 'fas fa-sync' },
  { id: 'report-export', name: '报告导出', icon: 'fas fa-download' }
]

// 功能卡片
const functionCards = [
  { id: 'data-overview', name: '数据概览', icon: 'fas fa-database', status: 'active' },
  { id: 'stock-selection', name: '智能选股', icon: 'fas fa-search', status: 'active' },
  { id: 'backtest-lab', name: '回测实验室', icon: 'fas fa-flask', status: 'active' },
  { id: 'ai-assistant', name: 'AI策略助手', icon: 'fas fa-robot', status: 'active' }
]

// 系统状态
const systemStatus = ref({
  cpu: 45,
  memory: 62,
  dataDelay: 12,
  overall: '正常'
})

// 计算属性
const isDarkTheme = computed(() => theme.value === 'dark')
const userAvatar = computed(() => profile.value?.avatar || '/default-avatar.png')
const userName = computed(() => profile.value?.name || '用户')
const hasAlerts = computed(() => alertCount.value > 0)
const alertCount = ref(3)

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const toggleTheme = () => {
  appStore.toggleTheme()
}

const toggleVoiceAssistant = () => {
  // 实现语音助手功能
  console.log('Toggle voice assistant')
}

const toggleUserMenu = () => {
  // 实现用户菜单功能
  console.log('Toggle user menu')
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // 实现搜索功能
    console.log('Search for:', searchQuery.value)
  }
}

const handleQuickAction = (action: any) => {
  console.log('Quick action:', action.id)
  // 根据action.id执行相应操作
}

const handleCardSelect = (card: any) => {
  activeCard.value = card.id
  router.push(`/function/${card.id}`)
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 生命周期
onMounted(() => {
  updateTime()
  timeTimer.value = setInterval(updateTime, 1000)
  
  // 模拟系统状态更新
  setInterval(() => {
    systemStatus.value.cpu = Math.floor(Math.random() * 30) + 30
    systemStatus.value.memory = Math.floor(Math.random() * 20) + 50
    systemStatus.value.dataDelay = Math.floor(Math.random() * 10) + 5
  }, 5000)
})

onUnmounted(() => {
  if (timeTimer.value) {
    clearInterval(timeTimer.value)
  }
})
</script>

<style lang="scss" scoped>
.main-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
}

// 顶部导航栏
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 24px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-color);
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 32px;
    
    .logo {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .logo-image {
        width: 32px;
        height: 32px;
      }
      
      .logo-text {
        font-size: 20px;
        font-weight: 600;
        color: var(--primary);
      }
    }
    
    .main-nav {
      display: flex;
      gap: 8px;
      
      .nav-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 8px;
        color: var(--text-secondary);
        text-decoration: none;
        transition: all 0.2s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.05);
          color: var(--text-primary);
        }
        
        &.active {
          background: var(--primary);
          color: white;
        }
      }
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .global-search {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 20px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      
      input {
        background: none;
        border: none;
        outline: none;
        color: var(--text-primary);
        width: 200px;
        
        &::placeholder {
          color: var(--text-secondary);
        }
      }
    }
    
    .voice-assistant,
    .theme-toggle {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
      }
    }
    
    .user-menu {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.05);
      }
      
      .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
      }
      
      .user-name {
        color: var(--text-primary);
      }
    }
  }
}

// 主内容区域
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

// 侧边栏
.sidebar {
  width: 280px;
  background: var(--bg-surface);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  
  &.collapsed {
    width: 80px;
  }
  
  .sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid var(--border-color);
    
    h3 {
      margin: 0;
      font-size: 16px;
      color: var(--text-primary);
    }
    
    .collapse-btn {
      background: none;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      padding: 4px;
      
      &:hover {
        color: var(--text-primary);
      }
    }
  }
  
  .sidebar-content {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    
    h4 {
      margin: 0 0 12px 0;
      font-size: 14px;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .quick-actions {
      margin-bottom: 24px;
      
      .action-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.05);
        }
        
        i {
          width: 20px;
          text-align: center;
          color: var(--primary);
        }
      }
    }
    
    .function-cards {
      margin-bottom: 24px;
      
      .card-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.05);
        }
        
        &.active {
          background: rgba(37, 99, 235, 0.1);
          border-left: 3px solid var(--primary);
        }
        
        i {
          width: 20px;
          text-align: center;
          color: var(--text-secondary);
        }
        
        .card-status {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-left: auto;
          
          &.active {
            background: var(--success);
          }
          
          &.warning {
            background: var(--warning);
          }
          
          &.error {
            background: var(--danger);
          }
        }
      }
    }
    
    .system-monitor {
      .monitor-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        
        .progress-bar {
          flex: 1;
          height: 4px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 2px;
          overflow: hidden;
          
          .progress {
            height: 100%;
            background: var(--primary);
            transition: width 0.3s ease;
          }
        }
        
        .delay-value {
          color: var(--success);
          font-weight: 500;
        }
      }
    }
  }
}

// 页面内容
.page-content {
  flex: 1;
  overflow: auto;
  padding: 24px;
}

// 底部状态栏
.bottom-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 48px;
  padding: 0 24px;
  background: var(--bg-surface);
  border-top: 1px solid var(--border-color);
  
  .status-left,
  .status-right {
    display: flex;
    align-items: center;
    gap: 24px;
    
    .status-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: var(--text-secondary);
      
      i {
        color: var(--primary);
      }
    }
    
    .alert-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: var(--warning);
      
      i {
        color: var(--warning);
      }
    }
  }
  
  .status-center {
    .realtime-data {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: var(--success);
      
      .pulse {
        animation: pulse 2s infinite;
      }
    }
  }
  
  .time-display {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>