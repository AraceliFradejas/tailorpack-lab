export const decisionSchema={
  type:'object',additionalProperties:false,required:['tool','arguments'],properties:{
    tool:{type:'string',enum:['run_experiment','finish']},
    arguments:{type:'object',additionalProperties:false,properties:{
      strategy:{type:'string',enum:['v1','v2']},seed:{type:'integer',minimum:0,maximum:4294967295},
      budget:{type:'integer',minimum:1,maximum:50000}
    }}
  }
};
const exactKeys=(value,keys)=>value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).length===keys.length&&keys.every(k=>Object.hasOwn(value,k));
export function validateDecision(value,{remaining,maxTrial,seeds}){
  if(!exactKeys(value,['tool','arguments']))throw Error('Expected only tool and arguments');
  if(value.tool==='finish'){
    if(!exactKeys(value.arguments,[]))throw Error('finish takes no arguments');
    return {tool:'finish',arguments:{}};
  }
  const a=value.arguments;
  if(value.tool!=='run_experiment'||!exactKeys(a,['strategy','seed','budget']))throw Error('Unknown tool or arguments');
  if(!['v1','v2'].includes(a.strategy)||!Number.isInteger(a.seed)||!seeds.includes(a.seed))throw Error('Strategy or seed outside allowed choices');
  if(!Number.isInteger(a.budget)||a.budget<1||a.budget>Math.min(maxTrial,remaining))throw Error('Proposal budget outside remaining allowance');
  return {tool:'run_experiment',arguments:{strategy:a.strategy,seed:a.seed,budget:a.budget}};
}
