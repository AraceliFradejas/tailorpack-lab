import {createSearch} from './solver.js';
let engine;
self.onmessage=({data})=>{
  try{
    engine=createSearch(data.n,data.initial,data);
    function tick(){
      try{const result=engine.advance(data.n>100?5:50);self.postMessage(result);if(!result.done)setTimeout(tick,0);}
      catch(error){self.postMessage({error:error.message});}
    }
    tick();
  }catch(error){self.postMessage({error:error.message});}
};
