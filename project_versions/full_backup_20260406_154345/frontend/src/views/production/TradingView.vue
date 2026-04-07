<template>
  <div class="trading-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="phase-badge production">🚀 实盘阶段</div>
          <h1 class="page-title"><i class="fas fa-exchange-alt"></i> 实盘交易</h1>
          <p class="page-subtitle">交易接口管理、下单与撤单操作</p>
        </div>
        <div class="header-actions">
          <el-button
            v-if="!connectionStatus.connected"
            type="success"
            @click="connectInterface"
            :loading="connecting"
          >
            <el-icon><Connection /></el-icon>
            连接交易接口
          </el-button>
          <el-button
            v-else
            type="danger"
            @click="disconnectInterface"
          >
            <el-icon><SwitchButton /></el-icon>
            断开连接
          </el-button>
          <el-button @click="refreshAccount">
            <el-icon><Refresh /></el-icon>
            刷新账户
          </el-button>
        </div>
      </div>
    </div>

    <!-- 连接状态 -->
    <div class="connection-section">
      <el-alert
        :type="connectionStatus.connected ? 'success' : 'warning'"
        :closable="false"
      >
        <template #title>
          <div class="connection-status">
            <el-icon><component :is="connectionStatus.connected ? 'CircleCheck' : 'CircleClose'" /></el-icon>
            <span>{{ connectionStatus.connected ? '交易接口已连接' : '交易接口未连接' }}</span>
            <span v-if="connectionStatus.connected" class="account-info">
              账户: {{ connectionStatus.account_id }}
            </span>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 账户信息 -->
    <div class="account-section" v-if="accountInfo">
      <el-card>
        <template #header>
          <span>账户信息</span>
        </template>

        <el-row :gutter="20">
          <el-col :span="6">
            <div class="account-item">
              <span class="label">总资产</span>
              <span class="value">{{ formatCurrency(accountInfo.total_assets) }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="account-item">
              <span class="label">可用资金</span>
              <span class="value">{{ formatCurrency(accountInfo.cash) }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="account-item">
              <span class="label">持仓市值</span>
              <span class="value">{{ formatCurrency(accountInfo.market_value) }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="account-item">
              <span class="label">总盈亏</span>
              <span class="value" :class="{'profit': accountInfo.total_profit_loss >= 0, 'loss': accountInfo.total_profit_loss < 0}">
                {{ formatCurrency(accountInfo.total_profit_loss) }}
              </span>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 下单面板 -->
    <div class="order-panel">
      <el-card>
        <template #header>
          <span>下单</span>
        </template>

        <el-form :model="orderForm" label-width="100px" :disabled="!connectionStatus.connected">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="股票代码">
                <el-input
                  v-model="orderForm.symbol"
                  placeholder="例如: 600000.SH"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="订单方向">
                <el-radio-group v-model="orderForm.side">
                  <el-radio label="buy" size="large">买入</el-radio>
                  <el-radio label="sell" size="large">卖出</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="订单类型">
                <el-radio-group v-model="orderForm.order_type">
                  <el-radio label="market">市价单</el-radio>
                  <el-radio label="limit">限价单</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="数量">
                <el-input-number
                  v-model="orderForm.quantity"
                  :min="100"
                  :step="100"
                  controls-position="right"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="价格" v-if="orderForm.order_type === 'limit'">
                <el-input-number
                  v-model="orderForm.price"
                  :precision="2"
                  :step="0.01"
                  controls-position="right"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  @click="placeOrder"
                  :loading="placingOrder"
                  style="width: 100%"
                  :disabled="!connectionStatus.connected"
                >
                  {{ orderForm.side === 'buy' ? '买入' : '卖出' }}
                </el-button>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-card>
    </div>

    <!-- 订单查询 -->
    <div class="order-query-section">
      <el-card>
        <template #header>
          <div class="section-header">
            <span>订单查询</span>
            <el-input
              v-model="orderIdQuery"
              placeholder="输入订单ID"
              style="width: 200px"
            >
              <template #append>
                <el-button @click="queryOrder" :loading="queryingOrder">
                  查询
                </el-button>
              </template>
            </el-input>
          </div>
        </template>

        <div v-if="orderDetail" class="order-detail">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="订单ID">{{ orderDetail.order_id }}</el-descriptions-item>
            <el-descriptions-item label="股票代码">{{ orderDetail.symbol }}</el-descriptions-item>
            <el-descriptions-item label="订单方向">
              <el-tag :type="orderDetail.direction === 'buy' ? 'success' : 'danger'">
                {{ orderDetail.direction === 'buy' ? '买入' : '卖出' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="订单类型">
              <el-tag>{{ orderDetail.order_type === 'market' ? '市价单' : '限价单' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数量">{{ orderDetail.quantity }}</el-descriptions-item>
            <el-descriptions-item label="价格">{{ orderDetail.price?.toFixed(2) || '-' }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getOrderStatusType(orderDetail.status)">
                {{ getOrderStatusText(orderDetail.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="成交数量">{{ orderDetail.filled_quantity || 0 }}</el-descriptions-item>
            <el-descriptions-item label="成交均价">{{ orderDetail.avg_fill_price?.toFixed(2) || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDateTime(orderDetail.created_at) }}</el-descriptions-item>
          </el-descriptions>

          <div class="order-actions" v-if="orderDetail.status === 'submitted' || orderDetail.status === 'partial_filled'">
            <el-button type="danger" @click="cancelOrder(orderDetail.order_id)" :loading="cancellingOrder">
              撤单
            </el-button>
          </div>
        </div>

        <el-empty v-else description="请输入订单ID查询" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Connection,
  SwitchButton,
  Refresh,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'

// 状态
const connecting = ref(false)
const placingOrder = ref(false)
const queryingOrder = ref(false)
const cancellingOrder = ref(false)

// 数据
const connectionStatus = ref<any>({
  connected: false,
  account_id: ''
})

const accountInfo = ref<any>(null)

const orderForm = ref({
  symbol: '',
  side: 'buy',
  order_type: 'market',
  quantity: 100,
  price: 0
})

const orderIdQuery = ref('')
const orderDetail = ref<any>(null)

// 格式化函数
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(value)
}

const formatDateTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getOrderStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    'submitted': 'warning',
    'partial_filled': 'primary',
    'filled': 'success',
    'cancelled': 'info',
    'rejected': 'danger'
  }
  return typeMap[status] || 'info'
}

const getOrderStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    'submitted': '已报',
    'partial_filled': '部分成交',
    'filled': '已成',
    'cancelled': '已撤',
    'rejected': '废单'
  }
  return textMap[status] || status
}

// API调用
const API_BASE = '/api/v1/production/trading'

const checkConnectionStatus = async () => {
  try {
    const res = await fetch(`${API_BASE}/status`)
    const data = await res.json()
    if (data.code === 200) {
      connectionStatus.value = data.data
      if (connectionStatus.value.connected) {
        refreshAccount()
      }
    }
  } catch (error: any) {
    console.error('获取连接状态失败:', error)
  }
}

const connectInterface = async () => {
  connecting.value = true
  try {
    const res = await fetch(`${API_BASE}/connect`, { method: 'POST' })
    const data = await res.json()
    if (data.code === 200) {
      connectionStatus.value = data.data
      ElMessage.success('连接成功')
      refreshAccount()
    }
  } catch (error: any) {
    ElMessage.error('连接失败: ' + error.message)
  } finally {
    connecting.value = false
  }
}

const disconnectInterface = async () => {
  try {
    await ElMessageBox.confirm('确定要断开交易接口吗？', '确认', {
      type: 'warning'
    })

    const res = await fetch(`${API_BASE}/disconnect`, { method: 'POST' })
    const data = await res.json()
    if (data.code === 200) {
      connectionStatus.value.connected = false
      accountInfo.value = null
      ElMessage.success('已断开连接')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('断开失败: ' + error.message)
    }
  }
}

const refreshAccount = async () => {
  try {
    const res = await fetch(`${API_BASE}/account`)
    const data = await res.json()
    if (data.code === 200) {
      accountInfo.value = data.data
    }
  } catch (error: any) {
    ElMessage.error('获取账户信息失败: ' + error.message)
  }
}

const placeOrder = async () => {
  if (!orderForm.value.symbol) {
    ElMessage.warning('请输入股票代码')
    return
  }

  if (orderForm.value.order_type === 'limit' && !orderForm.value.price) {
    ElMessage.warning('限价单必须输入价格')
    return
  }

  placingOrder.value = true
  try {
    const res = await fetch(`${API_BASE}/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        account_id: 'default',
        ...orderForm.value
      })
    })
    const data = await res.json()
    if (data.code === 200) {
      ElMessage.success(`下单成功！订单ID: ${data.data.order_id}`)
      orderIdQuery.value = data.data.order_id
      queryOrder()
    }
  } catch (error: any) {
    ElMessage.error('下单失败: ' + error.message)
  } finally {
    placingOrder.value = false
  }
}

const queryOrder = async () => {
  if (!orderIdQuery.value) {
    ElMessage.warning('请输入订单ID')
    return
  }

  queryingOrder.value = true
  try {
    const res = await fetch(`${API_BASE}/orders/${orderIdQuery.value}`)
    const data = await res.json()
    if (data.code === 200) {
      orderDetail.value = data.data
    } else {
      ElMessage.warning('未找到该订单')
      orderDetail.value = null
    }
  } catch (error: any) {
    ElMessage.error('查询失败: ' + error.message)
  } finally {
    queryingOrder.value = false
  }
}

const cancelOrder = async (orderId: string) => {
  try {
    await ElMessageBox.confirm('确定要撤单吗？', '确认', {
      type: 'warning'
    })

    cancellingOrder.value = true
    const res = await fetch(`${API_BASE}/orders/${orderId}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.code === 200) {
      ElMessage.success('撤单成功')
      queryOrder()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('撤单失败: ' + error.message)
    }
  } finally {
    cancellingOrder.value = false
  }
}

// 生命周期
onMounted(() => {
  checkConnectionStatus()
})
</script>

<style scoped>
.trading-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.phase-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
}

.phase-badge.production {
  background: linear-gradient(135deg, #2962ff 0%, #764ba2 100%);
  color: white;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.page-subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.connection-section {
  margin-bottom: 20px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.account-info {
  margin-left: 20px;
  color: #606266;
}

.account-section {
  margin-bottom: 20px;
}

.account-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.account-item .label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.account-item .value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.account-item .value.profit {
  color: #F56C6C;
}

.account-item .value.loss {
  color: #67C23A;
}

.order-panel,
.order-query-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-detail {
  padding: 10px 0;
}

.order-actions {
  margin-top: 20px;
  text-align: center;
}
</style>
