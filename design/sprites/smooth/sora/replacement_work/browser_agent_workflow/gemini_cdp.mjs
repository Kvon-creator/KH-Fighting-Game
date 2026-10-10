// Scoped Gemini browser connection. Uses Node 22+ built-ins; installs nothing.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
const here = path.dirname(fileURLToPath(import.meta.url));
const root = fs.realpathSync(path.resolve(here, '../../../../../..'));
if (root.toLowerCase() !== 'd:\\kh fighting game') throw Error(`Unexpected workspace: ${root}`);
const argv = process.argv.slice(2);
const command = argv.shift() || 'inspect';
const options = {};
while (argv.length) {
  const key = argv.shift();
  if (!key.startsWith('--') || !argv.length) throw Error('Options require --name value.');
  options[key.slice(2)] = argv.shift();
}
const allowed = new Set(['inspect', 'screenshot', 'click', 'upload', 'type', 'hit-test', 'ax-menu', 'attach-references', 'save-image', 'download-image', 'record', 'exchange', 'new-chat']);
if (!allowed.has(command)) throw Error(`Unknown command: ${command}`);
const port = Number(options.port || 9222);
if (!Number.isInteger(port) || port < 1024 || port > 65535) throw Error('Invalid local port.');
const local = path.join(root, '.local', 'browser-agent');
function inside(file) {
  const full = path.resolve(root, file);
  const rel = path.relative(root, full);
  if (rel === '..' || rel.startsWith(`..${path.sep}`) || path.isAbsolute(rel)) throw Error('Path outside workspace.');
  return full;
}
function candidateDirectory() {
  if(!options.output)throw Error('Supply a separate candidate output directory.');
  const out=inside(options.output);
  const relative=path.relative(root,out).replaceAll('\\','/');
  if(!/^design\/sprites\/smooth\/sora\/replacement_work\/ready\/(run_start|run_loop|run_stop)\/gemini_browser_trial\/attempt_\d+$/.test(relative))throw Error('Only a separate running candidate directory is allowed.');
  fs.mkdirSync(out,{recursive:true});
  return out;
}
function isGemini(url) {
  try { const u = new URL(url); return u.origin === 'https://gemini.google.com' && /^\/(?:app|videos)(?:\/|$)/.test(u.pathname); }
  catch { return false; }
}
const response = await fetch(`http://127.0.0.1:${port}/json/list`, {signal: AbortSignal.timeout(5000)});
if (!response.ok) throw Error(`Debug endpoint HTTP ${response.status}`);
const pages = (await response.json()).filter(p => p.type === 'page' && isGemini(p.url));
const candidates = options.target ? pages.filter(p => p.id === options.target) : pages;
if (candidates.length !== 1) {
  console.log(JSON.stringify({geminiTabs: pages.map(p => ({id:p.id, url:p.url, title:p.title}))}, null, 2));
  throw Error(`Expected one Gemini tab, found ${candidates.length}. Use --target with an observed id.`);
}
const tab = candidates[0];
const wsURL = new URL(tab.webSocketDebuggerUrl);
if (wsURL.protocol !== 'ws:' || !['127.0.0.1', 'localhost', '[::1]'].includes(wsURL.hostname) || Number(wsURL.port) !== port) {
  throw Error('Only the selected local debugging endpoint is allowed.');
}
const socket = new WebSocket(wsURL);
await new Promise((resolve, reject) => {
  const timeout = setTimeout(() => reject(Error('WebSocket connection timeout')), 5000);
  socket.addEventListener('open', () => {clearTimeout(timeout); resolve();}, {once:true});
  socket.addEventListener('error', () => {clearTimeout(timeout); reject(Error('WebSocket connection failed'));}, {once:true});
});
let sequence = 0;
const pending = new Map();
const contexts = new Map();
let chooserCallback;
socket.addEventListener('message', event => {
  const message = JSON.parse(String(event.data));
  if (message.method === 'Runtime.executionContextCreated') contexts.set(message.params.context.id,message.params.context);
  if (message.method === 'Runtime.executionContextDestroyed') contexts.delete(message.params.executionContextId);
  if (message.method === 'Page.fileChooserOpened' && chooserCallback) chooserCallback(message.params);
  const request = pending.get(message.id);
  if (!request) return;
  clearTimeout(request.timer); pending.delete(message.id);
  if (message.error) request.reject(Error(JSON.stringify(message.error)));
  else request.resolve(message.result);
});
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => {pending.delete(id); reject(Error(`${method} timed out`));}, 8000);
    pending.set(id, {resolve, reject, timer});
    socket.send(JSON.stringify({id, method, params}));
  });
}
async function evaluate(expression, byValue = true) {
  const wrapped = `(() => {
    const roots = [document];
    for (let i=0; i<roots.length; i++) for (const e of roots[i].querySelectorAll('*')) if(e.shadowRoot) roots.push(e.shadowRoot);
    const queryAll = selector => roots.flatMap(r=>[...r.querySelectorAll(selector)]);
    const queryOne = selector => {let es=queryAll(selector);const wanted=${JSON.stringify(options.text||null)};if(wanted!==null)es=es.filter(e=>e.innerText?.trim().split('\\n')[0]===wanted);if(es.length!==1)throw Error('Control is not unique');return es[0];};
    return (${expression});
  })()`;
  const out = await send('Runtime.evaluate', {expression:wrapped, contextId:mainContext.id, returnByValue:byValue, userGesture:true});
  if (out.exceptionDetails) throw Error(JSON.stringify(out.exceptionDetails));
  return byValue ? out.result.value : out.result;
}
await send('Page.enable');
await send('Runtime.enable');
const frameTree = await send('Page.getFrameTree');
const mainContexts = [...contexts.values()].filter(c=>c.auxData?.isDefault&&c.auxData?.frameId===frameTree.frameTree.frame.id);
if (mainContexts.length!==1) {socket.close();throw Error(`Expected one active main-frame context, found ${mainContexts.length}`);}
const mainContext=mainContexts[0];
const referenceSets = {original: [
  'design/sprites/smooth/sora/replacement_work/ready/standing_idle/sora_stand_idle_00.png',
  'design/sprites/smooth/sora/replacement_work/ready/run_loop/layers/frame_00_review_v1/sora_run_loop_00_review.png',
  'design/references/Sora_KHIV_Render.webp'
], 'idle-only': [
  'design/sprites/smooth/sora/replacement_work/ready/standing_idle/sora_stand_idle_00.png'
], 'anticipation-endpoints': [
  'design/sprites/smooth/sora/replacement_work/ready/standing_idle/sora_stand_idle_00.png',
  'design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial/attempt_08/gemini_original_preview.jpg'
], 'release-endpoint': [
  'design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial/attempt_11/gemini_original_preview.jpg'
], 'release-cleanup': [
  'design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial/attempt_12/gemini_original_preview.jpg'
], 'first-lift': [
  'design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial/attempt_13/gemini_original_preview.jpg'
], 'far-carry': [
  'design/sprites/smooth/sora/replacement_work/ready/standing_idle/sora_stand_idle_00.png',
  'design/references/Sora_KHIV_Render.webp'
] , 'start-guide': [
  'design/sprites/smooth/sora/replacement_work/ready/standing_idle/sora_stand_idle_00.png',
  'design/references/Sora_KHIV_Render.webp',
  'design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial/guides/start_pose_guide_00_03.png'
], 'start-guide-middle': [
  'design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial/attempt_03/frame_review_v1/sora_run_start_03.png',
  'design/sprites/smooth/sora/replacement_work/ready/standing_idle/sora_stand_idle_00.png',
  'design/references/Sora_KHIV_Render.webp',
  'design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial/guides/start_pose_guide_04_07.png'
], 'motion-loop': [
  'design/sprites/smooth/sora/replacement_work/ready/run_loop/gemini_browser_trial/attempt_08/gemini_original_preview.jpg'
]};
const referenceSet=options['reference-set']||'original';
if(referenceSet==='start-new-pose') {
  const pose=Number(options['next-pose']);
  if(!Number.isInteger(pose)||pose<1||pose>11)throw Error('Start pose must be01-11.');
  referenceSets[referenceSet]=['design/sprites/smooth/sora/replacement_work/ready/standing_idle/sora_stand_idle_00.png',`design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial/guides_clean/guide_${String(pose).padStart(2,'0')}.png`];
}
if(referenceSet==='next-start-frame') {
  const nextPose=Number(options['next-pose']);
  if(!Number.isInteger(nextPose)||nextPose<1||nextPose>11)throw Error('Next start pose must be01-11.');
  const previous=inside(options['previous-frame']||'');
  const relative=path.relative(root,previous).replaceAll('\\','/');
  if(!/^design\/sprites\/smooth\/sora\/replacement_work\/ready\/run_start\/gemini_browser_trial\/attempt_\d+\/frame_review_v1\/sora_run_start_\d+\.png$/.test(relative))throw Error('Previous frame must be a complete exported run-start candidate.');
  referenceSets[referenceSet]=[relative,`design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial/guides_clean/guide_${String(nextPose).padStart(2,'0')}.png`];
}
if(!Object.hasOwn(referenceSets,referenceSet))throw Error('Unknown project art reference set.');
const referenceFiles=referenceSets[referenceSet].map(inside);
async function guard() {
  const currentURL = await evaluate('location.href');
  if (!isGemini(currentURL)) throw Error(`Target left Gemini: ${currentURL}. Stop; login is performed by the user.`);
}
const observation = `(() => {
  const visible = e => e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  const bodyText = document.body.innerText;
  const conversationStart = bodyText.lastIndexOf('Conversation with Gemini');
  const chatText = conversationStart >= 0 ? bodyText.slice(conversationStart) : (document.querySelector('main')?.innerText || '');
  return {url:location.href, title:document.title, text:chatText.slice(-14000),
    controls:queryAll('button,input,textarea,[contenteditable="true"],[role="button"],[role="menuitem"]')
      .filter(visible).map(e=>({tag:e.tagName,id:e.id,role:e.getAttribute('role'),type:e.getAttribute('type'),
        label:e.getAttribute('aria-label'),text:e.innerText?.slice(0,140),disabled:!!e.disabled,
        classes:e.className,href:e.tagName==='A'?e.href:undefined})),
    fileInputs:queryAll('input[type="file"]').map(e=>({id:e.id,classes:e.className,accept:e.accept,multiple:e.multiple})),
    videoControls:queryAll('a,button,[role="button"],[role="menuitem"]').filter(e=>visible(e)&&/^(Create video|Videos|Video)$/.test(e.innerText?.trim())||visible(e)&&/Create video/.test(e.getAttribute('aria-label')||'')).map(e=>({tag:e.tagName,role:e.getAttribute('role'),label:e.getAttribute('aria-label'),text:e.innerText?.trim(),classes:e.className,href:e.href})),
    images:queryAll('img').filter(e=>visible(e)&&e.naturalWidth>200).map(e=>({alt:e.alt,width:e.naturalWidth,height:e.naturalHeight})),
    videos:queryAll('video').map(e=>({width:e.videoWidth,height:e.videoHeight,duration:Number.isFinite(e.duration)?e.duration:null,readyState:e.readyState,error:e.error?.code})),
    shadowHosts:roots.slice(1).map(r=>({tag:r.host.tagName,classes:r.host.className})),
    uploadMenuItems:queryAll('*').filter(e=>visible(e)&&e.children.length===0&&/^(Upload files|Create image|Add from Drive|More uploads)$/.test(e.textContent.trim())).map(e=>({text:e.textContent.trim(),tag:e.tagName,classes:e.className,parents:[e.parentElement,e.parentElement?.parentElement].filter(Boolean).map(p=>({tag:p.tagName,classes:p.className,role:p.getAttribute('role')}))})),
    viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio}};
})()`;
function promptFile() {
  const file=options.prompt?inside(options.prompt):path.join(here,'PILOT_PROMPT.txt');
  const relative=path.relative(here,fs.realpathSync(file));
  if(relative.startsWith('..')||path.isAbsolute(relative)||path.extname(file)!=='.txt')throw Error('Only workflow prompt .txt files are allowed.');
  return file;
}
async function paint() {
  // Flush the page's pending render before reading or deciding whether to submit.
  await send('Page.captureScreenshot',{format:'jpeg',quality:20,captureBeyondViewport:false});
}
async function stateSummary() {
  const state=await evaluate(observation);
  return {url:state.url,responseTail:state.text.slice(-1000),images:state.images.map(i=>({kind:i.alt.endsWith('generated')?'generated':i.alt==='Uploaded image preview'?'reference':i.alt.slice(0,80),width:i.width,height:i.height})),fileInputs:state.fileInputs.map(i=>({...i,accept:i.accept.startsWith('image')?i.accept:i.accept.slice(0,60)})),videoControls:state.videoControls,controls:state.controls.filter(c=>/Send message|Stop|Download|Enter a prompt|Open mode picker|Upload & tools/.test(c.label||'')).map(c=>({label:c.label,disabled:c.disabled,text:c.text}))};
}
function reportJob(job) {
  console.log(JSON.stringify({status:job.status,attempt:options.output,preview:job.preview,originalDownload:job.originalDownload,size:job.nativePreviewSize,video:job.videoMetadata,review:job.review,finalUserApproval:job.finalUserApproval,exactResponse:job.exactResponse,note:job.note}));
}
async function exchange() {
  const media=options.media||'image';
  if(!['image','video'].includes(media))throw Error('Media must be image or video.');
  const timeoutSeconds=Number(options.timeout||180);
  if(!Number.isFinite(timeoutSeconds)||timeoutSeconds<1||timeoutSeconds>600)throw Error('Timeout must be between 1 and 600 seconds.');
  const out=candidateDirectory();
  const receipt=path.join(out,'exchange_state.json');
  const file=promptFile();
  // Git may restore Windows line endings; preserve receipt identity across checkouts.
  const prompt=fs.readFileSync(file,'utf8').replace(/\r\n/g,'\n');
  if(!prompt.trim()||prompt.length>16000)throw Error('Prompt is empty or too long.');
  const digest=text=>createHash('sha256').update(text).digest('hex');
  const images=()=>evaluate(`queryAll('img[alt$="generated"]').filter(e=>e.complete&&e.naturalWidth>0).map(e=>({url:e.src,width:e.naturalWidth,height:e.naturalHeight}))`);
  const videos=()=>evaluate(`queryAll('video').map(e=>({url:e.currentSrc||e.src,width:e.videoWidth,height:e.videoHeight,duration:Number.isFinite(e.duration)?e.duration:null,readyState:e.readyState})).filter(e=>e.url)`);
  const save=state=>fs.writeFileSync(receipt,JSON.stringify(state,null,2));
  let job=fs.existsSync(receipt)?JSON.parse(fs.readFileSync(receipt,'utf8')):null;
  if(job&&job.promptSha256!==digest(prompt))throw Error('Attempt belongs to a different prompt; use another attempt directory.');
  if(['ready_for_visual_review','ready_for_video_review','provider_block'].includes(job?.status)) {reportJob(job);return;}
  if(job?.tabId&&job.tabId!==tab.id)throw Error('This in-progress attempt belongs to another Gemini tab; use its recorded --target.');
  await paint();
  await guard();
  if(!job) {
    let state=await evaluate(observation);
    const uploadDeadline=Date.now()+30000;
    while(state.text.includes('Uploading image')&&Date.now()<uploadDeadline) {
      await new Promise(resolve=>setTimeout(resolve,1000));await paint();await guard();
      state=await evaluate(observation);
    }
    if(state.text.includes('Uploading image'))throw Error('Art references are still uploading; no prompt submitted.');
    const videoMode=state.controls.some(c=>c.label==='Deselect Videos');
    if(media!=='video'&&videoMode)throw Error('Video mode is selected; do not submit an image/text request in this mode.');
    if(media==='video'&&!videoMode)throw Error('Select the observed video mode before requesting a clip.');
    if(state.controls.some(c=>/^Stop/.test(c.label||'')))throw Error('Gemini is still responding; do not submit another prompt.');
    const composer='[aria-label="Enter a prompt for Gemini"]';
    const current=await evaluate(`queryOne(${JSON.stringify(composer)}).innerText`);
    if(current.trim())throw Error('Composer contains text; do not overwrite it.');
    const refs=[...referenceFiles];
    if(options['attach-references']==='true') {
      refs.forEach(f=>{if(!fs.statSync(f).isFile())throw Error(`Missing art reference: ${f}`);});
      await evaluate(`queryOne('button[aria-label="Upload & tools"]').click()`);await paint();
      const input=await evaluate(`queryOne('input[type="file"][accept^="image"]')`,false);
      await send('DOM.setFileInputFiles',{files:refs,objectId:input.objectId});await paint();
      const attachmentDeadline=Date.now()+30000;
      let uploaded=await evaluate(observation);
      while(uploaded.text.includes('Uploading image')&&Date.now()<attachmentDeadline) {
        await new Promise(resolve=>setTimeout(resolve,1000));await paint();await guard();
        uploaded=await evaluate(observation);
      }
      if(uploaded.text.includes('Uploading image'))throw Error('Art references are still uploading; no prompt submitted.');
    }
    if(options['weapon-reference']==='true') {
      const weapon=inside('design/sprites/smooth/sora/replacement_work/ready/run_loop/layers/art_pass_05/kingdom_key_master_finished.png');
      await evaluate(`queryOne('button[aria-label="Upload & tools"]').click()`);await paint();
      const input=await evaluate(`queryOne('input[type="file"][accept^="image"]')`,false);
      await send('DOM.setFileInputFiles',{files:[weapon],objectId:input.objectId});await paint();
      refs.push(weapon);
    }
    job={status:'prepared',media,tabId:tab.id,chatUrl:state.url,referenceSet,promptSha256:digest(prompt),promptFile:path.relative(root,file),mode:state.controls.find(c=>c.label?.startsWith('Open mode picker'))?.text,createdAt:new Date().toISOString(),baselineImages:(await images()).map(i=>digest(i.url)),baselineVideos:(await videos()).map(i=>digest(i.url)),references:refs.map(f=>({file:path.relative(root,f),sha256:digest(fs.readFileSync(f))})),finalUserApproval:'pending'};
    fs.writeFileSync(path.join(out,'submitted_prompt.txt'),prompt,{flag:'wx'});
    save(job);
    await evaluate(`queryOne(${JSON.stringify(composer)}).focus()`);
    await send('Input.insertText',{text:prompt});
    await paint();
    const actual=await evaluate(`queryOne(${JSON.stringify(composer)}).innerText`);
    if(actual.replace(/\s+/g,' ').trim()!==prompt.replace(/\s+/g,' ').trim())throw Error('Composer verification failed; no prompt submitted.');
    fs.writeFileSync(path.join(out,'composer_capture.json'),JSON.stringify({text:actual},null,2)+'\n',{flag:'wx'});
    const ready=await evaluate(`(()=>{const e=queryOne('button[aria-label="Send message"]');return !e.disabled})()`);
    if(!ready)throw Error('Send control is disabled.');
    // Save before sending: a resumed invocation collects instead of duplicating requests.
    job.status='submission_attempted';save(job);
    await evaluate(`queryOne('button[aria-label="Send message"]').click()`);
    await paint();
    console.log(JSON.stringify({status:'waiting_for_gemini',attempt:out}));
  } else if(job.status==='prepared') {
    throw Error('Prepared attempt was interrupted before confirmed submission. Inspect composer; do not resend automatically.');
  }
  const deadline=Date.now()+timeoutSeconds*1000;
  let lastNotice=Date.now();
  while(Date.now()<deadline) {
    await paint();await guard();
    const state=await evaluate(observation);
    const all=await images();
    const fresh=all.filter(i=>!job.baselineImages.includes(digest(i.url)));
    const busy=state.controls.some(c=>/^Stop/.test(c.label||''));
    const replyStart=state.text.lastIndexOf('Gemini said');
    const reply=replyStart>=0?state.text.slice(replyStart+'Gemini said'.length).trim():'';
    if(media==='video') {
      const clips=(await videos()).filter(v=>!(job.baselineVideos||[]).includes(digest(v.url))&&v.readyState>=1&&v.width>0&&v.duration>0);
      if(clips.length===1) {
        const {url,...videoMetadata}=clips[0];
        fs.writeFileSync(path.join(out,'gemini_response.txt'),reply);
        job={...job,status:'ready_for_video_review',chatUrl:state.url,completedAt:new Date().toISOString(),videoMetadata,review:'pending',finalUserApproval:'pending',note:'Video is ready in the browser. Preserve via its observed native download control before frame extraction.'};
        save(job);reportJob(job);return;
      }
      if(clips.length>1)throw Error('Multiple new clips appeared; inspect before collecting.');
    }
    if(media==='image'&&fresh.length===1&&!busy) {
      const info=fresh[0];
      const resource=await send('Page.getResourceContent',{frameId:frameTree.frameTree.frame.id,url:info.url});
      if(!resource.base64Encoded)throw Error('Generated resource is not binary.');
      const bytes=Buffer.from(resource.content,'base64');
      const ext=bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))?'png':bytes[0]===255&&bytes[1]===216?'jpg':bytes.toString('ascii',8,12)==='WEBP'?'webp':null;
      if(!ext)throw Error('Unsupported generated image format.');
      const preview=path.join(out,`gemini_original_preview.${ext}`);
      if(!fs.existsSync(preview))fs.writeFileSync(preview,bytes,{flag:'wx'});
      fs.writeFileSync(path.join(out,'gemini_response.txt'),reply);
      const before=new Set(fs.readdirSync(out));
      await send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:out,eventsEnabled:true});
      const original=await evaluate(`(()=>{const img=queryAll('img[alt$="generated"]').find(e=>e.src===${JSON.stringify(info.url)});if(!img)throw Error('Generated image disappeared');let p=img;for(let i=0;p&&i<9;i++,p=p.parentElement){const buttons=p.querySelectorAll('button[aria-label="Download full size image"]');if(buttons.length===1){buttons[0].click();return true;}}return false;})()`);
      await paint();
      let full=null;
      if(original)for(let i=0;i<60;i++) {
        const files=fs.readdirSync(out).filter(f=>!before.has(f)&&/\.(png|jpe?g|jfif|webp)$/i.test(f));
        if(files.length===1){full=path.join(out,files[0]);break;}
        if(files.length>1)throw Error('Multiple original downloads; inspect the candidate directory.');
        await new Promise(resolve=>setTimeout(resolve,500));
      }
      job={...job,status:'ready_for_visual_review',chatUrl:state.url,completedAt:new Date().toISOString(),preview,originalDownload:full,nativePreviewSize:[info.width,info.height],imageFormat:ext,review:'pending',finalUserApproval:'pending'};
      save(job);reportJob(job);return;
    }
    if(fresh.length>1)throw Error('More than one new image appeared; inspect before continuing.');
    if(!busy&&/can't generate|cannot generate|third.party content providers|quota|limit reached|something went wrong|try again later/i.test(reply)) {
      fs.writeFileSync(path.join(out,'gemini_response.txt'),reply);
      job={...job,status:'provider_block',exactResponse:reply};save(job);reportJob(job);return;
    }
    if(Date.now()-lastNotice>20000){console.log(JSON.stringify({status:'waiting_for_gemini',attempt:out}));lastNotice=Date.now();}
    await new Promise(resolve=>setTimeout(resolve,3000));
  }
  job={...job,status:'waiting_for_gemini',note:'Timed out collecting; rerun this same attempt to collect without resubmitting.'};save(job);reportJob(job);
}
try {
  await guard();
  if(command==='exchange') {
    await exchange();
  } else if(command==='new-chat') {
    await paint();
    const state=await evaluate(observation);
    if(state.controls.some(c=>/^Stop/.test(c.label||'')))throw Error('Finish the current generation before opening another context.');
    const text=await evaluate(`queryOne('[aria-label="Enter a prompt for Gemini"]').innerText`);
    if(text.trim())throw Error('Composer contains text; preserve it instead of navigating away.');
    await send('Page.navigate',{url:'https://gemini.google.com/app'});
    console.log(JSON.stringify({status:'opened_fresh_context',target:tab.id,url:'https://gemini.google.com/app',previousChatPreserved:true}));
  } else if (command === 'inspect') {
    await paint();
    console.log(JSON.stringify(options.verbose==='true'?await evaluate(observation):await stateSummary(),null,2));
  } else if(command==='record') {
    const out=candidateDirectory();
    const state=await evaluate(observation);
    fs.writeFileSync(path.join(out,`gemini_observation_${Date.now()}.json`),JSON.stringify(state,null,2),{flag:'wx'});
    console.log(JSON.stringify({recordedDirectory:out,text:state.text}));
  } else if(command==='download-image') {
    if(!options.selector)throw Error('Supply the observed download button selector.');
    const out=candidateDirectory();
    const before=new Set(fs.readdirSync(out));
    const query=JSON.stringify(options.selector);
    const label=await evaluate(`queryOne(${query}).getAttribute('aria-label')`);
    if(label!=='Download full size image')throw Error('Only the generated-image download control is allowed.');
    await send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:out,eventsEnabled:true});
    await evaluate(`queryOne(${query}).click()`);
    await send('Page.captureScreenshot',{format:'jpeg',quality:20,captureBeyondViewport:false});
    for(let i=0;i<40;i++) {
      const complete=fs.readdirSync(out).filter(f=>!before.has(f)&&/\.(png|jpe?g|jfif|webp)$/i.test(f));
      if(complete.length===1) {console.log(JSON.stringify({downloadedImage:path.join(out,complete[0])}));break;}
      if(complete.length>1)throw Error('Multiple downloaded images; review the candidate directory.');
      if(i===39)throw Error('Download not complete yet. Check this candidate directory without submitting again.');
      await new Promise(resolve=>setTimeout(resolve,500));
    }
  } else if (command === 'save-image') {
    if(!options.selector||!options.output)throw Error('Supply the observed image selector and candidate output directory.');
    const out=candidateDirectory();
    const info=await evaluate(`(()=>{const e=queryOne(${JSON.stringify(options.selector)});if(e.tagName!=='IMG'||!e.complete||!e.naturalWidth)throw Error('Generated image is not ready');return{url:e.currentSrc||e.src,width:e.naturalWidth,height:e.naturalHeight};})()`);
    const resource=await send('Page.getResourceContent',{frameId:frameTree.frameTree.frame.id,url:info.url});
    if(!resource.base64Encoded)throw Error('Image resource is not binary; do not save it as artwork.');
    const bytes=Buffer.from(resource.content,'base64');
    const ext=bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))?'png':bytes[0]===255&&bytes[1]===216?'jpg':bytes.toString('ascii',0,4)==='RIFF'&&bytes.toString('ascii',8,12)==='WEBP'?'webp':null;
    if(!ext)throw Error('Unsupported generated image format; preserve via the download control.');
    fs.mkdirSync(out,{recursive:true});
    const file=path.join(out,`gemini_original_preview.${ext}`);
    fs.writeFileSync(file,bytes,{flag:'wx'});
    console.log(JSON.stringify({savedImage:file,bytes:bytes.length,width:info.width,height:info.height}));
  } else if (command === 'ax-menu') {
    const tree = await send('Accessibility.getFullAXTree');
    console.log(JSON.stringify(tree.nodes.filter(n=>/upload|create image|add from drive|more tools/i.test(n.name?.value||'')).map(n=>({name:n.name?.value,role:n.role?.value,backendNodeId:n.backendDOMNodeId,ignored:n.ignored,properties:n.properties})),null,2));
  } else if (command === 'attach-references') {
    referenceFiles.forEach(f=>{if(!fs.statSync(f).isFile())throw Error(`Missing reference: ${f}`);});
    const tree = await send('Accessibility.getFullAXTree');
    const buttons = tree.nodes.filter(n=>!n.ignored&&n.role?.value==='menuitem'&&n.name?.value?.startsWith('Upload files.'));
    if(buttons.length!==1) throw Error('Observe and open the Upload files menu before attaching references.');
    await send('Page.enable');
    await send('Page.setInterceptFileChooserDialog',{enabled:true});
    let chooserTimer;
    try {
      const chooser = new Promise((resolve,reject)=>{
        chooserCallback=resolve;
        chooserTimer=setTimeout(()=>reject(Error('File chooser did not open; no references attached.')),6000);
      });
      const {model}=await send('DOM.getBoxModel',{backendNodeId:buttons[0].backendDOMNodeId});
      const q=model.border;
      const point={x:(q[0]+q[2]+q[4]+q[6])/4,y:(q[1]+q[3]+q[5]+q[7])/4};
      await send('Input.dispatchMouseEvent',{type:'mousePressed',...point,button:'left',clickCount:1});
      await send('Input.dispatchMouseEvent',{type:'mouseReleased',...point,button:'left',clickCount:1});
      const event=await chooser;
      clearTimeout(chooserTimer);
      if(!event.backendNodeId)throw Error('File input was not identified.');
      await send('DOM.setFileInputFiles',{files:referenceFiles,backendNodeId:event.backendNodeId});
      console.log(JSON.stringify({attachedReferences:referenceFiles}));
    } finally {
      clearTimeout(chooserTimer);chooserCallback=undefined;
      await send('Page.setInterceptFileChooserDialog',{enabled:false});
    }
    console.log(JSON.stringify(await evaluate(observation),null,2));
  } else if (command === 'hit-test') {
    const x=Number(options.x), y=Number(options.y);
    if (!Number.isFinite(x)||!Number.isFinite(y)||x<0||y<0) throw Error('Invalid observation coordinates.');
    console.log(JSON.stringify(await evaluate(`(() => {let e=document.elementFromPoint(${x},${y}); const out=[]; for(let i=0;e&&i<4;i++,e=e.parentElement)out.push({tag:e.tagName,id:e.id,classes:e.className,role:e.getAttribute('role'),label:e.getAttribute('aria-label'),text:e.innerText?.slice(0,400),html:e.outerHTML.slice(0,1500)});return out;})()`),null,2));
  } else if (command === 'screenshot') {
    fs.mkdirSync(local, {recursive:true});
    const out = path.join(local, `gemini-${Date.now()}.png`);
    const capture = await send('Page.captureScreenshot', {format:'png',captureBeyondViewport:false});
    fs.writeFileSync(out, Buffer.from(capture.data,'base64'), {flag:'wx'});
    console.log(JSON.stringify({screenshot:out}));
  } else {
    // Operators choose a unique control from an immediately preceding inspection.
    if (!options.selector) throw Error('Supply --selector from the current page observation.');
    const query = JSON.stringify(options.selector);
    const info = await evaluate(`(() => {const e=queryOne(${query});return {tag:e.tagName,type:e.type,editable:e.isContentEditable,disabled:!!e.disabled,text:e.innerText||'',value:e.value||'',label:e.getAttribute('aria-label')||'',href:e.href||''};})()`);
    if (/sign\s*in|log\s*in|password|captcha/i.test(`${info.label} ${info.text}`) || info.type === 'password') throw Error('Authentication must be performed by the user.');
    if (info.disabled) throw Error('Control is disabled.');
    if (command === 'upload') {
      if (info.tag !== 'INPUT' || info.type !== 'file') throw Error('Selected control is not a file input.');
      const files = referenceFiles;
      files.forEach(f=>{if(!fs.statSync(f).isFile())throw Error(`Missing reference: ${f}`);});
      const remote = await evaluate(`queryOne(${query})`, false);
      await send('DOM.setFileInputFiles', {files,objectId:remote.objectId});
      console.log(JSON.stringify({uploadedReferences:files}));
    } else if (command === 'type') {
      if (!info.editable && !['TEXTAREA','INPUT'].includes(info.tag)) throw Error('Selected control is not editable.');
      if (info.value.trim() || info.text.trim()) throw Error('Composer contains text; do not overwrite it.');
      const file = options.prompt ? inside(options.prompt) : path.join(here,'PILOT_PROMPT.txt');
      const rel = path.relative(here,fs.realpathSync(file));
      if (rel.startsWith('..') || path.isAbsolute(rel) || path.extname(file) !== '.txt') throw Error('Only workflow prompt .txt files are allowed.');
      const text = fs.readFileSync(file,'utf8');
      if (!text.trim() || text.length > 16000) throw Error('Prompt is empty or too long.');
      await evaluate(`queryOne(${query}).focus()`);
      await send('Input.insertText',{text});
      const actual = await evaluate(`(()=>{const e=queryOne(${query});return e.value??e.innerText})()`);
      if (actual.replace(/\s+/g,' ').trim() !== text.replace(/\s+/g,' ').trim()) throw Error('Composer verification failed; do not submit.');
      console.log(JSON.stringify({typedPrompt:file,characters:text.length}));
    } else if (command === 'click') {
      // This does not follow instructions found on the page. User-authorized operator chooses the action.
      if (info.href && !isGemini(info.href)) throw Error('Refuse to navigate outside the Gemini app.');
      if(info.label==='Send message') {
        const file=options.prompt?inside(options.prompt):path.join(here,'PILOT_PROMPT.txt');
        const rel=path.relative(here,fs.realpathSync(file));
        if(rel.startsWith('..')||path.isAbsolute(rel)||path.extname(file)!=='.txt')throw Error('Only workflow prompts may be submitted.');
        const expected=fs.readFileSync(file,'utf8');
        const actual=await evaluate(`(()=>{const e=queryOne('[aria-label="Enter a prompt for Gemini"]');return e.value??e.innerText})()`);
        if(actual.replace(/\s+/g,' ').trim()!==expected.replace(/\s+/g,' ').trim())throw Error('Send verification failed; no message submitted.');
        console.log(JSON.stringify({verifiedPrompt:file,composerText:actual}));
      }
      await send('Page.bringToFront');
      if(options.method==='dom') {
        await evaluate(`queryOne(${query}).click()`);
        console.log(JSON.stringify({clicked:options.selector,method:'dom'}));
      } else {
      const point = await evaluate(`(() => {const e=queryOne(${query});e.scrollIntoView({block:'nearest'});const r=e.getBoundingClientRect();const x=r.x+r.width/2,y=r.y+r.height/2;if(!r.width||!r.height)throw Error('Control is not visible');const hit=document.elementFromPoint(x,y);if(hit!==e&&!e.contains(hit))throw Error('Control is covered');return{x,y};})()`);
      await send('Input.dispatchMouseEvent',{type:'mouseMoved',...point});
      await send('Input.dispatchMouseEvent',{type:'mousePressed',...point,button:'left',clickCount:1});
      await send('Input.dispatchMouseEvent',{type:'mouseReleased',...point,button:'left',clickCount:1});
      console.log(JSON.stringify({clicked:options.selector,point}));
      }
      await new Promise(resolve=>setTimeout(resolve,250));
    }
    await guard();
    await paint();
    console.log(JSON.stringify(options.verbose==='true'?await evaluate(observation):await stateSummary(), null, 2));
  }
} finally {
  socket.close();
  for (const p of pending.values()) clearTimeout(p.timer);
}
