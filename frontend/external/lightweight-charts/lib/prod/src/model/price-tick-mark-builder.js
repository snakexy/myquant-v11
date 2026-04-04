import { ensure } from '../helpers/assertions';
import { min } from '../helpers/mathex';
import { convertPriceRangeFromLog } from './price-scale-conversions';
import { PriceTickSpanCalculator } from './price-tick-span-calculator';
export class PriceTickMarkBuilder {
    constructor(priceScale, base, coordinateToLogicalFunc, logicalToCoordinateFunc) {
        this._private__marks = [];
        this._private__priceScale = priceScale;
        this._private__base = base;
        this._private__coordinateToLogicalFunc = coordinateToLogicalFunc;
        this._private__logicalToCoordinateFunc = logicalToCoordinateFunc;
    }
    _internal_tickSpan(high, low) {
        if (high < low) {
            throw new Error('high < low');
        }
        const scaleHeight = this._private__priceScale._internal_height();
        const markHeight = this._private__tickMarkHeight();
        const maxTickSpan = (high - low) * markHeight / scaleHeight;
        const spanCalculator1 = new PriceTickSpanCalculator(this._private__base, [2, 2.5, 2]);
        const spanCalculator2 = new PriceTickSpanCalculator(this._private__base, [2, 2, 2.5]);
        const spanCalculator3 = new PriceTickSpanCalculator(this._private__base, [2.5, 2, 2]);
        const spans = [];
        spans.push(spanCalculator1._internal_tickSpan(high, low, maxTickSpan), spanCalculator2._internal_tickSpan(high, low, maxTickSpan), spanCalculator3._internal_tickSpan(high, low, maxTickSpan));
        return min(spans);
    }
    _internal_rebuildTickMarks() {
        const priceScale = this._private__priceScale;
        const firstValue = priceScale._internal_firstValue();
        if (firstValue === null) {
            this._private__marks = [];
            return;
        }
        const scaleHeight = priceScale._internal_height();
        const bottom = this._private__coordinateToLogicalFunc(scaleHeight - 1, firstValue);
        const top = this._private__coordinateToLogicalFunc(0, firstValue);
        const extraTopBottomMargin = this._private__priceScale._internal_options().entireTextOnly ? this._private__fontHeight() / 2 : 0;
        const minCoord = extraTopBottomMargin;
        const maxCoord = scaleHeight - 1 - extraTopBottomMargin;
        const high = Math.max(bottom, top);
        const low = Math.min(bottom, top);
        if (high === low) {
            this._private__marks = [];
            return;
        }
        const span = this._internal_tickSpan(high, low);
        this._private__updateMarks(firstValue, span, high, low, minCoord, maxCoord);
        if (priceScale._internal_hasVisibleEdgeMarks() && this._private__shouldApplyEdgeMarks(span, low, high)) {
            const padding = this._private__priceScale._internal_getEdgeMarksPadding();
            this._private__applyEdgeMarks(firstValue, span, minCoord, maxCoord, padding, padding * 2);
        }
        const logicals = this._private__marks.map((mark) => mark._internal_logical);
        const labels = this._private__priceScale._internal_formatLogicalTickmarks(logicals);
        for (let i = 0; i < this._private__marks.length; i++) {
            this._private__marks[i]._internal_label = labels[i];
        }
    }
    _internal_marks() {
        return this._private__marks;
    }
    _private__fontHeight() {
        return this._private__priceScale._internal_fontSize();
    }
    _private__tickMarkHeight() {
        return Math.ceil(this._private__fontHeight() * this._private__priceScale._internal_options().tickMarkDensity);
    }
    _private__updateMarks(firstValue, span, high, low, minCoord, maxCoord) {
        const marks = this._private__marks;
        const priceScale = this._private__priceScale;
        let mod = high % span;
        mod += mod < 0 ? span : 0;
        const sign = (high >= low) ? 1 : -1;
        let prevCoord = null;
        let targetIndex = 0;
        for (let logical = high - mod; logical > low; logical -= span) {
            const coord = this._private__logicalToCoordinateFunc(logical, firstValue, true);
            // check if there is place for it
            // this is required for log scale
            if (prevCoord !== null && Math.abs(coord - prevCoord) < this._private__tickMarkHeight()) {
                continue;
            }
            // check if a tick mark is partially visible and skip it if entireTextOnly is true
            if (coord < minCoord || coord > maxCoord) {
                continue;
            }
            if (targetIndex < marks.length) {
                marks[targetIndex]._internal_coord = coord;
                marks[targetIndex]._internal_label = priceScale._internal_formatLogical(logical);
                marks[targetIndex]._internal_logical = logical;
            }
            else {
                marks.push({
                    _internal_coord: coord,
                    _internal_label: priceScale._internal_formatLogical(logical),
                    _internal_logical: logical,
                });
            }
            targetIndex++;
            prevCoord = coord;
            if (priceScale._internal_isLog()) {
                // recalc span
                span = this._internal_tickSpan(logical * sign, low);
            }
        }
        marks.length = targetIndex;
    }
    _private__applyEdgeMarks(firstValue, span, minCoord, maxCoord, minPadding, maxPadding) {
        const marks = this._private__marks;
        // top boundary
        const topMark = this._private__computeBoundaryPriceMark(firstValue, minCoord, minPadding, maxPadding);
        // bottom boundary
        const bottomMark = this._private__computeBoundaryPriceMark(firstValue, maxCoord, -maxPadding, -minPadding);
        const spanPx = this._private__logicalToCoordinateFunc(0, firstValue, true)
            - this._private__logicalToCoordinateFunc(span, firstValue, true);
        if (marks.length > 0 && marks[0]._internal_coord - topMark._internal_coord < spanPx / 2) {
            marks.shift();
        }
        if (marks.length > 0 && bottomMark._internal_coord - marks[marks.length - 1]._internal_coord < spanPx / 2) {
            marks.pop();
        }
        marks.unshift(topMark);
        marks.push(bottomMark);
    }
    _private__computeBoundaryPriceMark(firstValue, coord, minPadding, maxPadding) {
        const avgPadding = (minPadding + maxPadding) / 2;
        const value1 = this._private__coordinateToLogicalFunc(coord + minPadding, firstValue);
        const value2 = this._private__coordinateToLogicalFunc(coord + maxPadding, firstValue);
        const minValue = Math.min(value1, value2);
        const maxValue = Math.max(value1, value2);
        const valueSpan = Math.max(0.1, this._internal_tickSpan(maxValue, minValue));
        const value = this._private__coordinateToLogicalFunc(coord + avgPadding, firstValue);
        const roundedValue = value - (value % valueSpan);
        const roundedCoord = this._private__logicalToCoordinateFunc(roundedValue, firstValue, true);
        return { _internal_label: this._private__priceScale._internal_formatLogical(roundedValue), _internal_coord: roundedCoord, _internal_logical: roundedValue };
    }
    _private__shouldApplyEdgeMarks(span, low, high) {
        let range = ensure(this._private__priceScale._internal_priceRange());
        if (this._private__priceScale._internal_isLog()) {
            range = convertPriceRangeFromLog(range, this._private__priceScale._internal_getLogFormula());
        }
        return (range._internal_minValue() - low < span) && (high - range._internal_maxValue() < span);
    }
}
