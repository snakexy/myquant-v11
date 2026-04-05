import { PaneRendererBaselineArea } from '../../renderers/baseline-renderer-area';
import { PaneRendererBaselineLine } from '../../renderers/baseline-renderer-line';
import { CompositeRenderer } from '../../renderers/composite-renderer';
import { LinePaneViewBase } from './line-pane-view-base';
export class SeriesBaselinePaneView extends LinePaneViewBase {
    constructor(series, model) {
        super(series, model);
        this._internal__renderer = new CompositeRenderer();
        this._private__baselineAreaRenderer = new PaneRendererBaselineArea();
        this._private__baselineLineRenderer = new PaneRendererBaselineLine();
        this._internal__renderer._internal_setRenderers([this._private__baselineAreaRenderer, this._private__baselineLineRenderer]);
    }
    _internal__createRawItem(time, price, colorer) {
        return {
            ...this._internal__createRawItemBase(time, price),
            ...colorer._internal_barStyle(time),
        };
    }
    _internal__prepareRendererData() {
        const firstValue = this._internal__series._internal_firstValue();
        if (firstValue === null) {
            return;
        }
        const options = this._internal__series._internal_options();
        const baseLevelCoordinate = this._internal__series._internal_priceScale()._internal_priceToCoordinate(options.baseValue.price, firstValue._internal_value);
        const barWidth = this._internal__model._internal_timeScale()._internal_barSpacing();
        if (this._internal__itemsVisibleRange === null || this._internal__items.length === 0) {
            return;
        }
        let topCoordinate;
        let bottomCoordinate;
        if (options.relativeGradient) {
            topCoordinate = this._internal__items[this._internal__itemsVisibleRange.from]._internal_y;
            bottomCoordinate = this._internal__items[this._internal__itemsVisibleRange.from]._internal_y;
            for (let i = this._internal__itemsVisibleRange.from; i < this._internal__itemsVisibleRange.to; i++) {
                const item = this._internal__items[i];
                if (item._internal_y < topCoordinate) {
                    topCoordinate = item._internal_y;
                }
                if (item._internal_y > bottomCoordinate) {
                    bottomCoordinate = item._internal_y;
                }
            }
        }
        this._private__baselineAreaRenderer._internal_setData({
            _internal_items: this._internal__items,
            _internal_lineWidth: options.lineWidth,
            _internal_lineStyle: options.lineStyle,
            _internal_lineType: options.lineType,
            _internal_baseLevelCoordinate: baseLevelCoordinate,
            _internal_topCoordinate: topCoordinate,
            _internal_bottomCoordinate: bottomCoordinate,
            _internal_invertFilledArea: false,
            _internal_visibleRange: this._internal__itemsVisibleRange,
            _internal_barWidth: barWidth,
        });
        this._private__baselineLineRenderer._internal_setData({
            _internal_items: this._internal__items,
            _internal_lineWidth: options.lineWidth,
            _internal_lineStyle: options.lineStyle,
            _internal_lineType: options.lineVisible ? options.lineType : undefined,
            _internal_pointMarkersRadius: options.pointMarkersVisible ? (options.pointMarkersRadius || options.lineWidth / 2 + 2) : undefined,
            _internal_baseLevelCoordinate: baseLevelCoordinate,
            _internal_topCoordinate: topCoordinate,
            _internal_bottomCoordinate: bottomCoordinate,
            _internal_visibleRange: this._internal__itemsVisibleRange,
            _internal_barWidth: barWidth,
        });
    }
}
