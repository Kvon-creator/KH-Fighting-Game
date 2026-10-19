# Local Sora art workflow

**October19 result:** The user approved `attempt_03/final_pose_v1.png` as the single-pose style/carry anchor. The new partial sequence is [approved_style_sequence_v1/Review.html](../ready/run_loop/comfyui_trial/approved_style_sequence_v1/Review.html): approved anchor plus two complete flat refinements, board, once-only normal/slow GIFs and passing preservation/export/offline-viewer QA. `Prepare-AdjacentRunGuides.ps1` and `AdjacentRunPainting.cs` draw new empty-arm phases using original-sheet01/02 leg drawings and the approved upper carry. Use `adjacent_guides_v3`; v1/v2 are excluded diagnostics. Attempts04/05 completed and were collected. Their native renders need sleeve/cuff/finger/chest corrections; `Finalize-AdjacentRunPose.ps1` produces reviewed sibling `final_pose_v2.png` on a full flat canvas. Existing attempts and refinements must not be resubmitted/overwritten.

`inspect_adjacent_poses.py` checks native hashes/provenance/pixels; `--final` additionally verifies the reviewed derivatives and36,956 original visible leg pixels against white compositing. `Build-AdjacentPoseReview.ps1` requires passing final preservation QA and actual art review. `inspect_adjacent_review.py` validates copied PNGs, GIF timing/no-repeat and floor variation; `check_adjacent_review.mjs` checks links and controls offline. Both preserve existing reports. Actual browser/Godot playback, transparent sprites and the full alternating run/stop with follow-through and final joins remain unfinished. Phase labels and timing in this short study are provisional.

Historical records below describe the earlier pending state. Attempt03 is now approved; attempts01/02 are rejected terminal diagnostics. They are not still running or awaiting collection.

**Current art result, October14:** `ready/run_loop/comfyui_trial/attempt_03/final_pose_v1.png` is ready for the user's single-pose art review. Its comparison and ART_REVIEW.md explain the complete flat-guide/model/direct-fist finishing workflow. Final_Preservation_QA.json verifies all242,555 outside-selection pixels and original protected grip/face/weapon regions unchanged. The native render and failed16-background-edge QA remain preserved; future selections now hard-protect their edges. Attempts01/02 are rejected diagnostics. CPU generation works but took401seconds for the first render and373.81seconds for the third; unconstrained whole-image generation did not preserve the design. Final user approval, transparent sprites, complete chronological run/stop cycles, motion/wrap/joins and gameplay integration remain unfinished. No component production layers or additional packages/models were used.

**Current status, October14:** Installation recovery is complete. [Runtime_Validation.json](Runtime_Validation.json) records52,839 intact files plus5,641 missing entries restored and verified, for all58,480 archive files. The checkpoint size/SHA256 also match the pins. [CUDA_Diagnostic.json](CUDA_Diagnostic.json) preserves `RuntimeError: No CUDA GPUs are available`; GPU generation is unavailable for this runtime, with cause unestablished. The approved pilot is proceeding on CPU through `Start-LocalComfy.ps1 -Cpu`; the CPU API/core nodes/checkpoint passed live checks and attempt_01 is running with a saved request/receipt. Collect its existing prompt ID without resubmission; actual art review remains pending. No drivers, global settings, additional models or packages were changed. Earlier preparation/download text below is historical.

Prepared October13 for the computer the user chose: GTX1650, approximately4GiB VRAM,23.4GiB RAM and22.7GiB free on D: at inspection. GPU inventory succeeded through WMI; NVIDIA-SMI reported insufficient permissions. Actual CUDA generation remains untested.

## Prepared installation

Portable **ComfyUI v0.39.0, CUDA12.6**, plus **DreamShaper8 pruned**. The pinned archives/model total4,027,961,412 download bytes (about3.75GiB), with additional space needed for extraction. Exact URLs, sizes, revisions and published SHA256 digests are in [setup_plan.json](setup_plan.json). The installer verifies every download and inspects archive paths/expanded size before extraction. It retains the archive and any failed partial files.

Runtime/model files stay in ignored `.local/` inside this workspace. No global Python/PATH changes, driver updates, Krita, custom nodes or cloud account are included. The launcher binds loopback8188, disables partner/custom nodes, uses low-VRAM mode and CPU VAE, and keeps its process hidden. These settings are a starting point for this hardware; performance and art quality must be measured with the pilot.

Sources: [official portable installation](https://docs.comfy.org/installation/comfyui_portable_windows), [pinned release](https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.39.0), [model author's repository](https://huggingface.co/Lykon/DreamShaper), [exact checkpoint](https://huggingface.co/Lykon/DreamShaper/blob/main/DreamShaper_8_pruned.safetensors), [pinned startup flags](https://github.com/Comfy-Org/ComfyUI/blob/v0.39.0/comfy/cli_args.py).

**Installation and the first pilot are explicitly approved, October13.** The user selected "Install and run the pilot" for this exact portable runtime/model setup. The runtime archive downloaded and matched its published checksum; archive path and space checks passed. Extraction is active (58,480 files,5,580,961,635 expanded bytes). The approved model completed through `Stage-LocalModel.ps1`, matched its pinned size/hash and was placed while extraction remained active. A curl56 Schannel connection failure was preserved exactly in `Model_Download_Failure_01.json`; explicit byte-range resume succeeded, recorded in `Model_Download_Recovery_01.json`. The original installer will verify the checkpoint again. Do not rerun the active installer or run the incomplete runtime. CUDA access and actual generation remain to be verified. No repeated installation confirmation is needed for this approved scope.

## Complete-frame pilot

The original twelve-pose generated sheet remains the source. Its existing complete registered pose00 was flattened onto white at unchanged512px coordinates under `ready/run_loop/comfyui_trial/reference_v1/`. This is an input-format conversion, not a new pose. Original sheet/frame hashes are unchanged; provenance is recorded beside the whole reference. No body or weapon parts/layers were created.

[pilot_job.json](pilot_job.json) requests one complete pose with the front empty arm pulled backward while the far arm keeps its own shoulder carry behind the head. [pilot_request_template.json](pilot_request_template.json) exposes the exact8-node local image-to-image graph and prompts. Its upload name is a placeholder; nothing has been submitted. Fixed seed,28 steps and0.55 denoise are pilot settings, not validated production settings.

The model must preserve clean curved KH2 cel shading, rich original materials/proportions, a noninverted grip and one connected constant Kingdom Key, with the tip slightly toward the foreground. Review the actual output, including full figure/cell fit. A failed pose is diagnostic; use a specific correction and a fresh attempt. A passing pose goes to the user for final approval. Only then expand into chronological complete-frame running cycles with alternate supports, both directions of free-arm swing and a smooth wrap. Running quality comes before aerial production.

This first graph is a plain image-to-image pilot, without pose ControlNet or a reference adapter. It does not guarantee the requested topology or style. If it fails, inspect the result before proposing another model/package. Generated output is expected to have a background; an alpha-capable PNG alone does not prove transparency.

The backward-arm pilot holds the original leg pose to isolate the drawing correction. It tests arm/carry topology, not a correctly phased running contact. The eventual cycle must counter-swing against newly alternating legs.

## Agent controls

`comfy_local.mjs` provides `status`, `plan JOB`, `submit JOB attempt_NN` and `collect RECEIPT_FOLDER`. Use the already installed project-local Node when its CLI works, or import the same module through the available Node REPL. The API functions operate only on a loopback backend and project files. Production CLI attempts live under each animation's `ready/<animation>/comfyui_trial/` folder. No approved/gameplay asset is replaced.

- Status verifies the live core nodes and local checkpoint.
- Submission preserves exact prompts, graph, input hash, upload/queue responses and receipt.
- Collection is bounded to45 seconds and resumes the existing prompt ID. Existing attempts cannot be resubmitted automatically.
- An uncertain submission stops without another POST. The raw error stays in `complete_error.txt`;400 validation,401/403 permission and5xx service errors remain separate from submission certainty. Unspecified errors are not labeled content refusals.
- Downloads preserve native PNGs and hashes, with `generated_pending_review` and final user approval pending. PNG metadata is not an artwork/transparency certificate.

The current runtime is installed: do not rerun `Install-LocalComfy.ps1 -Install` on it. Inspect the saved receipt and current launch/API state. `Start-LocalComfy.ps1 -Cpu` is the approved same-model CPU fallback; GPU mode requires a successful CUDA check. These scripts assert the D: root. Inspect launch logs/API status before submitting `pilot_job.json`. Collect the same attempt until terminal; open the resulting image for actual visual review before changing the job or presenting artwork.

## Verification so far

[QA_Preparation.json](QA_Preparation.json) records successful PowerShell syntax checks, source/hash/512px RGB reference checks and a mock HTTP API test of upload, queuing, recovery, exact errors and pending approval. Mock copies/receipts remain under ignored `.local/comfy_adapter_checks/` and are not generated artwork.

Project-local Node CLI checks stalled and were stopped; the adapter module and mock checks passed in the available Node REPL. Runtime/model installation is in progress; no real GPU generation, new drawing, browser playback or Godot test has occurred. Local8188 returned ECONNREFUSED at preinstallation inspection. The current preserved local drawing candidate remains gait_cycle_study_v5; its stop join and final artwork approval remain unfinished.
