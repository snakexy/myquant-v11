<template>
  <div class="data-cleaning-config">
    <!-- 空状态提示 -->
    <div v-if="!showQualityReport" class="empty-state">
      <div class="empty-icon">
        <font-awesome-icon icon="database" />
      </div>
      <div class="empty-text">
        <h4>暂无数据清洗结果</h4>
        <p>请先执行工作流以获取数据清洗结果</p>
      </div>
    </div>

    <!-- 数据质量报告 -->
    <div class="config-section" v-if="showQualityReport">
      <h4 class="section-title">
        <font-awesome-icon icon="chart-pie" />
        数据质量报告
      </h4>

      <div class="quality-report-tabs">
        <button
          v-for="tab in qualityTabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- 原始数据概览 -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <div class="quality-overview">
          <div class="overview-grid">
            <div class="overview-item">
              <div class="overview-label">原始数据行数</div>
              <div class="overview-value">{{ formatNumber(qualityReport.originalRows) }}</div>
            </div>
            <div class="overview-item" v-if="qualityReport.originalColumns > 0">
              <div class="overview-label">原始数据列数</div>
              <div class="overview-value">{{ qualityReport.originalColumns }}</div>
            </div>
            <div class="overview-item">
              <div class="overview-label">数据时间范围</div>
              <div class="overview-value">{{ qualityReport.dateRange }}</div>
            </div>
            <div class="overview-item">
              <div class="overview-label">标的数量</div>
              <div class="overview-value">{{ qualityReport.stockCount + qualityReport.indexCount }}</div>
            </div>
          </div>

          <!-- 分组显示：股票和指数 -->
          <div v-if="qualityReport.stockCount > 0 || qualityReport.indexCount > 0" class="stock-groups">
            <div class="group-item" v-if="qualityReport.stockCount > 0">
              <div class="group-icon" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
                <font-awesome-icon icon="building" />
              </div>
              <div class="group-content">
                <div class="group-label">股票数量</div>
                <div class="group-value">{{ qualityReport.stockCount }}</div>
              </div>
            </div>
            <div class="group-item" v-if="qualityReport.indexCount > 0">
              <div class="group-icon" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                <font-awesome-icon icon="chart-area" />
              </div>
              <div class="group-content">
                <div class="group-label">指数数量</div>
                <div class="group-value">{{ qualityReport.indexCount }}</div>
              </div>
            </div>
          </div>

          <!-- 每只标的平均数据量 -->
          <div v-if="qualityReport.stockCount > 0 || qualityReport.indexCount > 0" class="detailed-stats">
            <h5>详细统计</h5>
            <div class="stats-grid-compact">
              <!-- 🔧 新增：日线数据行数 -->
              <div class="stat-compact-item" v-if="qualityReport.dailyRecords > 0">
                <div class="stat-compact-icon" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                  <font-awesome-icon icon="calendar-alt" />
                </div>
                <div class="stat-compact-content">
                  <div class="stat-compact-label">日线数据</div>
                  <div class="stat-compact-value">{{ formatNumber(qualityReport.dailyRecords) }} 行</div>
                </div>
              </div>
              <!-- 🔧 新增：分钟线数据行数 -->
              <div class="stat-compact-item" v-if="qualityReport.intradayRecords > 0">
                <div class="stat-compact-icon" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);">
                  <font-awesome-icon icon="clock" />
                </div>
                <div class="stat-compact-content">
                  <div class="stat-compact-label">分钟线数据</div>
                  <div class="stat-compact-value">{{ formatNumber(qualityReport.intradayRecords) }} 行</div>
                </div>
              </div>
              <div class="stat-compact-item">
                <div class="stat-compact-icon" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
                  <font-awesome-icon icon="list-ol" />
                </div>
                <div class="stat-compact-content">
                  <div class="stat-compact-label">每只标的平均行数</div>
                  <div class="stat-compact-value">{{ formatNumber(Math.round(safeDivide(qualityReport.originalRows, (qualityReport.stockCount + qualityReport.indexCount), 0))) }}</div>
                </div>
              </div>
              <div class="stat-compact-item" v-if="qualityReport.originalColumns > 0">
                <div class="stat-compact-icon" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                  <font-awesome-icon icon="chart-pie" />
                </div>
                <div class="stat-compact-content">
                  <div class="stat-compact-label">数据密度</div>
                  <div class="stat-compact-value">{{ formatPercent(qualityReport.validRows, (qualityReport.originalRows * qualityReport.originalColumns), 1) }}%</div>
                </div>
              </div>
              <div class="stat-compact-item" v-if="qualityReport.originalColumns > 0">
                <div class="stat-compact-icon" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                  <font-awesome-icon icon="cubes" />
                </div>
                <div class="stat-compact-content">
                  <div class="stat-compact-label">总数据点</div>
                  <div class="stat-compact-value">{{ formatNumber(qualityReport.originalRows * qualityReport.originalColumns) }}</div>
                </div>
              </div>
              <div class="stat-compact-item" v-if="qualityReport.originalColumns > 0">
                <div class="stat-compact-icon" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);">
                  <font-awesome-icon icon="check-double" />
                </div>
                <div class="stat-compact-content">
                  <div class="stat-compact-label">有效数据点</div>
                  <div class="stat-compact-value">{{ formatNumber(qualityReport.validRows * qualityReport.originalColumns) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 简化的数据质量评分 -->
          <div class="quality-score-display">
            <div class="score-circle" :class="getScoreClass(qualityReport.dataQualityScore * 100)">
              <div class="score-number">{{ Math.round(qualityReport.dataQualityScore * 100) }}%</div>
            </div>
            <div class="score-text">
              <h5>数据质量评分</h5>
              <p>{{ getScoreDescription(qualityReport.dataQualityScore * 100) }}</p>
              <!-- 🔧 新增：显示扣分详情 -->
              <div class="score-breakdown" v-if="qualityReport.qualityScoreBreakdown" style="margin-top: 10px; font-size: 12px; color: #666;">
                <div v-for="(item, key) in qualityReport.qualityScoreBreakdown" :key="key" style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                  <span>{{ getScoreLabel(key) }}:</span>
                  <span>{{ Math.round(item.score * 100) }}% (权重{{ (item.weight * 100) }}%)</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 简化的数据分布 -->
          <div class="data-distribution">
            <h5>数据分布</h5>
            <div class="distribution-bars">
              <div class="bar-item">
                <span class="bar-label">有效数据</span>
                <div class="bar-container">
                  <div class="bar-fill valid" :style="{ width: formatPercent(qualityReport.validRows, qualityReport.rowsProcessed, 1) + '%' }"></div>
                </div>
                <span class="bar-value">{{ Math.round(safeDivide(qualityReport.validRows, qualityReport.rowsProcessed, 0) * 100) }}%</span>
              </div>
              <div class="bar-item">
                <span class="bar-label">已删除数据</span>
                <div class="bar-container">
                  <div class="bar-fill removed" :style="{ width: formatPercent(qualityReport.rowsRemoved, qualityReport.rowsProcessed, 1) + '%' }"></div>
                </div>
                <span class="bar-value">{{ Math.round(safeDivide(qualityReport.rowsRemoved, qualityReport.rowsProcessed, 0) * 100) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 清洗统计 -->
      <div v-if="activeTab === 'cleaning'" class="tab-content">
        <div class="cleaning-stats">
          <div class="stats-grid">
            <div class="stat-item highlight">
              <div class="stat-icon">
                <font-awesome-icon icon="database" />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ formatNumber(qualityReport.rowsProcessed) }}</div>
                <div class="stat-label">已处理数据行数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon success">
                <font-awesome-icon icon="check-circle" />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ formatNumber(qualityReport.validRows) }}</div>
                <div class="stat-label">有效数据行数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon warning">
                <font-awesome-icon icon="exclamation-triangle" />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ formatNumber(qualityReport.rowsRemoved) }}</div>
                <div class="stat-label">删除数据行数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon info">
                <font-awesome-icon icon="percentage" />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ Math.round(qualityReport.dataQualityScore * 100) }}%</div>
                <div class="stat-label">数据质量评分</div>
              </div>
            </div>
          </div>

          <!-- 清洗过程可视化 -->
          <div class="process-visualization">
            <h5>数据清洗过程</h5>
            <div class="process-steps">
              <div class="process-step completed">
                <div class="step-number">1</div>
                <div class="step-content">
                  <div class="step-title">原始数据</div>
                  <div class="step-value">{{ formatNumber(qualityReport.rowsProcessed) }} 行</div>
                </div>
              </div>
              <div class="process-step" :class="getDuplicateStepClass(qualityReport.duplicatesRemoved)">
                <div class="step-number">2</div>
                <div class="step-content">
                  <div class="step-title">去重处理</div>
                  <div class="step-value" :class="getDuplicateValueClass(qualityReport.duplicatesRemoved)">
                    {{ qualityReport.duplicatesRemoved > 0 ? `删除 ${formatNumber(qualityReport.duplicatesRemoved)} 行` : '无重复' }}
                  </div>
                </div>
              </div>
              <div class="process-step" :class="getOutlierStepClass(qualityReport.outliersDetected)">
                <div class="step-number">3</div>
                <div class="step-content">
                  <div class="step-title">异常值检测</div>
                  <div class="step-value" :class="getOutlierValueClass(qualityReport.outliersDetected)">
                    {{ qualityReport.outliersDetected > 0 ? `处理 ${formatNumber(qualityReport.outliersDetected)} 个` : '无异常' }}
                  </div>
                </div>
              </div>
              <div class="process-step" :class="getMissingStepClass(qualityReport.missingValuesHandled, qualityReport.rowsProcessed)">
                <div class="step-number">4</div>
                <div class="step-content">
                  <div class="step-title">缺失值处理</div>
                  <div class="step-value" :class="getMissingValueClass(qualityReport.missingValuesHandled, qualityReport.rowsProcessed)">
                    {{ getMissingValueText(qualityReport.missingValuesHandled, qualityReport.rowsProcessed) }}
                  </div>
                </div>
              </div>
              <div class="process-step completed">
                <div class="step-number">5</div>
                <div class="step-content">
                  <div class="step-title">完成清洗</div>
                  <div class="step-value">{{ formatNumber(qualityReport.validRows) }} 行</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 详细清洗统计 -->
          <div class="detailed-stats">
            <h5>详细清洗统计：</h5>
            <div class="stats-list">
              <div class="stats-list-item" v-if="qualityReport.duplicatesRemoved > 0">
                <span class="stats-label">
                  <font-awesome-icon icon="copy" />
                  重复数据删除：
                  <small class="stats-hint">检测并删除完全重复的数据行</small>
                </span>
                <span class="stats-value">{{ qualityReport.duplicatesRemoved }} 行</span>
              </div>
              <div class="stats-list-item" v-if="qualityReport.invalidValuesFixed > 0">
                <span class="stats-label">
                  <font-awesome-icon icon="wrench" />
                  无效值修复：
                  <small class="stats-hint">修正格式错误或超出范围的数值</small>
                </span>
                <span class="stats-value">{{ qualityReport.invalidValuesFixed }} 个</span>
              </div>
              <div class="stats-list-item" v-if="qualityReport.missingValuesHandled > 0">
                <span class="stats-label">
                  <font-awesome-icon icon="fill-drip" />
                  缺失值处理：
                  <small class="stats-hint">
                    所有列空值单元格总数（{{ qualityReport.missingValuesHandled }}个）
                    <span v-if="qualityReport.originalColumns > 0">
                      ≈ {{ Math.round(qualityReport.missingValuesHandled / qualityReport.originalColumns) }}个/列
                    </span>
                  </small>
                </span>
                <span class="stats-value">{{ qualityReport.missingValuesHandled }} 个</span>
              </div>
              <div class="stats-list-item" v-if="qualityReport.outliersDetected > 0">
                <span class="stats-label">
                  <font-awesome-icon icon="exclamation-circle" />
                  异常值检测：
                  <small class="stats-hint">识别并处理偏离正常范围的数值</small>
                </span>
                <span class="stats-value">{{ qualityReport.outliersDetected }} 个</span>
              </div>
              <div class="stats-list-item" v-if="qualityReport.featuresAdded > 0">
                <span class="stats-label">
                  <font-awesome-icon icon="plus-circle" />
                  新增特征：
                  <small class="stats-hint">基于原始数据计算的新指标</small>
                </span>
                <span class="stats-value">{{ qualityReport.featuresAdded }} 个</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据库存储信息 -->
      <div v-if="activeTab === 'storage'" class="tab-content">
        <div class="storage-info">
          <div class="storage-grid">
            <div class="storage-item">
              <div class="storage-label">已存入数据库行数</div>
              <div class="storage-value">{{ formatNumber(qualityReport.storedRows) }}</div>
            </div>
            <div class="storage-item">
              <div class="storage-label">数据库表名称</div>
              <div class="storage-value storage-table-name" :title="qualityReport.tableName">{{ qualityReport.tableName }}</div>
            </div>
            <div class="storage-item">
              <div class="storage-label">存储大小</div>
              <div class="storage-value">{{ formatFileSize(qualityReport.storageSize) }}</div>
            </div>
            <div class="storage-item">
              <div class="storage-label">存储时间</div>
              <div class="storage-value storage-time">{{ formatStorageTime(qualityReport.storageTime) }}</div>
            </div>
          </div>

          <!-- 存储详情 -->
          <div class="storage-details">
            <h5>存储详情：</h5>
            <div class="storage-list">
              <div class="storage-list-item">
                <span class="storage-list-label">数据压缩比：</span>
                <span class="storage-list-value">{{ qualityReport.compressionRatio }}%</span>
              </div>
              <div class="storage-list-item">
                <span class="storage-list-label">索引创建状态：</span>
                <span class="storage-list-value">{{ qualityReport.indexStatus }}</span>
              </div>
              <div class="storage-list-item">
                <span class="storage-list-label">数据备份状态：</span>
                <span class="storage-list-value">{{ qualityReport.backupStatus }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 缺失值分析 -->
      <div v-if="activeTab === 'missing'" class="tab-content">
        <div class="missing-analysis">
          <div class="missing-overview">
            <div class="missing-chart-placeholder">
              <div class="placeholder-icon">
                <font-awesome-icon icon="chart-bar" />
              </div>
              <div class="placeholder-text">
                <h4>缺失值分布图表</h4>
                <p>各列缺失值统计可视化</p>
              </div>
            </div>
            <div class="missing-stats">
              <div class="missing-stat">
                <div class="missing-label">总缺失值</div>
                <div class="missing-value">{{ formatNumber(qualityReport.totalMissing) }}</div>
              </div>
              <div class="missing-stat">
                <div class="missing-label">缺失率</div>
                <div class="missing-value">{{ qualityReport.missingRate }}%</div>
              </div>
            </div>
          </div>

          <!-- 各列缺失值详情 -->
          <div class="missing-details" v-if="qualityReport.columnMissingStats">
            <h5>各列缺失值统计：</h5>
            <div class="missing-table">
              <table>
                <thead>
                  <tr>
                    <th>列名</th>
                    <th>缺失数量</th>
                    <th>缺失率</th>
                    <th>处理方式</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="stat in qualityReport.columnMissingStats" :key="stat.column">
                    <td>{{ stat.column }}</td>
                    <td>{{ formatNumber(stat.missingCount) }}</td>
                    <td>{{ stat.missingRate }}%</td>
                    <td>{{ stat.handlingMethod }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, withDefaults } from 'vue'

// 数据质量报告接口
interface QualityReport {
  // 原始数据概览
  originalRows: number
  originalColumns: number
  dateRange: string
  stockCount: number
  indexCount: number  // 指数数量
  dailyRecords: number  // 🔧 新增：日线数据行数
  intradayRecords: number  // 🔧 新增：分钟线数据行数

  // 清洗统计
  rowsProcessed: number
  validRows: number
  rowsRemoved: number
  duplicatesRemoved: number
  invalidValuesFixed: number
  missingValuesHandled: number
  outliersDetected: number
  featuresAdded: number
  dataQualityScore: number

  // 数据库存储信息
  storedRows: number
  tableName: string
  storageSize: number
  storageTime: string
  compressionRatio: number
  indexStatus: string
  backupStatus: string

  // 缺失值分析
  totalMissing: number
  missingRate: number
  columnMissingStats?: Array<{
    column: string
    missingCount: number
    missingRate: number
    handlingMethod: string
  }>
  qualityScoreBreakdown?: {
    // 🔧 新增：质量评分分解
    completeness?: { score: number; weight: number; contribution: number }
    accuracy?: { score: number; weight: number; contribution: number }
    consistency?: { score: number; weight: number; contribution: number }
    timeliness?: { score: number; weight: number; contribution: number }
  }
}

// Props
interface Props {
  modelValue?: any
  nodeData?: any  // 添加 nodeData prop 来接收节点的执行结果数据
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => ({}),
  nodeData: null
})

// 数据质量报告数据
const showQualityReport = ref(false)
const activeTab = ref('overview')
const qualityReport = ref<QualityReport>({
  originalRows: 0,
  originalColumns: 0,
  dateRange: '',
  stockCount: 0,
  indexCount: 0,
  dailyRecords: 0,  // 🔧 新增
  intradayRecords: 0,  // 🔧 新增
  rowsProcessed: 0,
  validRows: 0,
  rowsRemoved: 0,
  duplicatesRemoved: 0,
  invalidValuesFixed: 0,
  missingValuesHandled: 0,
  outliersDetected: 0,
  featuresAdded: 0,
  dataQualityScore: 0,
  storedRows: 0,
  tableName: '',
  storageSize: 0,
  storageTime: '',
  compressionRatio: 0,
  indexStatus: '',
  backupStatus: '',
  totalMissing: 0,
  missingRate: 0,
  columnMissingStats: []
})

// 质量报告标签页
const qualityTabs = [
  { key: 'overview', label: '数据概览' },
  { key: 'cleaning', label: '清洗统计' },
  { key: 'storage', label: '存储信息' },
  { key: 'missing', label: '缺失值分析' }
]

// 方法
const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toLocaleString()
}

// 安全的除法运算，避免NaN
const safeDivide = (numerator: number, denominator: number, defaultValue: number = 0): number => {
  if (denominator === 0 || !isFinite(denominator)) {
    return defaultValue
  }
  if (!isFinite(numerator)) {
    return defaultValue
  }
  return numerator / denominator
}

// 安全的百分比格式化
const formatPercent = (numerator: number, denominator: number, decimals: number = 1): string => {
  const ratio = safeDivide(numerator, denominator, 0)
  return (ratio * 100).toFixed(decimals)
}

// 计算缺失值率（占总单元格数的百分比）
const getMissingRate = (missingCount: number, rowCount: number): number => {
  if (rowCount === 0) return 0
  // 🔧 修复：应该除以总单元格数（行数 × 列数），而不是只除以行数
  // 假设标准OHLCV数据有8列
  const columnCount = qualityReport.value.originalColumns || 8
  const totalCells = rowCount * columnCount
  if (totalCells === 0) return 0
  return (missingCount / totalCells) * 100
}

// 缺失值处理 - 步骤状态
const getMissingStepClass = (missingCount: number, rowCount: number) => {
  const rate = getMissingRate(missingCount, rowCount)
  if (missingCount === 0) return 'completed'
  if (rate < 5) return 'completed'  // 优秀：少于5%
  if (rate < 15) return 'warning'   // 良好：5-15%
  return 'danger'  // 警告：超过15%
}

// 缺失值处理 - 值的颜色
const getMissingValueClass = (missingCount: number, rowCount: number) => {
  const rate = getMissingRate(missingCount, rowCount)
  if (missingCount === 0) return 'status-excellent'
  if (rate < 5) return 'status-good'
  if (rate < 15) return 'status-warning'
  return 'status-danger'
}

// 缺失值处理 - 显示文本
const getMissingValueText = (missingCount: number, rowCount: number): string => {
  if (missingCount === 0) return '无缺失'
  const rate = getMissingRate(missingCount, rowCount)
  return `处理 ${formatNumber(missingCount)} 个 (${rate.toFixed(1)}%)`
}

// 去重处理 - 步骤状态
const getDuplicateStepClass = (duplicateCount: number) => {
  if (duplicateCount === 0) return 'completed'
  if (duplicateCount < 10) return 'warning'
  return 'danger'
}

// 去重处理 - 值的颜色
const getDuplicateValueClass = (duplicateCount: number) => {
  if (duplicateCount === 0) return 'status-excellent'
  if (duplicateCount < 10) return 'status-good'
  return 'status-warning'
}

// 异常值检测 - 步骤状态
const getOutlierStepClass = (outlierCount: number) => {
  if (outlierCount === 0) return 'completed'
  if (outlierCount < 10) return 'warning'
  return 'danger'
}

// 异常值检测 - 值的颜色
const getOutlierValueClass = (outlierCount: number) => {
  if (outlierCount === 0) return 'status-excellent'
  if (outlierCount < 10) return 'status-good'
  return 'status-warning'
}

const getScoreLabel = (key: string): string => {
  // 🔧 新增：获取评分维度的中文标签
  const labels: Record<string, string> = {
    completeness: '完整性',
    accuracy: '准确性',
    consistency: '一致性',
    timeliness: '及时性'
  }
  return labels[key] || key
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatStorageTime = (time: string) => {
  if (!time) return '未存储'
  try {
    const date = new Date(time)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return time
  }
}

const getScoreClass = (score: number) => {
  if (score >= 90) return 'excellent'
  if (score >= 70) return 'good'
  if (score >= 50) return 'fair'
  return 'poor'
}

const getScoreDescription = (score: number) => {
  if (score >= 90) return '数据质量优秀，无需额外处理'
  if (score >= 70) return '数据质量良好，建议轻微优化'
  if (score >= 50) return '数据质量一般，需要重点处理'
  return '数据质量较差，需要立即处理'
}

// 动态计算日期范围 - 使用更合理的时间范围（一年前到今天）
const today = new Date()
const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate()) // 一年前
const defaultStartDate = oneYearAgo.toISOString().split('T')[0]
const defaultEndDate = today.toISOString().split('T')[0]

// 获取数据质量报告
const fetchQualityReport = async () => {
  try {
    // 调用实际的后端API
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8010/api/v1'
    const nodeId = 'data-cleaning' // 从props中获取节点ID

    // 获取股票代码 - 优先从节点配置中读取
    let stockCodes = '' // 默认为空，让后端使用实际清洗的数据

    // 尝试从节点配置中获取股票代码
    if (props.modelValue?.config?.stockCodes) {
      stockCodes = props.modelValue.config.stockCodes.join(',')
    } else if (props.nodeData?.stockCodes) {
      stockCodes = props.nodeData.stockCodes.join(',')
    } else if (props.nodeData?.content?.stockCodes) {
      stockCodes = props.nodeData.content.stockCodes.join(',')
    }

    console.log('[DataCleaningConfigSimple] 使用股票代码:', stockCodes || '(使用实际清洗数据)')

    const url = new URL(`${apiBase}/data-cleaning/quality-report/${nodeId}`, window.location.origin)
    if (stockCodes) {
      url.searchParams.append('stock_codes', stockCodes)
    }

    const response = await fetch(url.toString())

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`)
    }

    const result = await response.json()

    if (result.code === 200) {
      // 将后端数据转换为前端格式，全部使用真实数据
      const backendReport = result.data
      const dataOverview = backendReport.data_overview || {}

      // 修复字段映射：使用后端实际返回的字段名
      // 🔧 修复：准确计算股票和指数数量（根据交易所和代码范围）
      const stockCodesList = backendReport.stock_codes || []

      // 判断是否为指数代码的函数（支持标准格式和 QLib 格式）
      const isIndexCode = (code: string): boolean => {
        // 标准化代码格式（转为大写）
        const normalizedCode = code.toUpperCase()

        // 提取数字部分和交易所后缀
        let numericPart = ''
        let exchange = ''

        if (normalizedCode.includes('.')) {
          // 标准格式: 000001.SH, 000001.SZ
          const parts = normalizedCode.split('.')
          numericPart = parts[0]
          exchange = parts[1]
        } else if (normalizedCode.length === 7) {
          // QLib 格式: SH000001, SZ000001
          exchange = normalizedCode.substring(0, 2)
          numericPart = normalizedCode.substring(2)
        } else {
          // 其他格式，无法判断
          return false
        }

        // 上海证券交易所指数代码范围
        // 000001-000999: 上证综合指数、上证50、上证180、沪深300等
        // 000688: 科创50
        if (numericPart.startsWith('000') && numericPart.length === 6) {
          const num = parseInt(numericPart)
          if ((num >= 1 && num <= 999) || num === 688) {
            return exchange === 'SH'
          }
        }

        // 深圳证券交易所指数代码范围
        // 399001-399999: 深证成指、深证综指、创业板指等
        if (numericPart.startsWith('399') && numericPart.length === 6) {
          return exchange === 'SZ'
        }

        return false
      }

      // 计算股票和指数数量
      const indexCodesCount = stockCodesList.filter((code: string) => isIndexCode(code)).length
      const stockCodesCount = stockCodesList.length - indexCodesCount

      qualityReport.value = {
        originalRows: backendReport.storage_info?.data_storage?.total_records || dataOverview.total_records || 0,  // 🔧 修复：优先显示存储的数据行数
        originalColumns: dataOverview.data_columns || dataOverview.columns_count || 0,  // 修复：使用正确的字段名
        dateRange: dataOverview.data_time_range || dataOverview.date_range || `${defaultStartDate} 至 ${defaultEndDate}`,  // 修复：使用正确的字段名
        stockCount: stockCodesCount > 0 ? stockCodesCount : (dataOverview.stock_count || 0),  // 修复：优先使用计算值
        indexCount: indexCodesCount,  // 修复：根据股票代码前缀计算指数数量
        dailyRecords: backendReport.storage_info?.data_storage?.daily_records || 0,  // 🔧 新增：日线数据行数
        intradayRecords: backendReport.storage_info?.data_storage?.intraday_records || 0,  // 🔧 新增：分钟线数据行数
        rowsProcessed: backendReport.storage_info?.data_storage?.total_records || dataOverview.total_records || 0,  // 🔧 修复：优先显示存储的数据行数
        validRows: backendReport.storage_info?.data_storage?.total_records || dataOverview.valid_records || 0,  // 🔧 修复：优先显示存储的数据行数
        rowsRemoved: (dataOverview.missing_records || 0) +
                   (dataOverview.duplicate_records || 0) +
                   (dataOverview.outlier_records || 0),
        duplicatesRemoved: backendReport.issue_analysis?.duplicates?.total || 0,
        invalidValuesFixed: 0,  // 后端暂未提供此统计
        missingValuesHandled: backendReport.issue_analysis?.missing_values?.total || 0,
        outliersDetected: backendReport.issue_analysis?.outliers?.total || 0,
        featuresAdded: 0,  // 后端暂未提供此统计
        dataQualityScore: (backendReport.overall_quality_score || 0),  // 🔧 修复：后端返回的是小数形式（0.96），保持原样
        storedRows: backendReport.storage_info?.data_storage?.total_records || 0,
        tableName: backendReport.storage_info?.data_storage?.table_name ||
                   backendReport.storage_info?.data_storage?.location?.split('/').filter(Boolean).pop() || 'stock_data',
        storageSize: backendReport.storage_info?.data_storage?.storage_size_bytes || backendReport.storage_info?.data_storage?.storage_size || 0,  // 修复：优先使用字节数
        storageTime: backendReport.storage_info?.data_storage?.last_updated || new Date().toISOString(),
        compressionRatio: 0,  // 后端暂未提供此统计
        indexStatus: backendReport.storage_info?.index_info?.indexed ?
                    `已创建索引` : '未创建索引',  // 简化显示
        backupStatus: backendReport.storage_info?.backup_storage?.backup_enabled ?
                     `已备份` : '未备份',  // 简化显示
        totalMissing: backendReport.issue_analysis?.missing_values?.total || backendReport.issue_analysis?.missing_values?.total_cells || 0,  // 修复：使用总缺失单元格数
        missingRate: Math.round(((backendReport.issue_analysis?.missing_values?.total_cells || 0) / (dataOverview.total_records || 1)) * 100 * 100) / 100,  // 修复：基于单元格数计算
        columnMissingStats: Object.entries(backendReport.issue_analysis?.missing_values?.by_column || {}).map(([column, data]) => ({
          column,
          missingCount: (data as any)?.count || 0,
          missingRate: Math.round(((data as any)?.count || 0) / (dataOverview.total_records || 1) * 100 * 100) / 100,
          handlingMethod: (data as any)?.handling_method || '插值填充'
        })),
        qualityScoreBreakdown: backendReport.quality_metrics?.score_breakdown || undefined  // 🔧 新增：评分分解
      }
      showQualityReport.value = true
      console.log('成功获取真实数据质量报告:', qualityReport.value)
    } else {
      throw new Error(result.message || '获取数据质量报告失败')
    }
  } catch (error) {
    console.error('获取数据质量报告失败:', error)
    // 不使用模拟数据，显示真实错误状态
    qualityReport.value = {
      originalRows: 0,
      originalColumns: 0,
      dateRange: '无数据',
      stockCount: 0,
      rowsProcessed: 0,
      validRows: 0,
      rowsRemoved: 0,
      duplicatesRemoved: 0,
      invalidValuesFixed: 0,
      missingValuesHandled: 0,
      outliersDetected: 0,
      featuresAdded: 0,
      dataQualityScore: 0,
      storedRows: 0,
      tableName: '无数据',
      storageSize: 0,
      storageTime: '无数据',
      compressionRatio: 0,
      indexStatus: '未创建索引',
      backupStatus: '未备份',
      totalMissing: 0,
      missingRate: 0,
      columnMissingStats: []
    }
    showQualityReport.value = true
  }
}

// 从节点数据加载质量报告
const loadQualityReportFromNodeData = () => {
  if (!props.nodeData) return

  try {
    // 获取节点内容 - 支持多种数据格式
    const nodeContent = props.nodeData.data?.content || props.nodeData.content

    // 检查是否有清洗后的数据
    if (!nodeContent || typeof nodeContent !== 'object') {
      console.log('[DataCleaningConfigSimple] nodeContent为空或不是对象, nodeData:', props.nodeData)
      return
    }
    console.log('[DataCleaningConfigSimple] 从节点数据加载质量报告:', nodeContent)
    console.log('[DataCleaningConfigSimple] nodeContent关键字段:', {
      conversionStatus: nodeContent.conversionStatus,
      originalRows: nodeContent.originalRows,
      originalColumns: nodeContent.originalColumns,
      stockCount: nodeContent.stockCount,
      cleanedRows: nodeContent.cleanedRows
    })

    // 优先使用节点内容中的数据（DataCleaningNode 执行后设置的 node.data.content）
    // 格式: { conversionStatus, qualityScore, completeness, accuracy, consistency, ... }
    if (nodeContent.conversionStatus === 'completed') {
      console.log('[DataCleaningConfigSimple] 解析节点数据内容 - 转换后的数据库报告:', {
        missingCount: nodeContent.missingCount,
        duplicateCount: nodeContent.duplicateCount,
        outlierCount: nodeContent.outlierCount,
        originalRows: nodeContent.originalRows,
        cleanedRows: nodeContent.cleanedRows,
        qualityScore: nodeContent.qualityScore
      })

      // 🔧 修复：显示"转换后的数据库报告"，而不是原始数据的清洗报告
      // 这个报告应该显示最终保存到数据库的数据统计

      const originalRows = nodeContent.originalRows || 0
      const originalColumns = nodeContent.originalColumns || 8  // OHLCV + 其他字段
      const cleanedRows = nodeContent.cleanedRows || 0
      const rowsRemoved = (nodeContent.missingCount || 0) + (nodeContent.duplicateCount || 0) + (nodeContent.outlierCount || 0)

      qualityReport.value = {
        // 🔧 原始数据统计（输入）
        originalRows: originalRows,
        originalColumns: originalColumns,
        dateRange: nodeContent.dateRange || '未指定',
        stockCount: nodeContent.stockCount || 0,
        indexCount: nodeContent.indexCount || 0,

        // 🔧 转换后的数据库统计（输出）
        rowsProcessed: originalRows,  // 处理的总行数
        validRows: cleanedRows,  // 清洗后保存到数据库的行数
        rowsRemoved: rowsRemoved,  // 删除的行数

        // 🔧 清洗过程中处理的问题数量
        duplicatesRemoved: nodeContent.duplicateCount || 0,
        invalidValuesFixed: 0,  // 后端暂未提供此统计
        missingValuesHandled: nodeContent.missingCount || 0,
        outliersDetected: nodeContent.outlierCount || 0,
        featuresAdded: 0,  // 后端暂未提供此统计

        // 🔧 数据质量评分（基于清洗后的数据）
        dataQualityScore: nodeContent.qualityScore || 0,

        // 🔧 存储信息（保存到数据库的数据）
        storedRows: cleanedRows,  // 保存到数据库的行数
        tableName: 'stock_data',
        storageSize: nodeContent.storageSize || 0,
        storageTime: nodeContent.storageTime || new Date().toISOString(),
        compressionRatio: 0,
        indexStatus: '已创建索引',  // QLib格式已创建索引
        backupStatus: '未备份',

        // 🔧 缺失值统计（清洗过程中发现的）
        totalMissing: nodeContent.missingCount || 0,
        // 🔧 修复：缺失值率应该基于总单元格数（行数 × 列数）计算
        missingRate: (originalRows > 0 && originalColumns > 0)
          ? Math.round((nodeContent.missingCount || 0) / (originalRows * originalColumns) * 10000) / 100
          : 0,
        // 🔧 新增：从quality_report中提取各列的缺失值统计
        columnMissingStats: (() => {
          const qualityReport = nodeContent.qualityReport || {}
          const byColumn = qualityReport.issue_analysis?.missing_values?.by_column || {}

          // 调试日志
          console.log('[DataCleaningConfigSimple] ===== 各列缺失值统计 =====')
          console.log('[DataCleaningConfigSimple] nodeContent.qualityReport:', qualityReport)
          console.log('[DataCleaningConfigSimple] qualityReport 类型:', typeof qualityReport)
          console.log('[DataCleaningConfigSimple] qualityReport 键:', qualityReport ? Object.keys(qualityReport) : 'null/undefined')
          console.log('[DataCleaningConfigSimple] byColumn:', byColumn)
          console.log('[DataCleaningConfigSimple] byColumn 长度:', byColumn ? Object.keys(byColumn).length : 0)
          console.log('[DataCleaningConfigSimple] 原始行数:', originalRows)

          const stats = Object.entries(byColumn).map(([column, data]: [string, any]) => {
            const count = data?.count || 0
            const rate = originalRows > 0 ? (count / originalRows * 100).toFixed(1) : '0.0'
            console.log(`[DataCleaningConfigSimple] 列 ${column}: 缺失${count}个 (${rate}%)`)
            return {
              column,
              missingCount: count,
              missingRate: parseFloat(rate),
              handlingMethod: data?.handling_method || '插值填充'
            }
          })

          console.log('[DataCleaningConfigSimple] 最终统计:', stats)
          console.log('[DataCleaningConfigSimple] ============================')
          return stats
        })()
      }

      showQualityReport.value = true
      console.log('[DataCleaningConfigSimple] 转换后的数据库报告已加载:', qualityReport.value)
      console.log('[DataCleaningConfigSimple] 数据库统计 - 原始行数:', originalRows, '保存行数:', cleanedRows, '删除行数:', rowsRemoved)
      return
    } else {
      console.log('[DataCleaningConfigSimple] ❌ 节点未完成执行，conversionStatus:', nodeContent.conversionStatus)
    }

    // 备选方案：从工作流引擎返回的数据结构中提取信息
    console.log('[DataCleaningConfigSimple] 尝试备选方案：从工作流引擎返回的数据结构中提取信息')
    const reportData = props.nodeData.qualityReport || nodeContent.qualityReport || {}
    const statistics = props.nodeData.statistics || nodeContent.statistics || {}
    const dataOverview = reportData.data_overview || {}

    console.log('[DataCleaningConfigSimple] 备选方案数据:', {
      reportData,
      statistics,
      dataOverview,
      nodeContent
    })

    // 🔧 修复：准确计算股票和指数数量（备选方案，支持 QLib 格式）
    const stockCodesList = props.nodeData.stockCodes || reportData.stock_codes || dataOverview.stock_codes || []
    const isIndexCode2 = (code: string): boolean => {
      // 标准化代码格式（转为大写）
      const normalizedCode = code.toUpperCase()

      let numericPart = ''
      let exchange = ''

      if (normalizedCode.includes('.')) {
        const parts = normalizedCode.split('.')
        numericPart = parts[0]
        exchange = parts[1]
      } else if (normalizedCode.length === 7) {
        exchange = normalizedCode.substring(0, 2)
        numericPart = normalizedCode.substring(2)
      } else {
        return false
      }

      if (numericPart.startsWith('000') && numericPart.length === 6) {
        const num = parseInt(numericPart)
        if ((num >= 1 && num <= 999) || num === 688) {
          return exchange === 'SH'
        }
      }
      if (numericPart.startsWith('399') && numericPart.length === 6) {
        return exchange === 'SZ'
      }
      return false
    }
    const indexCodesCount2 = stockCodesList.filter((code: string) => isIndexCode2(code)).length
    const stockCodesCount2 = stockCodesList.length - indexCodesCount2

    // 填充质量报告数据 - 修复：使用正确的字段名，移除模拟默认值
    qualityReport.value = {
      originalRows: reportData.storage_info?.data_storage?.total_records || props.nodeData.originalDataCount || dataOverview.total_records || nodeContent.originalRows || 0,  // 🔧 修复：优先显示存储的数据行数
      originalColumns: dataOverview.data_columns || dataOverview.columns_count || nodeContent.originalColumns || 0,  // 修复：使用正确的字段名
      dateRange: dataOverview.data_time_range || dataOverview.date_range || nodeContent.dateRange || '未指定',  // 修复：使用正确的字段名
      stockCount: stockCodesCount2 > 0 ? stockCodesCount2 : (dataOverview.stock_count || nodeContent.stockCount || 0),
      indexCount: indexCodesCount2 > 0 ? indexCodesCount2 : (nodeContent.indexCount || 0),  // 🔧 修复：使用计算值
      rowsProcessed: props.nodeData.originalDataCount || dataOverview.total_records || nodeContent.rowsProcessed || 0,
      validRows: props.nodeData.cleanedDataCount || dataOverview.valid_records || nodeContent.validRows || 0,
      rowsRemoved: (dataOverview.missing_records || 0) + (dataOverview.duplicate_records || 0) + (dataOverview.outlier_records || 0),
      duplicatesRemoved: reportData.issue_analysis?.duplicates?.total || nodeContent.duplicatesRemoved || 0,
      invalidValuesFixed: reportData.issue_analysis?.invalid_values?.total || nodeContent.invalidValuesFixed || 0,
      missingValuesHandled: reportData.issue_analysis?.missing_values?.total || nodeContent.missingValuesHandled || 0,
      outliersDetected: reportData.issue_analysis?.outliers?.total || nodeContent.outliersDetected || 0,
      featuresAdded: reportData.feature_engineering?.features_added || nodeContent.featuresAdded || 0,
      dataQualityScore: (reportData.overall_quality_score || nodeContent.dataQualityScore || 0),  // 🔧 修复：保持小数形式（0.96）
      storedRows: statistics.storedRows || reportData.storage_info?.data_storage?.total_records || nodeContent.storedRows || 0,
      tableName: statistics.tableName || reportData.storage_info?.data_storage?.table_name || nodeContent.tableName || 'stock_data',
      storageSize: statistics.storageSize || reportData.storage_info?.data_storage?.storage_size_bytes || reportData.storage_info?.data_storage?.storage_size || nodeContent.storageSize || 0,  // 修复：优先使用字节数
      storageTime: statistics.storageTime || reportData.storage_info?.data_storage?.last_updated || nodeContent.storageTime || new Date().toISOString(),
      compressionRatio: statistics.compressionRatio || reportData.storage_info?.compression_info?.ratio || nodeContent.compressionRatio || 0,
      indexStatus: statistics.indexStatus || (reportData.storage_info?.index_info?.indexed ?
        `已创建索引` : '未创建索引'),  // 简化显示
      backupStatus: statistics.backupStatus || (reportData.storage_info?.backup_storage?.backup_enabled ?
        `已备份` : '未备份'),  // 简化显示
      totalMissing: reportData.issue_analysis?.missing_values?.total_cells || reportData.issue_analysis?.missing_values?.total || nodeContent.totalMissing || 0,  // 修复：使用总缺失单元格数
      missingRate: (dataOverview.total_records || props.nodeData.originalDataCount || 1) > 0
        ? Math.round(((reportData.issue_analysis?.missing_values?.total_cells || reportData.issue_analysis?.missing_values?.total || 0) /
          (dataOverview.total_records || props.nodeData.originalDataCount || 1)) * 10000) / 100
        : 0,
      columnMissingStats: Object.entries(reportData.issue_analysis?.missing_values?.by_column || {}).map(([column, data]) => ({
        column,
        missingCount: (data as any)?.count || 0,
        missingRate: (dataOverview.total_records || 1) > 0
          ? Math.round(((data as any)?.count || 0) / (dataOverview.total_records || 1) * 10000) / 100
          : 0,
        handlingMethod: (data as any)?.handling_method || '插值填充'
      }))
    }

    showQualityReport.value = true
    console.log('[DataCleaningConfigSimple] 质量报告已从节点数据加载 (格式2):', qualityReport.value)
  } catch (error) {
    console.error('[DataCleaningConfigSimple] loadQualityReportFromNodeData 出错:', error)
  }
}

// 组件挂载时的初始化
onMounted(() => {
  // 🔧 修复：总是调用后端 API 获取最新的 QLib 数据库统计信息
  // 节点缓存中的 stockCount/indexCount 可能不准确，应该以 QLib 数据库为准
  console.log('[DataCleaningConfigSimple] 调用API获取最新的质量报告')
  fetchQualityReport()
})

// 监听 nodeData 变化
watch(() => props.nodeData, (newNodeData) => {
  console.log('[DataCleaningConfigSimple] nodeData changed:', newNodeData)
  if (newNodeData) {
    try {
      // 🔧 修复：优先使用节点数据
      const nodeContent = newNodeData.data?.content || newNodeData?.content
      if (nodeContent && nodeContent.conversionStatus === 'completed') {
        // 节点已成功执行，使用节点返回的清洗结果
        loadQualityReportFromNodeData()
      } else {
        // 节点未执行，调用API
        fetchQualityReport()
      }
    } catch (error) {
      console.error('[DataCleaningConfigSimple] 加载质量报告时出错:', error)
    }
  }
}, { deep: true, immediate: true })
</script>

<style scoped>
.data-cleaning-config {
  padding: 20px;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.config-section {
  margin-bottom: 25px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title i {
  color: var(--primary-color);
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: var(--text-muted);
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-text h4 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-text p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* 数据质量报告样式 */
.quality-report-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--border-color-light);
  padding-bottom: 10px;
}

.tab-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 6px 6px 0 0;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
}

.tab-btn:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--primary-color);
  color: white;
}

.tab-content {
  padding: 20px;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color-light);
}

/* 数据概览样式 */
.overview-grid,
.stats-grid,
.storage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.overview-item,
.storage-item {
  text-align: center;
  padding: 15px;
  background: var(--info-bg);
  border-radius: 8px;
  border: 1px solid var(--info-border);
}

.overview-label,
.storage-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}

/* 分组显示样式 - 股票和指数 */
.stock-groups {
  display: flex;
  gap: 15px;
  margin: 20px 0;
  justify-content: center;
}

.group-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 20px;
  background: linear-gradient(135deg, var(--info-bg) 0%, var(--card-bg) 100%);
  border-radius: 10px;
  border: 1px solid var(--info-border);
  flex: 1;
  max-width: 250px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.group-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.group-icon {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, #6366f1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  flex-shrink: 0;
}

.group-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.group-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.group-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

/* 详细统计样式 */
.detailed-stats {
  margin: 25px 0;
  padding: 20px;
  background: linear-gradient(135deg, var(--card-bg) 0%, var(--info-bg) 100%);
  border-radius: 12px;
  border: 1px solid var(--border-color-light);
}

.detailed-stats h5 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  text-align: center;
}

.stats-grid-compact {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.stat-compact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 15px;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
}

.stat-compact-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: var(--primary-color);
}

.stat-compact-icon {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--primary-color) 0%, #6366f1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  flex-shrink: 0;
}

.stat-compact-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-compact-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-compact-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.overview-value,
.storage-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
}

/* 数据库表名称特殊样式 - 防止长路径溢出 */
.storage-table-name {
  font-size: 14px !important;
  word-break: break-all;
  line-height: 1.4;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 存储时间样式 - 使用较小字体 */
.storage-time {
  font-size: 14px !important;
  line-height: 1.4;
}

/* 数据质量评分显示 */
.quality-score-display {
  display: flex;
  align-items: center;
  gap: 30px;
  margin: 30px 0;
  padding: 20px;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color-light);
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 28px;
  color: white;
  position: relative;
  overflow: hidden;
}

.score-circle::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: conic-gradient(
    var(--primary-color) 0deg,
    var(--primary-color) var(--data-quality-score),
    var(--background) var(--data-quality-score)
  );
  border-radius: 50%;
  z-index: -1;
}

.score-circle.excellent {
  background: #28a745;
}

.score-circle.good {
  background: #ffc107;
}

.score-circle.fair {
  background: #fd7e14;
}

.score-circle.poor {
  background: #dc3545;
}

.score-number {
  position: relative;
  z-index: 1;
}

.score-text {
  flex: 1;
}

.score-text h5 {
  margin: 0 0 10px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.score-text p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
}

/* 数据分布可视化 */
.data-distribution {
  margin: 30px 0;
  padding: 20px;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color-light);
}

.data-distribution h5 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  text-align: center;
}

.distribution-bars {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  min-width: 80px;
  font-size: 14px;
  color: var(--text-secondary);
}

.bar-container {
  flex: 1;
  height: 20px;
  background: var(--hover-bg);
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 10px;
}

.bar-fill.valid {
  background: linear-gradient(90deg, #28a745, #20c997);
}

.bar-fill.removed {
  background: linear-gradient(90deg, #dc3545, #c82333);
}

.bar-value {
  min-width: 50px;
  text-align: right;
  font-weight: 600;
  color: var(--text-primary);
}

/* 清洗统计样式 */
.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-item.highlight {
  background: linear-gradient(135deg, var(--primary-color-light), var(--primary-color));
  color: white;
  border: 1px solid var(--primary-color);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-item:not(.highlight) .stat-icon {
  background: var(--info-bg);
  color: var(--info-color);
}

.stat-icon.success {
  background: var(--success-bg);
  color: var(--success-color);
}

.stat-icon.warning {
  background: var(--warning-bg);
  color: var(--warning-color);
}

.stat-icon.info {
  background: var(--info-bg);
  color: var(--info-color);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 清洗过程可视化 */
.process-visualization {
  margin: 30px 0;
  padding: 20px;
  background: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color-light);
}

.process-visualization h5 {
  font-size: 16px;
  font-width: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  text-align: center;
}

.process-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  padding: 10px 0;
}

.process-steps::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 10%;
  right: 10%;
  height: 2px;
  background: var(--border-color-light);
  z-index: 0;
}

.process-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  z-index: 1;
  flex: 1;
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--border-color);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 10px;
}

.process-step.completed .step-number {
  background: var(--success-color);
  color: white;
}

.process-step.warning .step-number {
  background: var(--warning-color);
  color: white;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.step-value {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 状态颜色 - 用于清洗过程中的值显示 */
.step-value.status-excellent {
  color: #28a745;
  font-weight: 600;
}

.step-value.status-good {
  color: #67c23a;
  font-weight: 600;
}

.step-value.status-warning {
  color: #e6a23c;
  font-weight: 600;
}

.step-value.status-danger {
  color: #f56c6c;
  font-weight: 600;
}

/* 详细统计样式 */
.detailed-stats,
.storage-details {
  margin-top: 20px;
}

.detailed-stats h5,
.storage-details h5 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 15px;
}

.stats-list,
.storage-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stats-list-item,
.storage-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: var(--hover-bg);
  border-radius: 6px;
}

.stats-label,
.storage-list-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stats-label i {
  font-size: 12px;
  color: var(--primary-color);
  margin-right: 4px;
}

.stats-hint {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 400;
  line-height: 1.3;
}

.stats-value,
.storage-list-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 缺失值分析样式 */
.missing-overview {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.missing-chart-placeholder {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 40px;
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  text-align: center;
}

.placeholder-icon {
  font-size: 48px;
  color: var(--text-muted);
  margin-bottom: 20px;
}

.placeholder-text h4 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 5px 0;
}

.placeholder-text p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.missing-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.missing-stat {
  text-align: center;
  padding: 15px;
  background: var(--warning-bg);
  border-radius: 8px;
  border: 1px solid var(--warning-border);
}

.missing-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}

.missing-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--warning-color);
}

/* 缺失值表格样式 */
.missing-table {
  overflow-x: auto;
  margin-top: 15px;
}

.missing-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.missing-table th,
.missing-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color-light);
}

.missing-table th {
  background: var(--hover-bg);
  font-weight: 600;
  color: var(--text-primary);
}

.missing-table tr:hover {
  background: var(--hover-bg);
}

/* 报告操作按钮样式 */
.report-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.primary {
  background: var(--primary-color);
  color: white;
}

.action-btn.primary:hover {
  background: var(--primary-color-dark);
}

.action-btn.secondary {
  background: var(--secondary-color);
  color: white;
}

.action-btn.secondary:hover {
  background: var(--secondary-color-dark);
}

.action-btn.tertiary {
  background: var(--info-bg);
  color: var(--info-color);
  border: 1px solid var(--info-border);
}

.action-btn.tertiary:hover {
  background: var(--info-color);
  color: white;
}

.action-btn.success {
  background: #28a745;
  color: white;
}

.action-btn.success:hover {
  background: #218838;
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-grid,
  .stats-grid,
  .storage-grid {
    grid-template-columns: 1fr;
  }

  .missing-overview {
    grid-template-columns: 1fr;
  }

  .quality-report-tabs {
    flex-wrap: wrap;
  }

  .tab-btn {
    flex: 1;
    min-width: 100px;
  }

  .quality-score-display {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }

  .process-steps {
    flex-direction: column;
    gap: 20px;
  }

  .report-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
    justify-content: center;
  }

  .data-distribution .distribution-bars {
    gap: 10px;
  }

  .bar-item {
    flex-direction: column;
    align-items: stretch;
  }

  .bar-label {
    min-width: auto;
    text-align: center;
  }

  .bar-container {
    width: 100%;
  }

  .bar-value {
    text-align: center;
  }
}
</style>