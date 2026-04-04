function distanceByCoordinates(p1x, p1y, p2x, p2y) {
    return Math.hypot(p2x - p1x, p2y - p1y);
}
// eslint-disable-next-line max-params, complexity
export function walkLine(renderingScope, items, lineType, visibleRange, barWidth, 
// the values returned by styleGetter are compared using the operator !==,
// so if styleGetter returns objects, then styleGetter should return the same object for equal styles
styleGetter, finishStyledArea, dashPatternLength = 0) {
    if (items.length === 0 || visibleRange.from >= items.length || visibleRange.to <= 0) {
        return;
    }
    const { context: ctx, horizontalPixelRatio, verticalPixelRatio } = renderingScope;
    const firstItem = items[visibleRange.from];
    let currentStyle = styleGetter(renderingScope, firstItem);
    let currentStyleFirstItem = firstItem;
    if (visibleRange.to - visibleRange.from < 2) {
        const halfBarWidth = barWidth / 2;
        ctx.beginPath();
        const item1 = { _internal_x: firstItem._internal_x - halfBarWidth, _internal_y: firstItem._internal_y };
        const item2 = { _internal_x: firstItem._internal_x + halfBarWidth, _internal_y: firstItem._internal_y };
        ctx.moveTo(item1._internal_x * horizontalPixelRatio, item1._internal_y * verticalPixelRatio);
        ctx.lineTo(item2._internal_x * horizontalPixelRatio, item2._internal_y * verticalPixelRatio);
        finishStyledArea(renderingScope, currentStyle, item1, item2);
    }
    else {
        const shouldTrackDashOffset = dashPatternLength > 0;
        let accumulatedDistance = 0;
        const changeStyle = (newStyle, currentItem) => {
            finishStyledArea(renderingScope, currentStyle, currentStyleFirstItem, currentItem);
            ctx.beginPath();
            currentStyle = newStyle;
            currentStyleFirstItem = currentItem;
            if (shouldTrackDashOffset) {
                const offset = accumulatedDistance % dashPatternLength;
                ctx.lineDashOffset = offset;
                // reset to the remainder to avoid floating-point precision drift over very long series.
                accumulatedDistance = offset;
            }
        };
        let currentItem = currentStyleFirstItem;
        ctx.beginPath();
        ctx.moveTo(firstItem._internal_x * horizontalPixelRatio, firstItem._internal_y * verticalPixelRatio);
        for (let i = visibleRange.from + 1; i < visibleRange.to; ++i) {
            currentItem = items[i];
            const currentX = currentItem._internal_x * horizontalPixelRatio;
            const currentY = currentItem._internal_y * verticalPixelRatio;
            const itemStyle = styleGetter(renderingScope, currentItem);
            switch (lineType) {
                case 0 /* LineType.Simple */: {
                    ctx.lineTo(currentX, currentY);
                    if (shouldTrackDashOffset) {
                        const prevItem = items[i - 1];
                        const prevX = prevItem._internal_x * horizontalPixelRatio;
                        const prevY = prevItem._internal_y * verticalPixelRatio;
                        accumulatedDistance += distanceByCoordinates(prevX, prevY, currentX, currentY);
                    }
                    break;
                }
                case 1 /* LineType.WithSteps */: {
                    const prevItem = items[i - 1];
                    const prevY = prevItem._internal_y * verticalPixelRatio;
                    ctx.lineTo(currentX, prevY);
                    if (shouldTrackDashOffset) {
                        accumulatedDistance += Math.abs(currentItem._internal_x - prevItem._internal_x) * horizontalPixelRatio;
                    }
                    if (itemStyle !== currentStyle) {
                        changeStyle(itemStyle, currentItem);
                        ctx.lineTo(currentX, prevY);
                    }
                    ctx.lineTo(currentX, currentY);
                    if (shouldTrackDashOffset) {
                        accumulatedDistance += Math.abs(currentItem._internal_y - prevItem._internal_y) * verticalPixelRatio;
                    }
                    break;
                }
                case 2 /* LineType.Curved */: {
                    const [cp1, cp2] = getControlPoints(items, i - 1, i);
                    const cp1x = cp1._internal_x * horizontalPixelRatio;
                    const cp1y = cp1._internal_y * verticalPixelRatio;
                    const cp2x = cp2._internal_x * horizontalPixelRatio;
                    const cp2y = cp2._internal_y * verticalPixelRatio;
                    ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, currentX, currentY);
                    if (shouldTrackDashOffset) {
                        const prevItem = items[i - 1];
                        const prevX = prevItem._internal_x * horizontalPixelRatio;
                        const prevY = prevItem._internal_y * verticalPixelRatio;
                        const chord = distanceByCoordinates(prevX, prevY, currentX, currentY);
                        const controlPolygon = distanceByCoordinates(prevX, prevY, cp1x, cp1y) +
                            distanceByCoordinates(cp1x, cp1y, cp2x, cp2y) +
                            distanceByCoordinates(cp2x, cp2y, currentX, currentY);
                        accumulatedDistance += (chord + controlPolygon) / 2;
                    }
                    break;
                }
            }
            if (lineType !== 1 /* LineType.WithSteps */ && itemStyle !== currentStyle) {
                changeStyle(itemStyle, currentItem);
                ctx.moveTo(currentX, currentY);
            }
        }
        if (currentStyleFirstItem !== currentItem || currentStyleFirstItem === currentItem && lineType === 1 /* LineType.WithSteps */) {
            finishStyledArea(renderingScope, currentStyle, currentStyleFirstItem, currentItem);
        }
        if (shouldTrackDashOffset) {
            ctx.lineDashOffset = 0;
        }
    }
}
const curveTension = 6;
function subtract(p1, p2) {
    return { _internal_x: p1._internal_x - p2._internal_x, _internal_y: p1._internal_y - p2._internal_y };
}
function add(p1, p2) {
    return { _internal_x: p1._internal_x + p2._internal_x, _internal_y: p1._internal_y + p2._internal_y };
}
function divide(p1, n) {
    return { _internal_x: p1._internal_x / n, _internal_y: p1._internal_y / n };
}
/**
 * @returns Two control points that can be used as arguments to {@link CanvasRenderingContext2D.bezierCurveTo} to draw a curved line between `points[fromPointIndex]` and `points[toPointIndex]`.
 */
export function getControlPoints(points, fromPointIndex, toPointIndex) {
    const beforeFromPointIndex = Math.max(0, fromPointIndex - 1);
    const afterToPointIndex = Math.min(points.length - 1, toPointIndex + 1);
    const cp1 = add(points[fromPointIndex], divide(subtract(points[toPointIndex], points[beforeFromPointIndex]), curveTension));
    const cp2 = subtract(points[toPointIndex], divide(subtract(points[afterToPointIndex], points[fromPointIndex]), curveTension));
    return [cp1, cp2];
}
