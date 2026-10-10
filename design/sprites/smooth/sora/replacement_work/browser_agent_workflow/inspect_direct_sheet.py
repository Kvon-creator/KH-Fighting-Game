"""Extract an inspected direct-tool grid for diagnosis, preserving native alpha."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument("attempt", type=int, choices=(1, 2, 3))
parser.add_argument("--rows", type=int, choices=(2, 3), required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[6]
if str(root).lower() != r"d:\kh fighting game":
    raise RuntimeError(f"Unexpected workspace: {root}")
directory = root / f"design/sprites/smooth/sora/replacement_work/ready/run_start/direct_imagegen_trial/attempt_{args.attempt:02d}"
source = directory / "sora_run_start_original.png"
out = directory / "grid_review_v1"
if out.exists():
    raise RuntimeError("Preserve the existing review")
before = hashlib.sha256(source.read_bytes()).hexdigest()
native = Image.open(source)
if "A" not in native.getbands():
    raise RuntimeError("No native alpha; do not label transparent")
sheet = native.convert("RGBA")
w, h = sheet.size
if abs(w / 4 - h / args.rows) > 2:
    raise RuntimeError("Requested equal-square-cell layout not present")
out.mkdir()
frames, records = [], []
board = Image.new("RGB", (4 * 266, args.rows * 286), (230, 232, 237))
draw = ImageDraw.Draw(board)
for index in range(4 * args.rows):
    row, col = divmod(index, 4)
    box = (round(col * w / 4), round(row * h / args.rows), round((col + 1) * w / 4), round((row + 1) * h / args.rows))
    frame = sheet.crop(box).resize((512, 512), Image.Resampling.LANCZOS)
    alpha = np.asarray(frame.getchannel("A"))
    edge = bool((alpha[:3] > 32).any() or (alpha[-3:] > 32).any() or (alpha[:, :3] > 32).any() or (alpha[:, -3:] > 32).any())
    frame.save(out / f"frame_{index:02d}.png")
    white = Image.new("RGBA", frame.size, "white")
    white.alpha_composite(frame)
    white = white.convert("RGB")
    frames.append(white)
    board.paste(white.resize((256, 256), Image.Resampling.LANCZOS), (col * 266 + 5, row * 286 + 5))
    draw.text((col * 266 + 5, row * 286 + 263), f"{index:02d} / {'EDGE RISK' if edge else 'draft'}", fill=(25, 30, 40))
    records.append({"index": index, "nativeCrop": list(box), "file": f"frame_{index:02d}.png", "edgeRisk": edge,
                    "pixelSha256": hashlib.sha256(frame.tobytes()).hexdigest()})
board.save(out / "Contact_Sheet.png")
for name, size, duration in [("Preview.gif", 512, 70), ("Preview_Slow.gif", 512, 210), ("Preview_128.gif", 128, 70)]:
    sequence = [frame.resize((size, size), Image.Resampling.LANCZOS) for frame in frames]
    strip = Image.new("RGB", (size * len(sequence), size))
    for index, frame in enumerate(sequence):
        strip.paste(frame, (index * size, 0))
    palette = strip.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    sequence = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in sequence]
    sequence[0].save(out / name, save_all=True, append_images=sequence[1:], duration=duration, loop=0, disposal=2, optimize=False)
manifest = {"status": "diagnostic_not_approved", "sourceSha256": before, "nativeSize": [w, h], "grid": [4, args.rows],
            "nativeAlphaExtrema": list(sheet.getchannel("A").getextrema()), "workingSize": [512, 512],
            "method": "equal whole-cell crop/resize; no pose fitting or generated intermediates", "frames": records}
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
if hashlib.sha256(source.read_bytes()).hexdigest() != before:
    raise RuntimeError("Original changed")
print(json.dumps({"attempt": args.attempt, "nativeSize": [w, h], "alpha": manifest["nativeAlphaExtrema"],
                  "frames": len(frames), "edgeRiskFrames": [r["index"] for r in records if r["edgeRisk"]], "sourcePreserved": True}))
