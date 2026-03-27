<template>
  <div class="alert-system-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">📋 智能预警系统</h1>
        <p class="page-subtitle">基于阈值和条件的自定义预警规则</p>
      </div>
      <div class="header-right">
        <el-button @click="handleBack">返回</el-button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <el-row :gutter="16">
      <!-- 左侧：规则管理 -->
      <el-col :span="12">
        <AlertRuleManager />
      </el-col>

      <!-- 右侧：预警历史 -->
      <el-col :span="12">
        <AlertHistoryPanel />
      </el-col>
    </el-row>

    <!-- 通知配置 -->
    <el-row style="margin-top: 16px">
      <el-col :span="24">
        <NotificationConfig />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import AlertRuleManager from '@/components/validation/alerts/AlertRuleManager.vue'
import AlertHistoryPanel from '@/components/validation/alerts/AlertHistoryPanel.vue'
import NotificationConfig from '@/components/validation/alerts/NotificationConfig.vue'

const router = useRouter()

const handleBack = () => {
  router.back()
}
</script>

<style scoped lang="scss">
.alert-system-view {
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

    .header-right {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }
}
</style>
