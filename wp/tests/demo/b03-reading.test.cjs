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
