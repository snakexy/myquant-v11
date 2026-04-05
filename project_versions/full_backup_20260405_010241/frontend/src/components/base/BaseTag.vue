<template>
  <span :class="tagClass" @click="handleClick">
    <span v-if="$slots.icon" class="tag-icon">
      <slot name="icon"></slot>
    </span>
    <span v-if="$slots.default" class="tag-content">
      <slot></slot>
    </span>
    <span v-if="closable" class="tag-close" @click.stop="handleClose">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type TagType = 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'up' | 'down' | 'flat'
type TagSize = 'small' | 'medium' | 'large'

interface Props {
  type?: TagType
  size?: TagSize
  effect?: 'dark' | 'light' | 'plain'
  closable?: boolean
  round?: boolean
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'medium',
  effect: 'light',
  closable: false,
  round: false,
  clickable: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
  close: [event: MouseEvent]
}>()

const tagClass = computed(() => {
  return [
    'base-tag',
    `tag-${props.type}`,
    `tag-${props.size}`,
    `tag-${props.effect}`,
    {
      'tag-round': props.round,
      'tag-clickable': props.clickable
    }
  ]
})

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}

const handleClose = (event: MouseEvent) => {
  emit('close', event)
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.base-tag {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-xs $spacing-sm;
  font-size: $font-xs;
  font-weight: 500;
  line-height: 1;
  white-space: nowrap;
  border-radius: $radius-sm;
  transition: all $transition-base;

  &.tag-round {
    border-radius: $radius-full;
  }

  &.tag-clickable {
    cursor: pointer;

    &:hover {
      opacity: 0.8;
    }
  }

  // 尺寸
  &.tag-small {
    padding: 2px $spacing-xs;
    font-size: 10px;
  }

  &.tag-medium {
    padding: $spacing-xs $spacing-sm;
    font-size: $font-xs;
  }

  &.tag-large {
    padding: $spacing-sm $spacing-md;
    font-size: $font-sm;
  }

  // 涨跌颜色
  &.tag-up {
    background: rgba($color-up, 0.1);
    color: $color-up;
    border: 1px solid rgba($color-up, 0.2);

    &.tag-dark {
      background: $color-up;
      color: white;
    }

    &.tag-plain {
      background: transparent;
      border: 1px solid $color-up;
      color: $color-up;
    }
  }

  &.tag-down {
    background: rgba($color-down, 0.1);
    color: $color-down;
    border: 1px solid rgba($color-down, 0.2);

    &.tag-dark {
      background: $color-down;
      color: white;
    }

    &.tag-plain {
      background: transparent;
      border: 1px solid $color-down;
      color: $color-down;
    }
  }

  &.tag-flat {
    background: rgba($color-flat, 0.1);
    color: $color-flat;
    border: 1px solid rgba($color-flat, 0.2);

    &.tag-dark {
      background: $color-flat;
      color: white;
    }

    &.tag-plain {
      background: transparent;
      border: 1px solid $color-flat;
      color: $color-flat;
    }
  }

  // 类型颜色
  &.tag-primary {
    background: rgba($primary-color, 0.1);
    color: $primary-color;
    border: 1px solid rgba($primary-color, 0.2);

    &.tag-dark {
      background: $primary-color;
      color: white;
    }

    &.tag-plain {
      background: transparent;
      border: 1px solid $primary-color;
      color: $primary-color;
    }
  }

  &.tag-success {
    background: rgba($success-color, 0.1);
    color: $success-color;
    border: 1px solid rgba($success-color, 0.2);

    &.tag-dark {
      background: $success-color;
      color: white;
    }

    &.tag-plain {
      background: transparent;
      border: 1px solid $success-color;
      color: $success-color;
    }
  }

  &.tag-warning {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
    border: 1px solid rgba($warning-color, 0.2);

    &.tag-dark {
      background: $warning-color;
      color: white;
    }

    &.tag-plain {
      background: transparent;
      border: 1px solid $warning-color;
      color: $warning-color;
    }
  }

  &.tag-danger {
    background: rgba($error-color, 0.1);
    color: $error-color;
    border: 1px solid rgba($error-color, 0.2);

    &.tag-dark {
      background: $error-color;
      color: white;
    }

    &.tag-plain {
      background: transparent;
      border: 1px solid $error-color;
      color: $error-color;
    }
  }

  &.tag-info {
    background: rgba($info-color, 0.1);
    color: $info-color;
    border: 1px solid rgba($info-color, 0.2);

    &.tag-dark {
      background: $info-color;
      color: white;
    }

    &.tag-plain {
      background: transparent;
      border: 1px solid $info-color;
      color: $info-color;
    }
  }
}

.tag-icon {
  display: inline-flex;
  align-items: center;
}

.tag-content {
  display: inline-flex;
  align-items: center;
}

.tag-close {
  display: inline-flex;
  align-items: center;
  margin-left: $spacing-xs;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity $transition-fast;

  &:hover {
    opacity: 1;
  }

  svg {
    width: 12px;
    height: 12px;
  }
}
</style>
