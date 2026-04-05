import { IPrimitivePaneRenderer, IPrimitivePaneView } from '../../model/ipane-primitive';
import { TextWatermarkOptions } from './options';
export declare class TextWatermarkPaneView implements IPrimitivePaneView {
    private _options;
    constructor(options: TextWatermarkOptions);
    update(options: TextWatermarkOptions): void;
    renderer(): IPrimitivePaneRenderer;
}
