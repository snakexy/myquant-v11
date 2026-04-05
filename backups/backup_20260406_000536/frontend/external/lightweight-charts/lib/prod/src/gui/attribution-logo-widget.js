const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="35" height="19" fill="none"><g fill-rule="evenodd" clip-path="url(#a)" clip-rule="evenodd"><path fill="var(--stroke)" d="M2 0H0v10h6v9h21.4l.5-1.3 6-15 1-2.7H23.7l-.5 1.3-.2.6a5 5 0 0 0-7-.9V0H2Zm20 17h4l5.2-13 .8-2h-7l-1 2.5-.2.5-1.5 3.8-.3.7V17Zm-.8-10a3 3 0 0 0 .7-2.7A3 3 0 1 0 16.8 7h4.4ZM14 7V2H2v6h6v9h4V7h2Z"/><path fill="var(--fill)" d="M14 2H2v6h6v9h6V2Zm12 15h-7l6-15h7l-6 15Zm-7-9a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/></g><defs><clipPath id="a"><path fill="var(--stroke)" d="M0 0h35v19H0z"/></clipPath></defs></svg>`;
const css = `a#tv-attr-logo{--fill:#131722;--stroke:#fff;position:absolute;left:10px;bottom:10px;height:19px;width:35px;margin:0;padding:0;border:0;z-index:3;}a#tv-attr-logo[data-dark]{--fill:#D1D4DC;--stroke:#131722;}`;
// This widget doesn't support dynamically responding to options changes
// because it is expected that the `attributionLogo` option won't be changed
// and this saves some bundle size.
export class AttributionLogoWidget {
    constructor(container, chart) {
        this._private__element = undefined;
        this._private__cssElement = undefined;
        this._private__theme = undefined;
        this._private__visible = false;
        this._private__container = container;
        this._private__chart = chart;
        this._private__render();
    }
    _internal_update() {
        this._private__render();
    }
    _internal_removeElement() {
        if (this._private__element) {
            this._private__container.removeChild(this._private__element);
        }
        if (this._private__cssElement) {
            this._private__container.removeChild(this._private__cssElement);
        }
        this._private__element = undefined;
        this._private__cssElement = undefined;
    }
    _private__shouldUpdate() {
        return this._private__visible !== this._private__shouldBeVisible() || this._private__theme !== this._private__themeToUse();
    }
    _private__themeToUse() {
        return this._private__chart._internal_model()._internal_colorParser()._internal_colorStringToGrayscale(this._private__chart._internal_options()['layout'].textColor) > 160
            ? 'dark'
            : 'light';
    }
    _private__shouldBeVisible() {
        return this._private__chart._internal_options()['layout'].attributionLogo;
    }
    _private__getUTMSource() {
        const url = new URL(location.href);
        if (!url.hostname) {
            // ignore local testing
            return '';
        }
        return '&utm_source=' + url.hostname + url.pathname;
    }
    _private__render() {
        if (!this._private__shouldUpdate()) {
            return;
        }
        this._internal_removeElement();
        this._private__visible = this._private__shouldBeVisible();
        if (this._private__visible) {
            this._private__theme = this._private__themeToUse();
            this._private__cssElement = document.createElement('style');
            this._private__cssElement.innerText = css;
            this._private__element = document.createElement('a');
            this._private__element.href = `https://www.tradingview.com/?utm_medium=lwc-link&utm_campaign=lwc-chart${this._private__getUTMSource()}`;
            this._private__element.title = 'Charting by TradingView';
            this._private__element.id = 'tv-attr-logo';
            this._private__element.target = '_blank';
            this._private__element.innerHTML = svg;
            this._private__element.toggleAttribute('data-dark', this._private__theme === 'dark');
            this._private__container.appendChild(this._private__cssElement);
            this._private__container.appendChild(this._private__element);
        }
    }
}
