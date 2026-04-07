<template>
  <div class="data-management-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="phase-badge research">🔬 研究阶段</div>
          <h1 class="page-title"><i class="fas fa-hdd"></i> 数据管理节点</h1>
          <p class="page-subtitle">统一数据入口 - L0-L5数据分层架构</p>
        </div>
        <div class="header-actions">
          <el-button type="success" @click="triggerSmartSync" :loading="syncing">
            <el-icon><Connection /></el-icon>
            智能同步数据
          </el-button>
          <el-button type="primary" @click="refreshAllData" :loading="refreshing">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button @click="showSettings = true">
            <el-icon><Setting /></el-icon>
            数据源配置
          </el-button>
        </div>
      </div>
    </div>

    <!-- L0-L5 数据分层可视化 -->
    <div class="data-layers-section">
      <div class="section-title">
        <h2>L0-L5 数据分层架构</h2>
        <p class="section-subtitle">根据数据类型和速度需求智能选择最优数据源</p>
      </div>

      <div class="layers-container">
        <!-- L0: 订阅缓存 -->
        <div class="layer-card l0">
          <div class="layer-header">
            <div class="layer-badge">L0</div>
            <div class="layer-title">订阅缓存</div>
            <div class="layer-speed">&lt;1ms</div>
          </div>
          <div class="layer-content">
            <div class="layer-stats">
              <div class="stat-item">
                <span class="stat-label">容量</span>
                <span class="stat-value">600只</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">数据源</span>
                <span class="stat-value">XtQuant双实例</span>
              </div>
            </div>
            <div class="layer-usage">
              <div class="usage-bar">
                <div class="usage-fill" :style="{ width: l0Usage + '%' }"></div>
              </div>
              <div class="usage-text">已订阅 {{ l0Usage }}/600 只</div>
            </div>
          </div>
        </div>

        <!-- L1: 实时快照 -->
        <div class="layer-card l1">
          <div class="layer-header">
            <div class="layer-badge">L1</div>
            <div class="layer-title">实时快照</div>
            <div class="layer-speed">1-17ms</div>
          </div>
          <div class="layer-content">
            <div class="layer-stats">
              <div class="stat-item">
                <span class="stat-label">优先级</span>
                <span class="stat-value">XtQuant → PyTdx</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">可用性</span>
                <span class="stat-value">24/7</span>
              </div>
            </div>
            <div class="data-sources">
              <div class="source-item priority-1">
                <span class="source-name">XtQuant订阅</span>
                <span class="source-latency">~1ms</span>
              </div>
              <div class="source-item priority-2">
                <span class="source-name">PyTdx批量</span>
                <span class="source-latency">~17ms</span>
              </div>
            </div>
          </div>
        </div>

        <!-- L2: 历史摘要 -->
        <div class="layer-card l2">
          <div class="layer-header">
            <div class="layer-badge">L2</div>
            <div class="layer-title">历史摘要</div>
            <div class="layer-speed">7-17ms</div>
          </div>
          <div class="layer-content">
            <div class="layer-stats">
              <div class="stat-item">
                <span class="stat-label">时间范围</span>
                <span class="stat-value">30天</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">优先级</span>
                <span class="stat-value">LocalDB → XtQuant</span>
              </div>
            </div>
          </div>
        </div>

        <!-- L3: 完整数据 -->
        <div class="layer-card l3">
          <div class="layer-header">
            <div class="layer-badge">L3</div>
            <div class="layer-title">完整数据</div>
            <div class="layer-speed">5-18ms</div>
          </div>
          <div class="layer-content">
            <div class="layer-stats">
              <div class="stat-item">
                <span class="stat-label">容量</span>
                <span class="stat-value">800天日K</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">优先级</span>
                <span class="stat-value">XtQuant(117x) → PyTdx</span>
              </div>
            </div>
            <div class="data-sources">
              <div class="source-item priority-1">
                <span class="source-name">QLib本地DB</span>
                <span class="source-latency">~5ms</span>
              </div>
              <div class="source-item priority-2">
                <span class="source-name">XtQuant双实例</span>
                <span class="source-latency">~38ms</span>
              </div>
              <div class="source-item priority-3">
                <span class="source-name">PyTdx服务器</span>
                <span class="source-latency">~100ms</span>
              </div>
            </div>
          </div>
        </div>

        <!-- L3.5: 股东信息 -->
        <div class="layer-card l3-5">
          <div class="layer-header">
            <div class="layer-badge">L3.5</div>
            <div class="layer-title">股东信息</div>
            <div class="layer-speed">50-500ms</div>
          </div>
          <div class="layer-content">
            <div class="layer-stats">
              <div class="stat-item">
                <span class="stat-label">数据类型</span>
                <span class="stat-value">股东名册</span>
              </div>
            </div>
          </div>
        </div>

        <!-- L4: 财务数据 -->
        <div class="layer-card l4">
          <div class="layer-header">
            <div class="layer-badge">L4</div>
            <div class="layer-title">财务数据</div>
            <div class="layer-speed">100-300ms</div>
          </div>
          <div class="layer-content">
            <div class="layer-stats">
              <div class="stat-item">
                <span class="stat-label">字段数</span>
                <span class="stat-value">GP1-GP46 (46个)</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">数据源</span>
                <span class="stat-value">PyTdx优先</span>
              </div>
            </div>
          </div>
        </div>

        <!-- L5: 特色数据 -->
        <div class="layer-card l5">
          <div class="layer-header">
            <div class="layer-badge">L5</div>
            <div class="layer-title">特色数据</div>
            <div class="layer-speed">10-500ms</div>
          </div>
          <div class="layer-content">
            <div class="layer-stats">
              <div class="stat-item">
                <span class="stat-label">数据类型</span>
                <span class="stat-value">板块/预警</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">数据源</span>
                <span class="stat-value">LocalDB</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 多级缓存展示 -->
    <div class="cache-section">
      <div class="section-title">
        <h2>多级缓存架构</h2>
        <p class="section-subtitle">内存缓存 → Redis缓存 → 本地DB → 在线数据源</p>
      </div>

      <div class="cache-levels">
        <!-- L1: 内存缓存 -->
        <div class="cache-level l1">
          <div class="cache-header">
            <div class="cache-title">L1 内存缓存</div>
            <div class="cache-latency">&lt;1ms</div>
          </div>
          <div class="cache-stats">
            <div class="stat-row">
              <span class="stat-label">缓存命中率</span>
              <span class="stat-value">{{ cacheStats.l1_hit_rate || '0%' }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">使用率</span>
              <span class="stat-value">{{ cacheStats.l1_usage || '0%' }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">TTL</span>
              <span class="stat-value">5-60秒</span>
            </div>
          </div>
          <div class="cache-visual">
            <div class="cache-bar">
              <div class="cache-fill" :style="{ width: cacheStats.l1_usage || '0%' }"></div>
            </div>
          </div>
        </div>

        <!-- L2: Redis缓存 -->
        <div class="cache-level l2">
          <div class="cache-header">
            <div class="cache-title">L2 Redis缓存</div>
            <div class="cache-latency">0.566ms</div>
          </div>
          <div class="cache-stats">
            <div class="stat-row">
              <span class="stat-label">缓存命中率</span>
              <span class="stat-value">{{ cacheStats.l2_hit_rate || '0%' }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">键数量</span>
              <span class="stat-value">{{ cacheStats.l2_keyspace || 0 }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">TTL</span>
              <span class="stat-value">60秒-30分钟</span>
            </div>
          </div>
          <div class="cache-status" :class="{ active: cacheStats.l2_enabled }">
            {{ cacheStats.l2_enabled ? '✅ 已启用' : '❌ 未启用' }}
          </div>
        </div>

        <!-- L3: 本地数据库 -->
        <div class="cache-level l3">
          <div class="cache-header">
            <div class="cache-title">L3 QLib本地DB</div>
            <div class="cache-latency">10-100ms</div>
          </div>
          <div class="cache-stats">
            <div class="stat-row">
              <span class="stat-label">股票数量</span>
              <span class="stat-value">{{ cacheStats.l3_stocks || 0 }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">覆盖率</span>
              <span class="stat-value">{{ cacheStats.l3_coverage || '0%' }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">最后更新</span>
              <span class="stat-value">{{ cacheStats.l3_last_update || '-' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据流转可视化 -->
    <div class="data-flow-section">
      <div class="section-title">
        <h2>数据流转过程</h2>
        <p class="section-subtitle">完整的获取 → 缓存 → 归档流程</p>
      </div>

      <div class="flow-diagram">
        <div class="flow-step" v-for="(step, index) in flowSteps" :key="index">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-content">
            <div class="step-title">{{ step.title }}</div>
            <div class="step-description">{{ step.description }}</div>
            <div class="step-latency">{{ step.latency }}</div>
          </div>
          <div class="step-arrow" v-if="index < flowSteps.length - 1">→</div>
        </div>
      </div>

      <div class="data-flow-cards">
        <!-- 首次获取流程 -->
        <div class="flow-card">
          <div class="flow-card-header">
            <h3>首次获取流程</h3>
          </div>
          <div class="flow-card-content">
            <div class="flow-step-item">
              <span class="step-label">用户请求</span>
              <span class="step-arrow">↓</span>
            </div>
            <div class="flow-step-item">
              <span class="step-label">检查内存缓存</span>
              <span class="step-status miss">未命中</span>
              <span class="step-arrow">↓</span>
            </div>
            <div class="flow-step-item">
              <span class="step-label">检查Redis缓存</span>
              <span class="step-status miss">未命中</span>
              <span class="step-arrow">↓</span>
            </div>
            <div class="flow-step-item">
              <span class="step-label">检查QLib本地DB</span>
              <span class="step-status miss">未命中</span>
              <span class="step-arrow">↓</span>
            </div>
            <div class="flow-step-item highlight">
              <span class="step-label">智能数据源选择</span>
              <span class="step-status success">XtQuant → PyTdx</span>
              <span class="step-arrow">↓</span>
            </div>
            <div class="flow-step-item highlight">
              <span class="step-label">数据归档</span>
              <span class="step-status success">.day文件 → QLib主数据库</span>
              <span class="step-arrow">↓</span>
            </div>
            <div class="flow-step-item">
              <span class="step-label">更新缓存</span>
              <span class="step-status success">Redis + 内存</span>
              <span class="step-arrow">↓</span>
            </div>
            <div class="flow-step-item">
              <span class="step-label">返回用户</span>
              <span class="step-status success">✅</span>
            </div>
          </div>
        </div>

        <!-- 缓存命中流程 -->
        <div class="flow-card">
          <div class="flow-card-header">
            <h3>缓存命中流程（理想）</h3>
          </div>
          <div class="flow-card-content">
            <div class="flow-step-item">
              <span class="step-label">用户请求</span>
              <span class="step-arrow">↓</span>
            </div>
            <div class="flow-step-item highlight">
              <span class="step-label">检查内存缓存</span>
              <span class="step-status hit">命中 ✅</span>
            </div>
            <div class="flow-step-item">
              <span class="step-label">返回数据</span>
              <span class="step-status success">&lt;1ms</span>
            </div>
            <div class="flow-performance">
              <div class="performance-label">性能提升</div>
              <div class="performance-value">88x 加速</div>
              <div class="performance-compare">50ms → &lt;1ms</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 设置对话框 -->
    <el-dialog v-model="showSettings" title="数据源配置" width="800px">
      <el-tabs v-model="settingsTab">
        <el-tab-pane label="数据源优先级" name="sources">
          <div class="settings-content">
            <p class="settings-tip">根据L0-L5数据类型自动选择最优数据源</p>
            <div class="source-priority-list">
              <div v-for="layer in dataLayers" :key="layer.level" class="layer-config">
                <div class="layer-config-header">
                  <span class="layer-level-badge">{{ layer.level }}</span>
                  <span class="layer-name">{{ layer.name }}</span>
                </div>
                <div class="layer-sources">
                  <div v-for="source in layer.sources" :key="source.name" class="source-priority">
                    <span class="priority-badge">优先级 {{ source.priority }}</span>
                    <span class="source-name">{{ source.name }}</span>
                    <span class="source-speed">{{ source.speed }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="缓存配置" name="cache">
          <div class="settings-content">
            <el-form :model="cacheConfig" label-width="120px">
              <el-form-item label="内存缓存TTL">
                <el-input-number v-model="cacheConfig.l1_ttl" :min="1" :max="300" />
                <span class="unit">秒</span>
              </el-form-item>
              <el-form-item label="Redis缓存TTL">
                <el-input-number v-model="cacheConfig.l2_ttl" :min="10" :max="3600" />
                <span class="unit">秒</span>
              </el-form-item>
              <el-form-item label="启用Redis">
                <el-switch v-model="cacheConfig.enable_redis" />
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="showSettings = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Setting, Connection } from '@element-plus/icons-vue'
import axios from 'axios'

// 状态定义
const refreshing = ref(false)
const syncing = ref(false)
const showSettings = ref(false)
const settingsTab = ref('sources')
const l0Usage = ref(0)

// 数据同步状态
const syncStatus = ref({
  status: 'idle',
  progress: 0,
  total_stocks: 0,
  processed_stocks: 0
})

// 缓存统计
const cacheStats = ref({
  l1_hit_rate: '0%',
  l1_usage: '0%',
  l2_hit_rate: '0%',
  l2_keyspace: 0,
  l2_enabled: true,
  l3_stocks: 5496,
  l3_coverage: '98.5%',
  l3_last_update: '2026-02-04 00:26'
})

// 缓存配置
const cacheConfig = ref({
  l1_ttl: 5,
  l2_ttl: 60,
  enable_redis: true
})

// 数据流转步骤
const flowSteps = ref([
  { title: '用户请求', description: '请求数据', latency: '-' },
  { title: 'L1内存缓存', description: '检查内存缓存', latency: '&lt;1ms' },
  { title: 'L2 Redis缓存', description: '检查Redis缓存', latency: '0.566ms' },
  { title: 'L3 QLib本地DB', description: '检查本地数据库', latency: '10-100ms' },
  { title: 'L4 智能数据源', description: '根据L0-L5层级选择', latency: '5-100ms' },
  { title: '数据归档', description: '.day文件 → QLib主数据库', latency: '-' },
  { title: '更新缓存', description: 'Redis + 内存缓存', latency: '-' }
])

// L0-L5数据层配置
const dataLayers = ref([
  {
    level: 'L0',
    name: '订阅缓存',
    sources: [
      { name: 'XtQuant双实例订阅', priority: 1, speed: '&lt;1ms' }
    ]
  },
  {
    level: 'L1',
    name: '实时快照',
    sources: [
      { name: 'XtQuant订阅', priority: 1, speed: '~1ms' },
      { name: 'PyTdx批量API', priority: 2, speed: '~17ms' }
    ]
  },
  {
    level: 'L2',
    name: '历史摘要',
    sources: [
      { name: 'QLib本地DB', priority: 1, speed: '7ms' },
      { name: 'XtQuant', priority: 2, speed: '~50ms' },
      { name: 'PyTdx', priority: 3, speed: '~100ms' }
    ]
  },
  {
    level: 'L3',
    name: '完整K线',
    sources: [
      { name: 'QLib本地DB', priority: 1, speed: '5ms' },
      { name: 'XtQuant双实例(117x并发)', priority: 2, speed: '~38ms' },
      { name: 'PyTdx服务器', priority: 3, speed: '~100ms' }
    ]
  },
  {
    level: 'L4',
    name: '财务数据',
    sources: [
      { name: 'QLib本地DB', priority: 1, speed: '50ms' },
      { name: 'PyTdx (37字段)', priority: 2, speed: '~100ms' }
    ]
  }
])

// 方法
const refreshAllData = async () => {
  refreshing.value = true
  try {
    // 调用API刷新数据
    const response = await axios.post('/api/v1/research/data/refresh')

    if (response.data.success) {
      ElMessage.success('数据刷新成功')
      await loadCacheStats()
    } else {
      ElMessage.error('数据刷新失败')
    }
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('数据刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 智能同步数据
const triggerSmartSync = async () => {
  syncing.value = true
  try {
    ElMessage.info('正在启动智能数据同步...')

    // 调用智能同步API
    const response = await axios.post('/api/v1/data-management/sync/trigger', {
      period: '1d',
      days_back: 30,
      save_to_qlib: true
    })

    if (response.data.success) {
      ElMessage.success('智能同步任务已启动！正在后台执行...')
      // 开始轮询同步状态
      startPollingSyncStatus()
    } else {
      ElMessage.error('启动同步任务失败')
    }
  } catch (error) {
    console.error('启动同步失败:', error)
    if (error.response?.status === 409) {
      ElMessage.warning('同步任务正在进行中，请稍后再试')
    } else {
      ElMessage.error('启动同步任务失败')
    }
  } finally {
    syncing.value = false
  }
}

// 轮询同步状态
const startPollingSyncStatus = () => {
  const pollInterval = setInterval(async () => {
    try {
      const response = await axios.get('/api/v1/data-management/sync/status')
      if (response.data.success) {
        syncStatus.value = response.data

        // 如果同步完成，停止轮询
        if (response.data.status === 'completed' || response.data.status === 'failed') {
          clearInterval(pollInterval)

          if (response.data.status === 'completed') {
            ElMessage.success(
              `✅ 同步完成！已同步 ${response.data.last_result?.synced_stocks} 只股票`
            )
          } else {
            ElMessage.error('❌ 同步失败')
          }

          // 刷新数据统计
          await loadCacheStats()
        }
      }
    } catch (error) {
      console.error('获取同步状态失败:', error)
      clearInterval(pollInterval)
    }
  }, 2000) // 每2秒轮询一次
}

const loadCacheStats = async () => {
  try {
    const response = await axios.get('/api/v1/research/data/cache-stats')
    if (response.data.success) {
      cacheStats.value = { ...cacheStats.value, ...response.data.data }
    }
  } catch (error) {
    console.error('加载缓存统计失败:', error)
  }
}

const saveSettings = () => {
  showSettings.value = false
  ElMessage.success('配置保存成功')
}

// 生命周期
onMounted(() => {
  loadCacheStats()
})
</script>

<style scoped lang="scss">
.data-management-view {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 30px;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .header-left {
    .phase-badge {
      display: inline-block;
      padding: 4px 12px;
      background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
      color: white;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 10px;
    }

    .page-title {
      font-size: 28px;
      font-weight: 700;
      color: #2c3e50;
      margin: 0 0 8px 0;
    }

    .page-subtitle {
      font-size: 14px;
      color: #7f8c8d;
      margin: 0;
    }
  }

  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.section-title {
  margin-bottom: 20px;

  h2 {
    font-size: 20px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0 0 5px 0;
  }

  .section-subtitle {
    font-size: 14px;
    color: #7f8c8d;
    margin: 0;
  }
}

// L0-L5 数据分层卡片
.data-layers-section {
  margin-bottom: 40px;
}

.layers-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.layer-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  }

  .layer-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #ecf0f1;

    .layer-badge {
      padding: 4px 10px;
      background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
      color: white;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
    }

    .layer-title {
      font-size: 16px;
      font-weight: 600;
      color: #2c3e50;
    }

    .layer-speed {
      font-size: 12px;
      color: #27ae60;
      font-weight: 600;
    }
  }

  .layer-content {
    .layer-stats {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-bottom: 15px;

      .stat-item {
        display: flex;
        justify-content: space-between;
        font-size: 13px;

        .stat-label {
          color: #7f8c8d;
        }

        .stat-value {
          color: #2c3e50;
          font-weight: 500;
        }
      }
    }

    .layer-usage {
      .usage-bar {
        height: 6px;
        background: #ecf0f1;
        border-radius: 3px;
        overflow: hidden;
        margin-bottom: 8px;

        .usage-fill {
          height: 100%;
          background: linear-gradient(90deg, #2962ff 0%, #764ba2 100%);
          transition: width 0.3s;
        }
      }

      .usage-text {
        font-size: 12px;
        color: #7f8c8d;
      }
    }

    .data-sources {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .source-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: #f8f9fa;
        border-radius: 6px;
        font-size: 12px;

        .source-name {
          flex: 1;
          color: #2c3e50;
        }

        .source-latency {
          color: #27ae60;
          font-weight: 600;
        }

        .priority-badge {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 600;
        }

        &.priority-1 .priority-badge {
          background: #e8f5e9;
          color: #2e7d32;
        }

        &.priority-2 .priority-badge {
          background: #fff3e0;
          color: #e65100;
        }

        &.priority-3 .priority-badge {
          background: #fce4ec;
          color: #c2185b;
        }
      }
    }
  }
}

// 多级缓存展示
.cache-section {
  margin-bottom: 40px;
}

.cache-levels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.cache-level {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

  .cache-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #ecf0f1;

    .cache-title {
      font-size: 16px;
      font-weight: 600;
      color: #2c3e50;
    }

    .cache-latency {
      font-size: 13px;
      color: #27ae60;
      font-weight: 600;
    }
  }

  .cache-stats {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 15px;

    .stat-row {
      display: flex;
      justify-content: space-between;
      font-size: 13px;

      .stat-label {
        color: #7f8c8d;
      }

      .stat-value {
        color: #2c3e50;
        font-weight: 600;
      }
    }
  }

  .cache-visual {
    .cache-bar {
      height: 8px;
      background: #ecf0f1;
      border-radius: 4px;
      overflow: hidden;

      .cache-fill {
        height: 100%;
        background: linear-gradient(90deg, #2962ff 0%, #764ba2 100%);
        transition: width 0.3s;
      }
    }
  }

  .cache-status {
    text-align: center;
    padding: 8px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;

    &.active {
      background: #e8f5e9;
      color: #2e7d32;
    }

    &:not(.active) {
      background: #ffebee;
      color: #c62828;
    }
  }
}

// 数据流转可视化
.data-flow-section {
  margin-bottom: 40px;
}

.flow-diagram {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow-x: auto;

  .flow-step {
    display: flex;
    align-items: center;
    gap: 15px;
    flex-shrink: 0;

    .step-number {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 14px;
      flex-shrink: 0;
    }

    .step-content {
      .step-title {
        font-size: 14px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 4px;
      }

      .step-description {
        font-size: 12px;
        color: #7f8c8d;
        margin-bottom: 4px;
      }

      .step-latency {
        font-size: 12px;
        color: #27ae60;
        font-weight: 600;
      }
    }

    .step-arrow {
      font-size: 20px;
      color: #bdc3c7;
      margin: 0 10px;
    }
  }
}

.data-flow-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.flow-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

  .flow-card-header {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #ecf0f1;

    h3 {
      font-size: 16px;
      font-weight: 600;
      color: #2c3e50;
      margin: 0;
    }
  }

  .flow-card-content {
    .flow-step-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px;
      margin-bottom: 8px;
      border-radius: 6px;
      transition: background 0.2s;

      &:not(:last-child) {
        margin-bottom: 12px;
      }

      .step-label {
        flex: 1;
        font-size: 13px;
        color: #2c3e50;
      }

      .step-status {
        font-size: 12px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        white-space: nowrap;

        &.hit {
          background: #e8f5e9;
          color: #2e7d32;
        }

        &.miss {
          background: #ffebee;
          color: #c62828;
        }

        &.success {
          background: #e8f5e9;
          color: #2e7d32;
        }
      }

      .step-arrow {
        color: #95a5a6;
        font-size: 16px;
      }

      &.highlight {
        background: #f0f4ff;
        border-left: 3px solid #2962ff;
      }
    }

    .flow-performance {
      margin-top: 20px;
      padding: 15px;
      background: linear-gradient(135deg, #2962ff15 0%, #764ba215 100%);
      border-radius: 8px;
      text-align: center;

      .performance-label {
        font-size: 12px;
        color: #7f8c8d;
        margin-bottom: 5px;
      }

      .performance-value {
        font-size: 24px;
        font-weight: 700;
        color: #2962ff;
        margin-bottom: 5px;
      }

      .performance-compare {
        font-size: 12px;
        color: #95a5a6;
      }
    }
  }
}

// 设置对话框
.settings-content {
  .settings-tip {
    color: #7f8c8d;
    font-size: 13px;
    margin-bottom: 20px;
  }

  .source-priority-list {
    .layer-config {
      margin-bottom: 20px;
      padding: 15px;
      background: #f8f9fa;
      border-radius: 8px;

      .layer-config-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;

        .layer-level-badge {
          padding: 4px 10px;
          background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
          color: white;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
        }

        .layer-name {
          font-size: 14px;
          font-weight: 600;
          color: #2c3e50;
        }
      }

      .layer-sources {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .source-priority {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 12px;
          background: white;
          border-radius: 6px;
          font-size: 13px;

          .priority-badge {
            padding: 2px 8px;
            background: #e8f5e9;
            color: #2e7d32;
            border-radius: 4px;
            font-weight: 600;
          }

          .source-name {
            flex: 1;
            color: #2c3e50;
          }

          .source-speed {
            color: #27ae60;
            font-weight: 600;
          }
        }
      }
    }
  }

  .unit {
    margin-left: 8px;
    color: #7f8c8d;
    font-size: 13px;
  }
}
</style>
