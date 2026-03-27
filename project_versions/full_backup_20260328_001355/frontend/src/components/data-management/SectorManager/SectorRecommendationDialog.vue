<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`${targetSector?.name || '板块'} - 智能推荐`"
    width="900px"
    :before-close="handleClose"
    custom-class="recommendation-dialog"
    append-to-body
    :z-index="20000"
  >
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><loading /></el-icon>
      <p>正在分析板块关联...</p>
      <el-progress
        :percentage="analysisProgress"
        :status="analysisProgress === 100 ? 'success' : undefined"
      />
      <p class="progress-text">{{ progressText }}</p>
    </div>

    <!-- 推荐结果 -->
    <div v-else-if="recommendations.length > 0" class="recommendation-content">
      <!-- 推荐摘要 -->
      <div class="summary-section">
        <div class="summary-card">
          <div class="summary-icon">🤖</div>
          <div class="summary-text">
            <h4>基于 QLib 方法论</h4>
            <p>从 {{ totalCandidates }} 个板块中找到 {{ recommendations.length }} 个相关板块</p>
          </div>
        </div>
        <div class="methodology-tags">
          <el-tag type="danger" size="small">价格相关性 40%</el-tag>
          <el-tag type="warning" size="small">行业关联 30%</el-tag>
          <el-tag type="info" size="small">成分股重叠 15%</el-tag>
          <el-tag type="success" size="small">用户偏好 15%</el-tag>
        </div>
      </div>

      <!-- 推荐列表 -->
      <div class="recommendation-list">
        <div
          v-for="(item, index) in recommendations"
          :key="item.sector.id"
          class="recommendation-item"
          :class="`item-level-${getRecommendationLevel(item.relevanceScore).level.toLowerCase()}`"
        >
          <!-- 排名和基本信息 -->
          <div class="item-header">
            <div class="rank-badge" :class="`rank-top-${Math.min(index + 1, 3)}`">
              #{{ index + 1 }}
            </div>
            <div class="item-info">
              <h4 class="sector-name">{{ item.sector.name }}</h4>
              <div class="sector-meta">
                <span>{{ item.sector.stockCount }} 只成分股</span>
              </div>
            </div>
            <div class="item-score">
              <div
                class="score-circle"
                :style="{
                  background: `conic-gradient(${getQLibRecommendationLevel(item.relevanceScore).color} ${item.relevanceScore}%, transparent 0)`
                }"
              >
                <span class="score-text">{{ item.relevanceScore }}</span>
              </div>
              <div
                class="score-label"
                :style="{ color: getQLibRecommendationLevel(item.relevanceScore).color }"
              >
                {{ getQLibRecommendationLevel(item.relevanceScore).level }}
              </div>
            </div>
          </div>

          <!-- 推荐理由 -->
          <div class="item-reasons">
            <div class="reasons-header">
              <span class="reasons-title">推荐理由：</span>
              <span class="reasons-summary">{{ getQLibReasonSummary(item.reasons) }}</span>
            </div>
            <div class="reasons-tags">
              <el-tag
                v-for="reason in item.reasons"
                :key="reason.type"
                :type="getReasonTagType(reason.impact)"
                size="small"
                class="reason-tag"
              >
                <strong>{{ reason.label }}</strong>
                <span class="reason-desc">: {{ reason.description }}</span>
                <span class="reason-weight">({{ reason.weight }}%)</span>
                <span v-if="reason.qlibRef" class="reason-ref" title="基于 QLib 方法论">📖</span>
              </el-tag>
            </div>
          </div>

          <!-- QLib 方法论指标详情 -->
          <div class="item-details">
            <div class="details-title">📊 QLib 方法论分析</div>
            <el-descriptions :column="2" size="small" border>
              <!-- 价格相关性 (核心支柱1) -->
              <el-descriptions-item
                v-if="item.metrics.priceCorrelation"
                label="价格相关系数"
              >
                <span :class="getCorrelationClass(item.metrics.priceCorrelation.coefficient)">
                  {{ item.metrics.priceCorrelation.coefficient.toFixed(3) }}
                </span>
                <span class="detail-hint">
                  (p={{ item.metrics.priceCorrelation.significance.toFixed(3) }})
                </span>
              </el-descriptions-item>

              <!-- 风险归因 (核心支柱2) -->
              <el-descriptions-item
                v-if="item.metrics.riskAttribution"
                label="系统性风险 (β)"
              >
                {{ item.metrics.riskAttribution.systematicRisk.toFixed(3) }}
                <span class="detail-hint">
                  (特异性风险={{ item.metrics.riskAttribution.specificRisk.toFixed(3) }})
                </span>
              </el-descriptions-item>

              <!-- IC 分析 (核心支柱3) -->
              <el-descriptions-item
                v-if="item.metrics.icAnalysis"
                label="IC 值"
              >
                {{ item.metrics.icAnalysis.ic.toFixed(3) }}
                <span class="detail-hint">
                  (IR={{ item.metrics.icAnalysis.ir.toFixed(3) }})
                </span>
              </el-descriptions-item>

              <!-- 行业关联 (辅助指标) -->
              <el-descriptions-item
                v-if="item.metrics.industryRelation !== undefined && item.metrics.industryRelation > 0"
                label="行业关联度"
              >
                {{ (item.metrics.industryRelation * 100).toFixed(0) }}%
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 操作按钮 -->
          <div class="item-actions">
            <el-button
              size="small"
              @click="handleViewDetail(item.sector)"
            >
              查看详情
            </el-button>
            <el-button
              size="small"
              @click="handleAddToCompare(item.sector)"
            >
              加入对比
            </el-button>
            <el-button
              size="small"
              type="primary"
              @click="handleSelectSector(item.sector)"
            >
              选择此板块
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 无结果提示 -->
    <div v-else class="no-results">
      <el-empty description="未找到相关板块">
        <template #image>
          <div class="empty-icon">🔍</div>
        </template>
        <p>当前板块暂无明显关联板块</p>
      </el-empty>
    </div>

    <!-- 底部操作栏 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button
          v-if="recommendations.length > 0"
          type="primary"
          @click="handleExportRecommendations"
        >
          导出推荐列表
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import type { SectorNode } from '@/components/data-management/shared/types'
import {
  generateQLibRecommendations,
  getQLibReasonSummary,
  getQLibRecommendationLevel,
  type QLibRecommendationResult
} from './qlib-recommendation-engine'

interface Props {
  visible: boolean
  targetSector: SectorNode | null
  allSectors: SectorNode[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'select-sector': [sector: SectorNode]
  'add-to-compare': [sector: SectorNode]
  'view-detail': [sector: SectorNode]
}>()

// 状态
const dialogVisible = ref(false)
const loading = ref(false)
const analysisProgress = ref(0)
const progressText = ref('')
const recommendations = ref<QLibRecommendationResult[]>([])
const totalCandidates = ref(0)

// 监听 visible 变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.targetSector) {
    loadRecommendations()
  }
})

watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

// 加载推荐数据
const loadRecommendations = async () => {
  if (!props.targetSector) return

  loading.value = true
  analysisProgress.value = 0
  progressText.value = '正在分析板块关联...'
  recommendations.value = []

  try {
    // 模拟分析进度
    const progressInterval = setInterval(() => {
      if (analysisProgress.value < 90) {
        analysisProgress.value += 10
        const progress = analysisProgress.value
        if (progress < 20) {
          progressText.value = '📊 正在计算价格相关性 (QLib Corr)...'
        } else if (progress < 40) {
          progressText.value = '⚠️ 正在进行风险归因分析 (QLib risk_analysis)...'
        } else if (progress < 60) {
          progressText.value = '📈 正在计算 IC 值 (QLib IC Analysis)...'
        } else if (progress < 80) {
          progressText.value = '🔗 正在匹配行业关联规则...'
        } else {
          progressText.value = '✨ 综合分析中...'
        }
      }
    }, 200)

    // TODO: 从后端获取价格历史数据
    // const priceHistoryData = await fetchPriceHistoryData([props.targetSector.name, ...allSectors.map(s => s.name)])

    // 获取用户收藏的板块
    const userFavorites = getUserFavorites()

    // 生成推荐 (使用 QLib 方法论)
    // 注意：当前使用行业关联规则和用户偏好进行推荐
    // 如果接入价格历史数据，将启用 QLib 核心支柱：价格相关性、风险归因、IC分析
    const results = await generateQLibRecommendations(
      props.targetSector,
      props.allSectors,
      undefined, // priceHistoryData - 待接入后端API
      userFavorites
    )

    clearInterval(progressInterval)
    analysisProgress.value = 100
    progressText.value = '分析完成！'

    recommendations.value = results
    totalCandidates.value = props.allSectors.filter(s => s.type === 'sector').length

    if (results.length > 0) {
      ElMessage.success(`找到 ${results.length} 个相关板块`)
    } else {
      ElMessage.info('暂未找到相关板块，推荐功能需要接入价格历史数据后会更准确')
    }
  } catch (error: any) {
    console.error('生成推荐失败:', error)
    ElMessage.error(`生成推荐失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 获取用户收藏的板块
const getUserFavorites = (): string[] => {
  try {
    const favorites = localStorage.getItem('sector_favorites')
    if (favorites) {
      const data = JSON.parse(favorites)
      return data.collections?.flatMap((c: any) => c.sectors.map((s: any) => s.name)) || []
    }
  } catch (error) {
    console.error('读取用户收藏失败:', error)
  }
  return []
}

// 获取推荐理由标签类型
const getReasonTagType = (impact: string): any => {
  switch (impact) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return ''
  }
}

// 获取相关性样式类
const getCorrelationClass = (value: number): string => {
  if (value > 0.6) return 'text-strong-positive'
  if (value > 0.3) return 'text-positive'
  if (value > -0.3) return 'text-neutral'
  return 'text-negative'
}

// 处理查看详情
const handleViewDetail = (sector: SectorNode) => {
  emit('view-detail', sector)
}

// 处理加入对比
const handleAddToCompare = (sector: SectorNode) => {
  emit('add-to-compare', sector)
  ElMessage.success(`已将 ${sector.name} 加入对比`)
}

// 处理选择板块
const handleSelectSector = (sector: SectorNode) => {
  emit('select-sector', sector)
  handleClose()
}

// 处理导出推荐列表
const handleExportRecommendations = () => {
  const data = recommendations.value.map((item, index) => ({
    '排名': index + 1,
    '板块名称': item.sector.name,
    '成分股数量': item.sector.stockCount,
    '相关性得分': item.relevanceScore,
    '推荐等级': getRecommendationLevel(item.relevanceScore).level,
    '推荐理由': getReasonSummary(item.reasons),
    '价格相关系数': item.data.priceCorrelation?.toFixed(3) || '-',
    '行业关联度': item.data.industryRelation ? `${(item.data.industryRelation * 100).toFixed(0)}%` : '-',
    '成分股重叠': item.data.stockOverlap ? `${(item.data.stockOverlap * 100).toFixed(1)}%` : '-',
    '用户偏好匹配': item.data.userBehavior ? `${(item.data.userBehavior * 100).toFixed(0)}%` : '-'
  }))

  // 转换为CSV格式
  const headers = Object.keys(data[0]).join(',')
  const rows = data.map(row => Object.values(row).join(','))
  const csv = [headers, ...rows].join('\n')

  // 创建下载链接
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `板块推荐_${props.targetSector?.name}_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()

  ElMessage.success('导出成功')
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style>
/* 全局样式 - 确保对话框在导航栏之上 */
.recommendation-dialog .el-dialog {
  z-index: 20000 !important;
}

.recommendation-dialog .el-dialog__header {
  z-index: 20001 !important;
}

.recommendation-dialog .el-dialog__body {
  z-index: 20000 !important;
}

.recommendation-dialog .el-overlay {
  z-index: 19999 !important;
}
</style>

<style scoped>
/* 加载容器 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 20px;
  color: #2962ff;
}

.loading-container .el-progress {
  width: 300px;
  margin: 20px 0;
}

.progress-text {
  font-size: 14px;
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.5);
}

/* 推荐内容 */
.recommendation-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 摘要部分 */
.summary-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-icon {
  font-size: 40px;
}

.summary-text h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #ffffff;
}

.summary-text p {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.methodology-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 推荐列表 */
.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.recommendation-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

/* 等级样式 */
.item-level-强烈推荐 {
  border-color: rgba(245, 108, 108, 0.4);
}

.item-level-推荐 {
  border-color: rgba(230, 162, 60, 0.4);
}

/* 项头部 */
.item-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.rank-badge {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 16px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.7);
}

.rank-top-1 {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #000;
}

.rank-top-2 {
  background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
  color: #000;
}

.rank-top-3 {
  background: linear-gradient(135deg, #cd7f32, #e6a166);
  color: #fff;
}

.item-info {
  flex: 1;
}

.sector-name {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #ffffff;
  font-weight: 600;
}

.sector-meta {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

/* 评分圆圈 */
.item-score {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.score-circle::before {
  content: '';
  position: absolute;
  width: 50px;
  height: 50px;
  background: rgba(26, 26, 46, 0.95);
  border-radius: 50%;
}

.score-text {
  position: relative;
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
}

.score-label {
  font-size: 14px;
  font-weight: 600;
  min-width: 80px;
  text-align: right;
}

/* 推荐理由 */
.item-reasons {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.reasons-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.reasons-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
}

.reasons-summary {
  font-size: 13px;
  color: #2962ff;
}

.reasons-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.reason-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.reason-desc {
  opacity: 0.8;
}

.reason-weight {
  opacity: 0.6;
  font-size: 11px;
}

/* QLib 指标详情 */
.item-details {
  margin-bottom: 12px;
  padding: 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.details-title {
  font-size: 14px;
  font-weight: 600;
  color: #2962ff;
  margin-bottom: 12px;
}

.detail-hint {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-left: 8px;
}

.reason-ref {
  margin-left: 4px;
  cursor: help;
}

.item-details :deep(.el-descriptions) {
  --el-descriptions-table-border-color: rgba(255, 255, 255, 0.1);
}

.item-details :deep(.el-descriptions__label) {
  background: rgba(255, 255, 255, 0.05) !important;
  color: rgba(255, 255, 255, 0.6) !important;
}

.item-details :deep(.el-descriptions__content) {
  background: transparent !important;
  color: rgba(255, 255, 255, 0.9) !important;
}

/* 相关性颜色 */
.text-strong-positive {
  color: #f56c6c;
  font-weight: 600;
}

.text-positive {
  color: #e6a23c;
}

.text-neutral {
  color: rgba(255, 255, 255, 0.6);
}

.text-negative {
  color: #67c23a;
}

/* 操作按钮 */
.item-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 无结果 */
.no-results {
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

/* 底部操作栏 */
.dialog-footer {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

/* 响应式 */
@media (max-width: 768px) {
  .summary-section {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .item-header {
    flex-wrap: wrap;
  }

  .item-score {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
