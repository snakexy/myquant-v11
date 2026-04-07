import type { CustomData } from 'lightweight-charts/typings';

/**
 * StackedBars Series Data - 堆叠柱状图数据接口
 * values: 每个堆叠层的数值数组（所有值必须 >= 0）
 */
export interface StackedBarsData extends CustomData {
	values: number[];
}
