"""Audit preserved sources and browser candidate provenance; no visual approval."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parents[6]
if str(root).lower() != r"d:\kh fighting game":
    raise RuntimeError(f"Unexpected workspace: {root}")
work = root / "design/sprites/smooth/sora/replacement_work"
expected = {
    work / "ready/standing_idle/sora_stand_idle_00.png": "baf8959c0e0d42b74bf7f6100a83ccf5c208a9decd5b98b95110f3129fbacdc7",
    work / "ready/run_loop/layers/frame_00_review_v1/sora_run_loop_00_review.png": "b171c554aef835fefe805b88c00431836d67f7b9f91e1f43f8f930257edea48e",
    work / "ready/run_loop/layers/art_pass_05/kingdom_key_master_finished.png": "d942f08de984050119716906f0311a467f5be3150811ae634b40c327c6eaa800",
    root / "design/references/Sora_KHIV_Render.webp": "5dc59758a962e411e1b90f5f440f2d4cef0e42b07b1a91550d42455147f19a30",
}
digest = lambda file: hashlib.sha256(file.read_bytes()).hexdigest()
for file, sha in expected.items():
    if digest(file) != sha:
        raise RuntimeError(f"Established source changed: {file.relative_to(root)}")
attempts = []
for animation in ("run_start", "run_loop", "run_stop"):
    for directory in sorted((work / f"ready/{animation}/gemini_browser_trial").glob("attempt_*")):
        receipt = directory / "exchange_state.json"
        job = json.loads(receipt.read_text(encoding="utf-8")) if receipt.exists() else {}
        capture = directory / "submitted_prompt.txt"
        if job.get("promptSha256"):
            normalized = capture.read_text(encoding="utf-8").replace("\r\n", "\n")
            if hashlib.sha256(normalized.encode("utf-8")).hexdigest() != job["promptSha256"]:
                raise RuntimeError(f"Captured prompt differs from receipt: {directory.name}")
        images = []
        for file in sorted(directory.iterdir()):
            if file.suffix.lower() not in {".png", ".jpg", ".jpeg", ".jfif", ".webp"}:
                continue
            with Image.open(file) as im:
                im.load()
                images.append({"file": file.name, "format": im.format, "size": list(im.size),
                               "mode": im.mode, "hasAlpha": "A" in im.getbands(), "sha256": digest(file)})
        for manifest_file in directory.glob("frame_review_*/manifest.json"):
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            original = directory / manifest["source"]
            if digest(original) != manifest["sourceSha256"]:
                raise RuntimeError(f"Original changed after extraction: {original}")
        attempts.append({"animation": animation, "attempt": directory.name,
                         "status": job.get("status", "historical_manual_capture"), "media": job.get("media", "image"),
                         "review": job.get("review", "see preserved QA notes"),
                         "finalUserApproval": job.get("finalUserApproval", "pending"), "images": images})
audit = {"checkedAt": datetime.now(timezone.utc).isoformat(), "establishedSourcesUnchanged": True,
         "scope": "file provenance and image formats only; does not verify anatomy, weapon geometry, natural motion or final approval",
         "establishedSources": [{"file": file.relative_to(root).as_posix(), "sha256": sha} for file, sha in expected.items()],
         "attempts": attempts}
(Path(__file__).parent / "AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"establishedSourcesUnchanged": True, "attempts": len(attempts),
                  "images": sum(len(attempt["images"]) for attempt in attempts),
                  "providerBlocks": [f"{attempt['animation']}/{attempt['attempt']}" for attempt in attempts if attempt["status"] == "provider_block"],
                  "pendingCollections": [f"{attempt['animation']}/{attempt['attempt']}" for attempt in attempts if attempt["status"] in {"prepared", "submission_attempted", "waiting_for_gemini"}]}))
