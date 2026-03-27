import { ensureNever } from '../../helpers/assertions';

import { TickMarkType, TimePoint } from './types';

export function defaultTickMarkFormatter(timePoint: TimePoint, tickMarkType: TickMarkType, locale: string): string {
	const formatOptions: Intl.DateTimeFormatOptions = {};

	switch (tickMarkType) {
		case TickMarkType.Year:
			formatOptions.year = 'numeric';
			break;

		case TickMarkType.Month:
			formatOptions.month = 'short';
			break;

		case TickMarkType.DayOfMonth:
			formatOptions.day = 'numeric';
			break;

		case TickMarkType.Time:
			formatOptions.hour12 = false;
			formatOptions.hour = '2-digit';
			formatOptions.minute = '2-digit';
			break;

		case TickMarkType.TimeWithSeconds:
			formatOptions.hour12 = false;
			formatOptions.hour = '2-digit';
			formatOptions.minute = '2-digit';
			formatOptions.second = '2-digit';
			break;

		default:
			ensureNever(tickMarkType);
	}

	const date = timePoint.businessDay === undefined
		? new Date(timePoint.timestamp * 1000)
		: new Date(Date.UTC(timePoint.businessDay.year, timePoint.businessDay.month - 1, timePoint.businessDay.day));

	// from given date we should use only as UTC date or timestamp
	// but to format as locale date we can convert UTC date to local date
	// 【修改】前端已传北京时间戳，插件不加偏移，直接用 UTC 方法显示
	switch (tickMarkType) {
		case TickMarkType.Year:
			return String(date.getUTCFullYear());
		case TickMarkType.Month:
			const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
			return months[date.getUTCMonth()];
		case TickMarkType.DayOfMonth:
			return String(date.getUTCDate());
		case TickMarkType.Time:
			return `${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')}`;
		case TickMarkType.TimeWithSeconds:
			return `${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')}:${String(date.getUTCSeconds()).padStart(2, '0')}`;
		default:
			ensureNever(tickMarkType);
			return '';
	}
}
