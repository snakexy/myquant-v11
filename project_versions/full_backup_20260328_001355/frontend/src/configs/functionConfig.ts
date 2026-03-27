/**
 * 功能模块配置
 * 定义六大功能模块及其在各层级的配置（三层架构 + 独立工程师工具箱）
 */

// 功能模块类型定义
export interface FunctionModule {
  id: string
  name: string
  description: string
  icon: string
  category: string
  status: 'online' | 'offline' | 'warning' | 'error'
  metrics?: Array<{
    label: string
    value: string
    trend?: 'up' | 'down' | 'stable'
  }>
  layers: LayerConfig[]
}

// 层级配置
export interface LayerConfig {
  level: number
  name: string
  description: string
  path: string
  component: string
  features: string[]
  permissions?: string[]
}

// 工程师工具配置
export interface EngineerTool {
  id: string
  name: string
  description: string
  icon: string
  component: string
  features: string[]
  permissions?: string[]
}

// 六大功能模块配置（三层架构）
export const functionModules: FunctionModule[] = [
  {
    id: 'data-management',
    name: '数据管理',
    description: '数据库查看、数据新鲜度监控、数据质量分析',
    icon: 'database',
    category: 'core',
    status: 'online',
    metrics: [
      { label: '股票总数', value: '4,521', trend: 'up' },
      { label: '数据新鲜度', value: '98.5%', trend: 'stable' },
      { label: '更新频率', value: '实时' }
    ],
    layers: [
      {
        level: 1,
        name: '数据概览',
        description: '查看数据库统计、数据新鲜度、股票分类',
        path: '/function/data-management',
        component: 'DataOverview',
        features: ['数据统计', '新鲜度监控', '分类查看', '导入导出']
      },
      {
        level: 2,
        name: '数据架构',
        description: '数据流架构图、节点状态监控、数据血缘',
        path: '/function/data-management/architecture',
        component: 'DataArchitecture',
        features: ['数据流可视化', '节点监控', '血缘追踪', '性能分析']
      },
      {
        level: 3,
        name: '数据监控',
        description: '实时数据质量监控、异常检测、预警系统',
        path: '/function/data-management/monitoring',
        component: 'DataMonitoring',
        features: ['质量监控', '异常检测', '预警墙', '历史对比']
      }
    ]
  },
  {
    id: 'backtest',
    name: '回测功能',
    description: '多模型对比、参数优化、回测结果分析',
    icon: 'experiment',
    category: 'analysis',
    status: 'online',
    metrics: [
      { label: '运行中回测', value: '12', trend: 'up' },
      { label: '完成回测', value: '1,248', trend: 'stable' },
      { label: '成功率', value: '87.3%' }
    ],
    layers: [
      {
        level: 1,
        name: '回测实验室',
        description: '策略回测、参数配置、多模型对比',
        path: '/function/backtest',
        component: 'BacktestLab',
        features: ['策略配置', '参数优化', '模型对比', '结果分析']
      },
      {
        level: 2,
        name: '回测架构',
        description: '回测流程架构、数据处理流程、性能监控',
        path: '/function/backtest/architecture',
        component: 'BacktestArchitecture',
        features: ['流程可视化', '性能监控', '瓶颈分析', '优化建议']
      },
      {
        level: 3,
        name: '回测监控',
        description: '实时回测进度、资源使用、结果监控',
        path: '/function/backtest/monitoring',
        component: 'BacktestMonitoring',
        features: ['进度监控', '资源监控', '结果对比', '性能分析']
      }
    ]
  },
  {
    id: 'ai-strategy',
    name: '策略生成与分析',
    description: 'AI实时分析、指标组合优化、智能策略生成',
    icon: 'robot',
    category: 'ai',
    status: 'online',
    metrics: [
      { label: '活跃策略', value: '48', trend: 'up' },
      { label: 'AI建议', value: '156', trend: 'up' },
      { label: '准确率', value: '92.1%' }
    ],
    layers: [
      {
        level: 1,
        name: 'AI策略助手',
        description: '智能对话、策略生成、实时分析',
        path: '/function/ai-strategy',
        component: 'AIStrategyAssistant',
        features: ['智能对话', '策略生成', '实时分析', '指标优化']
      },
      {
        level: 2,
        name: '策略架构',
        description: 'AI处理流程、模型架构、数据流向',
        path: '/function/ai-strategy/architecture',
        component: 'StrategyArchitecture',
        features: ['AI流程图', '模型架构', '数据流向', '处理监控']
      },
      {
        level: 3,
        name: '策略监控',
        description: '策略性能监控、AI建议跟踪、效果评估',
        path: '/function/ai-strategy/monitoring',
        component: 'StrategyMonitoring',
        features: ['性能监控', '建议跟踪', '效果评估', 'A/B测试']
      }
    ]
  },
  {
    id: 'trading-monitor',
    name: '实盘交易与监控',
    description: '多时间框架分析、预警系统、模拟交易',
    icon: 'trading',
    category: 'trading',
    status: 'online',
    metrics: [
      { label: '监控股票', value: '234', trend: 'stable' },
      { label: '活跃预警', value: '18', trend: 'down' },
      { label: '收益率', value: '+12.4%', trend: 'up' }
    ],
    layers: [
      {
        level: 1,
        name: '实盘交易',
        description: '实时交易监控、多时间框架分析、预警系统',
        path: '/function/trading-monitor',
        component: 'TradingMonitor',
        features: ['实时监控', '多时间框架', '预警系统', '模拟交易']
      },
      {
        level: 2,
        name: '交易架构',
        description: '交易系统架构、订单流处理、风险控制',
        path: '/function/trading-monitor/architecture',
        component: 'TradingArchitecture',
        features: ['系统架构', '订单流', '风险控制', '执行监控']
      },
      {
        level: 3,
        name: '交易监控',
        description: '多屏对比、实时预警、性能监控',
        path: '/function/trading-monitor/monitoring',
        component: 'TradingMonitoring',
        features: ['多屏对比', '实时预警', '性能监控', '风险监控']
      }
    ]
  },
  {
    id: 'system-monitor',
    name: '系统监控',
    description: '股票软件式界面、多阶段走势、系统健康度',
    icon: 'monitor',
    category: 'system',
    status: 'online',
    metrics: [
      { label: '系统负载', value: '67%', trend: 'stable' },
      { label: '响应时间', value: '124ms', trend: 'down' },
      { label: '可用性', value: '99.8%', trend: 'stable' }
    ],
    layers: [
      {
        level: 1,
        name: '系统总览',
        description: '系统健康度、性能指标、资源使用情况',
        path: '/function/system-monitor',
        component: 'SystemMonitor',
        features: ['健康监控', '性能指标', '资源监控', '告警中心']
      },
      {
        level: 2,
        name: '系统架构',
        description: '系统组件架构、服务依赖关系、数据流向',
        path: '/function/system-monitor/architecture',
        component: 'SystemArchitecture',
        features: ['组件架构', '依赖关系', '数据流向', '服务拓扑']
      },
      {
        level: 3,
        name: '系统监控',
        description: '多维度监控、自定义面板、预警墙',
        path: '/function/system-monitor/monitoring',
        component: 'SystemMonitoring',
        features: ['多维监控', '自定义面板', '预警墙', '性能分析']
      }
    ]
  },
  {
    id: 'model-management',
    name: '模型管理',
    description: '在线滚动训练、元学习引擎、模型可解释性',
    icon: 'chart',
    category: 'ml',
    status: 'online',
    metrics: [
      { label: '活跃模型', value: '36', trend: 'up' },
      { label: '训练任务', value: '8', trend: 'stable' },
      { label: '模型准确率', value: '89.7%' }
    ],
    layers: [
      {
        level: 1,
        name: '模型管理',
        description: '模型生命周期管理、训练任务监控、性能评估',
        path: '/function/model-management',
        component: 'ModelManagement',
        features: ['模型管理', '训练监控', '性能评估', '版本控制']
      },
      {
        level: 2,
        name: '模型架构',
        description: '模型训练架构、数据处理流程、元学习引擎',
        path: '/function/model-management/architecture',
        component: 'ModelArchitecture',
        features: ['训练架构', '数据流程', '元学习引擎', '模型拓扑']
      },
      {
        level: 3,
        name: '模型监控',
        description: '训练进度监控、性能指标跟踪、资源使用',
        path: '/function/model-management/monitoring',
        component: 'ModelMonitoring',
        features: ['进度监控', '性能跟踪', '资源监控', '自动调优']
      }
    ]
  }
]

// 独立的工程师工具箱模块
export const engineerToolbox = {
  id: 'engineer-toolbox',
  name: '工程师工具箱',
  description: '深度调试、性能分析、代码级调试工具集',
  icon: 'tools',
  category: 'debug',
  status: 'online',
  permissions: ['admin', 'developer'],
  tools: [
    {
      id: 'data-debug',
      name: '数据调试工具',
      description: '数据溯源、问题诊断、性能分析',
      icon: 'database-debug',
      component: 'DataDebugTool',
      features: ['数据溯源', '问题诊断', '性能分析', '日志查看'],
      permissions: ['admin', 'developer']
    },
    {
      id: 'backtest-debug',
      name: '回测调试工具',
      description: '回测问题诊断、性能调优、代码级调试',
      icon: 'experiment-debug',
      component: 'BacktestDebugTool',
      features: ['问题诊断', '性能调优', '代码调试', '日志分析'],
      permissions: ['admin', 'developer']
    },
    {
      id: 'strategy-debug',
      name: '策略调试工具',
      description: 'AI模型调试、策略优化、深度分析',
      icon: 'robot-debug',
      component: 'StrategyDebugTool',
      features: ['模型调试', '策略优化', '深度分析', '参数调优'],
      permissions: ['admin', 'developer', 'ml-engineer']
    },
    {
      id: 'trading-debug',
      name: '交易调试工具',
      description: '交易问题诊断、订单调试、风险分析',
      icon: 'trading-debug',
      component: 'TradingDebugTool',
      features: ['问题诊断', '订单调试', '风险分析', '日志追踪'],
      permissions: ['admin', 'developer', 'trader']
    },
    {
      id: 'system-debug',
      name: '系统调试工具',
      description: '深度系统调试、性能分析、问题诊断',
      icon: 'monitor-debug',
      component: 'SystemDebugTool',
      features: ['深度调试', '性能分析', '问题诊断', '日志分析'],
      permissions: ['admin', 'developer']
    },
    {
      id: 'model-debug',
      name: '模型调试工具',
      description: '模型调试、参数优化、可解释性分析',
      icon: 'chart-debug',
      component: 'ModelDebugTool',
      features: ['模型调试', '参数优化', '可解释性', '特征分析'],
      permissions: ['admin', 'developer', 'ml-engineer']
    }
  ]
}

// 功能分类
export const functionCategories = [
  { id: 'core', name: '核心功能', color: '#2563eb' },
  { id: 'analysis', name: '分析功能', color: '#7c3aed' },
  { id: 'ai', name: 'AI功能', color: '#10b981' },
  { id: 'trading', name: '交易功能', color: '#f59e0b' },
  { id: 'system', name: '系统功能', color: '#ef4444' },
  { id: 'ml', name: '机器学习', color: '#06b6d4' },
  { id: 'debug', name: '调试工具', color: '#8b5cf6' }
]

// 层级配置（三层架构）
export const layerConfigs = [
  { level: 1, name: '功能总览', icon: 'dashboard', color: '#2563eb' },
  { level: 2, name: '架构图', icon: 'architecture', color: '#7c3aed' },
  { level: 3, name: '监控层', icon: 'monitor', color: '#f59e0b' }
]

// 获取功能模块
export const getFunctionModule = (id: string): FunctionModule | undefined => {
  return functionModules.find(module => module.id === id)
}

// 获取功能模块的层级配置
export const getLayerConfig = (functionId: string, level: number): LayerConfig | undefined => {
  const module = getFunctionModule(functionId)
  return module?.layers.find(layer => layer.level === level)
}

// 获取用户有权限的功能模块
export const getAccessibleModules = (userPermissions: string[]): FunctionModule[] => {
  return functionModules.filter(module => {
    // 检查第一层权限
    return true // 第一层对所有用户开放
  })
}

// 获取用户有权限的层级
export const getAccessibleLayers = (functionId: string, userPermissions: string[]): LayerConfig[] => {
  const module = getFunctionModule(functionId)
  if (!module) return []
  
  return module.layers.filter(layer => {
    // 如果没有权限要求，则开放
    if (!layer.permissions || layer.permissions.length === 0) return true
    
    // 检查用户是否有任一权限
    return layer.permissions.some(permission => userPermissions.includes(permission))
  })
}

// 获取用户有权限的工程师工具
export const getAccessibleTools = (userPermissions: string[]): EngineerTool[] => {
  if (!userPermissions.some(perm => ['admin', 'developer'].includes(perm))) {
    return []
  }
  
  return engineerToolbox.tools.filter(tool => {
    if (!tool.permissions || tool.permissions.length === 0) return true
    return tool.permissions.some(permission => userPermissions.includes(permission))
  })
}