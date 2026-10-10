"""Package intact complete drawings for run-start pacing review, without layers."""
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[6]
if str(root).lower() != r"d:\kh fighting game":
    raise RuntimeError(f"Unexpected workspace: {root}")
base = root / "design/sprites/smooth/sora/replacement_work/ready/run_start"
source = base / "direct_imagegen_trial/whole_figure_review_v3"
out = base / "sync_refinement_v1/timing_review_v1"
if out.exists():
    raise RuntimeError("Preserve existing review; choose a new version")
durations = [100, 80, 80, 60, 70, 75, 75, 65, 65, 65, 55, 70]
phases = ["Ready", "Release near hand", "Early lift", "Upright lift",
          "Turn overhead", "Lower into carry", "Settle carry", "Prepare drive",
          "Forward lean", "Knee drive", "Leg reach", "First flight"]
frames, records = [], []
for i, (duration, phase) in enumerate(zip(durations, phases)):
    path = source / f"frame_{i:02d}.png"
    frame = Image.open(path).convert("RGBA")
    if frame.size != (512, 512) or frame.getchannel("A").getextrema() != (0, 255):
        raise RuntimeError(f"Frame {i} has an unexpected canvas or alpha")
    bounds = frame.getbbox()
    if bounds[0] < 8 or bounds[1] < 8 or bounds[2] > 504 or bounds[3] > 504:
        raise RuntimeError(f"Frame {i} would be clipped")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    frames.append(frame)
    records.append({"index": i, "phase": phase, "durationMs": duration,
                    "source": path.relative_to(root).as_posix(), "sha256": digest,
                    "file": f"frame_{i:02d}.png", "bounds": list(bounds)})
if len({record["sha256"] for record in records}) != 12:
    raise RuntimeError("Duplicate drawings are not valid new motion")
original = base / "direct_imagegen_trial/attempt_03/sora_run_start_original.png"
original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
if original_hash != "6108be48aa93f736514c1860f1a9966de1998b0800814156c681321cb779530e":
    raise RuntimeError("Selected original changed")
out.mkdir()
for record in records:
    shutil.copyfile(root / record["source"], out / record["file"])
    if hashlib.sha256((out / record["file"]).read_bytes()).hexdigest() != record["sha256"]:
        raise RuntimeError("Whole-frame copy changed")
sheet = Image.new("RGBA", (2048, 1536))
for i, frame in enumerate(frames):
    sheet.alpha_composite(frame, ((i % 4) * 512, (i // 4) * 512))
sheet.save(out / "Sprite_Sheet.png")
for name, size, slow in [("Run_Start_Once.gif", 512, 1),
                         ("Run_Start_Slow_Once.gif", 512, 3),
                         ("Run_Start_128_Once.gif", 128, 1)]:
    flat = []
    for frame in frames:
        canvas = Image.new("RGBA", frame.size, "white")
        canvas.alpha_composite(frame)
        flat.append(canvas.convert("RGB").resize((size, size), Image.Resampling.LANCZOS))
    strip = Image.new("RGB", (size * len(flat), size))
    for i, frame in enumerate(flat):
        strip.paste(frame, (i * size, 0))
    palette = strip.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in flat]
    # No loop extension: run-start is a transition, not a cycle back to idle.
    indexed[0].save(out / name, save_all=True, append_images=indexed[1:],
                    duration=[duration * slow for duration in durations],
                    disposal=2, optimize=False)
    with Image.open(out / name) as check:
        if check.n_frames != 12 or "loop" in check.info:
            raise RuntimeError("Unexpected GIF frame count or looping")

pair_board = Image.new("RGB", (792, 1116), (231, 234, 240))
draw = ImageDraw.Draw(pair_board)
for row, pair in enumerate([(1, 2), (3, 4), (5, 6), (9, 10)]):
    for col, i in enumerate(pair):
        canvas = Image.new("RGBA", (512, 512), "white")
        canvas.alpha_composite(frames[i])
        pair_board.paste(canvas.convert("RGB").resize((256, 256)), (col * 396, row * 279))
        draw.text((col * 396 + 6, row * 279 + 258), f"{i:02d}: {phases[i]}", fill=(20, 25, 35))
    draw.text((265, row * 279 + 122), "missing", fill=(70, 75, 90))
    draw.text((265, row * 279 + 137), "midpoint", fill=(70, 75, 90))
pair_board.save(out / "Remaining_Gaps.png")
manifest = {"status": "whole-drawing pacing review; pose/weapon gaps unresolved",
            "originalSha256": original_hash, "frameCount": 12,
            "sequenceDurationMs": sum(durations), "onePassHoldFinal": True,
            "noIndividualLayers": True, "noNewDrawings": True,
            "geometry": "Identical complete PNG bytes to registered review_v3",
            "timing": "Provisional display pacing; GIF rounds to 10ms, HTML uses specified times",
            "remainingGaps": [[1, 2], [3, 4], [5, 6], [9, 10]], "frames": records}
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
data = json.dumps(records, separators=(",", ":"))
html = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sora run-start review</title>
<style>
body{margin:0;background:#151923;color:#edf0f7;font:16px system-ui,sans-serif}
main{max-width:1000px;margin:0 auto;padding:24px}h1{font-size:25px;margin:0 0 8px}
p{color:#b9c1d4;line-height:1.5}.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:18px 0}
button,select{background:#2b354c;color:inherit;border:1px solid #53607b;border-radius:7px;padding:10px 15px}
button{cursor:pointer}button:focus-visible,input:focus-visible{outline:3px solid #ffd666}
.views{display:flex;gap:24px;align-items:flex-end;flex-wrap:wrap}
.sprite{background-color:#d4d7dc;background-image:conic-gradient(#eee 25%,transparent 0 50%,#eee 0 75%,transparent 0);background-size:32px 32px;border-radius:8px}
.large{width:min(512px,100%);height:auto}.small{width:128px;height:128px}
.thumbs{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-top:20px}.thumbs button{padding:2px;min-width:0}
.thumbs img{display:block;width:100%;height:auto}.thumbs button[aria-pressed=true]{border:3px solid #ffd666}
input[type=range]{width:min(400px,90vw)}output{min-width:220px}.caption{font-size:13px;margin:5px 0}
@media(max-width:600px){main{padding:12px}.thumbs{grid-template-columns:repeat(4,1fr)}}
</style>
<main><h1>Sora: run start</h1><p>12 complete poses. Play once, or scrub to compare the lift and first step.</p>
<div class="controls"><button id="play">Play once</button><button id="pause">Pause</button>
<label>Speed <select id="speed"><option value="1">Normal</option><option value="3">Slow</option></select></label>
<label>Frame <input id="scrub" type="range" min="0" max="11" value="0"></label><output id="readout"></output></div>
<div class="views"><div><img id="large" class="sprite large" width="512" height="512" alt="Sora run-start pose"><p class="caption">Working canvas</p></div>
<div><img id="small" class="sprite small" width="128" height="128" alt="Same complete pose at game export size"><p class="caption">128 px preview</p></div></div>
<div id="thumbs" class="thumbs"></div><p>Artwork quality is retained. New intermediate drawings and consistent weapon projection are still needed at the larger gaps.</p></main>
<script>
const frames=__FRAME_DATA__;
const large=document.getElementById('large'),small=document.getElementById('small'),scrub=document.getElementById('scrub'),readout=document.getElementById('readout');
let current=0,timer=null,runToken=0;
const preload=frames.map(f=>{const image=new Image();image.src=f.file;return image;});
const buttons=frames.map((f,i)=>{const button=document.createElement('button');button.type='button';button.title=f.phase;button.setAttribute('aria-label',`Frame ${i}: ${f.phase}`);button.innerHTML=`<img src="${f.file}" alt=""><span>${String(i).padStart(2,'0')}</span>`;button.onclick=()=>{stop();show(i);};document.getElementById('thumbs').append(button);return button;});
function show(i){current=i;large.src=small.src=frames[i].file;scrub.value=i;readout.textContent=`${String(i).padStart(2,'0')} / ${frames[i].phase}`;buttons.forEach((b,j)=>b.setAttribute('aria-pressed',String(i===j)));}
function stop(){runToken++;clearTimeout(timer);timer=null;}
function schedule(token){if(token!==runToken)return;timer=setTimeout(()=>{if(token!==runToken)return;if(current===frames.length-1){timer=null;return;}show(current+1);schedule(token);},frames[current].durationMs*Number(document.getElementById('speed').value));}
document.getElementById('play').onclick=async()=>{stop();const token=runToken;await Promise.all(preload.map(im=>im.decode()));if(token!==runToken)return;show(0);schedule(token);};
document.getElementById('pause').onclick=stop;scrub.oninput=()=>{stop();show(Number(scrub.value));};show(0);
</script></html>'''
(out / "Review.html").write_text(html.replace("__FRAME_DATA__", data), encoding="utf-8")
(out / "QA_NOTES.md").write_text("""# Complete-drawing run-start review

The selected twelve-pose art remains the source. Every PNG is an exact copy of the registered whole-figure v3 export; the original sheet is unchanged. There are no body/weapon layers, replacement poses, morphs, crossfades, mirrored stride substitutes or synthesized frames.

The preview uses provisional per-pose durations and holds the last drawing. Run start does not loop directly from flight back to idle. The interactive review shows the same frame at working size and128px, with frame selection and slower playback.

This improves review pacing, not drawing continuity. Early lift01-to02, overhead turn03-to04, carry settle05-to06 and knee-drive09-to10 still need genuine intermediate poses. Guard/profile and projected blade length vary across source poses; correct those with complete-image edits when an authorized generation route is available. Inspect both arms, grip orientation, attached chain, straight connected shaft, same far-arm shoulder carry and slight foreground tip on every new drawing. Reject candidates whose wrist/feet/head do not lie coherently between their neighbors.

The four midpoint candidates are excluded because their wrists are too high. The latest targeted generation returned an output-stage content refusal; exact request/error are stored in ../inbetweens_trial/attempt_03/. No further generation call or layer fallback was made in this pass.

Verified offline: all12 RGBA inputs, safe margins, distinct whole-frame hashes, byte-identical copied PNGs, original source hash,12 GIF frames and no GIF loop extension. Browser playback and Godot integration have not been tested. Timing is provisional; no final animation approval is claimed.
""", encoding="utf-8")
if hashlib.sha256(original.read_bytes()).hexdigest() != original_hash:
    raise RuntimeError("Original changed during packaging")
print(json.dumps({"review": str(out), "completePoses": 12, "durationMs": sum(durations),
                  "newDrawings": 0, "sourcePreserved": True, "copiesVerified": True}))
