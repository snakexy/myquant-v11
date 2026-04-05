export class TextWatermarkRenderer {
    constructor(options) {
        this._private__metricsCache = new Map();
        this._private__data = options;
    }
    draw(target) {
        target.useMediaCoordinateSpace((scope) => {
            if (!this._private__data.visible) {
                return;
            }
            const { context: ctx, mediaSize } = scope;
            let textHeight = 0;
            for (const line of this._private__data.lines) {
                if (line.text.length === 0) {
                    continue;
                }
                ctx.font = line._internal_font;
                const textWidth = this._private__metrics(ctx, line.text);
                if (textWidth > mediaSize.width) {
                    line._internal_zoom = mediaSize.width / textWidth;
                }
                else {
                    line._internal_zoom = 1;
                }
                textHeight += line.lineHeight * line._internal_zoom;
            }
            let vertOffset = 0;
            switch (this._private__data.vertAlign) {
                case 'top':
                    vertOffset = 0;
                    break;
                case 'center':
                    vertOffset = Math.max((mediaSize.height - textHeight) / 2, 0);
                    break;
                case 'bottom':
                    vertOffset = Math.max(mediaSize.height - textHeight, 0);
                    break;
            }
            for (const line of this._private__data.lines) {
                ctx.save();
                ctx.fillStyle = line.color;
                let horzOffset = 0;
                switch (this._private__data.horzAlign) {
                    case 'left':
                        ctx.textAlign = 'left';
                        horzOffset = line.lineHeight / 2;
                        break;
                    case 'center':
                        ctx.textAlign = 'center';
                        horzOffset = mediaSize.width / 2;
                        break;
                    case 'right':
                        ctx.textAlign = 'right';
                        horzOffset = mediaSize.width - 1 - line.lineHeight / 2;
                        break;
                }
                ctx.translate(horzOffset, vertOffset);
                ctx.textBaseline = 'top';
                ctx.font = line._internal_font;
                ctx.scale(line._internal_zoom, line._internal_zoom);
                ctx.fillText(line.text, 0, line._internal_vertOffset);
                ctx.restore();
                vertOffset += line.lineHeight * line._internal_zoom;
            }
        });
    }
    _private__metrics(ctx, text) {
        const fontCache = this._private__fontCache(ctx.font);
        let result = fontCache.get(text);
        if (result === undefined) {
            result = ctx.measureText(text).width;
            fontCache.set(text, result);
        }
        return result;
    }
    _private__fontCache(font) {
        let fontCache = this._private__metricsCache.get(font);
        if (fontCache === undefined) {
            fontCache = new Map();
            this._private__metricsCache.set(font, fontCache);
        }
        return fontCache;
    }
}
