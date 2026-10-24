import {bounds, collisions} from './engine.js';

// Compute geometry once per board update, then share it with rendering/storage.
export function analyzePacking(pack) {
  const box = bounds(pack);
  const pairs = collisions(pack);
  return {box, pairs, bad: new Set(pairs.flat()), ok: pairs.length === 0};
}
