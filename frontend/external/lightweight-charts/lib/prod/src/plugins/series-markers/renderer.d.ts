import { BitmapCoordinatesRenderingScope, CanvasRenderingTarget2D } from 'fancy-canvas';
import { Coordinate } from '../../model/coordinate';
import { IPrimitivePaneRenderer, PrimitiveHoveredItem } from '../../model/ipane-primitive';
import { SeriesItemsIndexesRange, TimedValue } from '../../model/time-data';
import { SeriesMarkerZOrder } from './options';
import { SeriesMarkerShape } from './types';
export interface SeriesMarkerText {
    content: string;
    x: Coordinate;
    y: Coordinate;
    width: number;
    height: number;
}
export interface SeriesMarkerRendererDataItem extends TimedValue {
    y: Coordinate;
    size: number;
    shape: SeriesMarkerShape;
    color: string;
    internalId: number;
    externalId?: string;
    text?: SeriesMarkerText;
}
export interface SeriesMarkerRendererData {
    items: SeriesMarkerRendererDataItem[];
    visibleRange: SeriesItemsIndexesRange | null;
}
export declare class SeriesMarkersRenderer implements IPrimitivePaneRenderer {
    private _data;
    private _textWidthCache;
    private _fontSize;
    private _fontFamily;
    private _font;
    private _zOrder;
    setData(data: SeriesMarkerRendererData): void;
    setParams(fontSize: number, fontFamily: string, zOrder: SeriesMarkerZOrder): void;
    hitTest(x: number, y: number): PrimitiveHoveredItem | null;
    draw(target: CanvasRenderingTarget2D): void;
    drawBackground(target: CanvasRenderingTarget2D): void;
    protected _drawImpl({ context: ctx, horizontalPixelRatio, verticalPixelRatio }: BitmapCoordinatesRenderingScope): void;
}
