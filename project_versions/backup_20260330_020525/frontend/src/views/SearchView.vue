<template>
  <div class="search-view">
    <div class="page-header">
      <h2>股票搜索</h2>
      <p>搜索股票代码、名称或拼音缩写</p>
    </div>

    <div class="search-content">
      <el-card>
        <el-input
          v-model="keyword"
          placeholder="输入股票代码、名称或拼音缩写..."
          size="large"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <div v-if="results.length > 0" class="search-results">
          <div
            v-for="item in results"
            :key="item.symbol"
            class="result-item"
            @click="goToStock(item.symbol)"
          >
            <div class="stock-info">
              <span class="stock-code">{{ item.symbol }}</span>
              <span class="stock-name">{{ item.name }}</span>
            </div>
            <el-icon class="arrow-icon"><ArrowRight /></el-icon>
          </div>
        </div>

        <div v-else-if="keyword && !loading" class="no-results">
          <el-empty description="未找到相关股票" />
        </div>

        <div v-if="!keyword" class="search-hints">
          <p>搜索提示：</p>
          <ul>
            <li>输入股票代码，如：600519</li>
            <li>输入股票名称，如：茅台</li>
            <li>输入拼音缩写，如：gzmt</li>
          </ul>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Search, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const keyword = ref('')
const results = ref<any[]>([])
const loading = ref(false)

const handleSearch = async (value: string) => {
  if (!value) {
    results.value = []
    return
  }

  loading.value = true

  // TODO: 实际搜索逻辑
  // 模拟搜索结果
  setTimeout(() => {
    if (value.includes('600519') || value.toLowerCase().includes('maotai') || value.toLowerCase().includes('gzmt')) {
      results.value = [
        { symbol: '600519', name: '贵州茅台' }
      ]
    } else if (value.includes('000858') || value.toLowerCase().includes('wly')) {
      results.value = [
        { symbol: '000858', name: '五粮液' }
      ]
    } else {
      results.value = []
    }
    loading.value = false
  }, 300)
}

const goToStock = (symbol: string) => {
  router.push(`/stock?symbol=${symbol}`)
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.search-view {
  padding: $spacing-lg;
  max-width: 800px;
  margin: 0 auto;

  .page-header {
    margin-bottom: $spacing-xl;
    text-align: center;

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

  .search-results {
    margin-top: $spacing-lg;

    .result-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-md $spacing-lg;
      margin-bottom: $spacing-sm;
      background: $bg-elevated;
      border: 1px solid $border-light;
      border-radius: $radius-md;
      cursor: pointer;
      transition: all $transition-base;

      &:hover {
        background: $bg-hover;
        border-color: $primary-color;
      }

      .stock-info {
        display: flex;
        gap: $spacing-md;
        align-items: center;

        .stock-code {
          font-family: monospace;
          font-weight: 600;
          color: $primary-color;
        }

        .stock-name {
          color: $text-primary;
        }
      }

      .arrow-icon {
        color: $text-muted;
      }
    }
  }

  .search-hints {
    margin-top: $spacing-lg;
    padding: $spacing-lg;
    background: $bg-elevated;
    border-radius: $radius-md;

    p {
      margin: 0 0 $spacing-md 0;
      font-weight: 600;
      color: $text-primary;
    }

    ul {
      margin: 0;
      padding-left: $spacing-lg;

      li {
        margin-bottom: $spacing-xs;
        color: $text-secondary;
      }
    }
  }
}
</style>
