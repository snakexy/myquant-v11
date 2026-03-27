<template>
  <div class="research-page">
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
          <h1 class="page-title">研究阶段</h1>
          <p class="page-subtitle">量化策略研究与开发 - 探索市场规律与机会</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="startNewResearch">
              <i class="fas fa-play"></i>
              <span>新建研究</span>
            </button>
            <button class="secondary-btn" @click="openResearchHistory">
              <i class="fas fa-history"></i>
              <span>研究历史</span>
            </button>
            <button class="secondary-btn" @click="openSettings">
              <i class="fas fa-cog"></i>
              <span>设置</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 研究工作台 -->
      <section class="research-workspace">
        <div class="workspace-grid">
          <!-- 数据驱动研究 -->
          <div class="workspace-card" @click="navigateToDataResearch">
            <div class="card-icon">
              <i class="fas fa-database"></i>
            </div>
            <div class="card-content">
              <h3>数据驱动研究</h3>
              <p>基于历史数据进行模式识别和规律发现</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">数据集</span>
                  <span class="stat-value">24</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">模型</span>
                  <span class="stat-value">18</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 75%"></div>
            </div>
          </div>

          <!-- 模型训练 -->
          <div class="workspace-card" @click="navigateToModelTraining">
            <div class="card-icon">
              <i class="fas fa-brain"></i>
            </div>
            <div class="card-content">
              <h3>模型训练</h3>
              <p>训练和优化量化策略模型</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">训练中</span>
                  <span class="stat-value">6</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">已完成</span>
                  <span class="stat-value">42</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 85%"></div>
            </div>
          </div>

          <!-- AI策略生成 -->
          <div class="workspace-card" @click="navigateToAIStrategy">
            <div class="card-icon">
              <i class="fas fa-robot"></i>
            </div>
            <div class="card-content">
              <h3>AI策略生成</h3>
              <p>使用AI技术辅助策略开发</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">AI模型</span>
                  <span class="stat-value">8</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">生成数</span>
                  <span class="stat-value">156</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 65%"></div>
            </div>
          </div>

          <!-- 回测分析 -->
          <div class="workspace-card" @click="navigateToBacktest">
            <div class="card-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="card-content">
              <h3>回测分析</h3>
              <p>验证策略的历史表现</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">回测数</span>
                  <span class="stat-value">89</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">胜率</span>
                  <span class="stat-value">72%</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 80%"></div>
            </div>
          </div>

          <!-- 风险评估 -->
          <div class="workspace-card" @click="navigateToRiskAssessment">
            <div class="card-icon">
              <i class="fas fa-shield-alt"></i>
            </div>
            <div class="card-content">
              <h3>风险评估</h3>
              <p>分析策略的风险特征</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">风险指标</span>
                  <span class="stat-value">16</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">压力测试</span>
                  <span class="stat-value">12</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 70%"></div>
            </div>
          </div>

          <!-- 性能优化 -->
          <div class="workspace-card" @click="navigateToPerformanceOptimization">
            <div class="card-icon">
              <i class="fas fa-tachometer-alt"></i>
            </div>
            <div class="card-content">
              <h3>性能优化</h3>
              <p>优化策略执行效率</p>
              <div class="card-stats">
                <div class="stat-item">
                  <span class="stat-label">优化项</span>
                  <span class="stat-value">34</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">提升率</span>
                  <span class="stat-value">28%</span>
                </div>
              </div>
            </div>
            <div class="card-progress">
              <div class="progress-bar" style="width: 60%"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 当前研究任务 -->
      <section class="current-tasks">
        <div class="section-header">
          <h2>当前研究任务</h2>
          <button class="view-all-btn" @click="viewAllTasks">
            <span>查看全部</span>
            <i class="fas fa-arrow-right"></i>
          </button>
        </div>
        
        <div class="tasks-grid">
          <div class="task-card" v-for="task in currentTasks" :key="task.id">
            <div class="task-header">
              <h3>{{ task.name }}</h3>
              <div class="task-status" :class="task.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ task.statusText }}</span>
              </div>
            </div>
            
            <p class="task-description">{{ task.description }}</p>
            
            <div class="task-progress">
              <div class="progress-info">
                <span class="progress-label">进度</span>
                <span class="progress-value">{{ task.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
              </div>
            </div>
            
            <div class="task-metrics">
              <div class="metric-item">
                <span class="metric-label">准确率</span>
                <span class="metric-value" :class="getPerformanceClass(task.accuracy)">
                  {{ task.accuracy.toFixed(1) }}%
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">收益率</span>
                <span class="metric-value" :class="getPerformanceClass(task.return)">
                  {{ task.return > 0 ? '+' : '' }}{{ task.return.toFixed(2) }}%
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">夏普比率</span>
                <span class="metric-value">{{ task.sharpeRatio.toFixed(2) }}</span>
              </div>
            </div>
            
            <div class="task-footer">
              <div class="task-time">
                <i class="fas fa-clock"></i>
                <span>{{ task.estimatedTime }}</span>
              </div>
              <div class="task-actions">
                <button class="action-btn" @click="pauseTask(task)" v-if="task.status === 'running'">
                  <i class="fas fa-pause"></i>
                </button>
                <button class="action-btn" @click="resumeTask(task)" v-else-if="task.status === 'paused'">
                  <i class="fas fa-play"></i>
                </button>
                <button class="action-btn" @click="viewTask(task)">
                  <i class="fas fa-eye"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 研究工具箱 -->
      <section class="research-tools">
        <div class="section-header">
          <h2>研究工具箱</h2>
          <p>专业的量化研究工具和平台</p>
        </div>
        
        <div class="tools-grid">
          <div class="tool-card" v-for="tool in researchTools" :key="tool.id" @click="openTool(tool)">
            <div class="tool-icon">
              <i :class="tool.icon"></i>
            </div>
            <div class="tool-content">
              <h3>{{ tool.name }}</h3>
              <p>{{ tool.description }}</p>
            </div>
            <div class="tool-badge" v-if="tool.isNew">新</div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 响应式数据
const currentTasks = ref([
  {
    id: 1,
    name: '多因子选股策略研究',
    description: '基于财务指标和技术指标的多因子选股模型，通过机器学习方法优化因子权重',
    status: 'running',
    statusText: '运行中',
    progress: 75,
    accuracy: 78.5,
    return: 12.3,
    sharpeRatio: 1.85,
    estimatedTime: '剩余2小时'
  },
  {
    id: 2,
    name: '动量反转策略优化',
    description: '结合市场情绪指标的动量反转策略，在不同市场环境下自适应调整参数',
    status: 'running',
    statusText: '运行中',
    progress: 45,
    accuracy: 72.1,
    return: 8.7,
    sharpeRatio: 1.42,
    estimatedTime: '剩余5小时'
  },
  {
    id: 3,
    name: '行业轮动模型',
    description: '基于宏观经济数据的行业轮动模型，预测未来3-6个月的行业表现',
    status: 'paused',
    statusText: '已暂停',
    progress: 30,
    accuracy: 65.8,
    return: -2.4,
    sharpeRatio: 0.68,
    estimatedTime: '剩余8小时'
  }
])

const researchTools = ref([
  {
    id: 1,
    name: '数据挖掘工具',
    description: '从海量数据中发现隐藏模式和规律',
    icon: 'fas fa-database',
    isNew: false
  },
  {
    id: 2,
    name: '特征工程平台',
    description: '自动化特征提取和选择工具',
    icon: 'fas fa-cogs',
    isNew: true
  },
  {
    id: 3,
    name: '模型训练框架',
    description: '支持多种机器学习算法的训练平台',
    icon: 'fas fa-brain',
    isNew: false
  },
  {
    id: 4,
    name: '回测分析系统',
    description: '全面的策略回测和性能分析工具',
    icon: 'fas fa-chart-line',
    isNew: false
  },
  {
    id: 5,
    name: '风险评估工具',
    description: '多维度的风险度量和预警系统',
    icon: 'fas fa-exclamation-triangle',
    isNew: false
  },
  {
    id: 6,
    name: '可视化分析平台',
    description: '交互式数据可视化和分析工具',
    icon: 'fas fa-chart-pie',
    isNew: true
  }
])

// 方法
const startNewResearch = () => {
  console.log('开始新研究')
}

const openResearchHistory = () => {
  console.log('打开研究历史')
}

const openSettings = () => {
  console.log('打开设置')
}

const navigateToDataResearch = () => {
  console.log('导航到数据驱动研究')
}

const navigateToModelTraining = () => {
  console.log('导航到模型训练')
}

const navigateToAIStrategy = () => {
  console.log('导航到AI策略生成')
}

const navigateToBacktest = () => {
  console.log('导航到回测分析')
}

const navigateToRiskAssessment = () => {
  console.log('导航到风险评估')
}

const navigateToPerformanceOptimization = () => {
  console.log('导航到性能优化')
}

const viewAllTasks = () => {
  console.log('查看所有任务')
}

const pauseTask = (task: any) => {
  console.log('暂停任务:', task.name)
}

const resumeTask = (task: any) => {
  console.log('恢复任务:', task.name)
}

const viewTask = (task: any) => {
  console.log('查看任务:', task.name)
}

const openTool = (tool: any) => {
  console.log('打开工具:', tool.name)
}

const getPerformanceClass = (value: number) => {
  if (value > 0) return 'positive'
  if (value < 0) return 'negative'
  return 'neutral'
}

// 初始化粒子系统
const initParticleSystem = () => {
  const particleSystemEl = document.querySelector('.particle-system')
  if (!particleSystemEl) return
  
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  if (!ctx) return
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  canvas.style.position = 'absolute'
  canvas.style.top = '0'
  canvas.style.left = '0'
  canvas.style.pointerEvents = 'none'
  
  particleSystemEl.appendChild(canvas)
  
  // 简单的粒子动画
  const particles: any[] = []
  for (let i = 0; i < 25; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
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
      ctx.fillStyle = `rgba(59, 130, 246, ${particle.opacity})`
      ctx.fill()
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 生命周期
onMounted(() => {
  initParticleSystem()
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.research-page {
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
      rgba(59, 130, 246, 0.03) 50%, 
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
      background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
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
    .action-buttons {
      display: flex;
      gap: 16px;
      
      .primary-btn, .secondary-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
      }
      
      .primary-btn {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
        }
      }
      
      .secondary-btn {
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-primary);
        border: 1px solid rgba(255, 255, 255, 0.1);
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
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
  max-width: 1400px;
  margin: 0 auto;
}

// 研究工作台
.research-workspace {
  margin-bottom: 60px;
  
  .workspace-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    
    .workspace-card {
      position: relative;
      padding: 24px;
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      overflow: hidden;
      box-shadow:
        0 8px 32px rgba(59, 130, 246, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      cursor: pointer;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        box-shadow:
          0 12px 40px rgba(59, 130, 246, 0.15),
          inset 0 1px 0 rgba(255, 255, 255, 0.15);
      }
      
      .card-icon {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(59, 130, 246, 0.1);
        border-radius: 12px;
        color: #3b82f6;
        font-size: 20px;
      }
      
      .card-content {
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
          line-height: 1.5;
        }
        
        .card-stats {
          display: flex;
          gap: 24px;
          
          .stat-item {
            display: flex;
            flex-direction: column;
            gap: 4px;
            
            .stat-label {
              font-size: 12px;
              color: var(--text-secondary);
            }
            
            .stat-value {
              font-size: 18px;
              font-weight: 600;
              color: var(--text-primary);
            }
          }
        }
      }
      
      .card-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.1);
        
        .progress-bar {
          height: 100%;
          background: linear-gradient(90deg, #3b82f6, #2563eb);
          transition: width 0.3s ease;
        }
      }
    }
  }
}

// 当前研究任务
.current-tasks {
  margin-bottom: 60px;
  
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 40px;
    
    h2 {
      margin: 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    .view-all-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      color: var(--text-primary);
      font-size: 14px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
      }
    }
  }
  
  .tasks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 24px;
    
    .task-card {
      padding: 24px;
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      box-shadow:
        0 8px 32px rgba(59, 130, 246, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        box-shadow:
          0 12px 40px rgba(59, 130, 246, 0.15),
          inset 0 1px 0 rgba(255, 255, 255, 0.15);
      }
      
      .task-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        
        h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .task-status {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          
          &.running {
            background: rgba(16, 185, 129, 0.1);
            color: var(--market-rise);
           
            .status-dot {
              background: var(--market-rise);
              animation: pulse 2s infinite;
            }
          }
          
          &.paused {
            background: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
           
            .status-dot {
              background: #f59e0b;
            }
          }
          
          &.completed {
            background: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
           
            .status-dot {
              background: #3b82f6;
            }
          }
          
          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
          }
        }
      }
      
      .task-description {
        margin: 0 0 20px 0;
        color: var(--text-secondary);
        font-size: 14px;
        line-height: 1.5;
      }
      
      .task-progress {
        margin-bottom: 20px;
        
        .progress-info {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          
          .progress-label {
            font-size: 12px;
            color: var(--text-secondary);
          }
          
          .progress-value {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-primary);
          }
        }
        
        .progress-bar {
          height: 6px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
          overflow: hidden;
          
          .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            transition: width 0.3s ease;
          }
        }
      }
      
      .task-metrics {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 20px;
        
        .metric-item {
          text-align: center;
          
          .metric-label {
            display: block;
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 4px;
          }
          
          .metric-value {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
           
            // 收益率（红涨绿跌）
            &.positive {
              color: var(--market-rise);
            }

            &.negative {
              color: var(--market-fall);
            }
          }
        }
      }
      
      .task-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        
        .task-time {
          display: flex;
          align-items: center;
          gap: 6px;
          color: var(--text-secondary);
          font-size: 12px;
        }
        
        .task-actions {
          display: flex;
          gap: 8px;
          
          .action-btn {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: var(--text-primary);
            cursor: pointer;
            transition: all 0.2s ease;
           
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

// 研究工具箱
.research-tools {
  .section-header {
    text-align: center;
    margin-bottom: 40px;
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    p {
      margin: 0;
      color: var(--text-secondary);
      font-size: 16px;
    }
  }
  
  .tools-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
    
    .tool-card {
      position: relative;
      padding: 24px;
      background: rgba(255, 255, 255, 0.02);
      backdrop-filter: blur(8px) saturate(120%);
      -webkit-backdrop-filter: blur(8px) saturate(120%);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      box-shadow:
        0 8px 32px rgba(59, 130, 246, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
      cursor: pointer;
      
      &:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px) saturate(150%);
        -webkit-backdrop-filter: blur(12px) saturate(150%);
        box-shadow:
          0 12px 40px rgba(59, 130, 246, 0.15),
          inset 0 1px 0 rgba(255, 255, 255, 0.15);
      }
      
      .tool-icon {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(59, 130, 246, 0.1);
        border-radius: 12px;
        color: #3b82f6;
        font-size: 20px;
      }
      
      .tool-content {
        h3 {
          margin: 0 0 12px 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        p {
          margin: 0;
          color: var(--text-secondary);
          font-size: 14px;
          line-height: 1.5;
        }
      }
      
      .tool-badge {
        position: absolute;
        top: 16px;
        left: 16px;
        padding: 4px 8px;
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        font-size: 12px;
        font-weight: 500;
        border-radius: 12px;
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

// 响应式设计
@media (max-width: 1024px) {
  .workspace-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tasks-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tools-grid {
    grid-template-columns: repeat(2, 1fr);
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
  
  .workspace-grid {
    grid-template-columns: 1fr;
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
  }
}
</style>