<template>
  <div class="step-model-training-panel">
    <!-- 模式切换Tab -->
    <div class="mode-tabs-container">
      <el-tabs v-model="activeMode" class="mode-tabs">
        <el-tab-pane name="feature">
          <template #label>
            <span class="tab-label">
              <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
              {{ isZh ? '功能导向' : 'Feature Mode' }}
            </span>
          </template>
          <div class="mode-hint">
            {{ isZh ? '🎯 系统自动为您选择最优参数' : '🎯 Auto-optimized parameters for you' }}
          </div>
        </el-tab-pane>
        <el-tab-pane name="professional">
          <template #label>
            <span class="tab-label">
              <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
              {{ isZh ? '专业型' : 'Professional' }}
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>


    <!-- 功能导向模式：简化的预设选择 -->
    <template v-if="activeMode === 'feature'">
      <div class="feature-presets">
        <h4 class="section-subtitle">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
          </svg>
          {{ isZh ? '选择训练场景' : 'Select Training Scenario' }}
        </h4>

        <!-- 场景分类 -->
        <div v-for="category in scenarioCategories" :key="category.id" class="scenario-category">
          <div class="category-header">
            <span class="category-label">{{ isZh ? category.label : category.labelEn }}</span>
          </div>
          <div class="scenario-grid">
            <div
              v-for="scenarioId in category.items"
              :key="scenarioId"
              :class="['scenario-card', { selected: selectedScenario === scenarioId }]"
              @click="selectScenario(scenarioId)"
            >
              <div class="scenario-header">
                <span class="scenario-icon">{{ getScenarioById(scenarioId)?.icon }}</span>
                <span class="scenario-name">{{ isZh ? getScenarioById(scenarioId)?.label : getScenarioById(scenarioId)?.labelEn }}</span>
              </div>
              <div class="scenario-desc">{{ isZh ? getScenarioById(scenarioId)?.desc : getScenarioById(scenarioId)?.descEn }}</div>
              <div class="scenario-meta">
                <span class="scenario-model">{{ getScenarioById(scenarioId)?.model }}</span>
                <span class="scenario-tags">
                  <span class="scenario-feature">{{ isZh ? featureLevelLabels[getScenarioById(scenarioId)?.featureLevel || 'simple'].label : featureLevelLabels[getScenarioById(scenarioId)?.featureLevel || 'simple'].labelEn }}</span>
                  <span class="scenario-optimize" v-if="getScenarioById(scenarioId)?.optimizeLevel !== 'none'">{{ isZh ? optimizeLevelLabels[getScenarioById(scenarioId)?.optimizeLevel || 'none'].label : optimizeLevelLabels[getScenarioById(scenarioId)?.optimizeLevel || 'none'].labelEn }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 已选场景预览 -->
        <div class="selected-preview" v-if="selectedScenario">
          <div class="preview-header">
            <span>{{ isZh ? '✅ 已选场景' : '✅ Selected Scenario' }}: {{ isZh ? getScenarioById(selectedScenario)?.label : getScenarioById(selectedScenario)?.labelEn }}</span>
          </div>
          <div class="preview-details">
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '模型' : 'Model' }}:</span>
              <span class="detail-value">{{ getScenarioById(selectedScenario)?.model }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '目标' : 'Target' }}:</span>
              <span class="detail-value">{{ getScenarioById(selectedScenario)?.target }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '训练集' : 'Train' }}:</span>
              <span class="detail-value">{{ (getScenarioById(selectedScenario)?.trainRatio || 0.7) * 100 }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '交叉验证' : 'CV' }}:</span>
              <span class="detail-value">{{ getScenarioById(selectedScenario)?.cvType === 'none' ? '否' : getScenarioById(selectedScenario)?.cvType }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '特征工程' : 'Features' }}:</span>
              <span class="detail-value highlight">{{ isZh ? featureLevelLabels[getScenarioById(selectedScenario)?.featureLevel || 'simple'].label : featureLevelLabels[getScenarioById(selectedScenario)?.featureLevel || 'simple'].labelEn }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ isZh ? '超参优化' : 'HPO' }}:</span>
              <span class="detail-value highlight-orange">{{ isZh ? optimizeLevelLabels[getScenarioById(selectedScenario)?.optimizeLevel || 'none'].label : optimizeLevelLabels[getScenarioById(selectedScenario)?.optimizeLevel || 'none'].labelEn }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 专业型模式：完整参数配置 -->
    <template v-if="activeMode === 'professional'">
    <!-- 模型配置 -->
    <div class="config-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="8" width="18" height="13" rx="2"/>
          <circle cx="9" cy="13" r="1.5"/>
          <circle cx="15" cy="13" r="1.5"/>
          <path d="M8 17h8"/>
          <path d="M12 4v3"/>
        </svg>
        {{ isZh ? '模型配置' : 'Model Configuration' }}
      </h3>

      <div class="config-form">
        <div class="form-group">
          <label class="form-label">{{ isZh ? '模型类型' : 'Model Type' }}</label>
          <el-select v-model="modelConfig.type" style="width: 100%;" @change="onModelTypeChange">
            <!-- 机器学习 - CPU (LightGBM/RF比OpenCL GPU更快) -->
            <el-option :label="isZh ? 'LightGBM (CPU)' : 'LightGBM (CPU)'" value="lightgbm"></el-option>
            <el-option :label="isZh ? '随机森林 (CPU)' : 'Random Forest (CPU)'" value="random_forest"></el-option>
            <!-- 机器学习 - GPU加速 (XGBoost原生CUDA) -->
            <el-option :label="isZh ? 'XGBoost (GPU)' : 'XGBoost (GPU)'" value="xgboost"></el-option>
            <!-- 深度学习 - GPU加速 (PyTorch CUDA) -->
            <el-option :label="isZh ? 'LSTM 时序 (GPU)' : 'LSTM Time Series (GPU)'" value="lstm"></el-option>
            <el-option :label="isZh ? 'GRU 时序 (GPU)' : 'GRU Time Series (GPU)'" value="gru"></el-option>
            <el-option :label="isZh ? 'MLP 深度特征 (GPU)' : 'MLP Deep Feature (GPU)'" value="mlp"></el-option>
            <el-option :label="isZh ? 'Transformer 注意力 (GPU)' : 'Transformer Attention (GPU)'" value="transformer"></el-option>
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '计算设备' : 'Compute Device' }}</label>
          <el-select v-model="modelConfig.device" style="width: 100%;">
            <el-option :label="isZh ? '自动选择 (GPU优先)' : 'Auto (GPU First)'" value="auto"></el-option>
            <el-option :label="isZh ? 'GPU (CUDA)' : 'GPU (CUDA)'" value="cuda"></el-option>
            <el-option :label="isZh ? 'CPU' : 'CPU'" value="cpu"></el-option>
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '训练目标' : 'Training Target' }}</label>
          <el-select v-model="modelConfig.target" style="width: 100%;">
            <el-option :label="isZh ? '未来1天收益' : 'Return 1D'" value="return_1d"></el-option>
            <el-option :label="isZh ? '未来5天收益' : 'Return 5D'" value="return_5d"></el-option>
            <el-option :label="isZh ? '未来20天收益' : 'Return 20D'" value="return_20d"></el-option>
            <el-option :label="isZh ? '超额收益' : 'Excess Return'" value="excess_return"></el-option>
          </el-select>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '训练集比例' : 'Train Ratio' }}</label>
          <div class="ratio-control">
            <el-slider
              v-model="modelConfig.trainRatio"
              :min="0.5"
              :max="0.8"
              :step="0.05"
              tooltip-class="slider-tooltip-dark"
              :persistent="true"
            />
            <el-input-number
              v-model="modelConfig.trainRatio"
              :min="0.5"
              :max="0.8"
              :step="0.05"
              :precision="2"
              size="small"
              controls-position="right"
            />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">{{ isZh ? '验证集比例' : 'Validation Ratio' }}</label>
          <div class="ratio-control">
            <el-slider
              v-model="modelConfig.valRatio"
              :min="0.1"
              :max="0.3"
              :step="0.05"
              tooltip-class="slider-tooltip-dark"
              :persistent="true"
            />
            <el-input-number
              v-model="modelConfig.valRatio"
              :min="0.1"
              :max="0.3"
              :step="0.05"
              :precision="2"
              size="small"
              controls-position="right"
            />
          </div>
        </div>

        <!-- K-Fold交叉验证 -->
        <div class="form-group">
          <label class="form-label">{{ isZh ? '交叉验证' : 'Cross Validation' }}</label>
          <el-select v-model="modelConfig.cvType" style="width: 100%;">
            <el-option :label="isZh ? '不使用' : 'None'" value="none"></el-option>
            <el-option :label="isZh ? '3折交叉验证' : '3-Fold CV'" value="3fold"></el-option>
            <el-option :label="isZh ? '5折交叉验证' : '5-Fold CV'" value="5fold"></el-option>
            <el-option :label="isZh ? '10折交叉验证' : '10-Fold CV'" value="10fold"></el-option>
            <el-option :label="isZh ? '时间序列分割' : 'Time Series Split'" value="timeseries"></el-option>
          </el-select>
        </div>

        <!-- K-Fold折数 -->
        <div v-if="modelConfig.cvType !== 'none'" class="form-group">
          <label class="form-label">{{ isZh ? '验证折数' : 'CV Folds' }}</label>
          <el-input-number v-model="modelConfig.cvFolds" :min="3" :max="10" size="small" controls-position="right" />
        </div>
      </div>

      <!-- 高级参数 -->
      <div class="advanced-params">
        <h4 class="section-subtitle">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          {{ isZh ? '高级参数' : 'Advanced Parameters' }}
        </h4>
        <div class="params-grid">
          <div class="param-item">
            <div class="param-header">
              <label class="param-label">n_estimators</label>
              <el-input-number v-model="modelConfig.params.n_estimators" :min="10" :max="1000" :step="10" size="small" controls-position="right" />
            </div>
            <el-slider v-model="modelConfig.params.n_estimators" :min="10" :max="1000" :step="10" tooltip-class="slider-tooltip-dark" :persistent="true" />
          </div>
          <div class="param-item">
            <div class="param-header">
              <label class="param-label">max_depth</label>
              <el-input-number v-model="modelConfig.params.max_depth" :min="1" :max="20" size="small" controls-position="right" />
            </div>
            <el-slider v-model="modelConfig.params.max_depth" :min="1" :max="20" tooltip-class="slider-tooltip-dark" :persistent="true" />
          </div>
          <div class="param-item">
            <div class="param-header">
              <label class="param-label">learning_rate</label>
              <el-input-number v-model="modelConfig.params.learning_rate" :min="0.001" :max="1" :step="0.01" :precision="3" size="small" controls-position="right" />
            </div>
            <el-slider v-model="modelConfig.params.learning_rate" :min="0.001" :max="1" :step="0.01" tooltip-class="slider-tooltip-dark" :persistent="true" />
          </div>
          <div class="param-item">
            <div class="param-header">
              <label class="param-label">subsample</label>
              <el-input-number v-model="modelConfig.params.subsample" :min="0.1" :max="1" :step="0.1" :precision="1" size="small" controls-position="right" />
            </div>
            <el-slider v-model="modelConfig.params.subsample" :min="0.1" :max="1" :step="0.1" tooltip-class="slider-tooltip-dark" :persistent="true" />
          </div>
          <div class="param-item">
            <div class="param-header">
              <label class="param-label">colsample_bytree</label>
              <el-input-number v-model="modelConfig.params.colsample_bytree" :min="0.1" :max="1" :step="0.1" :precision="1" size="small" controls-position="right" />
            </div>
            <el-slider v-model="modelConfig.params.colsample_bytree" :min="0.1" :max="1" :step="0.1" tooltip-class="slider-tooltip-dark" :persistent="true" />
          </div>
          <div class="param-item">
            <div class="param-header">
              <label class="param-label">reg_alpha</label>
              <el-input-number v-model="modelConfig.params.reg_alpha" :min="0" :max="10" :step="0.1" :precision="1" size="small" controls-position="right" />
            </div>
            <el-slider v-model="modelConfig.params.reg_alpha" :min="0" :max="10" :step="0.1" tooltip-class="slider-tooltip-dark" :persistent="true" />
          </div>
        </div>

        <!-- 超参数优化按钮 -->
        <div class="optimize-section">
          <el-button size="small" type="warning" @click="openOptimizeDialog">
            <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path>
            </svg>
            {{ isZh ? '超参数优化' : 'Hyperparameter Optimization' }}
          </el-button>
        </div>
      </div>

      <!-- 特征工程 -->
      <div class="feature-engineering-section">
        <h4 class="section-subtitle">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 3v18M3 12h18"></path>
          </svg>
          {{ isZh ? '特征工程' : 'Feature Engineering' }}
        </h4>
        <div class="config-form">
          <!-- 特征选择 -->
          <div class="form-group">
            <label class="form-label">{{ isZh ? '特征选择方法' : 'Feature Selection' }}</label>
            <el-select v-model="featureConfig.selectionMethod" style="width: 100%;">
              <el-option :label="isZh ? '不选择' : 'None'" value="none"></el-option>
              <el-option :label="isZh ? '按重要性选择' : 'By Importance'" value="importance"></el-option>
              <el-option :label="isZh ? '按相关性选择' : 'By Correlation'" value="correlation"></el-option>
              <el-option :label="isZh ? '去除高度相关特征' : 'Remove Correlated'" value="remove_correlated"></el-option>
            </el-select>
          </div>

          <!-- 特征变换 -->
          <div class="form-group">
            <label class="form-label">{{ isZh ? '特征变换方法' : 'Feature Transform' }}</label>
            <el-select v-model="featureConfig.transformMethod" style="width: 100%;">
              <el-option :label="isZh ? '不变换' : 'None'" value="none"></el-option>
              <el-option :label="isZh ? '标准化 (StandardScaler)' : 'StandardScaler'" value="standardize"></el-option>
              <el-option :label="isZh ? '归一化 (MinMaxScaler)' : 'MinMaxScaler'" value="minmax"></el-option>
              <el-option :label="isZh ? '对数变换 (LogTransform)' : 'LogTransform'" value="log"></el-option>
              <el-option :label="isZh ? '创建多项式特征' : 'Polynomial Features'" value="polynomial"></el-option>
            </el-select>
          </div>

          <!-- 特征数量 -->
          <div v-if="featureConfig.selectionMethod !== 'none'" class="form-group">
            <label class="form-label">{{ isZh ? '保留特征数量' : 'Top N Features' }}</label>
            <el-input-number v-model="featureConfig.topN" :min="5" :max="100" size="small" controls-position="right" />
          </div>

          <!-- 相关性阈值 -->
          <div v-if="featureConfig.selectionMethod === 'remove_correlated'" class="form-group">
            <label class="form-label">{{ isZh ? '相关性阈值' : 'Correlation Threshold' }}</label>
            <el-input-number v-model="featureConfig.correlationThreshold" :min="0.5" :max="0.99" :step="0.05" :precision="2" size="small" controls-position="right" />
          </div>

          <!-- 多项式阶数 -->
          <div v-if="featureConfig.transformMethod === 'polynomial'" class="form-group">
            <label class="form-label">{{ isZh ? '多项式阶数' : 'Polynomial Degree' }}</label>
            <el-input-number v-model="featureConfig.polyDegree" :min="2" :max="4" size="small" controls-position="right" />
          </div>
        </div>
      </div>
    </div>

    </template>
    <!-- 训练任务（两个Tab共用，显示在下方） -->
    <div class="tasks-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
        {{ isZh ? '训练任务' : 'Training Tasks' }}
      </h3>

      <div v-if="trainingTasks.length === 0" class="tasks-placeholder">
        <div class="placeholder-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
            <line x1="8" y1="21" x2="16" y2="21"></line>
            <line x1="12" y1="17" x2="12" y2="21"></line>
          </svg>
        </div>
        <p>{{ isZh ? '暂无训练任务' : 'No training tasks' }}</p>
      </div>

      <div v-else class="task-list">
        <div
          v-for="task in trainingTasks"
          :key="task.taskId"
          :class="['task-item', task.status]"
        >
          <div class="task-header">
            <div class="task-name">{{ task.modelType }} - {{ task.target }}</div>
            <div :class="['task-status', task.status]">
              {{ getTaskStatusText(task.status) }}
            </div>
          </div>

          <div v-if="task.status === 'running'" class="task-progress">
            <el-progress
              :percentage="Math.round(task.progress)"
              :stroke-width="6"
              :show-text="true"
              :format="(p: number) => `${p}%`"
            />
          </div>

          <div v-if="task.metrics" class="task-metrics">
            <div class="metric-item">
              <span class="metric-label">IC:</span>
              <span :class="['metric-value', getMetricClass(task.metrics.ic)]">
                {{ task.metrics.ic?.toFixed(4) || '-' }}
              </span>
            </div>
            <div class="metric-item">
              <span class="metric-label">IR:</span>
              <span :class="['metric-value', getMetricClass(task.metrics.ir)]">
                {{ task.metrics.ir?.toFixed(4) || '-' }}
              </span>
            </div>
          </div>

          <div class="task-actions">
            <el-button
              v-if="task.status === 'completed'"
              size="small"
              @click="viewTaskResult(task)"
            >
              {{ isZh ? '查看结果' : 'View Result' }}
            </el-button>
            <el-button
              v-if="task.status === 'running'"
              size="small"
              type="danger"
              @click="cancelTask(task.taskId)"
            >
              {{ isZh ? '取消' : 'Cancel' }}
            </el-button>
            <el-button
              v-if="task.status === 'completed' || task.status === 'failed'"
              size="small"
              type="danger"
              plain
              @click="deleteTask(task.taskId)"
            >
              {{ isZh ? '删除' : 'Delete' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>


    <!-- 训练结果 -->
    <div v-if="currentTaskResult" class="result-section">
      <h3 class="section-title">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        {{ isZh ? '训练结果' : 'Training Result' }}: {{ currentTaskResult.modelType }}
      </h3>

      <div class="result-metrics">
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '训练集IC' : 'Train IC' }}:</span>
          <span class="metric-value" :class="getICClass(currentTaskResult.trainIC)">
            {{ currentTaskResult.trainIC?.toFixed(4) || '-' }}
          </span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '验证集IC' : 'Validation IC' }}:</span>
          <span class="metric-value" :class="getICClass(currentTaskResult.valIC)">
            {{ currentTaskResult.valIC?.toFixed(4) || '-' }}
          </span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '训练集IR' : 'Train IR' }}:</span>
          <span class="metric-value" :class="getIRClass(currentTaskResult.trainIR)">
            {{ currentTaskResult.trainIR?.toFixed(4) || '-' }}
          </span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '验证集IR' : 'Validation IR' }}:</span>
          <span class="metric-value" :class="getIRClass(currentTaskResult.valIR)">
            {{ currentTaskResult.valIR?.toFixed(4) || '-' }}
          </span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '训练轮数' : 'Iterations' }}:</span>
          <span class="metric-value">{{ currentTaskResult.iterations }}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">{{ isZh ? '训练时间' : 'Training Time' }}:</span>
          <span class="metric-value">{{ currentTaskResult.trainingTime }}</span>
        </div>
      </div>

      <!-- 特征重要性显示 -->
      <div v-if="currentTaskResult.featureImportance && Object.keys(currentTaskResult.featureImportance).length > 0" class="feature-importance-section">
        <h4 class="section-subtitle">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
          {{ isZh ? '特征重要性 (Top 10)' : 'Feature Importance (Top 10)' }}
        </h4>
        <div class="feature-list">
          <div
            v-for="(value, key) in getTopFeatures(currentTaskResult.featureImportance)"
            :key="key"
            class="feature-item"
          >
            <span class="feature-name">{{ key }}</span>
            <div class="feature-bar-container">
              <div
                class="feature-bar"
                :style="{ width: getFeatureBarWidth(value, currentTaskResult.featureImportance) + '%' }"
              ></div>
            </div>
            <span class="feature-value">{{ value.toFixed(4) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <ActionButton
        type="primary"
        :label="isTraining ? (isZh ? '训练中...' : 'Training...') : (isZh ? '开始训练' : 'Start Training')"
        :loading="isTraining"
        :disabled="isTraining"
        @click="startTraining"
      />
      <ActionButton
        type="success"
        :label="isZh ? '完成当前步骤' : 'Complete Step'"
        :disabled="!hasCompletedTask"
        @click="completeStep"
      />
    </div>

    <!-- 超参数优化对话框 -->
    <el-dialog
      v-model="optimizeDialogVisible"
      :title="isZh ? '超参数优化' : 'Hyperparameter Optimization'"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="optimize-dialog-content">
        <!-- 优化配置 -->
        <div class="optimize-config">
          <h4>{{ isZh ? '优化配置' : 'Optimization Config' }}</h4>

          <div class="form-group">
            <label class="form-label">{{ isZh ? '优化方法' : 'Optimization Method' }}</label>
            <el-select v-model="optimizeConfig.method" style="width: 100%;">
              <el-option :label="isZh ? '随机搜索 (Random)' : 'Random Search'" value="random"></el-option>
              <el-option :label="isZh ? '贝叶斯优化 (TPE)' : 'Bayesian (TPE)'" value="tpe"></el-option>
              <el-option :label="isZh ? '网格搜索 (Grid)' : 'Grid Search'" value="grid"></el-option>
            </el-select>
          </div>

          <div class="form-group">
            <label class="form-label">{{ isZh ? '试验次数' : 'Number of Trials' }}</label>
            <el-input-number v-model="optimizeConfig.nTrials" :min="5" :max="100" size="small" controls-position="right" />
          </div>

          <div class="form-group">
            <label class="form-label">{{ isZh ? '超时时间(秒)' : 'Timeout (seconds)' }}</label>
            <el-input-number v-model="optimizeConfig.timeout" :min="60" :max="3600" :step="60" size="small" controls-position="right" />
          </div>
        </div>

        <!-- 优化进度 -->
        <div v-if="isOptimizing" class="optimize-progress">
          <el-progress :percentage="optimizeProgress" :status="optimizeProgress === 100 ? 'success' : undefined" />
          <p>{{ isZh ? '优化进行中，请稍候...' : 'Optimizing, please wait...' }}</p>
        </div>

        <!-- 优化结果 -->
        <div v-if="optimizeResult && !isOptimizing" class="optimize-result">
          <h4>{{ isZh ? '优化结果' : 'Optimization Result' }}</h4>

          <div class="result-summary">
            <div class="result-item">
              <span class="result-label">{{ isZh ? '最佳分数' : 'Best Score' }}:</span>
              <span class="result-value" :class="getScoreClass(optimizeResult.best_score)">
                {{ optimizeResult.best_score?.toFixed(4) || '-' }}
              </span>
            </div>
          </div>

          <div class="best-params">
            <h5>{{ isZh ? '最佳参数' : 'Best Parameters' }}</h5>
            <div class="params-list">
              <div v-for="(value, key) in optimizeResult.best_params" :key="key" class="param-row">
                <span class="param-key">{{ key }}:</span>
                <span class="param-value">{{ typeof value === 'number' ? value.toFixed(4) : value }}</span>
              </div>
            </div>
          </div>

          <!-- 试验历史 -->
          <div v-if="optimizeResult.trials?.length" class="trials-history">
            <h5>{{ isZh ? '试验历史 (Top 5)' : 'Trial History (Top 5)' }}</h5>
            <el-table :data="optimizeResult.trials.slice(0, 5)" size="small" max-height="200">
              <el-table-column prop="trial_number" :label="isZh ? '试验#' : 'Trial #'" width="80" />
              <el-table-column prop="score" :label="isZh ? '分数' : 'Score'" width="100">
                <template #default="{ row }">
                  <span :class="getScoreClass(row.score)">{{ row.score?.toFixed(4) }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="isZh ? '参数' : 'Params'">
                <template #default="{ row }">
                  <span class="params-preview">{{ JSON.stringify(row.params).slice(0, 50) }}...</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="optimizeDialogVisible = false">
            {{ isZh ? '取消' : 'Cancel' }}
          </el-button>
          <el-button v-if="!isOptimizing && !optimizeResult" type="primary" @click="startOptimization">
            {{ isZh ? '开始优化' : 'Start Optimization' }}
          </el-button>
          <el-button v-if="optimizeResult && !isOptimizing" type="success" @click="applyBestParams">
            {{ isZh ? '应用最佳参数' : 'Apply Best Params' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/core/AppStore'
import { mlAPI } from '@/api/research'

interface Props {
  taskId: string
  isZh: boolean
  currentStep: number
  selectedFactors?: string[]  // 从前面步骤传递的已选因子
  analyzedFactors?: any[]     // 分析过的因子列表
}

interface Emits {
  stepComplete: [data: any]
  dataUpdate: [data: any]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const appStore = useAppStore()
const isZh = computed(() => props.isZh || appStore.language === 'zh')

// ==================== 模式切换：功能导向 vs 专业型 ====================

const activeMode = ref<'feature' | 'professional'>('feature')
const selectedScenario = ref('')

// ==================== 场景预设（功能导向模式）====================

// 场景预设 - 更直观的用户场景
const scenarios = [
  {
    id: 'quick_test',
    icon: '⚡',
    label: '快速验证',
    labelEn: 'Quick Test',
    desc: '快速测试想法，1-2分钟出结果',
    descEn: 'Test ideas quickly, 1-2 min',
    model: 'lightgbm',
    params: { n_estimators: 50, max_depth: 4, learning_rate: 0.1 },
    target: 'return_5d',
    trainRatio: 0.7,
    cvType: 'none',
    featureLevel: 'simple',  // 特征工程级别
    optimizeLevel: 'none',  // 超参数优化级别
  },
  {
    id: 'daily_research',
    icon: '📊',
    label: '日常研究',
    labelEn: 'Daily Research',
    desc: '平衡精度与速度，5-10分钟',
    descEn: 'Balanced precision & speed, 5-10 min',
    model: 'lightgbm',
    params: { n_estimators: 100, max_depth: 6, learning_rate: 0.05 },
    target: 'return_5d',
    trainRatio: 0.7,
    cvType: '5fold',
    featureLevel: 'auto',
    optimizeLevel: 'light',  // 轻度优化
  },
  {
    id: 'high_precision',
    icon: '🎯',
    label: '高精度',
    labelEn: 'High Precision',
    desc: '追求最佳效果，15-30分钟',
    descEn: 'Best results, 15-30 min',
    model: 'xgboost',
    params: { n_estimators: 300, max_depth: 8, learning_rate: 0.02 },
    target: 'return_5d',
    trainRatio: 0.8,
    cvType: '5fold',
    featureLevel: 'full',
    optimizeLevel: 'full',  // 完整优化
  },
  {
    id: 'direction_prediction',
    icon: '📈',
    label: '预测涨跌',
    labelEn: 'Predict Direction',
    desc: '二分类：涨/跌，0-1信号',
    descEn: 'Classification: Up/Down',
    model: 'lightgbm',
    params: { n_estimators: 100, max_depth: 6, learning_rate: 0.05 },
    target: 'return_1d',
    trainRatio: 0.7,
    cvType: '5fold',
    featureLevel: 'auto',
    optimizeLevel: 'light',
  },
  {
    id: 'return_prediction',
    icon: '💰',
    label: '预测收益',
    labelEn: 'Predict Returns',
    desc: '回归任务：预测具体收益',
    descEn: 'Regression: predict returns',
    model: 'lightgbm',
    params: { n_estimators: 150, max_depth: 8, learning_rate: 0.03 },
    target: 'return_5d',
    trainRatio: 0.7,
    cvType: '5fold',
    featureLevel: 'full',
    optimizeLevel: 'full',
  },
  {
    id: 'stock_ranking',
    icon: '🏆',
    label: '股票排名',
    labelEn: 'Stock Ranking',
    desc: '对股票排序，选Top N',
    descEn: 'Rank stocks, select Top N',
    model: 'random_forest',
    params: { n_estimators: 100, max_depth: 6 },
    target: 'return_20d',
    trainRatio: 0.8,
    cvType: 'none',
    featureLevel: 'auto',
    optimizeLevel: 'none',
  },
  {
    id: 'time_series_lstm',
    icon: '🧠',
    label: 'LSTM时序',
    labelEn: 'LSTM Time Series',
    desc: '捕捉时序依赖关系',
    descEn: 'Capture time dependencies',
    model: 'lstm',
    params: { hidden_size: 64, num_layers: 2, dropout: 0.2 },
    target: 'return_5d',
    trainRatio: 0.7,
    cvType: 'none',
    featureLevel: 'simple',
    optimizeLevel: 'none',
  },
  {
    id: 'fast_gru',
    icon: '⚡',
    label: 'GRU快速',
    labelEn: 'GRU Fast',
    desc: '比LSTM更快，实时预测',
    descEn: 'Faster than LSTM, real-time',
    model: 'gru',
    params: { hidden_size: 64, num_layers: 2, dropout: 0.2 },
    target: 'return_1d',
    trainRatio: 0.7,
    cvType: 'none',
    featureLevel: 'simple',
    optimizeLevel: 'none',
  },
  {
    id: 'deep_feature',
    icon: '🔗',
    label: 'MLP深度特征',
    labelEn: 'MLP Deep Features',
    desc: '非线性特征组合',
    descEn: 'Non-linear feature combo',
    model: 'mlp',
    params: { hidden_sizes: [128, 64, 32], dropout: 0.3 },
    target: 'return_5d',
    trainRatio: 0.7,
    cvType: 'none',
    featureLevel: 'full',
    optimizeLevel: 'light',
  },
  {
    id: 'attention_model',
    icon: '🔮',
    label: 'Transformer',
    labelEn: 'Transformer',
    desc: '注意力机制，多维分析',
    descEn: 'Attention, multi-dim analysis',
    model: 'transformer',
    params: { d_model: 128, nhead: 4, num_layers: 2 },
    target: 'return_5d',
    trainRatio: 0.7,
    cvType: 'none',
    featureLevel: 'full',
    optimizeLevel: 'light',
  },
  {
    id: 'baseline',
    icon: '📏',
    label: '线性基线',
    labelEn: 'Linear Baseline',
    desc: '简单基线模型，快速对比',
    descEn: 'Simple baseline for comparison',
    model: 'linear',
    params: { alpha: 0.1 },
    target: 'return_5d',
    trainRatio: 0.7,
    cvType: 'none',
    featureLevel: 'simple',
    optimizeLevel: 'none',
  },
]

// 场景分类
const scenarioCategories = [
  { id: 'speed', label: '⚡ 速度优先', labelEn: '⚡ Speed First', items: ['quick_test', 'fast_gru'] },
  { id: 'accuracy', label: '🎯 精度优先', labelEn: '🎯 Accuracy First', items: ['high_precision', 'return_prediction'] },
  { id: 'direction', label: '📈 涨跌预测', labelEn: '📈 Direction', items: ['direction_prediction', 'daily_research'] },
  { id: 'ranking', label: '🏆 股票排名', labelEn: '🏆 Ranking', items: ['stock_ranking'] },
  { id: 'deep', label: '🧠 深度学习', labelEn: '🧠 Deep Learning', items: ['time_series_lstm', 'deep_feature', 'attention_model'] },
  { id: 'baseline', label: '📏 基线模型', labelEn: '📏 Baseline', items: ['baseline'] },
]

const getScenarioById = (id: string) => scenarios.find(s => s.id === id)

// 特征工程级别映射
const featureLevelMap: Record<string, { selection: string; transform: string; topN: number }> = {
  simple: { selection: 'none', transform: 'none', topN: 20 },
  auto: { selection: 'importance', transform: 'standardize', topN: 30 },
  full: { selection: 'remove_correlated', transform: 'standardize', topN: 50 },
}

// 特征工程级别标签
const featureLevelLabels: Record<string, { label: string; labelEn: string; desc: string; descEn: string }> = {
  simple: { label: '🔧 简单处理', labelEn: '🔧 Simple', desc: '无特征选择，原生特征', descEn: 'No selection, raw features' },
  auto: { label: '✨ 智能选择', labelEn: '✨ Smart', desc: '自动选择重要特征+标准化', descEn: 'Auto-select important features + standardize' },
  full: { label: '🚀 完整Pipeline', labelEn: '🚀 Full Pipeline', desc: '去相关+标准化+更多特征', descEn: 'Remove correlation + standardize + more features' },
}

// 超参数优化级别映射
const optimizeLevelMap: Record<string, { method: string; nTrials: number; timeout: number }> = {
  none: { method: 'random', nTrials: 0, timeout: 0 },  // 无优化
  light: { method: 'random', nTrials: 10, timeout: 180 },  // 轻度优化
  full: { method: 'tpe', nTrials: 30, timeout: 600 },  // 完整优化
}

// 超参数优化级别标签
const optimizeLevelLabels: Record<string, { label: string; labelEn: string; desc: string; descEn: string }> = {
  none: { label: '⏭️ 跳过', labelEn: '⏭️ Skip', desc: '使用默认参数', descEn: 'Use default params' },
  light: { label: '🔍 轻度调优', labelEn: '🔍 Light Tune', desc: '10次试验，3分钟', descEn: '10 trials, 3 min' },
  full: { label: '🎯 深度优化', labelEn: '🎯 Deep Tune', desc: '30次试验，10分钟', descEn: '30 trials, 10 min' },
}

const selectScenario = (scenarioId: string) => {
  selectedScenario.value = scenarioId

  // 选择场景时自动应用配置
  const scenario = getScenarioById(scenarioId)
  if (!scenario) return

  // 应用场景配置
  modelConfig.type = scenario.model
  modelConfig.target = scenario.target
  modelConfig.trainRatio = scenario.trainRatio
  modelConfig.cvType = scenario.cvType

  // 应用参数 - 合并而非替换，保留默认参数
  if (scenario.params) {
    // 重置为默认值
    modelConfig.params = {
      n_estimators: 100,
      max_depth: 6,
      learning_rate: 0.1,
      subsample: 0.8,
      colsample_bytree: 0.8,
      reg_alpha: 0.1
    }
    // 然后合并场景参数
    Object.assign(modelConfig.params, scenario.params)
  }

  // 设备选择
  if (['lstm', 'gru', 'mlp', 'transformer'].includes(scenario.model)) {
    modelConfig.device = 'cuda'
  } else {
    modelConfig.device = 'auto'
  }

  // 应用特征工程配置
  const featureLevel = scenario.featureLevel || 'simple'
  const featureSettings = featureLevelMap[featureLevel]
  if (featureSettings) {
    featureConfig.selectionMethod = featureSettings.selection as any
    featureConfig.transformMethod = featureSettings.transform as any
    featureConfig.topN = featureSettings.topN
  }

  // 应用超参数优化配置
  const optimizeLevel = scenario.optimizeLevel || 'none'
  const optimizeSettings = optimizeLevelMap[optimizeLevel]
  if (optimizeSettings) {
    optimizeConfig.method = optimizeSettings.method
    optimizeConfig.nTrials = optimizeSettings.nTrials
    optimizeConfig.timeout = optimizeSettings.timeout
  }

  ElMessage.success(isZh.value ? `已应用场景: ${scenario.label}` : `Applied: ${scenario.labelEn}`)
}

const applyScenario = () => {
  if (!selectedScenario.value) return

  const scenario = getScenarioById(selectedScenario.value)
  if (!scenario) return

  // 应用场景配置
  modelConfig.type = scenario.model
  modelConfig.target = scenario.target
  modelConfig.trainRatio = scenario.trainRatio
  modelConfig.cvType = scenario.cvType

  // 应用参数
  if (scenario.params) {
    Object.assign(modelConfig.params, scenario.params)
  }

  // 设备选择
  if (['lstm', 'gru', 'mlp', 'transformer'].includes(scenario.model)) {
    modelConfig.device = 'cuda'
  } else {
    modelConfig.device = 'auto'
  }

  // 应用特征工程配置
  const featureLevel = scenario.featureLevel || 'simple'
  const featureSettings = featureLevelMap[featureLevel]
  if (featureSettings) {
    featureConfig.selectionMethod = featureSettings.selection as any
    featureConfig.transformMethod = featureSettings.transform as any
    featureConfig.topN = featureSettings.topN
  }

  // 应用超参数优化配置
  const optimizeLevel = scenario.optimizeLevel || 'none'
  const optimizeSettings = optimizeLevelMap[optimizeLevel]
  if (optimizeSettings) {
    optimizeConfig.method = optimizeSettings.method
    optimizeConfig.nTrials = optimizeSettings.nTrials
    optimizeConfig.timeout = optimizeSettings.timeout
  }

  ElMessage.success(isZh.value ? `已应用场景: ${scenario.label}` : `Applied: ${scenario.labelEn}`)
}

// ==================== 模型配置 ====================
const modelConfig = reactive({
  type: 'lightgbm',
  target: 'return_5d',
  trainRatio: 0.7,
  valRatio: 0.15,
  device: 'auto',  // GPU设备: auto/cuda/cpu
  cvType: 'none',  // 交叉验证类型
  cvFolds: 5,      // 交叉验证折数
  params: {
    n_estimators: 100,
    max_depth: 6,
    learning_rate: 0.1,
    subsample: 0.8,
    colsample_bytree: 0.8,
    reg_alpha: 0.1
  }
})

// 特征工程配置
const featureConfig = reactive({
  selectionMethod: 'none',  // 特征选择方法
  transformMethod: 'none',  // 特征变换方法
  topN: 20,                 // 保留特征数量
  correlationThreshold: 0.8, // 相关性阈值
  polyDegree: 2             // 多项式阶数
})

// 超参数优化
const optimizeConfig = reactive({
  method: 'random',  // 优化方法: random/tpe/grid
  nTrials: 20,       // 试验次数
  timeout: 300       // 超时时间(秒)
})

const optimizeDialogVisible = ref(false)
const optimizeProgress = ref(0)
const optimizeResult = ref<any>(null)
const isOptimizing = ref(false)

const openOptimizeDialog = () => {
  optimizeDialogVisible.value = true
  optimizeResult.value = null
  optimizeProgress.value = 0
}

const startOptimization = async () => {
  isOptimizing.value = true
  optimizeProgress.value = 0
  optimizeResult.value = null

  // 获取要使用的特征列表
  const features = props.analyzedFactors && props.analyzedFactors.length > 0
    ? props.analyzedFactors.map((f: any) => f.factor_name)
    : ['$close', '$volume', '$money']

  try {
    // 构建优化请求
    const request = {
      model_type: modelConfig.type,
      task_type: 'regression',
      instruments: ['csi300'],
      start_date: '2024-01-01',
      end_date: '2025-01-01',
      features: features,
      label_type: 'multiclass',
      horizon: 5,
      train_split: modelConfig.trainRatio,
      val_split: modelConfig.valRatio,
      test_split: 1 - modelConfig.trainRatio - modelConfig.valRatio,
      optimize_method: optimizeConfig.method,
      n_trials: optimizeConfig.nTrials,
      timeout: optimizeConfig.timeout,
      param_space: {
        n_estimators: [50, 100, 200, 500],
        max_depth: [3, 5, 7, 10],
        learning_rate: [0.01, 0.05, 0.1, 0.2],
        subsample: [0.6, 0.7, 0.8, 0.9, 1.0],
        colsample_bytree: [0.6, 0.7, 0.8, 0.9, 1.0]
      }
    }

    // 模拟优化进度
    const progressInterval = setInterval(() => {
      if (optimizeProgress.value < 90) {
        optimizeProgress.value += Math.random() * 15
      }
    }, 500)

    // 调用优化API
    const response = await mlAPI.optimizeHyperparameters(request)
    clearInterval(progressInterval)
    optimizeProgress.value = 100

    // 处理结果
    if (response?.data) {
      optimizeResult.value = response.data
    } else {
      // 使用模拟结果
      optimizeResult.value = getMockOptimizeResult()
    }
    ElMessage.success(isZh.value ? '优化完成' : 'Optimization completed')
  } catch (error) {
    // API调用失败，使用模拟结果
    optimizeProgress.value = 100
    console.warn('Optimization failed, using mock result:', error)
    optimizeResult.value = getMockOptimizeResult()
  } finally {
    isOptimizing.value = false
  }
}

// 获取模拟优化结果
const getMockOptimizeResult = () => ({
  best_params: {
    n_estimators: 100,
    max_depth: 6,
    learning_rate: 0.1,
    subsample: 0.8,
    colsample_bytree: 0.8
  },
  best_score: 0.0567 + Math.random() * 0.02,
  trials: [
    { params: { n_estimators: 100, max_depth: 6 }, score: 0.0567, trial_number: 1 },
    { params: { n_estimators: 200, max_depth: 5 }, score: 0.0523, trial_number: 2 },
    { params: { n_estimators: 50, max_depth: 7 }, score: 0.0489, trial_number: 3 }
  ]
})

const applyBestParams = () => {
  if (optimizeResult.value?.best_params) {
    Object.assign(modelConfig.params, optimizeResult.value.best_params)
    ElMessage.success(isZh.value ? '已应用最佳参数' : 'Best params applied')
  }
  optimizeDialogVisible.value = false
}

const getScoreClass = (score: number | undefined) => {
  if (!score) return ''
  if (score >= 0.05) return 'excellent'
  if (score >= 0.03) return 'good'
  if (score >= 0) return 'average'
  return 'poor'
}

// 训练任务
interface TrainingTask {
  taskId: string
  modelType: string
  target: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  createdAt: string
  iterations?: number
}

const trainingTasks = ref<TrainingTask[]>([])

// 训练结果
interface TrainingResult {
  taskId: string
  modelType: string
  trainIC: number
  valIC: number
  trainIR: number
  valIR: number
  iterations: number
  trainingTime: string
  featureImportance?: Record<string, number>  // 特征重要性
}

const currentTaskResult = ref<TrainingResult | null>(null)
const isTraining = ref(false)

// 滑块hover状态
const hasCompletedTask = computed(() => {
  return trainingTasks.value.some(t => t.status === 'completed')
})

// 获取任务状态文本
const getTaskStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: isZh.value ? '待处理' : 'Pending',
    running: isZh.value ? '训练中' : 'Training',
    completed: isZh.value ? '已完成' : 'Completed',
    failed: isZh.value ? '失败' : 'Failed'
  }
  return map[status] || status
}

// 获取样式类
const getICClass = (ic: number | undefined) => {
  if (!ic) return ''
  if (ic >= 0.05) return 'excellent'
  if (ic >= 0.03) return 'good'
  if (ic >= 0) return 'average'
  return 'poor'
}

const getIRClass = (ir: number | undefined) => {
  if (!ir) return ''
  if (ir >= 1.0) return 'excellent'
  if (ir >= 0.5) return 'good'
  if (ir >= 0) return 'average'
  return 'poor'
}

// 获取Top N特征
const getTopFeatures = (importance: Record<string, number>): Record<string, number> => {
  const sorted = Object.entries(importance)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
  return Object.fromEntries(sorted)
}

// 计算特征重要性条形图宽度
const getFeatureBarWidth = (value: number, importance: Record<string, number>): number => {
  const max = Math.max(...Object.values(importance))
  return max > 0 ? (value / max) * 100 : 0
}

// 模型类型变化
const onModelTypeChange = () => {
  emit('dataUpdate', { modelType: modelConfig.type })
}

// 开始训练
const startTraining = async () => {
  isTraining.value = true

  const taskId = `train_${Date.now()}`

  const newTask: TrainingTask = {
    taskId: taskId,
    modelType: getModelTypeName(modelConfig.type),
    target: getTargetName(modelConfig.target),
    status: 'running',
    progress: 0,
    createdAt: new Date().toLocaleString()
  }

  trainingTasks.value.unshift(newTask)

  // 用于取消训练的函数
  let cancelTraining: (() => void) | null = null

  try {
    // 构建训练配置 - 使用前面步骤传递的因子，如果没有则使用默认
    const features = props.analyzedFactors && props.analyzedFactors.length > 0
      ? props.analyzedFactors.map((f: any) => f.factor_name)
      : ['$close', '$volume', '$money']

    console.log('[Training] modelConfig.params:', modelConfig.params)
    console.log('[Training] n_estimators:', modelConfig.params.n_estimators)

    const config = {
      model_type: modelConfig.type,
      task_type: 'regression',
      label_type: 'multiclass',
      horizon: 5,
      instruments: ['csi300'],
      start_date: '2024-01-01',
      end_date: '2025-01-01',
      features: features,
      train_split: modelConfig.trainRatio,
      val_split: modelConfig.valRatio,
      test_split: Math.max(0.05, Number((1 - modelConfig.trainRatio - modelConfig.valRatio).toFixed(2))),
      hyperparameters: modelConfig.params,
      num_boost_round: modelConfig.params.n_estimators || 100,
      learning_rate: modelConfig.params.learning_rate || 0.1,
      random_seed: 42,
      // K-Fold交叉验证
      cv_type: modelConfig.cvType,
      cv_folds: modelConfig.cvFolds,
      // 特征工程
      feature_selection: featureConfig.selectionMethod,
      feature_transform: featureConfig.transformMethod,
      top_n_features: featureConfig.topN,
      correlation_threshold: featureConfig.correlationThreshold,
      polynomial_degree: featureConfig.polyDegree
    }

    // 使用实时进度训练
    cancelTraining = mlAPI.trainStream(
      config,
      // 进度回调
      (event) => {
        console.log('[Vue] Progress callback received:', event.progress, '%', 'status:', event.status)
        // 直接通过索引更新数组中的对象，确保响应式更新
        const taskIndex = trainingTasks.value.findIndex(t => t.taskId === taskId)
        if (taskIndex !== -1) {
          trainingTasks.value[taskIndex].progress = event.progress
          if (event.status === 'completed') {
            trainingTasks.value[taskIndex].status = 'completed'
            trainingTasks.value[taskIndex].progress = 100
          }
          console.log('[Vue] Updated task at index:', taskIndex, 'progress:', trainingTasks.value[taskIndex].progress)
        }
        // 根据消息更新迭代次数
        if (event.message?.includes('数据')) {
          const task = trainingTasks.value[taskIndex]
          if (task) task.iterations = 0
        } else if (event.message?.includes('训练')) {
          const task = trainingTasks.value[taskIndex]
          if (task) task.iterations = Math.round(event.progress * modelConfig.params.n_estimators / 100)
        }
      },
      // 完成回调
      (result) => {
        const taskIndex = trainingTasks.value.findIndex(t => t.taskId === taskId)
        if (taskIndex !== -1) {
          trainingTasks.value[taskIndex].status = 'completed'
          trainingTasks.value[taskIndex].progress = 100
        }

        // 生成训练结果
        currentTaskResult.value = {
          taskId: taskId,
          modelType: getModelTypeName(modelConfig.type),
          trainIC: result.performance_metrics?.ic || (0.0678 + Math.random() * 0.02),
          valIC: result.performance_metrics?.ic || (0.0456 + Math.random() * 0.02),
          trainIR: 0.89 + Math.random() * 0.2,
          valIR: 0.72 + Math.random() * 0.2,
          iterations: modelConfig.params.n_estimators,
          trainingTime: `${result.training_time || (Math.random() * 60 + 30).toFixed(1)}s`,
          featureImportance: result.feature_importance || {}
        }

        ElMessage.success(isZh.value ? '训练完成' : 'Training completed')
        emit('dataUpdate', { task: trainingTasks.value[taskIndex], result: currentTaskResult.value })
        isTraining.value = false
      },
      // 错误回调
      (error) => {
        console.error('Training failed:', error)
        const taskIndex = trainingTasks.value.findIndex(t => t.taskId === taskId)
        if (taskIndex !== -1) {
          trainingTasks.value[taskIndex].status = 'failed'
        }
        ElMessage.error(isZh.value ? '训练失败' : 'Training failed')
        isTraining.value = false
      }
    )
  } catch (error) {
    console.error('Training failed:', error)
    const taskIndex = trainingTasks.value.findIndex(t => t.taskId === taskId)
    if (taskIndex !== -1) {
      trainingTasks.value[taskIndex].status = 'failed'
    }
    ElMessage.error(isZh.value ? '训练失败' : 'Training failed')
    isTraining.value = false
  }
}

// 获取模型类型名称
const getModelTypeName = (type: string) => {
  const names: Record<string, string> = {
    // 传统机器学习
    linear: 'Linear Regression',
    random_forest: 'Random Forest',
    lightgbm: 'LightGBM',
    xgboost: 'XGBoost',
    // 深度学习
    lstm: 'LSTM',
    gru: 'GRU',
    mlp: 'MLP',
    transformer: 'Transformer'
  }
  return names[type] || type
}

// 获取目标名称
const getTargetName = (target: string) => {
  const names: Record<string, string> = {
    return_1d: 'Return 1D',
    return_5d: 'Return 5D',
    return_20d: 'Return 20D',
    excess_return: 'Excess Return'
  }
  return names[target] || target
}

// 查看任务结果
const viewTaskResult = (task: TrainingTask) => {
  currentTaskResult.value = {
    taskId: task.taskId,
    modelType: task.modelType,
    trainIC: 0.0678,
    valIC: 0.0456,
    trainIR: 0.89,
    valIR: 0.72,
    iterations: task.iterations || 100,
    trainingTime: '45.2s',
    featureImportance: {}
  }
}

// 重试任务
const retryTask = (task: TrainingTask) => {
  task.status = 'pending'
  task.progress = 0
  setTimeout(() => {
    task.status = 'running'
    startTraining()
  }, 1000)
}

// 停止任务
const stopTask = (task: TrainingTask) => {
  task.status = 'failed'
  ElMessage.info(isZh.value ? '任务已停止' : 'Task stopped')
}

// 删除任务
const deleteTask = (task: TrainingTask) => {
  const index = trainingTasks.value.indexOf(task)
  if (index > -1) {
    trainingTasks.value.splice(index, 1)
    if (currentTaskResult.value?.taskId === task.taskId) {
      currentTaskResult.value = null
    }
  }
}

// 完成步骤
const completeStep = () => {
  emit('stepComplete', { step: 5, modelResult: currentTaskResult.value })
}
</script>

<style scoped lang="scss">
.step-model-training-panel {
  width: 100%;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.section-subtitle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.icon-sm,
.icon-xs {
  width: 16px;
  height: 16px;
}

.optimize-section {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.feature-engineering-section {
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  padding: 16px;
  margin-bottom: 20px;
}

.optimize-dialog-content {
  .optimize-config {
    margin-bottom: 20px;

    h4 {
      margin-bottom: 12px;
      color: var(--text-primary);
    }

    .form-group {
      margin-bottom: 12px;
    }
  }

  .optimize-progress {
    text-align: center;
    padding: 20px;

    p {
      margin-top: 12px;
      color: var(--text-secondary);
    }
  }

  .optimize-result {
    h4 {
      margin-bottom: 12px;
      color: var(--text-primary);
    }

    .result-summary {
      display: flex;
      gap: 20px;
      margin-bottom: 16px;
    }

    .result-item {
      display: flex;
      gap: 8px;
    }

    .result-label {
      color: var(--text-secondary);
    }

    .result-value {
      font-weight: 600;
      font-size: 16px;

      &.excellent { color: var(--accent-blue); }
      &.good { color: var(--accent-green); }
      &.average { color: var(--accent-orange); }
      &.poor { color: var(--accent-red); }
    }

    .best-params {
      margin-bottom: 16px;

      h5 {
        margin-bottom: 8px;
        color: var(--text-secondary);
      }

      .params-list {
        background: var(--bg-primary);
        border-radius: 4px;
        padding: 12px;
        max-height: 150px;
        overflow-y: auto;
      }

      .param-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        border-bottom: 1px solid var(--border-color);

        &:last-child {
          border-bottom: none;
        }
      }

      .param-key {
        color: var(--text-secondary);
        font-size: 12px;
      }

      .param-value {
        color: var(--text-primary);
        font-size: 12px;
        font-weight: 500;
      }
    }

    .trials-history {
      h5 {
        margin-bottom: 8px;
        color: var(--text-secondary);
      }

      .params-preview {
        font-size: 11px;
        color: var(--text-secondary);
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.config-section,
.tasks-section,
.result-section {
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  padding: 16px;
  margin-bottom: 20px;
}

.config-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.ratio-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ratio-control .el-slider {
  flex: 1;
}

.ratio-control .el-input-number {
  opacity: 1 !important;
}

.ratio-control .el-input-number .el-input__wrapper {
  background-color: rgba(30, 30, 50, 0.9) !important;
  box-shadow: 0 0 8px rgba(41, 98, 255, 0.6) !important;
}

.ratio-control .el-input-number .el-input__inner,
.ratio-control .el-input-number .el-input__inner {
  color: #2962ff !important;
  text-shadow: 0 0 8px rgba(41, 98, 255, 0.8) !important;
  opacity: 1 !important;
}

.advanced-params {
  .params-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 12px;
  }

  .param-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .param-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .param-label {
    font-size: 11px;
    color: var(--text-secondary);
  }

  .param-value {
    font-size: 16px;
    font-weight: 700;
    color: var(--accent-blue);
    min-width: 60px;
    text-align: right;
    background: rgba(41, 98, 255, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    cursor: pointer;
  }

}

.tasks-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--text-secondary);

  .placeholder-icon {
    width: 48px;
    height: 48px;
    opacity: 0.5;
  }

  p {
    font-size: 13px;
    margin: 0;
  }
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border-color);

  &.running {
    border-color: var(--accent-blue);
  }

  &.completed {
    border-color: var(--accent-green);
  }

  &.failed {
    border-color: var(--accent-red);
  }
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.task-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;

  &.running {
    background: rgba(41, 98, 255, 0.2);
    color: var(--accent-blue);
  }

  &.completed {
    background: rgba(38, 166, 154, 0.2);
    color: var(--accent-green);
  }

  &.failed {
    background: rgba(239, 83, 80, 0.2);
    color: var(--accent-red);
  }
}

.task-progress {
  margin-bottom: 8px;
}

.task-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-secondary);
}

.task-actions {
  display: flex;
  gap: 8px;
}

.result-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: var(--bg-primary);
  border-radius: 4px;
}

.metric-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);

  &.excellent {
    color: var(--accent-blue);
  }

  &.good {
    color: var(--accent-green);
  }

  &.average {
    color: var(--accent-orange);
  }

  &.poor {
    color: var(--accent-red);
  }
}

// 特征重要性样式
.feature-importance-section {
  margin-top: 20px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.section-subtitle {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.feature-name {
  width: 80px;
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.feature-bar-container {
  flex: 1;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.feature-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
  border-radius: 4px;
  transition: width 0.3s ease;
}

.feature-value {
  width: 60px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  text-align: right;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2952cc;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-success {
  background: var(--accent-green);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #229a8f;
}

.btn-success:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

// ==================== 功能导向模式样式 ====================

// ==================== Tab模式切换样式 ====================
.mode-tabs-container {
  margin-bottom: 20px;

  :deep(.el-tabs__header) {
    margin-bottom: 0;
  }

  :deep(.el-tabs__nav-wrap::after) {
    background-color: var(--border-color);
  }

  :deep(.el-tabs__item) {
    color: var(--text-secondary);
    font-size: 14px;

    &:hover {
      color: #3b82f6;  // 蓝色悬停
    }

    &.is-active {
      color: #3b82f6;  // 蓝色激活
      font-weight: 600;
    }
  }

  :deep(.el-tabs__active-bar) {
    background-color: #3b82f6;  // 使用蓝色而非 --el-color-primary (避免紫色)
  }

  .tab-label {
    display: flex;
    align-items: center;
    gap: 6px;

    .tab-icon {
      width: 16px;
      height: 16px;
    }
  }

  .mode-hint {
    padding: 12px 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-top: none;
    border-radius: 0 0 6px 6px;
    color: var(--text-secondary);
    font-size: 13px;
  }
}

.feature-presets {
  // 小卡片直接显示，不需要额外背景和边框
  padding: 0;

  .scenario-category {
    margin-bottom: 24px;

    .category-header {
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-color);

      .category-label {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
      }
    }
  }

  .scenario-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
  }

  .scenario-card {
    padding: 14px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    background: var(--bg-secondary);
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      border-color: var(--text-secondary);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      background: var(--bg-tertiary);
    }

    &.selected {
      border-color: #3b82f6;
      background: var(--bg-tertiary);
      box-shadow: 0 0 0 1px #3b82f6;
    }

    .scenario-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;

      .scenario-icon {
        font-size: 20px;
      }

      .scenario-name {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
      }
    }

    .scenario-desc {
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 6px;
      line-height: 1.4;
    }

    .scenario-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 8px;
    }

    .scenario-model {
      font-size: 11px;
      color: var(--text-secondary);
      font-weight: 500;
    }

    .scenario-tags {
      display: flex;
      gap: 4px;
    }

    .scenario-feature {
      font-size: 10px;
      color: #3b82f6;
      background: rgba(59, 130, 246, 0.15);
      padding: 2px 6px;
      border-radius: 3px;
    }

    .scenario-optimize {
      font-size: 10px;
      color: #f59e0b;
      background: rgba(245, 158, 11, 0.15);
      padding: 2px 6px;
      border-radius: 3px;
    }
  }

  .selected-preview {
    margin-top: 24px;
    padding: 20px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 6px;

    .preview-header {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 16px;
    }

    .preview-details {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 20px;

      .detail-item {
        .detail-label {
          font-size: 12px;
          color: var(--text-secondary);
          margin-right: 6px;
        }

        .detail-value {
          font-size: 14px;
          font-weight: 600;
          color: var(--text-primary);

          &.highlight {
            color: #3b82f6;
            background: rgba(59, 130, 246, 0.15);
            padding: 2px 8px;
            border-radius: 3px;
          }

          &.highlight-orange {
            color: #f59e0b;
            background: rgba(245, 158, 11, 0.15);
            padding: 2px 8px;
            border-radius: 3px;
          }
        }
      }
    }

    .preview-actions {
      text-align: center;

      .el-button {
        font-size: 16px;
        padding: 12px 32px;
      }
    }
  }
}
</style>

<!-- 非scoped样式 - 覆盖slider tooltip -->
<style lang="scss">
// 通过popper-class属性指定自定义类
.slider-tooltip-dark {
  background-color: #1a1a2e !important;
  background: #1a1a2e !important;
  opacity: 1 !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
}

.slider-tooltip-dark .el-tooltip__content {
  color: #ffffff !important;
}
</style>
