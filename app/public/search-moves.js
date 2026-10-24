import {grid,HALF_PI} from './engine.js';
const turn=a=>((a%HALF_PI)+HALF_PI)%HALF_PI;

// Explicit extension of the project's five-square control: four k×k corner blocks + a centre.
// This is an explicit construction, not a discovery made by the search.
export function cornerBlocks(n){
  const k=Math.sqrt((n-1)/4);
  if(!Number.isInteger(k)||k<1)return null;
  const gap=1e-8,block=k+(k-1)*gap,L=2*block+Math.SQRT1_2+gap,pack=[];
  for(const dx of [0,L-block])for(const dy of [0,L-block])
    for(let x=0;x<k;x++)for(let y=0;y<k;y++)pack.push({x:dx+x*(1+gap)+.5,y:dy+y*(1+gap)+.5,angle:0});
  pack.push({x:L/2,y:L/2,angle:Math.PI/4});
  return pack;
}

export function startingLayout(n,kind,random){
  if(kind===0)return grid(n);
  const width=Math.ceil(Math.sqrt(n)),rows=Math.ceil(n/width);
  const pack=Array.from({length:n},(_,i)=>({
    x:i%width+.5+(kind===1&&Math.floor(i/width)%2 ? .35 : 0),
    y:Math.floor(i/width)+.5,angle:0
  }));
  // Rotate centres AND unit squares together, preserving relative geometry.
  if(kind===2){
    const angle=(random()-.5)*.35,c=Math.cos(angle),s=Math.sin(angle);
    return pack.map(p=>{const x=p.x-width/2,y=p.y-rows/2;return {x:c*x-s*y,y:s*x+c*y,angle};});
  }
  return pack;
}

export function propose(pack,{random,normal,size,kind}){
  const anchor=Math.floor(random()*pack.length),origin=pack[anchor];
  const chosen=new Set([anchor]);
  if(kind==='cluster'){
    const nearest=pack.map((p,i)=>({i,d:(p.x-origin.x)**2+(p.y-origin.y)**2})).sort((a,b)=>a.d-b.d||a.i-b.i);
    const count=Math.min(pack.length,2+Math.floor(random()*4));
    nearest.slice(0,count).forEach(p=>chosen.add(p.i));
  }
  const dx=normal()*size,dy=normal()*size;
  const angle=kind==='translate'?0:normal()*size*2,c=Math.cos(angle),s=Math.sin(angle);
  return pack.map((p,i)=>{
    if(!chosen.has(i))return p;
    const x=p.x-origin.x,y=p.y-origin.y;
    return {x:origin.x+c*x-s*y+dx,y:origin.y+s*x+c*y+dy,angle:turn(p.angle+angle)};
  });
}
