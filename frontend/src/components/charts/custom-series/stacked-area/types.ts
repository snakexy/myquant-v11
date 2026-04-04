import type { CustomData } from 'lightweight-charts/typings';

/**
 * StackedArea Series Data - 堆叠面积图数据接口
 * values: 每个堆叠层的数值数组（所有值必须 >= 0）
 */
export interface StackedAreaData extends CustomData {
	values: number[];
}
