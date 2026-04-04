<template>
  <div class="factor-engine-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="phase-badge research">🔬 研究阶段</div>
          <h1 class="page-title"><i class="fas fa-cogs"></i> 因子计算引擎</h1>
          <p class="page-subtitle">双输入端：数据驱动 + AI助手策略构思</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="calculateFactors" :loading="calculating">
            <el-icon><Operation /></el-icon>
            计算因子
          </el-button>
          <el-button @click="showTemplates = true">
            <el-icon><Document /></el-icon>
            因子模板
          </el-button>
        </div>
      </div>
    </div>

    <!-- 因子类型选择 -->
    <div class="factor-types-section">
      <div class="section-title">
        <h2>选择因子类型</h2>
        <p class="section-subtitle">支持Alpha158、Alpha360等主流因子库</p>
      </div>

      <div class="factor-types-grid">
        <div
          v-for="type in factorTypes"
          :key="type.id"
          :class="['factor-type-card', { active: selectedFactorType === type.id }]"
          @click="selectFactorType(type.id)"
        >
          <div class="factor-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="factor-info">
            <h3>{{ type.name }}</h3>
            <p>{{ type.description }}</p>
            <div class="factor-meta">
              <span class="factor-count">{{ type.factorCount }}个因子</span>
              <span class="factor-time">{{ type.estimatedTime }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 股票选择 -->
    <div class="stock-selection-section">
      <div class="section-title">
        <h2>选择股票池</h2>
        <p class="section-subtitle">支持自定义股票池、指数成分股、全市场</p>
      </div>

      <div class="stock-selection-container">
        <el-tabs v-model="stockSelectionMode">
          <el-tab-pane label="自定义股票" name="custom">
            <el-input
              v-model="customStocks"
              type="textarea"
              :rows="3"
              placeholder="输入股票代码，用逗号或换行分隔&#10;例如：600000.SH, 000001.SZ"
            ></el-input>
          </el-tab-pane>
          <el-tab-pane label="指数成分股" name="index">
            <el-select v-model="selectedIndex" placeholder="选择指数" style="width: 200px; margin-right: 10px;">
              <el-option label="上证50" value="sh000050"></el-option>
              <el-option label="沪深300" value="sh000300"></el-option>
              <el-option label="中证500" value="sh000905"></el-option>
              <el-option label="创业板指" value="sz399006"></el-option>
            </el-select>
            <el-button @click="loadIndexStocks">加载成分股</el-button>
            <div v-if="indexStocks.length > 0" class="index-stocks-info">
              已加载 {{ indexStocks.length }} 只成分股
            </div>
          </el-tab-pane>
          <el-tab-pane label="全市场" name="all">
            <el-alert title="全市场计算耗时较长，建议先测试少量股票" type="warning" show-icon :closable="false" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 时间范围选择 -->
    <div class="time-range-section">
      <div class="section-title">
        <h2>选择时间范围</h2>
      </div>

      <div class="time-range-container">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        ></el-date-picker>
      </div>
    </div>

    <!-- 计算结果展示 -->
    <div class="results-section" v-if="calculationResults">
      <div class="section-title">
        <h2>计算结果</h2>
        <div class="section-actions">
          <el-button @click="exportResults">
            <el-icon><Download /></el-icon>
            导出结果
          </el-button>
          <el-button @click="saveToQLib">
            <el-icon><FolderOpened /></el-icon>
            保存到QLib
          </el-button>
        </div>
      </div>

      <div class="results-stats">
        <div class="stat-card">
          <div class="stat-label">计算状态</div>
          <div class="stat-value" :class="calculationResults.status">
            {{ calculationResults.statusText }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">股票数量</div>
          <div class="stat-value">{{ calculationResults.stockCount }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">因子数量</div>
          <div class="stat-value">{{ calculationResults.factorCount }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">耗时</div>
          <div class="stat-value">{{ calculationResults.duration }}</div>
        </div>
      </div>

      <!-- 因子数据预览 -->
      <div class="factor-preview">
        <el-table :data="calculationResults.previewData" stripe border style="width: 100%" max-height="400">
          <el-table-column prop="symbol" label="股票代码" width="120" />
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="factor_001" label="Alpha001" width="100" />
          <el-table-column prop="factor_002" label="Alpha002" width="100" />
          <el-table-column prop="factor_003" label="Alpha003" width="100" />
          <!-- 显示更多因子列 -->
        </el-table>
      </div>
    </div>

    <!-- 因子模板对话框 -->
    <el-dialog v-model="showTemplates" title="因子模板" width="900px">
      <div class="templates-grid">
        <div
          v-for="template in factorTemplates"
          :key="template.id"
          class="template-card"
          @click="applyTemplate(template)"
        >
          <div class="template-header">
            <h3>{{ template.name }}</h3>
            <el-tag :type="template.type">{{ template.category }}</el-tag>
          </div>
          <div class="template-content">
            <p>{{ template.description }}</p>
            <div class="template-meta">
              <span>因子数: {{ template.factorCount }}</span>
              <span>耗时: {{ template.estimatedTime }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Operation, Document, TrendCharts, Download, FolderOpened } from '@element-plus/icons-vue'
import axios from 'axios'

// 状态定义
const calculating = ref(false)
const showTemplates = ref(false)
const selectedFactorType = ref('alpha158')
const customStocks = ref('')
const selectedIndex = ref('')
const indexStocks = ref<any[]>([])
const dateRange = ref<any[]>([])
const calculationResults = ref<any>(null)

// 因子类型
const factorTypes = ref([
  {
    id: 'alpha158',
    name: 'Alpha158',
    description: '经典因子库，包含158个技术因子',
    factorCount: 158,
    estimatedTime: '约5-10分钟（100只股票）'
  },
  {
    id: 'alpha360',
    name: 'Alpha360',
    description: '扩展因子库，包含360个技术因子',
    factorCount: 360,
    estimatedTime: '约15-20分钟（100只股票）'
  },
  {
    id: 'custom',
    name: '自定义因子',
    description: '自定义因子计算公式',
    factorCount: '自定义',
    estimatedTime: '根据公式复杂度'
  }
])

// 因子模板
const factorTemplates = ref([
  {
    id: 1,
    name: '动量类因子',
    category: 'momentum',
    description: '基于价格动量的因子，包括ROC、MA等',
    factorCount: 20,
    estimatedTime: '约2分钟'
  },
  {
    id: 2,
    name: '波动率类因子',
    category: 'volatility',
    description: '基于价格波动率的因子，包括STD、ATR等',
    factorCount: 15,
    estimatedTime: '约2分钟'
  },
  {
    id: 3,
    name: '成交量类因子',
    category: 'volume',
    description: '基于成交量的因子，包括OBV、VMA等',
    factorCount: 18,
    estimatedTime: '约2分钟'
  }
])

// 股票选择模式
const stockSelectionMode = ref('custom')

// 方法
const selectFactorType = (typeId: string) => {
  selectedFactorType.value = typeId
}

const loadIndexStocks = async () => {
  if (!selectedIndex.value) {
    ElMessage.warning('请先选择指数')
    return
  }

  try {
    const response = await axios.get(`/api/v1/research/data/index/${selectedIndex.value}`)
    if (response.data.success) {
      indexStocks.value = response.data.data.stocks
      ElMessage.success(`成功加载 ${indexStocks.value.length} 只成分股`)
    }
  } catch (error) {
    console.error('加载成分股失败:', error)
    ElMessage.error('加载成分股失败')
  }
}

const calculateFactors = async () => {
  // 准备计算参数
  let stocks: string[] = []

  if (stockSelectionMode.value === 'custom') {
    if (!customStocks.value) {
      ElMessage.warning('请输入股票代码')
      return
    }
    stocks = customStocks.value.split(/[,，\n]/).map(s => s.trim()).filter(s => s)
  } else if (stockSelectionMode.value === 'index') {
    stocks = indexStocks.value
  } else {
    // 全市场
    ElMessage.warning('全市场计算暂未实现，请先使用自定义股票')
    return
  }

  if (stocks.length === 0) {
    ElMessage.warning('请选择股票')
    return
  }

  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择时间范围')
    return
  }

  calculating.value = true

  try {
    const response = await axios.post('/api/v1/research/factor/calculate', {
      factor_type: selectedFactorType.value,
      symbols: stocks,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1]
    })

    if (response.data.success) {
      calculationResults.value = response.data.data
      ElMessage.success('因子计算成功')
    } else {
      ElMessage.error('因子计算失败')
    }
  } catch (error) {
    console.error('计算因子失败:', error)
    ElMessage.error('因子计算失败')
  } finally {
    calculating.value = false
  }
}

const exportResults = () => {
  ElMessage.info('导出功能开发中...')
}

const saveToQLib = () => {
  ElMessage.info('保存到QLib功能开发中...')
}

const applyTemplate = (template: any) => {
  ElMessage.success(`已应用模板: ${template.name}`)
  showTemplates.value = false
}
</script>

<style scoped lang="scss">
.factor-engine-view {
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

  .section-actions {
    float: right;
    display: flex;
    gap: 10px;
  }
}

.factor-types-section,
.stock-selection-section,
.time-range-section,
.results-section {
  margin-bottom: 40px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.factor-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.factor-type-card {
  padding: 20px;
  border: 2px solid #ecf0f1;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    border-color: #2962ff;
    transform: translateY(-2px);
  }

  &.active {
    border-color: #2962ff;
    background: linear-gradient(135deg, #2962ff10 0%, #764ba210 100%);
  }

  .factor-icon {
    font-size: 32px;
    color: #2962ff;
    margin-bottom: 15px;
  }

  .factor-info {
    h3 {
      font-size: 18px;
      font-weight: 600;
      color: #2c3e50;
      margin: 0 0 8px 0;
    }

    p {
      font-size: 14px;
      color: #7f8c8d;
      margin: 0 0 12px 0;
    }

    .factor-meta {
      display: flex;
      gap: 15px;
      font-size: 12px;
      color: #95a5a6;
    }
  }
}

.stock-selection-container {
  .index-stocks-info {
    margin-top: 10px;
    padding: 8px 12px;
    background: #e8f5e9;
    color: #2e7d32;
    border-radius: 6px;
    display: inline-block;
  }
}

.time-range-container {
  display: flex;
  align-items: center;
}

.results-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;

  .stat-card {
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;

    .stat-label {
      font-size: 12px;
      color: #7f8c8d;
      margin-bottom: 5px;
    }

    .stat-value {
      font-size: 20px;
      font-weight: 700;
      color: #2c3e50;

      &.success {
        color: #27ae60;
      }

      &.error {
        color: #e74c3c;
      }
    }
  }
}

.factor-preview {
  margin-top: 20px;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;

  .template-card {
    padding: 15px;
    border: 1px solid #ecf0f1;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      border-color: #2962ff;
      transform: translateY(-2px);
    }

    .template-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;

      h3 {
        font-size: 16px;
        font-weight: 600;
        color: #2c3e50;
        margin: 0;
      }
    }

    .template-content {
      p {
        font-size: 13px;
        color: #7f8c8d;
        margin: 0 0 10px 0;
      }

      .template-meta {
        display: flex;
        gap: 10px;
        font-size: 12px;
        color: #95a5a6;
      }
    }
  }
}
</style>
