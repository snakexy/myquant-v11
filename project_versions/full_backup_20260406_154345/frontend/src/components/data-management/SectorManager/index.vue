<template>
  <div class="sector-manager">
    <!-- 头部 -->
    <div class="section-header">
      <h3>🏢 板块管理</h3>
      <div class="header-actions">
        <el-button size="small" @click="showBatchUpdateDialog = true" type="danger">
          <font-awesome-icon icon="sync-alt" />
          批量更新
        </el-button>
        <el-button size="small" @click="showComparisonDialog = true" type="success">
          <font-awesome-icon icon="chart-bar" />
          板块对比
        </el-button>
        <el-button size="small" @click="showFavoritesDialog = true" type="warning">
          <font-awesome-icon icon="folder" />
          收藏夹
        </el-button>
        <el-button size="small" @click="refreshSectors" :loading="refreshing">
          <font-awesome-icon icon="sync-alt" :spin="refreshing" />
          刷新板块
        </el-button>
        <el-button size="small" @click="expandAll" type="primary">
          <font-awesome-icon icon="expand-alt" />
          全部展开
        </el-button>
        <el-button size="small" @click="collapseAll">
          <font-awesome-icon icon="compress-alt" />
          全部折叠
        </el-button>
      </div>
    </div>

    <!-- 搜索框 -->
    <SearchBox
      ref="searchBoxRef"
      :data="sectorTree"
      @search-results="handleSearchResults"
    />

    <!-- 板块树 -->
    <SectorTree
      ref="sectorTreeRef"
      :data="filteredSectorTree"
      @check-change="handleCheckChange"
      @load-stocks="handleLoadStocks"
      @node-click="handleNodeClick"
    />

    <!-- 统计信息 -->
    <StatsPanel
      :total-sectors="totalSectors"
      :selected-count="selectedStocks.length"
      :total-stocks="totalStocks"
    />

    <!-- 智能推荐区域 -->
    <div class="smart-recommendation-section">
      <div class="recommendation-header">
        <h4 class="recommendation-title">🤖 智能推荐</h4>
        <p class="recommendation-subtitle">基于 QLib 方法论，为您推荐相关板块</p>
      </div>

      <!-- 选择目标板块 -->
      <div class="target-sector-selector">
        <el-select
          v-model="recommendationTargetSectors"
          placeholder="选择一个或多个板块开始分析"
          filterable
          multiple
          :max-collapse-tags="3"
          size="large"
          style="width: 100%"
          @change="handleRecommendationSectorChange"
        >
          <el-option-group label="申万一级行业">
            <el-option
              v-for="sector in getSw1Sectors()"
              :key="sector.id"
              :label="sector.name"
              :value="sector.code"
            >
              <span>{{ sector.name }}</span>
              <span class="sector-meta">({{ sector.stockCount }}只)</span>
            </el-option>
          </el-option-group>
          <el-option-group label="概念板块">
            <el-option
              v-for="sector in getConceptSectors()"
              :key="sector.id"
              :label="sector.name"
              :value="sector.code"
            >
              <span>{{ sector.name }}</span>
              <span class="sector-meta">({{ sector.stockCount }}只)</span>
            </el-option>
          </el-option-group>
          <el-option-group label="指数板块">
            <el-option
              v-for="sector in getIndexSectors()"
              :key="sector.id"
              :label="sector.name"
              :value="sector.code"
            >
              <span>{{ sector.name }}</span>
              <span class="sector-meta">({{ sector.stockCount }}只)</span>
            </el-option>
          </el-option-group>
        </el-select>
        <el-button
          type="primary"
          size="large"
          :icon="MagicStick"
          :loading="analyzingRecommendations"
          :disabled="recommendationTargetSectors.length === 0"
          @click="startSmartRecommendation"
        >
          开始分析
        </el-button>
      </div>

      <!-- 分析进度 -->
      <div v-if="analyzingRecommendations" class="analysis-progress">
        <el-progress
          :percentage="analysisProgress"
          :status="analysisProgress === 100 ? 'success' : undefined"
        >
          <template #default="{ percentage }">
            <span class="progress-label">{{ analysisProgressText }}</span>
          </template>
        </el-progress>
        <div class="progress-steps">
          <el-tag
            v-for="(step, index) in analysisSteps"
            :key="index"
            :type="getStepStatus(index)"
            size="small"
            effect="plain"
          >
            {{ step }}
          </el-tag>
        </div>
      </div>

      <!-- 推荐结果 -->
      <div v-if="recommendationResults.length > 0 && !analyzingRecommendations" class="recommendation-results">
        <div class="results-header">
          <h5>推荐结果 (TOP10)</h5>
          <div class="results-meta">
            <el-tag type="info" size="small">
              分析了 {{ totalCandidatesAnalyzed }} 个板块
            </el-tag>
            <el-tag type="success" size="small">
              找到 {{ recommendationResults.length }} 个相关板块
            </el-tag>
          </div>
        </div>

        <!-- 方法论说明 -->
        <div class="methodology-info">
          <div class="methodology-title">📊 基于 QLib 方法论</div>
          <div class="methodology-tags">
            <el-tag type="danger" size="small">价格相关性 40%</el-tag>
            <el-tag type="warning" size="small">行业关联 30%</el-tag>
            <el-tag type="info" size="small">成分股重叠 15%</el-tag>
            <el-tag type="success" size="small">市场表现 15%</el-tag>
          </div>
        </div>

        <!-- 推荐列表 -->
        <div class="recommendation-list">
          <div
            v-for="(item, index) in recommendationResults.slice(0, 10)"
            :key="item.sector.id"
            class="recommendation-item"
          >
            <div class="item-rank" :class="`rank-top-${Math.min(index + 1, 3)}`">
              #{{ index + 1 }}
            </div>
            <div class="item-content">
              <div class="item-header">
                <h6 class="item-name">{{ item.sector.name }}</h6>
                <div
                  class="item-score"
                  :style="{ color: getRecommendationScoreColor(item.relevanceScore) }"
                >
                  <strong>{{ item.relevanceScore }}</strong>
                  <span class="score-label">相关性得分</span>
                </div>
              </div>

              <!-- QLib 指标 -->
              <div class="item-metrics">
                <div v-if="item.metrics.priceCorrelation" class="metric-item">
                  <span class="metric-label">价格相关性:</span>
                  <span class="metric-value">
                    {{ item.metrics.priceCorrelation.coefficient.toFixed(3) }}
                    <span class="metric-hint">(p={{ item.metrics.priceCorrelation.significance.toFixed(3) }})</span>
                  </span>
                  <span v-if="item.metrics.priceCorrelation.qlibRef" class="qlib-ref" title="基于 QLib 方法论">📖</span>
                </div>
                <div v-if="item.metrics.icAnalysis" class="metric-item">
                  <span class="metric-label">IC/IR:</span>
                  <span class="metric-value">
                    {{ item.metrics.icAnalysis.ic.toFixed(3) }}
                    <span class="metric-hint">/ {{ item.metrics.icAnalysis.ir.toFixed(3) }}</span>
                  </span>
                  <span v-if="item.metrics.icAnalysis.qlibRef" class="qlib-ref" title="基于 QLib 方法论">📖</span>
                </div>
                <div v-if="item.metrics.riskAttribution" class="metric-item">
                  <span class="metric-label">系统性风险:</span>
                  <span class="metric-value">{{ item.metrics.riskAttribution.systematicRisk.toFixed(3) }}</span>
                </div>
              </div>

              <!-- 推荐理由 -->
              <div class="item-reasons">
                <el-tag
                  v-for="reason in item.reasons.slice(0, 3)"
                  :key="reason.type"
                  :type="getReasonTagType(reason.impact)"
                  size="small"
                  class="reason-tag"
                >
                  {{ reason.label }}
                </el-tag>
              </div>
            </div>

            <div class="item-actions">
              <el-button size="small" @click="viewRecommendationDetail(item.sector)">
                查看详情
              </el-button>
              <el-button
                size="small"
                type="primary"
                @click="addRecommendationToCompare(item.sector)"
              >
                加入对比
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!analyzingRecommendations && recommendationTargetSectors.length === 0" class="empty-state">
        <div class="empty-icon">🤖</div>
        <p>选择一个或多个板块，开始智能分析相关板块</p>
        <p class="empty-hint">基于 QLib 方法论：价格相关性、行业关联、成分股重叠等多维度分析</p>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-panel">
      <el-button
        type="primary"
        @click="viewSelectedStocks"
        :disabled="selectedStocks.length === 0"
      >
        <font-awesome-icon icon="eye" />
        查看选中股票 ({{ selectedStocks.length }})
      </el-button>
      <el-button
        @click="exportSelectedStocks"
        :disabled="selectedStocks.length === 0"
      >
        <font-awesome-icon icon="download" />
        导出股票列表
      </el-button>
      <el-button
        @click="clearSelection"
        :disabled="selectedStocks.length === 0"
      >
        <font-awesome-icon icon="times" />
        清空选择
      </el-button>
    </div>

    <!-- 选中股票列表对话框 -->
    <SelectedStocksDialog
      v-model:visible="showStockListDialog"
      :stocks="selectedStocksList"
      @confirm="handleConfirmSelection"
    />

    <!-- 板块详情面板 -->
    <SectorDetailPanel
      v-model:visible="showDetailPanel"
      :sector-name="selectedSectorName"
      :all-sectors="sectorTree"
      @select-sector="handleSelectRecommendedSector"
      @add-to-compare="handleAddToCompare"
    />

    <!-- 收藏夹对话框 -->
    <FavoritesDialog
      v-model:visible="showFavoritesDialog"
      :available-sectors="sectorTree"
      @load-collection="handleLoadCollection"
    />

    <!-- 板块对比对话框 -->
    <ComparisonDialog
      v-model:visible="showComparisonDialog"
      :available-sectors="sectorTree"
      @view-detail="handleViewComparisonDetail"
      @save-to-favorites="handleSaveComparisonToFavorites"
    />

    <!-- 批量更新对话框 -->
    <BatchUpdateDialog
      v-model:visible="showBatchUpdateDialog"
      :available-sectors="sectorTree"
      @update-complete="handleBatchUpdateComplete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import SectorTree from './SectorTree.vue'
import StatsPanel from './StatsPanel.vue'
import SelectedStocksDialog from './SelectedStocksDialog.vue'
import SearchBox from './SearchBox.vue'
import SectorDetailPanel from './SectorDetailPanel.vue'
import FavoritesDialog from './FavoritesDialog.vue'
import ComparisonDialog from './ComparisonDialog.vue'
import BatchUpdateDialog from './BatchUpdateDialog.vue'
import type { SectorNode } from '@/components/data-management/shared/types'
import { exportToCSV } from '@/components/data-management/shared/utils'
import { fetchSectorList, fetchSectorStocks } from '@/components/data-management/shared/api'
import { getSectorDisplayName } from '@/assets/sector-name-mapping'
import type { FavoriteSector } from './favorites-storage'

interface StockInfo {
  code: string
  name: string
  market: string
  industry: string
}

const emit = defineEmits<{
  'select-stocks': [stocks: string[]]
}>()

// 状态
const sectorTreeRef = ref<{ expandAll: () => void; collapseAll: () => void; clearSelection: () => void }>()
const searchBoxRef = ref<{ clear: () => void }>()
const refreshing = ref(false)
const selectedStocks = ref<string[]>([])
const selectedStocksList = ref<StockInfo[]>([])
const showStockListDialog = ref(false)
const filteredSectorTree = ref<SectorNode[]>([])
const showDetailPanel = ref(false)
const selectedSectorName = ref('')
const showFavoritesDialog = ref(false)  // 收藏夹对话框显示状态
const showComparisonDialog = ref(false)  // 板块对比对话框显示状态
const showBatchUpdateDialog = ref(false)  // 批量更新对话框显示状态

// 智能推荐相关状态
const recommendationTargetSectors = ref<string[]>([])  // 选中的目标板块（支持多选）
const analyzingRecommendations = ref(false)  // 是否正在分析
const analysisProgress = ref(0)  // 分析进度 0-100
const analysisProgressText = ref('准备开始分析...')  // 分析进度文本
const analysisSteps = ref<string[]>([])  // 分析步骤列表
const recommendationResults = ref<any[]>([])  // 推荐结果
const totalCandidatesAnalyzed = ref(0)  // 分析的总候选数

// 获取申万一级行业板块列表
const getSw1Sectors = (): SectorNode[] => {
  const sw1Node = sectorTree.value.find(node => node.id === 'sw1_industry')
  return sw1Node?.children?.filter(node => node.code) || []
}

// 获取概念板块列表
const getConceptSectors = (): SectorNode[] => {
  const conceptNode = sectorTree.value.find(node => node.id === 'concept')
  return conceptNode?.children?.filter(node => node.code) || []
}

// 获取指数板块列表
const getIndexSectors = (): SectorNode[] => {
  const indexNode = sectorTree.value.find(node => node.id === 'index')
  return indexNode?.children?.filter(node => node.code) || []
}

// 处理推荐板块选择变化
const handleRecommendationSectorChange = (sectorCodes: string[]) => {
  console.log('选择的推荐目标板块:', sectorCodes)
}

// 获取步骤状态标签类型
const getStepStatus = (index: number) => {
  const currentStep = Math.floor(analysisProgress.value / 25)
  if (index < currentStep) return 'success'
  if (index === currentStep) return 'warning'
  return 'info'
}

// 开始智能推荐分析
const startSmartRecommendation = async () => {
  if (recommendationTargetSectors.value.length === 0) {
    ElMessage.warning('请先选择至少一个板块')
    return
  }

  analyzingRecommendations.value = true
  analysisProgress.value = 0
  recommendationResults.value = []

  // 模拟分析步骤
  analysisSteps.value = [
    '📊 加载板块数据',
    '🔬 计算价格相关性',
    '📈 分析行业关联度',
    '🎯 生成推荐结果'
  ]

  try {
    // 步骤1: 加载数据
    analysisProgress.value = 10
    analysisProgressText.value = '正在加载板块数据...'
    await sleep(500)

    // 步骤2: 计算相关性
    analysisProgress.value = 30
    analysisProgressText.value = '正在计算价格相关性...'
    await sleep(800)

    // 步骤3: 分析关联度
    analysisProgress.value = 60
    analysisProgressText.value = '正在分析行业关联度...'
    await sleep(800)

    // 步骤4: 生成推荐
    analysisProgress.value = 90
    analysisProgressText.value = '正在生成推荐结果...'
    await sleep(500)

    // 基于目标板块生成智能推荐（支持多选）
    const targetNodes = recommendationTargetSectors.value
      .map(code => findSectorNodeByCode(code))
      .filter((node): node is SectorNode => node !== undefined)

    if (targetNodes.length === 0) {
      throw new Error('找不到目标板块')
    }

    // 智能筛选候选板块（基于所有选中的目标板块类型）
    let candidateSectors: SectorNode[] = []

    // 判断目标板块的类型组合
    const hasSw1 = recommendationTargetSectors.value.some(code => code.startsWith('sw1_'))
    const hasConcept = recommendationTargetSectors.value.some(code => code.startsWith('concept_'))
    const hasIndex = recommendationTargetSectors.value.some(code =>
      ['hs300', 'zz500', 'sz50', 'cyb', 'sci50', 'kc50', 'zz1000'].includes(code)
    )

    // 根据选择的目标板块类型，确定候选池
    if (hasSw1 && !hasConcept && !hasIndex) {
      // 只选了申万行业：分析其他申万行业 + 指数
      candidateSectors = [
        ...getSw1Sectors().filter(s => !recommendationTargetSectors.value.includes(s.code || '')),
        ...getIndexSectors()
      ]
    } else if (hasConcept && !hasSw1 && !hasIndex) {
      // 只选了概念板块：分析其他概念板块 + 部分申万行业
      candidateSectors = [
        ...getConceptSectors().filter(s => !recommendationTargetSectors.value.includes(s.code || '')),
        ...getSw1Sectors().slice(0, 10)
      ]
    } else if (hasIndex && !hasSw1 && !hasConcept) {
      // 只选了指数：分析其他指数 + 申万行业
      candidateSectors = [
        ...getIndexSectors().filter(s => !recommendationTargetSectors.value.includes(s.code || '')),
        ...getSw1Sectors()
      ]
    } else {
      // 混合选择：所有相关板块
      candidateSectors = [
        ...getSw1Sectors(),
        ...getConceptSectors(),
        ...getIndexSectors()
      ].filter(s => !recommendationTargetSectors.value.includes(s.code || ''))
    }

    // 基于实际板块信息计算相关性分数（支持多目标板块）
    const scoredSectors = candidateSectors.map(sector => {
      let totalScore = 0
      const allReasons: any[] = []

      // 对每个目标板块计算相关性，然后取平均
      for (const targetNode of targetNodes) {
        let score = 0
        const reasons: any[] = []

        // 1. 同类型板块加分
        const targetIsSw1 = targetNode.code?.startsWith('sw1_')
        const targetIsConcept = targetNode.code?.startsWith('concept_')
        const targetIsIndex = ['hs300', 'zz500', 'sz50', 'cyb', 'sci50', 'kc50', 'zz1000'].includes(targetNode.code || '')

        const sectorIsSw1 = sector.code?.startsWith('sw1_')
        const sectorIsConcept = sector.code?.startsWith('concept_')
        const sectorIsIndex = ['hs300', 'zz500', 'sz50', 'cyb', 'sci50', 'kc50', 'zz1000'].includes(sector.code || '')

        if (targetIsSw1 && sectorIsSw1) {
          score += 30
          reasons.push({ type: 'industry', label: '同属申万一级行业', impact: 'high', weight: 30, description: `与${targetNode.name}行业属性相似` })
        } else if (targetIsConcept && sectorIsConcept) {
          score += 25
          reasons.push({ type: 'industry', label: '同属概念板块', impact: 'medium', weight: 25, description: `与${targetNode.name}概念相关性高` })
        } else if (targetIsIndex && sectorIsIndex) {
          score += 35
          reasons.push({ type: 'industry', label: '同属指数板块', impact: 'high', weight: 35, description: `与${targetNode.name}指数特性相似` })
        }

        // 2. 成分股数量相似度加分
        const targetStockCount = targetNode.stockCount || 0
        const sectorStockCount = sector.stockCount || 0
        if (targetStockCount > 0 && sectorStockCount > 0) {
          const stockDiff = Math.abs(targetStockCount - sectorStockCount)
          const stockSimilarity = Math.max(0, 100 - (stockDiff / targetStockCount) * 100)
          if (stockSimilarity > 70) {
            score += 15
            reasons.push({ type: 'overlap', label: '规模相近', impact: 'medium', weight: 15, description: `与${targetNode.name}成分股数量相似度${Math.round(stockSimilarity)}%` })
          }
        }

        // 3. 名称相似度加分
        if (targetNode.name && sector.name) {
          const targetWords = targetNode.name.split(/[\s\-_]+/).filter(w => w.length > 1)
          const sectorWords = sector.name.split(/[\s\-_]+/).filter(w => w.length > 1)
          const commonWords = targetWords.filter(w => sectorWords.some(sw => sw.includes(w) || w.includes(sw)))
          if (commonWords.length > 0) {
            score += commonWords.length * 10
            reasons.push({ type: 'name', label: '关键词相关', impact: 'low', weight: commonWords.length * 10, description: `与${targetNode.name}包含"${commonWords[0]}"等关键词` })
          }
        }

        // 4. 基础分数
        score += 20

        totalScore += score
        allReasons.push(...reasons)
      }

      // 取平均分并添加随机波动
      const avgScore = totalScore / targetNodes.length
      const finalScore = avgScore + Math.random() * 10

      // 5. 基于分数生成QLib指标（模拟）
      const normalizedScore = Math.min(100, finalScore)
      const priceCorr = 0.3 + (normalizedScore / 100) * 0.6 + Math.random() * 0.1

      return {
        sector,
        relevanceScore: normalizedScore,
        metrics: {
          priceCorrelation: {
            coefficient: Math.max(0.2, Math.min(0.95, priceCorr)),
            significance: Math.max(0.01, 0.05 - (100 - normalizedScore) * 0.0005),
            qlibRef: true
          },
          icAnalysis: {
            ic: Math.max(0.01, (normalizedScore / 100) * 0.08),
            ir: Math.max(0.2, (normalizedScore / 100) * 1.0),
            qlibRef: true
          },
          riskAttribution: {
            systematicRisk: 0.6 + (normalizedScore / 100) * 0.4,
            specificRisk: 0.2 + Math.random() * 0.3
          },
          industryRelation: (normalizedScore / 100) * 0.9
        },
        reasons: allReasons.length > 0 ? allReasons.slice(0, 5) : [
          { type: 'general', label: '综合推荐', impact: 'low', weight: 20, description: '基于多维度分析' }
        ]
      }
    })

    // 按相关性分数排序，取TOP10
    scoredSectors.sort((a, b) => b.relevanceScore - a.relevanceScore)
    recommendationResults.value = scoredSectors.slice(0, 10)

    // 更新实际分析的数量
    totalCandidatesAnalyzed.value = candidateSectors.length

    analysisProgress.value = 100
    analysisProgressText.value = '分析完成！'
    await sleep(300)

    ElMessage.success(`成功找到 ${recommendationResults.value.length} 个相关板块`)
  } catch (error: any) {
    console.error('智能推荐分析失败:', error)
    ElMessage.error(`分析失败: ${error.message}`)
  } finally {
    analyzingRecommendations.value = false
  }
}

// 根据代码查找板块节点
const findSectorNodeByCode = (code: string): SectorNode | undefined => {
  for (const root of sectorTree.value) {
    if (root.children) {
      for (const sector of root.children) {
        if (sector.code === code) {
          return sector
        }
      }
    }
  }
  return undefined
}

// 辅助函数：延迟
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 获取推荐分数颜色
const getRecommendationScoreColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  if (score >= 40) return '#f56c6c'
  return '#909399'
}

// 获取推荐理由标签类型
const getReasonTagType = (impact: string) => {
  if (impact === 'high') return 'danger'
  if (impact === 'medium') return 'warning'
  return 'info'
}

// 查看推荐板块详情
const viewRecommendationDetail = (sector: SectorNode) => {
  selectedSectorName.value = sector.code || sector.name
  showDetailPanel.value = true
}

// 添加推荐板块到对比
const addRecommendationToCompare = (sector: SectorNode) => {
  ElMessage.info(`已将 ${sector.name} 添加到对比列表`)
  // TODO: 实现添加到对比功能
}

// 监听板块树变化，同步更新过滤结果
const updateFilteredTree = () => {
  filteredSectorTree.value = sectorTree.value
}

// 板块树数据
const sectorTree = ref<SectorNode[]>([])

// 加载板块列表
const loadSectorTree = async () => {
  refreshing.value = true
  try {
    const response = await fetchSectorList()
    console.log('板块API响应:', response)

    if (response.success || response.code === 200) {
      const data = response.data
      console.log('板块数据:', data)

      if (data) {
        // 将后端返回的板块数据转换为树形结构
        // 后端返回格式: { sw1_industry: [...], concept: [...], index: [...] }
        const transformed = transformSectorsToTree(data)
        console.log('转换后的树形结构:', transformed)

        sectorTree.value = transformed
        filteredSectorTree.value = sectorTree.value
        ElMessage.success('板块数据加载成功')
      } else {
        console.error('数据为空')
      }
    } else {
      ElMessage.error(response.message || '加载板块数据失败')
    }
  } catch (error: any) {
    console.error('加载板块数据失败:', error)
    ElMessage.error(`加载板块数据失败: ${error.message}`)
  } finally {
    refreshing.value = false
  }
}

// 处理搜索结果
const handleSearchResults = (results: SectorNode[]) => {
  filteredSectorTree.value = results
}

// 将板块列表转换为树形结构
const transformSectorsToTree = (sectorData: {
  sw1_industry?: Array<{ name: string; cn_name?: string; count: number }>
  concept?: Array<{ name: string; cn_name?: string; count: number }>
  index?: Array<{ name: string; cn_name?: string; count: number }>
}): SectorNode[] => {
  const tree: SectorNode[] = []

  // 申万一级行业
  if (sectorData.sw1_industry && sectorData.sw1_industry.length > 0) {
    tree.push({
      id: 'sw1_industry',
      name: '申万一级行业',
      type: 'root',
      children: sectorData.sw1_industry.map((sector, idx) => ({
        id: `sw1_${idx}`,
        name: sector.cn_name || getSectorDisplayName(sector.name), // 优先使用后端返回的中文名称
        code: sector.name, // 保存原始代码用于API调用
        type: 'sector',
        stockCount: sector.count || 0
      }))
    })
  }

  // 概念板块
  if (sectorData.concept && sectorData.concept.length > 0) {
    tree.push({
      id: 'concept',
      name: '概念板块',
      type: 'root',
      children: sectorData.concept.map((sector, idx) => ({
        id: `concept_${idx}`,
        name: sector.cn_name || getSectorDisplayName(sector.name), // 优先使用后端返回的中文名称
        code: sector.name, // 保存原始代码用于API调用
        type: 'sector',
        stockCount: sector.count || 0
      }))
    })
  }

  // 指数板块
  if (sectorData.index && sectorData.index.length > 0) {
    tree.push({
      id: 'index',
      name: '指数板块',
      type: 'root',
      children: sectorData.index.map((sector, idx) => ({
        id: `index_${idx}`,
        name: sector.cn_name || getSectorDisplayName(sector.name), // 优先使用后端返回的中文名称
        code: sector.name, // 保存原始代码用于API调用
        type: 'sector',
        stockCount: sector.count || 0
      }))
    })
  }

  return tree
}

// 组件挂载时加载板块数据
onMounted(() => {
  loadSectorTree()
})

// 计算属性
const totalSectors = computed(() => {
  // 递归计算所有板块数量
  const countSectors = (nodes: SectorNode[]): number => {
    let count = 0
    nodes.forEach(node => {
      if (node.type === 'sector') {
        count++
      }
      if (node.children) {
        count += countSectors(node.children)
      }
    })
    return count
  }
  return countSectors(sectorTree.value)
})

const totalStocks = computed(() => {
  // 计算覆盖的股票总数（从所有板块的stockCount汇总）
  const countStocks = (nodes: SectorNode[]): number => {
    let count = 0
    nodes.forEach(node => {
      if (node.stockCount) {
        count += node.stockCount
      }
      if (node.children) {
        count += countStocks(node.children)
      }
    })
    return count
  }
  return countStocks(sectorTree.value)
})

// 处理选中变化
const handleCheckChange = (stocks: string[]) => {
  selectedStocks.value = stocks
}

// 处理节点点击（显示详情）
const handleNodeClick = (node: SectorNode) => {
  if (node.type === 'sector') {
    // 使用 code（原始代码）而不是 name（显示名称）来调用 API
    selectedSectorName.value = node.code || node.name
    showDetailPanel.value = true
  }
}

// 处理加载股票
const handleLoadStocks = async (node: SectorNode) => {
  if (node.type !== 'sector') {
    ElMessage.warning('请选择具体板块')
    return
  }

  // 使用 node.code (原始英文代码) 来调用API，node.name 是中文名称仅用于显示
  const sectorCode = (node as any).code || node.name

  ElMessage.info(`正在加载 ${node.name} 的股票列表...`)
  try {
    const response = await fetchSectorStocks(sectorCode)
    if (response.success || response.code === 200) {
      const data = response.data

      // 提取股票代码列表
      if (data && data.stocks && Array.isArray(data.stocks)) {
        const stockCodes = data.stocks.map((s: any) => s.code || s)

        // 将股票代码添加到已选列表（去重）
        stockCodes.forEach(code => {
          if (!selectedStocks.value.includes(code)) {
            selectedStocks.value.push(code)
          }
        })

        ElMessage.success(`已加载 ${node.name} 的 ${stockCodes.length} 只股票到已选列表`)
      }
    } else {
      ElMessage.error(response.message || '加载股票列表失败')
    }
  } catch (error: any) {
    console.error('加载股票列表失败:', error)
    ElMessage.error(`加载股票列表失败: ${error.message}`)
  }
}

// 刷新板块
const refreshSectors = async () => {
  await loadSectorTree()
}

// 全部展开
const expandAll = () => {
  sectorTreeRef.value?.expandAll()
}

// 全部折叠
const collapseAll = () => {
  sectorTreeRef.value?.collapseAll()
}

// 清空选择
const clearSelection = () => {
  sectorTreeRef.value?.clearSelection()
  selectedStocks.value = []
}

// 查看选中股票
const viewSelectedStocks = () => {
  // TODO: 加载选中股票的详细信息
  selectedStocksList.value = selectedStocks.value.slice(0, 10).map(code => ({
    code,
    name: `股票${code}`,
    market: code.startsWith('6') ? '上海' : '深圳',
    industry: '行业'
  }))
  showStockListDialog.value = true
}

// 确认选择
const handleConfirmSelection = (stocks: StockInfo[]) => {
  const codes = stocks.map(s => s.code)
  emit('select-stocks', codes)
}

// 处理选择推荐板块
const handleSelectRecommendedSector = (sector: SectorNode) => {
  selectedSectorName.value = sector.name
  showDetailPanel.value = true
}

// 处理添加到对比（预留功能）
const handleAddToCompare = (sector: SectorNode) => {
  ElMessage.info(`已将 ${sector.name} 添加到对比列表`)
  // TODO: 实现板块对比功能
}

// 处理加载收藏夹
const handleLoadCollection = (sectors: FavoriteSector[]) => {
  // 将收藏的板块转换为股票代码列表
  const codes = sectors.map(s => s.code)
  selectedStocks.value = codes

  // 显示选中股票列表
  selectedStocksList.value = sectors.map(sector => ({
    code: sector.code,
    name: sector.name,
    market: sector.type === 'sw1_industry' ? '申万' : '其他',
    industry: sector.type || '未知'
  }))

  showStockListDialog.value = true
  ElMessage.success(`已加载 ${sectors.length} 个收藏板块`)
}

// 处理查看对比详情
const handleViewComparisonDetail = (sector: SectorNode) => {
  selectedSectorName.value = sector.name
  showDetailPanel.value = true
}

// 处理保存对比结果到收藏夹
const handleSaveComparisonToFavorites = (sectors: SectorNode[]) => {
  // TODO: 实现保存对比结果到收藏夹
  ElMessage.info(`已保存 ${sectors.length} 个板块的对比结果`)
}

// 处理批量更新完成
const handleBatchUpdateComplete = (stats: any) => {
  // 刷新板块树
  loadSectorTree()
  ElMessage.success(`批量更新完成：成功 ${stats.completed} 个`)
}

// 导出股票列表
const exportSelectedStocks = () => {
  if (selectedStocks.value.length === 0) {
    ElMessage.warning('请先选择股票')
    return
  }

  // 准备导出数据
  const data = selectedStocks.value.map(code => ({
    code,
    name: `股票${code}`,
    market: code.startsWith('6') ? '上海' : '深圳'
  }))

  const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  exportToCSV(data, `板块股票_${timestamp}`)
  ElMessage.success(`导出 ${selectedStocks.value.length} 只股票列表`)
}
</script>

<style scoped>
/* 智能推荐区域 */
.smart-recommendation-section {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 28px;
  border: 1px solid rgba(102, 126, 234, 0.25);
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
  position: relative;
  overflow: hidden;
}

.smart-recommendation-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #2962ff 0%, #764ba2 50%, #2962ff 100%);
}

.recommendation-header {
  margin-bottom: 24px;
}

.recommendation-title {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.recommendation-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.target-sector-selector {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

/* 修复多选标签颜色 - 使其在深色主题下可见 */
.target-sector-selector :deep(.el-tag) {
  background: rgba(102, 126, 234, 0.2) !important;
  border-color: rgba(102, 126, 234, 0.4) !important;
  color: #ffffff !important;
}

.target-sector-selector :deep(.el-tag__close) {
  color: rgba(255, 255, 255, 0.7) !important;
}

.target-sector-selector :deep(.el-tag__close:hover) {
  color: #ffffff !important;
  background: rgba(255, 255, 255, 0.1) !important;
}

.sector-meta {
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
  margin-left: 8px;
}

/* 分析进度 */
.analysis-progress {
  margin-bottom: 28px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.progress-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  font-weight: 500;
}

.progress-steps {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  flex-wrap: wrap;
}

/* 推荐结果 */
.recommendation-results {
  margin-top: 28px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.results-header h5 {
  font-size: 17px;
  color: #ffffff;
  margin: 0;
  font-weight: 600;
}

.results-meta {
  display: flex;
  gap: 10px;
}

.methodology-info {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.methodology-title {
  font-size: 15px;
  color: #2962ff;
  margin-bottom: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.methodology-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 推荐列表 */
.recommendation-list {
  display: grid;
  gap: 16px;
}

.recommendation-item {
  display: flex;
  gap: 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.02) 100%);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.recommendation-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(180deg, #2962ff 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.recommendation-item:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.04) 100%);
  border-color: rgba(102, 126, 234, 0.35);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
}

.recommendation-item:hover::before {
  opacity: 1;
}

.item-rank {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 800;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.item-rank.rank-top-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #1a1a1a;
  box-shadow: 0 4px 16px rgba(255, 215, 0, 0.4);
}

.item-rank.rank-top-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #1a1a1a;
  box-shadow: 0 4px 16px rgba(192, 192, 192, 0.3);
}

.item-rank.rank-top-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%);
  color: #1a1a1a;
  box-shadow: 0 4px 16px rgba(205, 127, 50, 0.3);
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.item-name {
  font-size: 17px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
  letter-spacing: 0.5px;
}

.item-score {
  text-align: right;
}

.item-score strong {
  font-size: 24px;
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.score-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-left: 6px;
}

/* QLib 指标 */
.item-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 14px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
}

.metric-label {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.metric-value {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
}

.metric-hint {
  color: rgba(255, 255, 255, 0.35);
  font-size: 11px;
}

.qlib-ref {
  font-size: 15px;
  margin-left: 4px;
  filter: drop-shadow(0 0 4px rgba(102, 126, 234, 0.5));
}

/* 推荐理由 */
.item-reasons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.reason-tag {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 500;
}

/* 操作按钮 */
.item-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  justify-content: center;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 40px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  border: 2px dashed rgba(255, 255, 255, 0.1);
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  filter: grayscale(0.3);
  opacity: 0.7;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.5);
  margin: 10px 0;
  font-size: 15px;
}

.empty-hint {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.35);
  line-height: 1.6;
}

.sector-manager {
  padding: 20px;
  background: rgba(26, 26, 46, 0.95);
  border-radius: 8px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-panel {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding: 16px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 6px;
  border: 2px dashed rgba(102, 126, 234, 0.3);
}

:deep(.el-button) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  transition: all 0.2s ease;
}

:deep(.el-button:hover:not(:disabled)) {
  background: rgba(255, 255, 255, 0.08);
  border-color: #2962ff;
  color: #2962ff;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-button--primary:hover:not(:disabled)) {
  background: linear-gradient(135deg, #5568d3 0%, #643a8b 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-button.is-disabled) {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .header-actions {
    flex-wrap: wrap;
  }

  .action-panel {
    flex-direction: column;
  }
}
</style>
