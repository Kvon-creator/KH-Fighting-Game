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
