// Offline control/link checks for the partial study. This does not test a browser.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {ROOT,projectPath} from './comfy_local.mjs';
export async function checkAdjacentReview(version='approved_style_sequence_v1'){
  if(!/^approved_style_sequence_v[0-9]+$/.test(version))throw new Error('Invalid review version');
  const folder=projectPath('design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial/'+version,true);
  const html=fs.readFileSync(path.join(folder,'Review.html'),'utf8');
  const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
  if(!script)throw new Error('Review script missing');
  const elements=Object.fromEntries(['play','previous','next','speed','scrub','status','original','refined'].map(id=>[id,{id,disabled:true,textContent:'',value:id==='speed'?'0.25':'0'}]));
  const timers=new Map();let serial=0;
  const context=vm.createContext({document:{getElementById:id=>elements[id]},Image:class{set src(value){this.onload?.();}},setTimeout:(callback,delay)=>{const id=++serial;timers.set(id,{callback,delay});return id;},clearTimeout:id=>timers.delete(id),Error,Promise});
  vm.runInContext(script,context);await Promise.resolve();await Promise.resolve();
  const evaluate=text=>vm.runInContext(text,context);
  const assert=(condition,message)=>{if(!condition)throw new Error(message);};
  assert(evaluate('ready')&&!elements.play.disabled,'Image preload did not enable playback');
  const sequence=JSON.parse(evaluate('JSON.stringify(sequence)'));
  assert(sequence.length===3&&evaluate('index')===0,'Unexpected initial study state');
  const assetPaths=[...sequence.flatMap(frame=>[frame.file,frame.original]),...Array.from(html.matchAll(/href="([^"]+)"/g),m=>m[1])];
  for(const asset of assetPaths){const file=path.resolve(folder,asset);assert(file.toLowerCase().startsWith(ROOT.toLowerCase()+path.sep)&&fs.statSync(file).isFile(),'Missing/outside-project review asset: '+asset);}
  elements.play.onclick();assert(evaluate('playing')&&evaluate('index')===0,'Play did not start at the first pose');
  const delays=[];let advances=0;
  while(timers.size){assert(++advances<=3,'Study unexpectedly repeats');const [id,timer]=timers.entries().next().value;timers.delete(id);delays.push(timer.delay);timer.callback();}
  assert(!evaluate('playing')&&evaluate('index')===2&&elements.status.textContent.includes('end of partial study'),'Playback did not hold the last pose');
  assert(delays.every(value=>value===320),'Slow timing differs from manifest');
  elements.previous.onclick();assert(evaluate('index')===1,'Previous did not step');
  elements.scrub.value='0';elements.scrub.oninput();assert(evaluate('index')===0&&!evaluate('playing'),'Scrub failed');
  elements.next.onclick();elements.next.onclick();elements.next.onclick();assert(evaluate('index')===2,'Next wrapped past the last pose');
  elements.speed.value='1';elements.play.onclick();assert([...timers.values()][0].delay===80,'Normal timing incorrect');
  elements.play.onclick();assert(!evaluate('playing')&&timers.size===0,'Pause did not cancel playback');
  const result={passed:true,frameCount:3,onceOnly:true,slowDelayMs:320,normalDelayMs:80,preloadAndAssets:true,playPauseStepScrub:true,loopWrapIntentionallyAbsent:true,actualBrowserTested:false,godotTested:false};
  const target=path.join(folder,'Viewer_QA.json');
  if(fs.existsSync(target))assert(fs.readFileSync(target,'utf8')===JSON.stringify(result,null,2)+'\n','Preserve existing viewer QA');else fs.writeFileSync(target,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
  return result;
}
