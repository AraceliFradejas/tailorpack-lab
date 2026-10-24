import test from 'node:test';
import assert from 'node:assert/strict';
import {runCampaign} from '../agent/campaign.mjs';
import {validateDecision} from '../agent/protocol.mjs';
import {RoundRobinPolicy,OllamaPolicy} from '../agent/policies.mjs';
import {valid} from '../public/engine.js';
const context={remaining:100,maxTrial:50,seeds:[10,11]};
const decision=(budget=50,strategy='v2',seed=10)=>({tool:'run_experiment',arguments:{strategy,seed,budget}});

test('agent rejects arbitrary tools, extra fields, disallowed seeds and over-budget requests',()=>{
  for(const d of [{tool:'shell',arguments:{command:'anything'}}, {...decision(),code:'anything'},decision(101),decision(51),decision(0),decision(1,'v3'),decision(1,'v1',12),decision(1.5),{tool:'finish',arguments:{budget:1}}])
    assert.throws(()=>validateDecision(d,context));
  assert.deepEqual(validateDecision({tool:'finish',arguments:{}},context),{tool:'finish',arguments:{}});
});
test('scripted control executes real tools, respects global caps and makes no model claim',async()=>{
  const result=await runCampaign(new RoundRobinPolicy(),{n:17,totalBudget:101,maxTrial:50,maxDecisions:8,seeds:[10,11]});
  assert.equal(result.report.usedProposals,101);assert.equal(result.report.trials.reduce((n,r)=>n+r.budget,0),101);
  assert.equal(result.report.stopReason,'proposal_limit');assert.equal(result.report.modelExecuted,false);
  assert.equal(result.report.inferenceAttempts,0);assert.equal(valid(result.best,17),true);assert.ok(result.report.bestL<5);
});
test('rejections and reordered duplicates cannot spend proposals twice or loop forever',async()=>{
  let calls=0;
  const policy={name:'test_fixture',async decide(){calls++;return calls===1?decision(999):calls===2?decision(10):{tool:'run_experiment',arguments:{budget:10,seed:10,strategy:'v2'}};}};
  const result=await runCampaign(policy,{n:5,totalBudget:100,maxTrial:50,maxDecisions:5,seeds:[10]});
  assert.equal(calls,5);assert.equal(result.report.usedProposals,10);assert.equal(result.report.trials.length,1);
  assert.equal(result.report.stopReason,'decision_limit');assert.equal(result.report.events.filter(e=>e.event==='rejected').length,4);
});
test('policy errors preserve the best result without silently falling back to a fake model',async()=>{
  let count=0;const policy={name:'unavailable_fixture',usesModel:true,completedResponses:3,async decide(){if(count++)throw Error('private detail');return decision(10);}};
  const result=await runCampaign(policy,{n:17,totalBudget:100,maxTrial:50,maxDecisions:4,seeds:[10]});
  assert.equal(result.report.stopReason,'policy_error');assert.equal(result.report.usedProposals,10);
  assert.equal(result.report.modelExecuted,false);assert.equal(result.report.inferenceAttempts,2);assert.equal(result.report.inferenceResponses,0);
  assert.ok(!JSON.stringify(result.report).includes('private detail'));assert.ok(result.report.bestL<5);
});
test('policy cannot mutate the campaign context or fabricate a winning score',async()=>{
  const policy={name:'mutation_fixture',async decide(c){c.trials.push({L:0});c.bestL=0;return {tool:'finish',arguments:{}};}};
  const result=await runCampaign(policy);assert.equal(result.report.bestL,5);assert.deepEqual(result.report.trials,[]);assert.equal(result.report.usedProposals,0);
});
test('agent control is reproducible and invalid configurations fail before decisions',async()=>{
  const options={n:17,totalBudget:100,maxTrial:50,maxDecisions:4,seeds:[10,11]};
  const a=await runCampaign(new RoundRobinPolicy(),options),b=await runCampaign(new RoundRobinPolicy(),options);
  assert.deepEqual(a.report,b.report);assert.deepEqual(a.best,b.best);
  for(const bad of [{totalBudget:-1},{maxDecisions:21},{seeds:[10,10]},{n:0},{maxTrial:50001}])await assert.rejects(runCampaign(new RoundRobinPolicy(),{...options,...bad}));
});
test('Ollama transport uses bounded JSON, no streaming, no redirects and validated local origin',async()=>{
  for(const endpoint of ['https://example.com','http://example.com','http://localhost/path','http://user@localhost','http://localhost?token=secret'])assert.throws(()=>new OllamaPolicy({model:'gemma',endpoint}));
  let request;
  const policy=new OllamaPolicy({model:'gemma-fixture',transport:async(url,options)=>{request={url,options};return new Response(JSON.stringify({done:true,message:{content:JSON.stringify(decision(10))}}));}});
  assert.deepEqual(await policy.decide(context),decision(10));
  const body=JSON.parse(request.options.body);assert.equal(body.stream,false);assert.equal(body.options.num_predict,256);
  assert.equal(request.options.redirect,'error');assert.equal(request.url,'http://127.0.0.1:11434/api/chat');assert.equal(policy.completedResponses,1);
});
test('incomplete, oversized and non-JSON model responses are rejected',async()=>{
  for(const body of [JSON.stringify({done:false,message:{content:'{}'}}),JSON.stringify({done:true,message:{content:'not json'}}),'x'.repeat(65537)]){
    const policy=new OllamaPolicy({model:'gemma-fixture',transport:async()=>new Response(body)});
    await assert.rejects(policy.decide(context));
  }
});
