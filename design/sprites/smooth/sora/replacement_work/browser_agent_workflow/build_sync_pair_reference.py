"""Whole-frame endpoint comparisons for new complete in-between drawings."""
import hashlib
import json
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parents[6]
if str(root).lower() != r"d:\kh fighting game":
    raise RuntimeError(f"Unexpected workspace: {root}")
work = root / "design/sprites/smooth/sora/replacement_work/ready/run_start"
source = work / "direct_imagegen_trial/whole_figure_review_v3"
out = work / "sync_refinement_v1/references"
out.mkdir(parents=True, exist_ok=True)
target = out / "Four_Endpoint_Pairs.png"
if target.exists():
    raise RuntimeError("Preserve the existing reference")
pairs = [(1, 2), (3, 4), (5, 6), (9, 10)]
sheet = Image.new("RGBA", (1024, 2048))
records = []
for row, pair in enumerate(pairs):
    for col, index in enumerate(pair):
        file = source / f"frame_{index:02d}.png"
        with Image.open(file) as frame:
            sheet.alpha_composite(frame.convert("RGBA"), (col * 512, row * 512))
        records.append({"row": row, "side": "start" if col == 0 else "end", "originalPose": index,
                        "file": file.relative_to(root).as_posix(), "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
sheet.save(target)
(out / "manifest.json").write_text(json.dumps({"purpose": "whole drawings as endpoint pose references; not production layers",
                                               "pairs": pairs, "sources": records}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"reference": str(target), "pairs": pairs}))
