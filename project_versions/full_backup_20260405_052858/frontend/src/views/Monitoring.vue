<template>
  <div class="monitoring-page">
    <GlobalNavBar />

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 左侧：策略监控网格 -->
      <div class="monitor-panel">
        <!-- 工具栏：筛选标签 + 布局 -->
        <div class="toolbar">
          <!-- 筛选标签 -->
          <div class="filter-tabs">
            <button
              v-for="tab in filterTabs"
              :key="tab.id"
              :class="['filter-tab', { active: currentFilter === tab.id }]"
              @click="currentFilter = tab.id"
            >
              <svg v-if="tab.icon === 'grid'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
              </svg>
              <svg v-else-if="tab.icon === 'play'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <svg v-else-if="tab.icon === 'pause'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="6" y="4" width="4" height="16"></rect>
                <rect x="14" y="4" width="4" height="16"></rect>
              </svg>
              <svg v-else-if="tab.icon === 'alert'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              {{ tab.name }}
              <span class="count">({{ getTabCount(tab.id) }})</span>
            </button>
          </div>

          <div class="toolbar-right">
            <span class="last-update">刷新: {{ lastUpdateTime }}</span>
            <button class="refresh-btn" @click="refreshData">
              <i class="fas fa-sync-alt" :class="{ spinning: isRefreshing }"></i>
            </button>
          </div>
        </div>

        <!-- 阶段分组显示 -->
        <div class="strategy-sections">
          <!-- 实盘阶段 -->
          <template v-if="productionStrategies.length > 0">
            <div class="section-header">
              <span class="section-icon">🚀</span>
              <span class="section-title">{{ isZh ? '实盘阶段' : 'Production' }}</span>
              <span class="section-count">({{ productionStrategies.length }})</span>
            </div>
            <div class="monitor-grid" :class="`layout-${currentLayout}`">
              <div
                v-for="strategy in productionStrategies"
                :key="strategy.id"
                class="strategy-card"
                :class="[strategy.status, { selected: selectedStrategy?.id === strategy.id }]"
                @click="selectStrategy(strategy)"
              >
                <div class="card-header">
                  <div class="strategy-name">{{ strategy.name }}</div>
                  <div class="strategy-status" :class="strategy.status">
                    <span class="status-icon">{{ getStatusIcon(strategy.status) }}</span>
                    <span class="status-text">{{ getStatusText(strategy.status) }}</span>
                  </div>
                </div>

                <!-- 信号 -->
                <div class="signal-section" v-if="strategy.signal">
                  <span class="signal-label" v-if="strategy.type === 'production'">{{ isZh ? '今日信号' : 'Today' }}:</span>
                  <span class="signal-badge" :class="strategy.signal">{{ strategy.signal }}</span>
                  <span class="signal-text" :class="strategy.signal" v-if="strategy.signalLabel">{{ getSignalLabel(strategy.signalLabel) }}</span>
                  <span class="signal-count" v-if="strategy.signalCount">({{ strategy.signalCount }}{{ isZh ? '只' : '' }})</span>
                </div>

                <!-- 今日操作 -->
                <div class="action-cards" v-if="strategy.todayBuys?.length || strategy.todaySells?.length">
                  <div class="action-card buy" v-for="(buy, idx) in strategy.todayBuys" :key="'buy-'+idx">
                    <span class="action-tag">买入</span>
                    <span class="action-code">{{ buy.code }}</span>
                    <span class="action-name">{{ buy.name }}</span>
                    <span class="action-shares">+{{ buy.shares }}{{ isZh ? '股' : '' }}</span>
                  </div>
                  <div class="action-card sell" v-for="(sell, idx) in strategy.todaySells" :key="'sell-'+idx">
                    <span class="action-tag">卖出</span>
                    <span class="action-code">{{ sell.code }}</span>
                    <span class="action-name">{{ sell.name }}</span>
                    <span class="action-shares">{{ sell.shares }}{{ isZh ? '股' : '' }}</span>
                  </div>
                </div>

                <!-- 持仓明细 -->
                <div class="positions-section" v-if="strategy.positions?.length">
                  <div class="section-header">
                    <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                    </svg>
                    <span class="section-label">{{ isZh ? '持仓明细' : 'Positions' }}</span>
                    <span class="position-count">({{ strategy.positions.length }})</span>
                    <button class="expand-btn" @click.stop="toggleExpand(strategy.id)">
                      {{ isExpanded(strategy.id) ? (isZh ? '收起' : 'Collapse') : (isZh ? '展开' : 'Expand') }}
                    </button>
                  </div>
                  <div class="positions-grid" v-show="isExpanded(strategy.id)">
                    <div
                      v-for="pos in strategy.positions.slice(0, 6)"
                      :key="pos.code"
                      class="position-card"
                      :class="[pos.pnl >= 0 ? 'up' : 'down', pos.alert]"
                    >
                      <div class="card-header">
                        <!-- 止损指示器 - 橙色警告图标闪烁 -->
                        <span class="pos-alert stop-loss" v-if="pos.alert === 'stop_loss'">
                          <svg class="alert-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                          </svg>
                          <span class="alert-label">{{ isZh ? '止损' : 'Stop' }}</span>
                        </span>
                        <!-- 止盈指示器 - 绿色金钱图标闪烁 -->
                        <span class="pos-alert take-profit" v-else-if="pos.alert === 'take_profit'">
                          <svg class="alert-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="12" y1="1" x2="12" y2="23"></line>
                            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                          </svg>
                          <span class="alert-label">{{ isZh ? '止赢' : 'Profit' }}</span>
                        </span>
                        <span class="pos-alert new" v-else-if="pos.alert === 'new'">🟡</span>
                        <span class="pos-code">{{ pos.code }}</span>
                        <span class="pos-name">{{ pos.name }}</span>
                      </div>
                      <div class="card-body">
                        <div class="card-row">
                          <span class="label">{{ isZh ? '持股' : 'Shares' }}</span>
                          <span class="value">{{ pos.shares }}{{ isZh ? '股' : '' }}</span>
                        </div>
                        <div class="card-row">
                          <span class="label">{{ isZh ? '成本' : 'Cost' }}</span>
                          <span class="value">¥{{ pos.costPrice?.toFixed(2) }}</span>
                        </div>
                        <div class="card-row">
                          <span class="label">{{ isZh ? '现价' : 'Current' }}</span>
                          <span class="value">¥{{ pos.currentPrice?.toFixed(2) }}</span>
                        </div>
                        <div class="card-row" v-if="pos.holdDays">
                          <span class="label">{{ isZh ? '持有' : 'Hold' }}</span>
                          <span class="value">{{ pos.holdDays }}{{ isZh ? '天' : 'd' }}</span>
                        </div>
                      </div>
                      <div class="card-footer">
                        <span class="pnl-label">{{ isZh ? '盈亏' : 'P&L' }}</span>
                        <span class="pnl-value" :class="pos.pnl >= 0 ? 'up' : 'down'">
                          {{ pos.pnl >= 0 ? '+' : '' }}¥{{ pos.pnl }}
                        </span>
                        <span class="pnl-percent" :class="pos.pnlPercent >= 0 ? 'up' : 'down'">
                          ({{ pos.pnlPercent >= 0 ? '+' : '' }}{{ pos.pnlPercent?.toFixed(2) }}%)
                        </span>
                      </div>
                    </div>
                    <div class="more-positions" v-if="strategy.positions.length > 6">
                      {{ isZh ? '还有 ' : '+' }}{{ strategy.positions.length - 6 }}{{ isZh ? ' 只' : ' more' }}
                    </div>
                  </div>
                </div>

                <!-- 综合走势图区域 - TVLineChart净值曲线 -->
                <div class="comprehensive-chart" v-if="strategy.netValueData && strategy.netValueData.length > 0">
                  <div class="chart-main">
                    <div class="chart-info">
                      <div class="info-item">
                        <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                          <polyline points="17 6 23 6 23 12"></polyline>
                        </svg>
                        <span class="info-value" :class="strategy.aiDirection">{{ strategy.aiPrediction }}%</span>
                        <span class="info-label">AI</span>
                      </div>
                      <div class="info-item" v-if="strategy.factors?.alpha001">
                        <span class="info-icon-text">α</span>
                        <span class="info-value" :class="strategy.factors.alpha001 >= 0 ? 'up' : 'down'">{{ strategy.factors.alpha001 > 0 ? '+' : '' }}{{ strategy.factors.alpha001.toFixed(2) }}</span>
                      </div>
                      <div class="info-item" v-if="strategy.todayPnL !== undefined">
                        <span class="info-icon-text">¥</span>
                        <span class="info-value" :class="strategy.todayPnL >= 0 ? 'up' : 'down'">{{ strategy.todayPnL >= 0 ? '+' : '-' }}{{ Math.abs(strategy.todayPnL).toLocaleString() }}</span>
                      </div>
                      <div class="info-item" v-if="strategy.totalPnL !== undefined">
                        <span class="info-icon-text">¥</span>
                        <span class="info-value" :class="strategy.totalPnL >= 0 ? 'up' : 'down'">{{ strategy.totalPnL >= 0 ? '+' : '-' }}{{ Math.abs(strategy.totalPnL).toLocaleString() }}</span>
                      </div>
                      <div class="info-item" v-if="strategy.sharpe !== undefined">
                        <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                        </svg>
                        <span class="info-value">{{ strategy.sharpe }}</span>
                        <span class="info-label">Sharpe</span>
                      </div>
                      <div class="info-item" v-if="strategy.maxDD !== undefined">
                        <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
                          <polyline points="17 18 23 18 23 12"></polyline>
                        </svg>
                        <span class="info-value down">{{ strategy.maxDD }}%</span>
                        <span class="info-label">MaxDD</span>
                      </div>
                    </div>
                  </div>
                  <!-- TVLineChart净值曲线组件 -->
                  <TVLineChart
                    :title="isZh ? '策略收益' : 'Strategy Return'"
                    :strategy-data="strategy.netValueData"
                    :benchmark-data="strategy.benchmarkData"
                    :dates="strategy.netValueData.map(d => d.time)"
                    :strategy-label="isZh ? '策略' : 'Strategy'"
                    :benchmark-label="isZh ? '基准(沪深300)' : 'Benchmark(CSI300)'"
                    :strategy-color="'#4a90d9'"
                    :benchmark-color="'#b0b3bc'"
                    :show-period-selector="true"
                    :resizable="true"
                    :height="180"
                    :locale="isZh ? 'zh-CN' : 'en-US'"
                    :custom-periods="[
                      { label: isZh ? '小时' : '1H', value: '1h' },
                      { label: isZh ? '日线' : '1D', value: '1d' },
                      { label: isZh ? '1周' : '1W', value: '1w' },
                      { label: isZh ? '1月' : '1M', value: '1m' },
                      { label: isZh ? '3月' : '3M', value: '3m' },
                      { label: isZh ? '6月' : '6M', value: '6m' },
                      { label: isZh ? '1年' : '1Y', value: '1y' },
                      { label: isZh ? '全部' : 'All', value: 'all' }
                    ]"
                    :extra-series="strategy.aiPredictionData ? [
                      { data: strategy.aiPredictionData, color: '#ff9800', label: isZh ? 'AI预测' : 'AI Prediction', dashed: true }
                    ] : []"
                  />
                </div>

                <!-- 简化的sparkline（当没有净值曲线数据时） -->
                <div class="comprehensive-chart" v-else-if="strategy.positionValue !== undefined">
                  <div class="chart-main">
                    <div class="chart-info">
                      <div class="info-item">
                        <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                          <polyline points="17 6 23 6 23 12"></polyline>
                        </svg>
                        <span class="info-value" :class="strategy.aiDirection">{{ strategy.aiPrediction }}%</span>
                        <span class="info-label">AI</span>
                      </div>
                      <div class="info-item" v-if="strategy.factors?.alpha001">
                        <span class="info-icon-text">α</span>
                        <span class="info-value" :class="strategy.factors.alpha001 >= 0 ? 'up' : 'down'">{{ strategy.factors.alpha001 > 0 ? '+' : '' }}{{ strategy.factors.alpha001.toFixed(2) }}</span>
                      </div>
                      <div class="info-item" v-if="strategy.todayPnL !== undefined">
                        <span class="info-icon-text">¥</span>
                        <span class="info-value" :class="strategy.todayPnL >= 0 ? 'up' : 'down'">{{ strategy.todayPnL >= 0 ? '+' : '-' }}{{ Math.abs(strategy.todayPnL).toLocaleString() }}</span>
                      </div>
                      <div class="info-item" v-if="strategy.totalPnL !== undefined">
                        <span class="info-icon-text">¥</span>
                        <span class="info-value" :class="strategy.totalPnL >= 0 ? 'up' : 'down'">{{ strategy.totalPnL >= 0 ? '+' : '-' }}{{ Math.abs(strategy.totalPnL).toLocaleString() }}</span>
                      </div>
                      <div class="info-item" v-if="strategy.sharpe !== undefined">
                        <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                        </svg>
                        <span class="info-value">{{ strategy.sharpe }}</span>
                        <span class="info-label">Sharpe</span>
                      </div>
                      <div class="info-item" v-if="strategy.maxDD !== undefined">
                        <svg class="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
                          <polyline points="17 18 23 18 23 12"></polyline>
                        </svg>
                        <span class="info-value down">{{ strategy.maxDD }}%</span>
                        <span class="info-label">MaxDD</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Qlib特色（无走势图时显示） -->
                <div class="qlib-info" v-if="strategy.positionValue === undefined">
                  <div class="ai-signal" v-if="strategy.aiPrediction !== undefined">
                    <span class="ai-icon">{{ strategy.aiDirection === 'up' ? '▲' : strategy.aiDirection === 'down' ? '▼' : '─' }}</span>
                    <span class="ai-value" :class="strategy.aiDirection">{{ Math.abs(strategy.aiPrediction) }}%</span>
                  </div>
                  <div class="factors" v-if="strategy.factors">
                    <span class="factor" v-if="strategy.factors.alpha001 !== undefined">α:{{ strategy.factors.alpha001 > 0 ? '+' : '' }}{{ strategy.factors.alpha001.toFixed(2) }}</span>
                  </div>
                </div>

                <!-- 盈亏（无走势图时显示） -->
                <div class="metrics" v-if="strategy.positionValue === undefined">
                  <div class="metric-row">
                    <div class="metric" v-if="strategy.todayPnL !== undefined">
                      <span class="label">{{ isZh ? '今日' : 'Today' }}</span>
                      <span class="value" :class="strategy.todayPnL >= 0 ? 'up' : 'down'">
                        {{ strategy.todayPnL >= 0 ? '+' : '-' }}¥{{ Math.abs(strategy.todayPnL).toLocaleString() }} ({{ strategy.todayPnLPercent }}%)
                      </span>
                    </div>
                    <div class="metric" v-if="strategy.totalPnL !== undefined">
                      <span class="label">{{ isZh ? '累计' : 'Total' }}</span>
                      <span class="value" :class="strategy.totalPnL >= 0 ? 'up' : 'down'">
                        {{ strategy.totalPnL >= 0 ? '+' : '-' }}¥{{ Math.abs(strategy.totalPnL).toLocaleString() }} ({{ strategy.totalPnLPercent }}%)
                      </span>
                    </div>
                    <span class="metric-tag" v-if="strategy.sharpe !== undefined">Sharpe: {{ strategy.sharpe }}</span>
                    <span class="metric-tag" v-if="strategy.maxDD !== undefined">MaxDD: {{ strategy.maxDD }}%</span>
                  </div>
                </div>

                <!-- 错误信息 -->
                <div class="error-msg" v-if="strategy.error">
                  {{ strategy.error }}
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- 右侧：策略详情面板 -->
      <div class="detail-panel">
        <div class="panel-header">
          <h3>{{ isZh ? '策略详情' : 'Strategy Detail' }}</h3>
        </div>

        <div v-if="selectedStrategy" class="detail-content">
          <!-- 基本信息 -->
          <div class="detail-section">
            <h4>{{ selectedStrategy.name }}</h4>
            <div class="detail-row">
              <span class="label">{{ isZh ? '类型' : 'Type' }}</span>
              <span class="value">{{ selectedStrategy.type === 'validation' ? (isZh ? '验证阶段' : 'Validation') : (isZh ? '实盘阶段' : 'Production') }}</span>
            </div>
            <div class="detail-row">
              <span class="label">{{ isZh ? '状态' : 'Status' }}</span>
              <span class="value status-badge" :class="selectedStrategy.status">
                {{ getStatusText(selectedStrategy.status) }}
              </span>
            </div>
          </div>

          <!-- AI预测信号 -->
          <div class="detail-section" v-if="selectedStrategy.aiPrediction !== undefined">
            <h5>{{ isZh ? 'AI预测信号' : 'AI Prediction' }}</h5>
            <div class="ai-prediction">
              <div class="prediction-direction" :class="selectedStrategy.aiDirection">
                <span class="dir-icon">{{ selectedStrategy.aiDirection === 'up' ? '▲' : selectedStrategy.aiDirection === 'down' ? '▼' : '─' }}</span>
                <span class="dir-value">{{ Math.abs(selectedStrategy.aiPrediction) }}%</span>
              </div>
              <div class="confidence">
                <span class="label">{{ isZh ? '置信度' : 'Confidence' }}:</span>
                <span class="value" :class="selectedStrategy.aiConfidence">{{ selectedStrategy.aiConfidence === 'high' ? (isZh ? '高' : 'High') : selectedStrategy.aiConfidence === 'medium' ? (isZh ? '中' : 'Medium') : (isZh ? '低' : 'Low') }}</span>
              </div>
            </div>
            <div class="signal-display" v-if="selectedStrategy.signal">
              <span class="label">{{ isZh ? '策略信号' : 'Signal' }}:</span>
              <span class="signal-tag" :class="selectedStrategy.signal">{{ getSignalLabel(selectedStrategy.signalLabel || '持有') }}</span>
            </div>
          </div>

          <!-- 因子分析 -->
          <div class="detail-section" v-if="selectedStrategy.factors">
            <h5>{{ isZh ? '因子分析' : 'Factor Analysis' }}</h5>
            <div class="factors-grid">
              <div class="factor-item" v-for="(value, key) in selectedStrategy.factors" :key="key">
                <span class="factor-name">{{ key }}</span>
                <span class="factor-value" :class="value !== undefined && value >= 0 ? 'positive' : 'negative'">
                  {{ value !== undefined ? (value > 0 ? '+' : '') + value.toFixed(3) : '-' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 技术指标 -->
          <div class="detail-section" v-if="selectedStrategy.technicalIndicators">
            <h5>{{ isZh ? '技术指标' : 'Technical Indicators' }}</h5>
            <div class="tech-indicators">
              <div class="tech-item" v-if="selectedStrategy.technicalIndicators.rsi">
                <span class="tech-label">RSI</span>
                <span class="tech-value" :class="selectedStrategy.technicalIndicators.rsiStatus">
                  {{ selectedStrategy.technicalIndicators.rsi }}
                  <span class="tech-status">({{ selectedStrategy.technicalIndicators.rsiStatus === 'overbought' ? (isZh ? '超买' : 'Overbought') : selectedStrategy.technicalIndicators.rsiStatus === 'oversold' ? (isZh ? '超卖' : 'Oversold') : (isZh ? '中性' : 'Neutral') }})</span>
                </span>
              </div>
              <div class="tech-item" v-if="selectedStrategy.technicalIndicators.macd">
                <span class="tech-label">MACD</span>
                <span class="tech-value" :class="selectedStrategy.technicalIndicators.macd">
                  {{ selectedStrategy.technicalIndicators.macd === 'golden' ? (isZh ? '金叉' : 'Golden Cross') : selectedStrategy.technicalIndicators.macd === 'death' ? (isZh ? '死叉' : 'Death Cross') : (isZh ? '中性' : 'Neutral') }}
                </span>
              </div>
            </div>
          </div>

          <!-- 验证指标 -->
          <div class="detail-section" v-if="selectedStrategy.validationMetrics">
            <h5>{{ isZh ? '验证指标' : 'Validation Metrics' }}</h5>
            <div class="metrics-list">
              <div
                v-for="metric in selectedStrategy.validationMetrics"
                :key="metric.nameKey"
                class="metric-item"
                :class="metric.status"
              >
                <span class="metric-icon">{{ getMetricIcon(metric.status) }}</span>
                <span class="metric-name">{{ getValidationName(metric.nameKey) }}</span>
                <span class="metric-value" v-if="metric.value">{{ metric.value }}</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="detail-actions">
            <button class="btn btn-primary" v-if="selectedStrategy.type === 'validation'">
              {{ isZh ? '终止验证' : 'Stop Validation' }}
            </button>
            <button class="btn btn-secondary" v-if="selectedStrategy.type === 'validation'">
              {{ isZh ? '部署实盘' : 'Deploy' }}
            </button>
            <button class="btn btn-secondary">
              {{ isZh ? '查看详情' : 'View Details' }}
            </button>
          </div>
        </div>

        <div v-else class="no-selection">
          <p>{{ isZh ? '选择一个策略查看详情' : 'Select a strategy to view details' }}</p>
        </div>
      </div>

      <!-- 底部：实时预警 -->
      <div class="alerts-panel">
        <div class="panel-header">
          <h3>📢 {{ isZh ? '实时预警' : 'Real-time Alerts' }}</h3>
          <button class="clear-btn" @click="clearAlerts">{{ isZh ? '清除' : 'Clear' }}</button>
        </div>

        <div class="alerts-list">
          <div
            v-for="alert in alerts"
            :key="alert.id"
            class="alert-item"
            :class="[alert.level, { unread: !alert.read }]"
          >
            <span class="time">{{ alert.time }}</span>
            <span class="indicator" :class="alert.level"></span>
            <span class="content">
              <strong>[{{ alert.strategy }}]</strong>
              {{ alert.messageKey ? getAlertMessage(alert.messageKey, alert.params as Record<string, string>) : (alert as any).message }}
            </span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import TVLineChart, { type Time } from '@/components/charts/TVLineChart.vue'
import GlobalNavBar from '@/components/GlobalNavBar.vue'


// ========== 类型定义 ==========
type StrategyStatus = 'validating' | 'running' | 'stopped' | 'error'
type StrategyType = 'validation' | 'production'
type MetricStatus = 'pass' | 'warning' | 'pending' | 'fail'

interface ValidationMetric {
  nameKey: string
  status: MetricStatus
  value?: string
}

interface Factors {
  alpha001?: number
  beta?: number
  momentum?: number
  volatility?: number
  [key: string]: number | undefined
}

interface TechnicalIndicators {
  rsi?: number
  rsiStatus?: 'overbought' | 'oversold' | 'neutral'
  macd?: 'golden' | 'death' | 'neutral'
}

interface Strategy {
  id: string
  name: string
  type: StrategyType
  status: StrategyStatus
  progress?: number

  // 股票买卖信号（核心监控功能）
  buyStocks?: StockSignal[]   // 今日买入股票
  sellStocks?: StockSignal[]  // 今日卖出股票

  // 持仓股票（核心监控功能）
  positions?: Position[]

  // 今日操作
  todayBuys?: StockAction[]
  todaySells?: StockAction[]

  // Qlib特色字段
  aiPrediction?: number
  aiConfidence?: 'high' | 'medium' | 'low'
  aiDirection?: 'up' | 'down' | 'neutral'
  signal?: string
  signalLabel?: string
  factors?: Factors
  technicalIndicators?: TechnicalIndicators

  // 验证阶段
  validationRange?: string
  daysRun?: number
  validationMetrics?: ValidationMetric[]

  // 实盘阶段
  todaySignal?: string
  signalCount?: number
  positionValue?: number
  positionValueChange?: number
  positionValueHistory?: number[]
  // 净值曲线数据 (TVLineChart格式)
  netValueData?: { time: Time; value: number }[]
  benchmarkData?: { time: Time; value: number }[]
  aiPredictionData?: { time: Time; value: number }[]
  todayPnL?: number
  todayPnLPercent?: number
  totalPnL?: number
  totalPnLPercent?: number

  // 共同
  return?: number
  sharpe?: number
  maxDD?: number
  error?: string
  lastUpdate?: string
}

interface StockSignal {
  code: string
  name: string
  price?: number
  change?: number
  reason?: string
}

// 持仓股票（核心监控功能）
interface Position {
  code: string
  name: string
  shares: number
  costPrice: number
  currentPrice: number
  pnl: number
  pnlPercent: number
  holdDays?: number
  alert?: 'stop_loss' | 'take_profit' | 'new' | null
}

// 股票操作（买入/卖出）
interface StockAction {
  code: string
  name: string
  shares: number
  amount: number
}

// ========== 国际化 ==========
const isZh = ref(true)

// ========== 净值曲线周期选择 ==========
const chartPeriod = ref('all')
const chartPeriods = computed(() => [
  { value: '1w', label: isZh.value ? '1周' : '1W' },
  { value: '1m', label: isZh.value ? '1月' : '1M' },
  { value: '3m', label: isZh.value ? '3月' : '3M' },
  { value: '6m', label: isZh.value ? '6月' : '6M' },
  { value: 'all', label: isZh.value ? '全部' : 'All' }
])

// 根据周期筛选数据
const filterDataByPeriod = (history: number[], period: string) => {
  if (!history || history.length === 0) return history
  if (period === 'all') return history

  // 模拟周期：假设数据点是按时间顺序排列的
  // 1周 = 7个点, 1月 = 30个点, 3月 = 90个点, 6月 = 180个点
  let cutoff = history.length
  switch (period) {
    case '1w':
      cutoff = Math.min(7, history.length)
      break
    case '1m':
      cutoff = Math.min(30, history.length)
      break
    case '3m':
      cutoff = Math.min(90, history.length)
      break
    case '6m':
      cutoff = Math.min(180, history.length)
      break
  }
  return history.slice(-cutoff)
}

// 验证指标翻译映射
const validationNames: Record<string, { zh: string; en: string }> = {
  returnValidation: { zh: '收益率验证', en: 'Return Validation' },
  sharpeValidation: { zh: 'Sharpe验证', en: 'Sharpe Validation' },
  turnoverValidation: { zh: '换手率验证', en: 'Turnover Validation' },
  drawdownValidation: { zh: '回撤验证', en: 'Drawdown Validation' },
  returnStability: { zh: '收益稳定性', en: 'Return Stability' },
  factorDecay: { zh: '因子衰减', en: 'Factor Decay' }
}

const getValidationName = (nameKey: string) => {
  return isZh.value ? validationNames[nameKey]?.zh || nameKey : validationNames[nameKey]?.en || nameKey
}

// 信号标签翻译映射
const signalLabels: Record<string, { zh: string; en: string }> = {
  '强烈买入': { zh: '强烈买入', en: 'Strong Buy' },
  '买入': { zh: '买入', en: 'Buy' },
  '卖出': { zh: '卖出', en: 'Sell' },
  '强烈卖出': { zh: '强烈卖出', en: 'Strong Sell' },
  '持有': { zh: '持有', en: 'Hold' }
}

const getSignalLabel = (label: string) => {
  return isZh.value ? signalLabels[label]?.zh || label : signalLabels[label]?.en || label
}

// ========== 筛选标签 ==========
const filterTabs = computed(() => [
  { id: 'all', name: isZh.value ? '全部' : 'All', icon: 'grid' },
  { id: 'running', name: isZh.value ? '实盘运行' : 'Running', icon: 'play' },
  { id: 'stopped', name: isZh.value ? '已停止' : 'Stopped', icon: 'pause' },
  { id: 'error', name: isZh.value ? '异常' : 'Error', icon: 'alert' }
])

const currentFilter = ref('all')

const getTabCount = (tabId: string) => {
  // 只统计实盘阶段的策略
  const productionOnly = strategies.value.filter(s => s.type === 'production')
  if (tabId === 'all') return productionOnly.length
  return productionOnly.filter(s => s.status === tabId).length
}

// ========== 布局（自适应）==========
const currentLayout = ref('2x2') // 默认布局

// ========== 刷新状态 ==========
const isRefreshing = ref(false)
const lastUpdateTime = ref('14:30:25')

// ========== 净值曲线数据生成函数 ==========
// 生成策略净值数据
const generateNetValueData = (days: number): { time: Time; value: number }[] => {
  const data: { time: Time; value: number }[] = []
  let value = 1.0
  const now = new Date()

  for (let i = days; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    const timeStr = date.toISOString().split('T')[0] as Time

    // 模拟策略净值增长（带有随机波动）
    const change = (Math.random() - 0.45) * 0.02
    value = value * (1 + change)
    data.push({ time: timeStr, value })
  }
  return data
}

// 生成完整的净值数据（包含历史+AI预测）
// 返回 { netValueData, benchmarkData, aiPredictionData }
const generateAllNetValueData = (days: number) => {
  const now = new Date()

  // 生成策略净值历史
  const netValueData: { time: Time; value: number }[] = []
  let netValue = 1.0

  // 生成基准历史
  const benchmarkData: { time: Time; value: number }[] = []
  let benchmarkValue = 1.0

  for (let i = days; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    const timeStr = date.toISOString().split('T')[0] as Time

    const netChange = (Math.random() - 0.45) * 0.02
    netValue = netValue * (1 + netChange)
    netValueData.push({ time: timeStr, value: netValue })

    const benchChange = (Math.random() - 0.48) * 0.015
    benchmarkValue = benchmarkValue * (1 + benchChange)
    benchmarkData.push({ time: timeStr, value: benchmarkValue })
  }

  // AI预测从最后一个净值开始
  const aiPredictionData: { time: Time; value: number }[] = []
  let aiValue = netValue // 从策略最后一个净值开始
  const lastDate = new Date(netValueData[netValueData.length - 1].time as string)

  for (let i = 1; i <= 30; i++) {
    const date = new Date(lastDate)
    date.setDate(date.getDate() + i)
    const timeStr = date.toISOString().split('T')[0] as Time

    const aiChange = (Math.random() - 0.4) * 0.025
    aiValue = aiValue * (1 + aiChange)
    aiPredictionData.push({ time: timeStr, value: aiValue })
  }

  return { netValueData, benchmarkData, aiPredictionData }
}

// 生成基准净值数据 (沪深300)
const generateBenchmarkData = (days: number): { time: Time; value: number }[] => {
  const data: { time: Time; value: number }[] = []
  let value = 1.0
  const now = new Date()

  for (let i = days; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    const timeStr = date.toISOString().split('T')[0] as Time

    // 模拟基准波动
    const change = (Math.random() - 0.48) * 0.015
    value = value * (1 + change)
    data.push({ time: timeStr, value })
  }
  return data
}

// 生成AI预测数据 (未来30天)
// 从传入的最后净值和日期开始预测
const generateAIPredictionData = (lastValue: number, lastTime: Time): { time: Time; value: number }[] => {
  const data: { time: Time; value: number }[] = []
  let value = lastValue

  // 解析最后日期
  const lastDate = new Date(lastTime as string)

  for (let i = 1; i <= 30; i++) {
    const date = new Date(lastDate)
    date.setDate(date.getDate() + i)
    const timeStr = date.toISOString().split('T')[0] as Time

    // AI预测：更乐观的增长预期，从最后值开始
    const change = (Math.random() - 0.4) * 0.025
    value = value * (1 + change)
    data.push({ time: timeStr, value })
  }
  return data
}

// 预生成净值曲线数据（供mock使用）
const mockNetValueData = generateAllNetValueData(180)

// ========== 策略数据 ==========
const strategies = ref<Strategy[]>([
  // 验证阶段
  {
    id: '1',
    name: 'Alpha158-科技股轮动',
    type: 'validation',
    status: 'validating',
    progress: 65,
    validationRange: '2025.01-2025.12',
    daysRun: 156,
    return: 28.5,
    sharpe: 1.85,
    maxDD: -8,
    // 持仓股票
    positions: [
      { code: '600519', name: '贵州茅台', shares: 100, costPrice: 180, currentPrice: 185, pnl: 500, pnlPercent: 2.78, holdDays: 30 },
      { code: '000858', name: '五粮液', shares: 50, costPrice: 170, currentPrice: 168, pnl: -100, pnlPercent: -1.18, holdDays: 15 },
      { code: '600000', name: '浦发银行', shares: 200, costPrice: 10, currentPrice: 12, pnl: 400, pnlPercent: 20, holdDays: 5 }
    ],
    // 今日操作
    todayBuys: [
      { code: '600519', name: '贵州茅台', shares: 100, amount: 18000 }
    ],
    todaySells: [
      { code: '000858', name: '五粮液', shares: -50, amount: 8500 }
    ],
    // 盈亏
    todayPnL: -300,
    todayPnLPercent: -0.5,
    totalPnL: 12000,
    totalPnLPercent: 8.5,
    // Qlib特色
    aiPrediction: 73,
    aiConfidence: 'high',
    aiDirection: 'up',
    signal: 'B',
    signalLabel: '强烈买入',
    factors: { alpha001: 0.82, beta: 1.15, momentum: 0.23, volatility: 0.15 },
    technicalIndicators: { rsi: 72, rsiStatus: 'overbought', macd: 'golden' },
    validationMetrics: [
      { nameKey: 'returnValidation', status: 'pass' },
      { nameKey: 'sharpeValidation', status: 'pass' },
      { nameKey: 'turnoverValidation', status: 'pass' }
    ]
  },
  {
    id: '2',
    name: 'Momentum-短线动量',
    type: 'validation',
    status: 'validating',
    progress: 32,
    validationRange: '2025.06-2025.12',
    daysRun: 98,
    return: 15.2,
    sharpe: 1.2,
    maxDD: -12,
    // 持仓股票
    positions: [
      { code: '300750', name: '宁德时代', shares: 200, costPrice: 180, currentPrice: 175, pnl: -1000, pnlPercent: -2.78, holdDays: 8 },
      { code: '002594', name: '比亚迪', shares: 150, costPrice: 250, currentPrice: 265, pnl: 2250, pnlPercent: 6, holdDays: 12 }
    ],
    // 今日操作
    todayBuys: [],
    todaySells: [
      { code: '300750', name: '宁德时代', shares: -100, amount: 17500 }
    ],
    // 盈亏
    todayPnL: -800,
    todayPnLPercent: -1.2,
    totalPnL: 8500,
    totalPnLPercent: 5.2,
    // Qlib特色
    aiPrediction: -45,
    aiConfidence: 'medium',
    aiDirection: 'down',
    signal: 'S',
    signalLabel: '卖出',
    factors: { alpha001: -0.31, beta: 0.89, momentum: -0.15, volatility: 0.22 },
    technicalIndicators: { rsi: 35, rsiStatus: 'oversold', macd: 'death' },
    validationMetrics: [
      { nameKey: 'returnValidation', status: 'pass' },
      { nameKey: 'drawdownValidation', status: 'warning', value: '-12%' },
      { nameKey: 'returnStability', status: 'pending' },
      { nameKey: 'factorDecay', status: 'pending' }
    ]
  },
  // 实盘阶段
  {
    id: '3',
    name: 'Beta对冲-蓝筹股',
    type: 'production',
    status: 'running',
    // 持仓股票
    positions: [
      { code: '600036', name: '招商银行', shares: 500, costPrice: 35, currentPrice: 38, pnl: 1500, pnlPercent: 8.57, holdDays: 20 },
      { code: '601318', name: '中国平安', shares: 300, costPrice: 52, currentPrice: 50, pnl: -600, pnlPercent: -3.85, holdDays: 45 },
      { code: '000001', name: '平安银行', shares: 1000, costPrice: 12, currentPrice: 11, pnl: -1000, pnlPercent: -8.33, holdDays: 10, alert: 'stop_loss' }
    ],
    // 今日操作
    todayBuys: [
      { code: '600036', name: '招商银行', shares: 500, amount: 17500 }
    ],
    todaySells: [
      { code: '601318', name: '中国平安', shares: -300, amount: 15600 }
    ],
    // 盈亏
    positionValue: 800000,
    positionValueChange: 2.5,
    // 策略收益数据 (TVLineChart格式) - 180天历史 + AI预测
    ...mockNetValueData,
    todayPnL: -2300,
    todayPnLPercent: -0.3,
    totalPnL: 45000,
    totalPnLPercent: 6,
    sharpe: 1.2,
    maxDD: -5,
    aiPrediction: 68,
    aiConfidence: 'high',
    aiDirection: 'up',
    signal: 'B',
    signalLabel: '买入',
    factors: { alpha001: 0.75, beta: 0.95, momentum: 0.12, volatility: 0.10 }
  },
  {
    id: '4',
    name: 'ML-Ensemble',
    type: 'production',
    status: 'error',
    error: '因子数据获取超时',
    lastUpdate: '14:10',
    totalPnL: 12000,
    totalPnLPercent: 3.5,
    aiPrediction: 0,
    aiConfidence: 'low',
    aiDirection: 'neutral'
  }
])

// ========== 计算属性 ==========
const filteredStrategies = computed(() => {
  if (currentFilter.value === 'all') return strategies.value
  return strategies.value.filter(s => s.status === currentFilter.value)
})

const productionStrategies = computed(() => {
  return filteredStrategies.value.filter(s => s.type === 'production')
})

// 卡片展开/收起状态
const expandedCards = ref<Set<string>>(new Set())

// 持仓市值走势图生成
const getPositionSparklinePoints = (history: number[], width = 100, height = 30) => {
  if (!history || history.length === 0) return ''
  const min = Math.min(...history)
  const max = Math.max(...history)
  const range = max - min || 1

  return history.map((val, i) => {
    const x = (i / (history.length - 1)) * width
    const y = height - ((val - min) / range) * height
    return `${x},${y}`
  }).join(' ')
}

const getPositionSparklineArea = (history: number[], width = 100, height = 30) => {
  if (!history || history.length === 0) return ''
  const min = Math.min(...history)
  const max = Math.max(...history)
  const range = max - min || 1

  const points = history.map((val, i) => {
    const x = (i / (history.length - 1)) * width
    const y = height - ((val - min) / range) * height
    return `${x},${y}`
  })

  return `0,${height} ${points.join(' ')} ${width},${height}`
}

const getPositionSparklineAverage = (history: number[], width = 100, height = 30) => {
  if (!history || history.length === 0) return height / 2
  const avg = history.reduce((a, b) => a + b, 0) / history.length
  const min = Math.min(...history)
  const max = Math.max(...history)
  const range = max - min || 1
  return height - ((avg - min) / range) * height
}

const getPositionSparklineEnd = (history: number[], width = 100, height = 30) => {
  if (!history || history.length === 0) return { x: width, y: height / 2 }
  const min = Math.min(...history)
  const max = Math.max(...history)
  const range = max - min || 1
  const lastVal = history[history.length - 1]
  return {
    x: width,
    y: height - ((lastVal - min) / range) * height
  }
}

const selectedStrategy = ref<Strategy | null>(null)

// ========== 方法 ==========
const selectStrategy = (strategy: Strategy) => {
  selectedStrategy.value = strategy
}

const toggleExpand = (strategyId: string) => {
  if (expandedCards.value.has(strategyId)) {
    expandedCards.value.delete(strategyId)
  } else {
    expandedCards.value.add(strategyId)
  }
}

const isExpanded = (strategyId: string) => {
  return expandedCards.value.has(strategyId)
}

const refreshData = () => {
  isRefreshing.value = true
  const now = new Date()
  lastUpdateTime.value = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  setTimeout(() => {
    isRefreshing.value = false
  }, 1000)
}

const getStatusIcon = (status: string) => {
  const icons: Record<string, string> = {
    validating: '🔄',
    running: '🟢',
    stopped: '🔴',
    error: '🟡'
  }
  return icons[status] || '⚪'
}

const getStatusText = (status: string) => {
  const texts: Record<string, { zh: string; en: string }> = {
    validating: { zh: '验证中', en: 'Validating' },
    running: { zh: '运行中', en: 'Running' },
    stopped: { zh: '已停止', en: 'Stopped' },
    error: { zh: '异常', en: 'Error' }
  }
  return isZh.value ? texts[status]?.zh || status : texts[status]?.en || status
}

const getMetricIcon = (status: string) => {
  const icons: Record<string, string> = {
    pass: '✓',
    warning: '⚠',
    pending: '○',
    fail: '✗'
  }
  return icons[status] || '○'
}

// ========== 预警 ==========
const alerts = ref([
  { id: '1', time: '14:30', strategy: 'Alpha158', level: 'info', messageKey: 'validationProgress', params: { value: '65%' }, read: false },
  { id: '2', time: '14:25', strategy: 'Momentum', level: 'warning', messageKey: 'drawdownThreshold', params: { value: '-12%' }, read: false },
  { id: '3', time: '14:10', strategy: 'ML-Ensemble', level: 'error', messageKey: 'factorDataTimeout', params: {}, read: true },
  { id: '4', time: '14:05', strategy: 'Alpha158', level: 'info', messageKey: 'aiPredictionUp', params: { value: '73%' }, read: true }
])

// 预警消息翻译
const alertMessages: Record<string, { zh: string; en: string }> = {
  validationProgress: { zh: '验证进度 {value}', en: 'Validation progress {value}' },
  drawdownThreshold: { zh: '回撤超过阈值 {value}', en: 'Drawdown exceeds threshold {value}' },
  factorDataTimeout: { zh: '因子数据获取超时', en: 'Factor data timeout' },
  aiPredictionUp: { zh: 'AI预测概率提升至{value}', en: 'AI prediction probability increased to {value}' }
}

const getAlertMessage = (messageKey: string, params: Record<string, string> = {}) => {
  const template = isZh.value ? alertMessages[messageKey]?.zh || messageKey : alertMessages[messageKey]?.en || messageKey
  return template.replace(/\{(\w+)\}/g, (_, key) => params[key] || '')
}

const clearAlerts = () => {
  alerts.value = []
}
</script>

<style lang="scss" scoped>
// ========== 统一使用全局配色 ==========
:scope, .monitoring-page {
  background: var(--bg-primary, #131722);
}

// ========== 主布局 ==========
.monitoring-page {
  min-height: 100vh;
  background: var(--bg-primary, #131722);
  overflow: auto;
  display: flex;
  flex-direction: column;
  color: var(--text-primary);
  margin: 0;
  padding: 0;
}

.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 400px;
  grid-template-rows: 1fr auto;
  gap: 1px;
  background: var(--border-color);
  overflow: hidden;
}


// ========== 监控面板 ==========
.monitor-panel {
  background: var(--bg-primary);
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  grid-column: 1;
  grid-row: 1;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 40px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  gap: 16px;
}

.filter-tabs {
  display: flex;
  align-items: center;
  height: 100%;
  gap: 4px;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary, #cbd5e1);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  &:hover {
    color: var(--text-primary, #d1d4dc);
  }
  &.active {
    color: var(--accent-blue, #2962ff);
    border-bottom-color: var(--accent-blue, #2962ff);
  }
  .tab-icon {
    width: 14px;
    height: 14px;
    flex-shrink: 0;
  }
  .count { color: var(--text-muted); font-size: 12px; }
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  .last-update { font-size: 12px; color: var(--text-muted); }
}

.refresh-btn {
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  background: transparent; border: none; border-radius: 4px;
  color: var(--text-muted); cursor: pointer;
  &:hover { background: rgba(255,255,255,0.05); color: var(--text-primary); }
  .spinning { animation: spin 1s linear infinite; }
}

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

// ========== 阶段分组 ==========
.strategy-sections {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  margin-bottom: 12px;
  .section-icon {
    font-size: 14px;
    width: 14px;
    height: 14px;
  }
  .section-title { font-size: 14px; font-weight: 600; color: var(--text-primary); }
  .section-count { font-size: 12px; color: var(--text-muted); }
}

// ========== 策略网格（自适应布局）==========
.monitor-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 24px;
  // 自适应列数，最小300px宽度
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  // 默认2行高度
  grid-auto-rows: minmax(280px, auto);
}

// ========== 策略卡片 ==========
.strategy-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 12px;
  &:hover { background: var(--bg-secondary); border-color: var(--border-color); }
  &.selected { border-color: var(--border-color); border-width: 2px; }
  &.running .status-icon { color: var(--success); }
  &.error .status-icon { color: var(--warning); }
  &.stopped .status-icon { color: var(--danger); }
  &.validating .status-icon { color: var(--accent-blue); }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  .strategy-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
  .strategy-status {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    &.running { color: var(--success); }
    &.error { color: var(--warning); }
    &.stopped { color: var(--danger); }
    &.validating { color: var(--accent-blue); }
  }
}

.progress-section {
  display: flex;
  align-items: center;
  gap: 8px;
  .progress-bar {
    flex: 1;
    height: 6px;
    background: var(--border-color);
    border-radius: 3px;
    overflow: hidden;
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--accent-blue), #7c3aed);
      border-radius: 3px;
    }
  }
  .progress-text { font-size: 12px; color: var(--text-muted); min-width: 35px; }
}

.qlib-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  .ai-signal {
    display: flex;
    align-items: center;
    gap: 4px;
    .ai-icon { font-size: 12px; }
    .ai-value { font-size: 13px; font-weight: 600;
      &.up { color: var(--up-color); }
      &.down { color: var(--down-color); }
      &.neutral { color: var(--text-muted); }
    }
    .ai-label { font-size: 11px; color: var(--text-muted); }
  }
  .factors {
    display: flex;
    gap: 8px;
    .factor { font-size: 11px; color: var(--text-muted); }
  }
  .tech-indicators {
    display: flex;
    gap: 8px;
    .tech {
      font-size: 10px;
      padding: 2px 4px;
      border-radius: 2px;
      &.overbought { background: rgba(239,83,80,0.2); color: var(--up-color); }
      &.oversold { background: rgba(38,166,154,0.2); color: var(--down-color); }
      &.golden { background: rgba(239,83,80,0.2); color: var(--up-color); }
      &.death { background: rgba(38,166,154,0.2); color: var(--down-color); }
      &.neutral { background: rgba(255,255,255,0.05); color: var(--text-muted); }
    }
  }
}

.metrics {
  display: block;
  margin-top: -4px;
  .metric-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
  }
  .metric {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    .label { font-size: 11px; color: var(--text-muted); }
    .value { font-size: 12px; font-weight: 500; color: var(--text-primary);
      &.up { color: var(--up-color); }
      &.down { color: var(--down-color); }
    }
  }
  .metric-tag {
    font-size: 11px;
    color: var(--text-secondary);
    background: var(--bg-tertiary);
    padding: 2px 8px;
    border-radius: 3px;
  }
}

.action-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
  .action-card {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    background: var(--bg-tertiary);
    padding: 3px 8px;
    border-radius: 4px;
    border-left: 2px solid;
    &.buy {
      border-color: #ef5350;
      .action-tag { color: #ef5350; }
    }
    &.sell {
      border-color: #26a69a;
      .action-tag { color: #26a69a; }
    }
    .action-tag {
      font-weight: 600;
    }
    .action-code {
      color: var(--accent-blue);
      font-family: monospace;
    }
    .action-name {
      color: var(--text-secondary);
    }
    .action-shares {
      color: var(--text-muted);
    }
  }
}

.comprehensive-chart {
  margin-top: 4px;
  .chart-period-selector {
    display: flex;
    gap: 4px;
    margin-bottom: 6px;
    .period-btn {
      padding: 2px 8px;
      font-size: 10px;
      border: 1px solid var(--border-color, #2a2e39);
      background: var(--bg-secondary);
      color: var(--text-muted);
      border-radius: 3px;
      cursor: pointer;
      transition: all 0.2s;
      &:hover {
        border-color: var(--primary-color, #4a90d9);
        color: var(--text-primary);
      }
      &.active {
        background: var(--primary-color, #4a90d9);
        border-color: var(--primary-color, #4a90d9);
        color: #fff;
      }
    }
  }
  .chart-main {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .chart-info {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    flex: 1;
    min-width: 0;
    .info-item {
      display: inline-flex;
      align-items: center;
      gap: 3px;
      font-size: 12px;
      background: var(--bg-tertiary);
      padding: 3px 8px;
      border-radius: 3px;
      .info-icon {
        width: 12px;
        height: 12px;
        opacity: 0.7;
      }
      .info-icon-text {
        font-size: 13px;
        font-weight: 600;
        opacity: 0.7;
      }
      .info-value {
        font-weight: 600;
        font-size: 13px;
        color: var(--text-primary);
        &.up { color: #ef5350; }  // 红色 = 涨（A股）
        &.down { color: #26a69a; } // 绿色 = 跌（A股）
      }
      .info-label {
        color: var(--text-muted);
        font-size: 10px;
      }
    }
  }
  .value-sparkline {
    width: 200px;
    height: 60px;
    flex-shrink: 0;
    polyline, circle {
      &.up { color: #26a69a; }
      &.down { color: #ef5350; }
    }
  }

  // TVLineChart容器样式
  .tv-line-chart {
    margin-top: 8px;
    border-radius: 6px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color, #2a2e39);
    overflow: hidden;

    .tv-toolbar {
      padding: 5px 8px;
      border-bottom: 1px solid var(--border-color, #2a2e39);
      background: var(--bg-secondary);

      .chart-title {
        font-size: 7px;
        font-weight: 600;
      }

      .period-btn {
        padding: 1px 5px;
        font-size: 6px;
      }

      .legend {
        .legend-item {
          font-size: 6px;
        }
      }
    }

    .tv-chart-area {
      height: 180px;
    }
  }
}

// 今日操作
.today-actions {
  margin-top: 2px;
  padding: 4px 0;

  .action-label {
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 6px;
  }

  .action-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .action-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;

    .action-tag {
      padding: 1px 4px;
      border-radius: 2px;
      font-size: 10px;
      font-weight: 500;
    }

    &.buy .action-tag {
      background: rgba(239, 83, 80, 0.2);
      color: #ef5350;
    }

    &.sell .action-tag {
      background: rgba(38, 166, 154, 0.2);
      color: #26a69a;
    }

    .action-stock {
      color: var(--text-primary);
      flex: 1;
    }

    .action-shares {
      color: var(--text-secondary);
    }

    .action-amount {
      color: var(--text-muted);
    }
  }
}

// 持仓明细
.positions-section {
  margin-top: -4px;
  padding: 2px 0 0 0;

  .section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 2px;

    .section-label {
      font-size: 11px;
      color: var(--text-muted);
    }

    .position-count {
      font-size: 10px;
      color: var(--text-muted);
      flex: 1;
    }

    .expand-btn {
      background: transparent;
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      font-size: 10px;
      padding: 2px 8px;
      border-radius: 3px;
      cursor: pointer;
      &:hover { background: var(--bg-hover); }
    }
  }

  .positions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 6px;
    max-height: 180px;
    overflow-y: auto;
    padding-right: 4px;

    &::-webkit-scrollbar {
      width: 4px;
    }
    &::-webkit-scrollbar-track {
      background: var(--bg-secondary);
      border-radius: 2px;
    }
    &::-webkit-scrollbar-thumb {
      background: var(--border-color);
      border-radius: 2px;
      &:hover { background: var(--text-muted); }
    }
  }

  .position-card {
    background: var(--bg-tertiary, #2a2e39);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    padding: 6px;
    font-size: 10px;
    transition: all 0.2s ease;

    &:hover {
      border-color: var(--accent-blue);
      transform: translateY(-1px);
    }

    &.up {
      border-left: 3px solid #ef5350;
      .pnl-value, .pnl-percent { color: #ef5350; }
    }

    &.down {
      border-left: 3px solid #26a69a;
      .pnl-value, .pnl-percent { color: #26a69a; }
    }

    &.stop_loss {
      border-left: 3px solid #f44336;
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 4px;
      margin-bottom: 4px;
      padding-bottom: 4px;
      border-bottom: 1px dashed var(--border-color);

      .pos-alert {
        font-size: 8px;
        display: inline-flex;
        align-items: center;
        gap: 2px;

        &.stop-loss {
          color: #ff9800;
          animation: blink-orange 1s ease-in-out infinite;

          .alert-icon {
            width: 12px;
            height: 12px;
          }

          .alert-label {
            font-size: 9px;
            font-weight: 600;
          }
        }

        &.take-profit {
          color: #ef5350;
          animation: blink-red 1s ease-in-out infinite;

          .alert-icon {
            width: 12px;
            height: 12px;
          }

          .alert-label {
            font-size: 9px;
            font-weight: 600;
          }
        }
      }

      @keyframes blink-orange {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
      }

      @keyframes blink-red {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
      }

      .pos-code {
        color: var(--accent-blue);
        font-weight: 600;
        font-family: monospace;
      }

      .pos-name {
        color: var(--text-secondary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
      }
    }

    .card-body {
      display: flex;
      flex-direction: column;
      gap: 2px;
      margin-bottom: 4px;

      .card-row {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .label {
          color: var(--text-muted);
        }

        .value {
          color: var(--text-primary);
          font-weight: 500;
        }
      }
    }

    .card-footer {
      display: flex;
      align-items: baseline;
      gap: 4px;
      padding-top: 4px;
      border-top: 1px dashed var(--border-color);

      .pnl-label {
        color: var(--text-muted);
        font-size: 9px;
      }

      .pnl-value {
        font-weight: 600;
        font-size: 11px;
      }

      .pnl-percent {
        font-size: 9px;
      }
    }
  }

  .more-positions {
    grid-column: 1 / -1;
    font-size: 10px;
    color: var(--text-muted);
    text-align: center;
    padding: 6px;
    background: var(--bg-hover);
    border-radius: 4px;
  }
}

.signal-section {
  display: flex;
  align-items: center;
  gap: 8px;
  .signal-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px; height: 28px;
    border-radius: 4px;
    font-size: 14px; font-weight: 700;
    &.B, &.BS { background: rgba(239,83,80,0.2); color: #ef5350; }  // 红色 = 买入（A股）
    &.S, &.SS { background: rgba(38,166,154,0.2); color: #26a69a; }  // 绿色 = 卖出（A股）
    &.H { background: rgba(255,255,255,0.1); color: var(--text-muted); }
  }
  .signal-text {
    font-size: 12px;
    font-weight: 600;
    &.B, &.BS { color: #ef5350; }  // 红色 = 买入（A股）
    &.S, &.SS { color: #26a69a; }  // 绿色 = 卖出（A股）
    &.H { color: var(--text-muted); }
  }
  .signal-count { font-size: 12px; color: var(--text-muted); }
}

.error-msg {
  font-size: 12px;
  color: var(--danger);
  padding: 8px;
  background: rgba(239,68,68,0.1);
  border-radius: 4px;
}

// ========== 详情面板 ==========
.detail-panel {
  background: var(--bg-secondary);
  grid-row: 1 / -1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-left: 1px solid var(--border-color);
  .panel-header {
    padding: 16px;
    border-bottom: 1px solid var(--border-color);
    h3 { margin: 0; font-size: 14px; font-weight: 600; color: var(--text-primary); }
  }
  .detail-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }
  .detail-section {
    margin-bottom: 20px;
    h4 { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 12px; }
    h5 { font-size: 12px; font-weight: 500; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px; }
    .detail-row {
      display: flex;
      justify-content: space-between;
      padding: 6px 0;
      border-bottom: 1px solid var(--border-color);
      .label { font-size: 12px; color: var(--text-muted); }
      .value { font-size: 12px; color: var(--text-primary); }
      .status-badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        &.running { background: rgba(16,185,129,0.2); color: var(--success); }
        &.error { background: rgba(245,158,11,0.2); color: var(--warning); }
        &.validating { background: rgba(41,98,255,0.2); color: var(--accent-blue); }
      }
    }
  }
  .ai-prediction {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 12px;
    .prediction-direction {
      display: flex;
      align-items: center;
      gap: 4px;
      .dir-icon { font-size: 20px; }
      .dir-value { font-size: 24px; font-weight: 700; }
      &.up { color: var(--up-color); }
      &.down { color: var(--down-color); }
      &.neutral { color: var(--text-muted); }
    }
    .confidence {
      .label { font-size: 12px; color: var(--text-muted); }
      .value { font-size: 12px; font-weight: 600;
        &.high { color: var(--success); }
        &.medium { color: var(--warning); }
        &.low { color: var(--text-muted); }
      }
    }
  }
  .signal-display {
    display: flex;
    align-items: center;
    gap: 8px;
    .label { font-size: 12px; color: var(--text-muted); }
    .signal-tag {
      padding: 4px 12px;
      border-radius: 4px;
      font-size: 12px; font-weight: 600;
      &.B { background: rgba(239,83,80,0.2); color: var(--up-color); }
      &.S { background: rgba(38,166,154,0.2); color: var(--down-color); }
    }
  }
  .factors-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    .factor-item {
      display: flex;
      justify-content: space-between;
      padding: 6px 8px;
      background: rgba(255,255,255,0.02);
      border-radius: 4px;
      .factor-name { font-size: 11px; color: var(--text-muted); }
      .factor-value { font-size: 12px; font-weight: 600;
        &.positive { color: var(--up-color); }
        &.negative { color: var(--down-color); }
      }
    }
  }
  .tech-indicators {
    .tech-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid var(--border-color);
      .tech-label { font-size: 12px; color: var(--text-muted); }
      .tech-value {
        font-size: 12px; font-weight: 500;
        &.overbought { color: var(--up-color); }
        &.oversold { color: var(--down-color); }
        &.golden { color: var(--up-color); }
        &.death { color: var(--down-color); }
        .tech-status { font-size: 10px; opacity: 0.8; }
      }
    }
  }
  .metrics-list {
    .metric-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px;
      border-radius: 4px;
      margin-bottom: 4px;
      &.pass { background: rgba(16,185,129,0.1); }
      &.warning { background: rgba(245,158,11,0.1); }
      &.fail { background: rgba(239,68,68,0.1); }
      &.pending { background: rgba(255,255,255,0.02); }
      .metric-icon { font-size: 12px; width: 16px; }
      .metric-name { flex: 1; font-size: 12px; color: var(--text-primary); }
      .metric-value { font-size: 11px; color: var(--text-muted); }
    }
  }
  .detail-actions {
    display: flex;
    gap: 8px;
    margin-top: 16px;
    .btn {
      flex: 1;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-primary {
      background: var(--accent-blue);
      border: none;
      color: white;
      &:hover { background: var(--accent-blue); }
    }
    .btn-secondary {
      background: transparent;
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      &:hover { background: rgba(255,255,255,0.05); }
    }
  }
  .no-selection {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    font-size: 14px;
  }
}

// ========== 预警面板 ==========
.alerts-panel {
  background: var(--bg-primary);
  grid-column: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-top: 1px solid var(--border-color);
  max-height: 180px;
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    flex-shrink: 0;
    h3 { margin: 0; font-size: 13px; font-weight: 600; color: var(--text-primary); }
    .clear-btn {
      padding: 4px 12px;
      background: transparent;
      border: 1px solid var(--border-color);
      border-radius: 4px;
      color: var(--text-muted);
      font-size: 12px;
      cursor: pointer;
      &:hover { background: rgba(255,255,255,0.05); color: var(--text-primary); }
    }
  }
  .alerts-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }
  .alert-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 4px;
    background: rgba(255,255,255,0.02);
    &:hover { background: rgba(255,255,255,0.05); }
    &.unread { background: rgba(41,98,255,0.08); }
    .time { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }
    .indicator {
      width: 8px; height: 8px;
      border-radius: 50%;
      flex-shrink: 0;
      &.info { background: var(--accent-blue); }
      &.warning { background: var(--warning); }
      &.error { background: var(--danger); }
    }
    .content { font-size: 12px; color: var(--text-muted);
      strong { color: var(--text-primary); margin-right: 4px; }
    }
  }
}

// 涨跌色
.up { color: var(--up-color); }
.down { color: var(--down-color); }
</style>
