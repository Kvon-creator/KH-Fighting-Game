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
| Run start | Body poses accepted; weapon geometry rejected. Two same-arm shoulder-carry correction attempts blocked; existing source remains draft. |
| Run loop | Eight-pose local rigid-carry review exported in run_loop/review_cycle_v1. Anatomy, gait/seam and garment consistency remain draft-quality review work; no engine integration. |
| Run stop | Output-stage generation rejected; no artwork produced. |
| KH1 first jump / KH2 Aerial Dodge second jump | Pending. |
| Backdash / forward and backward air dashes | Pending. |
| Nine basic attacks | Pending. Motions already approved in the design chart. |

## Review

Open Shimmy_Previews.html in a browser to pause, step, change playback speed, and mirror facing. PNGs retain transparency; GIF previews use a dark solid background.

The old asset package is copied to design/sprite_backups/sora_before_pose_replacement. Original sprite-package filenames are preserved. Animation-specific files are grouped in ready/ flow folders; replacement_work retains shared packaging tools.

Generation used built-in image_gen with the approved stand-idle sprite as reference. Prompts and production methods are recorded alongside the sources. Every pose comes from new drawings; no animation was fabricated by stretching a static character. One uniform scale per generated batch fits the established 512 x 512 export canvas. Individual frame placement aligns floor contact at y=470.

Checks: every GIF frame decoded; manifest frame paths exist; forward and backward packages each contain ten distinct pixel images. Pose and linework consistency still require visual review. This is not Godot gameplay integration or an in-engine test. Weapon socket positions are not measured yet.
