<template>
  <div class="backtest-view">
    <div class="page-header">
      <h2>策略回测</h2>
      <p>量化策略历史回测与性能分析</p>
    </div>

    <div class="backtest-content">
      <el-card class="config-card">
        <template #header>
          <span>策略配置</span>
        </template>

        <el-form :model="config" label-width="120px">
          <el-form-item label="策略类型">
            <el-select v-model="config.strategy" placeholder="选择策略">
              <el-option label="双均线策略" value="ma_cross" />
              <el-option label="布林带策略" value="boll" />
              <el-option label="MACD策略" value="macd" />
              <el-option label="RSI策略" value="rsi" />
            </el-select>
          </el-form-item>

          <el-form-item label="股票代码">
            <el-input v-model="config.symbol" placeholder="例如: 600519" />
          </el-form-item>

          <el-form-item label="时间范围">
            <el-date-picker
              v-model="config.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            />
          </el-form-item>

          <el-form-item label="初始资金">
            <el-input-number v-model="config.initialCapital" :min="10000" :max="10000000" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="runBacktest" :loading="loading">
              开始回测
            </el-button>
            <el-button @click="resetConfig">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card v-if="result" class="result-card">
        <template #header>
          <span>回测结果</span>
        </template>

        <div class="result-stats">
          <div class="stat-item">
            <span class="label">总收益率</span>
            <span class="value" :class="getChangeClass(result.totalReturn)">
              {{ result.totalReturn }}%
            </span>
          </div>
          <div class="stat-item">
            <span class="label">年化收益率</span>
            <span class="value" :class="getChangeClass(result.annualReturn)">
              {{ result.annualReturn }}%
            </span>
          </div>
          <div class="stat-item">
            <span class="label">最大回撤</span>
            <span class="value down">
              {{ result.maxDrawdown }}%
            </span>
          </div>
          <div class="stat-item">
            <span class="label">夏普比率</span>
            <span class="value">
              {{ result.sharpeRatio }}
            </span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const config = ref({
  strategy: 'ma_cross',
  symbol: '600519',
  dateRange: [],
  initialCapital: 100000
})

const result = ref(null)
const loading = ref(false)

const runBacktest = () => {
  loading.value = true
  // TODO: 实现回测逻辑
  setTimeout(() => {
    result.value = {
      totalReturn: 45.6,
      annualReturn: 22.8,
      maxDrawdown: -12.5,
      sharpeRatio: 1.85
    }
    loading.value = false
  }, 2000)
}

const resetConfig = () => {
  config.value = {
    strategy: 'ma_cross',
    symbol: '600519',
    dateRange: [],
    initialCapital: 100000
  }
  result.value = null
}

const getChangeClass = (value: number) => {
  return value > 0 ? 'up' : value < 0 ? 'down' : ''
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.backtest-view {
  padding: $spacing-lg;

  .page-header {
    margin-bottom: $spacing-xl;

    h2 {
      margin: 0 0 $spacing-sm 0;
      font-size: $font-2xl;
      color: $text-primary;
    }

    p {
      margin: 0;
      color: $text-muted;
    }
  }

  .backtest-content {
    display: grid;
    gap: $spacing-lg;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  }

  .result-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: $spacing-lg;

    .stat-item {
      display: flex;
      flex-direction: column;
      gap: $spacing-xs;
      padding: $spacing-lg;
      background: $bg-elevated;
      border-radius: $radius-md;

      .label {
        font-size: $font-sm;
        color: $text-muted;
      }

      .value {
        font-size: $font-xl;
        font-weight: 600;

        &.up {
          color: $color-up;
        }

        &.down {
          color: $color-down;
        }
      }
    }
  }
}
</style>
