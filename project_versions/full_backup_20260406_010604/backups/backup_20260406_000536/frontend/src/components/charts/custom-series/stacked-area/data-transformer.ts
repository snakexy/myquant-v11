import type { Time } from 'lightweight-charts/typings';
import type { StackedAreaData } from './types';

/**
 * 多股涨跌幅数据转换为堆叠面积图数据
 * @param times 时间序列
 * @param symbols 股票代码列表
 * @param dataMap 每只股票的涨跌幅数据 { [symbol]: number[] }
 */
export function multiStockToStackedAreaData(
	times: Time[],
	symbols: string[],
	dataMap: Record<string, number[]>
): StackedAreaData[] {
	return times.map((time, i) => ({
		time,
		values: symbols.map(s => Math.abs(dataMap[s]?.[i] ?? 0))
	}));
}

/**
 * 生成模拟堆叠面积数据（用于开发测试）
 * @param count 数据点数量
 * @param groups 堆叠层数量
 */
export function generateMockStackedAreaData(count: number, groups: number): StackedAreaData[] {
	const data: StackedAreaData[] = [];
	const baseDate = new Date('2024-01-01').getTime() / 1000;
	for (let i = 0; i < count; i++) {
		data.push({
			time: (baseDate + i * 86400) as Time,
			values: Array.from({ length: groups }, () => Math.random() * 5 + 0.5)
		});
	}
	return data;
}
