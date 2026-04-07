/**
 * Lightweight Charts 插件统一导出
 *
 * 包含以下插件:
 * - UserPriceAlerts: 用户自定义价格线
 * - ExpiringPriceAlerts: 带过期时间的价格提醒
 */

export { UserPriceAlerts, type PriceAlert, type PriceAlertOptions } from './user-price-alerts';
export {
  ExpiringPriceAlerts,
  type ExpiringPriceAlert,
  type ExpiringAlertOptions,
} from './expiring-price-alerts';

// 重新导出基类（如果需要扩展）
export { PluginBase } from './plugin-base';
