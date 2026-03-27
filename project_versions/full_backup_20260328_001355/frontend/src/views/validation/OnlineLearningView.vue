<template>
  <div class="online-learning-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">📚 在线滚动训练</h1>
        <p class="page-subtitle">基于最新数据实时优化模型</p>
      </div>
      <div class="header-right">
        <el-button @click="handleBack">返回</el-button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <el-row :gutter="16">
      <!-- 左侧：训练控制 -->
      <el-col :span="8">
        <TrainingControlPanel />
      </el-col>

      <!-- 右侧：训练详情 -->
      <el-col :span="16">
        <el-tabs v-model="activeTab" class="training-tabs">
          <el-tab-pane label="训练进度" name="progress">
            <LearningProgressPanel :model-id="currentModelId" />
          </el-tab-pane>

          <el-tab-pane label="模型版本" name="versions">
            <ModelVersionCard :model-id="currentModelId" />
          </el-tab-pane>

          <el-tab-pane label="性能对比" name="comparison">
            <PerformanceComparisonPanel :model-id="currentModelId" />
          </el-tab-pane>

          <el-tab-pane label="交易信号" name="signals">
            <TradingSignalsPanel :model-id="currentModelId" />
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import TrainingControlPanel from '@/components/validation/learning/TrainingControlPanel.vue'
import LearningProgressPanel from '@/components/validation/learning/LearningProgressPanel.vue'
import ModelVersionCard from '@/components/validation/learning/ModelVersionCard.vue'
import PerformanceComparisonPanel from '@/components/validation/learning/PerformanceComparisonPanel.vue'
import TradingSignalsPanel from '@/components/validation/learning/TradingSignalsPanel.vue'

const router = useRouter()
const activeTab = ref('progress')

// 当前模型ID（实际应该从路由参数或状态管理中获取）
const currentModelId = ref('model_topk_dropout_v2')

const handleBack = () => {
  router.back()
}
</script>

<style scoped lang="scss">
.online-learning-view {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .header-left {
      .page-title {
        font-size: 28px;
        font-weight: 600;
        color: #303133;
        margin: 0 0 8px 0;
      }

      .page-subtitle {
        font-size: 14px;
        color: #909399;
        margin: 0;
      }
    }
  }

  .training-tabs {
    :deep(.el-tabs__content) {
      padding-top: 16px;
    }

    .placeholder-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 20px;
      background-color: #f5f7fa;
      border-radius: 8px;
      min-height: 400px;

      .placeholder-text {
        margin-top: 16px;
        font-size: 16px;
        color: #909399;
      }
    }
  }
}
</style>
