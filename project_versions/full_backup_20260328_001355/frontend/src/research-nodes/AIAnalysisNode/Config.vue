<template>
  <div class="ai-analysis-config">
    <el-form label-position="top" size="small">
      <!-- 分析类型 -->
      <el-form-item label="分析类型">
        <el-select v-model="localParams.analysisType" style="width: 100%">
          <el-option label="市场趋势分析" value="market-trend" />
          <el-option label="个股分析" value="individual-stock" />
          <el-option label="组合分析" value="portfolio" />
        </el-select>
        <div class="form-tip">选择分析的对象类型</div>
      </el-form-item>

      <!-- 分析深度 -->
      <el-form-item label="分析深度">
        <el-radio-group v-model="localParams.depth">
          <el-radio value="basic">基础</el-radio>
          <el-radio value="standard">标准</el-radio>
          <el-radio value="comprehensive">综合</el-radio>
        </el-radio-group>
        <div class="form-tip">选择分析的详细程度</div>
      </el-form-item>

      <!-- 输出格式 -->
      <el-form-item label="输出格式">
        <el-select v-model="localParams.outputFormat" style="width: 100%">
          <el-option label="摘要" value="summary" />
          <el-option label="详细" value="detailed" />
          <el-option label="报告" value="report" />
        </el-select>
      </el-form-item>

      <!-- 其他选项 -->
      <div class="section-title">其他选项</div>

      <el-form-item>
        <el-checkbox v-model="localParams.includeCharts">
          包含图表
        </el-checkbox>
        <div class="form-tip">生成图表分析</div>
      </el-form-item>

      <el-form-item>
        <el-checkbox v-model="localParams.includeRisk">
          包含风险评估
        </el-checkbox>
        <div class="form-tip">包含风险评估结果</div>
      </el-form-item>
    </el-form>

    <!-- 分析状态显示 -->
    <div class="analysis-status" v-if="analysisData">
      <el-divider />
      <div class="status-header">分析结果</div>
      <div class="status-content">
        <el-tag type="success" size="large">分析完成</el-tag>
        <div class="analysis-summary">
          {{ analysisData.summary || 'AI分析已完成' }}
        </div>
        <div v-if="analysisData.risk_assessment" class="risk-assessment">
          <div class="risk-label">风险评估:</div>
          <div class="risk-value">{{ analysisData.risk_assessment.level || '--' }}</div>
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
  analysisType: 'market-trend',
  depth: 'standard',
  outputFormat: 'detailed',
  includeCharts: true,
  includeRisk: true,
  ...props.params
})

// 分析数据
const analysisData = computed(() => props.data?.data)

// 监听参数变化
watch(localParams, (newParams) => {
  emit('update:params', { ...newParams })
}, { deep: true })
</script>

<style scoped>
.ai-analysis-config {
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

.analysis-status {
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

.analysis-summary {
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
  padding: 8px;
  background: #f9fafb;
  border-radius: 4px;
}

.risk-assessment {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding: 6px 8px;
  background: #fef3c7;
  border-radius: 4px;
}

.risk-label {
  color: #92400e;
  font-weight: 500;
}

.risk-value {
  color: #78350f;
  font-weight: 600;
}
</style>
