import {bounds,grid,repair,valid,rng,fivePattern,HALF_PI} from './engine.js';

export function createSearch(n,initial,{seed=42,budget=2500,method='annealing'}={}){
  if(!Number.isInteger(budget)||budget<1||budget>50000||!['greedy','annealing'].includes(method)) throw new Error('Presupuesto o método no válido');
  if(!Number.isInteger(seed)||seed<0||seed>4294967295) throw new Error('Semilla no válida');
  if(!Array.isArray(initial)||initial.length!==n) throw new Error('El estado inicial debe contener exactamente n cuadrados');
  for(const s of initial) if(!s||![s.x,s.y,s.angle].every(Number.isFinite)) throw new Error('Coordenadas iniciales no válidas');
  const random=rng(seed),normal=()=>Math.sqrt(-2*Math.log(Math.max(random(),1e-12)))*Math.cos(2*Math.PI*random());
  let best=grid(n),bestL=bounds(best).L;
  if(valid(initial,n)&&bounds(initial).L<bestL){best=structuredClone(initial);bestL=bounds(best).L;}
  let current=valid(initial,n)?structuredClone(initial):(repair(initial)||grid(n));
  // An explicit starting family, not a claimed discovery of the solver.
  if(n===5&&bounds(current).L>=3) current=fivePattern(0);
  let currentL=bounds(current).L,step=0,accepted=0;
  return {
    advance(count=50){
      if(!Number.isInteger(count)||count<1) throw new Error('El lote debe ser un entero positivo');
      for(let k=0;k<count&&step<budget;k++,step++){
        const fraction=step/Math.max(1,budget-1),cycle=fraction<1?(fraction*4)%1:1;
        const temperature=.20*(1-cycle)**2+.00005,size=.12*(1-cycle)+.005;
        const i=Math.floor(random()*n),proposal=current.slice(),s=proposal[i];
        proposal[i]={x:s.x+normal()*size,y:s.y+normal()*size,angle:((s.angle+normal()*size*2)%HALF_PI+HALF_PI)%HALF_PI};
        const candidate=repair(proposal);if(!candidate) continue;
        const L=bounds(candidate).L,delta=L-currentL,draw=random();
        if(delta<=0||(method==='annealing'&&draw<Math.exp(-delta/temperature))){current=candidate;currentL=L;accepted++;}
        if(L<bestL&&valid(candidate,n)){best=candidate;bestL=L;}
      }
      return {step,budget,done:step>=budget,best:structuredClone(best),L:bestL,accepted};
    }
  };
}
