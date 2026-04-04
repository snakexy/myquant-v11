import { FormatterBase } from './formatter-base';
import { IPriceFormatter } from './iprice-formatter';
export declare class VolumeFormatter extends FormatterBase implements IPriceFormatter {
    private readonly _precision;
    constructor(precision: number);
    format(vol: number): string;
    private _formatNumber;
}
