<template>
  <div class="position-management-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="phase-badge production">🚀 实盘阶段</div>
          <h1 class="page-title"><i class="fas fa-briefcase"></i> 仓位管理</h1>
          <p class="page-subtitle">实盘持仓查询、分析与监控</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="refreshPositions" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新持仓
          </el-button>
          <el-button @click="showReportDialog = true">
            <el-icon><Document /></el-icon>
            持仓报告
          </el-button>
        </div>
      </div>
    </div>

    <!-- 组合汇总卡片 -->
    <div class="summary-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="card-header">
              <span class="label">总资产</span>
              <el-icon class="icon" color="#409EFF"><Wallet /></el-icon>
            </div>
            <div class="card-value">{{ formatCurrency(summary.total_assets) }}</div>
            <div class="card-sub">现金: {{ formatCurrency(summary.total_cash) }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="card-header">
              <span class="label">总市值</span>
              <el-icon class="icon" color="#67C23A"><TrendCharts /></el-icon>
            </div>
            <div class="card-value">{{ formatCurrency(summary.total_market_value) }}</div>
            <div class="card-sub">仓位: {{ (summary.position_ratio * 100).toFixed(1) }}%</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card" :class="{'profit': summary.total_profit_loss >= 0, 'loss': summary.total_profit_loss < 0}">
            <div class="card-header">
              <span class="label">总盈亏</span>
              <el-icon class="icon" :color="summary.total_profit_loss >= 0 ? '#F56C6C' : '#67C23A'">
                <component :is="summary.total_profit_loss >= 0 ? 'ArrowUp' : 'ArrowDown'" />
              </el-icon>
            </div>
            <div class="card-value">{{ formatCurrency(summary.total_profit_loss) }}</div>
            <div class="card-sub">{{ (summary.total_profit_loss_pct * 100).toFixed(2) }}%</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card">
            <div class="card-header">
              <span class="label">当日盈亏</span>
              <el-icon class="icon" color="#E6A23C"><Sunrise /></el-icon>
            </div>
            <div class="card-value">{{ formatCurrency(summary.today_profit_loss) }}</div>
            <div class="card-sub">持仓数: {{ summary.position_count }}</div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 持仓列表 -->
    <div class="positions-section">
      <el-card>
        <template #header>
          <div class="section-header">
            <span>持仓列表</span>
            <el-input
              v-model="searchText"
              placeholder="搜索股票代码/名称"
              style="width: 200px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </template>

        <el-table
          :data="filteredPositions"
          stripe
          style="width: 100%"
          v-loading="loading"
        >
          <el-table-column prop="symbol" label="股票代码" width="120" />
          <el-table-column prop="symbol_name" label="股票名称" width="120" />
          <el-table-column prop="quantity" label="持仓数量" width="100" align="right">
            <template #default="{ row }">
              {{ formatNumber(row.quantity) }}
            </template>
          </el-table-column>
          <el-table-column prop="avg_price" label="成本价" width="100" align="right">
            <template #default="{ row }">
              {{ formatPrice(row.avg_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="current_price" label="现价" width="100" align="right">
            <template #default="{ row }">
              {{ formatPrice(row.current_price) }}
            </template>
          </el-table-column>
          <el-table-column prop="market_value" label="市值" width="120" align="right">
            <template #default="{ row }">
              {{ formatCurrency(row.market_value) }}
            </template>
          </el-table-column>
          <el-table-column prop="profit_loss" label="浮动盈亏" width="120" align="right">
            <template #default="{ row }">
              <span :class="{'profit-text': row.profit_loss >= 0, 'loss-text': row.profit_loss < 0}">
                {{ formatCurrency(row.profit_loss) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="profit_loss_pct" label="盈亏比例" width="100" align="right">
            <template #default="{ row }">
              <span :class="{'profit-text': row.profit_loss_pct >= 0, 'loss-text': row.profit_loss_pct < 0}">
                {{ (row.profit_loss_pct * 100).toFixed(2) }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="change_pct" label="涨跌幅" width="100" align="right">
            <template #default="{ row }">
              <span :class="{'profit-text': row.change_pct >= 0, 'loss-text': row.change_pct < 0}">
                {{ row.change_pct >= 0 ? '+' : '' }}{{ (row.change_pct * 100).toFixed(2) }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewPositionDetail(row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 持仓详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="持仓详情"
      width="800px"
    >
      <div v-if="selectedPosition" class="position-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="股票代码">{{ selectedPosition.symbol }}</el-descriptions-item>
          <el-descriptions-item label="股票名称">{{ selectedPosition.symbol_name }}</el-descriptions-item>
          <el-descriptions-item label="持仓数量">{{ formatNumber(selectedPosition.quantity) }}</el-descriptions-item>
          <el-descriptions-item label="可用数量">{{ formatNumber(selectedPosition.available_quantity) }}</el-descriptions-item>
          <el-descriptions-item label="冻结数量">{{ formatNumber(selectedPosition.frozen_quantity) }}</el-descriptions-item>
          <el-descriptions-item label="成本价">{{ formatPrice(selectedPosition.avg_price) }}</el-descriptions-item>
          <el-descriptions-item label="当前价">{{ formatPrice(selectedPosition.current_price) }}</el-descriptions-item>
          <el-descriptions-item label="昨收价">{{ formatPrice(selectedPosition.last_close) }}</el-descriptions-item>
          <el-descriptions-item label="市值">{{ formatCurrency(selectedPosition.market_value) }}</el-descriptions-item>
          <el-descriptions-item label="成本金额">{{ formatCurrency(selectedPosition.cost_amount) }}</el-descriptions-item>
          <el-descriptions-item label="浮动盈亏">
            <span :class="{'profit-text': selectedPosition.profit_loss >= 0, 'loss-text': selectedPosition.profit_loss < 0}">
              {{ formatCurrency(selectedPosition.profit_loss) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="盈亏比例">
            <span :class="{'profit-text': selectedPosition.profit_loss_pct >= 0, 'loss-text': selectedPosition.profit_loss_pct < 0}">
              {{ (selectedPosition.profit_loss_pct * 100).toFixed(2) }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="涨跌幅">
            <span :class="{'profit-text': selectedPosition.change_pct >= 0, 'loss-text': selectedPosition.change_pct < 0}">
              {{ selectedPosition.change_pct >= 0 ? '+' : '' }}{{ (selectedPosition.change_pct * 100).toFixed(2) }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedPosition.status)">
              {{ getStatusText(selectedPosition.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(selectedPosition.updated_at) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 持仓报告对话框 -->
    <el-dialog
      v-model="showReportDialog"
      title="持仓分析报告"
      width="1000px"
    >
      <div v-loading="loadingReport">
        <el-descriptions v-if="report" :column="2" border>
          <el-descriptions-item label="总收益率">
            {{ (report.analysis?.total_return * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="年化收益率">
            {{ (report.analysis?.annual_return * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="最大回撤">
            {{ (report.analysis?.max_drawdown * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="最大盈利">
            {{ (report.analysis?.max_profit * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="波动率">
            {{ (report.analysis?.volatility * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="Beta系数">
            {{ report.analysis?.beta?.toFixed(2) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Document,
  Wallet,
  TrendCharts,
  ArrowUp,
  ArrowDown,
  Sunrise,
  Search
} from '@element-plus/icons-vue'

// 状态
const loading = ref(false)
const loadingReport = ref(false)
const searchText = ref('')
const showDetailDialog = ref(false)
const showReportDialog = ref(false)
const selectedPosition = ref<any>(null)

// 数据
const summary = ref<any>({
  total_assets: 0,
  total_cash: 0,
  total_market_value: 0,
  total_profit_loss: 0,
  total_profit_loss_pct: 0,
  today_profit_loss: 0,
  position_count: 0,
  position_ratio: 0
})

const positions = ref<any[]>([])
const report = ref<any>(null)

// 计算属性
const filteredPositions = computed(() => {
  if (!searchText.value) return positions.value
  const search = searchText.value.toLowerCase()
  return positions.value.filter(p =>
    p.symbol.toLowerCase().includes(search) ||
    p.symbol_name.toLowerCase().includes(search)
  )
})

// 格式化函数
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(value)
}

const formatNumber = (value: number) => {
  return new Intl.NumberFormat('zh-CN').format(value)
}

const formatPrice = (value: number) => {
  return value.toFixed(2)
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'normal': 'success',
    'suspended': 'warning',
    'risk_limit': 'danger',
    'forced_close': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'normal': '正常',
    'suspended': '停牌',
    'risk_limit': '风险限制',
    'forced_close': '强平'
  }
  return statusMap[status] || status
}

// API调用
const API_BASE = '/api/v1/production/position'

const refreshPositions = async () => {
  loading.value = true
  try {
    // 获取组合汇总
    const summaryRes = await fetch(`${API_BASE}/portfolio-summary?account_id=default`)
    const summaryData = await summaryRes.json()
    if (summaryData.code === 200) {
      summary.value = summaryData.data
    }

    // 获取持仓列表
    const positionsRes = await fetch(`${API_BASE}/list?account_id=default&force_refresh=true`)
    const positionsData = await positionsRes.json()
    if (positionsData.code === 200) {
      positions.value = positionsData.data.positions
    }

    ElMessage.success('持仓刷新成功')
  } catch (error: any) {
    ElMessage.error('刷新失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const viewPositionDetail = async (position: any) => {
  selectedPosition.value = position
  showDetailDialog.value = true
}

const loadReport = async () => {
  loadingReport.value = true
  try {
    const res = await fetch(`${API_BASE}/report?account_id=default`)
    const data = await res.json()
    if (data.code === 200) {
      report.value = data.data
    }
  } catch (error: any) {
    ElMessage.error('加载报告失败: ' + error.message)
  } finally {
    loadingReport.value = false
  }
}

// 生命周期
onMounted(() => {
  refreshPositions()
})
</script>

<style scoped>
.position-management-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.phase-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
}

.phase-badge.production {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  color: white;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.page-subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.summary-section {
  margin-bottom: 16px;
}

.summary-card {
  text-align: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.card-header .label {
  font-size: 14px;
  color: #909399;
}

.card-header .icon {
  font-size: 24px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.card-sub {
  font-size: 12px;
  color: #909399;
}

.summary-card.profit .card-value {
  color: #F56C6C;
}

.summary-card.loss .card-value {
  color: #67C23A;
}

.positions-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profit-text {
  color: #F56C6C;
}

.loss-text {
  color: #67C23A;
}

.position-detail {
  padding: 10px;
}
</style>
