import { size } from 'fancy-canvas';
import { clamp } from '../helpers/mathex';
import { MouseEventHandler } from './mouse-event-handler';
;
export class PaneSeparator {
    constructor(chartWidget, topPaneIndex, bottomPaneIndex) {
        this._private__handle = null;
        this._private__mouseEventHandler = null;
        this._private__resizeEnabled = true;
        this._private__resizeInfo = null;
        this._private__chartWidget = chartWidget;
        this._private__topPane = chartWidget._internal_paneWidgets()[topPaneIndex];
        this._private__bottomPane = chartWidget._internal_paneWidgets()[bottomPaneIndex];
        this._private__rowElement = document.createElement('tr');
        this._private__rowElement.style.height = 1 /* SeparatorConstants.SeparatorHeight */ + 'px';
        this._private__cell = document.createElement('td');
        this._private__cell.style.position = 'relative';
        this._private__cell.style.padding = '0';
        this._private__cell.style.margin = '0';
        this._private__cell.setAttribute('colspan', '3');
        this._private__updateBorderColor();
        this._private__rowElement.appendChild(this._private__cell);
        this._private__resizeEnabled = this._private__chartWidget._internal_options()['layout'].panes.enableResize;
        if (!this._private__resizeEnabled) {
            this._private__handle = null;
            this._private__mouseEventHandler = null;
        }
        else {
            this._private__addResizableHandle();
        }
    }
    _internal_destroy() {
        if (this._private__mouseEventHandler !== null) {
            this._private__mouseEventHandler._internal_destroy();
        }
    }
    _internal_getElement() {
        return this._private__rowElement;
    }
    _internal_getSize() {
        return size({
            width: this._private__topPane._internal_getSize().width,
            height: 1 /* SeparatorConstants.SeparatorHeight */,
        });
    }
    _internal_getBitmapSize() {
        return size({
            width: this._private__topPane._internal_getBitmapSize().width,
            height: 1 /* SeparatorConstants.SeparatorHeight */ * window.devicePixelRatio,
        });
    }
    _internal_drawBitmap(ctx, x, y) {
        const bitmapSize = this._internal_getBitmapSize();
        ctx.fillStyle = this._private__chartWidget._internal_options()['layout'].panes.separatorColor;
        ctx.fillRect(x, y, bitmapSize.width, bitmapSize.height);
    }
    _internal_update() {
        this._private__updateBorderColor();
        if (this._private__chartWidget._internal_options()['layout'].panes.enableResize !== this._private__resizeEnabled) {
            this._private__resizeEnabled = this._private__chartWidget._internal_options()['layout'].panes.enableResize;
            if (this._private__resizeEnabled) {
                this._private__addResizableHandle();
            }
            else {
                if (this._private__handle !== null) {
                    this._private__cell.removeChild(this._private__handle._internal_backgroundElement);
                    this._private__cell.removeChild(this._private__handle._internal_element);
                    this._private__handle = null;
                }
                if (this._private__mouseEventHandler !== null) {
                    this._private__mouseEventHandler._internal_destroy();
                    this._private__mouseEventHandler = null;
                }
            }
        }
    }
    _private__addResizableHandle() {
        const backgroundElement = document.createElement('div');
        const bgStyle = backgroundElement.style;
        bgStyle.position = 'fixed';
        bgStyle.display = 'none';
        bgStyle.zIndex = '49';
        bgStyle.top = '0';
        bgStyle.left = '0';
        bgStyle.width = '100%';
        bgStyle.height = '100%';
        bgStyle.cursor = 'row-resize';
        this._private__cell.appendChild(backgroundElement);
        const element = document.createElement('div');
        const style = element.style;
        style.position = 'absolute';
        style.zIndex = '50';
        style.top = '-4px';
        style.height = '9px';
        style.width = '100%';
        style.backgroundColor = '';
        style.cursor = 'row-resize';
        this._private__cell.appendChild(element);
        const handlers = {
            _internal_mouseEnterEvent: this._private__mouseOverEvent.bind(this),
            _internal_mouseLeaveEvent: this._private__mouseLeaveEvent.bind(this),
            _internal_mouseDownEvent: this._private__mouseDownEvent.bind(this),
            _internal_touchStartEvent: this._private__mouseDownEvent.bind(this),
            _internal_pressedMouseMoveEvent: this._private__pressedMouseMoveEvent.bind(this),
            _internal_touchMoveEvent: this._private__pressedMouseMoveEvent.bind(this),
            _internal_mouseUpEvent: this._private__mouseUpEvent.bind(this),
            _internal_touchEndEvent: this._private__mouseUpEvent.bind(this),
        };
        this._private__mouseEventHandler = new MouseEventHandler(element, handlers, {
            _internal_treatVertTouchDragAsPageScroll: () => false,
            _internal_treatHorzTouchDragAsPageScroll: () => true,
        });
        this._private__handle = { _internal_element: element, _internal_backgroundElement: backgroundElement };
    }
    _private__updateBorderColor() {
        this._private__cell.style.background = this._private__chartWidget._internal_options()['layout'].panes.separatorColor;
    }
    _private__mouseOverEvent(event) {
        if (this._private__handle !== null) {
            this._private__handle._internal_element.style.backgroundColor = this._private__chartWidget._internal_options()['layout'].panes.separatorHoverColor;
        }
    }
    _private__mouseLeaveEvent(event) {
        if (this._private__handle !== null && this._private__resizeInfo === null) {
            this._private__handle._internal_element.style.backgroundColor = '';
        }
    }
    _private__mouseDownEvent(event) {
        if (this._private__handle === null) {
            return;
        }
        const totalStretch = this._private__topPane._internal_state()._internal_stretchFactor() + this._private__bottomPane._internal_state()._internal_stretchFactor();
        const totalHeight = this._private__topPane._internal_getSize().height + this._private__bottomPane._internal_getSize().height;
        const pixelStretchFactor = totalStretch / totalHeight;
        const minPaneStretch = 30 /* SeparatorConstants.MinPaneHeight */ * pixelStretchFactor;
        if (totalStretch <= minPaneStretch * 2) {
            // cannot resize panes that already have less than minimal height
            // that's possible if there are many panes on the chart
            return;
        }
        this._private__resizeInfo = {
            _internal_startY: event.pageY,
            _internal_prevStretchTopPane: this._private__topPane._internal_state()._internal_stretchFactor(),
            _internal_maxPaneStretch: totalStretch - minPaneStretch,
            _internal_totalStretch: totalStretch,
            _internal_pixelStretchFactor: pixelStretchFactor,
            _internal_minPaneStretch: minPaneStretch,
        };
        this._private__handle._internal_backgroundElement.style.display = 'block';
    }
    _private__pressedMouseMoveEvent(event) {
        const resizeInfo = this._private__resizeInfo;
        if (resizeInfo === null) {
            return;
        }
        const deltaY = event.pageY - resizeInfo._internal_startY;
        const deltaStretchFactor = deltaY * resizeInfo._internal_pixelStretchFactor;
        const upperPaneNewStretch = clamp(resizeInfo._internal_prevStretchTopPane + deltaStretchFactor, resizeInfo._internal_minPaneStretch, resizeInfo._internal_maxPaneStretch);
        this._private__topPane._internal_state()._internal_setStretchFactor(upperPaneNewStretch);
        this._private__bottomPane._internal_state()._internal_setStretchFactor(resizeInfo._internal_totalStretch - upperPaneNewStretch);
        this._private__chartWidget._internal_model()._internal_fullUpdate();
    }
    _private__mouseUpEvent(event) {
        if (this._private__resizeInfo === null || this._private__handle === null) {
            return;
        }
        this._private__resizeInfo = null;
        this._private__handle._internal_backgroundElement.style.display = 'none';
    }
}
