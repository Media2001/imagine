/* Mode lecture Imagine : autonome, sans requête réseau. */
(function () {
    'use strict';
    function preferences(raw) {
        raw = raw || {};
        return {
            theme: ['light', 'sepia', 'dark'].includes(raw.theme) ? raw.theme : 'light',
            size: ['normal', 'large', 'larger'].includes(raw.size) ? raw.size : 'large'
        };
    }
    function read(storage, key) {
        try { return JSON.parse(storage.getItem(key)) || {}; } catch (_) { return {}; }
    }
    function write(storage, key, value) {
        try { storage.setItem(key, JSON.stringify(value)); return true; } catch (_) { return false; }
    }
    const api = {preferences, read, write};
    if (typeof module === 'object' && module.exports) module.exports = api;
}());
