<template>
  <div class="data-management-display">
    <!-- VSCode 风格标签页头部 -->
    <div class="vscode-tabs-header">
      <div class="tabs-container">
        <div
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab-item', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          <font-awesome-icon :icon="tab.icon" class="tab-icon" />
          <span class="tab-label">{{ tab.label }}</span>
          <span v-if="tab.badge" :class="['tab-badge', tab.badgeClass]">{{ tab.badge }}</span>
        </div>
      </div>
    </div>

    <!-- 标签页内容区域 -->
    <div class="tab-content-container">
      <!-- 数据库管理 -->
      <transition name="tab-fade" mode="out-in">
        <div v-if="activeTab === 'database'" key="database" class="tab-content">
          <DatabaseManager
            :config="localConfig.database"
            :params="nodeData?.params"
            :selectedStockCodes="localConfig.selectedStockCodes"
            @update:selectedStockCodes="handleSelectedStocksChange"
            @update:selectedFrequencies="handleFrequenciesChange"
            @update:databaseStats="handleDatabaseStatsUpdate"
          />
        </div>

        <!-- 清洗报告 -->
        <div v-else-if="activeTab === 'cleaning'" key="cleaning" class="tab-content">
          <!-- 空状态提示 -->
          <div v-if="!hasCleaningData" class="cleaning-empty-state">
            <div class="empty-illustration">
              <div class="empty-circle">
                <font-awesome-icon icon="broom" />
              </div>
              <div class="empty-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
            <div class="empty-content">
              <h3>暂无清洗数据</h3>
              <p>在"数据库管理"标签页点击"运行清洗"按钮后即可查看报告</p>
              <button class="action-btn" @click="switchToDatabaseTab">
                <font-awesome-icon icon="database" />
                <span>去运行清洗</span>
              </button>
            </div>
          </div>

          <!-- 显示清洗报告 -->
          <DataCleaningReport
            v-else
            v-model="localConfig"
            :nodeData="nodeData"
          />
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import DatabaseManager from './DatabaseManager.vue'
import DataCleaningReport from '../../components/node/DataCleaningConfigSimple.vue'
import { timeRangeSyncState } from '@/utils/timeRangeSync'

interface Props {
  modelValue?: any
  nodeData?: any
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: any]
}>()

const localConfig = ref<any>({
  mode: props.modelValue?.mode || 'cleaning',
  // 数据清洗配置
  qlibDataPath: props.modelValue?.qlibDataPath || 'E:\\MyQuant_v8.0.1\\data\\qlib_data',
  frequency: props.modelValue?.frequency || 'daily',
  frequencies: props.modelValue?.frequencies || (props.modelValue?.frequency ? [props.modelValue.frequency] : ['daily']),
  dropMissing: props.modelValue?.dropMissing ?? true,
  maxMissingRatio: props.modelValue?.maxMissingRatio ?? 0.3,
  forwardFill: props.modelValue?.forwardFill ?? true,
  handleOutliers: props.modelValue?.handleOutliers ?? false,
  outlierMethod: props.modelValue?.outlierMethod || 'clip',
  normalize: props.modelValue?.normalize ?? false,
  includeIndex: props.modelValue?.includeIndex ?? true,
  // 🔧 已选标的代码
  selectedStockCodes: props.modelValue?.selectedStockCodes || [],
  selectedStockCount: props.modelValue?.selectedStockCount || 0,
  // 数据库管理配置
  database: props.modelValue?.database || {
    autoRefresh: false,
    showNeedsUpdateOnly: false,
    sortBy: 'code',
    sortOrder: 'asc',
    expiryThreshold: 7,
    batchUpdateLimit: 10
  },
  ...props.modelValue
})

// 🔧 添加日志：检查初始的 selectedStockCodes
console.log('[DataCleaning Display] 初始化 - localConfig.value.selectedStockCodes:', localConfig.value.selectedStockCodes)
console.log('[DataCleaning Display] 初始化 - props.modelValue:', props.modelValue)

// 当前激活的标签页
const activeTab = ref('database')

// 标签页定义
const tabs = computed(() => [
  {
    key: 'database',
    label: '数据库管理',
    icon: 'database'
  },
  {
    key: 'cleaning',
    label: '清洗报告',
    icon: 'chart-bar',
    badge: hasCleaningData.value ? '有数据' : '',
    badgeClass: 'badge-success'
  }
])

// 检查是否有清洗数据
const hasCleaningData = computed(() => {
  const content = props.nodeData?.data?.content || props.nodeData?.content
  return content && (
    content.conversionStatus === 'completed' ||
    content.originalRows > 0 ||
    content.stockCount > 0
  )
})

// 切换到数据库管理标签页
const switchToDatabaseTab = () => {
  activeTab.value = 'database'
}

// 🔧 处理选中的标的变更
const handleSelectedStocksChange = (stockCodes: string[]) => {
  console.log('[DataCleaning Display] 选中的标的代码:', stockCodes)

  // 将选中的标的代码保存到配置中
  localConfig.value.selectedStockCodes = stockCodes
  localConfig.value.selectedStockCount = stockCodes.length

  // 触发更新，让父组件知道选中状态变化
  emit('update:modelValue', { ...localConfig.value })
}

// 🔧 处理频率变更
const handleFrequenciesChange = (frequencies: string[]) => {
  console.log('[DataCleaning Display] 频率变化:', frequencies)

  // 将选中的频率保存到配置中
  localConfig.value.frequencies = frequencies

  // 同时保存到 params 中
  if (!localConfig.value.params) {
    localConfig.value.params = {}
  }
  localConfig.value.params.frequencies = frequencies

  // 触发更新，让父组件知道频率变化
  emit('update:modelValue', { ...localConfig.value })
}

// 🔧 处理数据库统计信息更新（来自 DatabaseManager）
const handleDatabaseStatsUpdate = (stats: any) => {
  console.log('[DataCleaning Display] 数据库统计信息更新:', stats)

  // 将统计信息保存到 localConfig 中（会通过 watch 传递给父组件）
  localConfig.value.data_overview = stats.data_overview
  localConfig.value.storage_info = stats.storage_info

  // 触发更新
  emit('update:modelValue', { ...localConfig.value })
}

// 监听配置变化
watch(localConfig, (newVal) => {
  emit('update:modelValue', { ...newVal })
}, { deep: true })

// 组件挂载时，从同步服务获取上游节点的频率配置
onMounted(() => {
  // 从同步状态获取合并后的频率（股票选择和指数选择的并集）
  const syncedFreqs = timeRangeSyncState.syncedFrequencies || []

  if (syncedFreqs.length > 0) {
    // 使用同步服务的频率更新本地配置
    console.log('[DataCleaning Display] 从同步服务获取频率:', syncedFreqs)

    // 更新本地参数
    localConfig.value.frequencies = [...syncedFreqs]
    if (syncedFreqs.length === 1) {
      localConfig.value.frequency = syncedFreqs[0]
    } else {
      localConfig.value.frequency = syncedFreqs[0] // 使用第一个作为主频率
    }

    // 手动触发更新，确保父组件接收到变化
    emit('update:modelValue', { ...localConfig.value })

    console.log('[DataCleaning Display] 频率已更新:', {
      frequency: localConfig.value.frequency,
      frequencies: localConfig.value.frequencies
    })
  }
})
</script>

<style scoped>
.data-management-display {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 500px;
  background: var(--bg-surface);
  border-radius: 12px;
  overflow: hidden;
}

/* VSCode 风格标签页头部 */
.vscode-tabs-header {
  background: linear-gradient(180deg, var(--bg-elevated) 0%, var(--bg-surface) 100%);
  border-bottom: 1px solid var(--border-color);
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.tabs-container {
  display: flex;
  gap: 4px;
  overflow-x: auto;
}

/* 隐藏滚动条 */
.tabs-container::-webkit-scrollbar {
  height: 0;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  user-select: none;
  margin-top: 8px;
}

.tab-item:hover {
  background: rgba(37, 99, 235, 0.15);
  color: var(--primary-color);
  transform: translateY(-1px);
}

.tab-item.active {
  background: var(--bg-surface);
  color: var(--primary-color);
  font-weight: 600;
  box-shadow: 0 -2px 8px rgba(37, 99, 235, 0.2);
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--primary-color) 100%);
  border-radius: 3px 3px 0 0;
  box-shadow: 0 0 10px var(--primary-color);
}

.tab-icon {
  font-size: 14px;
  transition: transform 0.3s ease;
}

.tab-item:hover .tab-icon {
  transform: scale(1.1);
}

.tab-label {
  white-space: nowrap;
}

.tab-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.badge-success {
  background: linear-gradient(135deg, var(--success-color) 0%, #059669 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.4);
}

/* 标签页内容区域 */
.tab-content-container {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-surface);
}

.tab-content {
  height: 100%;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 标签切换动画 */
.tab-fade-enter-active,
.tab-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tab-fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.tab-fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 空状态样式 */
.cleaning-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  min-height: 400px;
}

.empty-illustration {
  position: relative;
  margin-bottom: 32px;
}

.empty-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--bg-elevated) 0%, var(--bg-surface) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  position: relative;
  z-index: 1;
  box-shadow: 0 8px 32px rgba(37, 99, 235, 0.3);
  border: 2px solid var(--border-color);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.empty-circle i {
  font-size: 48px;
  color: var(--primary-color);
  opacity: 0.9;
}

.empty-dots {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
}

.empty-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary-color);
  opacity: 0.4;
  animation: bounce 1.4s infinite ease-in-out both;
}

.empty-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.empty-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.empty-content h3 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  letter-spacing: -0.5px;
}

.empty-content p {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0 0 32px 0;
  line-height: 1.6;
  max-width: 400px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.4);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.5);
}

.action-btn:active {
  transform: translateY(0);
}

.action-btn i {
  font-size: 16px;
}

/* 滚动条样式 */
.tab-content-container::-webkit-scrollbar {
  width: 8px;
}

.tab-content-container::-webkit-scrollbar-track {
  background: transparent;
}

.tab-content-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

.tab-content-container::-webkit-scrollbar-thumb:hover {
  background: var(--border-light);
}
</style>
