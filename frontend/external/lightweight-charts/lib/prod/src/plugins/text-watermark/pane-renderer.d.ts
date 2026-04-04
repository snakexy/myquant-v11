import { CanvasRenderingTarget2D } from 'fancy-canvas';
import { IPrimitivePaneRenderer } from '../../model/ipane-primitive';
import { TextWatermarkLineOptions, TextWatermarkOptions } from './options';
export interface TextWatermarkLineRendererOptions extends TextWatermarkLineOptions {
    zoom: number;
    vertOffset: number;
    font: string;
    lineHeight: number;
}
export interface TextWatermarkRendererOptions extends TextWatermarkOptions {
    lines: TextWatermarkLineRendererOptions[];
}
export declare class TextWatermarkRenderer implements IPrimitivePaneRenderer {
    private _data;
    private _metricsCache;
    constructor(options: TextWatermarkRendererOptions);
    draw(target: CanvasRenderingTarget2D): void;
    private _metrics;
    private _fontCache;
}
