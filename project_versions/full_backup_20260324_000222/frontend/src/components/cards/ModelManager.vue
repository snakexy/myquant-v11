<template>
  <n-card class="model-manager-card" hoverable>
    <template #header>
      <div class="card-header">
        <div class="card-title">
          <span class="card-icon">🤖</span>
          <span>模型管理</span>
        </div>
        <div class="card-actions">
          <n-dropdown trigger="hover" placement="bottom-end">
            <template #trigger>
              <n-button circle size="small" quaternary>
                <template #icon>
                  <n-icon><EllipsisVertical /></n-icon>
                </template>
              </n-button>
            </template>
            <template #dropdown>
              <n-doption @click="createModel">
                <template #icon>
                  <n-icon><Add /></n-icon>
                </template>
                创建模型
              </n-doption>
              <n-doption @click="importModel">
                <template #icon>
                  <n-icon><Download /></n-icon>
                </template>
                导入模型
              </n-doption>
              <n-doption @click="exportModels">
                <template #icon>
                  <n-icon><Save /></n-icon>
                </template>
                导出模型
              </n-doption>
            </template>
          </n-dropdown>
        </div>
      </div>
    </template>
    
    <div class="card-content">
      <!-- 模型列表 -->
      <div class="model-list">
        <div class="list-header">
          <div class="header-title">模型列表</div>
          <div class="header-actions">
            <n-input
              v-model:value="searchKeyword"
              placeholder="搜索模型..."
              size="small"
              style="width: 200px;"
            >
              <template #prefix>
                <n-icon><Search /></n-icon>
              </template>
            </n-input>
            <n-select
              v-model:value="filterType"
              :options="filterOptions"
              size="small"
              style="width: 120px;"
            />
          </div>
        </div>
        
        <div class="models-grid">
          <div
            v-for="model in filteredModels"
            :key="model.id"
            class="model-card"
            @click="selectModel(model)"
            :class="{ active: selectedModel?.id === model.id }"
          >
            <div class="model-header">
              <div class="model-info">
                <div class="model-name">{{ model.name }}</div>
                <div class="model-type">{{ model.type }}</div>
              </div>
              <div class="model-status">
                <n-tag
                  :type="getModelStatusType(model.status)"
                  size="small"
                >
                  {{ model.status }}
                </n-tag>
              </div>
            </div>
            
            <div class="model-metrics">
              <div class="metric-item">
                <span class="metric-label">准确率</span>
                <span class="metric-value">{{ (model.accuracy * 100).toFixed(1) }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">夏普比率</span>
                <span class="metric-value">{{ model.sharpeRatio.toFixed(2) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">最大回撤</span>
                <span class="metric-value">{{ (model.maxDrawdown * 100).toFixed(2) }}%</span>
              </div>
            </div>
            
            <div class="model-details">
              <div class="detail-item">
                <span class="detail-label">创建时间</span>
                <span class="detail-value">{{ formatTime(model.createdAt) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">最后训练</span>
                <span class="detail-value">{{ formatTime(model.lastTrained) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">数据集</span>
                <span class="detail-value">{{ model.dataset }}</span>
              </div>
            </div>
            
            <div class="model-actions">
              <n-button @click="trainModel(model)" size="small" type="primary">
                <template #icon>
                  <n-icon><Play /></n-icon>
                </template>
                训练
              </n-button>
              <n-button @click="explainModel(model)" size="small" type="info">
                <template #icon>
                  <n-icon><Analytics /></n-icon>
                </template>
                解释
              </n-button>
              <n-button @click="deleteModel(model)" size="small" type="error">
                <template #icon>
                  <n-icon><Trash /></n-icon>
                </template>
                删除
              </n-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 模型详情 -->
      <div v-if="selectedModel" class="model-detail-panel">
        <div class="detail-header">
          <h3>{{ selectedModel.name }} 详细信息</h3>
          <n-button @click="selectedModel = null" size="small" quaternary>
            <template #icon>
              <n-icon><Close /></n-icon>
            </template>
          </n-button>
        </div>
        
        <n-tabs v-model:value="detailTab" type="card">
          <n-tab-pane name="training" tab="训练配置">
            <div class="training-config">
              <div class="config-section">
                <h4>滚动训练配置</h4>
                <div class="config-grid">
                  <div class="config-item">
                    <n-label>训练窗口</n-label>
                    <n-input-number
                      v-model:value="trainingConfig.windowSize"
                      :min="10"
                      :max="252"
                      :step="1"
                    />
                  </div>
                  <div class="config-item">
                    <n-label>滚动频率</n-label>
                    <n-select
                      v-model:value="trainingConfig.rollFrequency"
                      :options="rollFrequencyOptions"
                    />
                  </div>
                  <div class="config-item">
                    <n-label>再训练阈值</n-label>
                    <n-input-number
                      v-model:value="trainingConfig.retrainThreshold"
                      :min="0.01"
                      :max="0.5"
                      :step="0.01"
                      :precision="2"
                    />
                  </div>
                </div>
              </div>
              
              <div class="config-section">
                <h4>元学习配置</h4>
                <div class="config-grid">
                  <div class="config-item">
                    <n-checkbox v-model:checked="metaLearningConfig.enabled">
                      启用元学习
                    </n-checkbox>
                  </div>
                  <div class="config-item">
                    <n-label>学习率</n-label>
                    <n-input-number
                      v-model:value="metaLearningConfig.learningRate"
                      :min="0.0001"
                      :max="0.1"
                      :step="0.0001"
                      :precision="4"
                    />
                  </div>
                  <div class="config-item">
                    <n-label>批量大小</n-label>
                    <n-input-number
                      v-model:value="metaLearningConfig.batchSize"
                      :min="16"
                      :max="512"
                      :step="16"
                    />
                  </div>
                  <div class="config-item">
                    <n-label>迭代次数</n-label>
                    <n-input-number
                      v-model:value="metaLearningConfig.epochs"
                      :min="10"
                      :max="1000"
                      :step="10"
                    />
                  </div>
                </div>
              </div>
            </div>
          </n-tab-pane>
          
          <n-tab-pane name="interpretability" tab="模型可解释性">
            <div class="interpretability-panel">
              <div class="interpretation-header">
                <h4>模型可解释性分析</h4>
                <n-button @click="generateInterpretation" size="small" type="primary">
                  <template #icon>
                    <n-icon><Refresh /></n-icon>
                  </template>
                  生成解释
                </n-button>
              </div>
              
              <div class="interpretation-content" v-if="interpretationResult">
                <div class="interpretation-section">
                  <h5>特征重要性</h5>
                  <div class="feature-importance">
                    <div
                      v-for="feature in interpretationResult.featureImportance"
                      :key="feature.name"
                      class="feature-item"
                    >
                      <div class="feature-name">{{ feature.name }}</div>
                      <div class="feature-bar">
                        <div class="bar-fill" :style="{ width: `${feature.importance * 100}%` }"></div>
                      </div>
                      <div class="feature-value">{{ (feature.importance * 100).toFixed(1) }}%</div>
                    </div>
                  </div>
                </div>
                
                <div class="interpretation-section">
                  <h5>决策路径</h5>
                  <div class="decision-path">
                    <div
                      v-for="(step, index) in interpretationResult.decisionPath"
                      :key="index"
                      class="path-step"
                    >
                      <div class="step-number">{{ index + 1 }}</div>
                      <div class="step-content">{{ step.description }}</div>
                      <div class="step-confidence">置信度: {{ (step.confidence * 100).toFixed(1) }}%</div>
                    </div>
                  </div>
                </div>
                
                <div class="interpretation-section">
                  <h5>局部解释</h5>
                  <div class="local-explanations">
                    <div
                      v-for="(explanation, index) in interpretationResult.localExplanations"
                      :key="index"
                      class="explanation-item"
                    >
                      <div class="explanation-title">{{ explanation.title }}</div>
                      <div class="explanation-content">{{ explanation.content }}</div>
                      <div class="explanation-relevance">相关性: {{ (explanation.relevance * 100).toFixed(1) }}%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </n-tab-pane>
        </n-tabs>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NIcon, NButton, NDropdown, NDropdownOption, NTabs, NTabPane, NInput, NSelect, NInputNumber, NCheckbox, NLabel, NSpace, NTag } from 'naive-ui'
import { EllipsisVertical, Add, Download, Search, Play, Analytics, Close, Trash } from '@vicons/ionicons5'
import { formatTime } from '@/utils/format'

interface Model {
  id: string
  name: string
  type: string
  status: 'training' | 'trained' | 'deployed' | 'error'
  accuracy: number
  sharpeRatio: number
  maxDrawdown: number
  createdAt: Date
  lastTrained: Date
  dataset: string
}

interface Props {
  onCreateModel?: () => void
  onImportModel?: () => void
  onExportModels?: () => void
  onTrainModel?: (model: Model) => void
  onExplainModel?: (model: Model) => void
  onDeleteModel?: (model: Model) => void
}

const props = defineProps<Props>()

// 状态管理
const searchKeyword = ref('')
const filterType = ref('all')
const selectedModel = ref<Model | null>(null)
const detailTab = ref('training')
const interpretationResult = ref<any>(null)

// 训练配置
const trainingConfig = ref({
  windowSize: 60,
  rollFrequency: 'daily',
  retrainThreshold: 0.05
})

// 元学习配置
const metaLearningConfig = ref({
  enabled: true,
  learningRate: 0.001,
  batchSize: 32,
  epochs: 100
})

// 模拟模型数据
const models = ref<Model[]>([
  {
    id: '1',
    name: 'LSTM价格预测模型',
    type: '深度学习',
    status: 'trained',
    accuracy: 0.85,
    sharpeRatio: 1.25,
    maxDrawdown: 0.12,
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    lastTrained: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    dataset: 'A股日线数据'
  },
  {
    id: '2',
    name: 'XGBoost分类模型',
    type: '机器学习',
    status: 'deployed',
    accuracy: 0.78,
    sharpeRatio: 1.15,
    maxDrawdown: 0.18,
    createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    lastTrained: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    dataset: 'A股分钟数据'
  },
  {
    id: '3',
    name: 'Transformer注意力模型',
    type: '深度学习',
    status: 'training',
    accuracy: 0.92,
    sharpeRatio: 1.45,
    maxDrawdown: 0.08,
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    lastTrained: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    dataset: 'A股tick数据'
  }
])

// 配置选项
const filterOptions = [
  { label: '全部', value: 'all' },
  { label: '深度学习', value: 'deep_learning' },
  { label: '机器学习', value: 'machine_learning' },
  { label: '训练中', value: 'training' },
  { label: '已部署', value: 'deployed' }
]

const rollFrequencyOptions = [
  { label: '每日', value: 'daily' },
  { label: '每周', value: 'weekly' },
  { label: '每月', value: 'monthly' }
]

// 计算属性
const filteredModels = computed(() => {
  let filtered = models.value
  
  // 按类型筛选
  if (filterType.value !== 'all') {
    filtered = filtered.filter(model => {
      if (filterType.value === 'deep_learning') {
        return model.type === '深度学习'
      } else if (filterType.value === 'machine_learning') {
        return model.type === '机器学习'
      } else if (filterType.value === 'training') {
        return model.status === 'training'
      } else if (filterType.value === 'deployed') {
        return model.status === 'deployed'
      }
      return true
    })
  }
  
  // 按关键词搜索
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(model => 
      model.name.toLowerCase().includes(keyword) ||
      model.type.toLowerCase().includes(keyword)
    )
  }
  
  return filtered
})

// 方法
const getModelStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    training: 'warning',
    trained: 'info',
    deployed: 'success',
    error: 'error'
  }
  return typeMap[status] || 'default'
}

const createModel = () => {
  if (props.onCreateModel) {
    props.onCreateModel()
  }
}

const importModel = () => {
  if (props.onImportModel) {
    props.onImportModel()
  }
}

const exportModels = () => {
  if (props.onExportModels) {
    props.onExportModels()
  }
}

const selectModel = (model: Model) => {
  selectedModel.value = model
}

const trainModel = (model: Model) => {
  if (props.onTrainModel) {
    props.onTrainModel(model)
  }
}

const explainModel = (model: Model) => {
  if (props.onExplainModel) {
    props.onExplainModel(model)
  }
}

const deleteModel = (model: Model) => {
  if (props.onDeleteModel) {
    props.onDeleteModel(model)
  }
}

const generateInterpretation = () => {
  if (!selectedModel.value) return
  
  // 模拟生成解释结果
  interpretationResult.value = {
    featureImportance: [
      { name: '收盘价', importance: 0.35 },
      { name: '成交量', importance: 0.28 },
      { name: 'RSI', importance: 0.18 },
      { name: 'MACD', importance: 0.12 },
      { name: '布林带', importance: 0.07 }
    ],
    decisionPath: [
      { description: '数据预处理和特征工程', confidence: 0.95 },
      { description: 'LSTM层处理序列数据', confidence: 0.88 },
      { description: '注意力机制识别关键模式', confidence: 0.82 },
      { description: '全连接层生成预测', confidence: 0.76 }
    ],
    localExplanations: [
      {
        title: '价格突破',
        content: '当价格突破20日均线且成交量放大时，模型预测上涨概率增加',
        relevance: 0.85
      },
      {
        title: '超买反弹',
        content: 'RSI指标低于30时，模型预测反弹概率较高',
        relevance: 0.72
      },
      {
        title: '趋势延续',
        content: '短期均线向上穿越长期均线时，模型预测上涨趋势延续',
        relevance: 0.68
      }
    ]
  }
}

onMounted(() => {
  // 组件初始化
})
</script>

<style lang="scss" scoped>
.model-manager-card {
  @include card-style;
  height: 600px;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .card-header {
    @include card-header;
    flex-shrink: 0;

    .card-title {
      display: flex;
      align-items: center;
      gap: var(--spacing-2);

      .card-icon {
        font-size: var(--font-size-lg);
      }
    }

    .card-actions {
      margin-left: auto;
    }
  }

  .card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: var(--spacing-4);
    gap: var(--spacing-4);

    .model-list {
      margin-bottom: var(--spacing-4);

      .list-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-3);

        .header-title {
          font-weight: 600;
          color: var(--text-primary);
        }

        .header-actions {
          display: flex;
          gap: var(--spacing-2);
        }
      }

      .models-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--spacing-3);
        max-height: 300px;
        overflow-y: auto;

        .model-card {
          background: rgba(15, 23, 42, 0.4);
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: var(--border-radius-medium);
          padding: var(--spacing-3);
          cursor: pointer;
          transition: all 0.2s ease;

          &:hover {
            background: rgba(15, 23, 42, 0.6);
            transform: translateY(-2px);
          }

          &.active {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(var(--primary-color), 0.3);
          }

          .model-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--spacing-2);

            .model-info {
              .model-name {
                font-weight: 600;
                color: var(--text-primary);
              }

              .model-type {
                font-size: var(--font-size-xs);
                color: var(--text-secondary);
                margin-left: var(--spacing-1);
              }
            }
          }

          .model-metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--spacing-2);
            margin-bottom: var(--spacing-2);

            .metric-item {
              text-align: center;

              .metric-label {
                font-size: var(--font-size-xs);
                color: var(--text-secondary);
                margin-bottom: var(--spacing-1);
              }

              .metric-value {
                font-weight: 600;
                color: var(--text-primary);
              }
            }
          }

          .model-details {
            .detail-item {
              display: flex;
              justify-content: space-between;
              margin-bottom: var(--spacing-1);

              .detail-label {
                font-size: var(--font-size-xs);
                color: var(--text-secondary);
              }

              .detail-value {
                font-weight: 500;
                color: var(--text-primary);
              }
            }
          }

          .model-actions {
            display: flex;
            gap: var(--spacing-1);
            margin-top: var(--spacing-2);
          }
        }
      }
    }

    .model-detail-panel {
      flex: 1;
      padding: var(--spacing-4);
      background: rgba(15, 23, 42, 0.4);
      border-radius: var(--border-radius-medium);
      border: 1px solid rgba(148, 163, 184, 0.1);

      .detail-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-3);

        h3 {
          margin: 0;
          color: var(--text-primary);
        }
      }

      .training-config {
        .config-section {
          margin-bottom: var(--spacing-4);

          h4 {
            margin-bottom: var(--spacing-2);
            color: var(--text-primary);
          }

          .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--spacing-3);

            .config-item {
              display: flex;
              flex-direction: column;
              gap: var(--spacing-1);

              .n-label {
                margin-bottom: var(--spacing-1);
              }
            }
          }
        }
      }

      .interpretability-panel {
        .interpretation-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-3);

          h4 {
            margin: 0;
            color: var(--text-primary);
          }
        }

        .interpretation-content {
          .interpretation-section {
            margin-bottom: var(--spacing-4);

            h5 {
              margin-bottom: var(--spacing-2);
              color: var(--text-primary);
            }

            .feature-importance {
              .feature-item {
                display: flex;
                align-items: center;
                margin-bottom: var(--spacing-2);
                gap: var(--spacing-2);

                .feature-name {
                  min-width: 100px;
                  font-size: var(--font-size-sm);
                  color: var(--text-secondary);
                }

                .feature-bar {
                  flex: 1;
                  height: 20px;
                  background: rgba(148, 163, 184, 0.1);
                  border-radius: var(--border-radius-sm)all;
                  overflow: hidden;

                  .bar-fill {
                    height: 100%;
                    background: linear-gradient(90deg, var(--primary-color), var(--info-color));
                    transition: width 0.5s ease;
                  }
                }

                .feature-value {
                  min-width: 50px;
                  font-weight: 600;
                  color: var(--text-primary);
                  text-align: right;
                }
              }
            }

            .decision-path {
              .path-step {
                display: flex;
                align-items: center;
                gap: var(--spacing-2);
                padding: var(--spacing-2);
                background: rgba(0, 0, 0, 0.1);
                border-radius: var(--border-radius-sm)all;
                margin-bottom: var(--spacing-2);

                .step-number {
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  width: 24px;
                  height: 24px;
                  background: var(--primary-color);
                  color: white;
                  border-radius: 50%;
                  font-weight: 600;
                  font-size: var(--font-size-xs);
                }

                .step-content {
                  flex: 1;
                  font-size: var(--font-size-sm);
                  color: var(--text-primary);
                }

                .step-confidence {
                  font-size: var(--font-size-xs);
                  color: var(--text-secondary);
                }
              }
            }

            .local-explanations {
              .explanation-item {
                padding: var(--spacing-2);
                background: rgba(0, 0, 0, 0.1);
                border-radius: var(--border-radius-sm)all;
                margin-bottom: var(--spacing-2);

                .explanation-title {
                  font-weight: 600;
                  color: var(--text-primary);
                  margin-bottom: var(--spacing-1);
                }

                .explanation-content {
                  font-size: var(--font-size-sm);
                  color: var(--text-secondary);
                  margin-bottom: var(--spacing-1);
                  line-height: 1.4;
                }

                .explanation-relevance {
                  font-size: var(--font-size-xs);
                  color: var(--text-secondary);
                  text-align: right;
                }
              }
            }
          }
        }
      }
    }
  }
}
</style>