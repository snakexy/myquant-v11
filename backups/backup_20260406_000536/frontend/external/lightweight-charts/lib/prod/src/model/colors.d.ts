import { Nominal } from '../helpers/nominal';
/**
 * Red component of the RGB color value
 * The valid values are integers in range [0, 255]
 */
type RedComponent = Nominal<number, 'RedComponent'>;
/**
 * Green component of the RGB color value
 * The valid values are integers in range [0, 255]
 */
type GreenComponent = Nominal<number, 'GreenComponent'>;
/**
 * Blue component of the RGB color value
 * The valid values are integers in range [0, 255]
 */
type BlueComponent = Nominal<number, 'BlueComponent'>;
/**
 * Alpha component of the RGBA color value
 * The valid values are integers in range [0, 1]
 */
type AlphaComponent = Nominal<number, 'AlphaComponent'>;
export type Rgba = [RedComponent, GreenComponent, BlueComponent, AlphaComponent];
export interface ContrastColors {
    foreground: string;
    background: string;
}
export type CustomColorParser = (color: string) => Rgba | null;
export declare class ColorParser {
    private _rgbaCache;
    private _customParsers;
    constructor(customParsers: CustomColorParser[], initialCache?: Map<string, Rgba>);
    /**
     * We fallback to RGBA here since supporting alpha transformations
     * on wider color gamuts would currently be a lot of extra code
     * for very little benefit due to actual usage.
     */
    applyAlpha(color: string, alpha: number): string;
    generateContrastColors(background: string): ContrastColors;
    colorStringToGrayscale(background: string): number;
    gradientColorAtPercent(topColor: string, bottomColor: string, percent: number): string;
    private _parseColor;
}
export {};
