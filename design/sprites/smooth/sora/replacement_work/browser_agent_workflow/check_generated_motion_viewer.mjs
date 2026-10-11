// Read-only offline UI/asset checks. This is not an actual browser playback test.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const file=path.resolve(process.argv[2]);
assert.ok(file.toLowerCase().startsWith('d:\\kh fighting game\\'));
const html=fs.readFileSync(file,'utf8'),script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const elements=new Map();
for(const id of ['original','large','small','kind','scrub','label','play','pause','slow','previous','next','guide'])
  elements.set('#'+id,{value:id==='kind'?'run':0,checked:true,width:id==='small'?128:512,height:id==='small'?128:512,
    getContext:()=>({fillRect(){},drawImage(){},setLineDash(){},beginPath(){},moveTo(){},lineTo(){},stroke(){}})});
let timer=null,nextId=0;
const context=vm.createContext({document:{querySelector:id=>elements.get(id)},Image:class{complete=true;naturalWidth=512;},
  setTimeout(fn,delay){timer={fn,delay,id:++nextId};return nextId;},clearTimeout(id){if(timer&&timer.id===id)timer=null;}});
vm.runInContext(script,context);
const frames=vm.runInContext('[...run,...stop]',context);
assert.equal(frames.length,24);
for(const frame of frames)for(const key of ['file','original'])assert.ok(fs.existsSync(path.resolve(path.dirname(file),frame[key])),frame[key]);
for(const match of html.matchAll(/href="([^"]+)"/g))assert.ok(fs.existsSync(path.resolve(path.dirname(file),match[1])),match[1]);
function step(){assert.ok(timer);const pending=timer;timer=null;pending.fn();}
for(const [kind,length] of [['stop',12],['join',36]]){
  elements.get('#kind').value=kind;elements.get('#kind').onchange();elements.get('#play').onclick();
  for(let i=0;i<length;i++)step();
  assert.equal(timer,null);assert.equal(vm.runInContext('index',context),length-1);
}
elements.get('#kind').value='run';elements.get('#kind').onchange();elements.get('#play').onclick();
for(let i=0;i<12;i++)step();assert.equal(vm.runInContext('index',context),0);assert.ok(timer);
elements.get('#slow').onclick();assert.equal(timer.delay,240);assert.equal(vm.runInContext('index',context),0);
elements.get('#scrub').value=7;elements.get('#scrub').oninput();assert.equal(timer,null);
elements.get('#next').onclick();assert.equal(vm.runInContext('index',context),8);
elements.get('#previous').onclick();assert.equal(vm.runInContext('index',context),7);
elements.get('#guide').checked=false;elements.get('#guide').onchange();
console.log('Offline checks passed: 48 original/study frame links, review links, run wrap, one-pass stop and36-frame join, x3 timing, scrub/step and guide controls.');
