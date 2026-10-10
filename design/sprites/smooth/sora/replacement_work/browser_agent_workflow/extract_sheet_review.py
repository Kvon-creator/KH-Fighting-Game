"""Extract an inspected equal-cell sheet into opaque draft frames and review GIFs.

This is whole-frame extraction/export, not pose creation or separate body/weapon layers.
Call only after visually confirming the actual grid. Originals remain unchanged.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument("attempt")
parser.add_argument("--columns", type=int, required=True)
parser.add_argument("--rows", type=int, required=True)
parser.add_argument("--duration", type=int, default=80)
parser.add_argument("--start-index", type=int, default=0)
parser.add_argument("--grid-confirmed", action="store_true", required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[6]
if str(root).lower() != r"d:\kh fighting game":
    raise RuntimeError(f"Unexpected workspace: {root}")
attempt = (root / args.attempt).resolve()
relative = attempt.relative_to(root).as_posix()
if not re.fullmatch(r"design/sprites/smooth/sora/replacement_work/ready/(run_start|run_loop|run_stop)/gemini_browser_trial/attempt_\d+", relative):
    raise RuntimeError("Only a preserved running candidate directory is allowed")
if not (1 <= args.columns <= 4 and 1 <= args.rows <= 4 and 20 <= args.duration <= 250 and 0 <= args.start_index <= 32):
    raise RuntimeError("Invalid grid or provisional timing")
job = json.loads((attempt / "exchange_state.json").read_text(encoding="utf-8"))
source = Path(job.get("originalDownload") or job["preview"]).resolve()
if source.parent != attempt:
    raise RuntimeError("Image must belong to this candidate directory")
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
sheet = Image.open(source).convert("RGB")
width, height = sheet.size
if abs(width / args.columns - height / args.rows) > 2:
    raise RuntimeError("Inspected grid cells are not square; choose the actual layout")
out = attempt / "frame_review_v1"
manifest_path = out / "manifest.json"
if manifest_path.exists():
    raise RuntimeError("Preserve the existing review; choose a new candidate for another sheet")
out.mkdir(exist_ok=True)
frames, metadata = [], []
animation = attempt.parent.parent.name
contact = Image.new("RGB", (args.columns * 276, args.rows * 298), (230, 232, 237))
draw = ImageDraw.Draw(contact)
for index in range(args.columns * args.rows):
    frame_index = args.start_index + index
    row, column = divmod(index, args.columns)
    box = (round(column * width / args.columns), round(row * height / args.rows),
           round((column + 1) * width / args.columns), round((row + 1) * height / args.rows))
    native = sheet.crop(box)
    frame = native.resize((512, 512), Image.Resampling.LANCZOS)
    # The same whole-cell export ratio is used for every frame. Never fit body parts.
    pixels = np.asarray(frame)
    foreground = pixels.min(axis=2) < 220
    ys, xs = np.where(foreground)
    bounds = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(xs) else None
    edge = bool(foreground[:3].any() or foreground[-3:].any() or foreground[:, :3].any() or foreground[:, -3:].any())
    name = f"sora_{animation}_{frame_index:02d}.png"
    frame.save(out / name)
    frames.append(frame)
    metadata.append({"frame": frame_index, "file": name, "nativeCrop": list(box),
                     "opaqueRGB": True, "darkPixelBounds": bounds, "edgeRisk": edge,
                     "pixelSha256": hashlib.sha256(frame.tobytes()).hexdigest()})
    contact.paste(frame.resize((256, 256), Image.Resampling.LANCZOS), (column * 276 + 10, row * 298 + 10))
    draw.text((column * 276 + 10, row * 298 + 272), f"{frame_index:02d} - provisional", fill=(20, 25, 35))
contact.save(out / "Contact_Sheet.png")
for name, size, duration in [("Preview.gif", 512, args.duration), ("Preview_Slow.gif", 512, args.duration * 2), ("Preview_128.gif", 128, args.duration)]:
    review_frames = [frame.resize((size, size), Image.Resampling.LANCZOS) for frame in frames]
    review_frames[0].save(out / name, save_all=True, append_images=review_frames[1:],
                          duration=duration, loop=0, disposal=2)
manifest = {"status": "draft_for_visual_review", "source": source.name,
            "sourceSha256": source_hash, "nativeSheetSize": [width, height],
            "grid": [args.columns, args.rows], "frameCount": len(frames),
            "workingCanvas": [512, 512], "gameReviewCanvas": [128, 128],
            "background": "opaque white; transparency export pending",
            "provisionalDurationMs": args.duration, "finalUserApproval": "pending",
            "frames": metadata}
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
if hashlib.sha256(source.read_bytes()).hexdigest() != source_hash:
    raise RuntimeError("Source changed during extraction")
print(json.dumps({"reviewDirectory": str(out), "frames": len(frames),
                  "distinctPixelHashes": len({frame["pixelSha256"] for frame in metadata}),
                  "edgeRiskFrames": [frame["frame"] for frame in metadata if frame["edgeRisk"]],
                  "sourcePreserved": True, "status": "draft_for_visual_review"}))
