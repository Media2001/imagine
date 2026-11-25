'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const script = path.resolve(__dirname, '../../themes/imagine/assets/reading.js');
function reader() {
    assert.ok(fs.existsSync(script), 'Script de lecture absent');
    return require(script);
}

test('préférences : choix autorisés et défauts prudents, même avec données corrompues', () => {
    const r = reader();
    assert.deepEqual(r.preferences({theme: 'sepia', size: 'larger'}), {theme: 'sepia', size: 'larger'});
    for (const raw of [null, [], 'dark', 3, {theme: '__proto__', size: '999'}, {}]) {
        assert.deepEqual(r.preferences(raw), {theme: 'light', size: 'large'});
    }
    assert.deepEqual(r.preferences({theme: 'dark', size: 'normal'}), {theme: 'dark', size: 'normal'});
});

test('stockage local : aller-retour, absence, corruption, refus et quota sans exception', () => {
    const r = reader();
    const data = new Map();
    const storage = {getItem: k => data.get(k) ?? null, setItem: (k,v) => data.set(k,v)};
    assert.deepEqual(r.read(storage, 'inconnu'), {});
    assert.equal(r.write(storage, 'prefs', {theme: 'dark', size: 'normal'}), true);
    assert.deepEqual(r.preferences(r.read(storage, 'prefs')), {theme: 'dark', size: 'normal'});
    data.set('casse', '{');
    assert.deepEqual(r.read(storage, 'casse'), {});
    const blocked = {getItem() { throw Error('refus'); }, setItem() { throw Error('quota'); }};
    assert.deepEqual(r.read(blocked, 'x'), {});
    assert.equal(r.write(blocked, 'x', {}), false);
    assert.deepEqual(r.read(null, 'x'), {});
    assert.equal(r.write(null, 'x', {}), false);
});

test('progression bornée sur le texte, et état de reprise validé sans coercition', () => {
    const r = reader();
    assert.equal(r.progress(0, 100, 2000, 1000), 0);
    assert.equal(r.progress(600, 100, 2000, 1000), 0.5);
    assert.equal(r.progress(5000, 100, 2000, 1000), 1);
    assert.equal(r.progress(0, 100, 100, 500), 1);
    assert.equal(r.progress(0, 1000, 100, 500), 0);
    assert.equal(r.progress(NaN, 100, 2000, 1000), 0);
    assert.deepEqual(r.position({active: true, position: 0.6}), {active: true, position: 0.6});
    assert.deepEqual(r.position({active: true, position: 9}), {active: true, position: 1});
    for (const raw of [null, {}, {active: 'true', position: '0.5'}, {position: NaN}]) {
        assert.deepEqual(r.position(raw), {active: false, position: 0});
    }
});

function environment(data = new Map(), id = '42', text = 'texte autorisé', blocked = false) {
    function element(attrs = {}) {
        const events = {};
        return {hidden: true, value: '', textContent: '', attrs,
            setAttribute(k,v) { this.attrs[k] = String(v); }, getAttribute(k) { return this.attrs[k]; },
            addEventListener(k,fn) { events[k] = fn; },
            fire(k,extra={}) { if (events[k]) events[k]({target: this, ...extra}); },
            focus() { this.focused = true; }};
    }
    const nodes = {};
    for (const name of ['tools', 'toggle', 'options', 'size', 'theme', 'progress', 'percent']) nodes[name] = element();
    nodes.toggle.attrs = {'data-enter-label': 'Lire l’article', 'data-exit-label': 'Quitter le mode lecture'};
    const article = element({'data-imagine-reading-id': id});
    const content = element(); content.textContent = text;
    const classes = new Set();
    const root = element(); root.classList = {toggle(k,on) { on ? classes.add(k) : classes.delete(k); }};
    const doc = element(); doc.documentElement = root;
    doc.querySelector = s => s === '[data-imagine-reading-id]' ? article : s === '.imagine-paywall-body' ? content : nodes[s.replace('#imagine-reading-', '')];
    const frames = [], timers = new Map(); let serial = 0;
    const win = element(); win.scrollY = 0; win.innerHeight = 800;
    win.requestAnimationFrame = fn => { frames.push(fn); };
    win.setTimeout = fn => { timers.set(++serial, fn); return serial; };
    win.clearTimeout = key => timers.delete(key);
    win.scrollTo = opts => { win.scrollY = opts.top; win.lastScroll = opts; };
    Object.defineProperty(win, 'localStorage', {get() {
        if (blocked) throw Error('localStorage refusé');
        return {getItem: k => data.get(k) ?? null, setItem: (k,v) => data.set(k,v)};
    }});
    content.getBoundingClientRect = () => ({top: 400 - win.scrollY, height: 2400});
    function flush() { while (frames.length) frames.shift()(); for (const fn of timers.values()) fn(); timers.clear(); }
    return {doc, win, nodes, classes, data, flush};
}

test('parcours DOM sans navigateur : activation, réglages, progression, reprise et sortie clavier', () => {
    const r = reader(), e = environment();
    assert.equal(r.mount(e.doc, e.win), true);
    assert.equal(e.nodes.tools.hidden, false);
    assert.equal(e.nodes.options.hidden, true);
    e.nodes.toggle.fire('click'); e.flush();
    assert.ok(e.classes.has('imagine-reading'));
    assert.equal(e.nodes.toggle.attrs['aria-pressed'], 'true');
    assert.equal(e.nodes.options.hidden, false);
    e.nodes.theme.value = 'sepia'; e.nodes.theme.fire('change'); e.flush();
    e.nodes.size.value = 'normal'; e.nodes.size.fire('change'); e.flush();
    assert.equal(e.doc.documentElement.attrs['data-imagine-reading-theme'], 'sepia');
    assert.equal(e.doc.documentElement.attrs['data-imagine-reading-size'], 'normal');
    e.win.scrollY = 1200; e.win.fire('scroll'); e.flush();
    assert.equal(e.nodes.progress.value, 50);
    assert.equal(e.nodes.percent.textContent, '50 %');
    e.win.fire('pagehide');
    const resumed = environment(e.data);
    r.mount(resumed.doc, resumed.win); resumed.flush();
    assert.ok(resumed.classes.has('imagine-reading'));
    assert.equal(resumed.win.scrollY, 1200);
    assert.equal(resumed.win.lastScroll.behavior, 'instant');
    assert.equal(resumed.nodes.theme.value, 'sepia');
    assert.equal(resumed.nodes.size.value, 'normal');
    resumed.doc.fire('keydown', {key: 'Escape'}); resumed.flush();
    assert.ok(!resumed.classes.has('imagine-reading'));
    assert.equal(resumed.nodes.toggle.attrs['aria-pressed'], 'false');
    assert.equal(resumed.nodes.options.hidden, true);
    assert.ok(resumed.nodes.toggle.focused);
    const afterExit = environment(e.data); r.mount(afterExit.doc, afterExit.win); afterExit.flush();
    assert.ok(!afterExit.classes.has('imagine-reading'));
    assert.ok([...e.data.values()].every(v => !v.includes('texte autorisé')));
});

test('reprise isolée par article et longueur du texte servi ; stockage indisponible et page hors article', () => {
    const r = reader(), e = environment();
    r.mount(e.doc, e.win); e.nodes.toggle.fire('click'); e.flush(); e.win.fire('pagehide');
    for (const other of [environment(e.data, '43'), environment(e.data, '42', 'extrait')]) {
        r.mount(other.doc, other.win); other.flush();
        assert.ok(!other.classes.has('imagine-reading'));
    }
    const blocked = environment(new Map(), '42', 'texte', true);
    assert.equal(r.mount(blocked.doc, blocked.win), true);
    blocked.nodes.toggle.fire('click'); blocked.flush();
    assert.ok(blocked.classes.has('imagine-reading'));
    assert.equal(r.mount({querySelector() { return null; }}, {}), false);
});
