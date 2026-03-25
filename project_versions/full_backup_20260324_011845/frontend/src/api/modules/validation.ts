/**
 * MyQuant v10.0.0 - Validation API 统一导出
 * Validation阶段所有API的统一入口
 */

export { simulationApi } from './simulation'
export type { Strategy, SimulationStatus, SimulationMetrics, OnlineTrainingStatus, SimulationDetail } from './simulation'

export { trainingApi } from './training'
export type {
  Model,
  TrainingStatus,
  TrainingParams,
  TrainingProgress,
  TrainingHistory,
  TrainingDetail
} from './training'

export { monitoringApi } from './monitoring'
export type {
  OverviewMetrics,
  ReturnCurvePoint,
  RiskMetrics,
  Position,
  Trade,
  AlertMessage,
  TimePeriod
} from './monitoring'

export { alertApi } from './alerts'
export type {
  AlertRule,
  AlertCondition,
  Alert,
  CreateRuleRequest,
  UpdateRuleRequest,
  RuleListResponse,
  AlertStatistics,
  NotificationChannel,
  NotificationTemplate
} from './alerts'

// 统一导出所有Validation API
export const validationApi = {
  simulation: () => import('./simulation').then(m => m.simulationApi),
  training: () => import('./training').then(m => m.trainingApi),
  monitoring: () => import('./monitoring').then(m => m.monitoringApi),
  alerts: () => import('./alerts').then(m => m.alertApi)
}
