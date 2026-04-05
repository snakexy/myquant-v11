import { numberToStringWithLeadingZero } from './price-formatter';

export class TimeFormatter {
	private _formatStr: string;

	public constructor(format?: string) {
		this._formatStr = format || '%h:%m:%s';
	}

	public format(date: Date): string {
		// 加8小时时区偏移（UTC → 北京时间）
		const localDate = new Date(date.getTime() + 8 * 60 * 60 * 1000);
		return this._formatStr.replace('%h', numberToStringWithLeadingZero(localDate.getHours(), 2)).
			replace('%m', numberToStringWithLeadingZero(localDate.getMinutes(), 2)).
			replace('%s', numberToStringWithLeadingZero(localDate.getSeconds(), 2));
	}
}
