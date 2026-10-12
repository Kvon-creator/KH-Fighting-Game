// Read-only offline control and asset checks, not actual browser playback.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const file=path.resolve(process.argv[2]);
assert.ok(file.toLowerCase().startsWith('d:\\kh fighting game\\'));
const html=fs.readFileSync(file,'utf8'),script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const elements=new Map();
for(const id of ['original','large','small','kind','scrub','label','play','pause','slow','previous','next','guide','comparisonCaption'])
  elements.set('#'+id,{value:id==='kind'?'arm':0,checked:true,width:id==='small'?128:512,height:id==='small'?128:512,
    getContext:()=>({fillRect(){},drawImage(){},setLineDash(){},beginPath(){},moveTo(){},lineTo(){},stroke(){}})});
let timer=null,nextId=0;
const context=vm.createContext({document:{querySelector:id=>elements.get(id)},Image:class{complete=true;naturalWidth=512;},
  setTimeout(fn,delay){timer={fn,delay,id:++nextId};return nextId;},clearTimeout(id){if(timer&&timer.id===id)timer=null;}});
vm.runInContext(script,context);
const frames=vm.runInContext('frames',context);
assert.equal(frames.length,16);
for(const f of frames)for(const key of ['file','game','original','arm','gait']){
  const asset=path.resolve(path.dirname(file),f[key]);
  assert.ok(asset.toLowerCase().startsWith('d:\\kh fighting game\\'));
  assert.ok(fs.existsSync(asset),asset);
}
for(const m of html.matchAll(/href="([^"]+)"/g))assert.ok(fs.existsSync(path.resolve(path.dirname(file),m[1])),m[1]);
function step(){assert.ok(timer);const pending=timer;timer=null;pending.fn();}
elements.get('#play').onclick();
let elapsed=0;
for(let i=0;i<16;i++){assert.equal(timer.delay,frames[i].durationMs);elapsed+=timer.delay;step();}
assert.equal(elapsed,960);assert.equal(vm.runInContext('index',context),0);assert.ok(timer);
elements.get('#slow').onclick();assert.equal(timer.delay,240);
elements.get('#scrub').value=3;elements.get('#scrub').oninput();assert.equal(timer,null);
elements.get('#play').onclick();assert.equal(timer.delay,120);
elements.get('#pause').onclick();assert.equal(timer,null);
elements.get('#next').onclick();assert.equal(vm.runInContext('index',context),4);
elements.get('#previous').onclick();assert.equal(vm.runInContext('index',context),3);
for(const kind of ['arm','original','gait']){elements.get('#kind').value=kind;elements.get('#kind').onchange();assert.equal(vm.runInContext('index',context),3);}
elements.get('#guide').checked=false;elements.get('#guide').onchange();
console.log('Offline checks passed: 80 frame/export/comparison links, review links, 16-frame wrap, 960ms timing, x3 speed, scrub/step/pause, comparison and floor controls.');
