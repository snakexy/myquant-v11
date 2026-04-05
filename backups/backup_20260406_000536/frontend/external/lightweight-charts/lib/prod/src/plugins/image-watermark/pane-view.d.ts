import { IPrimitivePaneRenderer, IPrimitivePaneView, PrimitivePaneViewZOrder } from '../../model/ipane-primitive';
import { ImageWatermarkOptions } from './options';
interface ImageWatermarkPaneViewState {
    image: HTMLImageElement | null;
    imageWidth: number;
    imageHeight: number;
}
export declare class ImageWatermarkPaneView<T> implements IPrimitivePaneView {
    private _options;
    private _rendererOptions;
    private _image;
    private _imageWidth;
    private _imageHeight;
    constructor(options: ImageWatermarkOptions);
    stateUpdate(state: ImageWatermarkPaneViewState): void;
    optionsUpdate(options: ImageWatermarkOptions): void;
    zOrder(): PrimitivePaneViewZOrder;
    update(): void;
    renderer(): IPrimitivePaneRenderer;
}
export {};
