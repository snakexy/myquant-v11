<template>
  <div class="layer-navigation">
    <!-- 面包屑导航 -->
    <div class="breadcrumb-container">
      <n-breadcrumb separator=">">
        <n-breadcrumb-item
          v-for="(item, index) in breadcrumbItems"
          :key="index"
          :clickable="index < breadcrumbItems.length - 1"
          @click="handleBreadcrumbClick(item, index)"
        >
          <n-icon :component="item.icon" />
          {{ item.label }}
        </n-breadcrumb-item>
      </n-breadcrumb>
    </div>
    
    <!-- 层级切换器 -->
    <div class="layer-switcher">
      <n-space>
        <n-button
          v-for="layer in availableLayers"
          :key="layer.level"
          :type="currentLayer === layer.level ? 'primary' : 'default'"
          :size="small"
          @click="switchToLayer(layer.level)"
          :disabled="!isLayerAccessible(layer)"
        >
          <n-icon :component="layer.icon" />
          {{ layer.name }}
        </n-button>
      </n-space>
    </div>
    
    <!-- 快捷操作 -->
    <div class="quick-actions">
      <n-space>
        <!-- 工程师工具箱快捷入口 -->
        <n-button
          v-if="hasEngineerAccess"
          type="tertiary"
          size="small"
          @click="openEngineerToolbox"
          class="engineer-toolbox-btn"
        >
          <n-icon :component="ToolsIcon" />
          工程师工具箱
        </n-button>
        
        <!-- 快捷键提示 -->
        <n-tooltip trigger="hover" placement="bottom">
          <template #trigger>
            <n-button type="tertiary" size="small" text>
              <n-icon :component="HelpIcon" />
            </n-button>
          </template>
          <div class="shortcut-hints">
            <div class="hint-item">Alt+1-3: 切换层级</div>
            <div class="hint-item">Alt+E: 打开工程师工具箱</div>
            <div class="hint-item">Alt+H: 返回首页</div>
          </div>
        </n-tooltip>
      </n-space>
    </div>
    
    <!-- 层级进度指示器 -->
    <div class="layer-progress">
      <n-steps :current="currentLayer" :size="small" status="process">
        <n-step
          v-for="layer in layerConfigs"
          :key="layer.level"
          :title="layer.name"
          :description="layer.description"
        />
      </n-steps>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { functionModules, layerConfigs, engineerToolbox, getLayerConfig, getAccessibleLayers } from '@/configs/functionConfig'
import {
  GridOutline as DashboardIcon,
  ServerOutline as ArchitectureIcon,
  DesktopOutline as MonitorIcon,
  BuildOutline as ToolsIcon,
  HelpOutline as HelpIcon,
  HomeOutline as HomeIcon
} from '@vicons/ionicons5'

// 路由和状态
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 当前状态
const currentLayer = ref(1)
const currentFunctionId = ref('')

// 计算属性
const breadcrumbItems = computed(() => {
  const items = [
    { label: '首页', path: '/', icon: HomeIcon }
  ]

  if (currentFunctionId.value) {
    const module = functionModules.find(m => m.id === currentFunctionId.value)
    if (module) {
      items.push({
        label: module.name,
        path: `/function/${currentFunctionId.value}`,
        icon: undefined
      })
    }

    // 添加层级信息
    if (currentLayer.value > 1) {
      const layerConfig = getLayerConfig(currentFunctionId.value, currentLayer.value)
      if (layerConfig) {
        items.push({
          label: layerConfig.name,
          path: layerConfig.path,
          icon: undefined
        })
      }
    }
  }

  return items
})

const availableLayers = computed(() => {
  if (!currentFunctionId.value) return []
  
  const userPermissions = userStore.permissions || []
  return getAccessibleLayers(currentFunctionId.value, userPermissions)
})

const hasEngineerAccess = computed(() => {
  const userPermissions = userStore.permissions || []
  return userPermissions.some(perm => ['admin', 'developer'].includes(perm))
})

// 方法
const handleBreadcrumbClick = (item: any, index: number) => {
  if (index < breadcrumbItems.value.length - 1) {
    router.push(item.path)
  }
}

const switchToLayer = (level: number) => {
  if (!currentFunctionId.value) return
  
  const layerConfig = getLayerConfig(currentFunctionId.value, level)
  if (layerConfig) {
    currentLayer.value = level
    router.push(layerConfig.path)
  }
}

const isLayerAccessible = (layer: any) => {
  return availableLayers.value.some(l => l.level === layer.level)
}

const openEngineerToolbox = () => {
  router.push('/engineer-toolbox')
}

// 快捷键处理
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.altKey) {
    switch (event.key) {
      case '1':
      case '2':
      case '3':
        const layer = parseInt(event.key)
        if (layer <= layerConfigs.length) {
          switchToLayer(layer)
        }
        break
      case 'e':
      case 'E':
        if (hasEngineerAccess.value) {
          openEngineerToolbox()
        }
        break
      case 'h':
      case 'H':
        router.push('/')
        break
    }
  }
}

// 监听路由变化
watch(() => route.path, (newPath) => {
  // 解析当前功能ID和层级
  const functionMatch = newPath.match(/^\/function\/([^\/]+)/)
  if (functionMatch) {
    currentFunctionId.value = functionMatch[1]
    
    // 解析层级
    if (newPath.includes('/architecture')) {
      currentLayer.value = 2
    } else if (newPath.includes('/monitoring')) {
      currentLayer.value = 3
    } else {
      currentLayer.value = 1
    }
  } else {
    currentFunctionId.value = ''
    currentLayer.value = 1
  }
}, { immediate: true })

// 生命周期
onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<style lang="scss" scoped>
.layer-navigation {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: rgba(var(--surface-color), 0.8);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-lg);
  border: 1px solid rgba(var(--border-color), 0.2);
  
  .breadcrumb-container {
    .n-breadcrumb {
      :deep(.n-breadcrumb-item) {
        .n-icon {
          margin-right: var(--spacing-1);
        }
        
        &:hover {
          color: var(--primary-color);
        }
      }
    }
  }
  
  .layer-switcher {
    .n-button {
      transition: all 0.3s ease;
      
      &:hover:not(.n-button--disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(var(--primary-color), 0.3);
      }
      
      .n-icon {
        margin-right: var(--spacing-1);
      }
    }
  }
  
  .quick-actions {
    .engineer-toolbox-btn {
      background: linear-gradient(135deg, var(--accent-color), var(--secondary-color));
      border: none;
      color: white;
      
      &:hover {
        background: linear-gradient(135deg, var(--accent-color), var(--secondary-color));
        filter: brightness(0.9);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(var(--accent-color), 0.4);
      }
    }
    
    .shortcut-hints {
      .hint-item {
        padding: var(--spacing-1) 0;
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
        
        &:not(:last-child) {
          border-bottom: 1px solid rgba(var(--border-color), 0.2);
        }
      }
    }
  }
  
  .layer-progress {
    :deep(.n-steps) {
      .n-step {
        .n-step-content {
          .n-step-content__title {
            font-size: var(--font-size-sm);
            font-weight: 500;
          }
          
          .n-step-content__description {
            font-size: var(--font-size-xs);
            color: var(--text-secondary);
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .layer-navigation {
    .layer-progress {
      :deep(.n-steps) {
        .n-step-content__description {
          display: none;
        }
      }
    }
  }
  
  .quick-actions {
    .shortcut-hints {
      display: none;
    }
  }
}
</style>