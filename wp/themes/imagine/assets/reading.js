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
    function unit(value) {
        return Number.isFinite(value) ? Math.max(0, Math.min(1, value)) : 0;
    }
    function position(raw) {
        return {active: !!raw && raw.active === true, position: unit(raw && raw.position)};
    }
    function progress(y, top, height, viewport) {
        if (![y, top, height, viewport].every(Number.isFinite)) return 0;
        const distance = height - viewport;
        return distance > 0 ? unit((y - top) / distance) : (y + viewport >= top + height ? 1 : 0);
    }
    function mount(doc, win) {
        const article = doc.querySelector('[data-imagine-reading-id]');
        const content = doc.querySelector('.imagine-paywall-body');
        if (!article || !content) return false;
        const root = doc.documentElement;
        const get = name => doc.querySelector('#imagine-reading-' + name);
        const tools = get('tools'), toggle = get('toggle'), options = get('options');
        const size = get('size'), theme = get('theme'), bar = get('progress'), percent = get('percent');
        if (![tools, toggle, options, size, theme, bar, percent].every(Boolean)) return false;
        let storage;
        try { storage = win.localStorage; } catch (_) { /* Lecture disponible sans stockage. */ }
        const prefix = 'imagine-reading:v1:';
        // Aucun compte ni texte stocké ; pas de reprise du texte complet dans l'extrait.
        const key = prefix + 'position:' + article.getAttribute('data-imagine-reading-id') + ':' + content.textContent.length;
        const prefs = preferences(read(storage, prefix + 'preferences'));
        const saved = position(read(storage, key));
        let active = false, fraction = saved.position, pending = false, timer;
        function apply() {
            root.setAttribute('data-imagine-reading-theme', prefs.theme);
            root.setAttribute('data-imagine-reading-size', prefs.size);
            size.value = prefs.size;
            theme.value = prefs.theme;
        }
        function measure() {
            const rect = content.getBoundingClientRect();
            return {top: rect.top + win.scrollY, height: rect.height};
        }
        function save() { write(storage, key, {active, position: fraction}); }
        function update() {
            const m = measure();
            const value = progress(win.scrollY, m.top, m.height, win.innerHeight);
            bar.value = Math.round(value * 100);
            percent.textContent = bar.value + ' %';
            if (active) fraction = value;
        }
        function restore() {
            const target = fraction;
            win.requestAnimationFrame(() => {
                if (!active) return;
                if (target > 0) {
                    const m = measure();
                    // Pas d'animation, y compris lorsque prefers-reduced-motion est actif.
                    win.scrollTo({top: m.top + target * Math.max(0, m.height - win.innerHeight), behavior: 'instant'});
                }
                update();
            });
        }
        function activate(next) {
            if (active) update();
            active = next;
            root.classList.toggle('imagine-reading', active);
            toggle.setAttribute('aria-pressed', String(active));
            toggle.textContent = toggle.getAttribute(active ? 'data-exit-label' : 'data-enter-label');
            options.hidden = !active;
            apply();
            save();
            if (active) restore();
        }
        function schedule() {
            if (pending) return;
            pending = true;
            win.requestAnimationFrame(() => {
                pending = false;
                update();
                if (active) {
                    win.clearTimeout(timer);
                    timer = win.setTimeout(save, 150);
                }
            });
        }
        function change() {
            if (active) update();
            Object.assign(prefs, preferences({size: size.value, theme: theme.value}));
            apply();
            write(storage, prefix + 'preferences', prefs);
            if (active) restore();
        }
        toggle.addEventListener('click', () => activate(!active));
        size.addEventListener('change', change);
        theme.addEventListener('change', change);
        doc.addEventListener('keydown', event => {
            if (event.key === 'Escape' && active) { activate(false); toggle.focus(); }
        });
        doc.addEventListener('visibilitychange', () => { if (doc.hidden) save(); });
        win.addEventListener('scroll', schedule, {passive: true});
        win.addEventListener('resize', schedule);
        win.addEventListener('pagehide', save);
        win.addEventListener('load', () => { if (active) restore(); });
        apply();
        tools.hidden = false;
        if (saved.active) activate(true);
        else update();
        return true;
    }
    const api = {preferences, read, write, position, progress, mount};
    if (typeof module === 'object' && module.exports) module.exports = api;
    if (typeof document === 'object') mount(document, window);
}());
