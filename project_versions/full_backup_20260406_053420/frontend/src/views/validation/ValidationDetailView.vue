<template>
  <div class="validation-detail-view">
    <!-- 顶部导航 -->
    <header class="navbar">
      <!-- 返回按钮 - 放在最左边 -->
      <button class="back-btn" @click="goBack" :title="isZh ? '返回工作流' : 'Back to Workflow'">
        <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        {{ isZh ? '返回' : 'Back' }}
      </button>

      <div class="logo">
        <div class="logo-icon">M</div>
        <span>MyQuant</span>
      </div>

      <!-- 阶段相关导航菜单 - Validation阶段 -->
      <nav class="stage-nav">
        <button :class="['stage-btn', { active: currentStageModule === 'paper-trading' }]" @click="switchStageModule('paper-trading')">
          <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          {{ isZh ? '模拟盘' : 'Paper Trading' }}
        </button>
        <button :class="['stage-btn', { active: currentStageModule === 'performance' }]" @click="switchStageModule('performance')">
          <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 21H3V3"/>
            <path d="M21 9l-6 6-4-4-6 6"/>
          </svg>
          {{ isZh ? '绩效分析' : 'Performance' }}
        </button>
        <button :class="['stage-btn', { active: currentStageModule === 'approval' }]" @click="switchStageModule('approval')">
          <svg class="icon-nav" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          {{ isZh ? '审批上线' : 'Approval' }}
        </button>
      </nav>

      <!-- 用户菜单 -->
      <div class="user-menu">
        <button class="icon-btn" @click="toggleLanguage" :title="isZh ? '切换语言' : 'Toggle Language'">
          {{ isZh ? '🇨🇳' : '🇺🇸' }}
        </button>
        <button class="icon-btn" @click="showNotifications" :title="isZh ? '通知' : 'Notifications'">
          🔔
        </button>
        <div class="user-avatar" @click="showUserMenu">U</div>
      </div>
    </header>

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
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else-if="step.id === 2" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 21H3V3"/>
                  <path d="M21 9l-6 6-4-4-6 6"/>
                </svg>
                <svg v-else-if="step.id === 3" class="icon-step" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span v-else class="step-number">{{ step.id }}</span>
              </template>
            </div>
            <div class="step-info">
              <div class="step-title">{{ isZh ? step.nameZh : step.name }}</div>
              <div :class="['step-status', step.status]">
                {{ getStepStatusText(step.status) }}
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 左侧：验证时间线 -->
      <aside class="panel timeline-panel">
        <div class="panel-header">
          <span class="panel-title">
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            {{ isZh ? '验证时间线' : 'Validation Timeline' }}
          </span>
        </div>
        <div class="timeline-list">
          <div
            v-for="item in timelineItems"
            :key="item.id"
            :class="['timeline-item', item.status, { selected: currentItem === item.id }]"
            @click="selectTimelineItem(item.id)"
          >
            <div class="timeline-date">{{ item.date }}</div>
            <div class="timeline-title">
              <span class="title-text">{{ isZh ? item.nameZh : item.name }}</span>
              <span :class="['timeline-badge', item.status]">
                {{ getStatusBadge(item.status) }}
              </span>
            </div>
            <div class="timeline-metrics">
              <div class="metric" v-for="(metric, idx) in item.metrics" :key="idx">
                <span class="metric-label">{{ isZh ? metric.labelZh : metric.label }}:</span>
                <span :class="['metric-value', metric.class]">{{ metric.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 中间：主内容区 -->
      <main class="panel content-panel">
        <div class="content-area">
          <!-- 任务头部信息 -->
          <div class="task-header-info">
            <div class="task-title-row">
              <h1 class="page-title">{{ isZh ? currentTask.titleZh : currentTask.title }}</h1>
              <span class="task-id-badge">#{{ currentTask.id }}</span>
            </div>
            <!-- 任务配置参数 -->
            <div class="task-config-info" v-if="currentTask.stockPool || currentTask.factors">
              <div class="config-item" v-if="currentTask.stockPool">
                <span class="config-label">{{ isZh ? '股票池' : 'Stock Pool' }}</span>
                <span class="config-value">{{ isZh ? currentTask.stockPoolZh : currentTask.stockPool }}</span>
              </div>
              <div class="config-item" v-if="currentTask.factors">
                <span class="config-label">{{ isZh ? '因子' : 'Factors' }}</span>
                <span class="config-value">{{ isZh ? currentTask.factorsZh : currentTask.factors }}</span>
              </div>
              <div class="config-item" v-if="currentTask.model">
                <span class="config-label">{{ isZh ? '模型' : 'Model' }}</span>
                <span class="config-value">{{ currentTask.model }}</span>
              </div>
              <div class="config-item" v-if="currentTask.dateStart">
                <span class="config-label">{{ isZh ? '回测区间' : 'Backtest Period' }}</span>
                <span class="config-value">{{ currentTask.dateStart }} ~ {{ currentTask.dateEnd }}</span>
              </div>
            </div>
          </div>

          <!-- ===== 模拟盘模块 ===== -->
          <template v-if="currentStageModule === 'paper-trading'">
            <p class="page-subtitle">{{ isZh ? '上线前模拟真实交易环境' : 'Simulate real trading environment before going live' }}</p>

            <!-- Stats Grid -->
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-label">{{ isZh ? '总资产' : 'Total Assets' }}</div>
                <div class="stat-value">¥{{ formatNumber(paperMetrics.totalAssets) }}</div>
                <div class="stat-change">{{ isZh ? '模拟账户' : 'Simulation Account' }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">{{ isZh ? '今日盈亏' : "Today's P&L" }}</div>
                <div :class="['stat-value', { positive: paperMetrics.todayPnL > 0, negative: paperMetrics.todayPnL < 0 }]">
                  {{ paperMetrics.todayPnL >= 0 ? '+' : '' }}¥{{ formatNumber(paperMetrics.todayPnL) }}
                </div>
                <div :class="['stat-change', { positive: paperMetrics.todayPnLRate > 0, negative: paperMetrics.todayPnLRate < 0 }]">
                  {{ paperMetrics.todayPnLRate >= 0 ? '+' : '' }}{{ paperMetrics.todayPnLRate.toFixed(2) }}%
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-label">{{ isZh ? '总收益率' : 'Total Return' }}</div>
                <div :class="['stat-value', { positive: paperMetrics.totalReturn > 0, negative: paperMetrics.totalReturn < 0 }]">
                  {{ paperMetrics.totalReturn >= 0 ? '+' : '' }}{{ paperMetrics.totalReturn.toFixed(1) }}%
                </div>
                <div class="stat-change">{{ isZh ? '自开始以来' : 'Since inception' }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">{{ isZh ? '持仓数量' : 'Positions' }}</div>
                <div class="stat-value">{{ paperMetrics.positionCount }}</div>
                <div class="stat-change">{{ isZh ? '只股票' : 'stocks' }}</div>
              </div>
            </div>

            <!-- Equity Curve Chart -->
            <div class="chart-container">
              <TVLineChart
                v-if="equityChartData.strategyData.length > 0"
                ref="equityChartRef"
                :title="isZh ? '权益曲线' : 'Equity Curve'"
                :strategy-data="equityChartData.strategyData"
                :benchmark-data="equityChartData.benchmarkData"
                :dates="equityChartData.dates"
                :strategy-label="equityChartData.strategyLabel"
                :benchmark-label="equityChartData.benchmarkLabel"
                :strategy-color="equityChartData.strategyColor"
                :benchmark-color="equityChartData.benchmarkColor"
                :show-period-selector="true"
                :resizable="true"
                :height="equityChartHeight"
                :locale="isZh ? 'zh' : 'en'"
              />
              <div v-else class="equity-chart-empty">
                <span>{{ isZh ? '暂无数据' : 'No Data' }}</span>
              </div>
            </div>

            <!-- Trade History Table -->
            <div class="table-container">
              <div class="table-header">
                <h3 class="section-title">
                  <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                  {{ isZh ? '交易记录' : 'Trade History' }}
                </h3>
                <ActionButton
                  type="default"
                  size="small"
                  :icon="iconRefresh"
                  :label="isZh ? '刷新' : 'Refresh'"
                  @click="refreshTrades"
                />
              </div>
              <table class="data-table">
                <thead>
                  <tr>
                    <th>{{ isZh ? '时间' : 'Time' }}</th>
                    <th>{{ isZh ? '方向' : 'Side' }}</th>
                    <th>{{ isZh ? '代码' : 'Symbol' }}</th>
                    <th>{{ isZh ? '数量' : 'Qty' }}</th>
                    <th>{{ isZh ? '价格' : 'Price' }}</th>
                    <th>{{ isZh ? '盈亏' : 'P&L' }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="trade in recentTrades" :key="trade.id">
                    <td>{{ trade.time }}</td>
                    <td>
                      <span :class="['side-badge', trade.side]">
                        {{ trade.side === 'buy' ? (isZh ? '买入' : 'BUY') : (isZh ? '卖出' : 'SELL') }}
                      </span>
                    </td>
                    <td>
                      <span class="symbol">{{ trade.symbol }}</span>
                      <span class="symbol-name">{{ trade.name }}</span>
                    </td>
                    <td>{{ trade.quantity }}</td>
                    <td>¥{{ trade.price.toFixed(2) }}</td>
                    <td :class="['pnl', { positive: trade.pnl > 0, negative: trade.pnl < 0 }]">
                      {{ trade.pnl >= 0 ? '+' : '' }}{{ trade.pnl.toFixed(2) }}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>

          <!-- ===== 绩效分析模块 ===== -->
          <template v-else-if="currentStageModule === 'performance'">
            <p class="page-subtitle">{{ isZh ? '全面评估策略表现和风险指标' : 'Comprehensive evaluation of strategy performance and risk metrics' }}</p>

            <!-- 绩效统计 -->
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-label">{{ isZh ? '累计收益' : 'Cumulative Return' }}</div>
                <div :class="['stat-value', { positive: performanceStats.cumulativeReturn > 0, negative: performanceStats.cumulativeReturn < 0 }]">
                  {{ performanceStats.cumulativeReturn >= 0 ? '+' : '' }}{{ performanceStats.cumulativeReturn.toFixed(1) }}%
                </div>
                <div class="stat-change">{{ isZh ? '策略收益' : 'Strategy Return' }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">{{ isZh ? '年化收益' : 'Annual Return' }}</div>
                <div :class="['stat-value', { positive: performanceStats.annualReturn > 0, negative: performanceStats.annualReturn < 0 }]">
                  {{ performanceStats.annualReturn >= 0 ? '+' : '' }}{{ performanceStats.annualReturn.toFixed(1) }}%
                </div>
                <div class="stat-change">{{ isZh ? '年化' : 'Annualized' }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">{{ isZh ? '夏普比率' : 'Sharpe Ratio' }}</div>
                <div :class="['stat-value', { positive: performanceStats.sharpeRatio > 1 }]">
                  {{ performanceStats.sharpeRatio.toFixed(2) }}
                </div>
                <div class="stat-change">{{ isZh ? '风险调整收益' : 'Risk-Adjusted' }}</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">{{ isZh ? '最大回撤' : 'Max Drawdown' }}</div>
                <div :class="['stat-value', { negative: performanceStats.maxDrawdown < -10 }]">
                  {{ performanceStats.maxDrawdown.toFixed(1) }}%
                </div>
                <div class="stat-change">{{ isZh ? '风险控制' : 'Risk Control' }}</div>
              </div>
            </div>

            <!-- 详细指标 -->
            <div class="progress-section">
              <h3 class="section-title" style="margin-bottom: 16px;">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="20" x2="18" y2="10"></line>
                  <line x1="12" y1="20" x2="12" y2="4"></line>
                  <line x1="6" y1="20" x2="6" y2="14"></line>
                </svg>
                {{ isZh ? '详细绩效指标' : 'Detailed Performance Metrics' }}
              </h3>
              <div class="metrics-table">
                <div class="metric-row">
                  <span class="metric-name">{{ isZh ? 'Calmar比率' : 'Calmar Ratio' }}</span>
                  <span :class="['metric-val', { positive: performanceStats.calmarRatio > 3 }]">{{ performanceStats.calmarRatio.toFixed(2) }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">{{ isZh ? 'Sortino比率' : 'Sortino Ratio' }}</span>
                  <span :class="['metric-val', { positive: performanceStats.sortinoRatio > 1 }]">{{ performanceStats.sortinoRatio.toFixed(2) }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">{{ isZh ? '胜率' : 'Win Rate' }}</span>
                  <span :class="['metric-val', { positive: performanceStats.winRate > 50 }]">{{ performanceStats.winRate.toFixed(1) }}%</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">{{ isZh ? '盈亏比' : 'Profit/Loss Ratio' }}</span>
                  <span :class="['metric-val', { positive: performanceStats.profitLossRatio > 1 }]">{{ performanceStats.profitLossRatio.toFixed(2) }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">{{ isZh ? '交易次数' : 'Total Trades' }}</span>
                  <span class="metric-val">{{ performanceStats.totalTrades }}</span>
                </div>
                <div class="metric-row">
                  <span class="metric-name">{{ isZh ? '持仓周期' : 'Holding Period' }}</span>
                  <span class="metric-val">{{ performanceStats.avgHoldingDays }} {{ isZh ? '天' : 'days' }}</span>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <ActionButton
                type="primary"
                :label="isZh ? '生成绩效报告' : 'Generate Report'"
                @click="generatePerformanceReport"
              />
              <ActionButton
                type="default"
                :label="isZh ? '导出数据' : 'Export Data'"
                @click="exportPerformance"
              />
            </div>
          </template>

          <!-- ===== 审批上线模块 ===== -->
          <template v-else-if="currentStageModule === 'approval'">
            <p class="page-subtitle">{{ isZh ? '通过审批后将策略部署到实盘环境' : 'Deploy strategy to production after approval' }}</p>

            <!-- 审批检查清单 -->
            <div class="progress-section">
              <h3 class="section-title" style="margin-bottom: 16px;">
                <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 11l3 3L22 4"></path>
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                </svg>
                {{ isZh ? '上线前检查清单' : 'Pre-Launch Checklist' }}
              </h3>
              <div class="checklist">
                <div v-for="item in approvalChecklist" :key="item.id" :class="['checklist-item', item.status]">
                  <div class="check-icon">
                    <svg v-if="item.status === 'passed'" class="icon-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    <svg v-else-if="item.status === 'failed'" class="icon-fail" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                      <line x1="18" y1="6" x2="6" y2="18"/>
                      <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                    <span v-else class="pending-dot"></span>
                  </div>
                  <div class="check-content">
                    <div class="check-title">{{ isZh ? item.nameZh : item.name }}</div>
                    <div class="check-desc">{{ isZh ? item.descZh : item.desc }}</div>
                  </div>
                  <span :class="['check-status', item.status]">
                    {{ item.status === 'passed' ? (isZh ? '通过' : 'Passed') : item.status === 'failed' ? (isZh ? '未通过' : 'Failed') : (isZh ? '待检查' : 'Pending') }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 审批进度 -->
            <div class="progress-section">
              <div class="progress-header">
                <span class="progress-title">{{ isZh ? '审批进度' : 'Approval Progress' }}</span>
                <span class="progress-percent">{{ approvalProgress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${approvalProgress}%` }"></div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <ActionButton
                type="primary"
                :label="isZh ? '提交审批' : 'Submit for Approval'"
                :disabled="!canSubmitApproval"
                @click="submitForApproval"
              />
              <ActionButton
                type="default"
                :label="isZh ? '运行预检' : 'Run Pre-Check'"
                @click="runPreCheck"
              />
            </div>
          </template>
        </div>
      </main>

      <!-- 右侧：风险监控 -->
      <aside class="panel risk-panel">
        <div class="panel-header">
          <span class="panel-title">
            <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            {{ isZh ? '风险监控' : 'Risk Monitor' }}
          </span>
          <span :class="['risk-status', riskStatus]">{{ getRiskStatusText(riskStatus) }}</span>
        </div>
        <div class="risk-content">
          <div class="risk-item" v-for="risk in riskMetrics" :key="risk.id">
            <div class="risk-header">
              <span class="risk-label">{{ isZh ? risk.labelZh : risk.label }}</span>
              <span :class="['risk-value', risk.level]">
                {{ risk.current }}% ({{ isZh ? '限制' : 'limit' }} {{ risk.limit }}%)
              </span>
            </div>
            <div class="risk-bar">
              <div
                :class="['risk-bar-fill', risk.level]"
                :style="{ width: `${(risk.current / risk.limit) * 100}%` }"
              ></div>
            </div>
          </div>

          <!-- Alert Section -->
          <div class="alert-section">
            <h4 class="alert-title">
              <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
              {{ isZh ? '系统告警' : 'System Alerts' }}
            </h4>
            <div class="alert-list">
              <div
                v-for="alert in alerts"
                :key="alert.id"
                :class="['alert-item', alert.level]"
              >
                <span class="alert-icon">{{ getAlertIcon(alert.level) }}</span>
                <div class="alert-content">
                  <div class="alert-message">{{ isZh ? alert.messageZh : alert.message }}</div>
                  <div class="alert-time">{{ alert.time }}</div>
                </div>
              </div>
              <div v-if="alerts.length === 0" class="no-alerts">
                <span class="no-alert-icon">✓</span>
                {{ isZh ? '暂无告警' : 'No alerts' }}
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ActionButton from '@/components/ui/ActionButton.vue'
import { monitoringApi, simulationApi, type AlertMessage } from '@/api/modules/validation'
import * as echarts from 'echarts'
import { useAppStore } from '@/stores/core/AppStore'
import TVLineChart, { type Time } from '@/components/charts/TVLineChart.vue'

const router = useRouter()
const route = useRoute()

// 全局语言设置
const appStore = useAppStore()
const isZh = computed(() => appStore.language === 'zh')

// 图标定义
const iconRefresh = '<svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>'

// 图表相关
const equityChartRef = ref<any>(null)
let equityChartInstance: echarts.ECharts | null = null

// 权益曲线图高度调整（带localStorage持久化）
const EQUITY_CHART_HEIGHT_KEY = 'myquant-validation-equity-height'
const equityChartHeight = ref(350)

// 加载保存的高度
const loadSavedHeight = () => {
  const saved = localStorage.getItem(EQUITY_CHART_HEIGHT_KEY)
  if (saved) {
    const parsed = parseInt(saved, 10)
    if (!isNaN(parsed) && parsed >= 200 && parsed <= 600) {
      equityChartHeight.value = parsed
    }
  }
}

// 保存高度到localStorage
const saveEquityHeight = () => {
  localStorage.setItem(EQUITY_CHART_HEIGHT_KEY, equityChartHeight.value.toString())
}

// 拖拽调整高度相关状态
const isResizingEquity = ref(false)
const resizeStartY = ref(0)
const resizeStartHeight = ref(0)

// 开始调整高度
const startResizeEquity = (e: MouseEvent) => {
  isResizingEquity.value = true
  resizeStartY.value = e.clientY
  resizeStartHeight.value = equityChartHeight.value
  document.addEventListener('mousemove', onResizeEquity)
  document.addEventListener('mouseup', stopResizeEquity)
  document.body.style.cursor = 'ns-resize'
  document.body.style.userSelect = 'none'
}

// 拖拽中
const onResizeEquity = (e: MouseEvent) => {
  if (!isResizingEquity.value) return
  const delta = e.clientY - resizeStartY.value
  const newHeight = Math.max(200, Math.min(600, resizeStartHeight.value + delta))
  equityChartHeight.value = newHeight
  if (equityChartInstance) {
    equityChartInstance.resize()
  }
}

// 停止调整
const stopResizeEquity = () => {
  if (isResizingEquity.value) {
    isResizingEquity.value = false
    saveEquityHeight()
    document.removeEventListener('mousemove', onResizeEquity)
    document.removeEventListener('mouseup', stopResizeEquity)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }
}

// 获取URL中的taskId参数
const taskId = computed(() => route.query.taskId as string || 'default')

// 任务配置存储
interface TaskConfig {
  id: string
  title: string
  titleZh: string
  stockPool?: string
  stockPoolZh?: string
  dateStart?: string
  dateEnd?: string
  factors?: string
  factorsZh?: string
  model?: string
  progress: number
  status: string
}

const taskStore: Record<string, TaskConfig> = {
  'VAL-2024-001': {
    id: 'VAL-2024-001',
    title: 'Alpha158 Strategy Paper Trading',
    titleZh: 'Alpha158策略模拟交易',
    stockPool: 'CSI300',
    stockPoolZh: '沪深300',
    dateStart: '2024-01-01',
    dateEnd: '2024-12-31',
    factors: 'Alpha158',
    factorsZh: 'Alpha158因子集',
    model: 'LightGBM',
    progress: 35,
    status: 'running'
  },
  'VAL-2024-002': {
    id: 'VAL-2024-002',
    title: 'Momentum Strategy Validation',
    titleZh: '动量策略验证',
    stockPool: 'CSI500',
    stockPoolZh: '中证500',
    dateStart: '2023-01-01',
    dateEnd: '2024-12-31',
    factors: 'Momentum',
    factorsZh: '动量因子',
    model: 'XGBoost',
    progress: 0,
    status: 'queued'
  },
  'VAL-2024-003': {
    id: 'VAL-2024-003',
    title: 'Multi-Factor Model Validation',
    titleZh: '多因子模型验证',
    stockPool: 'All A-shares',
    stockPoolZh: '全A股',
    dateStart: '2022-01-01',
    dateEnd: '2024-12-31',
    factors: 'Multi-Factor',
    factorsZh: '多因子组合',
    model: 'Ensemble',
    progress: 72,
    status: 'running'
  },
  'VAL-2024-004': {
    id: 'VAL-2024-004',
    title: 'Risk Model Stress Test',
    titleZh: '风险模型压力测试',
    stockPool: 'CSI300',
    stockPoolZh: '沪深300',
    factors: 'Risk Factors',
    factorsZh: '风险因子',
    progress: 100,
    status: 'completed'
  },
  'VAL-2024-005': {
    id: 'VAL-2024-005',
    title: 'Strategy Approval Review',
    titleZh: '策略审批评审',
    stockPool: 'CSI300',
    stockPoolZh: '沪深300',
    factors: 'Alpha158',
    factorsZh: 'Alpha158因子集',
    model: 'LightGBM',
    progress: 0,
    status: 'queued'
  },
  'default': {
    id: 'VAL-DEFAULT',
    title: 'Validation Task',
    titleZh: '验证任务',
    progress: 50,
    status: 'running'
  }
}

const currentTask = computed(() => taskStore[taskId.value] || taskStore['default'])

// 阶段模块导航
const currentStageModule = ref('paper-trading')

const switchStageModule = (module: string) => {
  currentStageModule.value = module
  console.log('Switching to module:', module)
}

// 工作流步骤
const workflowSteps = ref([
  { id: 1, name: 'Paper Trading', nameZh: '模拟交易', status: 'active' },
  { id: 2, name: 'Performance Analysis', nameZh: '绩效分析', status: 'pending' },
  { id: 3, name: 'Approval', nameZh: '审批上线', status: 'pending' }
])

const currentStep = ref(1)

// 选择步骤
const selectStep = (stepId: number) => {
  currentStep.value = stepId
  // 根据步骤切换到对应的模块
  const stepModuleMap: Record<number, string> = {
    1: 'paper-trading',
    2: 'performance',
    3: 'approval'
  }
  switchStageModule(stepModuleMap[stepId] || 'paper-trading')
}

// 获取步骤状态文本
const getStepStatusText = (status: string) => {
  const statusMap: Record<string, { zh: string; en: string }> = {
    completed: { zh: '已完成', en: 'Completed' },
    active: { zh: '进行中', en: 'In Progress' },
    pending: { zh: '待处理', en: 'Pending' }
  }
  const statusObj = statusMap[status] || statusMap.pending
  return isZh.value ? statusObj.zh : statusObj.en
}

const toggleLanguage = () => {
  appStore.setLanguage(appStore.language === 'zh' ? 'en' : 'zh')
}

const goBack = () => {
  router.push('/workflow')
}

const showNotifications = () => {
  console.log('Showing notifications...')
}

const showUserMenu = () => {
  console.log('Showing user menu...')
}

const navigateStage = (stageId: string) => {
  if (stageId === 'research') router.push('/research/detail')
  if (stageId === 'production') router.push('/production/detail')
}

// 时间线数据
interface TimelineMetric {
  label: string
  labelZh: string
  value: string
  class?: string
}

interface TimelineItem {
  id: number
  name: string
  nameZh: string
  date: string
  status: 'completed' | 'active' | 'pending'
  metrics: TimelineMetric[]
}

const timelineItems = ref<TimelineItem[]>([
  {
    id: 1,
    name: 'Historical Backtest',
    nameZh: '历史回测',
    date: '2024-01-15',
    status: 'completed',
    metrics: [
      { label: 'Return', labelZh: '收益', value: '+15.2%', class: 'positive' },
      { label: 'Sharpe', labelZh: '夏普', value: '1.8', class: 'positive' }
    ]
  },
  {
    id: 2,
    name: 'Paper Trading',
    nameZh: '模拟实盘',
    date: '2024-01-20 - Present',
    status: 'active',
    metrics: [
      { label: 'Current', labelZh: '当前', value: '+2.3%', class: 'positive' },
      { label: 'Days', labelZh: '天数', value: '5' }
    ]
  },
  {
    id: 3,
    name: 'Online Rolling Training',
    nameZh: '在线滚动训练',
    date: isZh.value ? '待定' : 'Scheduled',
    status: 'pending',
    metrics: [
      { label: 'Window', labelZh: '窗口', value: '252 days' }
    ]
  },
  {
    id: 4,
    name: 'Risk Assessment',
    nameZh: '风险评估',
    date: isZh.value ? '待定' : 'Scheduled',
    status: 'pending',
    metrics: [
      { label: 'Metrics', labelZh: '指标', value: '5 dimensions' }
    ]
  }
])

const currentItem = ref(2)

const selectTimelineItem = (id: number) => {
  currentItem.value = id
}

const getStatusBadge = (status: string) => {
  const statusMapZh: Record<string, string> = {
    completed: '已完成',
    active: '进行中',
    pending: '待处理'
  }
  const statusMapEn: Record<string, string> = {
    completed: 'Completed',
    active: 'Active',
    pending: 'Pending'
  }
  return (isZh.value ? statusMapZh[status] : statusMapEn[status]) || status
}

// 指标数据
const paperMetrics = reactive({
  totalAssets: 1023456,
  todayPnL: 2345,
  todayPnLRate: 0.23,
  totalReturn: 2.3,
  positionCount: 8
})

// 净值曲线数据
const equityCurveData = reactive({
  dates: [] as string[],
  values: [] as number[],
  benchmark: [] as number[]
})

// 净值曲线数据 - 适配TVLineChart
const equityChartData = computed(() => {
  const currentIsZh = isZh.value

  const dates = equityCurveData.dates
  const values = equityCurveData.values
  const benchmark = equityCurveData.benchmark

  if (!dates.length || !values.length) {
    return {
      strategyData: [],
      benchmarkData: [],
      dates: [],
      strategyLabel: currentIsZh ? '策略' : 'Strategy',
      benchmarkLabel: currentIsZh ? '基准' : 'Benchmark',
      strategyColor: '#ef5350',
      benchmarkColor: '#787b86'
    }
  }

  const strategyData = dates.map((date, index) => ({
    time: date as Time,
    value: values[index]
  }))

  const benchmarkData = benchmark.length > 0
    ? dates.map((date, index) => ({
        time: date as Time,
        value: benchmark[index]
      }))
    : []

  // 根据收益率设置颜色 - 红涨绿跌
  const lastValue = values[values.length - 1]
  const firstValue = values[0]
  const returnPct = (lastValue - firstValue) / firstValue
  const strategyColor = returnPct >= 0 ? '#ef5350' : '#26a69a'

  return {
    strategyData,
    benchmarkData,
    dates,
    strategyLabel: currentIsZh ? '策略' : 'Strategy',
    benchmarkLabel: currentIsZh ? '基准' : 'Benchmark',
    strategyColor,
    benchmarkColor: '#787b86'
  }
})

// 生成模拟净值数据
const generateMockEquityData = () => {
  const dates: string[] = []
  const values: number[] = [1.0]
  const benchmark: number[] = [1.0]
  const today = new Date()

  // 生成60个交易日的数据
  for (let i = 59; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    if (date.getDay() !== 0 && date.getDay() !== 6) { // 跳过周末
      dates.push(date.toISOString().split('T')[0])

      // 策略收益率带趋势
      const dailyReturn = (Math.random() - 0.45) * 0.02
      values.push(values[values.length - 1] * (1 + dailyReturn))

      // 基准收益率
      const benchmarkReturn = (Math.random() - 0.48) * 0.015
      benchmark.push(benchmark[benchmark.length - 1] * (1 + benchmarkReturn))
    }
  }

  equityCurveData.dates = dates
  equityCurveData.values = values
  equityCurveData.benchmark = benchmark
}

// Y轴范围计算
const yAxisMin = computed(() => {
  if (equityCurveData.values.length === 0) return 0.95
  const minVal = Math.min(...equityCurveData.values, ...equityCurveData.benchmark)
  return Math.floor((minVal - 0.02) * 100) / 100
})

const yAxisMax = computed(() => {
  if (equityCurveData.values.length === 0) return 1.1
  const maxVal = Math.max(...equityCurveData.values, ...equityCurveData.benchmark)
  return Math.ceil((maxVal + 0.02) * 100) / 100
})

// 计算基准收益率
const benchmarkReturn = computed(() => {
  if (equityCurveData.benchmark.length < 2) return 0
  const first = equityCurveData.benchmark[0]
  const last = equityCurveData.benchmark[equityCurveData.benchmark.length - 1]
  return (last - first) / first
})

// 深色主题配色
const darkTheme = {
  background: '#1e222d',
  text: '#d1d4dc',
  textSecondary: '#787b86',
  border: '#2a2e39',
  up: '#ef5350',
  down: '#26a69a',
  accent: '#2962ff',
  benchmark: '#787b86'
}

// 窗口大小变化
const handleChartResize = () => {
  // TVLineChart会自动处理
}

// 格式化数字
const formatNumber = (num: number) => {
  return num.toLocaleString('zh-CN')
}

// 交易记录
interface Trade {
  id: string
  time: string
  side: 'buy' | 'sell'
  symbol: string
  name: string
  quantity: number
  price: number
  pnl: number
}

const recentTrades = ref<Trade[]>([
  { id: '1', time: '09:31:25', side: 'buy', symbol: '600519', name: '贵州茅台', quantity: 100, price: 1850.00, pnl: 1.2 },
  { id: '2', time: '09:32:10', side: 'sell', symbol: '000858', name: '五粮液', quantity: 50, price: 152.80, pnl: 0.8 },
  { id: '3', time: '09:33:05', side: 'buy', symbol: '600036', name: '招商银行', quantity: 200, price: 35.60, pnl: -0.3 },
  { id: '4', time: '09:35:18', side: 'buy', symbol: '000001', name: '平安银行', quantity: 300, price: 12.35, pnl: 0.5 },
  { id: '5', time: '09:38:22', side: 'sell', symbol: '601318', name: '中国平安', quantity: 80, price: 49.20, pnl: 2.1 }
])

const refreshTrades = async () => {
  console.log('Refreshing trades...')
}

// ========== 绩效分析模块数据 ==========
const performanceStats = reactive({
  cumulativeReturn: 15.8,
  annualReturn: 18.5,
  sharpeRatio: 1.85,
  maxDrawdown: -8.2,
  calmarRatio: 2.26,
  sortinoRatio: 2.15,
  winRate: 58.6,
  profitLossRatio: 1.45,
  totalTrades: 156,
  avgHoldingDays: 3.5
})

const generatePerformanceReport = () => {
  console.log('Generating performance report...')
}

const exportPerformance = () => {
  console.log('Exporting performance data...')
}

// ========== 审批上线模块数据 ==========
interface ChecklistItem {
  id: string
  name: string
  nameZh: string
  desc: string
  descZh: string
  status: 'passed' | 'failed' | 'pending'
}

const approvalChecklist = ref<ChecklistItem[]>([
  { id: '1', name: 'Backtest Performance', nameZh: '回测绩效', desc: 'Annual return > 10%, Sharpe > 1', descZh: '年化收益>10%, 夏普>1', status: 'passed' },
  { id: '2', name: 'Paper Trading', nameZh: '模拟盘测试', desc: 'Paper trading > 5 trading days', descZh: '模拟盘运行>5个交易日', status: 'passed' },
  { id: '3', name: 'Risk Limits', nameZh: '风险限制', desc: 'Max drawdown < 15%', descZh: '最大回撤<15%', status: 'passed' },
  { id: '4', name: 'Position Limits', nameZh: '持仓限制', desc: 'Single position < 20%', descZh: '单只持仓<20%', status: 'passed' },
  { id: '5', name: 'Model Version', nameZh: '模型版本', desc: 'Model v1.2.0 validated', descZh: '模型v1.2.0已验证', status: 'passed' },
  { id: '6', name: 'Compliance Check', nameZh: '合规检查', desc: 'Compliance review completed', descZh: '合规审查已完成', status: 'pending' }
])

const approvalProgress = computed(() => {
  const passed = approvalChecklist.value.filter(item => item.status === 'passed').length
  return Math.round((passed / approvalChecklist.value.length) * 100)
})

const canSubmitApproval = computed(() => {
  return approvalChecklist.value.every(item => item.status === 'passed')
})

const submitForApproval = () => {
  console.log('Submitting for approval...')
}

const runPreCheck = () => {
  console.log('Running pre-check...')
}

// 风险指标
interface RiskMetric {
  id: string
  label: string
  labelZh: string
  current: number
  limit: number
  level: 'safe' | 'warning' | 'danger'
}

const riskMetrics = ref<RiskMetric[]>([
  { id: 'single', label: 'Single Position', labelZh: '单只持仓', current: 15, limit: 20, level: 'safe' },
  { id: 'sector', label: 'Sector Concentration', labelZh: '行业集中度', current: 35, limit: 40, level: 'warning' },
  { id: 'drawdown', label: 'Current Drawdown', labelZh: '当前回撤', current: 3.2, limit: 15, level: 'safe' },
  { id: 'dailyLoss', label: 'Daily Loss', labelZh: '日内亏损', current: 0.8, limit: 5, level: 'safe' },
  { id: 'volatility', label: 'Volatility', labelZh: '波动率', current: 18, limit: 20, level: 'safe' }
])

const riskStatus = computed(() => {
  const hasDanger = riskMetrics.value.some(r => r.level === 'danger')
  const hasWarning = riskMetrics.value.some(r => r.level === 'warning')
  if (hasDanger) return 'danger'
  if (hasWarning) return 'warning'
  return 'safe'
})

const getRiskStatusText = (status: string) => {
  const statusMapZh: Record<string, string> = {
    safe: '安全',
    warning: '警告',
    danger: '危险'
  }
  const statusMapEn: Record<string, string> = {
    safe: 'Safe',
    warning: 'Warning',
    danger: 'Danger'
  }
  return isZh.value ? statusMapZh[status] : statusMapEn[status]
}

// 告警
interface Alert {
  id: string
  level: 'info' | 'warning' | 'critical'
  message: string
  messageZh: string
  time: string
}

const alerts = ref<Alert[]>([
  { id: '1', level: 'warning', message: 'Sector concentration approaching limit', messageZh: '行业集中度接近限制', time: '10:30' },
  { id: '2', level: 'info', message: 'Model retraining scheduled for tonight', messageZh: '模型重训练已安排在今晚', time: '09:00' }
])

const getAlertIcon = (level: string) => {
  const icons: Record<string, string> = {
    info: 'ℹ️',
    warning: '⚠️',
    critical: '🔴'
  }
  return icons[level] || 'ℹ️'
}

// 刷新数据
let refreshInterval: ReturnType<typeof setInterval> | null = null

const refreshData = async () => {
  try {
    // 获取概览数据
    const overviewRes = await monitoringApi.getOverview()
    if (overviewRes.data) {
      paperMetrics.totalAssets = overviewRes.data.currentAssets
      paperMetrics.totalReturn = overviewRes.data.totalReturnRate * 100
    }

    // 获取风险指标
    const riskRes = await monitoringApi.getRiskMetrics()
    if (riskRes.data) {
      // 更新风险指标
    }

    // 获取告警
    const alertsRes = await monitoringApi.getAlerts()
    // 更新告警列表
  } catch (error) {
    console.error('Failed to refresh data:', error)
  }
}

// 监听语言变化，重新渲染图表
watch(isZh, () => {
  // TVLineChart会自动响应标签变化
})

onMounted(async () => {
  console.log('ValidationDetailView mounted')
  // 加载保存的图表高度
  loadSavedHeight()
  // 生成模拟净值数据
  generateMockEquityData()
  // TVLineChart会自动初始化
  // 监听窗口大小变化
  window.addEventListener('resize', handleChartResize)
  // 初始加载数据
  // await refreshData()

  // 定时刷新（每30秒）
  // refreshInterval = setInterval(refreshData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  // 销毁图表实例
  if (equityChartInstance) {
    equityChartInstance.dispose()
    equityChartInstance = null
  }
  window.removeEventListener('resize', handleChartResize)
})
</script>

<style scoped>
/* 主容器 - 使用固定定位覆盖整个屏幕 */
.validation-detail-view {
  --bg-primary: #131722;
  --bg-secondary: #1e222d;
  --bg-tertiary: #2a2e39;
  --text-primary: #d1d4dc;
  --text-secondary: #787b86;
  --accent-blue: #2962ff;
  /* A股颜色规则：红涨绿跌 */
  --color-up: #ef5350;      /* 红色 - 上涨/正面 */
  --color-down: #26a69a;    /* 绿色 - 下跌/负面 */
  --accent-red: #ef5350;
  --accent-green: #26a69a;
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

/* 顶部导航 */
.navbar {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-orange));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
}

/* 阶段导航菜单样式 */
.stage-nav {
  display: flex;
  gap: 4px;
  flex: 1;
  margin-left: 16px;
}

.stage-btn {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
}

.stage-btn:hover {
  color: var(--text-primary);
  background: transparent;
}

.stage-btn.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
  background: transparent;
}

.icon-nav {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

/* 用户菜单 */
.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-orange));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.2s;
}

.user-avatar:hover {
  transform: scale(1.1);
}

.back-btn {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  margin-right: 16px;
}

.back-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--accent-blue);
}

.icon-btn {
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.icon-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.icon-sm {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* 主容器布局 */
.main-container {
  display: grid;
  grid-template-columns: 280px 280px 1fr 280px;
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

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 工作流步骤列表 */
.workflow-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.workflow-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.workflow-step:hover {
  background: var(--bg-secondary);
}

.workflow-step.selected {
  background: var(--bg-tertiary);
  border: 1px solid var(--accent-blue);
}

.workflow-step.completed .step-icon {
  background: #26a69a;
  color: #fff;
}

.workflow-step.active .step-icon {
  background: var(--accent-blue);
  color: #fff;
}

.workflow-step.pending .step-icon {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-check {
  width: 16px;
  height: 16px;
}

.icon-step {
  width: 18px;
  height: 18px;
}

.step-number {
  font-size: 14px;
  font-weight: 600;
}

.step-info {
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.step-status {
  font-size: 11px;
  color: var(--text-secondary);
}

.step-status.completed {
  color: #26a69a;
}

.step-status.active {
  color: var(--accent-blue);
}

/* 时间线列表 */
.timeline-list {
  flex: 1;
  overflow-y: auto;
}

.timeline-item {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.15s;
}

.timeline-item:hover {
  background: var(--bg-secondary);
}

.timeline-item.selected {
  background: var(--bg-tertiary);
  border-left: 2px solid var(--accent-blue);
}

.timeline-date {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.timeline-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.title-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.timeline-badge {
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
}

.timeline-badge.completed {
  background: rgba(239, 83, 80, 0.2);
  color: var(--color-up);
}

.timeline-badge.active {
  background: rgba(41, 98, 255, 0.2);
  color: var(--accent-blue);
}

.timeline-badge.pending {
  background: rgba(120, 123, 134, 0.2);
  color: var(--text-secondary);
}

.timeline-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 11px;
}

.metric {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
}

.metric-label {
  color: var(--text-secondary);
}

.metric-value {
  color: var(--text-primary);
  font-weight: 600;
}

.metric-value.positive {
  color: var(--color-up);
}

.metric-value.negative {
  color: var(--color-down);
}

/* 主内容区 */
.content-area {
  padding: 24px;
  overflow-y: auto;
}

/* 任务头部信息 */
.task-header-info {
  margin-bottom: 20px;
}

.task-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.task-id-badge {
  padding: 4px 10px;
  background: rgba(41, 98, 255, 0.15);
  border: 1px solid rgba(41, 98, 255, 0.3);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-blue);
  font-family: monospace;
}

.task-config-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-label {
  font-size: 11px;
  color: var(--text-secondary);
}

.config-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 16px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

/* A股规则：红涨/好，绿跌/坏 */
.stat-value.positive {
  color: var(--color-up);
}

.stat-value.negative {
  color: var(--color-down);
}

.stat-change {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.stat-change.positive {
  color: var(--color-up);
}

.stat-change.negative {
  color: var(--color-down);
}

/* 图表容器 */
.chart-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 24px;
  position: relative;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--text-secondary);
}

.legend-line {
  width: 16px;
  height: 2px;
  border-radius: 1px;
}

.legend-line.strategy {
  background: var(--accent-green);
}

.legend-line.benchmark {
  background: var(--text-secondary);
  background: repeating-linear-gradient(
    90deg,
    var(--text-secondary),
    var(--text-secondary) 3px,
    transparent 3px,
    transparent 6px
  );
}

.chart-body {
  height: 250px;
}

.chart-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.equity-chart {
  width: 100%;
  /* height 由JS动态控制 */
  background: var(--bg-primary, #131722);
  border-radius: 4px;
}

.equity-chart-empty {
  width: 100%;
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted, #787b86);
  background: var(--bg-primary, #131722);
  border-radius: 4px;
}

/* 图表调整高度把手 */
.resize-handle {
  position: absolute;
  bottom: -12px;
  left: 0;
  right: 0;
  height: 24px;
  cursor: ns-resize;
  display: flex;
  align-items: center;
  justify-content: center;
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

/* 表格 */
.table-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;

  .icon-sm {
    width: 16px;
    height: 16px;
    color: inherit;
  }
}

.side-badge {
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
}

.side-badge.buy {
  background: rgba(239, 83, 80, 0.2);
  color: var(--color-up);
}

.side-badge.sell {
  background: rgba(38, 166, 154, 0.2);
  color: var(--color-down);
}

.symbol {
  font-weight: 600;
  color: var(--text-primary);
}

.symbol-name {
  margin-left: 8px;
  color: var(--text-secondary);
  font-size: 12px;
}

.pnl {
  font-weight: 600;
}

.pnl.positive {
  color: var(--color-up);
}

.pnl.negative {
  color: var(--color-down);
}

/* 按钮 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 11px;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: #363a45;
}

/* 风险面板 */
.risk-panel .panel-header {
  gap: 12px;
}

.risk-status {
  padding: 4px 10px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
}

.risk-status.safe {
  background: rgba(38, 166, 154, 0.2);
  color: var(--accent-green);
}

.risk-status.warning {
  background: rgba(255, 152, 0, 0.2);
  color: var(--accent-orange);
}

.risk-status.danger {
  background: rgba(239, 83, 80, 0.2);
  color: var(--accent-red);
}

.risk-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.risk-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 8px;
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.risk-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.risk-value {
  font-size: 11px;
}

.risk-value.safe {
  color: var(--accent-green);
}

.risk-value.warning {
  color: var(--accent-orange);
}

.risk-value.danger {
  color: var(--accent-red);
}

.risk-bar {
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.risk-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.risk-bar-fill.safe {
  background: var(--accent-green);
}

.risk-bar-fill.warning {
  background: var(--accent-orange);
}

.risk-bar-fill.danger {
  background: var(--accent-red);
}

/* 告警区域 */
.alert-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.alert-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px;
  background: var(--bg-secondary);
  border-radius: 4px;
  font-size: 11px;
}

.alert-item.info {
  border-left: 2px solid var(--accent-blue);
}

.alert-item.warning {
  border-left: 2px solid var(--accent-orange);
}

.alert-item.critical {
  border-left: 2px solid var(--accent-red);
}

.alert-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

.alert-message {
  color: var(--text-primary);
  margin-bottom: 4px;
}

.alert-time {
  color: var(--text-secondary);
  font-size: 10px;
}

.no-alerts {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: var(--text-secondary);
  font-size: 12px;
}

.no-alert-icon {
  color: var(--accent-green);
  font-weight: 700;
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

/* 绩效分析模块样式 */
.metrics-table {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.metric-name {
  color: var(--text-secondary);
  font-size: 12px;
}

.metric-val {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.metric-val.positive {
  color: var(--color-up);
}

/* 审批上线模块样式 */
.checklist {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.checklist-item.passed {
  border-left: 3px solid var(--color-up);
}

.checklist-item.failed {
  border-left: 3px solid var(--color-down);
}

.checklist-item.pending {
  border-left: 3px solid var(--text-secondary);
}

.check-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-check {
  width: 18px;
  height: 18px;
  color: var(--color-up);
}

.icon-fail {
  width: 18px;
  height: 18px;
  color: var(--color-down);
}

.pending-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-secondary);
}

.check-content {
  flex: 1;
}

.check-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.check-desc {
  font-size: 11px;
  color: var(--text-secondary);
}

.check-status {
  padding: 4px 10px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
}

.check-status.passed {
  background: rgba(239, 83, 80, 0.2);
  color: var(--color-up);
}

.check-status.failed {
  background: rgba(38, 166, 154, 0.2);
  color: var(--color-down);
}

.check-status.pending {
  background: rgba(120, 123, 134, 0.2);
  color: var(--text-secondary);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  margin-top: 24px;
}

.btn-primary {
  background: var(--accent-blue);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1e4bd8;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.progress-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 24px;
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
</style>
