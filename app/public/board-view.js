import {corners} from './engine.js';

// The visual skin lives here; geometry remains in engine.js.
export function renderPieces(pack, {selected, bad}) {
  const n = pack.length;
  return pack.map((s,i)=>`<g data-i="${i}" data-tone="${i%6}" role="button" tabindex="${i===selected?0:-1}" aria-label="Cuadrado ${i+1}${bad.has(i)?', solapado':''}" aria-pressed="${i===selected}" class="${i===selected?'selected ':''}${bad.has(i)?'colliding':''}"><polygon points="${corners(s).map(([x,y])=>`${x},${-y}`).join(' ')}"/><g class="tile-face" transform="translate(${s.x} ${-s.y}) rotate(${-s.angle*180/Math.PI})"><rect class="sticker" x="-.447" y="-.447" width=".894" height=".894" rx=".055"/><path class="tile-shine" d="M-.39 .33 V-.34 Q-.39 -.39 -.34 -.39 H.34" fill="none"/><path class="tile-shade" d="M-.34 .39 H.34 Q.39 .39 .39 .34 V-.33" fill="none"/></g>${n<=50?`<text x="${s.x}" y="${-s.y}">${String(i+1).padStart(2,'0')}</text>`:''}${i===selected?`<circle class="selection-dot" cx="${s.x}" cy="${-s.y+.25}" r=".025"/>`:''}</g>`).join('');
}
