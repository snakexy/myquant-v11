<template>
  <div class="feature-engineering-config">
    <el-form label-position="top" size="small">
      <!-- 特征选择方法 -->
      <el-form-item label="特征选择方法">
        <el-select v-model="localParams.selectionMethod" style="width: 100%">
          <el-option label="方差阈值" value="variance-threshold" />
          <el-option label="K个最佳特征" value="k-best" />
          <el-option label="递归特征消除" value="recursive" />
          <el-option label="特征重要性" value="importance" />
        </el-select>
        <div class="form-tip">选择特征筛选的方法</div>
      </el-form-item>

      <!-- 保留特征数量 -->
      <el-form-item
        label="保留特征数量"
        v-if="localParams.selectionMethod === 'k-best' || localParams.selectionMethod === 'importance'"
      >
        <el-input-number
          v-model="localParams.kBest"
          :min="1"
          :max="1000"
          :step="10"
          style="width: 100%"
        />
        <div class="form-tip">当使用K个最佳特征方法时，保留的特征数量</div>
      </el-form-item>

      <!-- 特征转换 -->
      <div class="section-title">特征转换</div>

      <el-form-item label="特征转换方法">
        <el-select v-model="localParams.transformation" style="width: 100%">
          <el-option label="不转换" value="none" />
          <el-option label="PCA降维" value="pca" />
          <el-option label="标准化" value="standardization" />
          <el-option label="归一化" value="normalization" />
        </el-select>
      </el-form-item>

      <!-- PCA主成分数量 -->
      <el-form-item
        label="PCA主成分数量"
        v-if="localParams.transformation === 'pca'"
      >
        <el-input-number
          v-model="localParams.pcaComponents"
          :min="1"
          :max="100"
          style="width: 100%"
        />
        <div class="form-tip">PCA降维后保留的主成分数量</div>
      </el-form-item>

      <!-- 相关性过滤 -->
      <div class="section-title">相关性过滤</div>

      <el-form-item>
        <el-checkbox v-model="localParams.removeCorrelated">
          移除高度相关特征
        </el-checkbox>
        <div class="form-tip">自动移除相关性过高的特征以减少冗余</div>
      </el-form-item>

      <el-form-item
        label="相关性阈值"
        v-if="localParams.removeCorrelated"
      >
        <el-slider
          v-model="localParams.correlationThreshold"
          :min="0.8"
          :max="0.99"
          :step="0.01"
          :format-tooltip="(v) => v.toFixed(2)"
        />
        <div class="form-tip">特征相关性的阈值（0-1之间）</div>
      </el-form-item>
    </el-form>

    <!-- 处理状态显示 -->
    <div class="processing-status" v-if="processingStatus">
      <el-divider />
      <div class="status-header">特征工程状态</div>
      <div class="status-content">
        <el-tag :type="statusType" size="large">
          {{ statusText }}
        </el-tag>
        <div v-if="processingData" class="status-details">
          <div class="detail-item">
            <span class="detail-label">原始特征:</span>
            <span class="detail-value">{{ processingData.originalFeatures }} 个</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">最终特征:</span>
            <span class="detail-value">{{ processingData.finalFeatures }} 个</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">选择比例:</span>
            <span class="detail-value">{{ processingData.selectionRatio }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  params: Record<string, any>
  data?: any
}

interface Emits {
  (e: 'update:params', value: Record<string, any>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 本地参数副本
const localParams = ref<Record<string, any>>({
  selectionMethod: 'variance-threshold',
  kBest: 50,
  transformation: 'none',
  pcaComponents: 10,
  removeCorrelated: false,
  correlationThreshold: 0.95,
  ...props.params
})

// 处理状态
const processingStatus = computed(() => props.data?.content?.status)
const processingData = computed(() => props.data?.content)

const statusType = computed(() => {
  switch (processingStatus.value) {
    case 'completed': return 'success'
    case 'processing': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
})

const statusText = computed(() => {
  switch (processingStatus.value) {
    case 'completed': return '处理完成'
    case 'processing': return '处理中...'
    case 'failed': return '处理失败'
    case 'pending': return '待处理'
    default: return '未开始'
  }
})

// 监听参数变化
watch(localParams, (newParams) => {
  emit('update:params', { ...newParams })
}, { deep: true })
</script>

<style scoped>
.feature-engineering-config {
  padding: 8px;
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

.processing-status {
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
</style>
