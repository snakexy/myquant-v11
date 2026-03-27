<!-- 步骤3：因子分析容器组件 -->
<template>
  <div class="step-factor-analysis-panel">
    <!-- Tabs 导航 -->
    <div class="content-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['content-tab', { active: currentTab === tab.id }]"
        @click="switchTab(tab.id)"
      >
        <svg v-if="tab.id === 'overview'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="14" y="3" width="7" height="7"></rect>
          <rect x="14" y="14" width="7" height="7"></rect>
          <rect x="3" y="14" width="7" height="7"></rect>
        </svg>
        <svg v-else-if="tab.id === 'ic-ir'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
          <polyline points="17 6 23 6 23 12"></polyline>
        </svg>
        <svg v-else-if="tab.id === 'correlation'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="2"></circle>
          <path d="M16.24 7.76a6 6 0 010 8.49m-8.48-.01a6 6 0 010-8.49m11.31-2.82a10 10 0 010 14.14m-14.14 0a10 10 0 010-14.14"></path>
        </svg>
        <svg v-else-if="tab.id === 'distribution'" class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
        <svg v-else class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
        </svg>
        {{ isZh ? tab.nameZh : tab.name }}
      </button>
    </div>

    <!-- Tab 内容区域 -->
    <div class="tab-content">
      <!-- 概览 Tab - 将在 Task 7 中实现 -->
      <div v-if="currentTab === 'overview'" class="tab-pane active">
        <!-- FactorAnalysisOverview 组件占位符 -->
        <div class="placeholder-content">
          <p>{{ isZh ? '因子库概览' : 'Factor Library Overview' }}</p>
          <p class="placeholder-hint">{{ isZh ? '（子组件将在 Task 7-10 中实现）' : '(Child components will be implemented in Tasks 7-10)' }}</p>
        </div>
      </div>

      <!-- IC/IR 分析 Tab - 将在 Task 8 中实现 -->
      <div v-else-if="currentTab === 'ic-ir'" class="tab-pane active">
        <!-- FactorAnalysisICIR 组件占位符 -->
        <div class="placeholder-content">
          <p>{{ isZh ? 'IC/IR 分析' : 'IC/IR Analysis' }}</p>
          <p class="placeholder-hint">{{ isZh ? '（子组件将在 Task 7-10 中实现）' : '(Child components will be implemented in Tasks 7-10)' }}</p>
        </div>
      </div>

      <!-- 相关性 Tab - 将在 Task 9 中实现 -->
      <div v-else-if="currentTab === 'correlation'" class="tab-pane active">
        <!-- FactorAnalysisCorrelation 组件占位符 -->
        <div class="placeholder-content">
          <p>{{ isZh ? '因子相关性分析' : 'Factor Correlation Analysis' }}</p>
          <p class="placeholder-hint">{{ isZh ? '（子组件将在 Task 7-10 中实现）' : '(Child components will be implemented in Tasks 7-10)' }}</p>
        </div>
      </div>

      <!-- 分布 Tab - 将在 Task 10 中实现 -->
      <div v-else-if="currentTab === 'distribution'" class="tab-pane active">
        <!-- FactorAnalysisDistribution 组件占位符 -->
        <div class="placeholder-content">
          <p>{{ isZh ? '因子分布分析' : 'Factor Distribution Analysis' }}</p>
          <p class="placeholder-hint">{{ isZh ? '（子组件将在 Task 7-10 中实现）' : '(Child components will be implemented in Tasks 7-10)' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

/**
 * 步骤3：因子分析容器组件
 *
 * 功能：
 * - 提供 Tab 导航（概览、IC/IR分析、相关性、分布）
 * - 管理当前活动 Tab 状态
 * - 为子组件提供容器
 *
 * 注意：子组件（FactorAnalysisOverview、FactorAnalysisICIR 等）
 * 将在后续 Task 7-10 中实现
 */

interface TabItem {
  id: string
  name: string
  nameZh: string
}

interface Props {
  taskId?: string
  isZh?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  taskId: '',
  isZh: true
})

// Tab 定义
const tabs = ref<TabItem[]>([
  { id: 'overview', name: 'Overview', nameZh: '概览' },
  { id: 'ic-ir', name: 'IC/IR Analysis', nameZh: 'IC/IR分析' },
  { id: 'correlation', name: 'Correlation', nameZh: '相关性' },
  { id: 'distribution', name: 'Distribution', nameZh: '分布' }
])

// 当前活动 Tab
const currentTab = ref<string>('overview')

/**
 * 切换 Tab
 * @param tabId - Tab ID
 */
const switchTab = (tabId: string) => {
  currentTab.value = tabId
}
</script>

<style scoped lang="scss">
.step-factor-analysis-panel {
  width: 100%;
  height: 100%;
}

/* Tabs 导航 */
.content-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.content-tab {
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary, #6b7280);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 6px;

  &:hover {
    color: var(--text-primary, #1f2937);
    background: var(--bg-secondary-hover, #f3f4f6);
  }

  &.active {
    color: var(--color-primary, #3b82f6);
    border-bottom-color: var(--color-primary, #3b82f6);
  }
}

.tab-icon {
  width: 16px;
  height: 16px;
}

/* Tab 内容区域 */
.tab-content {
  flex: 1;
  overflow: auto;
}

.tab-pane {
  &.active {
    display: block;
  }
}

/* 占位符样式（临时，子组件实现后将移除） */
.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary, #6b7280);

  p {
    font-size: 16px;
    font-weight: 500;
    margin: 0 0 8px 0;
  }

  .placeholder-hint {
    font-size: 14px;
    color: var(--text-tertiary, #9ca3af);
    font-style: italic;
  }
}
</style>
