import { ensureNever } from '../../helpers/assertions';
export function defaultTickMarkFormatter(timePoint, tickMarkType, locale) {
    const formatOptions = {};
    switch (tickMarkType) {
        case 0 /* TickMarkType.Year */:
            formatOptions.year = 'numeric';
            break;
        case 1 /* TickMarkType.Month */:
            formatOptions.month = 'short';
            break;
        case 2 /* TickMarkType.DayOfMonth */:
            formatOptions.day = 'numeric';
            break;
        case 3 /* TickMarkType.Time */:
            formatOptions.hour12 = false;
            formatOptions.hour = '2-digit';
            formatOptions.minute = '2-digit';
            break;
        case 4 /* TickMarkType.TimeWithSeconds */:
            formatOptions.hour12 = false;
            formatOptions.hour = '2-digit';
            formatOptions.minute = '2-digit';
            formatOptions.second = '2-digit';
            break;
        default:
            ensureNever(tickMarkType);
    }
    const date = timePoint._internal_businessDay === undefined
        ? new Date(timePoint._internal_timestamp * 1000)
        : new Date(Date.UTC(timePoint._internal_businessDay.year, timePoint._internal_businessDay.month - 1, timePoint._internal_businessDay.day));
    // from given date we should use only as UTC date or timestamp
    // but to format as locale date we can convert UTC date to local date
    // 【修改】前端已传北京时间戳，插件不加偏移，直接用 UTC 方法显示
    switch (tickMarkType) {
        case 0 /* TickMarkType.Year */:
            return String(date.getUTCFullYear());
        case 1 /* TickMarkType.Month */:
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            return months[date.getUTCMonth()];
        case 2 /* TickMarkType.DayOfMonth */:
            return String(date.getUTCDate());
        case 3 /* TickMarkType.Time */:
            return `${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')}`;
        case 4 /* TickMarkType.TimeWithSeconds */:
            return `${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')}:${String(date.getUTCSeconds()).padStart(2, '0')}`;
        default:
            ensureNever(tickMarkType);
            return '';
    }
}
