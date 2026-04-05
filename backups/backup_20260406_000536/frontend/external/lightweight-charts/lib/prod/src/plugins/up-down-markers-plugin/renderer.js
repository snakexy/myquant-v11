;
export class MarkersPrimitiveRenderer {
    constructor(data, neutralColor, negativeColor, positiveColor) {
        this._private__data = data;
        this._private__neutralColor = neutralColor;
        this._private__negativeColor = negativeColor;
        this._private__positiveColor = positiveColor;
    }
    draw(target) {
        target.useBitmapCoordinateSpace((scope) => {
            const ctx = scope.context;
            const tickWidth = Math.max(1, Math.floor(scope.horizontalPixelRatio));
            const correction = (tickWidth % 2) / 2;
            const rad = 4 /* Constants.Radius */ * scope.verticalPixelRatio + correction;
            this._private__data.forEach((item) => {
                const centreX = Math.round(item._internal_x * scope.horizontalPixelRatio) + correction;
                ctx.beginPath();
                const color = this._private__getColor(item._internal_sign);
                ctx.fillStyle = color;
                ctx.arc(centreX, item._internal_y * scope.verticalPixelRatio, rad, 0, 2 * Math.PI, false);
                ctx.fill();
                if (item._internal_sign) {
                    ctx.strokeStyle = color;
                    ctx.lineWidth = Math.floor(2 /* Constants.ArrowLineWidth */ * scope.horizontalPixelRatio);
                    ctx.beginPath();
                    ctx.moveTo((item._internal_x - 4.7 /* Constants.ArrowSize */) * scope.horizontalPixelRatio + correction, (item._internal_y - 7 /* Constants.ArrowOffset */ * item._internal_sign) *
                        scope.verticalPixelRatio);
                    ctx.lineTo(item._internal_x * scope.horizontalPixelRatio + correction, (item._internal_y -
                        7 /* Constants.ArrowOffset */ * item._internal_sign -
                        7 /* Constants.ArrowOffset */ * item._internal_sign * 0.5 /* Constants.VerticalScale */) *
                        scope.verticalPixelRatio);
                    ctx.lineTo((item._internal_x + 4.7 /* Constants.ArrowSize */) * scope.horizontalPixelRatio + correction, (item._internal_y - 7 /* Constants.ArrowOffset */ * item._internal_sign) *
                        scope.verticalPixelRatio);
                    ctx.stroke();
                }
            });
        });
    }
    _private__getColor(sign) {
        if (sign === 0) {
            return this._private__neutralColor;
        }
        return sign > 0 ? this._private__positiveColor : this._private__negativeColor;
    }
}
