<template>
  <div :class="cardClass" :style="cardStyle">
    <!-- 头部 -->
    <div v-if="$slots.header || title" class="card-header">
      <slot name="header">
        <div class="card-title">
          <span v-if="icon" class="card-icon">
            <component :is="icon" />
          </span>
          <span>{{ title }}</span>
          <span v-if="subtitle" class="card-subtitle">{{ subtitle }}</span>
        </div>
        <div v-if="$slots.extra" class="card-extra">
          <slot name="extra"></slot>
        </div>
      </slot>
    </div>

    <!-- 内容 -->
    <div class="card-body" :class="{ 'no-padding': noPadding }">
      <slot></slot>
    </div>

    <!-- 底部 -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'

interface Props {
  title?: string
  subtitle?: string
  icon?: Component
  shadow?: 'never' | 'hover' | 'always'
  bordered?: boolean
  noPadding?: boolean
  hoverable?: boolean
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  shadow: 'hover',
  bordered: true,
  noPadding: false,
  hoverable: false,
  clickable: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const cardClass = computed(() => {
  return [
    'base-card',
    `shadow-${props.shadow}`,
    {
      'bordered': props.bordered,
      'hoverable': props.hoverable,
      'clickable': props.clickable
    }
  ]
})

const cardStyle = computed(() => {
  return {}
})

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.base-card {
  background: $bg-surface;
  border-radius: $radius-lg;
  overflow: hidden;
  transition: all $transition-base;

  &.bordered {
    border: 1px solid $border-light;
  }

  &.hoverable:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-lg;
  }

  &.clickable {
    cursor: pointer;

    &:hover {
      border-color: $primary-color;
    }
  }

  &.shadow-never {
    box-shadow: none;
  }

  &.shadow-hover {
    box-shadow: $shadow-sm;

    &:hover {
      box-shadow: $shadow-md;
    }
  }

  &.shadow-always {
    box-shadow: $shadow-md;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
  border-bottom: 1px solid $border-light;

  .card-title {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    font-size: $font-md;
    font-weight: 600;
    color: $text-primary;

    .card-icon {
      display: inline-flex;
      color: $primary-color;
    }

    .card-subtitle {
      font-size: $font-sm;
      font-weight: 400;
      color: $text-muted;
      margin-left: $spacing-xs;
    }
  }

  .card-extra {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
  }
}

.card-body {
  padding: $spacing-lg;

  &.no-padding {
    padding: 0;
  }
}

.card-footer {
  padding: $spacing-lg;
  border-top: 1px solid $border-light;
}
</style>
