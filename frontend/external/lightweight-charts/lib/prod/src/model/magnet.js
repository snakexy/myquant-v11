import { ensure } from '../helpers/assertions';
import { Series } from './series';
const magnetPlotRowKeys = [
    3 /* PlotRowValueIndex.Close */,
];
const magnetOHLCPlotRowKeys = [
    0 /* PlotRowValueIndex.Open */,
    1 /* PlotRowValueIndex.High */,
    2 /* PlotRowValueIndex.Low */,
    3 /* PlotRowValueIndex.Close */,
];
export class Magnet {
    constructor(options) {
        this._private__options = options;
    }
    _internal_align(price, index, pane) {
        let res = price;
        if (this._private__options.mode === 0 /* CrosshairMode.Normal */) {
            return res;
        }
        const defaultPriceScale = pane._internal_defaultPriceScale();
        const firstValue = defaultPriceScale._internal_firstValue();
        if (firstValue === null) {
            return res;
        }
        const y = defaultPriceScale._internal_priceToCoordinate(price, firstValue);
        // get all serieses from the pane
        const serieses = pane._internal_dataSources().filter(((ds) => (ds instanceof Series)));
        const candidates = serieses.reduce((acc, series) => {
            if (pane._internal_isOverlay(series) || !series._internal_visible()) {
                return acc;
            }
            const ps = series._internal_priceScale();
            const bars = series._internal_bars();
            if (ps._internal_isEmpty() || !bars._internal_contains(index)) {
                return acc;
            }
            const bar = bars._internal_valueAt(index);
            if (bar === null) {
                return acc;
            }
            // convert bar to pixels
            const firstPrice = ensure(series._internal_firstValue());
            const plotRowKeys = this._private__options.mode === 3 /* CrosshairMode.MagnetOHLC */
                ? magnetOHLCPlotRowKeys
                : magnetPlotRowKeys;
            return acc.concat(plotRowKeys.map((key) => ps._internal_priceToCoordinate(bar._internal_value[key], firstPrice._internal_value)));
        }, []);
        if (candidates.length === 0) {
            return res;
        }
        candidates.sort((y1, y2) => Math.abs(y1 - y) - Math.abs(y2 - y));
        const nearest = candidates[0];
        res = defaultPriceScale._internal_coordinateToPrice(nearest, firstValue);
        return res;
    }
}
