import { CanvasRenderingTarget2D } from 'fancy-canvas';
import { IPrimitivePaneRenderer } from '../../model/ipane-primitive';
import { MarkerCoordinates } from './types';
export declare class MarkersPrimitiveRenderer implements IPrimitivePaneRenderer {
    private _data;
    private readonly _neutralColor;
    private readonly _negativeColor;
    private readonly _positiveColor;
    constructor(data: MarkerCoordinates[], neutralColor: string, negativeColor: string, positiveColor: string);
    draw(target: CanvasRenderingTarget2D): void;
    private _getColor;
}
