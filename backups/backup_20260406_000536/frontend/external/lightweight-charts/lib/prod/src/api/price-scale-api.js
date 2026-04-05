import { ensureNotNull } from '../helpers/assertions';
import { isDefaultPriceScale } from '../model/default-price-scale';
import { PriceRangeImpl } from '../model/price-range-impl';
import { convertPriceRangeFromLog } from '../model/price-scale-conversions';
import { precisionByMinMove } from '../model/series-options';
export class PriceScaleApi {
    constructor(chartWidget, priceScaleId, paneIndex) {
        this._private__chartWidget = chartWidget;
        this._private__priceScaleId = priceScaleId;
        this._private__paneIndex = paneIndex ?? 0;
    }
    applyOptions(options) {
        this._private__chartWidget._internal_model()._internal_applyPriceScaleOptions(this._private__priceScaleId, options, this._private__paneIndex);
    }
    options() {
        return this._private__priceScale()._internal_options();
    }
    width() {
        if (!isDefaultPriceScale(this._private__priceScaleId)) {
            return 0;
        }
        return this._private__chartWidget._internal_getPriceAxisWidth(this._private__priceScaleId);
    }
    setVisibleRange(range) {
        this.setAutoScale(false);
        this._private__priceScale()._internal_setCustomPriceRange(new PriceRangeImpl(range.from, range.to));
    }
    getVisibleRange() {
        let range = this._private__priceScale()._internal_priceRange();
        if (range === null) {
            return null;
        }
        let from;
        let to;
        if (this._private__priceScale()._internal_isLog()) {
            const minMove = this._private__priceScale()._internal_minMove();
            const minMovePrecision = precisionByMinMove(minMove);
            range = convertPriceRangeFromLog(range, this._private__priceScale()._internal_getLogFormula());
            from = Number((Math.round(range._internal_minValue() / minMove) * minMove).toFixed(minMovePrecision));
            to = Number((Math.round(range._internal_maxValue() / minMove) * minMove).toFixed(minMovePrecision));
        }
        else {
            from = range._internal_minValue();
            to = range._internal_maxValue();
        }
        return {
            from,
            to,
        };
    }
    setAutoScale(on) {
        this.applyOptions({ autoScale: on });
    }
    _private__priceScale() {
        return ensureNotNull(this._private__chartWidget._internal_model()._internal_findPriceScale(this._private__priceScaleId, this._private__paneIndex))._internal_priceScale;
    }
}
