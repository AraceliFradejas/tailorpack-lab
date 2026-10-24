import {createSearch} from '../public/solver.js';
import {grid,bounds,valid} from '../public/engine.js';
import {validateDecision} from './protocol.mjs';

export function validateConfig({n,totalBudget,maxTrial,maxDecisions,seeds}){
  grid(n);
  for(const [key,value,max] of [['totalBudget',totalBudget,50000],['maxTrial',maxTrial,50000],['maxDecisions',maxDecisions,20]])
    if(!Number.isInteger(value)||value<1||value>max)throw Error(`Invalid ${key}`);
  if(!Array.isArray(seeds)||!seeds.length||seeds.length>20||new Set(seeds).size!==seeds.length||seeds.some(s=>!Number.isInteger(s)||s<0||s>4294967295))throw Error('Invalid seed choices');
}
export async function runCampaign(policy,{n=17,totalBudget=10000,maxTrial=2500,maxDecisions=8,seeds=[10,11,12,13]}={}){
  const config={n,totalBudget,maxTrial,maxDecisions,seeds:[...seeds]};validateConfig(config);
  const initial=grid(n),initialL=bounds(initial).L,responseBase=policy.completedResponses??0;
  let best=structuredClone(initial),bestL=initialL,used=0,stopReason='decision_limit',inferenceAttempts=0;
  const trials=[],events=[],timings=[],seen=new Set();
  for(let turn=0;turn<maxDecisions;turn++){
    if(used>=totalBudget){stopReason='proposal_limit';break;}
    const context={n,initialL,bestL,remaining:totalBudget-used,maxTrial,seeds:[...seeds],trials:structuredClone(trials),lastEvent:events.at(-1)??null};
    let proposed,decision;const start=performance.now();
    if(policy.usesModel)inferenceAttempts++;
    try{proposed=await policy.decide(structuredClone(context));}
    catch{events.push({turn,event:'policy_unavailable'});stopReason='policy_error';break;}
    timings.push({turn,kind:'decision',seconds:(performance.now()-start)/1000});
    try{decision=validateDecision(proposed,context);}
    catch(error){events.push({turn,event:'rejected',reason:error.message});continue;}
    if(decision.tool==='finish'){events.push({turn,event:'finish'});stopReason='policy_finished';break;}
    const {strategy,seed,budget}=decision.arguments,key=JSON.stringify(decision.arguments);
    if(seen.has(key)){events.push({turn,event:'rejected',reason:'Duplicate trial'});continue;}
    seen.add(key);
    // Reserve the complete cost BEFORE starting any tool. Invalid decisions cost no proposals.
    used+=budget;const begin=performance.now();let result;
    try{
      const engine=createSearch(n,structuredClone(initial),{strategy,seed,budget,method:'annealing'});
      do{result=engine.advance(100);}while(!result.done);
      if(result.step!==budget||!valid(result.best,n)||result.L>initialL+1e-12)throw Error('Invalid solver result');
    }catch{events.push({turn,event:'solver_error'});stopReason='solver_error';break;}
    timings.push({turn,kind:'solver',seconds:(performance.now()-begin)/1000});
    const row={id:trials.length,strategy,seed,budget,L:result.L};trials.push(row);
    events.push({turn,event:'experiment',trial:row.id,decision});
    if(result.L<bestL){best=result.best;bestL=result.L;}
  }
  if(used>=totalBudget&&!['policy_error','solver_error'].includes(stopReason))stopReason='proposal_limit';
  return {report:{status:'LOCAL_FLOAT_NOT_OFFICIALLY_VALIDATED',provider:policy.name,model:policy.model??null,
    modelExecuted:(policy.completedResponses??0)>responseBase,inferenceAttempts,inferenceResponses:(policy.completedResponses??0)-responseBase,config,initialL,bestL,usedProposals:used,stopReason,trials,events},best:structuredClone(best),timings};
}
