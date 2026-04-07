<template>
  <div class="tdx-path-config">
    <el-tooltip content="配置通达信数据源" placement="top">
      <el-button
        size="small"
        @click="dialogVisible = true"
        class="config-icon-btn"
        circle
      >
        <font-awesome-icon icon="cog" />
      </el-button>
    </el-tooltip>

    <!-- 配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="通达信数据源配置"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="config-dialog-content">
        <div class="path-display">
          <div class="path-info">
            <div class="path-label">
              <font-awesome-icon icon="database" />
              当前数据目录
            </div>
            <div class="path-value">
              {{ tdxPath || '未检测到通达信安装路径' }}
            </div>
          </div>
        </div>
        <div class="form-tip">
          系统会自动检测通达信安装目录，如需手动设置请点击下方按钮
        </div>
        <el-button
          type="primary"
          @click="$emit('select-path')"
          class="config-btn"
          style="width: 100%; margin-top: 16px;"
        >
          <font-awesome-icon icon="folder-open" />
          浏览并设置通达信目录
        </el-button>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  tdxPath: string
}

defineProps<Props>()

defineEmits<{
  'update:tdxPath': [value: string]
  'select-path': []
}>()

const dialogVisible = ref(false)
</script>

<style scoped>
.tdx-path-config {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}

.config-icon-btn {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
}

.config-icon-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
  color: #2962ff;
  transform: rotate(90deg);
}

.config-dialog-content {
  padding: 8px 0;
}

.path-display {
  display: flex;
  align-items: center;
  padding: 16px;
  background: rgba(26, 26, 46, 0.8);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 16px;
}

.path-info {
  flex: 1;
  min-width: 0;
}

.path-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
  font-weight: 500;
}

.path-value {
  font-size: 14px;
  color: #10b981;
  font-family: 'Consolas', 'Monaco', monospace;
  font-weight: 600;
  word-break: break-all;
}

.form-tip {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
  text-align: center;
  line-height: 1.5;
}

/* 对话框样式适配 */
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

/* 统一按钮风格 */
:deep(.el-button) {
  border-radius: 20px;
}

:deep(.el-button--primary) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

:deep(.el-button--primary:hover:not(:disabled)) {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-button--primary:active:not(:disabled)) {
  background: linear-gradient(135deg, #5568d3 0%, #643a8b 100%);
  border-color: transparent;
  color: white;
}
</style>
