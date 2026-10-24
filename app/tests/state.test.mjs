import test from 'node:test';
import assert from 'node:assert/strict';
import {grid, square} from '../public/engine.js';
import {analyzePacking} from '../public/metrics.js';
import {createRecordStore} from '../public/records.js';
import {renderPieces} from '../public/board-view.js';
import {createSearch} from '../public/solver.js';

function memory(initial = '{}') {
  let raw = initial;
  return {getItem: () => raw, setItem: (_, value) => {raw = value;}};
}

test('persisted records survive reload and cannot be mutated by callers', () => {
  const storage = memory();
  const store = createRecordStore(storage);
  store.record(5, grid(5));
  const snapshot = store.get(5);
  snapshot.L = -1;
  snapshot.pack[0].x = -100;
  assert.equal(store.get(5).L, 3);
  assert.equal(createRecordStore(storage).get(5).L, 3);
});

test('malformed, forged and overlapping saved records are discarded', () => {
  for (const raw of ['not-json', '[]', 'null', JSON.stringify({5: {L: 1, pack: grid(5)}}),
    JSON.stringify({2: {L: 1, pack: [square(0, 0), square(0, 0)]}})]) {
    const store = createRecordStore(memory(raw));
    assert.equal(store.get(5), null);
    assert.equal(store.get(2), null);
  }
});

test('storage failure does not break play and worse or invalid records never replace best', () => {
  const store = createRecordStore({getItem() {throw Error();}, setItem() {throw Error();}});
  assert.equal(store.record(2, grid(2)), true);
  assert.equal(store.record(2, [square(0, 0), square(0, 0)]), false);
  assert.equal(store.record(2, [square(0, 0), square(3, 0)]), false);
  assert.equal(store.get(2).L, 2);
});

test('shared metrics and visual skin retain collision IDs and all six face colors', () => {
  const pack = grid(6);
  pack[1] = {...pack[0]};
  const analysis = analyzePacking(pack);
  assert.equal(analysis.ok, false);
  assert.ok(analysis.bad.has(0) && analysis.bad.has(1));
  const markup = renderPieces(pack, {selected: 0, bad: analysis.bad});
  for (let i = 0; i < 6; i++) assert.ok(markup.includes(`data-tone="${i}"`));
  assert.ok(markup.includes('Cuadrado 1, solapado'));
});

test('solver rejects malformed starts, seeds and non-progressing batches', () => {
  assert.throws(() => createSearch(5, grid(2)));
  assert.throws(() => createSearch(1, [{x: NaN, y: 0, angle: 0}]));
  assert.throws(() => createSearch(1, grid(1), {seed: -1}));
  assert.throws(() => createSearch(1, grid(1)).advance(0));
});
