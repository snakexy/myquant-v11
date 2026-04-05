import { numberToStringWithLeadingZero } from './price-formatter';
export class TimeFormatter {
    constructor(format) {
        this._private__formatStr = format || '%h:%m:%s';
    }
    _internal_format(date) {
        // 加8小时时区偏移（UTC → 北京时间）
        const localDate = new Date(date.getTime() + 8 * 60 * 60 * 1000);
        return this._private__formatStr.replace('%h', numberToStringWithLeadingZero(localDate.getHours(), 2)).
            replace('%m', numberToStringWithLeadingZero(localDate.getMinutes(), 2)).
            replace('%s', numberToStringWithLeadingZero(localDate.getSeconds(), 2));
    }
}
