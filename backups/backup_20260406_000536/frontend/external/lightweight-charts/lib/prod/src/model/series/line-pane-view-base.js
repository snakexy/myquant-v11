import { undefinedIfNull } from '../../helpers/strict-type-checks';
import { SeriesPaneViewBase } from './series-pane-view-base';
export class LinePaneViewBase extends SeriesPaneViewBase {
    constructor(series, model) {
        super(series, model, true);
    }
    _internal__convertToCoordinates(priceScale, timeScale, firstValue) {
        timeScale._internal_indexesToCoordinates(this._internal__items, undefinedIfNull(this._internal__itemsVisibleRange));
        priceScale._internal_pointsArrayToCoordinates(this._internal__items, firstValue, undefinedIfNull(this._internal__itemsVisibleRange));
    }
    _internal__createRawItemBase(time, price) {
        return {
            _internal_time: time,
            _internal_price: price,
            _internal_x: NaN,
            _internal_y: NaN,
        };
    }
    _internal__fillRawPoints() {
        const colorer = this._internal__series._internal_barColorer();
        this._internal__items = this._internal__series._internal_conflatedBars()._internal_rows().map((row) => {
            const isConflated = (row._internal_originalDataCount ?? 1) > 1;
            let value;
            if (isConflated) {
                const high = row._internal_value[1 /* PlotRowValueIndex.High */];
                const low = row._internal_value[2 /* PlotRowValueIndex.Low */];
                const close = row._internal_value[3 /* PlotRowValueIndex.Close */];
                const highMove = Math.abs(high - close);
                const lowMove = Math.abs(low - close);
                // in case of conflation we want to show more extreme price to represent the range
                // and we choose the one which is further from the close price
                value = (highMove > lowMove) ? high : low;
            }
            else {
                value = row._internal_value[3 /* PlotRowValueIndex.Close */];
            }
            return this._internal__createRawItem(row._internal_index, value, colorer);
        });
    }
}
