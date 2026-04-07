# 数据管理组件

## 目录结构

```
data-management/
├── index.ts                      # 组件导出文件
├── OverviewCards.vue             # 概览卡片组件
├── StockCategories.vue           # 股票分类统计组件
├── StockCategoryCard.vue         # 单个分类卡片子组件
├── DataQualityMonitor.vue        # 数据质量监控组件
└── DataSourceManagement.vue      # 数据源管理组件
```

## 组件说明

### OverviewCards
显示系统概览信息，包括：
- 总数据量
- 数据完整度
- 活跃数据源
- 今日更新

**Props:** 无

**特性:**
- 自动从 API 加载数据
- 显示数据库详情（通达信、Qlib）
- 显示活跃数据源列表

---

### StockCategories
股票分类统计，显示不同板块的股票信息。

**Props:** 无

**包含子组件:** `StockCategoryCard`

**分类包括:**
- 沪深300
- 中证500
- 上证50
- 创业板指
- 科创50

---

### StockCategoryCard
单个股票分类卡片，显示：
- 分类名称和描述
- 股票数量
- 平均涨幅
- 性能图表
- 热门股票列表

---

### DataQualityMonitor
数据质量监控，实时监控各类数据的质量指标。

**监控指标包括:**
- 日线数据
- 分钟线数据
- 分笔数据
- 财务数据
- 指数数据
- 板块数据

---

### DataSourceManagement
数据源管理，配置和监控各个数据源。

**功能包括:**
- 启用/禁用数据源
- 测试连接
- 配置数据源
- 查看数据源状态
- 监控错误数量

---

## API 依赖

所有组件都使用以下后端 API：

1. `/api/v1/data-management/database/stats` - 数据库统计
2. `/api/v1/data-management/categories/stats` - 分类统计
3. `/api/v1/data-management/sources/list` - 数据源列表

## 使用示例

```vue
<template>
  <div>
    <OverviewCards />
    <StockCategories />
    <DataQualityMonitor />
    <DataSourceManagement />
  </div>
</template>

<script setup lang="ts">
import OverviewCards from '@/components/data-management/OverviewCards.vue'
import StockCategories from '@/components/data-management/StockCategories.vue'
import DataQualityMonitor from '@/components/data-management/DataQualityMonitor.vue'
import DataSourceManagement from '@/components/data-management/DataSourceManagement.vue'
</script>
```

