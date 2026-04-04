import { Delegate } from '../../helpers/delegate';
function createDebouncedMicroTaskHandler(callback) {
    let scheduled = false;
    return function (...args) {
        if (!scheduled) {
            scheduled = true;
            queueMicrotask(() => {
                callback(...args);
                scheduled = false;
            });
        }
    };
}
function markWithGreaterWeight(a, b) {
    return a.weight > b.weight ? a : b;
}
function toInternalHorzScaleItem(item) {
    return item;
}
function fromInternalHorzScaleItem(item) {
    return item;
}
export class YieldCurveHorzScaleBehavior {
    constructor() {
        this._private__pointsChangedDelegate = new Delegate();
        this._private__invalidateWhitespace = createDebouncedMicroTaskHandler(() => this._private__pointsChangedDelegate._internal_fire(this._private__largestIndex));
        this._private__largestIndex = 0;
    }
    /** Data changes might require that the whitespace be generated again */
    _internal_whitespaceInvalidated() {
        return this._private__pointsChangedDelegate;
    }
    _internal_destroy() {
        this._private__pointsChangedDelegate._internal_destroy();
    }
    options() {
        return this._private__options;
    }
    setOptions(options) {
        this._private__options = options;
    }
    preprocessData(data) {
        // No preprocessing needed for yield curve data
    }
    updateFormatter(options) {
        if (!this._private__options) {
            return;
        }
        this._private__options.localization = options;
    }
    createConverterToInternalObj(data) {
        this._private__invalidateWhitespace();
        return (time) => {
            if (time > this._private__largestIndex) {
                this._private__largestIndex = time;
            }
            return toInternalHorzScaleItem(time);
        };
    }
    key(internalItem) {
        return internalItem;
    }
    cacheKey(internalItem) {
        return fromInternalHorzScaleItem(internalItem);
    }
    convertHorzItemToInternal(item) {
        return toInternalHorzScaleItem(item);
    }
    formatHorzItem(item) {
        return this._private__formatTime(item);
    }
    formatTickmark(item) {
        return this._private__formatTime(item.time);
    }
    maxTickMarkWeight(marks) {
        return marks.reduce(markWithGreaterWeight, marks[0]).weight;
    }
    fillWeightsForPoints(sortedTimePoints, startIndex) {
        const timeWeight = (time) => {
            if (time % 120 === 0) {
                return 10;
            }
            if (time % 60 === 0) {
                return 9;
            }
            if (time % 36 === 0) {
                return 8;
            }
            if (time % 12 === 0) {
                return 7;
            }
            if (time % 6 === 0) {
                return 6;
            }
            if (time % 3 === 0) {
                return 5;
            }
            if (time % 1 === 0) {
                return 4;
            }
            return 0;
        };
        for (let index = startIndex; index < sortedTimePoints.length; ++index) {
            sortedTimePoints[index].timeWeight = timeWeight(fromInternalHorzScaleItem(sortedTimePoints[index].time));
        }
        this._private__largestIndex = fromInternalHorzScaleItem(sortedTimePoints[sortedTimePoints.length - 1].time);
        this._private__invalidateWhitespace();
    }
    _private__formatTime(months) {
        if (this._private__options.localization?.timeFormatter) {
            return this._private__options.localization.timeFormatter(months);
        }
        if (months < 12) {
            return `${months}M`;
        }
        const years = Math.floor(months / 12);
        const remainingMonths = months % 12;
        if (remainingMonths === 0) {
            return `${years}Y`;
        }
        return `${years}Y${remainingMonths}M`;
    }
}
