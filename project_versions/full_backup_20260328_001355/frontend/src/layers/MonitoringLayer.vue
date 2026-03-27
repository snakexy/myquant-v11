<template>
  <div class="monitoring-layer">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-system" ref="particleSystem"></div>
      <div class="data-stream-overlay" ref="dataStreamOverlay"></div>
      <div class="grid-pattern"></div>
    </div>

    <!-- 顶部控制栏 -->
    <div class="top-control-bar">
      <div class="left-controls">
        <div class="monitoring-title">
          <h2>{{ currentFunction?.name }} - 实时监控</h2>
          <div class="status-indicator" :class="systemStatus">
            <span class="status-dot"></span>
            <span>{{ systemStatusText }}</span>
          </div>
        </div>
      </div>
      
      <div class="center-controls">
        <div class="view-mode-selector">
          <button
            v-for="mode in viewModes"
            :key="mode.id"
            :class="['view-mode-btn', { active: currentViewMode === mode.id }]"
            @click="switchViewMode(mode.id)"
          >
            <i :class="mode.icon"></i>
            <span>{{ mode.name }}</span>
          </button>
        </div>
      </div>
      
      <div class="right-controls">
        <div class="alert-controls">
          <button class="alert-filter-btn" @click="showAlertFilter = !showAlertFilter">
            <i class="fas fa-filter"></i>
            <span>预警筛选</span>
            <span v-if="activeAlerts.length > 0" class="alert-count">{{ activeAlerts.length }}</span>
          </button>
          <button class="alert-settings-btn" @click="showAlertSettings = true">
            <i class="fas fa-cog"></i>
          </button>
        </div>
        
        <div class="layout-controls">
          <button class="layout-btn" @click="showLayoutSelector = !showLayoutSelector">
            <i class="fas fa-th"></i>
            <span>布局</span>
          </button>
          <button class="fullscreen-btn" @click="toggleFullscreen">
            <i :class="isFullscreen ? 'fas fa-compress' : 'fas fa-expand'"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 主监控区域 -->
    <div class="main-monitoring-area" :class="currentViewMode">
      <!-- 多屏对比模式 -->
      <div v-if="currentViewMode === 'multi-screen'" class="multi-screen-layout">
        <div 
          v-for="(screen, index) in monitorScreens" 
          :key="screen.id"
          class="monitor-screen"
          :class="screen.size"
          :style="screen.position"
          @contextmenu.prevent="showScreenContextMenu($event, screen)"
        >
          <div class="screen-header">
            <div class="screen-title">
              <i :class="screen.icon"></i>
              <span>{{ screen.title }}</span>
            </div>
            <div class="screen-controls">
              <button class="minimize-btn" @click="minimizeScreen(screen.id)">
                <i class="fas fa-minus"></i>
              </button>
              <button class="maximize-btn" @click="maximizeScreen(screen.id)">
                <i class="fas fa-square"></i>
              </button>
              <button class="close-btn" @click="closeScreen(screen.id)">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
          
          <div class="screen-content">
            <component 
              :is="screen.component" 
              :config="screen.config"
              :realtime-data="screen.realtimeData"
              @update:data="updateScreenData(screen.id, $event)"
            />
          </div>
          
          <div class="screen-footer">
            <div class="performance-metrics">
              <span class="metric">延迟: {{ screen.latency }}ms</span>
              <span class="metric">更新: {{ screen.updateRate }}/s</span>
              <span class="metric">状态: {{ screen.status }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 预警墙模式 -->
      <div v-else-if="currentViewMode === 'alert-wall'" class="alert-wall-layout">
        <div class="alert-filters" v-if="showAlertFilter">
          <div class="filter-group">
            <label>预警级别</label>
            <div class="checkbox-group">
              <label v-for="level in alertLevels" :key="level.value" class="checkbox-label">
                <input 
                  type="checkbox" 
                  :value="level.value" 
                  v-model="selectedAlertLevels"
                >
                <span :class="['level-indicator', level.value]"></span>
                <span>{{ level.label }}</span>
              </label>
            </div>
          </div>
          
          <div class="filter-group">
            <label>预警类型</label>
            <div class="checkbox-group">
              <label v-for="type in alertTypes" :key="type.value" class="checkbox-label">
                <input 
                  type="checkbox" 
                  :value="type.value" 
                  v-model="selectedAlertTypes"
                >
                <span>{{ type.label }}</span>
              </label>
            </div>
          </div>
        </div>
        
        <div class="alert-wall">
          <div 
            v-for="alert in filteredAlerts" 
            :key="alert.id"
            class="alert-card"
            :class="[alert.level, alert.type]"
            @click="showAlertDetails(alert)"
          >
            <div class="alert-header">
              <div class="alert-icon">
                <i :class="getAlertIcon(alert)"></i>
              </div>
              <div class="alert-info">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
              </div>
              <div class="alert-actions">
                <button class="acknowledge-btn" @click.stop="acknowledgeAlert(alert.id)">
                  <i class="fas fa-check"></i>
                </button>
                <button class="dismiss-btn" @click.stop="dismissAlert(alert.id)">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            
            <div class="alert-content">
              <div class="alert-message">{{ alert.message }}</div>
              <div class="alert-details" v-if="alert.details">
                <div v-for="(value, key) in alert.details" :key="key" class="detail-item">
                  <span class="detail-key">{{ key }}:</span>
                  <span class="detail-value">{{ value }}</span>
                </div>
              </div>
            </div>
            
            <div class="alert-footer">
              <div class="alert-source">来源: {{ alert.source }}</div>
              <div class="alert-trend" :class="alert.trend">
                <i :class="getTrendIcon(alert.trend)"></i>
                <span>{{ alert.trendText }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 自定义面板模式 -->
      <div v-else-if="currentViewMode === 'custom-panel'" class="custom-panel-layout">
        <div class="panel-toolbar">
          <div class="panel-tools">
            <button class="add-widget-btn" @click="showWidgetLibrary = true">
              <i class="fas fa-plus"></i>
              <span>添加组件</span>
            </button>
            <button class="edit-layout-btn" @click="toggleEditMode">
              <i class="fas fa-edit"></i>
              <span>编辑布局</span>
            </button>
            <button class="save-layout-btn" @click="saveCurrentLayout">
              <i class="fas fa-save"></i>
              <span>保存布局</span>
            </button>
          </div>
          
          <div class="layout-presets">
            <button 
              v-for="preset in layoutPresets" 
              :key="preset.id"
              class="preset-btn"
              @click="applyLayoutPreset(preset)"
            >
              {{ preset.name }}
            </button>
          </div>
        </div>
        
        <div class="custom-panel-grid" ref="customPanelGrid">
          <div 
            v-for="widget in customWidgets" 
            :key="widget.id"
            class="custom-widget"
            :class="{ 'edit-mode': isEditMode }"
            :style="widget.style"
            @mousedown="startWidgetDrag(widget, $event)"
          >
            <div class="widget-header" v-if="isEditMode">
              <div class="widget-title">{{ widget.title }}</div>
              <div class="widget-controls">
                <button class="widget-config-btn" @click="configureWidget(widget)">
                  <i class="fas fa-cog"></i>
                </button>
                <button class="widget-remove-btn" @click="removeWidget(widget.id)">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
            
            <div class="widget-content">
              <component 
                :is="widget.component" 
                :config="widget.config"
                :realtime-data="widget.realtimeData"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 3D监控模式 -->
      <div v-else-if="currentViewMode === '3d-monitor'" class="three-d-monitor-layout">
        <div class="three-d-scene" ref="threeDScene">
          <div class="three-d-controls">
            <button class="rotate-btn" @click="toggleRotation">
              <i :class="isRotating ? 'fas fa-pause' : 'fas fa-play'"></i>
              <span>旋转</span>
            </button>
            <button class="zoom-in-btn" @click="zoomIn">
              <i class="fas fa-search-plus"></i>
            </button>
            <button class="zoom-out-btn" @click="zoomOut">
              <i class="fas fa-search-minus"></i>
            </button>
            <button class="reset-view-btn" @click="reset3DView">
              <i class="fas fa-undo"></i>
              <span>重置</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部状态栏 -->
    <div class="bottom-status-bar">
      <div class="left-status">
        <div class="system-health">
          <span class="health-label">系统健康度:</span>
          <div class="health-bar">
            <div class="health-fill" :style="{ width: systemHealth + '%' }"></div>
          </div>
          <span class="health-value">{{ systemHealth }}%</span>
        </div>
        
        <div class="data-quality">
          <span class="quality-label">数据质量:</span>
          <span class="quality-value" :class="dataQuality.level">{{ dataQuality.text }}</span>
        </div>
      </div>
      
      <div class="center-status">
        <div class="real-time-stats">
          <div class="stat-item">
            <span class="stat-label">数据流:</span>
            <span class="stat-value">{{ dataFlowRate }}/s</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">处理延迟:</span>
            <span class="stat-value">{{ processingLatency }}ms</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">活跃连接:</span>
            <span class="stat-value">{{ activeConnections }}</span>
          </div>
        </div>
      </div>
      
      <div class="right-status">
        <div class="time-display">
          <span class="current-time">{{ currentTime }}</span>
          <span class="timezone">{{ timezone }}</span>
        </div>
      </div>
    </div>

    <!-- 组件库弹窗 -->
    <div v-if="showWidgetLibrary" class="widget-library-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>添加监控组件</h3>
          <button class="close-btn" @click="showWidgetLibrary = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="widget-categories">
          <div 
            v-for="category in widgetCategories" 
            :key="category.id"
            class="category-section"
          >
            <h4>{{ category.name }}</h4>
            <div class="widget-grid">
              <div 
                v-for="widget in category.widgets" 
                :key="widget.id"
                class="widget-item"
                @click="addWidgetToPanel(widget)"
              >
                <div class="widget-preview">
                  <i :class="widget.icon"></i>
                </div>
                <div class="widget-info">
                  <div class="widget-name">{{ widget.name }}</div>
                  <div class="widget-description">{{ widget.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 预警设置弹窗 -->
    <div v-if="showAlertSettings" class="alert-settings-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>预警设置</h3>
          <button class="close-btn" @click="showAlertSettings = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="settings-content">
          <div class="setting-group">
            <label>预警声音</label>
            <div class="toggle-group">
              <label class="toggle-switch">
                <input type="checkbox" v-model="alertSettings.sound">
                <span class="toggle-slider"></span>
              </label>
              <span>启用声音预警</span>
            </div>
          </div>
          
          <div class="setting-group">
            <label>预警级别阈值</label>
            <div class="threshold-settings">
              <div v-for="level in alertLevels" :key="level.value" class="threshold-item">
                <span :class="['level-indicator', level.value]"></span>
                <span>{{ level.label }}:</span>
                <input 
                  type="number" 
                  v-model="alertSettings.thresholds[level.value]"
                  min="0"
                  max="100"
                >
                <span>%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 布局选择器 -->
    <div v-if="showLayoutSelector" class="layout-selector">
      <div class="layout-options">
        <div 
          v-for="layout in layoutOptions" 
          :key="layout.id"
          class="layout-option"
          :class="{ active: currentLayout === layout.id }"
          @click="applyLayout(layout)"
        >
          <div class="layout-preview">
            <div v-for="zone in layout.zones" :key="zone.id" class="layout-zone" :style="zone.style"></div>
          </div>
          <div class="layout-name">{{ layout.name }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore, useDataStore } from '@/stores'
import { formatTime } from '@/utils/format'

// 路由和状态管理
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const dataStore = useDataStore()

// 当前功能信息
const currentFunction = computed(() => {
  const functionId = route.params.functionId as string
  return appStore.getFunctionById(functionId)
})

// 视图模式
const viewModes = [
  { id: 'multi-screen', name: '多屏对比', icon: 'fas fa-th' },
  { id: 'alert-wall', name: '预警墙', icon: 'fas fa-exclamation-triangle' },
  { id: 'custom-panel', name: '自定义面板', icon: 'fas fa-palette' },
  { id: '3d-monitor', name: '3D监控', icon: 'fas fa-cube' }
]

const currentViewMode = ref('multi-screen')

// 系统状态
const systemStatus = ref('online')
const systemStatusText = computed(() => {
  const statusMap = {
    online: '系统正常',
    warning: '系统警告',
    error: '系统错误',
    offline: '系统离线'
  }
  return statusMap[systemStatus.value] || '未知状态'
})

// 监控屏幕配置
const monitorScreens = ref([
  {
    id: 'screen-1',
    title: '实时数据流',
    icon: 'fas fa-stream',
    component: 'DataStreamMonitor',
    size: 'large',
    position: { left: '0%', top: '0%', width: '50%', height: '50%' },
    config: { refreshRate: 1000, showDetails: true },
    realtimeData: {},
    latency: 12,
    updateRate: 60,
    status: '正常'
  },
  {
    id: 'screen-2',
    title: '性能监控',
    icon: 'fas fa-tachometer-alt',
    component: 'PerformanceMonitor',
    size: 'medium',
    position: { left: '50%', top: '0%', width: '50%', height: '50%' },
    config: { metrics: ['cpu', 'memory', 'network'] },
    realtimeData: {},
    latency: 8,
    updateRate: 30,
    status: '正常'
  },
  {
    id: 'screen-3',
    title: '预警监控',
    icon: 'fas fa-bell',
    component: 'AlertMonitor',
    size: 'medium',
    position: { left: '0%', top: '50%', width: '50%', height: '50%' },
    config: { maxAlerts: 50, autoRefresh: true },
    realtimeData: {},
    latency: 15,
    updateRate: 10,
    status: '正常'
  },
  {
    id: 'screen-4',
    title: '系统日志',
    icon: 'fas fa-file-alt',
    component: 'LogMonitor',
    size: 'small',
    position: { left: '50%', top: '50%', width: '50%', height: '50%' },
    config: { logLevel: 'info', maxLines: 100 },
    realtimeData: {},
    latency: 5,
    updateRate: 20,
    status: '正常'
  }
])

// 预警相关
const showAlertFilter = ref(false)
const showAlertSettings = ref(false)
const activeAlerts = ref([])
const selectedAlertLevels = ref(['critical', 'warning', 'info'])
const selectedAlertTypes = ref(['system', 'performance', 'data'])

const alertLevels = [
  { value: 'critical', label: '严重' },
  { value: 'warning', label: '警告' },
  { value: 'info', label: '信息' }
]

const alertTypes = [
  { value: 'system', label: '系统' },
  { value: 'performance', label: '性能' },
  { value: 'data', label: '数据' },
  { value: 'security', label: '安全' }
]

const alertSettings = ref({
  sound: true,
  thresholds: {
    critical: 90,
    warning: 70,
    info: 50
  }
})

// 过滤后的预警
const filteredAlerts = computed(() => {
  return activeAlerts.value.filter(alert => 
    selectedAlertLevels.value.includes(alert.level) &&
    selectedAlertTypes.value.includes(alert.type)
  )
})

// 自定义面板相关
const showWidgetLibrary = ref(false)
const isEditMode = ref(false)
const customWidgets = ref([
  {
    id: 'widget-1',
    title: '系统健康度',
    component: 'SystemHealthWidget',
    style: { left: '0%', top: '0%', width: '300px', height: '200px' },
    config: { showDetails: true },
    realtimeData: {}
  },
  {
    id: 'widget-2',
    title: '实时数据流',
    component: 'DataStreamWidget',
    style: { left: '320px', top: '0%', width: '400px', height: '200px' },
    config: { maxItems: 10 },
    realtimeData: {}
  }
])

const widgetCategories = [
  {
    id: 'monitoring',
    name: '监控组件',
    widgets: [
      {
        id: 'system-health',
        name: '系统健康度',
        icon: 'fas fa-heartbeat',
        description: '显示系统整体健康状态',
        component: 'SystemHealthWidget'
      },
      {
        id: 'data-stream',
        name: '数据流监控',
        icon: 'fas fa-stream',
        description: '实时数据流可视化',
        component: 'DataStreamWidget'
      },
      {
        id: 'performance-chart',
        name: '性能图表',
        icon: 'fas fa-chart-line',
        description: '系统性能指标图表',
        component: 'PerformanceChartWidget'
      },
      {
        id: 'alert-panel',
        name: '预警面板',
        icon: 'fas fa-exclamation-triangle',
        description: '预警信息展示面板',
        component: 'AlertPanelWidget'
      }
    ]
  },
  {
    id: 'data',
    name: '数据组件',
    widgets: [
      {
        id: 'stock-ticker',
        name: '股票行情',
        icon: 'fas fa-chart-bar',
        description: '实时股票价格显示',
        component: 'StockTickerWidget'
      },
      {
        id: 'market-overview',
        name: '市场概览',
        icon: 'fas fa-globe',
        description: '整体市场状况概览',
        component: 'MarketOverviewWidget'
      }
    ]
  }
]

// 布局相关
const showLayoutSelector = ref(false)
const currentLayout = ref('default')
const layoutOptions = [
  {
    id: 'default',
    name: '默认布局',
    zones: [
      { id: 1, style: { left: '0%', top: '0%', width: '50%', height: '50%' } },
      { id: 2, style: { left: '50%', top: '0%', width: '50%', height: '50%' } },
      { id: 3, style: { left: '0%', top: '50%', width: '50%', height: '50%' } },
      { id: 4, style: { left: '50%', top: '50%', width: '50%', height: '50%' } }
    ]
  },
  {
    id: 'focus',
    name: '焦点布局',
    zones: [
      { id: 1, style: { left: '0%', top: '0%', width: '70%', height: '70%' } },
      { id: 2, style: { left: '70%', top: '0%', width: '30%', height: '70%' } },
      { id: 3, style: { left: '0%', top: '70%', width: '100%', height: '30%' } }
    ]
  }
]

const layoutPresets = [
  { id: 'trading', name: '交易布局' },
  { id: 'analysis', name: '分析布局' },
  { id: 'monitoring', name: '监控布局' }
]

// 3D监控相关
const isRotating = ref(false)

// 系统指标
const systemHealth = ref(95)
const dataQuality = ref({ level: 'good', text: '良好' })
const dataFlowRate = ref(1250)
const processingLatency = ref(8)
const activeConnections = ref(42)
const currentTime = ref(new Date().toLocaleTimeString())
const timezone = ref('UTC+8')

// 全屏状态
const isFullscreen = ref(false)

// 粒子系统引用
const particleSystem = ref<HTMLElement>()
const dataStreamOverlay = ref<HTMLElement>()
const customPanelGrid = ref<HTMLElement>()
const threeDScene = ref<HTMLElement>()

// 方法
const switchViewMode = (mode: string) => {
  currentViewMode.value = mode
  initializeViewMode(mode)
}

const initializeViewMode = (mode: string) => {
  nextTick(() => {
    switch (mode) {
      case 'multi-screen':
        initMultiScreenMode()
        break
      case 'alert-wall':
        initAlertWallMode()
        break
      case 'custom-panel':
        initCustomPanelMode()
        break
      case '3d-monitor':
        init3DMonitorMode()
        break
    }
  })
}

const initMultiScreenMode = () => {
  // 初始化多屏模式
  console.log('初始化多屏监控模式')
}

const initAlertWallMode = () => {
  // 初始化预警墙模式
  console.log('初始化预警墙模式')
}

const initCustomPanelMode = () => {
  // 初始化自定义面板模式
  console.log('初始化自定义面板模式')
}

const init3DMonitorMode = () => {
  // 初始化3D监控模式
  console.log('初始化3D监控模式')
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

const showScreenContextMenu = (event: MouseEvent, screen: any) => {
  // 显示屏幕右键菜单
  console.log('显示屏幕右键菜单', screen)
}

const minimizeScreen = (screenId: string) => {
  console.log('最小化屏幕', screenId)
}

const maximizeScreen = (screenId: string) => {
  console.log('最大化屏幕', screenId)
}

const closeScreen = (screenId: string) => {
  const index = monitorScreens.value.findIndex(screen => screen.id === screenId)
  if (index > -1) {
    monitorScreens.value.splice(index, 1)
  }
}

const updateScreenData = (screenId: string, data: any) => {
  const screen = monitorScreens.value.find(s => s.id === screenId)
  if (screen) {
    screen.realtimeData = data
  }
}

const getAlertIcon = (alert: any) => {
  const iconMap = {
    critical: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  }
  return iconMap[alert.level] || 'fas fa-bell'
}

const getTrendIcon = (trend: string) => {
  const iconMap = {
    up: 'fas fa-arrow-up',
    down: 'fas fa-arrow-down',
    stable: 'fas fa-minus'
  }
  return iconMap[trend] || 'fas fa-minus'
}

const showAlertDetails = (alert: any) => {
  console.log('显示预警详情', alert)
}

const acknowledgeAlert = (alertId: string) => {
  console.log('确认预警', alertId)
}

const dismissAlert = (alertId: string) => {
  const index = activeAlerts.value.findIndex(alert => alert.id === alertId)
  if (index > -1) {
    activeAlerts.value.splice(index, 1)
  }
}

const toggleEditMode = () => {
  isEditMode.value = !isEditMode.value
}

const addWidgetToPanel = (widget: any) => {
  const newWidget = {
    id: `widget-${Date.now()}`,
    title: widget.name,
    component: widget.component,
    style: { 
      left: Math.random() * 60 + '%', 
      top: Math.random() * 60 + '%', 
      width: '300px', 
      height: '200px' 
    },
    config: {},
    realtimeData: {}
  }
  customWidgets.value.push(newWidget)
  showWidgetLibrary.value = false
}

const configureWidget = (widget: any) => {
  console.log('配置组件', widget)
}

const removeWidget = (widgetId: string) => {
  const index = customWidgets.value.findIndex(widget => widget.id === widgetId)
  if (index > -1) {
    customWidgets.value.splice(index, 1)
  }
}

const saveCurrentLayout = () => {
  console.log('保存当前布局', customWidgets.value)
}

const applyLayoutPreset = (preset: any) => {
  console.log('应用布局预设', preset)
}

const applyLayout = (layout: any) => {
  currentLayout.value = layout.id
  showLayoutSelector.value = false
  // 应用布局逻辑
}

const startWidgetDrag = (widget: any, event: MouseEvent) => {
  if (!isEditMode.value) return
  
  const startX = event.clientX
  const startY = event.clientY
  const startLeft = parseInt(widget.style.left)
  const startTop = parseInt(widget.style.top)
  
  const handleMouseMove = (e: MouseEvent) => {
    const deltaX = e.clientX - startX
    const deltaY = e.clientY - startY
    widget.style.left = (startLeft + deltaX) + 'px'
    widget.style.top = (startTop + deltaY) + 'px'
  }
  
  const handleMouseUp = () => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const toggleRotation = () => {
  isRotating.value = !isRotating.value
}

const zoomIn = () => {
  console.log('放大3D视图')
}

const zoomOut = () => {
  console.log('缩小3D视图')
}

const reset3DView = () => {
  console.log('重置3D视图')
}

// 更新时间
const updateTime = () => {
  currentTime.value = new Date().toLocaleTimeString()
}

// 模拟实时数据更新
const simulateRealtimeData = () => {
  // 更新系统健康度
  systemHealth.value = Math.max(0, Math.min(100, systemHealth.value + (Math.random() - 0.5) * 5))
  
  // 更新数据流率
  dataFlowRate.value = Math.max(0, dataFlowRate.value + (Math.random() - 0.5) * 100)
  
  // 更新处理延迟
  processingLatency.value = Math.max(0, processingLatency.value + (Math.random() - 0.5) * 2)
  
  // 更新活跃连接数
  activeConnections.value = Math.max(0, activeConnections.value + Math.floor((Math.random() - 0.5) * 5))
}

// 生命周期
onMounted(() => {
  // 初始化视图模式
  initializeViewMode(currentViewMode.value)
  
  // 启动时间更新
  const timeInterval = setInterval(updateTime, 1000)
  
  // 启动实时数据模拟
  const dataInterval = setInterval(simulateRealtimeData, 2000)
  
  // 清理函数
  onUnmounted(() => {
    clearInterval(timeInterval)
    clearInterval(dataInterval)
  })
})
</script>

<style lang="scss" scoped>
.monitoring-layer {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family-primary);
}

// 沉浸式背景
.immersive-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  
  .particle-system {
    position: absolute;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at 20% 50%, rgba(37, 99, 235, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(124, 58, 237, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(16, 185, 129, 0.1) 0%, transparent 50%);
  }
  
  .data-stream-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, 
      transparent 30%, 
      rgba(0, 255, 136, 0.03) 50%, 
      transparent 70%);
    animation: dataFlow 8s linear infinite;
  }
  
  .grid-pattern {
    position: absolute;
    width: 100%;
    height: 100%;
    background-image: 
      linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
  }
}

// 顶部控制栏
.top-control-bar {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  .left-controls {
    .monitoring-title {
      display: flex;
      align-items: center;
      gap: 16px;
      
      h2 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }
      
      .status-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        
        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #10b981;
          animation: pulse 2s infinite;
        }
        
        &.warning .status-dot {
          background: #f59e0b;
        }
        
        &.error .status-dot {
          background: #ef4444;
        }
        
        &.offline .status-dot {
          background: #6b7280;
        }
      }
    }
  }
  
  .center-controls {
    .view-mode-selector {
      display: flex;
      gap: 8px;
      padding: 4px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      
      .view-mode-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: transparent;
        border: none;
        border-radius: 8px;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          color: var(--text-primary);
        }
        
        &.active {
          background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
          color: white;
        }
        
        i {
          font-size: 16px;
        }
        
        span {
          font-size: 14px;
          font-weight: 500;
        }
      }
    }
  }
  
  .right-controls {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .alert-controls {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .alert-filter-btn, .alert-settings-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: var(--text-primary);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
        
        .alert-count {
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 20px;
          height: 20px;
          padding: 0 6px;
          background: #ef4444;
          color: white;
          border-radius: 10px;
          font-size: 12px;
          font-weight: 600;
        }
      }
    }
    
    .layout-controls {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .layout-btn, .fullscreen-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: var(--text-primary);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
      }
    }
  }
}

// 主监控区域
.main-monitoring-area {
  position: relative;
  z-index: 5;
  height: calc(100vh - 120px);
  padding: 20px;
  
  // 多屏对比模式
  &.multi-screen {
    .multi-screen-layout {
      position: relative;
      width: 100%;
      height: 100%;
      
      .monitor-screen {
        position: absolute;
        background: rgba(26, 26, 46, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
        transition: all 0.3s ease;
        
        &:hover {
          border-color: rgba(255, 255, 255, 0.2);
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .screen-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 16px;
          background: rgba(0, 0, 0, 0.3);
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          
          .screen-title {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-primary);
            font-weight: 500;
            
            i {
              color: var(--primary);
            }
          }
          
          .screen-controls {
            display: flex;
            gap: 4px;
            
            button {
              width: 24px;
              height: 24px;
              background: transparent;
              border: none;
              border-radius: 4px;
              color: var(--text-secondary);
              cursor: pointer;
              transition: all 0.2s ease;
              
              &:hover {
                background: rgba(255, 255, 255, 0.1);
                color: var(--text-primary);
              }
            }
          }
        }
        
        .screen-content {
          height: calc(100% - 80px);
          padding: 16px;
        }
        
        .screen-footer {
          padding: 8px 16px;
          background: rgba(0, 0, 0, 0.3);
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          
          .performance-metrics {
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: var(--text-secondary);
            
            .metric {
              display: flex;
              align-items: center;
              gap: 4px;
            }
          }
        }
      }
    }
  }
  
  // 预警墙模式
  &.alert-wall {
    .alert-wall-layout {
      display: flex;
      height: 100%;
      gap: 20px;
      
      .alert-filters {
        width: 280px;
        padding: 20px;
        background: rgba(26, 26, 46, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        
        .filter-group {
          margin-bottom: 24px;
          
          label {
            display: block;
            margin-bottom: 12px;
            color: var(--text-primary);
            font-weight: 500;
          }
          
          .checkbox-group {
            .checkbox-label {
              display: flex;
              align-items: center;
              gap: 8px;
              margin-bottom: 8px;
              cursor: pointer;
              
              .level-indicator {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                
                &.critical {
                  background: #ef4444;
                }
                
                &.warning {
                  background: #f59e0b;
                }
                
                &.info {
                  background: #3b82f6;
                }
              }
            }
          }
        }
      }
      
      .alert-wall {
        flex: 1;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 16px;
        padding: 20px;
        overflow-y: auto;
        
        .alert-card {
          padding: 16px;
          background: rgba(26, 26, 46, 0.6);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
          }
          
          &.critical {
            border-left: 4px solid #ef4444;
          }
          
          &.warning {
            border-left: 4px solid #f59e0b;
          }
          
          &.info {
            border-left: 4px solid #3b82f6;
          }
          
          .alert-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
            
            .alert-icon {
              width: 32px;
              height: 32px;
              display: flex;
              align-items: center;
              justify-content: center;
              background: rgba(255, 255, 255, 0.1);
              border-radius: 50%;
              
              i {
                font-size: 16px;
              }
            }
            
            .alert-info {
              flex: 1;
              margin-left: 12px;
              
              .alert-title {
                color: var(--text-primary);
                font-weight: 500;
                margin-bottom: 4px;
              }
              
              .alert-time {
                color: var(--text-secondary);
                font-size: 12px;
              }
            }
            
            .alert-actions {
              display: flex;
              gap: 8px;
              
              button {
                width: 28px;
                height: 28px;
                background: transparent;
                border: none;
                border-radius: 50%;
                color: var(--text-secondary);
                cursor: pointer;
                transition: all 0.2s ease;
                
                &:hover {
                  background: rgba(255, 255, 255, 0.1);
                  color: var(--text-primary);
                }
              }
            }
          }
          
          .alert-content {
            margin-bottom: 12px;
            
            .alert-message {
              color: var(--text-primary);
              margin-bottom: 8px;
            }
            
            .alert-details {
              .detail-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
                font-size: 12px;
                
                .detail-key {
                  color: var(--text-secondary);
                }
                
                .detail-value {
                  color: var(--text-primary);
                  font-weight: 500;
                }
              }
            }
          }
          
          .alert-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            
            .alert-source {
              color: var(--text-secondary);
            }
            
            .alert-trend {
              display: flex;
              align-items: center;
              gap: 4px;
              
              &.up {
                color: #10b981;
              }
              
              &.down {
                color: #ef4444;
              }
              
              &.stable {
                color: var(--text-secondary);
              }
            }
          }
        }
      }
    }
  }
  
  // 自定义面板模式
  &.custom-panel {
    .custom-panel-layout {
      height: 100%;
      display: flex;
      flex-direction: column;
      
      .panel-toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px;
        background: rgba(26, 26, 46, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        margin-bottom: 16px;
        
        .panel-tools {
          display: flex;
          gap: 8px;
          
          button {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: var(--text-primary);
            cursor: pointer;
            transition: all 0.3s ease;
            
            &:hover {
              background: rgba(255, 255, 255, 0.1);
              border-color: rgba(255, 255, 255, 0.2);
            }
          }
        }
        
        .layout-presets {
          display: flex;
          gap: 8px;
          
          .preset-btn {
            padding: 8px 16px;
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
            
            &:hover {
              background: rgba(255, 255, 255, 0.05);
              color: var(--text-primary);
            }
          }
        }
      }
      
      .custom-panel-grid {
        flex: 1;
        position: relative;
        background: rgba(26, 26, 46, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
        
        .custom-widget {
          position: absolute;
          background: rgba(26, 26, 46, 0.6);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          overflow: hidden;
          
          &.edit-mode {
            border-color: var(--primary);
            cursor: move;
            
            &:hover {
              box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.3);
            }
          }
          
          .widget-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            background: rgba(0, 0, 0, 0.3);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            
            .widget-title {
              color: var(--text-primary);
              font-size: 14px;
              font-weight: 500;
            }
            
            .widget-controls {
              display: flex;
              gap: 4px;
              
              button {
                width: 20px;
                height: 20px;
                background: transparent;
                border: none;
                border-radius: 4px;
                color: var(--text-secondary);
                cursor: pointer;
                transition: all 0.2s ease;
                
                &:hover {
                  background: rgba(255, 255, 255, 0.1);
                  color: var(--text-primary);
                }
              }
            }
          }
          
          .widget-content {
            height: calc(100% - 40px);
            padding: 12px;
          }
        }
      }
    }
  }
  
  // 3D监控模式
  &.three-d-monitor {
    .three-d-monitor-layout {
      position: relative;
      width: 100%;
      height: 100%;
      
      .three-d-scene {
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at center, rgba(37, 99, 235, 0.1) 0%, transparent 70%);
        border-radius: 12px;
        position: relative;
        
        .three-d-controls {
          position: absolute;
          top: 20px;
          right: 20px;
          display: flex;
          flex-direction: column;
          gap: 8px;
          
          button {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 16px;
            background: rgba(26, 26, 46, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: var(--text-primary);
            cursor: pointer;
            transition: all 0.3s ease;
            
            &:hover {
              background: rgba(255, 255, 255, 0.1);
              border-color: rgba(255, 255, 255, 0.2);
            }
          }
        }
      }
    }
  }
}

// 底部状态栏
.bottom-status-bar {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  
  .left-status {
    display: flex;
    align-items: center;
    gap: 24px;
    
    .system-health {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .health-label {
        color: var(--text-secondary);
        font-size: 14px;
      }
      
      .health-bar {
        width: 120px;
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        overflow: hidden;
        
        .health-fill {
          height: 100%;
          background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%);
          transition: width 0.3s ease;
        }
      }
      
      .health-value {
        color: var(--text-primary);
        font-weight: 500;
        font-size: 14px;
      }
    }
    
    .data-quality {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .quality-label {
        color: var(--text-secondary);
        font-size: 14px;
      }
      
      .quality-value {
        font-weight: 500;
        font-size: 14px;
        
        &.good {
          color: #10b981;
        }
        
        &.warning {
          color: #f59e0b;
        }
        
        &.error {
          color: #ef4444;
        }
      }
    }
  }
  
  .center-status {
    .real-time-stats {
      display: flex;
      gap: 24px;
      
      .stat-item {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .stat-label {
          color: var(--text-secondary);
          font-size: 14px;
        }
        
        .stat-value {
          color: var(--text-primary);
          font-weight: 500;
          font-size: 14px;
        }
      }
    }
  }
  
  .right-status {
    .time-display {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      
      .current-time {
        color: var(--text-primary);
        font-weight: 500;
        font-size: 16px;
      }
      
      .timezone {
        color: var(--text-secondary);
        font-size: 12px;
      }
    }
  }
}

// 弹窗样式
.widget-library-modal, .alert-settings-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .modal-content {
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
    background: rgba(26, 26, 46, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    overflow: hidden;
    
    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px 24px;
      background: rgba(0, 0, 0, 0.3);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      
      h3 {
        margin: 0;
        color: var(--text-primary);
        font-size: 20px;
        font-weight: 600;
      }
      
      .close-btn {
        width: 32px;
        height: 32px;
        background: transparent;
        border: none;
        border-radius: 50%;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          color: var(--text-primary);
        }
      }
    }
  }
}

.widget-library-modal {
  .modal-content {
    .widget-categories {
      padding: 24px;
      overflow-y: auto;
      max-height: calc(80vh - 80px);
      
      .category-section {
        margin-bottom: 32px;
        
        h4 {
          margin: 0 0 16px 0;
          color: var(--text-primary);
          font-size: 16px;
          font-weight: 600;
        }
        
        .widget-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 16px;
          
          .widget-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            
            &:hover {
              background: rgba(255, 255, 255, 0.1);
              border-color: var(--primary);
              transform: translateY(-2px);
            }
            
            .widget-preview {
              width: 48px;
              height: 48px;
              display: flex;
              align-items: center;
              justify-content: center;
              background: rgba(255, 255, 255, 0.1);
              border-radius: 8px;
              
              i {
                font-size: 24px;
                color: var(--primary);
              }
            }
            
            .widget-info {
              flex: 1;
              
              .widget-name {
                color: var(--text-primary);
                font-weight: 500;
                margin-bottom: 4px;
              }
              
              .widget-description {
                color: var(--text-secondary);
                font-size: 12px;
                line-height: 1.4;
              }
            }
          }
        }
      }
    }
  }
}

.alert-settings-modal {
  .modal-content {
    .settings-content {
      padding: 24px;
      
      .setting-group {
        margin-bottom: 24px;
        
        label {
          display: block;
          margin-bottom: 12px;
          color: var(--text-primary);
          font-weight: 500;
        }
        
        .toggle-group {
          display: flex;
          align-items: center;
          gap: 12px;
          
          .toggle-switch {
            position: relative;
            width: 48px;
            height: 24px;
            
            input {
              opacity: 0;
              width: 0;
              height: 0;
            }
            
            .toggle-slider {
              position: absolute;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              background: rgba(255, 255, 255, 0.1);
              border-radius: 12px;
              cursor: pointer;
              transition: all 0.3s ease;
              
              &:before {
                position: absolute;
                top: 2px;
                left: 2px;
                width: 20px;
                height: 20px;
                background: white;
                border-radius: 50%;
                transition: all 0.3s ease;
                content: '';
              }
            }
            
            input:checked + .toggle-slider {
              background: var(--primary);
              
              &:before {
                transform: translateX(24px);
              }
            }
          }
        }
        
        .threshold-settings {
          .threshold-item {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            
            .level-indicator {
              width: 12px;
              height: 12px;
              border-radius: 50%;
              
              &.critical {
                background: #ef4444;
              }
              
              &.warning {
                background: #f59e0b;
              }
              
              &.info {
                background: #3b82f6;
              }
            }
            
            input {
              width: 80px;
              padding: 6px 8px;
              background: rgba(255, 255, 255, 0.05);
              border: 1px solid rgba(255, 255, 255, 0.1);
              border-radius: 4px;
              color: var(--text-primary);
              font-size: 14px;
            }
          }
        }
      }
    }
  }
}

// 布局选择器
.layout-selector {
  position: fixed;
  top: 80px;
  right: 24px;
  z-index: 100;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  
  .layout-options {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    
    .layout-option {
      padding: 12px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: var(--primary);
      }
      
      &.active {
        background: rgba(37, 99, 235, 0.2);
        border-color: var(--primary);
      }
      
      .layout-preview {
        width: 80px;
        height: 60px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 4px;
        margin: 0 auto 8px;
        position: relative;
        
        .layout-zone {
          position: absolute;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 2px;
        }
      }
      
      .layout-name {
        text-align: center;
        color: var(--text-primary);
        font-size: 12px;
        font-weight: 500;
      }
    }
  }
}

// 动画
@keyframes dataFlow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
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