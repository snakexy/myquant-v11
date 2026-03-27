<template>
  <el-dialog
    v-model="dialogVisible"
    title="🔄 批量更新板块数据"
    width="700px"
    :before-close="handleClose"
    custom-class="batch-update-dialog"
    append-to-body
    :z-index="20000"
  >
    <!-- 选择板块 -->
    <div v-if="!updating" class="selection-section">
      <div class="selection-header">
        <h4>选择要更新的板块</h4>
        <el-button size="small" @click="selectAllFromFavorites">
          从收藏夹选择
        </el-button>
      </div>

      <el-input
        v-model="searchKeyword"
        placeholder="搜索板块名称..."
        :prefix-icon="Search"
        clearable
        style="margin-bottom: 16px;"
      />

      <div class="sectors-grid">
        <div
          v-for="sector in filteredSectors"
          :key="sector.id"
          class="sector-item"
        >
          <el-checkbox
            :model-value="isSectorSelected(sector)"
            @change="handleSectorToggle(sector, $event)"
          >
            {{ sector.name }}
            <span v-if="sector.stockCount" class="count">
              ({{ sector.stockCount }})
            </span>
          </el-checkbox>
        </div>
      </div>

      <div class="selection-summary">
        已选择 <strong>{{ selectedSectors.length }}</strong> 个板块
      </div>
    </div>

    <!-- 更新进度 -->
    <div v-else class="progress-section">
      <div class="progress-header">
        <h4>正在更新板块数据</h4>
        <el-tag :type="getProgressStatus().type">
          {{ getProgressStatus().label }}
        </el-tag>
      </div>

      <el-progress
        :percentage="updateProgress"
        :status="updateProgress === 100 ? 'success' : undefined"
        :stroke-width="20"
        style="margin: 20px 0;"
      >
        <template #default="{ percentage }">
          <span class="progress-text">{{ percentage }}%</span>
        </template>
      </el-progress>

      <div class="progress-info">
        <p v-if="currentUpdateSector">
          <el-icon class="is-loading"><loading /></el-icon>
          正在更新: <strong>{{ currentUpdateSector.name }}</strong>
        </p>
        <p class="stats">
          已完成: <strong>{{ updateStats.completed }}</strong> /
          失败: <strong>{{ updateStats.failed }}</strong> /
          剩余: <strong>{{ updateStats.remaining }}</strong>
        </p>
        <p v-if="estimatedTimeRemaining" class="time-remaining">
          预计剩余时间: {{ estimatedTimeRemaining }}
        </p>
      </div>

      <!-- 失败列表 -->
      <div v-if="failedUpdates.length > 0" class="failed-section">
        <el-collapse>
          <el-collapse-item title="查看失败项" name="failed">
            <div class="failed-list">
              <div
                v-for="item in failedUpdates"
                :key="item.sector.id"
                class="failed-item"
              >
                <span class="sector-name">{{ item.sector.name }}</span>
                <span class="error-message">{{ item.error }}</span>
                <el-button
                  size="small"
                  type="primary"
                  link
                  @click="handleRetrySector(item)"
                >
                  重试
                </el-button>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <!-- 底部操作 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">
          {{ updating ? '取消' : '关闭' }}
        </el-button>
        <el-button
          v-if="!updating && selectedSectors.length > 0"
          type="primary"
          @click="handleStartUpdate"
          :loading="updating"
        >
          开始更新 ({{ selectedSectors.length }})
        </el-button>
        <el-button
          v-if="updating && updateProgress === 100"
          type="success"
          @click="handleFinish"
        >
          完成
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Search } from '@element-plus/icons-vue'
import type { SectorNode } from '@/components/data-management/shared/types'
import { fetchSectorStocks } from '@/components/data-management/shared/api'
import { getAllCollections, sectorNodeToFavorite } from './favorites-storage'

interface Props {
  visible: boolean
  availableSectors: SectorNode[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'update-complete': [stats: UpdateStats]
}>()

// ==================== 类型定义 ====================

interface FailedUpdate {
  sector: SectorNode
  error: string
  retryCount: number
}

interface UpdateStats {
  total: number
  completed: number
  failed: number
  remaining: number
}

// ==================== 状态 ====================

const dialogVisible = ref(false)
const searchKeyword = ref('')
const selectedSectors = ref<SectorNode[]>([])
const updating = ref(false)
const updateProgress = ref(0)
const currentUpdateSector = ref<SectorNode | null>(null)
const updateStats = ref<UpdateStats>({
  total: 0,
  completed: 0,
  failed: 0,
  remaining: 0
})
const failedUpdates = ref<FailedUpdate[]>([])
const startTime = ref<number>(0)

// ==================== 计算属性 ====================

const filteredSectors = computed(() => {
  if (!searchKeyword.value) return props.availableSectors

  const keyword = searchKeyword.value.toLowerCase().trim()
  return props.availableSectors.filter(sector =>
    sector.name.toLowerCase().includes(keyword)
  )
})

const estimatedTimeRemaining = computed(() => {
  if (!startTime.value || updateProgress.value === 0) return null

  const elapsed = Date.now() - startTime.value
  const totalEstimated = (elapsed / updateProgress.value) * 100
  const remaining = totalEstimated - elapsed

  if (remaining < 60000) {
    return `${Math.ceil(remaining / 1000)}秒`
  } else {
    return `${Math.ceil(remaining / 60000)}分钟`
  }
})

// ==================== 监听 ====================

watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (!newVal) {
    resetState()
  }
})

watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

// ==================== 方法 ====================

const resetState = () => {
  searchKeyword.value = ''
  selectedSectors.value = []
  updating.value = false
  updateProgress.value = 0
  currentUpdateSector.value = null
  updateStats.value = {
    total: 0,
    completed: 0,
    failed: 0,
    remaining: 0
  }
  failedUpdates.value = []
  startTime.value = 0
}

const isSectorSelected = (sector: SectorNode): boolean => {
  return selectedSectors.value.some(s => s.id === sector.id)
}

const handleSectorToggle = (sector: SectorNode, checked: boolean) => {
  if (checked) {
    if (!isSectorSelected(sector)) {
      selectedSectors.value.push(sector)
    }
  } else {
    const index = selectedSectors.value.findIndex(s => s.id === sector.id)
    if (index > -1) {
      selectedSectors.value.splice(index, 1)
    }
  }
}

const selectAllFromFavorites = () => {
  const collections = getAllCollections()
  const allFavoriteSectors = new Set<string>()

  collections.forEach(collection => {
    collection.sectors.forEach(sector => {
      allFavoriteSectors.add(sector.code)
    })
  })

  selectedSectors.value = props.availableSectors.filter(sector => {
    const code = (sector as any).code || sector.name
    return allFavoriteSectors.has(code)
  })

  ElMessage.success(`已从收藏夹选择 ${selectedSectors.value.length} 个板块`)
}

const getProgressStatus = (): { type: any; label: string } => {
  if (updateProgress.value === 100) {
    return { type: 'success', label: '更新完成' }
  } else if (updateStats.value.failed > 0) {
    return { type: 'danger', label: '部分失败' }
  } else if (updateProgress.value > 0) {
    return { type: 'warning', label: '更新中' }
  }
  return { type: 'info', label: '准备就绪' }
}

const handleStartUpdate = async () => {
  if (selectedSectors.value.length === 0) {
    ElMessage.warning('请先选择要更新的板块')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要批量更新 ${selectedSectors.value.length} 个板块的数据吗？`,
      '确认更新',
      {
        type: 'warning',
        confirmButtonText: '开始更新',
        cancelButtonText: '取消'
      }
    )

    startUpdate()
  } catch {
    // 用户取消
  }
}

const startUpdate = async () => {
  updating.value = true
  startTime.value = Date.now()

  updateStats.value = {
    total: selectedSectors.value.length,
    completed: 0,
    failed: 0,
    remaining: selectedSectors.value.length
  }

  // 逐个更新板块
  for (let i = 0; i < selectedSectors.value.length; i++) {
    const sector = selectedSectors.value[i]
    await updateSector(sector)

    updateProgress.value = Math.round(((i + 1) / selectedSectors.value.length) * 100)
    updateStats.value.completed = i + 1
    updateStats.value.remaining = selectedSectors.value.length - i - 1
  }

  updating.value = false

  if (failedUpdates.value.length === 0) {
    ElMessage.success(`成功更新 ${updateStats.value.completed} 个板块`)
  } else {
    ElMessage.warning(
      `更新完成：成功 ${updateStats.value.completed} 个，失败 ${failedUpdates.value.length} 个`
    )
  }

  emit('update-complete', updateStats.value)
}

const updateSector = async (sector: SectorNode) => {
  currentUpdateSector.value = sector

  try {
    const code = (sector as any).code || sector.name
    await fetchSectorStocks(code)
  } catch (error: any) {
    console.error(`更新板块 ${sector.name} 失败:`, error)

    const failedIndex = failedUpdates.value.findIndex(f => f.sector.id === sector.id)
    if (failedIndex === -1) {
      failedUpdates.value.push({
        sector,
        error: error.message || '未知错误',
        retryCount: 0
      })
    }
    updateStats.value.failed++
  }
}

const handleRetrySector = async (item: FailedUpdate) => {
  if (item.retryCount >= 3) {
    ElMessage.warning('已达到最大重试次数')
    return
  }

  // 从失败列表中移除
  const index = failedUpdates.value.findIndex(f => f.sector.id === item.sector.id)
  if (index > -1) {
    failedUpdates.value.splice(index, 1)
  }

  // 重试
  item.retryCount++
  await updateSector(item.sector)

  if (failedUpdates.value.findIndex(f => f.sector.id === item.sector.id) === -1) {
    ElMessage.success(`${item.sector.name} 重试成功`)
  } else {
    ElMessage.error(`${item.sector.name} 重试失败`)
  }
}

const handleFinish = () => {
  handleClose()
  // 刷新父组件数据
  emit('update-complete', updateStats.value)
}

const handleClose = () => {
  if (updating.value) {
    ElMessageBox.confirm(
      '更新正在进行中，确定要取消吗？',
      '确认取消',
      {
        type: 'warning'
      }
    ).then(() => {
      dialogVisible.value = false
    }).catch(() => {
      // 用户取消
    })
  } else {
    dialogVisible.value = false
  }
}
</script>

<style>
/* 全局样式 - 确保对话框在导航栏之上 */
.batch-update-dialog .el-dialog {
  z-index: 20000 !important;
}

.batch-update-dialog .el-dialog__header {
  z-index: 20001 !important;
}

.batch-update-dialog .el-dialog__body {
  z-index: 20000 !important;
}

.batch-update-dialog .el-overlay {
  z-index: 19999 !important;
}
</style>

<style scoped>
/* 选择区域 */
.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.selection-header h4 {
  margin: 0;
  font-size: 16px;
  color: #ffffff;
}

.sectors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding: 16px;
  background: rgba(26, 26, 46, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sector-item {
  padding: 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  transition: all 0.2s ease;
}

.sector-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.sector-item .count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.sector-item :deep(.el-checkbox__label) {
  color: rgba(255, 255, 255, 0.9);
}

.selection-summary {
  margin-top: 16px;
  padding: 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 6px;
  text-align: center;
  font-size: 14px;
  color: #2962ff;
}

.selection-summary strong {
  font-size: 18px;
  font-weight: 700;
}

/* 进度区域 */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-header h4 {
  margin: 0;
  font-size: 16px;
  color: #ffffff;
}

.progress-text {
  font-weight: 600;
  color: #ffffff;
}

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: rgba(26, 26, 46, 0.5);
  border-radius: 8px;
}

.progress-info p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-info .stats {
  display: flex;
  gap: 16px;
}

.progress-info strong {
  color: #2962ff;
  font-weight: 600;
}

.time-remaining {
  font-size: 13px !important;
  color: rgba(255, 255, 255, 0.6) !important;
}

.progress-info .el-icon {
  color: #2962ff;
}

/* 失败列表 */
.failed-section {
  padding: 16px;
  background: rgba(245, 108, 108, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(245, 108, 108, 0.3);
}

.failed-section :deep(.el-collapse) {
  border: none;
}

.failed-section :deep(.el-collapse-item__header) {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  border: none;
}

.failed-section :deep(.el-collapse-item__wrap) {
  background: transparent;
  border: none;
}

.failed-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.failed-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(245, 108, 108, 0.1);
  border-radius: 6px;
}

.failed-item .sector-name {
  flex: 1;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.failed-item .error-message {
  flex: 2;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* 底部操作 */
.dialog-footer {
  display: flex;
  justify-content: space-between;
  width: 100%;
}
</style>
