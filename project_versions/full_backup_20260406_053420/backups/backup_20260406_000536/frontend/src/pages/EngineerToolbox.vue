<template>
  <div class="engineer-toolbox">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-field" ref="particleField"></div>
      <div class="data-streams" ref="dataStreams"></div>
    </div>

    <!-- 全屏主界面 -->
    <div class="main-interface">
      <!-- 顶部控制栏 -->
      <div class="top-control-bar">
        <div class="brand-section">
          <div class="brand-logo">
            <n-icon size="28" :component="ToolsIcon" color="#8b5cf6" />
            <span class="brand-text">工程师工具箱</span>
          </div>
          <div class="brand-subtitle">深度调试 · 性能分析 · 代码级调试</div>
        </div>
        
        <div class="control-section">
          <!-- 智能搜索 -->
          <div class="smart-search">
            <n-input
              v-model:value="searchText"
              placeholder="智能搜索调试工具..."
              size="large"
              clearable
              class="search-input"
              @focus="handleSearchFocus"
              @blur="handleSearchBlur"
            >
              <template #prefix>
                <n-icon :component="SearchIcon" />
              </template>
            </n-input>
            
            <!-- 搜索建议下拉 -->
            <div v-if="showSearchSuggestions" class="search-suggestions">
              <div
                v-for="suggestion in searchSuggestions"
                :key="suggestion.id"
                class="suggestion-item"
                @click="selectSuggestion(suggestion)"
              >
                <n-icon :component="getToolIcon(suggestion.icon)" />
                <div class="suggestion-content">
                  <div class="suggestion-title">{{ suggestion.name }}</div>
                  <div class="suggestion-desc">{{ suggestion.description }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 快捷操作 -->
          <div class="quick-actions">
            <n-button
              v-for="action in quickActions"
              :key="action.id"
              :type="action.type"
              size="large"
              circle
              @click="action.handler"
              class="action-btn"
            >
              <n-icon size="20" :component="action.icon" />
            </n-button>
          </div>
        </div>
      </div>

      <!-- 工具选择区域 -->
      <div class="tool-selection-area">
        <!-- 分类导航 -->
        <div class="category-navigation">
          <div
            v-for="category in toolCategories"
            :key="category.id"
            :class="['category-item', { active: activeCategory === category.id }]"
            @click="switchCategory(category.id)"
          >
            <n-icon size="24" :component="category.icon" />
            <span>{{ category.name }}</span>
            <div class="category-indicator"></div>
          </div>
        </div>

        <!-- 工具展示区 -->
        <div class="tools-showcase">
          <div class="tools-container">
            <div
              v-for="tool in filteredTools"
              :key="tool.id"
              :class="['tool-item', { featured: isFeaturedTool(tool) }]"
              @click="enterTool(tool)"
              @mouseenter="highlightTool(tool)"
              @mouseleave="unhighlightTool(tool)"
            >
              <!-- 工具光环效果 -->
              <div class="tool-aura" ref="toolAura"></div>
              
              <!-- 工具核心内容 -->
              <div class="tool-core">
                <div class="tool-icon-wrapper">
                  <n-icon size="40" :component="getToolIcon(tool.icon)" />
                  <div class="tool-status" :class="tool.status"></div>
                </div>
                
                <div class="tool-info">
                  <h3 class="tool-name">{{ tool.name }}</h3>
                  <p class="tool-description">{{ tool.description }}</p>
                  
                  <div class="tool-features">
                    <div
                      v-for="feature in tool.features.slice(0, 2)"
                      :key="feature"
                      class="feature-chip"
                    >
                      {{ feature }}
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 工具交互层 -->
              <div class="tool-interaction">
                <div class="tool-metrics">
                  <div class="metric-item">
                    <span class="metric-label">使用次数</span>
                    <span class="metric-value">{{ tool.usage || 0 }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">权限</span>
                    <span class="metric-value">{{ getAccessLevelText(tool.permissions) }}</span>
                  </div>
                </div>
                
                <div class="tool-action">
                  <n-button type="primary" size="large" ghost>
                    进入工具
                  </n-button>
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
            <span>{{ filteredTools.length }} 个工具可用</span>
          </div>
        </div>
        
        <div class="status-right">
          <div class="keyboard-hint">
            <n-button text size="small">
              <n-icon :component="HelpIcon" />
              快捷键
            </n-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 工具详情全屏模态 -->
    <div v-if="showToolDetail" class="tool-detail-modal" @click="closeToolDetail">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <div class="tool-detail-header">
            <n-icon size="64" :component="getToolIcon(selectedTool?.icon)" />
            <div class="tool-detail-info">
              <h2>{{ selectedTool?.name }}</h2>
              <p>{{ selectedTool?.description }}</p>
            </div>
          </div>
          
          <n-button circle size="large" text @click="closeToolDetail">
            <n-icon size="24" :component="CloseIcon" />
          </n-button>
        </div>
        
        <div class="modal-body">
          <div class="detail-section">
            <h3>核心功能</h3>
            <div class="features-grid">
              <div
                v-for="feature in selectedTool?.features"
                :key="feature"
                class="feature-card"
              >
                <n-icon :component="CheckIcon" />
                <span>{{ feature }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section">
            <h3>权限要求</h3>
            <div class="permissions-badges">
              <n-badge
                v-for="permission in selectedTool?.permissions"
                :key="permission"
                :value="getPermissionText(permission)"
                type="warning"
              />
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <n-space size="large">
            <n-button type="primary" size="large" @click="launchTool(selectedTool)">
              启动工具
            </n-button>
            <n-button size="large" @click="closeToolDetail">
              返回
            </n-button>
          </n-space>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { engineerToolbox, getAccessibleTools } from '@/configs/functionConfig'
import {
  BuildOutline as ToolsIcon,
  FunnelOutline as FilterIcon,
  SearchOutline as SearchIcon,
  ShieldOutline as ShieldIcon,
  BugOutline as BugIcon,
  ConstructOutline as ConstructIcon,
  CodeSlashOutline as CodeSlashIcon,
  BarChartOutline as AnalyticsIcon,
  ServerOutline as ServerIcon,
  SettingsOutline as CogIcon,
  CloseOutline as CloseIcon,
  CheckmarkOutline as CheckIcon,
  HelpCircleOutline as HelpIcon,
  StarOutline as StarIcon,
  TimeOutline as TimeIcon
} from '@vicons/ionicons5'

// 状态管理
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const searchText = ref('')
const activeCategory = ref('all')
const showToolDetail = ref(false)
const selectedTool = ref<any>(null)
const showSearchSuggestions = ref(false)
const searchSuggestions = ref<any[]>([])
const highlightedTool = ref<string | null>(null)

// DOM引用
const particleField = ref<HTMLElement>()
const dataStreams = ref<HTMLElement>()
const toolAura = ref<HTMLElement[]>([])

// 工具分类
const toolCategories = [
  { id: 'all', name: '全部工具', icon: ToolsIcon },
  { id: 'data', name: '数据调试', icon: AnalyticsIcon },
  { id: 'system', name: '系统调试', icon: ServerIcon },
  { id: 'code', name: '代码调试', icon: CodeSlashIcon },
  { id: 'performance', name: '性能分析', icon: ConstructIcon },
  { id: 'troubleshoot', name: '问题诊断', icon: BugIcon }
]

// 快捷操作
const quickActions = [
  {
    id: 'recent',
    icon: TimeIcon,
    type: 'tertiary',
    handler: () => console.log('Recent tools')
  },
  {
    id: 'favorites',
    icon: StarIcon,
    type: 'tertiary',
    handler: () => console.log('Favorite tools')
  },
  {
    id: 'filter',
    icon: FilterIcon,
    type: 'tertiary',
    handler: () => console.log('Filter tools')
  }
]

// 获取用户可访问的工具
const accessibleTools = computed(() => {
  const userPermissions = userStore.permissions || []
  return getAccessibleTools(userPermissions)
})

// 扩展工具信息（添加分类和状态）
const extendedTools = computed(() => {
  return accessibleTools.value.map(tool => ({
    ...tool,
    category: getToolCategory(tool.id),
    status: getToolStatus(tool.id),
    usage: getToolUsage(tool.id)
  }))
})

// 筛选后的工具
const filteredTools = computed(() => {
  let tools = extendedTools.value

  // 分类筛选
  if (activeCategory.value !== 'all') {
    tools = tools.filter(tool => tool.category === activeCategory.value)
  }

  // 搜索筛选
  if (searchText.value) {
    const searchLower = searchText.value.toLowerCase()
    tools = tools.filter(tool =>
      tool.name.toLowerCase().includes(searchLower) ||
      tool.description.toLowerCase().includes(searchLower) ||
      tool.features.some(feature => feature.toLowerCase().includes(searchLower))
    )
  }

  return tools
})

// 方法
const getToolCategory = (toolId: string): string => {
  const categoryMap: Record<string, string> = {
    'data-debug': 'data',
    'system-debug': 'system',
    'model-debug': 'code',
    'backtest-debug': 'performance',
    'strategy-debug': 'code',
    'trading-debug': 'troubleshoot'
  }
  return categoryMap[toolId] || 'all'
}

const getToolStatus = (toolId: string): string => {
  const statusMap: Record<string, string> = {
    'data-debug': 'online',
    'system-debug': 'online',
    'model-debug': 'idle',
    'backtest-debug': 'maintenance',
    'strategy-debug': 'online',
    'trading-debug': 'online'
  }
  return statusMap[toolId] || 'online'
}

const getToolUsage = (toolId: string): number => {
  const usageMap: Record<string, number> = {
    'data-debug': 45,
    'system-debug': 32,
    'model-debug': 28,
    'backtest-debug': 15,
    'strategy-debug': 38,
    'trading-debug': 22
  }
  return usageMap[toolId] || 0
}

const getToolIcon = (iconName: string) => {
  const iconMap: Record<string, any> = {
    'database-debug': AnalyticsIcon,
    'experiment-debug': ConstructIcon,
    'robot-debug': CodeSlashIcon,
    'trading-debug': BugIcon,
    'monitor-debug': ServerIcon,
    'chart-debug': CogIcon
  }
  return iconMap[iconName] || ToolsIcon
}

const getAccessLevelText = (permissions?: string[]) => {
  if (!permissions || permissions.length === 0) return '所有用户'
  
  const levelMap: Record<string, string> = {
    'admin': '管理员',
    'developer': '开发者',
    'ml-engineer': 'ML工程师',
    'trader': '交易员'
  }
  
  return permissions.map(perm => levelMap[perm] || perm).join(', ')
}

const getPermissionText = (permission: string) => {
  const textMap: Record<string, string> = {
    'admin': '管理员',
    'developer': '开发者',
    'ml-engineer': 'ML工程师',
    'trader': '交易员'
  }
  return textMap[permission] || permission
}

const isFeaturedTool = (tool: any): boolean => {
  return tool.usage > 30
}

const switchCategory = (categoryId: string) => {
  activeCategory.value = categoryId
}

const enterTool = (tool: any) => {
  selectedTool.value = tool
  showToolDetail.value = true
}

const closeToolDetail = () => {
  showToolDetail.value = false
  selectedTool.value = null
}

const launchTool = (tool: any) => {
  router.push(`/engineer-toolbox/${tool.id}`)
  closeToolDetail()
}

const highlightTool = (tool: any) => {
  highlightedTool.value = tool.id
}

const unhighlightTool = (tool: any) => {
  if (highlightedTool.value === tool.id) {
    highlightedTool.value = null
  }
}

const handleSearchFocus = () => {
  if (searchText.value) {
    updateSearchSuggestions()
  }
  showSearchSuggestions.value = true
}

const handleSearchBlur = () => {
  setTimeout(() => {
    showSearchSuggestions.value = false
  }, 200)
}

const updateSearchSuggestions = () => {
  if (!searchText.value) {
    searchSuggestions.value = []
    return
  }
  
  const searchLower = searchText.value.toLowerCase()
  searchSuggestions.value = extendedTools.value
    .filter(tool =>
      tool.name.toLowerCase().includes(searchLower) ||
      tool.description.toLowerCase().includes(searchLower)
    )
    .slice(0, 5)
}

const selectSuggestion = (suggestion: any) => {
  searchText.value = suggestion.name
  showSearchSuggestions.value = false
  enterTool(suggestion)
}

// 粒子动画效果
const initParticleAnimation = () => {
  if (!particleField.value) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  particleField.value.appendChild(canvas)
  
  const particles: any[] = []
  const particleCount = 50
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.2
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
      ctx.fillStyle = `rgba(139, 92, 246, ${particle.opacity})`
      ctx.fill()
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 数据流动画效果
const initDataStreamAnimation = () => {
  if (!dataStreams.value) return
  
  const createDataStream = () => {
    const stream = document.createElement('div')
    stream.className = 'data-stream'
    stream.style.cssText = `
      position: absolute;
      width: 2px;
      height: 100px;
      background: linear-gradient(to bottom, transparent, #8b5cf6, transparent);
      left: ${Math.random() * 100}%;
      top: -100px;
      opacity: 0.6;
      animation: dataFlow 3s linear infinite;
    `
    
    dataStreams.value.appendChild(stream)
    
    setTimeout(() => {
      stream.remove()
    }, 3000)
  }
  
  setInterval(createDataStream, 500)
}

// 生命周期
onMounted(() => {
  nextTick(() => {
    initParticleAnimation()
    initDataStreamAnimation()
  })
  
  // 如果路由中有工具ID，自动打开对应工具
  const toolId = route.params.toolId as string
  if (toolId) {
    const tool = accessibleTools.value.find(t => t.id === toolId)
    if (tool) {
      enterTool(tool)
    }
  }
})

onUnmounted(() => {
  // 清理动画
  if (particleField.value) {
    particleField.value.innerHTML = ''
  }
  if (dataStreams.value) {
    dataStreams.value.innerHTML = ''
  }
})
</script>

<style lang="scss" scoped>
.engineer-toolbox {
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
    
    .particle-field {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    
    .data-streams {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
    }
  }
  
  .main-interface {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    height: 100vh;
    backdrop-filter: blur(2px);
  }
  
  .top-control-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-6) var(--spacing-8);
    background: rgba(var(--surface-color), 0.1);
    border-bottom: 1px solid rgba(var(--border-color), 0.1);
    
    .brand-section {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-1);
      
      .brand-logo {
        display: flex;
        align-items: center;
        gap: var(--spacing-2);
        
        .brand-text {
          font-size: var(--font-size-xl);
          font-weight: 600;
          color: var(--text-primary);
          letter-spacing: 1px;
        }
      }
      
      .brand-subtitle {
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
        margin-left: var(--spacing-8);
      }
    }
    
    .control-section {
      display: flex;
      align-items: center;
      gap: var(--spacing-6);
      
      .smart-search {
        position: relative;
        
        .search-input {
          width: 400px;
          background: rgba(var(--surface-color), 0.8);
          border: 1px solid rgba(var(--border-color), 0.3);
          border-radius: var(--border-radius-lg);
          
          &:focus-within {
            border-color: var(--primary-color);
            box-shadow: 0 0 20px rgba(var(--primary-color), 0.3);
          }
        }
        
        .search-suggestions {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: rgba(var(--surface-color), 0.95);
          border: 1px solid rgba(var(--border-color), 0.2);
          border-radius: var(--border-radius-lg);
          margin-top: var(--spacing-2);
          backdrop-filter: blur(10px);
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
          
          .suggestion-item {
            display: flex;
            align-items: center;
            gap: var(--spacing-3);
            padding: var(--spacing-3) var(--spacing-4);
            cursor: pointer;
            transition: background 0.2s ease;
             
            &:hover {
              background: rgba(var(--primary-color), 0.1);
            }
             
            .suggestion-content {
              .suggestion-title {
                font-size: var(--font-size-sm);
                  color: var(--text-primary);
                  font-weight: 500;
                }
                 
                .suggestion-desc {
                  font-size: var(--font-size-xs);
                  color: var(--text-secondary);
                  margin-top: var(--spacing-1);
                }
              }
            }
          }
      }
      
      .quick-actions {
        display: flex;
        gap: var(--spacing-3);
        
        .action-btn {
          background: rgba(var(--surface-color), 0.8);
          border: 1px solid rgba(var(--border-color), 0.3);
          
          &:hover {
            background: rgba(var(--primary-color), 0.2);
            border-color: var(--primary-color);
            transform: scale(1.1);
          }
        }
      }
    }
  }
  
  .tool-selection-area {
    flex: 1;
    display: flex;
    padding: var(--spacing-6);
    gap: var(--spacing-6);
    
    .category-navigation {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-2);
      width: 200px;
      
      .category-item {
        position: relative;
        display: flex;
        align-items: center;
        gap: var(--spacing-3);
        padding: var(--spacing-4);
        border-radius: var(--border-radius-lg);
        cursor: pointer;
        transition: all 0.3s ease;
        background: rgba(var(--surface-color), 0.1);
        border: 1px solid transparent;
        
        &:hover {
          background: rgba(var(--primary-color), 0.1);
          border-color: rgba(var(--primary-color), 0.3);
        }
        
        &.active {
          background: rgba(var(--primary-color), 0.2);
          border-color: var(--primary-color);
          
          .category-indicator {
            opacity: 1;
          }
        }
        
        .category-indicator {
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 3px;
          height: 60%;
          background: var(--primary-color);
          opacity: 0;
          transition: opacity 0.3s ease;
        }
      }
    }
    
    .tools-showcase {
      flex: 1;
      
      .tools-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: var(--spacing-6);
        
        .tool-item {
          position: relative;
          background: rgba(var(--surface-color), 0.1);
          border: 1px solid rgba(var(--border-color), 0.2);
          border-radius: var(--border-radius-xl);
          padding: var(--spacing-6);
          cursor: pointer;
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          overflow: hidden;
          
          &:hover {
            transform: translateY(-8px) scale(1.02);
            background: rgba(var(--surface-color), 0.2);
            border-color: rgba(var(--primary-color), 0.4);
            
            .tool-aura {
              opacity: 1;
            }
          }
          
          &.featured {
            border-color: var(--accent-color);
            background: rgba(var(--accent-color), 0.05);
          }
          
          .tool-aura {
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
          
          .tool-core {
            position: relative;
            z-index: 2;
            
            .tool-icon-wrapper {
              display: flex;
              justify-content: center;
              margin-bottom: var(--spacing-4);
              
              .tool-status {
                position: absolute;
                top: -5px;
                right: -5px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                
                &.online {
                  background: var(--success-color);
                  box-shadow: 0 0 8px rgba(var(--success-color), 0.6);
                }
                
                &.idle {
                  background: var(--warning-color);
                  box-shadow: 0 0 8px rgba(var(--warning-color), 0.6);
                }
                
                &.maintenance {
                  background: var(--error-color);
                  box-shadow: 0 0 8px rgba(var(--error-color), 0.6);
                }
              }
            }
            
            .tool-info {
              text-align: center;
              
              .tool-name {
                font-size: var(--font-size-lg);
                font-weight: 600;
                color: var(--text-primary);
                margin: 0 0 var(--spacing-2) 0;
              }
              
              .tool-description {
                color: var(--text-secondary);
                font-size: var(--font-size-sm);
                line-height: 1.5;
                margin: 0 0 var(--spacing-4) 0;
              }
              
              .tool-features {
                display: flex;
                flex-wrap: wrap;
                gap: var(--spacing-2);
                justify-content: center;
                
                .feature-chip {
                  background: rgba(var(--primary-color), 0.1);
                  color: var(--primary-color);
                  padding: var(--spacing-1) var(--spacing-2);
                  border-radius: var(--border-radius-full);
                  font-size: var(--font-size-xs);
                  font-weight: 500;
                }
              }
            }
          }
          
          .tool-interaction {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: var(--spacing-4);
            background: linear-gradient(to top, rgba(var(--bg-deep), 0.9), transparent);
            transform: translateY(100%);
            transition: transform 0.3s ease;
            
            .tool-metrics {
              display: flex;
              justify-content: space-between;
              margin-bottom: var(--spacing-3);
              
              .metric-item {
                text-align: center;
                
                .metric-label {
                  display: block;
                  font-size: var(--font-size-xs);
                  color: var(--text-tertiary);
                  margin-bottom: var(--spacing-1);
                }
                
                .metric-value {
                  font-size: var(--font-size-sm);
                  color: var(--text-primary);
                  font-weight: 600;
                }
              }
            }
          }
          
          &:hover .tool-interaction {
            transform: translateY(0);
          }
        }
      }
    }
  }
  
  .bottom-status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-4) var(--spacing-8);
    background: rgba(var(--surface-color), 0.1);
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
    
    .status-right {
      .keyboard-hint {
        color: var(--text-secondary);
      }
    }
  }
  
  .tool-detail-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(var(--bg-deep), 0.95);
    backdrop-filter: blur(20px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .modal-content {
      background: rgba(var(--surface-color), 0.9);
      border: 1px solid rgba(var(--border-color), 0.2);
      border-radius: var(--border-radius-xl);
      padding: var(--spacing-8);
      max-width: 800px;
      width: 90%;
      max-height: 80vh;
      overflow-y: auto;
      
      .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: var(--spacing-6);
        
        .tool-detail-header {
          display: flex;
          align-items: center;
          gap: var(--spacing-4);
          
          .tool-detail-info {
            h2 {
              font-size: var(--font-size-xl);
              color: var(--text-primary);
              margin: 0 0 var(--spacing-2) 0;
            }
           
            p {
              color: var(--text-secondary);
              margin: 0;
            }
          }
        }
      }
      
     .modal-body {
       .detail-section {
         margin-bottom: var(--spacing-6);
         
         h3 {
           font-size: var(--font-size-lg);
           color: var(--text-primary);
           margin: 0 0 var(--spacing-4) 0;
         }
         
         .features-grid {
           display: grid;
           grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
           gap: var(--spacing-3);
           
           .feature-card {
             display: flex;
             align-items: center;
             gap: var(--spacing-2);
             padding: var(--spacing-3);
             background: rgba(var(--primary-color), 0.05);
             border-radius: var(--border-radius-lg);
             
             span {
               color: var(--text-primary);
               font-size: var(--font-size-sm);
             }
           }
         }
         
         .permissions-badges {
           display: flex;
           gap: var(--spacing-2);
         }
       }
     }
      
      .modal-footer {
        margin-top: var(--spacing-8);
        text-align: center;
      }
    }
  }
}

// 动画定义
@keyframes dataFlow {
  0% {
    transform: translateY(-100px);
  }
  100% {
    transform: translateY(calc(100vh + 100px));
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .engineer-toolbox {
    .tool-selection-area {
      flex-direction: column;
      
      .category-navigation {
        width: 100%;
        flex-direction: row;
        overflow-x: auto;
      }
      
      .tools-showcase .tools-container {
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      }
    }
  }
}

@media (max-width: 768px) {
  .engineer-toolbox {
    .top-control-bar {
      flex-direction: column;
      gap: var(--spacing-4);
      padding: var(--spacing-4);
      
      .control-section {
        width: 100%;
        justify-content: space-between;
        
        .smart-search .search-input {
          width: 100%;
        }
      }
    }
    
    .tool-selection-area {
      padding: var(--spacing-4);
      
      .tools-showcase .tools-container {
        grid-template-columns: 1fr;
      }
    }
    
    .tool-detail-modal .modal-content {
      padding: var(--spacing-6);
    }
  }
}
</style>