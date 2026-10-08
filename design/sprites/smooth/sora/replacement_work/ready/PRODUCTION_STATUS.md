# Sora smooth sprite production status

## Current files

October 8 steering: K'von ended the Gemini trial and requested returning to local refinement. design/gemini_movement_handoff/ is deleted; original artwork is retained. Latest run_loop/review_cycle_v4 includes individual03-07 jacket/arm repairs, with source hood/pad detail on05-07 and06's old chest arm/guard strip removed. Previous candidates/packages remain preserved. These changes do not finalize the running animations.

| Batch | Status |
| --- | --- |
| Standing guard / breathing idle | New 10-frame artwork and package installed; full-cycle preview approved by K'von. |
| Crouch down / stand up | New eight-pose articulated transition installed; rise reverses the poses. Full-cycle preview approved. |
| Crouching guard / idle | New guard and four generated breathing poses installed with updated sheet and manifest; visual review still required. |
| Forward shimmy | Ten generated step poses, transparent frames, sheet, GIF and manifest delivered for review. |
| Backward shimmy | Ten shared poses from forward footwork, in reverse order. Separate backward generation had inadequate front-foot follow-through; its correction was blocked. Shared artwork is documented in the manifest. |
| Attack wind-up | Original file retained. Two new generation attempts were rejected by the image tool's output safety system; no replacement is claimed. |
| Run start | All eight working poses are packaged in run_start/refinement_v4/review_cycle_v2. Latest stride05-07 have individual arm/cloth repairs and the last shoe is recovered from an expanded source crop. The earlier failed full-cycle draft and partial review are retained. Artwork detail, idle weapon endpoint, root/timing and body/rear-leg transition into loop00 remain unfinished. |
| Run loop | run_loop/review_cycle_v4 combines03/04 v4 garments and05/06/07 v3 source-pose jackets/arms. The old straight-arm/guard strip on06's chest is removed. Frames00-02 retain v2 clothing. Carry/grip/chain files are unchanged; frame00 retains its approved hand/cuff. Original sources and all earlier reviews remain. Remaining jackets, cross-frame arm/material proportions, both alternating strides, root/timing and seams require work; see QA_NOTES.md. No engine integration. |
| Run stop | Eight-pose refinement_v2 replaces flat construction legs with shaded shorts contours, trim and arm lighting. Still below approved-idle quality; anatomy, torso seams and guard transition remain. Original construction_v1 retained. |
| KH1 first jump / KH2 Aerial Dodge second jump | Pending. |
| Backdash / forward and backward air dashes | Pending. |
| Nine basic attacks | Pending. Motions already approved in the design chart. |

## Review

Open Shimmy_Previews.html in a browser to pause, step, change playback speed, and mirror facing. PNGs retain transparency; GIF previews use a dark solid background.

The old asset package is copied to design/sprite_backups/sora_before_pose_replacement. Original sprite-package filenames are preserved. Animation-specific files are grouped in ready/ flow folders; replacement_work retains shared packaging tools.

Earlier idle, crouch and shimmy generation used built-in image_gen with the approved stand-idle sprite as reference. Prompts and production methods are recorded alongside the sources. Running now uses the authorized local layered workflow: genuine source pose differences, individually drawn repairs, a fixed rigid weapon master and corrected grip. No generation retries are in progress. No animation is fabricated by stretching a static character. Earlier packages use one uniform batch scale and floor y470; current running review exports use 512 x 512 canvases with grounded contact aligned at y432 by translation only.

Checks: both eight-pose running packages have distinct PNG content, decodable GIFs, complete manifests and clean RGB under full transparency. Translation exports do not clip opaque pixels; running originals retain their recorded hashes. New loop layers verify unchanged weapon projections, corrected grip drawings/interiors and retained lower-body regions. Pose, gait and linework consistency still require visual review. This is not Godot gameplay integration or an in-engine test. Local rigid-weapon grip/collar/tip anchors are recorded, but engine weapon sockets are not configured.
