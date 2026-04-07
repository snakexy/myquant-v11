import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// M2-15优化：所有页面组件使用动态导入（懒加载），减少初始加载体积

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: {
      title: 'Quant-UI - 智能量化交易平台',
      requiresAuth: false,
      keepAlive: false,
      hideGlobalNav: true
    }
  },
  {
    path: '/RealtimeQuotes',
    name: 'RealtimeQuotes',
    component: () => import('../views/market/RealtimeQuotes.vue'),
    meta: {
      title: '实时行情 - MyQuant v11',
      requiresAuth: false,
      keepAlive: false,
      hideGlobalNav: false
    }
  },
  {
    path: '/test',
    name: 'TestHome',
    component: () => import('../views/TestHome.vue'),
    meta: {
      title: '测试页面 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/style-test',
    name: 'StyleTest',
    component: () => import('../views/StyleTestView.vue'),
    meta: {
      title: '统一设计系统预览',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/data-management',
    name: 'DataManagement',
    component: () => import('../views/DataManagement.vue'),
    meta: {
      title: '数据管理 - Quant-UI',
      requiresAuth: false,
      keepAlive: true,
      hideGlobalNav: true
    }
  },
  {
    path: '/hotspot-analysis',
    name: 'HotspotAnalysis',
    component: () => import('../views/HotspotAnalysis.vue'),
    meta: {
      title: '热点分析 - Quant-UI',
      requiresAuth: false,
      keepAlive: true,
      hideGlobalNav: true
    }
  },
  {
    path: '/stock-list',
    name: 'StockList',
    component: () => import('../views/StockList.vue'),
    meta: {
      title: '股票列表 - Quant-UI',
      requiresAuth: false,
      keepAlive: true
    }
  },
  {
    path: '/kline',
    name: 'KlineChart',
    component: () => import('../views/KlineChartPage.vue'),
    meta: {
      title: 'K线图 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/klinecharts-test',
    name: 'KlineChartsTest',
    component: () => import('../views/KlineChartsTest.vue'),
    meta: {
      title: 'KlineCharts 测试 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/chart-test',
    name: 'ChartTest',
    component: () => import('../views/ChartTestPage.vue'),
    meta: {
      title: '纯净图表测试 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/chart-test-step1',
    name: 'ChartTestStep1',
    component: () => import('../views/ChartTestStep1.vue'),
    meta: {
      title: '图表测试步骤1 - 顶部工具栏',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/chart-test-step2',
    name: 'ChartTestStep2',
    component: () => import('../views/ChartTestStep2.vue'),
    meta: {
      title: '图表测试步骤2 - 右侧边栏',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/chart-test-step3',
    name: 'ChartTestStep3',
    component: () => import('../views/ChartTestStep3.vue'),
    meta: {
      title: '图表测试步骤3 - 左侧工具栏',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/chart-test-no-indicators',
    name: 'ChartTestNoIndicators',
    component: () => import('../views/ChartTestNoIndicators.vue'),
    meta: {
      title: '指标测试 - 无指标vs有指标',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/tradingview-kline',
    name: 'TradingViewKLine',
    component: () => import('../views/KlineChartsTest.vue'),
    meta: {
      title: 'TradingView完整K线图 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/sector-map',
    name: 'SectorMap',
    component: () => import('../views/SectorMap.vue'),
    meta: {
      title: '板块地图 - Quant-UI',
      requiresAuth: false,
      keepAlive: true
    }
  },
  {
    path: '/backtest',
    name: 'Backtest',
    component: () => import('../views/BacktestView.vue'),
    meta: {
      title: '回测实验室 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  {
    path: '/api-test',
    name: 'ApiTest',
    component: () => import('../views/ApiTest.vue'),
    meta: {
      title: 'API测试 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/simple-api-test',
    name: 'SimpleApiTest',
    component: () => import('../views/SimpleApiTest.vue'),
    meta: {
      title: '简单API测试 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/unified-api-test',
    name: 'UnifiedAPITest',
    component: () => import('../views/UnifiedAPITest.vue'),
    meta: {
      title: '统一API测试 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  // 测试路由
  {
    path: '/test-intelligent',
    name: 'TestIntelligent',
    component: () => import('@/components/TestComponent.vue'),
    meta: {
      title: '智能节点测试 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/drag-test',
    name: 'DragTest',
    component: () => import('@/components/DragTest.vue'),
    meta: {
      title: '拖拽性能测试 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/slider-demo',
    name: 'SliderDemo',
    component: () => import('../views/SliderDemo.vue'),
    meta: {
      title: '滑杆组件演示 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: {
      title: '页面未找到 - Quant-UI',
      requiresAuth: false
    }
  },
  // Unreal蓝图系统测试页面
  {
    path: '/unreal-blueprint',
    name: 'UnrealBlueprint',
    component: () => import('../views/UnrealBlueprintView.vue'),
    meta: {
      title: 'Unreal蓝图系统 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  // Unreal蓝图系统简化测试页面
  {
    path: '/unreal-test',
    name: 'UnrealBlueprintTest',
    component: () => import('../views/UnrealBlueprintTest.vue'),
    meta: {
      title: 'Unreal蓝图测试 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  // ==================== Research阶段 - RL策略优化模块 ====================
  {
    path: '/research/rl/training',
    name: 'RLStrategyTraining',
    component: () => import('../views/research/RLStrategyTrainingView.vue'),
    meta: {
      title: 'RL策略训练 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/research/rl/optimization',
    name: 'RLStrategyOptimization',
    component: () => import('../views/research/RLStrategyOptimizationView.vue'),
    meta: {
      title: 'RL策略优化 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/research/rl/models',
    name: 'RLModelManagement',
    component: () => import('../views/research/RLModelManagementView.vue'),
    meta: {
      title: 'RL模型管理 - Quant-UI',
      requiresAuth: false,
      keepAlive: true
    }
  },
  // 监控系统页面
  {
    path: '/monitoring',
    name: 'Monitoring',
    component: () => import('../views/Monitoring.vue'),
    meta: {
      title: '监控系统 - Quant-UI',
      requiresAuth: true,
      keepAlive: true,
      hideGlobalNav: true
    }
  },
  // 研究阶段页面
  {
    path: '/research',
    name: 'Research',
    component: () => import('../views/Research.vue'),
    meta: {
      title: '研究阶段 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  // 工作流管理（总览入口）
  {
    path: '/workflow',
    name: 'WorkflowManager',
    component: () => import('../views/workflow/WorkflowManagerView.vue'),
    meta: {
      title: '工作流管理 - Quant-UI',
      requiresAuth: false,
      keepAlive: true,
      hideGlobalNav: true
    }
  },
  // Research阶段 - 专业版详情页（拆分版本）
  {
    path: '/research/detail',
    name: 'ResearchDetail',
    component: () => import('../views/research/ResearchDetailViewSplit.vue'), // 拆分版本
    meta: {
      title: 'Research详情 - Quant-UI',
      requiresAuth: false,
      keepAlive: true,
      hideGlobalNav: true  // 隐藏全局导航栏和侧边栏菜单
    }
  },
  // Research阶段 - 因子评估
  {
    path: '/research/factor-evaluation',
    name: 'FactorEvaluation',
    component: () => import('../views/research/components/ResearchStep4FactorEvaluation.vue'),
    meta: {
      title: '因子评估 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  // Research阶段 - 因子分析
  {
    path: '/research/factor-analysis',
    name: 'FactorAnalysis',
    component: () => import('../views/research/FactorAnalysisView.vue'),
    meta: {
      title: '因子分析 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  // Research阶段 - AI助手
  {
    path: '/research/ai-assistant',
    name: 'AIAssistant',
    component: () => import('../views/research/AIAssistantView.vue'),
    meta: {
      title: 'AI助手 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  // ==================== Research阶段 - ML模型训练模块 ====================
  // 已归档 - 功能合并到 ResearchStep5ModelTraining.vue
  // {
  //   path: '/research/ml/training',
  //   name: 'MLModelTraining',
  //   component: () => import('../views/research/MLModelTrainingView.vue'),
  //   meta: {
  //     title: 'ML模型训练 - Quant-UI',
  //     requiresAuth: false,
  //     keepAlive: false
  //   }
  // },
  {
    path: '/research/ml/prediction',
    name: 'MLModelPrediction',
    component: () => import('../views/research/MLModelPredictionView.vue'),
    meta: {
      title: 'ML模型预测 - Quant-UI',
      requiresAuth: false,
      keepAlive: false
    }
  },
  {
    path: '/research/ml/management',
    name: 'MLModelManagement',
    component: () => import('../views/research/MLModelManagementView.vue'),
    meta: {
      title: 'ML模型管理 - Quant-UI',
      requiresAuth: false,
      keepAlive: false,
      hideGlobalNav: true
    }
  },
  // Research阶段 - 因子计算
  {
    path: '/research/factor-calculation',
    name: 'FactorCalculation',
    component: () => import('../views/research/FactorCalculationView.vue'),
    meta: {
      title: '因子计算 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  // 验证阶段页面（M3-4: 精美首页 + 子页面）
  {
    path: '/validation',
    name: 'Validation',
    component: () => import('../views/Validation.vue'),
    meta: {
      title: '验证阶段 - Quant-UI',
      requiresAuth: false,
      keepAlive: true
    }
  },
  // Validation阶段 - 专业版详情页
  {
    path: '/validation/detail',
    name: 'ValidationDetail',
    component: () => import('../views/validation/ValidationDetailView.vue'),
    meta: {
      title: 'Validation详情 - Quant-UI',
      requiresAuth: false,
      keepAlive: true
    }
  },
  // Validation子页面（独立路由，不从属于父路由）
  {
    path: '/validation/backtest',
    name: 'ValidationBacktest',
    component: () => import('@/views/validation/BacktestView.vue'),
    meta: { title: '历史回测 - Quant-UI', requiresAuth: false }
  },
  {
    path: '/validation/simulation',
    name: 'ValidationSimulation',
    component: () => import('@/views/validation/SimulationView.vue'),
    meta: { title: '模拟实盘验证 - Quant-UI', requiresAuth: false }
  },
  {
    path: '/validation/learning',
    name: 'ValidationLearning',
    component: () => import('@/views/validation/OnlineLearningView.vue'),
    meta: { title: '在线滚动训练 - Quant-UI', requiresAuth: false }
  },
  {
    path: '/validation/monitoring',
    name: 'ValidationMonitoring',
    component: () => import('@/views/validation/MonitoringView.vue'),
    meta: { title: '实时监控 - Quant-UI', requiresAuth: false }
  },
  {
    path: '/validation/alerts',
    name: 'ValidationAlerts',
    component: () => import('@/views/validation/AlertSystemView.vue'),
    meta: { title: '规则预警系统 - Quant-UI', requiresAuth: false }
  },
  {
    path: '/validation/ai-alerts',
    name: 'ValidationAIAlerts',
    component: () => import('@/views/validation/AIRiskAlertView.vue'),
    meta: { title: 'AI智能预警 - Quant-UI', requiresAuth: false }
  },
  // 上线阶段页面
  {
    path: '/production',
    name: 'Production',
    component: () => import('../views/Production.vue'),
    meta: {
      title: '上线阶段 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  // Production阶段 - 专业版详情页
  {
    path: '/production/detail',
    name: 'ProductionDetail',
    component: () => import('../views/production/ProductionDetailView.vue'),
    meta: {
      title: 'Production详情 - Quant-UI',
      requiresAuth: false,
      keepAlive: true
    }
  },
  // Production阶段 - 仓位管理
  {
    path: '/production/position',
    name: 'ProductionPosition',
    component: () => import('../views/production/PositionManagementView.vue'),
    meta: {
      title: '仓位管理 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  // Production阶段 - 风险控制
  {
    path: '/production/risk',
    name: 'ProductionRisk',
    component: () => import('../views/production/RiskControlView.vue'),
    meta: {
      title: '风险管理 - Quant-UI',
      requiresAuth: true,
      keepAlive: true,
      hideGlobalNav: true
    }
  },
  // Production阶段 - 实盘交易
  {
    path: '/production/trading',
    name: 'ProductionTrading',
    component: () => import('../views/production/TradingView.vue'),
    meta: {
      title: '实盘交易 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  // 节点工作流页面
  {
    path: '/research/nodes',
    name: 'NodeWorkflow',
    component: () => import('../views/NodeWorkflow.vue'),
    meta: {
      title: '节点工作流 - Quant-UI',
      requiresAuth: true,
      keepAlive: true
    }
  },
  // 策略管理页面
  {
    path: '/strategy',
    name: 'StrategyManagement',
    component: () => import('../views/strategy/StrategyManagementView.vue'),
    meta: {
      title: '策略管理 - Quant-UI',
      requiresAuth: false,
      keepAlive: true,
      hideGlobalNav: true
    }
  },
  // 策略中心页面（带沉浸式效果）
  {
    path: '/strategy-main',
    name: 'StrategyMain',
    component: () => import('../views/Strategy.vue'),
    meta: {
      title: '策略中心 - Quant-UI',
      requiresAuth: false,
      keepAlive: true
    }
  },
  // 策略架构页面
  {
    path: '/strategy-architecture',
    name: 'StrategyArchitecture',
    component: () => import('../views/StrategyArchitecture.vue'),
    meta: {
      title: '策略架构 - Quant-UI',
      requiresAuth: false,
      keepAlive: true
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 如果有保存的位置，恢复滚动位置
    if (savedPosition) {
      return savedPosition
    }
    
    // 如果是层级切换，保持当前滚动位置
    if (to.meta?.layer && from.meta?.layer) {
      return { top: 0, left: 0 }
    }
    
    // 默认滚动到顶部
    return { top: 0, left: 0 }
  }
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = to.meta.title as string
  }
  
  // 检查认证状态
  const requiresAuth = to.meta?.requiresAuth
  if (requiresAuth) {
    // 这里可以添加认证逻辑
    // const isAuthenticated = await checkAuth()
    // if (!isAuthenticated) {
    //   next('/login')
    //   return
    // }
  }
  
  // 检查权限
  const requiredRole = to.meta?.role
  if (requiredRole) {
    // 这里可以添加权限检查逻辑
    // const userRole = getUserRole()
    // if (userRole !== requiredRole) {
    //   next('/403')
    //   return
    // }
  }
  
  // 层级导航状态保持
  if (to.meta?.layer && from.meta?.layer) {
    // 保存离开层级的状态
    const fromLayer = from.meta.layer as number
    const toLayer = to.meta.layer as number
    
    // 触发状态保存事件
    window.dispatchEvent(new CustomEvent('layer-state-save', {
      detail: {
        fromLayer,
        toLayer,
        from: from.path,
        to: to.path
      }
    }))
  }
  
  next()
})

// 全局后置钩子
router.afterEach((to, from) => {
  // 层级切换完成后的处理
  if (to.meta?.layer && from.meta?.layer) {
    const toLayer = to.meta.layer as number
    const fromLayer = from.meta.layer as number
    
    // 触发状态恢复事件
    window.dispatchEvent(new CustomEvent('layer-state-restore', {
      detail: {
        fromLayer,
        toLayer,
        from: from.path,
        to: to.path
      }
    }))
  }
  
  // 路由变化分析
  console.log(`Route changed: ${from.path} -> ${to.path}`)
  
  // 可以添加路由变化统计
  if (process.env.NODE_ENV === 'development') {
    console.log('Route meta:', to.meta)
  }
})

// 路由错误处理
router.onError((error) => {
  console.error('Router error:', error)
  
  // 可以添加错误上报逻辑
  // reportError(error)
})

// 导航失败处理
router.isReady().then(() => {
  console.log('Router is ready')
}).catch((error) => {
  console.error('Router initialization failed:', error)
})

// 导出路由实例
export default router

// 导出路由工具函数
export const navigateToLayer = (functionId: string, layer: number) => {
  const layerMap: Record<number, string> = {
    1: 'dashboard',
    2: 'architecture',
    3: 'monitoring'
  }
  
  const layerPath = layerMap[layer]
  if (!layerPath) {
    console.error(`Invalid layer: ${layer}`)
    return
  }
  
  return router.push(`/function/${functionId}/${layerPath}`)
}

export const navigateToFunction = (functionId: string, defaultLayer: number = 1) => {
  return navigateToLayer(functionId, defaultLayer)
}

export const navigateToDataManagement = () => {
  return router.push('/data-management')
}

export const navigateToApiTest = () => {
  return router.push('/api-test')
}

export const navigateToEngineerToolbox = () => {
  return router.push('/engineer-toolbox')
}

export const navigateToUnrealBlueprint = () => {
  return router.push('/unreal-blueprint')
}

export const navigateToNodeWorkflow = () => {
  return router.push('/research/nodes')
}

export const goBack = () => {
  return router.back()
}

export const goForward = () => {
  return router.forward()
}

// 获取当前层级
export const getCurrentLayer = (): number => {
  const currentRoute = router.currentRoute.value
  return currentRoute.meta?.layer as number || 0
}

// 获取当前功能ID
export const getCurrentFunctionId = (): string | null => {
  const currentRoute = router.currentRoute.value
  return currentRoute.params.functionId as string || null
}

// 检查是否在功能页面
export const isInFunctionPage = (): boolean => {
  return !!getCurrentFunctionId()
}

// 检查是否在工程师工具箱
export const isInEngineerToolbox = (): boolean => {
  const currentRoute = router.currentRoute.value
  return currentRoute.name === 'EngineerToolbox'
}