import type { APIEndpoint } from '@/types/node-system';
import { APIStatus } from '@/types/node-system';

// API监控器类
export class APIMonitor {
  private endpoints: Map<string, APIEndpoint> = new Map();
  private healthStatus: Map<string, APIStatus> = new Map();
  private monitoringIntervals: Map<string, NodeJS.Timeout> = new Map();
  private eventListeners: Map<string, Function[]> = new Map();
  
  constructor() {
    this.setupEventSystem();
  }
  
  // 设置事件系统
  private setupEventSystem(): void {
    this.eventListeners.set('api-status-changed', []);
    this.eventListeners.set('api-error', []);
    this.eventListeners.set('api-recovered', []);
  }
  
  // 注册API端点
  registerEndpoint(endpoint: APIEndpoint): void {
    this.endpoints.set(endpoint.id, endpoint);
    this.healthStatus.set(endpoint.id, APIStatus.CHECKING);
    this.startHealthCheck(endpoint);
    
    console.log(`API端点已注册: ${endpoint.id} - ${endpoint.url}`);
  }
  
  // 开始健康检查
  private startHealthCheck(endpoint: APIEndpoint): void {
    const interval = setInterval(async () => {
      await this.checkEndpointHealth(endpoint);
    }, endpoint.healthCheckInterval);
    
    this.monitoringIntervals.set(endpoint.id, interval);
  }
  
  // 检查端点健康状态
  private async checkEndpointHealth(endpoint: APIEndpoint): Promise<void> {
    try {
      const startTime = Date.now();
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), endpoint.timeout);
      
      const response = await fetch(endpoint.url, {
        method: endpoint.method,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'X-Health-Check': 'true'
        }
      });
      
      clearTimeout(timeoutId);
      
      const responseTime = Date.now() - startTime;
      const newStatus = this.determineAPIStatus(response, responseTime, endpoint.expectedResponseTime);
      
      this.updateHealthStatus(endpoint.id, newStatus, responseTime);
      
    } catch (error) {
      let newStatus = APIStatus.UNAVAILABLE;
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          newStatus = APIStatus.ERROR;
        } else if (error.message.includes('fetch')) {
          newStatus = APIStatus.UNAVAILABLE;
        }
      }
      
      this.updateHealthStatus(endpoint.id, newStatus, 0);
      this.emit('api-error', {
        endpointId: endpoint.id,
        error: error instanceof Error ? error.message : String(error),
        timestamp: new Date()
      });
    }
  }
  
  // 确定API状态
  private determineAPIStatus(
    response: Response, 
    responseTime: number, 
    expectedTime: number
  ): APIStatus {
    if (!response.ok) {
      return APIStatus.ERROR;
    }
    
    if (responseTime > expectedTime * 2) {
      return APIStatus.DEGRADED;
    }
    
    if (responseTime > expectedTime) {
      return APIStatus.DEGRADED;
    }
    
    return APIStatus.AVAILABLE;
  }
  
  // 更新健康状态
  private updateHealthStatus(endpointId: string, status: APIStatus, responseTime: number): void {
    const previousStatus = this.healthStatus.get(endpointId);
    
    if (previousStatus !== status) {
      this.healthStatus.set(endpointId, status);
      
      const event = {
        endpointId,
        previousStatus,
        newStatus: status,
        responseTime,
        timestamp: new Date()
      };
      
      this.emit('api-status-changed', event);
      
      // 如果从错误状态恢复，发出恢复事件
      if (previousStatus === APIStatus.ERROR || previousStatus === APIStatus.UNAVAILABLE) {
        if (status === APIStatus.AVAILABLE || status === APIStatus.DEGRADED) {
          this.emit('api-recovered', {
            endpointId,
            status,
            responseTime,
            timestamp: new Date()
          });
        }
      }
    }
  }
  
  // 获取API状态
  getAPIStatus(endpointId: string): APIStatus | undefined {
    return this.healthStatus.get(endpointId);
  }
  
  // 获取所有API状态
  getAllAPIStatus(): Map<string, APIStatus> {
    return new Map(this.healthStatus);
  }
  
  // 获取API端点信息
  getEndpoint(endpointId: string): APIEndpoint | undefined {
    return this.endpoints.get(endpointId);
  }
  
  // 获取所有端点
  getAllEndpoints(): Map<string, APIEndpoint> {
    return new Map(this.endpoints);
  }
  
  // 批量注册端点
  registerEndpoints(endpoints: APIEndpoint[]): void {
    endpoints.forEach(endpoint => {
      this.registerEndpoint(endpoint);
    });
  }
  
  // 停止监控特定端点
  stopMonitoring(endpointId: string): void {
    const interval = this.monitoringIntervals.get(endpointId);
    if (interval) {
      clearInterval(interval);
      this.monitoringIntervals.delete(endpointId);
      console.log(`已停止监控API端点: ${endpointId}`);
    }
  }
  
  // 停止所有监控
  stopAllMonitoring(): void {
    for (const [endpointId, interval] of this.monitoringIntervals) {
      clearInterval(interval);
    }
    this.monitoringIntervals.clear();
    console.log('已停止所有API端点监控');
  }
  
  // 重新开始监控
  restartMonitoring(): void {
    this.stopAllMonitoring();
    
    for (const endpoint of this.endpoints.values()) {
      this.startHealthCheck(endpoint);
    }
    
    console.log('已重新开始所有API端点监控');
  }
  
  // 手动检查端点
  async manualCheck(endpointId: string): Promise<void> {
    const endpoint = this.endpoints.get(endpointId);
    if (endpoint) {
      await this.checkEndpointHealth(endpoint);
    }
  }
  
  // 获取健康统计
  getHealthStats(): {
    total: number;
    available: number;
    degraded: number;
    unavailable: number;
    error: number;
    checking: number;
  } {
    const stats = {
      total: this.healthStatus.size,
      available: 0,
      degraded: 0,
      unavailable: 0,
      error: 0,
      checking: 0
    };
    
    for (const status of this.healthStatus.values()) {
      switch (status) {
        case APIStatus.AVAILABLE:
          stats.available++;
          break;
        case APIStatus.DEGRADED:
          stats.degraded++;
          break;
        case APIStatus.UNAVAILABLE:
          stats.unavailable++;
          break;
        case APIStatus.ERROR:
          stats.error++;
          break;
        case APIStatus.CHECKING:
          stats.checking++;
          break;
      }
    }
    
    return stats;
  }
  
  // 获取性能统计
  getPerformanceStats(): Map<string, { avgResponseTime: number; uptime: number }> {
    const stats = new Map();
    
    // 这里应该从历史数据中计算，现在返回模拟数据
    for (const endpointId of this.endpoints.keys()) {
      stats.set(endpointId, {
        avgResponseTime: Math.random() * 1000,
        uptime: 0.95 + Math.random() * 0.05
      });
    }
    
    return stats;
  }
  
  // 事件系统
  on(event: string, listener: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(listener);
  }
  
  off(event: string, listener: Function): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }
  
  private emit(event: string, data: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(data);
        } catch (error) {
          console.error(`事件监听器错误 (${event}):`, error);
        }
      });
    }
  }
  
  // 清理资源
  destroy(): void {
    this.stopAllMonitoring();
    this.eventListeners.clear();
    this.endpoints.clear();
    this.healthStatus.clear();
    console.log('API监控器已销毁');
  }
}

// 创建全局API监控器实例
export const apiMonitor = new APIMonitor();

// 初始化默认API端点
export function initializeDefaultEndpoints(): void {
  const defaultEndpoints: APIEndpoint[] = [
    // 数据中枢层
    {
      id: 'dh1-overview',
      url: '/api/v1/data/overview',
      method: 'GET',
      timeout: 5000,
      retryCount: 3,
      healthCheckInterval: 30000,
      expectedResponseTime: 1000
    },
    {
      id: 'dh2-query',
      url: '/api/v1/data/query',
      method: 'POST',
      timeout: 10000,
      retryCount: 3,
      healthCheckInterval: 30000,
      expectedResponseTime: 2000
    },
    {
      id: 'dh3-update',
      url: '/api/v1/data/update',
      method: 'POST',
      timeout: 15000,
      retryCount: 2,
      healthCheckInterval: 60000,
      expectedResponseTime: 5000
    },
    {
      id: 'dh4-search',
      url: '/api/v1/data/symbols/search',
      method: 'GET',
      timeout: 8000,
      retryCount: 3,
      healthCheckInterval: 30000,
      expectedResponseTime: 1500
    },
    {
      id: 'dh5-health',
      url: '/api/v1/data/health',
      method: 'GET',
      timeout: 3000,
      retryCount: 3,
      healthCheckInterval: 15000,
      expectedResponseTime: 500
    },
    
    // QLib核心层
    {
      id: 'ql1-data-processing',
      url: '/api/v1/qlib_core/data_processing',
      method: 'POST',
      timeout: 10000,
      retryCount: 3,
      healthCheckInterval: 30000,
      expectedResponseTime: 2000
    },
    {
      id: 'ql2-analysis',
      url: '/api/v1/qlib_core/analysis',
      method: 'POST',
      timeout: 15000,
      retryCount: 2,
      healthCheckInterval: 45000,
      expectedResponseTime: 3000
    },
    {
      id: 'ql3-backtest',
      url: '/api/v1/qlib_core/backtest',
      method: 'POST',
      timeout: 30000,
      retryCount: 2,
      healthCheckInterval: 60000,
      expectedResponseTime: 5000
    },
    {
      id: 'ql4-computation',
      url: '/api/v1/qlib_core/computation',
      method: 'POST',
      timeout: 20000,
      retryCount: 2,
      healthCheckInterval: 45000,
      expectedResponseTime: 4000
    },
    {
      id: 'ql5-qlib-dataprocessing',
      url: '/api/v1/qlib_core/qlib_dataprocessing',
      method: 'POST',
      timeout: 12000,
      retryCount: 3,
      healthCheckInterval: 30000,
      expectedResponseTime: 2500
    },
    {
      id: 'ql6-models',
      url: '/api/v1/qlib_core/models',
      method: 'GET',
      timeout: 8000,
      retryCount: 3,
      healthCheckInterval: 30000,
      expectedResponseTime: 1500
    },
    {
      id: 'ql7-integration',
      url: '/api/v1/qlib_core/integration',
      method: 'POST',
      timeout: 10000,
      retryCount: 3,
      healthCheckInterval: 30000,
      expectedResponseTime: 2000
    }
  ];
  
  apiMonitor.registerEndpoints(defaultEndpoints);
}

// 导出API监控器
export default apiMonitor;