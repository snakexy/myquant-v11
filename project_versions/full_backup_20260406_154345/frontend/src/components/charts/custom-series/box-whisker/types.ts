import type { CustomData } from 'lightweight-charts/typings';

/**
 * Whisker Series Data - 箱线图数据接口
 * quartiles: [q0(0%), q1(25%), q2(50%), q3(75%), q4(100%)]
 * outliers: 可选的异常值列表
 */
export interface WhiskerData extends CustomData {
	quartiles: [number, number, number, number, number];
	outliers?: number[];
}
