// Send one prompt to the public MoMask demo (Gradio 3.24 queue) and save the BVH + MP4 it returns.
// usage: node momask_client.mjs <outDir> <seconds> "<prompt>"
import fs from 'node:fs';
import path from 'node:path';

const HOST = 'meyourhint-momask.hf.space';
const [outDir, seconds, prompt] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const session = Math.random().toString(36).slice(2, 12);

let html = await new Promise((resolve, reject) => {
  const ws = new WebSocket(`wss://${HOST}/queue/join`);
  const timer = setTimeout(() => { ws.close(); reject(new Error('timeout')); }, 600000);
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.msg === 'send_hash') ws.send(JSON.stringify({ fn_index: 3, session_hash: session }));
    else if (m.msg === 'send_data') ws.send(JSON.stringify({ fn_index: 3, session_hash: session, event_data: null, data: [prompt, String(seconds), 'IK'] }));
    else if (m.msg === 'estimation') console.log('queue position', m.rank, 'eta', m.rank_eta);
    else if (m.msg === 'process_completed') {
      clearTimeout(timer); ws.close();
      if (!m.success) reject(new Error(JSON.stringify(m.output))); else resolve(m.output.data[0]);
    }
  };
  ws.onerror = (e) => { clearTimeout(timer); reject(new Error('websocket error ' + (e.message || ''))); };
});

fs.writeFileSync(path.join(outDir, 'response.json'), JSON.stringify(html, null, 2));
html = JSON.stringify(html);
const links = [...html.matchAll(/(?:src|href)=\\?"file\/([^"\\]+)\\?"/g)].map((x) => x[1]);
for (const link of links) {
  const name = path.basename(link);
  let res = await fetch(`https://${HOST}/file=${link}`);
  if (!res.ok) res = await fetch(`https://${HOST}/file/${link}`);
  if (!res.ok) { console.log('download failed', link, res.status); continue; }
  fs.writeFileSync(path.join(outDir, name), Buffer.from(await res.arrayBuffer()));
  console.log('saved', name);
}
fs.writeFileSync(path.join(outDir, 'prompt.json'), JSON.stringify({ prompt, seconds, postprocess: 'IK', space: 'MeYourHint/MoMask', when: new Date().toISOString() }, null, 2));
