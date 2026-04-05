import { Size } from 'fancy-canvas';
import { IDestroyable } from '../helpers/idestroyable';
import { IChartWidgetBase } from './chart-widget';
export declare const enum SeparatorConstants {
    SeparatorHeight = 1,
    MinPaneHeight = 30
}
export declare class PaneSeparator implements IDestroyable {
    private readonly _chartWidget;
    private readonly _rowElement;
    private readonly _cell;
    private readonly _topPane;
    private readonly _bottomPane;
    private _handle;
    private _mouseEventHandler;
    private _resizeEnabled;
    private _resizeInfo;
    constructor(chartWidget: IChartWidgetBase, topPaneIndex: number, bottomPaneIndex: number);
    destroy(): void;
    getElement(): HTMLElement;
    getSize(): Size;
    getBitmapSize(): Size;
    drawBitmap(ctx: CanvasRenderingContext2D, x: number, y: number): void;
    update(): void;
    private _addResizableHandle;
    private _updateBorderColor;
    private _mouseOverEvent;
    private _mouseLeaveEvent;
    private _mouseDownEvent;
    private _pressedMouseMoveEvent;
    private _mouseUpEvent;
}
