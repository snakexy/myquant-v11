<template>
  <div class="unreal-blueprint-view">
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
          <h1 class="page-title">Unreal Engine 蓝图系统</h1>
          <p class="page-subtitle">智能节点连接与可视化编程平台</p>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="primary-btn" @click="saveBlueprint">
              <i class="fas fa-save"></i>
              <span>保存蓝图</span>
            </button>
            <button class="secondary-btn" @click="exportBlueprint">
              <i class="fas fa-download"></i>
              <span>导出代码</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- Unreal蓝图系统 -->
      <UnrealBlueprintSystem ref="blueprintSystem" />
      
      <!-- 系统信息面板 -->
      <section class="info-panel">
        <div class="panel-section">
          <h3>系统状态</h3>
          <div class="status-grid">
            <div class="status-item">
              <span class="status-label">节点数量</span>
              <span class="status-value">{{ nodeCount }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">连接数量</span>
              <span class="status-value">{{ connectionCount }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">活动连接</span>
              <span class="status-value">{{ activeConnections }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">系统负载</span>
              <span class="status-value" :class="systemLoadClass">{{ systemLoad }}%</span>
            </div>
          </div>
        </div>
        
        <div class="panel-section">
          <h3>性能监控</h3>
          <div class="performance-chart">
            <canvas ref="performanceChart" width="300" height="150"></canvas>
          </div>
        </div>
        
        <div class="panel-section">
          <h3>快捷操作</h3>
          <div class="quick-actions">
            <button class="action-btn" @click="autoArrange">
              <i class="fas fa-magic"></i>
              <span>智能排列</span>
            </button>
            <button class="action-btn" @click="validateBlueprint">
              <i class="fas fa-check-circle"></i>
              <span>验证蓝图</span>
            </button>
            <button class="action-btn" @click="optimizeConnections">
              <i class="fas fa-route"></i>
              <span>优化连接</span>
            </button>
            <button class="action-btn" @click="clearCanvas">
              <i class="fas fa-trash-alt"></i>
              <span>清空画布</span>
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import UnrealBlueprintSystem from '../components/UnrealBlueprintSystem.vue'

// 响应式数据
const blueprintSystem = ref<InstanceType<typeof UnrealBlueprintSystem>>()
const nodeCount = ref(0)
const connectionCount = ref(0)
const activeConnections = ref(0)
const systemLoad = ref(25)
const performanceChart = ref<HTMLCanvasElement | null>(null)

// 计算属性
const systemLoadClass = computed(() => {
  if (systemLoad.value < 30) return 'success'
  if (systemLoad.value < 60) return 'warning'
  return 'error'
})

// 方法
const saveBlueprint = () => {
  console.log('保存蓝图')
  // 这里可以实现蓝图保存逻辑
}

const exportBlueprint = () => {
  console.log('导出代码')
  // 这里可以实现代码导出逻辑
}

const autoArrange = () => {
  console.log('智能排列')
  // 调用蓝图系统的自动排列功能
  if (blueprintSystem.value) {
    blueprintSystem.value.executeLayoutTool('auto-distribute')
  }
}

const validateBlueprint = () => {
  console.log('验证蓝图')
  // 这里可以实现蓝图验证逻辑
}

const optimizeConnections = () => {
  console.log('优化连接')
  // 调用蓝图系统的连接优化功能
  if (blueprintSystem.value) {
    blueprintSystem.value.executeLayoutTool('force-layout')
  }
}

const clearCanvas = () => {
  console.log('清空画布')
  // 这里可以实现画布清空逻辑
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
  for (let i = 0; i < 30; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      size: Math.random() * 3 + 1,
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
      ctx.fillStyle = `rgba(124, 58, 237, ${particle.opacity})`
      ctx.fill()
    })
    
    requestAnimationFrame(animate)
  }
  
  animate()
}

// 初始化性能图表
const initPerformanceChart = () => {
  if (!performanceChart.value) return
  
  const canvas = performanceChart.value
  const ctx = canvas.getContext('2d')
  
  if (!ctx) return
  
  // 模拟性能数据
  const data = [65, 72, 68, 75, 82, 78, 85, 88, 92, 87, 90]
  const labels = ['10s', '20s', '30s', '40s', '50s', '60s', '70s', '80s', '90s', '100s']
  
  // 清空画布
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // 绘制坐标轴
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(30, 20)
  ctx.lineTo(30, 130)
  ctx.moveTo(30, 130)
  ctx.lineTo(280, 130)
  ctx.stroke()
  
  // 绘制数据线
  ctx.strokeStyle = '#00ff88'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  const stepX = 250 / (data.length - 1)
  data.forEach((value, index) => {
    const x = 30 + index * stepX
    const y = 130 - (value / 100) * 100
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
  
  // 绘制数据点
  data.forEach((value, index) => {
    const x = 30 + index * stepX
    const y = 130 - (value / 100) * 100
    
    ctx.fillStyle = '#00ff88'
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fill()
  })
  
  // 绘制标签
  ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
  ctx.font = '10px Arial'
  ctx.textAlign = 'center'
  
  labels.forEach((label, index) => {
    if (index % 2 === 0) {
      const x = 30 + index * stepX
      ctx.fillText(label, x, 145)
    }
  })
}

// 模拟数据更新
const updateSystemData = () => {
  // 模拟节点和连接数量变化
  nodeCount.value = 5 + Math.floor(Math.random() * 3)
  connectionCount.value = 8 + Math.floor(Math.random() * 4)
  activeConnections.value = Math.floor(connectionCount.value * 0.8)
  systemLoad.value = 20 + Math.floor(Math.random() * 40)
  
  // 更新性能图表
  initPerformanceChart()
}

// 生命周期
onMounted(() => {
  initParticleSystem()
  initPerformanceChart()
  
  // 定期更新系统数据
  setInterval(updateSystemData, 3000)
})
</script>

<style lang="scss" scoped>
.unreal-blueprint-view {
  position: relative;
  min-height: 100vh;
  background: #0a0a0f;
  color: #f8fafc;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
  background: #0a0a0f;
  
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
      rgba(124, 58, 237, 0.03) 50%,
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
  background: rgba(26, 26, 46, 0.9);
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
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .page-subtitle {
      margin: 0;
      color: #cbd5e1;
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
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
  padding: 20px;
  display: flex;
  gap: 20px;
  height: calc(100vh - 120px);
  
  // 蓝图系统占据主要空间
  > :deep(.unreal-blueprint-system) {
    flex: 1;
    height: 100%;
  }
}

// 信息面板
.info-panel {
  width: 350px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  
  .panel-section {
    background: rgba(26, 26, 46, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
    
    h3 {
      margin: 0 0 16px 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .status-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      
      .status-item {
        text-align: center;
        padding: 12px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        
        .status-label {
          display: block;
          font-size: 12px;
          color: var(--text-secondary);
          margin-bottom: 4px;
        }
        
        .status-value {
          font-size: 20px;
          font-weight: 700;
          color: var(--text-primary);
          
          &.success {
            color: var(--market-rise);
          }
          
          &.warning {
            color: #f59e0b;
          }
          
          &.error {
            color: var(--market-fall);
          }
        }
      }
    }
    
    .performance-chart {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      padding: 16px;
      text-align: center;
      
      canvas {
        max-width: 100%;
        height: auto;
      }
    }
    
    .quick-actions {
      display: flex;
      flex-direction: column;
      gap: 8px;
      
      .action-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: var(--text-primary);
        font-size: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
        
        i {
          width: 16px;
          text-align: center;
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

// 响应式设计
@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
    
    .info-panel {
      width: 100%;
      flex-direction: row;
      flex-wrap: wrap;
      
      .panel-section {
        flex: 1;
        min-width: 300px;
      }
    }
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
    padding: 16px;
    flex-direction: column;
    
    .info-panel {
      width: 100%;
      
      .panel-section {
        padding: 16px;
      }
    }
  }
}
</style>