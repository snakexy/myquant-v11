<template>
  <div class="data-management-config">
    <!-- 功能模式选择 -->
    <div class="mode-section">
      <div class="section-title">功能模式</div>
      <el-radio-group v-model="localParams.mode" size="small" @change="onModeChange">
        <el-radio-button value="cleaning">
          <el-icon><Brush /></el-icon>
          <span>数据清洗</span>
        </el-radio-button>
        <el-radio-button value="database">
          <el-icon><DataLine /></el-icon>
          <span>数据库管理</span>
        </el-radio-button>
      </el-radio-group>
      <div class="form-tip">{{ modeDescription }}</div>
    </div>

    <el-divider />

    <!-- 数据清洗配置 -->
    <div v-show="localParams.mode === 'cleaning'" class="cleaning-config">
      <el-form label-position="top" size="small">
        <!-- QLib 数据保存路径 -->
        <el-form-item label="QLib数据保存路径">
          <el-input
            v-model="localParams.qlibDataPath"
            placeholder="E:\MyQuant_v8.0.1\data\qlib_data"
            clearable
          >
            <template #append>
              <el-button icon="Folder" @click="selectDirectory" />
            </template>
          </el-input>
          <div class="form-tip">QLib格式数据保存的目录路径</div>
        </el-form-item>

        <!-- 数据频率 -->
        <el-form-item label="数据频率 (支持多选)">
          <div class="frequency-group">
            <label class="checkbox-option" v-for="freq in dataFrequencies" :key="freq.value">
              <input
                type="checkbox"
                :value="freq.value"
                v-model="selectedFrequencies"
              />
              <span>{{ freq.label }}</span>
              <small v-if="freq.description">{{ freq.description }}</small>
            </label>
          </div>
        </el-form-item>

        <!-- 数据清洗选项 -->
        <div class="section-title">数据清洗选项</div>

        <el-form-item>
          <el-checkbox v-model="localParams.dropMissing">
            删除缺失值过多的股票
          </el-checkbox>
        </el-form-item>

        <el-form-item label="最大缺失比例" v-if="localParams.dropMissing">
          <el-slider
            v-model="localParams.maxMissingRatio"
            :min="0"
            :max="1"
            :step="0.05"
            :format-tooltip="(v) => `${(v * 100).toFixed(0)}%`"
          />
          <div class="form-tip">允许的最大数据缺失比例</div>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="localParams.forwardFill">
            前向填充缺失值
          </el-checkbox>
          <div class="form-tip">用前一个有效值填充缺失值</div>
        </el-form-item>

        <!-- 异常值处理 -->
        <div class="section-title">异常值处理</div>

        <el-form-item>
          <el-checkbox v-model="localParams.handleOutliers">
            启用异常值检测和处理
          </el-checkbox>
        </el-form-item>

        <el-form-item label="处理方法" v-if="localParams.handleOutliers">
          <el-radio-group v-model="localParams.outlierMethod">
            <el-radio value="clip">截断</el-radio>
            <el-radio value="winsorize">缩尾</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 其他选项 -->
        <div class="section-title">其他选项</div>

        <el-form-item>
          <el-checkbox v-model="localParams.normalize">
            标准化数据
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="localParams.includeIndex">
            包含指数数据
          </el-checkbox>
          <div class="form-tip">将上游指数数据一并转换为QLib格式</div>
        </el-form-item>
      </el-form>

      <!-- 转换状态显示 -->
      <div class="conversion-status" v-if="conversionStatus">
        <el-divider />
        <div class="status-header">转换状态</div>
        <div class="status-content">
          <el-tag :type="statusType" size="large">
            {{ statusText }}
          </el-tag>
          <div v-if="conversionData" class="status-details">
            <div class="detail-item">
              <span class="detail-label">数据路径:</span>
              <span class="detail-value">{{ conversionData.dataPath }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">标的数量:</span>
              <span class="detail-value">{{ conversionData.stockCount }} 只</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据库管理配置 -->
    <div v-show="localParams.mode === 'database'" class="database-config">
      <el-form label-position="top" size="small">
        <!-- 自动刷新 -->
        <div class="section-title">显示选项</div>

        <el-form-item>
          <el-checkbox v-model="localParams.database.autoRefresh">
            自动刷新数据库状态
          </el-checkbox>
          <div class="form-tip">每次打开节点时自动扫描数据库</div>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="localParams.database.showNeedsUpdateOnly">
            仅显示需要更新的股票
          </el-checkbox>
          <div class="form-tip">过滤显示数据超过7天的股票</div>
        </el-form-item>

        <!-- 排序选项 -->
        <div class="section-title">排序选项</div>

        <el-form-item label="默认排序字段">
          <el-select v-model="localParams.database.sortBy" style="width: 100%">
            <el-option label="股票代码" value="code" />
            <el-option label="股票名称" value="name" />
            <el-option label="更新日期" value="endDate" />
            <el-option label="记录数" value="recordCount" />
            <el-option label="数据年龄" value="dataAge" />
          </el-select>
        </el-form-item>

        <el-form-item label="排序顺序">
          <el-radio-group v-model="localParams.database.sortOrder">
            <el-radio value="asc">升序</el-radio>
            <el-radio value="desc">降序</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 更新设置 -->
        <div class="section-title">更新设置</div>

        <el-form-item label="数据过期阈值（天）">
          <el-slider
            v-model="localParams.database.expiryThreshold"
            :min="1"
            :max="90"
            :step="1"
            :format-tooltip="(v) => `${v} 天`"
          />
          <div class="form-tip">超过此天数的数据将被标记为需要更新</div>
        </el-form-item>

        <el-form-item label="批量更新限制">
          <el-input-number
            v-model="localParams.database.batchUpdateLimit"
            :min="1"
            :max="100"
            :step="5"
            style="width: 100%"
          />
          <div class="form-tip">单次批量更新的最大股票数量</div>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Brush, DataLine } from '@element-plus/icons-vue'
import { timeRangeSyncService, timeRangeSyncState } from '@/utils/timeRangeSync'

interface Props {
  params: Record<string, any>
  data?: any
}

interface Emits {
  (e: 'update:params', value: Record<string, any>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 数据频率选项
const dataFrequencies = [
  { label: '日线', value: 'daily' },
  { label: '5分钟', value: '5min', description: '(短线交易分析)' },
  { label: '15分钟', value: '15min', description: '(适合日内交易)' },
  { label: '30分钟', value: '30min', description: '(适合波段操作)' },
  { label: '60分钟', value: '60min', description: '(适合中短期趋势)' }
]

// 本地参数副本
const localParams = ref<Record<string, any>>({
  mode: 'cleaning',
  // 数据清洗配置
  qlibDataPath: 'E:\\MyQuant_v8.0.1\\data\\qlib_data',
  frequency: 'daily',
  frequencies: ['daily'],
  dropMissing: true,
  maxMissingRatio: 0.3,
  forwardFill: true,
  handleOutliers: false,
  outlierMethod: 'clip',
  normalize: false,
  includeIndex: true,
  // 数据库管理配置
  database: {
    autoRefresh: false,
    showNeedsUpdateOnly: false,
    sortBy: 'code',
    sortOrder: 'asc',
    expiryThreshold: 7,
    batchUpdateLimit: 10
  },
  ...props.params
})

// 多频率选择（兼容旧的单频率配置）
const selectedFrequencies = ref<string[]>(
  localParams.value.frequencies ||
  (localParams.value.frequency ? [localParams.value.frequency] : ['daily'])
)

// 监听频率选择变化，同时更新 frequency 和 frequencies
watch(selectedFrequencies, (newFrequencies) => {
  localParams.value.frequencies = [...newFrequencies]
  // 保持向后兼容，如果只选了一个频率，同步到 frequency 字段
  if (newFrequencies.length === 1) {
    localParams.value.frequency = newFrequencies[0]
  } else if (newFrequencies.length === 0) {
    // 如果没有选择任何频率，默认选择日线
    localParams.value.frequency = 'daily'
    localParams.value.frequencies = ['daily']
    selectedFrequencies.value = ['daily']
    ElMessage.warning('请至少选择一个数据频率')
  }
}, { deep: true })

// 组件挂载时，从同步服务获取上游节点的频率配置
onMounted(() => {
  // 从同步状态获取合并后的频率（股票选择和指数选择的并集）
  const syncedFreqs = timeRangeSyncState.syncedFrequencies || []

  if (syncedFreqs.length > 0) {
    // 使用同步服务的频率更新本地配置
    console.log('[数据清洗节点] 从同步服务获取频率:', syncedFreqs)

    // 更新本地参数
    localParams.value.frequencies = [...syncedFreqs]
    if (syncedFreqs.length === 1) {
      localParams.value.frequency = syncedFreqs[0]
    } else {
      localParams.value.frequency = syncedFreqs[0] // 使用第一个作为主频率
    }

    // 更新UI选择的频率
    selectedFrequencies.value = [...syncedFreqs]

    // 关键修复：手动触发参数更新，确保父组件接收到变化
    emit('update:params', { ...localParams.value })

    ElMessage.info(`已从上游节点同步频率配置: ${syncedFreqs.join(', ')}`)
  }
})

// 模式描述
const modeDescription = computed(() => {
  return localParams.value.mode === 'cleaning'
    ? '清洗原始股票数据并转换为 QLib 格式'
    : '查看和管理已清洗的数据库，支持数据更新和维护'
})

// 转换状态（仅清洗模式）
const conversionStatus = computed(() => {
  if (localParams.value.mode !== 'cleaning') return null
  return props.data?.content?.conversionStatus
})

const conversionData = computed(() => {
  if (localParams.value.mode !== 'cleaning') return null
  return props.data?.content
})

const statusType = computed(() => {
  switch (conversionStatus.value) {
    case 'completed': return 'success'
    case 'converting': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
})

const statusText = computed(() => {
  switch (conversionStatus.value) {
    case 'completed': return '转换完成'
    case 'converting': return '转换中...'
    case 'failed': return '转换失败'
    case 'pending': return '待转换'
    default: return '未开始'
  }
})

// 监听参数变化
watch(localParams, (newParams) => {
  emit('update:params', { ...newParams })
}, { deep: true })

// 模式切换处理
const onModeChange = (mode: string) => {
  ElMessage.info(`已切换到${mode === 'cleaning' ? '数据清洗' : '数据库管理'}模式`)
}

// 选择目录
const selectDirectory = () => {
  ElMessage.info('请手动输入目录路径')
}
</script>

<style scoped>
.data-management-config {
  padding: 8px;
}

.mode-section {
  margin-bottom: 8px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin: 12px 0 8px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #e5e7eb;
}

.form-tip {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
  line-height: 1.4;
}

.conversion-status {
  margin-top: 16px;
}

.status-header {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.detail-label {
  color: #6b7280;
}

.detail-value {
  color: #374151;
  font-weight: 500;
}

/* 频率选择复选框样式 */
.frequency-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  user-select: none;
}

.checkbox-option:hover {
  background-color: rgba(37, 99, 235, 0.05);
}

.checkbox-option input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #2563eb;
}

.checkbox-option span {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
}

.checkbox-option small {
  font-size: 11px;
  color: #6b7280;
  margin-left: 4px;
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .section-title {
    color: #e5e7eb;
    border-bottom-color: #374151;
  }

  .form-tip {
    color: #6b7280;
  }

  .status-header {
    color: #e5e7eb;
  }

  .detail-label {
    color: #9ca3af;
  }

  .detail-value {
    color: #e5e7eb;
  }
}
</style>
