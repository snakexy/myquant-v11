/**
 * MyQuant v10.0.0 - Alert System API
 * 智能预警系统相关API
 */

import { http } from '../request'

// ==================== 类型定义 ====================

// 预警条件
export interface AlertCondition {
  metric: string // 指标名称（如 'sharpe_ratio', 'max_drawdown'）
  operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte' // 比较运算符
  threshold: number // 阈值
  timeWindow?: number // 时间窗口（秒）
}

// 预警规则
export interface AlertRule {
  ruleId: string
  ruleName: string
  ruleType: 'risk' | 'opportunity' | 'system' // 规则类型
  condition: AlertCondition
  severity: 'info' | 'warning' | 'critical' // 严重程度
  enabled: boolean // 是否启用
  description?: string // 规则描述
  createdAt: string
  updatedAt: string
  triggerCount?: number // 触发次数
}

// 预警记录
export interface Alert {
  alertId: string
  ruleId: string
  ruleName: string
  message: string
  severity: 'info' | 'warning' | 'critical'
  metrics: Record<string, number> // 触发时的指标值
  acknowledged: boolean // 是否已确认
  acknowledgedBy?: string // 确认人
  acknowledgedAt?: string // 确认时间
  createdAt: string
  channelId?: string // 推送渠道
  channelStatus?: 'pending' | 'sent' | 'failed' // 推送状态
}

// 创建规则请求
export interface CreateRuleRequest {
  ruleName: string
  ruleType: 'risk' | 'opportunity' | 'system'
  condition: AlertCondition
  severity: 'info' | 'warning' | 'critical'
  description?: string
}

// 更新规则请求
export interface UpdateRuleRequest {
  ruleName?: string
  condition?: AlertCondition
  severity?: 'info' | 'warning' | 'critical'
  description?: string
}

// 规则列表响应
export interface RuleListResponse {
  rules: AlertRule[]
  total: number
}

// 预警统计
export interface AlertStatistics {
  total: number
  critical: number
  warning: number
  info: number
  acknowledged: number
  pending: number
  byRule: Record<string, number>
  todayCount: number
  weekCount: number
  monthCount: number
}

// 通知渠道配置
export interface NotificationChannel {
  channelId: string
  channelType: 'email' | 'dingtalk' | 'wechat' | 'webhook'
  enabled: boolean
  config: Record<string, any>
  lastUsed?: string
}

// 推送模板
export interface NotificationTemplate {
  templateId: string
  templateName: string
  severity: 'info' | 'warning' | 'critical'
  subject: string
  body: string
  variables: string[] // 可用变量
}

// ==================== API方法 ====================

export const alertApi = {
  /**
   * 创建预警规则
   * POST /api/v1/validation/alerts/rules
   * @param request 创建规则请求
   */
  createRule(request: CreateRuleRequest): Promise<{ code: number; data: AlertRule; message: string }> {
    return http.post('/v1/validation/alerts/rules', request)
  },

  /**
   * 获取规则列表
   * GET /api/v1/validation/alerts/rules
   * @param severity 严重程度过滤
   * @param enabledOnly 是否只返回启用的规则
   */
  listRules(severity?: string, enabledOnly?: boolean): Promise<{ code: number; data: RuleListResponse; message: string }> {
    return http.get('/v1/validation/alerts/rules', { params: { severity, enabled_only: enabledOnly } })
  },

  /**
   * 获取单个规则
   * GET /api/v1/validation/alerts/rules/{rule_id}
   * @param ruleId 规则ID
   */
  getRule(ruleId: string): Promise<{ code: number; data: AlertRule; message: string }> {
    return http.get(`/v1/validation/alerts/rules/${ruleId}`)
  },

  /**
   * 更新规则
   * PUT /api/v1/validation/alerts/rules/{rule_id}
   * @param ruleId 规则ID
   * @param request 更新请求
   */
  updateRule(ruleId: string, request: UpdateRuleRequest): Promise<{ code: number; data: AlertRule; message: string }> {
    return http.put(`/v1/validation/alerts/rules/${ruleId}`, request)
  },

  /**
   * 删除规则
   * DELETE /api/v1/validation/alerts/rules/{rule_id}
   * @param ruleId 规则ID
   */
  deleteRule(ruleId: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.delete(`/v1/validation/alerts/rules/${ruleId}`)
  },

  /**
   * 启用规则
   * POST /api/v1/validation/alerts/rules/{rule_id}/enable
   * @param ruleId 规则ID
   */
  enableRule(ruleId: string): Promise<{ code: number; data: AlertRule; message: string }> {
    return http.post(`/v1/validation/alerts/rules/${ruleId}/enable`)
  },

  /**
   * 禁用规则
   * POST /api/v1/validation/alerts/rules/{rule_id}/disable
   * @param ruleId 规则ID
   */
  disableRule(ruleId: string): Promise<{ code: number; data: AlertRule; message: string }> {
    return http.post(`/v1/validation/alerts/rules/${ruleId}/disable`)
  },

  /**
   * 获取预警记录列表
   * GET /api/v1/validation/alerts
   * @param severity 严重程度过滤
   * @param acknowledged 是否已确认
   * @param limit 返回数量限制
   * @param offset 偏移量
   */
  listAlerts(severity?: string, acknowledged?: boolean, limit: number = 50, offset: number = 0): Promise<{ code: number; data: { alerts: Alert[]; total: number }; message: string }> {
    return http.get('/v1/validation/alerts/list', { params: { severity, acknowledged, limit, offset } })
  },

  /**
   * 确认预警
   * POST /api/v1/validation/alerts/{alert_id}/acknowledge
   * @param alertId 预警ID
   * @param acknowledgedBy 确认人
   */
  acknowledgeAlert(alertId: string, acknowledgedBy?: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post(`/v1/validation/alerts/${alertId}/acknowledge`, { acknowledged_by: acknowledgedBy })
  },

  /**
   * 批量确认预警
   * POST /api/v1/validation/alerts/batch-acknowledge
   * @param alertIds 预警ID列表
   * @param acknowledgedBy 确认人
   */
  batchAcknowledgeAlerts(alertIds: string[], acknowledgedBy?: string): Promise<{ code: number; data: { success: boolean; count: number }; message: string }> {
    return http.post('/v1/validation/alerts/batch-acknowledge', { alert_ids: alertIds, acknowledged_by: acknowledgedBy })
  },

  /**
   * 获取预警统计
   * GET /api/v1/validation/alerts/statistics
   */
  getStatistics(): Promise<{ code: number; data: AlertStatistics; message: string }> {
    return http.get('/v1/validation/alerts/statistics')
  },

  /**
   * 评估规则（手动触发）
   * POST /api/v1/validation/alerts/evaluate
   * @param currentMetrics 当前指标值
   */
  evaluateRules(currentMetrics: Record<string, number>): Promise<{ code: number; data: { triggered: Alert[] }; message: string }> {
    return http.post('/v1/validation/alerts/evaluate', { current_metrics: currentMetrics })
  },

  /**
   * 获取通知渠道列表
   * GET /api/v1/validation/alerts/channels
   */
  getNotificationChannels(): Promise<{ code: number; data: NotificationChannel[]; message: string }> {
    return http.get('/v1/validation/alerts/channels')
  },

  /**
   * 配置通知渠道
   * POST /api/v1/validation/alerts/channels
   * @param channel 渠道配置
   */
  configureNotificationChannel(channel: Omit<NotificationChannel, 'channelId'>): Promise<{ code: number; data: NotificationChannel; message: string }> {
    return http.post('/v1/validation/alerts/channels', channel)
  },

  /**
   * 测试通知推送
   * POST /api/v1/validation/alerts/test-notification
   * @param channelId 渠道ID
   * @param message 测试消息
   */
  testNotification(channelId: string, message: string): Promise<{ code: number; data: { success: boolean }; message: string }> {
    return http.post('/v1/validation/alerts/test-notification', { channel_id: channelId, message })
  },

  /**
   * 获取通知模板列表
   * GET /api/v1/validation/alerts/templates
   */
  getNotificationTemplates(): Promise<{ code: number; data: NotificationTemplate[]; message: string }> {
    return http.get('/v1/validation/alerts/templates')
  }
}

export default alertApi
