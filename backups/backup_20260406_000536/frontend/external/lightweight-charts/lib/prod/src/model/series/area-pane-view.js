import { PaneRendererArea } from '../../renderers/area-renderer';
import { CompositeRenderer } from '../../renderers/composite-renderer';
import { PaneRendererLine } from '../../renderers/line-renderer';
import { LinePaneViewBase } from './line-pane-view-base';
export class SeriesAreaPaneView extends LinePaneViewBase {
    constructor(series, model) {
        super(series, model);
        this._internal__renderer = new CompositeRenderer();
        this._private__areaRenderer = new PaneRendererArea();
        this._private__lineRenderer = new PaneRendererLine();
        this._internal__renderer._internal_setRenderers([this._private__areaRenderer, this._private__lineRenderer]);
    }
    _internal__createRawItem(time, price, colorer) {
        return {
            ...this._internal__createRawItemBase(time, price),
            ...colorer._internal_barStyle(time),
        };
    }
    _internal__prepareRendererData() {
        const options = this._internal__series._internal_options();
        if (this._internal__itemsVisibleRange === null || this._internal__items.length === 0) {
            return;
        }
        let topCoordinate;
        if (options.relativeGradient) {
            topCoordinate = this._internal__items[this._internal__itemsVisibleRange.from]._internal_y;
            for (let i = this._internal__itemsVisibleRange.from; i < this._internal__itemsVisibleRange.to; i++) {
                const item = this._internal__items[i];
                if (item._internal_y < topCoordinate) {
                    topCoordinate = item._internal_y;
                }
            }
        }
        this._private__areaRenderer._internal_setData({
            _internal_lineType: options.lineType,
            _internal_items: this._internal__items,
            _internal_lineStyle: options.lineStyle,
            _internal_lineWidth: options.lineWidth,
            _internal_baseLevelCoordinate: null,
            _internal_topCoordinate: topCoordinate,
            _internal_invertFilledArea: options.invertFilledArea,
            _internal_visibleRange: this._internal__itemsVisibleRange,
            _internal_barWidth: this._internal__model._internal_timeScale()._internal_barSpacing(),
        });
        this._private__lineRenderer._internal_setData({
            _internal_lineType: options.lineVisible ? options.lineType : undefined,
            _internal_items: this._internal__items,
            _internal_lineStyle: options.lineStyle,
            _internal_lineWidth: options.lineWidth,
            _internal_visibleRange: this._internal__itemsVisibleRange,
            _internal_barWidth: this._internal__model._internal_timeScale()._internal_barSpacing(),
            _internal_pointMarkersRadius: options.pointMarkersVisible ? (options.pointMarkersRadius || options.lineWidth / 2 + 2) : undefined,
        });
    }
}
