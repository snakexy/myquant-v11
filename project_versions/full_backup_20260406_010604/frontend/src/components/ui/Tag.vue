<template>
  <span class="quant-tag" :class="tagClass" :style="tagStyle">
    <slot>{{ label }}</slot>
    <n-icon
      v-if="closable"
      class="quant-tag__close"
      @click="handleClose"
    >
      <CloseOutline />
    </n-icon>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NIcon } from 'naive-ui'
import { CloseOutline } from '@vicons/ionicons5'
import type { TagProps } from '@/types/components'

const props = withDefaults(defineProps<TagProps>(), {
  type: 'default',
  effect: 'light',
  closable: false,
  size: 'medium',
  hit: false
})

const emit = defineEmits<{
  close: []
}>()

const tagClass = computed(() => [
  `quant-tag--${props.type}`,
  `quant-tag--${props.effect}`,
  `quant-tag--${props.size}`,
  {
    'is-hit': props.hit
  }
])

const tagStyle = computed(() => {
  if (props.color) {
    return {
      backgroundColor: props.effect === 'dark' ? props.color : undefined,
      borderColor: props.color,
      color: props.effect === 'dark' ? 'white' : props.color
    }
  }
  return {}
})

const handleClose = (event: MouseEvent) => {
  event.stopPropagation()
  emit('close')
}
</script>

<style lang="scss" scoped>
.quant-tag {
  display: inline-flex;
  align-items: center;
  padding: 0 var(--spacing-2);
  height: 22px;
  line-height: 20px;
  font-size: var(--font-size-sm);
  border-radius: var(--border-radius-base);
  border: 1px solid transparent;
  white-space: nowrap;
  
  &__close {
    margin-left: var(--spacing-1);
    cursor: pointer;
    opacity: 0.7;
    transition: opacity var(--transition-duration-base) var(--transition-timing-function-base);
    
    &:hover {
      opacity: 1;
    }
  }
  
  &--small {
    height: 18px;
    line-height: 16px;
    padding: 0 var(--spacing-1);
    font-size: var(--font-size-xs);
  }
  
  &--large {
    height: 26px;
    line-height: 24px;
    padding: 0 var(--spacing-3);
    font-size: var(--font-size-base);
  }
  
  &--primary {
    &.quant-tag--dark {
      background-color: var(--primary-color);
      border-color: var(--primary-color);
      color: white;
    }
    
    &.quant-tag--light {
      background-color: rgba(var(--primary-color), 0.1);
      border-color: var(--primary-color);
      color: var(--primary-color);
    }
    
    &.quant-tag--plain {
      background-color: transparent;
      border-color: var(--primary-color);
      color: var(--primary-color);
    }
  }
  
  &--success {
    &.quant-tag--dark {
      background-color: var(--success-color);
      border-color: var(--success-color);
      color: white;
    }
    
    &.quant-tag--light {
      background-color: rgba(var(--success-color), 0.1);
      border-color: var(--success-color);
      color: var(--success-color);
    }
    
    &.quant-tag--plain {
      background-color: transparent;
      border-color: var(--success-color);
      color: var(--success-color);
    }
  }
  
  &--info {
    &.quant-tag--dark {
      background-color: var(--info-color);
      border-color: var(--info-color);
      color: white;
    }
    
    &.quant-tag--light {
      background-color: rgba(var(--info-color), 0.1);
      border-color: var(--info-color);
      color: var(--info-color);
    }
    
    &.quant-tag--plain {
      background-color: transparent;
      border-color: var(--info-color);
      color: var(--info-color);
    }
  }
  
  &--warning {
    &.quant-tag--dark {
      background-color: var(--warning-color);
      border-color: var(--warning-color);
      color: white;
    }
    
    &.quant-tag--light {
      background-color: rgba(var(--warning-color), 0.1);
      border-color: var(--warning-color);
      color: var(--warning-color);
    }
    
    &.quant-tag--plain {
      background-color: transparent;
      border-color: var(--warning-color);
      color: var(--warning-color);
    }
  }
  
  &--danger {
    &.quant-tag--dark {
      background-color: var(--danger-color);
      border-color: var(--danger-color);
      color: white;
    }
    
    &.quant-tag--light {
      background-color: rgba(var(--danger-color), 0.1);
      border-color: var(--danger-color);
      color: var(--danger-color);
    }
    
    &.quant-tag--plain {
      background-color: transparent;
      border-color: var(--danger-color);
      color: var(--danger-color);
    }
  }
  
  &--default {
    &.quant-tag--dark {
      background-color: var(--text-primary);
      border-color: var(--text-primary);
      color: white;
    }
    
    &.quant-tag--light {
      background-color: var(--bg-color-secondary);
      border-color: var(--border-color)-base;
      color: var(--text-primary);
    }
    
    &.quant-tag--plain {
      background-color: transparent;
      border-color: var(--border-color)-base;
      color: var(--text-primary);
    }
  }
  
  &.is-hit {
    border-width: 2px;
  }
}
</style>