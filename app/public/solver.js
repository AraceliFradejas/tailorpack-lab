import {createSearch as legacySearch} from './solver-v1.js';
import {bounds,grid,repair,valid,rng} from './engine.js';
import {cornerBlocks,startingLayout,propose} from './search-moves.js';

export function createSearch(n,initial,options={}){
  const {strategy='v1'}=options;
  if(!['v1','v2'].includes(strategy))throw new Error('Motor no válido');
  // Reuse the baseline's input validation without consuming any proposals.
  const baseline=legacySearch(n,initial,options);
  if(strategy==='v1')return baseline;
  const {seed=42,budget=2500,method='annealing'}=options;
  const random=rng(seed),normal=()=>Math.sqrt(-2*Math.log(Math.max(random(),1e-12)))*Math.cos(2*Math.PI*random());
  let best=grid(n),bestL=bounds(best).L;
  if(valid(initial,n)&&bounds(initial).L<bestL){best=structuredClone(initial);bestL=bounds(best).L;}
  let current=structuredClone(best),currentL=bestL,step=0,accepted=0,restarts=0;
  const moves={construction:0,restart:0,single:0,translate:0,cluster:0};
  const span=Math.max(1,Math.ceil(budget/4));
  return {advance(count=50){
    if(!Number.isInteger(count)||count<1)throw new Error('El lote debe ser un entero positivo');
    for(let k=0;k<count&&step<budget;k++,step++){
      const phase=Math.floor(step/span),local=(step%span)/span;
      const size=.10*(1-local)+.003,temperature=.045*(1-local)**2+.00002;
      let proposal,kind;
      if(step===0&&cornerBlocks(n)){
        kind='construction';proposal=cornerBlocks(n);
      }else if(step>0&&step%span===0){
        kind='restart';restarts++;
        proposal=phase===3?structuredClone(best):startingLayout(n,phase,random);
      }else{
        const draw=random();kind=draw<.25?'cluster':draw<.50?'translate':'single';
        proposal=propose(current,{random,normal,size,kind});
      }
      moves[kind]++;
      // Construction and restart trials count towards the SAME proposal budget.
      const candidate=repair(proposal);if(!candidate||!valid(candidate,n))continue;
      const L=bounds(candidate).L,delta=L-currentL,draw=random();
      if(kind==='restart'||delta<=0||(method==='annealing'&&draw<Math.exp(-delta/temperature))){current=candidate;currentL=L;accepted++;}
      if(L<bestL){best=candidate;bestL=L;}
    }
    return {step,budget,done:step>=budget,best:structuredClone(best),L:bestL,accepted,restarts,moves:{...moves}};
  }};
}
