/**
 * 智能节点连接推荐API
 * 基于MyQuant v9.0.0架构的智能推荐系统
 */

import type { 
  FunctionRequirement, 
  RecommendationResult, 
  ArchitectureNode,
  NodeConnection,
  WorkflowStep,
  AlternativeSolution,
  AnalysisResult
} from '../types/recommendation';

// API基础配置
const API_BASE_URL = '/api/recommendations';
const TIMEOUT = 30000; // 30秒超时

/**
 * 智能推荐API客户端
 */
export class IntelligentRecommendationAPI {
  private static instance: IntelligentRecommendationAPI;
  
  private constructor() {}
  
  public static getInstance(): IntelligentRecommendationAPI {
    if (!IntelligentRecommendationAPI.instance) {
      IntelligentRecommendationAPI.instance = new IntelligentRecommendationAPI();
    }
    return IntelligentRecommendationAPI.instance;
  }
  
  /**
   * 生成智能推荐
   * @param requirement 功能需求
   * @returns 推荐结果
   */
  async generateRecommendation(requirement: FunctionRequirement): Promise<RecommendationResult> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requirement),
      });
      
      if (!response.ok) {
        throw new Error(`推荐生成失败: ${response.statusText}`);
      }
      
      const result = await response.json();
      return this.validateRecommendationResult(result);
    } catch (error) {
      console.error('生成推荐失败:', error);
      throw error;
    }
  }
  
  /**
   * 分析功能需求
   * @param requirement 功能需求
   * @returns 分析结果
   */
  async analyzeRequirement(requirement: FunctionRequirement): Promise<AnalysisResult> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requirement),
      });
      
      if (!response.ok) {
        throw new Error(`需求分析失败: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('需求分析失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取架构节点库
   * @returns 节点库
   */
  async getNodeLibrary(): Promise<ArchitectureNode[]> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/nodes`, {
        method: 'GET',
      });
      
      if (!response.ok) {
        throw new Error(`获取节点库失败: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('获取节点库失败:', error);
      throw error;
    }
  }
  
  /**
   * 验证节点连接
   * @param fromNode 源节点
   * @param toNode 目标节点
   * @returns 验证结果
   */
  async validateConnection(
    fromNode: ArchitectureNode, 
    toNode: ArchitectureNode
  ): Promise<{ valid: boolean; description: string; dataType?: string }> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/validate-connection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fromNode, toNode }),
      });
      
      if (!response.ok) {
        throw new Error(`连接验证失败: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('连接验证失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取推荐历史
   * @param userId 用户ID
   * @returns 推荐历史
   */
  async getRecommendationHistory(userId: string): Promise<RecommendationResult[]> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/history/${userId}`, {
        method: 'GET',
      });
      
      if (!response.ok) {
        throw new Error(`获取推荐历史失败: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('获取推荐历史失败:', error);
      throw error;
    }
  }
  
  /**
   * 保存推荐结果
   * @param result 推荐结果
   * @returns 保存结果
   */
  async saveRecommendation(result: RecommendationResult): Promise<{ success: boolean; id: string }> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(result),
      });
      
      if (!response.ok) {
        throw new Error(`保存推荐失败: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('保存推荐失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取替代方案
   * @param recommendationId 推荐ID
   * @returns 替代方案
   */
  async getAlternatives(recommendationId: string): Promise<AlternativeSolution[]> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/alternatives/${recommendationId}`, {
        method: 'GET',
      });
      
      if (!response.ok) {
        throw new Error(`获取替代方案失败: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('获取替代方案失败:', error);
      throw error;
    }
  }
  
  /**
   * 优化节点组合
   * @param nodes 节点列表
   * @param constraints 约束条件
   * @returns 优化后的节点组合
   */
  async optimizeNodeCombination(
    nodes: ArchitectureNode[], 
    constraints: { maxNodes?: number; preferredLayers?: string[] }
  ): Promise<ArchitectureNode[]> {
    try {
      const response = await this.fetchWithTimeout(`${API_BASE_URL}/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nodes, constraints }),
      });
      
      if (!response.ok) {
        throw new Error(`节点组合优化失败: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('节点组合优化失败:', error);
      throw error;
    }
  }
  
  /**
   * 带超时的fetch请求
   */
  private async fetchWithTimeout(url: string, options: RequestInit): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('请求超时');
      }
      throw error;
    }
  }
  
  /**
   * 验证推荐结果格式
   */
  private validateRecommendationResult(result: any): RecommendationResult {
    if (!result || typeof result !== 'object') {
      throw new Error('无效的推荐结果格式');
    }
    
    const requiredFields = ['id', 'requirementId', 'nodes', 'connections', 'workflow', 'confidence'];
    for (const field of requiredFields) {
      if (!(field in result)) {
        throw new Error(`推荐结果缺少必需字段: ${field}`);
      }
    }
    
    if (!Array.isArray(result.nodes) || !Array.isArray(result.connections) || !Array.isArray(result.workflow)) {
      throw new Error('推荐结果中的数组字段格式错误');
    }
    
    if (typeof result.confidence !== 'number' || result.confidence < 0 || result.confidence > 1) {
      throw new Error('置信度必须是0-1之间的数字');
    }
    
    return result as RecommendationResult;
  }
}

/**
 * 智能推荐API的便捷方法
 */
export const intelligentRecommendationAPI = {
  /**
   * 生成智能推荐
   */
  generateRecommendation: (requirement: FunctionRequirement) => 
    IntelligentRecommendationAPI.getInstance().generateRecommendation(requirement),
  
  /**
   * 分析功能需求
   */
  analyzeRequirement: (requirement: FunctionRequirement) => 
    IntelligentRecommendationAPI.getInstance().analyzeRequirement(requirement),
  
  /**
   * 获取架构节点库
   */
  getNodeLibrary: () => 
    IntelligentRecommendationAPI.getInstance().getNodeLibrary(),
  
  /**
   * 验证节点连接
   */
  validateConnection: (fromNode: ArchitectureNode, toNode: ArchitectureNode) => 
    IntelligentRecommendationAPI.getInstance().validateConnection(fromNode, toNode),
  
  /**
   * 获取推荐历史
   */
  getRecommendationHistory: (userId: string) => 
    IntelligentRecommendationAPI.getInstance().getRecommendationHistory(userId),
  
  /**
   * 保存推荐结果
   */
  saveRecommendation: (result: RecommendationResult) => 
    IntelligentRecommendationAPI.getInstance().saveRecommendation(result),
  
  /**
   * 获取替代方案
   */
  getAlternatives: (recommendationId: string) => 
    IntelligentRecommendationAPI.getInstance().getAlternatives(recommendationId),
  
  /**
   * 优化节点组合
   */
  optimizeNodeCombination: (nodes: ArchitectureNode[], constraints: any) => 
    IntelligentRecommendationAPI.getInstance().optimizeNodeCombination(nodes, constraints),
};

/**
 * 推荐状态管理
 */
export class RecommendationStateManager {
  private static instance: RecommendationStateManager;
  private recommendations: Map<string, RecommendationResult> = new Map();
  private currentRecommendation: RecommendationResult | null = null;
  
  private constructor() {}
  
  public static getInstance(): RecommendationStateManager {
    if (!RecommendationStateManager.instance) {
      RecommendationStateManager.instance = new RecommendationStateManager();
    }
    return RecommendationStateManager.instance;
  }
  
  /**
   * 设置当前推荐
   */
  setCurrentRecommendation(recommendation: RecommendationResult): void {
    this.currentRecommendation = recommendation;
    this.recommendations.set(recommendation.id, recommendation);
    
    // 保存到本地存储
    this.saveToLocalStorage();
  }
  
  /**
   * 获取当前推荐
   */
  getCurrentRecommendation(): RecommendationResult | null {
    return this.currentRecommendation;
  }
  
  /**
   * 获取推荐
   */
  getRecommendation(id: string): RecommendationResult | undefined {
    return this.recommendations.get(id);
  }
  
  /**
   * 获取所有推荐
   */
  getAllRecommendations(): RecommendationResult[] {
    return Array.from(this.recommendations.values());
  }
  
  /**
   * 删除推荐
   */
  deleteRecommendation(id: string): boolean {
    const deleted = this.recommendations.delete(id);
    if (deleted && this.currentRecommendation?.id === id) {
      this.currentRecommendation = null;
    }
    this.saveToLocalStorage();
    return deleted;
  }
  
  /**
   * 清空所有推荐
   */
  clearAllRecommendations(): void {
    this.recommendations.clear();
    this.currentRecommendation = null;
    this.saveToLocalStorage();
  }
  
  /**
   * 从本地存储加载
   */
  loadFromLocalStorage(): void {
    try {
      const stored = localStorage.getItem('intelligent_recommendations');
      if (stored) {
        const data = JSON.parse(stored);
        this.recommendations = new Map(data.recommendations || []);
        this.currentRecommendation = data.currentRecommendation || null;
      }
    } catch (error) {
      console.error('从本地存储加载推荐失败:', error);
    }
  }
  
  /**
   * 保存到本地存储
   */
  private saveToLocalStorage(): void {
    try {
      const data = {
        recommendations: Array.from(this.recommendations.entries()),
        currentRecommendation: this.currentRecommendation,
      };
      localStorage.setItem('intelligent_recommendations', JSON.stringify(data));
    } catch (error) {
      console.error('保存推荐到本地存储失败:', error);
    }
  }
}

/**
 * 推荐状态管理的便捷方法
 */
export const recommendationState = {
  setCurrentRecommendation: (recommendation: RecommendationResult) => 
    RecommendationStateManager.getInstance().setCurrentRecommendation(recommendation),
  
  getCurrentRecommendation: () => 
    RecommendationStateManager.getInstance().getCurrentRecommendation(),
  
  getRecommendation: (id: string) => 
    RecommendationStateManager.getInstance().getRecommendation(id),
  
  getAllRecommendations: () => 
    RecommendationStateManager.getInstance().getAllRecommendations(),
  
  deleteRecommendation: (id: string) => 
    RecommendationStateManager.getInstance().deleteRecommendation(id),
  
  clearAllRecommendations: () => 
    RecommendationStateManager.getInstance().clearAllRecommendations(),
  
  loadFromLocalStorage: () => 
    RecommendationStateManager.getInstance().loadFromLocalStorage(),
};

// 初始化时从本地存储加载
recommendationState.loadFromLocalStorage();