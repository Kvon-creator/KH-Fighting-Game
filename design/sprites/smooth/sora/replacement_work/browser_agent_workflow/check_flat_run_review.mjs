// Offline preview logic checks. Does not claim real browser or Godot playback.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const htmlPath=path.resolve(process.argv[2]);
assert.ok(htmlPath.toLowerCase().startsWith('d:\\kh fighting game\\'));
const script=fs.readFileSync(htmlPath,'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const elements=new Map();
const draws=[];
for(const id of ['large','small','kind','scrub','label','play','join','pause','slow']){
  elements.set('#'+id,{value:id==='kind'?'run':0,width:id==='large'?512:128,height:id==='large'?512:128,
    getContext:()=>({fillRect(){},drawImage(img){draws.push(img.src);}})});
}
let timer=null,nextId=0;
const context=vm.createContext({
  document:{querySelector:id=>elements.get(id)},
  Image:class {complete=true;naturalWidth=512;},
  setTimeout(fn,delay){timer={fn,delay,id:++nextId};return nextId;},
  clearTimeout(id){if(timer&&timer.id===id)timer=null;},
});
vm.runInContext(script,context);
for(const frame of vm.runInContext('[...run,...stop]',context)){
  assert.ok(fs.existsSync(path.resolve(path.dirname(htmlPath),frame.file)),frame.file);
}
function step(){const pending=timer;assert.ok(pending);timer=null;pending.fn();}
elements.get('#kind').value='stop';elements.get('#kind').onchange();
elements.get('#play').onclick();
for(let i=0;i<16;i++)step();
assert.equal(timer,null);assert.match(elements.get('#label').textContent,/15.*ready hold/);
elements.get('#kind').value='run';elements.get('#kind').onchange();elements.get('#play').onclick();
for(let i=0;i<16;i++)step();
assert.match(elements.get('#label').textContent,/00.*near contact/);
elements.get('#pause').onclick();assert.equal(timer,null);
elements.get('#join').onclick();for(let i=0;i<48;i++)step();
assert.equal(timer,null);assert.match(elements.get('#label').textContent,/15.*ready hold/);
elements.get('#kind').value='run';elements.get('#kind').onchange();
elements.get('#slow').onclick();elements.get('#play').onclick();assert.equal(timer.delay,180);
elements.get('#scrub').value=8;elements.get('#scrub').oninput();assert.equal(timer,null);
assert.match(elements.get('#label').textContent,/08.*far contact/);
console.log('Preview syntax, local asset links, loop wrapping, one-pass stop, 48-frame join, pause, slow timing and scrubbing passed in an offline JavaScript harness.');
