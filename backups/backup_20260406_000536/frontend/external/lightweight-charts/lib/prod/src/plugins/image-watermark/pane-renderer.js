export class ImageWatermarkRenderer {
    constructor(data) {
        this._private__data = data;
    }
    draw(target) {
        target.useMediaCoordinateSpace((scope) => {
            const ctx = scope.context;
            const pos = this._private__determinePlacement(this._private__data, scope.mediaSize);
            if (!pos || !this._private__data._internal_imgElement) {
                return;
            }
            ctx.globalAlpha = this._private__data.alpha ?? 1;
            ctx.drawImage(this._private__data._internal_imgElement, pos._internal_x, pos._internal_y, pos._internal_width, pos._internal_height);
        });
    }
    _private__determinePlacement(data, paneSize) {
        const { maxHeight, maxWidth, _internal_imgHeight: imgHeight, _internal_imgWidth: imgWidth, padding } = data;
        const plotCentreX = Math.round(paneSize.width / 2);
        const plotCentreY = Math.round(paneSize.height / 2);
        const paddingSize = padding ?? 0;
        let availableWidth = paneSize.width - 2 * paddingSize;
        let availableHeight = paneSize.height - 2 * paddingSize;
        if (maxHeight) {
            availableHeight = Math.min(availableHeight, maxHeight);
        }
        if (maxWidth) {
            availableWidth = Math.min(availableWidth, maxWidth);
        }
        const scaleX = availableWidth / imgWidth;
        const scaleY = availableHeight / imgHeight;
        const scaleToUse = Math.min(scaleX, scaleY);
        const drawWidth = imgWidth * scaleToUse;
        const drawHeight = imgHeight * scaleToUse;
        const x = plotCentreX - 0.5 * drawWidth;
        const y = plotCentreY - 0.5 * drawHeight;
        return {
            _internal_x: x,
            _internal_y: y,
            _internal_height: drawHeight,
            _internal_width: drawWidth,
        };
    }
}
