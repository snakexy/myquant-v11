<template>
  <div class="tdx-sector-map">
    <!-- 顶部标签切换 -->
    <div class="tabs-header">
      <div
        class="tab-item"
        :class="{ active: activeTab === 'all' }"
        @click="switchTab('all')"
      >
        全部
      </div>
      <div
        class="tab-item"
        :class="{ active: activeTab === '881' }"
        @click="switchTab('881')"
      >
        行业
      </div>
      <div
        class="tab-item"
        :class="{ active: activeTab === '880' }"
        @click="switchTab('880')"
      >
        概念
      </div>
      <div class="tab-info">
        共 {{ filteredSectors.length }} 个板块
        <span class="up-count">↑{{ upCount }}</span>
        <span class="down-count">↓{{ downCount }}</span>
        <span class="flat-count">-{{ flatCount }}</span>
        <span class="avg-change" :class="avgChange >= 0 ? 'positive' : 'negative'">
          平均: {{ avgChange >= 0 ? '+' : '' }}{{ avgChange.toFixed(2) }}%
        </span>
      </div>
    </div>

    <!-- 板块地图网格 -->
    <div class="map-container">
      <div v-if="loading" class="loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在加载板块数据...</span>
      </div>
      <div v-else-if="error" class="error">
        <el-icon><Warning /></el-icon>
        <span>{{ error }}</span>
      </div>
      <div v-else class="sector-grid">
        <!-- 扁平显示所有板块 -->
        <div
          v-for="sector in filteredSectors"
          :key="sector.code"
          class="sector-cell"
          :style="{ backgroundColor: getChangeColor(sector.changePercent) }"
          @click="showSectorDetail(sector)"
        >
          <div class="sector-name">{{ sector.name }}</div>
          <div class="sector-change">
            {{ sector.changePercent >= 0 ? '+' : '' }}{{ sector.changePercent.toFixed(2) }}%
          </div>
          <div class="sector-stocks">{{ sector.stocksCount }}只</div>
        </div>
      </div>
    </div>

    <!-- 板块详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="`${selectedSector?.code} ${selectedSector?.name}`"
      width="500px"
    >
      <div v-if="selectedSector" class="sector-detail">
        <div class="detail-row">
          <span class="detail-label">板块代码:</span>
          <span class="detail-value">{{ selectedSector.code }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">板块名称:</span>
          <span class="detail-value">{{ selectedSector.name }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">涨跌幅:</span>
          <span class="detail-value" :class="selectedSector.changePercent >= 0 ? 'positive' : 'negative'">
            {{ selectedSector.changePercent >= 0 ? '+' : '' }}{{ selectedSector.changePercent.toFixed(2) }}%
          </span>
        </div>
        <div class="detail-row">
          <span class="detail-label">成交额:</span>
          <span class="detail-value">{{ (selectedSector.amount / 100000000).toFixed(2) }}亿</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">成分股数:</span>
          <span class="detail-value">{{ selectedSector.stocksCount }}只</span>
        </div>
        <div class="detail-row" v-if="selectedSector.topStocks && selectedSector.topStocks.length > 0">
          <span class="detail-label">龙头股:</span>
          <div class="stocks-list">
            <el-tag v-for="(stock, index) in selectedSector.topStocks.slice(0, 10)" :key="index" size="small" style="margin: 2px;">
              {{ stock }}
            </el-tag>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Warning } from '@element-plus/icons-vue'

// 数据接口
interface SectorData {
  code: string
  name: string
  changePercent: number
  amount: number
  stocksCount: number
  topStocks: string[]
  hasQuote?: boolean
}

interface ApiResponse {
  success: boolean
  data: {
    viewMode?: string
    sectors: SectorData[]
    summary?: {
      total: number
    }
  }
}

// 响应式数据
const activeTab = ref('all')
const loading = ref(false)
const error = ref('')
const sectors = ref<SectorData[]>([])
const detailDialogVisible = ref(false)
const selectedSector = ref<SectorData | null>(null)

// 过滤后的板块（扁平视图）
const filteredSectors = computed(() => {
  let result = sectors.value

  // 按标签页筛选
  if (activeTab.value === '881') {
    result = result.filter(s => s.code.startsWith('881'))
  } else if (activeTab.value === '880') {
    result = result.filter(s => s.code.startsWith('880'))
    if (result.length > 0 && result.every(s => s.changePercent === 0)) {
      result = []
    }
  }

  // 只显示有数据的板块
  result = result.filter(s => s.changePercent !== 0 || s.stocksCount > 0)

  // 按涨跌幅排序（涨幅大的在前）
  return result.sort((a, b) => b.changePercent - a.changePercent)
})

// 统计数据
const upCount = computed(() => {
  return filteredSectors.value.filter(s => s.changePercent > 0).length
})

const downCount = computed(() => {
  return filteredSectors.value.filter(s => s.changePercent < 0).length
})

const flatCount = computed(() => {
  return filteredSectors.value.filter(s => s.changePercent === 0).length
})

const avgChange = computed(() => {
  const all = filteredSectors.value
  if (all.length === 0) return 0
  return all.reduce((sum, s) => sum + s.changePercent, 0) / all.length
})

// 切换标签页
const switchTab = (tab: string) => {
  activeTab.value = tab
}

// 加载数据
const loadData = async () => {
  loading.value = true
  error.value = ''

  try {
    console.log('📡 开始请求板块数据（扁平视图）...')

    const response = await fetch(`/api/v1/market/sector-performance?limit=100`)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()

    if (data.success && data.sectors) {
      // 转换数据格式以适配前端
      sectors.value = data.sectors.map((s: any) => ({
        code: s.sector_code,
        name: s.sector_name,
        changePercent: Number(s.change_pct).toFixed(2),  // 保留2位小数
        stocksCount: s.stocks_count,
        amount: s.amount,
        price: s.price
      }))
      console.log(`✅ 成功加载 ${sectors.value.length} 个板块（扁平视图）`)
    } else {
      throw new Error('数据格式不正确')
    }
  } catch (e: any) {
    console.error('❌ 加载失败:', e)
    error.value = e.message || '加载失败'
    ElMessage.error('加载板块数据失败: ' + error.value)
  } finally {
    loading.value = false
  }
}

// 获取涨跌颜色（现代风格）
const getChangeColor = (changePercent: number): string => {
  const abs = Math.abs(changePercent)

  if (changePercent > 0) {
    // 红色渐变 - 5个等级（更柔和的现代色调）
    if (abs >= 10) return '#ff4d4f'
    if (abs >= 7) return '#ff7875'
    if (abs >= 5) return '#ff9c9e'
    if (abs >= 3) return '#ffb8b9'
    return '#ffd8d8'
  } else if (changePercent < 0) {
    // 绿色渐变 - 5个等级（更柔和的现代色调）
    if (abs >= 10) return '#52c41a'
    if (abs >= 7) return '#73d13d'
    if (abs >= 5) return '#95de64'
    if (abs >= 3) return '#b7eb8f'
    return '#d9f7be'
  } else {
    // 平盘 - 浅灰色
    return '#f5f5f5'
  }
}

// 显示板块详情
const showSectorDetail = (sector: SectorData) => {
  selectedSector.value = sector
  detailDialogVisible.value = true
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.tdx-sector-map {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 0;
  margin: 0;
}

/* 顶部标签栏 */
.tabs-header {
  display: flex;
  align-items: center;
  background: linear-gradient(to bottom, #ffffff, #f8f9fa);
  border-bottom: 3px solid #e0e0e0;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  user-select: none;
  position: relative;
  z-index: 100;
}

.tab-item {
  padding: 12px 28px;
  cursor: pointer;
  background: linear-gradient(to bottom, #e8e8e8, #dddddd);
  border-right: 1px solid #ccc;
  border-bottom: 3px solid transparent;
  margin-bottom: -3px;
  transition: all 0.3s ease;
  font-size: 14px;
  color: #555;
  font-weight: 500;
  position: relative;
}

.tab-item:hover {
  background: linear-gradient(to bottom, #f0f0f0, #e5e5e5);
  color: #333;
}

.tab-item.active {
  background: linear-gradient(to bottom, #ffffff, #fafafa);
  border-bottom: 3px solid #409eff;
  font-weight: 600;
  color: #409eff;
  box-shadow: inset 0 -1px 2px rgba(0, 0, 0, 0.05);
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(to right, #409eff, #66b1ff);
  border-radius: 0 0 2px 2px;
}

.tab-info {
  margin-left: auto;
  padding-right: 25px;
  font-size: 13px;
  color: #666;
  display: flex;
  gap: 20px;
  align-items: center;
  font-weight: 500;
}

.up-count {
  color: #f56c6c;
  font-weight: 600;
  background: rgba(245, 108, 108, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
}

.down-count {
  color: #67c23a;
  font-weight: 600;
  background: rgba(103, 194, 58, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
}

.flat-count {
  color: #909399;
  font-weight: 600;
  background: rgba(144, 147, 153, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
}

.avg-change {
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
}

.avg-change.positive {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.avg-change.negative {
  color: #67c23a;
  background: rgba(103, 194, 58, 0.1);
}

/* 地图容器 */
.map-container {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background: rgba(255, 255, 255, 0.5);
}

.loading,
.error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 100%;
  font-size: 16px;
  color: #666;
}

.error {
  color: #f56c6c;
}

/* 板块网格 - 扁平视图 */
.sector-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  padding: 10px;
}

/* 扁平板块单元格 */
.sector-cell {
  border: 2px solid rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: 80px;
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.sector-cell:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
  border-color: rgba(0, 0, 0, 0.3);
  z-index: 10;
}

.sector-name {
  font-size: 15px;
  font-weight: 700;
  line-height: 1.4;
  color: #333;
  margin-bottom: 8px;
}

.sector-change {
  font-size: 18px;
  font-weight: 800;
  color: #333;
  padding: 4px 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  margin-bottom: 6px;
}

.sector-stocks {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  background: rgba(0, 0, 0, 0.05);
  padding: 3px 8px;
  border-radius: 8px;
}

/* 板块详情对话框 */
.sector-detail {
  padding: 15px;
}

.detail-row {
  display: flex;
  margin-bottom: 18px;
  align-items: flex-start;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
  transition: background 0.2s;
}

.detail-row:hover {
  background: #ecf0f1;
}

.detail-label {
  font-weight: 600;
  min-width: 90px;
  color: #606266;
  font-size: 14px;
}

.detail-value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.detail-value.positive {
  color: #f56c6c;
  font-weight: 700;
}

.detail-value.negative {
  color: #67c23a;
  font-weight: 700;
}

.stocks-list {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 滚动条样式 */
.map-container::-webkit-scrollbar {
  width: 14px;
}

.map-container::-webkit-scrollbar-track {
  background: linear-gradient(to right, #f1f1f1, #e8e8e8);
  border-radius: 7px;
}

.map-container::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #c0c0c0, #a0a0a0);
  border-radius: 7px;
  border: 2px solid #f1f1f1;
}

.map-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #a0a0a0, #888888);
}

:deep(.el-icon) {
  font-size: 20px;
}
</style>
