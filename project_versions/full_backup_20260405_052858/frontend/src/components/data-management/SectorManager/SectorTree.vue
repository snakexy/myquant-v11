<template>
  <div class="sector-tree-wrapper">
    <el-tree
      ref="treeRef"
      :data="data"
      :props="treeProps"
      node-key="id"
      show-checkbox
      @check-change="handleCheckChange"
      class="sector-tree"
    >
      <template #default="{ node, data }">
        <div class="tree-node">
          <div class="node-icon">
            <font-awesome-icon
              :icon="getNodeIcon(data)"
              :style="{ color: getNodeColor(data) }"
            />
          </div>
          <div class="node-content">
            <span class="node-label">{{ data.name }}</span>
            <span class="node-count" v-if="data.stockCount !== undefined">
              ({{ data.stockCount }} 只)
            </span>
          </div>
          <div class="node-actions">
            <el-button
              v-if="data.type === 'sector'"
              link
              type="primary"
              size="small"
              @click.stop="showDetail(data)"
            >
              <font-awesome-icon icon="info-circle" />
              详情
            </el-button>
            <el-button
              v-if="!node.isLeaf && data.type !== 'sector'"
              link
              type="primary"
              size="small"
              @click.stop="loadStocks(data)"
            >
              <font-awesome-icon icon="list" />
              加载股票
            </el-button>
          </div>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { ElTree } from 'element-plus'
import type { SectorNode } from '@/components/data-management/shared/types'

interface Props {
  data: SectorNode[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'check-change': [stocks: string[]]
  'load-stocks': [node: SectorNode]
  'node-click': [node: SectorNode]
}>()

const treeRef = ref<InstanceType<typeof ElTree>>()

const treeProps = {
  label: 'name',
  children: 'children',
  isLeaf: (data: SectorNode) => data.isLeaf
}

// 懒加载节点
const load = async (node: any, resolve: Function) => {
  if (node.level === 0) {
    // 根节点，直接返回传入的数据
    resolve(props.data)
    return
  }

  // 非根节点，如果已有子节点则直接返回
  if (node.data.children && node.data.children.length > 0) {
    resolve(node.data.children)
    return
  }

  // 否则返回空数组
  resolve([])
}

// 生成模拟子节点
const generateMockChildren = (parentNode: SectorNode): SectorNode[] => {
  if (parentNode.type === 'root') {
    if (parentNode.id === 'industry') {
      return [
        { id: 'industry_1', name: '金融', type: 'category' as const },
        { id: 'industry_2', name: '科技', type: 'category' as const },
        { id: 'industry_3', name: '医药', type: 'category' as const },
        { id: 'industry_4', name: '消费', type: 'category' as const },
        { id: 'industry_5', name: '能源', type: 'category' as const }
      ]
    } else if (parentNode.id === 'concept') {
      return [
        { id: 'concept_1', name: '人工智能', type: 'category' as const },
        { id: 'concept_2', name: '新能源汽车', type: 'category' as const },
        { id: 'concept_3', name: '芯片半导体', type: 'category' as const },
        { id: 'concept_4', name: '5G通信', type: 'category' as const }
      ]
    }
  } else if (parentNode.type === 'category') {
    return [
      { id: `${parentNode.id}_s1`, name: '龙头股', type: 'sector' as const, stockCount: 15 },
      { id: `${parentNode.id}_s2`, name: '成长股', type: 'sector' as const, stockCount: 23 },
      { id: `${parentNode.id}_s3`, name: '小盘股', type: 'sector' as const, stockCount: 18 }
    ]
  }

  return []
}

// 🔧 修复：处理选中变化 - 只更新选中状态，不再自动加载股票
// 自动加载会导致多选时发起大量API请求，造成界面卡死
const handleCheckChange = async () => {
  const checkedNodes = treeRef.value?.getCheckedNodes() || []
  const checkedStocks: string[] = []

  // 只处理股票节点，不处理板块节点的自动加载
  for (const node of checkedNodes) {
    if (node.type === 'stock' && node.code) {
      checkedStocks.push(node.code)
    }
  }

  // 通知父组件选中的股票（如果有直接选中的股票节点）
  if (checkedStocks.length > 0) {
    emit('check-change', checkedStocks)
  }
}

// 加载股票
const loadStocks = (node: SectorNode) => {
  ElMessage.info(`正在加载 ${node.name} 的股票列表...`)
  emit('load-stocks', node)
}

// 显示详情
const showDetail = (node: SectorNode) => {
  emit('node-click', node)
}

// 获取节点图标
const getNodeIcon = (node: SectorNode) => {
  const iconMap: Record<string, any> = {
    'root': 'folder',
    'category': 'folder-open',
    'sector': 'layer-group',
    'stock': 'chart-line'
  }
  // 直接返回图标名称字符串，font-awesome-icon 会自动处理
  return iconMap[node.type] || 'circle'
}

// 获取节点颜色
const getNodeColor = (node: SectorNode) => {
  const colorMap: Record<string, string> = {
    'root': '#2962ff',
    'category': '#764ba2',
    'sector': '#10b981',
    'stock': '#f59e0b'
  }
  return colorMap[node.type] || '#ffffff'
}

// 全部展开
const expandAll = () => {
  const allNodes = treeRef.value?.store?.nodesMap || {}
  Object.keys(allNodes).forEach(key => {
    allNodes[key].expanded = true
  })
}

// 全部折叠
const collapseAll = () => {
  const allNodes = treeRef.value?.store?.nodesMap || {}
  Object.keys(allNodes).forEach(key => {
    allNodes[key].expanded = false
  })
}

// 清空选择
const clearSelection = () => {
  treeRef.value?.setCheckedKeys([])
}

// 暴露方法
defineExpose({
  expandAll,
  collapseAll,
  clearSelection
})
</script>

<style scoped>
.sector-tree-wrapper {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  padding: 16px;
}

:deep(.el-tree) {
  background: transparent;
  color: #ffffff;
}

:deep(.el-tree-node__content) {
  background: transparent;
  height: 40px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

:deep(.el-tree-node__content:hover) {
  background: rgba(102, 126, 234, 0.15);
}

/* 选中状态 - 深色主题风格 */
:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: rgba(102, 126, 234, 0.25) !important;
  border: 1px solid rgba(102, 126, 234, 0.5);
}

:deep(.el-tree-node.is-current > .el-tree-node__content .node-label) {
  color: #2962ff;
  font-weight: 600;
}

:deep(.el-tree-node:focus > .el-tree-node__content) {
  background: rgba(102, 126, 234, 0.2) !important;
  border: 1px solid rgba(102, 126, 234, 0.4);
}

:deep(.el-tree-node__expand-icon) {
  color: rgba(255, 255, 255, 0.6);
}

:deep(.el-tree-node.is-current > .el-tree-node__content .el-tree-node__expand-icon) {
  color: #2962ff;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.node-icon {
  font-size: 16px;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.node-label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.node-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

:deep(.el-tree-node__content:hover) .node-actions {
  opacity: 1;
}
</style>
