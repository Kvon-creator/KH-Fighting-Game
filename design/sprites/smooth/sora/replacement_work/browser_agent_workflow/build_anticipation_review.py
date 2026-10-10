"""Review approved idle, four complete in-betweens, and anticipation endpoint.

Uniform canvas export only: no fitting, interpolation, pose layers or alignment.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument("--middle-attempt")
parser.add_argument("--adjacent-attempt")
parser.add_argument("--end-attempt", default="attempt_08")
parser.add_argument("--review", required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[6]
if str(root).lower() != r"d:\kh fighting game":
    raise RuntimeError(f"Unexpected workspace: {root}")
trial = root / "design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial"
if bool(args.middle_attempt) == bool(args.adjacent_attempt):
    raise RuntimeError("Choose either a four-frame bridge or one adjacent-frame comparison")
for name in (args.middle_attempt or args.adjacent_attempt, args.end_attempt):
    if not re.fullmatch(r"attempt_\d+", name):
        raise RuntimeError("Use a preserved run-start attempt name")
if not re.fullmatch(r"(?:anticipation|adjacent)_review_v\d+", args.review):
    raise RuntimeError("Use a separate numbered anticipation review")
out = trial / args.review
if out.exists():
    raise RuntimeError("Preserve the existing review; choose a new version")
idle = root / "design/sprites/smooth/sora/replacement_work/ready/standing_idle/sora_stand_idle_00.png"
middle_sources = []
if args.middle_attempt:
    middle = trial / args.middle_attempt / "frame_review_v1"
    grid = json.loads((middle / "manifest.json").read_text(encoding="utf-8"))
    if grid["grid"] != [2, 2] or grid["frameCount"] != 4:
        raise RuntimeError("Inspect and extract the actual four-cell layout first")
    middle_sources = [middle / frame["file"] for frame in grid["frames"]]
endpoint_attempt = args.adjacent_attempt or args.end_attempt
job = json.loads((trial / endpoint_attempt / "exchange_state.json").read_text(encoding="utf-8"))
end = Path(job.get("originalDownload") or job["preview"]).resolve()
if end.parent != trial / endpoint_attempt:
    raise RuntimeError("Endpoint image must belong to its preserved attempt")
sources = [idle] + middle_sources + [end]
before = {file: hashlib.sha256(file.read_bytes()).hexdigest() for file in sources}
if before[idle] != "baf8959c0e0d42b74bf7f6100a83ccf5c208a9decd5b98b95110f3129fbacdc7":
    raise RuntimeError("Approved idle changed")
frames, metadata = [], []
for index, file in enumerate(sources):
    with Image.open(file) as source:
        native_size = source.size
        if native_size[0] != native_size[1]:
            raise RuntimeError("Square whole-frame canvases required; do not stretch")
        rgba = source.convert("RGBA")
        rgb = Image.new("RGBA", rgba.size, "white")
        rgb.alpha_composite(rgba)
        frame = rgb.convert("RGB").resize((512, 512), Image.Resampling.LANCZOS)
    frames.append(frame)
    foreground = np.asarray(frame).min(axis=2) < 220
    edge = bool(foreground[:3].any() or foreground[-3:].any() or foreground[:, :3].any() or foreground[:, -3:].any())
    metadata.append({"index": index, "role": "approved_idle_reference" if index == 0 else "generated_adjacent_candidate" if args.adjacent_attempt else "provisional_endpoint" if index == len(sources)-1 else "generated_inbetween",
                     "source": file.relative_to(root).as_posix(), "sourceSha256": before[file],
                     "nativeSize": list(native_size), "wholeCanvasRatio": 512 / native_size[0],
                     "edgeRisk": edge})
out.mkdir()
columns = min(3, len(frames))
rows = (len(frames) + columns - 1) // columns
contact = Image.new("RGB", (columns * 276, rows * 298), (230, 232, 237))
draw = ImageDraw.Draw(contact)
for index, frame in enumerate(frames):
    row, column = divmod(index, columns)
    frame.save(out / f"frame_{index:02d}_review.png")
    contact.paste(frame.resize((256, 256), Image.Resampling.LANCZOS), (column * 276 + 10, row * 298 + 10))
    draw.text((column * 276 + 10, row * 298 + 272), f"{index:02d} / {metadata[index]['role']}", fill=(20, 25, 35))
contact.save(out / "Contact_Sheet.png")
for name, size, interval in [("Preview.gif", 512, 70), ("Preview_Slow.gif", 512, 240), ("Preview_128.gif", 128, 70)]:
    sequence = [frame.resize((size, size), Image.Resampling.LANCZOS) for frame in frames]
    # One common palette reduces GIF color flicker without modifying pose drawings.
    strip = Image.new("RGB", (size * len(sequence), size))
    for index, frame in enumerate(sequence):
        strip.paste(frame, (index * size, 0))
    palette = strip.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    quantized = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in sequence]
    durations = ([350 if interval == 70 else 700] * 2 if args.adjacent_attempt
                 else [500] + [interval] * (len(sequence) - 2) + [650])
    quantized[0].save(out / name, save_all=True, append_images=quantized[1:],
                      duration=durations, loop=0, disposal=2, optimize=False)
manifest = {"status": "diagnostic_not_approved_animation", "scope": "adjacent-pose comparison; not a running cycle" if args.adjacent_attempt else "idle-to-anticipation only; not a running cycle",
            "canvas": [512, 512], "background": "white review composite; native originals preserved",
            "transforms": "uniform whole-canvas export only; no per-pose fitting, registration correction or morphing",
            "timing": "comparison flashes350ms normal/700ms slow; not animation timing" if args.adjacent_attempt else "provisional70ms intermediates; endpoint holds and visible reset for inspection",
            "finalUserApproval": "pending", "frames": metadata}
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
for file, digest in before.items():
    if hashlib.sha256(file.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f"Source changed: {file}")
print(json.dumps({"review": str(out), "frames": len(frames), "sourceHashesUnchanged": True,
                  "edgeRiskFrames": [item["index"] for item in metadata if item["edgeRisk"]],
                  "status": manifest["status"]}))
