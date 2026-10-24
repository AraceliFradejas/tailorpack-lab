// Float geometry for play. Official interval certification stays in Python.
export const HALF_PI=Math.PI/2;
export function square(x,y,angle=0){
  if(![x,y,angle].every(Number.isFinite)) throw new Error('Coordenadas no finitas');
  return {x,y,angle};
}
export function grid(n){
  if(!Number.isInteger(n)||n<1||n>1000) throw new Error('n debe estar entre 1 y 1000');
  const width=Math.ceil(Math.sqrt(n));
  return Array.from({length:n},(_,i)=>square(i%width+.5,Math.floor(i/width)+.5));
}
export function corners(s){
  const c=Math.cos(s.angle),t=Math.sin(s.angle);
  return [[-.5,-.5],[.5,-.5],[.5,.5],[-.5,.5]].map(([x,y])=>[s.x+c*x-t*y,s.y+t*x+c*y]);
}
export function bounds(pack){
  if(!pack.length) throw new Error('Configuración vacía');
  let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;
  for(const s of pack) for(const [x,y] of corners(s)){x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);}
  return {x0,y0,x1,y1,L:Math.max(x1-x0,y1-y0)};
}
export function overlaps(a,b){
  const pa=corners(a),pb=corners(b);
  for(const s of [a,b]){
    const c=Math.cos(s.angle),t=Math.sin(s.angle);
    for(const [ux,uy] of [[c,t],[-t,c]]){
      const aa=pa.map(([x,y])=>x*ux+y*uy),bb=pb.map(([x,y])=>x*ux+y*uy);
      if(Math.max(...aa)<=Math.min(...bb)||Math.max(...bb)<=Math.min(...aa)) return false;
    }
  }
  return true;
}
export function collisions(pack){
  const buckets=new Map(),pairs=[];
  pack.forEach((s,i)=>{
    square(s.x,s.y,s.angle);
    const box=bounds([s]),near=new Set(),cells=[];
    for(let x=Math.floor(box.x0);x<=Math.floor(box.x1);x++) for(let y=Math.floor(box.y0);y<=Math.floor(box.y1);y++){
      const key=`${x},${y}`;cells.push(key);for(const j of buckets.get(key)||[]) near.add(j);
    }
    for(const j of near) if(overlaps(pack[j],s)) pairs.push([j,i]);
    for(const key of cells){if(!buckets.has(key)) buckets.set(key,[]);buckets.get(key).push(i);}
  });
  return pairs;
}
export function valid(pack,n=pack.length){return pack.length===n&&n>0&&n<=1000&&collisions(pack).length===0;}
export function repair(pack,margin=1e-8){
  const axes=pack.map(s=>[Math.cos(s.angle),Math.sin(s.angle)]);
  function threshold(i,j){
    const a=pack[i],b=pack[j],[ca,sa]=axes[i],[cb,sb]=axes[j];
    let best=Infinity;
    for(const [ux,uy] of [[ca,sa],[-sa,ca],[cb,sb],[-sb,cb]]){
      const distance=Math.abs((a.x-b.x)*ux+(a.y-b.y)*uy);
      if(distance>1e-14){
        const support=.5*(Math.abs(ca*ux+sa*uy)+Math.abs(-sa*ux+ca*uy)+Math.abs(cb*ux+sb*uy)+Math.abs(-sb*ux+cb*uy));
        best=Math.min(best,(support+margin)/distance);
      }
    }
    return best;
  }
  if(!pack.length) return null;
  let scale=pack.length>1?threshold(1,0):1;
  if(!Number.isFinite(scale)) return null;
  const radius=(2+Math.SQRT2*margin)/scale*(1+1e-12),buckets=new Map();
  for(let i=0;i<pack.length;i++){
    const s=pack[i],x=Math.floor(s.x/radius),y=Math.floor(s.y/radius);
    for(let dx=-1;dx<=1;dx++) for(let dy=-1;dy<=1;dy++) for(const j of buckets.get(`${x+dx},${y+dy}`)||[]) scale=Math.max(scale,threshold(i,j));
    const key=`${x},${y}`;if(!buckets.has(key)) buckets.set(key,[]);buckets.get(key).push(i);
  }
  if(!Number.isFinite(scale)||scale>1e6) return null;
  const cx=pack.reduce((v,s)=>v+s.x,0)/pack.length,cy=pack.reduce((v,s)=>v+s.y,0)/pack.length;
  const result=pack.map(s=>square((s.x-cx)*scale,(s.y-cy)*scale,s.angle)),box=bounds(result);
  return result.map(s=>square(s.x-box.x0,s.y-box.y0,s.angle));
}
export function rng(seed){
  let state=seed>>>0;
  return ()=>{state+=0x6d2b79f5;let t=state;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};
}
export function fivePattern(angle=0){
  const L=2+1/(Math.cos(angle)+Math.sin(angle))+1e-8;
  return [[.5,.5],[L-.5,.5],[.5,L-.5],[L-.5,L-.5]].map(([x,y])=>square(x,y)).concat(square(L/2,L/2,angle));
}
export function toCSV(pack){
  if(!valid(pack)) throw new Error('Corrige los solapamientos antes de exportar');
  return 'id,n,square_id,x,y,angle\n'+pack.map((s,i)=>[i,pack.length,i,...[s.x,s.y,s.angle].map(v=>v.toPrecision(17))].join(',')).join('\n')+'\n';
}
