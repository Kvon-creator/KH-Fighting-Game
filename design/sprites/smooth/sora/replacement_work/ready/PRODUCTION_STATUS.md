# Sora smooth sprite production status

## Current files

| Batch | Status |
| --- | --- |
| Standing guard / breathing idle | New 10-frame artwork and package installed; full-cycle preview approved by K'von. |
| Crouch down / stand up | New eight-pose articulated transition installed; rise reverses the poses. Full-cycle preview approved. |
| Crouching guard / idle | New guard and four generated breathing poses installed with updated sheet and manifest; visual review still required. |
| Forward shimmy | Ten generated step poses, transparent frames, sheet, GIF and manifest delivered for review. |
| Backward shimmy | Ten shared poses from forward footwork, in reverse order. Separate backward generation had inadequate front-foot follow-through; its correction was blocked. Shared artwork is documented in the manifest. |
| Attack wind-up | Original file retained. Two new generation attempts were rejected by the image tool's output safety system; no replacement is claimed. |
| Run start | Original eight-pose source retained. Earlier full-cycle draft FAILED visual QA. Individual start refinements now cover 01-04: 01 in refinement_v3, revised lift 02 in refinement_v4, shoulder-settle 03 and push-off 04 in refinement_v3. Five-pose partial review includes approved idle endpoint 00; it is not a complete cycle. Remaining 05-07, inferred garment detail and weapon endpoint seam are unfinished. |
| Run loop | Eight-pose local rigid-carry review exported in run_loop/review_cycle_v1. Anatomy, gait/seam and garment consistency remain draft-quality review work; no engine integration. |
| Run stop | Eight-pose refinement_v2 replaces flat construction legs with shaded shorts contours, trim and arm lighting. Still below approved-idle quality; anatomy, torso seams and guard transition remain. Original construction_v1 retained. |
| KH1 first jump / KH2 Aerial Dodge second jump | Pending. |
| Backdash / forward and backward air dashes | Pending. |
| Nine basic attacks | Pending. Motions already approved in the design chart. |

## Review

Open Shimmy_Previews.html in a browser to pause, step, change playback speed, and mirror facing. PNGs retain transparency; GIF previews use a dark solid background.

The old asset package is copied to design/sprite_backups/sora_before_pose_replacement. Original sprite-package filenames are preserved. Animation-specific files are grouped in ready/ flow folders; replacement_work retains shared packaging tools.

Earlier idle, crouch and shimmy generation used built-in image_gen with the approved stand-idle sprite as reference. Prompts and production methods are recorded alongside the sources. Running now uses the authorized local layered workflow: genuine source pose differences, individually drawn repairs, a fixed rigid weapon master and corrected grip. No generation retries are in progress. No animation is fabricated by stretching a static character. Earlier packages use one uniform batch scale and floor y470; current running review exports use 512 x 512 canvases with grounded contact aligned at y432 by translation only.

Checks: GIF frames decode, manifest paths exist, and running originals retain their recorded hashes. The new five-frame run-start review also verifies distinct image content and clear RGB under full transparency. Pose and linework consistency still require visual review. This is not Godot gameplay integration or an in-engine test. Local rigid-weapon grip/collar/tip anchors are recorded, but engine weapon sockets are not configured.
