export function drawBackground(renderer, target, isHovered, hitTestData) {
    if (renderer._internal_drawBackground) {
        renderer._internal_drawBackground(target, isHovered, hitTestData);
    }
}
export function drawForeground(renderer, target, isHovered, hitTestData) {
    renderer._internal_draw(target, isHovered, hitTestData);
}
export function drawSourceViews(paneViewsGetter, drawRendererFn, source, pane) {
    const views = paneViewsGetter(source, pane);
    for (const view of views) {
        const renderer = view._internal_renderer(pane);
        if (renderer !== null) {
            drawRendererFn(renderer);
        }
    }
}
