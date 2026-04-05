import { IPaneView } from '../views/pane/ipane-view';
import { HoveredObject } from './chart-model';
import { Coordinate } from './coordinate';
import { IPrimitiveHitTestSource } from './idata-source';
import { Pane } from './pane';
export interface HitTestResult {
    source: IPrimitiveHitTestSource;
    object?: HoveredObject;
    view?: IPaneView;
    cursorStyle?: string;
}
export interface HitTestPaneViewResult {
    view: IPaneView;
    object?: HoveredObject;
}
export declare function hitTestPane(pane: Pane, x: Coordinate, y: Coordinate): HitTestResult | null;
