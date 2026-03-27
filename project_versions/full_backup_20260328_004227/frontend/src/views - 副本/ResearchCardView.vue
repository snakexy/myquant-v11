<template>
  <div class="card-view">
    <div class="workspace-grid">
      <!-- 数据驱动研究卡片 -->
      <div class="workspace-card">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-database"></i>
          </div>
          <h3>数据驱动研究</h3>
          <span class="card-status active">运行中</span>
        </div>
        <div class="card-content">
          <div class="metrics">
            <div class="metric">
              <span class="label">数据源</span>
              <span class="value">12</span>
            </div>
            <div class="metric">
              <span class="label">数据量</span>
              <span class="value">2.3TB</span>
            </div>
          </div>
          <p class="description">
            基于历史数据进行模式识别和策略开发
          </p>
        </div>
        <div class="card-footer">
          <button class="btn-primary">
            <i class="fas fa-chart-line"></i>
            查看详情
          </button>
        </div>
      </div>

      <!-- 模型训练卡片（可展开） -->
      <div
        class="workspace-card model-training-card"
        :class="{ 'expanded': modelCardStates['model-training'].showDetails }"
      >
        <div class="card-header" @click="toggleCardDetails('model-training')">
          <div class="card-icon">
            <i class="fas fa-brain"></i>
          </div>
          <h3>模型训练</h3>
          <span class="card-status training">训练中</span>
          <i class="fas fa-chevron-down expand-icon" :class="{ 'rotated': modelCardStates['model-training'].showDetails }"></i>
        </div>
        <div class="card-content">
          <div class="metrics">
            <div class="metric">
              <span class="label">准确率</span>
              <span class="value">92.3%</span>
            </div>
            <div class="metric">
              <span class="label">迭代次数</span>
              <span class="value">1,245</span>
            </div>
          </div>
          <p class="description">
            使用深度学习算法预测市场走势
          </p>
        </div>

        <!-- 可展开的模型详情 -->
        <transition name="model-details">
          <div class="model-details" v-show="modelCardStates['model-training'].showDetails">
            <div class="model-section">
              <h4>选择模型类型</h4>
              <div class="model-categories">
                <div
                  v-for="category in modelCategories"
                  :key="category.id"
                  class="category-item"
                  :class="{ active: selectedModels[category.id] }"
                  @click="toggleModel(category.id)"
                >
                  <i :class="category.icon"></i>
                  <span>{{ category.name }}</span>
                  <div class="model-count">{{ category.count }}</div>
                </div>
              </div>
            </div>

            <div class="model-section">
              <h4>预设模型</h4>
              <div class="preset-models">
                <div
                  v-for="model in presetModels"
                  :key="model.id"
                  class="preset-model"
                  :class="{ selected: selectedPresetModel === model.id }"
                  @click="selectPresetModel(model.id)"
                >
                  <div class="model-info">
                    <h5>{{ model.name }}</h5>
                    <p>{{ model.description }}</p>
                    <div class="model-stats">
                      <span class="stat">
                        <i class="fas fa-chart-line"></i>
                        准确率: {{ model.accuracy }}%
                      </span>
                      <span class="stat">
                        <i class="fas fa-clock"></i>
                        训练时间: {{ model.trainingTime }}
                      </span>
                    </div>
                  </div>
                  <div class="model-action">
                    <button class="btn-select" :class="{ selected: selectedPresetModel === model.id }">
                      {{ selectedPresetModel === model.id ? '已选择' : '选择' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="model-actions">
              <button class="btn-secondary" @click.stop="resetModelSelection">
                <i class="fas fa-undo"></i>
                重置
              </button>
              <button class="btn-primary" @click.stop="startTraining">
                <i class="fas fa-play"></i>
                开始训练
              </button>
            </div>
          </div>
        </transition>

        <div class="card-footer">
          <button class="btn-primary">
            <i class="fas fa-cog"></i>
            配置
          </button>
        </div>
      </div>

      <!-- AI策略生成卡片 -->
      <div class="workspace-card">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-robot"></i>
          </div>
          <h3>AI策略生成</h3>
          <span class="card-status">待启动</span>
        </div>
        <div class="card-content">
          <div class="metrics">
            <div class="metric">
              <span class="label">生成策略</span>
              <span class="value">48</span>
            </div>
            <div class="metric">
              <span class="label">成功率</span>
              <span class="value">78.5%</span>
            </div>
          </div>
          <p class="description">
            利用大语言模型生成创新交易策略
          </p>
        </div>
        <div class="card-footer">
          <button class="btn-primary">
            <i class="fas fa-magic"></i>
            开始生成
          </button>
        </div>
      </div>

      <!-- 回测分析卡片 -->
      <div class="workspace-card">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-history"></i>
          </div>
          <h3>回测分析</h3>
          <span class="card-status completed">已完成</span>
        </div>
        <div class="card-content">
          <div class="metrics">
            <div class="metric">
              <span class="label">年化收益</span>
              <span class="value positive">+23.5%</span>
            </div>
            <div class="metric">
              <span class="label">夏普比率</span>
              <span class="value">2.34</span>
            </div>
          </div>
          <p class="description">
            历史数据回测验证策略有效性
          </p>
        </div>
        <div class="card-footer">
          <button class="btn-primary">
            <i class="fas fa-chart-bar"></i>
            查看报告
          </button>
        </div>
      </div>

      <!-- 风险评估卡片 -->
      <div class="workspace-card">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-shield-alt"></i>
          </div>
          <h3>风险评估</h3>
          <span class="card-status warning">需关注</span>
        </div>
        <div class="card-content">
          <div class="metrics">
            <div class="metric">
              <span class="label">风险等级</span>
              <span class="value warning">中等</span>
            </div>
            <div class="metric">
              <span class="label">VaR</span>
              <span class="value negative">-5.2%</span>
            </div>
          </div>
          <p class="description">
            多维度风险评估和管理建议
          </p>
        </div>
        <div class="card-footer">
          <button class="btn-primary">
            <i class="fas fa-exclamation-triangle"></i>
            查看详情
          </button>
        </div>
      </div>

      <!-- 性能优化卡片 -->
      <div class="workspace-card">
        <div class="card-header">
          <div class="card-icon">
            <i class="fas fa-tachometer-alt"></i>
          </div>
          <h3>性能优化</h3>
          <span class="card-status">优化中</span>
        </div>
        <div class="card-content">
          <div class="metrics">
            <div class="metric">
              <span class="label">执行速度</span>
              <span class="value">+45%</span>
            </div>
            <div class="metric">
              <span class="label">资源占用</span>
              <span class="value">-28%</span>
            </div>
          </div>
          <p class="description">
            算法优化提升策略执行效率
          </p>
        </div>
        <div class="card-footer">
          <button class="btn-primary">
            <i class="fas fa-rocket"></i>
            优化设置
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// 模型卡片状态
const modelCardStates = reactive({
  'model-training': {
    showDetails: false
  }
})

// 选中的模型
const selectedModels = ref<Record<string, boolean>>({})
const selectedPresetModel = ref<string>('')

// 模型分类
const modelCategories = ref([
  { id: 'lstm', name: 'LSTM', icon: 'fas fa-network-wired', count: 12 },
  { id: 'transformer', name: 'Transformer', icon: 'fas fa-project-diagram', count: 8 },
  { id: 'cnn', name: 'CNN', icon: 'fas fa-cube', count: 15 },
  { id: 'rl', name: '强化学习', icon: 'fas fa-gamepad', count: 6 },
  { id: 'ensemble', name: '集成学习', icon: 'fas fa-layer-group', count: 10 }
])

// 预设模型
const presetModels = ref([
  {
    id: 'lstm-v1',
    name: 'LSTM预测模型 v1.0',
    description: '基于长短期记忆网络的价格预测模型，适用于短期趋势预测',
    accuracy: 92.3,
    trainingTime: '2小时'
  },
  {
    id: 'transformer-v2',
    name: 'Transformer注意力模型 v2.0',
    description: '使用自注意力机制捕捉市场长期依赖关系',
    accuracy: 89.7,
    trainingTime: '3小时'
  },
  {
    id: 'cnn-pattern',
    name: 'CNN模式识别模型',
    description: '卷积神经网络识别K线图形态，发现技术模式',
    accuracy: 87.5,
    trainingTime: '1.5小时'
  },
  {
    id: 'rl-trader',
    name: '强化学习交易智能体',
    description: '通过深度Q网络学习最优交易策略',
    accuracy: 85.2,
    trainingTime: '4小时'
  }
])

// 方法
const toggleCardDetails = (cardId: string) => {
  modelCardStates[cardId].showDetails = !modelCardStates[cardId].showDetails
}

const toggleModel = (categoryId: string) => {
  selectedModels.value[categoryId] = !selectedModels.value[categoryId]
}

const selectPresetModel = (modelId: string) => {
  selectedPresetModel.value = modelId
}

const resetModelSelection = () => {
  selectedModels.value = {}
  selectedPresetModel.value = ''
}

const startTraining = () => {
  console.log('开始训练模型', {
    categories: Object.keys(selectedModels.value).filter(key => selectedModels.value[key]),
    preset: selectedPresetModel.value
  })
}
</script>

<style scoped>
.card-view {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px;
}

.workspace-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  align-items: start;
}

.workspace-card {
  background-color: var(--bg-white);
  border-radius: var(--border-radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  height: fit-content;
  min-height: 240px;
  display: flex;
  flex-direction: column;
}

.workspace-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.workspace-card.model-training-card {
  cursor: pointer;
}

.workspace-card.model-training-card.expanded {
  grid-column: span 2;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  position: relative;
}

.card-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  font-size: 18px;
  color: var(--primary-color);
}

.card-header h3 {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.card-status {
  padding: 4px 8px;
  border-radius: var(--border-radius-sm);
  font-size: 12px;
  font-weight: 500;
}

.card-status.active {
  background-color: var(--success-light);
  color: var(--success-color);
}

.card-status.training {
  background-color: var(--warning-light);
  color: var(--warning-color);
}

.card-status.completed {
  background-color: var(--info-light);
  color: var(--info-color);
}

.card-status.warning {
  background-color: var(--danger-light);
  color: var(--danger-color);
}

.expand-icon {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  transition: transform 0.3s ease;
  color: var(--text-regular);
}

.expand-icon.rotated {
  transform: translateY(-50%) rotate(180deg);
}

.card-content {
  flex: 1;
  margin-bottom: 16px;
}

.metrics {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric .label {
  font-size: 12px;
  color: var(--text-regular);
}

.metric .value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.metric .value.positive {
  color: var(--market-rise);
}

.metric .value.negative {
  color: var(--market-fall);
}

.metric .value.warning {
  color: var(--warning-color);
}

.description {
  font-size: 14px;
  color: var(--text-regular);
  margin: 0;
  line-height: 1.5;
}

.card-footer {
  margin-top: auto;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.model-details {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.model-section {
  margin-bottom: 24px;
}

.model-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.model-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-item:hover {
  border-color: var(--primary-color);
  background-color: var(--bg-hover);
}

.category-item.active {
  border-color: var(--primary-color);
  background-color: rgba(var(--primary-rgb), 0.05);
}

.category-item i {
  font-size: 20px;
  color: var(--primary-color);
}

.category-item span {
  font-size: 12px;
  color: var(--text-primary);
  font-weight: 500;
}

.model-count {
  font-size: 11px;
  color: var(--text-regular);
}

.preset-models {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preset-model {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.3s ease;
}

.preset-model:hover {
  border-color: var(--primary-color);
  background-color: var(--bg-hover);
}

.preset-model.selected {
  border-color: var(--primary-color);
  background-color: rgba(var(--primary-rgb), 0.05);
}

.model-info h5 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.model-info p {
  font-size: 12px;
  color: var(--text-regular);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.model-stats {
  display: flex;
  gap: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-regular);
}

.btn-select {
  padding: 6px 12px;
  background-color: var(--bg-secondary);
  color: var(--text-regular);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-select.selected {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.model-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: var(--bg-secondary);
  color: var(--text-regular);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background-color: var(--bg-hover);
}

/* 动画效果 */
.model-details-enter-active,
.model-details-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.model-details-enter-from,
.model-details-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-10px);
}

.model-details-enter-to,
.model-details-leave-from {
  opacity: 1;
  max-height: 800px;
  transform: translateY(0);
}
</style>