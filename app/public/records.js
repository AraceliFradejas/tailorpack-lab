import {bounds, valid} from './engine.js';
import {analyzePacking} from './metrics.js';

const KEY = 'tailorpack.records.v1';

export function createRecordStore(storage) {
  let records = {};
  const checked = new Set();
  try {
    const raw = storage?.getItem(KEY) || '{}';
    if (raw.length < 4_000_000) records = JSON.parse(raw);
    if (!records || typeof records !== 'object' || Array.isArray(records)) records = {};
  } catch { records = {}; }

  function get(n) {
    if (!checked.has(n)) {
      const saved = records[n];
      try {
        if (saved && (!Array.isArray(saved.pack) || !valid(saved.pack, n) ||
            !Number.isFinite(saved.L) || Math.abs(bounds(saved.pack).L - saved.L) > 1e-12)) {
          delete records[n];
        }
      } catch { delete records[n]; }
      checked.add(n);
    }
    const saved = records[n];
    // Callers cannot mutate the stored incumbent.
    return saved ? structuredClone(saved) : null;
  }

  function record(n, pack, analysis = analyzePacking(pack)) {
    if (pack.length !== n || !analysis.ok) return false;
    const previous = get(n);
    if (previous && analysis.box.L >= previous.L) return false;
    records[n] = {L: analysis.box.L, pack: structuredClone(pack)};
    checked.add(n);
    try { storage?.setItem(KEY, JSON.stringify(records)); } catch { /* Storage is optional. */ }
    return true;
  }

  return {get, record};
}
