import type { Time } from 'lightweight-charts/typings';
import type { WhiskerData } from './types';

interface OHLCVBar {
	time: Time;
	open: number;
	high: number;
	low: number;
	close: number;
	volume?: number;
}

/**
 * 将 OHLCV K线数据转换为箱线图数据
 * 使用滑动窗口内的 close 价格计算四分位数
 * @param bars K线数据
 * @param windowSize 滑动窗口大小（默认20根K线）
 */
export function ohlcvToWhiskerData(bars: OHLCVBar[], windowSize = 20): WhiskerData[] {
	return bars.map((bar, index) => {
		const start = Math.max(0, index - windowSize + 1);
		const window = bars.slice(start, index + 1);
		const closes = window.map(b => b.close).sort((a, b) => a - b);
		const n = closes.length;

		const q = (percentile: number) => {
			const pos = (n - 1) * percentile / 100;
			const lower = Math.floor(pos);
			const upper = Math.ceil(pos);
			if (lower === upper) return closes[lower];
			return closes[lower] + (closes[upper] - closes[lower]) * (pos - lower);
		};

		return {
			time: bar.time,
			quartiles: [q(0), q(25), q(50), q(75), q(100)],
		};
	});
}
