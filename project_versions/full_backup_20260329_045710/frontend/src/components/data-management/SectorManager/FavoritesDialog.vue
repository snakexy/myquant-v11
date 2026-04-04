<template>
  <el-dialog
    v-model="dialogVisible"
    title="📁 板块收藏夹"
    width="900px"
    :before-close="handleClose"
    custom-class="favorites-dialog"
    append-to-body
    :z-index="20000"
  >
    <!-- 顶部操作栏 -->
    <div class="dialog-toolbar">
      <el-button
        type="primary"
        :icon="Plus"
        @click="showCreateDialog = true"
      >
        新建收藏夹
      </el-button>
      <el-button
        :icon="Download"
        @click="handleExportAll"
      >
        导出全部
      </el-button>
      <el-upload
        :show-file-list="false"
        :before-upload="handleImportFile"
        accept=".json"
        style="display: inline-block; margin-left: 8px;"
      >
        <el-button :icon="Upload">
          导入收藏
        </el-button>
      </el-upload>
    </div>

    <!-- 收藏夹列表 -->
    <div v-if="collections.length > 0" class="collections-container">
      <div
        v-for="collection in collections"
        :key="collection.id"
        class="collection-item"
      >
        <!-- 收藏夹头部 -->
        <div class="collection-header">
          <div class="collection-info">
            <h4 class="collection-name">
              {{ collection.name }}
              <el-tag v-if="collection.sectors.length > 0" size="small" type="info">
                {{ collection.sectors.length }} 个板块
              </el-tag>
            </h4>
            <p class="collection-description">{{ collection.description || '暂无描述' }}</p>
            <p class="collection-meta">
              <span>创建于 {{ formatDate(collection.createdAt) }}</span>
              <span v-if="collection.updatedAt !== collection.createdAt">
                · 更新于 {{ formatDate(collection.updatedAt) }}
              </span>
            </p>
          </div>
          <div class="collection-actions">
            <el-button
              size="small"
              :icon="FolderOpened"
              @click="handleLoadCollection(collection)"
            >
              加载
            </el-button>
            <el-button
              size="small"
              :icon="Edit"
              @click="handleEditCollection(collection)"
            >
              编辑
            </el-button>
            <el-button
              size="small"
              :icon="Delete"
              type="danger"
              @click="handleDeleteCollection(collection)"
            >
              删除
            </el-button>
          </div>
        </div>

        <!-- 板块列表 -->
        <div class="sectors-list">
          <div
            v-for="sector in collection.sectors"
            :key="sector.code"
            class="sector-tag-item"
          >
            <el-tag closable @close="handleRemoveSector(collection.id, sector)">
              {{ sector.name }}
              <span v-if="sector.stockCount" class="sector-count">
                ({{ sector.stockCount }})
              </span>
            </el-tag>
          </div>
          <el-button
            v-if="collection.sectors.length === 0"
            size="small"
            text
            :icon="Plus"
            @click="handleAddSectors(collection)"
          >
            添加板块
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty description="暂无收藏夹">
        <template #image>
          <div class="empty-icon">📁</div>
        </template>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
          创建第一个收藏夹
        </el-button>
      </el-empty>
    </div>

    <!-- 创建/编辑收藏夹对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingCollection ? '编辑收藏夹' : '新建收藏夹'"
      width="600px"
      append-to-body
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input
            v-model="form.name"
            placeholder="例如：我的科技股、AI组合等"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="例如：AI + 芯片 + 5G"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCollection" :disabled="!form.name.trim()">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加板块对话框 -->
    <el-dialog
      v-model="showAddSectorsDialog"
      title="添加板块到收藏夹"
      width="700px"
      append-to-body
    >
      <div v-if="currentCollection" class="add-sectors-content">
        <p class="current-collection">
          当前收藏夹：<strong>{{ currentCollection.name }}</strong>
        </p>

        <el-input
          v-model="sectorSearchKeyword"
          placeholder="搜索板块名称..."
          :prefix-icon="Search"
          clearable
          style="margin-bottom: 16px;"
        />

        <div class="available-sectors">
          <div
            v-for="sector in filteredAvailableSectors"
            :key="sector.id"
            class="sector-select-item"
          >
            <el-checkbox
              :model-value="isSectorSelected(sector)"
              @change="handleSectorSelect(sector, $event)"
            >
              {{ sector.name }}
              <span v-if="sector.stockCount" class="sector-count">
                ({{ sector.stockCount }}只)
              </span>
            </el-checkbox>
          </div>
        </div>

        <div class="selected-summary">
          已选择 {{ selectedSectors.length }} 个板块
        </div>
      </div>

      <template #footer>
        <el-button @click="showAddSectorsDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="handleConfirmAddSectors"
          :disabled="selectedSectors.length === 0"
        >
          添加 ({{ selectedSectors.length }})
        </el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Edit,
  Delete,
  Download,
  Upload,
  FolderOpened,
  Search
} from '@element-plus/icons-vue'
import type { SectorNode } from '@/components/data-management/shared/types'
import {
  getAllCollections,
  createCollection,
  updateCollection,
  deleteCollection,
  addSectorToCollection,
  removeSectorFromCollection,
  exportFavoritesToFile,
  importFavoritesFromFile,
  sectorNodeToFavorite,
  type FavoriteCollection,
  type FavoriteSector
} from './favorites-storage'

interface Props {
  visible: boolean
  availableSectors?: SectorNode[]  // 所有可用的板块列表
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'load-collection': [sectors: FavoriteSector[]]
}>()

// 状态
const dialogVisible = ref(false)
const collections = ref<FavoriteCollection[]>([])
const showCreateDialog = ref(false)
const showAddSectorsDialog = ref(false)
const editingCollection = ref<FavoriteCollection | null>(null)
const currentCollection = ref<FavoriteCollection | null>(null)
const sectorSearchKeyword = ref('')
const selectedSectors = ref<FavoriteSector[]>([])

// 表单数据
const form = ref({
  name: '',
  description: ''
})

// 监听 visible 变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    loadCollections()
  }
})

watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

// 加载收藏夹列表
const loadCollections = () => {
  collections.value = getAllCollections()
}

// 过滤可用板块
const filteredAvailableSectors = computed(() => {
  if (!props.availableSectors) return []

  const keyword = sectorSearchKeyword.value.toLowerCase().trim()
  if (!keyword) return props.availableSectors

  return props.availableSectors.filter(sector =>
    sector.name.toLowerCase().includes(keyword) ||
    sector.id.toLowerCase().includes(keyword)
  )
})

// 格式化日期
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`

  return date.toLocaleDateString('zh-CN')
}

// 处理创建收藏夹
const handleSaveCollection = () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入收藏夹名称')
    return
  }

  if (editingCollection.value) {
    // 更新
    updateCollection(editingCollection.value.id, {
      name: form.value.name,
      description: form.value.description
    })
    ElMessage.success('收藏夹已更新')
  } else {
    // 创建
    createCollection(form.value.name, form.value.description)
    ElMessage.success('收藏夹已创建')
  }

  loadCollections()
  showCreateDialog.value = false
  resetForm()
}

// 处理编辑收藏夹
const handleEditCollection = (collection: FavoriteCollection) => {
  editingCollection.value = collection
  form.value.name = collection.name
  form.value.description = collection.description
  showCreateDialog.value = true
}

// 处理删除收藏夹
const handleDeleteCollection = async (collection: FavoriteCollection) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除收藏夹"${collection.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )

    deleteCollection(collection.id)
    loadCollections()
    ElMessage.success('收藏夹已删除')
  } catch {
    // 用户取消
  }
}

// 处理加载收藏夹
const handleLoadCollection = (collection: FavoriteCollection) => {
  emit('load-collection', collection.sectors)
  ElMessage.success(`已加载 ${collection.sectors.length} 个板块`)
  handleClose()
}

// 处理添加板块
const handleAddSectors = (collection: FavoriteCollection) => {
  currentCollection.value = collection
  selectedSectors.value = []
  sectorSearchKeyword.value = ''
  showAddSectorsDialog.value = true
}

// 检查板块是否已选择
const isSectorSelected = (sector: SectorNode): boolean => {
  if (!currentCollection.value) return false

  const code = (sector as any).code || sector.name
  return currentCollection.value.sectors.some(s => s.code === code)
}

// 处理板块选择
const handleSectorSelect = (sector: SectorNode, checked: boolean) => {
  const favorite = sectorNodeToFavorite(sector)

  if (checked) {
    selectedSectors.value.push(favorite)
  } else {
    const index = selectedSectors.value.findIndex(s => s.code === favorite.code)
    if (index > -1) {
      selectedSectors.value.splice(index, 1)
    }
  }
}

// 确认添加板块
const handleConfirmAddSectors = () => {
  if (!currentCollection.value || selectedSectors.value.length === 0) {
    return
  }

  let successCount = 0
  let duplicateCount = 0

  selectedSectors.value.forEach(sector => {
    const added = addSectorToCollection(currentCollection.value!.id, sector)
    if (added) {
      successCount++
    } else {
      duplicateCount++
    }
  })

  loadCollections()

  if (successCount > 0) {
    ElMessage.success(`已添加 ${successCount} 个板块`)
  }
  if (duplicateCount > 0) {
    ElMessage.warning(`${duplicateCount} 个板块已存在`)
  }

  showAddSectorsDialog.value = false
}

// 处理移除板块
const handleRemoveSector = (collectionId: string, sector: FavoriteSector) => {
  removeSectorFromCollection(collectionId, sector.code)
  loadCollections()
  ElMessage.success('板块已移除')
}

// 处理导出全部
const handleExportAll = () => {
  if (collections.value.length === 0) {
    ElMessage.warning('暂无收藏夹可导出')
    return
  }

  exportFavoritesToFile()
  ElMessage.success('收藏夹已导出')
}

// 处理导入文件
const handleImportFile = async (file: File) => {
  const success = await importFavoritesFromFile(file)

  if (success) {
    loadCollections()
    ElMessage.success('收藏夹已导入')
  } else {
    ElMessage.error('导入失败，请检查文件格式')
  }

  return false // 阻止自动上传
}

// 重置表单
const resetForm = () => {
  form.value.name = ''
  form.value.description = ''
  editingCollection.value = null
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}
</script>

<style>
/* 全局样式 - 确保对话框在导航栏之上 */
.favorites-dialog .el-dialog {
  z-index: 20000 !important;
}

.favorites-dialog .el-dialog__header {
  z-index: 20001 !important;
}

.favorites-dialog .el-dialog__body {
  z-index: 20000 !important;
}

.favorites-dialog .el-overlay {
  z-index: 19999 !important;
}
</style>

<style scoped>
/* 工具栏 */
.dialog-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* 收藏夹容器 */
.collections-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 收藏夹项 */
.collection-item {
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.collection-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(102, 126, 234, 0.3);
}

/* 收藏夹头部 */
.collection-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.collection-info {
  flex: 1;
}

.collection-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
}

.collection-description {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.collection-meta {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.collection-actions {
  display: flex;
  gap: 8px;
}

/* 板块列表 */
.sectors-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.sector-tag-item {
  display: inline-block;
}

.sector-count {
  font-size: 11px;
  opacity: 0.7;
}

/* 空状态 */
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

/* 添加板块对话框 */
.add-sectors-content {
  max-height: 400px;
  display: flex;
  flex-direction: column;
}

.current-collection {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.available-sectors {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background: rgba(26, 26, 46, 0.5);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sector-select-item {
  padding: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.sector-select-item:last-child {
  border-bottom: none;
}

.sector-select-item :deep(.el-checkbox__label) {
  color: rgba(255, 255, 255, 0.9);
}

.selected-summary {
  margin-top: 12px;
  padding: 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 6px;
  text-align: center;
  font-size: 14px;
  color: #2962ff;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 768px) {
  .collection-header {
    flex-direction: column;
    gap: 12px;
  }

  .collection-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .dialog-toolbar {
    flex-wrap: wrap;
  }
}
</style>
