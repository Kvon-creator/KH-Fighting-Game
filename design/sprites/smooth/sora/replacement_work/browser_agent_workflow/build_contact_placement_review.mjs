// Review whole-frame display placement. Never modify sprite pixels or split layers.
import { createHash } from 'node:crypto';
import { copyFileSync, existsSync, mkdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = realpathSync(fileURLToPath(new URL('../../../../../../', import.meta.url)));
if (root.toLowerCase() !== String.raw`D:\KH Fighting Game`.toLowerCase()) throw new Error(`Unexpected workspace: ${root}`);
const base = path.join(root, 'design/sprites/smooth/sora/replacement_work/ready/run_start');
const source = path.join(base, 'sync_refinement_v1/timing_review_v1');
const out = path.join(base, 'sync_refinement_v2/contact_placement_review_v1');
if (existsSync(out)) throw new Error('Preserve existing review; choose a new version');
const digest = file => createHash('sha256').update(readFileSync(file)).digest('hex');
const previous = JSON.parse(readFileSync(path.join(source, 'manifest.json'), 'utf8'));
if (previous.frames.length !== 12) throw new Error('Expected the selected twelve drawings');
const original = path.join(base, 'direct_imagegen_trial/attempt_03/sora_run_start_original.png');
const originalHash = digest(original);
if (originalHash !== '6108be48aa93f736514c1860f1a9966de1998b0800814156c681321cb779530e') throw new Error('Original sheet changed');
const frames = previous.frames.map(frame => ({ ...frame,
  displayOffsetY: frame.index === 10 ? 8 : 0,
  phase: frame.index === 10 ? 'First contact candidate' : frame.phase,
  proposedBounds: frame.bounds.map((n, i) => n + (frame.index === 10 && i % 2 === 1 ? 8 : 0)),
}));
for (const frame of frames) {
  if (digest(path.join(source, frame.file)) !== frame.sha256) throw new Error(`Source frame${frame.index} changed`);
  const [x0, y0, x1, y1] = frame.proposedBounds;
  if (x0 < 8 || y0 < 8 || x1 > 504 || y1 > 504) throw new Error('Display placement would clip the whole figure');
}
mkdirSync(out, { recursive: true });
for (const frame of frames) {
  copyFileSync(path.join(source, frame.file), path.join(out, frame.file));
  if (digest(path.join(out, frame.file)) !== frame.sha256) throw new Error('Copied sprite changed');
}
let html = readFileSync(path.join(source, 'Review.html'), 'utf8');
const match = html.match(/<script>([\s\S]*?)<\/script>/);
if (!match) throw new Error('Existing review script not found');
let script = match[1];
const oldData = JSON.stringify(previous.frames, null, 0);
if (!script.includes(oldData)) throw new Error('Existing frame metadata changed');
script = script.replace(oldData, JSON.stringify(frames));
const oldShow = 'current=i;large.src=small.src=frames[i].file;scrub.value=i;';
if (!script.includes(oldShow)) throw new Error('Review display function changed');
script = script.replace(oldShow, `current=i;large.src=small.src=frames[i].file;
const offset=document.getElementById('placement').value==='proposed'?frames[i].displayOffsetY:0;
large.style.transform=small.style.transform='translateY('+(100*offset/512)+'%)';scrub.value=i;`);
script += `\ndocument.getElementById('placement').onchange=()=>show(current);
document.getElementById('floor').onchange=event=>document.querySelectorAll('.floor').forEach(line=>line.hidden=!event.target.checked);\n`;
html = html.replace(match[0], '<script src="Review.js"></script>');
html = html.replace('<title>Sora run-start review</title>', '<title>Sora first-contact placement review</title>');
html = html.replace('<h1>Sora: run start</h1>', '<h1>Sora: first-contact placement</h1>');
html = html.replace('12 complete poses. Play once, or scrub to compare the lift and first step.',
  'Compare the previous and proposed placement at frame10. The proposed first-contact pose meets the floor; the following flight pose keeps its clearance.');
html = html.replace('.sprite{', '.stage{');
html = html.replace('</style>', `.stage{position:relative;overflow:hidden}.stage-large{width:min(512px,100%);aspect-ratio:1}.stage-small{width:128px;height:128px}
.stage img{display:block;width:100%;height:100%}.floor{position:absolute;top:91.796875%;left:0;width:100%;height:1px;background:#9f6708;pointer-events:none}
</style>`);
html = html.replace('<label>Frame <input', '<label>Placement <select id="placement"><option value="proposed">Proposed</option><option value="previous">Previous</option></select></label><label><input id="floor" type="checkbox" checked> Floor guide</label><label>Frame <input');
html = html.replace('<img id="large" class="sprite large" width="512" height="512" alt="Sora run-start pose">',
  '<div class="stage stage-large"><img id="large" class="large" width="512" height="512" alt="Sora run-start pose"><div class="floor"></div></div>');
html = html.replace('<img id="small" class="sprite small" width="128" height="128" alt="Same complete pose at game export size">',
  '<div class="stage stage-small"><img id="small" class="small" width="128" height="128" alt="Same complete pose at game export size"><div class="floor"></div></div>');
html = html.replace('Artwork quality is retained. New intermediate drawings and consistent weapon projection are still needed at the larger gaps.',
  'This is a placement candidate. All12 drawings are unchanged. Missing intermediate poses and inconsistent weapon projection remain unresolved.');
writeFileSync(path.join(out, 'Review.html'), html);
writeFileSync(path.join(out, 'Review.js'), script);
writeFileSync(path.join(out, 'manifest.json'), JSON.stringify({
  status: 'first-contact placement candidate; no new drawings or retouched pixels',
  originalSha256: originalHash, frameCount: 12, frames,
  displayFloorY: 470, sequenceDurationMs: previous.sequenceDurationMs,
  geometry: 'Complete frame10 display translation +8px at512px (+2px at128px); all source PNG bytes preserved',
  interpretation: 'Review10 as first heel contact, then11 as flight. This is an art-phase proposal, not tested gameplay physics.',
  noIndividualLayers: true, newDrawingCount: 0,
  remainingGaps: previous.remainingGaps,
}, null, 2) + '\n');
writeFileSync(path.join(out, 'QA_NOTES.md'), `# First-contact placement candidate

## What changed

The previous registered frame10 has its lowest boot pixel at y462 on the512px canvas, eight pixels above the shared floor y470. This review proposes treating the extended leading boot as first heel contact: display the complete frame10 eight pixels lower. At128px that is a two-pixel shift. Both the entire body and connected weapon move together. Frame09 remains at y470; frame11 retains its y458 flight clearance.

This reduces the whole-figure upward jump into10 by eight pixels and separates contact from subsequent flight. It is a provisional art-phase interpretation. The source sheet requested precontact; a final running sequence still needs genuinely drawn contact/compression intermediates, not a claim that this adjustment repairs anatomy.

## What remains

All12 PNGs are exact copies of the previous registered review, with verified hashes. No pixels were painted, body/weapon layers made, new poses inserted or crossfades applied. The HTML applies only one whole-frame display offset. The floor guide is review UI, absent from sprite art. The original native sheet and earlier previews remain unchanged.

The full-image stride-midpoint attempt returned an output-stage content refusal. Exact tool arguments and error are in ../stride_midpoint_01/. No subsequent generation call was made in this pass. Early lift01-to02, overhead03-to04, carry settle05-to06, first step09-to10 and projected weapon consistency remain unresolved.

Offline checks establish preserved source/copy hashes, safe display bounds and12 frame records. Browser playback and Godot integration are untested. No final art/motion approval is claimed.
`);
if (digest(original) !== originalHash) throw new Error('Original changed during review packaging');
console.log(JSON.stringify({ review: out, completeDrawings: 12, pixelsRetouched: 0,
  frame10DisplayOffsetY: 8, previousFrame10Bounds: previous.frames[10].bounds,
  proposedFrame10Bounds: frames[10].proposedBounds, originalPreserved: true, copiesVerified: true }));
