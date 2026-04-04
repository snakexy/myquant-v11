/**
 * 批量更新 LocalDB 工具函数（状态栏版本）
 */

import { ElMessage } from 'element-plus';
import { h, createApp, nextTick } from 'vue';
import BatchUpdateStatusbar from './BatchUpdateStatusbar.vue';

interface BatchUpdateOptions {
  symbols: string[];
  periods?: string[];
  source?: string;
  autoClose?: boolean;
  autoMinimize?: boolean; // 完成后自动最小化
}

interface BatchUpdateResult {
  success: boolean;
  task_id?: string;
  total?: number;
  results?: Record<string, { success: boolean; count?: number; error?: string }>;
}

/**
 * 批量更新 LocalDB（状态栏模式）
 *
 * @param options 更新选项
 * @returns Promise<boolean> 是否成功
 */
export async function batchUpdateLocalDB(options: BatchUpdateOptions): Promise<boolean> {
  const {
    symbols,
    periods = ['1d', '5m'],
    source = 'pytdx',
    autoClose = true,
    autoMinimize = true
  } = options;

  try {
    // 1. 调用 API 创建任务
    const response = await fetch('/api/v5/hotdata/update-localdb', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        symbols,
        periods,
        source
      })
    });

    if (!response.ok) {
      throw new Error(`API 错误: ${response.status}`);
    }

    const data: BatchUpdateResult = await response.json();

    if (!data.success || !data.task_id) {
      throw new Error(data.error || '创建任务失败');
    }

    // 2. 在右下角显示状态栏进度
    await showStatusbarProgress(data.task_id, autoClose, autoMinimize);

    return true;

  } catch (error) {
    console.error('[批量更新] 失败:', error);
    ElMessage.error(`批量更新失败: ${error}`);
    return false;
  }
}

/**
 * 显示状态栏进度
 */
async function showStatusbarProgress(
  taskId: string,
  autoClose: boolean,
  autoMinimize: boolean
): Promise<void> {
  return new Promise((resolve) => {
    // 创建挂载点
    const container = document.createElement('div');
    document.body.appendChild(container);

    const app = createApp({
      render() {
        return h(BatchUpdateStatusbar, {
          taskId,
          autoClose,
          autoMinimize,
          onClose: () => {
            app.unmount();
            if (container.parentNode) {
              document.body.removeChild(container);
            }
            resolve();
          },
          onComplete: (results) => {
            console.log('[批量更新] 完成:', results);
          }
        });
      }
    });

    app.mount(container);
  });
}

/**
 * 显示"建议更新 LocalDB"提示，用户可选择是否更新
 *
 * @param symbolCount 股票数量
 * @returns Promise<boolean> 用户是否选择更新
 */
export async function promptUpdateLocalDB(symbolCount: number): Promise<boolean> {
  try {
    const { ElMessageBox } = await import('element-plus');

    const result = await ElMessageBox.confirm(
      `检测到大量数据缺失（${symbolCount} 只股票），建议更新 LocalDB 以加快访问速度。\n\n是否立即更新？`,
      '建议更新本地数据库',
      {
        confirmButtonText: '立即更新',
        cancelButtonText: '稍后提醒',
        type: 'warning',
        distinguishCancelAndClose: true
      }
    );

    if (result === 'confirm') {
      // 用户选择更新，获取所有自选股列表
      const watchlistSymbols = await getWatchlistSymbols();
      if (watchlistSymbols.length > 0) {
        return await batchUpdateLocalDB({
          symbols: watchlistSymbols,
          periods: ['1d', '5m'],
          autoClose: false,
          autoMinimize: true
        });
      }
    }

    return false;

  } catch (error) {
    // 用户取消
    return false;
  }
}

/**
 * 获取自选股列表
 */
async function getWatchlistSymbols(): Promise<string[]> {
  try {
    // 从 localStorage 读取自选股
    const watchlist = localStorage.getItem('watchlist');
    if (watchlist) {
      const symbols = JSON.parse(watchlist);
      return symbols.map((s: any) => s.symbol || s);
    }
    return [];
  } catch (error) {
    console.error('[自选股] 读取失败:', error);
    return [];
  }
}

// 导出组件供单独使用
export { default as BatchUpdateStatusbar } from './BatchUpdateStatusbar.vue';
