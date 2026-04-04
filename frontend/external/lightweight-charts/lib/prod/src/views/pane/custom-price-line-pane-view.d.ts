import { CustomPriceLine } from '../../model/custom-price-line';
import { ISeries } from '../../model/iseries';
import { SeriesType } from '../../model/series-options';
import { SeriesHorizontalLinePaneView } from './series-horizontal-line-pane-view';
export declare class CustomPriceLinePaneView extends SeriesHorizontalLinePaneView {
    private readonly _priceLine;
    constructor(series: ISeries<SeriesType>, priceLine: CustomPriceLine);
    protected _updateImpl(): void;
}
