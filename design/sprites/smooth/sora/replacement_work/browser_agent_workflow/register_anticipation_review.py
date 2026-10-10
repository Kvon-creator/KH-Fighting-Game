"""Register whole generated drawings to planted sole anchors for diagnosis.

This corrects image framing, never creates poses or alters individual anatomy/weapons.
The original unregistered sequence and all downloaded artwork are preserved.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[6]
if str(root).lower() != r"d:\kh fighting game":
    raise RuntimeError(f"Unexpected workspace: {root}")
trial = root / "design/sprites/smooth/sora/replacement_work/ready/run_start/gemini_browser_trial"
source = trial / "anticipation_review_v1"
out = trial / "registration_review_v1"
if out.exists():
    raise RuntimeError("Preserve this review; select a new version before another pass")
files = [source / f"frame_{index:02d}_review.png" for index in range(6)]
hashes = {file: hashlib.sha256(file.read_bytes()).hexdigest() for file in files}
frames = [Image.open(file).convert("RGB") for file in files]

def anchors(frame):
    pixels = np.asarray(frame)
    dark = pixels.min(axis=2) < 70
    result = []
    for left, right in [(20, 256), (256, 505)]:
        region = dark[350:505, left:right]
        ys, xs = np.where(region)
        if not len(ys):
            raise RuntimeError("Sole region not found; inspect image instead of guessing")
        bottom = int(ys.max()) + 350
        # Lower12px of the black sole, not the boot's upper/leg.
        ys, xs = np.where(dark[max(350, bottom - 11):bottom + 1, left:right])
        result.append([float(np.median(xs)) + left, float(bottom)])
    return result

target = anchors(frames[0])
target_span = target[1][0] - target[0][0]
registered, metadata = [], []
for index, frame in enumerate(frames):
    points = anchors(frame)
    span = points[1][0] - points[0][0]
    scale = target_span / span
    tx = target[0][0] - scale * points[0][0]
    ty = sum(point[1] for point in target) / 2 - scale * sum(point[1] for point in points) / 2
    residual = [scale * points[j][1] + ty - target[j][1] for j in range(2)]
    if not 0.8 <= scale <= 1.2 or max(abs(value) for value in residual) > 6:
        raise RuntimeError(f"Frame{index} requires an excessive framing correction; inspect before proceeding")
    registered.append(frame.transform((512, 512), Image.Transform.AFFINE,
                                     (1 / scale, 0, -tx / scale, 0, 1 / scale, -ty / scale),
                                     resample=Image.Resampling.BICUBIC, fillcolor="white"))
    metadata.append({"index": index, "sourceSoles": points, "uniformWholeDrawingScale": scale,
                     "translation": [tx, ty], "verticalSoleResidual": residual,
                     "source": files[index].relative_to(root).as_posix(), "sourceSha256": hashes[files[index]]})
out.mkdir()
contact = Image.new("RGB", (828, 596), (230, 232, 237))
draw = ImageDraw.Draw(contact)
for index, frame in enumerate(registered):
    row, column = divmod(index, 3)
    frame.save(out / f"frame_{index:02d}_review.png")
    contact.paste(frame.resize((256, 256), Image.Resampling.LANCZOS), (column * 276 + 10, row * 298 + 10))
    draw.text((column * 276 + 10, row * 298 + 272), f"{index:02d} / whole-frame registration", fill=(20, 25, 35))
contact.save(out / "Contact_Sheet.png")
for name, size, interval in [("Preview.gif", 512, 70), ("Preview_Slow.gif", 512, 240), ("Preview_128.gif", 128, 70)]:
    sequence = [frame.resize((size, size), Image.Resampling.LANCZOS) for frame in registered]
    strip = Image.new("RGB", (size * len(sequence), size))
    for index, frame in enumerate(sequence):
        strip.paste(frame, (index * size, 0))
    palette = strip.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    quantized = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in sequence]
    quantized[0].save(out / name, save_all=True, append_images=quantized[1:],
                      duration=[500] + [interval] * 4 + [650], loop=0, disposal=2, optimize=False)
(out / "manifest.json").write_text(json.dumps({"status": "diagnostic_not_approved_animation",
    "method": "single uniform scale+translation for each whole drawing from measured planted sole anchors",
    "limits": "Does not repair anatomy, change weapon design, produce in-betweens or prove fluidity. Do not use this on flight/toe-off frames.",
    "targetSoles": target, "finalUserApproval": "pending", "frames": metadata}, indent=2) + "\n", encoding="utf-8")
if any(hashlib.sha256(file.read_bytes()).hexdigest() != digest for file, digest in hashes.items()):
    raise RuntimeError("Review source changed")
print(json.dumps({"review": str(out), "sourceHashesUnchanged": True, "frames": metadata}))
