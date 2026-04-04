<script setup lang="ts">
import { ref } from 'vue'
import { TrendingUpOutline, TrendingDownOutline, AnalyticsOutline, WalletOutline, SpeedometerOutline } from '@vicons/ionicons5'

// 表格测试数据
const tableData = [
  { code: '600519', name: '贵州茅台', price: 1850.00, change: 2.35 },
  { code: '000858', name: '五粮液', price: 156.80, change: -1.25 },
  { code: '601318', name: '中国平安', price: 48.50, change: 0.00 },
  { code: '600036', name: '招商银行', price: 35.20, change: 1.85 },
  { code: '000001', name: '平安银行', price: 12.45, change: -0.65 },
]

// 导入新增的可复用组件
import ScoreCard from '@/components/ui/ScoreCard.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import RiskGauge from '@/components/ui/RiskGauge.vue'
import RiskScoreGauge from '@/components/ui/RiskScoreGauge.vue'
import VaRCVaRCard from '@/components/ui/VaRCVaRCard.vue'
import FactorExposureCard from '@/components/ui/FactorExposureCard.vue'
import FactorQualityRadar from '@/components/ui/FactorQualityRadar.vue'
import FactorEvaluationCard from '@/components/ui/FactorEvaluationCard.vue'
import PositionRiskCard from '@/components/ui/PositionRiskCard.vue'
import PortfolioAnalysisCard from '@/components/ui/PortfolioAnalysisCard.vue'
import RiskRuleCard from '@/components/ui/RiskRuleCard.vue'
import RiskEventCard from '@/components/ui/RiskEventCard.vue'
import SummaryCard from '@/components/ui/SummaryCard.vue'
import StatusLight from '@/components/ui/StatusLight.vue'
import FeatureEntry from '@/components/ui/FeatureEntry.vue'
import TaskCard from '@/components/ui/TaskCard.vue'
import SectorListCard from '@/components/ui/SectorListCard.vue'
import ModeSwitch from '@/components/ui/ModeSwitch.vue'
import RefreshButton from '@/components/ui/RefreshButton.vue'
import ActionButton from '@/components/ui/ActionButton.vue'
import FactorTag from '@/components/ui/FactorTag.vue'
import Table from '@/components/ui/Table.vue'
import PeriodSelector from '@/components/ui/PeriodSelector.vue'
import ChartToggle from '@/components/ui/ChartToggle.vue'
import FactorCard from '@/components/ui/FactorCard.vue'

// 导入图表卡片组件
import FactorWeightCard from '@/components/ui/charts/FactorWeightCard.vue'
import PerformanceRadarCard from '@/components/ui/charts/PerformanceRadarCard.vue'
import RiskCompareCard from '@/components/ui/charts/RiskCompareCard.vue'

// 导入图表组件
import BarChart3D from '@/components/ui/charts/BarChart3D.vue'
import DonutChart from '@/components/ui/charts/DonutChart.vue'
import RadarChart from '@/components/ui/charts/RadarChart.vue'
import HorizontalBarChart from '@/components/ui/charts/HorizontalBarChart.vue'
import ScoreBarChart from '@/components/ui/charts/ScoreBarChart.vue'

// 评分颜色计算函数（与因子分析页面一致）
const getFactorQualityColor = (score: number) => {
  if (score > 100) return '#8b5cf6'   // 紫色
  if (score >= 80) return '#ef5350'    // 红色 - 优秀
  if (score >= 60) return '#ff9800'    // 橙色 - 良好
  if (score >= 40) return '#2962ff'    // 蓝色 - 一般
  return '#26a69a'                      // 绿色 - 较差
}

// 获取字母等级
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

// 评分卡片数据
const scoreCards = [
  { label: '综合评分', score: 85, grade: 'A' },
  { label: '风险评估', score: 62, grade: 'B' },
  { label: '可行性', score: 78, grade: 'A-' }
]

// 滑杆值（交互用）
const sliderValue = ref(60)

// ModeSwitch 演示变量
const modeValue = ref('live')
const modeOptions = [
  { value: 'live', label: '实盘', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>' },
  { value: 'sim', label: '模拟', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>' }
]

// PeriodSelector 演示变量
const periodValue = ref('1d')
const periodOptions = [
  { value: '1d', label: '1日' },
  { value: '1w', label: '1周' },
  { value: '1m', label: '1月' },
  { value: '3m', label: '3月' },
  { value: '1y', label: '1年' }
]

// ChartToggle 演示变量
const chartType = ref('bar')

const updateSliderValue = (event: Event) => {
  const target = event.target as HTMLInputElement
  sliderValue.value = parseInt(target.value)
}
</script>

<template>
  <div class="style-test-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">统一设计系统 - 效果预览</h1>
        <p class="page-subtitle">基于工作流风格的全局样式统一演示</p>
      </div>
    </header>

    <div class="page-content">
      <!-- 第一部分：按钮系统 -->
      <section class="section">
        <h2 class="section-title">1. 按钮系统</h2>
        <div class="demo-block">
          <div class="demo-row">
            <span class="demo-label">主要按钮：</span>
            <button class="btn btn-primary">主要按钮</button>
            <button class="btn btn-primary btn-sm">小型</button>
            <button class="btn btn-primary btn-lg">大型</button>
            <button class="btn btn-primary" disabled>禁用</button>
          </div>
          <div class="demo-row">
            <span class="demo-label">次要按钮：</span>
            <button class="btn btn-secondary">次要按钮</button>
            <button class="btn btn-secondary btn-sm">小型</button>
            <button class="btn btn-secondary btn-lg">大型</button>
          </div>
          <div class="demo-row">
            <span class="demo-label">状态按钮：</span>
            <button class="btn btn-success">成功</button>
            <button class="btn btn-warning">警告</button>
            <button class="btn btn-danger">危险</button>
            <button class="btn btn-ghost">幽灵</button>
          </div>
          <div class="demo-row">
            <span class="demo-label">加载状态：</span>
            <button class="btn btn-primary">
              <span class="loading-line"></span>
              加载中
            </button>
          </div>
        </div>
      </section>

      <!-- 第二部分：输入框系统 -->
      <section class="section">
        <h2 class="section-title">2. 输入框系统</h2>
        <div class="demo-block">
          <div class="demo-row">
            <span class="demo-label">基础输入框：</span>
            <input type="text" class="input" placeholder="请输入内容" />
            <input type="text" class="input input-sm" placeholder="小型输入框" />
          </div>
          <div class="demo-row">
            <span class="demo-label">计数器：</span>
            <div class="input-number">
              <button class="input-number-btn">-</button>
              <input type="text" class="input-number-input" value="1" />
              <button class="input-number-btn">+</button>
            </div>
          </div>
          <div class="demo-row">
            <span class="demo-label">下拉框：</span>
            <div class="select-dropdown-demo">
              <div class="select-trigger-demo">
                <span>请选择选项</span>
                <span class="select-arrow">▼</span>
              </div>
              <div class="select-dropdown-demo-content">
                <div class="select-option-demo">选项一</div>
                <div class="select-option-demo">选项二</div>
                <div class="select-option-demo is-selected">选项三（已选）</div>
                <div class="select-option-demo">选项四</div>
              </div>
            </div>
          </div>
          <div class="demo-row">
            <span class="demo-label">多选下拉框：</span>
            <div class="select-dropdown-demo select-multiple-demo">
              <div class="select-trigger-demo">
                <div class="select-tags">
                  <span class="select-tag">日线 <span class="select-tag-close">×</span></span>
                  <span class="select-tag">周线 <span class="select-tag-close">×</span></span>
                </div>
                <span class="select-arrow">▼</span>
              </div>
              <div class="select-dropdown-demo-content">
                <div class="select-option-demo">
                  <span class="select-checkbox checked"></span>
                  <span>日线</span>
                </div>
                <div class="select-option-demo">
                  <span class="select-checkbox checked"></span>
                  <span>周线</span>
                </div>
                <div class="select-option-demo">
                  <span class="select-checkbox"></span>
                  <span>月线</span>
                </div>
                <div class="select-option-demo">
                  <span class="select-checkbox"></span>
                  <span>季线</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 第三部分：卡片系统 -->
      <section class="section">
        <h2 class="section-title">3. 卡片系统</h2>
        <div class="demo-block" style="background: transparent; border: none; padding: 0;">
          <!-- 风控规则卡片 -->
          <div style="margin-bottom: 24px;">
            <h3 style="color: #787b86; font-size: 14px; margin-bottom: 12px;">RiskRuleCard 风险规则卡片</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; max-width: 900px;">
              <RiskRuleCard
                :rule="{ rule_id: 'position_limit_001', rule_name: '仓位上限控制', rule_type: 'position_limit', params: { max_ratio: 0.8 }, enabled: true }"
                :isZh="true"
                @toggle="(r) => console.log('toggle', r)"
                @edit="(r) => console.log('edit', r)"
                @backtest="(r) => console.log('backtest', r)"
                @delete="(r) => console.log('delete', r)"
              />
              <RiskRuleCard
                :rule="{ rule_id: 'drawdown_limit_001', rule_name: '最大回撤控制', rule_type: 'drawdown_limit', params: { max_drawdown: 0.15 }, enabled: true }"
                :isZh="true"
                @toggle="(r) => console.log('toggle', r)"
                @edit="(r) => console.log('edit', r)"
                @backtest="(r) => console.log('backtest', r)"
                @delete="(r) => console.log('delete', r)"
              />
              <RiskRuleCard
                :rule="{ rule_id: 'loss_limit_001', rule_name: '日亏损限制', rule_type: 'loss_limit', params: { max_daily_loss: 0.05 }, enabled: false }"
                :isZh="true"
                @toggle="(r) => console.log('toggle', r)"
                @edit="(r) => console.log('edit', r)"
                @backtest="(r) => console.log('backtest', r)"
                @delete="(r) => console.log('delete', r)"
              />
            </div>
          </div>
          <!-- 风险事件卡片 -->
          <div style="margin-bottom: 24px;">
            <h3 style="color: #787b86; font-size: 14px; margin-bottom: 12px;">RiskEventCard 风险事件卡片</h3>
            <div style="max-width: 600px;">
              <RiskEventCard :event="{ event_id: '1', level: 'warning', message: '行业集中度过高', details: '金融行业集中度达到35%，接近30%限额', timestamp: '2024-01-15T10:30:00' }" />
              <RiskEventCard :event="{ event_id: '2', level: 'error', message: '单票持仓超限', details: '600519 持仓达到12%，超过10%限额', timestamp: '2024-01-15T09:15:00' }" />
              <RiskEventCard :event="{ event_id: '3', level: 'info', message: '自动减仓已执行', details: '已将600519减仓至9.8%', timestamp: '2024-01-15T08:00:00' }" />
            </div>
          </div>
          <!-- SummaryCard 汇总卡片 -->
          <div style="margin-bottom: 24px;">
            <h3 style="color: #787b86; font-size: 14px; margin-bottom: 12px;">SummaryCard 汇总卡片</h3>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; max-width: 900px;">
              <SummaryCard
                icon='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>'
                iconColor="blue"
                :value="1850000"
                label="总资产"
                subtitle="现金: ¥46.25万"
                currency
                currencyUnit="wan"
              />
              <SummaryCard
                icon='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
                iconColor="blue"
                :value="1387500"
                label="总市值"
                subtitle="仓位: 75.0%"
                currency
                currencyUnit="wan"
              />
              <SummaryCard
                icon='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>'
                iconColor="red"
                valueColor="profit"
                :value="125800"
                label="总盈亏"
                subtitle="7.29%"
                currency
                currencyUnit="wan"
              />
              <SummaryCard
                icon='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
                iconColor="orange"
                valueColor="profit"
                :value="18600"
                label="当日盈亏"
                subtitle="持仓数: 12"
                currency
                currencyUnit="wan"
              />
            </div>
          </div>

          <!-- SectorListCard 板块列表 -->
          <div style="margin-bottom: 24px;">
            <h3 style="color: #787b86; font-size: 14px; margin-bottom: 12px;">SectorListCard 板块列表</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; max-width: 800px;">
              <SectorListCard
                :items="[{name: 'AI算力', code: 'BK001', change: 0.0325}, {name: '芯片半导体', code: 'BK002', change: 0.0287}, {name: '机器人', code: 'BK003', change: 0.0256}]"
                type="gainers"
                title="涨幅榜"
                :icon="'<svg viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\'><polyline points=\'18 15 12 9 6 15\'></polyline></svg>'"
              />
              <SectorListCard
                :items="[{name: '银行', code: 'BK101', change: -0.0152}, {name: '房地产', code: 'BK102', change: -0.0138}, {name: '白酒', code: 'BK103', change: -0.0115}]"
                type="losers"
                title="跌幅榜"
                :icon="'<svg viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\'><polyline points=\'6 9 12 15 18 9\'></polyline></svg>'"
              />
              <SectorListCard
                :items="[{name: '科技', code: 'BK201', weight: 0.35, change: 0.012}, {name: '新能源', code: 'BK202', weight: 0.25, change: -0.005}, {name: '医药', code: 'BK203', weight: 0.15, change: 0.008}]"
                type="my"
                title="持仓板块"
                :icon="'<svg viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\'><path d=\'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z\'></path></svg>'"
                :show-rank="false"
                summary="持仓集中在 科技、新能源、医药"
              />
            </div>
          </div>

          <!-- ModeSwitch 模式切换 -->
          <div style="margin-bottom: 24px;">
            <h3 style="color: #787b86; font-size: 14px; margin-bottom: 12px;">ModeSwitch 模式切换</h3>
            <div style="display: flex; gap: 16px; align-items: center;">
              <ModeSwitch v-model="modeValue" :options="modeOptions" />
              <span style="color: #787b86; font-size: 12px;">当前: {{ modeValue }}</span>
            </div>
          </div>

          <!-- RefreshButton 刷新按钮 -->
          <div style="margin-bottom: 24px;">
            <h3 style="color: #787b86; font-size: 14px; margin-bottom: 12px;">RefreshButton 刷新按钮</h3>
            <div style="display: flex; gap: 16px; align-items: center;">
              <RefreshButton :loading="false" label="刷新" />
              <RefreshButton :loading="true" label="加载中..." />
              <RefreshButton :loading="false" size="small" />
              <RefreshButton :loading="true" size="small" />
            </div>
          </div>

          <!-- ActionButton 操作按钮 -->
          <div style="margin-bottom: 24px;">
            <h3 style="color: #787b86; font-size: 14px; margin-bottom: 12px;">ActionButton 操作按钮</h3>
            <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 12px;">
              <ActionButton type="primary" label="主要按钮" />
              <ActionButton type="success" label="成功按钮" />
              <ActionButton type="warning" label="警告按钮" />
              <ActionButton type="danger" label="危险按钮" />
              <ActionButton type="default" label="默认按钮" />
            </div>
            <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 12px;">
              <ActionButton type="primary" size="small" label="小按钮" />
              <ActionButton type="success" size="medium" label="中按钮" />
              <ActionButton type="warning" size="large" label="大按钮" />
            </div>
            <div style="display: flex; gap: 12px; align-items: center;">
              <ActionButton type="primary" :loading="true" label="加载中" />
              <ActionButton type="default" disabled label="禁用" />
              <ActionButton type="primary" icon-only :icon="'<svg viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\'><line x1=\'12\' y1=\'5\' x2=\'12\' y2=\'19\'></line><line x1=\'5\' y1=\'12\' x2=\'19\' y2=\'12\'></line></svg>'" />
            </div>
          </div>

          <!-- PeriodSelector 周期选择 -->
          <div style="margin-bottom: 24px;">
            <h3 style="color: #787b86; font-size: 14px; margin-bottom: 12px;">PeriodSelector 周期选择</h3>
            <div style="display: flex; gap: 16px; align-items: center;">
              <PeriodSelector v-model="periodValue" :options="periodOptions" />
              <span style="color: #787b86; font-size: 12px;">当前: {{ periodValue }}</span>
            </div>
          </div>

          <!-- ChartToggle 图表切换 -->
          <div style="margin-bottom: 24px;">
            <h3 style="color: #787b86; font-size: 14px; margin-bottom: 12px;">ChartToggle 图表切换</h3>
            <div style="display: flex; gap: 8px;">
              <ChartToggle
                :active="chartType === 'bar'"
                :icon="'<svg viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\'><line x1=\'18\' y1=\'20\' x2=\'18\' y2=\'10\'></line><line x1=\'12\' y1=\'20\' x2=\'12\' y2=\'4\'></line><line x1=\'6\' y1=\'20\' x2=\'6\' y2=\'14\'></line></svg>'"
                title="柱状图"
                @click="chartType = 'bar'"
              />
              <ChartToggle
                :active="chartType === 'line'"
                :icon="'<svg viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\'><polyline points=\'22 12 18 12 15 21 9 3 6 12 2 12\'></polyline></svg>'"
                title="折线图"
                @click="chartType = 'line'"
              />
              <ChartToggle
                :active="chartType === 'pie'"
                :icon="'<svg viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\'><path d=\'M21.21 15.89A10 10 0 1 1 8 2.83\'></path><path d=\'M22 12A10 10 0 0 0 12 2v10z\'></path></svg>'"
                title="饼图"
                @click="chartType = 'pie'"
              />
            </div>
          </div>

          <div class="card-grid card-grid-4">
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">基础卡片</h3>
              </div>
              <div class="card-body">
                <p>这是一个普通的卡片，没有交互效果。</p>
              </div>
            </div>
            <div class="card card-interactive">
              <div class="card-header">
                <h3 class="card-title">可交互卡片</h3>
                <span class="badge badge-primary">NEW</span>
              </div>
              <div class="card-body">
                <p>鼠标悬停会有浮起效果和边框高亮。</p>
              </div>
            </div>
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">带副标题</h3>
                <p class="card-subtitle">这是副标题说明</p>
              </div>
              <div class="card-body">
                <p>卡片内容区域。</p>
              </div>
              <div class="card-footer">
                <button class="btn btn-ghost btn-sm">取消</button>
                <button class="btn btn-primary btn-sm">确定</button>
              </div>
            </div>
            <!-- 可开关卡片 -->
            <div class="card card-with-switch">
              <div class="card-header">
                <h3 class="card-title">风控规则</h3>
                <label class="switch">
                  <input type="checkbox" checked />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="card-body">
                <p>右上角带开关的卡片，用于启用/禁用功能。</p>
              </div>
              <div class="card-footer">
                <button class="btn btn-ghost btn-sm">编辑</button>
                <button class="btn btn-primary btn-sm">保存</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 第四部分：标签页 -->
      <section class="section">
        <h2 class="section-title">4. 标签页（下划线样式）</h2>
        <div class="demo-block" style="background: transparent; border: none; padding: 0;">
          <!-- 下划线风格标签页 -->
          <div class="tabs-underline">
            <div class="tab-underline is-active">标签一</div>
            <div class="tab-underline">标签二</div>
            <div class="tab-underline">标签三</div>
          </div>
          <div class="tab-content">
            <p>标签页内容区域 - 当前显示标签一的内容</p>
          </div>
        </div>
      </section>

      <!-- 第五部分：进度条 -->
      <section class="section">
        <h2 class="section-title">5. 进度条</h2>
        <div class="demo-block">
          <div class="demo-row">
            <span class="demo-label">基础进度条：</span>
            <div class="progress-wrapper" style="flex: 1;">
              <div class="progress-header">
                <span class="progress-label">进度</span>
                <span class="progress-value">65%</span>
              </div>
              <div class="progress">
                <div class="progress-bar" style="width: 65%;"></div>
              </div>
            </div>
          </div>
          <div class="demo-row">
            <span class="demo-label">小型进度条：</span>
            <div class="progress progress-sm" style="flex: 1;">
              <div class="progress-bar" style="width: 40%;"></div>
            </div>
          </div>
          <div class="demo-row">
            <span class="demo-label">渐变进度条：</span>
            <div style="flex: 1;">
              <div class="progress" style="height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                <div style="width: 80%; height: 100%; border-radius: 5px; background: linear-gradient(90deg, #ef5350, #ff8a80);"></div>
              </div>
            </div>
          </div>
          <div class="demo-row">
            <span class="demo-label">风险渐变：</span>
            <div style="flex: 1;">
              <div class="progress" style="height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                <div style="width: 60%; height: 100%; border-radius: 5px; background: linear-gradient(90deg, #26a69a, #5ce5a9);"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 第六部分：滑杆 -->
      <section class="section">
        <h2 class="section-title">6. 滑杆（数值联动）</h2>
        <div class="demo-block">
          <div class="slider">
            <!-- 使用原生 input range 实现交互 -->
            <input
              type="range"
              min="0"
              max="100"
              v-model="sliderValue"
              class="slider-input"
              @input="updateSliderValue"
            />
            <div class="slider-track">
              <div class="slider-fill" :style="{ width: sliderValue + '%', background: getFactorQualityColor(sliderValue) }"></div>
              <div class="slider-thumb" :style="{ left: sliderValue + '%', borderColor: getFactorQualityColor(sliderValue), background: getFactorQualityColor(sliderValue) }">
                <div class="slider-thumb-value" :style="{ color: getFactorQualityColor(sliderValue) }">
                  {{ sliderValue }}
                </div>
              </div>
            </div>
            <div class="slider-labels">
              <span>0</span>
              <span>50</span>
              <span>100</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 第七部分：评分卡片 -->
      <section class="section">
        <h2 class="section-title">7. 评分卡片（颜色与分数联动，含ABCD等级）</h2>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
          <ScoreCard
            v-for="(card, index) in scoreCards"
            :key="index"
            :label="card.label"
            :score="card.score"
            :show-bar="true"
          />
        </div>
      </section>

      <!-- 第八部分：仪表盘 -->
      <section class="section">
        <h2 class="section-title">8. 指标卡片（参考风险监控）</h2>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px;">
          <MetricCard
            :icon="WalletOutline"
            value="8524"
            label="总资产"
            :trend="5.2"
            suffix="万"
            :precision="0"
          />
          <MetricCard
            :icon="AnalyticsOutline"
            value="2340"
            label="今日收益"
            :trend="5.2"
            suffix="万"
            :precision="0"
            icon-color="#ef5350"
          />
          <MetricCard
            :icon="AnalyticsOutline"
            value="890"
            label="今日亏损"
            :trend="-3.1"
            suffix="万"
            :precision="0"
            icon-color="#26a69a"
          />
          <MetricCard
            :icon="SpeedometerOutline"
            value="156"
            label="运行策略"
            :trend="12"
            :precision="0"
            icon-color="#ff9800"
          />
        </div>
        <!-- 风险仪表盘 -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
          <div class="overview-card" style="display: flex; flex-direction: column; align-items: center;">
            <RiskGauge :value="12.5" :max="100" label="VaR(95%)" :size="100" />
          </div>
          <MetricCard
              :icon="SpeedometerOutline"
              value="-8.2"
              label="CVaR(95%)"
              :trend="-2.1"
              suffix="%"
              icon-color="#ff9800"
            />
            <MetricCard
              :icon="SpeedometerOutline"
              value="1.12"
              label="Beta"
              :trend="0.1"
              icon-color="#2962ff"
            />
            <MetricCard
              :icon="AnalyticsOutline"
              value="-15.3"
              label="当前回撤"
              :trend="-1.2"
              suffix="%"
              icon-color="#9c27b0"
            />
          </div>
      </section>

      <!-- 第九点五部分：综合风险评分仪表盘 -->
      <section class="section">
        <h2 class="section-title">9.5 综合风险评分仪表盘</h2>
        <div class="demo-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
          <!-- 低风险示例 -->
          <RiskScoreGauge
            :score="25"
            :dimensions="[
              { name: '仓位风险', score: 5, maxScore: 25 },
              { name: '回撤风险', score: 8, maxScore: 25 },
              { name: 'VaR/CVaR', score: 6, maxScore: 25 },
              { name: 'Beta/因子', score: 6, maxScore: 25 }
            ]"
          />
          <!-- 中风险示例 -->
          <RiskScoreGauge
            :score="55"
            :dimensions="[
              { name: '仓位风险', score: 15, maxScore: 25 },
              { name: '回撤风险', score: 12, maxScore: 25 },
              { name: 'VaR/CVaR', score: 18, maxScore: 25 },
              { name: 'Beta/因子', score: 10, maxScore: 25 }
            ]"
          />
          <!-- 高风险示例 -->
          <RiskScoreGauge
            :score="82"
            :dimensions="[
              { name: '仓位风险', score: 22, maxScore: 25 },
              { name: '回撤风险', score: 20, maxScore: 25 },
              { name: 'VaR/CVaR', score: 22, maxScore: 25 },
              { name: 'Beta/因子', score: 18, maxScore: 25 }
            ]"
          />
        </div>
      </section>

      <!-- 第九点六部分：VaR/CVaR 分析卡片 -->
      <section class="section">
        <h2 class="section-title">9.6 VaR/CVaR 分析卡片</h2>
        <div class="demo-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
          <VaRCVaRCard :var95="0.015" :cvar95="0.022" />
          <VaRCVaRCard :var95="0.035" :cvar95="0.055" />
          <VaRCVaRCard :var95="0.065" :cvar95="0.095" />
        </div>
      </section>

      <!-- 第九点六五部分：持仓风险指标卡片 -->
      <section class="section">
        <h2 class="section-title">9.65 持仓风险指标卡片</h2>
        <PositionRiskCard />
      </section>

      <!-- 第九点六六部分：组合分析指标卡片 -->
      <section class="section">
        <h2 class="section-title">9.66 组合分析指标卡片</h2>
        <PortfolioAnalysisCard />
      </section>

      <!-- 第九点七部分：因子暴露分析卡片 -->
      <section class="section">
        <h2 class="section-title">9.7 因子暴露分析卡片</h2>
        <div class="demo-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
          <FactorExposureCard :factors="[
            { name: '市值', value: 0.35 },
            { name: '价值', value: -0.22 },
            { name: '动量', value: 0.18 },
            { name: '质量', value: -0.15 },
            { name: '波动', value: 0.28 }
          ]" />
          <FactorExposureCard :factors="[
            { name: '市值', value: -0.45 },
            { name: '价值', value: 0.38 },
            { name: '动量', value: -0.25 },
            { name: '质量', value: 0.52 },
            { name: '波动', value: -0.18 }
          ]" />
        </div>
      </section>

      <!-- 第九部分：雷达图卡片 -->
      <section class="section">
        <h2 class="section-title">9. 雷达图卡片（中大型）</h2>
        <FactorQualityRadar
          title="因子库整体质量"
          :indicator="[
            { name: '平均IC', max: 100 },
            { name: 'IR比率', max: 100 },
            { name: '通过率', max: 100 },
            { name: '因子数量', max: 100 }
          ]"
          :indicator-values="[0.035, 0.85, 0.72, 150]"
          :data="[
            {
              name: '当前因子库',
              value: [75, 68, 82, 90],
              color: '#409ee1',
              areaColor: 'rgba(64, 158, 225, 0.3)',
              lineType: 'solid'
            },
            {
              name: '行业基准',
              value: [60, 55, 70, 80],
              color: '#ff9800',
              areaColor: 'rgba(255, 152, 0, 0.2)',
              lineType: 'dashed'
            }
          ]"
        />
        <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px;">
          <FactorCard :rank="1" name="alpha158_001" :ic="0.056" :ir="0.82" :t-stat="3.5" status="pass" size="large" />
          <FactorCard :rank="2" name="alpha158_002" :ic="0.043" :ir="0.65" :t-stat="2.8" status="pass" size="large" />
          <FactorCard :rank="3" name="alpha360_001" :ic="0.028" :ir="0.42" :t-stat="1.9" status="fail" size="large" />
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px;">
          <FactorCard :rank="1" name="alpha158_001" :ic="0.056" :ir="0.82" :t-stat="3.5" status="pass" size="small" />
          <FactorCard :rank="2" name="alpha158_002" :ic="0.043" :ir="0.65" :t-stat="2.8" status="pass" size="small" />
          <FactorCard :rank="3" name="alpha360_001" :ic="0.028" :ir="0.42" :t-stat="1.9" status="fail" size="small" />
          <FactorCard :rank="4" name="technical_001" :ic="0.015" :ir="0.25" :t-stat="1.2" status="fail" size="small" />
        </div>

        <!-- 个体因子综合评估 -->
        <FactorEvaluationCard
          title="个体因子综合评估"
          :indicator="[
            { name: 'IC均值', max: 100 },
            { name: 'IC标准差', max: 100 },
            { name: 'IC最大值', max: 100 },
            { name: 'IC最小值', max: 100 },
            { name: 'IR值', max: 100 },
            { name: '正IC比率', max: 100 },
            { name: 't统计量', max: 100 },
            { name: 'p值', max: 100 },
            { name: '单调性', max: 100 },
            { name: '稳定性', max: 100 }
          ]"
          :indicator-values="[0.035, 0.02, 0.08, -0.02, 1.5, 0.65, 2.5, 0.03, 0.75, 0.8]"
          :data="[
            {
              name: '当前因子',
              value: [75, 60, 80, 55, 70, 85, 65, 50, 72, 68],
              color: '#409ee1',
              areaColor: 'rgba(64, 158, 225, 0.3)',
              lineType: 'solid'
            },
            {
              name: '行业基准',
              value: [60, 55, 65, 45, 55, 70, 50, 60, 60, 55],
              color: '#ff9800',
              areaColor: 'rgba(255, 152, 0, 0.2)',
              lineType: 'dashed'
            }
          ]"
        />
      </section>

      <!-- 第十部分：状态指示灯 -->
      <section class="section">
        <h2 class="section-title">10. 状态指示灯（信号灯）</h2>
        <div class="demo-block">
          <div class="demo-row">
            <span class="demo-label">组件演示：</span>
            <StatusLight status="normal" />
            <StatusLight status="warning" />
            <StatusLight status="risk" />
          </div>
          <div class="demo-row">
            <span class="demo-label">不同尺寸：</span>
            <StatusLight status="normal" size="small" />
            <StatusLight status="warning" size="medium" />
            <StatusLight status="risk" size="large" />
          </div>
          <div class="demo-row">
            <span class="demo-label">不带文字：</span>
            <StatusLight status="normal" :show-label="false" />
            <StatusLight status="warning" :show-label="false" />
            <StatusLight status="risk" :show-label="false" />
          </div>
        </div>
      </section>

      <!-- 第十部分：涨跌颜色 -->
      <section class="section">
        <h2 class="section-title">10. 涨跌颜色（A股：红涨绿跌）</h2>
        <div class="demo-block">
          <div class="demo-row">
            <span class="demo-label">数值颜色：</span>
            <span class="text-rise" style="font-size: 24px; font-weight: bold;">+5.23%</span>
            <span class="text-fall" style="font-size: 24px; font-weight: bold;">-3.12%</span>
            <span class="text-flat" style="font-size: 24px; font-weight: bold;">0.00%</span>
          </div>
          <div class="demo-row">
            <span class="demo-label">状态徽章：</span>
            <span class="badge badge-success">通过</span>
            <span class="badge badge-error">失败</span>
            <span class="badge badge-warning">警告</span>
            <span class="badge badge-info">信息</span>
          </div>
          <div class="demo-row">
            <span class="demo-label">评级颜色：</span>
            <span class="text-rating-excellent">优秀</span>
            <span class="text-rating-good">良好</span>
            <span class="text-rating-average">一般</span>
            <span class="text-rating-poor">较差</span>
            <span class="text-rating-bad">差</span>
          </div>
        </div>
      </section>

      <!-- 第十部分：表格 -->
      <section class="section">
        <h2 class="section-title">11. 表格</h2>
        <div class="demo-block">
          <el-table :data="tableData" class="data-table" style="width: 100%">
            <el-table-column prop="code" label="股票代码" width="120" />
            <el-table-column prop="name" label="股票名称" width="150" />
            <el-table-column prop="price" label="当前价格" width="120">
              <template #default="{ row }">
                {{ row.price.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="change" label="涨跌幅" width="120">
              <template #default="{ row }">
                <span :class="row.change >= 0 ? 'text-rise' : 'text-fall'">
                  {{ row.change >= 0 ? '+' : '' }}{{ row.change.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.change > 0 ? 'success' : (row.change < 0 ? 'danger' : 'info')" size="small">
                  {{ row.change > 0 ? '上涨' : (row.change < 0 ? '下跌' : '平盘') }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>
      <!-- 第十一部分：因子标签 -->
      <section class="section">
        <h2 class="section-title">12. 因子标签（按类型分类）</h2>
        <div class="demo-block">
          <p style="margin-bottom: 12px; color: var(--text-secondary);">
            因子标签根据因子名称自动识别类型并显示彩色左边框：
            <span style="color: #26a69a;">动量(绿色)</span>、
            <span style="color: #ff9800;">波动率(橙色)</span>、
            <span style="color: #2962ff;">成交量(蓝色)</span>、
            <span style="color: #9c27b0;">技术(紫色)</span>、
            <span style="color: #ef5350;">因子(红色)</span>、
            <span style="color: #787b86;">其他(灰色)</span>
          </p>
          <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;">
            <!-- 动量因子 -->
            <FactorTag factor-name="MA5" :ic="0.052" />
            <FactorTag factor-name="EMA20" :ic="0.048" />
            <FactorTag factor-name="SMA10" :ic="0.045" />
            <FactorTag factor-name="CROSS" :ic="0.038" />
            <!-- 波动率因子 -->
            <FactorTag factor-name="STD20" :ic="0.032" />
            <FactorTag factor-name="VAR30" :ic="0.028" />
            <!-- 成交量因子 -->
            <FactorTag factor-name="VOL5" :ic="0.041" />
            <FactorTag factor-name="VOLUME" :ic="0.039" />
            <!-- 技术因子 -->
            <FactorTag factor-name="RSI14" :ic="0.055" />
            <FactorTag factor-name="MACD" :ic="0.051" />
            <FactorTag factor-name="KDJ" :ic="0.047" />
            <!-- 因子 -->
            <FactorTag factor-name="BETA" :ic="0.035" />
            <FactorTag factor-name="ALPHA" :ic="0.042" />
            <!-- 其他 -->
            <FactorTag factor-name="CLOSE" :ic="0.025" />
            <FactorTag factor-name="OPEN" :ic="0.022" />
          </div>
          <h4 style="margin: 16px 0 8px;">选中状态</h4>
          <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;">
            <FactorTag factor-name="MA5" :ic="0.052" selected />
            <FactorTag factor-name="EMA20" :ic="0.048" selected />
            <FactorTag factor-name="RSI14" :ic="0.055" selected />
          </div>
          <h4 style="margin: 16px 0 8px;">不同尺寸</h4>
          <div style="display: flex; align-items: center; gap: 12px;">
            <FactorTag factor-name="MA5" size="small" />
            <FactorTag factor-name="MA5" size="medium" />
            <FactorTag factor-name="MA5" size="large" />
          </div>
        </div>
      </section>

      <!-- 第十二部分：折叠面板 -->
      <section class="section">
        <h2 class="section-title">13. 折叠面板</h2>
        <div class="demo-block">
          <div class="collapse">
            <div class="collapse-item is-open">
              <div class="collapse-header">
                <span class="collapse-title">第一项 - 点击展开/收起</span>
                <span class="collapse-arrow">▶</span>
              </div>
              <div class="collapse-content">
                <p>这是折叠面板的内容区域，可以放置更多的详细信息。</p>
              </div>
            </div>
            <div class="collapse-item">
              <div class="collapse-header">
                <span class="collapse-title">第二项</span>
                <span class="collapse-arrow">▶</span>
              </div>
              <div class="collapse-content">
                <p>这是第二项的内容。</p>
              </div>
            </div>
            <div class="collapse-item">
              <div class="collapse-header">
                <span class="collapse-title">第三项</span>
                <span class="collapse-arrow">▶</span>
              </div>
              <div class="collapse-content">
                <p>这是第三项的内容。</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 第十二部分：功能入口（三个工作流） -->
      <section class="section">
        <h2 class="section-title">14. 功能入口（顶部工作流按钮）</h2>
        <div class="demo-block" style="background: transparent; border: none; padding: 0;">
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px;">
            <FeatureEntry
              icon="🔬"
              title="研究流程"
              color="#2962ff"
              :stage="5"
              statusText="2 运行中 · 1 排队 · 2 已完成"
            />
            <FeatureEntry
              icon="🎯"
              title="验证流程"
              color="#26a69a"
              :stage="3"
              statusText="1 运行中 · 2 已完成"
            />
            <FeatureEntry
              icon="🚀"
              title="实盘交易"
              color="#ff9800"
              :stage="2"
              statusText="运行中"
            />
          </div>
        </div>
      </section>

      <!-- 第十三部分：任务卡片 -->
      <section class="section">
        <h2 class="section-title">15. 任务卡片</h2>
        <div class="demo-block" style="background: transparent; border: none; padding: 0;">
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; max-width: 800px;">
            <TaskCard
              title="Alpha158因子计算"
              taskId="task_001"
              status="running"
              description="基于Alpha158因子的全市场股票计算任务"
              :configTags="['📊 A股全市场', '🔢 Alpha158', '📅 2024-01 ~ 2024-12']"
              created="创建于 2024-01-15 10:30"
              duration="已运行 2小时30分"
              :showProgress="true"
              :progress="65"
            />
            <TaskCard
              title="LightGBM模型训练"
              taskId="task_002"
              status="completed"
              description="使用LightGBM训练选股模型"
              :configTags="['📊 A股全市场', '🤖 LightGBM', '📅 2024-01 ~ 2024-12']"
              created="创建于 2024-01-14 14:20"
              duration="运行时长 45分"
              :showProgress="true"
              :progress="100"
            />
          </div>
        </div>
      </section>

      <!-- 第十四部分：图表卡片组件（标准复用） -->
      <section class="section">
        <h2 class="section-title">16. 图表卡片组件（标准复用）</h2>
        <div class="demo-block" style="background: transparent; border: none; padding: 0;">
          <!-- 策略评分单独一行 -->
          <div style="margin-bottom: 16px;">
            <ScoreBarChart />
          </div>
          <!-- 图表布局 -->
          <div class="charts-grid-demo">
            <!-- 左侧：收益统计（BarChart3D自带标题，用普通卡片包裹） -->
            <div class="chart-card">
              <BarChart3D />
            </div>

            <!-- 右侧：综合分析 -->
            <div class="analysis-card-demo">
              <!-- 第一行：因子权重 + 性能雷达 -->
              <div class="analysis-row-demo">
                <div class="analysis-left-demo">
                  <DonutChart title="因子权重" />
                </div>
                <div class="analysis-right-demo">
                  <PerformanceRadarCard>
                    <RadarChart />
                  </PerformanceRadarCard>
                </div>
              </div>
              <!-- 第二行：风险指标对比 -->
              <div class="analysis-row-demo full-width-demo">
                <div class="risk-card-demo">
                  <RiskCompareCard>
                    <HorizontalBarChart />
                  </RiskCompareCard>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style>
/* 导入统一设计系统样式 */
@import '@/styles/design-system.css';
@import '@/styles/global.css';
@import '@/styles/components.css';

.style-test-page {
  /* 基础颜色变量 */
  --bg-primary: #131722;
  --bg-secondary: #1e222d;
  --bg-tertiary: #2a2e39;
  --bg-elevated: #363a45;
  --text-primary: #d1d4dc;
  --text-secondary: #787b86;
  --accent-blue: #2962ff;
  --accent-blue-hover: #1e4fd8;
  --accent-blue-light: rgba(41, 98, 255, 0.15);
  --accent-green: #26a69a;
  --accent-red: #ef5350;
  --accent-orange: #ff9800;
  --border-color: #363a45;

  /* 间距变量 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-lg: 16px;
  --spacing-xl: 20px;
  --spacing-2xl: 24px;

  /* 圆角变量 */
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;

  /* 字体变量 */
  --font-size-base: 14px;
  --font-size-sm: 12px;
  --font-size-xs: 11px;
  --font-weight-medium: 500;

  /* 阴影变量 */
  --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.25);

  /* 过渡变量 */
  --transition-base: 0.2s ease;

  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 页面头部 */
.page-header {
  padding: 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* 页面内容 */
.page-content {
  padding: 24px;
}

/* 区块 */
.section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

/* 演示块 */
.demo-block {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
}

.demo-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.demo-row:last-child {
  margin-bottom: 0;
}

.demo-label {
  min-width: 120px;
  font-size: 14px;
  color: var(--text-secondary);
}

/* 计数器样式 */
.input-number {
  display: flex;
  align-items: center;
  background: #1e222d;
  border: 1px solid #363a45;
  border-radius: 6px;
  overflow: hidden;
}

.input-number-btn {
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  color: #d1d4dc;
  cursor: pointer;
  transition: background 0.2s;
}

.input-number-btn:hover {
  background: rgba(41, 98, 255, 0.15);
}

.input-number-input {
  width: 50px;
  height: 32px;
  background: transparent;
  border: none;
  border-left: 1px solid #363a45;
  border-right: 1px solid #363a45;
  color: #d1d4dc;
  text-align: center;
  outline: none;
}

/* 下拉框箭头 */
.select-arrow {
  font-size: 10px;
  transition: transform 0.2s;
}

/* 单元格颜色 */
.cell-positive {
  color: var(--accent-red) !important;
}

.cell-negative {
  color: var(--accent-green) !important;
}

.cell-neutral {
  color: var(--text-secondary) !important;
}

/* 折叠箭头 */
.collapse-arrow {
  font-size: 10px;
  transition: transform 0.2s;
}

.collapse-item.is-open .collapse-arrow {
  transform: rotate(90deg);
}

/* 下拉框样式 */
.select-dropdown-demo {
  position: relative;
  width: 200px;
}

.select-trigger-demo {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #1e222d;
  border: 1px solid #363a45;
  border-radius: 6px;
  color: #d1d4dc;
  cursor: pointer;
  transition: all 0.2s;
}

.select-trigger-demo:hover {
  border-color: #2962ff;
}

.select-dropdown-demo-content {
  display: none;
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #1e222d;
  border: 1px solid #363a45;
  border-radius: 6px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  z-index: 100;
  overflow: hidden;
}

.select-dropdown-demo:hover .select-dropdown-demo-content {
  display: block;
}

.select-option-demo {
  padding: 10px 12px;
  color: #d1d4dc;
  cursor: pointer;
  transition: background 0.15s;
}

.select-option-demo:hover {
  background: rgba(41, 98, 255, 0.15);
}

.select-option-demo.is-selected {
  background: rgba(41, 98, 255, 0.2);
  color: #2962ff;
}

/* 多选下拉框 */
.select-multiple-demo {
  width: 240px;
}

.select-multiple-demo .select-option-demo {
  display: flex;
  align-items: center;
}

.select-multiple-demo .select-option-demo.is-selected {
  background: transparent;
  color: #d1d4dc;
}

.select-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  flex: 1;
}

.select-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  background: #1e222d;
  color: #d1d4dc;
  border-radius: 4px;
  font-size: 12px;
  border: 1px solid #363a45;
}

.select-tag-close {
  cursor: pointer;
  opacity: 0.7;
  font-size: 14px;
  line-height: 1;
}

.select-tag-close:hover {
  opacity: 1;
}

.select-checkbox {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 1px solid #787b86;
  border-radius: 3px;
  margin-right: 8px;
  vertical-align: middle;
  position: relative;
  flex-shrink: 0;
}

.select-checkbox.checked {
  background: #2962ff;
  border-color: #2962ff;
}

.select-checkbox.checked::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 10px;
  line-height: 1;
}

/* 下划线标签页 */
.tabs-underline {
  display: flex;
  gap: 0;
  border-bottom: 1px solid #363a45;
  padding: 0;
}

.tab-underline {
  padding: 12px 20px;
  color: #787b86;
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}

.tab-underline:hover {
  color: #d1d4dc;
}

.tab-underline.is-active {
  color: #2962ff;
}

.tab-underline.is-active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #2962ff;
}

/* 卡片网格 */
.card-grid {
  display: grid;
  gap: 16px;
}

.card-grid-2 { grid-template-columns: repeat(2, 1fr); }
.card-grid-3 { grid-template-columns: repeat(3, 1fr); }
.card-grid-4 { grid-template-columns: repeat(4, 1fr); }

/* 开关组件 */
.switch {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
  flex-shrink: 0;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch .slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #3a3f4b;
  transition: 0.3s;
  border-radius: 20px;
}

.switch .slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

.switch input:checked + .slider {
  background: #2962ff;
}

.switch input:checked + .slider:before {
  transform: translateX(16px);
}

/* 带开关的卡片 */
.card-with-switch .card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-with-switch .card-header .card-title {
  margin: 0;
}

/* 指标卡片（参考风险监控） */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.overview-card {
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  padding: 20px;
}

.overview-card .card-title {
  font-size: 12px;
  font-weight: 600;
  color: #787b86;
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.overview-card .card-metric {
  font-size: 28px;
  font-weight: 700;
  color: #d1d4dc;
  margin-bottom: 4px;
}

.overview-card .card-metric.text-rise {
  color: #ef5350;
}

.overview-card .card-metric.text-fall {
  color: #26a69a;
}

.overview-card .card-desc {
  font-size: 11px;
  color: #575e6a;
}

/* 指标卡片警告/危险状态 */
.overview-card .card-metric.warning {
  color: #ff9800;
}

.overview-card .card-metric.danger {
  color: #ef5350;
}

/* 风险仪表盘 */
.overview-card.risk-gauge {
  grid-column: span 1;
}

.risk-gauge .gauge-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0;
}

.risk-gauge .gauge-value {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 4px;
}

.risk-gauge .gauge-value.low { color: #26a69a; }
.risk-gauge .gauge-value.medium { color: #ff9800; }
.risk-gauge .gauge-value.high { color: #ef5350; }
.risk-gauge .gauge-value.critical { color: #e91e63; }

.risk-gauge .gauge-label {
  font-size: 12px;
  color: #787b86;
  margin-bottom: 12px;
}

.risk-gauge .gauge-bar {
  width: 100%;
  height: 8px;
  background: #2a2e39;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.risk-gauge .gauge-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.risk-gauge .gauge-fill.low { background: #26a69a; }
.risk-gauge .gauge-fill.medium { background: #ff9800; }
.risk-gauge .gauge-fill.high { background: #ef5350; }
.risk-gauge .gauge-fill.critical { background: #e91e63; }

.risk-gauge .gauge-scale {
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: 10px;
  color: #575e6a;
}

/* 滑杆交互样式 */
.slider {
  position: relative;
  padding: 10px 0;
}

.slider-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 30px;
  opacity: 0;
  cursor: pointer;
  z-index: 10;
}

.slider-track {
  position: relative;
  height: 6px;
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
}

.slider-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: #2962ff;
  border-radius: 3px;
  transition: width 0.1s;
}

.slider-thumb {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 18px;
  height: 18px;
  background: white;
  border: 3px solid #2962ff;
  border-radius: 50%;
  cursor: grab;
  transition: transform 0.1s;
  pointer-events: none;
}

.slider-thumb:hover {
  transform: translate(-50%, -50%) scale(1.1);
}

.slider-thumb-value {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translate(-50%, 8px);
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #787b86;
}

.slider-value {
  text-align: center;
  margin-top: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: color 0.2s;
}

/* 下划线加载动画 */
.loading-line {
  display: inline-block;
  width: 20px;
  height: 2px;
  background: currentColor;
  margin-right: 8px;
  border-radius: 1px;
  animation: loading-line 1s ease-in-out infinite;
}

@keyframes loading-line {
  0% { width: 5px; opacity: 0.5; }
  50% { width: 20px; opacity: 1; }
  100% { width: 5px; opacity: 0.5; }
}

/* 状态指示灯 */
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #d1d4dc;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.normal {
  background: #2962ff;
  box-shadow: 0 0 6px rgba(41, 98, 255, 0.5);
}

.status-dot.warning {
  background: #ff9800;
  box-shadow: 0 0 6px rgba(255, 152, 0, 0.5);
}

.status-dot.error {
  background: #9c27b0;
  box-shadow: 0 0 6px rgba(156, 39, 176, 0.5);
}

.status-dot.info {
  background: #2962ff;
  box-shadow: 0 0 6px rgba(41, 98, 255, 0.5);
}

/* 状态徽章 */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.normal {
  background: rgba(41, 98, 255, 0.2);
  color: #2962ff;
}

.status-badge.warning {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
}

.status-badge.error {
  background: rgba(156, 39, 176, 0.2);
  color: #9c27b0;
}

.status-badge.info {
  background: rgba(41, 98, 255, 0.2);
  color: #2962ff;
}

/* 图表卡片 */
.chart-card {
  background: #1e222d;
  border: 1px solid #2a2e39;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

/* 复刻策略页面图表布局 */
.charts-grid-demo {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.analysis-card-demo {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analysis-row-demo {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.analysis-row-demo.full-width-demo {
  width: 100%;
}

.analysis-left-demo,
.analysis-right-demo {
  flex: 1;
  min-width: 200px;
}

.risk-card-demo {
  width: 100%;
  display: flex;
  display: -webkit-flex;
}

/* 固定高度卡片 */
.fixed-height-160 {
  height: 160px;
}

.fixed-height-300 {
  height: 300px;
}
</style>
