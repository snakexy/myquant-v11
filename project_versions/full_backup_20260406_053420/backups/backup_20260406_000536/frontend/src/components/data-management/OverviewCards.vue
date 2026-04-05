<template>
  <section class="overview-section">
    <div class="section-header">
      <h2>数据概览</h2>
      <p>实时监控系统数据状态和性能指标</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="cards-grid">
      <div
        v-for="card in cards"
        :key="card.id"
        class="overview-card"
      >
        <div class="card-content">
          <div class="card-header">
            <div class="card-icon">
              <i :class="card.icon"></i>
            </div>
            <div class="card-info">
              <h3>{{ card.title }}</h3>
              <p class="card-value">{{ card.value }}</p>
            </div>
          </div>

          <div class="card-change" :class="card.changeType">
            <i :class="getChangeIcon(card.changeType)"></i>
            <span>{{ card.change }}</span>
          </div>

          <!-- 总数据量卡片：显示数据库详细信息 -->
          <div v-if="card.id === 0 && databaseDetails.length > 0" class="card-source-names">
            <div class="source-names-label">数据库详情</div>
            <div class="source-names-list">
              <div
                v-for="detail in databaseDetails"
                :key="detail.name"
                class="source-name-item"
              >
                <span class="source-status-dot" :style="{ '--status-color': getStatusColor(detail.status) }"></span>
                <div class="database-detail-info">
                  <div class="source-name-text">{{ detail.name }}</div>
                  <div class="database-detail-meta">
                    <span>{{ detail.size }}</span>
                    <span v-if="detail.stockCount !== undefined && detail.stockCount !== null">{{ detail.stockCount }}只股票</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 活跃数据源卡片：显示具体数据源名称 -->
          <div v-if="card.id === 2 && activeSourceItems.length > 0" class="card-source-names">
            <div class="source-names-label">活跃数据源</div>
            <div class="source-names-list">
              <div
                v-for="source in activeSourceItems"
                :key="source.id"
                class="source-name-item"
              >
                <span class="source-status-dot"></span>
                <span class="source-name-text">{{ source.name }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card-progress">
          <div class="progress-bar" :style="{ width: card.progress + '%' }"></div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Card {
  id: number
  title: string
  value: string
  change: string
  changeType: 'up' | 'down' | 'stable'
  progress: number
  icon: string
}

interface DatabaseDetail {
  name: string
  size: string
  stockCount: number
  status: string
}

const loading = ref(true)
const cards = ref<Card[]>([])
const databaseDetails = ref<DatabaseDetail[]>([])
const activeSourceItems = ref<any[]>([])

const loadData = async () => {
  loading.value = true

  try {
    // 加载数据库统计
    const statsResponse = await fetch('/api/v1/data-management/database/stats')
    const statsResult = await statsResponse.json()

    if (statsResult.success && statsResult.data) {
      const stats = statsResult.data

      // 更新卡片数据
      cards.value = [
        {
          id: 0,
          title: '总数据量',
          value: stats.dataSize || '加载中...',
          change: '+1.2%',
          changeType: 'up',
          progress: 85,
          icon: 'fas fa-database'
        },
        {
          id: 1,
          title: '数据完整度',
          value: '96.8%',
          change: '+2.1%',
          changeType: 'up',
          progress: 97,
          icon: 'fas fa-check-circle'
        },
        {
          id: 2,
          title: '活跃数据源',
          value: '3',
          change: '+3',
          changeType: 'stable',
          progress: 75,
          icon: 'fas fa-plug'
        },
        {
          id: 3,
          title: '今日更新',
          value: '2小时前',
          change: '+1.2%',
          changeType: 'up',
          progress: 92,
          icon: 'fas fa-clock'
        }
      ]

      // 更新数据库详情
      if (stats.tableStats && stats.tableStats.length > 0) {
        databaseDetails.value = stats.tableStats.slice(0, 2).map((table: any) => {
          let status = 'inactive'
          if (table.details?.status) {
            status = table.details.status
          } else if (table.details?.stockCount > 0 || table.recordCount > 0) {
            status = 'active'
          }

          return {
            name: table.name,
            size: table.size,
            stockCount: table.details?.stockCount || table.recordCount,
            status: status
          }
        })
      }
    }

    // 加载数据源列表
    const sourcesResponse = await fetch('/api/v1/data-management/sources/list')
    const sourcesResult = await sourcesResponse.json()

    if (sourcesResult.success && sourcesResult.data) {
      activeSourceItems.value = sourcesResult.data
        .filter((s: any) => s.status === 'active' && s.enabled)
        .slice(0, 4)
    }
  } catch (error) {
    console.error('加载概览数据失败:', error)
    // 使用默认数据
    cards.value = [
      {
        id: 0,
        title: '总数据量',
        value: '3.11GB',
        change: '+1.2%',
        changeType: 'up',
        progress: 85,
        icon: 'fas fa-database'
      },
      {
        id: 1,
        title: '数据完整度',
        value: '96.8%',
        change: '+2.1%',
        changeType: 'up',
        progress: 97,
        icon: 'fas fa-check-circle'
      },
      {
        id: 2,
        title: '活跃数据源',
        value: '3',
        change: '+3',
        changeType: 'stable',
        progress: 75,
        icon: 'fas fa-plug'
      },
      {
        id: 3,
        title: '今日更新',
        value: '2小时前',
        change: '+1.2%',
        changeType: 'up',
        progress: 92,
        icon: 'fas fa-clock'
      }
    ]
  } finally {
    loading.value = false
  }
}

const getChangeIcon = (type: string) => {
  const icons: Record<string, string> = {
    up: 'fas fa-arrow-up',
    down: 'fas fa-arrow-down',
    stable: 'fas fa-minus'
  }
  return icons[type] || 'fas fa-minus'
}

const getStatusColor = (status: string) => {
  if (status === 'not_converted' || status === 'inactive' || status === '未转换') {
    return 'rgba(255, 193, 7, 0.8)' // 黄色 - 未转换
  }
  if (status === 'ready' || status === 'active' || status === '已就绪') {
    return 'rgba(76, 175, 80, 0.8)' // 绿色 - 已就绪
  }
  return 'rgba(255, 255, 255, 0.5)' // 默认灰色
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.overview-section {
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

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.overview-card {
  position: relative;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  color: var(--text-primary);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    border-color: var(--primary-color);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary-color), var(--primary-color));
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover::before {
    opacity: 1;
  }
}

.card-content {
  position: relative;
  z-index: 1;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-color));
  border-radius: 12px;
  font-size: 24px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-info {
  flex: 1;
  margin-left: 12px;
}

.card-info h3 {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 8px;
}

.card-change {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;

  &.up {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444; // 红色表示上涨
  }

  &.down {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981; // 绿色表示下跌
  }

  &.stable {
    background: rgba(156, 163, 175, 0.1);
    color: #9ca3af;
  }
}

.card-source-names {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.source-names-label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.source-names-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.source-name-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 3px 0;
}

.source-status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  background-color: var(--status-color, #10b981);
  box-shadow: 0 0 8px currentColor;
}

.database-detail-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.source-name-text {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
  line-height: 1.2;
}

.database-detail-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 400;
}

.card-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(0, 0, 0, 0.05);
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--primary-color));
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: shimmer 2s infinite;
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }

  .card-value {
    font-size: 28px;
  }
}
</style>
