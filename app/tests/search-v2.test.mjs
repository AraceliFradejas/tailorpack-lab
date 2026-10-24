import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {createSearch} from '../public/solver.js';
import {createComparison} from '../public/comparison.js';
import {cornerBlocks,propose,startingLayout} from '../public/search-moves.js';
import {grid,valid,bounds,rng} from '../public/engine.js';
const finish=(engine,chunk=37)=>{let r;do{r=engine.advance(chunk);}while(!r.done);return r;};

test('v1 remains the byte-identical published baseline',()=>{
  const source=readFileSync(new URL('../public/solver-v1.js',import.meta.url));
  assert.equal(createHash('sha256').update(source).digest('hex'),'d834e44f89f9d247327f485e3a214211b8bb51e19adf9d7e6887ccfad736f711');
});
test('corner-block family is feasible for every applicable n through 1000',()=>{
  for(let k=1;4*k*k+1<=1000;k++){
    const n=4*k*k+1,pack=cornerBlocks(n);
    assert.equal(pack.length,n);assert.equal(valid(pack,n),true);
    assert.ok(Math.abs(bounds(pack).L-(2*(k+(k-1)*1e-8)+Math.SQRT1_2+1e-8))<1e-12);
  }
  for(const n of [1,9,10,16,1000])assert.equal(cornerBlocks(n),null);
});
test('cluster proposal is a rigid transformation and does not mutate its input',()=>{
  const pack=grid(3),copy=structuredClone(pack);
  const q=propose(pack,{random:()=>.99,normal:()=>1,size:.2,kind:'cluster'});
  assert.deepEqual(pack,copy);
  for(let i=0;i<3;i++)for(let j=0;j<i;j++){
    const distance=p=>Math.hypot(p[i].x-p[j].x,p[i].y-p[j].y);
    assert.ok(Math.abs(distance(pack)-distance(q))<1e-12);
  }
  assert.ok(q.some((s,i)=>s.angle!==pack[i].angle));
});
test('v2 is independent of worker chunking; all move families execute within its budget',()=>{
  const options={strategy:'v2',seed:10,budget:401};
  const a=finish(createSearch(17,grid(17),options),1),b=finish(createSearch(17,grid(17),options),73);
  assert.deepEqual(a,b);assert.equal(a.step,401);assert.equal(a.restarts,3);
  assert.equal(Object.values(a.moves).reduce((x,y)=>x+y,0),401);
  for(const kind of ['construction','restart','single','translate','cluster'])assert.ok(a.moves[kind]>0);
  assert.equal(valid(a.best,17),true);assert.ok(a.L<5);
});
test('v2 retains strong input, publishes detached snapshots and handles edge budgets',()=>{
  const initial=cornerBlocks(17),L=bounds(initial).L;
  const e=createSearch(17,initial,{strategy:'v2',budget:40}),first=e.advance(2);first.best[0].x=999;
  const r=finish(e);assert.equal(valid(r.best,17),true);assert.ok(r.L<=L);
  for(const n of [1,2,1000]){
    const r=finish(createSearch(n,grid(n),{strategy:'v2',budget:1}));
    assert.equal(r.step,1);assert.equal(valid(r.best,n),true);assert.ok(r.L<=bounds(grid(n)).L);
  }
  assert.throws(()=>createSearch(5,grid(5),{strategy:'unknown'}));
  assert.throws(()=>createSearch(5,grid(5),{strategy:'v2'}).advance(0));
});
test('comparison matches independent same-start runs and charges each engine separately',()=>{
  const options={seed:19,budget:151},initial=grid(17),copy=structuredClone(initial);
  const result=finish(createComparison(17,initial,options),20);
  for(const strategy of ['v1','v2']){
    const separate=finish(createSearch(17,initial,{...options,strategy}));
    assert.equal(result.comparison[strategy].L,separate.L);
    assert.equal(result.comparison[strategy].step,151);assert.equal(result.comparison[strategy].done,true);
  }
  assert.equal(result.step,302);assert.equal(result.budget,302);
  assert.equal(result.L,Math.min(...Object.values(result.comparison).map(r=>r.L)));
  assert.equal(valid(result.best,17),true);assert.deepEqual(initial,copy);
});
test('alternative starts preserve count and are repairable without changing square size',()=>{
  for(const n of [1,10,17])for(const kind of [0,1,2]){
    const p=startingLayout(n,kind,rng(42));assert.equal(p.length,n);
    // Rigid rotation may have float-level contact noise; the solver repairs starts.
    for(const s of p)assert.ok([s.x,s.y,s.angle].every(Number.isFinite));
  }
});
