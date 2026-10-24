// Reproducible browser-engine benchmark, executable without a browser or network.
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {resolve,join} from 'node:path';
import {performance} from 'node:perf_hooks';
import {createSearch} from '../public/solver.js';
import {grid,bounds,valid,toCSV} from '../public/engine.js';
import {cornerBlocks} from '../public/search-moves.js';

const args=process.argv.slice(2),option=(name,fallback)=>{
  const i=args.indexOf(`--${name}`);return i<0?fallback:args[i+1];
};
if(args.some((a,i)=>i%2===0&&!['--out','--ns','--seeds','--budget'].includes(a))||args.length%2)throw Error('Use --out PATH --ns 5,10,... --seeds 10,11,... --budget INT');
const ns=option('ns','5,9,10,11,13,16,17,20,37').split(',').map(Number);
const seeds=option('seeds','10,11,12,13,14,15,16,17,18,19').split(',').map(Number);
const budget=Number(option('budget','2500')),out=resolve(option('out','../runs/web-v02'));
for(const [values,max] of [[ns,1000],[seeds,4294967295]])if(!values.length||new Set(values).size!==values.length||values.some(n=>!Number.isInteger(n)||n<(values===ns?1:0)||n>max))throw Error('Invalid or duplicate ns/seeds');
const root=fileURLToPath(new URL('../public/',import.meta.url));
const sources=Object.fromEntries(['engine.js','solver.js','solver-v1.js','search-moves.js'].map(f=>[f,createHash('sha256').update(readFileSync(join(root,f))).digest('hex')]));
mkdirSync(out,{recursive:true});
const rows=[],timings=[],best=new Map();
for(const n of ns){
  const constructed=cornerBlocks(n);
  const starts=[['grid',grid(n)]];
  if(constructed)starts.push(['shared-construction',constructed]);
  for(const [start,initial] of starts)for(const seed of seeds)for(const strategy of ['v1','v2']){
    const t=performance.now(),engine=createSearch(n,initial,{seed,budget,strategy});let result;
    do{result=engine.advance(53);}while(!result.done);
    if(!valid(result.best,n)||result.step!==budget||result.L>Math.min(bounds(initial).L,bounds(grid(n)).L)+1e-12)throw Error('Benchmark invariant failed');
    timings.push({n,start,seed,strategy,seconds:(performance.now()-t)/1000});
    rows.push({n,start,seed,strategy,initialL:bounds(initial).L,L:result.L,step:result.step,accepted:result.accepted,restarts:result.restarts??0,moves:result.moves??null});
    if(!best.has(n)||result.L<bounds(best.get(n)).L)best.set(n,result.best);
  }
  console.log(`n=${n} complete`);
}
const median=xs=>{const a=[...xs].sort((a,b)=>a-b),m=Math.floor(a.length/2);return a.length%2?a[m]:(a[m-1]+a[m])/2;};
const summary=[];
for(const n of ns)for(const start of ['grid','shared-construction']){
  const a=rows.filter(r=>r.n===n&&r.start===start&&r.strategy==='v1'),b=rows.filter(r=>r.n===n&&r.start===start&&r.strategy==='v2');if(!a.length)continue;
  summary.push({n,start,v1:{best:Math.min(...a.map(r=>r.L)),median:median(a.map(r=>r.L)),improved:a.filter(r=>r.L<r.initialL-1e-7).length},v2:{best:Math.min(...b.map(r=>r.L)),median:median(b.map(r=>r.L)),improved:b.filter(r=>r.L<r.initialL-1e-7).length},v2Wins:b.filter((r,i)=>r.L<a[i].L-1e-7).length,v1Wins:a.filter((r,i)=>r.L<b[i].L-1e-7).length,ties:b.filter((r,i)=>Math.abs(r.L-a[i].L)<=1e-7).length});
}
let csv='id,n,square_id,x,y,angle\n',id=0;
for(const [n,pack] of best)for(const line of toCSV(pack).trim().split('\n').slice(1)){const fields=line.split(',');fields[0]=id++;csv+=fields.join(',')+'\n';}
writeFileSync(join(out,'candidate_NOT_VALIDATED.csv'),csv);
writeFileSync(join(out,'benchmark.json'),JSON.stringify({status:'LOCAL_FLOAT_ONLY_NOT_OFFICIALLY_VALIDATED',config:{ns,seeds,budget,method:'annealing',candidate_sha256:createHash('sha256').update(csv).digest('hex')},sources,rows,summary},null,2)+'\n');
writeFileSync(join(out,'timings.json'),JSON.stringify({node:process.version,platform:process.platform,arch:process.arch,rows:timings},null,2)+'\n');
console.log(JSON.stringify(summary,null,2));
