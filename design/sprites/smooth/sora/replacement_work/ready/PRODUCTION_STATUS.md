# Sora smooth sprite production status

## Current files

October 8 steering: local refinement is paused while K'von tests Gemini complete-frame generation for all movement clips. The compact prompt, essential references, full movement list and optional cycle guides are in design/gemini_movement_handoff/. Existing artwork is preserved. Unapproved individual loop03/04 garment candidates are retained with known visual defects documented in run_loop/GARMENT_V3_CHECKPOINT.md; they have not replaced the current v2 full-cycle package.

| Batch | Status |
| --- | --- |
| Standing guard / breathing idle | New 10-frame artwork and package installed; full-cycle preview approved by K'von. |
| Crouch down / stand up | New eight-pose articulated transition installed; rise reverses the poses. Full-cycle preview approved. |
| Crouching guard / idle | New guard and four generated breathing poses installed with updated sheet and manifest; visual review still required. |
| Forward shimmy | Ten generated step poses, transparent frames, sheet, GIF and manifest delivered for review. |
| Backward shimmy | Ten shared poses from forward footwork, in reverse order. Separate backward generation had inadequate front-foot follow-through; its correction was blocked. Shared artwork is documented in the manifest. |
| Attack wind-up | Original file retained. Two new generation attempts were rejected by the image tool's output safety system; no replacement is claimed. |
| Run start | All eight working poses are packaged in run_start/refinement_v4/review_cycle_v2. Latest stride05-07 have individual arm/cloth repairs and the last shoe is recovered from an expanded source crop. The earlier failed full-cycle draft and partial review are retained. Artwork detail, idle weapon endpoint, root/timing and body/rear-leg transition into loop00 remain unfinished. |
| Run loop | run_loop/review_cycle_v2 applies rear-shaft/front-guard overlap to all eight existing genuine poses. Weapon projections and corrected grip drawings are unchanged; frame00 retains its exact approved hand/cuff area. Attached old guard fragments in03/04 are cleared with local masks. Individual body layers and prior reviews are preserved. Clothing/arm anatomy, gait, registration and transition seams remain unfinished; see QA_NOTES.md. No engine integration. |
| Run stop | Eight-pose refinement_v2 replaces flat construction legs with shaded shorts contours, trim and arm lighting. Still below approved-idle quality; anatomy, torso seams and guard transition remain. Original construction_v1 retained. |
| KH1 first jump / KH2 Aerial Dodge second jump | Pending. |
| Backdash / forward and backward air dashes | Pending. |
| Nine basic attacks | Pending. Motions already approved in the design chart. |

## Review

Open Shimmy_Previews.html in a browser to pause, step, change playback speed, and mirror facing. PNGs retain transparency; GIF previews use a dark solid background.

The old asset package is copied to design/sprite_backups/sora_before_pose_replacement. Original sprite-package filenames are preserved. Animation-specific files are grouped in ready/ flow folders; replacement_work retains shared packaging tools.

Earlier idle, crouch and shimmy generation used built-in image_gen with the approved stand-idle sprite as reference. Prompts and production methods are recorded alongside the sources. Running now uses the authorized local layered workflow: genuine source pose differences, individually drawn repairs, a fixed rigid weapon master and corrected grip. No generation retries are in progress. No animation is fabricated by stretching a static character. Earlier packages use one uniform batch scale and floor y470; current running review exports use 512 x 512 canvases with grounded contact aligned at y432 by translation only.

Checks: both eight-pose running packages have distinct PNG content, decodable GIFs, complete manifests and clean RGB under full transparency. Translation exports do not clip opaque pixels; running originals retain their recorded hashes. New loop layers verify unchanged weapon projections, corrected grip drawings/interiors and retained lower-body regions. Pose, gait and linework consistency still require visual review. This is not Godot gameplay integration or an in-engine test. Local rigid-weapon grip/collar/tip anchors are recorded, but engine weapon sockets are not configured.
