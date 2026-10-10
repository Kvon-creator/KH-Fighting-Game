"""Separate full sprites by alpha connectivity; never split body/weapon layers.

The direct tool's tightly packed sheet does not obey equal-cell crop boundaries.
Every native original stays intact. These are whole-figure review exports.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

root = Path(__file__).resolve().parents[6]
if str(root).lower() != r"d:\kh fighting game":
    raise RuntimeError(f"Unexpected workspace: {root}")
trial = root / "design/sprites/smooth/sora/replacement_work/ready/run_start/direct_imagegen_trial"
source = trial / "attempt_03/sora_run_start_original.png"
out = trial / "whole_figure_review_v3"
if out.exists():
    raise RuntimeError("Preserve this review; choose a new version")
sha = hashlib.sha256(source.read_bytes()).hexdigest()
sheet = Image.open(source).convert("RGBA")
rgba = np.asarray(sheet)
occupied = rgba[:, :, 3] > 16
height, width = occupied.shape
parent, runs, previous = [], [], []

def find(value):
    while parent[value] != value:
        parent[value] = parent[parent[value]]
        value = parent[value]
    return value

def union(a, b):
    a, b = find(a), find(b)
    if a != b:
        parent[max(a, b)] = min(a, b)

for y in range(height):
    row = np.pad(occupied[y].astype(np.int8), (1, 1))
    transitions = np.diff(row)
    starts, ends = np.where(transitions == 1)[0], np.where(transitions == -1)[0]
    current = []
    first = 0
    for left, right in zip(starts, ends):
        label = len(parent)
        parent.append(label)
        current.append((int(left), int(right), label))
        runs.append((y, int(left), int(right), label))
        while first < len(previous) and previous[first][1] < left:
            first += 1
        j = first
        while j < len(previous) and previous[j][0] <= right:
            union(label, previous[j][2])
            j += 1
    previous = current
groups = {}
for y, left, right, label in runs:
    label = find(label)
    component = groups.setdefault(label, {"area": 0, "bounds": [width, height, 0, 0], "runs": []})
    component["area"] += right - left
    component["bounds"] = [min(component["bounds"][0], left), min(component["bounds"][1], y),
                           max(component["bounds"][2], right), max(component["bounds"][3], y + 1)]
    component["runs"].append((y, left, right))
main = sorted(groups.values(), key=lambda component: component["area"], reverse=True)[:12]
if len(main) != 12 or min(component["area"] for component in main) < 7000:
    raise RuntimeError("Twelve full-body components not established; inspect instead of guessing")
cells = {}
for component in main:
    x0, y0, x1, y1 = component["bounds"]
    # The torso/feet mass stays inside its nominal cell even when blade/soles cross it.
    count = sum(right - left for y, left, right in component["runs"])
    cx = sum((left + right - 1) / 2 * (right - left) for y, left, right in component["runs"]) / count
    cy = sum(y * (right - left) for y, left, right in component["runs"]) / count
    col, row = min(3, int(cx * 4 / width)), min(2, int(cy * 3 / height))
    index = row * 4 + col
    if index in cells:
        raise RuntimeError(f"Ambiguous figure assignment to cell{index}")
    component["center"] = [cx, cy]
    component["index"] = index
    cells[index] = component
if sorted(cells) != list(range(12)):
    raise RuntimeError("One full figure per cell was not established")
main_ids = {id(component) for component in main}
for component in groups.values():
    if id(component) in main_ids:
        continue
    a, b, c, d = component["bounds"]
    cx, cy = (a + c) / 2, (b + d) / 2
    def distance(body):
        x0, y0, x1, y1 = body["bounds"]
        box_gap = max(x0 - cx, 0, cx - x1) ** 2 + max(y0 - cy, 0, cy - y1) ** 2
        center_gap = (cx - body["center"][0]) ** 2 + (cy - body["center"][1]) ** 2
        return box_gap + center_gap * .015
    owner = min(main, key=distance)
    owner["runs"].extend(component["runs"])
    owner["bounds"] = [min(owner["bounds"][0], a), min(owner["bounds"][1], b),
                       max(owner["bounds"][2], c), max(owner["bounds"][3], d)]
figures, metadata = [], []
for index in range(12):
    component = cells[index]
    mask = Image.new("L", sheet.size)
    draw = ImageDraw.Draw(mask)
    for y, left, right in component["runs"]:
        draw.line((left, y, right - 1, y), fill=255)
    mask = mask.filter(ImageFilter.MaxFilter(3))
    pixels = rgba.copy()
    pixels[:, :, 3] = np.where(np.asarray(mask) > 0, rgba[:, :, 3], 0)
    figure = Image.fromarray(pixels, "RGBA")
    bounds = figure.getbbox()
    figure = figure.crop(bounds)
    figures.append(figure)
    metadata.append({"index": index, "nativeBounds": list(bounds), "nativeFigureSize": list(figure.size),
                     "method": "complete connected figure plus nearest detached detail components; antialias margin1px"})
# One identical export ratio for every genuine drawing, never per-pose size fitting.
ratio = min(476 / (max(figure.width for figure in figures) + 2),
            454 / (max(figure.height for figure in figures) + 2))
exported = []
rgba_exports = []
registered_sheet = Image.new("RGBA", (2048, 1536))
late_camera_origin = None
board = Image.new("RGB", (1064, 858), (230, 232, 237))
draw = ImageDraw.Draw(board)
for index, figure in enumerate(figures):
    w, h = [round(value * ratio) for value in figure.size]
    resized = figure.resize((w, h), Image.Resampling.LANCZOS)
    # First ten poses retain support; last two preserve a small airborne/precontact gap.
    ground = 470 if index <= 9 else 462 if index == 10 else 458
    if index <= 8:
        pixels = np.asarray(figure)
        sole = (pixels[:, :, 3] > 32) & (pixels[:, :, :3].min(axis=2) < 80)
        sole[:max(0, figure.height - 28)] = False
        split = figure.width // 2
        left_y, left_x = np.where(sole[:, :split])
        right_y, right_x = np.where(sole[:, split:])
        if not len(left_x) or not len(right_x):
            raise RuntimeError(f"Both planted sole anchors not established in{index}")
        pivot = (float(np.median(left_x)) + float(np.median(right_x)) + split) / 2
        x = round(240 - pivot * ratio)
        if index == 8:
            late_camera_origin = x - metadata[index]["nativeBounds"][0] * ratio
        metadata[index]["solePivotNativeX"] = pivot
        placement = "planted-sole midpoint, same whole-drawing scale"
    else:
        # Retain the original cell-relative placement in drive/flight poses;
        # never pin the leading foot or fit each pose independently.
        col = index % 4
        x = round(late_camera_origin + (metadata[index]["nativeBounds"][0] - col * width / 4) * ratio)
        placement = "shared late-phase source camera offset, no foot pinning"
    y = ground - h
    if x < 8 or x + w > 504 or y < 8 or y + h > 504:
        raise RuntimeError(f"Whole figure{index} exceeds safe export margins")
    frame = Image.new("RGBA", (512, 512))
    frame.alpha_composite(resized, (x, y))
    rgba_exports.append(frame)
    registered_sheet.alpha_composite(frame, ((index % 4) * 512, (index // 4) * 512))
    flat = Image.new("RGBA", frame.size, "white")
    flat.alpha_composite(frame)
    flat = flat.convert("RGB")
    exported.append(flat)
    row, col = divmod(index, 4)
    board.paste(flat.resize((256, 256), Image.Resampling.LANCZOS), (col * 266 + 5, row * 286 + 5))
    draw.text((col * 266 + 5, row * 286 + 263), f"{index:02d} / complete figure", fill=(25, 30, 40))
    metadata[index].update({"uniformScale": ratio, "translation": [x, y], "placementMethod": placement, "displaySoleBaseline": ground,
                            "nativeSheetEdgeRisk": any(value == boundary for value, boundary in zip(metadata[index]["nativeBounds"], (0, 0, width, height)))})
out.mkdir()
for index, (figure, frame) in enumerate(zip(figures, rgba_exports)):
    figure.save(out / f"native_figure_{index:02d}.png")
    frame.save(out / f"frame_{index:02d}.png")
board.save(out / "Contact_Sheet.png")
registered_sheet.save(out / "Registered_Sheet.png")
for name, size, duration in [("Preview.gif", 512, 70), ("Preview_Slow.gif", 512, 210), ("Preview_128.gif", 128, 70)]:
    frames = [frame.resize((size, size), Image.Resampling.LANCZOS) for frame in exported]
    strip = Image.new("RGB", (size * len(frames), size))
    for index, frame in enumerate(frames):
        strip.paste(frame, (index * size, 0))
    palette = strip.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    frames[0].save(out / name, save_all=True, append_images=frames[1:], duration=duration, loop=0, disposal=2, optimize=False)
(out / "manifest.json").write_text(json.dumps({"status": "whole-figure extraction/placement review; joint and weapon refinement pending",
    "source": source.relative_to(root).as_posix(), "sourceSha256": sha, "nativeSize": list(sheet.size),
    "frameCount": 12, "uniformExportRatio": ratio, "noIndividualBodyWeaponLayers": True,
    "timing": "provisional70ms; display baseline/flight clearance not gameplay physics", "frames": metadata}, indent=2) + "\n", encoding="utf-8")
if hashlib.sha256(source.read_bytes()).hexdigest() != sha:
    raise RuntimeError("Original sheet changed")
print(json.dumps({"review": str(out), "wholeFigures": 12, "uniformScale": ratio, "sourcePreserved": True,
                  "nativeBounds": [item["nativeBounds"] for item in metadata]}))
