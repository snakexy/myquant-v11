import { clamp } from '../helpers/mathex';
export class GradientStyleCache {
    // eslint-disable-next-line complexity
    _internal_get(scope, params) {
        const cachedParams = this._private__params;
        const { _internal_topColor1: topColor1, _internal_topColor2: topColor2, _internal_bottomColor1: bottomColor1, _internal_bottomColor2: bottomColor2, _internal_baseLevelCoordinate: baseLevelCoordinate, _internal_topCoordinate: topCoordinate, _internal_bottomCoordinate: bottomCoordinate, } = params;
        if (this._private__cachedValue === undefined ||
            cachedParams === undefined ||
            cachedParams._internal_topColor1 !== topColor1 ||
            cachedParams._internal_topColor2 !== topColor2 ||
            cachedParams._internal_bottomColor1 !== bottomColor1 ||
            cachedParams._internal_bottomColor2 !== bottomColor2 ||
            cachedParams._internal_baseLevelCoordinate !== baseLevelCoordinate ||
            cachedParams._internal_topCoordinate !== topCoordinate ||
            cachedParams._internal_bottomCoordinate !== bottomCoordinate) {
            const { verticalPixelRatio } = scope;
            const multiplier = baseLevelCoordinate || topCoordinate > 0 ? verticalPixelRatio : 1;
            const top = topCoordinate * multiplier;
            const bottom = bottomCoordinate === scope.bitmapSize.height ? bottomCoordinate : bottomCoordinate * multiplier;
            const baseline = (baseLevelCoordinate ?? 0) * multiplier;
            const gradient = scope.context.createLinearGradient(0, top, 0, bottom);
            gradient.addColorStop(0, topColor1);
            if (baseLevelCoordinate !== null && baseLevelCoordinate !== undefined) {
                const range = bottom - top;
                const baselineRatio = clamp(((baseline - top) / range), 0, 1);
                gradient.addColorStop(baselineRatio, topColor2);
                gradient.addColorStop(baselineRatio, bottomColor1);
            }
            gradient.addColorStop(1, bottomColor2);
            this._private__cachedValue = gradient;
            this._private__params = params;
        }
        return this._private__cachedValue;
    }
}
