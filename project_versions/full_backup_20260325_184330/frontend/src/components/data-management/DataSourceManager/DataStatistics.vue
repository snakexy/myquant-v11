<template>
  <div class="stats-section">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon primary">
          <font-awesome-icon icon="chart-line" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(tdxInfo?.dailyStocks || 0) }}</div>
          <div class="stat-label">日线数据</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon success">
          <font-awesome-icon icon="clock" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(tdxInfo?.minute5Stocks || 0) }}</div>
          <div class="stat-label">5分钟数据</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon warning">
          <font-awesome-icon icon="database" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(tdxInfo?.totalStocks || 0) }}</div>
          <div class="stat-label">可用股票</div>
        </div>
      </div>

      <div class="stat-card clickable" @click="showDateRangeDetail">
        <el-tooltip
          content="点击查看详细时间段"
          placement="top"
        >
          <div class="stat-icon info">
            <font-awesome-icon icon="calendar-days" />
          </div>
        </el-tooltip>
        <div class="stat-content">
          <div class="stat-value">{{ tdxInfo?.dateRange || '-' }}</div>
          <div class="stat-label">数据时间范围</div>
        </div>
      </div>
    </div>
  </div>

  <!-- 时间范围详情对话框 -->
  <el-dialog
    v-model="dateRangeDialogVisible"
    title="数据时间范围详情"
    width="600px"
  >
    <div class="date-range-detail">
      <div v-if="loadingDateRange" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在加载详细时间段...</span>
      </div>
      <div v-else-if="dateRangeDetails.length > 0">
        <div class="detail-section">
          <h4>📅 日线数据时间分布</h4>
          <div class="date-summary">
            <!-- 数据起始日期 -->
            <div class="summary-item" :class="{ editable: editingDate }">
              <span class="summary-label">数据起始日期:</span>
              <template v-if="!editingDate">
                <span class="summary-value">{{ customStartDate || dateRangeDetails[0]?.startDate || '-' }}</span>
                <el-button
                  text
                  size="small"
                  @click="startEditDate"
                  class="edit-btn"
                >
                  <font-awesome-icon icon="edit" />
                </el-button>
              </template>
              <el-date-picker
                v-else
                v-model="customStartDate"
                type="date"
                placeholder="选择起始日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                size="small"
                style="width: 160px"
                :clearable="false"
              />
            </div>

            <!-- 数据结束日期 -->
            <div class="summary-item" :class="{ editable: editingDate }">
              <span class="summary-label">数据结束日期:</span>
              <template v-if="!editingDate">
                <span class="summary-value">{{ customEndDate || dateRangeDetails[0]?.endDate || '-' }}</span>
                <el-button
                  text
                  size="small"
                  @click="startEditDate"
                  class="edit-btn"
                >
                  <font-awesome-icon icon="edit" />
                </el-button>
              </template>
              <el-date-picker
                v-else
                v-model="customEndDate"
                type="date"
                placeholder="选择结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                size="small"
                style="width: 160px"
                :clearable="false"
              />
            </div>

            <!-- 编辑确认按钮 -->
            <div v-if="editingDate" class="summary-item editing-actions">
              <el-button
                type="primary"
                size="small"
                @click="confirmDateEdit"
              >
                <font-awesome-icon icon="check" />
                确认
              </el-button>
              <el-button
                size="small"
                @click="cancelDateEdit"
              >
                <font-awesome-icon icon="times" />
                取消
              </el-button>
            </div>

            <div class="summary-item">
              <span class="summary-label">检测到的范围:</span>
              <span class="summary-value info">{{ dateRangeDetails[0]?.startDate || '-' }} ~ {{ dateRangeDetails[0]?.endDate || '-' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">最后更新:</span>
              <span class="summary-value">{{ tdxInfo?.lastUpdate || '-' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">交易日数量:</span>
              <span class="summary-value">{{ estimatedTradingDays }} 天</span>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="detail-section">
          <h4>📊 数据完整性说明</h4>
          <div class="completeness-notice">
            <el-icon><InfoFilled /></el-icon>
            <span>实际数据可能存在缺失，以上显示的是文件时间戳估算的范围。建议通过数据验证功能检查具体缺失的交易日。</span>
          </div>
        </div>
      </div>
      <div v-else class="no-data">
        <el-icon><WarningFilled /></el-icon>
        <span>暂无详细时间段信息</span>
      </div>
    </div>

    <template #footer>
      <el-button @click="dateRangeDialogVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, InfoFilled, WarningFilled } from '@element-plus/icons-vue'
import type { TDXInfo } from '../../shared/types'

interface Props {
  tdxInfo: TDXInfo | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update-date-range': [startDate: string, endDate: string]
}>()

const dateRangeDialogVisible = ref(false)
const loadingDateRange = ref(false)
const dateRangeDetails = ref<any[]>([])

// 自定义日期范围
const customStartDate = ref<string>('')
const customEndDate = ref<string>('')
const editingDate = ref(false)
const originalStartDate = ref<string>('')
const originalEndDate = ref<string>('')

// 开始编辑日期
const startEditDate = () => {
  originalStartDate.value = customStartDate.value
  originalEndDate.value = customEndDate.value
  editingDate.value = true
}

// 确认日期编辑
const confirmDateEdit = () => {
  if (customStartDate.value && customEndDate.value) {
    const start = new Date(customStartDate.value)
    const end = new Date(customEndDate.value)

    if (start > end) {
      ElMessage.warning('起始日期不能晚于结束日期')
      return
    }

    emit('update-date-range', customStartDate.value, customEndDate.value)
    ElMessage.success('日期范围已更新')
  }
  editingDate.value = false
}

// 取消日期编辑
const cancelDateEdit = () => {
  customStartDate.value = originalStartDate.value
  customEndDate.value = originalEndDate.value
  editingDate.value = false
}

// 监听日期变化，发送更新事件（仅在非编辑模式下）
watch([customStartDate, customEndDate], ([newStart, newEnd]) => {
  if (!editingDate.value && newStart && newEnd) {
    emit('update-date-range', newStart, newEnd)
  }
})

// 估算交易日数量（基于自定义日期范围）
const estimatedTradingDays = computed(() => {
  if (!customStartDate.value || !customEndDate.value) {
    return '-'
  }

  const start = new Date(customStartDate.value)
  const end = new Date(customEndDate.value)

  if (start > end) {
    return '起始日期不能晚于结束日期'
  }

  // 计算工作日（排除周六日）
  let tradingDays = 0
  const current = new Date(start)

  while (current <= end) {
    const dayOfWeek = current.getDay()
    if (dayOfWeek !== 0 && dayOfWeek !== 6) {
      tradingDays++
    }
    current.setDate(current.getDate() + 1)
  }

  return tradingDays.toLocaleString()
})

const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

const showDateRangeDetail = async () => {
  if (!props.tdxInfo) {
    ElMessage.warning('请先检测数据源')
    return
  }

  dateRangeDialogVisible.value = true
  loadingDateRange.value = true

  try {
    // 模拟加载详细时间段数据
    // 实际应该调用后端API获取真实的时间段信息
    await new Promise(resolve => setTimeout(resolve, 500))

    // 从 dateRange 解析出开始和结束日期
    const dateRange = props.tdxInfo.dateRange || ''
    const parts = dateRange.split(' ~ ')

    if (parts.length === 2) {
      dateRangeDetails.value = [{
        type: '日线数据',
        startDate: parts[0],
        endDate: parts[1],
        tradingDays: '估算约 ' + (props.tdxInfo.dailyStocks || 0) + ' 只股票'
      }]

      // 初始化自定义日期为检测到的范围
      customStartDate.value = parts[0]
      customEndDate.value = parts[1]
    } else {
      dateRangeDetails.value = []
    }
  } catch (error) {
    console.error('加载时间段详情失败:', error)
    ElMessage.error('加载时间段详情失败')
  } finally {
    loadingDateRange.value = false
  }
}
</script>

<style scoped>
.stats-section {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 20px;
  color: white;
}

.stat-icon.primary {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
}

.stat-icon.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-icon.warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-icon.info {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: white;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

/* 对话框样式 */
:deep(.el-dialog) {
  background: rgba(26, 26, 46, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

:deep(.el-dialog__title) {
  color: #ffffff;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  padding: 20px;
  color: rgba(255, 255, 255, 0.8);
}

:deep(.el-dialog__footer) {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px 20px;
}

.date-range-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.loading-state .el-icon {
  font-size: 32px;
  color: #2962ff;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.date-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.summary-item.editable {
  background: rgba(102, 126, 234, 0.05);
  border-color: rgba(102, 126, 234, 0.2);
}

.summary-item.editable:hover {
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.3);
}

.summary-item.editing-actions {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.2);
  justify-content: center;
  gap: 12px;
}

.edit-btn {
  opacity: 0.4;
  transition: opacity 0.2s ease;
  padding: 4px 8px;
  color: rgba(255, 255, 255, 0.6);
  margin-left: 8px;
}

.edit-btn:hover {
  opacity: 1;
  color: #2962ff;
}

.summary-item:hover .edit-btn {
  opacity: 0.7;
}

.summary-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.summary-value {
  font-size: 14px;
  font-weight: 600;
  color: #10b981;
  font-family: 'Consolas', 'Monaco', monospace;
}

.summary-value.info {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.completeness-notice {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.completeness-notice .el-icon {
  margin-top: 2px;
  font-size: 20px;
  color: #f59e0b;
  flex-shrink: 0;
}

.completeness-notice span {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px;
  color: rgba(255, 255, 255, 0.4);
}

.no-data .el-icon {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.2);
}

:deep(.el-divider) {
  border-color: rgba(255, 255, 255, 0.1);
}

/* 日期选择器深色主题 */
:deep(.el-date-picker) {
  --el-input-bg-color: rgba(102, 126, 234, 0.08);
  --el-input-border-color: rgba(102, 126, 234, 0.3);
  --el-input-text-color: rgba(255, 255, 255, 0.9);
  --el-bg-color: rgba(26, 26, 46, 0.95);
}

:deep(.el-date-picker .el-input__wrapper) {
  background-color: rgba(102, 126, 234, 0.08) !important;
  box-shadow: none !important;
  border: 1px solid rgba(102, 126, 234, 0.3) !important;
}

:deep(.el-date-picker .el-input__wrapper:hover) {
  background-color: rgba(102, 126, 234, 0.12) !important;
  border-color: rgba(102, 126, 234, 0.6) !important;
}

:deep(.el-date-picker .el-input__wrapper.is-focus) {
  background-color: rgba(102, 126, 234, 0.15) !important;
  border-color: #2962ff !important;
}

:deep(.el-date-picker .el-input__inner) {
  color: rgba(255, 255, 255, 0.9) !important;
}
</style>
