/**
 * 板块收藏夹数据管理
 * 基于 LocalStorage 的持久化存储
 */

import type { SectorNode } from '@/components/data-management/shared/types'

// ==================== 类型定义 ====================

export interface FavoriteSector {
  code: string          // 板块代码
  name: string          // 板块名称
  type?: string         // 板块类型
  stockCount?: number   // 成分股数量
}

export interface FavoriteCollection {
  id: string                    // 唯一标识
  name: string                  // 收藏夹名称
  description: string           // 描述
  sectors: FavoriteSector[]     // 板块列表
  createdAt: string             // 创建时间
  updatedAt: string             // 更新时间
}

export interface FavoritesData {
  collections: FavoriteCollection[]
  version: string
}

// ==================== 常量定义 ====================

const STORAGE_KEY = 'sector_favorites'
const CURRENT_VERSION = '1.0.0'

// ==================== 工具函数 ====================

/**
 * 生成唯一ID
 */
function generateId(): string {
  return `fav_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
}

/**
 * 获取所有收藏夹数据
 */
export function getFavoritesData(): FavoritesData {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const data = JSON.parse(stored) as FavoritesData
      // 版本兼容性检查
      if (!data.version || data.version !== CURRENT_VERSION) {
        // 迁移旧版本数据
        return migrateData(data)
      }
      return data
    }
  } catch (error) {
    console.error('读取收藏夹数据失败:', error)
  }

  // 返回默认空数据
  return {
    collections: [],
    version: CURRENT_VERSION
  }
}

/**
 * 保存所有收藏夹数据
 */
export function saveFavoritesData(data: FavoritesData): boolean {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    return true
  } catch (error) {
    console.error('保存收藏夹数据失败:', error)
    return false
  }
}

/**
 * 数据迁移（用于版本升级）
 */
function migrateData(oldData: any): FavoritesData {
  // 这里可以添加版本迁移逻辑
  // 目前直接返回新格式
  return {
    collections: oldData.collections || [],
    version: CURRENT_VERSION
  }
}

// ==================== 收藏夹操作 ====================

/**
 * 获取所有收藏夹
 */
export function getAllCollections(): FavoriteCollection[] {
  const data = getFavoritesData()
  return data.collections
}

/**
 * 获取单个收藏夹
 */
export function getCollection(id: string): FavoriteCollection | null {
  const data = getFavoritesData()
  return data.collections.find(c => c.id === id) || null
}

/**
 * 创建收藏夹
 */
export function createCollection(
  name: string,
  description: string,
  sectors: FavoriteSector[] = []
): FavoriteCollection {
  const data = getFavoritesData()

  const newCollection: FavoriteCollection = {
    id: generateId(),
    name,
    description,
    sectors: [...sectors],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }

  data.collections.push(newCollection)
  saveFavoritesData(data)

  return newCollection
}

/**
 * 更新收藏夹
 */
export function updateCollection(
  id: string,
  updates: Partial<Pick<FavoriteCollection, 'name' | 'description' | 'sectors'>>
): FavoriteCollection | null {
  const data = getFavoritesData()
  const index = data.collections.findIndex(c => c.id === id)

  if (index === -1) {
    return null
  }

  // 更新字段
  if (updates.name !== undefined) {
    data.collections[index].name = updates.name
  }
  if (updates.description !== undefined) {
    data.collections[index].description = updates.description
  }
  if (updates.sectors !== undefined) {
    data.collections[index].sectors = [...updates.sectors]
  }

  // 更新时间
  data.collections[index].updatedAt = new Date().toISOString()

  saveFavoritesData(data)

  return data.collections[index]
}

/**
 * 删除收藏夹
 */
export function deleteCollection(id: string): boolean {
  const data = getFavoritesData()
  const index = data.collections.findIndex(c => c.id === id)

  if (index === -1) {
    return false
  }

  data.collections.splice(index, 1)
  saveFavoritesData(data)

  return true
}

/**
 * 添加板块到收藏夹
 */
export function addSectorToCollection(
  collectionId: string,
  sector: FavoriteSector
): boolean {
  const collection = getCollection(collectionId)
  if (!collection) {
    return false
  }

  // 检查是否已存在
  const exists = collection.sectors.some(s => s.code === sector.code)
  if (exists) {
    return false
  }

  collection.sectors.push(sector)
  updateCollection(collectionId, { sectors: collection.sectors })

  return true
}

/**
 * 从收藏夹移除板块
 */
export function removeSectorFromCollection(
  collectionId: string,
  sectorCode: string
): boolean {
  const collection = getCollection(collectionId)
  if (!collection) {
    return false
  }

  const index = collection.sectors.findIndex(s => s.code === sectorCode)
  if (index === -1) {
    return false
  }

  collection.sectors.splice(index, 1)
  updateCollection(collectionId, { sectors: collection.sectors })

  return true
}

/**
 * 检查板块是否在收藏夹中
 */
export function isSectorInFavorites(
  sectorCode: string,
  collectionId?: string
): boolean {
  const collections = collectionId
    ? [getCollection(collectionId)].filter(Boolean) as FavoriteCollection[]
    : getAllCollections()

  return collections.some(collection =>
    collection.sectors.some(sector => sector.code === sectorCode)
  )
}

/**
 * 获取板块所在的所有收藏夹
 */
export function getSectorCollections(sectorCode: string): FavoriteCollection[] {
  const allCollections = getAllCollections()
  return allCollections.filter(collection =>
    collection.sectors.some(sector => sector.code === sectorCode)
  )
}

// ==================== 导出导入 ====================

/**
 * 导出收藏夹数据为 JSON
 */
export function exportFavorites(): string {
  const data = getFavoritesData()
  return JSON.stringify(data, null, 2)
}

/**
 * 导出收藏夹数据为文件
 */
export function exportFavoritesToFile(filename?: string): void {
  const data = exportFavorites()
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const link = document.createElement('a')
  link.href = url
  link.download = filename || `板块收藏夹_${new Date().toISOString().slice(0, 10)}.json`
  link.click()

  URL.revokeObjectURL(url)
}

/**
 * 导入收藏夹数据
 */
export function importFavorites(jsonString: string): boolean {
  try {
    const data = JSON.parse(jsonString) as FavoritesData

    // 验证数据格式
    if (!data.collections || !Array.isArray(data.collections)) {
      throw new Error('无效的数据格式')
    }

    // 保存数据
    return saveFavoritesData({
      collections: data.collections,
      version: CURRENT_VERSION
    })
  } catch (error) {
    console.error('导入收藏夹数据失败:', error)
    return false
  }
}

/**
 * 从文件导入收藏夹
 */
export function importFavoritesFromFile(file: File): Promise<boolean> {
  return new Promise((resolve) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      const content = e.target?.result as string
      const success = importFavorites(content)
      resolve(success)
    }

    reader.onerror = () => {
      console.error('读取文件失败')
      resolve(false)
    }

    reader.readAsText(file)
  })
}

// ==================== 辅助函数 ====================

/**
 * 将 SectorNode 转换为 FavoriteSector
 */
export function sectorNodeToFavorite(sector: SectorNode): FavoriteSector {
  return {
    code: (sector as any).code || sector.name,
    name: sector.name,
    type: sector.type,
    stockCount: sector.stockCount
  }
}

/**
 * 获取收藏夹统计信息
 */
export function getFavoritesStats(): {
  totalCollections: number
  totalSectors: number
  latestUpdate: string | null
} {
  const collections = getAllCollections()

  let totalSectors = 0
  let latestUpdate: string | null = null

  collections.forEach(collection => {
    totalSectors += collection.sectors.length
    if (!latestUpdate || collection.updatedAt > latestUpdate) {
      latestUpdate = collection.updatedAt
    }
  })

  return {
    totalCollections: collections.length,
    totalSectors,
    latestUpdate
  }
}
