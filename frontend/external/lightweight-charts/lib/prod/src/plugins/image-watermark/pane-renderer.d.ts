import { CanvasRenderingTarget2D } from 'fancy-canvas';
import { IPrimitivePaneRenderer } from '../../model/ipane-primitive';
import { ImageWatermarkOptions } from './options';
export interface Placement {
    x: number;
    y: number;
    height: number;
    width: number;
}
export interface ImageWatermarkRendererOptions extends ImageWatermarkOptions {
    imgElement: HTMLImageElement | null;
    imgWidth: number;
    imgHeight: number;
}
export declare class ImageWatermarkRenderer implements IPrimitivePaneRenderer {
    private _data;
    constructor(data: ImageWatermarkRendererOptions);
    draw(target: CanvasRenderingTarget2D): void;
    private _determinePlacement;
}
