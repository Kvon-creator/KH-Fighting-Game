// Dependency-free local ComfyUI client. Receipts prevent duplicate generation.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const HERE=path.dirname(fileURLToPath(import.meta.url));
export const ROOT=path.resolve(HERE,'../../../../../..');
if(ROOT.toLowerCase()!=='d:\\kh fighting game')throw new Error('Unexpected workspace');
const READY='design/sprites/smooth/sora/replacement_work/ready';
const CLASSES=['CheckpointLoaderSimple','CLIPTextEncode','LoadImage','VAEEncode','KSampler','VAEDecode','SaveImage'];
const INPAINT_CLASSES=['LoadImageMask','VAEEncodeForInpaint','ImageCompositeMasked'];
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const json=file=>JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));
function write(file,value,exclusive=false){fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n',{flag:exclusive?'wx':'w'});}
export function projectPath(relative,mustExist=false){
  const full=path.resolve(ROOT,relative);
  if(!full.toLowerCase().startsWith(ROOT.toLowerCase()+path.sep))throw new Error('Path escaped workspace');
  if(mustExist&&!fs.realpathSync(full).toLowerCase().startsWith(ROOT.toLowerCase()+path.sep))throw new Error('Symlink escaped workspace');
  return full;
}
function pngInfo(bytes){
  if(bytes.length<33||!bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))throw new Error('Expected PNG data');
  return {width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20),colorType:bytes[25],hasAlphaChannel:bytes[25]===4||bytes[25]===6};
}
export function readJob(file){
  const job=json(projectPath(file,true));
  if(!['run_start','run_loop','run_stop'].includes(job.animation))throw new Error('Current scope is running animations');
  if(job.checkpoint!=='DreamShaper_8_pruned.safetensors')throw new Error('Checkpoint is outside prepared installation');
  if(typeof job.positive!=='string'||!job.positive.trim()||typeof job.negative!=='string')throw new Error('Missing exact prompts');
  for(const [key,min,max] of [['steps',8,80],['cfg',1,20],['denoise',.1,.85]])if(!Number.isFinite(job[key])||job[key]<min||job[key]>max)throw new Error(`Invalid ${key}`);
  if(!Number.isSafeInteger(job.seed)||job.seed<0||!Number.isInteger(job.steps))throw new Error('Invalid seed/steps');
  if(job.sampler!=='dpmpp_2m'||job.scheduler!=='karras')throw new Error('Unexpected pilot sampler');
  if(typeof job.sourceSheet!=='string'||!/^\w{64}$/.test(job.sourceSheetSha256??'')||sha(fs.readFileSync(projectPath(job.sourceSheet,true)))!==job.sourceSheetSha256)throw new Error('Original source sheet hash differs');
  const reference=fs.readFileSync(projectPath(job.reference,true)),info=pngInfo(reference);
  if(info.width!==512||info.height!==512||info.colorType!==2)throw new Error('Use one complete512px RGB reference on white');
  let maskSha256;
  if(job.mask){
    const mask=fs.readFileSync(projectPath(job.mask,true)),maskInfo=pngInfo(mask);
    if(maskInfo.width!==512||maskInfo.height!==512||maskInfo.colorType!==2)throw new Error('Use one512px RGB temporary canvas selection');
    maskSha256=sha(mask);
  }
  return {...job,referenceSha256:sha(reference),...(maskSha256?{maskSha256}:{})};
}
export function workflow(job,uploadedName,prefix,uploadedMask){
  const graph={
    '1':{class_type:'CheckpointLoaderSimple',inputs:{ckpt_name:job.checkpoint}},
    '2':{class_type:'CLIPTextEncode',inputs:{text:job.positive,clip:['1',1]}},
    '3':{class_type:'CLIPTextEncode',inputs:{text:job.negative,clip:['1',1]}},
    '4':{class_type:'LoadImage',inputs:{image:uploadedName}},
    '5':{class_type:'VAEEncode',inputs:{pixels:['4',0],vae:['1',2]}},
    '6':{class_type:'KSampler',inputs:{seed:job.seed,steps:job.steps,cfg:job.cfg,sampler_name:job.sampler,scheduler:job.scheduler,denoise:job.denoise,model:['1',0],positive:['2',0],negative:['3',0],latent_image:['5',0]}},
    '7':{class_type:'VAEDecode',inputs:{samples:['6',0],vae:['1',2]}},
    '8':{class_type:'SaveImage',inputs:{filename_prefix:prefix,images:['7',0]}}
  };
  if(job.mask){
    if(!uploadedMask)throw new Error('Upload the temporary selection before building the inpaint graph');
    graph['9']={class_type:'LoadImageMask',inputs:{image:uploadedMask,channel:'red'}};
    graph['5']={class_type:'VAEEncodeForInpaint',inputs:{pixels:['4',0],vae:['1',2],mask:['9',0],grow_mask_by:8}};
    graph['10']={class_type:'ImageCompositeMasked',inputs:{destination:['4',0],source:['7',0],x:0,y:0,resize_source:false,mask:['9',0]}};
    graph['8'].inputs.images=['10',0];
  }
  for(const node of Object.values(graph))if(![...CLASSES,...INPAINT_CLASSES].includes(node.class_type))throw new Error('Only prepared built-in local nodes are permitted');
  return graph;
}
export class Comfy {
  constructor(endpoint='http://127.0.0.1:8188'){
    const url=new URL(endpoint);
    if(url.protocol!=='http:'||url.hostname!=='127.0.0.1'||url.username||url.password||url.pathname!=='/'||url.search||url.hash)throw new Error('Only local loopback ComfyUI is supported');
    this.endpoint=url.origin;
  }
  async request(route,options={}){
    const response=await fetch(this.endpoint+route,{...options,redirect:'error',signal:AbortSignal.timeout(20000)});
    const raw=await response.text();
    if(!response.ok){const error=new Error(raw);error.httpStatus=response.status;error.raw=raw;throw error;}
    try{return {raw,data:JSON.parse(raw)};}catch(cause){const error=new Error('Invalid JSON response');error.raw=raw;error.httpStatus=response.status;error.cause=cause;throw error;}
  }
  async status(requiredClasses=CLASSES){
    const stats=(await this.request('/system_stats')).data;
    if(!stats.system||!Array.isArray(stats.devices))throw new Error('Endpoint is not a recognized ComfyUI server');
    const definitions=(await this.request('/object_info')).data;
    const missing=requiredClasses.filter(name=>!definitions[name]);
    const checkpoints=definitions.CheckpointLoaderSimple?.input?.required?.ckpt_name?.[0]??[];
    return {available:true,endpoint:this.endpoint,devices:stats.devices,system:stats.system,missingNodes:missing,checkpointAvailable:checkpoints.includes('DreamShaper_8_pruned.safetensors'),definitions};
  }
}
function verifyReceiptFolder(relative){
  const folder=projectPath(relative,true);
  if(!fs.statSync(folder).isDirectory())throw new Error('Receipt folder missing');
  return folder;
}
function summary(receipt){return {status:receipt.status,promptId:receipt.promptId??null,errorClass:receipt.errorClass??null,error:receipt.error??null,files:receipt.files??[],finalUserApproval:'pending'};}
export function serverImagePath(output){
  // Native Windows ComfyUI returns relative subfolders with backslashes.
  // Normalize separators while still rejecting roots, drives and traversal.
  if(!output||typeof output.filename!=='string'||!output.filename||path.basename(output.filename)!==output.filename||/[\\/:\x00-\x1f]/.test(output.filename)||!output.filename.toLowerCase().endsWith('.png')||typeof output.subfolder!=='string'||output.type!=='output')throw new Error('Unsafe image path in history');
  const subfolder=output.subfolder.replaceAll('\\','/');
  if(subfolder.startsWith('/')||subfolder.includes('..')||/[:\x00-\x1f]/.test(subfolder)||(subfolder&&subfolder.split('/').some(part=>!part||part==='.')))throw new Error('Unsafe image path in history');
  return {filename:output.filename,subfolder,type:'output'};
}
export async function submit(client,job,relativeFolder){
  const folder=projectPath(relativeFolder);
  if(fs.existsSync(folder))throw new Error('Attempt already exists; collect its receipt instead of resubmitting');
  const parent=path.dirname(folder);fs.mkdirSync(parent,{recursive:true});projectPath(path.relative(ROOT,parent),true);
  const live=await client.status(job.mask?[...CLASSES,...INPAINT_CLASSES]:CLASSES);
  if(live.missingNodes.length||!live.checkpointAvailable)throw new Error('Prepared nodes/checkpoint are unavailable; no prompt submitted');
  fs.mkdirSync(folder);
  const receiptFile=path.join(folder,'receipt.json');
  const receipt={status:'preparing',createdAtUtc:new Date().toISOString(),endpoint:client.endpoint,clientId:crypto.randomUUID(),jobSha256:sha(Buffer.from(JSON.stringify(job))),sourceSheet:job.sourceSheet,sourceSheetSha256:job.sourceSheetSha256,reference:job.reference,referenceSha256:job.referenceSha256,finalUserApproval:'pending'};
  if(job.mask){receipt.mask=job.mask;receipt.maskSha256=job.maskSha256;}
  write(receiptFile,receipt,true);write(path.join(folder,'job.json'),job,true);
  try{
    const reference=fs.readFileSync(projectPath(job.reference,true));
    if(sha(reference)!==job.referenceSha256)throw new Error('Reference changed after planning');
    // Explicit multipart encoding also works in restricted JavaScript runtimes
    // that provide fetch but do not expose FormData or Blob globals.
    const boundary='sora_'+crypto.randomUUID();
    const multipart=Buffer.concat([
      Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="image"; filename="sora_${job.referenceSha256.slice(0,16)}.png"\r\nContent-Type: image/png\r\n\r\n`),reference,
      Buffer.from(`\r\n--${boundary}\r\nContent-Disposition: form-data; name="type"\r\n\r\ninput\r\n--${boundary}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\nfalse\r\n--${boundary}--\r\n`)
    ]);
    const upload=await client.request('/upload/image',{method:'POST',headers:{'Content-Type':`multipart/form-data; boundary=${boundary}`},body:multipart});
    fs.writeFileSync(path.join(folder,'upload_response.txt'),upload.raw,{flag:'wx'});
    const name=upload.data.name,sub=upload.data.subfolder??'';
    if(typeof name!=='string'||path.basename(name)!==name||/[\\/:]/.test(name)||sub.includes('..')||sub.startsWith('/')||/[\\:]/.test(sub))throw new Error('Unexpected server upload path');
    let maskName;
    if(job.mask){
      const mask=fs.readFileSync(projectPath(job.mask,true));
      if(sha(mask)!==job.maskSha256)throw new Error('Temporary selection changed after planning');
      const maskBoundary='sora_'+crypto.randomUUID();
      const maskBody=Buffer.concat([
        Buffer.from(`--${maskBoundary}\r\nContent-Disposition: form-data; name="image"; filename="sora_mask_${job.maskSha256.slice(0,16)}.png"\r\nContent-Type: image/png\r\n\r\n`),mask,
        Buffer.from(`\r\n--${maskBoundary}\r\nContent-Disposition: form-data; name="type"\r\n\r\ninput\r\n--${maskBoundary}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\nfalse\r\n--${maskBoundary}--\r\n`)
      ]);
      const maskUpload=await client.request('/upload/image',{method:'POST',headers:{'Content-Type':`multipart/form-data; boundary=${maskBoundary}`},body:maskBody});
      fs.writeFileSync(path.join(folder,'mask_upload_response.txt'),maskUpload.raw,{flag:'wx'});
      const maskFile=maskUpload.data.name,maskSub=maskUpload.data.subfolder??'';
      if(typeof maskFile!=='string'||path.basename(maskFile)!==maskFile||/[\\/:]/.test(maskFile)||typeof maskSub!=='string'||maskSub.includes('..')||maskSub.startsWith('/')||/[\\:]/.test(maskSub))throw new Error('Unexpected selection upload path');
      maskName=maskSub?`${maskSub}/${maskFile}`:maskFile;
    }
    const graph=workflow(job,sub?`${sub}/${name}`:name,`kh_sora/${job.animation}/${path.basename(folder)}`,maskName);
    const body={prompt:graph,client_id:receipt.clientId,extra_data:{sora_attempt:path.basename(folder)}};
    write(path.join(folder,'request.json'),body,true);
    receipt.status='submitting';write(receiptFile,receipt);
    const queued=await client.request('/prompt',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    fs.writeFileSync(path.join(folder,'prompt_response.txt'),queued.raw,{flag:'wx'});
    if(typeof queued.data.prompt_id!=='string'||!queued.data.prompt_id)throw new Error('No prompt ID returned; submission outcome uncertain');
    receipt.promptId=queued.data.prompt_id;receipt.status='queued';write(receiptFile,receipt);
  }catch(error){
    receipt.error=error.raw??String(error);receipt.httpStatus=error.httpStatus??null;
    const uncertain=receipt.status==='submitting'&&![400,401,403].includes(error.httpStatus);
    receipt.errorClass=error.httpStatus===400?'tool_validation_error':[401,403].includes(error.httpStatus)?'permissions_rejection':error.httpStatus>=500?'service_failure':uncertain?'submission_uncertain':'upload_or_service_failure';
    receipt.status=uncertain?'submission_uncertain':'failed';
    fs.writeFileSync(path.join(folder,'complete_error.txt'),receipt.error+'\n',{flag:'wx'});write(receiptFile,receipt);
  }
  return summary(receipt);
}
export async function collect(relativeFolder,waitMs=45000){
  if(!Number.isInteger(waitMs)||waitMs<0||waitMs>45000)throw new Error('Collection wait must be0-45000ms');
  const folder=verifyReceiptFolder(relativeFolder),receiptFile=path.join(folder,'receipt.json'),receipt=json(receiptFile);
  if(receipt.status==='generated_pending_review'){
    for(const item of receipt.files)if(sha(fs.readFileSync(path.join(folder,item.file)))!==item.sha256)throw new Error('Collected image hash changed');
    return summary(receipt);
  }
  if(!receipt.promptId)return summary(receipt);
  const client=new Comfy(receipt.endpoint),deadline=Date.now()+waitMs;
  do{
    const response=await client.request('/history/'+encodeURIComponent(receipt.promptId));
    fs.writeFileSync(path.join(folder,'history_response.json'),response.raw);
    const result=response.data[receipt.promptId];
    if(result?.status?.status_str==='error'){
      receipt.status='failed';receipt.errorClass='execution_failure';receipt.error=response.raw;write(receiptFile,receipt);return summary(receipt);
    }
    const outputs=(result?.outputs?.['8']?.images??[]).filter(i=>i.type==='output');
    if(result?.status?.completed&&outputs.length){
      const files=[];
      for(let index=0;index<outputs.length;index++){
        const output=outputs[index];
        const query=new URLSearchParams(serverImagePath(output));
        const response=await fetch(client.endpoint+'/view?'+query,{redirect:'error',signal:AbortSignal.timeout(20000)});
        if(!response.ok)throw new Error(`Image download HTTP${response.status}: ${await response.text()}`);
        const bytes=Buffer.from(await response.arrayBuffer()),info=pngInfo(bytes);
        if(info.width!==512||info.height!==512)throw new Error('Unexpected generated canvas size');
        const file=`candidate_${String(index).padStart(2,'0')}.png`,target=path.join(folder,file);
        if(fs.existsSync(target)){if(sha(fs.readFileSync(target))!==sha(bytes))throw new Error('Preserve different partial download');}
        else fs.writeFileSync(target,bytes,{flag:'wx'});
        files.push({file,sha256:sha(bytes),...info,transparencyVerified:false,serverImage:output});
      }
      receipt.files=files;receipt.status='generated_pending_review';write(receiptFile,receipt);return summary(receipt);
    }
    if(result?.status?.completed){receipt.status='failed';receipt.errorClass='completed_without_image';receipt.error=response.raw;write(receiptFile,receipt);return summary(receipt);}
    if(Date.now()>=deadline)break;
    await new Promise(resolve=>setTimeout(resolve,750));
  }while(Date.now()<deadline);
  return summary(receipt);
}
if(typeof process!=='undefined'&&process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  try{
    const [command,arg,attempt]=process.argv.slice(2),plan=json(path.join(HERE,'setup_plan.json'));
    let result;
    if(command==='status'){result=await new Comfy(plan.endpoint).status();delete result.definitions;}
    else if(command==='plan'){const job=readJob(arg);result={job,workflow:workflow(job,'REFERENCE_UPLOADED_AFTER_SETUP','kh_sora/pilot'),status:'prepared_not_submitted'};}
    else if(command==='submit'){
      if(!/^attempt_[0-9]{2,}$/.test(attempt??''))throw new Error('Use a fresh numbered attempt');
      const job=readJob(arg);result=await submit(new Comfy(plan.endpoint),job,`${READY}/${job.animation}/comfyui_trial/${attempt}`);
    }else if(command==='collect'){
      if(!arg?.replaceAll('\\','/').startsWith(READY+'/'))throw new Error('Collect a receipt inside the ready animation folders');
      result=await collect(arg);
    }else throw new Error('Use status, plan JOB, submit JOB attempt_NN, or collect RECEIPT_FOLDER');
    console.log(JSON.stringify(result,null,2));
  }catch(error){console.error(JSON.stringify({status:'error',completeError:error.raw??String(error),httpStatus:error.httpStatus??null},null,2));process.exitCode=1;}
}
