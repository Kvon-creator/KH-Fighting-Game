"""Record preserved image formats and this pilot's manual review; edit no sprites."""
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[6]
if str(ROOT).lower() != r"d:\kh fighting game":
    raise RuntimeError(f"Unexpected workspace: {ROOT}")
WORK = ROOT / "design/sprites/smooth/sora/replacement_work"
TRIAL = WORK / "ready/run_loop/gemini_browser_trial"
EXPECTED = {
    "ready/standing_idle/sora_stand_idle_00.png": "baf8959c0e0d42b74bf7f6100a83ccf5c208a9decd5b98b95110f3129fbacdc7",
    "ready/run_loop/layers/frame_00_review_v1/sora_run_loop_00_review.png": "b171c554aef835fefe805b88c00431836d67f7b9f91e1f43f8f930257edea48e",
    "ready/run_loop/layers/art_pass_05/kingdom_key_master_finished.png": "d942f08de984050119716906f0311a467f5be3150811ae634b40c327c6eaa800",
}
for relative, expected in EXPECTED.items():
    if hashlib.sha256((WORK / relative).read_bytes()).hexdigest() != expected:
        raise RuntimeError(f"Reference changed: {relative}")
carry = ROOT / "design/references/Sora_KHIV_Render.webp"
if hashlib.sha256(carry.read_bytes()).hexdigest() != "5dc59758a962e411e1b90f5f440f2d4cef0e42b07b1a91550d42455147f19a30":
    raise RuntimeError("Carry reference changed")

notes = {
    1: "Rejected carry direction and free-hand/blade overlap.",
    2: "Carry corrected; key-head side and invented glove wheel need correction.",
    3: "Key-head side and glove corrected; rounded-cutout objection later recalibrated against approved idle.",
    4: "Construction-master reference did not materially change cutouts; preserved comparison revision.",
    5: "User liked general art and requested opposite far-arm carry; unchanged pose not finally approved.",
}
prompt = Path(__file__).parent / "PILOT_PROMPT.txt"
first = TRIAL / "attempt_01/submitted_prompt.txt"
if first.exists() and first.read_bytes() != prompt.read_bytes():
    raise RuntimeError("Initial prompt record differs; preserve it for inspection")
if not first.exists():
    shutil.copyfile(prompt, first)

results = []
for attempt, note in notes.items():
    directory = TRIAL / f"attempt_{attempt:02d}"
    raw_composer = directory / "composer_text.txt"
    composer_json = directory / "composer_capture.json"
    if raw_composer.exists() and not composer_json.exists():
        # Preserve every UI newline inside JSON rather than trimming the capture.
        composer_json.write_text(json.dumps({"text": raw_composer.read_text(encoding="utf-8")}, indent=2) + "\n", encoding="utf-8")
    images = []
    for file in sorted(directory.iterdir()):
        if file.suffix.lower() not in {".jpg", ".jpeg", ".jfif", ".png", ".webp"}:
            continue
        with Image.open(file) as im:
            images.append({"file": file.name, "format": im.format,
                           "dimensions": list(im.size), "mode": im.mode,
                           "hasAlpha": "A" in im.getbands(),
                           "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    review_file = directory / "visual_review.json"
    review = json.loads(review_file.read_text(encoding="utf-8")) if review_file.exists() else {
        "attempt": attempt, "review": note, "finalUserApproval": "pending", "animationPhaseCount": 1}
    # Rechecking formats must not reset a later human verdict.
    review["images"] = images
    review_file.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    results.append({"attempt": attempt, "images": len(images),
                    "formats": sorted({im["format"] for im in images})})

receipt = TRIAL / "attempt_05/exchange_state.json"
job = json.loads(receipt.read_text(encoding="utf-8"))
if job.get("review") in {None, "pending", "pilot_art_passed"}:
    job["review"] = "revision_requested_opposite_arm_carry"
job.setdefault("reviewNotes", "visual_review.json and ../REVIEW.md")
job["referenceContext"] = ["Construction master uploaded in attempt04 and retained in chat context; finished-idle detailed design takes precedence."]
receipt.write_text(json.dumps(job, indent=2) + "\n", encoding="utf-8")
local = ROOT / ".local/browser-agent"
local.mkdir(parents=True, exist_ok=True)
with Image.open(TRIAL / "attempt_05/gemini_original_preview.jpg") as im:
    im.resize((128, 128), Image.Resampling.LANCZOS).save(local / "pilot_game_scale_inspection.png")
print(json.dumps({"referenceHashesUnchanged": True, "attempts": results,
                  "review": job.get("review"), "finalUserApproval": job.get("finalUserApproval")}))
