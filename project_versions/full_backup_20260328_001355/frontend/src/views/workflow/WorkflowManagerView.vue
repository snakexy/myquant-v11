<template>
  <div class="workflow-manager">
    <GlobalNavBar />

    <!-- 主容器 -->
    <div class="main-container">
      <!-- 功能入口 -->
      <div class="feature-entries">
        <FeatureEntry
          icon="🔬"
          :title="isZh ? '研究流程' : 'Research'"
          color="#2962ff"
          :stage="stages[0]?.count || 0"
          :status-text="getStageDetail(stages[0])"
          @click="switchStage('research')"
          @dblclick="goToStageDetail('research')"
        />
        <FeatureEntry
          icon="🎯"
          :title="isZh ? '验证流程' : 'Validation'"
          color="#26a69a"
          :stage="stages[1]?.count || 0"
          :status-text="getStageDetail(stages[1])"
          @click="switchStage('validation')"
          @dblclick="goToStageDetail('validation')"
        />
        <FeatureEntry
          icon="🚀"
          :title="isZh ? '实盘交易' : 'Production'"
          color="#ff9800"
          :stage="stages[2]?.count || 0"
          :status-text="getStageDetail(stages[2])"
          @click="switchStage('production')"
          @dblclick="goToStageDetail('production')"
        />
      </div>

      <!-- 内容区域 -->
      <div class="content-area">
        <!-- 左侧侧边栏 -->
        <aside class="sidebar">
          <div class="sidebar-section">
            <div class="sidebar-title">
              <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
              </svg>
              {{ isZh ? '状态筛选' : 'Status Filter' }}
            </div>
            <div
              v-for="filter in statusFilters"
              :key="filter.id"
              :class="['nav-item', { active: currentFilter === filter.id }]"
              @click="setFilter(filter.id)"
            >
              <svg v-if="filter.icon === 'list'" class="nav-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="8" y1="6" x2="21" y2="6"></line>
                <line x1="8" y1="12" x2="21" y2="12"></line>
                <line x1="8" y1="18" x2="21" y2="18"></line>
                <line x1="3" y1="6" x2="3.01" y2="6"></line>
                <line x1="3" y1="12" x2="3.01" y2="12"></line>
                <line x1="3" y1="18" x2="3.01" y2="18"></line>
              </svg>
              <svg v-else-if="filter.icon === 'play'" class="nav-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <svg v-else-if="filter.icon === 'hourglass'" class="nav-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 22h14"></path>
                <path d="M5 2h14"></path>
                <path d="M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22"></path>
                <path d="M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2"></path>
              </svg>
              <svg v-else-if="filter.icon === 'clock'" class="nav-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              <svg v-else-if="filter.icon === 'check'" class="nav-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              <svg v-else-if="filter.icon === 'x'" class="nav-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
              <span>{{ isZh ? filter.nameZh : filter.name }}</span>
            </div>
          </div>

          <div class="sidebar-section">
            <div class="sidebar-title">
              <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
              </svg>
              {{ isZh ? '快捷操作' : 'Quick Actions' }}
            </div>
            <div class="nav-item" @click="createNewTaskPool">
              <svg class="nav-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              <span>{{ isZh ? '新建任务池' : 'New Pool' }}</span>
            </div>
            <div class="nav-item" @click="openSettings">
              <svg class="nav-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65任务统计 0 0 0-1.51 1z"></path>
              </svg>
              <span>{{ isZh ? '设置' : 'Settings' }}</span>
            </div>
            <div class="nav-item" @click="openAnalytics">
              <svg class="nav-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
              <span>{{ isZh ? '数据分析' : 'Analytics' }}</span>
            </div>
          </div>

          <!-- 批量任务池 -->
          <div class="sidebar-section">
            <div class="sidebar-title">
              <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="8" y1="6" x2="21" y2="6"></line>
                <line x1="8" y1="12" x2="21" y2="12"></line>
                <line x1="8" y1="18" x2="21" y2="18"></line>
                <line x1="3" y1="6" x2="3.01" y2="6"></line>
                <line x1="3" y1="12" x2="3.01" y2="12"></line>
                <line x1="3" y1="18" x2="3.01" y2="18"></line>
              </svg>
              {{ isZh ? '批量任务池' : 'Task Pools' }}
            </div>
            <div v-if="isLoadingPools" class="loading-mini">{{ isZh ? '加载中...' : 'Loading...' }}</div>
            <div v-else-if="taskPools.length === 0" class="empty-mini">
              {{ isZh ? '暂无任务池' : 'No pools' }}
            </div>
            <div
              v-else
              v-for="pool in taskPools"
              :key="pool.name"
              class="pool-item"
              @click="viewResults(pool.name)"
            >
              <div class="pool-name">{{ pool.name }}</div>
              <div class="pool-stats-mini" v-if="poolStats[pool.name]">
                <span class="stat-waiting">{{ poolStats[pool.name].waiting }}</span>
                <span class="stat-running">{{ poolStats[pool.name].running }}</span>
                <span class="stat-done">{{ poolStats[pool.name].done }}</span>
              </div>
              <ActionButton type="success" size="small" :icon="iconPlay" :icon-only="true" @click.stop="startTraining(pool.name)" :title="isZh ? '启动训练' : 'Start'" />
            </div>
          </div>
        </aside>

        <!-- 右侧主内容 -->
        <main class="main-content">
          <div class="page-header">
            <div>
              <h1 class="page-title">{{ getCurrentStageTitle() }}</h1>
              <p class="page-subtitle">{{ isZh ? '管理任务、跟踪进度、比较结果' : 'Manage your tasks, track progress, and compare results' }}</p>
            </div>
            <div class="page-actions">
              <ActionButton type="primary" size="small" :label="isZh ? '新建任务' : 'New Task'" :icon="iconAdd" @click="createNewTask" />
              <ActionButton type="default" size="small" :label="isZh ? '设置' : 'Settings'" :icon="iconSettings" @click="openSettings" />
            </div>
          </div>

          <!-- 过滤器 -->
          <div class="task-filters">
            <div class="filter-group">
              <span class="filter-label">{{ isZh ? '类型' : 'Type' }}:</span>
              <ActionButton
                v-for="type in taskTypes"
                :key="type.id"
                :type="currentType === type.id ? 'primary' : 'default'"
                size="small"
                :label="isZh ? type.nameZh : type.name"
                @click="setType(type.id)"
              />
            </div>
            <div class="filter-group" style="margin-left: auto;">
              <span class="filter-label">{{ isZh ? '排序' : 'Sort' }}:</span>
              <ActionButton
                v-for="sort in sortOptions"
                :key="sort.id"
                :type="currentSort === sort.id ? 'primary' : 'default'"
                size="small"
                :label="isZh ? sort.nameZh : sort.name"
                @click="setSort(sort.id)"
              />
            </div>
          </div>

          <!-- 任务网格 -->
          <div v-if="isLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>{{ isZh ? '正在加载数据...' : 'Loading data...' }}</p>
          </div>

          <div v-else class="tasks-grid">
            <div
              v-for="task in filteredTasks"
              :key="task.id"
              class="task-card"
              @click="openTask(task)"
            >
              <div class="task-header">
                <div>
                  <div class="task-title">{{ isZh ? task.titleZh : task.title }}</div>
                  <div class="task-id">#{{ task.id }}</div>
                </div>
                <span :class="['task-badge', task.status]">
                  {{ getStatusBadge(task.status) }}
                </span>
              </div>
              <div class="task-description">
                {{ isZh ? task.descriptionZh : task.description }}
              </div>
              <!-- 任务配置参数预览 -->
              <div v-if="task.config" class="task-config">
                <span class="config-tag" v-if="task.config.stockPool">
                  📊 {{ isZh ? task.config.stockPoolZh : task.config.stockPool }}
                </span>
                <span class="config-tag" v-if="task.config.factors">
                  🔢 {{ isZh ? task.config.factorsZh : task.config.factors }}
                </span>
                <span class="config-tag" v-if="task.config.dateStart">
                  📅 {{ task.config.dateStart }} ~ {{ task.config.dateEnd }}
                </span>
                <span class="config-tag" v-if="task.config.model">
                  🤖 {{ task.config.model }}
                </span>
              </div>
              <div class="task-meta">
                <div class="meta-item">📅 {{ isZh ? '创建于' : 'Created' }}: {{ task.created }}</div>
                <div class="meta-item">⏱️ {{ task.duration }}</div>
              </div>
              <div class="task-progress">
                <div class="progress-header">
                  <span>{{ isZh ? '进度' : 'Progress' }}</span>
                  <span>{{ task.progress }}%</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
                </div>
              </div>
              <!-- 任务操作按钮 -->
              <div class="task-actions" @click.stop>
                <ActionButton
                  type="default"
                  size="small"
                  :icon="iconArchive"
                  :icon-only="true"
                  @click="archiveTask(task)"
                  :title="isZh ? '保存到策略库' : 'Save to Library'"
                />
                <ActionButton
                  type="warning"
                  size="small"
                  :icon="iconRestore"
                  :icon-only="true"
                  @click="restoreTask(task)"
                  :title="isZh ? '重新激活' : 'Reactivate'"
                />
                <ActionButton
                  type="danger"
                  size="small"
                  :icon="iconDelete"
                  :icon-only="true"
                  @click="deleteTask(task)"
                  :title="isZh ? '删除任务' : 'Delete Task'"
                />
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="filteredTasks.length === 0" class="empty-state">
            <div class="empty-icon">📋</div>
            <p>{{ isZh ? '暂无任务' : 'No tasks found' }}</p>
          </div>
        </main>
      </div>
    </div>

    <!-- 新建任务模态框 -->
    <div v-if="showCreateTaskModal" class="modal-overlay" @click.self="showCreateTaskModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ isZh ? '新建任务' : 'New Task' }}</h2>
          <ActionButton type="default" size="small" :icon="iconClose" :icon-only="true" @click="showCreateTaskModal = false" />
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>{{ isZh ? '任务名称' : 'Task Name' }}</label>
            <input v-model="newTaskForm.title" type="text" :placeholder="isZh ? '输入任务名称' : 'Enter task name'" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>{{ isZh ? '阶段' : 'Stage' }}</label>
              <select v-model="newTaskForm.stage">
                <option value="research">{{ isZh ? '研究' : 'Research' }}</option>
                <option value="validation">{{ isZh ? '验证' : 'Validation' }}</option>
                <option value="production">{{ isZh ? '实盘' : 'Production' }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>{{ isZh ? '股票池' : 'Stock Pool' }}</label>
              <select v-model="newTaskForm.stockPool">
                <option value="CSI300">{{ isZh ? '沪深300' : 'CSI300' }}</option>
                <option value="CSI500">{{ isZh ? '中证500' : 'CSI500' }}</option>
                <option value="ALL">{{ isZh ? '全A股' : 'All A-shares' }}</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>{{ isZh ? '开始日期' : 'Start Date' }}</label>
              <input v-model="newTaskForm.dateStart" type="date" />
            </div>
            <div class="form-group">
              <label>{{ isZh ? '结束日期' : 'End Date' }}</label>
              <input v-model="newTaskForm.dateEnd" type="date" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>{{ isZh ? '因子' : 'Factors' }}</label>
              <input v-model="newTaskForm.factors" type="text" :placeholder="isZh ? '如: Alpha158' : 'e.g. Alpha158'" />
            </div>
            <div class="form-group">
              <label>{{ isZh ? '模型' : 'Model' }}</label>
              <select v-model="newTaskForm.model">
                <option value="LightGBM">LightGBM</option>
                <option value="XGBoost">XGBoost</option>
                <option value="MLP">MLP</option>
                <option value="LSTM">LSTM</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>{{ isZh ? '描述' : 'Description' }}</label>
            <textarea v-model="newTaskForm.description" rows="3" :placeholder="isZh ? '任务描述...' : 'Task description...'"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <ActionButton type="default" :label="isZh ? '取消' : 'Cancel'" @click="showCreateTaskModal = false" />
          <ActionButton type="primary" :label="isZh ? '创建' : 'Create'" @click="submitNewTask" />
        </div>
      </div>
    </div>

    <!-- 新建任务池模态框 -->
    <div v-if="showCreateTaskPoolModal" class="modal-overlay" @click.self="showCreateTaskPoolModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ isZh ? '新建任务池' : 'New Task Pool' }}</h2>
          <ActionButton type="default" size="small" :icon="iconClose" :icon-only="true" @click="showCreateTaskPoolModal = false" />
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>{{ isZh ? '任务池名称' : 'Pool Name' }}</label>
            <input v-model="newPoolForm.name" type="text" :placeholder="isZh ? '如: rolling_lstm_2024' : 'e.g. rolling_lstm_2024'" />
          </div>
          <div class="form-group">
            <label>{{ isZh ? '描述' : 'Description' }}</label>
            <textarea v-model="newPoolForm.description" rows="2" :placeholder="isZh ? '任务池描述...' : 'Pool description...'"></textarea>
          </div>
          <div class="form-group">
            <label>{{ isZh ? '生成类型' : 'Generate Type' }}</label>
            <select v-model="newPoolForm.genType">
              <option value="rolling">{{ isZh ? '滚动训练' : 'Rolling Training' }}</option>
              <option value="multi_loss">{{ isZh ? '多损失函数对比' : 'Multi-Loss Comparison' }}</option>
              <option value="optuna">{{ isZh ? '超参数搜索 (Optuna)' : 'Hyperparameter Search (Optuna)' }}</option>
              <option value="custom">{{ isZh ? '自定义' : 'Custom' }}</option>
            </select>
          </div>

          <!-- 滚动训练配置 -->
          <div v-if="newPoolForm.genType === 'rolling'" class="gen-config">
            <div class="config-title">{{ isZh ? '滚动训练配置' : 'Rolling Config' }}</div>
            <div class="form-group">
              <label>{{ isZh ? '滚动步长（交易日）' : 'Rolling Step (trading days)' }}</label>
              <input v-model.number="newPoolForm.rollStep" type="number" min="1" />
              <div class="form-hint">{{ isZh ? '252 ≈ 1年' : '252 ≈ 1 year' }}</div>
            </div>
          </div>

          <!-- 多损失函数配置 -->
          <div v-if="newPoolForm.genType === 'multi_loss'" class="gen-config">
            <div class="config-title">{{ isZh ? '损失函数选择' : 'Loss Functions' }}</div>
            <div class="checkbox-group">
              <label class="checkbox-item">
                <input type="checkbox" value="mse" v-model="newPoolForm.losses" />
                <span>MSE (均方误差)</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" value="ic" v-model="newPoolForm.losses" />
                <span>IC (信息系数)</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" value="rank_ic" v-model="newPoolForm.losses" />
                <span>Rank IC</span>
              </label>
            </div>
          </div>

          <!-- Optuna超参搜索配置 -->
          <div v-if="newPoolForm.genType === 'optuna'" class="gen-config">
            <div class="config-title">{{ isZh ? '超参搜索配置' : 'Optuna Config' }}</div>
            <div class="form-group">
              <label>{{ isZh ? '搜索次数' : 'Number of Trials' }}</label>
              <input v-model.number="newPoolForm.nTrials" type="number" min="1" max="1000" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <ActionButton type="default" :label="isZh ? '取消' : 'Cancel'" @click="showCreateTaskPoolModal = false" />
          <ActionButton type="primary" :label="isZh ? '创建' : 'Create'" @click="submitNewTaskPool" :disabled="!newPoolForm.name" />
        </div>
      </div>
    </div>

    <!-- 设置模态框 -->
    <div v-if="showSettingsModal" class="modal-overlay" @click.self="showSettingsModal = false">
      <div class="modal-content modal-small">
        <div class="modal-header">
          <h2>{{ isZh ? '设置' : 'Settings' }}</h2>
          <ActionButton type="default" size="small" :icon="iconClose" :icon-only="true" @click="showSettingsModal = false" />
        </div>
        <div class="modal-body">
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-label">{{ isZh ? '自动保存' : 'Auto Save' }}</div>
              <div class="setting-desc">{{ isZh ? '自动保存任务进度' : 'Automatically save task progress' }}</div>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="settingsForm.autoSave" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-label">{{ isZh ? '通知提醒' : 'Notifications' }}</div>
              <div class="setting-desc">{{ isZh ? '任务完成时发送通知' : 'Send notification when task completes' }}</div>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="settingsForm.notifications" />
              <span class="toggle-slider"></span>
            </label>
          </div>
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-label">{{ isZh ? '刷新间隔' : 'Refresh Interval' }}</div>
              <div class="setting-desc">{{ isZh ? '数据刷新频率（秒）' : 'Data refresh frequency (seconds)' }}</div>
            </div>
            <select v-model="settingsForm.refreshInterval" class="setting-select">
              <option :value="10">10s</option>
              <option :value="30">30s</option>
              <option :value="60">60s</option>
              <option :value="300">5min</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <ActionButton type="default" :label="isZh ? '取消' : 'Cancel'" @click="showSettingsModal = false" />
          <ActionButton type="primary" :label="isZh ? '保存' : 'Save'" @click="saveSettings" />
        </div>
      </div>
    </div>

    <!-- 数据分析模态框 -->
    <div v-if="showAnalyticsModal" class="modal-overlay" @click.self="showAnalyticsModal = false">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h2>{{ isZh ? '数据分析' : 'Data Analytics' }}</h2>
          <ActionButton type="default" size="small" :icon="iconClose" :icon-only="true" @click="showAnalyticsModal = false" />
        </div>
        <div class="modal-body">
          <div class="analytics-grid">
            <div class="analytics-card">
              <div class="analytics-title">
                <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="20" x2="18" y2="10"></line>
                  <line x1="12" y1="20" x2="12" y2="4"></line>
                  <line x1="6" y1="20" x2="6" y2="14"></line>
                </svg>
                {{ isZh ? '任务统计' : 'Task Statistics' }}
              </div>
              <div class="analytics-stats">
                <div class="stat-item">
                  <div class="stat-value">{{ tasks.length }}</div>
                  <div class="stat-label">{{ isZh ? '总任务' : 'Total Tasks' }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value running">{{ tasks.filter((t: Task) => t.status === 'running').length }}</div>
                  <div class="stat-label">{{ isZh ? '运行中' : 'Running' }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value completed">{{ tasks.filter((t: Task) => t.status === 'completed').length }}</div>
                  <div class="stat-label">{{ isZh ? '已完成' : 'Completed' }}</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value queued">{{ tasks.filter((t: Task) => t.status === 'queued').length }}</div>
                  <div class="stat-label">{{ isZh ? '排队中' : 'Queued' }}</div>
                </div>
              </div>
            </div>
            <div class="analytics-card">
              <div class="analytics-title">
                <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="8" y1="6" x2="21" y2="6"></line>
                  <line x1="8" y1="12" x2="21" y2="12"></line>
                  <line x1="8" y1="18" x2="21" y2="18"></line>
                  <line x1="3" y1="6" x2="3.01" y2="6"></line>
                  <line x1="3" y1="12" x2="3.01" y2="12"></line>
                  <line x1="3" y1="18" x2="3.01" y2="18"></line>
                </svg>
                {{ isZh ? '批量任务池' : 'Task Pools' }}
              </div>
              <div v-if="taskPools.length === 0" class="analytics-empty">
                {{ isZh ? '暂无任务池' : 'No task pools' }}
              </div>
              <div v-else class="pool-list">
                <div v-for="pool in taskPools" :key="pool.name" class="pool-summary">
                  <div class="pool-name">{{ pool.name }}</div>
                  <div class="pool-progress">
                    <div class="pool-progress-bar" :style="{ width: ((poolStats[pool.name]?.done || 0) / Math.max(poolStats[pool.name]?.total || 1, 1) * 100) + '%' }"></div>
                  </div>
                  <div class="pool-count">{{ poolStats[pool.name]?.done || 0 }}/{{ poolStats[pool.name]?.total || 0 }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <ActionButton type="primary" :label="isZh ? '关闭' : 'Close'" @click="showAnalyticsModal = false" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import GlobalNavBar from '@/components/GlobalNavBar.vue'
import { strategyLibraryApi, type StrategyEntity } from '@/api/modules/library'
import { taskApi, type TaskPool, type TaskPoolStats } from '@/api/modules/task'
import { workflowApi } from '@/api/modules/workflow'
import { useAppStore } from '@/stores/core/AppStore'
import FeatureEntry from '@/components/ui/FeatureEntry.vue'
import { ActionButton } from '@/components/ui'

// 图标定义
const iconAdd = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>'
const iconSettings = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>'
const iconArchive = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8v13H3V8"></path><path d="M1 3h22v5H1z"></path><path d="M10 12h4"></path></svg>'
const iconRestore = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M3 21v-5h5"></path></svg>'
const iconDelete = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"></path><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10"></line><line x1="14" y1="11" x2="14"></line></svg>'
const iconClose = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>'
const iconPlay = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>'

const router = useRouter()
const appStore = useAppStore()

// API加载状态
const isLoading = ref(false)

// ==================== Task批量任务管理 ====================
const taskPools = ref<TaskPool[]>([])
const poolStats = ref<Record<string, TaskPoolStats>>({})
const isLoadingPools = ref(false)

const loadTaskPools = async () => {
  isLoadingPools.value = true
  try {
    const response = await taskApi.getPools()
    if (response.code === 200) {
      taskPools.value = response.data
      for (const pool of response.data) {
        loadPoolStats(pool.name)
      }
    }
  } catch (error) {
    console.error('Failed to load task pools:', error)
  } finally {
    isLoadingPools.value = false
  }
}

const loadPoolStats = async (poolName: string) => {
  try {
    const response = await taskApi.getPoolStats(poolName)
    if (response.code === 200) {
      poolStats.value[poolName] = response.data
    }
  } catch (error) {
    console.error('Failed to load pool stats:', error)
  }
}

const startTraining = async (poolName: string) => {
  try {
    await taskApi.startTraining(poolName)
    await loadPoolStats(poolName)
  } catch (error) {
    console.error('Failed to start training:', error)
  }
}

const viewResults = async (poolName: string) => {
  try {
    const response = await taskApi.getResults(poolName)
    console.log('Results:', response.data)
  } catch (error) {
    console.error('Failed to get results:', error)
  }
}

// ==================== Workflow单次流水线 ====================
const startWorkflowTask = async (taskId: string) => {
  try {
    await workflowApi.executeWorkflow(taskId)
    await loadStrategiesFromApi()
  } catch (error) {
    console.error('Failed to start workflow:', error)
  }
}

// 语言切换
const isZh = computed(() => appStore.language === 'zh')

// 动态计算各阶段统计数据
const getStageStats = (stageId: string) => {
  const stageTasks = tasks.value.filter((t: Task) => t.stage === stageId)
  const running = stageTasks.filter((t: Task) => t.status === 'running').length
  const queued = stageTasks.filter((t: Task) => t.status === 'queued').length
  const completed = stageTasks.filter((t: Task) => t.status === 'completed').length
  return { count: stageTasks.length, running, queued, completed }
}

// 阶段配置 - 使用computed动态更新
const stages = computed(() => [
  { id: 'research', name: 'Research', nameZh: '研究', icon: '🔬', ...getStageStats('research') },
  { id: 'validation', name: 'Validation', nameZh: '验证', icon: '🧪', ...getStageStats('validation') },
  { id: 'production', name: 'Production', nameZh: '实盘', icon: '🚀', ...getStageStats('production') }
])

const currentStage = ref('research')

const switchStage = (stageId: string) => {
  currentStage.value = stageId
}

// 双击状态卡片进入对应阶段详情页
const goToStageDetail = (stageId: string) => {
  const routeMap: Record<string, string> = {
    research: '/research/detail',
    validation: '/validation/detail',
    production: '/production/detail'
  }
  const path = routeMap[stageId] || '/workflow'
  router.push(path)
}

const getStageDetail = (stage: { id: string; running: number; queued: number; completed: number; count: number }) => {
  if (stage.id === 'production') {
    // 实盘阶段：运行中 和 暂停中（非运行的都是暂停状态）
    const paused = stage.count - stage.running
    return `${stage.running} ${isZh.value ? '运行中' : 'active'} · ${paused} ${isZh.value ? '暂停中' : 'paused'}`
  }
  const parts = []
  if (stage.running > 0) parts.push(`${stage.running} ${isZh.value ? '运行中' : 'running'}`)
  if (stage.queued > 0) parts.push(`${stage.queued} ${isZh.value ? '排队' : 'queued'}`)
  if (stage.completed > 0) parts.push(`${stage.completed} ${isZh.value ? '已完成' : 'completed'}`)
  return parts.length > 0 ? parts.join(' · ') : (isZh.value ? '暂无任务' : 'No tasks')
}

const getCurrentStageTitle = () => {
  const titles: Record<string, { en: string; zh: string }> = {
    research: { en: 'Research Stage Tasks', zh: '研究阶段任务' },
    validation: { en: 'Validation Stage Tasks', zh: '验证阶段任务' },
    production: { en: 'Production Stage Tasks', zh: '实盘阶段任务' },
    archive: { en: 'Strategy Library', zh: '策略库' }
  }
  const title = titles[currentStage.value]
  return isZh.value ? title.zh : title.en
}

// 状态筛选
const statusFilters = [
  { id: 'all', name: 'All Tasks', nameZh: '全部任务', icon: 'list' },
  { id: 'running', name: 'Running', nameZh: '运行中', icon: 'hourglass' },
  { id: 'queued', name: 'Queued', nameZh: '排队中', icon: 'clock' },
  { id: 'completed', name: 'Completed', nameZh: '已完成', icon: 'check' },
  { id: 'failed', name: 'Failed', nameZh: '失败', icon: 'x' }
]

const currentFilter = ref('all')

const setFilter = (filterId: string) => {
  currentFilter.value = filterId
}

// 任务类型
const taskTypes = [
  { id: 'all', name: 'All', nameZh: '全部' },
  { id: 'factor', name: 'Factor Analysis', nameZh: '因子分析' },
  { id: 'model', name: 'Model Training', nameZh: '模型训练' },
  { id: 'backtest', name: 'Backtest', nameZh: '回测' }
]

const currentType = ref('all')

const setType = (typeId: string) => {
  currentType.value = typeId
}

// 排序选项
const sortOptions = [
  { id: 'created', name: 'Created', nameZh: '创建时间' },
  { id: 'progress', name: 'Progress', nameZh: '进度' },
  { id: 'name', name: 'Name', nameZh: '名称' }
]

const currentSort = ref('created')

const setSort = (sortId: string) => {
  currentSort.value = sortId
}

// 任务数据
interface TaskConfig {
  stockPool?: string
  stockPoolZh?: string
  dateStart?: string
  dateEnd?: string
  factors?: string
  factorsZh?: string
  model?: string
  icMethod?: string
  icThreshold?: number
}

interface Task {
  id: string
  title: string
  titleZh: string
  description: string
  descriptionZh: string
  status: 'running' | 'queued' | 'completed' | 'failed'
  type: string
  stage: string
  progress: number
  created: string
  duration: string
  config?: TaskConfig
  // 用于API同步的策略ID
  strategyId?: string
}

// 将API策略实体转换为本地Task格式
const convertStrategyToTask = (strategy: StrategyEntity): Task => {
  const stageMap: Record<string, string> = {
    'research': 'research',
    'validation': 'validation',
    'production': 'production'
  }

  const statusMap: Record<string, 'running' | 'queued' | 'completed' | 'failed'> = {
    'active': 'running',
    'paused': 'queued',
    'archived': 'completed',
    'deleted': 'failed'
  }

  return {
    id: strategy.strategyId,
    strategyId: strategy.strategyId,
    title: strategy.strategyName,
    titleZh: strategy.strategyNameZh || strategy.strategyName,
    description: strategy.description || '',
    descriptionZh: strategy.descriptionZh || strategy.description || '',
    status: statusMap[strategy.status] || 'queued',
    type: 'Factor Analysis', // 默认类型
    stage: stageMap[strategy.stage] || 'research',
    progress: strategy.status === 'active' ? 85 : strategy.status === 'archived' ? 100 : 0,
    created: formatDate(strategy.createdAt),
    duration: strategy.status === 'active' ? (isZh.value ? '持续运行' : 'Active') :
              strategy.status === 'archived' ? (isZh.value ? '策略保留中' : 'Strategy Saved') :
              (isZh.value ? '等待中' : 'Waiting'),
    config: {
      stockPool: strategy.config?.stockPool,
      stockPoolZh: strategy.config?.stockPoolZh,
      factors: strategy.config?.factors,
      factorsZh: strategy.config?.factorsZh,
      model: strategy.config?.modelType
    }
  }
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return isZh.value ? '刚刚' : 'Just now'
  if (diffDays === 1) return isZh.value ? '1天前' : '1 day ago'
  if (diffDays < 30) return isZh.value ? `${diffDays}天前` : `${diffDays} days ago`
  if (diffDays < 365) return isZh.value ? `${Math.floor(diffDays / 30)}个月前` : `${Math.floor(diffDays / 30)} months ago`
  return isZh.value ? `${Math.floor(diffDays / 365)}年前` : `${Math.floor(diffDays / 365)} years ago`
}

// 本地任务数据（作为后备）
const localTasks = ref<Task[]>([
  // ==================== Research 阶段任务 ====================
  {
    id: 'RES-2024-001',
    title: 'Alpha158 Factor Analysis',
    titleZh: 'Alpha158因子分析',
    description: 'Analyze IC/IR metrics for Alpha158 factors on CSI300 stock pool with 3-year historical data.',
    descriptionZh: '分析沪深300股票池Alpha158因子的IC/IR指标，使用3年历史数据。',
    status: 'running',
    type: 'Factor Analysis',
    stage: 'research',
    progress: 67,
    created: isZh.value ? '2天前' : '2 days ago',
    duration: isZh.value ? '约2小时' : '~2h left',
    config: {
      stockPool: 'CSI300',
      stockPoolZh: '沪深300',
      dateStart: '2021-01-01',
      dateEnd: '2024-12-31',
      factors: 'Alpha158',
      factorsZh: 'Alpha158因子集',
      icMethod: 'spearman',
      icThreshold: 0.03
    }
  },
  {
    id: 'RES-2024-002',
    title: 'LGB Model Training',
    titleZh: 'LightGBM模型训练',
    description: 'Train LightGBM model with top 20 factors from Alpha158 analysis, 7-fold cross-validation.',
    descriptionZh: '使用Alpha158分析中的前20个因子训练LightGBM模型，7折交叉验证。',
    status: 'running',
    type: 'Model Training',
    stage: 'research',
    progress: 45,
    created: isZh.value ? '5天前' : '5 days ago',
    duration: isZh.value ? '约4小时' : '~4h left',
    config: {
      stockPool: 'CSI500',
      stockPoolZh: '中证500',
      dateStart: '2020-01-01',
      dateEnd: '2024-12-31',
      factors: 'Top20 Selected',
      factorsZh: '精选Top20因子',
      model: 'LightGBM'
    }
  },
  {
    id: 'RES-2024-003',
    title: 'Factor Correlation Analysis',
    titleZh: '因子相关性分析',
    description: 'Generate correlation heatmap for all qualified factors to identify duplicates and redundancy.',
    descriptionZh: '生成所有合格因子的相关性热图，识别重复和冗余因子。',
    status: 'queued',
    type: 'Factor Analysis',
    stage: 'research',
    progress: 0,
    created: isZh.value ? '刚刚' : 'Just now',
    duration: isZh.value ? '等待依赖' : 'Waiting for dependencies',
    config: {
      stockPool: 'All A-shares',
      stockPoolZh: '全A股',
      dateStart: '2022-01-01',
      dateEnd: '2024-12-31',
      factors: 'All Qualified',
      factorsZh: '全部合格因子',
      icThreshold: 0.05
    }
  },
  {
    id: 'RES-2024-004',
    title: 'Data Configuration - CSI300',
    titleZh: '数据配置 - 沪深300',
    description: 'Configure data source, stock pool, and date range for CSI300 index constituent stocks.',
    descriptionZh: '配置沪深300指数成份股的数据源、股票池和日期范围。',
    status: 'completed',
    type: 'Factor Analysis',
    stage: 'research',
    progress: 100,
    created: isZh.value ? '1天前' : '1 day ago',
    duration: isZh.value ? '耗时2小时' : 'Took 2 hours',
    config: {
      stockPool: 'CSI300',
      stockPoolZh: '沪深300',
      dateStart: '2021-01-01',
      dateEnd: '2024-12-31',
      factors: 'Basic Setup',
      factorsZh: '基础配置'
    }
  },
  {
    id: 'RES-2024-005',
    title: 'Custom Factor - MA_Cross',
    titleZh: '自定义因子 - 均线交叉',
    description: 'Custom moving average crossover factor with 60-day window for momentum strategy.',
    descriptionZh: '自定义均线交叉因子，60日窗口，用于动量策略。',
    status: 'completed',
    type: 'Factor Analysis',
    stage: 'research',
    progress: 100,
    created: isZh.value ? '3天前' : '3 days ago',
    duration: isZh.value ? '耗时4小时' : 'Took 4 hours',
    config: {
      stockPool: 'CSI300',
      stockPoolZh: '沪深300',
      dateStart: '2020-01-01',
      dateEnd: '2024-12-31',
      factors: 'MA_Cross_60',
      factorsZh: '60日均线交叉'
    }
  },
  // ==================== Validation 阶段任务 ====================
  {
    id: 'VAL-2024-001',
    title: 'Alpha158 Strategy Paper Trading',
    titleZh: 'Alpha158策略模拟交易',
    description: 'Paper trading validation for Alpha158 factor strategy on CSI300, starting with 1M virtual capital.',
    descriptionZh: 'Alpha158因子策略在沪深300的模拟交易验证，初始虚拟资金100万。',
    status: 'running',
    type: 'Backtest',
    stage: 'validation',
    progress: 35,
    created: isZh.value ? '3天前' : '3 days ago',
    duration: isZh.value ? '运行中14天' : '14 days running',
    config: {
      stockPool: 'CSI300',
      stockPoolZh: '沪深300',
      dateStart: '2024-01-01',
      dateEnd: '2024-12-31',
      factors: 'Alpha158',
      factorsZh: 'Alpha158因子集',
      model: 'LightGBM'
    }
  },
  {
    id: 'VAL-2024-002',
    title: 'Momentum Strategy Validation',
    titleZh: '动量策略验证',
    description: 'Out-of-sample validation for momentum strategy with rolling window backtesting.',
    descriptionZh: '动量策略的样本外验证，使用滚动窗口回测方法。',
    status: 'queued',
    type: 'Backtest',
    stage: 'validation',
    progress: 0,
    created: isZh.value ? '1天前' : '1 day ago',
    duration: isZh.value ? '等待资源' : 'Waiting for resources',
    config: {
      stockPool: 'CSI500',
      stockPoolZh: '中证500',
      dateStart: '2023-01-01',
      dateEnd: '2024-12-31',
      factors: 'Momentum',
      factorsZh: '动量因子',
      model: 'XGBoost'
    }
  },
  {
    id: 'VAL-2024-003',
    title: 'Multi-Factor Model Validation',
    titleZh: '多因子模型验证',
    description: 'Cross-sectional validation of multi-factor model combining value, momentum, and quality factors.',
    descriptionZh: '结合价值、动量、质量因子的多因子模型横截面验证。',
    status: 'running',
    type: 'Model Training',
    stage: 'validation',
    progress: 72,
    created: isZh.value ? '7天前' : '7 days ago',
    duration: isZh.value ? '运行中21天' : '21 days running',
    config: {
      stockPool: 'All A-shares',
      stockPoolZh: '全A股',
      dateStart: '2022-01-01',
      dateEnd: '2024-12-31',
      factors: 'Multi-Factor',
      factorsZh: '多因子组合',
      model: 'Ensemble'
    }
  },
  {
    id: 'VAL-2024-004',
    title: 'Risk Model Stress Test',
    titleZh: '风险模型压力测试',
    description: 'Stress testing the risk model under various market scenarios including flash crash and liquidity crisis.',
    descriptionZh: '在各种市场情景下测试风险模型，包括闪崩和流动性危机。',
    status: 'completed',
    type: 'Backtest',
    stage: 'validation',
    progress: 100,
    created: isZh.value ? '14天前' : '14 days ago',
    duration: isZh.value ? '耗时3天' : 'Took 3 days',
    config: {
      stockPool: 'CSI300',
      stockPoolZh: '沪深300',
      factors: 'Risk Factors',
      factorsZh: '风险因子'
    }
  },
  {
    id: 'VAL-2024-005',
    title: 'Strategy Approval Review',
    titleZh: '策略审批评审',
    description: 'Final review and approval process for validated strategies before production deployment.',
    descriptionZh: '验证通过策略的最终评审和审批流程，准备实盘部署。',
    status: 'queued',
    type: 'Factor Analysis',
    stage: 'validation',
    progress: 0,
    created: isZh.value ? '刚刚' : 'Just now',
    duration: isZh.value ? '等待审批' : 'Pending approval',
    config: {
      stockPool: 'CSI300',
      stockPoolZh: '沪深300',
      factors: 'Alpha158',
      factorsZh: 'Alpha158因子集',
      model: 'LightGBM'
    }
  },
  // ==================== Production 阶段任务 ====================
  {
    id: 'PRD-2024-001',
    title: 'Alpha158 Live Trading',
    titleZh: 'Alpha158实盘交易',
    description: 'Live trading execution of Alpha158 strategy with real capital allocation.',
    descriptionZh: 'Alpha158策略的实盘交易执行，真实资金配置。',
    status: 'running',
    type: 'Factor Analysis',
    stage: 'production',
    progress: 85,
    created: isZh.value ? '30天前' : '30 days ago',
    duration: isZh.value ? '持续运行' : 'Active',
    config: {
      stockPool: 'CSI300',
      stockPoolZh: '沪深300',
      factors: 'Alpha158',
      factorsZh: 'Alpha158因子集',
      model: 'LightGBM'
    }
  },
  {
    id: 'PRD-2024-002',
    title: 'ML Signal Generation Service',
    titleZh: 'ML信号生成服务',
    description: 'Real-time ML signal generation service producing daily stock recommendations.',
    descriptionZh: '实时机器学习信号生成服务，每日输出股票推荐。',
    status: 'running',
    type: 'Model Training',
    stage: 'production',
    progress: 92,
    created: isZh.value ? '60天前' : '60 days ago',
    duration: isZh.value ? '持续运行' : 'Active',
    config: {
      stockPool: 'All A-shares',
      stockPoolZh: '全A股',
      factors: 'ML Features',
      factorsZh: 'ML特征',
      model: 'Ensemble'
    }
  },
  {
    id: 'PRD-2024-003',
    title: 'Risk Monitor - Portfolio Exposure',
    titleZh: '风险监控 - 组合敞口',
    description: 'Real-time monitoring of portfolio exposure, position limits, and risk metrics.',
    descriptionZh: '实时监控组合敞口、仓位限制和风险指标。',
    status: 'running',
    type: 'Factor Analysis',
    stage: 'production',
    progress: 100,
    created: isZh.value ? '90天前' : '90 days ago',
    duration: isZh.value ? '持续监控' : 'Monitoring',
    config: {
      stockPool: 'CSI300+CSI500',
      stockPoolZh: '沪深300+中证500'
    }
  },
  {
    id: 'PRD-2024-004',
    title: 'Alert System - Drawdown Warning',
    titleZh: '预警系统 - 回撤预警',
    description: 'Automated alert system for maximum drawdown breaches and volatility spikes.',
    descriptionZh: '自动预警系统，监控最大回撤突破和波动率异常。',
    status: 'running',
    type: 'Factor Analysis',
    stage: 'production',
    progress: 100,
    created: isZh.value ? '90天前' : '90 days ago',
    duration: isZh.value ? '持续监控' : 'Monitoring',
    config: {
      stockPool: 'All Positions',
      stockPoolZh: '全部持仓'
    }
  },
  // ==================== 策略库（Archive阶段）- 保留的优质策略 ====================
  {
    id: 'ARC-2024-001',
    title: 'Momentum Strategy (Paused)',
    titleZh: '动量策略（暂停）',
    description: 'Tested momentum strategy with 15.2% annual return. Paused for market condition adjustment.',
    descriptionZh: '已验证的动量策略，年化收益15.2%。因市场环境调整暂停运行。',
    status: 'completed',
    type: 'Factor Analysis',
    stage: 'production',
    progress: 100,
    created: isZh.value ? '180天前' : '180 days ago',
    duration: isZh.value ? '策略保留中' : 'Strategy Saved',
    config: {
      stockPool: 'CSI300',
      stockPoolZh: '沪深300',
      factors: 'Momentum_20',
      factorsZh: '20日动量因子'
    }
  },
  {
    id: 'ARC-2024-002',
    title: 'Value Factor Strategy (Validated)',
    titleZh: '价值因子策略（已验证）',
    description: 'Validated value factor strategy with sharp ratio 1.85. Saved for future deployment.',
    descriptionZh: '已验证的价值因子策略，夏普比率1.85。已保留待后续部署。',
    status: 'completed',
    type: 'Factor Analysis',
    stage: 'production',
    progress: 100,
    created: isZh.value ? '365天前' : '365 days ago',
    duration: isZh.value ? '策略保留中' : 'Strategy Saved',
    config: {
      stockPool: 'All A-shares',
      stockPoolZh: '全A股',
      factors: 'Value_Factors',
      factorsZh: '价值因子组'
    }
  }
])

// 实际任务数据（从API加载或使用本地数据）
const tasks = ref<Task[]>([])

// 从API加载策略数据
const loadStrategiesFromApi = async () => {
  isLoading.value = true

  try {
    const response = await strategyLibraryApi.getStrategies()
    if (response.code === 200 && response.data && response.data.strategies.length > 0) {
      // API返回有效数据时使用API数据
      tasks.value = response.data.strategies.map(convertStrategyToTask)
    } else {
      // API返回空数据或无数据时，使用本地模拟数据作为演示
      console.log('API返回空数据，使用本地模拟数据')
      tasks.value = localTasks.value
    }
  } catch (error: any) {
    console.warn('API请求失败，使用本地数据:', error)
    // 如果API请求失败，使用本地数据作为后备
    tasks.value = localTasks.value
  } finally {
    isLoading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadStrategiesFromApi()
  loadTaskPools()  // 加载批量任务池
})

const filteredTasks = computed(() => {
  let result = tasks.value.filter((t: Task) => t.stage === currentStage.value)

  if (currentFilter.value !== 'all') {
    result = result.filter((t: Task) => t.status === currentFilter.value)
  }

  if (currentType.value !== 'all') {
    const typeMap: Record<string, string> = {
      factor: 'Factor Analysis',
      model: 'Model Training',
      backtest: 'Backtest'
    }
    result = result.filter((t: Task) => t.type === typeMap[currentType.value])
  }

  return result
})

const getStatusBadge = (status: string) => {
  const badges: Record<string, { en: string; zh: string }> = {
    running: { en: '🔄 Running', zh: '🔄 运行中' },
    queued: { en: '⏳ Queued', zh: '⏳ 排队中' },
    completed: { en: '✅ Completed', zh: '✅ 已完成' },
    failed: { en: '❌ Failed', zh: '❌ 失败' }
  }
  const badge = badges[status]
  return isZh.value ? badge.zh : badge.en
}

// 操作方法
const createNewTask = () => {
  showCreateTaskModal.value = true
}

// 新建任务池
const createNewTaskPool = () => {
  showCreateTaskPoolModal.value = true
}

const openSettings = () => {
  showSettingsModal.value = true
}

const openAnalytics = () => {
  showAnalyticsModal.value = true
}

// ==================== 模态框状态 ====================
const showCreateTaskModal = ref(false)
const showCreateTaskPoolModal = ref(false)
const showSettingsModal = ref(false)
const showAnalyticsModal = ref(false)

// 新建任务池表单
const newPoolForm = ref({
  name: '',
  description: '',
  genType: 'rolling' as 'rolling' | 'multi_loss' | 'optuna' | 'custom',
  // 滚动训练配置
  rollStep: 252,
  // 多损失函数配置
  losses: ['mse', 'ic', 'rank_ic'],
  // 超参搜索配置
  nTrials: 10
})

// 提交新建任务池
const submitNewTaskPool = async () => {
  try {
    // 1. 创建任务池
    const createResponse = await taskApi.createPool({
      name: newPoolForm.value.name,
      description: newPoolForm.value.description
    })

    if (createResponse.code === 200) {
      // 2. 刷新任务池列表
      await loadTaskPools()

      // 3. 关闭模态框并重置表单
      showCreateTaskPoolModal.value = false
      newPoolForm.value = {
        name: '',
        description: '',
        genType: 'rolling',
        rollStep: 252,
        losses: ['mse', 'ic', 'rank_ic'],
        nTrials: 10
      }

      alert(isZh.value ? `任务池 "${newPoolForm.value.name}" 创建成功` : `Task pool "${newPoolForm.value.name}" created`)
    }
  } catch (error) {
    console.error('Failed to create task pool:', error)
    alert(isZh.value ? '创建任务池失败' : 'Failed to create task pool')
  }
}

// 新建任务表单
const newTaskForm = ref({
  title: '',
  titleZh: '',
  description: '',
  descriptionZh: '',
  stage: 'research',
  stockPool: 'CSI300',
  dateStart: '2021-01-01',
  dateEnd: '2024-12-31',
  factors: '',
  model: 'LightGBM'
})

// 设置选项
const settingsForm = ref({
  autoSave: true,
  notifications: true,
  language: 'zh',
  theme: 'dark',
  refreshInterval: 30
})

// 提交新建任务
const submitNewTask = async () => {
  const stagePrefixMap: Record<string, string> = {
    research: 'RES',
    validation: 'VAL',
    production: 'PRD'
  }
  const taskId = `${stagePrefixMap[newTaskForm.value.stage] || 'RES'}-${Date.now().toString().slice(-6)}`

  const newTask: Task = {
    id: taskId,
    title: newTaskForm.value.title || 'New Task',
    titleZh: newTaskForm.value.titleZh || newTaskForm.value.title || '新任务',
    description: newTaskForm.value.description || '',
    descriptionZh: newTaskForm.value.descriptionZh || newTaskForm.value.description || '',
    status: 'queued',
    type: 'Factor Analysis',
    stage: newTaskForm.value.stage,
    progress: 0,
    created: isZh.value ? '刚刚' : 'Just now',
    duration: isZh.value ? '等待中' : 'Waiting',
    config: {
      stockPool: newTaskForm.value.stockPool,
      stockPoolZh: newTaskForm.value.stockPool === 'CSI300' ? '沪深300' :
                   newTaskForm.value.stockPool === 'CSI500' ? '中证500' : '全A股',
      dateStart: newTaskForm.value.dateStart,
      dateEnd: newTaskForm.value.dateEnd,
      factors: newTaskForm.value.factors || 'Default',
      model: newTaskForm.value.model
    }
  }

  // 添加到本地任务列表
  tasks.value.unshift(newTask)

  // 尝试同步到后端
  try {
    const stageMap: Record<string, 'research' | 'validation' | 'production' | 'library'> = {
      research: 'research',
      validation: 'validation',
      production: 'production'
    }
    const response = await strategyLibraryApi.createStrategy({
      strategyName: newTask.title,
      strategyNameZh: newTask.titleZh,
      description: newTask.description,
      descriptionZh: newTask.descriptionZh,
      stage: stageMap[newTask.stage] || 'research',
      config: {
        stockPool: newTaskForm.value.stockPool,
        stockPoolZh: newTask.config?.stockPoolZh,
        factors: newTaskForm.value.factors || 'Default',
        factorsZh: newTaskForm.value.factors,
        modelType: newTaskForm.value.model
      }
    })
    if (response.code === 200 && response.data) {
      newTask.strategyId = response.data.strategyId
    }
  } catch (error) {
    console.error('Failed to sync new task to backend:', error)
  }

  // 关闭模态框并重置表单
  showCreateTaskModal.value = false
  newTaskForm.value = {
    title: '',
    titleZh: '',
    description: '',
    descriptionZh: '',
    stage: 'research',
    stockPool: 'CSI300',
    dateStart: '2021-01-01',
    dateEnd: '2024-12-31',
    factors: '',
    model: 'LightGBM'
  }
}

// 保存设置
const saveSettings = () => {
  localStorage.setItem('workflowSettings', JSON.stringify(settingsForm.value))
  showSettingsModal.value = false
  alert(isZh.value ? '设置已保存' : 'Settings saved')
}

// 关闭模态框
const closeModal = (modal: string) => {
  if (modal === 'create') showCreateTaskModal.value = false
  else if (modal === 'settings') showSettingsModal.value = false
  else if (modal === 'analytics') showAnalyticsModal.value = false
}

const openTask = (task: Task) => {
  const routeMap: Record<string, string> = {
    research: '/research/detail',
    validation: '/validation/detail',
    production: '/production/detail'
  }
  // 传递任务ID到详情页
  router.push({
    path: routeMap[task.stage] || '/workflow',
    query: { taskId: task.id }
  })
}

// 保存到外部策略库（数据库），保持当前阶段不变
const archiveTask = async (task: Task) => {
  try {
    if (task.strategyId) {
      // 如果已有策略ID，调用归档API保存到策略库
      await strategyLibraryApi.archiveToLibrary(task.strategyId)
    } else {
      // 如果没有策略ID，创建新策略并保存到策略库
      const response = await strategyLibraryApi.createStrategy({
        strategyName: task.title,
        strategyNameZh: task.titleZh,
        description: task.description,
        descriptionZh: task.descriptionZh,
        stage: 'library',
        config: {
          stockPool: task.config?.stockPool || '',
          stockPoolZh: task.config?.stockPoolZh,
          factors: task.config?.factors || '',
          factorsZh: task.config?.factorsZh,
          modelType: task.config?.model
        }
      })
      if (response.code === 200 && response.data) {
        task.strategyId = response.data.strategyId
      }
    }
    // 提示用户已保存到策略库
    alert(isZh.value ? '策略已保存到策略库' : 'Strategy saved to library')
  } catch (error) {
    console.error('Failed to save strategy to library:', error)
    alert(isZh.value ? '保存失败' : 'Save failed')
  }
}

// 从策略库重新激活（更新数据库状态）
const restoreTask = async (task: Task) => {
  try {
    if (task.strategyId) {
      // 根据任务ID前缀判断目标阶段
      const prefix = task.id.split('-')[0]
      const stageMap: Record<string, 'validation' | 'production'> = {
        'RES': 'validation',
        'VAL': 'validation',
        'PRD': 'production'
      }
      const targetStage = stageMap[prefix] || 'validation'
      await strategyLibraryApi.reactivateStrategy(task.strategyId, targetStage)
      alert(isZh.value ? '策略已重新激活' : 'Strategy reactivated')
    }
  } catch (error) {
    console.error('Failed to reactivate strategy:', error)
    alert(isZh.value ? '激活失败' : 'Activation failed')
  }
}

// 删除任务（软删除）
const deleteTask = async (task: Task) => {
  if (confirm(isZh.value ? `确定要删除任务 ${task.id} 吗？` : `Are you sure you want to delete task ${task.id}?`)) {
    // 更新本地状态
    tasks.value = tasks.value.filter((t: Task) => t.id !== task.id)

    // 同步到后端数据库
    try {
      if (task.strategyId) {
        await strategyLibraryApi.deleteStrategy(task.strategyId)
      }
    } catch (error) {
      console.error('Failed to delete strategy from database:', error)
    }
  }
}
</script>

<style scoped>
/* ========================================
   使用全局统一配色
   ======================================== */
.workflow-manager {

  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  font-size: 13px;
  overflow: hidden;
}

/* ========================================
   主容器
   ======================================== */
.main-container {
  height: calc(100vh - 56px);
  display: flex;
  flex-direction: column;
}

/* ========================================
   状态卡片
   ======================================== */
.status-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  background: var(--bg-primary);
}

/* 功能入口 */
.feature-entries {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.status-card {
  background: var(--bg-primary);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: background 0.15s;
}

.status-card:hover {
  background: var(--bg-secondary);
}

.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.status-card.research .status-icon {
  background: rgba(41, 98, 255, 0.15);
  color: var(--accent-blue);
}

.status-card.validation .status-icon {
  background: rgba(255, 152, 0, 0.15);
  color: var(--accent-orange);
}

.status-card.production .status-icon {
  background: rgba(38, 166, 154, 0.15);
  color: var(--accent-green);
}

.status-content {
  flex: 1;
}

.status-label {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.status-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.status-detail {
  font-size: 12px;
  color: var(--text-secondary);
}

/* ========================================
   内容区域
   ======================================== */
.content-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* ========================================
   左侧侧边栏
   ======================================== */
.sidebar {
  width: 260px;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-section {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-title {
  font-size: 11px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  color: var(--text-primary);
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s;
  margin-bottom: 4px;
}

.nav-item:hover {
  background: var(--bg-tertiary);
}

.nav-item.active {
  background: var(--accent-blue);
  color: white;
}

.nav-icon {
  font-size: 16px;
}

.nav-icon-svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* ========================================
   右侧主内容
   ======================================== */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.page-subtitle {
  color: var(--text-secondary);
  margin-top: 4px;
  margin-bottom: 0;
}

.page-actions {
  display: flex;
  gap: 8px;
}

/* ========================================
   任务过滤器
   ======================================== */
.task-filters {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.filter-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 600;
}

/* ========================================
   任务网格
   ======================================== */
.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.task-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.task-card:hover {
  border-color: var(--accent-blue);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.task-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.task-id {
  font-size: 11px;
  color: var(--text-secondary);
  font-family: monospace;
}

.task-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.task-badge.running {
  background: rgba(41, 98, 255, 0.2);
  color: var(--accent-blue);
}

.task-badge.completed {
  background: rgba(38, 166, 154, 0.2);
  color: var(--accent-green);
}

.task-badge.queued {
  background: rgba(255, 152, 0, 0.2);
  color: var(--accent-orange);
}

.task-badge.failed {
  background: rgba(239, 83, 80, 0.2);
  color: var(--accent-red);
}

.task-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
}

.task-config {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.config-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 11px;
  color: var(--text-secondary);
}

.task-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: var(--text-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ========================================
   进度条
   ======================================== */
.task-progress {
  margin-top: 12px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 11px;
}

.progress-bar {
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-blue), var(--accent-green));
  border-radius: 2px;
  transition: width 0.3s;
}

/* 任务操作按钮 */
.task-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
  justify-content: flex-end;
}

/* ========================================
   空状态
   ======================================== */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* ========================================
   加载状态
   ======================================== */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--bg-tertiary);
  border-top-color: var(--accent-blue);
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ========================================
   加载状态
   ======================================== */
.loading-mini,
.empty-mini {
  padding: 12px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 12px;
}

.pool-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin: 4px 0;
  background: var(--bg-tertiary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pool-item:hover {
  background: var(--border-color);
}

.pool-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pool-stats-mini {
  display: flex;
  gap: 6px;
  margin: 0 8px;
  font-size: 11px;
  font-weight: 600;
}

.pool-stats-mini span {
  padding: 2px 6px;
  border-radius: 4px;
}

.stat-waiting {
  background: #3d3d00;
  color: #ffeb3b;
}

.stat-running {
  background: #0d3d0d;
  color: #4caf50;
}

.stat-done {
  background: #0d2d3d;
  color: #29b6f6;
}

/* ========================================
   滚动条
   ======================================== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-tertiary);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #363a45;
}

/* ========================================
   模态框样式
   ======================================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

.modal-small {
  max-width: 400px;
}

.modal-large {
  max-width: 800px;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 24px;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.modal-close:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-primary);
}

/* Form Styles */
.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
  transition: border-color 0.15s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent-blue);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* Task Pool Form Styles */
.gen-config {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.config-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-blue);
  margin-bottom: 12px;
}

.form-hint {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  transition: background 0.15s;
}

.checkbox-item:hover {
  background: var(--border-color);
}

.checkbox-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-item span {
  font-size: 13px;
  color: var(--text-primary);
}

/* Settings Styles */
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info {
  flex: 1;
}

.setting-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.setting-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.setting-select {
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-tertiary);
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: var(--text-secondary);
  transition: 0.3s;
  border-radius: 50%;
}

.toggle-switch input:checked + .toggle-slider {
  background-color: var(--accent-blue);
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(24px);
  background-color: white;
}

/* Analytics Styles */
.analytics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.analytics-card {
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 20px;
}

.analytics-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.analytics-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-item {
  text-align: center;
}

.stat-item .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-item .stat-value.running { color: var(--accent-blue); }
.stat-item .stat-value.completed { color: var(--accent-green); }
.stat-item .stat-value.queued { color: var(--accent-orange); }

.stat-item .stat-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.stage-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stage-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.stage-bar:last-child {
  margin-bottom: 0;
}

.stage-bar-label {
  width: 60px;
  font-size: 12px;
  color: var(--text-secondary);
}

.stage-bar-track {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.stage-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.stage-bar-fill.research { background: var(--accent-blue); }
.stage-bar-fill.validation { background: var(--accent-orange); }
.stage-bar-fill.production { background: var(--accent-green); }

.stage-bar-value {
  width: 30px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  text-align: right;
}

.analytics-empty {
  text-align: center;
  color: var(--text-secondary);
  padding: 20px;
}

.pool-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pool-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: 6px;
}

.pool-summary .pool-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
}

.pool-progress {
  width: 100px;
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

.pool-progress-bar {
  height: 100%;
  background: var(--accent-green);
  transition: width 0.3s;
}

.pool-count {
  font-size: 12px;
  color: var(--text-secondary);
  width: 50px;
  text-align: right;
}
</style>
