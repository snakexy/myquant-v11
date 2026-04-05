<template>
  <div class="node-workflow">
    <!-- 沉浸式背景 -->
    <div class="immersive-background">
      <div class="particle-system" ref="particleSystem"></div>
      <div class="data-stream-overlay"></div>
      <div class="grid-pattern"></div>
    </div>

    <header class="workflow-header">
      <h1>节点工作流</h1>
      <div class="header-controls">
        <button class="btn-set-default" @click="setDefaultLayout" title="设为默认布局">
          <font-awesome-icon icon="thumbtack" />
        </button>
        <button class="btn-restore-default" @click="restoreDefaultLayout" title="恢复默认布局">
          <font-awesome-icon icon="rotate-left" />
        </button>
        <button class="btn-save" @click="saveWorkflow" title="保存工作流">
          <font-awesome-icon icon="save" />
        </button>
        <button class="btn-load" @click="triggerLoadWorkflow" title="加载工作流">
          <font-awesome-icon icon="folder-open" />
        </button>
        <button class="btn-reset" @click="resetLayout" title="重置布局">
          <font-awesome-icon icon="undo" />
        </button>
          <button class="btn-back" @click="goBack">返回研究</button>
        <input
          ref="fileInput"
          type="file"
          accept=".json"
          style="display: none"
          @change="handleFileLoad"
        />
      </div>
    </header>

    <main class="main-content">
      <div class="workflow-canvas">
        <!-- 连线层 - 在画布容器外面 -->
        <svg
          class="connections-layer"
          :style="{
            position: 'absolute',
            top: '0',
            left: '0',
            width: '100vw',
            height: 'calc(100vh - 80px)',
            pointerEvents: 'none'
          }"
        >
          <defs>
          </defs>
          <g
            :style="{
              transform: `translate(${canvasOffset.x}px, ${canvasOffset.y}px) scale(${canvasScale})`,
              transformOrigin: '0 0'
            }"
          >
            <path
              v-for="connection in connections"
              :key="`${connection.from}-${connection.to}`"
              :d="getConnectionPath(connection)"
              :stroke="connection.enabled === false ? '#666' : '#3b82f6'"
              :stroke-width="connection.enabled === false ? '1' : '2'"
              :stroke-dasharray="connection.enabled === false ? '5,5' : 'none'"
              fill="none"
              stroke-linecap="round"
              :opacity="connection.enabled === false ? '0.3' : '0.7'"
            />
          </g>
        </svg>

        <div
          class="canvas-container"
          :style="{
            transform: `translate(${canvasOffset.x}px, ${canvasOffset.y}px) scale(${canvasScale})`,
            transformOrigin: '0 0'
          }"
          @mousedown="startCanvasDrag"
          @wheel="handleWheel"
        >

          <!-- 节点 -->
          <div
            v-for="node in nodes"
            :key="node.id"
            :id="node.id"
            class="workflow-node"
            :data-node-id="node.id"
            :class="{ 'active': activeNode === node.id, 'dragging': isDragging && draggedNode === node.id }"
            :style="{
              position: 'absolute',
              left: `${nodePositions[node.id]?.x || node.x}px`,
              top: `${nodePositions[node.id]?.y || node.y}px`,
              transition: isDragging && draggedNode === node.id ? 'none' : 'all 0.2s ease'
            }"
            @mousedown="startDrag($event, node)"
            @click="selectNode(node.id)"
            @dblclick="openNodeDetail(node)"
          >
            <!-- 节点输入端口（上方） -->
            <!-- 如果节点有多个输入端口，显示多个端口 -->
            <template v-if="node.inputs && node.inputs.length > 0">
              <div
                v-for="(input, index) in node.inputs"
                :key="input.id"
                class="node-port node-input-port multi-port"
                :class="{ 'port-active': input.active, 'port-inactive': !input.active }"
                @mouseenter="onPortHover"
                @mouseleave="onPortLeave"
                @click.stop="toggleInputPort(node.id, input.id)"
              ></div>
            </template>
            <!-- 默认单个输入端口 -->
            <div v-else class="node-port node-input-port" @mouseenter="onPortHover" @mouseleave="onPortLeave"></div>

            <!-- 节点输出端口（下方） -->
            <div class="node-port node-output-port" @mouseenter="onPortHover" @mouseleave="onPortLeave"></div>

            <div class="node-header">
              <div class="node-icon">{{ node.icon }}</div>
              <div class="node-title">{{ node.title }}</div>
            </div>
            <div class="node-description">{{ node.description }}</div>

            <!-- 股票选择节点的获取数据按钮 -->
            <div v-if="node.id === 'stock-selection'" class="node-actions">
              <button
                @click.stop="fetchStockData"
                class="btn-fetch"
                :disabled="isFetchingData"
                title="获取真实股票数据"
              >
                <font-awesome-icon v-if="!isFetchingData" icon="sync-alt" />
                <font-awesome-icon v-else icon="spinner" spin />
                {{ isFetchingData ? '获取中...' : '获取数据' }}
              </button>
            </div>

            <!-- 指数选择节点的获取数据按钮 -->
            <div v-if="node.id === 'index-selection'" class="node-actions">
              <button
                @click.stop="fetchIndexData"
                class="btn-fetch"
                :disabled="isFetchingIndexData"
                title="获取指数数据"
              >
                <font-awesome-icon v-if="!isFetchingIndexData" icon="sync-alt" />
                <font-awesome-icon v-else icon="spinner" spin />
                {{ isFetchingIndexData ? '获取中...' : '获取数据' }}
              </button>
            </div>

            <!-- 数据清洗节点的运行按钮 -->
            <div v-if="node.id === 'data-cleaning'" class="node-actions">
              <button
                @click.stop="runDataCleaning"
                class="btn-fetch"
                :disabled="isDataCleaningRunning"
                title="运行数据清洗"
              >
                <font-awesome-icon v-if="!isDataCleaningRunning" icon="play" />
                <font-awesome-icon v-else icon="spinner" spin />
                {{ isDataCleaningRunning ? '清洗中...' : '运行清洗' }}
              </button>
            </div>

            <!-- 数据内容区域 -->
            <div class="node-content" v-if="node.data">
              <!-- 🔧 数据清洗节点：使用节点自带的 MiniDataReport 组件 -->
              <DataCleaningMiniReport
                v-if="node.id === 'data-cleaning'"
                :key="`${node.id}-${node.updateKey || 0}`"
                :metadata="getDataCleaningNodeMetadata(node)"
              />

              <!-- 加载状态 -->
              <div v-else-if="node.data.type === 'loading'" class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">正在获取数据{{ node.data.content?.percent ? ` ${node.data.content.percent}%` : '...' }}</div>
                <div v-if="node.data.content?.total" class="loading-progress">
                  <div class="progress-bar-bg">
                    <div class="progress-bar-fill" :style="{ width: node.data.content.percent + '%' }"></div>
                  </div>
                </div>
              </div>

              <!-- 统计数据 -->
              <div v-else-if="node.data.type === 'stats'" class="stats-container">
                <!-- 🔧 股票选择节点：使用通用小组件组件 -->
                <MiniDataReportCards
                  v-if="node.id === 'stock-selection'"
                  :key="`${node.id}-${node.updateKey || 0}`"
                  :node-type="node.id"
                  :metadata="getDataCleaningNodeMetadata(node)"
                  :params="node.params"
                  :frequencies="node.params?.frequencies || []"
                  :content="node.data.content"
                />

                <!-- 🔧 指数选择节点：使用通用小组件组件 -->
                <MiniDataReportCards
                  v-else-if="node.id === 'index-selection'"
                  :key="`${node.id}-${node.updateKey || 0}`"
                  :node-type="node.id"
                  :metadata="getDataCleaningNodeMetadata(node)"
                  :params="node.params"
                  :frequencies="node.params?.frequencies || []"
                  :content="node.data.content"
                />

                <!-- 其他节点：默认显示 -->
                <div v-else>
                  <div v-for="(value, key) in node.data.content" :key="key" class="stat-item">
                    <span class="stat-label">{{ formatStatLabel(key) }}:</span>
                    <span class="stat-value" :style="{ color: getValueColor(value) }">{{ formatStatValue(value) }}</span>
                  </div>
                </div>
              </div>

              <!-- 表格数据 -->
              <div v-else-if="node.data.type === 'table'" class="table-container">
                <div v-for="(row, index) in node.data.content.slice(0, 2)" :key="index" class="table-row">
                  <div v-for="(value, key) in row" :key="key" class="table-cell" :style="{ color: formatTableValue(value).color }">
                    {{ formatTableValue(value).text }}
                  </div>
                </div>

                <!-- 🔧 重构：使用通用小组件组件 -->
                <!-- 股票选择节点和指数选择节点的小组件 -->
                <MiniDataReportCards
                  v-if="node.id === 'stock-selection' || node.id === 'index-selection'"
                  :key="`${node.id}-${node.updateKey || 0}`"
                  :node-type="node.id"
                  :metadata="getDataCleaningNodeMetadata(node)"
                  :params="node.params"
                  :frequencies="node.params?.frequencies || []"
                  :content="node.data.content"
                />
              </div>

              <!-- 文本数据 -->
              <div v-else-if="node.data.type === 'text'" class="text-container">
                {{ node.data.content }}
              </div>

              <!-- 列表数据 -->
              <div v-else-if="node.data.type === 'list'" class="list-container">
                <div v-for="(item, index) in node.data.content" :key="index" class="list-item">
                  {{ item }}
                </div>
              </div>

              <!-- 图表数据 -->
              <div v-else-if="node.data.type === 'chart'" class="chart-container">
                <div class="chart-summary">
                  <div class="chart-item">
                    <span class="chart-label">识别模式:</span>
                    <div class="chart-patterns">
                      <span v-for="(pattern, index) in node.data.content.patterns" :key="index" class="pattern-tag">
                        {{ pattern }}
                      </span>
                    </div>
                  </div>
                  <div class="chart-stats">
                    <div class="chart-stat">
                      <span>准确率: </span>
                      <span :style="{ color: node.data.content.accuracy >= 90 ? '#ef4444' : node.data.content.accuracy >= 80 ? '#f59e0b' : '#6b7280' }">
                        {{ node.data.content.accuracy }}%
                      </span>
                    </div>
                    <div class="chart-stat">
                      <span>置信度: </span>
                      <span :style="{ color: node.data.content.confidence >= 90 ? '#ef4444' : node.data.content.confidence >= 80 ? '#f59e0b' : '#6b7280' }">
                        {{ node.data.content.confidence }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 节点详情弹窗 -->
    <NodeDetailModal
      v-model:visible="showNodeDetail"
      :node="selectedNode"
      :connections="connections"
      :nodes="nodes"
      @update-node="updateNodeConfig"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import NodeDetailModal from '../components/node/NodeDetailModal.vue'
import MiniDataReportCards from '../components/node/MiniDataReportCards.vue'
import DataCleaningMiniReport from '../research-nodes/DataCleaningNode/MiniDataReport.vue' // 🔧 新增：导入数据清洗节点的小报告组件
import { getStockDetail, getBatchStockNames, getRealtimeData, getStockHistory } from '../api/modules/data'
import { fileManager, type WorkflowFile } from '../utils/fileManager'
// 导入研究阶段节点模块
import { getAllNodeModules, StockSelectionNode, IndexSelectionNode, DataCleaningNode, type NodeContext, type NodeModule } from '../research-nodes'
// 导入节点辅助函数
import {
  extractCount as stockExtractCount,
  extractUnit as stockExtractUnit,
  getStatusTagClass as stockGetStatusTagClass,
  getStatusShortLabel as stockGetStatusShortLabel,
  getStockCountFromTable,
  formatDataCount,
  formatDateRange,
  getFrequencyFromParams as stockGetFrequencyFromParams
} from '../research-nodes/StockSelectionNode'
import {
  extractCount as indexExtractCount,
  extractUnit as indexExtractUnit,
  getStatusTagClass as indexGetStatusTagClass,
  getStatusShortLabel as indexGetStatusShortLabel,
  getIndexCountFromTable,
  getFrequencyFromParams as indexGetFrequencyFromParams
} from '../research-nodes/IndexSelectionNode'

const router = useRouter()

// 辅助函数供模板使用
const extractCount = (value: string) => stockExtractCount(value)
const extractUnit = (value: string) => stockExtractUnit(value)
const getStatusTagClass = (status: string) => stockGetStatusTagClass(status)
const getStatusShortLabel = (status: string) => stockGetStatusShortLabel(status)

// 🔧 修复：根据节点类型使用正确的 getFrequencyFromParams
const getFrequencyFromParams = (node: any): string => {
  if (node.id === 'index-selection') {
    return indexGetFrequencyFromParams(node)
  }
  return stockGetFrequencyFromParams(node)
}

// 🔧 修复：确保日期范围只显示日期，不显示时间
const safeFormatDateRange = (startDate: string | undefined, endDate: string | undefined): string => {
  if (!startDate || !endDate || startDate === '--' || endDate === '--') return '--'

  // 提取日期部分，忽略时间和T
  // 支持格式: "2025-01-01T10:30:00" 或 "2025-01-01 10:30:00" 或 "2025-01-01"
  const extractDate = (dateStr: string) => {
    // 移除T或空格之后的时间部分
    const tIndex = dateStr.indexOf('T')
    if (tIndex !== -1) {
      return dateStr.substring(0, tIndex)
    }
    const spaceIndex = dateStr.indexOf(' ')
    if (spaceIndex !== -1) {
      return dateStr.substring(0, spaceIndex)
    }
    return dateStr
  }

  const startClean = extractDate(startDate)
  const endClean = extractDate(endDate)

  // 简化日期格式，只显示月日，例如 "2025-01-01" -> "01-01"
  const start = startClean.split('-').slice(1).join('-')
  const end = endClean.split('-').slice(1).join('-')
  return `${start} 至 ${end}`
}

interface Node {
  id: string
  x: number
  y: number
  icon: string
  title: string
  description: string
  inputs?: Array<{
    id: string
    label: string
    active: boolean
    description?: string
  }>
  params?: any
  metadata?: any
  data?: {
    type: 'chart' | 'table' | 'stats' | 'text' | 'list'
    content: any
  }
  updateKey?: number // 用于强制组件重新渲染
}

// 节点默认位置配置（研究阶段工作流程的标准布局）
const DEFAULT_NODE_POSITIONS: Record<string, { x: number; y: number }> = {
  'stock-selection': { x: 100, y: 100 },
  'index-selection': { x: 100, y: 280 },
  'data-cleaning': { x: 350, y: 100 },
  'factor-engine': { x: 600, y: 100 },
  'feature-engineering': { x: 850, y: 100 },
  'signal-engine': { x: 600, y: 280 },
  'ai-analysis': { x: 850, y: 280 },
  'ai-strategy-assistant': { x: 100, y: 480 },
  'model-training': { x: 350, y: 480 },
  'preliminary-validation': { x: 600, y: 480 }
}

// 从研究节点模块创建初始节点
const createInitialNodes = (): Node[] => {
  const nodeModules = getAllNodeModules()

  return nodeModules.map(module => {
    const pos = DEFAULT_NODE_POSITIONS[module.id] || { x: 100, y: 100 }
    return {
      id: module.id,
      x: pos.x,
      y: pos.y,
      icon: module.icon,
      title: module.title,
      description: module.description,
      params: module.params || {},
      metadata: module.metadata || {},
      data: module.data || { type: 'stats', content: {} },
      inputs: module.inputs || []
    }
  })
}

// 节点数据
const nodes = ref<Node[]>(createInitialNodes())

// 格式化成交额
const formatTurnover = (turnover: number) => {
  if (turnover >= 100000000) {
    return `${(turnover / 100000000).toFixed(1)}亿`
  } else if (turnover >= 10000) {
    return `${(turnover / 10000).toFixed(0)}万`
  } else {
    return turnover.toString()
  }
}

// 根据时间范围计算日期
const calculateDateRange = (timeRange: string) => {
  const endDate = new Date()
  const startDate = new Date()

  switch (timeRange) {
    case '1D':
      startDate.setDate(endDate.getDate() - 1)
      break
    case '1W':
      startDate.setDate(endDate.getDate() - 7)
      break
    case '1M':
      startDate.setMonth(endDate.getMonth() - 1)
      break
    case '3M':
      startDate.setMonth(endDate.getMonth() - 3)
      break
    case '6M':
      startDate.setMonth(endDate.getMonth() - 6)
      break
    case '1Y':
      startDate.setFullYear(endDate.getFullYear() - 1)
      break
    default:
      startDate.setMonth(endDate.getMonth() - 1) // 默认1个月
  }

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0]
  }
}

// 获取股票历史数据
const fetchStockHistoryData = async (code: string, startDate: string, endDate: string) => {
  try {
    // 确保code是字符串类型
    const codeStr = String(code).trim()
    console.log(`[fetchStockHistoryData] 获取股票历史数据: ${codeStr}, ${startDate} ~ ${endDate}`)

    const response = await getStockHistory({
      symbol: codeStr,
      start_date: startDate,
      end_date: endDate,
      frequency: 'daily'
    }, 15000) // 15秒超时

    if (response.success && response.data && response.data.length > 0) {
      console.log(`[fetchStockHistoryData] 成功获取 ${response.data.length} 条历史数据`)
      return response.data
    } else {
      console.warn(`[fetchStockHistoryData] 未获取到历史数据:`, response)
      return null
    }
  } catch (error) {
    console.error(`获取股票 ${code} 历史数据失败:`, error)
    return null
  }
}

// 生成股票预览数据（支持新旧参数结构）
const generateStockPreviewData = async (useTimeRange = false) => {
  const stockNode = nodes.value.find(n => n.id === 'stock-selection')

  // 支持新的简化参数结构
  if (!stockNode) {
    return []
  }

  // 优先使用新的symbols参数，回退到旧的stockCode参数
  let codes = []
  if (stockNode.params?.symbols && Array.isArray(stockNode.params.symbols)) {
    codes = stockNode.params.symbols.slice(0, 5) // 最多显示5只
  } else if (stockNode.params?.stockCode) {
    codes = stockNode.params.stockCode.split(/[,，]/)
      .map(code => code.trim())
      .filter(code => code)
      .slice(0, 5) // 最多显示5只
  }

  if (codes.length === 0) {
    return []
  }

  // 如果使用时间范围，计算日期范围（支持新旧参数）
  let dateRange = null
  if (useTimeRange) {
    if (stockNode.params?.start_date && stockNode.params?.end_date) {
      // 新的参数结构
      dateRange = {
        start: stockNode.params.start_date,
        end: stockNode.params.end_date
      }
    } else if (stockNode.params?.timeRange) {
      // 旧的参数结构
      dateRange = calculateDateRange(stockNode.params.timeRange)
    }
  }

  try {
    // 获取真实股票数据
    const stockPromises = codes.map(async (code) => {
      try {
        // 获取股票基本信息
        const stockDetail = await getStockDetail(code)

        // 获取实时数据
        const realtimeResponse = await getRealtimeData([code])

        // 查找对应股票的实时数据
        const realtimeInfo = realtimeResponse.data?.find(item => item.code === code)

        // 如果使用时间范围，获取历史数据
        let historyData = null
        if (useTimeRange && dateRange) {
          historyData = await fetchStockHistoryData(code, dateRange.startDate, dateRange.endDate)
        }

        console.log(`[NodeWorkflow] 股票 ${code} API原始数据:`, {
          stockDetail,
          realtimeResponse,
          realtimeInfo
        })

        // 股票名称映射（作为后备，尽量使用API返回的真实数据）
        const stockNames: Record<string, string> = {
          '000001': '平安银行',
          '000002': '万科A',
          '601318': '中国平安',
          '600519': '贵州茅台',
          '002594': '比亚迪',
          '600036': '招商银行',
          '000858': '五粮液',
          '002415': '海康威视',
          '601166': '兴业银行',
          '600276': '恒瑞医药',
          'SH000001': '上证指数',
          'SZ399001': '深证成指',
          'SH000300': '沪深300',
          'SZ399006': '创业板指'
        }

        // 优先使用stockDetail数据（API返回的真实QMT数据）
        if (stockDetail.success && stockDetail.data) {
          const currentPrice = stockDetail.data.current_price || 0
          const lastClose = stockDetail.data.last_close || stockDetail.data.pre_close || 0

          // 直接使用API返回的真实涨跌幅数据，不重新计算
          let change = stockDetail.data.change || 0
          let changePercent = stockDetail.data.change_percent || 0

          // 如果API没有返回change，但有current_price和last_close，才计算change
          if (!change && currentPrice && lastClose > 0) {
            change = currentPrice - lastClose
          }

          const result = {
            code,
            name: stockDetail.data.name || stockNames[code] || code,
            close: currentPrice.toFixed(2),
            change: change >= 0 ? `+${change.toFixed(2)}` : change.toFixed(2),
            changePercent: changePercent >= 0 ? `+${changePercent.toFixed(2)}%` : `${changePercent.toFixed(2)}%`,
            turnover: formatTurnover(stockDetail.data.turnover || 0),
            isRealData: true,
            error: null
          }

          console.log(`[NodeWorkflow] 股票 ${code} 使用stockDetail数据:`, result)
          return result
        }

        // 如果有实时数据，使用实时数据
        if (realtimeInfo) {
          const currentPrice = realtimeInfo.price || 0
          const lastClose = realtimeInfo.last_close || 0
          const change = currentPrice - lastClose
          const changePercent = lastClose > 0 ? (change / lastClose) * 100 : 0

          const result = {
            code,
            name: realtimeInfo.name || stockNames[code] || code,
            close: currentPrice.toFixed(2),
            change: change >= 0 ? `+${change.toFixed(2)}` : change.toFixed(2),
            changePercent: changePercent >= 0 ? `+${changePercent.toFixed(2)}%` : `${changePercent.toFixed(2)}%`,
            turnover: realtimeInfo.turnover || '0万',
            isRealData: true,
            error: null
          }

          console.log(`[NodeWorkflow] 股票 ${code} 使用实时数据:`, result)
          return result
        }

      // 如果没有真实数据，返回明确的错误信息，不显示虚拟数据
        return {
          code,
          name: stockNames[code] || code,
          close: '--',
          change: '--',
          changePercent: '--',
          turnover: '--',
          isRealData: false,
          error: '无法获取真实股票数据'
        }

      } catch (error) {
        console.warn(`获取股票 ${code} 数据失败:`, error)

        // 降级到基本信息显示
        return {
          code,
          name: code,
          close: '0.00',
          change: '0.00',
          changePercent: '0.00%',
          turnover: '0万',
          isRealData: false,
          error: 'API调用失败'
        }
      }
    })

    const results = await Promise.all(stockPromises)
    return results

  } catch (error) {
    console.error('批量获取股票数据失败:', error)

    // 完全失败时返回基本信息
    return codes.map(code => {
      // 最小化的股票名称映射，仅作为后备
      const minimalStockNames: Record<string, string> = {
        '000001': '平安银行',
        '000002': '万科A',
        '601318': '中国平安',
        '600519': '贵州茅台',
        '002594': '比亚迪',
        '600036': '招商银行',
        '000858': '五粮液',
        '002415': '海康威视',
        '601166': '兴业银行',
        '600276': '恒瑞医药',
        'SH000001': '上证指数',
        'SZ399001': '深证成指',
        'SH000300': '沪深300',
        'SZ399006': '创业板指'
      }

      return {
        code,
        name: minimalStockNames[code] || code,
        close: '0.00',
        change: '0.00',
        changePercent: '0.00%',
        turnover: '0万',
        isRealData: false,
        error: '全部API调用失败'
      }
    })
  }
}

// 创建节点上下文
const createNodeContext = (): NodeContext => ({
  nodes,
  connections,
  getUpstreamNodes: (nodeId: string) => {
    return connections.value
      .filter(c => c.to === nodeId)
      .map(c => nodes.value.find(n => n.id === c.from))
      .filter(n => n)
  },
  getDownstreamNodes: (nodeId: string) => {
    return connections.value
      .filter(c => c.from === nodeId)
      .map(c => nodes.value.find(n => n.id === c.to))
      .filter(n => n)
  },
  globalState: {}
})

// 更新股票选择节点的显示数据 - 使用节点模块
const updateStockNodeDisplay = async () => {
  const stockNode = nodes.value.find(n => n.id === 'stock-selection')
  if (!stockNode) return

  const context = createNodeContext()
  await StockSelectionNode.updateDisplay?.(stockNode, context)
}

// 获取股票数据（按钮触发）- 使用节点模块
const fetchStockData = async () => {
  if (isFetchingData.value) return

  isFetchingData.value = true

  try {
    const stockNode = nodes.value.find(n => n.id === 'stock-selection')

    if (!stockNode) {
      console.error('[NodeWorkflow] 找不到股票选择节点')
      ElMessage({
        message: '系统错误：找不到股票选择节点',
        type: 'error',
        duration: 3000
      })
      isFetchingData.value = false
      return
    }

    // 显示加载状态
    stockNode.data = stockNode.data || { type: 'table', content: [] }
    stockNode.data.content = [{
      '股票代码': '加载中...',
      '收盘价': '正在获取数据',
      '涨跌幅': '--',
      '成交量': '--'
    }]

    // 使用节点模块获取数据
    const context = createNodeContext()
    const result = await StockSelectionNode.fetchData?.(stockNode, context)

    if (result?.success) {
      ElMessage({
        message: result.message || '数据获取成功',
        type: 'success',
        duration: 3000
      })
    } else {
      ElMessage({
        message: result?.errors?.join(', ') || '数据获取失败',
        type: 'error',
        duration: 3000
      })
    }
  } catch (error) {
    console.error('[NodeWorkflow] 股票数据获取失败:', error)
    ElMessage({
      message: '股票数据获取失败，请检查API服务器状态',
      type: 'error',
      duration: 5000,
      showClose: true
    })
  } finally {
    isFetchingData.value = false
  }
}

// 更新指数选择节点的显示数据 - 使用节点模块
const updateIndexNodeDisplay = async () => {
  const indexNode = nodes.value.find(n => n.id === 'index-selection')
  if (!indexNode) return

  const context = createNodeContext()
  await IndexSelectionNode.updateDisplay?.(indexNode, context)
}

// 更新数据清洗节点的显示数据 - 使用节点模块
const updateDataCleaningNodeDisplay = async () => {
  const dataCleaningNode = nodes.value.find(n => n.id === 'data-cleaning')
  if (!dataCleaningNode) return

  const context = createNodeContext()
  await DataCleaningNode.updateDisplay?.(dataCleaningNode, context)
}

// 获取指数数据（按钮触发）- 使用节点模块
const fetchIndexData = async () => {
  if (isFetchingIndexData.value) return

  isFetchingIndexData.value = true

  try {
    const indexNode = nodes.value.find(n => n.id === 'index-selection')

    if (!indexNode) {
      console.error('[NodeWorkflow] 找不到指数选择节点')
      ElMessage({
        message: '系统错误：找不到指数选择节点',
        type: 'error',
        duration: 3000
      })
      isFetchingIndexData.value = false
      return
    }

    // 显示加载状态
    indexNode.data = indexNode.data || { type: 'table', content: [] }
    indexNode.data.content = [{
      '指数代码': '加载中...',
      '收盘点位': '正在获取数据',
      '涨跌幅': '--',
      '成交量': '--'
    }]

    // 使用节点模块获取数据
    const context = createNodeContext()
    const result = await IndexSelectionNode.fetchData?.(indexNode, context)

    if (result?.success) {
      ElMessage({
        message: result.message || '数据获取成功',
        type: 'success',
        duration: 3000
      })
    } else {
      ElMessage({
        message: result?.errors?.join(', ') || '数据获取失败',
        type: 'error',
        duration: 3000
      })
    }
  } catch (error) {
    console.error('[NodeWorkflow] 指数数据获取失败:', error)
    ElMessage({
      message: '指数数据获取失败，请检查API服务器状态',
      type: 'error',
      duration: 5000,
      showClose: true
    })
  } finally {
    isFetchingIndexData.value = false
  }
}

// 获取股票代码从节点
const getStockCodesFromNodes = () => {
  const stockNode = nodes.value.find(n => n.id === 'stock-selection')
  const indexNode = nodes.value.find(n => n.id === 'index-selection')
  
  const codes = []
  
  // 从股票选择节点获取股票代码
  if (stockNode?.params?.symbols && Array.isArray(stockNode.params.symbols)) {
    codes.push(...stockNode.params.symbols)
  } else if (stockNode?.params?.stockCode) {
    const stockCodes = stockNode.params.stockCode.split(/[,，]/)
      .map(code => code.trim())
      .filter(code => code)
    codes.push(...stockCodes)
  }
  
  // 从指数选择节点获取指数代码
  if (indexNode?.params?.indexCode) {
    const indexCodes = indexNode.params.indexCode.split(/[,，]/)
      .map(code => code.trim())
      .filter(code => code)
    codes.push(...indexCodes)
  }
  
  return codes.length > 0 ? codes : ['000001.SZ'] // 默认返回平安银行
}

// 获取开始日期从节点
const getStartDateFromNodes = () => {
  const stockNode = nodes.value.find(n => n.id === 'stock-selection')
  const indexNode = nodes.value.find(n => n.id === 'index-selection')

  // 优先使用股票选择节点的日期
  if (stockNode?.params?.start_date) {
    return stockNode.params.start_date
  }
  if (stockNode?.params?.startDate) {
    return stockNode.params.startDate
  }

  // 如果股票节点有timeRange参数,计算日期
  if (stockNode?.params?.timeRange) {
    const timeRange = stockNode.params.timeRange
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    // 解析timeRange (如 1W, 3M, 1Y)
    const match = timeRange.match(/^(\d+)([WMY])$/)
    if (match) {
      const value = parseInt(match[1])
      const unit = match[2]
      const startDate = new Date(today)

      switch (unit) {
        case 'W':
          startDate.setDate(today.getDate() - value * 7)
          break
        case 'M':
          startDate.setMonth(today.getMonth() - value)
          break
        case 'Y':
          startDate.setFullYear(today.getFullYear() - value)
          break
      }
      return startDate.toISOString().split('T')[0]
    }
  }

  // 使用指数选择节点的日期
  if (indexNode?.params?.start_date) {
    return indexNode.params.start_date
  }
  if (indexNode?.params?.startDate) {
    return indexNode.params.startDate
  }

  // 默认返回一年前的日期
  const date = new Date()
  date.setFullYear(date.getFullYear() - 1)
  return date.toISOString().split('T')[0]
}

// 获取结束日期从节点
const getEndDateFromNodes = () => {
  const stockNode = nodes.value.find(n => n.id === 'stock-selection')
  const indexNode = nodes.value.find(n => n.id === 'index-selection')
  
  // 优先使用股票选择节点的日期
  if (stockNode?.params?.end_date) {
    return stockNode.params.end_date
  }
  if (stockNode?.params?.endDate) {
    return stockNode.params.endDate
  }
  
  // 使用指数选择节点的日期
  if (indexNode?.params?.end_date) {
    return indexNode.params.end_date
  }
  if (indexNode?.params?.endDate) {
    return indexNode.params.endDate
  }
  
  // 默认返回今天的日期
  return new Date().toISOString().split('T')[0]
}

// 运行数据清洗（按钮触发）- 使用节点模块
const runDataCleaning = async () => {
  if (isDataCleaningRunning.value) return

  console.log('[DataCleaning] 开始运行数据清洗')

  isDataCleaningRunning.value = true

  try {
    const dataCleaningNode = nodes.value.find(n => n.id === 'data-cleaning')

    if (!dataCleaningNode) {
      console.error('[NodeWorkflow] 找不到数据清洗节点')
      ElMessage({
        message: '系统错误：找不到数据清洗节点',
        type: 'error',
        duration: 3000
      })
      isDataCleaningRunning.value = false
      return
    }

    // 显示运行状态
    dataCleaningNode.data = dataCleaningNode.data || { type: 'stats', content: {} }
    dataCleaningNode.data.content = {
      '状态': '正在运行数据清洗...',
      '进度': '0%'
    }

    // 使用数据清洗节点的fetchData函数
    const context = createNodeContext()
    const result = await DataCleaningNode.fetchData?.(dataCleaningNode, context)

    if (result?.success) {
      ElMessage({
        message: result.message || '数据清洗运行成功',
        type: 'success',
        duration: 3000
      })

      // 不覆盖 data.ts 中设置的完整数据
      // data.ts 已经在 node.data.content 中设置了所有必要的字段
      console.log('[NodeWorkflow] 数据清洗成功，节点数据已由 data.ts 更新')
    } else {
      throw new Error(result?.errors?.join(', ') || '数据清洗运行失败')
    }
  } catch (error) {
    console.error('[NodeWorkflow] 数据清洗运行失败:', error)
    ElMessage({
      message: `数据清洗运行失败: ${error instanceof Error ? error.message : '未知错误'}`,
      type: 'error',
      duration: 5000,
      showClose: true
    })

    // 更新错误状态
    const dataCleaningNode = nodes.value.find(n => n.id === 'data-cleaning')
    if (dataCleaningNode) {
      dataCleaningNode.data = dataCleaningNode.data || { type: 'stats', content: {} }
      dataCleaningNode.data.content = {
        '状态': '运行失败',
        '错误': error instanceof Error ? error.message : '未知错误'
      }
    }
  } finally {
    isDataCleaningRunning.value = false
  }
}

// 监听股票配置变化
watch(() => {
  const stockNode = nodes.value.find(n => n.id === 'stock-selection')
  // 监听symbols、stockCode和日期范围的变化
  return stockNode?.params?.symbols || stockNode?.params?.stockCode || stockNode?.params?.startDate || stockNode?.params?.endDate
}, () => {
  updateStockNodeDisplay()
}, { deep: true })

// 监听指数配置变化
watch(() => {
  const indexNode = nodes.value.find(n => n.id === 'index-selection')
  // 监听indexCode和日期范围的变化
  return indexNode?.params?.indexCode || indexNode?.params?.startDate || indexNode?.params?.endDate
}, () => {
  updateIndexNodeDisplay()
}, { deep: true })

// 监听数据清洗配置变化
watch(() => {
  const dataCleaningNode = nodes.value.find(n => n.id === 'data-cleaning')
  // 监听清洗策略和参数的变化
  return dataCleaningNode?.params?.cleaningStrategy || dataCleaningNode?.params?.frequency || dataCleaningNode?.params?.threshold
}, () => {
  updateDataCleaningNodeDisplay()
}, { deep: true })

// 初始化时更新一次
onMounted(() => {
  updateStockNodeDisplay()
  updateIndexNodeDisplay()
  updateDataCleaningNodeDisplay()
})

// 拖拽状态
const isDragging = ref(false)
const draggedNode = ref<string | null>(null)
const dragOffset = reactive({ x: 0, y: 0 })

// 画布控制状态
const canvasScale = ref(1)
const canvasOffset = reactive({ x: 200, y: 100 }) // 初始偏移，调整到更合适的位置
const isCanvasDragging = ref(false)
const canvasDragStart = reactive({ x: 0, y: 0 })
const canvasOffsetStart = reactive({ x: 0, y: 0 })

// 连线定义 - 按照研究阶段工作流程设计文档
const connections = ref([
  // 股票选择 → 数据清洗 (股票数据输入端口)
  { from: 'stock-selection', to: 'data-cleaning', toInputId: 'stock-driven' },
  // 指数选择 → 数据清洗 (指数数据输入端口)
  { from: 'index-selection', to: 'data-cleaning', toInputId: 'index-driven' },
  // 数据清洗 → 因子计算引擎 (数据驱动输入端口)
  { from: 'data-cleaning', to: 'factor-engine', toInputId: 'data-driven' },
  // AI助手策略构思 → 因子计算引擎 (AI驱动输入端口)
  { from: 'ai-strategy-assistant', to: 'factor-engine', toInputId: 'ai-driven' },
  // 因子计算引擎 → 特征工程
  { from: 'factor-engine', to: 'feature-engineering' },
  // 特征工程 → 智能信号引擎
  { from: 'feature-engineering', to: 'signal-engine' },
  // 智能信号引擎 → AI智能分析
  { from: 'signal-engine', to: 'ai-analysis' },
  // AI智能分析 → 模型训练 (AI分析输入端口)
  { from: 'ai-analysis', to: 'model-training', toInputId: 'ai-insights' },
  // 特征工程 → 模型训练 (特征输入端口)
  { from: 'feature-engineering', to: 'model-training', toInputId: 'features' },
  // 模型训练 → 初步验证
  { from: 'model-training', to: 'preliminary-validation' }
])

// 活跃节点
const activeNode = ref<string>('')

// 节点详情弹窗
const showNodeDetail = ref(false)
const selectedNode = ref<Node | null>(null)
const isFetchingData = ref(false)
const isFetchingIndexData = ref(false)
const isDataCleaningRunning = ref(false)

// 文件输入引用
const fileInput = ref<HTMLInputElement | null>(null)

// 节点位置状态（响应式）
const nodePositions = ref<Record<string, { x: number; y: number; scale: number; isExpanded: boolean }>>({})

// 获取节点的实际尺寸
const getNodeDimensions = (nodeId: string) => {
  // 查找实际的DOM元素
  const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`) as HTMLElement
  if (nodeElement) {
    return {
      width: nodeElement.offsetWidth,
      height: nodeElement.offsetHeight
    }
  }

  // 回退到估算值
  const node = nodes.value.find(n => n.id === nodeId)
  if (!node) return { width: 220, height: 80 }

  // 根据数据内容估算尺寸
  const nodeWidth = node.data ? 280 : 220
  const nodeHeight = node.data ? 160 : 80

  return { width: nodeWidth, height: nodeHeight }
}

// 获取节点的输出位置（下方中间）
const getNodeOutputPosition = (nodeId: string) => {
  const nodePos = nodePositions.value[nodeId]
  if (!nodePos) return { x: 0, y: 0 }

  const dimensions = getNodeDimensions(nodeId)

  return {
    x: nodePos.x + dimensions.width / 2,
    y: nodePos.y + dimensions.height
  }
}

// 获取节点的输入位置（上方中间）
const getNodeInputPosition = (nodeId: string) => {
  const nodePos = nodePositions.value[nodeId]
  if (!nodePos) return { x: 0, y: 0 }

  const dimensions = getNodeDimensions(nodeId)

  return {
    x: nodePos.x + dimensions.width / 2,
    y: nodePos.y
  }
}

// 智能端口检测 - 根据节点位置确定最佳连接方向
const detectOptimalPorts = (fromNodeId: string, toNodeId: string) => {
  const fromNode = nodePositions.value[fromNodeId]
  const toNode = nodePositions.value[toNodeId]

  if (!fromNode || !toNode) {
    return { fromPort: 'right', toPort: 'left' }
  }

  // 获取节点中心点
  const fromCenterX = fromNode.x + 140 // 假设节点宽度280
  const fromCenterY = fromNode.y + 80  // 假设节点高度160
  const toCenterX = toNode.x + 140
  const toCenterY = toNode.y + 80

  // 计算方向向量
  const dx = toCenterX - fromCenterX
  const dy = toCenterY - fromCenterY

  // 确定主要方向
  const horizontalDistance = Math.abs(dx)
  const verticalDistance = Math.abs(dy)
  const isHorizontalPrimary = horizontalDistance > verticalDistance

  // 根据相对位置确定端口
  let fromPort: string, toPort: string

  if (isHorizontalPrimary) {
    // 水平连接为主
    if (dx > 0) {
      // from在左边，to在右边
      fromPort = 'right'
      toPort = 'left'
    } else {
      // from在右边，to在左边
      fromPort = 'left'
      toPort = 'right'
    }
  } else {
    // 垂直连接为主
    if (dy > 0) {
      // from在上边，to在下边
      fromPort = 'bottom'
      toPort = 'top'
    } else {
      // from在下边，to在上边
      fromPort = 'top'
      toPort = 'bottom'
    }
  }

  return { fromPort, toPort }
}

// 获取节点的端口位置
const getPortPosition = (nodeId: string, port: string) => {
  const nodePos = nodePositions.value[nodeId]
  if (!nodePos) return { x: 0, y: 0 }

  const nodeWidth = 280 // 节点宽度
  const nodeHeight = 160 // 节点高度
  const portSize = 12 // 端口大小

  // 根据端口类型计算位置
  switch (port) {
    case 'left':
      return {
        x: nodePos.x,
        y: nodePos.y + nodeHeight / 2
      }
    case 'right':
      return {
        x: nodePos.x + nodeWidth,
        y: nodePos.y + nodeHeight / 2
      }
    case 'top':
      return {
        x: nodePos.x + nodeWidth / 2,
        y: nodePos.y
      }
    case 'bottom':
      return {
        x: nodePos.x + nodeWidth / 2,
        y: nodePos.y + nodeHeight
      }
    default:
      return {
        x: nodePos.x + nodeWidth / 2,
        y: nodePos.y + nodeHeight / 2
      }
  }
}

// 连线路径计算 - 支持多端口的连接
const getConnectionPath = (connection: { from: string; to: string; toInputId?: string }) => {
  const fromNode = nodePositions.value[connection.from]
  const toNode = nodePositions.value[connection.to]

  if (!fromNode || !toNode) {
    return ''
  }

  // 获取实际的节点尺寸
  const getNodeActualDimensions = (nodeId: string) => {
    const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`) as HTMLElement
    if (nodeElement) {
      return {
        width: nodeElement.offsetWidth,
        height: nodeElement.offsetHeight
      }
    }
    return { width: 280, height: 160 }
  }

  const fromDimensions = getNodeActualDimensions(connection.from)
  const toDimensions = getNodeActualDimensions(connection.to)

  // 计算起始点（从输出端口）
  const fromX = fromNode.x + fromDimensions.width / 2
  const fromY = fromNode.y + fromDimensions.height

  // 计算目标点（到输入端口）
  let toX = toNode.x + toDimensions.width / 2
  let toY = toNode.y

  // 如果目标节点有多个输入端口，根据toInputId确定具体位置
  if (connection.toInputId) {
    const toNodeData = nodes.value.find(n => n.id === connection.to)
    if (toNodeData && toNodeData.inputs) {
      const inputIndex = toNodeData.inputs.findIndex(i => i.id === connection.toInputId)
      if (inputIndex !== -1) {
        // 计算特定输入端口的位置（与CSS中的35%和65%对应）
        toX = toNode.x + toDimensions.width * (0.35 + inputIndex * 0.3)
      }
    }
  }

  // 简单优雅的贝塞尔曲线
  const dx = toX - fromX
  const dy = toY - fromY

  // 计算控制点，创建平滑的弧线
  const controlPointOffset = Math.min(Math.abs(dy) * 0.5, 100)
  const midX = (fromX + toX) / 2
  const midY = (fromY + toY) / 2

  // 如果节点水平对齐较多，使用垂直方向的曲线
  if (Math.abs(dx) < 50) {
    return `M ${fromX} ${fromY}
            Q ${fromX + 30} ${midY}, ${midX} ${toY}`
  }

  // 横平竖直的S型直线连接（L型路径）
  // 根据节点相对位置决定路径
  if (Math.abs(toX - fromX) > 50) {
    // 水平距离较大，使用L型路径
    if (toX > fromX) {
      // 目标节点在右边，先向下再向右再向上
      const arrowX = fromX + (toX - fromX) * 0.75 // 箭头在水平段75%位置，避开转角
      return `M ${fromX} ${fromY}
              L ${fromX} ${midY}
              L ${arrowX} ${midY}
              L ${toX} ${midY}
              L ${toX} ${toY}`
    } else {
      // 目标节点在左边，先向下再向左再向上
      const arrowX = toX + (fromX - toX) * 0.75 // 箭头在水平段75%位置，避开转角
      return `M ${fromX} ${fromY}
              L ${fromX} ${midY}
              L ${arrowX} ${midY}
              L ${toX} ${midY}
              L ${toX} ${toY}`
    }
  } else {
    // 垂直对齐较多，使用更简单的路径
    const arrowY = fromY + (toY - fromY) * 0.75 // 箭头在垂直段75%位置，避开转角
    return `M ${fromX} ${fromY}
            L ${midX} ${fromY}
            L ${midX} ${arrowY}
            L ${midX} ${toY}
            L ${toX} ${toY}`
  }
}

// 创建智能路径，避开节点
const createSmartPath = (
  fromX: number,
  fromY: number,
  toX: number,
  toY: number,
  nodeBounds: Array<{ id: string; x: number; y: number; width: number; height: number }>
): string => {
  const margin = 25 // 节点周围的边距

  // 判断点是否在节点内
  const isInsideNode = (x: number, y: number) => {
    return nodeBounds.some(node =>
      x >= node.x - margin &&
      x <= node.x + node.width + margin &&
      y >= node.y - margin &&
      y <= node.y + node.height + margin
    )
  }

  // 判断线段是否与节点相交
  const lineIntersectsNode = (x1: number, y1: number, x2: number, y2: number) => {
    return nodeBounds.some(node => {
      // 扩展节点的边界框
      const expandedLeft = node.x - margin
      const expandedRight = node.x + node.width + margin
      const expandedTop = node.y - margin
      const expandedBottom = node.y + node.height + margin

      // 检查线段是否与扩展的边界框相交
      return !(x2 < expandedLeft || x1 > expandedRight ||
               y2 < expandedTop || y1 > expandedBottom)
    })
  }

  // 如果直线连接不穿过节点，使用直线
  if (!lineIntersectsNode(fromX, fromY, toX, toY)) {
    return `M ${fromX} ${fromY} L ${toX} ${toY}`
  }

  // 计算方向和距离
  const horizontalDistance = Math.abs(toX - fromX)
  const verticalDistance = Math.abs(toY - fromY)
  const movingDown = toY > fromY
  const movingRight = toX > fromX

  // 创建智能的折线路径
  const waypoints: string[] = []
  waypoints.push(`M ${fromX} ${fromY}`)

  // 尝试多个避障策略
  const strategies = [
    // 策略1：先水平后垂直
    () => {
      const midX = fromX + (toX - fromX) * 0.5
      const path = [
        `M ${fromX} ${fromY}`,
        `L ${midX} ${fromY}`,
        `L ${midX} ${toY}`,
        `L ${toX} ${toY}`
      ].join(' ')

      const intersects = lineIntersectsNode(fromX, fromY, midX, fromY) ||
                         lineIntersectsNode(midX, fromY, midX, toY) ||
                         lineIntersectsNode(midX, toY, toX, toY)
      return { path, intersects }
    },

    // 策略2：先垂直后水平
    () => {
      const midY = fromY + (toY - fromY) * 0.5
      const path = [
        `M ${fromX} ${fromY}`,
        `L ${fromX} ${midY}`,
        `L ${toX} ${midY}`,
        `L ${toX} ${toY}`
      ].join(' ')

      const intersects = lineIntersectsNode(fromX, fromY, fromX, midY) ||
                         lineIntersectsNode(fromX, midY, toX, midY) ||
                         lineIntersectsNode(toX, midY, toX, toY)
      return { path, intersects }
    },

    // 策略3：上方绕行
    () => {
      const buffer = margin + 20
      const upperY = Math.min(
        ...nodeBounds.map(n => n.y - buffer)
      )

      const path = [
        `M ${fromX} ${fromY}`,
        `L ${fromX} ${upperY}`,
        `L ${toX} ${upperY}`,
        `L ${toX} ${toY}`
      ].join(' ')

      const intersects = lineIntersectsNode(fromX, fromY, fromX, upperY) ||
                         lineIntersectsNode(fromX, upperY, toX, upperY) ||
                         lineIntersectsNode(toX, upperY, toX, toY)
      return { path, intersects }
    },

    // 策略4：下方绕行
    () => {
      const buffer = margin + 20
      const lowerY = Math.max(
        ...nodeBounds.map(n => n.y + n.height + buffer)
      )

      const path = [
        `M ${fromX} ${fromY}`,
        `L ${fromX} ${lowerY}`,
        `L ${toX} ${lowerY}`,
        `L ${toX} ${toY}`
      ].join(' ')

      const intersects = lineIntersectsNode(fromX, fromY, fromX, lowerY) ||
                         lineIntersectsNode(fromX, lowerY, toX, lowerY) ||
                         lineIntersectsNode(toX, lowerY, toX, toY)
      return { path, intersects }
    }
  ]

  // 尝试每个策略
  for (const strategy of strategies) {
    const result = strategy()
    if (!result.intersects) {
      return result.path
    }
  }

  // 如果所有策略都失败，使用简单的直角连接
  const midX = fromX + (toX - fromX) * 0.5
  return `M ${fromX} ${fromY} L ${midX} ${fromY} L ${midX} ${toY} L ${toX} ${toY}`
}

// 画布控制方法
const startCanvasDrag = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    isCanvasDragging.value = true
    canvasDragStart.x = event.clientX
    canvasDragStart.y = event.clientY
    canvasOffsetStart.x = canvasOffset.x
    canvasOffsetStart.y = canvasOffset.y

    document.addEventListener('mousemove', onCanvasDrag)
    document.addEventListener('mouseup', stopCanvasDrag)

    event.preventDefault()
  }
}

const onCanvasDrag = (event: MouseEvent) => {
  if (!isCanvasDragging.value) return

  const deltaX = event.clientX - canvasDragStart.x
  const deltaY = event.clientY - canvasDragStart.y

  canvasOffset.x = canvasOffsetStart.x + deltaX
  canvasOffset.y = canvasOffsetStart.y + deltaY
}

const stopCanvasDrag = () => {
  isCanvasDragging.value = false
  document.removeEventListener('mousemove', onCanvasDrag)
  document.removeEventListener('mouseup', stopCanvasDrag)
}

const handleWheel = (event: WheelEvent) => {
  event.preventDefault()

  const delta = event.deltaY > 0 ? 0.9 : 1.1
  const newScale = canvasScale.value * delta

  if (newScale >= 0.1 && newScale <= 3) {
    canvasScale.value = newScale
  }
}

// 开始拖拽节点
// 拖拽相关变量
let dragStartPos = { x: 0, y: 0 }
let dragStartTime = 0
let isDraggingActive = false
const DRAG_THRESHOLD = 5
const DRAG_TIME_THRESHOLD = 200  // 按住200ms才算拖拽

const startDrag = (event: MouseEvent, node: Node) => {
  console.log('[mousedown] startDrag 被调用:', node.id)

  // 左键点击才开始处理
  if (event.button !== 0) return

  // 记录初始状态
  dragStartPos = { x: event.clientX, y: event.clientY }
  dragStartTime = Date.now()
  isDraggingActive = false
  draggedNode.value = node.id

  // 获取鼠标相对于画布的位置（考虑缩放和偏移）
  const workflowCanvas = document.querySelector('.workflow-canvas') as HTMLElement
  const workflowRect = workflowCanvas.getBoundingClientRect()

  // 转换为画布坐标
  const canvasX = (event.clientX - workflowRect.left - canvasOffset.x) / canvasScale.value
  const canvasY = (event.clientY - workflowRect.top - canvasOffset.y) / canvasScale.value

  // 确保节点位置存在
  if (!nodePositions.value[node.id]) {
    nodePositions.value[node.id] = reactive({
      x: node.x || 0,
      y: node.y || 0,
      scale: 1,
      isExpanded: false
    })
  }

  const nodePos = nodePositions.value[node.id]
  dragOffset.x = canvasX - nodePos.x
  dragOffset.y = canvasY - nodePos.y

  // 添加全局事件监听器（用于检测拖拽和鼠标释放）
  document.addEventListener('mousemove', onDrag, { passive: false })
  document.addEventListener('mouseup', stopDrag, { passive: false })
}

// 拖拽中
const onDrag = (event: MouseEvent) => {
  if (!draggedNode.value) return

  // 计算按住时间和移动距离
  const elapsedTime = Date.now() - dragStartTime
  const deltaX = Math.abs(event.clientX - dragStartPos.x)
  const deltaY = Math.abs(event.clientY - dragStartPos.y)

  // 只有当按住时间超过阈值且移动距离超过阈值时，才开始拖拽
  if (!isDraggingActive) {
    if (elapsedTime > DRAG_TIME_THRESHOLD && (deltaX > DRAG_THRESHOLD || deltaY > DRAG_THRESHOLD)) {
      isDraggingActive = true
      isDragging.value = true
      // 阻止默认行为和事件冒泡，避免干扰双击
      event.preventDefault()
      event.stopPropagation()
      console.log('[onDrag] 拖拽已激活，时间:', elapsedTime, 'ms')
    } else {
      return
    }
  }

  // 确保节点位置存在
  if (!nodePositions.value[draggedNode.value]) {
    console.warn(`拖拽时发现节点 ${draggedNode.value} 位置不存在，重新初始化`)
    const node = nodes.value.find(n => n.id === draggedNode.value)
    if (node) {
      nodePositions.value[draggedNode.value] = reactive({
        x: node.x || 0,
        y: node.y || 0,
        scale: 1,
        isExpanded: false
      })
    } else {
      return
    }
  }

  const nodePos = nodePositions.value[draggedNode.value]

  // 获取鼠标相对于画布的位置（考虑缩放和偏移）
  const workflowCanvas = document.querySelector('.workflow-canvas') as HTMLElement
  const workflowRect = workflowCanvas.getBoundingClientRect()

  // 转换为画布坐标
  const canvasX = (event.clientX - workflowRect.left - canvasOffset.x) / canvasScale.value
  const canvasY = (event.clientY - workflowRect.top - canvasOffset.y) / canvasScale.value

  // 更新节点位置
  const newX = canvasX - dragOffset.x
  const newY = canvasY - dragOffset.y

  // 使用Vue的响应式方式更新位置
  nodePos.x = newX
  nodePos.y = newY

  // 同时更新节点原始数据中的位置，确保数据一致性
  const node = nodes.value.find(n => n.id === draggedNode.value)
  if (node) {
    node.x = newX
    node.y = newY
  }
}

// 停止拖拽
const stopDrag = (event: MouseEvent) => {
  const wasDragging = isDraggingActive

  isDragging.value = false
  draggedNode.value = null
  isDraggingActive = false

  // 移除全局事件监听器（使用与添加时相同的选项）
  document.removeEventListener('mousemove', onDrag, { passive: false } as any)
  document.removeEventListener('mouseup', stopDrag, { passive: false } as any)

  // 只有真正发生了拖拽才阻止默认行为和保存布局
  if (wasDragging) {
    event.preventDefault()
    event.stopPropagation()

    try {
      const layoutData = {
        nodePositions: nodePositions.value,
        canvasOffset: canvasOffset,
        canvasScale: canvasScale.value,
        timestamp: new Date().toISOString()
      }
      localStorage.setItem('node-workflow-layout', JSON.stringify(layoutData))
      console.log('拖拽结束，布局已自动保存')
    } catch (error) {
      console.error('保存布局失败:', error)
    }
  }
  // 如果不是真正的拖拽（只是点击或快速点击），不阻止事件传播，让双击事件能正常触发
}

// 选择节点
const selectNode = (nodeId: string) => {
  console.log('[click] selectNode 被调用:', nodeId)
  activeNode.value = nodeId
}

// 端口事件处理
const onPortHover = (event: MouseEvent) => {
  const port = event.target as HTMLElement
  port.style.transform = port.style.transform === 'scale(1.5)' ? 'scale(1)' : 'scale(1.5)'
}

const onPortLeave = (event: MouseEvent) => {
  const port = event.target as HTMLElement
  port.style.transform = 'scale(1)'
}

// 切换输入端口状态
const toggleInputPort = (nodeId: string, inputId: string) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node && node.inputs) {
    const input = node.inputs.find(i => i.id === inputId)
    if (input) {
      input.active = !input.active
      console.log(`节点 ${nodeId} 的输入端口 ${inputId} ${input.active ? '已启用' : '已禁用'}`)

      // 更新连接状态
      updateConnectionVisibility()
    }
  }
}

// 更新连接的可见性
const updateConnectionVisibility = () => {
  // 更新所有具有多输入端口的节点的连接状态
  connections.value.forEach(conn => {
    if (conn.toInputId) {
      const targetNode = nodes.value.find(n => n.id === conn.to)
      if (targetNode && targetNode.inputs) {
        const input = targetNode.inputs.find(i => i.id === conn.toInputId)
        if (input) {
          conn.enabled = input.active
        }
      }
    }
  })
}

// 保存工作流（快速保存）
const saveWorkflow = async () => {
  try {
    // 创建包含实际位置的节点数据
    const nodesWithPositions = nodes.value.map(node => ({
      ...node,
      x: nodePositions.value[node.id]?.x || node.x,
      y: nodePositions.value[node.id]?.y || node.y
    }))

    await fileManager.saveWorkflow({
      name: 'MyQuant工作流',
      description: '量化交易工作流配置',
      nodes: nodesWithPositions,
      connections: connections.value,
      canvasOffset: canvasOffset.value,
      canvasScale: canvasScale.value,
      metadata: {
        tags: ['quant', 'trading'],
        category: 'trading'
      }
    })

    // 同时保存布局到本地存储
    const layoutData = {
      nodePositions: nodePositions.value,
      canvasOffset: canvasOffset.value,
      canvasScale: canvasScale.value,
      timestamp: new Date().toISOString()
    }
    localStorage.setItem('node-workflow-layout', JSON.stringify(layoutData))

    showNotification('工作流已保存到本地', 'success')
  } catch (error) {
    console.error('保存工作流失败:', error)
    showNotification('保存失败', 'error')
  }
}

// 触发加载工作流
const triggerLoadWorkflow = () => {
  fileInput.value?.click()
}

// 处理文件加载
const handleFileLoad = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  try {
    const workflow = await fileManager.loadWorkflow(file)

    // 加载工作流数据
    nodes.value = workflow.nodes
    connections.value = workflow.connections
    canvasOffset.x = workflow.canvasOffset.x
    canvasOffset.y = workflow.canvasOffset.y
    canvasScale.value = workflow.canvasScale

    // 更新节点位置
    nodes.value.forEach(node => {
      nodePositions.value[node.id] = {
        x: node.x,
        y: node.y,
        scale: 1,
        isExpanded: false
      }
    })

    showNotification('工作流加载成功', 'success')
  } catch (error) {
    console.error('加载工作流失败:', error)
    showNotification('加载失败: ' + (error as Error).message, 'error')
  }

  // 清空文件输入
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}


// 加载布局
const loadLayout = () => {
  try {
    // 优先加载默认布局
    const defaultLayout = localStorage.getItem('node-workflow-default-layout')
    const savedLayout = localStorage.getItem('node-workflow-layout')
    
    // 使用默认布局（如果存在）或保存的布局
    const layoutToLoad = defaultLayout || savedLayout
    
    if (layoutToLoad) {
      const layoutData = JSON.parse(layoutToLoad)

      // 恢复节点位置
      if (layoutData.nodePositions) {
        nodePositions.value = layoutData.nodePositions
      }

      // 恢复画布偏移和缩放
      if (layoutData.canvasOffset) {
        canvasOffset.value = layoutData.canvasOffset
      }

      if (layoutData.canvasScale !== undefined) {
        canvasScale.value = layoutData.canvasScale
      }

      const layoutType = defaultLayout ? '默认布局' : '保存的布局'
      console.log(`${layoutType}已加载`, layoutData)
      console.log('布局保存时间:', new Date(layoutData.timestamp).toLocaleString())
    }
  } catch (error) {
    console.error('加载布局失败:', error)
  }
}

// 设为默认布局
const setDefaultLayout = () => {
  if (confirm('确定要将当前布局设为默认布局吗？这将覆盖原有的默认布局。')) {
    // 获取当前所有节点的位置
    const currentLayout: Record<string, any> = {}
    nodes.value.forEach(node => {
      const pos = nodePositions.value[node.id]
      if (pos) {
        currentLayout[node.id] = {
          x: pos.x,
          y: pos.y,
          scale: pos.scale || 1,
          isExpanded: pos.isExpanded || false
        }
      }
    })

    // 保存为默认布局到localStorage
    localStorage.setItem('node-workflow-default-layout', JSON.stringify(currentLayout))

    console.log('当前布局已设为默认布局:', currentLayout)
    showNotification('当前布局已设为默认布局', 'success')
  }
}

// 恢复默认布局
const restoreDefaultLayout = () => {
  try {
    const defaultLayout = localStorage.getItem('node-workflow-default-layout')
    
    if (!defaultLayout) {
      showNotification('没有保存的默认布局', 'info')
      return
    }

    const layoutData = JSON.parse(defaultLayout)

    // 恢复节点位置
    if (layoutData) {
      Object.keys(layoutData).forEach(nodeId => {
        if (nodePositions.value[nodeId]) {
          nodePositions.value[nodeId].x = layoutData[nodeId].x
          nodePositions.value[nodeId].y = layoutData[nodeId].y
          nodePositions.value[nodeId].scale = layoutData[nodeId].scale || 1
          nodePositions.value[nodeId].isExpanded = layoutData[nodeId].isExpanded || false
        }
      })
    }

    console.log('已恢复默认布局:', layoutData)
    showNotification('已恢复默认布局', 'success')
  } catch (error) {
    console.error('恢复默认布局失败:', error)
    showNotification('恢复默认布局失败', 'error')
  }
}

// 重置布局
const resetLayout = () => {
  if (confirm('确定要重置布局到默认状态吗？已保存的布局将被清除。')) {
    // 清除保存的布局
    localStorage.removeItem('node-workflow-layout')
    localStorage.removeItem('node-workflow-default-layout')

    // 重置节点位置
    nodePositions.value = {}

    // 重置画布
    canvasOffset.value = { x: 0, y: 0 }
    canvasScale.value = 1

    // 重新初始化节点位置
    initializeNodePositions()

    console.log('布局已重置')
    showNotification('布局已重置', 'info')
  }
}

// 显示通知
const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
  // 创建通知元素
  const notification = document.createElement('div')
  notification.className = `notification notification-${type}`
  notification.textContent = message
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 9999;
    transition: all 0.3s ease;
    transform: translateX(100%);
  `

  // 设置背景色
  switch (type) {
    case 'success':
      notification.style.background = 'linear-gradient(135deg, #22c55e, #16a34a)'
      break
    case 'error':
      notification.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)'
      break
    default:
      notification.style.background = 'linear-gradient(135deg, #3b82f6, #2563eb)'
  }

  // 添加到页面
  document.body.appendChild(notification)

  // 显示动画
  setTimeout(() => {
    notification.style.transform = 'translateX(0)'
  }, 100)

  // 自动隐藏
  setTimeout(() => {
    notification.style.transform = 'translateX(100%)'
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification)
      }
    }, 300)
  }, 3000)
}
// 🔧 辅助函数：为数据清洗节点构建metadata
const getDataCleaningNodeMetadata = (node: any) => {
  console.log('[NodeWorkflow] getDataCleaningNodeMetadata 调用, nodeId:', node.id)
  console.log('[NodeWorkflow] node.data:', node.data)
  console.log('[NodeWorkflow] node.params:', node.params)

  // 优先使用 node.data.metadata（如果存在）
  if (node.data?.metadata) {
    console.log('[NodeWorkflow] 使用 node.data.metadata:', node.data.metadata)
    return node.data.metadata
  }

  // 🔧 如果 metadata 不存在，从 node.data.content 和 node.params 中构建
  const metadata: any = {}

  // 🔧 对于数据清洗节点，构建 data_overview 结构
  if (node.id === 'data-cleaning') {
    metadata.data_overview = {}
  }

  // 从 node.data.content 获取数据
  if (node.data?.content) {
    const content = node.data.content
    console.log('[NodeWorkflow] node.data.content 存在, keys:', Object.keys(content))

    // 股票数量（数据库标的）
    if (content.stockCount) {
      metadata.stockCount = content.stockCount
      // 🔧 同时设置到 data_overview 中
      if (metadata.data_overview) {
        metadata.data_overview.stock_count = content.stockCount
      }
      console.log('[NodeWorkflow] 从 content 设置 stockCount:', content.stockCount)
    }

    // 已选标的数量
    if (content.selectedStocks !== undefined) {
      metadata.selectedStockCount = content.selectedStocks
    } else if (content.stockCount) {
      metadata.selectedStockCount = content.stockCount
    }

    // 时间范围
    if (content.dateRange && content.dateRange !== '未设置' && content.dateRange !== '未配置') {
      metadata.dateRange = content.dateRange
      // 🔧 同时设置到 data_overview 中
      if (metadata.data_overview) {
        metadata.data_overview.data_time_range = content.dateRange
      }
      console.log('[NodeWorkflow] 从 content 设置 dateRange:', content.dateRange)
    }

    // 质量评分
    if (content.qualityScore) {
      metadata.overall_quality_score = content.qualityScore
      metadata.data_quality_score = content.qualityScore
      metadata.qualityScore = content.qualityScore
    }

    // 数据统计
    if (content.originalRows) {
      metadata.totalRecords = content.originalRows
    }
    if (content.cleanedRows) {
      metadata.totalDataPoints = content.cleanedRows
    }

    // 缺失值、重复值、异常值统计
    if (content.missingCount !== undefined) {
      metadata.missingCount = content.missingCount
    }
    if (content.duplicateCount !== undefined) {
      metadata.duplicateCount = content.duplicateCount
    }
    if (content.outlierCount !== undefined) {
      metadata.outlierCount = content.outlierCount
    }

    // 数据新鲜度（最后更新时间）
    if (content.storageTime) {
      metadata.lastUpdated = content.storageTime
      if (!metadata.storage_info) {
        metadata.storage_info = {}
      }
      if (!metadata.storage_info.data_storage) {
        metadata.storage_info.data_storage = {}
      }
      metadata.storage_info.data_storage.last_updated = content.storageTime
    }

    // 转换状态
    if (content.conversionStatus) {
      metadata.conversionStatus = content.conversionStatus
    }
  } else {
    console.log('[NodeWorkflow] node.data.content 不存在或为空')
  }

  // 从 node.params 获取频率信息
  if (node.params?.frequencies && Array.isArray(node.params.frequencies)) {
    metadata.frequencies = node.params.frequencies
  } else if (node.params?.frequency) {
    metadata.frequencies = [node.params.frequency]
  }

  // 从 node.params 获取日期范围
  if (node.params?.startDate && node.params?.endDate) {
    if (!metadata.dateRange || metadata.dateRange === '未设置') {
      metadata.dateRange = `${node.params.startDate} ~ ${node.params.endDate}`
      // 🔧 同时设置到 data_overview 中
      if (metadata.data_overview) {
        metadata.data_overview.data_time_range = metadata.dateRange
      }
      console.log('[NodeWorkflow] 从 params 设置 dateRange:', metadata.dateRange)
    }
  }

  // 🔧 如果没有 stockCount，尝试从上游节点获取
  if (!metadata.stockCount) {
    console.log('[NodeWorkflow] metadata.stockCount 不存在，尝试从上游节点获取')
    console.log('[NodeWorkflow] metadata.stockCount 值:', metadata.stockCount)
    console.log('[NodeWorkflow] metadata:', metadata)
    // 查找上游的股票选择节点
    const upstreamConnections = connections.value.filter((e: any) => e.to === node.id)
    console.log('[NodeWorkflow] 上游连接数量:', upstreamConnections.length)

    for (const connection of upstreamConnections) {
      const upstreamNode = nodes.value.find((n: any) => n.id === connection.from)
      if (upstreamNode) {
        console.log('[NodeWorkflow] 检查上游节点:', upstreamNode.id)

        // 从股票选择节点获取
        if (upstreamNode.id === 'stock-selection') {
          const symbols = upstreamNode.params?.symbols || []
          const stockCode = upstreamNode.params?.stockCode || ''
          const count = symbols.length > 0 ? symbols.length : (stockCode ? stockCode.split(/[,，]/).filter((c: string) => c).length : 0)
          if (count > 0) {
            metadata.stockCount = count
            // 🔧 同时设置到 data_overview 中
            if (metadata.data_overview) {
              metadata.data_overview.stock_count = count
            }
            console.log('[NodeWorkflow] 从 stock-selection 获取 stockCount:', count)
          }
        }

        // 从指数选择节点获取
        if (upstreamNode.id === 'index-selection' && upstreamNode.params?.indexCode) {
          const indexCodes = upstreamNode.params.indexCode.split(/[,，]/).filter((c: string) => c)
          if (indexCodes.length > 0) {
            metadata.stockCount = (metadata.stockCount || 0) + indexCodes.length
            // 🔧 同时设置到 data_overview 中
            if (metadata.data_overview) {
              metadata.data_overview.stock_count = metadata.stockCount
            }
            console.log('[NodeWorkflow] 从 index-selection 获取 stockCount:', indexCodes.length)
          }
        }

        // 从上游节点获取时间范围
        if (!metadata.dateRange || metadata.dateRange === '未设置') {
          if (upstreamNode.params?.startDate && upstreamNode.params?.endDate) {
            metadata.dateRange = `${upstreamNode.params.startDate} ~ ${upstreamNode.params.endDate}`
            // 🔧 同时设置到 data_overview 中
            if (metadata.data_overview) {
              metadata.data_overview.data_time_range = metadata.dateRange
            }
            console.log('[NodeWorkflow] 从上游节点设置 dateRange:', metadata.dateRange)
          }
        }
      }
    }
  }

  // 🔧 如果没有任何数据，至少提供一个默认的 frequencies
  if (!metadata.frequencies || metadata.frequencies.length === 0) {
    metadata.frequencies = ['daily']
  }

  console.log('[NodeWorkflow] 构建的 data-cleaning metadata:', metadata)
  return metadata
}


const toggleLayoutMenu = () => {
  showLayoutMenu.value = !showLayoutMenu.value

  // 点击其他地方关闭菜单
  if (showLayoutMenu.value) {
    nextTick(() => {
      document.addEventListener('click', closeLayoutMenu)
    })
  }
}

// 关闭布局菜单
const closeLayoutMenu = () => {
  showLayoutMenu.value = false
  document.removeEventListener('click', closeLayoutMenu)
}

// 处理文件导入
const handleFileImport = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  try {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const layoutData = JSON.parse(e.target?.result as string)

        // 验证布局数据
        if (!layoutData.nodePositions || !layoutData.canvasOffset || layoutData.canvasScale === undefined) {
          throw new Error('无效的布局文件格式')
        }

        // 应用布局
        if (layoutData.nodePositions) {
          nodePositions.value = layoutData.nodePositions
        }
        if (layoutData.canvasOffset) {
          canvasOffset.value = layoutData.canvasOffset
        }
        if (layoutData.canvasScale !== undefined) {
          canvasScale.value = layoutData.canvasScale
        }

        // 保存到 localStorage
        localStorage.setItem('node-workflow-layout', JSON.stringify(layoutData))

        console.log('布局已导入', layoutData)
        showNotification('布局导入成功', 'success')
      } catch (error) {
        console.error('导入失败:', error)
        showNotification('导入失败: ' + (error as Error).message, 'error')
      }
    }
    reader.readAsText(file)
  } catch (error) {
    console.error('读取文件失败:', error)
    showNotification('读取文件失败', 'error')
  }

  // 重置文件输入
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 打开节点详情
const openNodeDetail = (node: Node) => {
  console.log('[双击] openNodeDetail 被调用:', node.id, node.title)
  console.log('[双击] 当前 showNodeDetail:', showNodeDetail.value)
  selectedNode.value = node
  showNodeDetail.value = true
  console.log('[双击] showNodeDetail 已设置为:', showNodeDetail.value)
  // 使用 nextTick 确保 DOM 更新
  nextTick(() => {
    console.log('[双击] nextTick 后 showNodeDetail:', showNodeDetail.value)
  })
}

// 更新节点配置
const updateNodeConfig = (nodeId: string, config: any) => {
  const nodeIndex = nodes.value.findIndex(n => n.id === nodeId)
  if (nodeIndex !== -1) {
    const node = nodes.value[nodeIndex]

    // 更新节点信息
    if (config.title) node.title = config.title
    if (config.description) node.description = config.description
    if (config.params) {
      // 🔧 确保 node.params 对象存在
      if (!node.params) {
        node.params = {}
      }

      // 🔧 确保 frequencies 字段存在（用于旧数据兼容）
      if (!node.params.frequencies) {
        node.params.frequencies = node.params.frequency ? [node.params.frequency] : ['daily']
      }

      // 🔧 直接合并 params
      Object.assign(node.params, config.params)

      // 🔧 新增：同时更新 node.data.metadata，让 MiniDataReport 能够读取到选中的标的数量和频率
      if (!node.data) {
        node.data = {} as any
      }
      if (!node.data.metadata) {
        node.data.metadata = {} as any
      }

      // 将 params 中的 selectedStockCount 复制到 metadata 中
      if (config.params.selectedStockCount !== undefined) {
        node.data.metadata.selectedStockCount = config.params.selectedStockCount
      }
      if (config.params.selectedStockCodes !== undefined) {
        node.data.metadata.selectedStockCodes = config.params.selectedStockCodes
      }
      // 🔧 将 frequencies 复制到 metadata 中
      if (config.params.frequencies !== undefined) {
        node.data.metadata.frequencies = config.params.frequencies
      }
    }

    // 🔧 新增：更新 inputs 状态（用于连线激活/停用）
    if (config.inputs) {
      console.log(`[NodeWorkflow] 更新节点 ${nodeId} 的 inputs 状态:`, config.inputs)
      node.inputs = config.inputs
    }

    // 🔧 强制组件重新渲染：递增 updateKey 并重新赋值整个 nodes 数组
    node.updateKey = (node.updateKey || 0) + 1

    // 🔧 关键：重新赋值整个 nodes 数组来触发响应式更新
    nodes.value = [...nodes.value]

    // 🔧 更新连线可见性（如果节点的 inputs 状态发生了变化）
    updateConnectionVisibility()
  }
}

const goBack = () => {
  router.push('/research')
}

// 数据格式化函数
const formatStatLabel = (key: string): string => {
  const labelMap: Record<string, string> = {
    totalStocks: '股票总数',
    dataPoints: '数据点',
    lastUpdate: '更新时间',
    sources: '数据源',
    duplicateRecords: '重复记录',
    missingValues: '缺失值',
    outliers: '异常值',
    cleanRate: '清洗率',
    epochs: '训练轮次',
    accuracy: '准确率',
    loss: '损失值',
    bestScore: '最佳得分'
  }
  return labelMap[key] || key
}

const formatStatValue = (value: any): string => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return String(value)
}

// 判断数值的颜色（中国股市配色）
const getValueColor = (value: string | number): string => {
  const str = String(value)

  // 涨跌颜色判断
  if (str.includes('+') || str.startsWith('涨') ||
      (typeof value === 'number' && value > 0) ||
      str.includes('优秀') || str.includes('增长')) {
    return '#ef4444' // 红色 - 上涨
  } else if (str.includes('-') || str.startsWith('跌') ||
             (typeof value === 'number' && value < 0) ||
             str.includes('不良') || str.includes('下降')) {
    return '#22c55e' // 绿色 - 下跌
  } else if (str.includes('平') || (typeof value === 'number' && value === 0)) {
    return '#6b7280' // 灰色 - 平盘
  } else {
    return '#3b82f6' // 默认紫色
  }
}

// 格式化表格单元格值
const formatTableValue = (value: any): { text: string; color: string } => {
  const str = String(value)
  let color = '#ffffff' // 默认白色

  // 涨跌幅颜色
  if (str.includes('+')) {
    color = '#ef4444' // 红色
  } else if (str.includes('-')) {
    color = '#22c55e' // 绿色
  }

  // 状态颜色
  if (str === '优秀') color = '#ef4444'
  if (str === '良好') color = '#f59e0b'
  if (str === '一般') color = '#6b7280'
  if (str === '差') color = '#22c55e'

  return { text: str, color }
}

// 状态相关辅助函数
const getStatusClass = (status: string): string => {
  if (!status) return 'status-pending'
  const str = String(status)
  if (str.includes('待获取') || str.includes('未配置')) return 'status-pending'
  if (str.includes('已获取') || str.includes('全部成功') || str.includes('已配置')) return 'status-success'
  if (str.includes('部分成功') || str.includes('获取失败')) return 'status-warning'
  return 'status-default'
}

const getStatusLabel = (status: string): string => {
  if (!status) return '待配置'
  const str = String(status)
  if (str.includes('待获取')) return '待获取'
  if (str.includes('未配置')) return '未配置'
  if (str.includes('已配置')) return '已配置'
  if (str.includes('全部成功')) return '已完成'
  if (str.includes('部分成功')) return '部分完成'
  if (str.includes('已获取')) return '已获取'
  return str
}

// 粒子系统引用
const particleCanvas = ref<HTMLCanvasElement | null>(null)
const animationFrameId = ref<number | null>(null)

// 初始化粒子系统
const initParticleSystem = () => {
  // 延迟执行以确保DOM已完全渲染
  setTimeout(() => {
    const particleSystemEl = document.querySelector('.particle-system')
    if (!particleSystemEl) {
      console.warn('Particle system element not found')
      return
    }

    // 清理可能存在的旧canvas
    const existingCanvas = particleSystemEl.querySelector('canvas')
    if (existingCanvas) {
      existingCanvas.remove()
    }

    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    if (!ctx) {
      console.warn('Could not get canvas context')
      return
    }

    const updateCanvasSize = () => {
      const rect = particleSystemEl.getBoundingClientRect()
      canvas.width = rect.width || window.innerWidth
      canvas.height = rect.height || window.innerHeight
    }

    updateCanvasSize()
    canvas.style.position = 'absolute'
    canvas.style.top = '0'
    canvas.style.left = '0'
    canvas.style.pointerEvents = 'none'
    canvas.style.width = '100%'
    canvas.style.height = '100%'

    particleSystemEl.appendChild(canvas)
    particleCanvas.value = canvas

    // 简单的粒子动画
    const particles: any[] = []
    for (let i = 0; i < 25; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        size: Math.random() * 2 + 1,
        opacity: Math.random() * 0.5 + 0.2
      })
    }

    const animate = () => {
      if (!ctx || !canvas) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      particles.forEach(particle => {
        particle.x += particle.vx
        particle.y += particle.vy

        if (particle.x < 0 || particle.x > canvas.width) particle.vx = -particle.vx
        if (particle.y < 0 || particle.y > canvas.height) particle.vy = -particle.vy

        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(59, 130, 246, ${particle.opacity})`
        ctx.fill()
      })

      animationFrameId.value = requestAnimationFrame(animate)
    }

    animate()

    // 监听窗口大小变化
    const handleResize = () => {
      updateCanvasSize()
    }

    window.addEventListener('resize', handleResize)

    // 更新清理函数
    cleanup = () => {
      window.removeEventListener('resize', handleResize)
      if (animationFrameId.value) {
        cancelAnimationFrame(animationFrameId.value)
      }
      if (canvas && canvas.parentNode) {
        canvas.parentNode.removeChild(canvas)
      }
    }
  }, 100) // 延迟100ms执行

  // 返回初始清理函数
  return () => {
    if (cleanup) cleanup()
  }
}

// 清理函数引用
let cleanup: (() => void) | null = null

// 生命周期
onMounted(async () => {
  // 确保DOM完全渲染后再初始化
  await nextTick()

  try {
    // 首先初始化节点位置，确保基础结构存在
    initializeNodePositions()
    
    // 等待下一个tick确保位置已设置
    await nextTick()
    
    // 然后尝试加载保存的布局（会覆盖默认位置）
    loadLayout()
    
    // 再次等待确保布局加载完成
    await nextTick()
    
    // 初始化连接可见性
    updateConnectionVisibility()
    
    // 最后初始化粒子系统
    cleanup = initParticleSystem()
  } catch (error) {
    console.error('初始化过程中发生错误:', error)
    // 即使出错也要确保基本功能可用
    if (Object.keys(nodePositions.value).length === 0) {
      initializeNodePositions()
    }
    updateConnectionVisibility()
    cleanup = initParticleSystem()
  }
})

// 初始化节点位置，避免重叠
const initializeNodePositions = () => {
  console.log('开始初始化节点位置，节点数量:', nodes.value.length)

  // 确保nodePositions是响应式的
  if (!nodePositions.value) {
    nodePositions.value = reactive({})
  }

  nodes.value.forEach((node, index) => {
    // 优先使用当前节点位置，如果没有则使用默认位置
    const currentPos = nodePositions.value[node.id]
    const defaultPos = DEFAULT_NODE_POSITIONS[node.id] || { x: 100, y: 100 }
    
    // 如果节点已经有位置，保持当前位置；否则使用默认位置
    const finalPos = currentPos || defaultPos

    // 使用响应式方式设置节点位置
    if (!nodePositions.value[node.id]) {
      nodePositions.value[node.id] = reactive({
        x: finalPos.x,
        y: finalPos.y,
        scale: finalPos.scale || 1,
        isExpanded: finalPos.isExpanded || false
      })
    } else {
      // 更新现有位置
      nodePositions.value[node.id].x = finalPos.x
      nodePositions.value[node.id].y = finalPos.y
      nodePositions.value[node.id].scale = finalPos.scale || 1
      nodePositions.value[node.id].isExpanded = finalPos.isExpanded || false
    }

    console.log(`节点 ${node.id} 位置设置为:`, { x: finalPos.x, y: finalPos.y })
  })

  // 调整画布初始偏移，确保节点在可视区域内
  if (Object.keys(nodePositions.value).length === 0) {
    canvasOffset.x = 0
    canvasOffset.y = 0
  }

  console.log('节点位置初始化完成:', nodePositions.value)
}

onUnmounted(() => {
  // 清理布局菜单事件监听器
  document.removeEventListener('click', closeLayoutMenu)

  // 清理粒子系统
  if (cleanup) {
    cleanup()
  }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables.scss' as *;

.node-workflow {
  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family-primary);
  overflow-x: hidden;
}

/* 沉浸式背景 */
.immersive-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

.particle-system {
  position: absolute;
  width: 100%;
  height: 100%;
}

.data-stream-overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg,
    transparent 30%,
    rgba(59, 130, 246, 0.03) 50%,
    transparent 70%);
  animation: dataFlow 8s linear infinite;
}

.grid-pattern {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 100;
}

.workflow-header h1 {
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn-back,
.btn-save,
.btn-load,
.btn-reset {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;

  :deep(.fa-save),
  :deep(.fa-folder-open),
  :deep(.fa-undo) {
    font-size: 14px;
  }
}

.btn-back {
  background: rgba(255, 255, 255, 0.1);
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.btn-save {
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.4);
}

.btn-save:hover {
  background: rgba(34, 197, 94, 0.3);
  border-color: rgba(34, 197, 94, 0.6);
  transform: translateY(-1px);
}

.btn-load {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.4);
}

.btn-load:hover {
  background: rgba(59, 130, 246, 0.3);
  border-color: rgba(59, 130, 246, 0.6);
  transform: translateY(-1px);
}


.btn-reset {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
}

.btn-reset:hover {
  background: rgba(239, 68, 68, 0.3);
  border-color: rgba(239, 68, 68, 0.6);
  transform: translateY(-1px);
}

.btn-set-default,
.btn-restore-default {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.4);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.btn-set-default:hover,
.btn-restore-default:hover {
  background: rgba(139, 92, 246, 0.3);
  border-color: rgba(139, 92, 246, 0.6);
  transform: translateY(-1px);
}

.btn-set-default :deep(.fa-thumbtack),
.btn-restore-default :deep(.fa-rotate-left) {
  font-size: 14px;
}

.btn-set-default span {
  font-size: 12px;
  font-weight: 500;
}

.main-content {
  height: calc(100vh - 80px);
  position: relative;
  z-index: 5;
}

.workflow-canvas {
  height: calc(100vh - 80px);
  width: 100%;
  position: relative;
  overflow: visible;
  background: transparent;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100vw;
  height: calc(100vh - 80px);
  pointer-events: none;
  z-index: 3;
  overflow: visible;
}

.canvas-container {
  position: absolute;
  width: 3000px;
  height: 2000px;
  background: transparent;
  cursor: grab;
  transform-origin: 0 0;
  left: 0;
  top: 0;
  z-index: 2;
}

.canvas-container:active {
  cursor: grabbing;
}


.workflow-node {
  position: absolute;
  min-width: 200px;
  width: auto;
  padding: 20px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  cursor: grab;
  user-select: none;
  z-index: 1;
  transition: all 0.3s ease;
}

/* 股票选择节点和指数选择节点：根据数据状态设置宽度 */
.workflow-node[id="stock-selection"],
.workflow-node[id="index-selection"],
.workflow-node[data-node-id="stock-selection"],
.workflow-node[data-node-id="index-selection"] {
  min-width: 400px;
  max-width: none;
  width: 400px !important;
  padding: 10px;
}

/* 其他节点保持较窄的宽度 */
.workflow-node:not([id="stock-selection"]):not([id="index-selection"]):not([data-node-id="stock-selection"]):not([data-node-id="index-selection"]) {
  max-width: 320px;
}

.workflow-node:not(.dragging):hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(139, 92, 246, 0.3);
}

.workflow-node.active {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 0 30px rgba(139, 92, 246, 0.2);
}

.workflow-node.dragging {
  cursor: grabbing;
  z-index: 1000;
  opacity: 0.9;
  transform: scale(1.02);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.node-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.node-title {
  font-size: 1.1rem;
  font-weight: 600;
  flex: 1;
  min-width: 0;
}

.node-description {
  font-size: 0.9rem;
  opacity: 0.8;
  line-height: 1.4;
  margin-bottom: 12px;
}

/* 数据内容样式 */
.node-content {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 12px;
  margin-top: 8px;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px 10px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(139, 92, 246, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.loading-progress {
  width: 100%;
  margin-top: 4px;
}

.progress-bar-bg {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #6366f1);
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* 统计数据 */
.stats-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
}

.stat-value {
  font-weight: 500;
}

/* 数据清洗节点小图表 */
.data-cleaning-mini-charts {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px;
}

.mini-quality-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quality-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: conic-gradient(#10b981 0deg, #10b981 calc(var(--score) * 3.6deg), rgba(255,255,255,0.1) calc(var(--score) * 3.6deg));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.quality-circle::before {
  content: '';
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #1a1a2e;
  position: absolute;
}

.quality-score {
  font-size: 8px;
  font-weight: bold;
  color: #10b981;
  z-index: 1;
}

.quality-label {
  font-size: 10px;
  color: rgba(255,255,255,0.7);
}

.mini-progress-bars {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.progress-label {
  font-size: 9px;
  color: rgba(255,255,255,0.6);
  min-width: 28px;
}

.progress-bar {
  flex: 1;
  height: 3px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-fill.completeness {
  background: #3b82f6;
}

.progress-fill.accuracy {
  background: #10b981;
}

.progress-fill.consistency {
  background: #f59e0b;
}

.mini-issue-indicators {
  display: flex;
  gap: 8px;
  justify-content: space-around;
}

.issue-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.issue-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.issue-dot.missing {
  background: #f59e0b;
}

.issue-dot.duplicates {
  background: #ef4444;
}

.issue-dot.outliers {
  background: #3b82f6;
}

.issue-count {
  font-size: 9px;
  color: rgba(255,255,255,0.8);
  font-weight: 500;
}

/* 股票和指数选择节点小图表 */
.stock-selection-mini-charts,
.index-selection-mini-charts {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 6px 8px;
}

/* 数量大显示 */
.stock-count-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  padding: 8px 0;
}

.count-number {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1;
}

.count-unit {
  font-size: 12px;
  color: rgba(255,255,255,0.6);
  font-weight: 500;
  margin-left: 2px;
}

/* 状态标签行 */
.status-tags-row {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.status-tag {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-tag.tag-pending {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-tag.tag-success {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-tag.tag-warning {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.status-tag.tag-default {
  background: rgba(107, 114, 128, 0.15);
  color: #6b7280;
  border: 1px solid rgba(107, 114, 128, 0.3);
}

.config-tag {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 500;
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

/* 小数据报告卡片样式 */
.mini-data-report-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.mini-data-report-cards .mini-report-card:nth-child(n+4) {
  grid-column: span 1.5;
}

.mini-report-card {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  transition: all 0.2s;
}

.mini-report-card.highlight {
}

.mini-report-card.success {
}

.mini-report-card.warning {
}

.mini-report-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  color: #3b82f6;
}

.mini-report-icon.primary-gradient {
  color: #3b82f6;
}

.mini-report-icon.success-gradient {
  color: #22c55e;
}

.mini-report-icon.warning-gradient {
  color: #f59e0b;
}

.mini-report-icon.info-gradient {
  color: #3b82f6;
}

.mini-report-icon.purple-gradient {
  color: #a855f7;
}

.mini-report-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.mini-report-label {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-report-value {
  font-size: 13px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-report-value-small {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 底部信息行 */
.stock-info-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding-top: 4px;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.info-item {
  font-size: 9px;
  color: rgba(255,255,255,0.5);
  font-weight: 500;
}

/* 表格下方的小组件（紧凑版） */
.stock-selection-mini-charts-after-table,
.index-selection-mini-charts-after-table {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px 0 0 0;
  margin-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.stock-count-display-small {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2px;
}

.count-number-small {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1;
}

.count-unit-small {
  font-size: 10px;
  color: rgba(255,255,255,0.6);
  font-weight: 500;
}

/* 数据汇总行 */
.data-summary-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 2px 0;
}

.summary-item {
  font-size: 11px;
  color: rgba(255,255,255,0.9);
  font-weight: 600;
}

/* 日期范围行 */
.date-range-row {
  display: flex;
  justify-content: center;
  padding: 2px 0;
}

.date-range {
  font-size: 10px;
  color: rgba(255,255,255,0.7);
  font-weight: 500;
}

/* 状态标签行 */
.status-tags-row {
  display: flex;
  justify-content: center;
  gap: 6px;
  padding: 2px 0;
}

/* 表格数据 */
.table-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: visible;
  width: 100%;
  padding: 0 12px;
}

.table-row {
  display: grid;
  grid-template-columns: 0.9fr 1fr 0.8fr 0.8fr 1.1fr;
  gap: 0;
  font-size: 0.8rem;
  padding: 4px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  width: 100%;
  box-sizing: border-box;
}

.table-header {
  display: grid;
  grid-template-columns: 0.9fr 1fr 0.8fr 0.8fr 1.1fr;
  gap: 0;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 4px 0;
  margin-bottom: 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  width: 100%;
  box-sizing: border-box;
}

.header-cell {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
}

.table-cell {
  color: rgba(255, 255, 255, 0.9);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 1px;
}

/* 股票代码列 */
.table-row .table-cell:first-child {
  text-align: left;
}

/* 股票名称列 */
.table-row .table-cell:nth-child(2) {
  text-align: left;
}

/* 收盘价列 */
.table-row .table-cell:nth-child(3) {
  text-align: right;
}

/* 涨跌幅列 */
.table-row .table-cell:nth-child(4) {
  text-align: right;
}

/* 成交量列 */
.table-row .table-cell:nth-child(5) {
  text-align: right;
}

/* 文本数据 */
.text-container {
  font-size: 0.85rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
  padding: 8px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 8px;
  border-left: 3px solid #3b82f6;
}

/* 列表数据 */
.list-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.list-item {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.9);
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  border-left: 2px solid rgba(139, 92, 246, 0.5);
}

/* 图表数据 */
.chart-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chart-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.chart-patterns {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.pattern-tag {
  font-size: 0.75rem;
  padding: 2px 6px;
  background: rgba(139, 92, 246, 0.2);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 12px;
  color: #a78bfa;
}

.chart-stats {
  display: flex;
  justify-content: space-between;
}

.chart-stat {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

/* 节点端口样式 */
.node-port {
  position: absolute;
  width: 12px;
  height: 12px;
  background: #3b82f6;
  border: 2px solid rgba(26, 26, 46, 0.9);
  border-radius: 50%;
  z-index: 10;
  transition: all 0.2s ease;
  opacity: 0.3;
}

.node-port:hover {
  transform: scale(1.5);
  background: #a78bfa;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.6);
  opacity: 1;
}

.node-input-port {
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
}

.node-input-port.multi-port {
  cursor: pointer;
  position: absolute;
  top: -6px;
  transform: translateX(-50%);

  &:nth-child(1) {
    left: 35%;
  }

  &:nth-child(2) {
    left: 65%;
  }

  &.port-active {
    background: #3b82f6;
    border-color: rgba(139, 92, 246, 0.9);
    opacity: 1;
  }

  &.port-inactive {
    background: #666;
    border-color: rgba(102, 102, 102, 0.6);
    opacity: 0.4;
  }
}

.node-output-port {
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
}

.workflow-node.active .node-port {
  background: #3b82f6;
  border-color: rgba(59, 130, 246, 0.8);
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);
}

// 动画
@keyframes dataFlow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

// 节点操作区域
.node-actions {
  margin-top: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: center;
}

.btn-fetch {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.1));
  backdrop-filter: blur(10px);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
  font-weight: 500;
  width: 100%;
  justify-content: center;

  &:hover:not(:disabled) {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(139, 92, 246, 0.2));
    border-color: rgba(139, 92, 246, 0.5);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
    background: rgba(139, 92, 246, 0.1);
  }

  :deep(.fa-sync-alt),
  :deep(.fa-play) {
    font-size: 11px;
  }

  :deep(.fa-spin) {
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>