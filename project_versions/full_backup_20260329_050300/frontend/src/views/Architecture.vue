<template>
  <div class="architecture-page">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-system" ref="particleSystem"></div>
      <div class="data-stream-overlay"></div>
      <div class="grid-pattern"></div>
    </div>

    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title"><i class="fas fa-sitemap"></i> 系统架构</h1>
          <p class="page-subtitle">可视化量化交易系统的技术架构</p>
        </div>
        <div class="header-right">
          <div class="view-controls">
            <button 
              v-for="mode in viewModes" 
              :key="mode.id"
              :class="['view-btn', { active: currentViewMode === mode.id }]"
              @click="switchViewMode(mode.id)"
            >
              <i :class="mode.icon"></i>
              <span>{{ mode.name }}</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 架构图展示 -->
      <section class="architecture-showcase">
        <div class="showcase-header">
          <h2><i class="fas fa-project-diagram"></i> 系统架构概览</h2>
          <p>点击下方功能模块进入详细架构图</p>
        </div>
        
        <div class="architecture-grid">
          <div 
            v-for="module in architectureModules" 
            :key="module.id"
            class="arch-module-card"
            @click="enterModule(module)"
          >
            <div class="module-visual">
              <div class="module-icon">
                <i :class="module.icon"></i>
              </div>
              <div class="module-status" :class="module.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ module.statusText }}</span>
              </div>
            </div>
            
            <div class="module-info">
              <h3>{{ module.name }}</h3>
              <p>{{ module.description }}</p>
              <div class="module-stats">
                <div class="stat-item">
                  <span class="stat-label">节点数:</span>
                  <span class="stat-value">{{ module.nodes }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">连接数:</span>
                  <span class="stat-value">{{ module.connections }}</span>
                </div>
              </div>
            </div>
            
            <div class="module-overlay">
              <div class="overlay-content">
                <i class="fas fa-arrow-right"></i>
                <span>查看架构</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 技术栈展示 -->
      <section class="tech-stack-section">
        <div class="section-header">
          <h2><i class="fas fa-layer-group"></i> 技术栈</h2>
          <p>系统使用的核心技术和框架</p>
        </div>
        
        <div class="tech-grid">
          <div 
            v-for="tech in techStack" 
            :key="tech.id"
            class="tech-card"
          >
            <div class="tech-icon">
              <i :class="tech.icon"></i>
            </div>
            <div class="tech-info">
              <h4>{{ tech.name }}</h4>
              <p>{{ tech.description }}</p>
              <div class="tech-tags">
                <span 
                  v-for="tag in tech.tags" 
                  :key="tag"
                  class="tech-tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 性能指标 -->
      <section class="performance-section">
        <div class="section-header">
          <h2>系统性能</h2>
          <p>实时系统性能监控指标</p>
        </div>
        
        <div class="performance-grid">
          <div 
            v-for="metric in performanceMetrics" 
            :key="metric.id"
            class="performance-card"
          >
            <div class="metric-header">
              <div class="metric-icon">
                <i :class="metric.icon"></i>
              </div>
              <div class="metric-title">{{ metric.title }}</div>
            </div>
            
            <div class="metric-value" :class="metric.status">
              {{ metric.value }}
              <span class="metric-unit">{{ metric.unit }}</span>
            </div>
            
            <div class="metric-chart">
              <div class="mini-chart" :id="`chart-${metric.id}`"></div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 视图模式
const viewModes = [
  { id: 'overview', name: '概览', icon: 'fas fa-th' },
  { id: 'detailed', name: '详细', icon: 'fas fa-sitemap' },
  { id: 'performance', name: '性能', icon: 'fas fa-tachometer-alt' }
]

const currentViewMode = ref('overview')

// 架构模块
const architectureModules = ref([
  {
    id: 'data-layer',
    name: '数据层',
    description: '数据获取、清洗、存储和管理',
    icon: 'fas fa-database',
    status: 'online',
    statusText: '运行正常',
    nodes: 12,
    connections: 24,
    route: '/function/data-overview/architecture'
  },
  {
    id: 'processing-layer',
    name: '处理层',
    description: '数据处理、特征工程和预处理',
    icon: 'fas fa-cogs',
    status: 'online',
    statusText: '运行正常',
    nodes: 18,
    connections: 36,
    route: '/function/processing-center/architecture'
  },
  {
    id: 'ai-layer',
    name: 'AI层',
    description: '机器学习模型和策略生成',
    icon: 'fas fa-brain',
    status: 'online',
    statusText: '运行正常',
    nodes: 15,
    connections: 30,
    route: '/function/ai-engine/architecture'
  },
  {
    id: 'strategy-layer',
    name: '策略层',
    description: '策略执行、风险控制和订单管理',
    icon: 'fas fa-chess',
    status: 'warning',
    statusText: '负载较高',
    nodes: 8,
    connections: 16,
    route: '/function/strategy-engine/architecture'
  },
  {
    id: 'monitoring-layer',
    name: '监控层',
    description: '系统监控、日志分析和预警',
    icon: 'fas fa-desktop',
    status: 'online',
    statusText: '运行正常',
    nodes: 10,
    connections: 20,
    route: '/function/monitoring-center/architecture'
  },
  {
    id: 'api-layer',
    name: 'API层',
    description: '接口服务、认证和权限管理',
    icon: 'fas fa-plug',
    status: 'online',
    statusText: '运行正常',
    nodes: 6,
    connections: 12,
    route: '/function/api-gateway/architecture'
  }
])

// 技术栈
const techStack = ref([
  {
    id: 1,
    name: 'Vue 3',
    description: '现代化的前端框架，提供响应式数据绑定和组件化开发',
    icon: 'fab fa-vuejs',
    tags: ['Frontend', 'Reactive', 'Component-based']
  },
  {
    id: 2,
    name: 'TypeScript',
    description: '类型安全的JavaScript超集，提供更好的开发体验',
    icon: 'fab fa-js',
    tags: ['Type-safe', 'Development', 'Tooling']
  },
  {
    id: 3,
    name: 'Pinia',
    description: 'Vue 3官方推荐的状态管理库',
    icon: 'fas fa-box',
    tags: ['State Management', 'Vue 3', 'Reactive']
  },
  {
    id: 4,
    name: 'ECharts',
    description: '强大的数据可视化图表库',
    icon: 'fas fa-chart-line',
    tags: ['Visualization', 'Charts', 'Interactive']
  },
  {
    id: 5,
    name: 'FastAPI',
    description: '现代化的Python Web框架，支持异步处理',
    icon: 'fab fa-python',
    tags: ['Backend', 'API', 'Async']
  },
  {
    id: 6,
    name: 'Redis',
    description: '高性能的内存数据库，用于缓存和会话管理',
    icon: 'fas fa-server',
    tags: ['Database', 'Cache', 'Performance']
  }
])

// 性能指标
const performanceMetrics = ref([
  {
    id: 'cpu',
    title: 'CPU使用率',
    value: 45.2,
    unit: '%',
    status: 'normal',
    icon: 'fas fa-microchip'
  },
  {
    id: 'memory',
    title: '内存使用率',
    value: 68.7,
    unit: '%',
    status: 'warning',
    icon: 'fas fa-memory'
  },
  {
    id: 'network',
    title: '网络延迟',
    value: 12.5,
    unit: 'ms',
    status: 'good',
    icon: 'fas fa-network-wired'
  },
  {
    id: 'throughput',
    title: '数据处理量',
    value: 1250,
    unit: 'ops/s',
    status: 'good',
    icon: 'fas fa-exchange-alt'
  }
])

// 切换视图模式
const switchViewMode = (mode: string) => {
  currentViewMode.value = mode
}

// 进入模块
const enterModule = (module: any) => {
  router.push(module.route)
}

// 初始化粒子系统
const initParticleSystem = () => {
  const particleSystem = document.querySelector('.particle-system')
  if (!particleSystem) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  canvas.style.position = 'absolute'
  canvas.style.top = '0'
  canvas.style.left = '0'
  canvas.style.pointerEvents = 'none'
  
  particleSystem.appendChild(canvas)
  
  // 简单的粒子动画
  const particles: any[] = []
  for (let i = 0; i < 30; i++) {
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
      
      if (particle.x < 0 || particle.x > canvas.width) particle.vx = -particle.vx
      if (particle.y < 0 || particle.y > canvas.height) particle.vy = -particle.vy
      
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(139, 92, 246, ${particle.opacity})`
      ctx.fill()
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 生命周期
onMounted(() => {
  nextTick(() => {
    initParticleSystem()
  })
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.architecture-page {
  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family-primary);
  overflow-x: hidden;
}

// 沉浸式背景
.immersive-background {
  position: fixed;
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

// 页面头部
.page-header {
  position: relative;
  z-index: 10;
  padding: 24px 40px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .header-left {
    .page-title {
      margin: 0 0 8px 0;
      font-size: 32px;
      font-weight: 700;
      background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .page-subtitle {
      margin: 0;
      color: var(--text-secondary);
      font-size: 16px;
    }
  }
  
  .header-right {
    .view-controls {
      display: flex;
      gap: 8px;
      
      .view-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 20px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          color: var(--text-primary);
        }
        
        &.active {
          background: rgba(37, 99, 235, 0.2);
          border-color: var(--primary);
          color: var(--primary);
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
}

// 主内容区域
.main-content {
  position: relative;
  z-index: 5;
  padding: 40px;
}

// 架构图展示
.architecture-showcase {
  margin-bottom: 80px;
  
  .showcase-header {
    text-align: center;
    margin-bottom: 60px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 36px;
      font-weight: 700;
      background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 18px;
    }
  }
  
  .architecture-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 32px;
    
    .arch-module-card {
      position: relative;
      padding: 32px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      cursor: pointer;
      transition: all 0.3s ease;
      overflow: hidden;
      
      &:hover {
        transform: translateY(-8px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
        
        .module-overlay {
          opacity: 1;
        }
      }
      
      .module-visual {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
        
        .module-icon {
          width: 64px;
          height: 64px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 16px;
          color: var(--primary);
          font-size: 24px;
        }
        
        .module-status {
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
            
            &.online {
              background: var(--market-rise);
              animation: pulse 2s infinite;
            }
            
            &.warning {
              background: #f59e0b;
            }
            
            &.error {
              background: var(--market-fall);
            }
          }
          
          .status-text {
            font-size: 12px;
            color: var(--text-secondary);
          }
        }
      }
      
      .module-info {
        h3 {
          margin: 0 0 12px 0;
          font-size: 20px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        p {
          margin: 0 0 20px 0;
          color: var(--text-secondary);
          font-size: 14px;
          line-height: 1.6;
        }
        
        .module-stats {
          display: flex;
          gap: 24px;
          
          .stat-item {
            display: flex;
            flex-direction: column;
            
            .stat-label {
              font-size: 12px;
              color: var(--text-secondary);
              margin-bottom: 4px;
            }
            
            .stat-value {
              font-size: 18px;
              font-weight: 600;
              color: var(--text-primary);
            }
          }
        }
      }
      
      .module-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(37, 99, 235, 0.9);
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
        
        .overlay-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          color: white;
          
          i {
            font-size: 24px;
          }
          
          span {
            font-size: 16px;
            font-weight: 500;
          }
        }
      }
    }
  }
}

// 技术栈展示
.tech-stack-section {
  margin-bottom: 80px;
  
  .section-header {
    text-align: center;
    margin-bottom: 60px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 36px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 18px;
    }
  }
  
  .tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 32px;
    
    .tech-card {
      padding: 32px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
      }
      
      .tech-icon {
        width: 64px;
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        margin-bottom: 20px;
        color: var(--primary);
        font-size: 28px;
      }
      
      .tech-info {
        h4 {
          margin: 0 0 12px 0;
          font-size: 20px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        p {
          margin: 0 0 16px 0;
          color: var(--text-secondary);
          font-size: 14px;
          line-height: 1.6;
        }
        
        .tech-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          
          .tech-tag {
            padding: 4px 8px;
            background: rgba(37, 99, 235, 0.1);
            color: var(--primary);
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
          }
        }
      }
    }
  }
}

// 性能指标
.performance-section {
  .section-header {
    text-align: center;
    margin-bottom: 60px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 36px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 18px;
    }
  }
  
  .performance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    
    .performance-card {
      padding: 24px;
      background: rgba(26, 26, 46, 0.6);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      
      .metric-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        
        .metric-icon {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          color: var(--primary);
          font-size: 18px;
        }
        
        .metric-title {
          font-size: 16px;
          font-weight: 500;
          color: var(--text-primary);
        }
      }
      
      .metric-value {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 16px;
        
        .metric-unit {
          font-size: 16px;
          font-weight: 400;
          color: var(--text-secondary);
          margin-left: 4px;
        }
        
        &.good {
          color: var(--market-rise);
        }
        
        &.normal {
          color: var(--text-primary);
        }
        
        &.warning {
          color: #f59e0b;
        }
        
        &.error {
          color: var(--market-fall);
        }
      }
      
      .metric-chart {
        height: 60px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 4px;
        position: relative;
        overflow: hidden;
        
        &::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(37, 99, 235, 0.3), transparent);
          animation: chartFlow 3s linear infinite;
        }
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

@keyframes chartFlow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .architecture-grid,
  .tech-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
  
  .performance-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 20px;
    
    .header-content {
      flex-direction: column;
      gap: 16px;
      text-align: center;
    }
  }
  
  .main-content {
    padding: 20px;
  }
  
  .architecture-grid,
  .tech-grid,
  .performance-grid {
    grid-template-columns: 1fr;
  }
}
</style>