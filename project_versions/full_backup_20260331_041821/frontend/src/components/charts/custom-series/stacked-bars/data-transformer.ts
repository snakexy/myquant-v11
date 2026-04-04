import type { Time } from 'lightweight-charts/typings';
import type { StackedBarsData } from './types';

/**
 * 多股数据转换为堆叠柱状图数据
 * @param times 时间序列
 * @param symbols 股票代码列表
 * @param dataMap 每只股票的数据 { [symbol]: number[] }
 */
export function multiStockToStackedBarsData(
	times: Time[],
	symbols: string[],
	dataMap: Record<string, number[]>
): StackedBarsData[] {
	return times.map((time, i) => ({
		time,
		values: symbols.map(s => Math.abs(dataMap[s]?.[i] ?? 0))
	}));
}

/**
 * 生成模拟堆叠柱状数据（用于开发测试）
 * @param count 数据点数量
 * @param groups 堆叠层数量
 */
export function generateMockStackedBarsData(count: number, groups: number): StackedBarsData[] {
	const data: StackedBarsData[] = [];
	const baseDate = new Date('2024-01-01').getTime() / 1000;
	for (let i = 0; i < count; i++) {
		data.push({
			time: (baseDate + i * 86400) as Time,
			values: Array.from({ length: groups }, () => Math.random() * 10 + 1)
		});
	}
	return data;
}
