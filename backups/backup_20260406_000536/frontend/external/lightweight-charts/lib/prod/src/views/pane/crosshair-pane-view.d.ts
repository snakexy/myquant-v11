import { Crosshair } from '../../model/crosshair';
import { Pane } from '../../model/pane';
import { IPaneRenderer } from '../../renderers/ipane-renderer';
import { IPaneView } from './ipane-view';
export declare class CrosshairPaneView implements IPaneView {
    private _invalidated;
    private readonly _pane;
    private readonly _source;
    private readonly _rendererData;
    private _renderer;
    constructor(source: Crosshair, pane: Pane);
    update(): void;
    renderer(pane: Pane): IPaneRenderer;
    private _updateImpl;
}
