<template>
  <div class="risk-management-view">
    <GlobalNavBar />

    <!-- 子导航标签页 -->
    <div class="sub-nav">
      <div class="sub-nav-tabs">
        <button
          :class="['sub-tab', { active: activeModule === 'risk' }]"
          @click="activeModule = 'risk'"
        >
          <svg class="icon-sub" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          {{ isZh ? '风险监控' : 'Risk Monitor' }}
        </button>
        <button
          :class="['sub-tab', { active: activeModule === 'position' }]"
          @click="activeModule = 'position'"
        >
          <svg class="icon-sub" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 2a10 10 0 0 1 10 10"></path>
            <path d="M12 12L12 2"></path>
            <path d="M12 12L22 12"></path>
          </svg>
          {{ isZh ? '仓位管理' : 'Position' }}
        </button>
        <button
          :class="['sub-tab', { active: activeModule === 'rules' }]"
          @click="activeModule = 'rules'"
        >
          <svg class="icon-sub" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="8" y1="6" x2="21" y2="6"></line>
            <line x1="8" y1="12" x2="21" y2="12"></line>
            <line x1="8" y1="18" x2="21" y2="18"></line>
            <line x1="3" y1="6" x2="3.01" y2="6"></line>
            <line x1="3" y1="12" x2="3.01" y2="12"></line>
            <line x1="3" y1="18" x2="3.01" y2="18"></line>
          </svg>
          {{ isZh ? '风控规则' : 'Rules' }}
        </button>
        <button
          :class="['sub-tab', { active: activeModule === 'events' }]"
          @click="activeModule = 'events'"
        >
          <svg class="icon-sub" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          {{ isZh ? '风险事件' : 'Events' }}
        </button>
      </div>
    </div>

    <!-- 主容器 -->
    <div class="main-container">
      <!-- 主内容区 -->
      <main class="main-content">
        <!-- ===== 风险监控模块 ===== -->
        <template v-if="activeModule === 'risk'">
          <!-- 页面标题 -->
          <div class="module-header">
            <div class="header-left">
              <div class="title-row">
                <div class="title-icon risk">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                  </svg>
                </div>
                <div class="title-text">
                  <h1 class="page-title">{{ isZh ? '风险监控' : 'Risk Monitor' }}</h1>
                  <span class="page-subtitle">{{ isZh ? '实时风险指标与限额配置' : 'Real-time risk metrics and limits' }}</span>
                </div>
              </div>
            </div>
            <div class="header-right">
              <button class="btn-secondary" @click="refreshRiskAnalysis" :disabled="analysisLoading">
                <svg class="icon-sm" :class="{ spinning: analysisLoading }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="23 4 23 10 17 10"></polyline>
                  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                </svg>
                {{ isZh ? '刷新分析' : 'Refresh' }}
              </button>
              <button class="btn-primary" @click="runStressTest" :disabled="stressTestLoading">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                </svg>
                {{ stressTestLoading ? (isZh ? '测试中...' : 'Testing...') : (isZh ? '运行压力测试' : 'Stress Test') }}
              </button>
              <button
                :class="['btn-monitor', monitoringActive ? 'active' : '']"
                @click="toggleMonitoring"
              >
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polygon v-if="!monitoringActive" points="10 8 16 12 10 16 10 8"></polygon>
                  <rect v-else x="9" y="9" width="6" height="6"></rect>
                </svg>
                {{ monitoringActive ? (isZh ? '停止监控' : 'Stop') : (isZh ? '启动监控' : 'Start') }}
              </button>
            </div>
          </div>

          <!-- ===== 大盘风险监控 ===== -->
          <div class="market-risk-section">
            <div class="section-header">
              <div class="section-title">
                <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="2" y1="12" x2="22" y2="12"></line>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
                <span>{{ isZh ? '大盘风险' : 'Market Risk' }}</span>
              </div>
              <div class="market-time">{{ isZh ? '更新时间: ' : 'Updated: ' }}{{ marketUpdateTime }}</div>
            </div>

            <!-- 市场情绪指标卡片 -->
            <div class="sentiment-cards">
              <!-- 涨跌停 -->
              <SummaryCard
                :icon="limitIcon"
                :value="String(marketSentiment.limitUp) + ' / ' + String(marketSentiment.limitDown)"
                :label="isZh ? '涨跌停' : 'Limit Up/Down'"
                :subtitle="(isZh ? '涨停 ' : 'Up ') + marketSentiment.limitUp + ' | ' + (isZh ? '跌停 ' : 'Down ') + marketSentiment.limitDown"
                :icon-color="limitStatus === 'up' ? 'red' : limitStatus === 'down' ? 'green' : 'blue'"
              />

              <!-- 涨跌比 -->
              <SummaryCard
                :icon="ratioIcon"
                :value="marketSentiment.upDownRatio.toFixed(2)"
                :label="isZh ? '涨跌比' : 'Up/Down Ratio'"
                :subtitle="(marketSentiment.upRatio * 100).toFixed(0) + '% ' + (isZh ? '上涨' : 'Rising')"
                :icon-color="marketSentiment.upRatio >= 0.5 ? 'red' : 'green'"
              />

              <!-- 成交额 -->
              <SummaryCard
                :icon="volumeIcon"
                :value="marketSentiment.turnover"
                :label="isZh ? '成交额' : 'Volume'"
                :subtitle="(marketSentiment.turnoverChange >= 0 ? '+' : '') + marketSentiment.turnoverChange.toFixed(1) + '%'"
                :icon-color="marketSentiment.turnoverChange >= 0 ? 'red' : 'green'"
                :value-color="marketSentiment.turnoverChange >= 0 ? 'profit' : 'loss'"
              />

              <!-- 北向资金 -->
              <SummaryCard
                :icon="northIcon"
                :value="(marketSentiment.northBound >= 0 ? '+' : '') + marketSentiment.northBound"
                :label="isZh ? '北向资金' : 'North Bound'"
                :subtitle="marketSentiment.northBoundDays + (isZh ? '天连续流入' : ' days in')"
                :icon-color="marketSentiment.northBound >= 0 ? 'red' : 'green'"
                :value-color="marketSentiment.northBound >= 0 ? 'profit' : 'loss'"
              />
            </div>

            <!-- 板块涨跌 -->
            <div class="sector-section">
              <SectorListCard
                :items="topGainers"
                type="gainers"
                :title="isZh ? '涨幅榜' : 'Top Gainers'"
                :icon="upTrendIcon"
                :show-rank="true"
              />
              <SectorListCard
                :items="topLosers"
                type="losers"
                :title="isZh ? '跌幅榜' : 'Top Losers'"
                :icon="downTrendIcon"
                :show-rank="true"
              />
              <SectorListCard
                :items="mySectors"
                type="my"
                :title="isZh ? '持仓板块' : 'My Sectors'"
                :icon="portfolioIcon"
                :show-rank="false"
                :summary="(isZh ? '持仓集中在 ' : 'Positions concentrated in ') + mySectors.map(s => s.name).join('、')"
              />
            </div>
          </div>

          <!-- 持仓风险指标 -->
          <div class="position-risk-header">
            <div class="section-header">
              <div class="section-title">
                <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
                <span>{{ isZh ? '持仓风险指标' : 'Position Risk Metrics' }}</span>
              </div>
            </div>
          </div>

          <!-- 核心风险指标卡片 -->
          <div class="key-metrics-row">
            <!-- VaR 仪表盘 - 增强版 -->
            <div class="metric-card gauge-card enhanced" :class="getVarSignal(riskAnalysis.var_95)">
              <div class="gauge-header">
                <div class="gauge-icon var-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                    <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
                  </svg>
                </div>
                <div class="gauge-title-row">
                  <span class="gauge-title">VaR(95%)</span>
                  <div class="signal-light" :class="getVarSignal(riskAnalysis.var_95)"></div>
                  <span class="metric-hint">{{ isZh ? '↓ 越低越好' : '↓ Lower' }}</span>
                </div>
              </div>
              <div class="gauge-main">
                <div class="gauge-value-row">
                  <div class="gauge-value" :class="getVarLevel">{{ (riskAnalysis.var_95 * 100).toFixed(2) }}%</div>
                  <div class="gauge-sparkline-mini">
                    <MiniSparkline :data="sparklineData.var" />
                  </div>
                </div>
                <div class="gauge-bar-wrapper">
                  <div class="gauge-bar">
                    <div class="gauge-fill" :style="{ width: Math.min(riskAnalysis.var_95 * 1000, 100) + '%' }" :class="getVarLevel"></div>
                  </div>
                  <div class="gauge-scale">
                    <span>{{ isZh ? '低' : 'Low' }}</span>
                    <span>{{ isZh ? '中' : 'Med' }}</span>
                    <span>{{ isZh ? '高' : 'High' }}</span>
                    <span>{{ isZh ? '危' : 'Crit' }}</span>
                  </div>
                </div>
              </div>
              <div class="gauge-status">
                <div class="metric-baseline">
                  <span class="baseline-dir" :class="getVarBaselineDir(riskAnalysis.var_95)">
                    {{ getVarBaselineDir(riskAnalysis.var_95) === 'up' ? '▲' : getVarBaselineDir(riskAnalysis.var_95) === 'down' ? '▼' : '●' }}
                  </span>
                  <span>{{ getVarBaselineText(riskAnalysis.var_95) }}</span>
                </div>
                <div class="metric-trend" :class="getVarTrend">{{ getVarTrendLabel }}</div>
              </div>
            </div>

            <!-- CVaR 仪表盘 - 增强版 -->
            <div class="metric-card gauge-card enhanced" :class="getCvarSignal(riskAnalysis.cvar_95)">
              <div class="gauge-header">
                <div class="gauge-icon cvar-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                  </svg>
                </div>
                <div class="gauge-title-row">
                  <span class="gauge-title">CVaR(95%)</span>
                  <div class="signal-light" :class="getCvarSignal(riskAnalysis.cvar_95)"></div>
                  <span class="metric-hint">{{ isZh ? '↓ 越低越好' : '↓ Lower' }}</span>
                </div>
              </div>
              <div class="gauge-main">
                <div class="gauge-value-row">
                  <div class="gauge-value" :class="getCvarLevel">{{ (riskAnalysis.cvar_95 * 100).toFixed(2) }}%</div>
                  <div class="gauge-sparkline-mini">
                    <MiniSparkline :data="sparklineData.cvar" />
                  </div>
                </div>
                <div class="gauge-bar-wrapper">
                  <div class="gauge-bar">
                    <div class="gauge-fill" :style="{ width: Math.min(Math.abs(riskAnalysis.cvar_95) * 800, 100) + '%' }" :class="getCvarLevel"></div>
                  </div>
                  <div class="gauge-scale">
                    <span>{{ isZh ? '低' : 'Low' }}</span>
                    <span>{{ isZh ? '中' : 'Med' }}</span>
                    <span>{{ isZh ? '高' : 'High' }}</span>
                    <span>{{ isZh ? '危' : 'Crit' }}</span>
                  </div>
                </div>
              </div>
              <div class="gauge-status">
                <div class="metric-baseline">
                  <span class="baseline-dir" :class="getCvarBaselineDir(riskAnalysis.cvar_95)">
                    {{ getCvarBaselineDir(riskAnalysis.cvar_95) === 'up' ? '▲' : getCvarBaselineDir(riskAnalysis.cvar_95) === 'down' ? '▼' : '●' }}
                  </span>
                  <span>{{ getCvarBaselineText(riskAnalysis.cvar_95) }}</span>
                </div>
                <div class="metric-trend" :class="getCvarTrend">{{ getCvarTrendLabel }}</div>
              </div>
            </div>

            <!-- 回撤仪表盘 - 增强版 -->
            <div class="metric-card gauge-card enhanced" :class="getDrawdownSignal(riskAnalysis.current_drawdown)">
              <div class="gauge-header">
                <div class="gauge-icon drawdown-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
                    <polyline points="17 18 23 18 23 12"></polyline>
                  </svg>
                </div>
                <div class="gauge-title-row">
                  <span class="gauge-title">{{ isZh ? '当前回撤' : 'Drawdown' }}</span>
                  <span class="metric-hint">{{ isZh ? '↓ 越低越好' : '↓ Lower' }}</span>
                </div>
              </div>
              <div class="gauge-main">
                <div class="gauge-value-row">
                  <div class="gauge-value" :class="getDrawdownLevel">{{ (Math.abs(riskAnalysis.current_drawdown) * 100).toFixed(2) }}%</div>
                  <div class="gauge-sparkline-mini">
                    <MiniSparkline :data="sparklineData.drawdown" />
                  </div>
                </div>
                <div class="gauge-bar-wrapper">
                  <div class="gauge-bar">
                    <div class="gauge-fill" :style="{ width: Math.min(Math.abs(riskAnalysis.current_drawdown) * 500, 100) + '%' }" :class="getDrawdownLevel"></div>
                  </div>
                  <div class="gauge-scale">
                    <span>{{ isZh ? '低' : 'Low' }}</span>
                    <span>{{ isZh ? '中' : 'Med' }}</span>
                    <span>{{ isZh ? '高' : 'High' }}</span>
                    <span>{{ isZh ? '危' : 'Crit' }}</span>
                  </div>
                </div>
              </div>
              <div class="gauge-status">
                <div class="metric-baseline">
                  <span class="baseline-dir" :class="getDrawdownBaselineDir(riskAnalysis.current_drawdown)">
                    {{ getDrawdownBaselineDir(riskAnalysis.current_drawdown) === 'up' ? '▲' : getDrawdownBaselineDir(riskAnalysis.current_drawdown) === 'down' ? '▼' : '●' }}
                  </span>
                  <span>{{ getDrawdownBaselineText(riskAnalysis.current_drawdown) }}</span>
                </div>
                <div class="metric-trend" :class="getDrawdownTrend">{{ getDrawdownTrendLabel }}</div>
              </div>
            </div>

            <!-- Beta 仪表盘 - 增强版 -->
            <div class="metric-card gauge-card enhanced" :class="getBetaSignal(riskAnalysis.beta)">
              <div class="gauge-header">
                <div class="gauge-icon beta-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="20" x2="18" y2="10"></line>
                    <line x1="12" y1="20" x2="12" y2="4"></line>
                    <line x1="6" y1="20" x2="6" y2="14"></line>
                  </svg>
                </div>
                <div class="gauge-title-row">
                  <span class="gauge-title">Beta</span>
                  <span class="metric-hint">{{ isZh ? '≈ 1 为宜' : '≈ 1 ideal' }}</span>
                </div>
              </div>
              <div class="gauge-main">
                <div class="gauge-value-row">
                  <div class="gauge-value" :class="getBetaLevel">{{ riskAnalysis.beta.toFixed(2) }}</div>
                  <div class="gauge-sparkline-mini">
                    <MiniSparkline :data="sparklineData.beta" />
                  </div>
                </div>
                <div class="gauge-bar-wrapper">
                  <div class="gauge-bar">
                    <div class="gauge-fill" :style="{ width: Math.min(Math.abs(riskAnalysis.beta - 1) * 100, 100) + '%' }" :class="getBetaLevel"></div>
                  </div>
                  <div class="gauge-scale">
                    <span>{{ isZh ? '低' : 'Low' }}</span>
                    <span>{{ isZh ? '中' : 'Med' }}</span>
                    <span>{{ isZh ? '高' : 'High' }}</span>
                    <span>{{ isZh ? '危' : 'Crit' }}</span>
                  </div>
                </div>
              </div>
              <div class="gauge-status">
                <div class="metric-baseline">
                  <span class="baseline-dir" :class="getBetaBaselineDir(riskAnalysis.beta)">
                    {{ getBetaBaselineDir(riskAnalysis.beta) === 'up' ? '▲' : getBetaBaselineDir(riskAnalysis.beta) === 'down' ? '▼' : '●' }}
                  </span>
                  <span>{{ getBetaBaselineText(riskAnalysis.beta) }}</span>
                </div>
                <div class="metric-trend" :class="getBetaTrend">{{ getBetaTrendLabel }}</div>
              </div>
            </div>

            <!-- 波动率仪表盘 - 增强版 -->
            <div class="metric-card gauge-card enhanced" :class="getVolatilitySignal(riskAnalysis.daily_volatility)">
              <div class="gauge-header">
                <div class="gauge-icon volatility-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                  </svg>
                </div>
                <div class="gauge-title-row">
                  <span class="gauge-title">{{ isZh ? '日波动率' : 'Volatility' }}</span>
                  <span class="metric-hint">{{ isZh ? '↓ 越低越好' : '↓ Lower' }}</span>
                </div>
              </div>
              <div class="gauge-main">
                <div class="gauge-value-row">
                  <div class="gauge-value" :class="getVolatilityLevel">{{ (riskAnalysis.daily_volatility * 100).toFixed(2) }}%</div>
                  <div class="gauge-sparkline-mini">
                    <MiniSparkline :data="sparklineData.volatility" />
                  </div>
                </div>
                <div class="gauge-bar-wrapper">
                  <div class="gauge-bar">
                    <div class="gauge-fill" :style="{ width: Math.min(riskAnalysis.daily_volatility * 2000, 100) + '%' }" :class="getVolatilityLevel"></div>
                  </div>
                  <div class="gauge-scale">
                    <span>{{ isZh ? '低' : 'Low' }}</span>
                    <span>{{ isZh ? '中' : 'Med' }}</span>
                    <span>{{ isZh ? '高' : 'High' }}</span>
                    <span>{{ isZh ? '危' : 'Crit' }}</span>
                  </div>
                </div>
              </div>
              <div class="gauge-status">
                <div class="metric-baseline">
                  <span class="baseline-dir" :class="getVolatilityBaselineDir(riskAnalysis.daily_volatility)">
                    {{ getVolatilityBaselineDir(riskAnalysis.daily_volatility) === 'up' ? '▲' : getVolatilityBaselineDir(riskAnalysis.daily_volatility) === 'down' ? '▼' : '●' }}
                  </span>
                  <span>{{ getVolatilityBaselineText(riskAnalysis.daily_volatility) }}</span>
                </div>
                <div class="metric-trend" :class="getVolatilityTrend">{{ getVolatilityTrendLabel }}</div>
              </div>
            </div>
          </div>

          <!-- 三栏布局：评分 | 趋势图 | 预警 -->
          <div class="three-column-grid">
            <!-- 左侧：综合风险评分 -->
            <div class="score-panel">
              <div class="panel-header">
                <div class="panel-title">
                  <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                  </svg>
                  {{ isZh ? '综合风险评分' : 'Risk Score' }}
                </div>
                <RefreshButton
                  :loading="scoreLoading"
                  size="small"
                  @click="refreshRiskScore"
                />
              </div>

              <div class="score-body">
                <RiskScoreGauge
                  :score="comprehensiveRiskScore.score"
                  :level="comprehensiveRiskScore.level"
                  :dimensions="riskScoreDimensions"
                />
              </div>
            </div>

            <!-- 中间：风险趋势图 -->
            <div class="trend-panel">
              <div class="panel-header">
                <div class="panel-title">
                  <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                  </svg>
                  {{ isZh ? '风险趋势 (30天)' : 'Risk Trend (30D)' }}
                </div>
                <div class="trend-summary">
                  <span class="trend-badge" :class="riskTrendStats.trend">
                    <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline v-if="riskTrendStats.trend === 'up'" points="18 15 12 9 6 15"></polyline>
                      <polyline v-else-if="riskTrendStats.trend === 'down'" points="6 9 12 15 18 9"></polyline>
                      <line v-else x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    {{ riskTrendStats.trend === 'up' ? (isZh ? '上升' : 'Up') : riskTrendStats.trend === 'down' ? (isZh ? '下降' : 'Down') : (isZh ? '稳定' : 'Stable') }}
                  </span>
                </div>
              </div>
              <div class="trend-body">
                <div class="trend-chart" ref="riskTrendChartRef"></div>
                <div class="trend-stats-row">
                  <div class="trend-stat">
                    <span class="label">{{ isZh ? '7日均值' : '7D Avg' }}</span>
                    <span class="value" :style="{ color: getRiskLevelColor(riskTrendStats.avg7d) }">{{ riskTrendStats.avg7d.toFixed(0) }}</span>
                  </div>
                  <div class="trend-stat">
                    <span class="label">{{ isZh ? '最高' : 'Max' }}</span>
                    <span class="value">{{ riskTrendStats.max.toFixed(0) }}</span>
                  </div>
                  <div class="trend-stat">
                    <span class="label">{{ isZh ? '最低' : 'Min' }}</span>
                    <span class="value">{{ riskTrendStats.min.toFixed(0) }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右侧：风险预警 -->
            <div class="alerts-panel">
              <div class="panel-header">
                <div class="panel-title">
                  <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                  </svg>
                  {{ isZh ? '风险预警' : 'Alerts' }}
                  <span class="alert-count" v-if="riskAlerts.length > 0">{{ riskAlerts.length }}</span>
                </div>
                <button class="btn-dismiss-all" @click="dismissAllAlerts" v-if="riskAlerts.length > 1">
                  {{ isZh ? '清除' : 'Clear' }}
                </button>
              </div>

              <div class="alerts-body">
                <div v-if="riskAlerts.length === 0" class="no-alerts">
                  <svg class="icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                  </svg>
                  <span>{{ isZh ? '暂无风险预警' : 'No active alerts' }}</span>
                </div>
                <div v-else class="alerts-list">
                  <div
                    v-for="(alert, index) in riskAlerts.slice(0, 5)"
                    :key="index"
                    :class="['alert-item', alert.level]"
                  >
                    <div class="alert-icon">
                      <svg v-if="alert.level === 'critical'" class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                      </svg>
                      <svg v-else-if="alert.level === 'warning'" class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                      </svg>
                      <svg v-else class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                      </svg>
                    </div>
                    <div class="alert-content">
                      <div class="alert-title">{{ alert.title }}</div>
                      <div class="alert-description">{{ alert.description }}</div>
                    </div>
                    <button class="btn-alert-dismiss" @click="dismissAlert(index)">
                      <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- VaR/CVaR 分析 -->
          <div class="analysis-cards-row">
            <div class="analysis-card var-card">
              <VaRCVaRCard
                :var95="riskAnalysis.var_95"
                :cvar95="riskAnalysis.cvar_95"
              />
            </div>

            <!-- 因子暴露分析 -->
            <div class="analysis-card factor-card">
              <FactorExposureCard :factors="factorExposureList" />
            </div>
          </div>

          <!-- 压力测试结果（单独一行） -->
          <div class="stress-test-row" v-if="stressTestResult">
            <div class="analysis-card stress-card">
              <div class="panel-header">
                <div class="panel-title">
                  <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #ff9800;">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                  </svg>
                  {{ isZh ? '压力测试结果' : 'Stress Test' }}
                </div>
                <span class="test-time" v-if="stressTestResult.test_time">
                  {{ formatDateTime(stressTestResult.test_time) }}
                </span>
              </div>
              <div class="stress-scenarios-grid">
                <div v-for="scenario in stressTestResult.scenarios" :key="scenario.name"
                     class="scenario-mini-card"
                     :class="[scenario.impact_level, { current: isCurrentScenario(scenario) }, isCurrentScenario(scenario) ? 'risk-' + riskGaugeLevel : '']">
                  <!-- 当前状态指示器 -->
                  <div class="current-indicator" v-if="isCurrentScenario(scenario)">
                    <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"></circle>
                      <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    {{ isZh ? '当前' : 'Now' }}
                  </div>
                  <div class="scenario-name">{{ scenario.name }}</div>
                  <div class="scenario-loss" :class="scenario.estimated_loss < 0 ? 'loss' : 'profit'">
                    {{ formatCurrency(scenario.estimated_loss) }}
                  </div>
                  <div class="scenario-pct">{{ (scenario.estimated_loss_pct * 100).toFixed(1) }}%</div>
                </div>
              </div>
              <div class="stress-summary-row" v-if="stressTestResult.risk_summary">
                <div class="summary-badge worst">
                  {{ isZh ? '最差' : 'Worst' }}: {{ stressTestResult.risk_summary.worst_scenario }}
                </div>
                <div class="summary-badge max-loss">
                  {{ isZh ? '最大损失' : 'Max' }}: {{ formatCurrency(stressTestResult.risk_summary.max_potential_loss) }}
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ===== 仓位管理模块 ===== -->
        <template v-else-if="activeModule === 'position'">
          <div class="module-header">
            <div class="header-left">
              <div class="title-row">
                <div class="title-icon position" :class="{ simulated: isSimulatedMode }">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M12 2a10 10 0 0 1 10 10"></path>
                    <path d="M12 12L12 2"></path>
                    <path d="M12 12L22 12"></path>
                  </svg>
                </div>
                <div class="title-text">
                  <h1 class="page-title">{{ isZh ? '仓位管理' : 'Position Management' }}</h1>
                  <span class="page-subtitle">{{ isSimulatedMode ? (isZh ? '模拟交易账户' : 'Simulated Trading') : (isZh ? '实盘持仓查询与分析' : 'Real-time position tracking') }}</span>
                </div>
              </div>
              <!-- 账户模式切换 -->
              <ModeSwitch
                v-model="isSimulatedMode"
                :options="accountModeOptions"
                @change="handleModeChange"
              />
            </div>
            <div class="header-right">
              <RefreshButton
                :loading="loading"
                :label="isZh ? '刷新' : 'Refresh'"
                @click="refreshPositions"
              />
            </div>
          </div>

          <!-- 模拟账户提示条 -->
          <div v-if="isSimulatedMode" class="sim-banner">
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <span>{{ isZh ? '当前为模拟交易模式，持仓由策略自动管理。初始资金: ¥1,000,000' : 'Simulated trading mode. Positions are managed by strategy. Initial capital: ¥1,000,000' }}</span>
            <button class="btn-reset" @click="resetSimulatedAccount">{{ isZh ? '重置账户' : 'Reset' }}</button>
          </div>

          <!-- 组合汇总 -->
          <div class="summary-cards">
            <SummaryCard
              :icon="walletIcon"
              iconColor="blue"
              :value="currentPositionSummary.total_assets"
              :label="isZh ? '总资产' : 'Total Assets'"
              :subtitle="`${isZh ? '现金' : 'Cash'}: ¥${((currentPositionSummary.available_cash || currentPositionSummary.total_cash) / 10000).toFixed(2)}万`"
              currency
              currencyUnit="wan"
            />
            <SummaryCard
              :icon="rmbIcon"
              iconColor="blue"
              :value="currentPositionSummary.market_value || currentPositionSummary.total_market_value"
              :label="isZh ? '总市值' : 'Market Value'"
              :subtitle="`${isZh ? '仓位' : 'Position'}: ${(currentPositionSummary.position_ratio * 100).toFixed(1)}%`"
              currency
              currencyUnit="wan"
            />
            <SummaryCard
              :icon="currentPositionSummary.total_profit_loss >= 0 ? upIcon : downIcon"
              :iconColor="currentPositionSummary.total_profit_loss >= 0 ? 'red' : 'green'"
              :valueColor="currentPositionSummary.total_profit_loss >= 0 ? 'profit' : 'loss'"
              :value="currentPositionSummary.total_profit_loss"
              :label="isZh ? '总盈亏' : 'Total P&L'"
              :subtitle="`${(currentPositionSummary.total_profit_loss_pct * 100).toFixed(2)}%`"
              currency
              currencyUnit="wan"
            />
            <SummaryCard
              :icon="clockIcon"
              iconColor="orange"
              :value="currentPositionSummary.today_profit_loss"
              :valueColor="currentPositionSummary.today_profit_loss >= 0 ? 'profit' : 'loss'"
              :label="isZh ? '当日盈亏' : 'Today P&L'"
              :subtitle="`${isZh ? '持仓数' : 'Positions'}: ${currentPositionSummary.position_count}`"
              currency
              currencyUnit="wan"
            />
          </div>

          <!-- 高级分析指标 - 信号灯+风险区间+趋势 -->
          <PortfolioAnalysisCard :metrics="analysisMetrics" />

          <!-- 收益走势图 -->
          <div class="chart-section">
            <div class="chart-header">
              <div class="chart-title">
                <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
                {{ isZh ? '收益走势' : 'Return Trend' }}
              </div>
            </div>
            <div ref="trendChartRef" class="echarts-chart" :style="{ height: trendChartHeight + 'px' }"></div>
            <!-- 调整高度把手 -->
            <div class="resize-handle" @mousedown="startResizeTrend" :title="isZh ? '拖拽调整高度' : 'Drag to resize'">
              <div class="resize-line"></div>
            </div>
          </div>

          <!-- 持仓分布图 & 盈亏贡献图 -->
          <!-- TODO: [生产环境] 数据需对接API:
               - 饼图: POST /api/v1/production/position/distribution
               - 条形图: POST /api/v1/production/position/contribution
               当前为静态演示数据 -->
          <div class="charts-row">
            <div class="chart-section half">
              <div class="chart-header">
                <div class="chart-title">
                  <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                    <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
                  </svg>
                  {{ isZh ? '持仓分布' : 'Position Distribution' }}
                </div>
              </div>
              <div class="chart-body pie-chart-body">
                <div class="pie-chart">
                  <svg viewBox="0 0 100 100">
                    <!-- 白酒 30% -->
                    <circle cx="50" cy="50" r="40" fill="transparent" stroke="#2962ff" stroke-width="20" stroke-dasharray="75.4 251.3" transform="rotate(-90 50 50)"/>
                    <!-- 金融 25% -->
                    <circle cx="50" cy="50" r="40" fill="transparent" stroke="#26a69a" stroke-width="20" stroke-dasharray="62.8 251.3" stroke-dashoffset="-75.4" transform="rotate(-90 50 50)"/>
                    <!-- 家电 20% -->
                    <circle cx="50" cy="50" r="40" fill="transparent" stroke="#f7931a" stroke-width="20" stroke-dasharray="50.3 251.3" stroke-dashoffset="-138.2" transform="rotate(-90 50 50)"/>
                    <!-- 科技 15% -->
                    <circle cx="50" cy="50" r="40" fill="transparent" stroke="#9c27b0" stroke-width="20" stroke-dasharray="37.7 251.3" stroke-dashoffset="-188.5" transform="rotate(-90 50 50)"/>
                    <!-- 其他 10% -->
                    <circle cx="50" cy="50" r="40" fill="transparent" stroke="#787b86" stroke-width="20" stroke-dasharray="25.1 251.3" stroke-dashoffset="-226.2" transform="rotate(-90 50 50)"/>
                    <text x="50" y="50" text-anchor="middle" dominant-baseline="middle" fill="#d1d4dc" font-size="10" font-weight="600">5{{ isZh ? '板块' : 'Sectors' }}</text>
                  </svg>
                </div>
                <div class="pie-legend">
                  <div class="legend-row"><span class="color-box blue"></span>{{ isZh ? '白酒' : 'Baijiu' }} <span class="pct">30%</span></div>
                  <div class="legend-row"><span class="color-box green"></span>{{ isZh ? '金融' : 'Finance' }} <span class="pct">25%</span></div>
                  <div class="legend-row"><span class="color-box orange"></span>{{ isZh ? '家电' : 'Appliance' }} <span class="pct">20%</span></div>
                  <div class="legend-row"><span class="color-box purple"></span>{{ isZh ? '科技' : 'Tech' }} <span class="pct">15%</span></div>
                  <div class="legend-row"><span class="color-box gray"></span>{{ isZh ? '其他' : 'Other' }} <span class="pct">10%</span></div>
                </div>
              </div>
            </div>

            <div class="chart-section half">
              <div class="chart-header">
                <div class="chart-title">
                  <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="20" x2="18" y2="10"></line>
                    <line x1="12" y1="20" x2="12" y2="4"></line>
                    <line x1="6" y1="20" x2="6" y2="14"></line>
                  </svg>
                  {{ isZh ? '盈亏贡献' : 'P&L Contribution' }}
                </div>
              </div>
              <div class="chart-body bar-chart-body">
                <div class="bar-item">
                  <div class="bar-label">600519</div>
                  <div class="bar-track">
                    <div class="bar-fill excellent" style="width: 65%"></div>
                  </div>
                  <div class="bar-value excellent">+7,050</div>
                </div>
                <div class="bar-item">
                  <div class="bar-label">000858</div>
                  <div class="bar-track">
                    <div class="bar-fill good" style="width: 24%"></div>
                  </div>
                  <div class="bar-value good">+2,640</div>
                </div>
                <div class="bar-item">
                  <div class="bar-label">000333</div>
                  <div class="bar-track">
                    <div class="bar-fill good" style="width: 15%"></div>
                  </div>
                  <div class="bar-value good">+1,580</div>
                </div>
                <div class="bar-item">
                  <div class="bar-label">600036</div>
                  <div class="bar-track">
                    <div class="bar-fill average" style="width: 10%"></div>
                  </div>
                  <div class="bar-value average">+1,020</div>
                </div>
                <div class="bar-item">
                  <div class="bar-label">601318</div>
                  <div class="bar-track">
                    <div class="bar-fill poor" style="width: 12%"></div>
                  </div>
                  <div class="bar-value poor">-1,275</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 持仓列表 -->
          <div class="chart-section">
            <div class="chart-header">
              <div class="chart-title">
                <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="8" y1="6" x2="21" y2="6"></line>
                  <line x1="8" y1="12" x2="21" y2="12"></line>
                  <line x1="8" y1="18" x2="21" y2="18"></line>
                  <circle cx="4" cy="6" r="1.5" fill="currentColor"></circle>
                  <circle cx="4" cy="12" r="1.5" fill="currentColor"></circle>
                  <circle cx="4" cy="18" r="1.5" fill="currentColor"></circle>
                </svg>
                <span>{{ isZh ? '持仓列表' : 'Position List' }}</span>
              </div>
            </div>
            <div class="positions-table-wrapper">
              <table class="positions-table">
                <thead>
                  <tr>
                    <th>{{ isZh ? '代码' : 'Code' }}</th>
                    <th>{{ isZh ? '名称' : 'Name' }}</th>
                    <th class="right">{{ isZh ? '数量' : 'Qty' }}</th>
                    <th class="right">{{ isZh ? '成本价' : 'Cost' }}</th>
                    <th class="right">{{ isZh ? '现价' : 'Price' }}</th>
                    <th class="right">{{ isZh ? '市值' : 'Value' }}</th>
                    <th class="right">{{ isZh ? '盈亏' : 'P&L' }}</th>
                    <th class="right">{{ isZh ? '盈亏%' : 'P&L%' }}</th>
                    <th class="right">{{ isZh ? '今日%' : 'Today%' }}</th>
                    <th>{{ isZh ? '状态' : 'Status' }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="pos in currentPositions" :key="pos.symbol">
                    <td class="code">{{ pos.symbol }}</td>
                    <td>{{ pos.symbol_name }}</td>
                    <td class="right">{{ formatNumber(pos.quantity) }}</td>
                    <td class="right">{{ pos.avg_price.toFixed(2) }}</td>
                    <td class="right">{{ pos.current_price.toFixed(2) }}</td>
                    <td class="right">{{ formatCurrency(pos.market_value) }}</td>
                    <td class="right" :class="pos.profit_loss >= 0 ? 'profit' : 'loss'">
                      {{ formatCurrency(pos.profit_loss) }}
                    </td>
                    <td class="right" :class="pos.profit_loss_pct >= 0 ? 'profit' : 'loss'">
                      {{ pos.profit_loss_pct >= 0 ? '+' : '' }}{{ (pos.profit_loss_pct * 100).toFixed(2) }}%
                    </td>
                    <td class="right" :class="pos.change_pct >= 0 ? 'profit' : 'loss'">
                      {{ pos.change_pct >= 0 ? '+' : '' }}{{ (pos.change_pct * 100).toFixed(2) }}%
                    </td>
                    <td>
                      <span :class="['status-badge', pos.status]">{{ getPositionStatusText(pos.status) }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="currentPositions.length === 0" class="empty-state">
                {{ isZh ? '暂无持仓数据' : 'No positions' }}
              </div>
            </div>
          </div>
        </template>

        <!-- ===== 风控规则模块 ===== -->
        <template v-else-if="activeModule === 'rules'">
          <div class="module-header">
            <div class="header-left">
              <div class="title-row">
                <div class="title-icon rules">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="8" y1="6" x2="21" y2="6"></line>
                    <line x1="8" y1="12" x2="21" y2="12"></line>
                    <line x1="8" y1="18" x2="21" y2="18"></line>
                    <line x1="3" y1="6" x2="3.01" y2="6"></line>
                    <line x1="3" y1="12" x2="3.01" y2="12"></line>
                    <line x1="3" y1="18" x2="3.01" y2="18"></line>
                  </svg>
                </div>
                <div class="title-text">
                  <h1 class="page-title">{{ isZh ? '风控规则' : 'Risk Rules' }}</h1>
                  <span class="page-subtitle">{{ isZh ? '配置和管理风险控制规则' : 'Configure risk control rules' }}</span>
                </div>
              </div>
            </div>
            <div class="header-right">
              <button class="btn-ai" @click="showAIDialog = true">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2M7.5 13A1.5 1.5 0 0 0 6 14.5 1.5 1.5 0 0 0 7.5 16 1.5 1.5 0 0 0 9 14.5 1.5 1.5 0 0 0 7.5 13m9 0a1.5 1.5 0 0 0-1.5 1.5 1.5 1.5 0 0 0 1.5 1.5 1.5 1.5 0 0 0 1.5-1.5 1.5 1.5 0 0 0-1.5-1.5M12 17a1 1 0 0 0-1 1 1 1 0 0 0 1 1 1 1 0 0 0 1-1 1 1 0 0 0-1-1Z"></path>
                </svg>
                {{ isZh ? 'AI调参' : 'AI Tune' }}
              </button>
              <button class="btn-primary" @click="showAddRuleDialog = true">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                {{ isZh ? '添加规则' : 'Add Rule' }}
              </button>
            </div>
          </div>

          <!-- 规则统计 -->
          <div class="rules-stats">
            <div class="stat-item">
              <span class="stat-label">{{ isZh ? '总规则' : 'Total' }}</span>
              <span class="stat-value">{{ rules.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">{{ isZh ? '已启用' : 'Enabled' }}</span>
              <span class="stat-value enabled">{{ rules.filter(r => r.enabled).length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">{{ isZh ? '今日触发' : 'Triggered Today' }}</span>
              <span class="stat-value warning">{{ rules.reduce((sum, r) => sum + (r.triggerCount || 0), 0) }}</span>
            </div>
            <div class="stat-item ai-badge" @click="showAIDialog = true">
              <svg class="icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path>
              </svg>
              <span>{{ isZh ? '智能优化可用' : 'AI Optimize' }}</span>
            </div>
          </div>

          <div class="rules-grid">
            <RiskRuleCard
              v-for="rule in rules"
              :key="rule.rule_id"
              :rule="rule"
              :isZh="isZh"
              @toggle="toggleRule"
              @edit="editRule"
              @backtest="showBacktest"
              @delete="removeRule"
            />
          </div>
        </template>

        <!-- ===== 风险事件模块 ===== -->
        <template v-else-if="activeModule === 'events'">
          <div class="module-header">
            <div class="header-left">
              <div class="title-row">
                <div class="title-icon events">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                  </svg>
                </div>
                <div class="title-text">
                  <h1 class="page-title">{{ isZh ? '风险事件' : 'Risk Events' }}</h1>
                  <span class="page-subtitle">{{ isZh ? '风险事件时间线与历史记录' : 'Risk event timeline' }}</span>
                </div>
              </div>
            </div>
            <div class="header-right">
              <button class="btn-secondary" @click="loadEvents">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="23 4 23 10 17 10"></polyline>
                  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                </svg>
                {{ isZh ? '刷新' : 'Refresh' }}
              </button>
            </div>
          </div>

          <div class="events-timeline">
            <RiskEventCard
              v-for="event in events"
              :key="event.event_id"
              :event="event"
            />
            <div v-if="events.length === 0" class="empty-state">
              {{ isZh ? '暂无风险事件' : 'No risk events' }}
            </div>
          </div>
        </template>
      </main>
    </div>

    <!-- 添加规则对话框 -->
    <div v-if="showAddRuleDialog" class="dialog-overlay" @click.self="showAddRuleDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ isZh ? '添加风险规则' : 'Add Risk Rule' }}</h3>
          <button class="btn-close" @click="showAddRuleDialog = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>{{ isZh ? '规则ID' : 'Rule ID' }}</label>
            <input type="text" v-model="ruleForm.rule_id" :placeholder="isZh ? '例如: position_limit_001' : 'e.g.: position_limit_001'" />
          </div>
          <div class="form-group">
            <label>{{ isZh ? '规则名称' : 'Rule Name' }}</label>
            <input type="text" v-model="ruleForm.rule_name" :placeholder="isZh ? '例如: 仓位上限控制' : 'e.g.: Position Limit Control'" />
          </div>
          <div class="form-group">
            <label>{{ isZh ? '规则类型' : 'Rule Type' }}</label>
            <select v-model="ruleForm.rule_type">
              <option value="">{{ isZh ? '选择规则类型' : 'Select rule type' }}</option>
              <option value="position_limit">{{ isZh ? '仓位限制' : 'Position Limit' }}</option>
              <option value="loss_limit">{{ isZh ? '亏损限制' : 'Loss Limit' }}</option>
              <option value="drawdown_limit">{{ isZh ? '回撤限制' : 'Drawdown Limit' }}</option>
              <option value="single_position_limit">{{ isZh ? '单票限制' : 'Single Position Limit' }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>{{ isZh ? '规则参数 (JSON)' : 'Rule Params (JSON)' }}</label>
            <textarea v-model="ruleFormParams" rows="4" placeholder='{"max_ratio": 0.8}'></textarea>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="ruleForm.enabled" />
              <span>{{ isZh ? '启用规则' : 'Enable Rule' }}</span>
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showAddRuleDialog = false">{{ isZh ? '取消' : 'Cancel' }}</button>
          <button class="btn-primary" @click="addRule" :disabled="addingRule">
            {{ addingRule ? (isZh ? '添加中...' : 'Adding...') : (isZh ? '添加' : 'Add') }}
          </button>
        </div>
      </div>
    </div>

    <!-- AI智能调参对话框 -->
    <div v-if="showAIDialog" class="dialog-overlay" @click.self="showAIDialog = false">
      <div class="dialog-content ai-dialog">
        <div class="dialog-header">
          <h2>
            <svg class="icon-ai-header" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2"></path>
            </svg>
            {{ isZh ? 'AI智能调参' : 'AI Smart Tuning' }}
          </h2>
          <button class="dialog-close" @click="showAIDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div v-if="aiAnalyzing" class="ai-analyzing">
            <div class="ai-spinner"></div>
            <p>{{ isZh ? 'AI正在分析历史数据和市场波动...' : 'AI is analyzing historical data...' }}</p>
          </div>
          <div v-else-if="aiSuggestions.length === 0" class="ai-ready">
            <div class="ai-icon-large">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path>
              </svg>
            </div>
            <p>{{ isZh ? '基于历史波动率、回撤数据和市场环境，AI将为您推荐最优风控参数' : 'AI will recommend optimal risk parameters based on volatility, drawdown and market conditions' }}</p>
            <button class="btn-ai-analyze" @click="analyzeWithAI">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              {{ isZh ? '开始AI分析' : 'Start Analysis' }}
            </button>
          </div>
          <div v-else class="ai-suggestions">
            <div v-for="s in aiSuggestions" :key="s.rule_id" class="suggestion-card">
              <div class="suggestion-header">
                <span class="suggestion-name">{{ s.rule_name }}</span>
                <button class="btn-apply" @click="applyAISuggestion(s)">
                  {{ isZh ? '应用' : 'Apply' }}
                </button>
              </div>
              <div class="suggestion-change">
                <span class="current">{{ isZh ? '当前' : 'Current' }}: {{ (s.current * 100).toFixed(0) }}%</span>
                <svg class="arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
                <span class="suggested">{{ (s.suggested * 100).toFixed(0) }}%</span>
              </div>
              <div class="suggestion-reason">{{ s.reason }}</div>
              <div class="suggestion-impact">{{ s.impact }}</div>
            </div>
            <div class="suggestion-actions">
              <button class="btn-secondary" @click="aiSuggestions = []">{{ isZh ? '重新分析' : 'Re-analyze' }}</button>
              <button class="btn-ai-apply-all" @click="applyAllSuggestions">{{ isZh ? '应用全部' : 'Apply All' }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 规则回测对话框 -->
    <div v-if="showBacktestDialog" class="dialog-overlay" @click.self="showBacktestDialog = false">
      <div class="dialog-content backtest-dialog">
        <div class="dialog-header">
          <h2>
            <svg class="icon-backtest-header" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
            {{ isZh ? '规则回测' : 'Rule Backtest' }}
          </h2>
          <button class="dialog-close" @click="showBacktestDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div v-if="backtestingRule" class="backtest-rule-info">
            <span class="rule-name">{{ backtestingRule.rule_name }}</span>
            <span class="rule-type">{{ getRuleTypeText(backtestingRule.rule_type) }}</span>
          </div>

          <div v-if="!backtestResult && !backtestLoading" class="backtest-ready">
            <p>{{ isZh ? '回测将使用历史数据模拟规则触发情况，评估规则效果' : 'Backtest uses historical data to simulate rule triggers and evaluate effectiveness' }}</p>
            <button class="btn-backtest-run" @click="runBacktest">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              {{ isZh ? '开始回测' : 'Start Backtest' }}
            </button>
          </div>

          <div v-if="backtestLoading" class="backtest-loading">
            <div class="ai-spinner"></div>
            <p>{{ isZh ? '正在回测历史数据...' : 'Backtesting historical data...' }}</p>
          </div>

          <div v-if="backtestResult" class="backtest-result">
            <div class="result-stats">
              <div class="result-item">
                <span class="label">{{ isZh ? '回测周期' : 'Period' }}</span>
                <span class="value">{{ backtestResult.period }}</span>
              </div>
              <div class="result-item">
                <span class="label">{{ isZh ? '触发次数' : 'Triggers' }}</span>
                <span class="value warning">{{ backtestResult.trigger_count }}</span>
              </div>
              <div class="result-item">
                <span class="label">{{ isZh ? '避免损失' : 'Prevented Loss' }}</span>
                <span class="value success">¥{{ Number(backtestResult.prevented_loss).toLocaleString() }}</span>
              </div>
              <div class="result-item">
                <span class="label">{{ isZh ? '回撤降低' : 'Drawdown Reduced' }}</span>
                <span class="value success">{{ backtestResult.max_drawdown_reduced }}%</span>
              </div>
              <div class="result-item">
                <span class="label">{{ isZh ? '夏普提升' : 'Sharpe Improved' }}</span>
                <span class="value success">+{{ backtestResult.sharpe_improved }}</span>
              </div>
            </div>
            <div class="result-recommendations">
              <div class="rec-title">{{ isZh ? '分析建议' : 'Analysis' }}</div>
              <ul>
                <li v-for="(rec, i) in backtestResult.recommendations" :key="i">{{ rec }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import RiskMonitorChart from './RiskMonitorChart.vue'
import { riskAnalysisApi } from '@/api/modules/production'
import * as echarts from 'echarts'
import { useAppStore } from '@/stores/core/AppStore'
import GlobalNavBar from '@/components/GlobalNavBar.vue'
import { MiniSparkline } from '@/components/ui/charts'
import RiskScoreGauge from '@/components/ui/RiskScoreGauge.vue'
import VaRCVaRCard from '@/components/ui/VaRCVaRCard.vue'
import FactorExposureCard from '@/components/ui/FactorExposureCard.vue'
import PortfolioAnalysisCard from '@/components/ui/PortfolioAnalysisCard.vue'
import RiskRuleCard from '@/components/ui/RiskRuleCard.vue'
import RiskEventCard from '@/components/ui/RiskEventCard.vue'
import SummaryCard from '@/components/ui/SummaryCard.vue'
import SectorListCard from '@/components/ui/SectorListCard.vue'
import ModeSwitch from '@/components/ui/ModeSwitch.vue'
import RefreshButton from '@/components/ui/RefreshButton.vue'

const router = useRouter()
const appStore = useAppStore()

// SummaryCard 图标
const walletIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>'
const rmbIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><text x="12" y="18" font-size="20" text-anchor="middle" fill="currentColor" stroke="none" font-weight="bold">¥</text></svg>'
const upIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>'
const downIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>'
const clockIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
// 大盘风险图标
const limitIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"></polyline></svg>'
const ratioIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"></line><polyline points="18 14 12 8 6 14"></polyline></svg>'
const volumeIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>'
const northIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>'

// SectorListCard 图标
const upTrendIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"></polyline></svg>'
const downTrendIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>'
const portfolioIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>'

// ModeSwitch 图标
const liveIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
const simIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>'

// 实盘/模拟切换选项
const accountModeOptions = computed(() => [
  { value: false, label: isZh.value ? '实盘' : 'Live', icon: liveIcon },
  { value: true, label: isZh.value ? '模拟' : 'Sim', icon: simIcon }
])

// 基础状态
const isZh = computed(() => appStore.language === 'zh')
const activeModule = ref<'risk' | 'position' | 'rules' | 'events' | 'analysis'>('risk')
const loading = ref(false)
const toggling = ref(false)
const addingRule = ref(false)
const showAddRuleDialog = ref(false)
const showAIDialog = ref(false)
const aiAnalyzing = ref(false)
const monitoringActive = ref(false)

// 组件引用
const trendChartRef = ref<HTMLElement>()
let trendChartInstance: echarts.ECharts | null = null

// 图表高度调整（带localStorage持久化）
const TREND_CHART_HEIGHT_KEY = 'myquant-risk-trend-height'
const trendChartHeight = ref(280)

// 拖拽调整高度相关状态
const isResizingTrend = ref(false)
const resizeStartY = ref(0)
const resizeStartHeight = ref(0)

// 加载保存的高度
const loadSavedTrendHeight = () => {
  const saved = localStorage.getItem(TREND_CHART_HEIGHT_KEY)
  if (saved) {
    const parsed = parseInt(saved, 10)
    if (!isNaN(parsed) && parsed >= 150 && parsed <= 500) {
      trendChartHeight.value = parsed
    }
  }
}

// 保存高度到localStorage
const saveTrendHeight = () => {
  localStorage.setItem(TREND_CHART_HEIGHT_KEY, trendChartHeight.value.toString())
}

// 开始调整高度
const startResizeTrend = (e: MouseEvent) => {
  isResizingTrend.value = true
  resizeStartY.value = e.clientY
  resizeStartHeight.value = trendChartHeight.value
  document.addEventListener('mousemove', onResizeTrend)
  document.addEventListener('mouseup', stopResizeTrend)
  document.body.style.cursor = 'ns-resize'
  document.body.style.userSelect = 'none'
}

// 拖拽中
const onResizeTrend = (e: MouseEvent) => {
  if (!isResizingTrend.value) return
  const delta = e.clientY - resizeStartY.value
  const newHeight = Math.max(150, Math.min(500, resizeStartHeight.value + delta))
  trendChartHeight.value = newHeight
  if (trendChartInstance) {
    trendChartInstance.resize()
  }
}

// 停止调整
const stopResizeTrend = () => {
  if (isResizingTrend.value) {
    isResizingTrend.value = false
    saveTrendHeight()
    document.removeEventListener('mousemove', onResizeTrend)
    document.removeEventListener('mouseup', stopResizeTrend)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }
}

// 收益走势数据
const trendData = ref({
  dates: [] as string[],
  strategy: [] as number[],
  benchmark: [] as number[]
})

// ========== AI智能调参建议 ==========
const aiSuggestions = ref<any[]>([])

// ========== 规则回测 ==========
const showBacktestDialog = ref(false)
const backtestingRule = ref<any>(null)
const backtestLoading = ref(false)
const backtestResult = ref<any>(null)

// ========== 风险规则数据 ==========
const rules = ref<any[]>([
  { rule_id: 'position_limit_001', rule_name: '仓位上限控制', rule_type: 'position_limit', params: { max_ratio: 0.8 }, enabled: true, triggerCount: 3 },
  { rule_id: 'single_position_001', rule_name: '单票持仓限制', rule_type: 'single_position_limit', params: { max_ratio: 0.1 }, enabled: true, triggerCount: 1 },
  { rule_id: 'drawdown_limit_001', rule_name: '最大回撤控制', rule_type: 'drawdown_limit', params: { max_drawdown: 0.15 }, enabled: true, triggerCount: 0 },
  { rule_id: 'loss_limit_001', rule_name: '日亏损限制', rule_type: 'loss_limit', params: { max_daily_loss: 0.05 }, enabled: false, triggerCount: 2 }
])

const ruleForm = ref({ rule_id: '', rule_name: '', rule_type: '', enabled: true })
const ruleFormParams = ref('{}')

// ========== 仓位数据 ==========
const positionSummary = ref({
  total_assets: 1850000,
  total_cash: 462500,
  total_market_value: 1387500,
  total_profit_loss: 125800,
  total_profit_loss_pct: 0.0729,
  today_profit_loss: 18600,
  position_count: 12,
  position_ratio: 0.75
})

// ========== 组合分析指标 ==========
// TODO: [生产环境] 替换为真实API数据 - POST /api/v1/production/position/analysis
// 当前为演示数据，上线前需对接后端接口
const positionAnalysis = ref({
  volatility: 0.185,        // 波动率 (60日年化) - API: position_analysis.volatility
  beta: 1.12,               // Beta系数 - API: position_analysis.beta
  max_drawdown: -0.082,     // 最大回撤 - API: position_analysis.max_drawdown
  turnover_rate: 0.42,      // 换手率 (近30天) - API: position_analysis.turnover_rate
  annual_return: 0.156,     // 年化收益率 - API: position_analysis.annual_return
  tracking_error: 0.035     // 跟踪误差 - API: position_analysis.tracking_error
})

// ========== 模拟交易账户 ==========
// TODO: [生产环境] 模拟账户数据应从后端获取 - GET /api/v1/simulation/account
// 当前为演示数据，用于展示模拟交易功能
const isSimulatedMode = ref(false)

// 模拟账户数据
const simulatedAccount = ref({
  initial_capital: 1000000,      // 初始资金
  available_cash: 658000,        // 可用现金
  total_assets: 1156000,         // 总资产
  market_value: 498000,          // 持仓市值
  total_profit_loss: 156000,     // 总盈亏
  total_profit_loss_pct: 0.156,  // 总收益率
  today_profit_loss: 12300,      // 今日盈亏
  position_count: 6,             // 持仓数量
  position_ratio: 0.43,          // 仓位比例
  created_at: '2026-02-01',      // 创建时间
  strategy_name: '动量策略v2.1'   // 运行策略
})

// 模拟持仓数据
const simulatedPositions = ref<any[]>([
  { symbol: '600519', symbol_name: '贵州茅台', quantity: 50, avg_price: 1820.00, current_price: 1920.50, market_value: 96025, profit_loss: 5025, profit_loss_pct: 0.0553, change_pct: 0.0156, status: 'normal' },
  { symbol: '000858', symbol_name: '五粮液', quantity: 300, avg_price: 160.00, current_price: 178.20, market_value: 53460, profit_loss: 5460, profit_loss_pct: 0.114, change_pct: 0.0215, status: 'normal' },
  { symbol: '600036', symbol_name: '招商银行', quantity: 800, avg_price: 34.00, current_price: 38.90, market_value: 31120, profit_loss: 3920, profit_loss_pct: 0.144, change_pct: 0.0089, status: 'normal' },
  { symbol: '000333', symbol_name: '美的集团', quantity: 600, avg_price: 55.00, current_price: 62.15, market_value: 37290, profit_loss: 4290, profit_loss_pct: 0.13, change_pct: 0.0192, status: 'normal' },
  { symbol: '002415', symbol_name: '海康威视', quantity: 1000, avg_price: 28.50, current_price: 32.10, market_value: 32100, profit_loss: 3600, profit_loss_pct: 0.126, change_pct: 0.0123, status: 'normal' },
  { symbol: '601012', symbol_name: '隆基绿能', quantity: 1500, avg_price: 18.20, current_price: 16.85, market_value: 25275, profit_loss: -2025, profit_loss_pct: -0.074, change_pct: -0.0089, status: 'normal' }
])

// 模拟账户组合分析
const simulatedAnalysis = ref({
  volatility: 0.165,
  beta: 1.05,
  max_drawdown: -0.065,
  turnover_rate: 0.58,
  annual_return: 0.198,
  tracking_error: 0.028
})

// 模式切换方法
const switchToLive = () => {
  isSimulatedMode.value = false
  ElMessage.success(isZh.value ? '已切换到实盘账户' : 'Switched to Live Account')
}

const switchToSimulated = () => {
  isSimulatedMode.value = true
  ElMessage.success(isZh.value ? '已切换到模拟账户' : 'Switched to Simulated Account')
}

const handleModeChange = (value: string | boolean | number) => {
  if (value === true) {
    ElMessage.success(isZh.value ? '已切换到模拟账户' : 'Switched to Simulated Account')
  } else {
    ElMessage.success(isZh.value ? '已切换到实盘账户' : 'Switched to Live Account')
  }
}

// 重置模拟账户
const resetSimulatedAccount = async () => {
  try {
    await ElMessageBox.confirm(
      isZh.value ? '确定要重置模拟账户吗？所有持仓和收益记录将被清空。' : 'Reset simulated account? All positions and records will be cleared.',
      isZh.value ? '确认重置' : 'Confirm Reset',
      { type: 'warning' }
    )
    // TODO: [生产环境] 调用后端API重置账户 - POST /api/v1/simulation/reset
    simulatedAccount.value = {
      initial_capital: 1000000,
      available_cash: 1000000,
      total_assets: 1000000,
      market_value: 0,
      total_profit_loss: 0,
      total_profit_loss_pct: 0,
      today_profit_loss: 0,
      position_count: 0,
      position_ratio: 0,
      created_at: new Date().toISOString().split('T')[0],
      strategy_name: ''
    }
    simulatedPositions.value = []
    ElMessage.success(isZh.value ? '模拟账户已重置' : 'Account reset successfully')
  } catch {
    // 用户取消
  }
}

// 计算属性：根据模式返回对应数据
const currentPositionSummary = computed(() => isSimulatedMode.value ? simulatedAccount.value : positionSummary.value)
const currentPositions = computed(() => isSimulatedMode.value ? simulatedPositions.value : positions.value)
const currentPositionAnalysis = computed(() => isSimulatedMode.value ? simulatedAnalysis.value : positionAnalysis.value)

// 为 PortfolioAnalysisCard 转换数据格式
const analysisMetrics = computed(() => {
  const a = currentPositionAnalysis.value
  return [
    {
      name: isZh.value ? '年化收益' : 'Annual Return',
      value: `${(a.annual_return * 100).toFixed(1)}%`,
      period: isZh.value ? '持仓期' : 'Hold Period',
      hint: a.annual_return >= 0 ? (isZh.value ? '正收益' : 'Positive') : (isZh.value ? '负收益' : 'Negative'),
      iconType: 'return' as const,
      rawValue: a.annual_return * 100,
      direction: 'higher-better' as const,
      markers: ['-25%', '0', '+25%'],
      baselineDir: 'neutral' as const,
      baselineText: isZh.value ? '相对基准' : 'vs benchmark',
      trend: a.annual_return >= 0 ? 'up' as const : 'down' as const,
      trendLabel: a.annual_return >= 0 ? (isZh.value ? '正收益' : 'Positive') : (isZh.value ? '负收益' : 'Negative'),
      sparklinePoints: generateSparklinePoints('return')
    },
    {
      name: isZh.value ? '最大回撤' : 'Max Drawdown',
      value: `${(Math.abs(a.max_drawdown) * 100).toFixed(1)}%`,
      period: isZh.value ? '持仓期' : 'Hold Period',
      hint: isZh.value ? '↓ 越低越好' : '↓ Lower is better',
      iconType: 'drawdown' as const,
      rawValue: a.max_drawdown * 100,
      isDrawdown: true,
      direction: 'lower-better' as const,
      markers: ['0%', '10%', '20%'],
      baselineDir: 'down' as const,
      baselineText: isZh.value ? '低于均值' : 'Below avg',
      trend: 'stable' as const,
      trendLabel: isZh.value ? '稳定' : 'Stable',
      sparklinePoints: generateSparklinePoints('drawdown')
    },
    {
      name: isZh.value ? '波动率' : 'Volatility',
      value: `${(a.volatility * 100).toFixed(1)}%`,
      period: isZh.value ? '60日年化' : '60D',
      hint: isZh.value ? '↓ 越低越好' : '↓ Lower is better',
      iconType: 'volatility' as const,
      rawValue: a.volatility * 100,
      direction: 'lower-better' as const,
      markers: ['0', '15%', '30%'],
      baselineDir: 'down' as const,
      baselineText: isZh.value ? '低于均值' : 'Below avg',
      trend: 'stable' as const,
      trendLabel: isZh.value ? '稳定' : 'Stable',
      sparklinePoints: generateSparklinePoints('volatility')
    },
    {
      name: isZh.value ? 'Beta' : 'Beta',
      value: a.beta.toFixed(2),
      period: '沪深300',
      hint: isZh.value ? '~ 接近1为宜' : '~ Near 1 is ideal',
      iconType: 'beta' as const,
      rawValue: a.beta,
      isBeta: true,
      direction: 'neutral' as const,
      markers: ['0.5', '1.0', '1.5'],
      baselineDir: 'neutral' as const,
      baselineText: isZh.value ? '接近基准' : 'Near benchmark',
      trend: 'stable' as const,
      trendLabel: isZh.value ? '稳定' : 'Stable',
      sparklinePoints: generateSparklinePoints('beta')
    },
    {
      name: isZh.value ? '换手率' : 'Turnover',
      value: `${(a.turnover_rate * 100).toFixed(1)}%`,
      period: isZh.value ? '30D' : '30D',
      hint: isZh.value ? '~ 适中为宜' : '~ Moderate is ideal',
      iconType: 'turnover' as const,
      rawValue: a.turnover_rate * 100,
      direction: 'neutral' as const,
      markers: ['0', '25%', '50%'],
      baselineDir: 'neutral' as const,
      baselineText: isZh.value ? '正常区间' : 'Normal range',
      trend: 'stable' as const,
      trendLabel: isZh.value ? '交易活跃' : 'Active',
      sparklinePoints: generateSparklinePoints('turnover')
    },
    {
      name: isZh.value ? '跟踪误差' : 'Tracking Error',
      value: `${(a.tracking_error * 100).toFixed(1)}%`,
      period: isZh.value ? '集中度' : 'Est',
      hint: isZh.value ? '↓ 越低越好' : '↓ Lower is better',
      iconType: 'tracking' as const,
      rawValue: a.tracking_error * 100,
      direction: 'lower-better' as const,
      markers: ['0', '10%', '20%'],
      baselineDir: 'down' as const,
      baselineText: isZh.value ? '适度分散' : 'Moderate',
      trend: 'stable' as const,
      trendLabel: isZh.value ? '分散度上升' : 'More diversified',
      sparklinePoints: generateSparklinePoints('tracking')
    }
  ]
})

const positions = ref<any[]>([
  { symbol: '600519', symbol_name: '贵州茅台', quantity: 100, avg_price: 1850.00, current_price: 1920.50, market_value: 192050, profit_loss: 7050, profit_loss_pct: 0.0381, change_pct: 0.0156, status: 'normal' },
  { symbol: '000858', symbol_name: '五粮液', quantity: 200, avg_price: 165.00, current_price: 178.20, market_value: 35640, profit_loss: 2640, profit_loss_pct: 0.08, change_pct: 0.0215, status: 'normal' },
  { symbol: '601318', symbol_name: '中国平安', quantity: 500, avg_price: 45.80, current_price: 43.25, market_value: 21625, profit_loss: -1275, profit_loss_pct: -0.0557, change_pct: -0.0123, status: 'normal' },
  { symbol: '600036', symbol_name: '招商银行', quantity: 300, avg_price: 35.50, current_price: 38.90, market_value: 11670, profit_loss: 1020, profit_loss_pct: 0.0958, change_pct: 0.0089, status: 'normal' },
  { symbol: '000333', symbol_name: '美的集团', quantity: 400, avg_price: 58.20, current_price: 62.15, market_value: 24860, profit_loss: 1580, profit_loss_pct: 0.0679, change_pct: 0.0192, status: 'normal' }
])

// ========== 风险事件数据 ==========
const events = ref<any[]>([
  { event_id: '1', level: 'warning', message: '行业集中度过高', details: '金融行业集中度达到35%，接近30%限额', timestamp: new Date(Date.now() - 300000).toISOString() },
  { event_id: '2', level: 'error', message: '单票持仓超限', details: '600519 持仓达到12%，超过10%限额', timestamp: new Date(Date.now() - 900000).toISOString() },
  { event_id: '3', level: 'info', message: '自动减仓已执行', details: '已将600519减仓至9.8%', timestamp: new Date(Date.now() - 1200000).toISOString() },
  { event_id: '4', level: 'warning', message: '杠杆接近上限', details: '当前杠杆1.9x，限额2.0x', timestamp: new Date(Date.now() - 1800000).toISOString() },
  { event_id: '5', level: 'info', message: '每日风险评估完成', details: '所有指标正常', timestamp: new Date(Date.now() - 3600000).toISOString() }
])

// ========== 高级风险分析数据 ==========
const analysisLoading = ref(false)
const stressTestLoading = ref(false)
const varConfidence = ref(0.95)

const riskAnalysis = ref({
  var_95: 0.025,
  var_99: 0.035,
  cvar_95: 0.032,
  beta: 1.05,
  current_drawdown: -0.035,
  max_drawdown: -0.082,
  daily_volatility: 0.018
})

const factorExposures = ref<Record<string, number>>({
  size: 0.15,
  value: -0.08,
  momentum: 0.22,
  beta: 1.05
})

const factorExposureLimits = ref<Record<string, number>>({
  size: 0.5,
  value: 0.3,
  momentum: 0.4,
  beta: 1.2
})

const stressTestResult = ref<any>(null)
const riskRecommendations = ref<string[]>([])

// ========== 大盘风险数据 ==========
const marketUpdateTime = ref('09:35:00')

// 市场情绪指标
const marketSentiment = ref({
  limitUp: 45,          // 涨停家数
  limitDown: 23,        // 跌停家数
  upDownRatio: 1.85,    // 涨跌比
  upRatio: 0.65,        // 上涨比例
  turnover: '1.2万亿',  // 成交额
  turnoverChange: 15.2, // 成交额变化%
  northBound: 56.8,     // 北向资金（亿）
  northBoundDays: 3     // 连续流入天数
})

// 涨跌停状态：涨>跌用up(红)，跌>涨用down(绿)
const limitStatus = computed(() => {
  if (marketSentiment.value.limitUp > marketSentiment.value.limitDown) {
    return 'up'
  } else if (marketSentiment.value.limitDown > marketSentiment.value.limitUp) {
    return 'down'
  }
  return 'neutral'
})

// 板块涨幅榜
const topGainers = ref([
  { name: 'AI算力', code: 'BK001', change: 0.0325 },
  { name: '芯片半导体', code: 'BK002', change: 0.0287 },
  { name: '机器人', code: 'BK003', change: 0.0256 },
  { name: '数字经济', code: 'BK004', change: 0.0218 },
  { name: '新能源车', code: 'BK005', change: 0.0195 }
])

// 板块跌幅榜
const topLosers = ref([
  { name: '银行', code: 'BK101', change: -0.0152 },
  { name: '房地产', code: 'BK102', change: -0.0138 },
  { name: '白酒', code: 'BK103', change: -0.0115 },
  { name: '医药商业', code: 'BK104', change: -0.0098 },
  { name: '建材', code: 'BK105', change: -0.0085 }
])

// 持仓板块
const mySectors = ref([
  { name: '科技', code: 'BK201', weight: 0.35, change: 0.012 },
  { name: '新能源', code: 'BK202', weight: 0.25, change: -0.005 },
  { name: '医药', code: 'BK203', weight: 0.15, change: 0.008 },
  { name: '消费', code: 'BK204', weight: 0.10, change: -0.003 }
])

// 综合风险评分
const comprehensiveRiskScore = ref<any>({
  score: 0,
  level: 'unknown',
  dimensions: {
    position: { score: 0, weight: 0.25, max_score: 25, details: '' },
    drawdown: { score: 0, weight: 0.25, max_score: 25, details: '' },
    var_cvar: { score: 0, weight: 0.25, max_score: 25, details: '' },
    beta_factor: { score: 0, weight: 0.25, max_score: 25, details: '' }
  },
  top_risks: [],
  recommendations: []
})

// 为 RiskScoreGauge 转换数据格式
const riskScoreDimensions = computed(() => {
  const dims = comprehensiveRiskScore.value.dimensions || {}
  return [
    { name: isZh.value ? '仓位风险' : 'Position', score: dims.position?.score || 0, maxScore: dims.position?.max_score || 25 },
    { name: isZh.value ? '回撤风险' : 'Drawdown', score: dims.drawdown?.score || 0, maxScore: dims.drawdown?.max_score || 25 },
    { name: isZh.value ? 'VaR/CVaR' : 'VaR/CVaR', score: dims.var_cvar?.score || 0, maxScore: dims.var_cvar?.max_score || 25 },
    { name: isZh.value ? 'Beta/因子' : 'Beta/Factor', score: dims.beta_factor?.score || 0, maxScore: dims.beta_factor?.max_score || 25 }
  ]
})

// 为 FactorExposureCard 转换数据格式
const factorExposureList = computed(() => {
  const factors = factorExposures.value || {}
  return Object.entries(factors).map(([name, value]) => ({ name, value }))
})

const scoreLoading = ref(false)

// 评分视图模式
const scoreViewMode = ref<'current' | 'trend'>('current')
const riskTrendChartRef = ref<HTMLElement | null>(null)
let riskTrendChart: echarts.ECharts | null = null

// 风险趋势历史数据
const riskTrendData = ref<{ date: string; score: number }[]>([])

// 风险趋势统计
const riskTrendStats = computed(() => {
  if (riskTrendData.value.length === 0) {
    return { avg7d: 0, trend: 'stable', max: 0, min: 0 }
  }
  const scores = riskTrendData.value.map(d => d.score)
  const avg7d = scores.slice(-7).reduce((a, b) => a + b, 0) / Math.min(7, scores.length)
  const recentScores = scores.slice(-3)
  const olderScores = scores.slice(-6, -3)
  let trend = 'stable'
  if (olderScores.length > 0) {
    const recentAvg = recentScores.reduce((a, b) => a + b, 0) / recentScores.length
    const olderAvg = olderScores.reduce((a, b) => a + b, 0) / olderScores.length
    if (recentAvg - olderAvg > 5) trend = 'up'
    else if (olderAvg - recentAvg > 5) trend = 'down'
  }
  return {
    avg7d,
    trend,
    max: Math.max(...scores),
    min: Math.min(...scores)
  }
})

// 风险预警列表
const riskAlerts = ref<Array<{
  level: 'critical' | 'warning' | 'info'
  title: string
  description: string
  timestamp: string
  dimension?: string
}>>([])

// 初始化风险趋势图
const initRiskTrendChart = () => {
  if (!riskTrendChartRef.value) {
    console.warn('[RiskTrendChart] DOM元素未就绪')
    return
  }

  // 检查元素是否有有效的尺寸
  const rect = riskTrendChartRef.value.getBoundingClientRect()
  if (rect.width <= 0 || rect.height <= 0) {
    console.warn('[RiskTrendChart] 元素尺寸无效, width:', rect.width, 'height:', rect.height)
    // 延迟重试
    setTimeout(() => {
      if (riskTrendChartRef.value) {
        const retryRect = riskTrendChartRef.value.getBoundingClientRect()
        if (retryRect.width > 0 && retryRect.height > 0) {
          initRiskTrendChart()
        }
      }
    }, 100)
    return
  }

  if (riskTrendChart) {
    riskTrendChart.dispose()
  }

  try {
    riskTrendChart = echarts.init(riskTrendChartRef.value)

  const option: echarts.EChartsOption = {
    grid: {
      top: 20,
      right: 20,
      bottom: 30,
      left: 40
    },
    xAxis: {
      type: 'category',
      data: riskTrendData.value.map(d => d.date.slice(5)),
      axisLine: { lineStyle: { color: '#2a2e39' } },
      axisLabel: { color: '#787b86', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#2a2e39' } },
      axisLabel: { color: '#787b86', fontSize: 10 }
    },
    series: [{
      type: 'line',
      data: riskTrendData.value.map(d => d.score),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        color: '#2962ff',
        width: 2
      },
      itemStyle: {
        color: '#2962ff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(41, 98, 255, 0.3)' },
            { offset: 1, color: 'rgba(41, 98, 255, 0.05)' }
          ]
        }
      }
    }],
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e222d',
      borderColor: '#2a2e39',
      textStyle: { color: '#d1d4dc' },
      formatter: (params: any) => {
        const data = params[0]
        return `${data.name}<br/>风险评分: <strong style="color: #2962ff">${data.value}</strong>`
      }
    }
  }

    riskTrendChart.setOption(option)
    console.log('[RiskTrendChart] 图表初始化成功')
  } catch (error) {
    console.error('[RiskTrendChart] 图表初始化失败:', error)
  }
}

// 处理风险趋势图resize
const handleRiskTrendChartResize = () => {
  if (riskTrendChart) {
    riskTrendChart.resize()
  }
}

// 加载风险趋势数据
const loadRiskTrendData = async () => {
  // 生成模拟历史数据（实际应从API获取）
  const today = new Date()
  const data = []
  for (let i = 29; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    data.push({
      date: date.toISOString().split('T')[0],
      score: Math.round(25 + Math.random() * 40)
    })
  }
  riskTrendData.value = data

  // 更新图表 - 始终初始化，因为趋势图现在在三栏布局中始终可见
  nextTick(() => initRiskTrendChart())
}

// 加载风险预警
const loadRiskAlerts = async () => {
  try {
    // 从后端API获取风险事件
    const response = await riskAnalysisApi.getRiskEvents(10)
    const codeValue = response?.code
    const isSuccess = codeValue === 200 || codeValue === '200'

    if (isSuccess && response?.data?.events) {
      // 将后端事件转换为前端预警格式
      const alerts: typeof riskAlerts.value = response.data.events.map((event: any) => ({
        level: event.risk_level === 'critical' ? 'critical' :
               event.risk_level === 'high' ? 'warning' : 'info',
        title: event.message || `${event.risk_type} 预警`,
        description: `当前值: ${event.current_value?.toFixed(2) || 'N/A'}, 阈值: ${event.threshold?.toFixed(2) || 'N/A'}`,
        timestamp: event.triggered_at,
        dimension: event.risk_type
      }))

      riskAlerts.value = alerts
      console.log('[RiskAlerts] 从API加载预警:', alerts.length)
    } else {
      // API失败时使用本地规则生成预警
      generateLocalAlerts()
    }
  } catch (error) {
    console.warn('[RiskAlerts] API调用失败，使用本地规则:', error)
    // API调用失败时使用本地规则生成预警
    generateLocalAlerts()
  }
}

// 本地规则生成预警（备用）
const generateLocalAlerts = () => {
  const alerts: typeof riskAlerts.value = []

  if (comprehensiveRiskScore.value.score > 60) {
    alerts.push({
      level: 'critical',
      title: isZh.value ? '高风险警告' : 'High Risk Alert',
      description: isZh.value ? '综合风险评分超过60，建议立即降低仓位' : 'Risk score exceeds 60, consider reducing positions',
      timestamp: new Date().toISOString(),
      dimension: 'overall'
    })
  }

  if (Math.abs(riskAnalysis.value.current_drawdown) > 0.05) {
    alerts.push({
      level: 'warning',
      title: isZh.value ? '回撤预警' : 'Drawdown Warning',
      description: isZh.value ? `当前回撤 ${(riskAnalysis.value.current_drawdown * 100).toFixed(1)}%，接近止损线` : `Current drawdown at ${(riskAnalysis.value.current_drawdown * 100).toFixed(1)}%`,
      timestamp: new Date().toISOString(),
      dimension: 'drawdown'
    })
  }

  if (riskAnalysis.value.beta > 1.3) {
    alerts.push({
      level: 'warning',
      title: isZh.value ? 'Beta系数过高' : 'High Beta Warning',
      description: isZh.value ? `组合Beta系数 ${riskAnalysis.value.beta.toFixed(2)}，市场敏感度高` : `Portfolio Beta at ${riskAnalysis.value.beta.toFixed(2)}`,
      timestamp: new Date().toISOString(),
      dimension: 'beta_factor'
    })
  }

  if (riskAnalysis.value.var_95 > 0.04) {
    alerts.push({
      level: 'info',
      title: isZh.value ? 'VaR提示' : 'VaR Notice',
      description: isZh.value ? `95% VaR为 ${(riskAnalysis.value.var_95 * 100).toFixed(1)}%，注意风险敞口` : `95% VaR at ${(riskAnalysis.value.var_95 * 100).toFixed(1)}%`,
      timestamp: new Date().toISOString(),
      dimension: 'var_cvar'
    })
  }

  riskAlerts.value = alerts
}

// 格式化预警时间
const formatAlertTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return isZh.value ? '刚刚' : 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} ${isZh.value ? '分钟前' : 'min ago'}`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} ${isZh.value ? '小时前' : 'hr ago'}`
  return date.toLocaleDateString()
}

// 查看预警详情
const viewAlertDetail = (alert: typeof riskAlerts.value[0]) => {
  ElMessage.info(isZh.value ? `查看预警: ${alert.title}` : `View alert: ${alert.title}`)
}

// 关闭单个预警
const dismissAlert = (index: number) => {
  riskAlerts.value.splice(index, 1)
}

// 关闭所有预警
const dismissAllAlerts = () => {
  riskAlerts.value = []
  ElMessage.success(isZh.value ? '已清除所有预警' : 'All alerts dismissed')
}

// 监听视图模式变化
watch(scoreViewMode, (newMode) => {
  if (newMode === 'trend') {
    nextTick(() => initRiskTrendChart())
  }
})

// 计算属性：风险仪表盘等级
const riskGaugeLevel = computed(() => {
  const var95 = Math.abs(riskAnalysis.value.var_95)
  if (var95 > 0.06) return 'critical'
  if (var95 > 0.04) return 'high'
  if (var95 > 0.02) return 'medium'
  return 'low'
})

// 高级分析方法
const refreshRiskAnalysis = async () => {
  analysisLoading.value = true
  try {
    // 调用后端API获取风险分析报告
    const accountId = 'default_account'
    const response = await riskAnalysisApi.getReport(accountId)

    // 检查API响应 - 支持两种格式
    const isSuccess = response.data?.code === 200 || response.data?.success === true
    if (isSuccess && response.data?.data) {
      const data = response.data.data
      riskAnalysis.value = data.risk_metrics
      factorExposures.value = data.factor_exposures
      riskRecommendations.value = data.recommendations
    } else {
      // 如果API返回失败，使用备用数据
      riskAnalysis.value = {
        var_95: 0.025 + Math.random() * 0.01,
        var_99: 0.035 + Math.random() * 0.01,
        cvar_95: 0.032 + Math.random() * 0.01,
        beta: 1.0 + Math.random() * 0.2,
        current_drawdown: -0.03 - Math.random() * 0.02,
        max_drawdown: -0.082,
        daily_volatility: 0.015 + Math.random() * 0.005
      }
      factorExposures.value = {
        size: (Math.random() - 0.5) * 0.3,
        value: (Math.random() - 0.5) * 0.2,
        momentum: (Math.random() - 0.5) * 0.25,
        beta: riskAnalysis.value.beta
      }
      riskRecommendations.value = [
        '当前VaR水平适中，继续保持监控',
        '建议关注因子暴露变化',
        'Beta接近1.0，组合与市场同步性较高'
      ]
    }
    ElMessage.success(isZh.value ? '风险分析已更新' : 'Risk analysis updated')
  } catch (error) {
    console.error('Risk analysis failed:', error)
    // API调用失败时使用备用数据
    riskAnalysis.value = {
      var_95: 0.025 + Math.random() * 0.01,
      var_99: 0.035 + Math.random() * 0.01,
      cvar_95: 0.032 + Math.random() * 0.01,
      beta: 1.0 + Math.random() * 0.2,
      current_drawdown: -0.03 - Math.random() * 0.02,
      max_drawdown: -0.082,
      daily_volatility: 0.015 + Math.random() * 0.005
    }
    factorExposures.value = {
      size: (Math.random() - 0.5) * 0.3,
      value: (Math.random() - 0.5) * 0.2,
      momentum: (Math.random() - 0.5) * 0.25,
      beta: riskAnalysis.value.beta
    }
    riskRecommendations.value = [
      '当前VaR水平适中，继续保持监控',
      '建议关注因子暴露变化',
      'Beta接近1.0，组合与市场同步性较高'
    ]
    ElMessage.warning(isZh.value ? '使用离线数据' : 'Using offline data')
  } finally {
    analysisLoading.value = false
  }
}

// 获取综合风险评分
const refreshRiskScore = async () => {
  scoreLoading.value = true
  try {
    const accountId = 'default_account'
    const response = await riskAnalysisApi.getScore(accountId)

    // 检查API响应 - 支持两种格式
    const isSuccess = response.data?.code === 200 || response.data?.success === true
    if (isSuccess && response.data?.data) {
      comprehensiveRiskScore.value = response.data.data
    } else {
      // 如果API返回失败，使用备用估算
      comprehensiveRiskScore.value = {
        score: 25 + Math.random() * 30,
        level: 'medium',
        dimensions: {
          position: { score: 8 + Math.random() * 5, weight: 0.25, max_score: 25, details: '仓位适中，集中度正常' },
          drawdown: { score: 5 + Math.random() * 8, weight: 0.25, max_score: 25, details: '当前回撤较小' },
          var_cvar: { score: 6 + Math.random() * 6, weight: 0.25, max_score: 25, details: 'VaR/CVaR在正常范围' },
          beta_factor: { score: 4 + Math.random() * 5, weight: 0.25, max_score: 25, details: 'Beta和因子暴露正常' }
        },
        top_risks: [],
        recommendations: ['风险水平适中，继续保持监控']
      }
    }

    // 加载趋势数据和预警
    await Promise.all([
      loadRiskTrendData(),
      loadRiskAlerts()
    ])
  } catch (error) {
    console.error('Risk score failed:', error)
    // 使用备用估算
    comprehensiveRiskScore.value = {
      score: 30 + Math.random() * 20,
      level: 'medium',
      dimensions: {
        position: { score: 10, weight: 0.25, max_score: 25, details: '估算数据' },
        drawdown: { score: 8, weight: 0.25, max_score: 25, details: '估算数据' },
        var_cvar: { score: 7, weight: 0.25, max_score: 25, details: '估算数据' },
        beta_factor: { score: 5, weight: 0.25, max_score: 25, details: '估算数据' }
      },
      top_risks: [],
      recommendations: ['使用离线数据']
    }
    // 加载备用趋势数据
    loadRiskTrendData()
    loadRiskAlerts()
  } finally {
    scoreLoading.value = false
  }
}

// 获取风险等级对应的颜色
const getRiskLevelColor = (level: string) => {
  const colors: Record<string, string> = {
    low: '#26a69a',
    medium: '#ff9800',
    high: '#f44336',
    critical: '#9c27b0'
  }
  return colors[level] || '#787b86'
}

// 获取风险等级文本
const getRiskLevelText = (level: string) => {
  const texts: Record<string, string> = {
    low: isZh.value ? '低风险' : 'Low',
    medium: isZh.value ? '中等风险' : 'Medium',
    high: isZh.value ? '高风险' : 'High',
    critical: isZh.value ? '严重风险' : 'Critical',
    unknown: isZh.value ? '未知' : 'Unknown'
  }
  return texts[level] || level
}

// 获取维度名称
const getDimensionName = (key: string) => {
  const names: Record<string, string> = {
    position: isZh.value ? '仓位风险' : 'Position',
    drawdown: isZh.value ? '回撤风险' : 'Drawdown',
    var_cvar: isZh.value ? 'VaR/CVaR' : 'VaR/CVaR',
    beta_factor: isZh.value ? 'Beta/因子' : 'Beta/Factor'
  }
  return names[key] || key
}

// 获取维度颜色
const getDimensionColor = (ratio: number) => {
  if (ratio > 0.8) return '#f44336'
  if (ratio > 0.6) return '#ff9800'
  if (ratio > 0.4) return '#ffc107'
  return '#26a69a'
}

// 格式化百分比
const formatPercent = (value: number) => {
  if (value === null || value === undefined) return '-'
  return `${(value * 100).toFixed(2)}%`
}

// VaR 颜色类
const getVaRClass = computed(() => {
  const var95 = Math.abs(riskAnalysis.value.var_95)
  if (var95 > 0.06) return 'critical'
  if (var95 > 0.04) return 'warning'
  return 'normal'
})

// CVaR 颜色类
const getCvarClass = computed(() => {
  const cvar95 = Math.abs(riskAnalysis.value.cvar_95)
  if (cvar95 > 0.08) return 'critical'
  if (cvar95 > 0.05) return 'warning'
  return 'normal'
})

// Beta 颜色类
const getBetaClass = computed(() => {
  const beta = riskAnalysis.value.beta
  if (beta > 1.5 || beta < 0.5) return 'critical'
  if (beta > 1.2 || beta < 0.8) return 'warning'
  return 'normal'
})

// 计算评分弧路径 - 从左(绿/低风险)向右(红/高风险)填充
const getScoreArcPath = (score: number) => {
  const maxAngle = 180
  const angle = (score / 100) * maxAngle
  // 从左侧(180°)开始，向右侧(0°)填充
  const startAngle = 180
  const endAngle = 180 - angle
  const radius = 80
  const cx = 100
  const cy = 100

  const startRad = (startAngle * Math.PI) / 180
  const endRad = (endAngle * Math.PI) / 180

  // 计算起点和终点坐标
  const x1 = cx + radius * Math.cos(startRad)
  const y1 = cy - radius * Math.sin(startRad)
  const x2 = cx + radius * Math.cos(endRad)
  const y2 = cy - radius * Math.sin(endRad)

  const largeArc = angle > 180 ? 1 : 0

  // 使用 sweep-flag=1 顺时针绘制上半圆弧（与背景弧方向一致）
  return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`
}

// 计算指针位置 - 从左侧(180°)向右侧(0°)移动
const getScorePointerPos = (score: number) => {
  const maxAngle = 180
  const angle = 180 - (score / 100) * maxAngle  // 分数越高，角度越小（越靠右）
  const radius = 80
  const cx = 100
  const cy = 100

  const rad = (angle * Math.PI) / 180
  const x = cx + radius * Math.cos(rad)
  const y = cy - radius * Math.sin(rad)

  return { x, y }
}

// 判断是否为当前风险状态对应的情景
// 基于当前VaR值来确定最接近的压力测试情景
const isCurrentScenario = (scenario: any) => {
  // 使用当前的VaR(95%)值来估算当前风险水平
  const currentVarPct = Math.abs(riskAnalysis.value.var_95)

  // 获取情景的损失百分比（绝对值）
  const scenarioLossPct = Math.abs(scenario.estimated_loss_pct)

  // 如果当前VaR接近某个情景的损失百分比（在3%范围内），则认为是当前情景
  // 或者当前VaR小于该情景但大于前一个情景
  const tolerance = 0.03

  if (!stressTestResult.value?.scenarios) return false

  const scenarios = stressTestResult.value.scenarios
    .filter((s: any) => s.estimated_loss_pct < 0) // 只考虑下跌情景
    .sort((a: any, b: any) => Math.abs(a.estimated_loss_pct) - Math.abs(b.estimated_loss_pct))

  // 找到第一个损失百分比大于等于当前VaR的情景
  for (let i = 0; i < scenarios.length; i++) {
    const s = scenarios[i]
    const sLoss = Math.abs(s.estimated_loss_pct)

    if (currentVarPct <= sLoss + tolerance) {
      return s.name === scenario.name
    }
  }

  // 如果当前VaR超过所有情景，标记最严重的那个
  if (scenarios.length > 0) {
    const worstScenario = scenarios[scenarios.length - 1]
    return worstScenario.name === scenario.name && currentVarPct > Math.abs(worstScenario.estimated_loss_pct)
  }

  return false
}

// 运行压力测试，结果直接显示在页面内
const runStressTest = async () => {
  stressTestLoading.value = true
  try {
    // 调用后端API运行压力测试
    // 根据当前模式传递mode参数
    const accountId = 'default_account'
    const mode = isSimulatedMode.value ? 'simulated' : 'live'
    console.log('[Stress Test] 运行压力测试, 模式:', mode)
    const response = await riskAnalysisApi.runStressTest(accountId, undefined, mode)

    // 检查API响应
    const codeValue = response?.code
    const isSuccess = codeValue === 200 || codeValue === '200' || response?.success === true

    if (isSuccess && response?.data) {
      stressTestResult.value = response.data
      console.log('[Stress Test] ✅ 完成, 模式:', response.data?.mode, ', scenarios:', response.data?.scenarios?.length)
      ElMessage.success(isZh.value ? '压力测试完成' : 'Stress test completed')
    } else {
      // 如果API返回失败，使用备用数据
      console.warn('Stress test API returned non-success, using fallback data')
      const totalAssets = currentPositionSummary.value.total_assets || 1000000
      const mode = isSimulatedMode.value ? 'simulated' : 'live'
      stressTestResult.value = {
        account_id: accountId,
        mode: mode,
        total_assets: totalAssets,
        test_time: new Date().toISOString(),
        scenarios: [
          { name: '轻度下跌', params: { market_shock: -0.10 }, estimated_loss: totalAssets * -0.10, estimated_loss_pct: -0.10, impact_level: 'low' },
          { name: '中度下跌', params: { market_shock: -0.20 }, estimated_loss: totalAssets * -0.20, estimated_loss_pct: -0.20, impact_level: 'medium' },
          { name: '严重下跌', params: { market_shock: -0.30 }, estimated_loss: totalAssets * -0.30, estimated_loss_pct: -0.30, impact_level: 'high' },
          { name: '闪崩', params: { market_shock: -0.40 }, estimated_loss: totalAssets * -0.40, estimated_loss_pct: -0.40, impact_level: 'critical' },
          { name: '波动率翻倍', params: { vol_shock: 2.0 }, estimated_loss: totalAssets * -0.05, estimated_loss_pct: -0.05, impact_level: 'medium' },
          { name: '流动性危机', params: { liquidity_shock: 0.5 }, estimated_loss: totalAssets * -0.08, estimated_loss_pct: -0.08, impact_level: 'high' }
        ],
        risk_summary: {
          max_potential_loss: totalAssets * -0.40,
          max_potential_loss_pct: 0.40,
          worst_scenario: '闪崩',
          recommendations: [
            '建议设置止损点，在市场下跌超过15%时减仓',
            '考虑增加防御性资产配置',
            '监控市场流动性指标，做好应急准备'
          ]
        }
      }
      ElMessage.warning(isZh.value ? '使用离线数据' : 'Using offline data')
    }
  } catch (error) {
    console.error('Stress test failed:', error)
    // API调用失败时使用备用数据
    const totalAssets = currentPositionSummary.value.total_assets
    const mode = isSimulatedMode.value ? 'simulated' : 'live'
    stressTestResult.value = {
      account_id: 'default_account',
      mode: mode,
      total_assets: totalAssets,
      test_time: new Date().toISOString(),
      scenarios: [
        { name: '轻度下跌', params: { market_shock: -0.10 }, estimated_loss: totalAssets * -0.10, estimated_loss_pct: -0.10, impact_level: 'low' },
        { name: '中度下跌', params: { market_shock: -0.20 }, estimated_loss: totalAssets * -0.20, estimated_loss_pct: -0.20, impact_level: 'medium' },
        { name: '严重下跌', params: { market_shock: -0.30 }, estimated_loss: totalAssets * -0.30, estimated_loss_pct: -0.30, impact_level: 'high' },
        { name: '闪崩', params: { market_shock: -0.40 }, estimated_loss: totalAssets * -0.40, estimated_loss_pct: -0.40, impact_level: 'critical' },
        { name: '波动率翻倍', params: { vol_shock: 2.0 }, estimated_loss: totalAssets * -0.05, estimated_loss_pct: -0.05, impact_level: 'medium' },
        { name: '流动性危机', params: { liquidity_shock: 0.5 }, estimated_loss: totalAssets * -0.08, estimated_loss_pct: -0.08, impact_level: 'high' }
      ],
      risk_summary: {
        max_potential_loss: totalAssets * -0.40,
        max_potential_loss_pct: 0.40,
        worst_scenario: '闪崩',
        recommendations: [
          '建议设置止损点，在市场下跌超过15%时减仓',
          '考虑增加防御性资产配置',
          '监控市场流动性指标，做好应急准备'
        ]
      }
    }
    ElMessage.warning(isZh.value ? '使用离线数据' : 'Using offline data')
  } finally {
    stressTestLoading.value = false
  }
}

const getFactorName = (factor: string): string => {
  const names: Record<string, string> = {
    size: isZh.value ? '规模因子' : 'Size',
    value: isZh.value ? '价值因子' : 'Value',
    momentum: isZh.value ? '动量因子' : 'Momentum',
    beta: isZh.value ? 'Beta因子' : 'Beta'
  }
  return names[factor] || factor
}

const getImpactLevelText = (level: string): string => {
  const texts: Record<string, string> = {
    low: isZh.value ? '低影响' : 'Low',
    medium: isZh.value ? '中等影响' : 'Medium',
    high: isZh.value ? '高影响' : 'High',
    critical: isZh.value ? '严重影响' : 'Critical'
  }
  return texts[level] || level
}

// ========== 方法 ==========

const getRuleTypeText = (type: string) => {
  const map: Record<string, string> = {
    'position_limit': isZh.value ? '仓位限制' : 'Position Limit',
    'loss_limit': isZh.value ? '亏损限制' : 'Loss Limit',
    'drawdown_limit': isZh.value ? '回撤限制' : 'Drawdown Limit',
    'single_position_limit': isZh.value ? '单票限制' : 'Single Position'
  }
  return map[type] || type
}

const getPositionStatusText = (status: string) => {
  const map: Record<string, string> = {
    'normal': isZh.value ? '正常' : 'Normal',
    'suspended': isZh.value ? '停牌' : 'Suspended',
    'risk_limit': isZh.value ? '风险限制' : 'Risk Limit'
  }
  return map[status] || status
}

const formatCurrency = (value: number) => {
  const abs = Math.abs(value)
  const sign = value < 0 ? '-' : ''
  if (abs >= 10000) {
    return sign + '¥' + (abs / 10000).toFixed(2) + '万'
  }
  return sign + '¥' + abs.toFixed(2)
}

const formatNumber = (value: number) => new Intl.NumberFormat('zh-CN').format(value)

const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const formatParamValue = (value: any) => {
  if (typeof value === 'number') return (value * 100).toFixed(0) + '%'
  return value
}

// ========== 监控相关 ==========
let monitoringInterval: ReturnType<typeof setInterval> | null = null
let stressTestInterval: ReturnType<typeof setInterval> | null = null

const toggleMonitoring = async () => {
  toggling.value = true
  try {
    if (!monitoringActive.value) {
      // 启动监控
      const response = await riskAnalysisApi.startMonitoring()
      if (response?.code === 200 || response?.code === '200') {
        monitoringActive.value = true
        ElMessage.success(isZh.value ? '监控已启动' : 'Monitoring started')

        // 启动定期刷新风险指标（每30秒）
        monitoringInterval = setInterval(async () => {
          await refreshRiskAnalysis()
        }, 30000)

        // 启动自动压力测试（每5分钟）
        stressTestInterval = setInterval(async () => {
          console.log('[Monitor] 自动运行压力测试...')
          await runStressTest()
        }, 5 * 60 * 1000)

        // 启动时立即运行一次压力测试
        await runStressTest()
      }
    } else {
      // 停止监控
      const response = await riskAnalysisApi.stopMonitoring()
      if (response?.code === 200 || response?.code === '200') {
        monitoringActive.value = false
        ElMessage.success(isZh.value ? '监控已停止' : 'Monitoring stopped')

        // 清除定时器
        if (monitoringInterval) {
          clearInterval(monitoringInterval)
          monitoringInterval = null
        }
        if (stressTestInterval) {
          clearInterval(stressTestInterval)
          stressTestInterval = null
        }
      }
    }
  } catch (error) {
    console.error('监控操作失败:', error)
    ElMessage.error(isZh.value ? '监控操作失败' : 'Monitoring operation failed')
  } finally {
    toggling.value = false
  }
}

const refreshPositions = async () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success(isZh.value ? '持仓已刷新' : 'Positions refreshed')
  }, 500)
}

const toggleRule = async (rule: any) => {
  ElMessage.success(`${rule.rule_name} ${rule.enabled ? (isZh.value ? '已启用' : 'enabled') : (isZh.value ? '已禁用' : 'disabled')}`)
}

const editRule = (rule: any) => {
  ruleForm.value = { ...rule }
  ruleFormParams.value = JSON.stringify(rule.params || {})
  showAddRuleDialog.value = true
}

const removeRule = async (rule: any) => {
  try {
    await ElMessageBox.confirm(isZh.value ? '确定删除此规则?' : 'Delete this rule?', isZh.value ? '确认' : 'Confirm', { type: 'warning' })
    const index = rules.value.findIndex(r => r.rule_id === rule.rule_id)
    if (index > -1) rules.value.splice(index, 1)
    ElMessage.success(isZh.value ? '规则已删除' : 'Rule deleted')
  } catch {}
}

const addRule = async () => {
  if (!ruleForm.value.rule_id || !ruleForm.value.rule_name || !ruleForm.value.rule_type) {
    ElMessage.warning(isZh.value ? '请填写完整信息' : 'Please fill all fields')
    return
  }
  addingRule.value = true
  setTimeout(() => {
    try {
      const params = JSON.parse(ruleFormParams.value)
      rules.value.push({ ...ruleForm.value, params })
      showAddRuleDialog.value = false
      ruleForm.value = { rule_id: '', rule_name: '', rule_type: '', enabled: true }
      ruleFormParams.value = '{}'
      ElMessage.success(isZh.value ? '规则添加成功' : 'Rule added')
    } catch {
      ElMessage.error(isZh.value ? '参数格式错误' : 'Invalid params')
    }
    addingRule.value = false
  }, 300)
}

const loadEvents = () => {
  ElMessage.success(isZh.value ? '事件已刷新' : 'Events refreshed')
}

// ========== AI智能调参功能 ==========
const analyzeWithAI = async () => {
  aiAnalyzing.value = true
  // 模拟AI分析（实际应调用后端API）
  setTimeout(() => {
    aiSuggestions.value = [
      {
        rule_id: 'position_limit_001',
        rule_name: isZh.value ? '仓位上限控制' : 'Position Limit',
        current: 0.8,
        suggested: 0.75,
        reason: isZh.value ? '近期市场波动加大，建议降低仓位上限以控制风险' : 'Market volatility increased, suggest lower limit',
        impact: isZh.value ? '预计减少15%最大回撤风险' : 'Est. 15% max drawdown reduction'
      },
      {
        rule_id: 'single_position_001',
        rule_name: isZh.value ? '单票持仓限制' : 'Single Position Limit',
        current: 0.1,
        suggested: 0.08,
        reason: isZh.value ? '持仓集中度偏高，建议收紧单票限制' : 'High concentration, suggest tighter limit',
        impact: isZh.value ? '提升组合分散度' : 'Better diversification'
      },
      {
        rule_id: 'loss_limit_001',
        rule_name: isZh.value ? '日亏损限制' : 'Daily Loss Limit',
        current: 0.05,
        suggested: 0.03,
        reason: isZh.value ? '根据历史数据，更严格的止损可提升长期收益' : 'Stricter stop-loss improves long-term returns',
        impact: isZh.value ? '预计提升夏普比率0.2' : 'Est. Sharpe +0.2'
      }
    ]
    aiAnalyzing.value = false
  }, 1500)
}

const applyAISuggestion = (suggestion: any) => {
  const rule = rules.value.find(r => r.rule_id === suggestion.rule_id)
  if (rule) {
    // 更新参数
    const key = Object.keys(rule.params)[0]
    if (key) {
      rule.params[key] = suggestion.suggested
    }
    ElMessage.success(isZh.value ? `已应用AI建议: ${suggestion.rule_name}` : `Applied: ${suggestion.rule_name}`)
  }
}

const applyAllSuggestions = () => {
  aiSuggestions.value.forEach(s => applyAISuggestion(s))
  showAIDialog.value = false
  aiSuggestions.value = []
  ElMessage.success(isZh.value ? '已应用所有AI建议' : 'All suggestions applied')
}

// ========== 规则回测功能 ==========
const showBacktest = (rule: any) => {
  backtestingRule.value = rule
  showBacktestDialog.value = true
  backtestResult.value = null
}

const runBacktest = async () => {
  backtestLoading.value = true
  // 模拟回测（实际应调用后端API）
  setTimeout(() => {
    backtestResult.value = {
      rule_name: backtestingRule.value.rule_name,
      period: isZh.value ? '近30天' : 'Last 30 days',
      trigger_count: Math.floor(Math.random() * 10) + 1,
      prevented_loss: (Math.random() * 50000 + 10000).toFixed(0),
      max_drawdown_reduced: (Math.random() * 5 + 2).toFixed(1),
      sharpe_improved: (Math.random() * 0.3 + 0.1).toFixed(2),
      recommendations: isZh.value ? [
        '规则阈值设置合理，触发频率适中',
        '建议在市场波动加大时适当收紧阈值',
        '历史数据显示该规则有效降低了最大回撤'
      ] : [
        'Threshold is reasonable, trigger frequency is moderate',
        'Suggest tightening during high volatility',
        'Historical data shows reduced max drawdown'
      ]
    }
    backtestLoading.value = false
  }, 1500)
}

// 初始化模拟收益走势数据
const initTrendData = () => {
  const dates: string[] = []
  const strategy: number[] = []
  const benchmark: number[] = []

  const now = new Date()
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)
    // 模拟策略收益（随机漫步）
    strategy.push(1 + (Math.random() - 0.4) * 0.1 * (30 - i))
    // 模拟基准收益
    benchmark.push(1 + (Math.random() - 0.45) * 0.05 * (30 - i))
  }

  trendData.value = { dates, strategy, benchmark }
}

// 渲染收益走势图
const renderTrendChart = () => {
  if (!trendChartRef.value) {
    setTimeout(() => renderTrendChart(), 200)
    return
  }

  try {
    if (!trendChartInstance) {
      trendChartInstance = echarts.init(trendChartRef.value, 'dark')
    }

    const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e222d',
      borderColor: '#2a2e39',
      textStyle: { color: '#d1d4dc' }
    },
    legend: {
      data: [isZh.value ? '策略' : 'Strategy', isZh.value ? '基准' : 'Benchmark'],
      top: 5,
      textStyle: { color: '#d1d4dc' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '18%',
      top: '8%',
      containLabel: true
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', start: 0, end: 100, height: 20, bottom: 8, borderColor: '#2a2e39', backgroundColor: '#1e222d', fillerColor: 'rgba(41, 98, 255, 0.2)', handleStyle: { color: '#2962ff' }, textStyle: { color: '#787b86' } }
    ],
    xAxis: {
      type: 'category',
      data: trendData.value.dates,
      axisLabel: { color: '#787b86', interval: 'auto' },
      axisLine: { lineStyle: { color: '#2a2e39' } },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#787b86',
        formatter: (v: number) => v.toFixed(2)
      },
      axisLine: { lineStyle: { color: '#2a2e39' } },
      splitLine: { lineStyle: { color: '#2a2e39' } }
    },
    series: [
      {
        name: isZh.value ? '策略' : 'Strategy',
        type: 'line',
        data: trendData.value.strategy,
        symbol: 'none',
        lineStyle: { color: '#2962ff', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(41, 98, 255, 0.3)' },
            { offset: 1, color: 'rgba(41, 98, 255, 0.05)' }
          ])
        }
      },
      {
        name: isZh.value ? '基准' : 'Benchmark',
        type: 'line',
        data: trendData.value.benchmark,
        symbol: 'none',
        lineStyle: { color: '#787b86', width: 1.5, type: 'dashed' }
      }
    ]
  }

  trendChartInstance.setOption(option)
  } catch (error) {
    console.error('Failed to render trend chart:', error)
  }
}

// ========== 组合分析指标辅助函数（新版：信号灯+风险区间+趋势） ==========

// --- 整体风险区间 ---
const getOverallRiskPosition = computed(() => {
  // 基于所有指标计算整体风险位置 (0-100)
  const vol = currentPositionAnalysis.value.volatility
  const dd = currentPositionAnalysis.value.max_drawdown  // 负数，如 -0.15 表示 -15%
  const beta = Math.abs(currentPositionAnalysis.value.beta)

  let score = 0
  // 波动率贡献
  if (vol > 0.35) score += 30
  else if (vol > 0.25) score += 20
  else if (vol > 0.15) score += 10

  // 回撤贡献（dd是负数，越负风险越高）
  if (dd < -0.20) score += 40
  else if (dd < -0.10) score += 25
  else if (dd < -0.05) score += 10

  // Beta贡献
  if (beta > 1.5) score += 30
  else if (beta > 1.2) score += 20
  else if (beta > 0.8) score += 5

  return Math.min(score, 100)
})

const getOverallRiskLevel = computed(() => {
  const pos = getOverallRiskPosition.value
  if (pos < 25) return 'safe'
  if (pos < 50) return 'caution'
  if (pos < 75) return 'warning'
  return 'danger'
})

const getOverallRiskLabel = computed(() => {
  const level = getOverallRiskLevel.value
  const labels: Record<string, { zh: string, en: string }> = {
    safe: { zh: '低风险', en: 'Low Risk' },
    caution: { zh: '中风险', en: 'Medium Risk' },
    warning: { zh: '高风险', en: 'High Risk' },
    danger: { zh: '危险', en: 'Danger' }
  }
  return isZh.value ? labels[level].zh : labels[level].en
})

// --- 迷你趋势图生成 ---
const sparklineData = ref<Record<string, number[]>>({
  volatility: [],
  beta: [],
  drawdown: [],
  turnover: [],
  return: [],
  tracking: [],
  // 新增风险指标趋势
  var: [],
  cvar: []
})

// 初始化趋势数据
const initSparklineData = () => {
  Object.keys(sparklineData.value).forEach(key => {
    sparklineData.value[key] = Array.from({ length: 10 }, () =>
      0.3 + Math.random() * 0.4
    )
  })
}

const generateSparklinePoints = (type: string): string => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return '0,20 80,20'

  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 80
    const y = 36 - (val * 32) // 反转，值越大y越小（线越高）
    return `${x.toFixed(1)},${y.toFixed(1)}`
  })
  return points.join(' ')
}

// 获取趋势图最后一个点的坐标（用于末端高亮）
const getSparklineEndPoint = (type: string): { x: number; y: number } => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return { x: 80, y: 20 }
  const lastVal = data[data.length - 1]
  return {
    x: 80,
    y: 36 - (lastVal * 32)
  }
}

// 获取最高点坐标
const getSparklineHighPoint = (type: string): { x: number; y: number; index: number } => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return { x: 40, y: 4, index: 0 }
  let maxVal = data[0]
  let maxIndex = 0
  data.forEach((val, i) => {
    if (val > maxVal) {
      maxVal = val
      maxIndex = i
    }
  })
  return {
    x: (maxIndex / (data.length - 1)) * 80,
    y: 36 - (maxVal * 32),
    index: maxIndex
  }
}

// 获取最低点坐标
const getSparklineLowPoint = (type: string): { x: number; y: number; index: number } => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return { x: 40, y: 36, index: 0 }
  let minVal = data[0]
  let minIndex = 0
  data.forEach((val, i) => {
    if (val < minVal) {
      minVal = val
      minIndex = i
    }
  })
  return {
    x: (minIndex / (data.length - 1)) * 80,
    y: 36 - (minVal * 32),
    index: minIndex
  }
}

// 获取趋势方向：'up' | 'down' | 'flat'
const getSparklineTrend = (type: string): 'up' | 'down' | 'flat' => {
  const data = sparklineData.value[type] || []
  if (data.length < 2) return 'flat'
  const first = data[0]
  const last = data[data.length - 1]
  const diff = last - first
  if (diff > 0.05) return 'up'
  if (diff < -0.05) return 'down'
  return 'flat'
}

// 获取趋势颜色（颜色联动）
const getSparklineColor = (type: string): string => {
  const trend = getSparklineTrend(type)
  // 特殊处理：回撤指标，下降是好事
  if (type === 'drawdown') {
    return trend === 'down' ? '#26a69a' : trend === 'up' ? '#f44336' : '#787b86'
  }
  // 其他指标：上升绿色，下降红色
  return trend === 'up' ? '#26a69a' : trend === 'down' ? '#f44336' : '#787b86'
}

// 获取平均值Y坐标（用于参考线）
const getSparklineAverageY = (type: string): number => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return 20
  const avg = data.reduce((a, b) => a + b, 0) / data.length
  return 36 - (avg * 32)
}

// 获取Tooltip内容
const getSparklineTooltip = (type: string): { value: string; trend: string; change: string; changeClass: string } => {
  const data = sparklineData.value[type] || []
  const trend = getSparklineTrend(type)
  const trendLabel = trend === 'up' ? (isZh.value ? '↑ 上升' : '↑ Up') :
                     trend === 'down' ? (isZh.value ? '↓ 下降' : '↓ Down') :
                     (isZh.value ? '→ 平稳' : '→ Flat')

  if (data.length < 2) {
    return { value: '-', trend: trendLabel, change: '-', changeClass: '' }
  }

  const last = data[data.length - 1]
  const first = data[0]
  const changePercent = ((last - first) / first * 100)
  const change = changePercent.toFixed(1)

  return {
    value: (last * 100).toFixed(1) + '%',
    trend: trendLabel,
    change: (parseFloat(change) >= 0 ? '+' : '') + change + '%',
    changeClass: changePercent >= 0 ? 'positive' : 'negative'
  }
}

// ============================================
// 迷你趋势图方法（用于仪表盘卡片，60x24尺寸）
// ============================================

// 生成迷你趋势图点（120x48尺寸）
const generateSparklinePointsMini = (type: string): string => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return '0,24 120,24'

  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 120
    const y = 44 - (val * 40) // 48px高度，留4px边距
    return `${x.toFixed(1)},${y.toFixed(1)}`
  })
  return points.join(' ')
}

// 获取迷你趋势图平均线Y坐标
const getSparklineAverageYMini = (type: string): number => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return 24
  const avg = data.reduce((a, b) => a + b, 0) / data.length
  return 44 - (avg * 40)
}

// 获取迷你趋势图末端点坐标
const getSparklineEndPointMini = (type: string): { x: number; y: number } => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return { x: 120, y: 24 }
  const lastVal = data[data.length - 1]
  return {
    x: 120,
    y: 44 - (lastVal * 40)
  }
}

// 获取迷你趋势图最高点坐标
const getSparklineHighPointMini = (type: string): { x: number; y: number } => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return { x: 60, y: 4 }
  let maxIdx = 0
  let maxVal = data[0]
  data.forEach((val, i) => {
    if (val > maxVal) {
      maxVal = val
      maxIdx = i
    }
  })
  return {
    x: (maxIdx / (data.length - 1)) * 120,
    y: 44 - (maxVal * 40)
  }
}

// 获取迷你趋势图最低点坐标
const getSparklineLowPointMini = (type: string): { x: number; y: number } => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return { x: 60, y: 44 }
  let minIdx = 0
  let minVal = data[0]
  data.forEach((val, i) => {
    if (val < minVal) {
      minVal = val
      minIdx = i
    }
  })
  return {
    x: (minIdx / (data.length - 1)) * 120,
    y: 44 - (minVal * 40)
  }
}

// ============================================
// 仪表盘卡片增强方法
// ============================================

// --- VaR 指标方法 ---
// 阈值与进度条指示器颜色一致：percent = var95 * 1000
const getVarSignal = (var95: number | undefined): string => {
  if (var95 === undefined || var95 === null) return ''
  const percent = var95 * 1000
  if (percent < 50) return 'low'
  if (percent < 75) return 'medium'
  return 'high'
}

const getVarLevel = computed(() => {
  const var95 = riskAnalysis.value.var_95
  if (var95 < 0.03) return 'low'
  if (var95 < 0.05) return 'medium'
  if (var95 < 0.08) return 'high'
  return 'critical'
})

const getVarBaselineDir = (var95: number): string => {
  if (var95 > 0.05) return 'up'
  if (var95 < 0.025) return 'down'
  return 'stable'
}

const getVarBaselineText = (var95: number): string => {
  if (var95 > 0.08) return isZh.value ? '显著高于均值' : 'Well above avg'
  if (var95 > 0.05) return isZh.value ? '略高于均值' : 'Above average'
  if (var95 < 0.025) return isZh.value ? '远低于均值' : 'Well below avg'
  return isZh.value ? '低于均值' : 'Below average'
}

const getVarTrend = computed(() => {
  const data = sparklineData.value.var
  if (data.length < 2) return 'trend-stable'
  const last = data.slice(-3)
  const avg = last.reduce((a, b) => a + b, 0) / last.length
  return avg > 0.55 ? 'trend-up' : avg < 0.4 ? 'trend-down' : 'trend-stable'
})

const getVarTrendLabel = computed(() => {
  const trend = getVarTrend.value
  if (trend === 'trend-up') return isZh.value ? '风险升' : 'Rising'
  if (trend === 'trend-down') return isZh.value ? '风险降' : 'Falling'
  return isZh.value ? '稳定' : 'Stable'
})

// --- CVaR 指标方法 ---
// 阈值与进度条指示器颜色一致：percent = abs(cvar_95) * 800
const getCvarSignal = (cvar95: number | undefined): string => {
  if (cvar95 === undefined || cvar95 === null) return ''
  const percent = Math.abs(cvar95) * 800
  if (percent < 50) return 'low'
  if (percent < 75) return 'medium'
  return 'high'
}

const getCvarLevel = computed(() => {
  const cvar = Math.abs(riskAnalysis.value.cvar_95)
  if (cvar < 0.04) return 'low'
  if (cvar < 0.06) return 'medium'
  if (cvar < 0.10) return 'high'
  return 'critical'
})

const getCvarBaselineDir = (cvar95: number): string => {
  const absVal = Math.abs(cvar95)
  if (absVal > 0.07) return 'up'
  if (absVal < 0.04) return 'down'
  return 'stable'
}

const getCvarBaselineText = (cvar95: number): string => {
  const absVal = Math.abs(cvar95)
  if (absVal > 0.10) return isZh.value ? '显著高于VaR' : 'Above VaR'
  if (absVal > 0.06) return isZh.value ? '略高于VaR' : 'Near VaR'
  return isZh.value ? '接近VaR' : 'Near VaR'
}

const getCvarTrend = computed(() => {
  const data = sparklineData.value.cvar
  if (data.length < 2) return 'trend-stable'
  const last = data.slice(-3)
  const avg = last.reduce((a, b) => a + b, 0) / last.length
  return avg > 0.55 ? 'trend-up' : avg < 0.4 ? 'trend-down' : 'trend-stable'
})

const getCvarTrendLabel = computed(() => {
  const trend = getCvarTrend.value
  if (trend === 'trend-up') return isZh.value ? '尾部升' : 'Rising'
  if (trend === 'trend-down') return isZh.value ? '尾部降' : 'Falling'
  return isZh.value ? '稳定' : 'Stable'
})

// --- Drawdown 指标方法 ---
// 阈值与 gauge-value 数值颜色一致
const getDrawdownSignal = (drawdown: number | undefined): string => {
  if (drawdown === undefined || drawdown === null) return ''
  const percent = Math.abs(drawdown) * 500
  if (percent < 50) return 'low'
  if (percent < 75) return 'medium'
  return 'high'
}

const getDrawdownLevel = computed(() => {
  const dd = Math.abs(riskAnalysis.value.current_drawdown)
  if (dd < 0.03) return 'low'
  if (dd < 0.05) return 'medium'
  if (dd < 0.10) return 'high'
  return 'critical'
})

const getDrawdownBaselineDir = (drawdown: number): string => {
  const absVal = Math.abs(drawdown)
  if (absVal > 0.06) return 'up'
  if (absVal < 0.03) return 'down'
  return 'stable'
}

const getDrawdownBaselineText = (drawdown: number): string => {
  const absVal = Math.abs(drawdown)
  if (absVal > 0.10) return isZh.value ? '深度回撤' : 'Deep drawdown'
  if (absVal > 0.05) return isZh.value ? '中等回撤' : 'Moderate'
  return isZh.value ? '轻度回撤' : 'Minor'
}

const getDrawdownTrend = computed(() => {
  const data = sparklineData.value.drawdown
  if (data.length < 2) return 'trend-stable'
  const last = data.slice(-3)
  const avg = last.reduce((a, b) => a + b, 0) / last.length
  return avg > 0.55 ? 'trend-up' : avg < 0.4 ? 'trend-down' : 'trend-stable'
})

const getDrawdownTrendLabel = computed(() => {
  const trend = getDrawdownTrend.value
  if (trend === 'trend-up') return isZh.value ? '扩大' : 'Widening'
  if (trend === 'trend-down') return isZh.value ? '收窄' : 'Narrowing'
  return isZh.value ? '稳定' : 'Stable'
})

// --- Beta 指标方法 ---
// 阈值与 gauge-value 数值颜色一致
const getBetaSignal = (beta: number | undefined): string => {
  if (beta === undefined || beta === null) return ''
  const percent = Math.abs(beta - 1) * 100
  if (percent < 50) return 'low'
  if (percent < 75) return 'medium'
  return 'high'
}

const getBetaLevel = computed(() => {
  const beta = riskAnalysis.value.beta
  const absBeta = Math.abs(beta - 1)
  if (absBeta < 0.2) return 'low'
  if (absBeta < 0.4) return 'medium'
  if (absBeta < 0.6) return 'high'
  return 'critical'
})

const getBetaBaselineDir = (beta: number): string => {
  const diff = beta - 1
  if (diff > 0.3) return 'up'
  if (diff < -0.2) return 'down'
  return 'stable'
}

const getBetaBaselineText = (beta: number): string => {
  const diff = beta - 1
  if (diff > 0.5) return isZh.value ? '显著高于1' : 'Well above 1'
  if (diff > 0.2) return isZh.value ? '略高于1' : 'Above 1'
  if (diff < -0.3) return isZh.value ? '显著低于1' : 'Well below 1'
  if (diff < -0.1) return isZh.value ? '略低于1' : 'Below 1'
  return isZh.value ? '接近基准' : 'Near baseline'
}

const getBetaTrend = computed(() => {
  const data = sparklineData.value.beta
  if (data.length < 2) return 'trend-stable'
  const last = data.slice(-3)
  const avg = last.reduce((a, b) => a + b, 0) / last.length
  return avg > 0.55 ? 'trend-up' : avg < 0.4 ? 'trend-down' : 'trend-stable'
})

const getBetaTrendLabel = computed(() => {
  const trend = getBetaTrend.value
  if (trend === 'trend-up') return isZh.value ? '上升' : 'Rising'
  if (trend === 'trend-down') return isZh.value ? '下降' : 'Falling'
  return isZh.value ? '稳定' : 'Stable'
})

// --- Volatility 指标方法 ---
// 阈值与 gauge-value 数值颜色一致
const getVolatilitySignal = (volatility: number | undefined): string => {
  if (volatility === undefined || volatility === null) return ''
  const percent = volatility * 2000
  if (percent < 50) return 'low'
  if (percent < 75) return 'medium'
  return 'high'
}

const getVolatilityLevel = computed(() => {
  const vol = riskAnalysis.value.daily_volatility
  if (vol < 0.015) return 'low'
  if (vol < 0.025) return 'medium'
  if (vol < 0.035) return 'high'
  return 'critical'
})

const getVolatilityBaselineDir = (volatility: number): string => {
  if (volatility > 0.03) return 'up'
  if (volatility < 0.015) return 'down'
  return 'stable'
}

const getVolatilityBaselineText = (volatility: number): string => {
  if (volatility > 0.04) return isZh.value ? '显著偏高' : 'Very high'
  if (volatility > 0.025) return isZh.value ? '略高于均值' : 'Above avg'
  if (volatility < 0.012) return isZh.value ? '显著偏低' : 'Very low'
  return isZh.value ? '低于均值' : 'Below avg'
}

const getVolatilityTrend = computed(() => {
  const data = sparklineData.value.volatility
  if (data.length < 2) return 'trend-stable'
  const last = data.slice(-3)
  const avg = last.reduce((a, b) => a + b, 0) / last.length
  return avg > 0.55 ? 'trend-up' : avg < 0.4 ? 'trend-down' : 'trend-stable'
})

const getVolatilityTrendLabel = computed(() => {
  const trend = getVolatilityTrend.value
  if (trend === 'trend-up') return isZh.value ? '放大' : 'Rising'
  if (trend === 'trend-down') return isZh.value ? '收窄' : 'Falling'
  return isZh.value ? '稳定' : 'Stable'
})

// 垂直方向的迷你趋势图（用于右侧区域）
const generateSparklinePointsVertical = (type: string): string => {
  const data = sparklineData.value[type] || []
  if (data.length === 0) return '20,38 20,2'

  const points = data.map((val, i) => {
    const y = 38 - (i / (data.length - 1)) * 36 // 从下往上
    const x = 2 + val * 36 // 值越大，x越大（线越靠右）
    return `${x.toFixed(1)},${y.toFixed(1)}`
  })
  return points.join(' ')
}

// --- 通用进度条颜色计算（根据位置百分比）---
// 标准渐变：0-50%绿色, 50-75%黄色, 75-100%红色
const getProgressColor = (percent: number): string => {
  if (percent < 50) return '#26a69a'
  if (percent < 75) return '#ff9800'
  return '#f44336'
}

// --- 最大回撤专用进度条颜色 ---
// percent = abs(drawdown) * 500，阈值：5%=25%, 10%=50%
const getDrawdownProgressColor = (drawdown: number): string => {
  const percent = Math.abs(drawdown) * 500
  if (percent < 25) return '#26a69a'  // < 5%
  if (percent < 50) return '#ff9800'  // 5%-10%
  return '#f44336'                     // >= 10%
}

// Beta专用：0-50%绿色, 50-80%黄色, 80-100%红色
const getBetaProgressColor = (beta: number): string => {
  const percent = ((beta - 0.5) / 1.0) * 100
  if (percent < 50) return '#26a69a'
  if (percent < 80) return '#ff9800'
  return '#f44336'
}

// 计算填充宽度：使填充等于轨道宽度，这样渐变位置才正确
const getFillWidth = (progressPercent: number): string => {
  if (progressPercent <= 0) return '0%'
  return (10000 / progressPercent) + '%'
}

// --- 组合分析指标专用信号灯函数 ---

// 波动率：percent = volatility * 333
const getVolatilitySignalAnalysis = (volatility: number | undefined): string => {
  if (volatility === undefined || volatility === null) return ''
  const percent = volatility * 333
  if (percent < 50) return 'signal-green'
  if (percent < 75) return 'signal-yellow'
  return 'signal-red'
}

// Beta：percent = (beta - 0.5) * 100
const getBetaSignalAnalysis = (beta: number | undefined): string => {
  if (beta === undefined || beta === null) return ''
  const percent = (beta - 0.5) * 100
  if (percent < 50) return 'signal-green'
  if (percent < 80) return 'signal-yellow'
  return 'signal-red'
}

// 最大回撤：percent = abs(drawdown) * 500
const getDrawdownSignalAnalysis = (drawdown: number | undefined): string => {
  if (drawdown === undefined || drawdown === null) return ''
  const percent = Math.abs(drawdown) * 500
  if (percent < 25) return 'signal-green'
  if (percent < 50) return 'signal-yellow'
  return 'signal-red'
}

// 换手率
const getTurnoverSignal = (turnover: number): string => {
  const percent = Math.min(turnover * 200, 100)
  if (percent < 50) return 'signal-green'
  if (percent < 75) return 'signal-yellow'
  return 'signal-red'
}

const getTurnoverBaselineDir = (turnover: number): string => {
  if (turnover > 0.6) return 'up'
  if (turnover < 0.3) return 'down'
  return 'stable'
}

const getTurnoverBaselineText = (turnover: number): string => {
  if (turnover > 0.8) return isZh.value ? '高于正常区间' : 'Above normal'
  if (turnover < 0.4) return isZh.value ? '低于正常区间' : 'Below normal'
  return isZh.value ? '正常交易区间' : 'Normal range'
}

const getTurnoverTrend = computed(() => {
  const data = sparklineData.value.turnover
  if (data.length < 2) return 'trend-stable'
  const last = data.slice(-3)
  const avg = last.reduce((a, b) => a + b, 0) / last.length
  return avg > 0.5 ? 'trend-up' : avg < 0.3 ? 'trend-down' : 'trend-stable'
})

const getTurnoverTrendLabel = computed(() => {
  const trend = getTurnoverTrend.value
  if (trend === 'trend-up') return isZh.value ? '交易活跃' : 'More active'
  if (trend === 'trend-down') return isZh.value ? '交易清淡' : 'Less active'
  return isZh.value ? '保持稳定' : 'Stable'
})

// --- 年化收益 ---
const getReturnBaselineText = (ret: number): string => {
  const pct = Math.abs(ret * 100).toFixed(1)
  if (ret > 0.15) return isZh.value ? `大幅超越基准` : 'Well above base'
  if (ret > 0) return isZh.value ? `正收益 +${pct}%` : `Positive +${pct}%`
  if (ret > -0.10) return isZh.value ? `小幅亏损 ${pct}%` : `Small loss ${pct}%`
  return isZh.value ? `较大亏损` : 'Significant loss'
}

// --- 跟踪误差 ---
const getTrackingSignal = (tracking: number): string => {
  const percent = Math.min(tracking * 500, 100)
  if (percent < 50) return 'signal-green'
  if (percent < 75) return 'signal-yellow'
  return 'signal-red'
}

const getTrackingBaselineDir = (tracking: number): string => {
  if (tracking > 0.06) return 'up'
  if (tracking < 0.03) return 'down'
  return 'stable'
}

const getTrackingBaselineText = (tracking: number): string => {
  if (tracking < 0.03) return isZh.value ? '高度集中' : 'Highly focused'
  if (tracking < 0.06) return isZh.value ? '适度分散' : 'Moderate divers.'
  return isZh.value ? '过于分散' : 'Too diversified'
}

const getTrackingTrend = computed(() => {
  const data = sparklineData.value.tracking
  if (data.length < 2) return 'trend-stable'
  const last = data.slice(-3)
  const avg = last.reduce((a, b) => a + b, 0) / last.length
  return avg > 0.5 ? 'trend-up' : avg < 0.3 ? 'trend-down' : 'trend-stable'
})

const getTrackingTrendLabel = computed(() => {
  const trend = getTrackingTrend.value
  if (trend === 'trend-up') return isZh.value ? '分散度上升' : 'More diverse'
  if (trend === 'trend-down') return isZh.value ? '集中度上升' : 'More focused'
  return isZh.value ? '保持稳定' : 'Stable'
})

// 监听语言变化
watch(isZh, () => {
  renderTrendChart()
})

onMounted(() => {
  // 加载保存的图表高度
  loadSavedTrendHeight()
  // 初始化收益走势数据
  initTrendData()
  // 初始化分析指标趋势数据
  initSparklineData()
  // 使用nextTick确保DOM渲染完成后再初始化图表
  nextTick(() => {
    renderTrendChart()
  })
  // 监听窗口大小变化
  window.addEventListener('resize', handleTrendChartResize)
  window.addEventListener('resize', handleRiskTrendChartResize)
  // 初始化加载综合风险评分
  refreshRiskScore()
})

onBeforeUnmount(() => {
  if (trendChartInstance) {
    trendChartInstance.dispose()
    trendChartInstance = null
  }
  if (riskTrendChart) {
    riskTrendChart.dispose()
    riskTrendChart = null
  }
  window.removeEventListener('resize', handleTrendChartResize)
  window.removeEventListener('resize', handleRiskTrendChartResize)
})

// 窗口大小变化处理
const handleTrendChartResize = () => {
  trendChartInstance?.resize()
}
</script>

<style scoped lang="scss">
.risk-management-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-primary, #131722);
  color: var(--text-primary, #d1d4dc);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

// 子导航标签
.sub-nav {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 40px;
  background: var(--bg-secondary, #1e222d);
  border-bottom: 1px solid var(--border-color, #2a2e39);
}

.sub-nav-tabs {
  display: flex;
  gap: 4px;
}

.sub-tab {
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
}

.icon-sub {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

// 主容器
.main-container {
  height: calc(100vh - 56px - 40px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

// 响应式：限制最大宽度，保持内容居中
.main-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary, #131722);
  overflow-y: auto;
  overflow-x: hidden;
}

// 统一的内容包装器 - 确保所有section边距一致
.module-header,
.market-risk-section,
.section-divider,
.summary-cards,
.risk-score-section,
.analysis-section,
.key-metrics-row,
.position-charts,
.risk-alerts-section,
.page-header-section,
.charts-row,
.chart-section,
.three-column-grid {
  padding-left: 20px;
  padding-right: 20px;

  // 统一的上边距（module-header、key-metrics-row、market-risk-section、three-column-grid 除外）
  &:not(.module-header):not(.key-metrics-row):not(.market-risk-section):not(.three-column-grid) {
    margin-top: 16px;
  }

  @media (max-width: 1200px) {
    padding-left: 16px;
    padding-right: 16px;
  }

  @media (max-width: 768px) {
    padding-left: 12px;
    padding-right: 12px;
  }
}

// 主内容区 - 已在上面定义，这里保留注释
// .main-content 定义在 main-container 之后

.module-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 20px;
  .header-left { display: flex; align-items: center; gap: 20px; }
  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

// ===== 大盘风险监控 =====
.market-risk-section {
  padding: 16px 20px;
  background: var(--bg-primary, #131722);
  margin-bottom: 0;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);

      .section-icon {
        width: 18px;
        height: 18px;
        color: #26a69a;
      }
    }

    .market-time {
      font-size: 11px;
      color: var(--text-muted, #787b86);
    }
  }
}

// 市场情绪卡片
.sentiment-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.sentiment-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  background: var(--bg-secondary, #1e222d);
  border-radius: 8px;
  border: 1px solid var(--border-color, #2a2e39);

  .sentiment-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    svg {
      width: 16px;
      height: 16px;
    }

    &.up {
      background: rgba(244, 67, 54, 0.15);
      color: #f44336;
    }

    &.down {
      background: rgba(38, 166, 154, 0.15);
      color: #26a69a;
    }

    &.neutral {
      background: rgba(41, 98, 255, 0.15);
      color: #2962ff;
    }
  }

  .sentiment-content {
    flex: 1;
    min-width: 0;

    .sentiment-label {
      font-size: 11px;
      color: var(--text-muted, #787b86);
      margin-bottom: 4px;
    }

    .sentiment-value {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);

      .up-count { color: #f44336; }
      .down-count { color: #26a69a; }
      .separator { margin: 0 4px; color: var(--text-muted, #787b86); }

      &.positive { color: #f44336; }
      &.negative { color: #26a69a; }
    }

    .sentiment-detail {
      font-size: 11px;
      color: var(--text-muted, #787b86);
      margin-top: 2px;

      &.positive { color: #f44336; }
      &.negative { color: #26a69a; }
    }
  }
}

// 板块区域
.sector-section {
  display: grid;
  grid-template-columns: 1fr 1fr 1.2fr;
  gap: 16px;
  padding: 0 20px 16px;
}

.sector-column {
  background: var(--bg-secondary, #1e222d);
  border-radius: 8px;
  border: 1px solid var(--border-color, #2a2e39);
  overflow: hidden;

  .sector-header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 10px 12px;
    font-size: 12px;
    font-weight: 600;
    background: var(--bg-tertiary, #2a2e39);

    svg {
      width: 14px;
      height: 14px;
    }

    &.up {
      color: #f44336;
      background: rgba(244, 67, 54, 0.1);
    }

    &.down {
      color: #26a69a;
      background: rgba(38, 166, 154, 0.1);
    }

    &.highlight {
      color: #2962ff;
      background: rgba(41, 98, 255, 0.1);
    }
  }

  .sector-list {
    padding: 8px 0;
  }

  .sector-item {
    display: flex;
    align-items: center;
    padding: 6px 12px;
    font-size: 12px;
    transition: background 0.15s;

    &:hover {
      background: rgba(255, 255, 255, 0.03);
    }

    .sector-rank {
      width: 18px;
      height: 18px;
      border-radius: 4px;
      background: var(--bg-tertiary, #2a2e39);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      font-weight: 600;
      color: var(--text-muted, #787b86);
      margin-right: 8px;
    }

    .sector-name {
      flex: 1;
      color: var(--text-primary, #d1d4dc);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .sector-weight {
      font-size: 11px;
      color: var(--text-muted, #787b86);
      margin-right: 8px;
    }

    .sector-change {
      font-weight: 500;

      &.positive { color: #f44336; }
      &.negative { color: #26a69a; }
    }
  }

  .sector-summary {
    padding: 10px 12px;
    font-size: 11px;
    color: var(--text-muted, #787b86);
    border-top: 1px solid var(--border-color, #2a2e39);
    line-height: 1.5;

    .highlight-text {
      color: #2962ff;
      font-weight: 500;
    }
  }
}

// 持仓风险指标头部
.position-risk-header {
  padding: 16px 20px 8px 20px;
  background: var(--bg-primary, #131722);
  position: relative;

  // 上方短分割线
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 1px;
    background: var(--border-color, #2a2e39);
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);

      .section-icon {
        width: 18px;
        height: 18px;
        color: #26a69a;
      }
    }
  }
}

// 分隔线
.section-divider {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: var(--bg-primary, #131722);

  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border-color, #2a2e39);
  }

  span {
    padding: 0 16px;
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted, #787b86);
  }
}

.title-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.title-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  svg {
    width: 22px;
    height: 22px;
  }
  &.risk {
    background: linear-gradient(135deg, rgba(38, 166, 154, 0.2), rgba(38, 166, 154, 0.1));
    color: #26a69a;
    border: 1px solid rgba(38, 166, 154, 0.3);
  }
  &.position {
    background: linear-gradient(135deg, rgba(41, 98, 255, 0.2), rgba(41, 98, 255, 0.1));
    color: #2962ff;
    border: 1px solid rgba(41, 98, 255, 0.3);
    &.simulated {
      background: linear-gradient(135deg, rgba(156, 39, 176, 0.2), rgba(103, 58, 183, 0.1));
      color: #ce93d8;
      border-color: rgba(156, 39, 176, 0.3);
    }
  }
  &.rules {
    background: linear-gradient(135deg, rgba(247, 147, 26, 0.2), rgba(247, 147, 26, 0.1));
    color: #f7931a;
    border: 1px solid rgba(247, 147, 26, 0.3);
  }
  &.events {
    background: linear-gradient(135deg, rgba(239, 83, 80, 0.2), rgba(239, 83, 80, 0.1));
    color: #ef5350;
    border: 1px solid rgba(239, 83, 80, 0.3);
  }
}

.title-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  .page-title { font-size: 18px; font-weight: 600; margin: 0; }
  .page-subtitle { font-size: 12px; color: var(--text-secondary, #787b86); margin: 0; }
}

.btn-monitor {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px;
  background: rgba(38, 166, 154, 0.2); border: 1px solid #26a69a; border-radius: 4px;
  color: #26a69a; font-size: 12px; cursor: pointer;
  &.active { background: rgba(239, 83, 80, 0.2); border-color: #ef5350; color: #ef5350; }
}

.btn-refresh, .btn-secondary {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px;
  background: var(--bg-tertiary, #2a2e39); border: 1px solid var(--border-color, #2a2e39); border-radius: 4px;
  color: var(--text-primary, #d1d4dc); font-size: 12px; cursor: pointer;
  &:hover { border-color: var(--accent-blue, #2962ff); }
}

.btn-primary {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px;
  background: var(--accent-blue, #2962ff); border: none; border-radius: 4px;
  color: white; font-size: 12px; cursor: pointer;
  &:hover { background: #1e53e4; }
}

.spinning { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

// AI智能调参按钮
.btn-ai {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 14px;
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.2), rgba(103, 58, 183, 0.2));
  border: 1px solid rgba(156, 39, 176, 0.5);
  border-radius: 4px;
  color: #ce93d8;
  font-size: 12px; cursor: pointer;
  transition: all 0.2s;
  &:hover { background: linear-gradient(135deg, rgba(156, 39, 176, 0.3), rgba(103, 58, 183, 0.3)); border-color: #ce93d8; }
}

// 模式切换按钮
.mode-switch {
  display: flex;
  gap: 2px;
  padding: 3px;
  background: var(--bg-tertiary, #2a2e39);
  border-radius: 6px;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-secondary, #cbd5e1);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { color: var(--text-primary, #d1d4dc); }
  &.active {
    background: var(--accent-blue, #2962ff);
    color: white;
  }
}

// 模拟账户提示条
.sim-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.15), rgba(103, 58, 183, 0.1));
  border-bottom: 1px solid rgba(156, 39, 176, 0.2);
  color: #ce93d8;
  font-size: 12px;
  svg { flex-shrink: 0; }
  span { flex: 1; }
  .btn-reset {
    padding: 4px 10px;
    background: rgba(239, 83, 80, 0.2);
    border: 1px solid rgba(239, 83, 80, 0.4);
    border-radius: 4px;
    color: #ef5350;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.15s;
    &:hover { background: rgba(239, 83, 80, 0.3); }
  }
}

// 规则统计栏
.rules-stats {
  display: flex;
  gap: 24px;
  padding: 12px 20px;
  background: var(--bg-secondary, #1e222d);
  border-bottom: 1px solid var(--border-color, #2a2e39);
  .stat-item {
    display: flex;
    align-items: center;
    gap: 8px;
    .stat-label { font-size: 12px; color: var(--text-secondary, #787b86); }
    .stat-value { font-size: 16px; font-weight: 600; &.enabled { color: #26a69a; } &.warning { color: #f7931a; } }
  }
  .ai-badge {
    margin-left: auto;
    padding: 4px 10px;
    background: linear-gradient(135deg, rgba(156, 39, 176, 0.15), rgba(103, 58, 183, 0.15));
    border: 1px solid rgba(156, 39, 176, 0.3);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;
    svg { color: #ce93d8; }
    span { font-size: 11px; color: #ce93d8; }
    &:hover { background: rgba(156, 39, 176, 0.25); }
  }
}

// AI对话框
.ai-dialog {
  width: 560px;
  max-width: 90vw;
}
.icon-ai-header { width: 24px; height: 24px; color: #ce93d8; margin-right: 8px; }

.ai-analyzing {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  .ai-spinner {
    width: 48px; height: 48px;
    border: 3px solid rgba(156, 39, 176, 0.2);
    border-top-color: #ce93d8;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  p { margin-top: 16px; color: var(--text-secondary, #787b86); }
}

.ai-ready {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  .ai-icon-large {
    width: 64px; height: 64px;
    background: linear-gradient(135deg, rgba(156, 39, 176, 0.2), rgba(103, 58, 183, 0.2));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    svg { width: 32px; height: 32px; color: #ce93d8; }
  }
  p { margin: 16px 0; color: var(--text-secondary, #787b86); text-align: center; }
}

.btn-ai-analyze {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  border: none; border-radius: 6px;
  color: white; font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all 0.2s;
  &:hover { transform: scale(1.02); box-shadow: 0 4px 20px rgba(156, 39, 176, 0.4); }
}

.ai-suggestions { padding: 8px 0; }
.suggestion-card {
  padding: 16px;
  margin-bottom: 12px;
  background: var(--bg-primary, #131722);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  .suggestion-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 12px;
    .suggestion-name { font-weight: 600; }
  }
  .suggestion-change {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 8px;
    .current { color: var(--text-secondary, #787b86); }
    .arrow { width: 16px; height: 16px; color: #26a69a; }
    .suggested { color: #26a69a; font-weight: 600; }
  }
  .suggestion-reason { font-size: 12px; color: var(--text-primary, #d1d4dc); margin-bottom: 4px; }
  .suggestion-impact { font-size: 11px; color: #f7931a; }
}
.btn-apply {
  padding: 4px 12px;
  background: rgba(38, 166, 154, 0.15);
  border: 1px solid #26a69a;
  border-radius: 4px;
  color: #26a69a;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;
  &:hover { background: rgba(38, 166, 154, 0.25); }
}
.suggestion-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color, #2a2e39);
}
.btn-ai-apply-all {
  flex: 1;
  padding: 10px 20px;
  background: linear-gradient(135deg, #9c27b0, #673ab7);
  border: none; border-radius: 4px;
  color: white; font-size: 13px; cursor: pointer;
  &:hover { opacity: 0.9; }
}

// 回测按钮
.btn-link.backtest:hover { background: rgba(247, 147, 26, 0.1); color: #f7931a; }

// 回测对话框
.backtest-dialog { width: 500px; }
.icon-backtest-header { width: 24px; height: 24px; color: #f7931a; margin-right: 8px; }
.backtest-rule-info {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--bg-primary, #131722);
  border-radius: 6px;
  .rule-name { font-weight: 600; }
  .rule-type { font-size: 12px; color: var(--accent-blue, #2962ff); }
}
.backtest-ready {
  text-align: center;
  padding: 30px 20px;
  p { color: var(--text-secondary, #787b86); margin-bottom: 16px; }
}
.btn-backtest-run {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 12px 24px;
  background: #f7931a;
  border: none; border-radius: 6px;
  color: white; font-size: 14px; font-weight: 600; cursor: pointer;
  &:hover { background: #e68a00; }
}
.backtest-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  p { margin-top: 16px; color: var(--text-secondary, #787b86); }
}
.backtest-result {
  .result-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 16px;
  }
  .result-item {
    padding: 12px;
    background: var(--bg-primary, #131722);
    border-radius: 6px;
    text-align: center;
    .label { display: block; font-size: 11px; color: var(--text-secondary, #787b86); margin-bottom: 4px; }
    .value { font-size: 16px; font-weight: 600; &.success { color: #26a69a; } &.warning { color: #f7931a; } }
  }
  .result-recommendations {
    padding: 16px;
    background: var(--bg-primary, #131722);
    border-radius: 6px;
    .rec-title { font-weight: 600; margin-bottom: 8px; }
    ul { margin: 0; padding-left: 20px; li { color: var(--text-secondary, #787b86); margin: 4px 0; font-size: 13px; } }
  }
}

// 开关
.switch { position: relative; display: inline-block; width: 36px; height: 20px; input { opacity: 0; width: 0; height: 0; } }
.slider {
  position: absolute; cursor: pointer; inset: 0;
  background: var(--bg-tertiary, #2a2e39); border-radius: 10px; transition: 0.2s;
  &:before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background: white; border-radius: 50%; transition: 0.2s; }
}
input:checked + .slider { background: var(--accent-blue, #2962ff); }
input:checked + .slider:before { transform: translateX(16px); }

// 风险监控
.risk-monitor-wrapper {
  flex: 1;
  min-height: 300px;
  overflow: hidden;
}

// 仓位汇总卡片
.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 0 20px;
}

.summary-card {
  display: flex; align-items: center; gap: 12px;
  padding: 16px;
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;

  &.profit .card-value, &.profit .card-icon { color: #ef5350; }
  &.loss .card-value, &.loss .card-icon { color: #26a69a; }
}

.card-icon {
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px;
  &.blue { background: rgba(41, 98, 255, 0.15); color: #2962ff; }
  &.green { background: rgba(38, 166, 154, 0.15); color: #26a69a; }
  &.orange { background: rgba(247, 147, 26, 0.15); color: #f7931a; }
  &.up { background: rgba(239, 83, 80, 0.15); color: #ef5350; }
  &.down { background: rgba(38, 166, 154, 0.15); color: #26a69a; }
  svg { width: 20px; height: 20px; }
}

.card-content { flex: 1; }
.card-label { font-size: 12px; color: var(--text-secondary, #787b86); margin-bottom: 4px; }
.card-value { font-size: 20px; font-weight: 600; &.profit { color: #ef5350; } &.loss { color: #26a69a; } }
.card-sub { font-size: 11px; color: var(--text-secondary, #787b86); margin-top: 4px; }

// 综合风险评分区域
.risk-score-section {
  padding: 16px 20px;
  background: var(--bg-secondary, #1e222d);
  border-bottom: 1px solid var(--border-color, #2a2e39);

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .section-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-secondary, #cbd5e1);
    }

    .btn-refresh-sm {
      width: 28px;
      height: 28px;
      border-radius: 6px;
      border: 1px solid var(--border-color, #2a2e39);
      background: var(--bg-primary, #131722);
      color: var(--text-secondary, #cbd5e1);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;

      &:hover:not(:disabled) {
        border-color: var(--accent-blue, #2962ff);
        color: var(--accent-blue, #2962ff);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .spinning {
        animation: spin 1s linear infinite;
      }
    }
  }

  .score-content {
    display: flex;
    gap: 24px;
    align-items: center;

    .score-gauge {
      flex-shrink: 0;
      width: 200px;
      height: 120px;
      position: relative;

      .gauge-svg {
        width: 100%;
        height: 100%;
        display: block;
      }

      .score-display {
        position: absolute;
        bottom: 8px;
        left: 50%;
        transform: translateX(-50%);
        text-align: center;
        white-space: nowrap;

        .score-value {
          font-size: 28px;
          font-weight: 700;
        }

        .score-max {
          font-size: 14px;
          color: var(--text-secondary, #cbd5e1);
        }
      }
    }

    .score-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 12px;

      .score-level {
        font-size: 16px;
        font-weight: 600;
      }

      .score-dimensions {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;

        .dimension-item {
          .dimension-header {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            margin-bottom: 4px;

            .dimension-name {
              color: var(--text-secondary, #cbd5e1);
            }

            .dimension-score {
              color: var(--text-primary, #d1d4dc);
              font-weight: 500;
            }
          }

          .dimension-bar {
            height: 4px;
            background: var(--bg-primary, #131722);
            border-radius: 2px;
            overflow: hidden;

            .dimension-fill {
              height: 100%;
              border-radius: 2px;
              transition: width 0.3s ease;
            }
          }
        }
      }

      .top-risks {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;

        .risk-tag {
          font-size: 11px;
          padding: 2px 8px;
          background: rgba(244, 67, 54, 0.15);
          color: #f44336;
          border-radius: 4px;
        }
      }
    }
  }
}

// 组合分析指标 - 新设计
.analysis-section {
  padding: 16px;
  margin: 0 20px;
  background: var(--bg-primary, #131722);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;

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
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary, #cbd5e1);

    .section-icon {
      width: 16px;
      height: 16px;
      color: #2962ff;
      flex-shrink: 0;
    }
  }

  // 整体风险区间条
  .overall-risk-zone {
    display: flex;
    align-items: center;
    gap: 10px;

    .zone-label {
      font-size: 11px;
      color: var(--text-muted, #787b86);
    }

    .zone-bar {
      width: 120px;
      height: 8px;
      border-radius: 4px;
      display: flex;
      overflow: hidden;
      position: relative;

      .zone-segment {
        flex: 1;
        &.safe { background: #26a69a; }
        &.caution { background: #ff9800; }
        &.warning { background: #ff5722; }
        &.danger { background: #f44336; }
      }

      .zone-indicator {
        position: absolute;
        top: -4px;
        width: 4px;
        height: 16px;
        background: #fff;
        border-radius: 2px;
        box-shadow: 0 0 6px rgba(255,255,255,0.5);
        transition: left 0.5s ease;
      }
    }

    .zone-text {
      font-size: 11px;
      font-weight: 600;
      &.safe { color: #26a69a; }
      &.caution { color: #ff9800; }
      &.warning { color: #ff5722; }
      &.danger { color: #f44336; }
    }
  }
}

.analysis-cards {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.metric-card {
  background: var(--bg-secondary, #1e222d);
  border: 2px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  // 移除transition，避免hover时产生过渡效果

  // 组合分析指标卡片 - 信号灯边框效果（使用 signal-green/signal-yellow/signal-red）
  &.signal-green {
    // 低风险时不显示边框亮起效果
  }

  &.signal-yellow {
    border-color: rgba(255, 152, 0, 0.8);
    box-shadow: 0 0 12px rgba(255, 152, 0, 0.3), inset 0 0 20px rgba(255, 152, 0, 0.05);
    background: linear-gradient(135deg, rgba(255, 152, 0, 0.08) 0%, var(--bg-secondary, #1e222d) 100%);
  }

  &.signal-red {
    border-color: rgba(244, 67, 54, 0.8);
    box-shadow: 0 0 12px rgba(244, 67, 54, 0.3), inset 0 0 20px rgba(244, 67, 54, 0.05);
    background: linear-gradient(135deg, rgba(244, 67, 54, 0.08) 0%, var(--bg-secondary, #1e222d) 100%);
  }
}

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  // 信号灯
  .signal-light {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;

    // 组合分析指标 - 与进度条颜色一致
    &.signal-green, &.green { background: #26a69a; box-shadow: 0 0 8px #26a69a; animation: pulse-green 2s infinite; }
    &.signal-yellow { background: #ff9800; box-shadow: 0 0 8px #ff9800; animation: pulse-yellow 2s infinite; }
    &.signal-red, &.red { background: #f44336; box-shadow: 0 0 8px #f44336; animation: pulse-red 1.5s infinite; }
  }

  .metric-label {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary, #d1d4dc);
  }

  .metric-period {
    font-size: 9px;
    color: var(--text-muted, #787b86);
    margin-left: auto;
  }

  .metric-value {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary, #d1d4dc);

    &.profit { color: #ef5350; }
    &.loss { color: #26a69a; }
  }

  // 基准对比
  .metric-baseline {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;

    .baseline-direction {
      &.up { color: #ef5350; }
      &.down { color: #26a69a; }
    }

    .baseline-text {
      color: var(--text-muted, #787b86);
    }
  }

  // 迷你趋势图
  .metric-sparkline {
    height: 20px;
    margin-top: 4px;

    svg {
      width: 100%;
      height: 100%;
      color: var(--text-muted, #787b86);
    }
  }

  // 趋势标签
  .metric-trend {
    font-size: 9px;
    font-weight: 500;
    padding: 2px 6px;
    border-radius: 4px;
    text-align: center;

    &.trend-up {
      background: rgba(239, 83, 80, 0.15);
      color: #ef5350;
    }

    &.trend-down {
      background: rgba(38, 166, 154, 0.15);
      color: #26a69a;
    }

    &.trend-stable {
      background: rgba(120, 123, 134, 0.15);
      color: #787b86;
    }
  }

  // 新增：卡片标题（带图标）
  .card-title {
    display: flex;
    align-items: center;
    gap: 6px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color, #2a2e39);
    margin-bottom: 8px;

    .title-icon {
      width: 14px;
      height: 14px;
      color: var(--text-muted, #787b86);

      &.profit { color: #ef5350; }
      &.loss { color: #26a69a; }
    }

    span:nth-child(2) {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-primary, #d1d4dc);
    }

    .title-period {
      font-size: 9px;
      color: var(--text-muted, #787b86);
      margin-left: auto;
      background: var(--bg-tertiary, #2a2e39);
      padding: 1px 4px;
      border-radius: 3px;
    }
  }

  // 新增：卡片主体（左右分栏）
  .card-body {
    display: flex;
    gap: 10px;
    flex: 1;
    min-height: 85px;
  }

  // 新增：左侧区域（信号灯、数值、进度条、基准、趋势）
  .left-section {
    display: flex;
    flex-direction: column;
    gap: 3px;
    flex: 0 0 auto;
    width: clamp(80px, 30%, 100px);  // 弹性宽度：最小80px，最大100px
    min-width: 70px;
  }

  // 新增：右侧区域（横向迷你趋势图）- 更大更专业
  .right-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: space-between;
    min-width: 50px;
    padding-bottom: 2px;

    .sparkline-container {
      position: relative;
      width: 100%;
      flex: 1;

      .sparkline-chart {
        width: 100%;
        height: 100%;
        overflow: visible;
      }
    }

    // 指标说明 - 和左边 metric-trend 对齐，字体一致
    .metric-hint {
      font-size: 9px;
      font-weight: 500;
      color: #a0a3ac;
      text-align: right;
      white-space: nowrap;
    }
  }

  // 新增：信号灯行
  .signal-row {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  // 新增：数值进度条
  .value-progress-bar {
    margin: 2px 0;

    .progress-track {
      height: 6px;
      border-radius: 3px;
      position: relative;
      // 默认：0-50%绿色, 50-75%黄色, 75-100%红色
      background: linear-gradient(to right,
        rgba(38, 166, 154, 0.2) 0%,
        rgba(38, 166, 154, 0.2) 50%,
        rgba(255, 152, 0, 0.2) 50%,
        rgba(255, 152, 0, 0.2) 75%,
        rgba(244, 67, 54, 0.2) 75%,
        rgba(244, 67, 54, 0.2) 100%
      );

      // 裁剪容器 - 控制可见范围
      .progress-clip {
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        border-radius: 3px;
        overflow: hidden;
        z-index: 1;

        // 填充层 - 固定渐变，通过宽度补偿实现正确显示
        .progress-fill {
          position: absolute;
          top: 0;
          left: 0;
          height: 100%;
          background: linear-gradient(to right,
            #26a69a 0%,
            #26a69a 50%,
            #ff9800 50%,
            #ff9800 75%,
            #f44336 75%,
            #f44336 100%
          );
        }
      }

      // 最大回撤专用：0-25%绿色, 25-50%黄色, 50-100%紫色
      &.drawdown-track {
        background: linear-gradient(to right,
          rgba(38, 166, 154, 0.2) 0%,
          rgba(38, 166, 154, 0.2) 25%,
          rgba(255, 152, 0, 0.2) 25%,
          rgba(255, 152, 0, 0.2) 50%,
          rgba(139, 92, 246, 0.2) 50%,
          rgba(139, 92, 246, 0.2) 100%
        );
        .progress-clip .progress-fill {
          background: linear-gradient(to right,
            #26a69a 0%,
            #26a69a 25%,
            #ff9800 25%,
            #ff9800 50%,
            #8b5cf6 50%,
            #8b5cf6 100%
          );
        }
      }

      &.beta-track {
        background: linear-gradient(to right,
          rgba(38, 166, 154, 0.2) 0%,
          rgba(38, 166, 154, 0.2) 50%,
          rgba(255, 152, 0, 0.2) 50%,
          rgba(255, 152, 0, 0.2) 80%,
          rgba(244, 67, 54, 0.2) 80%,
          rgba(244, 67, 54, 0.2) 100%
        );
        .progress-clip .progress-fill {
          background: linear-gradient(to right,
            #26a69a 0%,
            #26a69a 50%,
            #ff9800 50%,
            #ff9800 80%,
            #f44336 80%,
            #f44336 100%
          );
        }
      }

      &.return-track {
        background: linear-gradient(to right,
          rgba(38, 166, 154, 0.2) 0%,
          rgba(38, 166, 154, 0.2) 45%,
          rgba(120, 123, 134, 0.15) 45%,
          rgba(120, 123, 134, 0.15) 55%,
          rgba(239, 83, 80, 0.2) 55%,
          rgba(239, 83, 80, 0.2) 100%
        );
        .progress-clip .progress-fill {
          // 年化收益使用纯色：正收益红色，负收益绿色
          background: #ef5350; // 默认红色（正收益）
        }
        // 负收益时的绿色填充
        &.negative .progress-clip .progress-fill {
          background: #26a69a;
        }
      }

      .progress-center-line {
        position: absolute;
        left: 50%;
        top: 0;
        bottom: 0;
        width: 1px;
        background: var(--text-muted, #787b86);
        opacity: 0.5;
        transform: translateX(-50%);
        z-index: 2;
      }

      // 位置指示器
      .progress-indicator {
        position: absolute;
        top: -4px;
        width: 3px;
        height: 14px;
        border-radius: 2px;
        transform: translateX(-50%);
        transition: left 0.3s ease;
        z-index: 3;
      }
    }

    .progress-markers {
      display: flex;
      justify-content: space-between;
      margin-top: 2px;

      span {
        font-size: 8px;
        color: var(--text-muted, #787b86);
      }
    }
  }

  // 基准对比样式优化
  .metric-baseline {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;

    .baseline-dir {
      &.up { color: #ef5350; }
      &.down { color: #26a69a; }
      &.stable { color: #787b86; }
    }

    span:last-child {
      color: var(--text-muted, #787b86);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

@keyframes pulse-green {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes pulse-yellow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes pulse-red {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

// 图表区域
.chart-section {
  padding: 16px;
  margin: 0 20px;
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  position: relative;
  z-index: 1;

  &.half {
    flex: 1;
    padding: 16px;
    margin: 0;
    background: var(--bg-secondary, #1e222d);
    border: 1px solid var(--border-color, #2a2e39);
    border-radius: 8px;
  }
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  .chart-icon {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(41, 98, 255, 0.15);
    color: #2962ff;
    svg { width: 14px; height: 14px; }
    &.pie { background: rgba(156, 39, 176, 0.15); color: #ce93d8; }
    &.bar { background: rgba(38, 166, 154, 0.15); color: #26a69a; }
  }
  .section-icon {
    width: 16px;
    height: 16px;
    color: #2962ff;
    flex-shrink: 0;
  }
}

.chart-legend {
  display: flex;
  gap: 16px;
  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: var(--text-secondary, #cbd5e1);
    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      &.strategy { background: #2962ff; }
      &.benchmark { background: #787b86; }
    }
  }
}

.chart-body {
  padding: 12px;
}

.echarts-chart {
  width: 100%;
  background: var(--bg-primary, #131722);
  border-radius: 8px;
  display: block;
}

// 调整高度把手
.resize-handle {
  position: absolute;
  bottom: -12px;
  left: 0;
  right: 0;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: ns-resize;
  z-index: 10;
  background: transparent;
}

.resize-line {
  width: 40px;
  height: 4px;
  background: var(--text-secondary, #787b86);
  border-radius: 2px;
  opacity: 0.3;
  transition: opacity 0.2s;
}

.resize-handle:hover .resize-line {
  opacity: 1;
  background: var(--accent-blue, #2962ff);
}

.trend-chart {
  width: 100%;
  height: 120px;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 10px;
  color: var(--text-muted, #6b6b6b);
}

// 图表行
.charts-row {
  display: flex;
  gap: 16px;
  // padding已在统一定义中，这里不重复
}

// 饼图
.pie-chart-body {
  display: flex;
  align-items: center;
  gap: 20px;
}

.pie-chart {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
  svg { width: 100%; height: 100%; }
}

.pie-legend {
  flex: 1;
  .legend-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    margin-bottom: 6px;
    .color-box {
      width: 12px;
      height: 12px;
      border-radius: 3px;
      &.blue { background: #2962ff; }
      &.green { background: #26a69a; }
      &.orange { background: #f7931a; }
      &.purple { background: #9c27b0; }
      &.gray { background: #787b86; }
    }
    .pct {
      margin-left: auto;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
    }
  }
}

// 条形图
.bar-chart-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  .bar-label {
    width: 60px;
    font-size: 11px;
    font-family: monospace;
    color: var(--accent-blue, #2962ff);
  }
  .bar-track {
    flex: 1;
    height: 8px;
    background: var(--bg-tertiary, #2a2e39);
    border-radius: 4px;
    overflow: hidden;
  }
  .bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s;
    /* 五级色系：紫/红/橙/蓝/绿 */
    &.excellent { background: linear-gradient(90deg, #9c27b0, #ba68c8); }  /* 最高 - 紫色 */
    &.good { background: linear-gradient(90deg, #ef5350, #ff8a80); }       /* 较好 - 红色 */
    &.average { background: linear-gradient(90deg, #ff9800, #ffb74d); }    /* 中等 - 橙色 */
    &.low { background: linear-gradient(90deg, #2962ff, #5c95ff); }        /* 较低 - 蓝色 */
    &.poor { background: linear-gradient(90deg, #26a69a, #5ce5a9); }       /* 亏损 - 绿色 */
  }
  .bar-value {
    width: 60px;
    font-size: 11px;
    font-weight: 600;
    text-align: right;
    /* 五级色系文字颜色 */
    &.excellent { color: #9c27b0; }  /* 最高 - 紫色 */
    &.good { color: #ef5350; }       /* 较好 - 红色 */
    &.average { color: #ff9800; }    /* 中等 - 橙色 */
    &.low { color: #2962ff; }        /* 较低 - 蓝色 */
    &.poor { color: #26a69a; }       /* 亏损 - 绿色 */
  }
}

// 持仓表格
.positions-table-wrapper {
  flex: 1;
  overflow: auto;
  padding: 0 4px 4px;
}

.positions-table {
  width: 100%;
  border-collapse: collapse;
  th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border-color, #2a2e39); }
  th { background: var(--bg-secondary, #1e222d); font-size: 11px; font-weight: 600; color: var(--text-secondary, #787b86); text-transform: uppercase; position: sticky; top: 0; }
  td { font-size: 12px; }
  .right { text-align: right; }
  .code { color: var(--accent-blue, #2962ff); font-family: monospace; }
  .profit { color: #ef5350; }
  .loss { color: #26a69a; }
}

.status-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  &.normal { background: rgba(38, 166, 154, 0.2); color: #26a69a; }
  &.suspended { background: rgba(247, 147, 26, 0.2); color: #f7931a; }
  &.risk_limit { background: rgba(239, 83, 80, 0.2); color: #ef5350; }
}

// 规则卡片网格
.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  padding: 20px;
}

.rule-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  overflow: hidden;
  .rule-card-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border-color, #2a2e39); }
  .rule-card-name { font-size: 14px; font-weight: 600; }
  .rule-card-body { padding: 12px 16px; }
  .rule-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
  .rule-type-tag { font-size: 11px; color: var(--accent-blue, #2962ff); background: rgba(41, 98, 255, 0.15); padding: 2px 8px; border-radius: 4px; }
  .rule-id { font-size: 10px; color: var(--text-muted, #6b6b6b); font-family: monospace; }
  .rule-params { display: flex; flex-direction: column; gap: 4px; }
  .param-item { font-size: 12px; .param-key { color: var(--text-secondary, #787b86); } .param-value { color: var(--text-primary, #d1d4dc); margin-left: 4px; } }
  .rule-card-footer { display: flex; gap: 12px; padding: 8px 16px; border-top: 1px solid var(--border-color, #2a2e39); background: var(--bg-primary, #131722); }
}

.btn-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: none; border: none;
  color: var(--text-secondary, #cbd5e1);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
  &:hover { background: rgba(255,255,255,0.05); color: var(--accent-blue, #2962ff); }
  &.danger:hover { background: rgba(239, 83, 80, 0.1); color: #ef5350; }
}

// 事件时间线
.events-timeline {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.event-item {
  display: flex;
  gap: 12px;
  &.error .marker-dot { background: #ef5350; }
  &.warning .marker-dot { background: #f7931a; }
  &.info .marker-dot { background: #2962ff; }
}

.event-marker {
  display: flex; flex-direction: column; align-items: center;
  .marker-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
  .marker-line { flex: 1; width: 2px; background: var(--border-color, #2a2e39); margin-top: 4px; }
}

.event-card {
  flex: 1;
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 6px;
  padding: 12px;
  .event-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
  .event-level { font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 3px; background: var(--bg-tertiary, #2a2e39); }
  .event-time { font-size: 11px; color: var(--text-muted, #6b6b6b); }
  .event-message { font-size: 13px; font-weight: 500; margin-bottom: 4px; }
  .event-details { font-size: 12px; color: var(--text-secondary, #787b86); }
}

.empty-state { text-align: center; padding: 40px; color: var(--text-secondary, #787b86); font-size: 13px; }

// 对话框
.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: var(--bg-secondary, #1e222d); border: 1px solid var(--border-color, #2a2e39); border-radius: 8px; width: 480px; max-width: 90vw;
  .dialog-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--border-color, #2a2e39); h3 { margin: 0; font-size: 16px; display: flex; align-items: center; gap: 8px; } }
  .btn-close { width: 28px; height: 28px; background: transparent; border: none; cursor: pointer; color: var(--text-secondary, #787b86); svg { width: 18px; height: 18px; } &:hover { color: var(--text-primary, #d1d4dc); } }
  .dialog-body { padding: 20px; max-height: 60vh; overflow-y: auto; }
  .dialog-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 20px; border-top: 1px solid var(--border-color, #2a2e39); }
}

// 页面内压力测试面板（精简版）
.stress-test-panel {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 12px;
  margin: 16px 24px;
  padding: 16px;

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      margin: 0;
    }

    .test-time {
      font-size: 11px;
      color: var(--text-muted, #787b86);
    }
  }

  .stress-scenarios-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 8px;

    @media (max-width: 1200px) {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  .scenario-mini-card {
    background: var(--bg-tertiary, #2a2e39);
    border-radius: 6px;
    padding: 10px;
    text-align: center;
    border-top: 3px solid var(--text-muted, #787b86);
    position: relative;
    transition: all 0.3s ease;

    &.low { border-top-color: #26a69a; }
    &.medium { border-top-color: #ff9800; }
    &.high { border-top-color: #ef5350; }
    &.critical { border-top-color: #9c27b0; }

    // 当前状态高亮 - 按风险级别使用不同颜色和频率
    &.current {
      &.low, &.risk-low {
        animation: pulse-glow-low 5s ease-in-out infinite;
        &::before { border-top-color: #26a69a; }
        .current-indicator { color: #26a69a; background: rgba(38, 166, 154, 0.2); }
      }
      &.medium, &.risk-medium {
        animation: pulse-glow-medium 4s ease-in-out infinite;
        &::before { border-top-color: #ff9800; }
        .current-indicator { color: #ff9800; background: rgba(255, 152, 0, 0.2); }
      }
      &.high, &.risk-high {
        animation: pulse-glow-high 3s ease-in-out infinite;
        &::before { border-top-color: #ef5350; }
        .current-indicator { color: #ef5350; background: rgba(239, 83, 80, 0.2); }
      }
      &.critical, &.risk-critical {
        animation: pulse-glow-critical 2s ease-in-out infinite;
        &::before { border-top-color: #9c27b0; }
        .current-indicator { color: #9c27b0; background: rgba(156, 39, 176, 0.2); }
      }

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%) translateY(-100%);
        width: 0;
        height: 0;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-top: 10px solid #ff9800;
      }
    }

    .current-indicator {
      position: absolute;
      top: 4px;
      right: 4px;
      display: flex;
      align-items: center;
      gap: 2px;
      font-size: 9px;
      padding: 2px 4px;
      border-radius: 3px;
      animation: pulse-text 4s ease-in-out infinite;

      svg {
        width: 10px;
        height: 10px;
      }
    }

    .scenario-name {
      font-size: 11px;
      color: var(--text-secondary, #cbd5e1);
      margin-bottom: 6px;
    }

    .scenario-loss {
      font-size: 14px;
      font-weight: 700;
      &.loss { color: #26a69a; }
      &.profit { color: #ef5350; }
    }

    .scenario-pct {
      font-size: 10px;
      color: var(--text-muted, #787b86);
      margin-top: 2px;
    }
  }

  .stress-summary-row {
    display: flex;
    gap: 12px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-color, #2a2e39);

    .summary-badge {
      font-size: 12px;
      padding: 4px 10px;
      border-radius: 4px;
      background: var(--bg-tertiary, #2a2e39);

      &.worst {
        color: #ff9800;
      }

      &.max-loss {
        color: #ef5350;
      }
    }
  }
}

// 压力测试对话框
.stress-test-dialog {
  width: 700px;
  max-width: 95vw;

  .dialog-header {
    .test-time {
      font-size: 12px;
      color: var(--text-muted, #787b86);
      margin-left: auto;
      margin-right: 12px;
    }
  }
}

// 压力测试场景卡片
.stress-scenarios {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;

  .scenario-card {
    background: var(--bg-tertiary, #2a2e39);
    border-radius: 8px;
    padding: 12px;
    border-left: 3px solid var(--text-muted, #787b86);

    &.low { border-left-color: #26a69a; }
    &.medium { border-left-color: #ff9800; }
    &.high { border-left-color: #ef5350; }
    &.critical { border-left-color: #9c27b0; }

    .scenario-name {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      margin-bottom: 8px;
    }

    .scenario-impact {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .impact-value {
        font-size: 16px;
        font-weight: 700;
        &.loss { color: #26a69a; }
        &.profit { color: #ef5350; }
      }
      .impact-pct {
        font-size: 12px;
        color: var(--text-muted, #787b86);
        &.loss { color: #26a69a; }
        &.profit { color: #ef5350; }
      }
    }

    .scenario-level {
      margin-top: 8px;
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 4px;
      display: inline-block;

      &.low { background: rgba(38, 166, 154, 0.2); color: #26a69a; }
      &.medium { background: rgba(255, 152, 0, 0.2); color: #ff9800; }
      &.high { background: rgba(239, 83, 80, 0.2); color: #ef5350; }
      &.critical { background: rgba(156, 39, 176, 0.2); color: #9c27b0; }
    }
  }
}

.stress-summary {
  background: var(--bg-tertiary, #2a2e39);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;

  .summary-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-color, #2a2e39);

    &:last-child { border-bottom: none; }

    .label { color: var(--text-secondary, #cbd5e1); font-size: 13px; }
    .value { font-weight: 600; font-size: 14px;
      &.danger { color: #ef5350; }
    }
  }
}

.stress-recommendations {
  h4 {
    font-size: 14px;
    color: var(--text-primary, #d1d4dc);
    margin: 0 0 10px 0;
  }
  ul {
    margin: 0;
    padding-left: 20px;
    li {
      color: var(--text-secondary, #cbd5e1);
      font-size: 13px;
      margin-bottom: 6px;
      line-height: 1.5;
    }
  }
}

.form-group { margin-bottom: 16px;
  label { display: block; font-size: 12px; font-weight: 600; color: var(--text-secondary, #787b86); margin-bottom: 6px; }
  input, select, textarea { width: 100%; padding: 10px 12px; background: var(--bg-tertiary, #2a2e39); border: 1px solid var(--border-color, #2a2e39); border-radius: 4px; color: var(--text-primary, #d1d4dc); font-size: 13px; &:focus { outline: none; border-color: var(--accent-blue, #2962ff); } }
  textarea { font-family: monospace; }
  .checkbox-label { display: flex; align-items: center; gap: 8px; cursor: pointer; input { width: auto; accent-color: var(--accent-blue, #2962ff); } }
}

// ========== 高级风险分析模块样式 ==========
.title-icon.analysis {
  background: linear-gradient(135deg, rgba(156, 39, 176, 0.2), rgba(103, 58, 183, 0.1));
  color: #9c27b0;
  border: 1px solid rgba(156, 39, 176, 0.3);
}

.analysis-overview {
  display: grid;
  grid-template-columns: 1.5fr repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.overview-card {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 20px;

  .card-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary, #cbd5e1);
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .card-metric {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary, #d1d4dc);
    margin-bottom: 4px;

    &.warning { color: #f7931a; }
    &.danger { color: #ef5350; }
  }

  .card-desc {
    font-size: 11px;
    color: var(--text-muted, #6b6b6b);
  }
}

.risk-gauge {
  .gauge-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px 0;
  }

  .gauge-value {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 4px;

    &.low { color: #26a69a; }
    &.medium { color: #f7931a; }
    &.high {
      color: #ef5350;
      animation: pulse-text 1.5s ease-in-out infinite;
    }
    &.critical {
      color: #e91e63;
      animation: pulse-text 1s ease-in-out infinite;
    }
  }

  .gauge-label {
    font-size: 12px;
    color: var(--text-secondary, #cbd5e1);
    margin-bottom: 12px;
  }

  .gauge-bar {
    width: 100%;
    height: 8px;
    background: var(--bg-tertiary, #2a2e39);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
  }

  .gauge-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;

    &.low { background: linear-gradient(90deg, #26a69a, #4caf50); }
    &.medium { background: linear-gradient(90deg, #f7931a, #ffb300); }
    &.high { background: linear-gradient(90deg, #8b5cf6, #9c27b0); }
    &.critical { background: linear-gradient(90deg, #ef5350, #c2185b); }
  }

  .gauge-scale {
    display: flex;
    justify-content: space-between;
    width: 100%;
    font-size: 10px;
    color: var(--text-muted, #6b6b6b);
  }
}

.stress-test-section {
  background: var(--bg-card, #1e222d);
  border-radius: 12px;
  padding: 20px;
  margin-top: 16px;
  border: 1px solid var(--border-color, #2a2e39);

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      margin: 0;

      .icon-sm {
        width: 20px;
        height: 20px;
        color: var(--color-warning, #ff9800);
      }
    }

    .test-time {
      font-size: 12px;
      color: var(--text-muted, #787b86);
    }
  }
}

.analysis-sections {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
}

.analysis-section {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 16px;
  margin: 0 20px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      margin: 0;
    }

    .test-time {
      font-size: 11px;
      color: var(--text-muted, #6b6b6b);
    }
  }
}

.confidence-selector {
  display: flex;
  gap: 8px;

  .conf-btn {
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
    background: var(--bg-tertiary, #2a2e39);
    border: 1px solid var(--border-color, #2a2e39);
    border-radius: 4px;
    color: var(--text-secondary, #cbd5e1);
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      border-color: var(--accent-blue, #2962ff);
    }

    &.active {
      background: var(--accent-blue, #2962ff);
      border-color: var(--accent-blue, #2962ff);
      color: white;
    }
  }
}

.var-chart {
  .var-bars {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
  }

  .var-bar-item {
    display: grid;
    grid-template-columns: 60px 1fr 80px;
    align-items: center;
    gap: 12px;

    .bar-label {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary, #cbd5e1);
    }

    .bar-track {
      height: 24px;
      background: var(--bg-tertiary, #2a2e39);
      border-radius: 4px;
      overflow: hidden;
    }

    .bar-fill {
      height: 100%;
      border-radius: 4px;
      transition: width 0.5s ease;

      &.var { background: linear-gradient(90deg, #2962ff, #42a5f5); }
      &.cvar { background: linear-gradient(90deg, #7b1fa2, #ab47bc); }
    }

    .bar-value {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      text-align: right;
    }
  }

  .var-interpretation {
    display: flex;
    gap: 12px;
    padding: 12px;
    background: var(--bg-tertiary, #2a2e39);
    border-radius: 6px;

    .interp-icon {
      svg {
        width: 20px;
        height: 20px;
        color: var(--accent-blue, #2962ff);
      }
    }

    .interp-text {
      font-size: 12px;
      color: var(--text-secondary, #cbd5e1);
      line-height: 1.5;
    }
  }
}

.factor-exposures {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.factor-item {
  display: grid;
  grid-template-columns: 100px 1fr 60px 60px;
  align-items: center;
  gap: 12px;

  .factor-name {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary, #cbd5e1);
  }

  .factor-bar-container {
    display: flex;
    align-items: center;
    height: 20px;
  }

  .factor-bar {
    flex: 1;
    height: 8px;
    background: var(--bg-tertiary, #2a2e39);

    &.negative {
      border-radius: 4px 0 0 4px;
      .bar-fill {
        float: right;
        background: linear-gradient(90deg, #26a69a, #4caf50);
        height: 100%;
        border-radius: 4px 0 0 4px;
      }
    }

    &.positive {
      border-radius: 0 4px 4px 0;
      .bar-fill {
        background: linear-gradient(90deg, #ef5350, #f44336);
        height: 100%;
        border-radius: 0 4px 4px 0;
      }
    }
  }

  .factor-center {
    width: 2px;
    height: 16px;
    background: var(--text-muted, #6b6b6b);
  }

  .factor-value {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary, #d1d4dc);
    text-align: right;

    &.warning { color: #f7931a; }
  }

  .factor-limit {
    font-size: 10px;
    color: var(--text-muted, #6b6b6b);
    text-align: right;
  }
}

.factor-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color, #2a2e39);

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: var(--text-secondary, #cbd5e1);
  }

  .legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 2px;

    &.positive { background: #ef5350; }
    &.negative { background: #26a69a; }
  }
}

.stress-scenarios {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.scenario-card {
  background: var(--bg-tertiary, #2a2e39);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 6px;
  padding: 12px;
  text-align: center;

  &.low { border-left: 3px solid #26a69a; }
  &.medium { border-left: 3px solid #f7931a; }
  &.high { border-left: 3px solid #ef5350; }
  &.critical { border-left: 3px solid #e91e63; }

  .scenario-name {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary, #d1d4dc);
    margin-bottom: 8px;
  }

  .scenario-impact {
    margin-bottom: 8px;

    .impact-value {
      font-size: 16px;
      font-weight: 700;
      color: #ef5350;
    }

    .impact-pct {
      font-size: 11px;
      color: var(--text-secondary, #cbd5e1);
    }
  }

  .scenario-level {
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 10px;

    &.low { background: rgba(38, 166, 154, 0.2); color: #26a69a; }
    &.medium { background: rgba(247, 147, 26, 0.2); color: #f7931a; }
    &.high { background: rgba(239, 83, 80, 0.2); color: #ef5350; }
    &.critical { background: rgba(233, 30, 99, 0.2); color: #e91e63; }
  }
}

.stress-summary {
  display: flex;
  gap: 24px;
  padding: 12px;
  background: var(--bg-tertiary, #2a2e39);
  border-radius: 6px;
  margin-bottom: 16px;

  .summary-item {
    display: flex;
    flex-direction: column;
    gap: 4px;

    .label {
      font-size: 11px;
      color: var(--text-secondary, #cbd5e1);
    }

    .value {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);

      &.danger { color: #ef5350; }
    }
  }
}

.stress-recommendations {
  h4 {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary, #cbd5e1);
    margin: 0 0 8px 0;
  }

  ul {
    margin: 0;
    padding-left: 20px;

    li {
      font-size: 12px;
      color: var(--text-secondary, #cbd5e1);
      margin-bottom: 4px;
      line-height: 1.4;
    }
  }
}

.analysis-recommendations {
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  padding: 20px;

  h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary, #d1d4dc);
    margin: 0 0 12px 0;
  }

  .recommendations-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .recommendation-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px;
    background: var(--bg-tertiary, #2a2e39);
    border-radius: 6px;

    .rec-icon {
      flex-shrink: 0;
      svg {
        width: 16px;
        height: 16px;
        color: #26a69a;
      }
    }

    .rec-text {
      font-size: 12px;
      color: var(--text-secondary, #cbd5e1);
      line-height: 1.4;
    }
  }
}

// ===== 统一响应式布局 =====
// 所有grid在同一断点统一调整，确保整体协调

// 大屏幕 (1200-1399px)
@media (max-width: 1399px) {
  .analysis-cards { grid-template-columns: repeat(3, 1fr); }
  .sentiment-cards { grid-template-columns: repeat(4, 1fr); }
  .sector-section { grid-template-columns: 1fr 1fr 1.2fr; }
}

// 中屏幕 (900-1199px)
@media (max-width: 1199px) {
  .summary-cards { grid-template-columns: repeat(2, 1fr); }
  .analysis-cards { grid-template-columns: repeat(3, 1fr); }
  .sentiment-cards { grid-template-columns: repeat(2, 1fr); }
  .sector-section { grid-template-columns: 1fr 1fr; }
  .analysis-grid { grid-template-columns: repeat(3, 1fr); }
}

// 小屏幕 (600-899px)
@media (max-width: 899px) {
  .summary-cards { grid-template-columns: repeat(2, 1fr); }
  .analysis-cards { grid-template-columns: repeat(2, 1fr); }
  .sentiment-cards { grid-template-columns: repeat(2, 1fr); }
  .sector-section { grid-template-columns: 1fr; }
  .analysis-grid { grid-template-columns: repeat(2, 1fr); }
}

// 超小屏幕 (<600px)
@media (max-width: 599px) {
  .summary-cards { grid-template-columns: 1fr; }
  .analysis-cards { grid-template-columns: 1fr; }
  .sentiment-cards { grid-template-columns: repeat(2, 1fr); }
  .sector-section { grid-template-columns: 1fr; }
  .analysis-grid { grid-template-columns: 1fr; }
  .sub-nav-tabs { flex-wrap: wrap; }
}

// 评分视图切换按钮
.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-toggle {
  padding: 4px 10px;
  background: transparent;
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 4px;
  color: var(--text-secondary, #787b86);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    background: var(--bg-tertiary, #2a2e39);
  }

  &.active {
    background: var(--accent-blue, #2962ff);
    border-color: var(--accent-blue, #2962ff);
    color: white;
  }
}

// 趋势图内容
.trend-content {
  padding: 16px;
  display: flex;
  gap: 16px;

  .trend-chart {
    flex: 1;
    height: 160px;
    min-width: 300px;
  }

  .trend-stats {
    width: 120px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .trend-stat-item {
    display: flex;
    flex-direction: column;
    gap: 4px;

    .stat-label {
      font-size: 10px;
      color: var(--text-muted, #787b86);
      text-transform: uppercase;
    }

    .stat-value {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      display: flex;
      align-items: center;
      gap: 4px;

      &.up { color: #ef5350; }
      &.down { color: #26a69a; }
      &.stable { color: var(--text-secondary, #787b86); }

      svg {
        width: 14px;
        height: 14px;
      }
    }
  }
}

// 风险预警区域
.risk-alerts-section {
  padding: 16px 20px;
  background: var(--bg-secondary, #1e222d);
  border-bottom: 1px solid var(--border-color, #2a2e39);

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);

      svg {
        width: 16px;
        height: 16px;
        color: #f7931a;
      }

      .alert-count {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 18px;
        height: 18px;
        padding: 0 5px;
        background: #f44336;
        border-radius: 9px;
        font-size: 10px;
        font-weight: 600;
        color: white;
      }
    }
  }

  .alerts-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .alert-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    background: var(--bg-primary, #131722);
    border-radius: 8px;
    border-left: 3px solid;

    &.critical {
      border-left-color: #f44336;
      .alert-icon svg { color: #f44336; }
    }

    &.warning {
      border-left-color: #ff9800;
      .alert-icon svg { color: #ff9800; }
    }

    &.info {
      border-left-color: #2962ff;
      .alert-icon svg { color: #2962ff; }
    }

    .alert-icon {
      flex-shrink: 0;
      svg {
        width: 20px;
        height: 20px;
      }
    }

    .alert-content {
      flex: 1;
      min-width: 0;

      .alert-title {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary, #d1d4dc);
        margin-bottom: 4px;
      }

      .alert-description {
        font-size: 12px;
        color: var(--text-secondary, #787b86);
        line-height: 1.4;
        margin-bottom: 4px;
      }

      .alert-time {
        font-size: 10px;
        color: var(--text-muted, #787b86);
      }
    }

    .alert-actions {
      display: flex;
      gap: 4px;
      flex-shrink: 0;

      .btn-alert-action,
      .btn-alert-dismiss {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: transparent;
        border: 1px solid var(--border-color, #2a2e39);
        border-radius: 4px;
        color: var(--text-secondary, #787b86);
        cursor: pointer;
        transition: all 0.15s;

        &:hover {
          background: var(--bg-tertiary, #2a2e39);
          color: var(--text-primary, #d1d4dc);
        }

        svg {
          width: 14px;
          height: 14px;
        }
      }

      .btn-alert-dismiss:hover {
        border-color: #f44336;
        color: #f44336;
      }
    }
  }
}

.btn-dismiss-all {
  padding: 4px 8px;
  background: transparent;
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 4px;
  color: var(--text-secondary, #787b86);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    background: var(--bg-tertiary, #2a2e39);
    color: var(--text-primary, #d1d4dc);
  }
}

// ===== 新的风险监控页面样式 =====

// 页面头部区域
.page-header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 20px;
  background: var(--bg-secondary, #1e222d);
  border-bottom: 1px solid var(--border-color, #2a2e39);

  .header-left {
    .page-title {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 20px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      margin: 0;

      i {
        color: var(--accent-blue, #2962ff);
      }
    }

    .page-subtitle {
      font-size: 13px;
      color: var(--text-secondary, #787b86);
      margin-top: 4px;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
  }
}

// 核心指标卡片行
.key-metrics-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  padding: 0 20px 16px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary, #1e222d);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 8px;
  // 移除hover效果，避免用户误以为可以点击

  // 信号灯边框效果 - 持仓风险指标使用（与数值颜色一致：low/medium/high/critical）
  &.signal-green {
    // 低风险时不显示边框亮起效果
  }

  &.low {
    // 低风险时不显示边框亮起效果
  }

  &.signal-yellow, &.medium {
    border-color: rgba(255, 152, 0, 0.8);
    box-shadow: 0 0 12px rgba(255, 152, 0, 0.3), inset 0 0 20px rgba(255, 152, 0, 0.05);
    background: linear-gradient(135deg, rgba(255, 152, 0, 0.08) 0%, var(--bg-secondary, #1e222d) 100%);
  }

  &.signal-red, &.high, &.critical {
    border-color: rgba(244, 67, 54, 0.8);
    box-shadow: 0 0 12px rgba(244, 67, 54, 0.3), inset 0 0 20px rgba(244, 67, 54, 0.05);
    background: linear-gradient(135deg, rgba(244, 67, 54, 0.08) 0%, var(--bg-secondary, #1e222d) 100%);
  }

  .metric-icon {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    flex-shrink: 0;

    &.cvar { background: rgba(41, 98, 255, 0.15); svg { color: #2962ff; } }
    &.drawdown { background: rgba(38, 166, 154, 0.15); svg { color: #26a69a; } }
    &.beta { background: rgba(255, 152, 0, 0.15); svg { color: #ff9800; } }
    &.volatility { background: rgba(156, 39, 176, 0.15); svg { color: #9c27b0; } }

    svg {
      width: 22px;
      height: 22px;
    }
  }

  .metric-content {
    flex: 1;
    min-width: 0;

    .metric-label {
      font-size: 11px;
      color: var(--text-muted, #787b86);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .metric-value {
      font-size: 20px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      margin: 2px 0;

      &.critical { color: #f44336; }
      &.warning { color: #ff9800; }
      &.normal { color: #26a69a; }
      &.negative { color: #26a69a; }
    }

    .metric-desc {
      font-size: 10px;
      color: var(--text-muted, #787b86);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}

// 仪表盘卡片样式
.gauge-card {
  flex-direction: column;
  align-items: stretch;
  padding: 14px !important;

  .gauge-icon {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    margin-bottom: 8px;
    position: relative;

    // 持仓风险指标信号灯 - 与数值颜色一致
    .signal-light {
      position: absolute;
      top: -2px;
      right: -2px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      z-index: 10;

      &.low { background: #26a69a; box-shadow: 0 0 6px #26a69a; }
      &.medium { background: #ff9800; box-shadow: 0 0 6px #ff9800; }
      &.high { background: #8b5cf6; box-shadow: 0 0 6px #8b5cf6; }
      &.critical { background: #9c27b0; box-shadow: 0 0 6px #9c27b0; }
    }

    svg {
      width: 16px;
      height: 16px;
    }

    &.var-icon { background: rgba(41, 98, 255, 0.15); svg { color: #2962ff; } }
    &.cvar-icon { background: rgba(239, 83, 80, 0.15); svg { color: #ef5350; } }
    &.drawdown-icon { background: rgba(38, 166, 154, 0.15); svg { color: #26a69a; } }
    &.beta-icon { background: rgba(255, 152, 0, 0.15); svg { color: #ff9800; } }
    &.volatility-icon { background: rgba(156, 39, 176, 0.15); svg { color: #9c27b0; } }
  }

  .mini-gauge {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;

    .gauge-value {
      font-size: 22px;
      font-weight: 700;
      margin-bottom: 2px;

      &.low { color: #26a69a; }
      &.medium { color: #8bc34a; }
      &.high { color: #ff9800; }
      &.critical { color: #f44336; }
    }

    .gauge-label {
      font-size: 10px;
      color: var(--text-muted, #787b86);
      margin-bottom: 6px;
    }

    .gauge-bar {
      width: 100%;
      height: 6px;
      background: var(--bg-tertiary, #2a2e39);
      border-radius: 3px;
      overflow: hidden;
      margin-bottom: 4px;

      .gauge-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease;

        &.low { background: linear-gradient(90deg, #26a69a, #4caf50); }
        &.medium { background: linear-gradient(90deg, #8bc34a, #cddc39); }
        &.high { background: linear-gradient(90deg, #ff9800, #ffb300); }
        &.critical { background: linear-gradient(90deg, #f44336, #ff5722); }
      }
    }

    .gauge-scale {
      display: flex;
      justify-content: space-between;
      width: 100%;
      font-size: 9px;
      color: var(--text-muted, #787b86);

      span:nth-child(1) { color: #26a69a; }
      span:nth-child(2) { color: #8bc34a; }
      span:nth-child(3) { color: #ff9800; }
      span:nth-child(4) { color: #8b5cf6; }
    }
  }
}

// 增强型仪表盘卡片样式
.gauge-card.enhanced {
  padding: 12px !important;
  gap: 8px;

  .gauge-header {
    display: flex;
    align-items: flex-start;
    gap: 8px;

    .gauge-icon {
      position: relative;
      width: 28px;
      height: 28px;
      min-width: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 6px;
      margin-bottom: 0;

      svg {
        width: 16px;
        height: 16px;
      }

      .signal-light {
        position: absolute;
        top: -3px;
        left: -3px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        border: 1px solid var(--bg-primary, #1e222d);

        &.signal-green { background: #26a69a; box-shadow: 0 0 4px rgba(38, 166, 154, 0.5); }
        &.signal-yellow { background: #ff9800; box-shadow: 0 0 4px rgba(255, 152, 0, 0.5); }
        &.signal-red { background: #f44336; box-shadow: 0 0 4px rgba(244, 67, 54, 0.5); }
      }

      &.var-icon { background: rgba(41, 98, 255, 0.15); svg { color: #2962ff; } }
      &.cvar-icon { background: rgba(239, 83, 80, 0.15); svg { color: #ef5350; } }
      &.drawdown-icon { background: rgba(38, 166, 154, 0.15); svg { color: #26a69a; } }
      &.beta-icon { background: rgba(255, 152, 0, 0.15); svg { color: #ff9800; } }
      &.volatility-icon { background: rgba(156, 39, 176, 0.15); svg { color: #9c27b0; } }
    }

    .gauge-title-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex: 1;
      min-width: 0;

      .gauge-title {
        font-size: 11px;
        font-weight: 500;
        color: var(--text-secondary, #d1d4dc);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .metric-hint {
        font-size: 9px;
        color: var(--text-muted, #787b86);
        white-space: nowrap;
        margin-left: 4px;
      }
    }
  }

  .gauge-main {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 6px;

    .gauge-value-row {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;

      .gauge-value {
        font-size: 36px;
        font-weight: 700;
        line-height: 1.2;
        margin-right: 30px;

        &.low { color: #26a69a; }
        &.medium { color: #8bc34a; }
        &.high { color: #ff9800; }
        &.critical { color: #f44336; }
      }

      .gauge-sparkline-mini {
        display: flex;
        align-items: center;
        flex: 1;
        justify-content: flex-end;

        .sparkline-chart-mini {
          width: 180px;
          height: 70px;
        }

        .sparkline-avg-line {
          stroke: #b0b3bc;
        }

        .sparkline-endpoint {
          fill: var(--text-secondary, #d1d4dc);
        }
      }
    }

    .gauge-bar-wrapper {
      width: 100%;

      .gauge-bar {
        width: 100%;
        height: 5px;
        background: var(--bg-tertiary, #2a2e39);
        border-radius: 2.5px;
        overflow: hidden;
        margin-bottom: 3px;

        .gauge-fill {
          height: 100%;
          border-radius: 2.5px;
          transition: width 0.5s ease;

          &.low { background: linear-gradient(90deg, #26a69a, #4caf50); }
          &.medium { background: linear-gradient(90deg, #8bc34a, #cddc39); }
          &.high { background: linear-gradient(90deg, #ff9800, #ffb300); }
          &.critical { background: linear-gradient(90deg, #f44336, #ff5722); }
        }
      }

      .gauge-scale {
        display: flex;
        justify-content: space-between;
        width: 100%;
        font-size: 8px;
        color: var(--text-muted, #787b86);

        span:nth-child(1) { color: #26a69a; }
        span:nth-child(2) { color: #8bc34a; }
        span:nth-child(3) { color: #ff9800; }
        span:nth-child(4) { color: #8b5cf6; }
      }
    }
  }

  .gauge-status {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0;
    border-top: 1px solid var(--border-color, #363a45);
    margin-top: 2px;

    .metric-baseline {
      display: flex;
      align-items: center;
      gap: 3px;
      font-size: 10px;
      color: var(--text-muted, #787b86);

      .baseline-dir {
        font-size: 8px;

        &.up { color: #f44336; }
        &.down { color: #26a69a; }
        &.stable { color: var(--text-muted, #787b86); }
      }
    }

    .metric-trend {
      font-size: 9px;
      padding: 2px 6px;
      border-radius: 8px;
      font-weight: 500;

      &.trend-stable {
        background: rgba(120, 123, 134, 0.2);
        color: var(--text-muted, #787b86);
      }
      &.trend-up {
        background: rgba(244, 67, 54, 0.15);
        color: #f44336;
      }
      &.trend-down {
        background: rgba(38, 166, 154, 0.15);
        color: #26a69a;
      }
    }
  }

  .gauge-sparkline {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding-top: 4px;
    border-top: 1px solid var(--border-color, #363a45);

    .sparkline-chart-mini {
      width: 60px;
      height: 24px;
    }

    .sparkline-ref-line {
      stroke: var(--text-muted, #787b86);
    }

    .sparkline-endpoint {
      fill: var(--text-secondary, #d1d4dc);
    }

    .metric-hint {
      font-size: 8px;
      color: var(--text-muted, #787b86);
      text-align: center;
    }
  }
}

// VaR 仪表盘卡片（旧样式，保留兼容）
.var-gauge-card {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px !important;

  .var-gauge {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;

    .gauge-value {
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 2px;

      &.low { color: #26a69a; }
      &.medium { color: #8bc34a; }
      &.high { color: #ff9800; }
      &.critical { color: #f44336; }
    }

    .gauge-label {
      font-size: 11px;
      color: var(--text-muted, #787b86);
      margin-bottom: 8px;
    }

    .gauge-bar {
      width: 100%;
      height: 8px;
      background: var(--bg-tertiary, #2a2e39);
      border-radius: 4px;
      overflow: hidden;
      margin-bottom: 6px;

      .gauge-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;

        &.low { background: linear-gradient(90deg, #26a69a, #4caf50); }
        &.medium { background: linear-gradient(90deg, #8bc34a, #cddc39); }
        &.high { background: linear-gradient(90deg, #ff9800, #ffb300); }
        &.critical { background: linear-gradient(90deg, #f44336, #ff5722); }
      }
    }

    .gauge-scale {
      display: flex;
      justify-content: space-between;
      width: 100%;
      font-size: 10px;
      color: var(--text-muted, #787b86);

      span:nth-child(1) { color: #26a69a; }
      span:nth-child(2) { color: #8bc34a; }
      span:nth-child(3) { color: #ff9800; }
      span:nth-child(4) { color: #8b5cf6; }
    }
  }
}

// 主内容区网格布局
.main-content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 16px 24px;
}

// 评分面板
.score-panel {
  background: var(--bg-secondary, #1e222d);
  border-radius: 8px;
  overflow: visible;
  min-width: 0;

  // 移除header分段感，使用统一样式
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 16px 10px;
    // 无背景色区分，无底部边框
  }

  .panel-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary, #d1d4dc);

    svg { color: #26a69a; }
  }

  .panel-actions {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .score-content {
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;

    .score-gauge {
      position: relative;
      width: 200px;
      height: 110px;
      margin-bottom: 8px;

      .gauge-svg { display: block; }

      .score-display {
        position: absolute;
        bottom: 4px;
        left: 50%;
        transform: translateX(-50%);
        text-align: center;

        .score-value {
          font-size: 28px;
          font-weight: 700;
        }

        .score-max {
          font-size: 12px;
          color: var(--text-muted, #787b86);
        }
      }
    }

    .score-level {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 16px;
    }

    .score-dimensions {
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
  }

  // 新的 score-body 样式
  .score-body {
    padding: 16px;
    display: flex;
    flex-direction: column;
    align-items: center;

    .gauge-container {
      position: relative;
      width: 100%;
      max-width: 200px;
      display: flex;
      flex-direction: column;
      align-items: center;

      .gauge-svg {
        display: block;
        width: 100%;
        height: auto;
      }

      .score-display {
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        text-align: center;

        .score-value {
          font-size: 24px;
          font-weight: 700;
          line-height: 1;
        }

        .score-max {
          font-size: 11px;
          color: var(--text-muted, #787b86);
          margin-left: 2px;
        }
      }

      // 风险等级标签
      .gauge-labels {
        display: flex;
        justify-content: space-between;
        width: 100%;
        margin-top: 6px;
        padding: 0 8px;

        .gauge-label {
          font-size: 10px;
          font-weight: 500;

          &.low { color: #26a69a; }
          &.medium { color: #ff9800; }
          &.high { color: #f44336; }
          &.critical { color: #9c27b0; }
        }
      }
    }

    .score-level {
      font-size: 13px;
      font-weight: 600;
      margin-top: 8px;
      margin-bottom: 12px;
    }

    .score-dimensions {
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 8px;

      .dimension-item {
        .dimension-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 4px;

          .dimension-name {
            font-size: 11px;
            color: var(--text-secondary, #cbd5e1);
          }

          .dimension-score {
            font-size: 10px;
            color: var(--text-muted, #787b86);
          }
        }

        .dimension-bar {
          height: 4px;
          background: var(--bg-tertiary, #2a2e39);
          border-radius: 2px;
          overflow: hidden;

          .dimension-fill {
            height: 100%;
            border-radius: 2px;
            transition: width 0.3s ease;
          }
        }
      }
    }
  }
}

// 预警面板
.alerts-panel {
  background: var(--bg-secondary, #1e222d);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  // 移除header分段感，使用统一样式
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 16px 10px;
    // 无背景色区分，无底部边框
  }

  .panel-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary, #d1d4dc);

    svg { color: #f7931a; }

    .alert-count {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 18px;
      height: 18px;
      padding: 0 5px;
      background: #f44336;
      border-radius: 9px;
      font-size: 10px;
      font-weight: 600;
      color: white;
    }
  }

  .alerts-content {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
  }

  .no-alerts {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    color: var(--text-muted, #787b86);

    svg {
      width: 48px;
      height: 48px;
      color: #26a69a;
      margin-bottom: 12px;
    }

    span { font-size: 13px; }
  }

  .alerts-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .alert-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px;
    background: var(--bg-primary, #131722);
    border-radius: 6px;
    border-left: 3px solid;

    &.critical { border-left-color: #f44336; .alert-icon svg { color: #f44336; } }
    &.warning { border-left-color: #ff9800; .alert-icon svg { color: #ff9800; } }
    &.info { border-left-color: #2962ff; .alert-icon svg { color: #2962ff; } }

    .alert-icon {
      flex-shrink: 0;
      svg { width: 18px; height: 18px; }
    }

    .alert-content {
      flex: 1;
      min-width: 0;

      .alert-title {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-primary, #d1d4dc);
        margin-bottom: 2px;
      }

      .alert-description {
        font-size: 11px;
        color: var(--text-secondary, #787b86);
        line-height: 1.3;
        margin-bottom: 4px;
      }

      .alert-time {
        font-size: 10px;
        color: var(--text-muted, #787b86);
      }
    }

    .btn-alert-dismiss {
      flex-shrink: 0;
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: transparent;
      border: 1px solid var(--border-color, #2a2e39);
      border-radius: 4px;
      color: var(--text-muted, #787b86);
      cursor: pointer;
      transition: all 0.15s;

      &:hover {
        border-color: #f44336;
        color: #f44336;
      }

      svg { width: 12px; height: 12px; }
    }
  }
}

// 趋势图内容
.trend-content {
  padding: 16px;
  display: flex;
  gap: 16px;

  .trend-chart {
    flex: 1;
    height: 140px;
    min-width: 200px;
  }

  .trend-stats {
    width: 100px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .trend-stat-item {
    display: flex;
    flex-direction: column;
    gap: 2px;

    .stat-label {
      font-size: 10px;
      color: var(--text-muted, #787b86);
      text-transform: uppercase;
    }

    .stat-value {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
      display: flex;
      align-items: center;
      gap: 4px;

      &.up { color: #ef5350; }
      &.down { color: #26a69a; }
      &.stable { color: var(--text-secondary, #787b86); }

      svg { width: 12px; height: 12px; }
    }
  }
}

.btn-dismiss-all {
  padding: 4px 8px;
  background: transparent;
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 4px;
  color: var(--text-secondary, #cbd5e1);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    background: var(--bg-primary, #131722);
    color: var(--text-primary, #d1d4dc);
  }
}

// ========================================
// 分析卡片行样式（VaR/CVaR + 因子暴露）
// ========================================
.analysis-cards-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 0 20px 24px;
  margin-top: 32px;
}

// 压力测试结果单独一行
.stress-test-row {
  padding: 0 24px 24px;

  .stress-card {
    width: 100%;
  }
}

.analysis-card {
  background: var(--bg-secondary, #1e222d);
  border-radius: 8px;
  overflow: hidden;
  padding: 16px;
}

// VaR/CVaR 卡片
.var-card {
  .var-bars {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 0 16px 12px;
  }

  .var-bar-item {
    display: flex;
    align-items: center;
    gap: 12px;

    .bar-label {
      width: 70px;
      font-size: 11px;
      color: var(--text-secondary, #cbd5e1);
    }

    .bar-track {
      flex: 1;
      height: 8px;
      background: var(--bg-tertiary, #2a2e39);
      border-radius: 4px;
      overflow: hidden;

      .bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;

        &.var { background: linear-gradient(90deg, #2962ff, #42a5f5); }
        &.cvar { background: linear-gradient(90deg, #7b1fa2, #ab47bc); }
      }
    }

    .bar-value {
      width: 60px;
      text-align: right;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
    }
  }

  .var-interpretation {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin: 0 16px 16px;
    padding: 10px;
    background: var(--bg-tertiary, #2a2e39);
    border-radius: 6px;

    svg {
      flex-shrink: 0;
      color: #ff9800;
      margin-top: 2px;
    }

    span {
      font-size: 11px;
      color: var(--text-secondary, #cbd5e1);
      line-height: 1.5;
    }
  }
}

// 因子暴露卡片
.factor-card {
  .factor-exposures {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 0 16px 10px;
  }

  .factor-item {
    display: flex;
    align-items: center;
    gap: 10px;

    .factor-name {
      width: 60px;
      font-size: 11px;
      color: var(--text-secondary, #cbd5e1);
    }

    .factor-bar-container {
      flex: 1;
      display: flex;
      align-items: center;
      height: 8px;

      .factor-bar {
        flex: 1;
        height: 4px;
        background: var(--bg-tertiary, #2a2e39);

        &.negative .bar-fill {
          background: #26a69a;
          border-radius: 2px 0 0 2px;
          margin-left: auto;
        }
        &.positive .bar-fill {
          background: #ef5350;
          border-radius: 0 2px 2px 0;
        }

        .bar-fill {
          height: 100%;
          transition: width 0.3s ease;
        }
      }

      .factor-center {
        width: 2px;
        height: 12px;
        background: var(--text-muted, #787b86);
      }
    }

    .factor-value {
      width: 50px;
      text-align: right;
      font-size: 11px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);

      &.warning { color: #ff9800; }
    }
  }

  .factor-legend {
    display: flex;
    justify-content: center;
    gap: 16px;
    padding: 10px 16px 16px;
    border-top: 1px solid var(--border-color, #2a2e39);
    margin: 0 16px;

    .legend-item {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 10px;
      color: var(--text-muted, #787b86);

      .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 2px;

        &.positive { background: #ef5350; }
        &.negative { background: #26a69a; }
      }
    }
  }
}

// 压力测试卡片
.stress-card {
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color, #2a2e39);

    .test-time {
      font-size: 11px;
      color: var(--text-muted, #787b86);
    }
  }

  .stress-scenarios-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 8px;
    padding: 12px;

    @media (max-width: 1200px) {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  .scenario-mini-card {
    background: var(--bg-tertiary, #2a2e39);
    border-radius: 6px;
    padding: 10px;
    text-align: center;
    border-top: 3px solid var(--text-muted, #787b86);
    position: relative;
    transition: all 0.3s ease;

    &.low { border-top-color: #26a69a; }
    &.medium { border-top-color: #ff9800; }
    &.high { border-top-color: #ef5350; }
    &.critical { border-top-color: #9c27b0; }

    // 当前状态高亮 - 按风险级别使用不同颜色和频率
    &.current {
      &.low, &.risk-low {
        animation: pulse-glow-low 5s ease-in-out infinite;
        &::before { border-top-color: #26a69a; }
        .current-indicator { color: #26a69a; background: rgba(38, 166, 154, 0.2); }
      }
      &.medium, &.risk-medium {
        animation: pulse-glow-medium 4s ease-in-out infinite;
        &::before { border-top-color: #ff9800; }
        .current-indicator { color: #ff9800; background: rgba(255, 152, 0, 0.2); }
      }
      &.high, &.risk-high {
        animation: pulse-glow-high 3s ease-in-out infinite;
        &::before { border-top-color: #ef5350; }
        .current-indicator { color: #ef5350; background: rgba(239, 83, 80, 0.2); }
      }
      &.critical, &.risk-critical {
        animation: pulse-glow-critical 2s ease-in-out infinite;
        &::before { border-top-color: #9c27b0; }
        .current-indicator { color: #9c27b0; background: rgba(156, 39, 176, 0.2); }
      }

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%) translateY(-100%);
        width: 0;
        height: 0;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-top: 10px solid #ff9800;
      }
    }

    .current-indicator {
      position: absolute;
      top: 4px;
      right: 4px;
      display: flex;
      align-items: center;
      gap: 2px;
      font-size: 9px;
      padding: 2px 4px;
      border-radius: 3px;
      animation: pulse-text 4s ease-in-out infinite;

      svg {
        width: 10px;
        height: 10px;
      }
    }

    .scenario-name {
      font-size: 11px;
      color: var(--text-secondary, #cbd5e1);
      margin-bottom: 6px;
    }

    .scenario-loss {
      font-size: 14px;
      font-weight: 700;
      &.loss { color: #26a69a; }
      &.profit { color: #ef5350; }
    }

    .scenario-pct {
      font-size: 10px;
      color: var(--text-muted, #787b86);
      margin-top: 2px;
    }
  }

  .stress-summary-row {
    display: flex;
    gap: 12px;
    padding: 8px 12px 12px;

    .summary-badge {
      font-size: 11px;
      padding: 4px 10px;
      border-radius: 4px;
      background: var(--bg-tertiary, #2a2e39);

      &.worst { color: #ff9800; }
      &.max-loss { color: #ef5350; }
    }
  }
}

// ========================================
// 三栏布局样式
// ========================================
.three-column-grid {
  display: grid;
  grid-template-columns: minmax(240px, 280px) 1fr minmax(240px, 280px);
  gap: 16px;
  padding: 0 20px;
  min-height: 400px;
  margin-bottom: 32px;
}

// 通用面板样式 - 无分段感
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px 10px;
  // 无背景色区分，无底部边框
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary, #d1d4dc);

  svg { color: #26a69a; }
}

// 趋势面板
.trend-panel {
  background: var(--bg-secondary, #1e222d);
  border-radius: 8px;
  overflow: visible;
  display: flex;
  flex-direction: column;
  min-width: 0;

  .trend-summary {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .trend-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;

    &.up {
      background: rgba(239, 83, 80, 0.15);
      color: #ef5350;
    }
    &.down {
      background: rgba(38, 166, 154, 0.15);
      color: #26a69a;
    }
    &.stable {
      background: rgba(120, 123, 134, 0.15);
      color: #787b86;
    }
  }

  .trend-body {
    flex: 1;
    padding: 12px 16px 16px;
    display: flex;
    flex-direction: column;
  }

  .trend-chart {
    flex: 1;
    min-height: 200px;
  }

  .trend-stats-row {
    display: flex;
    justify-content: space-around;
    padding-top: 10px;
    margin-top: 10px;
    // 移除分隔线
  }

  .trend-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;

    .label {
      font-size: 10px;
      color: var(--text-muted, #787b86);
      text-transform: uppercase;
    }

    .value {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary, #d1d4dc);
    }
  }
}

// 预警面板内容
.alerts-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;

  .no-alerts {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 150px;
    color: var(--text-muted, #787b86);
    gap: 8px;

    svg {
      width: 32px;
      height: 32px;
      color: #26a69a;
    }

    span {
      font-size: 12px;
    }
  }

  .alerts-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .alert-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 6px;
    font-size: 12px;

    &.critical {
      background: rgba(239, 83, 80, 0.1);
      border-left: 3px solid #f44336;

      .alert-icon { color: #f44336; }
    }

    &.warning {
      background: rgba(255, 152, 0, 0.1);
      border-left: 3px solid #ff9800;

      .alert-icon { color: #ff9800; }
    }

    &.info {
      background: rgba(41, 98, 255, 0.1);
      border-left: 3px solid #2962ff;

      .alert-icon { color: #2962ff; }
    }

    .alert-icon {
      flex-shrink: 0;
      width: 16px;
      height: 16px;
    }

    .alert-content {
      flex: 1;
      min-width: 0;

      .alert-message {
        color: var(--text-primary, #d1d4dc);
        margin-bottom: 4px;
      }

      .alert-time {
        font-size: 10px;
        color: var(--text-muted, #787b86);
      }
    }

    .btn-dismiss {
      flex-shrink: 0;
      width: 20px;
      height: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: transparent;
      border: none;
      color: var(--text-muted, #787b86);
      cursor: pointer;
      border-radius: 4px;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary, #d1d4dc);
      }
    }
  }
}

// 小型按钮样式
.btn-refresh-sm {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 6px;
  color: var(--text-secondary, #cbd5e1);
  cursor: pointer;
  transition: all 0.15s;

  &:hover:not(:disabled) {
    background: var(--bg-hover, rgba(255, 255, 255, 0.05));
    color: var(--text-primary, #d1d4dc);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .spinning {
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// 当前状态慢闪动画 - 按风险级别颜色
@keyframes pulse-glow-low {
  0%, 100% {
    background: rgba(38, 166, 154, 0.05);
    box-shadow: 0 0 5px rgba(38, 166, 154, 0.2);
  }
  50% {
    background: rgba(38, 166, 154, 0.15);
    box-shadow: 0 0 15px rgba(38, 166, 154, 0.4);
  }
}

@keyframes pulse-glow-medium {
  0%, 100% {
    background: rgba(255, 152, 0, 0.05);
    box-shadow: 0 0 5px rgba(255, 152, 0, 0.2);
  }
  50% {
    background: rgba(255, 152, 0, 0.15);
    box-shadow: 0 0 15px rgba(255, 152, 0, 0.4);
  }
}

@keyframes pulse-glow-high {
  0%, 100% {
    background: rgba(239, 83, 80, 0.05);
    box-shadow: 0 0 5px rgba(239, 83, 80, 0.2);
  }
  50% {
    background: rgba(239, 83, 80, 0.15);
    box-shadow: 0 0 15px rgba(239, 83, 80, 0.4);
  }
}

@keyframes pulse-glow-critical {
  0%, 100% {
    background: rgba(156, 39, 176, 0.05);
    box-shadow: 0 0 5px rgba(156, 39, 176, 0.2);
  }
  50% {
    background: rgba(156, 39, 176, 0.15);
    box-shadow: 0 0 15px rgba(156, 39, 176, 0.4);
  }
}

@keyframes pulse-text {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

// 监控按钮
.btn-monitor {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-tertiary, #2a2e39);
  border: 1px solid var(--border-color, #2a2e39);
  border-radius: 6px;
  color: var(--text-primary, #d1d4dc);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    background: var(--bg-hover, rgba(255, 255, 255, 0.05));
  }

  &.active {
    background: #2962ff;
    border-color: #2962ff;
    color: white;
  }

  svg {
    width: 14px;
    height: 14px;
  }
}

// 图标尺寸
.icon-xs { width: 12px; height: 12px; }
.icon-sm { width: 16px; height: 16px; }
.icon-md { width: 20px; height: 20px; }
.icon-lg { width: 24px; height: 24px; }

// 响应式调整
@media (max-width: 1400px) {
  .key-metrics-row { grid-template-columns: repeat(3, 1fr); }
  .main-content-grid { grid-template-columns: 1fr; }
  .three-column-grid {
    grid-template-columns: minmax(220px, 1fr) 1fr;
    grid-template-rows: auto auto;
  }
  .score-panel { grid-column: 1; grid-row: 1; }
  .trend-panel { grid-column: 2; grid-row: 1; }
  .alerts-panel { grid-column: 1 / -1; grid-row: 2; }
  .analysis-cards-row { grid-template-columns: 1fr; }
  .stress-scenarios-grid { grid-template-columns: repeat(3, 1fr); }
  // 增强型仪表盘卡片：隐藏趋势图
  .gauge-card.enhanced .gauge-sparkline { display: none; }
}

@media (max-width: 1100px) {
  .three-column-grid {
    grid-template-columns: 1fr 1fr;
  }
  .alerts-panel { grid-column: 1 / -1; }
}

@media (max-width: 768px) {
  .key-metrics-row { grid-template-columns: repeat(2, 1fr); }
  .page-header-section { flex-direction: column; gap: 12px; }
  .three-column-grid { grid-template-columns: 1fr; }
  .score-panel, .trend-panel, .alerts-panel {
    grid-column: 1;
    grid-row: auto;
  }
  // 评分面板移动端适配
  .score-panel .score-body {
    padding: 12px;
    .gauge-container {
      max-width: 180px;
    }
    .score-dimensions {
      gap: 8px;
    }
  }
  // 趋势面板移动端适配
  .trend-panel .trend-body {
    padding: 12px;
    .trend-chart {
      min-height: 160px;
    }
  }
}

</style>
