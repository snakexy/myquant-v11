<template>
  <div class="score-card" :style="cardStyle">
    <div class="score-card-header">
      <span class="score-card-label" :style="{ color: qualityColor }">{{ label }}</span>
    </div>
    <div class="score-card-value" :style="{ color: qualityColor }">
      {{ displayValue }}
    </div>
    <div class="score-card-rating">
      <svg
        v-for="i in 5"
        :key="i"
        class="score-card-star"
        :style="{ color: i <= starCount ? qualityColor : 'rgba(255,255,255,0.2)' }"
        viewBox="0 0 24 24"
        fill="currentColor"
      >
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
      </svg>
    </div>
    <!-- 字母等级 + 进度条 -->
    <div class="score-card-grade-bar">
      <span class="score-card-grade" :style="{ color: qualityColor }">{{ letterGrade }}</span>
      <div class="score-card-bar">
        <div
          class="score-card-bar-fill"
          :style="{ width: `${Math.min(score, 100)}%`, background: qualityColor }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label: string
  score: number
  showBar?: boolean
  suffix?: string
  decimals?: number
}

const props = withDefaults(defineProps<Props>(), {
  showBar: true,
  suffix: '',
  decimals: 0
})

// 根据分数获取质量颜色
const getFactorQualityColor = (score: number): string => {
  if (score > 100) return '#8b5cf6'   // 紫色
  if (score >= 80) return '#ef5350'    // 红色 - 优秀
  if (score >= 60) return '#ff9800'    // 橙色 - 良好
  if (score >= 40) return '#2962ff'    // 蓝色 - 一般
  return '#26a69a'                      // 绿色 - 较差
}

// 获取字母等级
const getLetterGrade = (score: number): string => {
  if (score >= 95) return 'A+'
  if (score >= 85) return 'A'
  if (score >= 75) return 'B+'
  if (score >= 65) return 'B'
  if (score >= 55) return 'C+'
  if (score >= 45) return 'C'
  if (score >= 35) return 'D'
  return 'F'
}

// 计算显示值
const displayValue = computed(() => {
  const value = props.score.toFixed(props.decimals)
  return props.suffix ? `${value}${props.suffix}` : value
})

// 质量颜色
const qualityColor = computed(() => getFactorQualityColor(props.score))

// 字母等级
const letterGrade = computed(() => getLetterGrade(props.score))

// 计算星星数量 (5星评级)
const starCount = computed(() => {
  if (props.score >= 90) return 5
  if (props.score >= 70) return 4
  if (props.score >= 50) return 3
  if (props.score >= 30) return 2
  return 1
})

// 卡片样式 - 动态背景和边框颜色
const cardStyle = computed(() => {
  const color = qualityColor.value
  return {
    background: `linear-gradient(135deg, ${color}15 0%, rgba(30, 34, 45, 0.9) 100%)`,
    borderColor: `${color}4d`
  }
})
</script>

<style lang="scss" scoped>
.score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  border: 1px solid;
  border-radius: 16px;
  transition: all 0.3s ease;
  min-width: 140px;

  &:hover {
    transform: translateY(-2px);
  }
}

.score-card-header {
  margin-bottom: 8px;
}

.score-card-label {
  font-size: 14px;
  font-weight: 500;
}

.score-card-value {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
}

.score-card-rating {
  display: flex;
  gap: 2px;
  margin-top: 8px;
}

.score-card-star {
  width: 14px;
  height: 14px;
}

.score-card-grade-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
  width: 100%;
}

.score-card-grade {
  font-size: 20px;
  font-weight: 700;
  min-width: 28px;
}

.score-card-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.score-card-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}
</style>
