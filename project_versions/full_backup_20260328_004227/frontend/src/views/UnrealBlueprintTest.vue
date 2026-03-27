<template>
  <div class="unreal-test-container">
    <div class="test-header">
      <h1>Unreal蓝图系统测试页面</h1>
      <p>这是一个简化的测试版本，用于验证基本功能</p>
    </div>
    
    <div class="test-content">
      <div class="test-node" style="left: 100px; top: 100px;">
        <div class="node-header">
          <i class="fas fa-database"></i>
          <span>数据源</span>
        </div>
        <div class="node-ports">
          <div class="port output-port">出</div>
        </div>
      </div>
      
      <div class="test-node" style="left: 400px; top: 100px;">
        <div class="node-header">
          <i class="fas fa-cogs"></i>
          <span>处理器</span>
        </div>
        <div class="node-ports">
          <div class="port input-port">入</div>
          <div class="port output-port">出</div>
        </div>
      </div>
      
      <div class="test-node" style="left: 700px; top: 100px;">
        <div class="node-header">
          <i class="fas fa-brain"></i>
          <span>AI模型</span>
        </div>
        <div class="node-ports">
          <div class="port input-port">入</div>
          <div class="port output-port">出</div>
        </div>
      </div>
      
      <!-- SVG连接线 -->
      <svg class="connections-svg">
        <defs>
          <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#00ff88;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#0088ff;stop-opacity:0.8" />
          </linearGradient>
        </defs>
        
        <path d="M 200 130 Q 300 130 400 130" stroke="url(#grad1)" stroke-width="3" fill="none"/>
        <path d="M 500 130 Q 600 130 700 130" stroke="url(#grad1)" stroke-width="3" fill="none"/>
        
        <!-- 数据流动画粒子 -->
        <circle r="4" fill="#00ff88">
          <animateMotion dur="3s" repeatCount="indefinite">
            <mpath href="#path1"/>
          </animateMotion>
        </circle>
      </svg>
    </div>
    
    <div class="test-controls">
      <button @click="addNode">添加节点</button>
      <button @click="clearNodes">清空</button>
      <button @click="toggleAnimation">切换动画</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const animationEnabled = ref(true)

const addNode = () => {
  console.log('添加节点')
}

const clearNodes = () => {
  console.log('清空节点')
}

const toggleAnimation = () => {
  animationEnabled.value = !animationEnabled.value
  console.log('动画状态:', animationEnabled.value)
}
</script>

<style scoped>
.unreal-test-container {
  width: 100%;
  height: 100vh;
  background: #0a0a0f;
  color: #f8fafc;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow: hidden;
  position: relative;
}

.test-header {
  padding: 20px;
  text-align: center;
  background: rgba(26, 26, 46, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.test-header h1 {
  margin: 0 0 10px 0;
  color: #2962ff;
  font-size: 24px;
}

.test-header p {
  margin: 0;
  color: #cbd5e1;
  font-size: 14px;
}

.test-content {
  position: relative;
  width: 100%;
  height: calc(100vh - 200px);
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.test-node {
  position: absolute;
  width: 200px;
  min-height: 80px;
  background: rgba(26, 26, 46, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 15px;
  backdrop-filter: blur(10px);
  cursor: move;
  transition: all 0.3s ease;
}

.test-node:hover {
  border-color: #7c3aed;
  box-shadow: 0 8px 32px rgba(124, 58, 237, 0.3);
  transform: scale(1.02);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: #f8fafc;
  font-weight: 600;
}

.node-header i {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(124, 58, 237, 0.1);
  border-radius: 6px;
  color: #7c3aed;
}

.node-ports {
  display: flex;
  justify-content: space-between;
  position: relative;
}

.port {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.input-port {
  background: #0088ff;
  margin-left: -8px;
}

.output-port {
  background: #00ff88;
  margin-right: -8px;
}

.port:hover {
  transform: scale(1.2);
  box-shadow: 0 0 12px rgba(0, 255, 136, 0.6);
}

.connections-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.test-controls {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  background: rgba(26, 26, 46, 0.9);
  padding: 15px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.test-controls button {
  padding: 10px 20px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.test-controls button:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>