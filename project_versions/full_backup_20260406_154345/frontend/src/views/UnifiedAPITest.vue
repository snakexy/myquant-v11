<template>
  <div class="unified-api-test">
    <div class="header">
      <h1>🚀 统一数据获取API测试</h1>
      <p>测试新的统一数据获取系统 - 板块数据 + 股票K线 + 智能补全</p>
    </div>

    <!-- 测试选项卡 -->
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 板块列表测试 -->
      <el-tab-pane label="板块列表" name="boards">
        <div class="test-section">
          <h2>板块列表测试</h2>

          <!-- 控制面板 -->
          <div class="control-panel">
            <el-select v-model="boardCategory" placeholder="选择分类" clearable style="width: 200px; margin-right: 10px;">
              <el-option label="全部分类" value=""></el-option>
              <el-option label="一级行业" value="一级行业"></el-option>
              <el-option label="二级行业" value="二级行业"></el-option>
              <el-option label="概念板块" value="概念板块"></el-option>
              <el-option label="行业板块" value="行业板块"></el-option>
            </el-select>

            <el-checkbox v-model="boardHasData" style="margin-right: 10px;">只显示有数据</el-checkbox>

            <el-button type="primary" @click="loadBoardList" :loading="boardListLoading">
              获取板块列表
            </el-button>
          </div>

          <!-- 结果显示 -->
          <div v-if="boardListResult" class="result-panel">
            <el-alert
              :title="`成功获取 ${boardListResult.count} 个板块`"
              type="success"
              :closable="false"
              style="margin-bottom: 15px;"
            />

            <!-- 统计信息 -->
            <div class="stats">
              <el-tag type="success" size="large">总数: {{ boardListResult.count }}</el-tag>
              <el-tag type="primary" size="large">有数据: {{ boardsWithData }}</el-tag>
            </div>

            <!-- 板块列表 -->
            <el-table :data="boardListResult.boards.slice(0, 50)" style="width: 100%; margin-top: 15px;" max-height="500">
              <el-table-column prop="code" label="代码" width="100" />
              <el-table-column prop="name" label="名称" width="200" />
              <el-table-column prop="category" label="分类" width="150" />
              <el-table-column label="数据状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.has_data ? 'success' : 'info'">
                    {{ row.has_data ? '有数据' : '无数据' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>

            <div v-if="boardListResult.count > 50" style="margin-top: 10px; text-align: center; color: #909399;">
              仅显示前50个，共 {{ boardListResult.count }} 个板块
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 板块K线测试 -->
      <el-tab-pane label="板块K线" name="board-kline">
        <div class="test-section">
          <h2>板块K线测试</h2>

          <!-- 控制面板 -->
          <div class="control-panel">
            <el-input
              v-model="boardCode"
              placeholder="板块代码 (如: 880001)"
              style="width: 200px; margin-right: 10px;"
            />

            <el-date-picker
              v-model="boardStartDate"
              type="date"
              placeholder="开始日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 150px; margin-right: 10px;"
            />

            <el-date-picker
              v-model="boardEndDate"
              type="date"
              placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 150px; margin-right: 10px;"
            />

            <el-input-number
              v-model="boardLimit"
              :min="1"
              :max="1000"
              placeholder="数量"
              style="width: 120px; margin-right: 10px;"
            />

            <el-button type="primary" @click="loadBoardKline" :loading="boardKlineLoading">
              获取K线
            </el-button>
          </div>

          <!-- 结果显示 -->
          <div v-if="boardKlineResult" class="result-panel">
            <el-alert
              :title="`成功获取 ${boardKlineResult.count} 条K线数据`"
              type="success"
              :closable="false"
              style="margin-bottom: 15px;"
            />

            <!-- 日期范围 -->
            <div v-if="boardKlineResult.date_range" class="stats">
              <el-tag type="info">{{ boardKlineResult.date_range.start }}</el-tag>
              <el-icon><ArrowRight /></el-icon>
              <el-tag type="info">{{ boardKlineResult.date_range.end }}</el-tag>
            </div>

            <!-- K线数据表格 -->
            <el-table :data="boardKlineResult.data.slice(0, 20)" style="width: 100%; margin-top: 15px;" max-height="400">
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="open" label="开盘" width="100" />
              <el-table-column prop="high" label="最高" width="100" />
              <el-table-column prop="low" label="最低" width="100" />
              <el-table-column prop="close" label="收盘" width="100" />
              <el-table-column prop="volume" label="成交量" width="120" />
            </el-table>

            <div v-if="boardKlineResult.count > 20" style="margin-top: 10px; text-align: center; color: #909399;">
              仅显示前20条，共 {{ boardKlineResult.count }} 条数据
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 板块行情测试 -->
      <el-tab-pane label="板块行情" name="board-quote">
        <div class="test-section">
          <h2>板块实时行情测试</h2>

          <!-- 控制面板 -->
          <div class="control-panel">
            <el-input
              v-model="quoteBoardCode"
              placeholder="板块代码 (如: 880001)"
              style="width: 200px; margin-right: 10px;"
            />

            <el-button type="primary" @click="loadBoardQuote" :loading="boardQuoteLoading">
              获取行情
            </el-button>
          </div>

          <!-- 结果显示 -->
          <div v-if="boardQuoteResult" class="result-panel">
            <el-alert
              title="成功获取板块行情"
              type="success"
              :closable="false"
              style="margin-bottom: 20px;"
            />

            <!-- 行情卡片 -->
            <el-card class="quote-card">
              <template #header>
                <div class="card-header">
                  <span>{{ boardQuoteResult.code }} - {{ boardQuoteResult.name }}</span>
                </div>
              </template>

              <div class="quote-info">
                <div class="quote-item">
                  <label>最新价:</label>
                  <span class="price">{{ boardQuoteResult.price?.toFixed(2) }}</span>
                </div>

                <div class="quote-item">
                  <label>昨收:</label>
                  <span>{{ boardQuoteResult.last_close?.toFixed(2) }}</span>
                </div>

                <div class="quote-item">
                  <label>涨跌:</label>
                  <span :class="boardQuoteResult.change >= 0 ? 'rise' : 'fall'">
                    {{ boardQuoteResult.change?.toFixed(2) }}
                  </span>
                </div>

                <div class="quote-item">
                  <label>涨跌幅:</label>
                  <span :class="boardQuoteResult.change_percent >= 0 ? 'rise' : 'fall'">
                    {{ boardQuoteResult.change_percent?.toFixed(2) }}%
                  </span>
                </div>

                <div class="quote-item">
                  <label>成交量:</label>
                  <span>{{ boardQuoteResult.volume?.toLocaleString() }}</span>
                </div>

                <div class="quote-item">
                  <label>日期:</label>
                  <span>{{ boardQuoteResult.date }}</span>
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </el-tab-pane>

      <!-- 搜索板块测试 -->
      <el-tab-pane label="搜索板块" name="search">
        <div class="test-section">
          <h2>搜索板块测试</h2>

          <!-- 控制面板 -->
          <div class="control-panel">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索关键词 (如: 银行)"
              style="width: 200px; margin-right: 10px;"
              @keyup.enter="searchBoards"
            />

            <el-button type="primary" @click="searchBoards" :loading="searchLoading">
              搜索
            </el-button>
          </div>

          <!-- 结果显示 -->
          <div v-if="searchResult" class="result-panel">
            <el-alert
              :title="`找到 ${searchResult.count} 个匹配板块`"
              type="success"
              :closable="false"
              style="margin-bottom: 15px;"
            />

            <!-- 搜索结果 -->
            <el-table :data="searchResult.boards" style="width: 100%;" max-height="500">
              <el-table-column prop="code" label="代码" width="100" />
              <el-table-column prop="name" label="名称" width="200" />
              <el-table-column prop="category" label="分类" width="150" />
              <el-table-column label="数据状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.has_data ? 'success' : 'info'">
                    {{ row.has_data ? '有数据' : '无数据' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <!-- 股票K线测试 -->
      <el-tab-pane label="股票K线" name="stock-kline">
        <div class="test-section">
          <h2>股票K线测试（旧API - SmartSourceManager）</h2>

          <!-- 控制面板 -->
          <div class="control-panel">
            <el-input
              v-model="stockSymbol"
              placeholder="股票代码 (如: 600000)"
              style="width: 200px; margin-right: 10px;"
            />

            <el-date-picker
              v-model="stockStartDate"
              type="date"
              placeholder="开始日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 150px; margin-right: 10px;"
            />

            <el-date-picker
              v-model="stockEndDate"
              type="date"
              placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 150px; margin-right: 10px;"
            />

            <el-select v-model="stockFrequency" style="width: 100px; margin-right: 10px;">
              <el-option label="日线" value="day"></el-option>
              <el-option label="周线" value="week"></el-option>
              <el-option label="月线" value="month"></el-option>
            </el-select>

            <el-button type="primary" @click="loadStockKline" :loading="stockKlineLoading">
              获取K线
            </el-button>
          </div>

          <!-- 结果显示 -->
          <div v-if="stockKlineResult" class="result-panel">
            <el-alert
              :title="`成功获取 ${stockKlineResult.count} 条K线数据`"
              type="success"
              :closable="false"
              style="margin-bottom: 15px;"
            />

            <!-- 日期范围 -->
            <div v-if="stockKlineResult.date_range" class="stats">
              <el-tag type="info">{{ stockKlineResult.date_range.start }}</el-tag>
              <el-icon><ArrowRight /></el-icon>
              <el-tag type="info">{{ stockKlineResult.date_range.end }}</el-tag>
            </div>

            <!-- K线数据表格 -->
            <el-table :data="stockKlineResult.data.slice(0, 20)" style="width: 100%; margin-top: 15px;" max-height="400">
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="open" label="开盘" width="100" />
              <el-table-column prop="high" label="最高" width="100" />
              <el-table-column prop="low" label="最低" width="100" />
              <el-table-column prop="close" label="收盘" width="100" />
              <el-table-column prop="volume" label="成交量" width="120" />
            </el-table>

            <div v-if="stockKlineResult.count > 20" style="margin-top: 10px; text-align: center; color: #909399;">
              仅显示前20条，共 {{ stockKlineResult.count }} 条数据
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 新K线API测试（基于XtQuant） -->
      <el-tab-pane label="新K线API" name="new-kline-api">
        <div class="test-section">
          <h2>✨ 新K线API测试（基于XtQuant纯在线获取）</h2>
          <el-alert
            title="特性"
            type="success"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            <template #default>
              <ul style="margin: 0; padding-left: 20px;">
                <li>⚡ 纯在线获取，性能9-36ms</li>
                <li>📊 支持所有K线周期（月K、周K、日K、分钟K）</li>
                <li>💾 支持最大10000条数据</li>
                <li>🔴 数据实时，无需下载</li>
              </ul>
            </template>
          </el-alert>

          <!-- API健康检查 -->
          <div class="test-section">
            <h3>1. API健康检查</h3>
            <div class="control-panel">
              <el-button type="success" @click="testKlinePing" :loading="klinePingLoading">
                Ping K线服务
              </el-button>
            </div>

            <div v-if="klinePingResult" class="result-panel">
              <el-alert
                :title="`K线服务状态: ${klinePingResult.status}`"
                :description="`数据源: ${klinePingResult.data_source}`"
                type="success"
                :closable="false"
              />
            </div>
          </div>

          <!-- 获取支持的周期 -->
          <div class="test-section">
            <h3>2. 获取支持的周期</h3>
            <div class="control-panel">
              <el-button type="primary" @click="testGetPeriods" :loading="periodsLoading">
                获取支持周期
              </el-button>
            </div>

            <div v-if="periodsResult" class="result-panel">
              <el-alert
                :title="`共 ${periodsResult.data?.length || 0} 个支持的周期`"
                type="info"
                :closable="false"
                style="margin-bottom: 15px;"
              />

              <el-table :data="periodsResult.data" style="width: 100%;">
                <el-table-column prop="value" label="周期值" width="100" />
                <el-table-column prop="name" label="名称" width="100" />
                <el-table-column prop="name_en" label="英文名" width="100" />
                <el-table-column prop="description" label="描述" />
                <el-table-column prop="max_count" label="最大条数" width="100" />
                <el-table-column prop="performance_ms" label="性能" width="100" />
              </el-table>
            </div>
          </div>

          <!-- K线数据获取测试 -->
          <div class="test-section">
            <h3>3. 获取K线数据</h3>

            <!-- 控制面板 -->
            <div class="control-panel">
              <el-input
                v-model="newKlineSymbol"
                placeholder="股票代码 (如: 600519.SH)"
                style="width: 200px; margin-right: 10px;"
              />

              <el-select v-model="newKlinePeriod" style="width: 120px; margin-right: 10px;">
                <el-option label="月K" value="1mon"></el-option>
                <el-option label="周K" value="1w"></el-option>
                <el-option label="日K" value="1d"></el-option>
                <el-option label="60分钟" value="1h"></el-option>
                <el-option label="30分钟" value="30m"></el-option>
                <el-option label="15分钟" value="15m"></el-option>
                <el-option label="5分钟" value="5m"></el-option>
                <el-option label="1分钟" value="1m"></el-option>
              </el-select>

              <el-input-number
                v-model="newKlineCount"
                :min="1"
                :max="10000"
                placeholder="数据条数"
                style="width: 120px; margin-right: 10px;"
              />

              <el-button type="primary" @click="testNewKlineAPI" :loading="newKlineLoading">
                获取K线数据
              </el-button>

              <el-button @click="testNewKlineQuick('daily')" :loading="quickTestLoading">
                快速测试-日K
              </el-button>
            </div>

            <!-- 结果显示 -->
            <div v-if="newKlineResult" class="result-panel">
              <el-alert
                v-if="newKlineResult.code === 200"
                :title="`成功获取 ${newKlineResult.count} 条K线数据，耗时 ${newKlineResult.elapsed_ms}ms`"
                type="success"
                :closable="false"
                style="margin-bottom: 15px;"
              />
              <el-alert
                v-else
                :title="`获取失败: ${newKlineResult.message}`"
                type="error"
                :closable="false"
                style="margin-bottom: 15px;"
              />

              <!-- 性能指标 -->
              <div v-if="newKlineResult.code === 200" class="stats">
                <el-tag type="success" size="large">数据条数: {{ newKlineResult.count }}</el-tag>
                <el-tag type="primary" size="large">K线周期: {{ newKlineResult.period }}</el-tag>
                <el-tag :type="newKlineResult.elapsed_ms <= 36 ? 'success' : 'warning'" size="large">
                  耗时: {{ newKlineResult.elapsed_ms }}ms
                </el-tag>
              </div>

              <!-- K线数据表格 -->
              <el-table
                v-if="newKlineResult.data"
                :data="newKlineResult.data.slice(0, 10)"
                style="width: 100%; margin-top: 15px;"
                max-height="300"
              >
                <el-table-column prop="time" label="时间" width="180" />
                <el-table-column prop="open" label="开盘" width="100">
                  <template #default="{ row }">
                    {{ row.open?.toFixed(2) }}
                  </template>
                </el-table-column>
                <el-table-column prop="high" label="最高" width="100">
                  <template #default="{ row }">
                    {{ row.high?.toFixed(2) }}
                  </template>
                </el-table-column>
                <el-table-column prop="low" label="最低" width="100">
                  <template #default="{ row }">
                    {{ row.low?.toFixed(2) }}
                  </template>
                </el-table-column>
                <el-table-column prop="close" label="收盘" width="100">
                  <template #default="{ row }">
                    {{ row.close?.toFixed(2) }}
                  </template>
                </el-table-column>
                <el-table-column prop="volume" label="成交量" width="120" />
              </el-table>

              <div v-if="newKlineResult.count > 10" style="margin-top: 10px; text-align: center; color: #909399;">
                仅显示前10条，共 {{ newKlineResult.count }} 条数据
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- API文档链接 -->
    <div class="api-docs">
      <el-divider />
      <p>
        📖 查看完整文档:
        <el-link type="primary" href="/统一API快速开始.md" target="_blank">
          统一API快速开始指南
        </el-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'
import {
  getBoardList,
  getBoardKline,
  getBoardQuote,
  searchBoards,
  getStockKline,
  // 新K线API（基于XtQuant）
  getKlineData,
  getDailyKline,
  getWeeklyKline,
  getMonthlyKline,
  getSupportedPeriods,
  pingKline
} from '@/api/market'

// 当前激活的选项卡
const activeTab = ref('boards')

// ============ 板块列表 ============
const boardCategory = ref('')
const boardHasData = ref(true)
const boardListLoading = ref(false)
const boardListResult = ref<any>(null)

const boardsWithData = computed(() => {
  if (!boardListResult.value) return 0
  return boardList.value.boards.filter((b: any) => b.has_data).length
})

const boardList = computed(() => boardListResult.value || { boards: [] })

const loadBoardList = async () => {
  boardListLoading.value = true
  try {
    const response = await getBoardList(
      boardCategory.value || undefined,
      boardHasData.value
    )

    boardListResult.value = response

    ElMessage.success(`成功获取 ${response.count} 个板块`)
  } catch (error: any) {
    ElMessage.error(`获取失败: ${error.message}`)
    console.error('获取板块列表失败:', error)
  } finally {
    boardListLoading.value = false
  }
}

// ============ 板块K线 ============
const boardCode = ref('880001')
const boardStartDate = ref('')
const boardEndDate = ref('')
const boardLimit = ref(100)
const boardKlineLoading = ref(false)
const boardKlineResult = ref<any>(null)

const loadBoardKline = async () => {
  if (!boardCode.value) {
    ElMessage.warning('请输入板块代码')
    return
  }

  boardKlineLoading.value = true
  try {
    const response = await getBoardKline(
      boardCode.value,
      boardStartDate.value || undefined,
      boardEndDate.value || undefined,
      boardLimit.value
    )

    boardKlineResult.value = response

    ElMessage.success(`成功获取 ${response.count} 条K线数据`)
  } catch (error: any) {
    ElMessage.error(`获取失败: ${error.message}`)
    console.error('获取板块K线失败:', error)
  } finally {
    boardKlineLoading.value = false
  }
}

// ============ 板块行情 ============
const quoteBoardCode = ref('880001')
const boardQuoteLoading = ref(false)
const boardQuoteResult = ref<any>(null)

const loadBoardQuote = async () => {
  if (!quoteBoardCode.value) {
    ElMessage.warning('请输入板块代码')
    return
  }

  boardQuoteLoading.value = true
  try {
    const response = await getBoardQuote(quoteBoardCode.value)

    boardQuoteResult.value = response

    ElMessage.success('成功获取板块行情')
  } catch (error: any) {
    ElMessage.error(`获取失败: ${error.message}`)
    console.error('获取板块行情失败:', error)
  } finally {
    boardQuoteLoading.value = false
  }
}

// ============ 搜索板块 ============
const searchKeyword = ref('银行')
const searchLoading = ref(false)
const searchResult = ref<any>(null)

const searchBoards = async () => {
  if (!searchKeyword.value) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  searchLoading.value = true
  try {
    const response = await searchBoards(searchKeyword.value, 50)

    searchResult.value = response

    ElMessage.success(`找到 ${response.count} 个匹配板块`)
  } catch (error: any) {
    ElMessage.error(`搜索失败: ${error.message}`)
    console.error('搜索板块失败:', error)
  } finally {
    searchLoading.value = false
  }
}

// ============ 股票K线 ============
const stockSymbol = ref('600000')
const stockStartDate = ref('')
const stockEndDate = ref('')
const stockFrequency = ref<'day' | 'week' | 'month'>('day')
const stockKlineLoading = ref(false)
const stockKlineResult = ref<any>(null)

const loadStockKline = async () => {
  if (!stockSymbol.value) {
    ElMessage.warning('请输入股票代码')
    return
  }

  stockKlineLoading.value = true
  try {
    const response = await getStockKline(
      stockSymbol.value,
      stockStartDate.value || '2024-01-01',
      stockEndDate.value || '2024-12-31',
      stockFrequency.value
    )

    stockKlineResult.value = response

    ElMessage.success(`成功获取 ${response.count} 条K线数据`)
  } catch (error: any) {
    ElMessage.error(`获取失败: ${error.message}`)
    console.error('获取股票K线失败:', error)
  } finally {
    stockKlineLoading.value = false
  }
}

// ============ 新K线API测试（基于XtQuant） ============

// API健康检查
const klinePingResult = ref<any>(null)
const klinePingLoading = ref(false)

const testKlinePing = async () => {
  klinePingLoading.value = true
  try {
    const response = await pingKline()
    klinePingResult.value = response
    ElMessage.success('K线服务健康检查通过')
  } catch (error: any) {
    ElMessage.error(`健康检查失败: ${error.message}`)
    console.error('K线服务健康检查失败:', error)
  } finally {
    klinePingLoading.value = false
  }
}

// 获取支持的周期
const periodsResult = ref<any>(null)
const periodsLoading = ref(false)

const testGetPeriods = async () => {
  periodsLoading.value = true
  try {
    const response = await getSupportedPeriods()
    periodsResult.value = response
    ElMessage.success(`成功获取 ${response.data?.length || 0} 个支持的周期`)
  } catch (error: any) {
    ElMessage.error(`获取失败: ${error.message}`)
    console.error('获取支持周期失败:', error)
  } finally {
    periodsLoading.value = false
  }
}

// 获取K线数据
const newKlineSymbol = ref('600519.SH')
const newKlinePeriod = ref('1d')
const newKlineCount = ref(250)
const newKlineLoading = ref(false)
const quickTestLoading = ref(false)
const newKlineResult = ref<any>(null)

const testNewKlineAPI = async () => {
  if (!newKlineSymbol.value) {
    ElMessage.warning('请输入股票代码')
    return
  }

  newKlineLoading.value = true
  try {
    const response = await getKlineData(
      newKlineSymbol.value,
      newKlinePeriod.value as any,
      newKlineCount.value
    )
    newKlineResult.value = response

    if (response.code === 200) {
      ElMessage.success(`成功获取 ${response.count} 条K线数据，耗时 ${response.elapsed_ms}ms`)
    } else {
      ElMessage.warning(`获取失败: ${response.message}`)
    }
  } catch (error: any) {
    ElMessage.error(`获取失败: ${error.message}`)
    console.error('获取K线数据失败:', error)
  } finally {
    newKlineLoading.value = false
  }
}

// 快速测试 - 日K
const testNewKlineQuick = async (type: 'daily' | 'weekly' | 'monthly') => {
  quickTestLoading.value = true
  try {
    let response: any
    switch (type) {
      case 'daily':
        response = await getDailyKline(newKlineSymbol.value, 250)
        break
      case 'weekly':
        response = await getWeeklyKline(newKlineSymbol.value, 120)
        break
      case 'monthly':
        response = await getMonthlyKline(newKlineSymbol.value, 60)
        break
    }

    newKlineResult.value = response

    if (response.code === 200) {
      ElMessage.success(`✅ 成功获取 ${response.count} 条日K数据，耗时 ${response.elapsed_ms}ms`)
    } else {
      ElMessage.warning(`获取失败: ${response.message}`)
    }
  } catch (error: any) {
    ElMessage.error(`快速测试失败: ${error.message}`)
    console.error('快速测试失败:', error)
  } finally {
    quickTestLoading.value = false
  }
}
</script>

<style scoped>
.unified-api-test {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 28px;
  color: #409eff;
  margin-bottom: 10px;
}

.header p {
  color: #606266;
  font-size: 14px;
}

.test-section {
  padding: 20px;
}

.test-section h2 {
  margin-bottom: 20px;
  color: #303133;
}

.control-panel {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.result-panel {
  margin-top: 20px;
}

.stats {
  display: flex;
  gap: 10px;
  align-items: center;
}

.quote-card {
  max-width: 600px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.quote-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.quote-item {
  display: flex;
  align-items: center;
}

.quote-item label {
  font-weight: bold;
  margin-right: 10px;
  min-width: 80px;
}

.quote-item .price {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.quote-item .rise {
  color: #f56c6c;
}

.quote-item .fall {
  color: #67c23a;
}

.api-docs {
  text-align: center;
  margin-top: 30px;
  color: #909399;
}

.api-docs p {
  margin: 10px 0;
}
</style>
