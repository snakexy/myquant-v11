import { IPaneApi } from '../api/ipane-api';
import { IPanePrimitive } from '../api/ipane-primitive-api';
import { DeepPartial } from '../helpers/strict-type-checks';
/**
 * Interface for a primitive with options.
 */
export interface IPanePrimitiveWithOptions<T, K> extends IPanePrimitive<T> {
    /**
     * @param options - Options to apply. The options are deeply merged with the current options.
     */
    applyOptions?: (options: DeepPartial<K>) => void;
}
/**
 * Interface for a pane primitive.
 */
export interface IPanePrimitiveWrapper<T, Options> {
    /**
     * Detaches the plugin from the pane.
     */
    detach: () => void;
    /**
     * Returns the current pane.
     */
    getPane: () => IPaneApi<T>;
    /**
     * Applies options to the primitive.
     * @param options - Options to apply. The options are deeply merged with the current options.
     */
    applyOptions?: (options: DeepPartial<Options>) => void;
}
export declare class PanePrimitiveWrapper<T, Options = unknown, TPrimitive extends IPanePrimitiveWithOptions<T, Options> = IPanePrimitiveWithOptions<T, Options>> implements IPanePrimitiveWrapper<T, Options> {
    private _primitive;
    private _pane;
    constructor(pane: IPaneApi<T>, primitive: TPrimitive);
    detach(): void;
    getPane(): IPaneApi<T>;
    applyOptions(options: DeepPartial<Options>): void;
    private _attach;
}
