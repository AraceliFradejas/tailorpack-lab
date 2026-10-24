import {createSearch} from './solver.js';
import {bounds,grid,valid} from './engine.js';

// Sequential runs keep a single worker and equal per-engine proposal budgets.
export function createComparison(n,initial,options={}){
  const budget=options.budget??2500;
  const engines=['v1','v2'].map(strategy=>createSearch(n,initial,{...options,strategy}));
  let phase=0,best=grid(n),L=bounds(best).L;
  if(valid(initial,n)&&bounds(initial).L<L){best=structuredClone(initial);L=bounds(best).L;}
  const results={v1:null,v2:null};
  return {advance(count=50){
    const strategy=phase===0?'v1':'v2',r=engines[phase].advance(count);
    results[strategy]={L:r.L,step:r.step,done:r.done};
    if(r.L<L){best=r.best;L=r.L;}
    const step=phase*budget+r.step,done=phase===1&&r.done;
    if(phase===0&&r.done)phase=1;
    return {step,budget:2*budget,done,best:structuredClone(best),L,strategy,comparison:structuredClone(results)};
  }};
}
