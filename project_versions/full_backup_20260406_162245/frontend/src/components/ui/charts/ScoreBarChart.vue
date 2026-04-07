<template>
  <div class="score-bar-chart">
    <!-- 头部：标题 + 评分 -->
    <div class="score-header">
      <div class="score-title">
        <svg class="icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
        {{ title }}
      </div>
      <div class="score-total">
        <div class="score-stars">
          <svg v-for="i in 5" :key="i" class="star-lg" viewBox="0 0 24 24" :fill="i <= starCount ? scoreColor : '#2a2e39'">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </div>
        <span class="score-number" :style="{ color: scoreColor }">{{ score }}</span>
        <span class="score-grade" :style="{ background: `${scoreColor}20`, color: scoreColor }">{{ computedGrade }}</span>
      </div>
    </div>
    <!-- 进度条 -->
    <div class="bar-chart">
      <div v-for="(item, index) in data" :key="index" class="bar-item">
        <span class="bar-label">{{ item.name }}</span>
        <div class="bar-track">
          <div
            class="bar-fill"
            :class="item.color || 'blue'"
            :style="{ width: item.value + '%' }"
          >{{ item.value }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  score?: number
  grade?: string
  data?: { name: string; value: number; color?: string }[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '综合评分',
  score: 85,
  grade: '',
  data: () => [
    { name: '收益', value: 85, color: 'red' },
    { name: '风险调整', value: 72, color: 'blue' },
    { name: '稳定性', value: 90, color: 'purple' },
    { name: '容量', value: 65, color: 'cyan' }
  ]
})

// 等级：如果传入则使用传入的值，否则根据分数计算
const computedGrade = computed(() => {
  if (props.grade) return props.grade
  const s = props.score
  if (s >= 95) return 'A+'
  if (s >= 85) return 'A'
  if (s >= 75) return 'B+'
  if (s >= 65) return 'B'
  if (s >= 55) return 'C+'
  if (s >= 45) return 'C'
  return 'D'
})

// 计算星星数量（基于5星制）
const starCount = computed(() => {
  return Math.round(props.score / 20)
})

// 根据分数获取颜色
const scoreColor = computed(() => {
  const s = props.score
  if (s > 100) return '#8b5cf6'   // 紫色
  if (s >= 80) return '#ef5350'    // 红色 - 优秀
  if (s >= 60) return '#ff9800'    // 橙色 - 良好
  if (s >= 40) return '#2962ff'    // 蓝色 - 一般
  return '#26a69a'                   // 绿色 - 较差
})
</script>

<style lang="scss" scoped>
.score-bar-chart {
  width: 100%;
  height: 100%;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.score-title {
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary, #d1d4dc);
}

.icon-md {
  width: 18px;
  height: 18px;
  color: #ff9800;
}

.score-total {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-stars {
  display: flex;
  gap: 4px;
}

.star-lg {
  width: 20px;
  height: 20px;
}

.score-number {
  font-size: 36px;
  font-weight: 700;
}

.score-grade {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 700;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  min-width: 60px;
  font-size: 11px;
  color: var(--text-secondary, #787b86);
}

.bar-track {
  flex: 1;
  height: 24px;
  background: var(--bg-tertiary, #2a2e39);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding-left: 10px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  transition: width 0.5s;

  &.red {
    background: linear-gradient(90deg, #ef5350, #ff8a80);
  }

  &.blue {
    background: linear-gradient(90deg, #2962ff, #5c95ff);
  }

  &.purple {
    background: linear-gradient(90deg, #9c27b0, #ba68c8);
  }

  &.cyan {
    background: linear-gradient(90deg, #00bcd4, #4dd0e1);
  }

  &.green {
    background: linear-gradient(90deg, #26a69a, #80cbc4);
  }

  &.orange {
    background: linear-gradient(90deg, #ff9800, #ffcc80);
  }
}
</style>
