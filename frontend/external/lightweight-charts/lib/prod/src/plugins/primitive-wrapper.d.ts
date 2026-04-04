import { IPanePrimitive, PaneAttachedParameter } from '../api/ipane-primitive-api';
import { DeepPartial } from '../helpers/strict-type-checks';
export declare abstract class PrimitiveWrapper<T, Options = unknown> {
    protected _primitive: IPanePrimitive<T>;
    protected _options: Options;
    constructor(primitive: IPanePrimitive<T>, options: Options);
    detach(): void;
    abstract applyOptions(options: DeepPartial<Options>): void;
    protected _attachToPrimitive(params: PaneAttachedParameter<T>): void;
    protected _requestUpdate(): void;
}
