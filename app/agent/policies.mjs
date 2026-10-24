import {decisionSchema} from './protocol.mjs';

export class RoundRobinPolicy{
  name='scripted_round_robin_control';usesModel=false;
  async decide({trials,remaining,maxTrial,seeds}){
    const index=trials.length,seed=seeds[Math.floor(index/2)];
    return seed===undefined?{tool:'finish',arguments:{}}:{tool:'run_experiment',arguments:{strategy:index%2?'v2':'v1',seed,budget:Math.min(remaining,maxTrial)}};
  }
}
export class FixedPolicy{
  name='scripted_v1_control';usesModel=false;
  async decide({trials,remaining,maxTrial,seeds}){
    const seed=seeds[trials.length];
    return seed===undefined?{tool:'finish',arguments:{}}:{tool:'run_experiment',arguments:{strategy:'v1',seed,budget:Math.min(remaining,maxTrial)}};
  }
}
export class OllamaPolicy{
  name='ollama';usesModel=true;completedResponses=0;
  constructor({model,endpoint='http://127.0.0.1:11434',timeout=60000,transport=fetch}={}){
    if(typeof model!=='string'||!model.trim()||model.length>200)throw Error('Provide an installed model name');
    const url=new URL(endpoint);
    if(url.protocol!=='http:'||!['localhost','127.0.0.1','[::1]'].includes(url.hostname)||url.username||url.password||url.search||url.hash||url.pathname!=='/')throw Error('Ollama endpoint must be a loopback HTTP origin');
    if(!Number.isInteger(timeout)||timeout<1||timeout>120000)throw Error('Invalid inference timeout');
    this.endpoint=url.origin;this.model=model;this.timeout=timeout;this.transport=transport;
  }
  async decide(context){
    const response=await this.transport(`${this.endpoint}/api/chat`,{method:'POST',redirect:'error',signal:AbortSignal.timeout(this.timeout),headers:{'Content-Type':'application/json'},body:JSON.stringify({
      model:this.model,stream:false,format:decisionSchema,keep_alive:0,
      options:{temperature:0,seed:42,num_predict:256,num_ctx:4096},
      messages:[{role:'system',content:'You select square-packing experiments. Reply with one JSON object only: {"tool":"run_experiment","arguments":{"strategy":"v1" or "v2","seed":allowed integer,"budget":integer}} or {"tool":"finish","arguments":{}}. Never request other tools. Each experiment starts from the same grid. Minimize container side with remaining proposals. V2 includes explicit constructions for 4*k*k+1, restarts and group moves; it is not generally superior. The supplied numbers are measured solver outputs. Do not repeat a trial. Do not claim Kaggle acceptance or invent measurements.'},
        {role:'user',content:JSON.stringify(context)}]
    })});
    if(!response.ok)throw Error('Model service unavailable');
    const reader=response.body.getReader();let bytes=0,parts=[];
    try{while(true){const {value,done}=await reader.read();if(done)break;bytes+=value.byteLength;if(bytes>65536)throw Error('Model response too large');parts.push(value);}}
    finally{await reader.cancel();}
    const data=JSON.parse(Buffer.concat(parts).toString('utf8'));
    if(data.done!==true||typeof data.message?.content!=='string')throw Error('Incomplete model response');
    this.completedResponses++;
    return JSON.parse(data.message.content);
  }
}
