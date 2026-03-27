<template>
  <div class="research-detail-view">
    <GlobalNavBar />

    <!-- 主容器 -->
    <div class="main-container">
      <!-- 左侧：工作流步骤 -->
      <aside class="panel workflow-panel">
        <div class="panel-header">
          <span class="panel-title">
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 11 12 14 22 4"/>
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
            </svg>
            {{ isZh ? '工作流步骤' : 'Workflow Steps' }}
          </span>
        </div>
        <div class="workflow-list">
          <div
            v-for="step in workflowSteps"
            :key="step.id"
            :class="['workflow-step', step.status, { selected: currentStep === step.id }]"
            @click="selectStep(step.id)"
          >
            <div class="step-icon">
              <!-- 完成：打勾图标 -->
              <svg v-if="step.status === 'completed'" class="icon-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <!-- 进行中/待处理：数字或图标 -->
              <template v-else>
                <svg v-if="step.id === 1" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <ellipse cx="12" cy="5" rx="9" ry="3"/>
                  <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
                  <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
                </svg>
                <svg v-else-if="step.id === 2" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="4" y="4" width="16" height="16" rx="2"/>
                  <path d="M9 9h6M9 13h6M9 17h4"/>
                </svg>
                <svg v-else-if="step.id === 3" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 21H3V3"/>
                  <path d="M21 9l-6 6-4-4-6 6"/>
                </svg>
                <svg v-else-if="step.id === 4" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
                <svg v-else-if="step.id === 5" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="8" width="18" height="13" rx="2"/>
                  <circle cx="9" cy="13" r="1.5"/>
                  <circle cx="15" cy="13" r="1.5"/>
                  <path d="M8 17h8"/>
                  <path d="M12 4v3"/>
                </svg>
                <svg v-else-if="step.id === 6" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span v-else class="step-number">{{ step.id }}</span>
              </template>
            </div>
            <div class="step-info">
              <div class="step-title">{{ isZh ? step.nameZh : step.name }}</div>
              <div :class="['step-status', step.status]">
                <span class="status-dot"></span>
                {{ getStepStatusText(step.status) }}
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 中间：主内容区 -->
      <main class="panel content-panel">
        <div class="content-area">
          <!-- ===== 研究分析模块 ===== -->
          <template v-if="currentStageModule === 'research'">
            <!-- 任务标题和ID -->
            <div class="task-header-info">
              <el-input
                v-model="taskTitle"
                class="page-title-input"
                :placeholder="isZh ? '输入任务名称' : 'Enter task name'"
                @blur="updateTaskTitle"
              />
              <span class="task-id-badge">#{{ currentTask.id }}</span>
            </div>
            <p class="page-subtitle">{{ isZh ? currentStepData?.descriptionZh : currentStepData?.description }}</p>

            <!-- 步骤1：数据配置 -->
            <template v-if="currentStep === 1">
              <ResearchStep1DataConfig
                :task-id="taskId"
                :is-zh="isZh"
                v-model:model-stock-pool="stockPool"
                v-model:model-custom-stocks="customStocks"
                v-model:model-date-range="dateRange"
                v-model:model-periods="periods"
              />
            </template>

            <!-- 步骤2：因子计算 -->
            <template v-else-if="currentStep === 2">
              <ResearchStep2FactorCalculation
                :is-zh="isZh"
                :task-id="taskId"
                :date-range="dateRange"
                :stock-pool="stockPool"
              />
            </template>

            <!-- 步骤3：因子分析内容 -->
            <template v-else-if="currentStep === 3">
            <!-- Tabs -->
            <div class="content-tabs">
              <button
                v-for="tab in currentTabs"
                :key="tab.id"
                :class="['content-tab', { active: currentTab === tab.id }]"
                @click="switchTab(tab.id)"
              >
                <svg v-if="tab.id === 'overview'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="7" height="7"></rect>
                  <rect x="14" y="3" width="7" height="7"></rect>
                  <rect x="14" y="14" width="7" height="7"></rect>
                  <rect x="3" y="14" width="7" height="7"></rect>
                </svg>
                <svg v-else-if="tab.id === 'ic-ir'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                  <polyline points="17 6 23 6 23 12"></polyline>
                </svg>
                <svg v-else-if="tab.id === 'correlation'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="2"></circle>
                  <path d="M16.24 7.76a6 6 0 010 8.49m-8.48-.01a6 6 0 010-8.49m11.31-2.82a10 10 0 010 14.14m-14.14 0a10 10 0 010-14.14"></path>
                </svg>
                <svg v-else-if="tab.id === 'distribution'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="20" x2="18" y2="10"></line>
                  <line x1="12" y1="20" x2="12" y2="4"></line>
                  <line x1="6" y1="20" x2="6" y2="14"></line>
                </svg>
                <svg v-else class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                </svg>
                {{ isZh ? tab.nameZh : tab.name }}
              </button>
            </div>

            <!-- Tab Content -->
            <div class="tab-content">
            <!-- Overview Tab -->
            <div v-if="currentTab === 'overview'" class="tab-pane active">
              <!-- 因子库质量雷达图 - 使用 FactorQualityRadar 组件 -->
              <div class="factor-quality-section">
                <FactorQualityRadar
                  :title="isZh ? '因子库整体质量' : 'Factor Library Quality'"
                  :indicator="factorQualityRadarIndicator"
                  :indicator-values="factorQualityRadarIndicatorValues"
                  :data="factorQualityRadarData"
                />
              </div>

              <!-- Progress -->
              <div class="progress-section">
                <div class="progress-header">
                  <span class="progress-title">
                    <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    {{ isZh ? '分析进度' : 'Analysis Progress' }}
                  </span>
                  <span class="progress-percent">{{ currentTask.progress }}%</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: `${currentTask.progress}%` }"></div>
                </div>
              </div>

              <!-- Top Factors Table -->
              <h3 class="section-title">
                <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                {{ isZh ? '因子列表' : 'Factor List' }}
                <span class="factor-count">({{ factorListTab === 'current' ? topFactors.length : favoriteFactors.length }})</span>
                <!-- Tab切换：收藏 / 当前任务 -->
                <div class="factor-list-tabs">
                  <button
                    :class="['tab-btn', { active: factorListTab === 'current' }]"
                    @click="factorListTab = 'current'"
                  >
                    {{ isZh ? '当前' : 'Current' }}
                  </button>
                  <button
                    :class="['tab-btn', { active: factorListTab === 'favorites' }]"
                    @click="factorListTab = 'favorites'"
                  >
                    {{ isZh ? '收藏' : 'Favorites' }}
                    <span v-if="favoriteFactors.length > 0" class="favorite-badge">{{ favoriteFactors.length }}</span>
                  </button>
                </div>
                <!-- 卡片大小切换 -->
                <ModeSwitch
                  v-model="cardSize"
                  :options="cardSizeOptions"
                  class="card-size-switch-global"
                />
              </h3>

              <!-- 因子折叠面板（使用全局统一样式） -->
              <div class="collapse">
                <div
                  v-for="(factors, type) in groupedFactors"
                  :key="type"
                  :class="['collapse-item', { 'is-open': openFactorGroups.includes(type) }]"
                >
                  <div class="collapse-header" @click="toggleFactorGroup(type)">
                    <div class="collapse-title-row">
                      <span :class="['collapse-badge', 'badge-' + type]">{{ getFactorTypeLabel(type) }}</span>
                      <span class="collapse-count">{{ factors.length }} {{ isZh ? '个因子' : 'factors' }}</span>
                    </div>
                    <span class="collapse-arrow">▶</span>
                  </div>
                  <div class="collapse-content">
                    <div class="factor-card-grid">
                      <FactorCard
                        v-for="(factor, index) in factors"
                        :key="factor.factor_name"
                        :rank="getGlobalIndex(type, index) + 1"
                        :name="factor.factor_name"
                        :ic="factor.ic"
                        :ir="factor.ir"
                        :t-stat="factor.t_stat"
                        :status="factor.status"
                        :size="cardSize"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="action-buttons">
                <button class="btn btn-primary" @click="runFullAnalysis" :disabled="isAnalyzing">
                  {{ isAnalyzing ? (isZh ? '分析中...' : 'Analyzing...') : (isZh ? '运行完整分析' : 'Run Full Analysis') }}
                </button>
                <button class="btn btn-success" @click="completeCurrentStep">
                  {{ isZh ? '完成当前步骤' : 'Complete Step' }} ✓
                </button>
                <button class="btn btn-secondary" @click="exportResults">
                  {{ isZh ? '导出结果' : 'Export Results' }}
                </button>
              </div>
            </div>

            <!-- IC/IR Tab -->
            <div v-if="currentTab === 'ic-ir'" class="tab-pane active">
              <!-- 个体因子综合评估 - 使用 FactorEvaluationCard 组件 -->
              <FactorEvaluationCard
                :title="isZh ? '个体因子综合评估' : 'Individual Factor Evaluation'"
                :indicator="factorEvaluationIndicator"
                :indicator-values="factorEvaluationIndicatorValues"
                :data="factorEvaluationRadarData"
                style="margin-bottom: 12px"
              />

              <ICIRTrendChart
                :task-id="taskId"
                :target-period="icConfig.targetPeriod"
                :method="icConfig.method"
                :is-zh="isZh"
              />

            </div>

            <!-- Correlation Tab -->
            <div v-if="currentTab === 'correlation'" class="tab-pane active">
              <FactorCorrelationHeatmap
                :task-id="taskId"
                :method="correlationMethod"
                :is-zh="isZh"
              />
            </div>

            <!-- Distribution Tab -->
            <div v-if="currentTab === 'distribution'" class="tab-pane active">
              <FactorDistributionChart
                :task-id="taskId"
                :bins="distributionConfig.bins"
                :is-zh="isZh"
              />
            </div>
          </div>
          </template>

            <!-- 步骤4：因子评估 -->
            <template v-else-if="currentStep === 4">
              <ResearchStep4FactorEvaluation
                :task-id="taskId"
                :is-zh="isZh"
                :current-step="currentStep"
                :analyzed-factors="validFactors"
              />
            </template>

            <!-- 步骤5：模型训练 -->
            <template v-else-if="currentStep === 5">
              <ResearchStep5ModelTraining
                :task-id="taskId"
                :is-zh="isZh"
                :current-step="currentStep"
                :analyzed-factors="validFactors"
              />
            </template>

            <!-- 步骤6：可行性检查 -->
            <template v-else-if="currentStep === 6">
              <ResearchStep6FeasibilityCheck
                :task-id="taskId"
                :is-zh="isZh"
                :current-step="currentStep"
              />
            </template>
          </template>

          <template v-else-if="currentStageModule === 'backtest'">
            <h1 class="page-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
              {{ isZh ? '策略回测' : 'Strategy Backtest' }}
            </h1>
            <p class="page-subtitle">{{ isZh ? '验证策略在历史数据上的表现' : 'Validate strategy performance on historical data' }}</p>

            <!-- 回测绩效图表 -->
            <BacktestPerformanceChart
              :task-id="taskId"
              :is-zh="isZh"
            />

            <!-- 回测配置 -->
            <div class="progress-section">
              <h3 class="section-title" style="margin-bottom: 16px;">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="3"></circle>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                </svg>
                {{ isZh ? '回测配置' : 'Backtest Configuration' }}
              </h3>
              <div class="config-form">
                <div class="form-group">
                  <label class="form-label">{{ isZh ? '开始日期' : 'Start Date' }}</label>
                  <input type="date" class="form-input" v-model="backtestConfig.startDate" />
                </div>
                <div class="form-group">
                  <label class="form-label">{{ isZh ? '结束日期' : 'End Date' }}</label>
                  <input type="date" class="form-input" v-model="backtestConfig.endDate" />
                </div>
                <div class="form-group">
                  <label class="form-label">{{ isZh ? '初始资金' : 'Initial Capital' }}</label>
                  <input type="number" class="form-input" v-model.number="backtestConfig.initialCapital" />
                </div>
                <div class="form-group">
                  <label class="form-label">{{ isZh ? '手续费率' : 'Commission' }}</label>
                  <input type="number" class="form-input" step="0.0001" v-model.number="backtestConfig.commission" />
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <button class="btn btn-primary" @click="runBacktest" :disabled="isBacktesting">
                {{ isBacktesting ? (isZh ? '回测中...' : 'Backtesting...') : (isZh ? '运行回测' : 'Run Backtest') }}
              </button>
              <button class="btn btn-secondary" @click="exportBacktest">{{ isZh ? '导出报告' : 'Export Report' }}</button>
            </div>
          </template>

          <!-- ===== 信号生成模块 ===== -->
          <template v-else-if="currentStageModule === 'signal'">
            <h1 class="page-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
              {{ isZh ? '交易信号生成' : 'Trading Signal Generation' }}
            </h1>
            <p class="page-subtitle">{{ isZh ? '基于策略模型生成买卖信号' : 'Generate buy/sell signals based on strategy model' }}</p>

            <!-- 信号统计 -->
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-label">
                  <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                  </svg>
                  {{ isZh ? '今日信号' : 'Today Signals' }}
                </div>
                <div class="stat-value positive">{{ signalStats.todaySignals }}</div>
                <div class="stat-change">{{ isZh ? '个股票' : 'stocks' }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">
                  <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 19V5M5 12l7-7 7 7"/>
                  </svg>
                  {{ isZh ? '买入信号' : 'Buy Signals' }}
                </div>
                <div class="stat-value positive">{{ signalStats.buySignals }}</div>
                <div class="stat-change">{{ isZh ? '看涨' : 'Bullish' }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">
                  <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 5v14M5 12l7 7 7-7"/>
                  </svg>
                  {{ isZh ? '卖出信号' : 'Sell Signals' }}
                </div>
                <div class="stat-value negative">{{ signalStats.sellSignals }}</div>
                <div class="stat-change">{{ isZh ? '看跌' : 'Bearish' }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">
                  <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                  {{ isZh ? '信号准确率' : 'Accuracy' }}
                </div>
                <div :class="['stat-value', { positive: signalStats.accuracy > 60 }]">
                  {{ signalStats.accuracy.toFixed(1) }}%
                </div>
                <div class="stat-change">{{ isZh ? '近30天' : 'Last 30 days' }}</div>
              </div>
            </div>

            <!-- 最新信号列表 -->
            <div class="progress-section">
              <h3 class="section-title" style="margin-bottom: 16px;">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
                {{ isZh ? '最新交易信号' : 'Latest Trading Signals' }}
              </h3>
              <table class="data-table">
                <thead>
                  <tr>
                    <th>{{ isZh ? '股票代码' : 'Code' }}</th>
                    <th>{{ isZh ? '股票名称' : 'Name' }}</th>
                    <th>{{ isZh ? '信号类型' : 'Signal' }}</th>
                    <th>{{ isZh ? '信号强度' : 'Strength' }}</th>
                    <th>{{ isZh ? '生成时间' : 'Time' }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="signal in latestSignals" :key="signal.code">
                    <td>{{ signal.code }}</td>
                    <td>{{ signal.name }}</td>
                    <td>
                      <span :class="['status-badge', signal.type === 'buy' ? 'pass' : 'fail']">
                        {{ signal.type === 'buy' ? (isZh ? '买入' : 'Buy') : (isZh ? '卖出' : 'Sell') }}
                      </span>
                    </td>
                    <td :class="['value', { positive: signal.strength > 0.7 }]">{{ (signal.strength * 100).toFixed(0) }}%</td>
                    <td>{{ signal.time }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <button class="btn btn-primary" @click="generateSignals" :disabled="isGenerating">
                {{ isGenerating ? (isZh ? '生成中...' : 'Generating...') : (isZh ? '生成信号' : 'Generate Signals') }}
              </button>
              <button class="btn btn-secondary" @click="exportSignals">{{ isZh ? '导出信号' : 'Export Signals' }}</button>
            </div>
          </template>
        </div>

      </main>

      <!-- 右侧：因子库 -->
      <aside class="panel factor-panel">
        <div class="panel-header">
          <span class="panel-title">
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
            {{ isZh ? '因子库' : 'Factor Library' }}
          </span>
          <div class="panel-actions">
            <button class="icon-btn" @click="addCustomFactor" :title="isZh ? '添加自定义因子' : 'Add Custom Factor'">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
            <button class="icon-btn" @click="openFactorSettings" :title="isZh ? '设置' : 'Settings'">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
            </button>
          </div>
        </div>
        <div class="factor-list">
          <!-- 无因子时的提示 -->
          <div v-if="topFactorsForDisplay.length === 0" class="empty-tip">
            {{ isZh ? '暂无因子数据，请运行完整分析' : 'No factors. Run full analysis first.' }}
          </div>
          <div
            v-else
            v-for="factor in topFactorsForDisplay"
            :key="factor.name"
            :class="['factor-item', { selected: selectedFactor === factor.name }]"
            @click="selectFactorByName(factor.name)"
          >
            <div class="factor-header">
              <div class="factor-name">
                <span class="factor-status-dot" :class="getFactorStatus(factor.ic ?? undefined)"></span>
                {{ factor.name }}
                <!-- 收藏按钮 -->
                <span
                  class="favorite-btn"
                  :class="{ favorited: isFavorited(factor.name) }"
                  @click.stop="toggleFavorite(factor.name)"
                  :title="isFavorited(factor.name) ? (isZh ? '取消收藏' : 'Remove from favorites') : (isZh ? '添加收藏' : 'Add to favorites')"
                >
                  <svg viewBox="0 0 24 24" :fill="isFavorited(factor.name) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                  </svg>
                </span>
              </div>
              <div class="factor-score" :class="getFactorScoreClass(factor.ic ?? undefined)">
                <svg class="icon-xs" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
                {{ factor.ic?.toFixed(2) ?? 'N/A' }}
              </div>
            </div>
            <div class="factor-type">
              <span class="type-tag">{{ factor.category }}</span>
              <span class="type-separator">•</span>
              {{ isZh ? factor.typeZh : factor.type }}
            </div>
            <div class="factor-metrics">
              <span class="metric">
                <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M23 18l-9.5-9.5-5 5L1 6"/>
                </svg>
                IC: <span :class="['metric-value', { positive: (factor.ic ?? 0) > 0.03, negative: (factor.ic ?? 0) < 0 }]">{{ factor.ic?.toFixed(3) ?? 'N/A' }}</span>
              </span>
              <span class="metric">
                <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                IR: <span :class="['metric-value', { positive: (factor.ir ?? 0) > 0.5 }]">{{ factor.ir?.toFixed(2) ?? 'N/A' }}</span>
              </span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
// ============================================================================
// ResearchDetailView.vue - 研究分析详情页主组件
// ============================================================================
// 文件结构说明（方便将来拆分）：
// - 公共状态与配置
// - 因子库质量评估（概览Tab）
// - 个体因子评估（IC/IR Tab）
// - 因子计算相关
// - 其他功能
// ============================================================================

import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { factorApi, type FactorInfo, type FactorResult } from '@/api/modules/research'
import { DataLine, Connection, Histogram, Odometer, TrendCharts, Folder, Box, Document, Setting } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import CustomSelect from '@/components/common/CustomSelect.vue'
import FactorCard from '@/components/ui/FactorCard.vue'
import FactorQualityRadar from '@/components/ui/FactorQualityRadar.vue'
import FactorEvaluationCard from '@/components/ui/FactorEvaluationCard.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import ScoreCard from '@/components/ui/ScoreCard.vue'
import ModeSwitch from '@/components/ui/ModeSwitch.vue'
// ---- 子组件（将来可考虑进一步内联或统一管理）----
import ICIRTrendChart from './ICIRTrendChart.vue'
import FactorCorrelationHeatmap from './FactorCorrelationHeatmap.vue'
import FactorDistributionChart from './FactorDistributionChart.vue'
import BacktestPerformanceChart from './BacktestPerformanceChart.vue'
import ResearchStep1DataConfig from './components/ResearchStep1DataConfig.vue'
import ResearchStep2FactorCalculation from './components/ResearchStep2FactorCalculation.vue'
import ResearchStep4FactorEvaluation from './components/ResearchStep4FactorEvaluation.vue'
import ResearchStep5ModelTraining from './components/ResearchStep5ModelTraining.vue'
import ResearchStep6FeasibilityCheck from './components/ResearchStep6FeasibilityCheck.vue'
import { useAppStore } from '@/stores/core/AppStore'
import GlobalNavBar from '@/components/GlobalNavBar.vue'

// ============================================================================
// 公共状态与配置
// ============================================================================
const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

// 任务ID - 从URL获取
const taskId = computed(() => route.query.taskId as string || 'default')

// 任务配置数据 - 模拟从后端获取的任务数据
interface TaskConfig {
  id: string
  title: string
  titleZh: string
  stockPool: string
  stockPoolZh: string
  dateStart: string
  dateEnd: string
  periods?: string[]
  period?: string
  factors: string
  factorsZh: string
  model?: string
  icMethod: string
  icThreshold: number
  progress: number
}

// 模拟任务数据存储 - 使用reactive使其响应式
const taskStore = reactive<Record<string, TaskConfig>>({
  'RES-2024-001': {
    id: 'RES-2024-001',
    title: 'Alpha158 Factor Analysis',
    titleZh: 'Alpha158因子分析',
    stockPool: 'CSI300',
    stockPoolZh: '沪深300',
    dateStart: '2021-01-01',
    dateEnd: '2024-12-31',
    periods: ['1d'],
    factors: 'Alpha158',
    factorsZh: 'Alpha158因子集',
    icMethod: 'spearman',
    icThreshold: 0.03,
    progress: 67
  },
  'RES-2024-002': {
    id: 'RES-2024-002',
    title: 'LGB Model Training',
    titleZh: 'LightGBM模型训练',
    stockPool: 'CSI500',
    stockPoolZh: '中证500',
    dateStart: '2020-01-01',
    dateEnd: '2024-12-31',
    factors: 'Top20 Selected',
    factorsZh: '精选Top20因子',
    model: 'LightGBM',
    icMethod: 'spearman',
    icThreshold: 0.05,
    progress: 45
  },
  'RES-2024-003': {
    id: 'RES-2024-003',
    title: 'Factor Correlation Analysis',
    titleZh: '因子相关性分析',
    stockPool: 'All A-shares',
    stockPoolZh: '全A股',
    dateStart: '2022-01-01',
    dateEnd: '2024-12-31',
    factors: 'All Qualified',
    factorsZh: '全部合格因子',
    icMethod: 'pearson',
    icThreshold: 0.05,
    progress: 0
  },
  'RES-2024-004': {
    id: 'RES-2024-004',
    title: 'Data Configuration - CSI300',
    titleZh: '数据配置 - 沪深300',
    stockPool: 'CSI300',
    stockPoolZh: '沪深300',
    dateStart: '2021-01-01',
    dateEnd: '2024-12-31',
    factors: 'Basic Setup',
    factorsZh: '基础配置',
    icMethod: 'spearman',
    icThreshold: 0.03,
    progress: 100
  },
  'RES-2024-005': {
    id: 'RES-2024-005',
    title: 'Custom Factor - MA_Cross',
    titleZh: '自定义因子 - 均线交叉',
    stockPool: 'CSI300',
    stockPoolZh: '沪深300',
    dateStart: '2020-01-01',
    dateEnd: '2024-12-31',
    factors: 'MA_Cross_60',
    factorsZh: '60日均线交叉',
    icMethod: 'spearman',
    icThreshold: 0.03,
    progress: 100
  },
  'default': {
    id: 'default',
    title: 'New Research Task',
    titleZh: '新建研究任务',
    stockPool: 'CSI300',
    stockPoolZh: '沪深300',
    dateStart: '2023-01-01',
    dateEnd: '2024-12-31',
    periods: ['1d'],
    factors: 'Alpha158',
    factorsZh: 'Alpha158因子集',
    icMethod: 'spearman',
    icThreshold: 0.03,
    progress: 0
  }
})

// 当前任务配置
const currentTask = computed(() => taskStore[taskId.value] || taskStore['default'])

// 股票池 - 本地响应式副本
const stockPool = ref(currentTask.value?.stockPool || 'CSI300')
const customStocks = ref('')
const showCustomStockDialog = ref(false)

const handleStockPoolChange = (val: string) => {
  if (val === 'custom') {
    showCustomStockDialog.value = true
  } else {
    customStocks.value = ''
  }
}

// 监听 currentTask 变化，更新本地 stockPool
watch(() => currentTask.value?.stockPool, (newVal) => {
  if (newVal) {
    stockPool.value = newVal
  }
})

// 股票池变化时更新 taskStore
watch(stockPool, (newVal) => {
  const task = taskStore[taskId.value] || taskStore['default']
  if (task) {
    task.stockPool = newVal
    // 更新显示名称
    const poolNames: Record<string, string> = {
      'CSI300': '沪深300',
      'CSI500': '中证500',
      'CSI1000': '中证1000',
      'All A-shares': '全市场'
    }
    task.stockPoolZh = poolNames[newVal] || newVal
  }
})

// 日期范围 - 本地响应式副本
const dateRange = ref<Date[] | null>(null)

// 监听 currentTask 变化，初始化日期范围
watch(() => [currentTask.value?.dateStart, currentTask.value?.dateEnd], () => {
  if (currentTask.value?.dateStart && currentTask.value?.dateEnd) {
    dateRange.value = [
      new Date(currentTask.value.dateStart),
      new Date(currentTask.value.dateEnd)
    ]
  }
}, { immediate: true })

// 日期范围变化时更新 taskStore
watch(dateRange, (newVal) => {
  if (newVal && Array.isArray(newVal) && newVal[0] && newVal[1]) {
    const task = taskStore[taskId.value] || taskStore['default']
    if (task) {
      task.dateStart = newVal[0].toISOString().split('T')[0]
      task.dateEnd = newVal[1].toISOString().split('T')[0]
    }
  }
}, { deep: true })

// 周期 - 本地响应式副本（支持多选）
const periods = ref<string[]>(currentTask.value?.periods || ['1d'])

// 周期选项
const periodOptions = [
  { label: '日线', value: '1d' },
  { label: '周线', value: '1w' },
  { label: '月线', value: '1M' },
  { label: '季线', value: '1q' },
  { label: '年线', value: '1y' },
  { label: '5分钟', value: '5m' },
  { label: '15分钟', value: '15m' },
  { label: '30分钟', value: '30m' },
  { label: '60分钟', value: '60m' },
]

// 因子计算相关变量（支持多选）
const selectedCalcTypes = ref<string[]>(['alpha158'])
const customFactorExpression = ref('')
const isCalculating = ref(false)

// 因子任务列表相关变量
interface CalculationTask {
  task_id: string
  expression: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  created_at: string
}
const calculationTasks = ref<CalculationTask[]>([])
const currentResultTaskId = ref<string | null>(null)

// 因子结果查看器相关变量
interface FactorData {
  instrument: string
  name?: string  // 股票中文名称
  datetime: string
  value: number
}

interface CalculationResult {
  factor_name: string
  data: FactorData[]
  statistics: {
    count: number
    mean: number
    std: number
    min: number
    max: number
  }
}

const currentResult = ref<CalculationResult | null>(null)
const resultPage = ref(1)
const resultPageSize = 50

// 分页结果数据
const paginatedResultData = computed(() => {
  if (!currentResult.value?.data) return []
  const start = (resultPage.value - 1) * resultPageSize
  return currentResult.value.data.slice(start, start + resultPageSize)
})

// 获取任务状态文本
const getTaskStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待执行',
    running: '计算中',
    completed: '已完成',
    failed: '失败'
  }
  return isZh.value ? (map[status] || status) : status
}

// 股票名称映射（从后端API获取）
// const stockNames: Record<string, string> = {}

// 查看任务结果
const viewTaskResult = (taskId: string) => {
  currentResultTaskId.value = taskId
  // 模拟结果数据（正式环境中从后端API获取股票名称）
  currentResult.value = {
    factor_name: `Factor_${taskId.slice(0, 8)}`,
    data: Array.from({ length: 20 }, (_, i) => ({
      instrument: `00000${i}`.slice(-6),
      name: '', // 后端返回股票名称
      datetime: new Date(Date.now() - i * 86400000).toISOString().split('T')[0],
      value: Math.random() * 2 - 1
    })),
    statistics: {
      count: 1000,
      mean: 0.0234,
      std: 0.4567,
      min: -1.234,
      max: 1.567
    }
  }
}

// 重试任务
const retryTask = (taskId: string) => {
  const task = calculationTasks.value.find(t => t.task_id === taskId)
  if (task) {
    task.status = 'pending'
    task.progress = 0
    // 模拟重新计算
    setTimeout(() => {
      task.status = 'running'
      const interval = setInterval(() => {
        task.progress += 10
        if (task.progress >= 100) {
          clearInterval(interval)
          task.status = 'completed'
        }
      }, 500)
    }, 1000)
  }
}

// 删除任务
const deleteTask = (taskId: string) => {
  calculationTasks.value = calculationTasks.value.filter(t => t.task_id !== taskId)
  if (currentResultTaskId.value === taskId) {
    currentResult.value = null
    currentResultTaskId.value = null
  }
}

// 导出结果
const exportResult = (format: 'csv' | 'excel') => {
  console.log('Exporting result as:', format)
  ElMessage.success(isZh.value ? `已导出为${format.toUpperCase()}` : `Exported as ${format.toUpperCase()}`)
}

// 保存为QLib格式
const saveToQlib = () => {
  console.log('Saving to QLib format')
  ElMessage.success(isZh.value ? '已保存为QLib格式' : 'Saved as QLib format')
}

// 切换计算类型（多选）
const toggleCalcType = (type: string) => {
  const index = selectedCalcTypes.value.indexOf(type)
  if (index === -1) {
    selectedCalcTypes.value.push(type)
  } else {
    selectedCalcTypes.value.splice(index, 1)
  }
}

// 技术指标相关变量
const showIndicators = ref(false)
const selectedIndicators = ref<string[]>([])
const selectedPresets = ref<string[]>([])
const selectedFactorTemplate = ref('')

// 预设组合映射
const presetMap: Record<string, string[]> = {
  trend: ['MA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'T3', 'KAMA', 'BOLL', 'SAR', 'HT_TRENDLINE'],
  volume: ['AD', 'ADOSC', 'OBV'],
  oscillator: ['RSI', 'KDJ', 'CCI', 'MACD', 'STOCH', 'STOCHF', 'STOCHRSI', 'ULTOSC', 'TRIX', 'APO', 'PPO'],
  momentum: ['MOM', 'ROC', 'ROCP', 'ROCR', 'ROCR100', 'CMO', 'MFI'],
  volatility: ['ATR', 'NATR', 'STDDEV'],
  cycle: ['DPO', 'HT_DCPERIOD', 'HT_SINE', 'HT_TRENDMODE', 'AROON', 'AROONOSC']
}

// 切换预设组合（多选）
const togglePreset = (type: string) => {
  const index = selectedPresets.value.indexOf(type)
  if (index === -1) {
    selectedPresets.value.push(type)
    // 添加该预设的指标
    const indicators = presetMap[type] || []
    indicators.forEach(ind => {
      if (!selectedIndicators.value.includes(ind)) {
        selectedIndicators.value.push(ind)
      }
    })
  } else {
    selectedPresets.value.splice(index, 1)
    // 移除该预设的指标（如果不在其他预设中）
    const indicators = presetMap[type] || []
    indicators.forEach(ind => {
      const inOtherPreset = Object.entries(presetMap).some(([key, inds]) => {
        return key !== type && selectedPresets.value.includes(key) && inds.includes(ind)
      })
      if (!inOtherPreset) {
        selectedIndicators.value = selectedIndicators.value.filter(i => i !== ind)
      }
    })
  }
}

// 所有指标列表
const allIndicators = ref([
  // 趋势指标
  { label: 'MA(简单移动平均)', value: 'MA', category: 'trend' },
  { label: 'EMA(指数移动平均)', value: 'EMA', category: 'trend' },
  { label: 'WMA(加权移动平均)', value: 'WMA', category: 'trend' },
  { label: 'DEMA(双指数移动平均)', value: 'DEMA', category: 'trend' },
  { label: 'TEMA(三重指数移动平均)', value: 'TEMA', category: 'trend' },
  { label: 'T3(三重指数移动平均)', value: 'T3', category: 'trend' },
  { label: 'KAMA(考夫曼自适应均线)', value: 'KAMA', category: 'trend' },
  { label: 'BOLL(布林带)', value: 'BOLL', category: 'trend' },
  { label: 'SAR(抛物线转向)', value: 'SAR', category: 'trend' },
  { label: 'HT_TRENDLINE(希尔伯特趋势线)', value: 'HT_TRENDLINE', category: 'trend' },
  // 震荡指标
  { label: 'RSI(相对强弱指标)', value: 'RSI', category: 'oscillator' },
  { label: 'KDJ(随机指标)', value: 'KDJ', category: 'oscillator' },
  { label: 'STOCH(随机指标)', value: 'STOCH', category: 'oscillator' },
  { label: 'STOCHF(快速随机指标)', value: 'STOCHF', category: 'oscillator' },
  { label: 'MACD', value: 'MACD', category: 'oscillator' },
  { label: 'STOCHRSI(相对强弱随机指标)', value: 'STOCHRSI', category: 'oscillator' },
  { label: 'ULTOSC(终极振荡指标)', value: 'ULTOSC', category: 'oscillator' },
  { label: 'CCI(顺势指标)', value: 'CCI', category: 'oscillator' },
  { label: 'DX(趋向指标)', value: 'DX', category: 'oscillator' },
  { label: 'TRIX(三重指数平滑平均线)', value: 'TRIX', category: 'oscillator' },
  { label: 'APO(绝对价格振荡指标)', value: 'APO', category: 'oscillator' },
  { label: 'PPO(百分比价格振荡指标)', value: 'PPO', category: 'oscillator' },
  // 成交量指标
  { label: 'AD(累积/派发线)', value: 'AD', category: 'volume' },
  { label: 'ADOSC(累积/派发振荡指标)', value: 'ADOSC', category: 'volume' },
  { label: 'OBV(能量潮)', value: 'OBV', category: 'volume' },
  // 动量指标
  { label: 'MOM(动量)', value: 'MOM', category: 'momentum' },
  { label: 'ROC(变动率)', value: 'ROC', category: 'momentum' },
  { label: 'ROCP(变动率百分比)', value: 'ROCP', category: 'momentum' },
  { label: 'ROCR(变动率比值)', value: 'ROCR', category: 'momentum' },
  { label: 'ROCR100(变动率比值*100)', value: 'ROCR100', category: 'momentum' },
  { label: 'MFI(资金流量指标)', value: 'MFI', category: 'momentum' },
  // 波动率指标
  { label: 'ATR(真实波幅)', value: 'ATR', category: 'volatility' },
  { label: 'NATR(归一化真实波幅)', value: 'NATR', category: 'volatility' },
  { label: 'STDDEV(标准差)', value: 'STDDEV', category: 'volatility' },
  // 周期指标
  { label: 'DPO(区间震荡线)', value: 'DPO', category: 'cycle' },
  { label: 'HT_DCPERIOD(希尔伯特周期)', value: 'HT_DCPERIOD', category: 'cycle' },
  { label: 'HT_SINE(希尔伯特正弦波)', value: 'HT_SINE', category: 'cycle' },
  { label: 'HT_TRENDMODE(希尔伯特趋势模式)', value: 'HT_TRENDMODE', category: 'cycle' }
])

// Alpha因子模板
const factorTemplates = ref([
  { template_id: 'alpha158_1', name: 'Alpha158-基础', description: '经典158维因子' },
  { template_id: 'alpha158_2', name: 'Alpha158-扩展', description: '扩展因子集' },
  { template_id: 'alpha360_1', name: 'Alpha360-基础', description: '360维因子' },
])

// 清空选择
const clearSelection = () => {
  selectedIndicators.value = []
  selectedFactorTemplate.value = ''
  customFactorExpression.value = ''
}

// 移除指标
const removeIndicator = (ind: string) => {
  selectedIndicators.value = selectedIndicators.value.filter(i => i !== ind)
}

// 获取指标标签
const getIndicatorLabel = (val: string) => {
  const ind = allIndicators.value.find(i => i.value === val)
  return ind ? ind.label : val
}

// 技术指标分组（150+指标）
const indicatorGroups = [
  {
    label: '趋势指标',
    labelEn: 'Trend Indicators',
    options: [
      { label: '移动平均线', value: 'MA' },
      { label: '指数移动平均', value: 'EMA' },
      { label: '布林带', value: 'BOLL' },
      { label: '抛物线指标', value: 'SAR' },
      { label: '自适应移动平均', value: 'KAMA' },
      { label: '三重指数平均', value: 'TRIX' },
    ]
  },
  {
    label: '震荡指标',
    labelEn: 'Oscillators',
    options: [
      { label: '相对强弱指数', value: 'RSI' },
      { label: '随机指标', value: 'KDJ' },
      { label: '顺势指标', value: 'CCI' },
      { label: 'MACD', value: 'MACD' },
      { label: '威廉指标', value: 'WR' },
      { label: '能量潮', value: 'OBV' },
    ]
  },
  {
    label: '动量指标',
    labelEn: 'Momentum',
    options: [
      { label: '动量指标', value: 'MOM' },
      { label: '变化率指标', value: 'ROC' },
      { label: '乖离率', value: 'BIAS' },
      { label: '阿隆指标', value: 'AROON' },
    ]
  },
  {
    label: '波动率指标',
    labelEn: 'Volatility',
    options: [
      { label: '平均真实波幅', value: 'ATR' },
      { label: '标准差', value: 'STDDEV' },
      { label: '历史波动率', value: 'HV' },
    ]
  },
  {
    label: '成交量指标',
    labelEn: 'Volume',
    options: [
      { label: '成交量移动平均', value: 'VOL_MA' },
      { label: '成交量比率', value: 'VR' },
      { label: '价量趋势', value: 'PVT' },
    ]
  },
  {
    label: '周期指标',
    labelEn: 'Cycle',
    options: [
      { label: '去趋势价格震荡', value: 'DPO' },
      { label: '斐波那契周期', value: 'FIB' },
    ]
  },
]

// 计算函数
const runCalculation = async () => {
  if (!taskId.value) return
  isCalculating.value = true
  try {
    const hasFactors = selectedCalcTypes.value.length > 0
    const hasIndicators = selectedIndicators.value.length > 0
    if (!hasFactors && !hasIndicators) {
      ElMessage.warning(isZh.value ? '请至少选择一个计算类型' : 'Please select at least one calculation type')
      return
    }

    // 创建新任务
    const newTask: CalculationTask = {
      task_id: `task_${Date.now()}`,
      expression: selectedCalcTypes.value.join(', ') + (selectedIndicators.value.length > 0 ? ` + ${selectedIndicators.value.length} indicators` : ''),
      status: 'running',
      progress: 0,
      created_at: new Date().toLocaleString()
    }
    calculationTasks.value.unshift(newTask)

    console.log('Factor calculation:', selectedCalcTypes.value, customFactorExpression.value)
    console.log('Indicator calculation:', selectedIndicators.value)

    // 模拟计算进度（每200ms更新一次，更平滑）
    const progressInterval = setInterval(() => {
      // 随机增加进度，但确保最终能达到100%
      const remaining = 100 - newTask.progress
      const increment = remaining > 20 ? Math.random() * 15 + 5 : remaining
      newTask.progress = Math.min(100, newTask.progress + increment)

      // 强制触发Vue响应式更新
      calculationTasks.value = [...calculationTasks.value]

      if (newTask.progress >= 100) {
        newTask.progress = 100
        newTask.status = 'completed'
        clearInterval(progressInterval)

        // 自动显示结果
        viewTaskResult(newTask.task_id)
        ElMessage.success(isZh.value ? '计算完成' : 'Calculation complete')
      }
    }, 200)
  } catch (error: any) {
    ElMessage.error(error.message || (isZh.value ? '计算失败' : 'Calculation failed'))
    // 标记任务为失败
    if (calculationTasks.value.length > 0) {
      calculationTasks.value[0].status = 'failed'
    }
  } finally {
    isCalculating.value = false
  }
}

// 监听 currentTask 变化，更新本地 periods
watch(() => currentTask.value?.periods, (newVal) => {
  if (newVal && newVal.length > 0) {
    periods.value = newVal
  }
})

// 周期变化时更新 taskStore
watch(periods, (newVal) => {
  const task = taskStore[taskId.value] || taskStore['default']
  if (task) {
    task.periods = newVal
  }
}, { deep: true })

const isZh = computed(() => appStore.language === 'zh')

// 任务标题（可编辑）
const taskTitle = ref(currentTask.value?.title || '')

// 监听 currentTask 变化，更新 taskTitle
watch(() => currentTask.value?.title, (newTitle) => {
  if (newTitle) {
    taskTitle.value = newTitle
  }
})

// 更新任务标题
const updateTaskTitle = () => {
  const task = taskStore[taskId.value]
  if (task && taskTitle.value.trim()) {
    task.title = taskTitle.value
    task.titleZh = taskTitle.value
  }
}

// 阶段模块导航
const currentStageModule = ref('research')

const switchStageModule = (module: string) => {
  currentStageModule.value = module
  console.log('Switching to module:', module)
}

const goBack = () => {
  router.push('/workflow')
}

const navigateStage = (stageId: string) => {
  if (stageId === 'research') return
  if (stageId === 'validation') router.push('/validation/detail')
  if (stageId === 'production') router.push('/production/detail')
}

// 工作流步骤 - 初始全部pending，步骤1为active
const workflowSteps = ref([
  { id: 1, name: 'Data Configuration', nameZh: '数据配置', status: 'active', description: 'Configure data sources and date range', descriptionZh: '配置数据源和日期范围' },
  { id: 2, name: 'Factor Calculation', nameZh: '因子计算', status: 'pending', description: 'Calculate factor values for selected stocks', descriptionZh: '计算选定股票的因子值' },
  { id: 3, name: 'Factor Analysis', nameZh: '因子分析', status: 'pending', description: 'Analyze factor performance using IC/IR metrics', descriptionZh: '使用IC/IR指标分析因子表现' },
  { id: 4, name: 'Factor Evaluation', nameZh: '因子评估', status: 'pending', description: 'Evaluate factor effectiveness', descriptionZh: '评估因子有效性' },
  { id: 5, name: 'Model Training', nameZh: '模型训练', status: 'pending', description: 'Train ML models with selected factors', descriptionZh: '使用选定因子训练ML模型' },
  { id: 6, name: 'Feasibility Check', nameZh: '可行性检查', status: 'pending', description: 'Check model feasibility for validation', descriptionZh: '检查模型是否可用于验证' }
])

const currentStep = ref(1)

const currentStepData = computed(() => {
  const step = workflowSteps.value.find(s => s.id === currentStep.value)
  if (!step) return null
  return {
    ...step,
    displayName: isZh.value ? step.nameZh : step.name
  }
})

// 是否可以完成当前步骤
const canCompleteStep = computed(() => {
  const step = workflowSteps.value.find(s => s.id === currentStep.value)
  return step?.status === 'active'
})

const selectStep = (stepId: number) => {
  // 允许选择所有步骤
  const step = workflowSteps.value.find(s => s.id === stepId)
  if (step) {
    currentStep.value = stepId
    updateTabsForStep(stepId)
  }
}

// 完成当前步骤
const completeCurrentStep = () => {
  const step = workflowSteps.value.find(s => s.id === currentStep.value)
  if (step) {
    step.status = 'completed'
    // 激活下一个步骤
    const nextStep = workflowSteps.value.find(s => s.id === currentStep.value + 1)
    if (nextStep) {
      nextStep.status = 'active'
      currentStep.value = nextStep.id
      updateTabsForStep(nextStep.id)
    }
  }
}

const getStepStatusText = (status: string) => {
  const statusMapZh: Record<string, string> = {
    completed: '已完成',
    active: '进行中',
    pending: '待处理'
  }
  const statusMapEn: Record<string, string> = {
    completed: 'Completed',
    active: 'In Progress',
    pending: 'Pending'
  }
  return (isZh.value ? statusMapZh[status] : statusMapEn[status]) || status
}

// Tabs相关
const currentTab = ref('overview')
const currentTabs = ref([
  { id: 'overview', name: 'Overview', nameZh: '概览' },
  { id: 'ic-ir', name: 'IC/IR Analysis', nameZh: 'IC/IR分析' },
  { id: 'correlation', name: 'Correlation', nameZh: '相关性' },
  { id: 'distribution', name: 'Distribution', nameZh: '分布' }
])

const switchTab = (tabId: string) => {
  currentTab.value = tabId
}

const updateTabsForStep = (stepId: number) => {
  const tabConfigs: Record<number, { id: string, name: string, nameZh: string, icon?: any }[]> = {
    1: [
      { id: 'overview', name: 'Overview', nameZh: '概览', icon: Odometer },
      { id: 'sources', name: 'Data Sources', nameZh: '数据源', icon: Folder },
      { id: 'cache', name: 'Cache Stats', nameZh: '缓存统计', icon: Box }
    ],
    2: [
      { id: 'overview', name: 'Overview', nameZh: '概览', icon: Odometer },
      { id: 'templates', name: 'Templates', nameZh: '模板', icon: Document },
      { id: 'custom', name: 'Custom Factors', nameZh: '自定义因子', icon: DataLine }
    ],
    3: [
      { id: 'overview', name: 'Overview', nameZh: '概览', icon: Odometer },
      { id: 'ic-ir', name: 'IC/IR Analysis', nameZh: 'IC/IR分析', icon: TrendCharts },
      { id: 'correlation', name: 'Correlation', nameZh: '相关性', icon: Connection },
      { id: 'distribution', name: 'Distribution', nameZh: '分布', icon: Histogram }
    ],
    4: [
      { id: 'overview', name: 'Overview', nameZh: '概览', icon: Odometer },
      { id: 'ranking', name: 'Factor Ranking', nameZh: '因子排名', icon: TrendCharts },
      { id: 'backtest', name: 'Group Backtest', nameZh: '分组回测', icon: DataLine }
    ],
    5: [
      { id: 'overview', name: 'Overview', nameZh: '概览', icon: Odometer },
      { id: 'config', name: 'Configuration', nameZh: '配置', icon: Document },
      { id: 'training', name: 'Training Status', nameZh: '训练状态', icon: TrendCharts }
    ],
    6: [
      { id: 'overview', name: 'Overview', nameZh: '概览', icon: Odometer },
      { id: 'report', name: 'Feasibility Report', nameZh: '可行性报告', icon: Document },
      { id: 'export', name: 'Export Model', nameZh: '导出模型', icon: Box }
    ]
  }
  currentTabs.value = tabConfigs[stepId] || currentTabs.value
  currentTab.value = currentTabs.value[0]?.id || 'overview'
}

// 统计数据
const stats = reactive({
  totalFactors: 168,
  icMean: 0.045,
  irRatio: 0.78,
  qualifiedCount: 45,
  passRate: 26.8,
  progress: 67
})

// 顶部因子 - 只保留通过的因子
const topFactors = ref<FactorResult[]>([
  { factor_name: 'MA60_Cross_Price', ic: 0.058, ir: 0.92, t_stat: 3.45, p_value: 0.001, status: 'pass' },
  { factor_name: 'RSM60_Std_Dev', ic: 0.052, ir: 0.85, t_stat: 3.12, p_value: 0.002, status: 'pass' },
  { factor_name: 'ROC20_Return', ic: 0.049, ir: 0.78, t_stat: 2.89, p_value: 0.004, status: 'pass' },
  { factor_name: 'Beta60_Price', ic: 0.022, ir: 0.45, t_stat: 1.56, p_value: 0.12, status: 'fail' },
  { factor_name: 'VOL30_Volume', ic: 0.041, ir: 0.72, t_stat: 2.67, p_value: 0.008, status: 'pass' }
])

// 将topFactors转换为右侧因子库显示格式
const topFactorsForDisplay = computed(() => {
  return topFactors.value.map(f => ({
    name: f.factor_name,
    ic: f.ic,
    ir: f.ir,
    type: 'analysis' as const,
    typeZh: '已分析' as const,
    category: 'result' as const
  }))
})

// 只传递有效的因子（状态为pass）给下游步骤
const validFactors = computed(() => topFactors.value.filter(f => f.status === 'pass'))

// 加载因子列表并更新topFactors
const loadFactorList = async () => {
  try {
    const response = await factorApi.getFactorList()
    if (response.data?.factors && response.data.factors.length > 0) {
      // 将API返回的因子转换为topFactors格式
      topFactors.value = response.data.factors.map((f: any) => ({
        factor_name: f.factor_name || f.name || f,
        ic: f.ic || 0,
        ir: f.ir || 0,
        t_stat: f.t_stat || 0,
        p_value: f.p_value || 1,
        status: (f.ic && f.ic > 0.03) ? 'pass' : 'fail'
      }))
      console.log('因子列表已更新:', topFactors.value.length)
    }
  } catch (error) {
    console.warn('加载因子列表失败，使用默认数据:', error)
  }
}

// IC/IR配置
const icConfig = reactive({
  method: 'spearman' as 'pearson' | 'spearman',
  threshold: 0.03,
  targetPeriod: 1,
  includeAlpha158: true,
  includeAlpha360: false,
  includeCustom: true
})

// IC计算方法选项
const icMethodOptions = computed(() => [
  { value: 'pearson', label: isZh.value ? '皮尔逊相关' : 'Pearson Correlation' },
  { value: 'spearman', label: isZh.value ? '斯皮尔曼秩相关' : 'Spearman Rank Correlation' }
])

// 相关性配置
const correlationThreshold = ref(0.8)
const correlationMethod = ref<'pearson' | 'spearman'>('pearson')

// 因子库质量雷达图
const factorQualityRadarRef = ref<HTMLElement>()

// 因子库质量雷达图数据 - 供 FactorQualityRadar 组件使用
const factorQualityRadarIndicator = computed(() => [
  { name: isZh.value ? '平均IC' : 'Avg IC', max: 100 },
  { name: isZh.value ? 'IR比率' : 'IR Ratio', max: 100 },
  { name: isZh.value ? '通过率' : 'Pass Rate', max: 100 },
  { name: isZh.value ? '因子数量' : 'Factor Count', max: 100 }
])

// 因子库质量原始值 - 供 FactorQualityRadar 组件显示
const factorQualityRadarIndicatorValues = computed(() => [
  stats.icMean > 0 ? stats.icMean : 0,
  stats.irRatio > 0 ? stats.irRatio : 0,
  stats.passRate > 0 ? stats.passRate : 0,
  Math.round(stats.totalFactors)
])

const factorQualityRadarData = computed(() => [
  {
    name: isZh.value ? '当前因子库' : 'Current',
    value: factorQualityData.value,
    color: '#409ee1',
    areaColor: 'rgba(64, 158, 225, 0.3)',
    lineType: 'solid' as const
  },
  {
    name: isZh.value ? '行业基准' : 'Benchmark',
    value: [60, 55, 70, 80],
    color: '#ff9800',
    areaColor: 'rgba(255, 152, 0, 0.2)',
    lineType: 'dashed' as const
  }
])

// 个体因子综合评估数据 - 供 FactorEvaluationCard 组件使用
const factorEvaluationIndicator = computed(() => [
  { name: isZh.value ? 'IC均值' : 'IC Mean', max: 100 },
  { name: isZh.value ? 'IC标准差' : 'IC Std', max: 100 },
  { name: isZh.value ? 'IC最大值' : 'IC Max', max: 100 },
  { name: isZh.value ? 'IC最小值' : 'IC Min', max: 100 },
  { name: isZh.value ? 'IR值' : 'IR', max: 100 },
  { name: isZh.value ? '正IC比率' : 'IC+ Ratio', max: 100 },
  { name: isZh.value ? 't统计量' : 't-Stat', max: 100 },
  { name: isZh.value ? 'p值' : 'p-Value', max: 100 },
  { name: isZh.value ? '单调性' : 'Monotonicity', max: 100 },
  { name: isZh.value ? '稳定性' : 'Stability', max: 100 }
])

const factorEvaluationIndicatorValues = computed(() => [
  individualFactorData.value.ic_mean,                                    // IC均值
  individualFactorData.value.ic_std,                                    // IC标准差
  individualFactorData.value.ic_max,                                    // IC最大值
  individualFactorData.value.ic_min,                                    // IC最小值
  individualFactorData.value.ir,                                        // IR值
  individualFactorData.value.ic_positive_ratio * 100,                  // 正IC比率（转为%）
  individualFactorData.value.t_stat,                                     // t统计量
  individualFactorData.value.p_value,                                   // p值
  individualFactorData.value.monotonicity_score * 100,                  // 单调性（转为%）
  individualFactorData.value.stability_score * 100                      // 稳定性（转为%）
])

const factorEvaluationRadarData = computed(() => [
  {
    name: isZh.value ? '当前因子' : 'Current',
    value: [
      normalizeIC(individualFactorData.value.ic_mean),
      normalizeStd(individualFactorData.value.ic_std),
      normalizeRange(individualFactorData.value.ic_max, -1, 1),
      normalizeAbsMin(individualFactorData.value.ic_min),
      normalizeRange(individualFactorData.value.ir, -2, 2),
      individualFactorData.value.ic_positive_ratio * 100,
      normalizeRange(individualFactorData.value.t_stat, 0, 5),
      Math.max(0, (1 - individualFactorData.value.p_value / 0.05) * 100),
      individualFactorData.value.monotonicity_score * 100,
      individualFactorData.value.stability_score * 100
    ],
    color: '#409ee1',
    areaColor: 'rgba(64, 158, 225, 0.3)',
    lineType: 'solid' as const
  },
  {
    name: isZh.value ? '行业基准' : 'Benchmark',
    value: [60, 55, 65, 45, 55, 70, 50, 60, 60, 55],
    color: '#ff9800',
    areaColor: 'rgba(255, 152, 0, 0.2)',
    lineType: 'dashed' as const
  }
])

// 个体因子评估雷达图（IC/IR分析页）
const individualFactorRadarRef = ref<HTMLElement>()

// 个体因子IC/IR数据（从后端获取）
const individualFactorData = ref({
  ic_mean: 0,
  ic_std: 0,
  ic_min: 0,
  ic_max: 0,
  ir: 0,
  ic_positive_ratio: 0,
  t_stat: 0,
  p_value: 0,
  monotonicity_score: 0,  // 单调性得分（需要后端支持）
  stability_score: 0      // 稳定性得分（需要后端支持）
})

// 归一化辅助函数
// IC均值：使用绝对值，越大越好（无论正负）
const normalizeIC = (value: number) => Math.max(0, Math.min((Math.abs(value) / 0.05) * 80, 100))  // IC 5% = 80分
// IC标准差：范围0-0.35，越小越好
const normalizeStd = (value: number) => Math.max(0, Math.min((1 - value / 0.35) * 100, 100))
const normalizeRange = (value: number, min: number, max: number) => Math.max(0, (Math.abs(value) / Math.abs(max)) * 100)
const normalizeAbs = (value: number, max: number) => Math.min((Math.abs(value) / max) * 100, 100)
// p值：使用对数归一化
const normalizePValue = (value: number) => Math.max(0, Math.min((-Math.log10(Math.max(value, 1e-10)) / 2) * 100, 100))
const normalizeAbsMin = (value: number) => Math.min((1 - Math.abs(value)) * 100, 100)  // IC最小值绝对值越小越好

// 综合评分计算（10个指标的加权平均）
const totalEvaluationScore = computed(() => {
  const scores = [
    normalizeIC(individualFactorData.value.ic_mean),           // IC均值
    normalizeStd(individualFactorData.value.ic_std),           // IC标准差
    normalizeRange(individualFactorData.value.ic_max, -1, 1),  // IC最大值
    normalizeAbsMin(individualFactorData.value.ic_min),        // IC最小值
    normalizeRange(individualFactorData.value.ir, -2, 2),      // IR值
    individualFactorData.value.ic_positive_ratio * 100,        // 正IC比率
    normalizeAbs(individualFactorData.value.t_stat, 5),        // t统计量
    normalizePValue(individualFactorData.value.p_value),       // p值
    individualFactorData.value.monotonicity_score * 100,       // 单调性
    individualFactorData.value.stability_score * 100           // 稳定性
  ]

  // 加权平均：IC均值(15%) + IC标准差(10%) + IR(15%) + 正IC比率(10%) + t统计量(10%) + p值(5%) + 单调性(15%) + 稳定性(20%)
  const weights = [15, 10, 5, 5, 15, 10, 10, 5, 15, 20]
  let totalWeight = 0
  let weightedSum = 0

  scores.forEach((score, i) => {
    weightedSum += score * weights[i]
    totalWeight += weights[i]
  })

  // 确保评分不低于0
  return Math.max(0, weightedSum / totalWeight)
})

// 因子评估综合评分底板样式（根据分数动态计算）
const evaluationScoreStyle = computed(() => {
  const color = getFactorQualityColor(totalEvaluationScore.value)
  return {
    background: `linear-gradient(135deg, ${color}26 0%, rgba(30, 34, 45, 0.9) 100%)`,
    borderColor: `${color}4d`
  }
})

// 获取评分等级
const getScoreLevel = (score: number): string => {
  if (score > 100) return isZh.value ? '卓越' : 'Excellent'
  if (score >= 80) return isZh.value ? '优秀' : 'Outstanding'
  if (score >= 60) return isZh.value ? '良好' : 'Good'
  if (score >= 40) return isZh.value ? '一般' : 'Average'
  return isZh.value ? '较差' : 'Poor'
}

// 根据分数获取星星数量 (1-5星)
const getStarCount = (score: number): number => {
  if (score >= 90) return 5
  if (score >= 75) return 4
  if (score >= 55) return 3
  if (score >= 35) return 2
  return 1
}

// 根据分数获取字母等级
const getLetterGrade = (score: number): string => {
  if (score >= 95) return 'A+'
  if (score >= 85) return 'A'
  if (score >= 75) return 'B+'
  if (score >= 65) return 'B'
  if (score >= 55) return 'C+'
  if (score >= 45) return 'C'
  if (score >= 35) return 'D'
  return 'F'
}

// 因子库综合评分底板样式（根据分数动态计算）
const factorQualityScoreStyle = computed(() => {
  const color = getFactorQualityColor(factorLibraryTotalScore.value)
  return {
    background: `linear-gradient(135deg, ${color}26 0%, rgba(30, 34, 45, 0.9) 100%)`,
    borderColor: `${color}4d`
  }
})

// 因子类型分组
const groupedFactors = computed(() => {
  const groups: Record<string, any[]> = {
    alpha158: [],
    alpha360: [],
    base: [],
    technical: [],
    custom: []
  }

  // 根据当前Tab选择数据源
  const sourceFactors = factorListTab.value === 'favorites'
    ? topFactors.value.filter((f: any) => favoriteFactors.value.includes(f.factor_name))
    : topFactors.value

  sourceFactors.forEach((factor: any) => {
    const name = factor.factor_name.toLowerCase()
    if (name.startsWith('alpha158')) {
      groups.alpha158.push(factor)
    } else if (name.startsWith('alpha360')) {
      groups.alpha360.push(factor)
    } else if (['pe_ratio', 'pb_ratio', 'ps_ratio', 'market_cap', 'volume', 'turnover', 'price_change', 'return', 'volatility', 'momentum', 'beta', 'alpha'].includes(name)) {
      groups.base.push(factor)
    } else if (['ma5', 'ma10', 'ma20', 'ma60', 'ma120', 'ma250', 'rsi', 'macd', 'boll', 'kdj', 'cci', 'atr', 'obv', 'adx', 'williams_r', 'stoch'].includes(name)) {
      groups.technical.push(factor)
    } else {
      groups.custom.push(factor)
    }
  })

  return groups
})

// 因子类型标签
const getFactorTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    alpha158: 'Alpha158',
    alpha360: 'Alpha360',
    base: isZh.value ? '基础因子' : 'Base',
    technical: isZh.value ? '技术指标' : 'Technical',
    custom: isZh.value ? '自定义因子' : 'Custom'
  }
  return labels[type] || type
}

// 全局索引
const getGlobalIndex = (type: string, localIndex: number) => {
  const typeOrder = ['alpha158', 'alpha360', 'base', 'technical', 'custom']
  let globalIndex = 0
  for (const t of typeOrder) {
    if (t === type) return globalIndex + localIndex
    globalIndex += groupedFactors.value[t]?.length || 0
  }
  return localIndex
}

// 因子颜色类型（根据名称自动识别）
const getFactorColorClass = (factorName: string) => {
  const name = factorName.toLowerCase()

  // 动量因子 - 绿色
  if (name.includes('momentum') || name.includes('return') || name.includes('ma') || name.includes('roc') || name.includes('trend')) {
    return 'factor-momentum'
  }
  // 波动率因子 - 橙色
  if (name.includes('volatility') || name.includes('std') || name.includes('var') || name.includes('atr')) {
    return 'factor-volatility'
  }
  // 成交量因子 - 蓝色
  if (name.includes('volume') || name.includes('liquidity') || name.includes('turnover') || name.includes('obv')) {
    return 'factor-volume'
  }
  // 技术指标 - 紫色
  if (name.includes('rsi') || name.includes('macd') || name.includes('boll') || name.includes('kdj') || name.includes('cci') || name.includes('adx') || name.includes('williams')) {
    return 'factor-technical'
  }
  // Alpha因子 - 红色
  if (name.startsWith('alpha158') || name.startsWith('alpha360')) {
    return 'factor-alpha'
  }
  // 其他 - 灰色
  return 'factor-other'
}

// 因子库质量数据
const factorQualityData = computed(() => {
  // 归一化到0-100
  const icScore = Math.min((stats.icMean / 0.05) * 80, 100)  // IC 5% = 80分
  const irScore = Math.min((stats.irRatio / 0.8) * 80, 100)  // IR 0.8 = 80分
  const passScore = Math.min(stats.passRate * 1.2, 100)  // 通过率直接映射
  const countScore = Math.min((stats.totalFactors / 200) * 80, 100)  // 200个因子 = 80分

  return [icScore, irScore, passScore, countScore]
})

// 因子库综合评分（加权平均）
const factorLibraryTotalScore = computed(() => {
  const scores = factorQualityData.value
  // 权重: IC(30%) + IR(30%) + 通过率(25%) + 因子数量(15%)
  const weights = [30, 30, 25, 15]
  let weightedSum = 0
  scores.forEach((score, i) => {
    weightedSum += score * weights[i]
  })
  return weightedSum / 100
})

// 因子库质量颜色（与综合指标分析一致）
const getFactorQualityColor = (score: number) => {
  if (score > 100) return '#8b5cf6'  // 紫色=卓越
  if (score >= 80) return '#ef5350'   // 红色=优秀
  if (score >= 60) return '#f97316'   // 橙红色=良好
  if (score >= 40) return '#2962ff'   // 蓝色=一般
  return '#26a69a'                     // 绿色=差
}

// 行业基准数据
const factorQualityBenchmark = computed(() => {
  // 行业标准基准值
  const icBenchmark = 0.03  // IC 3% 为行业标准
  const irBenchmark = 0.4   // IR 0.4 为行业标准
  const passBenchmark = 30  // 通过率 30% 为行业标准
  const countBenchmark = 158 // Alpha158 基准

  const icScore = Math.min((icBenchmark / 0.05) * 80, 100)
  const irScore = Math.min((irBenchmark / 0.8) * 80, 100)
  const passScore = Math.min(passBenchmark * 1.2, 100)
  const countScore = Math.min((countBenchmark / 200) * 80, 100)

  return [icScore, irScore, passScore, countScore]
})

// 初始化雷达图
const initFactorQualityRadar = () => {
  if (!factorQualityRadarRef.value) return

  const chart = echarts.init(factorQualityRadarRef.value)

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e222d',
      borderColor: '#3a3f4b',
      textStyle: { color: '#d1d4dc' }
    },
    legend: {
      data: [isZh.value ? '当前因子库' : 'Current', isZh.value ? '行业基准' : 'Benchmark'],
      right: 10,
      top: 10,
      orient: 'vertical',
      textStyle: { color: '#d1d4dc', fontSize: 11 }
    },
    radar: {
      center: ['45%', '50%'],
      radius: '60%',
      indicator: [
        { name: isZh.value ? '平均IC' : 'Avg IC', max: 100 },
        { name: isZh.value ? 'IR比率' : 'IR Ratio', max: 100 },
        { name: isZh.value ? '通过率' : 'Pass Rate', max: 100 },
        { name: isZh.value ? '因子数量' : 'Factor Count', max: 100 }
      ],
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: '#d1d4dc',
        fontSize: 12
      },
      splitLine: {
        lineStyle: { color: '#3a3f4b' }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(30, 34, 45, 0.2)', 'rgba(30, 34, 45, 0.4)', 'rgba(30, 34, 45, 0.6)', 'rgba(30, 34, 45, 0.8)']
        }
      },
      axisLine: {
        lineStyle: { color: '#3a3f4b' }
      }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: factorQualityData.value,
            name: isZh.value ? '当前因子库' : 'Current',
            areaStyle: {
              color: 'rgba(64, 158, 225, 0.3)'
            },
            lineStyle: {
              color: '#409ee1',
              width: 2
            },
            itemStyle: {
              color: '#409ee1'
            }
          },
          {
            value: factorQualityBenchmark.value,
            name: isZh.value ? '行业基准' : 'Benchmark',
            areaStyle: {
              color: 'rgba(255, 152, 0, 0.2)'
            },
            lineStyle: {
              color: '#ff9800',
              width: 2,
              type: 'dashed'
            },
            itemStyle: {
              color: '#ff9800'
            }
          }
        ]
      }
    ]
  }

  chart.setOption(option)
}

// 个体因子综合评估雷达图（10个指标）
const initIndividualFactorRadar = () => {
  if (!individualFactorRadarRef.value) return

  const chart = echarts.init(individualFactorRadarRef.value)

  // 将原始值归一化到0-100分
  const normalizeValue = (value: number, max: number, min: number = 0, inverse: boolean = false) => {
    const normalized = ((value - min) / (max - min)) * 100
    const clamped = Math.max(0, Math.min(100, normalized))
    return inverse ? (100 - clamped) : clamped
  }

  // 10个指标的归一化值
  const radarValues = [
    normalizeValue(individualFactorData.value.ic_mean, 0.1, -0.1),           // IC均值: [-0.1, 0.1] -> [0, 100]
    normalizeValue(individualFactorData.value.ic_std, 0.15, 0, true),        // IC标准差: 越小越好，反转
    normalizeValue(individualFactorData.value.ic_max, 1, -1),                // IC最大值: [-1, 1] -> [0, 100]
    normalizeValue(1 - Math.abs(individualFactorData.value.ic_min), 1, 0),    // IC最小值: 绝对值越小越好
    normalizeValue(individualFactorData.value.ir, 2, -2),                    // IR值: [-2, 2] -> [0, 100]
    normalizeValue(individualFactorData.value.ic_positive_ratio, 1, 0),      // 正IC比率: [0, 1] -> [0, 100]
    normalizeValue(Math.abs(individualFactorData.value.t_stat), 5, 0),       // t统计量绝对值: [0, 5] -> [0, 100]
    normalizeValue(individualFactorData.value.p_value, 0.05, 0, true),       // p值: 越小越好，反转
    normalizeValue(individualFactorData.value.monotonicity_score, 1, 0),     // 单调性得分: [0, 1] -> [0, 100]
    normalizeValue(individualFactorData.value.stability_score, 1, 0)         // 稳定性得分: [0, 1] -> [0, 100]
  ]

  // 行业基准值（标准化参考）
  const benchmarkValues = [
    normalizeValue(0.03, 0.1, -0.1),       // IC均值基准: 3%
    normalizeValue(0.08, 0.15, 0, true),   // IC标准差基准: 0.08
    normalizeValue(0.3, 1, -1),            // IC最大值基准
    normalizeValue(1 - 0.3, 1, 0),          // IC最小值基准: 绝对值越小越好，0.3 -> 0.7
    normalizeValue(0.5, 2, -2),            // IR基准: 0.5
    normalizeValue(0.55, 1, 0),            // 正IC比率基准: 55%
    normalizeValue(2.0, 5, 0),             // t统计量基准
    normalizeValue(0.02, 0.05, 0, true),   // p值基准: 0.02
    normalizeValue(0.6, 1, 0),             // 单调性基准: 0.6
    normalizeValue(0.7, 1, 0)              // 稳定性基准: 0.7
  ]

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e222d',
      borderColor: '#3a3f4b',
      textStyle: { color: '#d1d4dc' },
      formatter: (params: any) => {
        const labels = [
          isZh.value ? 'IC均值' : 'IC Mean',
          isZh.value ? 'IC标准差' : 'IC Std',
          isZh.value ? 'IC最大值' : 'IC Max',
          isZh.value ? 'IC最小值' : 'IC Min',
          isZh.value ? 'IR值' : 'IR',
          isZh.value ? '正IC比率' : 'IC+ Ratio',
          isZh.value ? 't统计量' : 't-Stat',
          isZh.value ? 'p值' : 'p-Value',
          isZh.value ? '单调性' : 'Monotonicity',
          isZh.value ? '稳定性' : 'Stability'
        ]
        const rawValues = [
          individualFactorData.value.ic_mean.toFixed(4),
          individualFactorData.value.ic_std.toFixed(4),
          individualFactorData.value.ic_max.toFixed(4),
          individualFactorData.value.ic_min.toFixed(4),
          individualFactorData.value.ir.toFixed(4),
          (individualFactorData.value.ic_positive_ratio * 100).toFixed(1) + '%',
          individualFactorData.value.t_stat.toFixed(4),
          // p值使用科学计数法显示
          individualFactorData.value.p_value < 0.0001
            ? individualFactorData.value.p_value.toExponential(2)
            : individualFactorData.value.p_value.toFixed(4),
          individualFactorData.value.monotonicity_score.toFixed(2),
          individualFactorData.value.stability_score.toFixed(2)
        ]
        let html = `<div style="padding: 8px;"><strong>${params.name}</strong><br/>`
        labels.forEach((label, i) => {
          html += `<div style="margin-top: 4px;">${label}: ${rawValues[i]}</div>`
        })
        html += '</div>'
        return html
      }
    },
    legend: {
      data: [isZh.value ? '当前因子' : 'Current', isZh.value ? '行业基准' : 'Benchmark'],
      right: 10,
      top: 10,
      orient: 'vertical',
      textStyle: { color: '#d1d4dc', fontSize: 11 }
    },
    radar: {
      center: ['45%', '50%'],
      radius: '60%',
      indicator: [
        { name: isZh.value ? 'IC均值' : 'IC Mean', max: 100 },
        { name: isZh.value ? 'IC标准差' : 'IC Std', max: 100 },
        { name: isZh.value ? 'IC最大值' : 'IC Max', max: 100 },
        { name: isZh.value ? 'IC最小值' : 'IC Min', max: 100 },
        { name: isZh.value ? 'IR值' : 'IR', max: 100 },
        { name: isZh.value ? '正IC比率' : 'IC+ Ratio', max: 100 },
        { name: isZh.value ? 't统计量' : 't-Stat', max: 100 },
        { name: isZh.value ? 'p值' : 'p-Value', max: 100 },
        { name: isZh.value ? '单调性' : 'Monotonicity', max: 100 },
        { name: isZh.value ? '稳定性' : 'Stability', max: 100 }
      ],
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        color: '#d1d4dc',
        fontSize: 11
      },
      splitLine: {
        lineStyle: { color: '#3a3f4b' }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(30, 34, 45, 0.2)', 'rgba(30, 34, 45, 0.3)', 'rgba(30, 34, 45, 0.4)', 'rgba(30, 34, 45, 0.5)', 'rgba(30, 34, 45, 0.6)']
        }
      },
      axisLine: {
        lineStyle: { color: '#3a3f4b' }
      }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: radarValues,
            name: isZh.value ? '当前因子' : 'Current',
            areaStyle: {
              color: 'rgba(239, 83, 80, 0.3)'  // 红色填充
            },
            lineStyle: {
              color: '#ef5350',
              width: 2
            },
            itemStyle: {
              color: '#ef5350'
            }
          },
          {
            value: benchmarkValues,
            name: isZh.value ? '行业基准' : 'Benchmark',
            areaStyle: {
              color: 'rgba(255, 152, 0, 0.2)'  // 橙色填充
            },
            lineStyle: {
              color: '#ff9800',
              width: 2,
              type: 'dashed'
            },
            itemStyle: {
              color: '#ff9800'
            }
          }
        ]
      }
    ]
  }

  chart.setOption(option)
}

// 加载个体因子IC/IR数据
const loadIndividualFactorData = async () => {
  if (!taskId.value) return

  try {
    // 计算默认日期范围（过去1年）
    const endDate = new Date().toISOString().split('T')[0]
    const startDate = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]

    const requestData: any = {
      task_id: taskId.value,
      target_period: icConfig.targetPeriod,
      method: icConfig.method,
      start_date: startDate,
      end_date: endDate
    }

    // 如果选中了具体因子，传入因子名称
    if (selectedFactor.value) {
      requestData.factor_name = selectedFactor.value
    }

    console.log('加载IC/IR数据，请求参数:', requestData)

    const response = await axios.post('/api/v1/research/analysis/ic-ir', requestData)

    if (response.data.code === 200 && response.data.data) {
      const data = response.data.data
      // 更新个体因子数据
      individualFactorData.value = {
        ic_mean: data.ic?.mean || data.ic_mean || 0,
        ic_std: data.ic?.std || data.ic_std || 0,
        ic_min: data.ic?.min || data.ic_min || 0,
        ic_max: data.ic?.max || data.ic_max || 0,
        ir: data.ir || 0,
        ic_positive_ratio: data.ic_positive_ratio || 0,
        t_stat: data.t_stat || 0,
        p_value: data.p_value || 0,
        monotonicity_score: data.monotonicity_score || 0.5,
        stability_score: data.stability_score || 0.5
      }

      // 重新渲染雷达图
      nextTick(() => {
        initIndividualFactorRadar()
      })
    }
  } catch (error: any) {
    console.warn('加载IC/IR数据失败，使用模拟数据:', error.message)
    // 使用模拟数据
    individualFactorData.value = {
      ic_mean: 0.031258,
      ic_std: 0.050849,
      ic_min: -0.15234,
      ic_max: 0.21345,
      ir: 0.614733,
      ic_positive_ratio: 0.7167,
      t_stat: 2.4521,
      p_value: 0.0142,
      monotonicity_score: 0.78,
      stability_score: 0.85
    }
    nextTick(() => {
      initIndividualFactorRadar()
    })
  }
}

// 加载相关性分析数据
const loadCorrelationData = async () => {
  if (!selectedFactor.value || !taskId.value) {
    console.log('相关性分析: 无选中因子或taskId')
    return
  }

  try {
    // 调用相关性分析API，传入选中的因子
    const response = await factorApi.calculateCorrelation(
      [selectedFactor.value],
      0.8
    )
    console.log('相关性数据加载成功:', response.data)
    // TODO: 更新相关性分析图表
  } catch (error: any) {
    console.warn('加载相关性数据失败:', error.message)
  }
}

// 加载分布分析数据
const loadDistributionData = async () => {
  if (!selectedFactor.value || !taskId.value) {
    console.log('分布分析: 无选中因子或taskId')
    return
  }

  try {
    // 调用分布分析API
    const response = await factorApi.getFactorDistribution(
      selectedFactor.value,
      [],
      new Date().toISOString().split('T')[0]
    )
    console.log('分布数据加载成功:', response.data)
    // TODO: 更新分布分析图表
  } catch (error: any) {
    console.warn('加载分布数据失败:', error.message)
  }
}

// 监听步骤切换，步骤变化时初始化相应雷达图
watch(currentStep, () => {
  nextTick(() => {
    if (currentTab.value === 'overview') {
      initFactorQualityRadar()
    } else if (currentTab.value === 'ic-ir') {
      loadIndividualFactorData()
    }
  })
})

// 监听tab切换，切换到overview时初始化雷达图
watch(currentTab, (newTab) => {
  if (newTab === 'overview') {
    nextTick(() => {
      initFactorQualityRadar()
    })
  } else if (newTab === 'ic-ir') {
    // 加载IC/IR分析数据
    loadIndividualFactorData()
  } else if (newTab === 'correlation') {
    // 加载相关性分析数据
    loadCorrelationData()
  } else if (newTab === 'distribution') {
    // 加载分布分析数据
    loadDistributionData()
  }
})



onMounted(() => {
  // 加载因子列表
  loadFactorList()

  if (currentTab.value === 'overview') {
    nextTick(() => {
      initFactorQualityRadar()
    })
  } else if (currentTab.value === 'ic-ir') {
    nextTick(() => {
      loadIndividualFactorData()
    })
  }
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (currentTab.value === 'overview' && factorQualityRadarRef.value) {
      const chart = echarts.getInstanceByDom(factorQualityRadarRef.value)
      chart?.resize()
    }
    if (currentTab.value === 'ic-ir' && individualFactorRadarRef.value) {
      const chart = echarts.getInstanceByDom(individualFactorRadarRef.value)
      chart?.resize()
    }
  })
})

// 分布配置
const distributionConfig = reactive({
  histogram: true,
  qqPlot: true,
  boxPlot: false,
  bins: 50
})

// 因子库
const factorLibrary = ref<(FactorInfo & { typeZh?: string })[]>([
  { name: 'MA60_Cross_Price', type: 'momentum', typeZh: '动量', category: 'alpha158', ic: 0.058, ir: 0.92 },
  { name: 'RSM60_Std_Dev', type: 'volatility', typeZh: '波动率', category: 'alpha158', ic: 0.052, ir: 0.85 },
  { name: 'ROC20_Return', type: 'momentum', typeZh: '动量', category: 'alpha158', ic: 0.049, ir: 0.78 },
  { name: 'VOL30_Volume', type: 'volume', typeZh: '成交量', category: 'alpha158', ic: 0.041, ir: 0.72 },
  { name: 'Beta60_Price', type: 'technical', typeZh: '技术', category: 'alpha158', ic: 0.022, ir: 0.45 },
  { name: 'RSI14_Strength', type: 'technical', typeZh: '技术', category: 'alpha158', ic: 0.038, ir: 0.65 },
  { name: 'MACD_Trend', type: 'technical', typeZh: '技术', category: 'alpha158', ic: 0.035, ir: 0.61 },
  { name: 'Bollinger_Width', type: 'volatility', typeZh: '波动率', category: 'alpha158', ic: 0.032, ir: 0.58 }
])

const selectedFactor = ref<string | null>(null)

const selectFactor = (factor: FactorInfo) => {
  selectedFactor.value = factor.name
}

// 通过因子名称选择因子（用于右侧因子库列表点击）
const selectFactorByName = (factorName: string) => {
  selectedFactor.value = factorName
  console.log('选中因子:', factorName)

  // 不切换tab，保持当前tab，但加载当前tab对应的分析数据
  // 加载该因子的详细分析数据（由watch处理）
}

// 监听选中因子变化，加载详细分析数据
watch(() => selectedFactor.value, (newFactor, oldFactor) => {
  if (newFactor && newFactor !== oldFactor) {
    console.log('选中因子变化:', newFactor, '旧因子:', oldFactor)
    // 根据当前tab加载相应的分析数据
    if (currentTab.value === 'ic-ir') {
      loadIndividualFactorData()
    } else if (currentTab.value === 'correlation') {
      loadCorrelationData()
    } else if (currentTab.value === 'distribution') {
      loadDistributionData()
    }
  }
}, { immediate: false })

// ========== 收藏因子功能 ==========
// 收藏的因子列表 (使用localStorage持久化)
const favoriteFactors = ref<string[]>([])

// 左侧因子列表Tab: 'current' | 'favorites'
const factorListTab = ref<'current' | 'favorites'>('current')

// 从localStorage加载收藏的因子
const loadFavoriteFactors = () => {
  try {
    if (typeof localStorage === 'undefined') return
    const stored = localStorage.getItem('favoriteFactors')
    if (stored) {
      favoriteFactors.value = JSON.parse(stored)
    }
  } catch (e) {
    console.warn('加载收藏因子失败:', e)
  }
}

// 保存收藏的因子到localStorage
const saveFavoriteFactors = () => {
  try {
    if (typeof localStorage === 'undefined') return
    localStorage.setItem('favoriteFactors', JSON.stringify(favoriteFactors.value))
  } catch (e) {
    console.warn('保存收藏因子失败:', e)
  }
}

// 切换因子收藏状态
const toggleFavorite = (factorName: string) => {
  const index = favoriteFactors.value.indexOf(factorName)
  if (index > -1) {
    // 已收藏，取消收藏
    favoriteFactors.value.splice(index, 1)
  } else {
    // 未收藏，添加收藏
    favoriteFactors.value.push(factorName)
  }
  saveFavoriteFactors()
}

// 检查因子是否已收藏
const isFavorited = (factorName: string): boolean => {
  return favoriteFactors.value.includes(factorName)
}

// 初始化加载收藏因子
loadFavoriteFactors()

// 获取因子状态
const getFactorStatus = (ic: number | undefined): string => {
  if (ic === undefined) return 'unknown'
  if (ic >= 0.05) return 'excellent'
  if (ic >= 0.03) return 'good'
  if (ic >= 0) return 'average'
  return 'poor'
}

// 获取因子评分类名
const getFactorScoreClass = (ic: number | undefined): string => {
  return getFactorStatus(ic)
}

// 日期单元格类名（用于自定义日期范围样式）
const getDateCellClass = (data: { date: Date }) => {
  if (!dateRange.value || !Array.isArray(dateRange.value) || dateRange.value.length < 2) {
    return ''
  }
  const cellDate = new Date(data.date)
  const startDate = new Date(dateRange.value[0])
  const endDate = new Date(dateRange.value[1])

  // 设置时间为0点进行比较
  cellDate.setHours(0, 0, 0, 0)
  startDate.setHours(0, 0, 0, 0)
  endDate.setHours(0, 0, 0, 0)

  if (cellDate.getTime() === startDate.getTime()) {
    return 'custom-date-start'
  }
  if (cellDate.getTime() === endDate.getTime()) {
    return 'custom-date-end'
  }
  if (cellDate > startDate && cellDate < endDate) {
    return 'custom-date-inrange'
  }
  return ''
}

// 操作方法
const isAnalyzing = ref(false)
const cardSize = ref<'large' | 'small'>('large')
const cardSizeOptions = computed(() => [
  { value: 'large', label: '', icon: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>' },
  { value: 'small', label: '', icon: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="8" height="8"/><rect x="13" y="3" width="8" height="8"/><rect x="3" y="13" width="8" height="8"/><rect x="13" y="13" width="8" height="8"/></svg>' }
])
const openFactorGroups = ref<string[]>([])

const toggleFactorGroup = (type: string) => {
  const index = openFactorGroups.value.indexOf(type)
  if (index > -1) {
    openFactorGroups.value.splice(index, 1)
  } else {
    openFactorGroups.value.push(type)
  }
}

const runFullAnalysis = async () => {
  isAnalyzing.value = true
  const task = taskStore[taskId.value] || taskStore['default']
  try {
    // 获取因子列表
    const factorsRes = await factorApi.getFactorList()
    const factorNames = factorsRes.data?.factors || []

    // 批量分析因子
    const batchRes = await factorApi.batchAnalyzeFactors(
      factorNames,
      '2024-01-01',
      '2024-12-31',
      '5d'
    )

    const analysisResults = batchRes.data?.factors || []

    // 更新 topFactors (显示所有因子)
    topFactors.value = analysisResults.map((f: any) => ({
      factor_name: f.factor_name,
      ic: f.ic || 0,
      ir: f.ir || 0,
      t_stat: f.t_stat || 0,
      p_value: f.p_value || 1,
      status: f.status || 'fail'
    }))

    // 更新统计数据
    const passCount = analysisResults.filter((f: any) => f.status === 'pass').length
    stats.totalFactors = analysisResults.length
    stats.icMean = analysisResults.reduce((sum: number, f: any) => sum + (f.ic || 0), 0) / analysisResults.length
    stats.irRatio = analysisResults.reduce((sum: number, f: any) => sum + (f.ir || 0), 0) / analysisResults.length
    stats.qualifiedCount = passCount
    stats.passRate = (passCount / analysisResults.length * 100) || 0
    stats.progress = 100
    if (task) task.progress = 100

    // 分析完成后刷新雷达图
    nextTick(() => {
      initFactorQualityRadar()
    })
    isAnalyzing.value = false
  } catch (error) {
    console.error('Analysis failed:', error)
    isAnalyzing.value = false
  }
}

const exportResults = () => {
  console.log('Exporting results...')
}

const calculateICIR = async () => {
  console.log('Calculating IC/IR with config:', icConfig)
}

const generateHeatmap = () => {
  console.log('Generating heatmap...')
}

const removeDuplicates = () => {
  console.log('Removing duplicate factors...')
}

const plotDistribution = () => {
  console.log('Plotting distribution...')
}

const normalizeFactors = () => {
  console.log('Normalizing factors...')
}

const addCustomFactor = () => {
  console.log('Adding custom factor...')
}

const openFactorSettings = () => {
  console.log('Opening factor settings...')
}

// ========== 回测模块数据 ==========
const backtestStats = reactive({
  annualReturn: 18.5,
  sharpeRatio: 1.42,
  maxDrawdown: -12.3,
  winRate: 58.6
})

const backtestConfig = reactive({
  startDate: '2023-01-01',
  endDate: '2024-12-31',
  initialCapital: 1000000,
  commission: 0.0003
})

const isBacktesting = ref(false)

const runBacktest = async () => {
  isBacktesting.value = true
  console.log('Running backtest with config:', backtestConfig)
  // 调用后端回测API
  setTimeout(() => {
    isBacktesting.value = false
  }, 2000)
}

const exportBacktest = () => {
  console.log('Exporting backtest report...')
}

// ========== 信号生成模块数据 ==========
const signalStats = reactive({
  todaySignals: 15,
  buySignals: 10,
  sellSignals: 5,
  accuracy: 65.3
})

const latestSignals = ref([
  { code: '600519', name: '贵州茅台', type: 'buy', strength: 0.85, time: '09:35:12' },
  { code: '000858', name: '五粮液', type: 'buy', strength: 0.72, time: '09:42:08' },
  { code: '600036', name: '招商银行', type: 'sell', strength: 0.68, time: '10:15:33' },
  { code: '000001', name: '平安银行', type: 'buy', strength: 0.61, time: '10:28:45' },
  { code: '601318', name: '中国平安', type: 'sell', strength: 0.55, time: '11:05:22' }
])

const isGenerating = ref(false)

const generateSignals = async () => {
  isGenerating.value = true
  console.log('Generating trading signals...')
  // 调用后端信号生成API
  setTimeout(() => {
    isGenerating.value = false
  }, 2000)
}

const exportSignals = () => {
  console.log('Exporting signals...')
}

// 加载数据
onMounted(async () => {
  try {
    console.log('ResearchDetailView mounted')
  } catch (error) {
    console.error('Failed to load data:', error)
  }
})
</script>

<style>
/* 暂时注释掉所有el-picker相关样式，排查问题 */
/*
* >>> .el-select .el-input__wrapper { ... }
.el-picker-panel { ... }
*/
</style>

<style scoped>
/* 主容器 - 使用固定定位覆盖整个屏幕 */
.research-detail-view {
  --bg-primary: #131722;
  --bg-secondary: #1e222d;
  --bg-tertiary: #2a2e39;
  --text-primary: #d1d4dc;
  --text-secondary: #787b86;
  --accent-blue: #2962ff;
  /* A股颜色规则：红涨绿跌 */
  --color-up: #ef5350;      /* 红色 - 上涨/正面 */
  --color-down: #26a69a;    /* 绿色 - 下跌/负面 */
  --accent-red: #ef5350;    /* 红色 - 保持兼容 */
  --accent-green: #26a69a;  /* 绿色 - 保持兼容 */
  --accent-orange: #ff9800;
  --border-color: #2a2e39;

  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  background: #131722;
  color: #d1d4dc;
  font-size: 13px;
  overflow: hidden;
}

/* 图标样式 */
.icon-sm {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.icon-xs {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}

.icon-check {
  width: 18px;
  height: 18px;
}

.icon-step {
  width: 18px;
  height: 18px;
}

.step-number {
  font-size: 14px;
  font-weight: 700;
}

/* 主容器布局 */
.main-container {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  grid-template-rows: 1fr;
  height: calc(100vh - 56px);
  gap: 1px;
  background: var(--border-color);
}

/* 面板通用样式 */
.panel {
  background: var(--bg-primary);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  background: var(--bg-secondary);
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
}

.panel-actions {
  display: flex;
  gap: 4px;
}

.icon-btn {
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

/* 工作流列表 */
.workflow-list {
  flex: 1;
  overflow-y: auto;
}

.workflow-step {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.workflow-step:hover {
  background: var(--bg-secondary);
}

.workflow-step.selected {
  background: var(--bg-tertiary);
  border-left: 2px solid var(--accent-blue);
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}

.workflow-step.completed .step-icon {
  background: var(--accent-green);
  color: white;
}

.workflow-step.active .step-icon {
  background: var(--accent-blue);
  color: white;
}

.workflow-step.pending .step-icon {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.step-info {
  flex: 1;
}

.step-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.step-status {
  font-size: 11px;
  color: var(--text-secondary);
}

.step-status.completed {
  color: var(--accent-green);
}

/* 主内容区 */
.content-area {
  padding: 24px;
  overflow-y: auto;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

/* Tabs */
.content-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.content-tab {
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-icon {
  width: 14px;
  height: 14px;
}

.content-tab:hover {
  color: var(--text-primary);
}

.content-tab.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
}

.tab-pane {
  display: none;
  padding: 0;
}

.tab-pane.active {
  display: block;
}

/* 因子质量区域 */
.factor-quality-section {
  margin-bottom: 12px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
  padding: 0;

  .summary-card {
    background: var(--bg-secondary, #1e222d);
    padding: 12px;
    border-radius: 8px;
    border: 1px solid var(--border-color, #2a2e39);
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.2s;

    &:hover {
      border-color: var(--accent-blue, #2962ff);
    }

    .card-icon {
      width: 42px;
      height: 42px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      color: white;
      background: linear-gradient(135deg, #2962ff 0%, #1e88e5 100%);

      &.factors-icon {
        background: linear-gradient(135deg, #7c4dff 0%, #651fff 100%);
      }

      &.ic-icon {
        background: linear-gradient(135deg, #2962ff 0%, #1e88e5 100%);
      }

      &.ir-icon {
        background: linear-gradient(135deg, #00bfa5 0%, #00897b 100%);
      }

      &.qualified-icon {
        background: linear-gradient(135deg, #ef5350 0%, #c62828 100%);
      }
    }

    .card-content {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .stat-label {
      font-size: 10px;
      color: var(--text-primary, #d1d4dc);
      margin-bottom: 2px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      line-height: 1.2;
    }

    .stat-value {
      font-size: 18px;
      font-weight: 700;
      color: var(--text-primary, #d1d4dc);
      line-height: 1.2;

      &.positive {
        color: var(--color-up, #ef5350);
      }

      &.negative {
        color: var(--color-down, #26a69a);
      }
    }

    .stat-change {
      font-size: 10px;
      color: var(--text-secondary, #787b86);
      margin-top: 2px;
      line-height: 1.2;
    }
  }
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 14px;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;

  .icon-xs {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
  }
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

/* A股规则：红涨/好，绿跌/坏 */
.stat-value.positive {
  color: var(--color-up);  /* 红色 - 正面 */
}

.stat-value.negative {
  color: var(--color-down);  /* 绿色 - 负面 */
}

.stat-change {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* 因子库质量雷达图 */
.radar-section {
  width: 100%;
  box-sizing: border-box;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.radar-chart-container {
  width: 100%;
  height: 300px;
}

.radar-chart {
  width: 100%;
  height: 100%;
}

/* 质量指标面板 */
.quality-metrics-panel {
  display: flex;
  gap: 0;
  padding: 12px 0;
  align-items: center;
}

/* 质量指标列表 - 行内布局 */
.quality-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 0 0 500px;
}

.quality-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quality-item-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);

  svg {
    width: 16px;
    height: 16px;
  }
}

.quality-item-label {
  font-size: 14px;
  color: var(--text-primary);
  width: 70px;
}

.quality-item-score {
  font-size: 20px;
  font-weight: 700;
  width: 50px;
  text-align: right;
}

.quality-item-bar {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
  overflow: hidden;
  min-width: 80px;
}

.quality-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.quality-item-raw {
  font-size: 12px;
  color: var(--text-secondary);
  width: 50px;
  text-align: right;
}

.quality-metrics-panel .radar-chart-wrapper {
  flex: 1;
  min-width: 300px;
  height: 280px;
}

.quality-metrics-panel .radar-chart-wrapper .radar-chart {
  width: 100%;
  height: 100%;
}

/* 因子库综合评分样式 */
.quality-total-score {
  flex: 0 0 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid;
  margin-left: 16px;
  transition: all 0.3s;
}

.quality-total-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.quality-total-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.quality-total-value {
  font-size: 40px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 8px;
}

/* 星级和字母等级 */
.quality-rating {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}

.star-rating {
  display: flex;
  gap: 2px;

  .star-icon {
    width: 14px;
    height: 14px;
    color: #787b86;

    &.filled {
      color: inherit;
    }
  }
}

.letter-grade {
  font-size: 16px;
  font-weight: 700;
}

.quality-total-bar {
  width: 100%;
  height: 5px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.quality-total-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* 个体因子评估面板样式 */
.single-factor-evaluation-section {
  margin-bottom: 12px;
}

.evaluation-metrics-panel {
  display: flex;
  gap: 0;
  padding: 12px 0;
  align-items: flex-start;
}

/* 评估指标列表 - 两列布局 */
.evaluation-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 24px;
  flex: 0 0 620px;
  padding-bottom: 0;
}

.evaluation-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.evaluation-item-icon {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);

  svg {
    width: 14px;
    height: 14px;
  }
}

.evaluation-item-label {
  font-size: 12px;
  color: var(--text-primary);
  width: 60px;
}

.evaluation-item-score {
  font-size: 16px;
  font-weight: 700;
  width: 40px;
  text-align: right;
}

.evaluation-item-bar {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
  min-width: 60px;
}

.evaluation-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.evaluation-item-raw {
  font-size: 10px;
  color: var(--text-secondary);
  width: 45px;
  text-align: right;
  font-family: monospace;
}

.evaluation-radar-wrapper {
  flex: 1;
  min-width: 280px;
  height: 320px;
}

.evaluation-radar-wrapper .radar-chart {
  width: 100%;
  height: 100%;
}

/* 综合评分（内联在指标列表下方） */
.evaluation-total-score-inline {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid;
  margin-top: 40px;
}

.total-inline-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.total-inline-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 600;
  white-space: nowrap;
}

.total-inline-content {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.total-inline-value {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
  min-width: 70px;
}

/* 星级和字母等级（内联） */
.total-inline-rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.star-rating-inline {
  display: flex;
  gap: 2px;

  .star-icon-inline {
    width: 14px;
    height: 14px;
    color: #787b86;

    &.filled {
      color: inherit;
    }
  }
}

.letter-grade-inline {
  font-size: 14px;
  font-weight: 700;
}

.total-inline-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  max-width: 200px;
}

.total-inline-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* 综合指标面板样式 */
.metrics-panel {
  display: flex;
  gap: 12px;
  padding: 8px 0;
  align-items: center;
  justify-content: flex-end;
}

.metrics-panel .metrics-list {
  flex: 0 0 200px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metrics-panel .metric-score-item .metric-score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
}

.metrics-panel .metric-name {
  font-size: 12px;
  color: var(--text-secondary, #a0a0a0);
}

.metrics-panel .metric-value {
  font-size: 13px;
  font-weight: 600;
  color: #409ee1;
}

.metrics-panel .metric-progress-bar {
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.metrics-panel .metric-progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.metrics-panel .metric-raw-value {
  font-size: 11px;
  color: var(--text-secondary, #666);
  margin-top: 2px;
  text-align: right;
}

.metrics-panel .radar-chart-wrapper {
  flex: 1;
  min-width: 280px;
  height: 260px;
}

.metrics-panel .radar-chart-wrapper .radar-chart {
  width: 100%;
  height: 100%;
}

/* 进度条/配置区域 - 与BacktestPerformanceChart对齐 */
.progress-section {
  width: 100%;
  box-sizing: border-box;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-percent {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-blue);
}

.progress-bar {
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-blue), var(--accent-green));
  border-radius: 3px;
  transition: width 0.3s;
}

/* 因子计算类型卡片 */
.type-cards {
  display: flex;
  gap: 12px;
}

.type-card {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.type-card:hover {
  background: var(--bg-tertiary);
  border-color: var(--primary-color);
}

.type-card.active {
  background: var(--primary-color-light);
  border-color: var(--primary-color);
}

.type-card-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  color: var(--text-primary);
}

.type-card-icon svg {
  width: 24px;
  height: 24px;
}

.type-card-content {
  flex: 1;
}

.type-card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.type-card-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.type-card-check {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
}

.check-icon {
  width: 20px;
  height: 20px;
  color: var(--primary-color);
}

/* 技术指标区域 */
.indicator-section {
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.indicator-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.indicator-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.indicator-icon {
  width: 18px;
  height: 18px;
  color: var(--text-primary);
}

.indicator-options {
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.preset-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

/* 任务列表样式 */
.task-list-section {
  margin-top: 24px;
}

/* 结果查看器样式 */
.result-stats {
  background: rgba(64, 158, 255, 0.1);
  color: var(--primary-color);
}

.task-status.completed {
  background: rgba(103, 194, 58, 0.1);
  color: var(--success-color);
}

.task-status.failed {
  background: rgba(245, 108, 108, 0.1);
  color: var(--danger-color);
}

.task-info {
  margin-bottom: 8px;
}

/* 任务列表表格样式 */
.task-id-cell {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: monospace;
}

.task-expression-cell {
  font-size: 13px;
  color: var(--text-primary);
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100px;
}

.progress-text {
  font-size: 11px;
  color: var(--text-secondary);
  min-width: 30px;
}

.time-cell {
  font-size: 12px;
  color: var(--text-secondary);
}

.action-buttons-cell {
  display: flex;
  gap: 4px;
}

/* 结果查看器样式 */
.result-stats {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-top: 16px;
  margin-bottom: 16px;
  background: transparent;
}

.result-stats .stat-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  transition: all 0.2s;
}

.result-stats .stat-card:hover {
  border-color: var(--accent-blue, #2962ff);
}

.result-stats .stat-icon {
  width: 24px;
  height: 24px;
  margin: 0 auto 8px;
  color: var(--primary-color);
}

.result-stats .stat-icon svg {
  width: 100%;
  height: 100%;
}

/* 修复按钮组之间的白线 */
.result-btn-group {
  display: inline-flex;
  gap: 4px;
}

.result-btn-group .el-button {
  border-color: var(--border-color, #2a2e39) !important;
  border-radius: 6px !important;
}

.result-btn-group .el-button:hover {
  border-color: var(--primary-color) !important;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.icon-xs {
  width: 14px;
  height: 14px;
  margin-right: 4px;
}

/* 数据表格 */
.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  width: 16px;
  height: 16px;
}

.factor-count {
  font-size: 12px;
  color: var(--text-secondary);
}

.card-size-switch-global {
  margin-left: auto;
}

/* 因子卡片网格 */
.factor-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.factor-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--border-color);
  position: relative;
  transition: transform 0.2s, box-shadow 0.2s;
}

.factor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 通过/失败状态颜色 - 通过红色，失败绿色 */
.factor-card.pass {
  border-left: 3px solid #ef4444;
}

.factor-card.fail {
  border-left: 3px solid #10b981;
  opacity: 0.7;
}

/* 因子类型颜色边框 */
.factor-card.factor-momentum {
  border-left-color: #10b981 !important;
}
.factor-card.factor-volatility {
  border-left-color: #f97316 !important;
}
.factor-card.factor-volume {
  border-left-color: #3b82f6 !important;
}
.factor-card.factor-technical {
  border-left-color: #8b5cf6 !important;
}
.factor-card.factor-alpha {
  border-left-color: #ef4444 !important;
}
.factor-card.factor-other {
  border-left-color: #6b7280 !important;
}

.factor-card-rank {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 10px;
  color: var(--text-secondary);
  font-weight: 600;
}

.factor-card-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  margin-right: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.factor-card-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.metric-label {
  font-size: 9px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.metric-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.metric-value.positive {
  color: #10b981;
}

.metric-value.negative {
  color: #ef4444;
}

.factor-card-status {
  text-align: center;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

/* 折叠面板样式 */
.collapse {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
}

.collapse-item {
  border-bottom: 1px solid var(--border-color);
}

.collapse-item:last-child {
  border-bottom: none;
}

.collapse-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: var(--bg-secondary);
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid var(--border-color);
  min-width: 0;
  width: 100%;
  box-sizing: border-box;
}

.collapse-header:hover {
  background: rgba(255, 255, 255, 0.03);
}

.collapse-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-size-switch {
  margin-left: auto;
}

.collapse-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
  color: white;
  min-width: 90px;
  justify-content: center;
}

/* 不同类型的徽章颜色 */
.badge-alpha158 {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}
.badge-alpha360 {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}
.badge-base {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}
.badge-technical {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}
.badge-custom {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
}

.collapse-count {
  font-size: 12px;
  color: var(--text-secondary);
}

.collapse-arrow {
  font-size: 9px;
  color: var(--text-secondary);
  transition: transform 0.2s;
}

.collapse-item.is-open .collapse-arrow {
  transform: rotate(90deg);
}

.collapse-content {
  display: none;
  padding: 16px;
  background: var(--bg-primary);
}

.collapse-item.is-open .collapse-content {
  display: block;
}

.factor-card-status.pass {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.factor-card-status.fail {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

/* 因子类型分组（已合并到折叠面板中） */
.factor-type-group {
  margin-bottom: 24px;
}

.factor-type-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.factor-type-badge {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 16px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.factor-type-count {
  font-size: 11px;
  color: var(--text-secondary);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

.data-table th {
  background: var(--bg-secondary);
  padding: 10px 12px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border-color);
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
  color: var(--text-primary);
}

.data-table tr:hover {
  background: var(--bg-secondary);
}

/* A股规则：红涨/好，绿跌/坏 */
.value.positive {
  color: var(--color-up);  /* 红色 - 正面 */
  font-weight: 600;
}

.value.negative {
  color: var(--color-down);  /* 绿色 - 负面 */
  font-weight: 600;
}

.status-badge {
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.pass {
  background: rgba(239, 83, 80, 0.2);
  color: var(--accent-red);
}

.status-badge.fail {
  background: rgba(38, 166, 154, 0.2);
  color: var(--accent-green);
}

.status-badge.pending {
  background: rgba(128, 128, 128, 0.2);
  color: var(--text-secondary);
}

.status-badge.running {
  background: rgba(64, 158, 255, 0.2);
  color: var(--primary-color);
}

/* 表单 - 使用响应式网格与上面的统计卡片对齐 */
.config-form {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1400px) {
  .config-form {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .config-form {
    grid-template-columns: 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input,
.form-select {
  padding: 10px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 13px;
  transition: border-color 0.15s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--accent-blue);
}

/* 下拉框选项样式 */
.form-select option {
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: 8px 12px;
}

.form-select option:hover,
.form-select option:checked {
  background: var(--accent-blue);
  color: white;
}

.form-hint {
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  cursor: pointer;
}

.checkbox-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent-blue);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1e4bd8;
}

.btn-success {
  background: var(--accent-green);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #1e8a80;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: #363a45;
}

/* 占位符 */
.heatmap-placeholder {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.placeholder-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.hint {
  font-size: 13px;
  margin-top: 8px;
}

/* 因子列表 */
.factor-list {
  flex: 1;
  overflow-y: auto;
}

.empty-tip {
  padding: 40px 20px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
}

.factor-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.15s;
}

.factor-item:hover {
  background: var(--bg-secondary);
}

.factor-item.selected {
  background: var(--bg-secondary);
}

.factor-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 收藏按钮 */
.favorite-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s;
  flex-shrink: 0;
}

.favorite-btn svg {
  width: 14px;
  height: 14px;
}

.favorite-btn:hover {
  color: #f59e0b;
  transform: scale(1.1);
}

.favorite-btn.favorited {
  color: #f59e0b;
}

/* 因子列表Tab切换 */
.factor-list-tabs {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

.tab-btn {
  padding: 4px 12px;
  font-size: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-secondary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tab-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.favorite-badge {
  background: #f59e0b;
  color: white;
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
}

.factor-type {
  font-size: 10px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.factor-metrics {
  display: flex;
  gap: 12px;
  font-size: 11px;
}

.metric {
  color: var(--text-secondary);
}

.metric-value {
  font-weight: 600;
  color: var(--text-primary);
}

/* A股规则：红涨/好，绿跌/坏 */
.metric-value.positive {
  color: var(--color-up);  /* 红色 - 正面 */
}

.metric-value.negative {
  color: var(--color-down);  /* 绿色 - 负面 */
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-tertiary);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #363a45;
}

/* 面板标题带图标 */
.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 步骤状态指示点 */
.step-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-secondary);
}

.step-status.completed .status-dot {
  background: var(--color-up);  /* 红色 - 完成 */
  box-shadow: 0 0 6px var(--color-up);
}

.step-status.active .status-dot {
  background: var(--accent-blue);
  box-shadow: 0 0 6px var(--accent-blue);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 因子项新样式 */
.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.factor-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.factor-status-dot.excellent {
  background: var(--color-up);  /* 红色 - 极好 */
  box-shadow: 0 0 6px var(--color-up);
}

.factor-status-dot.good {
  background: var(--accent-orange);
}

.factor-status-dot.average {
  background: var(--text-secondary);
}

.factor-status-dot.poor {
  background: var(--color-down);  /* 绿色 - 差 */
}

.factor-score {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 700;
}

.factor-score.excellent {
  color: var(--color-up);  /* 红色 - 极好 */
}

.factor-score.good {
  color: var(--accent-orange);
}

.factor-score.average {
  color: var(--text-secondary);
}

.factor-score.poor {
  color: var(--color-down);  /* 绿色 - 差 */
}

.type-tag {
  display: inline-block;
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
  color: var(--accent-blue);
}

.type-separator {
  margin: 0 6px;
  color: var(--text-secondary);
}

/* 指标带图标样式 */
.metric {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
}

/* 任务头部信息 */
.task-header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.task-id-badge {
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-blue);
  font-family: monospace;
}

/* 任务配置信息 */
.task-config-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 8px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stock-pool-wrap {
  display: flex;
  align-items: center;
}

.stock-pool-wrap .el-select {
  width: auto;
  min-width: 100px;
}

.custom-stocks-count {
  font-size: 12px;
  color: var(--accent-blue);
  margin-left: 8px;
}

.dialog-header-with-icon {
  display: flex;
  align-items: center;
  gap: 10px;

  .dialog-header-icon {
    width: 20px;
    height: 20px;
    color: var(--accent-blue);
  }

  span {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.custom-stock-dialog-content {
  .dialog-desc {
    margin-bottom: 12px;
    color: var(--text-secondary);
  }

  :deep(.el-textarea__inner) {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border-color: var(--border-color);
  }

  .dialog-tips {
    margin-top: 12px;
    padding: 12px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    font-size: 12px;
    color: var(--text-secondary);

    p {
      margin-bottom: 8px;
    }

    ul {
      margin: 0;
      padding-left: 20px;
    }

    li {
      margin-bottom: 4px;
    }
  }
}

.config-label {
  font-size: 10px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.config-icon {
  width: 12px;
  height: 12px;
}

.config-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 日期选择器样式修复 */
.el-date-editor {
  background: rgba(255, 255, 255, 0.05) !important;
}

/* 强制所有日期编辑器背景透明 */
.el-date-editor.el-range-editor,
.el-date-editor.el-range-editor.el-input__wrapper,
.el-date-editor.el-range-editor .el-range-input,
.el-range-editor .el-range-input {
  background: transparent !important;
  background-color: transparent !important;
}

.el-date-editor .el-range-input {
  color: #e0e0e0 !important;
  background: transparent !important;
}

.el-date-editor .el-range-input::placeholder {
  color: rgba(255, 255, 255, 0.4) !important;
}

.el-date-editor .el-range-separator {
  color: rgba(255, 255, 255, 0.4) !important;
}

/* 日期范围编辑器背景强制透明 */
.el-range-editor.el-input__wrapper,
.el-range-editor.el-input__wrapper:hover,
.el-range-editor.el-input__wrapper.is-focus {
  background: transparent !important;
  box-shadow: none !important;
}

/* 日期选择器样式修复 */
.el-picker-panel__body {
  --el-datepicker-active-color: var(--el-color-primary);
}

/* 选中日期单元格背景透明 */
.el-date-table td.current .cell,
.el-date-table td.start-date .cell,
.el-date-table td.end-date .cell,
.el-date-table td.selected .cell {
  background: transparent !important;
  color: var(--el-color-primary) !important;
  border: 1px solid var(--el-color-primary) !important;
}

.el-date-table td.in-range .cell,
.el-date-table td.start-range .cell,
.el-date-table td.end-range .cell {
  background: rgba(102, 126, 234, 0.15) !important;
  color: var(--el-color-primary) !important;
}

.el-date-table td .cell:hover {
  background: rgba(102, 126, 234, 0.2) !important;
}

/* 强制覆盖所有td背景 */
.el-date-table td {
  background: transparent !important;
}

/* el-select 下拉框样式统一 */
.el-select-dropdown,
.el-select-dropdown.el-popper,
.el-select-dropdown__popper,
div.el-select-dropdown {
  background-color: rgba(26, 26, 46, 0.98) !important;
  border: 1px solid rgba(102, 126, 234, 0.3) !important;
  box-shadow: none !important;
}

/* 下拉框输入框和弹出框背景统一 */
.el-select .el-input__wrapper,
.el-select-dropdown {
  background-color: rgba(26, 26, 46, 0.98) !important;
  border-color: rgba(102, 126, 234, 0.3) !important;
}

.el-select-dropdown__item {
  color: #e0e0e0 !important;
  background-color: transparent !important;
}

.el-select-dropdown__item.hover,
.el-select-dropdown__item:hover,
.el-select-dropdown__item:focus,
.el-select-dropdown__item.is-hovering,
.el-select-dropdown__item.is-focus {
  background-color: #2a2a4e !important;
  color: #e0e0e0 !important;
}

.el-select-dropdown__item:last-child {
  background-color: transparent !important;
}

.el-select-dropdown__item.selected {
  color: #409eff !important;
  font-weight: 500;
}

.el-select-dropdown__empty {
  color: #888 !important;
}

/* 多选标签样式 */
.el-select {
  width: auto !important;
}

.el-select .el-select__wrapper {
  min-width: 80px;
  background-color: rgba(26, 26, 46, 0.98) !important;
  border-color: rgba(102, 126, 234, 0.3) !important;
  box-shadow: none !important;
}

.el-select .el-select__wrapper:hover {
  border-color: rgba(64, 158, 255, 0.5) !important;
}

.el-select .el-select__wrapper.is-focused {
  border-color: #409eff !important;
}

.el-select .el-select__wrapper .el-select__placeholder {
  color: rgba(255, 255, 255, 0.4) !important;
}

.el-select .el-select__wrapper .el-select__selected-item {
  color: #e0e0e0 !important;
}

.el-select__tags {
  gap: 2px;
}

.el-select__tags > span {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
}

/* 日期选择器范围选中样式 - 使用 :deep() 穿透 */
:deep(.el-date-table td.in-range .cell),
:deep(.el-date-table td.start-date .cell),
:deep(.el-date-table td.end-date .cell) {
  background-color: #1E222D !important;
  color: #ffffff !important;
}

:deep(.el-date-table td.in-range .cell span),
:deep(.el-date-table td.start-date .cell span),
:deep(.el-date-table td.end-date .cell span) {
  background-color: transparent !important;
  color: #ffffff !important;
}

/* 范围背景 */
:deep(.el-date-table td.in-range > div),
:deep(.el-date-table td.start-date > div),
:deep(.el-date-table td.end-date > div) {
  background-color: rgba(102, 126, 234, 0.2) !important;
}

:deep(.el-date-table td.start-date > div),
:deep(.el-date-table td.end-date > div) {
  background-color: #2962ff !important;
}

/* 自定义日期范围类名样式 */
:deep(.custom-date-inrange .cell),
:deep(.custom-date-start .cell),
:deep(.custom-date-end .cell) {
  background-color: #1E222D !important;
  color: #ffffff !important;
}

:deep(.custom-date-inrange .cell span),
:deep(.custom-date-start .cell span),
:deep(.custom-date-end .cell span) {
  background-color: transparent !important;
  color: #ffffff !important;
}

:deep(.custom-date-inrange > div) {
  background-color: rgba(102, 126, 234, 0.2) !important;
}

:deep(.custom-date-start > div),
:deep(.custom-date-end > div) {
  background-color: #2962ff !important;
}
</style>

<style lang="scss">
// 全局样式 - 预设按钮深色主题
.preset-buttons {
  // 直接选择 el-button，不加限定
  .el-button {
    transition: all 0.2s !important;
    border-radius: 4px !important;
    font-size: 12px !important;
    padding: 6px 12px !important;

    // 选中状态 - 淡蓝色背景
    &[class*="el-button--primary"] {
      background: rgba(41, 98, 255, 0.2) !important;
      border-color: #2962ff !important;
      color: #2962ff !important;

      &:hover {
        background: rgba(41, 98, 255, 0.3) !important;
        border-color: #2962ff !important;
        color: #2962ff !important;
      }
    }

    // 未选中状态 - 深色主题
    &[class*="is-plain"] {
      background: #131722 !important;
      border-color: #2a2e39 !important;
      color: #787b86 !important;

      &:hover {
        background: #1e222d !important;
        border-color: #d1d4dc !important;
        color: #d1d4dc !important;
      }
    }
  }
}

// 复选框样式 - 白色勾选
.el-checkbox {
  .el-checkbox__input.is-checked {
    .el-checkbox__inner {
      background-color: rgba(41, 98, 255, 0.2) !important;
      border-color: #2962ff !important;

      &::after {
        border-color: #ffffff !important;
      }
    }
  }

  .el-checkbox__inner {
    background-color: transparent !important;
    border-color: #787b86 !important;

    &:hover {
      border-color: #2962ff !important;
    }
  }

  .el-checkbox__label {
    color: var(--text-secondary, #787b86) !important;
  }
}
</style>
