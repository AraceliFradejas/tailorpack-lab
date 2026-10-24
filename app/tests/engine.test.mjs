import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {bounds,collisions,corners,fivePattern,grid,overlaps,repair,square,toCSV,valid} from '../public/engine.js';
import {createSearch} from '../public/solver.js';

const refs=JSON.parse(readFileSync(new URL('../public/references.json',import.meta.url)));

test('contacts are allowed, even a tiny positive intersection is rejected',()=>{
  assert.equal(overlaps(square(0,0),square(1,0)),false);
  assert.equal(overlaps(square(0,0),square(1,1)),false);
  assert.equal(overlaps(square(0,0),square(1-1e-12,0)),true);
});
test('grid domain and finite coordinates',()=>{
  for(const n of [0,-1,1001,1.5])assert.throws(()=>grid(n));
  assert.throws(()=>square(NaN,0));assert.throws(()=>square(0,Infinity));
});
test('rotated bounds and translation invariance',()=>{
  assert.ok(Math.abs(bounds([square(0,0,Math.PI/4)]).L-Math.SQRT2)<1e-14);
  const p=fivePattern(Math.PI/4),q=p.map(s=>square(s.x+10,s.y-4,s.angle));
  assert.ok(Math.abs(bounds(p).L-bounds(q).L)<1e-14);
});
test('spatial collision filter agrees with exhaustive SAT',()=>{
  const p=Array.from({length:35},(_,i)=>square(Math.sin(i)*3,Math.cos(i*3)*3,i*.21));
  const expected=[];for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++)if(overlaps(p[i],p[j]))expected.push(`${i},${j}`);
  assert.deepEqual(collisions(p).map(([i,j])=>`${i},${j}`).sort(),expected.sort());
});
test('reference CSV-derived configurations match the saved Python sides',()=>{
  assert.equal(refs.metric_version,17);
  assert.equal(valid(refs.packings[5],5),true);assert.equal(valid(refs.packings[10],10),true);
  assert.ok(Math.abs(bounds(refs.packings[5]).L-2.7071067821865475)<1e-12);
  assert.ok(Math.abs(bounds(refs.packings[10]).L-3.9100797962141782)<1e-12);
});
test('repair removes rotated overlaps and rejects coincident centres',()=>{
  const p=repair([square(0,0,.2),square(.2,.1,-.3),square(-.1,.2,.7)]);
  assert.equal(valid(p,3),true);
  assert.equal(repair([square(0,0),square(0,0,.2)]),null);
});
test('1000-piece grid validates and repairs',()=>{
  const p=grid(1000);assert.equal(bounds(p).L,32);assert.equal(valid(p),true);assert.equal(valid(repair(p)),true);
});
test('CSV has the verified six-column schema and complete square IDs',()=>{
  const lines=toCSV(refs.packings[5]).trim().split('\n');
  assert.equal(lines[0],'id,n,square_id,x,y,angle');assert.equal(lines.length,6);
  lines.slice(1).forEach((line,i)=>{const row=line.split(',');assert.equal(row[0],String(i));assert.equal(row[1],'5');assert.equal(row[2],String(i));assert.equal(row.length,6);});
  assert.throws(()=>toCSV([square(0,0),square(.1,0)]));
});
function finish(engine){let result;do{result=engine.advance(37);}while(!result.done);return result;}
test('browser solver is deterministic, budgeted and returns a feasible non-degraded incumbent',()=>{
  const a=finish(createSearch(5,grid(5),{seed:42,budget:1000}));
  const b=finish(createSearch(5,grid(5),{seed:42,budget:1000}));
  assert.deepEqual(a,b);assert.equal(a.step,1000);assert.equal(valid(a.best,5),true);assert.ok(a.L<3);
});
test('solver retains a stronger reference and handles invalid starts',()=>{
  const a=finish(createSearch(10,refs.packings[10],{seed:4,budget:100}));
  assert.ok(a.L<=3.9100797962141782);
  const b=finish(createSearch(3,[square(0,0),square(.1,0),square(.2,0)],{budget:100}));
  assert.equal(valid(b.best,3),true);
  assert.throws(()=>createSearch(5,grid(5),{budget:0}));
});
