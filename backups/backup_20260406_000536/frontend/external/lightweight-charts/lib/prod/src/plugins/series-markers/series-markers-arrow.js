import { ceiledOdd } from '../../helpers/mathex';
import { shapeSize } from './utils';
export function drawArrow(up, ctx, coords, size) {
    const arrowSize = shapeSize('arrowUp', size);
    const halfArrowSize = ((arrowSize - 1) / 2) * coords._internal_pixelRatio;
    const baseSize = ceiledOdd(size / 2);
    const halfBaseSize = ((baseSize - 1) / 2) * coords._internal_pixelRatio;
    ctx.beginPath();
    if (up) {
        ctx.moveTo(coords._internal_x - halfArrowSize, coords._internal_y);
        ctx.lineTo(coords._internal_x, coords._internal_y - halfArrowSize);
        ctx.lineTo(coords._internal_x + halfArrowSize, coords._internal_y);
        ctx.lineTo(coords._internal_x + halfBaseSize, coords._internal_y);
        ctx.lineTo(coords._internal_x + halfBaseSize, coords._internal_y + halfArrowSize);
        ctx.lineTo(coords._internal_x - halfBaseSize, coords._internal_y + halfArrowSize);
        ctx.lineTo(coords._internal_x - halfBaseSize, coords._internal_y);
    }
    else {
        ctx.moveTo(coords._internal_x - halfArrowSize, coords._internal_y);
        ctx.lineTo(coords._internal_x, coords._internal_y + halfArrowSize);
        ctx.lineTo(coords._internal_x + halfArrowSize, coords._internal_y);
        ctx.lineTo(coords._internal_x + halfBaseSize, coords._internal_y);
        ctx.lineTo(coords._internal_x + halfBaseSize, coords._internal_y - halfArrowSize);
        ctx.lineTo(coords._internal_x - halfBaseSize, coords._internal_y - halfArrowSize);
        ctx.lineTo(coords._internal_x - halfBaseSize, coords._internal_y);
    }
    ctx.fill();
}
export function hitTestArrow(up, centerX, centerY, size, x, y) {
    const arrowSize = shapeSize('arrowUp', size);
    const halfArrowSize = (arrowSize - 1) / 2;
    const baseSize = ceiledOdd(size / 2);
    const halfBaseSize = (baseSize - 1) / 2;
    const triangleTolerance = 3;
    const rectTolerance = 2;
    const baseLeft = centerX - halfBaseSize - rectTolerance;
    const baseRight = centerX + halfBaseSize + rectTolerance;
    const baseTop = up ? centerY : centerY - halfArrowSize;
    const baseBottom = up ? centerY + halfArrowSize : centerY;
    if (x >= baseLeft && x <= baseRight &&
        y >= baseTop - rectTolerance && y <= baseBottom + rectTolerance) {
        return true;
    }
    const isInTriangleBounds = () => {
        const headLeft = centerX - halfArrowSize - triangleTolerance;
        const headRight = centerX + halfArrowSize + triangleTolerance;
        const headTop = up ? centerY - halfArrowSize - triangleTolerance : centerY;
        const headBottom = up ? centerY : centerY + halfArrowSize + triangleTolerance;
        if (x < headLeft || x > headRight ||
            y < headTop || y > headBottom) {
            return false;
        }
        const dx = Math.abs(x - centerX);
        const dy = up
            ? Math.abs(y - centerY) // up arrow
            : Math.abs(y - centerY); // down arrow
        return dy + triangleTolerance >= dx / 2;
    };
    return isInTriangleBounds();
}
