<template>
  <div class="home">
    
    <!-- 背景装饰效果 -->
    <div class="bg-decoration">
      <div class="bg-gradient-overlay"></div>
      <div class="bg-circle-1"></div>
      <div class="bg-circle-2"></div>
      <div class="bg-circle-3"></div>
    </div>

    <!-- 主标题区域 -->
    <div class="hero-section">
      <div class="title-container">
        <h1 class="main-title">
          <span class="title-gradient">MyQuant</span>
        </h1>
      </div>
    </div>
    
    <!-- 功能卡片网格 -->
    <div class="function-cards">
      <div
        v-for="(card, index) in functionCards"
        :key="card.id"
        class="card"
        :class="[card.theme, { 'dragging': draggedCard === index, 'drag-over': draggedOverCard === index }]"
        draggable="true"
        @click="navigateTo(card.route)"
        @mouseenter="onCardHover(index, true)"
        @mouseleave="onCardHover(index, false)"
        @dragstart="onDragStart($event, index)"
        @dragend="onDragEnd"
        @dragover="onDragOver($event)"
        @dragenter="onDragEnter(index)"
        @dragleave="onDragLeave"
        @drop="onDrop($event, index)"
      >
        <div class="card-background">
          <div class="card-pattern"></div>
          <div class="card-glow"></div>
        </div>
        
        <div class="card-content">
          <div class="card-icon">
            <div class="icon-container">{{ card.icon }}</div>
            <div class="icon-particles"></div>
          </div>
          
          <div class="card-text">
            <h2>{{ card.title }}</h2>
            <p>{{ card.description }}</p>
          </div>
          
          <!-- 移除无用的指示器小点点 -->
        </div>
        
        <div class="card-border"></div>
        <div class="neon-border"></div>
      </div>
    </div>

    <!-- 数据统计区域 - 移除卡片背景，纯文本展示 -->
    <div class="data-stats">
      <div class="stat-item">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <span class="stat-label">总股票数</span>
          <span class="stat-value">4,528</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon">🔄</div>
        <div class="stat-content">
          <span class="stat-label">今日更新</span>
          <span class="stat-value">1,234</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon">✨</div>
        <div class="stat-content">
          <span class="stat-label">数据质量</span>
          <span class="stat-value">98.5%</span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 功能卡片数据
const functionCards = ref([
  {
    id: 1,
    title: '数据管理',
    description: '数据库查看、数据新鲜度监控',
    icon: '📊',
    route: '/data-management',
    theme: 'data-theme'
  },
  {
    id: 2,
    title: '回测功能',
    description: '策略回测验证、多模型对比',
    icon: '🧪',
    route: '/backtest',
    theme: 'backtest-theme'
  },
  {
    id: 3,
    title: '策略生成',
    description: 'AI智能辅助、策略生成、结果分析',
    icon: '🤖',
    route: '/strategy',
    theme: 'strategy-theme'
  },
  {
    id: 4,
    title: '实盘交易',
    description: '实时交易执行、风险控制、收益监控',
    icon: '💰',
    route: '/trading',
    theme: 'trading-theme'
  },
  {
    id: 5,
    title: '系统监控',
    description: '系统状态监控、性能指标、预警系统',
    icon: '🖥️',
    route: '/monitoring',
    theme: 'monitoring-theme'
  },
  {
    id: 6,
    title: '模型管理',
    description: '在线滚动训练、元学习引擎、模型版本管理',
    icon: '🧠',
    route: '/model-management',
    theme: 'model-theme'
  }
])

// 拖拽相关状态
const draggedCard = ref<number | null>(null)
const draggedOverCard = ref<number | null>(null)

// 导航函数
const navigateTo = (route: string) => {
  router.push(route)
}

// 拖拽开始
const onDragStart = (event: DragEvent, index: number) => {
  draggedCard.value = index
  event.dataTransfer?.setData('text/plain', index.toString())
}

// 拖拽结束
const onDragEnd = () => {
  draggedCard.value = null
  draggedOverCard.value = null
}

// 拖拽经过
const onDragOver = (event: DragEvent) => {
  event.preventDefault()
}

// 拖拽进入
const onDragEnter = (index: number) => {
  if (draggedCard.value !== null && draggedCard.value !== index) {
    draggedOverCard.value = index
  }
}

// 拖拽离开
const onDragLeave = () => {
  draggedOverCard.value = null
}

// 放置
const onDrop = (event: DragEvent, dropIndex: number) => {
  event.preventDefault()
  
  if (draggedCard.value !== null && draggedCard.value !== dropIndex) {
    // 交换卡片位置
    const draggedItem = functionCards.value[draggedCard.value]
    const dropItem = functionCards.value[dropIndex]
    
    // 创建新数组
    const newCards = [...functionCards.value]
    newCards[draggedCard.value] = dropItem
    newCards[dropIndex] = draggedItem
    
    functionCards.value = newCards
  }
  
  onDragEnd()
}

// 卡片悬停效果
const onCardHover = (index: number, isHovering: boolean) => {
  // 可以在这里添加额外的悬停逻辑
}
</script>

<style scoped>
/* 主容器 */
.home {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(ellipse at top left, rgba(37, 99, 235, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at bottom right, rgba(124, 58, 237, 0.12) 0%, transparent 50%),
    radial-gradient(ellipse at center, rgba(16, 185, 129, 0.08) 0%, transparent 50%),
    linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
}

/* 背景装饰效果 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.bg-gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    ellipse at top left,
    rgba(37, 99, 235, 0.1) 0%,
    transparent 50%
  ),
  radial-gradient(
    ellipse at bottom right,
    rgba(124, 58, 237, 0.08) 0%,
    transparent 50%
  );
}

.bg-circle-1 {
  position: absolute;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.15) 0%, transparent 70%);
  top: 15%;
  left: 10%;
}

.bg-circle-2 {
  position: absolute;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.12) 0%, transparent 70%);
  top: 60%;
  right: 15%;
}

.bg-circle-3 {
  position: absolute;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
  bottom: 20%;
  left: 50%;
}



/* 内容容器 */
.home > * {
  position: relative;
  z-index: 10;
}

/* 标题区域 */
.hero-section {
  position: relative;
  z-index: 10;
  padding: 60px 32px 30px;
  text-align: center;
}

.title-container {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
}

.main-title {
  font-size: 64px;
  font-weight: 800;
  margin: 0 0 16px 0;
  position: relative;
  z-index: 2;
}

.title-gradient {
  color: #2563eb;
  display: block;
}

@keyframes gradientFlow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.title-subtitle {
  font-size: 20px;
  color: #cbd5e1;
  margin: 0;
  font-weight: 300;
  letter-spacing: 2px;
  opacity: 0.9;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.title-decoration {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120%;
  height: 2px;
  z-index: 1;
}

.data-stream {
  width: 100%;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    #00ffff,
    #ff00ff,
    #ffff00,
    transparent
  );
  position: absolute;
  top: 50%;
  left: -100%;
  animation: dataFlow 3s linear infinite;
  filter: drop-shadow(0 0 10px rgba(0, 255, 255, 0.8));
}

@keyframes dataFlow {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* 数据统计区域 - 移动到页面最底部 */
.data-stats {
  position: fixed;
  bottom: 40px; /* 上移一些距离，避免压住边框 */
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  justify-content: center;
  gap: 48px;
  max-width: 800px;
  padding: 0 32px;
  z-index: 100;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  background: transparent; /* 移除背景边框 */
  backdrop-filter: none; /* 移除模糊效果 */
  -webkit-backdrop-filter: none;
  padding: 8px 12px; /* 减少padding */
  border: none; /* 移除边框 */
  border-radius: 0; /* 移除圆角 */
}

.stat-icon {
  font-size: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
}

/* 功能卡片 */
.function-cards {
  position: relative;
  z-index: 10;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 32px 120px; /* 增加底部padding，为底部数据统计留空间 */
}

.card {
  position: relative;
  height: 280px;
  cursor: pointer;
  border-radius: 24px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.card.dragging {
  opacity: 0.5;
  transform: scale(0.95);
  cursor: grabbing;
}

.card.drag-over {
  transform: scale(1.05);
  box-shadow:
    0 0 20px rgba(0, 255, 255, 0.4),
    0 0 40px rgba(0, 255, 255, 0.2);
}

.card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.card-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  opacity: 0.6;
}

.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card-content {
  position: relative;
  z-index: 2;
  height: 100%;
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  backdrop-filter: blur(16px) saturate(200%);
  -webkit-backdrop-filter: blur(16px) saturate(200%);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.card-icon {
  position: relative;
  width: 80px;
  height: 80px;
  margin-bottom: 20px;
  margin-left: auto;
  margin-right: auto;
}

.icon-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 80px; /* 放大一倍，从40px到80px */
  background: transparent;
  border: none;
  border-radius: 0;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.icon-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card-text {
  flex: 1;
}

.card-text h2 {
  font-size: 24px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.card-text p {
  font-size: 16px;
  color: #e2e8f0;
  margin: 0;
  line-height: 1.6;
  opacity: 0.95;
}

/* 移除指示器相关样式 */

.card-border {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 24px;
  border: 2px solid transparent;
  background: linear-gradient(135deg, transparent, rgba(255, 255, 255, 0.1), transparent) border-box;
  mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  mask-composite: subtract;
  opacity: 0;
  transition: opacity 0.3s ease;
}

/* 卡片霓虹边框 */
.card .neon-border {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 24px;
  opacity: 0;
  z-index: -1;
  filter: blur(8px);
  transition: opacity 0.3s ease;
  animation: neonBorder 3s linear infinite;
}

.data-theme .neon-border {
  background: linear-gradient(
    45deg,
    #00ffff,
    #00cccc,
    #0099ff,
    #00ffff
  );
}

.backtest-theme .neon-border {
  background: linear-gradient(
    45deg,
    #ff00ff,
    #cc00cc,
    #ff0099,
    #ff00ff
  );
}

.strategy-theme .neon-border {
  background: linear-gradient(
    45deg,
    #ffff00,
    #cccc00,
    #ffcc00,
    #ffff00
  );
}

.trading-theme .neon-border {
  background: linear-gradient(
    45deg,
    #00ff00,
    #00cc00,
    #66ff00,
    #00ff00
  );
}

.monitoring-theme .neon-border {
  background: linear-gradient(
    45deg,
    #ff6600,
    #cc5200,
    #ff9900,
    #ff6600
  );
}

.model-theme .neon-border {
  background: linear-gradient(
    45deg,
    #ff0066,
    #cc0052,
    #ff3399,
    #ff0066
  );
}

/* 悬停效果 */
.card:hover {
  transform: translateY(-12px) scale(1.03);
}

.card:hover .card-glow {
  opacity: 1;
}

.card:hover .icon-particles {
  opacity: 1;
  animation: iconPulse 1.2s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

/* 移除指示器相关样式，因为没有实际作用 */

.card:hover .card-border {
  opacity: 1;
}

.card:hover .neon-border {
  opacity: 0; /* 完全移除霓虹边框效果 */
}

/* 默认状态：无动画，无发光 */
.data-theme .icon-container {
  filter: none;
  transition: all 0.3s ease;
}

.data-theme:hover .icon-container {
  filter:
    drop-shadow(0 0 12px rgba(100, 200, 255, 0.8))
    drop-shadow(0 0 24px rgba(100, 200, 255, 0.6));
  transform: scale(1.1);
  animation: iconBounce 0.6s ease-in-out infinite;
}

.backtest-theme .icon-container {
  filter: none;
  transition: all 0.3s ease;
}

.backtest-theme:hover .icon-container {
  filter:
    drop-shadow(0 0 12px rgba(200, 100, 255, 0.8))
    drop-shadow(0 0 24px rgba(200, 100, 255, 0.6));
  transform: scale(1.1);
  animation: iconBounce 0.6s ease-in-out infinite;
}

.strategy-theme .icon-container {
  filter: none;
  transition: all 0.3s ease;
}

.strategy-theme:hover .icon-container {
  filter:
    drop-shadow(0 0 12px rgba(150, 150, 255, 0.8))
    drop-shadow(0 0 24px rgba(150, 150, 255, 0.6));
  transform: scale(1.1);
  animation: iconBounce 0.6s ease-in-out infinite;
}

.trading-theme .icon-container {
  filter: none;
  transition: all 0.3s ease;
}

.trading-theme:hover .icon-container {
  filter:
    drop-shadow(0 0 12px rgba(255, 215, 0, 0.8))
    drop-shadow(0 0 24px rgba(255, 215, 0, 0.6));
  transform: scale(1.1);
  animation: iconBounce 0.6s ease-in-out infinite;
}

.monitoring-theme .icon-container {
  filter: none;
  transition: all 0.3s ease;
}

.monitoring-theme:hover .icon-container {
  filter:
    drop-shadow(0 0 12px rgba(100, 150, 255, 0.8))
    drop-shadow(0 0 24px rgba(100, 150, 255, 0.6));
  transform: scale(1.1);
  animation: iconBounce 0.6s ease-in-out infinite;
}

.model-theme .icon-container {
  filter: none;
  transition: all 0.3s ease;
}

.model-theme:hover .icon-container {
  filter:
    drop-shadow(0 0 12px rgba(255, 150, 200, 0.8))
    drop-shadow(0 0 24px rgba(255, 150, 200, 0.6));
  transform: scale(1.1);
  animation: iconBounce 0.6s ease-in-out infinite;
}

/* 统一的上下跳动动画效果 */
@keyframes iconBounce {
  0% { transform: translateY(0px) scale(1.1); }
  50% { transform: translateY(-12px) scale(1.1); }
  75% { transform: translateY(-6px) scale(1.1); }
  90% { transform: translateY(-3px) scale(1.1); }
  100% { transform: translateY(0px) scale(1.1); }
}

/* 底部装饰 */
.bottom-decoration {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  z-index: 5;
  pointer-events: none;
}

.wave-animation {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    0deg,
    rgba(10, 10, 15, 0.8) 0%,
    transparent 100%
  );
  position: relative;
}

.wave-animation::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    #00ffff,
    #ff00ff,
    #ffff00,
    transparent
  );
  animation: waveMove 4s linear infinite;
  filter: drop-shadow(0 0 10px rgba(0, 255, 255, 0.8));
}

@keyframes waveMove {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .function-cards {
    grid-template-columns: repeat(2, 1fr);
    max-width: 800px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 40px 20px 20px;
  }
  
  .main-title {
    font-size: 48px;
  }
  
  .title-subtitle {
    font-size: 16px;
  }
  
  .data-stats {
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 0 20px;
  }
  
  .stat-item {
    max-width: 100%;
    width: 100%;
  }
  
  .function-cards {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 20px 16px 60px;
  }
  
  .card {
    height: 240px;
  }
  
  .card-content {
    padding: 24px;
  }
  
  .card-icon {
    width: 48px;
    height: 48px;
    margin-bottom: 16px;
  }
  
  .icon-container {
    font-size: 48px; /* 移动端图标也相应放大 */
  }
}
</style>