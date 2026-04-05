import { ensureNotNull } from '../../helpers/assertions';
import { notNull } from '../../helpers/strict-type-checks';
import { MarkersPrimitiveRenderer } from './renderer';
function isAreaStyleOptions(opts, seriesType) {
    return seriesType === 'Area';
}
function getNeutralColor(opts, seriesType) {
    if (isAreaStyleOptions(opts, seriesType)) {
        return opts.lineColor;
    }
    return opts.color;
}
export class MarkersPrimitivePaneView {
    constructor(series, timeScale, options) {
        this._private__data = [];
        this._private__series = series;
        this._private__timeScale = timeScale;
        this._private__options = options;
    }
    _internal_update(markers) {
        this._private__data = markers.map((marker) => {
            const y = this._private__series.priceToCoordinate(marker.value);
            if (y === null) {
                return null;
            }
            const x = ensureNotNull(this._private__timeScale.timeToCoordinate(marker.time));
            return {
                _internal_x: x,
                _internal_y: y,
                _internal_sign: marker.sign,
            };
        })
            .filter(notNull);
    }
    renderer() {
        const options = this._private__series.options();
        const seriesType = this._private__series.seriesType();
        const neutralColor = getNeutralColor(options, seriesType);
        return new MarkersPrimitiveRenderer(this._private__data, neutralColor, this._private__options.negativeColor, this._private__options.positiveColor);
    }
}
