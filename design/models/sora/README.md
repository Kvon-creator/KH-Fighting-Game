# Sora 3D-to-sprite experiment

Kvon chose3D animation rendered into2D sprites. Existing sprite assets and gameplay settings remain unchanged. Blender5.2.2 LTS was located and tested on this24GB-RAM computer; CPU modeling/export and transparent renders work without adding software. The VS Code Blender Development extension (jacqueslucke0.0.31) is installed; scripts run through the same Blender from the command line or with the extension's "Blender: Run Script".

**Experiments folder deleted (October21):** At Kvon's request, `design/models/sora/experiments/` was deleted. Weapon pipeline v1-v3 and the Hunyuan pilot remain recoverable from Git history (last present in commit 7cdbb40). Weapon v4 and character blockouts v1-v5 were never committed; they can be regenerated with the scripts in `blender_workflow/`:

- Weapon: `build_weapon_pilot.py`, `finalize_reference_crown.py`, `refine_reference_crown_v4.py`, `render_crown_v4_review.py` and helpers.
- Character: `build_character_blockout.py -- character_blockout_vN` (N=1-5). v5 is the latest from-scratch model: approved v2 proportions, almond eyes and blade hair after `design/references/sora_kh2_full_render.png`.

Run e.g. `blender --background --factory-startup --python blender_workflow/build_character_blockout.py -- character_blockout_v5`. Builders refuse to overwrite an existing version folder.

**Downloaded models (current direction):** Kvon downloaded models from The Models Resource into each character's `downloads/` folder and approved pushing them to GitHub. Sora's KH2 model `downloads/p_ex150.fbx` is rigged (49 bones, T-pose); `downloads/Kingdom Key/` holds the weapon. [inspect_downloaded_models.py](blender_workflow/inspect_downloaded_models.py) imports every OBJ/FBX read-only; results and front/side/back previews are in [../model_inspection_v1/](../model_inspection_v1/Inspection_Report.json).

**Sprite pilot (October21):** [build_sprite_pilot.py](blender_workflow/build_sprite_pilot.py) turns the downloaded model into one sprite frame. It scales Sora to 1.6 m and welds the rip's split vertices. The Kingdom Key is re-centered on its grip with the loose keychain links removed, then attached to his `R_buki` weapon bone. Each pose uses analytic two-bone aiming toward hand/foot targets. Original textures get a two-tone cel ramp, a heavy outer Freestyle contour and faint interior lines. One fixed orthographic camera at yaw -40 is framed like the approved idle: 512px canvas, soles at y=470, plus a 128px export.

- **Current:** [sprite_pilot_v4](sprite_pilot_v4/Approved_Idle_vs_Pilot.png).
- **Earlier revisions (kept):** v1 used IK constraints (twisted legs) and drew every rip seam. v2 cleaned the lines but stood narrow and upright. v3 widened the stance but stayed too dark from dense interior outlines.
- **Not done:** the pose is approximate and the left hand only roughly reaches the handle. No animation, no final approval.

**Idle breathing loop (October21):** `build_sprite_pilot.py -- idle_loop_vN` renders a refined pose: deeper, wider crouch, lower and more forward grip, flatter blade. The left hand's weapon socket is placed on the handle, landing within about 2 cm. Packaging: `python package_idle_loop.py idle_loop_vN`.

- **Loop:** 10 frames with the approved idle's timing (1480 ms). The body sinks and leans with the breath; hands, Key and head trail by 12% of a cycle.
- **Key placement:** placed rigidly at the grip every frame, because a bone-parented Key wobbled as the re-solved hand twisted.
- **Current:** [idle_loop_v17](idle_loop_v17/Hands_NoKey_v14_v16_v17.png): a `fist_wrap` shape key rolls the fingers and thumbs around the handle, and the wrists are squared so the fingers cross it. v15 curled too little; v16 left the right fingers lying along the handle.
- **v14:** [idle_loop_v14](idle_loop_v14/Hands_v13_vs_v14.png), from Kvon's suggestion: front (right) palm up, left wrist turned the opposite way, hands slid up toward the hilt.
- **v13:** [idle_loop_v13](idle_loop_v13/Reference_vs_3D_pose.png): a stronger hunch, with shoulders that reach forward when an arm falls short. The grip is measured at the visible hand mesh, and the Key slides so both fists wrap the handle inside the guard. v11 was the stronger hunch alone; v12 added mesh-measured hands, but the fists sat near the pommel.
- **v10:** Per Kvon, Sora hunches over a little and bends his elbows around the grip; a side-profile check render shows the lean. v9 was the first hunch pass, with the grip too high.
- **v8:** posed from Kvon's Smash idle reference (`design/references/sora_smash_idle_pose_reference.png`) with the same breathing. v7 was the first pass: grip centered, flatter blade.
- **v6:** Per Kvon, the Keyblade teeth face up, and each wrist is twisted about its forearm so the palm wraps the handle; twist and finger curl are searched per hand.
- **v5:** After Kvon said the Keyblade was held the wrong way, v4 turns the guard face toward the camera with the teeth down and puts the fist inside the guard. v5 adds an automatic finger curl (partial; the palms still need a wrist roll).
- **v3:** the breathing Kvon approved, with the wrong grip orientation. It includes 512/128px frames, a 5x2 sheet, looping GIFs, a keyed `.blend` and `Package_QA.json` (GIF timings, loop flag, soles at y=470-471, 10 distinct frames).
- **Earlier:** v2 is kept and repeats frames in a ping-pong, from a symmetric breath with no lag. v1 was an aborted first render.
- **Not done:** not tested in Godot, and not user-approved.

**One-handed pose (October22):** [one_hand_v3](one_hand_v3/Pose_Views.png) (front, side, sprite views). The right hand holds the Key at the hip, wrapped by the fist shape key; the blade angles down toward his right foot and stops just above the floor; the left arm is relaxed. The breathing loop and packaging are the same as the idle. Earlier tries: v1 (vertical blade, below the floor), v2 (teeth 2px below the floor).

**Mirrored guard crouch (October22):** [battle_v12](battle_v12/Hands_v11_vs_v12.png) turns the left palm 45 degrees back toward Sora. **Approved by Kvon "for now" as the current battle idle.** [battle_v11](battle_v11/Hands_v10_vs_v11.png) turns the left palm about 25 degrees back toward Sora. [battle_v10](battle_v10/Hands_v9_vs_v10.png) turns the left (non-anchoring) wrist so its palm faces the screen. [battle_v9](battle_v9/Hands_v8_vs_v9.png) shifts the grip until both fists hold the handle (left fist within 1.2-1.7 cm). [battle_v8](battle_v8/Mirrored_Reference_vs_Sprite_v7_v8.png) matches the drawing's Keyblade angle (v7: 20 degrees on-screen rise, foreshortened toward the viewer) with the legs a little closer together. [battle_v6](battle_v6/Mirrored_Reference_vs_Sprite_v5_v6.png) turns his body to the drawing's angle in the sprite view (camera unchanged). [battle_v5](battle_v5/Mirrored_Reference_vs_3D_pose.png) copies the top-right pose of the pose sheet, mirrored, with both hands on the handle (v3 had misread it as one-handed). The blade runs level out to his left and rises slightly, in a wide hunched squat with the head turned toward the opponent. v4 was the first pass, with the crouch too deep.

**Guard crouch (October22):** [battle_v3](battle_v3/Reference_vs_3D_pose.png) emulates the top-right pose of `design/references/sora_kh2_pose_sheet.png`: a wide, hunched crouch with the Key in the right fist at the hip, the blade level to his right, and the left arm down.

**Battle-ready pose (October22):** [battle_v2](battle_v2/Stance_Reference_vs_Battle.png) shows the KH2 battle-stance reference, then front, side and sprite views. The stance is staggered with the body turned toward the opponent; the Keyblade is low in the right hand, angled down and back; the left hand is a bent guard; the loop is a 1000 ms combat bounce. v1's guard arm was straight.

**Gemini animation request (October22):** refused by Gemini ("interests of third-party content providers"); the receipt is in `gemini_animation/attempt_01/`.

**2D sprite attempt (October22, approved by Kvon):** [sprite2d_v3](sprite2d_v3/Reference_vs_3D_vs_2D.png) re-renders the approved battle_v12 loop as illustration-style sprites: a cooler, larger two-tone shadow and crisp dark ink. It has the same 10 frames and timing ([game size](sprite2d_v3/Game_Size_3D_vs_2D_x2.png)). Scripts: `render_2d_style.py` and `stylize_2d_frames.py`. Earlier tries: v1 (palette snapping washed out colours), v2 (glowing rim).

**From-scratch articulated Sora (October22):** [character_blockout_v7](character_blockout_v7/Rig_Test_Board.png) is the procedural Sora (approved v2 proportions, v5 face/hair) with pose-sheet outfit details. It has a 19-bone (26 from v8) KH2-named skeleton and skin weights, and the articulation test bends the arms, chest, head and knee. v6 had stretched cloth pieces from a weighting bug. It has not yet been posed into the battle crouch.

**Decision (October22):** Kvon chose to stay with the PS2 model. The from-scratch model below is preserved but parked.

**From-scratch model as a sprite (October22):** [sheet2d_v1](sheet2d_v1/Reference_vs_PS2_2D_vs_Sheet_2D.png) shows the rigged from-scratch Sora (`character_blockout_v9`) posed with the approved battle_v12 recipe (`build_sprite_pilot.py -- battle_v12 sheet_battle_v3`) and rendered in the approved 2D style. [Game-size comparison](sheet2d_v1/Game_Size_PS2_vs_Sheet_x2.png) with sprite2d_v3.

Requirements carried forward: KH2 outfit, smooth cel style and rigid far-hand same-shoulder Kingdom Key carry behind the head, with slight foreground tip. Render run-start, loop and stop from one fixed orthographic camera; review against approved idle/run-start and match the joins before aerial movement.
