# Alternating-stride refinement

Current study: **16 complete poses, 960ms**, painted on single flat RGBA canvases. Original generated sheets, run-start benchmark, approved idle, earlier refinements and stop are preserved.

## Changes

- New hip/knee/ankle poses alternate near/far support, compression, recovery, passing, toe-off and flight. Shorts/calves have new curved contours; complete native PNG references preserve clothes and boot detail through temporary selections.
- The near/front arm counter-swings. Forward hand paths stay below the blade, so the hand reads as empty. The far/rear arm carries the Keyblade over its own shoulder behind the head. Version2's ambiguous hand03/10-blade overlaps are excluded.
- Four new joint/contour drawings bridge key02-03,08-09,09-10 and10-11. Splitting80ms into40/40 preserves the960ms cycle. Largest adjacent ankle displacement falls from77.62px in the twelve-pose version3 to38.81px here. This is spacing evidence, not a certificate of fluid motion.
- One native upper reference preserves consistent carrying grip/weapon shape. Protected grip/guard, face/hair and blade regions retain exact source pixels before integer body bob. The inherited tip direction is stylized toward the foreground, not certified3D.

No pose scaling or pixel morphs create the new drawings. Arm painting precedes leg drawing; stage/probe PNGs are complete sprites, never parts or production layers.

## Review and checks

[Review.html](Review.html) compares original drawings, the prior arm study or the twelve-pose gait against this cycle at the same cycle time. Earlier poses hold for80ms; similar indices do not imply matching leg roles. Use slow playback, pause and frame stepping. The128px panel uses the actual transparent export.

[Pose board](Contact_Sheet.png), [loop GIF](Preview_512_Loop.gif), [transparent sheet](Sprite_Sheet_512.png), [manifest](manifest.json) and [QA report](QA_Report.json) are here. Judge art finish against the [exact run-start benchmark](../../../run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/Run_Start_13_Once.gif).

Read-only QA checks distinct512px/128px RGBA exports, alpha/margins, projected limb-guide lengths, support/flight order, protected upper pixels, unchanged sources and GIF timing/repeat. Solid support soles end at470; flight has positive clearance. Faint native edge/shadow alpha extends up to5px lower. No detached opaque component above8px is present. Offline viewer checks cover links,16-frame wrap,960ms timing, x3 slow speed, scrub/step/pause/comparison/floor controls. No actual-browser or Godot playback test.

## Remaining work

Hip garment volume, native-brush/new-contour seams, shoe depth and sleeve/cuff shadows need more polish. Torso pitch, carrying-shoulder, cloth and chain follow-through remain. Passing and toe-off/flight speed need actual playback review. Revisit the first running frame and run-start entry. The preserved stop is still motion_refinement_v4 and does not share this new loop's entry; new braking drawings and the approved-idle join remain unfinished. Do not call the pair synchronized or idle-quality yet.

## Preserved diagnostics

Pilot1 is the inspection grid. Pilot2 exposed rotated red-cloth contamination; pilot3 introduced new pants contours. Partial near_stride_study_v1 had weak flight; version2 corrected sole registration and flight. These explore the opposite stride half, not chronological insertions between original02/03.

Gait cycle1 holds the free arm;2 adds counter-swing but has ambiguous hand03/10 overlaps;3 fixes the hand path;4 adds the new transitions. All complete canvases and painter snapshots are preserved. The first inbetween build failed before folder creation due to PowerShell array-expression precedence, then the helper was corrected. This was a local script error, not an image-generation rejection. No image-service retries, installations or engine edits in this batch.
