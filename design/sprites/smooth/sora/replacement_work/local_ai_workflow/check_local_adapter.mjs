// Mock API checks only: no model execution, downloads or production candidates.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
export async function checkLocalAdapter(adapter){
const {ROOT,Comfy,readJob,workflow,submit,collect,projectPath}=adapter;
const job=readJob('design/sprites/smooth/sora/replacement_work/local_ai_workflow/pilot_job.json');
const graph=workflow(job,'whole.png','kh_sora/test');
assert.equal(Object.keys(graph).length,8);assert.equal(graph['6'].inputs.latent_image[0],'5');
assert.throws(()=>new Comfy('https://example.com'));assert.throws(()=>projectPath('../outside.txt'));
const scratch=projectPath('.local/comfy_adapter_checks/'+crypto.randomUUID());fs.mkdirSync(scratch,{recursive:true});
let submissions=0,historyCalls=0,validation=false,ready=false,failureStatus=400;
const source=fs.readFileSync(projectPath(job.reference,true));
const errorText='{"error":{"type":"prompt_outputs_failed_validation","message":"Mock invalid checkpoint"},"node_errors":{"1":{"errors":[]}}}';
const server=http.createServer(async(req,res)=>{
  const body=[];for await(const chunk of req)body.push(chunk);
  const send=data=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify(data));};
  if(req.url==='/system_stats')return send({system:{comfyui_version:'mock'},devices:[]});
  if(req.url==='/object_info')return send(Object.fromEntries(['CheckpointLoaderSimple','CLIPTextEncode','LoadImage','VAEEncode','KSampler','VAEDecode','SaveImage'].map(name=>[name,name==='CheckpointLoaderSimple'?{input:{required:{ckpt_name:[[job.checkpoint]]}}}:{}])));
  if(req.url==='/upload/image'){assert.match(Buffer.concat(body).toString('latin1'),/name="image"/);return send({name:'whole.png',subfolder:'',type:'input'});}
  if(req.url==='/prompt'){
    submissions++;const request=JSON.parse(Buffer.concat(body));assert.equal(request.prompt['6'].inputs.seed,job.seed);
    if(validation){res.statusCode=failureStatus;return res.end(errorText);}
    return send({prompt_id:'mock-prompt-1',number:0,node_errors:{}});
  }
  if(req.url==='/history/mock-prompt-1'){historyCalls++;return send(ready?{'mock-prompt-1':{status:{completed:true,status_str:'success'},outputs:{'8':{images:[{filename:'whole.png',subfolder:'kh_sora/test',type:'output'}]}}}}:{});}
  if(req.url.startsWith('/view?')){res.setHeader('Content-Type','image/png');return res.end(source);}
  res.statusCode=404;res.end('{}');
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
try{
  const client=new Comfy('http://127.0.0.1:'+server.address().port),relative=path.relative(ROOT,path.join(scratch,'mock_attempt'));
  const queued=await submit(client,job,relative);assert.equal(queued.status,'queued');assert.equal(submissions,1);
  await assert.rejects(submit(client,job,relative),/Attempt already exists/);assert.equal(submissions,1);
  const waiting=await collect(relative,0);assert.equal(waiting.status,'queued');assert.equal(submissions,1);
  ready=true;const result=await collect(relative,0);assert.equal(result.status,'generated_pending_review');assert.equal(result.finalUserApproval,'pending');assert.equal(result.files[0].transparencyVerified,false);
  const before=historyCalls;await collect(relative,0);assert.equal(historyCalls,before);assert.equal(submissions,1);
  validation=true;const badRelative=path.relative(ROOT,path.join(scratch,'mock_validation_error'));
  const bad=await submit(client,job,badRelative);assert.equal(bad.errorClass,'tool_validation_error');assert.equal(bad.error,errorText);
  assert.equal(fs.readFileSync(path.join(ROOT,badRelative,'complete_error.txt'),'utf8'),errorText+'\n');
  await collect(badRelative,0);assert.equal(submissions,2);
  failureStatus=500;const uncertainRelative=path.relative(ROOT,path.join(scratch,'mock_uncertain_submission'));
  const uncertain=await submit(client,job,uncertainRelative);assert.equal(uncertain.status,'submission_uncertain');assert.equal(uncertain.errorClass,'service_failure');
  await collect(uncertainRelative,0);assert.equal(submissions,3);
  failureStatus=403;const permissionRelative=path.relative(ROOT,path.join(scratch,'mock_permission_rejection'));
  const permission=await submit(client,job,permissionRelative);assert.equal(permission.errorClass,'permissions_rejection');assert.equal(permission.status,'failed');
  await collect(permissionRelative,0);assert.equal(submissions,4);
  return 'PASS: local-only endpoints, workspace boundaries,8-node complete-image graph, live checkpoint check, multipart upload, queue receipt, no duplicate submission, bounded collection, preserved raw400/403/500 errors, separate validation/permissions/service classes, uncertain-submission recovery, pending review/approval and no transparency claim. Mock files retained under ignored .local; no real image generation.';
}finally{server.closeAllConnections();await new Promise(resolve=>server.close(resolve));}
}
if(typeof process!=='undefined'&&process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  console.log(await checkLocalAdapter(await import('./comfy_local.mjs')));
}
