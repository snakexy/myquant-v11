<template>
  <div class="factor-engine-config">
    <!-- 顶部状态栏 -->
    <div class="status-header">
      <div class="node-info">
        <div class="node-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M9 3H5C3.89543 3 3 3.89543 3 5V9C3 10.1046 3.89543 11 5 11H9C10.1046 11 11 10.1046 11 9V5C11 3.89543 10.1046 3 9 3Z" stroke="currentColor" stroke-width="2"/>
            <path d="M19 3H15C13.8954 3 13 3.89543 13 5V9C13 10.1046 13.8954 11 15 11H19C20.1046 11 21 10.1046 21 9V5C21 3.89543 20.1046 3 19 3Z" stroke="currentColor" stroke-width="2"/>
            <path d="M9 13H5C3.89543 13 3 13.8954 3 15V19C3 20.1046 3.89543 21 5 21H9C10.1046 21 11 20.1046 11 19V15C11 13.8954 10.1046 13 9 13Z" stroke="currentColor" stroke-width="2"/>
            <path d="M19 13H15C13.8954 13 13 13.8954 13 15V19C13 20.1046 13.8954 21 15 21H19C20.1046 21 21 20.1046 21 19V15C21 13.8954 20.1046 13 19 13Z" stroke="currentColor" stroke-width="2"/>
            <path d="M12 8V16M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="node-title">
          <h3>因子计算引擎</h3>
          <span class="node-id">BL1</span>
        </div>
      </div>
      <div class="connection-status">
        <div class="status-indicator" :class="{ active: connections.dh1 }">
          <span class="status-dot"></span>
          <span class="status-label">DH1 数据驱动</span>
        </div>
        <div class="status-indicator" :class="{ active: connections.ai }">
          <span class="status-dot"></span>
          <span class="status-label">H AI助手</span>
        </div>
      </div>
    </div>

    <!-- 工作流连接检测 -->
    <div class="config-section">
      <div class="section-header">
        <h4 class="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M13 10V3L4 14H11V21L20 10H13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          工作流连接检测
        </h4>
        <button class="detect-btn" @click="detectConnections" :disabled="detecting">
          <svg v-if="!detecting" width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else class="spinning" width="14" height="14" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-dasharray="32" stroke-linecap="round"/>
          </svg>
          {{ detecting ? '检测中...' : '检测连接' }}
        </button>
      </div>
      <div class="connection-cards">
        <div
          class="connection-card"
          :class="{
            connected: workflowConnections.dh1.connected,
            selected: selectedInputs.includes('dh1')
          }"
          @click="toggleInput('dh1')"
        >
          <div class="card-header">
            <div class="card-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M4 7H20M4 12H20M4 17H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="card-info">
              <h5>DH1 数据管理节点</h5>
              <span class="card-status" :class="{ connected: workflowConnections.dh1.connected }">
                {{ workflowConnections.dh1.connected ? '已连接' : '未连接' }}
              </span>
            </div>
            <div class="card-checkbox" :class="{ checked: selectedInputs.includes('dh1') }">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="card-preview" v-if="workflowConnections.dh1.connected">
            <div class="preview-stats">
              <div class="stat-item stat-item-full">
                <span class="stat-label">已选股票清单</span>
                <div class="stock-list-container">
                  <div
                    v-for="(stock, idx) in displayStockList"
                    :key="idx"
                    class="stock-chip"
                  >
                    <span class="stock-code">{{ stock.code }}</span>
                    <div class="stock-frequencies">
                      <span
                        v-for="(freq, fidx) in stock.frequencies"
                        :key="fidx"
                        class="freq-tag"
                        :class="freq.type"
                      >
                        {{ freq.label }}
                      </span>
                    </div>
                  </div>
                  <div v-if="hasMoreStocks" class="stock-more-chip">
                    <span class="more-text">还有 {{ moreStocksCount }} 只股票...</span>
                  </div>
                </div>
              </div>
              <div class="stat-item">
                <span class="stat-label">股票数量</span>
                <span class="stat-value stat-value-highlight">{{ workflowConnections.dh1.stockCount || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">时间范围</span>
                <span class="stat-value">{{ workflowConnections.dh1.dateRange || '-' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div
          class="connection-card"
          :class="{
            connected: workflowConnections.ai.connected,
            selected: selectedInputs.includes('ai')
          }"
          @click="toggleInput('ai')"
        >
          <div class="card-header">
            <div class="card-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="card-info">
              <h5>H AI助手策略</h5>
              <span class="card-status" :class="{ connected: workflowConnections.ai.connected }">
                {{ workflowConnections.ai.connected ? '已连接' : '未连接' }}
              </span>
            </div>
            <div class="card-checkbox" :class="{ checked: selectedInputs.includes('ai') }">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <div class="card-preview" v-if="workflowConnections.ai.connected">
            <div class="preview-stats">
              <div class="stat-item">
                <span class="stat-label">策略类型</span>
                <span class="stat-value">{{ workflowConnections.ai.strategyType || '动量反转' }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">推荐因子</span>
                <span class="stat-value">{{ workflowConnections.ai.factorCount || 35 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">市场环境</span>
                <span class="stat-value">{{ workflowConnections.ai.marketCondition || '震荡市' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 双输入融合策略 -->
    <div class="config-section" v-if="selectedInputs.length > 1">
      <div class="section-header">
        <h4 class="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          双输入融合策略
        </h4>
      </div>
      <div class="fusion-strategies">
        <div
          class="fusion-option"
          :class="{ active: fusionStrategy === 'weighted' }"
          @click="fusionStrategy = 'weighted'"
        >
          <div class="option-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M12 2V22M2 12H22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="option-content">
            <h5>加权融合</h5>
            <p>按照权重比例融合两个输入源的因子</p>
          </div>
          <div class="option-weights" v-if="fusionStrategy === 'weighted'">
            <div class="weight-slider">
              <label>数据驱动 {{ fusionWeights.data }}%</label>
              <input
                type="range"
                v-model.number="fusionWeights.data"
                min="0"
                max="100"
                @input="fusionWeights.ai = 100 - fusionWeights.data"
              />
            </div>
            <div class="weight-slider">
              <label>AI助手 {{ fusionWeights.ai }}%</label>
              <input
                type="range"
                v-model.number="fusionWeights.ai"
                min="0"
                max="100"
                @input="fusionWeights.data = 100 - fusionWeights.ai"
              />
            </div>
          </div>
        </div>

        <div
          class="fusion-option"
          :class="{ active: fusionStrategy === 'priority' }"
          @click="fusionStrategy = 'priority'"
        >
          <div class="option-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="option-content">
            <h5>优先级融合</h5>
            <p>优先使用数据驱动,冲突时AI助手补充</p>
          </div>
        </div>

        <div
          class="fusion-option"
          :class="{ active: fusionStrategy === 'union' }"
          @click="fusionStrategy = 'union'"
        >
          <div class="option-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <circle cx="10" cy="12" r="6" stroke="currentColor" stroke-width="2"/>
              <circle cx="14" cy="12" r="6" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="option-content">
            <h5>并集融合</h5>
            <p>保留两个输入源的所有因子</p>
          </div>
        </div>

        <div
          class="fusion-option"
          :class="{ active: fusionStrategy === 'intersection' }"
          @click="fusionStrategy = 'intersection'"
        >
          <div class="option-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="option-content">
            <h5>交集融合</h5>
            <p>仅保留两个输入源共同的因子</p>
          </div>
        </div>
      </div>
      <button class="apply-fusion-btn" @click="applyFusion" :disabled="applyingFusion">
        <svg v-if="!applyingFusion" width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else class="spinning" width="16" height="16" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-dasharray="32" stroke-linecap="round"/>
        </svg>
        {{ applyingFusion ? '融合中...' : '应用融合策略' }}
      </button>
    </div>

    <!-- AI因子推荐 -->
    <div class="config-section" v-if="workflowConnections.ai.connected && recommendations.length > 0">
      <div class="section-header">
        <h4 class="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          AI智能推荐
        </h4>
        <span class="recommendation-badge">基于AI助手策略</span>
      </div>
      <div class="recommendation-cards">
        <div
          v-for="rec in recommendations"
          :key="rec.id"
          class="recommendation-card"
          :class="{ selected: selectedRecommendation === rec.id }"
          @click="selectRecommendation(rec)"
        >
          <div class="rec-header">
            <div class="rec-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="rec-info">
              <h5>{{ rec.name }}</h5>
              <div class="rec-meta">
                <span class="match-score">匹配度 {{ (rec.matchScore * 100).toFixed(0) }}%</span>
                <span class="factor-count">{{ rec.factorCount }}个因子</span>
              </div>
            </div>
          </div>
          <div class="rec-description">{{ rec.description }}</div>
          <div class="rec-categories">
            <span v-for="(count, cat) in rec.categories" :key="cat" class="category-tag">
              {{ getCategoryName(cat) }} {{ count }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 因子库选择器 -->
    <div class="config-section">
      <div class="section-header">
        <h4 class="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M9 3H5C3.89543 3 3 3.89543 3 5V9C3 10.1046 3.89543 11 5 11H9C10.1046 11 11 10.1046 11 9V5C11 3.89543 10.1046 3 9 3Z" stroke="currentColor" stroke-width="2"/>
            <path d="M19 3H15C13.8954 3 13 3.89543 13 5V9C13 10.1046 13.8954 11 15 11H19C20.1046 11 21 10.1046 21 9V5C21 3.89543 20.1046 3 19 3Z" stroke="currentColor" stroke-width="2"/>
            <path d="M9 13H5C3.89543 13 3 13.8954 3 15V19C3 20.1046 3.89543 21 5 21H9C10.1046 21 11 20.1046 11 19V15C11 13.8954 10.1046 13 9 13Z" stroke="currentColor" stroke-width="2"/>
            <path d="M19 13H15C13.8954 13 13 13.8954 13 15V19C13 20.1046 13.8954 21 15 21H19C20.1046 21 21 20.1046 21 19V15C21 13.8954 20.1046 13 19 13Z" stroke="currentColor" stroke-width="2"/>
          </svg>
          因子库选择
          <span class="factor-count-badge">已选 {{ selectedFactors.length }} / {{ totalFactors }}</span>
        </h4>
        <div class="section-actions">
          <div class="search-box">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <input
              type="text"
              v-model="searchQuery"
              placeholder="搜索因子..."
              class="search-input"
            />
          </div>
        </div>
      </div>

      <!-- 因子分类筛选 -->
      <div class="category-filters">
        <div
          v-for="cat in factorCategories"
          :key="cat.id"
          class="category-chip"
          :class="{ active: activeCategory === cat.id }"
          @click="activeCategory = cat.id"
        >
          <span class="chip-icon">{{ cat.icon }}</span>
          <span class="chip-label">{{ cat.name }}</span>
          <span class="chip-count">{{ cat.count }}</span>
        </div>
      </div>

      <!-- 因子列表 -->
      <div class="factors-grid">
        <div
          v-for="factor in filteredFactors"
          :key="factor.id"
          class="factor-item"
          :class="{ selected: selectedFactors.includes(factor.id) }"
          @click="toggleFactor(factor.id)"
        >
          <div class="factor-checkbox">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="factor-content">
            <div class="factor-name">{{ factor.name }}</div>
            <div class="factor-code">{{ factor.code }}</div>
          </div>
          <div class="factor-category" :class="factor.category">
            {{ getCategoryShortName(factor.category) }}
          </div>
        </div>
      </div>

      <!-- 因子模板快捷选择 -->
      <div class="factor-templates">
        <div class="template-label">快捷模板</div>
        <div class="template-buttons">
          <button
            v-for="tpl in factorTemplates"
            :key="tpl.id"
            class="template-btn"
            :class="{ active: activeTemplate === tpl.id }"
            @click="applyTemplate(tpl)"
          >
            <span class="btn-icon">{{ tpl.icon }}</span>
            <span class="btn-label">{{ tpl.name }}</span>
            <span class="btn-count">{{ tpl.count }}个</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 预处理配置 -->
    <div class="config-section">
      <div class="section-header">
        <h4 class="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          预处理配置
        </h4>
      </div>
      <div class="preprocessing-grid">
        <div class="preprocess-item">
          <div class="preprocess-header">
            <div class="preprocess-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="preprocess-info">
              <h5>异常值处理</h5>
              <small>去除极端值影响</small>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="preprocessing.outlierRemoval.enabled" />
              <span class="switch-slider"></span>
            </label>
          </div>
          <div class="preprocess-options" v-if="preprocessing.outlierRemoval.enabled">
            <select v-model="preprocessing.outlierRemoval.method">
              <option value="mad">MAD (中位数绝对偏差)</option>
              <option value="std">标准差 (3σ)</option>
              <option value="percentile">百分位数</option>
            </select>
            <input
              type="number"
              v-model.number="preprocessing.outlierRemoval.threshold"
              placeholder="阈值"
              min="1"
              max="10"
              step="0.5"
            />
          </div>
        </div>

        <div class="preprocess-item">
          <div class="preprocess-header">
            <div class="preprocess-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M12 20V10M18 20V4M6 20V16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="preprocess-info">
              <h5>标准化</h5>
              <small>统一量纲和尺度</small>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="preprocessing.standardization.enabled" />
              <span class="switch-slider"></span>
            </label>
          </div>
          <div class="preprocess-options" v-if="preprocessing.standardization.enabled">
            <select v-model="preprocessing.standardization.method">
              <option value="zscore">Z-Score 标准化</option>
              <option value="minmax">Min-Max 归一化</option>
              <option value="robust">鲁棒标准化</option>
            </select>
          </div>
        </div>

        <div class="preprocess-item">
          <div class="preprocess-header">
            <div class="preprocess-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="preprocess-info">
              <h5>中性化</h5>
              <small>去除行业市值影响</small>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="preprocessing.neutralization.enabled" />
              <span class="switch-slider"></span>
            </label>
          </div>
          <div class="preprocess-options" v-if="preprocessing.neutralization.enabled">
            <label class="checkbox-label">
              <input type="checkbox" v-model="preprocessing.neutralization.industry" />
              行业中性化
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="preprocessing.neutralization.marketCap" />
              市值中性化
            </label>
          </div>
        </div>

        <div class="preprocess-item">
          <div class="preprocess-header">
            <div class="preprocess-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M4 4H20V20H4V4Z" stroke="currentColor" stroke-width="2"/>
                <path d="M4 12H20M12 4V20" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="preprocess-info">
              <h5>缺失值处理</h5>
              <small>填充空值</small>
            </div>
            <label class="switch">
              <input type="checkbox" v-model="preprocessing.missingValue.enabled" />
              <span class="switch-slider"></span>
            </label>
          </div>
          <div class="preprocess-options" v-if="preprocessing.missingValue.enabled">
            <select v-model="preprocessing.missingValue.method">
              <option value="ffill">前向填充</option>
              <option value="bfill">后向填充</option>
              <option value="mean">均值填充</option>
              <option value="median">中位数填充</option>
              <option value="drop">删除缺失</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- 执行模式 -->
    <div class="config-section">
      <div class="section-header">
        <h4 class="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M13 10V3L4 14H11V21L20 10H13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          执行模式
        </h4>
      </div>
      <div class="execution-modes">
        <div
          class="execution-mode"
          :class="{ active: executionMode === 'calculate' }"
          @click="executionMode = 'calculate'"
        >
          <div class="mode-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M9 11L12 14L22 4M21 12V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V5C3 3.89543 3.89543 3 5 3H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="mode-content">
            <h5>仅计算</h5>
            <p>计算因子值,不做评估</p>
          </div>
        </div>

        <div
          class="execution-mode"
          :class="{ active: executionMode === 'evaluate' }"
          @click="executionMode = 'evaluate'"
        >
          <div class="mode-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="mode-content">
            <h5>计算并评估</h5>
            <p>计算因子值并评估IC/IR等指标</p>
          </div>
        </div>

        <div
          class="execution-mode"
          :class="{ active: executionMode === 'visualize' }"
          @click="executionMode = 'visualize'"
        >
          <div class="mode-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M3 3V21H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <path d="M19 9L14 14L10 10L7 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="mode-content">
            <h5>计算、评估并可视化</h5>
            <p>完整分析并生成图表</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <button class="btn-secondary" @click="saveConfig">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M19 21H5C3.89543 21 3 20.1046 3 19V5C3 3.89543 3.89543 3 5 3H16L21 8V19C21 20.1046 20.1046 21 19 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M17 21V13H7V21M7 3V8H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        保存配置
      </button>
      <button class="btn-secondary" @click="loadConfig">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M21 15V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V15M17 8L12 3M12 3L7 8M12 3V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        加载配置
      </button>
      <button class="btn-primary" @click="startCalculation" :disabled="selectedFactors.length === 0">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M13 10V3L4 14H11V21L20 10H13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        开始计算
      </button>
    </div>

    <!-- 计算进度弹窗 -->
    <div class="progress-modal" v-if="showProgress" @click.self="closeProgress">
      <div class="progress-content">
        <div class="progress-header">
          <h4>因子计算中...</h4>
          <button class="close-btn" @click="closeProgress">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="progress-body">
          <div class="progress-circle">
            <svg class="progress-ring" width="200" height="200">
              <circle
                class="progress-ring-bg"
                cx="100"
                cy="100"
                r="85"
                fill="none"
                stroke="var(--border-light)"
                stroke-width="8"
              />
              <circle
                class="progress-ring-bar"
                cx="100"
                cy="100"
                r="85"
                fill="none"
                stroke="url(#progressGradient)"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="progressCircumference"
                :stroke-dashoffset="progressOffset"
                transform="rotate(-90 100 100)"
              />
              <defs>
                <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="var(--primary-color)" />
                  <stop offset="100%" stop-color="var(--secondary-color)" />
                </linearGradient>
              </defs>
            </svg>
            <div class="progress-text">
              <div class="progress-percentage">{{ progressPercentage }}%</div>
              <div class="progress-status">{{ progressStatus }}</div>
            </div>
          </div>
          <div class="progress-details">
            <div class="detail-item">
              <span class="detail-label">已完成</span>
              <span class="detail-value">{{ progress.completed }} / {{ progress.total }} 个因子</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">计算速度</span>
              <span class="detail-value">{{ progress.speed }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">预计剩余</span>
              <span class="detail-value">{{ progress.remaining }} 秒</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">内存使用</span>
              <span class="detail-value">{{ progress.memory }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'

// Props & Emits
const props = defineProps<{
  modelValue?: any
  nodeData?: any  // 🔧 添加 nodeData prop，用于访问节点的 inputs 状态
  nodes?: any[]  // 🔧 添加所有节点数据，用于访问上游节点
}>()

// 🔧 添加调试日志
console.log('[Config] props 初始化:', { modelValue: props.modelValue, nodeData: props.nodeData, nodes: props.nodes })

const emit = defineEmits<{
  'update:modelValue': [value: any]
}>()

// 状态管理
const connections = ref({
  dh1: false,
  ai: false
})

const workflowConnections = reactive({
  dh1: {
    connected: false,
    dataType: '',
    stockCount: 0,
    dateRange: '',
    stockList: [] as Array<{ code: string; frequencies: Array<{ label: string; type: string }> }>
  },
  ai: {
    connected: false,
    strategyType: '',
    factorCount: 0,
    marketCondition: ''
  }
})

const selectedInputs = ref<string[]>([])
const fusionStrategy = ref<'weighted' | 'priority' | 'union' | 'intersection'>('weighted')
const fusionWeights = ref({ data: 70, ai: 30 })
const selectedFactors = ref<string[]>([])
const searchQuery = ref('')
const activeCategory = ref('all')
const activeTemplate = ref('')
const selectedRecommendation = ref('')
const executionMode = ref<'calculate' | 'evaluate' | 'visualize'>('evaluate')

const detecting = ref(false)
const applyingFusion = ref(false)
const showProgress = ref(false)

const recommendations = ref<any[]>([])

// 🔧 股票列表显示限制 - 最多显示10个，超出部分显示"还有X只股票..."
const MAX_DISPLAY_STOCKS = 10
const displayStockList = computed(() => {
  return workflowConnections.dh1.stockList.slice(0, MAX_DISPLAY_STOCKS)
})

const hasMoreStocks = computed(() => {
  return workflowConnections.dh1.stockList.length > MAX_DISPLAY_STOCKS
})

const moreStocksCount = computed(() => {
  return workflowConnections.dh1.stockList.length - MAX_DISPLAY_STOCKS
})

const preprocessing = reactive({
  outlierRemoval: { enabled: true, method: 'mad', threshold: 3 },
  standardization: { enabled: true, method: 'zscore' },
  neutralization: { enabled: false, industry: false, marketCap: false },
  missingValue: { enabled: false, method: 'ffill' }
})

const progress = reactive({
  completed: 0,
  total: 0,
  speed: '0 factors/sec',
  remaining: 0,
  memory: '0 MB'
})

// 因子分类
const factorCategories = [
  { id: 'all', name: '全部', icon: '📊', count: 202 },
  { id: 'technical', name: '技术因子', icon: '📈', count: 116 },
  { id: 'fundamental', name: '基本面因子', icon: '💰', count: 34 },
  { id: 'macroeconomic', name: '宏观因子', icon: '🌍', count: 26 },
  { id: 'sentiment', name: '情绪因子', icon: '💭', count: 26 }
]

// 因子模板
const factorTemplates = [
  { id: 'combo_momentum_reversal_basic', name: '动量反转基础', icon: '⚡', count: 35 },
  { id: 'combo_value_quality_basic', name: '价值质量基础', icon: '💎', count: 42 },
  { id: 'combo_growth_sentiment_basic', name: '成长情绪基础', icon: '🚀', count: 38 },
  { id: 'combo_multi_strategy_basic', name: '多策略组合', icon: '🎯', count: 65 },
  { id: 'alpha158', name: 'Alpha158', icon: '🔢', count: 158 },
  { id: 'alpha360', name: 'Alpha360', icon: '📊', count: 360 }
]

// 模拟因子数据
const allFactors = ref<any[]>([])

// 计算属性
const totalFactors = computed(() => allFactors.value.length)

const filteredFactors = computed(() => {
  let factors = allFactors.value

  // 分类筛选
  if (activeCategory.value !== 'all') {
    factors = factors.filter(f => f.category === activeCategory.value)
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    factors = factors.filter(f =>
      f.name.toLowerCase().includes(query) ||
      f.code.toLowerCase().includes(query)
    )
  }

  return factors
})

const progressCircumference = computed(() => 2 * Math.PI * 85)
const progressPercentage = computed(() => {
  if (progress.total === 0) return 0
  return Math.round((progress.completed / progress.total) * 100)
})

const progressOffset = computed(() => {
  return progressCircumference.value - (progressPercentage.value / 100) * progressCircumference.value
})

const progressStatus = computed(() => {
  const pct = progressPercentage.value
  if (pct < 30) return '正在计算技术因子...'
  if (pct < 60) return '正在计算基本面因子...'
  if (pct < 90) return '正在计算宏观因子...'
  return '正在完成最后处理...'
})

// 方法
const detectConnections = async () => {
  detecting.value = true
  try {
    const response = await axios.get('/api/v1/domain/factor_engine/workflow-connections/BL1')
    if (response.data.success) {
      const inputs = response.data.data_flow_inputs || []
      let needFetchRecommendations = false

      for (const input of inputs) {
        if (input.source_type === 'data_driven') {
          workflowConnections.dh1.connected = input.connected
          workflowConnections.dh1.dataType = input.data_preview?.data_type || '股票日线'
          // 🔧 尝试从上游数据清洗节点获取"已选标的"数量和频率信息
          // 🔧 注意：节点的 type 字段是 undefined，需要用 id 来查找
          const upstreamNode = props.nodes?.find((n: any) => n.id === 'data-cleaning')
          console.log('[Config] 找到的数据清洗节点:', upstreamNode)
          console.log('[Config] 数据清洗节点的完整对象:', JSON.stringify(upstreamNode, null, 2))
          // 🔧 尝试多种方式获取已选标的数量
          let selectedCount = 0
          let selectedStockCodes: string[] = []
          if (upstreamNode?.params?.selectedStockCodes?.length > 0) {
            selectedStockCodes = upstreamNode.params.selectedStockCodes
            selectedCount = selectedStockCodes.length
          } else if (upstreamNode?.params?.selectedStockCount > 0) {
            selectedCount = upstreamNode.params.selectedStockCount
          } else if (upstreamNode?.data?.content?.selected_stock_codes?.length > 0) {
            selectedStockCodes = upstreamNode.data.content.selected_stock_codes
            selectedCount = selectedStockCodes.length
          } else if (upstreamNode?.data?.metadata?.selectedStockCount > 0) {
            selectedCount = upstreamNode.data.metadata.selectedStockCount
          }
          console.log('[Config] 计算的已选标的数量:', selectedCount)
          console.log('[Config] 已选标的代码:', selectedStockCodes)

          // 🔧 动态生成股票列表（带频率标签）
          // 构建结构化数据用于美观展示
          const stockList: Array<{ code: string; frequencies: Array<{ label: string; type: string }> }> = []
          if (selectedStockCodes.length > 0) {
            // 解析代码频率组合 (例如: "sh000001_daily" 或 "000001_daily")
            const stockFreqMap = new Map<string, Array<{ label: string; type: string }>>()
            const freqMap: Record<string, { label: string; type: string }> = {
              'daily': { label: '日线', type: 'daily' },
              '60min': { label: '60分', type: 'intraday' },
              '1min': { label: '1分', type: 'intraday' },
              '5min': { label: '5分', type: 'intraday' },
              '15min': { label: '15分', type: 'intraday' },
              '30min': { label: '30分', type: 'intraday' },
              'weekly': { label: '周线', type: 'weekly' },
              'monthly': { label: '月线', type: 'monthly' }
            }

            selectedStockCodes.forEach((codeFreq: string) => {
              // 格式可能是 "code_frequency" 或 "market_code_frequency"
              const parts = codeFreq.split('_')
              const freq = parts[parts.length - 1] // 最后一部分是频率
              const code = parts.slice(0, -1).join('_') // 前面的部分是代码

              if (!stockFreqMap.has(code)) {
                stockFreqMap.set(code, [])
              }
              if (freqMap[freq]) {
                stockFreqMap.get(code)!.push(freqMap[freq])
              }
            })

            // 转换为数组格式
            stockFreqMap.forEach((frequencies, code) => {
              stockList.push({ code, frequencies })
            })

            console.log('[Config] 构建的股票列表:', stockList)
          }

          // 生成旧格式的 dataTypeLabel（保持兼容性）
          let dataTypeLabel = stockList.map(s => `${s.code} ${s.frequencies.map(f => f.label).join('、')}`).join(' | ')
          if (!dataTypeLabel) dataTypeLabel = '股票日线'
          console.log('[Config] 动态数据类型:', dataTypeLabel)

          if (selectedCount > 0) {
            workflowConnections.dh1.stockCount = selectedCount
            workflowConnections.dh1.dataType = dataTypeLabel
            workflowConnections.dh1.stockList = stockList
            console.log('[Config] 从上游数据清洗节点获取已选标的数量:', selectedCount)
          } else {
            workflowConnections.dh1.stockCount = input.data_preview?.stock_count || 0
            workflowConnections.dh1.stockList = []
            console.log('[Config] 使用API返回的股票数量:', input.data_preview?.stock_count || 0)
          }
          workflowConnections.dh1.dateRange = input.data_preview?.date_range || '-'
          if (input.connected) connections.value.dh1 = true
        } else if (input.source_type === 'ai_assistant') {
          workflowConnections.ai.connected = input.connected
          workflowConnections.ai.strategyType = input.strategy_preview?.strategy_name || '动量反转'
          workflowConnections.ai.factorCount = input.strategy_preview?.recommended_factors || 35
          workflowConnections.ai.marketCondition = input.strategy_preview?.market_condition || '震荡市'
          if (input.connected) {
            connections.value.ai = true
            needFetchRecommendations = true
          }
        }
      }

      // 获取AI推荐
      if (needFetchRecommendations) {
        await fetchRecommendations()
      }

      // 🔧 不再自动选择输入，只检测连接状态
      // 用户的选择由 localStorage 恢复（在 loadConfig 中）
      console.log('[Config] 检测连接完成，用户选择:', selectedInputs.value)
    }
  } catch (error) {
    console.error('检测连接失败:', error)
  } finally {
    detecting.value = false
  }
}

const toggleInput = (input: string) => {
  const index = selectedInputs.value.indexOf(input)
  if (index > -1) {
    selectedInputs.value.splice(index, 1)
  } else {
    selectedInputs.value.push(input)
  }
}

const applyFusion = async () => {
  if (selectedInputs.value.length < 2) return

  applyingFusion.value = true
  try {
    const response = await axios.post('/api/v1/domain/factor_engine/dual-input-fusion', {
      use_data_driven: selectedInputs.value.includes('dh1'),
      use_ai_assistant: selectedInputs.value.includes('ai'),
      fusion_strategy: fusionStrategy.value,
      data_weight: fusionWeights.value.data / 100,
      ai_weight: fusionWeights.value.ai / 100
    })

    if (response.data.success) {
      selectedFactors.value = response.data.merged_factors || []
    }
  } catch (error) {
    console.error('融合失败:', error)
  } finally {
    applyingFusion.value = false
  }
}

const fetchRecommendations = async () => {
  try {
    const response = await axios.post('/api/v1/domain/factor_engine/factor-recommendations', {
      workflow_stage: 'research',
      strategy_type: workflowConnections.ai.strategyType,
      market_condition: workflowConnections.ai.marketCondition
    })

    if (response.data.success) {
      recommendations.value = response.data.recommendations || []
    }
  } catch (error) {
    console.error('获取推荐失败:', error)
  }
}

const selectRecommendation = (rec: any) => {
  selectedRecommendation.value = rec.id
  selectedFactors.value = rec.factor_list || []
}

const toggleFactor = (factorId: string) => {
  const index = selectedFactors.value.indexOf(factorId)
  if (index > -1) {
    selectedFactors.value.splice(index, 1)
  } else {
    selectedFactors.value.push(factorId)
  }
}

const applyTemplate = async (tpl: any) => {
  activeTemplate.value = tpl.id
  try {
    const response = await axios.get(`/api/v1/domain/factor_engine/factor-templates`)
    if (response.data.success && response.data.templates) {
      const template = response.data.templates.find((t: any) => t.id === tpl.id)
      if (template) {
        selectedFactors.value = template.factor_list || []
      }
    }
  } catch (error) {
    console.error('应用模板失败:', error)
  }
}

const getCategoryName = (cat: string) => {
  const names: Record<string, string> = {
    technical: '技术',
    fundamental: '基本面',
    macro: '宏观',
    sentiment: '情绪'
  }
  return names[cat] || cat
}

const getCategoryShortName = (cat: string) => {
  const names: Record<string, string> = {
    technical: '技术',
    fundamental: '基本面',
    macroeconomic: '宏观',
    sentiment: '情绪'
  }
  return names[cat] || cat
}

const loadConfig = () => {
  const saved = localStorage.getItem('factor_engine_config')
  if (saved) {
    const config = JSON.parse(saved)
    selectedInputs.value = config.selectedInputs || []
    fusionStrategy.value = config.fusionStrategy || 'weighted'
    fusionWeights.value = config.fusionWeights || { data: 70, ai: 30 }
    selectedFactors.value = config.selectedFactors || []
    Object.assign(preprocessing, config.preprocessing || {})
    executionMode.value = config.executionMode || 'evaluate'
    console.log('[Config] 加载保存的配置:', config)
  }
}

const saveConfig = () => {
  const config = {
    selectedInputs: selectedInputs.value,
    fusionStrategy: fusionStrategy.value,
    fusionWeights: fusionWeights.value,
    selectedFactors: selectedFactors.value,
    preprocessing: preprocessing,
    executionMode: executionMode.value
  }
  localStorage.setItem('factor_engine_config', JSON.stringify(config))
  emit('update:modelValue', config)
  console.log('[Config] 保存配置:', config)
}

// 🔧 监听 selectedInputs 变化，自动保存配置
watch(selectedInputs, () => {
  saveConfig()
  // 🔧 同步更新节点的 inputs 状态
  updateNodeInputStates()
}, { deep: true })

// 🔧 同步更新节点的 inputs 状态（用于外部输入点的激活/停用）
const updateNodeInputStates = () => {
  if (props.nodeData?.inputs) {
    props.nodeData.inputs.forEach((input: any) => {
      if (input.id === 'data-driven') {
        input.active = selectedInputs.value.includes('dh1')
      } else if (input.id === 'ai-driven') {
        input.active = selectedInputs.value.includes('ai')
      }
    })
    console.log('[Config] 更新节点输入点状态:', props.nodeData.inputs)
  }
}

const startCalculation = async () => {
  if (selectedFactors.value.length === 0) return

  showProgress.value = true
  progress.total = selectedFactors.value.length
  progress.completed = 0

  try {
    const response = await axios.post('/api/v1/domain/factor_engine/start-calculation', {
      selected_factors: selectedFactors.value,
      preprocessing: {
        outlier_removal: preprocessing.outlierRemoval.enabled ? {
          method: preprocessing.outlierRemoval.method,
          threshold: preprocessing.outlierRemoval.threshold
        } : null,
        standardization: preprocessing.standardization.enabled ? {
          method: preprocessing.standardization.method
        } : null,
        neutralization: preprocessing.neutralization.enabled ? {
          methods: [
            preprocessing.neutralization.industry ? 'industry' : null,
            preprocessing.neutralization.marketCap ? 'market_cap' : null
          ].filter(Boolean)
        } : null,
        missing_value: preprocessing.missingValue.enabled ? {
          method: preprocessing.missingValue.method
        } : null
      },
      execution_mode: executionMode.value
    })

    if (response.data.success) {
      const taskId = response.data.task_id
      await pollProgress(taskId)
    }
  } catch (error) {
    console.error('启动计算失败:', error)
    showProgress.value = false
  }
}

const pollProgress = async (taskId: string) => {
  const interval = setInterval(async () => {
    try {
      const response = await axios.get(`/api/v1/domain/factor_engine/calculation-status/${taskId}`)
      if (response.data.success) {
        const status = response.data
        progress.completed = status.completed_factors || 0
        progress.total = status.total_factors || 0
        progress.speed = status.performance_metrics?.calculation_speed || '0 factors/sec'
        progress.remaining = status.estimated_time_remaining || 0
        progress.memory = status.performance_metrics?.memory_usage || '0 MB'

        if (status.status === 'completed') {
          clearInterval(interval)
          setTimeout(() => {
            showProgress.value = false
          }, 1000)
        }
      }
    } catch (error) {
      clearInterval(interval)
      showProgress.value = false
    }
  }, 1000)
}

const closeProgress = () => {
  showProgress.value = false
}

// 初始化
onMounted(async () => {
  // 🔧 先加载保存的配置（恢复用户的选择）
  loadConfig()

  // 模拟加载因子数据
  await loadFactorLibrary()

  // 自动检测连接（现在不会自动选择输入了，只检测连接状态）
  await detectConnections()

  // 🔧 标记初始化完成
  console.log('[Config] 初始化完成，用户选择:', selectedInputs.value)

  // 🔧 同步节点输入点状态
  updateNodeInputStates()
})

const loadFactorLibrary = async () => {
  try {
    const response = await axios.get('/api/v1/domain/factor_engine/factor-library')
    if (response.data.success) {
      const library = response.data.factor_library
      allFactors.value = []

      // 🔧 辅助函数：安全地解析因子列表
      const parseFactorList = (factors: any, category: string) => {
        if (!factors) return

        // 如果是数组，直接遍历
        if (Array.isArray(factors)) {
          factors.forEach((factor: any) => {
            allFactors.value.push({
              id: factor.id || factor.code,
              name: factor.name || factor.code,
              code: factor.code,
              category: category
            })
          })
          return
        }

        // 如果是对象，遍历值
        if (typeof factors === 'object') {
          Object.values(factors).forEach((factorList: any) => {
            if (Array.isArray(factorList)) {
              factorList.forEach((factor: any) => {
                allFactors.value.push({
                  id: factor.id || factor.code,
                  name: factor.name || factor.code,
                  code: factor.code,
                  category: category
                })
              })
            } else if (factorList && typeof factorList === 'object') {
              // 可能是嵌套的子分类
              parseFactorList(factorList, category)
            }
          })
        }
      }

      // 解析因子库 - 处理多种可能的数据结构
      const parseCategory = (categoryData: any, categoryName: string) => {
        if (!categoryData) return

        // 情况1: 有 subcategories 字段
        if (categoryData.subcategories) {
          Object.entries(categoryData.subcategories).forEach(([catName, factors]: any) => {
            parseFactorList(factors, categoryName)
          })
          return
        }

        // 情况2: 有 factors 字段
        if (categoryData.factors) {
          parseFactorList(categoryData.factors, categoryName)
          return
        }

        // 情况3: 直接是数组
        if (Array.isArray(categoryData)) {
          parseFactorList(categoryData, categoryName)
          return
        }

        // 情况4: 遍历所有字段
        Object.values(categoryData).forEach((value: any) => {
          parseFactorList(value, categoryName)
        })
      }

      // 解析各类因子
      parseCategory(library.technical_factors, 'technical')
      parseCategory(library.fundamental_factors, 'fundamental')
      parseCategory(library.macroeconomic_factors, 'macroeconomic')
      parseCategory(library.sentiment_factors, 'sentiment')

      console.log('[FactorEngine] 加载因子库成功, 总数:', allFactors.value.length)
    }
  } catch (error) {
    console.error('加载因子库失败:', error)
    // 使用模拟数据
    allFactors.value = generateMockFactors()
  }
}

const generateMockFactors = () => {
  const factors = []
  const technical = ['RSI_14', 'MACD', 'MA_5', 'MA_10', 'MA_20', 'BOLL_UPPER', 'BOLL_LOWER', 'KDJ_K', 'KDJ_D', 'CCI']
  const fundamental = ['PE_TTM', 'PB_LF', 'PS_TTM', 'PCF_OCF', 'ROE_TTM', 'ROA_TTM', 'GP_TTM', 'OPT_TTM']
  const macro = ['SHIBOR_O_N', 'CPI_YOY', 'PPI_YOY', 'PMI', 'M1_YOY', 'M2_YOY']
  const sentiment = ['TURN', 'VSTD', 'VTURNO', 'ATR_14', 'HV30', 'STD30']

  technical.forEach((code, i) => {
    factors.push({ id: code, name: `技术因子${i + 1}`, code, category: 'technical' })
  })
  fundamental.forEach((code, i) => {
    factors.push({ id: code, name: `基本面因子${i + 1}`, code, category: 'fundamental' })
  })
  macro.forEach((code, i) => {
    factors.push({ id: code, name: `宏观因子${i + 1}`, code, category: 'macroeconomic' })
  })
  sentiment.forEach((code, i) => {
    factors.push({ id: code, name: `情绪因子${i + 1}`, code, category: 'sentiment' })
  })

  return factors
}
</script>

<style lang="scss" scoped>
.factor-engine-config {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 20px;
  background: var(--bg-surface);
  border-radius: 12px;
  max-width: 1200px;
  margin: 0 auto;
}

// 状态栏
.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.2);
  border-radius: 10px;
  backdrop-filter: blur(10px);
}

.node-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.node-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 8px;
  color: #fff;
}

.node-title {
  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .node-id {
    font-size: 12px;
    color: var(--text-disabled);
    font-weight: 500;
  }
}

.connection-status {
  display: flex;
  gap: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--bg-elevated);
  border-radius: 6px;
  transition: all 0.3s ease;

  &.active {
    background: rgba(34, 197, 94, 0.15);
    border: 1px solid rgba(34, 197, 94, 0.3);

    .status-dot {
      background: var(--success-color);
      box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
    }
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--text-disabled);
    transition: all 0.3s ease;
  }

  .status-label {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

// 配置区块
.config-section {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);

  svg {
    color: var(--primary-color);
  }

  .factor-count-badge {
    margin-left: auto;
    padding: 4px 10px;
    background: rgba(37, 99, 235, 0.15);
    border: 1px solid rgba(37, 99, 235, 0.3);
    border-radius: 6px;
    font-size: 11px;
    font-weight: 500;
    color: var(--primary-color);
  }
}

.detect-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(37, 99, 235, 0.1);
  border: 1px solid rgba(37, 99, 235, 0.3);
  border-radius: 6px;
  color: var(--primary-color);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: rgba(37, 99, 235, 0.2);
    border-color: var(--primary-color);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  svg.spinning {
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// 连接卡片
.connection-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.connection-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-elevated);
    border-color: rgba(37, 99, 235, 0.3);
  }

  &.connected {
    border-color: rgba(34, 197, 94, 0.3);
  }

  &.selected {
    background: rgba(37, 99, 235, 0.1);
    border-color: var(--primary-color);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border-radius: 6px;
  color: var(--text-secondary);
}

.card-info {
  flex: 1;

  h5 {
    margin: 0 0 4px 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .card-status {
    font-size: 12px;
    color: var(--text-disabled);

    &.connected {
      color: var(--success-color);
    }
  }
}

.card-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &.checked {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: #fff;
  }

  svg {
    display: none;
  }

  &.checked svg {
    display: block;
  }
}

.card-preview {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}

.preview-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;

  .stat-label {
    font-size: 11px;
    color: var(--text-disabled);
  }

  .stat-value {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
  }

  &.stat-item-full {
    grid-column: 1 / -1;
  }

  .stat-value-highlight {
    color: #2563eb;
    font-size: 16px;
  }
}

// 股票列表容器
.stock-list-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

// 股票芯片
.stock-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  font-size: 12px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);

  &:hover {
    background: var(--bg-elevated);
    border-color: rgba(37, 99, 235, 0.3);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    transform: translateY(-1px);
  }

  .stock-code {
    font-weight: 600;
    color: var(--text-primary);
    font-family: 'Consolas', 'Monaco', monospace;
  }

  .stock-frequencies {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .freq-tag {
    display: inline-flex;
    align-items: center;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 500;
    white-space: nowrap;

    &.daily {
      background: rgba(37, 99, 235, 0.12);
      color: #2563eb;
      border: 1px solid rgba(37, 99, 235, 0.25);
    }

    &.intraday {
      background: rgba(34, 197, 94, 0.12);
      color: #16a34a;
      border: 1px solid rgba(34, 197, 94, 0.25);
    }

    &.weekly {
      background: rgba(251, 146, 60, 0.12);
      color: #ea580c;
      border: 1px solid rgba(251, 146, 60, 0.25);
    }

    &.monthly {
      background: rgba(168, 85, 247, 0.12);
      color: #9333ea;
      border: 1px solid rgba(168, 85, 247, 0.25);
    }
  }
}

// "还有更多股票"提示卡片
.stock-more-chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  background: rgba(37, 99, 235, 0.08);
  border: 1px dashed rgba(37, 99, 235, 0.3);
  border-radius: 8px;
  font-size: 11px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(37, 99, 235, 0.12);
    border-color: rgba(37, 99, 235, 0.4);
  }

  .more-text {
    color: var(--text-secondary);
    font-style: italic;
  }
}

// 融合策略
.fusion-strategies {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.fusion-option {
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-elevated);
    border-color: rgba(37, 99, 235, 0.3);
  }

  &.active {
    background: rgba(37, 99, 235, 0.15);
    border-color: var(--primary-color);
  }

  .option-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(37, 99, 235, 0.1);
    border-radius: 6px;
    color: var(--primary-color);
    margin-bottom: 10px;
  }

  .option-content {
    h5 {
      margin: 0 0 4px 0;
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }

    p {
      margin: 0;
      font-size: 12px;
      color: var(--text-disabled);
    }
  }

  .option-weights {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-light);
  }

  .weight-slider {
    margin-bottom: 8px;

    label {
      display: block;
      font-size: 11px;
      color: var(--text-secondary);
      margin-bottom: 6px;
    }

    input[type="range"] {
      width: 100%;
      height: 4px;
      background: var(--border-light);
      border-radius: 2px;
      outline: none;
      -webkit-appearance: none;

      &::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 14px;
        height: 14px;
        background: var(--primary-color);
        border-radius: 50%;
        cursor: pointer;
      }
    }
  }
}

.apply-fusion-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  svg.spinning {
    animation: spin 1s linear infinite;
  }
}

// AI推荐
.recommendation-badge {
  padding: 4px 12px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  color: #fff;
}

.recommendation-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.recommendation-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-elevated);
    border-color: rgba(37, 99, 235, 0.3);
  }

  &.selected {
    background: rgba(37, 99, 235, 0.15);
    border-color: var(--primary-color);
  }
}

.rec-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.rec-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 6px;
  color: #fff;
}

.rec-info {
  flex: 1;

  h5 {
    margin: 0 0 4px 0;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .rec-meta {
    display: flex;
    gap: 10px;
  }

  .match-score,
  .factor-count {
    font-size: 11px;
    color: var(--text-disabled);
  }

  .match-score {
    color: var(--success-color);
  }
}

.rec-description {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 10px;
  line-height: 1.5;
}

.rec-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.category-tag {
  padding: 3px 8px;
  background: rgba(37, 99, 235, 0.1);
  border: 1px solid rgba(37, 99, 235, 0.2);
  border-radius: 4px;
  font-size: 10px;
  color: var(--primary-color);
}

// 因子选择器
.section-actions {
  display: flex;
  gap: 12px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 240px;

  svg {
    position: absolute;
    left: 12px;
    color: var(--text-disabled);
  }

  .search-input {
    width: 100%;
    padding: 8px 12px 8px 36px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-light);
    border-radius: 6px;
    color: var(--text-primary);
    font-size: 13px;
    transition: all 0.2s ease;

    &:focus {
      outline: none;
      border-color: var(--primary-color);
      background: var(--border-color);
    }

    &::placeholder {
      color: var(--text-disabled);
    }
  }
}

.category-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.category-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--border-color);
    border-color: rgba(37, 99, 235, 0.3);
  }

  &.active {
    background: rgba(37, 99, 235, 0.15);
    border-color: var(--primary-color);
  }

  .chip-icon {
    font-size: 14px;
  }

  .chip-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .chip-count {
    padding: 2px 6px;
    background: var(--border-light);
    border-radius: 4px;
    font-size: 11px;
    color: var(--text-secondary);
  }
}

.factors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  padding: 4px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: var(--bg-elevated);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(37, 99, 235, 0.3);
    border-radius: 3px;

    &:hover {
      background: rgba(37, 99, 235, 0.5);
    }
  }
}

.factor-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-elevated);
    border-color: rgba(37, 99, 235, 0.3);
  }

  &.selected {
    background: rgba(37, 99, 235, 0.1);
    border-color: var(--primary-color);

    .factor-checkbox {
      background: var(--primary-color);
      border-color: var(--primary-color);
      color: #fff;
    }
  }
}

.factor-checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s ease;

  svg {
    display: none;
  }

  .factor-item.selected & {
    svg {
      display: block;
    }
  }
}

.factor-content {
  flex: 1;
  min-width: 0;
}

.factor-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.factor-code {
  font-size: 11px;
  color: var(--text-disabled);
  font-family: 'Consolas', 'Monaco', monospace;
}

.factor-category {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;

  &.technical {
    background: rgba(59, 130, 246, 0.15);
    color: #3b82f6;
  }

  &.fundamental {
    background: rgba(34, 197, 94, 0.15);
    color: var(--success-color);
  }

  &.macroeconomic {
    background: rgba(251, 146, 60, 0.15);
    color: #fb923c;
  }

  &.sentiment {
    background: rgba(236, 72, 153, 0.15);
    color: #ec4899;
  }
}

// 因子模板
.factor-templates {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

.template-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.template-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1;

  &:hover {
    background: var(--border-color);
    border-color: rgba(37, 99, 235, 0.3);
  }

  &.active {
    background: rgba(37, 99, 235, 0.15);
    border-color: var(--primary-color);
  }

  .btn-icon {
    font-size: 18px;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .btn-label {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
    line-height: 1;
  }

  .btn-count {
    font-size: 11px;
    color: var(--text-disabled);
    line-height: 1;
  }
}

// 预处理配置
.preprocessing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.preprocess-item {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 14px;
}

.preprocess-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.preprocess-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(37, 99, 235, 0.1);
  border-radius: 6px;
  color: var(--primary-color);
}

.preprocess-info {
  flex: 1;

  h5 {
    margin: 0 0 2px 0;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
  }

  small {
    font-size: 11px;
    color: var(--text-disabled);
  }
}

// 开关
.switch {
  position: relative;
  width: 44px;
  height: 24px;

  input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  .switch-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--border-light);
    border-radius: 24px;
    transition: all 0.2s ease;

    &::before {
      content: '';
      position: absolute;
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background: white;
      border-radius: 50%;
      transition: all 0.2s ease;
    }
  }

  input:checked + .switch-slider {
    background: var(--primary-color);

    &::before {
      transform: translateX(20px);
    }
  }
}

.preprocess-options {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
  display: flex;
  gap: 8px;
  flex-wrap: wrap;

  select,
  input[type="number"] {
    padding: 6px 10px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-light);
    border-radius: 4px;
    color: var(--text-primary);
    font-size: 12px;
    transition: all 0.2s ease;

    &:focus {
      outline: none;
      border-color: var(--primary-color);
    }

    option {
      background: #1a1a2e;
    }
  }

  select {
    flex: 1;
  }

  input[type="number"] {
    width: 80px;
  }
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;

  input[type="checkbox"] {
    accent-color: var(--primary-color);
  }
}

// 执行模式
.execution-modes {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.execution-mode {
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-elevated);
    border-color: rgba(37, 99, 235, 0.3);
  }

  &.active {
    background: rgba(37, 99, 235, 0.15);
    border-color: var(--primary-color);

    .mode-icon {
      background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
      color: #fff;
    }
  }

  .mode-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(37, 99, 235, 0.1);
    border-radius: 8px;
    color: var(--primary-color);
    margin-bottom: 10px;
  }

  .mode-content {
    h5 {
      margin: 0 0 4px 0;
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }

    p {
      margin: 0;
      font-size: 12px;
      color: var(--text-disabled);
      line-height: 1.4;
    }
  }
}

// 操作按钮
.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-secondary,
.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary {
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  color: var(--text-primary);

  &:hover {
    background: var(--border-color);
    border-color: var(--border-color);
  }
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: #fff;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

// 进度弹窗
.progress-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.progress-content {
  background: rgba(20, 20, 35, 0.95);
  border: 1px solid rgba(37, 99, 235, 0.2);
  border-radius: 16px;
  padding: 32px;
  width: 90%;
  max-width: 500px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h4 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .close-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-elevated);
    border: none;
    border-radius: 6px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background: var(--border-light);
      color: var(--text-primary);
    }
  }
}

.progress-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.progress-circle {
  position: relative;
  width: 200px;
  height: 200px;
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring-bg {
  stroke: var(--border-light);
}

.progress-ring-bar {
  transition: stroke-dashoffset 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.progress-percentage {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
}

.progress-status {
  font-size: 12px;
  color: var(--text-disabled);
  margin-top: 4px;
}

.progress-details {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  padding: 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;

  .detail-label {
    display: block;
    font-size: 11px;
    color: var(--text-disabled);
    margin-bottom: 4px;
  }

  .detail-value {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }
}
</style>
