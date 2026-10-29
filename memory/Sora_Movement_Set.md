# Sora movement animation set

**Fact or rule (October22):** Sora's movement animations are made at 384 x 384, in the approved sprite2d_v3 style, starting from the approved battle_v12 stance, using the PS2-model pipeline. Kvon added to the earlier list (crouch down/hold/up, step forward/back shimmies, run start/loop/stop, KH1 first jump + KH2 Aerial Dodge second jump):

- **Back-dash:** a short hop backwards, the SAME animation on the ground and in the air.
- **Forward air-dash:** separate from the back-dash.
- **Landing.**
- **Air poses:** one for rising to the apex of the jump and one for falling from the apex.

**References:** `design/references/air_movement/air_movement_ref_01-04.png`. Kvon supplied these four stills of another fighting-game character's jump/air poses ("Think of the reference photo as an example"). They are pose references only, not Sora's design. Kvon's mapping:
  - ref_01 = rising toward the apex.
  - ref_02 = the apex tuck, and also the brief transition pose before any air option that needs another input.
  - ref_03 = falling toward the ground.
  - ref_04 = back-dash.

**Air transition rule:** Pose 1 (rising) -> Pose 2 (brief tuck) -> the air option. This applies to back-dash, forward-dash and any other air movement that needs an extra player input.

**Why:** User additions to the movement list.

**Keyblade during movement (October22):** Kvon said "One-handed, but he holds up high when he's falling."

- **Default (steps, crouch, run, rise, tuck, dashes, landing):** right hand only, held low and behind him, pointing away from the opponent; the left arm is free to move like the references.
- **Falling (ref_03 pose):** the Keyblade is raised up high in that hand.

**Why:** User decision.

**Ground movement first, October22:** Kvon said "Start with the ground movement, then we can move to aerial".

**Step forward (walk_fwd) built, pending review:**
- **Build:** `build_sprite_pilot.py -- walk_fwd_v1` aliases to the one-handed battle_v2 stance (right-hand Keyblade low/back, left fist guard, body turned 30 degrees). It is an in-place 10 x 80 ms gait: half-stride .12 m, lift .06 m, swing 40% of the cycle; the foot nearer the travel direction steps first; one body dip per step. `walk_back_v*` reverses the direction (not built yet).
- **2D style:** `render_2d_style.py -- walk_fwd_v1 walk_fwd2d_v1` + `stylize_2d_frames.py`.
- **Godot:** 384px frames in `KingdomArena/assets/sora/walk_fwd_384/` (soles on row 353, same anchor (192,354) as the idle). New `scenes/sora_move_test.tscn` + `scripts/sora_move_test.gd`: battle idle by default, hold D/Right to step forward at 90 px/s (matches the planted-foot slide: 0.5 m/s x 180.5 px/m at 384px), R resets.
- **Verified:** 135 px moved in 1.5 s; planted feet hold their screen x within ~3 px (sub-frame jitter only).
- **Known:** the idle is two-handed (battle_v12) and the walk one-handed, so the grip visibly pops on start/stop; transition frames are not made yet.

**Walk correction, October22:** Kvon said "The speed should be a little faster. The walk should keep both hands on the Keyblade".

- **This overrides the one-handed grip rule for steps (walks).** The one-handed rule still applies to the other movements unless Kvon says otherwise.
- **`walk_fwd_v2` (current):** recipe walk_*_v2+ is based on the approved two-handed battle_v12 idle (wide guard crouch, both fists on the handle), so there's no grip pop between idle and walk. 10 x 65 ms (650 ms cycle); 2D: walk_fwd2d_v2.
- **Godot:** the 384px frames replace walk_fwd_384, and WALK_SPEED is 111 px/s (0.615 m/s x 180.5).
- **Verified:** 167 px in 1.5 s; planted feet within ~4 px.

Pending review.

**Why:** User correction.

**Shuffle correction, October22:** Kvon said: "For less awkward movement, Sora's legs should move towards and away from each other for each cycle. His shoulders also bounce at a lower rate."

- **`walk_fwd_v3` (current):** shuffle step. The front foot steps out (feet spread to about the idle width), then the back foot closes up to 0.56 m spacing. Step 0.34 m with 0.06 m lift, eased; one shoulder/body bounce per cycle (was one per step). 10 x 55 ms = 0.55 s.
- **Godot:** 112 px/s. 168 px in 1.5 s; planted feet hold except ~5 px creep at the weight hand-off.
- **Packaging fix:** `package_idle_loop.py`'s GIF timing check now allows the 10 ms GIF rounding.

Pending review.

**Why:** User correction.

**Natural shimmy, October22:** Kvon said the back leg appeared to drag. I suggested six fixes: weight shift, back-foot push-off, arced foot path, uneven step/hold rhythm, per-frame root motion, and a body bob on landing. He said "Do all suggestions".

- **`walk_fwd_v5` (current):** 9 keyed frames (70,55,55,70,70,50,50,60,70 ms = 550 ms): settle, front lift, reach, land+dip, weight shift with back heel up 20 deg, toe push-off 35 deg, high arc with body rise, toe-first landing, settle.
- **Root motion per frame (384px):** [0, 2.7, 3.6, 4.5, 16.2, 9.0, 9.0, 10.8, 5.4] px = 61.2 px per cycle, avg 112 px/s.
- **v4:** its heel-up frame sank the toes 6 px; v5 scales the toe reach x1.5.
- **Godot:** `sora_move_test.gd` now moves on the AnimatedSprite2D `frame_changed` signal by each frame's root motion (no constant speed). Verified: planted feet hold the exact same pixel; 167 px in 1.5 s.
- **Deleted file:** I removed the obsolete 10th walk frame `walk_fwd_384/sora_walk_fwd_09.png` (+ .import), my own earlier output; it is in git history.

Pending review.

**Why:** User request.

**Knee correction, October22:** Kvon said "He should have his knee move towards the middle of his torso and then back to its original position." `walk_fwd_v6` (current) blends the back leg's knee bend direction toward the body midline during its swing: per-frame amounts [0,0,0,0,.3,.7,1,.5,0], peaking at the arc, then back out by the landing. Timing, root motion and floor contact are unchanged. The Godot frames were replaced; feet still hold exactly. Pending review.

**Why:** User correction.

**Foot correction, October22:** Kvon said "The foot should move towards the torso with his knee."

- **v7:** pulled the swing foot toward the midline sideways (FOOT_IN .7). From the sprite camera that is mostly depth, so it was nearly invisible.
- **`walk_fwd_v8` (current):** the back foot comes forward and up under his hips at the arc (back keys: push-off .14/.09, arc .42/.18, landing approach .37/.04, then .34), then reaches back out to land. Also keeps v6's knee-in and v7's lateral pull.
- **Unchanged:** root motion and timing; feet still planted exactly in Godot.
- **Lesson:** judge "toward X" in screen space for this three-quarter camera.

Pending review.

**Why:** User correction.

**Walking video reference, October22:** Kvon supplied `design/references/walking/Recording 2026-10-22 135407.mp4` (163 frames, 30 fps, 556x504; another fighting-game character's walk; the clip is paused from about frame 85) as the reference for how the legs should move.

- **Reading the video:** Blender's VSE can export the frames (no ffmpeg/cv2 needed).
- **What the reference shows:**
  - Feet come nearly together under the hips, knees almost touching, legs straighter, body up.
  - The front foot steps far out to a wide stance, knees bent, body down, and holds.
  - The back foot skims in low beside it, with its knee travelling inward.
  - There are holds at both the narrow and wide ends.
- **`walk_fwd_v9` (current):** 12 keyed frames (770 ms), narrow 0.30 m / wide 0.80 m, step 0.50 m, low 2-3 cm foot skims, body bob +/-0.04 m (up narrow, down wide), knee-in on both legs.
- **Root motion (384px):** [0, 5.4, 12.6, 14.4, 9.0, 7.2, 9.0, 9.0, 10.8, 7.2, 5.4, 0] px, ~117 px/s.
- **Godot verified:** feet held exactly.
- **Replaces** the v8 high tuck (the reference keeps the foot low).

Pending review.

**Why:** User reference.

**60 fps game frames and seamless loop, October22:** Kvon asked what frame rate the walk is. Answer: variable holds of 60-80 ms, ~15.6 drawings/s average. He then said "Yes" to whole 60 fps game frames and "I want there to be no delay between cycles."

- **Rule now:** every Sora animation drawing is held a whole number of 60 fps game frames.
- **`walk_fwd_v10` (current):** 11 drawings, [4,4,4,4,5,5,4,4,4,4,4] = 46 frames (0.767 s). The duplicate closing hold is removed and every drawing has root motion [2.7,6.3,11.7,13.5,9.0,8.1,8.1,9.0,9.9,7.2,4.5] px (90 px per cycle, ~117 px/s), so the loop has no pause.
- **Idle in game frames:** [6,5,5,6,7,6,5,5,6,7] = 58 frames (was 1000 ms).
- **Godot:** `sora_move_test.gd` uses animation speed 60 with per-drawing game-frame counts. Verified with a 60 fps movie: drawings change on exactly those frame counts, and nothing holds longer than 5 frames.
- **Stale file:** `walk_fwd_384/sora_walk_fwd_11.png` (+ .import) from v9 is no longer loaded. Asked before deleting.

Pending review.

**Why:** User decisions.

**Slightly faster walk, October22:** Kvon asked about making the frame rate slightly faster and chose option A.

- **`walk_fwd_v11` (current):** same 11 drawings as v10 (pixel-identical), held [4,3,3,4,4,4,4,3,3,4,4] = 40 game frames (0.67 s), ~135 px/s. The root motion per drawing is unchanged.
- **Godot:** frame counts updated; verified in a 60 fps capture.
- **Packaging fix:** `package_idle_loop.py` now rounds GIF preview delays to the nearest 10 ms (Pillow truncated 66.7 ms to 60).

Pending review.

**Why:** User choice.

**Pasted walk spec, October22:** Kvon pasted a detailed spec for an 11-pose, 40-frame, 60 fps walk, implemented as `walk_fwd_v12` (current, pending review).

- **Root motion:** constant 2.25 game px per frame, i.e. 9.0 px per 4-frame drawing and 6.75 px per 3-frame drawing = 90 px per cycle, 135 px/s. The step length was rescaled to 0.4987 m so planted feet stay exact. Sprites stay in place and Godot applies the root motion.
- **Pelvis drop:** 6 render px on the passing poses (drawings 3 and 9), 3 px on the neighbours, 0 on the contacts; hands follow. Verified: head top rows 137 -> 143.
- **Weapon drag:** -8 deg about the vertical at the passing poses (half on the neighbours); the left hand follows the handle. There is no torso twist in the walk, so the sign is as written.
- **Front arm (R, nearer the camera):** abduction 12-15 deg about the shoulder-wrist line, with the forearm-jacket gap measured in screen space. **The 10-12 px gap is NOT achievable with the two-handed grip:** the elbow is already at its outermost screen position and every swing moves it inward; the best is ~0.5-4.5 px depending on frame. Reported to Kvon with options.
- **Feet:** planted. In Godot they hold within 1 px; that pixel is rounding from the 6.75 px moves.
- **Output:** `compose_white_sheet.py` builds `walk_fwd2d_v12_sheet_white_4x3.png` (2048x1536: 11 frames at 512, white, last cell blank, no text/grid), in the approved 2D style.

**Why:** User spec.

**Front-arm gap option 2 tried, October22:** Kvon chose option 2 (pull the front shoulder back and out, keep the grip). `walk_fwd_v13` searches the R_kata collarbone angle (yaw +-20, lift +-15 in 5-deg steps) before the arm solve.

- **Result:** the best was yaw 5 / lift -5 with a gap of only ~0.7 px. The short collarbone moves the shoulder joint only 2-3 cm, while ~5 cm of screen-sideways room is needed.
- **Not adopted:** v13 is an experiment. It was not exported to Godot; v12 stays in the game test.
- **Remaining ways to get the 10-12 px gap:** move the grip forward (option 1), turn the chest so the front shoulder rotates back, or relax the gap target. Asked Kvon.

**Chest-twist attempt, October22:** Kvon said to revert the collarbone change and get the 10-12 px gap by twisting the upper spine/chest 6-10 deg away from the camera on its local Z, moving the grip forward at most 2-3 cm if needed.

- **`walk_fwd_v14`:** built from v12 with no collarbone change. The search picked a 10 deg twist (direction moves the front shoulder away from the camera) + 2 cm grip forward; arm extension 0.876, not hyper-extended.
- **Result: the gap is still not reached.**
- **Lesson:** the vertex-weight gap metric is unreliable. Its 'torso' set (mune/hara > .5) is mostly the inner shirt; the jacket side panels beside the elbow are weighted to the shoulder/arm bones (see `walk_fwd_v14/Gap_Measurement_Points.png`). Use rendered-alpha negative space instead.
- **Alpha measurement:** background between the front arm and jacket is essentially none in both v12 and v14 (max 4-8 px in 1-2 rows near the hem).
- **Status:** v14 is an experiment; Godot stays on v12. Asked Kvon whether to exceed the limits.

**Chest-twist spec (15-22 deg, render-measured gap), October22:** Kvon pasted a spec: revert v13, twist the upper spine/chest 15-22 deg away from the camera on its local Z, measure open background in the final 512 output, require >= 10 px every frame, and no grip shift.

- **Lessons found along the way:**
  - On the KH2 rig `mune`'s local Z points sideways (world X). A local-Z rotation BENDS the chest back/forward instead of twisting it; v14/v15 did this. The twist axis up the spine is local X (`twist_axis='spine'`).
  - The battle_v12 `shoulder_reach` step swings the collarbone to keep the front hand on the grip and undoes shoulder changes; v16 sets `no_reach_side` for the front arm.
- **Result (v15 local Z; v16 spine axis, no front reach):** the front shoulder moves only ~0.5 px on screen across 15-22 deg, and the probe gap stays [0,4,7,12,10,11,10,0,0,0,0] px for every twist.
- **Why it can't work:** in this sprite view Sora faces nearly toward the camera, so the shoulders sit across the screen and a twist about the spine moves the front shoulder mostly in depth. That is invisible from the sprite camera.
- **Conclusion:** the twist cannot create the gap. v15/v16 are experiments; Godot stays on v12. Asked Kvon which constraint to relax.

**Front-arm flare (option 1) result, October22:** Kvon chose option 1, elbow flare in the screen plane. `walk_fwd_v17` tilted the front collarbone about the camera view axis (0-40 deg, front shoulder-reach off).

- **Result:** the shoulder moves UP (~11 px) and under 2 px sideways; the gap is unchanged up to 25 deg and closes completely past 30 deg.
- **The real cause:** in the three-quarter sprite view the front arm lies IN FRONT of the jacket, and the jacket's silhouette extends past the arm on both sides. White background can only appear if the elbow clears the whole jacket outline, ~20-30 px further out. That is impossible with the hand fixed on the handle.
- **Bug fixed:** the v17 report crashed because a Vector was stored in POSE; now a tuple. The fix was not re-run.
- **Output removed:** the incomplete walk_fwd_v17 folder (my own output) was deleted.
- **Status:** Godot stays on v12. Asked Kvon to choose between grip changes or a different readability goal (skin-vs-jacket contrast/ink line).

**Forearm readability by ink (option 1), October22:** Kvon chose option 1: separate the arm from the jacket by contrast/outline instead of a background gap.

- **Kept from v12:** the pose and grip are unchanged.
- **Scripts:** `export_limb_screen.py -- walk_fwd_v12 R` writes `Limb_Screen.json` (front shoulder/elbow/wrist pixels per frame). `stylize_2d_frames.py walk_fwd_v12 walk_fwd2d_v12_ink` adds a 2 px ink band on the jacket side and a 1 px lightened skin rim, only inside a 26 px capsule around the front forearm. It only runs for `*_ink` output names, so approved outputs are unchanged.
- **Result:** ~505-590 ink px and ~220-270 rim px per frame; mean luminance step across the boundary 97-101 (of 255).
- **`walk_fwd2d_v12_ink` (current):** 384px frames replace `KingdomArena/assets/sora/walk_fwd_384`, with the same v12 timing/root motion; Godot screenshot verified. Includes the white 4x3 sheet and `Forearm_Ink_Before_After.png`.

Pending review.

**Why:** User choice.

**Idle-to-walk + grounded walk spec (Goku reference), October22:** Kvon supplied `design/references/walking/Goku walk.gif` (very wide sumo-like guard, knees splayed, feet barely lifting) and a pasted spec. Answers to my questions: keep the approved forearm ink instead of a background gap; start the transition from the battle_v12 idle.

- **`walk_fwd_v18` (cycle, current):** extra crouch 0.12 m below the idle (grip sinks with it); stance along 0.68-1.04 m, lateral x1.2; knee splay .8; foot lift capped at 1 cm; 6 render px passing drop; pitch 3.5 deg on contacts to 0 on passing; 2 deg chest roll toward the weight foot; weapon +5 cm lag on passing / -3 cm on contacts; -8 deg drag; 12 deg elbow flare + forearm ink.
  - Timing: 40 game frames [4,3,3,4,4,4,4,3,3,4,4].
  - Root motion 65 px per cycle (6.5 / 4.875 px per drawing = 1.625 px/frame, 97.5 px/s).
- **`walk_fwd_v18t` (transition):** 4 drawings x 3 game frames, smoothstep blend of crouch/stance/pitch/splay/roll/hands from the battle idle into walk drawing 1, in place.
- **2D outputs:** `walk_fwd2d_v18_ink` (4x3 white sheet) and `walk_fwd2d_v18t_ink` (4x1 white sheet).
- **Measured:** hands are 0.8 cm (R) and 2.2-3.3 cm (L) from the handle line, same as approved v12. Note the report's `grip_error_L_m` ignores the v18 hand offsets and is NOT valid for v18. Floor rows 470-471.
- **Godot:** `sora_move_test.gd` now steps animation itself in `_physics_process` (60 ticks/s default, confirmed in docs), because `animation_finished` added a 2-frame hitch at the transition. New `walk_start_384` assets; walk_fwd_384 replaced.
  - Verified: holds exact (3,3,3,3 then 4,3,3,4,4,4,4,3,3,4,4 repeating); planted feet within 1 px.
- **Builder change:** the v13/v15-17 gap experiments are now limited to their own versions.

Pending review. Offered the matching brake transition.

**Why:** User spec and reference.

**Three-part spec (start / walk / brake), October22:** Kvon pasted a spec repeating parts 1-2 (already built as v18t/v18) and adding a 4-frame brake. The spec names the front arm L_ude1/L_ude2, but in this camera the front (nearer) arm is R; kept R. The forearm gap is still handled by ink, per his earlier choice.

- **`walk_fwd_v18b`:** the brake. It is the same blend as v18t with the weights reversed (walk drawing 1 -> battle idle), 4 drawings x 3 game frames, in place. It is pixel-identical to v18t played backwards. 2D: `walk_fwd2d_v18b_ink` with a 4x1 white sheet.
- **Godot:** new `walk_stop_384`. Releasing forward during walk_start or walk_forward plays walk_stop, then idle; pressing forward during the brake restarts walk_start. Timed demo option `--walk-demo-ticks=N`.
- **Verified sequence:** start 3x4, walk 40, brake 3x4, idle.
- **Known limit:** the brake starts from the feet-together contact pose, so releasing mid-stride (wide stance) snaps the feet. Contact-matched brake or finish-the-step options were offered.

**Why:** User spec.

**Contact-matched brakes, October22:** Kvon chose option 2.

- **`walk_fwd_v18w`:** a second brake that blends from walk drawing 5 (index 4, the wide-stance contact) into the idle, with its knee-in/weapon-drag values eased out. 4 x 3 frames, 4x1 white sheet; floor/grip verified.
- **Godot:** `walk_stop_wide_384`. On release, walk drawings [3,4,5,6,7] (0-based; feet >= 0.86 m apart) use walk_stop_wide; the others, and walk_start, use walk_stop.
- **Verified:** releasing at tick 52 (feet together) gives a first-brake foot span of 213 px; at tick 32 (wide) 257 px. Holds exact.
- **v18t/v18b unchanged:** the source-drawing generalisation is a no-op for drawing 0.

**Why:** User choice.

**Gemini review loop and Goku-style walk, October22:** Kvon asked me to share outputs with Gemini (Brave port-9222 profile, conversation "Refining Fighting Game Walking Animation", tab 153AE57B3E4E81CACF5502C58F17154B), respond to its prompts, and continue until a new walking cycle was created.

- **Helper:** `gemini_cdp.mjs` gained `--media text` (completes when a 'Gemini said' block follows our 'You said' and stays stable), reference sets walk-v18-package / walk-vs-goku / walk-v19-goku, and `design/models/sora/gemini_walk_review/round_NN` output folders. Rounds 01-03 are saved there.
- **Round 01:** Gemini approved v18 and asked for a retreat cycle plus Brake 3.
  - Built: `walk_back_v18` (11 frames, -1.5 deg pitch, toe-first plants, grip 2.5 cm in, NARROW0 .62, stance shifted -8 cm along the walk direction because the leading leg locked straight; +6 cm made it worse) and `walk_back_v18w` (Brake 3).
  - Also built `walk_back_v18t`/`v18b` (not requested, but needed to avoid pops).
  - Rendered and verified, NOT yet in Godot. Kvon paused the retreat.
- **Round 02:** Kvon wants the forward walk to look like `design/references/walking/Goku walk.gif` (frame sheet `Goku_walk_frames_4x3.png`). Gemini gave a Goku-style prompt.
- **`walk_fwd_v19` (current forward-walk candidate):**
  - Inverted bounce: high with feet together, -7 cm at wide contacts (head rows 173-188).
  - 2.5 cm lateral pelvis shift; 7 cm stomp arcs with fast drop; extra knee splay at the low point.
  - hara +5 / mune +11 hunch; 12.5 deg spine twist toward the stepping leg; 6 deg roll; 8 deg shoulder shrug.
  - kubi -13.5 pitch plus counter-yaw; grip 4.5 cm in; weapon lag +6/-4 cm; blade sweeps with the twist.
  - NARROW0 .58 (the trailing leg locked at .68).
  - Outputs: GIFs `Walk_Cycle.gif` and `Goku_vs_Sora_v19.gif`.
- **Round 03:** Gemini approved v19 ("perfect adaptation"). It requested v19 start/brake transitions and a v19-style retreat. NOT started (the loop goal was met); asked Kvon.
- **Godot:** still uses the v18 walk and transitions, which match each other. v19 needs its own transitions before integration.

**Idle shuffle adopted for the walk, October22:** Kvon asked what the absolute easiest walk would be while keeping the idle pose and screen angle; I suggested an "idle shuffle". He interrupted the v19 check and said "Do the idle shuffle you suggested".

- **Recipe:** `build_sprite_pilot.py -- shuffle_fwd_v2` / `shuffle_back_v2`.
  - The battle_v12 upper body is unchanged, with the idle's BREATH values frozen at idle frame 1 (lag .1355), so drawing 1 matches the idle (max pixel diff 7/255).
  - The lead foot slides 0.22 m forward, then the back foot follows; lifts 1.2-1.8 cm.
  - The body sits midway between the feet, giving exact planted feet.
  - Hips dip up to 3 cm while the feet are spread, so the legs reach (grip sinks with them). v1's 0.28 m step locked both legs straight from the already-wide idle stance.
- **Timing:** 7 drawings x 4 game frames = 28 frames (0.467 s). Root [0.99,4.96,8.93,5.96,5.96,8.93,3.97] px at 384 (39.7 px per cycle, ~85 px/s). Back is mirrored.
- **2D:** `shuffle2d_fwd_v2` / `shuffle2d_back_v2`, same style as sprite2d_v3 (no forearm ink, to match the idle). 4x2 white sheets, GIFs.
- **Godot:** `sora_move_test.gd` now uses idle + shuffle_forward + shuffle_back only (D/Right forward, A/Left back). The shuffle starts straight from the idle; on release it finishes the cycle and then stands (no transitions/brakes needed). Verified: exact 4-frame holds, planted feet pixel-exact, clean stop.
- **Shelved:** the v18/v19 walk sets and their transitions/brakes stay on disk but are not used. The v19 transitions and retreat built in the background were not reviewed.
- **Known:** starting while the idle is mid-bounce can pop the upper body by up to the idle bounce (~4 px at 384).

**Faster shuffle, October22:** Kvon said the shuffle was too slow and didn't cover enough distance, then asked me to get Gemini's suggestions.

- **`shuffle_fwd_v3` / `shuffle_back_v3` (current in Godot):** 0.30 m step, hip dip 7.5 cm (6 cm left both legs fully straight at the widest point), holds [3,3,3,4,3,3,3] = 22 frames.
- **Root px:** [1.35, 6.77, 12.18, 8.12, 8.12, 12.18, 5.42] = 54.1 px per step, ~148 px/s (was 40 px / 85 px/s).
- **Verified in Godot:** exact holds, planted feet pixel-exact, clean stop both ways.
- **Gemini round 04 suggestions** (`gemini_walk_review/round_04`), NOT implemented yet; asked Kvon:
  - ~75 px per step over 18 frames (holds [3,2,2,4,2,2,3], ~250 px/s); step 0.42-0.45 m.
  - Foot lift 4.5-5 cm so it steps instead of skating.
  - Hip dip 9-10 cm; knee poles 3-4 cm further out on the widest drawings.
  - Upper body stays locked.

**Shuffle speed, October22:** Kvon said "Do the ones that make him faster and nothing else" (Gemini's speed suggestions only).

- **v4 test** (75 px per 18-frame step, 250 px/s) needed a 16 cm hip dip for leg reach (11 and 14 cm left the legs straight), so the head bobbed 38 px. Preview kept in `shuffle2d_fwd_v4_dip16`; not adopted.
- **Kvon then asked for a middle point between v3 and v4: `shuffle_fwd_v5` / `shuffle_back_v5` (current in Godot).**
  - 64.5 px per step, holds [3,3,2,4,2,3,3] = 20 frames, ~193 px/s; hip dip 11 cm (smallest keeping the knees bent, leg extension 0.684/0.693).
  - Root px [1.61, 8.07, 14.51, 9.67, 9.67, 14.51, 6.44]; head rows 137-163.
  - Feet lift and knees unchanged.
  - Verified in Godot: exact holds, planted feet pixel-exact, clean stop both ways.
- **Builder:** optional 3rd CLI argument = shuffle v4+ hip dip (m), e.g. `-- shuffle_fwd_v5 shuffle_fwd_v5 .11`.
- **Kvon approved v5:** "I like this. Continue with the other animations".

**Crouch grip, October22:** asked whether the crouch should be two-handed like the idle/walk or follow the one-hand movement rule; Kvon chose **"One hand"**. The left hand lets go of the handle as he crouches (free guard fist) and grabs it again as he stands; the Key goes low and behind him in the right hand, pointing away from the opponent (screen left).

**Why:** User decision.

**Crouch built, October22 (pending review):** `build_sprite_pilot.py -- crouch_down_vN` / `crouch_hold_vN` (current **v4**), from the battle_v12 idle with the idle breath frozen at frame 1 (like the shuffle), feet planted, no root motion.
- **Pose:** hips 32 cm lower than the idle, +9 hunch / +10 lean / -12 neck, knee splay .6. Head top 140 -> ~221 at 512 (about 76% of standing height).
- **Grip:** the right fist keeps the idle grip and turns rigidly with the Key (the forearm takes half the roll); the Key yaws round BEHIND him to point low toward screen left with the tip ~14 cm off the floor. The left hand stays on the handle for the first part, then lets go to a guard fist at the chest.
- **History:** v1 was too shallow (head down ~55 px); v2 hid the fist at knee height behind the thigh; v3's hold loop put the tip at the frame's left edge. v4 angles the blade further behind (CR_BEHIND 1.4).
- **Timing:** crouch_down has 7 drawings [2,1,1,1,2,2,3] = 12 game frames; crouch_hold is an 8-drawing bounce loop [6,5,5,7,6,5,5,7]; crouch_up is crouch_down backwards [3,2,2,1,1,1,2].
- **2D:** `crouch_down2d_v4` / `crouch_hold2d_v4`, with white sheets, `Idle_Crouch_Idle.gif` and `Crouch_Hold_Loop.gif`.
- **Godot:** `crouch_down_384` / `crouch_hold_384`, S/Down in `sora_move_test.gd`. Crouch wins over walking; mid-step he finishes the step first. Releasing or re-pressing mid-transition turns around from the matching drawing. New test flag `--crouch-demo-from=M`.
- **Verified (60 fps movie):** exact holds for all transitions.
- **Known:** the last crouch_down drawing is at 96% of the blend, so the tip settles ~27 px into the hold.

**Run plan with Gemini, October22:** after the old D: drive failed, the project was re-cloned from GitHub to the new Kingston flash drive at the same path, `D:\KH Fighting Game`. The system Node v24.14.0 now runs `gemini_cdp.mjs`; the old project-local `.local/` Node and browser profile were lost, and Kvon signed in again on a fresh profile.
- **Gemini round 05** (`gemini_walk_review/round_05`): run spec.
  - Speed ~540 px/s (180 px per 20-frame cycle).
  - Loop: 8 drawings [2,3,2,3,2,3,2,3] (contact/down/passing/flight per leg).
  - Start: 4 drawings [2,2,3,3]. Stop: 5 drawings [2,3,3,3,3] (wide plant, lean back, Key swept forward, regrip, settle).
  - Hunch ~8/20, alternating chest twist, free left arm in opposition, Key behind the hip pointing back at -10 deg with a lagged bounce.
- **Run control:** Kvon chose **double-tap forward** (tap D/Right twice and hold to run; a single press still walks).

**Why:** User decision; Gemini support requested by Kvon.

**Run built with Gemini, October22 (pending Kvon's review):** `build_sprite_pilot.py -- run_start_vN / run_loop_vN / run_stop_vN` (current **v5**).
- **Body and grip:** turns from the idle's -25 deg to +30 deg (three-quarter toward screen right). The right fist keeps the idle grip rigidly, with the Key low behind him (~30 deg out toward the camera, -27 deg pitch). The left hand is a free swinging fist.
- **Loop:** 8 drawings [2,3,2,3,...], 180 px per 20 frames (~540 px/s).
  - Contact +0.35 / -0.15 m; down; passing with the swing foot at -0.06 m lifted 0.20 (at 0.0 the shoes stacked on screen); flight reach +0.25.
  - Hip drop from standing 0.14 / 0.16 / 0.08 / 0.04 m.
  - Lean hara 12 / mune 24 total (Gemini's 8/20 read upright from this camera).
  - Root per half [0.09, 0.12, 0.16, 0.13] m.
- **Gemini rounds:**
  - 06 critiqued v3: too much lean/bounce, butt-kick, short stride, blade.
  - 07 approved v5 and gave the start/stop tables. Its numbers assumed a ±0.27 m idle stance (Sora's is ±0.44), so the foot positions were refit.
- **Start:** 4 drawings [2,2,3,3]. The left foot stays planted while he turns, dips, releases the left hand, sweeps the Key behind him and drives the right knee up. It ends on loop drawing 3 (passing) and hands over to loop index 3.
- **Stop:** 5 drawings [2,3,3,3,3], triggered only at the end of the loop (left foot about to plant), so release waits up to ~20 frames.
  - The left foot plants wide and skids 1 cm onto the idle spot; hips 0.26, lean back; the right foot stays planted then steps back.
  - Key swept forward, left hand regrips by w=.65; root [.15, .08, .04, .01, 0].
- **Godot:** `run_start_384` / `run_loop_384` / `run_stop_384`.
  - Double-tap D/Right within 15 game frames and hold. A tap that has started a shuffle snaps into run_start.
  - New flags `--run-demo-ticks=N` and `--trace` (prints every drawing change).
  - Verified by trace: exact holds through start -> loop -> stop -> idle. Planted shoes are pixel-exact contact-to-down; on the heel-up passing drawing the toe tip shifts ~4-5 px at 384.
- **Clone note:** the flash-drive clone needs `core.autocrlf=false` (set locally). Godot writes LF, and CRLF checkouts made every `.import` and `project.godot` look modified; their contents were identical to HEAD.
- **Previews:** `run_loop2d_v5/Idle_Run_Stop.gif`, `Run_Moving.gif`, `Run_Cycle.gif`; `blender_workflow/make_motion_gif.py`.

**Run matched to Gemini's generated poses, October22 (current; pending Kvon's review):** Kvon had Gemini generate an 11-pose running sheet (saved as `gemini_walk_review/round_09/gemini_original_preview.jpg`) and asked me to use it as the reference, going back and forth with Gemini.
- **Round 08:** suggestions on the v5 run. Gemini's start->loop velocity claim was wrong (it ignored the frame counts).
- **Round 10:** Gemini turned its poses into numbers: static arms, blade back and up, steeper lean, heel kick, less bounce.
- **v6/v7:** v7 overshot (lean 68 deg, hips too low).
- **Round 11:** Gemini's corrections; met part way, since its numbers understate its own picture.
- **Round 12:** Gemini said **"Matches"** for loop v8.
- **Round 13:** start/brake approved except the brake hip drop.

**Current set:**
- **Loop** `run_loop_v8`:
  - hara 26 / mune 30 / neck -40 total; hip drop .16/.20/.12/.10.
  - Contact +.38, passing swing -.06 lifted .20; the push-off leg leaves the ground at flight and stays kicked back (-.30, lift .14-.20).
  - Static arms: guard fist at the ribs; right fist behind the hip; blade back, toward the camera, +6 deg.
  - ~594 px/s (root per half .13/.13/.17/.12).
- **Start** `run_start_v9`: the blade reaches its carry angle sooner (`blade_s = w*1.25`) so the tip stays in the frame.
- **Brake** `run_stop_v10`: hip drop .20 (was .26). Holding the blade toward the camera longer (run_stop_v9) pushed the tip out of the frame, so it was not used.
- **Godot:** run_start_384 / run_loop_384 / run_stop_384 replaced.
- **Verified:** trace holds exact; planted shoe within 1 px contact->down (toe shifts ~4-5 px at 384 on heel-up); protected files unchanged.
- **Previews:** `run_loop2d_v8/Idle_Run_Stop.gif`, `Run_Moving.gif`.
- **Still open from round 08:** mirrored right-foot brake (removes the up-to-20-frame release wait) and locking the toe on the heel-up drawing. Not started; Kvon hasn't chosen.

**Run rebuilt for a natural sprint, October22 (current; pending Kvon's review):** Kvon said the v8 run "doesn't match the poses Gemini generated at all" and asked what would make it natural.
- **Lesson:** Gemini's earlier "Matches" (round 12) was wrong, and I had accepted it without comparing the pictures myself. From now on, judge by side-by-side boards (`Reference_vs_vN.png`) and by measured on-screen angles, not by Gemini's approval or the rotation numbers.
- **Round 14 (strict) causes:**
  - body turned too far toward the camera, hiding the legs;
  - no forward knee drive;
  - crouched too low;
  - weight behind the front foot.
- **v11-v15:**
  - turn +48 (+50 = exact profile on this camera; Gemini's +60-70 would show his back);
  - hips high (.09 / .12 / .04 / .02);
  - knee drive; heel kick-back in flight;
  - head lifted so the face profile shows (turning it toward the camera looked like "checking a blind spot").
- **Round 16:** the jacket and shorts swallow the lean, so a 42 deg rig lean measures only 22-26 deg on screen. The builder now logs `screen_back_deg` (tailbone -> neck base, projected).
- **`run_loop_v17` (current loop):**
  - hunch +19 / pitch +23 / neck -54 extra; measured back angle 45-49 deg on screen (Gemini's poses ~45-50).
  - Passing knee cheated forward through the shorts: foot +0.10, lift 0.28, toes down 45.
  - Flight scissor: trail -0.38 lifted 0.21, reach +0.36 (+0.40 was out of reach and locked the leg).
  - Contact hips 0.12, trail -0.35; blade +18 deg (continues the back leg's line); guard fist forward.
  - Root per half .12 / .12 / .18 / .13 (~594 px/s). Planted shoes exact contact -> down.
- **Gemini round 17:** "Matches". By my own eye it is much closer; its poses still lift the passing knee and the back foot a bit higher.
- **Start/brake:** `run_start_v18` (roots spread .06 / .11 / .15 / rest, no 48 px jump) and `run_stop_v18` (right-foot plant clamped to -0.36 m so the leg doesn't lock).
- **Godot:** start v18 / loop v17 / brake v18 exported; trace holds exact. Preview `run_loop2d_v17/Idle_Run_Stop.gif`.
- **Test folders:** run_loop_v12_look-20 / look20 (head-turn sign test) and run_loop_v15_m / v16_m (angle measurements).

**Glide instead of run, October23:** Kvon said "Instead of running, I want sora to glide across the screen low to the ground. Have Gemini create art of this first and show it to me."
- The double-tap forward move becomes a low ground glide. The v17/v18 run stays on disk but is superseded.
- **First step:** Gemini concept art, shown to Kvon before any 3D build (`gemini_walk_review/round_18`).

**Why:** User decision.
- **Round 18 art:** 7 poses: push-off, a full-plank horizontal glide skimming the floor with dust, a skid landing into a two-handed guard. Kvon: the rule breaks (Key pointing forward on one glide pose and in front on landing; 7 poses instead of 8) "are fine for now". He asked Gemini for another pose with a more relaxed glide posture instead of a full plank (round 19).
- **Round 19 art chosen:** Kvon: "Use this relaxed pose for the glide loop, keeping the push-off and skid landing from the first sheet."
- **Glide built (October23; pending Kvon's review):** `build_sprite_pilot.py -- glide_start_vN / glide_loop_vN / glide_stop_vN` (current **v6**). GLIDE maps onto the run machinery as run v18, with its own poses.
  - **Loop:** 6 drawings x 3 frames, gentle hover bob, constant 30 px per drawing (600 px/s), no planted feet.
    - Three-quarter turn +20 deg; on-screen back angle 42-45 deg; hips 0.17 m.
    - Near (right) leg trails at -0.44 m, 0.05 m up; far knee tucked at -0.08 m, 0.20 m up.
    - Left hand loose out behind; Key low at the right hip angled forward-down, as drawn (Kvon accepted the rule break for now).
  - **Push-off:** [2,2,3,3]: dip, the back foot pushes off on its toe with the front knee up, tips into the glide; root ramps 3.6 -> 28.9 px.
  - **Skid landing:** [2,3,3,3,3]: feet down wide (+0.40 / -0.42), hips 0.30, skids with the feet sliding (root 30 / 18 / 9 / 3.6 / 0), both hands regrip, rises into the idle.
- **Gemini round 20:** critique of v4. Not taken: "left hand forward" and "blade backward", which contradict its own drawing. Its claim that the trailing leg was locked straight was false (0.56 of 0.69 m measured).
- **Godot:** the glide replaces the run on double-tap forward (`glide_*_384`, `--glide-demo-ticks=N`). It enters loop drawing 1 after the push-off and lands after any loop drawing on release. Trace verified.
- **Preview:** `glide_loop2d_v6/Idle_Glide_Stop.gif`; boards `gemini_walk_review/round_20/Relaxed_Glide_vs_v4/v5/v6.png`.

**Obsolete animation folders deleted, October23:** Kvon: "delete the folders housing obsolete animations"; then "Approved, but don't remove the .import files".
- **Kept in `design/models/sora/` (current finals):**
  - battle_v12 + sprite2d_v3 (idle)
  - shuffle_fwd/back_v5 + 2D v5
  - crouch_down/hold_v4 + 2D v4
  - glide_start/loop/stop_v6 + 2D v6
  - plus blender_workflow, downloads, gemini_walk_review, gemini_animation, pose_edit, character_blockout_v6-v9, README.md.
- **Deleted (177 folders + Alignment_Review_v18.json):** older battle / idle_loop / one_hand / sprite_pilot / sprite2d v1-v2 / sheet2d / sheet_battle versions; every walk_* and run_* folder; shuffle v1-v4; crouch v1-v3; glide v1-v5.
- **Godot `assets/sora`:** images deleted from idle_battle, idle_battle_192/256/320, walk_fwd/start/stop/stop_wide_384 and run_start/loop/stop_384. Their `.import` files were KEPT, as Kvon instructed, so those folders now hold only orphan .import files.
- **Recovery:** everything deleted is recoverable from git commit f429bfd. Version notes above that name deleted folders refer to that history.
- **Not touched:** the old hand-drawn pipeline in `design/sprites/smooth/sora/replacement_work/` (still used as reference images); ask before cleaning it.

**Why:** User request.

**Glide v9 (October23; current, pending Kvon's approval):**
- **Round 21:** Gemini compared v6 with its art and made six suggestions. Kvon: "Apply all of them" and said v6 showed only the side profile. Asked to choose, he picked **"Pure side profile"** (not chest toward the camera).
- **v7:** all six fixes applied:
  - turn +55;
  - landing drawings 1-2 lean back (hara+mune about -18 deg total, measured -22 on screen) with hips 0.16;
  - push-off drawing 4 is a full stretch (back foot planted at -0.45, torso about 56 deg on screen);
  - loop legs near -0.35 / 3 cm up and far -0.15 / 12 cm up;
  - blade -30 deg tucked flat to his side (5 deg flare); left elbow bent.
- **v8:** +55 showed his back, so +50 = exact profile. The tucked blade ran to the frame edge, so the hand moved back and the blade went to -36.
- **v9:** the hand raised so the blade tip stays above the floor line.
- **Exported to Godot** `glide_*_384` (same holds and root motion); trace verified.
- **Preview:** `glide_loop2d_v9/Idle_Glide_Stop.gif`, board `gemini_walk_review/round_21/Relaxed_Glide_vs_v9.png`.
- **Cleanup pending:** glide v6-v8 folders are obsolete once Kvon approves (see Obsolete_Animation_Cleanup.md).

**Why:** User decisions.

**Glide consensus with Gemini, October23:** Kvon: "Communicate back and forth until you both come up with consistent instructions."
- **Process:** round 22 (strict) still misread my render; round 23 used large per-part boards plus my literal description and a draft list (AGREE/CHANGE per item); round 24 was **CONFIRMED**.
- **Agreed list** (`gemini_walk_review/round_24/submitted_prompt.txt`):
  - **L1.** Loop three-quarter, chest toward the viewer (~+20 deg), NOT pure profile. This reverses round 21 and Kvon's "Pure side profile" choice, which was based on Gemini's round-21 advice.
  - **L2.** Key low at the right hip, blade forward-down.
  - **L3.** Left arm trailing behind, elbow almost straight.
  - **L4.** Soft knees, feet behind/below, a few cm up.
  - **L5.** Back 40-45 deg off vertical.
  - **P1.** Push-off: drawing 1 dip; drawings 2-3 deep lunge, back leg pushing off.
  - **P2.** Key raised behind the shoulder on drawings 2-3 (Gemini's pose 2), swung to forward-down on drawing 4.
  - **S1.** Landing drawings 1-2: wide low stance, torso nearly upright (drop the v7-v9 lean-back).
  - **S2.** Both hands on the Key from landing drawing 1, low in front, blade forward-down.
  - **F1.** Face toward screen right throughout (seen in three-quarter with the body).
- Not built yet; reported to Kvon.

**Glide v10 built from the agreed list (October23; current, pending Kvon's approval):**
- **Loop:** v6's three-quarter pose (+20), the left arm trailing behind with a straighter elbow, face toward screen right.
- **Push-off drawings 2-3:** deep lunge (back foot planted on its toe at -0.45 m, front knee bent) with the Key raised BEHIND the shoulder; it swings to forward-down on drawing 4. `apply_run` now accepts a per-drawing `blade_dir`; big turns go round behind him.
- **Landing:** an upright, wide, low skid with BOTH hands on the Key from drawing 1, blade forward-down, rising into the idle.
- **Godot:** glide_*_384 replaced; push-off root [3.61, 14.44, 18.05, 28.88]; trace verified. Preview `glide_loop2d_v10/Idle_Glide_Stop.gif`.
- **Gemini round 27** (images actually attached): all ten agreed items MET.

**Lesson - Gemini never saw my images in rounds 05-26:** `gemini_cdp.mjs exchange` only uploaded a `--reference-set` when `--attach-references true` was also passed, and I never passed it. Every "comparison", "matches" and misdescription of my renders from those rounds (run v5-v17, glide v4-v9) was Gemini working from my text alone.
- **Fixed:** a named reference set now uploads by default (opt out with `--attach-references false`).
- **Always check:** confirm uploads in the chat screenshot (thumbnails on my message) or with `inspect` (new 'reference' images) before trusting a visual critique. Gemini downsizes uploads to 1024 px wide, so keep boards no wider than about 2:1.

**Why:** Root cause found when Gemini said the images were missing (rounds 25-26).

**Glide angle and arm attempts, October23 (attempts 1-25 = glide_loop v11-v35; Kvon picked attempt 24 = v34):** Kvon asked for a new glide changing only the facing angle in small steps, showing each result before the next. Steps:
- **Body turn:** v10's +20 went to +10, 0, then -10 (attempt 3, kept). Head turned back +10 relative to the body (attempt 4).
- **Keyblade arm:**
  - extended behind him (attempt 5); the blade aim is camera-relative so it stays in frame;
  - straight wrist (attempt 6): the hand rolls only about the forearm (`wrist_roll`, search keeps the Key in frame on every drawing);
  - wrist rolled 20 deg so the teeth show (attempt 7);
  - elbow straighter, hand 4 cm further back (attempt 8). The hand bob is off, so the Key doesn't flicker.
- **Left arm:**
  - forward into view (attempt 9); fist lowered twice (attempts 10-11);
  - arm rotated down at the shoulder (attempts 12-13); hand in front of the raised leg (14); elbow straighter (15); elbow tucked toward the torso (16); arm behind the raised leg (17);
  - shoulder raised (18); forearm across the front of the torso (19); elbow pointed forward (20); forearm lowered (21); hand away from the torso (22, mostly toward the camera); shoulder lowered (23: +4, then 24: -4 deg).
  - Attempt 25 (forearm extended along its own line) only foreshortened it toward the camera; Kvon chose to keep 24.
- **Builder bug fixed:** block order - v27's arm block ran after v28's, so attempt 18's 5 cm hand raise never applied.
- **Builder features:** `L_shrug_deg` (left collarbone), `L_elbow_hint_world` (elbow direction), per-drawing `wrist_roll`.
- Push-off/landing not yet rebuilt for this pose; Godot still has glide v10.

**Final glide approved, October23:** Kvon answered "Yes" to attempt 24 as the final glide.
- **Final set:** glide_start_v34 / glide_loop_v34 / glide_stop_v34, plus their 2D versions.
  - The push-off's last drawing uses the loop's arm setup (straight Keyblade wrist, forward left elbow, lowered shoulder) so it hands over without a pop.
  - The landing regrips with both hands (wrist_roll cleared).
- **Godot:** glide_*_384 exported; holds and root unchanged; trace verified. Preview `glide_loop2d_v34/Idle_Glide_Stop.gif`.
- **Known:** the Key jumps from behind him (loop) to low in front (landing drawing 1) as both hands regrip; the earlier glide versions had the same jump.
- **Cleanup** (per Obsolete_Animation_Cleanup.md): deleted 78 obsolete glide folders (v6-v33, v35, start/stop v6-v10). Recovery commits 3cb2859 (attempts) and df38942 (final).
- **Push-off fix, October23:** Kvon said the idle-to-glide transition wasn't smooth ("a frame or two where Sora is holding the Keyblade up in the air behind him"). Those were push-off drawings 2-3, raised behind the shoulder per agreed item P2.
  - **Fix:** `glide_start_v34d` (builder: `-- glide_start_v34 glide_start_v34d`). The lunge legs are kept; the hand and blade ease from the idle grip toward the loop's measured straight-wrist Key direction, with no raise.
  - Exported to Godot `glide_start_384`; trace verified. Preview GIF regenerated.
  - Leftover failed output folders: glide_start_v34b and v34c (a safety check blocked my rm). Delete them in the next cleanup.
- **Kvon approved the smooth push-off ("Yes"), October23.** Cleanup: deleted glide_start_v34 / glide_start2d_v34 (old raised-Key push-off) and the failed glide_start_v34b / v34c.
- **Final glide set:** glide_start_v34d, glide_loop_v34, glide_stop_v34, plus 2D versions. Recovery commit 71b2e6e.

**Back-dash started, October26:** Kvon said "Yes" to the back-dash and "Reconnect to Gemini". Brave relaunched (its debug port took longer than the launcher waits); Gemini was signed in, in Pro mode, on the walking conversation.
- **Round 29:** sent ref_04 plus the idle and glide sprites (all three images confirmed uploaded) and asked for a back-dash concept sheet.
- **Gemini refused:** "I cannot fulfill this request. I am unable to generate the back-dash concept sheet as requested because I cannot generate images directly." The same conversation generated images in rounds 18/19.
- Not retried, per the Gemini workflow rule (stop and report service refusals). Asked Kvon how to proceed.
- **Round 30 (Kvon chose "try Gemini once more"):** selected Upload & tools -> **Create image** (the composer shows "Describe your image" and an Images chip) and resent the same request with the three images. Reply: **"Sorry, something went wrong. Please try your request again."** No image. Stopped after this one retry and asked Kvon.
- **Round 31 (Kvon: "Refresh the page and try again"):** reloaded the tab (local CDP Page.reload), re-selected Create image and resent. Gemini returned a 4-pose back-dash concept (`gemini_walk_review/round_31/gemini_original_preview.jpg`):
  1. takeoff: crouch-push with dust, two-handed;
  2-3. backwards hop: knees tucked, right hand holding the Key low/back, left fist at the chest;
  4. landing: wide two-handed stance.
  - It added text labels I asked it to leave out. Shown to Kvon.

**Pivot to aerial movement, October26:** Kvon judged the round-31 sheet "matches that of a standard jumping animation rather than a quick backstep" and said "pivot to the aerial movement from this and come back to the back-dash later".
- The back-dash is paused (its ground=air rule still stands).
- The round-31 sheet becomes the jump reference. Planned first jump (KH1-style):
  - takeoff = sheet pose 1;
  - rising = sheet pose 2 / ref_01;
  - apex tuck = sheet pose 3 / ref_02;
  - falling = ref_03 with the Key raised high (Kvon's rule);
  - landing = sheet pose 4.
- The second jump (KH2 Aerial Dodge) and the forward air-dash come later.

**Why:** User decision.
- **Jump control (test scene):** Kvon chose **W / Up** to jump.
- **Jump drawings built (October26; pending Kvon's review):** recipe `jump_<start|rise|apex|fall|land>_vN` (JUMP on the run machinery, in place, turn -10 like the glide). Current: start v2, rise v2, apex v3 (v2's .blend save failed on the flash drive), fall v3, land v2, plus 2D versions.
  - **start** [2,2,2]: crouch, push through the toes as the left hand lets go, leave the floor.
  - **rise** [4,4]: front knee driven high, back leg hanging, Key low behind.
  - **apex** [6]: both knees tucked.
  - **fall** [4,4]: legs reaching down, Key raised high and angled toward the camera so it fits the frame (v1/v2 clipped the top).
  - **land** [3,3,4]: wide crouch, both hands on the Key, rising to the idle.
  - Review sheet: `jump_fall2d_v3/Jump_All_Drawings.png`. Not in Godot yet.
- **Landing elbow fix, October26:** Kvon said "The elbow holding the keyblade is bent too far inward in the landing poses."
  - Elbow-hint variants (land v3 out/down/cam/back) barely changed anything.
  - **Root cause (found with an idle-check render through the run machinery):** IDLE_R['hand'] was the idle's AIM point. The real idle's fist settles elsewhere after the wrists are squared, so every RUN-machinery blend from the idle put the grip further across his body.
  - **Fix (JUMP only):** IDLE_R['hand'] = the real idle's measured hand_point. The rebuilt idle now differs from battle_v12 frame 0 by 1.7k pixels (was 8.2k).
  - **land v5** (also upright chest, hands only 3 cm lower than the crouch) and **start v4** rebuilt.
  - The glide/run blends have the same old offset (approved, not rebuilt).
  - Test folders: jump_land_v3_down/cam/back, jump_idlecheck, jump_idlecheck2 (apex by mistake), jump_b_idlecheck.
  - Current set: start v4, rise v2, apex v3, fall v3, land v5. Sheet `jump_land2d_v5/Jump_All_Drawings.png`.
- **Takeoff 3 elbow, October26:** Kvon asked to isolate the takeoff poses (`jump_start2d_v4/Takeoff_Poses.png`, plus `jump_land2d_v5/Landing_Poses.png` made first by mistake), then "Straighten the elbow holding the keyblade a bit in takeoff 3". **jump_start_v5:** takeoff 3's fist reaches ~6 cm further down and back. Sheets `jump_start2d_v5/Takeoff_Poses.png`, `Takeoff3_before_after.png`.
- **Takeoff 1-2 elbow bend, October26:** Kvon: "Add a few more degrees to the angle at which both takeoff 1 and 2 are bending their elbow." Read as MORE bend. **jump_start_v6:** grip raised ~5 cm toward the shoulders in takeoff 1 and 2 (hz +.05); takeoff 3 unchanged from v5. Sheets `jump_start2d_v6/Takeoff_Poses.png`, `Takeoff1_2_before_after.png`.
- **Correction, October26:** Kvon: "keep the changes for 1 and instead apply the prompted changes to 2 and 3. I meant less bend in the elbow instead of more bend." **jump_start_v7:** takeoff 1 = v6's extra bend; takeoff 2 grip ~5 cm below its v5 height (hz -.05) and takeoff 3 a further ~4 cm down (straighter elbows). Sheets `jump_start2d_v7/Takeoff_Poses.png`, `Takeoff2_3_before_after.png`.
- **Keyblade toward the player, October26:** Kvon: "Rotate Sora's wrist in the last three images so that the keyblade is pointing towards the player. Increase the angle of rotation between each image." The last three images are takeoff 3, rising 1 and rising 2; "the player" = the camera/viewer.
  - Builder helper `toward_cam(b, deg)` rotates a blade direction toward the camera.
  - **jump_start_v8:** takeoff 3 at 20 deg. **jump_rise_v3:** 40 and 60 deg. The Key reads progressively shorter (foreshortened) as it turns toward the viewer.
  - Sheets `jump_start2d_v8/Takeoff_and_Rising.png` and `Takeoff_and_Rising_v7_vs_v8.png`.
- **Progressive elbow straightening, October26:** Kvon: rising 1's Keyblade elbow straighter than takeoff 3, then "rising 3" (there are only two rising drawings, so read as rising 2) straighter still. **jump_rise_v4:** fist further down and back (hand back -.22 / -.26, hz -.14 / -.20); the 40/60 deg turn toward the player is kept. Sheets `jump_rise2d_v4/Elbow_progression_before_after.png`, `Takeoff_and_Rising.png`.
- **Rising 2 bend, October26:** Kvon: "Give rising 2 slight more bend, but still less than rising 1." **jump_rise_v5:** rising 2's fist halfway between v4's rising 1 and rising 2 (hand back -.24, hz -.17). Sheets `jump_rise2d_v5/Rising2_before_after.png`, `Takeoff_and_Rising.png`.
- **Rising 2 wrist rotation, October26:** Kvon: "Increase the rotation on the wrist in rising 2." **jump_rise_v6:** rising 2's Keyblade turned 75 deg toward the player (was 60); everything else is v5. Sheets `jump_rise2d_v6/Rising2_rotation_before_after.png`, `Takeoff_and_Rising.png`.
- **Rising 2 wrist straightened and Key down, October26:** Kvon: "Straighten the wrist some as well before angling the keyblade down towards Sora's feet somewhat." **jump_rise_v7:** the turn toward the camera eased to 65 deg, then the blade tipped down (0.75 turned + 0.55 down). The Key now hangs down along his standing leg toward his foot. Sheets `jump_rise2d_v7/Rising2_before_after.png`, `Takeoff_and_Rising.png`.
- **Straight wrist = handle square to the forearm, October26:** Kvon clarified that "straighten the wrist" means "make the guard of the keyblade orient parallel to the forearm holding it" (handle perpendicular to the forearm, the fist's natural grip), and asked to revert v7.
  - v8/v9: rising 2 uses the straight wrist (wrist_roll about the forearm), searched or chosen per roll.
  - With this forearm, a straight wrist cannot point the blade both back and down: the down options point toward the camera/forward.
  - Picked roll 210 (blade down toward his feet, toward the player): build `jump_rise_v9_r210` -> 2D `jump_rise2d_v9`.
  - Review folders: jump_rise_v8 (forward across the body), jump_rise_v9 (roll 40, up/back), jump_rise_v9_r240/_r270.
  - Sheets `jump_rise2d_v9/Rising2_straight_wrist.png`, `Takeoff_and_Rising.png`.
- **Reverted, October26:** Kvon: "Revert the change." Rising is back to **jump_rise_v6** (rising 2's Key turned 75 deg toward the player with the bent wrist; v5 elbow). v7 (blade tipped down) and v8/v9 (straight wrist) are not used; they are obsolete at the next cleanup. Current jump set: start v8, rise v6, apex v3, fall v3, land v5.
- **Rising 2 Key slightly lower, October26:** Kvon: "And the keyblade down slightly more." **jump_rise_v10** = v6 (75 deg turn, bent wrist) with the blade tipped down (+0.3 down). The v8/v9 roll search is limited to those versions. Current set: start v8, rise v10, apex v3, fall v3, land v5. Sheets `jump_rise2d_v10/Rising2_before_after.png`, `Takeoff_and_Rising.png`.
- **Twist the Key in place, October26:** Kvon: "Twist the keyblade while keeping it in the same position." Added `blade_twist` (roll about the Key's own shaft). **jump_rise_v11_t45 / _t-45** (+/-45 deg) shown as options B/C against v10 (A): `jump_rise2d_v11_t45/Rising2_twist_options.png`. Awaiting Kvon's pick.
- **Twist pick, October26:** Kvon: "Twist it just a little bit more in the opposite direction." Read as option C (-45) a little further: **jump_rise_v11_t-60** (-60 deg). Current rising = jump_rise_v11_t-60 (2D `jump_rise2d_v11_t-60`).
- **Twist direction corrected, October26:** Kvon: "I meant the other direction." Current rising = **jump_rise_v11_t60** (+60 deg, option B's direction a little further); -60 is not used.
- **Twist too far, October26:** Kvon: "You twisted it way too far." Current rising = **jump_rise_v11_t20** (+20 deg in B's direction). "A little bit" twist ~ 20 deg; 45-60 read as too much.
- **Twist 10, October26:** Kvon: "Try 10." Current rising = **jump_rise_v11_t10** (+10 deg).
- **Twist 5, October26:** Kvon: "Try 5 instead." Current rising = **jump_rise_v11_t5** (+5 deg).
- **Twist chosen, October26:** from the options sheet (`jump_rise2d_v11_t5/Rising2_Twist_Options_Sheet.png`, -60..+60), Kvon: "Use the -30 degrees". Current rising = **jump_rise_v11_t-30** (2D `jump_rise2d_v11_t-30`). Current jump set: start v8, rise v11_t-30, apex v3, fall v3, land v5. The other twist folders are obsolete at cleanup.
- **Rising 2 raised leg, October26:** Kvon: "fix the position of rising 2's upper leg. It's pressed too far into Sora's torso." **jump_rise_v12** (output `jump_rise_v12_t-30`, keeps the -30 twist): raised (left) foot +6 cm forward and 12 cm lower, so the thigh sits below the jacket instead of up inside it. 2D `jump_rise2d_v12`; sheets `Rising2_leg_before_after.png`, `Takeoff_and_Rising.png`.
- **Rising 2 legs straighter, toes down, October26:** Kvon: "Straighten both legs some and angle the higher leg's foot to point the toes down some." **jump_rise_v14** (output `_t-30`): raised foot +20 cm forward and 16 cm lower than v12, toes-down pitch 35 deg; hanging foot 8 cm lower. Hip-to-ankle 0.26/0.32 -> 0.42/0.40 m (leg 0.69). v13 (+8 cm only) barely changed because the toe pitch raises the ankle target. 2D `jump_rise2d_v14`; sheets `Rising2_legs_before_after.png`, `Takeoff_and_Rising.png`.
- **Raised foot toes down at the ankle, October26:** Kvon: "Rotate joint so that the toe on his upper leg points down." **jump_rise_v15** (output `_t-30`): the raised foot's ankle pitch goes 35 -> 70 deg toes-down, with the ankle target lowered by the toe offset so the leg doesn't move (hip-to-ankle unchanged, 0.42 m). 2D `jump_rise2d_v15`; sheets `Rising2_toes_before_after.png`, `Takeoff_and_Rising.png`.
- **Reverted toe change; leg options, October26:** Kvon: "Revert that change and give me a full sheet of options for changing the position of his leg." Rising is back to v14 (toes 35 deg).
  - **Options:** `jump_rise_v16_t-30b_x<cm>_z<cm>` = v14 with the raised foot moved +/-10 cm forward/back and up/down (3x3). Sheet `jump_rise2d_v14/Rising2_Leg_Options_Sheet.png`.
  - Twist parsing now uses a regex. The first v16 attempt folders (`jump_rise_v16_t-30_x*`) are failed partial builds; delete them at cleanup.
- **Leg pick, October26:** Kvon: "use the bottom left picture and put more bend in the knee without changing anything else." Bottom-left = x-10 z-10. More bend at the same height: foot a further 8 cm back -> **jump_rise_v16_t-30b_x-18_z-10** (reach 0.41 -> 0.37; thigh about the same). x-15 z-6 (reach .35) also tried. Current rising = that build (2D `jump_rise2d_v16_t-30b_x-18_z-10`); sheets `Rising2_knee_bend.png`, `Takeoff_and_Rising.png`.
- **Knee raised, October26:** Kvon: "Raise the knee a little bit while bending it so the foot stays pointed in the same direction." Current rising = **jump_rise_v16_t-30b_x-22_z-5** (reach 0.31; foot pitch unchanged at 35 deg). x-24 z-2 (reach .27) was the stronger alternative. Sheets `jump_rise2d_v16_t-30b_x-22_z-5/Rising2_knee_raised.png`, `Takeoff_and_Rising.png`.
- **Hanging leg straighter, October26:** Kvon: "Can we straighten the lower leg so that the foot appears lower than it is?" Builder option `_rz<cm>` for the hanging (right) foot. Options: `jump_rise_v16_t-30b_x-22_z-5_rz-6` (reach .40 -> .46) and `_rz-12` (.51). Sheet `jump_rise2d_v16_t-30b_x-22_z-5_rz-6/Rising2_lower_leg_options.png`. Awaiting Kvon's pick.
- **Hanging leg pick, October26:** Kvon prefers the far right (12 cm lower). Current rising = **jump_rise_v16_t-30b_x-22_z-5_rz-12** (2D `jump_rise2d_v16_t-30b_x-22_z-5_rz-12`). Current jump set: start v8, rise that build, apex v3, fall v3, land v5. Sheet `.../Takeoff_and_Rising.png`.
- **Takeoff and rising approved, October26:** Kvon: "We're done with the takeoff and rising poses." Final: takeoff **jump_start_v8**, rising **jump_rise_v16_t-30b_x-22_z-5_rz-12**. Their older/test folders are obsolete; clean up at the whole-jump approval. Next: apex/fall/land review (`jump_land2d_v5/Apex_Fall_Land.png`).
- **Falling 1 Keyblade options, October26:** Kvon asked for a full sheet of options changing the Keyblade's position/orientation in falling 1. Builder option `_k<n>` (1-9 presets for hand position and blade direction): `jump_fall_v3_k1..k9`. Sheet `jump_fall2d_v3/Falling1_Keyblade_Options.png`. Options 2, 4, 6 and 8 run off the frame edge; they would be adjusted if picked. Awaiting Kvon's pick.
- **Falling 1 blade over his head, October26:** Kvon: "rotate the position of the first pose's keyblade so that the blade is above Sora's head."
  - With option 1's hand, the blade over his head put the guard over his face (k10-k12), so the hand was raised ~10 cm and moved 4 cm back.
  - Options k13 (level), k14 (angled up), k15 (steeper; 2D in `jump_fall2d_v3_k15b` after an interrupted run left a partial `jump_fall2d_v3_k15`).
  - Sheet `jump_fall2d_v3/Falling1_Blade_Over_Head.png`. Awaiting Kvon's pick.
- **Falling 1 kept as is, October26:** Kvon: "For simplicity, we'll stick with the image on the left" (option 1, the original jump_fall_v3 Key raised up and back). Current fall = **jump_fall_v3**; the k1-k15 option folders are obsolete at the jump cleanup.
- **Apex continues from rising 2, October26:** Kvon: "Start by making the apex continue on from rising 2." **jump_apex_v4:** same Keyblade hand / direction / -30 twist as rising 2; raised knee a little higher (foot lift .30), hanging leg tucked up (lift .10), slight forward curl. 2D `jump_apex2d_v4`; sheet `Apex_continues_from_rising2.png`; GIFs `Jump_Cycle(_slow).gif` in that folder. Apex -> falling 1 is now the big jump (Key swings overhead).
- **Apex approved, October26:** Kvon: "That's good" -> final apex **jump_apex_v4**. Remaining: falling 1-2 (falling 1 keeps the raised Key per Kvon; apex -> falling 1 is the big jump), landing.
- **Apex -> falling smoothed, October26:** Kvon chose option 2 (add an in-between). **jump_fall_v4:** 3 drawings [3,3,4]: an in-between (hand halfway, blade halfway between the apex's and falling 1's, twist -15, legs/torso halfway), then falling 1 and 2 unchanged (pixel diff vs v3 at most 6). 2D `jump_fall2d_v4`; sheet `Apex_to_Falling.png`; GIFs `Jump_Cycle(_slow).gif` there.
- **Falling approved, October26:** Kvon: "I like it." Final falling = **jump_fall_v4**. Remaining: landing (falling 2 -> landing 1 swings the Key from overhead to the two-handed front grip in one drawing), then Godot (W/Up) and cleanup.
- **Jump in Godot, October26:** Kvon: "put the jump in Godot, then move on to the cleanup."
  - **Assets:** jump_start_384 (start v8), jump_rise_384 (rise v16_t-30b_x-22_z-5_rz-12), jump_apex_384 (apex v4), jump_fall_384 (fall v4: in-between, fall 1, fall 2), jump_land_384 (land v5).
  - **Script:** W/Up (new press) from idle or a shuffle -> jump_start [2,2,2] -> airborne: y += vy, vy += gravity (200 px peak, 18 frames up); the `jump_air` drawing is picked from vy/launch speed (thresholds -.55/-.15/.15/.4/.75) -> jump_land [3,3,4] on reaching the floor -> idle.
  - ANIMATIONS entries can now list a per-drawing prefix and folder (indices 5 and 6). Demo flag `--jump-demo-at=N`; trace now prints y.
  - **Verified:** takeoff 6 frames, 36 frames in the air, landing 10, then idle; protected files unchanged.
  - **Not included yet:** horizontal drift in the air, double jump.
- **Jump cleanup, October26** (per Obsolete_Animation_Cleanup.md; recovery commit df2b1d3): deleted 155 obsolete jump folders (all test, option and older versions). Kept the final set: jump_start_v8, jump_rise_v16_t-30b_x-22_z-5_rz-12, jump_apex_v4, jump_fall_v4, jump_land_v5, plus their 2D folders. Godot still runs the jump without errors.

**Second jump next, October26:** Kvon skipped the landing in-between and chose the second jump (KH2 Aerial Dodge reference). Reference choice: **Gemini concept art** first (round 32), shown to Kvon before building.

**Why:** User decisions.
- **Round 32 second-jump concept:** Gemini made 6 poses (`gemini_walk_review/round_32/gemini_original_preview.jpg`), no labels this time:
  1. apex tuck;
  2-4. forward flip with motion arcs (pose 3 upside down);
  5. uncurled, open stance, slightly higher;
  6. falling with the Key raised high.
  Image mode needed re-selecting after the chat opened. Shown to Kvon.
- **Correction, October26:** Kvon: "I need his body to spin around on an axis like a top. Having him do a flip is inaccurate." The second jump is an upright spin about the vertical axis (like a top), not a forward flip. Round 33 asks Gemini for a redraw.

**Why:** User correction.
- **Round 33 spin concept:** Gemini redrew it as an upright top-spin (`gemini_walk_review/round_33/gemini_original_preview.jpg`):
  1. apex tuck;
  2. quarter turn;
  3. back to the viewer;
  4. three-quarters (back/side);
  5. facing front again, uncurled;
  6. falling with the Key raised.
  - Poses 1, 5 and 6 reuse round 32's art; the circular swirl is a drawn effect. Shown to Kvon.
- **Second jump spin built (October26; pending review):** Kvon: "Yes, but I need sora posed in more angles to have a smoother transition between images."
  - Recipe `jump_spin_vN`: the approved apex pose turned about his vertical axis in 30 deg steps (11 drawings [2]*11; 0/360 = the apex drawing). `apply_run` now supports `spin_deg` (rotates the hand, feet, left-arm target, elbow hints and Key hand orientation).
  - **v1:** blade level out sideways, hits the frame. **v2:** hangs down (fits). **v3:** in between, hits the sides.
  - **v4 (current):** eases from the apex blade to hanging down over the first and last 60 deg; all drawings inside the frame.
  - Spin direction: front turns away first (`ccw` in the output name reverses it).
  - 2D `jump_spin2d_v4`: `Spin_All_Angles.png`, `Spin_preview(_slow).gif`.
- **Second jump approved and in Godot, October26:** Kvon: "Everything is fine" (spin v4: direction, 2 frames per angle, apex pose).
  - `jump_spin_384`; W/Up pressed again while airborne (once per jump) sets vy = -0.7 x the first jump's speed and plays the 11 spin drawings, then the swing-up drawing (air 3) until frame 25 of the second jump, then the normal speed-picked fall.
  - The 0.85 speed put his head off the top of the screen when used at the peak; 0.7 keeps it on.
  - Flag `--jump2-demo-at=M`; traced and recorded.
  - An old heredoc patch had collapsed a line continuation in the `jump` input line; fixed.
- **Spin cleanup:** deleted jump_spin_v1-v3 (recovery commit 9c37cdf); kept jump_spin_v4 and jump_spin2d_v4.

**Forward air-dash next, October26:** Kvon chose it. Control: **double-tap forward in the air** (same as the ground glide). Reference: **Gemini concept art first** (round 34), following the air transition rule (rise -> brief tuck -> dash).

**Why:** User decisions.
- **Round 34 air-dash concept:** Gemini made 6 poses (`gemini_walk_review/round_34/gemini_original_preview.jpg`):
  1. tuck;
  2. burst forward, left arm reaching forward, Key back;
  3. nearly horizontal "superman" dash, Key straight back, legs trailing;
  4. still dashing, more crouched;
  5. braking upright;
  6. falling with the Key raised.
  - Speed lines and dust are drawn effects; pose 1 holds the Key two-handed (rule says one hand). Image mode needed re-selecting again. Shown to Kvon.
- **Air-dash built (October26; pending review):** Kvon: "Use the bottom left pose as the main reference for the dash, then build the transitions around that." Recipe `jump_dash_vN` (4 drawings [3,4,4,3]): burst (apex/dash blend), dash 1, dash 2, brake; then the existing falling in-between and fall.
  - **v1:** too upright and facing the camera; legs under him; Key off the frame.
  - **v2 (current):** dash turned +25, hunch 16 / pitch 26 / neck -34; both legs bent with the feet trailing (L -.06 lift .32, R -.38 lift .22); Key arm reaching back, blade back and toward the camera so it fits. Brake upright (turn 8), Key rising toward the falling pose.
  - 2D `jump_dash2d_v2`: `AirDash_Sequence.png` (with the reference crop), `AirDash_preview(_slow).gif`.
- **Air-dash approved "for now" and in Godot, October26:** Kvon: "It looks right for now" (may revisit).
  - `jump_dash_384`; a double tap of forward while airborne (once per jump, not during the spin) plays the apex tuck 3 frames, then burst 3 / dash 1 4 / dash 2 4 / brake 3 frames.
  - No gravity during the dash; it moves 4/10/16/16/6 px per frame (~190 px).
  - Afterwards vy = 0 and the falling drawing is forced to >= falling 1 (skipping the swing-up, since the brake already raised the Key).
  - Flag `--dash-demo-at=M`; traced (the plain jump and spin are unchanged) and recorded.
- **Air-dash cleanup:** deleted jump_dash_v1 (recovery commit above); kept jump_dash_v2 and jump_dash2d_v2.

**Back-dash resumed, October26:** Kvon chose the back-dash. Control: **double-tap back (A/Left)**, on the ground or in the air. Reference: **new Gemini art** (round 35) stressing a quick, low backstep (round 31 read as a jump), based on ref_04.

**Why:** User decisions.
- **Rounds 35-36 back-dash:**
  - **Round 35:** refused ("cannot generate images directly"), as in round 29.
  - **Round 36:** after a page refresh (Kvon's earlier remedy), 5 low poses (`gemini_walk_review/round_36/gemini_original_preview.jpg`):
    1. idle;
    2. push-off with dust;
    3. low hop, upright, knees bent, Key low in the right hand, left arm out;
    4. feet reaching down;
    5. landing back in the two-handed idle.
  - In poses 2-4 he leans/moves forward-right rather than backward. Shown to Kvon.
- **Back-dash built (October26; pending review):** recipe `jump_bdash_vN`, 5 drawings [2,4,4,3,4]: push, hop, hop 2, touch down, settle.
  - Corrected from round 36 so he leans BACK: torso pitch -17 / -12, feet out in front and lifted (L .28/.24, R .12/.16).
  - Key low behind in the right hand; left arm out for balance; settle regrips with both hands.
  - **v1:** barely off the floor, no visible lean. **v2:** current.
  - 2D `jump_bdash2d_v2`: `BackDash_Sequence.png`, `BackDash_preview(_slow).gif` (the GIF moves him ~160 px back with a small lift).
- **Back-dash and air-dash timing, October26:** Kvon: "I want the back-hop to linger slightly longer and carry a greater distance. I also want the air dashes to do the same while carrying some momentum." Drawings unchanged (bdash v2, dash v2); Godot timing changed:
  - **Back-dash** (double-tap A/Left, `back_dash_384`): holds [2,7,7,3,4] = 23 frames; speeds -6/-17/-14/-5/0 (~245 px); a 32 px sin hop over the hop drawings on the ground.
  - **In the air:** a back-dash plays push/hop/hop 2 with no gravity, sharing the one air dash per jump.
  - **Forward air-dash:** holds [3,3,6,6,4] (~255 px).
  - **Momentum:** after either air dash, vx = +/-7 px/frame fading by x0.9 per frame until landing.
  - Flags `--bdash-demo-at=N`; all three traced; ground back-dash recorded.
- **Faster glide and air steering, October26:** Kvon: "I want the forward dash to be faster on the ground. I also want him to be able to move left and right in the air without having to dash."
  - **Glide:** root motion x1.5: loop 45 px per 3-frame drawing (900 px/s, was 600); push-off [5.42, 21.66, 27.07, 43.32]; skid [45, 27.07, 13.54, 5.42, 0]. Drawings unchanged.
  - **Air steering:** while airborne (not during a dash or spin), holding D/Right or A/Left eases vx toward +/-4 px/frame (accel 0.5/frame). Dash momentum above that fades by the 0.9 drag first; no input = drag. About 140 px of drift over a full jump.
  - Traced: glide, jump holding forward, jump holding back.
- **Instant cancels and jump carry, October26:** Kvon: "I want every animation cancel to feel instant... move further both forward and backward when maneuvering in the air... jump a decent distance and angle while walking, then that angle and distance magnified when jumping out of a ground dash."
  - **Cancels:** jump, back-dash and glide now cancel any ground move at once (GROUND_CANCEL = idle, shuffles, crouch down/hold/up, glide start/loop/stop, jump_land, plus a running back-dash). Crouch cancels a shuffle, landing or glide skid at once; walking out of a landing is instant.
  - **Takeoff:** [1,1,1] = 3 frames from standing; 2 when already moving (skips the crouch drawing).
  - **Jump carry:** takeoff vx = walk +/-5, glide +12, back-dash -9 px/frame. Holding the same way keeps a faster carry; no input coasts at 0.98/frame; dash momentum still fades at 0.9.
  - **Steering:** up to +/-6 px/frame, accel 0.6.
  - **Traced:** standing jump (no drift), walk jump (~190 px forward), glide jump (~430 px), back-dash jump (backwards), walk->crouch, glide->back-dash.
- **Double jump further and higher, October26:** Kvon: "I want the double jump to travel a little further and higher." JUMP2_SPEED 0.7 -> 0.8 of the first jump (peak ~128 px above the press point vs ~98). JUMP2_VX = 7 px/frame sideways push in the held direction (unless already faster). Used at the very peak of the first jump, his hair passes the top of the fixed 720 px test screen by ~25 px (head top row 79 of 384); a game camera or a slightly lower first jump would fix it.
- **Simple camera, October26:** Kvon: "Add a simple camera." `sora_move_test.gd` creates a Camera2D at (640,360), limits left 0 / right 1280 / bottom 720, so it never pans sideways or below the floor. Each tick it eases (0.25/frame) up just enough to keep Sora's hair (row 60 of his 384 frame) 40 px below the screen top, then back down. A sky-coloured ColorRect (19,28,57) fills above the background painting. Verified in a recorded high double jump; Godot Camera2D docs checked (enabled/make_current/limits).

**Hurt animations started, October26:** Kvon asked for four hurt animations: (1) lying flat on the ground, (2) leaning back from a hit (ground), (3) leaning back from a hit in the air, (4) falling head first with his back to the screen and feet in the air. Choices: the lying pose is **face up** (on his back); reference is **Gemini concept art first**, shown to Kvon before any 3D build.
**Why:** Kvon's request and answers.
- **Round 37 hurt concept** (`gemini_walk_review/round_37/gemini_original_preview.jpg`; both reference images uploaded, image mode was already on): 8 poses in two rows. Row 1: ground hit impact (arched back, head thrown back), ground recovery, air hit impact (legs dangling), air drift back (nearly horizontal). Row 2: head-first fall with his back to the viewer and feet up, a closer upside-down pose with the shoulders about to land, hitting the floor on his back with dust, lying flat face up (head screen left). The hit sparks, dust and speed lines are drawn effects, not part of the sprite. Shown to Kvon; waiting for his choice.
- **Correction, October26:** Kvon: "In some pictures like the two to the left on the bottom, his legs face the wrong way. Make sure these errors are fixed when manipulating the 3d model." Gemini's round-37 poses 5-6 (head-first fall) draw the legs facing the wrong way. On the model, the knees must always bend naturally (shin folds toward his back, knee cap toward his front) and the feet point the way his body faces, whatever the body's rotation; check this on every hurt render before showing it.
**Why:** Kvon's correction of Gemini's art.
- **Hurt set built, October26 (pending Kvon's review):** `build_sprite_pilot.py -- hurt_<ground|air|fall|down>_vN` (JUMP machinery). Each drawing is solved upright (normal knee/elbow bends), then the whole pose is turned: `spin_deg` (vertical axis; 150 = back to the screen), `roll`/`body_angle` (screen plane about the hips; body_angle measures ankles->neck from v3, 180 = flat with head screen-left), `ground` (lowest vertex on the floor, centred across the frame) + `lift`. Upper-body/head lean in the screen plane via `lean_cam`/`head_cam` (a lean about his own side axis goes into the screen from this camera and barely showed in v1). Blade directions for spun drawings are given after the spin (Rz(-spin) @ wanted).
  - Current: ground hit `hurt_ground_v2` [2,6,5,4] (snap back, deepest, recover 50%, 85%); air hit `hurt_air_v2` [4,8]; head-first fall `hurt_fall_v3` [4,4,4] (back to the screen, feet up); floor `hurt_down_v4` [3,4,6] (shoulders hit with legs up, settle, lie flat face up). 2D: `hurt_*2d_*`; sheet `hurt_down2d_v4/Hurt_All_Sprites.png`, GIF `Air_Hit_To_Knockdown_slow.gif`.
  - `hurt_down_v2_upright` is a review render (pose before the turn); obsolete with v1-v3 once Kvon approves.
- **Correction, October27:** Kvon: "His legs should be mostly straightened out in the 2nd and 3rd rows of sprites" (air hit and head-first fall). Rebuilt with a `leg_reach` option: each foot target is pulled to a fixed fraction of the full leg length along its direction (0.975 = mostly straight, slight knee bend kept).
**Why:** Kvon's correction.
  - Result (pending Kvon's review): `hurt_air_v4` (legs straight; `offset_px` nudges drawing 1 up 36 px and drawing 2 left 44 px so the longer legs stay in the frame) and `hurt_fall_v4` (legs straight). Sheet `hurt_air2d_v4/Hurt_All_Sprites.png`, GIF `hurt_air2d_v4/Air_Hit_To_Knockdown_slow.gif`.
- **Correction, October27:** Kvon: "Straighten the ankles in the second image on row two and add slightly more bend to the knees in each of the rows that you had just edited." Air drift drawing: feet follow the shin line (new `ankle_deg` = angle between the shin's continuation and the foot; 30 = relaxed, nearly pointed). Air hit and fall: `leg_reach` .975 -> .94.
**Why:** Kvon's correction.
  - Result (pending Kvon's review): `hurt_air_v5` / `hurt_fall_v5` (+2D). Sheet `hurt_fall2d_v5/Hurt_All_Sprites.png`, GIF `hurt_fall2d_v5/Air_Hit_To_Knockdown_slow.gif`. Feet on the drift drawing now continue the shin line instead of tilting up.
- **Gemini round 38 (hurt review, October27; Kvon: "Connect with Gemini for suggestions"):** both images confirmed on the message (built sheet v5 1024x1024 + round-37 concept). Image mode had to be switched off first (button `[aria-label="Deselect Images"]`) for a text reply. Gemini's list (`gemini_walk_review/round_38/gemini_response.txt`):
  1. Ground hit drawings 1-2: more violent snap - spine back another 15-20 deg (sharp C curve), chest out, head back so the face aims at the ceiling.
  2. Air hit: legs "tucked like sitting", feet flat - extend the legs forward/down with a slight bend, ankles fully pointed along the leg. (My check: largely outdated - v5 legs are already mostly straight per Kvon; only the ankles on drawing 1 are still flexed.)
  3. Fall: "knees still sharply bent" (my check: not true in v5, slight bend only). Valid point: add an in-between drawing between the air drift and the fall with his body horizontal in the air.
  4. Knockdown drawings 2-3: claims he lands face-down/on his side (my check: he is face up, but seen side-on the face/chest read weakly); move the Keyblade off his body to rest on the floor beside his hip.
  Not applied; reported to Kvon.
- **Decision, October27:** Kvon: "Employ 1, 2, 3, and 4" (round-38 list as I summarized it): (1) stronger ground-hit snap on drawings 1-2 (more screen lean/head back, chest out); (2) a new in-between at the start of the fall with his body horizontal in the air; (3) ankles pointed on air-hit drawing 1 too; (4) knockdown: chest/face turned more toward the camera so face-up reads, Keyblade resting on the floor beside his hip instead of across his body.
**Why:** Kvon's choice of Gemini's suggestions.
  - Result (pending Kvon's review): `hurt_ground_v3` (snap), `hurt_air_v6` (both drawings' ankles pointed), `hurt_fall_v6` [3,4,4,4] (horizontal in-between first), `hurt_down_v6` (spin 30 so chest/face read face-up; right hand on the floor by his hip, Key lying on the floor toward his feet; v5's blade went through the floor). Sheet `hurt_down2d_v6/Hurt_All_Sprites.png`, GIFs `Air_Hit_To_Knockdown_slow.gif`, `Ground_Hit_slow.gif`.
- **Correction, October27:** Kvon: "For the last two poses on the second row [he meant row 3, the head-first fall], his body needs to be at the same rotational angle as the two images before it. Also, for that entire row, adjust his hip joints to make his legs move backward slightly." and "Sora leans too far back when getting hit on the ground." Applied: fall drawings 3-4 take drawing 2's tilt and turn (roll 130, spin 110; my reading - drawing 1 is horizontal, so it can't be head-first); new `hip_back_deg` (12 deg) swings both legs back at the hips on all four fall drawings; ground-hit lean set halfway between v2 and v3.
**Why:** Kvon's correction.
  - Result (pending Kvon's review): `hurt_ground_v4`, `hurt_fall_v8` (v7's Key kept the old aim and ran off the bottom; v8 aims drawings 3-4 like drawing 2). Sheet `hurt_fall2d_v8/Hurt_All_Sprites.png`, GIFs `Air_Hit_To_Knockdown_slow.gif`, `Ground_Hit_slow.gif` in the same folder. Note: fall drawings 3-4 are now nearly identical (same angle).
- **Correction, October27:** Kvon: "His final falling pose should have him completely upside down with his arms at the side." Fall drawing 4: roll 180 (straight upside down, same turn as drawings 2-3), both arms down along his sides (Key held along his body).
**Why:** Kvon's correction.
  - Result (pending Kvon's review): `hurt_fall_v11` - drawing 4 straight upside down, arms hanging straight at his sides (v9 had the hands at the waist), Key along his right side, nudged down 24 px (v10's Key tip touched the top). Sheet/GIF in `hurt_fall2d_v11/`.
- **Hurt set approved, October27:** Kvon: "I like this version." Finals: `hurt_ground_v4`/`hurt_ground2d_v4`, `hurt_air_v6`/`hurt_air2d_v6`, `hurt_fall_v11`/`hurt_fall2d_v11` (current full sheet and GIF live here), `hurt_down_v6`/`hurt_down2d_v6`. The 40 obsolete hurt folders (incl. `hurt_down_v2_upright`) were deleted per the cleanup rule (no .import files were among them); Godot still runs. Not yet exported to `KingdomArena/assets` or wired into the test scene.
- **Note, October27:** `KingdomArena/project.godot` showed an uncommitted `[input]` "jump" action (W + Space) that I did not make (likely Kvon in the editor). Left untouched and uncommitted; told Kvon.
- **Hurt set in Godot, October27 (Kvon: "Go ahead"):** exported to `KingdomArena/assets/sora/hurt_{ground,air,fall,down}_384/` (384 px LANCZOS from the approved 2D finals). `sora_move_test.gd` test keys (no opponent yet): **H** = hit (ground: hurt_ground [2,6,5,4] with knockback root motion [-10,-14,-4,0], then idle; in the air or while already knocked back: knockdown with half the launch), **J** = knockdown from the ground (KNOCK_SPEED = JUMP_SPEED*0.85, KNOCK_VX 5 back; HURT_AIR_HOLDS [4,8,3,4,4] = air hit 1-2 + fall 1-3, fall 4 held until landing; hurt_down [3,4,6] then lies LIE_FRAMES 60 and pops to idle - no get-up animation yet). Demo flags `--hit-demo-at`, `--knock-demo-at`. Verified by traces (ground hit, J, hit during a jump) and a recorded movie.
- **Correction, October27:** Kvon: "I first want the transitions between the first and last poses in the air to be faster." HURT_AIR_HOLDS [4,8,3,4,4] -> [2,4,2,2,2]: the final upside-down drawing now shows 12 game frames after the hit (was 23) and is held until landing. Next: a get-up animation (Kvon said "Yes" to it).
**Why:** Kvon's correction.
- **Get-up concept, October27:** Kvon: "Ask gemini first." Prompt `GETUP_CONCEPT_ROUND_39.txt` (6 poses: lying face up -> sit up pushing with the left hand -> roll onto one knee -> kneel -> rise -> battle idle), references `getup-concept` (lying drawing, battle idle, approved hurt sheet; all three thumbnails confirmed).
  - **Round 39:** "I seem to be encountering an error. Can I try something else for you?" - no image (Kvon saw it in the browser too).
  - **Round 40** (after a page refresh, Kvon's remedy, and re-selecting Create image): text claimed a sheet ("There is a file you can reference named watermarked_img_...jpg") but the reply contained NO image. Stopped and asked Kvon.
  - Image mode tip: after a reload, "Upload & tools" -> the `Create image` menuitemcheckbox; confirm the `[aria-label="Deselect Images"]` chip; click the prompt box to close the menu before sending.
- **Get-up from online references, October27:** Kvon: "Look up other similar fighting games online and use animations from there as reference for creating the poses yourself." Sources: SmashWiki Floor getup (neutral getup = "simply stand up"; roll getup; getup attack) and Sora (SSBU) (his floor attack spins and swings the Key while getting up - an attack, not used here); SuperCombo/EventHubs on Street Fighter quick rise/back rise. No source gave a frame-by-frame description, so the poses follow the common neutral stand-up: sit up leaning back with the left hand pushing on the floor -> knees tucked -> crouched over the feet -> rising -> idle. Built as `hurt_getup_vN` (5 drawings, from the approved lying pose's turn).
  - `hurt_getup_v2` (+2D `hurt_getup2d_v2`, pending Kvon's review): [5,4,4,4,4] sit up (lean back 50, legs forward, left hand on the floor behind, Key flat on the floor) -> tuck -> crouch over the feet (Key low behind) -> rise (left hand coming to the handle) -> 70% to the idle. Grounded, not centred (`no_center`), so the standing drawings line up with the idle's feet. v1's blade went through the floor on drawings 1-3. Sheet `Getup_Sheet.png` (lying -> 5 drawings -> idle), `Getup_slow.gif`.
- **Get-up approved, October27:** Kvon: "It looks great." Final `hurt_getup_v2` / `hurt_getup2d_v2`; obsolete `hurt_getup_v1` deleted (cleanup rule; no .import files). Exported to `KingdomArena/assets/sora/hurt_getup_384/`; in `sora_move_test.gd` the knockdown now lies LIE_FRAMES (60) then plays hurt_getup [5,4,4,4,4] into the idle (root motion +8 px on drawing 1 keeps the hips in place; checked in a recorded movie). Get-up can't be cancelled except by another hit.
- **Held jump, October27:** Kvon: "When holding the jump button, the player will continue jumping as soon as the character is in their upright position on the ground." `sora_move_test.gd`: while W/Up is held, a ground jump starts whenever he is upright - idle, shuffling, or the landing's last (nearly standing) drawing - not on the crouched landing drawings, not during a back-dash. The air second jump still needs a fresh press. Demo flag `--jump-hold-to=N`. Verified: held = lands, last landing drawing at frame 50, jumps again at 51; single press = one jump.
- **Correction, October27:** Kvon: "I want his getup animation to be a little faster and for him to stay on the ground for less time when knocked down." hurt_getup holds [5,4,4,4,4] -> [3,3,3,3,3] (21 -> 15 game frames); LIE_FRAMES 60 -> 30. Verified: knockdown lands frame 36, get-up at 79, idle at 94 (was 109 / 130).
**Why:** Kvon's correction.
- **Correction, October27:** Kvon: "make his getup animation slower than it is now, but still faster than it was previously." hurt_getup holds [4,4,4,3,3] = 18 game frames (between 21 and 15). Lying time stays 30.
**Why:** Kvon's correction.
- **Attacks started, October27:** Kvon: "Let's do the attacks next." Plan from memory (nine basics, Sora_*_Light/Medium/Heavy notes) and `design/Sora_Animation_Charts.md` (drawing counts and prep -> strike -> recovery), wind-up reference `design/references/sora_attack_pose_reference.jpg`. Per the chart: finish one complete attack in Godot before the rest. First: **Standing Light** (6 drawings: small draw-back -> short Keyblade thrust -> tight guard return). Reference choice: **Gemini art first**.
**Why:** Kvon's request and answer.
- **Round 41 Standing Light concept** (`gemini_walk_review/round_41/gemini_original_preview.jpg`; image mode, both references attached). The exchange helper stopped with "More than one new image appeared", so the image was saved with `save-image` (tagged the last reply's img `data-kh="r41"`). 6 poses: idle, small draw-back (blade up and back over his shoulder), thrust (front foot forward, Key level at chest height toward screen right), full extension (deep lunge), pulling back (blade up and back), guard return. My check: poses 1 and 6 draw the idle with the blade pointing FORWARD toward the opponent, not back behind him like the approved idle - use the approved idle instead. Shown to Kvon.
- **Standing Light redesign, October27:** Kvon replaced the thrust with a bunt-style guard bash (see `Sora_Standing_Light.md`) and corrected the idle note (`Sora_Idle_Pose.md`: blade in front). Gemini round 42: refused ("cannot generate images directly"); round 43 after a refresh (Kvon's remedy): 5-pose sheet `gemini_walk_review/round_43/gemini_original_preview.jpg`. My check: poses 1 and 5 hold the Key raised over his shoulder (not the approved idle); poses 2 and 4 hold it level but with the guard at his back hand and the blade pointing at the opponent; pose 3 is a one-handed push with the guard leading but the blade still extends far forward past it and the left hand is off the Key. Shown to Kvon.
- **Standing Light built, October27 (pending Kvon's review):** `atk_slight_vN` (HURT machinery, grounded, not centred), 4 drawings [2,4,3,3]: set (Key level at chest, guard forward, blade back, left hand on the shaft) -> bash (fist/guard shoved ~20 cm forward, small step in, lean 8) -> recoil -> 60% back to the idle. v2 moves the left hand from .22 to .32 m back along the shaft (v1 sat almost on the guard). 2D `atk_slight2d_v2`, sheet `Standing_Light_Sheet.png` (idle -> 4 -> idle), `Standing_Light_slow.gif`.
- **Standing Light v3, October27 (pending Kvon's review):** hands swapped per Kvon - left fist on the handle inside the leading guard, right hand on the shaft behind it (`key_in_left`: the Key keeps its angle and slides along its line onto the left fist). Return drawing hands the Key back to the right hand. 2D `atk_slight2d_v3`, sheet/GIF in that folder.
- **Standing Light v5, October27 (pending Kvon's review):** per Kvon's correction (extend the Key out front; wrists must line up with what they hold): guard at arm's length on the bash (step in .12, lean 12), chest height (v4 crossed his face), hands .36 m apart, Key placed from the solved fists (handle middle in the left fist via `key_slide` .12, shaft through the right fist). 2D `atk_slight2d_v5`, sheet/GIF there.
- **Standing Light v6, October27 (pending Kvon's review):** blade tip turned ~35 deg toward the camera (Kvon); on screen the blade reads shorter (foreshortened) with the teeth more face-on. 2D `atk_slight2d_v6`, sheet/GIF there.
- **Standing Light v8, October27 (pending Kvon's review):** blade ~45 deg toward the camera; shaft (right) hand with a straight wrist, roll searched so the fist lines up with the shaft (v7 let that roll turn the Key edge-on; v8 keeps the Key's own guard-to-camera angle, `KEY_ROT_FACE`). 2D `atk_slight2d_v8`, sheet/GIF there.
- **Standing Light v9, October27 (pending Kvon's review):** shaft hand .44 m up the shaft (Kvon). 2D `atk_slight2d_v9`, sheet/GIF there.
- **Standing Light v10, October27 (pending Kvon's review):** front foot pulled in (idle -.03 set, -.05 bash/recoil). 2D `atk_slight2d_v10`, sheet/GIF there.
- **Standing Light v11, October27 (pending Kvon's review):** front foot further in (idle -.07 set, -.10 bash/recoil). 2D `atk_slight2d_v11`, sheet/GIF there.
- **Standing Light approved and in Godot, October27:** Kvon: "It looks good. Make U trigger the light attack." Final `atk_slight_v11` / `atk_slight2d_v11`; 17 obsolete atk_slight folders deleted (cleanup rule; no .import files). Exported to `KingdomArena/assets/sora/attack_light_384/`; `sora_move_test.gd` animation `attack_light` [2,4,3,3] (12 game frames), **U** triggers it from any standing ground move (not crouching, not mid back-dash), it plays to the end (only a hit interrupts) and returns to what is held. Demo flag `--light-demo-at=N`. Verified by traces (standing, walking, crouching = no attack) and a recorded movie (feet planted). The scene label now lists U; that commit also carries the Godot editor's re-save of `sora_move_test.tscn` (format only).
- **Correction, October27:** Kvon: "Make the frame that the light attack is meant to hit linger a little bit longer." attack_light holds [2,4,3,3] -> [2,6,3,3] (14 game frames).
**Why:** Kvon's correction.
- **Frame data, October27:** Kvon set the Standing Light to startup 6, active 3, recovery 13 (22 game frames). attack_light holds [6,3,6,7]: set drawing = startup, bash drawing = active, recoil + return = recovery.
**Why:** Kvon's numbers.
- **Standing Medium started, October27:** Kvon: "Let's continue to the next step." Gemini round 44 (image mode; idle + approved Standing Light sheet attached): 8 poses, `gemini_walk_review/round_44/gemini_original_preview.jpg`. Row 1: idle?, wind-up, wind-up peak (Key level behind him), slash begins (Key level forward at chest). Row 2: impact (arms extended, Key level out front), follow-through (Key up over his shoulder), recovering (Key low in front), idle?. My check: poses 1, 2 and 8 hold the Key raised high over his shoulder instead of the approved idle (low in front, blade angled up toward the opponent) - start/end on the real idle. Shown to Kvon.
- **Standing Medium built, October27 (pending Kvon's review; no smears yet):** `atk_smed_vN` (HURT machinery, grounded, not centred), 9 drawings: 2 in-betweens out of the idle, raised over the right shoulder, wind-up (turn 75, twist -16, Key level back), slash start (turn 45), impact (turn 15, twist +14, front knee bent, back heel up 25, pitch 10, Key level out front), follow-through (turn -25, Key up over the left shoulder), recover, 70% to the idle; both hands on the handle (release 0). v1 ran off the frame (Key straight up, wind-up back to camera, impact past the right edge). 2D `atk_smed2d_v2`, `Standing_Medium_Sheet.png`, `Standing_Medium_slow.gif`.
- **Standing Medium v5 with smears, October27 (pending Kvon's review):** raised poses match Gemini's (hands by the rear shoulder, blade up and forward like a batter); Ekko-style lunge impact; wind-up blade starts low so the swing rises. `make_smears.py <3d> <2d>` draws the smear layer (`frames_smear_512/sora_smear_NN.png`) from the builder's `key_track`: solid two-tone crescents (deep blue outer, pale core) tapering to a point where the swing began; level swings (a straight line from this eye-level camera) are bowed into a crescent (20% of their length); a minimum on-screen width (64/30 px x taper); the layer sits ON TOP of the body, stopping short of the blade. Smears on begin (from wind-up), impact (from wind-up, 2 drawings) and follow-through. Sheet/GIF `atk_smed2d_v5/`.
- **Standing Medium v9, October27 (pending Kvon's review):** left arm visible (hands in his body frame; left elbow hint down and toward the camera so the far arm comes round the near side - the debug run showed the left hand WAS on the handle in v5/v6 but hidden; the report's grip_error_L metric is misleading for turned bodies), raised pose lowered (v7 tip off the top), recovery blade angled toward the camera (v8 touched the right edge). Smears as v5. Sheet/GIF `atk_smed2d_v9/`.
- **Standing Medium v12, October27 (pending Kvon's review):** chest toward the camera through the swing (slash start turn 20, impact -20, follow-through -40, recovery -20) so the arms are in front of the body; impact hands reach out toward the opponent at chest-to-waist height (v10's bunched at his chest with the guard over his face); impact blade angled toward the camera to stay inside the frame. Smears unchanged in style. Sheet/GIF `atk_smed2d_v12/`.
- **Standing Medium v13, October27 (pending Kvon's review):** batter's kinetic chain (Kvon): slash start turn 40 / twist -22 (hips lead, shoulders lag), impact -15, new wrap drawing (turn -45, Key sweeping on round toward the camera, smear), follow-through turn -70 with the back foot pivoting onto its toe (pitch 50, knee_in .8), front leg straighter, arms over the front shoulder, recovery -35. 10 drawings [2,2,3,3,2,3,2,3,4,4] (placeholder timing). New key option `knee_in` (HURT recipes). Sheet/GIF `atk_smed2d_v13/`.
- **Standing Medium v15, October27 (pending Kvon's review):** feet almost together under his torso from the wind-up on (raised halfway), straighter legs (v14's knee bend bowed the knees into a squat), impact arms straight at shoulder height with the blade straight at the opponent (full reach). Impact drawn 120 px left and wrap 40 px left inside the 512 frame (`offset_px`, in key_track) - Godot must shift those drawings back; previews (`atk_smed2d_v15/`) are composed on a wider canvas with the shift undone, as the game will show them. make_smears.py moves earlier drawings into the current drawing's frame.
- **Standing Heavy built, October27 (pending Kvon's review):** `atk_sheavy_vN` 11 drawings matched to Gemini round 45: in-between, raised over the rear shoulder, coiled low wind-up, spin (chest swings toward the camera with the Key up-back, back to the viewer with the Key trailing level, round to the front with the Key raised), deep-lunge impact, follow-through over the shoulder, heavy settle with the Key pointing down, 70% to the idle. Turn decreasing (v1 spun the other way from Gemini); feet pivot with the body through the spin. Timing [1,2,3,2,2,1,2 | 3 | 6,9,6] = Ekko's 13/3/21. Smears on the spin, impact (2 drawings back) and follow-through. v3 tilted blades to fit the frame. `atk_sheavy2d_v3/`: Standing_Heavy_Sheet.png, Standing_Heavy_vs_Gemini.png, Standing_Heavy_slow.gif.
- **Standing Heavy v6 (advancing downward slash), October27 (pending Kvon's review):** `atk_sheavy_v6` 9 drawings [2,4,3,4 | 3 | 5,6,5,5] = 13/3/21: lift, overhead, back foot steps up, front foot strides as the Key comes down, impact lunge (Sol 6H reference; Key down-forward, torso leaning), follow-through low, recover, back foot steps up, idle. Root motion (m) in the report moves him ~.56 m forward with planted feet still. Impact drawn 48 px left in its frame (offset_px; Godot shifts back). v4 blades left the top/went through the floor; v5 widened the lunge. Smears on the slash start/impact/follow-through. `atk_sheavy2d_v6/` sheet + travelling GIF.
- **Standing Heavy v7, October27 (pending Kvon's review):** impact/follow-through Keyblade extended further forward (Kvon); impact drawn 96 px and follow-through 40 px left in their frames (offset_px). `atk_sheavy2d_v7/`.
- **Crouching Light built, October27 (pending Kvon's review):** `atk_clight_vN` from the rebuilt crouch (checked against crouch_hold_v4 with `atk_clight_v1_crouchcheck`; new `knee_splay` key option), 6 drawings [2,3 | 3 | 4,4,4] = 5/3/12 proposal: draw-back, low forehand sweep (smear), hit at shin height out front (smear, drawn 40 px left - Godot shifts back), follow-through, two drawings back to the crouch. v1 blade off the left edge/through the floor, v2 tip on the right edge and follow-through end-on. `atk_clight2d_v3/` sheet + GIF.
- **Crouching Light v6, October27 (pending Kvon's review):** v4 follow-through drawn 30 px left, v5 return blade lifted off the floor. Smears: traced from the draw-back they ran along/under the floor (the tip skims the floor in this low swing), so make_smears.py now (a) clears anything below the floor line, (b) bows low swings upward, (c) flattens dips onto the floor; v6 smears only sweep->hit and hit->follow-through - small and faint. Offered Kvon a hand-shaped flat floor-level smear like Ky's 2S instead. `atk_clight2d_v6/` sheet + GIF. Proposed input: U while crouching (S/Down held).
- **Correction, October27:** Kvon: "I want to change his crouching pose so that his back leg is in a kneeling position." Crouch v5+ (crouch_down/crouch_hold): the back (right) leg kneels - foot further behind on its toes, knee down toward the floor, hips a little lower; front leg as before. The crouching attacks must start/end on the new crouch.
**Why:** Kvon's correction.
- **Kneeling crouch v11, October27 (pending Kvon's review):** crouch_down_v11 / crouch_hold_v11 (+2D). CR_KNEEL (slide 0, ankle lift .11, toe pitch 25, sink -.08 = hips higher than v4 by .08): back thigh drops straight down (knee hint straight down), knee at the floor (~.12 m), shin back to the foot on its toes; eased in over crouch_down. History: v5 foot "behind" in body frame hid the leg; v6-v8 hips too low (~.23 m) so the leg splayed sideways with the ankle raised (and v8's pitch sign flip was wrong); v9 foot too far back; v10 toe through the floor. Debug: `<name>_dbg` prints KNEEDBG joint positions. Previews `crouch_hold2d_v11/`: Kneel_Crouch_Sheet.png, Idle_To_Kneel_Crouch.gif, Crouch_v4_vs_Kneel_v11.png. Not yet in Godot; Crouching Light must be rebuilt on it.
- **Correction, October27:** Kvon: "His shin should be turned, putting his foot slightly behind him towards the background." Kneeling crouch v12: back foot moved .14 m away from the camera (CR_KNEEL_DEPTH), knee still on the floor. crouch_down_v12 / crouch_hold_v12 (+2D); previews in `crouch_hold2d_v12/` (Kneel_v11_vs_v12.png, sheet, GIF). Pending review.
- **Correction, October27:** Kvon: "Increase the turn." Kneeling crouch v13: back foot .28 m away from the camera (v12 .14). crouch_down_v13 / crouch_hold_v13 (+2D), previews `crouch_hold2d_v13/` (Kneel_v11_v12_v13.png, sheet, GIF). Pending review.
- **Correction, October27:** Kvon: "Add more turn than the previous attempt." Kneeling crouch v14: back foot .42 m away from the camera (v13 .28). From this camera the turn mostly shortens the shin on screen (the foot moves in under the knee and partly behind the leg). crouch_down_v14 / crouch_hold_v14 (+2D), `crouch_hold2d_v14/Kneel_Turn_v11_to_v14.png`. Pending review.
- **Correction, October27:** Kvon: "A little more turn." Kneeling crouch v15: back foot .50 m away from the camera (v14 .42). crouch_down_v15 / crouch_hold_v15 (+2D), `crouch_hold2d_v15/`. Pending review.
- **Kneeling crouch approved, October27:** Kvon: "This is good." Final crouch = `crouch_down_v15` / `crouch_hold_v15` (+2D v15), replacing v4. Exported over `KingdomArena/assets/sora/crouch_down_384/` and `crouch_hold_384/` (same file names and counts, .import files kept); verified in Godot (trace + recorded movie). Obsolete crouch v4-v14 (3D + 2D, incl. _dbg/_upright review folders) and the Crouching Light builds on the old crouch (atk_clight v1-v6) deleted per the cleanup rule. Next: rebuild the Crouching Light on the kneel.
- **Correction, October27:** Kvon (after approving v15, before the Crouching Light rebuild was shown): "Nevermind. Increase the turn until the foot is almost completely behind Sora." Kneeling crouch v16+: back foot further from the camera AND slid toward his body centre (screen right) so his body/front leg hide it. The Crouching Light (atk_clight v7 on crouch v15) must follow.
**Why:** Kvon's correction.
  - Result (pending review): crouch_down_v16 / crouch_hold_v16 (+2D): back foot slid .30 m toward his centre and .60 m away from the camera - hidden behind the knee/front leg except a small sliver. `crouch_hold2d_v16/Kneel_v15_vs_v16.png`, sheet, GIF. Godot still uses v15 until Kvon approves v16; atk_clight_v7 (built on v15) shown alongside.
- **Correction, October27:** Kvon: "Now just turn it a tiny bit in the opposite direction." Kneeling crouch v17: slide -.24 / depth .57 (v16 -.30 / .60). crouch_*_v17 (+2D), `crouch_hold2d_v17/Kneel_v15_v16_v17.png`. Pending review.
- **Correction, October27:** Kvon: "Now put more bend in his front knee, bringing his foot towards the middle of his torso." Kneeling crouch v18: front (left) foot slid .14 m toward screen left under his torso (CR_FRONT_IN), hips unchanged so the front knee bends more. crouch_*_v18 (+2D), `crouch_hold2d_v18/Kneel_v17_vs_v18.png`. Pending review.
- **Kneeling crouch final, October27:** Kvon: "This is the one." Final = `crouch_down_v18` / `crouch_hold_v18` (+2D): kneel (CR_KNEEL slide -.24, ankle .11, pitch 25, sink -.08; CR_KNEEL_DEPTH .57; CR_FRONT_IN .14). Exported over `crouch_down_384/` and `crouch_hold_384/` (.import kept), Godot verified. Obsolete crouch v15-v17 and atk_clight v7 (built on v15) deleted per the cleanup rule. Crouching Light rebuilt on v18 next.
- **Crouching Light v8, October27 (pending Kvon's review):** rebuilt on the final kneeling crouch v18 (kneel_R / kneel_L in the recipe; base pose checked with `atk_clight_v8_crouchcheck`). Same swing, smears and timing proposal (5/3/12) as before. `atk_clight2d_v8/` sheet + GIF.
- **Crouching Light approved and in Godot, October28:** Kvon: "I approve this version." Final `atk_clight_v30` / `atk_clight2d_v30` (low jab from the kneel; free arm tucked at his side, elbow folding 96.5/96.5/111.5/126.5 - history in Sora_Crouching_Light.md). Exported to `KingdomArena/assets/sora/attack_clight_384/` and `attack_clight_smear_384/` (384 px LANCZOS); `sora_move_test.gd` animation `attack_clight` [2,3,3,4,4,4] (startup 5, active 3, recovery 12), DRAW_SHIFT [0,45,82.5,75,0,0] (the 512 px in-frame offsets x .75), smear layer; **U while S/Down is held** triggers it from any ground move (not mid back-dash), it plays to the end, then crouch_hold if still crouching or crouch_up if released. Verified: traces (drawings at frames 30/32/35/38/42/46, crouch_hold or crouch_up at 50, x unchanged; standing U still plays attack_light) and a recorded Godot movie (feet planted across shifted drawings, Key teeth in frame). Recovery commit 0883bb41. Cleanup: the 44 obsolete atk_clight folders (v8-v29 + _crouchcheck/_lhandcheck review folders; 828 files, no .import files) were deleted after Kvon's OK ("You have my ok" - the first attempt, which read the list from a file, was blocked by Claude Code's safety check; the approved retry named every folder). Kept: atk_clight_v30, atk_clight2d_v30, momask_trial (tools). Godot move test re-run without errors; project.godot/.import unchanged.
- **Crouching Medium FINAL, October 29 (Kvon: "It is final"):** atk_cmed_v23 in Godot as `attack_cmedium` on I while crouching (details in Sora_Crouching_Medium.md); old versions v1-v22 cleaned up. Remaining attacks: Crouching Heavy, Jumping Light / Medium / Heavy.
