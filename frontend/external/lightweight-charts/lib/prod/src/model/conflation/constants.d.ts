/**
 * Power-of-2 conflation levels supported by the system.
 * These represent the number of original data points that get merged into one conflated point.
 */
export declare const CONFLATION_LEVELS: readonly [2, 4, 8, 16, 32, 64, 128, 256, 512];
/**
 * Maximum conflation level supported.
 */
export declare const MAX_CONFLATION_LEVEL = 512;
/**
 * Device pixel ratio threshold for conflation.
 * Conflation happens when barSpacing is less than 1.0 / devicePixelRatio.
 * This ensures we only conflate when we can't physically display the detail.
 */
export declare const DPR_CONFLATION_THRESHOLD = 1;
export declare const CONFLATION_ERROR_MESSAGES: {
    readonly missingPriceValueBuilder: "Custom series with conflation reducer must have a priceValueBuilder method";
};
