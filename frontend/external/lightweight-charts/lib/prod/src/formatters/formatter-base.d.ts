import { IPriceFormatter } from './iprice-formatter';
export declare abstract class FormatterBase implements IPriceFormatter {
    abstract format(price: number): string;
    formatTickmarks(prices: readonly number[]): string[];
}
