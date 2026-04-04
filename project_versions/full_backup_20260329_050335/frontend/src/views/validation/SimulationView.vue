<template>
  <div class="simulation-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">🎮 模拟实盘验证</h1>
        <p class="page-subtitle">使用真实行情数据验证策略表现</p>
      </div>
      <div class="header-right">
        <el-button @click="handleBack">返回</el-button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <el-row :gutter="16">
      <!-- 左侧：控制面板 -->
      <el-col :span="8">
        <SimulationControlPanel />
      </el-col>

      <!-- 右侧：监控面板 -->
      <el-col :span="16">
        <el-tabs v-model="activeTab" class="monitoring-tabs" @change="handleTabChange">
          <el-tab-pane label="实时监控" name="monitoring">
            <div class="placeholder-content">
              <el-icon size="48" color="#909399"><Monitor /></el-icon>
              <p class="placeholder-text">实时监控功能开发中...</p>
            </div>
          </el-tab-pane>

          <el-tab-pane label="持仓管理" name="positions">
            <PositionTable
              :account-id="accountId"
              :positions="positions"
              :loading="loadingPositions"
              @refresh="handleRefreshPositions"
            />
          </el-tab-pane>

          <el-tab-pane label="交易记录" name="trades">
            <TradeTable
              :orders="orders"
              :loading="loadingOrders"
              @refresh="handleRefreshOrders"
            />
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor, List, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import SimulationControlPanel from '@/components/validation/simulation/SimulationControlPanel.vue'
import PositionTable from '@/components/validation/simulation/PositionTable.vue'
import TradeTable from '@/components/validation/simulation/TradeTable.vue'
import { simulationApi } from '@/api/modules/simulation'
import type { Position, Order } from '@/api/modules/simulation'

const router = useRouter()
const activeTab = ref('monitoring')

// 账户ID
const accountId = ref('default_account')

// 数据状态
const positions = ref<Position[]>([])
const orders = ref<Order[]>([])
const loadingPositions = ref(false)
const loadingOrders = ref(false)

// 定时器
let refreshTimer: NodeJS.Timeout | null = null

// 加载持仓数据
const loadPositions = async () => {
  loadingPositions.value = true
  try {
    const response = await simulationApi.getPositions(accountId.value)
    if (response.code === 200) {
      positions.value = response.data
    } else {
      // 使用降级数据
      positions.value = []
      console.warn('获取持仓数据失败，使用空数据')
    }
  } catch (error) {
    console.error('加载持仓数据失败:', error)
    // 失败时使用空数据
    positions.value = []
  } finally {
    loadingPositions.value = false
  }
}

// 加载交易记录
const loadOrders = async () => {
  loadingOrders.value = true
  try {
    const response = await simulationApi.getOrders(accountId.value)
    if (response.code === 200) {
      orders.value = response.data
    } else {
      // 使用降级数据
      orders.value = []
      console.warn('获取交易记录失败，使用空数据')
    }
  } catch (error) {
    console.error('加载交易记录失败:', error)
    // 失败时使用空数据
    orders.value = []
  } finally {
    loadingOrders.value = false
  }
}

// 刷新持仓数据
const handleRefreshPositions = async () => {
  await loadPositions()
}

// 刷新交易记录
const handleRefreshOrders = async () => {
  await loadOrders()
}

// Tab切换处理
const handleTabChange = (tabName: string) => {
  activeTab.value = tabName
  // 根据Tab加载数据
  if (tabName === 'positions') {
    loadPositions()
  } else if (tabName === 'trades') {
    loadOrders()
  }
}

// 返回
const handleBack = () => {
  router.back()
}

// 组件挂载
onMounted(() => {
  // 初始加载数据
  loadPositions()
  loadOrders()

  // 设置定时刷新（每5秒）
  refreshTimer = setInterval(() => {
    if (activeTab.value === 'positions') {
      loadPositions()
    } else if (activeTab.value === 'trades') {
      loadOrders()
    }
  }, 5000)
})

// 组件卸载
onUnmounted(() => {
  // 清除定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})
</script>

<style scoped lang="scss">
.simulation-view {
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

  .monitoring-tabs {
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
