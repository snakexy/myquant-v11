<template>
  <div class="sector-search-box">
    <el-input
      v-model="searchText"
      :placeholder="placeholder"
      clearable
      @input="handleSearchInput"
      @clear="handleClear"
    >
      <template #prefix>
        <font-awesome-icon icon="search" />
      </template>
    </el-input>

    <div v-if="searchText && showResultCount" class="search-result-count">
      找到 {{ filteredCount }} 个结果
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { SectorNode } from '@/components/data-management/shared/types'
import { SECTOR_PINYIN_MAPPING } from '@/assets/sector-pinyin-mapping.js'

interface Props {
  data: SectorNode[]
  showResultCount?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showResultCount: true
})

const emit = defineEmits<{
  'search-results': [results: SectorNode[]]
}>()

const searchText = ref('')
const placeholder = ref('搜索板块名称/代码/拼音(如: rgzn, rengongzhineng)')

// 获取板块的拼音信息
const getSectorPinyin = (sectorName: string) => {
  // 从映射表中查找
  for (const key in SECTOR_PINYIN_MAPPING) {
    if (SECTOR_PINYIN_MAPPING[key].name === sectorName) {
      return {
        initials: SECTOR_PINYIN_MAPPING[key].pinyin_initials || '',
        full: SECTOR_PINYIN_MAPPING[key].pinyin_full || ''
      }
    }
  }
  return { initials: '', full: '' }
}

// 检查板块是否匹配搜索词
const isSectorMatch = (node: SectorNode, searchTerm: string): boolean => {
  // 跳过根节点（行业板块、概念板块等分类节点）
  if (node.type === 'root' || node.type === 'category') {
    return false
  }

  const term = searchTerm.toLowerCase()

  // 1. 检查板块名称
  if (node.name.toLowerCase().includes(term)) {
    return true
  }

  // 2. 检查拼音首字母
  const pinyin = getSectorPinyin(node.name)
  if (pinyin.initials && pinyin.initials.toLowerCase().includes(term)) {
    return true
  }

  // 3. 检查完整拼音
  if (pinyin.full && pinyin.full.includes(term)) {
    return true
  }

  return false
}

// 在树中搜索
const searchInTree = (nodes: SectorNode[], searchTerm: string): SectorNode[] => {
  if (!searchTerm) return nodes

  const results: SectorNode[] = []

  nodes.forEach(node => {
    // 对于根节点（分类），递归搜索其子节点
    if (node.type === 'root' || node.type === 'category') {
      if (node.children && node.children.length > 0) {
        const matchedChildren = searchInTree(node.children, searchTerm)
        // 如果有匹配的子节点，保留这个父节点
        if (matchedChildren.length > 0) {
          results.push({
            ...node,
            children: matchedChildren
          })
        }
      }
    } else {
      // 对于实际板块节点，检查是否匹配
      const nodeMatched = isSectorMatch(node, searchTerm)
      if (nodeMatched) {
        results.push(node)
      }
    }
  })

  return results
}

// 计算过滤后的数量
const filteredCount = computed(() => {
  if (!searchText.value) return 0
  const results = searchInTree(props.data, searchText.value)
  return countNodes(results)
})

// 递归计算节点数量
const countNodes = (nodes: SectorNode[]): number => {
  let count = 0
  nodes.forEach(node => {
    if (node.type === 'sector') {
      count++
    }
    if (node.children) {
      count += countNodes(node.children)
    }
  })
  return count
}

// 处理搜索输入
const handleSearchInput = () => {
  if (!searchText.value) {
    emit('search-results', props.data)
    return
  }

  const results = searchInTree(props.data, searchText.value)
  emit('search-results', results)
}

// 处理清除
const handleClear = () => {
  searchText.value = ''
  emit('search-results', props.data)
}

// 暴露方法
defineExpose({
  clear: handleClear
})
</script>

<style scoped>
.sector-search-box {
  margin-bottom: 16px;
}

.search-result-count {
  margin-top: 8px;
  padding: 4px 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
}

:deep(.el-input) {
  --el-input-bg-color: rgba(255, 255, 255, 0.05);
  --el-input-border-color: rgba(255, 255, 255, 0.1);
  --el-input-text-color: rgba(255, 255, 255, 0.9);
  --el-input-placeholder-color: rgba(255, 255, 255, 0.4);
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: none;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.5);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #2962ff;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

:deep(.el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}
</style>
