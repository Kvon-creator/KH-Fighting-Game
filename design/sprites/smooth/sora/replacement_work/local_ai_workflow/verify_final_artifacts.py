"""Read-only image/hash verification; writes only a small JSON QA record."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[6]
assert str(ROOT).lower() == r"d:\kh fighting game"
BASE = ROOT / "design/sprites/smooth/sora/replacement_work"
checks = [
    ("ready/run_loop/direct_generation_retry_v1/sora_run_loop_generated_original.png",
     "9d919b4f317981b331010a1ddb049a7807fb8f21ba214d82a40b04291c9065c7"),
    ("ready/standing_idle/sora_stand_idle_00.png",
     "baf8959c0e0d42b74bf7f6100a83ccf5c208a9decd5b98b95110f3129fbacdc7"),
    ("ready/run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/Run_Start_13_Once.gif",
     "1f9f81975ea11f747e8956e72e9705968ae5fdb8379e5622bc785c7aad747d41"),
]
results = []
for relative, expected in checks:
    actual = hashlib.sha256((BASE / relative).read_bytes()).hexdigest()
    assert actual == expected, f"Original changed: {relative}"
    results.append({"file": relative, "sha256": actual, "unchanged": True})
selection = BASE / "ready/run_loop/comfyui_trial/reference_v6/temporary_selection.png"
rects = [(125,100,188,140),(298,100,137,139),(404,177,81,80)]
with Image.open(selection) as image:
    assert image.size == (512,512) and image.mode == "RGB"
    pixels = image.load()
    nonzero = sum(pixels[x,y][0] != 0 for left,top,width,height in rects
                  for y in range(top,top+height) for x in range(left,left+width))
assert nonzero == 0, "Protected selection edge still leaks"
report = {"originals": results, "protectedMaskPixelsNonzero": nonzero,
          "passed": True, "imageEditingPerformed": False,
          "scope": "Original hashes and future hard protection; no generation"}
(BASE / "local_ai_workflow/QA_Final_Artifacts.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
