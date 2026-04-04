import { IPaneRenderer } from '../renderers/ipane-renderer';
import { IPaneView } from '../views/pane/ipane-view';
import { Coordinate } from './coordinate';
import { IPanePrimitiveBase, IPrimitivePaneView, PrimitiveHoveredItem, PrimitivePaneViewZOrder } from './ipane-primitive';
import { ISeriesPrimitiveBase } from './iseries-primitive';
export interface ISeriesPrimitivePaneViewWrapper extends IPaneView {
    zOrder(): PrimitivePaneViewZOrder;
}
declare class PrimitivePaneViewWrapper implements IPaneView {
    private readonly _paneView;
    private _cache;
    constructor(paneView: IPrimitivePaneView);
    renderer(): IPaneRenderer | null;
    zOrder(): PrimitivePaneViewZOrder;
}
export declare abstract class PrimitiveWrapper<T extends ISeriesPrimitiveBase<TAttachedParameters> | IPanePrimitiveBase<TAttachedParameters>, TAttachedParameters = unknown> {
    protected readonly _primitive: T;
    private _paneViewsCache;
    constructor(primitive: T);
    primitive(): T;
    updateAllViews(): void;
    paneViews(): readonly ISeriesPrimitivePaneViewWrapper[] | readonly PrimitivePaneViewWrapper[];
    hitTest(x: Coordinate, y: Coordinate): PrimitiveHoveredItem | null;
}
export declare class PanePrimitiveWrapper extends PrimitiveWrapper<IPanePrimitiveBase<unknown>> {
    labelPaneViews(): readonly IPaneView[];
}
export {};
