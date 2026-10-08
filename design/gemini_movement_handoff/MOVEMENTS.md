# Sora movement brief

Generate complete character-plus-weapon images. This Gemini trial replaces the layer-based production method for these new outputs only. Existing artwork stays intact.

## Movement inventory

Counts below are drawing targets, not gameplay timing. Older chart counts of 3-4 drawings for transitions are superseded by the user's request for approximately 7-12 transition drawings. The existing running batches have eight poses each.

| Folder / animation | Target frames | Motion |
| --- | ---: | --- |
| standing_idle | 10 | Approved KH2 combat guard; subtle breathing, planted feet; seamless loop. Keyblade held low with both hands, blade diagonally up and back, away from the opponent on the right. |
| duck_down | 8 | Balanced lowering from the approved guard into a low guard; bend hips, knees and ankles. |
| crouching_idle | 4 | Restrained breathing in a balanced low guard; seamless loop. |
| stand_up | 8 | Rise naturally into the exact standing guard, preserving support-foot contacts. |
| shimmy_forward | 10 | Lead foot advances, trailing foot follows; guarded torso and readable foot transfer. Loop. |
| shimmy_backward | 10 | Rear foot retreats, lead foot follows; continue facing the opponent. Draw genuine backward weight transfer. Loop. |
| run_start | 8 | Guard -> natural one-hand shoulder carry -> lean, push-off, accelerating stride. |
| run_loop | 8 | Alternate both legs through contact, recoil, passing, push-off and flight. Counter-motion in torso/free arm; same-arm shoulder carry. Seamless loop. |
| run_stop | 8 | Last running stride -> braking foot plant and compression -> recover upright guard. Do not merely reverse run start. |
| jump_takeoff | 8 | KH1 normal-jump-inspired anticipation, knee compression and push-off; leave the floor only after contact releases. |
| jump_ascent | 8 | KH1-inspired rising poses; coherent leg tuck and weapon/arm motion. |
| jump_apex | 2 | Brief transition from rising to falling, with clear body and weapon follow-through. |
| jump_fall | 8 | Prepare feet for contact while retaining the opponent-facing air pose. |
| jump_land | 8 | First contact -> absorb impact through knees/hips -> standing guard. |
| second_jump | 8 | KH2 Aerial Dodge-inspired somersault -> controlled return into the air pose. Motion reference only; no gameplay invulnerability is implied. |
| backdash | 8 | Guarded backward hop, recoil, contact and recovery; stay opponent-facing. |
| air_dash_forward | 8 | Anticipation, forward burst, braking and return to airborne pose. |
| air_dash_backward | 8 | Distinct backward burst and recoil, still opponent-facing; do not reverse the forward clip. |

First produce run_start, run_loop and run_stop as one connected set. Then generate the remaining inventory. Existing approved idle/crouch cycles are references for the new complete set. Attacks and optional wind effects are outside this movement handoff.

## Consistency and export

- Standard KH2 outfit and Kingdom Key, smooth line art/cel shading. The KH4 photo is a carry/construction reference only. Keep face, hair silhouette, jacket trim, yellow straps, red waist cloth, gloves, baggy shorts and large shoes consistent.
- Fixed right-facing three-quarter camera. Genuine pose changes; no whole-body squashing, stretching, per-frame auto-resizing, or joint-cutout animation. Allow believable foreshortening and fabric motion.
- One complete transparent RGBA PNG per pose, 512x512, roughly 384px standing body height. Do not shrink frames individually to fit the weapon. Keep the full silhouette inside the canvas.
- Use grounded foot-contact baseline y470 for the new set, matching approved idle. Older running previews use y432 and preliminary horizontal registration; do not inherit that baseline blindly. Airborne frames must retain meaningful root/pose offsets rather than snapping every foot to the floor.
- Running: shaft/blade lies behind the same holding-arm shoulder/head when appropriate; the attached guard and correctly oriented hand remain readable in front. Guard, handle, blade and tip must follow the same rigid weapon orientation. Tip points slightly toward the foreground. No drifting grip or changing teeth/length.
- Check idle -> start -> loop -> stop -> idle, takeoff -> ascent -> apex -> fall -> land, second jump -> fall, and dash -> air/guard. Include contact, passing and flight phases rather than eight variations of one stride.
- Export `sora_<animation>_00.png` onward, row-major `sora_<animation>_sheet.png`, and a looping GIF or video preview. Keep preview labels outside the actual transparent frames. Use four columns for eight frames or five columns for ten frames, with exact 512px cells and no internal padding.
- Include `manifest.json`: animation name, canvas, ordered filenames, proposed durations, loop flag, contact/root offsets and sheet rows/columns. Mark timing as proposed, not validated gameplay. If unable to create files/alpha/previews, state the limitation rather than claiming delivery.
- Optional metadata may record grip/tip positions; this does not require separate rendered layers. Inspect dark/light backgrounds, 128px downsample and mirrored facing.

Return each animation in its own folder. Suggested import destination when brought back to this repository: `design/sprites/smooth/sora/replacement_work/ready/<animation>/gemini_trial/`. Do not overwrite existing animations or modify Godot code/settings.

## Reference limits

The optional cycle guides include unfinished running artwork and a backward shimmy made from reversed forward poses. They are context, not quality or anatomy approval. Correct their jacket/arm joins, gait, timing, weapon transitions and root registration instead of reproducing defects.

No verified KH1 jump or KH2 Aerial Dodge gameplay footage is bundled. Verify those motion references before production; identify sources used and label the new drawings as adaptations. If references cannot be verified, keep those clips explicitly pending.
