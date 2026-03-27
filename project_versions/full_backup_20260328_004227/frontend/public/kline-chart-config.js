/**
 * K线图配置管理器
 * 管理窗口高度和激活指标的持久化
 */

class KlineChartConfigManager {
    constructor() {
        this.storageKey = 'kline-chart-config';
        this.config = this.loadConfig();
    }

    /**
     * 加载配置
     */
    loadConfig() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (saved) {
                console.log('[ConfigManager] 加载保存的配置:', saved);
                return JSON.parse(saved);
            }
        } catch (e) {
            console.warn('[ConfigManager] 加载配置失败:', e);
        }

        // 返回默认配置
        return {
            activeIndicators: {},
            chartHeights: {
                'main-chart-container': 400,
                'MACD': 150,
                'KDJ': 150,
                'RSI': 120,
                'CCI': 120,
                'WR': 120,
                'ATR': 120,
                'OBV': 120
            }
        };
    }

    /**
     * 保存配置
     */
    saveConfig() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.config));
            console.log('[ConfigManager] 配置已保存');
        } catch (e) {
            console.warn('[ConfigManager] 保存配置失败:', e);
        }
    }

    /**
     * 更新激活的指标
     */
    updateActiveIndicators(activeIndicators) {
        this.config.activeIndicators = { ...activeIndicators };
        this.saveConfig();
    }

    /**
     * 获取激活的指标
     */
    getActiveIndicators() {
        return this.config.activeIndicators || {};
    }

    /**
     * 更新图表高度
     */
    updateChartHeight(chartId, height) {
        if (!this.config.chartHeights) {
            this.config.chartHeights = {};
        }
        this.config.chartHeights[chartId] = height;
        this.saveConfig();
    }

    /**
     * 获取图表高度
     */
    getChartHeight(chartId) {
        return this.config.chartHeights && this.config.chartHeights[chartId];
    }

    /**
     * 获取所有图表高度
     */
    getAllChartHeights() {
        return this.config.chartHeights || {};
    }

    /**
     * 清除配置
     */
    clearConfig() {
        localStorage.removeItem(this.storageKey);
        this.config = this.loadConfig();
        console.log('[ConfigManager] 配置已清除');
    }
}

// 创建全局实例
const configManager = new KlineChartConfigManager();
