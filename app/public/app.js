import {grid,bounds,valid,toCSV} from './engine.js';
import {renderPieces} from './board-view.js';
import {analyzePacking} from './metrics.js';
import {createRecordStore} from './records.js';

const $=id=>document.getElementById(id),fmt=(v,d=4)=>v.toLocaleString('es-ES',{minimumFractionDigits:d,maximumFractionDigits:d});
const clone=p=>p.map(s=>({...s}));
let n=5,pack=grid(n),selected=0,history=[],worker=null,running=false,refs=null,drag=null,renderQueued=false;
let records;
try{records=createRecordStore(window.localStorage);}catch{records=createRecordStore(null);}
function say(message){$('status').textContent=message;}
function remember(){history.push(clone(pack));if(history.length>80)history.shift();}
function saveBest(analysis){records.record(n,pack,analysis);}
function fit(){
  const b=bounds(pack),size=Math.max(b.L,1)+1.2;
  $('board').setAttribute('viewBox',`${b.x0-.6} ${-b.y0-b.L-.6} ${size} ${size}`);
}
function render(analysis=analyzePacking(pack)){
  const {box,pairs,bad,ok}=analysis;
  const baseline=Math.ceil(Math.sqrt(n)),delta=100*(1-box.L/baseline),angle=pack[selected].angle*180/Math.PI;
  const container=$('container');
  for(const [key,value] of Object.entries({x:box.x0,y:-box.y0-box.L,width:box.L,height:box.L})) container.setAttribute(key,value);
  $('pieces').innerHTML=renderPieces(pack,{selected,bad});
  $('board-n').textContent=`/ ${String(n).padStart(2,'0')}`;
  $('side-value').textContent=fmt(box.L);
  $('improvement-value').textContent=ok?`${delta>0?'+':''}${fmt(delta,2)}%`:'—';
  $('improvement-note').textContent=!ok?'Primero, evita los cruces':delta>1e-6?'Menos lado que la rejilla':delta<-.000001?'Aún puedes compactarlo':'Tu punto de partida';
  $('valid-pill').classList.toggle('invalid',!ok);
  $('valid-pill').innerHTML=`<span></span>${ok?'Sin solapamientos':`${pairs.length} ${pairs.length===1?'cruce':'cruces'}`}`;
  const occupancy=100*n/(box.L*box.L);
  $('occupancy-value').textContent=ok?`${fmt(occupancy,1)} %`:'—';
  $('occupancy-meter').value=ok?Math.min(100,occupancy):0;
  $('selected-id').textContent=String(selected+1).padStart(2,'0');
  $('angle-value').textContent=`${fmt(angle,0)}°`;
  if(document.activeElement!==$('angle')) $('angle').value=angle;
  $('angle').disabled=running;
  $('rotate-left').disabled=$('rotate-right').disabled=running;
  $('undo').disabled=!history.length||running;
  $('export').disabled=!ok||running;
  $('reference').disabled=running||!refs?.packings?.[n];
  $('reference').title=refs?.packings?.[n]?'Referencia del proyecto validada offline':'Hay referencias para 5 y 10 cuadrados';
  const bestRecord=records.get(n);
  $('record-value').textContent=bestRecord?fmt(bestRecord.L):'—';
  for(const button of document.querySelectorAll('[data-n]')){const active=Number(button.dataset.n)===n;button.classList.toggle('selected',active);button.setAttribute('aria-pressed',active);}
  $('board-note').textContent=running?'El motor busca. Tú puedes detenerlo.':!ok?'Las piezas con contorno magenta necesitan espacio':`Cuadrado ${String(selected+1).padStart(2,'0')} seleccionado · arrastra o gira`;
}
function update(){const analysis=analyzePacking(pack);saveBest(analysis);render(analysis);}
function requestRender(){if(renderQueued)return;renderQueued=true;requestAnimationFrame(()=>{renderQueued=false;render();});}
function stop(message){
  worker?.terminate();worker=null;running=false;
  $('optimize').classList.remove('running');$('optimize-label').textContent='Que lo intente el motor';
  $('solver-progress').hidden=true;
  if(message)say(message);
  update();
}
function puzzle(value){
  if(!Number.isInteger(value)||value<1||value>1000){say('Elige un número entero entre 1 y 1.000.');return;}
  stop();n=value;pack=grid(n);selected=0;history=[];$('n-input').value=n;
  if(n>100)$('budget').value='250';
  fit();update();say(n>100?'Reto grande: usa un presupuesto pequeño en Laboratorio. El tablero sigue siendo interactivo.':'Empiezas con una rejilla. ¿Puedes ocupar menos espacio?');
}
function rotate(degrees){if(running)return;remember();pack[selected]={...pack[selected],angle:normalize(pack[selected].angle+degrees*Math.PI/180)};update();}
function normalize(angle){return ((angle+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;}
function world(event){
  const svg=$('board'),p=svg.createSVGPoint();p.x=event.clientX;p.y=event.clientY;
  const point=p.matrixTransform(svg.getScreenCTM().inverse());return {x:point.x,y:-point.y};
}
$('board').addEventListener('pointerdown',event=>{
  const piece=event.target.closest('[data-i]');if(!piece||running)return;
  selected=Number(piece.dataset.i);const point=world(event);remember();
  drag={id:event.pointerId,dx:pack[selected].x-point.x,dy:pack[selected].y-point.y};
  $('board').setPointerCapture(event.pointerId);$('board').focus();render();event.preventDefault();
});
$('board').addEventListener('pointermove',event=>{
  if(!drag||event.pointerId!==drag.id)return;
  const p=world(event);
  pack[selected]={...pack[selected],x:p.x+drag.dx,y:p.y+drag.dy};requestRender();
});
for(const name of ['pointerup','pointercancel','lostpointercapture'])$('board').addEventListener(name,()=>{if(drag){drag=null;update();}});
$('board').addEventListener('keydown',event=>{
  if(running)return;
  const moves={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,1],ArrowDown:[0,-1]};
  if(moves[event.key]){event.preventDefault();remember();const [dx,dy]=moves[event.key],step=event.shiftKey ? .2 : .05;pack[selected]={...pack[selected],x:pack[selected].x+dx*step,y:pack[selected].y+dy*step};update();$('board').focus();}
  if(['q','e'].includes(event.key.toLowerCase())){event.preventDefault();rotate((event.key.toLowerCase()==='q'?-1:1)*(event.shiftKey?15:5));$('board').focus();}
  if(event.key==='Enter'||event.key===' '){const piece=event.target.closest('[data-i]');if(piece){event.preventDefault();selected=Number(piece.dataset.i);render();$('board').focus();}}
});
$('angle').addEventListener('pointerdown',()=>{if(!running)remember();});
$('angle').addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key))remember();});
$('angle').addEventListener('input',event=>{if(running)return;pack[selected]={...pack[selected],angle:Number(event.target.value)*Math.PI/180};update();});
$('rotate-left').onclick=()=>rotate(-5);$('rotate-right').onclick=()=>rotate(5);
$('fit').onclick=()=>{fit();render();};
$('undo').onclick=()=>{if(history.length){stop();pack=history.pop();selected=Math.min(selected,pack.length-1);update();say('Último cambio deshecho.');}};
for(const button of document.querySelectorAll('[data-n]'))button.onclick=()=>puzzle(Number(button.dataset.n));
$('n-apply').onclick=()=>puzzle(Number($('n-input').value));
$('n-input').addEventListener('keydown',event=>{if(event.key==='Enter')puzzle(Number(event.target.value));});
$('reset').onclick=()=>{stop();remember();pack=grid(n);fit();update();say('De vuelta a la rejilla. Tu mejor marca local se conserva.');};
$('reference').onclick=()=>{
  const reference=refs?.packings?.[n];if(!reference)return;
  stop();remember();pack=clone(reference);fit();update();
  say('Referencia del proyecto Python, validada offline con la métrica v17. Si la editas, cambia la configuración validada.');
};
function mode(lab){$('lab-settings').hidden=!lab;$('play-tab').classList.toggle('active',!lab);$('lab-tab').classList.toggle('active',lab);$('play-tab').setAttribute('aria-pressed',!lab);$('lab-tab').setAttribute('aria-pressed',lab);}
$('play-tab').onclick=()=>mode(false);$('lab-tab').onclick=()=>mode(true);
$('optimize').onclick=()=>{
  if(running){stop('Motor detenido. Se conserva la mejor configuración recibida.');return;}
  const seed=Number($('seed').value),budget=Number($('budget').value);
  if(!Number.isInteger(seed)||seed<0||seed>4294967295){say('La semilla debe ser un entero entre 0 y 4.294.967.295.');return;}
  remember();running=true;$('optimize').classList.add('running');$('optimize-label').textContent='Detener búsqueda';
  $('solver-progress').hidden=false;$('solver-meter').max=budget;$('solver-meter').value=0;
  say(n===5?'El motor parte de una familia constructiva y prueba movimientos y giros.':'El motor prueba movimientos y giros en este navegador. No garantiza superar la rejilla.');
  try{worker=new Worker(new URL('./worker.js',import.meta.url),{type:'module'});}catch{stop('No se pudo iniciar el motor. Abre la app por HTTP o HTTPS, no como archivo local.');return;}
  const activeWorker=worker;
  worker.onerror=()=>{if(worker===activeWorker)stop('El motor encontró un problema. Tu tablero sigue disponible. Prueba un presupuesto menor.');};
  worker.onmessage=({data})=>{
    if(worker!==activeWorker)return;
    if(data.error){stop(`El motor se ha detenido: ${data.error}`);return;}
    if(!valid(data.best,n)){stop('Se descartó una configuración inválida del motor.');return;}
    pack=data.best;selected=Math.min(selected,n-1);$('solver-meter').value=data.step;
    $('solver-count').textContent=`${data.step.toLocaleString('es-ES')} / ${budget.toLocaleString('es-ES')} propuestas`;
    update();
    if(data.done){const L=bounds(pack).L;stop(`Búsqueda terminada: lado ${fmt(L)}. Resultado local; requiere evaluación oficial antes de usarlo en Kaggle.`);}
  };
  worker.postMessage({n,initial:clone(pack),seed,budget,method:$('method').value});render();
};
$('export').onclick=()=>{
  try{
    const url=URL.createObjectURL(new Blob([toCSV(pack)],{type:'text/csv;charset=utf-8'}));
    const a=document.createElement('a');a.href=url;a.download=`tailorpack-n${n}-local.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    say('CSV exportado como candidato local. El formato es compatible; la aceptación exige pasar el evaluador oficial de Kaggle.');
  }catch(error){say(error.message);}
};
for(const id of ['about-open','details-open'])$(id).onclick=()=>$('about').showModal();
$('help-open').onclick=()=>$('help').showModal();
for(const dialog of document.querySelectorAll('dialog')){
  dialog.querySelector('.dialog-close').onclick=()=>dialog.close();
  dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
}
fit();update();
fetch('./references.json').then(response=>{if(!response.ok)throw Error();return response.json();}).then(data=>{
  for(const [key,value] of Object.entries(data.packings||{})) if(!valid(value,Number(key)))throw Error('Referencia inválida');
  refs=data;render();
}).catch(()=>{say('Las referencias guardadas no están disponibles. Puedes seguir jugando y usar el motor local.');});
