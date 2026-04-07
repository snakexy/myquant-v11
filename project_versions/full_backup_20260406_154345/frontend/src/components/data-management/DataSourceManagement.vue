<template>
  <section class="data-sources-section">
    <div class="section-header">
      <h2>数据源管理</h2>
      <p>配置和监控各个数据源状态</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="sources-list">
      <div
        v-for="source in sources"
        :key="source.id"
        class="source-item"
        :class="{ disabled: !source.enabled }"
      >
        <div class="source-icon">
          <i :class="getSourceIcon(source.type)"></i>
        </div>

        <div class="source-info">
          <div class="source-header">
            <h3>{{ source.name }}</h3>
            <div class="source-status" :class="source.status">
              <span class="status-dot"></span>
              <span class="status-text">{{ source.statusText }}</span>
            </div>
          </div>

          <p class="source-description">{{ source.description }}</p>

          <div class="source-metrics">
            <div class="metric">
              <span class="metric-label">更新频率:</span>
              <span class="metric-value">{{ source.updateFreq }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">错误数:</span>
              <span class="metric-value" :class="{ error: source.errorCount > 0 }">
                {{ source.errorCount }}
              </span>
            </div>
            <div class="metric">
              <span class="metric-label">最后更新:</span>
              <span class="metric-value">{{ formatTime(source.lastUpdate) }}</span>
            </div>
          </div>
        </div>

        <div class="source-actions">
          <button
            class="action-btn toggle-btn"
            :class="{ active: source.enabled }"
            @click="toggleSource(source.id)"
          >
            <i :class="source.enabled ? 'fas fa-toggle-on' : 'fas fa-toggle-off'"></i>
            {{ source.enabled ? '已启用' : '已禁用' }}
          </button>

          <button class="action-btn" @click="testConnection(source.id)">
            <i class="fas fa-plug"></i>
            测试连接
          </button>

          <button class="action-btn" @click="configureSource(source.id)">
            <i class="fas fa-cog"></i>
            配置
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface DataSource {
  id: string
  name: string
  type: 'local' | 'remote' | 'cache' | 'database'
  status: 'active' | 'inactive' | 'error'
  statusText: string
  enabled: boolean
  description: string
  updateFreq: string
  errorCount: number
  lastUpdate: string
}

const loading = ref(true)
const sources = ref<DataSource[]>([])

const loadData = async () => {
  loading.value = true

  try {
    const response = await fetch('/api/v1/data-management/sources/list')
    const result = await response.json()

    if (result.success && result.data) {
      sources.value = result.data.map((s: any) => ({
        id: s.id,
        name: s.name,
        type: s.type,
        status: s.status,
        statusText: s.status === 'active' ? '正常' : s.status === 'error' ? '错误' : '未激活',
        enabled: s.enabled,
        description: s.description,
        updateFreq: s.updateFreq,
        errorCount: s.errorCount || 0,
        lastUpdate: s.lastUpdate
      }))
    }
  } catch (error) {
    console.error('加载数据源失败:', error)
    // 使用默认数据
    sources.value = [
      {
        id: 'smart-cache',
        name: '智能缓存系统',
        type: 'cache',
        status: 'active',
        statusText: '正常',
        enabled: true,
        description: 'L1内存缓存 + L2 Redis缓存 + L3本地文件缓存',
        updateFreq: '实时',
        errorCount: 0,
        lastUpdate: new Date().toISOString()
      },
      {
        id: 'local-tdx',
        name: '通达信本地数据',
        type: 'local',
        status: 'active',
        statusText: '正常',
        enabled: true,
        description: '从本地通达信VIP文档读取数据',
        updateFreq: '每日收盘后',
        errorCount: 0,
        lastUpdate: new Date().toISOString()
      },
      {
        id: 'remote-tdx',
        name: '通达信远程数据',
        type: 'remote',
        status: 'active',
        statusText: '正常',
        enabled: true,
        description: '从通达信服务器获取实时行情',
        updateFreq: '实时(3秒)',
        errorCount: 1,
        lastUpdate: new Date().toISOString()
      },
      {
        id: 'qlib',
        name: 'Qlib数据库',
        type: 'database',
        status: 'inactive',
        statusText: '未激活',
        enabled: false,
        description: '量化数据存储格式',
        updateFreq: '每日',
        errorCount: 0,
        lastUpdate: new Date().toISOString()
      }
    ]
  } finally {
    loading.value = false
  }
}

const getSourceIcon = (type: string) => {
  const icons: Record<string, string> = {
    local: 'fas fa-database',
    remote: 'fas fa-cloud',
    cache: 'fas fa-bolt',
    database: 'fas fa-server'
  }
  return icons[type] || 'fas fa-cog'
}

const formatTime = (timeStr: string) => {
  const time = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - time.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

const toggleSource = async (id: string) => {
  const source = sources.value.find(s => s.id === id)
  if (source) {
    source.enabled = !source.enabled
    // TODO: 调用API更新状态
  }
}

const testConnection = async (id: string) => {
  console.log('测试连接:', id)
  // TODO: 调用API测试连接
}

const configureSource = (id: string) => {
  console.log('配置数据源:', id)
  // TODO: 打开配置对话框
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.data-sources-section {
  margin-bottom: 32px;
}

.section-header {
  margin-bottom: 24px;

  h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  p {
    font-size: 14px;
    color: var(--text-secondary);
  }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: var(--card-bg);
  border-radius: 12px;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.source-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--primary-color);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }

  &.disabled {
    opacity: 0.6;
  }
}

.source-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border-radius: 10px;
  font-size: 24px;
  color: var(--primary-color);
}

.source-info {
  flex: 1;
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.source-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  &.active {
    color: #10b981;

    .status-dot {
      background: #10b981;
      box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
    }
  }

  &.inactive {
    color: var(--text-secondary);

    .status-dot {
      background: var(--text-secondary);
    }
  }

  &.error {
    color: #ef4444;

    .status-dot {
      background: #ef4444;
      box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
    }
  }
}

.source-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.source-metrics {
  display: flex;
  gap: 20px;
}

.metric {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;

  .metric-label {
    color: var(--text-secondary);
  }

  .metric-value {
    color: var(--text-primary);
    font-weight: 500;

    &.error {
      color: #ef4444;
    }
  }
}

.source-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;

  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary-color);
  }

  i {
    margin-right: 4px;
  }

  &.toggle-btn {
    &.active {
      background: rgba(16, 185, 129, 0.1);
      border-color: #10b981;
      color: #10b981;
    }
  }
}

@media (max-width: 768px) {
  .source-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .source-actions {
    width: 100%;
    justify-content: stretch;

    button {
      flex: 1;
    }
  }

  .source-metrics {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
