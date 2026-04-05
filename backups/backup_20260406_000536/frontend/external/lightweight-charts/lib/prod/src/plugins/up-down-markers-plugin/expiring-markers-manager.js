export class ExpiringMarkerManager {
    constructor(updateCallback) {
        this._private__markers = new Map();
        this._private__updateCallback = updateCallback;
    }
    _internal_setMarker(marker, key, timeout) {
        this._internal_clearMarker(key);
        if (timeout !== undefined) {
            const timeoutId = window.setTimeout(() => {
                this._private__markers.delete(key);
                this._private__triggerUpdate();
            }, timeout);
            const markerWithTimeout = {
                ...marker,
                _internal_timeoutId: timeoutId,
                _internal_expiresAt: Date.now() + timeout,
            };
            this._private__markers.set(key, markerWithTimeout);
        }
        else {
            // For markers without timeout, we set timeoutId and expiresAt to undefined
            this._private__markers.set(key, {
                ...marker,
                _internal_timeoutId: undefined,
                _internal_expiresAt: undefined,
            });
        }
        this._private__triggerUpdate();
    }
    _internal_clearMarker(key) {
        const marker = this._private__markers.get(key);
        if (marker && marker._internal_timeoutId !== undefined) {
            window.clearTimeout(marker._internal_timeoutId);
        }
        this._private__markers.delete(key);
        this._private__triggerUpdate();
    }
    _internal_clearAllMarkers() {
        for (const [point] of this._private__markers) {
            this._internal_clearMarker(point);
        }
    }
    _internal_getMarkers() {
        const now = Date.now();
        const activeMarkers = [];
        for (const [time, marker] of this._private__markers) {
            if (!marker._internal_expiresAt || marker._internal_expiresAt > now) {
                activeMarkers.push({ time: marker.time, sign: marker.sign, value: marker.value });
            }
            else {
                this._internal_clearMarker(time);
            }
        }
        return activeMarkers;
    }
    _internal_setUpdateCallback(callback) {
        this._private__updateCallback = callback;
    }
    _private__triggerUpdate() {
        if (this._private__updateCallback) {
            this._private__updateCallback();
        }
    }
}
