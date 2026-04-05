import { IChartModelBase } from '../../model/chart-model';
import { Crosshair } from '../../model/crosshair';
import { Pane } from '../../model/pane';
import { IPaneRenderer } from '../../renderers/ipane-renderer';
import { IUpdatablePaneView, UpdateType } from './iupdatable-pane-view';
export declare class CrosshairMarksPaneView implements IUpdatablePaneView {
    private readonly _chartModel;
    private readonly _crosshair;
    private readonly _pane;
    private readonly _compositeRenderer;
    private _markersRenderers;
    private _markersData;
    private _invalidated;
    constructor(chartModel: IChartModelBase, crosshair: Crosshair, pane: Pane);
    update(updateType?: UpdateType): void;
    renderer(): IPaneRenderer | null;
    private _createMarkerRenderersIfNeeded;
    private _updateImpl;
}
