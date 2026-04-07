/**
 * 用户配置 API
 *
 * 提供用户配置的云端存储：
 * - 指标配置（启用哪些指标、参数、高度等）
 * - 图表布局配置
 * - 个性化设置
 */

import axios from 'axios'

const BASE_URL = '/api/dataget/settings'

export interface IndicatorSettings {
  activeIndicators: string[]      // 启用的副图指标
  overlayIndicators: string[]     // 主图叠加指标
  indicatorParams: Record<string, any>  // 指标参数
  paneHeights: Record<string, number>   // 指标pane高度
}

export interface UserSettings {
  [key: string]: any
}

/**
 * 获取指标配置
 */
export async function getIndicatorSettings(userId: string = 'default'): Promise<IndicatorSettings> {
  const response = await axios.get(`${BASE_URL}/indicators/${userId}`)
  return response.data
}

/**
 * 保存指标配置
 */
export async function saveIndicatorSettings(settings: IndicatorSettings, userId: string = 'default'): Promise<void> {
  await axios.post(`${BASE_URL}/indicators`, {
    userId,
    ...settings
  })
}

/**
 * 获取通用配置
 */
export async function getGeneralSettings(userId: string = 'default'): Promise<UserSettings> {
  const response = await axios.get(`${BASE_URL}/general/${userId}`)
  return response.data
}

/**
 * 保存通用配置
 */
export async function saveGeneralSettings(settings: UserSettings, userId: string = 'default'): Promise<void> {
  await axios.post(`${BASE_URL}/general`, {
    userId,
    settings
  })
}
