import type {
	CustomSeriesOptions,
} from 'lightweight-charts/typings';
import { customSeriesDefaultOptions } from 'lightweight-charts';

export interface WhiskerBoxSeriesOptions extends CustomSeriesOptions {
	whiskerColor: string;
	lowerQuartileFill: string;
	upperQuartileFill: string;
	outlierColor: string;
}

export const defaultOptions: WhiskerBoxSeriesOptions = {
	...customSeriesDefaultOptions,
	whiskerColor: 'rgba(106, 27, 154, 0.6)',
	lowerQuartileFill: 'rgba(103, 58, 183, 0.3)',
	upperQuartileFill: 'rgba(233, 30, 99, 0.3)',
	outlierColor: 'rgba(149, 152, 161, 0.6)',
} as const;
